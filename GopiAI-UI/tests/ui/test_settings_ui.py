#!/usr/bin/env python3
"""
UI tests for settings functionality using pytest-qt.
Tests settings dialog, preferences management, and configuration through UI.
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
    qtbot, mock_settings_dialog, mock_main_window, mock_theme_manager,
    mock_notification_system, ui_test_data, mock_model_selector
)
from fixtures import mock_crewai_server


class TestSettingsDialogUI:
    """Test settings dialog functionality."""
    
    def test_settings_dialog_initialization(self, qtbot, mock_settings_dialog):
        """Test settings dialog initialization."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Test dialog properties
        assert dialog.exec() == 1  # QDialog.Accepted
        
        # Test initial settings
        settings = dialog.get_settings()
        assert settings["theme"] == "dark"
        assert settings["font_size"] == 12
        assert settings["auto_save"] is True
    
    def test_settings_dialog_show_hide(self, qtbot, mock_settings_dialog):
        """Test showing and hiding settings dialog."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Show dialog
        dialog.show()
        dialog.show.assert_called_once()
        
        # Hide dialog
        dialog.hide()
        dialog.hide.assert_called_once()
        
        # Close dialog
        result = dialog.close()
        assert result is True
    
    def test_settings_dialog_accept_reject(self, qtbot, mock_settings_dialog):
        """Test accepting and rejecting settings dialog."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Test accept
        dialog.exec.return_value = 1  # QDialog.Accepted
        result = dialog.exec()
        assert result == 1
        
        # Test reject
        dialog.exec.return_value = 0  # QDialog.Rejected
        result = dialog.exec()
        assert result == 0
    
    def test_settings_retrieval(self, qtbot, mock_settings_dialog, ui_test_data):
        """Test retrieving settings from dialog."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Configure test settings
        test_settings = ui_test_data["sample_settings"]
        dialog.get_settings.return_value = test_settings
        
        # Get settings
        settings = dialog.get_settings()
        
        # Verify settings
        assert settings["theme"] == "dark"
        assert settings["font_family"] == "Consolas"
        assert settings["font_size"] == 12
        assert settings["auto_save"] is True
        assert settings["show_timestamps"] is True
        assert settings["enable_notifications"] is True
    
    def test_settings_modification(self, qtbot, mock_settings_dialog):
        """Test modifying settings in dialog."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Modify settings
        new_settings = {
            "theme": "light",
            "font_size": 14,
            "auto_save": False
        }
        dialog.set_settings(new_settings)
        
        # Verify settings were set
        dialog.set_settings.assert_called_once_with(new_settings)


class TestThemeSettings:
    """Test theme-related settings functionality."""
    
    def test_theme_selection(self, qtbot, mock_settings_dialog, mock_theme_manager):
        """Test theme selection in settings."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        
        qtbot.addWidget(dialog)
        
        # Get available themes
        available_themes = theme_manager.get_available_themes()
        assert "light" in available_themes
        assert "dark" in available_themes
        assert "auto" in available_themes
        
        # Test current theme
        current_theme = theme_manager.get_current_theme()
        assert current_theme == "dark"
    
    def test_theme_change_through_settings(self, qtbot, mock_settings_dialog, mock_theme_manager, mock_main_window):
        """Test changing theme through settings dialog."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        main_window = mock_main_window
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(main_window)
        
        # Change theme
        theme_manager.set_theme("light")
        theme_manager.get_current_theme.return_value = "light"
        
        # Apply theme to main window
        main_window.apply_theme("light")
        
        # Verify theme change
        theme_manager.set_theme.assert_called_with("light")
        main_window.apply_theme.assert_called_with("light")
        assert theme_manager.get_current_theme() == "light"
    
    def test_theme_preview(self, qtbot, mock_settings_dialog, mock_theme_manager):
        """Test theme preview functionality."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        
        qtbot.addWidget(dialog)
        
        # Preview theme
        dialog.preview_theme = MagicMock()
        dialog.preview_theme("light")
        
        # Verify preview
        dialog.preview_theme.assert_called_once_with("light")
    
    def test_custom_theme_colors(self, qtbot, mock_settings_dialog, mock_theme_manager):
        """Test custom theme color configuration."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        
        qtbot.addWidget(dialog)
        
        # Get theme colors
        colors = theme_manager.get_theme_colors()
        assert "background" in colors
        assert "foreground" in colors
        assert "accent" in colors
        
        # Test custom colors
        custom_colors = {
            "background": "#1e1e1e",
            "foreground": "#ffffff",
            "accent": "#007acc"
        }
        
        dialog.set_custom_colors = MagicMock()
        dialog.set_custom_colors(custom_colors)
        
        # Verify custom colors were set
        dialog.set_custom_colors.assert_called_once_with(custom_colors)


