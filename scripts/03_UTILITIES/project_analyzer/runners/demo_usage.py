#!/usr/bin/env python
"""
Демонстрация использования Project Analyzer

Этот скрипт показывает основные способы использования анализаторов проекта.
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    AnalysisConfig,
    ProjectCleanupAnalyzer,
    StructureAnalyzer,
    CodeQualityAnalyzer,
    setup_logging
)


def demo_basic_usage():
    """Демонстрация базового использования анализатора."""
    print("=== Демонстрация базового использования ===")
    
    # Настраиваем логирование
    setup_logging("INFO")
    
    # Определяем путь к проекту
    project_path = os.path.abspath("../../..")
    print(f"Анализируем проект: {project_path}")
    
    # Создаем конфигурацию
    config = AnalysisConfig(
        project_path=project_path,
        analysis_depth="quick",
        max_files_per_analyzer=0,  # Убираем ограничение на количество файлов
        exclude_patterns=[
            "*.pyc", "__pycache__", ".git", "*_env",
            "*/site-packages/*",
            "*/gopiai_env/*", "*/mcp_env/*", "*/txtai_env/*", "*/crewai_env/*"
        ]
    )
    
    # Создаем и запускаем анализатор структуры
    print("\\nЗапуск анализатора структуры...")
    structure_analyzer = StructureAnalyzer(config)
    structure_results = structure_analyzer.analyze(project_path)
    
    print(f"Найдено проблем со структурой: {len(structure_results)}")
    for result in structure_results[:3]:  # Показываем первые 3
        print(f"  - {result.category}: {result.description}")
    
    # Создаем и запускаем анализатор качества кода
    print("\\nЗапуск анализатора качества кода...")
    quality_analyzer = CodeQualityAnalyzer(config)
    quality_results = quality_analyzer.analyze(project_path)
    
    print(f"Найдено проблем с качеством кода: {len(quality_results)}")
    for result in quality_results[:3]:  # Показываем первые 3
        print(f"  - {result.severity}: {result.description}")


def demo_full_analysis():
    """Демонстрация полного анализа проекта."""
    print("\\n=== Демонстрация полного анализа ===")
    
    project_path = os.path.abspath("../../..")
    
    # Конфигурация для быстрого анализа
    config = AnalysisConfig(
        project_path=project_path,
        analysis_depth="quick",
        max_files_per_analyzer=0,  # Убираем ограничение на количество файлов
        enable_caching=False,
        output_format="markdown"
    )
    
    # Создаем полный анализатор
    analyzer = ProjectCleanupAnalyzer(config)
    
    print("Запуск полного анализа (быстрый режим)...")
    try:
        # Запускаем анализ
        report_path = analyzer.run_full_analysis(
            parallel=True,
            output_path=None  # Автоматическое имя файла
        )
        
        print(f"Анализ завершен. Отчет сохранен: {report_path}")
        
    except Exception as e:
        print(f"Ошибка при анализе: {e}")


def demo_custom_config():
    """Демонстрация настройки конфигурации."""
    print("\\n=== Демонстрация настройки конфигурации ===")
    
    # Различные конфигурации для разных целей
    configs = {
        "Быстрый анализ": AnalysisConfig(
            project_path="../../..",
            analysis_depth="quick",
            max_files_per_analyzer=0,  # Убираем ограничение
            exclude_patterns=["*.pyc", "__pycache__", "*_env", "*/gopiai_env/*", "*/mcp_env/*", "*/txtai_env/*", "*/crewai_env/*"]
        ),
        
        "Стандартный анализ": AnalysisConfig(
            project_path="../../..",
            analysis_depth="standard", 
            max_files_per_analyzer=0,  # Убираем ограничение
            enable_caching=True,
            exclude_patterns=["*.pyc", "__pycache__", "*_env", "*/gopiai_env/*", "*/mcp_env/*", "*/txtai_env/*", "*/crewai_env/*"]
        ),
        
        "Полный анализ": AnalysisConfig(
            project_path="../../..",
            analysis_depth="full",
            max_files_per_analyzer=0,  # Убираем ограничение
            enable_caching=True,
            detailed_analysis=True,
            exclude_patterns=["*.pyc", "__pycache__", "*_env", "*/gopiai_env/*", "*/mcp_env/*", "*/txtai_env/*", "*/crewai_env/*"]
        )
    }
    
    for name, config in configs.items():
        print(f"\\n{name}:")
        print(f"  - Глубина анализа: {config.analysis_depth}")
        print(f"  - Макс. файлов: {config.max_files_per_analyzer}")
        print(f"  - Кэширование: {config.enable_caching}")
        print(f"  - Исключения: {len(config.exclude_patterns)} паттернов")


def main():
    """Главная функция демонстрации."""
    print("Project Analyzer - Демонстрация использования")
    print("=" * 50)
    
    try:
        # Демонстрация базового использования
        demo_basic_usage()
        
        # Демонстрация настройки конфигурации
        demo_custom_config()
        
        # Спрашиваем пользователя о полном анализе
        print("\\n" + "=" * 50)
        response = input("Запустить демонстрацию полного анализа? (y/n): ")
        if response.lower() == 'y':
            demo_full_analysis()
        
        print("\\nДемонстрация завершена!")
        
    except KeyboardInterrupt:
        print("\\nДемонстрация прервана пользователем.")
    except Exception as e:
        print(f"\\nОшибка во время демонстрации: {e}")


if __name__ == "__main__":
    main()
