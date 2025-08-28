"""
🚀 Пример использования динамических инструкций в CrewAI
Демонстрация интеграции ToolsInstructionManager с CrewAI workflow
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent))

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Импорт GopiAI инструментов
from .filesystem_tools import GopiAIFileSystemTool
from .browser_tools import GopiAIBrowserTool, GopiAIWebSearchTool, GopiAIPageAnalyzerTool
from .local_mcp_tools import LocalMCPTools

# Импорт системы динамических инструкций
from .crewai_tools_integration import (
    enhance_crew_with_instructions,
    enhance_agent_with_instructions,
    with_dynamic_instructions
)
from .tools_instruction_manager import get_tools_instruction_manager

# Загружаем переменные окружения
load_dotenv()

def create_enhanced_agent_example():
    """Пример создания агента с динамическими инструкциями"""
    print("🔧 === СОЗДАНИЕ АГЕНТА С ДИНАМИЧЕСКИМИ ИНСТРУКЦИЯМИ ===")
    
    # Создаем LLM
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        temperature=0.1
    )
    
    # Создаем инструменты
    tools = [
        GopiAIFileSystemTool(),
        GopiAIBrowserTool(),
        GopiAIWebSearchTool(),
        LocalMCPTools()
    ]
    
    # Создаем агента
    agent = Agent(
        role='AI Assistant with Dynamic Instructions',
        goal='Выполнять задачи с использованием динамически подгружаемых инструкций',
        backstory="""Ты продвинутый ИИ-ассистент, который умеет использовать различные инструменты.
        Когда ты выбираешь инструмент, система автоматически подгружает детальные инструкции по его использованию.""",
        tools=tools,
        llm=llm,
        verbose=True
    )
    
    # Улучшаем агента динамическими инструкциями
    enhanced_agent = enhance_agent_with_instructions(agent)
    
    print(f"✅ Создан агент с {len(enhanced_agent.tools)} улучшенными инструментами")
    return enhanced_agent


@with_dynamic_instructions
def create_enhanced_crew_example():
    """Пример создания команды с динамическими инструкциями (с декоратором)"""
    print("🚀 === СОЗДАНИЕ КОМАНДЫ С ДИНАМИЧЕСКИМИ ИНСТРУКЦИЯМИ ===")
    
    # Создаем LLM
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        temperature=0.1
    )
    
    # Создаем агентов с разными инструментами
    file_agent = Agent(
        role='File Manager',
        goal='Управлять файлами и файловой системой',
        backstory='Специалист по работе с файлами и директориями',
        tools=[GopiAIFileSystemTool()],
        llm=llm,
        verbose=True
    )
    
    web_agent = Agent(
        role='Web Researcher',
        goal='Исследовать информацию в интернете',
        backstory='Эксперт по поиску и анализу веб-информации',
        tools=[GopiAIBrowserTool(), GopiAIWebSearchTool(), GopiAIPageAnalyzerTool()],
        llm=llm,
        verbose=True
    )
    
    api_agent = Agent(
        role='API Specialist',
        goal='Работать с API и веб-сервисами',
        backstory='Специалист по интеграции с внешними сервисами',
        tools=[LocalMCPTools()],
        llm=llm,
        verbose=True
    )
    
    # Создаем команду (декоратор автоматически добавит динамические инструкции)
    crew = Crew(
        agents=[file_agent, web_agent, api_agent],
        tasks=[],  # Задачи будут добавлены позже
        verbose=True,
        planning=True
    )
    
    print(f"✅ Создана команда с {len(crew.agents)} агентами")
    return crew


def create_demo_tasks(crew: Crew):
    """Создание демонстрационных задач для тестирования динамических инструкций"""
    print("📋 === СОЗДАНИЕ ДЕМОНСТРАЦИОННЫХ ЗАДАЧ ===")
    
    # Задача для файлового агента
    file_task = Task(
        description="""
        Создай тестовый файл с информацией о системе динамических инструкций.
        Файл должен содержать:
        1. Описание системы
        2. Преимущества использования
        3. Примеры применения
        
        Сохрани файл как 'dynamic_instructions_info.md'
        """,
        expected_output="Markdown файл с подробной информацией о системе динамических инструкций",
        agent=crew.agents[0]  # File Manager
    )
    
    # Задача для веб-агента
    web_task = Task(
        description="""
        Найди информацию о лучших практиках использования инструментов в AI системах.
        Проанализируй найденную информацию и создай краткий отчет.
        """,
        expected_output="Отчет о лучших практиках использования AI инструментов",
        agent=crew.agents[1]  # Web Researcher
    )
    
    # Задача для API агента
    api_task = Task(
        description="""
        Протестируй работу с внешними API.
        Выполни простой HTTP запрос к публичному API и обработай ответ.
        """,
        expected_output="Результат тестирования API интеграции",
        agent=crew.agents[2]  # API Specialist
    )
    
    # Добавляем задачи к команде
    crew.tasks = [file_task, web_task, api_task]
    
    print(f"✅ Создано {len(crew.tasks)} демонстрационных задач")
    return crew


def test_tools_instruction_manager():
    """Тестирование ToolsInstructionManager"""
    print("🧪 === ТЕСТИРОВАНИЕ TOOLS INSTRUCTION MANAGER ===")
    
    manager = get_tools_instruction_manager()
    
    # Тестируем получение краткого списка инструментов
    tools_summary = manager.get_tools_summary()
    print(f"📝 Доступно инструментов: {len(tools_summary)}")
    for tool_name, description in tools_summary.items():
        print(f"  • {tool_name}: {description[:50]}...")
    
    # Тестируем получение детальных инструкций
    print("\n📖 Тестирование детальных инструкций:")
    for tool_name in tools_summary.keys():
        instructions = manager.get_tool_detailed_instructions(tool_name)
        if instructions:
            print(f"  ✅ {tool_name}: {len(instructions)} символов инструкций")
        else:
            print(f"  ❌ {tool_name}: инструкции не найдены")


def run_demo():
    """Запуск полной демонстрации"""
    print("🎯 === ДЕМОНСТРАЦИЯ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ В CREWAI ===\n")
    
    # Тестируем менеджер инструкций
    test_tools_instruction_manager()
    print("\n" + "="*60 + "\n")
    
    # Создаем агента с динамическими инструкциями
    enhanced_agent = create_enhanced_agent_example()
    print("\n" + "="*60 + "\n")
    
    # Создаем команду с динамическими инструкциями
    enhanced_crew = create_enhanced_crew_example()
    print("\n" + "="*60 + "\n")
    
    # Создаем демонстрационные задачи
    crew_with_tasks = create_demo_tasks(enhanced_crew)
    print("\n" + "="*60 + "\n")
    
    print("🎉 === ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")
    print("Система динамических инструкций готова к использованию!")
    print("\nДля запуска команды используйте:")
    print("crew_with_tasks.kickoff()")
    
    return crew_with_tasks


if __name__ == "__main__":
    # Запускаем демонстрацию
    demo_crew = run_demo()
    
    # Опционально: запускаем команду (раскомментируйте для тестирования)
    # print("\n🚀 Запуск команды с динамическими инструкциями...")
    # result = demo_crew.kickoff()
    # print(f"✅ Результат: {result}")
