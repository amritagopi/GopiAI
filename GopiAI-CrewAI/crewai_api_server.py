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
import crewai_tools
from crewai import Agent, Crew, Task
from crewai_tools import TavilySearchTool, BraveSearchTool
# from tools.crewai_toolkit.tools import WebsiteSearchTool
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage
)
from langchain_core.tools import tool

# Local application imports  
from crewai import LLM
# The following import is inside a try-except block in the original code,
# which is good practice if the module is not always available.
# However, for consistency, we can try to import it here.
# If it causes issues, it should be moved back inside the function.
from tools.gopiai_integration.system_prompts import get_default_prompt
from response_refinement_integration import (
    ResponseRefinementService, iterative_refinement, quick_refine
)
from iterative_execution_system import (
    IterativeExecutor, process_message_iteratively
)
from llm_rotation_config import (
    select_llm_model_safe, rate_limit_monitor, get_api_key_for_provider
)


# --- НАЧАЛО ВАЖНОГО БЛОКА ---
# Четко указываем путь к .env файлу в той же папке, что и наш скрипт
env_path = Path(__file__).parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[DEBUG] Переменные окружения успешно загружены из: {env_path}")
    # Диагностический вывод: проверяем ключи
    tavily_key = os.getenv('TAVILY_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"[DEBUG] TAVILY_API_KEY: {'Ключ найден!' if tavily_key else 'КЛЮЧ НЕ НАЙДЕН!'}")
    print(f"[DEBUG] GEMINI_API_KEY: {'Ключ найден!' if gemini_key else 'КЛЮЧ НЕ НАЙДЕН!'}")
else:
    print(f"[ERROR] Файл .env не найден по пути: {env_path}")
# --- КОНЕЦ ВАЖНОГО БЛОКА ---

class TaskStatus(Enum): # Изменено: убрано str, добавлено Enum
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

# Настройка читаемого логирования для CrewAI сервера
# Логи переносим в $HOME/.gopiai/logs с гарантированным созданием каталога.
_LOG_DIR = Path.home() / ".gopiai" / "logs"
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception as _e:
    # В случае ошибки — fallback в текущий каталог
    print(f"[WARNING] Не удалось создать каталог логов {_LOG_DIR}: {_e}. Используем текущий каталог.")
    _LOG_DIR = Path(".")
# Используем два файла для логирования: общий и локальный
log_file = str(_LOG_DIR / "crewai_api_server_debug.log")
local_log_file = str(Path(__file__).parent / "crewai_api_server_debug_local.log")

class UltraCleanFormatter(logging.Formatter):
    """Форматтер который убирает ВСЕ нечитаемые символы"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        """Убираем все проблемные символы из логов"""
        formatted = super().format(record)
        # Убираем ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-9]*[ -/]*[@-~])')
        formatted = ansi_escape.sub('', formatted)
        
        # Убираем другие управляющие символы
        formatted = ''.join(char for char in formatted if ord(char) >= 32 or char in '\t\n')
        
        return formatted

# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Удаляем все существующие хендлеры, чтобы избежать дублирования
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Создаем форматтер
clean_formatter = UltraCleanFormatter()

# Хендлер для основного файла логов (перезаписывается при каждом запуске)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(clean_formatter)
logger.addHandler(file_handler)

# Хендлер для локального файла логов (перезаписывается при каждом запуске)
local_file_handler = logging.FileHandler(local_log_file, mode='w', encoding='utf-8')
local_file_handler.setFormatter(clean_formatter)
logger.addHandler(local_file_handler)

# Хендлер для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(clean_formatter)
logger.addHandler(console_handler)

# Применяем форматтер к корневому логгеру
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
root_logger.addHandler(console_handler)

# Подавляем ненужные логи от сторонних библиотек
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

# Глобальный список инструментов
all_tools = []

# Глобальное хранилище задач
tasks_storage = {}

# Состояние UI для синхронизации с model_selector_widget
ui_state = {
    "provider": "gemini",
    "model_id": None  # Будет выбрана динамически
}

@tool(description="Читает содержимое файла или папки")
def read_file_or_directory(path: str) -> str:
    """Читает содержимое файла или показывает содержимое директории."""
    try:
        if os.path.isfile(path):
            # Это файл - читаем его содержимое
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return f"Содержимое файла {path}:\n{content}"
        elif os.path.isdir(path):
            # Это директория - показываем список файлов
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
    
    class RiskLevel(Enum):
        SAFE = "safe"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    def assess_command_risk(command: str) -> RiskLevel:
        """Оценивает риск выполнения команды"""
        command_lower = command.lower().strip()
        
        # Критический риск - команды, которые могут нанести серьезный ущерб
        critical_patterns = [
            r'rm\s+.*-rf.*/',  # rm -rf с путями
            r'format\s+[cd]:',  # format диска
            r'del\s+/[fsq]',  # del с флагами
            r'shutdown',
            r'reboot',
            r'init\s+[06]',
            r'fdisk',
            r'mkfs',
            r'dd\s+.*=/dev/',
        ]
        
        # Высокий риск
        high_patterns = [
            r'sudo\s+rm',
            r'chmod\s+.*777',
            r'chown\s+.*root',
            r'rm\s+.*\*',
            r'kill\s+-9',
            r'pkill',
            r'killall',
            r'crontab\s+-r',
        ]
        
        # Средний риск
        medium_patterns = [
            r'sudo',
            r'pip\s+install',
            r'apt\s+install',
            r'wget',
            r'curl.*-o',
            r'git\s+clone',
            r'python.*\.py',
            r'bash.*\.sh',
            r'chmod',
            r'chown',
        ]
        
        # Низкий риск
        low_patterns = [
            r'cat\s+/etc/',
            r'less\s+/etc/',
            r'more\s+/etc/',
            r'tail\s+-f',
            r'head.*-n\s*\d+',
        ]
        
        # Безопасные команды (явно разрешенные)
        safe_patterns = [
            r'^ls(\s|$)',
            r'^pwd(\s|$)',
            r'^date(\s|$)',
            r'^whoami(\s|$)',
            r'^id(\s|$)',
            r'^uname(\s|$)',
            r'^which\s+\w+$',
            r'^echo\s+',
            r'^cat\s+[^/]',
            r'^head\s+[^/]',
            r'^tail\s+[^/]',
            r'^wc\s+',
            r'^grep\s+',
            r'^find\s+.*-name',
            r'^locate\s+',
        ]
        
        # Проверяем от самого опасного к безопасному
        for pattern in critical_patterns:
            if re.search(pattern, command_lower):
                return RiskLevel.CRITICAL
                
        for pattern in high_patterns:
            if re.search(pattern, command_lower):
                return RiskLevel.HIGH
                
        for pattern in medium_patterns:
            if re.search(pattern, command_lower):
                return RiskLevel.MEDIUM
                
        for pattern in low_patterns:
            if re.search(pattern, command_lower):
                return RiskLevel.LOW
                
        for pattern in safe_patterns:
            if re.search(pattern, command_lower):
                return RiskLevel.SAFE
        
        # Если команда не попала ни под один паттерн - средний риск
        return RiskLevel.MEDIUM
    
    def ask_user_permission(command: str, risk_level: RiskLevel) -> bool:
        """Запрашивает разрешение пользователя на выполнение команды"""
        if risk_level == RiskLevel.SAFE:
            return True
            
        # В серверном контексте автоматически разрешаем безопасные и низкорисковые команды
        # а для остальных возвращаем False с пояснением
        
        # В серверном режиме не можем запрашивать интерактивное подтверждение
        # поэтому блокируем все команды выше низкого риска
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return False
        
        return True  # Разрешаем только SAFE и LOW
    
    try:
        if not command or not command.strip():
            return "Пустая команда"
        
        command = command.strip()
        
        # Оцениваем риск команды
        risk_level = assess_command_risk(command)
        
        # Запрашиваем разрешение у пользователя для опасных команд
        if not ask_user_permission(command, risk_level):
            risk_msg = {
                RiskLevel.MEDIUM: "🟠 Команда среднего риска заблокирована",
                RiskLevel.HIGH: "🔴 Команда высокого риска заблокирована", 
                RiskLevel.CRITICAL: "💀 КРИТИЧЕСКИ ОПАСНАЯ команда заблокирована"
            }
            return f"{risk_msg.get(risk_level, 'Команда заблокирована')}: '{command}'. Для безопасности сервера выполнение таких команд запрещено."
        
        # Выполняем команду
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        
        if result.returncode == 0:
            if stdout:
                return f"Команда: {command}\nВывод:\n{stdout}"
            else:
                return f"Команда: {command}\nВыполнена успешно (без вывода)"
        else:
            return f"Ошибка выполнения команды '{command}' (код: {result.returncode}):\n{stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Таймаут при выполнении команды '{command}'"
    except Exception as e:
        return f"Ошибка выполнения команды '{command}': {str(e)}"

# Функция для создания LLM динамически
def create_llm(provider="gemini", model=None, temperature=0.7):
    """
    Создает LLM объект на основе переданных параметров
    Поддерживает ротацию моделей и провайдеров с использованием системы ротации
    """
    try:
        # Если модель не указана, выбираем динамически
        if model is None:
            from llm_rotation_config import select_llm_model_safe
            model = select_llm_model_safe("dialog")
            if not model:
                raise Exception("Нет доступных моделей для динамического выбора")
        
        logger.debug(f"🤖 Создание LLM: provider={provider}, model={model}")
        
        # Нормализуем модель для CrewAI формата
        if provider == "gemini" and model and not model.startswith("gemini/"):
            # Конвертируем UI формат в CrewAI формат
            if model.startswith("gemini-"):
                normalized_model = f"gemini/{model}"
            else:
                normalized_model = f"gemini/{model}"
        else:
            normalized_model = model
        
        logger.debug(f"DEBUG: Нормализованная модель: {normalized_model}")
        
        # Попробуем сначала использовать запрашиваемую модель
        try:
            # Создаем LLM с указанными параметрами
            llm = LLM(
                model=normalized_model,
                temperature=temperature
            )
            logger.debug(f"✅ LLM создан успешно: {normalized_model}")
            return llm
            
        except Exception as model_error:
            logger.warning(f"⚠️ Не удалось создать LLM с моделью {normalized_model}: {model_error}")
            
            # Используем систему ротации для выбора альтернативной модели
            try:
                logger.info("🔄 Используем систему ротации для выбора альтернативной модели")
                
                # Выбираем модель через систему ротации
                alternative_model = select_llm_model_safe(
                    task_type="general",
                    intelligence_priority=False,
                    exclude_models=[normalized_model]  # Исключаем неработающую модель
                )
                
                if alternative_model:
                    logger.info(f"🎯 Система ротации предложила модель: {alternative_model}")
                    
                    # Создаем LLM с альтернативной моделью
                    llm = LLM(
                        model=alternative_model,
                        temperature=temperature
                    )
                    
                    # Отмечаем использование модели в мониторе
                    rate_limit_monitor.register_use(alternative_model, tokens=0)
                    
                    logger.debug(f"✅ LLM создан с альтернативной моделью: {alternative_model}")
                    return llm
                    
            except Exception as rotation_error:
                logger.error(f"❌ Ошибка в системе ротации: {rotation_error}")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка создания LLM: {e}")
        logger.error(f"DEBUG: Полная ошибка: {traceback.format_exc()}")
        
    # Fallback на любую доступную модель как последний шанс
    try:
        from llm_rotation_config import select_llm_model_safe
        fallback_model = select_llm_model_safe("simple")  # Попробуем простую задачу
        if fallback_model:
            logger.warning(f"🔄 Последний шанс: пробуем fallback модель {fallback_model}")
            # Нормализуем модель
            if not fallback_model.startswith("gemini/"):
                fallback_model = f"gemini/{fallback_model}" if fallback_model.startswith("gemini-") else f"gemini/{fallback_model}"
            
            fallback_llm = LLM(
                model=fallback_model,
                temperature=temperature
            )
            return fallback_llm
        else:
            raise Exception("Нет доступных моделей для fallback")
    except Exception as fallback_error:
        logger.error(f"❌ Критическая ошибка: нет доступных моделей: {fallback_error}")
        raise

# Проверка доступности API ключей при старте
try:
    logger.info("🔧 Проверка доступности API...")
    logger.debug(f"DEBUG: GEMINI_API_KEY начинается с: {os.getenv('GEMINI_API_KEY', 'НЕТ')[:10]}...")
    
    # Создаем LLM для тестирования соединения (автоматический выбор)
    test_llm = create_llm("gemini")
    logger.info("✅ Проверка API прошла успешно")
    
except Exception as e:
    logger.error(f"❌ Ошибка проверки API: {e}")
    logger.error("🔍 Проверьте GEMINI_API_KEY в .env файле")
    exit(1)

# Response Refinement Service будет создаваться динамически при необходимости
logger.info("🔄 Response Refinement Service настроен для динамического создания")
refinement_service = None  # Будет создаваться по запросу

# Shared store для pending команд с thread-safe access
import threading
pending_commands_store = {}
pending_commands_lock = threading.Lock()

# Инициализация Iterative Execution System
try:
    logger.info("⚡ Инициализация Iterative Execution System...")
    iterative_executor = IterativeExecutor(pending_commands_store=pending_commands_store)
    iterative_executor.pending_commands_lock = pending_commands_lock
    logger.info("✅ Iterative Execution System успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Iterative Execution System: {e}")
    logger.error(f"DEBUG: Полная ошибка: {traceback.format_exc()}")
    iterative_executor = None
    logger.warning("⚠️ Сервер запущен без Iterative Execution System")

# Инициализация инструментов
try:
    logger.info("🔧 Инициализация инструментов...")
    all_tools = []
    try:
        search_tool = TavilySearchTool()
        all_tools.append(search_tool)
    except Exception as e:
        logger.warning(f"⚠️ TavilySearchTool failed to initialize: {e}")
        search_tool = None
    try:
        # website_tool = WebsiteSearchTool()  # Комментирую, модуль не найден
        # all_tools.append(website_tool)
        website_tool = None
        pass
    except Exception as e:
        logger.warning(f"⚠️ WebsiteSearchTool failed to initialize: {e}")
    try:
        brave_tool = BraveSearchTool()
        all_tools.append(brave_tool)
    except Exception as e:
        logger.warning(f"⚠️ BraveSearchTool failed to initialize: {e}")
        brave_tool = None
    all_tools.append(read_file_or_directory)
    all_tools.append(execute_terminal_command)
    logger.info("✅ Инструменты успешно инициализированы")
    logger.info(f"📋 Доступные инструменты: {[tool.__class__.__name__ for tool in all_tools]}")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации инструментов: {e}")
    logger.error("🔍 Проверьте настройки API ключей в .env файле")
    all_tools = [read_file_or_directory, execute_terminal_command]
    logger.warning("⚠️ Работаем с базовыми инструментами (без поиска)")

def create_agent(role, goal, backstory, llm=None):
    """Создание агента с обработкой ошибок"""
    try:
        logger.debug(f"👤 Создание агента: {role}")
        
        # Если LLM не передан, создаем дефолтный
        if llm is None:
            llm = create_llm("gemini")
        
        # Собираем доступные инструменты
        tools = []
        if search_tool:
            tools.append(search_tool)
        if website_tool:
            tools.append(website_tool)
        if brave_tool:
            tools.append(brave_tool)
        
        # Добавляем инструменты файловой системы и терминала
        tools.append(read_file_or_directory)
        tools.append(execute_terminal_command)
        
        if not tools:
            logger.warning(f"⚠️ Агент {role} создается без инструментов")
        
        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            verbose=True,
            llm=llm
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
                    # Проверяем наличие прикрепленных файлов
                    processed_attachments = metadata.get('processed_attachments', [])
                    
                    if processed_attachments:
                        logger.info(f"[MULTIMODAL] Обнаружено {len(processed_attachments)} прикрепленных файлов")
                        
                        # Формируем мультимодальный контент
                        multimodal_content = [{"type": "text", "text": message}]
                        
                        for attachment in processed_attachments:
                            if attachment['type'] == 'image':
                                # Добавляем изображение в формате для Gemini
                                multimodal_content.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": attachment['content']
                                    }
                                })
                                logger.info(f"[MULTIMODAL] Добавлено изображение: {attachment['name']}")
                            elif attachment['type'] == 'text':
                                # Добавляем текстовый файл как дополнительный контекст
                                file_content = f"\n\n--- Содержимое файла {attachment['name']} ---\n{attachment['content']}\n--- Конец файла ---\n"
                                if isinstance(multimodal_content[0]['text'], str):
                                    multimodal_content[0]['text'] += file_content
                                logger.info(f"[MULTIMODAL] Добавлен текстовый файл: {attachment['name']}")
                            elif attachment['type'] == 'error':
                                error_info = f"\n\n--- Ошибка обработки файла {attachment['name']} ---\n{attachment['content']}\n--- Конец информации об ошибке ---\n"
                                if isinstance(multimodal_content[0]['text'], str):
                                    multimodal_content[0]['text'] += error_info
                        
                        # Для мультимодального контента передаем структурированный объект
                        if len(multimodal_content) > 1:  # Есть не только текст
                            logger.info(f"[MULTIMODAL] Отправляем мультимодальный запрос в LLM")
                            response = self.llm.call(multimodal_content)
                        else:
                            # Только текст - стандартный вызов
                            response = self.llm.call(multimodal_content[0]['text'])
                    else:
                        # Стандартный текстовый запрос
                        response = self.llm.call(message)
                    
                    return str(response)
                    
                except Exception as e:
                    logger.error(f"Ошибка генерации ответа: {e}")
                    logger.error(f"Metadata: {metadata}")
                    return f"Ошибка: {str(e)}"
        
        # Получаем параметры модели из запроса или используем дефолтные
        provider = data.get('provider', 'gemini')
        # Выбираем модель динамически если не указана
        model_name = data.get('model')
        if not model_name:
            from llm_rotation_config import select_llm_model_safe
            model_name = select_llm_model_safe("dialog") or "gemini/gemini-1.5-flash"
        temperature = data.get('temperature', 0.7)
        
        # Создаем динамический LLM для этого запроса
        llm = create_llm(provider, model_name, temperature)
        llm_client = LLMClientAdapter(llm)
        
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

@app.route('/api/tools/toggle', methods=['POST'])
def toggle_tool():
    """Включение/выключение инструмента"""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        enabled = data.get('enabled', True)
        
        logger.debug(f"🔧 Переключение инструмента {tool_name}: {enabled}")
        
        # В текущей реализации инструменты всегда включены
        # Это заглушка для будущей функциональности
        return jsonify({
            'success': True,
            'message': f'Инструмент {tool_name} {"включен" if enabled else "выключен"}'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка переключения инструмента: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tools/set_key', methods=['POST'])
def set_tool_key():
    """Установка API ключа для инструмента"""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        api_key = data.get('api_key', '').strip()
        
        logger.debug(f"🔧 Установка API ключа для {tool_name}")
        
        # Определяем переменную окружения по имени инструмента
        env_var_map = {
            'Tavily Search': 'TAVILY_API_KEY',
            'tavily_search': 'TAVILY_API_KEY',
            'Website Search': 'FIRECRAWL_API_KEY', 
            'website_search': 'FIRECRAWL_API_KEY',
            'Gemini LLM': 'GEMINI_API_KEY',
            'llm_gemini': 'GEMINI_API_KEY'
        }
        
        env_var = env_var_map.get(tool_name)
        if not env_var:
            return jsonify({'error': f'Неизвестный инструмент: {tool_name}'}), 400
        
        # Путь к .env файлу
        env_path = Path(__file__).parent / '.env'
        
        # Читаем существующий .env файл
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # Обновляем или добавляем переменную
        var_found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f'{env_var}='):
                if api_key:
                    env_lines[i] = f'{env_var}={api_key}\n'
                else:
                    # Удаляем строку если ключ пустой
                    env_lines[i] = ''
                var_found = True
                break
        
        # Если переменная не найдена и ключ не пустой, добавляем
        if not var_found and api_key:
            env_lines.append(f'{env_var}={api_key}\n')
        
        # Записываем обратно в файл
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        
        # Обновляем переменную окружения в текущем процессе
        if api_key:
            os.environ[env_var] = api_key
        elif env_var in os.environ:
            del os.environ[env_var]
        
        action = "установлен" if api_key else "удален"
        logger.info(f"✅ API ключ для {tool_name} ({env_var}) {action}")
        
        return jsonify({
            'success': True,
            'message': f'API ключ для {tool_name} {action}'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка установки API ключа: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Получение списка доступных агентов"""
    try:
        logger.debug("🤖 Запрос списка агентов")
        agents_list = [
            # Исследование и анализ
            {
                'id': 'research_agent',
                'name': 'Исследователь',
                'description': 'Специалист по поиску и анализу информации из различных источников. Использует веб-поиск, анализирует данные, проводит факт-чекинг.',
                'role': 'researcher',
                'goal': 'Найти достоверную информацию и провести глубокий анализ',
                'category': 'research',
                'type': 'agent'
            },
            {
                'id': 'data_analyst',
                'name': 'Аналитик данных',
                'description': 'Специалист по анализу структурированных данных, создает отчеты, визуализации и выявляет закономерности в больших объемах информации.',
                'role': 'data_analyst', 
                'goal': 'Анализировать данные и создавать инсайты',
                'category': 'analytics',
                'type': 'agent'
            },
            
            # Создание контента
            {
                'id': 'writer_agent',
                'name': 'Писатель-копирайтер',
                'description': 'Эксперт по созданию качественного текстового контента: статьи, обзоры, описания, маркетинговые тексты. Адаптирует стиль под аудиторию.',
                'role': 'writer',
                'goal': 'Создать качественный и убедительный контент',
                'category': 'content',
                'type': 'agent'
            },
            {
                'id': 'technical_writer',
                'name': 'Технический писатель',
                'description': 'Специалист по технической документации, инструкциям, API документации. Умеет объяснять сложные технические концепции простым языком.',
                'role': 'technical_writer',
                'goal': 'Создать понятную техническую документацию',
                'category': 'documentation',
                'type': 'agent'
            },
            
            # Программирование и разработка
            {
                'id': 'code_analyst',
                'name': 'Аналитик кода',
                'description': 'Специалист по анализу, рефакторингу и оптимизации кода. Находит баги, предлагает улучшения архитектуры, проводит код-ревью.',
                'role': 'code_analyst',
                'goal': 'Улучшить качество и производительность кода',
                'category': 'development',
                'type': 'agent'
            },
            {
                'id': 'security_expert',
                'name': 'Эксперт по безопасности',
                'description': 'Специалист по информационной безопасности. Анализирует уязвимости, предлагает решения по защите, аудит безопасности.',
                'role': 'security_expert',
                'goal': 'Обеспечить безопасность системы',
                'category': 'security',
                'type': 'agent'
            },
            
            # Планирование и управление
            {
                'id': 'project_manager',
                'name': 'Менеджер проекта',
                'description': 'Специалист по планированию, координации задач, управлению ресурсами и сроками. Создает roadmap и отслеживает прогресс.',
                'role': 'project_manager',
                'goal': 'Организовать эффективное выполнение проекта',
                'category': 'management',
                'type': 'agent'
            },
            {
                'id': 'consultant',
                'name': 'Консультант-стратег',
                'description': 'Эксперт по стратегическому планированию и решению бизнес-задач. Предлагает оптимальные подходы и методологии.',
                'role': 'consultant',
                'goal': 'Предложить оптимальную стратегию решения задачи',
                'category': 'strategy',
                'type': 'agent'
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
        # UI отправляет 'model_id', но также поддерживаем 'model' для обратной совместимости
        # Получаем модель из запроса или выбираем динамически
        model = request.json.get('model_id') or request.json.get('model')
        if not model:
            from llm_rotation_config import select_llm_model_safe
            model = select_llm_model_safe("dialog") or "gemini/gemini-1.5-flash"
        
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
        
        # Используем итеративную систему выполнения для обработки сообщения и выполнения tool_code блоков
        logger.info(f"🤖 Запуск итеративного выполнения для: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        logger.debug(f"DEBUG: Полное сообщение: {message}")
        
        try:
            # Создаем LLM client adapter для итеративного исполнителя
            class CrewAILLMAdapter:
                def __init__(self, llm, provider='gemini', temperature=0.7):
                    self.llm = llm
                    self.provider = provider
                    self.temperature = temperature
                    self.original_model = getattr(llm, 'model', None)
                    logger.debug(f"DEBUG: Создан CrewAI LLM адаптер с моделью: {self.original_model}")
                
                def generate_response(self, message_text, metadata):
                    try:
                        logger.debug("DEBUG: Получение системного промпта для итеративного выполнения")
                        from tools.gopiai_integration.system_prompts import get_iterative_execution_prompt
                        system_prompt = get_iterative_execution_prompt()
                        logger.debug(f"DEBUG: Системный промпт получен: {system_prompt[:100]}...")
                        
                        # Формируем полное сообщение с системным промптом и историей
                        formatted_message = f"System: {system_prompt}\n"
                        
                        # Добавляем историю чата (последние 10 сообщений для контекста)
                        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
                        for hist_msg in recent_history:
                            role = hist_msg.get('role')
                            content = hist_msg.get('content', '')
                            if role == 'user':
                                formatted_message += f"Human: {content}\n"
                            elif role == 'assistant':
                                formatted_message += f"Assistant: {content}\n"
                        
                        # Добавляем текущее сообщение
                        formatted_message += f"Human: {message_text}\n"
                        
                        logger.debug("DEBUG: Вызов LLM.call() через адаптер")
                        response = self.llm.call(formatted_message)
                        
                        logger.debug(f"DEBUG: Ответ от LLM: {str(response)[:200]}...")
                        return str(response)
                        
                    except Exception as e:
                        logger.error(f"Ошибка генерации ответа в адаптере: {e}")
                        
                        # Проверяем, является ли это ошибкой превышения квоты или перегрузки модели
                        error_str = str(e)
                        is_rate_limit_error = (
                            "RateLimitError" in error_str or 
                            "429" in error_str or 
                            "quota" in error_str.lower() or
                            "rate limit" in error_str.lower() or
                            "overloaded" in error_str.lower() or
                            "503" in error_str or
                            "UNAVAILABLE" in error_str or
                            "VertexAIException" in error_str
                        )
                        
                        if is_rate_limit_error:
                            # Определяем тип ошибки для более точного логирования
                            if "overloaded" in error_str.lower() or "503" in error_str or "UNAVAILABLE" in error_str:
                                logger.warning(f"🚨 Обнаружена перегрузка модели: {error_str[:200]}")
                            else:
                                logger.warning(f"🚨 Обнаружена ошибка превышения лимитов: {error_str[:200]}")
                            
                            # Получаем текущую модель и помечаем как недоступную
                            try:
                                from llm_rotation_config import rate_limit_monitor
                                current_model = getattr(self.llm, 'model', None)
                                if current_model:
                                    logger.warning(f"🔄 Помечаем модель {current_model} как недоступную из-за перегрузки/лимитов")
                                    rate_limit_monitor.mark_model_unavailable(current_model)
                                else:
                                    logger.warning("⚠️ Не удалось определить текущую модель для блокировки")
                            except Exception as mark_error:
                                logger.error(f"Ошибка маркировки модели как недоступной: {mark_error}")
                            
                            # Пытаемся переключиться на другую модель и повторить запрос
                            if self._switch_to_alternative_model():
                                logger.info("🔄 Повторяем запрос с новой моделью после обнаружения проблем с текущей")
                                try:
                                    # Повторяем запрос с новой моделью
                                    response = self.llm.call(formatted_message)
                                    logger.info(f"✅ Успешный ответ от новой модели: {getattr(self.llm, 'model', 'unknown')}")
                                    return str(response)
                                except Exception as retry_error:
                                    logger.error(f"❌ Ошибка даже с новой моделью: {retry_error}")
                                    return f"Ошибка: Не удалось получить ответ даже после переключения модели: {str(retry_error)}"
                            else:
                                logger.error("❌ Не удалось найти альтернативную модель")
                                return "Ошибка: Все доступные модели временно недоступны. Попробуйте позже."
                        
                        # Для других ошибок возвращаем обычное сообщение об ошибке
                        return f"Ошибка: {str(e)}"
                
                def _switch_to_alternative_model(self) -> bool:
                    """Переключается на альтернативную модель при превышении лимитов"""
                    try:
                        from llm_rotation_config import select_llm_model_safe
                        
                        # Выбираем новую модель
                        new_model = select_llm_model_safe("dialog")
                        if new_model and new_model != self.original_model:
                            logger.info(f"🔄 Переключаемся с {self.original_model} на {new_model}")
                            
                            # Создаем новый LLM с альтернативной моделью
                            new_llm = create_llm(self.provider, new_model, self.temperature)
                            if new_llm:
                                self.llm = new_llm
                                logger.info(f"✅ Успешно переключились на модель: {new_model}")
                                return True
                            else:
                                logger.error(f"❌ Не удалось создать LLM для модели: {new_model}")
                                return False
                        else:
                            logger.warning(f"⚠️ Нет доступной альтернативной модели (текущая: {self.original_model})")
                            return False
                    except Exception as switch_error:
                        logger.error(f"❌ Ошибка переключения модели: {switch_error}")
                        return False
            
            # Получаем параметры модели из запроса или используем дефолтные
            provider = request_data.get('provider', 'gemini')
            # UI отправляет 'model_id', но также поддерживаем 'model' для обратной совместимости
            # Получаем модель из запроса или выбираем динамически
            model_name = request_data.get('model_id') or request_data.get('model')
            if not model_name:
                from llm_rotation_config import select_llm_model_safe
                model_name = select_llm_model_safe("dialog") or "gemini/gemini-1.5-flash"
            temperature = request_data.get('temperature', 0.7)
            
            # Создаем динамический LLM для этого запроса
            llm = create_llm(provider, model_name, temperature)
            
            # Создаем адаптер LLM с параметрами для переключения моделей
            llm_client = CrewAILLMAdapter(llm, provider, temperature)
            
            # Запускаем итеративное выполнение
            logger.info("⚡ Запуск итеративного исполнителя")
            result = iterative_executor.process_iteratively(
                message, 
                llm_client, 
                metadata
            )
            
            # Получаем финальный результат
            result_text = result['final_response']
            logger.info(f"✅ Итеративное выполнение завершено за {result['iterations_count']} итераций")
            logger.debug(f"DEBUG: История выполнения: {len(result['execution_history'])} команд")
            
        except Exception as execution_error:
            logger.error(f"❌ Ошибка итеративного выполнения: {execution_error}")
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            
            # Проверяем, является ли это ошибкой лимитов/перегрузки модели
            error_str = str(execution_error)
            is_model_issue = (
                "RateLimitError" in error_str or 
                "429" in error_str or 
                "quota" in error_str.lower() or
                "rate limit" in error_str.lower() or
                "overloaded" in error_str.lower() or
                "503" in error_str or
                "UNAVAILABLE" in error_str or
                "VertexAIException" in error_str or
                "RESOURCE_EXHAUSTED" in error_str
            )
            
            if is_model_issue:
                logger.warning(f"🚨 Обнаружена проблема с моделью - пытаемся переключиться на альтернативную")
                
                # Пытаемся создать новый LLM с другой моделью
                try:
                    from llm_rotation_config import select_llm_model_safe, rate_limit_monitor
                    
                    # Помечаем текущую модель как недоступную
                    current_model = getattr(llm, 'model', None)
                    if current_model:
                        logger.warning(f"🔄 Помечаем модель {current_model} как недоступную")
                        rate_limit_monitor.mark_model_unavailable(current_model)
                    
                    # Выбираем альтернативную модель
                    alternative_model = select_llm_model_safe("dialog", intelligence_priority=False)
                    if alternative_model:
                        logger.info(f"🔄 Пытаемся переключиться на модель: {alternative_model}")
                        
                        # Создаем новый LLM с альтернативной моделью
                        alternative_llm = create_llm(provider, alternative_model, temperature)
                        alternative_client = CrewAILLMAdapter(alternative_llm, provider, temperature)
                        
                        # Повторяем попытку с новой моделью
                        logger.info("🔄 Повторяем итеративное выполнение с новой моделью")
                        result = iterative_executor.process_iteratively(
                            message, 
                            alternative_client, 
                            metadata
                        )
                        
                        result_text = result['final_response']
                        logger.info(f"✅ Успешно обработано с альтернативной моделью: {alternative_model}")
                        
                    else:
                        logger.error("❌ Нет доступных альтернативных моделей")
                        result_text = "Извините, все модели временно недоступны. Попробуйте позже."
                        
                except Exception as retry_error:
                    logger.error(f"❌ Ошибка при попытке переключения модели: {retry_error}")
                    result_text = "Извините, произошла ошибка при обработке запроса. Все модели временно недоступны."
            else:
                # Для других типов ошибок используем обычное сообщение
                result_text = f'Извините, произошла ошибка при обработке: {str(execution_error)}'
        
        # Проверяем, что получили ответ
        if not result_text:
            result_text = "Извините, не удалось получить ответ от модели."
                
        logger.info(f"✅ Получен финальный ответ: '{result_text[:100]}{'...' if len(result_text) > 100 else ''}')")
        
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

# ==========================================
# Internal endpoints for UI synchronization
# ==========================================

@app.route('/internal/state', methods=['GET', 'POST'])
def handle_internal_state():
    """Управление состоянием UI (провайдер/модель) для синхронизации с model_selector_widget"""
    global ui_state
    
    if request.method == 'GET':
        logger.debug(f"DEBUG: /internal/state GET - текущее состояние: {ui_state}")
        return jsonify(ui_state)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Отсутствует JSON данные'}), 400
            
            if 'provider' in data:
                ui_state['provider'] = data['provider']
            if 'model_id' in data:
                ui_state['model_id'] = data['model_id']
                
            logger.debug(f"DEBUG: /internal/state POST - обновлено состояние: {ui_state}")
            return jsonify(ui_state)
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния UI: {e}")
            return jsonify({'error': 'Ошибка обновления состояния'}), 500

@app.route('/internal/models', methods=['GET'])  
def handle_internal_models():
    """Получение списка моделей для указанного провайдера"""
    try:
        provider = request.args.get('provider', 'gemini')
        logger.debug(f"DEBUG: /internal/models GET - провайдер: {provider}")
        
        # Получаем модели через систему ротации (с перезагрузкой модуля)
        import importlib
        import llm_rotation_config
        importlib.reload(llm_rotation_config)
        from llm_rotation_config import get_available_models
        
        models = []
        for model in get_available_models("dialog"):
            # Поддерживаем оба формата: "gemini" и "google" 
            if model.get("provider") in [provider, "google"] or (provider == "gemini" and model.get("provider") == "google"):
                models.append({
                    "id": model["id"],
                    "display_name": model.get("name", model["id"]),
                    "provider": model["provider"]
                })
        
        logger.debug(f"DEBUG: Найдено {len(models)} моделей для провайдера {provider}")
        return jsonify(models)
        
    except Exception as e:
        logger.error(f"Ошибка получения моделей: {e}")
        return jsonify({'error': 'Ошибка получения моделей'}), 500

# === API ЭНДПОИНТЫ ДЛЯ УПРАВЛЕНИЯ ПОДТВЕРЖДЕНИЯМИ КОМАНД ===

@app.route('/api/commands/pending', methods=['GET'])
def get_pending_commands():
    """Получить список команд, ожидающих подтверждения"""
    try:
        with pending_commands_lock:
            pending = {cmd_id: cmd_info for cmd_id, cmd_info in pending_commands_store.items() 
                      if cmd_info.get('status') == 'pending'}
        
        logger.debug(f"[APPROVAL-API] Запрос pending команд: {len(pending)} найдено")
        return jsonify({
            'success': True,
            'pending_commands': pending
        })
    except Exception as e:
        logger.error(f"[APPROVAL-API] Ошибка при получении pending команд: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands/<command_id>/approve', methods=['POST'])
def approve_command(command_id):
    """Подтвердить выполнение команды"""
    try:
        with pending_commands_lock:
            if command_id in pending_commands_store:
                pending_commands_store[command_id]['status'] = 'approved'
                pending_commands_store[command_id]['approved_at'] = time.time()
                logger.info(f"[APPROVAL-API] Команда {command_id} подтверждена пользователем")
                return jsonify({'success': True, 'message': 'Command approved'})
            else:
                logger.warning(f"[APPROVAL-API] Команда {command_id} не найдена для подтверждения")
                return jsonify({'success': False, 'error': 'Command not found'}), 404
    except Exception as e:
        logger.error(f"[APPROVAL-API] Ошибка при подтверждении команды {command_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands/<command_id>/reject', methods=['POST'])
def reject_command(command_id):
    """Отклонить выполнение команды"""
    try:
        with pending_commands_lock:
            if command_id in pending_commands_store:
                pending_commands_store[command_id]['status'] = 'rejected'
                pending_commands_store[command_id]['rejected_at'] = time.time()
                logger.info(f"[APPROVAL-API] Команда {command_id} отклонена пользователем")
                return jsonify({'success': True, 'message': 'Command rejected'})
            else:
                logger.warning(f"[APPROVAL-API] Команда {command_id} не найдена для отклонения")
                return jsonify({'success': False, 'error': 'Command not found'}), 404
    except Exception as e:
        logger.error(f"[APPROVAL-API] Ошибка при отклонении команды {command_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands/status', methods=['GET'])
def get_commands_status():
    """Получить статистику по командам"""
    try:
        with pending_commands_lock:
            total = len(pending_commands_store)
            pending = sum(1 for cmd in pending_commands_store.values() if cmd.get('status') == 'pending')
            approved = sum(1 for cmd in pending_commands_store.values() if cmd.get('status') == 'approved')
            rejected = sum(1 for cmd in pending_commands_store.values() if cmd.get('status') == 'rejected')
        
        return jsonify({
            'success': True,
            'statistics': {
                'total': total,
                'pending': pending,
                'approved': approved,
                'rejected': rejected
            }
        })
    except Exception as e:
        logger.error(f"[APPROVAL-API] Ошибка при получении статистики команд: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# === ОБРАБОТЧИКИ ОШИБОК ===

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
            '/api/tasks/<id> [GET]',
            '/api/tools [GET]',
            '/api/agents [GET]',
            '/api/process [POST]',
            '/api/commands/pending [GET]',
            '/api/commands/<id>/approve [POST]',
            '/api/commands/<id>/reject [POST]',
            '/api/commands/status [GET]',
            '/internal/state [GET, POST]',
            '/internal/models [GET]'
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
        logger.info("✅ Запуск Flask сервера...")
        logger.info("🔗 Доступные endpoints:")
        logger.info("   GET  /api/health - проверка здоровья сервера")
        logger.info("   GET  /health - проверка здоровья сервера (legacy)")
        logger.info("   POST /api/tasks - создание новой задачи")
        logger.info("   GET  /api/tasks - список всех задач")
        logger.info("   GET  /api/tasks/<id> - статус конкретной задачи")
        logger.info("   POST /api/refine - итеративная обработка ответов")
        logger.info("   POST /api/iterate - итеративное выполнение команд")
        logger.info("   GET/POST /internal/state - управление состоянием UI")
        logger.info("   GET  /internal/models - получение списка моделей")
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
        logger.info("👋 Получен сигнал остановки (Ctrl+C)")
        logger.info("🔄 Завершение работы сервера...")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка запуска сервера: {e}")
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
    finally:
        logger.info("👋 CrewAI API Server остановлен")

# --- END OF FILE crewai_api_server.py ---
