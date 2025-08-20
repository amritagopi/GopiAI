"""
Unit tests for FileAnalyzer

Tests the functionality of the FileAnalyzer class for detecting temporary files,
outdated files, and duplicate files.
"""

import pytest
import tempfile
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from file_analyzer import FileAnalyzer


class TestFileAnalyzer:
    """Test suite for FileAnalyzer class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self, temp_project_dir):
        """Create a test configuration."""
        return AnalysisConfig(
            project_path=str(temp_project_dir),
            exclude_patterns=['*.pyc', '__pycache__'],
            severity_threshold='low'
        )
    
    @pytest.fixture
    def analyzer(self, config):
        """Create a FileAnalyzer instance for testing."""
        return FileAnalyzer(config)
    
    def test_analyzer_initialization(self, analyzer):
        """Test that FileAnalyzer initializes correctly."""
        assert analyzer.get_analyzer_name() == "File Analyzer"
        assert analyzer.outdated_threshold_days == 30
        assert isinstance(analyzer.file_hashes, dict)
    
    def test_temporary_file_detection(self, analyzer, temp_project_dir):
        """Test detection of temporary files."""
        # Create various temporary files
        temp_files = [
            temp_project_dir / "test.tmp",
            temp_project_dir / "backup.bak",
            temp_project_dir / "file~",
            temp_project_dir / "document.old",
            temp_project_dir / ".#lockfile",
            temp_project_dir / "#autosave#",
            temp_project_dir / "cache.cache",
            temp_project_dir / "app.log"
        ]
        
        # Create the files
        for temp_file in temp_files:
            temp_file.write_text("temporary content")
        
        # Also create a normal file
        normal_file = temp_project_dir / "normal.py"
        normal_file.write_text("print('hello')")
        
        # Run analysis
        results = analyzer.analyze(str(temp_project_dir))
        
        # Filter for temporary file results
        temp_results = [r for r in results if r.category == "temporary_files"]
        
        # Should detect all temporary files but not the normal file
        assert len(temp_results) == len(temp_files)
        
        # Check that all temporary files were detected
        detected_files = {Path(r.file_path).name for r in temp_results}
        expected_files = {f.name for f in temp_files}
        assert detected_files == expected_files
    
    def test_temporary_file_severity_levels(self, analyzer, temp_project_dir):
        """Test that temporary files get appropriate severity levels."""
        # High severity files
        high_severity_files = [
            temp_project_dir / "test.tmp",
            temp_project_dir / "app.lock",
            temp_project_dir / "process.pid",
            temp_project_dir / "file~"
        ]
        
        # Medium severity files
        medium_severity_files = [
            temp_project_dir / "backup.bak",
            temp_project_dir / "old.backup",
            temp_project_dir / "data.cache",
            temp_project_dir / "version.old"
        ]
        
        # Create all files
        for file_path in high_severity_files + medium_severity_files:
            file_path.write_text("content")
        
        results = analyzer.analyze(str(temp_project_dir))
        temp_results = [r for r in results if r.category == "temporary_files"]
        
        # Check severity levels
        high_results = [r for r in temp_results if r.severity == "high"]
        medium_results = [r for r in temp_results if r.severity == "medium"]
        
        assert len(high_results) == len(high_severity_files)
        assert len(medium_results) == len(medium_severity_files)
    
    def test_outdated_file_detection(self, analyzer, temp_project_dir):
        """Test detection of outdated files using real file timestamps."""
        import os
        import time
        
        # Create files with different ages
        old_temp_file = temp_project_dir / "old.tmp"
        old_log_file = temp_project_dir / "old.log"
        recent_file = temp_project_dir / "recent.py"
        
        # Create the files
        old_temp_file.write_text("old temporary content")
        old_log_file.write_text("old log content")
        recent_file.write_text("recent content")
        
        # Modify timestamps to make files appear old
        old_time = time.time() - (45 * 24 * 60 * 60)  # 45 days ago
        recent_time = time.time() - (5 * 24 * 60 * 60)  # 5 days ago
        
        os.utime(old_temp_file, (old_time, old_time))
        os.utime(old_log_file, (old_time, old_time))
        os.utime(recent_file, (recent_time, recent_time))
        
        # Run analysis
        results = analyzer.analyze(str(temp_project_dir))
        outdated_results = [r for r in results if r.category == "outdated_files"]
        
        # Should detect the old temporary and log files
        assert len(outdated_results) >= 2
        detected_files = {Path(r.file_path).name for r in outdated_results}
        assert "old.tmp" in detected_files
        assert "old.log" in detected_files
    
    def test_outdated_file_integration(self, analyzer, temp_project_dir):
        """Integration test for outdated file detection using real files."""
        import os
        import time
        
        # Create a temporary file
        old_temp_file = temp_project_dir / "old.tmp"
        old_temp_file.write_text("old temporary content")
        
        # Modify the file's timestamp to make it appear old
        old_time = time.time() - (45 * 24 * 60 * 60)  # 45 days ago
        os.utime(old_temp_file, (old_time, old_time))
        
        # Run analysis
        results = analyzer.analyze(str(temp_project_dir))
        outdated_results = [r for r in results if r.category == "outdated_files"]
        
        # Should detect the old temporary file
        assert len(outdated_results) >= 1
        detected_files = {Path(r.file_path).name for r in outdated_results}
        assert "old.tmp" in detected_files
    
    def test_duplicate_file_detection(self, analyzer, temp_project_dir):
        """Test detection of duplicate files."""
        # Create files with identical content
        content = "This is identical content for testing duplicates"
        
        file1 = temp_project_dir / "file1.txt"
        file2 = temp_project_dir / "file2.txt"
        file3 = temp_project_dir / "unique.txt"
        
        file1.write_text(content)
        file2.write_text(content)
        file3.write_text("This is unique content")
        
        # Create subdirectory with another duplicate
        subdir = temp_project_dir / "subdir"
        subdir.mkdir()
        file4 = subdir / "file4.txt"
        file4.write_text(content)
        
        results = analyzer.analyze(str(temp_project_dir))
        duplicate_results = [r for r in results if r.category == "duplicate_files"]
        
        # Should detect 2 duplicates (file2.txt and file4.txt, with file1.txt as primary)
        assert len(duplicate_results) == 2
        
        # Check that the duplicates are correctly identified
        detected_files = {Path(r.file_path).name for r in duplicate_results}
        assert "file1.txt" not in detected_files  # Primary file shouldn't be in duplicates
        assert "file2.txt" in detected_files or "file4.txt" in detected_files
    
    def test_binary_file_exclusion(self, analyzer, temp_project_dir):
        """Test that binary files are excluded from duplicate detection."""
        # Create a binary file (with null bytes)
        binary_file = temp_project_dir / "binary.dat"
        binary_file.write_bytes(b"binary\x00content\x00here")
        
        # Create a text file
        text_file = temp_project_dir / "text.txt"
        text_file.write_text("text content here")
        
        # Mock the _is_binary_file method to test the logic
        with patch.object(analyzer, '_is_binary_file') as mock_is_binary:
            mock_is_binary.side_effect = lambda path: path.name == "binary.dat"
            
            # Build hash map
            analyzer._build_file_hash_map([binary_file, text_file])
            
            # Binary file should not be in hash map
            assert len(analyzer.file_hashes) <= 1  # Only text file should be hashed
    
    def test_large_file_exclusion(self, analyzer, temp_project_dir):
        """Test that large files are excluded from analysis."""
        # Create a file
        test_file = temp_project_dir / "test.txt"
        test_file.write_text("test content")
        
        # Mock file size to be very large
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat_result = MagicMock()
            mock_stat_result.st_size = 20 * 1024 * 1024  # 20MB
            mock_stat_result.st_mtime = datetime.now().timestamp()
            mock_stat.return_value = mock_stat_result
            
            # Should exclude the file from analysis
            assert analyzer._should_exclude_file(test_file) == True
    
    def test_file_hash_calculation(self, analyzer, temp_project_dir):
        """Test file hash calculation."""
        test_file = temp_project_dir / "test.txt"
        content = "test content for hashing"
        test_file.write_text(content)
        
        # Calculate hash
        file_hash = analyzer._calculate_file_hash(test_file)
        
        # Verify hash is correct
        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        assert file_hash == expected_hash
    
    def test_module_detection(self, analyzer, temp_project_dir):
        """Test detection of files in different GopiAI modules."""
        # Create GopiAI module directories
        module1_dir = temp_project_dir / "GopiAI-Core"
        module2_dir = temp_project_dir / "GopiAI-UI"
        module1_dir.mkdir()
        module2_dir.mkdir()
        
        file1 = module1_dir / "test.py"
        file2 = module2_dir / "test.py"
        
        # Test module detection
        assert analyzer._files_in_different_modules(file1, file2) == True
        assert analyzer._files_in_different_modules(file1, module1_dir / "other.py") == False
    
    def test_error_handling(self, analyzer, temp_project_dir):
        """Test error handling during analysis."""
        # Create a file that will cause an error
        test_file = temp_project_dir / "test.txt"
        test_file.write_text("test content")
        
        # Mock file operations to raise exceptions
        with patch('pathlib.Path.stat', side_effect=OSError("Permission denied")):
            results = analyzer.analyze(str(temp_project_dir))
            
            # Analysis should continue despite errors
            assert isinstance(results, list)
            assert analyzer.error_handler.has_errors()
    
    def test_recommendations(self, analyzer, temp_project_dir):
        """Test that appropriate recommendations are provided."""
        # Create different types of files
        tmp_file = temp_project_dir / "test.tmp"
        bak_file = temp_project_dir / "backup.bak"
        log_file = temp_project_dir / "app.log"
        
        tmp_file.write_text("temp")
        bak_file.write_text("backup")
        log_file.write_text("log")
        
        results = analyzer.analyze(str(temp_project_dir))
        temp_results = [r for r in results if r.category == "temporary_files"]
        
        # Check that recommendations are provided
        for result in temp_results:
            assert result.recommendation != ""
            assert isinstance(result.recommendation, str)
    
    def test_severity_filtering(self, analyzer, temp_project_dir):
        """Test that severity filtering works correctly."""
        # Create files with different severity levels
        high_file = temp_project_dir / "test.tmp"  # High severity
        medium_file = temp_project_dir / "backup.bak"  # Medium severity
        
        high_file.write_text("temp")
        medium_file.write_text("backup")
        
        # Test with high severity threshold
        analyzer.config.severity_threshold = "high"
        results = analyzer.analyze(str(temp_project_dir))
        temp_results = [r for r in results if r.category == "temporary_files"]
        
        # Should only include high severity results
        assert all(r.severity == "high" for r in temp_results)
    
    def test_empty_project(self, analyzer, temp_project_dir):
        """Test analysis of empty project directory."""
        results = analyzer.analyze(str(temp_project_dir))
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_nonexistent_directory(self, config):
        """Test handling of nonexistent project directory."""
        # Create a new config with nonexistent path to avoid validation error
        from project_cleanup_analyzer import AnalysisConfig
        
        # Temporarily patch Path.exists to allow creating config
        with patch('pathlib.Path.exists', return_value=True):
            config = AnalysisConfig(
                project_path="/nonexistent/directory",
                exclude_patterns=['*.pyc', '__pycache__'],
                severity_threshold='low'
            )
        
        analyzer = FileAnalyzer(config)
        
        results = analyzer.analyze(config.project_path)
        assert isinstance(results, list)
        # The analyzer should handle the nonexistent directory gracefully
        # and may or may not report errors depending on implementation


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])