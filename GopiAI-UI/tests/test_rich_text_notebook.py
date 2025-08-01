"""
Тесты для RichTextNotebookWidget
===============================

Проверка всех функций текстового редактора с форматированием.
"""

import pytest
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QFont

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gopiai.ui.components.rich_text_notebook_widget import (
    NotebookEditorWidget, 
    CustomTabWidget, 
    TabContextMenu
)


class TestNotebookEditorWidget:
    """Тесты для NotebookEditorWidget"""
    
    @pytest.fixture
    def app(self):
        """Создание QApplication для тестов"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        
    @pytest.fixture
    def widget(self, app):
        """Создание виджета для тестов"""
        widget = NotebookEditorWidget()
        widget.show()
        return widget
    
    def test_widget_creation(self, widget):
        """Тест создания виджета"""
        assert widget is not None
        assert widget.editor is not None
        assert widget.font_box is not None
        assert widget.font_size is not None
        
    def test_placeholder_text(self, widget):
        """Тест placeholder текста"""
        placeholder = widget.editor.placeholderText()
        assert placeholder == "Введите заметку..."
        assert "<" not in placeholder  # Проверяем отсутствие HTML тегов
        
    def test_font_size_combo(self, widget):
        """Тест комбобокса размеров шрифта"""
        # Проверяем, что есть размеры
        assert widget.font_size.count() > 0
        
        # Проверяем минимальную ширину
        assert widget.font_size.minimumWidth() >= 60
        
        # Проверяем, что размер по умолчанию установлен
        assert widget.font_size.currentText() == "12"
        
        # Тестируем изменение размера
        widget.font_size.setCurrentText("18")
        QTest.qWait(100)  # Ждем обработки сигнала
        
    def test_text_operations(self, widget):
        """Тест операций с текстом"""
        test_text = "Тестовый текст"
        
        # Установка обычного текста
        widget.setPlainText(test_text)
        assert widget.toPlainText().strip() == test_text
        
        # Очистка
        widget.clear_content()
        assert widget.toPlainText().strip() == ""
        
        # HTML текст
        html_text = "<b>Жирный текст</b>"
        widget.setHtml(html_text)
        html_result = widget.toHtml()
        assert "жирный" in html_result.lower() or "bold" in html_result.lower()
        
    def test_formatting_actions(self, widget):
        """Тест действий форматирования"""
        # Добавляем текст
        widget.setPlainText("Тест форматирования")
        
        # Выделяем весь текст
        widget.editor.selectAll()
        
        # Тестируем жирный шрифт
        widget.bold_action.trigger()
        assert widget.bold_action.isChecked()
        
        # Тестируем курсив
        widget.italic_action.trigger()
        assert widget.italic_action.isChecked()
        
        # Тестируем подчеркивание
        widget.underline_action.trigger()
        assert widget.underline_action.isChecked()
        
    def test_format_detection(self, widget):
        """Тест определения текущего форматирования"""
        # Устанавливаем форматированный текст
        widget.setHtml("<b><i><u>Форматированный текст</u></i></b>")
        
        # Позиционируем курсор в начало
        cursor = widget.editor.textCursor()
        cursor.setPosition(1)
        widget.editor.setTextCursor(cursor)
        
        # Обновляем состояние тулбара
        widget.update_toolbar_state()
        
        # Проверяем формат
        format_info = widget.get_current_format()
        assert isinstance(format_info, dict)
        assert 'bold' in format_info
        assert 'italic' in format_info
        assert 'underline' in format_info
        
    def test_file_operations(self, widget, tmp_path):
        """Тест операций с файлами"""
        # Создаем временный файл
        test_file = tmp_path / "test.html"
        test_content = "<h1>Заголовок</h1><p>Параграф</p>"
        
        # Сохраняем файл
        widget.setHtml(test_content)
        widget.save_file(str(test_file))
        
        # Проверяем, что файл создан
        assert test_file.exists()
        
        # Очищаем виджет и загружаем файл
        widget.clear_content()
        widget.open_file(str(test_file))
        
        # Проверяем, что содержимое загружено
        loaded_html = widget.toHtml()
        assert "заголовок" in loaded_html.lower() or "h1" in loaded_html.lower()


class TestCustomTabWidget:
    """Тесты для CustomTabWidget с контекстным меню"""
    
    @pytest.fixture
    def app(self):
        """Создание QApplication для тестов"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        
    @pytest.fixture
    def tab_widget(self, app):
        """Создание виджета вкладок для тестов"""
        widget = CustomTabWidget()
        widget.show()
        return widget
    
    def test_tab_widget_creation(self, tab_widget):
        """Тест создания виджета вкладок"""
        assert tab_widget is not None
        assert tab_widget.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
        
    def test_tab_operations(self, tab_widget):
        """Тест операций с вкладками"""
        # Добавляем несколько вкладок
        for i in range(3):
            editor = NotebookEditorWidget()
            tab_widget.addTab(editor, f"Вкладка {i+1}")
        
        assert tab_widget.count() == 3
        
        # Тестируем закрытие вкладки
        tab_widget.removeTab(1)
        assert tab_widget.count() == 2
        
        # Тестируем очистку всех вкладок
        tab_widget.clear()
        assert tab_widget.count() == 0


