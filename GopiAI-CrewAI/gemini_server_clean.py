#!/usr/bin/env python3
"""
Чистый Gemini API сервер с поддержкой code_execution
Следует официальной документации: https://ai.google.dev/gemini-api/docs/code-execution
"""
import os
import uuid
import logging
import traceback
import time
from typing import Dict, Any
from enum import Enum, auto
from pathlib import Path
from threading import Thread
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS

# Загрузка переменных окружения
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[DEBUG] .env загружен из: {env_path}")
else:
    print(f"[ERROR] .env не найден: {env_path}")

# Настройка логирования
log_dir = Path.home() / ".gopiai" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "gemini_server_clean.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорт официального Gemini SDK
try:
    from google import genai
    from google.genai import types
    logger.info("✅ Официальный Gemini SDK импортирован")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта Gemini SDK: {e}")
    exit(1)

# Проверка API ключа
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY не найден")
    exit(1)

logger.info(f"🔑 API ключ найден: {GEMINI_API_KEY[:10]}...")

class TaskStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

# Инициализация Flask
app = Flask(__name__)
CORS(app)

# Хранилище задач
tasks_storage: Dict[str, Dict[str, Any]] = {}

# Инициализация Gemini клиента
try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Конфигурация с code_execution
    generation_config = types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
        temperature=0.7,
    )
    
    logger.info("✅ Gemini клиент инициализирован с code_execution")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Gemini: {e}")
    exit(1)

def process_gemini_response(response) -> str:
    """Обработка ответа Gemini согласно документации"""
    result_parts = []
    
    try:
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                result_parts.append(part.text)
                
            if part.executable_code is not None:
                result_parts.append(f"\n🐍 **Выполняемый код:**\n```python\n{part.executable_code.code}\n```")
                
            if part.code_execution_result is not None:
                result_parts.append(f"\n📊 **Результат выполнения:**\n```\n{part.code_execution_result.output}\n```")
        
        return "\n".join(result_parts) if result_parts else "Получен пустой ответ"
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки ответа: {e}")
        return f"Ошибка обработки ответа: {e}"

def execute_task(task_id: str, prompt: str):
    """Выполнение задачи через Gemini API"""
    try:
        logger.info(f"🚀 Начинаем выполнение задачи {task_id}")
        
        # Обновляем статус
        tasks_storage[task_id]["status"] = TaskStatus.PROCESSING
        tasks_storage[task_id]["progress"] = "Отправка запроса в Gemini..."
        
        # Отправляем запрос в Gemini
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=generation_config
        )
        
        logger.info(f"✅ Получен ответ от Gemini для задачи {task_id}")
        
        # Обрабатываем ответ
        result = process_gemini_response(response)
        
        # Обновляем результат
        tasks_storage[task_id]["status"] = TaskStatus.COMPLETED
        tasks_storage[task_id]["result"] = result
        tasks_storage[task_id]["progress"] = "Задача выполнена успешно"
        tasks_storage[task_id]["completed_at"] = time.time()
        
        logger.info(f"✅ Задача {task_id} выполнена успешно")
        
    except Exception as e:
        error_msg = f"Ошибка выполнения: {e}"
        logger.error(f"❌ Задача {task_id} провалена: {error_msg}")
        logger.error(traceback.format_exc())
        
        tasks_storage[task_id]["status"] = TaskStatus.FAILED
        tasks_storage[task_id]["error"] = error_msg
        tasks_storage[task_id]["progress"] = f"Ошибка: {error_msg}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    logger.debug("🔍 Health check запрос")
    return jsonify({
        "service": "Gemini Code Execution Server",
        "status": "healthy",
        "timestamp": time.time(),
        "gemini_sdk": "google-genai",
        "code_execution": True
    })

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создание новой задачи"""
    try:
        logger.info("📝 Получен запрос на создание задачи")
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "Требуется поле 'prompt'"}), 400
        
        # Создаем задачу
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "prompt": prompt,
            "status": TaskStatus.PENDING,
            "created_at": time.time(),
            "progress": "Задача создана"
        }
        
        tasks_storage[task_id] = task_data
        logger.info(f"🆔 Создана задача: {task_id}")
        
        # Запускаем выполнение в фоне
        thread = Thread(target=execute_task, args=(task_id, prompt))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "message": "Задача создана и запущена",
            "task_id": task_id,
            "status": TaskStatus.PENDING.name
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания задачи: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """Список всех задач"""
    try:
        tasks = []
        for task_id, task_data in tasks_storage.items():
            task_info = {
                "task_id": task_id,
                "status": task_data["status"].name,
                "created_at": task_data["created_at"],
                "progress": task_data.get("progress", "")
            }
            
            if "completed_at" in task_data:
                task_info["completed_at"] = task_data["completed_at"]
            
            tasks.append(task_info)
        
        return jsonify({"tasks": tasks})
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка задач: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """Получение информации о задаче"""
    try:
        logger.debug(f"📊 Запрос статуса задачи: {task_id}")
        
        if task_id not in tasks_storage:
            return jsonify({"error": "Задача не найдена"}), 404
        
        task_data = tasks_storage[task_id]
        
        response = {
            "task_id": task_id,
            "status": task_data["status"].name,
            "created_at": task_data["created_at"],
            "progress": task_data.get("progress", "")
        }
        
        if "result" in task_data:
            response["result"] = task_data["result"]
        
        if "error" in task_data:
            response["error"] = task_data["error"]
        
        if "completed_at" in task_data:
            response["completed_at"] = task_data["completed_at"]
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения задачи: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Прямое общение с Gemini (синхронное)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400
        
        message = data.get('message')
        if not message:
            return jsonify({"error": "Требуется поле 'message'"}), 400
        
        logger.info(f"💬 Chat запрос: {message[:50]}...")
        
        # Отправляем в Gemini
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config=generation_config
        )
        
        result = process_gemini_response(response)
        
        return jsonify({
            "response": result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка chat: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Запуск чистого Gemini сервера...")
    logger.info("🔗 Доступные endpoints:")
    logger.info("   GET  /api/health - проверка здоровья")
    logger.info("   POST /api/chat - прямое общение с Gemini")
    logger.info("   POST /api/tasks - создание задачи")
    logger.info("   GET  /api/tasks - список задач")
    logger.info("   GET  /api/tasks/<id> - статус задачи")
    logger.info("")
    logger.info("🚀 Сервер готов к работе на http://localhost:5052")
    
    app.run(host='0.0.0.0', port=5052, debug=False)