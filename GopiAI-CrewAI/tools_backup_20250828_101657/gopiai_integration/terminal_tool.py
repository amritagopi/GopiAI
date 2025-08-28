"""
Terminal Tool для GopiAI-CrewAI
==============================

Инструмент для выполнения команд в терминале через интерфейс GopiAI-UI.
Безопасная интеграция между LLM и терминальным виджетом.
"""

# Используем BaseTool из crewai_tools вместо langchain
from crewai.tools.agent_tools import StructuredTool as BaseTool
from typing import Dict, Any, Optional
import subprocess
import logging
import json
from pathlib import Path
import re
import os

# Настраиваем логгер
logger = logging.getLogger(__name__)

def _bool_env(val: str) -> bool:
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _read_settings_flag() -> bool:
    """Чтение флага небезопасного режима из settings.json.
    Поиск в порядке приоритета:
      1) Путь, заданный в GOPIAI_SETTINGS_PATH (файл или директория)
      2) Текущая директория: ./settings.json и ./config/settings.json
      3) Директория скрипта: <pkg>/settings.json и <pkg>/config/settings.json
      4) %APPDATA%/GopiAI/settings.json (Windows)
    Возвращает True, если в конфиге есть {"terminal_unsafe": true}
    """
    candidates = []

    # 1) Явный путь от пользователя
    custom = os.getenv("GOPIAI_SETTINGS_PATH")
    if custom:
        p = Path(custom)
        if p.is_file():
            candidates.append(p)
        elif p.is_dir():
            candidates.extend([p / "settings.json", p / "config" / "settings.json"])

    # 2) Текущая директория
    cwd = Path.cwd()
    candidates.extend([cwd / "settings.json", cwd / "config" / "settings.json"])

    # 3) Директория текущего файла/пакета
    here = Path(__file__).resolve().parent
    candidates.extend([here / "settings.json", here / "config" / "settings.json"])

    # 4) %APPDATA%/GopiAI/settings.json (Windows)
    appdata = os.getenv("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "GopiAI" / "settings.json")

    for path in candidates:
        try:
            if path and path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                val = data.get("terminal_unsafe")
                if isinstance(val, bool):
                    return val
                if isinstance(val, str):
                    return _bool_env(val)
        except Exception:
            continue
    return False


def _unsafe_mode_enabled() -> bool:
    """Динамическая проверка небезопасного режима.
    Приоритет: ENV GOPIAI_TERMINAL_UNSAFE > settings.json > False
    """
    env_val = os.getenv('GOPIAI_TERMINAL_UNSAFE')
    if env_val is not None:
        return _bool_env(env_val)
    return _read_settings_flag()

# Список запрещенных команд и паттернов для безопасности
FORBIDDEN_COMMANDS = [
    "rm -rf", "deltree", "format", "shutdown", "reboot",
    "mkfs", "dd if=", ":(){ :|:& };:", "> /dev/sda",
    "chmod -R 777 /", "mv /* /dev/null", "wget -O- | bash"
]

# Глобальная переменная для хранения ссылки на терминальный виджет
_terminal_widget_instance = None

def set_terminal_widget(terminal_widget):
    """Устанавливает глобальную ссылку на терминальный виджет"""
    global _terminal_widget_instance
    _terminal_widget_instance = terminal_widget
    logger.info(f"Терминальный виджет установлен: {terminal_widget}")

def get_terminal_widget():
    """Возвращает глобальную ссылку на терминальный виджет"""
    global _terminal_widget_instance
    return _terminal_widget_instance

class TerminalTool(BaseTool):
    """Инструмент для выполнения команд в терминале GopiAI"""
    
    name: str = 'terminal'
    description: str = 'Execute shell commands in the UI terminal and get output. Use for running commands visible to user.'
    
    def _is_safe_command(self, command: str) -> bool:
        """Проверяет команду на безопасность"""
        # В небезопасном режиме все команды считаются допустимыми
        if _unsafe_mode_enabled():
            return True
        # Проверка на запрещенные команды
        for forbidden in FORBIDDEN_COMMANDS:
            if forbidden in command.lower():
                return False
        
        # Проверка на подозрительные паттерны
        suspicious_patterns = [
            r"rm\s+-rf\s+[/~]",  # Удаление корневой директории
            r">\s+/dev/[hs]d[a-z]",  # Запись в устройство
            r"dd\s+.*\s+of=/dev/[hs]d[a-z]",  # Запись через dd
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, command):
                return False
                
        return True
    
    def _run(self, command: str) -> Dict[str, Any]:
        """Выполняет команду в терминале (MCP, либо прямой subprocess fallback)."""
        logger.debug(f"Executing command: {command} | UNSAFE_MODE={_unsafe_mode_enabled()}")
        
        # Проверка на безопасность (в UNSAFE_MODE пропускается)
        if not self._is_safe_command(command):
            logger.warning(f"Команда заблокирована: {command}")
            return {"terminal_output": {
                "command": command,
                "output": "",
                "error": "Команда заблокирована по соображениям безопасности",
                "success": False
            }}
        
        # 1) Попытаться выполнить через MCP, если клиент доступен
        mcp_client = getattr(self, 'mcp_client', None)
        if mcp_client is not None:
            try:
                mcp_result = mcp_client.query({"type": "execute_shell", "command": command})
                output = mcp_result.get('output', '')
                error = mcp_result.get('error', '')
                success = mcp_result.get('success', False)
                terminal = get_terminal_widget()
                if terminal:
                    terminal.log_ai_command(command, output + ("\n" + error if error else ""))
                return {"terminal_output": {"command": command, "output": output, "error": error, "success": success}}
            except Exception as e:
                logger.warning(f"MCP execution failed, falling back to subprocess: {e}")
                # Продолжаем к subprocess
        
        # 2) Fallback: прямое выполнение через subprocess (разрешено особенно в UNSAFE_MODE)
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )
            output = completed.stdout or ''
            error = completed.stderr or ''
            success = completed.returncode == 0
            terminal = get_terminal_widget()
            if terminal:
                terminal.log_ai_command(command, output + ("\n" + error if error else ""))
            return {"terminal_output": {"command": command, "output": output, "error": error, "success": success}}
        except Exception as e:
            error_msg = f"Subprocess error: {str(e)}"
            return {"terminal_output": {"command": command, "output": "", "error": error_msg, "success": False}}

    def _arun(self, command: str) -> Any:
        """Асинхронное выполнение не поддерживается"""
        raise NotImplementedError('Async operation not supported')