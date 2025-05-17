import asyncio
from typing import Any, Dict, List, Optional

from app.logger import logger
from app.tool.base import BaseTool, CLIResult
from app.ui.code_editor_widget import MultiEditorWidget


class CodeControlTool(BaseTool):
    """
    Инструмент для управления редактором кода.

    Позволяет открывать/закрывать файлы, переключаться между вкладками,
    получать информацию о текущем состоянии редактора.
    """

    code_control_name: str = "code_control"
    description: str = "Управление редактором кода: открытие, закрытие, создание файлов"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["open", "close", "new", "list", "current"],
                "description": "Действие, которое нужно выполнить",
            },
            "path": {
                "type": "string",
                "description": "Путь к файлу (для действия open)",
            },
        },
        "required": ["action"],
    }

    def __init__(self):
        super().__init__()
        self.editor_widget: Optional[MultiEditorWidget] = None

    def set_editor_widget(self, editor_widget: MultiEditorWidget):
        """Устанавливает ссылку на виджет редактора кода."""
        self.editor_widget = editor_widget

    async def execute(self, **kwargs) -> CLIResult:
        """
        Выполняет действие над редактором кода.

        Args:
            action: Действие, которое нужно выполнить
            path: Путь к файлу (для open)

        Returns:
            CLIResult: Результат выполнения операции
        """
        if not self.editor_widget:
            return CLIResult(error="Редактор кода не инициализирован")

        action = kwargs.get("action")
        if not action:
            return CLIResult(error="Не указано действие (action)")

        try:
            # Выполняем необходимое действие
            if action == "open":
                return await self._open_file(kwargs.get("path", ""))
            elif action == "close":
                return await self._close_file()
            elif action == "new":
                return await self._new_file()
            elif action == "list":
                return await self._get_open_files()
            elif action == "current":
                return await self._get_current_file()
            else:
                return CLIResult(error=f"Неизвестное действие: {action}")

        except Exception as e:
            logger.error(f"Ошибка при выполнении действия {action} в редакторе: {e}")
            return CLIResult(error=f"Ошибка: {str(e)}")

    async def _open_file(self, path: str) -> CLIResult:
        """Открывает файл в редакторе."""
        if not path:
            return CLIResult(error="Не указан путь к файлу (path)")

        # В реальном приложении здесь будет проверка существования файла
        try:
            self.notify_ui(f"Открываем файл {path}")
            self.editor_widget.open_file(path)

            return CLIResult(output=f"Файл {path} успешно открыт")
        except Exception as e:
            return CLIResult(error=f"Ошибка при открытии файла {path}: {str(e)}")

    async def _close_file(self) -> CLIResult:
        """Закрывает текущий файл в редакторе."""
        try:
            current_index = self.editor_widget.tabs.currentIndex()
            if current_index < 0:
                return CLIResult(error="Нет открытых вкладок")

            # Закрываем текущую вкладку
            self.notify_ui("Закрытие текущего файла")
            self.editor_widget.close_tab(current_index)

            return CLIResult(output="Файл успешно закрыт")
        except Exception as e:
            return CLIResult(error=f"Ошибка при закрытии файла: {str(e)}")

    async def _new_file(self) -> CLIResult:
        """Создает новый файл в редакторе."""
        try:
            self.notify_ui("Создание нового файла")
            self.editor_widget.new_file()
            return CLIResult(output="Новый файл создан")
        except Exception as e:
            return CLIResult(error=f"Ошибка при создании нового файла: {str(e)}")

    async def _get_open_files(self) -> CLIResult:
        """Получает список открытых файлов."""
        try:
            files = self.editor_widget.get_open_files()
            return CLIResult(output=files)
        except Exception as e:
            return CLIResult(
                error=f"Ошибка при получении списка открытых файлов: {str(e)}"
            )

    async def _get_current_file(self) -> CLIResult:
        """Получает название текущего открытого файла."""
        try:
            current_file = self.editor_widget.get_current_file()
            if not current_file:
                return CLIResult(output="Нет активного файла")
            return CLIResult(output=current_file)
        except Exception as e:
            return CLIResult(error=f"Ошибка при получении текущего файла: {str(e)}")

    def notify_ui(self, message: str):
        """Отправляет уведомление в UI."""
        if self.editor_widget and hasattr(self.editor_widget, "progress_update"):
            self.editor_widget.progress_update.emit(message)
