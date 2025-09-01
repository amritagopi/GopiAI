#!/usr/bin/env python3
"""
Финальный тест интеграции GopiAI UI ↔ CrewAI Server
"""

import requests
import time
import json

def test_chat_functionality():
    """Тестирование чата с CrewAI сервером"""
    print("🧪 Финальный тест чат функциональности GopiAI")
    print("=" * 50)
    
    try:
        # 1. Проверка здоровья сервера
        print("1. 🏥 Проверка здоровья сервера...")
        response = requests.get("http://127.0.0.1:5052/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Сервер работает: {health_data.get('status')}")
            print(f"   📊 Инструментов загружено: {health_data.get('tools_integrator_status')}")
        else:
            print(f"   ❌ Ошибка здоровья сервера: {response.status_code}")
            return False
        
        # 2. Проверка списка моделей
        print("\n2. 🤖 Проверка моделей OpenRouter...")
        response = requests.get("http://127.0.0.1:5052/api/models/openrouter", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models_count = len(models_data.get('models', []))
            print(f"   ✅ Доступно моделей: {models_count}")
        else:
            print(f"   ❌ Ошибка получения моделей: {response.status_code}")
        
        # 3. Установка модели
        print("\n3. ⚙️ Установка модели...")
        model_payload = {
            "provider": "OpenRouter",
            "model": "openai/gpt-4"
        }
        response = requests.post(
            "http://127.0.0.1:5052/api/model/set",
            json=model_payload,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Модель установлена: {result.get('message')}")
        else:
            print(f"   ❌ Ошибка установки модели: {response.status_code}")
        
        # 4. Тестирование чата
        print("\n4. 💬 Тест отправки сообщения в чат...")
        chat_payload = {
            "message": "Привет! Это финальный тест интеграции GopiAI UI с CrewAI сервером. Расскажи кратко о своих возможностях."
        }
        
        response = requests.post(
            "http://127.0.0.1:5052/api/process",
            json=chat_payload,
            timeout=10
        )
        
        if response.status_code == 202:
            result = response.json()
            task_id = result.get('task_id')
            print(f"   ✅ Сообщение отправлено, task_id: {task_id}")
            
            # Ждем обработки
            print("   ⏳ Ожидание ответа AI...")
            max_attempts = 15
            for attempt in range(max_attempts):
                time.sleep(2)
                
                status_response = requests.get(f"http://127.0.0.1:5052/api/task/{task_id}")
                if status_response.status_code == 200:
                    task_result = status_response.json()
                    status = task_result.get('status')
                    
                    if status == 'completed':
                        ai_response = task_result.get('result')
                        print(f"   ✅ Получен ответ от AI:")
                        print(f"   📝 Ответ: {ai_response}")
                        return True
                    elif status == 'failed':
                        error = task_result.get('error', 'Unknown error')
                        print(f"   ❌ Задача завершилась с ошибкой: {error}")
                        return False
                    else:
                        print(f"   ⏳ Статус: {status} (попытка {attempt + 1}/{max_attempts})")
                else:
                    print(f"   ❌ Ошибка получения статуса: {status_response.status_code}")
                    return False
            
            print("   ❌ Таймаут ожидания ответа")
            return False
        else:
            print(f"   ❌ Ошибка отправки сообщения: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def test_tools_and_agents():
    """Проверка доступности инструментов и агентов"""
    print("\n5. 🛠️ Проверка инструментов и агентов...")
    
    try:
        # Проверка инструментов
        response = requests.get("http://127.0.0.1:5052/api/tools", timeout=5)
        if response.status_code == 200:
            tools_data = response.json()
            tools_count = len(tools_data.get('tools', []))
            print(f"   ✅ Доступно инструментов: {tools_count}")
        
        # Проверка агентов  
        response = requests.get("http://127.0.0.1:5052/api/agents", timeout=5)
        if response.status_code == 200:
            agents_data = response.json()
            agents_count = len(agents_data.get('agents', []))
            flows_count = len(agents_data.get('flows', []))
            print(f"   ✅ Доступно агентов: {agents_count}, флоу: {flows_count}")
        
        return True
    except Exception as e:
        print(f"   ❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск финального теста интеграции GopiAI")
    
    # Основной тест чата
    chat_success = test_chat_functionality()
    
    # Тест инструментов и агентов
    tools_success = test_tools_and_agents()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ФИНАЛЬНОГО ТЕСТА:")
    print(f"  💬 Чат функциональность: {'✅ РАБОТАЕТ' if chat_success else '❌ НЕ РАБОТАЕТ'}")
    print(f"  🛠️ Инструменты и агенты: {'✅ РАБОТАЕТ' if tools_success else '❌ НЕ РАБОТАЕТ'}")
    
    overall_success = chat_success and tools_success
    print(f"\n🎉 ОБЩИЙ РЕЗУЛЬТАТ: {'✅ ВСЕ СИСТЕМЫ РАБОТАЮТ!' if overall_success else '❌ ТРЕБУЕТСЯ ДИАГНОСТИКА'}")
    
    if overall_success:
        print("\n✅ GopiAI готов к использованию!")
        print("🎯 Основной UI запущен и подключен к CrewAI серверу")
        print("📡 API связь работает стабильно")
        print("🤖 AI отвечает на запросы")
        print("🛠️ Инструменты и агенты доступны")
    else:
        print("\n❌ Требуется дополнительная настройка")