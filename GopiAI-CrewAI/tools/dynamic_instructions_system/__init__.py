"""
Система динамических инструкций для инструментов GopiAI

Этот пакет предоставляет функциональность для управления
динамическими инструкциями для различных инструментов системы.
"""

from .tools_instruction_manager import (
    ToolsInstructionManager,
    get_tools_instruction_manager,
    get_dynamic_tool_instructions
)

__all__ = [
    'ToolsInstructionManager',
    'get_tools_instruction_manager', 
    'get_dynamic_tool_instructions'
]