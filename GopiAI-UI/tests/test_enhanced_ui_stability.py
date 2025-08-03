"""
Расширенные тесты стабильности UI с новыми улучшениями
====================================================

Тестирует улучшения стабильности из ui_stability_enhancements.py
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from gopiai.ui.components.ui_stability_enhancements import (
        UIStabilityManager, StabilityMonitor, EnhancedErrorRecovery,
        stability_manager, error_recovery, stability_monitor,
        stable_widget_creation, safe_widget_operation
    )
    from gopiai.ui.components.tab_widget import TabDocumentWidget
    STABILITY_ENHANCEMENTS_AVAILABLE = True
except ImportError as e:
    print(f"Не удалось импортировать улучшения стабильности: {e}")
    STABILITY_ENHANCEMENTS_AVAILABLE = False


@pytest.fixture
def app():
    """Фикстура для создания QApplication"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.mark.skipif(not STABILITY_ENHANCEMENTS_AVAILABLE, reason="Улучшения стабильности недоступны")
class TestUIStabilityManager:
    """Тесты менеджера стабильности UI"""
    
    def test_stability_manager_initialization(self):
        """Тест инициализации менеджера стабильности"""
        manager = UIStabilityManager()
        assert manager is not None
        assert hasattr(manager, '_widget_registry')
        assert hasattr(manager, '_error_handlers')
        assert hasattr(manager, '_stability_metrics')
        
    def test_widget_registration(self, app):
        """Тест регистрации виджетов"""
        manager = UIStabilityManager()
        widget = QWidget()
        
        manager.register_widget("test_widget", widget)
        assert "test_widget" in manager._widget_registry
        
        # Проверяем, что ссылка работает
        widget_ref = manager._widget_registry["test_widget"]
        assert widget_ref() is widget
        
    def test_widget_unregistration(self, app):
        """Тест отмены регистрации виджетов"""
        manager = UIStabilityManager()
        widget = QWidget()
        
        manager.register_widget("test_widget", widget)
        manager.unregister_widget("test_widget")
        
        assert "test_widget" not in manager._widget_registry
        
    def test_memory_leak_detection(self, app):
        """Тест обнаружения утечек памяти"""
        manager = UIStabilityManager()
        
        # Создаем виджет и регистрируем его
        widget = QWidget()
        manager.register_widget("test_widget", widget)
        
        # Удаляем виджет, но не отменяем регистрацию
        del widget
        
        # Проверяем обнаружение утечки
        leaked_widgets = manager.check_memory_leaks()
        assert "test_widget" in leaked_widgets
        
    def test_error_handler_registration(self):
        """Тест регистрации обработчиков ошибок"""
        manager = UIStabilityManager()
        
        def test_handler(error, context):
            pass
            
        manager.register_error_handler("test_error", test_handler)
        assert "test_error" in manager._error_handlers
        
    def test_error_handling(self):
        """Тест обработки ошибок"""
        manager = UIStabilityManager()
        
        handled_errors = []
        
        def test_handler(error, context):
            handled_errors.append((error, context))
            
        manager.register_error_handler("test_error", test_handler)
        
        test_error = Exception("Test error")
        test_context = {"key": "value"}
        
        manager.handle_error("test_error", test_error, test_context)
        
        assert len(handled_errors) == 1
        assert handled_errors[0][0] is test_error
        assert handled_errors[0][1] == test_context
        
    def test_stability_metrics(self, app):
        """Тест метрик стабильности"""
        manager = UIStabilityManager()
        
        # Регистрируем виджет
        widget = QWidget()
        manager.register_widget("test_widget", widget)
        
        metrics = manager.get_stability_metrics()
        
        assert 'widget_creation_errors' in metrics
        assert 'widget_destruction_errors' in metrics
        assert 'memory_leaks_detected' in metrics
        assert 'fallback_activations' in metrics
        assert 'registered_widgets' in metrics
        assert 'active_widgets' in metrics
        
        assert metrics['registered_widgets'] >= 1
        assert metrics['active_widgets'] >= 1


