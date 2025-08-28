"""
GopiAI Tools Package

Этот пакет содержит все инструменты для AI ассистента GopiAI,
включая неограниченные инструменты для работы с файловой системой и выполнения кода.
"""

from .tools_config import ToolsConfig
from .command_executor import CommandExecutor
from .simple_filesystem_tool import SimpleFileSystemTool
from .simple_code_executor import SimpleCodeExecutor

# Попытка импорта дополнительных инструментов (могут отсутствовать зависимости)
try:
    from .code_interpreter_tool import CodeInterpreterTool
    CODE_INTERPRETER_AVAILABLE = True
except ImportError:
    CODE_INTERPRETER_AVAILABLE = False

try:
    from .unrestricted_filesystem_tool import UnrestrictedFileSystemTool
    UNRESTRICTED_FS_AVAILABLE = True
except ImportError:
    UNRESTRICTED_FS_AVAILABLE = False

try:
    from .unrestricted_code_executor import UnrestrictedCodeExecutor
    UNRESTRICTED_CODE_AVAILABLE = True
except ImportError:
    UNRESTRICTED_CODE_AVAILABLE = False

try:
    from .unrestricted_tools_manager import UnrestrictedToolsManager
    TOOLS_MANAGER_AVAILABLE = True
except ImportError:
    TOOLS_MANAGER_AVAILABLE = False

__all__ = [
    'ToolsConfig',
    'CommandExecutor', 
    'SimpleFileSystemTool',
    'SimpleCodeExecutor'
]

# Добавляем дополнительные инструменты если доступны
if CODE_INTERPRETER_AVAILABLE:
    __all__.append('CodeInterpreterTool')
if UNRESTRICTED_FS_AVAILABLE:
    __all__.append('UnrestrictedFileSystemTool')
if UNRESTRICTED_CODE_AVAILABLE:
    __all__.append('UnrestrictedCodeExecutor')
if TOOLS_MANAGER_AVAILABLE:
    __all__.append('UnrestrictedToolsManager')

# Создаем глобальные экземпляры для удобства использования
tools_config = ToolsConfig()
command_executor = CommandExecutor()
simple_fs = SimpleFileSystemTool()
simple_code = SimpleCodeExecutor()

# Создаем дополнительные экземпляры если доступны
if UNRESTRICTED_FS_AVAILABLE:
    try:
        unrestricted_fs = UnrestrictedFileSystemTool()
    except Exception:
        unrestricted_fs = None
else:
    unrestricted_fs = None

if UNRESTRICTED_CODE_AVAILABLE:
    try:
        unrestricted_code = UnrestrictedCodeExecutor()
    except Exception:
        unrestricted_code = None
else:
    unrestricted_code = None

if TOOLS_MANAGER_AVAILABLE:
    try:
        tools_manager = UnrestrictedToolsManager()
    except Exception:
        tools_manager = None
else:
    tools_manager = None