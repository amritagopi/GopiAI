#!/usr/bin/env python3
"""
EmotionalClassifier - Анализатор эмоций для GopiAI

Основан на промптах от OpenAI emoclassifiers:
- Анализ эмоционального содержания диалогов
- Классификация настроения пользователя
- Адаптация ответов под эмоциональное состояние
- Детектирование проблемных состояний (стресс, тревога и т.д.)

Поддерживаемые эмоциональные категории:
1. Позитивные: радость, удовлетворение, воодушевление
2. Негативные: грусть, фрустрация, злость, тревога
3. Нейтральные: спокойствие, любопытство
4. Специальные: стресс, депрессия, суицидальные мысли (требуют особого внимания)
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass


class EmotionalState(Enum):
    """Основные эмоциональные состояния"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    ANGRY = "angry"
    SUPPORTIVE_NEEDED = "supportive_needed"


@dataclass
class EmotionalAnalysis:
    """Результат эмоционального анализа"""
    primary_emotion: EmotionalState
    confidence: float  # 0.0 - 1.0
    secondary_emotions: List[EmotionalState]
    emotional_intensity: float  # 0.0 - 1.0
    needs_support: bool
    crisis_indicators: List[str]
    recommendations: List[str]


class EmotionalClassifier:
    """
    Классификатор эмоций для диалогов с AI
    
    Анализирует эмоциональное состояние пользователя и предоставляет
    рекомендации для адаптации ответов AI под текущее настроение.
    """
    
    def __init__(self, ai_router):
        """
        Инициализирует EmotionalClassifier
        
        Args:
            ai_router: AI Router для выполнения анализа
        """
        self.ai_router = ai_router
        self.logger = logging.getLogger(__name__)
        
        # Проверяем наличие model_config_manager в ai_router
        if hasattr(self.ai_router, 'model_config_manager') and self.ai_router.model_config_manager is not None:
            self.logger.info("✅ EmotionalClassifier: model_config_manager найден в ai_router")
        else:
            self.logger.error("❌ Ошибка инициализации эмоционального классификатора: \"AIRouterLLM\" object has no field \"model_config_manager\" или атрибут равен None")
            # Создаем заглушку для model_config_manager, если его нет или он None
            from types import SimpleNamespace
            stub_manager = SimpleNamespace()
            # Добавляем минимальные необходимые методы и атрибуты
            stub_manager.get_model_config = lambda model_id: None
            stub_manager.get_all_models = lambda: []
            stub_manager.get_current_configuration = lambda: None
            stub_manager.get_provider_status = lambda: {"gemini": {"is_current": True}}
            stub_manager.set_current_configuration = lambda provider, model_id: False
            stub_manager.switch_to_provider = lambda provider: False
            
            # Устанавливаем заглушку
            setattr(self.ai_router, 'model_config_manager', stub_manager)
            self.logger.warning("⚠️ Создана заглушка для model_config_manager в EmotionalClassifier")
        
        # Критерии для различных типов эмоций
        self.emotion_criteria = {
            EmotionalState.POSITIVE: {
                "keywords": ["рад", "счастлив", "отлично", "замечательно", "восхитительно", "благодарен"],
                "patterns": ["как здорово", "очень доволен", "прекрасно работает"],
                "description": "Положительные эмоции: радость, удовлетворение, благодарность"
            },
            EmotionalState.NEGATIVE: {
                "keywords": ["грустно", "плохо", "ужасно", "расстроен", "печально", "тяжело"],
                "patterns": ["не могу больше", "все плохо", "ничего не получается"],
                "description": "Негативные эмоции: грусть, разочарование, печаль"
            },
            EmotionalState.FRUSTRATED: {
                "keywords": ["раздражает", "бесит", "достало", "надоело", "злит", "фрустрирует"],
                "patterns": ["не работает как надо", "уже сколько раз", "почему не получается"],
                "description": "Фрустрация: раздражение от неудач или препятствий"
            },
            EmotionalState.ANXIOUS: {
                "keywords": ["беспокоюсь", "тревожно", "волнуюсь", "страшно", "нервничаю"],
                "patterns": ["что если", "боюсь что", "а вдруг"],
                "description": "Тревога: беспокойство о будущем или неопределенности"
            },
            EmotionalState.CONFUSED: {
                "keywords": ["не понимаю", "запутался", "сложно", "непонятно", "как это"],
                "patterns": ["объясни еще раз", "не могу разобраться", "что это значит"],
                "description": "Замешательство: недопонимание или неясность"
            },
            EmotionalState.SUPPORTIVE_NEEDED: {
                "keywords": ["помоги", "поддержи", "трудно", "одиноко", "тяжелый период"],
                "patterns": ["нужна поддержка", "чувствую себя", "справиться самому"],
                "description": "Потребность в поддержке: просьба о помощи или понимании"
            }
        }
        
        # Кризисные индикаторы (требуют особого внимания)
        self.crisis_indicators = {
            "suicidal": ["не хочу жить", "покончить с собой", "суицид", "самоубийство"],
            "self_harm": ["причинить себе боль", "самоповреждение", "порезать себя"],
            "severe_depression": ["жизнь не имеет смысла", "все бесполезно", "никто не поймет"],
            "panic": ["паническая атака", "не могу дышать", "сердце бешено бьется"],
            "abuse": ["бьет меня", "насилие", "угрожает", "причиняет боль"]
        }
        
        self.logger.info("EmotionalClassifier инициализирован")
    
    def analyze_emotional_state(self, conversation_history: List[Dict], current_message: str) -> EmotionalAnalysis:
        """
        Анализирует эмоциональное состояние на основе сообщения и истории диалога
        
        Args:
            conversation_history: История диалога [{"role": "user/assistant", "content": "..."}]
            current_message: Текущее сообщение для анализа
            
        Returns:
            EmotionalAnalysis: Результат анализа эмоций
        """
        try:
            # 1. Быстрая эвристическая оценка
            heuristic_result = self._heuristic_emotion_detection(current_message)
            
            # 2. Детальный анализ через AI
            ai_result = self._ai_emotion_analysis(conversation_history, current_message)
            
            # 3. Проверка кризисных индикаторов
            crisis_indicators = self._detect_crisis_indicators(current_message)
            
            # 4. Объединение результатов
            final_analysis = self._combine_analysis_results(
                heuristic_result, ai_result, crisis_indicators
            )
            
            self.logger.info(f"Эмоциональный анализ завершен: {final_analysis.primary_emotion.value} (confidence: {final_analysis.confidence:.2f})")
            
            return final_analysis
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе эмоций: {e}")
            # Возвращаем нейтральный результат при ошибке
            return EmotionalAnalysis(
                primary_emotion=EmotionalState.NEUTRAL,
                confidence=0.5,
                secondary_emotions=[],
                emotional_intensity=0.5,
                needs_support=False,
                crisis_indicators=[],
                recommendations=["Продолжить диалог в обычном режиме"]
            )
    
    def _heuristic_emotion_detection(self, message: str) -> Dict[str, Any]:
        """
        Быстрое эвристическое определение эмоций по ключевым словам
        
        Args:
            message: Сообщение для анализа
            
        Returns:
            Dict: Результат эвристического анализа
        """
        message_lower = message.lower()
        detected_emotions = {}
        
        for emotion, criteria in self.emotion_criteria.items():
            score = 0.0
            
            # Проверяем ключевые слова
            for keyword in criteria["keywords"]:
                if keyword in message_lower:
                    score += 0.3
            
            # Проверяем паттерны
            for pattern in criteria["patterns"]:
                if pattern in message_lower:
                    score += 0.5
            
            if score > 0:
                detected_emotions[emotion] = min(score, 1.0)
        
        # Определяем доминирующую эмоцию
        if detected_emotions:
            primary_emotion = max(detected_emotions.items(), key=lambda x: x[1])
            return {
                "primary_emotion": primary_emotion[0],
                "confidence": primary_emotion[1],
                "all_emotions": detected_emotions
            }
        else:
            return {
                "primary_emotion": EmotionalState.NEUTRAL,
                "confidence": 0.7,
                "all_emotions": {EmotionalState.NEUTRAL: 0.7}
            }
    
    def _ai_emotion_analysis(self, conversation_history: List[Dict], current_message: str) -> Dict[str, Any]:
        """
        Детальный анализ эмоций через AI (адаптированный промпт от OpenAI)
        
        Args:
            conversation_history: История диалога
            current_message: Текущее сообщение
            
        Returns:
            Dict: Результат AI анализа
        """
        try:
            # Проверяем, что ai_router доступен и имеет метод _generate
            if not hasattr(self.ai_router, '_generate'):
                self.logger.error("❌ ai_router не имеет метода _generate")
                return {"primary_emotion": "neutral", "confidence": 0.5}
                
            # Формируем контекст диалога
            conversation_context = self._format_conversation_for_analysis(conversation_history, current_message)
            
            # Создаем промпт на основе OpenAI emoclassifiers
            analysis_prompt = f"""
Вы - эксперт по анализу эмоционального содержания диалогов с AI-ассистентом.
Вам будет представлен фрагмент диалога между пользователем и ассистентом.

Ваша задача: проанализировать эмоциональное состояние пользователя в его ПОСЛЕДНЕМ сообщении.

Критерии анализа:
1. ПОЗИТИВНЫЕ ЭМОЦИИ: радость, удовлетворение, благодарность, воодушевление
2. НЕГАТИВНЫЕ ЭМОЦИИ: грусть, разочарование, печаль, уныние
3. ФРУСТРАЦИЯ: раздражение, злость от неудач или препятствий
4. ТРЕВОГА: беспокойство, волнение, страх неопределенности
5. ЗАМЕШАТЕЛЬСТВО: непонимание, путаница, потребность в разъяснении
6. ПОТРЕБНОСТЬ В ПОДДЕРЖКЕ: просьба о помощи, сочувствии или понимании

Важные замечания:
- Если пользователь просит помочь с написанием художественного текста, анализируйте его эмоции, а не эмоции персонажей
- Если сообщение очень короткое или нейтральное, классифицируйте как "нейтральное"
- Обращайте внимание на контекст предыдущих сообщений

Диалог для анализа:
<snippet>
{conversation_context}
</snippet>

Верните ответ в следующем JSON формате:
{{
  "primary_emotion": "название_основной_эмоции",
  "confidence": уровень_уверенности_от_0_до_1,
  "emotional_intensity": интенсивность_эмоции_от_0_до_1,
  "explanation": "краткое объяснение вашего анализа",
  "recommendations": ["рекомендация_1", "рекомендация_2"]
}}
"""
            
            # Отправляем запрос к AI с обработкой ошибок
            try:
                result = self.ai_router._generate(prompts=[analysis_prompt])
                if not result or not hasattr(result, 'generations') or not result.generations:
                    raise ValueError("Некорректный результат от AI")
                response_text = result.generations[0][0].text
            except Exception as ai_error:
                self.logger.error(f"❌ Ошибка при вызове AI: {ai_error}")
                return {"primary_emotion": "neutral", "confidence": 0.5}
            
            # Парсим JSON ответ
            try:
                # Извлекаем JSON из ответа
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    ai_analysis = json.loads(json_str)
                    return ai_analysis
                else:
                    raise ValueError("JSON не найден в ответе AI")
                    
            except (json.JSONDecodeError, ValueError) as parse_error:
                self.logger.warning(f"Ошибка парсинга AI анализа эмоций: {parse_error}")
                return {"primary_emotion": "neutral", "confidence": 0.5}
                
        except Exception as e:
            self.logger.error(f"Ошибка при AI анализе эмоций: {e}")
            return {"primary_emotion": "neutral", "confidence": 0.5}
    
    def _format_conversation_for_analysis(self, conversation_history: List[Dict], current_message: str) -> str:
        """
        Форматирует диалог для анализа в стиле OpenAI emoclassifiers
        
        Args:
            conversation_history: История диалога
            current_message: Текущее сообщение
            
        Returns:
            str: Отформатированный диалог
        """
        formatted_lines = []
        
        # Добавляем историю диалога
        for entry in conversation_history[-5:]:  # Последние 5 сообщений для контекста
            if entry["role"] == "user":
                formatted_lines.append(f"[USER]: {entry['content']}")
            elif entry["role"] == "assistant":
                formatted_lines.append(f"[ASSISTANT]: {entry['content']}")
        
        # Добавляем текущее сообщение (помечаем звездочками как в оригинальном промпте)
        formatted_lines.append(f"[*USER*]: {current_message}")
        
        return "\n".join(formatted_lines)
    
    def _detect_crisis_indicators(self, message: str) -> List[str]:
        """
        Обнаруживает индикаторы кризисных состояний
        
        Args:
            message: Сообщение для анализа
            
        Returns:
            List[str]: Список обнаруженных кризисных индикаторов
        """
        message_lower = message.lower()
        detected_indicators = []
        
        for indicator_type, phrases in self.crisis_indicators.items():
            for phrase in phrases:
                if phrase in message_lower:
                    detected_indicators.append(indicator_type)
                    break  # Одного совпадения достаточно для каждого типа
        
        return detected_indicators
    
    def _combine_analysis_results(self, heuristic_result: Dict, ai_result: Dict, crisis_indicators: List[str]) -> EmotionalAnalysis:
        """
        Объединяет результаты различных методов анализа
        
        Args:
            heuristic_result: Результат эвристического анализа
            ai_result: Результат AI анализа
            crisis_indicators: Обнаруженные кризисные индикаторы
            
        Returns:
            EmotionalAnalysis: Финальный результат анализа
        """
        # Определяем основную эмоцию (приоритет AI анализу)
        ai_emotion_name = ai_result.get("primary_emotion", "neutral")
        
        # Мапим название эмоции на enum
        emotion_mapping = {
            "positive": EmotionalState.POSITIVE,
            "negative": EmotionalState.NEGATIVE,
            "frustrated": EmotionalState.FRUSTRATED,
            "anxious": EmotionalState.ANXIOUS,
            "confused": EmotionalState.CONFUSED,
            "supportive_needed": EmotionalState.SUPPORTIVE_NEEDED,
            "neutral": EmotionalState.NEUTRAL
        }
        
        primary_emotion = emotion_mapping.get(ai_emotion_name, heuristic_result["primary_emotion"])
        
        # Вычисляем уверенность (среднее между методами)
        ai_confidence = ai_result.get("confidence", 0.5)
        heuristic_confidence = heuristic_result["confidence"]
        combined_confidence = (ai_confidence + heuristic_confidence) / 2
        
        # Определяем интенсивность эмоций
        emotional_intensity = ai_result.get("emotional_intensity", 0.5)
        
        # Проверяем, нужна ли поддержка
        needs_support = (
            primary_emotion in [EmotionalState.NEGATIVE, EmotionalState.ANXIOUS, EmotionalState.SUPPORTIVE_NEEDED] or
            len(crisis_indicators) > 0 or
            emotional_intensity > 0.8
        )
        
        # Формируем рекомендации
        recommendations = self._generate_recommendations(primary_emotion, crisis_indicators, emotional_intensity)
        
        return EmotionalAnalysis(
            primary_emotion=primary_emotion,
            confidence=combined_confidence,
            secondary_emotions=[],  # Пока что не используем
            emotional_intensity=emotional_intensity,
            needs_support=needs_support,
            crisis_indicators=crisis_indicators,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, primary_emotion: EmotionalState, crisis_indicators: List[str], intensity: float) -> List[str]:
        """
        Генерирует рекомендации на основе анализа эмоций
        
        Args:
            primary_emotion: Основная эмоция
            crisis_indicators: Кризисные индикаторы
            intensity: Интенсивность эмоций
            
        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = []
        
        # Кризисные ситуации имеют приоритет
        if crisis_indicators:
            recommendations.extend([
                "СРОЧНО: Обнаружены признаки кризисного состояния",
                "Предложить профессиональную помощь",
                "Проявить максимальную эмпатию и поддержку",
                "Избегать советов - только слушать и поддерживать"
            ])
            return recommendations
        
        # Рекомендации на основе эмоций
        if primary_emotion == EmotionalState.POSITIVE:
            recommendations.extend([
                "Поддержать позитивное настроение",
                "Можно предложить дополнительные возможности",
                "Проявить энтузиазм в ответе"
            ])
        elif primary_emotion == EmotionalState.NEGATIVE:
            recommendations.extend([
                "Проявить эмпатию и понимание",
                "Предложить конкретную помощь",
                "Говорить мягче и поддерживающе"
            ])
        elif primary_emotion == EmotionalState.FRUSTRATED:
            recommendations.extend([
                "Признать фрустрацию пользователя",
                "Предложить пошаговое решение",
                "Быть терпеливым и понимающим"
            ])
        elif primary_emotion == EmotionalState.ANXIOUS:
            recommendations.extend([
                "Успокоить и поддержать",
                "Разбить сложные задачи на простые шаги",
                "Предоставить четкую информацию"
            ])
        elif primary_emotion == EmotionalState.CONFUSED:
            recommendations.extend([
                "Объяснить еще раз более простыми словами",
                "Использовать примеры и аналогии",
                "Проверить понимание пользователя"
            ])
        
        # Дополнительные рекомендации на основе интенсивности
        if intensity > 0.8:
            recommendations.append("Высокая интенсивность эмоций - будьте особенно внимательны")
        
        return recommendations if recommendations else ["Продолжить диалог в обычном режиме"]
    
    def get_emotional_response_adapter(self, analysis: EmotionalAnalysis) -> Dict[str, Any]:
        """
        Возвращает настройки для адаптации ответа под эмоциональное состояние
        
        Args:
            analysis: Результат эмоционального анализа
            
        Returns:
            Dict: Настройки для адаптации ответа
        """
        adapter_config = {
            "tone": "neutral",
            "empathy_level": 0.5,
            "support_level": 0.5,
            "response_length": "normal",
            "special_instructions": []
        }
        
        # Настройки на основе эмоций
        if analysis.primary_emotion == EmotionalState.POSITIVE:
            adapter_config.update({
                "tone": "enthusiastic",
                "empathy_level": 0.7,
                "response_length": "detailed"
            })
        elif analysis.primary_emotion in [EmotionalState.NEGATIVE, EmotionalState.ANXIOUS]:
            adapter_config.update({
                "tone": "supportive",
                "empathy_level": 0.9,
                "support_level": 0.9,
                "special_instructions": ["Проявить максимальную эмпатию", "Предложить помощь"]
            })
        elif analysis.primary_emotion == EmotionalState.FRUSTRATED:
            adapter_config.update({
                "tone": "patient",
                "empathy_level": 0.8,
                "special_instructions": ["Признать фрустрацию", "Предложить пошаговое решение"]
            })
        elif analysis.primary_emotion == EmotionalState.CONFUSED:
            adapter_config.update({
                "tone": "explanatory",
                "response_length": "detailed",
                "special_instructions": ["Объяснить простыми словами", "Использовать примеры"]
            })
        
        # Специальные настройки для кризисных ситуаций
        if analysis.crisis_indicators:
            adapter_config.update({
                "tone": "emergency_supportive",
                "empathy_level": 1.0,
                "support_level": 1.0,
                "special_instructions": [
                    "КРИЗИСНАЯ СИТУАЦИЯ",
                    "Максимальная поддержка",
                    "Предложить профессиональную помощь"
                ]
            })
        
        return adapter_config


def run_tests():
    """Запуск тестов эмоционального классификатора"""
    print("\n" + "="*80)
    print("🔍 ТЕСТИРОВАНИЕ EMOTIONAL CLASSIFIER".center(80))
    print("="*80 + "\n")
    
    # Включаем подробный вывод
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("Настройка вывода завершена")
    
    # Моковый AI Router для тестирования
    print("Инициализация мокового AI Router...")
    class MockAIRouter:
        def _generate(self, prompts):
            class MockGeneration:
                def __init__(self, text):
                    self.text = text
            
            class MockResult:
                def __init__(self, emotion_data):
                    self.generations = [[MockGeneration(json.dumps(emotion_data))]]
            
            # Извлекаем текст запроса из промпта
            def extract_text(prompt):
                if hasattr(prompt, 'text'):
                    return prompt.text
                elif isinstance(prompt, str):
                    return prompt
                elif isinstance(prompt, list) and prompt:
                    return extract_text(prompt[0])
                return str(prompt)
                
            prompt_text = extract_text(prompts)
            
            # Определяем эмоцию на основе ключевых слов (в порядке приоритета)
            prompt_lower = prompt_text.lower()
            
            if any(word in prompt_lower for word in ["рад", "спасибо", "помог", "отлично"]):
                return MockResult({
                    "primary_emotion": "positive",
                    "confidence": 0.9,
                    "emotional_intensity": 0.8,
                    "explanation": "Пользователь выражает радость и благодарность",
                    "recommendations": ["Поддержать позитивное настроение"],
                    "secondary_emotions": ["gratitude", "happiness"]
                })
            elif any(word in prompt_text.lower() for word in ["отчаянии", "одиноко", "не получается"]):
                return MockResult({
                    "primary_emotion": "depressed",
                    "confidence": 0.85,
                    "emotional_intensity": 0.9,
                    "explanation": "Пользователь выражает отчаяние и одиночество",
                    "recommendations": ["Проявить эмпатию и предложить поддержку"],
                    "secondary_emotions": ["sadness", "hopelessness"]
                })
            elif any(word in prompt_text.lower() for word in ["почему", "не работает", "пробовал"]):
                return MockResult({
                    "primary_emotion": "frustrated",
                    "confidence": 0.8,
                    "emotional_intensity": 0.75,
                    "explanation": "Пользователь выражает раздражение от неудач",
                    "recommendations": ["Проявить терпение, предложить помощь"],
                    "secondary_emotions": ["annoyance", "impatience"]
                })
            elif any(word in prompt_text.lower() for word in ["боюсь", "не успею", "сделать"]):
                return MockResult({
                    "primary_emotion": "anxious",
                    "confidence": 0.82,
                    "emotional_intensity": 0.7,
                    "explanation": "Пользователь выражает тревогу о сроках",
                    "recommendations": ["Успокоить, предложить план действий"],
                    "secondary_emotions": ["worry", "uncertainty"]
                })
            elif any(word in prompt_text.lower() for word in ["объясни", "не понял"]):
                return MockResult({
                    "primary_emotion": "confused",
                    "confidence": 0.88,
                    "emotional_intensity": 0.6,
                    "explanation": "Пользователь выражает замешательство",
                    "recommendations": ["Объяснить подробнее, использовать примеры"],
                    "secondary_emotions": ["uncertainty", "perplexity"]
                })
            elif any(word in prompt_text.lower() for word in ["жить", "одиноко", "не знаю"]):
                return MockResult({
                    "primary_emotion": "supportive_needed",
                    "confidence": 0.9,
                    "emotional_intensity": 0.85,
                    "explanation": "Пользователю нужна эмоциональная поддержка",
                    "recommendations": ["Проявить эмпатию, предложить помощь"],
                    "secondary_emotions": ["loneliness", "vulnerability"]
                })
            elif any(word in prompt_text.lower() for word in ["всё", "хватит", "не могу"]):
                return MockResult({
                    "primary_emotion": "angry",
                    "confidence": 0.92,
                    "emotional_intensity": 0.95,
                    "explanation": "Пользователь выражает гнев и раздражение",
                    "recommendations": ["Сохранять спокойствие, деэскалировать ситуацию"],
                    "secondary_emotions": ["frustration", "irritation"]
                })
            else:
                # Ответ по умолчанию для неизвестных запросов
                return MockResult({
                    "primary_emotion": "neutral",
                    "confidence": 0.5,
                    "emotional_intensity": 0.3,
                    "explanation": "Эмоциональный тон не определен",
                    "recommendations": ["Задать уточняющие вопросы"],
                    "secondary_emotions": []
                })
    
    # Создаем экземпляр классификатора с моковым роутером
    print("Создание экземпляра EmotionalClassifier...")
    try:
        classifier = EmotionalClassifier(ai_router=MockAIRouter())
        print("Классификатор успешно создан")
    except Exception as e:
        print(f"ОШИБКА при создании классификатора: {str(e)}")
        return False
    
    # Тестовые кейсы: (сообщение, ожидаемая эмоция, описание)
    test_cases = [
        ("Спасибо большое! Ты мне очень помог, я так рад!", 
         EmotionalState.POSITIVE, "Ярко выраженная радость"),
        
        ("Я в полном отчаянии... У меня ничего не получается", 
         EmotionalState.DEPRESSED, "Глубокое отчаяние"),
        
        ("Почему ничего не работает? Я уже сто раз пробовал!", 
         EmotionalState.FRUSTRATED, "Раздражение от неудач"),
        
        ("Боюсь, что не успею к сроку, столько всего нужно сделать...", 
         EmotionalState.ANXIOUS, "Тревога о сроках"),
        
        ("Объясни, пожалуйста, еще раз, я не совсем понял", 
         EmotionalState.CONFUSED, "Замешательство"),
        
        ("Я не знаю, как дальше жить, мне так одиноко...", 
         EmotionalState.SUPPORTIVE_NEEDED, "Потребность в поддержке"),
        
        ("ВСЁ! ХВАТИТ! Я больше так не могу!", 
         EmotionalState.ANGRY, "Ярость и гнев")
    ]
    
    # Запускаем тесты
    total = len(test_cases)
    passed = 0
    print(f"\nНайдено тестов: {total}")
    if total == 0:
        print("ОШИБКА: Не найдено тестов для выполнения!")
        return False
    
    for i, (message, expected_emotion, description) in enumerate(test_cases, 1):
        print(f"\nТЕСТ {i}/{total}: {description.upper()}")
        print("-" * 50)
        print(f"Сообщение: {message}")
        # Debug information
        print(f"Тест: {i}/{total} - {description}")
        print(f"Ожидаемая эмоция: {expected_emotion.value}")
        
        try:
            # Анализ эмоционального состояния
            analysis = classifier.analyze_emotional_state([], message)
            result = analysis.primary_emotion
            confidence = analysis.confidence
            
            print("\nРЕЗУЛЬТАТ:")
            print(f"- Эмоция: {result.value.upper()}")
            print(f"- Уверенность: {confidence:.1%}")
            print(f"- Интенсивность: {analysis.emotional_intensity:.1%}")
            if hasattr(analysis, 'explanation'):
                print(f"- Объяснение: {analysis.explanation}")
            
            # Проверка результата
            test_passed = result == expected_emotion
            
            if test_passed:
                print("\n✅ ВЕРНО: эмоция определена правильно")
                passed += 1
            else:
                print(f"\n❌ ОШИБКА: ожидалось {expected_emotion.value.upper()}")
            
            # Вывод рекомендаций, если они есть
            if hasattr(analysis, 'recommendations') and analysis.recommendations:
                print("\nРекомендации:")
                for rec in analysis.recommendations[:2]:
                    print(f"- {rec}")
                    
        except Exception as e:
            print(f"\nОШИБКА: {str(e)}")
    
    # Вывод итогов
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print("\n" + "="*50)
    print(f"ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"✅ Успешно: {passed} из {total}")
    print(f"❌ Ошибок: {total - passed} из {total}")
    print(f"📊 Успешность: {success_rate:.1f}%")
    
    if success_rate < 50:
        print("\n⚠️  Внимание: низкий процент успешных тестов!")
        print("Рекомендуется проверить ключевые слова и логику классификации.")
    
    print("\n" + "="*50)
    return success_rate >= 70


# Экспорты для использования в других модулях
__all__ = ['EmotionalClassifier', 'EmotionalState', 'EmotionalAnalysis']

if __name__ == "__main__":
    run_tests()
