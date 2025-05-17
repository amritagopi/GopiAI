#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для поиска заглушек в проекте GopiAI.
Ищет методы, которые действительно являются заглушками и требуют реализации.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
import glob


# Папки, которые нужно исключить из поиска
EXCLUDED_DIRS = {
    'venv', '.venv', 'env', '.env', '__pycache__',
    'node_modules', 'dist', 'build', '.git', '.idea', '.vscode',
    'backup', 'temp', 'tmp', 'logs', 'tests', 'test'
}

# Файлы, которые нужно исключить из поиска
EXCLUDED_FILES = {
    '.pyc', '.pyo', '.so', '.o', '.a', '.dll', '.lib', '.dylib',
    '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz',
    '.json', '.md', '.txt'
}

# Допустимые расширения файлов для поиска
ALLOWED_EXTENSIONS = {'.py', '.pyw'}

# Строгие индикаторы заглушек в коде - точные признаки того, что метод не реализован
STRICT_STUB_PATTERNS = [
    r'^\s*pass\s*(?:#.*)?$',  # Строка содержит только pass и, возможно, комментарий
    r'^\s*raise\s+NotImplementedError',  # Строка с NotImplementedError
    r'^\s*#\s*(?:TODO|FIXME|stub|заглушка)',  # Комментарий с TODO, FIXME или явным указанием заглушки
    r'^\s*""".*(?:TODO|FIXME|stub|заглушка).*"""',  # Строковый литерал с указанием заглушки
]

# Исключения - паттерны, которые указывают, что метод НЕ является заглушкой
NON_STUB_INDICATORS = [
    r'if\s+',  # Условные конструкции
    r'for\s+',  # Циклы for
    r'while\s+',  # Циклы while
    r'try\s*:',  # Блоки try/except
    r'except\s+',  # Блоки except
    r'return\s+[^None]',  # return с чем-то кроме None
    r'\s+self\.[a-zA-Z_][a-zA-Z0-9_]*\s*\(',  # Вызов метода объекта
    r'\s+self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=',  # Присваивание атрибуту объекта
    r'super\(\)',  # Вызов родительского метода
]


