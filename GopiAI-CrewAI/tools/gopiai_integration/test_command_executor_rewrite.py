"""
Тесты для переписанного CommandExecutor с прямым интерфейсом методов.
Проверяет соответствие требованиям задачи 4.
"""

import unittest
import os
import tempfile
import shutil
import logging
from unittest.mock import patch, MagicMock
from command_executor import CommandExecutor


class TestCommandExecutorRewrite(unittest.TestCase):
    """Тесты для переписанного CommandExecutor"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.executor = CommandExecutor()
        self.test_dir = tempfile.mkdtemp()
        
        # Настройка логирования для тестов
        logging.basicConfig(level=logging.INFO)

    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_direct_method_interface(self):
        """Тест 1: Проверка прямого интерфейса методов (без текстового парсинга)"""
        # Проверяем, что методы вызываются напрямую
        self.assertTrue(hasattr(self.executor, 'execute_terminal_command'))
        self.assertTrue(hasattr(self.executor, 'browse_website'))
        self.assertTrue(hasattr(self.executor, 'web_search'))
        self.assertTrue(hasattr(self.executor, 'file_operations'))
        
        # Проверяем, что методы принимают параметры напрямую
        result = self.executor.execute_terminal_command("echo test")
        self.assertIsInstance(result, str)
        self.assertNotIn("[PARSER]", result)  # Убеждаемся, что нет текстового парсинга

    def test_command_safety_validation(self):
        """Тест 2: Проверка валидации безопасности команд с белым списком"""
        # Тест разрешённой команды
        result = self.executor.execute_terminal_command("echo hello")
        self.assertNotIn("не разрешена", result)
        
        # Тест запрещённой команды
        result = self.executor.execute_terminal_command("malicious_command")
        self.assertIn("не входит в белый список", result)
        
        # Тест опасной команды с подозрительными паттернами
        result = self.executor.execute_terminal_command("ls && rm -rf /")
        self.assertIn("подозрительный паттерн", result)

    def test_timeout_handling(self):
        """Тест 3: Проверка обработки таймаута (30 секунд по умолчанию)"""
        # Тест с коротким таймаутом для быстрого выполнения
        if os.name == "nt":  # Windows
            # В Windows используем ping с задержкой
            result = self.executor.execute_terminal_command("ping -n 3 127.0.0.1", timeout=1)
        else:  # Unix/Linux
            result = self.executor.execute_terminal_command("sleep 2", timeout=1)
        
        self.assertIn("превысила лимит времени", result)

    def test_error_handling_and_logging(self):
        """Тест 4: Проверка обработки ошибок и логирования"""
        # Тест с несуществующей командой
        result = self.executor.execute_terminal_command("nonexistent_command_12345")
        self.assertIn("Ошибка", result)
        
        # Тест с пустой командой
        result = self.executor.execute_terminal_command("")
        self.assertIn("пустая команда", result)
        
        # Тест файловой операции с несуществующим файлом
        result = self.executor.file_operations("read", "/nonexistent/file.txt")
        self.assertIn("не существует", result)

    def test_working_directory_support(self):
        """Тест 5: Проверка поддержки рабочих директорий"""
        # Создаём тестовую директорию
        test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(test_subdir, exist_ok=True)
        
        # Выполняем команду в указанной рабочей директории
        if os.name == "nt":  # Windows
            result = self.executor.execute_terminal_command("cd", working_directory=test_subdir)
        else:  # Unix/Linux
            result = self.executor.execute_terminal_command("pwd", working_directory=test_subdir)
        
        self.assertIsInstance(result, str)
        self.assertNotIn("Ошибка", result)

    def test_file_operations_direct_methods(self):
        """Тест 6: Проверка прямых методов файловых операций"""
        test_file = os.path.join(self.test_dir, "test.txt")
        test_content = "Тестовое содержимое"
        
        # Тест записи файла
        result = self.executor.file_operations("write", test_file, test_content)
        self.assertIn("успешно записан", result)
        self.assertTrue(os.path.exists(test_file))
        
        # Тест чтения файла
        result = self.executor.file_operations("read", test_file)
        self.assertIn(test_content, result)
        
        # Тест проверки существования
        result = self.executor.file_operations("exists", test_file)
        self.assertIn("существует", result)
        
        # Тест получения информации о файле
        result = self.executor.file_operations("info", test_file)
        self.assertIn("файл", result)

    def test_web_browsing_direct_method(self):
        """Тест 7: Проверка прямого метода веб-браузинга"""
        # Мокаем requests для тестирования без реального интернета
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"<html><body>Test content</body></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.executor.browse_website("https://example.com")
            self.assertIn("Содержимое страницы", result)

    def test_web_search_direct_method(self):
        """Тест 8: Проверка прямого метода веб-поиска"""
        # Мокаем requests для тестирования без реального интернета
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b'<div class="result"><a class="result__a">Test Result</a><a class="result__snippet">Test snippet</a></div>'
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.executor.web_search("test query", 1)
            self.assertIn("Результаты поиска", result)

    def test_security_validation(self):
        """Тест 9: Проверка валидации безопасности"""
        # Тест безопасности команд
        safety_result = self.executor._validate_command_safety("echo hello")
        self.assertTrue(safety_result["safe"])
        
        safety_result = self.executor._validate_command_safety("rm -rf /")
        self.assertFalse(safety_result["safe"])
        
        # Тест безопасности путей
        self.assertTrue(self.executor._validate_path_safety("./test.txt"))
        self.assertFalse(self.executor._validate_path_safety("../../../etc/passwd"))
        
        # Тест безопасности URL
        self.assertTrue(self.executor._validate_url_safety("https://example.com"))
        self.assertFalse(self.executor._validate_url_safety("http://localhost:8080"))

    def test_output_size_limits(self):
        """Тест 10: Проверка ограничений размера вывода"""
        # Создаём большой файл для тестирования
        large_content = "A" * 10000  # 10000 символов
        test_file = os.path.join(self.test_dir, "large_test.txt")
        
        with open(test_file, 'w') as f:
            f.write(large_content)
        
        # Проверяем, что вывод ограничен
        result = self.executor.file_operations("read", test_file)
        self.assertIn("обрезан", result)

    def test_requirements_compliance(self):
        """Тест 11: Проверка соответствия требованиям задачи 4"""
        # Requirement 1.3: Replace text parsing with direct method calls
        self.assertTrue(callable(getattr(self.executor, 'execute_terminal_command', None)))
        self.assertTrue(callable(getattr(self.executor, 'browse_website', None)))
        self.assertTrue(callable(getattr(self.executor, 'web_search', None)))
        self.assertTrue(callable(getattr(self.executor, 'file_operations', None)))
        
        # Requirement 5.1: Command safety validation with whitelist
        self.assertIsInstance(self.executor.allowed_commands, set)
        self.assertIn("ls", self.executor.allowed_commands)
        self.assertIn("echo", self.executor.allowed_commands)
        
        # Requirement 5.2: Reject dangerous commands
        result = self.executor.execute_terminal_command("dangerous_command")
        self.assertIn("не входит в белый список", result)
        
        # Requirement 5.3: Timeout handling (30 second limit)
        # Проверяем, что таймаут по умолчанию 30 секунд
        self.assertEqual(self.executor.execute_terminal_command.__defaults__[1], 30)
        
        # Requirement 5.4: Proper error handling and logging
        result = self.executor.execute_terminal_command("nonexistent_command")
        self.assertIn("Ошибка", result)

    def test_backward_compatibility(self):
        """Тест 12: Проверка обратной совместимости с существующим API"""
        # Проверяем, что старые методы всё ещё работают
        result = self.executor.execute_terminal_command("echo test")
        self.assertIsInstance(result, str)
        
        # Проверяем, что новые параметры работают
        result = self.executor.execute_terminal_command(
            "echo test", 
            working_directory=self.test_dir, 
            timeout=10
        )
        self.assertIsInstance(result, str)


def run_comprehensive_tests():
    """Запуск всех тестов с подробным выводом"""
    print("=== Запуск тестов переписанного CommandExecutor ===")
    
    # Создание тестового набора
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCommandExecutorRewrite)
    
    # Запуск тестов с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод результатов
    print(f"\n=== Результаты тестирования ===")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Неудачных: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.failures:
        print("\nНеудачные тесты:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nОшибки в тестах:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)