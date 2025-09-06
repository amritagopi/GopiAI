#!/usr/bin/env python3
"""
Unified Models Tab для GopiAI UI
Вкладка управления моделями Gemini с поддержкой ротации и выбора пользователя
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import Signal
import os
import json
import requests
import time
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer

# Импорт системы иконок
try:
    from ..components.icon_file_system_model import UniversalIconManager
    icon_manager = UniversalIconManager.instance()
except ImportError:
    icon_manager = None

# Импорт системы ротации моделей
try:
    import sys
    import os
    # Добавляем путь к CrewAI модулю для импорта llm_rotation_config
    from pathlib import Path
    current_file = Path(__file__)
    crewai_path = str(current_file.parents[3] / 'GopiAI-CrewAI')
    if crewai_path not in sys.path:
        sys.path.insert(0, crewai_path)
    from llm_rotation_config import get_next_available_model, register_use, get_model_usage_stats, MODELS as ROTATION_MODELS
    rotation_system_available = True
except ImportError as e:
    print(f"Warning: Could not import rotation system: {e}")
    rotation_system_available = False

# Доступные модели Gemini (основано на free-models-rate-limits данных и llm_rotation_config.py)
GEMINI_MODELS = [
    # Новейшие модели Gemini 2.5
    {"id": "gemini/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "description": "Самая мощная модель для сложных задач", "priority": 1},
    {"id": "gemini/gemini-2.5-flash", "name": "Gemini 2.5 Flash", "description": "Быстрая модель с гибридным рассуждением", "priority": 2},
    {"id": "gemini/gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash-Lite", "description": "Самая экономичная модель для высоких объемов", "priority": 3},
    
    # Модели Gemini 2.0 
    {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Сбалансированная мультимодальная модель для агентов", "priority": 4},
    {"id": "gemini/gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash-Lite", "description": "Компактная модель для высокопроизводительных задач", "priority": 5},
    
    # Проверенные модели Gemini 1.5
    {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Быстрая мультимодальная модель с окном 1M токенов", "priority": 6},
    {"id": "gemini/gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash-8B", "description": "Компактная модель для простых задач", "priority": 7},
    {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Высокоинтеллектуальная модель с окном 2M токенов", "priority": 8},
    
    # Открытые модели Gemma
    {"id": "gemma-3", "name": "Gemma 3", "description": "Легковесная открытая модель на базе технологий Gemini", "priority": 9},
    {"id": "gemma-3n", "name": "Gemma 3n", "description": "Открытая модель для мобильных устройств", "priority": 10},
]

logger = logging.getLogger(__name__)

class UnifiedModelsTab(QWidget):
    """Вкладка управления моделями Gemini

    Поддерживает автоматическую ротацию моделей и ручной выбор пользователем.
    Синхронизирует состояние с CrewAI API сервером через POST /internal/state.
    """
    
    # Сигналы
    model_changed = Signal(str, str)  # provider, model_id
    rotation_changed = Signal(bool)  # rotation_enabled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_provider = "gemini"  # Всегда Gemini
        self.current_model = "gemini/gemini-2.5-flash"  # Модель по умолчанию - лучшая из новых
        self.rotation_enabled = True  # Ротация включена по умолчанию
        
        # Таймер для автоматического обновления модели при ротации
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self._check_rotation_update)
        self.rotation_timer.setInterval(60000)  # Проверяем каждую минуту
        
        self._setup_ui()
        self._setup_connections()
        
        # Запускаем таймер ротации если система доступна
        if rotation_system_available and self.rotation_enabled:
            self.rotation_timer.start()
        
        logger.info("UnifiedModelsTab инициализирован")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Модели Gemini")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Группа управления ротацией
        rotation_group = QGroupBox("Режим работы")
        rotation_layout = QVBoxLayout(rotation_group)
        
        # Чекбокс для включения/отключения ротации
        self.rotation_checkbox = QCheckBox("Автоматическая ротация моделей")
        self.rotation_checkbox.setChecked(True)
        self.rotation_checkbox.setToolTip("При включении система автоматически переключает между моделями для оптимальной производительности")
        rotation_layout.addWidget(self.rotation_checkbox)
        
        # Информация о ротации
        rotation_info = QLabel("• При ротации система автоматически выбирает лучшую модель\n• Отключите для ручного выбора модели")
        rotation_info.setWordWrap(True)
        rotation_info.setStyleSheet("color: gray; font-size: 10px;")
        rotation_layout.addWidget(rotation_info)
        
        layout.addWidget(rotation_group)
        
        # Группа выбора модели
        model_group = QGroupBox("Выбор модели")
        model_layout = QVBoxLayout(model_group)
        
        # Комбобокс для выбора модели
        model_label = QLabel("Модель Gemini:")
        model_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        for model in GEMINI_MODELS:
            self.model_combo.addItem(f"{model['name']} - {model['description']}", model['id'])
        
        # Устанавливаем модель по умолчанию
        default_index = next((i for i, model in enumerate(GEMINI_MODELS) if model['id'] == self.current_model), 0)
        self.model_combo.setCurrentIndex(default_index)
        
        model_layout.addWidget(self.model_combo)
        
        # Информация о выбранной модели
        self.model_info_label = QLabel()
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet("color: gray; font-size: 10px;")
        model_layout.addWidget(self.model_info_label)
        
        layout.addWidget(model_group)
        
        # Статус
        self.status_label = QLabel("Статус: Активен (Gemini)")
        status_font = QFont()
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Обновляем информацию о модели
        self._update_model_info()
    
    def _update_model_info(self):
        """Обновляет информацию о выбранной модели"""
        current_model_id = self.model_combo.currentData()
        model_info = next((model for model in GEMINI_MODELS if model['id'] == current_model_id), None)
        
        if model_info:
            info_lines = []
            
            if self.rotation_enabled:
                info_lines.append(f"Текущая модель: {model_info['name']}")
                info_lines.append("Ротация: Включена (автоматический выбор лучшей модели)")
            else:
                info_lines.append(f"Выбрана модель: {model_info['name']}")
                info_lines.append("Ротация: Отключена (модель зафиксирована)")
            
            # Добавляем статистику использования если доступна система ротации
            if rotation_system_available:
                try:
                    stats = get_model_usage_stats(current_model_id)
                    if stats:
                        info_lines.append(f"Использование: {stats.get('rpm', 0)} зап/мин, {stats.get('rpd', 0)} зап/день")
                        if stats.get('blacklisted', False):
                            info_lines.append("⚠️ Модель временно заблокирована")
                except Exception as e:
                    logger.debug(f"Не удалось получить статистику для {current_model_id}: {e}")
            
            info_lines.append(f"Описание: {model_info['description']}")
            self.model_info_label.setText("\n".join(info_lines))
        else:
            self.model_info_label.setText("Информация о модели недоступна")
    
    def _check_rotation_update(self):
        """Проверяет, нужно ли обновить модель при ротации"""
        if not self.rotation_enabled or not rotation_system_available:
            return
        
        try:
            # Получаем лучшую доступную модель для диалога
            best_model = get_next_available_model("dialog")
            if best_model and best_model["id"] != self.current_model:
                old_model = self.current_model
                self.current_model = best_model["id"]
                
                # Обновляем комбобокс
                for i in range(self.model_combo.count()):
                    if self.model_combo.itemData(i) == best_model["id"]:
                        self.model_combo.setCurrentIndex(i)
                        break
                
                # Обновляем информацию
                self._update_model_info()
                
                # Уведомляем о смене
                self.model_changed.emit("gemini", self.current_model)
                logger.info(f"Ротация сменила модель: {old_model} → {best_model['display_name']}")
                
                # Синхронизируем с сервером
                self._sync_state_with_server("gemini", self.current_model)
                
        except Exception as e:
            logger.warning(f"Ошибка при проверке ротации: {e}")
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.rotation_checkbox.toggled.connect(self._on_rotation_changed)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
    
    def _on_rotation_changed(self, checked):
        """Обработчик изменения состояния ротации"""
        self.rotation_enabled = checked
        self.rotation_changed.emit(checked)
        
        # Обновляем доступность комбобокса модели
        self.model_combo.setEnabled(not checked)
        
        # Если включили ротацию, получаем лучшую доступную модель
        if checked and rotation_system_available:
            try:
                best_model = get_next_available_model("dialog")
                if best_model:
                    self.current_model = best_model["id"]
                    # Обновляем комбобокс под найденную модель
                    for i in range(self.model_combo.count()):
                        if self.model_combo.itemData(i) == best_model["id"]:
                            self.model_combo.setCurrentIndex(i)
                            break
                    logger.info(f"Ротация выбрала модель: {best_model['display_name']}")
            except Exception as e:
                logger.warning(f"Не удалось получить модель из системы ротации: {e}")
        
        # Обновляем информацию о модели
        self._update_model_info()
        
        logger.info(f"Ротация моделей: {'включена' if checked else 'отключена'}")
        
        # Управляем таймером ротации
        if checked and rotation_system_available:
            self.rotation_timer.start()
        else:
            self.rotation_timer.stop()
        
        # Синхронизируем с сервером
        current_model = self.current_model if not checked else "auto"
        self._sync_state_with_server("gemini", current_model)
    
    def _on_model_changed(self, index):
        """Обработчик изменения выбранной модели"""
        if index >= 0:
            model_id = self.model_combo.currentData()
            self.current_model = model_id
            
            # Обновляем информацию о модели
            self._update_model_info()
            
            # Излучаем сигнал об изменении модели
            self.model_changed.emit("gemini", model_id)
            
            logger.info(f"Выбрана модель Gemini: {model_id}")
            
            # Синхронизируем с сервером, если ротация отключена
            if not self.rotation_enabled:
                self._sync_state_with_server("gemini", model_id)
    
    def get_current_provider(self):
        """Возвращает текущего провайдера (всегда Gemini)"""
        return self.current_provider
    
    def get_current_model(self):
        """Возвращает текущую модель"""
        return self.current_model
    
    def get_rotation_enabled(self):
        """Возвращает состояние ротации"""
        return self.rotation_enabled
    
    def set_model(self, model_id: str):
        """Устанавливает модель программно"""
        # Находим индекс модели в комбобоксе
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == model_id:
                self.model_combo.setCurrentIndex(i)
                break
        else:
            logger.warning(f"Модель {model_id} не найдена в списке доступных моделей")
    
    def set_rotation(self, enabled: bool):
        """Устанавливает состояние ротации программно"""
        self.rotation_checkbox.setChecked(enabled)


    def _sync_state_with_server(self, provider: str, model_id: str | None):
        """
        Синхронизирует выбранную модель Gemini с CrewAI API сервером.
        Поддерживает автоматическую ротацию моделей.
        """
        try:
            from ..utils.network import get_crewai_server_base_url
            base_url = os.environ.get("CREWAI_API_BASE_URL", get_crewai_server_base_url())
            url = f"{base_url}/internal/state"
            
            # Всегда используем Gemini как провайдера
            provider = "gemini"
            
            # Если model_id равен "auto", это означает включенную ротацию
            if model_id == "auto" or not model_id:
                model_id = "gemini-2.0-flash-exp"  # Базовая модель для ротации
                logger.info(f"Используем базовую модель для ротации: {model_id}")
            
            payload = {
                "provider": provider, 
                "model_id": model_id,
                "rotation_enabled": self.rotation_enabled
            }
            headers = {"Content-Type": "application/json; charset=utf-8"}
            
            # Логируем отправляемые данные для отладки
            logger.debug(f"Отправка данных на сервер: {payload}")
            
            # Делаем несколько попыток отправки запроса
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
                    if resp.status_code == 200:
                        rotation_status = "с ротацией" if self.rotation_enabled else "без ротации"
                        logger.info(f"Модель Gemini синхронизирована с сервером: {model_id} ({rotation_status})")
                        return
                    else:
                        logger.warning(f"Попытка {attempt+1}/{max_retries}: Сервер вернул {resp.status_code}: {resp.text}")
                        
                        # Пробуем упрощенный формат без rotation_enabled
                        if resp.status_code == 400:
                            simple_payload = {"provider": provider, "model_id": model_id}
                            logger.debug(f"Пробуем упрощенный формат: {simple_payload}")
                            alt_resp = requests.post(url, data=json.dumps(simple_payload), headers=headers, timeout=5)
                            if alt_resp.status_code == 200:
                                logger.info("Модель синхронизирована с сервером (упрощенный формат)")
                                return
                            else:
                                logger.warning(f"Упрощенный формат также не сработал: {alt_resp.status_code}: {alt_resp.text}")
                except Exception as e:
                    logger.warning(f"Попытка {attempt+1}/{max_retries}: Ошибка при отправке запроса: {e}")
                
                # Если это не последняя попытка, ждем перед следующей
                if attempt < max_retries - 1:
                    time.sleep(1)  # Ждем 1 секунду перед следующей попыткой
            
            logger.error(f"Не удалось синхронизировать состояние с сервером после {max_retries} попыток")
        except Exception as e:
            logger.warning(f"Ошибка синхронизации состояния с сервером: {e}")

def test_unified_models_tab():
    """Тестовая функция для вкладки моделей Gemini"""
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = UnifiedModelsTab()
    widget.setWindowTitle("Gemini Models Tab Test")
    widget.show()
    
    # Тестируем сигналы
    def on_model_changed(provider, model_id):
        print(f"Модель изменена: {provider} -> {model_id}")
    
    def on_rotation_changed(enabled):
        print(f"Ротация: {'включена' if enabled else 'отключена'}")
    
    widget.model_changed.connect(on_model_changed)
    widget.rotation_changed.connect(on_rotation_changed)

    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_unified_models_tab()
