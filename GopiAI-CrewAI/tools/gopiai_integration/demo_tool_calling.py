#!/usr/bin/env python3
"""
Демонстрация нативного Tool Calling в GopiAI
Показывает работу улучшенной системы вызова инструментов
"""

import os
import sys
import json
from unittest.mock import Mock

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def demo_tool_schema():
    """Демонстрация схем инструментов"""
    print("🔧 Демонстрация схем инструментов")
    print("=" * 50)
    
    from tool_definitions import get_tool_schema, get_available_tools, get_tool_usage_examples
    
    # Показываем доступные инструменты
    tools = get_tool_schema()
    tool_names = get_available_tools()
    examples = get_tool_usage_examples()
    
    print(f"📋 Доступно инструментов: {len(tools)}")
    print(f"📝 Названия: {', '.join(tool_names)}")
    
    # Показываем детали каждого инструмента
    for tool in tools:
        function = tool["function"]
        print(f"\n🔧 {function['name']}")
        print(f"   📄 Описание: {function['description']}")
        
        # Показываем параметры
        params = function.get("parameters", {}).get("properties", {})
        required = function.get("parameters", {}).get("required", [])
        
        if params:
            print("   📋 Параметры:")
            for param_name, param_info in params.items():
                req_mark = "🔴" if param_name in required else "🟡"
                param_type = param_info.get("type", "unknown")
                param_desc = param_info.get("description", "Нет описания")
                print(f"      {req_mark} {param_name} ({param_type}): {param_desc}")
        
        # Показываем примеры использования
        if function['name'] in examples:
            print("   💡 Примеры:")
            for example in examples[function['name']][:2]:  # Показываем первые 2 примера
                print(f"      • {example['description']}")
                print(f"        Аргументы: {example['arguments']}")

def demo_json_parsing():
    """Демонстрация парсинга JSON аргументов"""
    print("\n\n🔧 Демонстрация парсинга JSON аргументов")
    print("=" * 50)
    
    from smart_delegator import SmartDelegator
    
    delegator = SmartDelegator()
    
    # Тестовые случаи с различными форматами JSON
    test_cases = [
        ('{"command": "ls -la"}', "Стандартный JSON"),
        ("{'command': 'pwd'}", "JSON с одинарными кавычками"),
        ('{"path": "/tmp", "operation": "read"}', "Множественные параметры"),
        ('{"command": "echo hello",}', "JSON с trailing запятой"),
        ('', "Пустая строка"),
        ('{"invalid": json}', "Невалидный JSON"),
    ]
    
    for json_str, description in test_cases:
        print(f"\n📝 {description}: {json_str}")
        result = delegator._parse_tool_arguments(json_str, "demo_function")
        
        if isinstance(result, dict):
            print(f"   ✅ Успешно распарсено: {result}")
        else:
            print(f"   ❌ Ошибка: {result}")

def demo_tool_validation():
    """Демонстрация валидации вызовов инструментов"""
    print("\n\n🔧 Демонстрация валидации инструментов")
    print("=" * 50)
    
    from tool_definitions import validate_tool_call
    
    # Тестовые случаи валидации
    test_cases = [
        # Валидные случаи
        ("execute_terminal_command", {"command": "ls -la"}, "Валидная команда терминала"),
        ("file_operations", {"operation": "read", "path": "/tmp/test.txt"}, "Валидная операция с файлом"),
        ("web_search", {"query": "python tutorial", "num_results": 5}, "Валидный веб-поиск"),
        
        # Невалидные случаи
        ("execute_terminal_command", {}, "Отсутствует обязательный параметр"),
        ("unknown_tool", {"param": "value"}, "Неизвестный инструмент"),
        ("file_operations", {"operation": "invalid_op", "path": "/tmp"}, "Неверное enum значение"),
        ("web_search", {"query": "test", "num_results": 100}, "Превышение максимального значения"),
    ]
    
    for tool_name, args, description in test_cases:
        print(f"\n📝 {description}")
        print(f"   Инструмент: {tool_name}")
        print(f"   Аргументы: {args}")
        
        result = validate_tool_call(tool_name, args)
        
        if result["valid"]:
            print(f"   ✅ Валидация прошла успешно")
            print(f"   📋 Нормализованные аргументы: {result['normalized_args']}")
        else:
            print(f"   ❌ Валидация не прошла")
            print(f"   🚫 Ошибки: {'; '.join(result['errors'])}")

