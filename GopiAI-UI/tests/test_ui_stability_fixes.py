"""
Тесты для проверки исправлений стабильности UI компонентов
========================================================

Проверяет исправления задачи 9: Fix UI component crashes and stability issues
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from gopiai.ui.components.tab_widget import TabDocumentWidget, CustomTabWidget
    from gopiai.ui.components.terminal_widget import TerminalWidget, InteractiveTerminal
    from gopiai.ui.components.error_display import ErrorDisplayWidget
    TAB_WIDGET_AVAILABLE = True
except ImportError as e:
    print(f"Не удалось импортировать компоненты UI: {e}")
    TAB_WIDGET_AVAILABLE = False


@pytest.fixture
def app():
    """Фикстура для создания QApplication"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    # Не закрываем приложение, так как оно может использоваться другими тестами


@pytest.mark.skipif(not TAB_WIDGET_AVAILABLE, reason="UI компоненты недоступны")
class TestTabWidgetStability:
    """Тесты стабильности TabDocumentWidget"""
    
    def test_tab_widget_initialization(self, app):
        """Тест инициализации TabDocumentWidget"""
        widget = TabDocumentWidget()
        assert widget is not None
        assert hasattr(widget, 'tab_widget')
        assert hasattr(widget, 'stacked_widget')
        assert hasattr(widget, '_widget_references')
        assert isinstance(widget._widget_references, dict)
        
    def test_error_display_integration(self, app):
        """Тест интеграции системы отображения ошибок"""
        widget = TabDocumentWidget()
        
        # Проверяем, что система ошибок создана
        if hasattr(widget, '_error_display'):
            assert widget._error_display is not None
            assert hasattr(widget._error_display, 'show_component_error')
            assert hasattr(widget._error_display, 'show_api_error')
            
    def test_notebook_tab_creation_with_error_handling(self, app):
        """Тест создания вкладки блокнота с обработкой ошибок"""
        widget = TabDocumentWidget()
        
        # Тест успешного создания
        with patch('gopiai.ui.components.tab_widget.NOTEBOOK_EDITOR_AVAILABLE', True):
            with patch('gopiai.ui.components.tab_widget.NotebookEditorWidget') as mock_notebook:
                mock_instance = Mock()
                mock_notebook.return_value = mock_instance
                
                result = widget.add_notebook_tab("Тест блокнот")
                
                # Проверяем, что вкладка создана
                assert result is not None
                assert widget.tab_widget.count() > 0
                
                # Проверяем, что ссылка сохранена
                widget_id = id(result)
                assert widget_id in widget._widget_references
                
    def test_notebook_tab_fallback_on_error(self, app):
        """Тест fallback при ошибке создания блокнота"""
        widget = TabDocumentWidget()
        
        # Симулируем ошибку создания NotebookEditorWidget
        with patch('gopiai.ui.components.tab_widget.NOTEBOOK_EDITOR_AVAILABLE', True):
            with patch('gopiai.ui.components.tab_widget.NotebookEditorWidget', side_effect=Exception("Test error")):
                result = widget.add_notebook_tab("Тест блокнот с ошибкой")
                
                # Проверяем, что fallback сработал
                assert result is not None
                assert widget.tab_widget.count() > 0
                
                # Проверяем, что название содержит указание на простой редактор
                tab_text = widget.tab_widget.tabText(widget.tab_widget.count() - 1)
                assert "простой редактор" in tab_text
                
    def test_terminal_tab_creation(self, app):
        """Тест создания вкладки терминала"""
        widget = TabDocumentWidget()
        
        with patch('gopiai.ui.components.tab_widget.InteractiveTerminal') as mock_terminal:
            mock_instance = Mock()
            mock_terminal.return_value = mock_instance
            
            result = widget.add_terminal_tab("Тест терминал")
            
            # Проверяем, что вкладка создана
            assert result is not None
            assert widget.tab_widget.count() > 0
            
            # Проверяем, что ссылка сохранена
            widget_id = id(result)
            assert widget_id in widget._widget_references
            
    def test_tab_closing_cleanup(self, app):
        """Тест очистки ссылок при закрытии вкладок"""
        widget = TabDocumentWidget()
        
        # Создаем вкладку
        editor = widget.add_new_tab("Тест вкладка")
        initial_count = len(widget._widget_references)
        
        # Закрываем вкладку
        widget._close_tab(0)
        
        # Проверяем, что ссылки очищены
        assert len(widget._widget_references) < initial_count
        
    def test_widget_references_prevent_garbage_collection(self, app):
        """Тест предотвращения garbage collection через ссылки"""
        widget = TabDocumentWidget()
        
        # Создаем несколько вкладок
        editor1 = widget.add_new_tab("Вкладка 1")
        editor2 = widget.add_new_tab("Вкладка 2")
        
        # Проверяем, что ссылки сохранены
        assert len(widget._widget_references) >= 2
        
        # Проверяем, что объекты доступны через ссылки
        widget_ids = [id(editor1), id(editor2)]
        for widget_id in widget_ids:
            if widget_id in widget._widget_references:
                assert widget._widget_references[widget_id] is not None