class TestTabContextMenu:
    """Тесты для контекстного меню вкладок"""
    
    @pytest.fixture
    def app(self):
        """Создание QApplication для тестов"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        
    @pytest.fixture
    def setup_tabs(self, app):
        """Настройка вкладок для тестов"""
        tab_widget = CustomTabWidget()
        
        # Добавляем 5 вкладок
        for i in range(5):
            editor = NotebookEditorWidget()
            tab_widget.addTab(editor, f"Вкладка {i+1}")
        
        return tab_widget
    
    def test_context_menu_creation(self, setup_tabs):
        """Тест создания контекстного меню"""
        tab_widget = setup_tabs
        menu = TabContextMenu(tab_widget, 2)  # Средняя вкладка
        
        assert menu is not None
        assert len(menu.actions()) == 3  # Три действия в меню
        
    def test_close_tabs_to_right(self, setup_tabs):
        """Тест закрытия вкладок справа"""
        tab_widget = setup_tabs
        initial_count = tab_widget.count()
        
        menu = TabContextMenu(tab_widget, 2)  # Вкладка с индексом 2
        menu.close_tabs_to_right()
        
        # Должно остаться 3 вкладки (0, 1, 2)
        assert tab_widget.count() == 3
        assert tab_widget.count() < initial_count
        
    def test_close_all_tabs(self, setup_tabs):
        """Тест закрытия всех вкладок"""
        tab_widget = setup_tabs
        
        menu = TabContextMenu(tab_widget, 0)
        menu.close_all_tabs()
        
        assert tab_widget.count() == 0


def run_manual_test():
    """Ручной тест для визуальной проверки"""
    app = QApplication([])
    
    # Создаем виджет вкладок
    tab_widget = CustomTabWidget()
    
    # Добавляем несколько вкладок с редакторами
    for i in range(3):
        editor = NotebookEditorWidget()
        editor.setPlainText(f"Содержимое вкладки {i+1}")
        tab_widget.addTab(editor, f"Документ {i+1}")
    
    tab_widget.resize(800, 600)
    tab_widget.show()
    
    print("Ручной тест запущен. Проверьте:")
    print("1. Placeholder текст без HTML тегов")
    print("2. Выпадающий список размеров шрифта отображается корректно")
    print("3. Правый клик по вкладке показывает контекстное меню")
    print("4. Форматирование текста работает")
    print("5. Кнопки тулбара обновляются при изменении форматирования")
    
    app.exec()


if __name__ == "__main__":
    # Запуск ручного теста
    run_manual_test()