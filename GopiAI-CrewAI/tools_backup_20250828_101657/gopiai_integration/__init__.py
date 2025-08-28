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

# ОСНОВНЫЕ ИНСТРУМЕНТЫ
from .filesystem_tools import GopiAIFileSystemTool
from .terminal_tool import TerminalTool
from .web_search_tool import GopiAIWebSearchTool
from .web_viewer_tool import GopiAIWebViewerTool

# ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ
from .memory_tools import GopiAIMemoryTool
from .communication_tools import GopiAICommunicationTool

# НЕОГРАНИЧЕННЫЕ ИНСТРУМЕНТЫ (без ограничений безопасности)
from .unrestricted_filesystem_tool import UnrestrictedFileSystemTool
from .unrestricted_code_executor import UnrestrictedCodeExecutor
from .unrestricted_tools_manager import (
    unrestricted_tools_manager, 
    get_unrestricted_tools,
    execute_filesystem_command,
    execute_code_command
)

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
    
    # Неограниченные инструменты
    'UnrestrictedFileSystemTool',
    'UnrestrictedCodeExecutor',
    'unrestricted_tools_manager',
    'get_unrestricted_tools',
    'execute_filesystem_command',
    'execute_code_command',
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
    'unrestricted_filesystem': {
        'class': 'UnrestrictedFileSystemTool',
        'description': 'Неограниченный доступ к файловой системе без ограничений безопасности',
        'capabilities': ['read', 'write', 'create', 'delete', 'list', 'execute', 'search', 'copy', 'move', 'full_system_access'],
        'status': 'unrestricted'
    },
    'unrestricted_code_executor': {
        'class': 'UnrestrictedCodeExecutor',
        'description': 'Выполнение кода без ограничений песочницы',
        'capabilities': ['python', 'bash', 'shell', 'install_packages', 'full_system_access', 'network_access'],
        'status': 'unrestricted'
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

def get_unrestricted_tools_list():
    """Возвращает неограниченные инструменты без ограничений безопасности"""
    return [
        UnrestrictedFileSystemTool(),
        UnrestrictedCodeExecutor(),
    ]

def get_all_tools_including_unrestricted():
    """Возвращает все инструменты включая неограниченные"""
    return get_all_tools() + get_additional_tools() + get_unrestricted_tools_list()

def get_tool_by_name(tool_name: str):
    """Получить инструмент по имени"""
    tools_map = {
        'filesystem': GopiAIFileSystemTool,
        'terminal': TerminalTool,
        'web_search': GopiAIWebSearchTool,
        'web_viewer': GopiAIWebViewerTool,
        'memory': GopiAIMemoryTool,
        'communication': GopiAICommunicationTool,
        'unrestricted_filesystem': UnrestrictedFileSystemTool,
        'unrestricted_code_executor': UnrestrictedCodeExecutor,
    }
    
    if tool_name in tools_map:
        return tools_map[tool_name]()
    else:
        available_tools = ', '.join(tools_map.keys())
        raise ValueError(f"Неизвестный инструмент: {tool_name}. Доступные: {available_tools}")

def get_active_tools_info():
    """Возвращает информацию только об активных инструментах"""
    return {k: v for k, v in TOOLS_INFO.items() if v['status'] == 'active'}

print("GopiAI Integration Tools loaded successfully!")