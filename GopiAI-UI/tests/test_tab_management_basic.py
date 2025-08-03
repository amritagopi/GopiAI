"""
Базовые тесты для улучшенного управления вкладками
================================================

Упрощенные тесты без проблемных компонентов
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import Qt, QPoint

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gopiai.ui.components.tab_widget import TabDocumentWidget, CustomTabWidget


class TestBasicTabManagement:
    """Базовые тесты управления вкладками"""

    @pytest.fixture
    def app(self):
        """Фикстура для QApplication"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def tab_widget(self, app):
        """Фикстура для TabDocumentWidget"""
        widget = TabDocumentWidget()
        yield widget
        try:
            widget.force_cleanup()
            widget.deleteLater()
        except:
            pass

    def test_basic_tab_creation(self, tab_widget):
        """Тест базового создания вкладок"""
        # Создаем текстовую вкладку
        editor = tab_widget.add_new_tab("Тест", "Тестовый контент")
        
        assert editor is not None
        assert tab_widget.tab_widget.count() == 1
        
        # Проверяем заголовок (может быть изменен fallback механизмом)
        tab_title = tab_widget.tab_widget.tabText(0)
        assert "тест" in tab_title.lower()

    def test_display_switching(self, tab_widget):
        """Тест переключения отображения между фоном и вкладками"""
        # Изначально должен отображаться фон
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget
        
        # Создаем вкладку
        tab_widget.add_new_tab("Тест")
        
        # Должны переключиться на вкладки
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.tab_widget
        
        # Закрываем вкладку
        tab_widget._close_tab(0)
        
        # Должны вернуться к фону
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_safe_tab_closing(self, tab_widget):
        """Тест безопасного закрытия вкладок"""
        # Создаем несколько вкладок
        tab_widget.add_new_tab("Вкладка 1")
        tab_widget.add_new_tab("Вкладка 2")
        tab_widget.add_new_tab("Вкладка 3")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем среднюю вкладку
        tab_widget._close_tab(1)
        
        assert tab_widget.tab_widget.count() == 2

    def test_close_all_tabs_operation(self, tab_widget):
        """Тест операции закрытия всех вкладок"""
        # Создаем несколько вкладок
        for i in range(3):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем все вкладки
        tab_widget.tab_widget._safe_close_all_tabs()
        
        assert tab_widget.tab_widget.count() == 0
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_close_other_tabs_operation(self, tab_widget):
        """Тест операции закрытия других вкладок"""
        # Создаем несколько вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем все кроме вкладки с индексом 2
        tab_widget.tab_widget._safe_close_other_tabs(2)
        
        assert tab_widget.tab_widget.count() == 1

    def test_close_tabs_to_left(self, tab_widget):
        """Тест закрытия вкладок слева"""
        # Создаем несколько вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем вкладки слева от индекса 2
        tab_widget.tab_widget._safe_close_tabs_to_left(2)
        
        assert tab_widget.tab_widget.count() == 3

    def test_close_tabs_to_right(self, tab_widget):
        """Тест закрытия вкладок справа"""
        # Создаем несколько вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем вкладки справа от индекса 2
        tab_widget.tab_widget._safe_close_tabs_to_right(2)
        
        assert tab_widget.tab_widget.count() == 3

    def test_invalid_index_handling(self, tab_widget):
        """Тест обработки невалидных индексов"""
        # Создаем одну вкладку
        tab_widget.add_new_tab("Единственная")
        
        # Пытаемся закрыть несуществующие вкладки
        tab_widget._close_tab(-1)  # Отрицательный индекс
        tab_widget._close_tab(10)  # Слишком большой индекс
        
        # Вкладка должна остаться
        assert tab_widget.tab_widget.count() == 1

    def test_widget_cleanup(self, tab_widget):
        """Тест очистки виджетов"""
        # Создаем вкладку
        editor = tab_widget.add_new_tab("Тест очистки")
        widget_id = id(editor)
        
        # Проверяем регистрацию
        assert widget_id in tab_widget._widget_references
        
        # Закрываем вкладку
        tab_widget._close_tab(0)
        
        # Проверяем очистку
        assert widget_id not in tab_widget._widget_references

    def test_stability_metrics(self, tab_widget):
        """Тест получения метрик стабильности"""
        # Создаем вкладки
        tab_widget.add_new_tab("Метрика 1")
        tab_widget.add_new_tab("Метрика 2")
        
        metrics = tab_widget.get_stability_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_tabs' in metrics
        assert metrics['total_tabs'] == 2

    def test_force_cleanup(self, tab_widget):
        """Тест принудительной очистки"""
        # Создаем вкладки
        for i in range(3):
            tab_widget.add_new_tab(f"Очистка {i+1}")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Принудительная очистка
        tab_widget.force_cleanup()
        
        assert tab_widget.tab_widget.count() == 0
        assert len(tab_widget._widget_references) == 0

    def test_tab_close_prevention(self, tab_widget):
        """Тест предотвращения рекурсивного закрытия"""
        # Создаем вкладки
        for i in range(3):
            tab_widget.add_new_tab(f"Рекурсия {i+1}")
        
        # Устанавливаем флаг операции
        tab_widget.tab_widget._tab_close_in_progress = True
        
        initial_count = tab_widget.tab_widget.count()
        tab_widget.tab_widget._safe_close_tab_at_index(0)
        
        # Количество не должно измениться
        assert tab_widget.tab_widget.count() == initial_count
        
        # Сбрасываем флаг
        tab_widget.tab_widget._tab_close_in_progress = False

    def test_background_image_display(self, tab_widget):
        """Тест отображения фонового изображения"""
        # Проверяем наличие фонового виджета
        assert tab_widget.background_widget is not None
        
        # Изначально должен отображаться фон
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget
        
        # Проверяем метод обеспечения отображения фона
        tab_widget._ensure_background_display()
        
        # Фон должен остаться активным
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_error_tab_creation(self, tab_widget):
        """Тест создания вкладки с ошибкой"""
        error_tab = tab_widget._create_error_tab("Тестовая ошибка", "Детали ошибки")
        
        assert error_tab is not None
        assert tab_widget.tab_widget.count() == 1
        assert "ошибка" in tab_widget.tab_widget.tabText(0).lower()

    def test_file_opening_error_handling(self, tab_widget):
        """Тест обработки ошибок при открытии файлов"""
        # Пытаемся открыть несуществующий файл
        editor = tab_widget.open_file_in_tab("/nonexistent/file.txt")
        
        assert editor is not None  # Должна создаться вкладка с ошибкой
        assert tab_widget.tab_widget.count() == 1

    def test_update_display_error_handling(self, tab_widget):
        """Тест обработки ошибок при обновлении отображения"""
        # Создаем вкладку
        tab_widget.add_new_tab("Тест отображения")
        
        # Вызываем обновление отображения (не должно быть ошибок)
        try:
            tab_widget._update_display()
            success = True
        except Exception:
            success = False
            
        assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])