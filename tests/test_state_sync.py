"""
Тесты для синхронизации состояния провайдера/модели между UI и backend.

Проверяет:
- Сохранение состояния в файл ~/.gopiai_state.json
- Загрузку состояния при запуске
- Синхронизацию между UI и backend
- Обработку ошибок и fallback сценариев
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Импортируем тестируемые модули
import sys
sys.path.append(str(Path(__file__).parent.parent / "GopiAI-Core"))

from gopiai.core.state_manager import (
    StateManager, 
    ProviderModelState, 
    get_state_manager,
    load_provider_model_state,
    save_provider_model_state
)


class TestProviderModelState(unittest.TestCase):
    """Тесты для класса ProviderModelState"""
    
    def test_create_state(self):
        """Тест создания объекта состояния"""
        state = ProviderModelState(
            provider="gemini",
            model_id="gemini-1.5-flash",
            last_updated="2025-01-01T12:00:00"
        )
        
        self.assertEqual(state.provider, "gemini")
        self.assertEqual(state.model_id, "gemini-1.5-flash")
        self.assertEqual(state.version, "1.0")
    
    def test_to_dict(self):
        """Тест преобразования в словарь"""
        state = ProviderModelState(
            provider="openrouter",
            model_id="anthropic/claude-3-haiku",
            last_updated="2025-01-01T12:00:00"
        )
        
        data = state.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data["provider"], "openrouter")
        self.assertEqual(data["model_id"], "anthropic/claude-3-haiku")
        self.assertEqual(data["version"], "1.0")
    
    def test_from_dict(self):
        """Тест создания из словаря"""
        data = {
            "provider": "gemini",
            "model_id": "gemini-1.5-pro",
            "last_updated": "2025-01-01T12:00:00",
            "version": "1.0"
        }
        
        state = ProviderModelState.from_dict(data)
        
        self.assertEqual(state.provider, "gemini")
        self.assertEqual(state.model_id, "gemini-1.5-pro")
        self.assertEqual(state.version, "1.0")
    
    def test_from_dict_with_defaults(self):
        """Тест создания из словаря с значениями по умолчанию"""
        data = {}
        
        state = ProviderModelState.from_dict(data)
        
        self.assertEqual(state.provider, "gemini")
        self.assertEqual(state.model_id, "")
        self.assertEqual(state.version, "1.0")


class TestStateManager(unittest.TestCase):
    """Тесты для класса StateManager"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        # Создаём временный файл для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / "test_state.json"
        self.state_manager = StateManager(self.test_state_file)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временные файлы
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_save_and_load_state(self):
        """Тест сохранения и загрузки состояния"""
        # Сохраняем состояние
        success = self.state_manager.save_state("openrouter", "anthropic/claude-3-sonnet")
        self.assertTrue(success)
        
        # Проверяем, что файл создан
        self.assertTrue(self.test_state_file.exists())
        
        # Загружаем состояние
        loaded_state = self.state_manager.load_state()
        
        self.assertEqual(loaded_state.provider, "openrouter")
        self.assertEqual(loaded_state.model_id, "anthropic/claude-3-sonnet")
        self.assertEqual(loaded_state.version, "1.0")
    
    def test_load_nonexistent_file(self):
        """Тест загрузки несуществующего файла"""
        # Убеждаемся, что файл не существует
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        
        # Загружаем состояние - должно создаться состояние по умолчанию
        state = self.state_manager.load_state()
        
        self.assertEqual(state.provider, "gemini")
        self.assertEqual(state.model_id, "gemini-1.5-flash")
        
        # Файл должен быть создан
        self.assertTrue(self.test_state_file.exists())
    
    def test_load_corrupted_file(self):
        """Тест загрузки повреждённого файла"""
        # Создаём повреждённый JSON файл
        self.test_state_file.write_text("invalid json content")
        
        # Загружаем состояние - должно создаться состояние по умолчанию
        state = self.state_manager.load_state()
        
        self.assertEqual(state.provider, "gemini")
        self.assertEqual(state.model_id, "gemini-1.5-flash")
        
        # Должна быть создана резервная копия
        backup_file = self.test_state_file.with_suffix('.json.backup')
        self.assertTrue(backup_file.exists())
    
    def test_save_invalid_data(self):
        """Тест сохранения некорректных данных"""
        # Пытаемся сохранить пустые значения
        success = self.state_manager.save_state("", "")
        self.assertFalse(success)
        
        # Пытаемся сохранить None
        success = self.state_manager.save_state(None, "model")
        self.assertFalse(success)
        
        success = self.state_manager.save_state("provider", None)
        self.assertFalse(success)
    
    def test_validate_state_file(self):
        """Тест валидации файла состояния"""
        # Сначала файл не существует
        self.assertFalse(self.state_manager.validate_state_file())
        
        # Сохраняем корректное состояние
        self.state_manager.save_state("gemini", "gemini-1.5-pro")
        self.assertTrue(self.state_manager.validate_state_file())
        
        # Портим файл
        self.test_state_file.write_text('{"invalid": "structure"}')
        self.assertFalse(self.state_manager.validate_state_file())
    
    def test_reset_to_default(self):
        """Тест сброса к значениям по умолчанию"""
        # Сначала сохраняем кастомное состояние
        self.state_manager.save_state("openrouter", "custom-model")
        
        # Сбрасываем к значениям по умолчанию
        default_state = self.state_manager.reset_to_default()
        
        self.assertEqual(default_state.provider, "gemini")
        self.assertEqual(default_state.model_id, "gemini-1.5-flash")
        
        # Проверяем, что файл обновлён
        loaded_state = self.state_manager.load_state()
        self.assertEqual(loaded_state.provider, "gemini")
        self.assertEqual(loaded_state.model_id, "gemini-1.5-flash")
    
    def test_concurrent_access(self):
        """Тест конкурентного доступа к файлу состояния"""
        import threading
        import time
        
        results = []
        errors = []
        
        def save_state_worker(provider, model_id):
            try:
                success = self.state_manager.save_state(provider, model_id)
                results.append((provider, model_id, success))
            except Exception as e:
                errors.append(e)
        
        # Запускаем несколько потоков одновременно
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=save_state_worker, 
                args=(f"provider_{i}", f"model_{i}")
            )
            threads.append(thread)
            thread.start()
        
        # Ждём завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем результаты
        self.assertEqual(len(errors), 0, f"Ошибки при конкурентном доступе: {errors}")
        self.assertEqual(len(results), 5)
        
        # Все операции должны быть успешными
        for provider, model_id, success in results:
            self.assertTrue(success, f"Неудачное сохранение для {provider}/{model_id}")