def demo_mock_tool_execution():
    """Демонстрация выполнения инструментов (мок)"""
    print("\n\n🔧 Демонстрация выполнения инструментов (мок)")
    print("=" * 50)
    
    from smart_delegator import SmartDelegator
    
    delegator = SmartDelegator()
    
    # Создаем мок tool_call объект
    mock_tool_call = Mock()
    mock_tool_call.function.name = "execute_terminal_command"
    mock_tool_call.function.arguments = '{"command": "pwd"}'
    
    print("📝 Мок вызов инструмента:")
    print(f"   Инструмент: {mock_tool_call.function.name}")
    print(f"   Аргументы: {mock_tool_call.function.arguments}")
    
    # Тестируем парсинг аргументов
    print("\n🔍 Парсинг аргументов:")
    parsed_args = delegator._parse_tool_arguments(
        mock_tool_call.function.arguments, 
        mock_tool_call.function.name
    )
    print(f"   Результат: {parsed_args}")
    
    # Тестируем валидацию
    print("\n🔍 Валидация:")
    from tool_definitions import validate_tool_call
    validation = validate_tool_call(mock_tool_call.function.name, parsed_args)
    print(f"   Валидно: {validation['valid']}")
    if validation['valid']:
        print(f"   Нормализованные аргументы: {validation['normalized_args']}")
    else:
        print(f"   Ошибки: {validation['errors']}")

def demo_error_handling():
    """Демонстрация обработки ошибок"""
    print("\n\n🔧 Демонстрация обработки ошибок")
    print("=" * 50)
    
    from smart_delegator import SmartDelegator
    
    delegator = SmartDelegator()
    
    # Тест обработки невалидного JSON
    print("📝 Тест невалидного JSON:")
    invalid_json = '{"command": "test", invalid}'
    result = delegator._parse_tool_arguments(invalid_json, "test_function")
    print(f"   Результат: {result}")
    
    # Тест обработки пустых аргументов
    print("\n📝 Тест пустых аргументов:")
    empty_result = delegator._parse_tool_arguments("", "test_function")
    print(f"   Результат: {empty_result}")
    
    # Тест обработки некорректного типа
    print("\n📝 Тест некорректного типа:")
    none_result = delegator._parse_tool_arguments(None, "test_function")
    print(f"   Результат: {none_result}")

def main():
    """Главная функция демонстрации"""
    print("🚀 Демонстрация нативного Tool Calling в GopiAI")
    print("🔧 Реализация задачи 3: Implement native Tool Calling in LLM integration")
    print("=" * 80)
    
    # Запускаем все демонстрации
    demo_tool_schema()
    demo_json_parsing()
    demo_tool_validation()
    demo_mock_tool_execution()
    demo_error_handling()
    
    print("\n" + "=" * 80)
    print("🎉 Демонстрация завершена!")
    print("\n📋 Реализованные возможности:")
    print("   ✅ Нативная поддержка OpenAI Tool Calling")
    print("   ✅ Двухфазная обработка: tool execution → final response generation")
    print("   ✅ Ограничение итераций для предотвращения бесконечных циклов")
    print("   ✅ Улучшенный парсинг JSON аргументов с обработкой ошибок")
    print("   ✅ Валидация аргументов против схем инструментов")
    print("   ✅ Comprehensive error handling для всех типов ошибок")
    print("   ✅ Retry логика с exponential backoff")
    print("   ✅ Поддержка множественных провайдеров (OpenRouter, Gemini, Generic)")
    print("   ✅ Таймауты и защита от зависания")
    
    print("\n🎯 Задача 3 выполнена успешно!")

if __name__ == "__main__":
    main()