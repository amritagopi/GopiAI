#!/usr/bin/env python
"""
Quick Project Analyzer - Быстрый анализ проекта GOPI_AI_MODULES
с возможностью пропуска тяжелых анализаторов
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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Импортируем необходимые модули
from project_analyzer.core.project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from project_analyzer.core.project_cleanup_orchestrator import setup_logging
from project_analyzer.core.structure_analyzer import StructureAnalyzer
from project_analyzer.core.code_quality_analyzer import CodeQualityAnalyzer
from project_analyzer.core.dead_code_analyzer import DeadCodeAnalyzer
from project_analyzer.core.file_analyzer import FileAnalyzer
from project_analyzer.core.dependency_analyzer import DependencyAnalyzer
from project_analyzer.core.documentation_analyzer import DocumentationAnalyzer
from project_analyzer.core.report_generator import ReportGenerator, CleanupReport

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('quick_analyze.log')
    ]
)

logger = logging.getLogger(__name__)

def run_analyzer(analyzer_class, config, timeout=300):
    """
    Запускает анализатор с таймаутом
    
    Args:
        analyzer_class: Класс анализатора
        config: Конфигурация анализа
        timeout: Таймаут в секундах
        
    Returns:
        Tuple (имя анализатора, результаты анализа)
    """
    analyzer_name = analyzer_class.__name__
    
    try:
        # Создаем анализатор
        analyzer = analyzer_class(config)
        
        # Запускаем анализ с таймаутом
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(analyzer.analyze, config.project_path)
            results = future.result(timeout=timeout)
            
        return analyzer_name, results
    except TimeoutError:
        logger.warning(f"Анализатор {analyzer_name} превысил таймаут {timeout} секунд")
        return analyzer_name, []
    except Exception as e:
        logger.error(f"Ошибка в анализаторе {analyzer_name}: {e}")
        return analyzer_name, []

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Быстрый анализ проекта GOPI_AI_MODULES')
    
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
    Основная функция для запуска быстрого анализа проекта
    """
    args = parse_arguments()
    
    print("Запуск быстрого анализа проекта GOPI_AI_MODULES...")
    
    # Определяем путь к проекту (текущая директория)
    project_path = os.path.abspath('..')
    
    # Проверяем, что мы находимся в директории GOPI_AI_MODULES
    current_dir = os.path.basename(os.path.abspath('.'))
    parent_dir = os.path.basename(project_path)
    
    if current_dir == '03_UTILITIES' and parent_dir == 'GOPI_AI_MODULES':
        print(f"Анализируем проект: {project_path}")
    else:
        print("ВНИМАНИЕ: Текущая директория не похожа на 03_UTILITIES в проекте GOPI_AI_MODULES")
        print(f"Текущая директория: {os.path.abspath('.')}")
        print(f"Родительская директория: {project_path}")
        print("Continuing analysis despite directory mismatch.")
    
    # Создаем конфигурацию для анализа
    config = AnalysisConfig(
        project_path=project_path,
        enable_caching=False,  # Отключаем кэширование для ускорения
        incremental_analysis=False,  # Отключаем инкрементальный анализ
        analysis_depth="quick",  # Быстрый анализ
        max_files_per_analyzer=0,  # Убираем ограничение на количество файлов
        output_format=args.format,  # Формат отчета
        # Исключаем виртуальные окружения и другие ненужные директории
        exclude_patterns=[
            '*.pyc', '__pycache__', '.git', '.vscode', 'node_modules',
            '*.egg-info', '.pytest_cache', '.tox', 'venv', '*_env',
            '*/gopiai_env/*', '*/mcp_env/*', '*/txtai_env/*', '*/crewai_env/*',
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
            # Исключаем специфичные директории с проблемными файлами
            '*/test_project_generator.py',  # Файл с множественными синтаксическими ошибками
            '*/scripts_fix_bridge_issue_corrected.py',  # Проблемный файл
            '*/agent_controller.py',  # Файл с проблемами (временно)
            # Исключаем директории с тестовыми проектами
            '*/test_projects/*',
            '*/test_project/*',
            '*/edge_case_project/*',
            # Исключаем большие файлы и директории
            '*_large.py',
            '*_huge.py',
            '*/large_file.py',
            # Исключаем файлы с известными проблемами
            '*syntax_error*',
            '*invalid_*',
            # Исключаем проблемные директории
            '*/potential_conflicts/*',
            # Дополнительные исключения для ускорения анализа дубликатов
            '*/GopiAI-CrewAI/*',
            '*/logs/*',
            '*/conversations/*',
            '*/examples/*'
        ]
    )
    
    # Создаем директорию для отчетов, если она не существует
    reports_dir = os.path.join(project_path, 'project_health', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Генерируем имя файла отчета
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(reports_dir, f"quick_analysis_{timestamp}.{args.format}")
    
    # Определяем список анализаторов
    analyzers = [
        StructureAnalyzer,
        CodeQualityAnalyzer,
        DeadCodeAnalyzer,
        FileAnalyzer,
        DependencyAnalyzer,
        DocumentationAnalyzer
    ]
    
    # Пропускаем анализаторы по запросу пользователя
    if not args.skip_conflict:
        from project_analyzer.core.conflict_analyzer import ConflictAnalyzer
        analyzers.append(ConflictAnalyzer)
    
    if not args.skip_duplicate:
        from project_analyzer.core.duplicate_analyzer import DuplicateAnalyzer
        analyzers.append(DuplicateAnalyzer)
    
    # Запускаем анализ
    start_time = time.time()
    print("Анализ начат. Это может занять некоторое время...")
    
    all_results = []
    all_errors = {}
    
    # Запускаем анализаторы параллельно
    with multiprocessing.Pool(processes=min(multiprocessing.cpu_count() - 1, 4)) as pool:
        # Создаем задачи для каждого анализатора
        tasks = [(analyzer_class, config, args.timeout) for analyzer_class in analyzers]
        
        # Запускаем задачи
        for i, (analyzer_name, results) in enumerate(pool.starmap(run_analyzer, tasks), 1):
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
    report = report_generator.generate_report(all_results, analyzer_errors=all_errors)
    
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
