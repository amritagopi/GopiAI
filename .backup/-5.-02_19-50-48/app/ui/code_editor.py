import sys
import os
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QTextEdit, QSizePolicy, QApplication, QMessageBox, QMenu
from PySide6.QtGui import QPainter, QColor, QTextFormat, QFont, QTextCharFormat, QSyntaxHighlighter, QKeyEvent, QContextMenuEvent, QAction
from PySide6.QtCore import Qt, QRect, QSize, QMimeData, Signal
import re

# Импортируем наш хайлайтер
from .syntax_highlighter import PythonHighlighter


class LineNumberArea(QTextEdit):
    """Область с номерами строк для редактора кода."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setCursor(Qt.ArrowCursor)

        # Устанавливаем формат
        self.setFrameStyle(0)
        font = QFont("Courier New", 10)
        self.setFont(font)

        # Серый фон для зоны номеров строк
        self.setStyleSheet("background-color: #F0F0F0; color: #808080;")

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        # Делегируем отрисовку редактору
        self.editor.lineNumberAreaPaintEvent(event)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса Python."""

    def __init__(self, document):
        super().__init__(document)

        self.highlighting_rules = []

        # Ключевые слова Python
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def", "del",
            "elif", "else", "except", "False", "finally", "for", "from", "global",
            "if", "import", "in", "is", "lambda", "None", "nonlocal", "not", "or",
            "pass", "raise", "return", "True", "try", "while", "with", "yield"
        ]

        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Строки в одинарных кавычках
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Строки в двойных кавычках
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))

        # Комментарии
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        self.highlighting_rules.append((re.compile(r"#[^\n]*"), comment_format))

        # Функции
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#800000"))
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r"\bdef\s+(\w+)\s*\("), function_format))
        self.highlighting_rules.append((re.compile(r"\bclass\s+(\w+)\s*[:\(]"), function_format))

        # Числа
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#A020A0"))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+\b"), number_format))

    def highlightBlock(self, text):
        """Подсвечивает блок текста."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class CodeEditor(QPlainTextEdit):
    """Редактор кода с подсветкой синтаксиса и номерами строк."""

    # Сигнал для отправки кода в чат
    send_to_chat = Signal(str)

    # Сигнал для проверки кода
    check_code = Signal(str)

    # Сигнал для запуска кода
    run_code = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Включаем перенос по словам
        self.setWordWrapMode(QTextOption.NoWrap)

        # Устанавливаем моноширинный шрифт
        font = QFont("Courier New", 10)
        self.setFont(font)

        # Устанавливаем отступы табуляции
        self.setTabStopDistance(40)  # 40 пикселей

        # Добавляем область с номерами строк
        self.line_number_area = LineNumberArea(self)

        # Подключаем сигналы
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Обновляем ширину области номеров строк
        self.update_line_number_area_width(0)

        # Подсвечиваем текущую строку
        self.highlight_current_line()

        # Добавляем подсветку синтаксиса Python
        self.highlighter = PythonSyntaxHighlighter(self.document())

        # Устанавливаем стиль для редактора
        self.setStyleSheet("background-color: #FFFFFF; color: #000000;")

    def line_number_area_width(self):
        """Вычисляет ширину области номеров строк."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Обновляет ширину области номеров строк."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Обновляет область номеров строк при прокрутке редактора."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        """Отрисовывает область номеров строк."""
        painter = QPainter(self.line_number_area.viewport())
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#808080"))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 5, self.fontMetrics().height(),
                    Qt.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        """Подсвечивает текущую строку."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#F0F8FF")  # Светло-голубой цвет
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, event: QKeyEvent):
        """Обрабатывает нажатия клавиш."""
        # Автоматический отступ при нажатии Enter
        if event.key() == Qt.Key_Return and not event.modifiers() & (Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier):
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()

            # Вычисляем отступ из текущей строки
            indent = ""
            for char in text:
                if char == ' ' or char == '\t':
                    indent += char
                else:
                    break

            # Если строка заканчивается двоеточием, добавляем дополнительный отступ
            if text.strip().endswith(':'):
                if '\t' in indent:
                    indent += '\t'  # Добавляем табуляцию
                else:
                    indent += '    '  # Добавляем 4 пробела

            # Вставляем новую строку с отступом
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        else:
            # Стандартная обработка для других клавиш
            super().keyPressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Переопределяем стандартное контекстное меню."""
        menu = self.createStandardContextMenu()

        # Получаем выделенный текст
        selected_text = self.textCursor().selectedText()

        if selected_text:
            # Добавляем разделитель
            menu.addSeparator()

            # Добавляем раздел для работы с кодом
            code_menu = QMenu("Code Actions", menu)

            # Отправить код в чат
            send_to_chat_action = QAction("Send to Chat", self)
            send_to_chat_action.triggered.connect(lambda: self.send_to_chat.emit(selected_text))
            code_menu.addAction(send_to_chat_action)

            # Проверить код
            check_code_action = QAction("Check Code", self)
            check_code_action.triggered.connect(lambda: self.check_code.emit(selected_text))
            code_menu.addAction(check_code_action)

            # Запустить код
            run_code_action = QAction("Run Code", self)
            run_code_action.triggered.connect(lambda: self.run_code.emit(selected_text))
            code_menu.addAction(run_code_action)

            # Добавляем меню кода в основное меню
            menu.addMenu(code_menu)

        menu.exec_(event.globalPos())

    # Реализация перетаскивания файлов
    def dragEnterEvent(self, event):
        """Обрабатывает событие при начале перетаскивания элемента на редактор."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        """Обрабатывает событие при перетаскивании файла на редактор."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # Проверяем, является ли файл текстовым
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.setPlainText(f.read())

                    # Сохраняем путь к файлу в атрибуте редактора
                    self.file_path = file_path

                    # Обновляем заголовок вкладки, если это возможно
                    if hasattr(self.parent(), 'central_tabs'):
                        current_index = self.parent().central_tabs.indexOf(self)
                        if current_index >= 0:
                            self.parent().central_tabs.setTabText(current_index, os.path.basename(file_path))

                    # Сбрасываем флаг модификации документа
                    self.document().setModified(False)
                except Exception as e:
                    # Показываем сообщение об ошибке
                    QMessageBox.critical(self, self.tr("Ошибка"), self.tr(f"Ошибка при открытии файла: {e}"))

            event.acceptProposedAction()
        else:
            super().dropEvent(event)

# Пример запуска для теста
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText("This is a test.\nLine 2\nLine 3")
    editor.resize(600, 400)
    editor.show()
    sys.exit(app.exec())
