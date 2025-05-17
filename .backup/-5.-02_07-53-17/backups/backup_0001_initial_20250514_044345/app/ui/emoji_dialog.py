import json
import logging
import os
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .i18n.translator import tr
from .lucide_icon_manager import get_lucide_icon

logger = logging.getLogger(__name__)


class EmojiButton(QPushButton):
    """Кнопка с эмодзи."""

    def __init__(self, emoji, parent=None, emoji_font=None):
        super().__init__(emoji, parent)

        # Устанавливаем шрифт с поддержкой эмодзи, если передан
        if emoji_font:
            font = QFont(emoji_font, 12)  # Уменьшен размер шрифта с 14 до 12
        else:
            # Используем системный шрифт с поддержкой эмодзи
            font = QFont("Segoe UI Emoji", 12)  # Уменьшен размер шрифта с 14 до 12

        self.setFont(font)
        self.setFixedSize(24, 24)  # Уменьшен размер кнопки с 34x34 до 24x24
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(emoji)

        # Изменение стиля кнопки на квадратный
        self.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #cccccc;
                border-radius: 0px;
                background-color: #f8f8f8;
                margin: 1px;
                padding: 0px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #aaaaaa;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #888888;
            }
            """
        )


class EmojiDialog(QDialog):
    """Диалог выбора эмодзи."""

    emoji_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("emoji_dialog.title", "Select Emoji"))
        self.setFixedSize(225, 225)  # Фиксированный квадратный размер 225x225
        # Устанавливаем флаги: убираем кнопку помощи и добавляем WindowStaysOnTopHint
        self.setWindowFlags(
            (self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            | Qt.WindowStaysOnTopHint
        )

        # Находим путь к данным эмодзи
        self.emoji_data_path = self._get_emoji_data_path()

        # Загружаем категории эмодзи из JSON файла
        self.emoji_categories = {}
        self.emoji_fonts = []
        self.load_emoji_data()

        # Находим доступный шрифт эмодзи
        self.emoji_font = self._find_available_emoji_font()
        logger.info(f"Используем шрифт для эмодзи: {self.emoji_font}")

        self.setup_ui()

        # Устанавливаем фокус на поле поиска для быстрого поиска эмодзи
        if hasattr(self, "search_input"):
            self.search_input.setFocus()

    def _get_emoji_data_path(self):
        """Получает путь к файлу данных эмодзи."""
        # Относительный путь от текущего файла
        app_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        emoji_data_path = app_dir / "assets" / "emoji" / "emoji_data.json"

        if not emoji_data_path.exists():
            logger.warning(
                f"Файл с данными эмодзи не найден по пути: {emoji_data_path}"
            )

        return emoji_data_path

    def load_emoji_data(self):
        """Загружает данные эмодзи из JSON файла."""
        try:
            if self.emoji_data_path.exists():
                with open(self.emoji_data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.emoji_categories = data.get("categories", {})
                    self.emoji_fonts = data.get("fonts", [])
                logger.info(
                    f"Загружено {len(self.emoji_categories)} категорий эмодзи и {len(self.emoji_fonts)} шрифтов"
                )
            else:
                # Если файл не найден, используем встроенные данные
                logger.warning("Используем встроенные данные эмодзи (без JSON файла)")
                self.emoji_categories = {
                    "Смайлы": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣"],
                    "Люди": ["👶", "👧", "🧒", "👦", "👩", "🧑", "👨"],
                    "Животные": ["🐵", "🐒", "🦍", "🦧", "🐶", "🐕"],
                    "Символы": ["❤️", "🧡", "💛", "💚", "💙", "💜"],
                }
                self.emoji_fonts = [
                    "Segoe UI Emoji",
                    "Segoe UI Symbol",
                    "Arial Unicode MS",
                ]
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных эмодзи: {e}")
            # Установка значений по умолчанию
            self.emoji_categories = {
                "Смайлы": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣"],
                "Люди": ["👶", "👧", "🧒", "👦", "👩", "🧑", "👨"],
                "Животные": ["🐵", "🐒", "🦍", "🦧", "🐶", "🐕"],
                "Символы": ["❤️", "🧡", "💛", "💚", "💙", "💜"],
            }
            self.emoji_fonts = ["Segoe UI Emoji", "Segoe UI Symbol", "Arial Unicode MS"]

    def _find_available_emoji_font(self):
        """Находит доступный шрифт с поддержкой эмодзи."""
        available_fonts = QFontDatabase().families()
        logger.debug(f"Доступные шрифты: {available_fonts[:10]}...")

        # Проверяем наличие шрифтов из нашего списка
        for font in self.emoji_fonts:
            if any(f == font or f.startswith(font) for f in available_fonts):
                logger.info(f"Найден подходящий шрифт: {font}")
                return font

        # Если ничего не нашли, попробуем другие популярные шрифты с эмодзи
        fallback_fonts = ["Segoe UI", "Arial", "Times New Roman"]
        for font in fallback_fonts:
            if any(f == font or f.startswith(font) for f in available_fonts):
                logger.info(f"Используем запасной шрифт: {font}")
                return font

        # Если не найдено подходящих шрифтов, используем системный шрифт по умолчанию
        logger.warning("Не найдены шрифты с поддержкой эмодзи, используем системный")
        return ""

    def setup_ui(self):
        """Настройка интерфейса диалога."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(4)  # Уменьшен интервал между элементами до 4
        main_layout.setContentsMargins(4, 4, 4, 4)  # Уменьшены отступы до 4

        # Строка поиска
        search_layout = QHBoxLayout()
        search_layout.setSpacing(2)  # Уменьшен интервал между элементами поиска до 2
        search_label = QLabel(tr("emoji_dialog.search", "Search:"))
        search_label.setFixedWidth(40)  # Фиксированная ширина для экономии места
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            tr("emoji_dialog.search_placeholder", "Enter emoji or category...")
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setToolTip(
            tr("emoji_dialog.search_tooltip", "Поиск по эмодзи и категориям")
        )
        self.search_input.textChanged.connect(self.search_emoji)
        search_icon = QPushButton()
        search_icon.setIcon(get_lucide_icon("search"))
        search_icon.setToolTip(tr("emoji_dialog.search_btn_tooltip", "Начать поиск"))
        search_icon.setFixedSize(20, 20)  # Уменьшен размер иконки поиска до 20x20
        search_icon.setFocusPolicy(Qt.NoFocus)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_icon)
        main_layout.addLayout(search_layout)

        # Вкладки категорий эмодзи
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 3px 6px;
                margin-right: 1px;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background: #fff;
                border-bottom: 1px solid #fff;
            }
            QTabBar::tab:hover {
                background: #e0e0e0;
            }
        """
        )

        # Добавление вкладок для каждой категории
        for category, emojis in self.emoji_categories.items():
            tab = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet(
                """
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 6px;
                    border-radius: 3px;
                }
                QScrollBar::handle:vertical {
                    background: #ccc;
                    border-radius: 3px;
                }
            """
            )
            scroll_content = QWidget()

            grid_layout = QGridLayout(scroll_content)
            grid_layout.setSpacing(1)  # Уменьшен интервал между кнопками эмодзи до 1
            grid_layout.setContentsMargins(1, 1, 1, 1)  # Минимальные отступы сетки

            # Расположение эмодзи в сетке
            row, col = 0, 0
            max_cols = 12  # Увеличено максимальное количество эмодзи в строке до 12

            for emoji in emojis:
                button = EmojiButton(emoji, emoji_font=self.emoji_font)
                button.clicked.connect(
                    lambda checked=False, e=emoji: self.on_emoji_clicked(e)
                )
                grid_layout.addWidget(button, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            scroll_area.setWidget(scroll_content)
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.addWidget(scroll_area)

            # Получаем иконку категории и отображаемое имя
            icon = (
                get_lucide_icon(category.lower())
                if category.lower() in ["smile", "users", "activity", "heart"]
                else None
            )
            tab_name = tr(f"emoji_dialog.category.{category.lower()}", category)

            if icon:
                self.tabs.addTab(tab, icon, tab_name)
            else:
                # Создаем иконку на основе первого эмодзи категории
                self.tabs.addTab(
                    tab,
                    self._create_emoji_icon(emojis[0] if emojis else "😀"),
                    tab_name,
                )

            idx = self.tabs.indexOf(tab)
            self.tabs.setTabToolTip(idx, tab_name)

        main_layout.addWidget(self.tabs)

        # Кнопки внизу диалога
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(2)  # Уменьшен интервал между кнопками до 2
        close_button = QPushButton(get_lucide_icon("x"), tr("dialogs.close", "Close"))
        close_button.setToolTip(
            tr("dialogs.close_tooltip", "Close emoji selection dialog")
        )
        close_button.setFixedHeight(20)  # Уменьшенная высота кнопки до 20
        close_button.setStyleSheet(
            "font-size: 10px;"
        )  # Меньший шрифт для экономии места
        # Подключаем обработчик для закрытия диалога
        close_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        main_layout.addLayout(buttons_layout)

    def _create_emoji_icon(self, emoji):
        """Создает иконку для вкладки на основе эмодзи."""
        # Создаем пиксмап
        pixmap = QPixmap(16, 16)  # Уменьшен размер иконки с 24x24 до 16x16
        pixmap.fill(Qt.transparent)

        # Рисуем эмодзи на пиксмапе
        painter = QPainter(pixmap)
        font = QFont(self.emoji_font, 10)  # Уменьшен шрифт с 14 до 10
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    def on_emoji_clicked(self, emoji):
        """Обработчик нажатия на эмодзи."""
        logger.debug(f"Выбран эмодзи: {emoji}")
        self.emoji_selected.emit(emoji)
        self.accept()  # Закрываем диалог с результатом Accepted

    def search_emoji(self, text):
        """Поиск эмодзи по тексту."""
        found = False

        if not text:
            # Если поле поиска пустое, показываем все категории и эмодзи
            for cat_idx in range(self.tabs.count()):
                self.tabs.setTabVisible(cat_idx, True)
                tab = self.tabs.widget(cat_idx)
                scroll_area = self._find_scroll_area(tab)
                if scroll_area and scroll_area.widget():
                    grid_layout = scroll_area.widget().layout()
                    for i in range(grid_layout.count()):
                        widget = grid_layout.itemAt(i).widget()
                        if widget:
                            widget.setVisible(True)
            return

        text = text.lower()

        # Поиск по всем категориям и эмодзи
        for cat_idx, (category, emojis) in enumerate(self.emoji_categories.items()):
            # Проверяем категорию
            category_name = tr(f"emoji_dialog.category.{category.lower()}", category)
            category_match = text in category_name.lower()

            # Флаг, показывающий, были ли найдены соответствия в этой категории
            category_has_matches = False

            # Получаем виджет вкладки и ищем QScrollArea
            tab = self.tabs.widget(cat_idx)
            scroll_area = self._find_scroll_area(tab)

            if scroll_area and scroll_area.widget():
                grid_layout = scroll_area.widget().layout()

                # Перебираем все эмодзи в категории
                for i in range(grid_layout.count()):
                    widget = grid_layout.itemAt(i).widget()
                    if widget and isinstance(widget, EmojiButton):
                        emoji = widget.text()
                        # Проверяем, содержит ли эмодзи искомый текст
                        emoji_match = text in emoji.lower()

                        # Показываем или скрываем эмодзи
                        widget.setVisible(category_match or emoji_match)

                        if emoji_match:
                            category_has_matches = True
                            found = True

            # Если в категории есть совпадения или название категории совпадает,
            # показываем вкладку, иначе скрываем
            self.tabs.setTabVisible(cat_idx, category_match or category_has_matches)

        # Если ничего не найдено, можно обновить подсказку в строке поиска
        if not found and hasattr(self, "search_input"):
            original_placeholder = tr(
                "emoji_dialog.search_placeholder", "Enter emoji or category..."
            )
            not_found_placeholder = tr(
                "emoji_dialog.search.not_found", "No emoji found"
            )

            # Сохраняем оригинальный текст, если это первый поиск
            if not hasattr(self, "_original_placeholder"):
                self._original_placeholder = self.search_input.placeholderText()

            # Меняем подсказку
            self.search_input.setPlaceholderText(not_found_placeholder)

            # Возвращаем оригинальную подсказку через 2 секунды
            QTimer.singleShot(
                2000,
                lambda: self.search_input.setPlaceholderText(
                    self._original_placeholder
                    if hasattr(self, "_original_placeholder")
                    else original_placeholder
                ),
            )

    def _find_scroll_area(self, tab):
        """Вспомогательный метод для поиска QScrollArea на вкладке."""
        if not tab:
            return None

        # Ищем QScrollArea
        for i in range(tab.layout().count()):
            widget = tab.layout().itemAt(i).widget()
            if isinstance(widget, QScrollArea):
                return widget

        return None

    def showEvent(self, event):
        """Обработчик события показа диалога."""
        super().showEvent(event)

        # Проверяем доступность шрифтов с эмодзи
        if not self.emoji_font:
            logger.warning("Не найден подходящий шрифт с поддержкой эмодзи")
            QMessageBox.warning(
                self,
                tr("emoji_dialog.font_warning_title", "Font Warning"),
                tr(
                    "emoji_dialog.font_warning_text",
                    "No emoji font found. Emojis may not display correctly. "
                    "Consider installing a font with emoji support like 'Segoe UI Emoji' or 'Noto Color Emoji'.",
                ),
            )

    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш."""
        # Обработка нажатия Escape для закрытия диалога
        if event.key() == Qt.Key_Escape:
            logger.info("Escape key pressed, closing emoji dialog")
            self.reject()
            return

        # Обработка нажатия Enter в поле поиска
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.search_input.hasFocus() and hasattr(self, "tabs"):
                # Выбираем первый видимый эмодзи из текущей активной вкладки
                current_tab = self.tabs.currentWidget()
                scroll_area = self._find_scroll_area(current_tab)

                if scroll_area and scroll_area.widget():
                    grid_layout = scroll_area.widget().layout()

                    for i in range(grid_layout.count()):
                        widget = grid_layout.itemAt(i).widget()
                        if (
                            widget
                            and isinstance(widget, EmojiButton)
                            and widget.isVisible()
                        ):
                            # Эмулируем нажатие на первый видимый эмодзи
                            self.on_emoji_clicked(widget.text())
                            return

        # Передаем остальные события базовому классу
        super().keyPressEvent(event)


# Для тестирования
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = EmojiDialog()

    # Для тестирования подключаем сигнал к обработчику
    dialog.emoji_selected.connect(lambda emoji: print(f"Selected emoji: {emoji}"))

    # Для тестирования показываем и ждем результат
    result = dialog.exec()
    print(
        f"Dialog result: {result} ({QDialog.Accepted if result == QDialog.Accepted else QDialog.Rejected})"
    )

    sys.exit(app.exec())
