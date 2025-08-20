"""
Test Data Generator for Project Cleanup Analyzer

This script generates test data for validating the Project Cleanup Analyzer.
It creates test projects with known issues for validation and testing.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_project_generator import TestProjectGenerator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Generate test data for Project Cleanup Analyzer')
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./test_projects',
        help='Directory where test projects will be created'
    )
    
    parser.add_argument(
        '--project-name', '-n',
        type=str,
        default='test_project',
        help='Name of the test project'
    )
    
    parser.add_argument(
        '--issue-types', '-i',
        nargs='+',
        choices=['structure', 'code_quality', 'dead_code', 'duplicate', 'dependency', 'documentation', 'conflict', 'edge_case', 'all'],
        default=['all'],
        help='Types of issues to include in the test project'
    )
    
    parser.add_argument(
        '--large-codebase', '-l',
        action='store_true',
        help='Generate a large codebase for performance testing'
    )
    
    parser.add_argument(
        '--modules', '-m',
        type=int,
        default=5,
        help='Number of modules to create for large codebase'
    )
    
    parser.add_argument(
        '--files-per-module', '-f',
        type=int,
        default=20,
        help='Number of files per module for large codebase'
    )
    
    parser.add_argument(
        '--lines-per-file', '-lf',
        type=int,
        default=200,
        help='Average number of lines per file for large codebase'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level'
    )
    
    return parser.parse_args()


def setup_logging(log_level):
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('generate_test_data.log')
        ]
    )


def main():
    """Main function."""
    args = parse_arguments()
    setup_logging(args.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Generating test data in {args.output_dir}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test project generator
    generator = TestProjectGenerator(output_dir)
    
    # Create test project
    project_path = generator.create_project(args.project_name)
    logger.info(f"Created test project at {project_path}")
    
    # Add issues based on command-line arguments
    issue_types = args.issue_types
    if 'all' in issue_types:
        issue_types = ['structure', 'code_quality', 'dead_code', 'duplicate', 'dependency', 'documentation', 'conflict', 'edge_case']
    
    for issue_type in issue_types:
        logger.info(f"Adding {issue_type} issues")
        
        if issue_type == 'structure':
            generator.add_structure_issues()
        elif issue_type == 'code_quality':
            generator.add_code_quality_issues()
        elif issue_type == 'dead_code':
            generator.add_dead_code_issues()
        elif issue_type == 'duplicate':
            generator.add_duplicate_code_issues()
        elif issue_type == 'dependency':
            generator.add_dependency_issues()
        elif issue_type == 'documentation':
            generator.add_documentation_issues()
        elif issue_type == 'conflict':
            generator.add_conflict_issues()
        elif issue_type == 'edge_case':
            generator.add_edge_case_files()
    
    # Generate large codebase if requested
    if args.large_codebase:
        logger.info("Generating large codebase for performance testing")
        stats = generator.generate_large_codebase(
            num_modules=args.modules,
            files_per_module=args.files_per_module,
            lines_per_file=args.lines_per_file
        )
        logger.info(f"Generated {stats['total_files']} files with {stats['total_lines']} lines")
    
    logger.info("Test data generation complete")


if __name__ == "__main__":
    main()