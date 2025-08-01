"""
Тесты для API клиента GopiAI.
"""

import json
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, RequestException

from gopiai.ui.api.client import GopiAIAPIClient, get_default_client, set_default_client


class TestGopiAIAPIClient:
    """Тесты для класса GopiAIAPIClient."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.client = GopiAIAPIClient(base_url="http://test-server:5051", timeout=10)
    
    def teardown_method(self):
        """Очистка после каждого теста."""
        self.client.close()
    
    def test_init(self):
        """Тест инициализации клиента."""
        assert self.client.base_url == "http://test-server:5051"
        assert self.client.timeout == 10
        assert self.client.session is not None
        assert 'Content-Type' in self.client.session.headers
        assert self.client.session.headers['Content-Type'] == 'application/json'
    
    @patch('requests.Session.post')
    def test_send_message_success(self, mock_post):
        """Тест успешной отправки сообщения."""
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "response": "Тестовый ответ",
            "tools_used": [],
            "execution_time": 1.5
        }
        mock_post.return_value = mock_response
        
        # Выполнение теста
        result = self.client.send_message("Тестовое сообщение", model_id="test-model")
        
        # Проверки
        assert result["status"] == "success"
        assert result["response"] == "Тестовый ответ"
        mock_post.assert_called_once()
        
        # Проверка параметров вызова
        call_args = mock_post.call_args
        assert call_args[1]['json']['message'] == "Тестовое сообщение"
        assert call_args[1]['json']['model_id'] == "test-model"
        assert call_args[1]['timeout'] == 10
    
    @patch('requests.Session.post')
    def test_send_message_connection_error(self, mock_post):
        """Тест обработки ошибки соединения."""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        result = self.client.send_message("Тестовое сообщение")
        
        assert result["status"] == "error"
        assert result["error_code"] == "CONNECTION_ERROR"
        assert "подключиться к серверу" in result["message"]
    
    @patch('requests.Session.post')
    def test_send_message_timeout_error(self, mock_post):
        """Тест обработки таймаута."""
        mock_post.side_effect = Timeout("Request timeout")
        
        result = self.client.send_message("Тестовое сообщение")
        
        assert result["status"] == "error"
        assert result["error_code"] == "TIMEOUT_ERROR"
        assert "превысил лимит времени" in result["message"]
    
    @patch('requests.Session.post')
    def test_send_message_http_error(self, mock_post):
        """Тест обработки HTTP ошибки."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = self.client.send_message("Тестовое сообщение")
        
        assert result["status"] == "error"
        assert result["error_code"] == "API_ERROR"
        assert "HTTP 500" in result["message"]
    
    @patch('requests.Session.post')
    def test_send_message_json_error(self, mock_post):
        """Тест обработки ошибки парсинга JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        result = self.client.send_message("Тестовое сообщение")
        
        assert result["status"] == "error"
        assert result["error_code"] == "JSON_ERROR"
        assert "некорректный JSON" in result["message"]
    
    @patch('requests.Session.get')
    def test_get_available_models_success(self, mock_get):
        """Тест успешного получения списка моделей."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "model1", "name": "Test Model 1"},
            {"id": "model2", "name": "Test Model 2"}
        ]
        mock_get.return_value = mock_response
        
        result = self.client.get_available_models()
        
        assert len(result) == 2
        assert result[0]["id"] == "model1"
        assert result[1]["id"] == "model2"
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_available_models_error(self, mock_get):
        """Тест обработки ошибки при получении моделей."""
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = self.client.get_available_models()
        
        assert result == []
    
    @patch('requests.Session.get')
    def test_health_check_healthy(self, mock_get):
        """Тест проверки состояния - сервер здоров."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_health_check_unhealthy(self, mock_get):
        """Тест проверки состояния - сервер нездоров."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "unhealthy"}
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result is False
    
    @patch('requests.Session.get')
    def test_health_check_connection_error(self, mock_get):
        """Тест проверки состояния - ошибка соединения."""
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = self.client.health_check()
        
        assert result is False
    
    def test_create_error_response(self):
        """Тест создания ответа об ошибке."""
        result = self.client._create_error_response(
            "TEST_ERROR",
            "Тестовая ошибка",
            {"detail": "test detail"}
        )
        
        assert result["status"] == "error"
        assert result["error_code"] == "TEST_ERROR"
        assert result["message"] == "Тестовая ошибка"
        assert result["response"] == "Тестовая ошибка"
        assert result["details"]["detail"] == "test detail"
        assert "timestamp" in result
    
    def test_context_manager(self):
        """Тест использования как контекстного менеджера."""
        with GopiAIAPIClient() as client:
            assert client.session is not None
        # После выхода из контекста сессия должна быть закрыта


class TestGlobalClient:
    """Тесты для глобального клиента."""
    
    def test_get_default_client(self):
        """Тест получения глобального клиента."""
        client1 = get_default_client()
        client2 = get_default_client()
        
        assert client1 is client2  # Должен быть тот же экземпляр
    
    def test_set_default_client(self):
        """Тест установки глобального клиента."""
        custom_client = GopiAIAPIClient(base_url="http://custom:8080")
        set_default_client(custom_client)
        
        retrieved_client = get_default_client()
        assert retrieved_client is custom_client
        assert retrieved_client.base_url == "http://custom:8080"
        
        custom_client.close()


if __name__ == "__main__":
    pytest.main([__file__])