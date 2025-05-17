"""
Модуль стратегий исследования для GopiAI Reasoning Agent

Предоставляет набор стратегий для сбора и анализа информации
из различных источников, включая файловую систему, веб-ресурсы и другие.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import os
import json
import time
from enum import Enum
import asyncio

from app.agent.browser_access import BrowserAccess
from app.agent.file_system_access import FileSystemAccess
from app.agent.text_editor_access import TextEditorAccess
from app.agent.thought_tree import ThoughtTree
from app.logger import logger


class ExplorationPhase(Enum):
    """Фазы процесса исследования"""
    INITIAL_QUERY = "initial_query"          # Начальный запрос/формулировка
    RESOURCE_DISCOVERY = "resource_discovery" # Поиск ресурсов
    DATA_COLLECTION = "data_collection"      # Сбор данных
    DATA_ANALYSIS = "data_analysis"          # Анализ данных
    INFORMATION_SYNTHESIS = "info_synthesis" # Синтез информации
    RESULT_VALIDATION = "result_validation"  # Проверка результатов


class InformationSource(Enum):
    """Источники информации для исследования"""
    WEB = "web"                  # Веб-ресурсы
    FILES = "files"              # Файловая система
    DATABASE = "database"        # Базы данных
    API = "api"                  # API сервисы
    USER_INPUT = "user_input"    # Ввод пользователя
    KNOWLEDGE_BASE = "knowledge_base"  # Базы знаний/модели
    OTHER = "other"              # Другие источники


class InformationItem:
    """
    Класс для представления отдельного элемента информации,
    собранной в процессе исследования.
    """

    def __init__(
        self,
        content: str,
        source: Union[InformationSource, str],
        source_details: Optional[Dict[str, Any]] = None,
        relevance_score: float = 0.0,
        confidence_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Инициализирует элемент информации.

        Args:
            content: Содержимое элемента информации
            source: Источник информации (тип InformationSource или строка)
            source_details: Дополнительные детали об источнике
            relevance_score: Оценка релевантности (0.0 - 1.0)
            confidence_score: Оценка достоверности (0.0 - 1.0)
            metadata: Дополнительные метаданные
            tags: Список тегов для категоризации
        """
        self.id = f"info_{int(time.time())}_{id(self)}"
        self.content = content

        # Обработка источника (enum или строка)
        if isinstance(source, InformationSource):
            self.source = source
        else:
            try:
                self.source = InformationSource(source)
            except ValueError:
                self.source = InformationSource.OTHER

        self.source_details = source_details or {}
        self.relevance_score = max(0.0, min(1.0, relevance_score))  # Ограничение 0-1
        self.confidence_score = max(0.0, min(1.0, confidence_score))  # Ограничение 0-1
        self.metadata = metadata or {}
        self.tags = tags or []
        self.created_at = time.time()
        self.updated_at = self.created_at

    def update_scores(self, relevance: Optional[float] = None, confidence: Optional[float] = None):
        """
        Обновляет оценки релевантности и достоверности.

        Args:
            relevance: Новая оценка релевантности (0.0 - 1.0)
            confidence: Новая оценка достоверности (0.0 - 1.0)
        """
        if relevance is not None:
            self.relevance_score = max(0.0, min(1.0, relevance))

        if confidence is not None:
            self.confidence_score = max(0.0, min(1.0, confidence))

        self.updated_at = time.time()

    def add_tags(self, tags: List[str]):
        """
        Добавляет теги к элементу информации.

        Args:
            tags: Список тегов для добавления
        """
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)

        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует элемент информации в словарь.

        Returns:
            Словарь с данными элемента информации
        """
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source.value,
            "source_details": self.source_details,
            "relevance_score": self.relevance_score,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InformationItem":
        """
        Создает элемент информации из словаря.

        Args:
            data: Словарь с данными элемента информации

        Returns:
            Созданный элемент информации
        """
        item = cls(
            content=data["content"],
            source=data["source"],
            source_details=data.get("source_details", {}),
            relevance_score=data.get("relevance_score", 0.0),
            confidence_score=data.get("confidence_score", 0.0),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", [])
        )

        # Восстанавливаем ID и временные метки
        item.id = data.get("id", item.id)
        item.created_at = data.get("created_at", item.created_at)
        item.updated_at = data.get("updated_at", item.updated_at)

        return item


class InformationCollection:
    """
    Коллекция информационных элементов, собранных в ходе исследования.
    Обеспечивает методы для управления, фильтрации и анализа информации.
    """

    def __init__(self, name: str = "exploration_results"):
        """
        Инициализирует коллекцию информации.

        Args:
            name: Название коллекции
        """
        self.name = name
        self.items: Dict[str, InformationItem] = {}
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.metadata: Dict[str, Any] = {}

    def add_item(self, item: InformationItem) -> str:
        """
        Добавляет элемент в коллекцию.

        Args:
            item: Элемент информации для добавления

        Returns:
            ID добавленного элемента
        """
        self.items[item.id] = item
        self.updated_at = time.time()
        return item.id

    def get_item(self, item_id: str) -> Optional[InformationItem]:
        """
        Получает элемент из коллекции по ID.

        Args:
            item_id: ID элемента

        Returns:
            Элемент информации или None, если не найден
        """
        return self.items.get(item_id)

    def remove_item(self, item_id: str) -> bool:
        """
        Удаляет элемент из коллекции.

        Args:
            item_id: ID элемента для удаления

        Returns:
            True, если элемент был удален, иначе False
        """
        if item_id in self.items:
            del self.items[item_id]
            self.updated_at = time.time()
            return True
        return False

    def filter_by_source(self, source: Union[InformationSource, str]) -> List[InformationItem]:
        """
        Фильтрует элементы по источнику.

        Args:
            source: Источник информации

        Returns:
            Список отфильтрованных элементов
        """
        if isinstance(source, str):
            try:
                source = InformationSource(source)
            except ValueError:
                source = InformationSource.OTHER

        return [item for item in self.items.values() if item.source == source]

    def filter_by_tags(self, tags: List[str], require_all: bool = False) -> List[InformationItem]:
        """
        Фильтрует элементы по тегам.

        Args:
            tags: Список тегов для фильтрации
            require_all: Требовать наличие всех тегов (True) или любого из них (False)

        Returns:
            Список отфильтрованных элементов
        """
        if require_all:
            return [
                item for item in self.items.values()
                if all(tag in item.tags for tag in tags)
            ]
        else:
            return [
                item for item in self.items.values()
                if any(tag in item.tags for tag in tags)
            ]

    def filter_by_relevance(self, min_score: float = 0.0) -> List[InformationItem]:
        """
        Фильтрует элементы по минимальной оценке релевантности.

        Args:
            min_score: Минимальная оценка релевантности (0.0 - 1.0)

        Returns:
            Список отфильтрованных элементов
        """
        return [
            item for item in self.items.values()
            if item.relevance_score >= min_score
        ]

    def filter_by_confidence(self, min_score: float = 0.0) -> List[InformationItem]:
        """
        Фильтрует элементы по минимальной оценке достоверности.

        Args:
            min_score: Минимальная оценка достоверности (0.0 - 1.0)

        Returns:
            Список отфильтрованных элементов
        """
        return [
            item for item in self.items.values()
            if item.confidence_score >= min_score
        ]

    def get_summary(self) -> Dict[str, Any]:
        """
        Возвращает сводку о коллекции.

        Returns:
            Словарь со сводной информацией
        """
        sources_count = {}
        for source in InformationSource:
            count = len(self.filter_by_source(source))
            if count > 0:
                sources_count[source.value] = count

        tags_count = {}
        for item in self.items.values():
            for tag in item.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1

        return {
            "name": self.name,
            "total_items": len(self.items),
            "sources": sources_count,
            "tags": tags_count,
            "avg_relevance": sum(item.relevance_score for item in self.items.values()) / max(1, len(self.items)),
            "avg_confidence": sum(item.confidence_score for item in self.items.values()) / max(1, len(self.items)),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует коллекцию в словарь.

        Returns:
            Словарь с данными коллекции
        """
        return {
            "name": self.name,
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InformationCollection":
        """
        Создает коллекцию из словаря.

        Args:
            data: Словарь с данными коллекции

        Returns:
            Созданная коллекция
        """
        collection = cls(name=data.get("name", "exploration_results"))

        # Восстанавливаем элементы
        items_data = data.get("items", {})
        for item_id, item_data in items_data.items():
            item = InformationItem.from_dict(item_data)
            collection.items[item_id] = item

        # Восстанавливаем метаданные и временные метки
        collection.created_at = data.get("created_at", collection.created_at)
        collection.updated_at = data.get("updated_at", collection.updated_at)
        collection.metadata = data.get("metadata", {})

        return collection

    def save_to_file(self, file_path: str) -> bool:
        """
        Сохраняет коллекцию в файл.

        Args:
            file_path: Путь к файлу для сохранения

        Returns:
            True, если сохранение успешно, иначе False
        """
        try:
            data = self.to_dict()

            # Создаем директории при необходимости
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            logger.error(f"Error saving information collection to file: {str(e)}")
            return False

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional["InformationCollection"]:
        """
        Загружает коллекцию из файла.

        Args:
            file_path: Путь к файлу для загрузки

        Returns:
            Загруженная коллекция или None в случае ошибки
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            collection = cls.from_dict(data)
            return collection
        except Exception as e:
            logger.error(f"Error loading information collection from file: {str(e)}")
            return None


class ExplorationStrategy(ABC):
    """
    Базовый абстрактный класс для стратегий исследования.
    Определяет общий интерфейс для всех стратегий исследования.
    """

    def __init__(
        self,
        name: str,
        description: str,
        file_system: Optional[FileSystemAccess] = None,
        browser_access: Optional[BrowserAccess] = None,
        text_editor: Optional[TextEditorAccess] = None,
        thought_tree: Optional[ThoughtTree] = None
    ):
        """
        Инициализирует стратегию исследования.

        Args:
            name: Название стратегии
            description: Описание стратегии
            file_system: Доступ к файловой системе
            browser_access: Доступ к браузеру
            text_editor: Доступ к текстовому редактору
            thought_tree: Дерево мыслей для интеграции
        """
        self.name = name
        self.description = description
        self.file_system = file_system
        self.browser_access = browser_access
        self.text_editor = text_editor
        self.thought_tree = thought_tree

        # Коллекция для хранения собранной информации
        self.information_collection = InformationCollection(name=f"{name}_collection")

        # Метаданные стратегии
        self.metadata: Dict[str, Any] = {
            "created_at": time.time(),
            "updated_at": time.time(),
            "executions": 0,
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "total_execution_time": 0.0
        }

        # История выполнений
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    async def explore(self, query: str, **kwargs) -> InformationCollection:
        """
        Выполняет исследование на основе запроса.

        Args:
            query: Текст запроса для исследования
            **kwargs: Дополнительные параметры для исследования

        Returns:
            Коллекция собранной информации
        """
        pass

    @abstractmethod
    async def process_results(self, collection: InformationCollection, **kwargs) -> Dict[str, Any]:
        """
        Обрабатывает результаты исследования.

        Args:
            collection: Коллекция с собранной информацией
            **kwargs: Дополнительные параметры для обработки

        Returns:
            Словарь с обработанными результатами
        """
        pass

    def _record_execution(self, query: str, result: Dict[str, Any], execution_time: float, success: bool):
        """
        Записывает информацию о выполнении стратегии.

        Args:
            query: Текст запроса
            result: Результат выполнения
            execution_time: Время выполнения (в секундах)
            success: Успешность выполнения
        """
        # Обновляем метаданные
        self.metadata["executions"] += 1
        self.metadata["updated_at"] = time.time()
        self.metadata["total_execution_time"] += execution_time
        self.metadata["avg_execution_time"] = (
            self.metadata["total_execution_time"] / self.metadata["executions"]
        )

        # Обновляем успешность
        success_count = sum(1 for entry in self.execution_history if entry["success"]) + (1 if success else 0)
        self.metadata["success_rate"] = success_count / self.metadata["executions"]

        # Записываем в историю
        execution_entry = {
            "timestamp": time.time(),
            "query": query,
            "execution_time": execution_time,
            "success": success,
            "result_summary": {
                "items_collected": result.get("items_collected", 0),
                "sources": result.get("sources", {}),
                "avg_relevance": result.get("avg_relevance", 0.0),
                "avg_confidence": result.get("avg_confidence", 0.0)
            }
        }

        self.execution_history.append(execution_entry)

    def add_to_thought_tree(
        self,
        content: str,
        node_type: str = "exploration",
        parent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Добавляет информацию в дерево мыслей, если оно доступно.

        Args:
            content: Содержимое для добавления
            node_type: Тип узла
            parent_id: ID родительского узла

        Returns:
            ID созданного узла или None, если дерево мыслей недоступно
        """
        if self.thought_tree is None:
            return None

        return self.thought_tree.add_thought(
            content=content,
            node_type=node_type,
            parent_id=parent_id
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования стратегии.

        Returns:
            Словарь со статистикой
        """
        return {
            "name": self.name,
            "description": self.description,
            "executions": self.metadata["executions"],
            "success_rate": self.metadata["success_rate"],
            "avg_execution_time": self.metadata["avg_execution_time"],
            "total_execution_time": self.metadata["total_execution_time"],
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "created_at": self.metadata["created_at"],
            "updated_at": self.metadata["updated_at"]
        }


# Конкретные стратегии исследования будут добавлены в других файлах
"""

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationSource, InformationItem,
    InformationCollection, ExplorationPhase
)
