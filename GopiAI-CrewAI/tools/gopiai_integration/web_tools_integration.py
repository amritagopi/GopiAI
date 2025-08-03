"""
Интеграция веб-инструментов для SmartDelegator.
Добавляет поддержку browse_website и web_search через CommandExecutor.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WebToolsIntegration:
    """
    Класс для интеграции веб-инструментов в SmartDelegator.
    Обеспечивает выполнение browse_website и web_search через CommandExecutor.
    """
    
    def __init__(self):
        self.command_executor = None
        self._initialize_command_executor()
    
    def _initialize_command_executor(self):
        """Инициализирует CommandExecutor для выполнения веб-инструментов."""
        try:
            # Пробуем разные варианты импорта
            try:
                from .command_executor import CommandExecutor
            except ImportError:
                from command_executor import CommandExecutor
            
            self.command_executor = CommandExecutor()
            logger.info("[WEB-TOOLS] CommandExecutor инициализирован для веб-инструментов")
        except ImportError as e:
            logger.error(f"[WEB-TOOLS] Не удалось импортировать CommandExecutor: {e}")
            self.command_executor = None
        except Exception as e:
            logger.error(f"[WEB-TOOLS] Ошибка инициализации CommandExecutor: {e}")
            self.command_executor = None
    
    def is_available(self) -> bool:
        """Проверяет, доступны ли веб-инструменты."""
        return self.command_executor is not None
    
    def execute_tool_call(self, tool_call) -> str:
        """
        Выполняет вызов веб-инструмента.
        
        Args:
            tool_call: Объект вызова инструмента от LLM
            
        Returns:
            str: Результат выполнения инструмента
        """
        if not self.is_available():
            return "Ошибка: веб-инструменты недоступны (CommandExecutor не инициализирован)"
        
        try:
            function_name = tool_call.function.name
            arguments_str = tool_call.function.arguments
            
            logger.info(f"[WEB-TOOLS] Выполняем веб-инструмент: {function_name}")
            logger.debug(f"[WEB-TOOLS] Аргументы: {arguments_str}")
            
            # Парсим аргументы
            try:
                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str) if arguments_str.strip() else {}
                elif isinstance(arguments_str, dict):
                    arguments = arguments_str
                else:
                    arguments = {}
            except json.JSONDecodeError as e:
                logger.error(f"[WEB-TOOLS] Ошибка парсинга аргументов: {e}")
                return f"Ошибка парсинга аргументов: {str(e)}"
            
            # Выполняем соответствующий метод
            if function_name == "browse_website":
                return self._execute_browse_website(arguments)
            elif function_name == "web_search":
                return self._execute_web_search(arguments)
            else:
                return f"Неизвестный веб-инструмент: {function_name}"
                
        except Exception as e:
            logger.error(f"[WEB-TOOLS] Ошибка выполнения веб-инструмента: {e}")
            return f"Ошибка выполнения веб-инструмента: {str(e)}"
    
    def _execute_browse_website(self, arguments: Dict[str, Any]) -> str:
        """
        Выполняет browse_website через CommandExecutor.
        
        Args:
            arguments: Аргументы для browse_website
            
        Returns:
            str: Результат просмотра веб-страницы
        """
        try:
            # Извлекаем параметры с значениями по умолчанию
            url = arguments.get("url", "")
            action = arguments.get("action", "navigate")
            selector = arguments.get("selector", "")
            extract_text = arguments.get("extract_text", True)
            max_content_length = arguments.get("max_content_length", 3000)
            
            if not url:
                return "Ошибка: не указан URL для просмотра"
            
            logger.info(f"[WEB-TOOLS] Просмотр веб-страницы: {url}")
            
            # Вызываем метод CommandExecutor
            result = self.command_executor.browse_website(
                url=url,
                action=action,
                selector=selector,
                extract_text=extract_text,
                max_content_length=max_content_length
            )
            
            logger.info(f"[WEB-TOOLS] Просмотр завершен, результат: {len(str(result))} символов")
            return result
            
        except Exception as e:
            logger.error(f"[WEB-TOOLS] Ошибка в _execute_browse_website: {e}")
            return f"Ошибка просмотра веб-страницы: {str(e)}"
    
    def _execute_web_search(self, arguments: Dict[str, Any]) -> str:
        """
        Выполняет web_search через CommandExecutor.
        
        Args:
            arguments: Аргументы для web_search
            
        Returns:
            str: Результаты поиска
        """
        try:
            # Извлекаем параметры с значениями по умолчанию
            query = arguments.get("query", "")
            num_results = arguments.get("num_results", 5)
            search_engine = arguments.get("search_engine", "duckduckgo")
            
            if not query:
                return "Ошибка: не указан поисковый запрос"
            
            # Ограничиваем количество результатов
            num_results = max(1, min(num_results, 10))
            
            logger.info(f"[WEB-TOOLS] Поиск в интернете: '{query}' ({num_results} результатов)")
            
            # Вызываем метод CommandExecutor
            result = self.command_executor.web_search(
                query=query,
                num_results=num_results,
                search_engine=search_engine
            )
            
            logger.info(f"[WEB-TOOLS] Поиск завершен, результат: {len(str(result))} символов")
            return result
            
        except Exception as e:
            logger.error(f"[WEB-TOOLS] Ошибка в _execute_web_search: {e}")
            return f"Ошибка поиска в интернете: {str(e)}"
    
    def get_supported_tools(self) -> list:
        """Возвращает список поддерживаемых веб-инструментов."""
        return ["browse_website", "web_search"]
    
    def validate_tool_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует вызов веб-инструмента.
        
        Args:
            function_name: Имя функции
            arguments: Аргументы функции
            
        Returns:
            Dict: Результат валидации
        """
        errors = []
        
        if function_name == "browse_website":
            if not arguments.get("url"):
                errors.append("Отсутствует обязательный параметр 'url'")
            else:
                url = arguments["url"]
                if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                    errors.append("URL должен быть строкой и начинаться с http:// или https://")
        
        elif function_name == "web_search":
            if not arguments.get("query"):
                errors.append("Отсутствует обязательный параметр 'query'")
            else:
                query = arguments["query"]
                if not isinstance(query, str) or len(query.strip()) == 0:
                    errors.append("Поисковый запрос должен быть непустой строкой")
            
            # Проверяем num_results
            num_results = arguments.get("num_results", 5)
            if not isinstance(num_results, int) or num_results < 1 or num_results > 10:
                errors.append("num_results должно быть целым числом от 1 до 10")
        
        else:
            errors.append(f"Неизвестный веб-инструмент: {function_name}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# Глобальный экземпляр для использования в SmartDelegator
web_tools_integration = WebToolsIntegration()


def integrate_web_tools_to_smart_delegator(smart_delegator_instance):
    """
    Интегрирует веб-инструменты в экземпляр SmartDelegator.
    
    Args:
        smart_delegator_instance: Экземпляр SmartDelegator для интеграции
    """
    if not hasattr(smart_delegator_instance, '_web_tools'):
        smart_delegator_instance._web_tools = web_tools_integration
        logger.info("[WEB-TOOLS] Веб-инструменты интегрированы в SmartDelegator")
    
    # Добавляем метод для выполнения веб-инструментов
    def _execute_web_tool(self, tool_call):
        """Выполняет веб-инструмент через интеграцию."""
        if hasattr(self, '_web_tools') and self._web_tools.is_available():
            return self._web_tools.execute_tool_call(tool_call)
        else:
            return "Ошибка: веб-инструменты недоступны"
    
    # Привязываем метод к экземпляру
    import types
    smart_delegator_instance._execute_web_tool = types.MethodType(_execute_web_tool, smart_delegator_instance)
    
    logger.info("[WEB-TOOLS] Методы веб-инструментов добавлены в SmartDelegator")


def get_web_tools_schema():
    """
    Возвращает схемы веб-инструментов для OpenAI Tool Calling.
    
    Returns:
        List[Dict]: Список схем веб-инструментов
    """
    try:
        # Пробуем разные варианты импорта
        try:
            from .tool_definitions import get_tool_schema
        except ImportError:
            from tool_definitions import get_tool_schema
        
        all_tools = get_tool_schema()
        
        # Фильтруем только веб-инструменты
        web_tools = []
        for tool in all_tools:
            function_name = tool.get("function", {}).get("name", "")
            if function_name in ["browse_website", "web_search"]:
                web_tools.append(tool)
        
        return web_tools
    except ImportError:
        logger.warning("[WEB-TOOLS] Не удалось импортировать tool_definitions")
        return []


if __name__ == "__main__":
    # Тестирование интеграции веб-инструментов
    print("🌐 Тестирование интеграции веб-инструментов")
    print("=" * 50)
    
    # Создаем экземпляр интеграции
    integration = WebToolsIntegration()
    
    print(f"Веб-инструменты доступны: {integration.is_available()}")
    print(f"Поддерживаемые инструменты: {integration.get_supported_tools()}")
    
    # Тестируем валидацию
    print("\nТестирование валидации:")
    
    # Валидный вызов browse_website
    validation = integration.validate_tool_call("browse_website", {"url": "https://example.com"})
    print(f"browse_website с валидным URL: {validation}")
    
    # Невалидный вызов browse_website
    validation = integration.validate_tool_call("browse_website", {})
    print(f"browse_website без URL: {validation}")
    
    # Валидный вызов web_search
    validation = integration.validate_tool_call("web_search", {"query": "Python tutorial"})
    print(f"web_search с валидным запросом: {validation}")
    
    # Невалидный вызов web_search
    validation = integration.validate_tool_call("web_search", {})
    print(f"web_search без запроса: {validation}")
    
    print("\n✅ Тестирование завершено")