"""
Интеграция системы стандартизации API ответов с существующими обработчиками ошибок.
Связывает api_response_builder с error_handler и llm_error_handler.
"""

import logging
from typing import Dict, Any, Optional, Union

from .api_response_builder import (
    APIResponseBuilder, APIErrorCode, ModelInfo, ErrorCodeMapper,
    create_success_response, create_error_response
)

logger = logging.getLogger(__name__)


class APIErrorIntegration:
    """
    Интеграционный слой между существующими обработчиками ошибок и новой системой API ответов.
    """
    
    def __init__(self):
        self.response_builder = APIResponseBuilder()
        self.logger = logger
        
    def handle_llm_error_to_api(
        self, 
        error: Exception, 
        model_id: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Преобразует ошибку LLM в стандартизированный API ответ.
        
        Args:
            error: Исключение LLM
            model_id: Идентификатор модели
            context: Дополнительный контекст
            
        Returns:
            Стандартизированный API ответ об ошибке
        """
        try:
            # Импортируем LLM error handler
            from .llm_error_handler import llm_error_handler, LLMErrorType
            
            # Получаем структурированную информацию об ошибке
            error_info = llm_error_handler.handle_llm_error(error, model_id, context)
            
            # Определяем код ошибки API
            llm_error_type = error_info.get("error_code", "UNKNOWN_ERROR").lower()
            api_error_code = ErrorCodeMapper.map_llm_error(llm_error_type)
            
            # Определяем retry_after для rate limit ошибок
            retry_after = None
            if api_error_code == APIErrorCode.RATE_LIMIT_EXCEEDED:
                retry_after = self._extract_retry_after(error_info)
            
            # Создаём модель информацию
            model_info = ModelInfo(
                model_id=model_id,
                provider=self._extract_provider_from_model_id(model_id)
            )
            
            # Формируем детали ошибки
            details = {
                "original_error": str(error),
                "error_class": error.__class__.__name__,
                "timestamp": error_info.get("timestamp"),
                "context": context or {}
            }
            
            # Создаём стандартизированный ответ
            return self.response_builder.model_error_response(
                model_id=model_id,
                error_message=error_info.get("message", str(error)),
                error_code=api_error_code,
                retryable=error_info.get("retryable", False)
            )
            
        except ImportError:
            # Fallback если LLM error handler недоступен
            self.logger.warning("LLM Error Handler недоступен, используем базовую обработку")
            return self._create_fallback_llm_error_response(error, model_id)
        except Exception as e:
            self.logger.error(f"Ошибка интеграции LLM error handler: {e}")
            return self._create_fallback_llm_error_response(error, model_id)
    
    def handle_tool_error_to_api(
        self,
        error: Exception,
        tool_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Преобразует ошибку инструмента в стандартизированный API ответ.
        
        Args:
            error: Исключение инструмента
            tool_name: Имя инструмента
            context: Дополнительный контекст
            
        Returns:
            Стандартизированный API ответ об ошибке
        """
        try:
            # Импортируем error handler
            from .error_handler import error_handler
            
            # Получаем пользовательское сообщение об ошибке
            user_message = error_handler.handle_tool_error(error, tool_name, context)
            
            # Определяем код ошибки API на основе типа исключения
            api_error_code = ErrorCodeMapper.map_exception(error)
            
            # Если это не специфичная ошибка, используем общий код ошибки инструмента
            if api_error_code == APIErrorCode.UNKNOWN_ERROR:
                api_error_code = APIErrorCode.TOOL_EXECUTION_ERROR
            
            # Создаём стандартизированный ответ
            return self.response_builder.tool_error_response(
                tool_name=tool_name,
                error_message=user_message,
                error_code=api_error_code,
                retryable=self._is_tool_error_retryable(error)
            )
            
        except ImportError:
            # Fallback если error handler недоступен
            self.logger.warning("Error Handler недоступен, используем базовую обработку")
            return self._create_fallback_tool_error_response(error, tool_name)
        except Exception as e:
            self.logger.error(f"Ошибка интеграции Tool error handler: {e}")
            return self._create_fallback_tool_error_response(error, tool_name)
    
    def handle_file_error_to_api(
        self,
        error: Exception,
        operation: str,
        path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Преобразует файловую ошибку в стандартизированный API ответ.
        
        Args:
            error: Файловое исключение
            operation: Тип операции
            path: Путь к файлу
            context: Дополнительный контекст
            
        Returns:
            Стандартизированный API ответ об ошибке
        """
        try:
            # Импортируем error handler
            from .error_handler import error_handler
            
            # Получаем пользовательское сообщение об ошибке
            user_message = error_handler.handle_file_operation_error(error, operation, path, context)
            
            # Определяем код ошибки API на основе типа исключения
            api_error_code = ErrorCodeMapper.map_exception(error)
            
            # Создаём детали ошибки
            details = {
                "operation": operation,
                "path": path,
                "original_error": str(error),
                "context": context or {}
            }
            
            # Определяем предложения по исправлению
            suggestions = self._get_file_error_suggestions(error, operation, path)
            
            # Создаём стандартизированный ответ
            return self.response_builder.error_response(
                error_code=api_error_code,
                message=user_message,
                details=details,
                retryable=self._is_file_error_retryable(error),
                suggestions=suggestions
            )
            
        except ImportError:
            # Fallback если error handler недоступен
            self.logger.warning("Error Handler недоступен, используем базовую обработку")
            return self._create_fallback_file_error_response(error, operation, path)
        except Exception as e:
            self.logger.error(f"Ошибка интеграции File error handler: {e}")
            return self._create_fallback_file_error_response(error, operation, path)
    
    def handle_network_error_to_api(
        self,
        error: Exception,
        url: str,
        operation: str = "request",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Преобразует сетевую ошибку в стандартизированный API ответ.
        
        Args:
            error: Сетевое исключение
            url: URL, вызвавший ошибку
            operation: Тип операции
            context: Дополнительный контекст
            
        Returns:
            Стандартизированный API ответ об ошибке
        """
        try:
            # Импортируем error handler
            from .error_handler import error_handler
            
            # Получаем пользовательское сообщение об ошибке
            user_message = error_handler.handle_network_error(error, url, operation, context)
            
            # Определяем код ошибки API
            api_error_code = self._classify_network_error(error)
            
            # Создаём детали ошибки
            details = {
                "url": url,
                "operation": operation,
                "original_error": str(error),
                "context": context or {}
            }
            
            # Определяем предложения по исправлению
            suggestions = self._get_network_error_suggestions(error, url)
            
            # Создаём стандартизированный ответ
            return self.response_builder.error_response(
                error_code=api_error_code,
                message=user_message,
                details=details,
                retryable=True,  # Сетевые ошибки обычно можно повторить
                suggestions=suggestions
            )
            
        except ImportError:
            # Fallback если error handler недоступен
            self.logger.warning("Error Handler недоступен, используем базовую обработку")
            return self._create_fallback_network_error_response(error, url)
        except Exception as e:
            self.logger.error(f"Ошибка интеграции Network error handler: {e}")
            return self._create_fallback_network_error_response(error, url)
    
    def create_successful_response(
        self,
        data: Any,
        message: Optional[str] = None,
        model_info: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт стандартизированный успешный ответ API.
        
        Args:
            data: Основные данные ответа
            message: Опциональное сообщение
            model_info: Информация о модели
            execution_time: Время выполнения
            metadata: Дополнительные метаданные
            
        Returns:
            Стандартизированный успешный ответ
        """
        # Если передано время выполнения, устанавливаем его
        if execution_time is not None:
            self.response_builder._start_time = time.time() - execution_time
        
        # Преобразуем model_info в объект ModelInfo если нужно
        model_info_obj = None
        if model_info:
            if isinstance(model_info, dict):
                model_info_obj = ModelInfo(
                    model_id=model_info.get("model_id", "unknown"),
                    provider=model_info.get("provider", "unknown"),
                    display_name=model_info.get("display_name"),
                    version=model_info.get("version"),
                    capabilities=model_info.get("capabilities")
                )
            else:
                model_info_obj = model_info
        
        return self.response_builder.success_response(
            data=data,
            message=message,
            model_info=model_info_obj,
            metadata=metadata
        )
    
    # Приватные методы
    
    def _extract_retry_after(self, error_info: Dict[str, Any]) -> Optional[int]:
        """Извлекает время retry_after из информации об ошибке."""
        return error_info.get("retry_after", 60)  # По умолчанию 60 секунд
    
    def _extract_provider_from_model_id(self, model_id: str) -> str:
        """Извлекает провайдера из идентификатора модели."""
        if "/" in model_id:
            return model_id.split("/")[0]
        elif "gemini" in model_id.lower():
            return "gemini"
        elif "gpt" in model_id.lower() or "openai" in model_id.lower():
            return "openai"
        else:
            return "unknown"
    
    def _is_tool_error_retryable(self, error: Exception) -> bool:
        """Определяет, можно ли повторить запрос после ошибки инструмента."""
        # Ошибки разрешений и безопасности не повторяемы
        if isinstance(error, PermissionError):
            return False
        # Ошибки валидации не повторяемы
        if isinstance(error, (ValueError, TypeError)):
            return False
        # Остальные ошибки можно повторить
        return True
    
    def _is_file_error_retryable(self, error: Exception) -> bool:
        """Определяет, можно ли повторить запрос после файловой ошибки."""
        # Ошибки разрешений и отсутствия файлов не повторяемы
        if isinstance(error, (PermissionError, FileNotFoundError)):
            return False
        # Остальные ошибки можно повторить
        return True
    
    def _classify_network_error(self, error: Exception) -> APIErrorCode:
        """Классифицирует сетевую ошибку."""
        error_name = error.__class__.__name__.lower()
        error_message = str(error).lower()
        
        if "timeout" in error_name or "timeout" in error_message:
            return APIErrorCode.NETWORK_TIMEOUT
        elif "connection" in error_name or "connection" in error_message:
            return APIErrorCode.NETWORK_CONNECTION_ERROR
        elif "http" in error_name or "http" in error_message:
            return APIErrorCode.HTTP_ERROR
        elif "dns" in error_message or "name resolution" in error_message:
            return APIErrorCode.DNS_RESOLUTION_ERROR
        else:
            return APIErrorCode.NETWORK_CONNECTION_ERROR
    
    def _get_file_error_suggestions(self, error: Exception, operation: str, path: str) -> List[str]:
        """Возвращает предложения по исправлению файловых ошибок."""
        suggestions = []
        
        if isinstance(error, FileNotFoundError):
            suggestions = [
                f"Убедитесь, что файл '{path}' существует",
                "Проверьте правильность пути к файлу",
                "Создайте файл, если он должен существовать"
            ]
        elif isinstance(error, PermissionError):
            suggestions = [
                f"Проверьте права доступа к файлу '{path}'",
                "Убедитесь, что файл не используется другим процессом",
                "Запустите приложение с правами администратора"
            ]
        elif isinstance(error, IsADirectoryError):
            suggestions = [
                f"'{path}' является директорией, а ожидался файл",
                "Укажите путь к файлу, а не к директории"
            ]
        else:
            suggestions = [
                "Проверьте правильность пути к файлу",
                "Убедитесь, что у вас есть необходимые права доступа"
            ]
        
        return suggestions
    
    def _get_network_error_suggestions(self, error: Exception, url: str) -> List[str]:
        """Возвращает предложения по исправлению сетевых ошибок."""
        suggestions = []
        
        error_name = error.__class__.__name__.lower()
        
        if "timeout" in error_name:
            suggestions = [
                "Проверьте стабильность интернет-соединения",
                "Попробуйте повторить запрос позже",
                "Увеличьте таймаут запроса"
            ]
        elif "connection" in error_name:
            suggestions = [
                "Проверьте интернет-соединение",
                f"Убедитесь, что сервер {url} доступен",
                "Проверьте настройки прокси или брандмауэра"
            ]
        else:
            suggestions = [
                "Проверьте интернет-соединение",
                "Попробуйте повторить запрос позже"
            ]
        
        return suggestions
    
    def _create_fallback_llm_error_response(self, error: Exception, model_id: str) -> Dict[str, Any]:
        """Создаёт fallback ответ для ошибки LLM."""
        return create_error_response(
            error_code=APIErrorCode.UNKNOWN_ERROR,
            message=f"LLM error for model '{model_id}': {str(error)}",
            details={"model_id": model_id, "original_error": str(error)},
            retryable=True
        )
    
    def _create_fallback_tool_error_response(self, error: Exception, tool_name: str) -> Dict[str, Any]:
        """Создаёт fallback ответ для ошибки инструмента."""
        return create_error_response(
            error_code=APIErrorCode.TOOL_EXECUTION_ERROR,
            message=f"Tool '{tool_name}' execution failed: {str(error)}",
            details={"tool_name": tool_name, "original_error": str(error)},
            retryable=True
        )
    
    def _create_fallback_file_error_response(self, error: Exception, operation: str, path: str) -> Dict[str, Any]:
        """Создаёт fallback ответ для файловой ошибки."""
        api_error_code = ErrorCodeMapper.map_exception(error)
        return create_error_response(
            error_code=api_error_code,
            message=f"File operation '{operation}' failed for '{path}': {str(error)}",
            details={"operation": operation, "path": path, "original_error": str(error)},
            retryable=False
        )
    
    def _create_fallback_network_error_response(self, error: Exception, url: str) -> Dict[str, Any]:
        """Создаёт fallback ответ для сетевой ошибки."""
        return create_error_response(
            error_code=APIErrorCode.NETWORK_CONNECTION_ERROR,
            message=f"Network error for '{url}': {str(error)}",
            details={"url": url, "original_error": str(error)},
            retryable=True
        )


# Глобальный экземпляр интеграции
api_error_integration = APIErrorIntegration()


# Удобные функции для использования в других модулях

def handle_llm_error_to_api(
    error: Exception, 
    model_id: str = "unknown",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Удобная функция для преобразования ошибки LLM в API ответ.
    """
    return api_error_integration.handle_llm_error_to_api(error, model_id, context)


def handle_tool_error_to_api(
    error: Exception,
    tool_name: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Удобная функция для преобразования ошибки инструмента в API ответ.
    """
    return api_error_integration.handle_tool_error_to_api(error, tool_name, context)


def create_successful_api_response(
    data: Any,
    message: Optional[str] = None,
    model_info: Optional[Dict[str, Any]] = None,
    execution_time: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Удобная функция для создания успешного API ответа.
    """
    return api_error_integration.create_successful_response(
        data, message, model_info, execution_time, metadata
    )


# Импорты для типов
import time
from typing import List, Any