#!/usr/bin/env python
"""
Simple Project Cleanup Analyzer - A simplified version that doesn't rely on complex dependencies
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
import argparse
from typing import Dict, List, Any, Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_cleanup_analyzer.log')
    ]
)

logger = logging.getLogger(__name__)

class SimpleAnalyzer:
    """Base class for simple analyzers."""
    
    def __init__(self, config=None):
        """Initialize the analyzer."""
        self.config = config or {}
        self.results = []
    
    def analyze(self, project_path):
        """Analyze the project."""
        raise NotImplementedError("Subclasses must implement analyze method")
    
    def get_analyzer_name(self):
        """Get the name of the analyzer."""
        return self.__class__.__name__

class ProjectStructureAnalyzer(SimpleAnalyzer):
    """Analyze project structure."""
    
    def analyze(self, project_path):
        """Analyze the project structure."""
        logger.info(f"Analyzing project structure in {project_path}")
        
        results = []
        
        # Get all directories and files
        all_files = []
        all_dirs = []
        
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and files
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                all_dirs.append(dir_path)
        
        # Count files by extension
        extensions = {}
        for file in all_files:
            ext = os.path.splitext(file)[1].lower()
            extensions[ext] = extensions.get(ext, 0) + 1
        
        # Find potential GopiAI modules
        gopiai_modules = [d for d in all_dirs if os.path.basename(d).startswith('GopiAI-')]
        
        # Check for standard directories
        standard_dirs = ['02_DOCUMENTATION', '03_UTILITIES', 'logs', 'conversations']
        for dir_name in standard_dirs:
            if not os.path.isdir(os.path.join(project_path, dir_name)):
                results.append({
                    'category': 'structure',
                    'severity': 'medium',
                    'description': f"Standard directory '{dir_name}' is missing",
                    'file_path': project_path,
                    'recommendation': f"Create the '{dir_name}' directory for project organization"
                })
        
        # Check for GopiAI modules
        if not gopiai_modules:
            results.append({
                'category': 'structure',
                'severity': 'high',
                'description': "No GopiAI modules found",
                'file_path': project_path,
                'recommendation': "Create GopiAI-* modules according to project structure"
            })
        
        return results

class CodeQualityAnalyzer(SimpleAnalyzer):
    """Analyze code quality."""
    
    def analyze(self, project_path):
        """Analyze code quality."""
        logger.info(f"Analyzing code quality in {project_path}")
        
        results = []
        python_files = []
        
        # Find Python files
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        # Analyze a sample of Python files (limit to 100 for speed)
        for py_file in python_files[:100]:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for long lines
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if len(line) > 100:
                        results.append({
                            'category': 'code_quality',
                            'severity': 'low',
                            'description': f"Line {i+1} is too long ({len(line)} characters)",
                            'file_path': py_file,
                            'line_number': i+1,
                            'recommendation': "Keep lines under 100 characters for readability"
                        })
                
                # Check for TODO comments
                for i, line in enumerate(lines):
                    if 'TODO' in line or 'FIXME' in line:
                        results.append({
                            'category': 'code_quality',
                            'severity': 'low',
                            'description': f"TODO/FIXME comment found at line {i+1}",
                            'file_path': py_file,
                            'line_number': i+1,
                            'recommendation': "Address TODO/FIXME comments before release"
                        })
                
                # Check for large functions (more than 50 lines)
                in_function = False
                function_start = 0
                function_name = ""
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith('def ') and line.endswith(':'):
                        in_function = True
                        function_start = i
                        function_name = line[4:line.find('(')]
                    elif in_function and line.startswith('def '):
                        # New function, check the length of the previous one
                        function_length = i - function_start
                        if function_length > 50:
                            results.append({
                                'category': 'code_quality',
                                'severity': 'medium',
                                'description': f"Function '{function_name}' is too long ({function_length} lines)",
                                'file_path': py_file,
                                'line_number': function_start + 1,
                                'recommendation': "Break down large functions into smaller ones"
                            })
                        in_function = True
                        function_start = i
                        function_name = line[4:line.find('(')]
            
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        return results

class SimpleCleanupAnalyzer:
    """Main orchestrator for simple project cleanup analysis."""
    
    def __init__(self, project_path=None, output_format='markdown'):
        """Initialize the analyzer."""
        self.project_path = project_path or os.path.abspath('.')
        self.output_format = output_format
        self.analyzers = [
            ProjectStructureAnalyzer(),
            CodeQualityAnalyzer()
        ]
    
    def run_analysis(self):
        """Run all analyzers and generate a report."""
        logger.info(f"Starting analysis of {self.project_path}")
        
        all_results = []
        
        for analyzer in self.analyzers:
            analyzer_name = analyzer.get_analyzer_name()
            logger.info(f"Running {analyzer_name}")
            
            try:
                results = analyzer.analyze(self.project_path)
                all_results.extend(results)
                logger.info(f"Completed {analyzer_name} - Found {len(results)} issues")
            except Exception as e:
                logger.error(f"Error running {analyzer_name}: {e}")
        
        # Generate report
        return self.generate_report(all_results)
    
    def generate_report(self, results):
        """Generate a report from the analysis results."""
        logger.info("Generating report")
        
        # Create output directory
        output_dir = os.path.join(self.project_path, 'project_health', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        if self.output_format == 'json':
            output_file = os.path.join(output_dir, f"cleanup_report_{timestamp}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        else:
            # Default to markdown
            output_file = os.path.join(output_dir, f"cleanup_report_{timestamp}.md")
            
            # Group results by category
            results_by_category = {}
            for result in results:
                category = result.get('category', 'unknown')
                if category not in results_by_category:
                    results_by_category[category] = []
                results_by_category[category].append(result)
            
            # Generate markdown content
            content = f"""# Project Cleanup Analysis Report

## Overview

Analysis performed on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Project path: {self.project_path}
Total issues found: {len(results)}

## Issues by Category

"""
            
            # Add issues by category
            for category, category_results in results_by_category.items():
                content += f"### {category.title()} Issues\n\n"
                
                # Group by severity
                high = [r for r in category_results if r.get('severity') == 'high']
                medium = [r for r in category_results if r.get('severity') == 'medium']
                low = [r for r in category_results if r.get('severity') == 'low']
                
                if high:
                    content += "#### High Severity\n\n"
                    for result in high:
                        content += self._format_result_markdown(result)
                
                if medium:
                    content += "#### Medium Severity\n\n"
                    for result in medium:
                        content += self._format_result_markdown(result)
                
                if low:
                    content += "#### Low Severity\n\n"
                    for result in low:
                        content += self._format_result_markdown(result)
            
            # Write content to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Report saved to {output_file}")
        return output_file
    
    def _format_result_markdown(self, result):
        """Format a result as markdown."""
        output = f"- **{result.get('description')}**\n"
        output += f"  - File: `{os.path.relpath(result.get('file_path'), self.project_path)}`\n"
        
        if result.get('line_number'):
            output += f"  - Line: {result.get('line_number')}\n"
        
        if result.get('recommendation'):
            output += f"  - Recommendation: {result.get('recommendation')}\n"
        
        output += "\n"
        return output

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Simple Project Cleanup Analyzer')
    
    parser.add_argument(
        '--project-path', '-p',
        type=str,
        default=os.path.abspath('.'),
        help='Path to the project root directory'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format for the report'
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_arguments()
    
    start_time = time.time()
    
    analyzer = SimpleCleanupAnalyzer(
        project_path=args.project_path,
        output_format=args.format
    )
    
    report_path = analyzer.run_analysis()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"Project Cleanup Analysis Complete")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Report saved to: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()