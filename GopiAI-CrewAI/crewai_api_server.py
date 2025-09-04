# --- START OF FILE crewai_api_server.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

import logging
import os
import uuid
from typing import Any, Dict
from enum import Enum, auto # Добавлено auto для TaskStatus
from dotenv import load_dotenv
from pathlib import Path

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
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        """Убираем все проблемные символы из логов"""
        formatted = super().format(record)
        # Убираем ANSI escape codes
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        formatted = ansi_escape.sub('', formatted)
        
        # Убираем другие управляющие символы
        formatted = ''.join(char for char in formatted if ord(char) >= 32 or char in '\t\n')
        
        return formatted

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Применяем чистый форматтер ко всем хендлерам
clean_formatter = UltraCleanFormatter()
for handler in logging.getLogger().handlers:
    handler.setFormatter(clean_formatter)

logger = logging.getLogger(__name__)

# Подавляем ненужные логи от сторонних библиотек
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger.info("🚀 Запуск CrewAI API сервера...")
logger.info(f"📁 Логи сохраняются в: {log_file}")

from flask import Flask, request, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import traceback
from threading import Thread
import time
from flask_cors import CORS

# Импорт модулей CrewAI
try:
    logger.info("📦 Импорт модулей CrewAI...")
    from crewai import Agent, Task, Crew
    from crewai_tools import TavilySearchTool, WebsiteSearchTool
    from langchain_google_genai import ChatGoogleGenerativeAI
    logger.info("✅ Модули CrewAI успешно импортированы")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта CrewAI модулей: {e}")
    logger.error("💡 Убедитесь, что CrewAI установлен: pip install crewai crewai-tools langchain-google-genai")
    exit(1)

# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)

# Глобальное хранилище задач
tasks_storage = {}

# Инициализация Gemini LLM
try:
    logger.info("🤖 Инициализация Gemini LLM...")
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv('GEMINI_API_KEY'),
        temperature=0.7,
        convert_system_message_to_human=True
    )
    logger.info("✅ Gemini LLM успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Gemini LLM: {e}")
    logger.error("🔍 Проверьте GEMINI_API_KEY в .env файле")
    exit(1)

# Инициализация инструментов
try:
    logger.info("🔧 Инициализация инструментов...")
    search_tool = TavilySearchTool()
    website_tool = WebsiteSearchTool()
    logger.info("✅ Инструменты успешно инициализированы")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации инструментов: {e}")
    logger.error("🔍 Проверьте настройки API ключей в .env файле")
    # Не выходим из программы, создаем заглушки
    search_tool = None
    website_tool = None
    logger.warning("⚠️ Работаем без инструментов поиска")

def create_agent(role, goal, backstory):
    """Создание агента с обработкой ошибок"""
    try:
        logger.debug(f"👤 Создание агента: {role}")
        
        # Собираем доступные инструменты
        tools = []
        if search_tool:
            tools.append(search_tool)
        if website_tool:
            tools.append(website_tool)
        
        if not tools:
            logger.warning(f"⚠️ Агент {role} создается без инструментов")
        
        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            verbose=True,
            llm=gemini_llm
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
        
        if not request.json:
            return jsonify({'error': 'Отсутствует JSON данные'}), 400
            
        message = request.json.get('message', '')
        session_id = request.json.get('session_id', str(uuid.uuid4()))
        
        if not message:
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
        thread = Thread(target=process_message_async, args=(task_id, message))
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

def process_message_async(task_id, message):
    """Асинхронная обработка сообщения"""
    try:
        task = tasks_storage.get(task_id)
        if not task:
            return
            
        task['status'] = TaskStatus.PROCESSING
        task['progress'] = 10
        
        logger.info(f"🔄 Начата обработка задачи {task_id}")
        
        # Имитация обработки с простым ответом
        import time
        time.sleep(2)  # Имитация обработки
        
        response = f"Получено сообщение: '{message}'. Это базовый ответ от сервера."
        
        task['status'] = TaskStatus.COMPLETED
        task['progress'] = 100
        task['result'] = response
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
        logger.info("")
        logger.info("🚀 Сервер готов к работе на http://localhost:5052")
        logger.info("📁 Логи сохраняются в: " + log_file)
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