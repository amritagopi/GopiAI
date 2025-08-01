# 🛡️ TASK 2.1: ДОБАВИТЬ ОБРАБОТКУ ОШИБОК LLM

## 🎯 ЦЕЛЬ
Добавить полноценную обработку ошибок при вызове LLM через litellm, чтобы приложение не падало молча и возвращало осмысленные сообщения об ошибках вместо пустых ответов.

## 📁 ЦЕЛЕВЫЕ ФАЙЛЫ
- `GopiAI-CrewAI/tools/gopiai_integration/smart_delegator.py`
- Функция `_call_llm_with_tools` (из Task 1.3)
- Возможно другие места вызова `litellm.completion()`

## 🚨 ТЕКУЩИЕ ПРОБЛЕМЫ

Из логов видны следующие ошибки:
1. **RateLimitError** - превышение лимитов запросов
2. **AuthenticationError** - проблемы с API ключами
3. **Exception has no attribute 'request'** - внутренние ошибки litellm
4. **Пустые ответы** - когда LLM не возвращает контент
5. **Таймауты** - долгие запросы

## 🛠️ ТИПЫ ОШИБОК И ИХ ОБРАБОТКА

### 1. Импорты для обработки ошибок:
```python
import litellm
from litellm.exceptions import (
    RateLimitError,
    AuthenticationError, 
    InvalidRequestError,
    APIError,
    Timeout,
    APIConnectionError
)
import time
from functools import wraps
```

### 2. Декоратор для retry логики:
```python
def retry_on_rate_limit(max_retries: int = 3, base_delay: float = 60.0):
    """
    Декоратор для повторных попыток при rate limit
    
    Args:
        max_retries: Максимальное количество попыток
        base_delay: Базовая задержка в секундах
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Экспоненциальная задержка
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                        continue
                    else:
                        # Исчерпаны попытки
                        break
                        
                except (AuthenticationError, InvalidRequestError) as e:
                    # Эти ошибки не стоит повторять
                    last_exception = e
                    break
                    
                except Exception as e:
                    # Другие ошибки - пробуем еще раз
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay, 30.0)  # Максимум 30 сек для других ошибок
                        logger.warning(f"LLM error, retrying in {delay}s: {str(e)}")
                        time.sleep(delay)
                        continue
                    else:
                        break
            
            # Если дошли сюда - все попытки исчерпаны
            raise last_exception
            
        return wrapper
    return decorator
```

### 3. Обновленная функция вызова LLM:
```python
@retry_on_rate_limit(max_retries=2, base_delay=60.0)
def _call_llm_with_tools(
    self, 
    messages: List[Dict], 
    model_id: str,
    max_tool_iterations: int = 3
) -> Dict[str, Any]:
    """
    Вызов LLM с полной обработкой ошибок
    """
    
    tools = get_tool_schema()
    tools_used = []
    
    try:
        # Основной цикл обработки
        for iteration in range(max_tool_iterations):
            
            try:
                # 1. Вызов LLM с инструментами
                response = litellm.completion(
                    model=f"openrouter/{model_id}",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=4000,
                    timeout=60  # Таймаут 60 секунд
                )
                
                # 2. Проверяем валидность ответа
                if not response or not response.choices:
                    return {
                        "text": "",
                        "tools_used": tools_used,
                        "error": "LLM вернул пустой ответ"
                    }
                
                response_message = response.choices[0].message
                
                # 3. Проверяем содержимое сообщения
                if not response_message:
                    return {
                        "text": "",
                        "tools_used": tools_used,
                        "error": "LLM вернул пустое сообщение"
                    }
                
                # 4. Обрабатываем tool_calls или текстовый ответ
                if not response_message.tool_calls:
                    # Текстовый ответ
                    content = response_message.content or ""
                    if not content.strip():
                        return {
                            "text": "LLM не предоставил ответ",
                            "tools_used": tools_used,
                            "error": "empty_content"
                        }
                    
                    return {
                        "text": content,
                        "tools_used": tools_used,
                        "error": None
                    }
                
                # 5. Обработка tool_calls (как в Task 1.3)
                messages.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        error_msg = f"Ошибка парсинга аргументов инструмента {function_name}: {e}"
                        logger.error(error_msg)
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"ОШИБКА: {error_msg}"
                        })
                        continue
                    
                    # Выполняем инструмент
                    try:
                        tool_result = self._execute_tool(function_name, function_args)
                    except Exception as tool_error:
                        tool_result = f"ОШИБКА выполнения инструмента: {str(tool_error)}"
                        logger.error(f"Tool execution error for {function_name}: {tool_error}")
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_result)
                    })
                    
                    tools_used.append({
                        "name": function_name,
                        "args": function_args,
                        "result": tool_result
                    })
                
                # Продолжаем цикл для финального ответа
                
            except RateLimitError as e:
                # Обрабатывается декоратором retry
                raise e
                
            except AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Ошибка аутентификации: Проверьте API ключ для модели {model_id}"
                }
                
            except InvalidRequestError as e:
                logger.error(f"Invalid request error: {e}")
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Некорректный запрос к модели {model_id}: {str(e)}"
                }
                
            except Timeout as e:
                logger.error(f"Timeout error: {e}")
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Таймаут при обращении к модели {model_id}. Попробуйте позже."
                }
                
            except APIConnectionError as e:
                logger.error(f"API connection error: {e}")
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Ошибка соединения с API {model_id}. Проверьте интернет-подключение."
                }
                
            except APIError as e:
                logger.error(f"API error: {e}")
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Ошибка API {model_id}: {str(e)}"
                }
                
            except Exception as e:
                logger.error(f"Unexpected error in LLM call: {e}", exc_info=True)
                return {
                    "text": "",
                    "tools_used": tools_used,
                    "error": f"Неожиданная ошибка: {str(e)}"
                }
        
        # Достигнуто максимальное количество итераций
        return {
            "text": "Достигнуто максимальное количество вызовов инструментов",
            "tools_used": tools_used,
            "error": "max_iterations_reached"
        }
        
    except RateLimitError as e:
        logger.error(f"Rate limit exceeded after retries: {e}")
        return {
            "text": "",
            "tools_used": tools_used,
            "error": f"Превышен лимит запросов к модели {model_id}. Попробуйте позже или выберите другую модель."
        }
        
    except Exception as e:
        logger.error(f"Fatal error in _call_llm_with_tools: {e}", exc_info=True)
        return {
            "text": "",
            "tools_used": tools_used,
            "error": f"Критическая ошибка при обращении к LLM: {str(e)}"
        }
```

