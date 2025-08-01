"""
Тесты для системы стандартизации API ответов.
Проверяет все аспекты APIResponseBuilder и связанных компонентов.
"""

import pytest
import json
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

from api_response_builder import (
    APIResponseBuilder,
    APIErrorCode,
    ResponseStatus,
    ModelInfo,
    ExecutionInfo,
    ErrorCodeMapper,
    create_success_response,
    create_error_response
)


class TestAPIErrorCode:
    """Тесты для enum кодов ошибок."""
    
    def test_error_codes_exist(self):
        """Проверяет, что все необходимые коды ошибок определены."""
        # LLM ошибки
        assert APIErrorCode.RATE_LIMIT_EXCEEDED.value == "RATE_LIMIT_EXCEEDED"
        assert APIErrorCode.AUTHENTICATION_ERROR.value == "AUTHENTICATION_ERROR"
        assert APIErrorCode.INVALID_REQUEST.value == "INVALID_REQUEST"
        assert APIErrorCode.CONTEXT_WINDOW_EXCEEDED.value == "CONTEXT_WINDOW_EXCEEDED"
        assert APIErrorCode.CONTENT_POLICY_VIOLATION.value == "CONTENT_POLICY_VIOLATION"
        assert APIErrorCode.MODEL_NOT_FOUND.value == "MODEL_NOT_FOUND"
        assert APIErrorCode.MODEL_UNAVAILABLE.value == "MODEL_UNAVAILABLE"
        assert APIErrorCode.EMPTY_RESPONSE.value == "EMPTY_RESPONSE"
        assert APIErrorCode.INVALID_RESPONSE.value == "INVALID_RESPONSE"
        
        # Tool ошибки
        assert APIErrorCode.TOOL_EXECUTION_ERROR.value == "TOOL_EXECUTION_ERROR"
        assert APIErrorCode.TOOL_NOT_FOUND.value == "TOOL_NOT_FOUND"
        assert APIErrorCode.TOOL_TIMEOUT.value == "TOOL_TIMEOUT"
        assert APIErrorCode.TOOL_PERMISSION_DENIED.value == "TOOL_PERMISSION_DENIED"
        assert APIErrorCode.COMMAND_NOT_ALLOWED.value == "COMMAND_NOT_ALLOWED"
        
        # Файловые ошибки
        assert APIErrorCode.FILE_NOT_FOUND.value == "FILE_NOT_FOUND"
        assert APIErrorCode.FILE_PERMISSION_DENIED.value == "FILE_PERMISSION_DENIED"
        assert APIErrorCode.FILE_TOO_LARGE.value == "FILE_TOO_LARGE"
        assert APIErrorCode.DIRECTORY_NOT_FOUND.value == "DIRECTORY_NOT_FOUND"
        assert APIErrorCode.INVALID_FILE_PATH.value == "INVALID_FILE_PATH"
        
        # Сетевые ошибки
        assert APIErrorCode.NETWORK_CONNECTION_ERROR.value == "NETWORK_CONNECTION_ERROR"
        assert APIErrorCode.NETWORK_TIMEOUT.value == "NETWORK_TIMEOUT"
        assert APIErrorCode.HTTP_ERROR.value == "HTTP_ERROR"
        assert APIErrorCode.DNS_RESOLUTION_ERROR.value == "DNS_RESOLUTION_ERROR"
        
        # Системные ошибки
        assert APIErrorCode.INTERNAL_SERVER_ERROR.value == "INTERNAL_SERVER_ERROR"
        assert APIErrorCode.SERVICE_UNAVAILABLE.value == "SERVICE_UNAVAILABLE"
        assert APIErrorCode.TIMEOUT_ERROR.value == "TIMEOUT_ERROR"
        assert APIErrorCode.MEMORY_ERROR.value == "MEMORY_ERROR"
        assert APIErrorCode.CONFIGURATION_ERROR.value == "CONFIGURATION_ERROR"
        
        # Валидационные ошибки
        assert APIErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert APIErrorCode.MISSING_REQUIRED_FIELD.value == "MISSING_REQUIRED_FIELD"
        assert APIErrorCode.INVALID_FIELD_VALUE.value == "INVALID_FIELD_VALUE"
        assert APIErrorCode.INVALID_JSON_FORMAT.value == "INVALID_JSON_FORMAT"
        
        # Общие ошибки
        assert APIErrorCode.UNKNOWN_ERROR.value == "UNKNOWN_ERROR"
        assert APIErrorCode.NOT_IMPLEMENTED.value == "NOT_IMPLEMENTED"
        assert APIErrorCode.DEPRECATED_ENDPOINT.value == "DEPRECATED_ENDPOINT"


