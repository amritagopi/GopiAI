#!/usr/bin/env python
"""
Модуль для анализа дублирующихся функций

Часть системы анализа дублирования кода в проекте GopiAI.
Оптимизирован для работы с низкими требованиями к ресурсам.
"""

import ast
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Any, Set


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
    Создает хеш AST-узла для сравнения семантически эквивалентных функций

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


def analyze_functions(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Анализирует указанные файлы и находит дублирующиеся функции

    Args:
        file_paths: Список путей к файлам для анализа

    Returns:
        Список словарей с информацией о дублирующихся функциях
    """
    print(f"Анализ дублирования функций в {len(file_paths)} файлах...")

    # Словарь для хранения хешей функций и их расположения
    functions_by_hash = {}
    function_source = {}

    # Счетчики для статистики
    files_analyzed = 0
    functions_analyzed = 0

    # Анализируем каждый файл отдельно
    for file_path in file_paths:
        content = read_file_content(file_path)
        if not content:
            continue

        files_analyzed += 1

        try:
            # Парсим исходный код в AST
            tree = ast.parse(content)

            # Обходим все узлы AST, соответствующие функциям
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions_analyzed += 1

                    # Получаем исходный код функции
                    func_lines = content.splitlines()[node.lineno - 1:node.end_lineno]
                    func_source = '\n'.join(func_lines)

                    # Создаем хеш для функции на основе ее AST
                    func_hash = hash_ast_node(node)

                    if func_hash not in functions_by_hash:
                        functions_by_hash[func_hash] = []

                    functions_by_hash[func_hash].append((file_path, node.lineno, node.end_lineno, node.name))
                    function_source[func_hash] = func_source
        except SyntaxError:
            print(f"Ошибка синтаксиса в файле {file_path}, пропускаем")
            continue

    # Фильтруем только дублирующиеся функции
    duplicate_functions = []
    for func_hash, locations in functions_by_hash.items():
        if len(locations) > 1:
            duplicate_functions.append({
                'hash': func_hash,
                'source': function_source[func_hash],
                'locations': locations,
                'names': [loc[3] for loc in locations],
                'size': len(function_source[func_hash].splitlines())
            })

    # Сортируем дубликаты функций по размеру (от больших к маленьким)
    duplicate_functions.sort(key=lambda x: x['size'], reverse=True)

    print(f"Проанализировано {files_analyzed} файлов, {functions_analyzed} функций")
    print(f"Найдено {len(duplicate_functions)} дублирующихся функций")

    return duplicate_functions


# Пример использования
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Использование: python duplicate_code_functions.py file1.py [file2.py ...]")
        sys.exit(1)

    file_paths = sys.argv[1:]
    duplicates = analyze_functions(file_paths)

    # Выводим пример результатов
    for i, dup in enumerate(duplicates[:3]):  # Первые 3 дубликата
        print(f"\nДубликат функции #{i+1}:")
        print(f"Имена: {', '.join(dup['names'])}")
        print(f"Размер: {dup['size']} строк")
        print(f"Местоположения:")
        for loc in dup['locations']:
            print(f"  - {loc[0]}:{loc[1]}-{loc[2]} ('{loc[3]}')")

    if len(duplicates) > 3:
        print(f"\n... и еще {len(duplicates) - 3} дубликатов функций")
