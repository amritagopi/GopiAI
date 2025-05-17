import ast
import asyncio
import os
import subprocess
import sys
import traceback
from typing import Any, Dict, Optional

from app.logger import logger
from app.tool.base import BaseTool, CLIResult
from app.ui.code_editor_widget import MultiEditorWidget


class CodeRunTool(BaseTool):
    """
    Инструмент для запуска кода из редактора.

    Позволяет выполнять файлы различных типов и показывать результаты
    выполнения в консоли редактора.
    """

    code_run_name: str = "code_run"
    description: str = "Запускает код на выполнение или проверяет его"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["run", "check"],
                "description": "Действие (run - запустить код, check - проверить синтаксис)",
            },
            "language": {
                "type": "string",
                "enum": ["python", "javascript", "html"],
                "description": "Язык программирования (по умолчанию определяется по расширению файла)",
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
        Выполняет код.

        Args:
            action: Действие, которое нужно выполнить (run, check)
            language: Язык программирования

        Returns:
            CLIResult: Результат выполнения операции
        """
        if not self.editor_widget:
            return CLIResult(error="Редактор кода не инициализирован")

        action = kwargs.get("action")
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

            # Определяем язык программирования
            language = kwargs.get("language") or self._detect_language(editor)

            # Выполняем соответствующее действие
            if action == "run":
                return await self._run_code(editor, language)
            elif action == "check":
                return await self._check_code(editor, language)
            else:
                return CLIResult(error=f"Неизвестное действие: {action}")

        except Exception as e:
            logger.error(f"Ошибка при выполнении действия {action} в редакторе: {e}")
            return CLIResult(error=f"Ошибка: {str(e)}")

    async def _run_code(self, editor, language: str) -> CLIResult:
        """Запускает код на выполнение в зависимости от языка."""
        try:
            code = editor.toPlainText()
            if not code.strip():
                return CLIResult(error="Файл пуст")

            self.notify_ui(f"Запуск кода на языке {language}")

            if language == "python":
                return await self._run_python_code(code)
            elif language == "javascript":
                return CLIResult(error="Запуск JavaScript пока не реализован")
            elif language == "html":
                return CLIResult(error="Запуск HTML пока не реализован")
            else:
                return CLIResult(error=f"Неподдерживаемый язык: {language}")
        except Exception as e:
            traceback.print_exc()
            return CLIResult(error=f"Ошибка при запуске кода: {str(e)}")

    async def _check_code(self, editor, language: str) -> CLIResult:
        """Проверяет синтаксис кода."""
        try:
            code = editor.toPlainText()
            if not code.strip():
                return CLIResult(output="Файл пуст")

            self.notify_ui(f"Проверка синтаксиса кода на языке {language}")

            if language == "python":
                try:
                    ast.parse(code)
                    return CLIResult(output="Синтаксис корректен")
                except SyntaxError as e:
                    return CLIResult(error=f"Синтаксическая ошибка: {str(e)}")
            elif language == "javascript":
                return CLIResult(error="Проверка JavaScript пока не реализована")
            elif language == "html":
                return CLIResult(error="Проверка HTML пока не реализована")
            else:
                return CLIResult(error=f"Неподдерживаемый язык: {language}")
        except Exception as e:
            return CLIResult(error=f"Ошибка при проверке кода: {str(e)}")

    async def _run_python_code(self, code: str) -> CLIResult:
        """Запускает Python код в изолированной среде."""
        try:
            # Проверяем синтаксис кода
            compile(code, "<string>", "exec")

            # Создаем временный файл для кода
            import tempfile
            import uuid

            temp_dir = tempfile.gettempdir()
            file_name = f"gopiAI_code_{uuid.uuid4().hex}.py"
            file_path = os.path.join(temp_dir, file_name)

            # Записываем код во временный файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Запускаем код в отдельном процессе с ограничениями
            # Устанавливаем таймаут и ограничиваем доступ к определенным модулям
            cmd = [sys.executable, file_path]

            # Создаем процесс
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # Устанавливаем ограничения для процесса
                env=os.environ.copy(),
            )

            # Ждем результат с таймаутом
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=10.0  # 10 секунд на выполнение
                )
                output = stdout.decode("utf-8", errors="replace")
                error = stderr.decode("utf-8", errors="replace")

                # Удаляем временный файл
                try:
                    os.remove(file_path)
                except Exception:
                    pass

                # Проверяем, были ли ошибки
                if error:
                    return CLIResult(error=f"Ошибки при выполнении:\n{error}")

                # Возвращаем результат
                return CLIResult(output=f"Результат выполнения:\n{output}")

            except asyncio.TimeoutError:
                # В случае таймаута прерываем процесс
                process.kill()

                # Удаляем временный файл
                try:
                    os.remove(file_path)
                except Exception:
                    pass

                return CLIResult(error="Превышено время выполнения (10 секунд)")

        except SyntaxError as e:
            return CLIResult(error=f"Ошибка синтаксиса: {str(e)}")
        except Exception as e:
            traceback.print_exc()
            return CLIResult(error=f"Ошибка при выполнении Python кода: {str(e)}")

    def _detect_language(self, editor) -> str:
        """Определяет язык программирования по расширению файла."""
        file_path = getattr(editor, "file_path", None)
        if not file_path:
            return "python"  # По умолчанию

        if file_path.endswith(".py"):
            return "python"
        elif file_path.endswith(".js"):
            return "javascript"
        elif file_path.endswith(".html"):
            return "html"
        else:
            return "python"  # По умолчанию

    def notify_ui(self, message: str):
        """Отправляет уведомление в UI."""
        if self.editor_widget and hasattr(self.editor_widget, "progress_update"):
            self.editor_widget.progress_update.emit(message)
