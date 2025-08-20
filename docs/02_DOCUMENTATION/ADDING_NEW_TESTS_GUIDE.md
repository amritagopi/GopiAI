# Adding New Tests Guide

## Overview

This guide explains how to add new tests to the GopiAI testing system, including best practices, conventions, and integration with the existing test infrastructure.

## Test Structure and Organization

### Directory Structure
```
GopiAI-Module/
├── tests/
│   ├── unit/                 # Unit tests
│   │   ├── conftest.py      # Unit test fixtures
│   │   ├── test_*.py        # Unit test files
│   │   └── README.md        # Unit tests documentation
│   ├── integration/         # Integration tests
│   │   ├── conftest.py      # Integration test fixtures
│   │   ├── test_*.py        # Integration test files
│   │   └── README.md        # Integration tests documentation
│   ├── ui/                  # UI tests (GopiAI-UI only)
│   │   ├── conftest.py      # UI test fixtures
│   │   ├── test_*.py        # UI test files
│   │   └── README.md        # UI tests documentation
│   ├── e2e/                 # End-to-end tests
│   ├── performance/         # Performance tests
│   ├── security/            # Security tests
│   └── conftest.py          # Module-level fixtures
```

### Naming Conventions
- **Test files**: `test_<component_name>.py`
- **Test functions**: `test_<functionality>_<expected_outcome>()`
- **Test classes**: `Test<ComponentName>`
- **Fixtures**: `<resource_name>_fixture` or `mock_<service_name>`

## Creating Unit Tests

### Basic Unit Test Template
```python
"""Unit tests for <component_name> module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from gopiai.<module>.<component> import <ComponentClass>
from gopiai.core.exceptions import <RelevantException>


class TestComponentClass:
    """Test suite for ComponentClass."""
    
    def test_component_initialization_success(self):
        """Test that component initializes correctly with valid parameters."""
        # Arrange
        config = {"param1": "value1", "param2": "value2"}
        
        # Act
        component = ComponentClass(config)
        
        # Assert
        assert component.param1 == "value1"
        assert component.param2 == "value2"
        assert component.is_initialized is True
    
    def test_component_method_with_valid_input(self):
        """Test component method with valid input returns expected result."""
        # Arrange
        component = ComponentClass({"param1": "test"})
        input_data = {"key": "value"}
        
        # Act
        result = component.process_data(input_data)
        
        # Assert
        assert result is not None
        assert result["status"] == "success"
        assert "processed_data" in result
    
    def test_component_method_with_invalid_input_raises_exception(self):
        """Test component method with invalid input raises appropriate exception."""
        # Arrange
        component = ComponentClass({"param1": "test"})
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(RelevantException) as exc_info:
            component.process_data(invalid_input)
        
        assert "Invalid input" in str(exc_info.value)
    
    @patch('gopiai.module.component.external_service')
    def test_component_with_mocked_external_service(self, mock_service):
        """Test component behavior with mocked external dependencies."""
        # Arrange
        mock_service.return_value = {"status": "success", "data": "test"}
        component = ComponentClass({"param1": "test"})
        
        # Act
        result = component.call_external_service()
        
        # Assert
        mock_service.assert_called_once()
        assert result["status"] == "success"


@pytest.fixture
def sample_component():
    """Fixture providing a configured component instance."""
    config = {"param1": "test_value", "param2": "another_value"}
    return ComponentClass(config)


def test_component_with_fixture(sample_component):
    """Test using a fixture for component setup."""
    # Act
    result = sample_component.get_status()
    
    # Assert
    assert result == "ready"
```

### Unit Test Best Practices
1. **Test one thing at a time** - each test should verify a single behavior
2. **Use descriptive test names** that explain the scenario and expected outcome
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Mock external dependencies** to isolate the unit under test
5. **Test both success and failure scenarios**
6. **Use fixtures for common test data** and setup

## Creating Integration Tests

### Integration Test Template
```python
"""Integration tests for <component> API endpoints."""

import pytest
import requests
from unittest.mock import patch

from test_infrastructure.service_manager import ServiceManager
from test_infrastructure.fixtures import api_client, test_database


class TestComponentIntegration:
    """Integration tests for component API."""
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Setup required services for integration tests."""
        self.service_manager = ServiceManager()
        self.service_manager.start_crewai_server()
        yield
        self.service_manager.stop_all_services()
    
    def test_api_endpoint_returns_valid_response(self, api_client):
        """Test API endpoint returns valid response structure."""
        # Arrange
        endpoint = "/api/v1/component/status"
        
        # Act
        response = api_client.get(endpoint)
        
        # Assert
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_api_endpoint_with_authentication(self, api_client):
        """Test API endpoint with authentication headers."""
        # Arrange
        endpoint = "/api/v1/component/protected"
        headers = {"Authorization": "Bearer test_token"}
        
        # Act
        response = api_client.get(endpoint, headers=headers)
        
        # Assert
        assert response.status_code == 200
        assert "data" in response.json()
    
    def test_api_endpoint_error_handling(self, api_client):
        """Test API endpoint error handling with invalid input."""
        # Arrange
        endpoint = "/api/v1/component/process"
        invalid_data = {"invalid": "data"}
        
        # Act
        response = api_client.post(endpoint, json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        assert "error" in response.json()
        assert "validation" in response.json()["error"].lower()
    
    @patch('gopiai.crewai.external_ai_service')
    def test_integration_with_mocked_ai_service(self, mock_ai, api_client):
        """Test integration with mocked AI service."""
        # Arrange
        mock_ai.return_value = {"response": "test response"}
        endpoint = "/api/v1/component/ai_query"
        query_data = {"query": "test query"}
        
        # Act
        response = api_client.post(endpoint, json=query_data)
        
        # Assert
        assert response.status_code == 200
        mock_ai.assert_called_once_with("test query")
        assert response.json()["response"] == "test response"
```

