"""
Интеграционный тест для проверки работы системы обработки ошибок LLM.
Проверяет интеграцию с smart_delegator и корректность обработки ошибок.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем логирование для тестов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm_error_handler_import():
    """Тест импорта обработчика ошибок."""
    try:
        from llm_error_handler import llm_error_handler, with_llm_error_handling, LLMErrorType
        logger.info("✅ LLM Error Handler импортирован успешно")
        return True
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта LLM Error Handler: {e}")
        return False

def test_smart_delegator_integration():
    """Тест интеграции с smart_delegator."""
    try:
        from smart_delegator import SmartDelegator
        
        # Создаём экземпляр делегатора
        delegator = SmartDelegator()
        logger.info("✅ SmartDelegator создан успешно")
        
        # Проверяем, что обработчик ошибок доступен
        if hasattr(delegator, 'LLM_ERROR_HANDLER_AVAILABLE'):
            logger.info(f"✅ LLM_ERROR_HANDLER_AVAILABLE = {delegator.LLM_ERROR_HANDLER_AVAILABLE}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка интеграции с SmartDelegator: {e}")
        return False

def test_error_handling_functionality():
    """Тест функциональности обработки ошибок."""
    try:
        from llm_error_handler import llm_error_handler, LLMErrorType
        
        # Тест классификации ошибок
        test_error = Exception("Rate limit exceeded")
        error_type = llm_error_handler._classify_error(test_error)
        logger.info(f"✅ Классификация ошибки: {error_type}")
        
        # Тест обработки ошибки
        response = llm_error_handler.handle_llm_error(test_error, "test-model")
        logger.info(f"✅ Структурированный ответ об ошибке: {response['status']}")
        
        # Тест валидации ответа
        validation = llm_error_handler.validate_llm_response("Тестовый ответ", "test-model")
        logger.info(f"✅ Валидация ответа: {validation['valid']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка функциональности: {e}")
        return False

def test_decorator_functionality():
    """Тест функциональности декоратора."""
    try:
        from llm_error_handler import with_llm_error_handling
        
        @with_llm_error_handling
        def test_function(model_id="test-model"):
            return "Успешный результат"
        
        result = test_function()
        logger.info(f"✅ Декоратор работает: {result}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка декоратора: {e}")
        return False

def test_litellm_exceptions():
    """Тест обработки исключений litellm."""
    try:
        from llm_error_handler import llm_error_handler
        
        # Создаём заглушки исключений для тестирования
        class MockRateLimitError(Exception):
            pass
        
        class MockAuthenticationError(Exception):
            pass
        
        # Тестируем обработку разных типов ошибок
        errors_to_test = [
            (MockRateLimitError("Rate limit exceeded"), "rate_limit"),
            (MockAuthenticationError("Invalid API key"), "authentication"),
            (Exception("Unknown error"), "unknown_error"),
        ]
        
        for error, expected_type in errors_to_test:
            response = llm_error_handler.handle_llm_error(error, "test-model")
            logger.info(f"✅ Обработка {error.__class__.__name__}: {response['error_code']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка обработки исключений: {e}")
        return False

def test_statistics_tracking():
    """Тест отслеживания статистики."""
    try:
        from llm_error_handler import llm_error_handler
        
        # Сбрасываем статистику
        llm_error_handler.reset_statistics()
        
        # Создаём несколько ошибок
        llm_error_handler.handle_llm_error(Exception("Test error 1"), "model1")
        llm_error_handler.handle_llm_error(Exception("Test error 2"), "model2")
        
        # Проверяем статистику
        stats = llm_error_handler.get_error_statistics()
        logger.info(f"✅ Статистика ошибок: {stats['total_errors']} ошибок")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка статистики: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов."""
    logger.info("🚀 Запуск интеграционных тестов системы обработки ошибок LLM")
    logger.info("=" * 60)
    
    tests = [
        ("Импорт обработчика ошибок", test_llm_error_handler_import),
        ("Интеграция с SmartDelegator", test_smart_delegator_integration),
        ("Функциональность обработки ошибок", test_error_handling_functionality),
        ("Функциональность декоратора", test_decorator_functionality),
        ("Обработка исключений litellm", test_litellm_exceptions),
        ("Отслеживание статистики", test_statistics_tracking),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Тест: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: ПРОЙДЕН")
            else:
                failed += 1
                logger.error(f"❌ {test_name}: ПРОВАЛЕН")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name}: ОШИБКА - {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Результаты тестирования:")
    logger.info(f"✅ Пройдено: {passed}")
    logger.info(f"❌ Провалено: {failed}")
    logger.info(f"📈 Успешность: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        logger.info("🎉 Все тесты пройдены успешно!")
        return True
    else:
        logger.error("⚠️  Некоторые тесты провалены!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)