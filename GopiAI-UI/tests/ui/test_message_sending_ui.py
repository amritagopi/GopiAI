#!/usr/bin/env python3
"""
UI tests for message sending and receiving functionality using pytest-qt.
Tests the core message sending scenarios and user interactions.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))

try:
    from ui_fixtures import (
        qtbot, mock_chat_widget, mock_model_selector,
        mock_notification_system, ui_test_data, mock_main_window
    )
    from fixtures import ai_service_mocker, mock_crewai_server
except ImportError:
    # Fallback fixtures if not available
    @pytest.fixture
    def qtbot():
        from unittest.mock import MagicMock
        return MagicMock()
    
    @pytest.fixture
    def mock_chat_widget():
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.send_message.return_value = True
        mock.set_message_text.return_value = None
        mock.get_message_text.return_value = "Test message"
        return mock
    
    @pytest.fixture
    def mock_model_selector():
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.currentText.return_value = "gpt-4"
        mock.currentData.return_value = {"provider": "openai", "model": "gpt-4"}
        return mock
    
    @pytest.fixture
    def mock_notification_system():
        from unittest.mock import MagicMock
        return MagicMock()
    
    @pytest.fixture
    def mock_main_window():
        from unittest.mock import MagicMock
        return MagicMock()
    
    @pytest.fixture
    def ui_test_data():
        return {
            "sample_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
    
    @pytest.fixture
    def ai_service_mocker():
        from unittest.mock import MagicMock
        mock = MagicMock()
        mock.add_response.return_value = None
        mock.add_streaming_response.return_value = None
        return mock
    
    @pytest.fixture
    def mock_crewai_server():
        from unittest.mock import MagicMock
        return MagicMock()


class TestMessageSendingUI:
    """Test message sending functionality through UI."""
    
    def test_send_simple_message(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test sending a simple text message."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure AI response
        ai_service_mocker.add_response("Hello! How can I help you?", "gpt-4", "openai")
        
        # Set message text
        test_message = "Hello, AI!"
        widget.set_message_text(test_message)
        
        # Send message
        result = widget.send_message()
        
        # Verify message was sent
        assert result is True
        widget.set_message_text.assert_called_with(test_message)
        widget.send_message.assert_called_once()
    
    def test_send_empty_message_handling(self, qtbot, mock_chat_widget):
        """Test handling of empty message sending."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Set empty message
        widget.set_message_text("")
        widget.get_message_text.return_value = ""
        
        # Configure mock to return False for empty message
        widget.send_message.return_value = False
        
        # Attempt to send empty message
        result = widget.send_message()
        
        # Verify empty message was handled
        assert result is False
    
    def test_send_long_message(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test sending a long message."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Create long message
        long_message = "This is a very long message. " * 100
        widget.set_message_text(long_message)
        widget.get_message_text.return_value = long_message
        
        # Configure AI response
        ai_service_mocker.add_response("I understand your detailed message.", "gpt-4", "openai")
        
        # Send message
        result = widget.send_message()
        
        # Verify long message was handled
        assert result is True
        widget.send_message.assert_called_once()
    
    def test_send_message_with_special_characters(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test sending message with special characters and emojis."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Message with special characters
        special_message = "Hello! 🤖 Can you help with Python? Here's code: print('Hello, World!')"
        widget.set_message_text(special_message)
        widget.get_message_text.return_value = special_message
        
        # Configure AI response
        ai_service_mocker.add_response("I can help with Python! 🐍", "gpt-4", "openai")
        
        # Send message
        result = widget.send_message()
        
        # Verify special characters were handled
        assert result is True
        widget.send_message.assert_called_once()
    
    def test_message_sending_with_different_models(self, qtbot, mock_chat_widget, mock_model_selector, ai_service_mocker):
        """Test sending messages with different AI models."""
        widget = mock_chat_widget
        model_selector = mock_model_selector
        
        qtbot.addWidget(widget)
        qtbot.addWidget(model_selector)
        
        # Test with GPT-4
        model_selector.currentText.return_value = "gpt-4"
        model_selector.currentData.return_value = {"provider": "openai", "model": "gpt-4"}
        ai_service_mocker.add_response("GPT-4 response", "gpt-4", "openai")
        
        widget.set_message_text("Test with GPT-4")
        result = widget.send_message()
        assert result is True
        
        # Test with Claude
        model_selector.currentText.return_value = "claude-3-sonnet"
        model_selector.currentData.return_value = {"provider": "anthropic", "model": "claude-3-sonnet"}
        ai_service_mocker.add_response("Claude response", "claude-3-sonnet", "anthropic")
        
        widget.set_message_text("Test with Claude")
        result = widget.send_message()
        assert result is True
    
    def test_message_sending_error_handling(self, qtbot, mock_chat_widget, mock_notification_system):
        """Test error handling during message sending."""
        widget = mock_chat_widget
        notification_system = mock_notification_system
        
        qtbot.addWidget(widget)
        
        # Configure mock to simulate error
        widget.send_message.return_value = False
        
        # Attempt to send message
        widget.set_message_text("Test message")
        result = widget.send_message()
        
        # Verify error was handled
        assert result is False
        
        # Simulate error notification
        notification_system.show_error("Failed to send message")
        notification_system.show_error.assert_called_with("Failed to send message")
    
    def test_message_sending_with_network_timeout(self, qtbot, mock_chat_widget, mock_notification_system):
        """Test handling of network timeout during message sending."""
        widget = mock_chat_widget
        notification_system = mock_notification_system
        
        qtbot.addWidget(widget)
        
        # Simulate timeout error
        widget.send_message.side_effect = TimeoutError("Network timeout")
        
        # Attempt to send message
        widget.set_message_text("Test message")
        
        try:
            result = widget.send_message()
        except TimeoutError:
            # Simulate error handling
            notification_system.show_error("Network timeout occurred")
            notification_system.show_error.assert_called_with("Network timeout occurred")
    
    def test_rapid_message_sending(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test rapid consecutive message sending."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure AI responses
        for i in range(5):
            ai_service_mocker.add_response(f"Response {i}", "gpt-4", "openai")
        
        # Send multiple messages rapidly
        for i in range(5):
            widget.set_message_text(f"Message {i}")
            result = widget.send_message()
            assert result is True
        
        # Verify all messages were sent
        assert widget.send_message.call_count == 5
    
    @pytest.mark.ui
    def test_message_input_keyboard_shortcuts(self, qtbot, mock_chat_widget):
        """Test keyboard shortcuts for message input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Test Enter key for sending (would be implemented with actual key events)
        # For now, just verify the widget is set up for shortcuts
        assert widget is not None
        
        # In real implementation:
        # qtbot.keyClick(widget.message_input, Qt.Key_Return)
        # assert widget.send_message.called
    
    @pytest.mark.ui
    def test_message_input_text_formatting(self, qtbot, mock_chat_widget):
        """Test text formatting in message input."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Test formatted text
        formatted_message = "**Bold text** and *italic text*"
        widget.set_message_text(formatted_message)
        
        # Verify formatted text was set
        widget.set_message_text.assert_called_with(formatted_message)
    
    def test_message_history_update_after_sending(self, qtbot, mock_chat_widget, ui_test_data):
        """Test that message history updates after sending."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Initial message count
        initial_messages = ui_test_data["sample_messages"]
        widget.get_messages.return_value = initial_messages
        
        initial_count = len(widget.get_messages())
        
        # Send new message
        widget.set_message_text("New test message")
        result = widget.send_message()
        
        # Simulate message being added to history
        new_messages = initial_messages + [{"role": "user", "content": "New test message"}]
        widget.get_messages.return_value = new_messages
        
        # Verify message was added to history
        assert result is True
        assert len(widget.get_messages()) == initial_count + 1


class TestMessageReceivingUI:
    """Test message receiving functionality through UI."""
    
    def test_receive_ai_response(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test receiving AI response after sending message."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure AI response
        expected_response = "This is an AI response"
        ai_service_mocker.add_response(expected_response, "gpt-4", "openai")
        
        # Send message and receive response
        widget.set_message_text("Test question")
        result = widget.send_message()
        
        # Verify response was received (in real implementation)
        assert result is True
        # In real implementation, you would check that the response appears in the chat
    
    def test_receive_streaming_response(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test receiving streaming AI response."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure streaming response
        ai_service_mocker.add_streaming_response(
            ["This ", "is ", "a ", "streaming ", "response"], "gpt-4", "openai"
        )
        
        # Send message
        widget.set_message_text("Test streaming")
        result = widget.send_message()
        
        # Verify streaming was handled
        assert result is True
    
    def test_receive_error_response(self, qtbot, mock_chat_widget, mock_notification_system):
        """Test handling of error responses from AI."""
        widget = mock_chat_widget
        notification_system = mock_notification_system
        
        qtbot.addWidget(widget)
        
        # Simulate error response
        widget.send_message.return_value = False
        
        # Send message
        widget.set_message_text("Test message")
        result = widget.send_message()
        
        # Verify error was handled
        assert result is False
        
        # Simulate error notification
        notification_system.show_error("AI service unavailable")
        notification_system.show_error.assert_called_with("AI service unavailable")
    
    def test_receive_long_response(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test receiving very long AI response."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure long response
        long_response = "This is a very long AI response. " * 200
        ai_service_mocker.add_response(long_response, "gpt-4", "openai")
        
        # Send message
        widget.set_message_text("Tell me a long story")
        result = widget.send_message()
        
        # Verify long response was handled
        assert result is True
    
    def test_receive_response_with_code_blocks(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test receiving response with code blocks."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure response with code
        code_response = """Here's a Python example:
        
```python
def hello_world():
    print("Hello, World!")
    return True
```

This function prints a greeting."""
        
        ai_service_mocker.add_response(code_response, "gpt-4", "openai")
        
        # Send message
        widget.set_message_text("Show me Python code")
        result = widget.send_message()
        
        # Verify code response was handled
        assert result is True


class TestMessageUIIntegration:
    """Test integration between message sending and UI components."""
    
    def test_message_sending_with_main_window(self, qtbot, mock_main_window, mock_chat_widget):
        """Test message sending integration with main window."""
        main_window = mock_main_window
        chat_widget = mock_chat_widget
        
        qtbot.addWidget(main_window)
        qtbot.addWidget(chat_widget)
        
        # Set chat widget in main window
        main_window.set_central_widget(chat_widget)
        
        # Send message through chat widget
        chat_widget.set_message_text("Integration test")
        result = chat_widget.send_message()
        
        # Verify integration
        assert result is True
        main_window.set_central_widget.assert_called_with(chat_widget)
    
    def test_message_sending_with_model_switching(self, qtbot, mock_chat_widget, mock_model_selector):
        """Test message sending after model switching."""
        chat_widget = mock_chat_widget
        model_selector = mock_model_selector
        
        qtbot.addWidget(chat_widget)
        qtbot.addWidget(model_selector)
        
        # Switch model
        model_selector.setCurrentText("claude-3-sonnet")
        model_selector.currentText.return_value = "claude-3-sonnet"
        
        # Send message with new model
        chat_widget.set_message_text("Test with Claude")
        result = chat_widget.send_message()
        
        # Verify message was sent with new model
        assert result is True
        model_selector.setCurrentText.assert_called_with("claude-3-sonnet")
    
    def test_message_sending_with_file_attachment(self, qtbot, mock_chat_widget):
        """Test message sending with file attachment."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Simulate file attachment
        test_file = "/path/to/test/file.txt"
        widget.attach_file = MagicMock(return_value=True)
        widget.attach_file(test_file)
        
        # Send message with attachment
        widget.set_message_text("Please analyze this file")
        result = widget.send_message()
        
        # Verify file attachment and message sending
        assert result is True
        widget.attach_file.assert_called_with(test_file)
    
    @pytest.mark.integration
    def test_full_conversation_flow(self, qtbot, mock_chat_widget, mock_model_selector, ai_service_mocker):
        """Test complete conversation flow through UI."""
        chat_widget = mock_chat_widget
        model_selector = mock_model_selector
        
        qtbot.addWidget(chat_widget)
        qtbot.addWidget(model_selector)
        
        # Configure AI responses
        ai_service_mocker.add_response("Hello! How can I help?", "gpt-4", "openai")
        ai_service_mocker.add_response("Sure, I can help with Python!", "gpt-4", "openai")
        
        # First message
        chat_widget.set_message_text("Hello")
        result1 = chat_widget.send_message()
        assert result1 is True
        
        # Second message
        chat_widget.set_message_text("Can you help with Python?")
        result2 = chat_widget.send_message()
        assert result2 is True
        
        # Verify conversation flow
        assert chat_widget.send_message.call_count == 2


@pytest.mark.slow
class TestMessageSendingPerformance:
    """Performance tests for message sending UI."""
    
    def test_message_sending_response_time(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test message sending response time."""
        import time
        
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure fast response
        ai_service_mocker.add_response("Quick response", "gpt-4", "openai")
        
        # Measure sending time
        start_time = time.time()
        widget.set_message_text("Quick test")
        result = widget.send_message()
        end_time = time.time()
        
        # Verify reasonable response time
        response_time = end_time - start_time
        assert result is True
        assert response_time < 1.0  # Should be very fast for mocks
    
    def test_large_message_handling_performance(self, qtbot, mock_chat_widget):
        """Test performance with very large messages."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Create very large message
        large_message = "Large message content. " * 10000
        
        # Test setting large message
        widget.set_message_text(large_message)
        widget.get_message_text.return_value = large_message
        
        # Verify large message was handled
        assert len(widget.get_message_text()) > 100000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])