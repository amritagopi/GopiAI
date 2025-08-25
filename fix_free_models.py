#!/usr/bin/env python3
"""
Скрипт для добавления атрибута is_free ко всем бесплатным моделям
в конфигурации model_configurations.json
"""

import json
import time
from pathlib import Path

def fix_free_models():
    """Добавляет атрибут is_free ко всем моделям с :free в model_id"""
    config_path = Path("GopiAI-CrewAI/tools/model_configurations.json")
    
    if not config_path.exists():
        print(f"❌ Файл конфигурации не найден: {config_path}")
        return False
    
    # Загружаем конфигурацию
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    modified_count = 0
    free_models = []
    
    # Проходим по всем конфигурациям
    for key, model_config in config["configurations"].items():
        model_id = model_config.get("model_id", "")
        
        # Определяем, является ли модель бесплатной
        is_free = model_id.endswith(":free")
        
        # Добавляем атрибут is_free, если его нет
        if "is_free" not in model_config:
            model_config["is_free"] = is_free
            modified_count += 1
            
            if is_free:
                free_models.append({
                    "key": key,
                    "model_id": model_id,
                    "display_name": model_config.get("display_name", "Unknown")
                })
        elif model_config["is_free"] != is_free:
            # Исправляем неправильное значение
            model_config["is_free"] = is_free
            modified_count += 1
            
            if is_free:
                free_models.append({
                    "key": key,
                    "model_id": model_id,
                    "display_name": model_config.get("display_name", "Unknown")
                })
    
    if modified_count > 0:
        # Обновляем timestamp
        config["last_updated"] = str(time.time())
        
        # Сохраняем конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Обновлено {modified_count} моделей")
        print(f"🆓 Найдено {len(free_models)} бесплатных моделей:")
        
        for model in free_models[:10]:  # Показываем первые 10
            print(f"   • {model['display_name']}")
            print(f"     ID: {model['model_id']}")
        
        if len(free_models) > 10:
            print(f"   ... и еще {len(free_models) - 10} моделей")
        
        print("💾 Конфигурация сохранена")
        return True
    else:
        print("ℹ️ Все модели уже имеют корректный атрибут is_free")
        return False

if __name__ == "__main__":
    fix_free_models()