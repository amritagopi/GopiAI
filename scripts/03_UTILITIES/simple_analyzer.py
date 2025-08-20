#!/usr/bin/env python
"""
Simple script to run the project cleanup analyzer
"""

import os
import sys
import logging
import time
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_analyzer.log')
    ]
)

def main():
    """
    Main function to run the project cleanup analyzer
    """
    # Get the project path (parent directory)
    project_path = os.path.abspath('..')
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_path, 'project_health', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"cleanup_report_{timestamp}.md")
    
    # Print information
    print(f"Analyzing project: {project_path}")
    print(f"Output will be saved to: {output_file}")
    
    # Run analysis using the batch script
    print("\nRunning project_cleanup_analyzer.bat...")
    os.system('cd 03_UTILITIES && project_cleanup_analyzer.bat --full')
    
    print("\nAnalysis complete. Check the output directory for the report.")

if __name__ == "__main__":
    main()