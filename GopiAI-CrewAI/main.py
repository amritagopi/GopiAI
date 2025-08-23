#!/usr/bin/env python3
"""
🚀 GopiAI-CrewAI Advanced Integration
Полная интеграция CrewAI с GopiAI системой и всеми инструментами
"""

import os
import sys
import yaml
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))  # GOPI_AI_MODULES
sys.path.append(str(current_dir))  # GopiAI-CrewAI
sys.path.append(str(current_dir / 'tools'))  # tools directory

# Загружаем переменные окружения (.env из нескольких локаций)
from dotenv import load_dotenv

def _load_env_multi():
    """Поддержка загрузки .env из типичных путей, чтобы .exe работал "из коробки".
    Приоритет: CWD → script dir → parent → exe dir.
    Каждая найденная .env загружается с override=True.
    """
    candidates = []

    # 1) Явный путь
    
    if custom:
        p = Path(custom)
        if p.is_file():
            candidates.append(p)
        elif p.is_dir():
            candidates.append(p / '.env')

    # 2) Текущая директория
    candidates.append(Path.cwd() / '.env')

    # 3) Директория скрипта
    candidates.append(current_dir / '.env')

    # 4) Родительская директория
    candidates.append(current_dir.parent / '.env')

    # 5) Директория исполняемого файла (актуально для упакованного .exe)
    exe_dir = Path(getattr(sys, 'frozen', False) and Path(sys.executable).parent or current_dir)
    candidates.append(exe_dir / '.env')

    loaded = False
    for path in candidates:
        try:
            if path and path.is_file():
                load_dotenv(path, override=True)
                print(f"✅ .env загружен: {path}")
                loaded = True
        except Exception as e:
            print(f"⚠️ Не удалось загрузить .env ({path}): {e}")
    if not loaded:
        print("ℹ️ .env не найден (это не критично)")

_load_env_multi()

# Импорт CrewAI
from crewai import Agent, Task, Crew, LLM
from tools.gopiai_integration.ai_router_llm import AIRouterLLM
from crewai.tasks.task_output import TaskOutput

# Импорт RAG системы
from rag_system import RAGSystem, get_rag_system

# Импорт всех GopiAI инструментов
try:
    from tools.gopiai_integration.base.base_tool import GopiAIBaseTool
    from tools.gopiai_integration.browser_tools import GopiAIBrowserTool
    from tools.gopiai_integration.filesystem_tools import GopiAIFileSystemTool
    from tools.gopiai_integration.ai_router_tools import GopiAIRouterTool
    from tools.gopiai_integration.memory_tools import GopiAIMemoryTool
    from tools.gopiai_integration.communication_tools import GopiAICommunicationTool
    from tools.gopiai_integration.huggingface_tools import GopiAIHuggingFaceTool
    from tools.gopiai_integration.terminal_tool import TerminalTool
    
    # Импорт системы динамических инструкций
    from tools.gopiai_integration.crewai_tools_integration import (
        enhance_crew_with_instructions,
        enhance_agent_with_instructions,
        with_dynamic_instructions,
        get_tools_integrator
    )
    from tools.gopiai_integration.tools_instruction_manager import get_tools_instruction_manager
    
    print("🔍 === ПРОВЕРКА ОКРУЖЕНИЯ ===")
    print("✅ Система динамических инструкций загружена")
except ImportError as e:
    print(f"❌ Ошибка импорта инструментов: {e}")
    sys.exit(1)

def check_environment():
    """Проверка окружения и ключей API"""
    print("🔍 === ПРОВЕРКА ОКРУЖЕНИЯ ===")
    
    # Проверяем .env файл
    if env_path.exists():
        print(f"✅ .env файл найден: {env_path}")
    else:
        print(f"❌ .env файл не найден: {env_path}")
        return False
    
    # Проверяем ключи API
    api_keys = {
        'GEMINI_API_KEY': {'prefix': 'AIza', 'name': 'Google Gemini'},
    }
    
    available_providers = []
    
    for key_name, config in api_keys.items():
        key_value = os.getenv(key_name)
        if key_value and key_value.strip() and key_value != "your_key_here":
            prefix_ok = True
            if config['prefix']:
                prefix_ok = key_value.startswith(config['prefix'])
            
            status = "✅" if prefix_ok else "⚠️"
            print(f"   {config['name']}: {status} {'(ключ найден)' if prefix_ok else '(неверный формат)'}")
            
            if prefix_ok:
                available_providers.append(config['name'])
        else:
            print(f"   {config['name']}: ❌ отсутствует")
    
    if not available_providers:
        print("❌ Нет доступных провайдеров!")
        return False
    
    print(f"✅ Доступные провайдеры: {', '.join(available_providers)}")
    return True

