from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor

class ThemeManager:
    """Централизованный менеджер тем для GopiAI."""
    
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
        self.app = app
        self.current_theme = 'dark'
        self.themes = {
            'dark': self.DARK_THEME,
            'light': self.LIGHT_THEME
        }
    
    def get_color(self, key):
        """Получает цвет из текущей темы."""
        if key not in self.themes[self.current_theme]:
            raise KeyError(f"Цвет '{key}' не найден в теме '{self.current_theme}'")
        return self.themes[self.current_theme][key]
    
    def get_qcolor(self, key):
        """Получает QColor из текущей темы."""
        return QColor(self.get_color(key))
    
    def set_theme(self, theme_name):
        """Устанавливает тему для всего приложения."""
        if theme_name not in self.themes:
            raise ValueError(f"Тема '{theme_name}' не существует")
        
        self.current_theme = theme_name
        self.app.setStyleSheet(self._generate_stylesheet())
    
    def _generate_stylesheet(self):
        """Генерирует QSS на основе текущей темы."""
        theme = self.themes[self.current_theme]
        
        return f"""
        /* Основные стили */
        QWidget {{
            background-color: {theme['background']};
            color: {theme['foreground']};
        }}
        
        /* Кнопки */
        QPushButton {{
            background-color: {theme['button_normal']};
            color: {theme['foreground']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 6px 12px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['button_pressed']};
        }}
        
        /* Поля ввода */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {theme['input_background']};
            color: {theme['input_text']};
            border: 1px solid {theme['input_border']};
            border-radius: 4px;
            padding: 4px;
        }}
        
        /* Вкладки */
        QTabWidget::pane {{
            border: 1px solid {theme['border']};
        }}
        
        QTabBar::tab {{
            background-color: {theme['tab_inactive']};
            color: {theme['foreground']};
            padding: 6px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme['tab_active']};
        }}
        
        /* Полосы прокрутки */
        QScrollBar:vertical {{
            background-color: {theme['background']};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['secondary']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['accent']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme['background']};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme['secondary']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['accent']};
        }}
        
        /* Списки и таблицы */
        QListView, QTreeView, QTableView {{
            background-color: {theme['input_background']};
            color: {theme['foreground']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent']};
            selection-color: {theme['foreground']};
        }}
        
        QHeaderView::section {{
            background-color: {theme['secondary']};
            color: {theme['foreground']};
            padding: 4px;
            border: 1px solid {theme['border']};
        }}
        
        /* Меню */
        QMenuBar {{
            background-color: {theme['background']};
            color: {theme['foreground']};
            border-bottom: 1px solid {theme['border']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {theme['accent']};
        }}
        
        QMenu {{
            background-color: {theme['background']};
            color: {theme['foreground']};
            border: 1px solid {theme['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {theme['accent']};
        }}
        """

# Пример использования:
# from theme_manager import ThemeManager
# app = QApplication([])
# theme_manager = ThemeManager.instance(app)
# theme_manager.set_theme('dark')  # или 'light'
