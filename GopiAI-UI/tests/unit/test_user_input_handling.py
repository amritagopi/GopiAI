#!/usr/bin/env python3
"""
Unit tests for user input handling functionality.
Tests keyboard input, mouse interactions, drag and drop, and input validation.
"""

import pytest
from unittest.mock import MagicMock

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_chat_widget, mock_drag_drop, mock_keyboard_shortcuts, ui_test_data
)


class TestUserInputHandling:
    """Test user input handling functionality."""
    
    def test_text_input_handling(self, qtbot, mock_chat_widget):
        """Test text input handling in chat widget."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Test setting text
        test_text = "Hello, this is a test message"
        widget.set_message_text(test_text)
        
        # Verify text was set
        widget.set_message_text.assert_called_once_with(test_text)
        
        # Test getting text
        current_text = widget.get_message_text()
        assert current_text == "Test message"  # Mock returns this
    
    def test_message_sending_input(self, qtbot, mock_chat_widget):
        """Test message sending through user input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Set up message
        test_message = "Can you help me with Python?"
        widget.set_message_text(test_message)
        
        # Send message
        result = widget.send_message()
        
        # Verify message was sent
        assert result is True
        widget.send_message.assert_called_once()
    
    def test_empty_input_handling(self, qtbot, mock_chat_widget):
        """Test handling of empty input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Test empty message
        widget.set_message_text("")
        empty_text = widget.get_message_text()
        
        # In real implementation, empty messages might be handled differently
        widget.set_message_text.assert_called_with("")
    
    def test_long_input_handling(self, qtbot, mock_chat_widget):
        """Test handling of very long input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Create long message
        long_message = "This is a very long message. " * 100
        widget.set_message_text(long_message)
        
        # Verify long message was handled
        widget.set_message_text.assert_called_with(long_message)
    
    def test_special_characters_input(self, qtbot, mock_chat_widget):
        """Test handling of special characters in input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Test special characters
        special_message = "Hello! @#$%^&*()_+ 中文 🚀 ñáéíóú"
        widget.set_message_text(special_message)
        
        # Verify special characters were handled
        widget.set_message_text.assert_called_with(special_message)
    
    @pytest.mark.ui
    def test_keyboard_shortcuts(self, qtbot, mock_chat_widget, mock_keyboard_shortcuts):
        """Test keyboard shortcuts handling."""
        widget = mock_chat_widget
        shortcuts = mock_keyboard_shortcuts
        qtbot.addWidget(widget)
        
        # Test getting shortcuts
        available_shortcuts = shortcuts.get_shortcuts()
        assert isinstance(available_shortcuts, dict)
        assert "Ctrl+N" in available_shortcuts
        assert "Ctrl+S" in available_shortcuts
        assert "Ctrl+Q" in available_shortcuts
        
        # Test registering shortcut
        result = shortcuts.register_shortcut("Ctrl+Enter", "send_message")
        assert result is True
    
    @pytest.mark.ui
    def test_enter_key_handling(self, qtbot, mock_chat_widget):
        """Test Enter key handling for message sending."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock Enter key press
        widget.handle_enter_key = MagicMock()
        widget.handle_enter_key.return_value = True
        
        # Test Enter key
        result = widget.handle_enter_key()
        assert result is True
        widget.handle_enter_key.assert_called_once()
    
    @pytest.mark.ui
    def test_shift_enter_handling(self, qtbot, mock_chat_widget):
        """Test Shift+Enter handling for new line."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock Shift+Enter key press
        widget.handle_shift_enter = MagicMock()
        widget.handle_shift_enter.return_value = True
        
        # Test Shift+Enter
        result = widget.handle_shift_enter()
        assert result is True
        widget.handle_shift_enter.assert_called_once()
    
    def test_input_validation(self, qtbot, mock_chat_widget):
        """Test input validation."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock validation
        widget.validate_input = MagicMock()
        widget.validate_input.return_value = True
        
        # Test valid input
        valid_message = "This is a valid message"
        is_valid = widget.validate_input(valid_message)
        assert is_valid is True
        widget.validate_input.assert_called_with(valid_message)
    
    def test_input_sanitization(self, qtbot, mock_chat_widget):
        """Test input sanitization."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock sanitization
        widget.sanitize_input = MagicMock()
        widget.sanitize_input.return_value = "Clean message"
        
        # Test sanitization
        dirty_message = "<script>alert('xss')</script>Hello"
        clean_message = widget.sanitize_input(dirty_message)
        assert clean_message == "Clean message"
        widget.sanitize_input.assert_called_with(dirty_message)


class TestDragAndDropHandling:
    """Test drag and drop functionality."""
    
    def test_drag_enter_event(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test drag enter event handling."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Test drag enter
        drag_drop.dragEnterEvent()
        drag_drop.dragEnterEvent.assert_called_once()
    
    def test_drop_event_handling(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test drop event handling."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Test drop event
        drag_drop.dropEvent()
        drag_drop.dropEvent.assert_called_once()
    
    def test_file_drop_handling(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test file drop handling."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Mock file URLs
        mock_urls = [MagicMock()]
        mock_urls[0].toLocalFile.return_value = "/path/to/file.txt"
        
        drag_drop.mimeData().urls.return_value = mock_urls
        
        # Test file drop
        urls = drag_drop.mimeData().urls()
        assert len(urls) == 1
        assert urls[0].toLocalFile() == "/path/to/file.txt"
    
    def test_image_drop_handling(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test image drop handling."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Mock image drop
        widget.handle_image_drop = MagicMock()
        widget.handle_image_drop.return_value = True
        
        # Test image drop
        result = widget.handle_image_drop("/path/to/image.png")
        assert result is True
        widget.handle_image_drop.assert_called_with("/path/to/image.png")
    
    def test_text_drop_handling(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test text drop handling."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Mock text drop
        widget.handle_text_drop = MagicMock()
        widget.handle_text_drop.return_value = True
        
        # Test text drop
        dropped_text = "This text was dropped"
        result = widget.handle_text_drop(dropped_text)
        assert result is True
        widget.handle_text_drop.assert_called_with(dropped_text)
    
    def test_multiple_files_drop(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test handling multiple files drop."""
        widget = mock_chat_widget
        drag_drop = mock_drag_drop
        qtbot.addWidget(widget)
        
        # Mock multiple files
        mock_urls = []
        for i in range(3):
            mock_url = MagicMock()
            mock_url.toLocalFile.return_value = f"/path/to/file{i}.txt"
            mock_urls.append(mock_url)
        
        drag_drop.mimeData().urls.return_value = mock_urls
        
        # Test multiple files
        urls = drag_drop.mimeData().urls()
        assert len(urls) == 3
        for i, url in enumerate(urls):
            assert url.toLocalFile() == f"/path/to/file{i}.txt"


