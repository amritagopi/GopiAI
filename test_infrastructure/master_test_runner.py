#!/usr/bin/env python3
"""
Master Test Runner for GopiAI Testing Infrastructure

Enhanced master test runner that provides:
- Single entry point for all test types
- Parallel execution of independent tests  
- Test prioritization by importance
- Automatic retry for unstable tests
- Comprehensive reporting and analysis

This module provides a unified interface for running tests across all GopiAI modules
with proper environment management and service coordination.
"""
import sys
import subprocess
import logging
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import random

from test_discovery import TestDiscovery, TestCategory
from problem_discovery import ProblemDiscovery

# Try to import service manager, but handle gracefully if not available
try:
    from service_manager import ServiceManager
    SERVICE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ServiceManager not available: {e}")
    SERVICE_MANAGER_AVAILABLE = False
    
    class MockServiceManager:
        """Mock service manager for when the real one is not available."""
        def start_crewai_server(self): return True
        def start_ui_application(self): return True
        def start_memory_system(self): return True
        def stop_all_services(self): return True
        def start_all_services(self): return True
        def check_service_health(self, service): return True
    
    ServiceManager = MockServiceManager


class TestResult(Enum):
    """Test execution results."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    RETRY = "retry"


class TestPriority(Enum):
    """Test priority levels for execution ordering."""
    CRITICAL = 1    # Core functionality tests
    HIGH = 2        # Important feature tests
    MEDIUM = 3      # Standard tests
    LOW = 4         # Optional/slow tests


@dataclass
class TestExecution:
    """Represents a test execution result."""
    module: str
    category: str
    command: str
    result: TestResult
    duration: float
    output: str
    error_output: str
    exit_code: int
    retry_count: int = 0
    priority: TestPriority = TestPriority.MEDIUM
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class RetryConfig:
    """Configuration for test retry behavior."""
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    retry_on_exit_codes: List[int] = None
    
    def __post_init__(self):
        if self.retry_on_exit_codes is None:
            # Common exit codes that indicate transient failures
            self.retry_on_exit_codes = [1, 2, 130]  # General errors, timeout, interrupted


class MasterTestRunner:
    """Enhanced master test runner for all GopiAI modules with prioritization and retry logic."""
    
    def __init__(self, root_path: str = ".", max_workers: int = 4, retry_config: RetryConfig = None):
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        self.retry_config = retry_config or RetryConfig()
        
        if SERVICE_MANAGER_AVAILABLE:
            self.service_manager = ServiceManager()
        else:
            self.service_manager = MockServiceManager()
            self.logger.warning("Using mock service manager - services will not be started")
        
        self.test_discovery = TestDiscovery(root_path)
        self.problem_discovery = ProblemDiscovery(root_path)
        
        # Test execution results and tracking
        self.executions: List[TestExecution] = []
        self.failed_tests: Set[str] = set()
        self.retry_queue: queue.Queue = queue.Queue()
        self.execution_lock = threading.Lock()
        
        # Test prioritization mapping
        self.priority_mapping = self._create_priority_mapping()
    
    def _create_priority_mapping(self) -> Dict[str, TestPriority]:
        """Create mapping of test patterns to priorities."""
        return {
            # Critical tests - core functionality
            "test_interfaces": TestPriority.CRITICAL,
            "test_exceptions": TestPriority.CRITICAL,
            "test_schema": TestPriority.CRITICAL,
            "test_api_server": TestPriority.CRITICAL,
            "test_main_window": TestPriority.CRITICAL,
            
            # High priority - important features
            "test_integration": TestPriority.HIGH,
            "test_authentication": TestPriority.HIGH,
            "test_model_switching": TestPriority.HIGH,
            "test_memory_system": TestPriority.HIGH,
            
            # Medium priority - standard functionality
            "test_ui": TestPriority.MEDIUM,
            "test_settings": TestPriority.MEDIUM,
            "test_theme": TestPriority.MEDIUM,
            
            # Low priority - performance and optional tests
            "test_performance": TestPriority.LOW,
            "test_benchmark": TestPriority.LOW,
            "test_load": TestPriority.LOW,
        }
    
    def _determine_test_priority(self, test_module: str, test_category: str) -> TestPriority:
        """Determine priority for a test based on its module and category."""
        # Check for specific test patterns
        for pattern, priority in self.priority_mapping.items():
            if pattern in test_module.lower():
                return priority
        
        # Category-based priority
        category_priorities = {
            TestCategory.UNIT: TestPriority.HIGH,
            TestCategory.INTEGRATION: TestPriority.HIGH,
            TestCategory.UI: TestPriority.MEDIUM,
            TestCategory.E2E: TestPriority.MEDIUM,
            TestCategory.SECURITY: TestPriority.HIGH,
            TestCategory.PERFORMANCE: TestPriority.LOW,
        }
        
        try:
            category_enum = TestCategory(test_category)
            return category_priorities.get(category_enum, TestPriority.MEDIUM)
        except ValueError:
            return TestPriority.MEDIUM

    def run_all_tests(self, 
                     categories: Optional[List[TestCategory]] = None,
                     environments: Optional[List[TestEnvironment]] = None,
                     parallel: bool = True,
                     prioritize: bool = True,
                     enable_retry: bool = True,
                     generate_reports: bool = True) -> Dict:
        """
        Run all tests with specified filters, prioritization, and retry logic.
        
        Args:
            categories: Test categories to run (None for all)
            environments: Test environments to use (None for all)
            parallel: Enable parallel execution
            prioritize: Enable test prioritization
            enable_retry: Enable automatic retry for failed tests
            generate_reports: Generate comprehensive reports
        """
        self.logger.info("🚀 Starting enhanced master test runner")
        
        # Discover tests
        test_modules = self.test_discovery.discover_all_tests()
        self.logger.info(f"📊 Discovered {len(test_modules)} test modules")
        
        # Filter tests if specified
        if categories:
            test_modules = [m for m in test_modules if m.category in categories]
        
        
        self.logger.info(f"🎯 Running {len(test_modules)} test modules after filtering")
        
        # Create test execution plan with priorities
        execution_plan = self._create_execution_plan(test_modules, prioritize)
        
        # Execute tests based on plan
        if parallel and len(execution_plan) > 1:
            self._run_tests_parallel(execution_plan, enable_retry)
        else:
            self._run_tests_sequential(execution_plan, enable_retry)
        
        # Process retry queue if enabled
        if enable_retry and not self.retry_queue.empty():
            self._process_retry_queue()
        
        # Generate reports if requested
        if generate_reports:
            self._generate_execution_report()
            self._generate_problem_report()
        
        return self._create_summary()
    
    def _create_execution_plan(self, test_modules: List, prioritize: bool = True) -> List[Tuple[str, str, TestPriority, List[str]]]:
        """Create an execution plan with priorities and dependencies."""
        execution_plan = []
        
        # Group tests by GopiAI module for efficient execution
        module_groups = {}
        for test_module in test_modules:
            gopiai_module = test_module.module_name
            if gopiai_module not in module_groups:
                module_groups[gopiai_module] = []
            module_groups[gopiai_module].append(test_module)
        
        # Create tasks for each module/category combination
        for gopiai_module, test_modules_list in module_groups.items():
            category_groups = {}
            for test_module in test_modules_list:
                category = test_module.category
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(test_module)
            
            for category, modules_in_category in category_groups.items():
                priority = self._determine_test_priority(gopiai_module, category.value)
                dependencies = self._determine_dependencies(gopiai_module, category.value)
                
                task = (gopiai_module, category.value, priority, dependencies)
                execution_plan.append(task)
        
        # Sort by priority if enabled
        if prioritize:
            execution_plan.sort(key=lambda x: x[3].value)  # Sort by priority value
            self.logger.info(f"📋 Execution plan prioritized: {len(execution_plan)} tasks")
        
        return execution_plan
    
    def _determine_dependencies(self, module: str, category: str) -> List[str]:
        """Determine dependencies for a test module/category."""
        dependencies = []
        
        # Core tests should run first
        if module == "GopiAI-Core":
            return []
        
        # UI tests depend on core
        if module == "GopiAI-UI":
            dependencies.append("GopiAI-Core:unit")
        
        # CrewAI tests depend on core
        if module == "GopiAI-CrewAI":
            dependencies.append("GopiAI-Core:unit")
        
        # Integration tests depend on unit tests
        if category == "integration":
            dependencies.append(f"{module}:unit")
        
        # E2E tests depend on integration tests
        if category == "e2e":
            dependencies.extend([f"{module}:unit", f"{module}:integration"])
        
        return dependencies
    
    def _run_tests_parallel(self, execution_plan: List, enable_retry: bool = True):
        """Run tests in parallel with dependency management."""
        self.logger.info(f"⚡ Running tests in parallel with {self.max_workers} workers")
        
        completed_tasks = set()
        task_futures = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit initial tasks that have no dependencies
            for task in execution_plan:
                module, category, priority, dependencies = task
                
                if not dependencies or all(dep in completed_tasks for dep in dependencies):
                    future = executor.submit(self._execute_test_task, module, category, environment, priority)
                    task_futures[future] = task
            
            # Process completed tasks and submit new ones
            while task_futures:
                for future in as_completed(list(task_futures.keys())):
                    task = task_futures.pop(future)
                    module, category, environment, priority, dependencies = task
                    
                    try:
                        execution = future.result()
                        with self.execution_lock:
                            self.executions.append(execution)
                        
                        task_key = f"{module}:{category}"
                        completed_tasks.add(task_key)
                        
                        # Check if we can submit more tasks
                        for remaining_task in execution_plan:
                            r_module, r_category, r_environment, r_priority, r_dependencies = remaining_task
                            r_task_key = f"{r_module}:{r_category}"
                            
                            if (r_task_key not in completed_tasks and 
                                all(dep in completed_tasks for dep in r_dependencies)):
                                
                                future = executor.submit(self._execute_test_task, r_module, r_category, r_priority)
                                task_futures[future] = remaining_task
                        
                        # Handle retry if test failed and retry is enabled
                        if enable_retry and execution.result in [TestResult.FAILED, TestResult.ERROR]:
                            if execution.retry_count < self.retry_config.max_retries:
                                self.retry_queue.put(execution)
                    
                    except Exception as e:
                        self.logger.error(f"❌ Task execution failed: {e}")
    
    def _run_tests_sequential(self, execution_plan: List, enable_retry: bool = True):
        """Run tests sequentially with dependency management."""
        self.logger.info("🔄 Running tests sequentially")
        
        completed_tasks = set()
        
        # Keep trying to execute tasks until all are complete
        while len(completed_tasks) < len(execution_plan):
            progress_made = False
            
            for task in execution_plan:
                module, category, priority, dependencies = task
                task_key = f"{module}:{category}"
                
                if task_key in completed_tasks:
                    continue
                
                # Check if dependencies are satisfied
                if all(dep in completed_tasks for dep in dependencies):
                    execution = self._execute_test_task(module, category, environment, priority)
                    self.executions.append(execution)
                    completed_tasks.add(task_key)
                    progress_made = True
                    
                    # Handle retry if test failed and retry is enabled
                    if enable_retry and execution.result in [TestResult.FAILED, TestResult.ERROR]:
                        if execution.retry_count < self.retry_config.max_retries:
                            self.retry_queue.put(execution)
            
            if not progress_made:
                # If no progress was made, there might be circular dependencies
                # Execute remaining tasks anyway
                self.logger.warning("⚠️ Possible circular dependencies detected, executing remaining tasks")
                for task in execution_plan:
                    module, category, environment, priority, dependencies = task
                    task_key = f"{module}:{category}"
                    
                    if task_key not in completed_tasks:
                        execution = self._execute_test_task(module, category, environment, priority)
                        self.executions.append(execution)
                        completed_tasks.add(task_key)
                break

    def _process_retry_queue(self):
        """Process the retry queue for failed tests."""
        self.logger.info(f"🔄 Processing retry queue with {self.retry_queue.qsize()} tests")
        
        retry_executions = []
        while not self.retry_queue.empty():
            failed_execution = self.retry_queue.get()
            
            # Calculate retry delay with exponential backoff
            delay = self.retry_config.retry_delay
            if self.retry_config.exponential_backoff:
                delay *= (2 ** failed_execution.retry_count)
            
            # Add some jitter to avoid thundering herd
            delay += random.uniform(0, 0.5)
            
            self.logger.info(f"⏳ Retrying {failed_execution.module}:{failed_execution.category} "
                           f"(attempt {failed_execution.retry_count + 1}/{self.retry_config.max_retries}) "
                           f"after {delay:.1f}s delay")
            
            time.sleep(delay)
            
            # Retry the test
            retry_execution = self._execute_test_task(
                failed_execution.module,
                failed_execution.category,
                failed_execution.environment,
                failed_execution.priority,
                failed_execution.retry_count + 1
            )
            
            retry_executions.append(retry_execution)
            
            # If still failing and retries remaining, add back to queue
            if (retry_execution.result in [TestResult.FAILED, TestResult.ERROR] and
                retry_execution.retry_count < self.retry_config.max_retries):
                self.retry_queue.put(retry_execution)
        
        # Add retry executions to main results
        self.executions.extend(retry_executions)
    
    def _execute_test_task(self, module: str, category: str, priority: TestPriority, retry_count: int = 0) -> TestExecution:
        """Execute a single test task with enhanced error handling."""
        self.logger.info(f"🧪 Executing {module}:{category} (priority: {priority.name}, retry: {retry_count})")
        
        python_exe = sys.executable
        module_path = self.root_path / module
        
        if not module_path.exists():
            self.logger.error(f"❌ Module path {module_path} does not exist")
            return TestExecution(
                module=module,
                category=category,
                environment=environment,
                command="",
                result=TestResult.ERROR,
                duration=0.0,
                output="",
                error_output=f"Module path {module_path} does not exist",
                exit_code=-1,
                retry_count=retry_count,
                priority=priority
            )
        
        # Build command
        cmd = [
            str(python_exe),
            "-m", "pytest",
            "-v",
            "--tb=short",
            "--color=yes",
            f"--junitxml=test_results_{module}_{category}_retry{retry_count}.xml"
        ]
        
        # Add HTML report if pytest-html is available
        try:
            import pytest_html
            cmd.extend([f"--html=test_report_{module}_{category}_retry{retry_count}.html", "--self-contained-html"])
        except ImportError:
            pass
        
        # Add test path
        test_path = module_path / "tests"
        if category != "all":
            # Try to find category-specific tests
            category_path = test_path / category
            if category_path.exists():
                cmd.append(str(category_path))
            else:
                # Use marker to filter tests
                cmd.extend([str(test_path), "-m", category])
        else:
            cmd.append(str(test_path))
        
        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=module_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Determine result status
            if result.returncode == 0:
                status = TestResult.PASSED
                self.logger.info(f"✅ {module}:{category} passed in {duration:.2f}s")
            elif result.returncode == 5:  # No tests collected
                status = TestResult.SKIPPED
                self.logger.warning(f"⊝ {module}:{category} skipped (no tests) in {duration:.2f}s")
            elif result.returncode in self.retry_config.retry_on_exit_codes:
                status = TestResult.FAILED
                self.logger.error(f"❌ {module}:{category} failed (retryable) in {duration:.2f}s")
            else:
                status = TestResult.ERROR
                self.logger.error(f"💥 {module}:{category} error in {duration:.2f}s")
            
            return TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=status,
                duration=duration,
                output=result.stdout,
                error_output=result.stderr,
                exit_code=result.returncode,
                retry_count=retry_count,
                priority=priority
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error(f"⏰ {module}:{category} timed out after {duration:.2f}s")
            return TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=TestResult.ERROR,
                duration=duration,
                output="",
                error_output="Test execution timed out",
                exit_code=-1,
                retry_count=retry_count,
                priority=priority
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"💥 {module}:{category} failed with exception: {e}")
            return TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=TestResult.ERROR,
                duration=duration,
                output="",
                error_output=str(e),
                exit_code=-1,
                retry_count=retry_count,
                priority=priority
            )

    def run_unit_tests(self, modules: Optional[List[str]] = None, **kwargs) -> Dict:
        """Run unit tests for specified modules."""
        return self.run_all_tests(
            categories=[TestCategory.UNIT],
            environments=None,
            **kwargs
        )

    def run_integration_tests(self, services: Optional[List[str]] = None, **kwargs) -> Dict:
        """Run integration tests with optional service filtering."""
        # Start required services
        if services is None or "crewai_server" in services:
            self.service_manager.start_crewai_server()
        
        try:
            return self.run_all_tests(
                categories=[TestCategory.INTEGRATION],
                environments=None,
                **kwargs
            )
        finally:
            # Clean up services
            self.service_manager.stop_all_services()

    def run_ui_tests(self, components: Optional[List[str]] = None, **kwargs) -> Dict:
        """Run UI tests with optional component filtering."""
        return self.run_all_tests(
            categories=[TestCategory.UI],
            **kwargs
        )

    def run_e2e_tests(self, scenarios: Optional[List[str]] = None, **kwargs) -> Dict:
        """Run end-to-end tests with optional scenario filtering."""
        # Start all required services
        self.service_manager.start_all_services()
        
        try:
            return self.run_all_tests(
                categories=[TestCategory.E2E],
                environments=None,
                **kwargs
            )
        finally:
            # Clean up services
            self.service_manager.stop_all_services()

    def run_performance_tests(self, **kwargs) -> Dict:
        """Run performance tests."""
        return self.run_all_tests(
            categories=[TestCategory.PERFORMANCE],
            environments=None,
            **kwargs
        )

    def run_security_tests(self, **kwargs) -> Dict:
        """Run security tests."""
        return self.run_all_tests(
            categories=[TestCategory.SECURITY],
            environments=None,
            **kwargs
        )



    def _generate_execution_report(self):
        """Generate a comprehensive test execution report."""
        report = {
            "summary": {
                "total_executions": len(self.executions),
                "total_duration": sum(e.duration for e in self.executions),
                "by_result": {},
                "by_module": {},
                "by_category": {}
            },
            "executions": []
        }
        
        # Convert executions to serializable format
        for execution in self.executions:
            exec_dict = asdict(execution)
            exec_dict["result"] = execution.result.value
            exec_dict["priority"] = execution.priority.name
            report["executions"].append(exec_dict)
        
        # Calculate summary statistics
        for execution in self.executions:
            # By result
            result = execution.result.value
            report["summary"]["by_result"][result] = report["summary"]["by_result"].get(result, 0) + 1
            
            # By module
            module = execution.module
            report["summary"]["by_module"][module] = report["summary"]["by_module"].get(module, 0) + 1
            
            # By category
            category = execution.category
            report["summary"]["by_category"][category] = report["summary"]["by_category"].get(category, 0) + 1
            
            
        
        # Write report
        report_file = "test_execution_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test execution report written to {report_file}")
        
        # Generate comprehensive analysis reports
        self._generate_analysis_reports()
    
    def _generate_analysis_reports(self):
        """Generate comprehensive analysis reports after test execution."""
        try:
            print("\n🔍 Generating comprehensive analysis reports...")
            
            # Import reporting components
            try:
                from .master_reporter import MasterReporter
                
                # Generate master report without running tests again
                reporter = MasterReporter(str(self.root_path))
                master_report = reporter.generate_master_report(
                    run_tests=False,  # Don't run tests again
                    generate_dashboard=True
                )
                
                if master_report:
                    print("✅ Comprehensive analysis reports generated")
                    if master_report.dashboard_url:
                        print(f"🌐 Dashboard available at: {master_report.dashboard_url}")
                else:
                    print("⚠️ Some analysis reports may have failed")
                    
            except ImportError as e:
                print(f"⚠️ Reporting system not available: {e}")
                print("You can generate reports manually with: python generate_test_reports.py --no-tests")
                
        except Exception as e:
            print(f"⚠️ Failed to generate analysis reports: {e}")
            print("You can generate them manually with: python generate_test_reports.py --no-tests")

    def _generate_problem_report(self):
        """Generate a problem discovery report."""
        problems = self.problem_discovery.discover_all_problems()
        self.problem_discovery.generate_report("test_problems_report.json")
        self.problem_discovery.generate_pytest_markers("test_known_issues.py")

    def _create_summary(self) -> Dict:
        """Create a comprehensive summary of test execution results."""
        total_retries = sum(e.retry_count for e in self.executions)
        
        summary = {
            "total_executions": len(self.executions),
            "passed": len([e for e in self.executions if e.result == TestResult.PASSED]),
            "failed": len([e for e in self.executions if e.result == TestResult.FAILED]),
            "skipped": len([e for e in self.executions if e.result == TestResult.SKIPPED]),
            "errors": len([e for e in self.executions if e.result == TestResult.ERROR]),
            "total_duration": sum(e.duration for e in self.executions),
            "total_retries": total_retries,
            "success_rate": 0.0,
            "by_priority": {},
            "by_environment": {},
            "by_category": {},
            "retry_statistics": {
                "tests_retried": len([e for e in self.executions if e.retry_count > 0]),
                "successful_retries": len([e for e in self.executions if e.retry_count > 0 and e.result == TestResult.PASSED]),
                "failed_after_retry": len([e for e in self.executions if e.retry_count > 0 and e.result in [TestResult.FAILED, TestResult.ERROR]])
            }
        }
        
        if summary["total_executions"] > 0:
            summary["success_rate"] = summary["passed"] / summary["total_executions"] * 100
        
        # Calculate statistics by priority
        for execution in self.executions:
            priority = execution.priority.name
            if priority not in summary["by_priority"]:
                summary["by_priority"][priority] = {"total": 0, "passed": 0, "failed": 0}
            
            summary["by_priority"][priority]["total"] += 1
            if execution.result == TestResult.PASSED:
                summary["by_priority"][priority]["passed"] += 1
            elif execution.result in [TestResult.FAILED, TestResult.ERROR]:
                summary["by_priority"][priority]["failed"] += 1
        
        
        
        # Calculate statistics by category
        for execution in self.executions:
            category = execution.category
            if category not in summary["by_category"]:
                summary["by_category"][category] = {"total": 0, "passed": 0, "failed": 0}
            
            summary["by_category"][category]["total"] += 1
            if execution.result == TestResult.PASSED:
                summary["by_category"][category]["passed"] += 1
            elif execution.result in [TestResult.FAILED, TestResult.ERROR]:
                summary["by_category"][category]["failed"] += 1
        
        return summary


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Enhanced GopiAI Master Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python master_test_runner.py --all                    # Run all tests with defaults
  python master_test_runner.py --unit --parallel        # Run unit tests in parallel
  python master_test_runner.py --integration --no-retry # Run integration tests without retry
  python master_test_runner.py --category ui --sequential # Run UI tests sequentially
  python master_test_runner.py --priority-only          # Run only critical/high priority tests
  python master_test_runner.py --max-workers 8          # Use 8 parallel workers
        """
    )
    
    # Test selection
    test_group = parser.add_argument_group('Test Selection')
    test_group.add_argument("--all", action="store_true", help="Run all tests")
    test_group.add_argument("--category", choices=["unit", "integration", "ui", "e2e", "performance", "security"],
                           help="Run tests of specific category")
    test_group.add_argument("--priority-only", action="store_true", 
                           help="Run only critical and high priority tests")
    
    # Execution options
    exec_group = parser.add_argument_group('Execution Options')
    exec_group.add_argument("--parallel", action="store_true", default=True,
                           help="Run tests in parallel (default)")
    exec_group.add_argument("--sequential", action="store_true", 
                           help="Run tests sequentially")
    exec_group.add_argument("--max-workers", type=int, default=4,
                           help="Maximum number of parallel workers (default: 4)")
    exec_group.add_argument("--no-prioritize", action="store_true",
                           help="Disable test prioritization")
    
    # Retry options
    retry_group = parser.add_argument_group('Retry Options')
    retry_group.add_argument("--no-retry", action="store_true", 
                           help="Disable automatic retry for failed tests")
    retry_group.add_argument("--max-retries", type=int, default=3,
                           help="Maximum number of retries per test (default: 3)")
    retry_group.add_argument("--retry-delay", type=float, default=1.0,
                           help="Base delay between retries in seconds (default: 1.0)")
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument("--no-reports", action="store_true", 
                             help="Skip report generation")
    output_group.add_argument("--verbose", "-v", action="store_true", 
                             help="Verbose logging")
    output_group.add_argument("--quiet", "-q", action="store_true",
                             help="Quiet mode (errors only)")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('master_test_runner.log')
        ]
    )
    
    # Create retry configuration
    retry_config = RetryConfig(
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        exponential_backoff=True
    )
    
    # Create runner
    runner = MasterTestRunner(
        max_workers=args.max_workers,
        retry_config=retry_config
    )
    
    # Determine what to run
    categories = None
    if args.all:
        categories = list(TestCategory)
    elif args.category:
        categories = [TestCategory(args.category)]
    elif args.priority_only:
        # Run tests that are typically critical/high priority
        categories = [TestCategory.UNIT, TestCategory.INTEGRATION, TestCategory.SECURITY]
    else:
        # Default to unit tests
        categories = [TestCategory.UNIT]
    
    environments = None
    if args.environment:
        environments = [TestEnvironment(args.environment)]
    
    # Determine execution mode
    parallel = args.parallel and not args.sequential
    prioritize = not args.no_prioritize
    enable_retry = not args.no_retry
    
    print("🚀 Starting Enhanced GopiAI Master Test Runner")
    print(f"📊 Configuration:")
    print(f"   Categories: {[c.value for c in categories] if categories else 'all'}")
    print(f"   Environments: {[e.value for e in environments] if environments else 'all'}")
    print(f"   Parallel: {parallel} (workers: {args.max_workers})")
    print(f"   Prioritization: {prioritize}")
    print(f"   Retry: {enable_retry} (max: {args.max_retries})")
    print()
    
    try:
        # Run tests
        summary = runner.run_all_tests(
            categories=categories,
            parallel=parallel,
            prioritize=prioritize,
            enable_retry=enable_retry,
            generate_reports=not args.no_reports
        )
        
        # Print comprehensive summary
        print("\n" + "="*70)
        print("🎯 ENHANCED TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"📊 Total executions: {summary['total_executions']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⊝ Skipped: {summary['skipped']}")
        print(f"💥 Errors: {summary['errors']}")
        print(f"🔄 Total retries: {summary['total_retries']}")
        print(f"📈 Success rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Total duration: {summary['total_duration']:.2f}s")
        
        # Print priority breakdown
        if summary['by_priority']:
            print(f"\n🎯 Results by Priority:")
            for priority, stats in summary['by_priority'].items():
                success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"   {priority}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Print retry statistics
        if summary['retry_statistics']['tests_retried'] > 0:
            retry_stats = summary['retry_statistics']
            print(f"\n🔄 Retry Statistics:")
            print(f"   Tests retried: {retry_stats['tests_retried']}")
            print(f"   Successful after retry: {retry_stats['successful_retries']}")
            print(f"   Failed after retry: {retry_stats['failed_after_retry']}")
        
        print("="*70)
        
        # Exit with appropriate code
        if summary['failed'] > 0 or summary['errors'] > 0:
            print("❌ Some tests failed - check logs for details")
            sys.exit(1)
        else:
            print("✅ All tests passed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()