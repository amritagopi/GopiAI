#!/usr/bin/env python3
"""
Тест связи между UI и API сервером
"""

import sys
import os
import requests
import json
from pathlib import Path

# Добавляем пути для импорта UI модулей
current_dir = Path(__file__).parent
gopiai_ui_dir = current_dir / "GopiAI-UI"
sys.path.insert(0, str(gopiai_ui_dir))

def test_api_connection():
    """Тестирование прямого подключения к API"""
    print("=== Тест подключения к API серверу ===")
    
    # Проверка здоровья сервера
    try:
        response = requests.get("http://127.0.0.1:5052/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API сервер доступен")
            print(f"📊 Ответ: {response.json()}")
        else:
            print(f"❌ Сервер вернул код {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False
    
    # Тест отправки сообщения
    print("\n=== Тест отправки сообщения ===")
    test_message = "Тестовое сообщение из автотеста UI-API связи"
    
    try:
        # Отправляем задачу
        payload = {"message": test_message}
        response = requests.post(
            "http://127.0.0.1:5052/api/process",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 202:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ Задача отправлена, ID: {task_id}")
            
            # Ждем обработки и получаем результат
            import time
            print("⏳ Ожидание обработки...")
            time.sleep(6)
            
            status_response = requests.get(f"http://127.0.0.1:5052/api/task/{task_id}")
            if status_response.status_code == 200:
                task_result = status_response.json()
                print(f"📝 Статус: {task_result.get('status')}")
                if task_result.get('result'):
                    print(f"💬 Ответ AI: {task_result.get('result')}")
                    print("✅ Тест связи UI ↔ API прошел успешно!")
                    return True
                else:
                    print("❌ Нет результата от AI")
            else:
                print(f"❌ Ошибка получения статуса: {status_response.status_code}")
        else:
            print(f"❌ Ошибка отправки: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    return False

def test_crewai_client():
    """Тестирование CrewAI клиента"""
    print("\n=== Тест CrewAI клиента ===")
    
    try:
        # Настройка путей
        os.environ['PYTHONPATH'] = str(gopiai_ui_dir) + ":" + os.environ.get('PYTHONPATH', '')
        
        # Импорт клиента
        from gopiai.ui.components.crewai_client import CrewAIClient
        
        # Инициализация клиента
        client = CrewAIClient(base_url="http://127.0.0.1:5052")
        
        # Проверка подключения
        if client.check_server_connection():
            print("✅ CrewAI клиент подключился успешно")
            
            # Тест отправки сообщения через клиент
            test_message = "Привет от CrewAI клиента!"
            result = client.process_message(test_message)
            
            if result and result.get('status') == 'success':
                print(f"💬 Ответ через клиент: {result.get('response')}")
                print("✅ CrewAI клиент работает!")
                return True
            else:
                print("❌ Клиент не получил корректный ответ")
        else:
            print("❌ CrewAI клиент не смог подключиться")
    except Exception as e:
        print(f"❌ Ошибка CrewAI клиента: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    print("🔄 Запуск тестов связи UI ↔ API")
    print("=" * 50)
    
    # Устанавливаем порт для клиента
    os.makedirs(os.path.expanduser("~/.gopiai"), exist_ok=True)
    with open(os.path.expanduser("~/.gopiai/crewai_server_port.txt"), "w") as f:
        f.write("5052")
    
    api_ok = test_api_connection()
    client_ok = test_crewai_client()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print(f"  🔗 Прямое API подключение: {'✅ РАБОТАЕТ' if api_ok else '❌ НЕ РАБОТАЕТ'}")
    print(f"  🤖 CrewAI клиент: {'✅ РАБОТАЕТ' if client_ok else '❌ НЕ РАБОТАЕТ'}")
    
    if api_ok:
        print("\n🎉 Базовая связь UI ↔ API настроена и работает!")
        print("✅ Можно переходить к тестированию полного UI")
    else:
        print("\n❌ Требуется исправление API связи перед продолжением")