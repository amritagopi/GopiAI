#!/usr/bin/env python
"""
Координатор анализа дублирования кода в проекте GopiAI

Этот скрипт предоставляет интерфейс для поэтапного анализа дублирования кода.
Разбивает процесс на отдельные этапы с низкими требованиями к ресурсам.

Использование:
1. Запустите скрипт с аргументом 'prepare' для подготовки списка файлов
2. Запустите скрипт с аргументами 'fragments --batch N --total M' для анализа фрагментов батчами
3. Запустите скрипт с аргументом 'functions' для анализа функций
4. Запустите скрипт с аргументом 'classes' для анализа классов
5. Запустите скрипт с аргументом 'report' для создания итогового отчета
"""

import os
import sys
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

# Константы
DATA_DIR = "duplication_data"  # Директория для промежуточных данных
REPORT_DIR = "duplication_reports"  # Директория для итоговых отчетов
EXCLUDE_DIRS = {
    'venv', '.venv', '.git', '.github', '__pycache__',
    '.pytest_cache', '.cursor', '.backup', '.vscode',
    'temp', 'logs', 'assets', 'picked_icons'
}
EXCLUDE_FILES = {'icons_rc.py'}

# Создаем необходимые директории
for directory in [DATA_DIR, REPORT_DIR]:
    Path(directory).mkdir(exist_ok=True)


def find_python_files(root_dir='.'):
    """Находит все Python файлы для анализа"""
    print("Поиск Python файлов...")
    root_path = Path(root_dir)
    python_files = []

    for path in root_path.rglob('*.py'):
        # Проверяем, не находится ли файл в исключенных директориях
        if any(exclude_dir in path.parts for exclude_dir in EXCLUDE_DIRS):
            continue

        # Проверяем, не находится ли файл в списке исключенных файлов
        if path.name in EXCLUDE_FILES:
            continue

        # Добавляем файл в список для анализа
        python_files.append(str(path))

    print(f"Найдено {len(python_files)} Python-файлов для анализа")
    return python_files


def prepare_file_list():
    """Подготавливает список файлов для анализа и сохраняет его"""
    files = find_python_files()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Сохраняем список файлов
    files_path = Path(DATA_DIR) / f"python_files_{timestamp}.json"
    with open(files_path, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=2)

    print(f"Список файлов ({len(files)}) сохранен в {files_path}")

    # Создаем пустые файлы для результатов
    for result_type in ['fragments', 'functions', 'classes']:
        result_path = Path(DATA_DIR) / f"{result_type}_results_{timestamp}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Сохраняем метку времени для идентификации набора результатов
    timestamp_path = Path(DATA_DIR) / "current_timestamp.txt"
    with open(timestamp_path, 'w', encoding='utf-8') as f:
        f.write(timestamp)

    print(f"Подготовка завершена! Текущая метка времени: {timestamp}")
    print(f"Для анализа фрагментов используйте: python {sys.argv[0]} fragments --batch 1 --total 10")


