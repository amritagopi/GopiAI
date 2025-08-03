"""
Тесты для безопасных файловых операций в CommandExecutor.
Проверяет функциональность задачи 14: Implement safe file system operations.
"""

import os
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Импортируем тестируемый класс
from command_executor import CommandExecutor


class TestFileOperations(unittest.TestCase):
    """Тесты для файловых операций CommandExecutor."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.executor = CommandExecutor()
        
        # Создаём временную директорию для тестов
        self.test_dir = tempfile.mkdtemp(prefix="gopiai_test_")
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        self.test_content = "Тестовое содержимое файла\nВторая строка\nТретья строка"
        
        # Создаём тестовый файл
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)

    def tearDown(self):
        """Очистка после тестов."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def _parse_response(self, response: str) -> dict:
        """Извлекает JSON данные из структурированного ответа."""
        try:
            # Ищем JSON часть в ответе
            json_start = response.find('[Структурированные данные]')
            if json_start != -1:
                json_part = response[json_start + len('[Структурированные данные]'):].strip()
                return json.loads(json_part)
            
            # Если не найден, пробуем парсить весь ответ как JSON
            return json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return {"raw_response": response}

    def test_read_file_success(self):
        """Тест успешного чтения файла."""
        result = self.executor.file_operations("read", self.test_file)
        
        self.assertIn("✅", result)
        self.assertIn("успешно прочитан", result)
        self.assertIn(self.test_content, result)
        
        # Проверяем структурированные данные
        data = self._parse_response(result)
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("data", {}).get("content"), self.test_content)

    def test_read_nonexistent_file(self):
        """Тест чтения несуществующего файла."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        result = self.executor.file_operations("read", nonexistent_file)
        
        self.assertIn("❌", result)
        self.assertIn("не существует", result)
        
        data = self._parse_response(result)
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("error_code"), "FILE_NOT_FOUND")

    def test_write_file_success(self):
        """Тест успешной записи файла."""
        new_file = os.path.join(self.test_dir, "new_file.txt")
        new_content = "Новое содержимое файла"
        
        result = self.executor.file_operations("write", new_file, new_content)
        
        self.assertIn("✅", result)
        self.assertIn("создан", result)
        
        # Проверяем, что файл действительно создан
        self.assertTrue(os.path.exists(new_file))
        
        with open(new_file, 'r', encoding='utf-8') as f:
            written_content = f.read()
        self.assertEqual(written_content, new_content)
        
        # Проверяем структурированные данные
        data = self._parse_response(result)
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("data", {}).get("operation"), "create")

    def test_write_file_overwrite(self):
        """Тест перезаписи существующего файла."""
        new_content = "Перезаписанное содержимое"
        
        result = self.executor.file_operations("write", self.test_file, new_content)
        
        self.assertIn("✅", result)
        self.assertIn("перезаписан", result)
        
        # Проверяем, что содержимое изменилось
        with open(self.test_file, 'r', encoding='utf-8') as f:
            written_content = f.read()
        self.assertEqual(written_content, new_content)
        
        data = self._parse_response(result)
        self.assertEqual(data.get("data", {}).get("operation"), "overwrite")

    def test_list_directory_success(self):
        """Тест успешного получения списка директории."""
        result = self.executor.file_operations("list_dir", self.test_dir)
        
        self.assertIn("✅", result)
        self.assertIn("test_file.txt", result)
        
        data = self._parse_response(result)
        self.assertEqual(data.get("status"), "success")
        self.assertGreater(data.get("data", {}).get("files_count", 0), 0)
        
        # Проверяем, что наш тестовый файл в списке
        items = data.get("data", {}).get("items", [])
        file_names = [item.get("name") for item in items]
        self.assertIn("test_file.txt", file_names)

    def test_list_nonexistent_directory(self):
        """Тест получения списка несуществующей директории."""
        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")
        result = self.executor.file_operations("list_dir", nonexistent_dir)
        
        self.assertIn("❌", result)
        self.assertIn("не существует", result)
        
        data = self._parse_response(result)
        self.assertEqual(data.get("error_code"), "DIRECTORY_NOT_FOUND")

    def test_exists_file_true(self):
        """Тест проверки существования файла (существует)."""
        result = self.executor.file_operations("exists", self.test_file)
        
        self.assertIn("✅", result)
        self.assertIn("существует", result)
        
        data = self._parse_response(result)
        self.assertTrue(data.get("data", {}).get("exists"))
        self.assertTrue(data.get("data", {}).get("is_file"))

    def test_exists_file_false(self):
        """Тест проверки существования файла (не существует)."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        result = self.executor.file_operations("exists", nonexistent_file)
        
        self.assertIn("✅", result)
        self.assertIn("не существует", result)
        
        data = self._parse_response(result)
        self.assertFalse(data.get("data", {}).get("exists"))

    def test_file_info_success(self):
        """Тест получения информации о файле."""
        result = self.executor.file_operations("info", self.test_file)
        
        self.assertIn("✅", result)
        self.assertIn("Информация о файле", result)
        
        data = self._parse_response(result)
        file_data = data.get("data", {})
        self.assertEqual(file_data.get("path"), self.test_file)
        self.assertTrue(file_data.get("is_file"))
        self.assertFalse(file_data.get("is_directory"))
        self.assertGreater(file_data.get("size_bytes", 0), 0)

    def test_mkdir_success(self):
        """Тест создания директории."""
        new_dir = os.path.join(self.test_dir, "new_directory")
        result = self.executor.file_operations("mkdir", new_dir)
        
        self.assertIn("✅", result)
        self.assertIn("создана", result)
        
        # Проверяем, что директория создана
        self.assertTrue(os.path.isdir(new_dir))
        
        data = self._parse_response(result)
        self.assertFalse(data.get("data", {}).get("already_existed"))

    def test_mkdir_already_exists(self):
        """Тест создания уже существующей директории."""
        result = self.executor.file_operations("mkdir", self.test_dir)
        
        self.assertIn("✅", result)
        self.assertIn("уже существовала", result)
        
        data = self._parse_response(result)
        self.assertTrue(data.get("data", {}).get("already_existed"))

    def test_copy_file_success(self):
        """Тест копирования файла."""
        dest_file = os.path.join(self.test_dir, "copied_file.txt")
        result = self.executor.file_operations("copy", self.test_file, destination=dest_file)
        
        self.assertIn("✅", result)
        self.assertIn("скопирован", result)
        
        # Проверяем, что файл скопирован
        self.assertTrue(os.path.exists(dest_file))
        
        with open(dest_file, 'r', encoding='utf-8') as f:
            copied_content = f.read()
        self.assertEqual(copied_content, self.test_content)
        
        data = self._parse_response(result)
        self.assertTrue(data.get("data", {}).get("source_was_file"))

    def test_move_file_success(self):
        """Тест перемещения файла."""
        # Создаём копию для перемещения
        source_file = os.path.join(self.test_dir, "file_to_move.txt")
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write("Содержимое для перемещения")
        
        dest_file = os.path.join(self.test_dir, "moved_file.txt")
        result = self.executor.file_operations("move", source_file, destination=dest_file)
        
        self.assertIn("✅", result)
        self.assertIn("перемещён", result)
        
        # Проверяем, что файл перемещён
        self.assertFalse(os.path.exists(source_file))
        self.assertTrue(os.path.exists(dest_file))

    def test_delete_file_success(self):
        """Тест удаления файла."""
        # Создаём файл для удаления
        file_to_delete = os.path.join(self.test_dir, "file_to_delete.txt")
        with open(file_to_delete, 'w', encoding='utf-8') as f:
            f.write("Файл для удаления")
        
        result = self.executor.file_operations("delete", file_to_delete)
        
        self.assertIn("✅", result)
        self.assertIn("удален", result)
        
        # Проверяем, что файл удалён
        self.assertFalse(os.path.exists(file_to_delete))
        
        data = self._parse_response(result)
        self.assertTrue(data.get("data", {}).get("was_file"))

    def test_invalid_operation(self):
        """Тест недопустимой операции."""
        result = self.executor.file_operations("invalid_op", self.test_file)
        
        self.assertIn("❌", result)
        self.assertIn("не поддерживается", result)
        
        data = self._parse_response(result)
        self.assertEqual(data.get("error_code"), "INVALID_OPERATION")

    def test_path_safety_validation(self):
        """Тест проверки безопасности путей."""
        dangerous_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\config",
            "/root/.ssh/id_rsa",
            "..\\..\\Windows\\System32"
        ]
        
        for dangerous_path in dangerous_paths:
            result = self.executor.file_operations("read", dangerous_path)
            self.assertIn("❌", result)
            self.assertIn("безопасност", result.lower())

    def test_encoding_handling(self):
        """Тест обработки различных кодировок."""
        # Создаём файл с кириллицей в cp1251
        cp1251_file = os.path.join(self.test_dir, "cp1251_file.txt")
        cp1251_content = "Тест кодировки cp1251"
        
        with open(cp1251_file, 'w', encoding='cp1251') as f:
            f.write(cp1251_content)
        
        # Читаем с правильной кодировкой
        result = self.executor.file_operations("read", cp1251_file, encoding="cp1251")
        self.assertIn("✅", result)
        self.assertIn(cp1251_content, result)
        
        # Читаем с неправильной кодировкой
        result_wrong = self.executor.file_operations("read", cp1251_file, encoding="utf-8")
        # Должна быть ошибка кодировки или искажённый текст
        data = self._parse_response(result_wrong)
        # В зависимости от системы может быть ошибка или искажение
        self.assertTrue(
            data.get("error_code") == "ENCODING_ERROR" or 
            data.get("status") == "success"  # Если система справилась с декодированием
        )

    def test_file_size_limits(self):
        """Тест ограничений размера файла."""
        # Создаём большой файл
        large_content = "A" * (self.executor.max_file_size + 1000)
        large_file = os.path.join(self.test_dir, "large_file.txt")
        
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        # Читаем большой файл
        result = self.executor.file_operations("read", large_file)
        
        # Должен быть успешным, но с обрезкой
        self.assertIn("✅", result)
        
        data = self._parse_response(result)
        if data.get("status") == "success":
            self.assertTrue(data.get("data", {}).get("was_truncated", False))
        
    def test_structured_response_format(self):
        """Тест формата структурированных ответов."""
        result = self.executor.file_operations("exists", self.test_file)
        
        # Проверяем, что ответ содержит и читаемую, и JSON части
        self.assertIn("✅", result)  # Читаемая часть
        self.assertIn("[Структурированные данные]", result)  # JSON часть
        
        data = self._parse_response(result)
        
        # Проверяем обязательные поля
        self.assertIn("status", data)
        self.assertIn("timestamp", data)
        
        if data.get("status") == "success":
            self.assertIn("data", data)
            self.assertIn("message", data)
        else:
            self.assertIn("error_code", data)
            self.assertIn("message", data)


