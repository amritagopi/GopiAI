#!/usr/bin/env python3
"""
🧪 Тест GithubSearchTool из CrewAI Toolkit
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "gopiai_tools"))

# Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

def test_github_search_tool():
    """Тестируем GithubSearchTool"""
    print("🔍 Тестирование GithubSearchTool...")
    
    # Проверяем наличие токена
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен в .env файле!")
        print("📝 Добавь свой токен в .env: GITHUB_TOKEN=твой_токен")
        return False
    
    print(f"✅ GitHub токен найден: {github_token[:8]}...")
    
    try:
        # Импортируем и тестируем GithubSearchTool
        from tools.crewai_toolkit.tools.github_search_tool.github_search_tool import GithubSearchTool
        
        print("📦 GithubSearchTool импортирован успешно")
        
        # Создаем экземпляр инструмента
        github_tool = GithubSearchTool()
        print("🛠️ Экземпляр GithubSearchTool создан")
        
        # Тестовый поиск
        print("\n🔍 Выполняем тестовый поиск...")
        test_query = "python machine learning"
        
        # Вызываем инструмент
        result = github_tool._run(query=test_query)
        
        print(f"✅ Поиск выполнен успешно!")
        print(f"📊 Результат (первые 500 символов):")
        print("-" * 50)
        print(str(result)[:500])
        print("-" * 50)
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Возможно, нужно установить зависимости:")
        print("   pip install PyGithub requests")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        print(f"🔧 Тип ошибки: {type(e).__name__}")
        return False

def test_crewai_integrator():
    """Тестируем наш CrewAI Tools Integrator с детальной диагностикой"""
    print("\n🔧 Тестирование CrewAI Tools Integrator...")
    
    try:
        from gopiai_tools.crewai_tools_integrator import get_crewai_tools_integrator
        
        integrator = get_crewai_tools_integrator()
        print("✅ CrewAI Tools Integrator загружен")
        
        # Детальная диагностика
        print("\n🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА:")
        print("-" * 50)
        
        # Проверяем все инструменты (включая недоступные)
        all_tools = integrator.available_tools
        print(f"📊 Всего инструментов в конфигурации: {len(all_tools)}")
        
        available_count = 0
        unavailable_count = 0
        
        for tool_name, tool_info in all_tools.items():
            if tool_info['available']:
                print(f"  ✅ {tool_name} - {tool_info['description']}")
                available_count += 1
            else:
                print(f"  ❌ {tool_name} - ОШИБКА: {tool_info.get('error', 'Неизвестная ошибка')}")
                unavailable_count += 1
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"  ✅ Доступно: {available_count}")
        print(f"  ❌ Недоступно: {unavailable_count}")
        
        # Проверяем категории
        categories = integrator.tool_categories
        print(f"\n📂 КАТЕГОРИИ ({len(categories)}):")
        for category, tools in categories.items():
            print(f"  📁 {category}: {tools}")
        
        # Проверяем github_search специально
        print("\n🔍 ПОИСК GITHUB ИНСТРУМЕНТОВ:")
        github_tools = [name for name in all_tools.keys() if 'github' in name.lower()]
        if github_tools:
            print(f"  📋 Найдены GitHub инструменты: {github_tools}")
            for tool_name in github_tools:
                tool_info = all_tools[tool_name]
                status = "✅ доступен" if tool_info['available'] else f"❌ недоступен ({tool_info.get('error', 'неизвестная ошибка')})"
                print(f"    🔧 {tool_name}: {status}")
        else:
            print("  ⚠️ GitHub инструменты не найдены в конфигурации")
        
        # Пробуем найти альтернативные пути к GitHub инструментам
        print("\n🔍 ПОИСК АЛЬТЕРНАТИВНЫХ ПУТЕЙ:")
        try:
            import os
            toolkit_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "crewai_toolkit", "tools")
            print(f"  📂 Путь к toolkit: {toolkit_path}")
            
            if os.path.exists(toolkit_path):
                github_dirs = [d for d in os.listdir(toolkit_path) if 'github' in d.lower()]
                print(f"  📋 GitHub директории: {github_dirs}")
            else:
                print(f"  ❌ Путь к toolkit не существует")
        except Exception as e:
            print(f"  ❌ Ошибка поиска путей: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интегратора: {e}")
        import traceback
        print(f"🔧 Полная ошибка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования GitHub инструментов...")
    print("=" * 60)
    
    # Тест 1: Прямое тестирование GithubSearchTool
    success1 = test_github_search_tool()
    
    # Тест 2: Тестирование через наш интегратор
    success2 = test_crewai_integrator()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"   Прямой тест GithubSearchTool: {'✅ УСПЕХ' if success1 else '❌ НЕУДАЧА'}")
    print(f"   Тест через интегратор: {'✅ УСПЕХ' if success2 else '❌ НЕУДАЧА'}")
    
    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🔥 GithubSearchTool готов к использованию!")
    else:
        print("\n⚠️ Есть проблемы, которые нужно исправить")
    
    input("\nНажми Enter для выхода...")
