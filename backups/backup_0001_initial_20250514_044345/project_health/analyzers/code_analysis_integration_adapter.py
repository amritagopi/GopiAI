
"""
Адаптер для интеграции функций анализа кода в интерфейс IDE.

Этот модуль содержит адаптеры для подключения реализованных функций анализа кода
к интерфейсу IDE. Он обеспечивает совместимость между интерфейсом UI и
реализованными функциями анализа.
"""

import logging
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Импортируем модули анализа
import analyze_dependencies
import duplicate_code_report
import find_unused_files
import improve_mark_dead_code

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DependenciesAnalyzer:
    """Адаптер для модуля анализа зависимостей."""

    @staticmethod
    def analyze_project(project_dir: str,
                       progress_callback: Optional[Callable] = None) -> Dict:
        """
        Анализирует зависимости проекта.

        Args:
            project_dir: Директория проекта
            progress_callback: Функция обратного вызова для отображения прогресса

        Returns:
            Dict: Граф импортов
        """
        logger.info(f"Запуск анализа зависимостей для директории: {project_dir}")

        # Вызываем функцию анализа зависимостей
        try:
            imports_graph = analyze_dependencies.analyze_dependencies(
                project_dir
            )

            # Вызов колбэка для сообщения о прогрессе
            if progress_callback:
                progress_callback(100)

            # Сохраняем результаты
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(os.getcwd(), 'imports_reports')
            os.makedirs(output_dir, exist_ok=True)

            # Сохраняем результаты в файл
            output_file = os.path.join(output_dir, f"imports_graph_{timestamp}.json")

            # Преобразуем пути к относительным для удобства просмотра
            relative_imports_graph = {}
            for file_path, imports in imports_graph.items():
                rel_path = os.path.relpath(file_path, project_dir)
                relative_imports_graph[rel_path] = imports

            # Сохраняем в JSON
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(relative_imports_graph, f, indent=4, ensure_ascii=False)

            return {
                'imports_graph': imports_graph,
                'output_file': output_file
            }
        except Exception as e:
            logger.exception(f"Ошибка при анализе зависимостей: {e}")
            raise

class UnusedCodeAnalyzer:
    """Адаптер для модуля поиска неиспользуемого кода."""

    @staticmethod
    def find_unused_files(project_dir: str,
                         progress_callback: Optional[Callable] = None) -> Dict:
        """
        Находит неиспользуемые файлы в проекте.

        Args:
            project_dir: Директория проекта
            progress_callback: Функция обратного вызова для отображения прогресса

        Returns:
            Dict: Результаты анализа
        """
        logger.info(f"Запуск анализа неиспользуемого кода для директории: {project_dir}")

        # Вызываем функцию поиска неиспользуемых файлов
        try:
            # Создаем директорию для отчетов, если её нет
            output_dir = os.path.join(os.getcwd(), 'imports_reports')
            os.makedirs(output_dir, exist_ok=True)

            # Анализируем проект
            imports_graph, unused_files = find_unused_files.find_unused_files(
                project_dir,
                progress_callback
            )

            # Сохраняем результаты
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"unused_files_summary_{timestamp}.txt")

            find_unused_files.save_unused_files_report(unused_files, output_file)

            return {
                'imports_graph': imports_graph,
                'unused_files': unused_files,
                'output_file': output_file
            }
        except Exception as e:
            logger.exception(f"Ошибка при анализе неиспользуемого кода: {e}")
            raise

class DuplicationAnalyzer:
    """Адаптер для модуля анализа дублирования кода."""

    @staticmethod
    def analyze_duplication(project_dir: str,
                           min_lines: int = 5,
                           include_comments: bool = False,
                           progress_callback: Optional[Callable] = None) -> Dict:
        """
        Анализирует дублирование кода в проекте.

        Args:
            project_dir: Директория проекта
            min_lines: Минимальное количество строк для обнаружения дубликатов
            include_comments: Включать ли комментарии в анализ
            progress_callback: Функция обратного вызова для отображения прогресса

        Returns:
            Dict: Результаты анализа
        """
        logger.info(f"Запуск анализа дублирования кода для директории: {project_dir}")

        # Вызываем функцию анализа дублирования
        try:
            # Создаем директорию для отчетов, если её нет
            output_dir = os.path.join(os.getcwd(), 'duplication_reports')
            os.makedirs(output_dir, exist_ok=True)

            # Анализируем проект
            results = duplicate_code_report.analyze_duplication(
                project_dir,
                min_lines=min_lines,
                include_comments=include_comments,
                progress_callback=progress_callback
            )

            # Сохраняем результаты
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_output_file = os.path.join(output_dir, f"duplication_report_{timestamp}")

            text_report = f"{base_output_file}.txt"
            html_report = f"{base_output_file}.html"
            json_report = f"{base_output_file}.json"

            duplicate_code_report.generate_text_report(results, text_report)
            duplicate_code_report.generate_html_report(results, html_report)
            duplicate_code_report.generate_json_report(results, json_report)

            return {
                'results': results,
                'output_files': [text_report, html_report, json_report]
            }
        except Exception as e:
            logger.exception(f"Ошибка при анализе дублирования кода: {e}")
            raise

class DeadCodeAnalyzer:
    """Адаптер для модуля маркировки мертвого кода."""

    @staticmethod
    def analyze_dead_code(project_dir: str,
                         confidence: int = 90,
                         dry_run: bool = True,
                         progress_callback: Optional[Callable] = None) -> Dict:
        """
        Анализирует и маркирует мертвый код в проекте.

        Args:
            project_dir: Директория проекта
            confidence: Уровень уверенности для маркировки (%)
            dry_run: Только анализ без внесения изменений
            progress_callback: Функция обратного вызова для отображения прогресса

        Returns:
            Dict: Результаты анализа
        """
        logger.info(f"Запуск анализа мертвого кода для директории: {project_dir}")

        # Вызываем функцию анализа мертвого кода
        try:
            # Создаем директорию для отчетов, если её нет
            output_dir = os.path.join(os.getcwd(), 'marked_code_reports')
            os.makedirs(output_dir, exist_ok=True)

            # Создаем анализатор мертвого кода
            analyzer = improve_mark_dead_code.DeadCodeAnalyzer(
                project_dir=project_dir,
                confidence_threshold=confidence,
                dry_run=dry_run,
                backup=True,
                interactive=False,
                verbose=True
            )

            # Выполняем анализ
            if progress_callback:
                results = analyzer.analyze(progress_callback)
            else:
                results = analyzer.analyze()

            # Генерируем отчеты
            reports = analyzer.generate_reports(results)

            return {
                'results': results,
                'reports': reports,
                'output_file': reports.get('text_report')
            }
        except Exception as e:
            logger.exception(f"Ошибка при анализе мертвого кода: {e}")
            raise

# Экспортируем функции для использования в интерфейсе
analyze_dependencies_project = DependenciesAnalyzer.analyze_project
find_unused_files_in_project = UnusedCodeAnalyzer.find_unused_files
analyze_code_duplication = DuplicationAnalyzer.analyze_duplication
analyze_and_mark_dead_code = DeadCodeAnalyzer.analyze_dead_code
