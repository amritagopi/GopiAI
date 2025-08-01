# 🚀 TASK 1.3: ПЕРЕПИСАТЬ ВЫЗОВ LLM С НАТИВНЫМ TOOL CALLING

## 🎯 ЦЕЛЬ
Модифицировать функцию `_call_llm` для использования нативного Tool Calling вместо парсинга текста. Реализовать двухэтапный процесс: вызов инструмента → финальный ответ.

## 📁 ЦЕЛЕВЫЕ ФАЙЛЫ
- `GopiAI-CrewAI/tools/gopiai_integration/smart_delegator.py`
- Функция `_call_llm` или аналогичная
- Места вызова `litellm.completion()`

## 🔍 ЧТО НАЙТИ И ИЗМЕНИТЬ

### 1. Найти текущий вызов LLM
Ищем код типа:
```python
response = litellm.completion(
    model=f"openrouter/{model_id}",
    messages=messages,
    # Возможно другие параметры
)
```

### 2. Найти обработку ответа
Ищем код типа:
```python
response_text = response.choices[0].message.content
# Далее идет парсинг текста (который мы удалили в Task 1.1)
```

## 🛠️ НОВАЯ АРХИТЕКТУРА

### Схема работы нативного Tool Calling:
```
1. Отправляем запрос с tools → LLM
2. LLM возвращает либо текст, либо tool_calls
3. Если tool_calls:
   a. Выполняем каждый инструмент
   b. Добавляем результаты в историю
   c. Делаем второй запрос для финального ответа
4. Возвращаем финальный текст пользователю
```

## 📝 НОВЫЙ КОД

### 1. Импорты в начале файла:
```python
import json
from typing import List, Dict, Any, Optional
from tool_definitions import get_tool_schema
```

### 2. Новая функция `_call_llm_with_tools`:
```python
def _call_llm_with_tools(
    self, 
    messages: List[Dict], 
    model_id: str,
    max_tool_iterations: int = 3
) -> Dict[str, Any]:
    """
    Вызов LLM с поддержкой нативного Tool Calling
    
    Args:
        messages: История сообщений
        model_id: ID модели (например, "deepseek/deepseek-chat")
        max_tool_iterations: Максимальное количество итераций инструментов
        
    Returns:
        Dict с результатом: {"text": str, "tools_used": List, "error": str}
    """
    
    # Получаем схему инструментов
    tools = get_tool_schema()
    tools_used = []
    
    try:
        # Основной цикл обработки
        for iteration in range(max_tool_iterations):
            
            # 1. Вызов LLM с инструментами
            response = litellm.completion(
                model=f"openrouter/{model_id}",
                messages=messages,
                tools=tools,
                tool_choice="auto",  # LLM сама решает, нужны ли инструменты
                temperature=0.7,
                max_tokens=4000
            )
            
            response_message = response.choices[0].message
            
            # 2. Проверяем, хочет ли LLM использовать инструменты
            if not response_message.tool_calls:
                # Нет инструментов - возвращаем текстовый ответ
                return {
                    "text": response_message.content or "",
                    "tools_used": tools_used,
                    "error": None
                }
            
            # 3. LLM хочет использовать инструменты
            # Добавляем сообщение LLM в историю
            messages.append(response_message)
            
            # 4. Выполняем каждый запрошенный инструмент
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    # Если LLM вернула невалидный JSON
                    error_msg = f"Ошибка парсинга аргументов инструмента: {e}"
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool", 
                        "name": function_name,
                        "content": f"ОШИБКА: {error_msg}"
                    })
                    continue
                
                # 5. Вызываем реальный инструмент через CommandExecutor
                tool_result = self._execute_tool(function_name, function_args)
                
                # 6. Добавляем результат в историю
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name, 
                    "content": str(tool_result)
                })
                
                # Запоминаем использованный инструмент
                tools_used.append({
                    "name": function_name,
                    "args": function_args,
                    "result": tool_result
                })
            
            # 7. Продолжаем цикл для получения финального ответа
            
        # Если достигли максимума итераций
        return {
            "text": "Достигнуто максимальное количество вызовов инструментов",
            "tools_used": tools_used,
            "error": "max_iterations_reached"
        }
        
    except Exception as e:
        logger.error(f"Ошибка в _call_llm_with_tools: {e}", exc_info=True)
        return {
            "text": "",
            "tools_used": tools_used,
            "error": str(e)
        }
```

