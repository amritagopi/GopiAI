import os
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QComboBox, QCheckBox, QDialog, QGroupBox,
    QFormLayout, QSpinBox, QDialogButtonBox, QTabWidget,
    QKeySequenceEdit, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QKeySequence

from app.voice.dictation_manager import DictationManager
from app.ui.i18n.translator import tr
from app.logger import logger
from app.utils.settings import get_settings


class DictationWidget(QWidget):
    """
    Виджет для голосового ввода текста.
    Предоставляет интерфейс для записи и распознавания речи.
    """

    # Сигнал для передачи распознанного текста
    textRecognized = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        model_path: str = "small",
        device: str = "cpu",
        language: Optional[str] = None
    ):
        """
        Инициализирует виджет диктовки.

        Args:
            parent: Родительский виджет
            model_path: Путь к модели или название предустановленной модели
            device: Устройство для вычислений ("cpu", "cuda")
            language: Язык для распознавания (None - автоопределение)
        """
        super().__init__(parent)

        # Создаем менеджер диктовки
        try:
            self.dictation_manager = DictationManager(
                model_path=model_path,
                device=device,
                language=language,
                auto_language_detection=True
            )

            # Подключаем сигналы менеджера
            self.dictation_manager.recordingStarted.connect(self._on_recording_started)
            self.dictation_manager.recordingStopped.connect(self._on_recording_stopped)
            self.dictation_manager.recordingPaused.connect(self._on_recording_paused)
            self.dictation_manager.recordingResumed.connect(self._on_recording_resumed)
            self.dictation_manager.volumeChanged.connect(self._on_volume_changed)
            self.dictation_manager.transcribing.connect(self._on_transcribing)
            self.dictation_manager.transcriptionComplete.connect(self._on_transcription_complete)
            self.dictation_manager.transcriptionError.connect(self._on_transcription_error)

        except Exception as e:
            logger.error(f"Ошибка при инициализации менеджера диктовки: {e}")
            self.dictation_manager = None

        # Сохраняем последний распознанный текст
        self.last_transcription = ""

        self._init_ui()

    def _init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        # Основной макет
        main_layout = QVBoxLayout(self)

        # Загружаем иконки или используем текст для кнопок
        record_icon = QIcon(":/icons/record.svg") if os.path.exists(":/icons/record.svg") else None
        stop_icon = QIcon(":/icons/stop.svg") if os.path.exists(":/icons/stop.svg") else None
        pause_icon = QIcon(":/icons/pause.svg") if os.path.exists(":/icons/pause.svg") else None
        settings_icon = QIcon(":/icons/settings.svg") if os.path.exists(":/icons/settings.svg") else None
        save_icon = QIcon(":/icons/save.svg") if os.path.exists(":/icons/save.svg") else None

        # Статус
        self.status_label = QLabel(tr("dictation.status.ready", "Готов к записи"))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Уровень громкости
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)
        self.volume_bar.setTextVisible(False)
        main_layout.addWidget(self.volume_bar)

        # Панель с кнопками
        buttons_layout = QHBoxLayout()

        # Кнопка записи
        self.record_button = QPushButton()
        if record_icon:
            self.record_button.setIcon(record_icon)
            self.record_button.setIconSize(QSize(24, 24))
        else:
            self.record_button.setText(tr("dictation.record", "Запись"))
        self.record_button.setToolTip(tr("dictation.record.tooltip", "Начать запись"))
        self.record_button.clicked.connect(self.toggle_recording)
        buttons_layout.addWidget(self.record_button)

        # Кнопка паузы
        self.pause_button = QPushButton()
        if pause_icon:
            self.pause_button.setIcon(pause_icon)
            self.pause_button.setIconSize(QSize(24, 24))
        else:
            self.pause_button.setText(tr("dictation.pause", "Пауза"))
        self.pause_button.setToolTip(tr("dictation.pause.tooltip", "Приостановить запись"))
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        buttons_layout.addWidget(self.pause_button)

        # Кнопка остановки
        self.stop_button = QPushButton()
        if stop_icon:
            self.stop_button.setIcon(stop_icon)
            self.stop_button.setIconSize(QSize(24, 24))
        else:
            self.stop_button.setText(tr("dictation.stop", "Стоп"))
        self.stop_button.setToolTip(tr("dictation.stop.tooltip", "Остановить запись и распознать"))
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_button)

        # Кнопка сохранения текста
        self.save_button = QPushButton()
        if save_icon:
            self.save_button.setIcon(save_icon)
            self.save_button.setIconSize(QSize(24, 24))
        else:
            self.save_button.setText(tr("dictation.save", "Сохранить"))
        self.save_button.setToolTip(tr("dictation.save.tooltip", "Сохранить распознанный текст в файл"))
        self.save_button.clicked.connect(self.save_transcription)
        self.save_button.setEnabled(False)
        buttons_layout.addWidget(self.save_button)

        # Кнопка настроек
        self.settings_button = QPushButton()
        if settings_icon:
            self.settings_button.setIcon(settings_icon)
            self.settings_button.setIconSize(QSize(24, 24))
        else:
            self.settings_button.setText(tr("dictation.settings", "Настройки"))
        self.settings_button.setToolTip(tr("dictation.settings.tooltip", "Настройки диктовки"))
        self.settings_button.clicked.connect(self.show_settings)
        buttons_layout.addWidget(self.settings_button)

        main_layout.addLayout(buttons_layout)

        # Чекбокс для автоматической остановки
        self.auto_stop_checkbox = QCheckBox(tr("dictation.auto_stop", "Автоматическая остановка при тишине"))
        self.auto_stop_checkbox.setChecked(True)
        main_layout.addWidget(self.auto_stop_checkbox)

        # Обновляем внешний вид в зависимости от доступности менеджера
        self._update_ui_enabled()

    def _update_ui_enabled(self):
        """Обновляет доступность элементов интерфейса."""
        enabled = self.dictation_manager is not None

        self.record_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.auto_stop_checkbox.setEnabled(enabled)

        if not enabled:
            self.status_label.setText(tr("dictation.status.error", "Ошибка инициализации"))
            self.status_label.setStyleSheet("color: red")

    def save_transcription(self):
        """Сохраняет распознанный текст в файл."""
        if not self.last_transcription:
            logger.warning("Нет текста для сохранения")
            return

        # Открываем диалог сохранения файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("dictation.save.dialog_title", "Сохранить распознанный текст"),
            "",
            tr("dictation.save.file_filter", "Текстовые файлы (*.txt);;Все файлы (*)")
        )

        if not file_path:
            return

        try:
            # Добавляем расширение .txt, если оно отсутствует
            if not file_path.lower().endswith('.txt'):
                file_path += '.txt'

            # Сохраняем текст в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.last_transcription)

            logger.info(f"Распознанный текст сохранен в файл: {file_path}")

            # Обновляем статус
            self.status_label.setText(tr("dictation.status.saved", "Текст сохранен"))
            self.status_label.setStyleSheet("color: green")

        except Exception as e:
            logger.error(f"Ошибка при сохранении текста: {e}")
            self.status_label.setText(tr("dictation.status.save_error", "Ошибка при сохранении"))
            self.status_label.setStyleSheet("color: red")

    def toggle_recording(self):
        """Начинает или останавливает запись."""
        if not self.dictation_manager:
            return

        if self.dictation_manager.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Начинает запись."""
        if not self.dictation_manager:
            return

        auto_stop = self.auto_stop_checkbox.isChecked()
        self.dictation_manager.start_dictation(auto_stop=auto_stop)

    def stop_recording(self):
        """Останавливает запись и запускает распознавание."""
        if not self.dictation_manager:
            return

        self.dictation_manager.stop_dictation(transcribe=True)

    def toggle_pause(self):
        """Приостанавливает или возобновляет запись."""
        if not self.dictation_manager:
            return

        if self.dictation_manager.is_paused:
            self.dictation_manager.resume_dictation()
        else:
            self.dictation_manager.pause_dictation()

    def show_settings(self):
        """Показывает диалог настроек."""
        dialog = DictationSettingsDialog(self.dictation_manager, self)
        dialog.exec()

    def _on_recording_started(self):
        """Обработчик начала записи."""
        self.status_label.setText(tr("dictation.status.recording", "Запись..."))
        self.status_label.setStyleSheet("color: red")

        self.record_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.auto_stop_checkbox.setEnabled(False)

    def _on_recording_stopped(self):
        """Обработчик остановки записи."""
        self.status_label.setText(tr("dictation.status.stopped", "Запись остановлена"))
        self.status_label.setStyleSheet("")

        self.record_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.auto_stop_checkbox.setEnabled(True)

        # Сбрасываем уровень громкости
        self.volume_bar.setValue(0)

    def _on_recording_paused(self):
        """Обработчик паузы записи."""
        self.status_label.setText(tr("dictation.status.paused", "Запись приостановлена"))
        self.status_label.setStyleSheet("color: orange")

        self.pause_button.setText(tr("dictation.resume", "Продолжить"))

    def _on_recording_resumed(self):
        """Обработчик возобновления записи."""
        self.status_label.setText(tr("dictation.status.recording", "Запись..."))
        self.status_label.setStyleSheet("color: red")

        self.pause_button.setText(tr("dictation.pause", "Пауза"))

    def _on_volume_changed(self, volume: float):
        """Обработчик изменения уровня громкости."""
        self.volume_bar.setValue(int(volume * 100))

    def _on_transcribing(self):
        """Обработчик начала распознавания."""
        self.status_label.setText(tr("dictation.status.transcribing", "Распознавание..."))
        self.status_label.setStyleSheet("color: blue")

        self.record_button.setEnabled(False)
        self.settings_button.setEnabled(False)

    def _on_transcription_complete(self, text: str):
        """Обработчик завершения распознавания."""
        self.status_label.setText(tr("dictation.status.transcription_complete", "Распознавание завершено"))
        self.status_label.setStyleSheet("color: green")

        self.record_button.setEnabled(True)
        self.settings_button.setEnabled(True)

        # Сохраняем текст и активируем кнопку сохранения
        self.last_transcription = text
        self.save_button.setEnabled(True)

        # Отправляем сигнал с распознанным текстом
        self.textRecognized.emit(text)

    def _on_transcription_error(self, error: str):
        """Обработчик ошибки распознавания."""
        self.status_label.setText(tr("dictation.status.transcription_error", "Ошибка распознавания"))
        self.status_label.setStyleSheet("color: red")

        self.record_button.setEnabled(True)
        self.settings_button.setEnabled(True)
        self.save_button.setEnabled(False)

        logger.error(f"Ошибка распознавания: {error}")

    def closeEvent(self, event):
        """Обработчик закрытия виджета."""
        if self.dictation_manager:
            self.dictation_manager.cleanup()
        event.accept()


class DictationSettingsDialog(QDialog):
    """Диалог настроек диктовки."""

    def __init__(self, dictation_manager: DictationManager, parent: Optional[QWidget] = None):
        """
        Инициализирует диалог настроек.

        Args:
            dictation_manager: Менеджер диктовки
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.dictation_manager = dictation_manager
        self.settings = get_settings()

        self.setWindowTitle(tr("dictation.settings.title", "Настройки диктовки"))
        self.setMinimumWidth(400)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        main_layout = QVBoxLayout(self)

        # Создаем вкладки для разных категорий настроек
        self.tab_widget = QTabWidget()

        # Вкладка основных настроек
        self.general_tab = QWidget()
        self.tab_widget.addTab(self.general_tab, tr("dictation.settings.tab.general", "Основные"))

        # Вкладка горячих клавиш
        self.shortcuts_tab = QWidget()
        self.tab_widget.addTab(self.shortcuts_tab, tr("dictation.settings.tab.shortcuts", "Горячие клавиши"))

        main_layout.addWidget(self.tab_widget)

        # Инициализируем основные настройки
        self._init_general_tab()

        # Инициализируем настройки горячих клавиш
        self._init_shortcuts_tab()

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._apply_settings)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _init_general_tab(self):
        """Инициализирует вкладку основных настроек."""
        layout = QVBoxLayout(self.general_tab)

        # Группа настроек устройства ввода
        input_group = QGroupBox(tr("dictation.settings.input_device", "Устройство ввода"))
        input_layout = QFormLayout(input_group)

        # Комбобокс с устройствами ввода
        self.devices_combo = QComboBox()
        self._populate_devices_combo()
        input_layout.addRow(tr("dictation.settings.device", "Устройство:"), self.devices_combo)

        layout.addWidget(input_group)

        # Группа настроек распознавания
        recognition_group = QGroupBox(tr("dictation.settings.recognition", "Распознавание речи"))
        recognition_layout = QFormLayout(recognition_group)

        # Чекбокс автоопределения языка
        self.auto_detect_checkbox = QCheckBox(tr("dictation.settings.auto_detect", "Автоматически определять язык"))
        self.auto_detect_checkbox.setChecked(self.dictation_manager.auto_language_detection)
        self.auto_detect_checkbox.stateChanged.connect(self._on_auto_detect_changed)
        recognition_layout.addRow("", self.auto_detect_checkbox)

        # Комбобокс выбора языка
        self.language_combo = QComboBox()
        self.language_combo.addItem(tr("dictation.settings.language.ru", "Русский"), "ru")
        self.language_combo.addItem(tr("dictation.settings.language.en", "Английский"), "en")
        self.language_combo.addItem(tr("dictation.settings.language.de", "Немецкий"), "de")
        self.language_combo.addItem(tr("dictation.settings.language.fr", "Французский"), "fr")
        self.language_combo.addItem(tr("dictation.settings.language.es", "Испанский"), "es")

        # Устанавливаем текущий язык
        if self.dictation_manager.language:
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == self.dictation_manager.language:
                    self.language_combo.setCurrentIndex(i)
                    break

        # Если включено автоопределение, отключаем выбор языка
        self.language_combo.setEnabled(not self.dictation_manager.auto_language_detection)

        recognition_layout.addRow(tr("dictation.settings.language", "Язык:"), self.language_combo)

        # Настройки автоматической остановки
        self.auto_stop_checkbox = QCheckBox(tr("dictation.settings.auto_stop", "Автоматически останавливать при тишине"))
        self.auto_stop_checkbox.setChecked(True)
        recognition_layout.addRow("", self.auto_stop_checkbox)

        # Длительность тишины
        self.silence_duration_spin = QSpinBox()
        self.silence_duration_spin.setRange(1, 10)
        self.silence_duration_spin.setValue(2)
        self.silence_duration_spin.setSuffix(" " + tr("dictation.settings.seconds", "сек"))
        recognition_layout.addRow(tr("dictation.settings.silence_duration", "Длительность тишины:"), self.silence_duration_spin)

        layout.addWidget(recognition_group)

        # Добавляем растягивающийся промежуток внизу
        layout.addStretch()

    def _init_shortcuts_tab(self):
        """Инициализирует вкладку настроек горячих клавиш."""
        layout = QVBoxLayout(self.shortcuts_tab)

        # Инструкция для пользователя
        help_label = QLabel(tr("dictation.shortcuts.help", "Настройте горячие клавиши для быстрого доступа к функциям диктовки:"))
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # Группа настроек горячих клавиш
        shortcuts_group = QGroupBox(tr("dictation.shortcuts.group", "Горячие клавиши"))
        shortcuts_layout = QFormLayout(shortcuts_group)

        # Получаем текущие настройки горячих клавиш
        start_key = self.settings.value("dictation/shortcut_start", "Ctrl+Alt+D")
        stop_key = self.settings.value("dictation/shortcut_stop", "Ctrl+Alt+S")
        toggle_key = self.settings.value("dictation/shortcut_toggle", "Ctrl+Alt+T")

        # Горячая клавиша для начала диктовки
        self.start_key_edit = QKeySequenceEdit(QKeySequence(start_key))
        shortcuts_layout.addRow(tr("dictation.shortcuts.start", "Начать диктовку:"), self.start_key_edit)

        # Горячая клавиша для остановки диктовки
        self.stop_key_edit = QKeySequenceEdit(QKeySequence(stop_key))
        shortcuts_layout.addRow(tr("dictation.shortcuts.stop", "Остановить диктовку:"), self.stop_key_edit)

        # Горячая клавиша для переключения диктовки
        self.toggle_key_edit = QKeySequenceEdit(QKeySequence(toggle_key))
        shortcuts_layout.addRow(tr("dictation.shortcuts.toggle", "Переключить диктовку:"), self.toggle_key_edit)

        layout.addWidget(shortcuts_group)

        # Добавляем растягивающийся промежуток внизу
        layout.addStretch()

    def _populate_devices_combo(self):
        """Заполняет комбобокс доступными устройствами ввода."""
        self.devices_combo.clear()

        # Добавляем устройство по умолчанию
        self.devices_combo.addItem(tr("dictation.settings.default_device", "Устройство по умолчанию"), -1)

        # Получаем список доступных устройств
        devices = self.dictation_manager.get_available_devices()

        for device in devices:
            self.devices_combo.addItem(f"{device['name']}", device['index'])

        # Устанавливаем текущее устройство
        # Здесь нужно добавить код для определения текущего устройства в рекордере

    def _on_auto_detect_changed(self, state):
        """Обработчик изменения состояния чекбокса автоопределения языка."""
        self.language_combo.setEnabled(not state)

    def _apply_settings(self):
        """Применяет настройки."""
        # Применяем основные настройки

        # Устройство ввода
        device_index = self.devices_combo.currentData()
        if device_index != -1:  # Если выбрано не устройство по умолчанию
            self.dictation_manager.set_input_device(device_index)

        # Язык и автоопределение
        auto_detect = self.auto_detect_checkbox.isChecked()
        self.dictation_manager.set_auto_language_detection(auto_detect)

        if not auto_detect:
            language = self.language_combo.currentData()
            self.dictation_manager.set_language(language)

        # Применяем настройки горячих клавиш
        self.settings.setValue("dictation/shortcut_start", self.start_key_edit.keySequence().toString())
        self.settings.setValue("dictation/shortcut_stop", self.stop_key_edit.keySequence().toString())
        self.settings.setValue("dictation/shortcut_toggle", self.toggle_key_edit.keySequence().toString())

        # Закрываем диалог
        self.accept()
