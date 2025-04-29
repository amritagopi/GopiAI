import sys
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QTextEdit, QSizePolicy, QApplication
from PySide6.QtGui import QPainter, QColor, QTextFormat, QFont
from PySide6.QtCore import Qt, QRect, QSize

# Импортируем наш хайлайтер
from .syntax_highlighter import PythonHighlighter


class LineNumberArea(QWidget):
    """Виджет для отображения номеров строк."""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    """Редактор кода с нумерацией строк и подсветкой синтаксиса."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        # Применяем подсветку синтаксиса
        self.highlighter = PythonHighlighter(self.document()) # Создаем экземпляр

        # Связываем сигналы для обновления области нумерации
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        # Настройка базовых параметров редактора
        # Используем шрифт из QSS или установим здесь
        # self.setFont(QFont("Consolas", 10)) # Теперь управляется QSS
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # Устанавливаем политику размера для редактора
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Устанавливаем минимальные размеры
        self.setMinimumWidth(200)
        self.setMinimumHeight(100)

    def lineNumberAreaWidth(self):
        """Рассчитывает ширину области нумерации."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        # Добавляем небольшой отступ
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits + 3
        return space

    def updateLineNumberAreaWidth(self, _):
        """Обновляет ширину области нумерации при изменении кол-ва строк."""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        """Перерисовывает область нумерации при скролле."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        """Обновляет геометрию области нумерации при изменении размера редактора."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        """Отрисовывает номера строк."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(Qt.lightGray).lighter(120)) # Фон области

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(Qt.darkGray)) # Цвет номера строки
                painter.drawText(0, int(top), self.line_number_area.width() - 3, int(self.fontMetrics().height()),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        """Подсвечивает текущую строку."""
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)


# Пример запуска для теста
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText("This is a test.\nLine 2\nLine 3")
    editor.resize(600, 400)
    editor.show()
    sys.exit(app.exec())
