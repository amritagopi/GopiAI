"""
Тестовое приложение для проверки работы LucideIconManager.

Запуск:
    python test_lucide_icons.py
"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Импортируем наш менеджер иконок
from app.ui.lucide_icon_manager import LucideIconManager


class LucideIconBrowser(QMainWindow):
    """Браузер иконок Lucide для тестирования."""

    def __init__(self):
        super().__init__()
        self.icon_manager = LucideIconManager.instance()
        self.initUI()

    def initUI(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Lucide Icon Browser")
        self.setMinimumSize(800, 600)

        # Центральный виджет и основной макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Верхняя панель с элементами управления
        controls_layout = QHBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск иконок...")
        self.search_input.textChanged.connect(self.filter_icons)
        controls_layout.addWidget(self.search_input)

        # Выбор размера
        size_label = QLabel("Размер:")
        controls_layout.addWidget(size_label)

        self.size_combo = QComboBox()
        for size in [16, 24, 32, 48]:
            self.size_combo.addItem(f"{size}x{size}", size)
        self.size_combo.setCurrentIndex(1)  # 24x24 по умолчанию
        self.size_combo.currentIndexChanged.connect(self.update_icon_display)
        controls_layout.addWidget(self.size_combo)

        # Выбор цвета
        self.color_button = QPushButton("Цвет")
        self.color_button.clicked.connect(self.choose_color)
        self.current_color = None
        controls_layout.addWidget(self.color_button)

        # Сброс цвета
        self.reset_color_button = QPushButton("Сброс цвета")
        self.reset_color_button.clicked.connect(self.reset_color)
        controls_layout.addWidget(self.reset_color_button)

        main_layout.addLayout(controls_layout)

        # Область прокрутки для иконок
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Контейнер для иконок
        icon_container = QWidget()
        self.icons_layout = QGridLayout(icon_container)
        self.icons_layout.setSpacing(10)

        scroll_area.setWidget(icon_container)
        main_layout.addWidget(scroll_area)

        # Статусная строка
        self.statusBar().showMessage("Готово")

        # Заполняем иконки
        self.populate_icons()

    def populate_icons(self):
        """Заполняет сетку иконками."""
        # Очищаем текущий макет
        while self.icons_layout.count():
            item = self.icons_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Получаем все иконки
        all_icons = self.icon_manager.list_available_icons()

        # Фильтруем, если есть поисковый запрос
        search_text = self.search_input.text().lower()
        if search_text:
            all_icons = [name for name in all_icons if search_text in name.lower()]

        # Отображаем информацию о количестве иконок
        self.statusBar().showMessage(f"Найдено иконок: {len(all_icons)}")

        # Максимум 5 столбцов
        columns = 5

        # Текущий размер
        size = self.size_combo.currentData()

        # Перебираем иконки и добавляем их в сетку
        for i, icon_name in enumerate(sorted(all_icons)):
            row = i // columns
            col = i % columns

            # Создаем виджет для иконки
            icon_widget = QWidget()
            icon_layout = QVBoxLayout(icon_widget)
            icon_layout.setAlignment(Qt.AlignCenter)

            # Получаем иконку
            icon = self.icon_manager.get_icon(
                icon_name, self.current_color, QSize(size, size)
            )

            # Создаем метку для иконки
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(QSize(size, size)))
            icon_label.setAlignment(Qt.AlignCenter)

            # Создаем метку для имени иконки
            name_label = QLabel(icon_name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)

            # Добавляем в макет
            icon_layout.addWidget(icon_label)
            icon_layout.addWidget(name_label)

            # Добавляем в сетку
            self.icons_layout.addWidget(icon_widget, row, col)

    def filter_icons(self):
        """Фильтрует иконки по поисковому запросу."""
        self.populate_icons()

    def update_icon_display(self):
        """Обновляет отображение иконок при изменении размера."""
        self.populate_icons()

    def choose_color(self):
        """Открывает диалог выбора цвета."""
        color = QColorDialog.getColor(
            (
                QColor(0, 120, 215)
                if not self.current_color
                else QColor(self.current_color)
            ),
            self,
            "Выберите цвет иконок",
        )

        if color.isValid():
            self.current_color = color.name()
            self.color_button.setText(f"Цвет: {self.current_color}")
            self.populate_icons()

    def reset_color(self):
        """Сбрасывает цвет иконок."""
        self.current_color = None
        self.color_button.setText("Цвет")
        self.populate_icons()


if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Устанавливаем темную тему, если она поддерживается
    try:
        # Попробуем установить темную палитру
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(dark_palette)
    except Exception as e:
        print(f"Не удалось установить темную тему: {e}")

    # Создаем и показываем главное окно
    main_window = LucideIconBrowser()
    main_window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())
