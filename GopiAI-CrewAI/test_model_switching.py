"""Тесты для проверки функциональности переключения провайдеров и моделей."""
import os
import sys
import time
import json
import tempfile
from pathlib import Path

# Добавляем пути для импорта
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from llm_rotation_config import (
    UsageTracker, 
    PROVIDER_KEY_ENV, 
    MODELS, 
    update_state,
    get_api_key_for_provider,
    get_available_models,
    register_use,
    is_model_blacklisted
)

def test_usage_tracker_provider_switching():
    """Тест переключения провайдеров в UsageTracker."""
    print("Тест 1: Переключение провайдеров")
    
    tracker = UsageTracker(MODELS)
    
    # Проверяем начальное состояние
    assert tracker.current_provider == "gemini"
    print("✓ Начальный провайдер: gemini")
    
    # Переключаемся на openrouter
    tracker.set_current_provider("openrouter")
    assert tracker.current_provider == "openrouter"
    print("✓ Переключение на openrouter успешно")
    
    # Переключаемся обратно на gemini
    tracker.set_current_provider("gemini")
    assert tracker.current_provider == "gemini"
    print("✓ Переключение обратно на gemini успешно")
    
    print("Тест 1 пройден успешно!\n")

def test_soft_blacklist():
    """Тест механизма мягкого черного списка."""
    print("Тест 2: Механизм мягкого черного списка")
    
    tracker = UsageTracker(MODELS)
    
    # Находим модель с низким RPM для теста
    test_model = None
    for model in MODELS:
        if model["provider"] == "gemini" and model["rpm"] > 0:
            test_model = model
            break
    
    if not test_model:
        print("✗ Не найдена подходящая модель для теста")
        return
    
    model_id = test_model["id"]
    rpm_limit = test_model["rpm"]
    
    # Проверяем, что модель не в черном списке
    assert not tracker.is_blacklisted(model_id)
    print(f"✓ Модель {model_id} не в черном списке")
    
    # Регистрируем использование, превышающее лимит в 1.5 раза
    for i in range(int(rpm_limit * 2)):  # Превышаем лимит
        tracker.register_use(test_model, 100)
    
    # Проверяем, что модель заблокирована
    assert tracker.is_blacklisted(model_id)
    print(f"✓ Модель {model_id} заблокирована после превышения лимита")
    
    # Ждем разблокировки (имитация времени)
    stats = tracker.get_stats(model_id)
    print(f"✓ Время до разблокировки: {stats['blacklisted_until'] - time.time():.1f} секунд")
    
    print("Тест 2 пройден успешно!\n")

def test_api_key_handling():
    """Тест обработки API ключей."""
    print("Тест 3: Обработка API ключей")
    
    # Сохраняем оригинальные переменные окружения
    original_gemini_key = os.environ.get("GEMINI_API_KEY")
    original_openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    try:
        # Устанавливаем тестовые ключи
        test_gemini_key = "test_gemini_key_1234567890"
        test_openrouter_key = "test_openrouter_key_1234567890"
        
        os.environ["GEMINI_API_KEY"] = test_gemini_key
        os.environ["OPENROUTER_API_KEY"] = test_openrouter_key
        
        # Проверяем получение ключей
        gemini_key = get_api_key_for_provider("gemini")
        openrouter_key = get_api_key_for_provider("openrouter")
        
        assert gemini_key == test_gemini_key
        assert openrouter_key == test_openrouter_key
        print("✓ API ключи корректно извлекаются")
        
        # Проверяем несуществующий провайдер
        unknown_key = get_api_key_for_provider("unknown")
        assert unknown_key is None
        print("✓ Неизвестный провайдер возвращает None")
        
    finally:
        # Восстанавливаем оригинальные переменные окружения
        if original_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = original_gemini_key
        elif "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            
        if original_openrouter_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_openrouter_key
        elif "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
    
    print("Тест 3 пройден успешно!\n")

def test_state_persistence():
    """Тест сохранения состояния в файл."""
    print("Тест 4: Сохранение состояния")
    
    # Создаем временный файл для состояния
    with tempfile.TemporaryDirectory() as temp_dir:
        state_file = Path(temp_dir) / ".gopiai_state.json"
        
        # Сохраняем оригинальный путь к файлу состояния
        import state_manager
        original_state_path = state_manager.STATE_PATH
        
        try:
            # Подменяем путь к файлу состояния
            state_manager.STATE_PATH = state_file
            
            # Обновляем состояние
            update_state("openrouter", "openrouter/mistralai-mistral-7b-instruct")
            
            # Проверяем, что файл создан
            assert state_file.exists()
            print("✓ Файл состояния создан")
            
            # Читаем и проверяем содержимое
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            assert state["provider"] == "openrouter"
            assert state["model_id"] == "openrouter/mistralai-mistral-7b-instruct"
            print("✓ Состояние корректно сохранено в файл")
            
        finally:
            # Восстанавливаем оригинальный путь
            state_manager.STATE_PATH = original_state_path
    
    print("Тест 4 пройден успешно!\n")

def test_model_availability():
    """Тест доступности моделей."""
    print("Тест 5: Доступность моделей")
    
    # Сохраняем оригинальные переменные окружения
    original_gemini_key = os.environ.get("GEMINI_API_KEY")
    original_openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    try:
        # Устанавливаем тестовые ключи
        os.environ["GEMINI_API_KEY"] = "test_key"
        os.environ["OPENROUTER_API_KEY"] = "test_key"
        
        # Получаем доступные модели
        dialog_models = get_available_models("dialog")
        code_models = get_available_models("code")
        
        print(f"✓ Найдено {len(dialog_models)} моделей для диалогов")
        print(f"✓ Найдено {len(code_models)} моделей для кода")
        
        # Проверяем, что есть модели от обоих провайдеров
        gemini_models = [m for m in dialog_models if m["provider"] == "gemini"]
        openrouter_models = [m for m in dialog_models if m["provider"] == "openrouter"]
        
        assert len(gemini_models) > 0
        assert len(openrouter_models) > 0
        print("✓ Модели от обоих провайдеров присутствуют")
        
    finally:
        # Восстанавливаем оригинальные переменные окружения
        if original_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = original_gemini_key
        elif "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            
        if original_openrouter_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_openrouter_key
        elif "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
    
    print("Тест 5 пройден успешно!\n")

def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск тестов для функциональности переключения провайдеров...\n")
    
    try:
        test_usage_tracker_provider_switching()
        test_soft_blacklist()
        test_api_key_handling()
        test_state_persistence()
        test_model_availability()
        
        print("🎉 Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)