class StubFinder:
    """Класс для поиска заглушек в Python проектах."""

    def __init__(self, root_dir: str, exclusions: Optional[Set[str]] = None, verbose: bool = False):
        """
        Инициализирует искатель заглушек.

        Args:
            root_dir: Корневая директория проекта
            exclusions: Дополнительные пути для исключения
            verbose: Подробный вывод
        """
        self.root_dir = root_dir
        self.exclusions = exclusions or set()
        self.verbose = verbose

        # Скомпилированные регулярные выражения
        self.method_pattern = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
        self.strict_patterns = [re.compile(pattern) for pattern in STRICT_STUB_PATTERNS]
        self.non_stub_patterns = [re.compile(pattern) for pattern in NON_STUB_INDICATORS]

        # Паттерн для определения наследников класса Exception
        self.exception_subclass_pattern = re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*Exception[^)]*\):')

        self.stub_methods = {}  # Результаты поиска
        self.class_context = {}  # Для отслеживания классов исключений

    def _is_excluded_path(self, path: Path) -> bool:
        """Проверяет, нужно ли исключить путь из поиска."""
        # Проверяем исключения по частям пути
        for part in path.parts:
            if part in EXCLUDED_DIRS or part in self.exclusions:
                return True

        # Проверяем расширение файла
        if path.suffix.lower() in EXCLUDED_FILES:
            return True

        return False

    def _extract_method_body(self, content: str, method_start: int) -> Tuple[str, int, int]:
        """
        Извлекает тело метода из содержимого файла.

        Args:
            content: Содержимое файла
            method_start: Начальная позиция определения метода

        Returns:
            Кортеж (тело метода, начальная строка, конечная строка)
        """
        lines = content.split('\n')
        method_start_line = content[:method_start].count('\n')

        # Ищем тело метода
        method_body = []
        indent_level = None
        line_idx = method_start_line

        # Добавляем первую строку (с def)
        if line_idx < len(lines):
            first_line = lines[line_idx]
            method_body.append(first_line)
            # Определяем отступ первой строки с def
            indent_match = re.match(r'^(\s*)', first_line)
            if indent_match:
                indent_level = len(indent_match.group(1))
            line_idx += 1

        # Добавляем остальные строки, пока не встретим строку с тем же или меньшим отступом
        while line_idx < len(lines):
            line = lines[line_idx]

            # Пропускаем пустые строки
            if not line.strip():
                method_body.append(line)
                line_idx += 1
                continue

            # Если нашли строку с меньшим отступом, то тело метода закончилось
            if line.strip():  # Непустая строка
                current_indent = len(line) - len(line.lstrip())
                if indent_level is not None and current_indent <= indent_level:
                    break

            method_body.append(line)
            line_idx += 1

        return '\n'.join(method_body), method_start_line, line_idx - 1

    def _find_exception_subclasses(self, content: str):
        """
        Находит все подклассы Exception в файле и сохраняет их имена.
        """
        for match in self.exception_subclass_pattern.finditer(content):
            class_name = match.group(1)
            self.class_context[class_name] = 'Exception'

    def _is_exception_subclass(self, method_body: str) -> bool:
        """
        Проверяет, является ли метод частью подкласса Exception.
        """
        # Извлекаем имя класса из строки определения метода
        class_match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', method_body)
        if class_match:
            class_name = class_match.group(1)
            return class_name in self.class_context and self.class_context[class_name] == 'Exception'
        return False

    def _is_stub_method(self, method_body: str) -> bool:
        """
        Точно определяет, является ли метод заглушкой.

        Args:
            method_body: Тело метода, включая строку определения

        Returns:
            True, если метод является настоящей заглушкой, иначе False
        """
        # Исключаем методы подклассов Exception с телом 'pass'
        if 'pass' in method_body and self._is_exception_subclass(method_body):
            return False

        # Разделяем тело метода на строки, исключая строку определения
        body_lines = method_body.strip().split('\n')[1:]  # Исключаем строку с def

        # Если тело метода пустое, это заглушка
        if not body_lines:
            return True

        # Удаляем пустые строки и строки с комментариями
        non_empty_lines = [line for line in body_lines if line.strip() and not line.strip().startswith('#')]

        # Если после удаления пустых строк и комментариев ничего не осталось, это заглушка
        if not non_empty_lines:
            return True

        # Если тело состоит только из docstring и pass, это заглушка
        if len(non_empty_lines) <= 3:  # Максимум docstring (""" """) + pass
            has_docstring = False
            has_pass = False
            for line in non_empty_lines:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                if 'pass' in line:
                    has_pass = True

            # Проверяем наличие строгих индикаторов заглушки
            for pattern in self.strict_patterns:
                for line in non_empty_lines:
                    if pattern.search(line):
                        return True

            # Если тело состоит только из docstring и pass
            if has_docstring and has_pass and len(non_empty_lines) <= 3:
                return True

            # Если тело - только pass без docstring
            if has_pass and not has_docstring and len(non_empty_lines) == 1:
                return True

        # Проверяем наличие индикаторов не-заглушки
        for pattern in self.non_stub_patterns:
            for line in non_empty_lines:
                if pattern.search(line):
                    return False

        # Если тело содержит только простейшие присваивания и лог-сообщения,
        # но нет реальной логики, считаем заглушкой
        simple_expressions = 0
        for line in non_empty_lines:
            if re.search(r'^\s*self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=', line):
                simple_expressions += 1
            elif re.search(r'^\s*(?:print|logger\.[a-z]+)\(', line):
                simple_expressions += 1

        return simple_expressions == len(non_empty_lines)

    def find_stubs(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Находит все методы-заглушки в проекте.

        Returns:
            Словарь {путь_к_файлу: [(имя_метода, номер_строки)]}
        """
        root_path = Path(self.root_dir)

        # Перебираем все файлы в директории
        for path in root_path.glob('**/*'):
            if path.is_dir():
                continue

            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            rel_path = path.relative_to(root_path)

            if self._is_excluded_path(rel_path):
                if self.verbose:
                    print(f"Пропускаю {rel_path} (исключен)")
                continue

            try:
                if self.verbose:
                    print(f"Обрабатываю {rel_path}...")

                # Читаем файл
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Сначала находим все подклассы Exception
                self._find_exception_subclasses(content)

                # Затем ищем методы
                stubs = []
                for match in self.method_pattern.finditer(content):
                    method_name = match.group(1)
                    method_start = match.start()

                    # Пропускаем специальные методы (магические методы)
                    if method_name.startswith('__') and method_name.endswith('__'):
                        continue

                    try:
                        method_body, start_line, end_line = self._extract_method_body(content, method_start)

                        # Проверяем, является ли метод заглушкой
                        if self._is_stub_method(method_body):
                            stubs.append((method_name, start_line + 1))  # +1 для 1-индексации строк
                    except Exception as e:
                        if self.verbose:
                            print(f"Ошибка при обработке метода {method_name} в файле {rel_path}: {e}")

                if stubs:
                    self.stub_methods[str(rel_path)] = stubs

            except Exception as e:
                print(f"Ошибка при обработке файла {rel_path}: {e}")

        return self.stub_methods

    def write_report(self, output_path: str) -> None:
        """
        Записывает отчет о найденных заглушках в файл.

        Args:
            output_path: Путь к файлу для сохранения отчета
        """
        if not self.stub_methods:
            print("Заглушек не найдено.")
            return

        # Сортируем файлы по количеству заглушек
        sorted_files = sorted(self.stub_methods.items(), key=lambda x: len(x[1]), reverse=True)

        # Формируем отчет
        total_stubs = sum(len(stubs) for stubs in self.stub_methods.values())

        report = [
            f"# Отчет о найденных методах-заглушках",
            f"",
            f"Всего найдено **{total_stubs}** заглушек в **{len(self.stub_methods)}** файлах.",
            f"",
            f"## Список файлов с заглушками",
            f"",
        ]

        # Добавляем информацию о каждом файле
        for file_path, stubs in sorted_files:
            report.append(f"### {file_path} ({len(stubs)} заглушек)")
            report.append("")

            for method_name, line in stubs:
                report.append(f"- `{method_name}` (строка {line})")

            report.append("")

        # Записываем в файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        print(f"Отчет сохранен в {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Поиск заглушек в проекте GopiAI')
    parser.add_argument('--root', '-r', default='.', help='Корневая директория проекта')
    parser.add_argument('--exclude', '-e', nargs='+', default=[], help='Дополнительные папки для исключения')
    parser.add_argument('--output', '-o', default='stubs_report.md', help='Путь для сохранения результатов')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')

    args = parser.parse_args()

    # Добавляем пользовательские исключения
    exclusions = set(args.exclude)

    print(f"Поиск заглушек в директории: {args.root}")
    print(f"Исключенные директории: {', '.join(EXCLUDED_DIRS | exclusions)}")

    # Создаем искатель заглушек и запускаем поиск
    finder = StubFinder(args.root, exclusions, args.verbose)
    stub_methods = finder.find_stubs()

    # Выводим статистику
    total_stubs = sum(len(stubs) for stubs in stub_methods.values())
    print(f"\nНайдено {total_stubs} заглушек в {len(stub_methods)} файлах.")

    # Записываем отчет
    finder.write_report(args.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПоиск прерван пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
