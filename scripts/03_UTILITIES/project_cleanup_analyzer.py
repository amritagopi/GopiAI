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
    cache_dir: str = ".analyzer_cache"  # Directory for cache files
    max_cache_size_mb: int = 100  # Maximum cache size in megabytes
    
    # Incremental analysis settings
    incremental_analysis: bool = True  # Only analyze changed files
    
    # Memory management settings
    memory_threshold_percent: float = 80.0  # Memory usage threshold
    
    # Analysis depth settings
    analysis_depth: str = 'full'  # 'quick', 'standard', 'full'
    max_files_per_analyzer: int = 0  # 0 means no limit
    
    def __post_init__(self):
        """Validate configuration parameters."""
        valid_severities = {'high', 'medium', 'low'}
        if self.severity_threshold not in valid_severities:
            raise ValueError(f"Severity threshold must be one of {valid_severities}")
        
        valid_formats = {'markdown', 'json', 'html'}
        if self.output_format not in valid_formats:
            raise ValueError(f"Output format must be one of {valid_formats}")
        
        valid_depths = {'quick', 'standard', 'full'}
        if self.analysis_depth not in valid_depths:
            raise ValueError(f"Analysis depth must be one of {valid_depths}")
        
        if not Path(self.project_path).exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")


class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    
    def __init__(self, analyzer: str, file_path: str, error: str, original_exception: Exception = None):
        self.analyzer = analyzer
        self.file_path = file_path
        self.error = error
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()
        
        super().__init__(f"{analyzer}: {error} in {file_path}")


