"""
Система обратной связи для улучшения стратегий исследования

Предоставляет механизмы для сбора, анализа и использования обратной связи
для улучшения стратегий исследования.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple
import json
import time
import os
from enum import Enum

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationCollection, InformationItem
)
from app.logger import logger


class FeedbackType(Enum):
    """Типы обратной связи"""
    RELEVANCE = "relevance"         # Релевантность найденной информации
    COMPLETENESS = "completeness"   # Полнота найденной информации
    EFFICIENCY = "efficiency"       # Эффективность стратегии
    ACCURACY = "accuracy"           # Точность найденной информации
    USABILITY = "usability"         # Удобство использования результатов
    OTHER = "other"                 # Другие типы обратной связи


class FeedbackSource(Enum):
    """Источники обратной связи"""
    USER = "user"                 # Пользователь
    AUTOMATIC = "automatic"       # Автоматическая оценка
    SYSTEM = "system"             # Системные метрики
    AGENT = "agent"               # Самооценка агента
    OTHER = "other"               # Другие источники


class FeedbackItem:
    """
    Класс для представления элемента обратной связи для стратегии.
    """

    def __init__(
        self,
        strategy_id: str,
        feedback_type: FeedbackType,
        score: float,
        source: FeedbackSource,
        description: Optional[str] = None,
        exploration_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует элемент обратной связи.

        Args:
            strategy_id: Идентификатор стратегии
            feedback_type: Тип обратной связи
            score: Оценка (0.0 - 1.0)
            source: Источник обратной связи
            description: Текстовое описание обратной связи
            exploration_id: Идентификатор конкретного исследования
            metadata: Дополнительные метаданные
        """
        self.id = f"feedback_{int(time.time())}_{id(self)}"
        self.strategy_id = strategy_id
        self.feedback_type = feedback_type
        self.score = max(0.0, min(1.0, score))  # Ограничение 0-1
        self.source = source
        self.description = description
        self.exploration_id = exploration_id
        self.metadata = metadata or {}
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует элемент обратной связи в словарь.

        Returns:
            Словарь с данными элемента обратной связи
        """
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "feedback_type": self.feedback_type.value,
            "score": self.score,
            "source": self.source.value,
            "description": self.description,
            "exploration_id": self.exploration_id,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackItem":
        """
        Создает элемент обратной связи из словаря.

        Args:
            data: Словарь с данными элемента обратной связи

        Returns:
            Созданный элемент обратной связи
        """
        feedback_type = FeedbackType(data["feedback_type"])
        source = FeedbackSource(data["source"])

        item = cls(
            strategy_id=data["strategy_id"],
            feedback_type=feedback_type,
            score=data["score"],
            source=source,
            description=data.get("description"),
            exploration_id=data.get("exploration_id"),
            metadata=data.get("metadata", {})
        )

        # Восстанавливаем ID и временную метку
        item.id = data.get("id", item.id)
        item.created_at = data.get("created_at", item.created_at)

        return item


class FeedbackStorage:
    """
    Класс для хранения и управления обратной связью по стратегиям.
    """

    def __init__(self, feedback_dir: str = "data/feedback"):
        """
        Инициализирует хранилище обратной связи.

        Args:
            feedback_dir: Директория для сохранения данных обратной связи
        """
        self.feedback_dir = feedback_dir
        self.feedback_items: Dict[str, FeedbackItem] = {}

        # Создаем директорию, если не существует
        os.makedirs(feedback_dir, exist_ok=True)

    def add_feedback(self, item: FeedbackItem) -> str:
        """
        Добавляет элемент обратной связи в хранилище.

        Args:
            item: Элемент обратной связи

        Returns:
            ID добавленного элемента
        """
        self.feedback_items[item.id] = item
        return item.id

    def get_feedback(self, item_id: str) -> Optional[FeedbackItem]:
        """
        Получает элемент обратной связи по ID.

        Args:
            item_id: ID элемента

        Returns:
            Элемент обратной связи или None, если не найден
        """
        return self.feedback_items.get(item_id)

    def get_all_by_strategy(self, strategy_id: str) -> List[FeedbackItem]:
        """
        Получает все элементы обратной связи для указанной стратегии.

        Args:
            strategy_id: ID стратегии

        Returns:
            Список элементов обратной связи
        """
        return [
            item for item in self.feedback_items.values()
            if item.strategy_id == strategy_id
        ]

    def get_by_type(self, feedback_type: FeedbackType) -> List[FeedbackItem]:
        """
        Получает все элементы обратной связи указанного типа.

        Args:
            feedback_type: Тип обратной связи

        Returns:
            Список элементов обратной связи
        """
        return [
            item for item in self.feedback_items.values()
            if item.feedback_type == feedback_type
        ]

    def get_by_source(self, source: FeedbackSource) -> List[FeedbackItem]:
        """
        Получает все элементы обратной связи от указанного источника.

        Args:
            source: Источник обратной связи

        Returns:
            Список элементов обратной связи
        """
        return [
            item for item in self.feedback_items.values()
            if item.source == source
        ]

    def get_average_score(
        self,
        strategy_id: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None
    ) -> float:
        """
        Вычисляет среднюю оценку для стратегии и/или типа обратной связи.

        Args:
            strategy_id: ID стратегии (опционально)
            feedback_type: Тип обратной связи (опционально)

        Returns:
            Средняя оценка или 0.0, если нет данных
        """
        items = list(self.feedback_items.values())

        if strategy_id:
            items = [item for item in items if item.strategy_id == strategy_id]

        if feedback_type:
            items = [item for item in items if item.feedback_type == feedback_type]

        if not items:
            return 0.0

        return sum(item.score for item in items) / len(items)

    def save(self) -> bool:
        """
        Сохраняет все данные обратной связи в файл.

        Returns:
            True, если сохранение успешно, иначе False
        """
        try:
            # Создаем файл для всех данных
            all_data_path = os.path.join(self.feedback_dir, "all_feedback.json")

            data = {
                item_id: item.to_dict()
                for item_id, item in self.feedback_items.items()
            }

            with open(all_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Создаем файлы по стратегиям
            strategies = set(item.strategy_id for item in self.feedback_items.values())

            for strategy_id in strategies:
                strategy_items = self.get_all_by_strategy(strategy_id)
                strategy_data = {item.id: item.to_dict() for item in strategy_items}

                strategy_file = os.path.join(self.feedback_dir, f"strategy_{strategy_id}.json")

                with open(strategy_file, 'w', encoding='utf-8') as f:
                    json.dump(strategy_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            logger.error(f"Failed to save feedback data: {str(e)}")
            return False

    def load(self) -> bool:
        """
        Загружает данные обратной связи из файла.

        Returns:
            True, если загрузка успешна, иначе False
        """
        try:
            all_data_path = os.path.join(self.feedback_dir, "all_feedback.json")

            if not os.path.exists(all_data_path):
                logger.warning(f"Feedback data file not found: {all_data_path}")
                return False

            with open(all_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.feedback_items = {
                item_id: FeedbackItem.from_dict(item_data)
                for item_id, item_data in data.items()
            }

            return True
        except Exception as e:
            logger.error(f"Failed to load feedback data: {str(e)}")
            return False


class FeedbackAnalyzer:
    """
    Класс для анализа обратной связи и формирования рекомендаций
    по улучшению стратегий исследования.
    """

    def __init__(self, storage: FeedbackStorage):
        """
        Инициализирует анализатор обратной связи.

        Args:
            storage: Хранилище обратной связи
        """
        self.storage = storage

    def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """
        Анализирует производительность стратегии на основе обратной связи.

        Args:
            strategy_id: ID стратегии

        Returns:
            Словарь с метриками производительности
        """
        feedback_items = self.storage.get_all_by_strategy(strategy_id)

        if not feedback_items:
            return {
                "strategy_id": strategy_id,
                "overall_score": 0.0,
                "feedback_count": 0,
                "metrics": {},
                "recent_trend": "unknown"
            }

        # Общая оценка
        overall_score = sum(item.score for item in feedback_items) / len(feedback_items)

        # Разбивка по типам обратной связи
        metrics = {}
        for feedback_type in FeedbackType:
            type_items = [item for item in feedback_items if item.feedback_type == feedback_type]

            if type_items:
                metrics[feedback_type.value] = sum(item.score for item in type_items) / len(type_items)
            else:
                metrics[feedback_type.value] = None

        # Анализ тренда (последние 5 элементов)
        recent_items = sorted(feedback_items, key=lambda x: x.created_at, reverse=True)[:5]

        if len(recent_items) >= 3:
            recent_avg = sum(item.score for item in recent_items) / len(recent_items)
            older_items = sorted(feedback_items, key=lambda x: x.created_at, reverse=True)[5:10]

            if older_items:
                older_avg = sum(item.score for item in older_items) / len(older_items)

                if recent_avg > older_avg + 0.1:
                    trend = "improving"
                elif recent_avg < older_avg - 0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
        else:
            trend = "insufficient_data"

        return {
            "strategy_id": strategy_id,
            "overall_score": overall_score,
            "feedback_count": len(feedback_items),
            "metrics": metrics,
            "recent_trend": trend
        }

    def get_improvement_recommendations(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Формирует рекомендации по улучшению стратегии.

        Args:
            strategy_id: ID стратегии

        Returns:
            Список рекомендаций
        """
        performance = self.get_strategy_performance(strategy_id)
        feedback_items = self.storage.get_all_by_strategy(strategy_id)

        recommendations = []

        if not feedback_items:
            return [{"message": "Недостаточно данных для формирования рекомендаций"}]

        # Проверяем низкие показатели по типам обратной связи
        metrics = performance.get("metrics", {})
        for feedback_type, score in metrics.items():
            if score is not None and score < 0.6:
                # Находим конкретные отзывы с низкими оценками
                low_items = [
                    item for item in feedback_items
                    if item.feedback_type.value == feedback_type and item.score < 0.6
                ]

                if low_items:
                    # Извлекаем описания проблем
                    descriptions = [item.description for item in low_items if item.description]

                    recommendation = {
                        "area": feedback_type,
                        "score": score,
                        "issue": f"Низкая оценка по критерию '{feedback_type}'",
                        "action": self._get_recommended_action(feedback_type, descriptions),
                        "priority": "high" if score < 0.4 else "medium"
                    }

                    recommendations.append(recommendation)

        # Добавляем общую рекомендацию, если нет конкретных
        if not recommendations:
            if performance.get("overall_score", 0) < 0.7:
                recommendations.append({
                    "area": "overall",
                    "score": performance.get("overall_score", 0),
                    "issue": "Общая производительность стратегии ниже оптимальной",
                    "action": "Рассмотрите возможность сбора дополнительной обратной связи для выявления конкретных проблем",
                    "priority": "medium"
                })
            else:
                recommendations.append({
                    "area": "overall",
                    "score": performance.get("overall_score", 0),
                    "issue": "Стратегия работает хорошо",
                    "action": "Продолжайте мониторинг производительности",
                    "priority": "low"
                })

        return recommendations

    def _get_recommended_action(self, feedback_type: str, descriptions: List[str]) -> str:
        """
        Формирует рекомендуемое действие на основе типа обратной связи и описаний.

        Args:
            feedback_type: Тип обратной связи
            descriptions: Описания проблем

        Returns:
            Рекомендуемое действие
        """
        # Стандартные рекомендации по типам
        standard_recommendations = {
            FeedbackType.RELEVANCE.value: "Улучшите алгоритмы фильтрации и ранжирования результатов",
            FeedbackType.COMPLETENESS.value: "Расширьте источники информации и увеличьте глубину поиска",
            FeedbackType.EFFICIENCY.value: "Оптимизируйте процесс сбора информации, добавьте кэширование",
            FeedbackType.ACCURACY.value: "Улучшите процесс проверки и валидации собранной информации",
            FeedbackType.USABILITY.value: "Доработайте форматирование и структурирование результатов"
        }

        # Если есть описания проблем, используем их для формирования более точной рекомендации
        if descriptions:
            common_words = self._extract_common_keywords(descriptions)
            if common_words:
                return f"{standard_recommendations.get(feedback_type, 'Улучшите стратегию')}. Обратите внимание на проблемы, связанные с: {', '.join(common_words)}"

        return standard_recommendations.get(feedback_type, "Проанализируйте и улучшите стратегию в соответствии с обратной связью")

    def _extract_common_keywords(self, texts: List[str], limit: int = 3) -> List[str]:
        """
        Извлекает общие ключевые слова из списка текстов.

        Args:
            texts: Список текстов
            limit: Максимальное количество ключевых слов

        Returns:
            Список общих ключевых слов
        """
        # Простая реализация - подсчет частоты слов
        word_counts = {}

        for text in texts:
            if not text:
                continue

            words = text.lower().split()

            for word in words:
                if len(word) < 4:  # Игнорируем короткие слова
                    continue

                word_counts[word] = word_counts.get(word, 0) + 1

        # Сортируем по частоте и возвращаем топ слова
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:limit]]


