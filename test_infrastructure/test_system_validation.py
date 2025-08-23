#!/usr/bin/env python3
"""
Test System Validation Tests

Tests for the comprehensive test system validation and optimization functionality.
This ensures that task 18 is properly implemented and working correctly.
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add test infrastructure to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from system_validator import SystemValidator, ValidationResult, OptimizationResult
except ImportError as e:
    print(f"Warning: Could not import system_validator: {e}")
    SystemValidator = None


class TestSystemValidation(unittest.TestCase):
    """Test cases for system validation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        if SystemValidator is None:
            self.skipTest("SystemValidator not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.validator = SystemValidator(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_system_validator_initialization(self):
        """Test that SystemValidator initializes correctly."""
        self.assertIsInstance(self.validator, SystemValidator)
        self.assertTrue(self.validator.validation_dir.exists())
        self.assertEqual(len(self.validator.validation_history), 0)
        self.assertEqual(len(self.validator.optimization_history), 0)
    
    @patch('test_infrastructure.system_validator.TestDiscovery')
    @patch('test_infrastructure.system_validator.TestPerformanceMonitor')
    def test_validate_system_on_real_data(self, mock_monitor, mock_discovery):
        """Test system validation on real data."""
        # Mock test discovery
        mock_discovery.return_value.discover_all_tests.return_value = [
            Mock(path=Path(self.temp_dir) / "test_module", category=Mock(value="unit"))
        ]
        
        # Mock performance monitor
        mock_monitor.return_value.monitor_test_suite.return_value.__enter__ = Mock()
        mock_monitor.return_value.monitor_test_suite.return_value.__exit__ = Mock()
        
        # Run validation
        result = self.validator.validate_system_on_real_data()
        
        # Verify result
        self.assertIsInstance(result, ValidationResult)
        self.assertIsInstance(result.timestamp, str)
        self.assertIsInstance(result.validation_success, bool)
        self.assertIsInstance(result.performance_score, float)
        self.assertIsInstance(result.bottlenecks, list)
        self.assertIsInstance(result.optimization_recommendations, list)
    
    @patch('test_infrastructure.system_validator.MasterTestRunner')
    def test_optimize_execution_times(self, mock_runner):
        """Test execution time optimization."""
        # Mock test runner results
        mock_runner.return_value.run_all_tests.return_value = {
            'passed': 10,
            'failed': 0,
            'total_executions': 10
        }
        
        # Run optimization
        result = self.validator.optimize_execution_times()
        
        # Verify result
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.optimizations_applied, list)
        self.assertIsInstance(result.performance_improvement_percent, float)
        self.assertIsInstance(result.execution_time_reduction_percent, float)
    
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_configure_load_balancing(self, mock_memory, mock_cpu):
        """Test load balancing configuration."""
        # Mock system resources
        mock_cpu.return_value = 8
        mock_memory.return_value.total = 16 * 1024**3  # 16GB
        mock_memory.return_value.available = 12 * 1024**3  # 12GB available
        
        # Run load balancing configuration
        result = self.validator.configure_load_balancing()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('optimal_worker_count', result)
        self.assertIn('test_distribution_strategy', result)
        self.assertIn('resource_allocation', result)
        self.assertIn('parallel_groups', result)
        self.assertGreater(result['optimal_worker_count'], 0)
    
    def test_create_performance_monitoring_system(self):
        """Test performance monitoring system creation."""
        # Run monitoring system creation
        result = self.validator.create_performance_monitoring_system()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('monitoring_components', result)
        self.assertIn('metrics_collected', result)
        self.assertIn('alerting_rules', result)
        self.assertIn('dashboard_config', result)
        self.assertIsInstance(result['monitoring_components'], list)
        self.assertIsInstance(result['metrics_collected'], list)
    
    @patch('test_infrastructure.system_validator.TestDiscovery')
    def test_validate_test_discovery(self, mock_discovery):
        """Test test discovery validation."""
        # Mock successful discovery
        mock_module = Mock()
        mock_module.path.exists.return_value = True
        mock_module.path.glob.return_value = [Path("test_example.py")]
        mock_discovery.return_value.discover_all_tests.return_value = [mock_module]
        
        # Run validation
        result = self.validator._validate_test_discovery()
        
        # Verify result
        self.assertTrue(result)
    
    
    
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_calculate_optimal_workers(self, mock_memory, mock_cpu):
        """Test optimal worker calculation."""
        # Mock system resources
        mock_cpu.return_value = 8
        mock_memory.return_value.available = 8 * 1024**3  # 8GB
        
        system_resources = {
            'cpu_count': 8,
            'memory_available_gb': 8.0
        }
        
        # Calculate optimal workers
        optimal_workers = self.validator._calculate_optimal_workers(system_resources)
        
        # Verify result
        self.assertIsInstance(optimal_workers, int)
        self.assertGreater(optimal_workers, 0)
        self.assertLessEqual(optimal_workers, 8)  # Should not exceed max limit
    
    def test_create_distribution_strategy(self):
        """Test distribution strategy creation."""
        # Mock test discovery
        with patch.object(self.validator, 'test_discovery') as mock_discovery:
            mock_modules = [
                Mock(category=Mock(value="unit")),
                Mock(category=Mock(value="integration")),
                Mock(category=Mock(value="ui"))
            ]
            mock_discovery.discover_all_tests.return_value = mock_modules
            
            # Create distribution strategy
            strategy = self.validator._create_distribution_strategy()
            
            # Verify result
            self.assertIsInstance(strategy, str)
            self.assertIn(strategy, ["category_based", "round_robin"])
    
    def test_create_parallel_groups(self):
        """Test parallel group creation."""
        # Mock test discovery
        with patch.object(self.validator, 'test_discovery') as mock_discovery:
            mock_modules = [
                Mock(category=Mock(value="unit"), module_name="GopiAI-Core"),
                Mock(category=Mock(value="integration"), module_name="GopiAI-UI"),
                Mock(category=Mock(value="ui"), module_name="GopiAI-UI")
            ]
            mock_discovery.discover_all_tests.return_value = mock_modules
            
            # Create parallel groups
            groups = self.validator._create_parallel_groups()
            
            # Verify result
            self.assertIsInstance(groups, list)
            for group in groups:
                self.assertIsInstance(group, dict)
                self.assertIn('name', group)
                self.assertIn('tests', group)
                self.assertIn('parallel', group)
                self.assertIn('max_workers', group)
    
    def test_performance_monitoring_database_creation(self):
        """Test performance monitoring database creation."""
        # Create monitoring database
        db_path = self.validator._create_monitoring_database()
        
        # Verify database exists and has correct structure
        self.assertTrue(Path(db_path).exists())
        
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            # Check if tables exist
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('test_performance', tables)
            self.assertIn('system_performance', tables)
    
    def test_metrics_collection_setup(self):
        """Test metrics collection setup."""
        # Set up metrics collection
        metrics = self.validator._setup_metrics_collection()
        
        # Verify metrics
        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)
        
        expected_metrics = [
            'test_execution_time',
            'test_success_rate',
            'memory_usage',
            'cpu_usage',
            'parallel_efficiency'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
    
    def test_performance_alerting_configuration(self):
        """Test performance alerting configuration."""
        # Configure alerting
        alerting_rules = self.validator._configure_performance_alerting()
        
        # Verify alerting rules
        self.assertIsInstance(alerting_rules, list)
        self.assertGreater(len(alerting_rules), 0)
        
        for rule in alerting_rules:
            self.assertIsInstance(rule, dict)
            self.assertIn('name', rule)
            self.assertIn('condition', rule)
            self.assertIn('severity', rule)
            self.assertIn('action', rule)
    
    def test_performance_dashboard_creation(self):
        """Test performance dashboard creation."""
        # Create dashboard configuration
        dashboard_config = self.validator._create_performance_dashboard()
        
        # Verify dashboard configuration
        self.assertIsInstance(dashboard_config, dict)
        self.assertIn('title', dashboard_config)
        self.assertIn('panels', dashboard_config)
        self.assertIn('alerts', dashboard_config)
        
        # Verify panels
        panels = dashboard_config['panels']
        self.assertIsInstance(panels, list)
        self.assertGreater(len(panels), 0)
        
        for panel in panels:
            self.assertIn('title', panel)
            self.assertIn('type', panel)
            self.assertIn('metrics', panel)
    
    def test_historical_tracking_setup(self):
        """Test historical tracking setup."""
        # Set up historical tracking
        tracking_config = self.validator._setup_historical_tracking()
        
        # Verify tracking configuration
        self.assertIsInstance(tracking_config, dict)
        self.assertIn('retention_days', tracking_config)
        self.assertIn('aggregation_intervals', tracking_config)
        self.assertIn('metrics_to_track', tracking_config)
        self.assertIn('trend_analysis', tracking_config)
    
    def test_performance_thresholds_definition(self):
        """Test performance thresholds definition."""
        # Define performance thresholds
        thresholds = self.validator._define_performance_thresholds()
        
        # Verify thresholds
        self.assertIsInstance(thresholds, dict)
        
        expected_thresholds = [
            'max_execution_time_seconds',
            'min_success_rate',
            'max_memory_usage_percent',
            'max_cpu_usage_percent',
            'min_parallel_efficiency'
        ]
        
        for threshold in expected_thresholds:
            self.assertIn(threshold, thresholds)
            self.assertIsInstance(thresholds[threshold], (int, float))
    
    def test_monitoring_scripts_creation(self):
        """Test monitoring scripts creation."""
        # Create monitoring scripts
        scripts = self.validator._create_monitoring_scripts()
        
        # Verify scripts
        self.assertIsInstance(scripts, list)
        self.assertGreater(len(scripts), 0)
        
        # Check if script files were created
        expected_scripts = [
            "monitor_performance.py",
            "performance_alerts.py",
            "performance_dashboard.py"
        ]
        
        for script_name in expected_scripts:
            script_path = self.validator.validation_dir / script_name
            self.assertTrue(script_path.exists())
    
    def test_validation_result_saving(self):
        """Test validation result saving."""
        # Create test validation result
        result = ValidationResult(
            timestamp="2024-01-01T00:00:00",
            validation_success=True,
            total_tests_run=100,
            tests_passed=95,
            tests_failed=5,
            execution_time_seconds=300.0,
            performance_score=85.5,
            bottlenecks=["slow_test_1"],
            optimization_recommendations=["optimize_test_1"],
            resource_usage={"memory": 512.0, "cpu": 75.0}
        )
        
        # Save result
        self.validator._save_validation_result(result)
        
        # Verify result was saved
        self.assertEqual(len(self.validator.validation_history), 1)
        
        # Check if files were created
        result_files = list(self.validator.validation_dir.glob("validation_result_*.json"))
        self.assertGreater(len(result_files), 0)
    
    def test_optimization_result_saving(self):
        """Test optimization result saving."""
        # Create test optimization result
        result = OptimizationResult(
            timestamp="2024-01-01T00:00:00",
            optimizations_applied=["pytest_config", "test_caching"],
            performance_improvement_percent=15.0,
            execution_time_reduction_percent=25.0,
            resource_savings={"memory_mb_saved": 100.0, "cpu_percent_saved": 10.0},
            load_balancing_config={"workers": 4}
        )
        
        # Save result
        self.validator._save_optimization_result(result)
        
        # Verify result was saved
        self.assertEqual(len(self.validator.optimization_history), 1)
        
        # Check if files were created
        result_files = list(self.validator.validation_dir.glob("optimization_result_*.json"))
        self.assertGreater(len(result_files), 0)


class TestSystemValidationIntegration(unittest.TestCase):
    """Integration tests for system validation."""
    
    def setUp(self):
        """Set up integration test environment."""
        if SystemValidator is None:
            self.skipTest("SystemValidator not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.validator = SystemValidator(self.temp_dir)
    
    def tearDown(self):
        """Clean up integration test environment."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('test_infrastructure.system_validator.MasterTestRunner')
    @patch('test_infrastructure.system_validator.TestDiscovery')
    def test_full_validation_workflow(self, mock_discovery, mock_runner):
        """Test the complete validation workflow."""
        # Mock test discovery
        mock_discovery.return_value.discover_all_tests.return_value = [
            Mock(path=Path(self.temp_dir) / "test_module", 
                 category=Mock(value="unit"))
        ]
        
        # Mock test runner
        mock_runner.return_value.run_all_tests.return_value = {
            'passed': 8,
            'failed': 2,
            'total_executions': 10
        }
        
        # Run full validation
        validation_result = self.validator.validate_system_on_real_data()
        optimization_result = self.validator.optimize_execution_times()
        load_balancing_config = self.validator.configure_load_balancing()
        monitoring_system = self.validator.create_performance_monitoring_system()
        
        # Verify all components completed successfully
        self.assertIsInstance(validation_result, ValidationResult)
        self.assertIsInstance(optimization_result, OptimizationResult)
        self.assertIsInstance(load_balancing_config, dict)
        self.assertIsInstance(monitoring_system, dict)
        
        # Verify files were created
        self.assertTrue(len(list(self.validator.validation_dir.glob("*.json"))) > 0)


def run_system_validation_tests():
    """Run all system validation tests."""
    print("🧪 Running system validation tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSystemValidation))
    test_suite.addTest(unittest.makeSuite(TestSystemValidationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ All system validation tests passed!")
    else:
        print(f"\n❌ Some system validation tests failed!")
    
    return success


if __name__ == "__main__":
    run_system_validation_tests()