"""
Полный тест системы обработки ошибок LLM.
Проверяет все требования задачи 5: Implement comprehensive LLM error handling.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_requirement_2_1_rate_limit_handling():
    """
    Требование 2.1: WHEN an API rate limit is exceeded THEN the system SHALL return 
    a clear error message and retry automatically
    """
    logger.info("🧪 Тестирование требования 2.1: Обработка rate limit с автоматическими повторами")
    
    try:
        from llm_error_handler import llm_error_handler, with_llm_error_handling
        
        # Создаём заглушку для RateLimitError
        class MockRateLimitError(Exception):
            def __init__(self, message):
                super().__init__(message)
                self.__class__.__name__ = "RateLimitError"
        
        # Тестируем обработку rate limit ошибки
        error = MockRateLimitError("Rate limit exceeded, retry after 60 seconds")
        response = llm_error_handler.handle_llm_error(error, "test-model")
        
        # Проверяем структуру ответа
        assert response["status"] == "error"
        assert response["error_code"] == "RATE_LIMIT"
        assert response["retryable"] == True
        assert "retry_after" in response
        assert "лимит запросов" in response["message"].lower()
        
        # Тестируем автоматические повторы с декоратором
        call_count = 0
        
        @with_llm_error_handling
        def mock_llm_function(model_id="test-model"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MockRateLimitError("Rate limit exceeded")
            return "Success after retry"
        
        with patch('time.sleep'):  # Ускоряем тест
            result = mock_llm_function()
            assert result == "Success after retry"
            assert call_count == 2  # Первая попытка + повтор
        
        logger.info("✅ Требование 2.1 выполнено: Rate limit обрабатывается с автоматическими повторами")
        return True
        
    except Exception as e:
        logger.error(f"❌ Требование 2.1 не выполнено: {e}")
        return False

def test_requirement_2_2_empty_response_handling():
    """
    Требование 2.2: WHEN an LLM returns an empty response THEN the system SHALL provide 
    a meaningful error message instead of crashing
    """
    logger.info("🧪 Тестирование требования 2.2: Обработка пустых ответов LLM")
    
    try:
        from llm_error_handler import llm_error_handler
        
        # Тестируем различные типы пустых ответов
        empty_responses = [
            None,
            "",
            "   ",
            "null",
            "none",
            "пустой ответ",
            {},
            []
        ]
        
        for empty_response in empty_responses:
            validation = llm_error_handler.validate_llm_response(empty_response, "test-model")
            
            assert validation["status"] == "error"
            assert validation["valid"] == False
            assert validation["error_code"] == "EMPTY_RESPONSE"
            assert "message" in validation
            assert validation["retryable"] == True
            
        logger.info("✅ Требование 2.2 выполнено: Пустые ответы обрабатываются корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Требование 2.2 не выполнено: {e}")
        return False

def test_requirement_2_5_comprehensive_error_logging():
    """
    Требование 2.5: WHEN any backend error occurs THEN it SHALL be logged with full details for debugging
    """
    logger.info("🧪 Тестирование требования 2.5: Детальное логирование ошибок")
    
    try:
        from llm_error_handler import llm_error_handler
        
        # Создаём различные типы ошибок для тестирования логирования
        test_errors = [
            (Exception("Authentication failed"), "authentication"),
            (Exception("Rate limit exceeded"), "rate_limit"),
            (Exception("Connection timeout"), "timeout"),
            (Exception("Invalid request format"), "invalid_request"),
        ]
        
        # Сбрасываем статистику
        llm_error_handler.reset_statistics()
        
        # Обрабатываем ошибки и проверяем логирование
        for error, expected_type in test_errors:
            with patch.object(llm_error_handler.logger, 'error') as mock_logger_error, \
                 patch.object(llm_error_handler.logger, 'warning') as mock_logger_warning, \
                 patch.object(llm_error_handler.logger, 'info') as mock_logger_info:
                
                response = llm_error_handler.handle_llm_error(error, "test-model", 
                                                            context={"user_id": "123", "request_id": "abc"})
                
                # Проверяем, что логирование произошло (любой уровень)
                assert mock_logger_error.called or mock_logger_warning.called or mock_logger_info.called, \
                    f"Логирование не произошло для ошибки: {error}"
                
                # Проверяем структуру ответа
                assert response["status"] == "error"
                assert "timestamp" in response
                assert response["model_id"] == "test-model"
        
        # Проверяем статистику ошибок
        stats = llm_error_handler.get_error_statistics()
        assert stats["total_errors"] == len(test_errors)
        assert stats["last_error_time"] is not None
        
        logger.info("✅ Требование 2.5 выполнено: Детальное логирование работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Требование 2.5 не выполнено: {e}")
        return False

def test_all_litellm_exception_types():
    """
    Подзадача: Add imports for all litellm exception types
    """
    logger.info("🧪 Тестирование импорта всех типов исключений litellm")
    
    try:
        from llm_error_handler import (
            RateLimitError, AuthenticationError, InvalidRequestError, 
            APIError, Timeout, APIConnectionError, BadRequestError,
            ContentPolicyViolationError, ContextWindowExceededError,
            InternalServerError, NotFoundError, PermissionDeniedError,
            ServiceUnavailableError, UnprocessableEntityError
        )
        
        # Проверяем, что все исключения доступны
        exception_types = [
            RateLimitError, AuthenticationError, InvalidRequestError, 
            APIError, Timeout, APIConnectionError, BadRequestError,
            ContentPolicyViolationError, ContextWindowExceededError,
            InternalServerError, NotFoundError, PermissionDeniedError,
            ServiceUnavailableError, UnprocessableEntityError
        ]
        
        for exc_type in exception_types:
            assert exc_type is not None
            assert callable(exc_type)
        
        logger.info("✅ Все типы исключений litellm импортированы успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка импорта исключений litellm: {e}")
        return False

def test_exponential_backoff_decorator():
    """
    Подзадача: Create retry decorator with exponential backoff for rate limits
    """
    logger.info("🧪 Тестирование декоратора с экспоненциальной задержкой")
    
    try:
        from llm_error_handler import LLMErrorHandler, LLMErrorType
        
        handler = LLMErrorHandler(max_retries=3, base_delay=0.1)
        
        # Тестируем расчёт экспоненциальной задержки
        delays = []
        for attempt in range(3):
            delay = handler._calculate_delay(LLMErrorType.RATE_LIMIT, attempt)
            delays.append(delay)
        
        # Проверяем экспоненциальный рост: 0.1, 0.2, 0.4
        assert delays[0] == 0.1  # base_delay * 2^0
        assert delays[1] == 0.2  # base_delay * 2^1
        assert delays[2] == 0.4  # base_delay * 2^2
        
        # Тестируем декоратор с повторными попытками
        attempt_count = 0
        
        @handler.with_error_handling
        def test_function(model_id="test-model"):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise Exception("Rate limit exceeded")
            return "Success"
        
        with patch('time.sleep') as mock_sleep:
            result = test_function()
            assert result == "Success"
            assert attempt_count == 3
            assert mock_sleep.call_count == 2  # Две задержки между тремя попытками
        
        logger.info("✅ Декоратор с экспоненциальной задержкой работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка декоратора с экспоненциальной задержкой: {e}")
        return False

def test_specific_error_handling():
    """
    Подзадача: Implement specific error handling for each exception type
    """
    logger.info("🧪 Тестирование специфичной обработки каждого типа ошибки")
    
    try:
        from llm_error_handler import llm_error_handler, LLMErrorType
        
        # Создаём заглушки для разных типов ошибок
        error_test_cases = [
            ("RateLimitError", "Rate limit exceeded", LLMErrorType.RATE_LIMIT, True),
            ("AuthenticationError", "Invalid API key", LLMErrorType.AUTHENTICATION, False),
            ("Timeout", "Request timed out", LLMErrorType.TIMEOUT, True),
            ("APIConnectionError", "Connection failed", LLMErrorType.CONNECTION_ERROR, True),
            ("ContentPolicyViolationError", "Content policy violation", LLMErrorType.CONTENT_POLICY, False),
            ("ContextWindowExceededError", "Context window exceeded", LLMErrorType.CONTEXT_WINDOW, False),
        ]
        
        for error_name, error_message, expected_type, should_retry in error_test_cases:
            # Создаём заглушку ошибки
            class MockError(Exception):
                def __init__(self, message):
                    super().__init__(message)
                    self.__class__.__name__ = error_name
            
            error = MockError(error_message)
            
            # Тестируем классификацию
            classified_type = llm_error_handler._classify_error(error)
            
            # Тестируем обработку
            response = llm_error_handler.handle_llm_error(error, "test-model")
            
            # Проверяем корректность обработки
            assert response["status"] == "error"
            assert response["retryable"] == should_retry
            assert "message" in response
            assert response["model_id"] == "test-model"
        
        logger.info("✅ Специфичная обработка каждого типа ошибки работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка специфичной обработки ошибок: {e}")
        return False

def test_structured_api_error_format():
    """
    Подзадача: Create structured error response format for API
    """
    logger.info("🧪 Тестирование структурированного формата ответов об ошибках для API")
    
    try:
        from llm_error_handler import llm_error_handler
        
        # Тестируем различные типы ошибок
        test_error = Exception("Test error message")
        response = llm_error_handler.handle_llm_error(test_error, "test-model-123")
        
        # Проверяем обязательные поля структурированного ответа
        required_fields = [
            "status",           # Статус ответа (error)
            "error_code",       # Код ошибки
            "message",          # Понятное пользователю сообщение
            "model_id",         # Идентификатор модели
            "timestamp",        # Время ошибки
            "retryable"         # Можно ли повторить запрос
        ]
        
        for field in required_fields:
            assert field in response, f"Отсутствует обязательное поле: {field}"
        
        # Проверяем типы данных
        assert response["status"] == "error"
        assert isinstance(response["error_code"], str)
        assert isinstance(response["message"], str)
        assert response["model_id"] == "test-model-123"
        assert isinstance(response["timestamp"], str)
        assert isinstance(response["retryable"], bool)
        
        # Тестируем специальные поля для rate limit
        rate_limit_error = Exception("Rate limit exceeded, retry after 30 seconds")
        rate_limit_response = llm_error_handler.handle_llm_error(rate_limit_error, "test-model")
        
        if rate_limit_response["error_code"] == "RATE_LIMIT":
            assert "retry_after" in rate_limit_response
            assert isinstance(rate_limit_response["retry_after"], int)
        
        logger.info("✅ Структурированный формат ответов об ошибках работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка структурированного формата ответов: {e}")
        return False

def test_integration_with_smart_delegator():
    """
    Тестирование интеграции с SmartDelegator
    """
    logger.info("🧪 Тестирование интеграции с SmartDelegator")
    
    try:
        # Проверяем импорт обработчика ошибок в smart_delegator
        import smart_delegator
        
        # Проверяем, что обработчик ошибок доступен
        assert hasattr(smart_delegator, 'LLM_ERROR_HANDLER_AVAILABLE')
        assert hasattr(smart_delegator, 'llm_error_handler')
        assert hasattr(smart_delegator, 'with_llm_error_handling')
        
        logger.info("✅ Интеграция с SmartDelegator работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка интеграции с SmartDelegator: {e}")
        return False

def run_complete_test_suite():
    """Запуск полного набора тестов для задачи 5."""
    logger.info("🚀 Запуск полного тестирования задачи 5: Implement comprehensive LLM error handling")
    logger.info("=" * 80)
    
    tests = [
        ("Требование 2.1: Обработка rate limit с повторами", test_requirement_2_1_rate_limit_handling),
        ("Требование 2.2: Обработка пустых ответов LLM", test_requirement_2_2_empty_response_handling),
        ("Требование 2.5: Детальное логирование ошибок", test_requirement_2_5_comprehensive_error_logging),
        ("Импорт всех типов исключений litellm", test_all_litellm_exception_types),
        ("Декоратор с экспоненциальной задержкой", test_exponential_backoff_decorator),
        ("Специфичная обработка каждого типа ошибки", test_specific_error_handling),
        ("Структурированный формат ответов API", test_structured_api_error_format),
        ("Интеграция с SmartDelegator", test_integration_with_smart_delegator),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 {test_name}")
        logger.info("-" * 60)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ ПРОЙДЕН: {test_name}")
            else:
                failed += 1
                logger.error(f"❌ ПРОВАЛЕН: {test_name}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ ОШИБКА в {test_name}: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ЗАДАЧИ 5")
    logger.info("=" * 80)
    logger.info(f"✅ Пройдено тестов: {passed}")
    logger.info(f"❌ Провалено тестов: {failed}")
    logger.info(f"📈 Процент успешности: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Задача 5 выполнена полностью.")
        logger.info("✅ Comprehensive LLM error handling реализована успешно!")
        return True
    else:
        logger.error("⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        logger.error("❌ Задача 5 требует доработки.")
        return False

if __name__ == "__main__":
    success = run_complete_test_suite()
    sys.exit(0 if success else 1)