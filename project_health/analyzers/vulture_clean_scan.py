#!/usr/bin/env python
"""
Анализатор неиспользуемого кода на основе vulture

Этот скрипт сканирует Python файлы проекта и находит:
- Неиспользуемые функции
- Неиспользуемые классы и методы
- Неиспользуемые переменные
- Неиспользуемые импорты

Результаты сортируются по категориям и сохраняются в отдельные файлы.
"""

import subprocess
import os
import re
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Конфигурация
EXCLUDED_FOLDERS = {
    "venv", ".venv", ".pytest_cache", "__pycache__",
    "temp", "logs", "picked_icons", "icons", "data",
    ".backup", ".git", ".github", "assets", "fonts",
    "compiled", ".cursor"
}
EXCLUDED_FILES = {
    "__init__.py", "setup.py", "conftest.py",
    "test_*.py", "*_test.py", "*_rc.py", "icons_rc.py"
}
MAX_FILE_SIZE_KB = 500  # Максимальный размер файла для анализа

# Директории, требующие особого внимания
IMPORTANT_DIRS = ["app", "GopiAI_Flow", "scripts", "config"]

# Настройки vulture
VULTURE_CMD = ["vulture", "--min-confidence", "80"]

# Пути для результатов
report_dir = Path("vulture_reports")
report_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result_path = report_dir / f"vulture_result_{timestamp}.txt"
summary_path = report_dir / f"vulture_summary_{timestamp}.txt"
json_path = report_dir / f"vulture_data_{timestamp}.json"
errors_path = report_dir / f"vulture_errors_{timestamp}.txt"

# Очистка файлов для записи
result_path.write_text("")
summary_path.write_text("")
errors_path.write_text("")

# Регулярные выражения для анализа вывода vulture
FUNCTION_PATTERN = re.compile(r"(.+):(\d+): unused (function|method) '(.+)'")
VARIABLE_PATTERN = re.compile(r"(.+):(\d+): unused (variable|attribute|property) '(.+)'")
CLASS_PATTERN = re.compile(r"(.+):(\d+): unused (class) '(.+)'")
IMPORT_PATTERN = re.compile(r"(.+):(\d+): unused (import) '(.+)'")
PARAM_PATTERN = re.compile(r"(.+):(\d+): unused (parameter) '(.+)'")

def is_valid_file(file: Path):
    """Проверяет, нужно ли анализировать данный файл"""
    # Проверка расширения
    if file.suffix != ".py":
        return False

    # Проверка на исключенные папки
    if any(excluded in file.parts for excluded in EXCLUDED_FOLDERS):
        return False

    # Проверка на исключенные файлы
    for pattern in EXCLUDED_FILES:
        if file.match(pattern):
            return False

    # Проверка размера
    if file.stat().st_size > MAX_FILE_SIZE_KB * 1024:
        print(f"Пропускаем слишком большой файл: {file} ({file.stat().st_size / 1024:.1f} KB)")
        return False

    return True

def analyze_vulture_output(output, file_path):
    """Анализирует вывод vulture и категоризирует результаты"""
    result = {
        "functions": [],
        "methods": [],
        "classes": [],
        "variables": [],
        "attributes": [],
        "imports": [],
        "parameters": [],
        "other": []
    }

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Проверяем разные шаблоны
        function_match = FUNCTION_PATTERN.match(line)
        variable_match = VARIABLE_PATTERN.match(line)
        class_match = CLASS_PATTERN.match(line)
        import_match = IMPORT_PATTERN.match(line)
        param_match = PARAM_PATTERN.match(line)

        if function_match:
            _, line_num, kind, name = function_match.groups()
            if kind == "function":
                result["functions"].append({"name": name, "line": int(line_num)})
            else:  # method
                result["methods"].append({"name": name, "line": int(line_num)})

        elif variable_match:
            _, line_num, kind, name = variable_match.groups()
            if kind == "variable":
                result["variables"].append({"name": name, "line": int(line_num)})
            else:  # attribute or property
                result["attributes"].append({"name": name, "line": int(line_num)})

        elif class_match:
            _, line_num, _, name = class_match.groups()
            result["classes"].append({"name": name, "line": int(line_num)})

        elif import_match:
            _, line_num, _, name = import_match.groups()
            result["imports"].append({"name": name, "line": int(line_num)})

        elif param_match:
            _, line_num, _, name = param_match.groups()
            result["parameters"].append({"name": name, "line": int(line_num)})

        else:
            result["other"].append({"text": line})

    return result

def format_findings_for_display(findings, file_path):
    """Форматирует результаты для отображения"""
    output = []

    if any(len(findings[key]) > 0 for key in findings):
        output.append(f"\n=== {file_path} ===\n")

        for key in ["functions", "methods", "classes", "variables", "attributes", "imports", "parameters"]:
            items = findings[key]
            if items:
                category_name = key.capitalize()
                output.append(f"  {category_name} ({len(items)}):")
                for item in items:
                    output.append(f"    - '{item['name']}' (строка {item['line']})")

        for item in findings["other"]:
            output.append(f"  {item['text']}")

    return "\n".join(output)

def append_to_file(file_path, text):
    """Добавляет текст в файл"""
    with open(file_path, 'a', encoding='utf-8', errors='ignore') as f:
        f.write(text)

