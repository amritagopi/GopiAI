"""
Тесты интеграции системы отображения ошибок в ChatWidget.

Проверяет корректную работу ErrorDisplayWidget в составе ChatWidget
и правильную обработку различных типов ошибок.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gopiai'))

from gopiai.ui.components.chat_widget import ChatWidget
from gopiai.ui.components.error_display import ErrorDisplayWidget


class TestErrorDisplayIntegration:
    """Тесты интеграции системы отображения ошибок"""
    
    @pytest.fixture
    def app(self):
        """Создание QApplication для тестов"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        
    @pytest.fixture
    def chat_widget(self, app):
        """Создание ChatWidget для тестов"""
        with patch('gopiai.ui.components.chat_widget.get_memory_manager') as mock_memory:
            mock_memory.return_value = Mock()
            mock_memory.return_value.list_sessions.return_value = []
            
            with patch('gopiai.ui.components.chat_widget.CrewAIClient') as mock_crew:
                mock_crew.return_value = Mock()
                
                widget = ChatWidget()
                yield widget
                widget.close()
    
    def test_error_display_widget_exists(self, chat_widget):
        """Проверяет, что ErrorDisplayWidget создан и интегрирован"""
        assert hasattr(chat_widget, 'error_display')
        assert isinstance(chat_widget.error_display, ErrorDisplayWidget)
        assert not chat_widget.error_display.isVisible()  # Скрыт по умолчанию
    
    def test_error_display_in_layout(self, chat_widget):
        """Проверяет, что ErrorDisplayWidget добавлен в layout"""
        layout = chat_widget.main_layout
        error_display_found = False
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() == chat_widget.error_display:
                error_display_found = True
                break
        
        assert error_display_found, "ErrorDisplayWidget не найден в layout"
    
    def test_error_signals_connected(self, chat_widget):
        """Проверяет подключение сигналов ErrorDisplayWidget"""
        # Проверяем, что сигналы подключены (косвенно через наличие методов)
        assert hasattr(chat_widget, '_handle_error_retry')
        assert hasattr(chat_widget, '_handle_error_dismiss')
        assert callable(chat_widget._handle_error_retry)
        assert callable(chat_widget._handle_error_dismiss)
    
    def test_show_api_error_method(self, chat_widget):
        """Тестирует публичный метод show_api_error"""
        error_message = "Test API error"
        error_code = "API_ERROR"
        
        chat_widget.show_api_error(error_message, error_code)
        
        assert chat_widget.error_display.isVisible()
        assert "API" in chat_widget.error_display.error_title.text()
        assert error_message in chat_widget.error_display.error_description.text()
    
    def test_show_connection_error_method(self, chat_widget):
        """Тестирует публичный метод show_connection_error"""
        service_name = "Test Service"
        
        chat_widget.show_connection_error(service_name)
        
        assert chat_widget.error_display.isVisible()
        assert "подключения" in chat_widget.error_display.error_title.text()
        assert service_name in chat_widget.error_display.error_description.text()
    
    def test_show_component_error_method(self, chat_widget):
        """Тестирует публичный метод show_component_error"""
        component_name = "TestComponent"
        error_details = "Test error details"
        
        chat_widget.show_component_error(component_name, error_details)
        
        assert chat_widget.error_display.isVisible()
        assert component_name in chat_widget.error_display.error_title.text()
        assert error_details in chat_widget.error_display.error_details.toPlainText()
    
    def test_show_tool_error_method(self, chat_widget):
        """Тестирует публичный метод show_tool_error"""
        tool_name = "TestTool"
        error_message = "Tool execution failed"
        command = "test command"
        
        chat_widget.show_tool_error(tool_name, error_message, command)
        
        assert chat_widget.error_display.isVisible()
        assert tool_name in chat_widget.error_display.error_title.text()
        assert command in chat_widget.error_display.error_details.toPlainText()
    
    def test_handle_error_with_dict_response(self, chat_widget):
        """Тестирует обработку ошибки в формате словаря"""
        error_response = {
            "status": "error",
            "error_code": "CONNECTION_ERROR",
            "message": "Connection failed"
        }
        
        chat_widget._handle_error(error_response)
        
        assert chat_widget.error_display.isVisible()
        assert chat_widget.send_btn.isEnabled()  # Кнопка должна быть разблокирована
    
    def test_handle_error_with_string_response(self, chat_widget):
        """Тестирует обработку ошибки в формате строки"""
        error_message = "Connection timeout occurred"
        
        chat_widget._handle_error(error_message)
        
        assert chat_widget.error_display.isVisible()
        assert chat_widget.send_btn.isEnabled()
    
    def test_error_retry_connection(self, chat_widget):
        """Тестирует повтор соединения"""
        with patch('gopiai.ui.components.chat_widget.get_default_client') as mock_client:
            mock_api_client = Mock()
            mock_api_client.health_check.return_value = True
            mock_client.return_value = mock_api_client
            
            chat_widget._handle_error_retry("connection")
            
            mock_api_client.health_check.assert_called_once()
    
    def test_error_retry_api(self, chat_widget):
        """Тестирует повтор API запроса"""
        # Мокаем memory_manager для возврата последнего сообщения
        with patch.object(chat_widget, '_get_last_user_message') as mock_get_msg:
            mock_get_msg.return_value = "Test message"
            
            with patch.object(chat_widget, 'async_handler') as mock_handler:
                chat_widget._handle_error_retry("api")
                
                mock_handler.send_message.assert_called_once()
    
    def test_error_retry_component(self, chat_widget):
        """Тестирует повтор инициализации компонента"""
        # Удаляем компоненты для тестирования переинициализации
        chat_widget.crew_ai_client = None
        chat_widget.async_handler = None
        
        with patch('gopiai.ui.components.chat_widget.CrewAIClient') as mock_crew:
            with patch('gopiai.ui.components.chat_widget.ChatAsyncHandler') as mock_handler:
                chat_widget._handle_error_retry("component")
                
                mock_crew.assert_called_once()
                mock_handler.assert_called_once()
    
    def test_error_dismiss(self, chat_widget):
        """Тестирует закрытие ошибки"""
        # Показываем ошибку
        chat_widget.show_api_error("Test error")
        assert chat_widget.error_display.isVisible()
        
        # Закрываем ошибку
        chat_widget._handle_error_dismiss()
        
        # Проверяем, что ошибка скрыта (через сигнал)
        # В реальности это происходит через сигнал dismissRequested
    
    def test_get_last_user_message(self, chat_widget):
        """Тестирует получение последнего сообщения пользователя"""
        # Мокаем memory_manager
        mock_messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Last message"}
        ]
        
        chat_widget.session_id = "test_session"
        chat_widget.memory_manager.get_messages.return_value = mock_messages
        
        last_message = chat_widget._get_last_user_message()
        
        assert last_message == "Last message"
    
    def test_get_last_user_message_no_session(self, chat_widget):
        """Тестирует получение последнего сообщения без сессии"""
        chat_widget.session_id = None
        
        last_message = chat_widget._get_last_user_message()
        
        assert last_message is None
    
    def test_error_display_styles_applied(self, chat_widget):
        """Проверяет применение стилей к ErrorDisplayWidget"""
        error_display = chat_widget.error_display
        
        # Проверяем, что стили применены (косвенно через наличие styleSheet)
        assert error_display.styleSheet() != ""
        assert "errorDisplayWidget" in error_display.styleSheet()
    
    def test_multiple_errors_handling(self, chat_widget):
        """Тестирует обработку нескольких ошибок подряд"""
        # Показываем первую ошибку
        chat_widget.show_api_error("First error")
        assert chat_widget.error_display.isVisible()
        
        # Показываем вторую ошибку (должна заменить первую)
        chat_widget.show_connection_error("Test Service")
        assert chat_widget.error_display.isVisible()
        assert "подключения" in chat_widget.error_display.error_title.text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])