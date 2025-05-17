"""
Main window implementation for GopiAI application.

This file imports the core MainWindow class and extends it with mixins.
"""

import logging
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from .main_window_core import MainWindowCore
from .main_window_components import apply_mixins
from app.ui.i18n.translator import tr

logger = logging.getLogger(__name__)

# Создаем класс MainWindow, применяя миксины к базовому классу MainWindowCore
MainWindow = apply_mixins(MainWindowCore)

# Добавляем метод для инициализации сигналов после создания экземпляра MainWindow
def initialize_signals(main_window):
    """
    Инициализирует автоматическое подключение сигналов после применения всех миксинов.
    Вызывается после создания экземпляра MainWindow.

    Args:
        main_window: Экземпляр MainWindow
    """
    try:
        # Отложенный запуск проверки сигналов, чтобы все компоненты успели инициализироваться
        QTimer.singleShot(1000, lambda: _run_signal_checks(main_window))
        logger.info("Scheduled delayed signal checks")
    except Exception as e:
        logger.error(f"Error scheduling signal checks: {e}")

def _run_signal_checks(main_window):
    """
    Запускает автоматическое подключение сигналов и показывает результаты.

    Args:
        main_window: Экземпляр MainWindow
    """
    try:
        logger.info("Running signal auto-connection...")

        # Запускаем автоматическое подключение сигналов
        connected_count, connections_info = main_window._auto_connect_signals()

        if connected_count == 0:
            logger.info("No signals auto-connected")
            return

        # Формируем подробную информацию о подключениях
        details = tr(
            "dialog.signals_auto.details",
            f"Автоматически подключено {connected_count} сигналов:\n\n",
        )
        for obj_path, signals in connections_info.items():
            details += f"✓ {obj_path}:\n"
            for signal_name in signals:
                details += f"   - {signal_name}\n"
            details += "\n"

        # Показываем информационное сообщение в терминале
        logger.info(f"Auto-connected {connected_count} signals. Details:\n{details}")

        # Показываем информацию в статусной строке, если она доступна
        if hasattr(main_window, "status_bar") and main_window.status_bar:
            main_window.status_bar.showMessage(
                tr(
                    "status.signals_auto_connected",
                    f"Подключено {connected_count} сигналов",
                ),
                5000,
            )
    except Exception as e:
        logger.error(f"Error running signal checks: {e}")
