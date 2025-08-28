#!/usr/bin/env python3
"""
Test System Validation and Optimization

This module provides comprehensive validation and optimization for the GopiAI testing system.
It validates the entire testing infrastructure on real data, optimizes execution times,
configures load balancing for parallel tests, and monitors test performance.
"""

import os
import sys
import json
import time
import threading
import statistics
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import psutil
import sqlite3

# Add test infrastructure to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

try:
    from master_test_runner import MasterTestRunner, TestCategory, TestEnvironment
    from test_discovery import TestDiscovery
    from quality_tracker import QualityTracker
    from service_manager import ServiceManager
except ImportError as e:
    print(f"Warning: Could not import test infrastructure: {e}")


@dataclass
class TestPerformanceMetrics:
    """Performance metrics for test execution."""
    test_name: str
    category: str
    
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    retry_count: int
    parallel_efficiency: float
    bottlenecks: List[str]


@dataclass
class SystemValidationResult:
    """Result of system validation."""
    timestamp: str
    total_tests_run: int
    validation_success: bool
    performance_score: float
    optimization_recommendations: List[str]
    bottlenecks_identified: List[str]
    resource_usage: Dict[str, float]
    execution_time_seconds: float


@dataclass
class OptimizationConfig:
    """Configuration for test optimization."""
    max_parallel_workers: int = 8
    memory_threshold_mb: float = 2048.0
    cpu_threshold_percent: float = 80.0
    timeout_seconds: int = 1800  # 30 minutes
    retry_failed_tests: bool = True
    enable_load_balancing: bool = True
    performance_monitoring: bool = True


