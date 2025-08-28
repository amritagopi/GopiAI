#!/usr/bin/env python3
"""
🎉 РАБОЧИЙ тест GithubSearchTool через официальный crewai-tools
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
project_root = Path(__file__).parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

# Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

def test_working_github_tool():
    """Тестируем рабочий GithubSearchTool с правильной конфигурацией"""
    print("🎉 РАБОЧИЙ тест GithubSearchTool...")
    
    # Проверяем наличие токена
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен в .env файле!")
        print("📝 Добавь свой токен в .env: GITHUB_TOKEN=твой_токен")
        return False
    
    print(f"✅ GitHub токен найден: {github_token[:8]}...")
    
    try:
        # Импорт официального инструмента
        from crewai_tools import GithubSearchTool
        print("✅ Официальный GithubSearchTool импортирован!")
        
        # Создаем экземпляр с правильной конфигурацией
        print("🛠️ Создаем экземпляр с GitHub токеном...")
        github_tool = GithubSearchTool(gh_token=github_token)
        print("✅ Экземпляр создан успешно!")
        
        # Проверяем атрибуты
        print(f"📋 Название: {github_tool.name}")
        print(f"📝 Описание: {github_tool.description}")
        
        # Тестовый поиск 1: Простой поиск в популярном репозитории
        print("\n🔍 ТЕСТ 1: Поиск в популярном репозитории...")
        test_params_1 = {
            'search_query': 'machine learning',
            'github_repo': 'microsoft/vscode',
            'content_types': ['repo']
        }
        
        print(f"🎯 Параметры: {test_params_1}")
        result_1 = github_tool._run(**test_params_1)
        
        print("✅ Тест 1 выполнен успешно!")
        print(f"📊 Результат (первые 300 символов):")
        print("-" * 50)
        print(str(result_1)[:300])
        print("-" * 50)
        
        # Тестовый поиск 2: Поиск кода
        print("\n🔍 ТЕСТ 2: Поиск кода...")
        test_params_2 = {
            'search_query': 'async function',
            'github_repo': 'microsoft/vscode',
            'content_types': ['code']
        }
        
        print(f"🎯 Параметры: {test_params_2}")
        result_2 = github_tool._run(**test_params_2)
        
        print("✅ Тест 2 выполнен успешно!")
        print(f"📊 Результат (первые 300 символов):")
        print("-" * 50)
        print(str(result_2)[:300])
        print("-" * 50)
        
        # Тестовый поиск 3: Поиск issues
        print("\n🔍 ТЕСТ 3: Поиск issues...")
        test_params_3 = {
            'search_query': 'bug',
            'github_repo': 'microsoft/vscode',
            'content_types': ['issue']
        }
        
        print(f"🎯 Параметры: {test_params_3}")
        result_3 = github_tool._run(**test_params_3)
        
        print("✅ Тест 3 выполнен успешно!")
        print(f"📊 Результат (первые 300 символов):")
        print("-" * 50)
        print(str(result_3)[:300])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        print(f"🔧 Тип ошибки: {type(e).__name__}")
        import traceback
        print(f"🔍 Полная ошибка: {traceback.format_exc()}")
        return False

def test_integration_with_smart_delegator():
    """Тестируем интеграцию с нашим SmartDelegator"""
    print("\n🔗 ТЕСТ ИНТЕГРАЦИИ с SmartDelegator...")
    
    try:
        # Создаем простой wrapper для интеграции
        from crewai_tools import GithubSearchTool
        
        github_token = os.getenv('GITHUB_TOKEN')
        github_tool = GithubSearchTool(gh_token=github_token)
        
        print("✅ Официальный инструмент готов для интеграции!")
        
        # Симулируем вызов через SmartDelegator
        def simulate_smart_delegator_call(tool_name, params):
            """Симуляция вызова через SmartDelegator"""
            if tool_name == 'github_search':
                # Адаптируем параметры для официального инструмента
                adapted_params = {
                    'search_query': params.get('query', ''),
                    'github_repo': params.get('repository', 'microsoft/vscode'),
                    'content_types': params.get('content_types', ['repo', 'code'])
                }
                return github_tool._run(**adapted_params)
            return None
        
        # Тестируем симуляцию
        test_call = simulate_smart_delegator_call('github_search', {
            'query': 'python AI',
            'repository': 'microsoft/vscode',
            'content_types': ['code']
        })
        
        print("✅ Симуляция SmartDelegator работает!")
        print(f"📊 Результат симуляции: {str(test_call)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск РАБОЧЕГО тестирования GitHub инструментов...")
    print("=" * 60)
    
    # Тест 1: Основной функционал
    success1 = test_working_github_tool()
    
    # Тест 2: Интеграция
    success2 = test_integration_with_smart_delegator()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ РАБОЧЕГО ТЕСТИРОВАНИЯ:")
    print(f"   Основной функционал: {'✅ УСПЕХ' if success1 else '❌ НЕУДАЧА'}")
    print(f"   Интеграция: {'✅ УСПЕХ' if success2 else '❌ НЕУДАЧА'}")
    
    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🔥 GithubSearchTool полностью готов к использованию!")
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("   1. Использовать официальный crewai-tools пакет")
        print("   2. Передавать GitHub токен как gh_token при создании инструмента")
        print("   3. Адаптировать параметры в SmartDelegator для совместимости")
    else:
        print("\n⚠️ Есть проблемы, которые нужно исправить")
    
    input("\nНажми Enter для выхода...")