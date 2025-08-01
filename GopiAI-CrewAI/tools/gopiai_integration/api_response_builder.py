"""
API Response Standardization System для GopiAI.
Реализует требования 2.5, 4.2, 4.3 из спецификации.

Обеспечивает:
- Единообразный JSON формат для всех API endpoints
- Систему кодов ошибок для разных типов ошибок
- Поле retry_after для rate limit ошибок
- Включение execution_time и model_info в успешные ответы
- Утилиты для построения структурированных ответов
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class APIErrorCode(Enum):
    """Стандартные коды ошибок API."""
    
    # LLM ошибки (1000-1999)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    CONTEXT_WINDOW_EXCEEDED = "CONTEXT_WINDOW_EXCEEDED"
    CONTENT_POLICY_VIOLATION = "CONTENT_POLICY_VIOLATION"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    
    # Tool ошибки (2000-2999)
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    COMMAND_NOT_ALLOWED = "COMMAND_NOT_ALLOWED"
    
    # Файловые ошибки (3000-3999)
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_PERMISSION_DENIED = "FILE_PERMISSION_DENIED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    DIRECTORY_NOT_FOUND = "DIRECTORY_NOT_FOUND"
    INVALID_FILE_PATH = "INVALID_FILE_PATH"
    
    # Сетевые ошибки (4000-4999)
    NETWORK_CONNECTION_ERROR = "NETWORK_CONNECTION_ERROR"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    HTTP_ERROR = "HTTP_ERROR"
    DNS_RESOLUTION_ERROR = "DNS_RESOLUTION_ERROR"
    
    # Системные ошибки (5000-5999)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    
    # Валидационные ошибки (6000-6999)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
    INVALID_JSON_FORMAT = "INVALID_JSON_FORMAT"
    
    # Общие ошибки (9000-9999)
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    DEPRECATED_ENDPOINT = "DEPRECATED_ENDPOINT"


class ResponseStatus(Enum):
    """Статусы ответов API."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL_SUCCESS = "partial_success"
    PROCESSING = "processing"


@dataclass
class ModelInfo:
    """Информация о модели, использованной для генерации ответа."""
    model_id: str
    provider: str
    display_name: Optional[str] = None
    version: Optional[str] = None
    capabilities: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь, исключая None значения."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class ExecutionInfo:
    """Информация о выполнении запроса."""
    execution_time: float
    started_at: str
    completed_at: str
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь, исключая None значения."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


