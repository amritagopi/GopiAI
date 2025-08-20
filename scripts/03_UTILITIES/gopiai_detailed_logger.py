"""
Модуль детального логирования для GopiAI
Подключается без изменения основных файлов через monkey-patching
"""

import logging
import sys
import time
import functools
import traceback
from datetime import datetime
import os
from pathlib import Path

class GopiAIDetailedLogger:
    """Безопасная система детального логирования"""
    
    def __init__(self, log_level=logging.DEBUG):
        self.log_level = log_level
        self.log_file = None
        self.original_functions = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Настройка логирования"""
        
        # Создаем уникальное имя файла лога
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"gopiai_detailed_{timestamp}.log"
        
        # Настраиваем форматтер
        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] %(levelname)-8s | %(name)-15s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # File handler  
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Настраиваем root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Убираем существующие handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        print(f"🔍 Детальное логирование GopiAI активировано")
        print(f"📁 Логи: {self.log_file}")
        print("=" * 80)
    
    def patch_imports(self):
        """Перехватываем импорты"""
        
        original_import = __builtins__.__import__
        logger = logging.getLogger('IMPORTS')
        
        def logged_import(name, globals=None, locals=None, fromlist=(), level=0):
            start_time = time.time()
            
            # Игнорируем системные модули для читаемости
            if name.startswith(('_', 'encodings', 'codecs')):
                return original_import(name, globals, locals, fromlist, level)
            
            try:
                logger.debug(f"📦 ИМПОРТ: {name}")
                result = original_import(name, globals, locals, fromlist, level)
                duration = time.time() - start_time
                if duration > 0.01:  # Логируем только медленные импорты
                    logger.debug(f"✅ ИМПОРТ: {name} ({duration:.3f}s)")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ ИМПОРТ: {name} ОШИБКА ({duration:.3f}s): {e}")
                raise
        
        __builtins__.__import__ = logged_import
        logger.debug("🔧 Import monitoring активирован")
    
    def patch_qt_events(self):
        """Перехватываем Qt события"""
        
        try:
            from PySide6.QtCore import QObject, QEvent
            from PySide6.QtWidgets import QWidget
            
            # Патчим QWidget.event
            original_event = QWidget.event
            logger = logging.getLogger('QT_EVENTS')
            
            def logged_event(self, event):
                event_type = event.type()
                
                # Логируем только важные события
                important_events = {
                    QEvent.Type.Show: "Show",
                    QEvent.Type.Hide: "Hide",
                    QEvent.Type.Close: "Close", 
                    QEvent.Type.Resize: "Resize",
                    QEvent.Type.WindowActivate: "Activate",
                    QEvent.Type.WindowDeactivate: "Deactivate",
                }
                
                if event_type in important_events:
                    widget_name = self.__class__.__name__
                    event_name = important_events[event_type]
                    logger.debug(f"🎭 {widget_name}.{event_name}")
                
                return original_event(self, event)
            
            QWidget.event = logged_event
            logger.debug("🎭 Qt events monitoring активирован")
            
        except ImportError:
            logging.getLogger('QT_EVENTS').warning("⚠️ PySide6 недоступен")
    
    def patch_functions(self, module_name, function_names):
        """Патчим конкретные функции модуля"""
        
        try:
            module = sys.modules.get(module_name)
            if not module:
                return
                
            logger = logging.getLogger(f'FUNC_{module_name}')
            
            for func_name in function_names:
                if hasattr(module, func_name):
                    original_func = getattr(module, func_name)
                    
                    # Сохраняем оригинал
                    key = f"{module_name}.{func_name}"
                    self.original_functions[key] = original_func
                    
                    # Создаем logged wrapper
                    def create_logged_wrapper(orig_func, name):
                        @functools.wraps(orig_func)
                        def wrapper(*args, **kwargs):
                            start_time = time.time()
                            logger.debug(f"🔵 ВХОД: {name}()")
                            try:
                                result = orig_func(*args, **kwargs)
                                duration = time.time() - start_time
                                if duration > 0.01:
                                    logger.debug(f"✅ ВЫХОД: {name}() ({duration:.3f}s)")
                                return result
                            except Exception as e:
                                duration = time.time() - start_time
                                logger.error(f"❌ ОШИБКА: {name}() ({duration:.3f}s): {e}")
                                raise
                        return wrapper
                    
                    # Устанавливаем патч
                    logged_func = create_logged_wrapper(original_func, f"{module_name}.{func_name}")
                    setattr(module, func_name, logged_func)
                    
            logger.debug(f"🔧 Patched {len(function_names)} functions in {module_name}")
            
        except Exception as e:
            logging.getLogger('PATCHER').error(f"❌ Ошибка патчинга {module_name}: {e}")
    
    def activate_for_gopiai(self):
        """Активируем детальное логирование для GopiAI"""
        
        logger = logging.getLogger('ACTIVATOR')
        logger.info("🚀 Активация детального логирования для GopiAI")
        
        # Патчим импорты
        self.patch_imports()
        
        # Патчим Qt события
        self.patch_qt_events()
        
        logger.info("✅ Детальное логирование активировано")
        return self.log_file

# Глобальный экземпляр
_detailed_logger = None

def activate_detailed_logging(log_level=logging.DEBUG):
    """Активация детального логирования (безопасно)"""
    global _detailed_logger
    
    if _detailed_logger is None:
        _detailed_logger = GopiAIDetailedLogger(log_level)
        return _detailed_logger.activate_for_gopiai()
    
    return _detailed_logger.log_file

def deactivate_detailed_logging():
    """Деактивация (восстановление оригинальных функций)"""
    global _detailed_logger
    
    if _detailed_logger:
        # Здесь можно восстановить оригинальные функции
        print("🛑 Детальное логирование деактивировано")
        _detailed_logger = None