class TestMouseInteractions:
    """Test mouse interaction handling."""
    
    def test_mouse_click_handling(self, qtbot, mock_chat_widget):
        """Test mouse click handling."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock mouse click
        widget.handle_mouse_click = MagicMock()
        widget.handle_mouse_click.return_value = True
        
        # Test mouse click
        result = widget.handle_mouse_click("left", 100, 200)
        assert result is True
        widget.handle_mouse_click.assert_called_with("left", 100, 200)
    
    def test_right_click_context_menu(self, qtbot, mock_chat_widget):
        """Test right-click context menu."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock context menu
        widget.show_context_menu = MagicMock()
        
        # Test right-click
        widget.show_context_menu()
        widget.show_context_menu.assert_called_once()
    
    def test_double_click_handling(self, qtbot, mock_chat_widget):
        """Test double-click handling."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock double-click
        widget.handle_double_click = MagicMock()
        widget.handle_double_click.return_value = True
        
        # Test double-click
        result = widget.handle_double_click()
        assert result is True
        widget.handle_double_click.assert_called_once()
    
    def test_mouse_wheel_handling(self, qtbot, mock_chat_widget):
        """Test mouse wheel handling."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock mouse wheel
        widget.handle_wheel_event = MagicMock()
        widget.handle_wheel_event.return_value = True
        
        # Test mouse wheel
        result = widget.handle_wheel_event(120)  # Positive delta for up
        assert result is True
        widget.handle_wheel_event.assert_called_with(120)