def get_current_timestamp():
    """Получает текущую метку времени для идентификации набора результатов"""
    timestamp_path = Path(DATA_DIR) / "current_timestamp.txt"
    if not timestamp_path.exists():
        print("Ошибка: Сначала запустите скрипт с аргументом 'prepare'")
        sys.exit(1)

    with open(timestamp_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def load_file_list():
    """Загружает список файлов для анализа"""
    timestamp = get_current_timestamp()
    files_path = Path(DATA_DIR) / f"python_files_{timestamp}.json"

    if not files_path.exists():
        print(f"Ошибка: Не найден список файлов {files_path}")
        sys.exit(1)

    with open(files_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_partial_results(result_type, results):
    """Сохраняет результаты анализа"""
    timestamp = get_current_timestamp()
    result_path = Path(DATA_DIR) / f"{result_type}_results_{timestamp}.json"

    # Загружаем существующие результаты, если они есть
    if result_path.exists():
        with open(result_path, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
    else:
        existing_results = []

    # Добавляем новые результаты
    combined_results = existing_results + results

    # Сохраняем результаты
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(combined_results, f, indent=2, default=str)

    print(f"Результаты {result_type} сохранены, всего {len(combined_results)} элементов")


def analyze_fragments_batch(batch, total_batches):
    """Анализирует один батч файлов на поиск дублирующихся фрагментов"""
    if batch < 1 or batch > total_batches:
        print(f"Ошибка: Номер батча должен быть от 1 до {total_batches}")
        return

    from duplicate_code_fragments import analyze_fragments

    # Загружаем список файлов
    all_files = load_file_list()

    # Разбиваем на батчи
    batch_size = len(all_files) // total_batches
    if batch == total_batches:
        # Последний батч может быть больше
        files_batch = all_files[(batch-1)*batch_size:]
    else:
        files_batch = all_files[(batch-1)*batch_size:batch*batch_size]

    print(f"Анализируем батч {batch}/{total_batches}: {len(files_batch)} файлов")

    # Анализируем файлы в текущем батче
    results = analyze_fragments(files_batch)

    # Сохраняем результаты
    save_partial_results('fragments', results)

    print(f"Анализ батча {batch}/{total_batches} завершен")
    if batch < total_batches:
        print(f"Для анализа следующего батча используйте: python {sys.argv[0]} fragments --batch {batch+1} --total {total_batches}")
    else:
        print(f"Все батчи обработаны! Для анализа функций используйте: python {sys.argv[0]} functions")


def analyze_functions():
    """Анализирует файлы на поиск дублирующихся функций"""
    from duplicate_code_functions import analyze_functions

    # Загружаем список файлов
    files = load_file_list()

    print(f"Анализируем {len(files)} файлов на наличие дублирующихся функций")

    # Анализируем файлы
    results = analyze_functions(files)

    # Сохраняем результаты
    save_partial_results('functions', results)

    print(f"Анализ функций завершен")
    print(f"Для анализа классов используйте: python {sys.argv[0]} classes")


def analyze_classes():
    """Анализирует файлы на поиск дублирующихся классов"""
    from duplicate_code_classes import analyze_classes

    # Загружаем список файлов
    files = load_file_list()

    print(f"Анализируем {len(files)} файлов на наличие дублирующихся классов")

    # Анализируем файлы
    results = analyze_classes(files)

    # Сохраняем результаты
    save_partial_results('classes', results)

    print(f"Анализ классов завершен")
    print(f"Для создания итогового отчета используйте: python {sys.argv[0]} report")


def create_final_report():
    """Создает итоговый отчет на основе результатов анализа"""
    from duplicate_code_report import create_report

    # Получаем метку времени
    timestamp = get_current_timestamp()

    # Пути к файлам с результатами
    fragments_path = Path(DATA_DIR) / f"fragments_results_{timestamp}.json"
    functions_path = Path(DATA_DIR) / f"functions_results_{timestamp}.json"
    classes_path = Path(DATA_DIR) / f"classes_results_{timestamp}.json"

    # Проверяем наличие всех результатов
    required_files = [fragments_path, functions_path, classes_path]
    for file_path in required_files:
        if not file_path.exists():
            print(f"Ошибка: Не найден файл с результатами {file_path}")
            print(f"Убедитесь, что вы выполнили все этапы анализа")
            return

    # Загружаем результаты
    fragments = json.load(open(fragments_path, 'r', encoding='utf-8'))
    functions = json.load(open(functions_path, 'r', encoding='utf-8'))
    classes = json.load(open(classes_path, 'r', encoding='utf-8'))

    print(f"Создаем итоговый отчет на основе результатов анализа:")
    print(f"- Дублирующиеся фрагменты: {len(fragments)}")
    print(f"- Дублирующиеся функции: {len(functions)}")
    print(f"- Дублирующиеся классы: {len(classes)}")

    # Создаем отчет
    create_report(fragments, functions, classes)

    print(f"Итоговый отчет создан в директории {REPORT_DIR}")


def main():
    """Основная функция скрипта"""
    parser = argparse.ArgumentParser(
        description="Анализатор дублирования кода с низкими требованиями к ресурсам"
    )
    subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')

    # Подготовка списка файлов
    subparsers.add_parser('prepare', help='Подготовить список файлов для анализа')

    # Анализ фрагментов кода
    fragments_parser = subparsers.add_parser('fragments', help='Анализировать дублирующиеся фрагменты кода')
    fragments_parser.add_argument('--batch', type=int, required=True, help='Номер батча для обработки')
    fragments_parser.add_argument('--total', type=int, required=True, help='Общее количество батчей')

    # Анализ функций
    subparsers.add_parser('functions', help='Анализировать дублирующиеся функции')

    # Анализ классов
    subparsers.add_parser('classes', help='Анализировать дублирующиеся классы')

    # Создание отчета
    subparsers.add_parser('report', help='Создать итоговый отчет')

    args = parser.parse_args()

    if args.command == 'prepare':
        prepare_file_list()
    elif args.command == 'fragments':
        analyze_fragments_batch(args.batch, args.total)
    elif args.command == 'functions':
        analyze_functions()
    elif args.command == 'classes':
        analyze_classes()
    elif args.command == 'report':
        create_final_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
