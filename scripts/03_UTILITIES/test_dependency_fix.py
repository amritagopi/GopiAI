#!/usr/bin/env python
"""
Test script for dependency analyzer fix
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the dependency analyzer
from dependency_analyzer import DependencyAnalyzer
from project_cleanup_analyzer import AnalysisConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """
    Test the dependency analyzer with a specific file
    """
    print("Starting dependency analyzer test...")
    
    # Create a basic configuration
    config = AnalysisConfig(
        project_path=os.path.abspath('.'),
        enable_caching=False,
        incremental_analysis=False,
        analysis_depth="quick"
    )
    
    print(f"Created configuration with project path: {config.project_path}")
    
    # Create the analyzer
    analyzer = DependencyAnalyzer(config)
    print("Created dependency analyzer")
    
    # Test with a specific requirements.txt file
    test_file_path = '/C:/Users/crazy/.windsurf/extensions/ms-python.python-2025.4.0-universal/python_files/jedilsp_requirements/requirements.txt'
    test_file = Path(test_file_path.replace('/C:', 'C:'))  # Fix path format
    
    print(f"Looking for test file at: {test_file}")
    
    if test_file.exists():
        print(f"Testing with file: {test_file}")
        try:
            analyzer._parse_requirements_txt(test_file)
            print("Successfully parsed the file!")
        except Exception as e:
            print(f"Error parsing file: {e}")
    else:
        print(f"Test file not found: {test_file}")
        
        # Try to find any requirements.txt file
        print("Searching for requirements.txt files...")
        found = False
        for root, _, files in os.walk('.'):
            for file in files:
                if file.lower() == 'requirements.txt':
                    req_file = Path(os.path.join(root, file))
                    print(f"Found requirements.txt: {req_file}")
                    try:
                        analyzer._parse_requirements_txt(req_file)
                        print("Successfully parsed the file!")
                        found = True
                        break
                    except Exception as e:
                        print(f"Error parsing file {req_file}: {e}")
        
        if not found:
            print("No requirements.txt files found in the project.")

if __name__ == "__main__":
    main()