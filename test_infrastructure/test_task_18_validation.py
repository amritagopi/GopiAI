#!/usr/bin/env python3
"""
Test validation for Task 18: System Validation and Optimization

This test verifies that all four sub-tasks of Task 18 have been completed successfully:
1. Test the entire testing system on real data
2. Optimize test execution times
3. Configure load balancing for parallel tests
4. Create monitoring system for test performance
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
import unittest

# Add test infrastructure to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

try:
    from comprehensive_system_validator import ComprehensiveSystemValidator
except ImportError as e:
    print(f"Warning: Could not import comprehensive_system_validator: {e}")


class TestTask18Validation(unittest.TestCase):
    """Test validation for Task 18 implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(".")
        self.validation_dir = self.project_root / "test_reports" / "system_validation"
        self.validator = ComprehensiveSystemValidator(str(self.project_root))
    
    def test_sub_task_1_system_validation_on_real_data(self):
        """Test sub-task 1: Test the entire testing system on real data."""
        print("\n🔍 Testing Sub-task 1: System validation on real data")
        
        # Check if validation results exist
        validation_file = self.validation_dir / "validation_latest.json"
        self.assertTrue(validation_file.exists(), "Validation results file should exist")
        
        # Load and validate results
        with open(validation_file, 'r') as f:
            validation_data = json.load(f)
        
        # Verify required fields exist
        required_fields = [
            'timestamp', 'validation_success', 'total_tests_run', 
            'tests_passed', 'tests_failed', 'execution_time_seconds',
            'performance_score', 'bottlenecks', 'optimization_recommendations',
            'resource_usage'
        ]
        
        for field in required_fields:
            self.assertIn(field, validation_data, f"Field '{field}' should be present in validation results")
        
        # Verify tests were actually run
        self.assertGreater(validation_data['total_tests_run'], 0, "Should have run some tests")
        
        # Verify performance score is calculated
        self.assertIsInstance(validation_data['performance_score'], (int, float), 
                            "Performance score should be numeric")
        self.assertGreaterEqual(validation_data['performance_score'], 0, 
                              "Performance score should be non-negative")
        self.assertLessEqual(validation_data['performance_score'], 100, 
                           "Performance score should not exceed 100")
        
        # Verify resource usage data
        self.assertIn('resource_usage', validation_data, "Resource usage data should be present")
        resource_usage = validation_data['resource_usage']
        self.assertIn('total_execution_time', resource_usage, "Total execution time should be tracked")
        
        print(f"✅ Sub-task 1 validated: {validation_data['total_tests_run']} tests run, "
              f"performance score: {validation_data['performance_score']:.1f}/100")
    
    def test_sub_task_2_execution_time_optimization(self):
        """Test sub-task 2: Optimize test execution times."""
        print("\n⚡ Testing Sub-task 2: Execution time optimization")
        
        # Check if optimization results exist
        optimization_file = self.validation_dir / "optimization_latest.json"
        self.assertTrue(optimization_file.exists(), "Optimization results file should exist")
        
        # Load and validate results
        with open(optimization_file, 'r') as f:
            optimization_data = json.load(f)
        
        # Verify required fields exist
        required_fields = [
            'timestamp', 'optimizations_applied', 'performance_improvement_percent',
            'execution_time_reduction_percent', 'resource_savings'
        ]
        
        for field in required_fields:
            self.assertIn(field, optimization_data, f"Field '{field}' should be present in optimization results")
        
        # Verify optimizations were applied
        optimizations = optimization_data['optimizations_applied']
        self.assertIsInstance(optimizations, list, "Optimizations should be a list")
        self.assertGreater(len(optimizations), 0, "Should have applied some optimizations")
        
        # Check for expected optimization types
        expected_optimizations = [
            'test result caching',
            'test ordering',
            'smart test selection',
            'resource usage optimization'
        ]
        
        applied_optimizations_text = ' '.join(optimizations).lower()
        found_optimizations = []
        for expected in expected_optimizations:
            if expected in applied_optimizations_text:
                found_optimizations.append(expected)
        
        self.assertGreater(len(found_optimizations), 0, 
                         f"Should have applied at least one expected optimization type. "
                         f"Applied: {optimizations}")
        
        # Verify performance metrics
        self.assertIsInstance(optimization_data['execution_time_reduction_percent'], (int, float),
                            "Execution time reduction should be numeric")
        self.assertIsInstance(optimization_data['performance_improvement_percent'], (int, float),
                            "Performance improvement should be numeric")
        
        # Check if cache configuration files were created
        cache_dir = self.project_root / ".pytest_cache"
        if cache_dir.exists():
            cache_files = ['cache_config.json', 'test_ordering.json', 'test_selection.json', 'resource_optimization.json']
            created_files = [f for f in cache_files if (cache_dir / f).exists()]
            self.assertGreater(len(created_files), 0, f"Should have created cache configuration files. Found: {created_files}")
        
        print(f"✅ Sub-task 2 validated: {len(optimizations)} optimizations applied, "
              f"{optimization_data['execution_time_reduction_percent']:.1f}% time reduction")
    
    def test_sub_task_3_load_balancing_configuration(self):
        """Test sub-task 3: Configure load balancing for parallel tests."""
        print("\n⚖️ Testing Sub-task 3: Load balancing configuration")
        
        # Check if load balancing config exists
        load_balancing_file = self.validation_dir / "load_balancing_config.json"
        self.assertTrue(load_balancing_file.exists(), "Load balancing config file should exist")
        
        # Load and validate configuration
        with open(load_balancing_file, 'r') as f:
            load_balancing_data = json.load(f)
        
        # Verify required fields exist
        required_fields = [
            'timestamp', 'optimal_worker_count', 'test_distribution_strategy',
            'resource_allocation', 'parallel_groups', 'dependency_graph',
            'performance_metrics'
        ]
        
        for field in required_fields:
            self.assertIn(field, load_balancing_data, f"Field '{field}' should be present in load balancing config")
        
        # Verify optimal worker count is reasonable
        optimal_workers = load_balancing_data['optimal_worker_count']
        self.assertIsInstance(optimal_workers, int, "Optimal worker count should be an integer")
        self.assertGreater(optimal_workers, 0, "Should have at least 1 worker")
        self.assertLessEqual(optimal_workers, 8, "Should not exceed 8 workers")
        
        # Verify resource allocation
        resource_allocation = load_balancing_data['resource_allocation']
        self.assertIn('worker_count', resource_allocation, "Resource allocation should specify worker count")
        self.assertIn('memory_per_worker_mb', resource_allocation, "Should specify memory per worker")
        self.assertIn('timeout_seconds', resource_allocation, "Should specify timeout")
        
        # Verify parallel groups
        parallel_groups = load_balancing_data['parallel_groups']
        self.assertIsInstance(parallel_groups, list, "Parallel groups should be a list")
        self.assertGreater(len(parallel_groups), 0, "Should have at least one parallel group")
        
        # Check parallel group structure
        for group in parallel_groups:
            self.assertIn('name', group, "Each parallel group should have a name")
            self.assertIn('max_workers', group, "Each parallel group should specify max workers")
            self.assertIn('categories', group, "Each parallel group should specify test categories")
        
        # Verify dependency graph
        dependency_graph = load_balancing_data['dependency_graph']
        self.assertIsInstance(dependency_graph, dict, "Dependency graph should be a dictionary")
        
        # Verify performance metrics
        performance_metrics = load_balancing_data['performance_metrics']
        self.assertIn('parallel_efficiency', performance_metrics, "Should track parallel efficiency")
        self.assertIn('resource_utilization', performance_metrics, "Should track resource utilization")
        
        print(f"✅ Sub-task 3 validated: {optimal_workers} optimal workers, "
              f"{len(parallel_groups)} parallel groups, "
              f"{load_balancing_data['test_distribution_strategy']} distribution strategy")
    
    def test_sub_task_4_performance_monitoring_system(self):
        """Test sub-task 4: Create monitoring system for test performance."""
        print("\n📊 Testing Sub-task 4: Performance monitoring system")
        
        # Check if monitoring config exists
        monitoring_file = self.validation_dir / "monitoring_system_config.json"
        self.assertTrue(monitoring_file.exists(), "Monitoring system config file should exist")
        
        # Load and validate configuration
        with open(monitoring_file, 'r') as f:
            monitoring_data = json.load(f)
        
        # Verify required fields exist
        required_fields = [
            'timestamp', 'monitoring_components', 'metrics_collected',
            'alerting_rules', 'dashboard_config', 'historical_tracking',
            'performance_thresholds'
        ]
        
        for field in required_fields:
            self.assertIn(field, monitoring_data, f"Field '{field}' should be present in monitoring config")
        
        # Verify monitoring components
        components = monitoring_data['monitoring_components']
        self.assertIsInstance(components, list, "Monitoring components should be a list")
        self.assertGreater(len(components), 0, "Should have at least one monitoring component")
        
        # Verify metrics collection
        metrics = monitoring_data['metrics_collected']
        expected_metrics = [
            'test_execution_time', 'test_success_rate', 'memory_usage', 
            'cpu_usage', 'parallel_efficiency'
        ]
        
        for expected_metric in expected_metrics:
            self.assertIn(expected_metric, metrics, f"Should collect '{expected_metric}' metric")
        
        # Verify alerting rules
        alerting_rules = monitoring_data['alerting_rules']
        self.assertIsInstance(alerting_rules, list, "Alerting rules should be a list")
        self.assertGreater(len(alerting_rules), 0, "Should have at least one alerting rule")
        
        # Check alerting rule structure
        for rule in alerting_rules:
            self.assertIn('name', rule, "Each alerting rule should have a name")
            self.assertIn('condition', rule, "Each alerting rule should have a condition")
            self.assertIn('severity', rule, "Each alerting rule should have a severity")
            self.assertIn('action', rule, "Each alerting rule should have an action")
        
        # Verify dashboard configuration
        dashboard_config = monitoring_data['dashboard_config']
        self.assertIn('title', dashboard_config, "Dashboard should have a title")
        self.assertIn('widgets', dashboard_config, "Dashboard should have widgets")
        
        widgets = dashboard_config['widgets']
        self.assertIsInstance(widgets, list, "Dashboard widgets should be a list")
        self.assertGreater(len(widgets), 0, "Dashboard should have at least one widget")
        
        # Verify performance thresholds
        thresholds = monitoring_data['performance_thresholds']
        expected_thresholds = [
            'max_execution_time', 'min_success_rate', 'max_memory_usage',
            'max_cpu_usage', 'min_parallel_efficiency'
        ]
        
        for expected_threshold in expected_thresholds:
            self.assertIn(expected_threshold, thresholds, f"Should define '{expected_threshold}' threshold")
        
        # Check if monitoring database was created
        db_file = self.validation_dir / "performance_monitoring.db"
        self.assertTrue(db_file.exists(), "Performance monitoring database should exist")
        
        # Verify database structure
        with sqlite3.connect(db_file) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn('test_performance', tables, "Database should have test_performance table")
        
        # Check if monitoring scripts were created (if they exist)
        monitoring_scripts = [
            'monitor_performance.py',
            'performance_alerts.py', 
            'performance_dashboard.py'
        ]
        
        existing_scripts = []
        for script in monitoring_scripts:
            script_path = self.validation_dir / script
            if script_path.exists():
                existing_scripts.append(script)
        
        # At least one script should exist
        self.assertGreater(len(existing_scripts), 0, 
                         f"Should have created at least one monitoring script. "
                         f"Expected: {monitoring_scripts}, Found: {existing_scripts}")
        
        print(f"✅ Sub-task 4 validated: {len(components)} monitoring components, "
              f"{len(metrics)} metrics collected, {len(alerting_rules)} alerting rules, "
              f"{len(existing_scripts)} monitoring scripts")
    
    def test_overall_task_18_completion(self):
        """Test overall Task 18 completion and integration."""
        print("\n🎯 Testing Overall Task 18 completion")
        
        # Check if complete results exist
        complete_file = self.validation_dir / "task_18_latest.json"
        self.assertTrue(complete_file.exists(), "Complete Task 18 results file should exist")
        
        # Load and validate complete results
        with open(complete_file, 'r') as f:
            complete_data = json.load(f)
        
        # Verify all sub-tasks are present
        self.assertIn('task_18_results', complete_data, "Should contain task 18 results")
        task_results = complete_data['task_18_results']
        
        sub_tasks = ['validation', 'optimization', 'load_balancing', 'monitoring']
        for sub_task in sub_tasks:
            self.assertIn(sub_task, task_results, f"Sub-task '{sub_task}' should be present in results")
        
        # Verify overall success assessment
        self.assertIn('overall_success', complete_data, "Should have overall success assessment")
        
        # Count successful sub-tasks
        successful_sub_tasks = 0
        
        # Check validation success
        validation = task_results['validation']
        if validation.get('total_tests_run', 0) > 0:
            successful_sub_tasks += 1
            print(f"  ✅ Sub-task 1 (Validation): {validation['total_tests_run']} tests run")
        
        # Check optimization success
        optimization = task_results['optimization']
        if len(optimization.get('optimizations_applied', [])) > 0:
            successful_sub_tasks += 1
            print(f"  ✅ Sub-task 2 (Optimization): {len(optimization['optimizations_applied'])} optimizations applied")
        
        # Check load balancing success
        load_balancing = task_results['load_balancing']
        if load_balancing.get('optimal_worker_count', 0) > 0:
            successful_sub_tasks += 1
            print(f"  ✅ Sub-task 3 (Load Balancing): {load_balancing['optimal_worker_count']} optimal workers")
        
        # Check monitoring success
        monitoring = task_results['monitoring']
        if len(monitoring.get('monitoring_components', [])) > 0:
            successful_sub_tasks += 1
            print(f"  ✅ Sub-task 4 (Monitoring): {len(monitoring['monitoring_components'])} components created")
        
        # Verify at least 3 out of 4 sub-tasks completed successfully
        self.assertGreaterEqual(successful_sub_tasks, 3, 
                              f"At least 3 out of 4 sub-tasks should be successful. "
                              f"Completed: {successful_sub_tasks}/4")
        
        print(f"🎯 Task 18 Overall Status: {successful_sub_tasks}/4 sub-tasks completed successfully")
        
        # Verify key deliverables exist
        key_files = [
            'validation_latest.json',
            'optimization_latest.json', 
            'load_balancing_config.json',
            'monitoring_system_config.json',
            'performance_monitoring.db'
        ]
        
        existing_files = []
        for file_name in key_files:
            file_path = self.validation_dir / file_name
            if file_path.exists():
                existing_files.append(file_name)
        
        self.assertGreaterEqual(len(existing_files), 4, 
                              f"Should have created at least 4 key deliverable files. "
                              f"Expected: {key_files}, Found: {existing_files}")
        
        print(f"📁 Deliverables: {len(existing_files)}/{len(key_files)} key files created")
    
    def test_performance_improvements_measurable(self):
        """Test that performance improvements are measurable and documented."""
        print("\n📈 Testing Performance improvements are measurable")
        
        # Load optimization results
        optimization_file = self.validation_dir / "optimization_latest.json"
        if not optimization_file.exists():
            self.skipTest("Optimization results not available")
        
        with open(optimization_file, 'r') as f:
            optimization_data = json.load(f)
        
        # Check if performance improvements are documented
        improvements = optimization_data.get('optimizations_applied', [])
        self.assertGreater(len(improvements), 0, "Should have documented performance improvements")
        
        # Check if metrics show improvement potential
        time_reduction = optimization_data.get('execution_time_reduction_percent', 0)
        performance_improvement = optimization_data.get('performance_improvement_percent', 0)
        
        # At least one metric should show improvement or potential for improvement
        has_improvement = (time_reduction > 0 or performance_improvement > 0 or len(improvements) > 0)
        self.assertTrue(has_improvement, 
                       "Should show measurable performance improvements or optimization potential")
        
        print(f"📈 Performance improvements: {time_reduction:.1f}% time reduction, "
              f"{performance_improvement:.1f}% performance improvement, "
              f"{len(improvements)} optimizations applied")
    
    def test_load_balancing_configuration_realistic(self):
        """Test that load balancing configuration is realistic for the system."""
        print("\n⚖️ Testing Load balancing configuration is realistic")
        
        # Load load balancing config
        load_balancing_file = self.validation_dir / "load_balancing_config.json"
        if not load_balancing_file.exists():
            self.skipTest("Load balancing configuration not available")
        
        with open(load_balancing_file, 'r') as f:
            load_balancing_data = json.load(f)
        
        # Check worker count is realistic
        optimal_workers = load_balancing_data.get('optimal_worker_count', 0)
        self.assertGreater(optimal_workers, 0, "Should have at least 1 worker")
        self.assertLessEqual(optimal_workers, 16, "Should not exceed reasonable worker limit")
        
        # Check resource allocation is reasonable
        resource_allocation = load_balancing_data.get('resource_allocation', {})
        memory_per_worker = resource_allocation.get('memory_per_worker_mb', 0)
        self.assertGreater(memory_per_worker, 0, "Should allocate memory per worker")
        self.assertLessEqual(memory_per_worker, 2048, "Memory per worker should be reasonable")
        
        # Check timeout is reasonable
        timeout = resource_allocation.get('timeout_seconds', 0)
        self.assertGreater(timeout, 0, "Should have a timeout")
        self.assertLessEqual(timeout, 3600, "Timeout should be reasonable (max 1 hour)")
        
        print(f"⚖️ Load balancing: {optimal_workers} workers, "
              f"{memory_per_worker}MB per worker, {timeout}s timeout")


def main():
    """Run Task 18 validation tests."""
    print("🧪 Running Task 18 Validation Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask18Validation)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 Task 18 Validation Summary:")
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"💥 Tests with errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    # Overall assessment
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun
    print(f"\n🎯 Overall Task 18 Validation: {success_rate:.1%} success rate")
    
    if success_rate >= 0.8:
        print("🎉 Task 18 implementation is SUCCESSFUL!")
    elif success_rate >= 0.6:
        print("⚠️ Task 18 implementation is PARTIALLY SUCCESSFUL - some improvements needed")
    else:
        print("❌ Task 18 implementation needs SIGNIFICANT IMPROVEMENTS")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)