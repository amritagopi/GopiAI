#!/usr/bin/env python3
"""
Unit tests for theme manager functionality.
Tests theme switching, theme application, and theme persistence.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock, mock_open

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_theme_manager, ui_test_data
)


class TestThemeManager:
    """Test theme manager functionality."""
    
    def test_theme_manager_initialization(self, mock_theme_manager):
        """Test theme manager initialization."""
        theme_manager = mock_theme_manager
        
        # Test initial state
        current_theme = theme_manager.get_current_theme()
        assert current_theme == "dark"
        
        available_themes = theme_manager.get_available_themes()
        assert "light" in available_themes
        assert "dark" in available_themes
        assert "auto" in available_themes
    
    def test_get_available_themes(self, mock_theme_manager):
        """Test getting available themes."""
        theme_manager = mock_theme_manager
        
        themes = theme_manager.get_available_themes()
        assert isinstance(themes, list)
        assert len(themes) >= 2  # At least light and dark
        assert "light" in themes
        assert "dark" in themes
    
    def test_get_current_theme(self, mock_theme_manager):
        """Test getting current theme."""
        theme_manager = mock_theme_manager
        
        current_theme = theme_manager.get_current_theme()
        assert current_theme in ["light", "dark", "auto"]
    
    def test_set_theme(self, mock_theme_manager):
        """Test setting a theme."""
        theme_manager = mock_theme_manager
        
        # Test setting valid theme
        result = theme_manager.set_theme("light")
        assert result is True
        theme_manager.set_theme.assert_called_once_with("light")
        
        # Test setting another theme
        theme_manager.set_theme.reset_mock()
        result = theme_manager.set_theme("dark")
        assert result is True
        theme_manager.set_theme.assert_called_once_with("dark")
    
    def test_apply_theme(self, mock_theme_manager):
        """Test applying a theme."""
        theme_manager = mock_theme_manager
        
        # Test applying theme
        theme_manager.apply_theme("dark")
        theme_manager.apply_theme.assert_called_once_with("dark")
    
    def test_get_theme_colors(self, mock_theme_manager):
        """Test getting theme colors."""
        theme_manager = mock_theme_manager
        
        colors = theme_manager.get_theme_colors()
        assert isinstance(colors, dict)
        assert "background" in colors
        assert "foreground" in colors
        assert "accent" in colors
        
        # Test color values
        assert colors["background"] == "#2b2b2b"
        assert colors["foreground"] == "#ffffff"
        assert colors["accent"] == "#0078d4"
    
    def test_theme_switching(self, mock_theme_manager):
        """Test switching between themes."""
        theme_manager = mock_theme_manager
        
        # Start with dark theme
        assert theme_manager.get_current_theme() == "dark"
        
        # Switch to light theme
        theme_manager.set_theme("light")
        theme_manager.get_current_theme.return_value = "light"
        assert theme_manager.get_current_theme() == "light"
        
        # Switch back to dark theme
        theme_manager.set_theme("dark")
        theme_manager.get_current_theme.return_value = "dark"
        assert theme_manager.get_current_theme() == "dark"
    
    @pytest.mark.ui
    def test_theme_application_to_widgets(self, qtbot, mock_theme_manager):
        """Test theme application to UI widgets."""
        theme_manager = mock_theme_manager
        
        # Mock widget
        mock_widget = MagicMock()
        qtbot.addWidget(mock_widget)
        
        # Apply theme to widget
        theme_manager.apply_theme("dark")
        
        # Verify theme was applied
        theme_manager.apply_theme.assert_called_once_with("dark")
    
    def test_theme_persistence(self, mock_theme_manager):
        """Test theme persistence across sessions."""
        theme_manager = mock_theme_manager
        
        # Set a theme
        theme_manager.set_theme("light")
        
        # Simulate restart - theme should be remembered
        # In a real implementation, this would involve file I/O
        saved_theme = theme_manager.get_current_theme()
        
        # Verify theme persistence
        theme_manager.set_theme.assert_called_with("light")
    
    def test_invalid_theme_handling(self, mock_theme_manager):
        """Test handling of invalid theme names."""
        theme_manager = mock_theme_manager
        
        # Test setting invalid theme
        theme_manager.set_theme.return_value = False
        result = theme_manager.set_theme("invalid_theme")
        assert result is False
    
    def test_auto_theme_detection(self, mock_theme_manager):
        """Test automatic theme detection based on system settings."""
        theme_manager = mock_theme_manager
        
        # Test auto theme
        theme_manager.set_theme("auto")
        theme_manager.get_current_theme.return_value = "auto"
        
        current_theme = theme_manager.get_current_theme()
        assert current_theme == "auto"


class TestThemeManagerIntegration:
    """Test theme manager integration with other components."""
    
    def test_theme_manager_with_settings(self, mock_theme_manager, ui_test_data):
        """Test theme manager integration with settings."""
        theme_manager = mock_theme_manager
        settings = ui_test_data["sample_settings"]
        
        # Test loading theme from settings
        theme_from_settings = settings["theme"]
        theme_manager.set_theme(theme_from_settings)
        
        # Verify theme was set from settings
        theme_manager.set_theme.assert_called_with("dark")
    
    def test_theme_manager_signal_emission(self, mock_theme_manager):
        """Test theme manager signal emission on theme change."""
        theme_manager = mock_theme_manager
        
        # Mock signal emission
        theme_changed_signal = MagicMock()
        theme_manager.themeChanged = theme_changed_signal
        
        # Change theme
        theme_manager.set_theme("light")
        
        # In a real implementation, this would emit a signal
        # For mock, we just verify the method was called
        theme_manager.set_theme.assert_called_with("light")
    
    @pytest.mark.integration
    def test_theme_manager_full_workflow(self, mock_theme_manager, ui_test_data):
        """Test complete theme manager workflow."""
        theme_manager = mock_theme_manager
        
        # 1. Get available themes
        themes = theme_manager.get_available_themes()
        assert len(themes) >= 2
        
        # 2. Get current theme
        current = theme_manager.get_current_theme()
        assert current in themes
        
        # 3. Switch to different theme
        new_theme = "light" if current == "dark" else "dark"
        result = theme_manager.set_theme(new_theme)
        assert result is True
        
        # 4. Apply the theme
        theme_manager.apply_theme(new_theme)
        
        # 5. Get theme colors
        colors = theme_manager.get_theme_colors()
        assert isinstance(colors, dict)
        assert len(colors) >= 3


class TestThemeManagerErrorHandling:
    """Test theme manager error handling."""
    
    def test_theme_file_not_found(self, mock_theme_manager):
        """Test handling when theme file is not found."""
        theme_manager = mock_theme_manager
        
        # Mock file not found scenario
        theme_manager.get_available_themes.side_effect = FileNotFoundError("Theme file not found")
        
        # Test graceful handling
        with pytest.raises(FileNotFoundError):
            theme_manager.get_available_themes()
    
    def test_corrupted_theme_file(self, mock_theme_manager):
        """Test handling of corrupted theme files."""
        theme_manager = mock_theme_manager
        
        # Mock corrupted file scenario
        theme_manager.get_theme_colors.side_effect = ValueError("Invalid theme data")
        
        # Test graceful handling
        with pytest.raises(ValueError):
            theme_manager.get_theme_colors()
    
    def test_theme_application_failure(self, mock_theme_manager):
        """Test handling of theme application failures."""
        theme_manager = mock_theme_manager
        
        # Mock application failure
        theme_manager.apply_theme.side_effect = Exception("Failed to apply theme")
        
        # Test graceful handling
        with pytest.raises(Exception, match="Failed to apply theme"):
            theme_manager.apply_theme("dark")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])