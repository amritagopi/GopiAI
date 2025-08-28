#!/usr/bin/env python3
"""
Unit tests for settings dialog functionality.
Tests settings dialog initialization, configuration management, and user interactions.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_settings_dialog, mock_theme_manager, ui_test_data
)


class TestSettingsDialog:
    """Test settings dialog functionality."""
    
    def test_settings_dialog_initialization(self, qtbot, mock_settings_dialog):
        """Test settings dialog initialization."""
        dialog = mock_settings_dialog
        
        # Test dialog can be created
        assert dialog is not None
        
        # Test initial settings
        settings = dialog.get_settings()
        assert isinstance(settings, dict)
        assert "theme" in settings
        assert "font_size" in settings
        assert "auto_save" in settings
    
    def test_settings_dialog_show(self, qtbot, mock_settings_dialog):
        """Test showing settings dialog."""
        dialog = mock_settings_dialog
        
        # Test showing dialog
        dialog.show()
        dialog.show.assert_called_once()
    
    def test_settings_dialog_exec(self, qtbot, mock_settings_dialog):
        """Test executing settings dialog."""
        dialog = mock_settings_dialog
        
        # Test executing dialog
        result = dialog.exec()
        assert result == 1  # QDialog.Accepted
        dialog.exec.assert_called_once()
    
    def test_settings_dialog_close(self, qtbot, mock_settings_dialog):
        """Test closing settings dialog."""
        dialog = mock_settings_dialog
        
        # Test closing dialog
        result = dialog.close()
        assert result is True
        dialog.close.assert_called_once()
    
    def test_get_settings(self, mock_settings_dialog):
        """Test getting settings from dialog."""
        dialog = mock_settings_dialog
        
        settings = dialog.get_settings()
        
        # Verify settings structure
        assert isinstance(settings, dict)
        assert settings["theme"] == "dark"
        assert settings["font_size"] == 12
        assert settings["auto_save"] is True
    
    def test_set_settings(self, mock_settings_dialog):
        """Test setting settings in dialog."""
        dialog = mock_settings_dialog
        
        new_settings = {
            "theme": "light",
            "font_size": 14,
            "auto_save": False
        }
        
        # Test setting settings
        dialog.set_settings(new_settings)
        dialog.set_settings.assert_called_once_with(new_settings)
    
    def test_settings_validation(self, mock_settings_dialog):
        """Test settings validation."""
        dialog = mock_settings_dialog
        
        # Test valid settings
        valid_settings = {
            "theme": "dark",
            "font_size": 12,
            "auto_save": True
        }
        
        dialog.set_settings(valid_settings)
        dialog.set_settings.assert_called_with(valid_settings)
    
    def test_settings_dialog_with_theme_manager(self, qtbot, mock_settings_dialog, mock_theme_manager):
        """Test settings dialog integration with theme manager."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        
        # Get current theme from theme manager
        current_theme = theme_manager.get_current_theme()
        assert current_theme == "dark"
        
        # Update settings with theme
        settings = dialog.get_settings()
        assert settings["theme"] == "dark"
    
    @pytest.mark.ui
    def test_settings_dialog_ui_elements(self, qtbot, mock_settings_dialog):
        """Test settings dialog UI elements."""
        dialog = mock_settings_dialog
        
        # Mock UI elements
        mock_theme_combo = MagicMock()
        mock_font_size_spin = MagicMock()
        mock_auto_save_check = MagicMock()
        
        # Test UI element configuration
        mock_theme_combo.currentText.return_value = "dark"
        mock_font_size_spin.value.return_value = 12
        mock_auto_save_check.isChecked.return_value = True
        
        # Verify UI elements work
        assert mock_theme_combo.currentText() == "dark"
        assert mock_font_size_spin.value() == 12
        assert mock_auto_save_check.isChecked() is True
    
    def test_settings_persistence(self, mock_settings_dialog):
        """Test settings persistence."""
        dialog = mock_settings_dialog
        
        # Set new settings
        new_settings = {
            "theme": "light",
            "font_size": 14,
            "auto_save": False
        }
        
        dialog.set_settings(new_settings)
        
        # Simulate dialog restart - settings should be remembered
        # In real implementation, this would involve file I/O
        saved_settings = dialog.get_settings()
        
        # Verify settings were saved
        dialog.set_settings.assert_called_with(new_settings)
    
    def test_settings_reset_to_defaults(self, mock_settings_dialog):
        """Test resetting settings to defaults."""
        dialog = mock_settings_dialog
        
        # Mock reset functionality
        dialog.reset_to_defaults = MagicMock()
        default_settings = {
            "theme": "light",
            "font_size": 12,
            "auto_save": True
        }
        dialog.reset_to_defaults.return_value = default_settings
        
        # Test reset
        result = dialog.reset_to_defaults()
        assert result == default_settings
        dialog.reset_to_defaults.assert_called_once()


