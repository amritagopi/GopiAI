import json
import os
import re
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, Qt, QByteArray
from PySide6.QtSvg import QSvgRenderer
from app.logger import logger
from app.utils.theme_manager import ThemeManager

# Импортируем ресурсы
try:
    import icons_rc
except ImportError:
    logger.warning("Не удалось импортировать модуль icons_rc. Иконки могут быть недоступны.")

class IconManager:
    """Управляет иконками приложения, загруженными из ресурсов Qt."""

    _instance = None
    _cache = {}
    _svg_cache = {}  # Кеш для SVG данных

    # Основной цвет иконок, который будет заменяться
    ICON_BASE_COLOR = "#2ca9bc"

    @classmethod
    def instance(cls):
        """Возвращает единственный экземпляр менеджера иконок (паттерн Singleton)."""
        if cls._instance is None:
            cls._instance = IconManager()
        return cls._instance

    def __init__(self):
        """Инициализирует менеджер иконок, загружая манифест."""
        self.manifest = {}
        self._load_manifest()

        # Подключаемся к сигналу изменения темы
        try:
            theme_manager = ThemeManager.instance()
            theme_manager.themeChanged.connect(self.clear_cache)
            theme_manager.visualThemeChanged.connect(self.clear_cache)
        except Exception as e:
            logger.warning(f"Не удалось подключиться к сигналам менеджера тем: {e}")

    def clear_cache(self):
        """Очищает кеш иконок при изменении темы."""
        logger.info("Очистка кеша иконок из-за изменения темы")
        self._cache = {}

    def _load_svg_data(self, icon_file):
        """Загружает SVG данные из файла или ресурса."""
        if icon_file in self._svg_cache:
            return self._svg_cache[icon_file]

        svg_data = None
        try:
            # Пробуем загрузить из ресурсов
            resource_path = f":/icons/assets/icons/{icon_file}"
            file = open(resource_path, "rb")
            svg_data = file.read().decode('utf-8')
            file.close()
        except:
            # Если не удалось, пробуем из файловой системы
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "../.."))
                file_path = os.path.join(project_root, "assets", "icons", icon_file)

                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        svg_data = f.read()
            except Exception as e:
                logger.error(f"Ошибка загрузки SVG данных из {icon_file}: {e}")

        if svg_data:
            self._svg_cache[icon_file] = svg_data

        return svg_data

    def get_themed_icon(self, icon_name):
        """
        Возвращает иконку с цветом, соответствующим текущей теме.

        Args:
            icon_name (str): Имя иконки из манифеста

        Returns:
            QIcon: Объект иконки с цветом текущей темы или стандартную иконку
        """
        cache_key = f"themed_{icon_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Получаем имя файла из манифеста
        if icon_name not in self.manifest:
            return self.get_icon(icon_name)  # Используем обычную иконку, если нет в манифесте

        icon_file = self.manifest[icon_name]
        if not icon_file.endswith('.svg'):
            return self.get_icon(icon_name)  # Только SVG поддерживают замену цвета

        # Загружаем SVG данные
        svg_data = self._load_svg_data(icon_file)
        if not svg_data:
            return self.get_icon(icon_name)

        # Получаем цвет для замены из текущей темы
        try:
            theme_manager = ThemeManager.instance()
            theme_color = theme_manager.get_color('accent')
        except:
            theme_color = '#3498DB'  # Цвет по умолчанию

        # Заменяем цвет в SVG
        themed_svg = svg_data.replace(self.ICON_BASE_COLOR, theme_color)

        # Создаем иконку из измененного SVG
        svg_bytes = QByteArray(themed_svg.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)

        if renderer.isValid():
            pixmap = QPixmap(32, 32)  # Размер иконки
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            icon = QIcon(pixmap)
            self._cache[cache_key] = icon
            return icon

        # Если не удалось создать иконку с темой, возвращаем обычную
        return self.get_icon(icon_name)

    def _load_manifest(self):
        """Загружает манифест иконок."""
        try:
            # Сначала пробуем загрузить из ресурсов
            manifest_path = ":/icons/assets/icons/manifest.json"
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f).get("icons", {})
                logger.info(f"Загружен манифест из ресурсов: {len(self.manifest)} иконок доступно")
        except (FileNotFoundError, IOError):
            # Если не удалось, пробуем загрузить из файловой системы
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "../.."))
                manifest_path = os.path.join(project_root, "assets", "icons", "manifest.json")

                with open(manifest_path, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f).get("icons", {})
                    logger.info(f"Загружен манифест из файловой системы: {len(self.manifest)} иконок доступно")
            except (FileNotFoundError, IOError) as e:
                logger.error(f"Ошибка загрузки манифеста: {e}")
                self.manifest = {}

    def get_icon(self, icon_name):
        """
        Возвращает иконку по имени.

        Args:
            icon_name (str): Имя иконки из манифеста

        Returns:
            QIcon: Объект иконки или стандартную иконку, если не найдена
        """
        # Проверяем кеш
        if icon_name in self._cache:
            return self._cache[icon_name]

        # Проверяем манифест
        if icon_name in self.manifest:
            icon_file = self.manifest[icon_name]

            # Пробуем загрузить из ресурсов
            resource_path = f":/icons/assets/icons/{icon_file}"
            icon = QIcon(resource_path)

            # Если не удалось, пробуем из файловой системы
            if icon.isNull():
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "../.."))
                file_path = os.path.join(project_root, "assets", "icons", icon_file)

                if os.path.exists(file_path):
                    icon = QIcon(file_path)

            if not icon.isNull():
                # Кешируем иконку
                self._cache[icon_name] = icon
                return icon

        # Обработка специальных случаев отсутствующих иконок
        fallback_icon = None

        # Более новые имена указывают на более старые имена в манифесте
        # или на более общие иконки
        if icon_name == "python_file":
            fallback_icon = self.get_icon("python")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("text-x-python")
        elif icon_name == "text_file":
            fallback_icon = self.get_icon("text")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("text-plain")
        elif icon_name == "js_file":
            fallback_icon = self.get_icon("javascript")
        elif icon_name == "html_file":
            fallback_icon = self.get_icon("html")
        elif icon_name == "css_file":
            fallback_icon = self.get_icon("css")
        elif icon_name == "image_file":
            fallback_icon = self.get_icon("image_png")
        # Добавляем fallback для отсутствующих иконок
        elif icon_name.endswith("_file") and icon_name[:-5] in self.manifest:
            # Например, если запрошен "xml_file", а в манифесте есть "xml"
            fallback_icon = self.get_icon(icon_name[:-5])
        elif icon_name == "flow":
            fallback_icon = self.get_icon("settings")
        elif icon_name == "terminal":
            fallback_icon = self.get_icon("shell")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("utilities-terminal")
        elif icon_name == "agent":
            fallback_icon = self.get_icon("settings")
        elif icon_name == "browser":
            fallback_icon = self.get_icon("html")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("web-browser")
        elif icon_name == "save_config" or icon_name == "load_config":
            fallback_icon = self.get_icon("settings")
        # Специальные иконки для браузера
        elif icon_name == "arrow_left":
            fallback_icon = self.get_icon("back")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("go-previous")
        elif icon_name == "arrow_right":
            fallback_icon = self.get_icon("forward")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("go-next")
        elif icon_name == "refresh":
            fallback_icon = self.get_icon("reload")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("view-refresh")
        elif icon_name == "stop":
            fallback_icon = self.get_icon("close")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("process-stop")
        elif icon_name == "home":
            fallback_icon = self.get_icon("home_folder")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("go-home")
        elif icon_name == "go":
            fallback_icon = self.get_icon("run")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("media-playback-start")
        # Иконки для темной/светлой темы
        elif icon_name in ["close_white", "close_black"]:
            fallback_icon = self.get_icon("close")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("window-close")
        elif icon_name in ["float_white", "float_black"]:
            fallback_icon = self.get_system_icon("window-float")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("view-restore")
        elif icon_name in ["maximize_white", "maximize_black"]:
            fallback_icon = self.get_system_icon("window-maximize")
            if fallback_icon.isNull():
                fallback_icon = self.get_system_icon("view-fullscreen")

        # Если есть fallback иконка и она не пустая, возвращаем её
        if fallback_icon and not fallback_icon.isNull():
            self._cache[icon_name] = fallback_icon
            logger.debug(f"Иконка '{icon_name}' не найдена, используется замена")
            return fallback_icon

        # Если все варианты не сработали, используем стандартную иконку
        logger.warning(f"Иконка '{icon_name}' не найдена")
        default_icon = self.get_system_icon("document")
        if default_icon.isNull():
            logger.warning(f"Системная иконка document не найдена")
            return QIcon()  # Возвращаем пустую иконку
        return default_icon  # Возвращаем стандартную системную иконку

    def get_system_icon(self, name):
        """
        Получает системную иконку, если она доступна.

        Args:
            name (str): Имя системной иконки

        Returns:
            QIcon: Системная иконка или пустая иконка, если не найдена
        """
        # Словарь соответствия имен системных иконок для разных тем/платформ
        system_icon_map = {
            "window-float": ["view-restore", "window-restore"],
            "window-maximize": ["view-fullscreen", "window-maximize"],
            "window-close": ["window-close", "dialog-close", "application-exit"],
            "document": ["text-x-generic", "document", "accessories-text-editor"],
            "web-browser": ["internet-web-browser", "applications-internet", "web-browser"],
            "utilities-terminal": ["utilities-terminal", "terminal", "gnome-terminal"],
            "go-home": ["go-home", "user-home", "kfm_home"],
            "go-previous": ["go-previous", "back", "previous"],
            "go-next": ["go-next", "forward", "next"],
            "process-stop": ["process-stop", "stop", "cancel"],
            "view-refresh": ["view-refresh", "reload", "refresh"],
            "media-playback-start": ["media-playback-start", "play", "start"]
        }

        # Пытаемся найти иконку по различным именам
        if name in system_icon_map:
            for icon_name in system_icon_map[name]:
                icon = QIcon.fromTheme(icon_name)
                if not icon.isNull():
                    return icon
        else:
            # Если имя не в нашей карте, пробуем напрямую
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon

        # Если не нашли системную иконку, возвращаем пустую
        return QIcon()

    def list_available_icons(self):
        """Возвращает список имен доступных иконок."""
        return list(self.manifest.keys())

# Удобные глобальные функции
def get_icon(icon_name, use_theme=False):
    """
    Глобальная функция для получения иконки по имени.

    Args:
        icon_name (str): Имя иконки из манифеста
        use_theme (bool): Использовать цвета текущей темы

    Returns:
        QIcon: Объект иконки или пустая иконка, если не найдена
    """
    if use_theme:
        return IconManager.instance().get_themed_icon(icon_name)
    return IconManager.instance().get_icon(icon_name)

def get_themed_icon(icon_name):
    """
    Глобальная функция для получения иконки с цветами текущей темы.

    Args:
        icon_name (str): Имя иконки из манифеста

    Returns:
        QIcon: Объект иконки с цветами текущей темы или пустая иконка, если не найдена
    """
    return IconManager.instance().get_themed_icon(icon_name)

def get_system_icon(name):
    """
    Глобальная функция для получения системной иконки.

    Args:
        name (str): Имя системной иконки

    Returns:
        QIcon: Системная иконка или пустая иконка, если не найдена
    """
    return IconManager.instance().get_system_icon(name)

def list_icons():
    """Глобальная функция для получения списка имен доступных иконок."""
    return IconManager.instance().list_available_icons()
