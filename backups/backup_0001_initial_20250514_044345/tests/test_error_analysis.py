"""
Тесты для системы анализа и категоризации типичных ошибок
"""

import os
import unittest
import json
import tempfile
import shutil
import time
from unittest.mock import patch, MagicMock

from app.agent.error_analysis_system import (
    ErrorSeverity, ErrorSource, ErrorCategory,
    ErrorInstance, ErrorStorage, ErrorAnalyzer
)
from app.agent.error_manager import ErrorManager


class TestErrorAnalysisSystem(unittest.TestCase):
    """
    Тесты для системы анализа и категоризации ошибок
    """

    def setUp(self):
        """
        Создает временную директорию для хранения тестовых данных
        """
        self.test_dir = tempfile.mkdtemp()
        self.error_storage = ErrorStorage(self.test_dir)
        self.error_analyzer = ErrorAnalyzer(self.error_storage)

        # Создаем тестовые категории
        self.permission_category = ErrorCategory(
            name="Permission Error",
            description="Errors related to permissions",
            patterns=[r"permission denied", r"access denied"],
            keywords=["permission", "access", "denied"],
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        self.file_category = ErrorCategory(
            name="File Error",
            description="Errors related to files",
            patterns=[r"no such file", r"file not found"],
            keywords=["file", "not found"],
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        # Добавляем категории в хранилище
        self.error_storage.add_category(self.permission_category)
        self.error_storage.add_category(self.file_category)

    def tearDown(self):
        """
        Удаляет временную директорию
        """
        shutil.rmtree(self.test_dir)

    def test_error_category_creation(self):
        """
        Тест создания категории ошибок
        """
        category = ErrorCategory(
            name="Test Category",
            description="Test description",
            patterns=[r"test pattern"],
            keywords=["test", "keyword"],
            source=ErrorSource.OTHER,
            severity=ErrorSeverity.LOW
        )

        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "Test description")
        self.assertEqual(len(category.patterns), 1)
        self.assertEqual(len(category.keywords), 2)
        self.assertEqual(category.source, ErrorSource.OTHER)
        self.assertEqual(category.severity, ErrorSeverity.LOW)

    def test_error_instance_creation(self):
        """
        Тест создания экземпляра ошибки
        """
        error = ErrorInstance(
            message="Test error message",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM,
            task_id="test_task_123"
        )

        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.source, ErrorSource.EXECUTION)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.task_id, "test_task_123")
        self.assertFalse(error.resolved)

    def test_error_matching(self):
        """
        Тест сопоставления ошибки с категорией
        """
        # Должен соответствовать категории Permission Error
        self.assertTrue(self.permission_category.matches("Permission denied when accessing file"))
        self.assertTrue(self.permission_category.matches("Access denied for user"))

        # Должен соответствовать категории File Error
        self.assertTrue(self.file_category.matches("No such file or directory: 'test.txt'"))
        self.assertTrue(self.file_category.matches("File not found: config.json"))

        # Не должен соответствовать ни одной категории
        self.assertFalse(self.permission_category.matches("Invalid argument provided"))
        self.assertFalse(self.file_category.matches("Connection refused"))

    def test_error_storage(self):
        """
        Тест хранения ошибок и категорий
        """
        # Создаем тестовую ошибку
        error = ErrorInstance(
            message="Permission denied when accessing file",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        # Добавляем ошибку в хранилище
        error_id = self.error_storage.add_error(error)

        # Проверяем, что ошибка добавлена
        self.assertIn(error_id, self.error_storage.errors)
        self.assertEqual(len(self.error_storage.errors), 1)

        # Получаем ошибку из хранилища
        retrieved_error = self.error_storage.get_error(error_id)
        self.assertEqual(retrieved_error.message, error.message)

        # Фильтруем ошибки по источнику
        permission_errors = self.error_storage.get_errors_by_source(ErrorSource.PERMISSION)
        self.assertEqual(len(permission_errors), 1)

        execution_errors = self.error_storage.get_errors_by_source(ErrorSource.EXECUTION)
        self.assertEqual(len(execution_errors), 0)

    def test_error_categorization(self):
        """
        Тест категоризации ошибок
        """
        # Создаем тестовые ошибки
        permission_error = ErrorInstance(
            message="Permission denied when accessing file",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        file_error = ErrorInstance(
            message="No such file or directory: 'test.txt'",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        unknown_error = ErrorInstance(
            message="Unknown error occurred",
            source=ErrorSource.OTHER,
            severity=ErrorSeverity.LOW
        )

        # Категоризируем ошибки
        permission_category_id = self.error_analyzer.categorize_error(permission_error)
        file_category_id = self.error_analyzer.categorize_error(file_error)
        unknown_category_id = self.error_analyzer.categorize_error(unknown_error)

        # Проверяем результаты категоризации
        self.assertEqual(permission_category_id, self.permission_category.id)
        self.assertEqual(file_category_id, self.file_category.id)
        self.assertIsNone(unknown_category_id)

    def test_suggest_new_category(self):
        """
        Тест предложения новой категории
        """
        error_messages = [
            "Connection refused: no route to host",
            "Connection refused: server not responding",
            "Connection failed: timeout",
            "Could not connect to server: connection refused",
            "Network error: connection refused"
        ]

        # Получаем предложение новой категории
        suggestion = self.error_analyzer.suggest_new_category(error_messages)

        # Проверяем результат
        self.assertIsNotNone(suggestion)
        self.assertIn("name", suggestion)
        self.assertIn("description", suggestion)
        self.assertIn("keywords", suggestion)

        # Проверяем, что ключевые слова связаны с подключением
        self.assertTrue(any("connect" in kw.lower() for kw in suggestion["keywords"]))

    def test_similar_errors(self):
        """
        Тест поиска похожих ошибок
        """
        # Создаем тестовые ошибки
        error1 = ErrorInstance(
            message="Permission denied when accessing file /etc/config.json",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        error2 = ErrorInstance(
            message="Access denied for file /var/log/app.log",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        error3 = ErrorInstance(
            message="No such file or directory: 'test.txt'",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        # Добавляем ошибки в хранилище
        self.error_storage.add_error(error1)
        self.error_storage.add_error(error2)
        self.error_storage.add_error(error3)

        # Ищем похожие ошибки
        similar = self.error_analyzer.get_similar_errors(error1)

        # Проверяем результаты
        self.assertEqual(len(similar), 2)  # Должно быть 2 похожие ошибки (включая error2)

        # Сортируем по сходству (от большего к меньшему)
        similar.sort(key=lambda x: x["similarity"], reverse=True)

        # Проверяем, что error2 более похож на error1, чем error3
        self.assertEqual(similar[0]["error"]["id"], error2.id)
        self.assertEqual(similar[1]["error"]["id"], error3.id)
        self.assertGreater(similar[0]["similarity"], similar[1]["similarity"])


class TestErrorManager(unittest.TestCase):
    """
    Тесты для менеджера ошибок
    """

    def setUp(self):
        """
        Создает временную директорию для хранения тестовых данных
        """
        self.test_dir = tempfile.mkdtemp()
        self.error_manager = ErrorManager(self.test_dir)

    def tearDown(self):
        """
        Удаляет временную директорию
        """
        shutil.rmtree(self.test_dir)

    def test_log_error(self):
        """
        Тест логирования ошибки
        """
        # Логируем тестовую ошибку
        error_id = self.error_manager.log_error(
            message="Test error message",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM,
            task_id="test_task_123"
        )

        # Проверяем, что ошибка добавлена в хранилище
        self.assertIn(error_id, self.error_manager.storage.errors)

        # Получаем ошибку из хранилища
        error = self.error_manager.storage.get_error(error_id)
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.source, ErrorSource.EXECUTION)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.task_id, "test_task_123")

    def test_log_exception(self):
        """
        Тест логирования исключения
        """
        try:
            # Вызываем исключение
            raise ValueError("Test exception")
        except Exception as e:
            # Логируем исключение
            error_id = self.error_manager.log_exception(
                exception=e,
                source=ErrorSource.EXECUTION,
                task_id="test_task_123"
            )

        # Проверяем, что ошибка добавлена в хранилище
        self.assertIn(error_id, self.error_manager.storage.errors)

        # Получаем ошибку из хранилища
        error = self.error_manager.storage.get_error(error_id)
        self.assertEqual(error.message, "Test exception")
        self.assertEqual(error.source, ErrorSource.EXECUTION)
        self.assertIsNotNone(error.stack_trace)

    def test_resolve_error(self):
        """
        Тест разрешения ошибки
        """
        # Логируем тестовую ошибку
        error_id = self.error_manager.log_error(
            message="Test error message",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        # Разрешаем ошибку
        result = self.error_manager.resolve_error(
            error_id=error_id,
            resolution="Fixed by updating configuration"
        )

        # Проверяем результат
        self.assertTrue(result)

        # Получаем ошибку из хранилища
        error = self.error_manager.storage.get_error(error_id)
        self.assertTrue(error.resolved)
        self.assertEqual(error.resolution, "Fixed by updating configuration")
        self.assertIsNotNone(error.resolved_at)

    def test_error_statistics(self):
        """
        Тест получения статистики ошибок
        """
        # Логируем несколько тестовых ошибок
        self.error_manager.log_error(
            message="Permission denied",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        self.error_manager.log_error(
            message="File not found",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        self.error_manager.log_error(
            message="Another file not found",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        # Получаем статистику
        stats = self.error_manager.get_error_statistics()

        # Проверяем результаты
        self.assertEqual(stats["total_errors"], 3)
        self.assertEqual(len(stats["by_source"]), 2)  # PERMISSION, EXECUTION
        self.assertEqual(len(stats["by_severity"]), 2)  # HIGH, MEDIUM

        # Проверяем распределение по источникам
        self.assertEqual(stats["by_source"]["permission"], 1)
        self.assertEqual(stats["by_source"]["execution"], 2)

        # Проверяем распределение по уровням серьезности
        self.assertEqual(stats["by_severity"]["high"], 1)
        self.assertEqual(stats["by_severity"]["medium"], 2)

    def test_learning_dataset_export_import(self):
        """
        Тест экспорта и импорта набора данных для обучения
        """
        # Логируем несколько тестовых ошибок
        error_id1 = self.error_manager.log_error(
            message="Permission denied",
            source=ErrorSource.PERMISSION,
            severity=ErrorSeverity.HIGH
        )

        error_id2 = self.error_manager.log_error(
            message="File not found",
            source=ErrorSource.EXECUTION,
            severity=ErrorSeverity.MEDIUM
        )

        # Разрешаем ошибки
        self.error_manager.resolve_error(error_id1, "Fixed by updating permissions")
        self.error_manager.resolve_error(error_id2, "Fixed by creating missing file")

        # Создаем временный файл для экспорта
        temp_file = os.path.join(self.test_dir, "test_dataset.json")

        # Экспортируем набор данных
        result = self.error_manager.export_learning_dataset(temp_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(temp_file))

        # Проверяем содержимое файла
        with open(temp_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            self.assertEqual(len(dataset), 2)  # 2 разрешенные ошибки

        # Создаем новый менеджер ошибок
        new_manager = ErrorManager(self.test_dir + "_new")

        # Импортируем набор данных
        count = new_manager.import_learning_dataset(temp_file)
        self.assertEqual(count, 2)  # 2 импортированные записи

        # Проверяем, что ошибки импортированы
        self.assertEqual(len(new_manager.storage.errors), 2)

        # Очищаем временные данные
        shutil.rmtree(self.test_dir + "_new")

    def test_error_deduplication(self):
        """
        Тест механизма предотвращения дублирования ошибок
        """
        # Логируем первую ошибку
        error_message = "Test duplicate error message"
        first_error_id = self.error_manager.log_error(
            message=error_message,
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW,
            prevent_duplicates=True
        )

        # Проверяем, что ошибка добавлена
        self.assertIsNotNone(first_error_id)
        self.assertEqual(len(self.error_manager.storage.errors), 1)

        # Логируем такую же ошибку через короткий промежуток времени
        second_error_id = self.error_manager.log_error(
            message=error_message,
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW,
            prevent_duplicates=True
        )

        # Проверяем, что новая ошибка не создана, а возвращен ID первой ошибки
        self.assertEqual(first_error_id, second_error_id)
        self.assertEqual(len(self.error_manager.storage.errors), 1)

        # Проверяем, что счетчик в recent_errors увеличен
        error_hash = f"{error_message[:100]}_{ErrorSource.AGENT.value}"
        self.assertEqual(self.error_manager.recent_errors[error_hash]['count'], 2)

        # Логируем ошибку с другим сообщением
        different_error_id = self.error_manager.log_error(
            message="Different error message",
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW,
            prevent_duplicates=True
        )

        # Проверяем, что создана новая ошибка
        self.assertNotEqual(first_error_id, different_error_id)
        self.assertEqual(len(self.error_manager.storage.errors), 2)

        # Логируем ошибку с тем же сообщением, но с отключенной дедупликацией
        third_error_id = self.error_manager.log_error(
            message=error_message,
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW,
            prevent_duplicates=False
        )

        # Проверяем, что создана новая ошибка
        self.assertNotEqual(first_error_id, third_error_id)
        self.assertEqual(len(self.error_manager.storage.errors), 3)

    def test_clean_recent_errors(self):
        """
        Тест очистки списка недавних ошибок
        """
        # Добавляем тестовые ошибки в список недавних
        self.error_manager.recent_errors = {
            "error1": {"count": 1, "last_time": time.time() - 400, "error_id": "id1"},
            "error2": {"count": 2, "last_time": time.time() - 200, "error_id": "id2"},
            "error3": {"count": 3, "last_time": time.time() - 100, "error_id": "id3"}
        }

        # Устанавливаем окно дедупликации на 300 секунд
        self.error_manager.deduplication_window = 300

        # Устанавливаем время последней очистки достаточно давно
        self.error_manager.last_cleanup_time = time.time() - 3700  # больше час назад

        # Вызываем метод очистки
        self.error_manager._clean_recent_errors()

        # Проверяем, что старые ошибки удалены
        self.assertNotIn("error1", self.error_manager.recent_errors)
        self.assertIn("error2", self.error_manager.recent_errors)
        self.assertIn("error3", self.error_manager.recent_errors)

        # Проверяем, что время последней очистки обновлено
        self.assertGreater(self.error_manager.last_cleanup_time, time.time() - 10)


class TestErrorStorage(unittest.TestCase):
    """
    Тесты для класса ErrorStorage
    """

    def setUp(self):
        # Создаем временный каталог для тестов
        self.test_dir = tempfile.mkdtemp()
        self.storage = ErrorStorage(self.test_dir)

    def tearDown(self):
        # Удаляем временный каталог после тестов
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_clean_old_errors(self):
        """
        Тест очистки старых ошибок
        """
        # Добавляем ошибки с разным временем создания
        current_time = time.time()

        # Создаем старую ошибку (100 дней назад) с низким приоритетом
        old_error = ErrorInstance(
            message="Old error",
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW
        )
        old_error.created_at = current_time - (100 * 24 * 60 * 60)  # 100 дней назад
        old_error_id = self.storage.add_error(old_error)

        # Создаем старую ошибку с высоким приоритетом
        critical_old_error = ErrorInstance(
            message="Critical old error",
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.CRITICAL
        )
        critical_old_error.created_at = current_time - (100 * 24 * 60 * 60)  # 100 дней назад
        critical_old_id = self.storage.add_error(critical_old_error)

        # Создаем новую ошибку (1 день назад)
        new_error = ErrorInstance(
            message="New error",
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.LOW
        )
        new_error.created_at = current_time - (1 * 24 * 60 * 60)  # 1 день назад
        new_error_id = self.storage.add_error(new_error)

        # Проверяем, что все ошибки добавлены
        self.assertEqual(len(self.storage.errors), 3)

        # Очищаем ошибки старше 90 дней
        cleaned_count = self.storage.clean_old_errors(days_threshold=90)

        # Проверяем, что удалена только старая ошибка с низким приоритетом
        self.assertEqual(cleaned_count, 1)
        self.assertEqual(len(self.storage.errors), 2)
        self.assertNotIn(old_error_id, self.storage.errors)
        self.assertIn(critical_old_id, self.storage.errors)
        self.assertIn(new_error_id, self.storage.errors)

    def test_create_backup(self):
        """
        Тест создания резервной копии данных
        """
        # Добавляем тестовые данные
        category = ErrorCategory(
            name="Test Category",
            description="Test description",
            patterns=["test pattern"],
            keywords=["test"]
        )
        self.storage.add_category(category)

        error = ErrorInstance(
            message="Test error",
            source=ErrorSource.AGENT,
            severity=ErrorSeverity.MEDIUM
        )
        self.storage.add_error(error)

        # Сохраняем данные
        self.storage.save()

        # Создаем резервную копию
        result = self.storage.create_backup()

        # Проверяем, что резервная копия создана успешно
        self.assertTrue(result)

        # Проверяем, что директория с резервными копиями существует
        backup_dir = os.path.join(self.test_dir, "backups")
        self.assertTrue(os.path.exists(backup_dir))

        # Проверяем, что файлы резервных копий созданы
        files = os.listdir(backup_dir)
        self.assertGreaterEqual(len(files), 1)

        # Проверяем содержимое файлов
        has_categories = False
        has_errors = False

        for file in files:
            if file.startswith("categories_"):
                has_categories = True
            elif file.startswith("errors_"):
                has_errors = True

        self.assertTrue(has_categories)
        self.assertTrue(has_errors)


if __name__ == '__main__':
    unittest.main()
