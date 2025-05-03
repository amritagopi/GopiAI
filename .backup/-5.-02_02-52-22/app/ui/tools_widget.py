from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QComboBox, QCheckBox, QSpinBox, QSlider, QFormLayout,
    QGroupBox, QToolButton, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from .icon_manager import get_icon
from .i18n.translator import tr


class ToolsWidget(QWidget):
    """Виджет с инструментами для GopiAI."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем главный layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)

        # Вкладка настроек агента
        self.agent_tab = QWidget()
        self.agent_layout = QVBoxLayout(self.agent_tab)

        # Форма настроек агента
        self.agent_form = QFormLayout()
        self.agent_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Добавляем элементы формы
        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4", "Claude 3 Opus", "Claude 3 Sonnet", "Llama 3"])
        self.agent_form.addRow(tr("tools.agent.model", "Модель:"), self.model_combo)

        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_slider.setTracking(True)

        self.temperature_value = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(
            lambda value: self.temperature_value.setText(f"{value/100:.1f}")
        )

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_value)

        self.agent_form.addRow(tr("tools.agent.temperature", "Температура:"), temp_layout)

        self.reflection_checkbox = QCheckBox(tr("tools.agent.reflection_enabled", "Включено"))
        self.reflection_checkbox.setChecked(True)

        self.reflection_level = QSpinBox()
        self.reflection_level.setRange(1, 3)
        self.reflection_level.setValue(1)
        self.reflection_level.setEnabled(self.reflection_checkbox.isChecked())

        self.reflection_checkbox.toggled.connect(self.reflection_level.setEnabled)

        reflection_layout = QHBoxLayout()
        reflection_layout.addWidget(self.reflection_checkbox)
        reflection_layout.addWidget(self.reflection_level)

        self.agent_form.addRow(tr("tools.agent.reflection", "Рефлексия:"), reflection_layout)

        self.memory_checkbox = QCheckBox(tr("tools.agent.memory_enabled", "Включена"))
        self.memory_checkbox.setChecked(True)
        self.agent_form.addRow(tr("tools.agent.memory", "Память:"), self.memory_checkbox)

        # Группа кнопок управления агентом
        self.agent_buttons = QHBoxLayout()

        self.run_button = QPushButton(tr("tools.agent.run", "Запустить"))
        self.run_button.setIcon(get_icon("play"))
        self.run_button.setMinimumWidth(100)

        self.stop_button = QPushButton(tr("tools.agent.stop", "Остановить"))
        self.stop_button.setIcon(get_icon("stop"))
        self.stop_button.setMinimumWidth(100)
        self.stop_button.setEnabled(False)

        self.agent_buttons.addWidget(self.run_button)
        self.agent_buttons.addWidget(self.stop_button)

        # Добавляем форму и кнопки на вкладку агента
        self.agent_layout.addLayout(self.agent_form)
        self.agent_layout.addStretch(1)
        self.agent_layout.addLayout(self.agent_buttons)

        # Вкладка инструментов разработчика
        self.dev_tab = QWidget()
        self.dev_layout = QVBoxLayout(self.dev_tab)

        # Группы инструментов
        self.dev_tools_group = QGroupBox(tr("tools.dev.tools", "Инструменты разработчика"))
        self.dev_tools_layout = QVBoxLayout(self.dev_tools_group)

        # Кнопки инструментов
        self.inspect_button = QPushButton(tr("tools.dev.inspect", "Инспектор элементов"))
        self.inspect_button.setIcon(get_icon("inspect"))

        self.console_button = QPushButton(tr("tools.dev.console", "JavaScript консоль"))
        self.console_button.setIcon(get_icon("console"))

        self.dev_tools_layout.addWidget(self.inspect_button)
        self.dev_tools_layout.addWidget(self.console_button)

        # Добавляем группу на вкладку
        self.dev_layout.addWidget(self.dev_tools_group)
        self.dev_layout.addStretch(1)

        # Добавляем вкладки
        self.tabs.addTab(self.agent_tab, get_icon("agent"), tr("tools.tabs.agent", "Агент"))
        self.tabs.addTab(self.dev_tab, get_icon("tools"), tr("tools.tabs.dev", "Разработка"))

        # Добавляем вкладки в основной layout
        self.layout.addWidget(self.tabs)
