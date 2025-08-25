"""
Простой инструмент для работы с файловой системой без ограничений
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class SimpleFileSystemTool:
    """Простой инструмент для работы с файловой системой без ограничений безопасности"""
    
    def __init__(self):
        self.name = "simple_filesystem_tool"
        self.description = "Инструмент для работы с файловой системой без ограничений"
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Читает содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def write_file(self, file_path: str, content: str, mode: str = 'w') -> Dict[str, Any]:
        """Записывает содержимое в файл"""
        try:
            # Создаем директории если не существуют
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "mode": mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def list_directory(self, directory_path: str) -> Dict[str, Any]:
        """Получает список файлов и папок в директории"""
        try:
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                items.append({
                    "name": item,
                    "path": item_path,
                    "is_file": os.path.isfile(item_path),
                    "is_directory": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                "success": True,
                "directory": directory_path,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory_path
            }
    
    def create_directory(self, directory_path: str) -> Dict[str, Any]:
        """Создает директорию"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return {
                "success": True,
                "directory": directory_path,
                "created": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory_path
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Удаляет файл"""
        try:
            os.remove(file_path)
            return {
                "success": True,
                "file_path": file_path,
                "deleted": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def delete_directory(self, directory_path: str) -> Dict[str, Any]:
        """Удаляет директорию"""
        try:
            shutil.rmtree(directory_path)
            return {
                "success": True,
                "directory": directory_path,
                "deleted": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory_path
            }
    
    def copy_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Копирует файл"""
        try:
            # Создаем директории если не существуют
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copy2(source_path, destination_path)
            
            return {
                "success": True,
                "source": source_path,
                "destination": destination_path,
                "copied": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": source_path,
                "destination": destination_path
            }
    
    def move_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Перемещает файл"""
        try:
            # Создаем директории если не существуют
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.move(source_path, destination_path)
            
            return {
                "success": True,
                "source": source_path,
                "destination": destination_path,
                "moved": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": source_path,
                "destination": destination_path
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Получает информацию о файле"""
        try:
            stat = os.stat(file_path)
            return {
                "success": True,
                "file_path": file_path,
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "exists": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "exists": False
            }