"""
Test module for the ProjectCleanupAnalyzer orchestrator.

This module contains tests for the ProjectCleanupAnalyzer class, including
configuration loading, parallel execution, progress reporting, and error handling.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
import logging
from pathlib import Path

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult, BaseAnalyzer
from project_cleanup_orchestrator import ProjectCleanupAnalyzer, ProgressReporter


class MockAnalyzer(BaseAnalyzer):
    """Mock analyzer for testing."""
    
    def __init__(self, config, name="Mock Analyzer", results=None, should_fail=False):
        super().__init__(config)
        self.name = name
        self.results = results or []
        self.should_fail = should_fail
    
    def analyze(self, project_path):
        if self.should_fail:
            raise RuntimeError(f"Mock failure in {self.name}")
        return self.results
    
    def get_analyzer_name(self):
        return self.name


class TestProgressReporter(unittest.TestCase):
    """Test the ProgressReporter class."""
    
    def setUp(self):
        self.reporter = ProgressReporter(total_analyzers=3)
    
    def test_initialization(self):
        """Test that the progress reporter initializes correctly."""
        self.assertEqual(self.reporter.total_analyzers, 3)
        self.assertEqual(self.reporter.completed_analyzers, 0)
        self.assertEqual(self.reporter.get_progress(), 0)
    
    def test_analyzer_completion(self):
        """Test tracking analyzer completion."""
        self.reporter.analyzer_started("Test Analyzer")
        self.reporter.analyzer_completed("Test Analyzer", 5)
        
        self.assertEqual(self.reporter.completed_analyzers, 1)
        self.assertAlmostEqual(self.reporter.get_progress(), 33.33, places=2)
        
        # Complete another analyzer
        self.reporter.analyzer_started("Another Analyzer")
        self.reporter.analyzer_completed("Another Analyzer", 3)
        
        self.assertEqual(self.reporter.completed_analyzers, 2)
        self.assertAlmostEqual(self.reporter.get_progress(), 66.67, places=2)
    
    def test_get_summary(self):
        """Test getting a progress summary."""
        self.reporter.analyzer_started("Test Analyzer")
        self.reporter.analyzer_completed("Test Analyzer", 5)
        
        summary = self.reporter.get_summary()
        
        self.assertEqual(summary['total_analyzers'], 3)
        self.assertEqual(summary['completed_analyzers'], 1)
        self.assertAlmostEqual(summary['progress_percent'], 33.33, places=2)
        self.assertIn('elapsed_seconds', summary)
        self.assertIn('analyzer_times', summary)
        self.assertIn('Test Analyzer', summary['analyzer_times'])


class TestProjectCleanupAnalyzer(unittest.TestCase):
    """Test the ProjectCleanupAnalyzer class."""
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.config = AnalysisConfig(project_path=self.test_dir.name)
        
        # Create some test files
        self.create_test_files()
        
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
    
    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()
        
        # Re-enable logging
        logging.disable(logging.NOTSET)
    
    def create_test_files(self):
        """Create test files in the temporary directory."""
        # Create a Python file
        with open(os.path.join(self.test_dir.name, "test_file.py"), "w") as f:
            f.write("def test_function():\n    pass\n")
        
        # Create a README file
        with open(os.path.join(self.test_dir.name, "README.md"), "w") as f:
            f.write("# Test Project\n\nThis is a test project.\n")
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = ProjectCleanupAnalyzer(config=self.config)
        
        self.assertEqual(analyzer.config, self.config)
        self.assertIsNotNone(analyzer.logger)
        self.assertIsNotNone(analyzer.error_handler)
        self.assertEqual(len(analyzer.analyzers), 8)  # 8 default analyzers
    
    def test_config_loading(self):
        """Test loading configuration from a file."""
        # Create a config file
        config_path = os.path.join(self.test_dir.name, "config.json")
        config_data = {
            "project_path": self.test_dir.name,
            "output_format": "json",
            "severity_threshold": "medium"
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Load the config
        analyzer = ProjectCleanupAnalyzer(config_path=config_path)
        
        self.assertEqual(analyzer.config.project_path, self.test_dir.name)
        self.assertEqual(analyzer.config.output_format, "json")
        self.assertEqual(analyzer.config.severity_threshold, "medium")
    
    @patch('project_cleanup_orchestrator.StructureAnalyzer')
    @patch('project_cleanup_orchestrator.CodeQualityAnalyzer')
    @patch('project_cleanup_orchestrator.DeadCodeAnalyzer')
    @patch('project_cleanup_orchestrator.FileAnalyzer')
    @patch('project_cleanup_orchestrator.DependencyAnalyzer')
    @patch('project_cleanup_orchestrator.DuplicateAnalyzer')
    @patch('project_cleanup_orchestrator.ConflictAnalyzer')
    @patch('project_cleanup_orchestrator.DocumentationAnalyzer')
    def test_sequential_analysis(self, *mocks):
        """Test running analyzers sequentially."""
        # Set up mock analyzers
        mock_results = [
            AnalysisResult(
                category="test",
                severity="medium",
                description="Test issue",
                file_path="test_file.py"
            )
        ]
        
        for mock in mocks:
            mock_instance = mock.return_value
            mock_instance.analyze.return_value = mock_results
            mock_instance.get_analyzer_name.return_value = "Mock Analyzer"
            mock_instance.error_handler.get_error_summary.return_value = {}
        
        # Run analysis
        analyzer = ProjectCleanupAnalyzer(config=self.config)
        report = analyzer.run_analysis_sequential()
        
        # Check that all analyzers were called
        for mock in mocks:
            mock_instance = mock.return_value
            mock_instance.analyze.assert_called_once_with(self.test_dir.name)
        
        # Check that results were collected
        self.assertEqual(len(report.results_by_category.get("test", [])), 8)  # 8 analyzers * 1 result each
    
    def test_run_full_analysis(self):
        """Test running a full analysis with mock analyzers."""
        # Create a ProjectCleanupAnalyzer with mock analyzers
        analyzer = ProjectCleanupAnalyzer(config=self.config)
        
        # Replace the analyzers with mocks
        analyzer.analyzers = [
            MockAnalyzer(
                self.config,
                name=f"Mock Analyzer {i}",
                results=[
                    AnalysisResult(
                        category="test",
                        severity="medium",
                        description=f"Test issue {i}",
                        file_path="test_file.py"
                    )
                ]
            )
            for i in range(3)
        ]
        
        # Run analysis
        output_path = os.path.join(self.test_dir.name, "report.md")
        report_path = analyzer.run_full_analysis(parallel=False, output_path=output_path)
        
        # Check that the report was saved
        self.assertEqual(report_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Check the report content
        with open(output_path, "r") as f:
            content = f.read()
            self.assertIn("Project Cleanup Analysis Report", content)
            self.assertIn("Test issue", content)
    
    def test_error_handling(self):
        """Test handling analyzer errors."""
        # Create a ProjectCleanupAnalyzer with mock analyzers
        analyzer = ProjectCleanupAnalyzer(config=self.config)
        
        # Replace the analyzers with mocks, one of which will fail
        analyzer.analyzers = [
            MockAnalyzer(
                self.config,
                name="Working Analyzer",
                results=[
                    AnalysisResult(
                        category="test",
                        severity="medium",
                        description="Test issue",
                        file_path="test_file.py"
                    )
                ]
            ),
            MockAnalyzer(
                self.config,
                name="Failing Analyzer",
                should_fail=True
            )
        ]
        
        # Run analysis
        report = analyzer.run_analysis_sequential()
        
        # Check that the working analyzer's results were collected
        self.assertEqual(len(report.results_by_category.get("test", [])), 1)
        
        # Check that the error was recorded
        self.assertIn("Failing Analyzer", report.analyzer_errors)
        self.assertEqual(report.analyzer_errors["Failing Analyzer"], 1)


if __name__ == "__main__":
    unittest.main()