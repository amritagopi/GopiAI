# Project Cleanup Analyzer CLI

This document describes how to use the Project Cleanup Analyzer command-line interface and batch script to analyze and clean up the GopiAI project codebase.

## Quick Start

The easiest way to run the analyzer is to use the batch script:

```batch
cd 03_UTILITIES
project_cleanup_analyzer.bat
```

This will analyze the entire GopiAI project and generate a report in the `project_health/reports` directory.

## Batch Script Options

The batch script supports several command-line options:

- `--html`: Generate an HTML report instead of Markdown
- `--json`: Generate a JSON report instead of Markdown
- `--high-only`: Only report high severity issues
- `--medium-up`: Only report medium and high severity issues
- `--detailed`: Enable detailed logging using the GopiAI logging system
- `--sequential`: Run analyzers sequentially (slower but uses less memory)

Example:

```batch
project_cleanup_analyzer.bat --html --medium-up
```

## CLI Script

For more advanced options, you can use the CLI script directly:

```batch
python project_cleanup_cli.py --help
```

### CLI Options

```
usage: project_cleanup_cli.py [-h] [--project-path PROJECT_PATH] [--config CONFIG]
                             [--output OUTPUT] [--format {markdown,json,html}]
                             [--output-name OUTPUT_NAME] [--sequential]
                             [--severity {high,medium,low}] [--include INCLUDE]
                             [--exclude EXCLUDE] [--max-file-size MAX_FILE_SIZE]
                             [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                             [--log-file LOG_FILE] [--detailed-logging]

GopiAI Project Cleanup Analyzer

options:
  -h, --help            show this help message and exit
  --project-path PROJECT_PATH, -p PROJECT_PATH
                        Path to the project root directory (default: parent directory)
  --config CONFIG, -c CONFIG
                        Path to a JSON configuration file
  --output OUTPUT, -o OUTPUT
                        Path to save the report (default: project_health/reports/)
  --format {markdown,json,html}, -f {markdown,json,html}
                        Output format for the report (default: markdown)
  --output-name OUTPUT_NAME
                        Name for the output file (default: cleanup_report_YYYYMMDD_HHMMSS)
  --sequential, -s      Run analyzers sequentially instead of in parallel
  --severity {high,medium,low}
                        Minimum severity level to report (default: low)
  --include INCLUDE     File patterns to include (can be specified multiple times)
  --exclude EXCLUDE     File patterns to exclude (can be specified multiple times)
  --max-file-size MAX_FILE_SIZE
                        Maximum file size in MB to analyze (default: 10)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}, -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: INFO)
  --log-file LOG_FILE   Path to save log file (default: project_cleanup_YYYYMMDD_HHMMSS.log)
  --detailed-logging    Enable detailed logging using GopiAI logging system
```

### Examples

```batch
# Run analysis on a specific module with HTML output
python project_cleanup_cli.py --project-path ../GopiAI-Core --format html

# Run analysis focusing only on Python files
python project_cleanup_cli.py --include "*.py"

# Run analysis with detailed logging and only high severity issues
python project_cleanup_cli.py --detailed-logging --severity high

# Run analysis with a custom configuration file
python project_cleanup_cli.py --config my_config.json
```

## Configuration File

You can provide a JSON configuration file with the `--config` option. The configuration file should have the following structure:

```json
{
  "project_path": "../",
  "exclude_patterns": ["*.pyc", "__pycache__", ".git"],
  "include_patterns": ["*.py", "*.md"],
  "severity_threshold": "medium",
  "output_format": "markdown",
  "detailed_analysis": true,
  "max_file_size_mb": 10
}
```

## Output Management

Reports are saved to the `project_health/reports` directory by default. You can specify a different location with the `--output` option.

The default filename format is `cleanup_report_YYYYMMDD_HHMMSS.{format}`, where `{format}` is `md`, `json`, or `html` depending on the output format.

## Integration with GopiAI Logging

The CLI script integrates with the GopiAI logging system if available. You can enable detailed logging with the `--detailed-logging` option.

## Running Tests

### Basic Tests

To run the tests for the CLI script:

```batch
python -m unittest test_project_cleanup_cli.py
```

### Comprehensive Test Suite

A comprehensive test suite is available to validate all aspects of the Project Cleanup Analyzer:

```batch
run_comprehensive_tests.bat
```

The comprehensive test suite includes:

- Individual analyzer tests
- Integration tests for analyzer combinations
- Regression tests using existing GopiAI modules
- Performance benchmarks for large codebase analysis
- Edge case testing with specially generated test data

### Performance Benchmarks

To run performance benchmarks separately:

```batch
python performance_test.py --project-path <path> --iterations 3
```

This will measure the performance of different configurations (baseline, with caching, with incremental analysis) and report the results.

## Troubleshooting

If you encounter issues:

1. Check the log file for detailed error messages
2. Try running with `--log-level DEBUG` for more verbose output
3. Use `--sequential` if you experience memory issues with parallel analysis
4. Reduce the scope of analysis with `--include` and `--exclude` options