#!/usr/bin/env python3
"""
🚀 Пример использования инструментов GopiAI с CrewAI
Демонстрация основных возможностей настроенных инструментов
"""

import os
import sys
from crewai import Agent, Task, Crew

# Импортируем основные инструменты
from filesystem_tools import GopiAIFileSystemTool
from terminal_tool import TerminalTool
from web_search_tool import GopiAIWebSearchTool
from web_viewer_tool import GopiAIWebViewerTool

def create_research_agent():
    """Создает агента-исследователя с основными инструментами"""
    
    # Основные инструменты
    tools = [
        GopiAIFileSystemTool(),
        TerminalTool(),
        GopiAIWebSearchTool(),
        GopiAIWebViewerTool(),
    ]
    
    agent = Agent(
        role='Research Assistant',
        goal='Помочь с исследованиями, поиском информации и работой с файлами',
        backstory="""Я - помощник-исследователь с доступом к основным инструментам:
        - Файловая система: чтение, запись, поиск файлов
        - Терминал: выполнение команд
        - Поиск в интернете: поиск актуальной информации
        - Просмотр веб-страниц: анализ содержимого сайтов
        
        Я помогаю находить информацию, анализировать данные и создавать отчеты.""",
        tools=tools,
        verbose=True,
        allow_delegation=False
    )
    
    return agent

def test_tools_directly():
    """Прямое тестирование инструментов без CrewAI"""
    
    print("\n1. Тестирование файловой системы...")
    fs_tool = GopiAIFileSystemTool()
    result = fs_tool._run(action="write", path="test.txt", data="Тест GopiAI инструментов")
    print(f"   {result}")
    
    result = fs_tool._run(action="read", path="test.txt")
    print(f"   Содержимое: {result}")
    
    print("\n2. Тестирование терминала...")
    terminal_tool = TerminalTool()
    result = terminal_tool._run(command="pwd")
    print(f"   {result}")
    
    print("\n3. Тестирование поиска...")
    search_tool = GopiAIWebSearchTool()
    result = search_tool._run(query="OpenAI GPT", num_results=2)
    print(f"   {result[:200]}...")
    
    print("\n4. Тестирование просмотра веб-страниц...")
    viewer_tool = GopiAIWebViewerTool()
    result = viewer_tool._run(action="get_title", url="https://www.python.org")
    print(f"   {result}")
    
    # Очистка
    fs_tool._run(action="delete", path="test.txt")
    print("\n✅ Тест завершен")

def run_example():
    """Запуск примера использования"""
    
    print("🚀 Демонстрация инструментов GopiAI")
    print("=" * 50)
    
    # Выбираем пример для запуска
    print("Выберите пример для запуска:")
    print("1. Создать агента-исследователя")
    print("2. Простой тест инструментов")
    
    choice = input("Введите номер (1-2): ").strip()
    
    if choice == "1":
        print("\n🤖 Создание агента-исследователя...")
        agent = create_research_agent()
        print(f"✅ Агент создан: {agent.role}")
        print(f"   Инструментов: {len(agent.tools)}")
        for tool in agent.tools:
            print(f"   - {tool.__class__.__name__}")
        
    elif choice == "2":
        print("\n🧪 Простой тест инструментов...")
        test_tools_directly()
        
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    try:
        run_example()
    except KeyboardInterrupt:
        print("\n\n⏹️ Выполнение прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
