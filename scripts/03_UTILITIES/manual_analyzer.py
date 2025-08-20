#!/usr/bin/env python
"""
Manual Project Analyzer - A simplified version that doesn't rely on complex dependencies
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
import subprocess
import shutil

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('manual_analyzer.log')
    ]
)

logger = logging.getLogger(__name__)

def analyze_project_structure(project_path):
    """
    Analyze the project structure and return a report
    """
    logger.info(f"Analyzing project structure in {project_path}")
    
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
    
    # Generate report
    report = {
        'total_files': len(all_files),
        'total_directories': len(all_dirs),
        'file_extensions': extensions,
        'gopiai_modules': gopiai_modules
    }
    
    return report

def analyze_python_files(project_path):
    """
    Analyze Python files in the project
    """
    logger.info(f"Analyzing Python files in {project_path}")
    
    python_files = []
    large_files = []
    empty_files = []
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip if file is too large
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                if file_size > 10:
                    large_files.append((file_path, file_size))
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if not content.strip():
                        empty_files.append(file_path)
                        continue
                    
                    python_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
    
    # Generate report
    report = {
        'total_python_files': len(python_files),
        'large_files': large_files,
        'empty_files': empty_files
    }
    
    return report

def analyze_dependencies(project_path):
    """
    Analyze project dependencies
    """
    logger.info(f"Analyzing dependencies in {project_path}")
    
    requirements_files = []
    pyproject_files = []
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file == 'requirements.txt':
                requirements_files.append(os.path.join(root, file))
            elif file == 'pyproject.toml':
                pyproject_files.append(os.path.join(root, file))
    
    # Generate report
    report = {
        'requirements_files': requirements_files,
        'pyproject_files': pyproject_files
    }
    
    return report

def generate_report(project_path, structure_report, python_report, dependencies_report):
    """
    Generate a comprehensive report
    """
    logger.info("Generating comprehensive report")
    
    # Create output directory
    output_dir = os.path.join(project_path, 'project_health', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"manual_cleanup_report_{timestamp}.md")
    
    # Generate report content
    report_content = f"""# Project Cleanup Analysis Report

## Overview

Analysis performed on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Project path: {project_path}

## Project Structure

- Total files: {structure_report['total_files']}
- Total directories: {structure_report['total_directories']}

### File Extensions

| Extension | Count |
|-----------|-------|
"""
    
    # Add file extensions
    for ext, count in sorted(structure_report['file_extensions'].items(), key=lambda x: x[1], reverse=True):
        report_content += f"| {ext or '(no extension)'} | {count} |\n"
    
    # Add GopiAI modules
    report_content += "\n### GopiAI Modules\n\n"
    for module in structure_report['gopiai_modules']:
        report_content += f"- {os.path.basename(module)}\n"
    
    # Add Python files analysis
    report_content += f"""
## Python Files Analysis

- Total Python files: {python_report['total_python_files']}
- Large files (>10MB): {len(python_report['large_files'])}
- Empty files: {len(python_report['empty_files'])}

### Large Python Files

| File | Size (MB) |
|------|-----------|
"""
    
    # Add large files
    for file_path, size in python_report['large_files']:
        report_content += f"| {os.path.relpath(file_path, project_path)} | {size:.2f} |\n"
    
    # Add empty files
    report_content += "\n### Empty Python Files\n\n"
    for file_path in python_report['empty_files']:
        report_content += f"- {os.path.relpath(file_path, project_path)}\n"
    
    # Add dependencies analysis
    report_content += f"""
## Dependencies Analysis

- Requirements files: {len(dependencies_report['requirements_files'])}
- Pyproject files: {len(dependencies_report['pyproject_files'])}

### Requirements Files

"""
    
    # Add requirements files
    for file_path in dependencies_report['requirements_files']:
        report_content += f"- {os.path.relpath(file_path, project_path)}\n"
    
    # Add pyproject files
    report_content += "\n### Pyproject Files\n\n"
    for file_path in dependencies_report['pyproject_files']:
        report_content += f"- {os.path.relpath(file_path, project_path)}\n"
    
    # Write report to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Report saved to {output_file}")
    
    return output_file

def main():
    """
    Main function
    """
    # Get the project path (parent directory)
    project_path = os.path.abspath('..')
    
    print(f"Starting manual project analysis for: {project_path}")
    print("This will take some time, please be patient...")
    
    start_time = time.time()
    
    # Analyze project structure
    structure_report = analyze_project_structure(project_path)
    
    # Analyze Python files
    python_report = analyze_python_files(project_path)
    
    # Analyze dependencies
    dependencies_report = analyze_dependencies(project_path)
    
    # Generate report
    report_path = generate_report(project_path, structure_report, python_report, dependencies_report)
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"Project Analysis Complete")
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Report saved to: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()