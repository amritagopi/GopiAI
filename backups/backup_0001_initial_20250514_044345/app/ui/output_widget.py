import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QComboBox, QLabel, QToolBar
)
from PySide6.QtCore import Qt, Signal, QSize, Slot
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont, QAction

from app.ui.icon_adapter import get_icon
from .i18n.translator import tr


class OutputWidget(QWidget):
    """Виджет для отображения вывода программы."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем панель инструментов
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))

        # Выпадающий список типов вывода
        self.output_label = QLabel(tr("output.type", "Тип вывода:"))
        self.toolbar.addWidget(self.output_label)

        self.output_type = QComboBox()
        self.output_type.addItems([
            tr("output.types.all", "Весь вывод"),
            tr("output.types.stdout", "Стандартный вывод"),
            tr("output.types.stderr", "Ошибки"),
            tr("output.types.debug", "Отладка")
        ])
        self.toolbar.addWidget(self.output_type)

        self.toolbar.addSeparator()

        # Кнопка очистки
        self.clear_action = QAction(get_icon("clear"), tr("output.clear", "Очистить"), self)
        self.clear_action.triggered.connect(self._clear_output)
        self.toolbar.addAction(self.clear_action)

        # Кнопка сохранения
        self.save_action = QAction(get_icon("save"), tr("output.save", "Сохранить"), self)
        self.save_action.triggered.connect(self._save_output)
        self.toolbar.addAction(self.save_action)

        # Добавляем панель инструментов в layout
        self.layout.addWidget(self.toolbar)

        # Создаем текстовое поле для вывода
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setLineWrapMode(QTextEdit.NoWrap)
        self.output_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)

        # Добавляем текстовое поле в layout
        self.layout.addWidget(self.output_text)

        # Подключаем изменение типа вывода
        self.output_type.currentIndexChanged.connect(self._filter_output)

        # Кеш вывода по типам
        self.output_cache = {
            "all": [],
            "stdout": [],
            "stderr": [],
            "debug": []
        }

    def _clear_output(self):
        """Очищает вывод."""
        self.output_text.clear()
        # Очищаем кеш
        for key in self.output_cache:
            self.output_cache[key] = []

    def _save_output(self):
        """Сохраняет вывод в файл."""
        from PySide6.QtWidgets import QFileDialog

        # Запрашиваем файл для сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("dialog.save_output.title", "Сохранить вывод"),
            "",
            tr("dialog.save_output.filter", "Текстовые файлы (*.txt);;Все файлы (*)")
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr("dialog.error.save_output", f"Не удалось сохранить вывод: {str(e)}")
                )

    def _filter_output(self, index):
        """Фильтрует вывод по типу."""
        self.output_text.clear()

        output_type = self.output_type.currentText()

        if output_type == tr("output.types.all", "Весь вывод"):
            for entry in self.output_cache["all"]:
                self._append_formatted_text(entry["text"], entry["type"])
        elif output_type == tr("output.types.stdout", "Стандартный вывод"):
            for entry in self.output_cache["stdout"]:
                self._append_formatted_text(entry["text"], "stdout")
        elif output_type == tr("output.types.stderr", "Ошибки"):
            for entry in self.output_cache["stderr"]:
                self._append_formatted_text(entry["text"], "stderr")
        elif output_type == tr("output.types.debug", "Отладка"):
            for entry in self.output_cache["debug"]:
                self._append_formatted_text(entry["text"], "debug")

    def append_stdout(self, text):
        """Добавляет текст в стандартный вывод."""
        self._cache_output(text, "stdout")
        if self.output_type.currentText() in [tr("output.types.all", "Весь вывод"), tr("output.types.stdout", "Стандартный вывод")]:
            self._append_formatted_text(text, "stdout")

    def append_stderr(self, text):
        """Добавляет текст в вывод ошибок."""
        self._cache_output(text, "stderr")
        if self.output_type.currentText() in [tr("output.types.all", "Весь вывод"), tr("output.types.stderr", "Ошибки")]:
            self._append_formatted_text(text, "stderr")

    def append_debug(self, text):
        """Добавляет текст в отладочный вывод."""
        self._cache_output(text, "debug")
        if self.output_type.currentText() in [tr("output.types.all", "Весь вывод"), tr("output.types.debug", "Отладка")]:
            self._append_formatted_text(text, "debug")

    def _cache_output(self, text, output_type):
        """Кеширует вывод по типу."""
        entry = {"text": text, "type": output_type}
        self.output_cache["all"].append(entry)
        self.output_cache[output_type].append(entry)

    def _append_formatted_text(self, text, output_type):
        """Добавляет отформатированный текст в вывод."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Создаем форматирование для разных типов вывода
        format = QTextCharFormat()
        format.setFontFamily("Consolas, Courier New, monospace")
        format.setFontPointSize(10)

        if output_type == "stdout":
            format.setForeground(QColor("#d4d4d4"))  # Белый
        elif output_type == "stderr":
            format.setForeground(QColor("#f14c4c"))  # Красный
        elif output_type == "debug":
            format.setForeground(QColor("#3a9e3a"))  # Зеленый

        # Добавляем текст с форматированием
        cursor.setCharFormat(format)
        cursor.insertText(text)

        # Прокручиваем вниз
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
