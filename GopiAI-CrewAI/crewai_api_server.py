# --- START OF FILE crewai_api_server.py (ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

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
# ВАЖНО: BraveSearchTool теперь импортируется из crewai_tools, если он там есть,
# или используется ваша локальная версия, если она необходима.
# Для простоты предположим, что все поисковые инструменты из crewai_tools.
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

# ВАЖНО: Импортируем официальный LLM-враппер от LangChain
from langchain_google_genai import ChatGoogleGenerativeAI

# Local application imports
# ВАЖНО: Удаляем импорт вашего кастомного `create_crewai_gemini_llm`
from tools.gopiai_integration.system_prompts import get_default_prompt
# Эти импорты пока оставим, так как они используются в других эндпоинтах
from response_refinement_integration import ResponseRefinementService
from iterative_execution_system import IterativeExecutor

# --- НАЧАЛО ВАЖНОГО БЛОКА ---
# Четко указываем путь к .env файлу в той же папке, что и наш скрипт
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[DEBUG] Переменные окружения успешно загружены из: {env_path}")
else:
    print(f"[ERROR] Файл .env не найден по пути: {env_path}")
# --- КОНЕЦ ВАЖНОГО БЛОКА ---

# ... (весь код для логирования и TaskStatus остается без изменений) ...
# Настройка логирования (оставляем как есть)
logger = logging.getLogger(__name__)
# ... (пропустим код настройки логгера для краткости) ...


# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)

# Глобальное хранилище задач
tasks_storage = {}

# --- Инструменты ---
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

@tool(description="Выполняет команду в терминале")
def execute_terminal_command(command: str) -> str:
    """Выполняет команду в терминале. Используйте с осторожностью."""
    # Упрощенная версия для предсказуемости
    if not command or not command.strip():
        return "Ошибка: пустая команда."
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if not output:
            return "Команда выполнена успешно, но не дала вывода."
        return output
    except Exception as e:
        return f"Ошибка выполнения команды '{command}': {str(e)}"

# --- Инициализация LLM и инструментов ---

# ВАЖНО: Инициализируем LLM через официальный класс
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        verbose=True,
        temperature=0.7,
    )
    logger.info("✅ Официальный Gemini LLM от LangChain инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Gemini LLM: {e}")
    llm = None

# Инициализация инструментов
all_tools = []
try:
    # Добавляем поисковые инструменты
    all_tools.append(TavilySearchTool())
    # all_tools.append(WebsiteSearchTool()) # Можно добавить по необходимости
    # all_tools.append(BraveSearchTool())   # Можно добавить по необходимости

    # Добавляем локальные инструменты
    all_tools.append(read_file_or_directory)
    all_tools.append(execute_terminal_command)
    logger.info(f"✅ Инструменты успешно инициализированы: {[tool.name for tool in all_tools]}")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации инструментов: {e}")
    all_tools = []


# ВАЖНО: Привязываем инструменты к LLM
if llm and all_tools:
    llm_with_tools = llm.bind_tools(all_tools)
    logger.info("✅ Инструменты успешно привязаны к LLM")
else:
    llm_with_tools = llm # Работаем без инструментов, если что-то пошло не так
    logger.warning("⚠️ LLM или инструменты не были инициализированы. Работаем без привязки инструментов.")


# --- Основной эндпоинт для обработки сообщений ---
@app.route('/api/process', methods=['POST'])
def process_message():
    if not llm_with_tools:
        return jsonify({'error': 'LLM не инициализирован, проверьте логи сервера'}), 503

    data = request.get_json()
    message_text = data.get('message', '')
    if not message_text:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    # ВАЖНО: Упрощенный вызов для демонстрации
    # Создаем агента "на лету" для выполнения задачи
    # В полноценной системе здесь была бы более сложная логика
    assistant_agent = Agent(
        role='Многофункциональный ассистент',
        goal='Точно и полно отвечать на запросы пользователя, используя все доступные инструменты.',
        backstory='Вы - продвинутый ИИ-ассистент, способный искать информацию в интернете, работать с файловой системой и выполнять команды в терминале для решения задач пользователя.',
        llm=llm_with_tools, # Передаем LLM с привязанными инструментами
        tools=all_tools,    # И сами инструменты
        verbose=True,
        allow_delegation=False
    )

    task = Task(
        description=f"Ответь на следующий запрос от пользователя: '{message_text}'",
        agent=assistant_agent,
        expected_output="Полный и исчерпывающий ответ на запрос пользователя."
    )

    # Запускаем выполнение в отдельном потоке, чтобы не блокировать ответ
    def run_task():
        try:
            result = task.execute()
            # В реальном приложении здесь была бы логика сохранения результата
            print(f"Результат выполнения задачи: {result}")
        except Exception as e:
            print(f"Ошибка выполнения задачи: {e}")

    # Для простоты примера, мы вернем ответ сразу, но в идеале
    # нужно использовать систему задач, как у вас уже было
    try:
        result = task.execute()
        return jsonify({'response': result})
    except Exception as e:
        logger.error(f"Ошибка выполнения Crew: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# --- Остальные эндпоинты (можно оставить или адаптировать) ---
# ... (Ваши эндпоинты /api/tasks, /api/health и т.д. можно оставить здесь,
# но их нужно будет адаптировать для работы с новой логикой `llm_with_tools`) ...


if __name__ == '__main__':
    if not llm:
        logger.error("💥 КРИТИЧЕСКАЯ ОШИБКА: Не удалось инициализировать LLM. Сервер не может быть запущен.")
    else:
        logger.info("🌟 Запуск Flask сервера...")
        app.run(host='0.0.0.0', port=5052, debug=False)