def test_all_tools():
    """Тестирование всех GopiAI инструментов"""
    print("🧪 === ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ ===")
    
    tools_results = {}
    
    # Тест Communication Tool
    try:
        print("📡 Тестирование Communication Tool...")
        comm_tool = GopiAICommunicationTool()
        result = comm_tool._run("notify", "", "Система запущена", "info", 3, "{}")
        tools_results['communication'] = True
        print(f"✅ Communication: {result}")
    except Exception as e:
        tools_results['communication'] = False
        print(f"❌ Communication ошибка: {e}")
    
    # Тест Memory Tool
    try:
        print("🧠 Тестирование Memory Tool...")
        memory_tool = GopiAIMemoryTool()
        result = memory_tool._run("store", "system_test", "Тест системы памяти", "general", 5)
        tools_results['memory'] = True
        print(f"✅ Memory: {result}")
    except Exception as e:
        tools_results['memory'] = False
        print(f"❌ Memory ошибка: {e}")
    
    # Тест FileSystem Tool
    try:
        print("📁 Тестирование FileSystem Tool...")
        fs_tool = GopiAIFileSystemTool()
        result = fs_tool._run("list", ".")
        tools_results['filesystem'] = True
        if isinstance(result, list):
            print(f"✅ FileSystem: найдено {len(result)} элементов")
        else:
            print(f"✅ FileSystem: {result}")
    except Exception as e:
        tools_results['filesystem'] = False
        print(f"❌ FileSystem ошибка: {e}")
    
    # Тест Browser Tool (может не работать без интернета)
    try:
        print("🌐 Тестирование Browser Tool...")
        browser_tool = GopiAIBrowserTool()
        result = browser_tool._run("search", "CrewAI", "", 3)
        tools_results['browser'] = True
        print(f"✅ Browser: {result[:50]}...")
    except Exception as e:
        tools_results['browser'] = False
        print(f"⚠️ Browser ошибка (нормально без интернета): {e}")
    
    # Тест AI Router Tool
    try:
        print("🔀 Тестирование AI Router Tool...")
        router_tool = GopiAIRouterTool()
        result = router_tool._run(message="Привет!", task_type="chat")
        tools_results['router'] = True
        print(f"✅ Router: {result[:50]}...")
    except Exception as e:
        tools_results['router'] = False
        print(f"❌ Router ошибка: {e}")
    
    # Тест HuggingFace Tool  
    try:
        print("🤗 Тестирование HuggingFace Tool...")
        hf_tool = GopiAIHuggingFaceTool()
        result = hf_tool._run("Привет!", "microsoft/DialoGPT-large", "conversational", 100, 0.7)
        tools_results['huggingface'] = True
        print(f"✅ HuggingFace: {result[:50]}...")
    except Exception as e:
        tools_results['huggingface'] = False
        print(f"❌ HuggingFace ошибка: {e}")
    
    working_tools = sum(tools_results.values())
    total_tools = len(tools_results)
    
    print(f"📊 Результат: {working_tools}/{total_tools} инструментов работают")
    return working_tools > 0

from tools.gopiai_integration.agent_templates import AgentTemplateSystem
from crewai import Agent
from llm_rotation_config import LLM_MODELS_CONFIG, select_llm_model, rag_answer

