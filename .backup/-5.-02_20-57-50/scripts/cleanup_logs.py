#!/usr/bin/env python
"""
Script for cleaning old logs in the GopiAI/logs directory.
Keeps only the specified number of most recent log files.
"""

import os
import sys
import glob
import argparse
from datetime import datetime
from pathlib import Path


def cleanup_logs(logs_dir, keep_last=20, dry_run=False):
    """
    Cleans old log files, keeping only the specified number of most recent ones.

    Args:
        logs_dir: Path to the logs directory
        keep_last: Number of most recent files to keep
        dry_run: If True, only shows which files would be deleted, but doesn't delete them

    Returns:
        Number of deleted files
    """
    # Check if directory exists
    if not os.path.exists(logs_dir) or not os.path.isdir(logs_dir):
        print(f"Error: directory {logs_dir} does not exist")
        return 0

    # Get list of log files
    log_files = []
    for ext in ('.log', '.txt'):
        log_files.extend(glob.glob(os.path.join(logs_dir, f'*{ext}')))

    # If no log files, exit
    if not log_files:
        print(f"No log files found in directory {logs_dir}")
        return 0

    # Sort files by last modification time (from oldest to newest)
    log_files.sort(key=lambda x: os.path.getmtime(x))

    # Determine which files to delete
    files_to_remove = log_files[:-keep_last] if len(log_files) > keep_last else []

    # If no files to delete, exit
    if not files_to_remove:
        print(f"No log files to delete (found {len(log_files)}, keeping {keep_last})")
        return 0

    # Output information about files to be deleted
    print(f"Found {len(log_files)} log files, deleting {len(files_to_remove)}, keeping {keep_last} most recent")

    # Delete files or show which files would be deleted
    removed_count = 0
    for file_path in files_to_remove:
        if dry_run:
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            file_size = os.path.getsize(file_path) / 1024  # in KB
            print(f"[SIMULATION] Delete: {os.path.basename(file_path)} "
                  f"(modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}, "
                  f"size: {file_size:.1f} KB)")
        else:
            try:
                os.remove(file_path)
                removed_count += 1
                if removed_count % 10 == 0:
                    print(f"Deleted {removed_count} files...")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    print(f"Deleted {removed_count} log files" if not dry_run else
          f"[SIMULATION] Would delete {len(files_to_remove)} log files")
    return removed_count


def main():
    """Main function of the script."""
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Cleans old log files, keeping only the specified number of most recent ones.')
    parser.add_argument('--logs-dir', type=str, help='Path to the logs directory')
    parser.add_argument('--keep-last', type=int, default=20, help='Number of most recent files to keep')
    parser.add_argument('--dry-run', action='store_true', help='Only show which files would be deleted, without actually deleting them')

    args = parser.parse_args()

    # If logs directory path is not specified, use default path
    if not args.logs_dir:
        # Determine path to project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        logs_dir = os.path.join(project_root, 'logs')
    else:
        logs_dir = args.logs_dir

    # Clean logs
    cleanup_logs(logs_dir, args.keep_last, args.dry_run)


if __name__ == "__main__":
    main()
