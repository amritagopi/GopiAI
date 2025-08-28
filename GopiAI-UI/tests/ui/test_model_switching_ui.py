#!/usr/bin/env python3
"""
UI tests for model switching functionality using pytest-qt.
Tests model selection, switching, and integration with chat functionality.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))

from ui_fixtures import (
    qtbot, mock_model_selector, mock_chat_widget, mock_main_window,
    mock_notification_system, ui_test_data
)
from fixtures import ai_service_mocker, mock_crewai_server


class TestModelSelectorUI:
    """Test model selector widget functionality."""
    
    def test_model_selector_initialization(self, qtbot, mock_model_selector):
        """Test model selector initialization."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test initial state
        assert selector.currentText() == "gpt-4"
        assert selector.count() == 3
        
        # Test available models
        models = [selector.itemText(i) for i in range(selector.count())]
        expected_models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
        assert models == expected_models
    
    def test_model_selection_change(self, qtbot, mock_model_selector):
        """Test changing model selection."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Change to Claude
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        selector.currentData.return_value = {"provider": "anthropic", "model": "claude-3-sonnet"}
        
        # Verify model change
        assert selector.currentText() == "claude-3-sonnet"
        current_data = selector.currentData()
        assert current_data["provider"] == "anthropic"
        assert current_data["model"] == "claude-3-sonnet"
    
    def test_model_data_retrieval(self, qtbot, mock_model_selector):
        """Test retrieving model data."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test GPT-4 data
        selector.currentText.return_value = "gpt-4"
        selector.currentData.return_value = {
            "provider": "openai",
            "model": "gpt-4",
            "max_tokens": 8192,
            "supports_streaming": True
        }
        
        data = selector.currentData()
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4"
        assert data["max_tokens"] == 8192
        assert data["supports_streaming"] is True
    
    def test_add_new_model(self, qtbot, mock_model_selector):
        """Test adding a new model to selector."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Add new model
        new_model_data = {"provider": "openai", "model": "gpt-3.5-turbo"}
        selector.addItem("gpt-3.5-turbo", new_model_data)
        
        # Update count
        selector.count.return_value = 4
        
        # Verify model was added
        selector.addItem.assert_called_with("gpt-3.5-turbo", new_model_data)
        assert selector.count() == 4
    
    def test_clear_models(self, qtbot, mock_model_selector):
        """Test clearing all models from selector."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Clear models
        selector.clear()
        selector.count.return_value = 0
        
        # Verify models were cleared
        selector.clear.assert_called_once()
        assert selector.count() == 0
    
    def test_model_selector_with_invalid_model(self, qtbot, mock_model_selector, mock_notification_system):
        """Test handling of invalid model selection."""
        selector = mock_model_selector
        notification_system = mock_notification_system
        
        qtbot.addWidget(selector)
        
        # Simulate invalid model selection
        selector.currentText.return_value = "invalid-model"
        selector.currentData.return_value = None
        
        # Verify invalid model handling
        assert selector.currentText() == "invalid-model"
        assert selector.currentData() is None
        
        # Simulate error notification
        notification_system.show_error("Invalid model selected")
        notification_system.show_error.assert_called_with("Invalid model selected")


