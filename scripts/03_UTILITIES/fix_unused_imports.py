#!/usr/bin/env python3
"""
Fix Unused Imports Script

This script identifies and removes unused imports in Python files.
It uses pyflakes to detect unused imports and modifies the files accordingly.

Usage:
    python fix_unused_imports.py [directory]

If no directory is specified, it will analyze the current directory.
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple


def get_python_files(directory: str) -> List[str]:
    """Get all Python files in the directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def get_unused_imports(file_path: str) -> List[Tuple[int, str]]:
    """Get unused imports in a Python file using pyflakes."""
    try:
        result = subprocess.run(['pyflakes', file_path], 
                               capture_output=True, 
                               text=True)
        
        unused_imports = []
        for line in result.stdout.splitlines():
            match = re.search(r"'(.+)' imported but unused", line)
            if match and ":" in line:
                line_num = int(line.split(':', 1)[0].split(':')[1])
                import_name = match.group(1)
                unused_imports.append((line_num, import_name))
        
        return unused_imports
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []


def fix_unused_imports(file_path: str, unused_imports: List[Tuple[int, str]]) -> bool:
    """Remove unused imports from a Python file."""
    if not unused_imports:
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Group by line number
        imports_by_line = {}
        for line_num, import_name in unused_imports:
            if line_num not in imports_by_line:
                imports_by_line[line_num] = []
            imports_by_line[line_num].append(import_name)
        
        # Process each line with unused imports
        modified = False
        for line_num, imports in imports_by_line.items():
            if line_num <= 0 or line_num > len(lines):
                continue
            
            line = lines[line_num - 1]
            original_line = line
            
            # Handle different import formats
            for import_name in imports:
                # Case 1: from module import name
                if 'from ' in line and ' import ' in line:
                    module = line.split('from ', 1)[1].split(' import ')[0].strip()
                    imports_str = line.split(' import ', 1)[1].strip()
                    
                    # Handle multiple imports on the same line
                    import_items = [i.strip() for i in imports_str.split(',')]
                    if import_name in import_items:
                        import_items.remove(import_name)
                    
                    if not import_items:
                        # Remove the entire line if no imports remain
                        lines[line_num - 1] = ''
                    else:
                        # Reconstruct the line with remaining imports
                        lines[line_num - 1] = f"from {module} import {', '.join(import_items)}\n"
                
                # Case 2: import module
                elif line.strip().startswith('import '):
                    imports_str = line.strip()[7:]  # Remove 'import '
                    import_items = [i.strip() for i in imports_str.split(',')]
                    
                    if import_name in import_items:
                        import_items.remove(import_name)
                    
                    if not import_items:
                        # Remove the entire line if no imports remain
                        lines[line_num - 1] = ''
                    else:
                        # Reconstruct the line with remaining imports
                        lines[line_num - 1] = f"import {', '.join(import_items)}\n"
            
            if lines[line_num - 1] != original_line:
                modified = True
        
        if modified:
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
    
    return False


def main():
    """Main function."""
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    python_files = get_python_files(directory)
    print(f"Found {len(python_files)} Python files")
    
    fixed_files = 0
    for file_path in python_files:
        unused_imports = get_unused_imports(file_path)
        if unused_imports:
            print(f"Found {len(unused_imports)} unused imports in {file_path}")
            if fix_unused_imports(file_path, unused_imports):
                fixed_files += 1
                print(f"Fixed unused imports in {file_path}")
    
    print(f"\nSummary: Fixed unused imports in {fixed_files} files")


if __name__ == "__main__":
    main()