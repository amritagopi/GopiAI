# --- START OF FILE crewai_api_server.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

# КРИТИЧЕСКИ ВАЖНО: Применяем патч для mem0/faiss ДО импорта любых других библиотек
import mem0_patch

import logging
import os

# Настройка читаемого логирования для CrewAI сервера
log_file = 'crewai_api_server_debug.log'

class UltraCleanFormatter(logging.Formatter):
    """Форматтер который убирает ВСЕ нечитаемые символы"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def format(self, record):
        # Получаем базовое сообщение
        message = super().format(record)
        
        # Оставляем только ASCII символы + кириллица + основные знаки препинания
        import re
        
        # Создаем новую строку только из читаемых символов
        clean_chars = []
        for char in message:
            # Проверяем каждый символ
            code = ord(char)
            
            # Разрешенные диапазоны:
            # 32-126: основные ASCII символы (пробел, буквы, цифры, знаки)
            # 1040-1103: кириллица (А-я)
            # 1025, 1105: Ё, ё
            if (32 <= code <= 126 or          # ASCII
                1040 <= code <= 1103 or       # Кириллица А-я
                code == 1025 or code == 1105  # Ё, ё
                ):
                clean_chars.append(char)
            else:
                # Заменяем нечитаемые символы на пробел
                if char not in ['\n', '\r', '\t']:  # Сохраняем переносы строк и табы
                    clean_chars.append(' ')
                else:
                    clean_chars.append(char)
        
        message = ''.join(clean_chars)
        
        # Убираем множественные пробелы
        message = re.sub(r' +', ' ', message)
        
        # Сокращаем длинные JSON строки
        if 'Raw data:' in message and len(message) > 200:
            message = message.split('Raw data:')[0] + 'Raw data: [JSON сокращен]'
        if 'Parsed JSON:' in message and len(message) > 200:
            message = message.split('Parsed JSON:')[0] + 'Parsed JSON: [JSON сокращен]'
        
        return message.strip()

# Настройка обработчиков логирования
handlers = []

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(UltraCleanFormatter())
handlers.append(console_handler)

# Файловый обработчик
try:
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except (OSError, PermissionError):
            print(f"[WARNING] Не удалось удалить старый лог файл {log_file}, возможно он открыт в редакторе")
    
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(UltraCleanFormatter())
    handlers.append(file_handler)
    print(f"[OK] Логирование настроено с записью в файл: {log_file}")
    
except (OSError, PermissionError) as e:
    print(f"[WARNING] Не удалось создать файл лога {log_file}: {e}")
    print("[INFO] Логирование будет только в консоль")

# Базовая настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    handlers=handlers
)

# Убираем лишние технические сообщения от библиотек
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('LiteLLM').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
import sys
import json
import time
import traceback
import uuid
import threading
import signal
import atexit
from pathlib import Path
from datetime import datetime, timedelta

# Исправляем конфликт OpenMP библиотек
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
# Загружаем .env из корневой директории проекта
load_dotenv(dotenv_path="../.env")
# Также загружаем локальный .env файл (если есть)
load_dotenv(dotenv_path=".env")

from flask import Flask, request, jsonify

# --- Настройка путей и импортов ---
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# ### ИЗМЕНЕНО: Импортируем правильные фабричные функции ###
from rag_system import get_rag_system
from tools.gopiai_integration.smart_delegator import SmartDelegator

# Импортируем функции для работы с провайдерами и моделями
try:
    from llm_rotation_config import get_available_models, update_state, PROVIDER_KEY_ENV
    from state_manager import load_state, save_state
except ImportError:
    # Если импорт не удался, попробуем относительный импорт
    from .llm_rotation_config import get_available_models, update_state, PROVIDER_KEY_ENV
    from .state_manager import load_state, save_state

# Импортируем наш новый StateManager
# Комментарий: Убрали импорт GopiAI_Core, чтобы избежать ошибок - STATE_MANAGER_AVAILABLE = False
STATE_MANAGER_AVAILABLE = False

# --- Настройки сервера ---
HOST = "0.0.0.0"  # Слушаем на всех интерфейсах
PORT = 5051  # Стандартный порт для CrewAI API сервера
DEBUG = False
TASK_CLEANUP_INTERVAL = 300

# --- Глобальное хранилище задач ---
TASKS = {}
TASKS_LOCK = threading.Lock()

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id, message, metadata):
        self.task_id = task_id
        self.message = message
        self.metadata = metadata
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.lock = threading.Lock()

    def start_processing(self):
        with self.lock:
            self.status = TaskStatus.PROCESSING
            self.started_at = datetime.now()

    def complete(self, result):
        with self.lock:
            self.status = TaskStatus.COMPLETED
            self.result = result
            self.completed_at = datetime.now()

    def fail(self, error):
        with self.lock:
            self.status = TaskStatus.FAILED
            self.error = str(error)
            self.completed_at = datetime.now()

    def to_dict(self):
        return {
            "task_id": self.task_id, "status": self.status, "message": self.message,
            "result": self.result, "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def cleanup_old_tasks():
    while True:
        time.sleep(TASK_CLEANUP_INTERVAL)
        now = datetime.now()
        with TASKS_LOCK:
            for task_id in list(TASKS.keys()):
                if TASKS[task_id].completed_at and (now - TASKS[task_id].completed_at) > timedelta(hours=1):
                    del TASKS[task_id]

cleanup_thread = threading.Thread(target=cleanup_old_tasks, daemon=True)
cleanup_thread.start()

app = Flask(__name__)

# --- Инициализация всех систем при старте ---
try:
    print("[ДИАГНОСТИКА] Начало инициализации систем")
    logger.info("--- ИНИЦИАЛИЗАЦИЯ СИСТЕМ ---")
    
    # 1. Получаем единственный экземпляр RAGSystem
    print("[ДИАГНОСТИКА] Вызов get_rag_system()")
    rag_system_instance = get_rag_system()
    print(f"[ДИАГНОСТИКА] RAGSystem получен: {rag_system_instance is not None}")
    
    # 2. Создаем SmartDelegator, передавая ему наш единственный экземпляр RAG
    print("[ДИАГНОСТИКА] Создание SmartDelegator")
    smart_delegator_instance = SmartDelegator(rag_system=rag_system_instance)
    print(f"[ДИАГНОСТИКА] SmartDelegator создан: {smart_delegator_instance is not None}")
    
    # 3. Загружаем состояние провайдера/модели при запуске
    if STATE_MANAGER_AVAILABLE:
        try:
            print("[ДИАГНОСТИКА] Загрузка состояния провайдера/модели")
            state_manager = get_state_manager()
            current_state = state_manager.load_state()
            
            # Обновляем внутреннее состояние системы
            update_state(current_state.provider, current_state.model_id)
            
            logger.info(f"✅ Состояние загружено: провайдер={current_state.provider}, модель={current_state.model_id}")
            print(f"[ДИАГНОСТИКА] Состояние загружено: {current_state.provider}/{current_state.model_id}")
        except Exception as e:
            logger.warning(f"[STARTUP] Ошибка загрузки состояния: {e}")
            print(f"[ДИАГНОСТИКА] Ошибка загрузки состояния: {e}")
    
    logger.info("✅ Smart Delegator и RAG System успешно инициализированы.")
    SERVER_IS_READY = True
    print("[ДИАГНОСТИКА] SERVER_IS_READY = True")
except Exception as e:
    print(f"[DIAGNOSTIC] CRITICAL ERROR: {e}")
    logger.error(f"CRITICAL ERROR DURING SERVER STARTUP: {e}", exc_info=True)
    rag_system_instance = None
    smart_delegator_instance = None
    SERVER_IS_READY = False
    print("[DIAGNOSTIC] SERVER_IS_READY = False, server will not be started")

# --- Flask routes ---

@app.route('/api/health', methods=['GET'])
def health_check():
    rag_status = "OK" if rag_system_instance and rag_system_instance.embeddings else "NOT INITIALIZED"
    return jsonify({
        "status": "online" if SERVER_IS_READY else "limited_mode",
        "rag_status": rag_status,
        "indexed_documents": rag_system_instance.embeddings.count() if rag_status == "OK" else 0
    })

def process_task(task_id: str):
    """Processes a task in a separate thread."""
    task = TASKS.get(task_id)
    if not task:
        logger.error(f"[TASK-ERROR] Task {task_id} not found in TASKS")
        return
        
    if not smart_delegator_instance:
        error_msg = "Smart Delegator not initialized."
        logger.error(f"[TASK-ERROR] {error_msg}")
        task.fail(error_msg)
        return

    try:
        task.start_processing()
        logger.info(f"[TASK-START] Starting task {task_id} for message: '{task.message}'")
        
        # Добавляем дополнительную проверку
        if not hasattr(smart_delegator_instance, 'process_request'):
            error_msg = "Smart Delegator missing process_request method"
            logger.error(f"[TASK-ERROR] {error_msg}")
            task.fail(error_msg)
            return
            
        response_data = smart_delegator_instance.process_request(
            message=task.message,
            metadata=task.metadata
        )
        
        logger.info(f"[TASK-SUCCESS] Task {task_id} processed successfully.")
        task.complete(response_data)
        
    except Exception as e:
        error_msg = f"Error processing task {task_id}: {str(e)}"
        logger.error(f"[TASK-ERROR] {error_msg}", exc_info=True)
        task.fail(error_msg)

@app.route('/api/process', methods=['POST'])
def process_request():
    if not SERVER_IS_READY:
        return jsonify({"error": "Server started in limited mode due to initialization error."}), 503

    # Добавляем отладочную информацию
    logger.info(f"[API-REQUEST] Получен POST запрос на /api/process")
    logger.info(f"[API-REQUEST] Content-Type: {request.content_type}")
    logger.info(f"[API-REQUEST] Raw data: {request.get_data()}")
    
    try:
        # Пробуем получить JSON данные
        data = request.get_json(force=True)
        logger.info(f"[API-REQUEST] Parsed JSON: {data}")
        
        if not data or 'message' not in data:
            logger.error(f"[API-REQUEST] Ошибка: нет поля 'message' в данных: {data}")
            return jsonify({"error": "Missing 'message' field"}), 400

        message = data.get('message')
        metadata = data.get('metadata', {})
        
        logger.info(f"[API-REQUEST] Message: {message}")
        logger.info(f"[API-REQUEST] Metadata: {metadata}")
        
    except Exception as e:
        logger.error(f"[API-REQUEST] Ошибка парсинга JSON: {str(e)}")
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    task_id = str(uuid.uuid4())
    task = Task(task_id, message, metadata)

    with TASKS_LOCK:
        TASKS[task_id] = task

    thread = threading.Thread(target=process_task, args=(task_id,), daemon=True)
    thread.start()

    return jsonify({
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "message": "Task queued for processing",
        "created_at": task.created_at.isoformat()
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())

@app.route('/api/debug', methods=['GET'])
def debug_status():
    """Debug endpoint for system status"""
    return jsonify({
        "server_ready": SERVER_IS_READY,
        "smart_delegator_ready": smart_delegator_instance is not None,
        "rag_system_ready": rag_system_instance is not None,
        "active_tasks": len(TASKS),
        "task_ids": list(TASKS.keys())
    })

# --- Новые эндпоинты для синхронизации состояния провайдеров и моделей ---

@app.route('/api/config/models', methods=['GET'])
def get_model_config():
    """
    Возвращает список активных моделей и провайдеров для UI.
    Этот эндпоинт заменяет прямой импорт llm_rotation_config в UI.
    """
    try:
        from llm_rotation_config import LLM_MODELS_CONFIG, rate_limit_monitor
        
        # Получаем активные модели с учетом blacklist
        active_models = []
        providers = set()
        
        for model in LLM_MODELS_CONFIG:
            if not model.get('deprecated', False):
                # Проверяем, не заблокирована ли модель
                if not rate_limit_monitor.is_model_blocked_safe(model['id']):
                    active_models.append({
                        'id': model['id'],
                        'name': model['name'],
                        'provider': model['provider'],
                        'type': model['type'],
                        'multimodal': model.get('multimodal', False),
                        'priority': model.get('priority', 1),
                        'base_score': model.get('base_score', 0.5)
                    })
                    providers.add(model['provider'])
        
        # Получаем статус blacklist для отладки
        blacklist_status = rate_limit_monitor.get_blacklist_status()
        
        config_data = {
            "providers": list(providers),
            "active_models": active_models,
            "blacklist_status": blacklist_status,
            "total_models": len(LLM_MODELS_CONFIG),
            "active_count": len(active_models)
        }
        
        logger.info(f"[CONFIG] Возвращаем конфигурацию: {len(active_models)} активных моделей из {len(LLM_MODELS_CONFIG)}")
        return jsonify(config_data)
        
    except Exception as e:
        logger.error(f"[CONFIG] Ошибка получения конфигурации моделей: {e}")
        return jsonify({"error": "Failed to load model configuration", "details": str(e)}), 500

@app.route('/api/models/<provider>', methods=['GET'])
def get_models_by_provider():
    """Возвращает список доступных моделей для указанного провайдера"""
    provider = request.args.get('provider')
    if not provider:
        return jsonify({"error": "Missing 'provider' parameter"}), 400
    
    # Получаем все доступные модели для указанного типа задач (используем 'dialog' как стандартный тип)
    all_models = get_available_models("dialog")
    
    # Фильтруем модели по провайдеру
    provider_models = [m for m in all_models if m["provider"] == provider]
    
    return jsonify(provider_models)

@app.route('/internal/state', methods=['POST'])
def update_provider_model_state():
    """Обновляет текущее состояние провайдера и модели в файле ~/.gopiai_state.json"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON data"}), 400
            
        provider = data.get("provider")
        model_id = data.get("model_id")
        
        if not provider or not model_id:
            return jsonify({"error": "Both 'provider' and 'model_id' are required"}), 400
        
        # Обновляем внутреннее состояние системы
        update_state(provider, model_id)
        
        # Сохраняем в файл состояния через StateManager
        if STATE_MANAGER_AVAILABLE:
            try:
                state_manager = get_state_manager()
                success = state_manager.save_state(provider, model_id)
                if success:
                    logger.info(f"[STATE] Состояние сохранено в файл: {provider}/{model_id}")
                else:
                    logger.warning(f"[STATE] Не удалось сохранить состояние в файл")
            except Exception as e:
                logger.error(f"[STATE] Ошибка сохранения состояния в файл: {e}")
        
        return jsonify({
            "status": "success",
            "message": f"State updated: provider={provider}, model_id={model_id}",
            "provider": provider,
            "model_id": model_id,
            "saved_to_file": STATE_MANAGER_AVAILABLE
        })
        
    except Exception as e:
        logger.error(f"Error updating state: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update state: {str(e)}"}), 500

