#!/usr/bin/env python3
"""
Простой тест для проверки нативного Tool Calling
"""

import sys
import os

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_tool_definitions():
    """Тест загрузки определений инструментов"""
    print("🔧 Тестируем загрузку определений инструментов...")
    
    try:
        from tool_definitions import get_tool_schema, get_available_tools
        
        tools = get_tool_schema()
        tool_names = get_available_tools()
        
        print(f"✅ Загружено инструментов: {len(tools)}")
        print(f"✅ Названия: {', '.join(tool_names)}")
        
        # Проверяем базовую структуру
        for tool in tools:
            assert "type" in tool
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
        
        print("✅ Структура инструментов корректна")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_delegator_import():
    """Тест импорта SmartDelegator"""
    print("\n🔧 Тестируем импорт SmartDelegator...")
    
    try:
        from smart_delegator import SmartDelegator
        
        # Создаем экземпляр
        delegator = SmartDelegator()
        
        # Проверяем наличие ключевых методов
        assert hasattr(delegator, '_call_llm_with_tools')
        assert hasattr(delegator, '_execute_tool_call')
        assert hasattr(delegator, '_parse_tool_arguments')
        
        print("✅ SmartDelegator импортирован успешно")
        print("✅ Все необходимые методы присутствуют")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_parsing():
    """Тест парсинга JSON"""
    print("\n🔧 Тестируем парсинг JSON аргументов...")
    
    try:
        from smart_delegator import SmartDelegator
        
        delegator = SmartDelegator()
        
        # Тестовые случаи
        test_cases = [
            ('{"command": "ls"}', {"command": "ls"}),
            ('{}', {}),
            ('', {}),
        ]
        
        for input_str, expected in test_cases:
            result = delegator._parse_tool_arguments(input_str, "test")
            if isinstance(result, dict) and result == expected:
                print(f"✅ Успешно: '{input_str}' -> {result}")
            else:
                print(f"❌ Неудача: '{input_str}' -> {result} (ожидалось {expected})")
                return False
        
        print("✅ Парсинг JSON работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("🚀 Простой тест нативного Tool Calling")
    print("=" * 50)
    
    tests = [
        test_tool_definitions,
        test_smart_delegator_import,
        test_json_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результат: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли! Реализация готова.")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)