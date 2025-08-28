#!/usr/bin/env python3
"""
EnhancedAIRouter - Продвинутый AI Router с рефлексией и эмоциональным анализом

Объединяет:
1. ReflectionEnabledAIRouter - саморефлексия и улучшение качества
2. EmotionalClassifier - анализ эмоций и адаптация ответов
3. Контекстная адаптация на основе эмоционального состояния пользователя

Процесс работы:
1. Анализ эмоционального состояния пользователя
2. Генерация ответа с учетом эмоций
3. Рефлексия и улучшение качества ответа
4. Адаптация тона и стиля под эмоциональное состояние
"""

import logging
import time
from typing import List, Optional, Dict, Any
from langchain.schema import LLMResult, Generation

try:
    from self_reflection import ReflectionEnabledAIRouter
    from emotional_classifier import EmotionalClassifier, EmotionalState, EmotionalAnalysis
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    ReflectionEnabledAIRouter = None
    EmotionalClassifier = None


class EnhancedAIRouter:
    """
    Продвинутый AI Router с эмоциональным интеллектом и саморефлексией
    
    Комбинирует анализ эмоций пользователя с улучшением качества ответов
    через рефлексию для создания более естественного и эмпатичного диалога.
    """
    
    def __init__(self, ai_router, enable_reflection=True, enable_emotions=True, 
                 reflection_config=None, emotional_config=None):
        """
        Инициализирует EnhancedAIRouter
        
        Args:
            ai_router: Базовый AI Router
            enable_reflection: Включить саморефлексию
            enable_emotions: Включить эмоциональный анализ
            reflection_config: Конфигурация рефлексии
            emotional_config: Конфигурация эмоционального анализа
        """
        self.base_ai_router = ai_router
        self.enable_reflection = enable_reflection
        self.enable_emotions = enable_emotions
        self.logger = logging.getLogger(__name__)
        
        # Инициализируем компоненты
        self.reflection_router = None
        self.emotional_classifier = None
        
        if enable_reflection and ReflectionEnabledAIRouter:
            self.reflection_router = ReflectionEnabledAIRouter(
                ai_router=ai_router,
                enable_reflection=True,
                reflection_config=reflection_config
            )
            self.logger.info("Модуль рефлексии активирован")
        
        if enable_emotions and EmotionalClassifier:
            self.emotional_classifier = EmotionalClassifier(ai_router)
            self.logger.info("Модуль эмоционального анализа активирован")
        
        # История диалога для эмоционального анализа
        self.conversation_history = []
        
        # Статистика работы
        self.enhanced_stats = {
            'total_requests': 0,
            'emotional_adaptations': 0,
            'reflection_improvements': 0,
            'crisis_detections': 0,
            'average_emotional_intensity': 0.0,
            'most_common_emotion': EmotionalState.NEUTRAL.value if EmotionalState else 'neutral'
        }
        
        self.logger.info(f"EnhancedAIRouter инициализирован (reflection={enable_reflection}, emotions={enable_emotions})")
    
    def process_request_with_emotions(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Обрабатывает запрос с учетом эмоционального состояния пользователя
        
        Args:
            user_message: Сообщение пользователя
            context: Дополнительный контекст
            
        Returns:
            Dict: Полный результат обработки с эмоциональным анализом
        """
        start_time = time.time()
        self.enhanced_stats['total_requests'] += 1
        
        try:
            # 1. Анализ эмоционального состояния
            emotional_analysis = None
            if self.enable_emotions and self.emotional_classifier:
                emotional_analysis = self.emotional_classifier.analyze_emotional_state(
                    self.conversation_history, user_message
                )
                
                # Обновляем статистику эмоций
                self._update_emotional_stats(emotional_analysis)
                
                self.logger.info(f"Эмоциональное состояние: {emotional_analysis.primary_emotion.value} "
                               f"(интенсивность: {emotional_analysis.emotional_intensity:.2f})")
            
            # 2. Адаптация промпта под эмоциональное состояние
            adapted_prompt = self._adapt_prompt_for_emotions(user_message, emotional_analysis)
            
            # 3. Генерация ответа с рефлексией (если включена)
            if self.enable_reflection and self.reflection_router:
                response_result = self.reflection_router._generate([adapted_prompt])
                self.enhanced_stats['reflection_improvements'] += 1
            else:
                response_result = self.base_ai_router._generate([adapted_prompt])
            
            response_text = response_result.generations[0][0].text
            
            # 4. Пост-обработка ответа под эмоциональное состояние
            final_response = self._post_process_response(response_text, emotional_analysis)
            
            # 5. Обновляем историю диалога
            self._update_conversation_history(user_message, final_response)
            
            # 6. Формируем полный результат
            processing_time = time.time() - start_time
            
            result = {
                'response': final_response,
                'emotional_analysis': emotional_analysis.__dict__ if emotional_analysis else None,
                'processing_time': processing_time,
                'adaptations_applied': self._get_applied_adaptations(emotional_analysis),
                'recommendations_for_user': self._get_user_recommendations(emotional_analysis)
            }
            
            self.logger.info(f"Запрос обработан за {processing_time:.2f} сек с эмоциональной адаптацией")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке запроса с эмоциями: {e}")
            # Fallback к базовому ответу
            fallback_result = self.base_ai_router._generate([user_message])
            return {
                'response': fallback_result.generations[0][0].text,
                'emotional_analysis': None,
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _adapt_prompt_for_emotions(self, original_prompt: str, emotional_analysis: Optional[EmotionalAnalysis]) -> str:
        """
        Адаптирует промпт под эмоциональное состояние пользователя
        
        Args:
            original_prompt: Исходный промпт
            emotional_analysis: Результат эмоционального анализа
            
        Returns:
            str: Адаптированный промпт
        """
        if not emotional_analysis or not self.enable_emotions:
            return original_prompt
        
        # Получаем настройки адаптации
        adapter_config = self.emotional_classifier.get_emotional_response_adapter(emotional_analysis)
        
        # Формируем инструкции для AI на основе эмоционального состояния
        emotional_instructions = self._generate_emotional_instructions(emotional_analysis, adapter_config)
        
        # Объединяем инструкции с исходным промптом
        adapted_prompt = f"""{emotional_instructions}

Запрос пользователя: {original_prompt}

Ответьте с учетом эмоционального состояния пользователя и приведенных выше инструкций."""
        
        return adapted_prompt
    
    def _generate_emotional_instructions(self, emotional_analysis: EmotionalAnalysis, 
                                       adapter_config: Dict[str, Any]) -> str:
        """
        Генерирует инструкции для AI на основе эмоционального анализа
        
        Args:
            emotional_analysis: Результат эмоционального анализа
            adapter_config: Конфигурация адаптера
            
        Returns:
            str: Инструкции для AI
        """
        instructions = [
            f"ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ ПОЛЬЗОВАТЕЛЯ: {emotional_analysis.primary_emotion.value}",
            f"Уверенность в анализе: {emotional_analysis.confidence:.1f}/1.0",
            f"Интенсивность эмоций: {emotional_analysis.emotional_intensity:.1f}/1.0"
        ]
        
        # Добавляем тон ответа
        tone_instructions = {
            "enthusiastic": "Отвечайте с энтузиазмом и позитивной энергией",
            "supportive": "Проявите максимальную поддержку и понимание",
            "patient": "Будьте терпеливы и спокойны в объяснениях",
            "explanatory": "Объясняйте детально и простыми словами",
            "emergency_supportive": "КРИЗИСНАЯ СИТУАЦИЯ: максимальная эмпатия и осторожность",
            "neutral": "Поддерживайте нейтральный, профессиональный тон"
        }
        
        tone = adapter_config.get('tone', 'neutral')
        if tone in tone_instructions:
            instructions.append(f"ТОН ОТВЕТА: {tone_instructions[tone]}")
        
        # Добавляем уровень эмпатии
        empathy_level = adapter_config.get('empathy_level', 0.5)
        if empathy_level > 0.8:
            instructions.append("ВЫСОКИЙ УРОВЕНЬ ЭМПАТИИ: Проявите максимальное понимание и сочувствие")
        elif empathy_level > 0.6:
            instructions.append("СРЕДНИЙ УРОВЕНЬ ЭМПАТИИ: Покажите понимание и поддержку")
        
        # Добавляем специальные инструкции
        special_instructions = adapter_config.get('special_instructions', [])
        if special_instructions:
            instructions.append("СПЕЦИАЛЬНЫЕ ИНСТРУКЦИИ:")
            instructions.extend([f"- {instruction}" for instruction in special_instructions])
        
        # Добавляем кризисные предупреждения
        if emotional_analysis.crisis_indicators:
            instructions.extend([
                "",
                "⚠️ ВНИМАНИЕ: ОБНАРУЖЕНЫ КРИЗИСНЫЕ ИНДИКАТОРЫ!",
                f"Типы кризиса: {', '.join(emotional_analysis.crisis_indicators)}",
                "Проявите максимальную осторожность и эмпатию.",
                "Рассмотрите возможность предложения профессиональной помощи."
            ])
            self.enhanced_stats['crisis_detections'] += 1
        
        # Добавляем рекомендации
        if emotional_analysis.recommendations:
            instructions.append("\nРЕКОМЕНДАЦИИ ПО ОТВЕТУ:")
            instructions.extend([f"- {rec}" for rec in emotional_analysis.recommendations])
        
        return "\n".join(instructions)
    
    def _post_process_response(self, response: str, emotional_analysis: Optional[EmotionalAnalysis]) -> str:
        """
        Пост-обработка ответа для улучшения эмоциональной адаптации
        
        Args:
            response: Исходный ответ
            emotional_analysis: Результат эмоционального анализа
            
        Returns:
            str: Обработанный ответ
        """
        if not emotional_analysis or not self.enable_emotions:
            return response
        
        processed_response = response
        
        # Добавляем эмоциональные элементы в зависимости от состояния
        if emotional_analysis.primary_emotion == EmotionalState.POSITIVE:
            # Для позитивных эмоций можем добавить энтузиазм
            if not any(marker in response.lower() for marker in ['!', 'отлично', 'замечательно']):
                # Добавляем позитивные маркеры, если их нет
                pass
        
        elif emotional_analysis.primary_emotion in [EmotionalState.NEGATIVE, EmotionalState.ANXIOUS]:
            # Для негативных эмоций добавляем поддерживающие фразы
            if emotional_analysis.needs_support and not any(phrase in response.lower() for phrase in ['понимаю', 'поддерживаю', 'помочь']):
                processed_response = f"Я понимаю, что вам сейчас нелегко. {response}"
        
        elif emotional_analysis.crisis_indicators:
            # Для кризисных ситуаций добавляем важное предупреждение
            crisis_notice = "\n\n⚠️ Если вы переживаете кризисную ситуацию, пожалуйста, обратитесь за профессиональной помощью или к службе экстренной психологической поддержки."
            processed_response += crisis_notice
        
        return processed_response
    
    def _update_conversation_history(self, user_message: str, ai_response: str):
        """
        Обновляет историю диалога
        
        Args:
            user_message: Сообщение пользователя
            ai_response: Ответ AI
        """
        self.conversation_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Ограничиваем историю последними 20 сообщениями
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _update_emotional_stats(self, emotional_analysis: EmotionalAnalysis):
        """
        Обновляет статистику эмоционального анализа
        
        Args:
            emotional_analysis: Результат анализа
        """
        # Обновляем среднюю интенсивность эмоций
        current_avg = self.enhanced_stats['average_emotional_intensity']
        total_requests = self.enhanced_stats['total_requests']
        new_avg = (current_avg * (total_requests - 1) + emotional_analysis.emotional_intensity) / total_requests
        self.enhanced_stats['average_emotional_intensity'] = new_avg
        
        # Подсчитываем адаптации
        if emotional_analysis.needs_support or emotional_analysis.crisis_indicators:
            self.enhanced_stats['emotional_adaptations'] += 1
    
    def _get_applied_adaptations(self, emotional_analysis: Optional[EmotionalAnalysis]) -> List[str]:
        """
        Возвращает список примененных адаптаций
        
        Args:
            emotional_analysis: Результат эмоционального анализа
            
        Returns:
            List[str]: Список адаптаций
        """
        if not emotional_analysis:
            return ["Эмоциональный анализ отключен"]
        
        adaptations = [
            f"Эмоциональное состояние: {emotional_analysis.primary_emotion.value}",
            f"Интенсивность: {emotional_analysis.emotional_intensity:.1f}/1.0"
        ]
        
        if emotional_analysis.needs_support:
            adaptations.append("Режим поддержки активирован")
        
        if emotional_analysis.crisis_indicators:
            adaptations.append("Кризисный протокол активирован")
        
        return adaptations
    
    def _get_user_recommendations(self, emotional_analysis: Optional[EmotionalAnalysis]) -> List[str]:
        """
        Генерирует рекомендации для пользователя
        
        Args:
            emotional_analysis: Результат эмоционального анализа
            
        Returns:
            List[str]: Рекомендации для пользователя
        """
        if not emotional_analysis:
            return []
        
        user_recommendations = []
        
        if emotional_analysis.primary_emotion == EmotionalState.FRUSTRATED:
            user_recommendations.extend([
                "Попробуйте разбить задачу на более мелкие шаги",
                "Сделайте небольшой перерыв, если это возможно"
            ])
        
        elif emotional_analysis.primary_emotion == EmotionalState.ANXIOUS:
            user_recommendations.extend([
                "Сосредоточьтесь на дыхании и расслаблении",
                "Обратитесь за поддержкой к близким, если нужно"
            ])
        
        elif emotional_analysis.crisis_indicators:
            user_recommendations.extend([
                "Обратитесь к специалисту по психическому здоровью",
                "Свяжитесь со службой экстренной помощи при необходимости",
                "Поговорите с доверенным другом или членом семьи"
            ])
        
        return user_recommendations
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """
        Возвращает расширенную статистику работы
        
        Returns:
            Dict: Статистика работы всех компонентов
        """
        stats = {
            'enhanced_router': self.enhanced_stats.copy(),
            'reflection_enabled': self.enable_reflection,
            'emotions_enabled': self.enable_emotions
        }
        
        if self.reflection_router:
            stats['reflection_stats'] = self.reflection_router.get_reflection_stats()
        
        return stats
    
    def clear_conversation_history(self):
        """Очищает историю диалога"""
        self.conversation_history.clear()
        self.logger.info("История диалога очищена")
    
    # Делегируем остальные методы базовому AI Router
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """Основной метод генерации (для совместимости)"""
        if len(prompts) == 1:
            result = self.process_request_with_emotions(prompts[0])
            return LLMResult(generations=[[Generation(text=result['response'])]])
        else:
            # Для множественных промптов используем базовый роутер
            return self.base_ai_router._generate(prompts, stop)
    
    def get_llm_instance(self):
        """Делегирует получение LLM instance"""
        return self.base_ai_router.get_llm_instance()
    
    def __getattr__(self, name):
        """Делегирует неизвестные методы базовому AI Router"""
        return getattr(self.base_ai_router, name)


# Для тестирования
if __name__ == "__main__":
    print("Тестирование EnhancedAIRouter")
    
    # Моковый AI Router для тестирования
    class MockAIRouter:
        def _generate(self, prompts):
            class MockGeneration:
                def __init__(self, text):
                    self.text = text
            
            class MockResult:
                def __init__(self):
                    prompt = prompts[0] if prompts else ""
                    if "грустно" in prompt.lower():
                        response = "Я понимаю, что вам сейчас тяжело. Хотите поговорить об этом?"
                    elif "спасибо" in prompt.lower():
                        response = "Пожалуйста! Я рад, что смог помочь!"
                    else:
                        response = "Я готов помочь вам с вашим вопросом."
                    
                    self.generations = [[MockGeneration(response)]]
            
            return MockResult()
        
        def get_llm_instance(self):
            return self
    
    # Тестируем Enhanced Router
    try:
        enhanced_router = EnhancedAIRouter(
            ai_router=MockAIRouter(),
            enable_reflection=True,
            enable_emotions=True
        )
        
        # Тест 1: Позитивное сообщение
        result1 = enhanced_router.process_request_with_emotions("Спасибо большое! Ты мне очень помог!")
        print(f"\n1. Позитивный тест:")
        print(f"Ответ: {result1['response']}")
        print(f"Эмоция: {result1['emotional_analysis']['primary_emotion'] if result1['emotional_analysis'] else 'N/A'}")
        
        # Тест 2: Негативное сообщение
        result2 = enhanced_router.process_request_with_emotions("Мне очень грустно и тяжело на душе...")
        print(f"\n2. Негативный тест:")
        print(f"Ответ: {result2['response']}")
        print(f"Эмоция: {result2['emotional_analysis']['primary_emotion'] if result2['emotional_analysis'] else 'N/A'}")
        
        # Статистика
        print(f"\n3. Статистика:")
        stats = enhanced_router.get_enhanced_stats()
        print(f"Обработано запросов: {stats['enhanced_router']['total_requests']}")
        print(f"Эмоциональных адаптаций: {stats['enhanced_router']['emotional_adaptations']}")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        print("Возможно, не все модули доступны")
