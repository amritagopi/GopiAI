"""
Модуль css_tools содержит набор утилит для работы с CSS/QSS файлами в GopiAI.

Основные утилиты:
- css_fixer.py - исправление дублирующихся селекторов
- css_refactor.py - рефакторинг CSS/QSS файлов, работа с цветами
- fix_duplicate_selectors.py - исправление вариаций селекторов
- fonts_fixer.py - исправление файлов шрифтов
- compile_themes.py и theme_compiler.py - компиляция тем
- cleanup.py - очистка проекта от ненужных файлов

Для запуска всех утилит исправления CSS используйте fix_css.bat
Для запуска очистки проекта используйте cleanup.bat
"""

from .css_fixer import fix_css_file
from .css_refactor import fix_duplicate_selectors, fix_hardcoded_colors
from .cleanup import cleanup_files, find_temp_files

__all__ = [
    'fix_css_file',
    'fix_duplicate_selectors',
    'fix_hardcoded_colors',
    'cleanup_files',
    'find_temp_files'
]
