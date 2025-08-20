# Test Documentation Generator

## Overview

The Test Documentation Generator is an automated tool that analyzes the GopiAI test suite and generates comprehensive documentation from the source code. It discovers test files, extracts metadata, and creates formatted documentation that stays up-to-date with the codebase.

## Features

- **Automatic Test Discovery**: Finds all test files in the project
- **Metadata Extraction**: Analyzes test functions, classes, and modules
- **Documentation Generation**: Creates formatted Markdown documentation
- **JSON Reports**: Generates machine-readable test inventory
- **Category Classification**: Automatically categorizes tests by type
- **Runtime Estimation**: Provides estimated execution times
- **Fixture Analysis**: Documents available test fixtures

## Usage

### Basic Usage
```bash
# Generate documentation with default settings
python test_infrastructure/test_documentation_generator.py

# Specify custom output file
python test_infrastructure/test_documentation_generator.py --output my_test_docs.md

# Generate JSON report
python test_infrastructure/test_documentation_generator.py --json test_report.json
```

### Command Line Options
```bash
python test_infrastructure/test_documentation_generator.py [OPTIONS]

Options:
  --root PATH          Root directory to scan for tests (default: .)
  --output PATH        Output file for documentation (default: 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md)
  --json PATH          Generate JSON report to specified file
  --list-files         List discovered test files without generating docs
  --help              Show help message
```

### Batch Script
For convenience, use the provided batch script:
```bash
generate_test_documentation.bat
```

This script generates both Markdown documentation and JSON reports.

## Generated Documentation Structure

### Main Documentation File
The generator creates `TEST_SUITE_DOCUMENTATION.md` with the following sections:

1. **Overview**: Summary of the test suite
2. **Test Statistics**: Metrics and category breakdown
3. **Test Modules**: Detailed documentation for each module
4. **Test Fixtures**: Inventory of available fixtures
5. **Running Tests**: Instructions for executing tests
6. **Troubleshooting**: Links to help resources

### JSON Report
The JSON report contains:
- Test file inventory
- Function and class metadata
- Fixture dependencies
- Category classifications
- Runtime estimates
- Generation timestamp

## How It Works

### Test Discovery
The generator scans specific project directories:
- `GopiAI-Core/tests/`
- `GopiAI-UI/tests/`
- `GopiAI-CrewAI/tests/`
- `GopiAI-Assets/tests/`
- `tests/`
- `test_infrastructure/`

It excludes virtual environments and package directories to focus on project-specific tests.

### Code Analysis
For each test file, the generator:
1. **Parses the AST** (Abstract Syntax Tree) to extract structure
2. **Identifies test functions** (starting with `test_`)
3. **Extracts test classes** (starting with `Test`)
4. **Finds fixtures** (decorated with `@pytest.fixture`)
5. **Analyzes imports** and dependencies
6. **Extracts docstrings** and comments

### Metadata Extraction
The generator extracts:
- **Function names** and signatures
- **Docstrings** and descriptions
- **pytest markers** (slow, integration, etc.)
- **Fixture dependencies** from function parameters
- **Complexity estimates** based on code structure
- **Runtime estimates** based on markers and content

### Category Classification
Tests are automatically categorized based on:
- **File path patterns** (unit/, integration/, ui/, etc.)
- **pytest markers** (@pytest.mark.integration)
- **Import patterns** (pytest-qt for UI tests)
- **Naming conventions** (test_api_* for API tests)

## Configuration

### Customizing Discovery
To modify which directories are scanned, edit the `project_dirs` list in the `discover_test_files()` method:

```python
project_dirs = [
    "GopiAI-Core/tests",
    "GopiAI-UI/tests", 
    "GopiAI-CrewAI/tests",
    "GopiAI-Assets/tests",
    "tests",
    "test_infrastructure",
    "my_custom_tests"  # Add custom directories
]
```

### Category Mapping
Customize test categorization by modifying the `category_mapping` dictionary:

```python
self.category_mapping = {
    "unit": ["unit", "test_unit"],
    "integration": ["integration", "test_integration"],
    "ui": ["ui", "test_ui", "gui"],
    "e2e": ["e2e", "end_to_end", "test_e2e"],
    "performance": ["performance", "benchmark", "test_performance"],
    "security": ["security", "test_security"],
    "custom": ["custom", "my_tests"]  # Add custom categories
}
```

### Runtime Estimation
Adjust runtime estimates by modifying the estimation logic:

```python
def _estimate_function_runtime(self, node: ast.FunctionDef, markers: List[str]) -> str:
    if 'slow' in markers or 'performance' in markers:
        return "slow (>30s)"
    elif 'integration' in markers or 'e2e' in markers:
        return "medium (5-30s)"
    else:
        return "fast (<5s)"
```

## Integration with Development Workflow

### Continuous Integration
Add documentation generation to your CI pipeline:

```yaml
# GitHub Actions example
- name: Generate Test Documentation
  run: |
    python test_infrastructure/test_documentation_generator.py
    git add 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md
    git commit -m "Update test documentation" || exit 0
```

