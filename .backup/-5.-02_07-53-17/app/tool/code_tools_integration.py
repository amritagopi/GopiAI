from typing import Optional, List

from app.ui.code_editor_widget import MultiEditorWidget
from app.tool.code_control_tool import CodeControlTool
from app.tool.code_edit_tool import CodeEditTool
from app.tool.code_analyze_tool import CodeAnalyzeTool
from app.tool.code_run_tool import CodeRunTool


class CodeToolsManager:
    """
    Менеджер инструментов для работы с кодом.
    Создает и настраивает инструменты для взаимодействия с редактором кода.
    """

    def __init__(self):
        self.editor_widget: Optional[MultiEditorWidget] = None
        self.code_control_tool: Optional[CodeControlTool] = None
        self.code_edit_tool: Optional[CodeEditTool] = None
        self.code_analyze_tool: Optional[CodeAnalyzeTool] = None
        self.code_run_tool: Optional[CodeRunTool] = None

    def set_editor_widget(self, editor_widget: MultiEditorWidget):
        """
        Устанавливает ссылку на виджет редактора кода и инициализирует инструменты.

        Args:
            editor_widget: Виджет редактора кода из UI
        """
        self.editor_widget = editor_widget

        # Инициализируем инструменты, если они не были созданы
        if not self.code_control_tool:
            self.code_control_tool = CodeControlTool()

        if not self.code_edit_tool:
            self.code_edit_tool = CodeEditTool()

        if not self.code_analyze_tool:
            self.code_analyze_tool = CodeAnalyzeTool()

        if not self.code_run_tool:
            self.code_run_tool = CodeRunTool()

        # Устанавливаем ссылку на виджет редактора в инструменты
        self.code_control_tool.set_editor_widget(editor_widget)
        self.code_edit_tool.set_editor_widget(editor_widget)
        self.code_analyze_tool.set_editor_widget(editor_widget)
        self.code_run_tool.set_editor_widget(editor_widget)

    def get_tools(self) -> List:
        """
        Возвращает список всех инструментов для работы с кодом.

        Returns:
            Список инструментов для работы с кодом
        """
        tools = []

        if self.code_control_tool:
            tools.append(self.code_control_tool)

        if self.code_edit_tool:
            tools.append(self.code_edit_tool)

        if self.code_analyze_tool:
            tools.append(self.code_analyze_tool)

        if self.code_run_tool:
            tools.append(self.code_run_tool)

        return tools


# Глобальный экземпляр менеджера инструментов кода
code_tools_manager = CodeToolsManager()


def initialize_coding_tools(editor_widget: MultiEditorWidget) -> List:
    """
    Инициализирует инструменты для работы с кодом и связывает их с виджетом редактора.

    Args:
        editor_widget: Виджет редактора кода из UI

    Returns:
        Список инициализированных инструментов
    """
    code_tools_manager.set_editor_widget(editor_widget)
    return code_tools_manager.get_tools()


def get_coding_tools() -> List:
    """
    Возвращает список инструментов для работы с кодом.

    Returns:
        Список инструментов для работы с кодом
    """
    return code_tools_manager.get_tools()
