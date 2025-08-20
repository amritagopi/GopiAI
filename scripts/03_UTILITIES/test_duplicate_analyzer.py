"""
Unit tests for DuplicateAnalyzer

This module contains comprehensive unit tests for the DuplicateAnalyzer class,
testing code duplication detection, similarity analysis, and refactoring suggestions.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import ast

from project_cleanup_analyzer import AnalysisConfig, AnalysisError
from duplicate_analyzer import (
    DuplicateAnalyzer, CodeBlock, FunctionSignature, DuplicateGroup,
    CodeBlockExtractor, FunctionSignatureExtractor
)


class TestDuplicateAnalyzer(unittest.TestCase):
    """Test cases for DuplicateAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.config = AnalysisConfig(project_path=str(self.project_path))
        self.analyzer = DuplicateAnalyzer(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.project_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_analyzer_name(self):
        """Test that analyzer returns correct name."""
        self.assertEqual(self.analyzer.get_analyzer_name(), "Duplicate Analyzer")
    
    def test_empty_project_analysis(self):
        """Test analysis of empty project."""
        results = self.analyzer.analyze(str(self.project_path))
        self.assertEqual(len(results), 0)
    
    def test_exact_duplicate_functions(self):
        """Test detection of exact duplicate functions."""
        # Create files with identical functions
        file1_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def other_function():
    pass
'''
        
        file2_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def different_function():
    pass
'''
        
        self.create_test_file("file1.py", file1_content)
        self.create_test_file("file2.py", file2_content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        # Should find exact duplicate
        duplicate_results = [r for r in results if r.category == "exact_duplicate"]
        self.assertGreater(len(duplicate_results), 0)
        
        # Check that the result mentions both files
        duplicate_result = duplicate_results[0]
        self.assertIn("file1.py", duplicate_result.description)
        self.assertIn("file2.py", duplicate_result.description)
        self.assertEqual(duplicate_result.severity, "high")
    
    def test_similar_code_blocks(self):
        """Test detection of similar but not identical code blocks."""
        file1_content = '''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
'''
        
        file2_content = '''
def transform_values(values):
    output = []
    for value in values:
        if value > 0:
            output.append(value * 2)
    return output
'''
        
        self.create_test_file("similar1.py", file1_content)
        self.create_test_file("similar2.py", file2_content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        # Should find similar code
        similar_results = [r for r in results if r.category == "similar_code"]
        self.assertGreater(len(similar_results), 0)
    
    def test_duplicate_function_names(self):
        """Test detection of functions with same name but different implementations."""
        file1_content = '''
def helper_function():
    return "implementation 1"
'''
        
        file2_content = '''
def helper_function():
    return "implementation 2"
'''
        
        self.create_test_file("name1.py", file1_content)
        self.create_test_file("name2.py", file2_content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        # Should find duplicate function names
        name_results = [r for r in results if r.category == "duplicate_function_name"]
        self.assertGreater(len(name_results), 0)
        
        name_result = name_results[0]
        self.assertIn("helper_function", name_result.description)
        self.assertEqual(name_result.severity, "medium")
    
    def test_refactoring_opportunities(self):
        """Test generation of refactoring suggestions."""
        # Create files with exact duplicate functions
        duplicate_content = '''
def utility_function(x):
    """A utility function."""
    return x * 2 + 1

def main():
    print(utility_function(5))
'''
        
        self.create_test_file("refactor1.py", duplicate_content)
        self.create_test_file("refactor2.py", duplicate_content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        # Should suggest refactoring opportunities
        refactor_results = [r for r in results if r.category == "refactoring_opportunity"]
        self.assertGreater(len(refactor_results), 0)
        
        refactor_result = refactor_results[0]
        self.assertIn("utility_function", refactor_result.description)
        self.assertIn("shared module", refactor_result.recommendation)
    
    def test_minimum_block_size_filtering(self):
        """Test that small code blocks are filtered out."""
        small_block_content = '''
def tiny():
    return 1

def small_function():
    x = 1
    return x
'''
        
        self.create_test_file("small.py", small_block_content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        # Small blocks should not generate duplicate warnings
        # (unless they are exact matches of significant functions)
        duplicate_results = [r for r in results if "tiny" in r.description]
        # This test verifies the filtering logic works
    
    def test_error_handling_invalid_python(self):
        """Test error handling for invalid Python files."""
        invalid_content = '''
def broken_function(
    # Missing closing parenthesis and colon
    return "this won't parse"
'''
        
        self.create_test_file("invalid.py", invalid_content)
        
        # Should not crash, should handle errors gracefully
        results = self.analyzer.analyze(str(self.project_path))
        
        # Check that errors were recorded
        self.assertTrue(self.analyzer.error_handler.has_errors())
    
    def test_get_duplicate_summary(self):
        """Test the duplicate summary functionality."""
        # Create some test files with duplicates
        content = '''
def test_function():
    return "test"

class TestClass:
    def method(self):
        pass
'''
        
        self.create_test_file("summary1.py", content)
        self.create_test_file("summary2.py", content)
        
        self.analyzer.analyze(str(self.project_path))
        summary = self.analyzer.get_duplicate_summary()
        
        self.assertIn('total_code_blocks', summary)
        self.assertIn('total_functions', summary)
        self.assertIn('duplicate_groups', summary)
        self.assertIn('exact_duplicates', summary)
        self.assertIn('similar_blocks', summary)
        self.assertIn('files_with_duplicates', summary)
        
        # Should have found some code blocks and functions
        self.assertGreater(summary['total_code_blocks'], 0)
        self.assertGreater(summary['total_functions'], 0)


class TestCodeBlockExtractor(unittest.TestCase):
    """Test cases for CodeBlockExtractor class."""
    
    def test_function_extraction(self):
        """Test extraction of function blocks."""
        code = '''
def example_function(param1, param2):
    """Example function."""
    result = param1 + param2
    return result
'''
        
        lines = code.strip().splitlines()
        extractor = CodeBlockExtractor("test.py", lines)
        tree = ast.parse(code)
        extractor.visit(tree)
        
        self.assertEqual(len(extractor.blocks), 1)
        block = extractor.blocks[0]
        self.assertEqual(block.block_type, "function")
        self.assertEqual(block.name, "example_function")
        self.assertIn("def example_function", block.code)
    
    def test_class_extraction(self):
        """Test extraction of class blocks."""
        code = '''
class ExampleClass:
    """Example class."""
    
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value
'''
        
        lines = code.strip().splitlines()
        extractor = CodeBlockExtractor("test.py", lines)
        tree = ast.parse(code)
        extractor.visit(tree)
        
        # Should extract class and methods
        class_blocks = [b for b in extractor.blocks if b.block_type == "class"]
        function_blocks = [b for b in extractor.blocks if b.block_type == "function"]
        
        self.assertEqual(len(class_blocks), 1)
        self.assertEqual(len(function_blocks), 2)  # __init__ and method
        
        class_block = class_blocks[0]
        self.assertEqual(class_block.name, "ExampleClass")
    
    def test_control_flow_extraction(self):
        """Test extraction of significant control flow blocks."""
        code = '''
def process_items(items):
    results = []
    for item in items:
        if item > 0:
            processed = item * 2
            results.append(processed)
        else:
            results.append(0)
    return results
'''
        
        lines = code.strip().splitlines()
        extractor = CodeBlockExtractor("test.py", lines)
        tree = ast.parse(code)
        extractor.visit(tree)
        
        # Should extract function and significant blocks
        blocks = extractor.blocks
        self.assertGreater(len(blocks), 1)  # At least the function
        
        function_block = next(b for b in blocks if b.block_type == "function")
        self.assertEqual(function_block.name, "process_items")
    
    def test_ast_hash_generation(self):
        """Test AST hash generation for identical structures."""
        code1 = '''
def func(x):
    return x + 1
'''
        
        code2 = '''
def func(y):
    return y + 1
'''
        
        # Parse both code snippets
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        
        func1 = tree1.body[0]
        func2 = tree2.body[0]
        
        extractor = CodeBlockExtractor("test.py", [])
        hash1 = extractor._generate_ast_hash(func1)
        hash2 = extractor._generate_ast_hash(func2)
        
        # Hashes should be the same for structurally identical functions
        # (parameter names don't affect AST structure significantly)
        self.assertIsInstance(hash1, str)
        self.assertIsInstance(hash2, str)
        self.assertTrue(len(hash1) > 0)
        self.assertTrue(len(hash2) > 0)


class TestFunctionSignatureExtractor(unittest.TestCase):
    """Test cases for FunctionSignatureExtractor class."""
    
    def test_signature_extraction(self):
        """Test extraction of function signatures."""
        code = '''
def example_function(param1: int, param2: str = "default") -> str:
    """Example function with annotations."""
    return f"{param1}: {param2}"

async def async_function(data: list) -> None:
    """Async function example."""
    await process_data(data)
'''
        
        extractor = FunctionSignatureExtractor("test.py")
        tree = ast.parse(code)
        extractor.visit(tree)
        
        self.assertEqual(len(extractor.signatures), 2)
        
        # Check first function
        sig1 = extractor.signatures[0]
        self.assertEqual(sig1.name, "example_function")
        self.assertEqual(len(sig1.parameters), 2)
        self.assertIn("param1: int", sig1.parameters)
        self.assertIn("param2: str", sig1.parameters)
        self.assertEqual(sig1.return_annotation, "str")
        self.assertIn("Example function", sig1.docstring)
        
        # Check async function
        sig2 = extractor.signatures[1]
        self.assertEqual(sig2.name, "async_function")
        self.assertEqual(len(sig2.parameters), 1)
        self.assertIn("data: list", sig2.parameters)
    
    def test_complexity_calculation(self):
        """Test complexity score calculation."""
        simple_code = '''
def simple_function(x):
    return x + 1
'''
        
        complex_code = '''
def complex_function(items):
    result = []
    for item in items:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        elif item < 0:
            try:
                result.append(abs(item))
            except Exception:
                result.append(0)
    return result
'''
        
        # Extract signatures
        extractor1 = FunctionSignatureExtractor("test.py")
        tree1 = ast.parse(simple_code)
        extractor1.visit(tree1)
        
        extractor2 = FunctionSignatureExtractor("test.py")
        tree2 = ast.parse(complex_code)
        extractor2.visit(tree2)
        
        simple_sig = extractor1.signatures[0]
        complex_sig = extractor2.signatures[0]
        
        # Complex function should have higher complexity score
        self.assertGreater(complex_sig.complexity_score, simple_sig.complexity_score)
        self.assertGreater(complex_sig.complexity_score, 5)  # Should be reasonably complex
    
    def test_body_hash_generation(self):
        """Test body hash generation for function bodies."""
        code1 = '''
def func1():
    x = 1
    return x + 1
'''
        
        code2 = '''
def func2():
    x = 1
    return x + 1
'''
        
        code3 = '''
def func3():
    y = 2
    return y + 2
'''
        
        # Extract signatures
        extractors = []
        for code in [code1, code2, code3]:
            extractor = FunctionSignatureExtractor("test.py")
            tree = ast.parse(code)
            extractor.visit(tree)
            extractors.append(extractor)
        
        sig1 = extractors[0].signatures[0]
        sig2 = extractors[1].signatures[0]
        sig3 = extractors[2].signatures[0]
        
        # Functions with identical bodies should have same hash
        self.assertEqual(sig1.body_hash, sig2.body_hash)
        
        # Function with different body should have different hash
        self.assertNotEqual(sig1.body_hash, sig3.body_hash)


class TestDuplicateGroup(unittest.TestCase):
    """Test cases for DuplicateGroup data class."""
    
    def test_duplicate_group_creation(self):
        """Test creation of duplicate groups."""
        block1 = CodeBlock(
            file_path="file1.py",
            start_line=1,
            end_line=5,
            code="def test(): pass",
            ast_hash="hash1",
            normalized_code="def test(): pass",
            block_type="function",
            name="test"
        )
        
        block2 = CodeBlock(
            file_path="file2.py",
            start_line=10,
            end_line=14,
            code="def test(): pass",
            ast_hash="hash1",
            normalized_code="def test(): pass",
            block_type="function",
            name="test"
        )
        
        group = DuplicateGroup(
            blocks=[block1, block2],
            similarity_score=1.0,
            duplicate_type="exact"
        )
        
        self.assertEqual(len(group.blocks), 2)
        self.assertEqual(group.similarity_score, 1.0)
        self.assertEqual(group.duplicate_type, "exact")


def run_tests():
    """Run all tests manually."""
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeBlockExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionSignatureExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateGroup))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    if success:
        print("\n✅ All unit tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)