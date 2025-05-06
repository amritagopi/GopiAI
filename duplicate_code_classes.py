#!/usr/bin/env python
"""
Модуль для анализа дублирующихся классов

Часть системы анализа дублирования кода в проекте GopiAI.
Оптимизирован для работы с низкими требованиями к ресурсам.
"""

import ast
import hashlib
from typing import List, Dict, Tuple, Any


def read_file_content(file_path: str) -> str:
    """Читает содержимое файла и возвращает его как строку"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return ""


def hash_ast_node(node: ast.AST) -> str:
    """
    Создает хеш AST-узла для сравнения семантически эквивалентных классов

    Игнорирует имена переменных, значения литералов и комментарии,
    фокусируясь на структуре кода.
    """
    if isinstance(node, (ast.Name, ast.Attribute)):
        # Для имен переменных используем фиксированное значение
        return f"NAME_{type(node).__name__}"
    elif isinstance(node, ast.Constant):
        # Для констант используем тип значения
        return f"CONST_{type(node.value).__name__}"
    elif isinstance(node, ast.Str):
        # Строки в старых версиях Python
        return "CONST_str"
    elif isinstance(node, ast.Num):
        # Числа в старых версиях Python
        return "CONST_num"
    elif isinstance(node, ast.AST):
        # Для других узлов AST сохраняем структуру
        fields = []
        for field, value in ast.iter_fields(node):
            if field != 'ctx' and field != 'lineno' and field != 'col_offset' and field != 'end_lineno' and field != 'end_col_offset':
                if isinstance(value, list):
                    fields.append((field, [hash_ast_node(v) for v in value if isinstance(v, ast.AST)]))
                elif isinstance(value, ast.AST):
                    fields.append((field, hash_ast_node(value)))

        node_hash = f"{type(node).__name__}({','.join(f'{f}={v}' for f, v in fields)})"
        return hashlib.md5(node_hash.encode('utf-8')).hexdigest()
    else:
        # Для других типов (не AST) используем строковое представление
        return str(type(node).__name__)


def analyze_classes(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Анализирует указанные файлы и находит дублирующиеся классы

    Args:
        file_paths: Список путей к файлам для анализа

    Returns:
        Список словарей с информацией о дублирующихся классах
    """
    print(f"Анализ дублирования классов в {len(file_paths)} файлах...")

    # Словарь для хранения хешей классов и их расположения
    classes_by_hash = {}
    class_source = {}

    # Счетчики для статистики
    files_analyzed = 0
    classes_analyzed = 0

    # Анализируем каждый файл отдельно
    for file_path in file_paths:
        content = read_file_content(file_path)
        if not content:
            continue

        files_analyzed += 1

        try:
            # Парсим исходный код в AST
            tree = ast.parse(content)

            # Обходим все узлы AST, соответствующие классам
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes_analyzed += 1

                    # Получаем исходный код класса
                    class_lines = content.splitlines()[node.lineno - 1:node.end_lineno]
                    cls_source = '\n'.join(class_lines)

                    # Создаем хеш для класса на основе его AST
                    class_hash = hash_ast_node(node)

                    if class_hash not in classes_by_hash:
                        classes_by_hash[class_hash] = []

                    classes_by_hash[class_hash].append((file_path, node.lineno, node.end_lineno, node.name))
                    class_source[class_hash] = cls_source
        except SyntaxError:
            print(f"Ошибка синтаксиса в файле {file_path}, пропускаем")
            continue

    # Фильтруем только дублирующиеся классы
    duplicate_classes = []
    for class_hash, locations in classes_by_hash.items():
        if len(locations) > 1:
            duplicate_classes.append({
                'hash': class_hash,
                'source': class_source[class_hash],
                'locations': locations,
                'names': [loc[3] for loc in locations],
                'size': len(class_source[class_hash].splitlines())
            })

    # Сортируем дубликаты классов по размеру (от больших к маленьким)
    duplicate_classes.sort(key=lambda x: x['size'], reverse=True)

    print(f"Проанализировано {files_analyzed} файлов, {classes_analyzed} классов")
    print(f"Найдено {len(duplicate_classes)} дублирующихся классов")

    return duplicate_classes


# Пример использования
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Использование: python duplicate_code_classes.py file1.py [file2.py ...]")
        sys.exit(1)

    file_paths = sys.argv[1:]
    duplicates = analyze_classes(file_paths)

    # Выводим пример результатов
    for i, dup in enumerate(duplicates[:3]):  # Первые 3 дубликата
        print(f"\nДубликат класса #{i+1}:")
        print(f"Имена: {', '.join(dup['names'])}")
        print(f"Размер: {dup['size']} строк")
        print(f"Местоположения:")
        for loc in dup['locations']:
            print(f"  - {loc[0]}:{loc[1]}-{loc[2]} ('{loc[3]}')")

    if len(duplicates) > 3:
        print(f"\n... и еще {len(duplicates) - 3} дубликатов классов")
