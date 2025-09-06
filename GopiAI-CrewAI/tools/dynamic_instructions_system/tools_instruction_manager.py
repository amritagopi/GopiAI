#!/usr/bin/env python3
"""
Менеджер динамических инструкций для инструментов

Этот модуль предоставляет функциональность для управления динамическими инструкциями
для различных инструментов в системе GopiAI.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ToolsInstructionManager:
    """Менеджер для управления инструкциями инструментов"""
    
    def __init__(self):
        """Инициализация менеджера инструкций"""
        self.instructions: Dict[str, str] = {}
        self.loaded = False
        logger.info("ToolsInstructionManager инициализирован")
    
    def get_instructions(self, tool_name: str) -> Optional[str]:
        """
        Получить инструкции для конкретного инструмента
        
        Args:
            tool_name: Название инструмента
            
        Returns:
            Строка с инструкциями или None если не найдено
        """
        return self.instructions.get(tool_name)
    
    def set_instructions(self, tool_name: str, instructions: str) -> None:
        """
        Установить инструкции для инструмента
        
        Args:
            tool_name: Название инструмента
            instructions: Текст инструкций
        """
        self.instructions[tool_name] = instructions
        logger.debug(f"Установлены инструкции для инструмента: {tool_name}")
    
    def load_default_instructions(self) -> None:
        """Загрузить инструкции по умолчанию"""
        default_instructions = {
            "filesystem_tools": "Используй инструменты для работы с файловой системой осторожно. Всегда проверяй пути.",
            "web_search_tools": "При поиске в интернете используй релевантные ключевые слова.",
            "code_execution_tools": "Выполняй код только после проверки безопасности.",
            "terminal_tools": "Используй терминальные команды с осторожностью."
        }
        
        self.instructions.update(default_instructions)
        self.loaded = True
        logger.info(f"Загружены инструкции по умолчанию для {len(default_instructions)} инструментов")
    
    def get_all_instructions(self) -> Dict[str, str]:
        """
        Получить все загруженные инструкции
        
        Returns:
            Словарь со всеми инструкциями
        """
        if not self.loaded:
            self.load_default_instructions()
        
        return self.instructions.copy()
    
    def is_loaded(self) -> bool:
        """Проверить, загружены ли инструкции"""
        return self.loaded
    
    def get_tool_detailed_instructions(self, tool_name: str) -> Optional[str]:
        """
        Получить детальные инструкции для конкретного инструмента (алиас для get_instructions)
        
        Args:
            tool_name: Название инструмента
            
        Returns:
            Строка с инструкциями или None если не найдено
        """
        return self.get_instructions(tool_name)
    
    def get_tools_summary(self) -> str:
        """
        Получить краткое описание всех доступных инструментов
        
        Returns:
            Строка с описанием инструментов
        """
        if not self.loaded:
            self.load_default_instructions()
        
        summary_lines = ["Доступные инструменты и их назначение:"]
        
        tool_descriptions = {
            "filesystem_tools": "Работа с файловой системой - создание, чтение, запись файлов",
            "web_search_tools": "Поиск информации в интернете",
            "code_execution_tools": "Выполнение кода и вычислений",
            "terminal_tools": "Выполнение команд в терминале"
        }
        
        for tool_name, instructions in self.instructions.items():
            description = tool_descriptions.get(tool_name, "Специализированный инструмент")
            summary_lines.append(f"- {tool_name}: {description}")
        
        return "\n".join(summary_lines)

# Глобальный экземпляр менеджера
_manager_instance: Optional[ToolsInstructionManager] = None

def get_tools_instruction_manager() -> ToolsInstructionManager:
    """Получить глобальный экземпляр менеджера инструкций"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ToolsInstructionManager()
        _manager_instance.load_default_instructions()
    return _manager_instance

def get_dynamic_tool_instructions() -> Dict[str, str]:
    """
    Получить все динамические инструкции для инструментов
    
    Returns:
        Словарь с инструкциями для инструментов
    """
    manager = get_tools_instruction_manager()
    return manager.get_all_instructions()