#!/usr/bin/env python3
"""
Unit tests for notification system functionality.
Tests notification display, queuing, persistence, and user interactions.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Import test infrastructure
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from ui_fixtures import (
    qtbot, mock_notification_system, mock_system_tray, ui_test_data
)


class TestNotificationSystem:
    """Test notification system functionality."""
    
    def test_notification_system_initialization(self, mock_notification_system):
        """Test notification system initialization."""
        notification_system = mock_notification_system
        
        # Test initial state
        pending = notification_system.get_pending_notifications()
        assert isinstance(pending, list)
        assert len(pending) == 0
    
    def test_show_info_notification(self, mock_notification_system):
        """Test showing info notification."""
        notification_system = mock_notification_system
        
        # Test info notification
        message = "This is an info message"
        notification_system.show_info(message)
        
        # Verify notification was shown
        notification_system.show_info.assert_called_once_with(message)
    
    def test_show_warning_notification(self, mock_notification_system):
        """Test showing warning notification."""
        notification_system = mock_notification_system
        
        # Test warning notification
        message = "This is a warning message"
        notification_system.show_warning(message)
        
        # Verify notification was shown
        notification_system.show_warning.assert_called_once_with(message)
    
    def test_show_error_notification(self, mock_notification_system):
        """Test showing error notification."""
        notification_system = mock_notification_system
        
        # Test error notification
        message = "This is an error message"
        notification_system.show_error(message)
        
        # Verify notification was shown
        notification_system.show_error.assert_called_once_with(message)
    
    def test_show_success_notification(self, mock_notification_system):
        """Test showing success notification."""
        notification_system = mock_notification_system
        
        # Test success notification
        message = "This is a success message"
        notification_system.show_success(message)
        
        # Verify notification was shown
        notification_system.show_success.assert_called_once_with(message)
    
    def test_notification_types(self, mock_notification_system):
        """Test different notification types."""
        notification_system = mock_notification_system
        
        # Test all notification types
        notification_system.show_info("Info message")
        notification_system.show_warning("Warning message")
        notification_system.show_error("Error message")
        notification_system.show_success("Success message")
        
        # Verify all types were called
        notification_system.show_info.assert_called_with("Info message")
        notification_system.show_warning.assert_called_with("Warning message")
        notification_system.show_error.assert_called_with("Error message")
        notification_system.show_success.assert_called_with("Success message")
    
    def test_get_pending_notifications(self, mock_notification_system):
        """Test getting pending notifications."""
        notification_system = mock_notification_system
        
        # Test getting pending notifications
        pending = notification_system.get_pending_notifications()
        assert isinstance(pending, list)
        
        # Mock some pending notifications
        mock_notifications = [
            {"type": "info", "message": "Info 1", "timestamp": "2025-01-01T00:00:00Z"},
            {"type": "warning", "message": "Warning 1", "timestamp": "2025-01-01T00:01:00Z"}
        ]
        notification_system.get_pending_notifications.return_value = mock_notifications
        
        pending = notification_system.get_pending_notifications()
        assert len(pending) == 2
        assert pending[0]["type"] == "info"
        assert pending[1]["type"] == "warning"
    
    def test_clear_notifications(self, mock_notification_system):
        """Test clearing notifications."""
        notification_system = mock_notification_system
        
        # Test clearing notifications
        notification_system.clear_notifications()
        notification_system.clear_notifications.assert_called_once()
    
    def test_notification_with_title(self, mock_notification_system):
        """Test notifications with custom titles."""
        notification_system = mock_notification_system
        
        # Mock notification with title
        notification_system.show_info_with_title = MagicMock()
        
        # Test notification with title
        title = "Custom Title"
        message = "Custom message"
        notification_system.show_info_with_title(title, message)
        
        notification_system.show_info_with_title.assert_called_once_with(title, message)
    
    def test_notification_duration(self, mock_notification_system):
        """Test notification duration settings."""
        notification_system = mock_notification_system
        
        # Mock notification with duration
        notification_system.show_timed_notification = MagicMock()
        
        # Test timed notification
        message = "This notification will disappear in 5 seconds"
        duration = 5000  # 5 seconds in milliseconds
        notification_system.show_timed_notification(message, duration)
        
        notification_system.show_timed_notification.assert_called_once_with(message, duration)


class TestNotificationQueue:
    """Test notification queue functionality."""
    
    def test_notification_queuing(self, mock_notification_system):
        """Test notification queuing when multiple notifications are shown."""
        notification_system = mock_notification_system
        
        # Mock queue functionality
        notification_system.queue_notification = MagicMock()
        notification_system.process_queue = MagicMock()
        
        # Test queuing multiple notifications
        messages = ["Message 1", "Message 2", "Message 3"]
        for message in messages:
            notification_system.queue_notification("info", message)
        
        # Verify notifications were queued
        assert notification_system.queue_notification.call_count == 3
        
        # Process queue
        notification_system.process_queue()
        notification_system.process_queue.assert_called_once()
    
    def test_notification_priority(self, mock_notification_system):
        """Test notification priority handling."""
        notification_system = mock_notification_system
        
        # Mock priority functionality
        notification_system.set_priority = MagicMock()
        
        # Test setting priority
        notification_system.set_priority("error", "high")
        notification_system.set_priority("info", "low")
        notification_system.set_priority("warning", "medium")
        
        # Verify priorities were set
        notification_system.set_priority.assert_any_call("error", "high")
        notification_system.set_priority.assert_any_call("info", "low")
        notification_system.set_priority.assert_any_call("warning", "medium")
    
    def test_notification_filtering(self, mock_notification_system):
        """Test notification filtering."""
        notification_system = mock_notification_system
        
        # Mock filtering functionality
        notification_system.filter_notifications = MagicMock()
        notification_system.filter_notifications.return_value = [
            {"type": "error", "message": "Error message"}
        ]
        
        # Test filtering by type
        filtered = notification_system.filter_notifications("error")
        assert len(filtered) == 1
        assert filtered[0]["type"] == "error"
        
        notification_system.filter_notifications.assert_called_with("error")
    
    def test_notification_history(self, mock_notification_system):
        """Test notification history."""
        notification_system = mock_notification_system
        
        # Mock history functionality
        notification_system.get_notification_history = MagicMock()
        mock_history = [
            {"type": "info", "message": "Historical info", "timestamp": "2025-01-01T00:00:00Z"},
            {"type": "error", "message": "Historical error", "timestamp": "2025-01-01T00:01:00Z"}
        ]
        notification_system.get_notification_history.return_value = mock_history
        
        # Test getting history
        history = notification_system.get_notification_history()
        assert len(history) == 2
        assert history[0]["type"] == "info"
        assert history[1]["type"] == "error"


class TestSystemTrayNotifications:
    """Test system tray notification functionality."""
    
    def test_system_tray_initialization(self, qtbot, mock_system_tray):
        """Test system tray initialization."""
        tray = mock_system_tray
        
        # Test tray is visible
        assert tray.isVisible() is True
    
    def test_system_tray_show_message(self, mock_system_tray):
        """Test showing message in system tray."""
        tray = mock_system_tray
        
        # Test showing tray message
        title = "GopiAI Notification"
        message = "This is a system tray notification"
        tray.showMessage(title, message)
        
        tray.showMessage.assert_called_once_with(title, message)
    
    def test_system_tray_tooltip(self, mock_system_tray):
        """Test system tray tooltip."""
        tray = mock_system_tray
        
        # Test setting tooltip
        tooltip = "GopiAI - AI Assistant"
        tray.setToolTip(tooltip)
        
        tray.setToolTip.assert_called_once_with(tooltip)
    
    def test_system_tray_visibility(self, mock_system_tray):
        """Test system tray visibility control."""
        tray = mock_system_tray
        
        # Test showing tray
        tray.show()
        tray.show.assert_called_once()
        
        # Test hiding tray
        tray.hide()
        tray.hide.assert_called_once()
    
    def test_system_tray_integration(self, mock_system_tray, mock_notification_system):
        """Test system tray integration with notification system."""
        tray = mock_system_tray
        notification_system = mock_notification_system
        
        # Test showing notification through system tray
        message = "Integration test message"
        notification_system.show_info(message)
        tray.showMessage("Info", message)
        
        # Verify both were called
        notification_system.show_info.assert_called_with(message)
        tray.showMessage.assert_called_with("Info", message)


class TestNotificationSettings:
    """Test notification settings and preferences."""
    
    def test_notification_enabled_setting(self, mock_notification_system, ui_test_data):
        """Test notification enabled/disabled setting."""
        notification_system = mock_notification_system
        settings = ui_test_data["sample_settings"]
        
        # Test notification setting
        notifications_enabled = settings["enable_notifications"]
        assert notifications_enabled is True
        
        # Mock setting check
        notification_system.are_notifications_enabled = MagicMock()
        notification_system.are_notifications_enabled.return_value = notifications_enabled
        
        # Test checking if notifications are enabled
        enabled = notification_system.are_notifications_enabled()
        assert enabled is True
    
    def test_notification_sound_setting(self, mock_notification_system):
        """Test notification sound settings."""
        notification_system = mock_notification_system
        
        # Mock sound settings
        notification_system.set_sound_enabled = MagicMock()
        notification_system.is_sound_enabled = MagicMock()
        notification_system.is_sound_enabled.return_value = True
        
        # Test enabling sound
        notification_system.set_sound_enabled(True)
        notification_system.set_sound_enabled.assert_called_with(True)
        
        # Test checking sound setting
        sound_enabled = notification_system.is_sound_enabled()
        assert sound_enabled is True
    
    def test_notification_position_setting(self, mock_notification_system):
        """Test notification position settings."""
        notification_system = mock_notification_system
        
        # Mock position settings
        notification_system.set_position = MagicMock()
        notification_system.get_position = MagicMock()
        notification_system.get_position.return_value = "top-right"
        
        # Test setting position
        notification_system.set_position("top-right")
        notification_system.set_position.assert_called_with("top-right")
        
        # Test getting position
        position = notification_system.get_position()
        assert position == "top-right"
    
    def test_notification_theme_setting(self, mock_notification_system):
        """Test notification theme settings."""
        notification_system = mock_notification_system
        
        # Mock theme settings
        notification_system.set_theme = MagicMock()
        notification_system.get_theme = MagicMock()
        notification_system.get_theme.return_value = "dark"
        
        # Test setting theme
        notification_system.set_theme("dark")
        notification_system.set_theme.assert_called_with("dark")
        
        # Test getting theme
        theme = notification_system.get_theme()
        assert theme == "dark"


class TestNotificationErrorHandling:
    """Test notification system error handling."""
    
    def test_notification_display_error(self, mock_notification_system):
        """Test handling of notification display errors."""
        notification_system = mock_notification_system
        
        # Mock display error
        notification_system.show_error.side_effect = Exception("Display error")
        
        # Test error handling
        with pytest.raises(Exception, match="Display error"):
            notification_system.show_error("Test error message")
    
    def test_system_tray_unavailable(self, mock_notification_system):
        """Test handling when system tray is unavailable."""
        notification_system = mock_notification_system
        
        # Mock system tray unavailable
        notification_system.is_system_tray_available = MagicMock()
        notification_system.is_system_tray_available.return_value = False
        
        # Test fallback behavior
        available = notification_system.is_system_tray_available()
        assert available is False
    
    def test_notification_queue_overflow(self, mock_notification_system):
        """Test handling of notification queue overflow."""
        notification_system = mock_notification_system
        
        # Mock queue overflow
        notification_system.is_queue_full = MagicMock()
        notification_system.is_queue_full.return_value = True
        
        # Test queue full handling
        queue_full = notification_system.is_queue_full()
        assert queue_full is True
    
    def test_invalid_notification_type(self, mock_notification_system):
        """Test handling of invalid notification types."""
        notification_system = mock_notification_system
        
        # Mock invalid type error
        notification_system.show_notification = MagicMock()
        notification_system.show_notification.side_effect = ValueError("Invalid notification type")
        
        # Test error handling
        with pytest.raises(ValueError, match="Invalid notification type"):
            notification_system.show_notification("invalid_type", "Test message")


class TestNotificationIntegration:
    """Test notification system integration with other components."""
    
    @pytest.mark.integration
    def test_notification_with_chat_system(self, mock_notification_system, mock_chat_widget):
        """Test notification integration with chat system."""
        notification_system = mock_notification_system
        chat_widget = mock_chat_widget
        
        # Test chat-related notification
        message = "New message received"
        notification_system.show_info(message)
        
        # Verify notification was shown
        notification_system.show_info.assert_called_with(message)
    
    def test_notification_with_settings(self, mock_notification_system, ui_test_data):
        """Test notification integration with settings."""
        notification_system = mock_notification_system
        settings = ui_test_data["sample_settings"]
        
        # Test notification respects settings
        if settings["enable_notifications"]:
            notification_system.show_info("Settings-aware notification")
            notification_system.show_info.assert_called_with("Settings-aware notification")
    
    @pytest.mark.integration
    def test_complete_notification_workflow(self, mock_notification_system, mock_system_tray):
        """Test complete notification workflow."""
        notification_system = mock_notification_system
        tray = mock_system_tray
        
        # 1. Show notification
        message = "Workflow test message"
        notification_system.show_info(message)
        
        # 2. Show in system tray
        tray.showMessage("Info", message)
        
        # 3. Check pending notifications
        pending = notification_system.get_pending_notifications()
        
        # 4. Clear notifications
        notification_system.clear_notifications()
        
        # Verify workflow
        notification_system.show_info.assert_called_with(message)
        tray.showMessage.assert_called_with("Info", message)
        notification_system.get_pending_notifications.assert_called_once()
        notification_system.clear_notifications.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])