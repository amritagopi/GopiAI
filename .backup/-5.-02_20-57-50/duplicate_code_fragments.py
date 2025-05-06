#!/usr/bin/env python
"""
Модуль для анализа дублирующихся фрагментов кода

Часть системы анализа дублирования кода в проекте GopiAI.
Оптимизирован для работы с низкими требованиями к ресурсам.
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Any
from collections import defaultdict

# Константы
MIN_DUPLICATE_LINES = 4  # Минимальное количество строк для детекции дубликата
MIN_TOKEN_LENGTH = 100   # Минимальная длина токенов для детекции дубликата


def read_file_content(file_path: str) -> Tuple[str, List[str]]:
    """Читает содержимое файла и возвращает его как строку и список строк"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()
            return content, lines
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return "", []


def analyze_fragments(file_paths: List[str], min_lines: int = MIN_DUPLICATE_LINES,
                     min_tokens: int = MIN_TOKEN_LENGTH) -> List[Dict[str, Any]]:
    """
    Анализирует указанные файлы и находит дублирующиеся фрагменты кода

    Args:
        file_paths: Список путей к файлам для анализа
        min_lines: Минимальное количество строк для детекции дубликата
        min_tokens: Минимальная длина токенов для детекции дубликата

    Returns:
        Список словарей с информацией о дублирующихся фрагментах
    """
    print(f"Анализ дублирования фрагментов кода в {len(file_paths)} файлах...")

    # Используем меньший размер окна для уменьшения потребления памяти
    duplicate_fragments = []

    # Словарь для хранения хешей фрагментов кода и их расположения
    fragments_by_hash = defaultdict(list)
    content_chunks = {}

    # Счетчики для статистики
    files_analyzed = 0
    lines_analyzed = 0

    # Анализируем каждый файл отдельно
    for file_path in file_paths:
        content, lines = read_file_content(file_path)
        if not content:
            continue

        files_analyzed += 1
        lines_analyzed += len(lines)

        # Оптимизация: проверяем только фрагменты с минимальным размером
        # вместо всех возможных размеров окна
        for i in range(len(lines) - min_lines + 1):
            chunk = '\n'.join(lines[i:i + min_lines])
            # Игнорируем фрагменты с малым количеством значимых символов
            if len(re.sub(r'\s', '', chunk)) < min_tokens / 4:
                continue

            chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
            fragments_by_hash[chunk_hash].append((file_path, i, i + min_lines))
            content_chunks[chunk_hash] = chunk

    # Фильтруем только дублирующиеся фрагменты
    for chunk_hash, locations in fragments_by_hash.items():
        if len(locations) > 1:
            # Группируем по файлам, чтобы избежать самоперекрытия
            file_groups = defaultdict(list)
            for loc in locations:
                file_groups[loc[0]].append(loc)

            # Если есть дубликаты в разных файлах, добавляем их
            if len(file_groups) > 1 or (len(file_groups) == 1 and len(next(iter(file_groups.values()))) > 1):
                duplicate_fragments.append({
                    'hash': chunk_hash,
                    'content': content_chunks[chunk_hash],
                    'locations': locations,
                    'size': len(content_chunks[chunk_hash].splitlines())
                })

    # Сортируем дубликаты по размеру (от больших к маленьким)
    duplicate_fragments.sort(key=lambda x: x['size'], reverse=True)

    # Удаляем перекрывающиеся дубликаты
    duplicate_fragments = remove_overlapping_duplicates(duplicate_fragments)

    print(f"Проанализировано {files_analyzed} файлов, {lines_analyzed} строк")
    print(f"Найдено {len(duplicate_fragments)} дублирующихся фрагментов кода")

    return duplicate_fragments


def remove_overlapping_duplicates(duplicate_fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Удаляет перекрывающиеся дубликаты из результатов"""
    if not duplicate_fragments:
        return []

    non_overlapping = []
    seen_locations = set()

    for dup in duplicate_fragments:
        has_overlap = False
        for loc in dup['locations']:
            file_path, start, end = loc
            # Проверяем, не перекрывается ли этот фрагмент с ранее найденными
            location_key = (str(file_path), start, end)
            if location_key in seen_locations:
                has_overlap = True
                break

        if not has_overlap:
            # Добавляем этот дубликат и отмечаем его местоположения
            non_overlapping.append(dup)
            for loc in dup['locations']:
                file_path, start, end = loc
                seen_locations.add((str(file_path), start, end))

    return non_overlapping


# Пример использования
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Использование: python duplicate_code_fragments.py file1.py [file2.py ...]")
        sys.exit(1)

    file_paths = sys.argv[1:]
    duplicates = analyze_fragments(file_paths)

    # Выводим пример результатов
    for i, dup in enumerate(duplicates[:5]):  # Первые 5 дубликатов
        print(f"\nДубликат #{i+1}:")
        print(f"Размер: {dup['size']} строк")
        print(f"Местоположения:")
        for loc in dup['locations']:
            print(f"  - {loc[0]}:{loc[1]+1}-{loc[2]}")

    if len(duplicates) > 5:
        print(f"\n... и еще {len(duplicates) - 5} дубликатов")