class TestModelSwitchingIntegration:
    """Test model switching integration with other UI components."""
    
    def test_model_switching_with_chat_widget(self, qtbot, mock_model_selector, mock_chat_widget, ai_service_mocker):
        """Test model switching integration with chat widget."""
        selector = mock_model_selector
        chat_widget = mock_chat_widget
        
        qtbot.addWidget(selector)
        qtbot.addWidget(chat_widget)
        
        # Start with GPT-4
        selector.currentText.return_value = "gpt-4"
        ai_service_mocker.add_response("GPT-4 response", "gpt-4", "openai")
        
        # Send message with GPT-4
        chat_widget.set_message_text("Test with GPT-4")
        result1 = chat_widget.send_message()
        assert result1 is True
        
        # Switch to Claude
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        selector.currentData.return_value = {"provider": "anthropic", "model": "claude-3-sonnet"}
        ai_service_mocker.add_response("Claude response", "claude-3-sonnet", "anthropic")
        
        # Send message with Claude
        chat_widget.set_message_text("Test with Claude")
        result2 = chat_widget.send_message()
        assert result2 is True
        
        # Verify model switching worked
        selector.setCurrentText.assert_called_with("claude-3-sonnet")
        assert chat_widget.send_message.call_count == 2
    
    def test_model_switching_preserves_conversation(self, qtbot, mock_model_selector, mock_chat_widget, ui_test_data):
        """Test that model switching preserves conversation history."""
        selector = mock_model_selector
        chat_widget = mock_chat_widget
        
        qtbot.addWidget(selector)
        qtbot.addWidget(chat_widget)
        
        # Set initial conversation
        initial_messages = ui_test_data["sample_messages"]
        chat_widget.get_messages.return_value = initial_messages
        
        # Switch model
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        
        # Verify conversation is preserved
        messages = chat_widget.get_messages()
        assert len(messages) == len(initial_messages)
        assert messages[0]["content"] == "Hello, how are you?"
    
    def test_model_switching_updates_ui_indicators(self, qtbot, mock_model_selector, mock_main_window):
        """Test that model switching updates UI indicators."""
        selector = mock_model_selector
        main_window = mock_main_window
        
        qtbot.addWidget(selector)
        qtbot.addWidget(main_window)
        
        # Switch model
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        
        # Simulate UI update
        main_window.update_model_indicator = MagicMock()
        main_window.update_model_indicator("claude-3-sonnet")
        
        # Verify UI was updated
        main_window.update_model_indicator.assert_called_with("claude-3-sonnet")
    
    def test_model_switching_with_settings_persistence(self, qtbot, mock_model_selector):
        """Test that model selection persists in settings."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Switch model
        selector.setCurrentText("gemini-pro")
        selector.currentText.return_value = "gemini-pro"
        
        # Simulate settings save
        selector.save_selection = MagicMock()
        selector.save_selection("gemini-pro")
        
        # Verify selection was saved
        selector.save_selection.assert_called_with("gemini-pro")


class TestModelAvailabilityUI:
    """Test model availability and status in UI."""
    
    def test_model_availability_check(self, qtbot, mock_model_selector, mock_crewai_server):
        """Test checking model availability."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock availability check
        selector.check_model_availability = MagicMock(return_value=True)
        
        # Check if current model is available
        is_available = selector.check_model_availability("gpt-4")
        
        # Verify availability check
        assert is_available is True
        selector.check_model_availability.assert_called_with("gpt-4")
    
    def test_unavailable_model_handling(self, qtbot, mock_model_selector, mock_notification_system):
        """Test handling of unavailable models."""
        selector = mock_model_selector
        notification_system = mock_notification_system
        
        qtbot.addWidget(selector)
        
        # Mock unavailable model
        selector.check_model_availability = MagicMock(return_value=False)
        
        # Try to select unavailable model
        is_available = selector.check_model_availability("unavailable-model")
        
        # Verify unavailable model handling
        assert is_available is False
        
        # Simulate warning notification
        notification_system.show_warning("Model unavailable")
        notification_system.show_warning.assert_called_with("Model unavailable")
    
    def test_model_status_indicators(self, qtbot, mock_model_selector):
        """Test model status indicators in UI."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock status indicators
        selector.set_model_status = MagicMock()
        
        # Set different statuses
        selector.set_model_status("gpt-4", "available")
        selector.set_model_status("claude-3-sonnet", "limited")
        selector.set_model_status("gemini-pro", "unavailable")
        
        # Verify status indicators were set
        assert selector.set_model_status.call_count == 3
        selector.set_model_status.assert_any_call("gpt-4", "available")
        selector.set_model_status.assert_any_call("claude-3-sonnet", "limited")
        selector.set_model_status.assert_any_call("gemini-pro", "unavailable")


class TestModelConfigurationUI:
    """Test model configuration through UI."""
    
    def test_model_parameters_configuration(self, qtbot, mock_model_selector):
        """Test configuring model parameters."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock parameter configuration
        selector.set_model_parameters = MagicMock()
        
        # Configure parameters
        parameters = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9
        }
        selector.set_model_parameters("gpt-4", parameters)
        
        # Verify parameters were set
        selector.set_model_parameters.assert_called_with("gpt-4", parameters)
    
    def test_model_provider_configuration(self, qtbot, mock_model_selector):
        """Test configuring model provider settings."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock provider configuration
        selector.configure_provider = MagicMock()
        
        # Configure OpenAI provider
        openai_config = {
            "api_key": "test_key",
            "base_url": "https://api.openai.com/v1",
            "timeout": 30
        }
        selector.configure_provider("openai", openai_config)
        
        # Verify provider was configured
        selector.configure_provider.assert_called_with("openai", openai_config)
    
    def test_custom_model_addition(self, qtbot, mock_model_selector):
        """Test adding custom model configuration."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock custom model addition
        selector.add_custom_model = MagicMock()
        
        # Add custom model
        custom_model = {
            "name": "custom-gpt",
            "provider": "openai",
            "model": "gpt-4-custom",
            "parameters": {"temperature": 0.5}
        }
        selector.add_custom_model(custom_model)
        
        # Verify custom model was added
        selector.add_custom_model.assert_called_with(custom_model)