class TestFileOperationsSafety(unittest.TestCase):
    """Дополнительные тесты безопасности файловых операций."""

    def setUp(self):
        self.executor = CommandExecutor()

    def test_path_traversal_prevention(self):
        """Тест предотвращения path traversal атак."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32\\config\\SAM",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "../../../../root/.bashrc"
        ]
        
        for path in malicious_paths:
            result = self.executor.file_operations("read", path)
            self.assertIn("❌", result)
            # Должна быть ошибка безопасности
            self.assertTrue(
                "безопасност" in result.lower() or 
                "запрещён" in result.lower() or
                "не существует" in result.lower()
            )

    def test_forbidden_file_names(self):
        """Тест запрещённых имён файлов (Windows)."""
        if os.name == 'nt':  # Только для Windows
            forbidden_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
            
            for name in forbidden_names:
                result = self.executor.file_operations("write", name, "test")
                # Должна быть ошибка или предупреждение
                self.assertTrue("❌" in result or "⚠️" in result)

    def test_empty_and_none_parameters(self):
        """Тест обработки пустых и None параметров."""
        # Пустая операция
        result = self.executor.file_operations("", "test.txt")
        self.assertIn("❌", result)
        
        # Пустой путь
        result = self.executor.file_operations("read", "")
        self.assertIn("❌", result)
        
        # None как содержимое (должно быть разрешено для создания пустых файлов)
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = os.path.join(temp_dir, "empty.txt")
            result = self.executor.file_operations("write", empty_file, None)
            # Должно быть успешным
            self.assertIn("✅", result)


if __name__ == "__main__":
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)