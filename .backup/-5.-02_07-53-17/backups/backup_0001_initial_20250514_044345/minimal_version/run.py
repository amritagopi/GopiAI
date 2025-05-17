#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска минимальной версии приложения GopiAI.
"""

import os
import sys
import logging
import subprocess

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    try:
        logger.info("Проверка наличия PySide6...")
        import PySide6
        logger.info(f"PySide6 установлен. Версия: {PySide6.__version__}")
        return True
    except ImportError:
        logger.error("PySide6 не установлен. Попытка установки...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
            logger.info("PySide6 успешно установлен")
            return True
        except Exception as e:
            logger.error(f"Не удалось установить PySide6: {e}")
            logger.error("Установите PySide6 вручную: pip install PySide6")
            return False

def run_minimal_app():
    """Запускает минимальную версию приложения."""
    logger.info("Запуск минимальной версии приложения...")

    # Проверяем наличие файла приложения
    if not os.path.exists("minimal_app.py"):
        logger.error("Файл minimal_app.py не найден!")
        return False

    # Запускаем приложение
    try:
        subprocess.call([sys.executable, "minimal_app.py"])
        return True
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        return False

if __name__ == "__main__":
    if check_dependencies():
        run_minimal_app()
