"""
Модуль для выполнения команд, полученных от Gemini AI.
Парсит JSON-ответы и выполняет команды терминала.
"""

import json
import subprocess
import os
import logging
import time
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Класс для безопасного выполнения команд из ответов Gemini"""

    def __init__(self):
        self.logger = logger

        # Разрешенные команды для безопасности
        self.allowed_commands = {
            "mkdir",
            "dir",
            "ls",
            "pwd",
            "cd",
            "echo",
            "type",
            "cat",
            "tree",
            "find",
            "grep",
            "copy",
            "cp",
            "move",
            "mv",
            "del",
            "rm",
            "rmdir",
            "touch",
            "whoami",
            "date",
            "time",
        }

        # Опасные команды, которые требуют особого внимания
        self.dangerous_commands = {
            "rm",
            "del",
            "rmdir",
            "format",
            "fdisk",
            "shutdown",
            "reboot",
        }

    def execute_command(self, command_data: Dict) -> Dict:
        """
        Выполняет одну команду

        Args:
            command_data: Словарь с данными команды

        Returns:
            Результат выполнения команды
        """
        try:
            tool = command_data.get("tool", "").lower()
            params = command_data.get("params", {})

            if tool == "terminal":
                return self._execute_terminal_command(params.get("command", ""))
            else:
                return {
                    "success": False,
                    "error": f"Неподдерживаемый инструмент: {tool}",
                    "output": "",
                }

        except Exception as e:
            self.logger.error(f"[EXECUTOR] Ошибка выполнения команды: {e}")
            return {"success": False, "error": str(e), "output": ""}

    def _execute_terminal_command(self, command: str) -> Dict:
        """Выполняет команду терминала"""
        if not command or not command.strip():
            return {"success": False, "error": "Пустая команда", "output": ""}

        command = command.strip()
        self.logger.info(f"[EXECUTOR] Выполняем команду: {command}")

        # Проверяем безопасность команды
        cmd_parts = command.split()
        if not cmd_parts:
            return {"success": False, "error": "Некорректная команда", "output": ""}

        base_cmd = cmd_parts[0].lower()

        # Проверяем, разрешена ли команда
        if base_cmd not in self.allowed_commands:
            self.logger.warning(f"[EXECUTOR] Команда не разрешена: {base_cmd}")
            return {
                "success": False,
                "error": f'Команда "{base_cmd}" не разрешена для выполнения',
                "output": "",
            }

        # Предупреждение для опасных команд
        if base_cmd in self.dangerous_commands:
            self.logger.warning(
                f"[EXECUTOR] Выполняется потенциально опасная команда: {command}"
            )

        try:
            # Выполняем команду
            if os.name == "nt":  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd(),
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd(),
                )

            success = result.returncode == 0
            output = result.stdout if success else result.stderr

            self.logger.info(
                f"[EXECUTOR] Команда выполнена. Код возврата: {result.returncode}"
            )
            self.logger.info(f"[EXECUTOR] Вывод: {output[:200]}...")

            return {
                "success": success,
                "error": result.stderr if not success else "",
                "output": output,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            error_msg = (
                f"Команда '{command}' превысила лимит времени выполнения (30 сек)"
            )
            self.logger.error(f"[EXECUTOR] {error_msg}")
            return {"success": False, "error": error_msg, "output": ""}
        except Exception as e:
            error_msg = f"Ошибка выполнения команды '{command}': {str(e)}"
            self.logger.error(f"[EXECUTOR] {error_msg}")
            return {"success": False, "error": error_msg, "output": ""}

    def execute_terminal_command(
        self, command: str, working_directory: str = ".", timeout: int = 30
    ) -> str:
        """
        Выполняет команду терминала с поддержкой Tool Calling

        Args:
            command: Команда для выполнения
            working_directory: Рабочая директория
            timeout: Таймаут выполнения в секундах

        Returns:
            str: Результат выполнения команды
        """
        if not command or not command.strip():
            return "Ошибка: пустая команда"

        command = command.strip()
        self.logger.info(f"[TOOL-EXEC] Выполняем терминальную команду: {command}")
        self.logger.info(f"[TOOL-EXEC] Рабочая директория: {working_directory}")
        self.logger.info(f"[TOOL-EXEC] Таймаут: {timeout} сек")

        # Проверяем безопасность команды
        cmd_parts = command.split()
        if not cmd_parts:
            return "Ошибка: некорректная команда"

        base_cmd = cmd_parts[0].lower()

        # Расширенный список разрешенных команд для Tool Calling
        extended_allowed_commands = self.allowed_commands.union(
            {
                "python",
                "pip",
                "git",
                "node",
                "npm",
                "yarn",
                "docker",
                "curl",
                "wget",
                "ping",
                "netstat",
                "ps",
                "top",
                "htop",
                "which",
                "where",
                "head",
                "tail",
                "wc",
                "sort",
                "uniq",
                "chmod",
                "chown",
                "stat",
                "file",
                "du",
                "df",
                "free",
                "uname",
                "hostname",
                "uptime",
                "history",
                "env",
                "printenv",
            }
        )

        # Проверяем, разрешена ли команда
        if base_cmd not in extended_allowed_commands:
            self.logger.warning(f"[TOOL-EXEC] Команда не разрешена: {base_cmd}")
            return f"Ошибка: команда '{base_cmd}' не разрешена для выполнения по соображениям безопасности"

        # Предупреждение для опасных команд
        if base_cmd in self.dangerous_commands:
            self.logger.warning(
                f"[TOOL-EXEC] Выполняется потенциально опасная команда: {command}"
            )

        try:
            # Проверяем и создаём рабочую директорию если нужно
            if working_directory != "." and not os.path.exists(working_directory):
                try:
                    os.makedirs(working_directory, exist_ok=True)
                    self.logger.info(
                        f"[TOOL-EXEC] Создана рабочая директория: {working_directory}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"[TOOL-EXEC] Не удалось создать рабочую директорию: {e}"
                    )
                    working_directory = "."

            # Выполняем команду
            if os.name == "nt":  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=working_directory,
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=working_directory,
                )

            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

            self.logger.info(
                f"[TOOL-EXEC] Команда выполнена. Код возврата: {result.returncode}"
            )

            # Формируем результат
            if success:
                output = stdout if stdout else "Команда выполнена успешно (без вывода)"
                self.logger.info(f"[TOOL-EXEC] Успешный вывод: {output[:200]}...")
                return output
            else:
                error_output = (
                    stderr
                    if stderr
                    else f"Команда завершилась с кодом {result.returncode}"
                )
                self.logger.error(f"[TOOL-EXEC] Ошибка выполнения: {error_output}")
                return f"Ошибка выполнения команды: {error_output}"

        except subprocess.TimeoutExpired:
            error_msg = f"Команда '{command}' превысила лимит времени выполнения ({timeout} сек)"
            self.logger.error(f"[TOOL-EXEC] {error_msg}")
            return f"Ошибка: {error_msg}"
        except Exception as e:
            error_msg = f"Критическая ошибка выполнения команды '{command}': {str(e)}"
            self.logger.error(f"[TOOL-EXEC] {error_msg}")
            return f"Ошибка: {error_msg}"

    def browse_website(
        self,
        url: str,
        action: str = "navigate",
        selector: str = "",
        text: str = "",
        browser_type: str = "auto",
        headless: bool = True,
        wait_seconds: int = 3,
    ) -> str:
        """
        Открывает веб-страницу и выполняет действия с ней

        Args:
            url: URL для открытия
            action: Действие для выполнения
            selector: CSS селектор для взаимодействия
            text: Текст для ввода
            browser_type: Тип браузера
            headless: Режим без GUI
            wait_seconds: Время ожидания

        Returns:
            str: Результат выполнения
        """
        try:
            self.logger.info(f"[TOOL-EXEC] Открываем веб-страницу: {url}")
            self.logger.info(f"[TOOL-EXEC] Действие: {action}")

            # Простая реализация через requests для базовой функциональности
            if action == "navigate" or action == "extract":
                try:
                    import requests
                    from bs4 import BeautifulSoup

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }

                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()

                    if action == "navigate":
                        # Извлекаем основной контент
                        soup = BeautifulSoup(response.content, "html.parser")

                        # Удаляем скрипты и стили
                        for script in soup(["script", "style"]):
                            script.decompose()

                        # Извлекаем текст
                        text_content = soup.get_text()

                        # Очищаем и ограничиваем размер
                        lines = (line.strip() for line in text_content.splitlines())
                        chunks = (
                            phrase.strip()
                            for line in lines
                            for phrase in line.split("  ")
                        )
                        text_content = " ".join(chunk for chunk in chunks if chunk)

                        # Ограничиваем размер до 2000 символов
                        if len(text_content) > 2000:
                            text_content = text_content[:2000] + "... [контент обрезан]"

                        self.logger.info(
                            f"[TOOL-EXEC] Извлечён контент страницы: {len(text_content)} символов"
                        )
                        return f"Содержимое страницы {url}:\n\n{text_content}"

                    elif action == "extract" and selector:
                        # Извлекаем контент по селектору
                        soup = BeautifulSoup(response.content, "html.parser")
                        elements = soup.select(selector)

                        if elements:
                            extracted_text = "\n".join(
                                [elem.get_text().strip() for elem in elements[:5]]
                            )  # Максимум 5 элементов
                            self.logger.info(
                                f"[TOOL-EXEC] Извлечено {len(elements)} элементов по селектору {selector}"
                            )
                            return f"Извлечённые элементы по селектору '{selector}':\n\n{extracted_text}"
                        else:
                            return f"Элементы по селектору '{selector}' не найдены на странице {url}"

                except ImportError:
                    return "Ошибка: для работы с веб-страницами требуются библиотеки requests и beautifulsoup4"
                except requests.RequestException as e:
                    return f"Ошибка загрузки страницы {url}: {str(e)}"
                except Exception as e:
                    return f"Ошибка обработки страницы {url}: {str(e)}"

            else:
                return f"Действие '{action}' пока не поддерживается. Доступные действия: navigate, extract"

        except Exception as e:
            error_msg = f"Критическая ошибка при работе с веб-страницей: {str(e)}"
            self.logger.error(f"[TOOL-EXEC] {error_msg}")
            return f"Ошибка: {error_msg}"

    def web_search(
        self,
        query: str,
        search_engine: str = "google",
        num_results: int = 5,
        search_type: str = "quick_search",
    ) -> str:
        """
        Выполняет поиск в интернете

        Args:
            query: Поисковый запрос
            search_engine: Поисковая система
            num_results: Количество результатов
            search_type: Тип поиска

        Returns:
            str: Результаты поиска
        """
        try:
            self.logger.info(f"[TOOL-EXEC] Выполняем поиск: '{query}'")
            self.logger.info(f"[TOOL-EXEC] Поисковая система: {search_engine}")
            self.logger.info(f"[TOOL-EXEC] Количество результатов: {num_results}")

            # Простая реализация через DuckDuckGo (не требует API ключа)
            try:
                import requests
                from bs4 import BeautifulSoup
                import urllib.parse

                # Формируем URL для поиска
                if (
                    search_engine.lower() == "duckduckgo"
                    or search_engine.lower() == "google"
                ):
                    # Используем DuckDuckGo как более простой вариант
                    encoded_query = urllib.parse.quote_plus(query)
                    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }

                    response = requests.get(search_url, headers=headers, timeout=10)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Извлекаем результаты поиска
                    results = []
                    search_results = soup.find_all("div", class_="result")

                    for i, result in enumerate(search_results[:num_results]):
                        try:
                            title_elem = result.find("a", class_="result__a")
                            title = (
                                title_elem.get_text().strip()
                                if title_elem
                                else "Без названия"
                            )
                            link = title_elem.get("href") if title_elem else ""

                            snippet_elem = result.find("a", class_="result__snippet")
                            snippet = (
                                snippet_elem.get_text().strip()
                                if snippet_elem
                                else "Описание недоступно"
                            )

                            results.append(f"{i+1}. {title}\n   {snippet}\n   {link}")
                        except Exception as e:
                            self.logger.warning(
                                f"[TOOL-EXEC] Ошибка обработки результата {i+1}: {e}"
                            )
                            continue

                    if results:
                        search_results_text = (
                            f"Результаты поиска для '{query}':\n\n"
                            + "\n\n".join(results)
                        )
                        self.logger.info(
                            f"[TOOL-EXEC] Найдено {len(results)} результатов"
                        )
                        return search_results_text
                    else:
                        return f"По запросу '{query}' результаты не найдены"

                else:
                    return f"Поисковая система '{search_engine}' пока не поддерживается. Используйте 'google' или 'duckduckgo'"

            except ImportError:
                return "Ошибка: для поиска в интернете требуются библиотеки requests и beautifulsoup4"
            except requests.RequestException as e:
                return f"Ошибка выполнения поиска: {str(e)}"
            except Exception as e:
                return f"Ошибка обработки результатов поиска: {str(e)}"

        except Exception as e:
            error_msg = f"Критическая ошибка при поиске в интернете: {str(e)}"
            self.logger.error(f"[TOOL-EXEC] {error_msg}")
            return f"Ошибка: {error_msg}"

    def file_operations(
        self,
        operation: str,
        path: str,
        content: str = "",
        destination: str = "",
        pattern: str = "*",
        recursive: bool = False,
        search_term: str = "",
        old_text: str = "",
        case_sensitive: bool = False,
        max_depth: int = 3,
    ) -> str:
        """
        Выполняет операции с файловой системой

        Args:
            operation: Тип операции
            path: Путь к файлу/директории
            content: Содержимое для записи
            destination: Путь назначения
            pattern: Паттерн для поиска
            recursive: Рекурсивный поиск
            search_term: Текст для поиска
            old_text: Текст для замены
            case_sensitive: Учитывать регистр
            max_depth: Максимальная глубина

        Returns:
            str: Результат операции
        """
        try:
            self.logger.info(f"[TOOL-EXEC] Файловая операция: {operation}")
            self.logger.info(f"[TOOL-EXEC] Путь: {path}")

            import glob
            import shutil
            import hashlib
            from pathlib import Path

            # Проверяем безопасность пути
            if not self._is_safe_path(path):
                return f"Ошибка: небезопасный путь '{path}'"

            if operation == "read":
                if not os.path.exists(path):
                    return f"Ошибка: файл '{path}' не существует"

                if not os.path.isfile(path):
                    return f"Ошибка: '{path}' не является файлом"

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    # Ограничиваем размер вывода
                    if len(file_content) > 5000:
                        file_content = (
                            file_content[:5000]
                            + "\n... [файл обрезан, показаны первые 5000 символов]"
                        )

                    self.logger.info(
                        f"[TOOL-EXEC] Прочитан файл: {len(file_content)} символов"
                    )
                    return f"Содержимое файла '{path}':\n\n{file_content}"

                except UnicodeDecodeError:
                    return f"Ошибка: не удалось прочитать файл '{path}' (возможно, это бинарный файл)"
                except Exception as e:
                    return f"Ошибка чтения файла '{path}': {str(e)}"

            elif operation == "write":
                if not content:
                    return "Ошибка: не указано содержимое для записи"

                try:
                    # Создаём директорию если нужно
                    os.makedirs(os.path.dirname(path), exist_ok=True)

                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)

                    self.logger.info(
                        f"[TOOL-EXEC] Записан файл: {len(content)} символов"
                    )
                    return f"Файл '{path}' успешно записан ({len(content)} символов)"

                except Exception as e:
                    return f"Ошибка записи файла '{path}': {str(e)}"

            elif operation == "list":
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
                            size = os.path.getsize(item_path)
                            items.append(f"📄 {item} ({size} байт)")

                    if items:
                        items_text = "\n".join(items[:50])  # Максимум 50 элементов
                        if len(os.listdir(path)) > 50:
                            items_text += (
                                f"\n... и ещё {len(os.listdir(path)) - 50} элементов"
                            )

                        self.logger.info(
                            f"[TOOL-EXEC] Список директории: {len(items)} элементов"
                        )
                        return f"Содержимое директории '{path}':\n\n{items_text}"
                    else:
                        return f"Директория '{path}' пуста"

                except Exception as e:
                    return f"Ошибка чтения директории '{path}': {str(e)}"

            elif operation == "exists":
                exists = os.path.exists(path)
                self.logger.info(
                    f"[TOOL-EXEC] Проверка существования: {path} = {exists}"
                )
                return f"Путь '{path}' {'существует' if exists else 'не существует'}"

            elif operation == "info":
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

                    self.logger.info(f"[TOOL-EXEC] Получена информация о: {path}")
                    return "\n".join(info_lines)

                except Exception as e:
                    return f"Ошибка получения информации о '{path}': {str(e)}"

            else:
                return f"Операция '{operation}' пока не реализована. Доступные операции: read, write, list, exists, info"

        except Exception as e:
            error_msg = f"Критическая ошибка файловой операции: {str(e)}"
            self.logger.error(f"[TOOL-EXEC] {error_msg}")
            return f"Ошибка: {error_msg}"

    def _is_safe_path(self, path: str) -> bool:
        """
        Проверяет безопасность пути для файловых операций

        Args:
            path: Путь для проверки

        Returns:
            bool: True если путь безопасен
        """
        try:
            # Нормализуем путь
            normalized_path = os.path.normpath(path)

            # Запрещённые паттерны
            dangerous_patterns = [
                "..",
                "/etc/",
                "/root/",
                "/home/",
                "C:\\Windows\\",
                "C:\\Program Files\\",
                "/usr/bin/",
                "/bin/",
                "/sbin/",
                "/var/",
                "/tmp/",
                "/dev/",
                "/proc/",
            ]

            # Проверяем на опасные паттерны
            for pattern in dangerous_patterns:
                if pattern in normalized_path:
                    self.logger.warning(
                        f"[TOOL-EXEC] Обнаружен опасный паттерн в пути: {pattern}"
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(f"[TOOL-EXEC] Ошибка проверки безопасности пути: {e}")
            return False