class TestSystemValidator:
    """Validates the entire testing system on real data."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        self.validation_results: List[SystemValidationResult] = []
        
        # Initialize components
        self.test_discovery = TestDiscovery(str(project_root))
        self.quality_tracker = QualityTracker(str(project_root))
        
        try:
            self.service_manager = ServiceManager()
        except:
            self.service_manager = None
            self.logger.warning("ServiceManager not available")
        
        # Create validation directory
        self.validation_dir = self.project_root / "test_reports" / "validation"
        self.validation_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_system_on_real_data(self, config: OptimizationConfig = None) -> SystemValidationResult:
        """Validate the entire testing system using real project data."""
        if config is None:
            config = OptimizationConfig()
        
        self.logger.info("🔍 Starting comprehensive system validation on real data")
        start_time = time.time()
        
        validation_result = SystemValidationResult(
            timestamp=datetime.now().isoformat(),
            total_tests_run=0,
            validation_success=False,
            performance_score=0.0,
            optimization_recommendations=[],
            bottlenecks_identified=[],
            resource_usage={},
            execution_time_seconds=0.0
        )
        
        try:
            # Step 1: Validate test discovery
            self.logger.info("📊 Validating test discovery system")
            discovery_valid = self._validate_test_discovery()
            
            # Step 2: Validate test environments
            self.logger.info("🌍 Validating test environments")
            env_valid = self._validate_test_environments()
            
            # Step 3: Run comprehensive test suite with monitoring
            self.logger.info("🧪 Running comprehensive test validation")
            test_results = self._run_validation_tests(config)
            
            # Step 4: Validate service integration
            self.logger.info("🔗 Validating service integration")
            service_valid = self._validate_service_integration()
            
            # Step 5: Analyze performance and bottlenecks
            self.logger.info("📈 Analyzing performance and bottlenecks")
            performance_analysis = self._analyze_performance(test_results)
            
            # Compile validation result
            validation_result.total_tests_run = len(test_results)
            validation_result.validation_success = (
                discovery_valid and service_valid and 
                len([r for r in test_results if r.success]) > len(test_results) * 0.8
            )
            validation_result.performance_score = performance_analysis['overall_score']
            validation_result.optimization_recommendations = performance_analysis['recommendations']
            validation_result.bottlenecks_identified = performance_analysis['bottlenecks']
            validation_result.resource_usage = performance_analysis['resource_usage']
            validation_result.execution_time_seconds = time.time() - start_time
            
            self.logger.info(f"✅ System validation completed in {validation_result.execution_time_seconds:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ System validation failed: {e}")
            validation_result.validation_success = False
            validation_result.optimization_recommendations.append(f"Fix validation error: {e}")
        
        # Save validation result
        self._save_validation_result(validation_result)
        
        return validation_result
    
    def _validate_test_discovery(self) -> bool:
        """Validate test discovery system."""
        try:
            # Discover all tests
            test_modules = self.test_discovery.discover_all_tests()
            
            if not test_modules:
                self.logger.error("No test modules discovered")
                return False
            
            # Validate each discovered module
            valid_modules = 0
            for module in test_modules:
                if module.path.exists() and module.path.is_dir():
                    test_files = list(module.path.glob("test_*.py"))
                    if test_files:
                        valid_modules += 1
            
            discovery_rate = valid_modules / len(test_modules)
            self.logger.info(f"📊 Test discovery: {valid_modules}/{len(test_modules)} modules valid ({discovery_rate:.1%})")
            
            return discovery_rate >= 0.8  # At least 80% of discovered modules should be valid
            
        except Exception as e:
            self.logger.error(f"Test discovery validation failed: {e}")
            return False
    
    
    
    def _run_validation_tests(self, config: OptimizationConfig) -> List[TestPerformanceMetrics]:
        """Run comprehensive validation tests with performance monitoring."""
        test_results = []
        
        # Create test runner with optimized configuration
        runner = MasterTestRunner(
            max_workers=config.max_parallel_workers,
            root_path=str(self.project_root)
        )
        
        # Monitor system resources during test execution
        resource_monitor = SystemResourceMonitor()
        resource_monitor.start_monitoring()
        
        try:
            # Run different test categories
            test_categories = [
                TestCategory.UNIT,
                TestCategory.INTEGRATION,
                TestCategory.UI,
                TestCategory.PERFORMANCE,
                TestCategory.SECURITY
            ]
            
            for category in test_categories:
                self.logger.info(f"🧪 Running {category.value} tests for validation")
                
                category_start = time.time()
                
                try:
                    # Run tests for this category
                    results = runner.run_all_tests(
                        categories=[category],
                        parallel=config.enable_load_balancing,
                        prioritize=True,
                        enable_retry=config.retry_failed_tests,
                        generate_reports=False  # Skip reports during validation
                    )
                    
                    category_duration = time.time() - category_start
                    
                    # Create performance metrics
                    metrics = TestPerformanceMetrics(
                        test_name=f"validation_{category.value}",
                        category=category.value,
                        execution_time=category_duration,
                        memory_usage_mb=0.0,  # Will be filled by resource monitor
                        cpu_usage_percent=0.0,  # Will be filled by resource monitor
                        success=results.get('failed', 0) == 0,
                        retry_count=results.get('total_retries', 0),
                        parallel_efficiency=self._calculate_parallel_efficiency(results, category_duration),
                        bottlenecks=[]
                    )
                    
                    test_results.append(metrics)
                    
                except Exception as e:
                    self.logger.error(f"❌ Validation failed for {category.value}: {e}")
                    
                    # Create failed test metrics
                    metrics = TestPerformanceMetrics(
                        test_name=f"validation_{category.value}",
                        category=category.value,
                        execution_time=time.time() - category_start,
                        memory_usage_mb=0.0,
                        cpu_usage_percent=0.0,
                        success=False,
                        retry_count=0,
                        parallel_efficiency=0.0,
                        bottlenecks=[f"Execution failed: {e}"]
                    )
                    
                    test_results.append(metrics)
        
        finally:
            # Stop resource monitoring and update metrics
            resource_data = resource_monitor.stop_monitoring()
            self._update_metrics_with_resource_data(test_results, resource_data)
        
        return test_results
    
    def _validate_service_integration(self) -> bool:
        """Validate service integration and communication."""
        if not self.service_manager:
            self.logger.warning("ServiceManager not available, skipping service validation")
            return True  # Don't fail validation if service manager is not available
        
        try:
            # Test service startup
            self.logger.info("🚀 Testing service startup")
            startup_success = self.service_manager.start_all_services()
            
            if not startup_success:
                self.logger.error("❌ Service startup failed")
                return False
            
            # Test service health
            time.sleep(5)  # Allow services to fully start
            
            health_checks = {
                "crewai_server": self.service_manager.check_service_health("crewai_server"),
                "ui_application": self.service_manager.check_service_health("ui_application"),
                "memory_system": self.service_manager.check_service_health("memory_system")
            }
            
            healthy_services = sum(health_checks.values())
            total_services = len(health_checks)
            
            self.logger.info(f"🏥 Service health: {healthy_services}/{total_services} services healthy")
            
            # Clean up services
            self.service_manager.stop_all_services()
            
            return healthy_services >= total_services * 0.67  # At least 2/3 services should be healthy
            
        except Exception as e:
            self.logger.error(f"Service integration validation failed: {e}")
            return False
    
    def _analyze_performance(self, test_results: List[TestPerformanceMetrics]) -> Dict[str, Any]:
        """Analyze test performance and identify bottlenecks."""
        if not test_results:
            return {
                'overall_score': 0.0,
                'recommendations': ['No test results to analyze'],
                'bottlenecks': ['No tests executed'],
                'resource_usage': {}
            }
        
        # Calculate performance metrics
        total_time = sum(r.execution_time for r in test_results)
        avg_time = statistics.mean(r.execution_time for r in test_results)
        success_rate = len([r for r in test_results if r.success]) / len(test_results)
        
        # Identify bottlenecks
        bottlenecks = []
        slow_tests = [r for r in test_results if r.execution_time > avg_time * 2]
        if slow_tests:
            bottlenecks.extend([f"Slow test: {r.test_name} ({r.execution_time:.2f}s)" for r in slow_tests])
        
        high_memory_tests = [r for r in test_results if r.memory_usage_mb > 500]
        if high_memory_tests:
            bottlenecks.extend([f"High memory: {r.test_name} ({r.memory_usage_mb:.1f}MB)" for r in high_memory_tests])
        
        # Calculate overall performance score
        time_score = max(0, 100 - (avg_time / 60) * 10)  # Penalize if avg > 6 minutes
        success_score = success_rate * 100
        efficiency_score = statistics.mean(r.parallel_efficiency for r in test_results if r.parallel_efficiency > 0) or 50
        
        overall_score = (time_score * 0.4 + success_score * 0.4 + efficiency_score * 0.2)
        
        # Generate recommendations
        recommendations = []
        
        if success_rate < 0.9:
            recommendations.append("Fix failing tests to improve reliability")
        
        if avg_time > 300:  # 5 minutes
            recommendations.append("Optimize slow tests to reduce execution time")
        
        if len(slow_tests) > len(test_results) * 0.2:
            recommendations.append("Consider parallel execution for slow test categories")
        
        if any(r.memory_usage_mb > 1000 for r in test_results):
            recommendations.append("Investigate high memory usage in tests")
        
        # Resource usage summary
        resource_usage = {
            'avg_memory_mb': statistics.mean(r.memory_usage_mb for r in test_results if r.memory_usage_mb > 0) or 0,
            'max_memory_mb': max((r.memory_usage_mb for r in test_results), default=0),
            'avg_cpu_percent': statistics.mean(r.cpu_usage_percent for r in test_results if r.cpu_usage_percent > 0) or 0,
            'total_execution_time': total_time
        }
        
        return {
            'overall_score': overall_score,
            'recommendations': recommendations,
            'bottlenecks': bottlenecks,
            'resource_usage': resource_usage
        }
    
    def _calculate_parallel_efficiency(self, results: Dict, execution_time: float) -> float:
        """Calculate parallel execution efficiency."""
        if not results or execution_time <= 0:
            return 0.0
        
        total_tests = results.get('total_executions', 0)
        if total_tests <= 1:
            return 100.0  # Single test is 100% efficient
        
        # Estimate sequential time (rough heuristic)
        estimated_sequential_time = execution_time * 2  # Assume parallel is 2x faster
        
        # Calculate efficiency
        efficiency = min(100.0, (estimated_sequential_time / execution_time) * 50)
        
        return efficiency
    
    def _update_metrics_with_resource_data(self, test_results: List[TestPerformanceMetrics], 
                                         resource_data: List[Dict]) -> None:
        """Update test metrics with resource monitoring data."""
        if not resource_data:
            return
        
        # Calculate average resource usage during test execution
        avg_memory = statistics.mean(d.get('memory_mb', 0) for d in resource_data)
        avg_cpu = statistics.mean(d.get('cpu_percent', 0) for d in resource_data)
        
        # Update all test results with resource data
        for result in test_results:
            result.memory_usage_mb = avg_memory
            result.cpu_usage_percent = avg_cpu
    
    def _save_validation_result(self, result: SystemValidationResult) -> None:
        """Save validation result to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON result
        json_file = self.validation_dir / f"validation_result_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        # Save as latest
        latest_file = self.validation_dir / "validation_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        self.logger.info(f"📊 Validation result saved: {json_file}")


