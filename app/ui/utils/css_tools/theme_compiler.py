#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Компилятор тем для GopiAI.
Интегрирует систему цветов с QSS файлами тем и создает готовые темы для приложения.
"""

import os
import sys
import re
import argparse
from pathlib import Path

# Пытаемся импортировать систему цветов (только если запущено из проекта)
try:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from app.ui.themes.color_system import ColorSystem
    color_system_available = True
except ImportError:
    color_system_available = False
    print("Предупреждение: Система цветов не доступна. Будет использован базовый режим.")


def find_theme_files(themes_dir):
    """
    Находит все файлы темы в указанной директории.

    Args:
        themes_dir: Путь к директории с темами

    Returns:
        dict: Словарь файлов тем в формате {theme_name: {qss: path, vars: path}}
    """
    theme_files = {}

    for root, dirs, files in os.walk(themes_dir):
        for file in files:
            if file.endswith(('-theme.qss', '-theme.css')):
                theme_name = file.split('-')[0].lower()  # Извлекаем имя темы из имени файла

                if theme_name not in theme_files:
                    theme_files[theme_name] = {}

                theme_files[theme_name]['qss'] = os.path.join(root, file)

                # Ищем соответствующий файл переменных
                vars_file = os.path.join(root, f"{theme_name}-vars.qss")
                if os.path.exists(vars_file):
                    theme_files[theme_name]['vars'] = vars_file

    return theme_files


def compile_theme(qss_path, vars_path=None, output_path=None, color_theme=None):
    """
    Компилирует QSS файл темы с применением переменных цветов.

    Args:
        qss_path: Путь к QSS файлу темы
        vars_path: Путь к файлу с переменными цветов (опционально)
        output_path: Путь для сохранения скомпилированного файла
        color_theme: Тип темы ('light' или 'dark') для генерации переменных

    Returns:
        str: Путь к скомпилированному файлу или None в случае ошибки
    """
    try:
        # Читаем файл темы
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss_content = f.read()

        # Подготавливаем содержимое переменных
        vars_content = ""

        # Используем систему цветов, если доступна
        if color_system_available and color_theme:
            # Генерируем переменные через систему цветов
            vars_content = ColorSystem.instance().generate_css_variables(color_theme)
        elif vars_path and os.path.exists(vars_path):
            # Читаем файл переменных, если доступен
            with open(vars_path, 'r', encoding='utf-8') as f:
                vars_content = f.read()

        # Компилируем тему
        compiled_content = vars_content + "\n" + qss_content

        # Определяем путь для сохранения
        if not output_path:
            output_dir = os.path.dirname(qss_path)
            file_name = os.path.basename(qss_path)
            output_path = os.path.join(output_dir, f"compiled-{file_name}")

        # Сохраняем скомпилированный файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compiled_content)

        print(f"Тема скомпилирована: {output_path}")
        return output_path

    except Exception as e:
        print(f"Ошибка при компиляции темы: {str(e)}")
        return None


def fix_qss_paths(qss_path, output_path=None):
    """
    Исправляет пути в QSS файле для корректной работы приложения.

    Args:
        qss_path: Путь к QSS файлу
        output_path: Путь для сохранения исправленного файла

    Returns:
        str: Путь к исправленному файлу или None в случае ошибки
    """
    try:
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss_content = f.read()

        # Исправляем пути к ресурсам
        # Заменяем относительные пути на алиасы ресурсов
        qss_content = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', lambda m: fix_resource_path(m.group(1)), qss_content)

        # Определяем путь для сохранения
        if not output_path:
            output_dir = os.path.dirname(qss_path)
            file_name = os.path.basename(qss_path)
            output_path = os.path.join(output_dir, f"fixed-{file_name}")

        # Сохраняем исправленный файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(qss_content)

        print(f"Пути в QSS исправлены: {output_path}")
        return output_path

    except Exception as e:
        print(f"Ошибка при исправлении путей в QSS: {str(e)}")
        return None


def fix_resource_path(path):
    """
    Исправляет путь к ресурсу в QSS файле.

    Args:
        path: Исходный путь к ресурсу

    Returns:
        str: Исправленный путь
    """
    # Если путь уже начинается с ':/' (алиас ресурса), оставляем как есть
    if path.startswith(':/'):
        return f"url({path})"

    # Для иконок используем алиас ресурсов
    if 'icons/' in path:
        icon_name = os.path.basename(path)
        return f"url(:/icons/{icon_name})"

    # Для шрифтов используем алиас ресурсов или прямой путь
    if 'fonts/' in path:
        font_path = path.split('fonts/')[1]
        return f"url(:/fonts/{font_path})"

    # Для остальных ресурсов оставляем как есть
    return f"url({path})"


def compile_all_themes(themes_dir, output_dir=None):
    """
    Компилирует все темы в указанной директории.

    Args:
        themes_dir: Путь к директории с темами
        output_dir: Директория для сохранения скомпилированных тем

    Returns:
        dict: Словарь с путями к скомпилированным темам
    """
    # Находим файлы тем
    theme_files = find_theme_files(themes_dir)

    # Создаем выходную директорию, если указана
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Компилируем каждую тему
    compiled_themes = {}

    for theme_name, files in theme_files.items():
        if 'qss' not in files:
            continue

        qss_path = files['qss']
        vars_path = files.get('vars')

        # Определяем тип темы для генерации переменных
        color_theme = "light" if theme_name == "light" else "dark"

        # Определяем путь для сохранения
        if output_dir:
            output_path = os.path.join(output_dir, f"{theme_name}-theme.qss")
        else:
            output_path = None

        # Компилируем тему
        compiled_path = compile_theme(qss_path, vars_path, output_path, color_theme)

        if compiled_path:
            # Исправляем пути
            fixed_path = fix_qss_paths(compiled_path)
            if fixed_path:
                compiled_themes[theme_name] = fixed_path

    return compiled_themes


def generate_theme_vars(themes_dir, output_dir=None):
    """
    Генерирует файлы с переменными цветов для всех тем.

    Args:
        themes_dir: Путь к директории с темами
        output_dir: Директория для сохранения файлов переменных

    Returns:
        dict: Словарь с путями к файлам переменных
    """
    if not color_system_available:
        print("Система цветов не доступна. Невозможно сгенерировать переменные.")
        return {}

    # Создаем выходную директорию, если указана
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = themes_dir

    # Генерируем переменные для каждого типа темы
    generated_vars = {}

    for theme_type in ["light", "dark"]:
        # Определяем путь для сохранения
        output_path = os.path.join(output_dir, f"{theme_type}-vars.qss")

        # Генерируем и сохраняем переменные
        if ColorSystem.instance().save_css_variables(output_path, theme_type):
            generated_vars[theme_type] = output_path

    return generated_vars


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Компилятор тем для GopiAI")
    parser.add_argument("--themes-dir", "-d", default="app/ui/themes", help="Директория с темами")
    parser.add_argument("--output-dir", "-o", help="Директория для сохранения скомпилированных тем")
    parser.add_argument("--compile-all", "-a", action="store_true", help="Скомпилировать все темы")
    parser.add_argument("--generate-vars", "-g", action="store_true", help="Сгенерировать файлы переменных цветов")
    parser.add_argument("--fix-paths", "-f", action="store_true", help="Исправить пути в QSS файлах")
    parser.add_argument("--qss-file", "-q", help="Путь к отдельному QSS файлу для компиляции")
    parser.add_argument("--vars-file", "-v", help="Путь к файлу с переменными цветов")

    args = parser.parse_args()

    # Если запуск без аргументов, печатаем помощь
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Компилировать один файл
    if args.qss_file:
        output_path = args.output_dir and os.path.join(args.output_dir, os.path.basename(args.qss_file)) or None

        # Исправляем пути, если нужно
        if args.fix_paths:
            fix_qss_paths(args.qss_file, output_path)
        else:
            # Определяем тип темы по имени файла
            theme_type = "light" if "light" in args.qss_file.lower() else "dark"
            compile_theme(args.qss_file, args.vars_file, output_path, theme_type)

    # Генерировать файлы переменных
    elif args.generate_vars:
        generate_theme_vars(args.themes_dir, args.output_dir)

    # Компилировать все темы
    elif args.compile_all:
        compile_all_themes(args.themes_dir, args.output_dir)


if __name__ == "__main__":
    main()
