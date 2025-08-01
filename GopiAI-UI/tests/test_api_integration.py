"""
Интеграционные тесты для API клиента GopiAI.

Эти тесты проверяют работу с реальным бэкенд сервером.
Запускайте их только когда бэкенд сервер доступен.
"""

import pytest
import time
from gopiai.ui.api.client import GopiAIAPIClient


class TestAPIIntegration:
    """Интеграционные тесты с реальным бэкенд сервером."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Создание клиента для тестов."""
        client = GopiAIAPIClient(base_url="http://localhost:5051", timeout=30)
        yield client
        client.close()
    
    @pytest.mark.integration
    def test_health_check_real_server(self, client):
        """Тест проверки состояния реального сервера."""
        # Этот тест пройдет только если сервер запущен
        result = client.health_check()
        
        # Результат может быть True или False в зависимости от состояния сервера
        assert isinstance(result, bool)
        
        if result:
            print("✅ Бэкенд сервер доступен")
        else:
            print("❌ Бэкенд сервер недоступен")
    
    @pytest.mark.integration
    def test_get_models_real_server(self, client):
        """Тест получения моделей от реального сервера."""
        models = client.get_available_models()
        
        # Результат должен быть списком (может быть пустым если сервер недоступен)
        assert isinstance(models, list)
        
        if models:
            print(f"✅ Получено {len(models)} моделей:")
            for model in models[:3]:  # Показать первые 3 модели
                print(f"  - {model.get('id', 'unknown')}: {model.get('name', 'unknown')}")
        else:
            print("❌ Модели не получены (сервер недоступен или ошибка)")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_send_message_real_server(self, client):
        """Тест отправки сообщения реальному серверу."""
        # Простое сообщение для тестирования
        test_message = "Привет! Это тестовое сообщение от API клиента."
        
        result = client.send_message(test_message)
        
        # Проверяем структуру ответа
        assert isinstance(result, dict)
        assert "status" in result
        
        if result["status"] == "success":
            print("✅ Сообщение успешно отправлено и обработано")
            print(f"Ответ: {result.get('response', 'Нет ответа')[:100]}...")
            
            # Проверяем обязательные поля успешного ответа
            assert "response" in result
            assert isinstance(result.get("tools_used", []), list)
            
        elif result["status"] == "error":
            print(f"❌ Ошибка при отправке сообщения: {result.get('message', 'Неизвестная ошибка')}")
            
            # Проверяем структуру ошибки
            assert "error_code" in result
            assert "message" in result
            
        else:
            pytest.fail(f"Неожиданный статус ответа: {result['status']}")
    
    @pytest.mark.integration
    def test_connection_timeout(self):
        """Тест обработки таймаута соединения."""
        # Создаем клиент с очень коротким таймаутом
        client = GopiAIAPIClient(base_url="http://localhost:5051", timeout=0.001)
        
        try:
            result = client.send_message("Тест таймаута")
            
            # Ожидаем ошибку таймаута
            assert result["status"] == "error"
            assert result["error_code"] in ["TIMEOUT_ERROR", "CONNECTION_ERROR"]
            print(f"✅ Таймаут корректно обработан: {result['error_code']}")
            
        finally:
            client.close()
    
    @pytest.mark.integration
    def test_invalid_server_url(self):
        """Тест обработки недоступного сервера."""
        # Создаем клиент с недоступным URL
        client = GopiAIAPIClient(base_url="http://nonexistent-server:9999", timeout=5)
        
        try:
            result = client.send_message("Тест недоступного сервера")
            
            # Ожидаем ошибку соединения
            assert result["status"] == "error"
            assert result["error_code"] == "CONNECTION_ERROR"
            print("✅ Ошибка соединения корректно обработана")
            
        finally:
            client.close()
    
    @pytest.mark.integration
    def test_concurrent_requests(self, client):
        """Тест параллельных запросов."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def send_request(message_id):
            """Отправка запроса в отдельном потоке."""
            result = client.send_message(f"Параллельный запрос #{message_id}")
            results.put((message_id, result))
        
        # Создаем и запускаем несколько потоков
        threads = []
        for i in range(3):
            thread = threading.Thread(target=send_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join(timeout=30)
        
        # Проверяем результаты
        received_results = []
        while not results.empty():
            received_results.append(results.get())
        
        assert len(received_results) == 3
        print(f"✅ Получено {len(received_results)} ответов на параллельные запросы")
        
        for message_id, result in received_results:
            assert isinstance(result, dict)
            assert "status" in result
            print(f"  Запрос #{message_id}: {result['status']}")


class TestAPIClientConfiguration:
    """Тесты конфигурации API клиента."""
    
    def test_custom_base_url(self):
        """Тест кастомного базового URL."""
        client = GopiAIAPIClient(base_url="http://custom-server:8080/")
        
        # URL должен быть нормализован (без trailing slash)
        assert client.base_url == "http://custom-server:8080"
        
        client.close()
    
    def test_custom_timeout(self):
        """Тест кастомного таймаута."""
        client = GopiAIAPIClient(timeout=60)
        
        assert client.timeout == 60
        
        client.close()
    
    def test_session_headers(self):
        """Тест заголовков сессии."""
        client = GopiAIAPIClient()
        
        headers = client.session.headers
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
        assert 'GopiAI-UI-Client' in headers['User-Agent']
        
        client.close()


if __name__ == "__main__":
    # Запуск интеграционных тестов
    pytest.main([
        __file__,
        "-v",
        "-m", "integration",
        "--tb=short"
    ])