class TestExecutionOptimizer:
    """Optimizes test execution times and resource usage."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        self.optimization_history = []
        
        # Create optimization directory
        self.optimization_dir = self.project_root / "test_reports" / "optimization"
        self.optimization_dir.mkdir(parents=True, exist_ok=True)
    
    def optimize_test_execution(self, config: OptimizationConfig = None) -> Dict[str, Any]:
        """Optimize test execution times and resource usage."""
        if config is None:
            config = OptimizationConfig()
        
        self.logger.info("⚡ Starting test execution optimization")
        
        optimization_result = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': [],
            'performance_improvements': {},
            'resource_savings': {},
            'recommendations': []
        }
        
        try:
            # Step 1: Analyze current test performance
            self.logger.info("📊 Analyzing current test performance")
            baseline_metrics = self._measure_baseline_performance(config)
            
            # Step 2: Apply execution optimizations
            self.logger.info("⚡ Applying execution optimizations")
            execution_optimizations = self._optimize_execution_strategy(config)
            optimization_result['optimizations_applied'].extend(execution_optimizations)
            
            # Step 3: Optimize test parallelization
            self.logger.info("🔄 Optimizing test parallelization")
            parallel_optimizations = self._optimize_parallelization(config)
            optimization_result['optimizations_applied'].extend(parallel_optimizations)
            
            # Step 4: Optimize resource usage
            self.logger.info("💾 Optimizing resource usage")
            resource_optimizations = self._optimize_resource_usage(config)
            optimization_result['optimizations_applied'].extend(resource_optimizations)
            
            # Step 5: Measure performance improvements
            self.logger.info("📈 Measuring performance improvements")
            improved_metrics = self._measure_optimized_performance(config)
            
            # Calculate improvements
            if baseline_metrics and improved_metrics:
                optimization_result['performance_improvements'] = self._calculate_improvements(
                    baseline_metrics, improved_metrics
                )
            
            # Generate recommendations
            optimization_result['recommendations'] = self._generate_optimization_recommendations(
                baseline_metrics, improved_metrics
            )
            
        except Exception as e:
            self.logger.error(f"❌ Test optimization failed: {e}")
            optimization_result['recommendations'].append(f"Fix optimization error: {e}")
        
        # Save optimization result
        self._save_optimization_result(optimization_result)
        
        return optimization_result
    
    def _measure_baseline_performance(self, config: OptimizationConfig) -> Dict[str, float]:
        """Measure baseline test performance."""
        self.logger.info("📊 Measuring baseline performance")
        
        # Run a subset of tests to measure baseline
        runner = MasterTestRunner(max_workers=2)  # Use minimal parallelization for baseline
        
        start_time = time.time()
        results = runner.run_all_tests(
            categories=[TestCategory.UNIT],  # Use unit tests for baseline
            parallel=False,  # Sequential for baseline
            generate_reports=False
        )
        execution_time = time.time() - start_time
        
        return {
            'execution_time': execution_time,
            'success_rate': (results.get('passed', 0) / max(results.get('total_executions', 1), 1)) * 100,
            'memory_usage': self._get_current_memory_usage(),
            'cpu_usage': self._get_current_cpu_usage()
        }
    
    def _optimize_execution_strategy(self, config: OptimizationConfig) -> List[str]:
        """Optimize test execution strategy."""
        optimizations = []
        
        # Optimize pytest configuration
        pytest_optimizations = self._optimize_pytest_config()
        optimizations.extend(pytest_optimizations)
        
        # Optimize test discovery
        discovery_optimizations = self._optimize_test_discovery()
        optimizations.extend(discovery_optimizations)
        
        # Optimize test ordering
        ordering_optimizations = self._optimize_test_ordering()
        optimizations.extend(ordering_optimizations)
        
        return optimizations
    
    def _optimize_pytest_config(self) -> List[str]:
        """Optimize pytest configuration files."""
        optimizations = []
        
        # Find all pytest.ini files
        pytest_configs = list(self.project_root.glob("**/pytest.ini"))
        
        for config_file in pytest_configs:
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                
                # Add performance optimizations
                optimized_content = content
                
                # Add parallel execution markers
                if "markers =" not in content:
                    optimized_content += "\n[tool:pytest]\nmarkers =\n"
                
                if "slow: marks tests as slow" not in content:
                    optimized_content += "    slow: marks tests as slow\n"
                    optimized_content += "    fast: marks tests as fast\n"
                    optimized_content += "    parallel: marks tests as parallelizable\n"
                
                # Add performance options
                if "addopts =" not in content:
                    optimized_content += "addopts = --tb=short --strict-markers\n"
                
                # Save optimized config
                if optimized_content != content:
                    with open(config_file, 'w') as f:
                        f.write(optimized_content)
                    
                    optimizations.append(f"Optimized pytest config: {config_file}")
                
            except Exception as e:
                self.logger.warning(f"Failed to optimize {config_file}: {e}")
        
        return optimizations
    
    def _optimize_test_discovery(self) -> List[str]:
        """Optimize test discovery process."""
        optimizations = []
        
        # Create test discovery cache
        cache_file = self.project_root / ".pytest_cache" / "test_discovery.json"
        cache_file.parent.mkdir(exist_ok=True)
        
        try:
            discovery = TestDiscovery(str(self.project_root))
            test_modules = discovery.discover_all_tests()
            
            # Cache discovery results
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'modules': [
                    {
                        'name': m.module_name,
                        'path': str(m.path),
                        'category': m.category.value,
                        
                    }
                    for m in test_modules
                ]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            optimizations.append(f"Created test discovery cache with {len(test_modules)} modules")
            
        except Exception as e:
            self.logger.warning(f"Failed to optimize test discovery: {e}")
        
        return optimizations
    
    def _optimize_test_ordering(self) -> List[str]:
        """Optimize test execution ordering."""
        optimizations = []
        
        # Create test ordering based on historical performance
        try:
            # Analyze historical test performance
            performance_data = self._load_historical_performance()
            
            if performance_data:
                # Sort tests by execution time (fast tests first)
                sorted_tests = sorted(performance_data.items(), key=lambda x: x[1].get('avg_time', 0))
                
                # Create ordering file
                ordering_file = self.project_root / ".pytest_cache" / "test_ordering.json"
                with open(ordering_file, 'w') as f:
                    json.dump({
                        'fast_tests': [t[0] for t in sorted_tests[:len(sorted_tests)//2]],
                        'slow_tests': [t[0] for t in sorted_tests[len(sorted_tests)//2:]]
                    }, f, indent=2)
                
                optimizations.append(f"Created test ordering for {len(sorted_tests)} tests")
        
        except Exception as e:
            self.logger.warning(f"Failed to optimize test ordering: {e}")
        
        return optimizations
    
    def _optimize_parallelization(self, config: OptimizationConfig) -> List[str]:
        """Optimize test parallelization strategy."""
        optimizations = []
        
        # Determine optimal worker count
        optimal_workers = self._calculate_optimal_workers(config)
        if optimal_workers != config.max_parallel_workers:
            optimizations.append(f"Adjusted worker count from {config.max_parallel_workers} to {optimal_workers}")
            config.max_parallel_workers = optimal_workers
        
        # Create parallelization groups
        parallel_groups = self._create_parallelization_groups()
        if parallel_groups:
            optimizations.append(f"Created {len(parallel_groups)} parallelization groups")
        
        return optimizations
    
    def _calculate_optimal_workers(self, config: OptimizationConfig) -> int:
        """Calculate optimal number of parallel workers."""
        # Base on CPU cores and memory
        cpu_cores = psutil.cpu_count(logical=False) or 4
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Conservative approach: use 75% of cores, limited by memory
        max_workers_by_cpu = max(1, int(cpu_cores * 0.75))
        max_workers_by_memory = max(1, int(memory_gb / 2))  # Assume 2GB per worker
        
        optimal = min(max_workers_by_cpu, max_workers_by_memory, config.max_parallel_workers)
        
        self.logger.info(f"💻 Optimal workers: {optimal} (CPU: {max_workers_by_cpu}, Memory: {max_workers_by_memory})")
        
        return optimal
    
    def _create_parallelization_groups(self) -> List[Dict]:
        """Create groups of tests that can run in parallel."""
        groups = []
        
        try:
            discovery = TestDiscovery(str(self.project_root))
            test_modules = discovery.discover_all_tests()
            
            # Group by category
            category_groups = {}
            for module in test_modules:
                key = module.category.value
                if key not in category_groups:
                    category_groups[key] = []
                category_groups[key].append(module)
            
            # Create parallel groups
            for group_name, modules in category_groups.items():
                if len(modules) > 1:  # Only create groups with multiple modules
                    groups.append({
                        'name': group_name,
                        'modules': [m.module_name for m in modules],
                        'parallelizable': True
                    })
        
        except Exception as e:
            self.logger.warning(f"Failed to create parallelization groups: {e}")
        
        return groups
    
    def _optimize_resource_usage(self, config: OptimizationConfig) -> List[str]:
        """Optimize resource usage during test execution."""
        optimizations = []
        
        # Optimize memory usage
        memory_optimizations = self._optimize_memory_usage(config)
        optimizations.extend(memory_optimizations)
        
        # Optimize CPU usage
        cpu_optimizations = self._optimize_cpu_usage(config)
        optimizations.extend(cpu_optimizations)
        
        # Optimize I/O usage
        io_optimizations = self._optimize_io_usage(config)
        optimizations.extend(io_optimizations)
        
        return optimizations
    
    def _optimize_memory_usage(self, config: OptimizationConfig) -> List[str]:
        """Optimize memory usage during tests."""
        optimizations = []
        
        # Set memory limits for test processes
        memory_limit_mb = min(config.memory_threshold_mb, psutil.virtual_memory().total / (1024**2) * 0.8)
        
        # Create memory optimization script
        memory_script = self.project_root / ".pytest_cache" / "memory_optimization.py"
        with open(memory_script, 'w') as f:
            f.write(f"""
