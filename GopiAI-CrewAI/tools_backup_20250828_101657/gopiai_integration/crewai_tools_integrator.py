"""
🛠️ CrewAI Tools Integrator
Интегратор для подключения и управления инструментами из CrewAI Toolkit
"""

import logging
import importlib
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import sys
import os

logger = logging.getLogger(__name__)

class CrewAIToolsIntegrator:
    """
    Интегратор для управления инструментами CrewAI Toolkit
    
    Возможности:
    - Автоматическое обнаружение доступных инструментов
    - Ленивая загрузка инструментов по требованию
    - Категоризация инструментов по типам
    - Fallback между различными инструментами
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tools = {}
        self.loaded_tools = {}
        self.tool_categories = {}
        
        # Добавляем путь к crewai_toolkit
        toolkit_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crewai_toolkit")
        if toolkit_path not in sys.path:
            sys.path.insert(0, toolkit_path)
        
        self._discover_tools()
        self.logger.info(f"✅ CrewAI Tools Integrator инициализирован. Найдено {len(self.available_tools)} инструментов")
    
    def _discover_tools(self):
        """Обнаруживает доступные CrewAI инструменты"""
        
        # Динамически формируем список инструментов, исходя из доступных ключей в окружении
        has_brave = bool(os.environ.get("BRAVE_API_KEY"))
        has_tavily = bool(os.environ.get("TAVILY_API_KEY"))
        has_firecrawl = bool(os.environ.get("FIRECRAWL_API_KEY"))
        has_github = bool(os.environ.get("GITHUB_TOKEN"))
        has_exa = bool(os.environ.get("EXA_API_KEY"))
        has_jina = bool(os.environ.get("JINA_API_KEY"))
        has_apify = bool(os.environ.get("APIFY_API_TOKEN"))
        has_composio = bool(os.environ.get("COMPOSIO_API_KEY"))
        has_patronus = bool(os.environ.get("PATRONUS_API_KEY"))
        has_qdrant = bool(os.environ.get("QDRANT_API_KEY"))

        # Базовый набор (не требуют внешних ключей)
        priority_tools = {
            # Выполнение кода
            'code_interpreter': {
                'module': 'tools.crewai_toolkit.tools.code_interpreter_tool.code_interpreter_tool',
                'class': 'CodeInterpreterTool',
                'category': 'code_execution',
                'description': 'Выполнение Python кода в безопасной среде'
            },

            # Веб-скрапинг (улучшенный)
            'selenium_scraping': {
                'module': 'tools.crewai_toolkit.tools.selenium_scraping_tool.selenium_scraping_tool',
                'class': 'SeleniumScrapingTool',
                'category': 'web_scraping',
                'description': 'Продвинутый веб-скрапинг с Selenium'
            },

            # Файловые операции (улучшенные)
            'file_read': {
                'module': 'tools.crewai_toolkit.tools.file_read_tool.file_read_tool',
                'class': 'FileReadTool',
                'category': 'file_operations',
                'description': 'Чтение файлов с поддержкой различных форматов'
            },

            'file_writer': {
                'module': 'tools.crewai_toolkit.tools.file_writer_tool.file_writer_tool',
                'class': 'FileWriterTool',
                'category': 'file_operations',
                'description': 'Запись файлов с поддержкой различных форматов'
            },

            'directory_read': {
                'module': 'tools.crewai_toolkit.tools.directory_read_tool.directory_read_tool',
                'class': 'DirectoryReadTool',
                'category': 'file_operations',
                'description': 'Чтение содержимого директорий'
            },

            # Поиск в файлах
            'csv_search': {
                'module': 'tools.crewai_toolkit.tools.csv_search_tool.csv_search_tool',
                'class': 'CSVSearchTool',
                'category': 'file_operations',
                'description': 'Поиск данных в CSV файлах'
            },

            # API клиенты
            'brave_search': {
                'module': 'tools.crewai_toolkit.tools.brave_search_tool.brave_search_tool',
                'class': 'BraveSearchTool',
                'category': 'web_search',
                'description': 'Поиск в интернете с использованием API Brave',
                'enabled': has_brave
            },

            'tavily_search': {
                'module': 'tools.crewai_toolkit.tools.tavily_search_tool.tavily_search_tool',
                'class': 'TavilySearchTool',
                'category': 'web_search',
                'description': 'Поиск в интернете с использованием API Tavily',
                'enabled': has_tavily
            },

            'firecrawl_search': {
                'module': 'tools.crewai_toolkit.tools.firecrawl_search_tool.firecrawl_search_tool',
                'class': 'FirecrawlSearchTool',
                'category': 'web_search',
                'description': 'Поиск в интернете с использованием API Firecrawl',
                'enabled': has_firecrawl
            },

            # GitHub интеграция
            'github_client': {
                'module': 'tools.crewai_toolkit.tools.github_client_tool.github_client_tool',
                'class': 'GitHubClientTool',
                'category': 'code_integration',
                'description': 'Интеграция с GitHub для управления репозиториями',
                'enabled': has_github
            },

            # Другие инструменты
            'exa_client': {
                'module': 'tools.crewai_toolkit.tools.exa_client_tool.exa_client_tool',
                'class': 'ExaClientTool',
                'category': 'data_processing',
                'description': 'Интеграция с Exa для обработки данных',
                'enabled': has_exa
            },

            'jina_client': {
                'module': 'tools.crewai_toolkit.tools.jina_client_tool.jina_client_tool',
                'class': 'JinaClientTool',
                'category': 'data_processing',
                'description': 'Интеграция с Jina для обработки данных',
                'enabled': has_jina
            },

            'apify_client': {
                'module': 'tools.crewai_toolkit.tools.apify_client_tool.apify_client_tool',
                'class': 'ApifyClientTool',
                'category': 'web_scraping',
                'description': 'Интеграция с Apify для веб-скрапинга',
                'enabled': has_apify
            },

            'composio_client': {
                'module': 'tools.crewai_toolkit.tools.composio_client_tool.composio_client_tool',
                'class': 'ComposioClientTool',
                'category': 'data_storage',
                'description': 'Интеграция с Composio для хранения данных',
                'enabled': has_composio
            },

            'patronus_client': {
                'module': 'tools.crewai_toolkit.tools.patronus_client_tool.patronus_client_tool',
                'class': 'PatronusClientTool',
                'category': 'security',
                'description': 'Интеграция с Patronus для обеспечения безопасности',
                'enabled': has_patronus
            },

            'qdrant_client': {
                'module': 'tools.crewai_toolkit.tools.qdrant_client_tool.qdrant_client_tool',
                'class': 'QdrantClientTool',
                'category': 'data_storage',
                'description': 'Интеграция с Qdrant для хранения данных',
                'enabled': has_qdrant
            }
        }

        # Добавляем инструменты в список доступных
        for tool_name, tool_info in priority_tools.items():
            if tool_info.get('enabled', True):
                self.available_tools[tool_name] = tool_info
                self.tool_categories.setdefault(tool_info['category'], []).append(tool_name)

    def get_tool(self, tool_name: str) -> Optional[Type[Any]]:
        """Получает инструмент по имени"""
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name]

        if tool_name in self.available_tools:
            tool_info = self.available_tools[tool_name]
            module_path = tool_info['module']
            class_name = tool_info['class']

            try:
                module = importlib.import_module(module_path)
                tool_class = getattr(module, class_name)
                self.loaded_tools[tool_name] = tool_class
                self.logger.info(f"✅ Инструмент {tool_name} загружен")
                return tool_class
            except (ImportError, AttributeError) as e:
                self.logger.error(f"❌ Ошибка при загрузке инструмента {tool_name}: {e}")
                return None

        self.logger.warning(f"⚠️ Инструмент {tool_name} не найден")
        return None

    def get_tools_by_category(self, category: str) -> List[str]:
        """Получает список инструментов по категории"""
        return self.tool_categories.get(category, [])

    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Получает все доступные инструменты"""
        return self.available_tools

    def get_available_tools(self) -> List[str]:
        """
        Возвращает список канонических названий доступных инструментов.

        Совместимо с вызовами в `SmartDelegator` и `ToolDispatcher`, где ожидается
        список строк с именами инструментов.
        """
        return list(self.available_tools.keys())

    def get_tools_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Краткая сводка инструментов по категориям для API/UI.

        Возвращает словарь вида:
        {
          "category": [
             {"name": str, "description": str, "available": bool}, ...
          ],
          ...
        }
        """
        summary: Dict[str, List[Dict[str, Any]]] = {}
        for name, info in self.available_tools.items():
            category = info.get('category', 'misc')
            summary.setdefault(category, []).append({
                'name': name,
                'description': info.get('description', ''),
                'available': True  # на этом уровне считаем доступным, т.к. прошёл discover
            })

        # Сортируем инструменты внутри категорий по имени для стабильности отображения
        for cat in summary:
            summary[cat] = sorted(summary[cat], key=lambda x: x['name'])
        return summary

# --- Factory function and explicit exports ---
def get_crewai_tools_integrator() -> "CrewAIToolsIntegrator":
    """Фабрика для совместимости с сервером CrewAI.

    Возвращает экземпляр интегратора инструментов CrewAI Toolkit.
    """
    return CrewAIToolsIntegrator()

__all__ = [
    "CrewAIToolsIntegrator",
    "get_crewai_tools_integrator",
]
