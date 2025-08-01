### 1. Критическая ошибка: `ImportError` при запуске UI

Это самая главная проблема, из-за которой не работает часть логики, связанной с моделями. Она проявляется в двух вариантах:

**Вариант А (в 12:29:03):**
```log
gopiai.ui.components.crewai_client - ERROR - [INIT] Ошибка импорта модулей emotional_classifier/ai_router_llm: cannot import name 'get_active_models' from 'llm_rotation_config' (c:\...\GopiAI-CrewAI\llm_rotation_config.py)
```
**Вариант Б (в 12:52:28 и позже):**
```log
gopiai.ui.components.crewai_client - ERROR - [INIT] Ошибка импорта модулей emotional_classifier/ai_router_llm: No module named 'llm_rotation_config'
```

**Анализ:**
Это классическая проблема архитектуры и путей Python (`sys.path`) в сложном проекте.

1.  **Что происходит:** Твой UI-компонент `gopiai.ui.components.crewai_client` (который является *клиентом*) пытается напрямую импортировать `llm_rotation_config` — файл, который является частью *серверной* логики и лежит в проекте `GopiAI-CrewAI`.
2.  **Почему это плохо:** Клиент и сервер должны общаться только через API (HTTP-запросы). Клиент не должен ничего знать о внутренней "кухне" сервера, такой как файлы конфигурации ротации моделей. Когда ты пытаешься импортировать серверный код в клиенте, начинаются проблемы с путями, потому что проекты запускаются из разных мест и имеют разные зависимости.
3.  **Разница между ошибками:**
    *   **Ошибка А (`cannot import name`)** говорит, что Python *нашел* файл `llm_rotation_config.py`, но не смог найти внутри него функцию `get_active_models`. Возможно, из-за того, что ты ее удалил/переименовал, или из-за циклического импорта.
    *   **Ошибка Б (`No module named`)** еще хуже. Она говорит, что Python теперь даже *не может найти* файл `llm_rotation_config.py`. Вероятно, ты переместил файл или изменил `sys.path` в попытке исправить первую ошибку.

**Как исправить (глобальное решение):**

Тебе нужно четко разделить клиент и сервер. UI не должен импортировать `llm_rotation_config`.

**Шаг 1: Создай API-эндпоинт на сервере (в GopiAI-CrewAI)**
Твой UI, вероятно, хочет получить список активных моделей для отображения в интерфейсе. Сделай для этого специальный эндпоинт на Flask-сервере.

*   В файле `crewai_api_server.py` (или где у тебя роуты Flask) добавь что-то вроде этого:

```python
# crewai_api_server.py

# Импортируй свою функцию из локального конфига
from llm_rotation_config import get_active_models, get_providers 

@app.route('/api/config/models', methods=['GET'])
def get_model_config():
    """
    Возвращает список активных моделей и провайдеров для UI.
    """
    try:
        # Получаем данные с помощью твоих функций
        active_models = get_active_models() # Пример
        providers = get_providers() # Пример

        config_data = {
            "providers": providers,
            "active_models": active_models
        }
        return jsonify(config_data)
    except Exception as e:
        # Важно! Логируем ошибку на сервере
        logging.error(f"Error getting model config: {e}")
        return jsonify({"error": "Failed to load model configuration"}), 500

```

**Шаг 2: Удали некорректный импорт из UI-клиента**
В файле `gopiai/ui/components/crewai_client.py` найди и полностью удали строку:
```python
# УДАЛИТЬ ЭТО
from llm_rotation_config import get_active_models 
```

**Шаг 3: Загружай конфигурацию в UI через HTTP-запрос**
Теперь в `crewai_client.py` при инициализации обращайся к новому API-эндпоинту, чтобы получить нужные данные.

```python
# gopiai/ui/components/crewai_client.py
import requests
import logging

class CrewAIClient:
    def __init__(self, base_url="http://127.0.0.1:5051"):
        self.base_url = base_url
        self.emotional_classifier = None
        self.tools_instruction_manager = None
        
        # Загружаем конфигурацию с сервера
        self.config = self._load_config_from_server()

        # Теперь инициализируем все остальное, используя self.config
        try:
            # Тут твоя логика импортов, которая ломалась
            from gopiai_integration.emotional_classifier import EmotionalClassifier
            from gopiai_integration.ai_router_llm import AIRouterLLM
            
            # Если ai_router_llm нужен список моделей, передай его из self.config
            # Вместо того чтобы он импортировал его сам!
            ai_router = AIRouterLLM(active_models=self.config.get('active_models', {}))
            self.emotional_classifier = EmotionalClassifier(ai_router)
            logging.info("[INIT] ✅ Эмоциональный классификатор инициализирован с AI Router")
        except ImportError as e:
            # Эта ошибка теперь будет указывать на реальные проблемы, а не на пути
            logging.error(f"[INIT] Ошибка импорта модулей: {e}")

    def _load_config_from_server(self):
        """Загружает конфигурацию моделей с бэкенд-сервера."""
        try:
            response = requests.get(f"{self.base_url}/api/config/models")
            response.raise_for_status() # Вызовет исключение для кодов 4xx/5xx
            logging.info("[INIT] ✅ Конфигурация моделей успешно загружена с сервера.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"[INIT] ❌ Не удалось загрузить конфигурацию моделей с сервера: {e}")
            return {"error": str(e)} # Возвращаем пустой конфиг или ошибку
```
Это правильный архитектурный подход. Он полностью разделяет клиент и сервер, решает все проблемы с импортами и делает систему гораздо стабильнее.

---

### 2. Мелкие предупреждения (остались с прошлого раза)

Эти проблемы всё ещё присутствуют в логах, и их стоит исправить для "гигиены" проекта.

*   **Искаженная кодировка:** `ToolsInstructionManager ���������������`
    *   **Решение:** Настрой логгер на использование `encoding='utf-8'`.

*   **Нет прав на запись лога:** `[Errno 13] Permission denied: '...\\crewai_api_server_debug.log'`
    *   **Решение:** Запускай сервер от имени администратора или измени путь для логов на папку, куда у пользователя есть права на запись (например, `C:\Users\crazy\Documents\GopiAI_Logs`).

### Резюме и план действий:

1.  **Главный приоритет:** Реализуй архитектурное разделение клиента и сервера.
    *   Создай API-эндпоинт (`/api/config/models`) на Flask-сервере для получения конфигурации моделей.
    *   Удали прямые импорты серверных конфигов из UI-кода (`gopiai.ui.components.crewai_client`).
    *   Загружай конфигурацию в UI через HTTP-запрос при старте приложения.
2.  **После исправления импортов:** Проверь и исправь идентификаторы моделей для OpenRouter.
3.  **Второстепенные задачи:** Исправь проблему с кодировкой и правами на запись лог-файлов.
