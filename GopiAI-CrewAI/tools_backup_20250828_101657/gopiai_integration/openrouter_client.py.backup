#!/usr/bin/env python3
"""
OpenRouter API Client для интеграции с GopiAI
Обеспечивает получение списка моделей, аутентификацию и кэширование
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

@dataclass
class OpenRouterModel:
    """Структура данных модели OpenRouter"""
    id: str
    name: str
    description: str
    context_length: int
    pricing: Dict[str, Any]
    is_active: bool
    is_free: bool
    provider: str
    top_provider: Dict[str, Any]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'OpenRouterModel':
        """Создает объект модели из ответа API"""
        pricing = data.get('pricing', {})
        prompt_price = float(pricing.get('prompt', '0'))
        completion_price = float(pricing.get('completion', '0'))
        
        # Определяем, является ли модель бесплатной
        is_free = (prompt_price == 0 and completion_price == 0) or ':free' in data.get('id', '')
        
        # Извлекаем провайдера из ID
        model_id = data.get('id', '')
        provider = model_id.split('/')[0] if '/' in model_id else 'unknown'
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', model_id),
            description=data.get('description', ''),
            context_length=data.get('context_length', 0),
            pricing=pricing,
            is_active=data.get('is_active', False),
            is_free=is_free,
            provider=provider,
            top_provider=data.get('top_provider', {})
        )
    
    def get_display_name(self) -> str:
        """Возвращает удобное для отображения имя модели"""
        if self.name and self.name != self.id:
            return f"{self.name} ({self.id})"
        return self.id
    
    def get_price_info(self) -> str:
        """Возвращает информацию о цене в удобном формате"""
        if self.is_free:
            return "🆓 Бесплатная"
        
        prompt_price = float(self.pricing.get('prompt', '0'))
        completion_price = float(self.pricing.get('completion', '0'))
        
        if prompt_price > 0 or completion_price > 0:
            return f"💰 ${prompt_price:.6f}/{completion_price:.6f} за 1K токенов"
        
        return "💰 Платная"
    
    def matches_search(self, search_term: str) -> bool:
        """Проверяет, соответствует ли модель поисковому запросу"""
        if not search_term:
            return True
        
        search_term = search_term.lower()
        return (
            search_term in self.id.lower() or
            search_term in self.name.lower() or
            search_term in self.description.lower() or
            search_term in self.provider.lower()
        )

class OpenRouterClient:
    """Клиент для работы с OpenRouter API"""
    
    BASE_URL = "https://openrouter.ai"
    MODELS_ENDPOINT = "/api/v1/models"
    CACHE_DURATION = timedelta(minutes=30)  # Кэшируем на 30 минут
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация клиента OpenRouter
        
        Args:
            api_key: API ключ OpenRouter (если не указан, берется из переменной окружения)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY не найден в переменных окружения")
        
        self._models_cache: List[OpenRouterModel] = []
        self._cache_timestamp: Optional[datetime] = None
        self._session = None
        
        # Настройка retry стратегии
        self.retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        logger.info("🔌 OpenRouterClient инициализирован")
    
    def _get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для HTTP запросов"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GopiAI/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Опциональные метаданные для OpenRouter
        if os.getenv('OR_SITE_URL'):
            headers["HTTP-Referer"] = os.getenv('OR_SITE_URL')
        
        if os.getenv('OR_APP_NAME'):
            headers["X-Title"] = os.getenv('OR_APP_NAME')
        
        return headers
    
    def _is_cache_valid(self) -> bool:
        """Проверяет, актуален ли кэш"""
        if not self._cache_timestamp:
            return False
        
        return datetime.now() - self._cache_timestamp < self.CACHE_DURATION
    
    def get_models_sync(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """
        Синхронно получает список моделей
        
        Args:
            force_refresh: Принудительно обновить кэш
            
        Returns:
            Список доступных моделей
        """
        if not force_refresh and self._is_cache_valid():
            logger.debug("📋 Возвращаем модели из кэша")
            return self._models_cache
        
        try:
            logger.info("🔄 Получаем список моделей OpenRouter...")
            
            session = requests.Session()
            session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
            
            url = f"{self.BASE_URL}{self.MODELS_ENDPOINT}"
            response = session.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 401:
                logger.error("❌ Ошибка аутентификации: проверьте OPENROUTER_API_KEY")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            # Парсим модели
            models_data = data.get('data', [])
            models = []
            
            for model_data in models_data:
                try:
                    model = OpenRouterModel.from_api_response(model_data)
                    # Фильтруем только активные модели
                    if model.is_active:
                        models.append(model)
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка парсинга модели {model_data.get('id', 'unknown')}: {e}")
            
            # Сортируем модели: сначала бесплатные, потом по алфавиту
            models.sort(key=lambda m: (not m.is_free, m.id.lower()))
            
            # Обновляем кэш
            self._models_cache = models
            self._cache_timestamp = datetime.now()
            
            logger.info(f"✅ Получено {len(models)} активных моделей OpenRouter")
            logger.info(f"🆓 Бесплатных моделей: {sum(1 for m in models if m.is_free)}")
            logger.info(f"💰 Платных моделей: {sum(1 for m in models if not m.is_free)}")
            
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка сети при получении моделей: {e}")
            return self._models_cache  # Возвращаем кэш при ошибке
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при получении моделей: {e}")
            return self._models_cache
    
    async def get_models_async(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """
        Асинхронно получает список моделей
        
        Args:
            force_refresh: Принудительно обновить кэш
            
        Returns:
            Список доступных моделей
        """
        if not force_refresh and self._is_cache_valid():
            logger.debug("📋 Возвращаем модели из кэша (async)")
            return self._models_cache
        
        try:
            logger.info("🔄 Получаем список моделей OpenRouter (async)...")
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"{self.BASE_URL}{self.MODELS_ENDPOINT}"
                
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 401:
                        logger.error("❌ Ошибка аутентификации: проверьте OPENROUTER_API_KEY")
                        return []
                    
                    response.raise_for_status()
                    data = await response.json()
            
            # Парсим модели
            models_data = data.get('data', [])
            models = []
            
            for model_data in models_data:
                try:
                    model = OpenRouterModel.from_api_response(model_data)
                    # Фильтруем только активные модели
                    if model.is_active:
                        models.append(model)
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка парсинга модели {model_data.get('id', 'unknown')}: {e}")
            
            # Сортируем модели: сначала бесплатные, потом по алфавиту
            models.sort(key=lambda m: (not m.is_free, m.id.lower()))
            
            # Обновляем кэш
            self._models_cache = models
            self._cache_timestamp = datetime.now()
            
            logger.info(f"✅ Получено {len(models)} активных моделей OpenRouter (async)")
            
            return models
            
        except aiohttp.ClientError as e:
            logger.error(f"❌ Ошибка сети при получении моделей (async): {e}")
            return self._models_cache
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при получении моделей (async): {e}")
            return self._models_cache
    
    def search_models(self, search_term: str, models: Optional[List[OpenRouterModel]] = None) -> List[OpenRouterModel]:
        """
        Поиск моделей по названию
        
        Args:
            search_term: Поисковый запрос
            models: Список моделей для поиска (если не указан, используется кэш)
            
        Returns:
            Отфильтрованный список моделей
        """
        if models is None:
            models = self._models_cache
        
        if not search_term:
            return models
        
        filtered_models = [model for model in models if model.matches_search(search_term)]
        
        logger.debug(f"🔍 Найдено {len(filtered_models)} моделей по запросу '{search_term}'")
        
        return filtered_models
    
    def get_model_by_id(self, model_id: str) -> Optional[OpenRouterModel]:
        """
        Получает модель по ID
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            Объект модели или None, если не найдена
        """
        for model in self._models_cache:
            if model.id == model_id:
                return model
        
        return None
    
    def get_free_models(self) -> List[OpenRouterModel]:
        """Возвращает только бесплатные модели"""
        return [model for model in self._models_cache if model.is_free]
    
    def get_paid_models(self) -> List[OpenRouterModel]:
        """Возвращает только платные модели"""
        return [model for model in self._models_cache if not model.is_free]
    
    def format_model_for_litellm(self, model_id: str) -> str:
        """
        Форматирует ID модели для использования с LiteLLM
        
        Args:
            model_id: ID модели OpenRouter
            
        Returns:
            Отформатированный ID для LiteLLM
        """
        if model_id.startswith('openrouter/'):
            return model_id
        
        return f"openrouter/{model_id}"
    
    def test_connection(self) -> bool:
        """
        Тестирует соединение с OpenRouter API
        
        Returns:
            True, если соединение успешно
        """
        try:
            logger.info("🧪 Тестируем соединение с OpenRouter API...")
            
            session = requests.Session()
            session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
            
            url = f"{self.BASE_URL}{self.MODELS_ENDPOINT}"
            response = session.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Соединение с OpenRouter API успешно")
                return True
            elif response.status_code == 401:
                logger.error("❌ Ошибка аутентификации: неверный API ключ")
                return False
            else:
                logger.error(f"❌ Ошибка соединения: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования соединения: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Возвращает информацию о состоянии кэша"""
        return {
            "cached_models": len(self._models_cache),
            "cache_timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "cache_valid": self._is_cache_valid(),
            "cache_age_minutes": (
                (datetime.now() - self._cache_timestamp).total_seconds() / 60
                if self._cache_timestamp else None
            )
        }

