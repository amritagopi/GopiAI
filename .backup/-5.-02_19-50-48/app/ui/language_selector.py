from PySide6.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, QEvent

from app.ui.i18n import JsonTranslationManager


class LanguageSelector(QWidget):
    """Виджет для выбора языка приложения"""

    language_changed = Signal(str)  # Сигнал, который отправляется при изменении языка

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        self.label = QLabel(self.tr("Выберите язык:"))
        layout.addWidget(self.label)

        # Горизонтальный контейнер для комбобокса и кнопки
        h_layout = QHBoxLayout()

        # Комбобокс со списком языков
        self.language_combo = QComboBox()
        self.populate_languages()
        h_layout.addWidget(self.language_combo)

        # Кнопка применения
        self.apply_button = QPushButton(self.tr("Применить"))
        self.apply_button.clicked.connect(self.on_apply_clicked)
        h_layout.addWidget(self.apply_button)

        layout.addLayout(h_layout)
        self.setLayout(layout)

    def populate_languages(self):
        """Заполняет комбобокс доступными языками"""
        self.language_combo.clear()

        # Получаем список доступных языков
        languages = JsonTranslationManager.instance().get_available_languages()

        # Добавляем языки в комбобокс
        for lang_code in languages:
            lang_name = JsonTranslationManager.instance().get_language_name(lang_code)
            self.language_combo.addItem(lang_name, lang_code)

        # Устанавливаем текущий язык
        current_lang = JsonTranslationManager.instance().get_current_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

    def on_apply_clicked(self):
        """Обработчик нажатия на кнопку применения"""
        selected_index = self.language_combo.currentIndex()
        if selected_index >= 0:
            lang_code = self.language_combo.itemData(selected_index)
            if JsonTranslationManager.instance().switch_language(lang_code):
                self.language_changed.emit(lang_code)

    def changeEvent(self, event):
        """Обработчик события изменения языка"""
        if event.type() == QEvent.LanguageChange:
            # Обновляем тексты в интерфейсе при изменении языка
            self.label.setText(self.tr("Выберите язык:"))
            self.apply_button.setText(self.tr("Применить"))

        super().changeEvent(event)
