"""
Тесты для системы обработки ошибок LLM.
Проверяет все аспекты обработки ошибок согласно требованиям 2.1, 2.2, 2.5.
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Импортируем тестируемые компоненты
from llm_error_handler import (
    LLMErrorHandler, LLMErrorType, RetryStrategy,
    llm_error_handler, with_llm_error_handling
)

# Импортируем исключения litellm для тестирования
try:
    from litellm import (
        RateLimitError, AuthenticationError, InvalidRequestError, 
        APIError, Timeout, APIConnectionError, BadRequestError,
        ContentPolicyViolationError, ContextWindowExceededError,
        InternalServerError, NotFoundError, PermissionDeniedError,
        ServiceUnavailableError, UnprocessableEntityError
    )
    LITELLM_AVAILABLE = True
except ImportError:
    # Создаём заглушки для тестирования
    class RateLimitError(Exception): pass
    class AuthenticationError(Exception): pass
    class InvalidRequestError(Exception): pass
    class APIError(Exception): pass
    class Timeout(Exception): pass
    class APIConnectionError(Exception): pass
    class BadRequestError(Exception): pass
    class ContentPolicyViolationError(Exception): pass
    class ContextWindowExceededError(Exception): pass
    class InternalServerError(Exception): pass
    class NotFoundError(Exception): pass
    class PermissionDeniedError(Exception): pass
    class ServiceUnavailableError(Exception): pass
    class UnprocessableEntityError(Exception): pass
    LITELLM_AVAILABLE = False


class TestLLMErrorHandler:
    """Тесты для класса LLMErrorHandler."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.handler = LLMErrorHandler(max_retries=2, base_delay=0.1)
        self.handler.reset_statistics()

    def test_initialization(self):
        """Тест инициализации обработчика."""
        handler = LLMErrorHandler(max_retries=5, base_delay=2.0)
        assert handler.max_retries == 5
        assert handler.base_delay == 2.0
        assert handler.error_stats["total_errors"] == 0

    def test_error_classification_rate_limit(self):
        """Тест классификации ошибки превышения лимита."""
        error = RateLimitError("Rate limit exceeded")
        error_type = self.handler._classify_error(error)
        assert error_type == LLMErrorType.RATE_LIMIT

    def test_error_classification_authentication(self):
        """Тест классификации ошибки аутентификации."""
        error = AuthenticationError("Invalid API key")
        error_type = self.handler._classify_error(error)
        assert error_type == LLMErrorType.AUTHENTICATION

    def test_error_classification_timeout(self):
        """Тест классификации ошибки таймаута."""
        error = Timeout("Request timed out")
        error_type = self.handler._classify_error(error)
        assert error_type == LLMErrorType.TIMEOUT

    def test_error_classification_by_message(self):
        """Тест классификации ошибки по содержимому сообщения."""
        error = Exception("Connection failed due to network issues")
        error_type = self.handler._classify_error(error)
        assert error_type == LLMErrorType.CONNECTION_ERROR

    def test_should_retry_logic(self):
        """Тест логики определения необходимости повторной попытки."""
        # Ошибки, которые должны повторяться
        assert self.handler._should_retry(LLMErrorType.RATE_LIMIT) == True
        assert self.handler._should_retry(LLMErrorType.TIMEOUT) == True
        assert self.handler._should_retry(LLMErrorType.CONNECTION_ERROR) == True
        
        # Ошибки, которые не должны повторяться
        assert self.handler._should_retry(LLMErrorType.AUTHENTICATION) == False
        assert self.handler._should_retry(LLMErrorType.INVALID_REQUEST) == False
        assert self.handler._should_retry(LLMErrorType.CONTENT_POLICY) == False

    def test_calculate_delay_exponential(self):
        """Тест расчёта экспоненциальной задержки."""
        delay_0 = self.handler._calculate_delay(LLMErrorType.RATE_LIMIT, 0)
        delay_1 = self.handler._calculate_delay(LLMErrorType.RATE_LIMIT, 1)
        delay_2 = self.handler._calculate_delay(LLMErrorType.RATE_LIMIT, 2)
        
        assert delay_0 == 0.1  # base_delay * 2^0
        assert delay_1 == 0.2  # base_delay * 2^1
        assert delay_2 == 0.4  # base_delay * 2^2

    def test_calculate_delay_linear(self):
        """Тест расчёта линейной задержки."""
        delay_0 = self.handler._calculate_delay(LLMErrorType.TIMEOUT, 0)
        delay_1 = self.handler._calculate_delay(LLMErrorType.TIMEOUT, 1)
        delay_2 = self.handler._calculate_delay(LLMErrorType.TIMEOUT, 2)
        
        assert delay_0 == 0.1  # base_delay * (0 + 1)
        assert delay_1 == 0.2  # base_delay * (1 + 1)
        assert delay_2 == 0.3  # base_delay * (2 + 1)

    def test_handle_llm_error_structure(self):
        """Тест структуры ответа при обработке ошибки."""
        error = RateLimitError("Rate limit exceeded")
        response = self.handler.handle_llm_error(error, "test-model")
        
        # Проверяем обязательные поля
        assert response["status"] == "error"
        assert response["error_code"] == "RATE_LIMIT"
        assert "message" in response
        assert response["model_id"] == "test-model"
        assert "timestamp" in response
        assert response["retryable"] == True
        assert "retry_after" in response  # Специфично для rate limit

    def test_handle_authentication_error(self):
        """Тест обработки ошибки аутентификации."""
        error = AuthenticationError("Invalid API key")
        response = self.handler.handle_llm_error(error, "test-model")
        
        assert response["error_code"] == "AUTHENTICATION"
        assert response["retryable"] == False
        assert "API ключа" in response["message"]
        assert "suggestion" in response

    def test_validate_llm_response_valid(self):
        """Тест валидации корректного ответа."""
        response = "Это корректный ответ от LLM"
        result = self.handler.validate_llm_response(response, "test-model")
        
        assert result["status"] == "success"
        assert result["valid"] == True
        assert result["response"] == response

    def test_validate_llm_response_empty_string(self):
        """Тест валидации пустой строки."""
        response = ""
        result = self.handler.validate_llm_response(response, "test-model")
        
        assert result["status"] == "error"
        assert result["valid"] == False
        assert result["error_code"] == "EMPTY_RESPONSE"

    def test_validate_llm_response_none(self):
        """Тест валидации None."""
        response = None
        result = self.handler.validate_llm_response(response, "test-model")
        
        assert result["status"] == "error"
        assert result["valid"] == False
        assert result["error_code"] == "EMPTY_RESPONSE"

    def test_validate_llm_response_whitespace(self):
        """Тест валидации строки из пробелов."""
        response = "   \n\t  "
        result = self.handler.validate_llm_response(response, "test-model")
        
        assert result["status"] == "error"
        assert result["valid"] == False

    def test_validate_llm_response_placeholder(self):
        """Тест валидации строк-заглушек."""
        placeholders = ["null", "none", "undefined", "пустой ответ", "empty response"]
        
        for placeholder in placeholders:
            result = self.handler.validate_llm_response(placeholder, "test-model")
            assert result["status"] == "error"
            assert result["valid"] == False

    def test_error_statistics_tracking(self):
        """Тест отслеживания статистики ошибок."""
        # Обрабатываем несколько ошибок
        self.handler.handle_llm_error(RateLimitError("Rate limit"), "model1")
        self.handler.handle_llm_error(AuthenticationError("Auth error"), "model2")
        self.handler.handle_llm_error(RateLimitError("Another rate limit"), "model3")
        
        stats = self.handler.get_error_statistics()
        
        assert stats["total_errors"] == 3
        assert stats["errors_by_type"]["rate_limit"] == 2
        assert stats["errors_by_type"]["authentication"] == 1
        assert stats["last_error_time"] is not None

    def test_statistics_reset(self):
        """Тест сброса статистики."""
        # Создаём ошибку
        self.handler.handle_llm_error(RateLimitError("Test"), "model")
        assert self.handler.error_stats["total_errors"] == 1
        
        # Сбрасываем статистику
        self.handler.reset_statistics()
        assert self.handler.error_stats["total_errors"] == 0
        assert self.handler.error_stats["errors_by_type"] == {}

    @patch('time.sleep')
    def test_retry_decorator_success_after_retry(self, mock_sleep):
        """Тест успешного выполнения после повторной попытки."""
        call_count = 0
        
        @self.handler.with_error_handling
        def test_function(model_id="test-model"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError("Rate limit exceeded")
            return "Success!"
        
        result = test_function()
        
        assert result == "Success!"
        assert call_count == 2
        assert mock_sleep.call_count == 1  # Одна задержка между попытками

    @patch('time.sleep')
    def test_retry_decorator_max_retries_exceeded(self, mock_sleep):
        """Тест исчерпания максимального количества попыток."""
        @self.handler.with_error_handling
        def test_function(model_id="test-model"):
            raise RateLimitError("Persistent rate limit")
        
        with pytest.raises(Exception) as exc_info:
            test_function()
        
        assert "LLM error after" in str(exc_info.value)
        assert mock_sleep.call_count == 2  # max_retries = 2

    @patch('time.sleep')
    def test_retry_decorator_no_retry_for_auth_error(self, mock_sleep):
        """Тест отсутствия повторных попыток для ошибок аутентификации."""
        @self.handler.with_error_handling
        def test_function(model_id="test-model"):
            raise AuthenticationError("Invalid API key")
        
        with pytest.raises(Exception):
            test_function()
        
        assert mock_sleep.call_count == 0  # Никаких повторных попыток

    def test_retry_after_estimation(self):
        """Тест оценки времени до следующей попытки."""
        # Тест с секундами
        retry_after = self.handler._estimate_retry_after("retry after 30 seconds")
        assert retry_after == 30
        
        # Тест с минутами
        retry_after = self.handler._estimate_retry_after("wait 2 minutes")
        assert retry_after == 120
        
        # Тест без указания времени
        retry_after = self.handler._estimate_retry_after("rate limit exceeded")
        assert retry_after == 60  # Значение по умолчанию

    def test_user_friendly_messages(self):
        """Тест понятных пользователю сообщений."""
        test_cases = [
            (RateLimitError("Rate limit"), "лимит запросов"),
            (AuthenticationError("Auth failed"), "аутентификации"),
            (Timeout("Timeout"), "время ожидания"),
            (APIConnectionError("Connection failed"), "подключения"),
        ]
        
        for error, expected_keyword in test_cases:
            response = self.handler.handle_llm_error(error, "test-model")
            assert expected_keyword in response["message"].lower()

    def test_context_preservation(self):
        """Тест сохранения контекста в ошибке."""
        context = {"user_id": "123", "request_id": "abc"}
        error = RateLimitError("Rate limit")
        
        response = self.handler.handle_llm_error(error, "test-model", context)
        
        # Контекст должен быть сохранён в логах, но не в публичном ответе
        assert "user_id" not in response
        assert response["model_id"] == "test-model"

    def test_fallback_error_handling(self):
        """Тест резервной обработки ошибок."""
        # Создаём ситуацию, когда обработчик ошибок сам падает
        with patch.object(self.handler, '_classify_error', side_effect=Exception("Handler error")):
            response = self.handler.handle_llm_error(RateLimitError("Test"), "model")
            
            assert response["status"] == "error"
            assert response["error_code"] == "HANDLER_ERROR"
            assert "Критическая ошибка" in response["message"]


class TestGlobalErrorHandler:
    """Тесты для глобального экземпляра обработчика ошибок."""

    def test_global_handler_exists(self):
        """Тест существования глобального обработчика."""
        assert llm_error_handler is not None
        assert isinstance(llm_error_handler, LLMErrorHandler)

    def test_decorator_function(self):
        """Тест функции-декоратора."""
        @with_llm_error_handling
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_decorator_with_error(self):
        """Тест декоратора с ошибкой."""
        @with_llm_error_handling
        def test_function(model_id="test-model"):
            raise AuthenticationError("Auth failed")
        
        with pytest.raises(Exception):
            test_function()


class TestIntegrationScenarios:
    """Интеграционные тесты для реальных сценариев."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.handler = LLMErrorHandler(max_retries=1, base_delay=0.01)

    @patch('time.sleep')
    def test_rate_limit_recovery_scenario(self, mock_sleep):
        """Тест сценария восстановления после rate limit."""
        call_count = 0
        
        @self.handler.with_error_handling
        def mock_llm_call(model_id="test-model"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError("Rate limit exceeded, retry after 60 seconds")
            return {"choices": [{"message": {"content": "Success response"}}]}
        
        result = mock_llm_call()
        
        assert result["choices"][0]["message"]["content"] == "Success response"
        assert call_count == 2
        assert mock_sleep.called

    def test_validation_with_various_responses(self):
        """Тест валидации различных типов ответов."""
        test_cases = [
            ("Нормальный ответ", True),
            ({"content": "JSON ответ"}, True),
            (["список", "ответов"], True),
            ("", False),
            (None, False),
            ({}, False),
            ([], False),
            ("null", False),
            ("   ", False),
        ]
        
        for response, should_be_valid in test_cases:
            result = self.handler.validate_llm_response(response, "test-model")
            assert result["valid"] == should_be_valid, f"Failed for response: {response}"

    def test_error_response_format_consistency(self):
        """Тест консистентности формата ответов об ошибках."""
        errors = [
            RateLimitError("Rate limit"),
            AuthenticationError("Auth error"),
            Timeout("Timeout error"),
            InvalidRequestError("Invalid request"),
        ]
        
        required_fields = ["status", "error_code", "message", "model_id", "timestamp", "retryable"]
        
        for error in errors:
            response = self.handler.handle_llm_error(error, "test-model")
            
            # Проверяем наличие всех обязательных полей
            for field in required_fields:
                assert field in response, f"Missing field {field} in response for {error.__class__.__name__}"
            
            # Проверяем правильность статуса
            assert response["status"] == "error"
            
            # Проверяем формат timestamp
            assert isinstance(response["timestamp"], str)
            
            # Проверяем тип retryable
            assert isinstance(response["retryable"], bool)


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])