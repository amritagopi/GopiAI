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
                from error_handler import error_handler
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
                from error_handler import error_handler
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
        encoding: str = "utf-8"
    ) -> str:
        """
        Выполняет операции с файловой системой.
        
        Args:
            operation: Тип операции (read, write, list, exists, info, copy, move, delete)
            path: Путь к файлу/директории
            content: Содержимое для записи
            destination: Путь назначения для копирования/перемещения
            encoding: Кодировка файла
            
        Returns:
            str: Результат операции или сообщение об ошибке
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
            path = path.strip()
            
            self.logger.info(f"[FILE-OPS] Операция: '{operation}', путь: '{path}'")
            
            # Проверка безопасности пути
            if not self._validate_path_safety(path):
                from error_handler import error_handler
                return error_handler.handle_command_safety_error(
                    f"file_operations {operation} {path}",
                    f"Небезопасный путь '{path}'",
                    {"operation": operation, "path": path, "destination": destination}
                )
            
            # Выполнение операции
            result = self._execute_file_operation(operation, path, content, destination, encoding)
            
            execution_time = time.time() - start_time
            self.logger.info(f"[FILE-OPS] Операция выполнена за {execution_time:.2f}с")
            
            return result
            
        except FileNotFoundError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding}
            )
        except PermissionError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "permission"}
            )
        except IsADirectoryError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "is_directory"}
            )
        except NotADirectoryError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "not_directory"}
            )
        except UnicodeDecodeError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "encoding"}
            )
        except OSError as e:
            from error_handler import error_handler
            return error_handler.handle_file_operation_error(
                e,
                operation,
                path,
                {"destination": destination, "encoding": encoding, "error_type": "os_error"}
            )
        except Exception as e:
            from error_handler import error_handler
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
        Проверяет безопасность файлового пути.
        
        Args:
            path: Путь для проверки
            
        Returns:
            bool: True если путь безопасен
        """
        try:
            # Нормализация пути
            normalized_path = os.path.normpath(path)
            
            # Запрещённые паттерны (исключаем временные директории)
            dangerous_patterns = [
                "..", "/etc/", "/root/", "/home/", "/usr/bin/", "/bin/", "/sbin/",
                "/var/", "/dev/", "/proc/", "/sys/",
                "C:\\Windows\\", "C:\\Program Files\\",
                # Исключаем C:\\Users\\ для временных директорий, но проверяем конкретные системные папки
                "C:\\Users\\Public\\", "C:\\Users\\Default\\", "C:\\Users\\All Users\\",
            ]
            
            # Дополнительная проверка для системных директорий в C:\Users\
            if "C:\\Users\\" in normalized_path:
                # Разрешаем только временные директории и AppData
                if not any(allowed in normalized_path for allowed in ["\\AppData\\", "\\Temp\\", "temp"]):
                    # Проверяем, что это не системная папка пользователя
                    system_user_dirs = ["\\Desktop\\", "\\Documents\\", "\\Downloads\\", "\\Pictures\\", "\\Music\\", "\\Videos\\"]
                    if any(sys_dir in normalized_path for sys_dir in system_user_dirs):
                        self.logger.warning(f"[PATH-SAFETY] Доступ к системной папке пользователя запрещён: {normalized_path}")
                        return False
            
            # Проверка на опасные паттерны
            for pattern in dangerous_patterns:
                if pattern in normalized_path:
                    self.logger.warning(f"[PATH-SAFETY] Обнаружен опасный паттерн '{pattern}' в пути: {normalized_path}")
                    return False
            
            # Проверка на абсолютные пути к системным директориям
            if os.path.isabs(normalized_path):
                system_dirs = ['/etc', '/root', '/usr', '/bin', '/sbin', '/var', '/tmp', '/dev', '/proc', '/sys']
                for sys_dir in system_dirs:
                    if normalized_path.startswith(sys_dir):
                        self.logger.warning(f"[PATH-SAFETY] Доступ к системной директории запрещён: {normalized_path}")
                        return False
            
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
        encoding: str
    ) -> str:
        """
        Выполняет конкретную файловую операцию.
        
        Args:
            operation: Тип операции
            path: Путь к файлу/директории
            content: Содержимое для записи
            destination: Путь назначения
            encoding: Кодировка файла
            
        Returns:
            str: Результат операции
        """
        try:
            if operation == "read":
                return self._read_file(path, encoding)
            elif operation == "write":
                return self._write_file(path, content, encoding)
            elif operation == "list":
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
                return f"Операция '{operation}' не поддерживается. Доступные операции: read, write, list, exists, info, copy, move, delete, mkdir"
                
        except Exception as e:
            return f"Ошибка выполнения операции '{operation}': {str(e)}"

    def _read_file(self, path: str, encoding: str) -> str:
        """Читает содержимое файла."""
        if not os.path.exists(path):
            return f"Ошибка: файл '{path}' не существует"
        
        if not os.path.isfile(path):
            return f"Ошибка: '{path}' не является файлом"
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                file_content = f.read()
            
            # Ограничение размера
            if len(file_content) > self.max_file_size:
                file_content = file_content[:self.max_file_size] + f"\n... [файл обрезан, показано {self.max_file_size} символов]"
            
            self.logger.info(f"[FILE-READ] Прочитан файл: {len(file_content)} символов")
            return f"Содержимое файла '{path}':\n\n{file_content}"
            
        except UnicodeDecodeError:
            return f"Ошибка: не удалось прочитать файл '{path}' с кодировкой {encoding} (возможно, это бинарный файл)"
        except Exception as e:
            return f"Ошибка чтения файла '{path}': {str(e)}"

    def _write_file(self, path: str, content: str, encoding: str) -> str:
        """Записывает содержимое в файл."""
        if not content:
            return "Ошибка: не указано содержимое для записи"
        
        try:
            # Создание директории если нужно
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.info(f"[FILE-WRITE] Записан файл: {len(content)} символов")
            return f"Файл '{path}' успешно записан ({len(content)} символов)"
            
        except Exception as e:
            return f"Ошибка записи файла '{path}': {str(e)}"

    def _list_directory(self, path: str) -> str:
        """Выводит содержимое директории."""
        if not os.path.exists(path):
            return f"Ошибка: директория '{path}' не существует"
        
        if not os.path.isdir(path):
            return f"Ошибка: '{path}' не является директорией"
        
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    try:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({size} байт)")
                    except:
                        items.append(f"📄 {item}")
            
            if items:
                items_text = "\n".join(items[:50])  # Максимум 50 элементов
                if len(os.listdir(path)) > 50:
                    items_text += f"\n... и ещё {len(os.listdir(path)) - 50} элементов"
                
                self.logger.info(f"[DIR-LIST] Список директории: {len(items)} элементов")
                return f"Содержимое директории '{path}':\n\n{items_text}"
            else:
                return f"Директория '{path}' пуста"
                
        except Exception as e:
            return f"Ошибка чтения директории '{path}': {str(e)}"

    def _check_exists(self, path: str) -> str:
        """Проверяет существование файла/директории."""
        exists = os.path.exists(path)
        self.logger.info(f"[EXISTS] Проверка существования: {path} = {exists}")
        return f"Путь '{path}' {'существует' if exists else 'не существует'}"

    def _get_file_info(self, path: str) -> str:
        """Получает информацию о файле/директории."""
        if not os.path.exists(path):
            return f"Ошибка: путь '{path}' не существует"
        
        try:
            stat = os.stat(path)
            is_file = os.path.isfile(path)
            is_dir = os.path.isdir(path)
            
            info_lines = [
                f"Путь: {path}",
                f"Тип: {'файл' if is_file else 'директория' if is_dir else 'другое'}",
                f"Размер: {stat.st_size} байт",
                f"Последнее изменение: {time.ctime(stat.st_mtime)}",
            ]
            
            if is_dir:
                try:
                    items_count = len(os.listdir(path))
                    info_lines.append(f"Элементов в директории: {items_count}")
                except:
                    pass
            
            self.logger.info(f"[FILE-INFO] Получена информация о: {path}")
            return "\n".join(info_lines)
            
        except Exception as e:
            return f"Ошибка получения информации о '{path}': {str(e)}"

    def _copy_file(self, source: str, destination: str) -> str:
        """Копирует файл или директорию."""
        if not destination:
            return "Ошибка: не указан путь назначения для копирования"
        
        if not self._validate_path_safety(destination):
            return f"Ошибка: небезопасный путь назначения '{destination}'"
        
        if not os.path.exists(source):
            return f"Ошибка: источник '{source}' не существует"
        
        try:
            if os.path.isfile(source):
                shutil.copy2(source, destination)
                self.logger.info(f"[COPY] Скопирован файл: {source} -> {destination}")
                return f"Файл '{source}' успешно скопирован в '{destination}'"
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                self.logger.info(f"[COPY] Скопирована директория: {source} -> {destination}")
                return f"Директория '{source}' успешно скопирована в '{destination}'"
            else:
                return f"Ошибка: '{source}' не является файлом или директорией"
                
        except Exception as e:
            return f"Ошибка копирования '{source}' в '{destination}': {str(e)}"

    def _move_file(self, source: str, destination: str) -> str:
        """Перемещает файл или директорию."""
        if not destination:
            return "Ошибка: не указан путь назначения для перемещения"
        
        if not self._validate_path_safety(destination):
            return f"Ошибка: небезопасный путь назначения '{destination}'"
        
        if not os.path.exists(source):
            return f"Ошибка: источник '{source}' не существует"
        
        try:
            shutil.move(source, destination)
            self.logger.info(f"[MOVE] Перемещён: {source} -> {destination}")
            return f"'{source}' успешно перемещён в '{destination}'"
            
        except Exception as e:
            return f"Ошибка перемещения '{source}' в '{destination}': {str(e)}"

    def _delete_file(self, path: str) -> str:
        """Удаляет файл или директорию."""
        if not os.path.exists(path):
            return f"Ошибка: путь '{path}' не существует"
        
        try:
            if os.path.isfile(path):
                os.remove(path)
                self.logger.info(f"[DELETE] Удалён файл: {path}")
                return f"Файл '{path}' успешно удалён"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                self.logger.info(f"[DELETE] Удалена директория: {path}")
                return f"Директория '{path}' успешно удалена"
            else:
                return f"Ошибка: '{path}' не является файлом или директорией"
                
        except Exception as e:
            return f"Ошибка удаления '{path}': {str(e)}"

    def _create_directory(self, path: str) -> str:
        """Создаёт директорию."""
        try:
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"[MKDIR] Создана директория: {path}")
            return f"Директория '{path}' успешно создана"
            
        except Exception as e:
            return f"Ошибка создания директории '{path}': {str(e)}"


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