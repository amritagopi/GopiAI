"""
Интеграция системы обратной связи со стратегиями исследования

Расширяет базовые стратегии исследования функциями для работы
с системой обратной связи.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union, Set, Tuple
import time

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationCollection, InformationItem,
    ExplorationPhase
)
from app.agent.web_exploration_strategy import WebExplorationStrategy
from app.agent.file_exploration_strategy import FileExplorationStrategy
from app.agent.feedback_system import (
    FeedbackManager, FeedbackType, FeedbackSource
)
from app.logger import logger


class FeedbackEnabledExplorationStrategy(ExplorationStrategy):
    """
    Базовый класс для стратегий исследования с поддержкой обратной связи.
    Расширяет базовый класс ExplorationStrategy.
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализирует стратегию с поддержкой обратной связи.
        """
        super().__init__(*args, **kwargs)

        # Инициализируем менеджер обратной связи
        self.feedback_manager = FeedbackManager()

        # Дополнительные атрибуты для мониторинга
        self.last_execution_time = 0.0
        self.last_query = ""
        self.last_collection = None
        self.adaptive_parameters = {}

    async def explore_with_feedback(self, query: str, **kwargs) -> InformationCollection:
        """
        Выполняет исследование с поддержкой обратной связи.

        Args:
            query: Текст запроса для исследования
            **kwargs: Дополнительные параметры

        Returns:
            Коллекция собранной информации
        """
        # Засекаем время начала
        start_time = time.time()

        # Сохраняем запрос для последующего анализа
        self.last_query = query

        # Применяем адаптивные параметры, если они есть
        exploration_kwargs = kwargs.copy()
        exploration_kwargs.update(self.get_adaptive_parameters(query))

        # Выполняем исследование с адаптивными параметрами
        collection = await self.explore(query, **exploration_kwargs)

        # Рассчитываем время выполнения
        execution_time = time.time() - start_time
        self.last_execution_time = execution_time

        # Сохраняем коллекцию для последующего анализа
        self.last_collection = collection

        # Генерируем автоматическую обратную связь
        self.feedback_manager.add_automatic_feedback(
            strategy_id=self.name,
            collection=collection,
            execution_time=execution_time,
            query=query
        )

        return collection

    async def process_results_with_feedback(
        self,
        collection: InformationCollection,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Обрабатывает результаты с учетом обратной связи.

        Args:
            collection: Коллекция собранной информации
            **kwargs: Дополнительные параметры

        Returns:
            Результаты обработки
        """
        # Обрабатываем результаты
        results = await self.process_results(collection, **kwargs)

        # Добавляем информацию о производительности
        performance = self.feedback_manager.get_strategy_performance(self.name)
        results["performance"] = performance

        # Добавляем рекомендации
        recommendations = self.feedback_manager.get_improvement_recommendations(self.name)
        results["recommendations"] = recommendations

        return results

    def get_adaptive_parameters(self, query: str) -> Dict[str, Any]:
        """
        Генерирует адаптивные параметры для стратегии на основе обратной связи.

        Args:
            query: Текст запроса

        Returns:
            Словарь с адаптивными параметрами
        """
        # По умолчанию возвращаем пустой словарь
        params = {}

        # Получаем производительность стратегии
        performance = self.feedback_manager.get_strategy_performance(self.name)
        metrics = performance.get("metrics", {})

        # Базовые параметры
        if self.adaptive_parameters:
            params = self.adaptive_parameters.copy()

        # На основе метрик адаптируем параметры
        # Это зависит от конкретной стратегии и будет переопределено в подклассах

        return params

    def apply_user_feedback(
        self,
        feedback_type: Union[FeedbackType, str],
        score: float,
        description: Optional[str] = None,
        exploration_id: Optional[str] = None
    ) -> str:
        """
        Применяет обратную связь от пользователя.

        Args:
            feedback_type: Тип обратной связи
            score: Оценка (0.0 - 1.0)
            description: Текстовое описание
            exploration_id: ID исследования (если отличается от последнего)

        Returns:
            ID добавленного элемента обратной связи
        """
        if exploration_id is None and self.last_collection is not None:
            exploration_id = self.last_collection.name

        return self.feedback_manager.add_user_feedback(
            strategy_id=self.name,
            feedback_type=feedback_type,
            score=score,
            description=description,
            exploration_id=exploration_id,
            metadata={"query": self.last_query}
        )

    def update_adaptive_parameters(self, parameters: Dict[str, Any]):
        """
        Обновляет адаптивные параметры стратегии.

        Args:
            parameters: Новые параметры
        """
        self.adaptive_parameters.update(parameters)

    def get_performance_history(self) -> Dict[str, Any]:
        """
        Получает историю производительности стратегии.

        Returns:
            Словарь с историей производительности
        """
        return {
            "strategy_id": self.name,
            "performance": self.feedback_manager.get_strategy_performance(self.name),
            "all_feedback": self.feedback_manager.get_all_feedback(self.name)
        }

    def add_agent_self_assessment(
        self,
        feedback_type: FeedbackType,
        score: float,
        description: str
    ) -> str:
        """
        Добавляет самооценку от агента.

        Args:
            feedback_type: Тип обратной связи
            score: Оценка (0.0 - 1.0)
            description: Текстовое описание

        Returns:
            ID добавленного элемента обратной связи
        """
        return self.feedback_manager.add_agent_feedback(
            strategy_id=self.name,
            feedback_type=feedback_type,
            score=score,
            description=description,
            exploration_id=self.last_collection.name if self.last_collection else None,
            metadata={
                "query": self.last_query,
                "execution_time": self.last_execution_time
            }
        )


