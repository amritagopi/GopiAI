# API Клиент GopiAI

Этот модуль предоставляет выделенный API клиент для коммуникации между фронтенд UI и бэкенд сервером GopiAI. Клиент обеспечивает чистое разделение между компонентами и надежную обработку ошибок.

## Основные возможности

- ✅ Отправка сообщений в чат через HTTP API
- ✅ Получение списка доступных моделей
- ✅ Проверка состояния бэкенд сервера
- ✅ Обработка ошибок соединения и повторные попытки
- ✅ Таймауты запросов и пулинг соединений
- ✅ Экспоненциальная задержка при повторных попытках
- ✅ Стандартизированные ответы об ошибках

## Быстрый старт

### Базовое использование

```python
from gopiai.ui.api import GopiAIAPIClient

# Создание клиента
client = GopiAIAPIClient(base_url="http://localhost:5051")

# Отправка сообщения
result = client.send_message("Привет, как дела?", model_id="deepseek/deepseek-chat")

if result["status"] == "success":
    print(f"Ответ: {result['response']}")
    print(f"Использованы инструменты: {result.get('tools_used', [])}")
else:
    print(f"Ошибка: {result['message']}")

# Получение списка моделей
models = client.get_available_models()
for model in models:
    print(f"Модель: {model['id']} - {model['name']}")

# Проверка состояния сервера
if client.health_check():
    print("Сервер доступен")
else:
    print("Сервер недоступен")

# Закрытие клиента
client.close()
```

### Использование как контекстного менеджера

```python
from gopiai.ui.api import GopiAIAPIClient

with GopiAIAPIClient() as client:
    result = client.send_message("Тестовое сообщение")
    print(result)
# Клиент автоматически закрывается при выходе из контекста
```

### Глобальный клиент

```python
from gopiai.ui.api import get_default_client, set_default_client

# Использование глобального клиента
client = get_default_client()
result = client.send_message("Сообщение")

# Установка кастомного глобального клиента
custom_client = GopiAIAPIClient(base_url="http://custom-server:8080")
set_default_client(custom_client)
```

## API Методы

### `send_message(message, model_id=None, session_id=None)`

Отправляет сообщение в чат для обработки бэкендом.

**Параметры:**
- `message` (str): Текст сообщения пользователя
- `model_id` (str, опционально): ID модели для использования
- `session_id` (str, опционально): ID сессии для контекста

**Возвращает:**
```python
{
    "status": "success",
    "response": "Ответ от AI",
    "tools_used": [
        {
            "name": "execute_terminal_command",
            "args": {"command": "ls -la"},
            "result": "список файлов..."
        }
    ],
    "execution_time": 2.34,
    "model_info": {
        "model_id": "deepseek/deepseek-chat",
        "provider": "openrouter"
    }
}
```

**При ошибке:**
```python
{
    "status": "error",
    "error_code": "CONNECTION_ERROR",
    "message": "Не удается подключиться к серверу...",
    "timestamp": 1640995200.0
}
```

### `get_available_models()`

Получает список доступных моделей от бэкенда.

**Возвращает:**
```python
[
    {
        "id": "deepseek/deepseek-chat",
        "name": "DeepSeek Chat",
        "provider": "openrouter",
        "context_length": 32768
    },
    {
        "id": "anthropic/claude-3-sonnet",
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "context_length": 200000
    }
]
```

### `health_check()`

Проверяет состояние бэкенд сервера.

**Возвращает:**
- `True` если сервер доступен и здоров
- `False` если сервер недоступен или нездоров

## Обработка ошибок

Клиент автоматически обрабатывает различные типы ошибок:

### Коды ошибок

- `CONNECTION_ERROR`: Не удается подключиться к серверу
- `TIMEOUT_ERROR`: Запрос превысил лимит времени
- `API_ERROR`: HTTP ошибка от сервера (4xx, 5xx)
- `JSON_ERROR`: Некорректный JSON ответ от сервера
- `REQUEST_ERROR`: Общая ошибка запроса
- `UNKNOWN_ERROR`: Неожиданная ошибка

### Повторные попытки

Клиент автоматически повторяет запросы при:
- HTTP статусах: 429, 500, 502, 503, 504
- Экспоненциальная задержка между попытками
- Максимум 3 попытки для каждого запроса

## Интеграция с UI компонентами

### Использование в Qt виджетах

```python
from PySide6.QtCore import QThread, Signal
from gopiai.ui.api import get_default_client

class ChatWorker(QThread):
    message_received = Signal(dict)
    error_occurred = Signal(str, str)
    
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.client = get_default_client()
    
    def run(self):
        result = self.client.send_message(self.message)
        
        if result["status"] == "success":
            self.message_received.emit(result)
        else:
            self.error_occurred.emit(
                result["error_code"], 
                result["message"]
            )

# В UI компоненте
worker = ChatWorker("Привет!")
worker.message_received.connect(self.on_message_received)
worker.error_occurred.connect(self.on_error)
worker.start()
```

### Мониторинг состояния сервера

```python
from PySide6.QtCore import QTimer
from gopiai.ui.api import get_default_client

class ServerMonitor:
    def __init__(self):
        self.client = get_default_client()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_health)
        self.timer.start(30000)  # Проверка каждые 30 секунд
    
    def check_health(self):
        if self.client.health_check():
            print("Сервер доступен")
        else:
            print("Сервер недоступен")
```

## Конфигурация

### Параметры инициализации

```python
client = GopiAIAPIClient(
    base_url="http://localhost:5051",  # URL бэкенд сервера
    timeout=30  # Таймаут запросов в секундах
)
```

### Настройка пула соединений

Клиент автоматически настраивает пул соединений:
- 10 пулов соединений
- Максимум 20 соединений в пуле
- Повторное использование соединений

### Настройка повторных попыток

```python
# Настройки встроены в клиент:
# - 3 попытки максимум
# - Экспоненциальная задержка
# - Повтор для статусов 429, 5xx
```

## Логирование

Клиент использует стандартное Python логирование:

```python
import logging

# Включение debug логов для API клиента
logging.getLogger('gopiai.ui.api.client').setLevel(logging.DEBUG)

# Создание обработчика для вывода в консоль
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger('gopiai.ui.api.client')
logger.addHandler(handler)
```

## Тестирование

Запуск тестов:

```bash
# Все тесты API клиента
python -m pytest tests/test_api_client.py -v

# Конкретный тест
python -m pytest tests/test_api_client.py::TestGopiAIAPIClient::test_send_message_success -v
```

## Примеры использования

См. файл `integration_example.py` для подробных примеров интеграции с различными компонентами UI, включая:

- Асинхронная отправка сообщений в отдельном потоке
- Мониторинг состояния сервера
- Кэширование списка моделей
- Отображение ошибок пользователю
- Полный пример виджета чата

## Требования

- Python 3.8+
- requests >= 2.25.0
- PySide6 (для UI интеграции)
- pytest (для тестирования)

## Безопасность

- Все запросы используют HTTPS когда возможно
- Таймауты предотвращают зависание запросов
- Валидация входных данных
- Безопасная обработка ошибок без утечки информации