#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для проверки доступности инструментов Serena через Python API.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.abspath('.'))

def check_serena_tools():
    """Проверяет доступность инструментов Serena."""
    print("Проверка доступности инструментов Serena...")
    
    try:
        # Проверяем наличие директории .serena
        serena_dir = Path('.serena')
        if serena_dir.exists() and serena_dir.is_dir():
            print(f"Директория .serena найдена: {serena_dir.absolute()}")
            
            # Проверяем наличие файла project.yml
            project_yml = serena_dir / 'project.yml'
            if project_yml.exists() and project_yml.is_file():
                print(f"Файл project.yml найден: {project_yml.absolute()}")
            else:
                print("Файл project.yml не найден")
                
            # Проверяем наличие директории memories
            memories_dir = serena_dir / 'memories'
            if memories_dir.exists() and memories_dir.is_dir():
                print(f"Директория memories найдена: {memories_dir.absolute()}")
                
                # Выводим список файлов в директории memories
                memory_files = list(memories_dir.glob('*'))
                if memory_files:
                    print(f"Найдено {len(memory_files)} файлов памяти:")
                    for file in memory_files:
                        print(f"  - {file.name}")
                else:
                    print("Файлы памяти не найдены")
            else:
                print("Директория memories не найдена")
        else:
            print("Директория .serena не найдена")
            
        # Проверяем наличие пакета serena-mcp-server
        try:
            import importlib.metadata
            try:
                version = importlib.metadata.version('serena-mcp-server')
                print(f"Пакет serena-mcp-server установлен, версия: {version}")
            except importlib.metadata.PackageNotFoundError:
                print("Пакет serena-mcp-server не установлен")
        except ImportError:
            print("Не удалось проверить наличие пакета serena-mcp-server")
        
        # Проверяем наличие пакета mcp
        try:
            import importlib.metadata
            try:
                version = importlib.metadata.version('mcp')
                print(f"Пакет mcp установлен, версия: {version}")
            except importlib.metadata.PackageNotFoundError:
                print("Пакет mcp не установлен")
        except ImportError:
            print("Не удалось проверить наличие пакета mcp")
            
    except Exception as e:
        print(f"Ошибка при проверке инструментов Serena: {e}")

if __name__ == "__main__":
    check_serena_tools() 