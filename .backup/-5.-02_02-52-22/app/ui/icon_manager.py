import json
import os
from PySide6.QtGui import QIcon

# Импортируем ресурсы
try:
    import icons_rc
except ImportError:
    print("Warning: Failed to import icons_rc module. Icons may not be available.")

class IconManager:
    """Управляет иконками приложения, загруженными из ресурсов Qt."""

    _instance = None
    _cache = {}

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

    def _load_manifest(self):
        """Загружает манифест иконок."""
        try:
            # Сначала пробуем загрузить из ресурсов
            manifest_path = ":/icons/assets/icons/manifest.json"
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f).get("icons", {})
                print(f"Loaded manifest from resources: {len(self.manifest)} icons available")
        except (FileNotFoundError, IOError):
            # Если не удалось, пробуем загрузить из файловой системы
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "../.."))
                manifest_path = os.path.join(project_root, "assets", "icons", "manifest.json")

                with open(manifest_path, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f).get("icons", {})
                    print(f"Loaded manifest from file system: {len(self.manifest)} icons available")
            except (FileNotFoundError, IOError) as e:
                print(f"Error loading manifest: {e}")
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
                fallback_icon = QIcon.fromTheme("text-x-python")
        elif icon_name == "text_file":
            fallback_icon = self.get_icon("text")
            if fallback_icon.isNull():
                fallback_icon = QIcon.fromTheme("text-plain")
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
        elif icon_name == "agent":
            fallback_icon = self.get_icon("settings")
        elif icon_name == "browser":
            fallback_icon = self.get_icon("html")
        elif icon_name == "save_config" or icon_name == "load_config":
            fallback_icon = self.get_icon("settings")
        # Специальные иконки для браузера
        elif icon_name == "arrow_left":
            fallback_icon = self.get_icon("back")
        elif icon_name == "arrow_right":
            fallback_icon = self.get_icon("forward")
        elif icon_name == "refresh":
            fallback_icon = self.get_icon("reload")
        elif icon_name == "stop":
            fallback_icon = self.get_icon("close")
        elif icon_name == "home":
            fallback_icon = self.get_icon("home_folder")
        elif icon_name == "go":
            fallback_icon = self.get_icon("run")

        # Если есть fallback иконка и она не пустая, возвращаем её
        if fallback_icon and not fallback_icon.isNull():
            self._cache[icon_name] = fallback_icon
            print(f"Icon '{icon_name}' not found, using fallback")
            return fallback_icon

        # Если все варианты не сработали, используем стандартную иконку
        print(f"Icon '{icon_name}' not found")
        default_icon = QIcon.fromTheme("document")
        if default_icon.isNull():
            return QIcon()  # Возвращаем пустую иконку
        return default_icon  # Возвращаем стандартную системную иконку

    def list_available_icons(self):
        """Возвращает список имен доступных иконок."""
        return list(self.manifest.keys())

# Удобные глобальные функции
def get_icon(icon_name):
    """
    Глобальная функция для получения иконки по имени.

    Args:
        icon_name (str): Имя иконки из манифеста

    Returns:
        QIcon: Объект иконки или пустая иконка, если не найдена
    """
    return IconManager.instance().get_icon(icon_name)

def list_icons():
    """Возвращает список имен доступных иконок."""
    return IconManager.instance().list_available_icons()
