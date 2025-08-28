"""
Неограниченный инструмент для работы с файловой системой для AI ассистента.
Предоставляет полный доступ к файловой системе без ограничений безопасности.

ВНИМАНИЕ: Этот инструмент предоставляет полный доступ к файловой системе.
Используйте только в доверенной среде!
"""

import os
import shutil
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field


class FileSystemToolSchema(BaseModel):
    """Схема для инструмента файловой системы"""
    operation: str = Field(..., description="Операция: read, write, create, delete, list, execute, search, copy, move")
    path: str = Field(..., description="Путь к файлу или директории")
    content: Optional[str] = Field(None, description="Содержимое для записи (для write/create)")
    destination: Optional[str] = Field(None, description="Путь назначения (для copy/move)")
    command: Optional[str] = Field(None, description="Команда для выполнения (для execute)")
    pattern: Optional[str] = Field(None, description="Паттерн для поиска (для search)")
    recursive: bool = Field(False, description="Рекурсивный поиск/операция")
    encoding: str = Field("utf-8", description="Кодировка файла")


class UnrestrictedFileSystemTool(BaseTool):
    """
    Неограниченный инструмент для работы с файловой системой.
    Предоставляет полный доступ к файловой системе без ограничений безопасности.
    """
    
    name: str = "unrestricted_filesystem_tool"
    description: str = """
    Мощный инструмент для работы с файловой системой без ограничений безопасности.
    
    Поддерживаемые операции:
    - read: Чтение файла
    - write: Запись в файл (перезапись)
    - create: Создание нового файла/директории
    - delete: Удаление файла/директории
    - list: Список файлов в директории
    - execute: Выполнение команд системы
    - search: Поиск файлов по паттерну
    - copy: Копирование файлов/директорий
    - move: Перемещение файлов/директорий
    
    Примеры использования:
    - {"operation": "read", "path": "/path/to/file.txt"}
    - {"operation": "write", "path": "/path/to/file.txt", "content": "Hello World"}
    - {"operation": "execute", "command": "ls -la /tmp"}
    - {"operation": "search", "path": "/home", "pattern": "*.py", "recursive": true}
    """
    args_schema: type[BaseModel] = FileSystemToolSchema

    def _run(self, **kwargs) -> str:
        """Выполняет операцию с файловой системой"""
        try:
            operation = kwargs.get('operation')
            path = kwargs.get('path')
            
            if operation == 'read':
                return self._read_file(path, kwargs.get('encoding', 'utf-8'))
            elif operation == 'write':
                return self._write_file(path, kwargs.get('content', ''), kwargs.get('encoding', 'utf-8'))
            elif operation == 'create':
                return self._create_path(path, kwargs.get('content'))
            elif operation == 'delete':
                return self._delete_path(path)
            elif operation == 'list':
                return self._list_directory(path, kwargs.get('recursive', False))
            elif operation == 'execute':
                return self._execute_command(kwargs.get('command'))
            elif operation == 'search':
                return self._search_files(path, kwargs.get('pattern'), kwargs.get('recursive', False))
            elif operation == 'copy':
                return self._copy_path(path, kwargs.get('destination'))
            elif operation == 'move':
                return self._move_path(path, kwargs.get('destination'))
            else:
                return f"Неизвестная операция: {operation}"
                
        except Exception as e:
            return f"Ошибка выполнения операции: {str(e)}"

    def _read_file(self, path: str, encoding: str = 'utf-8') -> str:
        """Читает содержимое файла"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            return f"Содержимое файла {path}:\n{content}"
        except Exception as e:
            return f"Ошибка чтения файла {path}: {str(e)}"

    def _write_file(self, path: str, content: str, encoding: str = 'utf-8') -> str:
        """Записывает содержимое в файл"""
        try:
            # Создаем директории если не существуют
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return f"Файл {path} успешно записан ({len(content)} символов)"
        except Exception as e:
            return f"Ошибка записи файла {path}: {str(e)}"

    def _create_path(self, path: str, content: Optional[str] = None) -> str:
        """Создает файл или директорию"""
        try:
            path_obj = Path(path)
            
            if content is not None:
                # Создаем файл с содержимым
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content, encoding='utf-8')
                return f"Файл {path} создан с содержимым"
            else:
                # Создаем директорию
                path_obj.mkdir(parents=True, exist_ok=True)
                return f"Директория {path} создана"
        except Exception as e:
            return f"Ошибка создания {path}: {str(e)}"

    def _delete_path(self, path: str) -> str:
        """Удаляет файл или директорию"""
        try:
            path_obj = Path(path)
            
            if path_obj.is_file():
                path_obj.unlink()
                return f"Файл {path} удален"
            elif path_obj.is_dir():
                shutil.rmtree(path)
                return f"Директория {path} удалена"
            else:
                return f"Путь {path} не существует"
        except Exception as e:
            return f"Ошибка удаления {path}: {str(e)}"

    def _list_directory(self, path: str, recursive: bool = False) -> str:
        """Выводит список файлов в директории"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return f"Путь {path} не существует"
            
            if not path_obj.is_dir():
                return f"Путь {path} не является директорией"
            
            files = []
            
            if recursive:
                for item in path_obj.rglob('*'):
                    files.append(str(item))
            else:
                for item in path_obj.iterdir():
                    files.append(str(item))
            
            files.sort()
            return f"Содержимое {path}:\n" + "\n".join(files)
            
        except Exception as e:
            return f"Ошибка чтения директории {path}: {str(e)}"

    def _execute_command(self, command: str) -> str:
        """Выполняет системную команду"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Команда: {command}\n"
            output += f"Код возврата: {result.returncode}\n"
            
            if result.stdout:
                output += f"Вывод:\n{result.stdout}\n"
            
            if result.stderr:
                output += f"Ошибки:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Команда {command} превысила таймаут (30 сек)"
        except Exception as e:
            return f"Ошибка выполнения команды {command}: {str(e)}"

    def _search_files(self, path: str, pattern: str, recursive: bool = False) -> str:
        """Ищет файлы по паттерну"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return f"Путь {path} не существует"
            
            files = []
            
            if recursive:
                files = list(path_obj.rglob(pattern))
            else:
                files = list(path_obj.glob(pattern))
            
            files = [str(f) for f in files]
            files.sort()
            
            return f"Найдено {len(files)} файлов по паттерну '{pattern}' в {path}:\n" + "\n".join(files)
            
        except Exception as e:
            return f"Ошибка поиска файлов: {str(e)}"

    def _copy_path(self, source: str, destination: str) -> str:
        """Копирует файл или директорию"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return f"Источник {source} не существует"
            
            if source_path.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                return f"Файл {source} скопирован в {destination}"
            elif source_path.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
                return f"Директория {source} скопирована в {destination}"
            
        except Exception as e:
            return f"Ошибка копирования {source} в {destination}: {str(e)}"

    def _move_path(self, source: str, destination: str) -> str:
        """Перемещает файл или директорию"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return f"Источник {source} не существует"
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, destination)
            return f"Путь {source} перемещен в {destination}"
            
        except Exception as e:
            return f"Ошибка перемещения {source} в {destination}: {str(e)}"


# Создаем экземпляр инструмента для использования
unrestricted_filesystem_tool = UnrestrictedFileSystemTool()