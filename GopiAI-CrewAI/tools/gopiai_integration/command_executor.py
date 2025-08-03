"""
Переписанный CommandExecutor с прямым интерфейсом методов.
Реализует безопасное выполнение инструментов без текстового парсинга.
"""

import json
import subprocess
import os
import logging
import time
import shutil
import hashlib
import glob
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Класс для безопасного выполнения инструментов через прямые методы.
    Заменяет текстовый парсинг на нативные вызовы методов.
    """

    def __init__(self):
        self.logger = logger
        
        # Белый список разрешённых команд для безопасности
        self.allowed_commands = {
            # Базовые команды навигации и просмотра
            "ls", "dir", "pwd", "cd", "echo", "type", "cat", "head", "tail",
            "tree", "find", "grep", "which", "where", "whoami", "date", "time",
            
            # Файловые операции
            "mkdir", "touch", "copy", "cp", "move", "mv", "chmod", "stat", "file",
            
            # Системная информация
            "ps", "top", "htop", "netstat", "ping", "hostname", "uptime", 
            "uname", "env", "printenv", "history", "du", "df", "free",
            
            # Инструменты разработки
            "python", "pip", "git", "node", "npm", "yarn", "curl", "wget",
            
            # Текстовые утилиты
            "wc", "sort", "uniq", "diff", "patch",
            
            # Команды для тестирования (безопасные)
            "timeout", "sleep", "test",
        }
        
        # Опасные команды, требующие особого внимания
        self.dangerous_commands = {
            "rm", "del", "rmdir", "format", "fdisk", "shutdown", "reboot",
            "kill", "killall", "pkill", "sudo", "su", "chmod", "chown"
        }
        
        # Максимальные размеры для предотвращения перегрузки
        self.max_output_size = 10000  # символов
        self.max_file_size = 5000     # символов для чтения файлов
        self.max_search_results = 10  # результатов поиска
        
        self.logger.info("[COMMAND-EXECUTOR] Инициализирован с прямым интерфейсом методов")

    def execute_terminal_command(
        self, 
        command: str, 
        working_directory: str = None, 
        timeout: int = 30
    ) -> str:
        """
        Выполняет команду терминала с проверкой безопасности.
        
        Args:
            command: Команда для выполнения
            working_directory: Рабочая директория (опционально)
            timeout: Таймаут выполнения в секундах
            
        Returns:
            str: Результат выполнения команды или сообщение об ошибке
        """
        start_time = time.time()
        
        try:
            # Валидация входных данных
            if not command or not command.strip():
                from .error_handler import error_handler
                return error_handler.handle_tool_error(
                    ValueError("Пустая команда"),
                    "execute_terminal_command",
                    {"command": command, "working_directory": working_directory}
                )

            command = command.strip()
            self.logger.info(f"[TERMINAL] Выполнение команды: '{command}'")
            
            if working_directory:
                self.logger.info(f"[TERMINAL] Рабочая директория: '{working_directory}'")
            
            # Проверка безопасности команды
            safety_result = self._validate_command_safety(command)
            if not safety_result["safe"]:
                from .error_handler import error_handler
                return error_handler.handle_command_safety_error(
                    command, 
                    safety_result['reason'],
                    {"working_directory": working_directory}
                )
            
            # Подготовка рабочей директории
            work_dir = self._prepare_working_directory(working_directory)
            
            # Выполнение команды
            result = self._execute_command_safely(command, work_dir, timeout)
            
            execution_time = time.time() - start_time
            self.logger.info(f"[TERMINAL] Команда выполнена за {execution_time:.2f}с")
            
            return result
            
        except subprocess.TimeoutExpired as e:
            from error_handler import error_handler
            return error_handler.handle_timeout_error(
                f"выполнение команды '{command}'",
                timeout,
                {"command": command, "working_directory": working_directory}
            )
        except PermissionError as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "execute_terminal_command",
                {"command": command, "working_directory": working_directory, "error_type": "permission"}
            )
        except FileNotFoundError as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "execute_terminal_command", 
                {"command": command, "working_directory": working_directory, "error_type": "file_not_found"}
            )
        except Exception as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "execute_terminal_command",
                {"command": command, "working_directory": working_directory, "execution_time": time.time() - start_time}
            )

    def browse_website(
        self, 
        url: str, 
        action: str = "navigate", 
        selector: str = "", 
        extract_text: bool = True,
        max_content_length: int = 3000
    ) -> str:
        """
        Открывает веб-страницу и извлекает контент.
        
        Args:
            url: URL для открытия
            action: Действие (navigate, extract)
            selector: CSS селектор для извлечения
            extract_text: Извлекать только текст
            max_content_length: Максимальная длина контента
            
        Returns:
            str: Содержимое страницы или сообщение об ошибке
        """
        start_time = time.time()
        
        try:
            # Валидация URL
            if not url or not url.strip():
                from error_handler import error_handler
                return error_handler.handle_tool_error(
                    ValueError("Пустой URL"),
                    "browse_website",
                    {"url": url, "action": action, "selector": selector}
                )
                
            url = url.strip()
            self.logger.info(f"[BROWSER] Открытие страницы: '{url}'")
            self.logger.info(f"[BROWSER] Действие: '{action}'")
            
            # Проверка безопасности URL
            if not self._validate_url_safety(url):
                from error_handler import error_handler
                return error_handler.handle_command_safety_error(
                    f"browse_website {url}",
                    f"Небезопасный URL '{url}'",
                    {"url": url, "action": action}
                )
            
            # Выполнение запроса
            content = self._fetch_web_content(url, selector, extract_text, max_content_length)
            
            execution_time = time.time() - start_time
            self.logger.info(f"[BROWSER] Страница обработана за {execution_time:.2f}с")
            
            return content
            
        except ImportError as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "browse_website",
                {"url": url, "action": action, "error_type": "missing_dependency", "missing_modules": "requests, beautifulsoup4"}
            )
        except ConnectionError as e:
            from error_handler import error_handler
            return error_handler.handle_network_error(
                e,
                url,
                "browse_website",
                {"action": action, "selector": selector}
            )
        except TimeoutError as e:
            from error_handler import error_handler
            return error_handler.handle_timeout_error(
                f"загрузка веб-страницы '{url}'",
                10,  # стандартный таймаут для веб-запросов
                {"url": url, "action": action}
            )
        except Exception as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "browse_website",
                {"url": url, "action": action, "selector": selector, "execution_time": time.time() - start_time}
            )

    def web_search(
        self, 
        query: str, 
        num_results: int = 5, 
        search_engine: str = "duckduckgo"
    ) -> str:
        """
        Выполняет поиск в интернете.
        
        Args:
            query: Поисковый запрос
            num_results: Количество результатов
            search_engine: Поисковая система
            
        Returns:
            str: Результаты поиска или сообщение об ошибке
        """
        start_time = time.time()
        
        try:
            # Валидация запроса
            if not query or not query.strip():
                from error_handler import error_handler
                return error_handler.handle_tool_error(
                    ValueError("Пустой поисковый запрос"),
                    "web_search",
                    {"query": query, "num_results": num_results, "search_engine": search_engine}
                )
                
            query = query.strip()
            num_results = max(1, min(num_results, self.max_search_results))
            
            self.logger.info(f"[SEARCH] Поиск: '{query}'")
            self.logger.info(f"[SEARCH] Поисковик: '{search_engine}', результатов: {num_results}")
            
            # Выполнение поиска
            results = self._perform_web_search(query, num_results, search_engine)
            
            execution_time = time.time() - start_time
            self.logger.info(f"[SEARCH] Поиск выполнен за {execution_time:.2f}с")
            
            return results
            
        except ImportError as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "web_search",
                {"query": query, "search_engine": search_engine, "error_type": "missing_dependency", "missing_modules": "requests, beautifulsoup4"}
            )
        except ConnectionError as e:
            from error_handler import error_handler
            return error_handler.handle_network_error(
                e,
                f"поисковая система {search_engine}",
                "web_search",
                {"query": query, "num_results": num_results}
            )
        except TimeoutError as e:
            from error_handler import error_handler
            return error_handler.handle_timeout_error(
                f"поиск в интернете '{query}'",
                10,  # стандартный таймаут для поиска
                {"query": query, "search_engine": search_engine}
            )
        except Exception as e:
            from error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "web_search",
                {"query": query, "num_results": num_results, "search_engine": search_engine, "execution_time": time.time() - start_time}
            )

    def file_operations(
        self, 
        operation: str, 
        path: str, 
        content: str = "", 
        destination: str = "",
        encoding: str = "utf-8",
        max_file_size: int = None
    ) -> str:
        """
        Выполняет безопасные операции с файловой системой.
        
        Поддерживаемые операции:
        - read: Чтение файла
        - write: Запись в файл
        - list_dir: Список содержимого директории
        - exists: Проверка существования файла/директории
        - info: Получение информации о файле/директории
        - copy: Копирование файла/директории
        - move: Перемещение файла/директории
        - delete: Удаление файла/директории
        - mkdir: Создание директории
        
        Args:
            operation: Тип операции
            path: Путь к файлу/директории
            content: Содержимое для записи (для операции write)
            destination: Путь назначения (для операций copy/move)
            encoding: Кодировка файла (по умолчанию utf-8)
            max_file_size: Максимальный размер файла в байтах (None = использовать по умолчанию)
            
        Returns:
            str: Структурированный результат операции в JSON-подобном формате
        """
        start_time = time.time()
        
        try:
            # Валидация параметров
            if not operation or not operation.strip():
                from error_handler import error_handler
                return error_handler.handle_tool_error(
                    ValueError("Не указана операция"),
                    "file_operations",
                    {"operation": operation, "path": path, "destination": destination}
                )
                
            if not path or not path.strip():
                from error_handler import error_handler
                return error_handler.handle_tool_error(
                    ValueError("Не указан путь"),
                    "file_operations",
                    {"operation": operation, "path": path, "destination": destination}
                )
                
            operation = operation.strip().lower()
            path = os.path.normpath(path.strip())
            
            # Нормализация имени операции для совместимости
            operation_mapping = {
                "list": "list_dir",
                "ls": "list_dir", 
                "dir": "list_dir",
                "create_dir": "mkdir",
                "create_directory": "mkdir",
                "remove": "delete",
                "rm": "delete",
                "del": "delete"
            }
            operation = operation_mapping.get(operation, operation)
            
            self.logger.info(f"[FILE-OPS] Операция: '{operation}', путь: '{path}'")
            
            # Проверка безопасности пути
            if not self._validate_path_safety(path):
                from error_handler import error_handler
                return error_handler.handle_command_safety_error(
                    f"file_operations {operation} {path}",
                    f"Небезопасный путь '{path}' - доступ запрещён по соображениям безопасности",
                    {"operation": operation, "path": path, "destination": destination}
                )
            
            # Проверка безопасности пути назначения для операций копирования/перемещения
            if destination and not self._validate_path_safety(destination):
                from error_handler import error_handler
                return error_handler.handle_command_safety_error(
                    f"file_operations {operation} {path} -> {destination}",
                    f"Небезопасный путь назначения '{destination}' - доступ запрещён",
                    {"operation": operation, "path": path, "destination": destination}
                )
            
            # Установка лимитов размера файла
            if max_file_size is None:
                max_file_size = self.max_file_size
            
            # Выполнение операции
            result = self._execute_file_operation(
                operation, path, content, destination, encoding, max_file_size
            )
            
            execution_time = time.time() - start_time
            self.logger.info(f"[FILE-OPS] Операция '{operation}' выполнена за {execution_time:.2f}с")
            
            return result
            
        except FileNotFoundError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding}
            )
        except PermissionError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "permission"}
            )
        except IsADirectoryError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "is_directory"}
            )
        except NotADirectoryError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "not_directory"}
            )
        except UnicodeDecodeError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "encoding"}
            )
        except OSError as e:
            from .error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "os_error"}
            )
        except Exception as e:
            from .error_handler import error_handler
            return error_handler.handle_tool_error(
                e,
                "file_operations",
                {"operation": operation, "path": path, "destination": destination, "encoding": encoding, "execution_time": time.time() - start_time}
            )

    # Приватные методы для валидации и выполнения

    def _validate_command_safety(self, command: str) -> Dict[str, Any]:
        """
        Проверяет безопасность команды.
        
        Args:
            command: Команда для проверки
            
        Returns:
            Dict: Результат проверки с полями 'safe' и 'reason'
        """
        try:
            cmd_parts = command.split()
            if not cmd_parts:
                return {"safe": False, "reason": "Пустая команда"}
            
            base_cmd = cmd_parts[0].lower()
            
            # Проверка на разрешённые команды
            if base_cmd not in self.allowed_commands:
                return {
                    "safe": False, 
                    "reason": f"Команда '{base_cmd}' не входит в белый список разрешённых команд"
                }
            
            # Дополнительные проверки для опасных команд
            if base_cmd in self.dangerous_commands:
                self.logger.warning(f"[SAFETY] Потенциально опасная команда: {command}")
                
                # Для rm/del проверяем, что не удаляются критические файлы
                if base_cmd in ["rm", "del", "rmdir"] and len(cmd_parts) > 1:
                    target = " ".join(cmd_parts[1:])
                    dangerous_patterns = ["*", "/", "\\", "C:", "D:", "system", "windows", "program"]
                    
                    for pattern in dangerous_patterns:
                        if pattern.lower() in target.lower():
                            return {
                                "safe": False,
                                "reason": f"Опасная операция удаления: '{target}' содержит запрещённый паттерн '{pattern}'"
                            }
            
            # Проверка на подозрительные паттерны
            suspicious_patterns = [
                "&&", "||", ";", "|", ">", ">>", "<", "$(", "`", 
                "curl", "wget", "nc", "netcat", "telnet", "ssh"
            ]
            
            for pattern in suspicious_patterns:
                if pattern in command:
                    return {
                        "safe": False,
                        "reason": f"Команда содержит подозрительный паттерн: '{pattern}'"
                    }
            
            return {"safe": True, "reason": "Команда прошла проверку безопасности"}
            
        except Exception as e:
            self.logger.error(f"[SAFETY] Ошибка проверки безопасности: {e}")
            return {"safe": False, "reason": f"Ошибка проверки безопасности: {str(e)}"}

    def _prepare_working_directory(self, working_directory: Optional[str]) -> str:
        """
        Подготавливает и валидирует рабочую директорию.
        
        Args:
            working_directory: Путь к рабочей директории
            
        Returns:
            str: Валидный путь к рабочей директории
        """
        try:
            if not working_directory:
                return os.getcwd()
            
            # Нормализация пути
            work_dir = os.path.normpath(working_directory)
            
            # Проверка безопасности пути
            if not self._validate_path_safety(work_dir):
                self.logger.warning(f"[WORKDIR] Небезопасная рабочая директория: {work_dir}")
                return os.getcwd()
            
            # Создание директории если не существует
            if not os.path.exists(work_dir):
                try:
                    os.makedirs(work_dir, exist_ok=True)
                    self.logger.info(f"[WORKDIR] Создана рабочая директория: {work_dir}")
                except Exception as e:
                    self.logger.error(f"[WORKDIR] Не удалось создать директорию {work_dir}: {e}")
                    return os.getcwd()
            
            return work_dir
            
        except Exception as e:
            self.logger.error(f"[WORKDIR] Ошибка подготовки рабочей директории: {e}")
            return os.getcwd()

    def _execute_command_safely(self, command: str, work_dir: str, timeout: int) -> str:
        """
        Безопасно выполняет команду с таймаутом.
        
        Args:
            command: Команда для выполнения
            work_dir: Рабочая директория
            timeout: Таймаут в секундах
            
        Returns:
            str: Результат выполнения команды
        """
        try:
            # Выполнение команды в зависимости от ОС
            if os.name == "nt":  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=work_dir,
                    encoding='utf-8',
                    errors='replace'
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=work_dir,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Обработка результата
            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            self.logger.info(f"[EXEC] Код возврата: {result.returncode}")
            
            if success:
                output = stdout if stdout else "Команда выполнена успешно (без вывода)"
                
                # Ограничение размера вывода
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + f"\n... [вывод обрезан, показано {self.max_output_size} символов]"
                
                self.logger.info(f"[EXEC] Успешное выполнение, вывод: {len(output)} символов")
                return output
            else:
                error_output = stderr if stderr else f"Команда завершилась с кодом {result.returncode}"
                
                # Ограничение размера ошибки
                if len(error_output) > self.max_output_size:
                    error_output = error_output[:self.max_output_size] + f"\n... [ошибка обрезана]"
                
                self.logger.error(f"[EXEC] Ошибка выполнения: {error_output}")
                return f"Ошибка выполнения команды:\n{error_output}"
                
        except subprocess.TimeoutExpired as e:
            # Исключение уже обрабатывается в вызывающем методе
            raise e
        except FileNotFoundError as e:
            # Команда не найдена
            raise FileNotFoundError(f"Команда '{command.split()[0]}' не найдена в системе")
        except PermissionError as e:
            # Недостаточно прав для выполнения
            raise PermissionError(f"Недостаточно прав для выполнения команды '{command}'")
        except Exception as e:
            # Прочие ошибки
            raise Exception(f"Критическая ошибка выполнения команды '{command}': {str(e)}")

    def _validate_url_safety(self, url: str) -> bool:
        """
        Проверяет безопасность URL.
        
        Args:
            url: URL для проверки
            
        Returns:
            bool: True если URL безопасен
        """
        try:
            # Базовая проверка формата URL
            if not url.startswith(('http://', 'https://')):
                self.logger.warning(f"[URL-SAFETY] Небезопасный протокол: {url}")
                return False
            
            # Парсинг URL
            parsed = urllib.parse.urlparse(url)
            
            # Проверка на подозрительные домены
            suspicious_domains = [
                'localhost', '127.0.0.1', '0.0.0.0', '::1',
                '192.168.', '10.', '172.16.', '172.17.', '172.18.',
                '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
                '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
                '172.29.', '172.30.', '172.31.'
            ]
            
            hostname = parsed.hostname or ""
            for suspicious in suspicious_domains:
                if suspicious in hostname.lower():
                    self.logger.warning(f"[URL-SAFETY] Подозрительный домен: {hostname}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"[URL-SAFETY] Ошибка проверки URL: {e}")
            return False

    def _fetch_web_content(
        self, 
        url: str, 
        selector: str, 
        extract_text: bool, 
        max_length: int
    ) -> str:
        """
        Извлекает контент веб-страницы.
        
        Args:
            url: URL страницы
            selector: CSS селектор
            extract_text: Извлекать только текст
            max_length: Максимальная длина контента
            
        Returns:
            str: Контент страницы
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Выполнение запроса
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Парсинг HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Удаление скриптов и стилей
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Извлечение контента
            if selector:
                # Извлечение по селектору
                elements = soup.select(selector)
                if elements:
                    content = '\n'.join([elem.get_text().strip() for elem in elements[:5]])
                else:
                    content = f"Элементы по селектору '{selector}' не найдены"
            else:
                # Извлечение всего текста
                if extract_text:
                    content = soup.get_text()
                else:
                    content = str(soup)
            
            # Очистка и форматирование
            if extract_text:
                lines = (line.strip() for line in content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
                content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Ограничение размера
            if len(content) > max_length:
                content = content[:max_length] + f"\n... [контент обрезан, показано {max_length} символов]"
            
            return f"Содержимое страницы {url}:\n\n{content}"
            
        except ImportError as e:
            # Исключение уже обрабатывается в вызывающем методе
            raise ImportError("Для работы с веб-страницами требуются библиотеки requests и beautifulsoup4")
        except requests.exceptions.ConnectionError as e:
            # Ошибка подключения
            raise ConnectionError(f"Не удалось подключиться к {url}: {str(e)}")
        except requests.exceptions.Timeout as e:
            # Таймаут
            raise TimeoutError(f"Превышено время ожидания при загрузке {url}")
        except requests.exceptions.HTTPError as e:
            # HTTP ошибка
            raise requests.exceptions.HTTPError(f"HTTP ошибка при загрузке {url}: {str(e)}")
        except requests.exceptions.RequestException as e:
            # Прочие ошибки requests
            raise requests.exceptions.RequestException(f"Ошибка запроса к {url}: {str(e)}")
        except Exception as e:
            # Прочие ошибки
            raise Exception(f"Ошибка обработки страницы {url}: {str(e)}")

    def _perform_web_search(self, query: str, num_results: int, search_engine: str) -> str:
        """
        Выполняет поиск в интернете.
        
        Args:
            query: Поисковый запрос
            num_results: Количество результатов
            search_engine: Поисковая система
            
        Returns:
            str: Результаты поиска
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Кодирование запроса
            encoded_query = urllib.parse.quote_plus(query)
            
            # Формирование URL поиска
            if search_engine.lower() in ['duckduckgo', 'ddg']:
                search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            else:
                # По умолчанию используем DuckDuckGo
                search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Выполнение поискового запроса
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Парсинг результатов
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Извлечение результатов поиска
            search_results = soup.find_all('div', class_='result')
            
            for i, result in enumerate(search_results[:num_results]):
                try:
                    title_elem = result.find('a', class_='result__a')
                    title = title_elem.get_text().strip() if title_elem else "Без названия"
                    link = title_elem.get('href') if title_elem else ""
                    
                    snippet_elem = result.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else "Описание недоступно"
                    
                    results.append(f"{i+1}. {title}\n   {snippet}\n   {link}")
                    
                except Exception as e:
                    self.logger.warning(f"[SEARCH] Ошибка обработки результата {i+1}: {e}")
                    continue
            
            if results:
                search_results_text = f"Результаты поиска для '{query}':\n\n" + "\n\n".join(results)
                self.logger.info(f"[SEARCH] Найдено {len(results)} результатов")
                return search_results_text
            else:
                return f"По запросу '{query}' результаты не найдены"
                
        except ImportError as e:
            # Исключение уже обрабатывается в вызывающем методе
            raise ImportError("Для поиска в интернете требуются библиотеки requests и beautifulsoup4")
        except requests.exceptions.ConnectionError as e:
            # Ошибка подключения
            raise ConnectionError(f"Не удалось подключиться к поисковой системе: {str(e)}")
        except requests.exceptions.Timeout as e:
            # Таймаут
            raise TimeoutError(f"Превышено время ожидания при выполнении поиска")
        except requests.exceptions.HTTPError as e:
            # HTTP ошибка
            raise requests.exceptions.HTTPError(f"HTTP ошибка при выполнении поиска: {str(e)}")
        except requests.exceptions.RequestException as e:
            # Прочие ошибки requests
            raise requests.exceptions.RequestException(f"Ошибка поискового запроса: {str(e)}")
        except Exception as e:
            # Прочие ошибки
            raise Exception(f"Ошибка обработки результатов поиска: {str(e)}")

    def _validate_path_safety(self, path: str) -> bool:
        """
        Проверяет безопасность файлового пути с улучшенными правилами.
        
        Args:
            path: Путь для проверки
            
        Returns:
            bool: True если путь безопасен
        """
        try:
            # Нормализация пути
            normalized_path = os.path.normpath(os.path.abspath(path))
            
            # Получаем текущую рабочую директорию
            current_dir = os.getcwd()
            
            # Разрешённые базовые директории
            allowed_base_dirs = [
                current_dir,  # Текущая рабочая директория
                os.path.expanduser("~/Documents"),  # Документы пользователя
                os.path.expanduser("~/Desktop"),    # Рабочий стол
                os.path.expanduser("~/Downloads"),  # Загрузки
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp"),  # Временные файлы
                os.environ.get("TEMP", ""),  # Системная временная директория
                os.environ.get("TMP", ""),   # Альтернативная временная директория
            ]
            
            # Добавляем пути из переменных окружения
            if "USERPROFILE" in os.environ:
                user_profile = os.environ["USERPROFILE"]
                allowed_base_dirs.extend([
                    os.path.join(user_profile, "AppData", "Local"),
                    os.path.join(user_profile, "AppData", "Roaming"),
                ])
            
            # Фильтруем пустые пути
            allowed_base_dirs = [d for d in allowed_base_dirs if d and os.path.exists(d)]
            
            # Проверяем, находится ли путь в разрешённых директориях
            path_is_allowed = False
            for allowed_dir in allowed_base_dirs:
                try:
                    # Проверяем, является ли путь поддиректорией разрешённой директории
                    if normalized_path.startswith(os.path.normpath(os.path.abspath(allowed_dir))):
                        path_is_allowed = True
                        break
                except:
                    continue
            
            if not path_is_allowed:
                self.logger.warning(f"[PATH-SAFETY] Путь не находится в разрешённых директориях: {normalized_path}")
                return False
            
            # Запрещённые паттерны в пути
            dangerous_patterns = [
                "..",  # Попытка выхода из директории
                "\\\\",  # UNC пути
                "//",    # Двойные слеши
                ":",     # Альтернативные потоки данных (Windows)
                "<",     # Недопустимые символы
                ">",
                "|",
                "?",
                "*",
                "\"",
            ]
            
            # Проверка на опасные паттерны
            for pattern in dangerous_patterns:
                if pattern in normalized_path:
                    self.logger.warning(f"[PATH-SAFETY] Обнаружен опасный паттерн '{pattern}' в пути: {normalized_path}")
                    return False
            
            # Запрещённые системные директории (абсолютные пути)
            forbidden_dirs = [
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\System Volume Information",
                "/etc",
                "/root",
                "/usr/bin",
                "/bin",
                "/sbin",
                "/var/log",
                "/dev",
                "/proc",
                "/sys"
            ]
            
            for forbidden_dir in forbidden_dirs:
                if normalized_path.startswith(forbidden_dir):
                    self.logger.warning(f"[PATH-SAFETY] Доступ к системной директории запрещён: {normalized_path}")
                    return False
            
            # Запрещённые имена файлов (Windows)
            forbidden_names = [
                "CON", "PRN", "AUX", "NUL",
                "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
            ]
            
            filename = os.path.basename(normalized_path).upper()
            if filename in forbidden_names or filename.split('.')[0] in forbidden_names:
                self.logger.warning(f"[PATH-SAFETY] Запрещённое имя файла: {filename}")
                return False
            
            # Проверка длины пути
            if len(normalized_path) > 260:  # Ограничение Windows
                self.logger.warning(f"[PATH-SAFETY] Путь слишком длинный ({len(normalized_path)} символов): {normalized_path}")
                return False
            
            self.logger.debug(f"[PATH-SAFETY] Путь прошёл проверку безопасности: {normalized_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"[PATH-SAFETY] Ошибка проверки безопасности пути: {e}")
            return False

    def _execute_file_operation(
        self, 
        operation: str, 
        path: str, 
        content: str, 
        destination: str, 
        encoding: str,
        max_file_size: int
    ) -> str:
        """
        Выполняет конкретную файловую операцию с улучшенной обработкой ошибок.
        
        Args:
            operation: Тип операции
            path: Путь к файлу/директории
            content: Содержимое для записи
            destination: Путь назначения
            encoding: Кодировка файла
            max_file_size: Максимальный размер файла
            
        Returns:
            str: Структурированный результат операции
        """
        try:
            if operation == "read":
                return self._read_file(path, encoding, max_file_size)
            elif operation == "write":
                return self._write_file(path, content, encoding)
            elif operation == "list_dir":
                return self._list_directory(path)
            elif operation == "exists":
                return self._check_exists(path)
            elif operation == "info":
                return self._get_file_info(path)
            elif operation == "copy":
                return self._copy_file(path, destination)
            elif operation == "move":
                return self._move_file(path, destination)
            elif operation == "delete":
                return self._delete_file(path)
            elif operation == "mkdir":
                return self._create_directory(path)
            else:
                available_ops = ["read", "write", "list_dir", "exists", "info", "copy", "move", "delete", "mkdir"]
                return self._format_error_response(
                    "INVALID_OPERATION",
                    f"Операция '{operation}' не поддерживается",
                    {
                        "operation": operation,
                        "available_operations": available_ops,
                        "path": path
                    }
                )
                
        except Exception as e:
            return self._format_error_response(
                "OPERATION_FAILED",
                f"Ошибка выполнения операции '{operation}': {str(e)}",
                {
                    "operation": operation,
                    "path": path,
                    "error_type": e.__class__.__name__
                }
            )

    def _read_file(self, path: str, encoding: str, max_file_size: int) -> str:
        """
        Читает содержимое файла с проверками безопасности и ограничениями размера.
        
        Args:
            path: Путь к файлу
            encoding: Кодировка файла
            max_file_size: Максимальный размер для чтения
            
        Returns:
            str: Структурированный ответ с содержимым файла
        """
        if not os.path.exists(path):
            return self._format_error_response(
                "FILE_NOT_FOUND",
                f"Файл '{path}' не существует",
                {"path": path, "operation": "read"}
            )
        
        if not os.path.isfile(path):
            return self._format_error_response(
                "NOT_A_FILE",
                f"'{path}' не является файлом",
                {"path": path, "operation": "read", "is_directory": os.path.isdir(path)}
            )
        
        try:
            # Проверка размера файла перед чтением
            file_size = os.path.getsize(path)
            if file_size > max_file_size * 2:  # Двойной лимит для предупреждения
                return self._format_error_response(
                    "FILE_TOO_LARGE",
                    f"Файл '{path}' слишком большой ({file_size} байт). Максимальный размер: {max_file_size * 2} байт",
                    {"path": path, "file_size": file_size, "max_size": max_file_size * 2}
                )
            
            with open(path, 'r', encoding=encoding) as f:
                file_content = f.read()
            
            # Ограничение размера содержимого
            was_truncated = False
            if len(file_content) > max_file_size:
                file_content = file_content[:max_file_size]
                was_truncated = True
            
            self.logger.info(f"[FILE-READ] Прочитан файл: {len(file_content)} символов")
            
            return self._format_success_response(
                "FILE_READ_SUCCESS",
                f"Файл '{path}' успешно прочитан",
                {
                    "path": path,
                    "content": file_content,
                    "file_size": file_size,
                    "content_length": len(file_content),
                    "encoding": encoding,
                    "was_truncated": was_truncated,
                    "truncated_at": max_file_size if was_truncated else None
                }
            )
            
        except UnicodeDecodeError as e:
            return self._format_error_response(
                "ENCODING_ERROR",
                f"Не удалось прочитать файл '{path}' с кодировкой {encoding}",
                {
                    "path": path,
                    "encoding": encoding,
                    "error_details": str(e),
                    "suggestion": "Попробуйте другую кодировку (cp1251, latin-1) или это может быть бинарный файл"
                }
            )
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для чтения файла '{path}'",
                {"path": path, "operation": "read"}
            )
        except Exception as e:
            return self._format_error_response(
                "READ_ERROR",
                f"Ошибка чтения файла '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _write_file(self, path: str, content: str, encoding: str) -> str:
        """
        Записывает содержимое в файл с проверками безопасности.
        
        Args:
            path: Путь к файлу
            content: Содержимое для записи
            encoding: Кодировка файла
            
        Returns:
            str: Структурированный ответ о результате записи
        """
        if content is None:
            content = ""  # Разрешаем создание пустых файлов
        
        try:
            # Проверка размера содержимого
            content_size = len(content.encode(encoding))
            max_write_size = self.max_file_size * 3  # Больший лимит для записи
            
            if content_size > max_write_size:
                return self._format_error_response(
                    "CONTENT_TOO_LARGE",
                    f"Содержимое слишком большое ({content_size} байт). Максимальный размер: {max_write_size} байт",
                    {"path": path, "content_size": content_size, "max_size": max_write_size}
                )
            
            # Создание директории если нужно
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"[FILE-WRITE] Создана директория: {dir_path}")
                except Exception as e:
                    return self._format_error_response(
                        "DIRECTORY_CREATION_FAILED",
                        f"Не удалось создать директорию '{dir_path}': {str(e)}",
                        {"path": path, "directory": dir_path}
                    )
            
            # Проверка существования файла для информации
            file_existed = os.path.exists(path)
            old_size = os.path.getsize(path) if file_existed else 0
            
            # Запись файла
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Проверка успешности записи
            new_size = os.path.getsize(path)
            
            self.logger.info(f"[FILE-WRITE] Записан файл: {len(content)} символов, {new_size} байт")
            
            return self._format_success_response(
                "FILE_WRITE_SUCCESS",
                f"Файл '{path}' успешно {'перезаписан' if file_existed else 'создан'}",
                {
                    "path": path,
                    "content_length": len(content),
                    "file_size_bytes": new_size,
                    "encoding": encoding,
                    "file_existed": file_existed,
                    "old_size": old_size if file_existed else None,
                    "operation": "overwrite" if file_existed else "create"
                }
            )
            
        except UnicodeEncodeError as e:
            return self._format_error_response(
                "ENCODING_ERROR",
                f"Не удалось закодировать содержимое в {encoding}",
                {
                    "path": path,
                    "encoding": encoding,
                    "error_details": str(e),
                    "suggestion": "Попробуйте другую кодировку или проверьте содержимое на специальные символы"
                }
            )
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для записи в файл '{path}'",
                {"path": path, "operation": "write"}
            )
        except OSError as e:
            return self._format_error_response(
                "WRITE_ERROR",
                f"Системная ошибка при записи файла '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )
        except Exception as e:
            return self._format_error_response(
                "WRITE_ERROR",
                f"Ошибка записи файла '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _list_directory(self, path: str) -> str:
        """
        Выводит структурированное содержимое директории.
        
        Args:
            path: Путь к директории
            
        Returns:
            str: Структурированный список содержимого директории
        """
        if not os.path.exists(path):
            return self._format_error_response(
                "DIRECTORY_NOT_FOUND",
                f"Директория '{path}' не существует",
                {"path": path, "operation": "list_dir"}
            )
        
        if not os.path.isdir(path):
            return self._format_error_response(
                "NOT_A_DIRECTORY",
                f"'{path}' не является директорией",
                {"path": path, "operation": "list_dir", "is_file": os.path.isfile(path)}
            )
        
        try:
            items = []
            directories = []
            files = []
            total_size = 0
            
            # Получение списка элементов
            dir_items = os.listdir(path)
            
            for item in dir_items:
                item_path = os.path.join(path, item)
                try:
                    stat_info = os.stat(item_path)
                    item_info = {
                        "name": item,
                        "path": item_path,
                        "size": stat_info.st_size,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "is_directory": os.path.isdir(item_path),
                        "is_file": os.path.isfile(item_path)
                    }
                    
                    if item_info["is_directory"]:
                        directories.append(item_info)
                    else:
                        files.append(item_info)
                        total_size += item_info["size"]
                    
                    items.append(item_info)
                    
                except (OSError, PermissionError) as e:
                    # Элемент недоступен, но продолжаем
                    items.append({
                        "name": item,
                        "path": item_path,
                        "error": f"Недоступен: {str(e)}",
                        "is_directory": None,
                        "is_file": None
                    })
            
            # Сортировка: сначала директории, потом файлы
            directories.sort(key=lambda x: x["name"].lower())
            files.sort(key=lambda x: x["name"].lower())
            
            # Ограничение количества элементов для отображения
            max_items = 100
            display_items = directories + files
            was_truncated = len(display_items) > max_items
            if was_truncated:
                display_items = display_items[:max_items]
            
            self.logger.info(f"[DIR-LIST] Список директории: {len(items)} элементов")
            
            return self._format_success_response(
                "DIRECTORY_LIST_SUCCESS",
                f"Содержимое директории '{path}' ({len(directories)} папок, {len(files)} файлов)",
                {
                    "path": path,
                    "total_items": len(items),
                    "directories_count": len(directories),
                    "files_count": len(files),
                    "total_size_bytes": total_size,
                    "items": display_items,
                    "was_truncated": was_truncated,
                    "truncated_at": max_items if was_truncated else None
                }
            )
                
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для чтения директории '{path}'",
                {"path": path, "operation": "list_dir"}
            )
        except Exception as e:
            return self._format_error_response(
                "LIST_ERROR",
                f"Ошибка чтения директории '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _check_exists(self, path: str) -> str:
        """Проверяет существование файла/директории."""
        exists = os.path.exists(path)
        self.logger.info(f"[EXISTS] Проверка существования: {path} = {exists}")
        
        if exists:
            return self._format_success_response(
                "PATH_EXISTS",
                f"Путь '{path}' существует",
                {
                    "path": path,
                    "exists": True,
                    "is_file": os.path.isfile(path),
                    "is_directory": os.path.isdir(path),
                    "operation": "exists"
                }
            )
        else:
            return self._format_success_response(
                "PATH_NOT_EXISTS",
                f"Путь '{path}' не существует",
                {
                    "path": path,
                    "exists": False,
                    "operation": "exists"
                }
            )

    def _get_file_info(self, path: str) -> str:
        """Получает подробную информацию о файле/директории."""
        if not os.path.exists(path):
            return self._format_error_response(
                "PATH_NOT_FOUND",
                f"Путь '{path}' не существует",
                {"path": path, "operation": "info"}
            )
        
        try:
            stat = os.stat(path)
            is_file = os.path.isfile(path)
            is_dir = os.path.isdir(path)
            
            info_data = {
                "path": path,
                "absolute_path": os.path.abspath(path),
                "name": os.path.basename(path),
                "parent_directory": os.path.dirname(path),
                "type": "file" if is_file else "directory" if is_dir else "other",
                "is_file": is_file,
                "is_directory": is_dir,
                "size_bytes": stat.st_size,
                "size_human": self._format_file_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "operation": "info"
            }
            
            # Дополнительная информация для директорий
            if is_dir:
                try:
                    items = os.listdir(path)
                    info_data.update({
                        "items_count": len(items),
                        "subdirectories": len([item for item in items if os.path.isdir(os.path.join(path, item))]),
                        "files": len([item for item in items if os.path.isfile(os.path.join(path, item))])
                    })
                except PermissionError:
                    info_data["items_count"] = "Недоступно (нет прав)"
            
            # Дополнительная информация для файлов
            if is_file:
                try:
                    # Попытка определить тип файла по расширению
                    _, ext = os.path.splitext(path)
                    info_data["extension"] = ext.lower() if ext else None
                    
                    # Попытка определить кодировку для текстовых файлов
                    if ext.lower() in ['.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml']:
                        try:
                            with open(path, 'rb') as f:
                                sample = f.read(1024)
                            try:
                                sample.decode('utf-8')
                                info_data["likely_encoding"] = "utf-8"
                            except UnicodeDecodeError:
                                try:
                                    sample.decode('cp1251')
                                    info_data["likely_encoding"] = "cp1251"
                                except UnicodeDecodeError:
                                    info_data["likely_encoding"] = "unknown"
                        except:
                            pass
                except:
                    pass
            
            self.logger.info(f"[FILE-INFO] Получена информация о: {path}")
            
            return self._format_success_response(
                "FILE_INFO_SUCCESS",
                f"Информация о {'файле' if is_file else 'директории'} '{path}'",
                info_data
            )
            
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для получения информации о '{path}'",
                {"path": path, "operation": "info"}
            )
        except Exception as e:
            return self._format_error_response(
                "INFO_ERROR",
                f"Ошибка получения информации о '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _format_file_size(self, size_bytes: int) -> str:
        """Форматирует размер файла в человекочитаемом виде."""
        if size_bytes == 0:
            return "0 байт"
        
        units = ['байт', 'КБ', 'МБ', 'ГБ', 'ТБ']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    def _copy_file(self, source: str, destination: str) -> str:
        """Копирует файл или директорию."""
        if not destination:
            return self._format_error_response(
                "MISSING_DESTINATION",
                "Не указан путь назначения для копирования",
                {"source": source, "operation": "copy"}
            )
        
        if not os.path.exists(source):
            return self._format_error_response(
                "SOURCE_NOT_FOUND",
                f"Источник '{source}' не существует",
                {"source": source, "destination": destination, "operation": "copy"}
            )
        
        try:
            source_is_file = os.path.isfile(source)
            source_is_dir = os.path.isdir(source)
            
            if not source_is_file and not source_is_dir:
                return self._format_error_response(
                    "INVALID_SOURCE_TYPE",
                    f"'{source}' не является файлом или директорией",
                    {"source": source, "destination": destination, "operation": "copy"}
                )
            
            # Проверка, не существует ли уже файл назначения
            dest_exists = os.path.exists(destination)
            
            if source_is_file:
                # Если назначение - директория, копируем файл в неё
                if os.path.isdir(destination):
                    destination = os.path.join(destination, os.path.basename(source))
                
                shutil.copy2(source, destination)
                operation_type = "file_copy"
                self.logger.info(f"[COPY] Скопирован файл: {source} -> {destination}")
                
            elif source_is_dir:
                if dest_exists:
                    return self._format_error_response(
                        "DESTINATION_EXISTS",
                        f"Директория назначения '{destination}' уже существует",
                        {"source": source, "destination": destination, "operation": "copy"}
                    )
                
                shutil.copytree(source, destination)
                operation_type = "directory_copy"
                self.logger.info(f"[COPY] Скопирована директория: {source} -> {destination}")
            
            # Получаем информацию о результате
            dest_size = os.path.getsize(destination) if os.path.isfile(destination) else self._get_directory_size(destination)
            
            return self._format_success_response(
                "COPY_SUCCESS",
                f"{'Файл' if source_is_file else 'Директория'} '{source}' успешно скопирован{'а' if source_is_dir else ''} в '{destination}'",
                {
                    "source": source,
                    "destination": destination,
                    "operation": "copy",
                    "operation_type": operation_type,
                    "source_was_file": source_is_file,
                    "source_was_directory": source_is_dir,
                    "destination_existed": dest_exists,
                    "destination_size": dest_size
                }
            )
                
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для копирования '{source}' в '{destination}'",
                {"source": source, "destination": destination, "operation": "copy"}
            )
        except shutil.SameFileError as e:
            return self._format_error_response(
                "SAME_FILE_ERROR",
                f"Источник и назначение указывают на один и тот же файл",
                {"source": source, "destination": destination, "operation": "copy"}
            )
        except Exception as e:
            return self._format_error_response(
                "COPY_ERROR",
                f"Ошибка копирования '{source}' в '{destination}': {str(e)}",
                {"source": source, "destination": destination, "error_type": e.__class__.__name__}
            )

    def _move_file(self, source: str, destination: str) -> str:
        """Перемещает файл или директорию."""
        if not destination:
            return self._format_error_response(
                "MISSING_DESTINATION",
                "Не указан путь назначения для перемещения",
                {"source": source, "operation": "move"}
            )
        
        if not os.path.exists(source):
            return self._format_error_response(
                "SOURCE_NOT_FOUND",
                f"Источник '{source}' не существует",
                {"source": source, "destination": destination, "operation": "move"}
            )
        
        try:
            source_is_file = os.path.isfile(source)
            source_is_dir = os.path.isdir(source)
            source_size = os.path.getsize(source) if source_is_file else self._get_directory_size(source)
            
            # Если назначение - существующая директория, перемещаем в неё
            if os.path.isdir(destination):
                destination = os.path.join(destination, os.path.basename(source))
            
            shutil.move(source, destination)
            self.logger.info(f"[MOVE] Перемещён: {source} -> {destination}")
            
            return self._format_success_response(
                "MOVE_SUCCESS",
                f"{'Файл' if source_is_file else 'Директория'} '{source}' успешно перемещён{'а' if source_is_dir else ''} в '{destination}'",
                {
                    "source": source,
                    "destination": destination,
                    "operation": "move",
                    "source_was_file": source_is_file,
                    "source_was_directory": source_is_dir,
                    "size": source_size
                }
            )
            
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для перемещения '{source}' в '{destination}'",
                {"source": source, "destination": destination, "operation": "move"}
            )
        except shutil.Error as e:
            return self._format_error_response(
                "MOVE_ERROR",
                f"Ошибка перемещения '{source}' в '{destination}': {str(e)}",
                {"source": source, "destination": destination, "error_type": e.__class__.__name__}
            )
        except Exception as e:
            return self._format_error_response(
                "MOVE_ERROR",
                f"Ошибка перемещения '{source}' в '{destination}': {str(e)}",
                {"source": source, "destination": destination, "error_type": e.__class__.__name__}
            )

    def _delete_file(self, path: str) -> str:
        """Удаляет файл или директорию с дополнительными проверками безопасности."""
        if not os.path.exists(path):
            return self._format_error_response(
                "PATH_NOT_FOUND",
                f"Путь '{path}' не существует",
                {"path": path, "operation": "delete"}
            )
        
        try:
            is_file = os.path.isfile(path)
            is_dir = os.path.isdir(path)
            
            if not is_file and not is_dir:
                return self._format_error_response(
                    "INVALID_PATH_TYPE",
                    f"'{path}' не является файлом или директорией",
                    {"path": path, "operation": "delete"}
                )
            
            # Получаем информацию перед удалением
            size_before = os.path.getsize(path) if is_file else self._get_directory_size(path)
            items_count = None
            
            if is_dir:
                try:
                    items_count = len(os.listdir(path))
                    # Дополнительная проверка для непустых директорий
                    if items_count > 0:
                        self.logger.warning(f"[DELETE] Удаление непустой директории: {path} ({items_count} элементов)")
                except:
                    items_count = "unknown"
            
            # Выполнение удаления
            if is_file:
                os.remove(path)
                operation_type = "file_delete"
                self.logger.info(f"[DELETE] Удалён файл: {path}")
            else:
                shutil.rmtree(path)
                operation_type = "directory_delete"
                self.logger.info(f"[DELETE] Удалена директория: {path}")
            
            return self._format_success_response(
                "DELETE_SUCCESS",
                f"{'Файл' if is_file else 'Директория'} '{path}' успешно удален{'а' if is_dir else ''}",
                {
                    "path": path,
                    "operation": "delete",
                    "operation_type": operation_type,
                    "was_file": is_file,
                    "was_directory": is_dir,
                    "size_bytes": size_before,
                    "items_count": items_count
                }
            )
                
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для удаления '{path}'",
                {"path": path, "operation": "delete"}
            )
        except OSError as e:
            return self._format_error_response(
                "DELETE_ERROR",
                f"Системная ошибка при удалении '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )
        except Exception as e:
            return self._format_error_response(
                "DELETE_ERROR",
                f"Ошибка удаления '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _get_directory_size(self, path: str) -> int:
        """Вычисляет общий размер директории."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        # Файл может быть удалён или недоступен
                        continue
        except (OSError, PermissionError):
            # Если не можем получить размер, возвращаем 0
            pass
        return total_size

    def _create_directory(self, path: str) -> str:
        """Создаёт директорию."""
        try:
            existed = os.path.exists(path)
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"[MKDIR] Создана директория: {path}")
            
            return self._format_success_response(
                "DIRECTORY_CREATE_SUCCESS",
                f"Директория '{path}' {'уже существовала' if existed else 'успешно создана'}",
                {
                    "path": path,
                    "operation": "mkdir",
                    "already_existed": existed
                }
            )
            
        except PermissionError as e:
            return self._format_error_response(
                "PERMISSION_DENIED",
                f"Недостаточно прав для создания директории '{path}'",
                {"path": path, "operation": "mkdir"}
            )
        except Exception as e:
            return self._format_error_response(
                "MKDIR_ERROR",
                f"Ошибка создания директории '{path}': {str(e)}",
                {"path": path, "error_type": e.__class__.__name__}
            )

    def _format_success_response(self, status_code: str, message: str, data: Dict[str, Any]) -> str:
        """
        Форматирует успешный ответ в структурированном виде.
        
        Args:
            status_code: Код статуса операции
            message: Сообщение о результате
            data: Данные результата
            
        Returns:
            str: Форматированный ответ
        """
        response = {
            "status": "success",
            "status_code": status_code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Для удобочитаемости возвращаем и JSON и текстовое представление
        json_response = json.dumps(response, ensure_ascii=False, indent=2)
        
        # Создаём читаемое представление
        readable_parts = [f"✅ {message}"]
        
        if "content" in data:
            readable_parts.append(f"\nСодержимое:\n{data['content']}")
        elif "items" in data:
            readable_parts.append(f"\nЭлементы:")
            for item in data["items"][:10]:  # Показываем первые 10 элементов
                if item.get("is_directory"):
                    readable_parts.append(f"  📁 {item['name']}/")
                elif item.get("is_file"):
                    size_str = f" ({item['size']} байт)" if "size" in item else ""
                    readable_parts.append(f"  📄 {item['name']}{size_str}")
                else:
                    readable_parts.append(f"  ❓ {item['name']}")
            
            if len(data["items"]) > 10:
                readable_parts.append(f"  ... и ещё {len(data['items']) - 10} элементов")
        
        readable_response = "\n".join(readable_parts)
        
        return f"{readable_response}\n\n[Структурированные данные]\n{json_response}"

    def _format_error_response(self, error_code: str, message: str, context: Dict[str, Any]) -> str:
        """
        Форматирует ответ об ошибке в структурированном виде.
        
        Args:
            error_code: Код ошибки
            message: Сообщение об ошибке
            context: Контекст ошибки
            
        Returns:
            str: Форматированный ответ об ошибке
        """
        response = {
            "status": "error",
            "error_code": error_code,
            "message": message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        json_response = json.dumps(response, ensure_ascii=False, indent=2)
        
        # Создаём читаемое представление ошибки
        readable_response = f"❌ {message}"
        
        # Добавляем полезные подсказки
        if error_code == "FILE_NOT_FOUND":
            readable_response += "\n💡 Проверьте правильность пути к файлу"
        elif error_code == "PERMISSION_DENIED":
            readable_response += "\n💡 Проверьте права доступа к файлу или директории"
        elif error_code == "ENCODING_ERROR":
            readable_response += "\n💡 Попробуйте другую кодировку (utf-8, cp1251, latin-1)"
        elif error_code == "FILE_TOO_LARGE":
            readable_response += "\n💡 Попробуйте обработать файл частями или увеличить лимит"
        
        return f"{readable_response}\n\n[Детали ошибки]\n{json_response}"


# Пример использования и тестирования
if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создание экземпляра CommandExecutor
    executor = CommandExecutor()
    
    print("=== Тестирование CommandExecutor ===")
    
    # Тест выполнения команды терминала
    print("\n1. Тест выполнения команды терминала:")
    result = executor.execute_terminal_command("ls -la" if os.name != "nt" else "dir")
    print(f"Результат: {result[:200]}...")
    
    # Тест файловых операций
    print("\n2. Тест файловых операций:")
    test_file = "test_command_executor.txt"
    test_content = "Тестовое содержимое файла\nВторая строка"
    
    # Запись файла
    write_result = executor.file_operations("write", test_file, test_content)
    print(f"Запись файла: {write_result}")
    
    # Чтение файла
    read_result = executor.file_operations("read", test_file)
    print(f"Чтение файла: {read_result[:100]}...")
    
    # Проверка существования
    exists_result = executor.file_operations("exists", test_file)
    print(f"Проверка существования: {exists_result}")
    
    # Удаление тестового файла
    try:
        os.remove(test_file)
        print("Тестовый файл удалён")
    except:
        pass
    
    # Тест веб-поиска (если доступны библиотеки)
    print("\n3. Тест веб-поиска:")
    try:
        search_result = executor.web_search("Python programming", 3)
        print(f"Результат поиска: {search_result[:200]}...")
    except Exception as e:
        print(f"Поиск недоступен: {e}")
    
    print("\n=== Тестирование завершено ===")