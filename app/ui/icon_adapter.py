"""
Адаптер для интеграции LucideIconManager с существующим кодом.

Этот модуль предоставляет совместимость с существующим кодом, который использует
старый IconManager, но перенаправляет запросы к новому LucideIconManager.
"""

import logging
from typing import Any, Dict, Optional, Union

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, QPixmap

from app.ui.lucide_icon_manager import LucideIconManager

logger = logging.getLogger(__name__)

# Карта соответствия старых имен иконок новым именам Lucide
ICON_NAME_MAPPING = {
    # Общие иконки
    "home": "home",
    "settings": "settings",
    "folder": "folder",
    "file": "file",
    "folder_open": "folder-open",
    "terminal": "terminal",
    "code": "code",
    "text_file": "file-text",
    "refresh": "refresh-cw",
    "save": "save",
    "search": "search",
    "info": "info",
    "link": "link",
    "documentation": "book",
    "preferences": "settings",
    "browser": "globe",
    "run": "play",
    "close": "x",
    "emoji": "smile",
    "chat": "message-circle",
    "open": "folder-open",
    "python_file": "file-code",
    "markdown": "file-text",
    "flow": "git-branch",
    "debug": "bug",
    "app_icon": "cpu",
    "arrow_left": "arrow-left",
    "arrow_right": "arrow-right",
    "arrow_up": "arrow-up",
    "arrow_down": "arrow-down",
    "cut": "scissors",
    "copy": "copy",
    "paste": "clipboard",
    "play": "play",
    "arrow": "arrow-down",
    "close_black": "x",
    "close_white": "x",
    "maximize_black": "maximize",
    "maximize_white": "maximize",
    "float_black": "box",
    "float_white": "box",
    "git": "git-branch",
    # Дополнительные маппинги для браузера
    "back": "chevron-left",
    "forward": "chevron-right",
    "stop": "x-circle",
    "analyze": "search-check",
    "view": "eye",
    "clear": "trash-2",
    # Дополнительные маппинги для типов файлов
    "js_file": "file-code",
    "html_file": "file-code",
    "css_file": "file-code",
    "json": "braces",
    "image_file": "image",
    "document": "file-text",
    "spreadsheet": "table",
    "pdf": "file-text",
    "archive": "archive",
    "home_folder": "home",
    "drive": "hard-drive",
    "agent": "bot",
    "tools": "tool",
    "console": "terminal",
    "inspect": "search",
    "message-square": "message-square",
    "check-circle": "check-circle",
    "file-plus": "file-plus",
    "save-all": "save-all",
    "grid": "grid",
    "palette": "palette",
    "file-code": "file-code",
    "undo": "undo",
    "redo": "redo",
    # Дополнительные иконки для различных UI компонентов
    "minimize": "minimize",
    "maximize": "maximize",
    "restore": "move",
    "dock": "layout",
    "pin": "pin",
    "unpin": "pin-off",
    "edit": "edit",
    "delete": "trash",
    "add": "plus",
    "remove": "minus",
    "check": "check",
    "x-circle": "x-circle",
    "alert": "alert-triangle",
    "warning": "alert-triangle",
    "error": "alert-octagon",
    "success": "check-circle",
    "info-circle": "info",
    "help": "help-circle",
    "settings-2": "settings-2",
    "user": "user",
    "logout": "log-out",
    "login": "log-in",
    "menu": "menu",
    "more": "more-horizontal",
    "more-vertical": "more-vertical",
    "send": "send",
    "upload": "upload",
    "download": "download",
    "camera": "camera",
    "mic": "mic",
    "mic-off": "mic-off",
    "video": "video",
    "video-off": "video-off",
    "speaker": "volume-2",
    "mute": "volume-x",
    "calendar": "calendar",
    "clock": "clock",
    "bell": "bell",
    "star": "star",
    "heart": "heart",
    "bookmark": "bookmark",
    "flag": "flag",
    "trash": "trash",
    "archive": "archive",
    "package": "package",
    "gift": "gift",
    "coffee": "coffee",
    "briefcase": "briefcase",
    "music": "music",
    "filter": "filter",
    "database": "database",
    "server": "server",
    "power": "power",
    "wifi": "wifi",
    "bluetooth": "bluetooth",
    "share": "share",
    "eye": "eye",
    "eye-off": "eye-off",
    "lock": "lock",
    "unlock": "unlock",
    "key": "key",
    "hash": "hash",
    "at-sign": "at-sign",
    "cloud": "cloud",
    "layers": "layers",
    "list": "list",
    "grid-view": "grid",
    "list-view": "list",
    "shuffle": "shuffle",
    "repeat": "repeat",
    "crop": "crop",
    "rotate": "rotate-cw",
    "zoom-in": "zoom-in",
    "zoom-out": "zoom-out",
    "monitor": "monitor",
    "tablet": "tablet",
    "smartphone": "smartphone",
    "laptop": "laptop",
    "printer": "printer",
    "shopping-bag": "shopping-bag",
    "shopping-cart": "shopping-cart",
    "tag": "tag",
    "scissors": "scissors",
    "paperclip": "paperclip",
    "map": "map",
    "map-pin": "map-pin",
    "navigation": "navigation",
    "globe": "globe",
    "umbrella": "umbrella",
    "mail": "mail",
    "message": "message-circle",
    "phone": "phone",
    "signal": "signal",
    "battery": "battery",
    "headphones": "headphones",
    "trending-up": "trending-up",
    "trending-down": "trending-down",
    "bar-chart": "bar-chart",
    "pie-chart": "pie-chart",
    "line-chart": "line-chart",
    "activity": "activity",
    "disc": "disc",
    "droplet": "droplet",
    "credit-card": "credit-card",
    "anchor": "anchor",
    "award": "award",
    "zap": "zap",
    # Любые другие маппинги...
}


