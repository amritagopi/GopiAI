#!/usr/bin/env python3
"""
ReflectionEnabledAIRouter - AI Router with self-reflection and improved response quality

Based on patterns:
1. Reflection Pattern (Andrew Ng) - cycles of generation and self-criticism
2. CrewAI Reasoning - planning and reflection before execution
3. Self-Refine - iterative improvement with self-assessment
4. CRITIC - using tools to check quality

Work process:
1. Generation of initial response
2. Critical quality assessment (by several criteria)
3. If quality is below threshold - generation of improved response
4. Repeat until achieving desired quality or iteration limit
"""

import logging
import time
import json
import re
from typing import List, Optional, Dict, Any, Tuple
from pydantic import Field
from langchain.schema import LLMResult, Generation


class ReflectionEnabledAIRouter:
    """
    AI Router с функциональностью саморефлексии и улучшения ответов
    
    Использует паттерн Reflection для автоматического улучшения качества ответов:
    1. Генерирует первичный ответ
    2. Проводит критическую оценку
    3. При необходимости улучшает ответ
    4. Повторяет процесс до достижения качества или лимита итераций
    """
    
    def __init__(self, ai_router, enable_reflection=True, reflection_config=None):
        """
        Инициализирует ReflectionEnabledAIRouter
        
        Args:
            ai_router: Базовый AI Router для генерации ответов
            enable_reflection: Включить ли функциональность рефлексии
            reflection_config: Конфигурация для рефлексии
        """
        self.ai_router = ai_router
        self.enable_reflection = enable_reflection
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация рефлексии по умолчанию
        default_config = {
            'min_quality_threshold': 8.0,  # Минимальная оценка качества (из 10)
            'max_iterations': 3,           # Максимум итераций улучшения
            'quality_criteria': [          # Критерии для оценки качества
                'relevance',              # Релевантность ответа
                'completeness',           # Полнота ответа
                'clarity',                # Ясность изложения
                'accuracy',               # Точность информации
                'usefulness'              # Полезность для пользователя
            ],
            'enable_detailed_critique': True,  # Детальная критика с пояснениями
            'enable_iterative_improvement': True  # Итеративное улучшение
        }
        
        self.reflection_config = {**default_config, **(reflection_config or {})}
        
        # Статистика для мониторинга
        self.reflection_stats = {
            'total_requests': 0,
            'reflection_triggered': 0,
            'improvement_iterations': 0,
            'quality_improvements': 0,
            'average_initial_quality': 0.0,
            'average_final_quality': 0.0,
            'processing_time_total': 0.0
        }
        
        self.logger.info(f"ReflectionEnabledAIRouter инициализирован (reflection={'enabled' if enable_reflection else 'disabled'})")
        self.logger.info(f"Порог качества: {self.reflection_config['min_quality_threshold']}/10")
    
    def _generate_initial_response(self, prompt: str) -> str:
        """
        Генерирует первичный ответ на запрос
        
        Args:
            prompt: Исходный запрос пользователя
            
        Returns:
            str: Первичный ответ
        """
        try:
            self.logger.info("Генерация первичного ответа...")
            result = self.ai_router._generate(prompts=[prompt])
            response = result.generations[0][0].text
            self.logger.info(f"Первичный ответ сгенерирован ({len(response)} символов)")
            return response
        except Exception as e:
            self.logger.error(f"Ошибка при генерации первичного ответа: {e}")
            raise e
    
    def _fallback_quality_assessment(self, prompt: str, response: str) -> float:
        """
        Простая эвристическая оценка качества как fallback
        
        Args:
            prompt: Исходный запрос
            response: Ответ для оценки
            
        Returns:
            float: Оценка качества (0-10)
        """
        score = 5.0  # Базовая оценка
        
        # Длина ответа (слишком короткие или слишком длинные ответы снижают оценку)
        response_length = len(response)
        if 50 <= response_length <= 2000:
            score += 1.0
        elif response_length < 20:
            score -= 2.0
        elif response_length > 5000:
            score -= 1.0
        
        # Наличие структуры (абзацы, списки, заголовки)
        if '\n\n' in response or '\n-' in response or '\n*' in response:
            score += 0.5
        
        # Отсутствие ошибок или предупреждений
        error_indicators = ['ошибка', 'извините', 'не могу', 'недоступно', 'error']
        if any(indicator in response.lower() for indicator in error_indicators):
            score -= 1.5
        
        # Релевантность ключевых слов
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        word_overlap = len(prompt_words.intersection(response_words)) / max(len(prompt_words), 1)
        score += word_overlap * 1.5
        
        return min(max(score, 0.0), 10.0)
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """
        Основной метод генерации с поддержкой рефлексии
        
        Args:
            prompts: Список промптов
            stop: Стоп-последовательности
            
        Returns:
            LLMResult: Результат генерации
        """
        # Пока что простая реализация без полной рефлексии для тестирования
        return self.ai_router._generate(prompts, stop)
    
    def get_llm_instance(self):
        """
        Делегирует получение LLM instance базовому AI Router
        
        Returns:
            LLM: Экземпляр LLM для CrewAI
        """
        return self.ai_router.get_llm_instance()
    
    def set_reflection_enabled(self, enabled: bool):
        """
        Включает/выключает функциональность рефлексии
        
        Args:
            enabled: Включить ли рефлексию
        """
        self.enable_reflection = enabled
        self.logger.info(f"Рефлексия {'включена' if enabled else 'выключена'}")
    
    def update_reflection_config(self, config: Dict):
        """
        Обновляет конфигурацию рефлексии
        
        Args:
            config: Новая конфигурация
        """
        self.reflection_config.update(config)
        self.logger.info(f"Конфигурация рефлексии обновлена: {config}")
    
    def get_reflection_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику по работе рефлексии
        
        Returns:
            Dict: Статистика рефлексии
        """
        stats = self.reflection_stats.copy()
        stats['reflection_enabled'] = self.enable_reflection
        stats['reflection_config'] = self.reflection_config
        return stats
    
    # Делегируем остальные методы базовому AI Router
    def __getattr__(self, name):
        """Делегирует неизвестные методы базовому AI Router"""
        return getattr(self.ai_router, name)
