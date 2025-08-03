"""
UI Stability Enhancements для GopiAI
===================================

Дополнительные улучшения стабильности UI компонентов.
Расширяет функциональность исправлений задачи 9.
"""

import logging
import weakref
import gc
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QTimer, QObject, Signal
import traceback

logger = logging.getLogger(__name__)


class UIStabilityManager:
    """Менеджер стабильности UI компонентов"""
    
    def __init__(self):
        self._widget_registry: Dict[str, weakref.ref] = {}
        self._error_handlers: Dict[str, Callable] = {}
        self._stability_metrics = {
            'widget_creation_errors': 0,
            'widget_destruction_errors': 0,
            'memory_leaks_detected': 0,
            'fallback_activations': 0
        }
        
    def register_widget(self, widget_id: str, widget: QWidget):
        """Регистрация виджета для мониторинга"""
        try:
            self._widget_registry[widget_id] = weakref.ref(widget, self._on_widget_destroyed)
            logger.debug(f"Зарегистрирован виджет: {widget_id}")
        except Exception as e:
            logger.error(f"Ошибка регистрации виджета {widget_id}: {e}")
            
    def unregister_widget(self, widget_id: str):
        """Отмена регистрации виджета"""
        try:
            if widget_id in self._widget_registry:
                del self._widget_registry[widget_id]
                logger.debug(f"Отменена регистрация виджета: {widget_id}")
        except Exception as e:
            logger.error(f"Ошибка отмены регистрации виджета {widget_id}: {e}")
            
    def _on_widget_destroyed(self, widget_ref):
        """Обработка уничтожения виджета"""
        try:
            # Находим и удаляем из реестра
            for widget_id, ref in list(self._widget_registry.items()):
                if ref is widget_ref:
                    del self._widget_registry[widget_id]
                    logger.debug(f"Виджет {widget_id} корректно уничтожен")
                    break
        except Exception as e:
            logger.error(f"Ошибка обработки уничтожения виджета: {e}")
            self._stability_metrics['widget_destruction_errors'] += 1
            
    def register_error_handler(self, error_type: str, handler: Callable):
        """Регистрация обработчика ошибок"""
        self._error_handlers[error_type] = handler
        logger.debug(f"Зарегистрирован обработчик ошибок: {error_type}")
        
    def handle_error(self, error_type: str, error: Exception, context: Dict[str, Any] = None):
        """Обработка ошибки через зарегистрированный обработчик"""
        try:
            if error_type in self._error_handlers:
                self._error_handlers[error_type](error, context or {})
            else:
                self._default_error_handler(error_type, error, context or {})
        except Exception as handler_error:
            logger.critical(f"Ошибка в обработчике ошибок {error_type}: {handler_error}")
            
    def _default_error_handler(self, error_type: str, error: Exception, context: Dict[str, Any]):
        """Обработчик ошибок по умолчанию"""
        logger.error(f"Необработанная ошибка {error_type}: {error}")
        logger.error(f"Контекст: {context}")
        logger.error(f"Трассировка: {traceback.format_exc()}")
        
    def check_memory_leaks(self) -> List[str]:
        """Проверка утечек памяти"""
        leaked_widgets = []
        try:
            for widget_id, widget_ref in list(self._widget_registry.items()):
                if widget_ref() is None:
                    # Виджет был уничтожен, но не удален из реестра
                    leaked_widgets.append(widget_id)
                    del self._widget_registry[widget_id]
                    
            if leaked_widgets:
                self._stability_metrics['memory_leaks_detected'] += len(leaked_widgets)
                logger.warning(f"Обнаружены потенциальные утечки памяти: {leaked_widgets}")
                
        except Exception as e:
            logger.error(f"Ошибка проверки утечек памяти: {e}")
            
        return leaked_widgets
        
    def get_stability_metrics(self) -> Dict[str, Any]:
        """Получение метрик стабильности"""
        return {
            **self._stability_metrics,
            'registered_widgets': len(self._widget_registry),
            'active_widgets': len([ref for ref in self._widget_registry.values() if ref() is not None])
        }
        
    def force_garbage_collection(self):
        """Принудительная сборка мусора"""
        try:
            collected = gc.collect()
            logger.debug(f"Собрано {collected} объектов сборщиком мусора")
            return collected
        except Exception as e:
            logger.error(f"Ошибка принудительной сборки мусора: {e}")
            return 0


# Глобальный экземпляр менеджера стабильности
stability_manager = UIStabilityManager()


def stable_widget_creation(fallback_factory: Optional[Callable] = None):
    """Декоратор для стабильного создания виджетов с fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    # Регистрируем успешно созданный виджет
                    widget_id = f"{func.__name__}_{id(result)}"
                    stability_manager.register_widget(widget_id, result)
                return result
            except Exception as e:
                logger.error(f"Ошибка создания виджета в {func.__name__}: {e}")
                stability_manager._stability_metrics['widget_creation_errors'] += 1
                
                # Пытаемся использовать fallback
                if fallback_factory:
                    try:
                        fallback_result = fallback_factory(*args, **kwargs)
                        stability_manager._stability_metrics['fallback_activations'] += 1
                        logger.info(f"Активирован fallback для {func.__name__}")
                        return fallback_result
                    except Exception as fallback_error:
                        logger.error(f"Ошибка fallback в {func.__name__}: {fallback_error}")
                
                # Если fallback не сработал, возвращаем None
                return None
        return wrapper
    return decorator


def safe_widget_operation(operation_name: str = "widget_operation"):
    """Декоратор для безопасных операций с виджетами"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка в {operation_name} ({func.__name__}): {e}")
                stability_manager.handle_error(operation_name, e, {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Ограничиваем длину для логирования
                    'kwargs': str(kwargs)[:100]
                })
                return None
        return wrapper
    return decorator


