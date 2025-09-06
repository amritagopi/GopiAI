"""
Официальный Gemini провайдер с поддержкой code_execution согласно документации.
https://ai.google.dev/gemini-api/docs/code-execution
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass

# Официальный Google Gemini SDK
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

@dataclass
class GeminiConfig:
    """Конфигурация для Gemini провайдера"""
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    enable_code_execution: bool = True
    api_key: Optional[str] = None

class GeminiProvider:
    """Провайдер для работы с официальным Gemini API"""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
            
        logger.info(f"🤖 Инициализация Gemini провайдера (модель: {config.model})")
        
        # Инициализируем клиент
        self.client = genai.Client(api_key=self.api_key)
        
        # Настраиваем конфигурацию генерации
        self._setup_generation_config()
        
        logger.info("✅ Gemini провайдер успешно инициализирован")
    
    def _setup_generation_config(self):
        """Настройка конфигурации генерации согласно документации"""
        tools = []
        
        if self.config.enable_code_execution:
            # Добавляем tool для выполнения кода согласно документации
            tools.append(types.Tool(code_execution=types.ToolCodeExecution()))
            logger.info("🔧 Code execution включен")
        
        self.generation_config = types.GenerateContentConfig(
            tools=tools,
            temperature=self.config.temperature,
        )
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Генерация контента с использованием Gemini API
        """
        try:
            logger.debug(f"📝 Отправка запроса в Gemini: {prompt[:100]}...")
            
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt,
                config=self.generation_config
            )
            
            # Обрабатываем ответ согласно документации
            result_parts = []
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    result_parts.append(part.text)
                    
                if part.executable_code is not None:
                    result_parts.append(f"\n```python\n{part.executable_code.code}\n```")
                    
                if part.code_execution_result is not None:
                    result_parts.append(f"\nВывод:\n{part.code_execution_result.output}")
            
            result = "\n".join(result_parts)
            
            logger.debug(f"✅ Получен ответ от Gemini: {len(result)} символов")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации контента: {e}")
            raise
    
    def create_chat(self):
        """Создание chat сессии с поддержкой code_execution"""
        try:
            chat = self.client.chats.create(
                model=self.config.model,
                config=self.generation_config
            )
            logger.debug("💬 Chat сессия создана")
            return GeminiChat(chat)
        except Exception as e:
            logger.error(f"❌ Ошибка создания chat: {e}")
            raise

class GeminiChat:
    """Обертка для chat сессии"""
    
    def __init__(self, chat):
        self.chat = chat
    
    def send_message(self, message: str) -> str:
        """Отправка сообщения в chat"""
        try:
            response = self.chat.send_message(message)
            
            # Обрабатываем ответ
            result_parts = []
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    result_parts.append(part.text)
                    
                if part.executable_code is not None:
                    result_parts.append(f"\n```python\n{part.executable_code.code}\n```")
                    
                if part.code_execution_result is not None:
                    result_parts.append(f"\nВывод:\n{part.code_execution_result.output}")
            
            return "\n".join(result_parts)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            raise

def create_gemini_provider(
    model: str = "gemini-2.5-flash",
    enable_code_execution: bool = True,
    temperature: float = 0.7
) -> GeminiProvider:
    """Фабричная функция для создания Gemini провайдера"""
    config = GeminiConfig(
        model=model,
        temperature=temperature,
        enable_code_execution=enable_code_execution
    )
    return GeminiProvider(config)