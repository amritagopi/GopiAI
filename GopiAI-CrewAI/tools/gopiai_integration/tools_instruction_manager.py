"""
📚 Tools Instruction Manager
Менеджер для управления инструкциями по использованию инструментов
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ToolsInstructionManager:
    """
    Менеджер для управления инструкциями по использованию инструментов
    
    Возможности:
    - Получение инструкций по использованию инструментов
    - Динамическая загрузка инструкций
    - Категоризация инструкций
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.instructions = {}
        self._load_instructions()
        self.logger.info(f"✅ Tools Instruction Manager инициализирован. Найдено {len(self.instructions)} инструкций")
    
    def _load_instructions(self):
        """Загружает инструкции по использованию инструментов"""
        self.instructions = {
            "execute_shell": self._get_execute_shell_instructions(),
            "web_scraper": self._get_web_scraper_instructions(),
            "web_search": self._get_web_search_instructions(),
            "api_client": self._get_api_client_instructions(),
            "url_analyzer": self._get_url_analyzer_instructions(),
            "file_operations": self._get_file_operations_instructions(),
            "system_info": self._get_system_info_instructions(),
            "process_manager": self._get_process_manager_instructions(),
            "time_helper": self._get_time_helper_instructions(),
            "project_helper": self._get_project_helper_instructions()
        }

    def get_tools_summary(self) -> Dict[str, str]:
        """
        Возвращает сводку по доступным инструментам в формате {tool_name: description}.
        Совместимо с ожиданиями вызывающего кода в `system_prompts.py`.
        """
        try:
            # Текущая структура уже хранит строки-описания
            return dict(self.instructions)
        except Exception as e:
            self.logger.error(f"Ошибка в get_tools_summary: {e}", exc_info=True)
            return {}

    def _get_execute_shell_instructions(self) -> str:
        """Детальные инструкции для execute_shell"""
        return "Используйте execute_shell для выполнения команд оболочки. Пример: execute_shell('ls -l')"

    def _get_web_scraper_instructions(self) -> str:
        """Детальные инструкции для web_scraper"""
        return "Используйте web_scraper для выполнения веб-скрапинга. Пример: web_scraper('https://example.com')"

    def _get_web_search_instructions(self) -> str:
        """Детальные инструкции для web_search"""
        return "Используйте web_search для выполнения поиска в интернете. Пример: web_search('Python programming')"

    def _get_api_client_instructions(self) -> str:
        """Детальные инструкции для api_client"""
        return "Используйте api_client для взаимодействия с API. Пример: api_client('https://api.example.com', method='GET')"

    def _get_url_analyzer_instructions(self) -> str:
        """Детальные инструкции для url_analyzer"""
        return "Используйте url_analyzer для анализа URL. Пример: url_analyzer('https://example.com')"

    def _get_file_operations_instructions(self) -> str:
        """Детальные инструкции для file_operations"""
        return "Используйте file_operations для выполнения операций с файлами. Пример: file_operations('read', 'file.txt')"

    def _get_system_info_instructions(self) -> str:
        """Детальные инструкции для system_info"""
        return "Используйте system_info для получения информации о системе. Пример: system_info('os')"

    def _get_process_manager_instructions(self) -> str:
        """Детальные инструкции для process_manager"""
        return "Используйте process_manager для управления процессами. Пример: process_manager('start', 'process_name')"

    def _get_time_helper_instructions(self) -> str:
        """Детальные инструкции для time_helper"""
        return "Используйте time_helper для работы с временем. Пример: time_helper('now')"

    def _get_project_helper_instructions(self) -> str:
        """Детальные инструкции для project_helper"""
        return "Используйте project_helper для помощи в управлении проектами. Пример: project_helper('create', 'project_name')"

    def get_instruction(self, tool_name: str) -> Optional[str]:
        """Получает инструкцию по использованию инструмента"""
        return self.instructions.get(tool_name)

    def get_all_instructions(self) -> Dict[str, str]:
        """Получает все инструкции"""
        return self.instructions

# Глобальный синглтон менеджера
_TOOLS_MANAGER_SINGLETON: Optional[ToolsInstructionManager] = None

def get_tools_instruction_manager() -> ToolsInstructionManager:
    """
    Фабрика (синглтон) для получения экземпляра ToolsInstructionManager.
    Соответствует импорту в `system_prompts.py`:
    `from tools.gopiai_integration.tools_instruction_manager import get_tools_instruction_manager`
    """
    global _TOOLS_MANAGER_SINGLETON
    if _TOOLS_MANAGER_SINGLETON is None:
        _TOOLS_MANAGER_SINGLETON = ToolsInstructionManager()
    return _TOOLS_MANAGER_SINGLETON
