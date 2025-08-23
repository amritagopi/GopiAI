#!/usr/bin/env python3
"""
Unified Models Tab для GopiAI UI
Объединенная вкладка с переключателем между Gemini и OpenRouter
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QButtonGroup, QRadioButton, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
import os
import json
import requests
import time
from PySide6.QtGui import QFont

# Импорт системы иконок
try:
    from ..components.icon_file_system_model import UniversalIconManager
    icon_manager = UniversalIconManager.instance()
except ImportError:
    icon_manager = None

# Импорт компонентов
try:
    from .openrouter_model_widget import OpenRouterModelWidget
except ImportError:
    OpenRouterModelWidget = None

logger = logging.getLogger(__name__)

class UnifiedModelsTab(QWidget):
    """Объединенная вкладка для переключения между Gemini и OpenRouter

    Дополнительно синхронизирует выбранного провайдера/модель с CrewAI API сервером
    через POST /internal/state.
    """
    
    # Сигналы
    provider_changed = Signal(str)  # provider
    model_changed = Signal(str, str)  # provider, model_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_provider = "gemini"  # По умолчанию Gemini
        
        self._setup_ui()
        self._setup_connections()
        
        logger.info("UnifiedModelsTab инициализирован")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Модели ИИ")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Переключатель провайдеров
        provider_frame = QFrame()
        provider_layout = QVBoxLayout(provider_frame)
        provider_layout.setContentsMargins(8, 8, 8, 8)
        
        provider_label = QLabel("Выберите провайдера:")
        provider_font = QFont()
        provider_font.setBold(True)
        provider_label.setFont(provider_font)
        provider_layout.addWidget(provider_label)
        
        # Радиокнопки для выбора провайдера
        radio_layout = QHBoxLayout()
        
        self.provider_button_group = QButtonGroup()
        
        self.gemini_radio = QRadioButton("Gemini")
        self.gemini_radio.setChecked(True)
        if icon_manager:
            gemini_icon = icon_manager.get_icon("brain")
            if not gemini_icon.isNull():
                self.gemini_radio.setIcon(gemini_icon)
        
        self.openrouter_radio = QRadioButton("OpenRouter")
        if icon_manager:
            openrouter_icon = icon_manager.get_icon("globe")
            if not openrouter_icon.isNull():
                self.openrouter_radio.setIcon(openrouter_icon)
        
        self.provider_button_group.addButton(self.gemini_radio, 0)
        self.provider_button_group.addButton(self.openrouter_radio, 1)
        
        radio_layout.addWidget(self.gemini_radio)
        radio_layout.addWidget(self.openrouter_radio)
        radio_layout.addStretch()
        
        provider_layout.addLayout(radio_layout)
        layout.addWidget(provider_frame)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Стековый виджет для содержимого провайдеров
        self.stacked_widget = QStackedWidget()
        
        # Страница Gemini
        self.gemini_page = self._create_gemini_page()
        self.stacked_widget.addWidget(self.gemini_page)
        
        # Страница OpenRouter
        if OpenRouterModelWidget:
            self.openrouter_page = OpenRouterModelWidget()
            self.stacked_widget.addWidget(self.openrouter_page)
            
            # Подключаем сигналы OpenRouter
            self.openrouter_page.model_selected.connect(self._on_openrouter_model_selected)
        else:
            # Заглушка, если OpenRouter недоступен
            self.openrouter_page = self._create_openrouter_fallback()
            self.stacked_widget.addWidget(self.openrouter_page)
        
        layout.addWidget(self.stacked_widget)
        
        # По умолчанию показываем Gemini
        self.stacked_widget.setCurrentIndex(0)
    
    def _create_gemini_page(self):
        """Создает страницу для Gemini"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        
        # Описание
        desc_label = QLabel("Основной провайдер ИИ. Модели настроены автоматически и ротируются для оптимальной производительности.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Статус
        self.gemini_status_label = QLabel("Статус: Активен")
        status_font = QFont()
        status_font.setBold(True)
        self.gemini_status_label.setFont(status_font)
        layout.addWidget(self.gemini_status_label)
        
        # Информация
        info_label = QLabel("Информация:")
        info_font = QFont()
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        info_text = QLabel(
            "• Модели ротируются автоматически\n"
            "• Настройки управляются системой\n"
            "• Оптимальная производительность\n"
            "• Не требует дополнительной настройки"
        )
        layout.addWidget(info_text)
        
        layout.addStretch()
        return page
    
    def _create_openrouter_fallback(self):
        """Создает заглушку для OpenRouter, если он недоступен"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        
        error_label = QLabel("OpenRouter недоступен")
        error_font = QFont()
        error_font.setBold(True)
        error_label.setFont(error_font)
        layout.addWidget(error_label)
        
        desc_label = QLabel("Компонент OpenRouter не загружен или недоступен.")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        return page
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.provider_button_group.buttonClicked.connect(self._on_provider_changed)
    
    def _on_provider_changed(self, button):
        """Обработчик переключения провайдера"""
        if button == self.gemini_radio:
            new_provider = "gemini"
            self.stacked_widget.setCurrentIndex(0)
        else:
            new_provider = "openrouter"
            self.stacked_widget.setCurrentIndex(1)
        
        if new_provider != self.current_provider:
            self.current_provider = new_provider
            self._update_status()
            self.provider_changed.emit(new_provider)
            
            logger.info(f"Переключение на провайдера: {new_provider}")
            # Синхронизируем провайдера с сервером (с текущей моделью, если есть)
            try:
                current_model_getter = getattr(getattr(self, "openrouter_page", None), "get_selected_model_id", None)
                model_id = current_model_getter() if callable(current_model_getter) else None
                model_id_str = str(model_id) if model_id is not None else None
                self._sync_state_with_server(provider=new_provider, model_id=model_id_str)
            except Exception as e:
                logger.warning(f"Не удалось синхронизировать провайдера: {e}")
    
    def _update_status(self):
        """Обновляет статус в зависимости от выбранного провайдера"""
        if self.current_provider == "gemini":
            self.gemini_status_label.setText("Статус: Активен")
        else:
            self.gemini_status_label.setText("Статус: Неактивен")
    
    def _on_openrouter_model_selected(self, model_data):
        """Обработчик выбора модели OpenRouter"""
        if isinstance(model_data, dict) and 'id' in model_data:
            model_id = model_data['id']
            self.model_changed.emit("openrouter", model_id)
            logger.info(f"Выбрана модель OpenRouter: {model_id}")
            # Синхронизируем выбранную модель с сервером
            try:
                self._sync_state_with_server(provider="openrouter", model_id=model_id)
            except Exception as e:
                logger.warning(f"Не удалось синхронизировать модель: {e}")
    
    def get_current_provider(self):
        """Возвращает текущего провайдера"""
        return self.current_provider
    
    def set_provider(self, provider: str):
        """Устанавливает провайдера программно и синхронизирует состояние с сервером"""
        if provider == "gemini":
            self.gemini_radio.setChecked(True)
            self.stacked_widget.setCurrentIndex(0)
        elif provider == "openrouter":
            self.openrouter_radio.setChecked(True)
            self.stacked_widget.setCurrentIndex(1)
        
        if provider != self.current_provider:
            self.current_provider = provider
            self._update_status()
            self.provider_changed.emit(provider)
            # Синхронизируем провайдера с сервером (с актуальной моделью если выбрана)
            try:
                current_model_getter = getattr(getattr(self, "openrouter_page", None), "get_selected_model_id", None)
                model_id = current_model_getter() if callable(current_model_getter) else None
                model_id_str = str(model_id) if model_id is not None else None
                self._sync_state_with_server(provider=provider, model_id=model_id_str)
            except Exception as e:
                logger.warning(f"Не удалось синхронизировать провайдера (programmatic): {e}")


    def _sync_state_with_server(self, provider: str, model_id: str | None):
        """
        Синхронизирует выбранного провайдера/модель с CrewAI API сервером.
        Требования сервера: оба поля обязательны.
        """
        try:
            from ..utils.network import get_crewai_server_base_url
            base_url = os.environ.get("CREWAI_API_BASE_URL", get_crewai_server_base_url())
            url = f"{base_url}/internal/state"
            
            # Проверяем, что оба параметра имеют значения
            if not provider:
                logger.warning("Не указан провайдер для синхронизации с сервером")
                return
                
            # Сервер ожидает оба поля, поэтому если model_id отсутствует — используем значение по умолчанию
            if not model_id and provider == "openrouter":
                # Для OpenRouter нужно указать конкретную модель
                # Пробуем получить текущую модель из OpenRouter виджета
                try:
                    current_model_getter = getattr(getattr(self, "openrouter_page", None), "get_selected_model_id", None)
                    if callable(current_model_getter):
                        model_id = current_model_getter()
                except Exception:
                    pass
                
                # Если не удалось получить модель, используем значение по умолчанию
                if not model_id:
                    model_id = "google/gemini-2.5-pro-exp-03-25"  # Модель по умолчанию для OpenRouter
                    logger.info(f"Используем модель по умолчанию для OpenRouter: {model_id}")
            elif not model_id and provider == "gemini":
                # Для Gemini используем стандартную модель
                model_id = "gemini-2.0-flash-exp"
                logger.info(f"Используем модель по умолчанию для Gemini: {model_id}")
                
            payload = {"provider": provider, "model_id": model_id}
            headers = {"Content-Type": "application/json; charset=utf-8"}
            
            # Логируем отправляемые данные для отладки
            logger.debug(f"Отправка данных на сервер: {payload}")
            
            # Делаем несколько попыток отправки запроса
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
                    if resp.status_code == 200:
                        logger.info(f"Состояние провайдера/модели синхронизировано с сервером: {provider}/{model_id}")
                        return
                    else:
                        logger.warning(f"Попытка {attempt+1}/{max_retries}: Сервер вернул {resp.status_code}: {resp.text}")
                        
                        # Если ошибка 400, возможно, сервер ожидает другой формат данных
                        if resp.status_code == 400:
                            # Пробуем альтернативный формат
                            alt_payload = {
                                "provider": provider,
                                "model_id": model_id,
                                "action": "set_model"
                            }
                            logger.debug(f"Пробуем альтернативный формат: {alt_payload}")
                            alt_resp = requests.post(url, data=json.dumps(alt_payload), headers=headers, timeout=5)
                            if alt_resp.status_code == 200:
                                logger.info("Состояние синхронизировано с сервером (альтернативный формат)")
                                return
                            else:
                                logger.warning(f"Альтернативный формат также не сработал: {alt_resp.status_code}: {alt_resp.text}")
                except Exception as e:
                    logger.warning(f"Попытка {attempt+1}/{max_retries}: Ошибка при отправке запроса: {e}")
                
                # Если это не последняя попытка, ждем перед следующей
                if attempt < max_retries - 1:
                    time.sleep(1)  # Ждем 1 секунду перед следующей попыткой
            
            logger.error(f"Не удалось синхронизировать состояние с сервером после {max_retries} попыток")
        except Exception as e:
            logger.warning(f"Ошибка синхронизации состояния с сервером: {e}")

def test_unified_models_tab():
    """Тестовая функция для объединенной вкладки моделей"""
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = UnifiedModelsTab()
    widget.setWindowTitle("Unified Models Tab Test")
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_unified_models_tab()
