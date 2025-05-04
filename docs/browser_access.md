# Модуль BrowserAccess для GopiAI

## Обзор

BrowserAccess — это модуль для безопасного выполнения действий в браузере в рамках Reasoning Agent. Модуль обеспечивает контролируемый доступ к браузеру с проверкой безопасности действий и ограничением потенциально опасных операций.

## Принцип работы

Модуль работает по следующим принципам:

1. **Проверка безопасности URL** — анализ URL на наличие потенциально опасных протоколов и паттернов
2. **Проверка безопасности действий** — анализ браузерных действий на наличие потенциально опасных операций
3. **Контроль выполнения действий** — обеспечение атомарности и корректности выполнения действий
4. **Логирование действий** — запись всех выполненных действий и их результатов
5. **Изоляция окружения** — предотвращение нежелательного воздействия на систему

## Основные возможности

### Безопасное выполнение действий в браузере

```python
result = await browser_access.execute_action(
    action="go_to_url",
    url="https://www.python.org"
)
```

### Получение текущего состояния браузера

```python
state = await browser_access.get_current_state()
if state["success"]:
    print(f"Текущий URL: {state['state'].get('current_url')}")
    print(f"Содержимое страницы: {state['state'].get('content')}")
```

### Получение истории действий

```python
history = browser_access.get_action_history()
for entry in history:
    print(f"Действие: {entry['action']}")
    print(f"Параметры: {entry['params']}")
    print(f"Успех: {entry.get('success', False)}")
```

## Меры безопасности

### Блокировка опасных URL

Модуль блокирует переход на URL с потенциально опасными протоколами:

```python
UNSAFE_URL_PATTERNS = [
    "file://",  # Локальные файлы
    "chrome://",  # Внутренние страницы Chrome
    "about:",  # Внутренние страницы браузера
    "data:",  # Data URLs (могут содержать JavaScript)
    "javascript:",  # JavaScript URLs
    "view-source:",  # Просмотр исходного кода
    "ftp://",  # FTP протокол (устаревший и потенциально небезопасный)
]
```

### Блокировка опасных действий

Модуль ограничивает выполнение потенциально опасных действий:

```python
UNSAFE_ACTIONS = [
    "execute_script",  # Произвольное выполнение JavaScript
    "raw_input",       # Прямой ввод без фильтрации
    "file_upload"      # Загрузка файлов
]
```

### Дополнительные проверки

- Проверка содержимого URL на наличие JavaScript
- Проверка вводимого текста на потенциально опасные паттерны
- Ограничение количества открываемых вкладок

## Интеграция с ReasoningAgent

Модуль BrowserAccess интегрирован в ReasoningAgent и автоматически используется для перехвата вызовов инструмента `browser_use`:

```python
# Внутри ReasoningAgent
if name == "browser_use" and self.browser_access:
    action = kwargs.get("action", "")

    # Удаляем action из kwargs для передачи остальных параметров
    action_params = kwargs.copy()
    if "action" in action_params:
        del action_params["action"]

    # Выполняем действие через наш безопасный BrowserAccess
    result = await self.browser_access.execute_action(action, **action_params)

    # Формируем ответ в формате ToolResult
    return {
        "output": result.get("output", ""),
        "error": result.get("error", ""),
    }
```

## Результаты выполнения действий

Функция `execute_action` возвращает словарь со следующими полями:

```python
{
    "success": bool,   # Успешность выполнения
    "output": str,     # Результат выполнения
    "error": str,      # Ошибка (если есть)
    "action": str,     # Выполненное действие
    "params": dict     # Параметры действия
}
```

## Возможные ошибки

1. **SafetyViolation** — попытка выполнения небезопасного действия
2. **UnsafeURL** — попытка перехода на небезопасный URL
3. **BrowserInitializationError** — ошибка инициализации браузера
4. **ActionExecutionError** — ошибка выполнения действия
5. **PlanNotApproved** — план не был одобрен для выполнения действий

## Пример использования

```python
from app.agent.browser_access import BrowserAccess

# Создание экземпляра
browser = BrowserAccess(
    safe_mode=True,
    headless=False,
    max_tabs=5
)

# Переход на веб-страницу
result = await browser.execute_action("go_to_url", url="https://www.python.org")
if result["success"]:
    print("Страница успешно загружена")
else:
    print(f"Ошибка загрузки страницы: {result['error']}")

# Прокрутка страницы
await browser.execute_action("scroll_down", scroll_amount=500)

# Получение состояния браузера
state = await browser.get_current_state()
if state["success"]:
    print(f"Заголовок страницы: {state['state'].get('title')}")

# Освобождение ресурсов
await browser.cleanup()
```

## Тестирование

Для тестирования модуля используйте скрипт `tests/test_browser_access.py`:

```bash
python tests/test_browser_access.py
```

Возможные параметры тестирования:

- `--test safe` — тестирование безопасной навигации
- `--test unsafe` — тестирование отклонения опасных URL и действий
- `--test actions` — тестирование различных браузерных действий
- `--test state` — тестирование получения состояния браузера
- `--test all` — запуск всех тестов (по умолчанию)
- `--headless` — запуск браузера в режиме без интерфейса
- `--safe-mode` — включение/выключение режима безопасности
