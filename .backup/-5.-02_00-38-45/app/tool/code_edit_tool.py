import asyncio
from typing import Dict, Any, Optional

from app.ui.code_editor_widget import MultiEditorWidget
from app.tool.base import BaseTool, CLIResult
from app.logger import logger


class CodeEditTool(BaseTool):
    """
    Инструмент для редактирования содержимого файлов в редакторе кода.

    Позволяет изменять текст, вставлять и удалять блоки кода,
    форматировать и структурировать код.
    """

    name: str = "code_edit"
    description: str = "Редактирует содержимое файлов в редакторе кода"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_content", "set_content", "insert_at", "replace_selection"],
                "description": "Действие, которое нужно выполнить"
            },
            "content": {
                "type": "string",
                "description": "Текст для вставки или замены"
            },
            "position": {
                "type": "integer",
                "description": "Позиция для вставки (для insert_at)"
            }
        },
        "required": ["action"]
    }

    def __init__(self):
        super().__init__()
        self.editor_widget: Optional[MultiEditorWidget] = None

    def set_editor_widget(self, editor_widget: MultiEditorWidget):
        """Устанавливает ссылку на виджет редактора кода."""
        self.editor_widget = editor_widget

    async def execute(self, **kwargs) -> CLIResult:
        """
        Выполняет действие по редактированию кода.

        Args:
            action: Действие, которое нужно выполнить
            content: Текст для вставки или замены
            position: Позиция для вставки (для insert_at)

        Returns:
            CLIResult: Результат выполнения операции
        """
        if not self.editor_widget:
            return CLIResult(error="Редактор кода не инициализирован")

        action = kwargs.get('action')
        if not action:
            return CLIResult(error="Не указано действие (action)")

        try:
            # Получаем текущий редактор
            current_index = self.editor_widget.tabs.currentIndex()
            if current_index < 0:
                return CLIResult(error="Нет открытых вкладок")

            editor = self.editor_widget.tabs.widget(current_index)
            if not editor:
                return CLIResult(error="Не удалось получить текущий редактор")

            # Выполняем соответствующее действие
            if action == 'get_content':
                content = editor.toPlainText()
                return CLIResult(output=content)

            elif action == 'set_content':
                content = kwargs.get('content')
                if content is None:
                    return CLIResult(error="Не указано содержимое (content)")

                self.notify_ui("Обновление содержимого файла")
                editor.setPlainText(content)
                return CLIResult(output="Содержимое файла обновлено")

            elif action == 'insert_at':
                content = kwargs.get('content')
                position = kwargs.get('position')

                if content is None:
                    return CLIResult(error="Не указано содержимое (content)")
                if position is None:
                    return CLIResult(error="Не указана позиция (position)")

                self.notify_ui(f"Вставка текста в позиции {position}")

                # Устанавливаем курсор в указанную позицию
                cursor = editor.textCursor()
                cursor.setPosition(position)
                editor.setTextCursor(cursor)

                # Вставляем текст
                cursor.insertText(content)
                return CLIResult(output=f"Текст вставлен в позиции {position}")

            elif action == 'replace_selection':
                content = kwargs.get('content')
                if content is None:
                    return CLIResult(error="Не указано содержимое (content)")

                self.notify_ui("Замена выделенного текста")

                # Заменяем выделенный текст
                cursor = editor.textCursor()
                if not cursor.hasSelection():
                    return CLIResult(error="Нет выделенного текста")

                cursor.insertText(content)
                return CLIResult(output="Выделенный текст заменен")

            else:
                return CLIResult(error=f"Неизвестное действие: {action}")

        except Exception as e:
            logger.error(f"Ошибка при выполнении действия {action} в редакторе: {e}")
            return CLIResult(error=f"Ошибка: {str(e)}")

    def notify_ui(self, message: str):
        """Отправляет уведомление в UI."""
        if self.editor_widget and hasattr(self.editor_widget, 'progress_update'):
            self.editor_widget.progress_update.emit(message)
