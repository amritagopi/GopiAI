#!/usr/bin/env python
"""
Инструмент для семантического поиска по кодовой базе GopiAI и анализа зависимостей.
Использует индекс, созданный с помощью Llama Index.
"""

import argparse
import subprocess
import json
import os
import sys
from pathlib import Path

# Определяем пути
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INDEX_DIR = os.path.join(PROJECT_ROOT, "index")
CODE_SEARCH_SCRIPT = os.path.join(INDEX_DIR, "code_search.py")
DEPENDENCY_EXPLORER_SCRIPT = os.path.join(INDEX_DIR, "dependency_explorer.py")


def run_code_search(query, limit=5):
    """Выполняет семантический поиск по коду"""
    cmd = [sys.executable, CODE_SEARCH_SCRIPT, INDEX_DIR, query]

    print(f"Выполняем поиск: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при поиске: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Не удалось разобрать JSON из результата поиска"}


def explore_dependencies(search_term=None, file_path=None):
    """Анализирует зависимости файлов по поисковому запросу или конкретного файла"""
    if search_term:
        cmd = [sys.executable, DEPENDENCY_EXPLORER_SCRIPT, "--search", search_term]
    elif file_path:
        cmd = [sys.executable, DEPENDENCY_EXPLORER_SCRIPT, "--file", file_path]
    else:
        return {"error": "Необходимо указать поисковый запрос или путь к файлу"}

    print(f"Анализируем зависимости: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при анализе зависимостей: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Не удалось разобрать JSON из результата анализа"}


def print_search_results(results):
    """Форматирует и выводит результаты поиска"""
    if "error" in results:
        print(f"Ошибка: {results['error']}")
        return

    print("\n=== Результаты семантического поиска ===")
    print(f"Запрос: {results.get('query', 'Неизвестный запрос')}")

    if results.get("results"):
        for i, result in enumerate(results["results"], 1):
            print(f"\n[{i}] {result.get('file', 'Неизвестный файл')} (score: {result.get('score', 'N/A'):.4f})")
            content = result.get('content', '').strip()
            print(f"    {content[:300]}{'...' if len(content) > 300 else ''}")
    else:
        print("Результаты поиска не найдены")

    print(f"\nОбщий ответ: {results.get('response', 'Нет ответа')}")


def print_dependency_results(results):
    """Форматирует и выводит результаты анализа зависимостей"""
    if "error" in results:
        print(f"Ошибка: {results['error']}")
        return

    print("\n=== Результаты анализа зависимостей ===")

    if "files" in results and results["files"]:
        print(f"Найдено файлов: {len(results['files'])}")
        for file in results["files"]:
            print(f"\nФайл: {file}")
            if file in results.get("dependencies", {}):
                imports = results["dependencies"][file]
                if imports:
                    print("  Импорты:")
                    for imp in imports:
                        print(f"    - {imp}")
                else:
                    print("  Импорты не найдены")
    else:
        print("Файлы не найдены")


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Семантический поиск по коду и анализ зависимостей')
    subparsers = parser.add_subparsers(dest='command', help='Команда')

    # Команда поиска
    search_parser = subparsers.add_parser('search', help='Семантический поиск по коду')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--limit', type=int, default=5, help='Максимальное количество результатов')

    # Команда анализа зависимостей
    dep_parser = subparsers.add_parser('deps', help='Анализ зависимостей')
    dep_group = dep_parser.add_mutually_exclusive_group(required=True)
    dep_group.add_argument('--search', help='Поиск файлов по названию')
    dep_group.add_argument('--file', help='Анализ конкретного файла')

    args = parser.parse_args()

    # Проверяем наличие скриптов
    if not os.path.exists(CODE_SEARCH_SCRIPT):
        print(f"Ошибка: Скрипт поиска не найден по пути {CODE_SEARCH_SCRIPT}")
        return 1

    if not os.path.exists(DEPENDENCY_EXPLORER_SCRIPT):
        print(f"Ошибка: Скрипт анализа зависимостей не найден по пути {DEPENDENCY_EXPLORER_SCRIPT}")
        return 1

    # Выполняем команду
    if args.command == 'search':
        results = run_code_search(args.query, args.limit)
        print_search_results(results)
    elif args.command == 'deps':
        if args.search:
            results = explore_dependencies(search_term=args.search)
        else:  # args.file
            results = explore_dependencies(file_path=args.file)
        print_dependency_results(results)
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