class ErrorHandler:
    """Handles and tracks errors during analysis."""
    
    def __init__(self):
        self.errors: List[AnalysisError] = []
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: AnalysisError) -> None:
        """Handle an analysis error by logging and storing it."""
        self.errors.append(error)
        self.logger.error(
            f"Analysis error in {error.analyzer}: {error.error} "
            f"(file: {error.file_path})",
            exc_info=error.original_exception
        )
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get a summary of errors by analyzer."""
        summary = {}
        for error in self.errors:
            summary[error.analyzer] = summary.get(error.analyzer, 0) + 1
        return summary
    
    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0
    
    def clear_errors(self) -> None:
        """Clear all recorded errors."""
        self.errors.clear()


class BaseAnalyzer(ABC):
    """Abstract base class for all project analyzers."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize cache if enabled
        self.cache = None
        self.incremental_analyzer = None
        self.memory_monitor = None
        
        if hasattr(config, 'enable_caching') and config.enable_caching:
            try:
                from analyzer_cache import AnalyzerCache, IncrementalAnalyzer, MemoryMonitor
                self.cache = AnalyzerCache(
                    cache_dir=config.cache_dir,
                    max_size_mb=config.max_cache_size_mb
                )
                self.incremental_analyzer = IncrementalAnalyzer(
                    project_path=config.project_path,
                    cache_dir=config.cache_dir
                )
                self.memory_monitor = MemoryMonitor(
                    threshold_percent=config.memory_threshold_percent
                )
                self.logger.info(f"Initialized caching for {self.get_analyzer_name()}")
            except ImportError:
                self.logger.warning("Caching modules not available, caching disabled")
    
    @abstractmethod
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        pass
    
    @abstractmethod
    def get_analyzer_name(self) -> str:
        """
        Get the name of this analyzer.
        
        Returns:
            Human-readable name of the analyzer
        """
        pass
    
    def should_analyze_file(self, file_path: Path) -> bool:
        """
        Check if a file should be analyzed based on configuration.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file should be analyzed, False otherwise
        """
        # Check file size
        try:
            if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                return False
        except OSError:
            return False
        
        # Check include patterns
        if self.config.include_patterns:
            if not any(file_path.match(pattern) for pattern in self.config.include_patterns):
                return False
        
        # Check exclude patterns
        if any(file_path.match(pattern) for pattern in self.config.exclude_patterns):
            return False
        
        return True
    
    def get_project_files(self, project_path: str, file_extensions: List[str] = None) -> List[Path]:
        """
        Get list of files to analyze in the project.
        
        Args:
            project_path: Path to the project root
            file_extensions: Optional list of file extensions to filter by
            
        Returns:
            List of file paths to analyze
        """
        project_root = Path(project_path)
        files = []
        
        try:
            for file_path in project_root.rglob('*'):
                if file_path.is_file():
                    if file_extensions:
                        if file_path.suffix.lower() in file_extensions:
                            if self.should_analyze_file(file_path):
                                files.append(file_path)
                    else:
                        if self.should_analyze_file(file_path):
                            files.append(file_path)
                            
            # Apply file limit based on analysis depth if configured
            if hasattr(self.config, 'max_files_per_analyzer') and self.config.max_files_per_analyzer > 0:
                if len(files) > self.config.max_files_per_analyzer:
                    self.logger.info(
                        f"Limiting analysis to {self.config.max_files_per_analyzer} files "
                        f"(out of {len(files)} total)"
                    )
                    files = files[:self.config.max_files_per_analyzer]
            
            # Apply incremental analysis if enabled
            if (hasattr(self.config, 'incremental_analysis') and 
                self.config.incremental_analysis and 
                self.incremental_analyzer):
                
                changed_files = self.incremental_analyzer.identify_changed_files(files)
                
                if len(changed_files) < len(files):
                    self.logger.info(
                        f"Incremental analysis: analyzing {len(changed_files)} changed files "
                        f"(out of {len(files)} total)"
                    )
                    files = changed_files
                    
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to scan project files: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return files
    
    def get_file_content(self, file_path: Path) -> str:
        """
        Get file content, using cache if available.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        if self.cache:
            content, _ = self.cache.get_file_content(file_path)
            return content
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Error reading file {file_path}: {e}")
            return ""
    
    def get_ast(self, file_path: Path):
        """
        Get AST for a Python file, using cache if available.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            AST or None if parsing failed
        """
        if self.cache:
            ast_tree, _ = self.cache.get_ast(file_path)
            return ast_tree
        
        try:
            content = self.get_file_content(file_path)
            if content:
                return ast.parse(content, filename=str(file_path))
        except SyntaxError:
            self.logger.debug(f"Syntax error in {file_path}")
        except Exception as e:
            self.logger.warning(f"Error parsing AST for {file_path}: {e}")
        
        return None
    
    def check_memory_usage(self):
        """
        Check memory usage and trigger cleanup if necessary.
        
        Returns:
            True if memory usage is within limits, False otherwise
        """
        if self.memory_monitor:
            usage_percent, exceeds_threshold = self.memory_monitor.check_memory_usage()
            
            if exceeds_threshold and self.cache:
                self.logger.warning(
                    f"Memory usage high ({usage_percent:.1f}%), clearing cache"
                )
                self.cache.clear_cache()
                return False
        
        return True
    
    def mark_file_analyzed(self, file_path: Path):
        """
        Mark a file as analyzed for incremental analysis.
        
        Args:
            file_path: Path to the file
        """
        if self.incremental_analyzer:
            self.incremental_analyzer.mark_file_analyzed(file_path)
    
    def filter_results_by_severity(self, results: List[AnalysisResult]) -> List[AnalysisResult]:
        """
        Filter results based on configured severity threshold.
        
        Args:
            results: List of analysis results
            
        Returns:
            Filtered list of results
        """
        severity_order = {'low': 0, 'medium': 1, 'high': 2}
        threshold_level = severity_order.get(self.config.severity_threshold, 0)
        
        return [
            result for result in results
            if severity_order.get(result.severity, 0) >= threshold_level
        ]
        
    def save_cache_state(self):
        """Save cache state to disk."""
        if self.cache:
            self.cache.save_cache_to_disk()
        
        if self.incremental_analyzer:
            self.incremental_analyzer.save_state()


# Example concrete analyzer for testing the infrastructure
class TestAnalyzer(BaseAnalyzer):
    """Test analyzer to verify the infrastructure works correctly."""
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """Perform a simple test analysis."""
        results = []
        
        # Test finding Python files
        python_files = self.get_project_files(project_path, ['.py'])
        
        if len(python_files) > 0:
            results.append(AnalysisResult(
                category="test",
                severity="low",
                description=f"Found {len(python_files)} Python files in project",
                file_path=project_path,
                recommendation="This is a test result to verify the infrastructure"
            ))
        
        return self.filter_results_by_severity(results)
    
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Test Analyzer"


if __name__ == "__main__":
    # Simple test of the infrastructure
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = TestAnalyzer(config)
        
        print(f"Testing {analyzer.get_analyzer_name()}...")
        results = analyzer.analyze(project_path)
        
        print(f"Analysis complete. Found {len(results)} results:")
        for result in results:
            print(f"  - {result.severity.upper()}: {result.description}")
        
        if analyzer.error_handler.has_errors():
            print(f"Errors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)