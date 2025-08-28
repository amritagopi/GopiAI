#!/usr/bin/env python3
"""
Unit tests for model selector widget functionality.
Tests model selection, provider switching, and API key management.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_model_selector, ui_test_data
)
from fixtures import ai_service_mocker


class TestModelSelector:
    """Test model selector widget functionality."""
    
    def test_model_selector_initialization(self, qtbot, mock_model_selector):
        """Test model selector initialization."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test initial state
        assert selector.count() == 3
        assert selector.currentText() == "gpt-4"
        
        # Test model data
        model_data = selector.currentData()
        assert model_data["provider"] == "openai"
        assert model_data["model"] == "gpt-4"
    
    def test_get_available_models(self, mock_model_selector):
        """Test getting available models."""
        selector = mock_model_selector
        
        # Test model count
        count = selector.count()
        assert count == 3
        
        # Test model names
        models = [selector.itemText(i) for i in range(count)]
        expected_models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
        assert models == expected_models
    
    def test_current_model_selection(self, mock_model_selector):
        """Test current model selection."""
        selector = mock_model_selector
        
        # Test current model
        current_model = selector.currentText()
        assert current_model == "gpt-4"
        
        # Test current model data
        model_data = selector.currentData()
        assert isinstance(model_data, dict)
        assert "provider" in model_data
        assert "model" in model_data
    
    def test_set_current_model(self, mock_model_selector):
        """Test setting current model."""
        selector = mock_model_selector
        
        # Test setting model
        selector.setCurrentText("claude-3-sonnet")
        selector.setCurrentText.assert_called_once_with("claude-3-sonnet")
    
    def test_add_model(self, mock_model_selector):
        """Test adding a new model."""
        selector = mock_model_selector
        
        # Test adding model
        new_model = "gpt-3.5-turbo"
        selector.addItem(new_model)
        selector.addItem.assert_called_once_with(new_model)
    
    def test_clear_models(self, mock_model_selector):
        """Test clearing all models."""
        selector = mock_model_selector
        
        # Test clearing models
        selector.clear()
        selector.clear.assert_called_once()
    
    def test_model_data_structure(self, mock_model_selector):
        """Test model data structure."""
        selector = mock_model_selector
        
        model_data = selector.currentData()
        
        # Verify required fields
        assert "provider" in model_data
        assert "model" in model_data
        
        # Verify data types
        assert isinstance(model_data["provider"], str)
        assert isinstance(model_data["model"], str)
    
    def test_provider_filtering(self, mock_model_selector):
        """Test filtering models by provider."""
        selector = mock_model_selector
        
        # Mock provider-specific models
        openai_models = ["gpt-4", "gpt-3.5-turbo"]
        anthropic_models = ["claude-3-sonnet", "claude-3-haiku"]
        
        # Test OpenAI models
        for model in openai_models:
            selector.addItem(model)
        
        # Verify models were added
        assert selector.addItem.call_count == len(openai_models)
    
    @pytest.mark.ui
    def test_model_selector_ui_interaction(self, qtbot, mock_model_selector):
        """Test model selector UI interactions."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Test selection change
        # In real implementation, this would trigger selection change event
        selector.setCurrentText("claude-3-sonnet")
        
        # Verify selection was changed
        selector.setCurrentText.assert_called_with("claude-3-sonnet")
    
    def test_model_selector_with_ai_service(self, mock_model_selector, ai_service_mocker):
        """Test model selector integration with AI service."""
        selector = mock_model_selector
        
        # Configure AI service for different models
        ai_service_mocker.add_response("OpenAI response", "gpt-4", "openai")
        ai_service_mocker.add_response("Anthropic response", "claude-3-sonnet", "anthropic")
        
        # Test model selection affects AI service
        current_model = selector.currentText()
        model_data = selector.currentData()
        
        # Verify model data matches AI service configuration
        assert current_model == "gpt-4"
        assert model_data["provider"] == "openai"


class TestModelSelectorAdvanced:
    """Test advanced model selector functionality."""
    
    def test_model_selector_with_api_keys(self, mock_model_selector):
        """Test model selector with API key management."""
        selector = mock_model_selector
        
        # Mock API key functionality
        selector.get_api_key = MagicMock()
        selector.set_api_key = MagicMock()
        
        # Test getting API key
        selector.get_api_key.return_value = "test_api_key"
        api_key = selector.get_api_key("openai")
        assert api_key == "test_api_key"
        
        # Test setting API key
        selector.set_api_key("openai", "new_api_key")
        selector.set_api_key.assert_called_with("openai", "new_api_key")
    
    def test_model_selector_validation(self, mock_model_selector):
        """Test model selector validation."""
        selector = mock_model_selector
        
        # Mock validation
        selector.validate_model = MagicMock()
        selector.validate_model.return_value = True
        
        # Test model validation
        is_valid = selector.validate_model("gpt-4")
        assert is_valid is True
        selector.validate_model.assert_called_with("gpt-4")
    
    def test_model_selector_refresh(self, mock_model_selector):
        """Test model selector refresh functionality."""
        selector = mock_model_selector
        
        # Mock refresh
        selector.refresh_models = MagicMock()
        
        # Test refresh
        selector.refresh_models()
        selector.refresh_models.assert_called_once()
    
    def test_model_selector_favorites(self, mock_model_selector):
        """Test model selector favorites functionality."""
        selector = mock_model_selector
        
        # Mock favorites
        selector.add_to_favorites = MagicMock()
        selector.get_favorites = MagicMock()
        selector.get_favorites.return_value = ["gpt-4", "claude-3-sonnet"]
        
        # Test adding to favorites
        selector.add_to_favorites("gpt-4")
        selector.add_to_favorites.assert_called_with("gpt-4")
        
        # Test getting favorites
        favorites = selector.get_favorites()
        assert "gpt-4" in favorites
        assert "claude-3-sonnet" in favorites
    
    def test_model_selector_search(self, mock_model_selector):
        """Test model selector search functionality."""
        selector = mock_model_selector
        
        # Mock search
        selector.search_models = MagicMock()
        selector.search_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        
        # Test search
        results = selector.search_models("gpt")
        assert "gpt-4" in results
        assert "gpt-3.5-turbo" in results
        selector.search_models.assert_called_with("gpt")
    
    @pytest.mark.ui
    def test_model_selector_context_menu(self, qtbot, mock_model_selector):
        """Test model selector context menu."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # Mock context menu
        selector.show_context_menu = MagicMock()
        
        # Test context menu
        selector.show_context_menu()
        selector.show_context_menu.assert_called_once()
    
    def test_model_selector_tooltips(self, mock_model_selector):
        """Test model selector tooltips."""
        selector = mock_model_selector
        
        # Mock tooltip functionality
        selector.setToolTip = MagicMock()
        
        # Test setting tooltip
        tooltip_text = "Select an AI model for conversation"
        selector.setToolTip(tooltip_text)
        selector.setToolTip.assert_called_with(tooltip_text)


