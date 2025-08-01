#!/usr/bin/env python3
"""
Тест нативного Tool Calling в SmartDelegator
Проверяет корректность реализации OpenAI-совместимого Tool Calling
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("🚀 Запуск тестов нативного Tool Calling")
print("=" * 60)

def test_tool_schema_loading():
    """Тест загрузки схем инструментов"""
    print("🔧 Тест 1: Загрузка схем инструментов")
    
    try:
        from tool_definitions import get_tool_schema, get_available_tools
        
        # Получаем схемы инструментов
        tools = get_tool_schema()
        tool_names = get_available_tools()
        
        print(f"✅ Загружено инструментов: {len(tools)}")
        print(f"✅ Названия инструментов: {', '.join(tool_names)}")
        
        # Проверяем формат схем
        for tool in tools:
            assert "type" in tool, f"Отсутствует 'type' в инструменте: {tool}"
            assert tool["type"] == "function", f"Неверный тип инструмента: {tool['type']}"
            assert "function" in tool, f"Отсутствует 'function' в инструменте: {tool}"
            
            function = tool["function"]
            assert "name" in function, f"Отсутствует 'name' в функции: {function}"
            assert "description" in function, f"Отсутствует 'description' в функции: {function}"
            assert "parameters" in function, f"Отсутствует 'parameters' в функции: {function}"
        
        print("✅ Все схемы инструментов корректны")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки схем: {e}")
        return False

def test_json_parsing():
    """Тест парсинга JSON аргументов"""
    print("\n🔧 Тест 2: Парсинг JSON аргументов")
    
    try:
        from smart_delegator import SmartDelegator
        
        # Создаем экземпляр SmartDelegator
        delegator = SmartDelegator()
        
        # Тестовые случаи для парсинга
        test_cases = [
            ('{"command": "ls -la"}', {"command": "ls -la"}),
            ("{'command': 'pwd'}", {"command": "pwd"}),
            ('{"path": "/tmp", "operation": "read"}', {"path": "/tmp", "operation": "read"}),
            ('', {}),
            ('{"command": "echo hello",}', {"command": "echo hello"}),  # trailing comma
        ]
        
        for test_input, expected in test_cases:
            result = delegator._parse_tool_arguments(test_input, "test_function")
            if isinstance(result, str) and result.startswith("Ошибка"):
                print(f"❌ Не удалось распарсить: {test_input}")
                return False
            elif result != expected:
                print(f"❌ Неверный результат для {test_input}: получено {result}, ожидалось {expected}")
                return False
            else:
                print(f"✅ Успешно распарсено: {test_input} -> {result}")
        
        print("✅ Все тесты парсинга JSON прошли успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования парсинга: {e}")
        return False

def test_tool_validation():
    """Тест валидации вызовов инструментов"""
    print("\n🔧 Тест 3: Валидация вызовов инструментов")
    
    try:
        from tool_definitions import validate_tool_call
        
        # Тестовые случаи валидации
        test_cases = [
            # Валидные случаи
            ("execute_terminal_command", {"command": "ls"}, True),
            ("file_operations", {"operation": "read", "path": "/tmp/test.txt"}, True),
            ("web_search", {"query": "python tutorial"}, True),
            
            # Невалидные случаи
            ("execute_terminal_command", {}, False),  # отсутствует обязательный параметр
            ("unknown_tool", {"param": "value"}, False),  # неизвестный инструмент
            ("file_operations", {"operation": "invalid_op", "path": "/tmp"}, False),  # неверное enum значение
        ]
        
        for tool_name, args, should_be_valid in test_cases:
            result = validate_tool_call(tool_name, args)
            is_valid = result["valid"]
            
            if is_valid != should_be_valid:
                print(f"❌ Неверная валидация для {tool_name} с {args}: получено {is_valid}, ожидалось {should_be_valid}")
                if not is_valid:
                    print(f"   Ошибки: {result['errors']}")
                return False
            else:
                status = "✅ валидно" if is_valid else "✅ невалидно (как ожидалось)"
                print(f"{status}: {tool_name} с {args}")
        
        print("✅ Все тесты валидации прошли успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования валидации: {e}")
        return False

def test_mock_llm_with_tools():
    """Тест вызова LLM с мок-инструментами"""
    print("\n🔧 Тест 4: Мок-тест вызова LLM с инструментами")
    
    try:
        from smart_delegator import SmartDelegator
        
        # Создаем мок-ответ от LLM с tool_calls
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "execute_terminal_command"
        mock_tool_call.function.arguments = '{"command": "pwd"}'
        
        mock_message = Mock()
        mock_message.content = "Я выполню команду для вас."
        mock_message.tool_calls = [mock_tool_call]
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        # Создаем экземпляр SmartDelegator
        delegator = SmartDelegator()
        
        # Мокаем методы
        with patch.object(delegator, '_get_model_for_request', return_value='test-model'):
            with patch.object(delegator, '_make_llm_request', return_value=mock_response):
                with patch.object(delegator, '_execute_tool_call', return_value="Current directory: /home/user"):
                    
                    # Создаем финальный мок-ответ
                    final_mock_message = Mock()
                    final_mock_message.content = "Текущая директория: /home/user"
                    final_mock_message.tool_calls = None
                    
                    final_mock_choice = Mock()
                    final_mock_choice.message = final_mock_message
                    
                    final_mock_response = Mock()
                    final_mock_response.choices = [final_mock_choice]
                    
                    # Настраиваем side_effect для последовательных вызовов
                    delegator._make_llm_request.side_effect = [mock_response, final_mock_response]
                    
                    # Тестируем вызов
                    messages = [{"role": "user", "content": "Покажи текущую директорию"}]
                    tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": "execute_terminal_command",
                                "description": "Execute terminal command",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string"}
                                    },
                                    "required": ["command"]
                                }
                            }
                        }
                    ]
                    
                    result = delegator._call_llm_with_tools(messages, tools, max_iterations=2)
                    
                    print(f"✅ Результат мок-теста: {result}")
                    
                    # Проверяем, что методы были вызваны
                    assert delegator._make_llm_request.call_count == 2, "LLM должен был быть вызван 2 раза"
                    assert delegator._execute_tool_call.call_count == 1, "Инструмент должен был быть вызван 1 раз"
                    
        print("✅ Мок-тест прошел успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка мок-теста: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Тест обработки ошибок"""
    print("\n🔧 Тест 5: Обработка ошибок")
    
    try:
        from smart_delegator import SmartDelegator
        from litellm import RateLimitError, AuthenticationError, InvalidRequestError
        
        delegator = SmartDelegator()
        
        # Тест обработки ошибок парсинга JSON
        invalid_json = '{"command": "test", invalid}'
        result = delegator._parse_tool_arguments(invalid_json, "test_function")
        assert isinstance(result, str) and "Ошибка" in result, "Должна быть возвращена ошибка парсинга"
        print("✅ Обработка ошибок парсинга JSON работает")
        
        # Тест retry логики
        call_count = 0
        def mock_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("Rate limit exceeded")
            return "Success"
        
        with patch('time.sleep'):  # Мокаем sleep для ускорения теста
            result = delegator._retry_with_backoff(mock_failing_function, max_retries=3, base_delay=0.1)
            assert result == "Success", "Retry должен был в итоге успешно выполниться"
            assert call_count == 3, f"Функция должна была быть вызвана 3 раза, но была вызвана {call_count} раз"
        
        print("✅ Retry логика работает корректно")
        
        print("✅ Все тесты обработки ошибок прошли успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования обработки ошибок: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов нативного Tool Calling")
    print("=" * 60)
    
    tests = [
        test_tool_schema_loading,
        test_json_parsing,
        test_tool_validation,
        test_mock_llm_with_tools,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования:")
    print(f"✅ Прошло: {passed}")
    print(f"❌ Не прошло: {failed}")
    print(f"📈 Успешность: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 Все тесты прошли успешно! Нативный Tool Calling готов к использованию.")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется доработка.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)