def create_demo_agents(llm):
    """Создание демонстрационных агентов с GopiAI инструментами и динамическими инструкциями"""
    print("👥 === СОЗДАНИЕ АГЕНТОВ С ДИНАМИЧЕСКИМИ ИНСТРУКЦИЯМИ ===")
    
    # Инициализируем систему динамических инструкций
    tools_manager = get_tools_instruction_manager()
    integrator = get_tools_integrator()
    
    print("📖 Доступные инструменты с динамическими инструкциями:")
    tools_summary = tools_manager.get_tools_summary()
    for tool_name, description in tools_summary.items():
        print(f"  • {tool_name}: {description[:60]}...")
    
    # Используем систему шаблонов для создания агентов
    template_system = AgentTemplateSystem(verbose=True)
    print(f"\n📋 Доступные шаблоны: {', '.join(template_system.list_available_templates())}")
    
    # Создаем агентов из шаблонов
    coordinator = template_system.create_agent_from_template(
        "coordinator_agent", 
        llm,
        team_size=3,
        verbose=True
    )
    
    researcher = template_system.create_agent_from_template(
        "researcher_agent",
        llm,
        topic="GopiAI интеграция с CrewAI",
        verbose=True
    )
    
    writer = template_system.create_agent_from_template(
        "writer_agent",
        llm,
        topic="Многоагентные системы",
        format="markdown",
        creativity_level="high",
        verbose=True
    )
    
    # Создаем агента-программиста вручную для демонстрации динамических инструкций
    # Создаем все инструменты
    all_tools = [
        GopiAICommunicationTool(),
        GopiAIMemoryTool(),
        GopiAIFileSystemTool(),
        GopiAIBrowserTool(),
        GopiAIRouterTool(),
        GopiAIHuggingFaceTool(),
        TerminalTool(),
    ]
    
    # ЯВНО привязываем инструменты к LLM, чтобы исключить галлюцинации tool-calls
    llm_bound = llm
    try:
        if hasattr(llm, "bind_tools") and callable(getattr(llm, "bind_tools")):
            llm_bound = llm.bind_tools(all_tools)
            print(f"🔗 LLM привязан к {len(all_tools)} инструментам через .bind_tools() (main.py)")
        else:
            print("ℹ️ .bind_tools() недоступен у LLM — используем исходный экземпляр")
    except Exception as e:
        print(f"⚠️ Не удалось выполнить .bind_tools() для LLM: {e}")
    
    # Агент-программист (полный набор инструментов)
    coder = Agent(
        role='Code Developer with Dynamic Instructions',
        goal='Разрабатывать и оптимизировать код на Python с использованием динамических инструкций',
        backstory="""Ты опытный Python-разработчик в GopiAI с доступом к системе динамических инструкций.
        Когда ты выбираешь инструмент, система автоматически подгружает детальные инструкции по его использованию.
        Твоя задача - писать чистый, эффективный и хорошо документированный код для различных компонентов системы.""",
        tools=all_tools,
        llm=llm_bound,
        verbose=True,
        allow_delegation=True,
        max_iter=5
    )
    
    # Улучшаем всех агентов динамическими инструкциями
    print("\n🔧 Применение динамических инструкций к агентам...")
    coordinator = enhance_agent_with_instructions(coordinator)
    researcher = enhance_agent_with_instructions(researcher)
    writer = enhance_agent_with_instructions(writer)
    coder = enhance_agent_with_instructions(coder)
    
    print(f"✅ Создано {len([coordinator, researcher, writer, coder])} агентов с динамическими инструкциями")
    return coordinator, researcher, writer, coder

