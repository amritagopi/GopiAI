# --- START OF FILE crewai_api_server.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

# Standard library imports
import logging
import os
import re
import subprocess
import time
import traceback
import uuid
from enum import Enum, auto
from pathlib import Path
from threading import Thread

# Third-party imports
from crewai import Agent, Crew, Task
from crewai_tools import TavilySearchTool, WebsiteSearchTool
from tools.crewai_toolkit.tools import BraveSearchTool
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage, ToolMessage
)
from langchain_core.tools import tool

# Local application imports
# ВАЖНО: Импортируем официальный LLM-враппер от LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
# ВАЖНО: УДАЛЕН импорт вашего кастомного `create_crewai_gemini_llm`
from tools.gopiai_integration.system_prompts import get_default_prompt
from response_refinement_integration import (
    ResponseRefinementService, iterative_refinement, quick_refine
)
from iterative_execution_system import (
    IterativeExecutor, process_message_iteratively
)


# --- НАЧАЛО ВАЖНОГО БЛОКА ---
# Четко указываем путь к .env файлу в той же папке, что и наш скрипт
env_path = Path(__file__).parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[DEBUG] Переменные окружения успешно загружены из: {env_path}")
    # Диагностический вывод: проверяем ключи
    brave_key = os.getenv('BRAVE_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"[DEBUG] BRAVE_API_KEY: {'Ключ найден!' if brave_key else 'КЛЮЧ НЕ НАЙДЕН!'}")
    print(f"[DEBUG] GEMINI_API_KEY: {'Ключ найден!' if gemini_key else 'КЛЮЧ НЕ НАЙДЕН!'}")
else:
    print(f"[ERROR] Файл .env не найден по пути: {env_path}")
# --- КОНЕЦ ВАЖНОГО БЛОКА ---

class TaskStatus(Enum): # Изменено: убрано str, добавлено Enum
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

# Настройка читаемого логирования для CrewAI сервера (оставлено без изменений)
_LOG_DIR = Path.home() / ".gopiai" / "logs"
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception as _e:
    print(f"[WARNING] Не удалось создать каталог логов {_LOG_DIR}: {_e}. Используем текущий каталог.")
    _LOG_DIR = Path(".")
log_file = str(_LOG_DIR / "crewai_api_server_debug.log")
local_log_file = str(Path(__file__).parent / "crewai_api_server_debug_local.log")

class UltraCleanFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    def format(self, record):
        formatted = super().format(record)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|[[0-9]*[ -/]*[@-~])')
        formatted = ansi_escape.sub('', formatted)
        formatted = ''.join(char for char in formatted if ord(char) >= 32 or char in '\t\n')
        return formatted

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
clean_formatter = UltraCleanFormatter()
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(clean_formatter)
logger.addHandler(file_handler)
local_file_handler = logging.FileHandler(local_log_file, mode='w', encoding='utf-8')
local_file_handler.setFormatter(clean_formatter)
logger.addHandler(local_file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(clean_formatter)
logger.addHandler(console_handler)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
root_logger.addHandler(console_handler)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger.info("🚀 Запуск CrewAI API сервера...")
logger.info(f"📁 Логи сохраняются в: {log_file}")
logger.info(f"📁 Локальные логи: {local_log_file}")
logger.debug("DEBUG: Детальное логирование включено")

# Import the more advanced refinement crew after logger is initialized
try:
    from crews.refinement_crew.refinement_crew import iterative_refinement as advanced_refinement
    logger.info("✅ Импорт продвинутой refinement crew успешен")
except ImportError as e:
    logger.warning(f"⚠️ Не удалось импортировать продвинутую refinement crew: {e}")
    advanced_refinement = None

# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)

# Глобальное хранилище задач
tasks_storage = {}

@tool(description="Читает содержимое файла или папки")
def read_file_or_directory(path: str) -> str:
    """Читает содержимое файла или показывает содержимое директории."""
    try:
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f"Содержимое файла {path}:\n{f.read()}"
        elif os.path.isdir(path):
            items = os.listdir(path)
            items_list = '\n'.join(f"{('📁' if os.path.isdir(os.path.join(path, item)) else '📄')} {item}" for item in sorted(items))
            return f"Содержимое папки {path}:\n{items_list}"
        else:
            return f"Путь {path} не существует или недоступен"
    except Exception as e:
        return f"Ошибка при чтении {path}: {str(e)}"

@tool(description="Выполняет команду в терминале с интерактивным контролем безопасности")
def execute_terminal_command(command: str) -> str:
    """Выполняет команду в терминале с умной оценкой рисков и запросом подтверждения для опасных команд."""
    # ... (код функции execute_terminal_command оставлен без изменений) ...
    class RiskLevel(Enum):
        SAFE = "safe"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    def assess_command_risk(command: str) -> RiskLevel:
        command_lower = command.lower().strip()
        critical_patterns = [r'rm\s+.*-rf.*/', r'format\s+[cd]:', r'del\s+/[fsq]', r'shutdown', r'reboot', r'init\s+[06]', r'fdisk', r'mkfs', r'dd\s+.*=/dev/']
        high_patterns = [r'sudo\s+rm', r'chmod\s+.*777', r'chown\s+.*root', r'rm\s+.*\*', r'kill\s+-9', r'pkill', r'killall', r'crontab\s+-r']
        medium_patterns = [r'sudo', r'pip\s+install', r'apt\s+install', r'wget', r'curl.*-o', r'git\s+clone', r'python.*\.py', r'bash.*\.sh', r'chmod', r'chown']
        low_patterns = [r'cat\s+/etc/', r'less\s+/etc/', r'more\s+/etc/', r'tail\s+-f', r'head.*-n\s*\d+']
        safe_patterns = [r'^ls(\s|$)', r'^pwd(\s|$)', r'^date(\s|$)', r'^whoami(\s|$)', r'^id(\s|$)', r'^uname(\s|$)', r'^which\s+\w+$', r'^echo\s+', r'^cat\s+[^/]', r'^head\s+[^/]', r'^tail\s+[^/]', r'^wc\s+', r'^grep\s+', r'^find\s+.*-name', r'^locate\s+']
        for pattern in critical_patterns:
            if re.search(pattern, command_lower): return RiskLevel.CRITICAL
        for pattern in high_patterns:
            if re.search(pattern, command_lower): return RiskLevel.HIGH
        for pattern in medium_patterns:
            if re.search(pattern, command_lower): return RiskLevel.MEDIUM
        for pattern in low_patterns:
            if re.search(pattern, command_lower): return RiskLevel.LOW
        for pattern in safe_patterns:
            if re.search(pattern, command_lower): return RiskLevel.SAFE
        return RiskLevel.MEDIUM
    
    def ask_user_permission(command: str, risk_level: RiskLevel) -> bool:
        if risk_level == RiskLevel.SAFE: return True
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]: return False
        return True

    try:
        if not command or not command.strip(): return "Пустая команда"
        command = command.strip()
        risk_level = assess_command_risk(command)
        if not ask_user_permission(command, risk_level):
            risk_msg = {RiskLevel.MEDIUM: "🟠 Команда среднего риска заблокирована", RiskLevel.HIGH: "🔴 Команда высокого риска заблокирована", RiskLevel.CRITICAL: "💀 КРИТИЧЕСКИ ОПАСНАЯ команда заблокирована"}
            return f"{risk_msg.get(risk_level, 'Команда заблокирована')}: '{command}'. Для безопасности сервера выполнение таких команд запрещено."
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=os.getcwd())
        stdout, stderr = result.stdout or "", result.stderr or ""
        if result.returncode == 0:
            return f"Команда: {command}\nВывод:\n{stdout}" if stdout else f"Команда: {command}\nВыполнена успешно (без вывода)"
        else:
            return f"Ошибка выполнения команды '{command}' (код: {result.returncode}):\n{stderr}"
    except subprocess.TimeoutExpired:
        return f"Таймаут при выполнении команды '{command}'"
    except Exception as e:
        return f"Ошибка выполнения команды '{command}': {str(e)}"