@pytest.mark.skipif(not TAB_WIDGET_AVAILABLE, reason="UI компоненты недоступны")
class TestTerminalWidgetStability:
    """Тесты стабильности TerminalWidget"""
    
    def test_terminal_widget_initialization(self, app):
        """Тест инициализации TerminalWidget"""
        widget = TerminalWidget()
        assert widget is not None
        assert hasattr(widget, 'tabs')
        assert hasattr(widget, '_terminal_references')
        assert isinstance(widget._terminal_references, dict)
        
        # Проверяем singleton
        assert TerminalWidget.instance is widget
        
    def test_terminal_tab_creation(self, app):
        """Тест создания вкладки терминала"""
        widget = TerminalWidget()
        initial_count = widget.tabs.count()
        
        index = widget.add_tab("Новый терминал")
        
        assert index >= 0
        assert widget.tabs.count() == initial_count + 1
        assert len(widget._terminal_references) >= initial_count + 1
        
    def test_terminal_tab_closing(self, app):
        """Тест закрытия вкладки терминала"""
        widget = TerminalWidget()
        
        # Создаем дополнительную вкладку (должна быть минимум одна)
        widget.add_tab("Дополнительный терминал")
        initial_count = widget.tabs.count()
        
        # Закрываем вкладку (не последнюю)
        if initial_count > 1:
            widget.close_tab(1)
            assert widget.tabs.count() == initial_count - 1
            
    def test_terminal_command_execution(self, app):
        """Тест выполнения команд в терминале"""
        widget = TerminalWidget()
        
        with patch.object(widget, 'tabs') as mock_tabs:
            mock_terminal = Mock()
            mock_tabs.currentIndex.return_value = 0
            mock_tabs.count.return_value = 1
            mock_tabs.widget.return_value = mock_terminal
            
            widget.execute_command("echo test")
            
            # Проверяем, что команда была отправлена
            mock_terminal.execute_command.assert_called_once_with("echo test")
            
    def test_terminal_cleanup(self, app):
        """Тест очистки ресурсов терминала"""
        widget = TerminalWidget()
        
        # Создаем несколько вкладок
        widget.add_tab("Терминал 1")
        widget.add_tab("Терминал 2")
        
        initial_refs = len(widget._terminal_references)
        assert initial_refs > 0
        
        # Выполняем очистку
        widget.cleanup()
        
        # Проверяем, что ссылки очищены
        assert len(widget._terminal_references) == 0


@pytest.mark.skipif(not TAB_WIDGET_AVAILABLE, reason="UI компоненты недоступны")
class TestErrorDisplaySystem:
    """Тесты системы отображения ошибок"""
    
    def test_error_display_initialization(self, app):
        """Тест инициализации ErrorDisplayWidget"""
        try:
            widget = ErrorDisplayWidget()
            assert widget is not None
            assert hasattr(widget, 'error_title')
            assert hasattr(widget, 'error_description')
            assert hasattr(widget, 'error_details')
        except ImportError:
            pytest.skip("ErrorDisplayWidget недоступен")
            
    def test_api_error_display(self, app):
        """Тест отображения API ошибок"""
        try:
            widget = ErrorDisplayWidget()
            
            widget.show_api_error("Test API error", "API_ERROR_001", "retry_action")
            
            assert widget.isVisible()
            assert "API" in widget.error_title.text()
            assert "Test API error" in widget.error_description.text()
            assert widget.retry_button.isVisible()
        except ImportError:
            pytest.skip("ErrorDisplayWidget недоступен")
            
    def test_connection_error_display(self, app):
        """Тест отображения ошибок подключения"""
        try:
            widget = ErrorDisplayWidget()
            
            widget.show_connection_error("Test Service")
            
            assert widget.isVisible()
            assert "подключения" in widget.error_title.text()
            assert "Test Service" in widget.error_description.text()
            assert widget.retry_button.isVisible()
        except ImportError:
            pytest.skip("ErrorDisplayWidget недоступен")
            
    def test_component_error_display(self, app):
        """Тест отображения ошибок компонентов"""
        try:
            widget = ErrorDisplayWidget()
            
            widget.show_component_error("TestComponent", "Test error details", fallback_available=True)
            
            assert widget.isVisible()
            assert "TestComponent" in widget.error_title.text()
            assert "резервный режим" in widget.error_description.text()
            assert not widget.retry_button.isVisible()  # Не показываем retry если есть fallback
        except ImportError:
            pytest.skip("ErrorDisplayWidget недоступен")


class TestUIStabilityIntegration:
    """Интеграционные тесты стабильности UI"""
    
    def test_error_handling_integration(self, app):
        """Тест интеграции обработки ошибок"""
        if not TAB_WIDGET_AVAILABLE:
            pytest.skip("UI компоненты недоступны")
            
        widget = TabDocumentWidget()
        
        # Симулируем ошибку и проверяем, что она обрабатывается
        with patch('gopiai.ui.components.tab_widget.logger') as mock_logger:
            with patch('gopiai.ui.components.tab_widget.NotebookEditorWidget', side_effect=Exception("Test error")):
                result = widget.add_notebook_tab("Error test")
                
                # Проверяем, что ошибка залогирована
                mock_logger.error.assert_called()
                
                # Проверяем, что fallback сработал
                assert result is not None
                
    def test_memory_management(self, app):
        """Тест управления памятью"""
        if not TAB_WIDGET_AVAILABLE:
            pytest.skip("UI компоненты недоступны")
            
        widget = TabDocumentWidget()
        
        # Создаем и закрываем много вкладок
        for i in range(10):
            widget.add_new_tab(f"Вкладка {i}")
            
        initial_refs = len(widget._widget_references)
        
        # Закрываем все вкладки
        while widget.tab_widget.count() > 0:
            widget._close_tab(0)
            
        # Проверяем, что ссылки очищены
        assert len(widget._widget_references) < initial_refs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])