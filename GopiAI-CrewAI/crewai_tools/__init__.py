"""
CrewAI Tools for GopiAI
Provides native tool integrations and model management for GopiAI
"""

from .model_manager import ModelManager, ModelConfiguration, ModelProvider, get_model_manager
from .tool_integration import ToolManager, get_tool_manager, ToolIntegration, WebSearchTool, FileReadTool

# Initialize default instances
model_manager = get_model_manager()
tool_manager = get_tool_manager()

__all__ = [
    'ModelManager',
    'ModelConfiguration',
    'ModelProvider',
    'get_model_manager',
    'ToolManager',
    'ToolIntegration',
    'WebSearchTool',
    'FileReadTool',
    'get_tool_manager',
    'model_manager',
    'tool_manager'
]
