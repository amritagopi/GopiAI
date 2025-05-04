"""
Диалог настроек Reasoning Agent

Отвечает за настройку параметров работы рассуждений агента
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QSpinBox, QCheckBox, QComboBox, QPushButton, QFrame,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, Slot

from app.config import config
from app.config.reasoning_config import ReasoningStrategy


class ReasoningSettingsDialog(QDialog):
    """
    Диалог для управления настройками Reasoning Agent.

    Позволяет настраивать глубину рассуждений, стратегию,
    безопасный режим и другие параметры.
    """

    # Сигнал об изменении настроек
    settings_changed = Signal()

    def __init__(self, parent=None):
        """Инициализирует диалог настроек."""
        super().__init__(parent)

        self.setWindowTitle("Настройки рассуждений")
        self.setMinimumWidth(500)

        # Получаем текущие настройки
        self.reasoning_config = config.reasoning_config

        # Создаем интерфейс
        self._setup_ui()

        # Заполняем значения из конфигурации
        self._load_config()

    def _setup_ui(self):
        """Настраивает интерфейс диалога."""
        # Основной layout
        main_layout = QVBoxLayout()

        # Группа настроек рассуждений
        reasoning_group = QGroupBox("Параметры рассуждений")
        reasoning_layout = QFormLayout()

        # Глубина рассуждений
        depth_layout = QHBoxLayout()
        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setMinimum(3)
        self.depth_slider.setMaximum(15)
        self.depth_slider.setTickInterval(1)
        self.depth_slider.setTickPosition(QSlider.TicksBelow)

        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setMinimum(3)
        self.depth_spinbox.setMaximum(15)

        # Связываем слайдер и спинбокс
        self.depth_slider.valueChanged.connect(self.depth_spinbox.setValue)
        self.depth_spinbox.valueChanged.connect(self.depth_slider.setValue)

        depth_layout.addWidget(self.depth_slider)
        depth_layout.addWidget(self.depth_spinbox)

        reasoning_layout.addRow("Глубина рассуждений:", depth_layout)

        # Стратегия рассуждений
        self.strategy_combo = QComboBox()
        for strategy in ReasoningStrategy:
            self.strategy_combo.addItem(
                self._get_strategy_display_name(strategy),
                strategy.value
            )
        reasoning_layout.addRow("Стратегия рассуждений:", self.strategy_combo)

        # Добавляем группу настроек рассуждений
        reasoning_group.setLayout(reasoning_layout)
        main_layout.addWidget(reasoning_group)

        # Группа настроек безопасности
        security_group = QGroupBox("Безопасность и мониторинг")
        security_layout = QFormLayout()

        # Безопасный режим
        self.safe_mode_checkbox = QCheckBox("Включить проверки безопасности")
        self.safe_mode_checkbox.setToolTip(
            "Ограничивает потенциально опасные операции "
            "и требует явного разрешения для них"
        )
        security_layout.addRow("", self.safe_mode_checkbox)

        # Интерактивный режим
        self.interactive_mode_checkbox = QCheckBox("Включить интерактивный режим")
        self.interactive_mode_checkbox.setToolTip(
            "Требует подтверждение для каждого шага выполнения плана"
        )
        security_layout.addRow("", self.interactive_mode_checkbox)

        # Мониторинг
        self.monitoring_checkbox = QCheckBox("Включить мониторинг выполнения")
        self.monitoring_checkbox.setToolTip(
            "Отслеживает выполнение плана и показывает прогресс"
        )
        security_layout.addRow("", self.monitoring_checkbox)

        # Подробное логирование
        self.detailed_logging_checkbox = QCheckBox("Включить подробное логирование")
        self.detailed_logging_checkbox.setToolTip(
            "Записывает все шаги рассуждений в лог"
        )
        security_layout.addRow("", self.detailed_logging_checkbox)

        # Таймаут операций
        timeout_layout = QHBoxLayout()
        self.timeout_slider = QSlider(Qt.Horizontal)
        self.timeout_slider.setMinimum(5)
        self.timeout_slider.setMaximum(300)
        self.timeout_slider.setTickInterval(30)
        self.timeout_slider.setTickPosition(QSlider.TicksBelow)

        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(5)
        self.timeout_spinbox.setMaximum(300)
        self.timeout_spinbox.setSuffix(" сек")

        # Связываем слайдер и спинбокс
        self.timeout_slider.valueChanged.connect(self.timeout_spinbox.setValue)
        self.timeout_spinbox.valueChanged.connect(self.timeout_slider.setValue)

        timeout_layout.addWidget(self.timeout_slider)
        timeout_layout.addWidget(self.timeout_spinbox)

        security_layout.addRow("Таймаут операций:", timeout_layout)

        # Добавляем группу настроек безопасности
        security_group.setLayout(security_layout)
        main_layout.addWidget(security_group)

        # Описание выбранной стратегии
        strategy_info_group = QGroupBox("Описание стратегии")
        strategy_info_layout = QVBoxLayout()

        self.strategy_description = QLabel()
        self.strategy_description.setWordWrap(True)
        self.strategy_description.setMinimumHeight(60)
        strategy_info_layout.addWidget(self.strategy_description)

        strategy_info_group.setLayout(strategy_info_layout)
        main_layout.addWidget(strategy_info_group)

        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Сбросить")
        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")

        self.save_button.setDefault(True)

        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        # Привязываем действия к кнопкам
        self.reset_button.clicked.connect(self._reset_to_defaults)
        self.save_button.clicked.connect(self._save_config)
        self.cancel_button.clicked.connect(self.reject)
        self.strategy_combo.currentIndexChanged.connect(self._update_strategy_description)

        self.setLayout(main_layout)

    def _load_config(self):
        """Загружает настройки из конфигурации."""
        config_data = self.reasoning_config

        # Устанавливаем значения
        self.depth_slider.setValue(config_data.reasoning_depth)
        self.depth_spinbox.setValue(config_data.reasoning_depth)

        # Находим индекс стратегии в комбобоксе
        strategy_index = self.strategy_combo.findData(config_data.reasoning_strategy.value)
        if strategy_index >= 0:
            self.strategy_combo.setCurrentIndex(strategy_index)

        # Устанавливаем флаги
        self.safe_mode_checkbox.setChecked(config_data.safe_mode)
        self.interactive_mode_checkbox.setChecked(config_data.interactive_mode)
        self.monitoring_checkbox.setChecked(config_data.monitoring_enabled)
        self.detailed_logging_checkbox.setChecked(config_data.detailed_logging)

        # Устанавливаем таймаут
        self.timeout_slider.setValue(config_data.operation_timeout)
        self.timeout_spinbox.setValue(config_data.operation_timeout)

        # Обновляем описание стратегии
        self._update_strategy_description()

    def _save_config(self):
        """Сохраняет настройки в конфигурацию."""
        # Получаем данные из интерфейса
        depth = self.depth_spinbox.value()

        strategy_value = self.strategy_combo.currentData()
        strategy = ReasoningStrategy(strategy_value)

        safe_mode = self.safe_mode_checkbox.isChecked()
        interactive_mode = self.interactive_mode_checkbox.isChecked()
        monitoring_enabled = self.monitoring_checkbox.isChecked()
        detailed_logging = self.detailed_logging_checkbox.isChecked()
        timeout = self.timeout_spinbox.value()

        # Обновляем конфигурацию
        self.reasoning_config.reasoning_depth = depth
        self.reasoning_config.reasoning_strategy = strategy
        self.reasoning_config.safe_mode = safe_mode
        self.reasoning_config.interactive_mode = interactive_mode
        self.reasoning_config.monitoring_enabled = monitoring_enabled
        self.reasoning_config.detailed_logging = detailed_logging
        self.reasoning_config.operation_timeout = timeout

        # Проверяем настройки на корректность
        errors = self.reasoning_config.validate()
        if errors:
            # Здесь можно показать диалог с ошибками
            return

        # Сохраняем настройки в глобальную конфигурацию
        config.reasoning_config = self.reasoning_config
        config.save()

        # Отправляем сигнал об изменении настроек
        self.settings_changed.emit()

        # Закрываем диалог
        self.accept()

    def _reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию."""
        from app.config.reasoning_config import DEFAULT_REASONING_CONFIG

        # Создаем копию дефолтной конфигурации
        self.reasoning_config = DEFAULT_REASONING_CONFIG

        # Загружаем дефолтные значения в интерфейс
        self._load_config()

    def _update_strategy_description(self):
        """Обновляет описание выбранной стратегии."""
        strategy_value = self.strategy_combo.currentData()
        if strategy_value:
            strategy = ReasoningStrategy(strategy_value)
            description = ReasoningStrategy.get_description(strategy)
            self.strategy_description.setText(description)

    def _get_strategy_display_name(self, strategy: ReasoningStrategy) -> str:
        """Возвращает отображаемое имя для стратегии."""
        names = {
            ReasoningStrategy.SEQUENTIAL: "Последовательная",
            ReasoningStrategy.TREE: "Древовидная",
            ReasoningStrategy.ADAPTIVE: "Адаптивная",
        }
        return names.get(strategy, str(strategy))
