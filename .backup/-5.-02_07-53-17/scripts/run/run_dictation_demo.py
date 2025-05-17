#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Демонстрационный скрипт для тестирования функции диктовки.
Показывает простое окно с виджетом диктовки для проверки его работы.
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton

# Устанавливаем путь к корню проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем компоненты диктовки
from app.voice.dictation_manager import DictationManager
from app.ui.dictation_widget import DictationWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DictationDemoWindow(QMainWindow):
    """Демонстрационное окно для тестирования диктовки."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Демонстрация диктовки")
        self.setGeometry(100, 100, 600, 500)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Создаем вертикальный макет
        layout = QVBoxLayout(central_widget)

        # Добавляем текстовое поле для вывода распознанного текста
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Здесь появится распознанный текст...")
        layout.addWidget(self.text_edit)

        # Создаем виджет диктовки
        self.dictation_widget = DictationWidget()
        self.dictation_widget.textRecognized.connect(self._on_text_recognized)
        layout.addWidget(self.dictation_widget)

        # Добавляем кнопку для добавления текста в виде нового сообщения
        self.add_message_button = QPushButton("Добавить как новое сообщение")
        self.add_message_button.setEnabled(False)
        self.add_message_button.clicked.connect(self._add_as_message)
        layout.addWidget(self.add_message_button)

        self.last_text = ""

    def _on_text_recognized(self, text):
        """Обработчик распознанного текста."""
        if text:
            self.text_edit.setText(text)
            self.last_text = text
            self.add_message_button.setEnabled(True)
            logger.info(f"Распознанный текст: {text[:50]}...")

    def _add_as_message(self):
        """Добавляет распознанный текст в виде нового сообщения."""
        if self.last_text:
            self.text_edit.append("\n\n" + self.last_text)
            self.last_text = ""
            self.add_message_button.setEnabled(False)
            logger.info("Текст добавлен как новое сообщение")

def run_dictation_demo():
    """Запускает демонстрационное окно диктовки."""
    app = QApplication(sys.argv)
    window = DictationDemoWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    run_dictation_demo()
