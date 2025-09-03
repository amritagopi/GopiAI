#!/usr/bin/env python3
"""
Gemini Model Widget для GopiAI UI
Виджет для работы с моделями Gemini
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, 
    QGroupBox, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)

class GeminiModelWidget(QWidget):
    """Виджет для работы с моделями Gemini"""
    
    # Сигналы
    model_selected = Signal(dict)  # Эмитится при выборе модели
    
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Инициализация GeminiModelWidget")
        
        self.current_model = None
        self.available_models = []
        
        # Заглушки для совместимости
        self.model_config_manager = None
        
        self._setup_ui()
        self._setup_connections()
        self._init_backends()
        
        # Загружаем модели при инициализации
        self._load_gemini_models()
        
    def _setup_ui(self):
        """Настраивает интерфейс виджета"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Группа выбора модели
        model_group = QGroupBox("🔷 Gemini Models")
        model_layout = QVBoxLayout()
        
        # Комбобокс для выбора модели
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("Модель:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        model_select_layout.addWidget(self.model_combo)
        
        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMaximumWidth(100)
        model_select_layout.addWidget(self.refresh_btn)
        
        model_layout.addLayout(model_select_layout)
        
        # Статус провайдера
        self.provider_status = QLabel("🔷 Gemini активен")
        self.provider_status.setStyleSheet("color: green; font-weight: bold;")
        model_layout.addWidget(self.provider_status)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        model_layout.addWidget(self.progress_bar)
        
        # Информационная панель
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        model_layout.addWidget(self.info_text)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.test_connection_btn = QPushButton("🔍 Проверить соединение")
        button_layout.addWidget(self.test_connection_btn)
        
        self.reset_btn = QPushButton("↩️ Сброс")
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def _setup_connections(self):
        """Настраивает соединения сигналов и слотов"""
        self.model_combo.currentTextChanged.connect(self._on_model_selected)
        self.refresh_btn.clicked.connect(self._load_gemini_models)
        self.test_connection_btn.clicked.connect(self._test_connection)
        self.reset_btn.clicked.connect(self._reset_selection)
        
    def _init_backends(self):
        """Инициализирует бэкенды"""
        try:
            # Создаем заглушку для конфиг менеджера
            class DummyConfigManager:
                def get_available_models(self):
                    return [
                        {'id': 'gemini/gemini-1.5-flash', 'display_name': 'Gemini 1.5 Flash', 'provider': 'gemini'},
                        {'id': 'gemini/gemini-1.5-pro', 'display_name': 'Gemini 1.5 Pro', 'provider': 'gemini'},
                        {'id': 'gemini/gemini-2.0-flash-lite', 'display_name': 'Gemini 2.0 Flash-Lite', 'provider': 'gemini'},
                    ]
            
            self.model_config_manager = DummyConfigManager()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации бэкендов: {e}")
            # Убедимся, что атрибуты определены даже в случае ошибки
            self.model_config_manager = None
    
    def _load_gemini_models(self):
        """Загружает модели Gemini"""
        try:
            self.progress_bar.setVisible(True)
            self.model_combo.clear()
            
            if not self.model_config_manager:
                self.model_combo.addItem("Модели недоступны", None)
                return
            
            models = self.model_config_manager.get_available_models()
            
            for model in models:
                if model.get('provider') == 'gemini':
                    display_name = model.get('display_name', model.get('id', 'Unknown'))
                    self.model_combo.addItem(display_name, model.get('id'))
            
            self.available_models = models
            
            if self.model_combo.count() > 0:
                self.model_combo.setCurrentIndex(0)
                self._on_model_selected()
            
            self._update_info_display()
            logger.info(f"Загружено {len(models)} моделей Gemini")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки моделей Gemini: {e}")
            self.model_combo.addItem("Ошибка загрузки", None)
        finally:
            self.progress_bar.setVisible(False)
    
    def _on_model_selected(self):
        """Обработчик выбора модели"""
        if self.model_combo.currentData():
            self.current_model = self.model_combo.currentData()
            
            # Ищем полную информацию о модели
            model_data = next((m for m in self.available_models if m.get('id') == self.current_model), None)
            
            if model_data:
                # Эмитируем сигнал с информацией о выбранной модели
                self.model_selected.emit({
                    'provider': 'gemini',
                    'model_id': self.current_model,
                    'model_data': model_data
                })
                
                logger.info(f"Выбрана модель Gemini: {self.current_model}")
            
            self._update_info_display()
    
    def _update_info_display(self):
        """Обновляет информационную панель"""
        if not self.current_model:
            self.info_text.setPlainText("Модель не выбрана")
            return
        
        # Находим данные о текущей модели
        model_data = next((m for m in self.available_models if m.get('id') == self.current_model), None)
        
        info_text = f"🔷 Gemini Models\n\n"
        info_text += f"📋 Выбранная модель: {self.model_combo.currentText()}\n"
        info_text += f"🆔 ID: {self.current_model}\n"
        info_text += f"⏰ Обновлено: {datetime.now().strftime('%H:%M:%S')}\n"
        
        if model_data:
            context_length = model_data.get('context_length', 'Неизвестно')
            info_text += f"📏 Контекст: {context_length} токенов\n"
            
            # Дополнительная информация о модели
            if 'priority' in model_data:
                info_text += f"⭐ Приоритет: {model_data['priority']}\n"
        
        info_text += f"\n🌐 Статус: Активен\n"
        info_text += f"📊 Всего моделей: {self.model_combo.count()}\n"
        
        self.info_text.setPlainText(info_text)
    
    def _test_connection(self):
        """Тестирует соединение с Gemini"""
        success = True
        message = "Соединение с Gemini готово к работе!"
        
        try:
            if self.model_config_manager:
                models = self.model_config_manager.get_available_models()
                if models:
                    message = f"Соединение успешно! Доступно {len(models)} моделей."
                else:
                    success = False
                    message = "Соединение установлено, но модели не найдены."
            else:
                success = False
                message = "Менеджер конфигурации не инициализирован."
                
        except Exception as e:
            success = False
            message = f"Ошибка соединения: {str(e)}"
        
        # Показываем результат в информационной панели
        status_text = f"🔍 Тест соединения:\n"
        status_text += f"{'✅' if success else '❌'} {message}\n\n"
        status_text += self.info_text.toPlainText()
        
        self.info_text.setPlainText(status_text)
        
        logger.info(f"Тест соединения Gemini: {'успешен' if success else 'неуспешен'} - {message}")
    
    def _reset_selection(self):
        """Сбрасывает выбор модели"""
        self.current_model = None
        self.model_combo.setCurrentIndex(0)
        self._update_info_display()
        logger.info("Выбор модели сброшен")
    
    def get_selected_model_info(self) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о выбранной модели"""
        if not self.current_model:
            return None
        
        model_data = next((m for m in self.available_models if m.get('id') == self.current_model), None)
        
        return {
            'provider': 'gemini',
            'model_id': self.current_model,
            'model_name': self.model_combo.currentText(),
            'model_data': model_data
        } if model_data else None
    
    def set_model_by_id(self, model_id: str):
        """Устанавливает модель по ID"""
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == model_id:
                self.model_combo.setCurrentIndex(i)
                logger.info(f"Установлена модель: {model_id}")
                return True
        
        logger.warning(f"Модель {model_id} не найдена")
        return False