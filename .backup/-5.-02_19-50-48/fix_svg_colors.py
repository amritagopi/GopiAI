#!/usr/bin/env python
"""
Утилита для исправления жестко закодированных цветов в SVG файлах.
Находит все SVG файлы с цветами, отличными от базового, и заменяет их.
"""

import os
import re
import json
import argparse
from app.ui.icon_manager import IconManager

def fix_svg_colors(icon_folder, dry_run=False):
    """
    Ищет и исправляет жестко закодированные цвета в SVG файлах.

    Args:
        icon_folder (str): Путь к папке с иконками
        dry_run (bool): Если True, только показывает изменения без их применения
    """
    manifest_path = os.path.join(icon_folder, "manifest.json")
    base_color = IconManager.ICON_BASE_COLOR

    if not os.path.exists(manifest_path):
        print(f"Манифест иконок не найден в {manifest_path}!")
        return

    print(f"Используем базовый цвет: {base_color}")

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке манифеста: {e}")
        return

    icons = manifest.get("icons", {})
    modified_files = []
    skipped_files = []

    for icon_name, file_name in icons.items():
        if not file_name.endswith('.svg'):
            continue

        svg_path = os.path.join(icon_folder, file_name)
        if not os.path.exists(svg_path):
            print(f"Файл иконки не найден: {svg_path}")
            continue

        # Читаем содержимое SVG
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {svg_path}: {e}")
            continue

        # Ищем все hex-цвета (исключая базовый)
        hex_colors = set(re.findall(r'#[0-9a-fA-F]{3,6}', svg_content))
        hard_colors = hex_colors - {base_color}

        if not hard_colors:
            skipped_files.append(file_name)
            continue

        # Заменяем все жесткие цвета на базовый
        modified_content = svg_content
        for color in hard_colors:
            modified_content = modified_content.replace(color, base_color)

        # Сохраняем изменения
        if not dry_run:
            try:
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                modified_files.append((file_name, list(hard_colors)))
            except Exception as e:
                print(f"Ошибка при записи файла {svg_path}: {e}")
        else:
            modified_files.append((file_name, list(hard_colors)))

    # Выводим результаты
    if modified_files:
        print(f"\nИсправлено {len(modified_files)} SVG файлов{' (тестовый режим)' if dry_run else ''}:")
        for file_name, colors in modified_files:
            color_str = ", ".join(colors)
            print(f"  {file_name}: {color_str} -> {base_color}")
    else:
        print("\nНе найдено SVG файлов с жестко закодированными цветами.")

    if skipped_files:
        print(f"\nПропущено {len(skipped_files)} файлов (уже используют базовый цвет)")

def main():
    parser = argparse.ArgumentParser(description='Утилита для исправления цветов в SVG файлах.')
    parser.add_argument('--icons-dir', default="assets/icons", help='Директория с иконками')
    parser.add_argument('--dry-run', action='store_true', help='Режим без внесения изменений')

    args = parser.parse_args()

    # Определяем путь к папке с иконками
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_folder = os.path.join(current_dir, args.icons_dir)

    if not os.path.exists(icon_folder):
        print(f"Директория {icon_folder} не существует!")
        return

    print(f"Анализ SVG файлов в {icon_folder}")
    fix_svg_colors(icon_folder, args.dry_run)

if __name__ == "__main__":
    main()
