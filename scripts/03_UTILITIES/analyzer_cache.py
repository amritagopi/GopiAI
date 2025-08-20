"""
Analyzer Cache - Performance Optimizations for Project Cleanup

This module implements caching mechanisms to improve performance of the project cleanup
analyzers, including file content caching, AST parsing cache, and incremental analysis.
"""

import os
import hashlib
import pickle
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set, Tuple, List
from dataclasses import dataclass, field

# Импортируем ast с обработкой ошибок
try:
    import ast
except ImportError:
    # Создаем заглушку для модуля ast
    class AstModule:
        class AST:
            pass

        @staticmethod
        def parse(source: str, filename: str = "<unknown>", mode: str = "exec"):
            # Простейшая заглушка: возвращаем None, что совместимо с Optional[Any] в get_ast
            return None

    ast = AstModule


@dataclass
class FileCacheEntry:
    """Cache entry for a file's content and metadata."""

    content: str
    hash: str
    mtime: float
    size: int
    ast: Optional[Any] = None  # Используем Any вместо ast.AST
    last_accessed: float = field(default_factory=time.time)


class AnalyzerCache:
    """Cache system for analyzer operations to improve performance."""

    def __init__(self, cache_dir: str = ".analyzer_cache", max_size_mb: int = 100):
        """
        Initialize the analyzer cache.

        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.logger = logging.getLogger(__name__)

        # In-memory caches
        self.file_cache: Dict[str, FileCacheEntry] = {}
        self.ast_cache: Dict[str, Any] = {}
        self.analysis_results_cache: Dict[str, Dict[str, Any]] = {}

        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_size_bytes = 0

        # Initialize cache directory
        self._init_cache_dir()

    def _init_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Cache directory initialized at {self.cache_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to create cache directory: {e}")

    def _compute_file_hash(self, content: str) -> str:
        """
        Compute a hash of the file content.

        Args:
            content: File content

        Returns:
            Hash string
        """
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def get_file_content(self, file_path: Path) -> Tuple[str, bool]:
        """
        Get file content, either from cache or by reading the file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (file content, whether it was a cache hit)
        """
        path_str = str(file_path)

        try:
            # Check if file exists and get stats
            if not file_path.exists():
                return "", False

            stat = file_path.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            # Check if file is in cache and up to date
            if path_str in self.file_cache:
                cache_entry = self.file_cache[path_str]

                # Check if file has been modified
                if mtime == cache_entry.mtime and size == cache_entry.size:
                    cache_entry.last_accessed = time.time()
                    self.cache_hits += 1
                    return cache_entry.content, True

            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Compute hash
            file_hash = self._compute_file_hash(content)

            # Update cache
            self.file_cache[path_str] = FileCacheEntry(
                content=content, hash=file_hash, mtime=mtime, size=size
            )

            # Update cache size
            self.cache_size_bytes += len(content)

            # Check if cache is too large
            if self.cache_size_bytes > self.max_size_bytes:
                self._cleanup_cache()

            self.cache_misses += 1
            return content, False

        except Exception as e:
            self.logger.warning(f"Error reading file {file_path}: {e}")
            return "", False

    def get_ast(self, file_path: Path) -> Tuple[Optional[Any], bool]:
        """
        Get AST for a Python file, either from cache or by parsing.

        Args:
            file_path: Path to the Python file

        Returns:
            Tuple of (AST or None, whether it was a cache hit)
        """
        path_str = str(file_path)

        try:
            # Get file content
            content, content_hit = self.get_file_content(file_path)

            if not content:
                return None, False

            # Check if file is in AST cache
            if (
                path_str in self.file_cache
                and self.file_cache[path_str].ast is not None
            ):
                cache_entry = self.file_cache[path_str]
                cache_entry.last_accessed = time.time()
                self.cache_hits += 1
                return cache_entry.ast, True

            # Parse AST
            tree = ast.parse(content, filename=path_str)

            # Update cache
            if path_str in self.file_cache:
                self.file_cache[path_str].ast = tree

            self.cache_misses += 1
            return tree, False

        except SyntaxError:
            # Don't cache files with syntax errors
            self.logger.debug(f"Syntax error in {file_path}")
            return None, False
        except Exception as e:
            self.logger.warning(f"Error parsing AST for {file_path}: {e}")
            return None, False

    def get_analysis_results(
        self, analyzer_name: str, file_path: Path
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Get cached analysis results for a file.

        Args:
            analyzer_name: Name of the analyzer
            file_path: Path to the file

        Returns:
            Tuple of (analysis results or None, whether it was a cache hit)
        """
        cache_key = f"{analyzer_name}:{file_path}"

        if cache_key in self.analysis_results_cache:
            # Check if file has been modified
            content, hit = self.get_file_content(file_path)

            if hit and content:
                file_hash = self._compute_file_hash(content)
                cached_result = self.analysis_results_cache[cache_key]

                if cached_result.get("file_hash") == file_hash:
                    self.cache_hits += 1
                    return cached_result.get("results"), True

        self.cache_misses += 1
        return None, False

    def store_analysis_results(
        self, analyzer_name: str, file_path: Path, results: Dict[str, Any]
    ) -> None:
        """
        Store analysis results in cache.

        Args:
            analyzer_name: Name of the analyzer
            file_path: Path to the file
            results: Analysis results to cache
        """
        try:
            content, _ = self.get_file_content(file_path)

            if content:
                file_hash = self._compute_file_hash(content)
                cache_key = f"{analyzer_name}:{file_path}"

                self.analysis_results_cache[cache_key] = {
                    "file_hash": file_hash,
                    "results": results,
                    "timestamp": time.time(),
                }
        except Exception as e:
            self.logger.warning(f"Error storing analysis results: {e}")

    def save_cache_to_disk(self) -> bool:
        """
        Save cache to disk for persistence between runs.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a dictionary with cache metadata
            cache_data = {
                "timestamp": time.time(),
                "analysis_results": self.analysis_results_cache,
                # Don't save file content or AST to disk, just metadata
                "file_metadata": {
                    path: {"hash": entry.hash, "mtime": entry.mtime, "size": entry.size}
                    for path, entry in self.file_cache.items()
                },
            }

            # Save to disk
            cache_file = self.cache_dir / "analyzer_cache.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            self.logger.info(f"Cache saved to {cache_file}")
            return True

        except Exception as e:
            self.logger.warning(f"Failed to save cache to disk: {e}")
            return False

    def load_cache_from_disk(self) -> bool:
        """
        Load cache from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_file = self.cache_dir / "analyzer_cache.pkl"

            if not cache_file.exists():
                return False

            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            # Load analysis results cache
            self.analysis_results_cache = cache_data.get("analysis_results", {})

            # Load file metadata (not content)
            file_metadata = cache_data.get("file_metadata", {})

            self.logger.info(f"Cache loaded from {cache_file}")
            return True

        except Exception as e:
            self.logger.warning(f"Failed to load cache from disk: {e}")
            return False

    def _cleanup_cache(self) -> None:
        """Clean up cache when it gets too large."""
        # Sort cache entries by last accessed time
        sorted_entries = sorted(
            self.file_cache.items(), key=lambda x: x[1].last_accessed
        )

        # Remove oldest entries until cache is under the size limit
        removed = 0
        for path, entry in sorted_entries:
            if (
                self.cache_size_bytes <= self.max_size_bytes * 0.8
            ):  # Target 80% of max size
                break

            self.cache_size_bytes -= len(entry.content)
            del self.file_cache[path]
            removed += 1

        self.logger.debug(f"Cleaned up cache, removed {removed} entries")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_ratio": (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0
            ),
            "size_bytes": self.cache_size_bytes,
            "size_mb": self.cache_size_bytes / (1024 * 1024),
            "file_entries": len(self.file_cache),
            "analysis_entries": len(self.analysis_results_cache),
        }

    def clear_cache(self) -> None:
        """Clear all caches."""
        self.file_cache.clear()
        self.ast_cache.clear()
        self.analysis_results_cache.clear()
        self.cache_size_bytes = 0
        self.logger.info("Cache cleared")


