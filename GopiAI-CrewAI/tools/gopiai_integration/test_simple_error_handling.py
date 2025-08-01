"""
Простые тесты для проверки обработки ошибок инструментов.
"""

import unittest
import tempfile
import os

# Импорты тестируемых модулей
from command_executor import CommandExecutor
from error_handler import ErrorHandler


class TestSimpleErrorHandling(unittest.TestCase):
    """Простые тесты обработки ошибок."""

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
        
        self.assertIn("ошибка", result.lower())
        print(f"✅ Тест пустой команды: {result[:100]}...")

    def test_terminal_command_unsafe_command(self):
        """Тест обработки небезопасной команды."""
        unsafe_command = "rm -rf /"
        result = self.command_executor.execute_terminal_command(unsafe_command)
        
        self.assertIn("безопасности", result.lower())
        print(f"✅ Тест небезопасной команды: {result[:100]}...")

    def test_file_operations_empty_operation(self):
        """Тест обработки пустой операции с файлами."""
        result = self.command_executor.file_operations("", "/some/path")
        
        self.assertIn("не указана операция", result.lower())
        print(f"✅ Тест пустой операции: {result[:100]}...")

    def test_file_operations_empty_path(self):
        """Тест обработки пустого пути."""
        result = self.command_executor.file_operations("read", "")
        
        self.assertIn("не указан путь", result.lower())
        print(f"✅ Тест пустого пути: {result[:100]}...")

    def test_browse_website_empty_url(self):
        """Тест обработки пустого URL."""
        result = self.command_executor.browse_website("")
        
        self.assertIn("пустой url", result.lower())
        print(f"✅ Тест пустого URL: {result[:100]}...")

    def test_web_search_empty_query(self):
        """Тест обработки пустого поискового запроса."""
        result = self.command_executor.web_search("")
        
        self.assertIn("пустой поисковый запрос", result.lower())
        print(f"✅ Тест пустого поискового запроса: {result[:100]}...")

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
        print(f"✅ Тест обработки ошибки инструмента: {result[:100]}...")

    def test_error_handler_command_safety_error(self):
        """Тест обработки ошибки безопасности команды."""
        result = self.error_handler.handle_command_safety_error(
            "rm -rf /",
            "Опасная команда удаления"
        )
        
        self.assertIn("отклонена", result)
        self.assertIn("безопасности", result)
        self.assertIn("rm -rf /", result)
        print(f"✅ Тест ошибки безопасности: {result[:100]}...")

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
        print(f"✅ Тест статистики ошибок: {stats['total_errors']} ошибок")

    def test_graceful_degradation_basic(self):
        """Базовый тест graceful degradation."""
        # Тестируем обработку несуществующего файла
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent_file.txt")
        result = self.command_executor.file_operations("read", nonexistent_path)
        
        # Должна быть обработана ошибка, а не исключение
        self.assertIsInstance(result, str)
        self.assertIn("ошибка", result.lower())
        print(f"✅ Тест graceful degradation: {result[:100]}...")

    def test_structured_error_information(self):
        """Тест возврата структурированной информации об ошибках."""
        # Тестируем, что ошибки возвращают строки, а не исключения
        result1 = self.command_executor.execute_terminal_command("")
        result2 = self.command_executor.file_operations("", "")
        result3 = self.command_executor.browse_website("")
        result4 = self.command_executor.web_search("")
        
        # Все результаты должны быть строками с описанием ошибок
        for i, result in enumerate([result1, result2, result3, result4], 1):
            self.assertIsInstance(result, str)
            self.assertIn("ошибка", result.lower())
            print(f"✅ Тест структурированной ошибки {i}: {result[:50]}...")


if __name__ == '__main__':
    print("🧪 Запуск простых тестов обработки ошибок инструментов...")
    print("=" * 60)
    
    # Запуск тестов
    unittest.main(verbosity=2)