# ВАЖНО: Новый, исправленный блок инициализации LLM и инструментов
gemini_llm = None
try:
    logger.info("🤖 Инициализация официального Gemini LLM...")
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", verbose=True, temperature=0.7)
    logger.info("✅ Gemini LLM успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Gemini LLM: {e}")
    logger.error(f"DEBUG: Полная ошибка: {traceback.format_exc()}")
    logger.error("🔍 Проверьте GEMINI_API_KEY в .env файле")
    # exit(1) # Не выходим, чтобы сервер мог запуститься и показать ошибку в UI

# Инициализация инструментов
all_tools = []
try:
    logger.info("🔧 Инициализация инструментов...")
    # ВАЖНО: Заменяем Tavily на Brave, как просил пользователь
    all_tools.append(BraveSearchTool())
    all_tools.append(WebsiteSearchTool())

    # Добавляем локальные инструменты
    all_tools.append(read_file_or_directory)
    all_tools.append(execute_terminal_command)
    logger.info(f"✅ Инструменты успешно инициализированы: {[tool.name for tool in all_tools]}")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации инструментов: {e}")
    logger.error("🔍 Проверьте API ключи для инструментов в .env файле (например, BRAVE_API_KEY)")
    all_tools = []

# ВАЖНО: Привязываем инструменты к LLM, если все инициализировалось успешно
if gemini_llm and all_tools:
    gemini_llm.bind_tools(all_tools)
    logger.info("✅ Инструменты успешно привязаны к LLM.")
