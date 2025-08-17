"""
GopiAI Integration Tools for CrewAI
Set of specialized tools for integrating CrewAI with GopiAI

ОСНОВНЫЕ ИНСТРУМЕНТЫ (рекомендуемые для использования):
- GopiAIFileSystemTool: работа с файловой системой
- TerminalTool: выполнение команд в терминале
- GopiAIWebSearchTool: поиск в интернете
- GopiAIWebViewerTool: просмотр веб-страниц

ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ:
- GopiAIMemoryTool: система памяти и RAG
- GopiAICommunicationTool: коммуникация между агентами

ОТКЛЮЧЕННЫЕ ИНСТРУМЕНТЫ:
- GopiAIBrowserTool: браузерная автоматизация (отключена)
"""

# Безопасный BaseTool (fallback, если crewai недоступен)
try:
    from crewai.tools.base_tool import BaseTool  # type: ignore
except Exception:  # pragma: no cover
    class BaseTool:  # минимальная заглушка
        name: str = "BaseTool"
        description: str = "Stub BaseTool when crewai is unavailable"
        def tool_schema(self):
            return {
                "type": "function",
                "function": {
                    "name": getattr(self, "name", "tool"),
                    "description": getattr(self, "description", ""),
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        def _run(self, *args, **kwargs):
            return {"error": "crewai BaseTool is unavailable"}

# ОСНОВНЫЕ ИНСТРУМЕНТЫ (с импортом через try/except)
try:
    from .filesystem_tools import GopiAIFileSystemTool
except Exception:  # pragma: no cover
    class GopiAIFileSystemTool(BaseTool):
        name = "gopiai_filesystem"
        description = "Filesystem tool unavailable (dependency missing)"
        def _run(self, *args, **kwargs):
            return {"error": "Filesystem tool unavailable"}

try:
    from .terminal_tool import TerminalTool
except Exception:  # pragma: no cover
    class TerminalTool(BaseTool):
        name = "terminal"
        description = "Terminal tool unavailable (dependency missing)"
        def _run(self, *args, **kwargs):
            return {"terminal_output": {"error": "Terminal tool unavailable", "success": False}}

try:
    from .web_search_tool import GopiAIWebSearchTool
except Exception:  # pragma: no cover
    class GopiAIWebSearchTool(BaseTool):
        name = "gopiai_web_search"
        description = "Web search unavailable (bs4/requests missing)"
        def _run(self, *args, **kwargs):
            return "❌ Web search tool unavailable"

try:
    from .web_viewer_tool import GopiAIWebViewerTool
except Exception:  # pragma: no cover
    class GopiAIWebViewerTool(BaseTool):
        name = "gopiai_web_viewer"
        description = "Web viewer unavailable (dependency missing)"
        def _run(self, *args, **kwargs):
            return "❌ Web viewer tool unavailable"

# ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ (с импортом через try/except)
try:
    from .memory_tools import GopiAIMemoryTool
except Exception:  # pragma: no cover
    class GopiAIMemoryTool(BaseTool):
        name = "gopiai_memory"
        description = "Memory tool unavailable"
        def _run(self, *args, **kwargs):
            return {"error": "Memory tool unavailable"}

try:
    from .communication_tools import GopiAICommunicationTool
except Exception:  # pragma: no cover
    class GopiAICommunicationTool(BaseTool):
        name = "gopiai_communication"
        description = "Communication tool unavailable"
        def _run(self, *args, **kwargs):
            return {"error": "Communication tool unavailable"}

# ОТКЛЮЧЕННЫЕ ИНСТРУМЕНТЫ (оставлены для совместимости)
# browser_tools удалены из проекта
# from .ai_router_tools import GopiAIRouterTool  # ОТКЛЮЧЕНО

__all__ = [
    # Основные инструменты
    'GopiAIFileSystemTool',
    'TerminalTool',
    'GopiAIWebSearchTool',
    'GopiAIWebViewerTool',
    
    # Дополнительные инструменты
    'GopiAIMemoryTool',
    'GopiAICommunicationTool',
]

__version__ = '1.0.0'
__author__ = 'GopiAI Team'
__description__ = 'Complete set of tools for integrating CrewAI with GopiAI platform'

# Information about tools
TOOLS_INFO = {
    'filesystem': {
        'class': 'GopiAIFileSystemTool', 
        'description': 'Безопасная работа с файловой системой',
        'capabilities': ['read', 'write', 'create', 'delete', 'find', 'list', 'json', 'csv', 'archive', 'search', 'backup'],
        'status': 'active'
    },
    'terminal': {
        'class': 'TerminalTool',
        'description': 'Выполнение команд в терминале с отображением в UI',
        'capabilities': ['execute', 'log', 'validate', 'safe_mode'],
        'status': 'active'
    },
    'web_search': {
        'class': 'GopiAIWebSearchTool',
        'description': 'Поиск информации в интернете через разные поисковые системы',
        'capabilities': ['duckduckgo', 'google_scrape', 'serper_api', 'serpapi', 'auto_select'],
        'status': 'active'
    },
    'web_viewer': {
        'class': 'GopiAIWebViewerTool',
        'description': 'Просмотр веб-страниц и извлечение контента',
        'capabilities': ['fetch', 'extract_text', 'extract_links', 'get_title', 'get_meta', 'cache'],
        'status': 'active'
    },
    'memory': {
        'class': 'GopiAIMemoryTool',
        'description': 'Система долговременной памяти и RAG',
        'capabilities': ['store', 'search', 'retrieve', 'categorize', 'summarize'],
        'status': 'additional'
    },
    'communication': {
        'class': 'GopiAICommunicationTool',
        'description': 'Коммуникация между агентами и с UI',
        'capabilities': ['send', 'receive', 'broadcast', 'notify', 'monitor'],
        'status': 'additional'
    },
    # ОТКЛЮЧЕННЫЕ ИНСТРУМЕНТЫ
    'browser_automation': {
        'class': 'GopiAIBrowserTool',
        'description': 'Автоматизация браузера (ОТКЛЮЧЕНО)',
        'capabilities': ['selenium', 'playwright', 'click', 'type', 'screenshot'],
        'status': 'disabled'
    }
}

def get_all_tools():
    """Возвращает все доступные основные инструменты GopiAI"""
    return [
        GopiAIFileSystemTool(),
        TerminalTool(),
        GopiAIWebSearchTool(),
        GopiAIWebViewerTool(),
    ]

def get_essential_tools():
    """Возвращает только самые необходимые инструменты (минимальный набор)"""
    return [
        GopiAIFileSystemTool(),
        TerminalTool(),
        GopiAIWebSearchTool(),
        GopiAIWebViewerTool(),
    ]

def get_additional_tools():
    """Возвращает дополнительные инструменты"""
    return [
        GopiAIMemoryTool(),
        GopiAICommunicationTool(),
    ]

def get_tool_by_name(tool_name: str):
    """Получить инструмент по имени"""
    tools_map = {
        'filesystem': GopiAIFileSystemTool,
        'terminal': TerminalTool,
        'web_search': GopiAIWebSearchTool,
        'web_viewer': GopiAIWebViewerTool,
        'memory': GopiAIMemoryTool,
        'communication': GopiAICommunicationTool,
    }
    
    if tool_name in tools_map:
        return tools_map[tool_name]()
    else:
        available_tools = ', '.join(tools_map.keys())
        raise ValueError(f"Неизвестный инструмент: {tool_name}. Доступные: {available_tools}")

def get_active_tools_info():
    """Возвращает информацию только об активных инструментах"""
    return {k: v for k, v in TOOLS_INFO.items() if v['status'] == 'active'}