#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для компиляции всех тем GopiAI после исправления дублирующихся селекторов.
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

try:
    # Импортируем функции из локального theme_compiler.py
    from app.ui.utils.css_tools.theme_compiler import compile_all_themes, fix_qss_paths
except ImportError:
    try:
        # Пытаемся импортировать функции из локального модуля
        from .theme_compiler import compile_all_themes, fix_qss_paths
    except ImportError:
        print("Ошибка: Не удалось импортировать функции из theme_compiler.py")
        sys.exit(1)

def main():
    """
    Основная функция скрипта.
    """
    # Путь к корневой директории проекта
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

    # Пути относительно корневой директории
    themes_dir = os.path.join(root_dir, 'app', 'ui', 'themes')
    output_dir = os.path.join(themes_dir, 'compiled')

    # Создаем директорию для скомпилированных тем, если ее нет
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Компилируем все темы
    print(f"Компиляция тем из {themes_dir} в {output_dir}...")
    compiled_themes = compile_all_themes(themes_dir, output_dir)

    if compiled_themes:
        print(f"Скомпилировано {len(compiled_themes)} тем:")
        for theme_name, path in compiled_themes.items():
            print(f"  - {theme_name}: {path}")

            # Исправляем пути в скомпилированных темах
            fixed_path = fix_qss_paths(path, os.path.join(output_dir, f"fixed-{theme_name}-theme.qss"))
            if fixed_path:
                print(f"    Исправлены пути: {fixed_path}")
    else:
        print("Темы не скомпилированы. Проверьте наличие файлов тем.")

if __name__ == "__main__":
    main()
