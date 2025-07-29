"""
Local LLM Client for GopiAI UI
Enhanced version with proper provider switching support
"""

import logging
import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к Core модулям для доступа к новому LLM клиенту
core_path = Path(__file__).parent.parent.parent.parent / "GopiAI-Core"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))

# Добавляем путь к CrewAI модулям для доступа к llm_rotation_config
crewai_path = Path(__file__).parent.parent.parent.parent / "GopiAI-CrewAI"
if str(crewai_path) not in sys.path:
    sys.path.append(str(crewai_path))

# Глобальная переменная для доступности нового клиента
NEW_LLM_CLIENT_AVAILABLE = False

try:
    # Импортируем новый LLM клиент из Core
    from gopiai.core.llm_client import LlmClient
    NEW_LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import new LlmClient from Core: {e}")

try:
    from llm_rotation_config import select_llm_model_safe, safe_llm_call, MODELS, get_api_key_for_provider, _usage_tracker
except ImportError:
    # Fallback если не удается импортировать
    def select_llm_model_safe(task_type, **kwargs):
        return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    def safe_llm_call(prompt, llm_call_func, task_type, **kwargs):
        return "LLM недоступен"

logger = logging.getLogger(__name__)

class SimpleLLMClient:
    """Enhanced LLM клиент для UI компонентов с поддержкой переключения провайдеров"""
    
    def __init__(self):
        self.current_model = None
        self._llm_client = None
        global NEW_LLM_CLIENT_AVAILABLE
        if NEW_LLM_CLIENT_AVAILABLE:
            try:
                self._llm_client = LlmClient.instance()
                logger.info("Using new LlmClient from Core")
            except Exception as e:
                logger.error(f"Error initializing new LlmClient: {e}")
                NEW_LLM_CLIENT_AVAILABLE = False
        logger.info("LLM client initialized")
    
    def get_model(self, task_type="dialog"):
        """Получить подходящую модель для задачи"""
        try:
            # Если доступен новый клиент, используем его провайдера
            if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
                try:
                    current_provider = self._llm_client.get_current_provider()
                    # Фильтруем модели по текущему провайдеру
                    provider_models = [m for m in MODELS if m["provider"] == current_provider]
                    if provider_models:
                        # Выбираем первую доступную модель текущего провайдера
                        for model in provider_models:
                            if get_api_key_for_provider(model["provider"]):
                                if _usage_tracker.can_use(model):
                                    self.current_model = model
                                    return model
                except Exception as e:
                    logger.error(f"Error getting model from new client: {e}")
            
            # Fallback к старому методу
            model = select_llm_model_safe(task_type)
            self.current_model = model
            return model
        except Exception as e:
            logger.error(f"Error selecting LLM model: {e}")
            return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    async def swap_provider(self, new_provider: str) -> bool:
        """
        Переключить провайдера LLM
        
        Args:
            new_provider: Новый провайдер (gemini, openrouter)
            
        Returns:
            True если переключение успешно, False в противном случае
        """
        global NEW_LLM_CLIENT_AVAILABLE
        if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
            try:
                result = await self._llm_client.swap_provider(new_provider)
                if result:
                    logger.info(f"Successfully switched provider to {new_provider}")
                else:
                    logger.error(f"Failed to switch provider to {new_provider}")
                return result
            except Exception as e:
                logger.error(f"Error switching provider: {e}")
                return False
        else:
            logger.warning("New LLM client not available, cannot switch provider")
            return False
    
    def call(self, prompt, task_type="dialog", **kwargs):
        """Вызов LLM с промптом"""
        global NEW_LLM_CLIENT_AVAILABLE
        # Если доступен новый клиент, используем его
        if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
            try:
                # Асинхронный вызов через asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(
                    self._llm_client.generate(prompt, task_type=task_type, **kwargs)
                )
                loop.close()
                return response
            except Exception as e:
                logger.error(f"Error calling new LLM client: {e}")
                # Fallback to old method
                pass
        
        try:
            # Старый метод как fallback
            model = self.get_model(task_type)
            
            # Простая заглушка для вызова LLM
            # В реальной реализации здесь был бы вызов API
            def mock_llm_call(prompt):
                return f"Mock response for: {prompt[:100]}..."
            
            return safe_llm_call(prompt, mock_llm_call, task_type, **kwargs)
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Error: {str(e)}"
"""
Local LLM Client for GopiAI UI
Enhanced version with proper provider switching support
"""

import logging
import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к Core модулям для доступа к новому LLM клиенту
core_path = Path(__file__).parent.parent.parent.parent / "GopiAI-Core"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))

