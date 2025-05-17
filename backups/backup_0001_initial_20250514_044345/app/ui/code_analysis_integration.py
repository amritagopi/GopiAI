import logging
import os

from PySide6.QtCore import Qt, QObject, Signal, Slot, QSize
from PySide6.QtWidgets import QAction, QMessageBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtGui import QFont

from .code_analysis_widget import (CodeAnalysisWidget,
                                   integrate_code_analysis_widget)
from .i18n.translator import tr
from .icon_adapter import get_icon

logger = logging.getLogger(__name__)

def integrate_with_main_window(main_window):
    """
    Интегрирует функциональность анализа кода с главным окном приложения.

    Добавляет пункт меню и действие для открытия инструмента анализа кода.
    """
    try:
        # Добавляем действие в меню Tools
        code_analysis_action = QAction(
            get_icon("analyze"),
            tr("menu.tools.code_analysis", "Анализ кода"),
            main_window
        )
        code_analysis_action.setStatusTip(
            tr("menu.tools.code_analysis.tooltip", "Запустить инструменты анализа кода")
        )
        code_analysis_action.triggered.connect(lambda: open_code_analysis_widget(main_window))

        # Получаем меню Tools
        if hasattr(main_window, 'tools_menu'):
            # Добавляем разделитель, если в меню уже есть действия
            if len(main_window.tools_menu.actions()) > 0:
                main_window.tools_menu.addSeparator()

            # Добавляем действие в меню
            main_window.tools_menu.addAction(code_analysis_action)
            logger.info("Действие анализа кода добавлено в меню Tools")
        else:
            logger.warning("Меню Tools не найдено в главном окне")

        # Сохраняем ссылку на действие
        main_window.code_analysis_action = code_analysis_action

        # Добавляем в тулбар, если он существует
        if hasattr(main_window, 'main_toolbar'):
            main_window.main_toolbar.addSeparator()
            main_window.main_toolbar.addAction(code_analysis_action)
            logger.info("Действие анализа кода добавлено в основную панель инструментов")

        # Установка горячей клавиши
        code_analysis_action.setShortcut("Ctrl+Shift+A")

        logger.info("Интеграция анализа кода с главным окном выполнена успешно")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при интеграции анализа кода с главным окном: {e}")
        return False

def open_code_analysis_widget(main_window):
    """
    Открывает виджет анализа кода.
    """
    try:
        # Интегрируем виджет анализа кода с главным окном
        widget = integrate_code_analysis_widget(main_window)

        if widget:
            # Показываем сообщение в статус-баре
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(
                    tr("code_analysis.opened", "Инструмент анализа кода открыт"), 3000
                )

            logger.info("Виджет анализа кода успешно открыт")
            return widget
        else:
            logger.error("Не удалось создать виджет анализа кода")
            return None
    except Exception as e:
        logger.exception(f"Ошибка при открытии виджета анализа кода: {e}")
        QMessageBox.critical(
            main_window,
            tr("code_analysis.error", "Ошибка"),
            tr("code_analysis.open_error", f"Ошибка при открытии инструмента анализа кода: {str(e)}")
        )
        return None
