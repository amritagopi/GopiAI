"""
Project Cleanup Orchestrator - Main Orchestrator

This module implements the ProjectCleanupAnalyzer class that coordinates all analyzers,
including parallel execution, progress reporting, configuration loading and validation,
and error aggregation and reporting across all analyzers.
"""

import os
import sys
import time
import logging
import multiprocessing
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import argparse
from dataclasses import asdict

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import (
    BaseAnalyzer, AnalysisResult, AnalysisConfig, AnalysisError, ErrorHandler
)
from structure_analyzer import StructureAnalyzer
from code_quality_analyzer import CodeQualityAnalyzer
from dead_code_analyzer import DeadCodeAnalyzer
from file_analyzer import FileAnalyzer
from dependency_analyzer import DependencyAnalyzer
from duplicate_analyzer import DuplicateAnalyzer
from conflict_analyzer import ConflictAnalyzer
from documentation_analyzer import DocumentationAnalyzer
from report_generator import ReportGenerator, CleanupReport


class ProgressReporter:
    """Reports progress for long-running analysis operations."""
    
    def __init__(self, total_analyzers: int):
        """
        Initialize the progress reporter.
        
        Args:
            total_analyzers: Total number of analyzers to track
        """
        self.total_analyzers = total_analyzers
        self.completed_analyzers = 0
        self.start_time = time.time()
        self.analyzer_times: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
    
    def analyzer_started(self, analyzer_name: str) -> None:
        """
        Record that an analyzer has started.
        
        Args:
            analyzer_name: Name of the analyzer that started
        """
        self.logger.info(f"Started {analyzer_name}")
        self.analyzer_times[analyzer_name] = time.time()
    
    def analyzer_completed(self, analyzer_name: str, result_count: int) -> None:
        """
        Record that an analyzer has completed.
        
        Args:
            analyzer_name: Name of the analyzer that completed
            result_count: Number of results found by the analyzer
        """
        self.completed_analyzers += 1
        elapsed = time.time() - self.analyzer_times.get(analyzer_name, self.start_time)
        
        self.logger.info(
            f"Completed {analyzer_name} in {elapsed:.2f}s - "
            f"Found {result_count} issues - "
            f"Progress: {self.completed_analyzers}/{self.total_analyzers} analyzers"
        )
    
    def get_progress(self) -> float:
        """
        Get the current progress as a percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        return (self.completed_analyzers / self.total_analyzers) * 100 if self.total_analyzers > 0 else 0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the progress.
        
        Returns:
            Dictionary with progress summary
        """
        elapsed = time.time() - self.start_time
        return {
            'total_analyzers': self.total_analyzers,
            'completed_analyzers': self.completed_analyzers,
            'progress_percent': self.get_progress(),
            'elapsed_seconds': elapsed,
            'analyzer_times': self.analyzer_times
        }