class StabilityMonitor(QObject):
    """Монитор стабильности UI с периодическими проверками"""
    
    stability_issue_detected = Signal(str, dict)  # Сигнал о проблемах стабильности
    
    def __init__(self, check_interval: int = 30000):  # 30 секунд
        super().__init__()
        self.check_interval = check_interval
        self.timer = QTimer()
        self.timer.timeout.connect(self._perform_stability_check)
        
    def start_monitoring(self):
        """Запуск мониторинга стабильности"""
        self.timer.start(self.check_interval)
        logger.info("Запущен мониторинг стабильности UI")
        
    def stop_monitoring(self):
        """Остановка мониторинга стабильности"""
        self.timer.stop()
        logger.info("Остановлен мониторинг стабильности UI")
        
    def _perform_stability_check(self):
        """Выполнение проверки стабильности"""
        try:
            # Проверяем утечки памяти
            leaked_widgets = stability_manager.check_memory_leaks()
            
            # Получаем метрики
            metrics = stability_manager.get_stability_metrics()
            
            # Проверяем критические показатели
            if metrics['widget_creation_errors'] > 10:
                self.stability_issue_detected.emit("high_creation_errors", metrics)
                
            if metrics['memory_leaks_detected'] > 5:
                self.stability_issue_detected.emit("memory_leaks", metrics)
                
            if len(leaked_widgets) > 0:
                self.stability_issue_detected.emit("widget_leaks", {
                    'leaked_widgets': leaked_widgets,
                    'metrics': metrics
                })
                
            # Принудительная сборка мусора при необходимости
            if metrics['registered_widgets'] > 100:
                collected = stability_manager.force_garbage_collection()
                logger.debug(f"Принудительная сборка мусора: собрано {collected} объектов")
                
        except Exception as e:
            logger.error(f"Ошибка проверки стабильности: {e}")


class EnhancedErrorRecovery:
    """Расширенная система восстановления после ошибок"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Регистрация стратегии восстановления"""
        self.recovery_strategies[error_type] = strategy
        logger.debug(f"Зарегистрирована стратегия восстановления: {error_type}")
        
    def attempt_recovery(self, error_type: str, error: Exception, context: Dict[str, Any]) -> bool:
        """Попытка восстановления после ошибки"""
        try:
            if error_type in self.recovery_strategies:
                strategy = self.recovery_strategies[error_type]
                success = strategy(error, context)
                
                # Записываем в историю
                self.recovery_history.append({
                    'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                        'recovery', logging.INFO, '', 0, '', (), None
                    )) if logger.handlers else 'unknown',
                    'error_type': error_type,
                    'success': success,
                    'error': str(error)
                })
                
                if success:
                    logger.info(f"Успешное восстановление после ошибки {error_type}")
                else:
                    logger.warning(f"Неудачная попытка восстановления после ошибки {error_type}")
                    
                return success
            else:
                logger.warning(f"Нет стратегии восстановления для ошибки {error_type}")
                return False
                
        except Exception as recovery_error:
            logger.error(f"Ошибка в процессе восстановления {error_type}: {recovery_error}")
            return False
            
    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Получение истории восстановлений"""
        return self.recovery_history.copy()


# Глобальный экземпляр системы восстановления
error_recovery = EnhancedErrorRecovery()


def setup_default_recovery_strategies():
    """Настройка стратегий восстановления по умолчанию"""
    
    def widget_creation_recovery(error: Exception, context: Dict[str, Any]) -> bool:
        """Стратегия восстановления при ошибках создания виджетов"""
        try:
            # Принудительная сборка мусора
            stability_manager.force_garbage_collection()
            
            # Попытка создания простого fallback виджета
            if 'fallback_factory' in context:
                fallback_factory = context['fallback_factory']
                result = fallback_factory()
                return result is not None
                
            return False
        except Exception:
            return False
            
    def memory_leak_recovery(error: Exception, context: Dict[str, Any]) -> bool:
        """Стратегия восстановления при утечках памяти"""
        try:
            # Очистка реестра виджетов
            leaked_widgets = stability_manager.check_memory_leaks()
            
            # Принудительная сборка мусора
            collected = stability_manager.force_garbage_collection()
            
            return len(leaked_widgets) > 0 or collected > 0
        except Exception:
            return False
            
    # Регистрируем стратегии
    error_recovery.register_recovery_strategy('widget_creation', widget_creation_recovery)
    error_recovery.register_recovery_strategy('memory_leak', memory_leak_recovery)


# Инициализация стратегий восстановления по умолчанию
setup_default_recovery_strategies()


def show_stability_report(parent: Optional[QWidget] = None):
    """Показ отчета о стабильности UI"""
    try:
        metrics = stability_manager.get_stability_metrics()
        recovery_history = error_recovery.get_recovery_history()
        
        report = f"""Отчет о стабильности UI GopiAI

Метрики стабильности:
• Ошибки создания виджетов: {metrics['widget_creation_errors']}
• Ошибки уничтожения виджетов: {metrics['widget_destruction_errors']}
• Обнаружено утечек памяти: {metrics['memory_leaks_detected']}
• Активаций fallback: {metrics['fallback_activations']}
• Зарегистрированных виджетов: {metrics['registered_widgets']}
• Активных виджетов: {metrics['active_widgets']}

История восстановлений: {len(recovery_history)} записей
Успешных восстановлений: {sum(1 for r in recovery_history if r['success'])}
"""
        
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Отчет о стабильности UI")
        msg_box.setText(report)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
        
    except Exception as e:
        logger.error(f"Ошибка показа отчета стабильности: {e}")


# Глобальный монитор стабильности
stability_monitor = StabilityMonitor()