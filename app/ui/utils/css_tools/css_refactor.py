#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Утилита для рефакторинга CSS/QSS файлов.
Позволяет:
1. Выявлять и объединять дублирующиеся селекторы
2. Находить хардкодированные цвета и заменять их на переменные
3. Создавать файл с цветовыми переменными

Использование:
    python css_refactor.py <путь_к_css_файлу>
"""

import sys
import os
import re
import argparse
from collections import defaultdict, Counter
from pathlib import Path
import json

# Регулярное выражение для поиска CSS-селекторов
SELECTOR_PATTERN = re.compile(r'([^{]+)\s*{([^}]*)}')

# Регулярное выражение для поиска hex-цветов
COLOR_PATTERN = re.compile(r'#([0-9a-fA-F]{3,6})\b')

# Регулярное выражение для поиска вариаций селекторов
STATE_SELECTORS = ['hover', 'pressed', 'selected', 'active', 'focus', 'disabled', 'vertical', 'horizontal']


def find_duplicate_selectors(css_content):
    """
    Находит дублирующиеся селекторы в CSS.
    Возвращает словарь с дублирующимися селекторами и их количеством.
    """
    selectors = defaultdict(list)

    for match in SELECTOR_PATTERN.finditer(css_content):
        selector = match.group(1).strip()
        # Проверяем вариации селекторов (hover, pressed и т.д.)
        for state in STATE_SELECTORS:
            if state in selector:
                base_selector = selector.split(':' + state)[0].strip()
                selectors[base_selector].append(selector)

    # Находим дубликаты
    duplicates = {base: variations for base, variations in selectors.items() if len(variations) > 1}

    return duplicates


def extract_colors(css_content):
    """
    Извлекает все HEX-цвета из CSS и считает их использование.
    Возвращает словарь с цветами и их количеством.
    """
    colors = Counter()

    for match in COLOR_PATTERN.finditer(css_content):
        color = "#" + match.group(1).upper()
        # Нормализуем сокращенные цвета (#ABC -> #AABBCC)
        if len(match.group(1)) == 3:
            r, g, b = match.group(1)
            color = f"#{r}{r}{g}{g}{b}{b}".upper()
        colors[color] += 1

    return colors


def create_color_variables(colors, prefix='color', output_path=None):
    """
    Создает файл с CSS-переменными для цветов.
    Возвращает содержимое файла с переменными и словарь соответствия цветов переменным.
    """
    color_vars = {}
    css_vars = ":root {\n"

    # Сортируем цвета по частоте использования
    sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)

    for i, (color, count) in enumerate(sorted_colors, 1):
        var_name = f"--{prefix}-{i}"
        color_vars[color] = var_name
        css_vars += f"    {var_name}: {color}; /* Используется {count} раз */\n"

    css_vars += "}\n"

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css_vars)

    return css_vars, color_vars


def replace_colors_with_variables(css_content, color_vars):
    """
    Заменяет хардкодированные цвета в CSS на переменные.
    Возвращает обновленное содержимое CSS.
    """
    result = css_content

    # Заменяем цвета на переменные
    for color, var_name in color_vars.items():
        # Используем регулярное выражение для точного совпадения цвета
        pattern = re.compile(r'(' + re.escape(color) + r')\b', re.IGNORECASE)
        result = pattern.sub(f"var({var_name})", result)

    return result


def merge_duplicate_selectors(css_content, duplicates):
    """
    Объединяет дублирующиеся селекторы в CSS.
    Возвращает обновленное содержимое CSS.
    """
    result = css_content

    # Создаем словарь для хранения правил для каждого селектора
    selector_rules = {}

    # Извлекаем все селекторы и их правила
    for match in SELECTOR_PATTERN.finditer(css_content):
        selector = match.group(1).strip()
        rules = match.group(2).strip()
        selector_rules[selector] = rules

    # Объединяем дублирующиеся селекторы
    for base_selector, variations in duplicates.items():
        # Собираем все правила для вариаций селектора
        combined_rules = {}
        for var_selector in variations:
            if var_selector in selector_rules:
                rules = selector_rules[var_selector]
                for rule in rules.split(';'):
                    rule = rule.strip()
                    if rule:
                        prop, value = rule.split(':', 1)
                        combined_rules[prop.strip()] = value.strip()

        # Создаем новый блок CSS для каждой вариации
        for var_selector in variations:
            if var_selector in selector_rules:
                old_rules = selector_rules[var_selector]
                new_rules = '; '.join([f"{prop}: {value}" for prop, value in combined_rules.items()])

                # Заменяем старый блок новым
                old_block = f"{var_selector} {{{old_rules}}}"
                new_block = f"{var_selector} {{{new_rules}}}"
                result = result.replace(old_block, new_block)

    return result


def fix_duplicate_selectors(file_path, output_path=None):
    """
    Исправляет дублирующиеся селекторы в CSS файле.
    """
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Находим дублирующиеся селекторы
    duplicates = find_duplicate_selectors(css_content)

    if duplicates:
        print(f"Найдено {len(duplicates)} дублирующихся селекторов в {file_path}:")
        for base, variations in duplicates.items():
            print(f"  - {base}: {len(variations)} вариаций")

        # Объединяем дублирующиеся селекторы
        fixed_css = merge_duplicate_selectors(css_content, duplicates)

        # Сохраняем исправленный CSS
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(fixed_css)
            print(f"Исправленный CSS сохранен в {output_path}")
        else:
            # Если выходной путь не указан, используем исходный файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_css)
            print(f"Файл {file_path} обновлен")
    else:
        print(f"Дублирующихся селекторов не найдено в {file_path}")


def fix_hardcoded_colors(file_path, output_path=None, vars_path=None):
    """
    Исправляет хардкодированные цвета в CSS файле.
    """
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Извлекаем цвета
    colors = extract_colors(css_content)

    if colors:
        print(f"Найдено {len(colors)} различных цветов в {file_path}:")
        for i, (color, count) in enumerate(sorted(colors.items(), key=lambda x: x[1], reverse=True)):
            if i < 10:  # Показываем топ-10 цветов
                print(f"  - {color}: {count} использований")

        # Создаем файл с переменными цветов
        prefix = Path(file_path).stem.split('-')[0].lower()  # Используем первую часть имени файла как префикс
        vars_file = vars_path or file_path.replace('.css', '.vars.css').replace('.qss', '.vars.qss')
        vars_content, color_vars = create_color_variables(colors, prefix, vars_file)

        # Заменяем цвета на переменные
        fixed_css = replace_colors_with_variables(css_content, color_vars)

        # Сохраняем исправленный CSS
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(fixed_css)
            print(f"Исправленный CSS сохранен в {output_path}")
        else:
            # Если выходной путь не указан, используем исходный файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_css)
            print(f"Файл {file_path} обновлен")
    else:
        print(f"Хардкодированных цветов не найдено в {file_path}")


def create_theme_definitions(themes_dir, output_path="theme_definitions.json"):
    """
    Создает JSON-файл с определениями тем на основе файлов в директории тем.
    """
    theme_info = {}

    for root, dirs, files in os.walk(themes_dir):
        for file in files:
            if file.endswith(('.qss', '.css')):
                file_path = os.path.join(root, file)
                theme_name = os.path.basename(root)

                with open(file_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()

                # Извлекаем цвета
                colors = extract_colors(css_content)

                # Добавляем информацию о теме
                if theme_name not in theme_info:
                    theme_info[theme_name] = {'colors': {}}

                # Добавляем цвета
                for color, count in colors.items():
                    if color not in theme_info[theme_name]['colors']:
                        theme_info[theme_name]['colors'][color] = 0
                    theme_info[theme_name]['colors'][color] += count

    # Сохраняем информацию о темах в JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(theme_info, f, indent=4)

    print(f"Информация о темах сохранена в {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Утилита для рефакторинга CSS/QSS файлов")
    parser.add_argument("file", help="Путь к CSS/QSS файлу или директории с файлами")
    parser.add_argument("--output", "-o", help="Путь для сохранения исправленного файла")
    parser.add_argument("--vars", "-v", help="Путь для сохранения файла с переменными цветов")
    parser.add_argument("--fix-duplicates", "-d", action="store_true", help="Исправить дублирующиеся селекторы")
    parser.add_argument("--fix-colors", "-c", action="store_true", help="Исправить хардкодированные цвета")
    parser.add_argument("--theme-info", "-t", action="store_true", help="Создать информацию о темах")

    args = parser.parse_args()

    if os.path.isdir(args.file):
        # Обрабатываем все CSS/QSS файлы в директории
        for root, dirs, files in os.walk(args.file):
            for file in files:
                if file.endswith(('.css', '.qss')):
                    file_path = os.path.join(root, file)
                    print(f"\nОбработка файла: {file_path}")

                    if args.fix_duplicates:
                        fix_duplicate_selectors(file_path)

                    if args.fix_colors:
                        fix_hardcoded_colors(file_path, vars_path=args.vars)

        if args.theme_info:
            create_theme_definitions(args.file)
    else:
        # Обрабатываем один файл
        if args.fix_duplicates:
            fix_duplicate_selectors(args.file, args.output)

        if args.fix_colors:
            fix_hardcoded_colors(args.file, args.output, args.vars)


if __name__ == "__main__":
    main()
