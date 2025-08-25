"""
Простой исполнитель кода без ограничений
"""

import subprocess
import sys
import os
import tempfile
import json
from typing import Dict, Any, List, Optional


class SimpleCodeExecutor:
    """Простой исполнитель кода без ограничений безопасности"""
    
    def __init__(self):
        self.name = "simple_code_executor"
        self.description = "Инструмент для выполнения кода без ограничений"
    
    def execute_python(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Выполняет Python код"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Выполняем код
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "timeout": timeout
                }
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(temp_file)
                except (OSError, IOError):
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Код выполнялся дольше {timeout} секунд",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timeout": False
            }
    
    def execute_shell(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Выполняет shell команду"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "timeout": timeout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Команда выполнялась дольше {timeout} секунд",
                "command": command,
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "timeout": False
            }
    
    def execute_script(self, script_path: str, args: List[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Выполняет скрипт"""
        try:
            if args is None:
                args = []
            
            # Определяем интерпретатор по расширению
            if script_path.endswith('.py'):
                cmd = [sys.executable, script_path] + args
            elif script_path.endswith('.sh'):
                cmd = ['bash', script_path] + args
            elif script_path.endswith('.js'):
                cmd = ['node', script_path] + args
            else:
                # Пытаемся выполнить как исполняемый файл
                cmd = [script_path] + args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "script_path": script_path,
                "args": args,
                "timeout": timeout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Скрипт выполнялся дольше {timeout} секунд",
                "script_path": script_path,
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "script_path": script_path,
                "timeout": False
            }
    
    def install_package(self, package_name: str, use_pip: bool = True) -> Dict[str, Any]:
        """Устанавливает пакет"""
        try:
            if use_pip:
                cmd = [sys.executable, '-m', 'pip', 'install', package_name]
            else:
                cmd = ['apt-get', 'install', '-y', package_name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут на установку
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "package": package_name,
                "installer": "pip" if use_pip else "apt-get"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Установка пакета заняла слишком много времени",
                "package": package_name,
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "package": package_name,
                "timeout": False
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получает информацию о системе"""
        try:
            import platform
            
            return {
                "success": True,
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "python_executable": sys.executable,
                "current_directory": os.getcwd(),
                "environment_variables": dict(os.environ)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }