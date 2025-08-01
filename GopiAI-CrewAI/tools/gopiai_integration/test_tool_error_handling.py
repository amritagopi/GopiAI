"""
Тесты для системы обработки ошибок выполнения инструментов.
Проверяет требования 2.3, 2.5 из спецификации.
"""

import unittest
import logging
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import subprocess
import requests

# Настройка логирования для тестов
logging.basicConfig(level=logging.DEBUG)

# Импорты тестируемых модулей
try:
    from command_executor import CommandExecutor
    from error_handler import ErrorHandler, ErrorType
    from smart_delegator import SmartDelegator, process_tool_calls
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все модули находятся в правильных путях")


class TestToolErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок выполнения инструментов."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.command_executor = CommandExecutor()
        self.error_handler = ErrorHandler()
        
        # Создаём временную директорию для тестов
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Очистка после тестов."""
        # Удаляем временную директорию
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_terminal_command_empty_input(self):
        """Тест обработки пустой команды."""
        result = self.command_executor.execute_terminal_command("")
        
        self.assertIn("Ошибка", result)
        self.assertIn("пустая команда", result.lower())

    def test_terminal_command_unsafe_command(self):
        """Тест обработки небезопасной команды."""
        unsafe_command = "rm -rf /"
        result = self.command_executor.execute_terminal_command(unsafe_command)
        
        self.assertIn("безопасности", result.lower())
        self.assertIn("отклонена", result.lower())

    def test_terminal_command_timeout(self):
        """Тест обработки таймаута команды."""
        # Команда, которая должна превысить таймаут
        if os.name == "nt":  # Windows
            long_command = "timeout 5"  # 5 секунд
        else:  # Unix/Linux
            long_command = "sleep 5"  # 5 секунд
            
        result = self.command_executor.execute_terminal_command(
            long_command, 
            timeout=1  # Таймаут 1 секунда
        )
        
        self.assertIn("таймаут", result.lower())

    def test_terminal_command_nonexistent_command(self):
        """Тест обработки несуществующей команды."""
        result = self.command_executor.execute_terminal_command("nonexistent_command_12345")
        
        self.assertIn("ошибка", result.lower())

    def test_file_operations_empty_operation(self):
        """Тест обработки пустой операции с файлами."""
        result = self.command_executor.file_operations("", "/some/path")
        
        self.assertIn("не указана операция", result.lower())

    def test_file_operations_empty_path(self):
        """Тест обработки пустого пути."""
        result = self.command_executor.file_operations("read", "")
        
        self.assertIn("не указан путь", result.lower())

    def test_file_operations_unsafe_path(self):
        """Тест обработки небезопасного пути."""
        unsafe_path = "/etc/passwd"
        result = self.command_executor.file_operations("read", unsafe_path)
        
        self.assertIn("безопасности", result.lower())

    def test_file_operations_nonexistent_file(self):
        """Тест обработки несуществующего файла."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent_file.txt")
        result = self.command_executor.file_operations("read", nonexistent_path)
        
        self.assertIn("не найден", result.lower())

    def test_browse_website_empty_url(self):
        """Тест обработки пустого URL."""
        result = self.command_executor.browse_website("")
        
        self.assertIn("пустой url", result.lower())

    def test_browse_website_unsafe_url(self):
        """Тест обработки небезопасного URL."""
        unsafe_url = "http://localhost:8080/admin"
        result = self.command_executor.browse_website(unsafe_url)
        
        self.assertIn("безопасности", result.lower())

    @patch('requests.get')
    def test_browse_website_connection_error(self, mock_get):
        """Тест обработки ошибки подключения."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = self.command_executor.browse_website("https://example.com")
        
        self.assertIn("подключиться", result.lower())

    @patch('requests.get')
    def test_browse_website_timeout_error(self, mock_get):
        """Тест обработки таймаута веб-запроса."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = self.command_executor.browse_website("https://example.com")
        
        self.assertIn("время ожидания", result.lower())

    def test_web_search_empty_query(self):
        """Тест обработки пустого поискового запроса."""
        result = self.command_executor.web_search("")
        
        self.assertIn("пустой поисковый запрос", result.lower())

    @patch('requests.get')
    def test_web_search_connection_error(self, mock_get):
        """Тест обработки ошибки подключения при поиске."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = self.command_executor.web_search("test query")
        
        self.assertIn("подключиться", result.lower())

    def test_error_handler_tool_error(self):
        """Тест обработки ошибки инструмента."""
        test_error = ValueError("Test error message")
        result = self.error_handler.handle_tool_error(
            test_error, 
            "test_tool",
            {"param1": "value1"}
        )
        
        self.assertIn("test_tool", result)
        self.assertIn("Test error message", result)

    def test_error_handler_command_safety_error(self):
        """Тест обработки ошибки безопасности команды."""
        result = self.error_handler.handle_command_safety_error(
            "rm -rf /",
            "Опасная команда удаления"
        )
        
        self.assertIn("отклонена", result)
        self.assertIn("безопасности", result)
        self.assertIn("rm -rf /", result)

    def test_error_handler_file_operation_error(self):
        """Тест обработки ошибки файловой операции."""
        test_error = FileNotFoundError("File not found")
        result = self.error_handler.handle_file_operation_error(
            test_error,
            "read",
            "/nonexistent/file.txt"
        )
        
        self.assertIn("не найден", result.lower())

    def test_error_handler_network_error(self):
        """Тест обработки сетевой ошибки."""
        test_error = requests.exceptions.ConnectionError("Connection failed")
        result = self.error_handler.handle_network_error(
            test_error,
            "https://example.com",
            "browse"
        )
        
        self.assertIn("подключиться", result.lower())

    def test_error_handler_timeout_error(self):
        """Тест обработки ошибки таймаута."""
        result = self.error_handler.handle_timeout_error(
            "test operation",
            30
        )
        
        self.assertIn("превысила лимит времени", result.lower())
        self.assertIn("30", result)

    def test_error_statistics(self):
        """Тест получения статистики ошибок."""
        # Генерируем несколько ошибок
        self.error_handler.handle_tool_error(ValueError("Error 1"), "tool1")
        self.error_handler.handle_tool_error(TypeError("Error 2"), "tool2")
        self.error_handler.handle_command_safety_error("dangerous_cmd", "Unsafe")
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertGreater(stats["total_errors"], 0)
        self.assertIn("tool_errors", stats)
        self.assertIn("error_types", stats)

    @patch('GopiAI-CrewAI.tools.gopiai_integration.smart_delegator.CREWAI_TOOLKIT_AVAILABLE', False)
    def test_process_tool_calls_no_toolkit(self):
        """Тест обработки tool calls без доступного toolkit."""
        tool_calls = [
            {
                "id": "test_call_1",
                "function": {
                    "name": "read_file",
                    "arguments": '{"file_path": "/test/file.txt"}'
                }
            }
        ]
        
        results = process_tool_calls(tool_calls)
        
        # Должен вернуть пустой список, так как toolkit недоступен
        self.assertEqual(len(results), 0)

    def test_process_tool_calls_invalid_json(self):
        """Тест обработки tool calls с некорректным JSON."""
        tool_calls = [
            {
                "id": "test_call_1",
                "function": {
                    "name": "read_file",
                    "arguments": '{"file_path": "/test/file.txt"'  # Некорректный JSON
                }
            }
        ]
        
        with patch('GopiAI-CrewAI.tools.gopiai_integration.smart_delegator.CREWAI_TOOLKIT_AVAILABLE', True):
            results = process_tool_calls(tool_calls)
        
        self.assertEqual(len(results), 1)
        self.assertIn("ошибка парсинга", results[0]["content"].lower())

    def test_graceful_degradation(self):
        """Тест graceful degradation при недоступности зависимостей."""
        # Тестируем поведение при отсутствии requests
        with patch.dict('sys.modules', {'requests': None}):
            result = self.command_executor.browse_website("https://example.com")
            self.assertIn("библиотеки", result.lower())

    def test_structured_error_information(self):
        """Тест возврата структурированной информации об ошибках."""
        # Создаём mock SmartDelegator для тестирования
        delegator = SmartDelegator()
        delegator.local_tools_available = True
        
        # Mock _call_tool для возврата ошибки
        with patch.object(delegator, '_call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": False,
                "error": "Test tool error"
            }
            
            # Тестируем обработку запроса с инструментом
            metadata = {
                "tool": {
                    "name": "test_tool",
                    "server_name": "local",
                    "params": {}
                }
            }
            
            result = delegator.process_request("Test message", metadata)
            
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error_code"], "TOOL_EXECUTION_ERROR")
            self.assertIn("test_tool", result["tool_name"])
            self.assertTrue(result["retryable"])

    def test_error_logging_context(self):
        """Тест логирования ошибок с полным контекстом."""
        with self.assertLogs(level='WARNING') as log:
            self.error_handler.handle_tool_error(
                ValueError("Test error"),
                "test_tool",
                {"param1": "value1", "param2": "value2"}
            )
        
        # Проверяем, что ошибка была залогирована
        self.assertTrue(any("test_tool" in record.message for record in log.records))
        self.assertTrue(any("Test error" in record.message for record in log.records))


class TestToolErrorHandlingIntegration(unittest.TestCase):
    """Интеграционные тесты обработки ошибок инструментов."""

    def setUp(self):
        """Настройка интеграционных тестов."""
        self.delegator = SmartDelegator()

    def test_end_to_end_tool_error_handling(self):
        """Интеграционный тест обработки ошибок от начала до конца."""
        # Создаём запрос с инструментом, который должен завершиться ошибкой
        metadata = {
            "tool": {
                "name": "nonexistent_tool",
                "server_name": "local", 
                "params": {}
            }
        }
        
        # Обрабатываем запрос
        result = self.delegator.process_request("Test message", metadata)
        
        # Проверяем структуру ответа об ошибке
        self.assertIn("status", result)
        if result.get("status") == "error":
            self.assertIn("error", result)
            self.assertIn("error_code", result)

    def test_multiple_tool_errors_handling(self):
        """Тест обработки множественных ошибок инструментов."""
        tool_calls = [
            {
                "id": "call_1",
                "function": {
                    "name": "nonexistent_tool_1",
                    "arguments": "{}"
                }
            },
            {
                "id": "call_2", 
                "function": {
                    "name": "nonexistent_tool_2",
                    "arguments": "{}"
                }
            }
        ]
        
        with patch('GopiAI-CrewAI.tools.gopiai_integration.smart_delegator.CREWAI_TOOLKIT_AVAILABLE', True):
            results = process_tool_calls(tool_calls)
        
        # Все вызовы должны вернуть ошибки
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("ошибка", result["content"].lower())


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)