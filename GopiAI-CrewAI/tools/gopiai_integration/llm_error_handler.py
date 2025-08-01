"""
Комплексная система обработки ошибок LLM для GopiAI.
Реализует требования 2.1, 2.2, 2.5 из спецификации.
"""

import logging
import time
import json
import traceback
from typing import Dict, Any, Optional, Union, Callable
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta

# Импорты всех типов исключений litellm
try:
    import litellm
    from litellm import (
        RateLimitError, AuthenticationError, InvalidRequestError, 
        APIError, Timeout, APIConnectionError, BadRequestError,
        ContentPolicyViolationError, ContextWindowExceededError,
        InternalServerError, NotFoundError, PermissionDeniedError,
        ServiceUnavailableError, UnprocessableEntityError
    )
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    # Создаём заглушки для случая отсутствия litellm
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

logger = logging.getLogger(__name__)


class LLMErrorType(Enum):
    """Типы ошибок LLM."""
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid_request"
    API_ERROR = "api_error"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CONTENT_POLICY = "content_policy"
    CONTEXT_WINDOW = "context_window"
    INTERNAL_SERVER = "internal_server"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    EMPTY_RESPONSE = "empty_response"
    INVALID_RESPONSE = "invalid_response"
    UNKNOWN_ERROR = "unknown_error"


class RetryStrategy(Enum):
    """Стратегии повторных попыток."""
    NO_RETRY = "no_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE_RETRY = "immediate_retry"


