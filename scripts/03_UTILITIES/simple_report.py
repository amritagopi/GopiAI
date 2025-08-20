#!/usr/bin/env python
"""
Simple Project Report Generator
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_report.log')
    ]
)

logger = logging.getLogger(__name__)

def generate_report():
    """
    Generate a simple report about the project
    """
    # Get the project path (current directory)
    project_path = os.path.abspath('.')
    
    # Count files by type
    file_counts = {}
    python_files = []
    
    for root, dirs, files in os.walk(project_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            file_counts[ext] = file_counts.get(ext, 0) + 1
            
            if ext == '.py':
                python_files.append(os.path.join(root, file))
    
    # Count lines of code in Python files
    total_lines = 0
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    for py_file in python_files[:100]:  # Limit to 100 files for speed
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            total_lines += len(lines)
            
            for line in lines:
                line = line.strip()
                if not line:
                    blank_lines += 1
                elif line.startswith('#'):
                    comment_lines += 1
                else:
                    code_lines += 1
        except Exception as e:
            logger.warning(f"Error reading {py_file}: {e}")
    
    # Generate report content
    report_content = f"""# Project Analysis Report

## Overview

Analysis performed on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Project path: {project_path}

## File Statistics

Total files: {sum(file_counts.values())}

### File Types

| Extension | Count |
|-----------|-------|
"""
    
    # Add file extensions
    for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
        report_content += f"| {ext or '(no extension)'} | {count} |\n"
    
    # Add Python code statistics
    report_content += f"""
## Python Code Statistics

- Python files analyzed: {len(python_files[:100])} (limited to 100)
- Total lines: {total_lines}
- Code lines: {code_lines} ({code_lines/total_lines*100:.1f}%)
- Comment lines: {comment_lines} ({comment_lines/total_lines*100:.1f}%)
- Blank lines: {blank_lines} ({blank_lines/total_lines*100:.1f}%)

## Project Structure

### Key Directories

"""
    
    # Add key directories
    for item in os.listdir(project_path):
        if os.path.isdir(os.path.join(project_path, item)) and not item.startswith('.'):
            report_content += f"- {item}/\n"
    
    # Write report to file
    output_file = os.path.join(project_path, "project_analysis_report.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Report saved to {output_file}")
    
    return output_file

if __name__ == "__main__":
    report_path = generate_report()
    print(f"\nReport saved to: {report_path}")