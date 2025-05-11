import os
import ast
from typing import Dict, Any, Optional, List, Set, Tuple
import re

from app.ui.code_editor_widget import MultiEditorWidget
from app.tool.base import BaseTool, CLIResult
from app.logger import logger


class CodeAnalyzeTool(BaseTool):
    """
    Инструмент для анализа содержимого файлов в редакторе кода.

    Позволяет искать паттерны, анализировать структуру кода,
    находить определения функций, классов и переменных.
    """

    name: str = "code_analyze"
    description: str = "Анализирует код и предоставляет информацию о его структуре"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["imports", "functions", "classes", "variables", "full_analysis"],
                "description": "Тип анализа, который нужно выполнить"
            },
            "language": {
                "type": "string",
                "enum": ["python", "javascript", "html"],
                "description": "Язык программирования (по умолчанию определяется по расширению файла)"
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
        Выполняет анализ кода.

        Args:
            action: Тип анализа, который нужно выполнить
            language: Язык программирования (опционально)

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

            # Получаем содержимое файла
            code = editor.toPlainText()
            if not code.strip():
                return CLIResult(error="Файл пуст")

            # Определяем язык программирования
            language = kwargs.get('language') or self._detect_language(editor)

            self.notify_ui(f"Анализ кода на языке {language}")

            # Выполняем соответствующее действие
            if language == 'python':
                if action == 'imports':
                    return await self._analyze_python_imports(code)
                elif action == 'functions':
                    return await self._analyze_python_functions(code)
                elif action == 'classes':
                    return await self._analyze_python_classes(code)
                elif action == 'variables':
                    return await self._analyze_python_variables(code)
                elif action == 'full_analysis':
                    return await self._analyze_python_full(code)
                else:
                    return CLIResult(error=f"Неизвестное действие: {action}")
            else:
                return CLIResult(error=f"Анализ для языка {language} пока не реализован")

        except Exception as e:
            logger.error(f"Ошибка при выполнении анализа {action} в редакторе: {e}")
            return CLIResult(error=f"Ошибка: {str(e)}")

    async def _analyze_python_imports(self, code: str) -> CLIResult:
        """Анализирует импорты в Python коде."""
        try:
            imports = []
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")

            if not imports:
                return CLIResult(output="Импорты не найдены")

            result = "Найденные импорты:\n" + "\n".join(imports)
            return CLIResult(output=result)
        except SyntaxError as e:
            return CLIResult(error=f"Синтаксическая ошибка: {str(e)}")
        except Exception as e:
            return CLIResult(error=f"Ошибка при анализе импортов: {str(e)}")

    async def _analyze_python_functions(self, code: str) -> CLIResult:
        """Анализирует функции в Python коде."""
        try:
            functions = []
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(f"{node.name}(args: {len(node.args.args)})")

            if not functions:
                return CLIResult(output="Функции не найдены")

            result = "Найденные функции:\n" + "\n".join(functions)
            return CLIResult(output=result)
        except SyntaxError as e:
            return CLIResult(error=f"Синтаксическая ошибка: {str(e)}")
        except Exception as e:
            return CLIResult(error=f"Ошибка при анализе функций: {str(e)}")

    async def _analyze_python_classes(self, code: str) -> CLIResult:
        """Анализирует классы в Python коде."""
        try:
            classes = []
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            if not classes:
                return CLIResult(output="Классы не найдены")

            result = "Найденные классы:\n" + "\n".join(classes)
            return CLIResult(output=result)
        except SyntaxError as e:
            return CLIResult(error=f"Синтаксическая ошибка: {str(e)}")
        except Exception as e:
            return CLIResult(error=f"Ошибка при анализе классов: {str(e)}")

    async def _analyze_python_variables(self, code: str) -> CLIResult:
        """Анализирует переменные в Python коде."""
        try:
            variables = []
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(target.id)

            if not variables:
                return CLIResult(output="Переменные не найдены")

            result = "Найденные переменные:\n" + "\n".join(variables)
            return CLIResult(output=result)
        except SyntaxError as e:
            return CLIResult(error=f"Синтаксическая ошибка: {str(e)}")
        except Exception as e:
            return CLIResult(error=f"Ошибка при анализе переменных: {str(e)}")

    async def _analyze_python_full(self, code: str) -> CLIResult:
        """Полный анализ Python кода."""
        try:
            imports_result = await self._analyze_python_imports(code)
            functions_result = await self._analyze_python_functions(code)
            classes_result = await self._analyze_python_classes(code)
            variables_result = await self._analyze_python_variables(code)

            if any(result.error for result in [imports_result, functions_result, classes_result, variables_result]):
                error_results = [result for result in [imports_result, functions_result, classes_result, variables_result] if result.error]
                return CLIResult(error=f"Ошибки при анализе: {', '.join(r.error for r in error_results)}")

            output = "ПОЛНЫЙ АНАЛИЗ КОДА:\n\n"
            if imports_result.output:
                output += imports_result.output + "\n\n"
            if functions_result.output:
                output += functions_result.output + "\n\n"
            if classes_result.output:
                output += classes_result.output + "\n\n"
            if variables_result.output:
                output += variables_result.output

            return CLIResult(output=output)
        except Exception as e:
            return CLIResult(error=f"Ошибка при полном анализе кода: {str(e)}")

    def _detect_language(self, editor) -> str:
        """Определяет язык программирования по расширению файла."""
        file_path = getattr(editor, 'file_path', None)
        if not file_path:
            return 'python'  # По умолчанию

        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.html'):
            return 'html'
        else:
            return 'python'  # По умолчанию

    def notify_ui(self, message: str):
        """Отправляет уведомление в UI."""
        if self.editor_widget and hasattr(self.editor_widget, 'progress_update'):
            self.editor_widget.progress_update.emit(message)
