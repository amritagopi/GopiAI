#!/usr/bin/env python3
"""
Скрипт для исправления относительных импортов на абсолютные.
"""

import os
import re

def fix_imports_in_file(file_path):
    """Исправляет относительные импорты в файле."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем относительные импорты на абсолютные
        content = re.sub(r'from \.error_handler import error_handler', 'from error_handler import error_handler', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Исправлены импорты в {file_path}")
        
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")

def main():
    """Основная функция."""
    files_to_fix = [
        'command_executor.py',
        'smart_delegator.py'
    ]
    
    for file_name in files_to_fix:
        if os.path.exists(file_name):
            fix_imports_in_file(file_name)
        else:
            print(f"Файл {file_name} не найден")

if __name__ == '__main__':
    main()