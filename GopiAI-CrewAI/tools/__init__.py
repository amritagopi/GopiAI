"""
GopiAI Tools Package

Этот пакет содержит нативные инструменты CrewAI для AI ассистента GopiAI.
Все кастомные инструменты были удалены для упрощения архитектуры.
"""

# Импорт нативных инструментов CrewAI
try:
    from .crewai_toolkit.tools.code_interpreter_tool import CodeInterpreterTool
    CODE_INTERPRETER_AVAILABLE = True
except ImportError:
    CODE_INTERPRETER_AVAILABLE = False

try:
    from .crewai_toolkit.tools.directory_read_tool.directory_read_tool import DirectoryReadTool
    DIRECTORY_READ_TOOL_AVAILABLE = True
except ImportError:
    DIRECTORY_READ_TOOL_AVAILABLE = False


__all__ = []

# Добавляем нативные инструменты CrewAI если доступны
if CODE_INTERPRETER_AVAILABLE:
    __all__.append('CodeInterpreterTool')

if DIRECTORY_READ_TOOL_AVAILABLE:
    __all__.append('DirectoryReadTool')

# Создаем глобальные экземпляры нативных инструментов CrewAI
if CODE_INTERPRETER_AVAILABLE:
    try:
        code_interpreter = CodeInterpreterTool()
    except Exception:
        code_interpreter = None
else:
    code_interpreter = None

if DIRECTORY_READ_TOOL_AVAILABLE:
    try:
        directory_read_tool = DirectoryReadTool()
    except Exception:
        directory_read_tool = None
else:
    directory_read_tool = None