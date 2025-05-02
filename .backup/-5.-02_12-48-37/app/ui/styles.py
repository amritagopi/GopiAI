import os
import sys
from pathlib import Path
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import QFile, QTextStream, QUrl


def load_styles(app):
    """
    Загружает только шрифты для приложения.
    Стили теперь загружаются через MainWindow._load_styles().

    Args:
        app: Экземпляр QApplication
    """
    # Получаем базовую директорию проекта
    base_dir = Path(__file__).resolve().parent.parent.parent

    # Больше не загружаем стили здесь, так как это делается в MainWindow._load_styles()
    # в зависимости от текущей темы (светлая/темная)
    print("Стили будут загружены через MainWindow._load_styles()")

    # Создаем путь к директории шрифтов
    fonts_dir = base_dir / "assets" / "fonts"
    print(f"Директория шрифтов: {fonts_dir}")

    # Загружаем CSS с шрифтами из Google Fonts
    font_css_path = fonts_dir / "fonts.css"
    if os.path.exists(font_css_path):
        try:
            print(f"Загружаем CSS шрифтов из {font_css_path}")
            with open(font_css_path, 'r', encoding='utf-8') as f:
                font_css = f.read()
                # Добавляем CSS импорт в общие стили приложения
                app.setStyleSheet(app.styleSheet() + "\n" + font_css)
        except Exception as e:
            print(f"ОШИБКА: Не удалось загрузить CSS шрифтов: {e}")
    else:
        print(f"ВНИМАНИЕ: Файл CSS шрифтов не найден по пути {font_css_path}")

    # Также регистрируем любые локальные шрифты
    register_local_fonts(fonts_dir)


def register_local_fonts(fonts_dir):
    """
    Регистрирует все TTF и OTF шрифты из указанной директории

    Args:
        fonts_dir: Путь к директории со шрифтами
    """
    if not os.path.exists(fonts_dir):
        print(f"ВНИМАНИЕ: Директория шрифтов не найдена по пути {fonts_dir}")
        return

    # Рекурсивно ищем все шрифты в директории
    font_count = 0
    for root, _, files in os.walk(fonts_dir):
        for file in files:
            if file.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(root, file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_count += 1
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"Загружен шрифт: {font_path} -> {', '.join(font_families)}")
                else:
                    print(f"ОШИБКА: Не удалось загрузить шрифт {font_path}")

    if font_count > 0:
        print(f"Успешно загружено {font_count} файлов шрифтов из {fonts_dir}")
    else:
        print(f"Не найдено файлов шрифтов в {fonts_dir}")
