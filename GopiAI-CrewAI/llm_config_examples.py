#!/usr/bin/env python3
"""
Примеры использования расширенной конфигурации LLM
Демонстрирует работу с новыми полями: rpd, deprecated, base_score
"""

from llm_rotation_config import (
    LLM_MODELS_CONFIG,
    get_active_models,
    get_models_by_intelligence,
    update_model_deprecated_status,
    get_model_usage_stats,
    select_llm_model_safe
)

def demo_new_features():
    """Демонстрация новых возможностей конфигурации"""
    
    print("🔧 Демонстрация расширенной конфигурации LLM")
    print("=" * 50)
    
    # 1. Показать все активные модели
    print("\n📋 Активные модели:")
    active_models = get_active_models()
    for model in active_models:
        print(f"  - {model['name']} (base_score: {model['base_score']}, deprecated: {model['deprecated']})")
    
    # 2. Модели с высоким интеллектом
    print("\n🧠 Модели с высоким интеллектом (base_score >= 0.7):")
    smart_models = get_models_by_intelligence(0.7)
    if smart_models:
        for model in smart_models:
            print(f"  - {model['name']} (base_score: {model['base_score']})")
    else:
        print("  Нет моделей с base_score >= 0.7")
    
    # 3. Пометить модель как deprecated
    print("\n⚠️ Помечаем старую модель как deprecated:")
    result = update_model_deprecated_status("gemini/gemma-3", deprecated=True)
    if result:
        print("  Статус успешно обновлен")
    
    # 4. Показать статистику использования
    print("\n📊 Статистика использования моделей:")
    for model in LLM_MODELS_CONFIG[:3]:  # Показываем первые 3 модели
        stats = get_model_usage_stats(model["id"])
        if stats:
            print(f"  {model['name']}:")
            print(f"    RPM: {stats['rpm_used']}/{stats['rpm_limit']}")
            print(f"    TPM: {stats['tpm_used']}/{stats['tpm_limit']}")
            print(f"    Base Score: {stats['base_score']}")
            print(f"    Deprecated: {stats['deprecated']}")
    
    # 5. Выбор модели с приоритетом интеллекта
    print("\n🎯 Выбор модели для задачи 'dialog':")
    
    # Обычный выбор по приоритету
    normal_choice = select_llm_model_safe("dialog", tokens=1000)
    print(f"  Обычный выбор: {normal_choice}")
    
    # Выбор с приоритетом интеллекта
    smart_choice = select_llm_model_safe("dialog", tokens=1000, intelligence_priority=True)
    print(f"  С приоритетом интеллекта: {smart_choice}")

def demo_advanced_scoring():
    """Демонстрация работы с base_score для разных типов задач"""
    
    print("\n🎯 Настройка base_score для разных типов задач")
    print("=" * 50)
    
    # Обновляем base_score для разных моделей в зависимости от их назначения
    model_scores = {
        "gemini/gemma-3": 0.3,          # Простая модель
        "gemini/gemma-3n": 0.4,         # Чуть лучше
        "gemini/gemini-1.5-flash": 0.6,  # Средний уровень
        "gemini/gemini-2.0-flash-lite": 0.7,  # Хорошая модель
        "gemini/gemini-2.5-flash-lite-preview": 0.8,  # Очень хорошая
        "gemini/gemini-2.5-flash": 0.9,  # Топовая модель
        "gemini/gemini-embedding-experimental": 0.5  # Для embedding
    }
    
    # Обновляем конфигурацию
    for model in LLM_MODELS_CONFIG:
        if model["id"] in model_scores:
            model["base_score"] = model_scores[model["id"]]
            print(f"✅ Обновлен base_score для {model['name']}: {model['base_score']}")

def demo_rpd_limits():
    """Демонстрация работы с дневными лимитами (RPD)"""
    
    print("\n📅 Настройка дневных лимитов (RPD)")
    print("=" * 50)
    
    # Устанавливаем дневные лимиты для разных моделей
    rpd_limits = {
        "gemini/gemma-3": 1000,         # Много запросов для простой модели
        "gemini/gemma-3n": 800,         
        "gemini/gemini-1.5-flash": 500,  
        "gemini/gemini-2.0-flash-lite": 300,  
        "gemini/gemini-2.5-flash-lite-preview": 200,  
        "gemini/gemini-2.5-flash": 100,  # Мало запросов для дорогой модели
        "gemini/gemini-embedding-experimental": 2000  # Много для embedding
    }
    
    # Обновляем конфигурацию
    for model in LLM_MODELS_CONFIG:
        if model["id"] in rpd_limits:
            model["rpd"] = rpd_limits[model["id"]]
            print(f"📊 Установлен RPD лимит для {model['name']}: {model['rpd']} запросов/день")

def demo_environment_keys():
    """Демонстрация работы с разными ключами для тест/прод"""
    
    print("\n🔑 Работа с разными API ключами для тест/прод")
    print("=" * 50)
    
    import os
    from llm_rotation_config import get_api_key_for_provider
    
    # Показываем, как система выбирает ключи
    print("Текущая среда:", os.getenv("ENVIRONMENT", "production"))
    
    # Имитируем разные среды
    for env in ["test", "production", None]:
        os.environ["ENVIRONMENT"] = env if env else ""
        key = get_api_key_for_provider("google")
        suffix = "_TEST" if env == "test" else ""
        expected_var = f"GEMINI_API_KEY{suffix}"
        print(f"  Среда '{env}': ищем переменную {expected_var}")
        if key:
            print(f"    ✅ Ключ найден: {key[:10]}...")
        else:
            print(f"    ❌ Ключ не найден")

if __name__ == "__main__":
    # Запускаем демонстрацию
    try:
        demo_new_features()
        demo_advanced_scoring()
        demo_rpd_limits()
        demo_environment_keys()
        
        print("\n✅ Демонстрация завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()
