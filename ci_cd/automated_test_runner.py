#!/usr/bin/env python3
"""
Automated Test Runner for CI/CD Integration
Provides comprehensive test execution with reporting and notifications
"""

import os
import sys
import json
import time
import logging
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from test_infrastructure.master_test_runner import MasterTestRunner
from test_infrastructure.master_reporter import MasterReporter
from test_infrastructure.service_manager import ServiceManager


@dataclass
class TestExecutionResult:
    """Result of automated test execution"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    coverage_percentage: float
    exit_code: int
    report_path: str
    artifacts: List[str]


class AutomatedTestRunner:
    """Automated test runner for CI/CD environments"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.service_manager = ServiceManager()
        self.master_runner = MasterTestRunner()
        self.reporter = MasterReporter()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load CI/CD configuration"""
        default_config = {
            "test_types": ["unit", "integration", "ui", "e2e", "performance", "security"],
            "parallel_execution": True,
            "timeout_minutes": 60,
            "coverage_threshold": 80.0,
            "retry_failed_tests": True,
            "max_retries": 2,
            "notification_enabled": True,
            "artifact_retention_days": 30,
            "environments": {
                "development": {
                    "skip_slow_tests": True,
                    "coverage_threshold": 70.0
                },
                "staging": {
                    "skip_slow_tests": False,
                    "coverage_threshold": 80.0
                },
                "production": {
                    "skip_slow_tests": False,
                    "coverage_threshold": 90.0
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for automated execution"""
        logger = logging.getLogger('automated_test_runner')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = Path('ci_cd/logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f'automated_tests_{timestamp}.log'
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
    
    def run_automated_tests(self, environment: str = "development", 
                          test_types: Optional[List[str]] = None) -> TestExecutionResult:
        """Run automated test suite"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        self.logger.info(f"Starting automated test execution for environment: {environment}")
        
        # Get environment-specific config
        env_config = self.config.get("environments", {}).get(environment, {})
        
        # Determine test types to run
        if test_types is None:
            test_types = self.config.get("test_types", ["unit", "integration"])
        
        try:
            # Pre-execution setup
            self._pre_execution_setup(environment)
            
            # Run tests
            results = self._execute_tests(test_types, env_config)
            
            # Generate reports
            report_path = self._generate_reports(results, environment)
            
            # Calculate metrics
            total_tests = sum(r.get('total', 0) for r in results.values())
            passed = sum(r.get('passed', 0) for r in results.values())
            failed = sum(r.get('failed', 0) for r in results.values())
            skipped = sum(r.get('skipped', 0) for r in results.values())
            errors = sum(r.get('errors', 0) for r in results.values())
            
            # Calculate coverage
            coverage_percentage = self._calculate_coverage(results)
            
            # Determine exit code
            exit_code = self._determine_exit_code(results, env_config)
            
            duration = time.time() - start_time
            
            result = TestExecutionResult(
                timestamp=timestamp,
                total_tests=total_tests,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                duration=duration,
                coverage_percentage=coverage_percentage,
                exit_code=exit_code,
                report_path=report_path,
                artifacts=self._collect_artifacts()
            )
            
            self.logger.info(f"Test execution completed in {duration:.2f}s")
            self.logger.info(f"Results: {passed}/{total_tests} passed, {failed} failed, {skipped} skipped")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            duration = time.time() - start_time
            
            return TestExecutionResult(
                timestamp=timestamp,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=duration,
                coverage_percentage=0.0,
                exit_code=1,
                report_path="",
                artifacts=[]
            )
        
        finally:
            # Cleanup
            self._post_execution_cleanup()
    
    def _pre_execution_setup(self, environment: str):
        """Setup before test execution"""
        self.logger.info("Setting up test environment...")
        
        # Create necessary directories
        for dir_name in ['ci_cd/reports', 'ci_cd/artifacts', 'ci_cd/logs']:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
        
        # Start required services
        if environment != "unit_only":
            self.service_manager.start_required_services()
            
        # Wait for services to be ready
        self._wait_for_services()
    
    def _execute_tests(self, test_types: List[str], env_config: Dict) -> Dict:
        """Execute specified test types"""
        results = {}
        
        for test_type in test_types:
            self.logger.info(f"Running {test_type} tests...")
            
            try:
                if test_type == "unit":
                    result = self.master_runner.run_unit_tests()
                elif test_type == "integration":
                    result = self.master_runner.run_integration_tests()
                elif test_type == "ui":
                    result = self.master_runner.run_ui_tests()
                elif test_type == "e2e":
                    result = self.master_runner.run_e2e_tests()
                elif test_type == "performance":
                    result = self.master_runner.run_performance_tests()
                elif test_type == "security":
                    result = self.master_runner.run_security_tests()
                else:
                    self.logger.warning(f"Unknown test type: {test_type}")
                    continue
                
                results[test_type] = result
                self.logger.info(f"{test_type} tests completed: {result}")
                
            except Exception as e:
                self.logger.error(f"Failed to run {test_type} tests: {e}")
                results[test_type] = {
                    'total': 0, 'passed': 0, 'failed': 1, 
                    'skipped': 0, 'errors': 1
                }
        
        return results
    
    def _generate_reports(self, results: Dict, environment: str) -> str:
        """Generate comprehensive test reports"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = Path(f'ci_cd/reports/{environment}_{timestamp}')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate master report
        report_path = str(report_dir / 'test_report.html')
        self.reporter.generate_comprehensive_report(results, report_path)
        
        # Generate JSON report for CI/CD systems
        json_report_path = str(report_dir / 'test_results.json')
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Generate JUnit XML for CI/CD integration
        junit_path = str(report_dir / 'junit_results.xml')
        self._generate_junit_xml(results, junit_path)
        
        return report_path
    
    def _generate_junit_xml(self, results: Dict, output_path: str):
        """Generate JUnit XML format for CI/CD systems"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        testsuites = Element('testsuites')
        
        for test_type, result in results.items():
            testsuite = SubElement(testsuites, 'testsuite')
            testsuite.set('name', test_type)
            testsuite.set('tests', str(result.get('total', 0)))
            testsuite.set('failures', str(result.get('failed', 0)))
            testsuite.set('errors', str(result.get('errors', 0)))
            testsuite.set('skipped', str(result.get('skipped', 0)))
            testsuite.set('time', str(result.get('duration', 0)))
            
            # Add individual test cases if available
            for test_case in result.get('test_cases', []):
                testcase = SubElement(testsuite, 'testcase')
                testcase.set('name', test_case.get('name', 'unknown'))
                testcase.set('classname', test_case.get('class', test_type))
                testcase.set('time', str(test_case.get('duration', 0)))
                
                if test_case.get('status') == 'failed':
                    failure = SubElement(testcase, 'failure')
                    failure.set('message', test_case.get('error', 'Test failed'))
                    failure.text = test_case.get('traceback', '')
                elif test_case.get('status') == 'skipped':
                    skipped = SubElement(testcase, 'skipped')
                    skipped.set('message', test_case.get('reason', 'Test skipped'))
        
        # Write formatted XML
        rough_string = tostring(testsuites, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))
    
    def _calculate_coverage(self, results: Dict) -> float:
        """Calculate overall test coverage"""
        total_coverage = 0.0
        count = 0
        
        for result in results.values():
            if 'coverage' in result:
                total_coverage += result['coverage']
                count += 1
        
        return total_coverage / count if count > 0 else 0.0
    
    def _determine_exit_code(self, results: Dict, env_config: Dict) -> int:
        """Determine exit code based on results and thresholds"""
        # Check for failures or errors
        total_failed = sum(r.get('failed', 0) for r in results.values())
        total_errors = sum(r.get('errors', 0) for r in results.values())
        
        if total_failed > 0 or total_errors > 0:
            return 1
        
        # Check coverage threshold
        coverage = self._calculate_coverage(results)
        threshold = env_config.get('coverage_threshold', self.config.get('coverage_threshold', 80.0))
        
        if coverage < threshold:
            self.logger.warning(f"Coverage {coverage:.1f}% below threshold {threshold:.1f}%")
            return 1
        
        return 0
    
    def _collect_artifacts(self) -> List[str]:
        """Collect test artifacts for archival"""
        artifacts = []
        
        # Collect log files
        for log_file in Path('ci_cd/logs').glob('*.log'):
            artifacts.append(str(log_file))
        
        # Collect report files
        for report_file in Path('ci_cd/reports').rglob('*'):
            if report_file.is_file():
                artifacts.append(str(report_file))
        
        # Collect coverage files
        for coverage_file in Path('.').glob('.coverage*'):
            artifacts.append(str(coverage_file))
        
        return artifacts
    
    def _wait_for_services(self, timeout: int = 30):
        """Wait for required services to be ready"""
        self.logger.info("Waiting for services to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.service_manager.check_all_services():
                self.logger.info("All services are ready")
                return
            time.sleep(2)
        
        self.logger.warning("Some services may not be ready")
    
    def _post_execution_cleanup(self):
        """Cleanup after test execution"""
        self.logger.info("Cleaning up test environment...")
        
        try:
            # Stop services if they were started
            self.service_manager.stop_all_services()
        except Exception as e:
            self.logger.warning(f"Cleanup warning: {e}")


def main():
    """Main entry point for automated test runner"""
    parser = argparse.ArgumentParser(description='Automated Test Runner for CI/CD')
    parser.add_argument('--environment', '-e', default='development',
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--test-types', '-t', nargs='+',
                       choices=['unit', 'integration', 'ui', 'e2e', 'performance', 'security'],
                       help='Test types to run')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--output', '-o', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = AutomatedTestRunner(args.config)
    
    # Run tests
    result = runner.run_automated_tests(
        environment=args.environment,
        test_types=args.test_types
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Environment: {args.environment}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Total Tests: {result.total_tests}")
    print(f"Passed: {result.passed}")
    print(f"Failed: {result.failed}")
    print(f"Skipped: {result.skipped}")
    print(f"Errors: {result.errors}")
    print(f"Coverage: {result.coverage_percentage:.1f}%")
    print(f"Exit Code: {result.exit_code}")
    print(f"Report: {result.report_path}")
    print(f"{'='*60}")
    
    # Save execution result
    result_file = Path('ci_cd/last_execution_result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()