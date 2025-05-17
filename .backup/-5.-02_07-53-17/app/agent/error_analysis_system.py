"""
Система анализа и категоризации типичных ошибок

Предоставляет механизмы для сбора, анализа и категоризации ошибок,
возникающих при работе агента, а также инструменты для обучения на основе
этих ошибок.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple
import json
import time
import os
from enum import Enum
from datetime import datetime
import re
from collections import Counter, defaultdict
import traceback
import shutil

from app.logger import logger


class ErrorSeverity(Enum):
    """Уровни серьезности ошибок"""
    CRITICAL = "critical"     # Критические ошибки, блокирующие работу агента
    HIGH = "high"             # Серьезные ошибки, существенно влияющие на результат
    MEDIUM = "medium"         # Ошибки средней серьезности, заметно влияющие на результат
    LOW = "low"               # Незначительные ошибки, минимально влияющие на результат
    INFO = "info"             # Информационные сообщения о потенциальных проблемах


class ErrorSource(Enum):
    """Источники ошибок"""
    PLANNING = "planning"                 # Ошибки при планировании действий
    EXECUTION = "execution"               # Ошибки при выполнении действий
    REASONING = "reasoning"               # Ошибки в логических рассуждениях
    TOOL_CALL = "tool_call"               # Ошибки при вызове инструментов
    SYSTEM = "system"                     # Системные ошибки
    PERMISSION = "permission"             # Ошибки, связанные с разрешениями
    USER_INTERACTION = "user_interaction" # Ошибки при взаимодействии с пользователем
    OTHER = "other"                       # Другие источники


class ErrorCategory:
    """
    Класс для определения категории ошибок.
    """

    def __init__(
        self,
        name: str,
        description: str,
        patterns: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        source: Optional[ErrorSource] = None,
        severity: Optional[ErrorSeverity] = None,
        parent_category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует категорию ошибок.

        Args:
            name: Уникальное имя категории
            description: Описание категории
            patterns: Регулярные выражения для сопоставления с ошибками
            keywords: Ключевые слова для сопоставления
            source: Основной источник ошибок данной категории
            severity: Стандартный уровень серьезности для ошибок категории
            parent_category: Родительская категория (для иерархической структуры)
            metadata: Дополнительные метаданные
        """
        self.id = f"cat_{name.lower().replace(' ', '_')}"
        self.name = name
        self.description = description
        self.patterns = [re.compile(p, re.IGNORECASE) for p in (patterns or [])]
        self.keywords = set(k.lower() for k in (keywords or []))
        self.source = source
        self.severity = severity
        self.parent_category = parent_category
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.updated_at = self.created_at

    def matches(self, error_message: str) -> bool:
        """
        Проверяет, соответствует ли ошибка данной категории.

        Args:
            error_message: Текст ошибки

        Returns:
            True, если ошибка соответствует категории, иначе False
        """
        error_message_lower = error_message.lower()

        # Проверка по регулярным выражениям
        for pattern in self.patterns:
            if pattern.search(error_message):
                return True

        # Проверка по ключевым словам
        for keyword in self.keywords:
            if keyword in error_message_lower:
                return True

        return False

    def update_patterns(self, patterns: List[str]) -> None:
        """
        Обновляет список регулярных выражений для категории.

        Args:
            patterns: Новые регулярные выражения
        """
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.updated_at = time.time()

    def update_keywords(self, keywords: List[str]) -> None:
        """
        Обновляет список ключевых слов для категории.

        Args:
            keywords: Новые ключевые слова
        """
        self.keywords = set(k.lower() for k in keywords)
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует категорию в словарь.

        Returns:
            Словарь с данными категории
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "patterns": [p.pattern for p in self.patterns],
            "keywords": list(self.keywords),
            "source": self.source.value if self.source else None,
            "severity": self.severity.value if self.severity else None,
            "parent_category": self.parent_category,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorCategory":
        """
        Создает категорию из словаря.

        Args:
            data: Словарь с данными категории

        Returns:
            Созданная категория
        """
        category = cls(
            name=data["name"],
            description=data["description"],
            patterns=data.get("patterns", []),
            keywords=data.get("keywords", []),
            source=ErrorSource(data["source"]) if data.get("source") else None,
            severity=ErrorSeverity(data["severity"]) if data.get("severity") else None,
            parent_category=data.get("parent_category"),
            metadata=data.get("metadata", {})
        )

        # Восстанавливаем ID и временные метки
        category.id = data.get("id", category.id)
        category.created_at = data.get("created_at", category.created_at)
        category.updated_at = data.get("updated_at", category.updated_at)

        return category