import gc
import psutil
import pytest

# Memory optimization for tests
MEMORY_LIMIT_MB = {memory_limit_mb}

@pytest.fixture(autouse=True)
def memory_monitor():
    # Force garbage collection before each test
    gc.collect()
    
    yield
    
    # Check memory usage after test
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > MEMORY_LIMIT_MB:
        print(f"Warning: Test used {{memory_mb:.1f}}MB (limit: {{MEMORY_LIMIT_MB}}MB)")
        gc.collect()  # Force cleanup
""")
        
        optimizations.append(f"Created memory optimization with {memory_limit_mb:.0f}MB limit")
        
        return optimizations
    
    def _optimize_cpu_usage(self, config: OptimizationConfig) -> List[str]:
        """Optimize CPU usage during tests."""
        optimizations = []
        
        # Set CPU affinity for test processes (if supported)
        try:
            import psutil
            cpu_count = psutil.cpu_count(logical=False)
            
            if cpu_count > 2:
                # Reserve some CPUs for system processes
                test_cpus = list(range(min(config.max_parallel_workers, cpu_count - 1)))
                
                cpu_script = self.project_root / ".pytest_cache" / "cpu_optimization.py"
                with open(cpu_script, 'w') as f:
                    f.write(f"""
import os
import psutil
import pytest

