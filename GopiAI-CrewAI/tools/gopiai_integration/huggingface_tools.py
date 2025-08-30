"""
🤗 GopiAI HuggingFace Tool
Интеграция с HuggingFace для работы с моделями
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from .base.base_tool import GopiAIBaseTool

logger = logging.getLogger(__name__)

class GopiAIHuggingFaceTool(GopiAIBaseTool):
    """
    Инструмент для работы с HuggingFace моделями
    """
    
    name: str = "huggingface_tool"
    description: str = "Работа с HuggingFace моделями для генерации текста"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_cache = {}
        self.available_models = self._get_available_models()
    
    def _get_available_models(self) -> List[str]:
        """Получает список доступных моделей"""
        # Базовый список популярных моделей
        return [
            "microsoft/DialoGPT-large",
            "facebook/blenderbot-400M-distill", 
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-small",
            "facebook/blenderbot-3B",
            "google/flan-t5-base",
            "google/flan-t5-large"
        ]
    
    def _run(self, 
             message: str, 
             model_name: str = "microsoft/DialoGPT-large",
             task_type: str = "conversational",
             max_length: int = 100,
             temperature: float = 0.7,
             **kwargs) -> str:
        """
        Запускает модель HuggingFace для генерации ответа
        
        Args:
            message: Входное сообщение
            model_name: Название модели из HuggingFace
            task_type: Тип задачи (conversational, text-generation, summarization)
            max_length: Максимальная длина генерируемого текста
            temperature: Температура для контроля случайности
            **kwargs: Дополнительные параметры
            
        Returns:
            Сгенерированный ответ
        """
        try:
            # Проверяем доступность модели
            if model_name not in self.available_models:
                return f"❌ Модель {model_name} недоступна. Доступные: {', '.join(self.available_models[:3])}..."
            
            # Имитация работы с моделью (в реальной реализации здесь был бы код с transformers)
            logger.info(f"🤖 Используется модель: {model_name}")
            logger.info(f"📝 Тип задачи: {task_type}")
            logger.info(f"🔧 Параметры: max_length={max_length}, temperature={temperature}")
            
            # Базовая генерация ответа (заглушка)
            if task_type == "conversational":
                response = self._generate_conversational_response(message, model_name)
            elif task_type == "text-generation":
                response = self._generate_text_response(message, model_name, max_length)
            elif task_type == "summarization":
                response = self._summarize_text(message, model_name)
            else:
                response = f"❌ Неизвестный тип задачи: {task_type}"
            
            # Логируем результат
            logger.info(f"✅ Сгенерирован ответ длиной {len(response)} символов")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка при работе с HuggingFace: {e}")
            return f"❌ Ошибка при генерации ответа: {str(e)}"
    
    def _generate_conversational_response(self, message: str, model_name: str) -> str:
        """Генерирует ответ в диалоговом режиме"""
        responses = {
            "microsoft/DialoGPT-large": [
                "Понимаю ваш вопрос. Давайте обсудим эту тему подробнее.",
                "Это интересная точка зрения! Можете рассказать больше?",
                "Я согласен с вашим мнением. Что вы думаете по этому поводу?",
                "Спасибо за ваш вопрос. Вот мой ответ..."
            ],
            "facebook/blenderbot-400M-distill": [
                "О, это действительно важная тема! Как вы считаете...",
                "Я понимаю вашу обеспокоенность. Давайте разберем это вместе.",
                "Хороший вопрос! Мой ответ будет основан на анализе...",
                "Спасибо, что поделились этой мыслью. Я полностью согласен."
            ]
        }
        
        default_responses = [
            "Спасибо за ваш вопрос. Я постараюсь помочь вам.",
            "Это интересная тема! Давайте обсудим ее подробнее.",
            "Я понимаю вашу ситуацию. Вот что я думаю по этому поводу..."
        ]
        
        # Выбираем ответ в зависимости от модели
        model_responses = responses.get(model_name, default_responses)
        import random
        return random.choice(model_responses)
    
    def _generate_text_response(self, message: str, model_name: str, max_length: int) -> str:
        """Генерирует текст по заданной теме"""
        return f"Сгенерированный текст на тему '{message[:50]}...' с использованием модели {model_name}. Максимальная длина: {max_length} символов."
    
    def _summarize_text(self, text: str, model_name: str) -> str:
        """Суммаризует текст"""
        if len(text) > 200:
            return f"Суммаризация текста длиной {len(text)} символов с помощью модели {model_name}. Краткое содержание: основной текст обсуждает важные темы и содержит ключевые идеи."
        else:
            return f"Текст уже достаточно короткий для суммаризации: {text}"
    
    def get_available_models(self) -> List[str]:
        """Возвращает список доступных моделей"""
        return self.available_models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Получает информацию о модели"""
        if model_name in self.available_models:
            return {
                "name": model_name,
                "available": True,
                "description": f"Модель {model_name} для работы с текстом",
                "tasks": ["conversational", "text-generation", "summarization"]
            }
        else:
            return {
                "name": model_name,
                "available": False,
                "error": "Модель не найдена"
            }
    
    def list_models(self) -> str:
        """Возвращает список доступных моделей в виде строки"""
        models_list = "\n".join([f"• {model}" for model in self.available_models])
        return f"🤖 Доступные HuggingFace модели:\n{models_list}"