class TestResponseStatus:
    """Тесты для enum статусов ответов."""
    
    def test_response_statuses_exist(self):
        """Проверяет, что все статусы ответов определены."""
        assert ResponseStatus.SUCCESS.value == "success"
        assert ResponseStatus.ERROR.value == "error"
        assert ResponseStatus.PARTIAL_SUCCESS.value == "partial_success"
        assert ResponseStatus.PROCESSING.value == "processing"


class TestModelInfo:
    """Тесты для класса ModelInfo."""
    
    def test_model_info_creation(self):
        """Тестирует создание ModelInfo."""
        model_info = ModelInfo(
            model_id="gpt-4",
            provider="openai",
            display_name="GPT-4",
            version="2024-01",
            capabilities=["text", "code"]
        )
        
        assert model_info.model_id == "gpt-4"
        assert model_info.provider == "openai"
        assert model_info.display_name == "GPT-4"
        assert model_info.version == "2024-01"
        assert model_info.capabilities == ["text", "code"]
    
    def test_model_info_to_dict(self):
        """Тестирует конвертацию ModelInfo в словарь."""
        model_info = ModelInfo(
            model_id="gpt-4",
            provider="openai",
            display_name="GPT-4"
        )
        
        result = model_info.to_dict()
        expected = {
            "model_id": "gpt-4",
            "provider": "openai",
            "display_name": "GPT-4"
        }
        
        assert result == expected
    
    def test_model_info_to_dict_excludes_none(self):
        """Тестирует, что to_dict исключает None значения."""
        model_info = ModelInfo(
            model_id="gpt-4",
            provider="openai"
        )
        
        result = model_info.to_dict()
        expected = {
            "model_id": "gpt-4",
            "provider": "openai"
        }
        
        assert result == expected
        assert "display_name" not in result
        assert "version" not in result
        assert "capabilities" not in result


class TestExecutionInfo:
    """Тесты для класса ExecutionInfo."""
    
    def test_execution_info_creation(self):
        """Тестирует создание ExecutionInfo."""
        execution_info = ExecutionInfo(
            execution_time=1.234,
            started_at="2024-01-01T10:00:00",
            completed_at="2024-01-01T10:00:01",
            request_id="req_123"
        )
        
        assert execution_info.execution_time == 1.234
        assert execution_info.started_at == "2024-01-01T10:00:00"
        assert execution_info.completed_at == "2024-01-01T10:00:01"
        assert execution_info.request_id == "req_123"
    
    def test_execution_info_to_dict(self):
        """Тестирует конвертацию ExecutionInfo в словарь."""
        execution_info = ExecutionInfo(
            execution_time=1.234,
            started_at="2024-01-01T10:00:00",
            completed_at="2024-01-01T10:00:01"
        )
        
        result = execution_info.to_dict()
        expected = {
            "execution_time": 1.234,
            "started_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:00:01"
        }
        
        assert result == expected