class TestGlobalFunctions(unittest.TestCase):
    """Тесты для глобальных функций"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / "test_global_state.json"
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        os.rmdir(self.temp_dir)
    
    @patch('gopiai.core.state_manager.STATE_FILE_PATH')
    def test_global_functions(self, mock_state_path):
        """Тест глобальных функций для работы с состоянием"""
        mock_state_path.return_value = self.test_state_file
        
        # Тестируем сохранение
        success = save_provider_model_state("openrouter", "test-model")
        self.assertTrue(success)
        
        # Тестируем загрузку
        state = load_provider_model_state()
        self.assertEqual(state.provider, "openrouter")
        self.assertEqual(state.model_id, "test-model")


class TestIntegrationScenarios(unittest.TestCase):
    """Интеграционные тесты для реальных сценариев использования"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / "integration_state.json"
        self.state_manager = StateManager(self.test_state_file)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_ui_backend_sync_scenario(self):
        """Тест сценария синхронизации между UI и backend"""
        # Симулируем изменение в UI
        ui_provider = "openrouter"
        ui_model = "anthropic/claude-3-haiku"
        
        # UI сохраняет состояние
        success = self.state_manager.save_state(ui_provider, ui_model)
        self.assertTrue(success)
        
        # Backend загружает состояние при запуске
        backend_state = self.state_manager.load_state()
        
        self.assertEqual(backend_state.provider, ui_provider)
        self.assertEqual(backend_state.model_id, ui_model)
        
        # Backend изменяет состояние
        backend_provider = "gemini"
        backend_model = "gemini-1.5-pro"
        
        success = self.state_manager.save_state(backend_provider, backend_model)
        self.assertTrue(success)
        
        # UI загружает обновлённое состояние
        ui_state = self.state_manager.load_state()
        
        self.assertEqual(ui_state.provider, backend_provider)
        self.assertEqual(ui_state.model_id, backend_model)
    
    def test_application_restart_scenario(self):
        """Тест сценария перезапуска приложения"""
        # Первый запуск - сохраняем состояние
        initial_provider = "openrouter"
        initial_model = "meta-llama/llama-3.1-8b-instruct"
        
        self.state_manager.save_state(initial_provider, initial_model)
        
        # Симулируем перезапуск - создаём новый экземпляр StateManager
        new_state_manager = StateManager(self.test_state_file)
        
        # Загружаем состояние после "перезапуска"
        restored_state = new_state_manager.load_state()
        
        self.assertEqual(restored_state.provider, initial_provider)
        self.assertEqual(restored_state.model_id, initial_model)
    
    def test_error_recovery_scenario(self):
        """Тест сценария восстановления после ошибок"""
        # Сначала сохраняем корректное состояние
        self.state_manager.save_state("gemini", "gemini-1.5-flash")
        
        # Портим файл
        self.test_state_file.write_text("corrupted data")
        
        # Пытаемся загрузить - должно создаться состояние по умолчанию
        recovered_state = self.state_manager.load_state()
        
        self.assertEqual(recovered_state.provider, "gemini")
        self.assertEqual(recovered_state.model_id, "gemini-1.5-flash")
        
        # Проверяем, что создана резервная копия
        backup_file = self.test_state_file.with_suffix('.json.backup')
        self.assertTrue(backup_file.exists())
        
        # Проверяем, что новый файл корректен
        self.assertTrue(self.state_manager.validate_state_file())


if __name__ == '__main__':
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Запуск тестов
    unittest.main(verbosity=2)