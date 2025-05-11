#!/usr/bin/env python
"""
Тестовый модуль для проверки корректности работы тематических иконок.
Проверяет наличие всех иконок в манифесте и их правильное отображение
в различных темах.
"""

import os
import sys
import json
import re
from PySide6.QtGui import QIcon, QColor, QPainter, QPixmap, QImage
from PySide6.QtCore import QSize, Qt, QByteArray
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout, QScrollArea

# Добавляем путь к родительской директории в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from app.ui.icon_manager import IconManager, get_icon, get_themed_icon
from app.utils.theme_manager import ThemeManager
from app.ui.i18n.translator import tr, APP_NAME

class IconTestWindow(QMainWindow):
    """Тестовое окно для отображения иконок в различных темах."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("icon_test.title", "Тест иконок {app_name}").format(app_name=APP_NAME))
        self.setMinimumSize(800, 600)

        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Создаем область прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        # Содержимое области прокрутки
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)
        self.grid_layout = QGridLayout(self.scroll_content)

        # Загружаем иконки
        self.load_icons()

    def load_icons(self):
        """Загружает все доступные иконки и отображает их."""
        icon_manager = IconManager.instance()
        available_icons = icon_manager.list_available_icons()

        # Добавляем заголовки
        self.grid_layout.addWidget(QLabel("<b>Имя иконки</b>"), 0, 0)
        self.grid_layout.addWidget(QLabel("<b>Стандартная иконка</b>"), 0, 1)
        self.grid_layout.addWidget(QLabel("<b>Тематическая иконка</b>"), 0, 2)
        self.grid_layout.addWidget(QLabel("<b>Тип файла</b>"), 0, 3)

        row = 1
        for icon_name in sorted(available_icons):
            # Имя иконки
            self.grid_layout.addWidget(QLabel(icon_name), row, 0)

            # Стандартная иконка
            standard_icon = get_icon(icon_name)
            if not standard_icon.isNull():
                icon_label = QLabel()
                icon_label.setPixmap(standard_icon.pixmap(QSize(32, 32)))
                self.grid_layout.addWidget(icon_label, row, 1)
            else:
                self.grid_layout.addWidget(QLabel("Ошибка"), row, 1)

            # Тематическая иконка
            themed_icon = get_themed_icon(icon_name)
            if not themed_icon.isNull():
                icon_label = QLabel()
                icon_label.setPixmap(themed_icon.pixmap(QSize(32, 32)))
                self.grid_layout.addWidget(icon_label, row, 2)
            else:
                self.grid_layout.addWidget(QLabel("Ошибка"), row, 2)

            # Тип файла (SVG или другой)
            file_type = "SVG" if icon_name in icon_manager.manifest and icon_manager.manifest[icon_name].endswith('.svg') else "Другой"
            self.grid_layout.addWidget(QLabel(file_type), row, 3)

            row += 1

def check_icon_colors():
    """Проверяет, что в SVG-файлах не используются жестко закодированные цвета."""
    icon_folder = os.path.join(project_root, "assets", "icons")
    manifest_path = os.path.join(icon_folder, "manifest.json")

    if not os.path.exists(manifest_path):
        print("Манифест иконок не найден!")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    icons = manifest.get("icons", {})
    hardcoded_colors = set()
    svg_files_with_hardcoded_colors = []

    for icon_name, file_name in icons.items():
        if not file_name.endswith('.svg'):
            continue

        svg_path = os.path.join(icon_folder, file_name)
        if not os.path.exists(svg_path):
            print(f"Файл иконки не найден: {svg_path}")
            continue

        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Ищем жестко закодированные цвета (hex)
        hex_colors = set(re.findall(r'#[0-9a-fA-F]{3,6}', svg_content))
        if hex_colors - {IconManager.ICON_BASE_COLOR}:  # Исключаем базовый цвет, он будет заменен
            svg_files_with_hardcoded_colors.append((file_name, hex_colors - {IconManager.ICON_BASE_COLOR}))
            hardcoded_colors.update(hex_colors - {IconManager.ICON_BASE_COLOR})

    if svg_files_with_hardcoded_colors:
        print(f"Найдено {len(svg_files_with_hardcoded_colors)} SVG-файлов с жестко закодированными цветами:")
        for file_name, colors in svg_files_with_hardcoded_colors:
            print(f"  {file_name}: {', '.join(colors)}")
        print(f"Всего уникальных цветов: {len(hardcoded_colors)}")
        print(f"Рекомендуется заменить все жестко закодированные цвета на {IconManager.ICON_BASE_COLOR}")
    else:
        print("Все SVG-файлы используют правильный базовый цвет.")

def main():
    """Запускает тестовое приложение."""
    app = QApplication(sys.argv)

    # Инициализируем менеджеры
    theme_manager = ThemeManager.instance(app)
    icon_manager = IconManager.instance()

    # Проверяем цвета в SVG
    check_icon_colors()

    # Создаем и показываем окно
    window = IconTestWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    main()
