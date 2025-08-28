#!/usr/bin/env python3
"""
Скрипт для обновления импортов и sys.path в проекте.
Заменяет прямые модификации sys.path на использование path_manager.
"""

import os
import re
from pathlib import Path

def update_file(file_path):
    """Обновить импорты в одном файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли в файле модификации sys.path
    if 'sys.path.' not in content:
        return False
    
    # Ищем импорты в начале файла
    import_lines = []
    lines = content.splitlines()
    
    # Находим конец блока импортов
    import_end = 0
    for i, line in enumerate(lines):
        if not line.strip() or line.startswith(('import ', 'from ')):
            import_end = i + 1
        else:
            break
    
    # Проверяем, есть ли уже импорт path_manager
    has_path_manager = any('path_manager' in line for line in lines[:import_end])
    
    # Добавляем импорт path_manager, если его нет
    if not has_path_manager and import_end > 0:
        lines.insert(import_end, 'from path_manager import setup_project_paths')
        import_end += 1
    
    # Заменяем sys.path.* на использование path_manager
    new_lines = []
    modified = False
    
    for line in lines:
        if 'sys.path.' in line and 'path_manager' not in line:
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
                new_lines.append('    # Инициализируем пути проекта')
                new_lines.append('    path_manager = setup_project_paths()')
                modified = True
            # Пропускаем другие модификации sys.path
    # Заменено на использование path_manager: elif 'sys.path.append(' in line or 'sys.path.insert(' in line:
                new_lines.append(f'    # Заменено на использование path_manager: {line.strip()}')
                modified = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        # Записываем обновленное содержимое
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        return True
    
    return False

def main():
    """Основная функция"""
    project_root = Path(__file__).parent.parent
    updated_files = []
    
    # Ищем все Python файлы в проекте
    for root, _, files in os.walk(project_root):
        # Пропускаем виртуальные окружения и скрытые директории
        if any(part.startswith('.') or part == 'venv' or part == 'env' 
               for part in Path(root).parts):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    if update_file(file_path):
                        updated_files.append(file_path)
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    print(f"\nОбновлено {len(updated_files)} файлов:")
    for f in updated_files:
        print(f"- {f}")

if __name__ == "__main__":
    main()