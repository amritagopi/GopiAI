#!/usr/bin/env python3
"""
Гид по миграции на новую систему переключения провайдеров
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def backup_file(file_path):
    """Создает резервную копию файла"""
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    return None

def migrate_env_file():
    """Мигрирует .env файл"""
    env_path = project_root / ".env"
    if not env_path.exists():
        print("⚠️  .env file not found, creating new one...")
        env_content = """# GopiAI Model Switching System - API Keys
# Generated on {}

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter API  
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Other API keys (optional)
# BRAVE_API_KEY=your_brave_api_key_here
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        env_path.write_text(env_content)
        print("✅ New .env file created")
        return True
    
    # Проверяем существующие ключи
    content = env_path.read_text()
    lines = content.splitlines()
    
    required_keys = {
        'GEMINI_API_KEY': 'Google Gemini API key',
        'OPENROUTER_API_KEY': 'OpenRouter API key',
        'OPENROUTER_API_BASE': 'https://openrouter.ai/api/v1'
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        if not any(line.startswith(f"{key}=") for line in lines):
            missing_keys.append((key, description))
    
    if missing_keys:
        print("⚠️  Missing required API keys in .env:")
        for key, description in missing_keys:
            print(f"   - {key}: {description}")
        return False
    
    print("✅ .env file is properly configured")
    return True

def migrate_state_file():
    """Мигрирует файл состояния"""
    state_path = Path.home() / ".gopiai_state.json"
    
    if state_path.exists():
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Проверяем структуру
            required_fields = ['provider', 'model_id']
            missing_fields = [field for field in required_fields if field not in state]
            
            if missing_fields:
                print(f"⚠️  State file missing fields: {missing_fields}")
                # Обновляем структуру
                state.setdefault('provider', 'gemini')
                state.setdefault('model_id', 'gemini/gemini-1.5-flash')
                
                backup_file(state_path)
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                print("✅ State file structure updated")
            else:
                print("✅ State file is properly configured")
                
        except Exception as e:
            print(f"❌ Error reading state file: {e}")
            return False
    else:
        # Создаем новый файл состояния
        default_state = {
            "provider": "gemini",
            "model_id": "gemini/gemini-1.5-flash"
        }
        
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(default_state, f, indent=2, ensure_ascii=False)
        print("✅ New state file created")
    
    return True

def check_old_files():
    """Проверяет наличие старых файлов, которые нужно удалить"""
    old_files = [
        "old_llm_config.py",
        "legacy_model_selector.py",
        "deprecated_api_keys.txt"
    ]
    
    found_old_files = []
    for file_name in old_files:
        file_path = project_root / file_name
        if file_path.exists():
            found_old_files.append(file_path)
    
    if found_old_files:
        print("⚠️  Found old files that should be removed:")
        for file_path in found_old_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ No old deprecated files found")
    return True

def update_imports_in_code():
    """Обновляет импорты в коде (если нужно)"""
    # В новой системе импорты остаются теми же:
    # from gopiai_integration.llm_rotation_config import ...
    print("ℹ️  Import paths remain unchanged:")
    print("   from gopiai_integration.llm_rotation_config import select_llm_model_safe")
    print("   from gopiai_integration.llm_rotation_config import get_available_models")
    print("   from gopiai_integration.llm_rotation_config import register_use")
    return True

def run_compatibility_tests():
    """Запускает тесты совместимости"""
    try:
        # Импортируем основные модули
        from llm_rotation_config import select_llm_model_safe, get_available_models, register_use
        from state_manager import load_state, save_state
        
        # Тестируем базовую функциональность
        models = get_available_models("dialog")
        print(f"✅ Available models: {len(models)}")
        
        if models:
            first_model = models[0]
            print(f"✅ First model: {first_model['display_name']} ({first_model['id']})")
        
        # Тестируем выбор модели
        selected_model = select_llm_model_safe("dialog")
        print(f"✅ Model selection: {selected_model}")
        
        # Тестируем состояние
        state = load_state()
        print(f"✅ Current state: provider={state.get('provider')}, model={state.get('model_id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False

def main():
    """Основная функция миграции"""
    print("🔄 GopiAI Model Switching System - Migration Guide")
    print("=" * 60)
    print("This guide will help you migrate to the new provider switching system.")
    print()
    
    steps = [
        ("Environment Configuration", migrate_env_file),
        ("State File Migration", migrate_state_file),
        ("Old Files Check", check_old_files),
        ("Import Paths", update_imports_in_code),
        ("Compatibility Tests", run_compatibility_tests)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        print("-" * 40)
        
        try:
            success = step_func()
            results.append((step_name, success))
            
            if success:
                print(f"✅ {step_name} completed")
            else:
                print(f"⚠️  {step_name} requires attention")
                
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            results.append((step_name, False))
    
    # Выводим сводку
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    
    completed = 0
    needs_attention = 0
    failed = 0
    
    for step_name, success in results:
        if success:
            status = "✅"
            completed += 1
        else:
            status = "⚠️"
            needs_attention += 1
        print(f"{status} {step_name}")
    
    print("-" * 60)
    print(f"Steps: {len(results)} | Completed: {completed} | Attention: {needs_attention}")
    
    if needs_attention == 0:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the new model switching system.")
    else:
        print(f"\n⚠️  {needs_attention} step(s) require your attention.")
        print("Please review the warnings above and take necessary actions.")
    
    print("\n💡 Quick Start:")
    print("   1. Run 'python start_model_switching_system.py'")
    print("   2. Use the UI widget to switch providers")
    print("   3. Or use the REST API endpoints directly")
    
    return 0 if needs_attention == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
