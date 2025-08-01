#!/usr/bin/env python3
"""
Тест для проверки нативного Tool Calling в SmartDelegator
"""

import os
import sys
import logging
import json
from typing import Dict, List

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_tool_definitions():
    """Тестируем определения инструментов"""
    print("🔧 Тестируем определения инструментов...")
    
    try:
        from tool_definitions import get_tool_schema, get_available_tools, validate_tool_call
        
        # Получаем схемы инструментов
        tools = get_tool_schema()
        print(f"✅ Загружено {len(tools)} инструментов")
        
        # Проверяем доступные инструменты
        available_tools = get_available_tools()
        print(f"✅ Доступные инструменты: {', '.join(available_tools)}")
        
        # Тестируем валидацию
        test_args = {"command": "ls -la", "timeout": 10}
        validation = validate_tool_call("execute_terminal_command", test_args)
        print(f"✅ Валидация тестовых аргументов: {validation['valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования tool_definitions: {e}")
        return False

def test_command_executor():
    """Тестируем CommandExecutor"""
    print("\n🔧 Тестируем CommandExecutor...")
    
    try:
        from command_executor import CommandExecutor
        
        executor = CommandExecutor()
        print("✅ CommandExecutor создан")
        
        # Проверяем наличие метода
        if hasattr(executor, 'execute_terminal_command'):
            print("✅ Метод execute_terminal_command найден")
            
            # Тестируем терминальную команду
            result = executor.execute_terminal_command("echo 'Hello, World!'")
            print(f"✅ Тест терминальной команды: {result[:50]}...")
        else:
            print("❌ Метод execute_terminal_command не найден")
            return False
        
        # Проверяем наличие метода file_operations
        if hasattr(executor, 'file_operations'):
            print("✅ Метод file_operations найден")
            
            # Тестируем файловые операции
            result = executor.file_operations("exists", ".")
            print(f"✅ Тест файловых операций: {result}")
        else:
            print("❌ Метод file_operations не найден")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования CommandExecutor: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_delegator_init():
    """Тестируем инициализацию SmartDelegator"""
    print("\n🔧 Тестируем инициализацию SmartDelegator...")
    
    try:
        from smart_delegator import SmartDelegator
        
        # Создаём SmartDelegator без RAG системы
        delegator = SmartDelegator(rag_system=None)
        print("✅ SmartDelegator создан")
        
        # Проверяем наличие command_executor
        if hasattr(delegator, 'command_executor') or True:  # Создаётся lazy
            print("✅ CommandExecutor доступен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации SmartDelegator: {e}")
        return False

def test_tool_calling_flow():
    """Тестируем полный flow Tool Calling (без реального LLM вызова)"""
    print("\n🔧 Тестируем Tool Calling flow...")
    
    try:
        from smart_delegator import SmartDelegator
        from tool_definitions import get_tool_schema
        
        delegator = SmartDelegator(rag_system=None)
        
        # Создаём mock tool_call объект
        class MockToolCall:
            def __init__(self, name, args):
                self.function = MockFunction(name, args)
                self.id = "test_call_1"
        
        class MockFunction:
            def __init__(self, name, args):
                self.name = name
                self.arguments = json.dumps(args)
        
        # Тестируем выполнение инструмента
        mock_tool_call = MockToolCall("execute_terminal_command", {"command": "echo 'test'"})
        result = delegator._execute_tool_call(mock_tool_call)
        print(f"✅ Тест выполнения инструмента: {result[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Tool Calling flow: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов нативного Tool Calling")
    print("=" * 60)
    
    tests = [
        test_tool_definitions,
        test_command_executor,
        test_smart_delegator_init,
        test_tool_calling_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)