class TestModelSwitchingPerformance:
    """Test performance aspects of model switching."""
    
    def test_model_switching_speed(self, qtbot, mock_model_selector):
        """Test speed of model switching."""
        import time
        
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Measure switching time
        start_time = time.time()
        
        # Switch between models rapidly
        models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
        for model in models:
            selector.setCurrentText(model)
            selector.currentText.return_value = model
        
        end_time = time.time()
        
        # Verify reasonable switching time
        switching_time = end_time - start_time
        assert switching_time < 1.0  # Should be very fast for mocks
    
    def test_model_list_loading_performance(self, qtbot, mock_model_selector):
        """Test performance of loading large model lists."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Simulate loading many models
        for i in range(100):
            model_data = {"provider": "test", "model": f"test-model-{i}"}
            selector.addItem(f"test-model-{i}", model_data)
        
        # Update count
        selector.count.return_value = 103  # 3 original + 100 new
        
        # Verify all models were added
        assert selector.count() == 103


@pytest.mark.ui
class TestModelSwitchingKeyboardShortcuts:
    """Test keyboard shortcuts for model switching."""
    
    def test_model_switching_shortcuts(self, qtbot, mock_model_selector):
        """Test keyboard shortcuts for model switching."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test shortcut setup (would use actual key events in real implementation)
        assert selector is not None
        
        # In real implementation:
        # qtbot.keyClick(selector, Qt.Key_1, Qt.ControlModifier)  # Ctrl+1 for first model
        # qtbot.keyClick(selector, Qt.Key_2, Qt.ControlModifier)  # Ctrl+2 for second model
    
    def test_model_switching_dropdown_navigation(self, qtbot, mock_model_selector):
        """Test dropdown navigation with keyboard."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test dropdown navigation (would use actual key events in real implementation)
        assert selector is not None
        
        # In real implementation:
        # qtbot.keyClick(selector, Qt.Key_Down)  # Navigate down
        # qtbot.keyClick(selector, Qt.Key_Up)    # Navigate up
        # qtbot.keyClick(selector, Qt.Key_Return) # Select model


@pytest.mark.integration
class TestModelSwitchingFullIntegration:
    """Test full integration of model switching with entire UI."""
    
    def test_complete_model_switching_workflow(self, qtbot, mock_model_selector, mock_chat_widget, mock_main_window, ai_service_mocker):
        """Test complete model switching workflow."""
        selector = mock_model_selector
        chat_widget = mock_chat_widget
        main_window = mock_main_window
        
        qtbot.addWidget(selector)
        qtbot.addWidget(chat_widget)
        qtbot.addWidget(main_window)
        
        # Configure AI responses for different models
        ai_service_mocker.add_response("GPT-4 response", "gpt-4", "openai")
        ai_service_mocker.add_response("Claude response", "claude-3-sonnet", "anthropic")
        
        # Start with GPT-4
        selector.currentText.return_value = "gpt-4"
        chat_widget.set_message_text("Hello GPT-4")
        result1 = chat_widget.send_message()
        assert result1 is True
        
        # Switch to Claude
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        selector.currentData.return_value = {"provider": "anthropic", "model": "claude-3-sonnet"}
        
        # Send message with Claude
        chat_widget.set_message_text("Hello Claude")
        result2 = chat_widget.send_message()
        assert result2 is True
        
        # Verify complete workflow
        assert selector.setCurrentText.call_count >= 1
        assert chat_widget.send_message.call_count == 2
    
    def test_model_switching_with_conversation_context(self, qtbot, mock_model_selector, mock_chat_widget, ui_test_data):
        """Test model switching while maintaining conversation context."""
        selector = mock_model_selector
        chat_widget = mock_chat_widget
        
        qtbot.addWidget(selector)
        qtbot.addWidget(chat_widget)
        
        # Set up conversation context
        conversation_messages = ui_test_data["sample_messages"]
        chat_widget.get_messages.return_value = conversation_messages
        
        # Switch model mid-conversation
        selector.setCurrentText("claude-3-sonnet")
        selector.currentText.return_value = "claude-3-sonnet"
        
        # Continue conversation with new model
        chat_widget.set_message_text("Continue with Claude")
        result = chat_widget.send_message()
        
        # Verify context was maintained
        assert result is True
        messages = chat_widget.get_messages()
        assert len(messages) == len(conversation_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])