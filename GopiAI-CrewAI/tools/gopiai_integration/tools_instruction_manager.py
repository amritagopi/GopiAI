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
            "project_helper": self._get_project_helper_instructions(),
            # Совместимость с UI: добавляем инструменты, которые ожидаются UI
            "browser_tools": self._get_browser_tools_instructions(),
            "page_analyzer": self._get_page_analyzer_instructions(),
        }

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

    def _get_browser_tools_instructions(self) -> str:
        """Детальные инструкции для browser_tools"""
        return (
            "Используйте browser_tools для автоматизации действий в браузере (открыть страницу, клик, ввод текста, скриншоты). "
            "Пример: browser_tools('open', url='https://example.com')"
        )

    def _get_page_analyzer_instructions(self) -> str:
        """Детальные инструкции для page_analyzer"""
        return (
            "Используйте page_analyzer для анализа веб-страниц (SEO, структура, заголовки, ссылки, скорость). "
            "Пример: page_analyzer(url='https://example.com')"
        )

    def get_instruction(self, tool_name: str) -> Optional[str]:
        """Получает инструкцию по использованию инструмента"""
        return self.instructions.get(tool_name)

    def get_all_instructions(self) -> Dict[str, str]:
        """Получает все инструкции"""
        return self.instructions

    # --- Расширенный интерфейс для совместимости с UI ---
    def get_tool_detailed_instructions(self, tool_name: str) -> Optional[str]:
        """
        Возвращает детальные инструкции по инструменту с учетом алиасов, которые
        использует UI (например, 'filesystem_tools', 'local_mcp_tools', 'browser_tools', 'page_analyzer').
        """
        alias_map = {
            # алиасы UI -> внутренние названия
            "filesystem_tools": "file_operations",
            "local_mcp_tools": "api_client",
            "browser_tools": "browser_tools",
            "page_analyzer": "url_analyzer",
        }
        internal_name = alias_map.get(tool_name, tool_name)
        return self.instructions.get(internal_name)

    def get_tools_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Возвращает сводку инструментов по категориям в формате, ожидаемом UI/сервером:
        {
          "category": [ {"name": str, "description": str, "available": bool}, ... ]
        }
        """
        # Метаданные инструментов: категория и краткое описание
        tool_meta: Dict[str, Dict[str, str]] = {
            "execute_shell": {"category": "system", "description": "Выполнение команд оболочки"},
            "web_scraper": {"category": "web", "description": "Скрапинг веб-страниц"},
            "web_search": {"category": "web", "description": "Поиск в интернете"},
            "api_client": {"category": "web", "description": "HTTP запросы к API"},
            "url_analyzer": {"category": "web", "description": "Анализ параметров URL/страницы"},
            "file_operations": {"category": "files", "description": "Операции с файлами и директориями"},
            "system_info": {"category": "system", "description": "Информация о системе"},
            "process_manager": {"category": "system", "description": "Управление процессами"},
            "time_helper": {"category": "utility", "description": "Операции со временем и датой"},
            "project_helper": {"category": "utility", "description": "Помощь в управлении проектами"},
            "browser_tools": {"category": "browser", "description": "Автоматизация браузера"},
            "page_analyzer": {"category": "web", "description": "Анализ веб-страниц (SEO/структура)"},
        }

        summary: Dict[str, List[Dict[str, Any]]] = {}
        for name, instruction in self.instructions.items():
            meta = tool_meta.get(name, {"category": "misc", "description": ""})
            category = meta.get("category", "misc")
            description = meta.get("description", "")
            summary.setdefault(category, []).append({
                "name": name,
                "description": description,
                "available": True if instruction else False,
            })

        # Сортируем инструменты внутри категорий по имени для стабильности
        for cat in summary:
            summary[cat] = sorted(summary[cat], key=lambda x: x["name"])

        self.logger.debug("[TOOLS] Сформирована сводка инструментов по категориям: %s", list(summary.keys()))
        return summary

# --- Singleton accessor ---
_tools_manager_instance: Optional[ToolsInstructionManager] = None

def get_tools_instruction_manager() -> ToolsInstructionManager:
    """Возвращает единый экземпляр менеджера инструкций инструментов."""
    global _tools_manager_instance
    if _tools_manager_instance is None:
        _tools_manager_instance = ToolsInstructionManager()
    return _tools_manager_instance
