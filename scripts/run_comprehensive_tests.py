#!/usr/bin/env python3
"""
Comprehensive Test Runner for GopiAI Project

Master test runner that executes all types of tests across all GopiAI modules.
Supports parallel execution, detailed reporting, and problem discovery.
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

# Add test infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from test_config import TestConfigManager, TestCategory, TestEnvironment
from problem_discovery import ProblemDiscovery


@dataclass
class TestResult:
    """Result of a test execution."""
    module: str
    category: str
    success: bool
    duration: float
    exit_code: int
    stdout: str
    stderr: str
    coverage_percentage: Optional[float] = None
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0


class ComprehensiveTestRunner:
    """Master test runner for all GopiAI modules."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.config_manager = TestConfigManager(root_path)
        self.logger = self._setup_logging()
        self.results: List[TestResult] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the test runner."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_runner.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def discover_problems(self) -> Dict:
        """Discover and categorize existing problems."""
        self.logger.info("Discovering existing problems in codebase...")
        
        discovery = ProblemDiscovery(str(self.root_path))
        problems = discovery.discover_all_problems()
        report = discovery.generate_report("problem_discovery_report.json")
        discovery.generate_pytest_markers("test_infrastructure/pytest_markers.py")
        
        self.logger.info(f"Discovered {len(problems)} problems")
        return report
    
    def validate_environments(self) -> bool:
        """Validate that all required test environments are available."""
        self.logger.info("Validating test environments...")
        
        all_valid = True
        for env in TestEnvironment:
            if self.config_manager.validate_environment(env):
                self.logger.info(f"✓ Environment {env.value} is valid")
            else:
                self.logger.warning(f"✗ Environment {env.value} is not available")
                all_valid = False
        
        return all_valid
    
    def run_module_tests(self, module_name: str, category: Optional[TestCategory] = None,
                        timeout: Optional[int] = None) -> TestResult:
        """Run tests for a specific module and category."""
        module_config = self.config_manager.get_module_config(module_name)
        if not module_config:
            raise ValueError(f"Module {module_name} not found")
        
        if category and category not in module_config.test_categories:
            self.logger.warning(f"Category {category.value} not supported by {module_name}")
            return TestResult(
                module=module_name,
                category=category.value if category else "all",
                success=False,
                duration=0.0,
                exit_code=-1,
                stdout="",
                stderr=f"Category {category.value} not supported"
            )
        
        # Create test command
        try:
            cmd = self.config_manager.create_test_command(module_name, category)
        except Exception as e:
            self.logger.error(f"Failed to create test command for {module_name}: {e}")
            return TestResult(
                module=module_name,
                category=category.value if category else "all",
                success=False,
                duration=0.0,
                exit_code=-1,
                stdout="",
                stderr=str(e)
            )
        
        # Set timeout
        test_timeout = timeout or module_config.timeout_seconds
        
        self.logger.info(f"Running {module_name} tests ({category.value if category else 'all'})...")
        self.logger.debug(f"Command: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            # Change to module directory
            original_cwd = os.getcwd()
            os.chdir(module_config.path)
            
            # Run the test command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=test_timeout,
                cwd=module_config.path
            )
            
            duration = time.time() - start_time
            
            # Parse test results from output
            test_count, passed_count, failed_count, skipped_count = self._parse_pytest_output(result.stdout)
            coverage_percentage = self._parse_coverage_output(result.stdout)
            
            test_result = TestResult(
                module=module_name,
                category=category.value if category else "all",
                success=result.returncode == 0,
                duration=duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                coverage_percentage=coverage_percentage,
                test_count=test_count,
                passed_count=passed_count,
                failed_count=failed_count,
                skipped_count=skipped_count
            )
            
            if test_result.success:
                self.logger.info(f"✓ {module_name} tests passed ({duration:.2f}s)")
            else:
                self.logger.error(f"✗ {module_name} tests failed ({duration:.2f}s)")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr[:500]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error(f"✗ {module_name} tests timed out after {test_timeout}s")
            return TestResult(
                module=module_name,
                category=category.value if category else "all",
                success=False,
                duration=duration,
                exit_code=-1,
                stdout="",
                stderr=f"Test execution timed out after {test_timeout} seconds"
            )
        
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"✗ {module_name} tests failed with exception: {e}")
            return TestResult(
                module=module_name,
                category=category.value if category else "all",
                success=False,
                duration=duration,
                exit_code=-1,
                stdout="",
                stderr=str(e)
            )
        
        finally:
            os.chdir(original_cwd)
    
    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int, int]:
        """Parse pytest output to extract test counts."""
        import re
        
        # Look for pytest summary line like "5 passed, 2 failed, 1 skipped"
        pattern = r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?'
        match = re.search(pattern, output)
        
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2)) if match.group(2) else 0
            skipped = int(match.group(3)) if match.group(3) else 0
            total = passed + failed + skipped
            return total, passed, failed, skipped
        
        return 0, 0, 0, 0
    
    def _parse_coverage_output(self, output: str) -> Optional[float]:
        """Parse coverage percentage from pytest output."""
        import re
        
        # Look for coverage percentage like "TOTAL 85%"
        pattern = r'TOTAL.*?(\d+)%'
        match = re.search(pattern, output)
        
        if match:
            return float(match.group(1))
        
        return None
    
    def run_all_tests(self, parallel: bool = True, categories: List[TestCategory] = None) -> List[TestResult]:
        """Run all tests across all modules."""
        self.logger.info("Starting comprehensive test run...")
        
        # Discover problems first
        problem_report = self.discover_problems()
        
        # Validate environments
        if not self.validate_environments():
            self.logger.warning("Some environments are not available - some tests may be skipped")
        
        # Prepare test tasks
        tasks = []
        for module_name, module_config in self.config_manager.config.modules.items():
            test_categories = categories or module_config.test_categories
            
            for category in test_categories:
                if category in module_config.test_categories:
                    tasks.append((module_name, category))
        
        self.logger.info(f"Prepared {len(tasks)} test tasks")
        
        # Execute tests
        if parallel and len(tasks) > 1:
            self.results = self._run_tests_parallel(tasks)
        else:
            self.results = self._run_tests_sequential(tasks)
        
        # Generate comprehensive report
        self._generate_comprehensive_report(problem_report)
        
        return self.results
    
    def _run_tests_parallel(self, tasks: List[Tuple[str, TestCategory]]) -> List[TestResult]:
        """Run tests in parallel."""
        results = []
        max_workers = min(self.config_manager.config.max_workers, len(tasks))
        
        self.logger.info(f"Running tests in parallel with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.run_module_tests, module, category): (module, category)
                for module, category in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                module, category = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Test task {module}:{category.value} failed: {e}")
                    results.append(TestResult(
                        module=module,
                        category=category.value,
                        success=False,
                        duration=0.0,
                        exit_code=-1,
                        stdout="",
                        stderr=str(e)
                    ))
        
        return results
    
    def _run_tests_sequential(self, tasks: List[Tuple[str, TestCategory]]) -> List[TestResult]:
        """Run tests sequentially."""
        results = []
        
        self.logger.info("Running tests sequentially")
        
        for module, category in tasks:
            try:
                result = self.run_module_tests(module, category)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Test task {module}:{category.value} failed: {e}")
                results.append(TestResult(
                    module=module,
                    category=category.value,
                    success=False,
                    duration=0.0,
                    exit_code=-1,
                    stdout="",
                    stderr=str(e)
                ))
        
        return results
    
    def _generate_comprehensive_report(self, problem_report: Dict):
        """Generate a comprehensive test report."""
        total_tests = sum(r.test_count for r in self.results)
        total_passed = sum(r.passed_count for r in self.results)
        total_failed = sum(r.failed_count for r in self.results)
        total_skipped = sum(r.skipped_count for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        successful_runs = sum(1 for r in self.results if r.success)
        total_runs = len(self.results)
        
        # Calculate average coverage
        coverage_results = [r.coverage_percentage for r in self.results if r.coverage_percentage is not None]
        avg_coverage = sum(coverage_results) / len(coverage_results) if coverage_results else 0
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_test_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": total_runs - successful_runs,
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "skipped_tests": total_skipped,
                "total_duration_seconds": total_duration,
                "average_coverage_percentage": avg_coverage
            },
            "results_by_module": {},
            "problem_discovery": problem_report,
            "detailed_results": [asdict(result) for result in self.results]
        }
        
        # Group results by module
        for result in self.results:
            if result.module not in report["results_by_module"]:
                report["results_by_module"][result.module] = []
            report["results_by_module"][result.module].append(asdict(result))
        
        # Write report
        report_file = f"comprehensive_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Comprehensive test report written to {report_file}")
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT SUMMARY")
        print("="*80)
        print(f"Total Test Runs: {total_runs}")
        print(f"Successful Runs: {successful_runs}")
        print(f"Failed Runs: {total_runs - successful_runs}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Skipped: {total_skipped}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Average Coverage: {avg_coverage:.1f}%")
        print(f"Problems Discovered: {problem_report['summary']['total_problems']}")
        print("="*80)
        
        return report


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner for GopiAI")
    parser.add_argument("--module", help="Run tests for specific module only")
    parser.add_argument("--category", help="Run specific test category only")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially instead of parallel")
    parser.add_argument("--discover-only", action="store_true", help="Only run problem discovery")
    parser.add_argument("--validate-only", action="store_true", help="Only validate environments")
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.validate_only:
        runner.validate_environments()
        return
    
    if args.discover_only:
        runner.discover_problems()
        return
    
    if args.module:
        # Run tests for specific module
        category = TestCategory(args.category) if args.category else None
        result = runner.run_module_tests(args.module, category)
        print(f"Test result: {'PASSED' if result.success else 'FAILED'}")
        if not result.success:
            print(f"Error: {result.stderr}")
        return
    
    # Run all tests
    categories = [TestCategory(args.category)] if args.category else None
    results = runner.run_all_tests(parallel=not args.sequential, categories=categories)
    
    # Exit with error code if any tests failed
    if any(not result.success for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()