"""
OpenAI-совместимые схемы инструментов для GopiAI
Определяет стандартные схемы инструментов в формате OpenAI Function Calling
"""

from typing import Dict, List, Any, Optional
import json


def get_tool_schema() -> List[Dict[str, Any]]:
    """
    Возвращает список всех доступных инструментов в формате OpenAI Function Calling
    
    Returns:
        List[Dict]: Список схем инструментов в стандартном формате OpenAI
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "execute_terminal_command",
                "description": "Выполняет безопасные команды терминала с проверкой безопасности и таймаутом",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Команда для выполнения в терминале (только безопасные команды из белого списка)"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Рабочая директория для выполнения команды (опционально)",
                            "default": "."
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Таймаут выполнения в секундах (максимум 30)",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 30
                        }
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browse_website",
                "description": "Открывает веб-страницу и извлекает её содержимое с поддержкой различных браузерных движков",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL веб-страницы для открытия"
                        },
                        "action": {
                            "type": "string",
                            "description": "Действие для выполнения",
                            "enum": ["navigate", "extract", "click", "type", "screenshot", "scroll", "wait"],
                            "default": "navigate"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS селектор или XPath для взаимодействия с элементом (для click, type, extract)",
                            "default": ""
                        },
                        "text": {
                            "type": "string",
                            "description": "Текст для ввода (для действия type)",
                            "default": ""
                        },
                        "browser_type": {
                            "type": "string",
                            "description": "Тип браузерного движка",
                            "enum": ["auto", "selenium", "playwright", "requests"],
                            "default": "auto"
                        },
                        "headless": {
                            "type": "boolean",
                            "description": "Запуск в headless режиме",
                            "default": True
                        },
                        "wait_seconds": {
                            "type": "integer",
                            "description": "Время ожидания после действия в секундах",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Выполняет поиск в интернете через различные поисковые системы",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Поисковый запрос"
                        },
                        "search_engine": {
                            "type": "string",
                            "description": "Поисковая система для использования",
                            "enum": ["google", "bing", "duckduckgo", "yandex"],
                            "default": "google"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Количество результатов для возврата",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Тип поиска",
                            "enum": ["quick_search", "full_search"],
                            "default": "quick_search"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "file_operations",
                "description": "Выполняет безопасные операции с файловой системой",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Тип операции с файлом",
                            "enum": [
                                "read", "write", "append", "delete", "list", "exists", 
                                "mkdir", "remove", "copy", "move", "info", "find",
                                "read_json", "write_json", "read_csv", "write_csv",
                                "hash", "backup", "compare", "tree", "search_text", "replace_text"
                            ]
                        },
                        "path": {
                            "type": "string",
                            "description": "Путь к файлу или директории"
                        },
                        "content": {
                            "type": "string",
                            "description": "Содержимое для записи (для операций write, append, replace_text)",
                            "default": ""
                        },
                        "destination": {
                            "type": "string",
                            "description": "Путь назначения (для операций copy, move)",
                            "default": ""
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Паттерн для поиска файлов (для операции find)",
                            "default": "*"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Рекурсивный поиск (для операции find)",
                            "default": False
                        },
                        "search_term": {
                            "type": "string",
                            "description": "Текст для поиска (для операции search_text)",
                            "default": ""
                        },
                        "old_text": {
                            "type": "string",
                            "description": "Текст для замены (для операции replace_text)",
                            "default": ""
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Учитывать регистр при поиске",
                            "default": False
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Максимальная глубина для операции tree",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["operation", "path"]
                }
            }
        }
    ]


def get_tool_by_name(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Возвращает схему инструмента по его имени
    
    Args:
        tool_name: Имя инструмента
        
    Returns:
        Dict или None: Схема инструмента или None если не найден
    """
    tools = get_tool_schema()
    for tool in tools:
        if tool["function"]["name"] == tool_name:
            return tool
    return None


def get_available_tools() -> List[str]:
    """
    Возвращает список имен всех доступных инструментов
    
    Returns:
        List[str]: Список имен инструментов
    """
    tools = get_tool_schema()
    return [tool["function"]["name"] for tool in tools]


