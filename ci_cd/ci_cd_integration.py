#!/usr/bin/env python3
"""
Complete CI/CD Integration Script
Orchestrates the entire CI/CD pipeline: test execution, reporting, notifications, and deployment
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from ci_cd.automated_test_runner import AutomatedTestRunner
from ci_cd.notification_system import NotificationSystem, TestResult
from ci_cd.deployment_system import DeploymentSystem


class CICDOrchestrator:
    """Complete CI/CD pipeline orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize components
        self.test_runner = AutomatedTestRunner()
        self.notifier = NotificationSystem()
        self.deployer = DeploymentSystem()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load CI/CD configuration"""
        default_config = {
            "pipeline": {
                "auto_deploy_on_success": True,
                "notify_on_start": True,
                "notify_on_completion": True,
                "generate_reports": True,
                "cleanup_artifacts": True
            },
            "environments": {
                "development": {
                    "test_types": ["unit"],
                    "auto_deploy": True,
                    "notify_failures_only": False
                },
                "staging": {
                    "test_types": ["unit", "integration", "ui"],
                    "auto_deploy": True,
                    "notify_failures_only": False
                },
                "production": {
                    "test_types": ["unit", "integration", "ui", "e2e", "security"],
                    "auto_deploy": False,
                    "notify_failures_only": True
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load CI/CD config: {e}")
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CI/CD orchestrator"""
        logger = logging.getLogger('cicd_orchestrator')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = Path('ci_cd/logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f'cicd_pipeline_{timestamp}.log'
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
    
    def run_pipeline(self, environment: str, version: str, 
                    commit_hash: Optional[str] = None,
                    test_types: Optional[List[str]] = None,
                    force_deploy: bool = False) -> Dict:
        """Run complete CI/CD pipeline"""
        
        pipeline_start_time = datetime.now()
        self.logger.info(f"Starting CI/CD pipeline for {environment} (version: {version})")
        
        pipeline_result = {
            'environment': environment,
            'version': version,
            'commit_hash': commit_hash,
            'start_time': pipeline_start_time.isoformat(),
            'stages': {},
            'overall_status': 'running'
        }
        
        try:
            # Stage 1: Send start notification
            if self.config['pipeline'].get('notify_on_start', True):
                self._send_start_notification(environment, version)
            
            # Stage 2: Run tests
            self.logger.info("Stage 2: Running tests...")
            test_result = self._run_tests_stage(environment, test_types)
            pipeline_result['stages']['tests'] = test_result
            
            if test_result['status'] != 'success':
                pipeline_result['overall_status'] = 'failed'
                self._send_failure_notification(test_result, 'test_failure')
                return pipeline_result
            
            # Stage 3: Generate reports
            if self.config['pipeline'].get('generate_reports', True):
                self.logger.info("Stage 3: Generating reports...")
                report_result = self._generate_reports_stage()
                pipeline_result['stages']['reports'] = report_result
            
            # Stage 4: Deploy (if configured)
            env_config = self.config['environments'].get(environment, {})
            should_deploy = (
                env_config.get('auto_deploy', False) or force_deploy
            ) and test_result['status'] == 'success'
            
            if should_deploy:
                self.logger.info("Stage 4: Deploying...")
                deploy_result = self._deploy_stage(environment, version, commit_hash, test_result['results'])
                pipeline_result['stages']['deployment'] = deploy_result
                
                if deploy_result['status'] != 'success':
                    pipeline_result['overall_status'] = 'failed'
                    self._send_failure_notification(deploy_result, 'deployment_failure')
                    return pipeline_result
            
            # Stage 5: Send success notification
            pipeline_result['overall_status'] = 'success'
            pipeline_result['end_time'] = datetime.now().isoformat()
            
            if self.config['pipeline'].get('notify_on_completion', True):
                self._send_success_notification(pipeline_result)
            
            # Stage 6: Cleanup
            if self.config['pipeline'].get('cleanup_artifacts', True):
                self._cleanup_artifacts()
            
            self.logger.info("CI/CD pipeline completed successfully")
            return pipeline_result
            
        except Exception as e:
            self.logger.error(f"CI/CD pipeline failed: {e}")
            pipeline_result['overall_status'] = 'error'
            pipeline_result['error'] = str(e)
            pipeline_result['end_time'] = datetime.now().isoformat()
            
            self._send_failure_notification(pipeline_result, 'pipeline_error')
            return pipeline_result
    
    def _run_tests_stage(self, environment: str, test_types: Optional[List[str]]) -> Dict:
        """Run tests stage"""
        try:
            # Get test types from environment config if not specified
            if test_types is None:
                env_config = self.config['environments'].get(environment, {})
                test_types = env_config.get('test_types', ['unit'])
            
            # Run tests
            result = self.test_runner.run_automated_tests(environment, test_types)
            
            return {
                'status': 'success' if result.exit_code == 0 else 'failed',
                'results': result,
                'test_types': test_types,
                'duration': result.duration
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'test_types': test_types or [],
                'duration': 0.0
            }
    
    def _generate_reports_stage(self) -> Dict:
        """Generate reports stage"""
        try:
            import subprocess
            
            # Generate comprehensive CI report
            result = subprocess.run([
                sys.executable, 'ci_cd/generate_ci_report.py',
                '--artifacts-dir', 'ci_cd/reports',
                '--output-dir', 'ci_cd/final_report',
                '--format', 'html', 'json', 'junit', 'markdown'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'report_path': 'ci_cd/final_report/index.html'
                }
            else:
                return {
                    'status': 'failed',
                    'error': result.stderr or 'Report generation failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _deploy_stage(self, environment: str, version: str, 
                     commit_hash: Optional[str], test_results: Dict) -> Dict:
        """Deploy stage"""
        try:
            # Check if deployment should proceed
            should_deploy, reason = self.deployer.should_deploy(environment, test_results)
            
            if not should_deploy:
                return {
                    'status': 'skipped',
                    'reason': reason
                }
            
            # Perform deployment
            deploy_result = self.deployer.deploy(environment, version, commit_hash)
            
            return {
                'status': deploy_result.status,
                'result': deploy_result,
                'duration': deploy_result.duration
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _send_start_notification(self, environment: str, version: str):
        """Send pipeline start notification"""
        try:
            # Create minimal test result for notification
            result = TestResult(
                timestamp=datetime.now().isoformat(),
                environment=environment,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                duration=0.0,
                coverage_percentage=0.0,
                exit_code=0,
                build_number=version
            )
            
            self.notifier.send_test_results(result, "pipeline_start")
            
        except Exception as e:
            self.logger.warning(f"Could not send start notification: {e}")
    
    def _send_success_notification(self, pipeline_result: Dict):
        """Send pipeline success notification"""
        try:
            test_stage = pipeline_result['stages'].get('tests', {})
            test_result = test_stage.get('results')
            
            if test_result:
                self.notifier.send_test_results(test_result, "pipeline_success")
            
        except Exception as e:
            self.logger.warning(f"Could not send success notification: {e}")
    
    def _send_failure_notification(self, stage_result: Dict, notification_type: str):
        """Send pipeline failure notification"""
        try:
            # Create test result from stage result
            if 'results' in stage_result:
                test_result = stage_result['results']
            else:
                # Create minimal failure result
                test_result = TestResult(
                    timestamp=datetime.now().isoformat(),
                    environment=stage_result.get('environment', 'unknown'),
                    total_tests=0,
                    passed=0,
                    failed=1,
                    skipped=0,
                    errors=0,
                    duration=stage_result.get('duration', 0.0),
                    coverage_percentage=0.0,
                    exit_code=1
                )
            
            self.notifier.send_test_results(test_result, notification_type)
            
        except Exception as e:
            self.logger.warning(f"Could not send failure notification: {e}")
    
    def _cleanup_artifacts(self):
        """Cleanup old artifacts"""
        try:
            # Clean up old logs (keep last 10)
            logs_dir = Path('ci_cd/logs')
            if logs_dir.exists():
                log_files = sorted(logs_dir.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
                for log_file in log_files[10:]:
                    log_file.unlink()
            
            # Clean up old reports (keep last 5)
            reports_dir = Path('ci_cd/reports')
            if reports_dir.exists():
                report_dirs = sorted(reports_dir.glob('*_*'), key=lambda x: x.stat().st_mtime, reverse=True)
                for report_dir in report_dirs[5:]:
                    if report_dir.is_dir():
                        import shutil
                        shutil.rmtree(report_dir)
            
            self.logger.info("Cleaned up old artifacts")
            
        except Exception as e:
            self.logger.warning(f"Could not cleanup artifacts: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GopiAI CI/CD Pipeline Orchestrator')
    parser.add_argument('--environment', required=True,
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--version', required=True,
                       help='Version to deploy')
    parser.add_argument('--commit-hash', help='Git commit hash')
    parser.add_argument('--test-types', nargs='+',
                       choices=['unit', 'integration', 'ui', 'e2e', 'performance', 'security'],
                       help='Test types to run')
    parser.add_argument('--force-deploy', action='store_true',
                       help='Force deployment even if auto-deploy is disabled')
    parser.add_argument('--config', help='CI/CD configuration file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without executing')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = CICDOrchestrator(args.config)
    
    if args.dry_run:
        print("DRY RUN - Would execute CI/CD pipeline with:")
        print(f"Environment: {args.environment}")
        print(f"Version: {args.version}")
        print(f"Commit Hash: {args.commit_hash}")
        print(f"Test Types: {args.test_types}")
        print(f"Force Deploy: {args.force_deploy}")
        return
    
    # Run pipeline
    result = orchestrator.run_pipeline(
        environment=args.environment,
        version=args.version,
        commit_hash=args.commit_hash,
        test_types=args.test_types,
        force_deploy=args.force_deploy
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"CI/CD PIPELINE RESULT")
    print(f"{'='*60}")
    print(f"Environment: {result['environment']}")
    print(f"Version: {result['version']}")
    print(f"Status: {result['overall_status'].upper()}")
    print(f"Start Time: {result['start_time']}")
    if 'end_time' in result:
        print(f"End Time: {result['end_time']}")
    
    print(f"\nStages:")
    for stage_name, stage_result in result['stages'].items():
        status = stage_result.get('status', 'unknown')
        print(f"  {stage_name}: {status.upper()}")
    
    if 'error' in result:
        print(f"\nError: {result['error']}")
    
    print(f"{'='*60}")
    
    # Save pipeline result
    result_file = Path(f'ci_cd/pipeline_results/{args.environment}_latest.json')
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    # Exit with appropriate code
    exit_code = 0 if result['overall_status'] == 'success' else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()