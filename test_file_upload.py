#!/usr/bin/env python3
"""
Тест загрузки файлов с base64 кодированием
"""

import base64
import requests
import time
import json

def test_file_upload():
    """Тестирование загрузки файла"""
    print("🧪 Тест загрузки файла с base64 конверсией")
    
    # Подготовка файла
    test_file_path = "test_file.txt"
    with open(test_file_path, 'rb') as f:
        content = f.read()
        encoded = base64.b64encode(content).decode('utf-8')
    
    # Подготовка запроса
    payload = {
        "message": "Тестирую загрузку файла в GopiAI UI",
        "files": [
            {
                "name": "test_file.txt",
                "content": encoded,
                "type": "text"
            }
        ]
    }
    
    try:
        # Отправка запроса
        print(f"📤 Отправка файла {test_file_path} (размер base64: {len(encoded)} символов)")
        response = requests.post(
            "http://127.0.0.1:5052/api/process",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 202:
            result = response.json()
            task_id = result.get('task_id')
            print(f"✅ Файл отправлен, task_id: {task_id}")
            
            # Ждем обработки
            print("⏳ Ожидание обработки...")
            time.sleep(8)
            
            # Получаем результат
            status_response = requests.get(f"http://127.0.0.1:5052/api/task/{task_id}")
            if status_response.status_code == 200:
                task_result = status_response.json()
                print(f"📊 Статус: {task_result.get('status')}")
                if task_result.get('result'):
                    print(f"💬 Ответ сервера:")
                    print(task_result.get('result'))
                    print("\n✅ Тест загрузки файла успешно завершен!")
                    return True
                else:
                    print("❌ Нет результата от сервера")
            else:
                print(f"❌ Ошибка получения статуса: {status_response.status_code}")
        else:
            print(f"❌ Ошибка отправки: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    return False

if __name__ == "__main__":
    success = test_file_upload()
    print(f"\n{'🎉 ТЕСТ ПРОШЕЛ' if success else '❌ ТЕСТ НЕ ПРОШЕЛ'}")