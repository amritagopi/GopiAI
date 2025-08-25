#!/usr/bin/env python3
"""
Pytest configuration and fixtures for GopiAI-UI unit tests.

Provides shared fixtures, test configuration, and setup/teardown logic
for all UI unit tests.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import logging

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
sys.path.append(str(test_infrastructure_path))

# Import test infrastructure fixtures
from ui_fixtures import *
from fixtures import *

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Disable verbose logging during tests
logging.getLogger("PySide6").setLevel(logging.WARNING)
logging.getLogger("Qt").setLevel(logging.WARNING)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment for UI tests."""
    # Ensure QApplication exists for UI tests
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)
    except ImportError:
        # If PySide6 is not available, tests will use mocks
        pass
    
    yield
    
    # Cleanup after all tests
    try:
        if QApplication.instance():
            QApplication.instance().quit()
    except (RuntimeError, AttributeError):
        pass


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test."""
    # This ensures clean state between tests
    yield
    # Cleanup happens automatically with MagicMock


@pytest.fixture
def mock_qt_application():
    """Mock Qt application for tests that don't need real Qt."""
    with patch('PySide6.QtWidgets.QApplication') as mock_app:
        mock_instance = MagicMock()
        mock_app.instance.return_value = mock_instance
        mock_app.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_widget_base():
    """Base mock widget with common Qt widget functionality."""
    mock_widget = MagicMock()
    
    # Common widget properties
    mock_widget.isVisible.return_value = True
    mock_widget.isEnabled.return_value = True
    mock_widget.width.return_value = 400
    mock_widget.height.return_value = 300
    
    # Common widget methods
    mock_widget.show.return_value = None
    mock_widget.hide.return_value = None
    mock_widget.setEnabled.return_value = None
    mock_widget.setVisible.return_value = None
    mock_widget.update.return_value = None
    mock_widget.repaint.return_value = None
    
    return mock_widget


@pytest.fixture
def mock_layout():
    """Mock Qt layout."""
    mock_layout = MagicMock()
    
    # Layout methods
    mock_layout.addWidget.return_value = None
    mock_layout.removeWidget.return_value = None
    mock_layout.count.return_value = 0
    mock_layout.itemAt.return_value = None
    mock_layout.setSpacing.return_value = None
    mock_layout.setContentsMargins.return_value = None
    
    return mock_layout


@pytest.fixture
def mock_signal():
    """Mock Qt signal."""
    mock_signal = MagicMock()
    
    # Signal methods
    mock_signal.connect.return_value = None
    mock_signal.disconnect.return_value = None
    mock_signal.emit.return_value = None
    
    return mock_signal


@pytest.fixture
def mock_timer():
    """Mock Qt timer."""
    mock_timer = MagicMock()
    
    # Timer methods
    mock_timer.start.return_value = None
    mock_timer.stop.return_value = None
    mock_timer.isActive.return_value = False
    mock_timer.interval.return_value = 1000
    mock_timer.setInterval.return_value = None
    mock_timer.setSingleShot.return_value = None
    
    return mock_timer


@pytest.fixture
def mock_event():
    """Mock Qt event."""
    mock_event = MagicMock()
    
    # Event methods
    mock_event.accept.return_value = None
    mock_event.ignore.return_value = None
    mock_event.isAccepted.return_value = True
    mock_event.type.return_value = 1
    
    return mock_event


@pytest.fixture
def mock_painter():
    """Mock Qt painter."""
    mock_painter = MagicMock()
    
    # Painter methods
    mock_painter.begin.return_value = True
    mock_painter.end.return_value = None
    mock_painter.drawText.return_value = None
    mock_painter.drawRect.return_value = None
    mock_painter.fillRect.return_value = None
    mock_painter.setPen.return_value = None
    mock_painter.setBrush.return_value = None
    
    return mock_painter


@pytest.fixture
def mock_font():
    """Mock Qt font."""
    mock_font = MagicMock()
    
    # Font methods
    mock_font.family.return_value = "Arial"
    mock_font.pointSize.return_value = 12
    mock_font.setBold.return_value = None
    mock_font.setItalic.return_value = None
    mock_font.setPointSize.return_value = None
    mock_font.setFamily.return_value = None
    
    return mock_font


@pytest.fixture
def mock_color():
    """Mock Qt color."""
    mock_color = MagicMock()
    
    # Color methods
    mock_color.name.return_value = "#000000"
    mock_color.red.return_value = 0
    mock_color.green.return_value = 0
    mock_color.blue.return_value = 0
    mock_color.alpha.return_value = 255
    mock_color.setRed.return_value = None
    mock_color.setGreen.return_value = None
    mock_color.setBlue.return_value = None
    
    return mock_color


@pytest.fixture
def mock_pixmap():
    """Mock Qt pixmap."""
    mock_pixmap = MagicMock()
    
    # Pixmap methods
    mock_pixmap.width.return_value = 100
    mock_pixmap.height.return_value = 100
    mock_pixmap.isNull.return_value = False
    mock_pixmap.load.return_value = True
    mock_pixmap.save.return_value = True
    mock_pixmap.scaled.return_value = mock_pixmap
    
    return mock_pixmap


@pytest.fixture
def mock_icon():
    """Mock Qt icon."""
    mock_icon = MagicMock()
    
    # Icon methods
    mock_icon.isNull.return_value = False
    mock_icon.pixmap.return_value = MagicMock()
    mock_icon.addFile.return_value = None
    mock_icon.addPixmap.return_value = None
    
    return mock_icon


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file for testing."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "theme": "dark",
        "font_size": 12,
        "auto_save": True,
        "enable_notifications": True
    }
    
    import json
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    return config_file


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        
        yield {
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'open': mock_open
        }


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_anthropic_key',
        'GOOGLE_API_KEY': 'test_google_key',
        'GOPIAI_DEBUG': 'true',
        'GOPIAI_TEST_MODE': 'true'
    }):
        yield


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "ui: UI tests that require Qt widgets"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "requires_display: Tests that require a display"
    )
    config.addinivalue_line(
        "markers", "requires_qt: Tests that require Qt/PySide6"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add ui marker to tests that use qtbot
        if "qtbot" in item.fixturenames:
            item.add_marker(pytest.mark.ui)
        
        # Add integration marker to tests with "integration" in name
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to performance tests
        if "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# Skip tests if dependencies are missing
def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Skip Qt tests if PySide6 is not available
    if item.get_closest_marker("requires_qt"):
        try:
            import PySide6
        except ImportError:
            pytest.skip("PySide6 not available")
    
    # Skip display tests in headless environments
    if item.get_closest_marker("requires_display"):
        if os.environ.get("DISPLAY") is None and os.name != "nt":
            pytest.skip("No display available")


# Custom assertions
def assert_widget_visible(widget):
    """Assert that a widget is visible."""
    assert widget.isVisible(), "Widget should be visible"


def assert_widget_enabled(widget):
    """Assert that a widget is enabled."""
    assert widget.isEnabled(), "Widget should be enabled"


def assert_signal_emitted(signal, timeout=1000):
    """Assert that a signal was emitted."""
    # This would be implemented with QSignalSpy in real Qt tests
    # For mocks, we just check if emit was called
    signal.emit.assert_called()


# Add custom assertions to pytest namespace
pytest.assert_widget_visible = assert_widget_visible
pytest.assert_widget_enabled = assert_widget_enabled
pytest.assert_signal_emitted = assert_signal_emitted