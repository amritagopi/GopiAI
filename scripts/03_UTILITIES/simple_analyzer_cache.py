"""
Simple Analyzer Cache - Performance Optimizations for Project Cleanup

This module implements a simplified caching mechanism to improve performance of the project cleanup
analyzers, without dependencies on the ast module.
"""

import os
import hashlib
import pickle
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set, Tuple, List
from dataclasses import dataclass, field


@dataclass
class FileCacheEntry:
    """Cache entry for a file's content and metadata."""
    content: str
    hash: str
    mtime: float
    size: int
    last_accessed: float = field(default_factory=time.time)


class AnalyzerCache:
    """Cache for file content and analysis results."""
    
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: float = 100.0):
        """
        Initialize the analyzer cache.
        
        Args:
            cache_dir: Directory to store cache files (default: .cache)
            max_size_mb: Maximum cache size in MB (default: 100)
        """
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '.cache')
        self.max_size_mb = max_size_mb
        self.file_cache: Dict[str, FileCacheEntry] = {}
        self.analysis_cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get file content from cache or read from disk.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content or None if file cannot be read
        """
        # Check if file exists
        if not os.path.isfile(file_path):
            return None
        
        # Get file metadata
        try:
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            size = stat.st_size
        except OSError:
            return None
        
        # Check if file is in cache and up to date
        if file_path in self.file_cache:
            cache_entry = self.file_cache[file_path]
            if cache_entry.mtime == mtime and cache_entry.size == size:
                # Update last accessed time
                cache_entry.last_accessed = time.time()
                self.hits += 1
                return cache_entry.content
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None
        
        # Calculate hash
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Create cache entry
        self.file_cache[file_path] = FileCacheEntry(
            content=content,
            hash=file_hash,
            mtime=mtime,
            size=size
        )
        
        self.misses += 1
        
        # Check cache size and clean up if necessary
        self._check_cache_size()
        
        return content
    
    def get_analysis_result(self, analyzer_name: str, file_path: str) -> Optional[Any]:
        """
        Get analysis result from cache.
        
        Args:
            analyzer_name: Name of the analyzer
            file_path: Path to the file
            
        Returns:
            Cached analysis result or None if not in cache
        """
        cache_key = f"{analyzer_name}:{file_path}"
        
        if cache_key in self.analysis_cache:
            # Check if file has changed
            if file_path in self.file_cache:
                file_hash = self.file_cache[file_path].hash
                cached_result = self.analysis_cache[cache_key]
                
                if cached_result.get('file_hash') == file_hash:
                    self.hits += 1
                    return cached_result.get('result')
        
        self.misses += 1
        return None
    
    def set_analysis_result(self, analyzer_name: str, file_path: str, result: Any) -> None:
        """
        Set analysis result in cache.
        
        Args:
            analyzer_name: Name of the analyzer
            file_path: Path to the file
            result: Analysis result
        """
        if file_path not in self.file_cache:
            return
        
        cache_key = f"{analyzer_name}:{file_path}"
        file_hash = self.file_cache[file_path].hash
        
        self.analysis_cache[cache_key] = {
            'file_hash': file_hash,
            'result': result,
            'timestamp': time.time()
        }
    
    def _check_cache_size(self) -> None:
        """Check cache size and remove oldest entries if necessary."""
        # Calculate current cache size
        cache_size = sum(len(entry.content) for entry in self.file_cache.values())
        cache_size_mb = cache_size / (1024 * 1024)
        
        # If cache size exceeds limit, remove oldest entries
        if cache_size_mb > self.max_size_mb:
            self.logger.info(f"Cache size ({cache_size_mb:.2f} MB) exceeds limit ({self.max_size_mb} MB), cleaning up")
            
            # Sort entries by last accessed time
            sorted_entries = sorted(
                self.file_cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            # Remove oldest entries until cache size is below limit
            removed = 0
            for file_path, _ in sorted_entries:
                entry_size = len(self.file_cache[file_path].content)
                del self.file_cache[file_path]
                cache_size -= entry_size
                cache_size_mb = cache_size / (1024 * 1024)
                removed += 1
                
                if cache_size_mb <= self.max_size_mb * 0.8:  # Remove until 80% of limit
                    break
            
            self.logger.info(f"Removed {removed} entries from cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        # Calculate cache size
        cache_size = sum(len(entry.content) for entry in self.file_cache.values())
        cache_size_mb = cache_size / (1024 * 1024)
        
        # Calculate hit ratio
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 0
        
        return {
            'size_mb': cache_size_mb,
            'file_entries': len(self.file_cache),
            'analysis_entries': len(self.analysis_cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio
        }
    
    def save_cache_to_disk(self) -> bool:
        """
        Save cache to disk.
        
        Returns:
            True if cache was saved successfully, False otherwise
        """
        try:
            cache_path = os.path.join(self.cache_dir, 'analyzer_cache.pkl')
            
            # Create a simplified version of the cache for serialization
            serializable_file_cache = {}
            for file_path, entry in self.file_cache.items():
                serializable_file_cache[file_path] = {
                    'content': entry.content,
                    'hash': entry.hash,
                    'mtime': entry.mtime,
                    'size': entry.size,
                    'last_accessed': entry.last_accessed
                }
            
            cache_data = {
                'file_cache': serializable_file_cache,
                'analysis_cache': self.analysis_cache,
                'hits': self.hits,
                'misses': self.misses
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.info(f"Cache saved to {cache_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
            return False
    
    def load_cache_from_disk(self) -> bool:
        """
        Load cache from disk.
        
        Returns:
            True if cache was loaded successfully, False otherwise
        """
        try:
            cache_path = os.path.join(self.cache_dir, 'analyzer_cache.pkl')
            
            if not os.path.exists(cache_path):
                return False
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Convert serialized file cache back to FileCacheEntry objects
            for file_path, entry_data in cache_data.get('file_cache', {}).items():
                self.file_cache[file_path] = FileCacheEntry(
                    content=entry_data['content'],
                    hash=entry_data['hash'],
                    mtime=entry_data['mtime'],
                    size=entry_data['size'],
                    last_accessed=entry_data['last_accessed']
                )
            
            self.analysis_cache = cache_data.get('analysis_cache', {})
            self.hits = cache_data.get('hits', 0)
            self.misses = cache_data.get('misses', 0)
            
            self.logger.info(f"Cache loaded from {cache_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            return False


class MemoryMonitor:
    """Monitor memory usage during analysis."""
    
    def __init__(self, threshold_percent: float = 80.0):
        """
        Initialize the memory monitor.
        
        Args:
            threshold_percent: Memory usage threshold percentage
        """
        self.threshold_percent = threshold_percent
        self.peak_memory_mb = 0
        self.logger = logging.getLogger(__name__)
    
    def check_memory_usage(self) -> Tuple[float, bool]:
        """
        Check current memory usage.
        
        Returns:
            Tuple of (memory usage in MB, whether threshold is exceeded)
        """
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            # Update peak memory
            if memory_mb > self.peak_memory_mb:
                self.peak_memory_mb = memory_mb
            
            # Check if memory usage exceeds threshold
            memory_percent = process.memory_percent()
            threshold_exceeded = memory_percent > self.threshold_percent
            
            if threshold_exceeded:
                self.logger.warning(
                    f"Memory usage ({memory_percent:.1f}%) exceeds threshold ({self.threshold_percent}%)"
                )
            
            return memory_mb, threshold_exceeded
            
        except ImportError:
            # psutil not available
            return 0, False
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
            return 0, False
    
    def get_memory_stats(self) -> Dict[str, float]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            current_mb = memory_info.rss / (1024 * 1024)
            
            return {
                'current_mb': current_mb,
                'peak_mb': self.peak_memory_mb,
                'percent': process.memory_percent()
            }
            
        except ImportError:
            # psutil not available
            return {
                'current_mb': 0,
                'peak_mb': self.peak_memory_mb,
                'percent': 0
            }
        except Exception:
            return {
                'current_mb': 0,
                'peak_mb': self.peak_memory_mb,
                'percent': 0
            }