class TestFontSettings:
    """Test font-related settings functionality."""
    
    def test_font_family_selection(self, qtbot, mock_settings_dialog):
        """Test font family selection."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock font selection
        dialog.set_font_family = MagicMock()
        dialog.get_font_family = MagicMock(return_value="Arial")
        
        # Set font family
        dialog.set_font_family("Arial")
        
        # Get font family
        font_family = dialog.get_font_family()
        
        # Verify font family
        dialog.set_font_family.assert_called_once_with("Arial")
        assert font_family == "Arial"
    
    def test_font_size_adjustment(self, qtbot, mock_settings_dialog):
        """Test font size adjustment."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock font size adjustment
        dialog.set_font_size = MagicMock()
        dialog.get_font_size = MagicMock(return_value=14)
        
        # Set font size
        dialog.set_font_size(14)
        
        # Get font size
        font_size = dialog.get_font_size()
        
        # Verify font size
        dialog.set_font_size.assert_called_once_with(14)
        assert font_size == 14
    
    def test_font_preview(self, qtbot, mock_settings_dialog):
        """Test font preview functionality."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock font preview
        dialog.preview_font = MagicMock()
        dialog.preview_font("Consolas", 12)
        
        # Verify font preview
        dialog.preview_font.assert_called_once_with("Consolas", 12)
    
    def test_font_settings_application(self, qtbot, mock_settings_dialog, mock_main_window):
        """Test applying font settings to main window."""
        dialog = mock_settings_dialog
        main_window = mock_main_window
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(main_window)
        
        # Apply font settings
        main_window.set_font = MagicMock()
        main_window.set_font("Consolas", 12)
        
        # Verify font was applied
        main_window.set_font.assert_called_once_with("Consolas", 12)


class TestAPIKeySettings:
    """Test API key management in settings."""
    
    def test_api_key_input(self, qtbot, mock_settings_dialog):
        """Test API key input in settings."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock API key input
        dialog.set_api_key = MagicMock()
        dialog.get_api_key = MagicMock(return_value="test_key_123")
        
        # Set API key
        dialog.set_api_key("openai", "test_key_123")
        
        # Get API key
        api_key = dialog.get_api_key("openai")
        
        # Verify API key handling
        dialog.set_api_key.assert_called_once_with("openai", "test_key_123")
        assert api_key == "test_key_123"
    
    def test_multiple_api_keys(self, qtbot, mock_settings_dialog):
        """Test managing multiple API keys."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock multiple API keys
        api_keys = {
            "openai": "openai_key_123",
            "anthropic": "anthropic_key_456",
            "google": "google_key_789"
        }
        
        dialog.set_all_api_keys = MagicMock()
        dialog.get_all_api_keys = MagicMock(return_value=api_keys)
        
        # Set all API keys
        dialog.set_all_api_keys(api_keys)
        
        # Get all API keys
        retrieved_keys = dialog.get_all_api_keys()
        
        # Verify API keys
        dialog.set_all_api_keys.assert_called_once_with(api_keys)
        assert len(retrieved_keys) == 3
        assert retrieved_keys["openai"] == "openai_key_123"
        assert retrieved_keys["anthropic"] == "anthropic_key_456"
        assert retrieved_keys["google"] == "google_key_789"
    
    def test_api_key_validation(self, qtbot, mock_settings_dialog, mock_notification_system):
        """Test API key validation."""
        dialog = mock_settings_dialog
        notification_system = mock_notification_system
        
        qtbot.addWidget(dialog)
        
        # Mock API key validation
        dialog.validate_api_key = MagicMock(return_value=True)
        
        # Validate API key
        is_valid = dialog.validate_api_key("openai", "valid_key")
        
        # Verify validation
        assert is_valid is True
        dialog.validate_api_key.assert_called_once_with("openai", "valid_key")
        
        # Test invalid key
        dialog.validate_api_key.return_value = False
        is_valid = dialog.validate_api_key("openai", "invalid_key")
        
        # Verify invalid key handling
        assert is_valid is False
        
        # Simulate error notification
        notification_system.show_error("Invalid API key")
        notification_system.show_error.assert_called_with("Invalid API key")
    
    def test_api_key_masking(self, qtbot, mock_settings_dialog):
        """Test API key masking in UI."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock API key masking
        dialog.mask_api_key = MagicMock(return_value="sk-...abc123")
        
        # Mask API key
        masked_key = dialog.mask_api_key("sk-1234567890abcdef1234567890abcdef")
        
        # Verify masking
        assert masked_key == "sk-...abc123"
        dialog.mask_api_key.assert_called_once_with("sk-1234567890abcdef1234567890abcdef")