else:
    logger.warning("⚠️ LLM или инструменты не были инициализированы. Инструменты не будут работать.")


# Инициализация Response Refinement Service
try:
    logger.info("🔄 Инициализация Response Refinement Service...")
    refinement_service = ResponseRefinementService(llm=gemini_llm)
    logger.info("✅ Response Refinement Service успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Response Refinement Service: {e}")
    refinement_service = None
    logger.warning("⚠️ Сервер запущен без Response Refinement Service")

# Инициализация Iterative Execution System
try:
    logger.info("⚡ Инициализация Iterative Execution System...")
    iterative_executor = IterativeExecutor()
    logger.info("✅ Iterative Execution System успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Iterative Execution System: {e}")
    iterative_executor = None
    logger.warning("⚠️ Сервер запущен без Iterative Execution System")

def create_agent(role, goal, backstory):
    """Создание агента с обработкой ошибок"""
    try:
        logger.debug(f"👤 Создание агента: {role}")
        
        if not all_tools:
            logger.warning(f"⚠️ Агент {role} создается без инструментов")
        
        # ВАЖНО: Убеждаемся, что агент получает LLM с уже привязанными инструментами
        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=all_tools, # Передаем список инструментов
            verbose=True,
            llm=gemini_llm # Передаем LLM (уже с привязанными инструментами)
        )
        logger.debug(f"✅ Агент {role} успешно создан")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания агента {role}: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        raise

