"""
Test module for the analyzer cache system.

This module contains tests for the AnalyzerCache, IncrementalAnalyzer,
and MemoryMonitor classes.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import time
import ast
from pathlib import Path

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer_cache import AnalyzerCache, IncrementalAnalyzer, MemoryMonitor, FileCacheEntry


class TestAnalyzerCache(unittest.TestCase):
    """Test the AnalyzerCache class."""
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.cache = AnalyzerCache(cache_dir=self.test_dir.name)
        
        # Create some test files
        self.test_file_path = Path(self.test_dir.name) / "test_file.py"
        with open(self.test_file_path, "w") as f:
            f.write("def test_function():\n    pass\n")
    
    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()
    
    def test_file_content_caching(self):
        """Test caching file content."""
        # First read should be a cache miss
        content1, hit1 = self.cache.get_file_content(self.test_file_path)
        self.assertEqual(content1, "def test_function():\n    pass\n")
        self.assertFalse(hit1)
        
        # Second read should be a cache hit
        content2, hit2 = self.cache.get_file_content(self.test_file_path)
        self.assertEqual(content2, "def test_function():\n    pass\n")
        self.assertTrue(hit2)
        
        # Check cache statistics
        self.assertEqual(self.cache.cache_hits, 1)
        self.assertEqual(self.cache.cache_misses, 1)
    
    def test_ast_caching(self):
        """Test caching AST parsing."""
        # First parse should be a cache miss
        ast1, hit1 = self.cache.get_ast(self.test_file_path)
        self.assertIsInstance(ast1, ast.AST)
        self.assertFalse(hit1)
        
        # Second parse should be a cache hit
        ast2, hit2 = self.cache.get_ast(self.test_file_path)
        self.assertIsInstance(ast2, ast.AST)
        self.assertTrue(hit2)
    
    def test_analysis_results_caching(self):
        """Test caching analysis results."""
        # Create test results
        test_results = {
            'issues': [
                {'severity': 'medium', 'message': 'Test issue'}
            ]
        }
        
        # Store results
        self.cache.store_analysis_results("TestAnalyzer", self.test_file_path, test_results)
        
        # Retrieve results
        results, hit = self.cache.get_analysis_results("TestAnalyzer", self.test_file_path)
        self.assertEqual(results, test_results)
        self.assertTrue(hit)
        
        # Try with a different analyzer
        results2, hit2 = self.cache.get_analysis_results("OtherAnalyzer", self.test_file_path)
        self.assertIsNone(results2)
        self.assertFalse(hit2)
    
    def test_cache_cleanup(self):
        """Test cache cleanup when it gets too large."""
        # Set a small max size
        self.cache.max_size_bytes = 100
        
        # Create a large file
        large_file_path = Path(self.test_dir.name) / "large_file.py"
        with open(large_file_path, "w") as f:
            f.write("x" * 200)  # 200 bytes, larger than cache limit
        
        # This should trigger cleanup
        content, hit = self.cache.get_file_content(large_file_path)
        
        # Check that the cache size is reasonable
        self.assertLessEqual(self.cache.cache_size_bytes, self.cache.max_size_bytes * 0.8)
    
    def test_save_and_load_cache(self):
        """Test saving and loading cache to/from disk."""
        # Add some data to the cache
        content, _ = self.cache.get_file_content(self.test_file_path)
        
        # Store some analysis results
        test_results = {'issues': [{'severity': 'medium', 'message': 'Test issue'}]}
        self.cache.store_analysis_results("TestAnalyzer", self.test_file_path, test_results)
        
        # Save cache to disk
        self.assertTrue(self.cache.save_cache_to_disk())
        
        # Create a new cache instance
        new_cache = AnalyzerCache(cache_dir=self.test_dir.name)
        
        # Load cache from disk
        self.assertTrue(new_cache.load_cache_from_disk())
        
        # Check that analysis results were loaded
        results, hit = new_cache.get_analysis_results("TestAnalyzer", self.test_file_path)
        self.assertEqual(results, test_results)
        self.assertTrue(hit)


class TestIncrementalAnalyzer(unittest.TestCase):
    """Test the IncrementalAnalyzer class."""
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.incremental = IncrementalAnalyzer(
            project_path=self.test_dir.name,
            cache_dir=self.test_dir.name
        )
        
        # Create some test files
        self.test_file_path = Path(self.test_dir.name) / "test_file.py"
        with open(self.test_file_path, "w") as f:
            f.write("def test_function():\n    pass\n")
    
    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()
    
    def test_identify_changed_files(self):
        """Test identifying changed files."""
        # First run should identify all files as changed
        files = [self.test_file_path]
        changed = self.incremental.identify_changed_files(files)
        self.assertEqual(len(changed), 1)
        
        # Mark file as analyzed
        self.incremental.mark_file_analyzed(self.test_file_path)
        
        # Second run should not identify any changes
        changed = self.incremental.identify_changed_files(files)
        self.assertEqual(len(changed), 0)
        
        # Modify the file
        time.sleep(0.1)  # Ensure mtime changes
        with open(self.test_file_path, "w") as f:
            f.write("def modified_function():\n    pass\n")
        
        # Should identify the file as changed
        changed = self.incremental.identify_changed_files(files)
        self.assertEqual(len(changed), 1)
    
    def test_save_and_load_state(self):
        """Test saving and loading state to/from disk."""
        # Mark a file as analyzed
        self.incremental.mark_file_analyzed(self.test_file_path)
        
        # Save state
        self.incremental.save_state()
        
        # Create a new incremental analyzer
        new_incremental = IncrementalAnalyzer(
            project_path=self.test_dir.name,
            cache_dir=self.test_dir.name
        )
        
        # Should have loaded the state
        self.assertIn(str(self.test_file_path), new_incremental.analyzed_files)
        
        # Should not identify the file as changed
        changed = new_incremental.identify_changed_files([self.test_file_path])
        self.assertEqual(len(changed), 0)


class TestMemoryMonitor(unittest.TestCase):
    """Test the MemoryMonitor class."""
    
    def setUp(self):
        self.monitor = MemoryMonitor(threshold_percent=90.0)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_check_memory_usage(self, mock_virtual_memory, mock_process):
        """Test checking memory usage."""
        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1000000000  # 1 GB
        
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_instance
        
        # Mock system memory
        mock_virtual_memory_info = MagicMock()
        mock_virtual_memory_info.total = 8000000000  # 8 GB
        mock_virtual_memory.return_value = mock_virtual_memory_info
        
        # Check memory usage
        usage_percent, exceeds_threshold = self.monitor.check_memory_usage()
        
        # Should be 12.5% (1 GB / 8 GB)
        self.assertAlmostEqual(usage_percent, 12.5, places=1)
        self.assertFalse(exceeds_threshold)
        
        # Test exceeding threshold
        self.monitor.threshold_percent = 10.0
        usage_percent, exceeds_threshold = self.monitor.check_memory_usage()
        self.assertTrue(exceeds_threshold)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_get_memory_stats(self, mock_virtual_memory, mock_process):
        """Test getting memory statistics."""
        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1000000000  # 1 GB
        
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_instance
        
        # Mock system memory
        mock_virtual_memory_info = MagicMock()
        mock_virtual_memory_info.total = 8000000000  # 8 GB
        mock_virtual_memory.return_value = mock_virtual_memory_info
        
        # Get memory stats
        stats = self.monitor.get_memory_stats()
        
        self.assertEqual(stats['current_bytes'], 1000000000)
        self.assertEqual(stats['current_mb'], 1000000000 / (1024 * 1024))
        self.assertEqual(stats['system_total_mb'], 8000000000 / (1024 * 1024))


if __name__ == "__main__":
    unittest.main()