class TestAPIResponseBuilder:
    """Тесты для основного класса APIResponseBuilder."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.builder = APIResponseBuilder()
    
    def test_start_request(self):
        """Тестирует начало отслеживания запроса."""
        request_id = "test_request_123"
        result = self.builder.start_request(request_id)
        
        assert result is self.builder  # Проверяем цепочку вызовов
        assert self.builder._request_id == request_id
        assert self.builder._start_time is not None
    
    @patch('api_response_builder.datetime')
    def test_success_response_basic(self, mock_datetime):
        """Тестирует создание базового успешного ответа."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"result": "success"}
        response = self.builder.success_response(data)
        
        expected = {
            "status": "success",
            "data": {"result": "success"},
            "timestamp": "2024-01-01T10:00:00"
        }
        
        assert response == expected
    
    @patch('api_response_builder.datetime')
    def test_success_response_with_message(self, mock_datetime):
        """Тестирует успешный ответ с сообщением."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"result": "success"}
        message = "Operation completed successfully"
        response = self.builder.success_response(data, message=message)
        
        assert response["message"] == message
    
    @patch('api_response_builder.datetime')
    @patch('api_response_builder.time')
    def test_success_response_with_execution_info(self, mock_time, mock_datetime):
        """Тестирует успешный ответ с информацией о выполнении."""
        # Настройка моков
        mock_time.time.side_effect = [1000.0, 1001.234]  # start_time, current_time
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:01"
        
        # Начинаем отслеживание
        self.builder.start_request("req_123")
        
        data = {"result": "success"}
        response = self.builder.success_response(data)
        
        assert "execution" in response
        execution = response["execution"]
        assert execution["execution_time"] == 1.234
        assert execution["request_id"] == "req_123"
    
    @patch('api_response_builder.datetime')
    def test_success_response_with_model_info(self, mock_datetime):
        """Тестирует успешный ответ с информацией о модели."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"result": "success"}
        model_info = ModelInfo(model_id="gpt-4", provider="openai")
        response = self.builder.success_response(data, model_info=model_info)
        
        assert "model_info" in response
        assert response["model_info"]["model_id"] == "gpt-4"
        assert response["model_info"]["provider"] == "openai"
    
    @patch('api_response_builder.datetime')
    def test_success_response_with_model_info_dict(self, mock_datetime):
        """Тестирует успешный ответ с информацией о модели в виде словаря."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"result": "success"}
        model_info = {"model_id": "gpt-4", "provider": "openai"}
        response = self.builder.success_response(data, model_info=model_info)
        
        assert "model_info" in response
        assert response["model_info"] == model_info
    
    @patch('api_response_builder.datetime')
    def test_success_response_with_metadata(self, mock_datetime):
        """Тестирует успешный ответ с метаданными."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"result": "success"}
        metadata = {"user_id": "user_123", "session_id": "session_456"}
        response = self.builder.success_response(data, metadata=metadata)
        
        assert "metadata" in response
        assert response["metadata"] == metadata
    
    @patch('api_response_builder.datetime')
    def test_error_response_basic(self, mock_datetime):
        """Тестирует создание базового ответа об ошибке."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.error_response(
            error_code=APIErrorCode.VALIDATION_ERROR,
            message="Invalid input data"
        )
        
        expected = {
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "retryable": False
            },
            "timestamp": "2024-01-01T10:00:00"
        }
        
        assert response == expected
    
    @patch('api_response_builder.datetime')
    def test_error_response_with_retry_after(self, mock_datetime):
        """Тестирует ответ об ошибке с retry_after."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.error_response(
            error_code=APIErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            retry_after=60,
            retryable=True
        )
        
        assert response["error"]["retry_after"] == 60
        assert response["error"]["retryable"] is True
    
    @patch('api_response_builder.datetime')
    def test_error_response_with_details(self, mock_datetime):
        """Тестирует ответ об ошибке с деталями."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        details = {"field": "email", "reason": "invalid format"}
        response = self.builder.error_response(
            error_code=APIErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            details=details
        )
        
        assert response["error"]["details"] == details
    
    @patch('api_response_builder.datetime')
    def test_error_response_with_suggestions(self, mock_datetime):
        """Тестирует ответ об ошибке с предложениями."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        suggestions = ["Check your input", "Try again later"]
        response = self.builder.error_response(
            error_code=APIErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            suggestions=suggestions
        )
        
        assert response["error"]["suggestions"] == suggestions
    
    @patch('api_response_builder.datetime')
    def test_error_response_with_string_error_code(self, mock_datetime):
        """Тестирует ответ об ошибке со строковым кодом."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.error_response(
            error_code="CUSTOM_ERROR",
            message="Custom error occurred"
        )
        
        assert response["error"]["code"] == "CUSTOM_ERROR"
    
    @patch('api_response_builder.datetime')
    def test_partial_success_response(self, mock_datetime):
        """Тестирует ответ о частичном успехе."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        data = {"processed": 5}
        errors = [{"item": 1, "error": "validation failed"}]
        response = self.builder.partial_success_response(data, errors)
        
        expected = {
            "status": "partial_success",
            "data": {"processed": 5},
            "errors": [{"item": 1, "error": "validation failed"}],
            "timestamp": "2024-01-01T10:00:00"
        }
        
        assert response == expected
    
    @patch('api_response_builder.datetime')
    def test_processing_response(self, mock_datetime):
        """Тестирует ответ о обработке."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.processing_response(
            task_id="task_123",
            message="Processing your request",
            estimated_completion="2024-01-01T10:05:00"
        )
        
        expected = {
            "status": "processing",
            "task_id": "task_123",
            "message": "Processing your request",
            "estimated_completion": "2024-01-01T10:05:00",
            "timestamp": "2024-01-01T10:00:00"
        }
        
        assert response == expected
    
    @patch('api_response_builder.datetime')
    def test_validation_error_response(self, mock_datetime):
        """Тестирует ответ об ошибке валидации."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        field_errors = {"email": "Invalid format", "age": "Must be positive"}
        response = self.builder.validation_error_response(field_errors)
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["details"]["field_errors"] == field_errors
        assert response["error"]["retryable"] is True
        assert len(response["error"]["suggestions"]) > 0
    
    @patch('api_response_builder.datetime')
    def test_rate_limit_error_response(self, mock_datetime):
        """Тестирует ответ об ошибке превышения лимита."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.rate_limit_error_response(
            retry_after=60,
            limit_type="requests",
            current_usage=100,
            limit=100
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert response["error"]["retry_after"] == 60
        assert response["error"]["retryable"] is True
        assert response["error"]["details"]["limit_type"] == "requests"
        assert response["error"]["details"]["current_usage"] == 100
        assert response["error"]["details"]["limit"] == 100
        assert len(response["error"]["suggestions"]) > 0
    
    @patch('api_response_builder.datetime')
    def test_tool_error_response(self, mock_datetime):
        """Тестирует ответ об ошибке инструмента."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.tool_error_response(
            tool_name="execute_command",
            error_message="Command not found"
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "TOOL_EXECUTION_ERROR"
        assert "execute_command" in response["error"]["message"]
        assert response["error"]["details"]["tool_name"] == "execute_command"
        assert response["error"]["details"]["original_error"] == "Command not found"
        assert response["error"]["retryable"] is True
        assert len(response["error"]["suggestions"]) > 0
    
    @patch('api_response_builder.datetime')
    def test_model_error_response_context_window(self, mock_datetime):
        """Тестирует ответ об ошибке модели - превышение контекстного окна."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.model_error_response(
            model_id="gpt-4",
            error_message="Context window exceeded",
            error_code=APIErrorCode.CONTEXT_WINDOW_EXCEEDED
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "CONTEXT_WINDOW_EXCEEDED"
        assert "gpt-4" in response["error"]["message"]
        assert response["error"]["details"]["model_id"] == "gpt-4"
        assert any("Сократите размер" in suggestion for suggestion in response["error"]["suggestions"])
    
    @patch('api_response_builder.datetime')
    def test_model_error_response_content_policy(self, mock_datetime):
        """Тестирует ответ об ошибке модели - нарушение политики контента."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.model_error_response(
            model_id="gpt-4",
            error_message="Content policy violation",
            error_code=APIErrorCode.CONTENT_POLICY_VIOLATION
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "CONTENT_POLICY_VIOLATION"
        assert any("Измените формулировку" in suggestion for suggestion in response["error"]["suggestions"])
    
    @patch('api_response_builder.datetime')
    def test_model_error_response_unavailable(self, mock_datetime):
        """Тестирует ответ об ошибке модели - недоступность."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.model_error_response(
            model_id="gpt-4",
            error_message="Model unavailable",
            error_code=APIErrorCode.MODEL_UNAVAILABLE
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "MODEL_UNAVAILABLE"
        assert any("другую модель" in suggestion for suggestion in response["error"]["suggestions"])


class TestErrorCodeMapper:
    """Тесты для класса ErrorCodeMapper."""
    
    def test_map_exception_file_not_found(self):
        """Тестирует сопоставление FileNotFoundError."""
        exception = FileNotFoundError("File not found")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.FILE_NOT_FOUND
    
    def test_map_exception_permission_error(self):
        """Тестирует сопоставление PermissionError."""
        exception = PermissionError("Permission denied")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.FILE_PERMISSION_DENIED
    
    def test_map_exception_connection_error(self):
        """Тестирует сопоставление ConnectionError."""
        exception = ConnectionError("Connection failed")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.NETWORK_CONNECTION_ERROR
    
    def test_map_exception_timeout_error(self):
        """Тестирует сопоставление TimeoutError."""
        exception = TimeoutError("Request timed out")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.NETWORK_TIMEOUT
    
    def test_map_exception_value_error(self):
        """Тестирует сопоставление ValueError."""
        exception = ValueError("Invalid value")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.VALIDATION_ERROR
    
    def test_map_exception_key_error(self):
        """Тестирует сопоставление KeyError."""
        exception = KeyError("Missing key")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.MISSING_REQUIRED_FIELD
    
    def test_map_exception_json_decode_error(self):
        """Тестирует сопоставление JSONDecodeError."""
        exception = json.JSONDecodeError("Invalid JSON", "", 0)
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.INVALID_JSON_FORMAT
    
    def test_map_exception_unknown(self):
        """Тестирует сопоставление неизвестного исключения."""
        exception = RuntimeError("Unknown error")
        result = ErrorCodeMapper.map_exception(exception)
        assert result == APIErrorCode.UNKNOWN_ERROR
    
    def test_map_llm_error_rate_limit(self):
        """Тестирует сопоставление ошибки rate limit."""
        result = ErrorCodeMapper.map_llm_error("rate_limit")
        assert result == APIErrorCode.RATE_LIMIT_EXCEEDED
    
    def test_map_llm_error_authentication(self):
        """Тестирует сопоставление ошибки аутентификации."""
        result = ErrorCodeMapper.map_llm_error("authentication")
        assert result == APIErrorCode.AUTHENTICATION_ERROR
    
    def test_map_llm_error_context_window(self):
        """Тестирует сопоставление ошибки контекстного окна."""
        result = ErrorCodeMapper.map_llm_error("context_window")
        assert result == APIErrorCode.CONTEXT_WINDOW_EXCEEDED
    
    def test_map_llm_error_unknown(self):
        """Тестирует сопоставление неизвестной LLM ошибки."""
        result = ErrorCodeMapper.map_llm_error("unknown_error")
        assert result == APIErrorCode.UNKNOWN_ERROR


class TestConvenienceFunctions:
    """Тесты для удобных функций."""
    
    @patch('api_response_builder.api_response_builder')
    def test_create_success_response(self, mock_builder):
        """Тестирует функцию create_success_response."""
        mock_builder.success_response.return_value = {"status": "success"}
        
        data = {"result": "test"}
        message = "Test message"
        model_info = {"model_id": "gpt-4"}
        metadata = {"user_id": "123"}
        
        result = create_success_response(data, message, model_info, metadata)
        
        mock_builder.success_response.assert_called_once_with(data, message, model_info, metadata)
        assert result == {"status": "success"}
    
    @patch('api_response_builder.api_response_builder')
    def test_create_error_response(self, mock_builder):
        """Тестирует функцию create_error_response."""
        mock_builder.error_response.return_value = {"status": "error"}
        
        error_code = APIErrorCode.VALIDATION_ERROR
        message = "Test error"
        details = {"field": "email"}
        retry_after = 60
        retryable = True
        suggestions = ["Fix the error"]
        
        result = create_error_response(error_code, message, details, retry_after, retryable, suggestions)
        
        mock_builder.error_response.assert_called_once_with(
            error_code, message, details, retry_after, retryable, suggestions
        )
        assert result == {"status": "error"}


class TestIntegrationScenarios:
    """Интеграционные тесты для реальных сценариев использования."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.builder = APIResponseBuilder()
    
    @patch('api_response_builder.datetime')
    @patch('api_response_builder.time')
    def test_complete_request_lifecycle(self, mock_time, mock_datetime):
        """Тестирует полный жизненный цикл запроса."""
        # Настройка моков
        mock_time.time.side_effect = [1000.0, 1002.5]
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:02"
        
        # Начинаем запрос
        self.builder.start_request("req_123")
        
        # Создаём успешный ответ
        model_info = ModelInfo(model_id="gpt-4", provider="openai")
        data = {"response": "Hello, world!", "tokens_used": 50}
        metadata = {"user_id": "user_123", "session_id": "session_456"}
        
        response = self.builder.success_response(
            data=data,
            message="Request processed successfully",
            model_info=model_info,
            metadata=metadata
        )
        
        # Проверяем структуру ответа
        assert response["status"] == "success"
        assert response["data"] == data
        assert response["message"] == "Request processed successfully"
        assert response["model_info"]["model_id"] == "gpt-4"
        assert response["model_info"]["provider"] == "openai"
        assert response["metadata"] == metadata
        assert response["execution"]["execution_time"] == 2.5
        assert response["execution"]["request_id"] == "req_123"
        assert response["timestamp"] == "2024-01-01T10:00:02"
    
    @patch('api_response_builder.datetime')
    def test_rate_limit_scenario(self, mock_datetime):
        """Тестирует сценарий превышения лимита запросов."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.rate_limit_error_response(
            retry_after=120,
            limit_type="tokens",
            current_usage=10000,
            limit=10000
        )
        
        # Проверяем, что ответ содержит всю необходимую информацию
        assert response["status"] == "error"
        assert response["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert response["error"]["retry_after"] == 120
        assert response["error"]["retryable"] is True
        assert "120 seconds" in response["error"]["message"]
        assert response["error"]["details"]["limit_type"] == "tokens"
        assert response["error"]["details"]["current_usage"] == 10000
        assert response["error"]["details"]["limit"] == 10000
        assert len(response["error"]["suggestions"]) >= 3
    
    @patch('api_response_builder.datetime')
    def test_tool_execution_failure_scenario(self, mock_datetime):
        """Тестирует сценарий ошибки выполнения инструмента."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        response = self.builder.tool_error_response(
            tool_name="execute_terminal_command",
            error_message="Command 'rm -rf /' not allowed",
            error_code=APIErrorCode.COMMAND_NOT_ALLOWED,
            retryable=False
        )
        
        # Проверяем специфичную обработку ошибки команды
        assert response["status"] == "error"
        assert response["error"]["code"] == "COMMAND_NOT_ALLOWED"
        assert response["error"]["retryable"] is False
        assert "execute_terminal_command" in response["error"]["message"]
        assert response["error"]["details"]["tool_name"] == "execute_terminal_command"
        assert response["error"]["details"]["original_error"] == "Command 'rm -rf /' not allowed"
    
    @patch('api_response_builder.datetime')
    def test_validation_error_scenario(self, mock_datetime):
        """Тестирует сценарий ошибки валидации."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T10:00:00"
        
        field_errors = {
            "email": "Неверный формат email адреса",
            "password": "Пароль должен содержать минимум 8 символов",
            "age": "Возраст должен быть положительным числом"
        }
        
        response = self.builder.validation_error_response(
            field_errors=field_errors,
            message="Ошибка валидации входных данных"
        )
        
        # Проверяем детальную информацию об ошибках валидации
        assert response["status"] == "error"
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["message"] == "Ошибка валидации входных данных"
        assert response["error"]["retryable"] is True
        assert response["error"]["details"]["field_errors"] == field_errors
        assert len(response["error"]["suggestions"]) >= 2
    
    def test_json_serialization(self):
        """Тестирует, что все ответы можно сериализовать в JSON."""
        # Тестируем различные типы ответов
        responses = [
            self.builder.success_response({"test": "data"}),
            self.builder.error_response(APIErrorCode.VALIDATION_ERROR, "Test error"),
            self.builder.partial_success_response({"success": 1}, [{"error": "test"}]),
            self.builder.processing_response("task_123"),
            self.builder.validation_error_response({"field": "error"}),
            self.builder.rate_limit_error_response(60),
            self.builder.tool_error_response("test_tool", "error"),
            self.builder.model_error_response("gpt-4", "error", APIErrorCode.MODEL_UNAVAILABLE)
        ]
        
        # Проверяем, что все ответы можно сериализовать
        for response in responses:
            try:
                json_str = json.dumps(response, ensure_ascii=False, indent=2)
                # Проверяем, что можно десериализовать обратно
                parsed = json.loads(json_str)
                assert isinstance(parsed, dict)
                assert "status" in parsed
                assert "timestamp" in parsed
            except (TypeError, ValueError) as e:
                pytest.fail(f"Failed to serialize response: {response}. Error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])