def create_demo_tasks(coordinator, researcher, writer, coder):
    """Создание демонстрационных задач"""
    print("📋 === СОЗДАНИЕ ЗАДАЧ ===")
    # Проверка на None для всех агентов
    if not all([coordinator, researcher, writer, coder]):
        print("❌ Ошибка: Один или несколько агентов не созданы. Проверьте шаблоны агентов!")
        return None, None, None, None
    # Задача 1: Инициализация проекта
    init_task = Task(
        description="""Инициализируй новый проект GopiAI-CrewAI интеграции.
        
        Выполни следующие действия:
        1. Отправь уведомление о запуске проекта
        2. Сохрани в память информацию о проекте (категория: "project")
        3. Проверь статус системы
        4. Создай список задач для команды
        
        Ключевая информация для сохранения:
        - Название: "GopiAI-CrewAI Integration Demo"
        - Дата запуска: текущая дата
        - Цель: демонстрация возможностей интеграции
        - Участники: координатор, аналитик, исследователь""",
        expected_output="Отчет об инициализации проекта с уведомлениями",
        agent=coordinator
    )
    
    # Задача 2: Исследование информации
    research_task = Task(
        description="""Проведи исследование о возможностях интеграции GopiAI-CrewAI.
        
        Выполни следующие действия:
        1. Изучи структуру проекта (используй filesystem tool)
        2. Найди и прочитай ключевые файлы документации
        3. Сохрани собранную информацию в память (категория: "research")
        4. Создай краткий отчет о возможностях системы
        5. Уведоми координатора о завершении исследования
        
        Обрати внимание на:
        - Документацию о CrewAI
        - Возможности инструментов
        - Примеры использования
        - Перспективные направления развития""",
        expected_output="Исследовательский отчет о возможностях системы",
        agent=researcher
    )
    
    # Задача 3: Создание документации
    writing_task = Task(
        description="""Создай документацию по улучшенной интеграции GopiAI и CrewAI.
        
        Выполни следующие действия:
        1. Изучи результаты исследования (из задачи исследования)
        2. Структурируй информацию в понятном формате
        3. Создай подробную документацию в формате markdown
        4. Сохрани документацию в файловой системе
        5. Уведоми команду о завершении документации
        
        Документация должна включать:
        - Обзор улучшенной архитектуры
        - Описание системы шаблонов агентов
        - Примеры использования базового класса инструментов
        - Рекомендации по созданию новых агентов
        - Лучшие практики интеграции""",
        expected_output="Полная документация по улучшенной интеграции",
        agent=writer,
        context=[research_task]  # Используем результаты предыдущей задачи
    )
    
    # Задача 4: Разработка улучшений
    coding_task = Task(
        description="""Разработай улучшения для системы интеграции GopiAI-CrewAI.
        
        Выполни следующие действия:
        1. Изучи существующий код инструментов
        2. Разработай прототип нового инструмента для работы с аудио
        3. Создай демонстрационный пример использования
        4. Сохрани код в файловой системе
        5. Уведоми команду о завершении разработки
        
        Требования к инструменту:
        - Наследование от базового класса GopiAIBaseTool
        - Поддержка записи и воспроизведения аудио
        - Интеграция с существующей системой
        - Документирование кода
        - Обработка ошибок""",
        expected_output="Код нового инструмента с демонстрацией",
        agent=coder
    )
    
    print(f"✅ Создано {len([init_task, research_task, writing_task, coding_task])} задач")
    return init_task, research_task, writing_task, coding_task

