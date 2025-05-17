"""
Terminal Access Module для Reasoning Agent

Модуль предоставляет контролируемый доступ к терминалу для ReasoningAgent
с системой разрешений и безопасным выполнением команд.
"""

import os
import sys
import asyncio
import subprocess
import shlex
import re
from typing import Dict, List, Optional, Union, Tuple, Any, Set

from app.logger import logger


class TerminalAccess:
    """
    Класс для безопасного доступа к терминалу в режиме reasoning.

    Предоставляет:
    1. Проверку безопасности команд перед выполнением
    2. Логирование всех выполняемых команд
    3. Ограничение опасных операций
    4. Возможность настройки рабочих директорий
    5. Контроль над историей выполненных команд
    6. Мониторинг состояния выполнения
    """

    # Список потенциально опасных команд
    UNSAFE_COMMANDS = [
        "rm -rf", "rmdir /s", "del /s", "format",
        "dd", ">", "DROP", "DELETE FROM", "sudo",
        "chmod -R", "chown -R", ":(){ :|:& };:",  # fork bomb
        "deltree", "rd /s", "reg delete", "mkfs",
        "wget -O - | bash", "curl | sh",
        "shutdown", "reboot", "halt", "> /dev/sda",
        "attrib -r", "xcopy /e /c /y", "rd /q /s",
    ]

    # Разрешенные директории для доступа (относительно корня проекта)
    ALLOWED_DIRS = [
        ".", "./app", "./tests", "./examples", "./workspace",
        "./data", "./docs", "./scripts", "./logs"
    ]

    # Безопасные команды, которые разрешены всегда
    SAFE_COMMANDS = [
        "echo", "dir", "ls", "pwd", "cd", "type", "cat",
        "python --version", "pip list", "pip freeze",
        "cls", "clear", "help", "ver", "date", "time"
    ]

    # Регулярные выражения для распознавания небезопасных команд
    UNSAFE_PATTERNS = [
        r">([\w\/\\\.]+)",  # перенаправление вывода
        r"rm\s+-[rf]{1,2}",  # опасные ключи rm
        r"wget\s+.*\|\s*[bash|sh]",  # скачивание и выполнение скриптов
        r"curl\s+.*\|\s*[bash|sh]",  # скачивание и выполнение скриптов
        r"sudo\s+",  # sudo команды
        r"\.\.\/",  # выход за пределы текущей директории
        r"\.\.\\",  # выход за пределы текущей директории в Windows
    ]

    def __init__(
        self,
        root_dir: Optional[str] = None,
        max_output_lines: int = 500,
        safe_mode: bool = True,
        timeout: Optional[float] = 30.0
    ):
        """
        Инициализирует объект доступа к терминалу.

        Args:
            root_dir: Корневая директория проекта (по умолчанию - текущая)
            max_output_lines: Максимальное количество линий для вывода
            safe_mode: Включение проверок безопасности
            timeout: Тайм-аут выполнения по умолчанию (в секундах)
        """
        self.root_dir = root_dir or os.getcwd()
        self.max_output_lines = max_output_lines
        self.safe_mode = safe_mode
        self.default_timeout = timeout
        self.command_history: List[Dict[str, Any]] = []
        self.current_dir = self.root_dir
        self.environment_vars: Dict[str, str] = {}
        self.allowed_extensions: Set[str] = {".py", ".txt", ".json", ".md", ".csv", ".yml", ".yaml"}

        # Инициализируем переменные окружения на основе текущего окружения
        self.environment_vars = dict(os.environ)

        # Создаем набор разрешенных абсолютных путей
        self.allowed_abs_paths = set()
        for rel_path in self.ALLOWED_DIRS:
            abs_path = os.path.abspath(os.path.join(self.root_dir, rel_path.replace("./", "")))
            self.allowed_abs_paths.add(abs_path)

        logger.info(f"Terminal access initialized with root dir: {self.root_dir}")
        logger.info(f"Safe mode: {self.safe_mode}, Timeout: {self.default_timeout}s")

    def _is_command_safe(self, command: str) -> Tuple[bool, str]:
        """
        Проверяет безопасность команды для выполнения.

        Args:
            command: Командная строка для проверки

        Returns:
            Кортеж (безопасность, причина небезопасности)
        """
        if not self.safe_mode:
            return True, ""

        command_lower = command.lower()

        # Проверяем на безусловно безопасные команды
        for safe_cmd in self.SAFE_COMMANDS:
            if command_lower.startswith(safe_cmd.lower()):
                return True, ""

        # Проверяем наличие опасных команд
        for unsafe_cmd in self.UNSAFE_COMMANDS:
            if unsafe_cmd.lower() in command_lower:
                return False, f"Команда содержит потенциально опасный элемент: {unsafe_cmd}"

        # Проверяем опасные шаблоны через регулярные выражения
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, command):
                return False, f"Команда соответствует опасному шаблону: {pattern}"

        # Проверяем подозрительные паттерны
        if ".." in command and ("cd" in command_lower or "dir" in command_lower):
            return False, "Попытка выхода за пределы рабочей директории"

        # Проверка на потенциально опасные вызовы командных файлов
        if any(ext in command.lower() for ext in [".exe", ".bat", ".sh", ".ps1"]):
            # Разрешаем только если это явный вызов Python
            if not command.lower().startswith(("python ", "py ")):
                return False, "Запрещен прямой запуск исполняемых файлов"

        # Проверяем на попытки выполнения скриптов с расширениями
        if ("./" in command or ".\\") and not command.startswith(("python ", "py ")):
            return False, "Прямой запуск скриптов запрещен"

        # Проверяем наличие потенциально опасных символов в командах
        if "&&" in command or "||" in command or ";" in command:
            parts = []
            if "&&" in command:
                parts.extend(command.split("&&"))
            elif "||" in command:
                parts.extend(command.split("||"))
            elif ";" in command:
                parts.extend(command.split(";"))

            # Проверяем каждую часть составной команды
            for part in parts:
                is_safe, reason = self._is_command_safe(part.strip())
                if not is_safe:
                    return False, f"Часть составной команды небезопасна: {reason}"

        return True, ""

    def _is_directory_allowed(self, directory: str) -> bool:
        """
        Проверяет, разрешен ли доступ к указанной директории.

        Args:
            directory: Проверяемая директория

        Returns:
            True если директория в списке разрешенных
        """
        if not self.safe_mode:
            return True

        # Нормализуем пути
        abs_dir = os.path.abspath(directory)
        abs_root = os.path.abspath(self.root_dir)

        # Проверяем напрямую, входит ли директория в список разрешенных абсолютных путей
        if abs_dir in self.allowed_abs_paths:
            return True

        # Проверяем, находится ли директория внутри корневой
        if not abs_dir.startswith(abs_root):
            return False

        # Проверяем, есть ли директория в списке разрешенных
        rel_path = os.path.relpath(abs_dir, abs_root)
        rel_path_normalized = rel_path.replace("\\", "/")  # Нормализуем слеши для Windows

        for allowed in self.ALLOWED_DIRS:
            allowed_path = allowed.replace("./", "").replace(".", "")
            if rel_path_normalized == allowed_path or rel_path_normalized.startswith(f"{allowed_path}/"):
                return True

        return False

    async def execute_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        capture_stderr: bool = True,
        timeout: Optional[float] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет команду в терминале.

        Args:
            command: Команда для выполнения
            working_dir: Рабочая директория (по умолчанию текущая)
            capture_stderr: Захватывать ли stderr
            timeout: Тайм-аут выполнения в секундах
            env_vars: Переменные окружения для команды

        Returns:
            Словарь с результатами выполнения команды
        """
        # Определяем тайм-аут, если не указан
        if timeout is None:
            timeout = self.default_timeout

        # Определяем рабочую директорию
        if working_dir:
            wd = os.path.abspath(os.path.join(self.root_dir, working_dir))
        else:
            wd = self.current_dir

        # Проверяем безопасность директории
        if not self._is_directory_allowed(wd):
            logger.warning(f"Access to directory denied: {wd}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Access denied: Directory {wd} is not in the allowed list",
                "command": command,
                "working_dir": wd,
                "error": "AccessDenied",
                "return_code": 1
            }

        # Проверяем безопасность команды
        is_safe, reason = self._is_command_safe(command)
        if not is_safe:
            logger.warning(f"Unsafe command rejected: {command}. Reason: {reason}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command rejected due to safety concerns: {reason}",
                "command": command,
                "working_dir": wd,
                "error": "UnsafeCommand",
                "return_code": 1
            }

        # Создаем запись в истории
        command_record = {
            "command": command,
            "working_dir": wd,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "started"
        }
        self.command_history.append(command_record)
        command_index = len(self.command_history) - 1

        # Объединяем переменные окружения
        merged_env = dict(self.environment_vars)
        if env_vars:
            merged_env.update(env_vars)

        # Логируем выполнение
        logger.info(f"Executing command in {wd}: {command}")

        try:
            # Определяем параметры процесса
            kwargs = {
                "shell": True,
                "cwd": wd,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE if capture_stderr else None,
                "env": merged_env
            }

            # Для Windows используем powershell
            if sys.platform == "win32":
                # Оборачиваем команду в PowerShell для лучшей совместимости
                cmd_args = ["powershell", "-Command", command]

                # Для переменных окружения в PowerShell требуется особый синтаксис
                # Заменим %VAR% на $env:VAR для лучшей совместимости
                if any(f"%{var}%" in command for var in self.environment_vars.keys()):
                    cmd_with_vars = command
                    for var, val in self.environment_vars.items():
                        cmd_with_vars = cmd_with_vars.replace(f"%{var}%", f"$env:{var}")
                    cmd_args = ["powershell", "-Command", cmd_with_vars]

                kwargs["shell"] = False
            else:
                cmd_args = command

            # Запускаем процесс с таймаутом
            process = await asyncio.create_subprocess_exec(
                *cmd_args if sys.platform == "win32" else cmd_args,
                **kwargs
            ) if sys.platform == "win32" else await asyncio.create_subprocess_shell(
                cmd_args,
                **kwargs
            )

            # Ожидаем завершения с таймаутом
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                # Декодируем вывод
                stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
                stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

            except asyncio.TimeoutError:
                process.kill()
                logger.warning(f"Command timed out after {timeout}s: {command}")

                # Обновляем запись в истории
                if command_index < len(self.command_history):
                    self.command_history[command_index].update({
                        "status": "timeout",
                        "end_timestamp": asyncio.get_event_loop().time(),
                        "duration": asyncio.get_event_loop().time() - self.command_history[command_index]["timestamp"]
                    })

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout}s",
                    "command": command,
                    "working_dir": wd,
                    "error": "Timeout",
                    "return_code": 1
                }

            # Получаем код возврата
            return_code = process.returncode or 0

            # Обрабатываем результат
            stdout_lines = stdout.splitlines() if stdout else []
            stderr_lines = stderr.splitlines() if stderr else []

            # Ограничиваем количество строк в выводе
            if len(stdout_lines) > self.max_output_lines:
                stdout_truncated = "\n".join(stdout_lines[:self.max_output_lines])
                stdout_truncated += f"\n... (output truncated, {len(stdout_lines) - self.max_output_lines} more lines)"
            else:
                stdout_truncated = stdout

            if len(stderr_lines) > self.max_output_lines:
                stderr_truncated = "\n".join(stderr_lines[:self.max_output_lines])
                stderr_truncated += f"\n... (output truncated, {len(stderr_lines) - self.max_output_lines} more lines)"
            else:
                stderr_truncated = stderr

            # Обновляем текущую директорию, если команда - cd
            if command.strip().startswith(("cd ", "chdir ")):
                parts = command.strip().split(" ", 1)
                if len(parts) > 1:
                    target_dir = parts[1].strip().strip('"').strip("'")

                    # Определяем абсолютный путь целевой директории
                    if os.path.isabs(target_dir):
                        abs_target = target_dir
                    else:
                        abs_target = os.path.abspath(os.path.join(wd, target_dir))

                    # Проверяем, разрешена ли директория
                    if self._is_directory_allowed(abs_target) and os.path.isdir(abs_target):
                        self.current_dir = abs_target
                        logger.info(f"Changed current directory to: {self.current_dir}")

            # Обновляем запись в истории
            if command_index < len(self.command_history):
                self.command_history[command_index].update({
                    "status": "completed" if return_code == 0 else "error",
                    "return_code": return_code,
                    "end_timestamp": asyncio.get_event_loop().time(),
                    "duration": asyncio.get_event_loop().time() - self.command_history[command_index]["timestamp"]
                })

            # Формируем результат
            result = {
                "success": return_code == 0,
                "stdout": stdout_truncated,
                "stderr": stderr_truncated,
                "command": command,
                "working_dir": wd,
                "return_code": return_code
            }

            logger.info(f"Command completed with return code: {return_code}")
            return result

        except Exception as e:
            logger.error(f"Error executing command: {command}, Error: {str(e)}")

            # Обновляем запись в истории
            if command_index < len(self.command_history):
                self.command_history[command_index].update({
                    "status": "error",
                    "error_message": str(e),
                    "end_timestamp": asyncio.get_event_loop().time(),
                    "duration": asyncio.get_event_loop().time() - self.command_history[command_index]["timestamp"]
                })

            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "command": command,
                "working_dir": wd,
                "error": "ExecutionError",
                "return_code": 1
            }

    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Возвращает историю выполненных команд.

        Args:
            limit: Максимальное количество записей истории для возврата

        Returns:
            Список записей истории команд
        """
        if limit is not None and limit > 0:
            return self.command_history[-limit:]
        return self.command_history

    def set_current_directory(self, directory: str) -> bool:
        """
        Устанавливает текущую рабочую директорию.

        Args:
            directory: Новая рабочая директория (абсолютный или относительный путь)

        Returns:
            True если директория успешно установлена
        """
        # Нормализуем путь
        if os.path.isabs(directory):
            abs_path = directory
        else:
            abs_path = os.path.abspath(os.path.join(self.root_dir, directory))

        # Проверяем, разрешена ли директория
        if not self._is_directory_allowed(abs_path):
            logger.warning(f"Access to directory denied: {abs_path}")
            return False

        # Проверяем, существует ли директория
        if not os.path.isdir(abs_path):
            logger.warning(f"Directory does not exist: {abs_path}")
            return False

        # Устанавливаем новую текущую директорию
        self.current_dir = abs_path
        logger.info(f"Changed current directory to: {self.current_dir}")
        return True

    def get_current_directory(self) -> str:
        """
        Возвращает текущую рабочую директорию.

        Returns:
            Текущая рабочая директория
        """
        return self.current_dir

    def set_environment_variable(self, name: str, value: str) -> bool:
        """
        Устанавливает переменную окружения для выполнения команд.

        Args:
            name: Имя переменной
            value: Значение переменной

        Returns:
            True если переменная успешно установлена
        """
        # Проверяем безопасность имени переменной
        if self.safe_mode and any(char in name for char in ["=", ";", "|", "&", "<", ">", "`", "$", "\\"]):
            logger.warning(f"Unsafe environment variable name: {name}")
            return False

        self.environment_vars[name] = value
        logger.info(f"Set environment variable: {name}={value}")
        return True

    def get_environment_variables(self) -> Dict[str, str]:
        """
        Возвращает текущие переменные окружения.

        Returns:
            Словарь переменных окружения
        """
        return dict(self.environment_vars)

    def clear_command_history(self) -> None:
        """
        Очищает историю команд.
        """
        self.command_history = []
        logger.info("Command history cleared")

    def is_file_access_allowed(self, file_path: str) -> bool:
        """
        Проверяет, разрешен ли доступ к указанному файлу.

        Args:
            file_path: Путь к файлу

        Returns:
            True если доступ к файлу разрешен
        """
        if not self.safe_mode:
            return True

        # Проверяем расширение файла
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.allowed_extensions:
            return False

        # Проверяем, находится ли файл в разрешенной директории
        file_dir = os.path.dirname(os.path.abspath(file_path))
        return self._is_directory_allowed(file_dir)

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

    def get_allowed_directories(self) -> List[str]:
        """
        Возвращает список разрешенных директорий.

        Returns:
            Список разрешенных директорий (относительные пути)
        """
        return self.ALLOWED_DIRS.copy()

    async def get_system_info(self) -> Dict[str, Any]:
        """
        Получает информацию о системе через безопасные команды.

        Returns:
            Словарь с информацией о системе
        """
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "current_directory": self.current_dir,
            "project_root": self.root_dir,
        }

        # Получаем список файлов в текущей директории
        dir_result = await self.execute_command("dir" if sys.platform == "win32" else "ls -la")
        if dir_result["success"]:
            info["directory_contents"] = dir_result["stdout"]

        # Получаем информацию о версии Python
        python_version = await self.execute_command("python --version")
        if python_version["success"]:
            info["python_version_full"] = python_version["stdout"]

        # На Windows получаем информацию о системе
        if sys.platform == "win32":
            sys_info = await self.execute_command("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"")
            if sys_info["success"]:
                info["windows_system_info"] = sys_info["stdout"]
        else:
            # На Unix-подобных системах
            sys_info = await self.execute_command("uname -a")
            if sys_info["success"]:
                info["unix_system_info"] = sys_info["stdout"]

        return info

    async def execute_python_script(
        self, script_path: str, args: Optional[List[str]] = None, timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет Python-скрипт с опциональными аргументами.

        Args:
            script_path: Путь к Python-скрипту для выполнения
            args: Список аргументов для скрипта
            timeout: Тайм-аут выполнения в секундах

        Returns:
            Словарь с результатами выполнения скрипта
        """
        # Проверка существования и расширения файла
        if not os.path.exists(script_path):
            return {
                "status": "error",
                "error": f"Script file not found: {script_path}",
                "success": False,
                "return_code": 1
            }

        # Проверка расширения файла
        if not script_path.endswith(".py"):
            return {
                "status": "error",
                "error": f"Access denied: Script {script_path} is not allowed",
                "success": False,
                "return_code": 1
            }

        # Проверка доступа к файлу
        if not self.is_file_access_allowed(script_path):
            return {
                "status": "error",
                "error": f"Access denied: Script {script_path} is outside allowed directories",
                "success": False,
                "return_code": 1
            }

        # Формируем команду
        command = f"python -u \"{script_path}\""
        if args:
            args_str = " ".join([f'"{arg}"' if " " in arg else arg for arg in args])
            command += f" {args_str}"

        # Для Windows добавляем параметр кодировки
        if sys.platform == "win32":
            # Добавляем PYTHONIOENCODING для решения проблем с кодировкой на Windows
            command = f"$env:PYTHONIOENCODING='utf-8'; {command}"

        # Принудительно устанавливаем safe_mode_backup в False для этой операции
        safe_mode_backup = self.safe_mode
        self.safe_mode = False

        try:
            # Выполняем скрипт
            result = await self.execute_command(command, timeout=timeout)
            return result
        finally:
            # Восстанавливаем предыдущее значение safe_mode
            self.safe_mode = safe_mode_backup

    def is_safe_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет безопасность команды перед выполнением.

        Args:
            command: Команда для проверки

        Returns:
            Кортеж (is_safe, reason), где is_safe - флаг безопасности,
            reason - причина отказа (если команда небезопасна)
        """
        # Игнорируем проверки в небезопасном режиме
        if not self.safe_mode:
            return True, None

        # Список команд, которые разрешены всегда
        safe_commands = ["cd", "dir", "ls", "echo", "type", "cat", "pwd",
                        "python --version", "pip --version", "python -V", "pip -V"]

        # Проверяем разрешенные команды
        for safe_cmd in safe_commands:
            if command.strip().startswith(safe_cmd):
                return True, None

        # Проверяем запуск Python-скриптов
        if ("python" in command and ".py" in command) or ("$env:PYTHONIOENCODING" in command and "python" in command):
            # Разрешаем запуск Python-скриптов через метод execute_python_script
            script_path = None
            for part in command.split():
                if part.endswith(".py") or part.endswith('.py"'):
                    script_path = part.strip('"')
                    break

            if script_path and os.path.exists(script_path.strip('"')):
                # Проверяем, находится ли скрипт в разрешенных директориях
                if self.is_file_access_allowed(script_path.strip('"')):
                    return True, None
                else:
                    return False, f"Файл скрипта находится вне разрешенных директорий: {script_path}"

        # Проверяем остальные команды
        is_safe, reason = self._is_command_safe(command)
        return is_safe, reason

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы модуля терминального доступа.
        """
        logger.info("Cleaning up terminal access resources")
        # Здесь может быть код для освобождения ресурсов, если они были выделены
        return None
