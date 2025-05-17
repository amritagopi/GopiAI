import os

import toml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config import config
from app.config.reasoning_config import ReasoningStrategy
from app.ui.i18n.translator import JsonTranslationManager, tr
from app.ui.icon_adapter import get_icon


class SettingsWidget(QWidget):
    """
    Виджет для отображения и редактирования основных настроек приложения GopiAI.
    Реализованы секции LLM, Browser и Reasoning.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("settings.dialog.title", "Настройки GopiAI"))
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.layout.addLayout(self.form)
        # LLM
        self.llm_model_edit = QLineEdit()
        self.llm_model_edit.setToolTip(
            self.tr("settings.llm.model.tooltip", "Название LLM модели")
        )
        self.llm_model_edit.setPlaceholderText(
            self.tr("settings.llm.model.placeholder", "Введите название модели")
        )
        self.llm_api_key_edit = QLineEdit()
        self.llm_api_key_edit.setEchoMode(QLineEdit.Password)
        self.llm_api_key_edit.setToolTip(
            self.tr("settings.llm.api_key.tooltip", "API ключ для LLM")
        )
        self.llm_api_key_edit.setPlaceholderText(
            self.tr("settings.llm.api_key.placeholder", "Введите API ключ")
        )
        self.llm_temperature_edit = QLineEdit()
        self.llm_temperature_edit.setToolTip(
            self.tr("settings.llm.temperature.tooltip", "Температура выборки (0-2.0)")
        )
        self.llm_temperature_edit.setPlaceholderText(
            self.tr("settings.llm.temperature.placeholder", "Например: 0.7")
        )
        self.llm_max_tokens_edit = QLineEdit()
        self.llm_max_tokens_edit.setToolTip(
            self.tr(
                "settings.llm.max_tokens.tooltip", "Максимальное количество токенов"
            )
        )
        self.llm_max_tokens_edit.setPlaceholderText(
            self.tr("settings.llm.max_tokens.placeholder", "Например: 2048")
        )
        self.form.addRow(
            QLabel(self.tr("settings.llm.model", "LLM модель:")), self.llm_model_edit
        )
        self.form.addRow(
            QLabel(self.tr("settings.llm.api_key", "LLM API ключ:")),
            self.llm_api_key_edit,
        )
        self.form.addRow(
            QLabel(self.tr("settings.llm.temperature", "Температура:")),
            self.llm_temperature_edit,
        )
        self.form.addRow(
            QLabel(self.tr("settings.llm.max_tokens", "Макс. токенов:")),
            self.llm_max_tokens_edit,
        )
        # Browser
        self.browser_headless = QCheckBox(
            self.tr("settings.browser.headless", "Headless режим")
        )
        self.browser_headless.setToolTip(
            self.tr(
                "settings.browser.headless.tooltip", "Запускать браузер без интерфейса"
            )
        )
        self.browser_disable_security = QCheckBox(
            self.tr("settings.browser.disable_security", "Отключить безопасность")
        )
        self.browser_disable_security.setToolTip(
            self.tr(
                "settings.browser.disable_security.tooltip", "Отключить защиту браузера"
            )
        )
        self.browser_chrome_path = QLineEdit()
        self.browser_chrome_path.setToolTip(
            self.tr(
                "settings.browser.chrome_path.tooltip",
                "Путь к исполняемому файлу Chrome",
            )
        )
        self.browser_chrome_path.setPlaceholderText(
            self.tr(
                "settings.browser.chrome_path.placeholder",
                "Например: C:/Program Files/Google/Chrome/Application/chrome.exe",
            )
        )
        self.browser_proxy_server = QLineEdit()
        self.browser_proxy_server.setToolTip(
            self.tr("settings.browser.proxy_server.tooltip", "Адрес прокси сервера")
        )
        self.browser_proxy_server.setPlaceholderText(
            self.tr(
                "settings.browser.proxy_server.placeholder", "proxy.example.com:8080"
            )
        )
        self.browser_proxy_username = QLineEdit()
        self.browser_proxy_username.setToolTip(
            self.tr(
                "settings.browser.proxy_username.tooltip", "Имя пользователя для прокси"
            )
        )
        self.browser_proxy_username.setPlaceholderText(
            self.tr(
                "settings.browser.proxy_username.placeholder",
                "Введите имя пользователя",
            )
        )
        self.browser_proxy_password = QLineEdit()
        self.browser_proxy_password.setEchoMode(QLineEdit.Password)
        self.browser_proxy_password.setToolTip(
            self.tr("settings.browser.proxy_password.tooltip", "Пароль для прокси")
        )
        self.browser_proxy_password.setPlaceholderText(
            self.tr("settings.browser.proxy_password.placeholder", "Введите пароль")
        )
        self.form.addRow(
            QLabel(self.tr("settings.browser.headless", "Браузер: Headless")),
            self.browser_headless,
        )
        self.form.addRow(
            QLabel(
                self.tr(
                    "settings.browser.disable_security",
                    "Браузер: Отключить безопасность",
                )
            ),
            self.browser_disable_security,
        )
        self.form.addRow(
            QLabel(self.tr("settings.browser.chrome_path", "Путь к Chrome")),
            self.browser_chrome_path,
        )
        self.form.addRow(
            QLabel(self.tr("settings.browser.proxy_server", "Прокси сервер")),
            self.browser_proxy_server,
        )
        self.form.addRow(
            QLabel(self.tr("settings.browser.proxy_username", "Прокси пользователь")),
            self.browser_proxy_username,
        )
        self.form.addRow(
            QLabel(self.tr("settings.browser.proxy_password", "Прокси пароль")),
            self.browser_proxy_password,
        )

        # Reasoning Settings
        self._setup_reasoning_settings()

        self.save_btn = QPushButton(self.tr("settings.save", "Сохранить"))
        self.save_btn.setIcon(get_icon("save"))
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)
        self.load_settings()
        self.retranslateUi()
        JsonTranslationManager.instance().languageChanged.connect(self.retranslateUi)
        self.setLayout(self.layout)

    def _setup_reasoning_settings(self):
        """Настраивает элементы управления для настроек reasoning"""
        # Заголовок секции
        reasoning_label = QLabel(
            self.tr("settings.reasoning.title", "Настройки рассуждений (Reasoning)")
        )
        reasoning_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.form.addRow(reasoning_label)

        # Глубина рассуждений (слайдер)
        self.reasoning_depth_slider = QSlider(Qt.Horizontal)
        self.reasoning_depth_slider.setMinimum(3)
        self.reasoning_depth_slider.setMaximum(15)
        self.reasoning_depth_slider.setValue(7)
        self.reasoning_depth_slider.setTickInterval(1)
        self.reasoning_depth_slider.setTickPosition(QSlider.TicksBelow)
        self.reasoning_depth_slider.setToolTip(
            self.tr(
                "settings.reasoning.depth.tooltip",
                "Количество шагов в цепочке рассуждений",
            )
        )

        # Добавляем спинбокс для отображения текущего значения
        self.reasoning_depth_spinbox = QSpinBox()
        self.reasoning_depth_spinbox.setMinimum(3)
        self.reasoning_depth_spinbox.setMaximum(15)
        self.reasoning_depth_spinbox.setValue(7)

        # Связываем слайдер и спинбокс
        self.reasoning_depth_slider.valueChanged.connect(
            self.reasoning_depth_spinbox.setValue
        )
        self.reasoning_depth_spinbox.valueChanged.connect(
            self.reasoning_depth_slider.setValue
        )

        # Создаем горизонтальный лейаут для слайдера и спинбокса
        depth_layout = QVBoxLayout()
        depth_layout.addWidget(self.reasoning_depth_slider)
        depth_layout.addWidget(self.reasoning_depth_spinbox)
        depth_widget = QWidget()
        depth_widget.setLayout(depth_layout)

        # Стратегия рассуждений (комбобокс)
        self.reasoning_strategy_combo = QComboBox()
        self.reasoning_strategy_combo.addItem(
            self.tr("settings.reasoning.strategy.sequential", "Последовательная"),
            ReasoningStrategy.SEQUENTIAL.value,
        )
        self.reasoning_strategy_combo.addItem(
            self.tr("settings.reasoning.strategy.tree", "Древовидная"),
            ReasoningStrategy.TREE.value,
        )
        self.reasoning_strategy_combo.addItem(
            self.tr("settings.reasoning.strategy.adaptive", "Адаптивная"),
            ReasoningStrategy.ADAPTIVE.value,
        )
        self.reasoning_strategy_combo.setToolTip(
            self.tr(
                "settings.reasoning.strategy.tooltip",
                "Стратегия построения цепочки рассуждений",
            )
        )

        # Флажки настроек
        self.reasoning_detailed_logging = QCheckBox(
            self.tr("settings.reasoning.detailed_logging", "Подробное логирование")
        )
        self.reasoning_detailed_logging.setToolTip(
            self.tr(
                "settings.reasoning.detailed_logging.tooltip",
                "Включить подробное логирование всех шагов рассуждений",
            )
        )

        self.reasoning_monitoring = QCheckBox(
            self.tr("settings.reasoning.monitoring", "Мониторинг выполнения")
        )
        self.reasoning_monitoring.setToolTip(
            self.tr(
                "settings.reasoning.monitoring.tooltip",
                "Включить мониторинг выполнения плана действий",
            )
        )

        self.reasoning_interactive_mode = QCheckBox(
            self.tr("settings.reasoning.interactive_mode", "Интерактивный режим")
        )
        self.reasoning_interactive_mode.setToolTip(
            self.tr(
                "settings.reasoning.interactive_mode.tooltip",
                "Требовать подтверждение для каждого шага плана",
            )
        )

        self.reasoning_safe_mode = QCheckBox(
            self.tr("settings.reasoning.safe_mode", "Безопасный режим")
        )
        self.reasoning_safe_mode.setToolTip(
            self.tr(
                "settings.reasoning.safe_mode.tooltip",
                "Включить проверки безопасности операций",
            )
        )

        # Таймаут операций
        self.reasoning_timeout_spinbox = QSpinBox()
        self.reasoning_timeout_spinbox.setMinimum(5)
        self.reasoning_timeout_spinbox.setMaximum(300)
        self.reasoning_timeout_spinbox.setValue(30)
        self.reasoning_timeout_spinbox.setSuffix(" сек")
        self.reasoning_timeout_spinbox.setToolTip(
            self.tr(
                "settings.reasoning.timeout.tooltip",
                "Максимальное время выполнения операции в секундах",
            )
        )

        # Добавляем все элементы управления в форму
        self.form.addRow(
            self.tr("settings.reasoning.depth", "Глубина рассуждений:"), depth_widget
        )
        self.form.addRow(
            self.tr("settings.reasoning.strategy", "Стратегия:"),
            self.reasoning_strategy_combo,
        )
        self.form.addRow(
            self.tr("settings.reasoning.detailed_logging", "Подробное логирование:"),
            self.reasoning_detailed_logging,
        )
        self.form.addRow(
            self.tr("settings.reasoning.monitoring", "Мониторинг выполнения:"),
            self.reasoning_monitoring,
        )
        self.form.addRow(
            self.tr("settings.reasoning.interactive_mode", "Интерактивный режим:"),
            self.reasoning_interactive_mode,
        )
        self.form.addRow(
            self.tr("settings.reasoning.safe_mode", "Безопасный режим:"),
            self.reasoning_safe_mode,
        )
        self.form.addRow(
            self.tr("settings.reasoning.timeout", "Таймаут операций:"),
            self.reasoning_timeout_spinbox,
        )

    def load_settings(self):
        llm = config.llm.get("default", {})
        self.llm_model_edit.setText(str(llm.get("model", "")))
        self.llm_api_key_edit.setText(str(llm.get("api_key", "")))
        self.llm_temperature_edit.setText(str(llm.get("temperature", "")))
        self.llm_max_tokens_edit.setText(str(llm.get("max_tokens", "")))
        browser = config.browser_config
        if browser:
            self.browser_headless.setChecked(getattr(browser, "headless", False))
            self.browser_disable_security.setChecked(
                getattr(browser, "disable_security", True)
            )
            self.browser_chrome_path.setText(
                str(getattr(browser, "chrome_instance_path", ""))
            )
            proxy = getattr(browser, "proxy", None)
            if proxy:
                self.browser_proxy_server.setText(str(getattr(proxy, "server", "")))
                self.browser_proxy_username.setText(str(getattr(proxy, "username", "")))
                self.browser_proxy_password.setText(str(getattr(proxy, "password", "")))
            else:
                self.browser_proxy_server.setText("")
                self.browser_proxy_username.setText("")
                self.browser_proxy_password.setText("")
        else:
            self.browser_headless.setChecked(False)
            self.browser_disable_security.setChecked(True)
            self.browser_chrome_path.setText("")
            self.browser_proxy_server.setText("")
            self.browser_proxy_username.setText("")
            self.browser_proxy_password.setText("")

        # Загрузка настроек reasoning
        reasoning = config.reasoning_config
        if reasoning:
            self.reasoning_depth_slider.setValue(reasoning.reasoning_depth)
            self.reasoning_depth_spinbox.setValue(reasoning.reasoning_depth)

            # Устанавливаем стратегию в комбобоксе
            strategy_index = 0
            for i in range(self.reasoning_strategy_combo.count()):
                if (
                    self.reasoning_strategy_combo.itemData(i)
                    == reasoning.reasoning_strategy.value
                ):
                    strategy_index = i
                    break
            self.reasoning_strategy_combo.setCurrentIndex(strategy_index)

            self.reasoning_detailed_logging.setChecked(reasoning.detailed_logging)
            self.reasoning_monitoring.setChecked(reasoning.monitoring_enabled)
            self.reasoning_interactive_mode.setChecked(reasoning.interactive_mode)
            self.reasoning_safe_mode.setChecked(reasoning.safe_mode)
            self.reasoning_timeout_spinbox.setValue(reasoning.operation_timeout)

    def save_settings(self):
        model = self.llm_model_edit.text().strip()
        api_key = self.llm_api_key_edit.text().strip()
        temperature = self.llm_temperature_edit.text().strip()
        max_tokens = self.llm_max_tokens_edit.text().strip()
        if not model or not api_key:
            QMessageBox.warning(
                self,
                self.tr("dialogs.warning.title", "Ошибка"),
                self.tr(
                    "settings.llm.empty_fields", "Поля LLM не должны быть пустыми!"
                ),
            )
            return
        try:
            temp_val = float(temperature)
            if not (0.0 <= temp_val <= 2.0):
                raise ValueError
        except Exception:
            QMessageBox.warning(
                self,
                self.tr("dialogs.warning.title", "Ошибка"),
                self.tr(
                    "settings.llm.temperature_invalid",
                    "Температура должна быть числом от 0 до 2!",
                ),
            )
            return
        try:
            max_tokens_val = int(max_tokens)
            if max_tokens_val <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(
                self,
                self.tr("dialogs.warning.title", "Ошибка"),
                self.tr(
                    "settings.llm.max_tokens_invalid",
                    "Максимальное число токенов должно быть положительным целым!",
                ),
            )
            return
        headless = self.browser_headless.isChecked()
        disable_security = self.browser_disable_security.isChecked()
        chrome_path = self.browser_chrome_path.text().strip()
        proxy_server = self.browser_proxy_server.text().strip()
        proxy_username = self.browser_proxy_username.text().strip()
        proxy_password = self.browser_proxy_password.text().strip()
        if not headless and not chrome_path:
            QMessageBox.warning(
                self,
                self.tr("dialogs.warning.title", "Ошибка"),
                self.tr(
                    "settings.browser.chrome_path_required",
                    "Путь к Chrome обязателен, если headless выключен!",
                ),
            )
            return

        # Получаем настройки reasoning
        reasoning_depth = self.reasoning_depth_spinbox.value()
        reasoning_strategy = self.reasoning_strategy_combo.currentData()
        reasoning_detailed_logging = self.reasoning_detailed_logging.isChecked()
        reasoning_monitoring = self.reasoning_monitoring.isChecked()
        reasoning_interactive_mode = self.reasoning_interactive_mode.isChecked()
        reasoning_safe_mode = self.reasoning_safe_mode.isChecked()
        reasoning_timeout = self.reasoning_timeout_spinbox.value()

        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.toml",
        )
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    data = toml.load(f)
            else:
                data = {}
            data.setdefault("llm", {})
            data["llm"]["model"] = model
            data["llm"]["api_key"] = api_key
            data["llm"]["temperature"] = float(temperature)
            data["llm"]["max_tokens"] = int(max_tokens)
            data.setdefault("browser", {})
            data["browser"]["headless"] = headless
            data["browser"]["disable_security"] = disable_security
            data["browser"]["chrome_instance_path"] = chrome_path
            if proxy_server or proxy_username or proxy_password:
                data["browser"].setdefault("proxy", {})
                data["browser"]["proxy"]["server"] = proxy_server
                data["browser"]["proxy"]["username"] = proxy_username
                data["browser"]["proxy"]["password"] = proxy_password
            else:
                if "proxy" in data["browser"]:
                    data["browser"]["proxy"] = {
                        "server": "",
                        "username": "",
                        "password": "",
                    }

            # Сохраняем настройки reasoning
            data.setdefault("reasoning", {})
            data["reasoning"]["reasoning_depth"] = reasoning_depth
            data["reasoning"]["reasoning_strategy"] = reasoning_strategy
            data["reasoning"]["detailed_logging"] = reasoning_detailed_logging
            data["reasoning"]["monitoring_enabled"] = reasoning_monitoring
            data["reasoning"]["interactive_mode"] = reasoning_interactive_mode
            data["reasoning"]["safe_mode"] = reasoning_safe_mode
            data["reasoning"]["operation_timeout"] = reasoning_timeout

            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(data, f)

            # Обновляем текущую конфигурацию
            if "default" not in config.llm:
                config.llm["default"] = {}
            config.llm["default"].model = model
            config.llm["default"].api_key = api_key
            config.llm["default"].temperature = float(temperature)
            config.llm["default"].max_tokens = int(max_tokens)

            if not config.browser_config:
                config.browser_config = {}
            config.browser_config.headless = headless
            config.browser_config.disable_security = disable_security
            config.browser_config.chrome_instance_path = chrome_path

            if proxy_server or proxy_username or proxy_password:
                if not config.browser_config.proxy:
                    config.browser_config.proxy = {}
                config.browser_config.proxy.server = proxy_server
                config.browser_config.proxy.username = proxy_username
                config.browser_config.proxy.password = proxy_password

            # Обновляем настройки reasoning
            config.reasoning_config.reasoning_depth = reasoning_depth
            config.reasoning_config.reasoning_strategy = ReasoningStrategy(
                reasoning_strategy
            )
            config.reasoning_config.detailed_logging = reasoning_detailed_logging
            config.reasoning_config.monitoring_enabled = reasoning_monitoring
            config.reasoning_config.interactive_mode = reasoning_interactive_mode
            config.reasoning_config.safe_mode = reasoning_safe_mode
            config.reasoning_config.operation_timeout = reasoning_timeout

            QMessageBox.information(
                self,
                self.tr("dialogs.info.title", "Настройки"),
                self.tr(
                    "settings.applied_message",
                    "Настройки успешно сохранены в config.toml!",
                ),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("dialogs.error.title", "Ошибка"),
                self.tr(
                    "settings.apply_error", "Ошибка при сохранении настроек: {error}"
                ).format(error=e),
            )

    def retranslateUi(self):
        self.setWindowTitle(self.tr("settings.dialog.title", "Настройки GopiAI"))
        # LLM
        self.form.labelForField(self.llm_model_edit).setText(
            self.tr("settings.llm.model", "LLM модель:")
        )
        self.llm_model_edit.setToolTip(
            self.tr("settings.llm.model.tooltip", "Название LLM модели")
        )
        self.form.labelForField(self.llm_api_key_edit).setText(
            self.tr("settings.llm.api_key", "LLM API ключ:")
        )
        self.llm_api_key_edit.setToolTip(
            self.tr("settings.llm.api_key.tooltip", "API ключ для LLM")
        )
        self.form.labelForField(self.llm_temperature_edit).setText(
            self.tr("settings.llm.temperature", "Температура:")
        )
        self.llm_temperature_edit.setToolTip(
            self.tr("settings.llm.temperature.tooltip", "Температура выборки (0-2.0)")
        )
        self.form.labelForField(self.llm_max_tokens_edit).setText(
            self.tr("settings.llm.max_tokens", "Макс. токенов:")
        )
        self.llm_max_tokens_edit.setToolTip(
            self.tr(
                "settings.llm.max_tokens.tooltip", "Максимальное количество токенов"
            )
        )
        # Browser
        self.form.labelForField(self.browser_headless).setText(
            self.tr("settings.browser.headless", "Браузер: Headless")
        )
        self.browser_headless.setText(
            self.tr("settings.browser.headless", "Headless режим")
        )
        self.browser_headless.setToolTip(
            self.tr(
                "settings.browser.headless.tooltip", "Запускать браузер без интерфейса"
            )
        )
        self.form.labelForField(self.browser_disable_security).setText(
            self.tr(
                "settings.browser.disable_security", "Браузер: Отключить безопасность"
            )
        )
        self.browser_disable_security.setText(
            self.tr("settings.browser.disable_security", "Отключить безопасность")
        )
        self.browser_disable_security.setToolTip(
            self.tr(
                "settings.browser.disable_security.tooltip", "Отключить защиту браузера"
            )
        )
        self.form.labelForField(self.browser_chrome_path).setText(
            self.tr("settings.browser.chrome_path", "Путь к Chrome")
        )
        self.browser_chrome_path.setToolTip(
            self.tr(
                "settings.browser.chrome_path.tooltip",
                "Путь к исполняемому файлу Chrome",
            )
        )
        self.form.labelForField(self.browser_proxy_server).setText(
            self.tr("settings.browser.proxy_server", "Прокси сервер")
        )
        self.browser_proxy_server.setToolTip(
            self.tr("settings.browser.proxy_server.tooltip", "Адрес прокси сервера")
        )
        self.form.labelForField(self.browser_proxy_username).setText(
            self.tr("settings.browser.proxy_username", "Прокси пользователь")
        )
        self.browser_proxy_username.setToolTip(
            self.tr(
                "settings.browser.proxy_username.tooltip", "Имя пользователя для прокси"
            )
        )
        self.form.labelForField(self.browser_proxy_password).setText(
            self.tr("settings.browser.proxy_password", "Прокси пароль")
        )
        self.browser_proxy_password.setToolTip(
            self.tr("settings.browser.proxy_password.tooltip", "Пароль для прокси")
        )
        # Reasoning
        try:
            # Получаем лейбл заголовка секции Reasoning
            form_items = [
                (self.form.itemAt(i).widget())
                for i in range(self.form.count())
                if isinstance(self.form.itemAt(i).widget(), QLabel)
            ]
            reasoning_label = next(
                (label for label in form_items if "Reasoning" in label.text()), None
            )
            if reasoning_label:
                reasoning_label.setText(
                    self.tr(
                        "settings.reasoning.title", "Настройки рассуждений (Reasoning)"
                    )
                )

            # Обновляем надписи полей Reasoning
            self.form.labelForField(self.reasoning_depth_slider.parent()).setText(
                self.tr("settings.reasoning.depth", "Глубина рассуждений:")
            )
            self.reasoning_depth_slider.setToolTip(
                self.tr(
                    "settings.reasoning.depth.tooltip",
                    "Количество шагов в цепочке рассуждений",
                )
            )

            self.form.labelForField(self.reasoning_strategy_combo).setText(
                self.tr("settings.reasoning.strategy", "Стратегия:")
            )
            self.reasoning_strategy_combo.setToolTip(
                self.tr(
                    "settings.reasoning.strategy.tooltip",
                    "Стратегия построения цепочки рассуждений",
                )
            )

            # Обновляем элементы комбобокса
            self.reasoning_strategy_combo.setItemText(
                0, self.tr("settings.reasoning.strategy.sequential", "Последовательная")
            )
            self.reasoning_strategy_combo.setItemText(
                1, self.tr("settings.reasoning.strategy.tree", "Древовидная")
            )
            self.reasoning_strategy_combo.setItemText(
                2, self.tr("settings.reasoning.strategy.adaptive", "Адаптивная")
            )

            self.form.labelForField(self.reasoning_detailed_logging).setText(
                self.tr("settings.reasoning.detailed_logging", "Подробное логирование:")
            )
            self.reasoning_detailed_logging.setText(
                self.tr("settings.reasoning.detailed_logging", "Подробное логирование")
            )
            self.reasoning_detailed_logging.setToolTip(
                self.tr(
                    "settings.reasoning.detailed_logging.tooltip",
                    "Включить подробное логирование всех шагов рассуждений",
                )
            )

            self.form.labelForField(self.reasoning_monitoring).setText(
                self.tr("settings.reasoning.monitoring", "Мониторинг выполнения:")
            )
            self.reasoning_monitoring.setText(
                self.tr("settings.reasoning.monitoring", "Мониторинг выполнения")
            )
            self.reasoning_monitoring.setToolTip(
                self.tr(
                    "settings.reasoning.monitoring.tooltip",
                    "Включить мониторинг выполнения плана действий",
                )
            )

            self.form.labelForField(self.reasoning_interactive_mode).setText(
                self.tr("settings.reasoning.interactive_mode", "Интерактивный режим:")
            )
            self.reasoning_interactive_mode.setText(
                self.tr("settings.reasoning.interactive_mode", "Интерактивный режим")
            )
            self.reasoning_interactive_mode.setToolTip(
                self.tr(
                    "settings.reasoning.interactive_mode.tooltip",
                    "Требовать подтверждение для каждого шага плана",
                )
            )

            self.form.labelForField(self.reasoning_safe_mode).setText(
                self.tr("settings.reasoning.safe_mode", "Безопасный режим:")
            )
            self.reasoning_safe_mode.setText(
                self.tr("settings.reasoning.safe_mode", "Безопасный режим")
            )
            self.reasoning_safe_mode.setToolTip(
                self.tr(
                    "settings.reasoning.safe_mode.tooltip",
                    "Включить проверки безопасности операций",
                )
            )

            self.form.labelForField(self.reasoning_timeout_spinbox).setText(
                self.tr("settings.reasoning.timeout", "Таймаут операций:")
            )
            self.reasoning_timeout_spinbox.setToolTip(
                self.tr(
                    "settings.reasoning.timeout.tooltip",
                    "Максимальное время выполнения операции в секундах",
                )
            )
        except Exception as e:
            print(f"Ошибка при переводе настроек reasoning: {e}")

        self.save_btn.setText(self.tr("settings.save", "Сохранить"))
