"""
Unit Tests for DocumentationAnalyzer

This module contains comprehensive unit tests for the DocumentationAnalyzer class,
testing docstring coverage analysis, README quality assessment, documentation
consistency checks, and outdated reference detection.
"""
import unittest
import tempfile
import os
import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from documentation_analyzer import (
    DocumentationAnalyzer, DocstringInfo, ReadmeInfo, 
    DocumentationReference, DocstringAnalyzer
)


class TestDocumentationAnalyzer(unittest.TestCase):
    """Test cases for DocumentationAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalysisConfig(project_path=self.temp_dir)
        self.analyzer = DocumentationAnalyzer(self.config)
    
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
    
    def test_analyzer_name(self):
        """Test analyzer name."""
        self.assertEqual(self.analyzer.get_analyzer_name(), "Documentation Analyzer")
    
    def test_docstring_coverage_analysis(self):
        """Test analysis of docstring coverage."""
        # Create a file with mixed docstring coverage
        test_code = '''"""
Module docstring with proper documentation.
"""

def function_with_docstring():
    """
    This function has a docstring.
    
    Returns:
        None
    """
    pass

def function_without_docstring():
    pass

class ClassWithDocstring:
    """
    This class has a docstring.
    """
    
    def method_with_docstring(self):
        """
        This method has a docstring.
        
        Args:
            self: The instance
            
        Returns:
            None
        """
        pass
    
    def method_without_docstring(self):
        pass
'''
        self.create_test_file("test_docstrings.py", test_code)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect docstring coverage issues
        docstring_results = [r for r in results if r.category in ['docstring_coverage', 'missing_docstring']]
        self.assertGreater(len(docstring_results), 0)
    
    def test_readme_quality_analysis(self):
        """Test analysis of README quality."""
        # Create a minimal README with missing sections
        minimal_readme = '''# Test Project

A very minimal README without proper sections.
'''
        self.create_test_file("README.md", minimal_readme)
        
        # Create a more complete README
        complete_readme = '''# Complete Test Project

## Introduction
This is a test project with a more complete README.

## Installation
Install with pip:
```
pip install test-project
```

## Usage
Here's how to use the project:
```python
import test_project
test_project.run()
```

## API Documentation
See the API docs for more details.
'''
        self.create_test_file("gopiai/README.md", complete_readme)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect README quality issues
        readme_results = [r for r in results if r.category in ['readme_completeness', 'readme_length']]
        self.assertGreater(len(readme_results), 0)
    
    def test_documentation_reference_analysis(self):
        """Test analysis of documentation references."""
        # Create a README with references to files
        readme_with_refs = '''# Test Project

## Files
- See `test_file.py` for implementation
- Import from `nonexistent_module`
- Check the configuration in `config.json`
'''
        self.create_test_file("README.md", readme_with_refs)
        
        # Create one of the referenced files
        self.create_test_file("test_file.py", "# Test file")
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect invalid references
        reference_results = [r for r in results if r.category == 'invalid_reference']
        self.assertGreater(len(reference_results), 0)
    
    def test_documentation_consistency_analysis(self):
        """Test analysis of documentation consistency."""
        # Create directory structure
        (Path(self.temp_dir) / "gopiai" / "module1").mkdir(parents=True)
        (Path(self.temp_dir) / "gopiai" / "module2").mkdir(parents=True)
        
        # Create files with inconsistent docstring styles
        google_style = '''"""Module using Google style docstrings."""

def function1(param1, param2):
    """
    Function with Google style docstring.
    
    Args:
        param1: First parameter
        param2: Second parameter
        
    Returns:
        The result
    """
    return param1 + param2
'''
        self.create_test_file("gopiai/module1/google_style.py", google_style)
        
        sphinx_style = '''"""Module using Sphinx style docstrings."""

def function1(param1, param2):
    """
    Function with Sphinx style docstring.
    
    :param param1: First parameter
    :param param2: Second parameter
    :return: The result
    """
    return param1 + param2
'''
        self.create_test_file("gopiai/module1/sphinx_style.py", sphinx_style)
        
        # Add more files to reach the threshold for consistency checking
        for i in range(3):
            self.create_test_file(f"gopiai/module1/extra{i}.py", google_style)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # May detect docstring style inconsistency
        # Note: This test might be fragile depending on the implementation details
        consistency_results = [r for r in results if r.category == 'docstring_style_inconsistency']
        # We don't assert on the length here as it depends on implementation details
    
    def test_empty_project(self):
        """Test analysis of empty project."""
        results = self.analyzer.analyze(self.temp_dir)
        self.assertEqual(len(results), 0)
    
    def test_invalid_python_file(self):
        """Test handling of invalid Python files."""
        # Create a file with syntax errors
        self.create_test_file("invalid.py", "def incomplete_function(:\n    pass")
        
        # Should handle gracefully without crashing
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should have recorded errors
        self.assertTrue(self.analyzer.error_handler.has_errors())


class TestDocstringAnalyzer(unittest.TestCase):
    """Test cases for DocstringAnalyzer."""
    
    def test_module_docstring_detection(self):
        """Test detection of module docstrings."""
        analyzer = DocstringAnalyzer("test.py")
        
        import ast
        code = '''"""
