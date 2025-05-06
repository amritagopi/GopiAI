#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для очистки ненужных файлов из корневой директории проекта.
Перемещает утилиты CSS в централизованную директорию или удаляет их,
если они уже были перенесены.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import re

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

# Определяем файлы, которые следует очистить из корневой директории
FILES_TO_CLEAN = [
    'css_fixer.py',
    'css_refactor.py',
    'fix_duplicate_selectors.py',
    'fonts_fixer.py',
    'theme_compiler.py',
    'compile_themes.py',
    'fix_all_css.bat',
    'fix_all_css_final.bat',
    'fix_themes.bat'
]

# Особые файлы, которые требуют дополнительной обработки
SPECIAL_FILES = {
    'theme_manager.py': 'app/ui/utils',  # Переместить theme_manager.py в app/ui/utils
    'simple_ui_auditor_final.py': 'app/ui/utils'  # Переместить simple_ui_auditor_final.py в app/ui/utils
}

# Временные или устаревшие файлы, которые можно удалить
TEMP_FILES = [
    'ui_debug.log',
    'spa-log.txt',
    'translation_diagnostics.py',
    'simple_ui_auditor.py'
]

def cleanup_files(files_list, root_dir, target_dir=None, force=False):
    """
    Очищает указанные файлы из корневой директории.
    Если target_dir указан, файлы будут перемещены туда, иначе - удалены.

    Args:
        files_list: Список файлов для очистки
        root_dir: Корневая директория проекта
        target_dir: Директория для перемещения файлов (если None, файлы удаляются)
        force: Принудительно удалить файлы, даже если они уже есть в target_dir
    """
    for filename in files_list:
        source_path = os.path.join(root_dir, filename)

        if not os.path.exists(source_path):
            print(f"Файл {filename} не найден.")
            continue

        if target_dir:
            target_path = os.path.join(target_dir, filename)

            # Проверяем, существует ли файл в целевой директории
            if os.path.exists(target_path) and not force:
                print(f"Файл {filename} уже существует в целевой директории. Удаляем оригинал.")
                os.remove(source_path)
            else:
                # Перемещаем файл
                print(f"Перемещаем {filename} в {target_dir}")
                try:
                    shutil.copy2(source_path, target_path)
                    os.remove(source_path)
                except Exception as e:
                    print(f"Ошибка при перемещении {filename}: {str(e)}")
        else:
            # Удаляем файл
            print(f"Удаляем {filename}")
            try:
                os.remove(source_path)
            except Exception as e:
                print(f"Ошибка при удалении {filename}: {str(e)}")

def handle_special_files(root_dir, force=False):
    """
    Обрабатывает особые файлы, которые требуют специального перемещения.

    Args:
        root_dir: Корневая директория проекта
        force: Принудительно заменить существующие файлы
    """
    for filename, target_subdir in SPECIAL_FILES.items():
        source_path = os.path.join(root_dir, filename)

        if not os.path.exists(source_path):
            print(f"Файл {filename} не найден.")
            continue

        target_dir = os.path.join(root_dir, target_subdir)
        target_path = os.path.join(target_dir, filename)

        # Создаем целевую директорию, если она не существует
        os.makedirs(target_dir, exist_ok=True)

        # Проверяем, существует ли файл в целевой директории
        if os.path.exists(target_path) and not force:
            # Если файл theme_manager.py, проведем проверку версий
            if filename == 'theme_manager.py':
                if is_newer_theme_manager(source_path, target_path):
                    print(f"Файл {filename} в целевой директории устарел. Обновляем его.")
                    backup_and_update_file(source_path, target_path)
                else:
                    print(f"Файл {filename} уже существует в целевой директории и актуален. Удаляем оригинал.")
                    os.remove(source_path)
            else:
                print(f"Файл {filename} уже существует в целевой директории. Удаляем оригинал.")
                os.remove(source_path)
        else:
            # Перемещаем файл
            print(f"Перемещаем {filename} в {target_dir}")
            try:
                shutil.copy2(source_path, target_path)
                os.remove(source_path)
            except Exception as e:
                print(f"Ошибка при перемещении {filename}: {str(e)}")

def is_newer_theme_manager(source_path, target_path):
    """
    Проверяет, является ли исходный файл theme_manager.py более новой версией.

    Args:
        source_path: Путь к исходному файлу
        target_path: Путь к целевому файлу

    Returns:
        bool: True, если исходный файл новее
    """
    # Простая проверка по времени модификации
    source_time = os.path.getmtime(source_path)
    target_time = os.path.getmtime(target_path)

    return source_time > target_time

def backup_and_update_file(source_path, target_path):
    """
    Создает резервную копию целевого файла и обновляет его.

    Args:
        source_path: Путь к исходному файлу
        target_path: Путь к целевому файлу
    """
    backup_path = f"{target_path}.bak"
    try:
        # Создаем резервную копию
        shutil.copy2(target_path, backup_path)
        print(f"Создана резервная копия: {backup_path}")

        # Обновляем файл
        shutil.copy2(source_path, target_path)
        os.remove(source_path)
        print(f"Файл {os.path.basename(source_path)} успешно обновлен.")
    except Exception as e:
        print(f"Ошибка при обновлении файла: {str(e)}")

def find_temp_files(root_dir, extensions=None):
    """
    Ищет временные файлы в проекте на основе расширений файлов.

    Args:
        root_dir: Корневая директория проекта
        extensions: Список расширений временных файлов

    Returns:
        list: Список найденных временных файлов
    """
    if extensions is None:
        extensions = ['.tmp', '.bak', '.log', '.pyc']

    temp_files = []

    for root, dirs, files in os.walk(root_dir):
        # Пропускаем директории venv и .git
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                temp_files.append(os.path.join(root, file))

    return temp_files

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Очистка ненужных файлов из проекта")
    parser.add_argument("--move", "-m", action="store_true", help="Переместить файлы вместо удаления")
    parser.add_argument("--temp", "-t", action="store_true", help="Найти и удалить временные файлы")
    parser.add_argument("--force", "-f", action="store_true", help="Принудительно переместить/удалить файлы")

    args = parser.parse_args()

    # Определяем пути
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    target_dir = os.path.dirname(__file__) if args.move else None

    print(f"Рабочая директория: {root_dir}")
    if target_dir:
        print(f"Целевая директория: {target_dir}")

    # Обрабатываем особые файлы
    print("\nОбработка специальных файлов...")
    handle_special_files(root_dir, args.force)

    # Очищаем CSS утилиты
    print("\nОчистка CSS-утилит...")
    cleanup_files(FILES_TO_CLEAN, root_dir, target_dir, args.force)

    # Очищаем временные файлы
    if args.temp:
        print("\nПоиск временных файлов...")
        temp_files = find_temp_files(root_dir)

        if temp_files:
            print(f"Найдено {len(temp_files)} временных файлов:")
            for file in temp_files:
                print(f"  - {os.path.relpath(file, root_dir)}")

            if input("\nУдалить эти файлы? (y/n): ").lower() == 'y':
                for file in temp_files:
                    try:
                        os.remove(file)
                        print(f"Удален: {os.path.relpath(file, root_dir)}")
                    except Exception as e:
                        print(f"Ошибка при удалении {file}: {str(e)}")
        else:
            print("Временных файлов не найдено.")

    # Очищаем известные устаревшие файлы
    print("\nОчистка известных устаревших файлов...")
    cleanup_files(TEMP_FILES, root_dir, None, args.force)

    print("\nОчистка завершена!")

if __name__ == "__main__":
    main()