class ErrorInstance:
    """
    Класс для представления экземпляра ошибки.
    """

    def __init__(
        self,
        message: str,
        source: ErrorSource,
        severity: ErrorSeverity,
        category_id: Optional[str] = None,
        task_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        resolution: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует экземпляр ошибки.

        Args:
            message: Сообщение об ошибке
            source: Источник ошибки
            severity: Уровень серьезности
            category_id: ID категории ошибки (если уже известна)
            task_id: ID задачи, при выполнении которой произошла ошибка
            stack_trace: Трассировка стека (если доступна)
            context: Контекст выполнения при возникновении ошибки
            resolution: Решение или обход проблемы (если известно)
            metadata: Дополнительные метаданные
        """
        self.id = f"err_{int(time.time())}_{id(self)}"
        self.message = message
        self.source = source
        self.severity = severity
        self.category_id = category_id
        self.task_id = task_id
        self.stack_trace = stack_trace
        self.context = context or {}
        self.resolution = resolution
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.resolved = False
        self.resolved_at = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует экземпляр ошибки в словарь.

        Returns:
            Словарь с данными экземпляра ошибки
        """
        return {
            "id": self.id,
            "message": self.message,
            "source": self.source.value,
            "severity": self.severity.value,
            "category_id": self.category_id,
            "task_id": self.task_id,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "resolution": self.resolution,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorInstance":
        """
        Создает экземпляр ошибки из словаря.

        Args:
            data: Словарь с данными экземпляра ошибки

        Returns:
            Созданный экземпляр ошибки
        """
        source = ErrorSource(data["source"])
        severity = ErrorSeverity(data["severity"])

        error = cls(
            message=data["message"],
            source=source,
            severity=severity,
            category_id=data.get("category_id"),
            task_id=data.get("task_id"),
            stack_trace=data.get("stack_trace"),
            context=data.get("context", {}),
            resolution=data.get("resolution"),
            metadata=data.get("metadata", {})
        )

        # Восстанавливаем ID и временные метки
        error.id = data.get("id", error.id)
        error.created_at = data.get("created_at", error.created_at)
        error.resolved = data.get("resolved", error.resolved)
        error.resolved_at = data.get("resolved_at", error.resolved_at)

        return error

    def mark_as_resolved(self, resolution: str) -> None:
        """
        Отмечает ошибку как разрешенную.

        Args:
            resolution: Описание решения проблемы
        """
        self.resolved = True
        self.resolved_at = time.time()
        self.resolution = resolution


class ErrorStorage:
    """
    Класс для хранения и управления ошибками и их категориями.
    """

    def __init__(self, storage_dir: str = "data/errors"):
        """
        Инициализирует хранилище ошибок.

        Args:
            storage_dir: Директория для хранения данных об ошибках
        """
        self.storage_dir = storage_dir
        self.errors: Dict[str, ErrorInstance] = {}
        self.categories: Dict[str, ErrorCategory] = {}

        # Создаем директорию, если не существует
        os.makedirs(storage_dir, exist_ok=True)

    def add_error(self, error: ErrorInstance) -> str:
        """
        Добавляет ошибку в хранилище.

        Args:
            error: Экземпляр ошибки

        Returns:
            ID добавленной ошибки
        """
        self.errors[error.id] = error
        return error.id

    def add_category(self, category: ErrorCategory) -> str:
        """
        Добавляет категорию ошибок в хранилище.

        Args:
            category: Категория ошибок

        Returns:
            ID добавленной категории
        """
        self.categories[category.id] = category
        return category.id

    def get_error(self, error_id: str) -> Optional[ErrorInstance]:
        """
        Получает ошибку по ID.

        Args:
            error_id: ID ошибки

        Returns:
            Экземпляр ошибки или None, если не найден
        """
        return self.errors.get(error_id)

    def get_category(self, category_id: str) -> Optional[ErrorCategory]:
        """
        Получает категорию по ID.

        Args:
            category_id: ID категории

        Returns:
            Категория ошибок или None, если не найдена
        """
        return self.categories.get(category_id)

    def get_errors_by_category(self, category_id: str) -> List[ErrorInstance]:
        """
        Получает все ошибки указанной категории.

        Args:
            category_id: ID категории

        Returns:
            Список ошибок
        """
        return [
            error for error in self.errors.values()
            if error.category_id == category_id
        ]

    def get_errors_by_source(self, source: ErrorSource) -> List[ErrorInstance]:
        """
        Получает все ошибки из указанного источника.

        Args:
            source: Источник ошибок

        Returns:
            Список ошибок
        """
        return [
            error for error in self.errors.values()
            if error.source == source
        ]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorInstance]:
        """
        Получает все ошибки указанного уровня серьезности.

        Args:
            severity: Уровень серьезности

        Returns:
            Список ошибок
        """
        return [
            error for error in self.errors.values()
            if error.severity == severity
        ]

    def save(self) -> bool:
        """
        Сохраняет данные об ошибках и категориях в файлы.

        Returns:
            True в случае успеха, иначе False
        """
        try:
            # Сохраняем категории
            categories_file = os.path.join(self.storage_dir, "categories.json")
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {cat_id: cat.to_dict() for cat_id, cat in self.categories.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            # Сохраняем ошибки
            errors_file = os.path.join(self.storage_dir, "errors.json")
            with open(errors_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {err_id: err.to_dict() for err_id, err in self.errors.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            logger.info(f"Saved {len(self.errors)} errors and {len(self.categories)} categories")
            return True
        except Exception as e:
            logger.error(f"Failed to save error data: {str(e)}")
            return False

    def load(self) -> bool:
        """
        Загружает данные об ошибках и категориях из файлов.

        Returns:
            True в случае успеха, иначе False
        """
        try:
            # Загружаем категории
            categories_file = os.path.join(self.storage_dir, "categories.json")
            if os.path.exists(categories_file):
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories_data = json.load(f)
                    self.categories = {
                        cat_id: ErrorCategory.from_dict(cat_data)
                        for cat_id, cat_data in categories_data.items()
                    }

            # Загружаем ошибки
            errors_file = os.path.join(self.storage_dir, "errors.json")
            if os.path.exists(errors_file):
                with open(errors_file, 'r', encoding='utf-8') as f:
                    errors_data = json.load(f)
                    self.errors = {
                        err_id: ErrorInstance.from_dict(err_data)
                        for err_id, err_data in errors_data.items()
                    }

            logger.info(f"Loaded {len(self.errors)} errors and {len(self.categories)} categories")
            return True
        except Exception as e:
            logger.error(f"Failed to load error data: {str(e)}")
            return False

    def clean_old_errors(self, days_threshold: int = 90) -> int:
        """
        Удаляет ошибки старше указанного порога.

        Args:
            days_threshold: Количество дней, старше которого удаляются ошибки

        Returns:
            Количество удаленных ошибок
        """
        if not self.errors:
            return 0

        # Расчёт порогового времени (текущее время - N дней в секундах)
        threshold_time = time.time() - (days_threshold * 24 * 60 * 60)

        # Находим ID ошибок, которые нужно удалить
        error_ids_to_delete = []

        for error_id, error in self.errors.items():
            # Если ошибка старше порога и не является важной (HIGH или CRITICAL)
            if (error.created_at < threshold_time and
                    error.severity not in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]):
                error_ids_to_delete.append(error_id)

        # Удаляем ошибки
        for error_id in error_ids_to_delete:
            del self.errors[error_id]

        # Если были удаления, сохраняем обновленные данные
        if error_ids_to_delete:
            self.save()

        logger.info(f"Cleaned {len(error_ids_to_delete)} old errors older than {days_threshold} days")
        return len(error_ids_to_delete)

    def create_backup(self) -> bool:
        """
        Создает резервную копию данных об ошибках.

        Returns:
            True если резервная копия создана успешно
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.storage_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)

            # Создаем резервную копию категорий
            categories_file = os.path.join(self.storage_dir, "categories.json")
            if os.path.exists(categories_file):
                backup_categories = os.path.join(backup_dir, f"categories_{timestamp}.json")
                shutil.copy2(categories_file, backup_categories)

            # Создаем резервную копию ошибок
            errors_file = os.path.join(self.storage_dir, "errors.json")
            if os.path.exists(errors_file):
                backup_errors = os.path.join(backup_dir, f"errors_{timestamp}.json")
                shutil.copy2(errors_file, backup_errors)

            logger.info(f"Created backup of error data at {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return False


class ErrorAnalyzer:
    """
    Класс для анализа ошибок и выявления паттернов.
    """

    def __init__(self, storage: ErrorStorage):
        """
        Инициализирует анализатор ошибок.

        Args:
            storage: Хранилище ошибок
        """
        self.storage = storage

    def categorize_error(self, error: ErrorInstance) -> Optional[str]:
        """
        Определяет категорию ошибки на основе ее сообщения.

        Args:
            error: Ошибка для категоризации

        Returns:
            ID категории или None, если не удалось определить
        """
        for cat_id, category in self.storage.categories.items():
            if category.matches(error.message):
                return cat_id

        # Если не нашли подходящую категорию
        return None

    def suggest_new_category(self, error_messages: List[str]) -> Optional[Dict[str, Any]]:
        """
        Предлагает новую категорию на основе набора сообщений об ошибках.

        Args:
            error_messages: Список сообщений об ошибках

        Returns:
            Словарь с предлагаемой категорией или None, если недостаточно данных
        """
        if not error_messages or len(error_messages) < 3:
            # Нужно достаточное количество ошибок для анализа
            return None

        # Извлекаем общие слова и фразы
        common_terms = self._extract_common_terms(error_messages)
        if not common_terms:
            return None

        # Создаем название и описание для категории
        main_term = common_terms[0]
        name = f"{main_term.title()} Error"
        description = f"Errors related to {main_term}"

        # Создаем ключевые слова и шаблоны
        keywords = common_terms[:5]  # Первые 5 наиболее общих терминов
        patterns = []

        return {
            "name": name,
            "description": description,
            "keywords": keywords,
            "patterns": patterns
        }

    def _extract_common_terms(self, texts: List[str], min_count: int = 3) -> List[str]:
        """
        Извлекает общие термины из списка текстов.

        Args:
            texts: Список текстов
            min_count: Минимальное количество вхождений для включения в результат

        Returns:
            Список общих терминов, отсортированный по частоте
        """
        # Объединяем все тексты и разбиваем на слова
        all_text = " ".join(texts).lower()
        words = re.findall(r'\b\w+\b', all_text)

        # Считаем частоты слов
        word_counts = Counter(words)

        # Фильтруем слова, которые встречаются реже min_count раз
        common_words = [word for word, count in word_counts.items() if count >= min_count]

        # Сортируем по частоте (от большего к меньшему)
        common_words.sort(key=lambda word: word_counts[word], reverse=True)

        return common_words

    def analyze_error_trends(
        self,
        time_period: Optional[int] = None,
        source: Optional[ErrorSource] = None
    ) -> Dict[str, Any]:
        """
        Анализирует тренды ошибок за указанный период.

        Args:
            time_period: Период анализа в днях (None - все время)
            source: Источник ошибок для анализа (None - все источники)

        Returns:
            Словарь с результатами анализа трендов
        """
        # Фильтруем ошибки по времени и источнику
        filtered_errors = self.storage.errors.values()

        if time_period:
            cutoff_time = time.time() - (time_period * 86400)  # 86400 секунд в дне
            filtered_errors = [err for err in filtered_errors if err.created_at >= cutoff_time]

        if source:
            filtered_errors = [err for err in filtered_errors if err.source == source]

        # Собираем статистику
        total_errors = len(filtered_errors)
        if total_errors == 0:
            return {
                "total_errors": 0,
                "by_category": {},
                "by_severity": {},
                "by_source": {},
                "resolution_rate": 0,
                "common_patterns": []
            }

        # Группируем по категориям
        category_counts = defaultdict(int)
        for error in filtered_errors:
            if error.category_id:
                category_name = self.storage.categories.get(error.category_id)
                category_counts[category_name.name if category_name else "Uncategorized"] += 1
            else:
                category_counts["Uncategorized"] += 1

        # Группируем по уровню серьезности
        severity_counts = defaultdict(int)
        for error in filtered_errors:
            severity_counts[error.severity.value] += 1

        # Группируем по источнику
        source_counts = defaultdict(int)
        for error in filtered_errors:
            source_counts[error.source.value] += 1

        # Считаем долю разрешенных ошибок
        resolved_errors = sum(1 for err in filtered_errors if err.resolved)
        resolution_rate = resolved_errors / total_errors if total_errors > 0 else 0

        # Собираем все сообщения для анализа общих паттернов
        all_messages = [err.message for err in filtered_errors]
        common_patterns = self._extract_common_terms(all_messages, min_count=2)

        return {
            "total_errors": total_errors,
            "by_category": dict(category_counts),
            "by_severity": dict(severity_counts),
            "by_source": dict(source_counts),
            "resolution_rate": resolution_rate,
            "common_patterns": common_patterns[:10]  # Топ-10 паттернов
        }

    def get_similar_errors(self, error: ErrorInstance, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Находит похожие ошибки на основе сообщения.

        Args:
            error: Ошибка для поиска похожих
            limit: Максимальное количество результатов

        Returns:
            Список похожих ошибок с оценкой сходства
        """
        results = []

        # Получаем ключевые слова из сообщения об ошибке
        error_words = set(re.findall(r'\b\w+\b', error.message.lower()))

        for err_id, err in self.storage.errors.items():
            # Пропускаем ту же самую ошибку
            if err.id == error.id:
                continue

            # Получаем ключевые слова из сообщения сравниваемой ошибки
            err_words = set(re.findall(r'\b\w+\b', err.message.lower()))

            # Вычисляем коэффициент Жаккара (пересечение / объединение)
            if not error_words or not err_words:
                similarity = 0
            else:
                intersection = len(error_words.intersection(err_words))
                union = len(error_words.union(err_words))
                similarity = intersection / union

            if similarity > 0.1:  # Минимальный порог сходства
                results.append({
                    "error": err.to_dict(),
                    "similarity": similarity
                })

        # Сортируем результаты по сходству (от большего к меньшему)
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:limit]

    def extract_resolution_patterns(self) -> Dict[str, List[str]]:
        """
        Извлекает паттерны разрешения для различных категорий ошибок.

        Returns:
            Словарь, где ключи - ID категорий, значения - списки стратегий разрешения
        """
        resolution_patterns = defaultdict(list)

        # Собираем все разрешенные ошибки
        resolved_errors = [err for err in self.storage.errors.values() if err.resolved and err.resolution]

        # Группируем решения по категориям
        for error in resolved_errors:
            category_id = error.category_id or "uncategorized"
            if error.resolution:
                resolution_patterns[category_id].append(error.resolution)

        # Для каждой категории находим наиболее общие стратегии
        result = {}
        for category_id, resolutions in resolution_patterns.items():
            # Если достаточно решений для анализа
            if len(resolutions) >= 3:
                # Упрощаем и нормализуем решения для лучшего поиска общих паттернов
                normalized_resolutions = [self._normalize_resolution(r) for r in resolutions]
                # Ищем общие слова и фразы
                common_terms = self._extract_common_terms(normalized_resolutions, min_count=2)
                result[category_id] = [r for r in resolutions][:5]  # берем до 5 примеров решений
            else:
                result[category_id] = resolutions

        return result

    def _normalize_resolution(self, resolution: str) -> str:
        """
        Нормализует текст решения для лучшего сравнения.

        Args:
            resolution: Исходный текст решения

        Returns:
            Нормализованный текст
        """
        # Приводим к нижнему регистру
        text = resolution.lower()
        # Удаляем спецсимволы, оставляя пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        # Заменяем множественные пробелы одним
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def suggest_resolution(self, error: ErrorInstance) -> Optional[str]:
        """
        Предлагает возможное решение проблемы на основе похожих ошибок.

        Args:
            error: Ошибка, для которой нужно предложить решение

        Returns:
            Предлагаемое решение или None, если не удалось найти
        """
        # Находим похожие ошибки
        similar_errors = self.get_similar_errors(error, limit=10)

        # Фильтруем только разрешенные ошибки с описанием решения
        resolved_errors = [
            err["error"] for err in similar_errors
            if err["error"].get("resolved") and err["error"].get("resolution")
        ]

        if not resolved_errors:
            return None

        # Если ошибки относятся к одной категории, предлагаем наиболее частое решение
        if error.category_id:
            # Получаем паттерны разрешения для категории
            resolution_patterns = self.extract_resolution_patterns().get(error.category_id, [])
            if resolution_patterns:
                return resolution_patterns[0]  # Возвращаем первый (наиболее частый) паттерн

        # Если нет категории или паттернов для нее, берем решение наиболее похожей ошибки
        if resolved_errors:
            return resolved_errors[0].get("resolution")

        return None


# Продолжение будет в следующих частях файла
