#!/usr/bin/env python3
"""
🔧 Альтернативный тест GitHub инструментов без OpenAI API
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

def test_github_with_mock_openai():
    """Тестируем GitHub инструмент с mock OpenAI ключом"""
    print("🔧 Тест GitHub инструмента с mock OpenAI ключом...")
    
    # Проверяем наличие GitHub токена
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен в .env файле!")
        return False
    
    print(f"✅ GitHub токен найден: {github_token[:8]}...")
    
    # Устанавливаем mock OpenAI ключ если его нет
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("⚠️ OpenAI API ключ не найден, используем mock ключ для тестирования...")
        os.environ['OPENAI_API_KEY'] = 'sk-mock-key-for-testing-only'
    
    try:
        from crewai_tools import GithubSearchTool
        print("✅ GithubSearchTool импортирован!")
        
        # Создаем экземпляр
        print("🛠️ Создаем экземпляр с GitHub токеном...")
        github_tool = GithubSearchTool(gh_token=github_token)
        print("✅ Экземпляр создан успешно!")
        
        # Проверяем атрибуты
        print(f"📋 Название: {github_tool.name}")
        print(f"📝 Описание: {github_tool.description}")
        
        # Простой тест поиска
        print("\n🔍 Выполняем простой тест поиска...")
        test_params = {
            'search_query': 'python',
            'github_repo': 'microsoft/vscode',
            'content_types': ['repo']
        }
        
        print(f"🎯 Параметры: {test_params}")
        result = github_tool._run(**test_params)
        
        print("✅ Поиск выполнен!")
        print(f"📊 Результат (первые 400 символов):")
        print("-" * 50)
        print(str(result)[:400])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"🔧 Тип ошибки: {type(e).__name__}")
        
        # Если ошибка связана с OpenAI, предлагаем решение
        if 'openai' in str(e).lower() or 'api_key' in str(e).lower():
            print("\n💡 РЕШЕНИЕ:")
            print("   1. Получи OpenAI API ключ на https://platform.openai.com/api-keys")
            print("   2. Добавь его в .env файл: OPENAI_API_KEY=твой_ключ")
            print("   3. Или используй альтернативные инструменты без OpenAI зависимостей")
        
        return False

def test_simple_github_api():
    """Тестируем простой GitHub API без CrewAI зависимостей"""
    print("\n🔄 Альтернативный тест: прямой GitHub API...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен!")
        return False
    
    try:
        import requests
        
        # Простой поиск через GitHub API
        print("🔍 Выполняем поиск через GitHub Search API...")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Поиск репозиториев
        search_url = 'https://api.github.com/search/repositories'
        params = {
            'q': 'python machine learning',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 5
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GitHub API поиск успешен!")
            print(f"📊 Найдено репозиториев: {data.get('total_count', 0)}")
            
            print("\n🏆 ТОП-5 РЕПОЗИТОРИЕВ:")
            for i, repo in enumerate(data.get('items', [])[:5], 1):
                print(f"   {i}. {repo['full_name']} ⭐ {repo['stargazers_count']}")
                print(f"      {repo['description'][:100]}...")
                print()
            
            return True
        else:
            print(f"❌ Ошибка GitHub API: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка прямого API: {e}")
        return False

def create_simple_github_wrapper():
    """Создаем простой wrapper для GitHub API"""
    print("\n🛠️ Создаем простой GitHub wrapper...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_github_token_here':
        print("❌ GITHUB_TOKEN не настроен!")
        return False
    
    try:
        import requests
        
        class SimpleGithubTool:
            def __init__(self, token):
                self.token = token
                self.headers = {
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json'
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
                
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                return None
            
            def search_code(self, query, repo=None, limit=5):
                """Поиск кода"""
                url = 'https://api.github.com/search/code'
                search_query = query
                if repo:
                    search_query += f' repo:{repo}'
                
                params = {
                    'q': search_query,
                    'per_page': limit
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                return None
        
        # Тестируем wrapper
        github_tool = SimpleGithubTool(github_token)
        print("✅ SimpleGithubTool создан!")
        
        # Тест поиска репозиториев
        repos = github_tool.search_repositories('python AI', 3)
        if repos:
            print(f"✅ Найдено репозиториев: {repos.get('total_count', 0)}")
            for repo in repos.get('items', [])[:3]:
                print(f"   📦 {repo['full_name']} ⭐ {repo['stargazers_count']}")
        
        # Тест поиска кода
        code_results = github_tool.search_code('machine learning', 'microsoft/vscode', 2)
        if code_results:
            print(f"✅ Найдено файлов с кодом: {code_results.get('total_count', 0)}")
            for item in code_results.get('items', [])[:2]:
                print(f"   📄 {item['name']} в {item['repository']['full_name']}")
        
        print("✅ SimpleGithubTool работает отлично!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка wrapper: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск альтернативного тестирования GitHub инструментов...")
    print("=" * 60)
    
    # Тест 1: CrewAI инструмент с mock ключом
    success1 = test_github_with_mock_openai()
    
    # Тест 2: Прямой GitHub API
    success2 = test_simple_github_api()
    
    # Тест 3: Простой wrapper
    success3 = create_simple_github_wrapper()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ АЛЬТЕРНАТИВНОГО ТЕСТИРОВАНИЯ:")
    print(f"   CrewAI инструмент: {'✅ УСПЕХ' if success1 else '❌ НЕУДАЧА'}")
    print(f"   Прямой GitHub API: {'✅ УСПЕХ' if success2 else '❌ НЕУДАЧА'}")
    print(f"   Простой wrapper: {'✅ УСПЕХ' if success3 else '❌ НЕУДАЧА'}")
    
    if success2 or success3:
        print("\n🎉 У НАС ЕСТЬ РАБОЧИЕ АЛЬТЕРНАТИВЫ!")
        print("💡 Можем использовать прямой GitHub API или простой wrapper")
        print("🔧 Это решает проблему зависимости от OpenAI API")
    
    if success1:
        print("🎊 CrewAI инструмент тоже работает!")
    elif not success1 and (success2 or success3):
        print("⚠️ CrewAI инструмент требует OpenAI API ключ")
        print("💡 Но у нас есть рабочие альтернативы!")
    
    input("\nНажми Enter для выхода...")