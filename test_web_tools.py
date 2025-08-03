#!/usr/bin/env python3
"""
Тестирование веб-браузинга и поисковых инструментов GopiAI
"""

import sys
import os
import logging

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'GopiAI-CrewAI'))

from tools.gopiai_integration.command_executor import CommandExecutor

def test_web_tools():
    """Тестирует веб-браузинг и поисковые инструменты"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🌐 Тестирование веб-инструментов GopiAI")
    print("=" * 60)
    
    # Создание экземпляра CommandExecutor
    executor = CommandExecutor()
    
    # Тест 1: Веб-браузинг - простая страница
    print("\n1️⃣ Тест веб-браузинга - простая страница:")
    try:
        result = executor.browse_website(
            url="https://httpbin.org/json",
            extract_text=True,
            max_content_length=500
        )
        print(f"✅ Результат: {result[:200]}{'...' if len(result) > 200 else ''}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Веб-браузинг - извлечение заголовка
    print("\n2️⃣ Тест веб-браузинга - извлечение заголовка:")
    try:
        result = executor.browse_website(
            url="https://example.com",
            selector="h1",
            extract_text=True,
            max_content_length=300
        )
        print(f"✅ Результат: {result}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Веб-поиск DuckDuckGo
    print("\n3️⃣ Тест веб-поиска DuckDuckGo:")
    try:
        result = executor.web_search(
            query="Python programming tutorial",
            num_results=3,
            search_engine="duckduckgo"
        )
        print(f"✅ Результат: {result[:300]}{'...' if len(result) > 300 else ''}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Проверка безопасности URL
    print("\n4️⃣ Тест безопасности URL:")
    try:
        result = executor.browse_website(
            url="http://localhost:8080/admin",
            extract_text=True,
            max_content_length=200
        )
        print(f"🛡️ Результат (должен быть заблокирован): {result}")
    except Exception as e:
        print(f"🛡️ Безопасность сработала: {e}")
    
    # Тест 5: Проверка лимитов контента
    print("\n5️⃣ Тест лимитов контента:")
    try:
        result = executor.browse_website(
            url="https://httpbin.org/html",
            extract_text=True,
            max_content_length=100  # Очень маленький лимит
        )
        print(f"📏 Результат (должен быть обрезан): {result}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено!")

if __name__ == "__main__":
    test_web_tools()