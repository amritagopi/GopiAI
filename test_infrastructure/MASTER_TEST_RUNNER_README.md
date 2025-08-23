# Enhanced Master Test Runner

The Enhanced Master Test Runner provides a single entry point for running all types of tests across the GopiAI project with advanced features including parallel execution, test prioritization, and automatic retry mechanisms.

## 🚀 Key Features

### Single Entry Point
- **Unified Interface**: One command to run all test types
- **Smart Defaults**: Intelligent configuration that works out of the box
- **Cross-Platform**: Works on Windows, Linux, and macOS

### Parallel Execution
- **Independent Test Execution**: Tests run in parallel when possible
- **Dependency Management**: Respects test dependencies and execution order
- **Configurable Workers**: Adjust parallel worker count based on system resources
- **Thread-Safe Results**: Safe concurrent execution with proper synchronization

### Test Prioritization
- **Priority-Based Execution**: Critical tests run first
- **Smart Ordering**: Important functionality tested before optional features
- **Configurable Priorities**: Customize test importance levels
- **Dependency-Aware**: Maintains logical test execution order

### Automatic Retry
- **Transient Failure Handling**: Automatically retries unstable tests
- **Exponential Backoff**: Intelligent retry delays with jitter
- **Configurable Limits**: Set maximum retry attempts per test
- **Retry Statistics**: Track retry success rates and patterns

### Comprehensive Reporting
- **Detailed Results**: Complete execution statistics and metrics
- **Priority Breakdown**: Results organized by test priority levels
- **Retry Analysis**: Statistics on retry attempts and success rates
- **Multiple Formats**: JSON reports, HTML dashboards, and console output

## 📋 Usage

### Basic Usage

```bash
# Run all tests with smart defaults (fast, parallel, with retry)
python run_all_tests.py

# Run specific test categories
python run_all_tests.py --unit
python run_all_tests.py --integration
python run_all_tests.py --ui
python run_all_tests.py --e2e
python run_all_tests.py --performance
python run_all_tests.py --security
```

### Execution Modes

```bash
# Fast mode - critical tests only
python run_all_tests.py --fast

# Full mode - all test categories
python run_all_tests.py --full

# Sequential execution (better for debugging)
python run_all_tests.py --sequential

# Custom parallel workers
python run_all_tests.py --max-workers 8
```

### Advanced Options

```bash
# Disable retry mechanism
python run_all_tests.py --no-retry

# Custom retry configuration
python run_all_tests.py --max-retries 5 --retry-delay 2.0

# Disable test prioritization
python run_all_tests.py --no-prioritize

### Discovery and Reporting

```bash
# Discover tests without running them
python run_all_tests.py --discover-only

# Discover problems only
python run_all_tests.py --problems-only

# Skip comprehensive reports
python run_all_tests.py --no-reports
```

## 🎯 Test Prioritization

Tests are automatically prioritized based on importance:

### Critical Priority
- Core functionality tests (`test_interfaces`, `test_exceptions`, `test_schema`)
- API server tests (`test_api_server`)
- Main application tests (`test_main_window`)

### High Priority
- Integration tests
- Authentication tests
- Model switching tests
- Memory system tests

### Medium Priority
- UI component tests
- Settings and configuration tests
- Theme and layout tests

### Low Priority
- Performance benchmarks
- Load tests
- Optional feature tests

## 🔄 Retry Mechanism

The automatic retry system handles transient failures:

### Retry Triggers
- Exit codes: 1 (general error), 2 (timeout), 130 (interrupted)
- Network-related failures
- Resource contention issues
- Temporary service unavailability

### Retry Strategy
- **Exponential Backoff**: Delays increase with each retry (1s, 2s, 4s, ...)
- **Jitter**: Random delay component to avoid thundering herd
- **Maximum Attempts**: Configurable limit (default: 3 retries)
- **Smart Filtering**: Only retry tests likely to succeed on retry

### Retry Statistics
- Track which tests required retries
- Monitor retry success rates
- Identify consistently unstable tests
- Generate retry analysis reports

## ⚡ Parallel Execution

The parallel execution system maximizes efficiency while maintaining correctness:

### Dependency Management
- **Automatic Detection**: Discovers test dependencies
- **Execution Ordering**: Ensures dependencies run before dependents
- **Parallel Groups**: Independent tests run simultaneously
- **Deadlock Prevention**: Detects and resolves circular dependencies

### Worker Management
- **Configurable Pool Size**: Adjust based on system resources
- **Load Balancing**: Distributes work evenly across workers
- **Resource Monitoring**: Prevents system overload
- **Graceful Shutdown**: Clean termination on interruption

### Thread Safety
- **Synchronized Results**: Thread-safe result collection
- **Atomic Operations**: Prevent race conditions
- **Shared State Management**: Safe access to shared resources
- **Exception Handling**: Proper error propagation

## 📊 Reporting and Analysis

### Execution Reports
- **Summary Statistics**: Pass/fail rates, execution times, retry counts
- **Priority Breakdown**: Results organized by test priority
- **Environment Analysis**: Results by test environment
- **Category Metrics**: Performance by test category

### Problem Discovery Integration
- **Known Issues**: Automatic detection of existing problems
- **Pytest Markers**: Generate markers for known failing tests
- **Trend Analysis**: Track problem resolution over time
- **Root Cause Analysis**: Identify common failure patterns

### Output Formats
- **Console Output**: Real-time progress and summary
- **JSON Reports**: Machine-readable detailed results
- **HTML Dashboards**: Interactive visual reports
- **Log Files**: Detailed execution logs for debugging

## 🔧 Configuration

### Environment Variables
```bash
# Set default test timeout
export GOPIAI_TEST_TIMEOUT=600

