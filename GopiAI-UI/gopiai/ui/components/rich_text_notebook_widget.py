"""
RichTextNotebookWidget
=====================

Блокнот с форматированием на основе PySide6 QTextEdit и тулбара форматирования.
Интеграция расширенного движка из rich_text_notebook_extension.wordprocessor.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QTextEdit, 
                               QFontComboBox, QComboBox, QMenu, QTabWidget)
from PySide6.QtGui import QFont, QKeySequence, QAction
from PySide6.QtCore import QSize, Qt
import chardet

class TabContextMenu(QMenu):
    """Контекстное меню для вкладок с опциями закрытия"""
    def __init__(self, tab_widget, tab_index, parent=None):
        super().__init__(parent)
        self.tab_widget = tab_widget
        self.tab_index = tab_index
        
        # Закрыть текущую вкладку
        close_action = QAction("Закрыть вкладку", self)
        close_action.triggered.connect(lambda: self.tab_widget.removeTab(self.tab_index))
        self.addAction(close_action)
        
        # Закрыть все вкладки справа
        close_right_action = QAction("Закрыть вкладки справа", self)
        close_right_action.triggered.connect(self.close_tabs_to_right)
        self.addAction(close_right_action)
        
        # Закрыть все вкладки
        close_all_action = QAction("Закрыть все вкладки", self)
        close_all_action.triggered.connect(self.close_all_tabs)
        self.addAction(close_all_action)
        
        # Отключить опции если нет вкладок справа
        if self.tab_index >= self.tab_widget.count() - 1:
            close_right_action.setEnabled(False)
    
    def close_tabs_to_right(self):
        """Закрыть все вкладки справа от текущей"""
        for i in range(self.tab_widget.count() - 1, self.tab_index, -1):
            self.tab_widget.removeTab(i)
    
    def close_all_tabs(self):
        """Закрыть все вкладки"""
        self.tab_widget.clear()


class CustomTabWidget(QTabWidget):
    """Кастомный QTabWidget с контекстным меню"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """Показать контекстное меню для вкладки"""
        tab_index = self.tabBar().tabAt(position)
        if tab_index >= 0:
            menu = TabContextMenu(self, tab_index, self)
            menu.exec(self.mapToGlobal(position))


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
        # Подключаем обновление тулбара при изменении курсора
        self.editor.cursorPositionChanged.connect(self.update_toolbar_state)
        layout.addWidget(self.editor)

        # Font family
        self.font_box = QFontComboBox()
        self.font_box.currentFontChanged.connect(self.editor.setCurrentFont)
        toolbar.addWidget(self.font_box)
        
        # Font size - исправляем ширину комбобокса
        self.font_size = QComboBox()
        self.font_size.addItems([str(s) for s in [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]])
        self.font_size.setCurrentText("12")  # Устанавливаем размер по умолчанию
        self.font_size.setMinimumWidth(60)  # Минимальная ширина для отображения чисел
        self.font_size.currentTextChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size)
        
        # Bold
        self.bold_action = QAction("B", self)
        self.bold_action.setShortcut(QKeySequence.StandardKey.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(lambda x: self.editor.setFontWeight(QFont.Weight.Bold if x else QFont.Weight.Normal))
        toolbar.addAction(self.bold_action)
        
        # Italic
        self.italic_action = QAction("I", self)
        self.italic_action.setShortcut(QKeySequence.StandardKey.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.editor.setFontItalic)
        toolbar.addAction(self.italic_action)
        
        # Underline
        self.underline_action = QAction("U", self)
        self.underline_action.setShortcut(QKeySequence.StandardKey.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(self.editor.setFontUnderline)
        toolbar.addAction(self.underline_action)
    
    def change_font_size(self, size_text):
        """Изменить размер шрифта"""
        try:
            size = int(size_text)
            self.editor.setFontPointSize(size)
        except ValueError:
            pass  # Игнорируем некорректные значения

    def setHtml(self, html):
        """Установить HTML содержимое"""
        self.editor.setHtml(html)
    
    def toHtml(self):
        """Получить HTML содержимое"""
        return self.editor.toHtml()
    
    def setPlainText(self, text):
        """Установить обычный текст"""
        self.editor.setPlainText(text)
    
    def toPlainText(self):
        """Получить обычный текст"""
        return self.editor.toPlainText()
    
    def clear_content(self):
        """Очистить содержимое редактора"""
        self.editor.clear()
    
    def open_file(self, path):
        """Открыть файл с автоопределением кодировки"""
        try:
            with open(path, 'rb') as f:
                raw = f.read()
            encoding = chardet.detect(raw)['encoding'] or 'utf-8'
            
            # Проверяем, является ли файл HTML
            content = raw.decode(encoding, errors='replace')
            if content.strip().startswith('<') and ('html' in content.lower() or 'body' in content.lower()):
                self.setHtml(content)
            else:
                self.setPlainText(content)
        except Exception as e:
            print(f"Ошибка при открытии файла {path}: {e}")
    
    def save_file(self, path):
        """Сохранить файл в HTML формате"""
        try:
            html = self.toHtml()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(f"Ошибка при сохранении файла {path}: {e}")
    
    def get_current_format(self):
        """Получить текущее форматирование курсора"""
        cursor = self.editor.textCursor()
        format_info = {
            'bold': cursor.charFormat().fontWeight() == QFont.Weight.Bold,
            'italic': cursor.charFormat().fontItalic(),
            'underline': cursor.charFormat().fontUnderline(),
            'font_family': cursor.charFormat().fontFamily(),
            'font_size': cursor.charFormat().fontPointSize()
        }
        return format_info
    
    def update_toolbar_state(self):
        """Обновить состояние кнопок тулбара в соответствии с текущим форматированием"""
        format_info = self.get_current_format()
        
        # Обновляем состояние кнопок без вызова сигналов
        self.bold_action.blockSignals(True)
        self.bold_action.setChecked(format_info['bold'])
        self.bold_action.blockSignals(False)
        
        self.italic_action.blockSignals(True)
        self.italic_action.setChecked(format_info['italic'])
        self.italic_action.blockSignals(False)
        
        self.underline_action.blockSignals(True)
        self.underline_action.setChecked(format_info['underline'])
        self.underline_action.blockSignals(False)
        
        # Обновляем размер шрифта
        if format_info['font_size'] > 0:
            self.font_size.blockSignals(True)
            self.font_size.setCurrentText(str(int(format_info['font_size'])))
            self.font_size.blockSignals(False)
