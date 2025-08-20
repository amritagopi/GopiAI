# Project Cleanup Analyzer Infrastructure

This directory contains the core infrastructure for the GopiAI project cleanup analyzer system.

## Files

- **`project_cleanup_analyzer.py`** - Core infrastructure with base classes and data models
- **`test_cleanup_infrastructure.py`** - Comprehensive test suite for the infrastructure
- **`README_CLEANUP_ANALYZER.md`** - This documentation file

## Core Components

### Data Models

#### `AnalysisResult`
Represents a single analysis finding with:
- `category`: Type of issue found
- `severity`: 'high', 'medium', or 'low'
- `description`: Human-readable description
- `file_path`: Path to the file with the issue
- `line_number`: Optional line number
- `recommendation`: Suggested fix or action

#### `AnalysisConfig`
Configuration for analysis runs with:
- `project_path`: Root directory to analyze
- `exclude_patterns`: File patterns to skip (defaults include *.pyc, __pycache__, etc.)
- `include_patterns`: File patterns to analyze (defaults include *.py, *.md, etc.)
- `severity_threshold`: Minimum severity level to report
- `output_format`: 'markdown', 'json', or 'html'
- `detailed_analysis`: Whether to include detailed recommendations
- `max_file_size_mb`: Skip files larger than this size

### Error Handling

#### `AnalysisError`
Custom exception for analysis errors with:
- `analyzer`: Name of the analyzer that failed
- `file_path`: File being analyzed when error occurred
- `error`: Error description
- `original_exception`: Optional wrapped exception
- `timestamp`: When the error occurred

#### `ErrorHandler`
Manages and tracks errors during analysis:
- `handle_error()`: Log and store an error
- `get_error_summary()`: Get count of errors by analyzer
- `has_errors()`: Check if any errors occurred
- `clear_errors()`: Reset error state

### Base Classes

#### `BaseAnalyzer`
Abstract base class for all analyzers with:
- `analyze()`: Abstract method to perform analysis
- `get_analyzer_name()`: Abstract method to return analyzer name
- `should_analyze_file()`: Check if file should be analyzed
- `get_project_files()`: Get list of files to analyze
- `filter_results_by_severity()`: Filter results by severity threshold

## Usage Example

```python
from project_cleanup_analyzer import AnalysisConfig, BaseAnalyzer, AnalysisResult

class MyAnalyzer(BaseAnalyzer):
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        results = []
        # Perform analysis...
        return self.filter_results_by_severity(results)
    
    def get_analyzer_name(self) -> str:
        return "My Custom Analyzer"

# Use the analyzer
config = AnalysisConfig(project_path="/path/to/project")
analyzer = MyAnalyzer(config)
results = analyzer.analyze("/path/to/project")
```

## Testing

Run the test suite to verify the infrastructure:

```bash
cd 03_UTILITIES
python test_cleanup_infrastructure.py
```

The test suite covers:
- Data model validation
- Configuration validation
- Error handling
- File filtering
- Severity filtering
- Base analyzer functionality

## Next Steps

This infrastructure provides the foundation for implementing specific analyzers:
- StructureAnalyzer
- CodeQualityAnalyzer  
- DeadCodeAnalyzer
- FileAnalyzer
- DependencyAnalyzer
- DuplicateAnalyzer
- ConflictAnalyzer
- DocumentationAnalyzer
- ReportGenerator

Each analyzer will inherit from `BaseAnalyzer` and implement the required abstract methods.