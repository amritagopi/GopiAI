#!/usr/bin/env python3
"""
Тест системы ротации моделей при перегрузке и ошибках
Проверяет автоматическое переключение между моделями
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:5052"

def log_with_timestamp(message):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_normal_request():
    """Тест обычного запроса"""
    log_with_timestamp("🧪 Тест 1: Обычный запрос")
    
    payload = {
        "message": "привет, как дела?",
        "use_refinement": False,
        "max_iterations": 1
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/iterate", 
                               json=payload, 
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            log_with_timestamp("✅ Обычный запрос прошел успешно")
            log_with_timestamp(f"📝 Ответ: {data.get('final_response', '')[:100]}...")
        else:
            log_with_timestamp(f"❌ Ошибка запроса: {response.status_code}")
            log_with_timestamp(f"📝 Ответ: {response.text[:200]}...")
    except Exception as e:
        log_with_timestamp(f"❌ Исключение при запросе: {e}")

def test_model_availability():
    """Проверяем доступность разных моделей"""
    log_with_timestamp("🧪 Тест 2: Проверка доступности моделей")
    
    # Вызовем несколько запросов подряд, чтобы увидеть ротацию
    for i in range(3):
        log_with_timestamp(f"📤 Запрос {i+1}/3")
        payload = {
            "message": f"тестовый запрос номер {i+1}",
            "use_refinement": False,
            "max_iterations": 1
        }
        
        try:
            response = requests.post(f"{API_BASE}/api/iterate", 
                                   json=payload, 
                                   timeout=20)
            if response.status_code == 200:
                data = response.json()
                log_with_timestamp(f"✅ Запрос {i+1} успешен")
            else:
                log_with_timestamp(f"⚠️ Запрос {i+1} завершился с кодом {response.status_code}")
        except requests.exceptions.Timeout:
            log_with_timestamp(f"⏱️ Запрос {i+1} превысил время ожидания")
        except Exception as e:
            log_with_timestamp(f"❌ Ошибка в запросе {i+1}: {e}")
        
        # Небольшая пауза между запросами
        time.sleep(2)

def test_concurrent_requests():
    """Тест параллельных запросов для проверки ротации под нагрузкой"""
    log_with_timestamp("🧪 Тест 3: Параллельные запросы")
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    
    def send_request(request_id):
        payload = {
            "message": f"параллельный запрос #{request_id}",
            "use_refinement": False,
            "max_iterations": 1
        }
        
        try:
            response = requests.post(f"{API_BASE}/api/iterate", 
                                   json=payload, 
                                   timeout=15)
            results_queue.put((request_id, "success" if response.status_code == 200 else f"error_{response.status_code}"))
        except Exception as e:
            results_queue.put((request_id, f"exception_{type(e).__name__}"))
    
    # Запускаем 5 параллельных запросов
    threads = []
    for i in range(5):
        thread = threading.Thread(target=send_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Ждём завершения всех потоков
    for thread in threads:
        thread.join()
    
    # Собираем результаты
    log_with_timestamp("📊 Результаты параллельных запросов:")
    while not results_queue.empty():
        request_id, result = results_queue.get()
        log_with_timestamp(f"  Запрос {request_id}: {result}")

def test_health_check():
    """Проверка здоровья сервера"""
    log_with_timestamp("🧪 Тест 4: Проверка здоровья сервера")
    
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_with_timestamp(f"✅ Сервер здоров: {data}")
        else:
            log_with_timestamp(f"⚠️ Проблемы со здоровьем сервера: {response.status_code}")
    except Exception as e:
        log_with_timestamp(f"❌ Не удалось проверить здоровье сервера: {e}")

def main():
    """Основная функция тестирования"""
    log_with_timestamp("🚀 Запуск тестов системы ротации моделей")
    log_with_timestamp("="*60)
    
    # Проверяем доступность сервера
    test_health_check()
    print()
    
    # Тест обычного запроса
    test_normal_request()
    print()
    
    # Тест доступности моделей
    test_model_availability()
    print()
    
    # Тест параллельных запросов
    test_concurrent_requests()
    print()
    
    log_with_timestamp("✅ Тестирование завершено")
    log_with_timestamp("="*60)
    log_with_timestamp("💡 Проверьте логи сервера для деталей ротации моделей")

if __name__ == "__main__":
    main()