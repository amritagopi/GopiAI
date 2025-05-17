"""
Утилиты UI для GopiAI.

Содержит инструменты для работы с пользовательским интерфейсом, темами, CSS и диагностики UI.
"""

# CSS-инструменты доступны из этого пакета
from app.ui.utils.css_tools import (
    cleanup_files,
    find_temp_files,
    fix_css_file,
    fix_duplicate_selectors,
    fix_hardcoded_colors,
)
from app.utils.theme_manager import ThemeManager

__all__ = [
    "ThemeManager",
    "fix_css_file",
    "fix_duplicate_selectors",
    "fix_hardcoded_colors",
    "cleanup_files",
    "find_temp_files",
]
