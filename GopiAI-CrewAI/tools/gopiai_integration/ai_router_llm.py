import logging
import traceback
import time
from typing import List, Optional, Any, Mapping, ClassVar
from pydantic import Field

# Импорт нашего кастомного клиента для обхода ограничений безопасности Gemini
from .gemini_crewai_adapter import GeminiDirectLLM, create_gemini_direct_llm
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, Generation
import sys
import os

# Добавляем путь к корню GopiAI-CrewAI
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from llm_rotation_config import (
    select_llm_model_safe, 
    rate_limit_monitor, 
    LLM_MODELS_CONFIG,
    get_available_models,
    get_models_by_intelligence,
    get_next_available_model,
    register_use,
    is_model_blacklisted
)
# ЕДИНЫЙ ИСТОЧНИК ПРАВДЫ: менеджер конфигураций моделей
from .model_config_manager import get_model_config_manager, ModelProvider
# Импортируем LLM из crewai
from crewai.llm import LLM
class AIRouterLLM(BaseLLM):
    """
    ИСПРАВЛЕННЫЙ AI Router с bulletproof системой ротации моделей
    
    Основные улучшения:
    - Автоматическое блокирование моделей при ошибках API 429
    - Гарантированное переключение на следующую доступную модель
    - Comprehensive error detection и handling
    - Graceful degradation при исчерпании всех моделей
    """
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
    model_configs: dict = Field(default_factory=dict)
    model_config_manager: Optional[Any] = Field(default=None)
    def __init__(self, model_config_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.model_configs = {m['id']: m for m in LLM_MODELS_CONFIG}
        
        # Гарантируем, что model_config_manager будет инициализирован в любом случае
        # Сначала устанавливаем значение по умолчанию
        self.model_config_manager = None
        
        # Инициализируем менеджер конфигураций как single source of truth
        try:
            # Используем переданный model_config_manager, если он есть
            if model_config_manager is not None:
                self.model_config_manager = model_config_manager
                self.logger.info("✅ AIRouterLLM инициализирован с переданным ModelConfigurationManager")
            else:
                # Иначе получаем его стандартным способом
                try:
                    self.model_config_manager = get_model_config_manager()
                    self.logger.info("✅ AIRouterLLM инициализирован с ModelConfigurationManager (SSOT)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Не удалось получить ModelConfigurationManager: {e}")
                    self.model_config_manager = None
        except Exception as e:
            self.logger.warning(f"⚠️ ModelConfigurationManager недоступен: {e}")
            self.model_config_manager = None
            
        # Если model_config_manager все еще None, создаем заглушку
        if self.model_config_manager is None:
            from types import SimpleNamespace
            self.model_config_manager = SimpleNamespace()
            # Добавляем минимальные необходимые методы и атрибуты
            self.model_config_manager.get_model_config = lambda model_id: None
            self.model_config_manager.get_all_models = lambda: []
            # Добавляем другие необходимые методы, которые могут использоваться
            self.model_config_manager.get_current_configuration = lambda: None
            self.model_config_manager.get_provider_status = lambda: {"gemini": {"is_current": True}}
            self.model_config_manager.set_current_configuration = lambda provider, model_id: False
            self.model_config_manager.switch_to_provider = lambda provider: False
            self.logger.warning("⚠️ Создана расширенная заглушка для ModelConfigurationManager")
            
        self.logger.info("✅ AIRouterLLM инициализирован с улучшенной системой ротации")
    def _is_quota_error(self, error):
        """Детектирует все типы ошибок лимитов и квот"""
        error_str = str(error).lower()
        
        # Расширенный список keywords для детекции ошибок квот
        quota_keywords = [
            'quota', 'rate limit', 'exceeded', 'resource_exhausted', 
            'too many requests', '429', 'billing', 'quota_exceeded',
            'limit_exceeded', 'rate_limited', 'throttled', 'overloaded',
            'service unavailable', 'temporarily_unavailable', 'capacity',
            'usage_limit', 'daily_quota', 'monthly_quota', 'free_quota'
        ]
        
        is_quota = any(keyword in error_str for keyword in quota_keywords)
        
        # Дополнительная проверка HTTP статус кодов
        status_codes = ['429', '503', '502', '500']
        has_status_code = any(code in error_str for code in status_codes)
        
        return is_quota or has_status_code
    def _try_model_request(self, prompt, model_id, attempt_number=1):
        """Попытка выполнить запрос к конкретной модели"""
        try:
            model_config = self.model_configs.get(model_id)
            if not model_config:
                raise ValueError(f"Конфигурация для модели {model_id} не найдена")
            # ЖЕСТКО: берём провайдера и ключ из SSOT (model_configurations.json через менеджер)
            provider_name = model_config.get('provider')
            api_key_env = model_config.get('api_key_env')
            
            # Проверяем наличие ключей в .env файле
            if provider_name == 'gemini':
                # Пробуем все возможные переменные для Gemini
                api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                api_key_env = 'GEMINI_API_KEY' if os.getenv('GEMINI_API_KEY') else 'GOOGLE_API_KEY'
            elif provider_name == 'openrouter':
                api_key = os.getenv('OPENROUTER_API_KEY')
            else:
                # Для других провайдеров используем указанную переменную
                api_key = os.getenv(api_key_env or '')
                
            # Если ключ все еще не найден, пробуем получить его из файла .env напрямую
            if not api_key:
                try:
                    from dotenv import load_dotenv
                    # Пробуем загрузить .env файл из разных мест
                    load_dotenv()  # Стандартный .env
                    load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))  # ~/.env
                    
                    # Пробуем снова получить ключ
                    if provider_name == 'gemini':
                        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                    elif provider_name == 'openrouter':
                        api_key = os.getenv('OPENROUTER_API_KEY')
                    else:
                        api_key = os.getenv(api_key_env or '')
                except ImportError:
                    self.logger.warning("python-dotenv не установлен, не могу загрузить .env файл")
                
            if not api_key:
                raise ValueError(f"API ключ не найден: env={api_key_env} для провайдера {provider_name}. Проверьте наличие ключа в .env файле.")
            
            # 🚀 КРИТИЧЕСКОЕ УЛУЧШЕНИЕ: Используем кастомный клиент для Google/Gemini
            # для обхода ограничений безопасности (без safetySettings)
            if provider_name.lower() in ('google', 'gemini'):
                self.logger.info(f"🔥 Используем GeminiDirectClient для обхода ограничений безопасности модели {model_id}")
                
                # Создаем наш кастомный LLM без safetySettings
                llm_instance = create_gemini_direct_llm(
                    model=model_id,
                    api_key=api_key,
                    temperature=0.7
                )
                
                self.logger.info(f"✅ GeminiDirectLLM создан для модели {model_id} (БЕЗ safetySettings!)")
            else:
                # Для других провайдеров используем стандартный подход
                llm_params = {
                    'model': model_id,
                    'api_key': api_key,
                    'config': {
                        'temperature': 0.7,
                        'max_tokens': 2000,
                    }
                }
                # Санитарная правка: если по каким-либо причинам сюда попала gemini-модель,
                # убираем max_tokens из конфига, чтобы не провоцировать BaseLLM.__init__ ошибку
                try:
                    if isinstance(model_id, str) and 'gemini' in model_id.lower():
                        llm_params['config'].pop('max_tokens', None)
                except Exception:
                    pass
                llm_instance = LLM(**llm_params)
                self.logger.info(f"📋 Стандартный LLM создан для модели {model_id}")
            
            # Добавляем задержку для избежания rate limits
            if attempt_number > 1:
                delay = min(attempt_number * 2, 10)  # Максимум 10 секунд
                self.logger.info(f"⏱️ Задержка {delay} секунд перед попыткой {attempt_number}")
                time.sleep(delay)
            
            self.logger.info(f"🔄 Попытка {attempt_number}: Отправляем запрос к модели {model_id}")
            
            # Выполняем запрос
            # Для Gemini используем maxOutputTokens вместо max_tokens
            if provider_name.lower() in ('google', 'gemini'):
                response = llm_instance.call(prompt, maxOutputTokens=8192)
            else:
                response = llm_instance.call(prompt)
            
            if not response or response.strip() == "":
                raise ValueError("Получен пустой ответ от модели")
                
            self.logger.info(f"✅ Успешный ответ от модели {model_id} (длина: {len(response)} символов)")
            return response
            
        except Exception as e:
            self.logger.warning(f"❌ Ошибка при запросе к модели {model_id}: {e}")
            
            # Дополнительная диагностика для Google моделей
            if 'google' in model_id.lower() or 'gemini' in model_id.lower():
                self.logger.info(f"🔍 Диагностика Google/Gemini модели {model_id}: используется прямой HTTP-клиент без safetySettings")
            
            raise e
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        
        for prompt_idx, prompt in enumerate(prompts):
            self.logger.info(f"🧠 Обработка промпта {prompt_idx + 1}/{len(prompts)}")
            response_text = ""
            
            try:
                # Приблизительно оцениваем количество токенов в промпте
                prompt_tokens = len(prompt) // 3
                
                # Определяем, нужна ли высокоинтеллектуальная модель
                intelligence_priority = (len(prompt) > 1000 or 
                                       "сложн" in prompt.lower() or 
                                       "анализ" in prompt.lower() or
                                       "исследование" in prompt.lower())
                
                self.logger.info(f"🧠 {'Высокий' if intelligence_priority else 'Обычный'} приоритет интеллекта")
                
                # 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Bulletproof система переключения моделей
                max_model_attempts = 3  # Максимум попыток с разными моделями
                current_model_id = None
                used_models = []
                
                for model_attempt in range(max_model_attempts):
                    try:
                        # Выбираем модель, исключая уже попробованные
                        # Выбираем модель. Старый параметр exclude_models убран из вызова,
                        # чтобы не ломать сигнатуру select_llm_model_safe. Исключение уже
                        # использованных моделей выполняем локально на уровне кода.
                        # select_llm_model_safe по текущей реализации возвращает СЛОВАРЬ модели,
                        # а также сам регистрирует её использование. Адаптируемся под это API.
                        model_cfg = select_llm_model_safe(
                            task_type="dialog",
                            tokens=prompt_tokens,
                            intelligence_priority=intelligence_priority
                        )
                        # Локально исключаем уже использованные модели и черный список
                        if model_cfg:
                            cand_id = model_cfg.get("id")
                            if cand_id and (cand_id in used_models or is_model_blacklisted(cand_id)):
                                self.logger.info(
                                    f"↩️ Модель {cand_id} уже использована или во временном blacklist — запрашиваем следующую"
                                )
                                try:
                                    next_model_cfg = get_next_available_model(
                                        task_type="dialog",
                                        tokens=prompt_tokens
                                    )
                                    model_cfg = next_model_cfg
                                except Exception as _e:
                                    self.logger.debug(f"get_next_available_model недоступен/ошибка: {_e}")
                        if model_cfg:
                            candidate_model_id = model_cfg.get("id")
                        else:
                            candidate_model_id = None
                        
                        # Безопасно пропускаем модели, уже использованные ранее или находящиеся в blacklist
                        if candidate_model_id and (candidate_model_id in used_models or is_model_blacklisted(candidate_model_id)):
                            self.logger.info(
                                f"↩️ Модель {candidate_model_id} уже использована или во временном blacklists — запрашиваем следующую доступную"
                            )
                            try:
                                next_model_cfg = get_next_available_model(
                                    task_type="dialog",
                                    tokens=prompt_tokens
                                )
                                model_cfg = next_model_cfg
                                candidate_model_id = next_model_cfg.get("id") if next_model_cfg else None
                            except Exception as _e:
                                self.logger.debug(f"get_next_available_model недоступен/вернул ошибку: {_e}")
                        
                        current_model_id = candidate_model_id
                        
                        if not current_model_id:
                            self.logger.error(f"❌ Нет доступных моделей после {model_attempt + 1} попыток")
                            self.logger.error(f"Blacklist статус: {rate_limit_monitor.get_blacklist_status()}")
                            self.logger.error(f"Использованные модели: {used_models}")
                            
                            # Если это первая попытка и нет доступных моделей, ждем и пробуем еще раз
                            if model_attempt == 0:
                                self.logger.info("⏱️ Ожидание восстановления моделей...")
                                time.sleep(30)  # Ждем 30 секунд
                                continue
                            else:
                                raise Exception("Все модели недоступны")
                        
                        used_models.append(current_model_id)
                        
                        # Информативное логирование
                        model_info = self.model_configs.get(current_model_id, {})
                        self.logger.info(f"🎯 Попытка {model_attempt + 1}: Выбрана модель '{current_model_id}' " +
                                       f"(приоритет: {model_info.get('priority', 'N/A')}, " +
                                       f"score: {model_info.get('base_score', 'N/A')})")
                        
                        # Пытаемся выполнить запрос с retry логикой для конкретной модели
                        max_retries = 2  # Максимум попыток для одной модели
                        last_error = None
                        
                        for retry_attempt in range(max_retries):
                            try:
                                response_text = self._try_model_request(
                                    prompt, 
                                    current_model_id, 
                                    retry_attempt + 1
                                )
                                
                                # Успех! Регистрируем использование и выходим
                                response_tokens = len(response_text) // 3
                                # По новой схеме register_use принимает model_id
                                register_use(
                                    current_model_id,
                                    tokens=prompt_tokens + response_tokens
                                )
                                
                                self.logger.info(f"✅ Успешно обработан промпт {prompt_idx + 1} моделью {current_model_id}")
                                break  # Выходим из retry loop
                                
                            except Exception as retry_error:
                                last_error = retry_error
                                self.logger.warning(f"⚠️ Retry {retry_attempt + 1}/{max_retries} для модели {current_model_id}: {retry_error}")
                                
                                # Проверяем тип ошибки
                                if self._is_quota_error(retry_error):
                                    self.logger.error(f"🚫 Quota error обнаружена для модели {current_model_id}")
                                    # В новой реализации у трекера нет прямого mark_model_unavailable.
                                    # Полагемся на мягкий blacklist внутри UsageTracker (автоматически при превышении RPM),
                                    # а также избегаем повторного использования модели в текущем цикле:
                                    if current_model_id:
                                        used_models.append(current_model_id)
                                    break  # Выходим из retry loop и пробуем другую модель
                                
                                # Для других ошибок продолжаем retry
                                if retry_attempt < max_retries - 1:
                                    time.sleep(2 ** retry_attempt)  # Exponential backoff
                        
                        # Если получили ответ, выходим из loop попыток моделей
                        if response_text:
                            break
                            
                        # Если не получили ответ, логируем и пробуем следующую модель
                        if self._is_quota_error(last_error):
                            self.logger.warning(f"🔄 Переключаемся на следующую модель из-за quota error")
                        else:
                            self.logger.warning(f"🔄 Переключаемся на следующую модель из-за ошибки: {last_error}")
                            
                    except Exception as model_error:
                        self.logger.error(f"❌ Критическая ошибка при работе с моделью {current_model_id}: {model_error}")
                        
                        # Если это quota error, блокируем модель
                        if current_model_id and self._is_quota_error(model_error):
                            # Аналогично, мягкий blacklist и исключение модели из повторного выбора
                            used_models.append(current_model_id)
                        
                        # Продолжаем к следующей модели
                        continue
                
                # Если после всех попыток нет ответа
                if not response_text:
                    blacklist_status = rate_limit_monitor.get_blacklist_status()
                    response_text = (f"❌ Все LLM модели временно недоступны из-за исчерпания лимитов. "
                                   f"Заблокированы: {list(blacklist_status.keys())}. "
                                   f"Пожалуйста, попробуйте позже.")
                    
                    self.logger.error(f"💥 КРИТИЧЕСКАЯ СИТУАЦИЯ: Все модели недоступны для промпта {prompt_idx + 1}")
                    self.logger.error(f"Blacklist: {blacklist_status}")
                    self.logger.error(f"Попробованные модели: {used_models}")
            except Exception as e:
                self.logger.error(f"❌ Критическая ошибка при обработке промпта {prompt_idx + 1}: {e}")
                traceback.print_exc()
                response_text = f"Произошла критическая ошибка в AI Router: {e}"
            generations.append([Generation(text=response_text)])
            
        return LLMResult(generations=generations)
    @property
    def _llm_type(self) -> str:
        return "ai_router_bulletproof"
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Возвращает идентификационные параметры LLM."""
        return {"model": self._llm_type}
    def _run(self, message: str, **kwargs) -> str:
        """
        Обязательный метод для наследников GopiAIBaseTool
        Перенаправляет вызов на основной метод `_generate`.
        """
        result = self._generate(prompts=[message])
        return result.generations[0][0].text
    def get_llm_instance(self) -> LLM:
        """
        Возвращает экземпляр LLM для использования в CrewAI с автоматической ротацией.
        """
        try:
            # Выбираем лучшую доступную модель
            # Убираем использование несуществующих параметров в select_llm_model_safe
            model_id = select_llm_model_safe("dialog", intelligence_priority=True)
            if not model_id:
                model_id = select_llm_model_safe("dialog", intelligence_priority=False)
            if not model_id:
                raise ValueError("Нет доступных моделей для CrewAI")
            
            model_config = self.model_configs.get(model_id)
            if not model_config:
                raise ValueError(f"Конфигурация для модели {model_id} не найдена")
            
            provider_name = model_config.get('provider')
            api_key_env = model_config.get('api_key_env')
            
            # Проверяем наличие ключей в .env файле
            if provider_name == 'gemini':
                # Пробуем все возможные переменные для Gemini
                api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                api_key_env = 'GEMINI_API_KEY' if os.getenv('GEMINI_API_KEY') else 'GOOGLE_API_KEY'
            elif provider_name == 'openrouter':
                api_key = os.getenv('OPENROUTER_API_KEY')
            else:
                # Для других провайдеров используем указанную переменную
                api_key = os.getenv(api_key_env or '')
                
            # Если ключ все еще не найден, пробуем получить его из файла .env напрямую
            if not api_key:
                try:
                    from dotenv import load_dotenv
                    # Пробуем загрузить .env файл из разных мест
                    load_dotenv()  # Стандартный .env
                    load_dotenv(os.path.join(os.path.expanduser("~"), ".env"))  # ~/.env
                    
                    # Пробуем снова получить ключ
                    if provider_name == 'gemini':
                        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                    elif provider_name == 'openrouter':
                        api_key = os.getenv('OPENROUTER_API_KEY')
                    else:
                        api_key = os.getenv(api_key_env or '')
                except ImportError:
                    self.logger.warning("python-dotenv не установлен, не могу загрузить .env файл")
                
            if not api_key:
                raise ValueError(f"API ключ не найден: env={api_key_env} для провайдера {provider_name}. Проверьте наличие ключа в .env файле.")
            
            # Для Gemini используем наш безопасный клиент; иначе стандартный LLM
            if provider_name and provider_name.lower() in ('google', 'gemini'):
                llm_instance = create_gemini_direct_llm(
                    model=model_id,
                    api_key=api_key,
                    temperature=0.7
                )
                self.logger.info(f"🎯 CrewAI использует GeminiDirectLLM: {model_id} (env={api_key_env})")
                return llm_instance  # совместим с crewai.llm.LLM интерфейсом-адаптером
            else:
                llm_params = {
                    'model': model_id,
                    'api_key': api_key,
                    'config': {
                        'temperature': 0.7,
                        'max_tokens': 2000,
                    }
                }
                self.logger.info(f"🎯 CrewAI использует стандартный LLM: {model_id} провайдер={provider_name} (env={api_key_env})")
                return LLM(**llm_params)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при создании LLM instance для CrewAI: {e}")
            raise e
    # 🚨 НОВОЕ: Методы для мониторинга и управления
    def get_system_status(self):
        """Возвращает текущий статус системы ротации"""
        blacklist = rate_limit_monitor.get_blacklist_status()
        available_models = [m['id'] for m in get_available_models() 
                          if not is_model_blacklisted(m['id'])]
        
        return {
            "blacklisted_models": blacklist,
            "available_models": available_models,
            "total_models": len(LLM_MODELS_CONFIG),
            "blocked_count": len(blacklist),
            "available_count": len(available_models)
        }
    def force_unblock_model(self, model_id):
        """Принудительно разблокирует модель (для отладки)"""
        # В новой реализации нет прямого доступа к структурам blacklist.
        # Поскольку используется мягкий blacklist по времени, явная разблокировка не поддерживается.
        # Возвращаем False и логируем подсказку.
        self.logger.info("⛔ Принудительная разблокировка недоступна в текущей реализации UsageTracker")
        return False
    def get_model_health(self):
        """Возвращает health check всех моделей"""
        health = {}
        for model in LLM_MODELS_CONFIG:
            model_id = model['id']
            # Если нет метода get_model_usage_stats, просто пропускаем usage_stats или используем заглушку
            health[model_id] = {
                "available": not is_model_blacklisted(model_id),
                "usage_stats": None,  # или {} если нужен пустой словарь
                "priority": model['priority'],
                "deprecated": model.get('deprecated', False)
            }
        return health
