#!/usr/bin/env python3
"""
Simple test for CodeQualityAnalyzer to verify it works correctly.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig
from code_quality_analyzer import CodeQualityAnalyzer, ComplexityVisitor
import ast


def test_complexity_visitor():
    """Test the ComplexityVisitor class."""
    print("Testing ComplexityVisitor...")
    
    code = '''
def simple_function():
    return "hello"

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
    
    print(f"Found {len(visitor.complexity_results)} functions")
    
    complexities = {name: complexity for name, complexity, _ in visitor.complexity_results}
    print(f"Complexities: {complexities}")
    
    assert len(visitor.complexity_results) == 2
    assert complexities['complex_function'] > complexities['simple_function']
    print("✓ ComplexityVisitor test passed")


def test_analyzer_creation():
    """Test that the analyzer can be created and basic functionality works."""
    print("Testing CodeQualityAnalyzer creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = AnalysisConfig(project_path=temp_dir)
        analyzer = CodeQualityAnalyzer(config)
        
        assert analyzer.get_analyzer_name() == "Code Quality Analyzer"
        assert isinstance(analyzer.complexity_results, list)
        assert isinstance(analyzer.style_issues, list)
        assert isinstance(analyzer.consistency_issues, list)
        
        print("✓ Analyzer creation test passed")


def test_style_checker():
    """Test the style checker functionality."""
    print("Testing StyleChecker...")
    
    from code_quality_analyzer import StyleChecker
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file with style issues
        test_file = Path(temp_dir) / "test_style.py"
        with open(test_file, 'w') as f:
            f.write("""# Test file with style issues
def function_with_long_line():
    return "This is a very long line that exceeds the recommended 88 character limit and should be flagged by the style checker"

def function_with_trailing_whitespace():   
    return "hello"

def	function_with_tabs():
    return "tabs"

def multiple_statements(): x = 1; y = 2; return x + y
""")
        
        checker = StyleChecker()
        issues = checker.check_file(test_file)
        
        print(f"Found {len(issues)} style issues")
        
        # Check that we found the expected issues
        issue_types = [issue.issue_type for issue in issues]
        print(f"Issue types: {issue_types}")
        
        assert 'line_too_long' in issue_types
        assert 'trailing_whitespace' in issue_types
        assert 'tab_indentation' in issue_types
        assert 'multiple_statements' in issue_types
        
        print("✓ StyleChecker test passed")


def test_full_analysis():
    """Test full analysis on a sample project."""
    print("Testing full analysis...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test Python files
        test_files = {
            "simple.py": """
def simple_function():
    '''A simple function.'''
    return "hello"
""",
            "complex.py": """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(x):
                    for j in range(y):
                        if i * j > z:
                            try:
                                result = x / (i + j)
                                if result > 1:
                                    return result
                                else:
                                    continue
                            except ZeroDivisionError:
                                return 0
                            except ValueError:
                                return -1
    return None
""",
            "style_issues.py": """
def bad_style():
    return "This line is way too long and exceeds the 88 character limit that we have set for our code style guidelines"
    
def trailing_spaces():   
    return "hello"
"""
        }
        
        for filename, content in test_files.items():
            with open(Path(temp_dir) / filename, 'w') as f:
                f.write(content)
        
        # Run analysis
        config = AnalysisConfig(project_path=temp_dir)
        analyzer = CodeQualityAnalyzer(config)
        
        results = analyzer.analyze(temp_dir)
        
        print(f"Analysis found {len(results)} issues")
        
        # Check that we found complexity and style issues
        categories = [result.category for result in results]
        print(f"Categories found: {set(categories)}")
        
        assert len(results) > 0
        assert 'complexity' in categories or 'style' in categories
        
        # Check quality summary
        summary = analyzer.get_quality_summary()
        print(f"Quality summary: {summary}")
        
        assert 'total_complexity_issues' in summary
        assert 'total_style_issues' in summary
        
        print("✓ Full analysis test passed")


def main():
    """Run all tests."""
    print("Running CodeQualityAnalyzer tests...\n")
    
    try:
        test_complexity_visitor()
        print()
        
        test_analyzer_creation()
        print()
        
        test_style_checker()
        print()
        
        test_full_analysis()
        print()
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)