# Set default worker count
export GOPIAI_TEST_WORKERS=4

# Enable debug logging
export GOPIAI_TEST_DEBUG=1
```

### Configuration Files
- `pytest.ini`: Per-module pytest configuration
- `test_config.json`: Global test infrastructure settings
- `problem_discovery_report.json`: Known issues database

## 🏗️ Architecture

### Core Components

#### MasterTestRunner
- Main orchestration class
- Manages test discovery, execution, and reporting
- Handles parallel execution and retry logic

#### TestDiscovery
- Discovers tests across all GopiAI modules
- Categorizes tests by type and priority
- Identifies dependencies and requirements

#### RetryConfig
- Configures retry behavior
- Manages retry delays and limits
- Tracks retry statistics

#### ServiceManager
- Manages test service dependencies
- Starts/stops required services
- Monitors service health

### Execution Flow

1. **Discovery Phase**
   - Discover all available tests
   - Categorize by type and priority
   - Identify dependencies

2. **Planning Phase**
   - Create execution plan
   - Sort by priority and dependencies
   - Prepare parallel execution groups

3. **Execution Phase**
   - Execute tests in priority order
   - Handle parallel execution
   - Manage retries for failed tests

4. **Reporting Phase**
   - Collect and analyze results
   - Generate comprehensive reports
   - Update problem discovery database

## 🐛 Troubleshooting

### Common Issues

#### Tests Not Discovered
- Check that test files follow naming conventions (`test_*.py`)
- Ensure test directories exist in GopiAI modules
- Verify Python path includes test infrastructure

#### Parallel Execution Issues
- Reduce worker count if system resources are limited
- Use `--sequential` for debugging
- Check for resource contention in logs

#### Retry Failures
- Review retry statistics in reports
- Adjust retry limits and delays
- Identify consistently failing tests

#### Environment Problems
- Verify virtual environments are properly set up
- Check Python executable paths
- Ensure required dependencies are installed

### Debug Mode
```bash
# Enable verbose logging
python run_all_tests.py --verbose

# Run in sequential mode for easier debugging
python run_all_tests.py --sequential --verbose

# Disable retry to see original failures
python run_all_tests.py --no-retry --verbose
```

## 📈 Performance Optimization

### System Resources
- **CPU**: Use `--max-workers` to match CPU cores
- **Memory**: Monitor memory usage during parallel execution
- **I/O**: Consider SSD storage for faster test execution

### Test Optimization
- **Fast Tests First**: Prioritization ensures quick feedback
- **Parallel Groups**: Independent tests run simultaneously
- **Smart Retry**: Only retry tests likely to succeed

### Monitoring
- Track execution times and resource usage
- Identify slow tests for optimization
- Monitor retry patterns for stability issues

## 🔮 Future Enhancements

### Planned Features
- **Distributed Execution**: Run tests across multiple machines
- **Smart Test Selection**: Run only tests affected by code changes
- **Machine Learning**: Predict test failures and optimize execution
- **Real-time Monitoring**: Live dashboard during test execution

### Integration Opportunities
- **CI/CD Integration**: Enhanced pipeline integration
- **IDE Integration**: Direct integration with development environments
- **Notification Systems**: Real-time alerts for test failures
- **Metrics Collection**: Long-term trend analysis and reporting

## 📚 API Reference

### MasterTestRunner Class

```python
class MasterTestRunner:
    def __init__(self, root_path: str = ".", max_workers: int = 4, retry_config: RetryConfig = None)
    
    def run_all_tests(self, categories: List[TestCategory] = None, 
                     environments: List[TestEnvironment] = None,
                     parallel: bool = True, prioritize: bool = True,
                     enable_retry: bool = True, generate_reports: bool = True) -> Dict
    
    def run_unit_tests(self, **kwargs) -> Dict
    def run_integration_tests(self, **kwargs) -> Dict
    def run_ui_tests(self, **kwargs) -> Dict
    def run_e2e_tests(self, **kwargs) -> Dict
    def run_performance_tests(self, **kwargs) -> Dict
    def run_security_tests(self, **kwargs) -> Dict
```

### RetryConfig Class

```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    retry_on_exit_codes: List[int] = None
```

### TestExecution Class

```python
@dataclass
class TestExecution:
    module: str
    category: str
    environment: str
    command: str
    result: TestResult
    duration: float
    output: str
    error_output: str
    exit_code: int
    retry_count: int = 0
    priority: TestPriority = TestPriority.MEDIUM
    dependencies: List[str] = None
```

## 📄 License

This enhanced master test runner is part of the GopiAI project and follows the same licensing terms.