class IncrementalAnalyzer:
    """
    Manages incremental analysis for large projects.

    This class tracks which files have been analyzed and which have changed,
    allowing analyzers to only process modified files.
    """

    def __init__(self, project_path: str, cache_dir: str = ".analyzer_cache"):
        """
        Initialize the incremental analyzer.

        Args:
            project_path: Path to the project root
            cache_dir: Directory to store cache files
        """
        self.project_path = Path(project_path)
        self.cache_dir = Path(cache_dir)
        self.logger = logging.getLogger(__name__)

        # File tracking
        self.analyzed_files: Dict[str, Dict[str, Any]] = {}
        self.changed_files: Set[str] = set()

        # Initialize cache directory
        self._init_cache_dir()

        # Load previous analysis state if available
        self._load_state()

    def _init_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.warning(f"Failed to create cache directory: {e}")

    def _load_state(self) -> None:
        """Load previous analysis state from disk."""
        try:
            state_file = self.cache_dir / "incremental_state.pkl"

            if state_file.exists():
                with open(state_file, "rb") as f:
                    state = pickle.load(f)

                self.analyzed_files = state.get("analyzed_files", {})
                self.logger.info(
                    f"Loaded incremental state with {len(self.analyzed_files)} files"
                )
        except Exception as e:
            self.logger.warning(f"Failed to load incremental state: {e}")

    def save_state(self) -> None:
        """Save current analysis state to disk."""
        try:
            state = {"timestamp": time.time(), "analyzed_files": self.analyzed_files}

            state_file = self.cache_dir / "incremental_state.pkl"

            with open(state_file, "wb") as f:
                pickle.dump(state, f)

            self.logger.info(
                f"Saved incremental state with {len(self.analyzed_files)} files"
            )
        except Exception as e:
            self.logger.warning(f"Failed to save incremental state: {e}")

    def identify_changed_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Identify files that have changed since the last analysis.

        Args:
            file_paths: List of file paths to check

        Returns:
            List of file paths that have changed
        """
        changed = []

        for file_path in file_paths:
            path_str = str(file_path)

            try:
                # Check if file exists
                if not file_path.exists():
                    continue

                # Get file stats
                stat = file_path.stat()
                mtime = stat.st_mtime
                size = stat.st_size

                # Check if file has been analyzed before
                if path_str in self.analyzed_files:
                    file_info = self.analyzed_files[path_str]

                    # Check if file has been modified
                    if mtime != file_info.get("mtime") or size != file_info.get("size"):
                        changed.append(file_path)
                        self.changed_files.add(path_str)
                else:
                    # New file
                    changed.append(file_path)
                    self.changed_files.add(path_str)

                    # Add to analyzed files
                    self.analyzed_files[path_str] = {
                        "mtime": mtime,
                        "size": size,
                        "last_analyzed": time.time(),
                    }

            except Exception as e:
                self.logger.warning(f"Error checking file {file_path}: {e}")

        return changed

    def mark_file_analyzed(self, file_path: Path) -> None:
        """
        Mark a file as analyzed.

        Args:
            file_path: Path to the file
        """
        path_str = str(file_path)

        try:
            # Check if file exists
            if not file_path.exists():
                return

            # Get file stats
            stat = file_path.stat()

            # Update analyzed files
            self.analyzed_files[path_str] = {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "last_analyzed": time.time(),
            }

            # Remove from changed files
            if path_str in self.changed_files:
                self.changed_files.remove(path_str)

        except Exception as e:
            self.logger.warning(f"Error marking file {file_path} as analyzed: {e}")

    def get_changed_file_count(self) -> int:
        """
        Get the number of changed files.

        Returns:
            Number of changed files
        """
        return len(self.changed_files)

    def reset(self) -> None:
        """Reset the incremental analyzer state."""
        self.analyzed_files.clear()
        self.changed_files.clear()
        self.logger.info("Incremental analyzer state reset")


class MemoryMonitor:
    """
    Monitors memory usage during analysis.

    This class tracks memory usage and can trigger cleanup actions
    when memory usage gets too high.
    """

    def __init__(self, threshold_percent: float = 80.0):
        """
        Initialize the memory monitor.

        Args:
            threshold_percent: Memory usage threshold as a percentage
        """
        self.threshold_percent = threshold_percent
        self.logger = logging.getLogger(__name__)
        self.peak_usage = 0
        self.last_check = time.time()
        self.check_interval = 5  # seconds

    def check_memory_usage(self) -> Tuple[float, bool]:
        """
        Check current memory usage.

        Returns:
            Tuple of (memory usage percentage, whether it exceeds threshold)
        """
        # Only check memory usage periodically
        now = time.time()
        if now - self.last_check < self.check_interval:
            return 0.0, False

        self.last_check = now

        try:
            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            # Get memory usage in bytes
            memory_usage = memory_info.rss

            # Get system memory
            system_memory = psutil.virtual_memory().total

            # Calculate percentage
            usage_percent = (memory_usage / system_memory) * 100

            # Update peak usage
            self.peak_usage = max(self.peak_usage, memory_usage)

            # Check if usage exceeds threshold
            exceeds_threshold = usage_percent > self.threshold_percent

            if exceeds_threshold:
                self.logger.warning(
                    f"Memory usage high: {usage_percent:.1f}% "
                    f"({memory_usage / (1024 * 1024):.1f} MB)"
                )

            return usage_percent, exceeds_threshold

        except ImportError:
            self.logger.warning("psutil not available, memory monitoring disabled")
            return 0.0, False
        except Exception as e:
            self.logger.warning(f"Error checking memory usage: {e}")
            return 0.0, False

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.

        Returns:
            Dictionary with memory statistics
        """
        try:
            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                "current_bytes": memory_info.rss,
                "current_mb": memory_info.rss / (1024 * 1024),
                "peak_bytes": self.peak_usage,
                "peak_mb": self.peak_usage / (1024 * 1024),
                "system_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
