"""
Тесты для проверки интеграции системы анализа ошибок с ReasoningAgent
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import os

from app.agent.reasoning import ReasoningAgent
from app.agent.error_analysis_system import ErrorSource, ErrorSeverity
from app.config.reasoning_config import ReasoningStrategy


class TestReasoningErrorIntegration(unittest.TestCase):
    """
    Тесты для проверки интеграции системы анализа ошибок с ReasoningAgent
    """

    @classmethod
    def setUpClass(cls):
        """
        Настраивает тестовое окружение перед выполнением тестов
        """
        # Создаем временную директорию для хранения данных
        cls.test_dir = tempfile.mkdtemp()

        # Настраиваем патчи для MCP клиентов
        cls.mcp_patcher = patch('app.agent.mcp.MCPClient')
        cls.mcp_mock = cls.mcp_patcher.start()

        # Настраиваем патч для вызова initialize
        cls.initialize_patcher = patch.object(ReasoningAgent, 'initialize')
        cls.initialize_mock = cls.initialize_patcher.start()
        cls.initialize_mock.return_value = asyncio.Future()
        cls.initialize_mock.return_value.set_result(None)

        # Настраиваем патч для проверки инструментов
        cls.check_tools_patcher = patch.object(ReasoningAgent, '_check_required_tools', return_value=[])
        cls.check_tools_mock = cls.check_tools_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Очищает тестовое окружение после выполнения тестов
        """
        # Останавливаем патчи
        cls.mcp_patcher.stop()
        cls.initialize_patcher.stop()
        cls.check_tools_patcher.stop()

        # Удаляем временную директорию
        shutil.rmtree(cls.test_dir)

    async def asyncSetUp(self):
        """
        Настраивает тест перед каждым тестовым методом
        """
        # Создаем экземпляр агента
        self.agent = ReasoningAgent()

        # Мокаем необходимые компоненты
        self.agent.error_manager = MagicMock()
        self.agent.error_manager.log_error.return_value = "test_error_id"
        self.agent.error_manager.log_exception.return_value = "test_exception_id"
        self.agent.error_manager.get_error_statistics.return_value = {
            "total_errors": 5,
            "by_category": {"test": 3, "other": 2},
            "by_severity": {"high": 2, "medium": 3},
            "by_source": {"execution": 3, "planning": 2},
            "resolution_rate": 0.6
        }

        # Устанавливаем корневую директорию для тестов
        os.environ["GOPI_ROOT_DIR"] = self.test_dir

    def asyncTearDown(self):
        """
        Очищает тест после каждого тестового метода
        """
        # Очищаем переменную окружения
        if "GOPI_ROOT_DIR" in os.environ:
            del os.environ["GOPI_ROOT_DIR"]

    def run_async_test(self, coro):
        """
        Запускает асинхронный тест
        """
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_error_manager_initialization(self):
        """
        Тест инициализации менеджера ошибок
        """
        # Создаем агента напрямую (без патчей)
        agent = ReasoningAgent()

        # Проверяем, что менеджер ошибок изначально не инициализирован
        self.assertIsNone(agent.error_manager)

    def test_log_error(self):
        """
        Тест метода _log_error для логирования ошибок
        """
        # Запускаем тест
        self.run_async_test(self._test_log_error())

    async def _test_log_error(self):
        """
        Асинхронная часть теста логирования ошибок
        """
        # Логируем тестовую ошибку
        error_id = self.agent._log_error(
            message="Test error message",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.HIGH,
            context={"test_key": "test_value"}
        )

        # Проверяем результат
        self.assertEqual(error_id, "test_error_id")

        # Проверяем, что метод log_error был вызван с правильными аргументами
        self.agent.error_manager.log_error.assert_called_once_with(
            message="Test error message",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.HIGH,
            task_id=None,
            context={"test_key": "test_value"}
        )

    def test_process_tool_call_with_error(self):
        """
        Тест обработки ошибок при вызове инструментов
        """
        # Запускаем тест
        self.run_async_test(self._test_process_tool_call_with_error())

    async def _test_process_tool_call_with_error(self):
        """
        Асинхронная часть теста обработки ошибок при вызове инструментов
        """
        # Мокаем метод process_tool_call базового класса, чтобы он вызывал ошибку
        with patch('app.agent.mcp.MCPAgent.process_tool_call') as mock_process:
            mock_process.side_effect = ValueError("Test tool error")

            # Вызываем инструмент, который вызовет ошибку
            result = await self.agent.process_tool_call("test_tool", arg1="value1")

            # Проверяем результат
            self.assertIn("error", result)
            self.assertIn("Test tool error", result["error"])
            self.assertIn("Error ID:", result["error"])

            # Проверяем, что ошибка была залогирована
            self.agent.error_manager.log_error.assert_called_once()

    def test_get_error_statistics(self):
        """
        Тест получения статистики ошибок
        """
        # Запускаем тест
        self.run_async_test(self._test_get_error_statistics())

    async def _test_get_error_statistics(self):
        """
        Асинхронная часть теста получения статистики ошибок
        """
        # Получаем статистику ошибок
        stats = self.agent.get_error_statistics(time_period=30, source=ErrorSource.EXECUTION)

        # Проверяем результат
        self.assertEqual(stats["total_errors"], 5)
        self.assertEqual(len(stats["by_category"]), 2)
        self.assertEqual(stats["resolution_rate"], 0.6)

        # Проверяем, что метод get_error_statistics был вызван с правильными аргументами
        self.agent.error_manager.get_error_statistics.assert_called_once_with(
            time_period=30,
            source=ErrorSource.EXECUTION
        )

    def test_detect_error_patterns(self):
        """
        Тест выявления паттернов ошибок
        """
        # Запускаем тест
        self.run_async_test(self._test_detect_error_patterns())

    async def _test_detect_error_patterns(self):
        """
        Асинхронная часть теста выявления паттернов ошибок
        """
        # Настраиваем мок для метода detect_error_patterns
        self.agent.error_manager.detect_error_patterns.return_value = [
            {
                "type": "category_frequency",
                "category": "test",
                "count": 3,
                "description": "Frequent occurrence of 'test' errors"
            },
            {
                "type": "source_frequency",
                "source": "execution",
                "count": 5,
                "description": "High number of errors from 'execution' source"
            }
        ]

        # Получаем паттерны ошибок
        patterns = self.agent.detect_error_patterns(time_period=7)

        # Проверяем результат
        self.assertEqual(len(patterns), 2)
        self.assertEqual(patterns[0]["type"], "category_frequency")
        self.assertEqual(patterns[1]["source"], "execution")

        # Проверяем, что метод detect_error_patterns был вызван с правильными аргументами
        self.agent.error_manager.detect_error_patterns.assert_called_once_with(time_period=7)

    def test_export_import_learning_dataset(self):
        """
        Тест экспорта и импорта набора данных для обучения
        """
        # Запускаем тест
        self.run_async_test(self._test_export_import_learning_dataset())

    async def _test_export_import_learning_dataset(self):
        """
        Асинхронная часть теста экспорта и импорта набора данных для обучения
        """
        # Настраиваем моки для методов экспорта и импорта
        self.agent.error_manager.export_learning_dataset.return_value = True
        self.agent.error_manager.import_learning_dataset.return_value = 10

        # Экспортируем набор данных
        export_result = self.agent.export_error_learning_dataset("test_export.json")

        # Проверяем результат экспорта
        self.assertTrue(export_result)
        self.agent.error_manager.export_learning_dataset.assert_called_once_with("test_export.json")

        # Импортируем набор данных
        import_result = self.agent.import_error_learning_dataset("test_import.json")

        # Проверяем результат импорта
        self.assertEqual(import_result, 10)
        self.agent.error_manager.import_learning_dataset.assert_called_once_with("test_import.json")

    def test_suggest_error_resolution(self):
        """
        Тест предложения решения для ошибки
        """
        # Запускаем тест
        self.run_async_test(self._test_suggest_error_resolution())

    async def _test_suggest_error_resolution(self):
        """
        Асинхронная часть теста предложения решения для ошибки
        """
        # Настраиваем моки для методов логирования и предложения решения
        self.agent.error_manager.log_error.return_value = "temp_error_id"
        self.agent.error_manager.suggest_error_resolution.return_value = "Update configuration file"

        # Получаем предлагаемое решение
        resolution = self.agent.suggest_error_resolution("Configuration file not found")

        # Проверяем результат
        self.assertEqual(resolution, "Update configuration file")

        # Проверяем, что методы были вызваны с правильными аргументами
        self.agent.error_manager.log_error.assert_called_once()
        self.agent.error_manager.suggest_error_resolution.assert_called_once_with("temp_error_id")


if __name__ == '__main__':
    unittest.main()