## Creating UI Tests

### UI Test Template (pytest-qt)
```python
"""UI tests for <widget_name> component."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from gopiai.ui.widgets.<widget_name> import <WidgetClass>
from test_infrastructure.ui_fixtures import qtbot, mock_theme_manager


class TestWidgetClass:
    """Test suite for WidgetClass UI component."""
    
    def test_widget_initialization(self, qtbot):
        """Test widget initializes with correct default state."""
        # Arrange & Act
        widget = WidgetClass()
        qtbot.addWidget(widget)
        
        # Assert
        assert widget.isVisible()
        assert widget.windowTitle() == "Expected Title"
        assert widget.isEnabled()
    
    def test_widget_button_click_triggers_action(self, qtbot):
        """Test button click triggers expected action."""
        # Arrange
        widget = WidgetClass()
        qtbot.addWidget(widget)
        
        # Act
        qtbot.mouseClick(widget.action_button, Qt.LeftButton)
        
        # Assert
        assert widget.action_performed is True
        assert widget.status_label.text() == "Action completed"
    
    def test_widget_text_input_validation(self, qtbot):
        """Test text input validation and error handling."""
        # Arrange
        widget = WidgetClass()
        qtbot.addWidget(widget)
        
        # Act
        qtbot.keyClicks(widget.text_input, "invalid input")
        qtbot.keyClick(widget.text_input, Qt.Key_Return)
        
        # Assert
        assert widget.error_label.isVisible()
        assert "invalid" in widget.error_label.text().lower()
    
    def test_widget_keyboard_shortcuts(self, qtbot):
        """Test keyboard shortcuts work correctly."""
        # Arrange
        widget = WidgetClass()
        qtbot.addWidget(widget)
        
        # Act
        qtbot.keySequence(widget, "Ctrl+S")
        
        # Assert
        assert widget.save_action_triggered is True
    
    @pytest.mark.slow
    def test_widget_with_long_operation(self, qtbot):
        """Test widget behavior during long-running operations."""
        # Arrange
        widget = WidgetClass()
        qtbot.addWidget(widget)
        
        # Act
        widget.start_long_operation()
        
        # Wait for operation to complete
        qtbot.waitUntil(lambda: widget.operation_completed, timeout=5000)
        
        # Assert
        assert widget.operation_completed is True
        assert widget.progress_bar.value() == 100
```

## Creating Performance Tests

### Performance Test Template
```python
"""Performance tests for <component> functionality."""

import pytest
import time
import psutil
from memory_profiler import profile

from gopiai.<module>.<component> import <ComponentClass>


class TestComponentPerformance:
    """Performance tests for ComponentClass."""
    
    def test_component_response_time_benchmark(self, benchmark):
        """Benchmark component response time."""
        # Arrange
        component = ComponentClass()
        test_data = {"key": "value"}
        
        # Act & Assert
        result = benchmark(component.process_data, test_data)
        assert result is not None
        
        # Performance assertions
        assert benchmark.stats.mean < 0.1  # Less than 100ms average
        assert benchmark.stats.max < 0.5   # Less than 500ms maximum
    
    @pytest.mark.slow
    def test_component_memory_usage(self):
        """Test component memory usage stays within limits."""
        # Arrange
        component = ComponentClass()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Act
        for i in range(1000):
            component.process_data({"iteration": i})
        
        # Assert
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 50  # Less than 50MB increase
    
    def test_component_concurrent_operations(self):
        """Test component performance under concurrent load."""
        import concurrent.futures
        
        # Arrange
        component = ComponentClass()
        num_threads = 10
        operations_per_thread = 100
        
        def worker():
            for i in range(operations_per_thread):
                component.process_data({"thread_op": i})
        
        # Act
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            concurrent.futures.wait(futures)
        end_time = time.time()
        
        # Assert
        total_operations = num_threads * operations_per_thread
        operations_per_second = total_operations / (end_time - start_time)
        
        assert operations_per_second > 100  # At least 100 ops/sec
```

## Test Markers and Categories

### Using pytest Markers
```python
# Mark slow tests
@pytest.mark.slow
def test_long_running_operation():
    pass

# Mark integration tests
@pytest.mark.integration
def test_api_integration():
    pass

# Mark UI tests
@pytest.mark.ui
def test_widget_behavior():
    pass

# Mark tests requiring external services
@pytest.mark.requires_service("crewai_api")
def test_with_crewai_service():
    pass

# Mark known failing tests
@pytest.mark.xfail(reason="Known issue #123")
def test_known_bug():
    pass

# Mark parametrized tests
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_with_parameters(input, expected):
    pass
```

