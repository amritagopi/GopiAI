#!/usr/bin/env python3
"""
Скрипт для переключения между бесплатными моделями OpenRouter
в случае rate limit или других проблем.
"""

import json
import time
import sys
from pathlib import Path

def load_config():
    """Загружает конфигурацию моделей"""
    config_path = Path("GopiAI-CrewAI/tools/model_configurations.json")
    if not config_path.exists():
        print(f"❌ Файл конфигурации не найден: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Сохраняет конфигурацию моделей"""
    config_path = Path("GopiAI-CrewAI/tools/model_configurations.json")
    config["last_updated"] = str(time.time())
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_free_models(config):
    """Получает список всех бесплатных моделей"""
    free_models = []
    for key, model in config["configurations"].items():
        if model["model_id"].endswith(":free") and model["provider"] == "openrouter":
            free_models.append({
                "key": key,
                "model_id": model["model_id"],
                "display_name": model["display_name"],
                "is_active": model["is_active"],
                "is_default": model["is_default"]
            })
    return free_models

def switch_to_next_model(config):
    """Переключается на следующую доступную бесплатную модель"""
    free_models = get_free_models(config)
    current_model = config["current"]["model_id"]
    
    print(f"🔄 Текущая модель: {current_model}")
    
    # Найдем индекс текущей модели
    current_index = -1
    for i, model in enumerate(free_models):
        if model["model_id"] == current_model:
            current_index = i
            break
    
    if current_index == -1:
        print("⚠️ Текущая модель не найдена среди бесплатных")
        next_index = 0
    else:
        next_index = (current_index + 1) % len(free_models)
    
    next_model = free_models[next_index]
    
    # Деактивируем все модели
    for key, model in config["configurations"].items():
        if model["provider"] == "openrouter" and model["model_id"].endswith(":free"):
            model["is_active"] = False
            model["is_default"] = False
    
    # Активируем новую модель
    config["configurations"][next_model["key"]]["is_active"] = True
    config["configurations"][next_model["key"]]["is_default"] = True
    config["current"]["model_id"] = next_model["model_id"]
    
    print(f"✅ Переключено на: {next_model['display_name']}")
    print(f"🆔 Model ID: {next_model['model_id']}")
    
    return next_model

def list_free_models(config):
    """Показывает список всех бесплатных моделей"""
    free_models = get_free_models(config)
    current_model = config["current"]["model_id"]
    
    print("📋 Доступные бесплатные модели:")
    print("=" * 80)
    
    for i, model in enumerate(free_models, 1):
        status = "🟢 АКТИВНА" if model["model_id"] == current_model else "⚪ Доступна"
        print(f"{i:2d}. {status}")
        print(f"    ID: {model['model_id']}")
        print(f"    Название: {model['display_name']}")
        print()

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python switch_free_model.py list    - показать все бесплатные модели")
        print("  python switch_free_model.py switch  - переключиться на следующую модель")
        print("  python switch_free_model.py set <model_id> - установить конкретную модель")
        sys.exit(1)
    
    command = sys.argv[1]
    config = load_config()
    
    if command == "list":
        list_free_models(config)
    
    elif command == "switch":
        next_model = switch_to_next_model(config)
        save_config(config)
        print("💾 Конфигурация сохранена")
        print("🔄 Перезапустите сервер CrewAI для применения изменений")
    
    elif command == "set" and len(sys.argv) > 2:
        target_model = sys.argv[2]
        free_models = get_free_models(config)
        
        found = False
        for model in free_models:
            if model["model_id"] == target_model:
                # Деактивируем все модели
                for key, cfg in config["configurations"].items():
                    if cfg["provider"] == "openrouter" and cfg["model_id"].endswith(":free"):
                        cfg["is_active"] = False
                        cfg["is_default"] = False
                
                # Активируем целевую модель
                config["configurations"][model["key"]]["is_active"] = True
                config["configurations"][model["key"]]["is_default"] = True
                config["current"]["model_id"] = target_model
                
                save_config(config)
                print(f"✅ Установлена модель: {model['display_name']}")
                print("💾 Конфигурация сохранена")
                print("🔄 Перезапустите сервер CrewAI для применения изменений")
                found = True
                break
        
        if not found:
            print(f"❌ Модель {target_model} не найдена среди бесплатных")
            print("Используйте 'list' для просмотра доступных моделей")
    
    else:
        print("❌ Неизвестная команда")
        sys.exit(1)

if __name__ == "__main__":
    main()