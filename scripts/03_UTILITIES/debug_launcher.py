#!/usr/bin/env python3
"""
Безопасный launcher для GopiAI с детальным логированием
Не изменяет основные файлы!
"""

import os
import sys
import logging
import time
from datetime import datetime

# Устанавливаем переменные окружения для детального логирования
os.environ['GOPIAI_DEBUG'] = 'true'
os.environ['GOPIAI_LOG_LEVEL'] = 'DEBUG'
os.environ['PYTHONPATH'] = '.'

class SuperDetailedFormatter(logging.Formatter):
    """Супер-детальный форматтер для логов"""
    
    def format(self, record):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        level = record.levelname
        location = f"{record.filename}:{record.lineno}"
        function = record.funcName
        message = record.getMessage()
        
        # Разные цвета для разных уровней (если терминал поддерживает)
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        reset = '\033[0m'
        
        color = colors.get(level, '')
        
        return f"{color}[{timestamp}] {level:8} | {location:35} | {function:30} | {message}{reset}"

def setup_detailed_logging():
    """Настройка детального логирования без изменения основных файлов"""
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Убираем старые handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler с детальным форматированием
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(SuperDetailedFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler для сохранения логов
    log_filename = f"gopiai_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Простой форматтер для файла (без цветов)
    file_formatter = logging.Formatter(
        '[%(asctime)s.%(msecs)03d] %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    print(f"🔍 Детальное логирование настроено")
    print(f"📁 Логи сохраняются в: {log_filename}")
    print(f"🎯 Уровень логирования: DEBUG")
    print("=" * 80)
    
    return log_filename

def monkey_patch_imports():
    """Перехватываем все импорты для логирования"""
    
    original_import = __builtins__.__import__
    
    def logged_import(name, globals=None, locals=None, fromlist=(), level=0):
        start_time = time.time()
        logger = logging.getLogger('IMPORT')
        
        try:
            logger.debug(f"📦 ИМПОРТ: {name} (level={level}, fromlist={fromlist})")
            result = original_import(name, globals, locals, fromlist, level)
            duration = time.time() - start_time
            logger.debug(f"✅ ИМПОРТ OK: {name} за {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ ИМПОРТ ОШИБКА: {name} за {duration:.3f}s: {e}")
            raise
    
    __builtins__.__import__ = logged_import
    logging.getLogger('IMPORT').debug("🔧 Monkey-patch импортов активирован")

def patch_pyside_logging():
    """Добавляем логирование для PySide6 событий"""
    
    try:
        from PySide6.QtCore import QObject, QEvent
        
        # Сохраняем оригинальный метод
        original_event = QObject.event
        
        def logged_event(self, event):
            logger = logging.getLogger('QT_EVENTS')
            event_type = event.type()
            
            # Логируем только важные события
            important_events = {
                QEvent.Type.Show: "Show",
                QEvent.Type.Hide: "Hide", 
                QEvent.Type.Close: "Close",
                QEvent.Type.Resize: "Resize",
                QEvent.Type.Paint: "Paint",
                QEvent.Type.MouseButtonPress: "MousePress",
                QEvent.Type.KeyPress: "KeyPress",
            }
            
            if event_type in important_events:
                logger.debug(f"🎭 QT_EVENT: {self.__class__.__name__}.{important_events[event_type]}")
            
            return original_event(self, event)
        
        QObject.event = logged_event
        logging.getLogger('QT_EVENTS').debug("🎭 PySide6 event logging активирован")
        
    except ImportError:
        logging.getLogger('QT_EVENTS').warning("⚠️ PySide6 не найден, пропускаем event logging")

def main():
    """Главная функция с детальным логированием"""
    
    print("🚀 GopiAI Debug Launcher")
    print("=" * 80)
    
    # Настраиваем детальное логирование
    log_file = setup_detailed_logging()
    
    # Активируем перехват импортов
    monkey_patch_imports()
    
    logger = logging.getLogger('LAUNCHER')
    logger.info("🚀 ЗАПУСК GopiAI с детальным логированием")
    
    try:
        # Добавляем путь к модулям GopiAI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        sys.path.insert(0, os.path.join(current_dir, 'GopiAI-UI'))
        
        logger.debug(f"📁 Рабочая директория: {current_dir}")
        logger.debug(f"🐍 Python paths: {sys.path[:3]}...")
        
        # Импортируем и запускаем основное приложение
        logger.info("📦 Импортируем GopiAI UI...")
        
        # Патчим Qt события
        patch_pyside_logging()
        
        # Импортируем главный модуль
        import gopiai.ui.main as gopiai_main
        
        logger.info("🎯 Запускаем main() функцию...")
        
        # Запускаем приложение
        gopiai_main.main()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Приложение остановлено пользователем")
    except Exception as e:
        logger.critical(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logger.critical("📋 FULL TRACEBACK:")
        import traceback
        logger.critical(traceback.format_exc())
        
        print(f"\n💥 ОШИБКА! Подробности в файле: {log_file}")
        return 1
    
    logger.info("✅ GopiAI завершен успешно")
    print(f"\n📁 Подробные логи сохранены в: {log_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
