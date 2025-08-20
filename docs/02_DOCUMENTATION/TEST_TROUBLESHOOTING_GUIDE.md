# Test Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues encountered when running the GopiAI testing system.

## Quick Diagnostics

### Health Check Commands
```bash
# Check overall system health
python test_infrastructure/master_test_runner.py --health-check

# Check service availability
python test_infrastructure/service_manager.py --check-all

# Verify test discovery
python test_infrastructure/test_discovery.py --list-all

# Check environment setup
python -c "import sys; print(f'Python: {sys.version}'); import pytest; print(f'pytest: {pytest.__version__}')"
```

### Quick Fixes
```bash
# Reinstall test dependencies
pip install -r requirements.txt --force-reinstall

# Clear pytest cache
pytest --cache-clear

# Reset test database
python test_infrastructure/fixtures.py --reset-db

# Restart all services
python test_infrastructure/service_manager.py --restart-all
```

## Common Issues and Solutions

### 1. Import Errors

#### Problem: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'gopiai.core'
```

#### Solutions:
```bash
# Install modules in development mode
cd GopiAI-Core && pip install -e .
cd GopiAI-UI && pip install -e .
cd GopiAI-CrewAI && pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify module installation
pip list | grep gopiai
```

#### Problem: Circular import errors
```
ImportError: cannot import name 'X' from partially initialized module
```

#### Solutions:
1. **Check import order** in test files
2. **Use lazy imports** where possible
3. **Refactor circular dependencies** in source code
4. **Use string-based imports** in type hints

```python
# Instead of direct import
from gopiai.ui.main import MainWindow

# Use string-based type hint
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gopiai.ui.main import MainWindow
```

### 2. Service Connection Issues

#### Problem: CrewAI API server not responding
```
ConnectionError: Failed to connect to CrewAI API at http://localhost:5051
```

#### Solutions:
```bash
# Check if server is running
netstat -an | findstr :5051

# Start server manually
cd GopiAI-CrewAI
python crewai_api_server.py

# Check server logs
tail -f GopiAI-CrewAI/crewai_api_server_debug.log

# Use service manager
python test_infrastructure/service_manager.py --start crewai_server
```

#### Problem: Memory system initialization fails
```
RuntimeError: txtai index not found or corrupted
```

#### Solutions:
```bash
# Rebuild txtai index
python -c "from gopiai.memory import rebuild_index; rebuild_index()"

