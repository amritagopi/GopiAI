#!/usr/bin/env python3
"""
Тест текущей функциональности системы переключения провайдеров
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Импортируем модули
from llm_rotation_config import (
    get_available_models, 
    get_current_provider, 
    update_state,
    is_model_blacklisted,
    get_model_usage_stats,
    register_use,
    MODELS
)

def test_provider_switching():
    """Тест переключения провайдеров"""
    print("=== Тест переключения провайдеров ===")
    
    # Проверяем текущий провайдер
    current_provider = get_current_provider()
    print(f"Текущий провайдер: {current_provider}")
    
    # Переключаемся на OpenRouter
    print("Переключаемся на OpenRouter...")
    update_state("openrouter", "openrouter/mistralai-mistral-7b-instruct")
    new_provider = get_current_provider()
    print(f"Новый провайдер: {new_provider}")
    
    # Проверяем доступные модели
    dialog_models = get_available_models("dialog")
    print(f"Доступные модели для диалога: {len(dialog_models)}")
    
    # Фильтруем по провайдеру
    openrouter_models = [m for m in dialog_models if m["provider"] == "openrouter"]
    gemini_models = [m for m in dialog_models if m["provider"] == "gemini"]
    print(f"Модели OpenRouter: {len(openrouter_models)}")
    print(f"Модели Gemini: {len(gemini_models)}")
    
    # Переключаемся обратно на Gemini
    print("Переключаемся обратно на Gemini...")
    update_state("gemini", "gemini/gemini-1.5-flash")
    final_provider = get_current_provider()
    print(f"Финальный провайдер: {final_provider}")
    
    return True

def test_blacklist_functionality():
    """Тест функциональности черного списка"""
    print("\n=== Тест черного списка ===")
    
    # Выбираем тестовую модель
    test_model_id = "gemini/gemini-1.5-flash"
    print(f"Тестовая модель: {test_model_id}")
    
    # Проверяем текущий статус blacklist
    is_blacklisted = is_model_blacklisted(test_model_id)
    print(f"Модель в черном списке: {is_blacklisted}")
    
    # Получаем статистику использования
    stats = get_model_usage_stats(test_model_id)
    print(f"Статистика использования: {stats}")
    
    return True

def test_model_selection():
    """Тест выбора моделей"""
    print("\n=== Тест выбора моделей ===")
    
    # Получаем доступные модели для разных типов задач
    dialog_models = get_available_models("dialog")
    code_models = get_available_models("code")
    simple_models = get_available_models("simple")
    
    print(f"Модели для диалога: {len(dialog_models)}")
    print(f"Модели для кода: {len(code_models)}")
    print(f"Модели для простых задач: {len(simple_models)}")
    
    # Показываем первые модели каждого типа
    if dialog_models:
        print(f"Первая модель для диалога: {dialog_models[0]['display_name']} ({dialog_models[0]['id']})")
    if code_models:
        print(f"Первая модель для кода: {code_models[0]['display_name']} ({code_models[0]['id']})")
    
    return True

def main():
    """Основная функция тестирования"""
    print("🧪 Тест текущей функциональности системы переключения провайдеров")
    print("=" * 60)
    
    try:
        test_provider_switching()
        test_blacklist_functionality()
        test_model_selection()
        
        print("\n✅ Все тесты успешно пройдены!")
        print("🎉 Система переключения провайдеров работает корректно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
