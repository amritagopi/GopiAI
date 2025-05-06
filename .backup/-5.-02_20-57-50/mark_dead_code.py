#!/usr/bin/env python
"""
Утилита для пометки "мертвого кода" в проекте

Этот скрипт выполняет следующие действия:
1. Читает результаты анализа неиспользуемых файлов и функций
2. Проверяет файл goodfiles.txt для исключений
3. Переименовывает неиспользуемые файлы, добавляя префикс "deprecated_"
4. Добавляет комментарии к неиспользуемым функциям
5. Создает отчет о проделанных изменениях

Использование:
    python mark_dead_code.py [--dry-run]

Опции:
    --dry-run  Запуск без фактического внесения изменений (только показ планируемых действий)
"""

import os
import json
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

# Константы
GOOD_FILES_LIST = "goodfiles.txt"
IMPORTS_REPORT_DIR = "imports_reports"
VULTURE_REPORT_DIR = "vulture_reports"
OUTPUT_DIR = "marked_code_reports"
DEPRECATED_PREFIX = "deprecated_"

# Создаем директорию для отчетов, если она не существует
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Отметка времени для имен файлов
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_path = Path(OUTPUT_DIR) / f"mark_dead_code_report_{timestamp}.txt"
changes_summary_path = Path(OUTPUT_DIR) / f"changes_summary_{timestamp}.txt"

# Флаг сухого запуска
dry_run = "--dry-run" in sys.argv


