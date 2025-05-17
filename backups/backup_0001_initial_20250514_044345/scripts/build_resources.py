#!/usr/bin/env python
"""
Script for building all resources and cleaning temporary files in GopiAI project.
This script:
1. Generates a set of icons
2. Compiles icon resources
3. Cleans temporary files
"""

import os
import sys
import glob
import subprocess
import argparse
from pathlib import Path
import shutil


def run_script(script_path, args=None):
    """Run a Python script with args"""
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)

    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Errors: {e.stderr}")
        return False


def generate_icons(force=False):
    """Generate icon set"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    icon_script = os.path.join(script_dir, "generate_icon_set.py")

    args = ["--force"] if force else []
    return run_script(icon_script, args)


def compile_resources():
    """Compile resources"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    compile_script = os.path.join(project_root, "compile_icons.py")
    return run_script(compile_script)


def clean_temp_files(dry_run=False):
    """Clean temporary files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Files to clean in root directory
    extensions_to_clean = ['.bak', '.tmp', '.temp', '~']
    temp_prefixes = ['check_', 'fix_', 'temp_', 'test_']

    deleted_files = 0

    # Clean files with specific extensions
    for ext in extensions_to_clean:
        for file_path in glob.glob(os.path.join(project_root, f'*{ext}')):
            if os.path.isfile(file_path):
                if dry_run:
                    print(f"Would delete: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                        deleted_files += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

    # Clean files with specific prefixes
    for prefix in temp_prefixes:
        for file_path in glob.glob(os.path.join(project_root, f'{prefix}*')):
            if os.path.isfile(file_path) and not file_path.endswith('.py'):
                if dry_run:
                    print(f"Would delete: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                        deleted_files += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

    # Clean logs
    logs_dir = os.path.join(project_root, 'logs')
    if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
        logs_script = os.path.join(script_dir, "cleanup_logs.py")
        args = ["--dry-run"] if dry_run else []
        run_script(logs_script, args)

    print(f"Temporary files cleaning complete. Deleted {deleted_files} files.")
    return deleted_files > 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build all resources and clean temporary files')
    parser.add_argument('--icons-only', action='store_true', help='Only generate and compile icons')
    parser.add_argument('--clean-only', action='store_true', help='Only clean temporary files')
    parser.add_argument('--force', action='store_true', help='Force icon regeneration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')

    args = parser.parse_args()

    success = True

    # Build icons
    if not args.clean_only:
        print("\n=== Generating icons ===")
        if not generate_icons(args.force):
            success = False

        print("\n=== Compiling resources ===")
        if not compile_resources():
            success = False

    # Clean temp files
    if not args.icons_only:
        print("\n=== Cleaning temporary files ===")
        clean_temp_files(args.dry_run)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