# Глобальный экземпляр клиента
_global_client: Optional[OpenRouterClient] = None

def get_openrouter_client() -> OpenRouterClient:
    """Возвращает глобальный экземпляр OpenRouter клиента"""
    global _global_client
    
    if _global_client is None:
        _global_client = OpenRouterClient()
    
    return _global_client

def test_openrouter_integration():
    """Тестовая функция для проверки интеграции"""
    print("🧪 === ТЕСТ OPENROUTER CLIENT ===")
    
    client = get_openrouter_client()
    
    # Тест соединения
    print("\n1. Тестируем соединение...")
    if client.test_connection():
        print("✅ Соединение успешно")
    else:
        print("❌ Ошибка соединения")
        return
    
    # Тест получения моделей
    print("\n2. Получаем список моделей...")
    models = client.get_models_sync()
    
    if models:
        print(f"✅ Получено {len(models)} моделей")
        
        # Показываем несколько примеров
        free_models = client.get_free_models()
        paid_models = client.get_paid_models()
        
        print(f"🆓 Бесплатных: {len(free_models)}")
        print(f"💰 Платных: {len(paid_models)}")
        
        if free_models:
            print(f"\nПример бесплатной модели: {free_models[0].get_display_name()}")
            print(f"Цена: {free_models[0].get_price_info()}")
        
        if paid_models:
            print(f"\nПример платной модели: {paid_models[0].get_display_name()}")
            print(f"Цена: {paid_models[0].get_price_info()}")
        
        # Тест поиска
        print("\n3. Тестируем поиск...")
        search_results = client.search_models("gpt")
        print(f"🔍 Найдено {len(search_results)} моделей по запросу 'gpt'")
        
        # Тест форматирования для LiteLLM
        if models:
            test_model = models[0]
            formatted = client.format_model_for_litellm(test_model.id)
            print(f"\n4. Форматирование для LiteLLM:")
            print(f"Исходный ID: {test_model.id}")
            print(f"Для LiteLLM: {formatted}")
        
        print("\n✅ Все тесты прошли успешно!")
    else:
        print("❌ Не удалось получить модели")

if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_openrouter_integration()