def load_good_files() -> set:
    """Загружает список файлов, которые не следует помечать как устаревшие"""
    good_files = set()
    try:
        if Path(GOOD_FILES_LIST).exists():
            with open(GOOD_FILES_LIST, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if line and not line.startswith('#'):
                        # Нормализуем путь для кросс-платформенности
                        normalized_path = line.replace('\\', '/')
                        good_files.add(normalized_path)
            print(f"Загружено {len(good_files)} исключений из {GOOD_FILES_LIST}")
        else:
            print(f"Файл {GOOD_FILES_LIST} не найден, исключения не загружены")
    except Exception as e:
        print(f"Ошибка при загрузке файла исключений: {str(e)}")

    return good_files


def find_latest_report(report_dir: str, pattern: str) -> str:
    """Находит самый последний отчет в указанной директории"""
    if not Path(report_dir).exists():
        print(f"Директория {report_dir} не найдена")
        return ""

    all_files = list(Path(report_dir).glob(pattern))
    if not all_files:
        print(f"Отчеты, соответствующие шаблону {pattern}, не найдены в {report_dir}")
        return ""

    # Сортируем по времени модификации (от новых к старым)
    latest_file = max(all_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)


def load_unused_files() -> list:
    """Загружает список неиспользуемых файлов из последнего отчета"""
    latest_report = find_latest_report(IMPORTS_REPORT_DIR, "unused_files_data_*.json")
    if not latest_report:
        return []

    try:
        with open(latest_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
            unused_files = data.get("unused_files", [])
            print(f"Загружено {len(unused_files)} неиспользуемых файлов из {latest_report}")
            return unused_files
    except Exception as e:
        print(f"Ошибка при загрузке неиспользуемых файлов: {str(e)}")
        return []


def load_unused_code_parts() -> dict:
    """Загружает информацию о неиспользуемых частях кода из последнего отчета vulture"""
    latest_report = find_latest_report(VULTURE_REPORT_DIR, "vulture_data_*.json")
    if not latest_report:
        return {}

    try:
        with open(latest_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get("results", {})
            print(f"Загружена информация о неиспользуемом коде из {latest_report}")
            return results
    except Exception as e:
        print(f"Ошибка при загрузке информации о неиспользуемом коде: {str(e)}")
        return {}


def should_process_file(file_path: str, good_files: set) -> bool:
    """Проверяет, следует ли обрабатывать данный файл"""
    # Нормализуем путь для сравнения
    normalized_path = file_path.replace('\\', '/')

    # Проверяем прямое совпадение
    if normalized_path in good_files:
        return False

    # Проверяем частичное совпадение
    for good_file in good_files:
        if normalized_path.endswith(good_file):
            return False

    return True


def mark_file_as_deprecated(file_path: str, dry_run: bool = False) -> tuple:
    """
    Переименовывает файл, добавляя префикс 'deprecated_'

    Возвращает:
        tuple: (успех, старый_путь, новый_путь)
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False, file_path, ""

        # Получаем директорию и имя файла
        directory = path.parent
        filename = path.name

        # Если файл уже помечен как устаревший, пропускаем
        if filename.startswith(DEPRECATED_PREFIX):
            return False, file_path, ""

        # Формируем новое имя файла
        new_filename = f"{DEPRECATED_PREFIX}{filename}"
        new_path = directory / new_filename

        # Проверяем, существует ли файл с новым именем
        if new_path.exists():
            return False, file_path, str(new_path)

        # Переименовываем файл
        if not dry_run:
            path.rename(new_path)

        return True, file_path, str(new_path)
    except Exception as e:
        print(f"Ошибка при переименовании файла {file_path}: {str(e)}")
        return False, file_path, ""


def add_deprecated_comments(file_path: str, unused_code: dict, dry_run: bool = False) -> list:
    """
    Добавляет комментарии к неиспользуемым частям кода

    Возвращает:
        list: список модифицированных частей кода
    """
    if not Path(file_path).exists() or not unused_code:
        return []

    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        modified_parts = []

        # Категории кода, которые нужно пометить
        categories = [
            ('functions', '# DEPRECATED: Неиспользуемая функция'),
            ('methods', '# DEPRECATED: Неиспользуемый метод'),
            ('classes', '# DEPRECATED: Неиспользуемый класс'),
            ('variables', '# DEPRECATED: Неиспользуемая переменная'),
            ('imports', '# DEPRECATED: Неиспользуемый импорт')
        ]

        # Проходим по каждой категории
        for category, comment in categories:
            if category in unused_code:
                for item in unused_code[category]:
                    line_num = item.get('line', 0)
                    name = item.get('name', '')

                    if line_num > 0 and line_num <= len(lines):
                        line_index = line_num - 1  # Индексация с 0
                        line = lines[line_index]

                        # Проверяем, что комментарий еще не добавлен
                        if 'DEPRECATED' not in line:
                            # Добавляем комментарий в конец строки
                            lines[line_index] = line.rstrip() + f"  {comment}\n"
                            modified_parts.append({
                                'type': category,
                                'name': name,
                                'line': line_num,
                                'original': line.strip(),
                                'modified': lines[line_index].strip()
                            })

        # Записываем изменения в файл
        if modified_parts and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        return modified_parts
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {str(e)}")
        return []


def main():
    """Основная функция скрипта"""
    print(f"Утилита для пометки 'мертвого кода' в проекте")
    print(f"Режим: {'Без изменений (dry-run)' if dry_run else 'С внесением изменений'}")
    print("-" * 70)

    # Загружаем список "хороших" файлов, которые не следует менять
    good_files = load_good_files()

    # Загружаем список неиспользуемых файлов
    unused_files = load_unused_files()

    # Загружаем информацию о неиспользуемом коде
    unused_code_parts = load_unused_code_parts()

    # Статистика изменений
    renamed_files = []
    skipped_files = []
    modified_files = []

    # Обрабатываем неиспользуемые файлы
    print(f"\nОбработка неиспользуемых файлов...")
    for file_path in unused_files:
        if should_process_file(file_path, good_files):
            success, old_path, new_path = mark_file_as_deprecated(file_path, dry_run)
            if success:
                renamed_files.append((old_path, new_path))
                print(f"Переименован: {old_path} -> {new_path}")
            else:
                skipped_files.append(file_path)
                print(f"Пропущен: {file_path}")
        else:
            skipped_files.append(file_path)
            print(f"Исключен: {file_path} (в списке исключений)")

    # Обрабатываем неиспользуемые части кода
    print(f"\nОбработка неиспользуемых частей кода...")
    for file_path, code_parts in unused_code_parts.items():
        # Пропускаем файлы, которые уже переименовали
        if any(file_path == old_path for old_path, _ in renamed_files):
            continue

        # Проверяем, следует ли обрабатывать файл
        if should_process_file(file_path, good_files):
            modified_parts = add_deprecated_comments(file_path, code_parts, dry_run)
            if modified_parts:
                modified_files.append((file_path, modified_parts))
                print(f"Модифицирован: {file_path} ({len(modified_parts)} частей кода)")

    # Формируем отчет
    report = [
        f"ОТЧЕТ ПО ПОМЕТКЕ 'МЕРТВОГО КОДА'",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Режим: {'Без изменений (dry-run)' if dry_run else 'С внесением изменений'}",
        f"",
        f"ОБЩАЯ СТАТИСТИКА:",
        f"- Всего неиспользуемых файлов: {len(unused_files)}",
        f"- Переименовано файлов: {len(renamed_files)}",
        f"- Пропущено файлов: {len(skipped_files)}",
        f"- Модифицировано файлов с неиспользуемым кодом: {len(modified_files)}",
        f"",
        f"ПЕРЕИМЕНОВАННЫЕ ФАЙЛЫ:"
    ]

    # Добавляем информацию о переименованных файлах
    for old_path, new_path in renamed_files:
        report.append(f"- {old_path} -> {new_path}")

    # Информация о пропущенных файлах
    if skipped_files:
        report.append(f"\nПРОПУЩЕННЫЕ ФАЙЛЫ:")
        for file_path in skipped_files:
            report.append(f"- {file_path}")

    # Информация о модифицированных файлах
    if modified_files:
        report.append(f"\nМОДИФИЦИРОВАННЫЕ ФАЙЛЫ:")
        for file_path, parts in modified_files:
            report.append(f"\n{file_path}:")
            for part in parts:
                report.append(f"  - '{part['name']}' (строка {part['line']})")
                report.append(f"    До: {part['original']}")
                report.append(f"    После: {part['modified']}")

    # Сохраняем подробный отчет
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    # Создаем краткую сводку изменений
    summary = [
        f"СВОДКА ИЗМЕНЕНИЙ",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"- Переименовано файлов: {len(renamed_files)}",
        f"- Модифицировано файлов: {len(modified_files)}",
        f"- Пропущено файлов: {len(skipped_files)}",
        f"",
        f"Подробный отчет: {report_path}"
    ]

    # Сохраняем сводку
    with open(changes_summary_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary))

    print(f"\nОбработка завершена!")
    print(f"Отчет сохранен: {report_path}")
    print(f"Сводка изменений: {changes_summary_path}")


if __name__ == "__main__":
    main()
