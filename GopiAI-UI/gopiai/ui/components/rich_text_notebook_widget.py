"""
RichTextNotebookWidget
=====================

Блокнот с форматированием на основе PySide6 QTextEdit и тулбара форматирования.
Интеграция расширенного движка из rich_text_notebook_extension.wordprocessor.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QTextEdit, QFontComboBox, QComboBox
from PySide6.QtGui import QFont, QKeySequence, QAction
from PySide6.QtCore import QSize

# Чистый rich text notebook для вкладок: тулбар + QTextEdit (или rich движок).
class NotebookEditorWidget(QWidget):
    """
    Чистый rich text notebook для вкладок: тулбар + QTextEdit (или rich движок).
    Не использует QMainWindow, не открывает отдельное окно.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Тулбар форматирования
        toolbar = QToolBar("Format")
        toolbar.setIconSize(QSize(16, 16))
        layout.addWidget(toolbar)

        # Редактор
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.setPlaceholderText("Введите заметку...")
        layout.addWidget(self.editor)

        # Font family
        font_box = QFontComboBox()
        font_box.currentFontChanged.connect(self.editor.setCurrentFont)
        toolbar.addWidget(font_box)
        # Font size
        font_size = QComboBox()
        font_size.addItems([str(s) for s in [8, 10, 12, 14, 18, 24, 36, 48]])
        font_size.currentIndexChanged.connect(lambda i: self.editor.setFontPointSize(int(font_size.currentText())))
        toolbar.addWidget(font_size)
        # Bold
        bold_action = QAction("B", self)
        bold_action.setShortcut(QKeySequence.StandardKey.Bold)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(lambda x: self.editor.setFontWeight(QFont.Weight.Bold if x else QFont.Weight.Normal))
        toolbar.addAction(bold_action)
        # Italic
        italic_action = QAction("I", self)
        italic_action.setShortcut(QKeySequence.StandardKey.Italic)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(self.editor.setFontItalic)
        toolbar.addAction(italic_action)
        # Underline
        underline_action = QAction("U", self)
        underline_action.setShortcut(QKeySequence.StandardKey.Underline)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.editor.setFontUnderline)
        toolbar.addAction(underline_action)

    def setHtml(self, html):
        self.editor.setHtml(html)
    def toHtml(self):
        return self.editor.toHtml()
    def setPlainText(self, text):
        self.editor.setPlainText(text)
    def toPlainText(self):
        return self.editor.toPlainText()
    def open_file(self, path):
        import chardet
        with open(path, 'rb') as f:
            raw = f.read()
        encoding = chardet.detect(raw)['encoding'] or 'utf-8'
        html = raw.decode(encoding, errors='replace')
        self.setHtml(html)
    def save_file(self, path):
        html = self.toHtml()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        html = self.toHtml()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
