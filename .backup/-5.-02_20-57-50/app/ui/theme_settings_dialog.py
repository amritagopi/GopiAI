from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QComboBox, QLabel, QColorDialog, QGroupBox,
                              QFormLayout, QDialogButtonBox, QTabWidget, QWidget)
from PySide6.QtCore import Qt, QSettings
from app.utils.theme_manager import ThemeManager
from app.ui.i18n.translator import JsonTranslationManager, tr
import logging

logger = logging.getLogger(__name__)

class ThemeSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("theme_settings_dialog.title", "Настройки темы и языка"))
        self.resize(550, 450)

        # Получаем экземпляр менеджера тем
        self.theme_manager = ThemeManager.instance()

        # Создаем основной макет
        main_layout = QVBoxLayout(self)

        # Создаем вкладки для разделения настроек
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Вкладка выбора темы и языка
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)
        self.tab_widget.addTab(theme_tab, tr("theme_settings_dialog.theme_tab", "Тема и язык"))

        # Группа выбора визуальной темы
        visual_theme_group = QGroupBox(tr("theme_settings_dialog.visual_theme", "Визуальная тема"))
        visual_theme_layout = QHBoxLayout()

        # Создаем комбобокс для выбора визуальных тем
        self.visual_theme_combo = QComboBox()

        # Загружаем список доступных визуальных тем из менеджера тем
        for theme_name in self.theme_manager.get_available_visual_themes():
            display_name = self.theme_manager.get_theme_display_name(theme_name)
            self.visual_theme_combo.addItem(display_name, theme_name)

        # Устанавливаем текущую визуальную тему
        current_theme = self.theme_manager.get_current_visual_theme()
        for i in range(self.visual_theme_combo.count()):
            if self.visual_theme_combo.itemData(i) == current_theme:
                self.visual_theme_combo.setCurrentIndex(i)
                break

        visual_theme_layout.addWidget(QLabel(tr("theme_settings_dialog.visual_theme_label", "Визуальная тема:")))
        visual_theme_layout.addWidget(self.visual_theme_combo)
        visual_theme_group.setLayout(visual_theme_layout)
        theme_layout.addWidget(visual_theme_group)

        # Группа выбора языка
        language_group = QGroupBox(tr("theme_settings_dialog.language", "Язык интерфейса"))
        language_layout = QHBoxLayout()

        # Создаем комбобокс для выбора языка
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en_US")
        self.language_combo.addItem("Русский", "ru_RU")

        # Устанавливаем текущий язык
        current_language = JsonTranslationManager.instance().get_current_language()
        language_index = 0
        if current_language == "ru_RU":
            language_index = 1
        self.language_combo.setCurrentIndex(language_index)

        language_layout.addWidget(QLabel(tr("theme_settings_dialog.language_label", "Язык:")))
        language_layout.addWidget(self.language_combo)
        language_group.setLayout(language_layout)
        theme_layout.addWidget(language_group)

        # Вкладка настройки цветов
        colors_tab = QWidget()
        colors_layout = QVBoxLayout(colors_tab)
        self.tab_widget.addTab(colors_tab, tr("theme_settings_dialog.colors_tab", "Цветовая схема"))

        # Просмотр и редактирование цветов темы
        colors_group = QGroupBox(tr("theme_settings_dialog.theme_colors", "Цвета темы"))
        colors_form_layout = QFormLayout()

        self.color_buttons = {}

        # Получаем цвета из текущей темы
        try:
            # Получаем цвета из ThemeManager
            theme_colors = self.theme_manager.themes[current_theme]

            for color_name, color_value in theme_colors.items():
                button = QPushButton(color_value)
                # Используем светлый или темный текст в зависимости от фона
                text_color = '#000000' if self.is_light_color(color_value) else '#FFFFFF'
                button.setStyleSheet(f"background-color: {color_value}; color: {text_color};")
                button.clicked.connect(lambda checked, name=color_name: self.change_color(name))
                self.color_buttons[color_name] = button
                colors_form_layout.addRow(f"{color_name}:", button)
        except Exception as e:
            colors_form_layout.addRow(tr("theme_settings_dialog.colors_error", "Ошибка загрузки цветов:"), QLabel(str(e)))

        colors_group.setLayout(colors_form_layout)
        colors_layout.addWidget(colors_group)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)

        main_layout.addWidget(button_box)

        # Подключаем сигналы
        self.visual_theme_combo.currentIndexChanged.connect(self.preview_visual_theme)
        self.language_combo.currentIndexChanged.connect(self.preview_language)

        # Сохраняем оригинальные настройки для возможности отмены
        self.original_theme = current_theme
        self.original_language = current_language

    def is_light_color(self, color):
        """Определяет, является ли цвет светлым (для выбора контрастного текста)."""
        if color.startswith('#'):
            color = color[1:]

        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        # Формула для определения яркости
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness > 128

    def preview_visual_theme(self):
        """Предварительный просмотр выбранной визуальной темы."""
        theme_type = self.visual_theme_combo.currentData()
        if theme_type:
            # Применяем тему через ThemeManager
            self.theme_manager.switch_visual_theme(theme_type)

            # Обновляем цвета кнопок на вкладке цветов
            self.update_color_buttons(theme_type)

    def update_color_buttons(self, theme_type):
        """Обновляет цвета кнопок редактирования цветов при смене темы."""
        try:
            if theme_type in self.theme_manager.themes:
                theme_colors = self.theme_manager.themes[theme_type]

                for color_name, color_value in theme_colors.items():
                    if color_name in self.color_buttons:
                        button = self.color_buttons[color_name]
                        button.setText(color_value)
                        text_color = '#000000' if self.is_light_color(color_value) else '#FFFFFF'
                        button.setStyleSheet(f"background-color: {color_value}; color: {text_color};")
        except Exception as e:
            logger.error(f"Ошибка обновления кнопок цветов: {str(e)}")

    def preview_language(self):
        """Предварительный просмотр выбранного языка."""
        language_code = self.language_combo.currentData()
        if language_code:
            # Применяем язык через JsonTranslationManager
            JsonTranslationManager.instance().switch_language(language_code)

    def change_color(self, color_name):
        """Изменяет цвет темы с помощью диалога выбора цвета."""
        current_button = self.color_buttons.get(color_name)
        if not current_button:
            return

        current_color = current_button.text()

        color = QColorDialog.getColor(Qt.black, self, f"Выберите цвет для {color_name}")
        if color.isValid():
            hex_color = color.name()

            # Обновляем кнопку
            current_button.setText(hex_color)
            text_color = '#000000' if self.is_light_color(hex_color) else '#FFFFFF'
            current_button.setStyleSheet(f"background-color: {hex_color}; color: {text_color};")

            # Обновляем цвет в пользовательской теме
            theme_type = self.visual_theme_combo.currentData()
            if theme_type in self.theme_manager.themes:
                # Создаем копию текущей темы
                custom_theme = self.theme_manager.themes[theme_type].copy()
                custom_theme[color_name] = hex_color

                # Создаем пользовательскую тему
                custom_theme_name = f"custom_{theme_type}"
                self.theme_manager.add_custom_theme(custom_theme_name, custom_theme)

                # Выбираем пользовательскую тему в комбобоксе
                for i in range(self.visual_theme_combo.count()):
                    if self.visual_theme_combo.itemData(i) == custom_theme_name:
                        self.visual_theme_combo.setCurrentIndex(i)
                        break
                else:
                    # Если пользовательской темы нет в списке, добавляем ее
                    display_name = self.theme_manager.get_theme_display_name(custom_theme_name)
                    self.visual_theme_combo.addItem(display_name, custom_theme_name)
                    self.visual_theme_combo.setCurrentIndex(self.visual_theme_combo.count() - 1)

                # Применяем новую тему
                self.theme_manager.switch_visual_theme(custom_theme_name)

    def apply_settings(self):
        """Применяет выбранные настройки."""
        # Применяем визуальную тему
        theme_type = self.visual_theme_combo.currentData()
        self.theme_manager.switch_visual_theme(theme_type)

        # Применяем язык
        language_code = self.language_combo.currentData()
        JsonTranslationManager.instance().switch_language(language_code)

    def accept(self):
        """Применяет изменения и закрывает диалог."""
        self.apply_settings()
        super().accept()

    def reject(self):
        """Отменяет изменения и закрывает диалог."""
        # Восстанавливаем оригинальную тему
        self.theme_manager.switch_visual_theme(self.original_theme)

        # Восстанавливаем оригинальный язык
        JsonTranslationManager.instance().switch_language(self.original_language)

        super().reject()
