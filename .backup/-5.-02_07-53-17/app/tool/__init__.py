"""Tools for the agent."""

from app.tool.base import BaseTool
from app.tool.bash import Bash  # Раскомментируем, так как используется в swe.py

# from app.tool.browser_use_tool import BrowserUseTool  # Комментируем эту строку
# from app.tool.browser_use_tool import BrowserUseTool  # Раскомментируем эту строку
from app.tool.create_chat_completion import CreateChatCompletion
from app.tool.planning import PlanningTool  # Добавляем импорт PlanningTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
# from app.tool.tavily_tool import TavilyTool <-- Commenting out this import
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection

__all__ = [
    "BaseTool",
    "Bash",  # Раскомментируем, так как используется в swe.py
    # "BrowserUseTool",  # Закомментируем
    # "BrowserUseTool",  # Раскомментируем
    "CreateChatCompletion",
    "PlanningTool",  # Добавляем экспорт PlanningTool
    "PythonExecute",
    "StrReplaceEditor",
    # "TavilyTool", <-- Commenting out this export
    "Terminate",
    "ToolCollection",
]
