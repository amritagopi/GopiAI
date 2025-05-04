"""
Terminal Access Module для Reasoning Agent

Модуль предоставляет контролируемый доступ к терминалу для ReasoningAgent
с системой разрешений и безопасным выполнением команд.
"""

import os
import sys
import asyncio
import subprocess
from typing import Dict, List, Optional, Union, Tuple, Any

from app.logger import logger


class TerminalAccess:
    """
    Класс для безопасного доступа к терминалу в режиме reasoning.

    Предоставляет:
    1. Проверку безопасности команд перед выполнением
    2. Логирование всех выполняемых команд
    3. Ограничение опасных операций
    4. Возможность настройки рабочих директорий
    """

    # Список потенциально опасных команд
    UNSAFE_COMMANDS = [
        "rm -rf", "rmdir /s", "del /s", "format",
        "dd", ">", "DROP", "DELETE FROM", "sudo",
        "chmod -R", "chown -R", ":(){ :|:& };:",  # fork bomb
    ]

    # Разрешенные директории для доступа (относительно корня проекта)
    ALLOWED_DIRS = [
        ".", "./app", "./tests", "./examples", "./workspace",
        "./data", "./docs", "./scripts", "./logs"
    ]

    def __init__(
        self,
        root_dir: Optional[str] = None,
        max_output_lines: int = 500,
        safe_mode: bool = True
    ):
        """
        Инициализирует объект доступа к терминалу.

        Args:
            root_dir: Корневая директория проекта (по умолчанию - текущая)
            max_output_lines: Максимальное количество линий для вывода
            safe_mode: Включение проверок безопасности
        """
        self.root_dir = root_dir or os.getcwd()
        self.max_output_lines = max_output_lines
        self.safe_mode = safe_mode
        self.command_history: List[Dict[str, Any]] = []
        self.current_dir = self.root_dir

        logger.info(f"Terminal access initialized with root dir: {self.root_dir}")

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

        # Проверяем наличие опасных команд
        for unsafe_cmd in self.UNSAFE_COMMANDS:
            if unsafe_cmd.lower() in command_lower:
                return False, f"Команда содержит потенциально опасный элемент: {unsafe_cmd}"

        # Проверяем подозрительные паттерны
        if ".." in command and ("cd" in command_lower or "dir" in command_lower):
            return False, "Попытка выхода за пределы рабочей директории"

        # Проверяем на попытки выполнения скриптов с расширениями
        if ("./" in command or ".\\") and not command.startswith(("python ", "py ")):
            return False, "Прямой запуск скриптов запрещен"

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

        # Проверяем, находится ли директория внутри корневой
        if not abs_dir.startswith(abs_root):
            return False

        # Проверяем, есть ли директория в списке разрешенных
        rel_path = os.path.relpath(abs_dir, abs_root)
        for allowed in self.ALLOWED_DIRS:
            allowed_path = allowed.replace("./", "").replace(".", "")
            if rel_path == allowed_path or rel_path.startswith(f"{allowed_path}/"):
                return True

        return False

    async def execute_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        capture_stderr: bool = True,
        timeout: Optional[float] = 30.0,
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет команду в терминале.

        Args:
            command: Команда для выполнения
            working_dir: Рабочая директория (по умолчанию текущая)
            capture_stderr: Захватывать ли stderr
            timeout: Тайм-аут выполнения в секундах

        Returns:
            Словарь с результатами выполнения команды
        """
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
                "error": "AccessDenied"
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
                "error": "UnsafeCommand"
            }

        # Создаем запись в истории
        command_record = {
            "command": command,
            "working_dir": wd,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.command_history.append(command_record)

        # Логируем выполнение
        logger.info(f"Executing command in {wd}: {command}")

        try:
            # Определяем параметры процесса
            kwargs = {
                "shell": True,
                "cwd": wd,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE if capture_stderr else None,
                "text": True,
                "encoding": "utf-8"
            }

            # Для Windows используем powershell
            if sys.platform == "win32":
                # Оборачиваем команду в PowerShell для лучшей совместимости
                cmd_args = ["powershell", "-Command", command]
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
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                logger.warning(f"Command timed out after {timeout}s: {command}")
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout}s",
                    "command": command,
                    "working_dir": wd,
                    "error": "Timeout"
                }

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
                    target_dir = parts[1].strip().strip('"\'')
                    if os.path.isabs(target_dir):
                        self.current_dir = target_dir
                    else:
                        self.current_dir = os.path.abspath(os.path.join(wd, target_dir))
                    logger.info(f"Changed current directory to: {self.current_dir}")

            # Формируем результат
            result = {
                "success": process.returncode == 0,
                "stdout": stdout_truncated,
                "stderr": stderr_truncated if capture_stderr else None,
                "return_code": process.returncode,
                "command": command,
                "working_dir": wd
            }

            # Обновляем запись в истории
            command_record.update({
                "success": process.returncode == 0,
                "return_code": process.returncode
            })

            return result

        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "command": command,
                "working_dir": wd,
                "error": str(e)
            }

    def get_command_history(self) -> List[Dict[str, Any]]:
        """
        Возвращает историю выполненных команд.

        Returns:
            Список словарей с информацией о выполненных командах
        """
        return self.command_history

    def set_current_directory(self, directory: str) -> bool:
        """
        Устанавливает текущую рабочую директорию.

        Args:
            directory: Новая рабочая директория

        Returns:
            True если директория успешно установлена
        """
        if not os.path.isabs(directory):
            abs_dir = os.path.abspath(os.path.join(self.root_dir, directory))
        else:
            abs_dir = directory

        if not self._is_directory_allowed(abs_dir):
            logger.warning(f"Access to directory denied: {abs_dir}")
            return False

        if not os.path.exists(abs_dir) or not os.path.isdir(abs_dir):
            logger.warning(f"Directory does not exist: {abs_dir}")
            return False

        self.current_dir = abs_dir
        logger.info(f"Current directory set to: {self.current_dir}")
        return True

    def get_current_directory(self) -> str:
        """
        Возвращает текущую рабочую директорию.

        Returns:
            Путь к текущей рабочей директории
        """
        return self.current_dir