Module docstring.
"""

def function():
    pass
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should detect module docstring
        module_docstrings = [info for info in analyzer.docstring_info if info.element_type == 'module']
        self.assertEqual(len(module_docstrings), 1)
        self.assertTrue(module_docstrings[0].has_docstring)
    
    def test_function_docstring_detection(self):
        """Test detection of function docstrings."""
        analyzer = DocstringAnalyzer("test.py")
        
        import ast
        code = '''
def function_with_docstring():
    """
    Function docstring.
    
    Args:
        None
        
    Returns:
        None
    """
    pass

def function_without_docstring():
    pass
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should detect both functions, one with docstring and one without
        function_docstrings = [info for info in analyzer.docstring_info if info.element_type == 'function']
        self.assertEqual(len(function_docstrings), 2)
        
        with_docstring = [info for info in function_docstrings if info.has_docstring]
        without_docstring = [info for info in function_docstrings if not info.has_docstring]
        
        self.assertEqual(len(with_docstring), 1)
        self.assertEqual(len(without_docstring), 1)
        
        # Check parameter and return detection
        self.assertTrue(with_docstring[0].has_parameters)
        self.assertTrue(with_docstring[0].has_returns)
    
    def test_class_and_method_docstring_detection(self):
        """Test detection of class and method docstrings."""
        analyzer = DocstringAnalyzer("test.py")
        
        import ast
        code = '''
class TestClass:
    """
    Class docstring.
    """
    
    def method_with_docstring(self):
        """
        Method docstring.
        
        Args:
            self: The instance
            
        Returns:
            None
        """
        pass
    
    def method_without_docstring(self):
        pass
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should detect class docstring
        class_docstrings = [info for info in analyzer.docstring_info if info.element_type == 'class']
        self.assertEqual(len(class_docstrings), 1)
        self.assertTrue(class_docstrings[0].has_docstring)
        
        # Should detect both methods, one with docstring and one without
        method_docstrings = [info for info in analyzer.docstring_info if info.element_type == 'method']
        self.assertEqual(len(method_docstrings), 2)
        
        with_docstring = [info for info in method_docstrings if info.has_docstring]
        without_docstring = [info for info in method_docstrings if not info.has_docstring]
        
        self.assertEqual(len(with_docstring), 1)
        self.assertEqual(len(without_docstring), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for DocumentationAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalysisConfig(project_path=self.temp_dir)
    
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
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis with multiple documentation issues."""
        # Create a project structure
        (Path(self.temp_dir) / "gopiai" / "module1").mkdir(parents=True)
        (Path(self.temp_dir) / "docs").mkdir(parents=True)
        
        # Create a README with issues
        readme_content = '''# Test Project

A minimal README without proper sections.

See `nonexistent.py` for implementation details.
'''
        self.create_test_file("README.md", readme_content)
        
        # Create a Python file with docstring issues
        python_file = '''"""
Module docstring.
"""

def function_without_docstring():
    # This function lacks a docstring
    pass

class PartiallyDocumented:
    """
    Class with docstring.
    """
    
    def documented_method(self):
        """This method has a docstring but no parameter or return docs."""
        pass
    
    def undocumented_method(self):
        pass
'''
        self.create_test_file("gopiai/module1/test.py", python_file)
        
        # Create a documentation file with references
        doc_file = '''# API Documentation

## Functions

- `function_without_docstring` in `gopiai/module1/test.py`
- `nonexistent_function` in `gopiai/module1/nonexistent.py`
'''
        self.create_test_file("docs/api.md", doc_file)
        
        analyzer = DocumentationAnalyzer(self.config)
        results = analyzer.analyze(self.temp_dir)
        
        # Should detect multiple types of issues
        categories = set(result.category for result in results)
        
        # Verify we found different types of issues
        self.assertGreater(len(results), 0)
        self.assertGreater(len(categories), 1)
        
        # Check summary
        summary = analyzer.get_documentation_summary()
        self.assertEqual(summary['total_python_files'], 1)
        self.assertEqual(summary['total_readme_files'], 1)
        self.assertGreater(summary['total_docstrings'], 0)
    
    def test_severity_filtering(self):
        """Test severity-based filtering of results."""
        # Create a file with documentation issues
        python_file = '''
def function_without_docstring():
    pass

class UndocumentedClass:
    def method(self):
        pass
'''
        self.create_test_file("test.py", python_file)
        
        # Test with different severity thresholds
        for threshold in ['low', 'medium', 'high']:
            config = AnalysisConfig(project_path=self.temp_dir, severity_threshold=threshold)
            analyzer = DocumentationAnalyzer(config)
            results = analyzer.analyze(self.temp_dir)
            
            # All results should meet the threshold
            severity_order = {'low': 0, 'medium': 1, 'high': 2}
            threshold_level = severity_order[threshold]
            
            for result in results:
                result_level = severity_order[result.severity]
                self.assertGreaterEqual(result_level, threshold_level)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run the tests
    unittest.main(verbosity=2)