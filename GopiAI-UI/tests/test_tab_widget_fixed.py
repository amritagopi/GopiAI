"""
Тесты для исправленной версии управления вкладками
===============================================

Тестирование TabDocumentWidgetFixed
"""

import pytest
import sys
import os
from PySide6.QtWidgets import QApplication

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gopiai.ui.components.tab_widget_fixed import TabDocumentWidgetFixed


class TestTabWidgetFixed:
    """Тесты исправленной версии управления вкладками"""

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
        """Фикстура для TabDocumentWidgetFixed"""
        widget = TabDocumentWidgetFixed()
        yield widget
        try:
            widget.force_cleanup()
            widget.deleteLater()
        except:
            pass

    def test_basic_tab_creation(self, tab_widget):
        """Тест создания базовых вкладок"""
        editor = tab_widget.add_new_tab("Тест", "Тестовый контент")
        
        assert editor is not None
        assert tab_widget.tab_widget.count() == 1
        assert tab_widget.tab_widget.tabText(0) == "Тест"

    def test_display_switching(self, tab_widget):
        """Тест переключения между фоном и вкладками"""
        # Изначально фон
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget
        
        # Создаем вкладку
        tab_widget.add_new_tab("Тест")
        
        # Переключились на вкладки
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.tab_widget
        
        # Закрываем вкладку
        tab_widget._close_tab(0)
        
        # Вернулись к фону
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_single_tab_closing(self, tab_widget):
        """Тест закрытия одной вкладки"""
        # Создаем вкладки
        tab_widget.add_new_tab("Вкладка 1")
        tab_widget.add_new_tab("Вкладка 2")
        tab_widget.add_new_tab("Вкладка 3")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем среднюю
        tab_widget.tab_widget._safe_close_tab(1)
        
        assert tab_widget.tab_widget.count() == 2

    def test_close_all_tabs(self, tab_widget):
        """Тест закрытия всех вкладок"""
        # Создаем вкладки
        for i in range(3):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем все
        tab_widget.tab_widget._safe_close_all()
        
        assert tab_widget.tab_widget.count() == 0
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_close_other_tabs(self, tab_widget):
        """Тест закрытия других вкладок"""
        # Создаем 5 вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем все кроме вкладки с индексом 2
        tab_widget.tab_widget._safe_close_others(2)
        
        assert tab_widget.tab_widget.count() == 1

    def test_close_tabs_to_left(self, tab_widget):
        """Тест закрытия вкладок слева"""
        # Создаем 5 вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем слева от индекса 2
        tab_widget.tab_widget._safe_close_left(2)
        
        assert tab_widget.tab_widget.count() == 3

    def test_close_tabs_to_right(self, tab_widget):
        """Тест закрытия вкладок справа"""
        # Создаем 5 вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем справа от индекса 2
        tab_widget.tab_widget._safe_close_right(2)
        
        assert tab_widget.tab_widget.count() == 3

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

    def test_invalid_index_handling(self, tab_widget):
        """Тест обработки невалидных индексов"""
        # Создаем одну вкладку
        tab_widget.add_new_tab("Единственная")
        
        # Пытаемся закрыть несуществующие
        tab_widget._close_tab(-1)
        tab_widget._close_tab(10)
        
        # Вкладка должна остаться
        assert tab_widget.tab_widget.count() == 1

    def test_operation_in_progress_protection(self, tab_widget):
        """Тест защиты от одновременных операций"""
        # Создаем вкладки
        for i in range(3):
            tab_widget.add_new_tab(f"Защита {i+1}")
        
        # Устанавливаем флаг операции
        tab_widget.tab_widget._operation_in_progress = True
        
        initial_count = tab_widget.tab_widget.count()
        
        # Пытаемся закрыть (должно быть проигнорировано)
        tab_widget.tab_widget._safe_close_tab(0)
        
        assert tab_widget.tab_widget.count() == initial_count
        
        # Сбрасываем флаг
        tab_widget.tab_widget._operation_in_progress = False

    def test_force_cleanup(self, tab_widget):
        """Тест принудительной очистки"""
        # Создаем вкладки
        for i in range(3):
            tab_widget.add_new_tab(f"Очистка {i+1}")
        
        assert tab_widget.tab_widget.count() == 3
        assert len(tab_widget._widget_references) == 3
        
        # Принудительная очистка
        tab_widget.force_cleanup()
        
        assert tab_widget.tab_widget.count() == 0
        assert len(tab_widget._widget_references) == 0
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_stability_metrics(self, tab_widget):
        """Тест получения метрик стабильности"""
        # Создаем вкладки
        tab_widget.add_new_tab("Метрика 1")
        tab_widget.add_new_tab("Метрика 2")
        
        metrics = tab_widget.get_stability_metrics()
        
        assert isinstance(metrics, dict)
        assert metrics['total_tabs'] == 2
        assert metrics['registered_widgets'] == 2
        assert metrics['background_displayed'] == False

    def test_background_display_when_empty(self, tab_widget):
        """Тест отображения фона при отсутствии вкладок"""
        # Изначально фон
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget
        
        # Создаем и закрываем вкладку
        tab_widget.add_new_tab("Временная")
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.tab_widget
        
        tab_widget._close_tab(0)
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_edge_cases(self, tab_widget):
        """Тест граничных случаев"""
        # Закрытие слева от первой вкладки
        tab_widget.add_new_tab("Первая")
        tab_widget.tab_widget._safe_close_left(0)
        assert tab_widget.tab_widget.count() == 1
        
        # Закрытие справа от последней вкладки
        tab_widget.tab_widget._safe_close_right(0)
        assert tab_widget.tab_widget.count() == 1
        
        # Закрытие других при одной вкладке
        tab_widget.tab_widget._safe_close_others(0)
        assert tab_widget.tab_widget.count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])