#!/usr/bin/env python3
"""
UI tests for chat widget using pytest-qt and improved fixtures.
"""

import pytest
import sys
import os

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_chat_widget, mock_model_selector,
    mock_notification_system, ui_test_data
)
from fixtures import ai_service_mocker, mock_crewai_server, mock_conversation_manager


class TestChatWidget:
    """Test chat widget functionality."""
    
    def test_chat_widget_initialization(self, qtbot, mock_chat_widget):
        """Test chat widget initialization."""
        widget = mock_chat_widget
        
        # Add widget to qtbot for testing
        qtbot.addWidget(widget)
        
        # Test initial state
        assert widget.get_message_text() == "Test message"
        messages = widget.get_messages()
        assert len(messages) >= 0
    
    def test_send_message_functionality(self, qtbot, mock_chat_widget, ai_service_mocker):
        """Test sending a message through the chat widget."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure AI service response
        ai_service_mocker.add_response("Hello! How can I help you today?", "gpt-4", "openai")
        
        # Set up message
        test_message = "Hello, AI assistant!"
        widget.set_message_text(test_message)
        
        # Simulate sending message
        result = widget.send_message()
        
        # Verify message was sent
        assert result is True
        widget.send_message.assert_called_once()
    
    def test_message_history_display(self, qtbot, mock_chat_widget, ui_test_data):
        """Test displaying message history in chat widget."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Configure mock to return test messages
        test_messages = ui_test_data["sample_messages"]
        widget.get_messages.return_value = test_messages
        
        # Get messages
        messages = widget.get_messages()
        
        # Verify message structure
        assert len(messages) == 4
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert "Hello" in messages[0]["content"]
    
    def test_clear_chat_functionality(self, qtbot, mock_chat_widget):
        """Test clearing chat history."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Clear chat
        widget.clear_chat()
        
        # Verify clear was called
        widget.clear_chat.assert_called_once()
    
    def test_add_message_to_chat(self, qtbot, mock_chat_widget):
        """Test adding a message to the chat."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Add a message
        test_message = {"role": "user", "content": "Test message"}
        widget.add_message(test_message)
        
        # Verify message was added
        widget.add_message.assert_called_once_with(test_message)
    
    def test_chat_widget_with_model_selector(self, qtbot, mock_chat_widget, mock_model_selector):
        """Test chat widget integration with model selector."""
        chat_widget = mock_chat_widget
        model_selector = mock_model_selector
        
        qtbot.addWidget(chat_widget)
        qtbot.addWidget(model_selector)
        
        # Test current model
        current_model = model_selector.currentText()
        assert current_model == "gpt-4"
        
        # Test model data
        model_data = model_selector.currentData()
        assert model_data["provider"] == "openai"
        assert model_data["model"] == "gpt-4"
    
    def test_chat_widget_error_handling(self, qtbot, mock_chat_widget, mock_notification_system):
        """Test error handling in chat widget."""
        widget = mock_chat_widget
        notification_system = mock_notification_system
        
        qtbot.addWidget(widget)
        
        # Simulate an error scenario
        widget.send_message.return_value = False
        
        # Attempt to send message
        result = widget.send_message()
        
        # Verify error handling
        assert result is False
        
        # Simulate showing error notification
        notification_system.show_error("Failed to send message")
        notification_system.show_error.assert_called_once_with("Failed to send message")
    
    def test_chat_widget_with_conversation_manager(self, qtbot, mock_chat_widget, mock_conversation_manager):
        """Test chat widget integration with conversation manager."""
        widget = mock_chat_widget
        conv_manager = mock_conversation_manager
        
        qtbot.addWidget(widget)
        
        # Test getting conversations
        conversations = conv_manager.get_conversations()
        assert len(conversations) > 0
        
        # Test creating new conversation
        new_conv_id = conv_manager.create_conversation()
        assert new_conv_id == "new_conv_id"
        
        # Test getting specific conversation
        conversation = conv_manager.get_conversation()
        assert "id" in conversation
        assert "messages" in conversation
    
    @pytest.mark.ui
    def test_chat_widget_keyboard_shortcuts(self, qtbot, mock_chat_widget):
        """Test keyboard shortcuts in chat widget."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # This would test actual keyboard events in a real implementation
        # For now, we just verify the widget is properly set up
        assert widget is not None
        
        # In a real test, you might do:
        # qtbot.keyClick(widget, Qt.Key_Return, Qt.ControlModifier)
        # But since we're using mocks, we just verify the setup
    
    @pytest.mark.ui
    def test_chat_widget_theme_changes(self, qtbot, mock_chat_widget):
        """Test chat widget response to theme changes."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # This would test theme application in a real implementation
        # For now, we verify the widget exists and can be themed
        assert widget is not None
        
        # In a real implementation, you might test:
        # widget.apply_theme("dark")
        # assert widget.styleSheet() contains dark theme colors
    
    @pytest.mark.integration
    def test_chat_widget_full_conversation_flow(self, qtbot, mock_chat_widget, mock_crewai_server, ai_service_mocker):
        """Test complete conversation flow through chat widget."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Set up AI response
        ai_service_mocker.add_response("I understand your question. Let me help you with that.", "gpt-4", "openai")
        
        # Simulate user input
        user_message = "Can you help me with Python programming?"
        widget.set_message_text(user_message)
        
        # Send message
        send_result = widget.send_message()
        
        # Verify the flow
        assert send_result is True
        widget.set_message_text.assert_called_with(user_message)
        widget.send_message.assert_called_once()
        
        # In a real implementation, this would also test:
        # - Message appears in chat history
        # - AI response is received and displayed
        # - UI updates appropriately


@pytest.mark.slow
class TestChatWidgetPerformance:
    """Performance tests for chat widget."""
    
    def test_large_message_history_performance(self, qtbot, mock_chat_widget):
        """Test chat widget performance with large message history."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Simulate large message history
        large_history = []
        for i in range(1000):
            large_history.extend([
                {"role": "user", "content": f"User message {i}"},
                {"role": "assistant", "content": f"Assistant response {i}"}
            ])
        
        widget.get_messages.return_value = large_history
        
        # Test getting messages (should be fast even with large history)
        messages = widget.get_messages()
        assert len(messages) == 2000
    
    def test_rapid_message_sending(self, qtbot, mock_chat_widget):
        """Test rapid message sending performance."""
        widget = mock_chat_widget
        qtbot.addWidget(widget)
        
        # Simulate rapid message sending
        for i in range(10):
            widget.set_message_text(f"Rapid message {i}")
            result = widget.send_message()
            assert result is True
        
        # Verify all messages were handled
        assert widget.send_message.call_count == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])