def execute_crew_task(task_data):
    """Выполнение задачи через CrewAI с подробным логированием"""
    task_id = task_data['task_id']
    
    try:
        logger.info(f"🎯 Начинаем выполнение задачи {task_id}")
        
        # Обновляем статус задачи
        tasks_storage[task_id]['status'] = TaskStatus.PROCESSING
        tasks_storage[task_id]['progress'] = 'Инициализация агентов...'
        
        # Создание агентов
        logger.info("👥 Создание команды агентов...")
        
        researcher = create_agent(
            role="Исследователь",
            goal="Найти и проанализировать информацию по заданной теме",
            backstory="Вы опытный исследователь с навыками поиска и анализа информации."
        )
        
        analyst = create_agent(
            role="Аналитик",
            goal="Проанализировать найденную информацию и сделать выводы",
            backstory="Вы профессиональный аналитик с опытом обработки данных."
        )
        
        # Обновляем прогресс
        tasks_storage[task_id]['progress'] = 'Создание задач...'
        
        # Создание задач
        logger.info("📋 Создание задач для команды...")
        
        research_task = Task(
            description=f"Исследуйте тему: {task_data['description']}. Найдите актуальную информацию и ключевые факты.",
            agent=researcher,
            expected_output="Подробный отчет с найденной информацией и источниками"
        )
        
        analysis_task = Task(
            description=f"Проанализируйте найденную информацию по теме: {task_data['description']}. Сделайте выводы и рекомендации.",
            agent=analyst,
            expected_output="Аналитический отчет с выводами и рекомендациями"
        )
        
        # Обновляем прогресс
        tasks_storage[task_id]['progress'] = 'Запуск команды...'
        
        # Создание и запуск команды
        logger.info("🚀 Запуск команды CrewAI...")
        
        crew = Crew(
            agents=[researcher, analyst],
            tasks=[research_task, analysis_task],
            verbose=True
        )
        
        # Выполнение задач
        logger.info("⚡ Команда начинает работу...")
        tasks_storage[task_id]['progress'] = 'Выполнение задач...'
        
        result = crew.kickoff()
        
        # Сохраняем результат
        logger.info(f"✅ Задача {task_id} успешно выполнена")
        
        tasks_storage[task_id]['status'] = TaskStatus.COMPLETED
        tasks_storage[task_id]['result'] = str(result)
        tasks_storage[task_id]['progress'] = 'Завершено'
        tasks_storage[task_id]['completed_at'] = time.time()
        
        logger.info(f"📊 Результат сохранен для задачи {task_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка выполнения задачи {task_id}: {e}")
        logger.error(f"🔍 Полная трассировка: {traceback.format_exc()}")
        
        tasks_storage[task_id]['status'] = TaskStatus.FAILED
        tasks_storage[task_id]['error'] = str(e)
        tasks_storage[task_id]['progress'] = f'Ошибка: {str(e)}'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    logger.debug("🔍 Health check запрос")
    return jsonify({
        'status': 'healthy',
        'service': 'CrewAI API Server',
        'timestamp': time.time()
    })

