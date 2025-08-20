"""
Project Analyzer - Комплексная система анализа проекта GOPI_AI_MODULES

Этот пакет предоставляет набор инструментов для анализа структуры проекта,
качества кода, зависимостей и других аспектов проекта GopiAI.

Основные компоненты:
- core: Основные анализаторы и инфраструктура
- runners: Исполняемые скрипты для различных типов анализа
- tests: Тесты для всех компонентов
- utils: Вспомогательные утилиты

Использование:
    from project_analyzer.core import AnalysisConfig, ProjectCleanupAnalyzer
    
    config = AnalysisConfig(project_path="/path/to/project")
    analyzer = ProjectCleanupAnalyzer(config)
    results = analyzer.run_full_analysis()
"""

from .core import (
    AnalysisResult,
    AnalysisConfig, 
    BaseAnalyzer,
    AnalysisError,
    ProjectCleanupAnalyzer,
    StructureAnalyzer,
    CodeQualityAnalyzer,
    DeadCodeAnalyzer,
    FileAnalyzer,
    DependencyAnalyzer,
    DocumentationAnalyzer,
    DuplicateAnalyzer,
    ConflictAnalyzer,
    ReportGenerator
)

__version__ = "1.0.0"
__author__ = "GopiAI Team"

__all__ = [
    'AnalysisResult',
    'AnalysisConfig',
    'BaseAnalyzer', 
    'AnalysisError',
    'ProjectCleanupAnalyzer',
    'StructureAnalyzer',
    'CodeQualityAnalyzer',
    'DeadCodeAnalyzer',
    'FileAnalyzer', 
    'DependencyAnalyzer',
    'DocumentationAnalyzer',
    'DuplicateAnalyzer',
    'ConflictAnalyzer',
    'ReportGenerator'
]