r"""
Кастомный клиент для прямых HTTP-запросов к Gemini API без safetySettings.

Основан на принципах обхода ограничений безопасности, найденных в 
mcp_servers/agentic-control-framework/src/prd_parser.js

Ключевые особенности:
1. Прямые HTTP-запросы через requests вместо официальной библиотеки Google
2. Отсутствие параметра safetySettings - используются настройки по умолчанию API
3. Детальный промпт-инжиниринг для получения структурированных ответов
"""

import os
import requests
import json
import logging
from typing import List, Optional, Dict, Any
from time import sleep

logger = logging.getLogger(__name__)

class GeminiDirectClient:
    """
    Кастомный клиент для прямых HTTP-запросов к Gemini API.
    Обходит ограничения безопасности путем исключения параметра safetySettings.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash-latest"):
        """
        Инициализация клиента.
        
        Args:
            api_key: API ключ Google (если не указан, берется из переменной окружения)
            model: Модель Gemini для использования
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
        
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Настройки по умолчанию (без safetySettings!)
        self.default_generation_config = {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
            "topP": 0.8,
            "topK": 40
        }
        
        logger.info(f"✅ GeminiDirectClient инициализирован для модели {model}")
    
    def _make_request(self, prompt: str, generation_config: Optional[Dict] = None, 
                     max_retries: int = 3) -> Dict[Any, Any]:
        """
        Выполняет прямой HTTP-запрос к Gemini API.
        
        Args:
            prompt: Текст промпта
            generation_config: Настройки генерации (опционально)
            max_retries: Максимальное количество попыток
            
        Returns:
            Ответ от API в формате dict
        """
        url = f"{self.base_url}/{self.model}:generateContent"
        
        # Используем настройки по умолчанию или переданные
        config = generation_config or self.default_generation_config
        
        # Формируем тело запроса БЕЗ safetySettings
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": config
            # ВАЖНО: НЕТ параметра safetySettings!
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "key": self.api_key
        }
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 Попытка {attempt + 1}: отправка запроса к {self.model}")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    params=params,
                    timeout=60
                )
                
                if response.status_code == 200:
                    logger.debug("✅ Успешный ответ от Gemini API")
                    return response.json()
                
                elif response.status_code == 429:
                    # Rate limit - ждем и повторяем
                    wait_time = min(2 ** attempt, 30)  # Экспоненциальная задержка
                    logger.warning(f"⚠️ Rate limit (429), ожидание {wait_time} секунд...")
                    sleep(wait_time)
                    continue
                
                else:
                    logger.error(f"❌ Ошибка API: {response.status_code} - {response.text}")
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Ошибка сети на попытке {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                sleep(2 ** attempt)  # Экспоненциальная задержка
        
        raise Exception(f"Не удалось выполнить запрос после {max_retries} попыток")
    
    def _process_prompt(self, prompt):
        """
        Обрабатывает промпт, поддерживая различные форматы входных данных.
        Конвертирует сообщения с ролями в простой текст для Gemini API.
        
        Args:
            prompt: Строка или список сообщений с ролями
            
        Returns:
            Обработанный текст промпта
        """
        if isinstance(prompt, str):
            return prompt
            
        if isinstance(prompt, list):
            # Обрабатываем список сообщений с ролями
            processed_parts = []
            
            for message in prompt:
                if isinstance(message, dict) and 'role' in message and 'content' in message:
                    role = message['role']
                    content = message['content']
                    
                    # Gemini API не поддерживает роль 'system', объединяем с пользовательским сообщением
                    if role == 'system':
                        processed_parts.append(f"Системные инструкции: {content}")
                    elif role == 'user':
                        processed_parts.append(f"Пользователь: {content}")
                    elif role == 'assistant':
                        processed_parts.append(f"Ассистент: {content}")
                    else:
                        processed_parts.append(content)
                else:
                    # Если это не словарь с ролью, просто добавляем как текст
                    processed_parts.append(str(message))
            
            return "\n\n".join(processed_parts)
        
        # Если это что-то другое, конвертируем в строку
        return str(prompt)
    
    def generate_text(self, prompt, **kwargs) -> str:
        """
        Генерирует текст на основе промпта.
        
        Args:
            prompt: Входной промпт (строка или список сообщений)
            **kwargs: Дополнительные параметры для generation_config
            
        Returns:
            Сгенерированный текст
        """
        # Обрабатываем промпт для поддержки различных форматов
        processed_prompt = self._process_prompt(prompt)
        logger.debug(f"🔄 Обработанный промпт: {processed_prompt[:100]}...")
        
        # Обновляем конфигурацию генерации дополнительными параметрами
        generation_config = self.default_generation_config.copy()
        generation_config.update(kwargs)
        
        try:
            response_data = self._make_request(processed_prompt, generation_config)
            
            # Извлекаем текст из ответа
            if (response_data.get("candidates") and 
                len(response_data["candidates"]) > 0 and
                response_data["candidates"][0].get("content") and
                response_data["candidates"][0]["content"].get("parts")):
                
                text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                logger.debug(f"✅ Получен ответ длиной {len(text)} символов")
                return text
            
            else:
                logger.error(f"❌ Неожиданный формат ответа: {response_data}")
                raise ValueError("Неожиданный формат ответа от Gemini API")
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации текста: {str(e)}")
            raise
    
    def generate_structured_response(self, prompt: str, expected_format: str = "JSON", 
                                   **kwargs) -> str:
        """
        Генерирует структурированный ответ с детальным промпт-инжинирингом.
        
        Args:
            prompt: Основной промпт
            expected_format: Ожидаемый формат ответа (JSON, XML, etc.)
            **kwargs: Дополнительные параметры
            
        Returns:
            Структурированный ответ
        """
        # Применяем принципы продвинутого промпт-инжиниринга
        enhanced_prompt = f"""
{prompt}

ВАЖНЫЕ ИНСТРУКЦИИ ПО ФОРМАТУ ОТВЕТА:
- Выводи ТОЛЬКО {expected_format}, без всякого вступительного текста или объяснений
- НЕ добавляй комментарии, префиксы или суффиксы
- Ответ должен быть валидным {expected_format}
- Начинай ответ сразу с открывающего символа формата

Формат ответа: {expected_format}
"""
        
        return self.generate_text(enhanced_prompt, **kwargs)
    
    def call(self, prompt: str, **kwargs) -> str:
        """
        Совместимый с CrewAI метод для генерации текста.
        
        Args:
            prompt: Входной промпт
            **kwargs: Дополнительные параметры
            
        Returns:
            Сгенерированный текст
        """
        return self.generate_text(prompt, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущей модели.
        
        Returns:
            Словарь с информацией о модели
        """
        return {
            "model": self.model,
            "provider": "google",
            "direct_api": True,
            "safety_settings": "disabled",  # Ключевая особенность!
            "base_url": self.base_url
        }
