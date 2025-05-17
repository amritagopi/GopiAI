#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска инспектора стилей Qt (qt_style_sheet_inspector).
Этот инструмент позволяет исследовать и редактировать стили виджетов в реальном времени.
"""

import sys
import os
import subprocess
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_demo_script(filename):
    """Создает демонстрационный скрипт для инспектора стилей."""
    with open(filename, "w", encoding='utf-8') as f:
        f.write("import sys\n")
        f.write("import os\n")
        f.write("from PySide6.QtWidgets import (\n")
        f.write("    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,\n")
        f.write("    QLabel, QLineEdit, QComboBox, QCheckBox, QRadioButton,\n")
        f.write("    QSlider, QProgressBar, QTabWidget, QGroupBox, QFormLayout,\n")
        f.write("    QSpinBox, QDateEdit, QTimeEdit, QTextEdit, QScrollBar,\n")
        f.write("    QMenu, QMenuBar, QToolBar, QStatusBar, QHBoxLayout\n")
        f.write(")\n")
        f.write("from PySide6.QtCore import Qt, QSize\n")
        f.write("from PySide6.QtGui import QAction, QIcon, QFont\n\n")

        f.write("# Пытаемся импортировать инспектор стилей\n")
        f.write("try:\n")
        f.write("    from qt_style_sheet_inspector import style_sheet_inspector\n")
        f.write("    has_inspector = True\n")
        f.write("except ImportError:\n")
        f.write("    has_inspector = False\n")
        f.write("    print(\"ОШИБКА: Не удалось импортировать инспектор стилей!\")\n")
        f.write("    print(\"Запускаем демо без инспектора.\")\n\n")

        f.write("class StyleShowcaseWindow(QMainWindow):\n")
        f.write("    \"\"\"Демонстрационное окно с различными виджетами для тестирования стилей.\"\"\"\n")
        f.write("    \n")
        f.write("    def __init__(self):\n")
        f.write("        super().__init__()\n")
        f.write("        \n")
        f.write("        self.setWindowTitle(\"Демонстрация стилей Qt\")\n")
        f.write("        self.setGeometry(100, 100, 900, 700)\n")
        f.write("        \n")
        f.write("        # Создаем главный виджет и макет\n")
        f.write("        central_widget = QWidget()\n")
        f.write("        main_layout = QVBoxLayout(central_widget)\n")
        f.write("        \n")
        f.write("        # Создаем меню\n")
        f.write("        menubar = self.menuBar()\n")
        f.write("        file_menu = menubar.addMenu(\"Файл\")\n")
        f.write("        edit_menu = menubar.addMenu(\"Правка\")\n")
        f.write("        view_menu = menubar.addMenu(\"Вид\")\n")
        f.write("        \n")
        f.write("        # Добавляем действия в меню\n")
        f.write("        exit_action = QAction(\"Выход\", self)\n")
        f.write("        exit_action.triggered.connect(self.close)\n")
        f.write("        file_menu.addAction(exit_action)\n")
        f.write("        \n")
        f.write("        # Создаем вкладки для разных групп элементов\n")
        f.write("        tab_widget = QTabWidget()\n")
        f.write("        main_layout.addWidget(tab_widget)\n")
        f.write("        \n")
        f.write("        # Вкладка 1: Базовые элементы\n")
        f.write("        basic_tab = QWidget()\n")
        f.write("        basic_layout = QVBoxLayout(basic_tab)\n")
        f.write("        \n")
        f.write("        # Группа с кнопками\n")
        f.write("        buttons_group = QGroupBox(\"Кнопки\")\n")
        f.write("        buttons_layout = QVBoxLayout(buttons_group)\n")
        f.write("        \n")
        f.write("        # Добавляем обычные кнопки\n")
        f.write("        normal_button = QPushButton(\"Обычная кнопка\")\n")
        f.write("        buttons_layout.addWidget(normal_button)\n")
        f.write("        \n")
        f.write("        hover_button = QPushButton(\"Кнопка с эффектом наведения\")\n")
        f.write("        hover_button.setStyleSheet('QPushButton { background-color: #3498db; color: white; } QPushButton:hover { background-color: #2980b9; }')\n")
        f.write("        buttons_layout.addWidget(hover_button)\n")
        f.write("        \n")
        f.write("        disabled_button = QPushButton(\"Отключенная кнопка\")\n")
        f.write("        disabled_button.setDisabled(True)\n")
        f.write("        buttons_layout.addWidget(disabled_button)\n")
        f.write("        \n")
        f.write("        basic_layout.addWidget(buttons_group)\n")
        f.write("        \n")
        f.write("        # Добавляем вкладку\n")
        f.write("        tab_widget.addTab(basic_tab, \"Базовые элементы\")\n")
        f.write("        \n")
        f.write("        # Устанавливаем центральный виджет\n")
        f.write("        self.setCentralWidget(central_widget)\n")
        f.write("        \n")
        f.write("        # Запускаем инспектор стилей, если он доступен\n")
        f.write("        if has_inspector:\n")
        f.write("            self.inspector = style_sheet_inspector(self)\n")
        f.write("            self.inspector.show()\n")
        f.write("\n")
        f.write("if __name__ == \"__main__\":\n")
        f.write("    app = QApplication(sys.argv)\n")
        f.write("    window = StyleShowcaseWindow()\n")
        f.write("    window.show()\n")
        f.write("    sys.exit(app.exec())\n")

def run_style_inspector():
    """Запускает инспектор стилей Qt, совместимый с PySide6."""
    try:
        # Проверяем, установлен ли инспектор стилей
        try:
            import qt_style_sheet_inspector
            logger.info("Инспектор стилей уже установлен.")
        except ImportError:
            logger.info("Установка инспектора стилей...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "qt-style-sheet-inspector"])
            logger.info("Инспектор стилей успешно установлен.")

            # Проверяем снова, чтобы убедиться, что установка прошла успешно
            try:
                import qt_style_sheet_inspector
            except ImportError:
                logger.error("Не удалось установить инспектор стилей. Попробуем использовать локальную версию.")

        # Создаем демонстрационное окно с разными виджетами
        logger.info("Создание демонстрационного окна...")

        demo_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_style_inspector_demo.py")
        create_demo_script(demo_script)

        # Запускаем демонстрационный скрипт
        logger.info("Запуск демонстрационного окна...")
        subprocess.Popen([sys.executable, demo_script],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        # Планируем удаление временного файла через некоторое время
        import threading
        def delete_temp_file():
            import time
            time.sleep(10)  # Ждем 10 секунд, чтобы скрипт успел запуститься
            if os.path.exists(demo_script):
                try:
                    os.remove(demo_script)
                    logger.info(f"Временный файл {demo_script} удален.")
                except Exception as e:
                    logger.warning(f"Не удалось удалить временный файл: {e}")

        threading.Thread(target=delete_temp_file).start()

        logger.info("Демонстрационное окно с инспектором стилей запущено.")
        logger.info("Вы можете использовать инспектор для изучения и изменения стилей в реальном времени.")

        return True

    except Exception as e:
        logger.error(f"Ошибка при запуске инспектора стилей: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    run_style_inspector()