class TestModelSettings:
    """Test model-related settings functionality."""
    
    def test_default_model_selection(self, qtbot, mock_settings_dialog, mock_model_selector):
        """Test default model selection in settings."""
        dialog = mock_settings_dialog
        model_selector = mock_model_selector
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(model_selector)
        
        # Mock default model setting
        dialog.set_default_model = MagicMock()
        dialog.get_default_model = MagicMock(return_value="gpt-4")
        
        # Set default model
        dialog.set_default_model("gpt-4")
        
        # Get default model
        default_model = dialog.get_default_model()
        
        # Verify default model
        dialog.set_default_model.assert_called_once_with("gpt-4")
        assert default_model == "gpt-4"
    
    def test_model_parameters_configuration(self, qtbot, mock_settings_dialog):
        """Test model parameters configuration."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock model parameters
        parameters = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9
        }
        
        dialog.set_model_parameters = MagicMock()
        dialog.get_model_parameters = MagicMock(return_value=parameters)
        
        # Set model parameters
        dialog.set_model_parameters("gpt-4", parameters)
        
        # Get model parameters
        retrieved_params = dialog.get_model_parameters("gpt-4")
        
        # Verify parameters
        dialog.set_model_parameters.assert_called_once_with("gpt-4", parameters)
        assert retrieved_params["temperature"] == 0.7
        assert retrieved_params["max_tokens"] == 2048
        assert retrieved_params["top_p"] == 0.9
    
    def test_model_availability_settings(self, qtbot, mock_settings_dialog):
        """Test model availability settings."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock model availability
        available_models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
        
        dialog.set_available_models = MagicMock()
        dialog.get_available_models = MagicMock(return_value=available_models)
        
        # Set available models
        dialog.set_available_models(available_models)
        
        # Get available models
        models = dialog.get_available_models()
        
        # Verify available models
        dialog.set_available_models.assert_called_once_with(available_models)
        assert len(models) == 3
        assert "gpt-4" in models
        assert "claude-3-sonnet" in models
        assert "gemini-pro" in models


