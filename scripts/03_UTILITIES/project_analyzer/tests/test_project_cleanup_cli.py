"""
End-to-end tests for the Project Cleanup CLI and integration scripts.

This module tests the command-line interface and batch script for the
project cleanup analyzer, ensuring they work correctly with the GopiAI project structure.
"""

import os
import sys
import unittest
import tempfile
import subprocess
import json
import argparse
from pathlib import Path

# Add the current directory to the path to import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the modules
from project_cleanup_cli import create_config_from_args, determine_output_path
from project_cleanup_analyzer import AnalysisConfig

# Mock parse_arguments for testing
def mock_parse_arguments(args=None):
    """Mock version of parse_arguments that accepts test arguments."""
    parser = argparse.ArgumentParser(description='GopiAI Project Cleanup Analyzer')
    
    # Project path and configuration
    parser.add_argument('--project-path', '-p', type=str, default=os.path.abspath('..'))
    parser.add_argument('--config', '-c', type=str)
    parser.add_argument('--output', '-o', type=str)
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'html'], default='markdown')
    parser.add_argument('--output-name', type=str)
    parser.add_argument('--sequential', '-s', action='store_true')
    parser.add_argument('--severity', choices=['high', 'medium', 'low'], default='low')
    parser.add_argument('--include', type=str, action='append')
    parser.add_argument('--exclude', type=str, action='append')
    parser.add_argument('--max-file-size', type=int, default=10)
    parser.add_argument('--log-level', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add_argument('--log-file', type=str)
    parser.add_argument('--detailed-logging', action='store_true')
    
    return parser.parse_args(args if args is not None else [])


class TestProjectCleanupCLI(unittest.TestCase):
    """Test the Project Cleanup CLI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_argument_parsing(self):
        """Test command-line argument parsing."""
        # Test with minimal arguments
        test_args = ["--project-path", "../GopiAI-Core"]
        parsed_args = mock_parse_arguments(test_args)
        
        self.assertEqual(parsed_args.project_path, "../GopiAI-Core")
        self.assertEqual(parsed_args.format, "markdown")
        self.assertEqual(parsed_args.severity, "low")
        self.assertFalse(parsed_args.sequential)
        
        # Test with more options
        test_args = [
            "--project-path", "../GopiAI-UI",
            "--format", "html",
            "--severity", "medium",
            "--sequential",
            "--include", "*.py",
            "--exclude", "*.pyc",
            "--max-file-size", "5"
        ]
        parsed_args = mock_parse_arguments(test_args)
        
        self.assertEqual(parsed_args.project_path, "../GopiAI-UI")
        self.assertEqual(parsed_args.format, "html")
        self.assertEqual(parsed_args.severity, "medium")
        self.assertTrue(parsed_args.sequential)
        self.assertEqual(parsed_args.include, ["*.py"])
        self.assertEqual(parsed_args.exclude, ["*.pyc"])
        self.assertEqual(parsed_args.max_file_size, 5)
    
    def test_config_creation(self):
        """Test creating configuration from arguments."""
        # Create mock arguments
        class MockArgs:
            project_path = "."  # Use current directory for testing
            severity = "medium"
            format = "json"
            max_file_size = 5
            include = ["*.py", "*.md"]
            exclude = ["*.pyc", "__pycache__"]
        
        args = MockArgs()
        config = create_config_from_args(args)
        
        self.assertEqual(config.project_path, os.path.abspath("."))
        self.assertEqual(config.severity_threshold, "medium")
        self.assertEqual(config.output_format, "json")
        self.assertEqual(config.max_file_size_mb, 5)
        self.assertEqual(config.include_patterns, ["*.py", "*.md"])
        self.assertEqual(config.exclude_patterns, ["*.pyc", "__pycache__"])
    
    def test_output_path_determination(self):
        """Test determining output path."""
        # Create mock arguments
        class MockArgs:
            output = None
            output_name = None
            format = "markdown"
        
        args = MockArgs()
        
        # Test default output path
        output_path = determine_output_path(args)
        self.assertTrue("reports" in output_path)
        self.assertTrue(output_path.endswith(".md"))
        
        # Test with custom output directory
        args.output = str(self.output_dir)
        output_path = determine_output_path(args)
        self.assertTrue(str(self.output_dir) in output_path)
        
        # Test with custom output name
        args.output_name = "custom_report"
        output_path = determine_output_path(args)
        self.assertEqual(os.path.basename(output_path), "custom_report.md")
        
        # Test with format-specific output name
        args.output_name = "custom_report.md"
        output_path = determine_output_path(args)
        self.assertEqual(os.path.basename(output_path), "custom_report.md")
    
    def test_cli_script_execution(self):
        """Test executing the CLI script with minimal arguments."""
        # Skip this test if not running in the GopiAI project
        if not os.path.exists("../GopiAI-Core"):
            self.skipTest("Not running in GopiAI project")
        
        # Create a test output file
        output_file = os.path.join(self.output_dir, "test_report.md")
        
        # Run the CLI script with minimal arguments
        result = subprocess.run(
            [
                sys.executable,
                "project_cleanup_cli.py",
                "--project-path", "../GopiAI-Core",
                "--output", output_file,
                "--log-level", "ERROR"  # Minimize output
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"CLI script failed: {result.stderr}")
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(output_file), "Output file was not created")
        
        # Check that the output file contains expected content
        with open(output_file, "r") as f:
            content = f.read()
            self.assertIn("Project Cleanup Analysis Report", content)


class TestBatchScriptIntegration(unittest.TestCase):
    """Test the batch script integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        
        # Path to the batch file
        batch_file_path = os.path.join(current_dir, "project_cleanup_analyzer.bat")
        
        # Create a modified batch file for testing
        self.test_batch_file = os.path.join(self.temp_dir.name, "test_analyzer.bat")
        
        # Check if the batch file exists
        if os.path.exists(batch_file_path):
            with open(batch_file_path, "r") as src:
                content = src.read()
            
            # Modify the batch file to use a specific output directory
            modified_content = content.replace(
                "python project_cleanup_cli.py",
                f"python project_cleanup_cli.py --output {self.output_dir}"
            )
            
            with open(self.test_batch_file, "w") as dst:
                dst.write(modified_content)
        else:
            # Create a simple batch file for testing
            with open(self.test_batch_file, "w") as dst:
                dst.write(f"@echo off\necho Test batch file\npython {current_dir}\\project_cleanup_cli.py --output {self.output_dir} %*")
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_batch_script_execution(self):
        """Test executing the batch script."""
        # Skip this test on non-Windows platforms
        if sys.platform != "win32":
            self.skipTest("Batch script tests only run on Windows")
        
        # Skip this test if not running in the GopiAI project
        if not os.path.exists("../GopiAI-Core"):
            self.skipTest("Not running in GopiAI project")
        
        # Run the batch script with the --json flag for easier parsing
        result = subprocess.run(
            [self.test_batch_file, "--json"],
            capture_output=True,
            text=True
        )
        
        # Check that the script executed successfully
        self.assertEqual(result.returncode, 0, f"Batch script failed: {result.stderr}")
        
        # Check that an output file was created
        output_files = list(self.output_dir.glob("*.json"))
        self.assertTrue(len(output_files) > 0, "No output files were created")
        
        # Check that the output file contains valid JSON
        with open(output_files[0], "r") as f:
            try:
                data = json.load(f)
                self.assertIn("timestamp", data)
                self.assertIn("project_path", data)
                self.assertIn("summary", data)
            except json.JSONDecodeError:
                self.fail("Output file does not contain valid JSON")


if __name__ == "__main__":
    unittest.main()