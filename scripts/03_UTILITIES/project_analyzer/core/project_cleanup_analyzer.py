"""
Project Cleanup Analyzer - Core Infrastructure

This module provides the base infrastructure for analyzing and cleaning up
the GopiAI project codebase. It includes abstract base classes, data models,
configuration management, and error handling framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime


@dataclass
class AnalysisResult:
    """Represents a single analysis finding."""
    category: str
    severity: str  # 'high', 'medium', 'low'
    description: str
    file_path: str
    line_number: Optional[int] = None
    recommendation: str = ""
    
    def __post_init__(self):
        """Validate severity level."""
        valid_severities = {'high', 'medium', 'low'}
        if self.severity not in valid_severities:
            raise ValueError(f"Severity must be one of {valid_severities}, got '{self.severity}'")


@dataclass
class AnalysisConfig:
    """Configuration for project cleanup analysis."""
    project_path: str
    exclude_patterns: List[str] = field(default_factory=lambda: [
        '*.pyc', '__pycache__', '.git', '.vscode', 'node_modules',
        '*.egg-info', '.pytest_cache', '.tox', 'venv', '*_env',
        '*/site-packages/*', '*/Lib/site-packages/*', '*/lib/python*/site-packages/*'
    ])
    include_patterns: List[str] = field(default_factory=lambda: ['*.py', '*.md', '*.txt', '*.toml'])
    severity_threshold: str = 'low'  # Minimum severity to report
    output_format: str = 'markdown'  # 'markdown', 'json', 'html'
    detailed_analysis: bool = True  # Include detailed recommendations
    max_file_size_mb: int = 10  # Skip files larger than this
    
    # Performance optimization settings
    enable_caching: bool = True  # Enable file content and AST caching
    incremental_analysis: bool = False  # Only analyze changed files
    analysis_depth: str = 'standard'  # 'quick', 'standard', 'full'
    max_files_per_analyzer: int = 1000  # Limit files per analyzer for performance
    cache_dir: str = '.analyzer_cache'
    max_cache_size_mb: int = 100
    memory_threshold_percent: float = 80.0
    
    def __post_init__(self):
        """Validate configuration."""
        valid_formats = {'markdown', 'json', 'html'}
        if self.output_format not in valid_formats:
            raise ValueError(f"Output format must be one of {valid_formats}")
        
        valid_depths = {'quick', 'standard', 'full'}
        if self.analysis_depth not in valid_depths:
            raise ValueError(f"Analysis depth must be one of {valid_depths}")


class BaseAnalyzer(ABC):
    """Abstract base class for all project analyzers."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """Analyze the project and return findings."""
        pass
    
    def get_project_files(self, project_path: str, file_extensions: Optional[List[str]] = None) -> List[Path]:
        """Get all relevant project files within project boundaries."""
        project_path = Path(project_path)
        project_path_abs = project_path.resolve()  # Get absolute path for comparison
        files = []
        
        # Use include patterns if file_extensions not specified
        if file_extensions is None:
            file_extensions = self.config.include_patterns
        
        for pattern in file_extensions:
            files.extend(project_path.rglob(pattern))
        
        # Filter out excluded patterns and ensure files are within project boundaries
        filtered_files = []
        for file_path in files:
            # Ensure file is within project boundaries
            try:
                file_path_abs = file_path.resolve()
                if not str(file_path_abs).startswith(str(project_path_abs)):
                    # Skip files outside project boundaries
                    continue
            except (OSError, ValueError):
                # If we can't resolve the path, skip it
                continue
            
            if not self._should_exclude_file(file_path):
                # Check file size
                try:
                    if file_path.stat().st_size <= self.config.max_file_size_mb * 1024 * 1024:
                        filtered_files.append(file_path)
                except (OSError, IOError):
                    # Skip files we can't access
                    continue
        
        # Limit number of files for performance (but only if limit is set and not 0)
        if self.config.max_files_per_analyzer > 0 and len(filtered_files) > self.config.max_files_per_analyzer:
            self.logger.warning(f"Limiting analysis to {self.config.max_files_per_analyzer} files")
            filtered_files = filtered_files[:self.config.max_files_per_analyzer]
        
        return filtered_files
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded based on patterns."""
        file_str = str(file_path).replace('\\', '/')  # Normalize path separators
        
        for pattern in self.config.exclude_patterns:
            pattern = pattern.replace('\\', '/')  # Normalize pattern separators
            
            # Check for directory exclusions (patterns ending with /* or containing directory names)
            if pattern.endswith('/*') or '/' in pattern.rstrip('/*'):
                # For directory patterns, check if any part of the file path matches
                pattern_dir = pattern.rstrip('/*')
                if pattern_dir in file_str:
                    return True
            
            # Check exact pattern match
            if pattern in file_str:
                return True
                
            # Use Path.match for glob patterns
            try:
                if file_path.match(pattern):
                    return True
            except Exception:
                # If match fails, fall back to substring check
                pass
                
        return False


class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    pass


class ConfigurationError(AnalysisError):
    """Exception for configuration-related errors."""
    pass


class FileAccessError(AnalysisError):
    """Exception for file access errors."""
    pass


# Utility functions
def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('project_cleanup_analysis.log')
        ]
    )


def validate_project_path(project_path: str) -> Path:
    """Validate and return project path."""
    path = Path(project_path)
    if not path.exists():
        raise ConfigurationError(f"Project path does not exist: {project_path}")
    if not path.is_dir():
        raise ConfigurationError(f"Project path is not a directory: {project_path}")
    return path
