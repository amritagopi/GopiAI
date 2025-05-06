from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, Signal, QSettings
import os
import json
from app.logger import logger

class ThemeManager(QObject):
    """Централизованный менеджер тем для GopiAI."""

    # Сигнал для изменения только визуальной темы
    visualThemeChanged = Signal(str)

    # Сигнал при изменении темы
    themeChanged = Signal(str)

    # Темная тема
    DARK_THEME = {
        'background': '#2D2D2D',
        'foreground': '#FFFFFF',
        'accent': '#3498DB',
        'secondary': '#555555',
        'error': '#E74C3C',
        'success': '#2ECC71',
        'warning': '#F39C12',
        'border': '#444444',
        'tab_active': '#3498DB',
        'tab_inactive': '#555555',
        'button_normal': '#555555',
        'button_hover': '#3498DB',
        'button_pressed': '#2980B9',
        'input_background': '#3D3D3D',
        'input_text': '#FFFFFF',
        'input_border': '#555555'
    }

    # Светлая тема
    LIGHT_THEME = {
        'background': '#F5F5F5',
        'foreground': '#333333',
        'accent': '#2980B9',
        'secondary': '#DDDDDD',
        'error': '#C0392B',
        'success': '#27AE60',
        'warning': '#E67E22',
        'border': '#CCCCCC',
        'tab_active': '#2980B9',
        'tab_inactive': '#DDDDDD',
        'button_normal': '#DDDDDD',
        'button_hover': '#2980B9',
        'button_pressed': '#3498DB',
        'input_background': '#FFFFFF',
        'input_text': '#333333',
        'input_border': '#CCCCCC'
    }

    _instance = None

    @classmethod
    def instance(cls, app=None):
        """Получение единственного экземпляра менеджера тем (паттерн Singleton)."""
        if cls._instance is None:
            if app is None:
                raise ValueError("При первом вызове необходимо передать экземпляр QApplication")
            cls._instance = ThemeManager(app)
        return cls._instance

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_visual_theme = 'light'  # Только визуальная тема (light/dark)

        self.themes = {
            'dark': self.DARK_THEME,
            'light': self.LIGHT_THEME
        }

        # Загружаем пользовательские настройки темы, если они есть
        self.load_user_theme_settings()

    def load_user_theme_settings(self):
        """Загружает пользовательские настройки темы из файла конфигурации."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'visual_theme' in config:
                        self.current_visual_theme = config['visual_theme']
                    if 'custom_themes' in config:
                        for theme_name, theme_colors in config['custom_themes'].items():
                            self.themes[theme_name] = theme_colors
                logger.info(f"Загружены настройки темы: {self.current_visual_theme}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек темы: {str(e)}")

    def save_user_theme_settings(self):
        """Сохраняет пользовательские настройки темы в файл конфигурации."""
        try:
            config = {
                'visual_theme': self.current_visual_theme,
                'custom_themes': {k: v for k, v in self.themes.items() if k not in ['dark', 'light']}
            }
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Сохранены настройки темы: {self.current_visual_theme}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек темы: {str(e)}")

    def get_color(self, key):
        """Получает цвет из текущей темы."""
        theme_type = self.current_visual_theme
        if theme_type not in self.themes:
            theme_type = 'light'

        if key not in self.themes[theme_type]:
            logger.warning(f"Цвет '{key}' не найден в теме '{theme_type}', используется значение по умолчанию")
            return "#000000"  # Возвращаем черный цвет по умолчанию
        return self.themes[theme_type][key]

    def get_qcolor(self, key):
        """Получает QColor из текущей темы."""
        return QColor(self.get_color(key))

    def switch_visual_theme(self, visual_theme):
        """Переключает только визуальную тему."""
        if visual_theme not in self.get_available_visual_themes():
            logger.error(f"Визуальная тема '{visual_theme}' не поддерживается")
            return False

        if self.current_visual_theme == visual_theme:
            logger.info(f"Визуальная тема '{visual_theme}' уже установлена")
            return True

        logger.info(f"Переключение визуальной темы с '{self.current_visual_theme}' на '{visual_theme}'")
        self.current_visual_theme = visual_theme

        # Применяем стиль
        self._apply_visual_theme()

        self.save_user_theme_settings()
        logger.info(f"Применена визуальная тема: {visual_theme}")

        # Уведомляем подписчиков об изменении темы
        self.visualThemeChanged.emit(visual_theme)

        return True

    def _apply_visual_theme(self):
        """Применяет визуальную тему к приложению."""
        theme_qss_path = self.get_theme_qss_path()

        # Пытаемся загрузить QSS из файла
        if os.path.exists(theme_qss_path):
            try:
                with open(theme_qss_path, 'r', encoding='utf-8') as f:
                    self.app.setStyleSheet(f.read())
                logger.info(f"Применен стиль из файла: {theme_qss_path}")
            except Exception as e:
                logger.error(f"Ошибка при чтении файла стиля: {str(e)}")
                # Если не удалось прочитать файл, генерируем стиль программно
                self.app.setStyleSheet(self._generate_stylesheet())
                logger.info("Применен программно сгенерированный стиль")
        else:
            # Если файл не существует, генерируем стиль программно
            self.app.setStyleSheet(self._generate_stylesheet())
            logger.info("Применен программно сгенерированный стиль (файл не найден)")

    def add_custom_theme(self, theme_name, theme_colors):
        """Добавляет пользовательскую тему цветов."""
        if theme_name in self.themes and theme_name in ['light', 'dark']:
            logger.warning(f"Невозможно перезаписать встроенную тему '{theme_name}'")
            return False

        self.themes[theme_name] = theme_colors
        self.save_user_theme_settings()
        logger.info(f"Добавлена пользовательская тема: {theme_name}")
        return True

    def _generate_stylesheet(self):
        """Генерирует таблицу стилей программно на основе текущей темы."""
        theme_type = self.current_visual_theme
        if theme_type not in self.themes:
            theme_type = 'light'

        colors = self.themes[theme_type]

        # Генерируем базовый QSS для приложения
        return f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {colors.get('background', '#F5F5F5')};
            color: {colors.get('foreground', '#333333')};
        }}

        QMenuBar, QMenu {{
            background-color: {colors.get('background', '#F5F5F5')};
            color: {colors.get('foreground', '#333333')};
            border: 1px solid {colors.get('border', '#CCCCCC')};
        }}

        QMenuBar::item:selected, QMenu::item:selected {{
            background-color: {colors.get('accent', '#2980B9')};
            color: white;
        }}

        QPushButton {{
            background-color: {colors.get('button_normal', '#DDDDDD')};
            color: {colors.get('foreground', '#333333')};
            border: 1px solid {colors.get('border', '#CCCCCC')};
            padding: 5px 10px;
            border-radius: 3px;
        }}

        QPushButton:hover {{
            background-color: {colors.get('button_hover', '#2980B9')};
            color: white;
        }}

        QPushButton:pressed {{
            background-color: {colors.get('button_pressed', '#3498DB')};
            color: white;
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QListView, QTreeView, QTableView {{
            background-color: {colors.get('input_background', '#FFFFFF')};
            color: {colors.get('input_text', '#333333')};
            border: 1px solid {colors.get('input_border', '#CCCCCC')};
            selection-background-color: {colors.get('accent', '#2980B9')};
            selection-color: white;
        }}

        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
        }}

        QTabBar::tab {{
            background-color: {colors.get('tab_inactive', '#DDDDDD')};
            color: {colors.get('foreground', '#333333')};
            padding: 5px 10px;
            border: 1px solid {colors.get('border', '#CCCCCC')};
            border-bottom: none;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors.get('tab_active', '#2980B9')};
            color: white;
        }}

        QDockWidget {{
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }}

        QDockWidget::title {{
            background-color: {colors.get('secondary', '#DDDDDD')};
            padding-left: 5px;
            padding-top: 2px;
        }}

        QDockWidget::close-button, QDockWidget::float-button {{
            background-color: {colors.get('secondary', '#DDDDDD')};
            border: 1px solid {colors.get('border', '#CCCCCC')};
            border-radius: 2px;
        }}

        QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
            background-color: {colors.get('accent', '#2980B9')};
        }}

        QToolBar {{
            background-color: {colors.get('background', '#F5F5F5')};
            border: 1px solid {colors.get('border', '#CCCCCC')};
            spacing: 3px;
        }}

        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 3px;
        }}

        QToolButton:hover {{
            background-color: {colors.get('button_hover', '#2980B9')};
            color: white;
            border: 1px solid {colors.get('border', '#CCCCCC')};
        }}

        QToolButton:pressed {{
            background-color: {colors.get('button_pressed', '#3498DB')};
        }}

        QComboBox {{
            background-color: {colors.get('input_background', '#FFFFFF')};
            color: {colors.get('input_text', '#333333')};
            border: 1px solid {colors.get('input_border', '#CCCCCC')};
            padding: 3px;
            border-radius: 2px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: {colors.get('border', '#CCCCCC')};
            border-left-style: solid;
        }}

        QProgressBar {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            border-radius: 2px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {colors.get('accent', '#2980B9')};
            width: 10px;
            margin: 0.5px;
        }}

        QScrollBar:vertical {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            width: 15px;
            margin: 15px 0 15px 0;
        }}

        QScrollBar::handle:vertical {{
            background: {colors.get('secondary', '#DDDDDD')};
            min-height: 20px;
        }}

        QScrollBar::add-line:vertical {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            height: 15px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}

        QScrollBar::sub-line:vertical {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            height: 15px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}

        QScrollBar:horizontal {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            height: 15px;
            margin: 0px 15px 0 15px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors.get('secondary', '#DDDDDD')};
            min-width: 20px;
        }}

        QScrollBar::add-line:horizontal {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            width: 15px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}

        QScrollBar::sub-line:horizontal {{
            border: 1px solid {colors.get('border', '#CCCCCC')};
            background: {colors.get('input_background', '#FFFFFF')};
            width: 15px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }}

        QStatusBar {{
            background-color: {colors.get('background', '#F5F5F5')};
            color: {colors.get('foreground', '#333333')};
            border-top: 1px solid {colors.get('border', '#CCCCCC')};
        }}

        QSplitter::handle {{
            background-color: {colors.get('border', '#CCCCCC')};
        }}
        """

    def get_theme_qss_path(self):
        """Получает путь к файлу QSS для текущей темы."""
        theme_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "themes")
        return os.path.join(theme_dir, f"{self.current_visual_theme}.qss")

    def get_available_visual_themes(self):
        """Получает список доступных визуальных тем."""
        return list(self.themes.keys())

    def get_current_visual_theme(self):
        """Возвращает текущую визуальную тему."""
        return self.current_visual_theme

    def get_theme_display_name(self, theme_name):
        """Получает отображаемое имя темы."""
        theme_names = {
            "light": "Светлая тема",
            "dark": "Темная тема"
        }

        if theme_name.startswith("custom_"):
            base_theme = theme_name.split("_", 1)[1]
            return f"Пользовательская {theme_names.get(base_theme, base_theme)}"

        return theme_names.get(theme_name, theme_name)

# Пример использования:
# from app.utils.theme_manager import ThemeManager
# app = QApplication([])
# theme_manager = ThemeManager.instance(app)
# theme_manager.set_theme('dark')  # или 'light'
