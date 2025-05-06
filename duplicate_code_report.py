#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Модуль для генерации отчетов о дублировании кода в проекте GopiAI.

Использует основной класс DuplicateCodeFinder из модуля find_duplicate_code.py
для анализа кодовой базы и создает удобные визуальные отчеты с возможностью
выборки по различным критериям.
"""

import argparse
import html
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Импортируем основной анализатор дублирования кода
from find_duplicate_code import REPORT_DIR, DuplicateCodeFinder

# Константы для отчетов
REPORT_FORMATS = ['html', 'json', 'txt', 'visual']
DEFAULT_OUTPUT_DIR = "duplication_reports"
COLOR_PALETTE = {
    'fragments': '#3498db',
    'functions': '#e74c3c',
    'classes': '#2ecc71',
    'background': '#f9f9f9'
}


class DuplicateCodeReport:
    """
    Класс для генерации и визуализации отчетов о дублировании кода.
    Предоставляет дополнительные возможности по сравнению с базовым анализатором,
    такие как интерактивные графики, фильтрация результатов и др.
    """

    def __init__(self,
                 project_path: Union[str, Path] = '.',
                 min_lines: int = 4,
                 min_tokens: int = 100,
                 report_formats: List[str] = None,
                 output_dir: Union[str, Path] = None,
                 exclude_dirs: Set[str] = None):
        """
        Инициализация генератора отчетов.

        Args:
            project_path: Путь к проекту
            min_lines: Минимальное количество строк для детекции дубликата
            min_tokens: Минимальная длина токенов для детекции дубликата
            report_formats: Форматы отчетов для генерации
            output_dir: Директория для сохранения отчетов
            exclude_dirs: Дополнительные директории для исключения из анализа
        """
        self.project_path = Path(project_path)
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.report_formats = report_formats or ['html', 'txt']
        self.output_dir = Path(output_dir) if output_dir else Path(DEFAULT_OUTPUT_DIR)

        # Создаем экземпляр анализатора дублирования кода
        self.finder = DuplicateCodeFinder(min_lines=min_lines, min_tokens=min_tokens)

        # Если заданы дополнительные директории для исключения, добавляем их
        if exclude_dirs:
            self.finder.EXCLUDE_DIRS.update(exclude_dirs)

        # Метаданные отчета
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_data = {}
        self.statistics = {}
        self.recommendations = []
        self.patterns = {}

    def generate_report(self) -> Dict[str, Any]:
        """
        Генерирует полный отчет о дублировании кода.

        Returns:
            Словарь с данными отчета
        """
        logger.info("Начинаем генерацию отчета о дублировании кода...")

        # Создаем директорию для отчетов, если ее нет
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Запускаем анализ дублирования кода
        logger.info("Запуск анализа дублирующегося кода...")
        python_files = self.finder.find_python_files(self.project_path)

        if not python_files:
            logger.warning("Не найдены Python файлы для анализа")
            return {}

        # Находим дублирующиеся элементы кода
        self.finder.find_duplicate_fragments(python_files)
        self.finder.find_duplicate_functions(python_files)
        self.finder.find_duplicate_classes(python_files)

        # Получаем результаты анализа
        self.patterns = self.finder.analyze_common_patterns()
        self.recommendations = self.finder.generate_refactoring_recommendations()
        self.statistics = self.finder.generate_statistics()

        # Формируем данные отчета
        self.report_data = {
            'timestamp': self.timestamp,
            'project_path': str(self.project_path),
            'statistics': self.statistics,
            'recommendations': self.recommendations,
            'patterns': self.patterns,
            'duplicate_fragments': self.finder.duplicate_fragments[:50],
            'duplicate_functions': self.finder.duplicate_functions,
            'duplicate_classes': self.finder.duplicate_classes
        }

        # Генерируем отчеты в запрошенных форматах
        for report_format in self.report_formats:
            if report_format not in REPORT_FORMATS:
                logger.warning(f"Неподдерживаемый формат отчета: {report_format}")
                continue

            if report_format == 'html':
                self._generate_html_report()
            elif report_format == 'json':
                self._generate_json_report()
            elif report_format == 'txt':
                self._generate_text_report()
            elif report_format == 'visual':
                self._generate_visual_report()

        logger.info(f"Отчеты успешно сгенерированы в директории: {self.output_dir}")
        return self.report_data

    def _generate_text_report(self) -> None:
        """Генерирует текстовый отчет"""
        report_content = self.finder.create_text_report(
            self.statistics, self.recommendations, self.patterns
        )

        report_path = self.output_dir / f"duplication_report_{self.timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"Текстовый отчет сохранен в: {report_path}")

    def _generate_json_report(self) -> None:
        """Генерирует отчет в формате JSON"""
        report_path = self.output_dir / f"duplication_data_{self.timestamp}.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, default=str)

        logger.info(f"JSON отчет сохранен в: {report_path}")

    def _generate_html_report(self) -> None:
        """Генерирует HTML отчет"""
        # Используем метод создания HTML-отчета из основного класса
        self.finder._create_html_report(
            self.statistics, self.recommendations, self.patterns
        )

        # HTML-отчет уже сохранен в директорию отчетов
        report_path = Path(REPORT_DIR) / f"duplication_report_{self.timestamp}.html"
        logger.info(f"HTML отчет сохранен в: {report_path}")

    def _generate_visual_report(self) -> None:
        """Генерирует визуальный отчет с графиками"""
        # Создаем папку для визуализаций, если она не существует
        visuals_dir = self.output_dir / "visuals"
        visuals_dir.mkdir(exist_ok=True)

        # 1. Круговая диаграмма типов дубликатов
        self._create_duplicates_pie_chart(visuals_dir)

        # 2. Гистограмма распределения размеров дублированных фрагментов
        self._create_size_histogram(visuals_dir)

        # 3. Тепловая карта директорий с дубликатами
        self._create_directories_heatmap(visuals_dir)

        logger.info(f"Визуальные отчеты сохранены в: {visuals_dir}")

    def _create_duplicates_pie_chart(self, output_dir: Path) -> None:
        """Создает круговую диаграмму распределения типов дубликатов"""
        plt.figure(figsize=(10, 7))

        # Данные для диаграммы
        labels = ['Фрагменты', 'Функции', 'Классы']
        sizes = [
            len(self.finder.duplicate_fragments),
            len(self.finder.duplicate_functions),
            len(self.finder.duplicate_classes)
        ]
        colors = [COLOR_PALETTE['fragments'], COLOR_PALETTE['functions'], COLOR_PALETTE['classes']]
        explode = (0.1, 0, 0)  # выделяем фрагменты

        # Создаем диаграмму
        plt.pie(
            sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140
        )
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Распределение дублированного кода по типам')

        # Сохраняем изображение
        output_path = output_dir / f"duplicates_distribution_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _create_size_histogram(self, output_dir: Path) -> None:
        """Создает гистограмму распределения размеров дублированных фрагментов"""
        plt.figure(figsize=(12, 8))

        # Собираем данные о размерах
        fragment_sizes = [fragment['size'] for fragment in self.finder.duplicate_fragments]
        function_sizes = [func['size'] for func in self.finder.duplicate_functions]
        class_sizes = [cls['size'] for cls in self.finder.duplicate_classes]

        # Создаем гистограмму
        plt.hist(
            [fragment_sizes, function_sizes, class_sizes],
            bins=20, alpha=0.7, label=['Фрагменты', 'Функции', 'Классы'],
            color=[COLOR_PALETTE['fragments'], COLOR_PALETTE['functions'], COLOR_PALETTE['classes']]
        )

        plt.xlabel('Количество строк кода')
        plt.ylabel('Количество дубликатов')
        plt.title('Распределение размеров дублированного кода')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Сохраняем изображение
        output_path = output_dir / f"size_distribution_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _create_directories_heatmap(self, output_dir: Path) -> None:
        """Создает тепловую карту директорий с дубликатами"""
        # Получаем статистику по директориям
        dirs_stats = self.statistics.get('top_dirs_with_duplicates', {})

        if not dirs_stats:
            logger.warning("Нет данных для создания тепловой карты директорий")
            return

        # Подготавливаем данные
        dirs = list(dirs_stats.keys())
        values = list(dirs_stats.values())

        # Создаем горизонтальную столбчатую диаграмму
        plt.figure(figsize=(12, 8))

        # Создаем красивую цветовую карту от светлого к темному оттенку
        cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#d3e0f2', '#1a5fb4'])

        bars = plt.barh(
            dirs, values, color=plt.cm.viridis(
                [x / max(values) for x in values]
            )
        )

        # Добавляем подписи значений
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{int(width)}', ha='left', va='center'
            )

        plt.xlabel('Количество файлов с дубликатами')
        plt.title('Директории с наибольшим количеством дублированного кода')
        plt.tight_layout()

        # Сохраняем изображение
        output_path = output_dir / f"directories_heatmap_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def generate_summary(self) -> str:
        """
        Генерирует краткую сводку результатов анализа.

        Returns:
            Строка с кратким отчетом
        """
        if not self.statistics:
            return "Анализ еще не был выполнен"

        summary_lines = [
            "СВОДКА ПО ДУБЛИРОВАНИЮ КОДА В ПРОЕКТЕ",
            f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Проанализировано файлов: {self.statistics['files_analyzed']}",
            f"Всего строк кода: {self.statistics['lines_analyzed']}",
            "",
            "РЕЗУЛЬТАТЫ:",
            f"- Дублирующиеся фрагменты: {self.statistics['duplicate_fragments']}",
            f"- Дублирующиеся функции: {self.statistics['duplicate_functions']}",
            f"- Дублирующиеся классы: {self.statistics['duplicate_classes']}",
            f"- Общее количество дублированных строк: {self.statistics['total_duplicate_lines']}",
            f"- Процент дублирования: {(self.statistics['total_duplicate_lines'] / self.statistics['lines_analyzed'] * 100):.2f}%",
            "",
            "ТОП-3 РЕКОМЕНДАЦИИ:"
        ]

        # Добавляем топ-3 рекомендации
        for i, rec in enumerate(self.recommendations[:3]):
            summary_lines.append(f"{i+1}. {rec['suggestion']} ({rec['priority']})")

        return "\n".join(summary_lines)


def parse_arguments():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description="Генератор отчетов о дублировании кода в проекте GopiAI"
    )

    parser.add_argument(
        "--project-path", "-p", type=str, default=".",
        help="Путь к проекту для анализа (по умолчанию: текущая директория)"
    )

    parser.add_argument(
        "--min-lines", "-l", type=int, default=4,
        help="Минимальное количество строк для детекции дубликата (по умолчанию: 4)"
    )

    parser.add_argument(
        "--min-tokens", "-t", type=int, default=100,
        help="Минимальная длина токенов для детекции дубликата (по умолчанию: 100)"
    )

    parser.add_argument(
        "--formats", "-f", type=str, nargs="+",
        choices=REPORT_FORMATS, default=["html", "txt"],
        help="Форматы отчетов для генерации (по умолчанию: html и txt)"
    )

    parser.add_argument(
        "--output-dir", "-o", type=str, default=DEFAULT_OUTPUT_DIR,
        help=f"Директория для сохранения отчетов (по умолчанию: {DEFAULT_OUTPUT_DIR})"
    )

    parser.add_argument(
        "--exclude-dirs", "-e", type=str, nargs="+", default=[],
        help="Дополнительные директории для исключения из анализа"
    )

    parser.add_argument(
        "--summary-only", "-s", action="store_true",
        help="Вывести только краткую сводку результатов анализа"
    )

    return parser.parse_args()


def main():
    """Основная функция"""
    args = parse_arguments()

    # Создаем экземпляр генератора отчетов
    report_generator = DuplicateCodeReport(
        project_path=args.project_path,
        min_lines=args.min_lines,
        min_tokens=args.min_tokens,
        report_formats=args.formats,
        output_dir=args.output_dir,
        exclude_dirs=set(args.exclude_dirs)
    )

    # Генерируем отчет
    report_generator.generate_report()

    # Выводим сводку, если запрошено
    if args.summary_only:
        print(report_generator.generate_summary())

    return 0


if __name__ == "__main__":
    sys.exit(main())
