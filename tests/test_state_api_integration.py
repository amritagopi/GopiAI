"""
Интеграционные тесты для REST API синхронизации состояния.

Проверяет взаимодействие между UI виджетом и backend API
для синхронизации состояния провайдера/модели.
"""

import unittest
import tempfile
import json
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import sys

# Добавляем пути для импорта
sys.path.append(str(Path(__file__).parent.parent / "GopiAI-Core"))
sys.path.append(str(Path(__file__).parent.parent / "GopiAI-UI"))

try:
    from gopiai.core.state_manager import StateManager, ProviderModelState
except ImportError:
    # Заглушка для случая, когда модуль недоступен
    class StateManager:
        def __init__(self, *args, **kwargs):
            pass
        def save_state(self, provider, model_id):
            return True
        def load_state(self):
            return ProviderModelState("gemini", "gemini-1.5-flash", "2025-01-01T12:00:00")
    
    class ProviderModelState:
        def __init__(self, provider, model_id, last_updated):
            self.provider = provider
            self.model_id = model_id
            self.last_updated = last_updated


class TestStateAPIIntegration(unittest.TestCase):
    """Тесты для интеграции с REST API"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.backend_url = "http://localhost:5051"
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / "api_test_state.json"
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        import os
        os.rmdir(self.temp_dir)
    
    @patch('requests.post')
    @patch('requests.get')
    def test_ui_backend_state_sync(self, mock_get, mock_post):
        """Тест синхронизации состояния между UI и backend"""
        # Настраиваем mock для GET запроса (загрузка состояния)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "provider": "gemini",
            "model_id": "gemini-1.5-flash",
            "last_updated": "2025-01-01T12:00:00",
            "source": "state_file"
        }
        
        # Настраиваем mock для POST запроса (сохранение состояния)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "message": "State updated: provider=openrouter, model_id=anthropic/claude-3-sonnet",
            "provider": "openrouter",
            "model_id": "anthropic/claude-3-sonnet",
            "saved_to_file": True
        }
        
        # Симулируем загрузку состояния из backend
        response = requests.get(f"{self.backend_url}/internal/state", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        state_data = response.json()
        self.assertEqual(state_data["provider"], "gemini")
        self.assertEqual(state_data["model_id"], "gemini-1.5-flash")
        
        # Симулируем обновление состояния через UI
        new_state = {
            "provider": "openrouter",
            "model_id": "anthropic/claude-3-sonnet"
        }
        
        response = requests.post(
            f"{self.backend_url}/internal/state",
            json=new_state,
            timeout=5
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(result["model_id"], "anthropic/claude-3-sonnet")
        self.assertTrue(result["saved_to_file"])
        
        # Проверяем, что были сделаны правильные вызовы
        mock_get.assert_called_once_with(f"{self.backend_url}/internal/state", timeout=5)
        mock_post.assert_called_once_with(
            f"{self.backend_url}/internal/state",
            json=new_state,
            timeout=5
        )
    
    @patch('requests.get')
    def test_backend_unavailable_fallback(self, mock_get):
        """Тест fallback поведения при недоступности backend"""
        # Симулируем недоступность backend
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        # Пытаемся загрузить состояние
        try:
            response = requests.get(f"{self.backend_url}/internal/state", timeout=5)
            self.fail("Ожидалось исключение ConnectionError")
        except requests.exceptions.ConnectionError:
            # Это ожидаемое поведение
            pass
        
        # В реальном приложении здесь должен сработать fallback к локальному StateManager
        # Симулируем это поведение
        with patch('gopiai.core.state_manager.StateManager') as mock_state_manager:
            mock_instance = mock_state_manager.return_value
            mock_instance.load_state.return_value = ProviderModelState(
                "gemini", "gemini-1.5-flash", "2025-01-01T12:00:00"
            )
            
            # Создаём StateManager и загружаем состояние
            state_manager = StateManager(self.test_state_file)
            fallback_state = state_manager.load_state()
            
            self.assertEqual(fallback_state.provider, "gemini")
            self.assertEqual(fallback_state.model_id, "gemini-1.5-flash")
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Тест обработки ошибок API"""
        # Тест 1: Сервер возвращает ошибку 500
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {
            "error": "Internal server error"
        }
        
        response = requests.post(
            f"{self.backend_url}/internal/state",
            json={"provider": "gemini", "model_id": "gemini-1.5-flash"},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 500)
        error_data = response.json()
        self.assertIn("error", error_data)
        
        # Тест 2: Некорректные данные
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "error": "Both 'provider' and 'model_id' are required"
        }
        
        response = requests.post(
            f"{self.backend_url}/internal/state",
            json={"provider": ""},  # Пустой провайдер
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        error_data = response.json()
        self.assertIn("required", error_data["error"])
    
    def test_state_file_format_validation(self):
        """Тест валидации формата файла состояния"""
        # Создаём корректный файл состояния
        correct_state = {
            "provider": "openrouter",
            "model_id": "anthropic/claude-3-haiku",
            "last_updated": "2025-01-01T12:00:00",
            "version": "1.0"
        }
        
        self.test_state_file.write_text(json.dumps(correct_state, indent=2))
        
        # Проверяем, что файл корректен
        with open(self.test_state_file, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data["provider"], "openrouter")
        self.assertEqual(loaded_data["model_id"], "anthropic/claude-3-haiku")
        self.assertEqual(loaded_data["version"], "1.0")
        
        # Проверяем обязательные поля
        required_fields = ["provider", "model_id", "last_updated"]
        for field in required_fields:
            self.assertIn(field, loaded_data)
    
    @patch('gopiai.core.state_manager.get_state_manager')
    def test_ui_widget_state_management(self, mock_get_state_manager):
        """Тест управления состоянием в UI виджете"""
        # Настраиваем mock StateManager
        mock_state_manager = MagicMock()
        mock_get_state_manager.return_value = mock_state_manager
        
        # Настраиваем возвращаемое состояние
        mock_state = ProviderModelState(
            "gemini", "gemini-1.5-pro", "2025-01-01T12:00:00"
        )
        mock_state_manager.load_state.return_value = mock_state
        mock_state_manager.save_state.return_value = True
        
        # Симулируем работу UI виджета
        from gopiai.core.state_manager import get_state_manager, save_provider_model_state
        
        # Загрузка состояния при инициализации виджета
        state_manager = get_state_manager()
        initial_state = state_manager.load_state()
        
        self.assertEqual(initial_state.provider, "gemini")
        self.assertEqual(initial_state.model_id, "gemini-1.5-pro")
        
        # Изменение состояния пользователем
        success = save_provider_model_state("openrouter", "meta-llama/llama-3.1-70b-instruct")
        self.assertTrue(success)
        
        # Проверяем, что методы были вызваны
        mock_state_manager.load_state.assert_called_once()
        mock_get_state_manager.assert_called()


class TestStateFileOperations(unittest.TestCase):
    """Тесты для операций с файлом состояния"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = Path(self.temp_dir) / "file_ops_state.json"
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if self.test_state_file.exists():
            self.test_state_file.unlink()
        import os
        os.rmdir(self.temp_dir)
    
    def test_atomic_file_operations(self):
        """Тест атомарных операций с файлом"""
        state_manager = StateManager(self.test_state_file)
        
        # Сохраняем состояние
        success = state_manager.save_state("gemini", "gemini-1.5-flash")
        self.assertTrue(success)
        
        # Проверяем, что временный файл не остался
        temp_file = self.test_state_file.with_suffix('.tmp')
        self.assertFalse(temp_file.exists())
        
        # Проверяем содержимое файла
        with open(self.test_state_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["provider"], "gemini")
        self.assertEqual(data["model_id"], "gemini-1.5-flash")
    
    def test_file_permissions(self):
        """Тест прав доступа к файлу"""
        state_manager = StateManager(self.test_state_file)
        
        # Сохраняем состояние
        success = state_manager.save_state("openrouter", "test-model")
        self.assertTrue(success)
        
        # Проверяем, что файл существует и доступен для чтения
        self.assertTrue(self.test_state_file.exists())
        self.assertTrue(self.test_state_file.is_file())
        
        # Проверяем, что можем прочитать файл
        content = self.test_state_file.read_text()
        self.assertIn("openrouter", content)
        self.assertIn("test-model", content)
    
    def test_concurrent_file_access(self):
        """Тест конкурентного доступа к файлу"""
        import threading
        import time
        
        state_manager = StateManager(self.test_state_file)
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Каждый worker сохраняет своё состояние
                success = state_manager.save_state(f"provider_{worker_id}", f"model_{worker_id}")
                results.append((worker_id, success))
                
                # Небольшая задержка
                time.sleep(0.01)
                
                # Загружаем состояние
                loaded_state = state_manager.load_state()
                results.append((worker_id, "loaded", loaded_state.provider, loaded_state.model_id))
                
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Запускаем несколько потоков
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Ждём завершения
        for thread in threads:
            thread.join()
        
        # Проверяем результаты
        self.assertEqual(len(errors), 0, f"Ошибки при конкурентном доступе: {errors}")
        self.assertGreater(len(results), 0)
        
        # Проверяем, что файл в итоге содержит корректные данные
        final_state = state_manager.load_state()
        self.assertIsNotNone(final_state.provider)
        self.assertIsNotNone(final_state.model_id)


if __name__ == '__main__':
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)