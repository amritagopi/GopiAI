#!/usr/bin/env python
"""
Fixed Project Cleanup CLI - Command-line interface for the Project Cleanup Analyzer

This module provides a command-line interface for running the project cleanup analyzer
with various options and configurations. It integrates with the GopiAI logging system
and provides detailed output formatting.
"""

import os
import sys
import argparse
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the project cleanup analyzer
from project_cleanup_orchestrator import ProjectCleanupAnalyzer, setup_logging
from project_cleanup_analyzer import AnalysisConfig

# Try to import GopiAI logging system
try:
    from gopiai_detailed_logger import activate_detailed_logging
    GOPIAI_LOGGING_AVAILABLE = True
except ImportError:
    GOPIAI_LOGGING_AVAILABLE = False


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments with extended options.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='GopiAI Project Cleanup Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis on the current project with default settings
  python fixed_cli.py
  
  # Run analysis on a specific project with HTML output
  python fixed_cli.py --project-path ../my-project --format html
  
  # Run analysis with detailed logging and only high severity issues
  python fixed_cli.py --detailed-logging --severity high
  
  # Run analysis with a custom configuration file
  python fixed_cli.py --config my_config.json
  
  # Run analysis focusing only on Python files
  python fixed_cli.py --include "*.py"
        """
    )
    
    # Project path and configuration
    parser.add_argument(
        '--project-path', '-p',
        type=str,
        default=os.path.abspath('..'),
        help='Path to the project root directory (default: parent directory)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to a JSON configuration file'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Path to save the report (default: project_health/reports/)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json', 'html'],
        default='markdown',
        help='Output format for the report (default: markdown)'
    )
    
    parser.add_argument(
        '--output-name',
        type=str,
        help='Name for the output file (default: cleanup_report_YYYYMMDD_HHMMSS)'
    )
    
    # Analysis options
    parser.add_argument(
        '--sequential', '-s',
        action='store_true',
        help='Run analyzers sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--severity',
        choices=['high', 'medium', 'low'],
        default='low',
        help='Minimum severity level to report (default: low)'
    )
    
    parser.add_argument(
        '--include',
        type=str,
        action='append',
        help='File patterns to include (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--exclude',
        type=str,
        action='append',
        help='File patterns to exclude (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--max-file-size',
        type=int,
        default=10,
        help='Maximum file size in MB to analyze (default: 10)'
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
    
    # Logging options
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to save log file (default: project_cleanup_YYYYMMDD_HHMMSS.log)'
    )
    
    parser.add_argument(
        '--detailed-logging',
        action='store_true',
        help='Enable detailed logging using GopiAI logging system'
    )
    
    return parser.parse_args()


def configure_logging(args: argparse.Namespace) -> str:
    """
    Configure logging based on command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Path to the log file
    """
    # Use GopiAI detailed logging if requested and available
    if args.detailed_logging and GOPIAI_LOGGING_AVAILABLE:
        log_level = getattr(logging, args.log_level)
        log_file = activate_detailed_logging(log_level)
        print(f"Using GopiAI detailed logging: {log_file}")
        return log_file
    
    # Otherwise use standard logging
    log_level = args.log_level
    
    # Generate log file name if not specified
    if args.log_file:
        log_file = args.log_file
    else:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        log_file = f"project_cleanup_{timestamp}.log"
    
    # Set up logging with a single argument
    setup_logging(log_level)
    
    # Configure file handler separately
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    return log_file


def create_config_from_args(args: argparse.Namespace) -> AnalysisConfig:
    """
    Create an AnalysisConfig object from command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Analysis configuration
    """
    config_kwargs = {
        'project_path': os.path.abspath(args.project_path),
        'severity_threshold': args.severity,
        'output_format': args.format,
        'max_file_size_mb': args.max_file_size,
        
        # Performance optimization settings
        'enable_caching': not args.no_cache,
        'incremental_analysis': not args.no_incremental,
        'analysis_depth': args.depth,
        'max_files_per_analyzer': args.max_files,
        'memory_threshold_percent': args.memory_threshold
    }
    
    # Add include patterns if specified
    if args.include:
        config_kwargs['include_patterns'] = args.include
    
    # Add exclude patterns if specified
    if args.exclude:
        config_kwargs['exclude_patterns'] = args.exclude
    
    return AnalysisConfig(**config_kwargs)


def determine_output_path(args: argparse.Namespace) -> str:
    """
    Determine the output path for the report.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Output path for the report
    """
    # Use specified output path if provided
    if args.output:
        output_dir = args.output
    else:
        # Default to project_health/reports/ directory
        output_dir = os.path.join(os.path.abspath('..'), 'project_health', 'reports')
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Map format to file extension
    format_extensions = {
        'markdown': '.md',
        'json': '.json',
        'html': '.html'
    }
    extension = format_extensions.get(args.format, '.md')
    
    # Generate filename
    if args.output_name:
        filename = args.output_name
        if not any(filename.endswith(ext) for ext in ['.md', '.json', '.html']):
            filename += extension
    else:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"cleanup_report_{timestamp}{extension}"
    
    return os.path.join(output_dir, filename)


def print_summary(report_path: str, start_time: float, analyzer: ProjectCleanupAnalyzer) -> None:
    """
    Print a summary of the analysis.
    
    Args:
        report_path: Path to the generated report
        start_time: Start time of the analysis
        analyzer: The ProjectCleanupAnalyzer instance
    """
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"Project Cleanup Analysis Complete")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Report saved to: {report_path}")
    
    # Print cache statistics if available
    try:
        if hasattr(analyzer, 'cache') and analyzer.cache:
            stats = analyzer.cache.get_cache_stats()
            print("\nCache Statistics:")
            print(f"  Hit ratio: {stats['hit_ratio']:.2%}")
            print(f"  Cache size: {stats['size_mb']:.2f} MB")
            print(f"  File entries: {stats['file_entries']}")
            print(f"  Analysis entries: {stats['analysis_entries']}")
    except Exception:
        pass
    
    # Print memory usage if available
    try:
        if hasattr(analyzer, 'memory_monitor') and analyzer.memory_monitor:
            stats = analyzer.memory_monitor.get_memory_stats()
            print("\nMemory Usage:")
            print(f"  Current: {stats.get('current_mb', 0):.2f} MB")
            print(f"  Peak: {stats.get('peak_mb', 0):.2f} MB")
    except Exception:
        pass
    
    print("=" * 80)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    start_time = time.time()
    
    # Parse command-line arguments
    args = parse_arguments()
    
    try:
        # Configure logging
        log_file = configure_logging(args)
        
        # Create analyzer
        if args.config:
            analyzer = ProjectCleanupAnalyzer(config_path=args.config)
        else:
            config = create_config_from_args(args)
            analyzer = ProjectCleanupAnalyzer(config=config)
        
        # Determine output path
        output_path = determine_output_path(args)
        
        # Run analysis
        report_path = analyzer.run_full_analysis(
            parallel=not args.sequential,
            output_path=output_path
        )
        
        # Print summary
        print_summary(report_path, start_time, analyzer)
        
        return 0
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}", exc_info=True)
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())