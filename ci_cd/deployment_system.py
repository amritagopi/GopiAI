#!/usr/bin/env python3
"""
Automated Deployment System for GopiAI
Handles deployment to different environments after successful tests
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from ci_cd.notification_system import NotificationSystem, TestResult


@dataclass
class DeploymentConfig:
    """Configuration for deployment environments"""
    name: str
    auto_deploy: bool
    requires_approval: bool
    test_requirements: List[str]
    coverage_threshold: float
    deployment_script: str
    rollback_script: Optional[str] = None
    health_check_url: Optional[str] = None
    health_check_timeout: int = 300
    post_deploy_tests: List[str] = None


@dataclass
class DeploymentResult:
    """Result of deployment operation"""
    environment: str
    status: str  # success, failure, rollback
    timestamp: str
    duration: float
    version: str
    commit_hash: Optional[str] = None
    rollback_version: Optional[str] = None
    error_message: Optional[str] = None
    health_check_passed: bool = False


class DeploymentSystem:
    """Automated deployment system with rollback capabilities"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.notifier = NotificationSystem()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, DeploymentConfig]:
        """Load deployment configuration"""
        default_config = {
            "development": {
                "name": "development",
                "auto_deploy": True,
                "requires_approval": False,
                "test_requirements": ["unit"],
                "coverage_threshold": 70.0,
                "deployment_script": "ci_cd/scripts/deploy_development.py",
                "health_check_url": "http://localhost:5051/health",
                "health_check_timeout": 60,
                "post_deploy_tests": []
            },
            "staging": {
                "name": "staging",
                "auto_deploy": True,
                "requires_approval": False,
                "test_requirements": ["unit", "integration", "ui"],
                "coverage_threshold": 80.0,
                "deployment_script": "ci_cd/scripts/deploy_staging.py",
                "rollback_script": "ci_cd/scripts/rollback_staging.py",
                "health_check_url": "https://staging.gopiai.com/health",
                "health_check_timeout": 120,
                "post_deploy_tests": ["smoke"]
            },
            "production": {
                "name": "production",
                "auto_deploy": False,
                "requires_approval": True,
                "test_requirements": ["unit", "integration", "ui", "e2e", "security"],
                "coverage_threshold": 90.0,
                "deployment_script": "ci_cd/scripts/deploy_production.py",
                "rollback_script": "ci_cd/scripts/rollback_production.py",
                "health_check_url": "https://gopiai.com/health",
                "health_check_timeout": 300,
                "post_deploy_tests": ["smoke", "critical_path"]
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load deployment config: {e}")
        
        # Convert to DeploymentConfig objects
        configs = {}
        for env_name, env_config in default_config.items():
            configs[env_name] = DeploymentConfig(**env_config)
        
        return configs
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for deployment system"""
        logger = logging.getLogger('deployment_system')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = Path('ci_cd/logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f'deployment_{timestamp}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def should_deploy(self, environment: str, test_results: Dict) -> tuple[bool, str]:
        """Check if deployment should proceed based on test results"""
        if environment not in self.config:
            return False, f"Unknown environment: {environment}"
        
        env_config = self.config[environment]
        
        # Check if auto-deploy is enabled
        if not env_config.auto_deploy:
            return False, f"Auto-deploy disabled for {environment}"
        
        # Check if approval is required
        if env_config.requires_approval:
            approval_file = Path(f'ci_cd/approvals/{environment}_approved.flag')
            if not approval_file.exists():
                return False, f"Manual approval required for {environment}"
        
        # Check test requirements
        for required_test in env_config.test_requirements:
            if required_test not in test_results:
                return False, f"Required test type '{required_test}' not found in results"
            
            test_result = test_results[required_test]
            if test_result.get('failed', 0) > 0 or test_result.get('errors', 0) > 0:
                return False, f"Test failures in required test type '{required_test}'"
        
        # Check coverage threshold
        overall_coverage = self._calculate_overall_coverage(test_results)
        if overall_coverage < env_config.coverage_threshold:
            return False, f"Coverage {overall_coverage:.1f}% below threshold {env_config.coverage_threshold:.1f}%"
        
        return True, "All deployment criteria met"
    
    def deploy(self, environment: str, version: str, commit_hash: Optional[str] = None) -> DeploymentResult:
        """Deploy to specified environment"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        self.logger.info(f"Starting deployment to {environment} (version: {version})")
        
        if environment not in self.config:
            return DeploymentResult(
                environment=environment,
                status="failure",
                timestamp=timestamp,
                duration=time.time() - start_time,
                version=version,
                commit_hash=commit_hash,
                error_message=f"Unknown environment: {environment}"
            )
        
        env_config = self.config[environment]
        
        try:
            # Pre-deployment backup
            backup_info = self._create_backup(environment)
            
            # Execute deployment script
            self.logger.info(f"Executing deployment script: {env_config.deployment_script}")
            deployment_success = self._execute_deployment_script(
                env_config.deployment_script, 
                environment, 
                version, 
                commit_hash
            )
            
            if not deployment_success:
                raise Exception("Deployment script failed")
            
            # Wait for application to start
            self.logger.info("Waiting for application to start...")
            time.sleep(30)
            
            # Health check
            health_check_passed = self._perform_health_check(env_config)
            
            if not health_check_passed:
                self.logger.error("Health check failed, initiating rollback...")
                rollback_result = self._rollback(environment, backup_info)
                
                return DeploymentResult(
                    environment=environment,
                    status="rollback",
                    timestamp=timestamp,
                    duration=time.time() - start_time,
                    version=version,
                    commit_hash=commit_hash,
                    rollback_version=backup_info.get('version'),
                    error_message="Health check failed",
                    health_check_passed=False
                )
            
            # Post-deployment tests
            if env_config.post_deploy_tests:
                self.logger.info("Running post-deployment tests...")
                post_test_success = self._run_post_deployment_tests(
                    environment, 
                    env_config.post_deploy_tests
                )
                
                if not post_test_success:
                    self.logger.error("Post-deployment tests failed, initiating rollback...")
                    rollback_result = self._rollback(environment, backup_info)
                    
                    return DeploymentResult(
                        environment=environment,
                        status="rollback",
                        timestamp=timestamp,
                        duration=time.time() - start_time,
                        version=version,
                        commit_hash=commit_hash,
                        rollback_version=backup_info.get('version'),
                        error_message="Post-deployment tests failed",
                        health_check_passed=True
                    )
            
            # Clean up old backups
            self._cleanup_old_backups(environment)
            
            # Clear approval flag if it exists
            approval_file = Path(f'ci_cd/approvals/{environment}_approved.flag')
            if approval_file.exists():
                approval_file.unlink()
            
            duration = time.time() - start_time
            
            result = DeploymentResult(
                environment=environment,
                status="success",
                timestamp=timestamp,
                duration=duration,
                version=version,
                commit_hash=commit_hash,
                health_check_passed=True
            )
            
            self.logger.info(f"Deployment to {environment} completed successfully in {duration:.2f}s")
            
            # Send success notification
            self._send_deployment_notification(result)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"Deployment to {environment} failed: {error_msg}")
            
            result = DeploymentResult(
                environment=environment,
                status="failure",
                timestamp=timestamp,
                duration=duration,
                version=version,
                commit_hash=commit_hash,
                error_message=error_msg
            )
            
            # Send failure notification
            self._send_deployment_notification(result)
            
            return result
    
    def _create_backup(self, environment: str) -> Dict:
        """Create backup before deployment"""
        self.logger.info(f"Creating backup for {environment}...")
        
        backup_dir = Path(f'ci_cd/backups/{environment}')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'backup_{timestamp}'
        
        # Get current version info
        current_version = self._get_current_version(environment)
        
        backup_info = {
            'timestamp': timestamp,
            'path': str(backup_path),
            'version': current_version,
            'environment': environment
        }
        
        # Save backup info
        with open(backup_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2)
        
        return backup_info
    
    def _execute_deployment_script(self, script_path: str, environment: str, 
                                 version: str, commit_hash: Optional[str]) -> bool:
        """Execute deployment script"""
        try:
            cmd = [
                sys.executable, script_path,
                '--environment', environment,
                '--version', version
            ]
            
            if commit_hash:
                cmd.extend(['--commit-hash', commit_hash])
            
            # Set environment variables
            env = os.environ.copy()
            env['DEPLOYMENT_ENVIRONMENT'] = environment
            env['DEPLOYMENT_VERSION'] = version
            if commit_hash:
                env['DEPLOYMENT_COMMIT'] = commit_hash
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
                env=env
            )
            
            if result.returncode == 0:
                self.logger.info("Deployment script completed successfully")
                if result.stdout:
                    self.logger.debug(f"Script output: {result.stdout}")
                return True
            else:
                self.logger.error(f"Deployment script failed with exit code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Script error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Deployment script timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error executing deployment script: {e}")
            return False
    
    def _perform_health_check(self, env_config: DeploymentConfig) -> bool:
        """Perform health check on deployed application"""
        if not env_config.health_check_url:
            self.logger.info("No health check URL configured, skipping health check")
            return True
        
        self.logger.info(f"Performing health check: {env_config.health_check_url}")
        
        import requests
        
        start_time = time.time()
        timeout = env_config.health_check_timeout
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    env_config.health_check_url,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.logger.info("Health check passed")
                    return True
                else:
                    self.logger.warning(f"Health check returned status {response.status_code}")
                    
            except requests.RequestException as e:
                self.logger.debug(f"Health check attempt failed: {e}")
            
            time.sleep(10)  # Wait 10 seconds before retry
        
        self.logger.error(f"Health check failed after {timeout} seconds")
        return False
    
    def _run_post_deployment_tests(self, environment: str, test_types: List[str]) -> bool:
        """Run post-deployment tests"""
        self.logger.info(f"Running post-deployment tests: {test_types}")
        
        try:
            from test_infrastructure.master_test_runner import MasterTestRunner
            runner = MasterTestRunner()
            
            for test_type in test_types:
                self.logger.info(f"Running {test_type} tests...")
                
                if test_type == "smoke":
                    result = runner.run_smoke_tests()
                elif test_type == "critical_path":
                    result = runner.run_critical_path_tests()
                else:
                    self.logger.warning(f"Unknown post-deployment test type: {test_type}")
                    continue
                
                if result.get('failed', 0) > 0 or result.get('errors', 0) > 0:
                    self.logger.error(f"Post-deployment {test_type} tests failed")
                    return False
            
            self.logger.info("All post-deployment tests passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error running post-deployment tests: {e}")
            return False
    
    def _rollback(self, environment: str, backup_info: Dict) -> bool:
        """Rollback to previous version"""
        self.logger.info(f"Rolling back {environment} to version {backup_info.get('version')}")
        
        env_config = self.config[environment]
        
        if not env_config.rollback_script:
            self.logger.error(f"No rollback script configured for {environment}")
            return False
        
        try:
            cmd = [
                sys.executable, env_config.rollback_script,
                '--environment', environment,
                '--backup-info', json.dumps(backup_info)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info("Rollback completed successfully")
                return True
            else:
                self.logger.error(f"Rollback failed with exit code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Rollback error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False
    
    def _get_current_version(self, environment: str) -> str:
        """Get current deployed version"""
        version_file = Path(f'ci_cd/versions/{environment}_version.txt')
        
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except Exception:
                pass
        
        return "unknown"
    
    def _calculate_overall_coverage(self, test_results: Dict) -> float:
        """Calculate overall test coverage"""
        total_coverage = 0.0
        count = 0
        
        for result in test_results.values():
            if 'coverage' in result:
                total_coverage += result['coverage']
                count += 1
        
        return total_coverage / count if count > 0 else 0.0
    
    def _cleanup_old_backups(self, environment: str, keep_count: int = 5):
        """Clean up old backup files"""
        backup_dir = Path(f'ci_cd/backups/{environment}')
        
        if not backup_dir.exists():
            return
        
        # Get all backup files sorted by modification time
        backup_files = sorted(
            backup_dir.glob('backup_*'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Remove old backups
        for backup_file in backup_files[keep_count:]:
            try:
                if backup_file.is_file():
                    backup_file.unlink()
                elif backup_file.is_dir():
                    shutil.rmtree(backup_file)
                self.logger.debug(f"Removed old backup: {backup_file}")
            except Exception as e:
                self.logger.warning(f"Could not remove old backup {backup_file}: {e}")
    
    def _send_deployment_notification(self, result: DeploymentResult):
        """Send deployment notification"""
        try:
            # Convert to TestResult format for notification system
            test_result = TestResult(
                timestamp=result.timestamp,
                environment=result.environment,
                total_tests=0,
                passed=1 if result.status == "success" else 0,
                failed=1 if result.status in ["failure", "rollback"] else 0,
                skipped=0,
                errors=0,
                duration=result.duration,
                coverage_percentage=0.0,
                exit_code=0 if result.status == "success" else 1,
                build_number=result.version,
                commit_hash=result.commit_hash
            )
            
            self.notifier.send_test_results(test_result, "deployment")
            
        except Exception as e:
            self.logger.warning(f"Could not send deployment notification: {e}")


def main():
    """Main entry point for deployment system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GopiAI Deployment System')
    parser.add_argument('--environment', required=True,
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--version', required=True,
                       help='Version to deploy')
    parser.add_argument('--commit-hash', help='Git commit hash')
    parser.add_argument('--config', help='Deployment configuration file')
    parser.add_argument('--force', action='store_true',
                       help='Force deployment even if criteria not met')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check if deployment should proceed')
    
    args = parser.parse_args()
    
    # Initialize deployment system
    deployer = DeploymentSystem(args.config)
    
    if args.check_only:
        # Load test results
        result_file = Path('ci_cd/last_execution_result.json')
        if result_file.exists():
            with open(result_file, 'r', encoding='utf-8') as f:
                test_results = json.load(f)
        else:
            test_results = {}
        
        should_deploy, reason = deployer.should_deploy(args.environment, test_results)
        
        print(f"Should deploy to {args.environment}: {should_deploy}")
        print(f"Reason: {reason}")
        
        sys.exit(0 if should_deploy else 1)
    
    # Perform deployment
    result = deployer.deploy(args.environment, args.version, args.commit_hash)
    
    print(f"\n{'='*60}")
    print(f"DEPLOYMENT RESULT")
    print(f"{'='*60}")
    print(f"Environment: {result.environment}")
    print(f"Status: {result.status.upper()}")
    print(f"Version: {result.version}")
    print(f"Duration: {result.duration:.2f}s")
    if result.error_message:
        print(f"Error: {result.error_message}")
    print(f"{'='*60}")
    
    # Save deployment result
    result_file = Path(f'ci_cd/deployment_results/{args.environment}_latest.json')
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    sys.exit(0 if result.status == "success" else 1)


if __name__ == '__main__':
    main()