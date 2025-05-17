"""
Text Editor Access Module для Reasoning Agent

Модуль предоставляет контролируемый доступ к текстовому редактору для ReasoningAgent
с системой разрешений и безопасной работой с файлами.
"""

import os
import re
import difflib
from typing import Dict, List, Optional, Union, Tuple, Any, Set

from app.logger import logger


class TextEditorAccess:
    """
    Класс для безопасного доступа к текстовому редактору в режиме reasoning.

    Предоставляет:
    1. Безопасное чтение и запись текстовых файлов
    2. Поиск по содержимому файлов
    3. Логирование всех операций с файлами
    4. Проверку разрешений и ограничение потенциально опасных операций
    5. Визуализацию различий между версиями файлов
    6. Функции для редактирования файлов (вставка, удаление, замена)
    """

    # Разрешенные расширения файлов для работы
    ALLOWED_EXTENSIONS = {
        ".txt", ".md", ".py", ".js", ".html", ".css", ".json",
        ".yaml", ".yml", ".csv", ".ini", ".cfg", ".conf",
        ".c", ".cpp", ".h", ".hpp", ".cs", ".java", ".kt",
        ".go", ".rs", ".rb", ".ts", ".tsx", ".jsx"
    }

    # Разрешенные директории для доступа (относительно корня проекта)
    ALLOWED_DIRS = [
        ".", "./app", "./tests", "./examples", "./workspace",
        "./data", "./docs", "./scripts", "./logs"
    ]

    # Максимальный размер файла для работы (в байтах)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        root_dir: Optional[str] = None,
        max_file_size: Optional[int] = None,
        safe_mode: bool = True
    ):
        """
        Инициализирует объект доступа к текстовому редактору.

        Args:
            root_dir: Корневая директория проекта (по умолчанию - текущая)
            max_file_size: Максимальный размер файла для работы (в байтах)
            safe_mode: Включение проверок безопасности
        """
        self.root_dir = root_dir or os.getcwd()
        self.max_file_size = max_file_size or self.MAX_FILE_SIZE
        self.safe_mode = safe_mode
        self.file_history: Dict[str, List[Dict[str, Any]]] = {}
        self.allowed_extensions = self.ALLOWED_EXTENSIONS.copy()

        # Создаем набор разрешенных абсолютных путей
        self.allowed_abs_paths = set()
        for rel_path in self.ALLOWED_DIRS:
            abs_path = os.path.abspath(os.path.join(self.root_dir, rel_path.replace("./", "")))
            self.allowed_abs_paths.add(abs_path)

        logger.info(f"Text editor access initialized with root dir: {self.root_dir}")
        logger.info(f"Safe mode: {self.safe_mode}, Max file size: {self.max_file_size} bytes")

    def _is_file_access_allowed(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет, разрешен ли доступ к указанному файлу.

        Args:
            file_path: Путь к файлу для проверки

        Returns:
            Кортеж (разрешен ли доступ, причина отказа)
        """
        if not self.safe_mode:
            return True, None

        # Проверяем существование файла
        if not os.path.exists(file_path) and not file_path.startswith(tuple(self.allowed_abs_paths)):
            return False, f"File does not exist: {file_path}"

        # Проверяем размер файла (только для существующих файлов)
        if os.path.exists(file_path) and os.path.getsize(file_path) > self.max_file_size:
            return False, f"File size exceeds maximum allowed size: {file_path}"

        # Проверяем расширение файла
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.allowed_extensions:
            return False, f"File extension not allowed: {ext}"

        # Проверяем директорию файла
        file_dir = os.path.dirname(os.path.abspath(file_path))
        for allowed_path in self.allowed_abs_paths:
            if file_dir.startswith(allowed_path):
                return True, None

        return False, f"File location not allowed: {file_dir}"

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Безопасно читает содержимое текстового файла.

        Args:
            file_path: Путь к файлу для чтения

        Returns:
            Словарь с результатами операции чтения
        """
        # Нормализуем путь к файлу
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.root_dir, file_path))

        # Проверяем доступ к файлу
        is_allowed, reason = self._is_file_access_allowed(file_path)
        if not is_allowed:
            logger.warning(f"Access to file denied: {file_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "file_path": file_path
            }

        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "file_path": file_path
                }

            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Добавляем запись в историю
            self._add_to_history(file_path, "read", content)

            # Возвращаем результат
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content),
                "lines": content.count('\n') + 1
            }

        except Exception as e:
            logger.error(f"Error reading file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}",
                "file_path": file_path
            }

    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Безопасно записывает содержимое в текстовый файл.

        Args:
            file_path: Путь к файлу для записи
            content: Содержимое для записи
            overwrite: Разрешение на перезапись существующего файла

        Returns:
            Словарь с результатами операции записи
        """
        # Нормализуем путь к файлу
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.root_dir, file_path))

        # Проверяем доступ к файлу
        is_allowed, reason = self._is_file_access_allowed(file_path)
        if not is_allowed:
            logger.warning(f"Access to file denied: {file_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "file_path": file_path
            }

        # Проверка существования файла и параметра overwrite
        if os.path.exists(file_path) and not overwrite:
            return {
                "success": False,
                "error": f"File already exists and overwrite is not allowed: {file_path}",
                "file_path": file_path
            }

        try:
            # Проверяем директорию и создаем, если необходимо
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)

            # Записываем содержимое в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            # Добавляем запись в историю
            self._add_to_history(file_path, "write", content)

            # Возвращаем результат
            return {
                "success": True,
                "file_path": file_path,
                "size": len(content),
                "lines": content.count('\n') + 1
            }

        except Exception as e:
            logger.error(f"Error writing file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}",
                "file_path": file_path
            }

    def append_to_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Безопасно добавляет содержимое в конец текстового файла.

        Args:
            file_path: Путь к файлу для добавления
            content: Содержимое для добавления

        Returns:
            Словарь с результатами операции добавления
        """
        # Нормализуем путь к файлу
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.root_dir, file_path))

        # Проверяем доступ к файлу
        is_allowed, reason = self._is_file_access_allowed(file_path)
        if not is_allowed:
            logger.warning(f"Access to file denied: {file_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "file_path": file_path
            }

        try:
            # Проверяем директорию и создаем, если необходимо
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)

            # Определяем, существует ли файл
            file_exists = os.path.exists(file_path)

            # Получаем текущее содержимое файла
            current_content = ""
            if file_exists:
                with open(file_path, 'r', encoding='utf-8') as file:
                    current_content = file.read()

            # Добавляем новое содержимое
            new_content = current_content + content

            # Записываем обновленное содержимое
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

            # Добавляем запись в историю
            self._add_to_history(file_path, "append", new_content)

            # Возвращаем результат
            return {
                "success": True,
                "file_path": file_path,
                "size": len(new_content),
                "lines": new_content.count('\n') + 1,
                "appended_size": len(content)
            }

        except Exception as e:
            logger.error(f"Error appending to file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error appending to file: {str(e)}",
                "file_path": file_path
            }

    def search_in_file(self, file_path: str, search_pattern: str,
                      case_sensitive: bool = False,
                      whole_word: bool = False) -> Dict[str, Any]:
        """
        Выполняет поиск по содержимому файла.

        Args:
            file_path: Путь к файлу для поиска
            search_pattern: Шаблон поиска (строка или регулярное выражение)
            case_sensitive: Учитывать регистр при поиске
            whole_word: Искать только целые слова

        Returns:
            Словарь с результатами поиска
        """
        # Сначала читаем файл
        read_result = self.read_file(file_path)
        if not read_result["success"]:
            return read_result

        try:
            content = read_result["content"]

            # Подготавливаем регулярное выражение для поиска
            if whole_word:
                pattern = rf'\b{re.escape(search_pattern)}\b'
            else:
                pattern = re.escape(search_pattern)

            flags = 0 if case_sensitive else re.IGNORECASE
            matches = []

            # Производим поиск
            for i, line in enumerate(content.splitlines(), 1):
                for match in re.finditer(pattern, line, flags=flags):
                    matches.append({
                        "line": i,
                        "column": match.start() + 1,
                        "end_column": match.end() + 1,
                        "text": line,
                        "match": match.group(0)
                    })

            # Возвращаем результаты
            return {
                "success": True,
                "file_path": file_path,
                "pattern": search_pattern,
                "matches": matches,
                "match_count": len(matches)
            }

        except Exception as e:
            logger.error(f"Error searching in file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error searching in file: {str(e)}",
                "file_path": file_path
            }

    def edit_lines(self, file_path: str, start_line: int, end_line: int,
                  new_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Редактирует или удаляет определенные строки в файле.

        Args:
            file_path: Путь к файлу для редактирования
            start_line: Номер начальной строки (1-based)
            end_line: Номер конечной строки (1-based, включительно)
            new_content: Новое содержимое для замены строк (None для удаления)

        Returns:
            Словарь с результатами операции редактирования
        """
        # Сначала читаем файл
        read_result = self.read_file(file_path)
        if not read_result["success"]:
            return read_result

        try:
            content = read_result["content"]
            lines = content.splitlines()

            # Проверяем корректность номеров строк
            if start_line < 1 or start_line > len(lines) + 1:
                return {
                    "success": False,
                    "error": f"Invalid start line: {start_line}",
                    "file_path": file_path
                }

            if end_line < start_line or end_line > len(lines):
                return {
                    "success": False,
                    "error": f"Invalid end line: {end_line}",
                    "file_path": file_path
                }

            # Редактируем строки
            before_lines = lines[:start_line - 1]
            after_lines = lines[end_line:]

            # Обрабатываем новое содержимое
            inserted_lines = []
            if new_content is not None:
                inserted_lines = new_content.splitlines()

            # Собираем новое содержимое файла
            new_lines = before_lines + inserted_lines + after_lines
            new_file_content = '\n'.join(new_lines)
            if lines and not content.endswith('\n') and new_lines:
                new_file_content += '\n'

            # Записываем обновленное содержимое
            write_result = self.write_file(file_path, new_file_content, overwrite=True)
            if not write_result["success"]:
                return write_result

            # Возвращаем результат
            operation = "replaced" if new_content is not None else "deleted"
            return {
                "success": True,
                "file_path": file_path,
                "operation": operation,
                "start_line": start_line,
                "end_line": end_line,
                "lines_affected": end_line - start_line + 1,
                "lines_inserted": len(inserted_lines)
            }

        except Exception as e:
            logger.error(f"Error editing lines in file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error editing lines: {str(e)}",
                "file_path": file_path
            }

    def insert_at_line(self, file_path: str, line_number: int, content: str) -> Dict[str, Any]:
        """
        Вставляет содержимое перед указанной строкой файла.

        Args:
            file_path: Путь к файлу для вставки
            line_number: Номер строки, перед которой произвести вставку (1-based)
            content: Содержимое для вставки

        Returns:
            Словарь с результатами операции вставки
        """
        # Сначала читаем файл
        read_result = self.read_file(file_path)
        # Для нового файла
        if not read_result["success"] and "File not found" in read_result.get("error", ""):
            if line_number == 1:
                return self.write_file(file_path, content)
            else:
                return {
                    "success": False,
                    "error": f"Cannot insert at line {line_number} in a new file",
                    "file_path": file_path
                }
        # Другие ошибки
        elif not read_result["success"]:
            return read_result

        try:
            content_lines = read_result["content"].splitlines()

            # Проверяем корректность номера строки
            if line_number < 1 or line_number > len(content_lines) + 1:
                return {
                    "success": False,
                    "error": f"Invalid line number: {line_number}",
                    "file_path": file_path
                }

            # Вставляем содержимое
            insert_lines = content.splitlines()
            new_lines = content_lines[:line_number - 1] + insert_lines + content_lines[line_number - 1:]
            new_content = '\n'.join(new_lines)

            # Сохраняем конечный перенос строки, если он был
            if read_result["content"].endswith('\n') and not new_content.endswith('\n'):
                new_content += '\n'

            # Записываем обновленное содержимое
            write_result = self.write_file(file_path, new_content, overwrite=True)
            if not write_result["success"]:
                return write_result

            # Возвращаем результат
            return {
                "success": True,
                "file_path": file_path,
                "operation": "insert",
                "line_number": line_number,
                "lines_inserted": len(insert_lines)
            }

        except Exception as e:
            logger.error(f"Error inserting at line in file: {file_path}. Error: {str(e)}")
            return {
                "success": False,
                "error": f"Error inserting at line: {str(e)}",
                "file_path": file_path
            }

    def create_diff(self, original_content: str, new_content: str) -> Dict[str, Any]:
        """
        Создает представление различий между двумя версиями содержимого.

        Args:
            original_content: Исходное содержимое
            new_content: Новое содержимое

        Returns:
            Словарь с результатами создания diff
        """
        try:
            original_lines = original_content.splitlines()
            new_lines = new_content.splitlines()

            # Создаем diff
            diff = list(difflib.unified_diff(
                original_lines,
                new_lines,
                lineterm='',
                n=3  # Контекст - 3 строки
            ))

            # Форматируем результат
            return {
                "success": True,
                "diff": '\n'.join(diff),
                "diff_lines": diff,
                "lines_added": sum(1 for line in diff if line.startswith('+')),
                "lines_removed": sum(1 for line in diff if line.startswith('-')),
                "chunks": len([1 for line in diff if line.startswith('@@')])
            }

        except Exception as e:
            logger.error(f"Error creating diff: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating diff: {str(e)}"
            }

    def get_file_history(self, file_path: str) -> Dict[str, Any]:
        """
        Возвращает историю изменений файла.

        Args:
            file_path: Путь к файлу для получения истории

        Returns:
            Словарь с историей изменений файла
        """
        # Нормализуем путь к файлу
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.root_dir, file_path))

        # Проверяем существование истории для файла
        if file_path not in self.file_history:
            return {
                "success": True,
                "file_path": file_path,
                "history": [],
                "version_count": 0
            }

        # Возвращаем историю
        history = self.file_history[file_path]
        return {
            "success": True,
            "file_path": file_path,
            "history": history,
            "version_count": len(history)
        }

    def find_files_by_extension(self, extensions: List[str], directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Находит все файлы с указанными расширениями в директории.

        Args:
            extensions: Список расширений файлов для поиска
            directory: Директория для поиска (относительно корня проекта)

        Returns:
            Словарь с результатами поиска
        """
        # Определяем директорию для поиска
        search_dir = self.root_dir
        if directory:
            if not os.path.isabs(directory):
                search_dir = os.path.abspath(os.path.join(self.root_dir, directory))
            else:
                search_dir = directory

        # Проверяем доступ к директории
        if self.safe_mode:
            allowed = False
            for allowed_path in self.allowed_abs_paths:
                if search_dir.startswith(allowed_path):
                    allowed = True
                    break

            if not allowed:
                return {
                    "success": False,
                    "error": f"Access to directory denied: {search_dir}",
                    "directory": search_dir
                }

        try:
            # Выполняем поиск файлов
            found_files = []

            # Проверяем, что все расширения начинаются с точки
            normalized_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

            for root, _, files in os.walk(search_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)
                    if ext.lower() in normalized_extensions:
                        # Проверяем доступ к файлу
                        is_allowed, _ = self._is_file_access_allowed(file_path)
                        if is_allowed:
                            rel_path = os.path.relpath(file_path, self.root_dir)
                            found_files.append({
                                "path": file_path,
                                "relative_path": rel_path,
                                "extension": ext,
                                "size": os.path.getsize(file_path)
                            })

            # Возвращаем результаты поиска
            return {
                "success": True,
                "directory": search_dir,
                "extensions": extensions,
                "files": found_files,
                "count": len(found_files)
            }

        except Exception as e:
            logger.error(f"Error finding files: {str(e)}")
            return {
                "success": False,
                "error": f"Error finding files: {str(e)}",
                "directory": search_dir
            }

    def add_allowed_extension(self, extension: str) -> bool:
        """
        Добавляет расширение файла в список разрешенных.

        Args:
            extension: Расширение файла для добавления

        Returns:
            True если расширение успешно добавлено
        """
        # Проверяем, начинается ли расширение с точки
        if not extension.startswith('.'):
            extension = f'.{extension}'

        # Добавляем расширение в список
        if extension.lower() not in self.allowed_extensions:
            self.allowed_extensions.add(extension.lower())
            logger.info(f"Added allowed file extension: {extension}")
            return True

        return False

    def add_allowed_directory(self, directory: str) -> bool:
        """
        Добавляет директорию в список разрешенных.

        Args:
            directory: Путь к директории (относительный от корня проекта)

        Returns:
            True если директория успешно добавлена
        """
        if not directory:
            return False

        # Нормализуем путь
        if not directory.startswith("./") and not directory == ".":
            directory = f"./{directory}"

        # Проверяем, что директория находится внутри корневой
        abs_dir = os.path.abspath(os.path.join(self.root_dir, directory.replace("./", "")))
        abs_root = os.path.abspath(self.root_dir)

        if not abs_dir.startswith(abs_root):
            logger.warning(f"Cannot add directory outside of project root: {directory}")
            return False

        # Добавляем в список разрешенных
        if directory not in self.ALLOWED_DIRS:
            self.ALLOWED_DIRS.append(directory)
            self.allowed_abs_paths.add(abs_dir)
            logger.info(f"Added allowed directory: {directory}")
            return True

        return False

    def _add_to_history(self, file_path: str, operation: str, content: str) -> None:
        """
        Добавляет запись в историю файла.

        Args:
            file_path: Путь к файлу
            operation: Тип операции (чтение, запись, добавление)
            content: Содержимое файла после операции
        """
        if file_path not in self.file_history:
            self.file_history[file_path] = []

        # Создаем запись истории
        import time
        history_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "content": content,
            "size": len(content),
            "lines": content.count('\n') + 1
        }

        # Добавляем в историю
        self.file_history[file_path].append(history_entry)

        # Ограничиваем размер истории (храним до 10 последних версий)
        if len(self.file_history[file_path]) > 10:
            self.file_history[file_path] = self.file_history[file_path][-10:]