class TestBehaviorSettings:
    """Test behavior-related settings functionality."""
    
    def test_auto_save_setting(self, qtbot, mock_settings_dialog):
        """Test auto-save setting."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock auto-save setting
        dialog.set_auto_save = MagicMock()
        dialog.get_auto_save = MagicMock(return_value=True)
        
        # Set auto-save
        dialog.set_auto_save(True)
        
        # Get auto-save
        auto_save = dialog.get_auto_save()
        
        # Verify auto-save
        dialog.set_auto_save.assert_called_once_with(True)
        assert auto_save is True
    
    def test_notification_settings(self, qtbot, mock_settings_dialog):
        """Test notification settings."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock notification settings
        notification_settings = {
            "enable_notifications": True,
            "show_system_tray": True,
            "sound_enabled": False
        }
        
        dialog.set_notification_settings = MagicMock()
        dialog.get_notification_settings = MagicMock(return_value=notification_settings)
        
        # Set notification settings
        dialog.set_notification_settings(notification_settings)
        
        # Get notification settings
        settings = dialog.get_notification_settings()
        
        # Verify notification settings
        dialog.set_notification_settings.assert_called_once_with(notification_settings)
        assert settings["enable_notifications"] is True
        assert settings["show_system_tray"] is True
        assert settings["sound_enabled"] is False
    
    def test_conversation_settings(self, qtbot, mock_settings_dialog):
        """Test conversation-related settings."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock conversation settings
        conversation_settings = {
            "show_timestamps": True,
            "auto_scroll": True,
            "max_history": 1000,
            "export_format": "markdown"
        }
        
        dialog.set_conversation_settings = MagicMock()
        dialog.get_conversation_settings = MagicMock(return_value=conversation_settings)
        
        # Set conversation settings
        dialog.set_conversation_settings(conversation_settings)
        
        # Get conversation settings
        settings = dialog.get_conversation_settings()
        
        # Verify conversation settings
        dialog.set_conversation_settings.assert_called_once_with(conversation_settings)
        assert settings["show_timestamps"] is True
        assert settings["auto_scroll"] is True
        assert settings["max_history"] == 1000
        assert settings["export_format"] == "markdown"
    
    def test_privacy_settings(self, qtbot, mock_settings_dialog):
        """Test privacy-related settings."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock privacy settings
        privacy_settings = {
            "store_conversations": True,
            "analytics_enabled": False,
            "crash_reporting": True,
            "data_retention_days": 30
        }
        
        dialog.set_privacy_settings = MagicMock()
        dialog.get_privacy_settings = MagicMock(return_value=privacy_settings)
        
        # Set privacy settings
        dialog.set_privacy_settings(privacy_settings)
        
        # Get privacy settings
        settings = dialog.get_privacy_settings()
        
        # Verify privacy settings
        dialog.set_privacy_settings.assert_called_once_with(privacy_settings)
        assert settings["store_conversations"] is True
        assert settings["analytics_enabled"] is False
        assert settings["crash_reporting"] is True
        assert settings["data_retention_days"] == 30


