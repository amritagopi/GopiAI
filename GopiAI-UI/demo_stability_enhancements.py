#!/usr/bin/env python3
"""
Демонстрация улучшений стабильности UI GopiAI
============================================

Этот скрипт демонстрирует работу расширенных улучшений стабильности UI.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям GopiAI
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PySide6.QtCore import QTimer
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from gopiai.ui.components.ui_stability_enhancements import (
        stability_manager, stability_monitor, error_recovery,
        show_stability_report, stable_widget_creation, safe_widget_operation
    )
    from gopiai.ui.components.tab_widget import TabDocumentWidget
    STABILITY_AVAILABLE = True
except ImportError as e:
    print(f"Улучшения стабильности недоступны: {e}")
    STABILITY_AVAILABLE = False


class StabilityDemoWindow(QMainWindow):
    """Демонстрационное окно для показа улучшений стабильности"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Демонстрация улучшений стабильности GopiAI UI")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("🛡️ Демонстрация улучшений стабильности UI")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Информация о статусе
        self.status_label = QLabel()
        self.update_status_info()
        layout.addWidget(self.status_label)
        
        # Кнопки для демонстрации
        self.create_demo_buttons(layout)
        
        # TabDocumentWidget для демонстрации
        if STABILITY_AVAILABLE:
            self.tab_widget = TabDocumentWidget()
            layout.addWidget(self.tab_widget)
            
            # Запускаем мониторинг стабильности
            if not stability_monitor.timer.isActive():
                stability_monitor.start_monitoring()
                
            # Подключаем обработчик проблем стабильности
            stability_monitor.stability_issue_detected.connect(self.handle_stability_issue)
        
        # Таймер для обновления информации
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status_info)
        self.update_timer.start(5000)  # Обновляем каждые 5 секунд
        
    def create_demo_buttons(self, layout):
        """Создание кнопок для демонстрации"""
        
        # Кнопка создания стабильных вкладок
        create_tabs_btn = QPushButton("📄 Создать стабильные вкладки")
        create_tabs_btn.clicked.connect(self.create_stable_tabs)
        layout.addWidget(create_tabs_btn)
        
        # Кнопка симуляции ошибок
        simulate_error_btn = QPushButton("⚠️ Симулировать ошибку создания виджета")
        simulate_error_btn.clicked.connect(self.simulate_widget_error)
        layout.addWidget(simulate_error_btn)
        
        # Кнопка проверки утечек памяти
        check_leaks_btn = QPushButton("🔍 Проверить утечки памяти")
        check_leaks_btn.clicked.connect(self.check_memory_leaks)
        layout.addWidget(check_leaks_btn)
        
        # Кнопка показа отчета стабильности
        show_report_btn = QPushButton("📊 Показать отчет стабильности")
        show_report_btn.clicked.connect(self.show_stability_report)
        layout.addWidget(show_report_btn)
        
        # Кнопка принудительной сборки мусора
        gc_btn = QPushButton("🗑️ Принудительная сборка мусора")
        gc_btn.clicked.connect(self.force_garbage_collection)
        layout.addWidget(gc_btn)
        
    def create_stable_tabs(self):
        """Создание стабильных вкладок с демонстрацией улучшений"""
        if not STABILITY_AVAILABLE:
            print("Улучшения стабильности недоступны")
            return
            
        try:
            # Создаем несколько вкладок разных типов
            self.tab_widget.add_new_tab("Обычная вкладка")
            self.tab_widget.add_notebook_tab("Блокнот с улучшениями")
            
            print("✅ Стабильные вкладки созданы успешно")
            self.update_status_info()
            
        except Exception as e:
            print(f"❌ Ошибка создания вкладок: {e}")
            
    def simulate_widget_error(self):
        """Симуляция ошибки создания виджета для демонстрации восстановления"""
        if not STABILITY_AVAILABLE:
            print("Улучшения стабильности недоступны")
            return
            
        @stable_widget_creation(fallback_factory=lambda: QTextEdit("Fallback виджет создан!"))
        def create_problematic_widget():
            raise Exception("Симулированная ошибка создания виджета")
            
        try:
            widget = create_problematic_widget()
            if widget:
                print("✅ Ошибка обработана, fallback виджет создан")
                # Добавляем fallback виджет как вкладку
                index = self.tab_widget.tab_widget.addTab(widget, "Восстановленная вкладка")
                self.tab_widget.tab_widget.setCurrentIndex(index)
                self.tab_widget._update_display()
            else:
                print("❌ Не удалось создать даже fallback виджет")
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            
        self.update_status_info()
        
    def check_memory_leaks(self):
        """Проверка утечек памяти"""
        if not STABILITY_AVAILABLE:
            print("Улучшения стабильности недоступны")
            return
            
        try:
            leaked_widgets = stability_manager.check_memory_leaks()
            if leaked_widgets:
                print(f"⚠️ Обнаружены утечки памяти: {leaked_widgets}")
            else:
                print("✅ Утечки памяти не обнаружены")
                
            self.update_status_info()
            
        except Exception as e:
            print(f"❌ Ошибка проверки утечек памяти: {e}")
            
    def show_stability_report(self):
        """Показ отчета стабильности"""
        if not STABILITY_AVAILABLE:
            print("Улучшения стабильности недоступны")
            return
            
        try:
            show_stability_report(self)
        except Exception as e:
            print(f"❌ Ошибка показа отчета: {e}")
            
    def force_garbage_collection(self):
        """Принудительная сборка мусора"""
        if not STABILITY_AVAILABLE:
            print("Улучшения стабильности недоступны")
            return
            
        try:
            collected = stability_manager.force_garbage_collection()
            print(f"🗑️ Собрано {collected} объектов сборщиком мусора")
            self.update_status_info()
        except Exception as e:
            print(f"❌ Ошибка сборки мусора: {e}")
            
    def update_status_info(self):
        """Обновление информации о статусе"""
        if not STABILITY_AVAILABLE:
            self.status_label.setText("❌ Улучшения стабильности недоступны")
            return
            
        try:
            metrics = stability_manager.get_stability_metrics()
            recovery_history = error_recovery.get_recovery_history()
            
            status_text = f"""
📊 Текущий статус стабильности:

🔧 Метрики:
• Ошибки создания виджетов: {metrics['widget_creation_errors']}
• Ошибки уничтожения виджетов: {metrics['widget_destruction_errors']}
• Обнаружено утечек памяти: {metrics['memory_leaks_detected']}
• Активаций fallback: {metrics['fallback_activations']}
• Зарегистрированных виджетов: {metrics['registered_widgets']}
• Активных виджетов: {metrics['active_widgets']}

🔄 Восстановления:
• Всего попыток: {len(recovery_history)}
• Успешных: {sum(1 for r in recovery_history if r['success'])}

🛡️ Мониторинг: {'🟢 Активен' if stability_monitor.timer.isActive() else '🔴 Неактивен'}
            """
            
            self.status_label.setText(status_text.strip())
            
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка получения статуса: {e}")
            
    def handle_stability_issue(self, issue_type: str, data: dict):
        """Обработка проблем стабильности"""
        print(f"🚨 Обнаружена проблема стабильности: {issue_type}")
        print(f"📋 Данные: {data}")
        self.update_status_info()
        
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if STABILITY_AVAILABLE:
            stability_monitor.stop_monitoring()
        event.accept()


def main():
    """Главная функция демонстрации"""
    app = QApplication(sys.argv)
    
    print("🚀 Запуск демонстрации улучшений стабильности GopiAI UI")
    print("=" * 60)
    
    if STABILITY_AVAILABLE:
        print("✅ Улучшения стабильности загружены успешно")
        
        # Показываем начальные метрики
        metrics = stability_manager.get_stability_metrics()
        print(f"📊 Начальные метрики: {metrics}")
        
    else:
        print("❌ Улучшения стабильности недоступны")
        print("   Убедитесь, что файл ui_stability_enhancements.py находится в правильном месте")
    
    # Создаем и показываем демонстрационное окно
    window = StabilityDemoWindow()
    window.show()
    
    print("\n🎯 Инструкции по демонстрации:")
    print("1. Нажмите 'Создать стабильные вкладки' для создания вкладок с улучшениями")
    print("2. Нажмите 'Симулировать ошибку' для демонстрации автоматического восстановления")
    print("3. Нажмите 'Проверить утечки памяти' для проверки системы мониторинга")
    print("4. Нажмите 'Показать отчет стабильности' для просмотра детальных метрик")
    print("5. Наблюдайте за автоматическим обновлением статуса каждые 5 секунд")
    
    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == "__main__":
    main()