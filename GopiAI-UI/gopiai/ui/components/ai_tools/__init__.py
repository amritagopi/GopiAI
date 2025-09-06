"""
UI Tools for AI Assistant

This module provides UI-specific tools that the AI can use to assist the user.
"""
from PySide6.QtCore import QObject, Signal
from ..utils.logger import get_logger

logger = get_logger(__name__)

class UIAssistant(QObject):
    """
    A class that provides UI assistant functionality with signals for communication.
    """
    # Define signals
    action_started = Signal(str)  # Emitted when an action starts
    action_completed = Signal(str, bool)  # Emitted when an action completes (message, success)
    visual_feedback = Signal(str, dict)  # Emitted for visual feedback (type, data)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_window = None
    
    def set_main_window(self, window):
        """Set the main window for the UI Assistant."""
        self._main_window = window
    
    def get_tool_definition(self):
        """
        Get the tool definition that describes what this tool can do.
        
        Returns:
            dict: A dictionary describing the tool's capabilities.
        """
        return {
            'name': 'ui_assistant',
            'description': 'A tool for interacting with the user interface.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'description': 'The action to perform',
                        'enum': ['navigate', 'click', 'type', 'select']
                    },
                    'target': {
                        'type': 'string',
                        'description': 'The target element or text to interact with'
                    },
                    'value': {
                        'type': 'string',
                        'description': 'The value to enter or select',
                        'default': ''
                    }
                },
                'required': ['action', 'target']
            }
        }

def get_ui_assistant():
    """
    Get the UI assistant tool.
    
    Returns:
        UIAssistant: An instance of the UIAssistant class with the required signals.
    """
    return UIAssistant()
