"""
Диалог настроек приложения

Позволяет пользователю настраивать параметры интерфейса,
локализацию, тему и другие общие настройки.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QComboBox, QCheckBox, QSpinBox, QLabel,
    QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QSettings

from app.ui.i18n.translator import tr, JsonTranslationManager
from app.utils.theme_manager import ThemeManager


class PreferencesDialog(QDialog):
    """
    Диалог для настройки основных параметров приложения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings.dialog.title", "Settings"))
        self.setMinimumSize(500, 400)

        # Получаем экземпляры менеджеров
        self.translator = JsonTranslationManager.instance()
        self.theme_manager = ThemeManager.instance()

        # Настройки для сохранения
        self.settings = QSettings("GopiAI", "UI")

        # Начальные значения
        self.selected_language = self.translator.get_current_language()
        self.selected_theme = self.theme_manager.get_current_visual_theme()

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс диалога."""
        # Основной layout
        main_layout = QVBoxLayout(self)

        # Создаем вкладки
        tab_widget = QTabWidget()

        # Вкладка "Внешний вид"
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)

        # Группа "Интерфейс"
        ui_group = QGroupBox(tr("settings.dialog.appearance", "Appearance"))
        ui_layout = QFormLayout(ui_group)

        # Выбор языка
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en_US")
        self.language_combo.addItem("Русский", "ru_RU")
        self.language_combo.setCurrentIndex(0 if self.selected_language == "en_US" else 1)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)

        # Выбор темы
        self.theme_combo = QComboBox()
        for theme_name in self.theme_manager.get_available_themes():
            self.theme_combo.addItem(theme_name, theme_name)
        # Устанавливаем текущую тему
        current_theme_index = self.theme_combo.findData(self.selected_theme)
        if current_theme_index >= 0:
            self.theme_combo.setCurrentIndex(current_theme_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        # Добавляем элементы в форму
        ui_layout.addRow(tr("settings.dialog.language", "Language:"), self.language_combo)
        ui_layout.addRow(tr("settings.dialog.theme", "Theme:"), self.theme_combo)

        # Предупреждение о необходимости перезапуска
        restart_label = QLabel(tr("settings.restart_message", "Some changes require application restart."))
        restart_label.setStyleSheet("color: red;")
        restart_label.setVisible(False)
        self.restart_label = restart_label

        # Добавляем в layout
        appearance_layout.addWidget(ui_group)
        appearance_layout.addWidget(restart_label)
        appearance_layout.addStretch()

        # Вкладка "Расширенные"
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        advanced_group = QGroupBox(tr("settings.dialog.advanced", "Advanced"))
        advanced_form = QFormLayout(advanced_group)

        # Здесь можно добавить дополнительные настройки

        advanced_layout.addWidget(advanced_group)
        advanced_layout.addStretch()

        # Добавляем вкладки
        tab_widget.addTab(appearance_tab, tr("settings.appearance", "Appearance"))
        tab_widget.addTab(advanced_tab, tr("settings.advanced", "Advanced"))

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(tr("dialogs.ok", "OK"))
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton(tr("dialogs.cancel", "Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        # Собираем все вместе
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

    def _load_settings(self):
        """Загружает текущие настройки."""
        pass

    def _on_language_changed(self, index):
        """Обработчик изменения языка."""
        new_language = self.language_combo.itemData(index)
        if new_language != self.selected_language:
            self.selected_language = new_language
            self.restart_label.setVisible(True)

    def _on_theme_changed(self, index):
        """Обработчик изменения темы."""
        new_theme = self.theme_combo.itemData(index)
        if new_theme != self.selected_theme:
            self.selected_theme = new_theme
            # Динамически меняем тему для предварительного просмотра
            self.theme_manager.set_theme(new_theme)

    def accept(self):
        """Сохраняет настройки и закрывает диалог."""
        # Сохраняем язык
        if self.selected_language != self.translator.get_current_language():
            self.translator.switch_language(self.selected_language)

            # Показываем предупреждение о перезапуске
            QMessageBox.information(
                self,
                tr("settings.restart_required", "Restart required"),
                tr("settings.restart_message", "Some changes require application restart.")
            )

        # Сохраняем тему
        if self.selected_theme != self.theme_manager.get_current_visual_theme():
            self.theme_manager.set_theme(self.selected_theme)

        # Закрываем диалог
        super().accept()

    def reject(self):
        """Отменяет изменения и закрывает диалог."""
        # Восстанавливаем исходную тему, если она была изменена
        if self.selected_theme != self.theme_manager.get_current_visual_theme():
            self.theme_manager.set_theme(self.theme_manager.get_current_visual_theme())

        # Закрываем диалог
        super().reject()
