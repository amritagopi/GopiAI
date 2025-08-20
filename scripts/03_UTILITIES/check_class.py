import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to read the file directly
file_path = os.path.join(current_dir, 'code_quality_analyzer.py')
print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"File size: {len(content)} bytes")
        print(f"Contains 'class CodeQualityAnalyzer': {'class CodeQualityAnalyzer' in content}")
        
        # Find the class definition
        import re
        match = re.search(r'class\s+(\w+)\s*\(', content)
        if match:
            print(f"Found class: {match.group(1)}")
        else:
            print("No class definition found")