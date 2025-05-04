"""
File System Access Module для Reasoning Agent

Модуль предоставляет контролируемый доступ к файловой системе для ReasoningAgent
с системой разрешений и безопасным выполнением файловых операций.
"""

import os
import re
import shutil
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any, Set, BinaryIO

from app.logger import logger


class FileSystemAccess:
    """
    Класс для безопасного доступа к файловой системе в режиме reasoning.

    Предоставляет:
    1. Проверку безопасности путей перед выполнением операций
    2. Контролируемый доступ к файлам и директориям
    3. Логирование всех файловых операций
    4. Ограничение опасных операций
    5. Преобразование путей из чата в абсолютные
    """

    # Расширения файлов, считающиеся потенциально опасными
    UNSAFE_EXTENSIONS = {
        ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".msi", ".dll",
        ".com", ".scr", ".pif", ".application", ".gadget", ".msc", ".jar"
    }

    # Разрешенные директории для доступа (относительно корня проекта)
    ALLOWED_DIRS = [
        ".", "./app", "./tests", "./examples", "./workspace",
        "./data", "./docs", "./scripts", "./logs"
    ]

    # Шаблоны опасных операций с файлами
    UNSAFE_PATH_PATTERNS = [
        r"\.\.\/", r"\.\.\\"  # Пути с выходом на уровень выше
    ]

    def __init__(
        self,
        root_dir: Optional[str] = None,
        safe_mode: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        chat_paths_enabled: bool = True
    ):
        """
        Инициализирует объект доступа к файловой системе.

        Args:
            root_dir: Корневая директория проекта (по умолчанию - текущая)
            safe_mode: Включение проверок безопасности
            max_file_size: Максимальный размер файла для чтения/записи в байтах
            chat_paths_enabled: Разрешить использование путей из чата
        """
        self.root_dir = root_dir or os.getcwd()
        self.safe_mode = safe_mode
        self.max_file_size = max_file_size
        self.chat_paths_enabled = chat_paths_enabled
        self.operation_history: List[Dict[str, Any]] = []
        self.current_dir = self.root_dir

        logger.info(f"File system access initialized with root dir: {self.root_dir}")

    def _is_path_safe(self, path: str) -> Tuple[bool, str]:
        """
        Проверяет безопасность пути для выполнения операций.

        Args:
            path: Путь для проверки

        Returns:
            Кортеж (безопасность, причина небезопасности)
        """
        if not self.safe_mode:
            return True, ""

        # Проверяем наличие опасных паттернов в пути
        for pattern in self.UNSAFE_PATH_PATTERNS:
            if re.search(pattern, path):
                return False, f"Путь содержит потенциально опасный паттерн: {pattern}"

        # Проверяем расширение файла, если это файл
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in self.UNSAFE_EXTENSIONS:
                return False, f"Файл имеет потенциально опасное расширение: {ext}"

        # Проверяем, находится ли путь внутри разрешенной директории
        abs_path = os.path.abspath(path)
        abs_root = os.path.abspath(self.root_dir)
        if not abs_path.startswith(abs_root):
            return False, f"Путь находится за пределами корневой директории: {abs_root}"

        # Проверяем, есть ли путь в списке разрешенных
        rel_path = os.path.relpath(abs_path, abs_root)
        for allowed in self.ALLOWED_DIRS:
            allowed_path = allowed.replace("./", "").replace(".", "")
            if rel_path == allowed_path or rel_path.startswith(f"{allowed_path}/") or rel_path.startswith(f"{allowed_path}\\"):
                return True, ""

        return False, f"Путь не находится в разрешенной директории"

    def _is_operation_safe(self, operation: str, path: str) -> Tuple[bool, str]:
        """
        Проверяет безопасность операции с файлом или директорией.

        Args:
            operation: Тип операции (read, write, delete, etc.)
            path: Путь к файлу или директории

        Returns:
            Кортеж (безопасность, причина небезопасности)
        """
        if not self.safe_mode:
            return True, ""

        # Проверяем безопасность пути
        path_safe, reason = self._is_path_safe(path)
        if not path_safe:
            return False, reason

        # Дополнительные проверки для различных операций
        if operation == "delete":
            # Проверяем, что не пытаемся удалить корневую директорию
            if os.path.abspath(path) == os.path.abspath(self.root_dir):
                return False, "Удаление корневой директории запрещено"

        if operation == "write":
            # Проверяем, что мы не пытаемся перезаписать системные файлы
            if any(dir_name in path.lower() for dir_name in ["system32", "windows", "programfiles"]):
                return False, "Запись в системные директории запрещена"

        return True, ""

    def _normalize_path(self, path: str, relative_to: Optional[str] = None) -> str:
        """
        Нормализует путь, преобразуя его в абсолютный.

        Args:
            path: Путь для нормализации
            relative_to: Директория, относительно которой интерпретировать путь (по умолчанию текущая)

        Returns:
            Нормализованный абсолютный путь
        """
        if not path:
            return self.current_dir

        # Если путь из чата отключен, то используем только путь из текущей директории
        if not self.chat_paths_enabled and relative_to != self.current_dir:
            relative_to = self.current_dir

        # Если путь абсолютный, проверяем его безопасность и возвращаем
        if os.path.isabs(path):
            return path

        # Иначе преобразуем относительный путь
        base_dir = relative_to or self.current_dir
        return os.path.abspath(os.path.join(base_dir, path))

    def parse_chat_path(self, chat_text: str) -> Optional[str]:
        """
        Извлекает и проверяет путь из сообщения в чате.

        Args:
            chat_text: Текст сообщения из чата

        Returns:
            Нормализованный абсолютный путь или None, если путь не найден или небезопасен
        """
        if not self.chat_paths_enabled:
            return None

        # Ищем пути в формате: /path/to/file, ./path/to/file, path\to\file
        path_patterns = [
            r'(?:^|\s)([\'"]?(?:\.{0,2}[\/\\])?[\w\-\.\~]+(?:[\/\\][\w\-\.\~]+)*[\'"]?)',  # Относительные пути
            r'(?:^|\s)([\'"]?[a-zA-Z]:[\/\\](?:[\w\-\.\~]+[\/\\])*[\w\-\.\~]*[\'"]?)'     # Windows абсолютные пути
        ]

        for pattern in path_patterns:
            matches = re.findall(pattern, chat_text)
            for match in matches:
                # Удаляем кавычки если они есть
                path = match.strip('\'"')

                # Нормализуем путь
                norm_path = self._normalize_path(path)

                # Проверяем безопасность пути
                is_safe, _ = self._is_path_safe(norm_path)
                if is_safe:
                    return norm_path

        return None

    def set_current_directory(self, directory: str) -> bool:
        """
        Устанавливает текущую рабочую директорию.

        Args:
            directory: Новая рабочая директория

        Returns:
            True если директория успешно установлена
        """
        norm_dir = self._normalize_path(directory)

        # Проверяем безопасность директории
        is_safe, reason = self._is_path_safe(norm_dir)
        if not is_safe:
            logger.warning(f"Access to directory denied: {norm_dir}. Reason: {reason}")
            return False

        # Проверяем существование директории
        if not os.path.exists(norm_dir) or not os.path.isdir(norm_dir):
            logger.warning(f"Directory does not exist: {norm_dir}")
            return False

        # Устанавливаем новую директорию
        self.current_dir = norm_dir
        logger.info(f"Current directory set to: {self.current_dir}")

        # Записываем операцию в историю
        self._add_to_history("set_directory", norm_dir, True)

        return True

    def get_current_directory(self) -> str:
        """
        Возвращает текущую рабочую директорию.

        Returns:
            Путь к текущей рабочей директории
        """
        return self.current_dir

    def _add_to_history(self, operation: str, path: str, success: bool, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Добавляет операцию в историю.

        Args:
            operation: Тип операции
            path: Путь к файлу или директории
            success: Успешность операции
            details: Дополнительные детали операции
        """
        record = {
            "operation": operation,
            "path": path,
            "success": success,
            "timestamp": asyncio.get_event_loop().time(),
            "details": details or {}
        }
        self.operation_history.append(record)

    async def read_file(self, file_path: str, mode: str = "text", encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Безопасно читает содержимое файла.

        Args:
            file_path: Путь к файлу для чтения
            mode: Режим чтения ("text" или "binary")
            encoding: Кодировка для текстового режима

        Returns:
            Словарь с результатами чтения
        """
        # Нормализуем путь
        norm_path = self._normalize_path(file_path)

        # Проверяем безопасность операции
        is_safe, reason = self._is_operation_safe("read", norm_path)
        if not is_safe:
            logger.warning(f"Read operation denied for: {norm_path}. Reason: {reason}")
            return {
                "success": False,
                "content": None,
                "error": f"Access denied: {reason}",
                "path": norm_path
            }

        try:
            # Проверяем существование файла
            if not os.path.exists(norm_path):
                logger.warning(f"File does not exist: {norm_path}")
                return {
                    "success": False,
                    "content": None,
                    "error": "File does not exist",
                    "path": norm_path
                }

            # Проверяем размер файла
            file_size = os.path.getsize(norm_path)
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {norm_path} ({file_size} bytes)")
                return {
                    "success": False,
                    "content": None,
                    "error": f"File too large: {file_size} bytes (max: {self.max_file_size})",
                    "path": norm_path
                }

            # Читаем файл в соответствующем режиме
            if mode == "binary":
                with open(norm_path, "rb") as f:
                    content = f.read()

                # Для binary режима возвращаем base64 представление
                result = {
                    "success": True,
                    "content": content,
                    "size": file_size,
                    "path": norm_path,
                    "mode": "binary"
                }
            else:
                with open(norm_path, "r", encoding=encoding) as f:
                    content = f.read()

                result = {
                    "success": True,
                    "content": content,
                    "size": file_size,
                    "path": norm_path,
                    "mode": "text",
                    "encoding": encoding
                }

            # Записываем операцию в историю
            self._add_to_history("read", norm_path, True, {"size": file_size, "mode": mode})

            return result

        except Exception as e:
            logger.error(f"Error reading file {norm_path}: {str(e)}")
            return {
                "success": False,
                "content": None,
                "error": f"Error reading file: {str(e)}",
                "path": norm_path
            }

    async def write_file(
        self,
        file_path: str,
        content: Union[str, bytes],
        mode: str = "text",
        encoding: str = "utf-8",
        create_dirs: bool = False
    ) -> Dict[str, Any]:
        """
        Безопасно записывает данные в файл.

        Args:
            file_path: Путь к файлу для записи
            content: Содержимое для записи (строка или байты)
            mode: Режим записи ("text" или "binary")
            encoding: Кодировка для текстового режима
            create_dirs: Создавать родительские директории, если их нет

        Returns:
            Словарь с результатами записи
        """
        # Нормализуем путь
        norm_path = self._normalize_path(file_path)

        # Проверяем безопасность операции
        is_safe, reason = self._is_operation_safe("write", norm_path)
        if not is_safe:
            logger.warning(f"Write operation denied for: {norm_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "path": norm_path
            }

        try:
            # Проверяем размер содержимого
            content_size = len(content)
            if content_size > self.max_file_size:
                logger.warning(f"Content too large for file: {norm_path} ({content_size} bytes)")
                return {
                    "success": False,
                    "error": f"Content too large: {content_size} bytes (max: {self.max_file_size})",
                    "path": norm_path
                }

            # Создаем родительские директории если нужно
            dir_path = os.path.dirname(norm_path)
            if dir_path and not os.path.exists(dir_path):
                if create_dirs:
                    # Проверяем безопасность создания директорий
                    dir_safe, dir_reason = self._is_path_safe(dir_path)
                    if not dir_safe:
                        logger.warning(f"Creating directory denied: {dir_path}. Reason: {dir_reason}")
                        return {
                            "success": False,
                            "error": f"Cannot create directory: {dir_reason}",
                            "path": norm_path
                        }
                    os.makedirs(dir_path, exist_ok=True)
                else:
                    logger.warning(f"Parent directory does not exist: {dir_path}")
                    return {
                        "success": False,
                        "error": f"Parent directory does not exist: {dir_path}",
                        "path": norm_path
                    }

            # Записываем файл в соответствующем режиме
            if mode == "binary":
                if isinstance(content, str):
                    logger.warning(f"Expected bytes for binary mode, got string for file: {norm_path}")
                    return {
                        "success": False,
                        "error": f"Expected bytes for binary mode, got string",
                        "path": norm_path
                    }

                with open(norm_path, "wb") as f:
                    f.write(content)
            else:
                if isinstance(content, bytes):
                    logger.warning(f"Expected string for text mode, got bytes for file: {norm_path}")
                    return {
                        "success": False,
                        "error": f"Expected string for text mode, got bytes",
                        "path": norm_path
                    }

                with open(norm_path, "w", encoding=encoding) as f:
                    f.write(content)

            # Записываем операцию в историю
            self._add_to_history("write", norm_path, True, {"size": content_size, "mode": mode})

            return {
                "success": True,
                "path": norm_path,
                "size": content_size,
                "mode": mode
            }

        except Exception as e:
            logger.error(f"Error writing to file {norm_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Error writing to file: {str(e)}",
                "path": norm_path
            }

    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Безопасно удаляет файл.

        Args:
            file_path: Путь к файлу для удаления

        Returns:
            Словарь с результатами удаления
        """
        # Нормализуем путь
        norm_path = self._normalize_path(file_path)

        # Проверяем безопасность операции
        is_safe, reason = self._is_operation_safe("delete", norm_path)
        if not is_safe:
            logger.warning(f"Delete operation denied for: {norm_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "path": norm_path
            }

        try:
            # Проверяем существование файла
            if not os.path.exists(norm_path):
                logger.warning(f"File does not exist: {norm_path}")
                return {
                    "success": False,
                    "error": "File does not exist",
                    "path": norm_path
                }

            # Проверяем, что это файл, а не директория
            if not os.path.isfile(norm_path):
                logger.warning(f"Not a file: {norm_path}")
                return {
                    "success": False,
                    "error": "Not a file",
                    "path": norm_path
                }

            # Удаляем файл
            os.remove(norm_path)

            # Записываем операцию в историю
            self._add_to_history("delete", norm_path, True)

            return {
                "success": True,
                "path": norm_path
            }

        except Exception as e:
            logger.error(f"Error deleting file {norm_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Error deleting file: {str(e)}",
                "path": norm_path
            }

    async def list_directory(
        self,
        directory: str,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Безопасно перечисляет содержимое директории.

        Args:
            directory: Путь к директории
            pattern: Шаблон для фильтрации файлов
            recursive: Рекурсивный обход директорий

        Returns:
            Словарь с результатами перечисления
        """
        # Нормализуем путь
        norm_path = self._normalize_path(directory)

        # Проверяем безопасность операции
        is_safe, reason = self._is_path_safe(norm_path)
        if not is_safe:
            logger.warning(f"List operation denied for: {norm_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "path": norm_path
            }

        try:
            # Проверяем существование директории
            if not os.path.exists(norm_path):
                logger.warning(f"Directory does not exist: {norm_path}")
                return {
                    "success": False,
                    "error": "Directory does not exist",
                    "path": norm_path
                }

            # Проверяем, что это директория
            if not os.path.isdir(norm_path):
                logger.warning(f"Not a directory: {norm_path}")
                return {
                    "success": False,
                    "error": "Not a directory",
                    "path": norm_path
                }

            # Получаем список файлов
            result = {
                "success": True,
                "path": norm_path,
                "directories": [],
                "files": []
            }

            if recursive:
                for root, dirs, files in os.walk(norm_path):
                    # Получаем относительный путь
                    rel_root = os.path.relpath(root, norm_path)
                    if rel_root == ".":
                        rel_root = ""

                    # Добавляем директории
                    for dir_name in dirs:
                        dir_path = os.path.join(rel_root, dir_name) if rel_root else dir_name
                        result["directories"].append(dir_path)

                    # Добавляем файлы
                    for file_name in files:
                        file_path = os.path.join(rel_root, file_name) if rel_root else file_name
                        if not pattern or re.match(pattern, file_name):
                            result["files"].append(file_path)
            else:
                # Без рекурсии, только прямые члены директории
                with os.scandir(norm_path) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            result["directories"].append(entry.name)
                        elif entry.is_file():
                            if not pattern or re.match(pattern, entry.name):
                                result["files"].append(entry.name)

            # Записываем операцию в историю
            self._add_to_history("list", norm_path, True, {
                "recursive": recursive,
                "pattern": pattern,
                "directories_count": len(result["directories"]),
                "files_count": len(result["files"])
            })

            return result

        except Exception as e:
            logger.error(f"Error listing directory {norm_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}",
                "path": norm_path
            }

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Получает информацию о файле.

        Args:
            file_path: Путь к файлу

        Returns:
            Словарь с информацией о файле
        """
        # Нормализуем путь
        norm_path = self._normalize_path(file_path)

        # Проверяем безопасность операции
        is_safe, reason = self._is_path_safe(norm_path)
        if not is_safe:
            logger.warning(f"Get info operation denied for: {norm_path}. Reason: {reason}")
            return {
                "success": False,
                "error": f"Access denied: {reason}",
                "path": norm_path
            }

        try:
            # Проверяем существование файла
            if not os.path.exists(norm_path):
                logger.warning(f"File does not exist: {norm_path}")
                return {
                    "success": False,
                    "error": "File does not exist",
                    "path": norm_path
                }

            # Получаем информацию о файле
            stat_info = os.stat(norm_path)

            result = {
                "success": True,
                "path": norm_path,
                "exists": True,
                "is_file": os.path.isfile(norm_path),
                "is_dir": os.path.isdir(norm_path),
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "name": os.path.basename(norm_path),
                "extension": os.path.splitext(norm_path)[1].lower() if os.path.isfile(norm_path) else "",
                "parent": os.path.dirname(norm_path)
            }

            # Записываем операцию в историю
            self._add_to_history("get_info", norm_path, True)

            return result

        except Exception as e:
            logger.error(f"Error getting info for {norm_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting file info: {str(e)}",
                "path": norm_path
            }

    def get_operation_history(self) -> List[Dict[str, Any]]:
        """
        Возвращает историю файловых операций.

        Returns:
            Список словарей с информацией о выполненных операциях
        """
        return self.operation_history
