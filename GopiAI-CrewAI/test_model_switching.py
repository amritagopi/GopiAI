#!/usr/bin/env python3
"""
Тестовый скрипт для проверки переключения провайдеров и моделей
"""

import os
import sys
import requests
import json
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()
load_dotenv(dotenv_path=project_root / ".env")

# Конфигурация
BASE_URL = "http://localhost:5051"
TEST_TIMEOUT = 10

def test_api_connection():
    """Проверяет подключение к API"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ API connection: OK")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   RAG Status: {data.get('rag_status', 'unknown')}")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_get_current_state():
    """Проверяет получение текущего состояния"""
    try:
        response = requests.get(f"{BASE_URL}/internal/state", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            state = response.json()
            print("✅ Get current state: OK")
            print(f"   Provider: {state.get('provider', 'unknown')}")
            print(f"   Model ID: {state.get('model_id', 'unknown')}")
            return state
        else:
            print(f"❌ Get current state failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get current state error: {e}")
        return None

def test_update_state(provider, model_id):
    """Проверяет обновление состояния"""
    try:
        payload = {
            "provider": provider,
            "model_id": model_id
        }
        response = requests.post(f"{BASE_URL}/internal/state", 
                               json=payload, 
                               timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Update state to {provider}: OK")
            print(f"   Message: {result.get('message', 'no message')}")
            return True
        else:
            print(f"❌ Update state to {provider} failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update state to {provider} error: {e}")
        return False

def test_get_models_by_provider(provider):
    """Проверяет получение моделей по провайдеру"""
    try:
        response = requests.get(f"{BASE_URL}/internal/models?provider={provider}", 
                              timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Get models for {provider}: OK")
            print(f"   Available models: {len(models)}")
            if models:
                for model in models[:3]:  # Показываем первые 3 модели
                    print(f"     - {model.get('display_name', 'unknown')} ({model.get('id', 'unknown')})")
            return models
        else:
            print(f"❌ Get models for {provider} failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get models for {provider} error: {e}")
        return None

def test_simple_request():
    """Проверяет простой запрос к API"""
    try:
        payload = {
            "message": "Привет! Как дела?",
            "metadata": {}
        }
        response = requests.post(f"{BASE_URL}/api/process", 
                               json=payload, 
                               timeout=30)  # Больше времени для обработки
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple request: OK")
            print(f"   Task ID: {result.get('task_id', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            return result.get('task_id')
        else:
            print(f"❌ Simple request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Simple request error: {e}")
        return None

def test_task_status(task_id):
    """Проверяет статус задачи"""
    if not task_id:
        return
        
    try:
        response = requests.get(f"{BASE_URL}/api/task/{task_id}", 
                              timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            status = response.json()
            print("✅ Task status check: OK")
            print(f"   Status: {status.get('status', 'unknown')}")
            if status.get('status') == 'completed':
                print(f"   Response length: {len(str(status.get('result', '')))} characters")
            elif status.get('status') == 'failed':
                print(f"   Error: {status.get('error', 'unknown')}")
            return status
        else:
            print(f"❌ Task status check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Task status check error: {e}")
        return None

def main():
    """Основная функция тестирования"""
    print("🧪 GopiAI Model Switching System Test")
    print("=" * 50)
    
    # Проверяем API подключение
    if not test_api_connection():
        print("\n❌ API connection failed. Make sure the server is running.")
        return
    
    print()
    
    # Проверяем текущее состояние
    current_state = test_get_current_state()
    print()
    
    # Тестируем получение моделей для Gemini
    print("📋 Testing Gemini models...")
    gemini_models = test_get_models_by_provider("gemini")
    print()
    
    # Тестируем получение моделей для OpenRouter
    print("📋 Testing OpenRouter models...")
    openrouter_models = test_get_models_by_provider("openrouter")
    print()
    
    # Тестируем переключение на OpenRouter
    print("🔄 Testing provider switching...")
    if openrouter_models and len(openrouter_models) > 0:
        first_openrouter_model = openrouter_models[0]
        test_update_state("openrouter", first_openrouter_model["id"])
        print()
        
        # Проверяем новое состояние
        test_get_current_state()
        print()
    
    # Тестируем переключение обратно на Gemini
    if gemini_models and len(gemini_models) > 0:
        first_gemini_model = gemini_models[0]
        test_update_state("gemini", first_gemini_model["id"])
        print()
        
        # Проверяем новое состояние
        test_get_current_state()
        print()
    
    # Тестируем простой запрос
    print("💬 Testing simple request...")
    task_id = test_simple_request()
    print()
    
    # Если задача создана, проверяем её статус
    if task_id:
        print("⏳ Waiting for task completion...")
        import time
        time.sleep(3)  # Ждем немного
        
        test_task_status(task_id)
        print()
    
    print("🎯 Testing completed!")

if __name__ == "__main__":
    main()
