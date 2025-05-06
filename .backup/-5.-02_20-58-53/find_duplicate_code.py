#!/usr/bin/env python
"""
Анализатор дублирования кода в проекте GopiAI

Этот скрипт выполняет следующие действия:
1. Сканирует все Python файлы проекта
2. Анализирует синтаксические конструкции и содержимое
3. Выявляет дублирующиеся фрагменты кода
4. Группирует дубликаты по типам и размерам
5. Формирует рекомендации по рефакторингу
6. Генерирует подробный отчет

Результаты сохраняются в директорию 'duplication_reports'
"""

import ast
import difflib
import hashlib
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Константы
REPORT_DIR = "duplication_reports"
MIN_DUPLICATE_LINES = 4  # Минимальное количество строк для детекции дубликата
MIN_TOKEN_LENGTH = 100   # Минимальная длина токенов для детекции дубликата
EXCLUDE_DIRS = {
    'venv', '.venv', '.git', '.github', '__pycache__',
    '.pytest_cache', '.cursor', '.backup', '.vscode',
    'temp', 'logs', 'assets', 'picked_icons'
}
EXCLUDE_FILES = {'icons_rc.py'}

# Создаем директорию для отчетов, если она отсутствует
Path(REPORT_DIR).mkdir(exist_ok=True)

# Текущая метка времени для имен файлов
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


