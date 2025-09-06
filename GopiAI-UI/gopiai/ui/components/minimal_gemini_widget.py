#!/usr/bin/env python3
"""
Minimal Gemini Widget для GopiAI UI
Минимальный переключатель для Gemini - только кнопка активации без настроек
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

# Импорт системы иконок
try:
    from ..components.icon_file_system_model import UniversalIconManager
    icon_manager = UniversalIconManager.instance()
except ImportError:
    icon_manager = None

logger = logging.getLogger(__name__)

class MinimalGeminiWidget(QWidget):
    """Минимальный виджет для переключения на Gemini"""
    
    # Сигналы
    provider_changed = Signal(str)  # provider
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.is_active = True  # Gemini активен по умолчанию
        
        self._setup_ui()
        self._setup_connections()
        
        logger.info("MinimalGeminiWidget инициализирован")
    
    def _setup_ui(self):
        """Настраивает минимальный пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Заголовок
        title_label = QLabel("Gemini")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Описание
        desc_label = QLabel("Основной провайдер ИИ. Модели настроены автоматически.")
        layout.addWidget(desc_label)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Кнопка активации
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Активировать Gemini")
        self.activate_btn.setMinimumHeight(40)
        
        # Устанавливаем иконку через глобальную систему
        if icon_manager:
            gemini_icon = icon_manager.get_icon("brain")  # Используем brain как иконку для ИИ
            if not gemini_icon.isNull():
                self.activate_btn.setIcon(gemini_icon)
        
        button_layout.addWidget(self.activate_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Статус
        self.status_label = QLabel("Статус: Активен")
        self.status_label.setProperty("status", "active")
        layout.addWidget(self.status_label)
        
        # Информация
        info_layout = QVBoxLayout()
        
        info_label = QLabel("Информация:")
        info_font = QFont()
        info_font.setBold(True)
        info_label.setFont(info_font)
        info_layout.addWidget(info_label)
        
        info_text = QLabel(
            "• Модели ротируются автоматически\n"
            "• Настройки управляются системой\n"
            "• Оптимальная производительность"
        )
        info_layout.addWidget(info_text)
        
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Обновляем состояние UI
        self._update_ui_state()
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.activate_btn.clicked.connect(self._on_activate_clicked)
    
    def _on_activate_clicked(self):
        """Обработчик нажатия кнопки активации"""
        if not self.is_active:
            self.is_active = True
            self._update_ui_state()
            self.provider_changed.emit("gemini")
            logger.info("Gemini активирован")
    
    def _update_ui_state(self):
        """Обновляет состояние UI в зависимости от активности"""
        if self.is_active:
            self.activate_btn.setText("Активен")
            self.activate_btn.setEnabled(False)
            self.status_label.setText("Статус: Активен")
            self.status_label.setProperty("status", "active")
        else:
            self.activate_btn.setText("Активировать Gemini")
            self.activate_btn.setEnabled(True)
            self.status_label.setText("Статус: Неактивен")
            self.status_label.setProperty("status", "inactive")
        
        # Применяем стили заново для обновления свойств
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
    
    def set_active(self, active: bool):
        """Устанавливает состояние активности"""
        if self.is_active != active:
            self.is_active = active
            self._update_ui_state()
    
    def is_provider_active(self) -> bool:
        """Возвращает состояние активности провайдера"""
        return self.is_active


def test_minimal_gemini_widget():
    """Тестовая функция для минимального виджета Gemini"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = MinimalGeminiWidget()
    widget.setWindowTitle("Minimal Gemini Widget Test")
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_minimal_gemini_widget()