def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валидирует вызов инструмента против его схемы
    
    Args:
        tool_name: Имя инструмента
        arguments: Аргументы для вызова
        
    Returns:
        Dict: Результат валидации с полями 'valid', 'errors', 'normalized_args'
    """
    tool_schema = get_tool_by_name(tool_name)
    if not tool_schema:
        return {
            "valid": False,
            "errors": [f"Инструмент '{tool_name}' не найден"],
            "normalized_args": {}
        }
    
    function_schema = tool_schema["function"]
    parameters = function_schema.get("parameters", {})
    properties = parameters.get("properties", {})
    required = parameters.get("required", [])
    
    errors = []
    normalized_args = {}
    
    # Проверяем обязательные параметры
    for req_param in required:
        if req_param not in arguments:
            errors.append(f"Отсутствует обязательный параметр: {req_param}")
    
    # Валидируем и нормализуем каждый аргумент
    for arg_name, arg_value in arguments.items():
        if arg_name not in properties:
            errors.append(f"Неизвестный параметр: {arg_name}")
            continue
            
        prop_schema = properties[arg_name]
        
        # Проверяем тип
        expected_type = prop_schema.get("type")
        if expected_type == "string" and not isinstance(arg_value, str):
            errors.append(f"Параметр '{arg_name}' должен быть строкой")
        elif expected_type == "integer" and not isinstance(arg_value, int):
            errors.append(f"Параметр '{arg_name}' должен быть целым числом")
        elif expected_type == "boolean" and not isinstance(arg_value, bool):
            errors.append(f"Параметр '{arg_name}' должен быть булевым значением")
        
        # Проверяем enum значения
        if "enum" in prop_schema and arg_value not in prop_schema["enum"]:
            errors.append(f"Параметр '{arg_name}' должен быть одним из: {prop_schema['enum']}")
        
        # Проверяем диапазоны для чисел
        if expected_type == "integer":
            if "minimum" in prop_schema and arg_value < prop_schema["minimum"]:
                errors.append(f"Параметр '{arg_name}' должен быть >= {prop_schema['minimum']}")
            if "maximum" in prop_schema and arg_value > prop_schema["maximum"]:
                errors.append(f"Параметр '{arg_name}' должен быть <= {prop_schema['maximum']}")
        
        normalized_args[arg_name] = arg_value
    
    # Добавляем значения по умолчанию
    for prop_name, prop_schema in properties.items():
        if prop_name not in normalized_args and "default" in prop_schema:
            normalized_args[prop_name] = prop_schema["default"]
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "normalized_args": normalized_args
    }


def get_tool_usage_examples() -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает примеры использования для каждого инструмента
    
    Returns:
        Dict: Словарь с примерами использования для каждого инструмента
    """
    return {
        "execute_terminal_command": [
            {
                "description": "Список файлов в текущей директории",
                "arguments": {"command": "ls -la"}
            },
            {
                "description": "Проверка версии Python",
                "arguments": {"command": "python --version"}
            },
            {
                "description": "Создание директории",
                "arguments": {"command": "mkdir test_dir"}
            }
        ],
        "browse_website": [
            {
                "description": "Открыть веб-страницу и извлечь содержимое",
                "arguments": {
                    "url": "https://example.com",
                    "action": "navigate"
                }
            },
            {
                "description": "Извлечь текст из определенного элемента",
                "arguments": {
                    "url": "https://example.com",
                    "action": "extract",
                    "selector": "h1"
                }
            },
            {
                "description": "Сделать скриншот страницы",
                "arguments": {
                    "url": "https://example.com",
                    "action": "screenshot"
                }
            }
        ],
        "web_search": [
            {
                "description": "Поиск в Google",
                "arguments": {
                    "query": "Python programming tutorial",
                    "search_engine": "google",
                    "num_results": 5
                }
            },
            {
                "description": "Быстрый поиск в DuckDuckGo",
                "arguments": {
                    "query": "machine learning basics",
                    "search_engine": "duckduckgo",
                    "search_type": "quick_search"
                }
            }
        ],
        "file_operations": [
            {
                "description": "Прочитать содержимое файла",
                "arguments": {
                    "operation": "read",
                    "path": "example.txt"
                }
            },
            {
                "description": "Записать текст в файл",
                "arguments": {
                    "operation": "write",
                    "path": "output.txt",
                    "content": "Hello, World!"
                }
            },
            {
                "description": "Найти файлы по паттерну",
                "arguments": {
                    "operation": "find",
                    "path": ".",
                    "pattern": "*.py",
                    "recursive": True
                }
            },
            {
                "description": "Получить информацию о файле",
                "arguments": {
                    "operation": "info",
                    "path": "example.txt"
                }
            }
        ]
    }


def export_schema_to_json(output_path: str = "tool_schema.json") -> str:
    """
    Экспортирует схему инструментов в JSON файл
    
    Args:
        output_path: Путь для сохранения JSON файла
        
    Returns:
        str: Сообщение о результате экспорта
    """
    try:
        schema_data = {
            "tools": get_tool_schema(),
            "available_tools": get_available_tools(),
            "usage_examples": get_tool_usage_examples(),
            "version": "1.0.0",
            "format": "OpenAI Function Calling"
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        
        return f"Схема инструментов успешно экспортирована в {output_path}"
    except Exception as e:
        return f"Ошибка при экспорте схемы: {str(e)}"


if __name__ == "__main__":
    # Демонстрация работы модуля
    print("🔧 GopiAI Tool Definitions - OpenAI Compatible Schema")
    print("=" * 60)
    
    # Показываем доступные инструменты
    tools = get_available_tools()
    print(f"📋 Доступные инструменты ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool}")
    
    print("\n" + "=" * 60)
    
    # Показываем пример схемы одного инструмента
    example_tool = get_tool_by_name("execute_terminal_command")
    if example_tool:
        print("📄 Пример схемы инструмента 'execute_terminal_command':")
        print(json.dumps(example_tool, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    
    # Тестируем валидацию
    print("✅ Тест валидации:")
    test_args = {"command": "ls -la", "timeout": 10}
    validation_result = validate_tool_call("execute_terminal_command", test_args)
    print(f"Валидация аргументов {test_args}:")
    print(f"  Валидно: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"  Ошибки: {validation_result['errors']}")
    print(f"  Нормализованные аргументы: {validation_result['normalized_args']}")
    
    print("\n" + "=" * 60)
    
    # Экспортируем схему
    export_result = export_schema_to_json("tool_schema_export.json")
    print(f"📤 {export_result}")