class LLMErrorHandler:
    """
    Комплексная система обработки ошибок LLM.
    
    Функциональность:
    - Обработка всех типов исключений litellm
    - Автоматические повторные попытки с экспоненциальной задержкой
    - Валидация пустых и некорректных ответов
    - Структурированные ответы об ошибках для API
    - Детальное логирование для отладки
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Инициализация обработчика ошибок LLM.
        
        Args:
            max_retries: Максимальное количество повторных попыток
            base_delay: Базовая задержка для экспоненциального backoff (секунды)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logger
        
        # Статистика ошибок
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "retries_performed": 0,
            "successful_retries": 0,
            "last_error_time": None
        }
        
        # Конфигурация стратегий повторных попыток для разных типов ошибок
        self.retry_strategies = {
            LLMErrorType.RATE_LIMIT: RetryStrategy.EXPONENTIAL_BACKOFF,
            LLMErrorType.TIMEOUT: RetryStrategy.LINEAR_BACKOFF,
            LLMErrorType.CONNECTION_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            LLMErrorType.INTERNAL_SERVER: RetryStrategy.EXPONENTIAL_BACKOFF,
            LLMErrorType.SERVICE_UNAVAILABLE: RetryStrategy.EXPONENTIAL_BACKOFF,
            LLMErrorType.AUTHENTICATION: RetryStrategy.NO_RETRY,
            LLMErrorType.INVALID_REQUEST: RetryStrategy.NO_RETRY,
            LLMErrorType.CONTENT_POLICY: RetryStrategy.NO_RETRY,
            LLMErrorType.CONTEXT_WINDOW: RetryStrategy.NO_RETRY,
            LLMErrorType.NOT_FOUND: RetryStrategy.NO_RETRY,
            LLMErrorType.PERMISSION_DENIED: RetryStrategy.NO_RETRY,
            LLMErrorType.UNPROCESSABLE_ENTITY: RetryStrategy.NO_RETRY,
            LLMErrorType.EMPTY_RESPONSE: RetryStrategy.IMMEDIATE_RETRY,
            LLMErrorType.INVALID_RESPONSE: RetryStrategy.IMMEDIATE_RETRY,
            LLMErrorType.UNKNOWN_ERROR: RetryStrategy.LINEAR_BACKOFF
        }
        
        self.logger.info(f"[LLM-ERROR-HANDLER] Инициализирован с max_retries={max_retries}, base_delay={base_delay}s")

    def with_error_handling(self, func: Callable) -> Callable:
        """
        Декоратор для автоматической обработки ошибок LLM с повторными попытками.
        
        Args:
            func: Функция для обёртки
            
        Returns:
            Обёрнутая функция с обработкой ошибок
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._execute_with_retry(func, *args, **kwargs)
        return wrapper

    def handle_llm_error(self, error: Exception, model_id: str = "unknown", 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обрабатывает ошибку LLM и возвращает структурированный ответ.
        
        Args:
            error: Исключение
            model_id: Идентификатор модели
            context: Дополнительный контекст
            
        Returns:
            Структурированный ответ об ошибке
        """
        try:
            # Определяем тип ошибки
            error_type = self._classify_error(error)
            
            # Обновляем статистику
            self._update_error_stats(error_type)
            
            # Создаём информацию об ошибке
            error_info = self._create_error_info(error, error_type, model_id, context)
            
            # Логируем ошибку
            self._log_error(error_info)
            
            # Создаём структурированный ответ
            response = self._create_error_response(error_info)
            
            return response
            
        except Exception as e:
            # Критическая ошибка в обработчике ошибок
            self.logger.critical(f"[LLM-ERROR-HANDLER] Критическая ошибка в обработчике: {e}")
            return self._create_fallback_error_response(error, model_id)

    def validate_llm_response(self, response: Any, model_id: str = "unknown") -> Dict[str, Any]:
        """
        Валидирует ответ LLM на пустоту и корректность.
        
        Args:
            response: Ответ от LLM
            model_id: Идентификатор модели
            
        Returns:
            Результат валидации или ошибка
        """
        try:
            # Проверка на None
            if response is None:
                return self._create_validation_error("LLM вернул None", model_id)
            
            # Проверка на пустую строку
            if isinstance(response, str) and not response.strip():
                return self._create_validation_error("LLM вернул пустую строку", model_id)
            
            # Проверка на пустой объект
            if isinstance(response, dict) and not response:
                return self._create_validation_error("LLM вернул пустой объект", model_id)
            
            # Проверка на пустой список
            if isinstance(response, list) and not response:
                return self._create_validation_error("LLM вернул пустой список", model_id)
            
            # Проверка на специальные значения-заглушки
            if isinstance(response, str):
                response_lower = response.lower().strip()
                if response_lower in ["", "null", "none", "undefined", "пустой ответ", "empty response"]:
                    return self._create_validation_error(f"LLM вернул заглушку: '{response}'", model_id)
            
            # Если всё в порядке
            return {
                "status": "success",
                "valid": True,
                "response": response,
                "model_id": model_id
            }
            
        except Exception as e:
            self.logger.error(f"[LLM-ERROR-HANDLER] Ошибка валидации ответа: {e}")
            return self._create_validation_error(f"Ошибка валидации: {str(e)}", model_id)

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику ошибок.
        
        Returns:
            Статистика ошибок
        """
        return {
            **self.error_stats,
            "retry_success_rate": (
                self.error_stats["successful_retries"] / max(self.error_stats["retries_performed"], 1)
            ) * 100 if self.error_stats["retries_performed"] > 0 else 0
        }

    def reset_statistics(self) -> None:
        """Сбрасывает статистику ошибок."""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "retries_performed": 0,
            "successful_retries": 0,
            "last_error_time": None
        }
        self.logger.info("[LLM-ERROR-HANDLER] Статистика ошибок сброшена")

    # Приватные методы

    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет функцию с автоматическими повторными попытками.
        
        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Результат выполнения функции
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Валидируем результат
                model_id = kwargs.get('model_id', 'unknown')
                validation = self.validate_llm_response(result, model_id)
                
                if validation.get("valid", False):
                    if attempt > 0:
                        self.error_stats["successful_retries"] += 1
                        self.logger.info(f"[LLM-ERROR-HANDLER] Успешная попытка {attempt + 1}/{self.max_retries + 1}")
                    return result
                else:
                    # Результат не прошёл валидацию
                    error_msg = validation.get("error", "Некорректный ответ LLM")
                    raise ValueError(error_msg)
                    
            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)
                
                # Проверяем, нужно ли повторять попытку
                if attempt < self.max_retries and self._should_retry(error_type):
                    self.error_stats["retries_performed"] += 1
                    delay = self._calculate_delay(error_type, attempt)
                    
                    self.logger.warning(
                        f"[LLM-ERROR-HANDLER] Попытка {attempt + 1}/{self.max_retries + 1} неудачна: {str(e)}. "
                        f"Повтор через {delay:.2f}s"
                    )
                    
                    time.sleep(delay)
                    continue
                else:
                    # Больше не повторяем
                    break
        
        # Все попытки исчерпаны, возвращаем ошибку
        if last_error:
            error_response = self.handle_llm_error(last_error, kwargs.get('model_id', 'unknown'))
            raise Exception(f"LLM error after {self.max_retries + 1} attempts: {error_response.get('message', str(last_error))}")
        else:
            raise Exception(f"Unknown error after {self.max_retries + 1} attempts")

    def _classify_error(self, error: Exception) -> LLMErrorType:
        """
        Классифицирует ошибку по типу.
        
        Args:
            error: Исключение
            
        Returns:
            Тип ошибки
        """
        error_class = error.__class__.__name__
        
        # Прямое сопоставление по классу исключения
        if isinstance(error, RateLimitError):
            return LLMErrorType.RATE_LIMIT
        elif isinstance(error, AuthenticationError):
            return LLMErrorType.AUTHENTICATION
        elif isinstance(error, InvalidRequestError):
            return LLMErrorType.INVALID_REQUEST
        elif isinstance(error, BadRequestError):
            return LLMErrorType.INVALID_REQUEST
        elif isinstance(error, Timeout):
            return LLMErrorType.TIMEOUT
        elif isinstance(error, APIConnectionError):
            return LLMErrorType.CONNECTION_ERROR
        elif isinstance(error, ContentPolicyViolationError):
            return LLMErrorType.CONTENT_POLICY
        elif isinstance(error, ContextWindowExceededError):
            return LLMErrorType.CONTEXT_WINDOW
        elif isinstance(error, InternalServerError):
            return LLMErrorType.INTERNAL_SERVER
        elif isinstance(error, NotFoundError):
            return LLMErrorType.NOT_FOUND
        elif isinstance(error, PermissionDeniedError):
            return LLMErrorType.PERMISSION_DENIED
        elif isinstance(error, ServiceUnavailableError):
            return LLMErrorType.SERVICE_UNAVAILABLE
        elif isinstance(error, UnprocessableEntityError):
            return LLMErrorType.UNPROCESSABLE_ENTITY
        elif isinstance(error, APIError):
            return LLMErrorType.API_ERROR
        
        # Классификация по имени класса (для заглушек в тестах)
        if error_class == "RateLimitError":
            return LLMErrorType.RATE_LIMIT
        elif error_class == "AuthenticationError":
            return LLMErrorType.AUTHENTICATION
        elif error_class == "Timeout":
            return LLMErrorType.TIMEOUT
        elif error_class == "APIConnectionError":
            return LLMErrorType.CONNECTION_ERROR
        elif error_class == "ContentPolicyViolationError":
            return LLMErrorType.CONTENT_POLICY
        elif error_class == "ContextWindowExceededError":
            return LLMErrorType.CONTEXT_WINDOW
        
        # Классификация по содержимому сообщения
        error_message = str(error).lower()
        
        if any(keyword in error_message for keyword in ["rate limit", "quota", "too many requests"]):
            return LLMErrorType.RATE_LIMIT
        elif any(keyword in error_message for keyword in ["authentication", "api key", "unauthorized"]):
            return LLMErrorType.AUTHENTICATION
        elif any(keyword in error_message for keyword in ["timeout", "timed out"]):
            return LLMErrorType.TIMEOUT
        elif any(keyword in error_message for keyword in ["connection", "network", "dns"]):
            return LLMErrorType.CONNECTION_ERROR
        elif any(keyword in error_message for keyword in ["empty", "пустой", "null", "none"]):
            return LLMErrorType.EMPTY_RESPONSE
        elif any(keyword in error_message for keyword in ["invalid", "malformed", "corrupt"]):
            return LLMErrorType.INVALID_RESPONSE
        
        return LLMErrorType.UNKNOWN_ERROR

    def _should_retry(self, error_type: LLMErrorType) -> bool:
        """
        Определяет, следует ли повторять попытку для данного типа ошибки.
        
        Args:
            error_type: Тип ошибки
            
        Returns:
            True, если следует повторить попытку
        """
        strategy = self.retry_strategies.get(error_type, RetryStrategy.NO_RETRY)
        return strategy != RetryStrategy.NO_RETRY

    def _calculate_delay(self, error_type: LLMErrorType, attempt: int) -> float:
        """
        Вычисляет задержку перед повторной попыткой.
        
        Args:
            error_type: Тип ошибки
            attempt: Номер попытки (начиная с 0)
            
        Returns:
            Задержка в секундах
        """
        strategy = self.retry_strategies.get(error_type, RetryStrategy.LINEAR_BACKOFF)
        
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            # Экспоненциальная задержка: base_delay * 2^attempt
            return self.base_delay * (2 ** attempt)
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            # Линейная задержка: base_delay * (attempt + 1)
            return self.base_delay * (attempt + 1)
        elif strategy == RetryStrategy.IMMEDIATE_RETRY:
            # Немедленная повторная попытка
            return 0.1  # Минимальная задержка для избежания спама
        else:
            # По умолчанию линейная задержка
            return self.base_delay * (attempt + 1)

    def _update_error_stats(self, error_type: LLMErrorType) -> None:
        """
        Обновляет статистику ошибок.
        
        Args:
            error_type: Тип ошибки
        """
        self.error_stats["total_errors"] += 1
        self.error_stats["last_error_time"] = datetime.now().isoformat()
        
        error_type_str = error_type.value
        if error_type_str not in self.error_stats["errors_by_type"]:
            self.error_stats["errors_by_type"][error_type_str] = 0
        self.error_stats["errors_by_type"][error_type_str] += 1

    def _create_error_info(self, error: Exception, error_type: LLMErrorType, 
                          model_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Создаёт структурированную информацию об ошибке.
        
        Args:
            error: Исключение
            error_type: Тип ошибки
            model_id: Идентификатор модели
            context: Дополнительный контекст
            
        Returns:
            Информация об ошибке
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type.value,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "model_id": model_id,
            "context": context or {},
            "traceback": traceback.format_exc(),
            "retry_strategy": self.retry_strategies.get(error_type, RetryStrategy.NO_RETRY).value
        }

    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """
        Логирует ошибку с соответствующим уровнем.
        
        Args:
            error_info: Информация об ошибке
        """
        error_type = error_info["error_type"]
        model_id = error_info["model_id"]
        error_message = error_info["error_message"]
        
        log_message = f"[LLM-ERROR] {error_type} для модели {model_id}: {error_message}"
        
        # Определяем уровень логирования по типу ошибки
        if error_type in [LLMErrorType.AUTHENTICATION.value, LLMErrorType.PERMISSION_DENIED.value]:
            self.logger.error(log_message)
        elif error_type in [LLMErrorType.RATE_LIMIT.value, LLMErrorType.TIMEOUT.value]:
            self.logger.warning(log_message)
        elif error_type in [LLMErrorType.EMPTY_RESPONSE.value, LLMErrorType.INVALID_RESPONSE.value]:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
        
        # Дополнительное логирование контекста для отладки
        if error_info.get("context"):
            self.logger.debug(f"[LLM-ERROR] Контекст: {error_info['context']}")

    def _create_error_response(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создаёт структурированный ответ об ошибке для API.
        
        Args:
            error_info: Информация об ошибке
            
        Returns:
            Структурированный ответ об ошибке
        """
        error_type = error_info["error_type"]
        error_message = error_info["error_message"]
        model_id = error_info["model_id"]
        
        # Базовая структура ответа
        response = {
            "status": "error",
            "error_code": error_type.upper(),
            "message": self._get_user_friendly_message(error_type, error_message),
            "model_id": model_id,
            "timestamp": error_info["timestamp"],
            "retryable": self._should_retry(LLMErrorType(error_type))
        }
        
        # Добавляем специфичные поля для определённых типов ошибок
        if error_type == LLMErrorType.RATE_LIMIT.value:
            response["retry_after"] = self._estimate_retry_after(error_message)
        elif error_type == LLMErrorType.CONTEXT_WINDOW.value:
            response["suggestion"] = "Сократите размер входного сообщения или используйте модель с большим контекстным окном"
        elif error_type == LLMErrorType.AUTHENTICATION.value:
            response["suggestion"] = "Проверьте правильность API ключа и его активность"
        
        return response

    def _create_validation_error(self, message: str, model_id: str) -> Dict[str, Any]:
        """
        Создаёт ошибку валидации.
        
        Args:
            message: Сообщение об ошибке
            model_id: Идентификатор модели
            
        Returns:
            Ошибка валидации
        """
        self._update_error_stats(LLMErrorType.EMPTY_RESPONSE)
        
        return {
            "status": "error",
            "valid": False,
            "error_code": "EMPTY_RESPONSE",
            "message": message,
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "retryable": True,
            "suggestion": "Попробуйте переформулировать запрос или использовать другую модель"
        }

    def _create_fallback_error_response(self, error: Exception, model_id: str) -> Dict[str, Any]:
        """
        Создаёт резервный ответ об ошибке.
        
        Args:
            error: Исключение
            model_id: Идентификатор модели
            
        Returns:
            Резервный ответ об ошибке
        """
        return {
            "status": "error",
            "error_code": "HANDLER_ERROR",
            "message": f"Критическая ошибка в обработчике ошибок: {str(error)}",
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "retryable": False
        }

    def _get_user_friendly_message(self, error_type: str, original_message: str) -> str:
        """
        Возвращает понятное пользователю сообщение об ошибке.
        
        Args:
            error_type: Тип ошибки
            original_message: Оригинальное сообщение об ошибке
            
        Returns:
            Понятное пользователю сообщение
        """
        messages = {
            LLMErrorType.RATE_LIMIT.value: "Превышен лимит запросов к модели. Попробуйте позже или используйте другую модель.",
            LLMErrorType.AUTHENTICATION.value: "Ошибка аутентификации. Проверьте правильность API ключа.",
            LLMErrorType.INVALID_REQUEST.value: "Некорректный запрос к модели. Проверьте параметры запроса.",
            LLMErrorType.TIMEOUT.value: "Превышено время ожидания ответа от модели. Попробуйте ещё раз.",
            LLMErrorType.CONNECTION_ERROR.value: "Ошибка подключения к сервису модели. Проверьте интернет-соединение.",
            LLMErrorType.CONTENT_POLICY.value: "Запрос нарушает политику контента модели. Измените формулировку.",
            LLMErrorType.CONTEXT_WINDOW.value: "Запрос слишком длинный для модели. Сократите размер сообщения.",
            LLMErrorType.INTERNAL_SERVER.value: "Внутренняя ошибка сервера модели. Попробуйте позже.",
            LLMErrorType.SERVICE_UNAVAILABLE.value: "Сервис модели временно недоступен. Попробуйте позже.",
            LLMErrorType.EMPTY_RESPONSE.value: "Модель вернула пустой ответ. Попробуйте переформулировать запрос.",
            LLMErrorType.INVALID_RESPONSE.value: "Модель вернула некорректный ответ. Попробуйте ещё раз.",
        }
        
        return messages.get(error_type, f"Неизвестная ошибка модели: {original_message}")

    def _estimate_retry_after(self, error_message: str) -> int:
        """
        Оценивает время до следующей попытки для rate limit ошибок.
        
        Args:
            error_message: Сообщение об ошибке
            
        Returns:
            Время в секундах
        """
        # Пытаемся извлечь время из сообщения об ошибке
        import re
        
        # Ищем паттерны типа "retry after 60 seconds" или "wait 2 minutes"
        patterns = [
            r'retry after (\d+) seconds?',
            r'wait (\d+) seconds?',
            r'retry in (\d+) seconds?',
            r'(\d+) seconds? remaining',
            r'retry after (\d+) minutes?',
            r'wait (\d+) minutes?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message.lower())
            if match:
                value = int(match.group(1))
                if 'minute' in pattern:
                    value *= 60  # Конвертируем минуты в секунды
                return value
        
        # Если не удалось извлечь, возвращаем стандартное значение
        return 60  # 1 минута по умолчанию


# Глобальный экземпляр обработчика ошибок LLM
llm_error_handler = LLMErrorHandler()


def with_llm_error_handling(func: Callable) -> Callable:
    """
    Декоратор для автоматической обработки ошибок LLM.
    
    Args:
        func: Функция для обёртки
        
    Returns:
        Обёрнутая функция
    """
    return llm_error_handler.with_error_handling(func)