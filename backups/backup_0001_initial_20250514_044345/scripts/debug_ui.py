#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для диагностики и отладки проблем пользовательского интерфейса GopiAI.
Активирует подробное логирование всех компонентов и взаимодействий UI.
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Настройка расширенного логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(project_root, 'ui_debug.log'), mode='w', encoding='utf-8')
    ]
)

# Логи для различных модулей
ui_logger = logging.getLogger('app.ui')
ui_logger.setLevel(logging.DEBUG)

menu_logger = logging.getLogger('app.ui.menu_manager')
menu_logger.setLevel(logging.DEBUG)

translator_logger = logging.getLogger('app.ui.i18n.translator')
translator_logger.setLevel(logging.DEBUG)

theme_logger = logging.getLogger('app.utils.theme_manager')
theme_logger.setLevel(logging.DEBUG)

signal_logger = logging.getLogger('app.signals')
signal_logger.setLevel(logging.DEBUG)

# Отображаем баннер диагностики
ui_logger.info("="*80)
ui_logger.info("ЗАПУСК ДИАГНОСТИЧЕСКОГО РЕЖИМА UI - ПОДРОБНОЕ ЛОГИРОВАНИЕ АКТИВИРОВАНО")
ui_logger.info("="*80)

# Установка переменных окружения для активации диагностических режимов
os.environ["GOPI_DEBUG_UI"] = "1"
os.environ["GOPI_DEBUG_MENU"] = "1"
os.environ["GOPI_DEBUG_TRANSLATOR"] = "1"
os.environ["GOPI_DEBUG_SIGNALS"] = "1"

# Патчи для отладки UI
def patch_signal_connect():
    """
    Патчит метод connect класса Signal для отладки подключений сигналов.
    """
    from PySide6.QtCore import Signal
    original_connect = Signal.connect

    def debug_connect(self, slot):
        signal_logger.debug(f"Сигнал подключен: {self} -> {slot}")
        return original_connect(self, slot)

    Signal.connect = debug_connect
    signal_logger.info("Патч для отладки сигналов активирован")

def patch_menu_actions():
    """
    Патчит класс QAction для отслеживания взаимодействий с меню.
    """
    from PySide6.QtGui import QAction
    original_trigger = QAction.trigger

    def debug_trigger(self):
        menu_logger.debug(f"Активировано действие меню: {self.text()}")
        return original_trigger(self)

    QAction.trigger = debug_trigger
    menu_logger.info("Патч для отладки действий меню активирован")

def monkey_patch_translator():
    """
    Патчит JsonTranslationManager для подробного логирования переводов.
    """
    from app.ui.i18n.translator import JsonTranslationManager, tr

    original_switch_language = JsonTranslationManager.switch_language

    def debug_switch_language(self, language_code):
        translator_logger.debug(f"[ПОДРОБНО] Переключение языка на {language_code}")
        translator_logger.debug(f"Стек вызовов: {sys._getframe(1).f_code.co_name} в {sys._getframe(1).f_code.co_filename}:{sys._getframe(1).f_lineno}")
        result = original_switch_language(self, language_code)
        translator_logger.debug(f"Результат переключения: {result}")
        return result

    JsonTranslationManager.switch_language = debug_switch_language
    translator_logger.info("Патч для отладки переводчика активирован")

# Импортируем и запускаем основное приложение
if __name__ == "__main__":
    ui_logger.info("Применение патчей для диагностики...")

    try:
        patch_signal_connect()
        patch_menu_actions()
    except Exception as e:
        ui_logger.error(f"Ошибка при применении патчей: {e}")

    ui_logger.info("Запуск основного приложения...")

    # Импортируем основной модуль
    import main

    # Перехватываем все исключения для подробного логирования
    try:
        ui_logger.info("Запуск main()")
        main.main()
    except Exception as e:
        ui_logger.critical(f"Критическая ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)