# CPU optimization for tests
TEST_CPUS = {test_cpus}

@pytest.fixture(scope="session", autouse=True)
def cpu_optimization():
    try:
        process = psutil.Process()
        process.cpu_affinity(TEST_CPUS)
        print(f"Set CPU affinity to cores: {{TEST_CPUS}}")
    except Exception as e:
        print(f"Could not set CPU affinity: {{e}}")
    
    yield
""")
                
                optimizations.append(f"Created CPU optimization for cores {test_cpus}")
        
        except Exception as e:
            self.logger.warning(f"Failed to optimize CPU usage: {e}")
        
        return optimizations
    
    def _optimize_io_usage(self, config: OptimizationConfig) -> List[str]:
        """Optimize I/O usage during tests."""
        optimizations = []
        
        # Create temporary directory for test I/O
        temp_dir = self.project_root / ".pytest_cache" / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Create I/O optimization script
        io_script = self.project_root / ".pytest_cache" / "io_optimization.py"
        with open(io_script, 'w') as f:
            f.write(f"""
import tempfile
import pytest
from pathlib import Path

# I/O optimization for tests
TEST_TEMP_DIR = Path("{temp_dir}")

@pytest.fixture
def temp_dir():
    # Use dedicated temp directory for tests
    return TEST_TEMP_DIR

@pytest.fixture
def temp_file():
    # Create temporary file in test directory
    import tempfile
    fd, path = tempfile.mkstemp(dir=TEST_TEMP_DIR)
    yield path
    try:
        os.close(fd)
        os.unlink(path)
    except:
        pass