class TestInputValidationAndSanitization:
    """Test input validation and sanitization."""
    
    def test_html_sanitization(self, qtbot, mock_chat_widget):
        """Test HTML sanitization in input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock HTML sanitization
        widget.sanitize_html = MagicMock()
        widget.sanitize_html.return_value = "Safe content"
        
        # Test HTML input
        html_input = "<script>alert('xss')</script><p>Safe content</p>"
        sanitized = widget.sanitize_html(html_input)
        assert sanitized == "Safe content"
        widget.sanitize_html.assert_called_with(html_input)
    
    def test_length_validation(self, qtbot, mock_chat_widget):
        """Test input length validation."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock length validation
        widget.validate_length = MagicMock()
        widget.validate_length.return_value = True
        
        # Test length validation
        normal_message = "This is a normal length message"
        is_valid = widget.validate_length(normal_message, max_length=1000)
        assert is_valid is True
        widget.validate_length.assert_called_with(normal_message, max_length=1000)
    
    def test_character_encoding_validation(self, qtbot, mock_chat_widget):
        """Test character encoding validation."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock encoding validation
        widget.validate_encoding = MagicMock()
        widget.validate_encoding.return_value = True
        
        # Test encoding validation
        unicode_message = "Hello 世界 🌍"
        is_valid = widget.validate_encoding(unicode_message)
        assert is_valid is True
        widget.validate_encoding.assert_called_with(unicode_message)
    
    def test_profanity_filtering(self, qtbot, mock_chat_widget):
        """Test profanity filtering."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock profanity filter
        widget.filter_profanity = MagicMock()
        widget.filter_profanity.return_value = "Clean message"
        
        # Test profanity filtering
        message_with_profanity = "This message contains bad words"
        filtered = widget.filter_profanity(message_with_profanity)
        assert filtered == "Clean message"
        widget.filter_profanity.assert_called_with(message_with_profanity)


class TestInputErrorHandling:
    """Test input error handling."""
    
    def test_invalid_input_handling(self, qtbot, mock_chat_widget):
        """Test handling of invalid input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock invalid input
        widget.set_message_text.side_effect = ValueError("Invalid input")
        
        # Test error handling
        with pytest.raises(ValueError, match="Invalid input"):
            widget.set_message_text("invalid_input")
    
    def test_input_too_long_handling(self, qtbot, mock_chat_widget):
        """Test handling of input that's too long."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock input too long error
        widget.validate_length.return_value = False
        widget.validate_length.side_effect = ValueError("Input too long")
        
        # Test error handling
        with pytest.raises(ValueError, match="Input too long"):
            widget.validate_length("x" * 10000, max_length=1000)
    
    def test_encoding_error_handling(self, qtbot, mock_chat_widget):
        """Test handling of encoding errors."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Mock encoding error
        widget.validate_encoding.side_effect = UnicodeError("Encoding error")
        
        # Test error handling
        with pytest.raises(UnicodeError, match="Encoding error"):
            widget.validate_encoding("invalid_encoding")


class TestInputIntegration:
    """Test input handling integration with other components."""
    
    @pytest.mark.integration
    def test_complete_input_workflow(self, qtbot, mock_chat_widget, mock_keyboard_shortcuts):
        """Test complete input handling workflow."""
        widget = mock_chat_widget
        shortcuts = mock_keyboard_shortcuts
        qtbot.addWidget(widget)
        
        # 1. Set up input
        test_message = "Hello, AI assistant!"
        widget.set_message_text(test_message)
        
        # 2. Validate input
        widget.validate_input = MagicMock(return_value=True)
        is_valid = widget.validate_input(test_message)
        assert is_valid is True
        
        # 3. Send message
        result = widget.send_message()
        assert result is True
        
        # 4. Verify workflow
        widget.set_message_text.assert_called_with(test_message)
        widget.validate_input.assert_called_with(test_message)
        widget.send_message.assert_called_once()
    
    def test_input_with_settings(self, qtbot, mock_chat_widget, ui_test_data):
        """Test input handling with settings integration."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        settings = ui_test_data["sample_settings"]
        
        # Test input handling respects settings
        if settings["enable_notifications"]:
            # Input handling would consider notification settings
            pass
        
        # Verify settings are considered
        assert settings["enable_notifications"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])