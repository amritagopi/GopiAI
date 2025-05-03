"""
Модуль для загрузки и управления стилями и шрифтами приложения.
"""
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import QDir, QFile

# Импортируем менеджер тем
from app.ui.theme_manager import theme_manager

def load_fonts():
    """
    Загружает шрифты приложения.

    Returns:
        bool: True если загрузка успешна, False в противном случае.
    """
    try:
        # Определяем корневую директорию проекта
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_dir = os.path.join(root_dir, "assets", "fonts")

        # Проверяем и создаем директорию, если её нет
        if not os.path.exists(font_dir):
            os.makedirs(font_dir, exist_ok=True)
            print(f"Created fonts directory: {font_dir}")

        # Ищем шрифты Inter
        inter_dirs = [
            os.path.join(font_dir, "Inter"),
            font_dir
        ]

        # Пытаемся загрузить различные варианты шрифта Inter
        fonts_loaded = 0
        for inter_dir in inter_dirs:
            if os.path.exists(inter_dir):
                for font_file in os.listdir(inter_dir):
                    if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                        font_path = os.path.join(inter_dir, font_file)
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            fonts_loaded += 1
                            print(f"Loaded font: {font_file}")

        # Ищем моноширинные шрифты в директории шрифтов
        mono_font_files = [
            "JetBrainsMono-Regular.ttf",
            "FiraCode-Regular.ttf",
            "SourceCodePro-Regular.ttf"
        ]

        for mono_font in mono_font_files:
            font_path = os.path.join(font_dir, mono_font)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    fonts_loaded += 1
                    print(f"Loaded monospace font: {mono_font}")

        print(f"Total fonts loaded: {fonts_loaded}")
        return fonts_loaded > 0

    except Exception as e:
        print(f"Error loading fonts: {str(e)}")
        return False

def apply_default_font(app, use_system_fallback=True):
    """
    Применяет шрифты по умолчанию к приложению.

    Args:
        app (QApplication): Экземпляр приложения.
        use_system_fallback (bool): Использовать системные шрифты, если наши не доступны.

    Returns:
        bool: True если шрифты успешно применены, False в противном случае.
    """
    try:
        # Пытаемся установить шрифт Inter для всего приложения
        default_font = QFont("Inter", 10)
        app.setFont(default_font)

        # Если шрифт не может быть правильно установлен, используем системный
        if use_system_fallback and not QFontDatabase.hasFamily("Inter"):
            if sys.platform == "darwin":  # macOS
                app.setFont(QFont("SF Pro", 10))
            elif sys.platform == "win32":  # Windows
                app.setFont(QFont("Segoe UI", 10))
            else:  # Linux/Unix
                app.setFont(QFont("Noto Sans", 10))
            print("Using system fonts as fallback")

        print("Font applied to application")
        return True

    except Exception as e:
        print(f"Error applying default font: {str(e)}")
        return False

def load_qss_file(file_path):
    """
    Загружает QSS файл и возвращает его содержимое.

    Args:
        file_path (str): Путь к QSS файлу.

    Returns:
        str: Содержимое QSS файла или пустую строку, если файл не найден.
    """
    if not os.path.exists(file_path):
        print(f"QSS file not found: {file_path}")
        return ""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading QSS file {file_path}: {str(e)}")
        return ""

def update_styles(app):
    """
    Обновляет стили приложения в соответствии с текущей темой.

    Args:
        app (QApplication): Экземпляр приложения.

    Returns:
        bool: True если стили успешно применены, False в противном случае.
    """
    try:
        # Получаем путь к файлу темы
        style_path = theme_manager.get_theme_qss_path()

        if not style_path:
            print("Theme path not found")
            return False

        print(f"Loading styles from: {style_path}")

        # Загружаем стили из файла темы
        style_content = load_qss_file(style_path)
        if not style_content:
            return False

        # Применяем стили к приложению
        app.setStyleSheet(style_content)
        print("Styles applied to application")
        return True

    except Exception as e:
        print(f"Error updating styles: {str(e)}")
        return False

def load_styles(app):
    """
    Загружает стили и шрифты для приложения.

    Args:
        app (QApplication): Экземпляр приложения.

    Returns:
        bool: True если стили и шрифты успешно загружены, False в противном случае.
    """
    # Загружаем шрифты
    fonts_loaded = load_fonts()

    # Применяем шрифт по умолчанию
    apply_default_font(app, use_system_fallback=True)

    # Загружаем стили
    styles_loaded = update_styles(app)

    return fonts_loaded or styles_loaded
