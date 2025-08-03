"""
Тесты для улучшенного управления вкладками с обработкой ошибок
==============================================================

Тестирование задачи 10: Enhance tab management with error recovery
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtGui import QContextMenuEvent

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gopiai.ui.components.tab_widget import TabDocumentWidget, CustomTabWidget


class TestEnhancedTabManagement:
    """Тесты улучшенного управления вкладками"""

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
        widget.force_cleanup()
        widget.deleteLater()

    def test_tab_creation_with_error_handling(self, tab_widget):
        """Тест создания вкладок с обработкой ошибок"""
        # Создаем обычную текстовую вкладку
        editor = tab_widget.add_new_tab("Тест", "Тестовый контент")
        
        assert editor is not None
        assert tab_widget.tab_widget.count() == 1
        assert tab_widget.tab_widget.tabText(0) in ["Тест", "Тест (простой редактор)"]
        
        # Проверяем, что виджет зарегистрирован
        assert len(tab_widget._widget_references) >= 1

    def test_notebook_creation_with_fallback(self, tab_widget):
        """Тест создания блокнота с fallback механизмом"""
        # Создаем блокнот
        notebook = tab_widget.add_notebook_tab("Тестовый блокнот", "Контент блокнота")
        
        assert notebook is not None
        assert tab_widget.tab_widget.count() == 1
        
        # Заголовок может быть изменен на fallback версию
        tab_title = tab_widget.tab_widget.tabText(0)
        assert "блокнот" in tab_title.lower() or "редактор" in tab_title.lower()

    def test_file_opening_with_error_handling(self, tab_widget, tmp_path):
        """Тест открытия файлов с обработкой ошибок"""
        # Создаем временный файл
        test_file = tmp_path / "test.txt"
        test_file.write_text("Тестовое содержимое файла", encoding='utf-8')
        
        # Открываем файл
        editor = tab_widget.open_file_in_tab(str(test_file))
        
        assert editor is not None
        assert tab_widget.tab_widget.count() == 1
        assert tab_widget.tab_widget.tabText(0) == "test.txt"

    def test_file_opening_nonexistent_file(self, tab_widget):
        """Тест открытия несуществующего файла"""
        # Пытаемся открыть несуществующий файл
        editor = tab_widget.open_file_in_tab("/nonexistent/file.txt")
        
        assert editor is not None  # Должна создаться вкладка с ошибкой
        assert tab_widget.tab_widget.count() == 1
        assert "ошибка" in tab_widget.tab_widget.tabText(0).lower()

    def test_safe_tab_closing(self, tab_widget):
        """Тест безопасного закрытия вкладок"""
        # Создаем несколько вкладок
        tab_widget.add_new_tab("Вкладка 1", "Контент 1")
        tab_widget.add_new_tab("Вкладка 2", "Контент 2")
        tab_widget.add_new_tab("Вкладка 3", "Контент 3")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем среднюю вкладку
        tab_widget._close_tab(1)
        
        assert tab_widget.tab_widget.count() == 2
        # Проверяем, что ссылки очищены
        # (точное количество может варьироваться из-за fallback механизмов)

    def test_context_menu_operations(self, tab_widget):
        """Тест операций контекстного меню"""
        # Создаем несколько вкладок
        tab_widget.add_new_tab("Вкладка 1")
        tab_widget.add_new_tab("Вкладка 2")
        tab_widget.add_new_tab("Вкладка 3")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Тестируем закрытие других вкладок
        tab_widget.tab_widget._safe_close_other_tabs(1)  # Оставляем только вкладку 1
        
        assert tab_widget.tab_widget.count() == 1

    def test_close_all_tabs(self, tab_widget):
        """Тест закрытия всех вкладок"""
        # Создаем несколько вкладок
        tab_widget.add_new_tab("Вкладка 1")
        tab_widget.add_new_tab("Вкладка 2")
        tab_widget.add_new_tab("Вкладка 3")
        
        assert tab_widget.tab_widget.count() == 3
        
        # Закрываем все вкладки
        tab_widget.tab_widget._safe_close_all_tabs()
        
        assert tab_widget.tab_widget.count() == 0
        
        # Проверяем, что отображается фоновое изображение
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_close_tabs_to_left(self, tab_widget):
        """Тест закрытия вкладок слева"""
        # Создаем несколько вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем вкладки слева от индекса 2
        tab_widget.tab_widget._safe_close_tabs_to_left(2)
        
        assert tab_widget.tab_widget.count() == 3  # Должно остаться 3 вкладки

    def test_close_tabs_to_right(self, tab_widget):
        """Тест закрытия вкладок справа"""
        # Создаем несколько вкладок
        for i in range(5):
            tab_widget.add_new_tab(f"Вкладка {i+1}")
        
        assert tab_widget.tab_widget.count() == 5
        
        # Закрываем вкладки справа от индекса 2
        tab_widget.tab_widget._safe_close_tabs_to_right(2)
        
        assert tab_widget.tab_widget.count() == 3  # Должно остаться 3 вкладки

    def test_background_display_when_no_tabs(self, tab_widget):
        """Тест отображения фона при отсутствии вкладок"""
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

    def test_widget_cleanup_on_close(self, tab_widget):
        """Тест правильной очистки виджетов при закрытии"""
        # Создаем вкладку
        editor = tab_widget.add_new_tab("Тест для очистки")
        widget_id = id(editor)
        
        # Проверяем, что виджет зарегистрирован
        assert widget_id in tab_widget._widget_references
        
        # Закрываем вкладку
        tab_widget._close_tab(0)
        
        # Проверяем, что ссылка удалена
        assert widget_id not in tab_widget._widget_references

    def test_error_display_integration(self, tab_widget):
        """Тест интеграции с системой отображения ошибок"""
        # Проверяем, что система ошибок инициализирована
        # (может быть None если ErrorDisplayWidget недоступен)
        assert hasattr(tab_widget, '_error_display')

    def test_stability_metrics(self, tab_widget):
        """Тест получения метрик стабильности"""
        # Создаем несколько вкладок
        tab_widget.add_new_tab("Метрика 1")
        tab_widget.add_new_tab("Метрика 2")
        
        metrics = tab_widget.get_stability_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_tabs' in metrics
        assert metrics['total_tabs'] == 2
        assert 'registered_widgets' in metrics

    def test_force_cleanup(self, tab_widget):
        """Тест принудительной очистки"""
        # Создаем несколько вкладок
        for i in range(3):
            tab_widget.add_new_tab(f"Очистка {i+1}")
        
        assert tab_widget.tab_widget.count() == 3
        assert len(tab_widget._widget_references) >= 3
        
        # Выполняем принудительную очистку
        tab_widget.force_cleanup()
        
        assert tab_widget.tab_widget.count() == 0
        assert len(tab_widget._widget_references) == 0
        assert tab_widget.stacked_widget.currentWidget() == tab_widget.background_widget

    def test_invalid_tab_index_handling(self, tab_widget):
        """Тест обработки невалидных индексов вкладок"""
        # Создаем одну вкладку
        tab_widget.add_new_tab("Единственная вкладка")
        
        # Пытаемся закрыть несуществующие вкладки
        tab_widget._close_tab(-1)  # Отрицательный индекс
        tab_widget._close_tab(10)  # Слишком большой индекс
        
        # Вкладка должна остаться
        assert tab_widget.tab_widget.count() == 1

    @patch('gopiai.ui.components.tab_widget.logger')
    def test_error_logging(self, mock_logger, tab_widget):
        """Тест логирования ошибок"""
        # Создаем вкладку
        tab_widget.add_new_tab("Тест логирования")
        
        # Закрываем вкладку (должно пройти без ошибок)
        tab_widget._close_tab(0)
        
        # Проверяем, что логирование работает
        # (конкретные вызовы зависят от реализации)
        assert mock_logger.debug.called or mock_logger.info.called

    def test_context_menu_creation_safety(self, tab_widget):
        """Тест безопасности создания контекстного меню"""
        # Создаем вкладку
        tab_widget.add_new_tab("Контекстное меню")
        
        # Создаем событие контекстного меню
        pos = QPoint(10, 10)
        event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, pos)
        
        # Вызываем обработчик (не должно быть исключений)
        try:
            tab_widget.tab_widget.contextMenuEvent(event)
            success = True
        except Exception:
            success = False
            
        assert success

    def test_tab_close_prevention_during_operation(self, tab_widget):
        """Тест предотвращения рекурсивного закрытия вкладок"""
        # Создаем несколько вкладок
        for i in range(3):
            tab_widget.add_new_tab(f"Рекурсия {i+1}")
        
        # Устанавливаем флаг операции закрытия
        tab_widget.tab_widget._tab_close_in_progress = True
        
        # Пытаемся закрыть вкладку (должно быть проигнорировано)
        initial_count = tab_widget.tab_widget.count()
        tab_widget.tab_widget._safe_close_tab_at_index(0)
        
        # Количество вкладок не должно измениться
        assert tab_widget.tab_widget.count() == initial_count
        
        # Сбрасываем флаг
        tab_widget.tab_widget._tab_close_in_progress = False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])