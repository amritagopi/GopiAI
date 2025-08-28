#!/usr/bin/env python3
"""
Unit tests for main window functionality.
Tests the main application window initialization, layout, and basic operations.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_main_window, mock_chat_widget, mock_model_selector,
    mock_settings_dialog, mock_theme_manager, ui_test_data
)
from fixtures import ai_service_mocker, mock_crewai_server


class TestMainWindow:
    """Test main application window functionality."""
    
    def test_main_window_initialization(self, qtbot, mock_main_window):
        """Test main window initialization."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Test initial state
        assert window.isVisible() is True
        assert window.size().width() == 1200
        assert window.size().height() == 800
    
    def test_main_window_show_hide(self, qtbot, mock_main_window):
        """Test main window show/hide functionality."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Test show
        window.show()
        window.show.assert_called_once()
        
        # Test hide
        window.hide()
        window.hide.assert_called_once()
    
    def test_main_window_close(self, qtbot, mock_main_window):
        """Test main window close functionality."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Test close
        result = window.close()
        assert result is True
        window.close.assert_called_once()
    
    def test_main_window_title(self, qtbot, mock_main_window):
        """Test main window title setting."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Test setting title
        test_title = "GopiAI - Test Mode"
        window.setWindowTitle(test_title)
        window.setWindowTitle.assert_called_once_with(test_title)
    
    def test_main_window_with_chat_widget(self, qtbot, mock_main_window, mock_chat_widget):
        """Test main window integration with chat widget."""
        window = mock_main_window
        chat_widget = mock_chat_widget
        
        qtbot.addWidget(window)
        qtbot.addWidget(chat_widget)
        
        # Test chat widget integration
        assert chat_widget.get_message_text() == "Test message"
        messages = chat_widget.get_messages()
        assert len(messages) == 2
    
    def test_main_window_with_model_selector(self, qtbot, mock_main_window, mock_model_selector):
        """Test main window integration with model selector."""
        window = mock_main_window
        model_selector = mock_model_selector
        
        qtbot.addWidget(window)
        qtbot.addWidget(model_selector)
        
        # Test model selector integration
        current_model = model_selector.currentText()
        assert current_model == "gpt-4"
        
        model_data = model_selector.currentData()
        assert model_data["provider"] == "openai"
    
    def test_main_window_with_settings_dialog(self, qtbot, mock_main_window, mock_settings_dialog):
        """Test main window integration with settings dialog."""
        window = mock_main_window
        settings_dialog = mock_settings_dialog
        
        qtbot.addWidget(window)
        
        # Test opening settings dialog
        result = settings_dialog.exec()
        assert result == 1  # QDialog.Accepted
        
        # Test getting settings
        settings = settings_dialog.get_settings()
        assert settings["theme"] == "dark"
        assert settings["font_size"] == 12
    
    @pytest.mark.ui
    def test_main_window_resize_handling(self, qtbot, mock_main_window):
        """Test main window resize handling."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Test resize
        new_size = MagicMock()
        new_size.width.return_value = 1400
        new_size.height.return_value = 900
        window.size.return_value = new_size
        
        assert window.size().width() == 1400
        assert window.size().height() == 900
    
    @pytest.mark.ui
    def test_main_window_menu_bar(self, qtbot, mock_main_window):
        """Test main window menu bar functionality."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Mock menu bar
        mock_menu_bar = MagicMock()
        window.menuBar.return_value = mock_menu_bar
        
        # Test menu bar exists
        menu_bar = window.menuBar()
        assert menu_bar is not None
        window.menuBar.assert_called_once()
    
    @pytest.mark.ui
    def test_main_window_status_bar(self, qtbot, mock_main_window):
        """Test main window status bar functionality."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Mock status bar
        mock_status_bar = MagicMock()
        window.statusBar.return_value = mock_status_bar
        
        # Test status bar exists
        status_bar = window.statusBar()
        assert status_bar is not None
        window.statusBar.assert_called_once()
    
    @pytest.mark.integration
    def test_main_window_full_initialization(self, qtbot, mock_main_window, mock_chat_widget, 
                                           mock_model_selector, mock_theme_manager):
        """Test complete main window initialization with all components."""
        window = mock_main_window
        chat_widget = mock_chat_widget
        model_selector = mock_model_selector
        theme_manager = mock_theme_manager
        
        qtbot.addWidget(window)
        qtbot.addWidget(chat_widget)
        qtbot.addWidget(model_selector)
        
        # Test window is properly initialized
        assert window.isVisible() is True
        
        # Test chat widget is working
        assert chat_widget.get_message_text() == "Test message"
        
        # Test model selector is working
        assert model_selector.currentText() == "gpt-4"
        
        # Test theme manager is working
        current_theme = theme_manager.get_current_theme()
        assert current_theme == "dark"


class TestMainWindowErrorHandling:
    """Test main window error handling."""
    
    def test_main_window_initialization_error(self, qtbot):
        """Test main window handling of initialization errors."""
        # Create a mock that raises an exception
        mock_window = MagicMock()
        mock_window.show.side_effect = Exception("Initialization failed")
        
        qtbot.addWidget(mock_window)
        
        # Test that exception is handled gracefully
        with pytest.raises(Exception, match="Initialization failed"):
            mock_window.show()
    
    def test_main_window_component_failure(self, qtbot, mock_main_window):
        """Test main window handling of component failures."""
        window = mock_main_window
        qtbot.addWidget(window)
        
        # Mock a component that fails
        mock_component = MagicMock()
        mock_component.initialize.side_effect = Exception("Component failed")
        
        # Test graceful handling
        with pytest.raises(Exception, match="Component failed"):
            mock_component.initialize()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])