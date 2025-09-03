"""
Terminal Tool - инструмент для выполнения команд в терминале
Восстановлено из коммита 2f0fe4256d7f0d5bf2168a4db56d6b6def937860
"""

import logging
import subprocess
import os
import shlex
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TerminalTool:
    """Инструмент для безопасного выполнения команд в терминале"""
    
    def __init__(self):
        self.name = "terminal"
        self.description = "Выполняет команды в терминале системы"
        logger.info("🔧 TerminalTool инициализирован")
    
    def _run(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Выполняет команду в терминале с таймаутом
        """
        logger.info(f"🖥️ Выполняется команда: {command}")
        
        try:
            # Безопасная обработка команды
            if not command or not command.strip():
                return {
                    "success": False,
                    "error": "Пустая команда",
                    "stdout": "",
                    "stderr": ""
                }
            
            command = command.strip()
            
            # Проверяем на потенциально опасные команды
            dangerous_commands = ['rm -rf /', 'format', 'del /f /s /q', 'shutdown', 'reboot']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                logger.warning(f"⚠️ Заблокирована потенциально опасная команда: {command}")
                return {
                    "success": False,
                    "error": "Команда заблокирована из соображений безопасности",
                    "stdout": "",
                    "stderr": ""
                }
            
            # Выполняем команду с таймаутом
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            logger.info(f"✅ Команда выполнена. Код возврата: {result.returncode}")
            logger.debug(f"STDOUT: {stdout[:200]}{'...' if len(stdout) > 200 else ''}")
            logger.debug(f"STDERR: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Таймаут при выполнении команды: {command}")
            return {
                "success": False,
                "error": f"Таймаут ({timeout}s) при выполнении команды",
                "stdout": "",
                "stderr": "",
                "command": command
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении команды '{command}': {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "command": command
            }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Публичный метод для выполнения команды через MCP интерфейс
        """
        command = params.get('command', '')
        timeout = params.get('timeout', 30)
        
        if not isinstance(command, str):
            return {
                "success": False,
                "error": "Параметр 'command' должен быть строкой"
            }
        
        return self._run(command, timeout)