# Clear memory cache
rm -rf rag_memory_system/txtai/cache/*

# Use test memory fixtures
pytest tests/memory/ --use-test-fixtures
```

### 3. UI Test Issues

#### Problem: QApplication already exists
```
RuntimeError: QApplication instance already exists
```

#### Solutions:
```python
# In conftest.py
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Ensure QApplication exists for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here - let pytest handle cleanup

# In test files
def test_widget(qtbot, qapp):
    widget = MyWidget()
    qtbot.addWidget(widget)
```

#### Problem: UI tests hang or timeout
```
TimeoutError: Widget did not become ready within timeout
```

#### Solutions:
```python
# Increase timeout
qtbot.waitUntil(lambda: widget.is_ready(), timeout=10000)  # 10 seconds

# Use explicit waits
qtbot.wait(1000)  # Wait 1 second

# Check widget state
assert widget.isVisible()
assert widget.isEnabled()

# Use processEvents to handle pending events
QApplication.processEvents()
```

### 4. Performance Test Issues

#### Problem: Benchmark tests fail with high variance
```
AssertionError: Benchmark variance too high: 150% > 50%
```

#### Solutions:
```python
# Warm up the system
@pytest.fixture(autouse=True)
def warmup():
    # Run operation once to warm up
    component.process_data({"warmup": True})

# Use more iterations
def test_performance(benchmark):
    result = benchmark.pedantic(
        component.process_data,
        args=(test_data,),
        iterations=100,
        rounds=10
    )

# Set appropriate thresholds
assert benchmark.stats.mean < 0.5  # Adjust based on system
```

#### Problem: Memory leak detection false positives
```
AssertionError: Memory usage increased by 100MB > 50MB threshold
```

#### Solutions:
```python
# Force garbage collection
import gc
gc.collect()

# Use memory profiler decorators
from memory_profiler import profile

@profile
def test_memory_usage():
    # Test code here
    pass

# Monitor specific objects
import tracemalloc
tracemalloc.start()
# Test code
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
```

### 5. Database and Fixture Issues

#### Problem: Test database conflicts
```
sqlite3.OperationalError: database is locked
```

#### Solutions:
```python
# Use separate test database
@pytest.fixture(scope="function")
def test_db():
    db_path = f"test_{uuid.uuid4().hex}.db"
    db = create_database(db_path)
    yield db
    os.unlink(db_path)

# Use in-memory database
db = sqlite3.connect(":memory:")

# Ensure proper cleanup
@pytest.fixture
def db_session():
    session = create_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
```

#### Problem: Fixture dependency issues
```
pytest.FixtureLookupError: fixture 'missing_fixture' not found
```

#### Solutions:
1. **Check fixture scope** - session vs function vs module
2. **Verify fixture location** - conftest.py files
3. **Check import paths** for fixture modules
4. **Use fixture dependencies** correctly

```python
# Correct fixture dependency
@pytest.fixture
def dependent_fixture(base_fixture):
    return base_fixture.create_dependent()

# Check fixture availability
pytest --fixtures test_file.py
```

### 6. Environment and Configuration Issues

#### Problem: Environment variables not loaded
```
KeyError: 'GOPIAI_TEST_MODE'
```

#### Solutions:
```bash
# Create .env file
echo "GOPIAI_TEST_MODE=true" > .env
echo "GOPIAI_LOG_LEVEL=DEBUG" >> .env

# Load environment in conftest.py
import os
from dotenv import load_dotenv

load_dotenv()

# Set default values
os.environ.setdefault('GOPIAI_TEST_MODE', 'true')
```

#### Problem: Virtual environment conflicts
```
ImportError: No module named 'pytest_qt'
```

#### Solutions:
```bash
# Activate correct environment
call gopiai_env\Scripts\activate.bat  # Windows
source gopiai_env/bin/activate        # Linux/Mac

# Install missing dependencies
pip install pytest-qt pytest-benchmark memory-profiler

# Check active environment
which python
pip list
```

### 7. Parallel Execution Issues

#### Problem: Tests fail when run in parallel
```
AssertionError: Resource conflict in parallel execution
```

#### Solutions:
```python
# Use unique resources per test
@pytest.fixture
def unique_port():
    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

# Mark tests that can't run in parallel
@pytest.mark.no_parallel
def test_exclusive_resource():
    pass

# Use file locking for shared resources
import fcntl

def test_with_file_lock():
    with open('test.lock', 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Test code here
```

### 8. CI/CD Integration Issues

#### Problem: Tests pass locally but fail in CI
```
Tests failed in CI environment but pass locally
```

#### Solutions:
1. **Check environment differences**:
   - Python version
   - Operating system
   - Available memory/CPU
   - Network access

2. **Add CI-specific configuration**:
```python
# In conftest.py
import os

@pytest.fixture
def ci_environment():
    return os.environ.get('CI', 'false').lower() == 'true'

def test_with_ci_adjustments(ci_environment):
    timeout = 30 if ci_environment else 10
    # Adjust test behavior for CI
```

3. **Use CI-specific markers**:
```python
@pytest.mark.skipif(os.environ.get('CI'), reason="Skipped in CI")
def test_local_only():
    pass
```

## Debugging Strategies

### 1. Verbose Output
```bash
# Maximum verbosity
pytest -vvv --tb=long

# Show local variables in tracebacks
pytest -l --tb=short

# Show print statements
pytest -s

# Show warnings
pytest --disable-warnings
```

### 2. Selective Test Execution
```bash
# Run only failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Stop on first failure
pytest -x

# Run specific test patterns
pytest -k "test_api and not slow"
```

### 3. Debug Mode
```bash
# Enter debugger on failure
pytest --pdb

# Enter debugger on error
pytest --pdb-trace

# Use custom breakpoints
import pdb; pdb.set_trace()
```

### 4. Logging and Monitoring
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use test-specific logger
logger = logging.getLogger(__name__)
logger.debug("Test checkpoint reached")

# Monitor resource usage
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
print(f"CPU: {psutil.cpu_percent()}%")
```

## Performance Optimization

### 1. Test Execution Speed
```bash
# Profile test execution
pytest --durations=10

# Run tests in parallel
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"
```

### 2. Resource Management
```python
# Use session-scoped fixtures for expensive setup
@pytest.fixture(scope="session")
def expensive_resource():
    resource = create_expensive_resource()
    yield resource
    resource.cleanup()

# Lazy loading of test data
@pytest.fixture
def test_data():
    return lambda: load_test_data()  # Load only when called
```

### 3. Test Isolation
```python
# Reset state between tests
@pytest.fixture(autouse=True)
def reset_state():
    # Reset global state
    GlobalState.reset()
    yield
    # Cleanup after test
    GlobalState.cleanup()
```

## Getting Help

### 1. Log Analysis
```bash
# Check recent logs
ls -la logs/ | tail -10

# Search for errors
grep -i error logs/*.log

# Monitor live logs
tail -f logs/test_runner.log
```

### 2. System Information
```bash
# Generate system report
python test_infrastructure/master_test_runner.py --system-info

# Check dependencies
pip check

# Verify test configuration
python test_infrastructure/test_config.py --validate
```

### 3. Community Resources
- Check existing issues in project repository
- Review test documentation and examples
- Consult pytest documentation for advanced features
- Use debugging tools like pdb, pytest-xdist, pytest-html

### 4. Creating Bug Reports
When reporting test issues, include:
1. **Full error message and traceback**
2. **Test command used**
3. **Environment information** (OS, Python version, dependencies)
4. **Minimal reproduction case**
5. **Expected vs actual behavior**
6. **Relevant log files**

## Prevention Strategies

### 1. Test Hygiene
- **Clean up resources** in test teardown
- **Use appropriate test isolation**
- **Mock external dependencies**
- **Avoid hardcoded values**
- **Use proper assertions**

### 2. Continuous Monitoring
- **Run tests regularly** in CI/CD
- **Monitor test performance** trends
- **Track flaky tests** and fix them
- **Update dependencies** regularly
- **Review test coverage** reports

### 3. Documentation
- **Document test requirements** and setup
- **Maintain troubleshooting knowledge**
- **Update guides** when issues are resolved
- **Share solutions** with team members

## Emergency Procedures

### 1. Complete Test System Reset
```bash
# Stop all services
python test_infrastructure/service_manager.py --stop-all

# Clear all caches
pytest --cache-clear
rm -rf .pytest_cache/
rm -rf __pycache__/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Reset test database
python test_infrastructure/fixtures.py --reset-all

# Restart services
python test_infrastructure/service_manager.py --start-all
```

### 2. Rollback to Known Good State
```bash
# Check git status
git status

# Revert recent changes
git checkout HEAD~1 -- test_file.py

# Run minimal test suite
pytest tests/unit/test_core.py -v
```

### 3. Isolate Problem Area
```bash
# Test each module separately
pytest GopiAI-Core/tests/ -v
pytest GopiAI-UI/tests/ -v
pytest GopiAI-CrewAI/tests/ -v

# Test each category separately
pytest -m unit -v
pytest -m integration -v
pytest -m ui -v
```

This troubleshooting guide should help resolve most common testing issues. For persistent problems, consider creating a minimal reproduction case and consulting the development team.