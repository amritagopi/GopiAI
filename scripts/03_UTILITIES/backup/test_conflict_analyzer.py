"""
Unit Tests for ConflictAnalyzer

This module contains comprehensive unit tests for the ConflictAnalyzer class,
testing global variable analysis, threading issue detection, resource management
analysis, and exception handling detection.
"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from conflict_analyzer import (
    ConflictAnalyzer, GlobalVariableUsage, ThreadingIssue, 
    ResourceIssue, ExceptionIssue, GlobalVariableAnalyzer,
    ThreadingAnalyzer, ResourceAnalyzer, ExceptionAnalyzer
)


class TestConflictAnalyzer(unittest.TestCase):
    """Test cases for ConflictAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalysisConfig(project_path=self.temp_dir)
        self.analyzer = ConflictAnalyzer(self.config)
    
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
        self.assertEqual(self.analyzer.get_analyzer_name(), "Conflict Analyzer")
    
    def test_global_variable_detection(self):
        """Test detection of global variable usage."""
        test_code = '''
global_var = "test"

def function1():
    global global_var
    global_var = "modified"
    return global_var

def function2():
    global global_var
    print(global_var)
'''
        self.create_test_file("test_global.py", test_code)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect global variable conflicts
        global_results = [r for r in results if r.category.startswith('global_variable')]
        self.assertGreater(len(global_results), 0)
    
    def test_threading_issue_detection(self):
        """Test detection of threading issues."""
        test_code = '''
import threading
import time

shared_data = []

def worker():
    global shared_data
    shared_data.append(time.time())

def main():
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
'''
        self.create_test_file("test_threading.py", test_code)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect threading issues
        threading_results = [r for r in results if r.category == 'threading_issue']
        self.assertGreater(len(threading_results), 0)
    
    def test_resource_leak_detection(self):
        """Test detection of resource management issues."""
        test_code = '''
def bad_file_handling():
    f = open("test.txt", "w")
    f.write("test")
    # Missing f.close()

def good_file_handling():
    with open("test.txt", "w") as f:
        f.write("test")

def connection_leak():
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 8080))
    # Missing sock.close()
'''
        self.create_test_file("test_resources.py", test_code)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect resource leaks
        resource_results = [r for r in results if r.category == 'resource_leak']
        self.assertGreater(len(resource_results), 0)
    
    def test_exception_handling_detection(self):
        """Test detection of unhandled exceptions."""
        test_code = '''
def risky_function():
    # This could raise ValueError
    value = int("not_a_number")
    return value

def safe_function():
    try:
        value = int("not_a_number")
        return value
    except ValueError:
        return 0

def file_operation():
    # This could raise FileNotFoundError
    with open("nonexistent.txt") as f:
        return f.read()
'''
        self.create_test_file("test_exceptions.py", test_code)
        
        results = self.analyzer.analyze(self.temp_dir)
        
        # Should detect unhandled exceptions
        exception_results = [r for r in results if r.category == 'unhandled_exception']
        self.assertGreater(len(exception_results), 0)
    
    def test_conflict_summary(self):
        """Test conflict analysis summary."""
        # Create files with various issues
        self.create_test_file("global_test.py", '''
global_var = "test"
def func():
    global global_var
    global_var = "changed"
''')
        
        self.create_test_file("thread_test.py", '''
import threading
def worker():
    pass
t = threading.Thread(target=worker)
t.start()
''')
        
        results = self.analyzer.analyze(self.temp_dir)
        summary = self.analyzer.get_conflict_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('global_variables', summary)
        self.assertIn('threading_issues', summary)
        self.assertIn('resource_issues', summary)
        self.assertIn('exception_issues', summary)
        self.assertIn('files_with_conflicts', summary)
    
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


class TestGlobalVariableAnalyzer(unittest.TestCase):
    """Test cases for GlobalVariableAnalyzer."""
    
    def test_global_declaration_detection(self):
        """Test detection of global declarations."""
        analyzer = GlobalVariableAnalyzer("test.py")
        
        import ast
        code = '''
def function():
    global test_var
    test_var = "value"
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        self.assertIn("test_var", analyzer.global_declarations)
        self.assertGreater(len(analyzer.global_usages), 0)
    
    def test_context_tracking(self):
        """Test context tracking in global variable analysis."""
        analyzer = GlobalVariableAnalyzer("test.py")
        
        import ast
        code = '''
class TestClass:
    def method(self):
        global test_var
        test_var = "value"

def function():
    global test_var
    print(test_var)
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should track different contexts
        contexts = set(usage.context for usage in analyzer.global_usages)
        self.assertGreater(len(contexts), 1)


class TestThreadingAnalyzer(unittest.TestCase):
    """Test cases for ThreadingAnalyzer."""
    
    def test_threading_import_detection(self):
        """Test detection of threading imports."""
        analyzer = ThreadingAnalyzer("test.py")
        
        import ast
        code = '''
import threading
from concurrent.futures import ThreadPoolExecutor
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        self.assertTrue(analyzer.has_threading_imports)
    
    def test_threading_call_detection(self):
        """Test detection of threading-related calls."""
        analyzer = ThreadingAnalyzer("test.py")
        
        import ast
        code = '''
