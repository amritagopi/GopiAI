import os
import time
import threading
# Конфиг моделей Gemini/Gemma для ротации и задач
LLM_MODELS_CONFIG = [
    {
        "name": "Gemini 1.5 Flash",
        "id": "gemini/gemini-1.5-flash",
        "provider": "google",
        "rpm": 15,  
        "tpm": 250000,  
        "type": ["simple", "dialog", "code", "summarize"],
        "multimodal": False,
        "embedding": False,
        "priority": 3,
        "rpd": 50,  
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemini 2.0 Flash-Lite",
        "id": "gemini/gemini-2.0-flash-lite",
        "provider": "google",
        "rpm": 30,
        "tpm": 1000000,  
        "type": ["simple", "dialog", "code", "summarize"],
        "multimodal": False,
        "embedding": False,
        "priority": 4,
        "rpd": 200,  
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemma 3",
        "id": "gemini/gemma-3",
        "provider": "google",
        "rpm": 30,  
        "tpm": 14400,  
        "type": ["simple", "lookup", "short_answer"],
        "multimodal": False,
        "embedding": False,
        "priority": 1,
        "rpd": 0,
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemma 3n",
        "id": "gemini/gemma-3n",
        "provider": "google",
        "rpm": 30,  
        "tpm": 14400,  
        "type": ["simple", "lookup", "short_answer"],
        "multimodal": False,
        "embedding": False,
        "priority": 2,
        "rpd": 0,
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemini 2.5 Flash-Lite Preview",
        "id": "gemini/gemini-2.5-flash-lite-preview",
        "provider": "google",
        "rpm": 15,
        "tpm": 60000,
        "type": ["dialog", "code", "summarize"],
        "multimodal": False,
        "embedding": False,
        "priority": 5,
        "rpd": 0,
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemini 2.5 Flash",
        "id": "gemini/gemini-2.5-flash",
        "provider": "google",
        "rpm": 10,
        "tpm": 60000,
        "type": ["dialog", "code", "multimodal", "vision", "long_answer"],
        "multimodal": True,
        "embedding": False,
        "priority": 6,
        "rpd": 0,
        "deprecated": False,
        "base_score": 0.5
    },
    {
        "name": "Gemini Embedding Experimental",
        "id": "gemini/gemini-embedding-experimental",
        "provider": "google",
        "rpm": 5,
        "tpm": 10000,
        "type": ["embedding"],
        "multimodal": False,
        "embedding": True,
        "priority": 10,
        "rpd": 0,
        "deprecated": False,
        "base_score": 0.5
    }
]
print(f"DEBUG: LLM_MODELS_CONFIG loaded: {LLM_MODELS_CONFIG}")
# Helper to get API key based on provider name

