import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea,
                             QWidget, QPushButton, QLabel, QLineEdit, QGridLayout)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from .icon_manager import get_icon
from .i18n.translator import tr

class EmojiButton(QPushButton):
    """Кнопка с эмодзи."""
    def __init__(self, emoji, parent=None):
        super().__init__(emoji, parent)
        self.setFont(QFont("Segoe UI Emoji", 16))
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(emoji)

class EmojiDialog(QDialog):
    """Диалог выбора эмодзи."""
    emoji_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("emoji_dialog.title", "Select Emoji"))
        self.setMinimumSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Категории эмодзи
        self.emoji_categories = {
            "Смайлы": [
                "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "☺️", "😊",
                "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙",
                "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎"
            ],
            "Люди": [
                "👶", "👧", "🧒", "👦", "👩", "🧑", "👨", "👵", "🧓", "👴",
                "👮", "🕵️", "💂", "👷", "🤴", "👸", "👳", "👲", "🧕", "🤵",
                "👰", "🤰", "🤱", "👼", "🎅", "🤶", "🦸", "🦹", "🧙", "🧚"
            ],
            "Животные": [
                "🐵", "🐒", "🦍", "🦧", "🐶", "🐕", "🦮", "🐩", "🐺", "🦊",
                "🦝", "🐱", "🐈", "🦁", "🐯", "🐅", "🐆", "🐴", "🐎", "🦄",
                "🦓", "🦌", "🐮", "🐂", "🐃", "🐄", "🐷", "🐖", "🐗", "🐽"
            ],
            "Еда": [
                "🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🍈",
                "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🥦",
                "🥬", "🥒", "🌶", "🌽", "🥕", "🧄", "🧅", "🥔", "🍠", "🥐"
            ],
            "Активности": [
                "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
                "🪀", "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "🥅", "⛳", "🪁",
                "🏹", "🎣", "🤿", "🥊", "🥋", "🎽", "🛹", "🛼", "🛷", "⛸"
            ],
            "Предметы": [
                "⌚", "📱", "📲", "💻", "⌨️", "🖥", "🖨", "🖱", "🖲", "🕹",
                "🗜", "💽", "💾", "💿", "📀", "📼", "📷", "📸", "📹", "🎥",
                "📽", "🎞", "📞", "☎️", "📟", "📠", "📺", "📻", "🎙", "🎚"
            ],
            "Символы": [
                "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
                "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️",
                "✝️", "☪️", "🕉", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐"
            ],
            "Флаги": [
                "🏁", "🚩", "🎌", "🏴", "🏳️", "🏳️‍🌈", "🏳️‍⚧️", "🏴‍☠️", "🇦🇫", "🇦🇽",
                "🇦🇱", "🇩🇿", "🇦🇸", "🇦🇩", "🇦🇴", "🇦🇮", "🇦🇶", "🇦🇬", "🇦🇷", "🇦🇲",
                "🇦🇼", "🇦🇺", "🇦🇹", "🇦🇿", "🇧🇸", "🇧🇭", "🇧🇩", "🇧🇧", "🇧🇾", "🇧🇪"
            ]
        }

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалога."""
        main_layout = QVBoxLayout(self)

        # Строка поиска
        search_layout = QHBoxLayout()
        search_label = QLabel(tr("emoji_dialog.search", "Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("emoji_dialog.search_placeholder", "Enter emoji or category..."))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setToolTip(tr("emoji_dialog.search_tooltip", "Поиск по эмодзи и категориям"))
        self.search_input.textChanged.connect(self.search_emoji)
        search_icon = QPushButton(get_icon("search"))
        search_icon.setToolTip(tr("emoji_dialog.search_btn_tooltip", "Начать поиск"))
        search_icon.setFixedSize(28, 28)
        search_icon.setFocusPolicy(Qt.NoFocus)
        search_icon.setEnabled(False)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_icon)
        main_layout.addLayout(search_layout)

        # Вкладки категорий эмодзи
        self.tabs = QTabWidget()

        # Добавление вкладок для каждой категории
        for category, emojis in self.emoji_categories.items():
            tab = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()

            grid_layout = QGridLayout(scroll_content)
            grid_layout.setSpacing(4)

            # Расположение эмодзи в сетке
            row, col = 0, 0
            max_cols = 8  # Максимум 8 эмодзи в строке

            for emoji in emojis:
                button = EmojiButton(emoji)
                button.clicked.connect(lambda checked=False, e=emoji: self.on_emoji_clicked(e))
                grid_layout.addWidget(button, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            scroll_area.setWidget(scroll_content)
            tab_layout = QVBoxLayout(tab)
            tab_layout.addWidget(scroll_area)

            # Иконка категории, если есть
            icon = get_icon(category.lower()) if get_icon(category.lower()) else None
            tab_name = tr(f"emoji_dialog.category.{category.lower()}", category)
            self.tabs.addTab(tab, icon if icon else None, tab_name)
            idx = self.tabs.indexOf(tab)
            self.tabs.setTabToolTip(idx, tab_name)

        main_layout.addWidget(self.tabs)

        # Кнопки внизу диалога
        buttons_layout = QHBoxLayout()
        close_button = QPushButton(get_icon("close"), tr("dialogs.close", "Close"))
        close_button.setToolTip(tr("dialogs.close_tooltip", "Close emoji selection dialog"))
        close_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        main_layout.addLayout(buttons_layout)

    def on_emoji_clicked(self, emoji):
        """Обработчик нажатия на эмодзи."""
        self.emoji_selected.emit(emoji)
        self.accept()

    def search_emoji(self, text):
        """Поиск эмодзи (заглушка)."""
        # В реальном приложении здесь можно добавить логику поиска
        # и отображения найденных эмодзи
        pass

# Для тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = EmojiDialog()
    if dialog.exec() == QDialog.Accepted:
        print("Selected emoji:", dialog.selected_emoji)
    sys.exit(app.exec())
