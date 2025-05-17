"""
Модуль адаптации к предыдущему опыту для Reasoning Agent

Обеспечивает механизмы для анализа и применения накопленного опыта
для улучшения принятия решений и избегания повторения ошибок.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math

from app.agent.personalization_manager import PersonalizationManager
from app.agent.error_manager import ErrorManager
from app.agent.experience_manager import ExperienceArchive
from app.agent.metacognitive_analyzer import MetacognitiveAnalyzer
from app.config.reasoning_config import ReasoningStrategy
from app.logger import logger


@dataclass
class SimilarExperience:
    """Класс для представления похожего опыта"""
    similarity_score: float
    task: str
    approach: str
    result: str
    timestamp: datetime
    success: bool
    source_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationSuggestion:
    """Класс для представления предложений адаптации"""
    suggestion_type: str
    suggestion: str
    confidence: float
    source: str
    reasoning: str
    applies_to: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExperienceAdapter:
    """
    Класс для адаптации поведения агента на основе предыдущего опыта.

    Анализирует предыдущий опыт для:
    1. Предотвращения повторения прошлых ошибок
    2. Оптимизации выбора стратегий для похожих задач
    3. Адаптации параметров планирования
    4. Предложения решений на основе похожих задач
    """

    def __init__(self,
                personalization_manager: Optional[PersonalizationManager] = None,
                error_manager: Optional[ErrorManager] = None,
                experience_archive: Optional[ExperienceArchive] = None,
                metacognitive_analyzer: Optional[MetacognitiveAnalyzer] = None):
        """
        Инициализирует адаптер опыта.

        Args:
            personalization_manager: Менеджер персонализации
            error_manager: Менеджер ошибок
            experience_archive: Архив опыта
            metacognitive_analyzer: Метакогнитивный анализатор
        """
        self.personalization_manager = personalization_manager
        self.error_manager = error_manager
        self.experience_archive = experience_archive
        self.metacognitive_analyzer = metacognitive_analyzer

        # Кэш для хранения извлеченных паттернов
        self._pattern_cache: Dict[str, Any] = {}
        self._cache_timestamp = datetime.now()
        self._cache_ttl = timedelta(minutes=30)  # Время жизни кэша

        logger.info("ExperienceAdapter: инициализирован адаптер опыта")

    def invalidate_cache(self) -> None:
        """Инвалидирует кэш паттернов"""
        self._pattern_cache = {}
        self._cache_timestamp = datetime.now()
        logger.info("ExperienceAdapter: кэш паттернов очищен")

    async def analyze_current_task(self, task: str) -> List[AdaptationSuggestion]:
        """
        Анализирует текущую задачу и предлагает адаптации на основе опыта.

        Args:
            task: Текущая задача

        Returns:
            Список предложений по адаптации
        """
        suggestions = []

        # Если кэш устарел, обновляем его
        if datetime.now() - self._cache_timestamp > self._cache_ttl:
            logger.info("ExperienceAdapter: обновление кэша паттернов")
            await self._update_pattern_cache()

        # Находим похожие задачи в накопленном опыте
        similar_experiences = await self._find_similar_experiences(task)

        if similar_experiences:
            # Если найдены похожие задачи, анализируем их для предложений
            strategy_suggestion = self._suggest_best_strategy(task, similar_experiences)
            if strategy_suggestion:
                suggestions.append(strategy_suggestion)

            # Предложения по предотвращению ошибок
            error_suggestions = self._suggest_error_prevention(task, similar_experiences)
            suggestions.extend(error_suggestions)

            # Предложения по оптимизации планирования
            planning_suggestion = self._suggest_planning_optimizations(task, similar_experiences)
            if planning_suggestion:
                suggestions.append(planning_suggestion)

            # Предложения по подходу к решению
            approach_suggestion = self._suggest_approach(task, similar_experiences)
            if approach_suggestion:
                suggestions.append(approach_suggestion)

        # Добавляем предложения на основе анализа ошибок
        if self.error_manager:
            error_patterns = self._get_error_patterns_for_task(task)
            for pattern in error_patterns:
                prevention_suggestion = AdaptationSuggestion(
                    suggestion_type="error_prevention",
                    suggestion=f"Избегайте {pattern['error_pattern']} - используйте {pattern['suggested_solution']}",
                    confidence=pattern.get("confidence", 0.7),
                    source="error_analysis",
                    reasoning=f"Основано на анализе {pattern.get('occurrence_count', 0)} похожих ошибок"
                )
                suggestions.append(prevention_suggestion)

        # Добавляем предложения на основе персонализации
        if self.personalization_manager:
            personalized_approach = self._get_personalized_approach(task)
            if personalized_approach:
                personalization_suggestion = AdaptationSuggestion(
                    suggestion_type="personalization",
                    suggestion=personalized_approach["suggestion"],
                    confidence=personalized_approach.get("confidence", 0.8),
                    source="personalization",
                    reasoning="Основано на предпочтениях пользователя и истории взаимодействий"
                )
                suggestions.append(personalization_suggestion)

        # Сортируем предложения по уверенности
        suggestions.sort(key=lambda x: x.confidence, reverse=True)

        logger.info(f"ExperienceAdapter: предложено {len(suggestions)} адаптаций для задачи")
        return suggestions

    async def adapt_planning_parameters(self, task: str) -> Dict[str, Any]:
        """
        Адаптирует параметры планирования на основе предыдущего опыта.

        Args:
            task: Текущая задача

        Returns:
            Словарь с адаптированными параметрами планирования
        """
        # Базовые параметры планирования
        default_params = {
            "strategy": ReasoningStrategy.ADAPTIVE.value,
            "max_depth": 7,
            "risk_threshold": 0.5,
            "detail_level": 0.6,
            "allow_parallelization": False,
            "adapted": False
        }

        # Если нет компонентов для адаптации, возвращаем стандартные параметры
        if not self.personalization_manager and not self.metacognitive_analyzer:
            return default_params

        try:
            # Получаем предложения адаптации
            suggestions = await self.analyze_current_task(task)

            # Если нет предложений, возвращаем стандартные параметры
            if not suggestions:
                return default_params

            # Адаптируем параметры на основе предложений
            params = default_params.copy()
            params["adapted"] = True

            # Обрабатываем предложения по стратегии
            strategy_suggestions = [s for s in suggestions if s.suggestion_type == "strategy"]
            if strategy_suggestions:
                best_strategy = strategy_suggestions[0]
                strategy_mapping = {
                    "последовательная": ReasoningStrategy.SEQUENTIAL.value,
                    "древовидная": ReasoningStrategy.TREE.value,
                    "адаптивная": ReasoningStrategy.ADAPTIVE.value
                }

                for strategy_name, strategy_value in strategy_mapping.items():
                    if strategy_name in best_strategy.suggestion.lower():
                        params["strategy"] = strategy_value
                        break

            # Обрабатываем предложения по планированию
            planning_suggestions = [s for s in suggestions if s.suggestion_type == "planning"]
            if planning_suggestions:
                planning_suggestion = planning_suggestions[0]

                # Адаптируем глубину планирования
                if "глубина" in planning_suggestion.suggestion.lower():
                    # Извлекаем числовое значение из предложения
                    for word in planning_suggestion.suggestion.split():
                        if word.isdigit():
                            depth = int(word)
                            if 3 <= depth <= 15:  # Проверяем разумные пределы
                                params["max_depth"] = depth

                # Адаптируем уровень детализации
                if "детализац" in planning_suggestion.suggestion.lower():
                    if "высок" in planning_suggestion.suggestion.lower():
                        params["detail_level"] = 0.8
                    elif "низк" in planning_suggestion.suggestion.lower():
                        params["detail_level"] = 0.3

                # Адаптируем порог риска
                if "риск" in planning_suggestion.suggestion.lower():
                    if "низк" in planning_suggestion.suggestion.lower():
                        params["risk_threshold"] = 0.3
                    elif "высок" in planning_suggestion.suggestion.lower():
                        params["risk_threshold"] = 0.7

                # Адаптируем параллелизацию
                if "параллел" in planning_suggestion.suggestion.lower():
                    params["allow_parallelization"] = True

            # Если есть менеджер персонализации, учитываем предпочтения пользователя
            if self.personalization_manager:
                active_profile = self.personalization_manager.get_active_profile()
                if active_profile:
                    # Адаптируем уровень детализации на основе предпочтений
                    detailed_planning = active_profile.get_preference("detailed_planning", 0.5)
                    params["detail_level"] = (params["detail_level"] + detailed_planning) / 2

                    # Адаптируем порог риска на основе толерантности к риску
                    risk_tolerance = active_profile.get_preference("risk_tolerance", 0.3)
                    params["risk_threshold"] = (params["risk_threshold"] + risk_tolerance) / 2

            logger.info(f"ExperienceAdapter: параметры планирования адаптированы: {params}")
            return params

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка адаптации параметров планирования: {str(e)}")
            return default_params

    async def get_improved_solution(self, task: str, initial_solution: str) -> Optional[Dict[str, Any]]:
        """
        Пытается улучшить начальное решение на основе предыдущего опыта.

        Args:
            task: Текущая задача
            initial_solution: Начальное решение

        Returns:
            Словарь с улучшенным решением или None, если улучшение невозможно
        """
        if not self.experience_archive and not self.error_manager:
            return None

        try:
            # Находим похожие задачи
            similar_experiences = await self._find_similar_experiences(task)

            # Если нет похожих задач, возвращаем None
            if not similar_experiences:
                return None

            # Находим успешные решения для похожих задач
            successful_solutions = [
                exp for exp in similar_experiences
                if exp.success and exp.similarity_score > 0.6
            ]

            if not successful_solutions:
                return None

            # Выбираем наиболее похожее решение
            best_solution = max(successful_solutions, key=lambda x: x.similarity_score)

            # Проверяем, действительно ли решение лучше начального
            if self._is_significantly_better(best_solution.approach, initial_solution):
                # Создаем обновленное решение, сохраняя контекст начального
                improved_solution = self._merge_solutions(initial_solution, best_solution.approach)

                return {
                    "improved_solution": improved_solution,
                    "source_task": best_solution.task,
                    "similarity_score": best_solution.similarity_score,
                    "has_improvement": True,
                    "reasoning": f"Решение улучшено на основе опыта с задачей: {best_solution.task}"
                }

            return {
                "improved_solution": initial_solution,
                "has_improvement": False,
                "reasoning": "Текущее решение уже оптимально на основе предыдущего опыта"
            }

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при попытке улучшить решение: {str(e)}")
            return None

    async def get_error_prevention_tips(self, task: str, approach: str) -> List[Dict[str, Any]]:
        """
        Возвращает советы по предотвращению ошибок для задачи и подхода.

        Args:
            task: Текущая задача
            approach: Выбранный подход к решению

        Returns:
            Список советов по предотвращению ошибок
        """
        if not self.error_manager:
            return []

        try:
            # Получаем паттерны ошибок для задачи
            error_patterns = self._get_error_patterns_for_task(task)

            # Фильтруем паттерны, которые применимы к текущему подходу
            applicable_patterns = []

            for pattern in error_patterns:
                # Проверяем, применим ли паттерн к текущему подходу
                if any(trigger in approach.lower() for trigger in pattern.get("triggers", [])):
                    applicable_patterns.append({
                        "error_type": pattern.get("error_type", "Неизвестная ошибка"),
                        "prevention_tip": pattern.get("suggested_solution", "Будьте внимательны"),
                        "confidence": pattern.get("confidence", 0.5),
                        "reasoning": f"Основано на анализе {pattern.get('occurrence_count', 0)} похожих ошибок",
                        "potential_impact": pattern.get("impact", "medium")
                    })

            # Добавляем общие советы по предотвращению ошибок
            generic_tips = self._get_generic_error_prevention_tips(task)
            applicable_patterns.extend(generic_tips)

            # Сортируем советы по уверенности
            applicable_patterns.sort(key=lambda x: x.get("confidence", 0), reverse=True)

            return applicable_patterns

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при получении советов по предотвращению ошибок: {str(e)}")
            return []

    async def _update_pattern_cache(self) -> None:
        """
        Обновляет кэш паттернов из всех источников опыта.
        """
        self._pattern_cache = {}

        # Извлекаем паттерны из архивов опыта, если доступны
        if self.experience_archive:
            try:
                archives = self.experience_archive.list_archives()

                for archive_info in archives[:5]:  # Берем не более 5 последних архивов
                    stats = self.experience_archive.extract_aggregate_statistics(archive_info["path"])

                    if "profiles" in stats and "preferences" in stats["profiles"]:
                        preferences = stats["profiles"]["preferences"]
                        self._pattern_cache["preferences"] = self._pattern_cache.get("preferences", {})
                        self._pattern_cache["preferences"].update(preferences)

                    if "profiles" in stats and "top_tasks" in stats["profiles"]:
                        tasks = stats["profiles"]["top_tasks"]
                        self._pattern_cache["tasks"] = self._pattern_cache.get("tasks", {})
                        for task, count in tasks.items():
                            self._pattern_cache["tasks"][task] = self._pattern_cache["tasks"].get(task, 0) + count
            except Exception as e:
                logger.error(f"ExperienceAdapter: ошибка при обновлении паттернов из архивов: {str(e)}")

        # Извлекаем паттерны ошибок, если доступен менеджер ошибок
        if self.error_manager:
            try:
                error_patterns = self.error_manager.detect_error_patterns()
                self._pattern_cache["error_patterns"] = error_patterns
            except Exception as e:
                logger.error(f"ExperienceAdapter: ошибка при обновлении паттернов ошибок: {str(e)}")

        # Извлекаем рекомендации по стратегиям, если доступен метакогнитивный анализатор
        if self.metacognitive_analyzer:
            try:
                for strategy_type in [
                    ReasoningStrategy.SEQUENTIAL,
                    ReasoningStrategy.TREE,
                    ReasoningStrategy.ADAPTIVE
                ]:
                    recommendations = self.metacognitive_analyzer.get_common_recommendations(
                        strategy_type=strategy_type,
                        limit=5
                    )

                    self._pattern_cache["strategy_recommendations"] = self._pattern_cache.get(
                        "strategy_recommendations", {}
                    )
                    self._pattern_cache["strategy_recommendations"][strategy_type.value] = recommendations
            except Exception as e:
                logger.error(f"ExperienceAdapter: ошибка при обновлении рекомендаций по стратегиям: {str(e)}")

        # Обновляем временную метку кэша
        self._cache_timestamp = datetime.now()
        logger.info("ExperienceAdapter: кэш паттернов обновлен")

    async def _find_similar_experiences(self, task: str) -> List[SimilarExperience]:
        """
        Находит похожий опыт для заданной задачи.

        Args:
            task: Текущая задача

        Returns:
            Список похожего опыта
        """
        similar_experiences = []

        # Если не активны ни менеджер персонализации, ни архив опыта, возвращаем пустой список
        if not self.personalization_manager and not self.experience_archive:
            return similar_experiences

        try:
            # Если есть активный профиль, извлекаем похожие задачи
            if self.personalization_manager:
                active_profile = self.personalization_manager.get_active_profile()
                if active_profile:
                    # Ищем похожие задачи в истории взаимодействий
                    task_words = set(task.lower().split())

                    for interaction in active_profile.recent_interactions:
                        content = interaction.content.lower()
                        content_words = set(content.split())

                        # Вычисляем сходство задач по словам
                        common_words = task_words.intersection(content_words)
                        if len(common_words) >= 3:
                            similarity = len(common_words) / math.sqrt(len(task_words) * len(content_words))

                            # Если сходство достаточно высокое, добавляем опыт
                            if similarity > 0.4:
                                experience = SimilarExperience(
                                    similarity_score=similarity,
                                    task=interaction.content,
                                    approach=interaction.metadata.get("approach", ""),
                                    result=interaction.metadata.get("result", ""),
                                    timestamp=interaction.timestamp,
                                    success=interaction.success,
                                    source_id="personalization",
                                    metadata=interaction.metadata
                                )
                                similar_experiences.append(experience)

            # Если есть архив опыта, анализируем архивы
            if self.experience_archive:
                # Получаем список архивов
                archives = self.experience_archive.list_archives()

                # Для демонстрационных целей анализируем только последний архив
                if archives:
                    # Извлекаем информацию из архива
                    archive_info = archives[0]
                    stats = self.experience_archive.extract_aggregate_statistics(archive_info["path"])

                    # Если в архиве есть частые задачи, сравниваем их с текущей
                    if "profiles" in stats and "top_tasks" in stats["profiles"]:
                        tasks = stats["profiles"]["top_tasks"]

                        for archive_task, _ in tasks.items():
                            # Вычисляем сходство с архивной задачей
                            archive_task_words = set(archive_task.lower().split())
                            task_words = set(task.lower().split())

                            common_words = task_words.intersection(archive_task_words)
                            if len(common_words) >= 2:
                                similarity = len(common_words) / math.sqrt(len(task_words) * len(archive_task_words))

                                if similarity > 0.3:
                                    experience = SimilarExperience(
                                        similarity_score=similarity,
                                        task=archive_task,
                                        approach="",  # Нет данных о подходе в архиве
                                        result="",    # Нет данных о результате в архиве
                                        timestamp=datetime.fromisoformat(archive_info["created"]),
                                        success=True, # Предполагаем успех для задач из архива
                                        source_id="archive",
                                        metadata={"archive_name": archive_info["filename"]}
                                    )
                                    similar_experiences.append(experience)

            # Сортируем результаты по убыванию сходства
            similar_experiences.sort(key=lambda x: x.similarity_score, reverse=True)

            # Возвращаем наиболее релевантные результаты
            return similar_experiences[:5]

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при поиске похожего опыта: {str(e)}")
            return []

    def _suggest_best_strategy(self, task: str, similar_experiences: List[SimilarExperience]) -> Optional[AdaptationSuggestion]:
        """
        Предлагает наилучшую стратегию для задачи на основе похожего опыта.

        Args:
            task: Текущая задача
            similar_experiences: Список похожего опыта

        Returns:
            Предложение адаптации стратегии или None
        """
        if not similar_experiences or not self.metacognitive_analyzer:
            return None

        try:
            # Получаем рекомендации по стратегиям из кэша
            strategy_recommendations = self._pattern_cache.get("strategy_recommendations", {})

            # Если нет рекомендаций, используем предопределенные стратегии
            if not strategy_recommendations:
                # Определяем стратегию на основе сложности задачи (по количеству слов)
                task_complexity = len(task.split())

                if task_complexity < 10:
                    strategy_name = "последовательная"
                    reasoning = "Простая задача требует последовательного подхода"
                elif task_complexity > 20:
                    strategy_name = "древовидная"
                    reasoning = "Сложная задача требует рассмотрения альтернативных путей"
                else:
                    strategy_name = "адаптивная"
                    reasoning = "Задача средней сложности подходит для адаптивной стратегии"

                return AdaptationSuggestion(
                    suggestion_type="strategy",
                    suggestion=f"Используйте {strategy_name} стратегию для данной задачи",
                    confidence=0.6,
                    source="heuristic",
                    reasoning=reasoning
                )

            # Анализируем успешные опыты для определения лучшей стратегии
            strategy_scores = {
                "sequential": 0.0,
                "tree": 0.0,
                "adaptive": 0.0
            }

            # Подсчитываем веса для каждой стратегии на основе похожего опыта
            for experience in similar_experiences:
                if experience.success:
                    # Определяем стратегию из метаданных или по содержанию
                    strategy = experience.metadata.get("strategy", "").lower()

                    if not strategy:
                        # Пытаемся определить стратегию по содержанию задачи
                        if "альтернатив" in experience.task.lower() or "ветвлени" in experience.task.lower():
                            strategy = "tree"
                        elif "последовательн" in experience.task.lower() or "шаг за шагом" in experience.task.lower():
                            strategy = "sequential"
                        else:
                            strategy = "adaptive"

                    # Добавляем вес стратегии на основе схожести опыта
                    if strategy in strategy_scores:
                        strategy_scores[strategy] += experience.similarity_score
                    elif strategy in ["последовательная", "последовательный"]:
                        strategy_scores["sequential"] += experience.similarity_score
                    elif strategy in ["древовидная", "древовидный"]:
                        strategy_scores["tree"] += experience.similarity_score

            # Выбираем стратегию с наибольшим весом
            best_strategy = max(strategy_scores, key=strategy_scores.get)

            # Сопоставляем с русскими названиями
            strategy_names = {
                "sequential": "последовательная",
                "tree": "древовидная",
                "adaptive": "адаптивная"
            }

            # Формируем обоснование
            strategy_name = strategy_names.get(best_strategy, best_strategy)
            confidence = min(0.9, 0.5 + strategy_scores[best_strategy])

            return AdaptationSuggestion(
                suggestion_type="strategy",
                suggestion=f"Используйте {strategy_name} стратегию планирования для данной задачи",
                confidence=confidence,
                source="experience_analysis",
                reasoning=f"Основано на анализе {len(similar_experiences)} похожих задач с общей схожестью {sum(e.similarity_score for e in similar_experiences):.2f}"
            )

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при предложении стратегии: {str(e)}")
            return None

    def _suggest_error_prevention(self, task: str, similar_experiences: List[SimilarExperience]) -> List[AdaptationSuggestion]:
        """
        Предлагает меры для предотвращения ошибок на основе похожего опыта.

        Args:
            task: Текущая задача
            similar_experiences: Список похожего опыта

        Returns:
            Список предложений для предотвращения ошибок
        """
        suggestions = []

        if not similar_experiences:
            return suggestions

        try:
            # Анализируем неуспешные опыты для определения возможных ошибок
            failed_experiences = [exp for exp in similar_experiences if not exp.success]

            for experience in failed_experiences:
                # Если есть информация об ошибке, формируем предложение
                error_info = experience.metadata.get("error", "")
                if error_info:
                    # Формируем предложение по предотвращению ошибки
                    suggestion = AdaptationSuggestion(
                        suggestion_type="error_prevention",
                        suggestion=f"Избегайте ошибки: {error_info}",
                        confidence=0.7 * experience.similarity_score,
                        source="similar_experience",
                        reasoning=f"Основано на похожей задаче: {experience.task}"
                    )
                    suggestions.append(suggestion)

            # Если есть данные из анализа ошибок, используем их
            error_patterns = self._pattern_cache.get("error_patterns", [])
            task_words = set(task.lower().split())

            for pattern in error_patterns:
                # Проверяем, применим ли паттерн к текущей задаче
                pattern_words = set(pattern.get("context", "").lower().split())
                common_words = task_words.intersection(pattern_words)

                if common_words and len(common_words) >= 2:
                    similarity = len(common_words) / math.sqrt(len(task_words) * len(pattern_words))

                    if similarity > 0.3:
                        suggestion = AdaptationSuggestion(
                            suggestion_type="error_prevention",
                            suggestion=f"Предотвратите ошибку: {pattern.get('error_pattern', '')} - {pattern.get('suggested_solution', '')}",
                            confidence=0.6 * similarity,
                            source="error_patterns",
                            reasoning=f"Основано на анализе {pattern.get('occurrence_count', 0)} похожих ошибок"
                        )
                        suggestions.append(suggestion)

            return suggestions

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при предложении мер по предотвращению ошибок: {str(e)}")
            return []

    def _suggest_planning_optimizations(self, task: str, similar_experiences: List[SimilarExperience]) -> Optional[AdaptationSuggestion]:
        """
        Предлагает оптимизации для планирования на основе похожего опыта.

        Args:
            task: Текущая задача
            similar_experiences: Список похожего опыта

        Returns:
            Предложение по оптимизации планирования или None
        """
        if not similar_experiences:
            return None

        try:
            # Анализируем успешные опыты для определения оптимальных параметров
            successful = [exp for exp in similar_experiences if exp.success]

            if not successful:
                return None

            # Определяем средние значения параметров из метаданных
            depth_values = []
            detail_levels = []
            risk_thresholds = []

            for exp in successful:
                if "max_depth" in exp.metadata:
                    depth_values.append(exp.metadata["max_depth"])

                if "detail_level" in exp.metadata:
                    detail_levels.append(exp.metadata["detail_level"])

                if "risk_threshold" in exp.metadata:
                    risk_thresholds.append(exp.metadata["risk_threshold"])

            # Формируем предложение на основе собранных данных
            suggestion_parts = []

            if depth_values:
                avg_depth = sum(depth_values) / len(depth_values)
                suggestion_parts.append(f"глубина планирования {int(avg_depth)}")

            if detail_levels:
                avg_detail = sum(detail_levels) / len(detail_levels)
                detail_text = "высокая детализация" if avg_detail > 0.7 else (
                    "низкая детализация" if avg_detail < 0.4 else "средняя детализация"
                )
                suggestion_parts.append(detail_text)

            if risk_thresholds:
                avg_risk = sum(risk_thresholds) / len(risk_thresholds)
                risk_text = "высокий порог риска" if avg_risk > 0.7 else (
                    "низкий порог риска" if avg_risk < 0.4 else "средний порог риска"
                )
                suggestion_parts.append(risk_text)

            if not suggestion_parts:
                return None

            suggestion_text = "Используйте " + ", ".join(suggestion_parts)

            return AdaptationSuggestion(
                suggestion_type="planning",
                suggestion=suggestion_text,
                confidence=0.7,
                source="experience_analysis",
                reasoning=f"Основано на анализе {len(successful)} успешных похожих задач"
            )

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при предложении оптимизаций планирования: {str(e)}")
            return None

    def _suggest_approach(self, task: str, similar_experiences: List[SimilarExperience]) -> Optional[AdaptationSuggestion]:
        """
        Предлагает подход к решению задачи на основе похожего опыта.

        Args:
            task: Текущая задача
            similar_experiences: Список похожего опыта

        Returns:
            Предложение по подходу к решению или None
        """
        if not similar_experiences:
            return None

        try:
            # Выбираем наиболее похожий успешный опыт
            successful = [exp for exp in similar_experiences if exp.success]

            if not successful:
                return None

            best_experience = max(successful, key=lambda x: x.similarity_score)

            # Если есть данные о подходе, формируем предложение
            if best_experience.approach:
                return AdaptationSuggestion(
                    suggestion_type="approach",
                    suggestion=f"Используйте подход: {best_experience.approach}",
                    confidence=best_experience.similarity_score,
                    source="similar_experience",
                    reasoning=f"Основано на успешной похожей задаче: {best_experience.task}"
                )

            return None

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при предложении подхода: {str(e)}")
            return None

    def _get_error_patterns_for_task(self, task: str) -> List[Dict[str, Any]]:
        """
        Возвращает паттерны ошибок, применимые к задаче.

        Args:
            task: Текущая задача

        Returns:
            Список паттернов ошибок
        """
        if not self.error_manager:
            return []

        try:
            # Получаем паттерны ошибок из кэша или из менеджера ошибок
            if "error_patterns" in self._pattern_cache:
                error_patterns = self._pattern_cache["error_patterns"]
            else:
                error_patterns = self.error_manager.detect_error_patterns()
                self._pattern_cache["error_patterns"] = error_patterns

            # Фильтруем паттерны, применимые к задаче
            task_words = set(task.lower().split())
            applicable_patterns = []

            for pattern in error_patterns:
                # Проверяем, применим ли паттерн к текущей задаче
                context = pattern.get("context", "").lower()
                context_words = set(context.split())
                common_words = task_words.intersection(context_words)

                # Если есть общие слова или контекст пустой, добавляем паттерн
                if common_words or not context:
                    applicable_patterns.append(pattern)

            return applicable_patterns

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при получении паттернов ошибок: {str(e)}")
            return []

    def _get_personalized_approach(self, task: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает персонализированный подход к задаче.

        Args:
            task: Текущая задача

        Returns:
            Словарь с персонализированным подходом или None
        """
        if not self.personalization_manager:
            return None

        try:
            # Получаем активный профиль
            active_profile = self.personalization_manager.get_active_profile()
            if not active_profile:
                return None

            # Анализируем задачу через менеджер персонализации
            task_analysis = self.personalization_manager.analyze_task(task)

            if not task_analysis.get("personalized", False):
                return None

            # Формируем персонализированный подход
            approach_parts = []

            # Добавляем рекомендации по подходу
            recommended_approach = task_analysis.get("recommended_approach")
            if recommended_approach:
                if recommended_approach == "rapid_prototyping":
                    approach_parts.append("быстрое прототипирование")
                elif recommended_approach == "thorough_analysis":
                    approach_parts.append("тщательный анализ")
                elif recommended_approach == "diagnostic":
                    approach_parts.append("диагностический подход")

            # Учитываем уровень детализации
            detail_level = task_analysis.get("detail_level")
            if detail_level:
                if detail_level == "high":
                    approach_parts.append("высокий уровень детализации")
                elif detail_level == "low":
                    approach_parts.append("низкий уровень детализации")

            # Учитываем основные домены пользователя
            domains = task_analysis.get("domains", [])
            if domains:
                # Добавляем специфику домена
                domain_mapping = {
                    "web_development": "веб-разработка",
                    "data_science": "анализ данных",
                    "devops": "DevOps",
                    "artificial_intelligence": "искусственный интеллект"
                }

                for domain in domains[:1]:  # Берем только первый домен
                    if domain in domain_mapping:
                        approach_parts.append(f"учитывая специфику {domain_mapping[domain]}")

            if not approach_parts:
                return None

            # Формируем персонализированное предложение
            suggestion = "Используйте " + ", ".join(approach_parts)

            return {
                "suggestion": suggestion,
                "confidence": 0.8,
                "task_type": task_analysis.get("task_type"),
                "domains": domains
            }

        except Exception as e:
            logger.error(f"ExperienceAdapter: ошибка при получении персонализированного подхода: {str(e)}")
            return None

    def _get_generic_error_prevention_tips(self, task: str) -> List[Dict[str, Any]]:
        """
        Возвращает общие советы по предотвращению ошибок.

        Args:
            task: Текущая задача

        Returns:
            Список общих советов
        """
        # Определяем тип задачи по ключевым словам
        task_lower = task.lower()

        # Советы по типам задач
        tips = []

        if any(word in task_lower for word in ["файл", "чтение", "запись", "открыть"]):
            tips.append({
                "error_type": "Ошибка доступа к файлу",
                "prevention_tip": "Всегда проверяйте существование файла перед чтением и наличие прав доступа",
                "confidence": 0.7,
                "reasoning": "Общая рекомендация для операций с файлами",
                "potential_impact": "high"
            })

        if any(word in task_lower for word in ["команда", "терминал", "bash", "shell"]):
            tips.append({
                "error_type": "Ошибка выполнения команды",
                "prevention_tip": "Обрабатывайте все коды возврата команд и используйте таймауты для долгих операций",
                "confidence": 0.7,
                "reasoning": "Общая рекомендация для операций с терминалом",
                "potential_impact": "medium"
            })

        if any(word in task_lower for word in ["api", "запрос", "http", "rest"]):
            tips.append({
                "error_type": "Ошибка API",
                "prevention_tip": "Обрабатывайте ошибки сети и проверяйте структуру ответа API",
                "confidence": 0.7,
                "reasoning": "Общая рекомендация для работы с API",
                "potential_impact": "high"
            })

        return tips

    def _is_significantly_better(self, proposed_solution: str, initial_solution: str) -> bool:
        """
        Определяет, существенно ли лучше предлагаемое решение.

        Args:
            proposed_solution: Предлагаемое решение
            initial_solution: Начальное решение

        Returns:
            True, если предлагаемое решение существенно лучше
        """
        # Простая эвристическая оценка - если решение длиннее и имеет мало общего
        if not proposed_solution or not initial_solution:
            return False

        # Если предлагаемое решение значительно длиннее, считаем его лучше
        if len(proposed_solution) > len(initial_solution) * 1.5:
            return True

        # Вычисляем сходство решений
        proposed_words = set(proposed_solution.lower().split())
        initial_words = set(initial_solution.lower().split())

        # Если решения очень похожи, предлагаемое не лучше
        common_words = proposed_words.intersection(initial_words)
        similarity = len(common_words) / max(len(proposed_words), len(initial_words))

        # Если решения не очень похожи, предлагаемое может быть лучше
        return similarity < 0.5

    def _merge_solutions(self, initial_solution: str, improved_parts: str) -> str:
        """
        Объединяет начальное решение с улучшенными частями.

        Args:
            initial_solution: Начальное решение
            improved_parts: Улучшенные части

        Returns:
            Объединенное решение
        """
        # Пока просто возвращаем улучшенные части, так как полное объединение сложно
        # В реальной реализации нужен более сложный алгоритм
        return improved_parts
