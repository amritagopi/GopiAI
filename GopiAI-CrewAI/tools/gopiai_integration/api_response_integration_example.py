"""
Пример интеграции системы стандартизации API ответов в GopiAI.
Демонстрирует использование APIResponseBuilder в реальных сценариях.
"""

import time
import json
from typing import Dict, Any, Optional

from api_response_builder import (
    APIResponseBuilder,
    APIErrorCode,
    ModelInfo,
    ErrorCodeMapper,
    create_success_response,
    create_error_response
)


class GopiAIAPIEndpoint:
    """
    Пример API endpoint с использованием стандартизированных ответов.
    """
    
    def __init__(self):
        self.response_builder = APIResponseBuilder()
    
    def process_chat_request(self, message: str, model_id: str, user_id: str) -> Dict[str, Any]:
        """
        Обрабатывает запрос чата с полной стандартизацией ответов.
        
        Args:
            message: Сообщение пользователя
            model_id: Идентификатор модели
            user_id: Идентификатор пользователя
            
        Returns:
            Стандартизированный API ответ
        """
        # Начинаем отслеживание времени выполнения
        request_id = f"chat_{user_id}_{int(time.time())}"
        self.response_builder.start_request(request_id)
        
        try:
            # Валидация входных данных
            validation_errors = self._validate_chat_request(message, model_id, user_id)
            if validation_errors:
                return self.response_builder.validation_error_response(
                    field_errors=validation_errors,
                    message="Ошибка валидации запроса чата"
                )
            
            # Симуляция обработки LLM запроса
            llm_response = self._simulate_llm_call(message, model_id)
            
            # Создание информации о модели
            model_info = ModelInfo(
                model_id=model_id,
                provider="openrouter",
                display_name=self._get_model_display_name(model_id),
                capabilities=["text", "code", "analysis"]
            )
            
            # Метаданные запроса
            metadata = {
                "user_id": user_id,
                "request_id": request_id,
                "message_length": len(message),
                "response_length": len(llm_response["content"]),
                "tokens_used": llm_response.get("tokens_used", 0)
            }
            
            # Успешный ответ
            return self.response_builder.success_response(
                data={
                    "response": llm_response["content"],
                    "has_commands": llm_response.get("has_commands", False),
                    "tools_used": llm_response.get("tools_used", []),
                    "conversation_id": llm_response.get("conversation_id")
                },
                message="Запрос обработан успешно",
                model_info=model_info,
                metadata=metadata
            )
            
        except RateLimitException as e:
            return self.response_builder.rate_limit_error_response(
                retry_after=e.retry_after,
                limit_type="requests",
                current_usage=e.current_usage,
                limit=e.limit
            )
            
        except ModelUnavailableException as e:
            return self.response_builder.model_error_response(
                model_id=model_id,
                error_message=str(e),
                error_code=APIErrorCode.MODEL_UNAVAILABLE,
                retryable=True
            )
            
        except ContextWindowExceededException as e:
            return self.response_builder.model_error_response(
                model_id=model_id,
                error_message=str(e),
                error_code=APIErrorCode.CONTEXT_WINDOW_EXCEEDED,
                retryable=True
            )
            
        except Exception as e:
            # Общая обработка ошибок с автоматическим сопоставлением
            error_code = ErrorCodeMapper.map_exception(e)
            return self.response_builder.error_response(
                error_code=error_code,
                message=f"Произошла ошибка при обработке запроса: {str(e)}",
                details={"exception_type": type(e).__name__, "original_error": str(e)},
                retryable=error_code not in [
                    APIErrorCode.VALIDATION_ERROR,
                    APIErrorCode.AUTHENTICATION_ERROR,
                    APIErrorCode.CONTENT_POLICY_VIOLATION
                ]
            )
    
    def execute_tool_request(self, tool_name: str, tool_args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Выполняет запрос инструмента с обработкой ошибок.
        
        Args:
            tool_name: Имя инструмента
            tool_args: Аргументы инструмента
            user_id: Идентификатор пользователя
            
        Returns:
            Стандартизированный API ответ
        """
        request_id = f"tool_{tool_name}_{user_id}_{int(time.time())}"
        self.response_builder.start_request(request_id)
        
        try:
            # Проверка разрешений на использование инструмента
            if not self._check_tool_permissions(tool_name, user_id):
                return self.response_builder.tool_error_response(
                    tool_name=tool_name,
                    error_message="Недостаточно прав для использования этого инструмента",
                    error_code=APIErrorCode.TOOL_PERMISSION_DENIED,
                    retryable=False
                )
            
            # Выполнение инструмента
            tool_result = self._execute_tool(tool_name, tool_args)
            
            # Успешный ответ
            return self.response_builder.success_response(
                data={
                    "tool_name": tool_name,
                    "result": tool_result["output"],
                    "exit_code": tool_result.get("exit_code", 0),
                    "execution_time": tool_result.get("execution_time", 0)
                },
                message=f"Инструмент '{tool_name}' выполнен успешно",
                metadata={
                    "user_id": user_id,
                    "tool_args": tool_args,
                    "request_id": request_id
                }
            )
            
        except ToolTimeoutException as e:
            return self.response_builder.tool_error_response(
                tool_name=tool_name,
                error_message=f"Превышено время ожидания выполнения ({e.timeout}s)",
                error_code=APIErrorCode.TOOL_TIMEOUT,
                retryable=True
            )
            
        except CommandNotAllowedException as e:
            return self.response_builder.tool_error_response(
                tool_name=tool_name,
                error_message=f"Команда не разрешена: {e.command}",
                error_code=APIErrorCode.COMMAND_NOT_ALLOWED,
                retryable=False
            )
            
        except Exception as e:
            return self.response_builder.tool_error_response(
                tool_name=tool_name,
                error_message=str(e),
                error_code=APIErrorCode.TOOL_EXECUTION_ERROR,
                retryable=True
            )
    
    def get_available_models(self, user_id: str) -> Dict[str, Any]:
        """
        Получает список доступных моделей.
        
        Args:
            user_id: Идентификатор пользователя
            
        Returns:
            Стандартизированный API ответ со списком моделей
        """
        request_id = f"models_{user_id}_{int(time.time())}"
        self.response_builder.start_request(request_id)
        
        try:
            models = self._fetch_available_models(user_id)
            
            return self.response_builder.success_response(
                data={
                    "models": models,
                    "total_count": len(models),
                    "user_tier": self._get_user_tier(user_id)
                },
                message=f"Найдено {len(models)} доступных моделей",
                metadata={
                    "user_id": user_id,
                    "request_id": request_id,
                    "cache_hit": False  # В реальной реализации проверяем кэш
                }
            )
            
        except Exception as e:
            error_code = ErrorCodeMapper.map_exception(e)
            return self.response_builder.error_response(
                error_code=error_code,
                message=f"Ошибка при получении списка моделей: {str(e)}",
                retryable=True
            )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния сервиса.
        
        Returns:
            Стандартизированный API ответ о состоянии
        """
        self.response_builder.start_request("health_check")
        
        try:
            # Проверка различных компонентов системы
            health_status = {
                "database": self._check_database_health(),
                "llm_providers": self._check_llm_providers_health(),
                "memory_system": self._check_memory_system_health(),
                "tools": self._check_tools_health()
            }
            
            overall_healthy = all(health_status.values())
            
            if overall_healthy:
                return self.response_builder.success_response(
                    data={
                        "status": "healthy",
                        "components": health_status,
                        "uptime": self._get_uptime(),
                        "version": "2.0.0"
                    },
                    message="Все системы работают нормально"
                )
            else:
                # Частичный успех - некоторые компоненты недоступны
                failed_components = [k for k, v in health_status.items() if not v]
                
                return self.response_builder.partial_success_response(
                    data={
                        "status": "degraded",
                        "components": health_status,
                        "uptime": self._get_uptime(),
                        "version": "2.0.0"
                    },
                    errors=[
                        {"component": comp, "status": "unhealthy"} 
                        for comp in failed_components
                    ],
                    message=f"Система работает с ограничениями. Недоступны: {', '.join(failed_components)}"
                )
                
        except Exception as e:
            return self.response_builder.error_response(
                error_code=APIErrorCode.INTERNAL_SERVER_ERROR,
                message=f"Ошибка при проверке состояния системы: {str(e)}",
                retryable=True
            )
    
    # Вспомогательные методы (заглушки для демонстрации)
    
    def _validate_chat_request(self, message: str, model_id: str, user_id: str) -> Optional[Dict[str, str]]:
        """Валидация запроса чата."""
        errors = {}
        
        if not message or len(message.strip()) == 0:
            errors["message"] = "Сообщение не может быть пустым"
        elif len(message) > 10000:
            errors["message"] = "Сообщение слишком длинное (максимум 10000 символов)"
            
        if not model_id:
            errors["model_id"] = "Необходимо указать идентификатор модели"
        elif not self._is_valid_model_id(model_id):
            errors["model_id"] = f"Неизвестная модель: {model_id}"
            
        if not user_id:
            errors["user_id"] = "Необходимо указать идентификатор пользователя"
            
        return errors if errors else None
    
    def _simulate_llm_call(self, message: str, model_id: str) -> Dict[str, Any]:
        """Симуляция вызова LLM."""
        # В реальной реализации здесь был бы вызов LLM API
        
        # Симуляция различных сценариев
        if "rate limit" in message.lower():
            raise RateLimitException(retry_after=60, current_usage=100, limit=100)
        elif "context window" in message.lower():
            raise ContextWindowExceededException("Message too long for model context")
        elif "unavailable" in message.lower():
            raise ModelUnavailableException(f"Model {model_id} is currently unavailable")
        
        return {
            "content": f"Ответ на сообщение: {message[:50]}...",
            "tokens_used": len(message.split()) * 2,
            "has_commands": "command" in message.lower(),
            "tools_used": [{"name": "test_tool", "result": "success"}] if "tool" in message.lower() else [],
            "conversation_id": f"conv_{int(time.time())}"
        }
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Симуляция выполнения инструмента."""
        if tool_name == "timeout_tool":
            raise ToolTimeoutException(timeout=30)
        elif tool_name == "forbidden_command":
            raise CommandNotAllowedException(command="rm -rf /")
        
        return {
            "output": f"Tool {tool_name} executed with args: {tool_args}",
            "exit_code": 0,
            "execution_time": 1.5
        }
    
    def _get_model_display_name(self, model_id: str) -> str:
        """Получает отображаемое имя модели."""
        model_names = {
            "gpt-4": "GPT-4",
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "claude-3": "Claude 3",
            "deepseek/deepseek-chat": "DeepSeek Chat"
        }
        return model_names.get(model_id, model_id)
    
    def _is_valid_model_id(self, model_id: str) -> bool:
        """Проверяет валидность идентификатора модели."""
        valid_models = ["gpt-4", "gpt-3.5-turbo", "claude-3", "deepseek/deepseek-chat"]
        return model_id in valid_models
    
    def _check_tool_permissions(self, tool_name: str, user_id: str) -> bool:
        """Проверяет права пользователя на использование инструмента."""
        # В реальной реализации проверяем права пользователя
        return tool_name != "admin_tool"
    
    def _fetch_available_models(self, user_id: str) -> list:
        """Получает список доступных моделей для пользователя."""
        return [
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
            {"id": "claude-3", "name": "Claude 3", "provider": "anthropic"},
            {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat", "provider": "deepseek"}
        ]
    
    def _get_user_tier(self, user_id: str) -> str:
        """Получает уровень пользователя."""
        return "premium"  # В реальной реализации из базы данных
    
    def _check_database_health(self) -> bool:
        """Проверяет состояние базы данных."""
        return True
    
    def _check_llm_providers_health(self) -> bool:
        """Проверяет состояние LLM провайдеров."""
        return True
    
    def _check_memory_system_health(self) -> bool:
        """Проверяет состояние системы памяти."""
        return True
    
    def _check_tools_health(self) -> bool:
        """Проверяет состояние инструментов."""
        return True
    
    def _get_uptime(self) -> str:
        """Получает время работы системы."""
        return "2 days, 14 hours, 32 minutes"


# Исключения для демонстрации
class RateLimitException(Exception):
    def __init__(self, retry_after: int, current_usage: int, limit: int):
        self.retry_after = retry_after
        self.current_usage = current_usage
        self.limit = limit
        super().__init__(f"Rate limit exceeded: {current_usage}/{limit}")


class ModelUnavailableException(Exception):
    pass


class ContextWindowExceededException(Exception):
    pass


class ToolTimeoutException(Exception):
    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Tool execution timed out after {timeout} seconds")


class CommandNotAllowedException(Exception):
    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Command not allowed: {command}")


def demo_api_responses():
    """
    Демонстрация различных сценариев использования API ответов.
    """
    api = GopiAIAPIEndpoint()
    
    print("=== Демонстрация стандартизированных API ответов GopiAI ===\n")
    
    # 1. Успешный запрос чата
    print("1. Успешный запрос чата:")
    response = api.process_chat_request(
        message="Привет! Как дела?",
        model_id="gpt-4",
        user_id="user_123"
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 2. Ошибка валидации
    print("2. Ошибка валидации:")
    response = api.process_chat_request(
        message="",  # Пустое сообщение
        model_id="invalid_model",
        user_id=""
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 3. Rate limit ошибка
    print("3. Rate limit ошибка:")
    response = api.process_chat_request(
        message="This message will trigger rate limit",
        model_id="gpt-4",
        user_id="user_123"
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 4. Успешное выполнение инструмента
    print("4. Успешное выполнение инструмента:")
    response = api.execute_tool_request(
        tool_name="execute_command",
        tool_args={"command": "ls -la"},
        user_id="user_123"
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 5. Ошибка инструмента - таймаут
    print("5. Ошибка инструмента - таймаут:")
    response = api.execute_tool_request(
        tool_name="timeout_tool",
        tool_args={},
        user_id="user_123"
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 6. Список доступных моделей
    print("6. Список доступных моделей:")
    response = api.get_available_models(user_id="user_123")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")
    
    # 7. Health check
    print("7. Health check:")
    response = api.health_check()
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    demo_api_responses()