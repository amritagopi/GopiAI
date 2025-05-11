#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import Path

# Паттерны для поиска настоящих заглушек
STUB_PATTERNS = [
    r'^\s*pass\s*$',  # Строка содержит только pass
    r'^\s*pass\s*#.*$',  # Строка содержит pass с комментарием
    r'^\s*#\s*TODO',  # Комментарий с TODO
    r'^\s*#\s*FIXME',  # Комментарий с FIXME
    r'^\s*#\s*[Ss]tub',  # Комментарий со словом stub/Stub
    r'^\s*#\s*[Зз]аглушка',  # Комментарий со словом заглушка
    r'^\s*raise\s+NotImplementedError',  # Выброс NotImplementedError
]

def is_stub_method(method_body):
    """Проверяет, является ли метод заглушкой."""
    # Разделяем на строки
    lines = method_body.split('\n')

    # Удаляем пустые строки и строку определения метода
    non_empty_lines = [line.strip() for line in lines[1:] if line.strip()]

    # Если тело пустое или только с docstring, это заглушка
    if not non_empty_lines:
        return True

    # Проверяем каждую строку на соответствие паттернам
    for line in non_empty_lines:
        for pattern in STUB_PATTERNS:
            if re.match(pattern, line):
                # Найден паттерн заглушки
                return True

    # Если все строки после docstring - только pass
    code_lines = [line for line in non_empty_lines
                  if not (line.startswith('"""') or line.startswith("'''") or
                         line.endswith('"""') or line.endswith("'''"))]
    if all(line.strip() == 'pass' for line in code_lines):
        return True

    return False

def extract_method(content, start_pos):
    """Извлекает метод из файла начиная с позиции start_pos."""
    lines = content.split('\n')
    method_start_line = content[:start_pos].count('\n')

    # Получаем строку с определением метода
    if method_start_line >= len(lines):
        return "", method_start_line, method_start_line

    method_def = lines[method_start_line]

    # Определяем отступ метода
    indent_match = re.match(r'^(\s*)', method_def)
    if not indent_match:
        return method_def, method_start_line, method_start_line

    indent_level = len(indent_match.group(1))

    # Собираем тело метода
    method_body = [method_def]
    line_idx = method_start_line + 1

    while line_idx < len(lines):
        line = lines[line_idx]

        # Пустая строка - добавляем и идем дальше
        if not line.strip():
            method_body.append(line)
            line_idx += 1
            continue

        # Если нашли строку с меньшим отступом, метод закончился
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
            break

        method_body.append(line)
        line_idx += 1

    return '\n'.join(method_body), method_start_line, line_idx - 1

def find_real_stubs(directory):
    """Находит настоящие заглушки в директории."""
    method_pattern = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
    stubs = {}

    # Рекурсивно обходим все Python-файлы
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Ищем методы
                file_stubs = []
                for match in method_pattern.finditer(content):
                    method_name = match.group(1)
                    method_start = match.start()

                    # Пропускаем специальные методы
                    if method_name.startswith('__') and method_name.endswith('__'):
                        continue

                    # Извлекаем тело метода
                    method_body, start_line, end_line = extract_method(content, method_start)

                    # Проверяем, является ли метод заглушкой
                    if is_stub_method(method_body):
                        file_stubs.append((method_name, start_line + 1))  # +1 для 1-индексации строк

                if file_stubs:
                    stubs[rel_path] = file_stubs

            except Exception as e:
                print(f"Ошибка при обработке файла {rel_path}: {e}")

    return stubs

def write_report(stubs, output_file):
    """Записывает отчет о найденных заглушках."""
    # Сортируем файлы по количеству заглушек
    sorted_files = sorted(stubs.items(), key=lambda x: len(x[1]), reverse=True)

    # Подсчитываем общее количество заглушек
    total_stubs = sum(len(file_stubs) for file_stubs in stubs.values())

    # Формируем отчет
    report = [
        f"# Отчет о найденных методах-заглушках",
        f"",
        f"Всего найдено **{total_stubs}** заглушек в **{len(stubs)}** файлах.",
        f"",
        f"## Список файлов с заглушками",
        f"",
    ]

    # Добавляем информацию о каждом файле
    for file_path, file_stubs in sorted_files:
        report.append(f"### {file_path} ({len(file_stubs)} заглушек)")
        report.append("")

        for method_name, line in file_stubs:
            report.append(f"- `{method_name}` (строка {line})")

        report.append("")

    # Записываем в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"Отчет сохранен в {output_file}")

if __name__ == "__main__":
    directory = 'app'
    output_file = 'real_stubs_report.md'

    print(f"Поиск настоящих заглушек в директории {directory}...")
    stubs = find_real_stubs(directory)

    print(f"Найдено {sum(len(s) for s in stubs.values())} заглушек в {len(stubs)} файлах.")
    write_report(stubs, output_file)
