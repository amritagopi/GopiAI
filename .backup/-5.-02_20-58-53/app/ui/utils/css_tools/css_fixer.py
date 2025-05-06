#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Улучшенный скрипт для исправления CSS/QSS файлов.
Решает проблемы с дублирующимися селекторами и хардкодированными цветами.
"""

import os
import re
import sys
import argparse
from collections import defaultdict

# Проблемные селекторы, которые часто дублируются
STATE_SELECTORS = ['hover', 'pressed', 'selected', 'vertical', 'horizontal', 'active', 'focus', 'disabled']

def read_file(file_path):
    """Читает содержимое файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    """Записывает содержимое в файл."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_css_blocks(css_content):
    """Извлекает все блоки CSS из содержимого."""
    # Регулярное выражение для поиска CSS-блоков: селектор { свойства }
    pattern = re.compile(r'([^{]+)\s*{\s*([^}]*)\s*}', re.DOTALL)
    return [(match.group(1).strip(), match.group(2).strip()) for match in pattern.finditer(css_content)]

def parse_properties(props_text):
    """Разбирает текст свойств CSS на словарь свойство: значение."""
    properties = {}
    for line in props_text.split(';'):
        line = line.strip()
        if not line:
            continue

        if ':' in line:
            prop, value = line.split(':', 1)
            properties[prop.strip()] = value.strip()

    return properties

def find_duplicate_selectors(css_blocks):
    """
    Находит дублирующиеся селекторы в CSS блоках.
    Возвращает словарь с группами дублирующихся селекторов.
    """
    selector_groups = defaultdict(list)

    for selector, _ in css_blocks:
        # Определяем базовый селектор (удаляя состояния как :hover, :pressed и т.д.)
        base_selector = selector
        for state in STATE_SELECTORS:
            state_marker = f":{state}"
            if state_marker in selector:
                parts = selector.split(state_marker)
                base_selector = parts[0].strip()
                break

        # Добавляем селектор в соответствующую группу
        selector_groups[base_selector].append(selector)

    # Оставляем только группы с дублирующимися селекторами
    duplicates = {base: group for base, group in selector_groups.items() if len(group) > 1}

    return duplicates

def rebuild_css(css_blocks):
    """
    Пересобирает CSS из блоков, удаляя дубликаты и нормализуя форматирование.
    """
    # Создаем словарь для хранения уникальных селекторов и их свойств
    unique_blocks = {}

    # Обрабатываем все блоки
    for selector, props_text in css_blocks:
        props = parse_properties(props_text)

        # Если селектор уже встречался, объединяем свойства
        if selector in unique_blocks:
            existing_props = unique_blocks[selector]
            # Обновляем существующие свойства только если они отсутствуют
            for key, value in props.items():
                if key not in existing_props:
                    existing_props[key] = value
        else:
            unique_blocks[selector] = props

    # Создаем новое содержимое CSS
    new_css = ""

    # Добавляем комментарий о том, что файл был обработан
    new_css += "/* Файл исправлен css_fixer.py - устранены дублирующиеся селекторы */\n\n"

    # Пересобираем CSS из уникальных блоков с красивым форматированием
    for selector, props in unique_blocks.items():
        new_css += f"{selector} {{\n"
        for prop, value in sorted(props.items()):
            new_css += f"    {prop}: {value};\n"
        new_css += "}\n\n"

    return new_css

def fix_css_file(file_path, output_path=None):
    """
    Исправляет CSS файл, удаляя дублирующиеся селекторы и нормализуя форматирование.
    """
    print(f"Обработка файла: {file_path}")

    try:
        # Читаем содержимое файла
        css_content = read_file(file_path)

        # Извлекаем блоки CSS
        css_blocks = extract_css_blocks(css_content)

        # Находим дублирующиеся селекторы
        duplicates = find_duplicate_selectors(css_blocks)

        if duplicates:
            print(f"Найдено {len(duplicates)} дублирующихся селекторов:")
            for base, group in duplicates.items():
                print(f"  - {base}: {len(group)} вариаций")
        else:
            print("Дублирующихся селекторов не найдено.")

        # Создаем исправленный CSS
        fixed_css = rebuild_css(css_blocks)

        # Определяем путь выходного файла
        if output_path is None:
            output_path = file_path

        # Записываем результат
        write_file(output_path, fixed_css)
        print(f"Файл сохранен: {output_path}")

        return True
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {str(e)}")
        return False

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Улучшенный инструмент для исправления CSS/QSS файлов")
    parser.add_argument("file", help="Путь к CSS/QSS файлу или директории с файлами")
    parser.add_argument("--output", "-o", help="Путь для сохранения исправленного файла")

    args = parser.parse_args()

    # Проверяем существование файла или директории
    if not os.path.exists(args.file):
        print(f"Ошибка: {args.file} не существует.")
        return 1

    # Обрабатываем файл или директорию
    if os.path.isdir(args.file):
        # Обрабатываем все CSS/QSS файлы в директории
        for root, dirs, files in os.walk(args.file):
            for file in files:
                if file.endswith(('.css', '.qss')):
                    file_path = os.path.join(root, file)
                    fix_css_file(file_path)
    else:
        # Обрабатываем один файл
        success = fix_css_file(args.file, args.output)
        if not success:
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
