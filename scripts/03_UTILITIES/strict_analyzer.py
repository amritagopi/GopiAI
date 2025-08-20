#!/usr/bin/env python
"""
Strict Project Analyzer - Строго ограниченный анализатор проекта GOPI_AI_MODULES
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

# Добавляем текущую директорию в путь для импорта локальных модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые модули
from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from project_cleanup_orchestrator import setup_logging
from structure_analyzer import StructureAnalyzer
from code_quality_analyzer import CodeQualityAnalyzer
from dead_code_analyzer import DeadCodeAnalyzer
from file_analyzer import FileAnalyzer
from dependency_analyzer import DependencyAnalyzer
from documentation_analyzer import DocumentationAnalyzer
from report_generator import ReportGenerator, CleanupReport

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('strict_analyzer.log')
    ]
)

logger = logging.getLogger(__name__)

class StrictAnalyzer:
    """Анализатор с строгим ограничением по директории"""
    
    def __init__(self, analyzer_class, config, project_dir):
        """
        Инициализация анализатора
        
        Args:
            analyzer_class: Класс анализатора
            config: Конфигурация анализа
            project_dir: Директория проекта (для строгой проверки)
        """
        self.analyzer_class = analyzer_class
        self.config = config
        self.project_dir = os.path.abspath(project_dir)
        self.analyzer = analyzer_class(config)
        self.name = analyzer_class.__name__
        
    def analyze(self):
        """
        Запуск анализа с строгой проверкой путей
        
        Returns:
            Список результатов анализа
        """
        try:
            # Переопределяем метод get_project_files для строгой проверки путей
            original_get_project_files = self.analyzer.get_project_files
            
            def strict_get_project_files(project_path, file_extensions=None):
                files = original_get_project_files(project_path, file_extensions)
                # Фильтруем файлы, оставляя только те, которые находятся в директории проекта
                return [f for f in files if str(f).startswith(self.project_dir)]
            
            # Заменяем метод
            self.analyzer.get_project_files = strict_get_project_files
            
            # Запускаем анализ
            results = self.analyzer.analyze(self.project_dir)
            
            # Фильтруем результаты, оставляя только те, которые относятся к директории проекта
            filtered_results = []
            for result in results:
                if hasattr(result, 'file_path') and result.file_path:
                    if str(result.file_path).startswith(self.project_dir):
                        filtered_results.append(result)
                else:
                    filtered_results.append(result)
            
            return filtered_results
        except Exception as e:
            logger.error(f"Ошибка в анализаторе {self.name}: {e}")
            return []

def run_analyzer_with_timeout(analyzer, timeout=300):
    """
    Запускает анализатор с таймаутом
    
    Args:
        analyzer: Экземпляр StrictAnalyzer
        timeout: Таймаут в секундах
        
    Returns:
        Tuple (имя анализатора, результаты анализа)
    """
    try:
        # Запускаем анализ с таймаутом
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(analyzer.analyze)
            results = future.result(timeout=timeout)
            
        return analyzer.name, results
    except TimeoutError:
        logger.warning(f"Анализатор {analyzer.name} превысил таймаут {timeout} секунд")
        return analyzer.name, []
    except Exception as e:
        logger.error(f"Ошибка в анализаторе {analyzer.name}: {e}")
        return analyzer.name, []

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Строго ограниченный анализатор проекта GOPI_AI_MODULES')
    
    parser.add_argument(
        '--skip-duplicate',
        action='store_true',
        help='Пропустить анализ дублирующегося кода (самый медленный)'
    )
    
    parser.add_argument(
        '--skip-conflict',
        action='store_true',
        help='Пропустить анализ конфликтов'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        default=100,
        help='Максимальное количество файлов для анализа (по умолчанию: 100)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Таймаут для каждого анализатора в секундах (по умолчанию: 300)'
    )
    
    parser.add_argument(
        '--format',
        choices=['markdown', 'html', 'json'],
        default='markdown',
        help='Формат отчета (по умолчанию: markdown)'
    )
    
    return parser.parse_args()

def main():
    """
    Основная функция для запуска строго ограниченного анализа проекта
    """
    args = parse_arguments()
    
    print("Запуск строго ограниченного анализа проекта GOPI_AI_MODULES...")
    
    # Определяем путь к проекту (текущая директория)
    project_path = os.path.abspath('..')
    
    # Проверяем, что мы находимся в директории GOPI_AI_MODULES
    current_dir = os.path.basename(os.path.abspath('.'))
    parent_dir = os.path.basename(project_path)
    
    if current_dir == '03_UTILITIES' and parent_dir == 'GOPI_AI_MODULES':
        print(f"Анализируем проект: {project_path}")
    else:
        print(f"ВНИМАНИЕ: Текущая директория не похожа на 03_UTILITIES в проекте GOPI_AI_MODULES")
        print(f"Текущая директория: {os.path.abspath('.')}")
        print(f"Родительская директория: {project_path}")
        
        # Спрашиваем пользователя, хочет ли он продолжить
        response = input("Продолжить анализ? (y/n): ")
        if response.lower() != 'y':
            print("Анализ отменен.")
            return
    
    # Создаем конфигурацию для анализа
    config = AnalysisConfig(
        project_path=project_path,
        enable_caching=False,  # Отключаем кэширование для ускорения
        incremental_analysis=False,  # Отключаем инкрементальный анализ
        analysis_depth="quick",  # Быстрый анализ
        max_files_per_analyzer=args.max_files,  # Ограничиваем количество файлов
        output_format=args.format,  # Формат отчета
        # Исключаем виртуальные окружения и другие ненужные директории
        exclude_patterns=[
            '*.pyc', '__pycache__', '.git', '.vscode', 'node_modules',
            '*.egg-info', '.pytest_cache', '.tox', 'venv', '*_env',
            '*/site-packages/*', '*/Lib/site-packages/*', '*/lib/python*/site-packages/*',
            # Дополнительные исключения для ускорения анализа
            '*.dll', '*.exe', '*.pyd', '*.so', '*.dylib',
            '*.zip', '*.tar', '*.gz', '*.bz2', '*.xz', '*.7z',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico',
            '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wav',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
            # Исключаем директории браузеров, которые могут вызывать проблемы
            '*/BraveSoftware/*', '*/Google/Chrome/*', '*/Microsoft/Edge/*',
            '*/Mozilla/Firefox/*', '*/Opera/*', '*/Safari/*',
            # Исключаем виртуальные окружения проекта
            'gopiai_env/*', 'txtai_env/*', 'crewai_env/*',
            'GopiAI-CrewAI/crewai_env/*'
        ]
    )
    
    # Создаем директорию для отчетов, если она не существует
    reports_dir = os.path.join(project_path, 'project_health', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Генерируем имя файла отчета
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(reports_dir, f"strict_analysis_{timestamp}.{args.format}")
    
    # Определяем список анализаторов
    analyzer_classes = [
        StructureAnalyzer,
        CodeQualityAnalyzer,
        DeadCodeAnalyzer,
        FileAnalyzer,
        DependencyAnalyzer,
        DocumentationAnalyzer
    ]
    
    # Пропускаем анализаторы по запросу пользователя
    if not args.skip_conflict:
        from conflict_analyzer import ConflictAnalyzer
        analyzer_classes.append(ConflictAnalyzer)
    
    if not args.skip_duplicate:
        from duplicate_analyzer import DuplicateAnalyzer
        analyzer_classes.append(DuplicateAnalyzer)
    
    # Создаем строгие анализаторы
    analyzers = [StrictAnalyzer(cls, config, project_path) for cls in analyzer_classes]
    
    # Запускаем анализ
    start_time = time.time()
    print("Анализ начат. Это может занять некоторое время...")
    
    all_results = []
    all_errors = {}
    
    # Запускаем анализаторы последовательно для лучшего контроля
    for i, analyzer in enumerate(analyzers, 1):
        print(f"Запуск анализатора {analyzer.name} ({i}/{len(analyzers)})...")
        analyzer_name, results = run_analyzer_with_timeout(analyzer, args.timeout)
        print(f"Завершен анализатор {analyzer_name} - Найдено {len(results)} проблем - Прогресс: {i}/{len(analyzers)}")
        all_results.extend(results)
    
    # Создаем отчет
    report_generator = ReportGenerator(config)
    report = CleanupReport(
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
        project_path=project_path,
        summary={},  # Будет заполнено в generate_report
        results_by_category={},  # Будет заполнено в generate_report
        recommendations=[],  # Будет заполнено в generate_report
        priority_actions=[]  # Будет заполнено в generate_report
    )
    
    # Генерируем отчет
    report = report_generator.generate_report(all_results, all_errors)
    
    # Сохраняем отчет
    report_path = report_generator.save_report(report, output_path)
    
    # Выводим результаты
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"Анализ проекта завершен за {elapsed:.2f} секунд")
    print(f"Отчет сохранен в: {report_path}")
    print("=" * 80)
    
    # Открываем отчет в браузере или текстовом редакторе
    try:
        import webbrowser
        webbrowser.open(report_path)
        print("Отчет открыт в браузере.")
    except:
        print(f"Пожалуйста, откройте отчет вручную: {report_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())