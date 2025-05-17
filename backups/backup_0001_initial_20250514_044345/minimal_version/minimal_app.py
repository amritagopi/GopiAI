#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Минимальная версия приложения GopiAI.
Содержит только главное окно, текстовый редактор и меню Файл с пунктами Открыть и Сохранить.
"""

import os
import sys
import logging
import chardet

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout,
    QWidget, QFileDialog, QMessageBox, QMenu, QMenuBar
)
from PySide6.QtGui import QAction, QKeySequence

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalMainWindow(QMainWindow):
    """Минимальное главное окно с текстовым редактором и меню Файл."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GopiAI - Минимальная версия")
        self.resize(800, 600)

        # Текущий файл
        self.current_file = None

        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем и настраиваем текстовый редактор
        self.text_editor = QTextEdit()

        # Создаем макет для центрального виджета
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_editor)

        # Создаем меню
        self.create_menus()

        logger.info("Минимальное приложение инициализировано")

    def create_menus(self):
        """Создает меню приложения."""
        # Создаем строку меню
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # Меню "Файл"
        file_menu = QMenu("Файл", self)
        menubar.addMenu(file_menu)

        # Действие "Открыть"
        open_action = QAction("Открыть", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Действие "Сохранить"
        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Действие "Сохранить как"
        save_as_action = QAction("Сохранить как...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        logger.info("Меню создано")

    def open_file(self):
        """Открывает файл с автоматическим определением кодировки."""
        logger.info("Открытие файла...")
        print("Меню: Открыть файл")

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if file_path:
            try:
                # Читаем файл в бинарном режиме для определения кодировки
                with open(file_path, 'rb') as raw_file:
                    raw_data = raw_file.read()

                # Определяем кодировку
                detected = chardet.detect(raw_data)
                encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
                confidence = detected.get('confidence', 0)

                logger.info(f"Обнаружена кодировка: {encoding} (уверенность: {confidence:.2f})")

                # Декодируем содержимое с обнаруженной кодировкой
                try:
                    content = raw_data.decode(encoding)
                except UnicodeDecodeError:
                    # В случае ошибки пробуем запасные кодировки
                    fallback_encodings = ['cp1251', 'latin-1', 'utf-16', 'ascii']
                    for enc in fallback_encodings:
                        try:
                            content = raw_data.decode(enc)
                            logger.info(f"Использована запасная кодировка: {enc}")
                            encoding = enc
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # Если все кодировки не подошли, используем latin-1, которая всегда работает
                        content = raw_data.decode('latin-1')
                        logger.warning("Использована кодировка latin-1 как крайнее средство")
                        encoding = 'latin-1'

                # Устанавливаем текст в редактор
                self.text_editor.setText(content)
                self.current_file = file_path
                self.current_encoding = encoding
                self.setWindowTitle(f"GopiAI - Минимальная версия - {os.path.basename(file_path)} [{encoding}]")

                logger.info(f"Файл открыт: {file_path} (кодировка: {encoding})")
                print(f"Файл открыт: {file_path} (кодировка: {encoding})")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")
                logger.error(f"Ошибка при открытии файла: {e}")

    def save_file(self):
        """Сохраняет файл."""
        logger.info("Сохранение файла...")
        print("Меню: Сохранить файл")

        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Сохраняет файл с новым именем."""
        logger.info("Сохранение файла с новым именем...")
        print("Меню: Сохранить файл как...")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if file_path:
            self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        """Сохраняет содержимое текстового редактора в файл."""
        try:
            encoding = getattr(self, 'current_encoding', 'utf-8')
            with open(file_path, 'w', encoding=encoding) as file:
                content = self.text_editor.toPlainText()
                file.write(content)

            self.current_file = file_path
            self.setWindowTitle(f"GopiAI - Минимальная версия - {os.path.basename(file_path)} [{encoding}]")
            logger.info(f"Файл сохранен: {file_path} (кодировка: {encoding})")
            print(f"Файл сохранен: {file_path} (кодировка: {encoding})")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
            logger.error(f"Ошибка при сохранении файла: {e}")

def main():
    """Функция запуска приложения."""
    try:
        # Проверяем наличие chardet
        import chardet
    except ImportError:
        print("Установка пакета chardet...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
            print("chardet успешно установлен")
        except Exception as e:
            print(f"Ошибка установки chardet: {e}")
            print("Пожалуйста, установите пакет chardet вручную: pip install chardet")
            sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("GopiAI - Минимальная версия")

    main_window = MinimalMainWindow()
    main_window.show()

    logger.info("Приложение запущено")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