class FeedbackEnabledWebExplorationStrategy(WebExplorationStrategy, FeedbackEnabledExplorationStrategy):
    """
    Расширение WebExplorationStrategy с поддержкой обратной связи.
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализирует стратегию веб-исследования с поддержкой обратной связи.
        """
        WebExplorationStrategy.__init__(self, *args, **kwargs)
        FeedbackEnabledExplorationStrategy.__init__(
            self,
            name=self.name,
            description=self.description,
            browser_access=self.browser_access,
            thought_tree=self.thought_tree,
            file_system=self.file_system,
            text_editor=self.text_editor
        )

    def get_adaptive_parameters(self, query: str) -> Dict[str, Any]:
        """
        Генерирует адаптивные параметры для веб-стратегии на основе обратной связи.

        Args:
            query: Текст запроса

        Returns:
            Словарь с адаптивными параметрами
        """
        params = super().get_adaptive_parameters(query)

        # Получаем производительность стратегии
        performance = self.feedback_manager.get_strategy_performance(self.name)
        metrics = performance.get("metrics", {})

        # Адаптируем параметры поиска на основе метрик

        # Полнота информации (completeness)
        completeness_score = metrics.get(FeedbackType.COMPLETENESS.value)
        if completeness_score is not None and completeness_score < 0.6:
            # Если оценка полноты низкая, увеличиваем количество страниц
            params["max_pages"] = min(15, self.max_pages + 5)
            params["max_depth"] = min(3, self.max_depth + 1)

        # Релевантность информации (relevance)
        relevance_score = metrics.get(FeedbackType.RELEVANCE.value)
        if relevance_score is not None and relevance_score < 0.6:
            # Если оценка релевантности низкая, меняем поисковую систему
            current_engine = self.default_search_engine
            params["search_engine"] = "DuckDuckGo" if current_engine == "Google" else "Google"

        # Эффективность (efficiency)
        efficiency_score = metrics.get(FeedbackType.EFFICIENCY.value)
        if efficiency_score is not None and efficiency_score < 0.4:
            # Если эффективность очень низкая, ограничиваем параметры поиска
            params["max_pages"] = max(3, self.max_pages - 2)
            params["search_timeout"] = max(10.0, self.search_timeout - 5.0)

        return params


class FeedbackEnabledFileExplorationStrategy(FileExplorationStrategy, FeedbackEnabledExplorationStrategy):
    """
    Расширение FileExplorationStrategy с поддержкой обратной связи.
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализирует стратегию исследования файловой системы с поддержкой обратной связи.
        """
        FileExplorationStrategy.__init__(self, *args, **kwargs)
        FeedbackEnabledExplorationStrategy.__init__(
            self,
            name=self.name,
            description=self.description,
            file_system=self.file_system,
            thought_tree=self.thought_tree,
            text_editor=self.text_editor
        )

    def get_adaptive_parameters(self, query: str) -> Dict[str, Any]:
        """
        Генерирует адаптивные параметры для стратегии файловой системы на основе обратной связи.

        Args:
            query: Текст запроса

        Returns:
            Словарь с адаптивными параметрами
        """
        params = super().get_adaptive_parameters(query)

        # Получаем производительность стратегии
        performance = self.feedback_manager.get_strategy_performance(self.name)
        metrics = performance.get("metrics", {})

        # Адаптируем параметры на основе метрик

        # Полнота информации (completeness)
        completeness_score = metrics.get(FeedbackType.COMPLETENESS.value)
        if completeness_score is not None and completeness_score < 0.6:
            # Если оценка полноты низкая, увеличиваем количество файлов
            params["max_files"] = min(30, self.max_files + 10)

            # Расширяем список расширений
            additional_extensions = [".json", ".xml", ".sql", ".sh", ".bat", ".cfg", ".ini"]

            if "extensions" not in params:
                params["extensions"] = self.default_extensions.copy()

            for ext in additional_extensions:
                if ext not in params["extensions"]:
                    params["extensions"].append(ext)

        # Релевантность информации (relevance)
        relevance_score = metrics.get(FeedbackType.RELEVANCE.value)
        if relevance_score is not None and relevance_score < 0.6:
            # Если оценка релевантности низкая, добавляем шаблон для поиска
            words = query.lower().split()
            pattern = "|".join(word for word in words if len(word) > 3)

            if pattern:
                params["pattern"] = pattern

        # Эффективность (efficiency)
        efficiency_score = metrics.get(FeedbackType.EFFICIENCY.value)
        if efficiency_score is not None and efficiency_score < 0.4:
            # Если эффективность очень низкая, ограничиваем параметры поиска
            params["max_files"] = max(5, self.max_files - 5)
            params["recursive"] = False

        return params
