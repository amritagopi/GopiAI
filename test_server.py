#!/usr/bin/env python3
"""
Минимальный тестовый сервер для проверки связи UI ↔ API
"""

from flask import Flask, request, jsonify
import uuid
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Минимальная имитация TaskStatus
class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

# Минимальная имитация ServerTask
class ServerTask:
    def __init__(self, task_id, message, files_data=None):
        self.task_id = task_id
        self.message = message
        self.files_data = files_data or []
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
    def start_processing(self):
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.now()
        
    def complete(self, result):
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "message": self.message,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

# Глобальное хранилище
TASKS = {}

def process_task(task_id):
    """Фоновая обработка задачи"""
    time.sleep(2)  # Имитация обработки
    task = TASKS.get(task_id)
    if task:
        task.start_processing()
        time.sleep(3)  # Имитация работы AI
        
        # Подготовка ответа
        response_parts = [f"Привет! Получил ваше сообщение: '{task.message}'."]
        
        # Проверяем наличие файлов
        if hasattr(task, 'files_data') and task.files_data:
            response_parts.append(f"\n📎 Обработано файлов: {len(task.files_data)}")
            for file_info in task.files_data:
                file_name = file_info.get('name', 'unknown')
                file_type = file_info.get('type', 'unknown')
                content_length = len(file_info.get('content', ''))
                response_parts.append(f"  - {file_name} (тип: {file_type}, размер base64: {content_length} символов)")
        
        response_parts.append("\nЭто тестовый ответ от минимального сервера.")
        response = "".join(response_parts)
        task.complete(response)

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "server": "test_server",
        "message": "Test server is running"
    })

@app.route('/api/process', methods=['POST'])
def process_message():
    """Обработка сообщения"""
    data = request.get_json()
    message = data.get('message', '')
    files_data = data.get('files', [])
    
    task_id = str(uuid.uuid4())
    task = ServerTask(task_id, message, files_data)
    TASKS[task_id] = task
    
    # Запускаем обработку в фоне
    thread = threading.Thread(target=process_task, args=(task_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "accepted",
        "message": "Task queued for processing"
    }), 202

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Получение статуса задачи"""
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())

# Глобальная переменная для хранения настроек модели
CURRENT_MODEL_SETTINGS = {
    "provider": "OpenRouter",
    "model": "openai/gpt-4"
}

@app.route('/api/models/openrouter', methods=['GET'])
def get_openrouter_models():
    """Получение списка моделей OpenRouter"""
    # В реальном проекте это будет запрос к OpenRouter API
    models = [
        {
            "id": "openai/gpt-4",
            "name": "GPT-4",
            "description": "OpenAI's most capable model"
        },
        {
            "id": "openai/gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo", 
            "description": "Fast and efficient model"
        },
        {
            "id": "anthropic/claude-3-sonnet",
            "name": "Claude 3 Sonnet",
            "description": "Anthropic's balanced model"
        },
        {
            "id": "anthropic/claude-3-haiku",
            "name": "Claude 3 Haiku",
            "description": "Fast and cost-effective"
        },
        {
            "id": "meta-llama/llama-3-8b-instruct",
            "name": "Llama 3 8B",
            "description": "Meta's open source model"
        },
        {
            "id": "google/gemma-2-9b-it",
            "name": "Gemma 2 9B",
            "description": "Google's efficient model"
        }
    ]
    
    return jsonify({
        "status": "success",
        "models": models
    })

@app.route('/api/model/set', methods=['POST'])
def set_model():
    """Установка текущей модели"""
    global CURRENT_MODEL_SETTINGS
    data = request.get_json()
    
    provider = data.get('provider')
    model = data.get('model')
    
    if not provider or not model:
        return jsonify({"error": "Provider and model are required"}), 400
    
    CURRENT_MODEL_SETTINGS['provider'] = provider
    CURRENT_MODEL_SETTINGS['model'] = model
    
    return jsonify({
        "status": "success",
        "message": f"Model set to {provider} / {model}",
        "current_settings": CURRENT_MODEL_SETTINGS
    })

@app.route('/api/model/current', methods=['GET'])
def get_current_model():
    """Получение текущей модели"""
    return jsonify({
        "status": "success",
        "settings": CURRENT_MODEL_SETTINGS
    })

if __name__ == '__main__':
    print("🚀 Запуск тестового сервера на порту 5052...")
    print("📋 Доступные эндпоинты:")
    print("  - GET  /api/health")
    print("  - POST /api/process")
    print("  - GET  /api/task/<task_id>")
    print("  - GET  /api/models/openrouter")
    print("  - POST /api/model/set")
    print("  - GET  /api/model/current")
    app.run(host='0.0.0.0', port=5052, debug=False)