### 4. Обновить основную функцию process_request:
```python
def process_request(self, user_message: str, model_id: str = None) -> Dict:
    """
    Основная функция с улучшенной обработкой ошибок
    """
    
    try:
        # Валидация входных данных
        if not user_message or not user_message.strip():
            return {
                "status": "error",
                "message": "Пустое сообщение пользователя",
                "response": ""
            }
        
        if not model_id:
            model_id = self.default_model
            
        # Подготавливаем сообщения
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message.strip()}
        ]
        
        # Вызываем LLM
        result = self._call_llm_with_tools(messages, model_id)
        
        # Обрабатываем результат
        if result["error"]:
            # Логируем ошибку для отладки
            logger.error(f"LLM request failed: {result['error']}")
            
            # Возвращаем пользователю понятную ошибку
            return {
                "status": "error",
                "message": result["error"],
                "response": result["text"] or "Не удалось получить ответ от LLM",
                "tools_used": result["tools_used"]
            }
        else:
            return {
                "status": "success",
                "response": result["text"],
                "tools_used": result["tools_used"],
                "has_commands": len(result["tools_used"]) > 0
            }
            
    except Exception as e:
        logger.error(f"Fatal error in process_request: {e}", exc_info=True)
        return {
            "status": "error", 
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "response": "Произошла неожиданная ошибка при обработке запроса"
        }
```

## 📊 МОНИТОРИНГ И ЛОГИРОВАНИЕ

### Добавить детальное логирование:
```python
def _log_llm_metrics(self, model_id: str, start_time: float, success: bool, error: str = None):
    """Логирование метрик вызовов LLM"""
    
    duration = time.time() - start_time
    
    if success:
        logger.info(f"LLM call successful: model={model_id}, duration={duration:.2f}s")
    else:
        logger.error(f"LLM call failed: model={model_id}, duration={duration:.2f}s, error={error}")
    
    # Можно добавить отправку метрик в систему мониторинга
```

## 🧪 ТЕСТИРОВАНИЕ

### 1. Тест обработки rate limit:
```python
def test_rate_limit_handling():
    # Мокаем RateLimitError
    with patch('litellm.completion') as mock_completion:
        mock_completion.side_effect = RateLimitError("Rate limit exceeded")
        
        delegator = SmartDelegator()
        result = delegator.process_request("test message")
        
        assert result["status"] == "error"
        assert "лимит запросов" in result["message"]
```

### 2. Тест обработки пустых ответов:
```python
def test_empty_response_handling():
    with patch('litellm.completion') as mock_completion:
        # Мокаем пустой ответ
        mock_response = Mock()
        mock_response.choices = []
        mock_completion.return_value = mock_response
        
        delegator = SmartDelegator()
        result = delegator.process_request("test message")
        
        assert result["status"] == "error"
        assert "пустой ответ" in result["message"]
```

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] Добавлены импорты для всех типов ошибок litellm
- [ ] Реализован декоратор retry для rate limit
- [ ] Добавлена обработка всех основных типов ошибок
- [ ] Обновлена функция `_call_llm_with_tools`
- [ ] Обновлена функция `process_request`
- [ ] Добавлена валидация входных данных
- [ ] Добавлено детальное логирование ошибок
- [ ] Написаны тесты для основных сценариев ошибок
- [ ] Проверена работа retry механизма

## 🎯 РЕЗУЛЬТАТ

После выполнения этой задачи:
1. ✅ Приложение не падает при ошибках LLM
2. ✅ Пользователи получают понятные сообщения об ошибках
3. ✅ Автоматические повторы при rate limit
4. ✅ Подробное логирование для отладки
5. ✅ Graceful degradation при любых сбоях

**Время выполнения:** 1-2 часа  
**Сложность:** Средняя  
**Критичность:** 🟡 Важная

---

## 🚀 СЛЕДУЮЩИЙ ШАГ: TASK 2.2
После стабилизации LLM переходим к исправлению крашей при создании вкладок в UI.