class FeedbackManager:
    """
    Менеджер обратной связи для управления сбором и использованием
    обратной связи для улучшения стратегий исследования.
    """

    def __init__(self, feedback_dir: str = "data/feedback"):
        """
        Инициализирует менеджер обратной связи.

        Args:
            feedback_dir: Директория для хранения данных обратной связи
        """
        self.storage = FeedbackStorage(feedback_dir=feedback_dir)
        self.analyzer = FeedbackAnalyzer(storage=self.storage)

        # Загружаем существующие данные
        self.storage.load()

    def add_user_feedback(
        self,
        strategy_id: str,
        feedback_type: Union[FeedbackType, str],
        score: float,
        description: Optional[str] = None,
        exploration_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Добавляет обратную связь от пользователя.

        Args:
            strategy_id: ID стратегии
            feedback_type: Тип обратной связи
            score: Оценка (0.0 - 1.0)
            description: Текстовое описание
            exploration_id: ID исследования
            metadata: Дополнительные метаданные

        Returns:
            ID созданного элемента обратной связи
        """
        # Преобразуем тип обратной связи, если передана строка
        if isinstance(feedback_type, str):
            try:
                feedback_type = FeedbackType(feedback_type)
            except ValueError:
                feedback_type = FeedbackType.OTHER

        # Создаем элемент обратной связи
        feedback_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=feedback_type,
            score=score,
            source=FeedbackSource.USER,
            description=description,
            exploration_id=exploration_id,
            metadata=metadata
        )

        # Добавляем в хранилище
        item_id = self.storage.add_feedback(feedback_item)

        # Сохраняем данные
        self.storage.save()

        return item_id

    def add_automatic_feedback(
        self,
        strategy_id: str,
        collection: InformationCollection,
        execution_time: float,
        query: str
    ) -> Dict[str, str]:
        """
        Генерирует и добавляет автоматическую обратную связь на основе результатов.

        Args:
            strategy_id: ID стратегии
            collection: Коллекция собранной информации
            execution_time: Время выполнения (в секундах)
            query: Запрос для исследования

        Returns:
            Словарь с ID созданных элементов обратной связи
        """
        feedback_ids = {}
        summary = collection.get_summary()

        # Оценка эффективности на основе времени выполнения
        efficiency_score = 0.0
        if execution_time > 0:
            # Чем меньше время выполнения, тем выше оценка (с учетом количества элементов)
            items_per_second = summary.get("total_items", 0) / execution_time
            efficiency_score = min(1.0, items_per_second / 2.0)  # Нормализация

        efficiency_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=FeedbackType.EFFICIENCY,
            score=efficiency_score,
            source=FeedbackSource.AUTOMATIC,
            description=f"Автоматическая оценка эффективности: {summary.get('total_items', 0)} элементов за {execution_time:.2f} секунд",
            exploration_id=collection.name,
            metadata={"query": query, "execution_time": execution_time}
        )

        feedback_ids["efficiency"] = self.storage.add_feedback(efficiency_item)

        # Оценка релевантности
        relevance_score = summary.get("avg_relevance", 0.0)
        relevance_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=FeedbackType.RELEVANCE,
            score=relevance_score,
            source=FeedbackSource.AUTOMATIC,
            description=f"Автоматическая оценка релевантности: {relevance_score:.2f}",
            exploration_id=collection.name,
            metadata={"query": query}
        )

        feedback_ids["relevance"] = self.storage.add_feedback(relevance_item)

        # Оценка точности
        accuracy_score = summary.get("avg_confidence", 0.0)
        accuracy_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=FeedbackType.ACCURACY,
            score=accuracy_score,
            source=FeedbackSource.AUTOMATIC,
            description=f"Автоматическая оценка точности: {accuracy_score:.2f}",
            exploration_id=collection.name,
            metadata={"query": query}
        )

        feedback_ids["accuracy"] = self.storage.add_feedback(accuracy_item)

        # Оценка полноты
        completeness_score = min(1.0, summary.get("total_items", 0) / 10.0)  # Нормализация
        completeness_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=FeedbackType.COMPLETENESS,
            score=completeness_score,
            source=FeedbackSource.AUTOMATIC,
            description=f"Автоматическая оценка полноты: {completeness_score:.2f}",
            exploration_id=collection.name,
            metadata={"query": query, "total_items": summary.get("total_items", 0)}
        )

        feedback_ids["completeness"] = self.storage.add_feedback(completeness_item)

        # Сохраняем данные
        self.storage.save()

        return feedback_ids

    def add_agent_feedback(
        self,
        strategy_id: str,
        feedback_type: FeedbackType,
        score: float,
        description: str,
        exploration_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Добавляет обратную связь от агента.

        Args:
            strategy_id: ID стратегии
            feedback_type: Тип обратной связи
            score: Оценка (0.0 - 1.0)
            description: Текстовое описание
            exploration_id: ID исследования
            metadata: Дополнительные метаданные

        Returns:
            ID созданного элемента обратной связи
        """
        feedback_item = FeedbackItem(
            strategy_id=strategy_id,
            feedback_type=feedback_type,
            score=score,
            source=FeedbackSource.AGENT,
            description=description,
            exploration_id=exploration_id,
            metadata=metadata
        )

        item_id = self.storage.add_feedback(feedback_item)
        self.storage.save()

        return item_id

    def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """
        Получает информацию о производительности стратегии.

        Args:
            strategy_id: ID стратегии

        Returns:
            Словарь с метриками производительности
        """
        return self.analyzer.get_strategy_performance(strategy_id)

    def get_improvement_recommendations(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Получает рекомендации по улучшению стратегии.

        Args:
            strategy_id: ID стратегии

        Returns:
            Список рекомендаций
        """
        return self.analyzer.get_improvement_recommendations(strategy_id)

    def get_all_feedback(self, strategy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получает всю обратную связь для стратегии или всех стратегий.

        Args:
            strategy_id: ID стратегии (опционально)

        Returns:
            Список элементов обратной связи в виде словарей
        """
        if strategy_id:
            items = self.storage.get_all_by_strategy(strategy_id)
        else:
            items = list(self.storage.feedback_items.values())

        return [item.to_dict() for item in items]
