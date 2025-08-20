"""
Unit Tests for ReportGenerator

This module contains comprehensive unit tests for the ReportGenerator class,
testing report generation, formatting, and output in various formats.
"""
import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from report_generator import ReportGenerator, CleanupReport


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalysisConfig(project_path=self.temp_dir)
        self.report_generator = ReportGenerator(self.config)
        
        # Create sample results for testing
        self.sample_results = [
            AnalysisResult(
                category="dead_code",
                severity="high",
                description="Unused function 'calculate_total'",
                file_path="sample/file.py",
                line_number=42,
                recommendation="Remove or refactor this unused function"
            ),
            AnalysisResult(
                category="dead_code",
                severity="medium",
                description="Unused import 'datetime'",
                file_path="sample/file.py",
                line_number=5,
                recommendation="Remove this unused import"
            ),
            AnalysisResult(
                category="code_quality",
                severity="medium",
                description="Function 'process_data' is too complex (cyclomatic complexity: 15)",
                file_path="sample/complex.py",
                line_number=78,
                recommendation="Refactor this function into smaller, more focused functions"
            ),
            AnalysisResult(
                category="structure",
                severity="low",
                description="File 'utils.py' doesn't follow module naming conventions",
                file_path="sample/utils.py",
                recommendation="Rename to follow project conventions"
            ),
            AnalysisResult(
                category="docstring_coverage",
                severity="medium",
                description="Low docstring coverage (25%) in core module",
                file_path="sample/core.py",
                recommendation="Add docstrings to improve documentation coverage"
            )
        ]
        
        self.sample_errors = {
            "Test Analyzer": 1,
            "Code Quality Analyzer": 2
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_report(self):
        """Test generating a report from analysis results."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        # Verify report structure
        self.assertIsInstance(report, CleanupReport)
        self.assertEqual(report.project_path, self.temp_dir)
        self.assertEqual(report.analyzer_errors, self.sample_errors)
        
        # Verify summary counts
        self.assertEqual(report.summary["dead_code"], 2)
        self.assertEqual(report.summary["code_quality"], 1)
        self.assertEqual(report.summary["structure"], 1)
        self.assertEqual(report.summary["docstring_coverage"], 1)
        
        # Verify results by category
        self.assertEqual(len(report.results_by_category["dead_code"]), 2)
        self.assertEqual(len(report.results_by_category["code_quality"]), 1)
        
        # Verify priority actions (should include high severity issues)
        high_severity_results = [r for r in self.sample_results if r.severity == "high"]
        self.assertEqual(len(report.priority_actions), len(high_severity_results))
        for action in report.priority_actions:
            self.assertEqual(action.severity, "high")
        
        # Verify recommendations
        self.assertTrue(any("dead code" in rec.lower() for rec in report.recommendations))
    
    def test_generate_markdown_report(self):
        """Test generating a markdown report."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        markdown = self.report_generator.generate_markdown_report(report)
        
        # Verify markdown structure
        self.assertIn("# Project Cleanup Analysis Report", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("## Detailed Findings", markdown)
        
        # Verify content
        self.assertIn("Dead Code", markdown)
        self.assertIn("Code Quality", markdown)
        self.assertIn("HIGH", markdown)
        self.assertIn("MEDIUM", markdown)
        
        # Verify recommendations
        self.assertIn("## Key Recommendations", markdown)
        
        # Verify errors section
        self.assertIn("## Analysis Errors", markdown)
        self.assertIn("Test Analyzer", markdown)
    
    def test_generate_json_report(self):
        """Test generating a JSON report."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        json_str = self.report_generator.generate_json_report(report)
        
        # Verify JSON can be parsed
        json_data = json.loads(json_str)
        
        # Verify structure
        self.assertIn("timestamp", json_data)
        self.assertIn("project_path", json_data)
        self.assertIn("summary", json_data)
        self.assertIn("results_by_category", json_data)
        self.assertIn("recommendations", json_data)
        self.assertIn("priority_actions", json_data)
        self.assertIn("analyzer_errors", json_data)
        
        # Verify content
        self.assertEqual(json_data["project_path"], self.temp_dir)
        self.assertEqual(json_data["summary"]["dead_code"], 2)
        
        # Verify priority actions count matches high severity issues
        high_severity_count = sum(1 for r in self.sample_results if r.severity == "high")
        self.assertEqual(len(json_data["priority_actions"]), high_severity_count)
    
    def test_generate_html_report(self):
        """Test generating an HTML report."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        html = self.report_generator.generate_html_report(report)
        
        # Verify HTML structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)
        self.assertIn("<head>", html)
        self.assertIn("<body>", html)
        
        # Verify content
        self.assertIn("Project Cleanup Analysis Report", html)
        self.assertIn("Dead Code", html)
        self.assertIn("Code Quality", html)
        self.assertIn("HIGH", html)
        self.assertIn("MEDIUM", html)
        
        # Verify styling
        self.assertIn("<style>", html)
        self.assertIn("severity-high", html)
        
        # Verify interactive elements
        self.assertIn("collapsible", html)
        self.assertIn("<script>", html)
    
    def test_save_report(self):
        """Test saving a report to a file."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        # Test saving in different formats
        for format_type in ['markdown', 'json', 'html']:
            self.config.output_format = format_type
            output_path = os.path.join(self.temp_dir, f"test_report.{format_type}")
            
            saved_path = self.report_generator.save_report(report, output_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(saved_path))
            
            # Verify file content
            with open(saved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if format_type == 'markdown':
                    self.assertIn("# Project Cleanup Analysis Report", content)
                elif format_type == 'json':
                    self.assertIn("\"timestamp\":", content)
                elif format_type == 'html':
                    self.assertIn("<!DOCTYPE html>", content)
    
    def test_recommendations_generation(self):
        """Test generation of recommendations based on result categories."""
        # Test with different result categories
        category_tests = [
            (["dead_code"], "Remove identified dead code"),
            (["duplicate_code"], "Refactor duplicate code"),
            (["code_quality"], "Address code quality issues"),
            (["structure"], "Reorganize project structure"),
            (["dependency"], "Update and consolidate dependencies"),
            (["docstring_coverage"], "Improve docstring coverage"),
            (["readme_completeness"], "Enhance documentation"),
            (["conflict"], "Address potential runtime conflicts")
        ]
        
        for categories, expected_text in category_tests:
            # Create results with the specified categories
            results = []
            for category in categories:
                results.append(AnalysisResult(
                    category=category,
                    severity="medium",
                    description=f"Test {category} issue",
                    file_path="test.py"
                ))
            
            # Generate report
            report = self.report_generator.generate_report(results, {})
            
            # Check if the expected recommendation text is present
            recommendation_found = any(
                expected_text.lower() in rec.lower() for rec in report.recommendations
            )
            self.assertTrue(
                recommendation_found, 
                f"Expected recommendation containing '{expected_text}' not found"
            )
    
    def test_priority_actions_selection(self):
        """Test selection of priority actions based on severity."""
        # Create results with different severities
        results = [
            AnalysisResult(
                category="category1",
                severity="high",
                description="High severity issue 1",
                file_path="test1.py"
            ),
            AnalysisResult(
                category="category2",
                severity="high",
                description="High severity issue 2",
                file_path="test2.py"
            ),
            AnalysisResult(
                category="category3",
                severity="medium",
                description="Medium severity issue 1",
                file_path="test3.py"
            ),
            AnalysisResult(
                category="category4",
                severity="medium",
                description="Medium severity issue 2",
                file_path="test4.py"
            ),
            AnalysisResult(
                category="category5",
                severity="low",
                description="Low severity issue",
                file_path="test5.py"
            )
        ]
        
        # Generate report
        report = self.report_generator.generate_report(results, {})
        
        # Verify priority actions
        self.assertEqual(len(report.priority_actions), 2)  # 2 high severity issues
        
        # Verify high severity issues are included first
        self.assertEqual(report.priority_actions[0].severity, "high")
        self.assertEqual(report.priority_actions[1].severity, "high")
        
        # Verify medium severity issues are not included when high severity ones exist
        medium_count = sum(1 for action in report.priority_actions if action.severity == "medium")
        self.assertEqual(medium_count, 0)
        
        # Verify low severity issues are not included
        low_count = sum(1 for action in report.priority_actions if action.severity == "low")
        self.assertEqual(low_count, 0)
        
        # Test with only medium severity issues
        medium_results = [
            AnalysisResult(
                category="category3",
                severity="medium",
                description="Medium severity issue 1",
                file_path="test3.py"
            ),
            AnalysisResult(
                category="category4",
                severity="medium",
                description="Medium severity issue 2",
                file_path="test4.py"
            )
        ]
        
        medium_report = self.report_generator.generate_report(medium_results, {})
        
        # Verify one medium severity issue is included when no high severity issues exist
        self.assertEqual(len(medium_report.priority_actions), 1)
        self.assertEqual(medium_report.priority_actions[0].severity, "medium")
    
    def test_unsupported_output_format(self):
        """Test handling of unsupported output formats."""
        report = self.report_generator.generate_report(
            self.sample_results, self.sample_errors
        )
        
        # Set an unsupported format
        self.config.output_format = 'unsupported'
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.report_generator.save_report(report)


class TestCleanupReport(unittest.TestCase):
    """Test cases for CleanupReport dataclass."""
    
    def test_cleanup_report_creation(self):
        """Test creating a CleanupReport instance."""
        timestamp = datetime.now().isoformat()
        project_path = "/test/path"
        summary = {"category1": 5, "category2": 3}
        results_by_category = {
            "category1": [
                AnalysisResult(
                    category="category1",
                    severity="medium",
                    description="Test issue",
                    file_path="test.py"
                )
            ]
        }
        recommendations = ["Recommendation 1", "Recommendation 2"]
        priority_actions = [
            AnalysisResult(
                category="category1",
                severity="high",
                description="High priority issue",
                file_path="test.py"
            )
        ]
        analyzer_errors = {"Analyzer1": 2}
        
        report = CleanupReport(
            timestamp=timestamp,
            project_path=project_path,
            summary=summary,
            results_by_category=results_by_category,
            recommendations=recommendations,
            priority_actions=priority_actions,
            analyzer_errors=analyzer_errors
        )
        
        # Verify attributes
        self.assertEqual(report.timestamp, timestamp)
        self.assertEqual(report.project_path, project_path)
        self.assertEqual(report.summary, summary)
        self.assertEqual(report.results_by_category, results_by_category)
        self.assertEqual(report.recommendations, recommendations)
        self.assertEqual(report.priority_actions, priority_actions)
        self.assertEqual(report.analyzer_errors, analyzer_errors)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run the tests
    unittest.main(verbosity=2)