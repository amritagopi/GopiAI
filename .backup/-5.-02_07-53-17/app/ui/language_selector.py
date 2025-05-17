from PySide6.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, QEvent

from app.ui.i18n.translator import JsonTranslationManager, tr
import logging

logger = logging.getLogger(__name__)

class LanguageSelector(QWidget):
    """Виджет для выбора языка приложения"""

    language_changed = Signal(str)  # Сигнал, который отправляется при изменении языка

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

        # Подключаемся к сигналу смены языка от TranslationManager
        self.translation_manager = JsonTranslationManager.instance()
        self.translation_manager.languageChanged.connect(self.on_language_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        self.label = QLabel(tr("language_selector.title", "Выберите язык:"))
        layout.addWidget(self.label)

        # Горизонтальный контейнер для комбобокса и кнопки
        h_layout = QHBoxLayout()

        # Комбобокс со списком языков
        self.language_combo = QComboBox()
        self.populate_languages()
        h_layout.addWidget(self.language_combo)

        # Кнопка применения
        self.apply_button = QPushButton(tr("language_selector.apply", "Применить"))
        self.apply_button.clicked.connect(self.on_apply_clicked)
        h_layout.addWidget(self.apply_button)

        layout.addLayout(h_layout)
        self.setLayout(layout)

    def populate_languages(self):
        """Заполняет комбобокс доступными языками"""
        self.language_combo.clear()

        # Получаем список доступных языков
        languages = self.translation_manager.get_available_languages()

        # Добавляем языки в комбобокс
        for lang_code in languages:
            lang_name = self.translation_manager.get_language_name(lang_code)
            self.language_combo.addItem(lang_name, lang_code)

        # Устанавливаем текущий язык
        current_lang = self.translation_manager.get_current_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

    def on_apply_clicked(self):
        """Обработчик нажатия на кнопку применения"""
        selected_index = self.language_combo.currentIndex()
        if selected_index >= 0:
            lang_code = self.language_combo.itemData(selected_index)
            logger.info(f"Выбран язык: {lang_code}")
            if self.translation_manager.switch_language(lang_code):
                # Сигнал languageChanged будет отправлен из JsonTranslationManager
                logger.info(f"Язык успешно переключен на {lang_code}")
            else:
                logger.error(f"Не удалось переключить язык на {lang_code}")

    def on_language_changed(self, language_code):
        """Обработчик сигнала languageChanged от JsonTranslationManager"""
        logger.info(f"Получен сигнал languageChanged: {language_code}")
        # Обновляем UI в соответствии с новым языком
        self.label.setText(tr("language_selector.title", "Выберите язык:"))
        self.apply_button.setText(tr("language_selector.apply", "Применить"))

        # Обновляем выделенный язык в комбобоксе
        index = self.language_combo.findData(language_code)
        if index >= 0 and index != self.language_combo.currentIndex():
            self.language_combo.setCurrentIndex(index)

        # Передаем сигнал дальше (например, для других компонентов UI)
        self.language_changed.emit(language_code)

    def changeEvent(self, event):
        """Обработчик события изменения языка"""
        if event.type() == QEvent.LanguageChange:
            # Обновляем тексты в интерфейсе при изменении языка
            self.label.setText(tr("language_selector.title", "Выберите язык:"))
            self.apply_button.setText(tr("language_selector.apply", "Применить"))

        super().changeEvent(event)
