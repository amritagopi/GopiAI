"""
Улучшенный инструмент для анализа и маркировки "мертвого" кода в проекте.

Данный модуль расширяет функциональность базового модуля mark_dead_code.py,
добавляя следующие возможности:
- Детальная интерактивная визуализация с графиками и диаграммами
- Система оценки "мертвости" кода на основе уровня доверия
- Возможность отмены внесенных изменений (undo)
- Интеграция с системой контроля версий
- Создание резервных копий файлов перед модификацией
- Оценка влияния удаления кода на систему
- Гибкие настройки через параметры командной строки
- Ведение подробного журнала всех выполненных действий
- Формирование отчётов в различных форматах
"""

import argparse
import ast
import datetime
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import threading
from collections import Counter, defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные константы
DEFAULT_CONFIDENCE = 90
BACKUP_DIR = os.path.join(os.getcwd(), 'backup_code')
REPORTS_DIR = os.path.join(os.getcwd(), 'marked_code_reports')
MARKER_PATTERN = r'# MARKED AS DEAD: (.*)'

# Глобальные переменные
_undo_stack = []
_change_history = []
_interrupted = False


class CodeEntity:
    """Представляет код, который может быть признан "мертвым"."""

    def __init__(self, file_path: str, line_start: int, line_end: int,
                 entity_type: str, name: str, source: str):
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.entity_type = entity_type  # function, class, method, variable, etc.
        self.name = name
        self.source = source
        self.confidence = 0  # уровень уверенности в "мертвости"
        self.marked = False  # был ли код помечен как "мертвый"
        self.references = []  # ссылки на другие части кода
        self.referenced_by = []  # части кода, ссылающиеся на данную
        self.impact_score = 0  # оценка влияния удаления
        self.metadata = {}  # дополнительные метаданные

    def __str__(self):
        return f"{self.entity_type} '{self.name}' ({self.file_path}:{self.line_start}-{self.line_end})"

    def to_dict(self):
        """Преобразует объект в словарь для сериализации."""
        return {
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'entity_type': self.entity_type,
            'name': self.name,
            'confidence': self.confidence,
            'marked': self.marked,
            'impact_score': self.impact_score,
            'references': self.references,
            'referenced_by': self.referenced_by,
            'metadata': self.metadata
        }


