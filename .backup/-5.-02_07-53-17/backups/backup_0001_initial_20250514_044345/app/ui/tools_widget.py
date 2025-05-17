import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QLabel, QComboBox, QCheckBox, QSpinBox, QSlider, QFormLayout,
    QGroupBox, QToolButton, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction

from app.ui.icon_adapter import get_icon
from app.ui.i18n.translator import tr


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
        self.model_combo.setToolTip(tr("tools.agent.model.tooltip", "Выберите LLM-модель для агента"))
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
        self.run_button.setToolTip(tr("tools.agent.run.tooltip", "Запустить агента"))

        self.stop_button = QPushButton(tr("tools.agent.stop", "Остановить"))
        self.stop_button.setIcon(get_icon("stop"))
        self.stop_button.setMinimumWidth(100)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip(tr("tools.agent.stop.tooltip", "Остановить выполнение агента"))

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
        self.inspect_button.setToolTip(tr("tools.dev.inspect.tooltip", "Открыть инспектор элементов"))

        self.console_button = QPushButton(tr("tools.dev.console", "JavaScript консоль"))
        self.console_button.setIcon(get_icon("console"))
        self.console_button.setToolTip(tr("tools.dev.console.tooltip", "Открыть JavaScript консоль"))

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

        # Переменная для отслеживания наличия вкладки браузера
        self.browser_tab = None
        self.browser_tab_index = -1

    def add_browser_tools_tab(self, browser_tools):
        """Добавляет вкладку с инструментами браузера."""
        # Проверяем, существует ли уже вкладка браузера
        if self.browser_tab is not None:
            # Если вкладка уже существует, очищаем её содержимое
            for i in reversed(range(self.browser_tab.layout().count())):
                widget = self.browser_tab.layout().itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
        else:
            # Создаем новую вкладку браузера
            self.browser_tab = QWidget()
            layout = QVBoxLayout(self.browser_tab)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(6)

            # Добавляем вкладку в TabWidget
            self.browser_tab_index = self.tabs.addTab(
                self.browser_tab,
                get_icon("browser"),
                tr("tools.tabs.browser", "Браузер")
            )

        # Получаем действующий layout вкладки
        layout = self.browser_tab.layout()

        # Добавляем инструменты браузера
        for tool in browser_tools:
            btn = QPushButton(tool.name)
            btn.setToolTip(tool.description.strip())
            # Добавляем иконку, если она определена
            if hasattr(tool, 'icon_name') and tool.icon_name:
                btn.setIcon(get_icon(tool.icon_name))
            layout.addWidget(btn)

        # Добавляем растягивающийся элемент внизу
        layout.addStretch(1)

    def update_translations(self):
        """Обновляет переводы в интерфейсе виджета инструментов."""
        # Обновляем заголовки вкладок
        self.tabs.setTabText(0, tr("tools.general", "Основные"))
        self.tabs.setTabText(1, tr("tools.agent", "Агент"))

        # Обновляем заголовки вкладки браузера, если она существует
        if self.browser_tab is not None and self.browser_tab_index >= 0:
            self.tabs.setTabText(self.browser_tab_index, tr("tools.browser", "Браузер"))

        # Проверяем и обновляем все дочерние элементы
        self._update_general_tab_translations()
        self._update_agent_tab_translations()

        # Обновляем заголовки элементов интерфейса браузера, если они существуют
        if self.browser_tab is not None:
            self._update_browser_tab_translations()

    def _update_general_tab_translations(self):
        """Обновляет переводы в основной вкладке инструментов."""
        # Обновляем заголовки групп и элементов управления
        for widget in self.general_tab.findChildren(QGroupBox):
            title = widget.title()
            key = f"tools.general.{title.lower().replace(' ', '_')}"
            widget.setTitle(tr(key, title))

        # Обновляем метки
        for widget in self.general_tab.findChildren(QLabel):
            text = widget.text()
            if text and not text.startswith("_"):
                key = f"tools.general.{text.lower().replace(' ', '_')}"
                widget.setText(tr(key, text))

    def _update_agent_tab_translations(self):
        """Обновляет переводы в вкладке агента."""
        # Обновляем заголовки групп и элементов управления
        for widget in self.agent_tab.findChildren(QGroupBox):
            title = widget.title()
            key = f"tools.agent.{title.lower().replace(' ', '_')}"
            widget.setTitle(tr(key, title))

        # Обновляем метки
        for widget in self.agent_tab.findChildren(QLabel):
            text = widget.text()
            if text and not text.startswith("_"):
                key = f"tools.agent.{text.lower().replace(' ', '_')}"
                widget.setText(tr(key, text))

    def _update_browser_tab_translations(self):
        """Обновляет переводы в вкладке браузера."""
        # Проверяем существование вкладки
        if self.browser_tab is None:
            return

        # Обновляем заголовки групп и элементов управления
        for widget in self.browser_tab.findChildren(QGroupBox):
            title = widget.title()
            key = f"tools.browser.{title.lower().replace(' ', '_')}"
            widget.setTitle(tr(key, title))

        # Обновляем метки
        for widget in self.browser_tab.findChildren(QLabel):
            text = widget.text()
            if text and not text.startswith("_"):
                key = f"tools.browser.{text.lower().replace(' ', '_')}"
                widget.setText(tr(key, text))
