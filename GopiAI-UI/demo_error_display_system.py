#!/usr/bin/env python3
"""
Демонстрация системы отображения ошибок GopiAI UI.

Этот скрипт демонстрирует работу ErrorDisplayWidget и его интеграцию
в ChatWidget для различных типов ошибок.
"""

import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gopiai'))

from gopiai.ui.components.error_display import ErrorDisplayWidget, show_error_dialog, show_critical_error


class ErrorDisplayDemo(QMainWindow):
    """Демонстрационное окно для системы отображения ошибок"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI - Демонстрация системы отображения ошибок")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout(central_widget)
        
        # Создаем ErrorDisplayWidget
        self.error_display = ErrorDisplayWidget()
        self.error_display.setVisible(False)  # Скрыт по умолчанию
        
        # Подключаем сигналы
        self.error_display.retryRequested.connect(self._on_retry_requested)
        self.error_display.dismissRequested.connect(self._on_error_dismissed)
        
        layout.addWidget(self.error_display)
        
        # Создаем кнопки для демонстрации различных типов ошибок
        buttons_layout = QHBoxLayout()
        
        # Кнопка API ошибки
        api_error_btn = QPushButton("🔌 API Ошибка")
        api_error_btn.clicked.connect(self._show_api_error)
        buttons_layout.addWidget(api_error_btn)
        
        # Кнопка ошибки соединения
        connection_error_btn = QPushButton("🚫 Ошибка соединения")
        connection_error_btn.clicked.connect(self._show_connection_error)
        buttons_layout.addWidget(connection_error_btn)
        
        # Кнопка ошибки компонента
        component_error_btn = QPushButton("⚠️ Ошибка компонента")
        component_error_btn.clicked.connect(self._show_component_error)
        buttons_layout.addWidget(component_error_btn)
        
        # Кнопка ошибки инструмента
        tool_error_btn = QPushButton("🔧 Ошибка инструмента")
        tool_error_btn.clicked.connect(self._show_tool_error)
        buttons_layout.addWidget(tool_error_btn)
        
        layout.addLayout(buttons_layout)
        
        # Вторая строка кнопок
        buttons_layout2 = QHBoxLayout()
        
        # Кнопка общей ошибки
        generic_error_btn = QPushButton("❌ Общая ошибка")
        generic_error_btn.clicked.connect(self._show_generic_error)
        buttons_layout2.addWidget(generic_error_btn)
        
        # Кнопка диалога ошибки
        dialog_error_btn = QPushButton("💬 Диалог ошибки")
        dialog_error_btn.clicked.connect(self._show_error_dialog)
        buttons_layout2.addWidget(dialog_error_btn)
        
        # Кнопка критической ошибки
        critical_error_btn = QPushButton("🚨 Критическая ошибка")
        critical_error_btn.clicked.connect(self._show_critical_error)
        buttons_layout2.addWidget(critical_error_btn)
        
        # Кнопка автоскрытия
        auto_hide_btn = QPushButton("⏰ Автоскрытие (5с)")
        auto_hide_btn.clicked.connect(self._show_auto_hide_error)
        buttons_layout2.addWidget(auto_hide_btn)
        
        layout.addLayout(buttons_layout2)
        
        # Кнопка скрытия ошибки
        hide_error_btn = QPushButton("✖ Скрыть ошибку")
        hide_error_btn.clicked.connect(self._hide_error)
        layout.addWidget(hide_error_btn)
        
        # Добавляем растягивающийся элемент
        layout.addStretch()
        
        print("🎯 Демонстрация системы отображения ошибок запущена")
        print("📋 Нажимайте кнопки для демонстрации различных типов ошибок")
    
    def _show_api_error(self):
        """Демонстрирует API ошибку"""
        print("🔌 Показываем API ошибку")
        self.error_display.show_api_error(
            error_message="Превышен лимит запросов к API. Попробуйте позже.",
            error_code="RATE_LIMIT_EXCEEDED",
            retry_action="api"
        )
    
    def _show_connection_error(self):
        """Демонстрирует ошибку соединения"""
        print("🚫 Показываем ошибку соединения")
        self.error_display.show_connection_error("GopiAI Backend Server")
    
    def _show_component_error(self):
        """Демонстрирует ошибку компонента"""
        print("⚠️ Показываем ошибку компонента")
        self.error_display.show_component_error(
            component_name="ChatWidget",
            error_details="Не удалось инициализировать компонент чата из-за отсутствия зависимостей",
            fallback_available=True
        )
    
    def _show_tool_error(self):
        """Демонстрирует ошибку инструмента"""
        print("🔧 Показываем ошибку инструмента")
        self.error_display.show_tool_error(
            tool_name="Terminal",
            error_message="Команда не найдена или недоступна",
            command="unknown_command --help"
        )
    
    def _show_generic_error(self):
        """Демонстрирует общую ошибку"""
        print("❌ Показываем общую ошибку")
        self.error_display.show_generic_error(
            title="Неожиданная ошибка",
            message="Произошла неожиданная ошибка в системе. Обратитесь к администратору.",
            details="Stack trace: TypeError at line 42 in module xyz.py"
        )
    
    def _show_error_dialog(self):
        """Демонстрирует диалог ошибки"""
        print("💬 Показываем диалог ошибки")
        show_error_dialog(
            title="Ошибка сохранения",
            message="Не удалось сохранить файл конфигурации.",
            details="Permission denied: /etc/gopiai/config.json",
            parent=self
        )
    
    def _show_critical_error(self):
        """Демонстрирует критическую ошибку"""
        print("🚨 Показываем критическую ошибку")
        show_critical_error(
            message="Критическая ошибка системы! Приложение будет закрыто.",
            details="Fatal error: Memory corruption detected",
            parent=self
        )
    
    def _show_auto_hide_error(self):
        """Демонстрирует ошибку с автоскрытием"""
        print("⏰ Показываем ошибку с автоскрытием")
        self.error_display.show_generic_error(
            title="Временная ошибка",
            message="Это сообщение исчезнет через 5 секунд"
        )
        self.error_display.auto_hide_after(5)
    
    def _hide_error(self):
        """Скрывает текущую ошибку"""
        print("✖ Скрываем ошибку")
        self.error_display.setVisible(False)
    
    def _on_retry_requested(self, error_type: str):
        """Обрабатывает запрос повтора"""
        print(f"🔄 Запрошен повтор для типа ошибки: {error_type}")
        
        # Имитируем обработку повтора
        QTimer.singleShot(1000, lambda: self._simulate_retry_result(error_type))
    
    def _simulate_retry_result(self, error_type: str):
        """Имитирует результат повтора операции"""
        import random
        
        success = random.choice([True, False])
        
        if success:
            print(f"✅ Повтор для {error_type} успешен")
            self.error_display.setVisible(False)
            # Здесь можно показать уведомление об успехе
        else:
            print(f"❌ Повтор для {error_type} неуспешен")
            self.error_display.show_generic_error(
                title="Повтор неуспешен",
                message=f"Не удалось выполнить повтор операции для {error_type}"
            )
    
    def _on_error_dismissed(self):
        """Обрабатывает закрытие ошибки"""
        print("👋 Ошибка закрыта пользователем")


def main():
    """Главная функция демонстрации"""
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    # Создаем и показываем демонстрационное окно
    demo = ErrorDisplayDemo()
    demo.show()
    
    print("\n" + "="*60)
    print("🎯 ДЕМОНСТРАЦИЯ СИСТЕМЫ ОТОБРАЖЕНИЯ ОШИБОК GOPIAI")
    print("="*60)
    print("📋 Доступные демонстрации:")
    print("   🔌 API Ошибка - показывает ошибку API с возможностью повтора")
    print("   🚫 Ошибка соединения - показывает проблемы с подключением")
    print("   ⚠️ Ошибка компонента - показывает ошибки UI компонентов")
    print("   🔧 Ошибка инструмента - показывает ошибки выполнения команд")
    print("   ❌ Общая ошибка - показывает общие системные ошибки")
    print("   💬 Диалог ошибки - показывает модальный диалог ошибки")
    print("   🚨 Критическая ошибка - показывает критические ошибки")
    print("   ⏰ Автоскрытие - показывает ошибку с автоматическим скрытием")
    print("="*60)
    print("🎮 Нажимайте кнопки для демонстрации различных типов ошибок")
    print("🔄 Кнопка 'Повторить' имитирует случайный результат")
    print("="*60)
    
    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == "__main__":
    main()