@app.route('/internal/state', methods=['GET'])
def get_current_state():
    """Возвращает текущее состояние провайдера и модели"""
    try:
        # Пытаемся загрузить из файла через StateManager
        if STATE_MANAGER_AVAILABLE:
            try:
                state_manager = get_state_manager()
                current_state = state_manager.get_current_state()
                
                if current_state:
                    return jsonify({
                        "provider": current_state.provider,
                        "model_id": current_state.model_id,
                        "last_updated": current_state.last_updated,
                        "source": "state_file"
                    })
            except Exception as e:
                logger.warning(f"[STATE] Ошибка чтения из файла состояния: {e}")
        
        # Fallback к старому методу
        state = load_state()
        state["source"] = "legacy_method"
        return jsonify(state)
        
    except Exception as e:
        logger.error(f"Error loading state: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to load state: {str(e)}"}), 500

# Обработка сигналов для корректного завершения
def signal_handler(signum, frame):
    print(f"\n[SHUTDOWN] Received signal {signum}. Shutting down gracefully...")
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def cleanup_on_exit():
    print("[SHUTDOWN] Cleaning up resources...")
    logger.info("Cleaning up resources...")

if __name__ == '__main__':
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_on_exit)
    
    print(f"[DIAGNOSTIC] __main__ block, SERVER_IS_READY = {SERVER_IS_READY}")
    if SERVER_IS_READY:
        print(f"[DIAGNOSTIC] Starting server on http://{HOST}:{PORT}")
        logger.info(f"[STARTUP] Server starting on http://{HOST}:{PORT}")
        try:
            print("[DIAGNOSTIC] Calling app.run()")
            app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True, use_reloader=False)
            print("[DIAGNOSTIC] After app.run() - this message should not appear")
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received KeyboardInterrupt. Shutting down gracefully...")
            logger.info("Received KeyboardInterrupt. Shutting down gracefully...")
        except Exception as e:
            print(f"[DIAGNOSTIC] Error starting server: {e}")
            logger.error(f"Error starting server: {e}")
    else:
        print("[DIAGNOSTIC] Server not started due to initialization errors")
        logger.error("Server not started due to initialization errors.")
        print("CRITICAL ERROR: Server cannot be started due to initialization errors.")
        sys.exit(1)

# --- END OF FILE crewai_api_server.py ---