# Добавляем путь к CrewAI модулям для доступа к llm_rotation_config
crewai_path = Path(__file__).parent.parent.parent.parent / "GopiAI-CrewAI"
if str(crewai_path) not in sys.path:
    sys.path.append(str(crewai_path))

# Глобальная переменная для доступности нового клиента
NEW_LLM_CLIENT_AVAILABLE = False

try:
    # Импортируем новый LLM клиент из Core
    from gopiai.core.llm_client import LlmClient
    NEW_LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import new LlmClient from Core: {e}")

try:
    from llm_rotation_config import select_llm_model_safe, safe_llm_call, MODELS, get_api_key_for_provider, _usage_tracker
except ImportError:
    # Fallback если не удается импортировать
    def select_llm_model_safe(task_type, **kwargs):
        return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    def safe_llm_call(prompt, llm_call_func, task_type, **kwargs):
        return "LLM недоступен"

logger = logging.getLogger(__name__)

class SimpleLLMClient:
    """Enhanced LLM клиент для UI компонентов с поддержкой переключения провайдеров"""
    
    def __init__(self):
        self.current_model = None
        self._llm_client = None
        global NEW_LLM_CLIENT_AVAILABLE
        if NEW_LLM_CLIENT_AVAILABLE:
            try:
                self._llm_client = LlmClient.instance()
                logger.info("Using new LlmClient from Core")
            except Exception as e:
                logger.error(f"Error initializing new LlmClient: {e}")
                NEW_LLM_CLIENT_AVAILABLE = False
        logger.info("LLM client initialized")
    
    def get_model(self, task_type="dialog"):
        """Получить подходящую модель для задачи"""
        try:
            # Если доступен новый клиент, используем его провайдера
            if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
                try:
                    current_provider = self._llm_client.get_current_provider()
                    # Фильтруем модели по текущему провайдеру
                    provider_models = [m for m in MODELS if m["provider"] == current_provider]
                    if provider_models:
                        # Выбираем первую доступную модель текущего провайдера
                        for model in provider_models:
                            if get_api_key_for_provider(model["provider"]):
                                if _usage_tracker.can_use(model):
                                    self.current_model = model
                                    return model
                except Exception as e:
                    logger.error(f"Error getting model from new client: {e}")
            
            # Fallback к старому методу
            model = select_llm_model_safe(task_type)
            self.current_model = model
            return model
        except Exception as e:
            logger.error(f"Error selecting LLM model: {e}")
            return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    async def swap_provider(self, new_provider: str) -> bool:
        """
        Переключить провайдера LLM
        
        Args:
            new_provider: Новый провайдер (gemini, openrouter)
            
        Returns:
            True если переключение успешно, False в противном случае
        """
        global NEW_LLM_CLIENT_AVAILABLE
        if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
            try:
                result = await self._llm_client.swap_provider(new_provider)
                if result:
                    logger.info(f"Successfully switched provider to {new_provider}")
                else:
                    logger.error(f"Failed to switch provider to {new_provider}")
                return result
            except Exception as e:
                logger.error(f"Error switching provider: {e}")
                return False
        else:
            logger.warning("New LLM client not available, cannot switch provider")
            return False
    
    def call(self, prompt, task_type="dialog", **kwargs):
        """Вызов LLM с промптом"""
        global NEW_LLM_CLIENT_AVAILABLE
        try:
            # Если доступен новый клиент, используем его
            if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
                try:
                    # Асинхронный вызов через asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        self._llm_client.generate(prompt, task_type=task_type, **kwargs)
                    )
                    loop.close()
                    return response
                except Exception as e:
                    logger.error(f"Error calling new LLM client: {e}")
                    # Fallback to old method
                    pass
            
            # Старый метод как fallback
            model = self.get_model(task_type)
            
            # Простая заглушка для вызова LLM
            # В реальной реализации здесь был бы вызов API
            def mock_llm_call(prompt):
                return f"Mock response for: {prompt[:100]}..."
            
            return safe_llm_call(prompt, mock_llm_call, task_type, **kwargs)
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self):
        """Проверка доступности LLM"""
        global NEW_LLM_CLIENT_AVAILABLE
        if NEW_LLM_CLIENT_AVAILABLE and self._llm_client:
            try:
                provider = self._llm_client.get_current_provider()
                # Проверяем наличие API ключа для текущего провайдера
                if provider == "gemini":
                    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
                elif provider == "openrouter":
                    return bool(os.getenv("OPENROUTER_API_KEY"))
            except Exception:
                pass
        return True

# Глобальный экземпляр клиента
_llm_client = None

def get_llm_client():
    """Получить экземпляр LLM клиента"""
    global _llm_client
    if _llm_client is None:
        _llm_client = SimpleLLMClient()
    return _llm_client
