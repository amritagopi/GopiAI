#!/usr/bin/env python3
"""
Полный интеграционный тест веб-инструментов.
Проверяет работу browse_website и web_search через WebToolsIntegration.
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

from web_tools_integration import WebToolsIntegration, get_web_tools_schema

def setup_logging():
    """Настройка логирования для тестов."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_web_integration.log', encoding='utf-8')
        ]
    )

class MockToolCall:
    """Мок-объект для имитации tool_call от LLM."""
    
    def __init__(self, function_name: str, arguments: dict):
        self.function = MockFunction(function_name, arguments)

class MockFunction:
    """Мок-объект для имитации function в tool_call."""
    
    def __init__(self, name: str, arguments: dict):
        self.name = name
        # Правильно сериализуем аргументы в JSON
        import json
        self.arguments = json.dumps(arguments) if isinstance(arguments, dict) else arguments

def test_web_tools_integration():
    """Тестирует интеграцию веб-инструментов."""
    print("\n🌐 Тестирование интеграции веб-инструментов")
    print("=" * 60)
    
    # Создаем экземпляр интеграции
    integration = WebToolsIntegration()
    
    if not integration.is_available():
        print("❌ Веб-инструменты недоступны - CommandExecutor не инициализирован")
        return False
    
    print("✅ Веб-инструменты доступны")
    
    # Тест 1: browse_website
    print("\n1. Тестирование browse_website:")
    try:
        tool_call = MockToolCall("browse_website", {
            "url": "https://httpbin.org/json",
            "extract_text": True,
            "max_content_length": 1000
        })
        
        result = integration.execute_tool_call(tool_call)
        print(f"✅ browse_website выполнен успешно")
        print(f"Длина результата: {len(result)} символов")
        print(f"Первые 200 символов: {result[:200]}...")
        
        # Проверяем, что результат содержит ожидаемые элементы
        if "Содержимое страницы" in result and "httpbin.org" in result:
            print("✅ Результат содержит ожидаемые элементы")
        else:
            print("❌ Результат не содержит ожидаемых элементов")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в browse_website: {e}")
        return False
    
    # Тест 2: web_search
    print("\n2. Тестирование web_search:")
    try:
        tool_call = MockToolCall("web_search", {
            "query": "Python programming tutorial",
            "num_results": 3,
            "search_engine": "duckduckgo"
        })
        
        result = integration.execute_tool_call(tool_call)
        print(f"✅ web_search выполнен успешно")
        print(f"Длина результата: {len(result)} символов")
        print(f"Первые 200 символов: {result[:200]}...")
        
        # Проверяем, что результат содержит ожидаемые элементы
        if "Результаты поиска для" in result and "Python" in result:
            print("✅ Результат содержит ожидаемые элементы")
        else:
            print("❌ Результат не содержит ожидаемых элементов")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в web_search: {e}")
        return False
    
    # Тест 3: Обработка ошибок
    print("\n3. Тестирование обработки ошибок:")
    
    # Тест с пустым URL
    try:
        tool_call = MockToolCall("browse_website", {"url": ""})
        result = integration.execute_tool_call(tool_call)
        
        if "не указан URL" in result:
            print("✅ Правильно обработан пустой URL")
        else:
            print(f"❌ Неправильная обработка пустого URL: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Неожиданная ошибка при пустом URL: {e}")
        return False
    
    # Тест с пустым запросом
    try:
        tool_call = MockToolCall("web_search", {"query": ""})
        result = integration.execute_tool_call(tool_call)
        
        if "не указан поисковый запрос" in result:
            print("✅ Правильно обработан пустой запрос")
        else:
            print(f"❌ Неправильная обработка пустого запроса: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Неожиданная ошибка при пустом запросе: {e}")
        return False
    
    # Тест с неизвестным инструментом
    try:
        tool_call = MockToolCall("unknown_tool", {})
        result = integration.execute_tool_call(tool_call)
        
        if "Неизвестный веб-инструмент" in result:
            print("✅ Правильно обработан неизвестный инструмент")
        else:
            print(f"❌ Неправильная обработка неизвестного инструмента: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Неожиданная ошибка при неизвестном инструменте: {e}")
        return False
    
    return True