### Custom Markers Configuration
Add to `pytest.ini`:
```ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    ui: marks tests as UI tests
    e2e: marks tests as end-to-end tests
    performance: marks tests as performance tests
    security: marks tests as security tests
    requires_service: marks tests that require external services
```

## Fixtures and Test Data

### Creating Reusable Fixtures
```python
# conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock = Mock()
    mock.query.return_value = {"response": "test response"}
    mock.is_available.return_value = True
    return mock

@pytest.fixture
def test_conversation_data():
    """Test conversation data fixture."""
    return {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "metadata": {"session_id": "test_session"}
    }

@pytest.fixture(scope="session")
def test_database():
    """Session-scoped test database fixture."""
    # Setup
    db = create_test_database()
    yield db
    # Teardown
    db.cleanup()
```

### Using Fixtures in Tests
```python
def test_with_multiple_fixtures(mock_ai_service, test_conversation_data):
    """Test using multiple fixtures."""
    # Arrange
    component = ConversationProcessor(mock_ai_service)
    
    # Act
    result = component.process_conversation(test_conversation_data)
    
    # Assert
    assert result["status"] == "processed"
    mock_ai_service.query.assert_called_once()
```

## Integration with Test Infrastructure

### Using Service Manager
```python
from test_infrastructure.service_manager import ServiceManager

def test_with_services():
    """Test that requires running services."""
    service_manager = ServiceManager()
    
    # Start required services
    service_manager.start_crewai_server()
    service_manager.start_memory_system()
    
    try:
        # Your test code here
        pass
    finally:
        # Cleanup
        service_manager.stop_all_services()
```

### Using Test Configuration
```python
from test_infrastructure.test_config import TestConfig

def test_with_config():
    """Test using centralized configuration."""
    config = TestConfig()
    
    # Access test settings
    api_url = config.get_api_url()
    timeout = config.get_timeout()
    
    # Your test code here
```

## Running and Debugging New Tests

### Running Specific Tests
```bash
# Run specific test file
pytest tests/unit/test_new_component.py

# Run specific test function
pytest tests/unit/test_new_component.py::test_specific_function

# Run tests with specific marker
pytest -m "new_feature"

# Run tests matching pattern
pytest -k "test_new"
```

### Debugging Tests
```bash
# Run with verbose output
pytest -v tests/unit/test_new_component.py

# Stop on first failure
pytest -x tests/unit/test_new_component.py

# Enter debugger on failure
pytest --pdb tests/unit/test_new_component.py

# Show local variables
pytest -l tests/unit/test_new_component.py
```

## Test Documentation

### Documenting Test Modules
```python
"""
Test module for <component_name>.

This module contains unit tests for the <component_name> component,
covering the following functionality:
- Component initialization and configuration
- Data processing and validation
- Error handling and edge cases
- Integration with external services

Test Categories:
- Unit tests: test_<component>_*
- Integration tests: test_<component>_integration_*
- Performance tests: test_<component>_performance_*

Dependencies:
- pytest
- unittest.mock
- <other_dependencies>

Usage:
    pytest tests/unit/test_<component>.py
"""
```

### Documenting Individual Tests
```python
def test_component_processes_valid_data_successfully(self):
    """
    Test that component correctly processes valid input data.
    
    This test verifies that:
    1. Valid input data is accepted without errors
    2. Processing returns expected result structure
    3. All required fields are present in the result
    4. Processing time is within acceptable limits
    
    Given: A component instance with default configuration
    When: Processing valid input data
    Then: Returns success result with processed data
    
    Test Data:
    - Input: {"key": "value", "type": "test"}
    - Expected: {"status": "success", "data": {...}}
    """
```

## Best Practices Summary

### Code Quality
1. **Write clear, descriptive test names**
2. **Keep tests simple and focused**
3. **Use appropriate assertions**
4. **Mock external dependencies**
5. **Clean up resources in teardown**

### Test Organization
1. **Group related tests in classes**
2. **Use consistent naming conventions**
3. **Organize tests by functionality**
4. **Separate unit, integration, and E2E tests**
5. **Use fixtures for common setup**

### Maintenance
1. **Update tests when code changes**
2. **Remove obsolete tests**
3. **Refactor duplicate code**
4. **Document complex test scenarios**
5. **Monitor test performance**

## Next Steps

After creating your tests:
1. Run them locally to ensure they pass
2. Add appropriate markers and documentation
3. Update the test discovery system if needed
4. Consider adding to CI/CD pipeline
5. Update this guide if you discover new patterns

For more information, see:
- [Testing System Guide](TESTING_SYSTEM_GUIDE.md)
- [Test Troubleshooting Guide](TEST_TROUBLESHOOTING_GUIDE.md)
- [Test Documentation Generator](TEST_DOCUMENTATION_GENERATOR.md)