@app.route('/health', methods=['GET'])
def health_check_legacy():
    """Проверка здоровья сервера (legacy)"""
    logger.debug("🔍 Health check запрос (legacy)")
    return jsonify({
        'status': 'healthy',
        'service': 'CrewAI API Server',
        'timestamp': time.time()
    })

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создание новой задачи"""
    try:
        logger.info("📝 Получен запрос на создание задачи")
        
        data = request.get_json()
        if not data or 'description' not in data:
            logger.error("❌ Неверный формат данных в запросе")
            return jsonify({'error': 'Требуется поле description'}), 400
        
        # Генерация ID задачи
        task_id = str(uuid.uuid4())
        logger.info(f"🆔 Создана задача с ID: {task_id}")
        
        # Сохранение задачи
        task_data = {
            'task_id': task_id,
            'description': data['description'],
            'created_at': time.time(),
            'status': TaskStatus.PENDING,
            'progress': 'Ожидание выполнения'
        }
        
        tasks_storage[task_id] = task_data
        logger.debug(f"💾 Задача {task_id} сохранена в хранилище")
        
        # Запуск выполнения в отдельном потоке
        logger.info(f"🎬 Запуск задачи {task_id} в фоновом режиме")
        thread = Thread(target=execute_crew_task, args=(task_data,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': TaskStatus.PENDING.name,
            'message': 'Задача создана и поставлена в очередь на выполнение'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания задачи: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Получение статуса задачи"""
    try:
        logger.debug(f"📊 Запрос статуса задачи: {task_id}")
        
        if task_id not in tasks_storage:
            logger.warning(f"⚠️ Задача {task_id} не найдена")
            return jsonify({'error': 'Задача не найдена'}), 404
        
        task = tasks_storage[task_id]
        
        response = {
            'task_id': task_id,
            'status': task['status'].name,
            'progress': task['progress'],
            'created_at': task['created_at']
        }
        
        if task['status'] == TaskStatus.COMPLETED:
            response['result'] = task['result']
            response['completed_at'] = task['completed_at']
        elif task['status'] == TaskStatus.FAILED:
            response['error'] = task['error']
        
        logger.debug(f"📤 Отправляем статус задачи {task_id}: {task['status'].name}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса задачи {task_id}: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """Получение списка всех задач"""
    try:
        logger.debug("📋 Запрос списка всех задач")
        
        tasks_list = []
        for task_id, task in tasks_storage.items():
            task_info = {
                'task_id': task_id,
                'description': task['description'],
                'status': task['status'].name,
                'progress': task['progress'],
                'created_at': task['created_at']
            }
            
            if task['status'] == TaskStatus.COMPLETED:
                task_info['completed_at'] = task['completed_at']
            elif task['status'] == TaskStatus.FAILED:
                task_info['error'] = task['error']
                
            tasks_list.append(task_info)
        
        logger.debug(f"📤 Отправляем список из {len(tasks_list)} задач")
        return jsonify({'tasks': tasks_list, 'count': len(tasks_list)})
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка задач: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/refine', methods=['POST'])
def refine_response():
    """Итеративная обработка ответа с использованием Response Refinement"""
    try:
        logger.info("🔄 Получен запрос на итеративную обработку ответа")
        
        data = request.get_json()
        if not data or 'content' not in data:
            logger.error("❌ Неверный формат данных в запросе на рефайнмент")
            return jsonify({'error': 'Требуется поле content для обработки'}), 400
        
        if not refinement_service:
            logger.error("❌ Response Refinement Service недоступен")
            return jsonify({'error': 'Сервис итеративной обработки недоступен'}), 503
        
        content = data['content']
        refinement_type = data.get('type', 'auto')  # auto, crew, simple, advanced
        max_rounds = data.get('max_rounds', 4)
        context = data.get('context', '')
        
        logger.info(f"🎯 Обработка контента типом: {refinement_type}, макс. итераций: {max_rounds}")
        
        # Выполняем итеративную обработку
        try:
            if refinement_type == 'advanced' and advanced_refinement:
                # Используем продвинутую систему с таймаутами и оптимизациями
                refined_result, history = advanced_refinement(
                    query=content, 
                    context=context, 
                    max_rounds=min(max_rounds, 3),  # Ограничиваем для производительности
                    timeout_per_iteration=60
                )
                # История не используется в ответе для краткости
            elif refinement_type == 'crew':
                refined_result = refinement_service.refine_with_crew(content, max_rounds)
            elif refinement_type == 'simple':
                refined_result, history = refinement_service.refine_simple(content, max_rounds)
            else:  # auto
                # Автоматический выбор: если длинный запрос или файловая операция - используем advanced
                if advanced_refinement and (len(content) > 200 or any(word in content.lower() for word in ['файл', 'папка', 'директория', 'file', 'folder', 'directory'])):
                    refined_result, _ = advanced_refinement(content, context, max_rounds=2)
                else:
                    refined_result = refinement_service.auto_refine(content, 'simple')
            
            logger.info(f"✅ Итеративная обработка завершена успешно")
            
            return jsonify({
                'original_content': content,
                'refined_result': refined_result,
                'refinement_type': refinement_type,
                'max_rounds_used': max_rounds,
                'status': 'completed'
            })
            
        except Exception as refine_error:
            logger.error(f"❌ Ошибка при итеративной обработке: {refine_error}")
            return jsonify({
                'error': f'Ошибка обработки: {str(refine_error)}',
                'original_content': content
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Общая ошибка endpoint рефайнмента: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/iterate', methods=['POST'])
def iterate_execution():
    """Итеративное выполнение команд с интерактивной обработкой"""
    try:
        logger.info("⚡ Получен запрос на итеративное выполнение")
        
        data = request.get_json()
        if not data or 'message' not in data:
            logger.error("❌ Неверный формат данных в запросе на итерацию")
            return jsonify({'error': 'Требуется поле message для обработки'}), 400
        
        if not iterative_executor:
            logger.error("❌ Iterative Execution System недоступен")
            return jsonify({'error': 'Система итеративного выполнения недоступна'}), 503
        
        message = data['message']
        metadata = data.get('metadata', {})
        
        logger.info(f"🎯 Итеративная обработка сообщения: {message[:100]}...")
        
        # Создаем простой LLM client adapter
        class LLMClientAdapter:
            def __init__(self, llm):
                self.llm = llm
            
            def generate_response(self, message, metadata):
                try:
                    messages = [{"role": "user", "content": message}]
                    response = self.llm.invoke(messages)
                    return response.content if hasattr(response, 'content') else str(response)
                except Exception as e:
                    logger.error(f"Ошибка генерации ответа: {e}")
                    return f"Ошибка: {str(e)}"
        
        llm_client = LLMClientAdapter(gemini_llm)
        
        # Выполняем итеративную обработку
        try:
            result = iterative_executor.process_iteratively(message, llm_client, metadata)
            
            logger.info(f"✅ Итеративная обработка завершена. Итераций: {result['iterations_count']}")
            
            return jsonify({
                'final_response': result['final_response'],
                'iterations_count': result['iterations_count'],
                'execution_history': result['execution_history'],
                'success': result['success'],
                'status': 'completed'
            })
            
        except Exception as iter_error:
            logger.error(f"❌ Ошибка при итеративной обработке: {iter_error}")
            return jsonify({
                'error': f'Ошибка обработки: {str(iter_error)}',
                'original_message': message
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Общая ошибка endpoint итераций: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

# Добавленные endpoints для совместимости с UI
@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Получение списка доступных инструментов"""
    try:
        logger.debug("🔧 Запрос списка инструментов")
        tools_list = [
            {
                'id': 'tavily_search',
                'name': 'Tavily Search',
                'description': 'Поиск в интернете с помощью Tavily API',
                'category': 'search'
            },
            {
                'id': 'website_search',
                'name': 'Website Search', 
                'description': 'Поиск информации на конкретных веб-сайтах',
                'category': 'search'
            },
            {
                'id': 'llm_gemini',
                'name': 'Gemini LLM',
                'description': 'Google Gemini языковая модель',
                'category': 'llm'
            }
        ]
        
        return jsonify({
            'tools': tools_list,
            'count': len(tools_list)
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка инструментов: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Получение списка доступных агентов"""
    try:
        logger.debug("🤖 Запрос списка агентов")
        agents_list = [
            {
                'id': 'research_agent',
                'name': 'Research Agent',
                'description': 'Агент для проведения исследований и анализа информации',
                'role': 'researcher',
                'goal': 'Найти и проанализировать релевантную информацию'
            },
            {
                'id': 'writer_agent',
                'name': 'Writer Agent', 
                'description': 'Агент для создания текстового контента',
                'role': 'writer',
                'goal': 'Создать качественный и структурированный контент'
            }
        ]
        
        return jsonify({
            'agents': agents_list,
            'count': len(agents_list)
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка агентов: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/process', methods=['POST'])
def process_message():
    """Основной endpoint для обработки сообщений"""
    try:
        logger.debug("💬 Запрос на обработку сообщения")
        logger.debug(f"DEBUG: Получен request.json: {request.json}")
        
        if not request.json:
            logger.error("DEBUG: Отсутствует JSON данные в запросе")
            return jsonify({'error': 'Отсутствует JSON данные'}), 400
            
        message = request.json.get('message', '')
        session_id = request.json.get('session_id', str(uuid.uuid4()))
        provider = request.json.get('provider', 'gemini')
        model = request.json.get('model', 'gemini-2.0-flash')
        
        logger.debug(f"DEBUG: Извлеченные данные - message: '{message[:100]}...', session_id: {session_id}, provider: {provider}, model: {model}")
        
        if not message:
            logger.error("DEBUG: Сообщение пустое")
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Создаем задачу обработки
        task_id = str(uuid.uuid4())
        task_data = {
            'task_id': task_id,
            'session_id': session_id,
            'description': f'Обработка сообщения: {message[:50]}...' if len(message) > 50 else message,
            'status': TaskStatus.PENDING,
            'progress': 0,
            'created_at': time.time(),
            'message': message
        }
        
        tasks_storage[task_id] = task_data
        
        logger.info(f"📝 Создана задача обработки сообщения: {task_id}")
        
        # Запускаем обработку в отдельном потоке
        thread = Thread(target=process_message_async, args=(task_id, request.json))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'session_id': session_id,
            'status': 'processing',
            'message': 'Сообщение принято к обработке'
        }), 202
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

def process_message_async(task_id, request_data):
    """Асинхронная обработка сообщения с использованием Gemini LLM"""
    try:
        logger.debug(f"DEBUG: Входим в process_message_async для task_id: {task_id}")
        task = tasks_storage.get(task_id)
        if not task:
            logger.error(f"DEBUG: Задача {task_id} не найдена в хранилище")
            return
            
        task['status'] = TaskStatus.PROCESSING
        task['progress'] = 10
        logger.debug(f"DEBUG: Статус задачи {task_id} изменен на PROCESSING")
        
        logger.info(f"🔄 Начата обработка задачи {task_id}")
        
        # Извлекаем данные из запроса
        message = request_data.get('message', '')
        metadata = request_data.get('metadata', {})
        chat_history = metadata.get('chat_history', [])
        
        logger.debug(f"DEBUG: Получена chat_history с {len(chat_history)} сообщениями")
        
        # Обращение к Gemini LLM для получения реального ответа
        logger.info(f"🤖 Отправка сообщения в Gemini: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        logger.debug(f"DEBUG: Полное сообщение: {message}")
        
        try:
            logger.debug("DEBUG: Начинается импорт модулей langchain")
            # Используем инициализированный gemini_llm для обработки сообщения
            logger.debug("DEBUG: Импорт модулей langchain завершен")
            
            # Добавляем системный промпт с личностью ассистента
            logger.debug("DEBUG: Получение системного промпта")
            system_prompt = get_default_prompt()
            logger.debug(f"DEBUG: Системный промпт получен: {system_prompt[:100]}...")
            
            # Начинаем с системного промпта
            messages = [SystemMessage(content=system_prompt)]
            
            # Добавляем историю чата (последние 20 сообщений)
            for hist_msg in chat_history:
                role = hist_msg.get('role')
                content = hist_msg.get('content', '')
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    messages.append(AIMessage(content=content))
            
            # Добавляем текущее сообщение пользователя
            messages.append(HumanMessage(content=message))
            
            logger.debug(f"DEBUG: Сформированы сообщения для отправки: {len(messages)} сообщений (системное + {len(chat_history)} историческое + 1 текущее)")
            
            logger.debug("DEBUG: Вызов gemini_llm.invoke()")
            response = gemini_llm.invoke(messages)
            logger.debug(f"DEBUG: Получен ответ от gemini_llm: type={type(response)}")
            logger.debug(f"DEBUG: Содержимое ответа: {response.content[:200] if hasattr(response, 'content') else 'НЕТ КОНТЕНТА'}...")
            
            logger.info(f"📊 Ответ получен. Tool calls: {len(response.tool_calls) if response.tool_calls else 0}")
            
            # Если есть tool calls, выполняем их
            if response.tool_calls:
                logger.info(f"🔧 Выполнение {len(response.tool_calls)} tool calls...")
                
                # Добавляем ответ модели в историю
                messages.append(response)
                
                # Выполняем каждый tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]
                    
                    logger.info(f"🔧 Выполняем {tool_name} с аргументами: {tool_args}")
                    
                    # Выполняем функцию в зависимости от её имени
                    try:
                        if tool_name == "read_file_or_directory":
                            tool_result = read_file_or_directory.invoke(tool_args)
                        elif tool_name == "execute_terminal_command":
                            tool_result = execute_terminal_command.invoke(tool_args)
                        else:
                            tool_result = f"Неизвестный инструмент: {tool_name}"
                        
                        logger.info(f"✅ Результат {tool_name}: {tool_result[:100]}{'...' if len(tool_result) > 100 else ''}")
                        
                        # Добавляем результат выполнения инструмента
                        messages.append(ToolMessage(
                            content=tool_result,
                            tool_call_id=tool_id
                        ))
                        
                    except Exception as tool_error:
                        logger.error(f"❌ Ошибка выполнения {tool_name}: {tool_error}")
                        messages.append(ToolMessage(
                            content=f"Ошибка при выполнении {tool_name}: {str(tool_error)}",
                            tool_call_id=tool_id
                        ))
                
                # Получаем финальный ответ от модели с учетом результатов инструментов
                final_response = gemini_llm.invoke(messages)
                result_text = final_response.content
                
            else:
                # Нет tool calls - используем обычный ответ
                result_text = response.content
                
            logger.info(f"✅ Получен финальный ответ от Gemini: '{result_text[:100]}{'...' if len(result_text) > 100 else ''}'")
            
        except Exception as llm_error:
            logger.error(f"❌ Ошибка при обращении к Gemini LLM: {llm_error}")
            result_text = f"Извините, произошла ошибка при обработке вашего сообщения: {str(llm_error)}"
        
        task['status'] = TaskStatus.COMPLETED
        task['progress'] = 100
        task['result'] = result_text
        task['completed_at'] = time.time()
        
        logger.info(f"✅ Задача {task_id} завершена успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при асинхронной обработке задачи {task_id}: {e}")
        task = tasks_storage.get(task_id)
        if task:
            task['status'] = TaskStatus.FAILED
            task['error'] = str(e)

@app.errorhandler(404)
def not_found(error):
    """Обработчик 404 ошибок"""
    logger.warning(f"🔍 404: Путь не найден - {request.path}")
    return jsonify({
        'error': 'Путь не найден',
        'path': request.path,
        'available_endpoints': [
            '/api/health',
            '/health (legacy)',
            '/api/tasks [POST, GET]',
            '/api/tasks/<task_id> [GET]',
            '/api/tools [GET]',
            '/api/agents [GET]',
            '/api/process [POST]'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500 ошибок"""
    logger.error(f"💥 500: Внутренняя ошибка сервера - {error}")
    return jsonify({
        'error': 'Внутренняя ошибка сервера',
        'message': 'Проверьте логи для получения подробной информации'
    }), 500

if __name__ == '__main__':
    try:
        logger.info("🌟 Запуск Flask сервера...")
        logger.info("🔗 Доступные endpoints:")
        logger.info("   GET  /api/health - проверка здоровья сервера")
        logger.info("   GET  /health - проверка здоровья сервера (legacy)")
        logger.info("   POST /api/tasks - создание новой задачи")
        logger.info("   GET  /api/tasks - список всех задач")
        logger.info("   GET  /api/tasks/<id> - статус конкретной задачи")
        logger.info("   POST /api/refine - итеративная обработка ответов")
        logger.info("   POST /api/iterate - итеративное выполнение команд")
        logger.info("")
        logger.info("🚀 Сервер готов к работе на http://localhost:5052")
        logger.info(f"📁 Логи сохраняются в: {log_file}")
        logger.info("⚡ Для остановки нажмите Ctrl+C")
        
        app.run(
            host='0.0.0.0',
            port=5052,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки (Ctrl+C)")
        logger.info("🔄 Завершение работы сервера...")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка запуска сервера: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
    finally:
        logger.info("👋 CrewAI API Server остановлен")

# --- END OF FILE crewai_api_server.py ---
