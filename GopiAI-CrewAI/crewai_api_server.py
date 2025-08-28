# --- START OF FILE crewai_api_server.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

import logging
import os
import uuid
from typing import Any, Dict

# Настройка читаемого логирования для CrewAI сервера
# Логи переносим в $HOME/.gopiai/logs с гарантированным созданием каталога.
from pathlib import Path as _Path
_LOG_DIR = _Path.home() / ".gopiai" / "logs"
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception as _e:
    # В случае ошибки — fallback в текущий каталог
    print(f"[WARNING] Не удалось создать каталог логов {_LOG_DIR}: {_e}. Используем текущий каталог.")
    _LOG_DIR = _Path(".")
log_file = str(_LOG_DIR / "crewai_api_server_debug.log")

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
    else:
        # гарантируем наличие родительского каталога
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        except Exception as _e:
            print(f"[WARNING] Не удалось создать родительский каталог для лога: {os.path.dirname(log_file)}: {_e}")
    
    from logging.handlers import RotatingFileHandler
    # Основной хендлер в домашней директории
    file_handler = RotatingFileHandler(log_file, mode='a', encoding='utf-8', maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(UltraCleanFormatter())
    handlers.append(file_handler)
    print(f"[OK] Логирование настроено с записью в файл: {log_file}")

    # Дополнительный локальный хендлер в папке проекта (перезаписывается при каждом запуске, с BOM для Windows)
    try:
        _LOCAL_LOG_PATH = _Path(__file__).parent / "crewai_api_server_debug_local.log"
        # Перезаписываем файл на каждый старт сервера
        from logging import FileHandler as _FileHandler
        local_file_handler = _FileHandler(str(_LOCAL_LOG_PATH), mode='w', encoding='utf-8-sig')
        local_file_handler.setFormatter(UltraCleanFormatter())
        handlers.append(local_file_handler)
        print(f"[OK] Доп. логирование включено (перезапись на старте): {_LOCAL_LOG_PATH}")
    except Exception as _le:
        print(f"[WARNING] Не удалось создать локальный лог в папке проекта: {_le}")
    
except (OSError, PermissionError) as e:
    print(f"[WARNING] Не удалось создать файл лога {log_file}: {e}")
    print("[INFO] Логирование будет только в консоль")

# Базовая настройка логирования
logging.basicConfig(
    level=logging.INFO,
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
from typing import Any, cast
from typing import Optional, Dict

# Исправляем конфликт OpenMP библиотек
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
# Загружаем .env из корневой директории проекта
load_dotenv(dotenv_path="../.env")
# Также загружаем локальный .env файл (если есть)
load_dotenv(dotenv_path=".env")

from flask import Flask, request, jsonify
from asgiref.wsgi import WsgiToAsgi

# DeerFlow logging integration
try:
    from gopiai.logging.json_logger import jlog, ensure_request_id, mask_headers, now_ms  # type: ignore
except Exception:
    # fallback no-op if module not available
    def jlog(*args, **kwargs):  # type: ignore
        logging.getLogger(__name__).log(getattr(logging, kwargs.get("level","INFO")), kwargs.get("message",""))
    def ensure_request_id(existing=None):  # type: ignore
        return str(uuid.uuid4())
    def mask_headers(h):  # type: ignore
        return None
    def now_ms():  # type: ignore
        import time as _t
        return int(_t.time()*1000)

# --- Настройка путей и импортов ---
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# ### ИЗМЕНЕНО: Импортируем правильные фабричные функции ###
from rag_system import get_rag_system
# Custom SmartDelegator removed - using basic CrewAI functionality

# Импортируем функции для работы с провайдерами и моделями
try:
    from llm_rotation_config import get_available_models, update_state, PROVIDER_KEY_ENV
    from state_manager import load_state, save_state
except ImportError:
    # Если импорт не удался, попробуем относительный импорт
    from .llm_rotation_config import get_available_models, update_state, PROVIDER_KEY_ENV
    from .state_manager import load_state, save_state

# --- Настройки сервера ---
HOST = "0.0.0.0"  # Слушаем на всех интерфейсах
PORT = 5051  # Стандартный порт для CrewAI API сервера
DEBUG = False
TASK_CLEANUP_INTERVAL = 300

# --- Динамический выбор свободного порта с учетом ENV ---
def _find_available_port(start_port: int, max_tries: int = 20) -> int:
    """Возвращает первый свободный порт, начиная с start_port.
    Если за max_tries не найден, возвращает исходный start_port.
    """
    import socket
    port = int(start_port)
    for _ in range(max_tries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            try:
                s.close()
            except Exception:
                pass
            port += 1
    return int(start_port)

def _write_selected_port(port_value: int) -> None:
    """Сохраняет выбранный порт в файл ~/.gopiai/crewai_server_port.txt"""
    try:
        target_dir = _Path.home() / ".gopiai"
        target_dir.mkdir(parents=True, exist_ok=True)
        port_file = target_dir / "crewai_server_port.txt"
        with open(port_file, "w", encoding="utf-8") as f:
            f.write(str(int(port_value)))
    except Exception as _e:
        logger.warning(f"Не удалось сохранить выбранный порт: {port_value}: {_e}")

# --- Глобальное хранилище задач ---
TASKS = {}
TASKS_LOCK = threading.Lock()

# Храним последнюю effective-конфигурацию (без секретов) для echo-эндпоинта
EFFECTIVE_CONFIG_LAST: Optional[Dict[str, Any]] = None

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
 
# --- Settings manager for UI toggle (temporarily disabled) ---
# Custom settings manager removed - using basic fallback
def _read_settings():
    return {}
def _write_settings(data):
    raise RuntimeError("settings_manager not available")
def _set_terminal_unsafe(enabled: bool):
    raise RuntimeError("settings_manager not available")
def _get_primary_settings_path(create_dirs: bool = False):
    from pathlib import Path as __P
    return __P.cwd() / "settings.json"

# Flask before/after request hooks to implement DeerFlow request_in/request_out
@app.before_request
def _before_request_logging():
    rid = ensure_request_id(request.headers.get("X-Request-ID"))
    # stash in flask.g via request context (werkzeug local)
    request.environ["gopiai.request_id"] = rid
    request.environ["gopiai.start_ms"] = now_ms()
    try:
        payload_keys = []
        if request.is_json:
            try:
                data = request.get_json(silent=True) or {}
                payload_keys = list(data.keys())
            except Exception:
                payload_keys = []
        jlog(
            level="INFO",
            event="request_in",
            request_id=rid,
            route=str(request.url),
            method=request.method,
            headers_masked=mask_headers({k: v for k, v in request.headers.items()}),
            payload_keys=payload_keys,
        )
    except Exception:
        # never break request processing due to logging
        pass

@app.after_request
def _after_request_logging(response):
    try:
        rid = request.environ.get("gopiai.request_id") or ensure_request_id(request.headers.get("X-Request-ID"))
        start_ms = request.environ.get("gopiai.start_ms") or now_ms()
        latency = now_ms() - int(start_ms)
        jlog(
            level="INFO",
            event="request_out",
            request_id=rid,
            route=str(request.url),
            method=request.method,
            status_code=response.status_code,
            latency_ms=latency,
            success=200 <= response.status_code < 400,
        )
        # propagate X-Request-ID back to client
        response.headers["X-Request-ID"] = rid
    except Exception:
        pass
    return response

# --- Инициализация всех систем при старте ---
try:
    logger.info("--- ИНИЦИАЛИЗАЦИЯ СИСТЕМ ---")
    
    # 1. Инициализируем RAG систему
    rag_system_instance = get_rag_system()
    
    # 2. Создаем базовый обработчик запросов (замена SmartDelegator)
    smart_delegator_instance = None  # Временно отключен после рефакторинга
    
    # 3. Инициализируем интегратор инструментов (временно отключен)
    # from tools.gopiai_integration.crewai_tools_integrator import get_crewai_tools_integrator
    # tools_integrator_instance = get_crewai_tools_integrator()
    tools_integrator_instance = None  # Временно отключен после рефакторинга
    
    logger.info("✅ Smart Delegator (с RAG) и Tools Integrator успешно инициализированы.")
    SERVER_IS_READY = True

except Exception as e:
    logger.error(f"CRITICAL ERROR DURING SERVER STARTUP: {e}", exc_info=True)
    rag_system_instance = None
    smart_delegator_instance = None
    tools_integrator_instance = None
    SERVER_IS_READY = False
    print("CRITICAL ERROR: Server will start in limited mode due to an initialization failure.", file=sys.stderr)
    traceback.print_exc()

# --- Flask routes ---

@app.route('/api/health', methods=['GET'])
def health_check():
    # Безопасные проверки на None для Pyright и рантайма
    indexed_documents = 0
    rag_status = "NOT INITIALIZED"
    try:
        if rag_system_instance is not None:
            # Используем новый метод get_document_count
            get_count_method = getattr(rag_system_instance, "get_document_count", None)
            if callable(get_count_method):
                indexed_documents = get_count_method()
                rag_status = "OK"
            else:
                # Fallback к старому методу через embeddings
                embeddings = getattr(rag_system_instance, "embeddings", None)
                if embeddings is not None:
                    count_attr = getattr(embeddings, "count", None)
                    if callable(count_attr):
                        indexed_documents = count_attr()
                    elif isinstance(count_attr, (int, float)):
                        indexed_documents = int(count_attr)
                    rag_status = "OK"
    except Exception as _e:
        # В случае любой ошибки оставляем значения по умолчанию
        rag_status = "ERROR"
        indexed_documents = 0

    return jsonify({
        "status": "online" if SERVER_IS_READY else "limited_mode",
        "rag_status": rag_status,
        "indexed_documents": indexed_documents,
        "refactoring_status": "Custom tools removed, native CrewAI tools preserved",
        "smart_delegator_status": "Disabled - replaced with basic functionality",
        "tools_integrator_status": "Disabled - replaced with native CrewAI tools"
    })

def process_task(task_id: str):
    """Processes a task in a separate thread."""
    task = TASKS.get(task_id)
    if not task:
        logger.error(f"Task {task_id} not found in TASKS dictionary.", extra={'task_id': task_id})
        return

    if not smart_delegator_instance:
        err_msg = "Smart Delegator not initialized (temporarily disabled after refactoring). Cannot process task."
        logger.error(err_msg, extra={'task_id': task_id})
        task.fail(err_msg)
        return

    try:
        task.start_processing()
        logger.info(f"Starting task {task_id}", extra={'task_id': task_id, 'task_message': task.message})

        # Temporary basic response until SmartDelegator is reimplemented
        response_data = {
            "response": f"Обработка запроса '{task.message}' временно недоступна после рефакторинга инструментов.",
            "status": "refactoring_in_progress",
            "message": "Система находится в процессе рефакторинга. Кастомные инструменты были удалены, нативные CrewAI инструменты сохранены."
        }

        logger.info(f"Task {task_id} processed with temporary response. Response data: {response_data}", extra={'task_id': task_id})
        task.complete(response_data)

    except Exception as e:
        error_msg = f"An unexpected error occurred while processing task {task_id}."
        logger.error(error_msg, exc_info=True, extra={'task_id': task_id})
        # Capture full traceback for the task's error field
        tb = traceback.format_exc()
        task.fail(f"{error_msg} Details: {e}\n{tb}")

@app.route('/api/process', methods=['POST'])
def process_request():
    global EFFECTIVE_CONFIG_LAST
    rid = request.environ.get("gopiai.request_id") or ensure_request_id(request.headers.get("X-Request-ID"))
    op_start = now_ms()
    jlog(level="INFO", event="api_entry", request_id=rid, route="/api/process", method="POST")

    # Собираем примитивный effective-config без секретов (демо для echo)
    # В боевом коде сюда можно добавить merge(defaults, user/org, overrides)
    try:
        data_preview = {}
        if request.is_json:
            data_preview = request.get_json(silent=True) or {}
        EFFECTIVE_CONFIG_LAST = {
            "provider": os.getenv("PROVIDER_DEFAULT", "openrouter"),
            "model": os.getenv("MODEL_DEFAULT", "openai/gpt-4o"),
            "temperature": float(os.getenv("TEMPERATURE_DEFAULT", "0.2")),
            "top_p": float(os.getenv("TOP_P_DEFAULT", "0.95")),
            "route": "/api/process",
            "request_id": rid,
            "payload_keys": list(data_preview.keys()),
        }
    except Exception:
        # Не прерываем обработку запроса
        pass
    rid = request.environ.get("gopiai.request_id") or ensure_request_id(request.headers.get("X-Request-ID"))
    op_start = now_ms()
    jlog(level="INFO", event="api_entry", request_id=rid, route="/api/process", method="POST")
    if not SERVER_IS_READY:
        return jsonify({"error": "Server started in limited mode due to initialization error."}), 503

    try:
        data = request.get_json()
        if data is None:
            logger.warning("Request received with non-JSON or empty body.", extra={'request_id': rid})
            return jsonify({"error": "Invalid request: body must be a valid JSON."}), 400

        jlog(level="DEBUG", event="api_payload", request_id=rid, payload_keys=list(data.keys()))

        message = data.get('message')
        if not message:
            logger.warning("Request is missing 'message' field.", extra={'request_id': rid})
            return jsonify({"error": "Missing required 'message' field in JSON payload."}), 400

        metadata = data.get('metadata', {})
        logger.info(f"Received task with message: '{message}'", extra={'request_id': rid})
        
    except Exception as e:
        logger.error(f"Failed to parse JSON payload: {e}", exc_info=True, extra={'request_id': rid})
        return jsonify({"error": f"Invalid JSON format: {e}"}), 400

    task_id = str(uuid.uuid4())
    task = Task(task_id, message, metadata)

    with TASKS_LOCK:
        TASKS[task_id] = task

    thread = threading.Thread(target=process_task, args=(task_id,), daemon=True)
    thread.start()

    jlog(
        level="INFO",
        event="request_out",
        request_id=rid,
        route="/api/process",
        method="POST",
        status_code=202,
        latency_ms=now_ms() - op_start,
        success=True,
    )
    return jsonify({
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "message": "Task queued for processing",
        "created_at": task.created_at.isoformat(),
        "request_id": rid,
    }), 202

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
        "tools_integrator_ready": tools_integrator_instance is not None,
        "active_tasks": len(TASKS),
        "task_ids": list(TASKS.keys()),
        "refactoring_status": "Custom tools removed, native CrewAI tools preserved",
        "gopiai_integration_status": "Removed - replaced with native CrewAI functionality"
    })

# --- Новые эндпоинты для синхронизации состояния провайдеров и моделей ---

@app.route('/internal/models', methods=['GET'])
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
        model_id = data.get("model_id", "")
        
        # Проверяем наличие обоих параметров
        if not provider:
            return jsonify({"error": "The 'provider' field is required"}), 400
            
        if not model_id and provider == "openrouter":
            return jsonify({"error": "Both 'provider' and 'model_id' are required"}), 400
        
        # Обновляем состояние
        save_state(provider, model_id)
        
        # Обновляем текущий провайдер в UsageTracker
        try:
            from llm_rotation_config import usage_tracker
            if usage_tracker:
                usage_tracker.set_current_provider(provider)
                logger.info(f"✅ UsageTracker успешно обновлен с провайдером: {provider}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось обновить UsageTracker: {e}")
        
        # Обновляем текущую модель в ModelConfigManager (временно отключен)
        # try:
        #     from tools.gopiai_integration.model_config_manager import get_model_config_manager
        #     mcm = get_model_config_manager()
        #     if mcm:
        #         mcm.switch_to_provider(provider)
        #         if model_id:
        #             mcm.set_current_configuration(provider, model_id)
        #         logger.info(f"✅ ModelConfigManager успешно обновлен: provider={provider}, model_id={model_id}")
        # except Exception as e:
        #     logger.warning(f"⚠️ Не удалось обновить ModelConfigManager: {e}")
        logger.info(f"ModelConfigManager временно отключен после рефакторинга")
        
        return jsonify({
            "status": "success",
            "message": f"State updated: provider={provider}, model_id={model_id}",
            "provider": provider,
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Error updating state: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update state: {str(e)}"}), 500

@app.route('/settings/effective', methods=['GET'])
def get_effective_config():
    """
    Echo-эндпоинт DeerFlow для отладки:
    Возвращает последнюю сохранённую effective-конфигурацию без секретов.
    """
    try:
        if EFFECTIVE_CONFIG_LAST is None:
            return jsonify({"error": "No effective config captured yet"}), 404
        return jsonify(EFFECTIVE_CONFIG_LAST)
    except Exception as e:
        logger.error(f"Error in /settings/effective: {e}", exc_info=True)
        return jsonify({"error": f"Failed to fetch effective config: {str(e)}"}), 500


@app.route('/internal/state', methods=['GET'])
def get_current_state():
    """Возвращает текущее состояние провайдера и модели"""
    try:
        state = load_state()
        return jsonify(state)
    except Exception as e:
        logger.error(f"Error loading state: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to load state: {str(e)}"}), 500

# --- API endpoints for Tools Management ---

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Получить список всех инструментов с их статусом (временно упрощен после рефакторинга)"""
    try:
        if not tools_integrator_instance:
            # Return basic native CrewAI tools list
            return jsonify({
                "native_crewai_tools": [
                    {
                        "name": "Directory Read Tool",
                        "description": "Чтение содержимого директорий",
                        "enabled": True,
                        "available": True
                    },
                    {
                        "name": "File Read Tool",
                        "description": "Чтение файлов",
                        "enabled": True,
                        "available": True
                    },
                    {
                        "name": "Code Interpreter Tool",
                        "description": "Исполнение кода",
                        "enabled": True,
                        "available": True
                    }
                ],
                "status": "refactoring_in_progress",
                "message": "Интегратор инструментов временно отключен после рефакторинга"
            })

        # Получаем сводку инструментов по категориям
        tools_summary = tools_integrator_instance.get_tools_summary()

        # Читаем настройки переключателей и ключей
        settings = _read_settings()
        tool_toggles = settings.get('tools', {}).get('toggles', {})
        tool_keys = settings.get('tools', {}).get('keys', {})

        # Формируем ответ
        result = {}
        for category, tools in tools_summary.items():
            result[category] = []
            for tool in tools:
                tool_name = tool['name']
                # Проверяем, включен ли инструмент (по умолчанию включен)
                enabled = tool_toggles.get(tool_name, True)
                # Проверяем наличие кастомного ключа
                has_custom_key = tool_name in tool_keys

                result[category].append({
                    'name': tool_name,
                    'description': tool['description'],
                    'enabled': enabled,
                    'has_custom_key': has_custom_key,
                    'available': tool['available']
                })

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return jsonify({"error": str(e)}), 500


# --- API aliases (to satisfy UI expecting /api/* endpoints) ---
@app.route('/api/settings/terminal_unsafe', methods=['GET'])
def api_get_terminal_unsafe():
    """Alias for GET /settings/terminal_unsafe (UI expects /api prefix)."""
    return get_terminal_unsafe()


@app.route('/api/settings/terminal_unsafe', methods=['POST'])
def api_set_terminal_unsafe():
    """Alias for POST /settings/terminal_unsafe (UI expects /api prefix)."""
    return set_terminal_unsafe()

@app.route('/api/tools/toggle', methods=['POST'])
def toggle_tool():
    """Переключить состояние инструмента (включен/выключен)"""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        enabled = data.get('enabled', True)
        
        if not tool_name:
            return jsonify({"error": "tool_name is required"}), 400
        
        # Читаем текущие настройки
        settings = _read_settings()
        if 'tools' not in settings:
            settings['tools'] = {}
        if 'toggles' not in settings['tools']:
            settings['tools']['toggles'] = {}
        
        # Обновляем состояние
        settings['tools']['toggles'][tool_name] = enabled
        
        # Сохраняем настройки
        _write_settings(settings)
        
        logger.info(f"Tool {tool_name} {'enabled' if enabled else 'disabled'}")
        return jsonify({"success": True, "tool_name": tool_name, "enabled": enabled})
    
    except Exception as e:
        logger.error(f"Error toggling tool: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tools/set_key', methods=['POST'])
def set_tool_key():
    """Установить кастомный API ключ для инструмента"""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        api_key = data.get('api_key', '')
        
        if not tool_name:
            return jsonify({"error": "tool_name is required"}), 400
        
        # Читаем текущие настройки
        settings = _read_settings()
        if 'tools' not in settings:
            settings['tools'] = {}
        if 'keys' not in settings['tools']:
            settings['tools']['keys'] = {}
        
        # Обновляем ключ (или удаляем, если пустой)
        if api_key.strip():
            settings['tools']['keys'][tool_name] = api_key.strip()
            logger.info(f"API key set for tool {tool_name}")
        else:
            settings['tools']['keys'].pop(tool_name, None)
            logger.info(f"API key removed for tool {tool_name}")
        
        # Сохраняем настройки
        _write_settings(settings)
        
        return jsonify({"success": True, "tool_name": tool_name, "has_key": bool(api_key.strip())})
    
    except Exception as e:
        logger.error(f"Error setting tool key: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Получить список доступных агент-шаблонов (временно отключен после рефакторинга)"""
    try:
        # Custom agent templates removed - using basic CrewAI agents
        agents = [
            {
                "id": "coder",
                "name": "Coder Agent",
                "description": "Агент для написания и отладки кода",
                "type": "agent"
            },
            {
                "id": "researcher",
                "name": "Researcher Agent",
                "description": "Агент для исследования и анализа информации",
                "type": "agent"
            }
        ]

        flows = [
            {
                "id": "simple_flow",
                "name": "Simple Flow",
                "description": "Простой флоу с одним агентом",
                "type": "flow"
            }
        ]

        return jsonify({"agents": agents, "flows": flows})
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return jsonify({"error": str(e)}), 500

# --- UI toggle for Terminal Unsafe Mode ---
def _compute_terminal_unsafe_status() -> dict:
    """Возвращает effective-статус небезопасного режима терминала и источник."""
    src = "default"
    value = False
    try:
        env_val = os.getenv("GOPIAI_TERMINAL_UNSAFE", "").strip().lower()
        if env_val in {"1", "true", "yes", "on"}:
            return {"enabled": True, "source": "env:GOPIAI_TERMINAL_UNSAFE"}
        if env_val in {"0", "false", "no", "off"}:
            # env задаёт явный false — считаем источником env
            return {"enabled": False, "source": "env:GOPIAI_TERMINAL_UNSAFE"}
    except Exception:
        pass

    # Если env не зафиксировал состояние, читаем settings.json
    try:
        cfg = _read_settings()
        if isinstance(cfg, dict) and "terminal_unsafe" in cfg:
            value = bool(cfg.get("terminal_unsafe"))
            src = "settings.json"
    except Exception:
        value = False
        src = "default"

    return {"enabled": value, "source": src}


@app.route('/settings/terminal_unsafe', methods=['GET'])
def get_terminal_unsafe():
    """Текущий effective-статус unsafe режима терминала."""
    try:
        status = _compute_terminal_unsafe_status()
        status["settings_path"] = str(_get_primary_settings_path(create_dirs=False))
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error in GET /settings/terminal_unsafe: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/settings/terminal_unsafe', methods=['POST'])
def set_terminal_unsafe():
    """Устанавливает флаг в settings.json. Приоритет ENV выше, но UI пишет конфиг."""
    try:
        data = request.get_json(silent=True) or {}
        enabled = bool(data.get("enabled"))
        path = _set_terminal_unsafe(enabled)
        status = _compute_terminal_unsafe_status()
        status.update({
            "written": True,
            "written_path": str(path),
        })
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error in POST /settings/terminal_unsafe: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/ui/terminal_unsafe', methods=['GET'])
def ui_terminal_unsafe():
    """Простейшая HTML-страница с чекбоксом для переключения режима."""
    html = """
    <!doctype html>
    <html lang=\"ru\">
    <head>
      <meta charset=\"utf-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>GopiAI — Настройки терминала</title>
      <style>
        body { font-family: system-ui, Arial, sans-serif; padding: 24px; background: #111; color: #eee; }
        .card { max-width: 680px; margin: 0 auto; background: #1b1b1b; border: 1px solid #2c2c2c; border-radius: 10px; padding: 20px; }
        h1 { font-size: 20px; margin: 0 0 12px; }
        p.desc { color: #c7c7c7; margin-top: 0; }
        label { display: flex; align-items: center; gap: 10px; font-weight: 600; }
        input[type=checkbox] { width: 20px; height: 20px; }
        .row { margin-top: 14px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #2f2f2f; font-size: 12px; color: #bbb; }
        .status { margin-top: 10px; }
        button { padding: 8px 12px; border-radius: 8px; border: 1px solid #2c2c2c; background: #2a2a2a; color: #fff; cursor: pointer; }
        button:hover { background: #333; }
        code { background: #222; padding: 2px 6px; border-radius: 6px; }
      </style>
    </head>
    <body>
      <div class=\"card\">
        <h1>Настройки терминала</h1>
        <p class=\"desc\">Переключатель небезопасного режима терминала. Включай только если доверяешь задачам и окружению.</p>
        <div class=\"row\">
          <label>
            <input id=\"toggle\" type=\"checkbox\" /> Разрешить терминал без ограничений
          </label>
        </div>
        <div class=\"row status\">
          <span id=\"source\" class=\"badge\"></span>
        </div>
        <div class=\"row\">
          <button id=\"save\">Сохранить</button>
          <span id=\"saved\" style=\"margin-left:10px;color:#7bd87b;display:none;\">Сохранено ✔</span>
        </div>
        <div class=\"row\" style=\"margin-top:12px;color:#aaa;\">
          Приоритет: <code>GOPIAI_TERMINAL_UNSAFE</code> в среде > <code>settings.json</code>
        </div>
      </div>
      <script>
        async function refresh(){
          const r = await fetch('/settings/terminal_unsafe');
          const j = await r.json();
          document.getElementById('toggle').checked = !!j.enabled;
          document.getElementById('source').textContent = 'Источник: '+(j.source||'default');
          document.getElementById('saved').style.display = 'none';
        }
        document.getElementById('save').addEventListener('click', async()=>{
          const enabled = document.getElementById('toggle').checked;
          const r = await fetch('/settings/terminal_unsafe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({enabled})});
          const j = await r.json();
          if(!j.error){
            document.getElementById('saved').style.display = 'inline';
            document.getElementById('source').textContent = 'Источник: '+(j.source||'settings.json');
          } else {
            alert('Ошибка: '+j.error);
          }
        });
        refresh();
      </script>
    </body>
    </html>
    """
    return html

# Обработка сигналов для корректного завершения
def signal_handler(signum, frame):
    print(f"\n[SHUTDOWN] Received signal {signum}. Shutting down gracefully...")
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def cleanup_on_exit():
    print("[SHUTDOWN] Cleaning up resources...")
    logger.info("Cleaning up resources...")

if __name__ == '__main__':
    # [AUDIT] Разовая диагностика загруженных модулей с префиксом "gopiai."
    try:
        loaded = sorted([m for m in sys.modules.keys() if m.startswith("gopiai.")])
        print(f"[AUDIT][CREWAI] Loaded gopiai.* modules (pre-run): {loaded}")
        logging.getLogger(__name__).info("[AUDIT][CREWAI] Loaded gopiai.* modules (pre-run): %s", loaded)
    except Exception as _e:
        print(f"[AUDIT][CREWAI] Error while auditing modules: {_e}")
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_on_exit)
    
    print(f"[DIAGNOSTIC] __main__ block, SERVER_IS_READY = {SERVER_IS_READY}")
    # Всегда определяем и сохраняем выбранный порт ЗАРАНЕЕ, даже если SERVER_IS_READY = False
    try:
        env_port = os.getenv("GOPIAI_CREWAI_PORT") or os.getenv("CREWAI_PORT")
        base_port = int(env_port) if env_port else int(PORT)
    except Exception:
        base_port = int(PORT)
    # selected_port = _find_available_port(base_port, max_tries=20)
    selected_port = base_port
    if selected_port != base_port:
        logger.warning(f"[STARTUP] Порт {base_port} занят. Переключаемся на {selected_port}")
        print(f"[STARTUP] Порт {base_port} занят. Переключаемся на {selected_port}")
    # Обновляем глобальный PORT и сохраняем для UI/скриптов
    PORT = selected_port  # type: ignore
    _write_selected_port(PORT)

    if SERVER_IS_READY:
        print(f"[DIAGNOSTIC] Starting server on http://{HOST}:{PORT}")
        logger.info(f"[STARTUP] Server starting on http://{HOST}:{PORT}")
        try:
            print("[DIAGNOSTIC] Calling app.run()")

            # Дополнительно планируем аудит уже после старта (через отдельный поток-таймер)
            try:
                def _late_audit():
                    import time as _t
                    _t.sleep(3)
                    try:
                        late_loaded = sorted([m for m in sys.modules.keys() if m.startswith("gopiai.")])
                        print(f"[AUDIT][CREWAI] Loaded gopiai.* modules (post-run): {late_loaded}")
                        logging.getLogger(__name__).info("[AUDIT][CREWAI] Loaded gopiai.* modules (post-run): %s", late_loaded)
                    except Exception as __e:
                        print(f"[AUDIT][CREWAI] Error while late auditing modules: {__e}")
                threading.Thread(target=_late_audit, daemon=True).start()
            except Exception as __e:
                print(f"[AUDIT][CREWAI] Unable to schedule late audit: {__e}")

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

sys.exit(1)

# ASGI приложение для совместимости с uvicorn
asgi_app = WsgiToAsgi(app)

# --- END OF FILE crewai_api_server.py ---