#!/usr/bin/env python
"""
Project Analyzer - Анализирует только директорию проекта GOPI_AI_MODULES
"""

import os
import sys
import time
import logging
from pathlib import Path

# Добавляем текущую директорию в путь для импорта локальных модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые модули
from project_analyzer.core.project_cleanup_analyzer import AnalysisConfig
from project_analyzer.core.project_cleanup_orchestrator import ProjectCleanupAnalyzer, setup_logging

def main():
    """
    Основная функция для запуска анализа проекта
    """
    print("Запуск анализа проекта GOPI_AI_MODULES...")
    
    # Настраиваем логирование
    setup_logging("INFO")
    
    # Определяем путь к проекту (родительская директория)
    current_dir = os.path.basename(os.path.abspath('.'))
    project_path = os.path.abspath('..')
    
    # Проверяем, что мы находимся в директории GOPI_AI_MODULES
    parent_dir = os.path.basename(project_path)
    
    if current_dir == '03_UTILITIES' and parent_dir == 'GOPI_AI_MODULES':
        print(f"Анализируем проект: {project_path}")
    else:
        print("ВНИМАНИЕ: Текущая директория не похожа на 03_UTILITIES в проекте GOPI_AI_MODULES")
        print(f"Текущая директория: {os.path.abspath('.')}")
        print(f"Родительская директория: {project_path}")
        print("ОШИБКА: Неправильная директория для запуска. Запускайте из 03_UTILITIES в проекте GOPI_AI_MODULES.")
        return 1
    
    # Создаем конфигурацию для анализа
    config = AnalysisConfig(
        project_path=project_path,
        enable_caching=True,
        incremental_analysis=True,
        analysis_depth="standard",  # Стандартный анализ для полного охвата
        max_files_per_analyzer=0,  # Убираем ограничение на количество файлов
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
    output_path = os.path.join(reports_dir, f"project_analysis_{timestamp}.md")
    
    # Создаем анализатор
    analyzer = ProjectCleanupAnalyzer(config=config)
    
    # Запускаем анализ
    start_time = time.time()
    print("Анализ начат. Это может занять некоторое время...")
    
    try:
        # Запускаем анализ (последовательно для стабильности)
        report_path = analyzer.run_full_analysis(parallel=False, output_path=output_path)
        
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
    
    except Exception as e:
        print(f"Ошибка при анализе проекта: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
