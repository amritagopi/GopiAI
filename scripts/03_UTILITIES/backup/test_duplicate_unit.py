#!/usr/bin/env python3
"""
Unit tests for DuplicateAnalyzer - simplified version
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from project_cleanup_analyzer import AnalysisConfig
from duplicate_analyzer import DuplicateAnalyzer, CodeBlock, FunctionSignature

class TestDuplicateAnalyzerBasic(unittest.TestCase):
    """Basic test cases for DuplicateAnalyzer."""
    
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
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_analyzer_name(self):
        """Test that analyzer returns correct name."""
        self.assertEqual(self.analyzer.get_analyzer_name(), "Duplicate Analyzer")
        print("✓ Analyzer name test passed")
    
    def test_empty_project(self):
        """Test analysis of empty project."""
        results = self.analyzer.analyze(str(self.project_path))
        self.assertEqual(len(results), 0)
        print("✓ Empty project test passed")
    
    def test_exact_duplicates(self):
        """Test detection of exact duplicate functions."""
        content = '''
def test_function():
    """A test function."""
    result = 1 + 2
    return result
'''
        
        self.create_test_file("file1.py", content)
        self.create_test_file("file2.py", content)
        
        results = self.analyzer.analyze(str(self.project_path))
        
        print(f"Found {len(results)} total results")
        for result in results:
            print(f"  - {result.category}: {result.description}")
        
        # Should find duplicates (exact or similar)
        duplicate_results = [r for r in results if "duplicate" in r.category]
        self.assertGreater(len(duplicate_results), 0, f"Expected duplicates but found: {[r.category for r in results]}")
        print("✓ Exact duplicate detection test passed")
    
    def test_code_block_creation(self):
        """Test CodeBlock data class."""
        block = CodeBlock(
            file_path="test.py",
            start_line=1,
            end_line=5,
            code="def test(): pass",
            ast_hash="hash123",
            normalized_code="def test(): pass",
            block_type="function",
            name="test"
        )
        
        self.assertEqual(block.file_path, "test.py")
        self.assertEqual(block.name, "test")
        self.assertEqual(block.block_type, "function")
        print("✓ CodeBlock creation test passed")
    
    def test_function_signature_creation(self):
        """Test FunctionSignature data class."""
        signature = FunctionSignature(
            name="test_func",
            file_path="test.py",
            line_number=1,
            parameters=["param1", "param2"],
            return_annotation="str",
            docstring="Test function",
            body_hash="body123",
            complexity_score=2
        )
        
        self.assertEqual(signature.name, "test_func")
        self.assertEqual(len(signature.parameters), 2)
        self.assertEqual(signature.complexity_score, 2)
        print("✓ FunctionSignature creation test passed")
    
    def test_duplicate_summary(self):
        """Test duplicate summary generation."""
        content = '''
def function1():
    return 1

def function2():
    return 2
'''
        
        self.create_test_file("summary_test.py", content)
        self.analyzer.analyze(str(self.project_path))
        
        summary = self.analyzer.get_duplicate_summary()
        
        self.assertIn('total_code_blocks', summary)
        self.assertIn('total_functions', summary)
        self.assertIn('duplicate_groups', summary)
        print("✓ Duplicate summary test passed")

def run_basic_tests():
    """Run basic tests."""
    print("Running basic DuplicateAnalyzer tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDuplicateAnalyzerBasic)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open('nul', 'w'))  # Suppress unittest output
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("✅ All basic unit tests passed!")
        return True
    else:
        print("❌ Some basic tests failed!")
        for failure in result.failures:
            print(f"FAILURE: {failure[0]}")
            print(f"  {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"  {error[1]}")
        return False

if __name__ == '__main__':
    success = run_basic_tests()
    exit(0 if success else 1)