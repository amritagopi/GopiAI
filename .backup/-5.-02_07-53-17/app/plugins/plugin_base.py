from typing import Optional, Dict, Any, Callable
from PySide6.QtCore import QObject


class PluginBase(QObject):
    """
    Базовый класс для всех плагинов приложения.
    Описывает стандартный интерфейс, который должны реализовывать все плагины.
    """

    # Статические атрибуты для метаданных плагина
    NAME = "base_plugin"  # Уникальный идентификатор плагина
    DISPLAY_NAME = "Base Plugin"  # Отображаемое имя
    DESCRIPTION = "Base plugin class"  # Описание
    VERSION = "1.0.0"  # Версия
    AUTHOR = "GopiAI"  # Автор

    def __init__(self, parent: Optional[QObject] = None):
        """
        Инициализирует плагин.

        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        self.main_window = None

    def initialize(self, main_window):
        """
        Инициализирует плагин.
        Этот метод вызывается после загрузки плагина.

        Args:
            main_window: Главное окно приложения
        """
        self.main_window = main_window

    def cleanup(self):
        """
        Очищает ресурсы, занятые плагином.
        Этот метод вызывается перед выгрузкой плагина.
        """
        pass

    def save_settings(self):
        """
        Сохраняет настройки плагина.
        Этот метод вызывается перед выходом из приложения.
        """
        pass

    def add_menu_item(self, menu: str, item_text: str, callback: Callable, enabled: bool = True, shortcut: Optional[str] = None):
        """
        Добавляет пункт меню.

        Args:
            menu: Имя меню ("file", "edit", "view", "tools", "help")
            item_text: Текст пункта меню
            callback: Функция, вызываемая при выборе пункта меню
            enabled: Доступность пункта меню
            shortcut: Горячая клавиша (например, "Ctrl+P")
        """
        if self.main_window and hasattr(self.main_window, "add_menu_action"):
            self.main_window.add_menu_action(menu, item_text, callback, enabled, shortcut)

    def add_toolbar_action(self, text: str, callback: Callable, icon_path: Optional[str] = None,
                          tooltip: Optional[str] = None, enabled: bool = True, checkable: bool = False):
        """
        Добавляет кнопку на панель инструментов.

        Args:
            text: Текст кнопки
            callback: Функция, вызываемая при нажатии кнопки
            icon_path: Путь к иконке
            tooltip: Подсказка при наведении
            enabled: Доступность кнопки
            checkable: Может ли кнопка быть "нажатой"
        """
        if self.main_window and hasattr(self.main_window, "add_toolbar_action"):
            self.main_window.add_toolbar_action(text, callback, icon_path, tooltip, enabled, checkable)

    def metadata(self) -> Dict[str, Any]:
        """
        Возвращает метаданные плагина.

        Returns:
            Словарь с метаданными
        """
        return {
            "name": self.NAME,
            "display_name": self.DISPLAY_NAME,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "author": self.AUTHOR
        }
