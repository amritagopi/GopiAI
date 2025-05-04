#!/usr/bin/env python
"""
Утилита для исправления дублирующихся селекторов в QSS файлах.
Анализирует QSS файлы, находит дублирующиеся селекторы и объединяет их.
Также удаляет лишние пустые строки между свойствами.
"""

import os
import re
import sys
import argparse
from collections import defaultdict

def parse_qss_file(file_path):
    """
    Парсит QSS файл и возвращает словарь селекторов с их содержимым.

    Args:
        file_path (str): Путь к QSS файлу

    Returns:
        dict: Словарь {селектор: [содержимое]}
    """
    selector_map = defaultdict(list)
    current_comment = ""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Сохраняем комментарии
        comments = re.findall(r'/\*.*?\*/', content, re.DOTALL)

        # Удаляем комментарии перед парсингом
        content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Разбиваем файл на блоки селекторов и их содержимое
        blocks = re.findall(r'([^{]+)\s*{([^}]*)}', content_no_comments)

        for selector, body in blocks:
            selector = selector.strip()

            # Убираем лишние пустые строки и форматируем правильно
            body_parts = []
            for line in body.strip().split('\n'):
                line = line.strip()
                if line and not line.isspace():
                    body_parts.append(line)

            body = '\n    '.join(body_parts)

            # Обрабатываем множественные селекторы (через запятую)
            selectors = [s.strip() for s in selector.split(',')]

            for s in selectors:
                selector_map[s].append(body)

    except Exception as e:
        print(f"Ошибка при парсинге файла {file_path}: {e}")

    return selector_map, comments

def merge_duplicate_selectors(selector_map):
    """
    Объединяет дублирующиеся селекторы.

    Args:
        selector_map (dict): Словарь {селектор: [содержимое]}

    Returns:
        dict: Словарь {селектор: объединенное_содержимое}
    """
    merged_map = {}

    for selector, bodies in selector_map.items():
        if len(bodies) > 1:
            print(f"Найден дублирующийся селектор: {selector} ({len(bodies)} повторений)")

            # Объединяем все свойства
            properties = {}
            for body in bodies:
                for prop_line in body.split(';'):
                    prop_line = prop_line.strip()
                    if not prop_line:
                        continue

                    try:
                        prop_parts = prop_line.split(':', 1)
                        if len(prop_parts) == 2:
                            prop_name, prop_value = prop_parts
                            properties[prop_name.strip()] = prop_value.strip()
                    except ValueError:
                        print(f"Ошибка парсинга свойства: {prop_line}")

            # Создаем новое содержимое
            merged_body = '\n    '.join([f"{name}: {value};" for name, value in properties.items()])
            merged_map[selector] = merged_body
        else:
            merged_map[selector] = bodies[0]

    return merged_map

def generate_qss_content(merged_map, comments):
    """
    Генерирует содержимое QSS файла из объединенных селекторов.

    Args:
        merged_map (dict): Словарь {селектор: объединенное_содержимое}
        comments (list): Список комментариев

    Returns:
        str: Содержимое QSS файла
    """
    lines = []

    # Сначала добавляем все комментарии в начало файла
    for comment in comments:
        lines.append(comment)
        lines.append("")  # Пустая строка после комментария

    for selector, body in merged_map.items():
        lines.append(f"{selector} {{\n    {body}\n}}")

    return '\n\n'.join(lines)

def process_qss_file(file_path, output_path=None, dry_run=False):
    """
    Обрабатывает QSS файл, удаляя дублирующиеся селекторы.

    Args:
        file_path (str): Путь к QSS файлу
        output_path (str, optional): Путь для сохранения обработанного файла
        dry_run (bool): Если True, только выводит результаты без сохранения

    Returns:
        bool: True, если файл был обработан успешно
    """
    print(f"Обработка файла: {file_path}")

    # Если выходной путь не указан, перезаписываем входной файл
    if not output_path:
        output_path = file_path

    try:
        # Парсим файл
        selector_map, comments = parse_qss_file(file_path)

        # Объединяем дублирующиеся селекторы
        merged_map = merge_duplicate_selectors(selector_map)

        # Генерируем новое содержимое
        new_content = generate_qss_content(merged_map, comments)

        if dry_run:
            print(f"Сгенерировано новое содержимое для {file_path} (без сохранения)")
            return True

        # Сохраняем результат
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Файл успешно обработан и сохранен: {output_path}")
        return True

    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return False

def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description='Утилита для исправления дублирующихся селекторов в QSS файлах.')
    parser.add_argument('files', nargs='+', help='QSS файлы для обработки')
    parser.add_argument('--dry-run', action='store_true', help='Только анализ без модификации файлов')
    parser.add_argument('--output-dir', help='Директория для сохранения обработанных файлов')

    args = parser.parse_args()

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue

        if args.output_dir:
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            output_path = os.path.join(args.output_dir, os.path.basename(file_path))
        else:
            output_path = file_path

        process_qss_file(file_path, output_path, args.dry_run)

if __name__ == "__main__":
    main()