import threading

def worker():
    pass

t = threading.Thread(target=worker)
t.start()
lock = threading.Lock()
lock.acquire()
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        self.assertGreater(len(analyzer.threading_issues), 0)


class TestResourceAnalyzer(unittest.TestCase):
    """Test cases for ResourceAnalyzer."""
    
    def test_file_resource_detection(self):
        """Test detection of file resource usage."""
        lines = [
            "def test():",
            "    f = open('test.txt')",
            "    data = f.read()",
            "    # Missing f.close()"
        ]
        analyzer = ResourceAnalyzer("test.py", lines)
        
        import ast
        code = '\n'.join(lines)
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        file_issues = [issue for issue in analyzer.resource_issues if issue.resource_type == 'file']
        self.assertGreater(len(file_issues), 0)
    
    def test_with_statement_detection(self):
        """Test detection of proper with statement usage."""
        lines = [
            "def test():",
            "    with open('test.txt') as f:",
            "        data = f.read()"
        ]
        analyzer = ResourceAnalyzer("test.py", lines)
        
        import ast
        code = '\n'.join(lines)
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        self.assertGreater(len(analyzer.with_statements), 0)


class TestExceptionAnalyzer(unittest.TestCase):
    """Test cases for ExceptionAnalyzer."""
    
    def test_try_block_detection(self):
        """Test detection of try blocks."""
        analyzer = ExceptionAnalyzer("test.py")
        
        import ast
        code = '''
try:
    risky_operation()
except Exception:
    handle_error()
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        self.assertGreater(len(analyzer.try_blocks), 0)
    
    def test_risky_call_detection(self):
        """Test detection of risky function calls."""
        analyzer = ExceptionAnalyzer("test.py")
        
        import ast
        code = '''
def test():
    value = int("123")  # Could raise ValueError
    data = open("file.txt")  # Could raise FileNotFoundError
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should detect risky calls
        unhandled_issues = [issue for issue in analyzer.exception_issues if not issue.is_handled]
        self.assertGreater(len(unhandled_issues), 0)
    
    def test_context_tracking(self):
        """Test context tracking in exception analysis."""
        analyzer = ExceptionAnalyzer("test.py")
        
        import ast
        code = '''
class TestClass:
    def method(self):
        raise ValueError("test")

def function():
    raise RuntimeError("test")
'''
        tree = ast.parse(code)
        analyzer.visit(tree)
        
        # Should track different contexts
        contexts = set(issue.context for issue in analyzer.exception_issues)
        self.assertGreater(len(contexts), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for ConflictAnalyzer."""
    
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
        """Test comprehensive analysis with multiple issue types."""
        # Create a complex test file with multiple issues
        complex_code = '''
import threading
import time

# Global variable used across functions
shared_counter = 0
config_data = {}

def worker_thread():
    global shared_counter
    # Race condition: multiple threads modifying shared state
    shared_counter += 1
    
    # Resource leak: file not properly closed
    f = open("log.txt", "a")
    f.write(f"Worker {shared_counter}\\n")
    # Missing f.close()
    
    # Unhandled exception risk
    value = int(input("Enter number: "))
    
    return value

def main():
    global config_data
    
    # Threading without proper synchronization
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker_thread)
        t.start()
        threads.append(t)
    
    # Lock acquired but not in with statement
    lock = threading.Lock()
    lock.acquire()
    try:
        config_data["status"] = "running"
    finally:
        lock.release()
    
    for t in threads:
        t.join()

def risky_operation():
    # Multiple unhandled exceptions
    data = open("config.json").read()  # FileNotFoundError
    config = json.loads(data)  # JSONDecodeError
    return config["key"]  # KeyError

if __name__ == "__main__":
    main()
'''
        
        self.create_test_file("complex_issues.py", complex_code)
        
        analyzer = ConflictAnalyzer(self.config)
        results = analyzer.analyze(self.temp_dir)
        
        # Should detect multiple types of issues
        categories = set(result.category for result in results)
        
        # Verify we found different types of issues
        self.assertGreater(len(results), 0)
        self.assertGreater(len(categories), 1)
        
        # Check summary
        summary = analyzer.get_conflict_summary()
        self.assertGreater(summary['files_with_conflicts'], 0)
    
    def test_severity_filtering(self):
        """Test severity-based filtering of results."""
        test_code = '''
global_var = "test"

def function():
    global global_var
    global_var = "modified"
'''
        self.create_test_file("severity_test.py", test_code)
        
        # Test with different severity thresholds
        for threshold in ['low', 'medium', 'high']:
            config = AnalysisConfig(project_path=self.temp_dir, severity_threshold=threshold)
            analyzer = ConflictAnalyzer(config)
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