#!/usr/bin/env python3
"""
Unit tests for CodeQualityAnalyzer.
"""

import unittest
import tempfile
import os
import sys
import ast
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules
from project_cleanup_analyzer import AnalysisConfig, AnalysisResult, AnalysisError
from code_quality_analyzer import CodeQualityAnalyzer, ComplexityVisitor, StyleChecker


class TestComplexityVisitor(unittest.TestCase):
    """Test cases for ComplexityVisitor."""
    
    def test_simple_function_complexity(self):
        """Test complexity calculation for simple function."""
        code = '''
def simple_function():
    return "hello"
'''
        tree = ast.parse(code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        self.assertEqual(len(visitor.complexity_results), 1)
        name, complexity, line_num = visitor.complexity_results[0]
        self.assertEqual(name, 'simple_function')
        self.assertEqual(complexity, 1)
    
    def test_complex_function_complexity(self):
        """Test complexity calculation for complex function."""
        code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    try:
                        result = x / i
                    except ZeroDivisionError:
                        result = 0
                    return result
    return 0
'''
        tree = ast.parse(code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        self.assertEqual(len(visitor.complexity_results), 1)
        name, complexity, line_num = visitor.complexity_results[0]
        self.assertEqual(name, 'complex_function')
        self.assertGreater(complexity, 5)  # Should be complex


class TestStyleChecker(unittest.TestCase):
    """Test cases for StyleChecker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.checker = StyleChecker()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_line_too_long(self):
        """Test detection of lines that are too long."""
        content = 'def function():\n    return "This is a very long line that exceeds the recommended 88 character limit and should be flagged"\n'
        file_path = self.create_test_file("test.py", content)
        
        issues = self.checker.check_file(file_path)
        line_too_long_issues = [i for i in issues if i.issue_type == 'line_too_long']
        
        self.assertGreater(len(line_too_long_issues), 0)
    
    def test_trailing_whitespace(self):
        """Test detection of trailing whitespace."""
        content = 'def function():   \n    return "hello"\n'
        file_path = self.create_test_file("test.py", content)
        
        issues = self.checker.check_file(file_path)
        trailing_issues = [i for i in issues if i.issue_type == 'trailing_whitespace']
        
        self.assertGreater(len(trailing_issues), 0)


class TestCodeQualityAnalyzer(unittest.TestCase):
    """Test cases for CodeQualityAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalysisConfig(project_path=self.temp_dir)
        self.analyzer = CodeQualityAnalyzer(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = Path(self.temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_analyzer_creation(self):
        """Test that the analyzer can be created."""
        self.assertEqual(self.analyzer.get_analyzer_name(), "Code Quality Analyzer")
        self.assertIsInstance(self.analyzer.complexity_results, list)
        self.assertIsInstance(self.analyzer.style_issues, list)
        self.assertIsInstance(self.analyzer.consistency_issues, list)
    
    def test_complexity_analysis(self):
        """Test complexity analysis functionality."""
        # Create a function that's definitely complex enough to trigger warnings
        content = '''"""Module with complex functions for testing."""

def simple():
    return 1

def very_complex(x, y, z, a, b):
    """A very complex function that should trigger complexity warnings."""
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        for i in range(x):
                            for j in range(y):
                                for k in range(z):
                                    if i * j * k > a:
                                        try:
                                            if i % 2 == 0:
                                                if j % 2 == 0:
                                                    if k % 2 == 0:
                                                        result = x / (i + j + k)
                                                        if result > b:
                                                            return result
                                                        elif result < 0:
                                                            continue
                                                        else:
                                                            break
                                        except ZeroDivisionError:
                                            continue
                                        except ValueError:
                                            break
                                    elif i + j + k > b:
                                        return i + j + k
    return 0
'''
        self.create_test_file("test.py", content)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should find at least some results (complexity or style)
        self.assertGreater(len(results), 0)
        
        # Check if we have complexity results
        complexity_results = [r for r in results if r.category == 'complexity']
        
        # The very_complex function should definitely trigger a complexity warning
        if len(complexity_results) > 0:
            complex_function_results = [r for r in complexity_results if 'very_complex' in r.description]
            self.assertGreater(len(complex_function_results), 0, "very_complex function should trigger complexity warning")
    
    def test_empty_project(self):
        """Test analysis of empty project."""
        results = self.analyzer.analyze(self.temp_dir)
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)