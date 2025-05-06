#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска инструмента диагностики пользовательского интерфейса GopiAI.
Позволяет запустить диагностику без запуска основного приложения.
"""

import os
import sys

from PySide6.QtWidgets import QApplication

# Проверяем, что мы в корневой директории проекта
if not os.path.exists("app") or not os.path.exists("requirements.txt"):
    print("Ошибка: Скрипт должен быть запущен из корневой директории проекта GopiAI.")
    sys.exit(1)

# Импортируем модуль диагностики
try:
    from app.ui.debug_ui import run_ui_diagnostics
except ImportError as e:
    print(f"Ошибка при импорте модуля диагностики: {e}")
    print("Убедитесь, что вы запускаете скрипт из корневой директории проекта и виртуальное окружение активировано.")
    sys.exit(1)

def main():
    """Основная функция для запуска инструмента диагностики."""
    print("Запуск инструмента диагностики UI...")

    # Создаем Qt приложение
    app = QApplication(sys.argv)

    # Запускаем диагностику
    run_ui_diagnostics(None)

    # Запускаем цикл обработки событий
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
