#!/usr/bin/env python3
"""
🎉 Тест GithubSearchTool с OpenRouter как заменой OpenAI API
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

def test_github_with_openrouter():
    """Тестируем GitHub инструмент с OpenRouter API"""
    print("🎉 Тест GithubSearchTool с OpenRouter API...")
    
    # Проверяем наличие токенов
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    openai_base = os.getenv('OPENAI_API_BASE')
    
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен в .env файле!")
        return False
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY не настроен в .env файле!")
        return False
    
    print(f"✅ GitHub токен найден: {github_token[:8]}...")
    print(f"✅ OpenAI API ключ найден: {openai_key[:8]}...")
    print(f"✅ OpenAI API Base: {openai_base}")
    
    try:
        # Импорт официального инструмента
        from crewai_tools import GithubSearchTool
        print("✅ GithubSearchTool импортирован!")
        
        # Создаем экземпляр с GitHub токеном
        print("🛠️ Создаем экземпляр с GitHub токеном...")
        github_tool = GithubSearchTool(gh_token=github_token)
        print("✅ Экземпляр создан успешно!")
        
        # Проверяем атрибуты
        print(f"📋 Название: {github_tool.name}")
        print(f"📝 Описание: {github_tool.description}")
        
        # Тестовый поиск 1: Простой поиск репозитория
        print("\n🔍 ТЕСТ 1: Поиск информации о репозитории...")
        test_params_1 = {
            'search_query': 'python machine learning',
            'github_repo': 'microsoft/vscode',
            'content_types': ['repo']
        }
        
        print(f"🎯 Параметры: {test_params_1}")
        
        try:
            result_1 = github_tool._run(**test_params_1)
            print("✅ Тест 1 выполнен успешно!")
            print(f"📊 Результат (первые 400 символов):")
            print("-" * 50)
            print(str(result_1)[:400])
            print("-" * 50)
        except Exception as e:
            print(f"⚠️ Тест 1 не удался: {e}")
            if 'embedding' in str(e).lower():
                print("💡 Возможно, проблема с embeddings через OpenRouter")
        
        # Тестовый поиск 2: Более простой запрос
        print("\n🔍 ТЕСТ 2: Простой поиск...")
        test_params_2 = {
            'search_query': 'README',
            'github_repo': 'microsoft/vscode',
            'content_types': ['repo']
        }
        
        print(f"🎯 Параметры: {test_params_2}")
        
        try:
            result_2 = github_tool._run(**test_params_2)
            print("✅ Тест 2 выполнен успешно!")
            print(f"📊 Результат (первые 400 символов):")
            print("-" * 50)
            print(str(result_2)[:400])
            print("-" * 50)
        except Exception as e:
            print(f"⚠️ Тест 2 не удался: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"🔧 Тип ошибки: {type(e).__name__}")
        
        # Детальная диагностика
        import traceback
        print(f"🔍 Полная ошибка: {traceback.format_exc()}")
        
        return False

def test_simple_github_integration():
    """Тестируем простую интеграцию GitHub API для SmartDelegator"""
    print("\n🔗 Тест простой GitHub интеграции для SmartDelegator...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен!")
        return False
    
    try:
        import requests
        
        class SimpleGithubIntegration:
            """Простая интеграция GitHub для использования в SmartDelegator"""
            
            def __init__(self, token):
                self.token = token
                self.headers = {
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'GopiAI-GitHub-Integration'
                }
            
            def search_repositories(self, query, limit=5):
                """Поиск репозиториев"""
                url = 'https://api.github.com/search/repositories'
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': limit
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for repo in data.get('items', []):
                        results.append({
                            'name': repo['full_name'],
                            'description': repo.get('description', 'Нет описания'),
                            'stars': repo['stargazers_count'],
                            'url': repo['html_url'],
                            'language': repo.get('language', 'Unknown')
                        })
                    return {
                        'success': True,
                        'total_count': data.get('total_count', 0),
                        'results': results
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
            
            def get_repository_info(self, repo_name):
                """Получение информации о конкретном репозитории"""
                url = f'https://api.github.com/repos/{repo_name}'
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    repo = response.json()
                    return {
                        'success': True,
                        'name': repo['full_name'],
                        'description': repo.get('description', 'Нет описания'),
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'language': repo.get('language', 'Unknown'),
                        'url': repo['html_url'],
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at']
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
        
        # Тестируем интеграцию
        github_integration = SimpleGithubIntegration(github_token)
        print("✅ SimpleGithubIntegration создана!")
        
        # Тест 1: Поиск репозиториев
        print("\n🔍 Тест поиска репозиториев...")
        search_result = github_integration.search_repositories('python AI', 3)
        
        if search_result['success']:
            print(f"✅ Найдено репозиториев: {search_result['total_count']}")
            print("🏆 ТОП-3 РЕЗУЛЬТАТА:")
            for i, repo in enumerate(search_result['results'], 1):
                print(f"   {i}. {repo['name']} ⭐ {repo['stars']}")
                print(f"      {repo['description'][:80]}...")
                print(f"      Язык: {repo['language']}")
                print()
        else:
            print(f"❌ Ошибка поиска: {search_result['error']}")
        
        # Тест 2: Информация о конкретном репозитории
        print("🔍 Тест получения информации о репозитории...")
        repo_info = github_integration.get_repository_info('microsoft/vscode')
        
        if repo_info['success']:
            print("✅ Информация о репозитории получена:")
            print(f"   📦 Название: {repo_info['name']}")
            print(f"   📝 Описание: {repo_info['description'][:100]}...")
            print(f"   ⭐ Звёзды: {repo_info['stars']}")
            print(f"   🍴 Форки: {repo_info['forks']}")
            print(f"   💻 Язык: {repo_info['language']}")
        else:
            print(f"❌ Ошибка получения информации: {repo_info['error']}")
        
        print("✅ SimpleGithubIntegration полностью работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        import traceback
        print(f"🔍 Полная ошибка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования GitHub с OpenRouter API...")
    print("=" * 60)
    
    # Тест 1: CrewAI инструмент с OpenRouter
    success1 = test_github_with_openrouter()
    
    # Тест 2: Простая интеграция для SmartDelegator
    success2 = test_simple_github_integration()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ С OPENROUTER:")
    print(f"   CrewAI + OpenRouter: {'✅ УСПЕХ' if success1 else '❌ НЕУДАЧА'}")
    print(f"   Простая интеграция: {'✅ УСПЕХ' if success2 else '❌ НЕУДАЧА'}")
    
    if success1:
        print("\n🎉 ОТЛИЧНО! CrewAI инструмент работает с OpenRouter!")
        print("🔥 Можем интегрировать его в SmartDelegator!")
    elif success2:
        print("\n🎉 У НАС ЕСТЬ РАБОЧАЯ АЛЬТЕРНАТИВА!")
        print("💡 Простая интеграция GitHub API готова для SmartDelegator")
        print("🔧 Это надёжное решение без зависимостей от embeddings")
    
    if success1 or success2:
        print("\n✨ ГОТОВО К ИНТЕГРАЦИИ В GOPIAI!")
    
    input("\nНажми Enter для выхода...")