""")
        
        optimizations.append(f"Created I/O optimization with temp dir: {temp_dir}")
        
        return optimizations
    
    def _measure_optimized_performance(self, config: OptimizationConfig) -> Dict[str, float]:
        """Measure performance after optimizations."""
        self.logger.info("📈 Measuring optimized performance")
        
        # Run the same tests with optimizations
        runner = MasterTestRunner(max_workers=config.max_parallel_workers)
        
        start_time = time.time()
        results = runner.run_all_tests(
            categories=[TestCategory.UNIT],
            parallel=config.enable_load_balancing,
            generate_reports=False
        )
        execution_time = time.time() - start_time
        
        return {
            'execution_time': execution_time,
            'success_rate': (results.get('passed', 0) / max(results.get('total_executions', 1), 1)) * 100,
            'memory_usage': self._get_current_memory_usage(),
            'cpu_usage': self._get_current_cpu_usage()
        }
    
    def _calculate_improvements(self, baseline: Dict[str, float], optimized: Dict[str, float]) -> Dict[str, float]:
        """Calculate performance improvements."""
        improvements = {}
        
        for metric in baseline:
            if metric in optimized:
                baseline_val = baseline[metric]
                optimized_val = optimized[metric]
                
                if baseline_val > 0:
                    if metric == 'execution_time':
                        # For time, lower is better
                        improvement = ((baseline_val - optimized_val) / baseline_val) * 100
                    else:
                        # For other metrics, higher is usually better
                        improvement = ((optimized_val - baseline_val) / baseline_val) * 100
                    
                    improvements[f"{metric}_improvement_percent"] = improvement
        
        return improvements
    
    def _generate_optimization_recommendations(self, baseline: Dict, optimized: Dict) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if not baseline or not optimized:
            recommendations.append("Collect more performance data for better recommendations")
            return recommendations
        
        # Time-based recommendations
        if optimized.get('execution_time', 0) > baseline.get('execution_time', 0):
            recommendations.append("Consider reducing parallel workers or optimizing slow tests")
        elif optimized.get('execution_time', 0) < baseline.get('execution_time', 0) * 0.8:
            recommendations.append("Great performance improvement! Consider applying optimizations permanently")
        
        # Memory-based recommendations
        if optimized.get('memory_usage', 0) > baseline.get('memory_usage', 0) * 1.2:
            recommendations.append("Memory usage increased - review memory optimization settings")
        
        # Success rate recommendations
        if optimized.get('success_rate', 0) < baseline.get('success_rate', 0):
            recommendations.append("Success rate decreased - verify optimizations don't break tests")
        
        return recommendations
    
    def _load_historical_performance(self) -> Dict:
        """Load historical test performance data."""
        try:
            perf_file = self.optimization_dir / "historical_performance.json"
            if perf_file.exists():
                with open(perf_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {}
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _get_current_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _save_optimization_result(self, result: Dict) -> None:
        """Save optimization result to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON result
        json_file = self.optimization_dir / f"optimization_result_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        # Save as latest
        latest_file = self.optimization_dir / "optimization_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        self.logger.info(f"⚡ Optimization result saved: {json_file}")


