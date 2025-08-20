# GopiAI Testing System Guide

## Overview

This guide provides comprehensive instructions for using the GopiAI testing system, including how to run tests, interpret results, and troubleshoot common issues.

## Quick Start

### Running All Tests
```bash
# Run all tests with the master runner
python run_all_tests.py

# Or use the batch script (Windows)
run_all_tests.bat
```

### Running Specific Test Categories
```bash
# Unit tests only
python test_infrastructure/master_test_runner.py --category unit

# Integration tests only  
python test_infrastructure/master_test_runner.py --category integration

# UI tests only
python test_infrastructure/master_test_runner.py --category ui

# E2E tests only
python test_infrastructure/master_test_runner.py --category e2e

# Performance tests only
python test_infrastructure/master_test_runner.py --category performance

# Security tests only
python test_infrastructure/master_test_runner.py --category security
```

### Running Tests for Specific Modules
```bash
# GopiAI-Core tests
cd GopiAI-Core && python -m pytest tests/

# GopiAI-UI tests
cd GopiAI-UI && python -m pytest tests/

# GopiAI-CrewAI tests
cd GopiAI-CrewAI && python -m pytest tests/
```

## Test Categories

### 1. Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Location**: `GopiAI-*/tests/unit/`
- **Tools**: pytest, unittest
- **Runtime**: Fast (< 30 seconds)

### 2. Integration Tests
- **Purpose**: Test component interactions and API endpoints
- **Location**: `GopiAI-*/tests/integration/`, `tests/memory/`
- **Tools**: pytest, requests, mock services
- **Runtime**: Medium (1-5 minutes)

### 3. UI Tests
- **Purpose**: Test PySide6 GUI components and user interactions
- **Location**: `GopiAI-UI/tests/ui/`
- **Tools**: pytest-qt, QTest
- **Runtime**: Medium (2-10 minutes)

### 4. End-to-End Tests
- **Purpose**: Test complete user scenarios across all services
- **Location**: `tests/e2e/`
- **Tools**: pytest, service orchestration
- **Runtime**: Slow (5-15 minutes)

### 5. Performance Tests
- **Purpose**: Measure system performance and resource usage
- **Location**: `tests/performance/`
- **Tools**: pytest-benchmark, memory profiler
- **Runtime**: Variable (2-30 minutes)

### 6. Security Tests
- **Purpose**: Validate security measures and vulnerability protection
- **Location**: `tests/security/`
- **Tools**: pytest, custom security validators
- **Runtime**: Medium (3-10 minutes)

## Test Results Interpretation

### Test Status Indicators
- ✅ **PASSED**: Test completed successfully
- ❌ **FAILED**: Test failed with assertion error
- ⚠️ **SKIPPED**: Test was skipped (usually due to missing dependencies)
- 🔄 **XFAIL**: Expected failure (known issue)
- ❗ **ERROR**: Test encountered an unexpected error

### Coverage Reports
Coverage reports show which parts of the code are tested:
- **Green**: Well-covered code (>80% coverage)
- **Yellow**: Moderately covered code (50-80% coverage)
- **Red**: Poorly covered code (<50% coverage)

### Performance Metrics
Performance tests report:
- **Response Time**: API endpoint response times
- **Memory Usage**: Peak memory consumption
- **CPU Usage**: Processing time and efficiency
- **Throughput**: Requests per second capacity

## Environment Setup

### Virtual Environments
The testing system uses three isolated environments:

1. **crewai_env**: For CrewAI server and AI components
2. **gopiai_env**: For UI application and core modules
3. **txtai_env**: For legacy memory system (if needed)

### Activating Environments
```bash
# Windows
call crewai_env\Scripts\activate.bat
call gopiai_env\Scripts\activate.bat

# Linux/Mac
source crewai_env/bin/activate
source gopiai_env/bin/activate
```

### Required Services
Some tests require running services:
- **CrewAI API Server**: Port 5051 (for integration/E2E tests)
- **Memory System**: txtai indexing (for memory tests)
- **UI Application**: PySide6 app (for UI/E2E tests)

## Configuration

### Test Configuration Files
- `pytest.ini`: Global pytest configuration
- `GopiAI-*/pytest.ini`: Module-specific configurations
- `test_infrastructure/test_config.py`: Test infrastructure settings

### Environment Variables
Create `.env` file with test-specific settings:
```env
# Test environment settings
GOPIAI_TEST_MODE=true
GOPIAI_LOG_LEVEL=DEBUG
GOPIAI_TEST_DATA_PATH=./test_data
GOPIAI_MOCK_AI_SERVICES=true

# API keys for integration tests (optional)
OPENAI_API_KEY=your_test_key_here
ANTHROPIC_API_KEY=your_test_key_here
```

### Known Issues Configuration
Tests with known issues are marked in:
- `test_infrastructure/known_issues/`: Issue tracking files
- `pytest.ini`: xfail markers for expected failures

## Advanced Usage

### Parallel Test Execution
```bash
# Run tests in parallel (faster execution)
python test_infrastructure/master_test_runner.py --parallel

# Specify number of workers
python test_infrastructure/master_test_runner.py --parallel --workers 4
```

### Filtering Tests
```bash
# Run tests matching pattern
pytest -k "test_api"

# Run tests with specific markers
pytest -m "integration"

# Exclude slow tests
pytest -m "not slow"
```

### Debugging Failed Tests
```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show local variables in tracebacks
pytest -l
```

### Custom Test Reports
```bash
# Generate HTML coverage report
python test_infrastructure/coverage_reporter.py --html

# Generate performance report
python test_infrastructure/master_reporter.py --performance

# Generate failure analysis
python test_infrastructure/failure_analyzer.py
```

## Continuous Integration

### Automated Test Execution
The CI/CD system automatically runs tests on:
- Code commits to main branch
- Pull request creation
- Scheduled daily runs

### CI Configuration Files
- `.github/workflows/`: GitHub Actions workflows
- `ci_cd/azure_pipelines.yml`: Azure DevOps pipeline
- `ci_cd/jenkins_pipeline.groovy`: Jenkins pipeline

### Test Reports in CI
CI systems generate:
- JUnit XML reports for test results
- Coverage reports in multiple formats
- Performance benchmark comparisons
- Security scan results

## Best Practices

### Writing Effective Tests
1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Keep tests independent** - no shared state between tests
4. **Use appropriate fixtures** for test data setup
5. **Mock external dependencies** to ensure test reliability

### Test Maintenance
1. **Update tests when code changes** to maintain accuracy
2. **Remove obsolete tests** that no longer serve a purpose
3. **Refactor duplicate test code** into reusable fixtures
4. **Document complex test scenarios** with clear comments

### Performance Considerations
1. **Use pytest markers** to categorize slow tests
2. **Run fast tests frequently**, slow tests less often
3. **Profile test execution** to identify bottlenecks
4. **Use test parallelization** for independent test suites

## Next Steps

- See [Adding New Tests Guide](ADDING_NEW_TESTS_GUIDE.md) for creating new tests
- See [Test Troubleshooting Guide](TEST_TROUBLESHOOTING_GUIDE.md) for common issues
- See [Test Documentation Generator](TEST_DOCUMENTATION_GENERATOR.md) for automated docs