def run_simple_demo():
    """Простая демонстрация с одним агентом"""
    print("🚀 === ПРОСТАЯ ДЕМОНСТРАЦИЯ ===")
    
    try:
        # Создаем LLM через новый AI Router
        ai_router_llm = AIRouterLLM()
        llm = ai_router_llm.get_llm_instance()
        provider_name = "GopiAI Google Router"
        print(f"🤖 Используется: {provider_name}")
        
        # Простой агент с коммуникацией
        demo_agent = Agent(
            role='Demo Assistant',
            goal='Продемонстрировать работу GopiAI инструментов',
            backstory='Ты демонстрационный ассистент для показа возможностей системы.',
            tools=[GopiAICommunicationTool(), GopiAIMemoryTool()],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Простая задача
        demo_task = Task(
            description="""Выполни демонстрацию возможностей GopiAI:
            
            1. Отправь приветственное уведомление
            2. Сохрани информацию о демонстрации в память
            3. Отправь уведомление о завершении
            
            Информация для сохранения:
            - Тема: "GopiAI Demo"
            - Статус: "Успешно выполнено"
            - Время: текущее время""",
            expected_output="Отчет о выполнении демонстрации",
            agent=demo_agent
        )
        
        # Создаем crew
        demo_crew = Crew(**{
            "agents": [demo_agent],
            "tasks": [demo_task],
            "verbose": True
        })
        
        # Запускаем
        print("⚡ Запуск простой демонстрации...")
        result = demo_crew.kickoff()
        
        print(f"✅ Простая демонстрация завершена!")
        print(f"📋 Результат: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка простой демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_advanced_demo():
    """Продвинутая демонстрация с несколькими агентами"""
    print("🚀 === ПРОДВИНУТАЯ ДЕМОНСТРАЦИЯ ===")
    
    try:
        # Создаем LLM через новый AI Router
        ai_router_llm = AIRouterLLM()
        llm = ai_router_llm.get_llm_instance()
        provider_name = "GopiAI Google Router"
        print(f"🤖 Используется: {provider_name}")
        coordinator, researcher, writer, coder = create_demo_agents(llm)
        agents = [coordinator, researcher, writer, coder]
        agents = [a for a in agents if a is not None]
        # Создаем задачи
        init_task, research_task, writing_task, coding_task = create_demo_tasks(
            coordinator, researcher, writer, coder
        )
        tasks = [init_task, research_task, writing_task, coding_task]
        tasks = [t for t in tasks if t is not None]
        # Создаем crew с динамическими инструкциями
        advanced_crew = Crew(**{
            "agents": agents,
            "tasks": tasks,
            "verbose": True
        })
        
        # Применяем динамические инструкции к команде
        print("🔧 Применение динамических инструкций к команде...")
        advanced_crew = enhance_crew_with_instructions(advanced_crew)
        # Запускаем
        print("⚡ Запуск продвинутой демонстрации...")
        try:
            result = advanced_crew.kickoff()
        except Exception as e:
            print(f"[ERROR] Crew.kickoff() exception: {e}")
            import traceback
            traceback.print_exc()
            raise
        print(f"✅ Продвинутая демонстрация завершена!")
        print(f"📋 Итоговый результат: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка продвинутой демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return False

def chat_interface():
    """Интерактивный чат-интерфейс с поддержкой RAG"""
    print("\n🤖 Добро пожаловать в GopiAI Chat!")
    print("Введите ваш вопрос или 'выход' для завершения.\n")
    
    # Инициализация LLM
    try:
        ai_router_llm = AIRouterLLM()
        llm = ai_router_llm.get_llm_instance()
        print("✅ Модель для генерации ответов загружена")
    except Exception as e:
        print(f"❌ Ошибка инициализации модели: {e}")
        return
    
    # Основной цикл чата
    while True:
        try:
            # Получаем ввод пользователя
            user_input = input("\nВы: ").strip()
            
            # Проверяем на команду выхода
            if user_input.lower() in ['выход', 'exit', 'quit', 'q']:
                print("\nДо свидания!")
                break
                
            if not user_input:
                continue
                
            # Индексируем сообщение пользователя
            message_id = f"user_{uuid.uuid4().hex}"
            index_chat_message(user_input, message_id, {
                'type': 'user_message',
                'timestamp': datetime.now().isoformat()
            })
            
            # Генерируем ответ с использованием RAG
            print("\n🤖 Думаю...")
            response = crewai_rag_query(user_input, llm)
            
            # Выводим ответ
            print(f"\n🤖 {response}")
            
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            import traceback
            traceback.print_exc()
            print("Попробуйте еще раз или введите 'выход' для завершения.")

def main():
    """Главная функция"""
    print("🚀 Запуск GopiAI-CrewAI интеграции...")
    
    # Проверка окружения
    if not check_environment():
        print("❌ Проверка окружения не пройдена. Завершение работы.")
        return
    
    # Инициализация RAG системы
    try:
        rag = get_rag_system()
        print("✅ RAG система инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации RAG системы: {e}")
        print("⚠️ Функциональность RAG будет недоступна")
    
    # Тестируем инструменты
    if not test_all_tools():
        print("❌ Критические проблемы с инструментами, остановка")
        return
    
    # Меню выбора режима
    print("\n🔹 Доступные режимы:")
    print("1. Простая демонстрация")
    print("2. Продвинутая демонстрация")
    print("3. Чат с RAG (новое!)")
    
    # Вместо input — всегда режим 3 (чат с RAG)
    mode = "3"
    print("\nВыбран режим: 3 (Чат с RAG)")
    
    if mode == "1":
        run_simple_demo()
    elif mode == "2":
        run_advanced_demo()
    elif mode == "3":
        chat_interface()
    # elif mode == "4":
    #     run_tools_tests()
    # elif mode == "5":
    #     show_templates()
    else:
        print("❌ Неизвестный режим!")

# Пример: учёт использования моделей (rpm/tpm)
current_llm_usage = {}

def index_chat_message(message: str, message_id: str, metadata: Optional[Dict] = None) -> bool:
    """
    Индексирует сообщение чата в RAG системе.
    
    Args:
        message: Текст сообщения для индексации
        message_id: Уникальный идентификатор сообщения
        metadata: Дополнительные метаданные (например, timestamp, отправитель и т.д.)
        
    Returns:
        True, если индексация прошла успешно, иначе False
    """
    try:
        rag = get_rag_system()
        if not metadata:
            metadata = {}
            
        # Добавляем временную метку, если её нет
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()
            
        # Индексируем сообщение
        success = rag.index_document(message, message_id, metadata)
        if success:
            print(f"[RAG] Сообщение {message_id} успешно проиндексировано")
        else:
            print(f"[RAG] Не удалось проиндексировать сообщение {message_id}")
            
        return success
    except Exception as e:
        print(f"❌ Ошибка при индексации сообщения: {e}")
        return False

def get_rag_context(query: str, max_results: int = 3, min_score: float = 0.3) -> List[Dict[str, Any]]:
    """
    Получает релевантный контекст из RAG системы.
    
    Args:
        query: Запрос для поиска релевантного контекста
        max_results: Максимальное количество возвращаемых результатов
        min_score: Минимальный показатель релевантности (0-1)
        
    Returns:
        Список релевантных документов с их метаданными
    """
    try:
        rag = get_rag_system()
        results = rag.search(query, limit=max_results)
        
        # Фильтруем результаты по минимальному показателю релевантности
        filtered_results = [
            {
                'text': result['text'],
                'score': result['score'],
                'metadata': result.get('metadata', {})
            }
            for result in results
            if result['score'] >= min_score
        ]
        
        return filtered_results
    except Exception as e:
        print(f"❌ Ошибка при получении контекста: {e}")
        return []

def crewai_rag_query(query: str, llm, task_type: str = "dialog", max_context_length: int = 4000) -> str:
    """
    Выполняет семантический поиск по базе знаний и генерирует ответ с использованием LLM.
    
    Args:
        query: Пользовательский запрос
        llm: Объект LLM для генерации ответа
        task_type: Тип задачи (dialog, code, summarize и т.д.)
        max_context_length: Максимальная длина контекста в символах
        
    Returns:
        Сгенерированный ответ с учётом контекста из базы знаний
    """
    # Получаем релевантный контекст
    context_results = get_rag_context(query)
    
    # Форматируем контекст для промпта
    context_parts = []
    current_length = 0
    
    for result in context_results:
        context_str = f"История: {result['text']}\n"
        if 'metadata' in result and result['metadata']:
            metadata_str = ", ".join(f"{k}={v}" for k, v in result['metadata'].items())
            context_str += f"Метаданные: {metadata_str}\n"
            
        context_str += f"Релевантность: {result['score']:.2f}\n"
        
        # Проверяем, не превысим ли мы максимальную длину
        if current_length + len(context_str) > max_context_length:
            break
            
        context_parts.append(context_str)
        current_length += len(context_str)
    
    context = "\n---\n".join(context_parts) if context_parts else "Релевантный контекст не найден."
    
    # Выбираем модель для генерации ответа
    model_id = select_llm_model(task_type, current_llm_usage)
    if not model_id:
        return "Все лимиты LLM исчерпаны, попробуйте позже."
    
    # Формируем промпт с контекстом
    prompt = f"""Ты - GopiAI, продвинутый ИИ-ассистент. Используй предоставленный контекст, чтобы ответить на вопрос.
    Если в контексте нет нужной информации, вежливо извинись и ответь на основе своих знаний.
    
    Контекст из базы знаний:
    {context}
    
    Вопрос пользователя: {query}
    
    Полезный и информативный ответ:"""
    
    # Генерируем ответ с использованием выбранной модели
    def llm_call_func(prompt_text, model=None):
        return llm.call(prompt_text, model=model) if model else llm.call(prompt_text)
    
    try:
        answer = llm_call_func(prompt, model=model_id)
        
        # Обновляем статистику использования
        current_llm_usage.setdefault(model_id, {"rpm": 0, "tpm": 0})
        current_llm_usage[model_id]["rpm"] += 1
        current_llm_usage[model_id]["tpm"] += len(prompt) + len(answer)  # Упрощённый расчёт токенов
        
        # Индексируем ответ в RAG системе
        answer_id = f"ans_{uuid.uuid4().hex}"
        index_chat_message(answer, answer_id, {
            'type': 'ai_response',
            'query': query,
            'model': model_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return answer.strip()
    except Exception as e:
        print(f"❌ Ошибка при генерации ответа: {e}")
        import traceback
        traceback.print_exc()
        return "Извините, не удалось сгенерировать ответ. Пожалуйста, попробуйте позже."

if __name__ == "__main__":
    main()