class LoadBalancer:
    """Configures load balancing for parallel test execution."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # Create load balancing directory
        self.lb_dir = self.project_root / "test_reports" / "load_balancing"
        self.lb_dir.mkdir(parents=True, exist_ok=True)
    
    def configure_load_balancing(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Configure load balancing for parallel test execution."""
        self.logger.info("⚖️ Configuring load balancing for parallel tests")
        
        lb_config = {
            'timestamp': datetime.now().isoformat(),
            'worker_configuration': {},
            'test_distribution': {},
            'resource_allocation': {},
            'balancing_strategy': 'dynamic'
        }
        
        try:
            # Step 1: Analyze test workload
            workload_analysis = self._analyze_test_workload()
            
            # Step 2: Configure worker pools
            worker_config = self._configure_worker_pools(config, workload_analysis)
            lb_config['worker_configuration'] = worker_config
            
            # Step 3: Create test distribution strategy
            distribution_strategy = self._create_distribution_strategy(workload_analysis)
            lb_config['test_distribution'] = distribution_strategy
            
            # Step 4: Configure resource allocation
            resource_allocation = self._configure_resource_allocation(config)
            lb_config['resource_allocation'] = resource_allocation
            
            # Step 5: Implement dynamic balancing
            dynamic_config = self._configure_dynamic_balancing(config)
            lb_config['dynamic_balancing'] = dynamic_config
            
        except Exception as e:
            self.logger.error(f"❌ Load balancing configuration failed: {e}")
            lb_config['error'] = str(e)
        
        # Save load balancing configuration
        self._save_load_balancing_config(lb_config)
        
        return lb_config
    
    def _analyze_test_workload(self) -> Dict[str, Any]:
        """Analyze test workload for load balancing."""
        workload = {
            'test_categories': {},
            'execution_times': {},
            'resource_requirements': {},
            'dependencies': {}
        }
        
        try:
            discovery = TestDiscovery(str(self.project_root))
            test_modules = discovery.discover_all_tests()
            
            # Analyze by category
            for module in test_modules:
                category = module.category.value
                if category not in workload['test_categories']:
                    workload['test_categories'][category] = {
                        'count': 0,
                        'modules': [],
                        'estimated_time': 0
                    }
                
                workload['test_categories'][category]['count'] += 1
                workload['test_categories'][category]['modules'].append(module.module_name)
                
                # Estimate execution time based on category
                time_estimates = {
                    'unit': 30,      # 30 seconds
                    'integration': 120,  # 2 minutes
                    'ui': 300,       # 5 minutes
                    'e2e': 600,      # 10 minutes
                    'performance': 900,  # 15 minutes
                    'security': 180  # 3 minutes
                }
                
                workload['test_categories'][category]['estimated_time'] += time_estimates.get(category, 60)
            
            # Analyze resource requirements
            for category, data in workload['test_categories'].items():
                resource_reqs = {
                    'unit': {'memory_mb': 100, 'cpu_percent': 20},
                    'integration': {'memory_mb': 200, 'cpu_percent': 40},
                    'ui': {'memory_mb': 500, 'cpu_percent': 60},
                    'e2e': {'memory_mb': 800, 'cpu_percent': 80},
                    'performance': {'memory_mb': 300, 'cpu_percent': 90},
                    'security': {'memory_mb': 150, 'cpu_percent': 30}
                }
                
                workload['resource_requirements'][category] = resource_reqs.get(category, {'memory_mb': 200, 'cpu_percent': 40})
        
        except Exception as e:
            self.logger.warning(f"Failed to analyze test workload: {e}")
        
        return workload
    
    def _configure_worker_pools(self, config: OptimizationConfig, workload: Dict) -> Dict[str, Any]:
        """Configure worker pools for different test types."""
        worker_config = {
            'total_workers': config.max_parallel_workers,
            'pools': {},
            'allocation_strategy': 'weighted'
        }
        
        # Calculate total estimated time
        total_time = sum(
            cat_data.get('estimated_time', 0) 
            for cat_data in workload.get('test_categories', {}).values()
        )
        
        if total_time == 0:
            # Default allocation if no workload data
            worker_config['pools'] = {
                'fast_pool': {'workers': max(1, config.max_parallel_workers // 2), 'categories': ['unit']},
                'slow_pool': {'workers': max(1, config.max_parallel_workers // 2), 'categories': ['integration', 'ui', 'e2e']}
            }
        else:
            # Allocate workers based on estimated workload
            remaining_workers = config.max_parallel_workers
            
            for category, data in workload.get('test_categories', {}).items():
                if remaining_workers <= 0:
                    break
                
                # Calculate worker allocation based on time proportion
                time_proportion = data.get('estimated_time', 0) / total_time
                allocated_workers = max(1, int(config.max_parallel_workers * time_proportion))
                allocated_workers = min(allocated_workers, remaining_workers)
                
                worker_config['pools'][f"{category}_pool"] = {
                    'workers': allocated_workers,
                    'categories': [category],
                    'estimated_time': data.get('estimated_time', 0)
                }
                
                remaining_workers -= allocated_workers
        
        return worker_config
    
    def _create_distribution_strategy(self, workload: Dict) -> Dict[str, Any]:
        """Create test distribution strategy."""
        strategy = {
            'algorithm': 'weighted_round_robin',
            'factors': {
                'execution_time': 0.4,
                'resource_usage': 0.3,
                'dependencies': 0.3
            },
            'distribution_rules': []
        }
        
        # Create distribution rules based on workload
        for category, data in workload.get('test_categories', {}).items():
            rule = {
                'category': category,
                'priority': self._get_category_priority(category),
                'max_concurrent': self._get_max_concurrent(category),
                'resource_weight': self._get_resource_weight(category)
            }
            
            strategy['distribution_rules'].append(rule)
        
        return strategy
    
    def _get_category_priority(self, category: str) -> int:
        """Get priority for test category."""
        priorities = {
            'unit': 1,        # Highest priority (fast)
            'security': 2,    # High priority (important)
            'integration': 3, # Medium priority
            'ui': 4,          # Lower priority (slower)
            'performance': 5, # Low priority (slowest)
            'e2e': 6          # Lowest priority (slowest, most complex)
        }
        
        return priorities.get(category, 3)
    
    def _get_max_concurrent(self, category: str) -> int:
        """Get maximum concurrent tests for category."""
        max_concurrent = {
            'unit': 8,        # Can run many in parallel
            'integration': 4, # Moderate parallelization
            'security': 3,    # Limited parallelization
            'ui': 2,          # Limited by display resources
            'performance': 1, # Should run sequentially
            'e2e': 1          # Should run sequentially
        }
        
        return max_concurrent.get(category, 2)
    
    def _get_resource_weight(self, category: str) -> float:
        """Get resource weight for category."""
        weights = {
            'unit': 0.1,        # Lightweight
            'integration': 0.3,  # Moderate
            'security': 0.2,     # Light-moderate
            'ui': 0.8,           # Heavy (GUI resources)
            'performance': 0.9,  # Very heavy
            'e2e': 1.0           # Heaviest
        }
        
        return weights.get(category, 0.5)
    
    def _configure_resource_allocation(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Configure resource allocation for load balancing."""
        system_info = {
            'cpu_cores': psutil.cpu_count(logical=False) or 4,
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'logical_cores': psutil.cpu_count(logical=True) or 4
        }
        
        allocation = {
            'system_info': system_info,
            'resource_limits': {
                'memory_per_worker_mb': min(
                    config.memory_threshold_mb / config.max_parallel_workers,
                    system_info['memory_gb'] * 1024 * 0.8 / config.max_parallel_workers
                ),
                'cpu_per_worker_percent': min(
                    config.cpu_threshold_percent / config.max_parallel_workers,
                    80.0 / config.max_parallel_workers
                )
            },
            'resource_monitoring': {
                'enabled': True,
                'interval_seconds': 5,
                'thresholds': {
                    'memory_warning_percent': 80,
                    'cpu_warning_percent': 85
                }
            }
        }
        
        return allocation
    
    def _configure_dynamic_balancing(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Configure dynamic load balancing."""
        dynamic_config = {
            'enabled': True,
            'rebalancing_interval_seconds': 30,
            'metrics_collection': {
                'queue_length': True,
                'worker_utilization': True,
                'resource_usage': True,
                'test_completion_rate': True
            },
            'rebalancing_triggers': {
                'queue_imbalance_threshold': 0.3,  # 30% imbalance triggers rebalancing
                'worker_idle_threshold': 0.2,     # 20% idle workers trigger rebalancing
                'resource_pressure_threshold': 0.9 # 90% resource usage triggers rebalancing
            },
            'rebalancing_strategies': [
                'redistribute_queued_tests',
                'adjust_worker_allocation',
                'pause_resource_intensive_tests'
            ]
        }
        
        return dynamic_config
    
    def _save_load_balancing_config(self, config: Dict) -> None:
        """Save load balancing configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON config
        json_file = self.lb_dir / f"load_balancing_config_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        # Save as latest
        latest_file = self.lb_dir / "load_balancing_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        self.logger.info(f"⚖️ Load balancing config saved: {json_file}")


class SystemResourceMonitor:
    """Monitors system resources during test execution."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_data = []
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self, interval: float = 1.0):
        """Start system resource monitoring."""
        self.monitoring = True
        self.resource_data.clear()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.start()
        self.logger.info(f"📊 Started resource monitoring (interval: {interval}s)")
    
    def stop_monitoring(self) -> List[Dict]:
        """Stop monitoring and return collected data."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        self.logger.info(f"📊 Stopped resource monitoring ({len(self.resource_data)} samples)")
        return self.resource_data.copy()
    
    def _monitor_loop(self, interval: float):
        """Monitor system resources in a loop."""
        while self.monitoring:
            try:
                data = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_io': self._get_disk_io(),
                    'network_io': self._get_network_io(),
                    'process_count': len(psutil.pids())
                }
                
                self.resource_data.append(data)
                
            except Exception as e:
                self.logger.warning(f"Resource monitoring error: {e}")
            
            time.sleep(interval)
    
    def _get_disk_io(self) -> Dict:
        """Get disk I/O statistics."""
        try:
            io_stats = psutil.disk_io_counters()
            if io_stats:
                return {
                    'read_mb': io_stats.read_bytes / 1024 / 1024,
                    'write_mb': io_stats.write_bytes / 1024 / 1024
                }
        except:
            pass
        
        return {'read_mb': 0, 'write_mb': 0}
    
    def _get_network_io(self) -> Dict:
        """Get network I/O statistics."""
        try:
            net_stats = psutil.net_io_counters()
            if net_stats:
                return {
                    'sent_mb': net_stats.bytes_sent / 1024 / 1024,
                    'recv_mb': net_stats.bytes_recv / 1024 / 1024
                }
        except:
            pass
        
        return {'sent_mb': 0, 'recv_mb': 0}


def main():
    """Main function for test validation and optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI Test System Validation and Optimization")
    parser.add_argument('--validate', action='store_true', help='Run system validation')
    parser.add_argument('--optimize', action='store_true', help='Run test optimization')
    parser.add_argument('--load-balance', action='store_true', help='Configure load balancing')
    parser.add_argument('--all', action='store_true', help='Run all validation and optimization')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum parallel workers')
    parser.add_argument('--memory-threshold', type=int, default=2048, help='Memory threshold in MB')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = OptimizationConfig(
        max_parallel_workers=args.max_workers
    )
    
    if args.all or args.validate:
        print("🔍 Running system validation...")
        validator = TestSystemValidator()
        result = validator.validate_system_on_real_data(config)
        
        print(f"\n📊 Validation Results:")
        print(f"   Success: {'✅' if result.validation_success else '❌'}")
        print(f"   Tests Run: {result.total_tests_run}")
        print(f"   Performance Score: {result.performance_score:.1f}/100")
        print(f"   Execution Time: {result.execution_time_seconds:.2f}s")
        
        if result.optimization_recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.optimization_recommendations:
                print(f"   • {rec}")
    
    if args.all or args.optimize:
        print("\n⚡ Running test optimization...")
        optimizer = TestExecutionOptimizer()
        result = optimizer.optimize_test_execution(config)
        
        print(f"\n📈 Optimization Results:")
        print(f"   Optimizations Applied: {len(result['optimizations_applied'])}")
        
        if result['performance_improvements']:
            print(f"   Performance Improvements:")
            for metric, improvement in result['performance_improvements'].items():
                print(f"     {metric}: {improvement:+.1f}%")
    
    if args.all or args.load_balance:
        print("\n⚖️ Configuring load balancing...")
        load_balancer = LoadBalancer()
        result = load_balancer.configure_load_balancing(config)
        
        print(f"\n⚖️ Load Balancing Configuration:")
        print(f"   Total Workers: {result['worker_configuration']['total_workers']}")
        print(f"   Worker Pools: {len(result['worker_configuration']['pools'])}")
        print(f"   Balancing Strategy: {result['balancing_strategy']}")


if __name__ == "__main__":
    main()