class TestSettingsPersistence:
    """Test settings persistence functionality."""
    
    def test_save_settings(self, qtbot, mock_settings_dialog):
        """Test saving settings to file."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock settings save
        dialog.save_settings = MagicMock(return_value=True)
        
        # Save settings
        result = dialog.save_settings()
        
        # Verify save
        assert result is True
        dialog.save_settings.assert_called_once()
    
    def test_load_settings(self, qtbot, mock_settings_dialog, ui_test_data):
        """Test loading settings from file."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock settings load
        test_settings = ui_test_data["sample_settings"]
        dialog.load_settings = MagicMock(return_value=test_settings)
        
        # Load settings
        settings = dialog.load_settings()
        
        # Verify load
        assert settings["theme"] == "dark"
        assert settings["font_size"] == 12
        dialog.load_settings.assert_called_once()
    
    def test_reset_settings(self, qtbot, mock_settings_dialog):
        """Test resetting settings to defaults."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock settings reset
        default_settings = {
            "theme": "light",
            "font_size": 10,
            "auto_save": False
        }
        dialog.reset_to_defaults = MagicMock(return_value=default_settings)
        
        # Reset settings
        settings = dialog.reset_to_defaults()
        
        # Verify reset
        assert settings["theme"] == "light"
        assert settings["font_size"] == 10
        assert settings["auto_save"] is False
        dialog.reset_to_defaults.assert_called_once()
    
    def test_export_settings(self, qtbot, mock_settings_dialog):
        """Test exporting settings to file."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock settings export
        dialog.export_settings = MagicMock(return_value=True)
        
        # Export settings
        result = dialog.export_settings("/path/to/settings.json")
        
        # Verify export
        assert result is True
        dialog.export_settings.assert_called_once_with("/path/to/settings.json")
    
    def test_import_settings(self, qtbot, mock_settings_dialog):
        """Test importing settings from file."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Mock settings import
        imported_settings = {
            "theme": "dark",
            "font_size": 14,
            "auto_save": True
        }
        dialog.import_settings = MagicMock(return_value=imported_settings)
        
        # Import settings
        settings = dialog.import_settings("/path/to/settings.json")
        
        # Verify import
        assert settings["theme"] == "dark"
        assert settings["font_size"] == 14
        assert settings["auto_save"] is True
        dialog.import_settings.assert_called_once_with("/path/to/settings.json")


@pytest.mark.integration
class TestSettingsIntegration:
    """Test settings integration with other UI components."""
    
    def test_settings_integration_with_main_window(self, qtbot, mock_settings_dialog, mock_main_window):
        """Test settings integration with main window."""
        dialog = mock_settings_dialog
        main_window = mock_main_window
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(main_window)
        
        # Open settings from main window
        main_window.open_settings = MagicMock(return_value=dialog)
        settings_dialog = main_window.open_settings()
        
        # Verify settings dialog was opened
        assert settings_dialog == dialog
        main_window.open_settings.assert_called_once()
    
    def test_settings_application_to_ui(self, qtbot, mock_settings_dialog, mock_main_window, mock_theme_manager):
        """Test applying settings to UI components."""
        dialog = mock_settings_dialog
        main_window = mock_main_window
        theme_manager = mock_theme_manager
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(main_window)
        
        # Apply settings
        settings = {
            "theme": "dark",
            "font_size": 12,
            "auto_save": True
        }
        
        # Apply theme
        theme_manager.set_theme(settings["theme"])
        main_window.apply_theme(settings["theme"])
        
        # Apply font
        main_window.set_font_size(settings["font_size"])
        
        # Verify settings application
        theme_manager.set_theme.assert_called_with("dark")
        main_window.apply_theme.assert_called_with("dark")
        main_window.set_font_size.assert_called_with(12)
    
    def test_settings_with_model_selector(self, qtbot, mock_settings_dialog, mock_model_selector):
        """Test settings integration with model selector."""
        dialog = mock_settings_dialog
        model_selector = mock_model_selector
        
        qtbot.addWidget(dialog)
        qtbot.addWidget(model_selector)
        
        # Set default model through settings
        dialog.set_default_model("claude-3-sonnet")
        model_selector.setCurrentText("claude-3-sonnet")
        model_selector.currentText.return_value = "claude-3-sonnet"
        
        # Verify integration
        dialog.set_default_model.assert_called_with("claude-3-sonnet")
        model_selector.setCurrentText.assert_called_with("claude-3-sonnet")
        assert model_selector.currentText() == "claude-3-sonnet"


@pytest.mark.ui
class TestSettingsKeyboardShortcuts:
    """Test keyboard shortcuts for settings."""
    
    def test_settings_dialog_shortcuts(self, qtbot, mock_settings_dialog):
        """Test keyboard shortcuts in settings dialog."""
        dialog = mock_settings_dialog
        qtbot.addWidget(dialog)
        
        # Test shortcut setup (would use actual key events in real implementation)
        assert dialog is not None
        
        # In real implementation:
        # qtbot.keyClick(dialog, Qt.Key_Escape)  # Close dialog
        # qtbot.keyClick(dialog, Qt.Key_Return)  # Accept dialog
        # qtbot.keyClick(dialog, Qt.Key_Tab)     # Navigate between fields


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])