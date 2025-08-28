#!/usr/bin/env python3
"""
Unified Model Widget для GopiAI UI
Объединенный виджет для работы с моделями Gemini и OpenRouter
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QLabel, QFrame, QSplitter, QTextEdit,
    QProgressBar, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QButtonGroup, QRadioButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QIcon
from typing import cast, Iterable
from gopiai.ui.utils.icon_helpers import create_icon_button

# Добавляем путь к backend для импорта клиентов
try:
    # Пробуем разные варианты путей
    possible_paths = [
        # Вариант 1: относительно текущего файла
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "GopiAI-CrewAI",
            "tools"
        ),
        # Вариант 2: абсолютный путь
        r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\tools",
        # Вариант 3: через переменную окружения
        os.path.join(os.environ.get('GOPI_AI_MODULES', ''), "GopiAI-CrewAI", "tools")
    ]
    
    tools_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            tools_path = path
            break
    
    if tools_path and tools_path not in sys.path:
    # Заменено на использование path_manager: sys.path.append(tools_path)
        print(f"[INFO] Successfully loaded tools from: {tools_path}")
    
    # Создаем fallback enum, так как gopiai_integration был удален
    from enum import Enum
    class ModelProvider(Enum):  # type: ignore[no-redef]
        GEMINI = "gemini"
        OPENROUTER = "openrouter"
    
    MODEL_PROVIDER_AVAILABLE = False
    print("[WARNING] Using fallback ModelProvider as gopiai_integration was removed")
except Exception as e:
    # Fallback в случае других ошибок
    from enum import Enum
    class ModelProvider(Enum):  # type: ignore[no-redef]
        GEMINI = "gemini"
        OPENROUTER = "openrouter"
    MODEL_PROVIDER_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedModelWidget(QWidget):
    """Объединенный виджет для работы с моделями Gemini и OpenRouter"""
    
    # Сигналы
    model_changed = Signal(str, str)  # provider, model_id
    provider_changed = Signal(str)   # provider
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Состояние
        self.current_provider = "gemini"
        self.current_model = None
        self.available_models = {"gemini": [], "openrouter": []}
        
        # Backend клиенты
        self.model_config_manager: Optional[object] = None
        self.openrouter_client: Optional[object] = None
        
        self._setup_ui()
        self._initialize_backend_clients()
        self._setup_connections()
        self._load_current_configuration()
        
        logger.info("UnifiedModelWidget инициализирован")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("🤖 Модели ИИ")
        layout.addWidget(title_label)
        
        # Переключатель провайдеров
        provider_group = QGroupBox("Выбор провайдера")
        provider_layout = QHBoxLayout(provider_group)
        
        self.provider_button_group = QButtonGroup()
        
        self.gemini_radio = QRadioButton("🔷 Gemini")
        self.gemini_radio.setChecked(True)
        self.openrouter_radio = QRadioButton("🌐 OpenRouter")
        
        self.provider_button_group.addButton(self.gemini_radio, 0)
        self.provider_button_group.addButton(self.openrouter_radio, 1)
        
        provider_layout.addWidget(self.gemini_radio)
        provider_layout.addWidget(self.openrouter_radio)
        provider_layout.addStretch()
        
        # Статус провайдера
        self.provider_status = QLabel("Gemini активен")
        provider_layout.addWidget(self.provider_status)
        
        layout.addWidget(provider_group)
        
        # Выбор модели
        model_group = QGroupBox("Выбор модели")
        model_layout = QVBoxLayout(model_group)
        
        # Комбобокс для выбора модели
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("Модель:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        model_select_layout.addWidget(self.model_combo)
        
        # Кнопка обновления
        self.refresh_btn = create_icon_button("refresh-cw", "Обновить список моделей")
        model_select_layout.addWidget(self.refresh_btn)
        
        model_layout.addLayout(model_select_layout)
        
        # Поиск (для OpenRouter)
        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(QLabel("Поиск:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название модели...")
        self.search_layout.addWidget(self.search_input)
        
        model_layout.addLayout(self.search_layout)
        
        # Скрываем поиск по умолчанию (для Gemini)
        self.search_input.setVisible(False)
        self.search_layout.itemAt(0).widget().setVisible(False)
        
        layout.addWidget(model_group)
        
        # Информация о модели
        info_group = QGroupBox("Информация о модели")
        info_layout = QVBoxLayout(info_group)
        
        self.model_info = QTextEdit()
        self.model_info.setMaximumHeight(150)
        self.model_info.setReadOnly(True)
        info_layout.addWidget(self.model_info)
        
        layout.addWidget(info_group)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.test_connection_btn = create_icon_button("activity", "Тест соединения")
        self.reset_config_btn = create_icon_button("rotate-ccw", "Сброс настроек")
        
        buttons_layout.addWidget(self.test_connection_btn)
        buttons_layout.addWidget(self.reset_config_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
    
    def _initialize_backend_clients(self):
        """Инициализирует клиенты backend"""
        try:
            # Инициализируем заглушки, так как gopiai_integration был удален
            self.model_config_manager = None
            self.openrouter_client = None
            
            logger.warning("gopiai_integration был удален. Используются заглушки для model_config_manager и openrouter_client")
            
            # Создаем базовую реализацию для совместимости
            class DummyConfigManager:
                def get_models(self, provider=None):
                    return []
                
                def get_model_info(self, model_id):
                    return {
                        "id": model_id,
                        "name": model_id,
                        "provider": "unknown",
                        "capabilities": []
                    }
            
            class DummyOpenRouterClient:
                def get_models(self):
                    return []
                
                def get_model_info(self, model_id):
                    return {
                        "id": model_id,
                        "name": model_id,
                        "description": "Model information not available"
                    }
            
            self.model_config_manager = DummyConfigManager()
            self.openrouter_client = DummyOpenRouterClient()
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации backend клиентов: {e}")
            # Убедимся, что атрибуты определены даже в случае ошибки
            self.model_config_manager = None
            self.openrouter_client = None
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        # Переключение провайдеров
        self.provider_button_group.buttonClicked.connect(self._on_provider_changed)
        
        # Выбор модели
        self.model_combo.currentTextChanged.connect(self._on_model_selected)
        
        # Поиск (для OpenRouter)
        self.search_input.textChanged.connect(self._filter_openrouter_models)
        
        # Кнопки
        self.refresh_btn.clicked.connect(self._refresh_models)
        self.test_connection_btn.clicked.connect(self._test_connection)
        self.reset_config_btn.clicked.connect(self._reset_configuration)
    
    def _on_provider_changed(self, button):
        """Обработчик переключения провайдера"""
        if button == self.gemini_radio:
            new_provider = "gemini"
        else:
            new_provider = "openrouter"
        
        if new_provider != self.current_provider:
            self.current_provider = new_provider
            self._update_ui_for_provider()
            self._load_models_for_provider()
            self.provider_changed.emit(new_provider)
            
            logger.info(f"Переключение на провайдера: {new_provider}")
    
    def _update_ui_for_provider(self):
        """Обновляет UI в зависимости от выбранного провайдера"""
        if self.current_provider == "gemini":
            self.provider_status.setText("🔷 Gemini активен")
            self.search_input.setVisible(False)
            self.search_layout.itemAt(0).widget().setVisible(False)
        else:
            self.provider_status.setText("🌐 OpenRouter активен")
            self.search_input.setVisible(True)
            self.search_layout.itemAt(0).widget().setVisible(True)
    
    def _load_current_configuration(self):
        """Загружает текущую конфигурацию"""
        if not self.model_config_manager:
            return
        
        try:
            current_config = getattr(self.model_config_manager, "get_current_configuration")()
            
            if current_config:
                self.current_provider = current_config.provider.value
                self.current_model = current_config.model_id
                
                # Обновляем UI
                if self.current_provider == "gemini":
                    self.gemini_radio.setChecked(True)
                else:
                    self.openrouter_radio.setChecked(True)
                
                self._update_ui_for_provider()
                self._load_models_for_provider()
                
                logger.info(f"Загружена конфигурация: {current_config.display_name}")
            else:
                logger.warning("Нет активной конфигурации")
                
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
    
    def _load_models_for_provider(self):
        """Загружает модели для текущего провайдера"""
        if not self.model_config_manager:
            return
        
        try:
            self.model_combo.clear()
            
            if self.current_provider == "gemini":
                self._load_gemini_models()
            else:
                self._load_openrouter_models()
                
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей: {e}")
    
    def _load_gemini_models(self):
        """Загружает модели Gemini"""
        try:
            provider_enum = ModelProvider.GEMINI
            # Типовой хинт для pyright: model_config_manager ожидается с методом get_configurations_by_provider
            manager = self.model_config_manager
            if manager is None:
                return
            models = cast(Iterable[Any], getattr(manager, "get_configurations_by_provider")(provider_enum))  # type: ignore[call-arg]
            available_models = [m for m in models if getattr(m, "is_available", lambda: False)()]
            
            for model in available_models:
                display_name = getattr(model, "display_name", getattr(model, "model_id", "unknown"))
                display_text = f"{display_name}"
                if getattr(model, "is_default", False):
                    display_text += " (по умолчанию)"
                
                self.model_combo.addItem(display_text, getattr(model, "model_id", "unknown"))
            
            # Устанавливаем текущую модель
            if self.current_model:
                index = self.model_combo.findData(self.current_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
            
            self.available_models["gemini"] = available_models
            logger.info(f"Загружено {len(available_models)} моделей Gemini")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей Gemini: {e}")
    
    def _load_openrouter_models(self):
        """Загружает модели OpenRouter"""
        try:
            if not self.openrouter_client:
                return
            
            client = self.openrouter_client
            models = getattr(client, "get_models_sync")()
            # Приводим к списку словарей для унифицированного доступа
            normalized: List[Dict[str, Any]] = []
            for model in models:
                # Некоторые клиенты возвращают dataclass/объекты – извлекаем атрибуты
                if isinstance(model, dict):
                    data = model
                else:
                    data = {
                        'id': getattr(model, 'id', 'unknown'),
                        'name': getattr(model, 'name', getattr(model, 'id', 'unknown')),
                        'created_by': getattr(model, 'created_by', None),
                        'pricing': getattr(model, 'pricing', None),
                    }
                normalized.append(data)
                self.model_combo.addItem(str(data.get("name", data.get("id", "unknown"))), data.get("id", "unknown"))
            
            self.available_models["openrouter"] = normalized
            logger.info(f"Загружено {len(normalized)} моделей OpenRouter")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей OpenRouter: {e}")
    
    def _filter_openrouter_models(self):
        """Фильтрует модели OpenRouter по поисковому запросу"""
        if self.current_provider != "openrouter":
            return
        
        search_text = self.search_input.text().lower()
        self.model_combo.clear()
        
        models = cast(List[Dict[str, Any]], self.available_models.get("openrouter", []))
        
        for model in models:
            model_id = str(model.get('id', 'unknown'))
            model_name = str(model.get('name', model_id))
            
            if not search_text or search_text in model_name.lower() or search_text in model_id.lower():
                self.model_combo.addItem(f"{model_name}", model_id)
    
    def _on_model_selected(self):
        """Обработчик выбора модели"""
        model_id = self.model_combo.currentData()
        if model_id and model_id != self.current_model:
            try:
                if self.model_config_manager and MODEL_PROVIDER_AVAILABLE:
                    provider_enum = (
                        ModelProvider.GEMINI
                        if self.current_provider == "gemini"
                        else ModelProvider.OPENROUTER
                    )
                    
                    success = getattr(self.model_config_manager, "set_current_configuration")(  # type: ignore[call-arg]
                        provider_enum, model_id
                    )
                    
                    if success:
                        self.current_model = model_id
                        self._update_model_info()
                        self.model_changed.emit(self.current_provider, model_id)
                        
                        logger.info(f"Выбрана модель: {self.current_provider}/{model_id}")
                    else:
                        logger.warning(f"Не удалось установить модель: {model_id}")
                        
            except Exception as e:
                logger.error(f"Ошибка выбора модели: {e}")
    
    def _update_model_info(self):
        """Обновляет информацию о выбранной модели"""
        if not self.current_model:
            self.model_info.setText("Модель не выбрана")
            return
        
        try:
            info_text = f"🤖 Провайдер: {self.current_provider.title()}\n"
            info_text += f"📋 ID модели: {self.current_model}\n"
            info_text += f"⏰ Обновлено: {datetime.now().strftime('%H:%M:%S')}\n"
            
            if self.current_provider == "openrouter":
                # Дополнительная информация для OpenRouter
                models = cast(List[Dict[str, Any]], self.available_models.get("openrouter", []))
                current_model_data = next((m for m in models if m.get('id') == self.current_model), None)
                
                if current_model_data:
                    info_text += f"📝 Название: {current_model_data.get('name', 'N/A')}\n"
                    info_text += f"🏢 Создатель: {current_model_data.get('created_by', 'N/A')}\n"
                    
                    pricing = cast(Dict[str, Any], current_model_data.get('pricing', {}))
                    if pricing:
                        prompt_cost = pricing.get('prompt', 'N/A')
                        completion_cost = pricing.get('completion', 'N/A')
                        info_text += f"💰 Стоимость: {prompt_cost}/{completion_cost} за токен\n"
            
            self.model_info.setText(info_text)
            
        except Exception as e:
            logger.error(f"Ошибка обновления информации о модели: {e}")
            self.model_info.setText(f"Ошибка: {e}")
    
    def _refresh_models(self):
        """Обновляет список моделей"""
        self._load_models_for_provider()
        logger.info(f"Модели для {self.current_provider} обновлены")
    
    def _test_connection(self):
        """Тестирует соединение с выбранным провайдером"""
        logger.info(f"Тест соединения с {self.current_provider}")

        success = False
        message = ""

        try:
            if self.current_provider == "openrouter":
                if self.openrouter_client:
                    # Пробуем получить модели как тест
                    getattr(self.openrouter_client, "get_models_sync")()
                    success = True
                    message = "Соединение с OpenRouter успешно установлено!"
                else:
                    message = "Клиент OpenRouter не инициализирован."
            else:  # gemini
                if self.model_config_manager:
                    # Пробуем получить конфигурации как тест
                    provider_enum = ModelProvider.GEMINI
                    getattr(self.model_config_manager, "get_configurations_by_provider")(provider_enum)
                    success = True
                    message = "Соединение с Gemini (через конфигурацию) успешно!"
                else:
                    message = "Менеджер конфигураций не инициализирован."

        except Exception as e:
            logger.error(f"Ошибка теста соединения: {e}")
            message = f"Ошибка: {e}"

        # Показываем результат
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Результат теста")
        msg_box.setText(message)
        if success:
            msg_box.setIcon(QMessageBox.Information)
        else:
            msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec()
    
    def _reset_configuration(self):
        """Сбрасывает конфигурацию к настройкам по умолчанию"""
        logger.info("Сброс конфигурации к настройкам по умолчанию")

        success = False
        message = ""

        try:
            if self.model_config_manager:
                if getattr(self.model_config_manager, "set_default_configuration")():
                    success = True
                    message = "Конфигурация успешно сброшена к настройкам по умолчанию."
                    # Перезагружаем UI, чтобы отразить изменения
                    self._load_current_configuration()
                else:
                    message = "Не удалось сбросить конфигурацию."
            else:
                message = "Менеджер конфигураций не инициализирован."

        except Exception as e:
            logger.error(f"Ошибка сброса конфигурации: {e}")
            message = f"Ошибка: {e}"

        # Показываем результат
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Результат сброса")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        msg_box.exec()
    
    def get_current_model(self):
        """Возвращает текущую выбранную модель"""
        return {
            'provider': self.current_provider,
            'model_id': self.current_model
        }
    
    def set_model_by_id(self, provider: str, model_id: str):
        """Устанавливает модель по ID"""
        if provider != self.current_provider:
            self.current_provider = provider
            if provider == "gemini":
                self.gemini_radio.setChecked(True)
            else:
                self.openrouter_radio.setChecked(True)
            self._update_ui_for_provider()
            self._load_models_for_provider()
        
        # Устанавливаем модель
        index = self.model_combo.findData(model_id)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)


def test_unified_widget():
    """Тестовая функция для объединенного виджета"""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG)
    
    # Создаем и настраиваем виджет
    widget = UnifiedModelWidget()
    widget.setWindowTitle("Unified Model Widget Test (gopiai_integration removed)")
    widget.resize(800, 600)
    widget.show()
    
    # Выводим предупреждение о том, что функциональность ограничена
    print("\n" + "="*80)
    print("ВНИМАНИЕ: gopiai_integration был удален. Используется ограниченный функционал.")
    print("="*80 + "\n")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    test_unified_widget()