@pytest.mark.skipif(not STABILITY_ENHANCEMENTS_AVAILABLE, reason="Улучшения стабильности недоступны")
class TestStabilityDecorators:
    """Тесты декораторов стабильности"""
    
    def test_stable_widget_creation_success(self, app):
        """Тест успешного создания виджета с декоратором"""
        
        @stable_widget_creation()
        def create_widget():
            return QWidget()
            
        widget = create_widget()
        assert widget is not None
        assert isinstance(widget, QWidget)
        
    def test_stable_widget_creation_with_fallback(self, app):
        """Тест создания виджета с fallback при ошибке"""
        
        def fallback_factory():
            return QTextEdit()
            
        @stable_widget_creation(fallback_factory=fallback_factory)
        def create_widget():
            raise Exception("Test error")
            
        widget = create_widget()
        assert widget is not None
        assert isinstance(widget, QTextEdit)
        
    def test_safe_widget_operation_success(self, app):
        """Тест успешной операции с виджетом"""
        
        @safe_widget_operation("test_operation")
        def test_operation():
            return "success"
            
        result = test_operation()
        assert result == "success"
        
    def test_safe_widget_operation_error_handling(self, app):
        """Тест обработки ошибок в операциях с виджетами"""
        
        @safe_widget_operation("test_operation")
        def test_operation():
            raise Exception("Test error")
            
        result = test_operation()
        assert result is None  # Должен вернуть None при ошибке


@pytest.mark.skipif(not STABILITY_ENHANCEMENTS_AVAILABLE, reason="Улучшения стабильности недоступны")
class TestStabilityMonitor:
    """Тесты монитора стабильности"""
    
    def test_stability_monitor_initialization(self, app):
        """Тест инициализации монитора стабильности"""
        monitor = StabilityMonitor(check_interval=1000)  # 1 секунда для тестов
        assert monitor is not None
        assert hasattr(monitor, 'timer')
        assert hasattr(monitor, 'check_interval')
        assert monitor.check_interval == 1000
        
    def test_stability_monitor_start_stop(self, app):
        """Тест запуска и остановки мониторинга"""
        monitor = StabilityMonitor(check_interval=1000)
        
        monitor.start_monitoring()
        assert monitor.timer.isActive()
        
        monitor.stop_monitoring()
        assert not monitor.timer.isActive()
        
    def test_stability_check_execution(self, app):
        """Тест выполнения проверки стабильности"""
        monitor = StabilityMonitor(check_interval=1000)
        
        # Мокаем stability_manager для контроля результатов
        with patch('gopiai.ui.components.ui_stability_enhancements.stability_manager') as mock_manager:
            mock_manager.check_memory_leaks.return_value = []
            mock_manager.get_stability_metrics.return_value = {
                'widget_creation_errors': 0,
                'memory_leaks_detected': 0,
                'registered_widgets': 5
            }
            
            # Выполняем проверку
            monitor._perform_stability_check()
            
            # Проверяем, что методы были вызваны
            mock_manager.check_memory_leaks.assert_called_once()
            mock_manager.get_stability_metrics.assert_called_once()


@pytest.mark.skipif(not STABILITY_ENHANCEMENTS_AVAILABLE, reason="Улучшения стабильности недоступны")
class TestEnhancedErrorRecovery:
    """Тесты системы восстановления после ошибок"""
    
    def test_error_recovery_initialization(self):
        """Тест инициализации системы восстановления"""
        recovery = EnhancedErrorRecovery()
        assert recovery is not None
        assert hasattr(recovery, 'recovery_strategies')
        assert hasattr(recovery, 'recovery_history')
        
    def test_recovery_strategy_registration(self):
        """Тест регистрации стратегий восстановления"""
        recovery = EnhancedErrorRecovery()
        
        def test_strategy(error, context):
            return True
            
        recovery.register_recovery_strategy("test_error", test_strategy)
        assert "test_error" in recovery.recovery_strategies
        
    def test_successful_recovery_attempt(self):
        """Тест успешной попытки восстановления"""
        recovery = EnhancedErrorRecovery()
        
        def test_strategy(error, context):
            return True
            
        recovery.register_recovery_strategy("test_error", test_strategy)
        
        test_error = Exception("Test error")
        test_context = {"key": "value"}
        
        success = recovery.attempt_recovery("test_error", test_error, test_context)
        assert success is True
        
        # Проверяем, что запись добавлена в историю
        history = recovery.get_recovery_history()
        assert len(history) == 1
        assert history[0]['error_type'] == "test_error"
        assert history[0]['success'] is True
        
    def test_failed_recovery_attempt(self):
        """Тест неудачной попытки восстановления"""
        recovery = EnhancedErrorRecovery()
        
        def test_strategy(error, context):
            return False
            
        recovery.register_recovery_strategy("test_error", test_strategy)
        
        test_error = Exception("Test error")
        test_context = {"key": "value"}
        
        success = recovery.attempt_recovery("test_error", test_error, test_context)
        assert success is False
        
    def test_recovery_without_strategy(self):
        """Тест восстановления без зарегистрированной стратегии"""
        recovery = EnhancedErrorRecovery()
        
        test_error = Exception("Test error")
        test_context = {"key": "value"}
        
        success = recovery.attempt_recovery("unknown_error", test_error, test_context)
        assert success is False