class ProjectCleanupAnalyzer:
    """Main orchestrator for project cleanup analysis."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None, config_path: Optional[str] = None):
        """
        Initialize the project cleanup analyzer.
        
        Args:
            config: Optional analysis configuration
            config_path: Optional path to a JSON configuration file
        """
        self.config = config or self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()
        self.progress_reporter = None
        
        # Initialize cache if enabled
        self.cache = None
        self.memory_monitor = None
        if hasattr(self.config, 'enable_caching') and self.config.enable_caching:
            try:
                from analyzer_cache import AnalyzerCache, MemoryMonitor
                self.cache = AnalyzerCache(
                    cache_dir=self.config.cache_dir,
                    max_size_mb=self.config.max_cache_size_mb
                )
                self.memory_monitor = MemoryMonitor(
                    threshold_percent=self.config.memory_threshold_percent
                )
                self.logger.info("Initialized caching system")
                
                # Load cache from disk
                self.cache.load_cache_from_disk()
            except ImportError:
                self.logger.warning("Caching modules not available, caching disabled")
        
        # Configure analyzers based on analysis depth
        self._configure_analyzers_by_depth()
        
        # Initialize analyzers
        self.analyzers: List[BaseAnalyzer] = [
            StructureAnalyzer(self.config),
            CodeQualityAnalyzer(self.config),
            DeadCodeAnalyzer(self.config),
            FileAnalyzer(self.config),
            DependencyAnalyzer(self.config),
            DuplicateAnalyzer(self.config),
            ConflictAnalyzer(self.config),
            DocumentationAnalyzer(self.config)
        ]
        
        self.report_generator = ReportGenerator(self.config)
        
    def _configure_analyzers_by_depth(self):
        """Configure analysis depth settings."""
        if not hasattr(self.config, 'analysis_depth'):
            return
            
        # Configure based on analysis depth
        if self.config.analysis_depth == 'quick':
            # Quick analysis - limit file count and disable some analyzers
            self.config.max_files_per_analyzer = self.config.max_files_per_analyzer or 100
            self.logger.info("Using 'quick' analysis depth - limiting to 100 files per analyzer")
            
        elif self.config.analysis_depth == 'standard':
            # Standard analysis - balanced approach
            self.config.max_files_per_analyzer = self.config.max_files_per_analyzer or 500
            self.logger.info("Using 'standard' analysis depth - limiting to 500 files per analyzer")
            
        elif self.config.analysis_depth == 'full':
            # Full analysis - no limits
            self.config.max_files_per_analyzer = self.config.max_files_per_analyzer or 0
            self.logger.info("Using 'full' analysis depth - no file limit")
    
    def _load_config(self, config_path: Optional[str] = None) -> AnalysisConfig:
        """
        Load configuration from a file or create default configuration.
        
        Args:
            config_path: Optional path to a JSON configuration file
            
        Returns:
            Analysis configuration
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Create config from loaded data
                return AnalysisConfig(**config_data)
            except Exception as e:
                self.logger.error(f"Failed to load configuration from {config_path}: {e}")
                self.logger.info("Using default configuration")
        
        # Use current directory as default project path
        return AnalysisConfig(project_path=os.getcwd())
    
    def _run_analyzer(self, analyzer: BaseAnalyzer) -> Tuple[str, List[AnalysisResult], Dict[str, int]]:
        """
        Run a single analyzer and return its results.
        
        Args:
            analyzer: The analyzer to run
            
        Returns:
            Tuple of (analyzer name, results, error summary)
        """
        analyzer_name = analyzer.get_analyzer_name()
        try:
            results = analyzer.analyze(self.config.project_path)
            error_summary = analyzer.error_handler.get_error_summary()
            return analyzer_name, results, error_summary
        except Exception as e:
            self.logger.error(f"Error running {analyzer_name}: {e}")
            return analyzer_name, [], {analyzer_name: 1}
    
    def run_analysis_parallel(self) -> CleanupReport:
        """
        Run all analyzers in parallel using multiprocessing.
        
        Returns:
            Cleanup report with analysis results
        """
        all_results: List[AnalysisResult] = []
        all_errors: Dict[str, int] = {}
        
        # Initialize progress reporter
        self.progress_reporter = ProgressReporter(len(self.analyzers))
        
        # Determine number of processes to use (leave at least one core free)
        max_workers = max(1, multiprocessing.cpu_count() - 1)
        
        self.logger.info(f"Starting parallel analysis with {max_workers} workers")
        
        # Run analyzers in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analyzer jobs
            future_to_analyzer = {
                executor.submit(self._run_analyzer_wrapper, analyzer): analyzer.get_analyzer_name()
                for analyzer in self.analyzers
            }
            
            # Process results as they complete
            for future in as_completed(future_to_analyzer):
                analyzer_name = future_to_analyzer[future]
                try:
                    name, results, errors = future.result()
                    all_results.extend(results)
                    all_errors.update(errors)
                    
                    if self.progress_reporter:
                        self.progress_reporter.analyzer_completed(name, len(results))
                        
                except Exception as e:
                    self.logger.error(f"Analyzer {analyzer_name} failed: {e}")
                    all_errors[analyzer_name] = all_errors.get(analyzer_name, 0) + 1
        
        # Generate and return the report
        return self.report_generator.generate_report(all_results, all_errors)
    
    def _run_analyzer_wrapper(self, analyzer: BaseAnalyzer) -> Tuple[str, List[AnalysisResult], Dict[str, int]]:
        """
        Wrapper for _run_analyzer that handles progress reporting.
        
        Args:
            analyzer: The analyzer to run
            
        Returns:
            Tuple of (analyzer name, results, error summary)
        """
        analyzer_name = analyzer.get_analyzer_name()
        if self.progress_reporter:
            self.progress_reporter.analyzer_started(analyzer_name)
        
        return self._run_analyzer(analyzer)
    
    def run_analysis_sequential(self) -> CleanupReport:
        """
        Run all analyzers sequentially.
        
        Returns:
            Cleanup report with analysis results
        """
        all_results: List[AnalysisResult] = []
        all_errors: Dict[str, int] = {}
        
        # Initialize progress reporter
        self.progress_reporter = ProgressReporter(len(self.analyzers))
        
        self.logger.info("Starting sequential analysis")
        
        # Run analyzers sequentially
        for analyzer in self.analyzers:
            analyzer_name = analyzer.get_analyzer_name()
            
            if self.progress_reporter:
                self.progress_reporter.analyzer_started(analyzer_name)
            
            try:
                results = analyzer.analyze(self.config.project_path)
                all_results.extend(results)
                
                # Collect errors
                error_summary = analyzer.error_handler.get_error_summary()
                for name, count in error_summary.items():
                    all_errors[name] = all_errors.get(name, 0) + count
                
                if self.progress_reporter:
                    self.progress_reporter.analyzer_completed(analyzer_name, len(results))
                    
            except Exception as e:
                self.logger.error(f"Error running {analyzer_name}: {e}")
                all_errors[analyzer_name] = all_errors.get(analyzer_name, 0) + 1
        
        # Generate and return the report
        return self.report_generator.generate_report(all_results, all_errors)
    
    def save_report(self, report: CleanupReport, output_path: Optional[str] = None) -> str:
        """
        Save the report to a file.
        
        Args:
            report: The report to save
            output_path: Optional path to save the report to
            
        Returns:
            Path where the report was saved
        """
        return self.report_generator.save_report(report, output_path)
    
    def run_full_analysis(self, parallel: bool = True, output_path: Optional[str] = None) -> str:
        """
        Run a full analysis and save the report.
        
        Args:
            parallel: Whether to run analyzers in parallel
            output_path: Optional path to save the report to
            
        Returns:
            Path where the report was saved
        """
        self.logger.info(f"Starting full analysis of {self.config.project_path}")
        self.logger.info(f"Running in {'parallel' if parallel else 'sequential'} mode")
        
        # Log performance optimization settings
        if hasattr(self.config, 'enable_caching'):
            self.logger.info(f"Caching: {'enabled' if self.config.enable_caching else 'disabled'}")
        if hasattr(self.config, 'incremental_analysis'):
            self.logger.info(f"Incremental analysis: {'enabled' if self.config.incremental_analysis else 'disabled'}")
        if hasattr(self.config, 'analysis_depth'):
            self.logger.info(f"Analysis depth: {self.config.analysis_depth}")
        
        start_time = time.time()
        
        # Run analysis
        if parallel:
            report = self.run_analysis_parallel()
        else:
            report = self.run_analysis_sequential()
        
        elapsed = time.time() - start_time
        self.logger.info(f"Analysis completed in {elapsed:.2f} seconds")
        
        # Save report
        report_path = self.save_report(report, output_path)
        self.logger.info(f"Report saved to {report_path}")
        
        # Save cache state if enabled
        if self.cache:
            self.cache.save_cache_to_disk()
            
            # Log cache statistics
            stats = self.cache.get_cache_stats()
            self.logger.info(
                f"Cache statistics: {stats['hit_ratio']:.2%} hit ratio, "
                f"{stats['size_mb']:.2f} MB, {stats['file_entries']} files"
            )
        
        # Log memory usage if available
        if self.memory_monitor:
            stats = self.memory_monitor.get_memory_stats()
            self.logger.info(
                f"Memory usage: {stats.get('current_mb', 0):.2f} MB current, "
                f"{stats.get('peak_mb', 0):.2f} MB peak"
            )
        
        return report_path


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('project_cleanup_analysis.log')
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Project Cleanup Analyzer')
    
    parser.add_argument(
        '--project-path', '-p',
        type=str,
        default=os.getcwd(),
        help='Path to the project root directory'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to a JSON configuration file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save the report'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json', 'html'],
        default='markdown',
        help='Output format for the report'
    )
    
    parser.add_argument(
        '--sequential', '-s',
        action='store_true',
        help='Run analyzers sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level'
    )
    
    # Performance optimization options
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable file content and AST caching'
    )
    
    parser.add_argument(
        '--no-incremental',
        action='store_true',
        help='Disable incremental analysis (analyze all files)'
    )
    
    parser.add_argument(
        '--depth',
        choices=['quick', 'standard', 'full'],
        default='standard',
        help='Analysis depth (quick=minimal, standard=balanced, full=comprehensive)'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        default=0,
        help='Maximum number of files to analyze per analyzer (0=no limit)'
    )
    
    parser.add_argument(
        '--memory-threshold',
        type=float,
        default=80.0,
        help='Memory usage threshold percentage'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    
    try:
        # Create configuration
        if args.config:
            analyzer = ProjectCleanupAnalyzer(config_path=args.config)
        else:
            config = AnalysisConfig(
                project_path=args.project_path,
                output_format=args.format,
                enable_caching=not args.no_cache,
                incremental_analysis=not args.no_incremental,
                analysis_depth=args.depth,
                max_files_per_analyzer=args.max_files,
                memory_threshold_percent=args.memory_threshold
            )
            analyzer = ProjectCleanupAnalyzer(config=config)
        
        # Run analysis
        start_time = time.time()
        report_path = analyzer.run_full_analysis(
            parallel=not args.sequential,
            output_path=args.output
        )
        elapsed = time.time() - start_time
        
        # Print performance statistics
        print(f"Analysis complete in {elapsed:.2f} seconds")
        print(f"Report saved to: {report_path}")
        
        # Print cache statistics if available
        try:
            from analyzer_cache import AnalyzerCache
            cache = AnalyzerCache()
            if cache.load_cache_from_disk():
                stats = cache.get_cache_stats()
                print("\nCache Statistics:")
                print(f"  Hit ratio: {stats['hit_ratio']:.2%}")
                print(f"  Cache size: {stats['size_mb']:.2f} MB")
                print(f"  File entries: {stats['file_entries']}")
                print(f"  Analysis entries: {stats['analysis_entries']}")
        except ImportError:
            pass
        
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}", exc_info=True)
        sys.exit(1)