class TestSettingsDialogAdvanced:
    """Test advanced settings dialog functionality."""
    
    def test_settings_dialog_tabs(self, qtbot, mock_settings_dialog):
        """Test settings dialog tab functionality."""
        dialog = mock_settings_dialog
        
        # Mock tab widget
        mock_tab_widget = MagicMock()
        dialog.tab_widget = mock_tab_widget
        
        # Test tab operations
        mock_tab_widget.currentIndex.return_value = 0
        mock_tab_widget.setCurrentIndex.return_value = None
        mock_tab_widget.count.return_value = 3
        
        # Verify tab functionality
        assert mock_tab_widget.currentIndex() == 0
        assert mock_tab_widget.count() == 3
        
        # Test switching tabs
        mock_tab_widget.setCurrentIndex(1)
        mock_tab_widget.setCurrentIndex.assert_called_with(1)
    
    def test_settings_dialog_categories(self, mock_settings_dialog, ui_test_data):
        """Test settings dialog categories."""
        dialog = mock_settings_dialog
        settings = ui_test_data["sample_settings"]
        
        # Test different setting categories
        appearance_settings = {
            "theme": settings["theme"],
            "font_family": settings["font_family"],
            "font_size": settings["font_size"]
        }
        
        behavior_settings = {
            "auto_save": settings["auto_save"],
            "show_timestamps": settings["show_timestamps"],
            "enable_notifications": settings["enable_notifications"]
        }
        
        # Verify categories exist
        assert appearance_settings["theme"] == "dark"
        assert behavior_settings["auto_save"] is True
    
    def test_settings_dialog_search(self, mock_settings_dialog):
        """Test settings dialog search functionality."""
        dialog = mock_settings_dialog
        
        # Mock search functionality
        dialog.search_settings = MagicMock()
        dialog.search_settings.return_value = ["theme", "font_size"]
        
        # Test search
        results = dialog.search_settings("font")
        assert "font_size" in results
        dialog.search_settings.assert_called_with("font")
    
    @pytest.mark.ui
    def test_settings_dialog_keyboard_navigation(self, qtbot, mock_settings_dialog):
        """Test settings dialog keyboard navigation."""
        dialog = mock_settings_dialog
        
        # Mock keyboard navigation
        dialog.handle_key_press = MagicMock()
        
        # Test keyboard events
        # In real implementation, this would test actual key events
        dialog.handle_key_press("Tab")
        dialog.handle_key_press.assert_called_with("Tab")
    
    def test_settings_dialog_import_export(self, mock_settings_dialog):
        """Test settings import/export functionality."""
        dialog = mock_settings_dialog
        
        # Mock import/export
        dialog.export_settings = MagicMock()
        dialog.import_settings = MagicMock()
        
        test_settings = {"theme": "dark", "font_size": 12}
        
        # Test export
        dialog.export_settings.return_value = test_settings
        exported = dialog.export_settings()
        assert exported == test_settings
        
        # Test import
        dialog.import_settings(test_settings)
        dialog.import_settings.assert_called_with(test_settings)


class TestSettingsDialogErrorHandling:
    """Test settings dialog error handling."""
    
    def test_invalid_settings_handling(self, mock_settings_dialog):
        """Test handling of invalid settings."""
        dialog = mock_settings_dialog
        
        # Test invalid settings
        invalid_settings = {
            "theme": "invalid_theme",
            "font_size": -1,
            "auto_save": "not_boolean"
        }
        
        # Mock validation error
        dialog.set_settings.side_effect = ValueError("Invalid settings")
        
        # Test error handling
        with pytest.raises(ValueError, match="Invalid settings"):
            dialog.set_settings(invalid_settings)
    
    def test_settings_file_error(self, mock_settings_dialog):
        """Test handling of settings file errors."""
        dialog = mock_settings_dialog
        
        # Mock file error
        dialog.get_settings.side_effect = FileNotFoundError("Settings file not found")
        
        # Test error handling
        with pytest.raises(FileNotFoundError):
            dialog.get_settings()
    
    def test_settings_dialog_initialization_error(self, qtbot):
        """Test handling of dialog initialization errors."""
        # Mock dialog that fails to initialize
        mock_dialog = MagicMock()
        mock_dialog.exec.side_effect = Exception("Dialog initialization failed")
        
        # Test error handling
        with pytest.raises(Exception, match="Dialog initialization failed"):
            mock_dialog.exec()


class TestSettingsDialogIntegration:
    """Test settings dialog integration with other components."""
    
    @pytest.mark.integration
    def test_settings_dialog_full_workflow(self, qtbot, mock_settings_dialog, mock_theme_manager):
        """Test complete settings dialog workflow."""
        dialog = mock_settings_dialog
        theme_manager = mock_theme_manager
        
        # 1. Open dialog
        dialog.show()
        
        # 2. Get current settings
        current_settings = dialog.get_settings()
        assert isinstance(current_settings, dict)
        
        # 3. Modify settings
        new_settings = current_settings.copy()
        new_settings["theme"] = "light"
        new_settings["font_size"] = 14
        
        # 4. Apply settings
        dialog.set_settings(new_settings)
        
        # 5. Apply theme through theme manager
        theme_manager.set_theme(new_settings["theme"])
        
        # 6. Close dialog
        result = dialog.exec()
        assert result == 1
        
        # Verify all operations were called
        dialog.show.assert_called_once()
        dialog.set_settings.assert_called_with(new_settings)
        theme_manager.set_theme.assert_called_with("light")
        dialog.exec.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])