### 3. Функция выполнения инструментов:
```python
def _execute_tool(self, function_name: str, function_args: Dict) -> str:
    """
    Выполняет конкретный инструмент по имени
    
    Args:
        function_name: Имя функции (execute_terminal_command, browse_website, etc.)
        function_args: Аргументы функции
        
    Returns:
        str: Результат выполнения инструмента
    """
    
    try:
        # Получаем CommandExecutor (или создаем, если нет)
        if not hasattr(self, 'command_executor'):
            from command_executor import CommandExecutor
            self.command_executor = CommandExecutor()
        
        # Маппинг имен функций на методы CommandExecutor
        if function_name == "execute_terminal_command":
            command = function_args.get("command", "")
            return self.command_executor.execute_terminal_command(command)
            
        elif function_name == "browse_website":
            url = function_args.get("url", "")
            return self.command_executor.browse_website(url)
            
        elif function_name == "web_search":
            query = function_args.get("query", "")
            num_results = function_args.get("num_results", 5)
            return self.command_executor.web_search(query, num_results)
            
        elif function_name == "file_operations":
            operation = function_args.get("operation", "")
            path = function_args.get("path", "")
            content = function_args.get("content", "")
            return self.command_executor.file_operations(operation, path, content)
            
        else:
            return f"ОШИБКА: Неизвестный инструмент '{function_name}'"
            
    except Exception as e:
        logger.error(f"Ошибка выполнения инструмента {function_name}: {e}")
        return f"ОШИБКА: {str(e)}"
```

### 4. Обновить основную функцию обработки запросов:
```python
def process_request(self, user_message: str, model_id: str = None) -> Dict:
    """
    Основная функция обработки запроса пользователя
    """
    
    # Подготавливаем сообщения
    messages = [
        {"role": "system", "content": self.get_system_prompt()},
        {"role": "user", "content": user_message}
    ]
    
    # Вызываем LLM с поддержкой инструментов
    result = self._call_llm_with_tools(messages, model_id or self.default_model)
    
    # Формируем ответ для API
    if result["error"]:
        return {
            "status": "error",
            "message": result["error"],
            "response": result["text"]
        }
    else:
        return {
            "status": "success", 
            "response": result["text"],
            "tools_used": result["tools_used"],
            "has_commands": len(result["tools_used"]) > 0
        }
```

## 🧪 ТЕСТИРОВАНИЕ

### 1. Тест без инструментов:
```python
def test_simple_text_response():
    delegator = SmartDelegator()
    result = delegator.process_request("Привет, как дела?")
    
    assert result["status"] == "success"
    assert len(result["response"]) > 0
    assert result["tools_used"] == []
```

### 2. Тест с инструментами:
```python
def test_tool_calling():
    delegator = SmartDelegator()
    result = delegator.process_request("Покажи содержимое текущей папки")
    
    assert result["status"] == "success"
    assert result["has_commands"] == True
    assert len(result["tools_used"]) > 0
    assert result["tools_used"][0]["name"] == "execute_terminal_command"
```

### 3. Тест обработки ошибок:
```python
def test_invalid_tool_args():
    # Тест с невалидными аргументами инструмента
    # Должен обрабатываться gracefully
    pass
```

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: Модель не поддерживает Tool Calling
**Решение:** Добавить fallback к старому методу для старых моделей
```python
if not self._model_supports_tools(model_id):
    return self._call_llm_legacy(messages, model_id)
```

### Проблема 2: Бесконечный цикл вызовов инструментов
**Решение:** Ограничение `max_tool_iterations = 3`

### Проблема 3: CommandExecutor не существует или изменился интерфейс
**Решение:** Создать адаптер или обновить интерфейс

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] Найдена и изучена текущая функция `_call_llm`
- [ ] Добавлен импорт `get_tool_schema`
- [ ] Реализована `_call_llm_with_tools`
- [ ] Реализована `_execute_tool` с маппингом функций
- [ ] Обновлена основная функция `process_request`
- [ ] Добавлена обработка ошибок JSON парсинга
- [ ] Добавлено ограничение на количество итераций
- [ ] Написаны базовые тесты
- [ ] Протестирован простой запрос без инструментов
- [ ] Протестирован запрос с инструментами

## 🎯 РЕЗУЛЬТАТ

После выполнения этой задачи:
1. ✅ LLM использует нативный Tool Calling вместо парсинга текста
2. ✅ Инструменты вызываются через стандартный интерфейс OpenAI
3. ✅ Реализован двухэтапный процесс: инструмент → финальный ответ
4. ✅ Добавлена защита от бесконечных циклов и ошибок

**Время выполнения:** 3-4 часа  
**Сложность:** Высокая  
**Критичность:** 🔴 Максимальная

---

## 🚀 СЛЕДУЮЩИЙ ШАГ: TASK 1.4
После переписывания вызова LLM переходим к обновлению CommandExecutor для работы с новым интерфейсом.