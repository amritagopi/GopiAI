#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для восстановления предыдущей версии приложения.
Просто запустите этот скрипт, чтобы вернуться к полной версии GopiAI.
"""

import os
import sys
import logging
import argparse

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def restore_original_version():
    """Восстанавливает оригинальную версию приложения."""
    logger.info("Восстановление оригинальной версии приложения...")

    try:
        # Проверяем, что мы находимся в правильной директории
        if not os.path.exists('../main.py'):
            logger.error("Скрипт должен выполняться из папки minimal_version!")
            sys.exit(1)

        # Запускаем оригинальное приложение
        os.chdir('..')
        logger.info("Запуск оригинальной версии приложения...")
        os.system('python main.py')

        logger.info("Восстановление выполнено успешно.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при восстановлении: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Восстановление оригинальной версии GopiAI")
    parser.add_argument('--no-run', action='store_true', help='Только восстановить, не запускать приложение')

    args = parser.parse_args()

    if args.no_run:
        logger.info("Восстановление без запуска приложения.")
        sys.exit(0)
    else:
        success = restore_original_version()
        sys.exit(0 if success else 1)
