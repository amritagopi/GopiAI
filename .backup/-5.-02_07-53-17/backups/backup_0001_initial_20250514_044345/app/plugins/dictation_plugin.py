from typing import Optional, Dict, Any

from PySide6.QtWidgets import QDockWidget, QWidget, QDialog
from PySide6.QtCore import Qt, Signal, Slot, QObject
from PySide6.QtGui import QKeySequence, QShortcut

from app.plugins.plugin_base import PluginBase
from app.ui.dictation_widget import DictationWidget
from app.ui.i18n.translator import tr
from app.logger import logger
from app.utils.settings import get_settings
from app.voice.dictation_manager import DictationManager


class DictationPlugin(PluginBase):
    """
    Плагин для голосового ввода текста с использованием модели Whisper.
    """

    NAME = "dictation"
    DISPLAY_NAME = tr("dictation.plugin.name", "Голосовой ввод")
    DESCRIPTION = tr("dictation.plugin.description", "Поддержка голосового ввода с использованием модели Whisper")
    VERSION = "1.0.0"
    AUTHOR = "GopiAI"

    def __init__(self, parent: Optional[QObject] = None):
        """
        Инициализирует плагин диктовки.

        Args:
            parent: Родительский объект
        """
        super().__init__(parent)

        self.dictation_widget = None
        self.dock_widget = None
        self.main_window = None
        self.shortcuts = {}  # Словарь для хранения горячих клавиш

        # Параметры модели
        self.settings = get_settings()
        self.model_path = self.settings.value("dictation/model_path", "ggml-small-q8_0.bin")
        self.device = self.settings.value("dictation/device", "cpu")
        self.language = self.settings.value("dictation/language", None)

    def initialize(self, main_window):
        """
        Инициализирует плагин.

        Args:
            main_window: Главное окно приложения
        """
        self.main_window = main_window

        # Создаем виджет диктовки
        self.dictation_widget = DictationWidget(
            model_path=self.model_path,
            device=self.device,
            language=self.language
        )

        # Подключаем сигнал распознанного текста
        self.dictation_widget.textRecognized.connect(self._on_text_recognized)

        # Создаем dock-виджет
        self.dock_widget = QDockWidget(tr("dictation.dock.title", "Голосовой ввод"), self.main_window)
        self.dock_widget.setObjectName("dictationDockWidget")
        self.dock_widget.setWidget(self.dictation_widget)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Добавляем dock-виджет в главное окно
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        # Добавляем пункт меню
        self.add_menu_item(
            menu="view",
            item_text=tr("dictation.menu.show_panel", "Панель голосового ввода"),
            callback=self._toggle_dock_widget
        )

        # Настраиваем горячие клавиши
        self._setup_shortcuts()

        # По умолчанию панель скрыта
        self.dock_widget.hide()

        logger.info("Плагин диктовки инициализирован")

    def _setup_shortcuts(self):
        """Настраивает горячие клавиши для управления диктовкой."""
        # Получаем настройки горячих клавиш из конфигурации
        start_key = self.settings.value("dictation/shortcut_start", "Ctrl+Alt+D")
        stop_key = self.settings.value("dictation/shortcut_stop", "Ctrl+Alt+S")
        toggle_key = self.settings.value("dictation/shortcut_toggle", "Ctrl+Alt+T")

        # Создаем горячие клавиши для основных действий
        self.shortcuts["start"] = QShortcut(QKeySequence(start_key), self.main_window)
        self.shortcuts["start"].activated.connect(self._start_dictation_shortcut)

        self.shortcuts["stop"] = QShortcut(QKeySequence(stop_key), self.main_window)
        self.shortcuts["stop"].activated.connect(self._stop_dictation_shortcut)

        self.shortcuts["toggle"] = QShortcut(QKeySequence(toggle_key), self.main_window)
        self.shortcuts["toggle"].activated.connect(self._toggle_dictation_shortcut)

        logger.info(f"Настроены горячие клавиши для диктовки: Старт ({start_key}), Стоп ({stop_key}), Переключение ({toggle_key})")

    def _start_dictation_shortcut(self):
        """Обработчик горячей клавиши для начала диктовки."""
        if self.dictation_widget:
            # Показываем панель, если она скрыта
            if not self.dock_widget.isVisible():
                self.dock_widget.show()

            # Начинаем диктовку
            self.dictation_widget.start_recording()
            logger.info("Диктовка запущена с помощью горячей клавиши")

    def _stop_dictation_shortcut(self):
        """Обработчик горячей клавиши для остановки диктовки."""
        if self.dictation_widget:
            # Останавливаем диктовку, если она запущена
            if self.dictation_widget.dictation_manager and self.dictation_widget.dictation_manager.is_recording:
                self.dictation_widget.stop_recording()
                logger.info("Диктовка остановлена с помощью горячей клавиши")

    def _toggle_dictation_shortcut(self):
        """Обработчик горячей клавиши для переключения состояния диктовки."""
        if self.dictation_widget:
            # Если панель скрыта, показываем её
            if not self.dock_widget.isVisible():
                self.dock_widget.show()

            # Переключаем состояние диктовки
            self.dictation_widget.toggle_recording()
            logger.info("Состояние диктовки переключено с помощью горячей клавиши")

    def _toggle_dock_widget(self):
        """Показывает или скрывает панель диктовки."""
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()

    def _on_text_recognized(self, text: str):
        """
        Обработчик распознанного текста.

        Args:
            text: Распознанный текст
        """
        if not text:
            return

        # Получаем активный виджет редактора
        editor = self.main_window.get_current_editor()
        if editor:
            # Вставляем текст в позицию курсора
            editor.insertPlainText(text)
            logger.info(f"Вставлен распознанный текст ({len(text)} символов)")
        else:
            logger.warning("Не найден активный редактор для вставки текста")

    def cleanup(self):
        """Освобождает ресурсы плагина."""
        # Удаляем горячие клавиши
        for shortcut in self.shortcuts.values():
            shortcut.setEnabled(False)
        self.shortcuts.clear()

        if self.dock_widget:
            self.main_window.removeDockWidget(self.dock_widget)

        if self.dictation_widget:
            # DictationWidget автоматически освобождает ресурсы в closeEvent
            self.dictation_widget.close()

        logger.info("Плагин диктовки остановлен")

    def save_settings(self):
        """Сохраняет настройки плагина."""
        if self.dictation_widget and self.dictation_widget.dictation_manager:
            dm = self.dictation_widget.dictation_manager

            self.settings.setValue("dictation/language", dm.language)
            self.settings.setValue("dictation/auto_language_detection", dm.auto_language_detection)

        logger.info("Настройки плагина диктовки сохранены")

    def metadata(self) -> Dict[str, Any]:
        """
        Возвращает метаданные плагина.

        Returns:
            Словарь с метаданными
        """
        return {
            "name": self.NAME,
            "display_name": self.DISPLAY_NAME,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "author": self.AUTHOR,
            "required_python_packages": ["PyAudio", "faster-whisper", "numpy"],
            "dockable": True
        }