def get_api_key_for_provider(provider_name: str):
    """Gets the API key from environment variables for a given provider."""
    print(f"[DEBUG] Getting API key for provider: {provider_name}")
    
    # Check if we're in test environment
    env_test_suffix = "_TEST" if os.getenv("ENVIRONMENT") == "test" else ""
    print(f"[DEBUG] Environment test suffix: '{env_test_suffix}'")
    
    # Map of provider names to their environment variable names
    key_map = {
        "google": "GEMINI_API_KEY"
    }
    print(f"[DEBUG] Key map: {key_map}")
    
    # Get the base environment variable name for the provider
    env_var_base = key_map.get(provider_name.lower())
    print(f"[DEBUG] Environment variable base for {provider_name}: '{env_var_base}'")
    
    if env_var_base is None:
        print(f"[ERROR] No environment variable mapping found for provider: {provider_name}")
        return None
    
    # Construct the full environment variable name
    env_var = env_var_base + env_test_suffix
    print(f"[DEBUG] Full environment variable name: '{env_var}'")
    
    # Get the API key from environment variables
    api_key = os.getenv(env_var)
    
    # Debug output about the API key
    if api_key:
        print(f"[DEBUG] Successfully retrieved API key for {provider_name}")
        print(f"[DEBUG] API key starts with: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
    else:
        print(f"[ERROR] Failed to get API key for {provider_name} from environment variable: {env_var}")
        print(f"[DEBUG] Current environment variables: {[k for k in os.environ if 'GEMINI' in k or 'API' in k]}")
    
    return api_key
# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Улучшенный монитор лимитов с blacklist механизмом
class RateLimitMonitor:
    def __init__(self, models_config):
        self.models = {m["id"]: m for m in models_config}
        self.usage = {
            m["id"]: {
                "rpm": 0, 
                "tpm": 0, 
                "rpd": 0, 
                "last_reset": time.time(), 
                "last_day_reset": time.time()
            } for m in models_config
        }
        
        # 🚨 НОВОЕ: Blacklist для временно недоступных моделей
        self.blacklisted_models = {}  # {model_id: expiry_timestamp}
        self.lock = threading.Lock()
        
        print("[OK] RateLimitMonitor инициализирован с blacklist механизмом")
    def _reset_if_needed(self, model_id):
        now = time.time()
        # Сброс usage каждую минуту
        if now - self.usage[model_id]["last_reset"] > 60:
            self.usage[model_id]["rpm"] = 0
            self.usage[model_id]["tpm"] = 0
            self.usage[model_id]["last_reset"] = now
        
        # Сброс RPD каждые 24 часа
        if now - self.usage[model_id]["last_day_reset"] > 86400:  # 24 часа
            self.usage[model_id]["rpd"] = 0
            self.usage[model_id]["last_day_reset"] = now
    # 🚨 НОВОЕ: Проверка блокировки модели
    def is_model_blocked(self, model_id):
        """Проверяет, заблокирована ли модель временно
        ВНИМАНИЕ: Эта функция должна вызываться только изнутри блокировки self.lock!
        """
        now = time.time()
        if model_id in self.blacklisted_models:
            expiry_time = self.blacklisted_models[model_id]
            if now >= expiry_time:
                # Модель восстановлена, удаляем из blacklist
                del self.blacklisted_models[model_id]
                print(f"✅ Модель {model_id} восстановлена и удалена из blacklist")
                return False
            else:
                remaining_time = int(expiry_time - now)
                print(f"🚫 Модель {model_id} заблокирована еще {remaining_time} секунд")
                return True
        return False

    
    def is_model_blocked_safe(self, model_id):
        """Публичная версия is_model_blocked с собственной блокировкой"""
        with self.lock:
            return self.is_model_blocked(model_id)
    # 🚨 НОВОЕ: Блокировка модели при ошибках API
    def mark_model_unavailable(self, model_id, duration=3600):
        """Помечает модель как недоступную на указанное время (в секундах)"""
        with self.lock:
            expiry_time = time.time() + duration
            self.blacklisted_models[model_id] = expiry_time
            
            # Также искусственно исчерпываем лимиты для двойной защиты
            if model_id in self.models:
                self.usage[model_id]["rpm"] = self.models[model_id]["rpm"]
                self.usage[model_id]["rpd"] = max(self.models[model_id]["rpd"], 1) if self.models[model_id]["rpd"] > 0 else 999
                
            print(f"🚫 Модель {model_id} заблокирована на {duration} секунд до {time.strftime('%H:%M:%S', time.localtime(expiry_time))}")
    # 🚨 ИСПРАВЛЕНО: can_use теперь учитывает blacklist
    def can_use(self, model_id, tokens=0):
        try:
            print(f"[CHECK] Проверка модели {model_id} с {tokens} токенами...")
            
            # Защита от зависания: используем timeout
            with self.lock:
                # Первая проверка: модель в blacklist?
                if self.is_model_blocked(model_id):
                    print(f"[BLOCKED] Модель {model_id} в blacklist")
                    return False
                    
                self._reset_if_needed(model_id)
                model = self.models[model_id]
                usage = self.usage[model_id]
                
                print(f"[STATS] Модель {model_id}: текущее использование RPM={usage['rpm']}/{model['rpm']}, TPM={usage['tpm']}/{model['tpm']}, RPD={usage['rpd']}/{model['rpd']}")
                
                # Проверяем все лимиты: RPM, TPM и RPD
                rpm_ok = usage["rpm"] < model["rpm"]
                tpm_ok = usage["tpm"] + tokens < model["tpm"]
                rpd_ok = model["rpd"] == 0 or usage["rpd"] < model["rpd"]  # Если RPD=0, игнорируем проверку
                
                result = rpm_ok and tpm_ok and rpd_ok
                
                print(f"[OK] Модель {model_id}: RPM_OK={rpm_ok}, TPM_OK={tpm_ok}, RPD_OK={rpd_ok} -> RESULT={result}")
                
                if not result:
                    print(f"[WARNING] Модель {model_id} недоступна: RPM={usage['rpm']}/{model['rpm']}, TPM={usage['tpm']}/{model['tpm']}, RPD={usage['rpd']}/{model['rpd']}")
                
                return result
        except Exception as e:
            print(f"[ERROR] ОШИБКА в can_use для модели {model_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    def register_use(self, model_id, tokens=0):
        with self.lock:
            self._reset_if_needed(model_id)
            self.usage[model_id]["rpm"] += 1
            self.usage[model_id]["tpm"] += tokens
            self.usage[model_id]["rpd"] += 1  # Также увеличиваем счетчик запросов в день
    def wait_for_slot(self, model_id, tokens=0):
        # Ждать, пока не появится слот для запроса
        while not self.can_use(model_id, tokens):
            time.sleep(1)
    # 🚨 НОВОЕ: Получение доступных моделей с учетом blacklist
    def get_available_models(self, task_type):
        """Возвращает список доступ��ых (не заблокированных) моделей для task_type"""
        available = []
        for model in LLM_MODELS_CONFIG:
            if (task_type in model["type"] and 
                not model.get("deprecated", False) and 
                not self.is_model_blocked_safe(model["id"])):
                available.append(model)
        return available
    # 🚨 НОВОЕ: Статистика blacklist
    def get_blacklist_status(self):
        """Возвращает текущее состояние blacklist"""
        with self.lock:
            now = time.time()
            active_blocks = {}
            for model_id, expiry_time in self.blacklisted_models.items():
                if now < expiry_time:
                    remaining = int(expiry_time - now)
                    active_blocks[model_id] = remaining
            return active_blocks
# Инициализация глобального монитора
rate_limit_monitor = RateLimitMonitor(LLM_MODELS_CONFIG)
# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: select_llm_model_safe с учетом blacklist
def select_llm_model_safe(task_type, tokens=0, intelligence_priority=False, exclude_models=None):
    """
    task_type: тип задачи
    tokens: количество токенов
    intelligence_priority: если True, приоритизируем модели с высоким base_score
    exclude_models: список моделей для исключения (дополнительно к blacklist)
    """
    exclude_models = exclude_models or []
    
    # Получаем подходящие модели с учетом blacklist и exclude_models
    suitable_models = []
    for m in LLM_MODELS_CONFIG:
        if (task_type in m["type"] and 
            not m.get("deprecated", False) and
            m["id"] not in exclude_models and
            not rate_limit_monitor.is_model_blocked_safe(m["id"])):
            suitable_models.append(m)
    
    if not suitable_models:
        print(f"❌ Нет доступных моделей для task_type '{task_type}'. Blacklist: {rate_limit_monitor.get_blacklist_status()}")
        return None
    
    # Сортируем с учётом base_score или обычного приоритета
    if intelligence_priority:
        suitable_models = sorted(suitable_models, key=lambda m: (-m["base_score"], m["priority"]))
    else:
        suitable_models = sorted(suitable_models, key=lambda m: m["priority"])
    
    print(f"[AVAILABLE] Доступные модели для '{task_type}': {[m['id'] for m in suitable_models]}")
    
    # ПЕРВЫЙ ПРОХОД: Ищем доступную модель
    for model in suitable_models:
        if rate_limit_monitor.can_use(model["id"], tokens):
            print(f"[SELECTED] AI Router: Выбрана модель '{model['id']}' (приоритет {model['priority']})")
            return model["id"]
    
    # ВТОРОЙ ПРОХОД: Если все модели заняты, берем модель с наименьшим использованием
    print("⚠️ Все доступные модели близки к лимитам, выбираем наименее загруженную...")
    best_model = None
    best_score = float('inf')
    
    for model in suitable_models:
        usage = rate_limit_monitor.usage[model["id"]]
        model_config = rate_limit_monitor.models[model["id"]]
        
        # Считаем "загруженность" как процент от лимитов
        rpm_load = usage["rpm"] / model_config["rpm"]
        tpm_load = (usage["tpm"] + tokens) / model_config["tpm"]
        total_load = rpm_load + tpm_load
        
        if total_load < best_score:
            best_score = total_load
            best_model = model
    
    if best_model:
        print(f"⚠️ AI Router: Принудительно выбрана н��именее загруженная модель '{best_model['id']}' (загрузка: {best_score:.2f})")
        return best_model["id"]
    
    # ТРЕТИЙ ПРОХОД: В крайнем случае возвращаем None для graceful degradation
    print("😴 Все доступные модели исчерпали лимиты. Требуется ожидание или fallback.")
    return None
# 🚨 НОВОЕ: Функция для получения следующей доступной модели (fallback chain)
def get_next_available_model(task_type, current_model_id, tokens=0):
    """Получает следующую доступную модель в цепочке fallback"""
    exclude_models = [current_model_id] if current_model_id else []
    return select_llm_model_safe(task_type, tokens, exclude_models=exclude_models)

def get_active_models():
    """
    Возвращает список активных (не deprecated и не заблокированных) моделей
    
    Returns:
        list: Список активных моделей с их конфигурацией
    """
    active_models = []
    
    for model in LLM_MODELS_CONFIG:
        # Пропускаем deprecated модели
        if model.get('deprecated', False):
            continue
            
        # Пропускаем заблокированные модели
        if rate_limit_monitor.is_model_blocked_safe(model['id']):
            continue
            
        active_models.append(model)
    
    return active_models

# === ФУНКЦИИ-ОБЕРТКИ ДЛЯ СОВМЕСТИМОСТИ С crewai_api_server.py ===

def get_available_models(task_type=None):
    """Функция-обертка для совместимости с crewai_api_server.py"""
    if task_type:
        return rate_limit_monitor.get_available_models(task_type)
    else:
        return get_active_models()

def update_state(*args, **kwargs):
    """Заглушка для update_state - пока не реализована"""
    pass

# Константы для совместимости
PROVIDER_KEY_ENV = {
    'google': 'GOOGLE_API_KEY',
    'openai': 'OPENAI_API_KEY', 
    'anthropic': 'ANTHROPIC_API_KEY',
    'openrouter': 'OPENROUTER_API_KEY'
}

print("[OK] llm_rotation_config загружен с функциями-обертками для совместимости")