class IconAdapter:
    """
    Адаптер для интеграции LucideIconManager с существующим кодом.

    Предоставляет тот же интерфейс, что и старый IconManager,
    но использует LucideIconManager под капотом.
    """

    _instance = None

    @classmethod
    def instance(cls):
        """Получение единственного экземпляра адаптера (паттерн Singleton)."""
        if cls._instance is None:
            cls._instance = IconAdapter()
        return cls._instance

    def __init__(self):
        """Инициализация адаптера."""
        self.lucide_manager = LucideIconManager.instance()
        logger.info("IconAdapter инициализирован")

    def get_icon(
        self,
        icon_name: str,
        color_override: Optional[str] = None,
        size: Union[QSize, int] = QSize(24, 24),
    ) -> QIcon:
        """
        Получение иконки по имени (совместимость со старым API).

        Args:
            icon_name: Имя иконки (в старой нотации)
            color_override: Цвет иконки в формате CSS (#RRGGBB)
            size: Размер иконки (QSize или int)

        Returns:
            QIcon: Объект иконки Qt
        """
        # Приводим размер к QSize, если передано число
        if isinstance(size, int):
            size = QSize(size, size)

        # Маппинг имени в новую нотацию
        lucide_name = self._map_icon_name(icon_name)

        # Получаем иконку через LucideIconManager
        return self.lucide_manager.get_icon(lucide_name, color_override, size)

    def _map_icon_name(self, old_name: str) -> str:
        """
        Преобразование старого имени иконки в имя Lucide.

        Args:
            old_name: Старое имя иконки

        Returns:
            str: Имя иконки в формате Lucide
        """
        # Если имя уже в формате Lucide, возвращаем как есть
        if "-" in old_name:
            return old_name

        # Проверяем маппинг
        if old_name in ICON_NAME_MAPPING:
            return ICON_NAME_MAPPING[old_name]

        # Пытаемся преобразовать snake_case в kebab-case
        if "_" in old_name:
            return old_name.replace("_", "-")

        # Если нет точного соответствия, проверяем fallback для типов файлов
        if old_name.endswith("_file"):
            return "file-text"

        # Возвращаем исходное имя, если нет соответствия
        logger.warning(f"Нет маппинга для иконки: {old_name}")
        return old_name

    def get_system_icon(self, name):
        """Совместимость со старым get_system_icon."""
        return self.get_icon(name)

    def list_available_icons(self):
        """Список доступных иконок."""
        return self.lucide_manager.list_available_icons()

    def clear_cache(self):
        """Очистка кеша иконок."""
        self.lucide_manager.clear_cache()


# Функция-хелпер для обратной совместимости
def get_icon(icon_name, color=None, size=24):
    """Функция для получения иконки (для обратной совместимости)."""
    return IconAdapter.instance().get_icon(icon_name, color, size)
