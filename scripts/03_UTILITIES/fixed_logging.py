#!/usr/bin/env python
"""
Fixed logging configuration for Project Cleanup CLI
"""

import os
import sys
import logging
import time

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


def configure_logging(args):
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


def run_analysis(project_path, output_format='markdown', depth='standard', severity='low', sequential=False):
    """
    Run the project cleanup analysis with the specified parameters.
    
    Args:
        project_path: Path to the project to analyze
        output_format: Output format (markdown, json, html)
        depth: Analysis depth (quick, standard, full)
        severity: Minimum severity level (low, medium, high)
        sequential: Whether to run analyzers sequentially
        
    Returns:
        Path to the generated report
    """
    # Create configuration
    config = AnalysisConfig(
        project_path=project_path,
        output_format=output_format,
        severity_threshold=severity,
        analysis_depth=depth
    )
    
    # Create analyzer
    analyzer = ProjectCleanupAnalyzer(config=config)
    
    # Set up basic logging
    setup_logging("INFO")
    
    # Run analysis
    start_time = time.time()
    report_path = analyzer.run_full_analysis(
        parallel=not sequential
    )
    elapsed = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print(f"Project Cleanup Analysis Complete")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Report saved to: {report_path}")
    print("=" * 80)
    
    return report_path


if __name__ == "__main__":
    # Example usage
    run_analysis(
        project_path=os.path.abspath('..'),
        output_format='markdown',
        depth='full',
        severity='low',
        sequential=False
    )