"""
Адаптер для интеграции GeminiDirectClient с CrewAI LLM интерфейсом.

Этот адаптер позволяет использовать наш кастомный клиент (без safetySettings)
как стандартный LLM объект в CrewAI.
"""

import logging
from typing import List, Optional, Any, Mapping
from pydantic import Field
from crewai.llm import LLM, BaseLLM
from .gemini_direct_client import GeminiDirectClient

logger = logging.getLogger(__name__)

class GeminiDirectLLM(BaseLLM):
    """
    Адаптер GeminiDirectClient для использования в CrewAI.
    Обходит ограничения безопасности Gemini API.
    """
    
    # Поля для совместимости с CrewAI
    model: str = Field(default="gemini-1.5-flash-latest")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192)
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Инициализация адаптера.

        ВАЖНО: не передаем api_key в BaseLLM.__init__, чтобы избежать ошибки
        """
        # Сохраняем ключ локально и убираем его из kwargs перед вызовом super
        self._api_key: Optional[str] = api_key
        super().__init__(**kwargs)

        # Создаем экземпляр нашего кастомного клиента
        self.client = GeminiDirectClient(
            api_key=self._api_key,
            model=self.model
        )
        
        # Обновляем настройки генерации
        self.client.default_generation_config.update({
            "temperature": self.temperature,
            "maxOutputTokens": self.max_tokens
        })
        
        logger.info(f"✅ GeminiDirectLLM инициализирован для модели {self.model}")
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs) -> List[str]:
        """
        Генерирует ответы для списка промптов.
        
        Args:
            prompts: Список промптов для генерации
            stop: Список стоп-слов (игнорируется в текущей реализации)
            **kwargs: Дополнительные параметры
            
        Returns:
            Список сгенерированных ответов
        """
        results = []
        
        for prompt in prompts:
            try:
                # Используем наш кастомный клиент
                response = self.client.generate_text(prompt, **kwargs)
                results.append(response)
                
            except Exception as e:
                logger.error(f"❌ Ошибка генерации для промпта: {str(e)}")
                # Возвращаем сообщение об ошибке вместо падения
                results.append(f"Ошибка генерации: {str(e)}")
        
        return results
    
    def call(self, prompt: str, **kwargs) -> str:
        """
        Совместимый с CrewAI метод для одиночного промпта.
        
        Args:
            prompt: Входной промпт
            **kwargs: Дополнительные параметры
            
        Returns:
            Сгенерированный ответ
        """
        try:
            return self.client.generate_text(prompt, **kwargs)
        except Exception as e:
            logger.error(f"❌ Ошибка вызова LLM: {str(e)}")
            return f"Ошибка генерации: {str(e)}"
    
    def generate_structured_response(self, prompt: str, format_type: str = "JSON", **kwargs) -> str:
        """
        Генерирует структурированный ответ с продвинутым промпт-инжинирингом.
        
        Args:
            prompt: Основной промпт
            format_type: Тип формата (JSON, XML, etc.)
            **kwargs: Дополнительные параметры
            
        Returns:
            Структурированный ответ
        """
        return self.client.generate_structured_response(prompt, format_type, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        """Возвращает тип LLM для CrewAI."""
        return "gemini_direct"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Возвращает идентификационные параметры LLM."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "google_direct",
            "safety_bypass": True  # Ключевая особенность!
        }
    
    def get_model_info(self) -> dict:
        """Возвращает информацию о модели."""
        return self.client.get_model_info()


def create_gemini_direct_llm(model: str = "gemini-1.5-flash-latest", 
                           api_key: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: int = 8192,
                           **kwargs) -> GeminiDirectLLM:
    """
    Фабричная функция для создания GeminiDirectLLM.
    
    Args:
        model: Модель Gemini для использования
        api_key: API ключ (если не указан, берется из переменной окружения)
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
        **kwargs: Дополнительные параметры
        
    Returns:
        Настроенный экземпляр GeminiDirectLLM
    """
    return GeminiDirectLLM(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


# Предустановленные конфигурации для разных моделей Gemini
GEMINI_MODELS_CONFIG = {
    "gemini-1.5-flash-latest": {
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Быстрая модель для общих задач"
    },
    "gemini-1.5-pro-latest": {
        "temperature": 0.4,
        "max_tokens": 8192,
        "description": "Продвинутая модель для сложных задач"
    },
    "gemini-2.0-flash-lite": {
        "temperature": 0.5,
        "max_tokens": 8192,
        "description": "Новая облегченная модель"
    }
}

def create_gemini_by_config(model_name: str, **override_params) -> GeminiDirectLLM:
    """
    Создает GeminiDirectLLM на основе предустановленной конфигурации.
    
    Args:
        model_name: Название модели из GEMINI_MODELS_CONFIG
        **override_params: Параметры для переопределения
        
    Returns:
        Настроенный экземпляр GeminiDirectLLM
    """
    if model_name not in GEMINI_MODELS_CONFIG:
        raise ValueError(f"Модель {model_name} не найдена в конфигурации")
    
    config = GEMINI_MODELS_CONFIG[model_name].copy()
    config.update(override_params)
    
    return create_gemini_direct_llm(
        model=model_name,
        **config
    )