class DeadCodeAnalyzer:
    """Анализатор "мертвого" кода с расширенными возможностями."""

    def __init__(self, project_dir: str, confidence_threshold: int = DEFAULT_CONFIDENCE,
                 dry_run: bool = True, backup: bool = True, use_git: bool = True,
                 interactive: bool = False, verbose: bool = False):
        self.project_dir = os.path.abspath(project_dir)
        self.confidence_threshold = confidence_threshold
        self.dry_run = dry_run
        self.backup = backup
        self.use_git = use_git and self._is_git_available()
        self.interactive = interactive
        self.verbose = verbose

        self.entities = []  # все обнаруженные сущности кода
        self.dead_code = []  # код, признанный "мертвым"
        self.modified_files = set()  # файлы, которые были изменены
        self.analysis_graph = nx.DiGraph()  # граф зависимостей кода
        self.progress_callback = None  # колбэк для отображения прогресса

        # Создаем директории для резервных копий и отчетов, если они не существуют
        if self.backup and not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR)

    def _is_git_available(self) -> bool:
        """Проверяет, доступен ли Git в системе и является ли проект Git-репозиторием."""
        try:
            import subprocess
            result = subprocess.run(['git', 'status'],
                                  cwd=self.project_dir,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            return result.returncode == 0
        except (ImportError, FileNotFoundError):
            return False

    def analyze(self, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Выполняет анализ кода проекта на наличие "мертвого" кода.

        Args:
            progress_callback: Функция обратного вызова для отображения прогресса

        Returns:
            Dict: Результаты анализа
        """
        self.progress_callback = progress_callback
        self._log_info("Начинаем анализ проекта на наличие мертвого кода...")

        # Шаг 1: Сбор всех сущностей кода
        self._collect_code_entities()

        # Шаг 2: Построение графа зависимостей
        self._build_dependency_graph()

        # Шаг 3: Оценка "мертвости" кода
        self._evaluate_dead_code()

        # Шаг 4: Оценка влияния удаления
        self._calculate_impact_scores()

        # Шаг 5: Маркировка мертвого кода (если не dry_run)
        if not self.dry_run:
            self._mark_dead_code()

        # Формируем результаты
        results = {
            'project_dir': self.project_dir,
            'entities_count': len(self.entities),
            'dead_code_count': len(self.dead_code),
            'confidence_threshold': self.confidence_threshold,
            'dry_run': self.dry_run,
            'modified_files': list(self.modified_files),
            'dead_code': [entity.to_dict() for entity in self.dead_code],
            'timestamp': datetime.datetime.now().isoformat()
        }

        self._log_info(f"Анализ завершен. Найдено {len(self.dead_code)} единиц мертвого кода.")
        return results

    def _collect_code_entities(self):
        """Собирает все сущности кода в проекте."""
        self._log_info("Сбор всех сущностей кода в проекте...")

        python_files = self._find_python_files()
        total_files = len(python_files)

        for i, file_path in enumerate(python_files):
            if self._is_interrupted():
                break

            try:
                self._log_debug(f"Обработка файла: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()

                # Анализируем AST-дерево файла
                try:
                    tree = ast.parse(source)
                    file_entities = self._extract_entities_from_ast(file_path, tree, source)
                    self.entities.extend(file_entities)
                except SyntaxError:
                    self._log_warning(f"Невозможно проанализировать файл {file_path} - синтаксическая ошибка")

                # Обновляем прогресс
                if self.progress_callback:
                    progress = int((i + 1) / total_files * 100)
                    self.progress_callback(progress)

            except Exception as e:
                self._log_error(f"Ошибка при обработке файла {file_path}: {str(e)}")

        self._log_info(f"Собрано {len(self.entities)} сущностей кода из {total_files} файлов.")

    def _find_python_files(self) -> List[str]:
        """Находит все Python-файлы в проекте."""
        python_files = []

        for root, _, files in os.walk(self.project_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Пропускаем текущий файл анализатора
                    if os.path.basename(file_path) == os.path.basename(__file__):
                        continue
                    python_files.append(file_path)

        return python_files

    def _extract_entities_from_ast(self, file_path: str, tree: ast.AST, source: str) -> List[CodeEntity]:
        """Извлекает сущности кода из AST-дерева."""
        entities = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Функции и методы
                entity_type = "function" if not hasattr(node, 'parent') or not isinstance(node.parent, ast.ClassDef) else "method"
                entity = CodeEntity(
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    entity_type=entity_type,
                    name=node.name,
                    source=ast.get_source_segment(source, node)
                )
                entities.append(entity)

            elif isinstance(node, ast.ClassDef):
                # Классы
                entity = CodeEntity(
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    entity_type="class",
                    name=node.name,
                    source=ast.get_source_segment(source, node)
                )
                entities.append(entity)

                # Устанавливаем родителя для методов класса
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        child.parent = node

        return entities

    def _build_dependency_graph(self):
        """Строит граф зависимостей между сущностями кода."""
        self._log_info("Построение графа зависимостей кода...")

        # Создаем узлы для всех сущностей
        for entity in self.entities:
            self.analysis_graph.add_node(entity.name, entity=entity)

        # Анализируем связи между сущностями
        for entity in self.entities:
            for other in self.entities:
                if entity == other:
                    continue

                # Проверяем, ссылается ли entity на other
                if other.name in entity.source:
                    # Добавляем ребро в граф
                    self.analysis_graph.add_edge(entity.name, other.name)

                    # Обновляем списки ссылок
                    entity.references.append(other.name)
                    other.referenced_by.append(entity.name)

        self._log_info(f"Построен граф зависимостей с {self.analysis_graph.number_of_nodes()} узлами и {self.analysis_graph.number_of_edges()} рёбрами.")

    def _evaluate_dead_code(self):
        """Оценивает код на предмет "мертвости"."""
        self._log_info(f"Оценка кода на предмет 'мертвости' (порог уверенности: {self.confidence_threshold}%)...")

        # Находим точки входа в программу (файлы, которые не импортируются другими)
        entry_points = self._find_entry_points()
        self._log_debug(f"Обнаружено {len(entry_points)} точек входа в программу.")

        # Для каждой сущности оцениваем вероятность того, что она мертвая
        for entity in self.entities:
            # Базовая оценка: если на сущность нет ссылок, она может быть мертвой
            if len(entity.referenced_by) == 0:
                # Если это не точка входа
                if entity.name not in entry_points:
                    entity.confidence = 95  # Высокая вероятность
                else:
                    entity.confidence = 10  # Низкая вероятность для точек входа
            else:
                # Если есть ссылки, оцениваем их качество
                referencing_entities = [e for e in self.entities if e.name in entity.referenced_by]
                dead_references = sum(1 for e in referencing_entities if e.confidence > self.confidence_threshold)

                if len(referencing_entities) > 0:
                    # Если все ссылающиеся объекты мертвые, то и эта сущность вероятно мертвая
                    if dead_references == len(referencing_entities):
                        entity.confidence = 90
                    else:
                        # Пропорциональная оценка
                        entity.confidence = int(dead_references / len(referencing_entities) * 100)

            # Дополнительные проверки для повышения точности
            self._apply_heuristics(entity)

            # Если превышен порог уверенности, считаем код мертвым
            if entity.confidence >= self.confidence_threshold:
                self.dead_code.append(entity)

        self._log_info(f"Найдено {len(self.dead_code)} единиц мертвого кода с уверенностью >= {self.confidence_threshold}%.")

    def _find_entry_points(self) -> Set[str]:
        """Находит точки входа в программу."""
        entry_points = set()

        # Ищем файлы, содержащие конструкцию if __name__ == "__main__":
        for entity in self.entities:
            with open(entity.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content:
                    entry_points.add(os.path.basename(entity.file_path)[:-3])  # Имя файла без расширения

                    # Также добавляем функции, вызываемые из main
                    main_block = re.search(r'if\s+__name__\s*==\s*(\'|\")__main__(\'|\")\s*:(.*?)(?=\n\S|\Z)',
                                         content, re.DOTALL)
                    if main_block:
                        main_code = main_block.group(3)
                        for other_entity in self.entities:
                            if other_entity.name in main_code:
                                entry_points.add(other_entity.name)

        return entry_points

    def _apply_heuristics(self, entity: CodeEntity):
        """Применяет эвристики для уточнения оценки "мертвости"."""
        # Проверка на специальные методы в классах
        if entity.entity_type == "method" and entity.name.startswith('__') and entity.name.endswith('__'):
            entity.confidence = max(0, entity.confidence - 40)  # Уменьшаем вероятность для магических методов

        # Проверка на методы, переопределяющие родительские
        if entity.entity_type == "method" and any("super()." + entity.name in e.source for e in self.entities):
            entity.confidence = max(0, entity.confidence - 50)  # Уменьшаем вероятность для переопределенных методов

        # Проверка на тесты
        if "test" in entity.name.lower() or "/test" in entity.file_path.lower():
            entity.confidence = max(0, entity.confidence - 30)  # Уменьшаем вероятность для тестов

        # Проверка на документацию
        docstring = re.search(r'""".*?"""', entity.source, re.DOTALL)
        if docstring and len(docstring.group(0)) > 100:
            entity.confidence = max(0, entity.confidence - 10)  # Код с хорошей документацией менее вероятно мертвый

    def _calculate_impact_scores(self):
        """Рассчитывает оценки влияния удаления кода."""
        self._log_info("Расчет оценок влияния удаления кода...")

        for entity in self.dead_code:
            # Базовая оценка влияния: количество ссылок на этот код
            entity.impact_score = len(entity.referenced_by)

            # Учитываем глубину в графе зависимостей
            try:
                descendants = nx.descendants(self.analysis_graph, entity.name)
                entity.impact_score += len(descendants) * 0.5
            except (nx.NetworkXError, KeyError):
                pass

            # Учитываем размер кода
            lines_count = entity.line_end - entity.line_start + 1
            entity.impact_score += lines_count * 0.1

            # Округляем до целого
            entity.impact_score = round(entity.impact_score)

        # Сортируем мертвый код по влиянию (от наименьшего к наибольшему)
        self.dead_code.sort(key=lambda e: e.impact_score)

    def _mark_dead_code(self):
        """Маркирует мертвый код в файлах."""
        global _undo_stack, _change_history

        self._log_info("Маркировка мертвого кода в файлах...")

        if self.dry_run:
            self._log_warning("Режим dry-run: изменения не будут применены.")
            return

        # Создаем резервные копии файлов, если нужно
        if self.backup:
            self._create_backups()

        # Группируем мертвый код по файлам для оптимизации
        files_to_modify = defaultdict(list)
        for entity in self.dead_code:
            files_to_modify[entity.file_path].append(entity)

        # Обрабатываем каждый файл
        for file_path, entities in files_to_modify.items():
            if self._is_interrupted():
                break

            try:
                self._log_debug(f"Маркировка кода в файле: {file_path}")

                # Сортируем сущности по номеру строки (от большего к меньшему),
                # чтобы не сбивать нумерацию при вставке маркеров
                entities.sort(key=lambda e: e.line_start, reverse=True)

                # Читаем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Сохраняем оригинальное содержимое для возможности отмены
                original_content = ''.join(lines)
                original_file_info = {
                    'path': file_path,
                    'content': original_content
                }
                _undo_stack.append(original_file_info)

                # Маркируем каждую сущность
                for entity in entities:
                    # Вставляем маркер в начало определения
                    marker = f"# MARKED AS DEAD: {entity.entity_type} {entity.name} (confidence: {entity.confidence}%)\n"
                    lines.insert(entity.line_start - 1, marker)

                    # Обновляем нумерацию строк для оставшихся сущностей
                    for e in entities:
                        if e.line_start > entity.line_start:
                            e.line_start += 1
                            e.line_end += 1

                    # Записываем информацию об изменении
                    change_info = {
                        'file': file_path,
                        'entity': entity.to_dict(),
                        'action': 'mark',
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    _change_history.append(change_info)

                # Записываем измененное содержимое файла
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                # Отмечаем файл как измененный
                self.modified_files.add(file_path)

                # Обновляем статусы сущностей
                for entity in entities:
                    entity.marked = True

            except Exception as e:
                self._log_error(f"Ошибка при маркировке кода в файле {file_path}: {str(e)}")

        self._log_info(f"Маркировка завершена. Изменено {len(self.modified_files)} файлов.")

    def _create_backups(self):
        """Создает резервные копии файлов, которые будут изменены."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")

        # Создаем директорию для текущего бэкапа
        os.makedirs(backup_path, exist_ok=True)

        # Собираем все файлы, которые будут модифицированы
        files_to_backup = set()
        for entity in self.dead_code:
            files_to_backup.add(entity.file_path)

        # Копируем файлы
        for file_path in files_to_backup:
            try:
                rel_path = os.path.relpath(file_path, self.project_dir)
                backup_file_path = os.path.join(backup_path, rel_path)

                # Создаем директории
                os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)

                # Копируем файл
                shutil.copy2(file_path, backup_file_path)
                self._log_debug(f"Создана резервная копия файла: {rel_path}")

            except Exception as e:
                self._log_error(f"Ошибка при создании резервной копии файла {file_path}: {str(e)}")

        self._log_info(f"Созданы резервные копии {len(files_to_backup)} файлов в {backup_path}")

    def generate_reports(self, results: Dict):
        """Генерирует отчеты о результатах анализа."""
        self._log_info("Генерация отчетов...")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Текстовый отчет
        text_report_path = os.path.join(REPORTS_DIR, f"mark_dead_code_report_{timestamp}.txt")
        self._generate_text_report(results, text_report_path)

        # JSON-отчет
        json_report_path = os.path.join(REPORTS_DIR, f"mark_dead_code_data_{timestamp}.json")
        self._generate_json_report(results, json_report_path)

        # HTML-отчет с визуализацией
        html_report_path = os.path.join(REPORTS_DIR, f"mark_dead_code_report_{timestamp}.html")
        self._generate_html_report(results, html_report_path)

        # Отчет о внесенных изменениях
        if not self.dry_run and len(self.modified_files) > 0:
            changes_report_path = os.path.join(REPORTS_DIR, f"changes_summary_{timestamp}.txt")
            self._generate_changes_report(changes_report_path)

        # Создаем визуализации
        self._generate_visualizations(timestamp)

        self._log_info(f"Отчеты сгенерированы и сохранены в директории {REPORTS_DIR}")

        return {
            'text_report': text_report_path,
            'json_report': json_report_path,
            'html_report': html_report_path,
            'timestamp': timestamp
        }

    def _generate_text_report(self, results: Dict, output_path: str):
        """Генерирует текстовый отчет."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== Отчет об анализе мертвого кода ===\n\n")
            f.write(f"Дата анализа: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Директория проекта: {results['project_dir']}\n")
            f.write(f"Всего сущностей кода: {results['entities_count']}\n")
            f.write(f"Обнаружено единиц мертвого кода: {results['dead_code_count']}\n")
            f.write(f"Порог уверенности: {results['confidence_threshold']}%\n")
            f.write(f"Режим dry-run: {'Да' if results['dry_run'] else 'Нет'}\n\n")

            if results['dead_code_count'] > 0:
                f.write("--- Обнаруженный мертвый код ---\n\n")

                # Группируем по файлам для удобства чтения
                files_map = defaultdict(list)
                for entity in results['dead_code']:
                    files_map[entity['file_path']].append(entity)

                for file_path, entities in files_map.items():
                    f.write(f"Файл: {file_path}\n")

                    # Сортируем по номеру строки
                    entities.sort(key=lambda e: e.get('line_start', 0))

                    for entity in entities:
                        f.write(f"  {entity['entity_type']} '{entity['name']}' (строки {entity['line_start']}-{entity['line_end']})\n")
                        f.write(f"    Уверенность: {entity['confidence']}%\n")
                        f.write(f"    Влияние удаления: {entity.get('impact_score', 0)}\n")

                        # Если есть ссылки или ссылающиеся объекты, показываем их
                        if entity.get('references', []):
                            f.write(f"    Ссылается на: {', '.join(entity['references'])}\n")

                        if entity.get('referenced_by', []):
                            f.write(f"    На него ссылаются: {', '.join(entity['referenced_by'])}\n")

                        f.write("\n")

                    f.write("\n")
            else:
                f.write("Мертвый код не обнаружен.\n")

    def _generate_json_report(self, results: Dict, output_path: str):
        """Генерирует JSON-отчет."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def _generate_html_report(self, results: Dict, output_path: str):
        """Генерирует HTML-отчет с визуализацией."""
        # Шаблон HTML-отчета
        html_template = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет об анализе мертвого кода</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #333;
        }
        .summary {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .file-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        }
        .entity {
            background-color: #f9f9f9;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #ccc;
        }
        .function {
            border-left-color: #4caf50;
        }
        .class {
            border-left-color: #2196f3;
        }
        .method {
            border-left-color: #ff9800;
        }
        .code {
            font-family: monospace;
            white-space: pre;
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 3px;
            font-size: 12px;
            overflow-x: auto;
        }
        .confidence-high {
            color: #d32f2f;
            font-weight: bold;
        }
        .confidence-medium {
            color: #f57c00;
            font-weight: bold;
        }
        .confidence-low {
            color: #388e3c;
            font-weight: normal;
        }
        .impact {
            font-style: italic;
            color: #555;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 15px;
            cursor: pointer;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
            margin-right: 5px;
            border-radius: 5px 5px 0 0;
        }
        .tab.active {
            background-color: #fff;
            border-bottom: 1px solid #fff;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
    <script>
        function switchTab(tabId) {
            // Скрыть все вкладки
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(tab => tab.classList.remove('active'));

            // Деактивировать все заголовки вкладок
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));

            // Активировать выбранную вкладку
            document.getElementById(tabId).classList.add('active');
            document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
        }

        function toggleEntityDetails(id) {
            const details = document.getElementById(id);
            if (details.style.display === 'none') {
                details.style.display = 'block';
            } else {
                details.style.display = 'none';
            }
        }
    </script>
