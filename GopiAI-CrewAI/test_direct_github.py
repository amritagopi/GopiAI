#!/usr/bin/env python3
"""
🧪 Прямой тест GithubSearchTool без интегратора
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем пути для импорта
project_root = Path(__file__).parent
# Инициализируем пути проекта
path_manager = setup_project_paths()

# Загружаем переменные окружения из .env
load_dotenv()

def test_direct_github_import():
    """Тестируем прямой импорт GithubSearchTool"""
    print("🔍 Прямой тест импорта GithubSearchTool...")
    
    # Проверяем наличие токена
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен в .env файле!")
        return False
    
    print(f"✅ GitHub токен найден: {github_token[:8]}...")
    
    try:
        # Прямой импорт из crewai_toolkit
        print("📦 Пробуем импортировать GithubSearchTool...")
        
        from tools.crewai_toolkit.tools.github_search_tool.github_search_tool import GithubSearchTool
        print("✅ GithubSearchTool импортирован успешно!")
        
        # Создаем экземпляр
        print("🛠️ Создаем экземпляр инструмента...")
        github_tool = GithubSearchTool()
        print("✅ Экземпляр создан успешно!")
        
        # Проверяем атрибуты
        print(f"📋 Название: {github_tool.name}")
        print(f"📝 Описание: {github_tool.description}")
        
        # Тестовый поиск
        print("\n🔍 Выполняем тестовый поиск...")
        test_params = {
            'search_query': 'python machine learning',
            'github_repo': 'microsoft/vscode',
            'content_types': ['code', 'repo']
        }
        
        print(f"🎯 Параметры поиска: {test_params}")
        
        # Вызываем инструмент
        result = github_tool._run(**test_params)
        
        print("✅ Поиск выполнен успешно!")
        print(f"📊 Результат (первые 500 символов):")
        print("-" * 50)
        print(str(result)[:500])
        print("-" * 50)
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Проблема с зависимостями CrewAI Toolkit")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        print(f"🔧 Тип ошибки: {type(e).__name__}")
        import traceback
        print(f"🔍 Полная ошибка: {traceback.format_exc()}")
        return False

def test_alternative_approach():
    """Тестируем альтернативный подход через официальный crewai-tools"""
    print("\n🔄 Альтернативный подход через crewai-tools...")
    
    try:
        # Пробуем импорт из официального пакета
        from crewai_tools import GithubSearchTool as OfficialGithubSearchTool
        print("✅ Официальный GithubSearchTool найден!")
        
        # Создаем экземпляр
        github_tool = OfficialGithubSearchTool()
        print("✅ Официальный экземпляр создан!")
        
        # Тестовый поиск
        result = github_tool._run(
            search_query='python AI',
            github_repo='microsoft/vscode',
            content_types=['code']
        )
        
        print("✅ Официальный инструмент работает!")
        print(f"📊 Результат: {str(result)[:200]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Официальный пакет недоступен: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка официального инструмента: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск прямого тестирования GitHub инструментов...")
    print("=" * 60)
    
    # Тест 1: Прямой импорт из нашего toolkit
    success1 = test_direct_github_import()
    
    # Тест 2: Альтернативный подход через официальный пакет
    success2 = test_alternative_approach()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ПРЯМОГО ТЕСТИРОВАНИЯ:")
    print(f"   Прямой импорт из toolkit: {'✅ УСПЕХ' if success1 else '❌ НЕУДАЧА'}")
    print(f"   Официальный crewai-tools: {'✅ УСПЕХ' if success2 else '❌ НЕУДАЧА'}")
    
    if success1 or success2:
        print("\n🎉 ХОТЯ БЫ ОДИН ПОДХОД РАБОТАЕТ!")
        if success2:
            print("💡 Рекомендация: использовать официальный crewai-tools пакет")
    else:
        print("\n⚠️ Оба подхода не работают - нужна дополнительная настройка")
    
    input("\nНажми Enter для выхода...")