### Pre-commit Hooks
Set up automatic documentation updates:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python test_infrastructure/test_documentation_generator.py --quiet
git add 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md
```

### Development Scripts
Include in development workflows:

```bash
# After adding new tests
python test_infrastructure/test_documentation_generator.py
git add 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md
git commit -m "Add new tests and update documentation"
```

## Output Examples

### Module Documentation Example
```markdown
### test_api_endpoints

**File:** `GopiAI-CrewAI/tests/integration/test_api_endpoints.py`
**Category:** Integration
**Tests:** 12
**Estimated Runtime:** medium (5-30s)

**Description:**
Integration tests for CrewAI API endpoints, covering authentication,
error handling, and response validation.

#### Test Functions

| Function | Complexity | Runtime | Markers |
|----------|------------|---------|---------|
| `test_health_endpoint` | simple | fast (<5s) | integration |
| `test_auth_required` | medium | medium (5-30s) | integration, auth |
| `test_error_handling` | complex | medium (5-30s) | integration, error |
```

### Statistics Example
```markdown
## Test Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 842 |
| Total Modules | 60 |
| Total Fixtures | 45 |
| Estimated Runtime | slow (>30m) |

### Tests by Category

| Category | Count | Percentage |
|----------|-------|------------|
| Unit | 425 | 50.5% |
| Integration | 234 | 27.8% |
| UI | 98 | 11.6% |
| E2E | 45 | 5.3% |
| Performance | 25 | 3.0% |
| Security | 15 | 1.8% |
```

## Troubleshooting

### Common Issues

#### Generator Fails to Find Tests
**Problem**: No test files discovered
**Solution**: 
- Check that test files follow naming conventions (`test_*.py`)
- Verify directory structure matches expected paths
- Ensure files are not in excluded directories

#### Parsing Errors
**Problem**: "Error parsing file" messages
**Solution**:
- Check for syntax errors in test files
- Ensure files use valid Python syntax
- Fix any import issues or circular dependencies

#### Incomplete Documentation
**Problem**: Missing test information
**Solution**:
- Add docstrings to test functions and classes
- Use proper pytest markers
- Follow naming conventions for fixtures

### Performance Issues

#### Slow Generation
**Problem**: Documentation generation takes too long
**Solution**:
- Exclude large directories with `--root` option
- Use `--list-files` to check discovery scope
- Consider running on smaller subsets

#### Large Output Files
**Problem**: Generated documentation is too large
**Solution**:
- Filter test discovery to specific modules
- Customize output format to include less detail
- Generate separate documentation for different components

## Extending the Generator

### Adding New Analysis Features
To add new metadata extraction:

1. **Extend the dataclasses** to include new fields
2. **Modify parsing methods** to extract new information
3. **Update documentation templates** to display new data
4. **Add configuration options** for new features

### Custom Output Formats
To support new output formats:

1. **Create new formatter methods** (e.g., `_generate_html_content()`)
2. **Add command line options** for format selection
3. **Implement format-specific templates**
4. **Update the main generation method**

### Integration with Other Tools
The generator can be extended to integrate with:
- **Coverage tools** (pytest-cov) for coverage data
- **Performance tools** (pytest-benchmark) for timing data
- **Quality tools** (pylint, mypy) for code quality metrics
- **CI/CD systems** for automated reporting

## API Reference

### Main Classes

#### `TestDocumentationGenerator`
Main class for generating test documentation.

**Methods:**
- `discover_test_files() -> List[Path]`: Find all test files
- `parse_test_file(file_path: Path) -> TestModule`: Parse a single test file
- `generate_test_suite_documentation(output_path: str) -> TestSuite`: Generate complete documentation
- `generate_json_report(output_path: str) -> Dict[str, Any]`: Generate JSON report

#### Data Classes
- `TestFunction`: Represents a single test function
- `TestClass`: Represents a test class
- `TestModule`: Represents a test module/file
- `TestSuite`: Represents the complete test suite

### Configuration Options
All configuration is done through class attributes and method parameters. See the source code for detailed configuration options.

## Best Practices

### For Test Authors
1. **Write descriptive docstrings** for test functions and classes
2. **Use appropriate pytest markers** to categorize tests
3. **Follow naming conventions** for tests and fixtures
4. **Keep test files organized** in appropriate directories

### For Documentation Maintenance
1. **Regenerate regularly** after adding or modifying tests
2. **Review generated output** for accuracy and completeness
3. **Customize categories** to match your project structure
4. **Integrate with CI/CD** for automatic updates

### For Project Integration
1. **Include in development workflow** as a standard step
2. **Version control generated documentation** for history tracking
3. **Use JSON reports** for programmatic analysis
4. **Link to documentation** from project README and guides

## Related Tools

- **pytest**: Test framework and runner
- **pytest-html**: HTML test reports
- **pytest-cov**: Coverage reporting
- **sphinx**: Documentation generation system
- **mkdocs**: Documentation site generator

For more information, see the [Testing System Guide](TESTING_SYSTEM_GUIDE.md) and [Adding New Tests Guide](ADDING_NEW_TESTS_GUIDE.md).