</head>
<body>
    <h1>Отчет об анализе мертвого кода</h1>
    <p>Дата анализа: {timestamp}</p>

    <div class="summary">
        <h2>Сводная информация</h2>
        <p>Директория проекта: <strong>{project_dir}</strong></p>
        <p>Всего проанализировано сущностей кода: <strong>{entities_count}</strong></p>
        <p>Обнаружено единиц мертвого кода: <strong>{dead_code_count}</strong></p>
        <p>Порог уверенности: <strong>{confidence_threshold}%</strong></p>
        <p>Режим dry-run: <strong>{dry_run}</strong></p>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('tab-overview')">Обзор</div>
        <div class="tab" onclick="switchTab('tab-files')">По файлам</div>
        <div class="tab" onclick="switchTab('tab-types')">По типам</div>
        <div class="tab" onclick="switchTab('tab-confidence')">По уверенности</div>
    </div>

    <div id="tab-overview" class="tab-content active">
        <h2>Обзор обнаруженного мертвого кода</h2>

        <div class="chart-container">
            <img src="{charts_dir}/distribution_by_type.png" alt="Распределение по типам" />
        </div>

        <div class="chart-container">
            <img src="{charts_dir}/distribution_by_confidence.png" alt="Распределение по уровню уверенности" />
        </div>

        <h3>Топ-10 единиц мертвого кода по влиянию:</h3>
        <ul>
            {top_impact_items}
        </ul>
    </div>

    <div id="tab-files" class="tab-content">
        <h2>Мертвый код по файлам</h2>
        {files_content}
    </div>

    <div id="tab-types" class="tab-content">
        <h2>Мертвый код по типам</h2>

        <h3>Функции</h3>
        {functions_content}

        <h3>Методы</h3>
        {methods_content}

        <h3>Классы</h3>
        {classes_content}
    </div>

    <div id="tab-confidence" class="tab-content">
        <h2>Мертвый код по уровню уверенности</h2>

        <h3>Высокая уверенность (90-100%)</h3>
        {high_confidence_content}

        <h3>Средняя уверенность ({confidence_threshold}-89%)</h3>
        {medium_confidence_content}
    </div>

    <script>
        // Инициализация активной вкладки
        switchTab('tab-overview');
    </script>
</body>
</html>'''

        # Форматируем HTML-шаблон с данными
        formatted_html = self._format_html_report_template(html_template, results)

        # Записываем HTML-отчет
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_html)

        self._log_info(f"HTML-отчет сохранен в: {output_path}")
