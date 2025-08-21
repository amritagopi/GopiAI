#!/usr/bin/env python3
"""
🚀 Быстрый пример: Ассистент с доступом к файловой системе
Минимальный код для предоставления ассистенту доступа к файлам
"""

import sys
import os

# Добавляем путь к GopiAI модулям
sys.path.append('GopiAI/GopiAI-CrewAI')

from crewai import Agent, Task, Crew
from tools.gopiai_integration import GopiAIFileSystemTool

def create_file_assistant():
    """Создает ассистента с доступом к файловой системе"""
    
    # Создаем инструмент файловой системы
    filesystem_tool = GopiAIFileSystemTool()
    
    # Создаем ассистента
    assistant = Agent(
        role='File Assistant',
        goal='Помочь пользователю с управлением файлами и данными',
        backstory="""Я - ассистент с полным доступом к файловой системе. 
        Могу читать, писать, создавать, удалять файлы, работать с JSON, CSV, 
        создавать архивы, искать файлы и многое другое.""",
        tools=[filesystem_tool],
        verbose=True
    )
    
    return assistant

def run_example():
    """Запуск примера работы с файлами"""
    
    print("🤖 Создание ассистента с доступом к файловой системе...")
    assistant = create_file_assistant()
    
    # Пример задачи
    task = Task(
        description="""Выполни следующие операции:
        1. Создай папку 'example_project' 
        2. Создай в ней файл 'info.txt' с информацией о проекте
        3. Создай файл 'config.json' с базовой конфигурацией
        4. Покажи содержимое созданной папки
        5. Создай резервную копию файла info.txt
        """,
        agent=assistant,
        expected_output="Отчет о выполненных операциях"
    )
    
    # Создаем команду и выполняем
    crew = Crew(
        agents=[assistant],
        tasks=[task],
        verbose=True
    )
    
    print("🚀 Запуск задачи...")
    result = crew.kickoff()
    
    print(f"\n✅ Результат: {result}")

def direct_tool_example():
    """Прямое использование инструмента без CrewAI"""
    
    print("\n🔧 Прямое использование GopiAI FileSystem Tool")
    print("=" * 50)
    
    # Создаем инструмент
    fs_tool = GopiAIFileSystemTool()
    
    # Примеры операций
    print("1. Создание файла...")
    result = fs_tool._run(
        action="write", 
        path="example.txt",
        data="Пример работы с файловой системой\nВторая строка\nТретья строка"
    )
    print(f"   {result}")
    
    print("2. Чтение файла...")
    result = fs_tool._run(action="read", path="/workspace/project/example.txt")
    print(f"   Содержимое: {result[:50]}...")
    
    print("3. Информация о файле...")
    result = fs_tool._run(action="info", path="/workspace/project/example.txt")
    print(f"   Размер: {result['size']} байт")
    print(f"   Тип: {result['mime_type']}")
    
    print("4. Поиск текста...")
    result = fs_tool._run(
        action="search_text", 
        path="/workspace/project/example.txt", 
        search_term="файловой"
    )
    print(f"   Найдено совпадений: {len(result)}")
    
    print("5. Создание JSON файла...")
    config = {
        "app_name": "GopiAI Example",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "max_files": 100
        }
    }
    result = fs_tool._run(
        action="write_json",
        path="/workspace/project/example_config.json",
        json_data=config
    )
    print(f"   {result}")
    
    print("6. Создание резервной копии...")
    result = fs_tool._run(action="backup", path="/workspace/project/example.txt")
    print(f"   {result}")
    
    # Очистка
    print("\n🧹 Очистка тестовых файлов...")
    for file in ["example.txt", "example_config.json"]:
        try:
            fs_tool._run(action="delete", path=f"/workspace/project/{file}")
            print(f"   Удален: {file}")
        except OSError as e:
            print(f"   Ошибка при удалении файла {file}: {e}")
    
    # Удаляем резервную копию
    backup_files = [f for f in os.listdir("/workspace/project") if f.startswith("example.txt.backup_")]
    for backup_file in backup_files:
        try:
            os.remove(f"/workspace/project/{backup_file}")
            print(f"   Удален: {backup_file}")
        except OSError as e:
            print(f"   Ошибка при удалении файла {backup_file}: {e}")

if __name__ == "__main__":
    print("🚀 GopiAI - Быстрый пример доступа к файловой системе")
    print("=" * 60)
    
    try:
        # Выбираем пример
        print("Выберите пример:")
        print("1. Ассистент с CrewAI")
        print("2. Прямое использование инструмента")
        
        choice = input("Введите номер (1-2): ").strip()
        
        if choice == "1":
            run_example()
        elif choice == "2":
            direct_tool_example()
        else:
            print("❌ Неверный выбор")
            
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()