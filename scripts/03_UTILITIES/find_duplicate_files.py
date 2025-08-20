#!/usr/bin/env python3
"""
Find Duplicate Files Script

This script identifies duplicate files in a directory structure based on content.
It can be used to find redundant files that can be removed to clean up a project.

Usage:
    python find_duplicate_files.py [directory]

If no directory is specified, it will analyze the current directory.
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def get_file_hash(file_path: str) -> str:
    """Calculate the MD5 hash of a file's content."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return ""


def find_duplicate_files(directory: str, extensions: Set[str] = None) -> Dict[str, List[str]]:
    """
    Find duplicate files in the directory based on content hash.
    
    Args:
        directory: Directory to search
        extensions: Set of file extensions to include (e.g., {'.py', '.txt'})
                   If None, all files are included
    
    Returns:
        Dictionary mapping content hashes to lists of file paths
    """
    hash_to_files = defaultdict(list)
    
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # Skip if we're only looking for specific extensions
            if extensions and not any(filename.endswith(ext) for ext in extensions):
                continue
            
            # Skip very large files
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB
                continue
            
            file_hash = get_file_hash(file_path)
            if file_hash:
                hash_to_files[file_hash].append(file_path)
    
    # Filter out unique files
    return {h: files for h, files in hash_to_files.items() if len(files) > 1}


def group_by_filename(duplicates: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Group duplicate files by filename to identify files with the same name."""
    filename_groups = defaultdict(list)
    
    for _, file_paths in duplicates.items():
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            filename_groups[filename].append(file_path)
    
    # Filter out unique filenames
    return {name: paths for name, paths in filename_groups.items() if len(paths) > 1}


def main():
    """Main function."""
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Searching for duplicate files in {directory}...")
    
    # Find duplicates by content
    duplicates_by_content = find_duplicate_files(directory)
    
    if not duplicates_by_content:
        print("No duplicate files found.")
        return
    
    # Find duplicates by filename
    duplicates_by_name = group_by_filename(duplicates_by_content)
    
    # Print results
    print("\n=== Duplicate Files by Content ===")
    for file_hash, file_paths in duplicates_by_content.items():
        print(f"\nHash: {file_hash}")
        for path in file_paths:
            print(f"  {path}")
    
    print(f"\nFound {len(duplicates_by_content)} sets of duplicate files by content.")
    
    print("\n=== Duplicate Files by Name ===")
    for filename, file_paths in duplicates_by_name.items():
        print(f"\nFilename: {filename}")
        for path in file_paths:
            print(f"  {path}")
    
    print(f"\nFound {len(duplicates_by_name)} sets of files with the same name.")


if __name__ == "__main__":
    main()