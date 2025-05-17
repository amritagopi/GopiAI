#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска QStyler - инструмента для тестирования и создания стилей Qt.
Позволяет экспериментировать с различными стилями для вашего приложения.
"""

import sys
import os
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_qstyler():
    """Запускает QStyler в отдельном процессе."""
    try:
        # Сначала попробуем запустить локальную версию стайлера из qt_tools
        logger.info("Проверяем локальную версию QStyler в qt_tools...")
        project_root = os.path.dirname(os.path.abspath(__file__))
        qstyler_path = os.path.join(project_root, "qt_tools", "QStyler")

        if os.path.exists(qstyler_path) and os.path.isdir(qstyler_path):
            logger.info("Найдена локальная версия QStyler. Запускаем...")
            # Проверяем наличие main.py или подобного скрипта запуска
            main_script = os.path.join(qstyler_path, "main.py")
            if os.path.exists(main_script):
                subprocess.Popen([sys.executable, main_script],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
                logger.info("Локальная версия QStyler запущена.")
                return True
            else:
                logger.warning("Не найден скрипт запуска для локальной версии QStyler.")
        else:
            logger.info("Локальная версия QStyler не найдена, попробуем установить и запустить.")

        # Проверяем, установлен ли PyQt5 (обязательное требование для QStyler)
        try:
            import PyQt5
            logger.info("PyQt5 уже установлен.")
        except ImportError:
            logger.info("Установка PyQt5 (обязательное требование для QStyler)...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
            logger.info("PyQt5 успешно установлен.")

        # Проверяем, установлен ли QStyler
        try:
            import QStyler
            logger.info("QStyler уже установлен.")
        except ImportError:
            logger.info("Установка QStyler...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "QStyler"])
            logger.info("QStyler успешно установлен.")

        # Запускаем QStyler
        logger.info("Запуск QStyler...")
        subprocess.Popen([sys.executable, "-m", "QStyler"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

        logger.info("QStyler запущен. Вы можете использовать его для создания и тестирования стилей Qt.")
        logger.info("Подробнее о QStyler: https://github.com/alexpdev/QStyler")

    except Exception as e:
        logger.error(f"Ошибка при запуске QStyler: {e}")
        return False

    return True

def run_style_inspector():
    """Запускает инспектор стилей Qt (qt_style_sheet_inspector)."""
    try:
        logger.info("Проверка локальной версии инспектора стилей...")
        project_root = os.path.dirname(os.path.abspath(__file__))
        inspector_path = os.path.join(project_root, "qt_tools", "qt_style_sheet_inspector")

        if os.path.exists(inspector_path) and os.path.isdir(inspector_path):
            logger.info("Найдена локальная версия инспектора стилей. Запускаем...")
            # Создаем простой тестовый скрипт для запуска инспектора
            test_script = os.path.join(project_root, "temp_inspector_test.py")
            with open(test_script, "w") as f:
                f.write("""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from qt_style_sheet_inspector import style_sheet_inspector

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Инспектор стилей Qt - Тестовое окно")
window.setGeometry(100, 100, 800, 600)

central_widget = QWidget()
layout = QVBoxLayout(central_widget)

button = QPushButton("Тестовая кнопка")
button.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
layout.addWidget(button)

window.setCentralWidget(central_widget)

inspector = style_sheet_inspector(window)
inspector.show()

window.show()
sys.exit(app.exec())
""")

            # Запускаем тестовый скрипт
            subprocess.Popen([sys.executable, test_script],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            logger.info("Инспектор стилей запущен с тестовым окном.")

            # Планируем удаление временного файла через некоторое время
            import threading
            def delete_temp_file():
                import time
                time.sleep(5)  # Ждем 5 секунд, чтобы скрипт успел запуститься
                if os.path.exists(test_script):
                    try:
                        os.remove(test_script)
                        logger.info(f"Временный файл {test_script} удален.")
                    except Exception as e:
                        logger.warning(f"Не удалось удалить временный файл: {e}")

            threading.Thread(target=delete_temp_file).start()
            return True
        else:
            logger.warning("Локальная версия инспектора стилей не найдена.")
            return False

    except Exception as e:
        logger.error(f"Ошибка при запуске инспектора стилей: {e}")
        return False

if __name__ == "__main__":
    # Спрашиваем пользователя, что запустить
    print("\nВыберите инструмент для запуска:")
    print("1 - QStyler (редактор и тестировщик стилей)")
    print("2 - Qt Style Sheet Inspector (инспектор стилей)")

    choice = input("Ваш выбор (1/2): ")

    if choice == "1":
        run_qstyler()
    elif choice == "2":
        run_style_inspector()
    else:
        print("Неверный выбор. Пожалуйста, введите 1 или 2.")
        sys.exit(1)