@pytest.mark.skipif(not STABILITY_ENHANCEMENTS_AVAILABLE, reason="Улучшения стабильности недоступны")
class TestTabWidgetStabilityIntegration:
    """Тесты интеграции улучшений стабильности с TabDocumentWidget"""
    
    def test_tab_widget_with_stability_enhancements(self, app):
        """Тест TabDocumentWidget с улучшениями стабильности"""
        widget = TabDocumentWidget()
        
        # Проверяем, что мониторинг стабильности инициализирован
        assert hasattr(widget, '_init_stability_monitoring')
        
        # Проверяем, что обработчик проблем стабильности подключен
        assert hasattr(widget, '_handle_stability_issue')
        
    def test_notebook_creation_with_stability_decorators(self, app):
        """Тест создания блокнота с декораторами стабильности"""
        widget = TabDocumentWidget()
        
        # Проверяем, что метод add_notebook_tab имеет декораторы
        method = getattr(widget, 'add_notebook_tab')
        assert hasattr(method, '__wrapped__')  # Признак декорированной функции
        
    def test_stability_issue_handling(self, app):
        """Тест обработки проблем стабильности"""
        widget = TabDocumentWidget()
        
        # Мокаем error_display для проверки вызовов
        widget._error_display = Mock()
        
        # Симулируем проблему с утечками памяти
        widget._handle_stability_issue("memory_leaks", {"memory_leaks_detected": 5})
        
        # Проверяем, что ошибка была показана
        widget._error_display.show_generic_error.assert_called_once()
        
        # Симулируем проблему с ошибками создания виджетов
        widget._handle_stability_issue("high_creation_errors", {"widget_creation_errors": 15})
        
        # Проверяем, что ошибка была показана
        assert widget._error_display.show_generic_error.call_count == 2


class TestStabilityIntegration:
    """Интеграционные тесты системы стабильности"""
    
    def test_global_stability_manager_integration(self):
        """Тест интеграции глобального менеджера стабильности"""
        if not STABILITY_ENHANCEMENTS_AVAILABLE:
            pytest.skip("Улучшения стабильности недоступны")
            
        # Проверяем, что глобальные экземпляры доступны
        assert stability_manager is not None
        assert error_recovery is not None
        assert stability_monitor is not None
        
        # Проверяем, что стратегии восстановления по умолчанию зарегистрированы
        assert 'widget_creation' in error_recovery.recovery_strategies
        assert 'memory_leak' in error_recovery.recovery_strategies
        
    def test_end_to_end_stability_workflow(self, app):
        """Тест полного рабочего процесса стабильности"""
        if not STABILITY_ENHANCEMENTS_AVAILABLE:
            pytest.skip("Улучшения стабильности недоступны")
            
        # Создаем TabDocumentWidget
        widget = TabDocumentWidget()
        
        # Создаем несколько вкладок
        tab1 = widget.add_new_tab("Тест 1")
        tab2 = widget.add_new_tab("Тест 2")
        
        # Проверяем, что виджеты зарегистрированы
        assert len(widget._widget_references) >= 2
        
        # Закрываем вкладки
        widget._close_tab(0)
        widget._close_tab(0)  # Индекс сдвигается после первого закрытия
        
        # Проверяем, что ссылки очищены
        assert len(widget._widget_references) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])