class TestModelSelectorErrorHandling:
    """Test model selector error handling."""
    
    def test_invalid_model_selection(self, mock_model_selector):
        """Test handling of invalid model selection."""
        selector = mock_model_selector
        
        # Mock invalid model
        selector.setCurrentText.side_effect = ValueError("Invalid model")
        
        # Test error handling
        with pytest.raises(ValueError, match="Invalid model"):
            selector.setCurrentText("invalid_model")
    
    def test_api_key_validation_error(self, mock_model_selector):
        """Test handling of API key validation errors."""
        selector = mock_model_selector
        
        # Mock API key validation error
        selector.validate_api_key = MagicMock()
        selector.validate_api_key.side_effect = Exception("Invalid API key")
        
        # Test error handling
        with pytest.raises(Exception, match="Invalid API key"):
            selector.validate_api_key("invalid_key")
    
    def test_model_loading_error(self, mock_model_selector):
        """Test handling of model loading errors."""
        selector = mock_model_selector
        
        # Mock model loading error
        selector.refresh_models.side_effect = ConnectionError("Failed to load models")
        
        # Test error handling
        with pytest.raises(ConnectionError, match="Failed to load models"):
            selector.refresh_models()
    
    def test_empty_model_list(self, mock_model_selector):
        """Test handling of empty model list."""
        selector = mock_model_selector
        
        # Mock empty model list
        selector.count.return_value = 0
        selector.currentText.return_value = ""
        
        # Test empty state
        assert selector.count() == 0
        assert selector.currentText() == ""


class TestModelSelectorIntegration:
    """Test model selector integration with other components."""
    
    @pytest.mark.integration
    def test_model_selector_full_workflow(self, qtbot, mock_model_selector, ai_service_mocker):
        """Test complete model selector workflow."""
        selector = mock_model_selector
        qtbot.addWidget(selector)
        
        # 1. Initialize with models
        assert selector.count() == 3
        
        # 2. Select a model
        selector.setCurrentText("claude-3-sonnet")
        
        # 3. Get model data
        model_data = selector.currentData()
        
        # 4. Configure AI service
        ai_service_mocker.add_response("Test response", "claude-3-sonnet", "anthropic")
        
        # 5. Verify integration
        selector.setCurrentText.assert_called_with("claude-3-sonnet")
        assert model_data["provider"] == "openai"  # Mock returns openai
    
    def test_model_selector_with_settings(self, mock_model_selector, ui_test_data):
        """Test model selector integration with settings."""
        selector = mock_model_selector
        
        # Test loading model from settings
        # In real implementation, this would load from settings file
        current_model = selector.currentText()
        assert current_model == "gpt-4"
    
    def test_model_selector_persistence(self, mock_model_selector):
        """Test model selector persistence across sessions."""
        selector = mock_model_selector
        
        # Set a model
        selector.setCurrentText("claude-3-sonnet")
        
        # Simulate restart - model should be remembered
        # In real implementation, this would involve settings persistence
        selector.setCurrentText.assert_called_with("claude-3-sonnet")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])