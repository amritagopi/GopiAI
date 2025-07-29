#!/usr/bin/env python3
"""
Скрипт для запуска системы переключения провайдеров
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_api_key(env_var, service_name):
    """Проверяет наличие API ключа"""
    key = os.getenv(env_var)
    if not key:
        print(f"❌ {service_name} API key not found in environment variables")
        return False
    print(f"✅ {service_name} API key found")
    return True

def start_crewai_server():
    """Запускает CrewAI сервер"""
    print("🚀 Starting CrewAI API server...")
    
    # Проверяем API ключи
    gemini_ok = check_api_key('GEMINI_API_KEY', 'Gemini')
    openrouter_ok = check_api_key('OPENROUTER_API_KEY', 'OpenRouter')
    
    if not gemini_ok and not openrouter_ok:
        print("❌ No API keys found. Please set GEMINI_API_KEY and/or OPENROUTER_API_KEY in .env file")
        return False
    
    # Запускаем сервер в отдельном процессе
    try:
        server_process = subprocess.Popen([
            sys.executable, 
            str(project_root / "crewai_api_server.py")
        ], cwd=str(project_root))
        
        print(f"✅ CrewAI server started with PID {server_process.pid}")
        
        # Ждем запуска сервера
        print("⏳ Waiting for server to start...")
        for i in range(30):  # Ждем до 30 секунд
            try:
                response = requests.get("http://localhost:5051/api/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            print(f"⏳ Still waiting... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def test_model_switching():
    """Тестирует переключение провайдеров"""
    print("\n🧪 Testing model switching...")
    
    try:
        # Проверяем текущее состояние
        response = requests.get("http://localhost:5051/internal/state")
        if response.status_code == 200:
            state = response.json()
            print(f"📊 Current state: {state}")
        
        # Тестируем переключение на OpenRouter
        print("\n🔄 Testing switch to OpenRouter...")
        response = requests.post("http://localhost:5051/internal/state", json={
            "provider": "openrouter",
            "model_id": "openrouter/google-gemma-2b-it"
        })
        if response.status_code == 200:
            print("✅ Switched to OpenRouter")
        else:
            print(f"❌ Failed to switch to OpenRouter: {response.text}")
        
        # Проверяем состояние после переключения
        response = requests.get("http://localhost:5051/internal/state")
        if response.status_code == 200:
            state = response.json()
            print(f"📊 New state: {state}")
        
        # Тестируем получение моделей для провайдера
        print("\n📋 Testing model listing...")
        response = requests.get("http://localhost:5051/internal/models?provider=openrouter")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ OpenRouter models: {len(models)} available")
            for model in models[:3]:  # Показываем первые 3 модели
                print(f"  - {model['display_name']} ({model['id']})")
        
        # Тестируем переключение обратно на Gemini
        print("\n🔄 Testing switch back to Gemini...")
        response = requests.post("http://localhost:5051/internal/state", json={
            "provider": "gemini",
            "model_id": "gemini/gemini-1.5-flash"
        })
        if response.status_code == 200:
            print("✅ Switched back to Gemini")
        else:
            print(f"❌ Failed to switch back to Gemini: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def main():
    """Основная функция"""
    print("🚀 GopiAI Model Switching System Startup")
    print("=" * 50)
    
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(dotenv_path=project_root / ".env")
    
    # Запускаем сервер
    if start_crewai_server():
        print("\n✅ System started successfully!")
        
        # Ждем немного и тестируем
        time.sleep(2)
        test_model_switching()
        
        print("\n🎯 System is ready for use!")
        print("💡 You can now use the UI to switch between providers")
        print("💡 Or use the API endpoints:")
        print("   GET  http://localhost:5051/internal/state")
        print("   POST http://localhost:5051/internal/state")
        print("   GET  http://localhost:5051/internal/models?provider={provider}")
    else:
        print("\n❌ Failed to start system")
        sys.exit(1)

if __name__ == "__main__":
    main()
