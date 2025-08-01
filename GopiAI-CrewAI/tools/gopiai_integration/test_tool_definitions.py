"""
Unit тесты для модуля tool_definitions.py
Проверяет корректность OpenAI-совместимых схем инструментов
"""

import unittest
import json
import os
from typing import Dict, Any

from tool_definitions import (
    get_tool_schema,
    get_tool_by_name,
    get_available_tools,
    validate_tool_call,
    get_tool_usage_examples,
    export_schema_to_json
)


class TestToolDefinitions(unittest.TestCase):
    """Тесты для модуля определений инструментов"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.expected_tools = [
            "execute_terminal_command",
            "browse_website", 
            "web_search",
            "file_operations"
        ]
    
    def test_get_tool_schema_structure(self):
        """Тест структуры схемы инструментов"""
        schema = get_tool_schema()
        
        # Проверяем, что возвращается список
        self.assertIsInstance(schema, list)
        self.assertGreater(len(schema), 0)
        
        # Проверяем структуру каждого инструмента
        for tool in schema:
            self.assertIsInstance(tool, dict)
            self.assertIn("type", tool)
            self.assertEqual(tool["type"], "function")
            self.assertIn("function", tool)
            
            function = tool["function"]
            self.assertIn("name", function)
            self.assertIn("description", function)
            self.assertIn("parameters", function)
            
            parameters = function["parameters"]
            self.assertIn("type", parameters)
            self.assertEqual(parameters["type"], "object")
            self.assertIn("properties", parameters)
            self.assertIn("required", parameters)
    
    def test_get_available_tools(self):
        """Тест получения списка доступных инструментов"""
        tools = get_available_tools()
        
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), len(self.expected_tools))
        
        for expected_tool in self.expected_tools:
            self.assertIn(expected_tool, tools)
    
    def test_get_tool_by_name(self):
        """Тест получения инструмента по имени"""
        # Тест существующего инструмента
        tool = get_tool_by_name("execute_terminal_command")
        self.assertIsNotNone(tool)
        self.assertEqual(tool["function"]["name"], "execute_terminal_command")
        
        # Тест несуществующего инструмента
        tool = get_tool_by_name("nonexistent_tool")
        self.assertIsNone(tool)
    
    def test_execute_terminal_command_schema(self):
        """Тест схемы инструмента execute_terminal_command"""
        tool = get_tool_by_name("execute_terminal_command")
        self.assertIsNotNone(tool)
        
        function = tool["function"]
        parameters = function["parameters"]
        properties = parameters["properties"]
        
        # Проверяем обязательные параметры
        self.assertIn("command", parameters["required"])
        
        # Проверяем свойства параметров
        self.assertIn("command", properties)
        self.assertEqual(properties["command"]["type"], "string")
        
        self.assertIn("working_directory", properties)
        self.assertEqual(properties["working_directory"]["type"], "string")
        
        self.assertIn("timeout", properties)
        self.assertEqual(properties["timeout"]["type"], "integer")
        self.assertEqual(properties["timeout"]["minimum"], 1)
        self.assertEqual(properties["timeout"]["maximum"], 30)
    
    def test_browse_website_schema(self):
        """Тест схемы инструмента browse_website"""
        tool = get_tool_by_name("browse_website")
        self.assertIsNotNone(tool)
        
        function = tool["function"]
        parameters = function["parameters"]
        properties = parameters["properties"]
        
        # Проверяем обязательные параметры
        self.assertIn("url", parameters["required"])
        
        # Проверяем enum значения для action
        self.assertIn("action", properties)
        expected_actions = ["navigate", "extract", "click", "type", "screenshot", "scroll", "wait"]
        self.assertEqual(properties["action"]["enum"], expected_actions)
        
        # Проверяем enum значения для browser_type
        self.assertIn("browser_type", properties)
        expected_browsers = ["auto", "selenium", "playwright", "requests"]
        self.assertEqual(properties["browser_type"]["enum"], expected_browsers)
    
    def test_web_search_schema(self):
        """Тест схемы инструмента web_search"""
        tool = get_tool_by_name("web_search")
        self.assertIsNotNone(tool)
        
        function = tool["function"]
        parameters = function["parameters"]
        properties = parameters["properties"]
        
        # Проверяем обязательные параметры
        self.assertIn("query", parameters["required"])
        
        # Проверяем enum значения для search_engine
        self.assertIn("search_engine", properties)
        expected_engines = ["google", "bing", "duckduckgo", "yandex"]
        self.assertEqual(properties["search_engine"]["enum"], expected_engines)
        
        # Проверяем диапазон для num_results
        self.assertIn("num_results", properties)
        self.assertEqual(properties["num_results"]["minimum"], 1)
        self.assertEqual(properties["num_results"]["maximum"], 20)
    
    def test_file_operations_schema(self):
        """Тест схемы инструмента file_operations"""
        tool = get_tool_by_name("file_operations")
        self.assertIsNotNone(tool)
        
        function = tool["function"]
        parameters = function["parameters"]
        properties = parameters["properties"]
        
        # Проверяем обязательные параметры
        required = parameters["required"]
        self.assertIn("operation", required)
        self.assertIn("path", required)
        
        # Проверяем enum значения для operation
        self.assertIn("operation", properties)
        expected_operations = [
            "read", "write", "append", "delete", "list", "exists", 
            "mkdir", "remove", "copy", "move", "info", "find",
            "read_json", "write_json", "read_csv", "write_csv",
            "hash", "backup", "compare", "tree", "search_text", "replace_text"
        ]
        self.assertEqual(properties["operation"]["enum"], expected_operations)
    
    def test_validate_tool_call_valid(self):
        """Тест валидации корректного вызова инструмента"""
        # Тест с минимальными аргументами
        result = validate_tool_call("execute_terminal_command", {"command": "ls"})
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertIn("command", result["normalized_args"])
        
        # Тест с дополнительными аргументами
        result = validate_tool_call("execute_terminal_command", {
            "command": "ls -la",
            "timeout": 15,
            "working_directory": "/tmp"
        })
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(result["normalized_args"]["timeout"], 15)
    
    def test_validate_tool_call_invalid(self):
        """Тест валидации некорректного вызова инструмента"""
        # Тест отсутствующего обязательного параметра
        result = validate_tool_call("execute_terminal_command", {})
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)
        self.assertIn("Отсутствует обязательный параметр: command", result["errors"])
        
        # Тест неверного типа параметра
        result = validate_tool_call("execute_terminal_command", {"command": 123})
        self.assertFalse(result["valid"])
        self.assertIn("Параметр 'command' должен быть строкой", result["errors"])
        
        # Тест неверного enum значения
        result = validate_tool_call("browse_website", {
            "url": "https://example.com",
            "action": "invalid_action"
        })
        self.assertFalse(result["valid"])
        self.assertTrue(any("должен быть одним из" in error for error in result["errors"]))
        
        # Тест несуществующего инструмента
        result = validate_tool_call("nonexistent_tool", {"param": "value"})
        self.assertFalse(result["valid"])
        self.assertIn("Инструмент 'nonexistent_tool' не найден", result["errors"])
    
    def test_validate_tool_call_ranges(self):
        """Тест валидации диапазонов значений"""
        # Тест превышения максимума
        result = validate_tool_call("execute_terminal_command", {
            "command": "ls",
            "timeout": 100  # Максимум 30
        })
        self.assertFalse(result["valid"])
        self.assertTrue(any("должен быть <= 30" in error for error in result["errors"]))
        
        # Тест ниже минимума
        result = validate_tool_call("execute_terminal_command", {
            "command": "ls",
            "timeout": 0  # Минимум 1
        })
        self.assertFalse(result["valid"])
        self.assertTrue(any("должен быть >= 1" in error for error in result["errors"]))
    
    def test_validate_tool_call_defaults(self):
        """Тест применения значений по умолчанию"""
        result = validate_tool_call("execute_terminal_command", {"command": "ls"})
        self.assertTrue(result["valid"])
        
        # Проверяем, что применились значения по умолчанию
        normalized = result["normalized_args"]
        self.assertEqual(normalized["working_directory"], ".")
        self.assertEqual(normalized["timeout"], 30)
    
    def test_get_tool_usage_examples(self):
        """Тест получения примеров использования"""
        examples = get_tool_usage_examples()
        
        self.assertIsInstance(examples, dict)
        
        # Проверяем, что есть примеры для всех инструментов
        for tool_name in self.expected_tools:
            self.assertIn(tool_name, examples)
            self.assertIsInstance(examples[tool_name], list)
            self.assertGreater(len(examples[tool_name]), 0)
            
            # Проверяем структуру примеров
            for example in examples[tool_name]:
                self.assertIn("description", example)
                self.assertIn("arguments", example)
                self.assertIsInstance(example["arguments"], dict)
    
    def test_export_schema_to_json(self):
        """Тест экспорта схемы в JSON"""
        test_file = "test_schema_export.json"
        
        try:
            result = export_schema_to_json(test_file)
            self.assertIn("успешно экспортирована", result)
            
            # Проверяем, что файл создался
            self.assertTrue(os.path.exists(test_file))
            
            # Проверяем содержимое файла
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertIn("tools", data)
            self.assertIn("available_tools", data)
            self.assertIn("usage_examples", data)
            self.assertIn("version", data)
            self.assertIn("format", data)
            
            self.assertEqual(data["format"], "OpenAI Function Calling")
            self.assertEqual(len(data["available_tools"]), len(self.expected_tools))
            
        finally:
            # Очищаем тестовый файл
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_schema_completeness(self):
        """Тест полноты схемы - все инструменты должны иметь полную документацию"""
        schema = get_tool_schema()
        
        for tool in schema:
            function = tool["function"]
            
            # Проверяем наличие описания
            self.assertIsInstance(function["description"], str)
            self.assertGreater(len(function["description"]), 10)
            
            # Проверяем параметры
            parameters = function["parameters"]
            properties = parameters["properties"]
            
            for prop_name, prop_schema in properties.items():
                # Каждое свойство должно иметь описание
                self.assertIn("description", prop_schema)
                self.assertIsInstance(prop_schema["description"], str)
                self.assertGreater(len(prop_schema["description"]), 5)
                
                # Каждое свойство должно иметь тип
                self.assertIn("type", prop_schema)
                self.assertIn(prop_schema["type"], ["string", "integer", "boolean", "array", "object"])


class TestToolSchemaIntegration(unittest.TestCase):
    """Интеграционные тесты для проверки совместимости с реальными инструментами"""
    
    def test_terminal_command_integration(self):
        """Тест интеграции с реальным терминальным инструментом"""
        # Проверяем, что схема соответствует ожидаемому интерфейсу
        tool = get_tool_by_name("execute_terminal_command")
        self.assertIsNotNone(tool)
        
        # Тестируем валидацию реальных команд
        valid_commands = [
            {"command": "ls"},
            {"command": "pwd"},
            {"command": "echo 'test'"},
            {"command": "python --version"}
        ]
        
        for cmd_args in valid_commands:
            result = validate_tool_call("execute_terminal_command", cmd_args)
            self.assertTrue(result["valid"], f"Команда {cmd_args} должна быть валидной")
    
    def test_file_operations_integration(self):
        """Тест интеграции с файловыми операциями"""
        tool = get_tool_by_name("file_operations")
        self.assertIsNotNone(tool)
        
        # Тестируем различные операции
        operations = [
            {"operation": "read", "path": "test.txt"},
            {"operation": "write", "path": "test.txt", "content": "test"},
            {"operation": "list", "path": "."},
            {"operation": "exists", "path": "test.txt"},
            {"operation": "find", "path": ".", "pattern": "*.py", "recursive": True}
        ]
        
        for op_args in operations:
            result = validate_tool_call("file_operations", op_args)
            self.assertTrue(result["valid"], f"Операция {op_args} должна быть валидной")


if __name__ == "__main__":
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)