class DuplicateCodeFinder:
    """Основной класс для поиска дублирующегося кода в проекте"""

    def __init__(self, min_lines: int = MIN_DUPLICATE_LINES, min_tokens: int = MIN_TOKEN_LENGTH):
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.files_analyzed = 0
        self.lines_analyzed = 0
        self.duplicate_fragments = []
        self.duplicate_functions = []
        self.duplicate_classes = []
        self.files_with_duplicates = set()
        self.method_signatures = {}
        self.syntax_patterns = {}
        self.ast_hashes = {}

    def find_python_files(self, root_dir: Union[str, Path] = '.') -> List[Path]:
        """Находит все Python файлы в проекте, исключая указанные директории"""
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
            python_files.append(path)

        print(f"Найдено {len(python_files)} Python-файлов для анализа")
        return python_files

    def read_file_content(self, file_path: Path) -> Tuple[str, List[str]]:
        """Читает содержимое файла и возвращает его как строку и список строк"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                return content, lines
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return "", []

    def hash_ast_node(self, node: ast.AST) -> str:
        """
        Создает хеш AST-узла для сравнения семантически эквивалентных фрагментов

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
                        fields.append((field, [self.hash_ast_node(v) for v in value if isinstance(v, ast.AST)]))
                    elif isinstance(value, ast.AST):
                        fields.append((field, self.hash_ast_node(value)))

            node_hash = f"{type(node).__name__}({','.join(f'{f}={v}' for f, v in fields)})"
            return hashlib.md5(node_hash.encode('utf-8')).hexdigest()
        else:
            # Для других типов (не AST) используем строковое представление
            return str(type(node).__name__)

    def find_duplicate_fragments(self, file_paths: List[Path]) -> None:
        """Находит дублирующиеся фрагменты кода в указанных файлах"""
        print("Анализ дублирования фрагментов кода...")

        # Словарь для хранения хешей фрагментов кода и их расположения
        fragments_by_hash = defaultdict(list)
        content_chunks = {}

        for file_path in file_paths:
            content, lines = self.read_file_content(file_path)
            if not content:
                continue

            self.files_analyzed += 1
            self.lines_analyzed += len(lines)

            # Обработка файла построчно с использованием скользящего окна
            for i in range(len(lines) - self.min_lines + 1):
                chunk = '\n'.join(lines[i:i + self.min_lines])
                # Игнорируем фрагменты с малым количеством значимых символов
                if len(re.sub(r'\s', '', chunk)) < self.min_tokens / 4:
                    continue

                chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                fragments_by_hash[chunk_hash].append((file_path, i, i + self.min_lines))
                content_chunks[chunk_hash] = chunk

            # Также ищем более длинные дублирующиеся фрагменты
            for window_size in range(self.min_lines + 1, min(30, len(lines) + 1)):
                for i in range(len(lines) - window_size + 1):
                    chunk = '\n'.join(lines[i:i + window_size])
                    chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                    fragments_by_hash[chunk_hash].append((file_path, i, i + window_size))
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
                    self.duplicate_fragments.append({
                        'hash': chunk_hash,
                        'content': content_chunks[chunk_hash],
                        'locations': locations,
                        'size': len(content_chunks[chunk_hash].splitlines())
                    })

                    # Добавляем файлы с дубликатами в набор
                    for loc in locations:
                        self.files_with_duplicates.add(str(loc[0]))

        # Сортируем дубликаты по размеру (от больших к маленьким)
        self.duplicate_fragments.sort(key=lambda x: x['size'], reverse=True)

        # Удаляем перекрывающиеся дубликаты (если меньший дубликат полностью содержится в большем)
        self._remove_overlapping_duplicates()

        print(f"Найдено {len(self.duplicate_fragments)} дублирующихся фрагментов кода")

    def _remove_overlapping_duplicates(self) -> None:
        """Удаляет перекрывающиеся дубликаты из результатов"""
        if not self.duplicate_fragments:
            return

        non_overlapping = []
        seen_locations = set()

        for dup in self.duplicate_fragments:
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
                    for i in range(start, end + 1):
                        seen_locations.add((str(file_path), start, end))

        self.duplicate_fragments = non_overlapping

    def find_duplicate_functions(self, file_paths: List[Path]) -> None:
        """Находит дублирующиеся функции в указанных файлах"""
        print("Анализ дублирования функций...")

        # Словарь для хранения хешей функций и их расположения
        functions_by_hash = defaultdict(list)
        function_source = {}

        for file_path in file_paths:
            content, _ = self.read_file_content(file_path)
            if not content:
                continue

            try:
                # Парсим исходный код в AST
                tree = ast.parse(content)

                # Обходим все узлы AST, соответствующие функциям
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Получаем исходный код функции
                        func_lines = content.splitlines()[node.lineno - 1:node.end_lineno]
                        func_source = '\n'.join(func_lines)

                        # Создаем хеш для функции на основе ее AST
                        func_hash = self.hash_ast_node(node)
                        functions_by_hash[func_hash].append((file_path, node.lineno, node.end_lineno, node.name))
                        function_source[func_hash] = func_source
            except SyntaxError:
                print(f"Ошибка синтаксиса в файле {file_path}, пропускаем")
                continue

        # Фильтруем только дублирующиеся функции
        for func_hash, locations in functions_by_hash.items():
            if len(locations) > 1:
                self.duplicate_functions.append({
                    'hash': func_hash,
                    'source': function_source[func_hash],
                    'locations': locations,
                    'names': [loc[3] for loc in locations],
                    'size': len(function_source[func_hash].splitlines())
                })

                # Добавляем файлы с дубликатами функций в набор
                for loc in locations:
                    self.files_with_duplicates.add(str(loc[0]))

        # Сортируем дубликаты функций по размеру (от больших к маленьким)
        self.duplicate_functions.sort(key=lambda x: x['size'], reverse=True)

        print(f"Найдено {len(self.duplicate_functions)} дублирующихся функций")

    def find_duplicate_classes(self, file_paths: List[Path]) -> None:
        """Находит дублирующиеся классы в указанных файлах"""
        print("Анализ дублирования классов...")

        # Словарь для хранения хешей классов и их расположения
        classes_by_hash = defaultdict(list)
        class_source = {}

        for file_path in file_paths:
            content, _ = self.read_file_content(file_path)
            if not content:
                continue

            try:
                # Парсим исходный код в AST
                tree = ast.parse(content)

                # Обходим все узлы AST, соответствующие классам
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Получаем исходный код класса
                        class_lines = content.splitlines()[node.lineno - 1:node.end_lineno]
                        cls_source = '\n'.join(class_lines)

                        # Создаем хеш для класса на основе его AST
                        class_hash = self.hash_ast_node(node)
                        classes_by_hash[class_hash].append((file_path, node.lineno, node.end_lineno, node.name))
                        class_source[class_hash] = cls_source
            except SyntaxError:
                print(f"Ошибка синтаксиса в файле {file_path}, пропускаем")
                continue

        # Фильтруем только дублирующиеся классы
        for class_hash, locations in classes_by_hash.items():
            if len(locations) > 1:
                self.duplicate_classes.append({
                    'hash': class_hash,
                    'source': class_source[class_hash],
                    'locations': locations,
                    'names': [loc[3] for loc in locations],
                    'size': len(class_source[class_hash].splitlines())
                })

                # Добавляем файлы с дубликатами классов в набор
                for loc in locations:
                    self.files_with_duplicates.add(str(loc[0]))

        # Сортируем дубликаты классов по размеру (от больших к маленьким)
        self.duplicate_classes.sort(key=lambda x: x['size'], reverse=True)

        print(f"Найдено {len(self.duplicate_classes)} дублирующихся классов")

    def analyze_common_patterns(self) -> Dict[str, List[Dict]]:
        """Анализирует общие шаблоны в дублированном коде"""
        patterns = {
            'file_operations': [],
            'api_calls': [],
            'gui_elements': [],
            'data_processing': [],
            'utility_functions': []
        }

        # Ключевые слова для каждой категории
        keywords = {
            'file_operations': ['open(', 'read', 'write', 'close', 'file', 'path', 'Path(', 'os.path', 'glob'],
            'api_calls': ['requests', 'get(', 'post(', 'api', 'json.loads', 'json.dumps', 'response', 'http'],
            'gui_elements': ['QWidget', 'QLayout', 'Button', 'Window', 'Interface', 'GUI', 'render', 'draw'],
            'data_processing': ['DataFrame', 'data', 'process', 'parse', 'filter', 'map', 'reduce', 'transform'],
            'utility_functions': ['util', 'helper', 'format', 'convert', 'validate', 'check', 'print_']
        }

        # Анализируем дублирующиеся функции
        for func in self.duplicate_functions:
            for category, words in keywords.items():
                if any(word in func['source'] for word in words):
                    patterns[category].append({
                        'type': 'function',
                        'names': func['names'],
                        'size': func['size'],
                        'locations': [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in func['locations']]
                    })
                    break

        # Анализируем дублирующиеся фрагменты
        for fragment in self.duplicate_fragments:
            for category, words in keywords.items():
                if any(word in fragment['content'] for word in words):
                    patterns[category].append({
                        'type': 'fragment',
                        'size': fragment['size'],
                        'locations': [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in fragment['locations']]
                    })
                    break

        return patterns

    def generate_refactoring_recommendations(self) -> List[Dict]:
        """Генерирует рекомендации по рефакторингу дублированного кода"""
        recommendations = []

        # Рекомендации по функциям
        for i, func in enumerate(self.duplicate_functions[:10]):  # Топ-10 дублирующихся функций
            names = func['names']
            similar_name = self._find_common_name(names)

            recommendation = {
                'id': f"FUNC_{i+1}",
                'type': 'function',
                'priority': 'high' if func['size'] > 15 else 'medium',
                'suggestion': f"Вынести функцию '{similar_name}' в общий модуль utilities.py",
                'impact': f"Устранит дублирование в {len(func['locations'])} местах, {func['size']} строк кода",
                'locations': [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in func['locations']]
            }
            recommendations.append(recommendation)

        # Рекомендации по классам
        for i, cls in enumerate(self.duplicate_classes[:5]):  # Топ-5 дублирующихся классов
            names = cls['names']
            similar_name = self._find_common_name(names)

            recommendation = {
                'id': f"CLASS_{i+1}",
                'type': 'class',
                'priority': 'high',
                'suggestion': f"Создать базовый класс '{similar_name}Base' в общем модуле",
                'impact': f"Устранит дублирование в {len(cls['locations'])} местах, {cls['size']} строк кода",
                'locations': [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in cls['locations']]
            }
            recommendations.append(recommendation)

        # Рекомендации по фрагментам кода
        fragment_count = 0
        for fragment in self.duplicate_fragments:
            if fragment['size'] >= 10 and fragment_count < 10:  # Только длинные фрагменты, не более 10
                # Определяем тип фрагмента на основе его содержимого
                fragment_type = self._determine_fragment_type(fragment['content'])

                recommendation = {
                    'id': f"FRAG_{fragment_count+1}",
                    'type': 'fragment',
                    'priority': 'medium' if fragment['size'] > 20 else 'low',
                    'suggestion': f"Вынести {fragment_type} код в отдельную функцию",
                    'impact': f"Устранит дублирование в {len(fragment['locations'])} местах, {fragment['size']} строк кода",
                    'locations': [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in fragment['locations']]
                }
                recommendations.append(recommendation)
                fragment_count += 1

        # Сортируем рекомендации по приоритету
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order[x['priority']])

        return recommendations

    def _find_common_name(self, names: List[str]) -> str:
        """Находит общее имя среди списка имен функций или классов"""
        if not names:
            return "Unknown"

        if len(names) == 1:
            return names[0]

        # Используем difflib для нахождения наиболее похожих имен
        sequences = [difflib.SequenceMatcher(None, names[0], name) for name in names[1:]]
        ratios = [seq.ratio() for seq in sequences]

        # Если есть очень похожие имена, используем первое
        if any(ratio > 0.8 for ratio in ratios):
            return names[0]

        # Иначе пытаемся найти общую часть в именах
        common_prefix = os.path.commonprefix(names)
        if len(common_prefix) > 3:
            return common_prefix

        # Если нет явного общего префикса, используем первое имя
        return names[0]

    def _determine_fragment_type(self, content: str) -> str:
        """Определяет тип фрагмента кода на основе его содержимого"""
        if any(keyword in content for keyword in ['open(', 'read', 'write', 'Path']):
            return "файловые операции"
        elif any(keyword in content for keyword in ['requests', 'http', 'api', 'json']):
            return "сетевой"
        elif any(keyword in content for keyword in ['def', 'return', 'yield']):
            return "функциональный"
        elif any(keyword in content for keyword in ['class', '__init__']):
            return "объектно-ориентированный"
        elif any(keyword in content for keyword in ['if', 'else', 'for', 'while']):
            return "логический"
        else:
            return "повторяющийся"

    def generate_statistics(self) -> Dict:
        """Генерирует статистику по дублированию кода в проекте"""
        # Общая статистика
        total_duplicate_lines = sum(fragment['size'] for fragment in self.duplicate_fragments)
        total_duplicate_lines += sum(func['size'] for func in self.duplicate_functions)
        total_duplicate_lines += sum(cls['size'] for cls in self.duplicate_classes)

        # Дублирование по файлам
        files_count = len(self.files_with_duplicates)

        # Дублирование по директориям
        dirs_with_duplicates = defaultdict(int)
        for file_path in self.files_with_duplicates:
            directory = os.path.dirname(file_path)
            if not directory:
                directory = '.'
            dirs_with_duplicates[directory] += 1

        top_dirs = sorted(dirs_with_duplicates.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'files_analyzed': self.files_analyzed,
            'lines_analyzed': self.lines_analyzed,
            'duplicate_fragments': len(self.duplicate_fragments),
            'duplicate_functions': len(self.duplicate_functions),
            'duplicate_classes': len(self.duplicate_classes),
            'total_duplicate_lines': total_duplicate_lines,
            'files_with_duplicates': files_count,
            'top_dirs_with_duplicates': dict(top_dirs)
        }

    def create_text_report(self, statistics: Dict, recommendations: List[Dict], patterns: Dict) -> str:
        """Создает текстовый отчет на основе результатов анализа"""
        report_lines = [
            "ОТЧЕТ О ДУБЛИРОВАНИИ КОДА В ПРОЕКТЕ GOPIAI",
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "ОБЩАЯ СТАТИСТИКА:",
            f"- Проанализировано файлов: {statistics['files_analyzed']}",
            f"- Проанализировано строк кода: {statistics['lines_analyzed']}",
            f"- Найдено дублирующихся фрагментов: {statistics['duplicate_fragments']}",
            f"- Найдено дублирующихся функций: {statistics['duplicate_functions']}",
            f"- Найдено дублирующихся классов: {statistics['duplicate_classes']}",
            f"- Общее количество дублированных строк: {statistics['total_duplicate_lines']}",
            f"- Файлов с дубликатами: {statistics['files_with_duplicates']}",
            "",
            "РЕКОМЕНДАЦИИ ПО РЕФАКТОРИНГУ:",
        ]

        # Добавляем рекомендации
        for i, rec in enumerate(recommendations[:15]):  # Ограничиваем до 15 рекомендаций
            report_lines.append(f"{i+1}. [{rec['priority'].upper()}] {rec['suggestion']}")
            report_lines.append(f"   - Влияние: {rec['impact']}")
            report_lines.append(f"   - Местоположения: {', '.join(str(loc) for loc in rec['locations'][:3])}" +
                            (f" и еще {len(rec['locations']) - 3}..." if len(rec['locations']) > 3 else ""))
            report_lines.append("")

        # Добавляем информацию о шаблонах
        report_lines.append("ОБНАРУЖЕННЫЕ ШАБЛОНЫ ДУБЛИРОВАНИЯ:")

        for category, items in patterns.items():
            if items:
                category_name = {
                    'file_operations': 'Файловые операции',
                    'api_calls': 'API-вызовы',
                    'gui_elements': 'GUI-элементы',
                    'data_processing': 'Обработка данных',
                    'utility_functions': 'Утилитарные функции'
                }.get(category, category)

                report_lines.append(f"\n{category_name} ({len(items)} дубликатов):")
                for i, item in enumerate(items[:5]):  # Ограничиваем до 5 примеров на категорию
                    report_lines.append(f"- {item['type'].capitalize()}, {item['size']} строк")
                    if 'names' in item:
                        report_lines.append(f"  Имена: {', '.join(item['names'])}")

        # Добавляем информацию о директориях с наибольшим дублированием
        report_lines.append("\nДИРЕКТОРИИ С НАИБОЛЬШИМ ДУБЛИРОВАНИЕМ:")
        for dir_path, count in statistics['top_dirs_with_duplicates'].items():
            report_lines.append(f"- {dir_path}: {count} файлов с дубликатами")

        # Добавляем рекомендации по модульной структуре
        report_lines.append("\nРЕКОМЕНДАЦИИ ПО ОРГАНИЗАЦИИ КОДА:")
        report_lines.append("1. Создать модуль utils/common.py для общих утилитарных функций")
        report_lines.append("2. Вынести повторяющиеся операции работы с файлами в utils/file_operations.py")
        report_lines.append("3. Создать базовые классы в соответствующих модулях")
        report_lines.append("4. Использовать абстрактные классы и интерфейсы для стандартизации API")
        report_lines.append("5. Внедрить принцип DRY (Don't Repeat Yourself) в процесс разработки")

        return "\n".join(report_lines)

    def save_reports(self, statistics: Dict, recommendations: List[Dict], patterns: Dict) -> None:
        """Сохраняет отчеты в различных форматах"""
        # Сохраняем текстовый отчет
        text_report = self.create_text_report(statistics, recommendations, patterns)
        text_report_path = Path(REPORT_DIR) / f"duplication_report_{timestamp}.txt"
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"Текстовый отчет сохранен в {text_report_path}")

        # Сохраняем данные в JSON
        json_data = {
            'statistics': statistics,
            'recommendations': recommendations,
            'patterns': patterns,
            'duplicate_fragments': self.duplicate_fragments[:50],  # Ограничиваем количество для уменьшения размера файла
            'duplicate_functions': self.duplicate_functions,
            'duplicate_classes': self.duplicate_classes
        }

        json_report_path = Path(REPORT_DIR) / f"duplication_data_{timestamp}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        print(f"Подробные данные сохранены в {json_report_path}")

        # Создаем HTML-отчет с примерами кода
        self._create_html_report(statistics, recommendations, patterns)

    def _create_html_report(self, statistics: Dict, recommendations: List[Dict], patterns: Dict) -> None:
        """Создает HTML-отчет с примерами кода и визуализациями"""
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="ru">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>Отчет о дублировании кода - GopiAI</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }',
            '        h1, h2, h3 { color: #333; }',
            '        .stats { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }',
            '        .recommendations { margin-bottom: 30px; }',
            '        .recommendation { border-left: 4px solid #ccc; padding-left: 15px; margin-bottom: 15px; }',
            '        .recommendation.high { border-color: #dc3545; }',
            '        .recommendation.medium { border-color: #ffc107; }',
            '        .recommendation.low { border-color: #28a745; }',
            '        .code { background-color: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; white-space: pre; overflow-x: auto; }',
            '        .locations { font-size: 0.9em; color: #6c757d; }',
            '        .pattern-category { margin-top: 20px; }',
            '        .pattern-item { margin-bottom: 10px; }',
            '    </style>',
            '</head>',
            '<body>',
            '    <h1>Отчет о дублировании кода в проекте GopiAI</h1>',
            f'    <p>Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',

            '    <div class="stats">',
            '        <h2>Общая статистика</h2>',
            f'        <p>Проанализировано файлов: <strong>{statistics["files_analyzed"]}</strong></p>',
            f'        <p>Проанализировано строк кода: <strong>{statistics["lines_analyzed"]}</strong></p>',
            f'        <p>Найдено дублирующихся фрагментов: <strong>{statistics["duplicate_fragments"]}</strong></p>',
            f'        <p>Найдено дублирующихся функций: <strong>{statistics["duplicate_functions"]}</strong></p>',
            f'        <p>Найдено дублирующихся классов: <strong>{statistics["duplicate_classes"]}</strong></p>',
            f'        <p>Общее количество дублированных строк: <strong>{statistics["total_duplicate_lines"]}</strong></p>',
            f'        <p>Файлов с дубликатами: <strong>{statistics["files_with_duplicates"]}</strong></p>',
            '    </div>',

            '    <h2>Рекомендации по рефакторингу</h2>',
            '    <div class="recommendations">'
        ]

        # Добавляем рекомендации
        for rec in recommendations[:15]:
            html_parts.extend([
                f'        <div class="recommendation {rec["priority"]}">',
                f'            <h3>{rec["id"]}: {rec["suggestion"]}</h3>',
                f'            <p><strong>Приоритет:</strong> {rec["priority"]}</p>',
                f'            <p><strong>Влияние:</strong> {rec["impact"]}</p>',
                '            <p class="locations"><strong>Местоположения:</strong></p>',
                '            <ul class="locations">'
            ])

            for loc in rec['locations'][:5]:
                html_parts.append(f'                <li>{loc}</li>')

            if len(rec['locations']) > 5:
                html_parts.append(f'                <li>... и еще {len(rec["locations"]) - 5}</li>')

            html_parts.append('            </ul>')

            # Добавляем пример кода, если это дублированная функция
            if rec['type'] == 'function' and len(self.duplicate_functions) > 0:
                for func in self.duplicate_functions:
                    func_locations = [f"{loc[0]}:{loc[1]}-{loc[2]}" for loc in func['locations']]
                    if any(loc in rec['locations'] for loc in func_locations):
                        html_parts.extend([
                            '            <p><strong>Пример кода:</strong></p>',
                            f'            <div class="code">{html.escape(func["source"])}</div>',
                            '            <p><strong>Предлагаемое решение:</strong> Вынести в общий модуль utils/common.py</p>'
                        ])
                        break

            html_parts.append('        </div>')

        html_parts.append('    </div>')

        # Добавляем информацию о шаблонах
        html_parts.append('    <h2>Обнаруженные шаблоны дублирования</h2>')

        for category, items in patterns.items():
            if items:
                category_name = {
                    'file_operations': 'Файловые операции',
                    'api_calls': 'API-вызовы',
                    'gui_elements': 'GUI-элементы',
                    'data_processing': 'Обработка данных',
                    'utility_functions': 'Утилитарные функции'
                }.get(category, category)

                html_parts.extend([
                    f'    <div class="pattern-category">',
                    f'        <h3>{category_name} ({len(items)} дубликатов)</h3>',
                    '        <ul>'
                ])

                for item in items[:5]:
                    item_desc = f"{item['type'].capitalize()}, {item['size']} строк"
                    if 'names' in item:
                        item_desc += f", Имена: {', '.join(item['names'])}"

                    html_parts.append(f'            <li class="pattern-item">{item_desc}</li>')

                html_parts.extend([
                    '        </ul>',
                    '    </div>'
                ])

        # Добавляем итоговые рекомендации
        html_parts.extend([
            '    <h2>Рекомендации по организации кода</h2>',
            '    <ol>',
            '        <li>Создать модуль <strong>utils/common.py</strong> для общих утилитарных функций</li>',
            '        <li>Вынести повторяющиеся операции работы с файлами в <strong>utils/file_operations.py</strong></li>',
            '        <li>Создать базовые классы в соответствующих модулях</li>',
            '        <li>Использовать абстрактные классы и интерфейсы для стандартизации API</li>',
            '        <li>Внедрить принцип DRY (Don\'t Repeat Yourself) в процесс разработки</li>',
            '    </ol>',
            '</body>',
            '</html>'
        ])

        # Сохраняем HTML-отчет
        html_content = '\n'.join(html_parts)
        html_report_path = Path(REPORT_DIR) / f"duplication_report_{timestamp}.html"

        with open(html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML-отчет сохранен в {html_report_path}")

    def run_analysis(self) -> None:
        """Запускает полный анализ дублирования кода в проекте"""
        # Находим все Python файлы для анализа
        python_files = self.find_python_files()

        if not python_files:
            print("Не найдены Python файлы для анализа")
            return

        # Находим дублирующиеся фрагменты кода
        self.find_duplicate_fragments(python_files)

        # Находим дублирующиеся функции
        self.find_duplicate_functions(python_files)

        # Находим дублирующиеся классы
        self.find_duplicate_classes(python_files)

        # Анализируем общие шаблоны
        patterns = self.analyze_common_patterns()

        # Генерируем рекомендации по рефакторингу
        recommendations = self.generate_refactoring_recommendations()

        # Собираем статистику
        statistics = self.generate_statistics()

        # Сохраняем отчеты
        self.save_reports(statistics, recommendations, patterns)

        print(f"\nАнализ завершен!")
        print(f"Проанализировано {self.files_analyzed} файлов, {self.lines_analyzed} строк кода")
        print(f"Найдено: {len(self.duplicate_fragments)} дублирующихся фрагментов, "
              f"{len(self.duplicate_functions)} функций, "
              f"{len(self.duplicate_classes)} классов")
        print(f"Рекомендаций по рефакторингу: {len(recommendations)}")
        print(f"Отчеты сохранены в директории: {REPORT_DIR}/")


def main():
    """Основная функция скрипта"""
    print("=" * 80)
    print("АНАЛИЗАТОР ДУБЛИРОВАНИЯ КОДА В ПРОЕКТЕ GOPIAI")
    print("=" * 80)

    # Создаем экземпляр анализатора
    finder = DuplicateCodeFinder(min_lines=4, min_tokens=100)

    # Запускаем анализ
    finder.run_analysis()

    return 0


if __name__ == "__main__":
    # Для Python 3.6+ защита от случайного выполнения при импорте
    sys.exit(main())
