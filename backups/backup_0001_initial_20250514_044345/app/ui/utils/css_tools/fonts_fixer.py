#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Утилита для исправления файла шрифтов CSS.
Позволяет устранить дублирующиеся селекторы @font-face и объединить их.
"""

import re
import os
import sys

# Регулярное выражение для поиска блоков @font-face
FONT_FACE_PATTERN = re.compile(r'@font-face\s*{([^}]*)}', re.DOTALL)

def extract_font_faces(css_content):
    """Извлекает все блоки @font-face из CSS."""
    return FONT_FACE_PATTERN.findall(css_content)

def parse_font_face(font_face_block):
    """Разбирает блок @font-face на свойства."""
    properties = {}
    for line in font_face_block.strip().split(';'):
        line = line.strip()
        if not line:
            continue

        parts = line.split(':', 1)
        if len(parts) != 2:
            continue

        prop_name = parts[0].strip()
        prop_value = parts[1].strip()
        properties[prop_name] = prop_value

    return properties

def normalize_font_faces(css_path, output_path=None):
    """
    Нормализует блоки @font-face в CSS файле.
    Объединяет дублирующиеся определения и улучшает форматирование.
    """
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Извлекаем все блоки @font-face
    font_face_blocks = extract_font_faces(css_content)

    if not font_face_blocks:
        print(f"Блоки @font-face не найдены в {css_path}")
        return

    print(f"Найдено {len(font_face_blocks)} блоков @font-face в {css_path}")

    # Парсим каждый блок
    font_families = {}
    for block in font_face_blocks:
        properties = parse_font_face(block)

        # Пропускаем блоки без font-family
        if 'font-family' not in properties:
            continue

        font_family = properties['font-family'].strip('\'"')
        weight = properties.get('font-weight', '400')
        style = properties.get('font-style', 'normal')

        # Ключ для группировки вариантов шрифта
        key = (font_family, weight, style)

        if key not in font_families:
            font_families[key] = properties
        else:
            # Объединяем свойства, если есть конфликты
            for prop, value in properties.items():
                if prop not in font_families[key]:
                    font_families[key][prop] = value

    # Создаем новое содержимое CSS
    new_css = "/* Нормализованные шрифты для GopiAI */\n\n"
    for (family, weight, style), properties in font_families.items():
        new_css += "@font-face {\n"
        for prop, value in sorted(properties.items()):
            new_css += f"    {prop}: {value};\n"
        new_css += "}\n\n"

    # Добавляем импорт Google Fonts
    if "@import" in css_content:
        import_match = re.search(r'@import url\([\'"]([^\'"]+)[\'"]\);', css_content)
        if import_match:
            google_fonts_url = import_match.group(1)
            new_css += f"/* Fallback Google Fonts */\n@import url('{google_fonts_url}');\n"

    # Сохраняем новый CSS
    output_file = output_path or css_path
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_css)

    print(f"Нормализовано {len(font_families)} определений шрифтов в {output_file}")

def main():
    """Основная функция скрипта."""
    if len(sys.argv) < 2:
        print("Использование: python fonts_fixer.py <путь_к_css_файлу> [выходной_файл]")
        sys.exit(1)

    css_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(css_path):
        print(f"Файл не найден: {css_path}")
        sys.exit(1)

    normalize_font_faces(css_path, output_path)

if __name__ == "__main__":
    main()