def main():
    """Основная функция скрипта"""
    print(f"Анализатор неиспользуемого кода (на основе vulture)")
    print("-" * 70)

    # Собираем все Python файлы для анализа
    files = [f for f in Path(".").rglob("*.py") if is_valid_file(f)]
    print(f"Найдено {len(files)} Python файлов для анализа")

    # Статистика по директориям
    dir_stats = defaultdict(int)
    for file in files:
        parent = file.parent.as_posix()
        dir_stats[parent] += 1

    print("\nРаспределение файлов по директориям:")
    for directory, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        if directory == ".":
            directory = "корневая директория"
        print(f"  {directory}: {count} файлов")

    # Результаты и статистика
    results = {}
    statistics = {
        "total_files": len(files),
        "files_with_unused_code": 0,
        "unused_counts": {
            "functions": 0,
            "methods": 0,
            "classes": 0,
            "variables": 0,
            "attributes": 0,
            "imports": 0,
            "parameters": 0,
            "other": 0
        },
        "important_dirs": {dir_name: 0 for dir_name in IMPORTANT_DIRS}
    }

    # Сканируем файлы
    print(f"\nСканирование файлов на наличие неиспользуемого кода...")

    file_count = 0
    for file in files:
        file_count += 1
        if file_count % 50 == 0:
            print(f"Обработано {file_count}/{len(files)} файлов...")

        try:
            # Запускаем vulture для анализа файла
            output = subprocess.check_output(
                VULTURE_CMD + [str(file)],
                stderr=subprocess.STDOUT,
                text=True
            )

            # Если vulture что-то нашел
            if output.strip():
                # Анализируем вывод
                findings = analyze_vulture_output(output, file)

                # Сохраняем результаты
                results[str(file)] = findings

                # Обновляем статистику
                statistics["files_with_unused_code"] += 1

                for key in findings:
                    statistics["unused_counts"][key] += len(findings[key])

                # Особое внимание к важным директориям
                for important_dir in IMPORTANT_DIRS:
                    if str(file).startswith(important_dir):
                        statistics["important_dirs"][important_dir] += 1

                # Записываем в основной файл результатов
                formatted_output = format_findings_for_display(findings, file)
                append_to_file(result_path, formatted_output)

        except subprocess.CalledProcessError as e:
            append_to_file(errors_path, f"\n=== {file} ===\n{e.output}\n")
        except Exception as e:
            append_to_file(errors_path, f"\n=== {file} ===\nОшибка: {str(e)}\n")

    # Формируем итоговый отчет
    summary = [
        f"ОТЧЕТ ПО АНАЛИЗУ НЕИСПОЛЬЗУЕМОГО КОДА",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"ОБЩАЯ СТАТИСТИКА:",
        f"- Всего проанализировано файлов: {statistics['total_files']}",
        f"- Файлов с неиспользуемым кодом: {statistics['files_with_unused_code']} " +
        f"({statistics['files_with_unused_code'] / max(1, statistics['total_files']) * 100:.1f}%)",
        f"",
        f"НАЙДЕНО НЕИСПОЛЬЗУЕМЫХ ЭЛЕМЕНТОВ:",
        f"- Функций: {statistics['unused_counts']['functions']}",
        f"- Методов: {statistics['unused_counts']['methods']}",
        f"- Классов: {statistics['unused_counts']['classes']}",
        f"- Переменных: {statistics['unused_counts']['variables']}",
        f"- Атрибутов: {statistics['unused_counts']['attributes']}",
        f"- Импортов: {statistics['unused_counts']['imports']}",
        f"- Параметров: {statistics['unused_counts']['parameters']}",
        f"",
        f"ВАЖНЫЕ ДИРЕКТОРИИ С НЕИСПОЛЬЗУЕМЫМ КОДОМ:"
    ]

    for dir_name, count in statistics["important_dirs"].items():
        if count > 0:
            summary.append(f"- {dir_name}: {count} файлов")

    # Топ файлов с наибольшим количеством неиспользуемого кода
    file_rankings = []
    for file_path, findings in results.items():
        unused_count = sum(len(findings[key]) for key in findings)
        file_rankings.append((file_path, unused_count))

    if file_rankings:
        summary.append(f"\nТОП-10 ФАЙЛОВ С НАИБОЛЬШИМ КОЛИЧЕСТВОМ НЕИСПОЛЬЗУЕМОГО КОДА:")
        for file_path, count in sorted(file_rankings, key=lambda x: x[1], reverse=True)[:10]:
            summary.append(f"- {file_path}: {count} элементов")

    summary.append(f"\nПОДРОБНЫЕ РЕЗУЛЬТАТЫ:")
    summary.append(f"- Полный отчет: {result_path}")
    summary.append(f"- Ошибки при анализе: {errors_path}")
    summary.append(f"- JSON-данные: {json_path}")

    # Записываем итоговый отчет
    summary_path.write_text("\n".join(summary), encoding="utf-8")

    # Сохраняем результаты в JSON для дальнейшего анализа
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "statistics": statistics,
            "results": results
        }, f, indent=2)

    print("\nАнализ завершен!")
    print(f"Итоговый отчет: {summary_path}")
    print(f"Подробные результаты: {result_path}")
    print(f"JSON-данные: {json_path}")

    # Подводим краткий итог
    print("\nКРАТКАЯ СВОДКА:")
    print(f"- Всего проанализировано: {statistics['total_files']} Python файлов")
    print(f"- Файлов с неиспользуемым кодом: {statistics['files_with_unused_code']}")
    print(f"- Всего найдено неиспользуемых элементов: " +
          f"{sum(statistics['unused_counts'].values())}")

if __name__ == "__main__":
    main()
