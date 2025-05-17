#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Улучшенный скрипт для устранения дублирующихся селекторов в CSS/QSS файлах.
Обнаруживает и объединяет селекторы hover, pressed, selected, vertical, horizontal и другие.
"""

import os
import re
import sys
import argparse
from collections import defaultdict

# Проблемные селекторы, которые часто дублируются
PROBLEMATIC_SELECTORS = ['hover', 'pressed', 'selected', 'vertical', 'horizontal', 'active', 'focus', 'disabled']
# Игнорируемые паттерны, которые нормально использовать многократно
IGNORED_PATTERNS = ['@font-face']

def read_file(file_path):
    """Читает содержимое файла."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    """Записывает содержимое в файл."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_style_blocks(content):
    """Извлекает все блоки стилей из CSS/QSS."""
    # Паттерн для поиска CSS-блоков: селектор { свойства }
    pattern = re.compile(r'([^{]+){\s*([^}]*)\s*}', re.DOTALL)
    return [(match.group(1).strip(), match.group(2).strip()) for match in pattern.finditer(content)]

def find_duplicate_selectors(content):
    """Находит дублирующиеся селекторы в CSS."""
    selectors = re.findall(r'([^{]+)\s*\{', content)
    # Очищаем селекторы от пробелов
    selectors = [s.strip() for s in selectors]

    # Отфильтровываем игнорируемые паттерны
    filtered_selectors = []
    for selector in selectors:
        if not any(ignored in selector for ignored in IGNORED_PATTERNS):
            filtered_selectors.append(selector)

    # Считаем полностью идентичные селекторы
    selector_counts = {}
    for selector in filtered_selectors:
        if selector in selector_counts:
            selector_counts[selector] += 1
        else:
            selector_counts[selector] = 1

    # Находим только полностью дублирующиеся селекторы
    duplicates = [s for s, count in selector_counts.items() if count > 1]
    return duplicates

def group_by_base_selector(blocks):
    """Группирует блоки стилей по базовым селекторам."""
    grouped = defaultdict(list)

    for selector, properties in blocks:
        # Если селектор содержит проблемный псевдокласс, обрабатываем его
        for problem in PROBLEMATIC_SELECTORS:
            if f":{problem}" in selector:
                parts = selector.split(f":{problem}")
                base_selector = parts[0].strip()
                grouped[base_selector].append((selector, properties))
                break
        else:
            # Если селектор не содержит проблемных псевдоклассов, добавляем его как есть
            grouped[selector].append((selector, properties))

    return grouped

def parse_properties(properties_text):
    """Разбирает текст свойств CSS на словарь свойство: значение."""
    properties = {}
    for line in properties_text.split(';'):
        line = line.strip()
        if not line:
            continue

        if ':' in line:
            key, value = line.split(':', 1)
            properties[key.strip()] = value.strip()

    return properties

def merge_duplicate_selectors(content):
    """Объединяет дублирующиеся селекторы в CSS/QSS."""
    # Проверяем наличие дублирующихся селекторов
    duplicates = find_duplicate_selectors(content)
    if not duplicates:
        return content  # Нет дублирующихся селекторов

    # Извлекаем все блоки стилей
    blocks = extract_style_blocks(content)

    # Группируем блоки по базовым селекторам
    grouped = group_by_base_selector(blocks)

    # Для каждого базового селектора смотрим, есть ли дублирующиеся состояния
    fixed_content = content
    for base_selector, variations in grouped.items():
        # Если есть только один вариант, пропускаем
        if len(variations) <= 1:
            continue

        # Находим дублирующиеся свойства
        all_properties = defaultdict(dict)
        for selector, props_text in variations:
            props = parse_properties(props_text)
            for key, value in props.items():
                all_properties[key][selector] = value

        # Находим свойства, которые имеют разные значения в разных селекторах
        # и исправляем каждый блок в контенте
        for selector, props_text in variations:
            # Создаем новый блок свойств для этого селектора
            props = parse_properties(props_text)

            # Находим оригинальный блок в контенте
            orig_block = f"{selector}{{{props_text}}}"

            # Создаем новый блок с уникальными свойствами
            new_props = []
            for key, value in props.items():
                new_props.append(f"{key}: {value}")

            new_props_text = ";\n    ".join(new_props)
            new_block = f"{selector}{{\n    {new_props_text};\n}}"

            # Заменяем старый блок на новый
            fixed_content = fixed_content.replace(orig_block, new_block)

    return fixed_content

def fix_file(file_path, output_path=None):
    """Исправляет дублирующиеся селекторы в файле."""
    print(f"Обработка файла: {file_path}")

    # Читаем содержимое файла
    content = read_file(file_path)

    # Проверяем наличие дублирующихся селекторов
    duplicates = find_duplicate_selectors(content)
    if duplicates:
        print(f"Найдены дублирующиеся селекторы: {', '.join(duplicates[:5])}")

        # Исправляем дублирующиеся селекторы
        fixed_content = merge_duplicate_selectors(content)
    else:
        print("Дублирующихся селекторов не обнаружено.")
        fixed_content = content

    # Определяем путь выходного файла
    if not output_path:
        output_path = file_path

    # Записываем результат
    write_file(output_path, fixed_content)
    print(f"Файл сохранен: {output_path}")

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Улучшенный скрипт для устранения дублирующихся селекторов в CSS/QSS файлах")
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
                    fix_file(file_path)
    else:
        # Обрабатываем один файл
        fix_file(args.file, args.output)

    return 0

if __name__ == "__main__":
    sys.exit(main())