class APIResponseBuilder:
    """
    Строитель стандартизированных API ответов.
    
    Обеспечивает единообразный формат ответов для всех endpoints GopiAI API.
    """
    
    def __init__(self):
        self.logger = logger
        self._start_time = None
        self._request_id = None
        
    def start_request(self, request_id: Optional[str] = None) -> 'APIResponseBuilder':
        """
        Начинает отслеживание времени выполнения запроса.
        
        Args:
            request_id: Уникальный идентификатор запроса
            
        Returns:
            Self для цепочки вызовов
        """
        self._start_time = time.time()
        self._request_id = request_id
        return self
    
    def success_response(
        self,
        data: Any,
        message: Optional[str] = None,
        model_info: Optional[Union[ModelInfo, Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт успешный ответ API.
        
        Args:
            data: Основные данные ответа
            message: Опциональное сообщение
            model_info: Информация о модели
            metadata: Дополнительные метаданные
            
        Returns:
            Стандартизированный успешный ответ
        """
        response = {
            "status": ResponseStatus.SUCCESS.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if message:
            response["message"] = message
            
        # Добавляем информацию о выполнении
        if self._start_time is not None:
            execution_info = self._create_execution_info()
            response["execution"] = execution_info.to_dict()
        
        # Добавляем информацию о модели
        if model_info:
            if isinstance(model_info, ModelInfo):
                response["model_info"] = model_info.to_dict()
            elif isinstance(model_info, dict):
                response["model_info"] = model_info
        
        # Добавляем метаданные
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    def error_response(
        self,
        error_code: Union[APIErrorCode, str],
        message: str,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
        retryable: bool = False,
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт ответ об ошибке API.
        
        Args:
            error_code: Код ошибки
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
            retry_after: Время до следующей попытки (секунды)
            retryable: Можно ли повторить запрос
            suggestions: Предложения по исправлению
            
        Returns:
            Стандартизированный ответ об ошибке
        """
        if isinstance(error_code, APIErrorCode):
            error_code = error_code.value
            
        response = {
            "status": ResponseStatus.ERROR.value,
            "error": {
                "code": error_code,
                "message": message,
                "retryable": retryable
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Добавляем retry_after для rate limit ошибок
        if retry_after is not None:
            response["error"]["retry_after"] = retry_after
            
        # Добавляем детали ошибки
        if details:
            response["error"]["details"] = details
            
        # Добавляем предложения
        if suggestions:
            response["error"]["suggestions"] = suggestions
            
        # Добавляем информацию о выполнении
        if self._start_time is not None:
            execution_info = self._create_execution_info()
            response["execution"] = execution_info.to_dict()
            
        return response
    
    def partial_success_response(
        self,
        data: Any,
        errors: List[Dict[str, Any]],
        message: Optional[str] = None,
        model_info: Optional[Union[ModelInfo, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт ответ о частичном успехе (некоторые операции успешны, некоторые с ошибками).
        
        Args:
            data: Успешно обработанные данные
            errors: Список ошибок
            message: Опциональное сообщение
            model_info: Информация о модели
            
        Returns:
            Стандартизированный ответ о частичном успехе
        """
        response = {
            "status": ResponseStatus.PARTIAL_SUCCESS.value,
            "data": data,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
        
        if message:
            response["message"] = message
            
        # Добавляем информацию о выполнении
        if self._start_time is not None:
            execution_info = self._create_execution_info()
            response["execution"] = execution_info.to_dict()
        
        # Добавляем информацию о модели
        if model_info:
            if isinstance(model_info, ModelInfo):
                response["model_info"] = model_info.to_dict()
            elif isinstance(model_info, dict):
                response["model_info"] = model_info
                
        return response
    
    def processing_response(
        self,
        task_id: str,
        message: str = "Request is being processed",
        estimated_completion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создаёт ответ о том, что запрос обрабатывается.
        
        Args:
            task_id: Идентификатор задачи
            message: Сообщение о статусе
            estimated_completion: Ожидаемое время завершения
            
        Returns:
            Стандартизированный ответ о обработке
        """
        response = {
            "status": ResponseStatus.PROCESSING.value,
            "task_id": task_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if estimated_completion:
            response["estimated_completion"] = estimated_completion
            
        return response
    
    def validation_error_response(
        self,
        field_errors: Dict[str, str],
        message: str = "Validation failed"
    ) -> Dict[str, Any]:
        """
        Создаёт ответ об ошибке валидации.
        
        Args:
            field_errors: Словарь ошибок по полям
            message: Общее сообщение об ошибке
            
        Returns:
            Стандартизированный ответ об ошибке валидации
        """
        return self.error_response(
            error_code=APIErrorCode.VALIDATION_ERROR,
            message=message,
            details={"field_errors": field_errors},
            retryable=True,
            suggestions=["Проверьте правильность заполнения полей", "Убедитесь, что все обязательные поля заполнены"]
        )
    
    def rate_limit_error_response(
        self,
        retry_after: int,
        limit_type: str = "requests",
        current_usage: Optional[int] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Создаёт ответ об ошибке превышения лимита запросов.
        
        Args:
            retry_after: Время до следующей попытки (секунды)
            limit_type: Тип лимита (requests, tokens, etc.)
            current_usage: Текущее использование
            limit: Максимальный лимит
            
        Returns:
            Стандартизированный ответ об ошибке rate limit
        """
        details = {"limit_type": limit_type}
        if current_usage is not None:
            details["current_usage"] = current_usage
        if limit is not None:
            details["limit"] = limit
            
        return self.error_response(
            error_code=APIErrorCode.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded for {limit_type}. Please try again in {retry_after} seconds.",
            details=details,
            retry_after=retry_after,
            retryable=True,
            suggestions=[
                f"Подождите {retry_after} секунд перед следующим запросом",
                "Рассмотрите возможность использования другой модели",
                "Уменьшите частоту запросов"
            ]
        )
    
    def tool_error_response(
        self,
        tool_name: str,
        error_message: str,
        error_code: Union[APIErrorCode, str] = APIErrorCode.TOOL_EXECUTION_ERROR,
        retryable: bool = True
    ) -> Dict[str, Any]:
        """
        Создаёт ответ об ошибке выполнения инструмента.
        
        Args:
            tool_name: Имя инструмента
            error_message: Сообщение об ошибке
            error_code: Код ошибки
            retryable: Можно ли повторить запрос
            
        Returns:
            Стандартизированный ответ об ошибке инструмента
        """
        return self.error_response(
            error_code=error_code,
            message=f"Tool '{tool_name}' execution failed: {error_message}",
            details={"tool_name": tool_name, "original_error": error_message},
            retryable=retryable,
            suggestions=[
                "Проверьте правильность параметров инструмента",
                "Убедитесь, что инструмент доступен",
                "Попробуйте использовать альтернативный инструмент"
            ]
        )
    
    def model_error_response(
        self,
        model_id: str,
        error_message: str,
        error_code: Union[APIErrorCode, str],
        retryable: bool = True
    ) -> Dict[str, Any]:
        """
        Создаёт ответ об ошибке модели.
        
        Args:
            model_id: Идентификатор модели
            error_message: Сообщение об ошибке
            error_code: Код ошибки
            retryable: Можно ли повторить запрос
            
        Returns:
            Стандартизированный ответ об ошибке модели
        """
        suggestions = []
        
        if error_code == APIErrorCode.CONTEXT_WINDOW_EXCEEDED:
            suggestions = [
                "Сократите размер входного сообщения",
                "Используйте модель с большим контекстным окном",
                "Разбейте запрос на несколько частей"
            ]
        elif error_code == APIErrorCode.CONTENT_POLICY_VIOLATION:
            suggestions = [
                "Измените формулировку запроса",
                "Убедитесь, что контент соответствует политике использования",
                "Попробуйте более нейтральную формулировку"
            ]
        elif error_code == APIErrorCode.MODEL_UNAVAILABLE:
            suggestions = [
                "Попробуйте использовать другую модель",
                "Повторите запрос позже",
                "Проверьте статус сервиса"
            ]
        else:
            suggestions = [
                "Попробуйте использовать другую модель",
                "Повторите запрос позже"
            ]
        
        return self.error_response(
            error_code=error_code,
            message=f"Model '{model_id}' error: {error_message}",
            details={"model_id": model_id, "original_error": error_message},
            retryable=retryable,
            suggestions=suggestions
        )
    
    def _create_execution_info(self) -> ExecutionInfo:
        """
        Создаёт информацию о выполнении запроса.
        
        Returns:
            Информация о выполнении
        """
        now = datetime.now()
        execution_time = time.time() - self._start_time if self._start_time else 0
        
        return ExecutionInfo(
            execution_time=round(execution_time, 3),
            started_at=(now - timedelta(seconds=execution_time)).isoformat(),
            completed_at=now.isoformat(),
            request_id=self._request_id
        )


class ErrorCodeMapper:
    """
    Утилита для сопоставления различных типов ошибок с стандартными кодами API.
    """
    
    # Сопоставление исключений Python с кодами ошибок
    EXCEPTION_MAPPING = {
        # Файловые ошибки
        FileNotFoundError: APIErrorCode.FILE_NOT_FOUND,
        PermissionError: APIErrorCode.FILE_PERMISSION_DENIED,
        IsADirectoryError: APIErrorCode.INVALID_FILE_PATH,
        NotADirectoryError: APIErrorCode.DIRECTORY_NOT_FOUND,
        
        # Сетевые ошибки
        ConnectionError: APIErrorCode.NETWORK_CONNECTION_ERROR,
        TimeoutError: APIErrorCode.NETWORK_TIMEOUT,
        
        # Системные ошибки
        MemoryError: APIErrorCode.MEMORY_ERROR,
        OSError: APIErrorCode.INTERNAL_SERVER_ERROR,
        
        # Валидационные ошибки
        ValueError: APIErrorCode.VALIDATION_ERROR,
        TypeError: APIErrorCode.VALIDATION_ERROR,
        KeyError: APIErrorCode.MISSING_REQUIRED_FIELD,
        
        # JSON ошибки
        json.JSONDecodeError: APIErrorCode.INVALID_JSON_FORMAT,
    }
    
    # Сопоставление LLM ошибок с кодами API
    LLM_ERROR_MAPPING = {
        "rate_limit": APIErrorCode.RATE_LIMIT_EXCEEDED,
        "authentication": APIErrorCode.AUTHENTICATION_ERROR,
        "invalid_request": APIErrorCode.INVALID_REQUEST,
        "context_window": APIErrorCode.CONTEXT_WINDOW_EXCEEDED,
        "content_policy": APIErrorCode.CONTENT_POLICY_VIOLATION,
        "not_found": APIErrorCode.MODEL_NOT_FOUND,
        "service_unavailable": APIErrorCode.MODEL_UNAVAILABLE,
        "empty_response": APIErrorCode.EMPTY_RESPONSE,
        "invalid_response": APIErrorCode.INVALID_RESPONSE,
    }
    
    @classmethod
    def map_exception(cls, exception: Exception) -> APIErrorCode:
        """
        Сопоставляет исключение Python с кодом ошибки API.
        
        Args:
            exception: Исключение Python
            
        Returns:
            Соответствующий код ошибки API
        """
        exception_type = type(exception)
        return cls.EXCEPTION_MAPPING.get(exception_type, APIErrorCode.UNKNOWN_ERROR)
    
    @classmethod
    def map_llm_error(cls, llm_error_type: str) -> APIErrorCode:
        """
        Сопоставляет тип ошибки LLM с кодом ошибки API.
        
        Args:
            llm_error_type: Тип ошибки LLM
            
        Returns:
            Соответствующий код ошибки API
        """
        return cls.LLM_ERROR_MAPPING.get(llm_error_type, APIErrorCode.UNKNOWN_ERROR)


# Глобальный экземпляр строителя ответов
api_response_builder = APIResponseBuilder()


def create_success_response(
    data: Any,
    message: Optional[str] = None,
    model_info: Optional[Union[ModelInfo, Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Удобная функция для создания успешного ответа.
    
    Args:
        data: Основные данные ответа
        message: Опциональное сообщение
        model_info: Информация о модели
        metadata: Дополнительные метаданные
        
    Returns:
        Стандартизированный успешный ответ
    """
    return api_response_builder.success_response(data, message, model_info, metadata)


def create_error_response(
    error_code: Union[APIErrorCode, str],
    message: str,
    details: Optional[Dict[str, Any]] = None,
    retry_after: Optional[int] = None,
    retryable: bool = False,
    suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Удобная функция для создания ответа об ошибке.
    
    Args:
        error_code: Код ошибки
        message: Сообщение об ошибке
        details: Дополнительные детали ошибки
        retry_after: Время до следующей попытки (секунды)
        retryable: Можно ли повторить запрос
        suggestions: Предложения по исправлению
        
    Returns:
        Стандартизированный ответ об ошибке
    """
    return api_response_builder.error_response(error_code, message, details, retry_after, retryable, suggestions)