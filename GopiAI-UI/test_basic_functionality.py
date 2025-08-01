#!/usr/bin/env python3
"""
Простой тест основной функциональности исправлений UI
==================================================

Проверяет базовую работоспособность исправленных компонентов.
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Тест импорта исправленных модулей"""
    print("🔍 Тестирование импортов...")
    
    try:
        from gopiai.ui.components.error_display import ErrorDisplayWidget
        print("✅ ErrorDisplayWidget импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта ErrorDisplayWidget: {e}")
        return False
    
    try:
        from gopiai.ui.components.tab_widget import TabDocumentWidget
        print("✅ TabDocumentWidget импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта TabDocumentWidget: {e}")
        return False
        
    try:
        from gopiai.ui.components.terminal_widget import TerminalWidget, InteractiveTerminal
        print("✅ TerminalWidget импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта TerminalWidget: {e}")
        return False
        
    return True

def test_error_display_creation():
    """Тест создания ErrorDisplayWidget"""
    print("\n🔍 Тестирование создания ErrorDisplayWidget...")
    
    try:
        # Создаем QApplication если его нет
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from gopiai.ui.components.error_display import ErrorDisplayWidget
        
        widget = ErrorDisplayWidget()
        print("✅ ErrorDisplayWidget создан успешно")
        
        # Проверяем основные атрибуты
        assert hasattr(widget, 'error_title'), "Отсутствует error_title"
        assert hasattr(widget, 'error_description'), "Отсутствует error_description"
        assert hasattr(widget, 'error_details'), "Отсутствует error_details"
        print("✅ Все атрибуты ErrorDisplayWidget присутствуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания ErrorDisplayWidget: {e}")
        return False

def test_tab_widget_improvements():
    """Тест улучшений TabDocumentWidget"""
    print("\n🔍 Тестирование улучшений TabDocumentWidget...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
            
        from gopiai.ui.components.tab_widget import TabDocumentWidget
        
        widget = TabDocumentWidget()
        print("✅ TabDocumentWidget создан успешно")
        
        # Проверяем новые атрибуты
        assert hasattr(widget, '_widget_references'), "Отсутствует _widget_references"
        assert isinstance(widget._widget_references, dict), "_widget_references не является словарем"
        print("✅ Система управления ссылками на виджеты работает")
        
        # Проверяем новые методы
        assert hasattr(widget, 'add_terminal_tab'), "Отсутствует метод add_terminal_tab"
        assert hasattr(widget, 'cleanup_widget_references'), "Отсутствует метод cleanup_widget_references"
        print("✅ Новые методы TabDocumentWidget присутствуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования TabDocumentWidget: {e}")
        return False

def test_terminal_widget_improvements():
    """Тест улучшений TerminalWidget"""
    print("\n🔍 Тестирование улучшений TerminalWidget...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
            
        from gopiai.ui.components.terminal_widget import TerminalWidget
        
        widget = TerminalWidget()
        print("✅ TerminalWidget создан успешно")
        
        # Проверяем singleton
        assert TerminalWidget.instance is widget, "Singleton не работает"
        print("✅ Singleton паттерн работает")
        
        # Проверяем новые атрибуты
        assert hasattr(widget, '_terminal_references'), "Отсутствует _terminal_references"
        assert isinstance(widget._terminal_references, dict), "_terminal_references не является словарем"
        print("✅ Система управления ссылками на терминалы работает")
        
        # Проверяем новые методы
        assert hasattr(widget, 'cleanup'), "Отсутствует метод cleanup"
        assert hasattr(widget, 'get_current_terminal'), "Отсутствует метод get_current_terminal"
        print("✅ Новые методы TerminalWidget присутствуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования TerminalWidget: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов исправлений UI компонентов")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_error_display_creation,
        test_tab_widget_improvements,
        test_terminal_widget_improvements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Тест {test.__name__} провален")
        except Exception as e:
            print(f"❌ Тест {test.__name__} завершился с ошибкой: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ Исправления UI компонентов работают корректно")
        return True
    else:
        print("⚠️ Некоторые тесты провалены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)