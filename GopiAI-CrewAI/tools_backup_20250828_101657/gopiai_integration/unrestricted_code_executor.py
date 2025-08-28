"""
Неограниченный исполнитель кода для AI ассистента.
Предоставляет полный доступ к выполнению Python кода без ограничений безопасности.

ВНИМАНИЕ: Этот инструмент выполняет произвольный код без ограничений.
Используйте только в доверенной среде!
"""

import os
import sys
import subprocess
import tempfile
import traceback
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from crewai.tools.agent_tools import StructuredTool as BaseTool
from pydantic import BaseModel, Field
import json


class CodeExecutorSchema(BaseModel):
    """Схема для исполнителя кода"""
    code: str = Field(..., description="Python код для выполнения")
    language: str = Field("python", description="Язык программирования (python, bash, shell)")
    install_packages: List[str] = Field([], description="Пакеты для установки перед выполнением")
    working_directory: Optional[str] = Field(None, description="Рабочая директория для выполнения")
    timeout: int = Field(30, description="Таймаут выполнения в секундах")
    capture_output: bool = Field(True, description="Захватывать вывод")
    environment_vars: Dict[str, str] = Field({}, description="Переменные окружения")


class UnrestrictedCodeExecutor(BaseTool):
    """
    Неограниченный исполнитель кода без ограничений безопасности.
    Может выполнять Python код, bash команды и устанавливать пакеты.
    """
    
    name: str = "unrestricted_code_executor"
    description: str = """
    Мощный инструмент для выполнения кода без ограничений безопасности.
    
    Возможности:
    - Выполнение Python кода с полным доступом к системе
    - Выполнение bash/shell команд
    - Автоматическая установка Python пакетов
    - Работа с файловой системой
    - Доступ к сети и внешним ресурсам
    - Установка переменных окружения
    
    Примеры использования:
    - {"code": "print('Hello World')", "language": "python"}
    - {"code": "import requests; print(requests.get('https://api.github.com').status_code)"}
    - {"code": "ls -la", "language": "bash"}
    - {"code": "pip install numpy", "language": "bash"}
    """
    args_schema: type[BaseModel] = CodeExecutorSchema

    def _run(self, **kwargs) -> str:
        """Выполняет код"""
        try:
            code = kwargs.get('code')
            language = kwargs.get('language', 'python').lower()
            install_packages = kwargs.get('install_packages', [])
            working_directory = kwargs.get('working_directory')
            timeout = kwargs.get('timeout', 30)
            capture_output = kwargs.get('capture_output', True)
            environment_vars = kwargs.get('environment_vars', {})
            
            # Устанавливаем пакеты если нужно
            if install_packages:
                install_result = self._install_packages(install_packages)
                if "Ошибка" in install_result:
                    return install_result
            
            # Выполняем код в зависимости от языка
            if language == 'python':
                return self._execute_python_code(
                    code, working_directory, timeout, capture_output, environment_vars
                )
            elif language in ['bash', 'shell', 'sh']:
                return self._execute_shell_command(
                    code, working_directory, timeout, capture_output, environment_vars
                )
            else:
                return f"Неподдерживаемый язык: {language}"
                
        except Exception as e:
            return f"Ошибка выполнения кода: {str(e)}\n{traceback.format_exc()}"

    def _install_packages(self, packages: List[str]) -> str:
        """Устанавливает Python пакеты"""
        try:
            results = []
            for package in packages:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    results.append(f"✓ {package} установлен успешно")
                else:
                    results.append(f"✗ Ошибка установки {package}: {result.stderr}")
            
            return "Установка пакетов:\n" + "\n".join(results)
            
        except Exception as e:
            return f"Ошибка установки пакетов: {str(e)}"

    def _execute_python_code(
        self, 
        code: str, 
        working_directory: Optional[str] = None,
        timeout: int = 30,
        capture_output: bool = True,
        environment_vars: Dict[str, str] = None
    ) -> str:
        """Выполняет Python код"""
        try:
            # Подготавливаем окружение
            if working_directory:
                original_cwd = os.getcwd()
                os.chdir(working_directory)
            
            if environment_vars:
                for key, value in environment_vars.items():
                    os.environ[key] = value
            
            # Создаем глобальное и локальное пространство имен
            global_namespace = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__file__': '<string>',
                'os': os,
                'sys': sys,
                'subprocess': subprocess,
                'Path': Path,
                'json': json,
                'tempfile': tempfile,
            }
            
            local_namespace = {}
            
            # Перехватываем вывод если нужно
            if capture_output:
                from io import StringIO
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                stdout_capture = StringIO()
                stderr_capture = StringIO()
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
            
            try:
                # Выполняем код
                exec(code, global_namespace, local_namespace)
                
                # Получаем результат
                result = ""
                
                if capture_output:
                    stdout_content = stdout_capture.getvalue()
                    stderr_content = stderr_capture.getvalue()
                    
                    if stdout_content:
                        result += f"Вывод:\n{stdout_content}\n"
                    if stderr_content:
                        result += f"Ошибки:\n{stderr_content}\n"
                
                # Добавляем значение переменной result если есть
                if 'result' in local_namespace:
                    result += f"Результат: {local_namespace['result']}\n"
                
                # Показываем все переменные если нет вывода
                if not result.strip():
                    variables = {k: v for k, v in local_namespace.items() 
                               if not k.startswith('_')}
                    if variables:
                        result = f"Переменные: {variables}"
                    else:
                        result = "Код выполнен успешно (без вывода)"
                
                return result
                
            finally:
                if capture_output:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                if working_directory:
                    os.chdir(original_cwd)
            
        except Exception as e:
            return f"Ошибка выполнения Python кода: {str(e)}\n{traceback.format_exc()}"

    def _execute_shell_command(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout: int = 30,
        capture_output: bool = True,
        environment_vars: Dict[str, str] = None
    ) -> str:
        """Выполняет shell команду"""
        try:
            # Подготавливаем окружение
            env = os.environ.copy()
            if environment_vars:
                env.update(environment_vars)
            
            # Выполняем команду
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=working_directory,
                env=env
            )
            
            output = f"Команда: {command}\n"
            output += f"Код возврата: {result.returncode}\n"
            
            if result.stdout:
                output += f"Вывод:\n{result.stdout}\n"
            
            if result.stderr:
                output += f"Ошибки:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Команда '{command}' превысила таймаут ({timeout} сек)"
        except Exception as e:
            return f"Ошибка выполнения команды '{command}': {str(e)}"

    def execute_interactive_python(self, code: str) -> str:
        """Выполняет Python код в интерактивном режиме"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Выполняем файл
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = f"Выполнение Python скрипта:\n"
                output += f"Код возврата: {result.returncode}\n"
                
                if result.stdout:
                    output += f"Вывод:\n{result.stdout}\n"
                
                if result.stderr:
                    output += f"Ошибки:\n{result.stderr}\n"
                
                return output
                
            finally:
                # Удаляем временный файл
                os.unlink(temp_file)
                
        except Exception as e:
            return f"Ошибка выполнения интерактивного Python: {str(e)}"

    def install_and_import(self, package_name: str, import_name: Optional[str] = None) -> str:
        """Устанавливает пакет и импортирует его"""
        try:
            # Устанавливаем пакет
            install_result = self._install_packages([package_name])
            
            if "Ошибка" in install_result:
                return install_result
            
            # Пытаемся импортировать
            import_name = import_name or package_name
            
            try:
                module = importlib.import_module(import_name)
                return f"Пакет {package_name} установлен и импортирован как {import_name}"
            except ImportError as e:
                return f"Пакет {package_name} установлен, но не удалось импортировать {import_name}: {str(e)}"
                
        except Exception as e:
            return f"Ошибка установки и импорта {package_name}: {str(e)}"


# Создаем экземпляр инструмента для использования
unrestricted_code_executor = UnrestrictedCodeExecutor()