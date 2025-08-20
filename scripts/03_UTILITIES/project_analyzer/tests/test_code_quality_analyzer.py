"""
Comprehensive tests for CodeQualityAnalyzer.
"""

import unittest
import tempfile
import os
import sys
import ast
from pathlib import Path
from unittest.mock import patch, MagicMock

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
    
    def test_multiple_functions(self):
        """Test complexity calculation for multiple functions."""
        code = '''
def simple():
    return 1

def medium(x):
    if x > 0:
        return x * 2
    return 0

def complex(x, y):
    if x > 0:
        if y > 0:
            for i in range(x):
                if i % 2 == 0:
                    return i
    return -1
'''
        tree = ast.parse(code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        self.assertEqual(len(visitor.complexity_results), 3)
        
        complexities = {name: complexity for name, complexity, _ in visitor.complexity_results}
        self.assertEqual(complexities['simple'], 1)
        self.assertGreater(complexities['medium'], 1)
        self.assertGreater(complexities['complex'], complexities['medium'])


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
    
    def test_tab_indentation(self):
        """Test detection of tab indentation."""
        content = 'def function():\n\treturn "hello"\n'
        file_path = self.create_test_file("test.py", content)
        
        issues = self.checker.check_file(file_path)
        tab_issues = [i for i in issues if i.issue_type == 'tab_indentation']
        
        self.assertGreater(len(tab_issues), 0)
    
    def test_multiple_statements(self):
        """Test detection of multiple statements on one line."""
        content = 'def function(): x = 1; y = 2; return x + y\n'
        file_path = self.create_test_file("test.py", content)
        
        issues = self.checker.check_file(file_path)
        multiple_stmt_issues = [i for i in issues if i.issue_type == 'multiple_statements']
        
        self.assertGreater(len(multiple_stmt_issues), 0)


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
        content = '''
def simple():
    return 1

def complex(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(x):
                    for j in range(y):
                        if i * j > z:
                            return i * j
    return 0
'''
        self.create_test_file("test.py", content)
        
        results = self.analyzer.analyze(self.temp_dir)
        complexity_results = [r for r in results if r.category == 'complexity']
        
        self.assertGreater(len(complexity_results), 0)
        
        # Check that we found the complex function
        complex_issues = [r for r in complexity_results if 'complex' in r.description]
        self.assertGreater(len(complex_issues), 0)
    
    def test_style_analysis(self):
        """Test style analysis functionality."""
        content = '''def bad_style():
    return "This line is way too long and exceeds the 88 character limit that we have set for our code style guidelines"
    
def trailing_spaces():   
    return "hello"
'''
        self.create_test_file("test.py", content)
        
        results = self.analyzer.analyze(self.temp_dir)
        style_results = [r for r in results if r.category == 'style']
        
        self.assertGreater(len(style_results), 0)
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        content = '''
def broken_function(
    # Missing closing parenthesis and colon
    return "broken"
'''
        self.create_test_file("broken.py", content)
        
        results = self.analyzer.analyze(self.temp_dir)
        syntax_errors = [r for r in results if r.category == 'syntax_error']
        
        self.assertGreater(len(syntax_errors), 0)
    
    def test_quality_summary(self):
        """Test quality summary generation."""
        content = '''
def simple():
    return 1

def complex(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    return i
    return 0

def bad_style():
    return "This line is way too long and exceeds the recommended character limit"
'''
        self.create_test_file("test.py", content)
        
        self.analyzer.analyze(self.temp_dir)
        summary = self.analyzer.get_quality_summary()
        
        self.assertIn('total_complexity_issues', summary)
        self.assertIn('total_style_issues', summary)
        self.assertIn('average_complexity', summary)
        self.assertIn('flake8_available', summary)
        self.assertIn('black_available', summary)
    
    def test_empty_project(self):
        """Test analysis of empty project."""
        results = self.analyzer.analyze(self.temp_dir)
        self.assertEqual(len(results), 0)
    
    def test_non_python_files_ignored(self):
        """Test that non-Python files are ignored."""
        self.create_test_file("readme.txt", "This is not Python code")
        self.create_test_file("config.json", '{"key": "value"}')
        
        results = self.analyzer.analyze(self.temp_dir)
        self.assertEqual(len(results), 0)


def run_simple_test():
    """Run a simple test of the CodeQualityAnalyzer."""
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        print("Testing CodeQualityAnalyzer...")
        
        # Try to import and test the analyzer
        try:
            from code_quality_analyzer import CodeQualityAnalyzer
            
            # Create configuration
            config = AnalysisConfig(project_path=".")
            
            # Create analyzer
            analyzer = CodeQualityAnalyzer(config)
            print(f"Created {analyzer.get_analyzer_name()}")
            print(f"Flake8 available: {analyzer.flake8_available}")
            print(f"Black available: {analyzer.black_available}")
            
            # Run analysis on a few Python files
            python_files = list(Path(".").glob("*.py"))[:3]
            print(f"Found {len(python_files)} Python files for testing")
            
            if python_files:
                # Test complexity analysis
                complexity_results = analyzer._analyze_code_complexity(python_files)
                print(f"Complexity analysis found {len(complexity_results)} issues")
                
                # Test style analysis
                style_results = analyzer._check_common_style_issues(python_files)
                print(f"Style analysis found {len(style_results)} issues")
                
                # Test full analysis
                results = analyzer.analyze(".")
                print(f"Full analysis found {len(results)} issues")
                
                # Print some example results
                if results:
                    print("\nExample results:")
                    for i, result in enumerate(results[:5]):
                        print(f"  {i+1}. {result.severity.upper()}: {result.description}")
                        if result.recommendation:
                            print(f"     → {result.recommendation}")
                
                # Print summary
                summary = analyzer.get_quality_summary()
                print("\nQuality Summary:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
            
            print("\nTest completed successfully!")
            return True
            
        except ImportError as e:
            print(f"CodeQualityAnalyzer not available: {e}")
            print("This is expected if the implementation is not complete yet.")
            return False
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CodeQualityAnalyzer")
    parser.add_argument("--unittest", action="store_true", help="Run unit tests")
    parser.add_argument("--simple", action="store_true", help="Run simple test")
    
    args = parser.parse_args()
    
    if args.unittest:
        # Run unit tests
        unittest.main(argv=[''], exit=False, verbosity=2)
    elif args.simple:
        # Run simple test
        success = run_simple_test()
        sys.exit(0 if success else 1)
    else:
        # Default: run simple test
        success = run_simple_test()
        sys.exit(0 if success else 1)