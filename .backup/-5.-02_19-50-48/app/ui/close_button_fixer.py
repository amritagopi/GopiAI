"""
Модуль для фиксации проблем с кнопками закрытия вкладок в PySide6.
"""
from PySide6.QtWidgets import QTabBar, QTabWidget, QMainWindow, QDockWidget
from PySide6.QtCore import Qt, QEvent
import os


class CloseButtonFixer:
    """
    Класс для исправления проблем с кнопками закрытия вкладок в PySide6.

    PySide6 имеет проблему с кнопками закрытия вкладок,
    которые могут отображаться некорректно или не отображаться вовсе.
    Этот класс исправляет эти проблемы, применяя необходимые стили и настройки.
    """

    @staticmethod
    def apply_to_window(window):
        """
        Применяет фиксы к главному окну приложения.

        Args:
            window (QMainWindow): Главное окно приложения.
        """
        # Применяем фикс ко всем QTabWidget в главном окне
        for tab_widget in window.findChildren(QTabWidget):
            CloseButtonFixer.apply_to_tab_widget(tab_widget)

        # Применяем фикс ко всем QDockWidget в главном окне
        for dock_widget in window.findChildren(QDockWidget):
            # Обрабатываем только доки, у которых есть QTabWidget
            for tab_widget in dock_widget.findChildren(QTabWidget):
                CloseButtonFixer.apply_to_tab_widget(tab_widget)

        # Возвращаем True, если фикс был применен успешно
        return True

    @staticmethod
    def apply_to_tab_widget(tab_widget):
        """
        Применяет фиксы к конкретному QTabWidget.

        Args:
            tab_widget (QTabWidget): Виджет с вкладками, к которому применяется фикс.
        """
        # Получаем QTabBar из QTabWidget
        tab_bar = tab_widget.tabBar()

        # Включаем кнопки закрытия, если они еще не включены
        tab_widget.setTabsClosable(True)

        # Устанавливаем минимальную ширину кнопки закрытия
        tab_bar.setStyleSheet("""
            QTabBar::close-button {
                margin: 2px;
                min-width: 16px;
                min-height: 16px;
            }

            QTabBar::close-button:hover {
                background-color: rgba(255, 85, 85, 0.3);
                border-radius: 4px;
            }
        """)

        # Устанавливаем политику для кнопок закрытия (всегда показывать)
        tab_bar.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)

        # Обновляем QTabBar, чтобы изменения вступили в силу
        tab_bar.update()

        # Возвращаем True, если фикс был применен успешно
        return True

# Для интеграции в MainWindow:
"""
# В файле main_window.py добавьте импорт:
from .close_button_fixer import CloseButtonFixer

# В методе __init__ после создания central_tabs:
CloseButtonFixer.apply_to_window(self)

# Также добавьте в метод _toggle_theme для обновления при смене темы:
def _toggle_theme(self, is_dark):
    # ... существующий код ...

    # Обновляем иконки закрытия вкладок после смены темы
    CloseButtonFixer.apply_to_window(self)
"""
