"""
File Analyzer - Outdated and Temporary File Detection

This module implements the FileAnalyzer class for detecting temporary files,
outdated files, and duplicate files in the GopiAI project.
"""

import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError


class FileAnalyzer(BaseAnalyzer):
    """Analyzer for detecting temporary, outdated, and duplicate files."""
    
    # Common temporary file patterns
    TEMP_FILE_PATTERNS = [
        '*.tmp', '*.temp', '*.bak', '*.backup', '*.old', '*.orig',
        '*~', '*.swp', '*.swo', '.#*', '#*#', '*.autosave',
        '*.cache', '*.log', '*.pid', '*.lock', 'Thumbs.db',
        '.DS_Store', 'desktop.ini', '*.pyc', '*.pyo', '*.pyd'
    ]
    
    # File extensions that are typically temporary or generated
    TEMP_EXTENSIONS = {
        '.tmp', '.temp', '.bak', '.backup', '.old', '.orig',
        '.swp', '.swo', '.autosave', '.cache', '.log', '.pid', '.lock'
    }
    
    # Files that are commonly outdated if not modified recently
    POTENTIALLY_OUTDATED_EXTENSIONS = {
        '.log', '.cache', '.tmp', '.pid', '.lock', '.bak'
    }
    
    def __init__(self, config):
        super().__init__(config)
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.outdated_threshold_days = 30  # Files older than 30 days might be outdated
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform file analysis to detect temporary, outdated, and duplicate files.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Get all files in the project
            all_files = self._get_all_files(project_root)
            
            # Analyze temporary files
            results.extend(self._analyze_temporary_files(all_files))
            
            # Analyze potentially outdated files
            results.extend(self._analyze_outdated_files(all_files))
            
            # Analyze duplicate files
            results.extend(self._analyze_duplicate_files(all_files))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze files: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "File Analyzer"
    
    def _get_all_files(self, project_root: Path) -> List[Path]:
        """Get all files in the project, respecting exclude patterns and project boundaries."""
        files = []
        
        try:
            # Convert project_root to absolute path for comparison
            project_root_abs = project_root.resolve()
            
            for file_path in project_root.rglob('*'):
                if file_path.is_file():
                    # Ensure file is within project boundaries
                    try:
                        file_path_abs = file_path.resolve()
                        if not str(file_path_abs).startswith(str(project_root_abs)):
                            # Skip files outside project boundaries
                            continue
                    except (OSError, ValueError):
                        # If we can't resolve the path, skip it
                        continue
                    
                    # Check if file should be excluded based on patterns
                    if not self._should_exclude_file(file_path):
                        files.append(file_path)
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to scan files: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return files
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from analysis."""
        # Check against exclude patterns
        for pattern in self.config.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        # Check file size
        try:
            if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                return True
        except OSError:
            return True
        
        return False
    
    def _analyze_temporary_files(self, files: List[Path]) -> List[AnalysisResult]:
        """Analyze files to detect temporary files."""
        results = []
        
        for file_path in files:
            try:
                if self._is_temporary_file(file_path):
                    severity = self._get_temp_file_severity(file_path)
                    results.append(AnalysisResult(
                        category="temporary_files",
                        severity=severity,
                        description=f"Temporary file detected: {file_path.name}",
                        file_path=str(file_path),
                        recommendation=self._get_temp_file_recommendation(file_path)
                    ))
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to analyze temporary file: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _analyze_outdated_files(self, files: List[Path]) -> List[AnalysisResult]:
        """Analyze files to detect potentially outdated files."""
        results = []
        cutoff_date = datetime.now() - timedelta(days=self.outdated_threshold_days)
        
        for file_path in files:
            try:
                if self._is_potentially_outdated(file_path, cutoff_date):
                    file_stat = file_path.stat()
                    last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                    days_old = (datetime.now() - last_modified).days
                    
                    severity = self._get_outdated_file_severity(days_old, file_path)
                    results.append(AnalysisResult(
                        category="outdated_files",
                        severity=severity,
                        description=f"Potentially outdated file (last modified {days_old} days ago): {file_path.name}",
                        file_path=str(file_path),
                        recommendation=self._get_outdated_file_recommendation(file_path, days_old)
                    ))
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to analyze file age: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _analyze_duplicate_files(self, files: List[Path]) -> List[AnalysisResult]:
        """Analyze files to detect content-based duplicates."""
        results = []
        
        # Build hash map of file contents
        self._build_file_hash_map(files)
        
        # Find duplicates
        for file_hash, file_list in self.file_hashes.items():
            if len(file_list) > 1:
                # Found duplicates
                primary_file = min(file_list, key=lambda f: len(str(f)))  # Shortest path as primary
                duplicate_files = [f for f in file_list if f != primary_file]
                
                for duplicate_file in duplicate_files:
                    try:
                        severity = self._get_duplicate_file_severity(duplicate_file, primary_file)
                        results.append(AnalysisResult(
                            category="duplicate_files",
                            severity=severity,
                            description=f"Duplicate file content detected: {duplicate_file.name}",
                            file_path=str(duplicate_file),
                            recommendation=f"Consider removing duplicate. Original file: {primary_file}"
                        ))
                    except Exception as e:
                        error = AnalysisError(
                            analyzer=self.get_analyzer_name(),
                            file_path=str(duplicate_file),
                            error=f"Failed to analyze duplicate file: {str(e)}",
                            original_exception=e
                        )
                        self.error_handler.handle_error(error)
        
        return results
    
    def _is_temporary_file(self, file_path: Path) -> bool:
        """Check if a file appears to be temporary."""
        # Check file extension
        if file_path.suffix.lower() in self.TEMP_EXTENSIONS:
            return True
        
        # Check file name patterns
        file_name = file_path.name
        for pattern in self.TEMP_FILE_PATTERNS:
            if file_path.match(pattern):
                return True
        
        # Check for backup file patterns (ends with ~, .bak, etc.)
        if (file_name.endswith('~') or 
            file_name.startswith('.#') or 
            file_name.startswith('#') and file_name.endswith('#')):
            return True
        
        return False
    
    def _is_potentially_outdated(self, file_path: Path, cutoff_date: datetime) -> bool:
        """Check if a file is potentially outdated."""
        try:
            file_stat = file_path.stat()
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Check if file is older than cutoff date
            if last_modified < cutoff_date:
                # Only flag certain types of files as potentially outdated
                if (file_path.suffix.lower() in self.POTENTIALLY_OUTDATED_EXTENSIONS or
                    self._is_temporary_file(file_path)):
                    return True
            
            return False
        except OSError:
            return False
    
    def _build_file_hash_map(self, files: List[Path]) -> None:
        """Build a hash map of file contents for duplicate detection."""
        self.file_hashes.clear()
        
        for file_path in files:
            try:
                # Skip very large files for performance
                if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    continue
                
                # Skip binary files that are unlikely to be duplicates
                if self._is_binary_file(file_path):
                    continue
                
                file_hash = self._calculate_file_hash(file_path)
                if file_hash:
                    self.file_hashes[file_hash].append(file_path)
                    
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to hash file: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file contents."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary (heuristic)."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return True
    
    def _get_temp_file_severity(self, file_path: Path) -> str:
        """Determine severity level for temporary files."""
        # High severity for files that are definitely temporary
        if (file_path.suffix.lower() in {'.tmp', '.temp', '.lock', '.pid'} or
            file_path.name.endswith('~')):
            return "high"
        
        # Medium severity for backup and cache files
        if file_path.suffix.lower() in {'.bak', '.backup', '.cache', '.old'}:
            return "medium"
        
        # Low severity for other temporary patterns
        return "low"
    
    def _get_outdated_file_severity(self, days_old: int, file_path: Path) -> str:
        """Determine severity level for outdated files."""
        # High severity for very old temporary files
        if days_old > 90 and self._is_temporary_file(file_path):
            return "high"
        
        # Medium severity for moderately old files
        if days_old > 60:
            return "medium"
        
        # Low severity for recently outdated files
        return "low"
    
    def _get_duplicate_file_severity(self, duplicate_file: Path, original_file: Path) -> str:
        """Determine severity level for duplicate files."""
        # High severity if duplicate is in a different module
        if self._files_in_different_modules(duplicate_file, original_file):
            return "high"
        
        # Medium severity for duplicates in same directory
        if duplicate_file.parent == original_file.parent:
            return "medium"
        
        # Low severity for other duplicates
        return "low"
    
    def _files_in_different_modules(self, file1: Path, file2: Path) -> bool:
        """Check if two files are in different GopiAI modules."""
        def get_module_name(file_path: Path) -> str:
            parts = file_path.parts
            for part in parts:
                if part.startswith('GopiAI-'):
                    return part
            return ""
        
        module1 = get_module_name(file1)
        module2 = get_module_name(file2)
        
        return module1 != module2 and module1 != "" and module2 != ""
    
    def _get_temp_file_recommendation(self, file_path: Path) -> str:
        """Get recommendation for temporary files."""
        if file_path.suffix.lower() in {'.tmp', '.temp'}:
            return "Safe to delete - temporary file"
        elif file_path.suffix.lower() in {'.bak', '.backup', '.old'}:
            return "Review before deleting - backup file that might be needed"
        elif file_path.name.endswith('~'):
            return "Safe to delete - editor backup file"
        elif file_path.suffix.lower() in {'.log'}:
            return "Consider archiving or deleting old log files"
        else:
            return "Review file contents before deleting"
    
    def _get_outdated_file_recommendation(self, file_path: Path, days_old: int) -> str:
        """Get recommendation for outdated files."""
        if self._is_temporary_file(file_path):
            return f"Consider deleting - temporary file not modified for {days_old} days"
        else:
            return f"Review if still needed - file not modified for {days_old} days"


if __name__ == "__main__":
    # Simple test of the FileAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = FileAnalyzer(config)
        
        print(f"Testing {analyzer.get_analyzer_name()}...")
        results = analyzer.analyze(project_path)
        
        print(f"Analysis complete. Found {len(results)} results:")
        
        # Group results by category
        by_category = defaultdict(list)
        for result in results:
            by_category[result.category].append(result)
        
        for category, category_results in by_category.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for result in category_results[:5]:  # Show first 5 results
                print(f"  - {result.severity.upper()}: {result.description}")
            if len(category_results) > 5:
                print(f"  ... and {len(category_results) - 5} more")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)