def test_tool_schema():
    """Тестирует получение схем веб-инструментов."""
    print("\n📋 Тестирование схем веб-инструментов")
    print("=" * 60)
    
    try:
        schemas = get_web_tools_schema()
        
        if not schemas:
            print("❌ Схемы веб-инструментов не найдены")
            return False
        
        print(f"✅ Найдено {len(schemas)} схем веб-инструментов")
        
        # Проверяем наличие обязательных инструментов
        tool_names = [schema.get("function", {}).get("name", "") for schema in schemas]
        
        if "browse_website" in tool_names:
            print("✅ Схема browse_website найдена")
        else:
            print("❌ Схема browse_website не найдена")
            return False
        
        if "web_search" in tool_names:
            print("✅ Схема web_search найдена")
        else:
            print("❌ Схема web_search не найдена")
            return False
        
        # Проверяем структуру схем
        for schema in schemas:
            function_info = schema.get("function", {})
            if not function_info.get("name") or not function_info.get("parameters"):
                print(f"❌ Некорректная структура схемы: {schema}")
                return False
        
        print("✅ Все схемы имеют корректную структуру")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при получении схем: {e}")
        return False

def test_validation():
    """Тестирует валидацию аргументов веб-инструментов."""
    print("\n✅ Тестирование валидации аргументов")
    print("=" * 60)
    
    integration = WebToolsIntegration()
    
    # Тесты для browse_website
    test_cases = [
        # Валидные случаи
        ("browse_website", {"url": "https://example.com"}, True),
        ("browse_website", {"url": "http://test.com", "extract_text": True}, True),
        
        # Невалидные случаи
        ("browse_website", {}, False),  # Нет URL
        ("browse_website", {"url": ""}, False),  # Пустой URL
        ("browse_website", {"url": "ftp://example.com"}, False),  # Неправильный протокол
        
        # Тесты для web_search
        ("web_search", {"query": "test"}, True),
        ("web_search", {"query": "test", "num_results": 5}, True),
        
        # Невалидные случаи для web_search
        ("web_search", {}, False),  # Нет запроса
        ("web_search", {"query": ""}, False),  # Пустой запрос
        ("web_search", {"query": "test", "num_results": 15}, False),  # Слишком много результатов
        
        # Неизвестный инструмент
        ("unknown_tool", {"param": "value"}, False),
    ]
    
    all_passed = True
    
    for function_name, arguments, expected_valid in test_cases:
        result = integration.validate_tool_call(function_name, arguments)
        actual_valid = result["valid"]
        
        if actual_valid == expected_valid:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {function_name}({arguments}) -> valid={actual_valid} (ожидалось {expected_valid})")
        
        if not actual_valid and result["errors"]:
            print(f"    Ошибки: {result['errors']}")
    
    return all_passed

def main():
    """Основная функция тестирования."""
    print("🚀 Запуск полного интеграционного тестирования веб-инструментов")
    print("=" * 80)
    
    setup_logging()
    
    # Проверяем наличие необходимых библиотек
    try:
        import requests
        import bs4
        print("✅ Необходимые библиотеки (requests, beautifulsoup4) доступны")
    except ImportError as e:
        print(f"❌ Отсутствуют необходимые библиотеки: {e}")
        print("Установите их командой: pip install requests beautifulsoup4")
        return False
    
    # Запуск тестов
    tests = [
        ("Интеграция веб-инструментов", test_web_tools_integration),
        ("Схемы инструментов", test_tool_schema),
        ("Валидация аргументов", test_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Запуск теста: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ Тест '{test_name}' пройден")
            else:
                print(f"❌ Тест '{test_name}' провален")
                
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    print(f"\nИтого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Веб-инструменты готовы к использованию.")
        return True
    else:
        print("⚠️ Некоторые тесты провалены. Требуется дополнительная отладка.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)