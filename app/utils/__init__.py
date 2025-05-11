"""
Модуль утилит для приложения.
"""

from .file_operations import *
from .theme_manager import ThemeManager
from .error_handling import *
from .common import *
from .signal_checker import SignalConnectionChecker, SignalMonitor, check_main_window_signals

# Создаем экземпляр ThemeManager для использования в других модулях
theme_manager = ThemeManager.instance()
