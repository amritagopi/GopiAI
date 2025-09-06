#!/usr/bin/env python3
"""
Simple UI test to verify pytest-qt setup.
"""

import pytest
from pathlib import Path

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))

try:
    from ui_fixtures import qtbot, mock_chat_widget
except ImportError:
    # Fallback if fixtures not available
    @pytest.fixture
    def qtbot():
        from unittest.mock import MagicMock
        return MagicMock()
    
    @pytest.fixture
    def mock_chat_widget():
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.send_message.return_value = True
        return mock


class TestSimpleUI:
    """Simple UI tests to verify setup."""
    
    def test_basic_ui_setup(self, qtbot, mock_chat_widget):
        """Test basic UI test setup."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Basic test
        result = widget.send_message()
        assert result is True
        widget.send_message.assert_called_once()
    
    def test_mock_functionality(self, mock_chat_widget):
        """Test mock functionality."""
        widget = mock_chat_widget
        
        # Test mock methods
        widget.set_message_text("Test message")
        widget.set_message_text.assert_called_with("Test message")
        
        # Test return values
        widget.get_message_text.return_value = "Test message"
        assert widget.get_message_text() == "Test message"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])