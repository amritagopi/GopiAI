"""
Модуль персонализации для Reasoning Agent

Позволяет адаптировать поведение агента на основе истории взаимодействия с пользователем.
Отслеживает предпочтения, частые задачи и паттерны использования.
"""

import json
import os
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import time

from app.logger import logger


class InteractionType(str, Enum):
    """Типы взаимодействий, которые отслеживает система персонализации"""
    COMMAND = "command"                # Выполнение команды
    FILE_ACCESS = "file_access"        # Доступ к файлам
    BROWSER_ACTION = "browser_action"  # Взаимодействие с браузером
    PLAN_APPROVAL = "plan_approval"    # Одобрение плана
    PLAN_REJECTION = "plan_rejection"  # Отклонение плана
    FEEDBACK = "feedback"              # Явная обратная связь


class ContentDomain(str, Enum):
    """Домены контента, с которыми работает пользователь"""
    WEB_DEVELOPMENT = "web_development"
    DATA_SCIENCE = "data_science"
    DEVOPS = "devops"
    MOBILE_DEVELOPMENT = "mobile_development"
    GENERAL_SOFTWARE = "general_software"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    UI_UX = "ui_ux"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASE = "database"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    OTHER = "other"


@dataclass
class UserPreference:
    """Модель предпочтений пользователя по определенному аспекту"""
    preference_id: str
    name: str
    value: float = 0.5  # от 0.0 до 1.0
    confidence: float = 0.0  # от 0.0 до 1.0
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    evidence_count: int = 0

    def update(self, new_value: float, evidence_weight: float = 1.0) -> None:
        """
        Обновляет значение предпочтения с учетом нового свидетельства

        Args:
            new_value: Новое значение (от 0.0 до 1.0)
            evidence_weight: Вес свидетельства (от 0.0 до 1.0)
        """
        # Ограничиваем значения диапазоном от 0 до 1
        new_value = max(0.0, min(1.0, new_value))
        evidence_weight = max(0.0, min(1.0, evidence_weight))

        # Рассчитываем новую уверенность (не может превышать 0.95)
        self.confidence = min(0.95, self.confidence + (1.0 - self.confidence) * evidence_weight * 0.1)

        # Обновляем значение с учетом текущей уверенности
        if self.evidence_count == 0:
            self.value = new_value
        else:
            self.value = (self.value * self.confidence) + (new_value * (1.0 - self.confidence))

        self.evidence_count += 1
        self.last_updated = datetime.datetime.now()


@dataclass
class UserInteraction:
    """Запись о взаимодействии пользователя с агентом"""
    interaction_id: str
    timestamp: datetime.datetime
    interaction_type: InteractionType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    duration: float = 0.0

    @classmethod
    def create(cls, interaction_type: InteractionType, content: str,
               metadata: Optional[Dict[str, Any]] = None, success: bool = True) -> "UserInteraction":
        """
        Создает новую запись о взаимодействии

        Args:
            interaction_type: Тип взаимодействия
            content: Содержание взаимодействия
            metadata: Дополнительные метаданные
            success: Флаг успешности взаимодействия

        Returns:
            Новый объект взаимодействия
        """
        interaction_id = f"{interaction_type.value}_{int(time.time())}_{hash(content) % 10000}"
        return cls(
            interaction_id=interaction_id,
            timestamp=datetime.datetime.now(),
            interaction_type=interaction_type,
            content=content,
            metadata=metadata or {},
            success=success,
            duration=0.0
        )


@dataclass
class UserProfile:
    """Профиль пользователя с предпочтениями и историей взаимодействий"""
    user_id: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_active: datetime.datetime = field(default_factory=datetime.datetime.now)
    preferences: Dict[str, UserPreference] = field(default_factory=dict)
    recent_interactions: List[UserInteraction] = field(default_factory=list)
    content_domains: Dict[ContentDomain, float] = field(default_factory=lambda: defaultdict(float))
    frequent_tasks: Dict[str, int] = field(default_factory=dict)
    common_files: Dict[str, int] = field(default_factory=dict)
    learning_rate: float = 0.1  # Скорость обучения профиля
    max_recent_interactions: int = 1000  # Максимальное количество сохраняемых взаимодействий

    def add_interaction(self, interaction: UserInteraction) -> None:
        """
        Добавляет запись о взаимодействии в профиль

        Args:
            interaction: Запись о взаимодействии
        """
        self.recent_interactions.append(interaction)
        self.last_active = datetime.datetime.now()

        # Ограничиваем количество сохраняемых взаимодействий
        if len(self.recent_interactions) > self.max_recent_interactions:
            self.recent_interactions = self.recent_interactions[-self.max_recent_interactions:]

    def update_content_domain(self, domain: ContentDomain, strength: float = 0.1) -> None:
        """
        Обновляет значимость определенного домена контента для пользователя

        Args:
            domain: Домен контента
            strength: Сила ассоциации (от 0.0 до 1.0)
        """
        current = self.content_domains[domain]
        self.content_domains[domain] = current + (strength * (1.0 - current))

    def update_frequent_task(self, task_signature: str) -> None:
        """
        Обновляет счетчик частых задач

        Args:
            task_signature: Сигнатура задачи
        """
        self.frequent_tasks[task_signature] = self.frequent_tasks.get(task_signature, 0) + 1

    def update_common_file(self, file_path: str) -> None:
        """
        Обновляет счетчик часто используемых файлов

        Args:
            file_path: Путь к файлу
        """
        self.common_files[file_path] = self.common_files.get(file_path, 0) + 1

    def get_preference(self, preference_id: str, default_value: float = 0.5) -> float:
        """
        Получает значение предпочтения

        Args:
            preference_id: Идентификатор предпочтения
            default_value: Значение по умолчанию, если предпочтение не найдено

        Returns:
            Значение предпочтения
        """
        if preference_id in self.preferences:
            return self.preferences[preference_id].value
        return default_value

    def set_preference(self, preference_id: str, name: str, value: float,
                       confidence: float = 0.5) -> None:
        """
        Устанавливает значение предпочтения

        Args:
            preference_id: Идентификатор предпочтения
            name: Название предпочтения
            value: Значение предпочтения (от 0.0 до 1.0)
            confidence: Уверенность в значении (от 0.0 до 1.0)
        """
        if preference_id in self.preferences:
            self.preferences[preference_id].update(value, confidence)
        else:
            self.preferences[preference_id] = UserPreference(
                preference_id=preference_id,
                name=name,
                value=value,
                confidence=confidence
            )

    def get_top_domains(self, limit: int = 3) -> List[Tuple[ContentDomain, float]]:
        """
        Получает список основных доменов контента пользователя

        Args:
            limit: Максимальное количество доменов

        Returns:
            Список кортежей (домен, значимость)
        """
        sorted_domains = sorted(
            self.content_domains.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_domains[:limit]

    def get_top_tasks(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Получает список наиболее частых задач

        Args:
            limit: Максимальное количество задач

        Returns:
            Список кортежей (задача, количество)
        """
        return Counter(self.frequent_tasks).most_common(limit)

    def get_top_files(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Получает список наиболее часто используемых файлов

        Args:
            limit: Максимальное количество файлов

        Returns:
            Список кортежей (файл, количество)
        """
        return Counter(self.common_files).most_common(limit)

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует профиль в словарь для сериализации

        Returns:
            Словарь с данными профиля
        """
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "preferences": {
                k: {
                    "preference_id": v.preference_id,
                    "name": v.name,
                    "value": v.value,
                    "confidence": v.confidence,
                    "last_updated": v.last_updated.isoformat(),
                    "evidence_count": v.evidence_count
                } for k, v in self.preferences.items()
            },
            "recent_interactions": [
                {
                    "interaction_id": i.interaction_id,
                    "timestamp": i.timestamp.isoformat(),
                    "interaction_type": i.interaction_type.value,
                    "content": i.content,
                    "metadata": i.metadata,
                    "success": i.success,
                    "duration": i.duration
                } for i in self.recent_interactions
            ],
            "content_domains": {k.value: v for k, v in self.content_domains.items()},
            "frequent_tasks": self.frequent_tasks,
            "common_files": self.common_files,
            "learning_rate": self.learning_rate,
            "max_recent_interactions": self.max_recent_interactions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """
        Создает профиль из словаря

        Args:
            data: Словарь с данными профиля

        Returns:
            Объект профиля
        """
        profile = cls(
            user_id=data["user_id"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            last_active=datetime.datetime.fromisoformat(data["last_active"]),
            learning_rate=data.get("learning_rate", 0.1),
            max_recent_interactions=data.get("max_recent_interactions", 1000)
        )

        # Загружаем предпочтения
        for pref_id, pref_data in data.get("preferences", {}).items():
            profile.preferences[pref_id] = UserPreference(
                preference_id=pref_data["preference_id"],
                name=pref_data["name"],
                value=pref_data["value"],
                confidence=pref_data["confidence"],
                last_updated=datetime.datetime.fromisoformat(pref_data["last_updated"]),
                evidence_count=pref_data["evidence_count"]
            )

        # Загружаем взаимодействия
        for interaction_data in data.get("recent_interactions", []):
            profile.recent_interactions.append(UserInteraction(
                interaction_id=interaction_data["interaction_id"],
                timestamp=datetime.datetime.fromisoformat(interaction_data["timestamp"]),
                interaction_type=InteractionType(interaction_data["interaction_type"]),
                content=interaction_data["content"],
                metadata=interaction_data["metadata"],
                success=interaction_data["success"],
                duration=interaction_data["duration"]
            ))

        # Загружаем домены контента
        for domain_str, value in data.get("content_domains", {}).items():
            try:
                domain = ContentDomain(domain_str)
                profile.content_domains[domain] = value
            except ValueError:
                # Пропускаем неизвестные домены
                pass

        # Загружаем частые задачи и файлы
        profile.frequent_tasks = data.get("frequent_tasks", {})
        profile.common_files = data.get("common_files", {})

        return profile


class PersonalizationManager:
    """
    Менеджер персонализации для адаптации поведения агента
    к предпочтениям пользователя
    """

    def __init__(self, storage_dir: str = "data/personalization"):
        """
        Инициализирует менеджер персонализации

        Args:
            storage_dir: Директория для хранения профилей
        """
        self.storage_dir = storage_dir
        self.profiles: Dict[str, UserProfile] = {}
        self.active_profile_id: Optional[str] = None
        self.content_analyzers: Dict[ContentDomain, List[str]] = self._initialize_content_analyzers()
        self.task_patterns: Dict[str, List[str]] = self._initialize_task_patterns()

        # Создаем директорию для хранения, если она не существует
        os.makedirs(storage_dir, exist_ok=True)

        logger.info(f"Персонализация: инициализирован менеджер с хранилищем в {storage_dir}")

    def _initialize_content_analyzers(self) -> Dict[ContentDomain, List[str]]:
        """
        Инициализирует анализаторы контента для определения домена

        Returns:
            Словарь с ключевыми словами для каждого домена
        """
        return {
            ContentDomain.WEB_DEVELOPMENT: ["html", "css", "javascript", "react", "vue", "angular", "dom", "frontend", "web", "ajax", "spa"],
            ContentDomain.DATA_SCIENCE: ["data", "pandas", "numpy", "matplotlib", "visualization", "analysis", "statistics", "machine learning", "dataset", "jupyter"],
            ContentDomain.DEVOPS: ["docker", "kubernetes", "cicd", "pipeline", "deployment", "jenkins", "ansible", "terraform", "infrastructure", "aws", "cloud"],
            ContentDomain.MOBILE_DEVELOPMENT: ["android", "ios", "flutter", "react native", "swift", "kotlin", "mobile app", "apk", "xcode", "mobile ui"],
            ContentDomain.DATABASE: ["sql", "database", "mysql", "postgresql", "mongodb", "sqlite", "query", "orm", "schema", "nosql", "index"],
            ContentDomain.ARTIFICIAL_INTELLIGENCE: ["ai", "ml", "deep learning", "neural network", "nlp", "tensorflow", "pytorch", "model", "training", "inference"],
            ContentDomain.TESTING: ["test", "unit test", "integration test", "assert", "mocking", "pytest", "jest", "tdd", "qa", "validation"],
            ContentDomain.UI_UX: ["ui", "ux", "design", "interface", "user experience", "accessibility", "responsive", "wireframe", "prototype", "usability"],
            ContentDomain.BACKEND: ["api", "server", "endpoint", "rest", "graphql", "microservice", "authorization", "authentication", "middleware"],
            ContentDomain.FRONTEND: ["component", "state", "render", "ui framework", "responsive", "css", "html", "javascript", "typescript", "jsx"],
            ContentDomain.DOCUMENTATION: ["docs", "documentation", "readme", "wiki", "tutorial", "guide", "explanation", "api docs", "markdown", "comments"],
            ContentDomain.GENERAL_SOFTWARE: ["algorithm", "design pattern", "code structure", "optimization", "refactoring", "bug fix", "feature", "framework"],
        }

    def _initialize_task_patterns(self) -> Dict[str, List[str]]:
        """
        Инициализирует шаблоны для распознавания типичных задач

        Returns:
            Словарь с ключевыми словами для каждого типа задачи
        """
        return {
            "code_search": ["найди", "поиск", "где находится", "найти код", "покажи код"],
            "code_explanation": ["объясни", "что делает", "как работает", "в чем смысл"],
            "code_refactoring": ["рефакторинг", "улучши", "оптимизируй", "перепиши", "исправь"],
            "code_generation": ["создай", "напиши", "сгенерируй", "реализуй"],
            "bug_fixing": ["исправь ошибку", "баг", "ошибка", "не работает", "починить"],
            "documentation": ["документация", "опиши", "поясни", "комментарии", "задокументируй"],
            "file_operations": ["создай файл", "удали файл", "переименуй", "переместить"],
            "environment_setup": ["настрой окружение", "конфигурация", "установи", "подготовь среду"]
        }

    def create_profile(self, user_id: str) -> UserProfile:
        """
        Создает новый профиль пользователя

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Новый профиль пользователя
        """
        profile = UserProfile(user_id=user_id)
        self.profiles[user_id] = profile
        self.active_profile_id = user_id

        # Инициализируем базовые предпочтения
        self._initialize_default_preferences(profile)

        logger.info(f"Персонализация: создан новый профиль для пользователя {user_id}")
        return profile

    def _initialize_default_preferences(self, profile: UserProfile) -> None:
        """
        Инициализирует профиль стандартными предпочтениями

        Args:
            profile: Профиль пользователя
        """
        default_preferences = [
            ("verbosity", "Подробность объяснений", 0.5),
            ("code_comments", "Уровень комментирования кода", 0.5),
            ("risk_tolerance", "Толерантность к риску", 0.3),
            ("auto_suggestions", "Автоматические предложения", 0.5),
            ("tech_level", "Технический уровень", 0.5),
            ("detailed_planning", "Детализация планирования", 0.5),
            ("interactive_confirmation", "Интерактивное подтверждение", 0.7),
            ("code_style", "Стиль кода", 0.5),
            ("ui_complexity", "Сложность пользовательского интерфейса", 0.5),
            ("notification_level", "Уровень уведомлений", 0.5)
        ]

        for pref_id, name, default_value in default_preferences:
            profile.set_preference(pref_id, name, default_value, confidence=0.2)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Получает профиль пользователя

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Профиль пользователя или None, если профиль не найден
        """
        return self.profiles.get(user_id)

    def get_active_profile(self) -> Optional[UserProfile]:
        """
        Получает активный профиль пользователя

        Returns:
            Активный профиль пользователя или None, если нет активного профиля
        """
        if self.active_profile_id:
            return self.profiles.get(self.active_profile_id)
        return None

    def set_active_profile(self, user_id: str) -> bool:
        """
        Устанавливает активный профиль пользователя

        Args:
            user_id: Идентификатор пользователя

        Returns:
            True, если профиль установлен, иначе False
        """
        if user_id in self.profiles:
            self.active_profile_id = user_id
            return True
        return False

    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Загружает профиль пользователя из хранилища

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Загруженный профиль или None, если профиль не найден
        """
        profile_path = os.path.join(self.storage_dir, f"{user_id}.json")

        if not os.path.exists(profile_path):
            logger.warning(f"Персонализация: профиль для {user_id} не найден")
            return None

        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = UserProfile.from_dict(data)
                self.profiles[user_id] = profile
                logger.info(f"Персонализация: загружен профиль для {user_id}")
                return profile
        except Exception as e:
            logger.error(f"Персонализация: ошибка загрузки профиля {user_id}: {str(e)}")
            return None

    def save_profile(self, user_id: Optional[str] = None) -> bool:
        """
        Сохраняет профиль пользователя в хранилище

        Args:
            user_id: Идентификатор пользователя (если None, сохраняет активный профиль)

        Returns:
            True, если профиль сохранен, иначе False
        """
        if user_id is None:
            user_id = self.active_profile_id

        if not user_id or user_id not in self.profiles:
            logger.warning(f"Персонализация: невозможно сохранить профиль {user_id}: профиль не найден")
            return False

        profile_path = os.path.join(self.storage_dir, f"{user_id}.json")

        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(self.profiles[user_id].to_dict(), f, ensure_ascii=False, indent=2)
                logger.info(f"Персонализация: сохранен профиль для {user_id}")
                return True
        except Exception as e:
            logger.error(f"Персонализация: ошибка сохранения профиля {user_id}: {str(e)}")
            return False

    def record_interaction(self, interaction_type: InteractionType, content: str,
                          metadata: Optional[Dict[str, Any]] = None,
                          success: bool = True) -> Optional[str]:
        """
        Записывает взаимодействие в активный профиль пользователя

        Args:
            interaction_type: Тип взаимодействия
            content: Содержание взаимодействия
            metadata: Дополнительные метаданные
            success: Флаг успешности взаимодействия

        Returns:
            Идентификатор взаимодействия или None, если нет активного профиля
        """
        profile = self.get_active_profile()
        if not profile:
            logger.warning("Персонализация: невозможно записать взаимодействие: нет активного профиля")
            return None

        interaction = UserInteraction.create(
            interaction_type=interaction_type,
            content=content,
            metadata=metadata,
            success=success
        )

        profile.add_interaction(interaction)

        # Анализируем взаимодействие для обновления профиля
        self._analyze_interaction(interaction, profile)

        return interaction.interaction_id

    def _analyze_interaction(self, interaction: UserInteraction, profile: UserProfile) -> None:
        """
        Анализирует взаимодействие для обновления профиля

        Args:
            interaction: Взаимодействие
            profile: Профиль пользователя
        """
        content = interaction.content.lower()

        # Определяем домен контента
        domains = self._detect_content_domains(content)
        for domain, score in domains:
            profile.update_content_domain(domain, score * 0.2)

        # Определяем тип задачи
        task_type = self._detect_task_type(content)
        if task_type:
            profile.update_frequent_task(task_type)

        # Анализируем файловые операции
        if interaction.interaction_type == InteractionType.FILE_ACCESS:
            file_path = interaction.metadata.get("file_path")
            if file_path:
                profile.update_common_file(file_path)

        # Анализируем одобрение/отклонение планов
        if interaction.interaction_type == InteractionType.PLAN_APPROVAL:
            # Увеличиваем значение для уровня детализации планирования
            current_value = profile.get_preference("detailed_planning")
            plan_complexity = interaction.metadata.get("plan_complexity", 0.5)
            # Если сложный план одобрен, увеличиваем предпочтение детального планирования
            if plan_complexity > 0.6:
                profile.set_preference("detailed_planning", "Детализация планирования",
                                      min(1.0, current_value + 0.05), 0.6)

        if interaction.interaction_type == InteractionType.PLAN_REJECTION:
            risk_level = interaction.metadata.get("risk_level", 0.5)
            # Если отклонен рискованный план, уменьшаем толерантность к риску
            if risk_level > 0.6:
                current_value = profile.get_preference("risk_tolerance")
                profile.set_preference("risk_tolerance", "Толерантность к риску",
                                      max(0.0, current_value - 0.05), 0.6)

        # Обрабатываем явную обратную связь
        if interaction.interaction_type == InteractionType.FEEDBACK:
            feedback_type = interaction.metadata.get("feedback_type")
            if feedback_type == "verbosity":
                value = interaction.metadata.get("value", 0.5)
                profile.set_preference("verbosity", "Подробность объяснений", value, 0.8)
            elif feedback_type == "code_style":
                value = interaction.metadata.get("value", 0.5)
                profile.set_preference("code_style", "Стиль кода", value, 0.8)

    def _detect_content_domains(self, content: str) -> List[Tuple[ContentDomain, float]]:
        """
        Определяет домены контента на основе текста

        Args:
            content: Текст для анализа

        Returns:
            Список кортежей (домен, уверенность)
        """
        domains = []
        content = content.lower()

        for domain, keywords in self.content_analyzers.items():
            score = 0.0
            matches = 0

            for keyword in keywords:
                if keyword.lower() in content:
                    matches += 1

            if matches > 0:
                # Нормализуем оценку от 0.1 до 0.9
                score = 0.1 + (0.8 * min(1.0, matches / min(3, len(keywords))))
                domains.append((domain, score))

        # Если не нашли совпадений, добавляем OTHER
        if not domains:
            domains.append((ContentDomain.OTHER, 0.5))

        # Сортируем по убыванию оценки
        return sorted(domains, key=lambda x: x[1], reverse=True)

    def _detect_task_type(self, content: str) -> Optional[str]:
        """
        Определяет тип задачи на основе текста

        Args:
            content: Текст для анализа

        Returns:
            Тип задачи или None, если тип не определен
        """
        content = content.lower()

        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content:
                    return task_type

        return None

    def get_personalized_parameters(self) -> Dict[str, Any]:
        """
        Получает персонализированные параметры для адаптации поведения агента

        Returns:
            Словарь с персонализированными параметрами
        """
        profile = self.get_active_profile()
        if not profile:
            return {
                "verbosity": 0.5,
                "code_comments": 0.5,
                "risk_tolerance": 0.3,
                "auto_suggestions": 0.5,
                "detailed_planning": 0.5,
                "interactive_confirmation": 0.7,
                "main_domains": [ContentDomain.GENERAL_SOFTWARE.value],
                "personalized": False
            }

        # Получаем основные предпочтения
        params = {
            "verbosity": profile.get_preference("verbosity"),
            "code_comments": profile.get_preference("code_comments"),
            "risk_tolerance": profile.get_preference("risk_tolerance"),
            "auto_suggestions": profile.get_preference("auto_suggestions"),
            "tech_level": profile.get_preference("tech_level"),
            "detailed_planning": profile.get_preference("detailed_planning"),
            "interactive_confirmation": profile.get_preference("interactive_confirmation"),
            "code_style": profile.get_preference("code_style"),
            "ui_complexity": profile.get_preference("ui_complexity"),
            "notification_level": profile.get_preference("notification_level"),
            "personalized": True
        }

        # Добавляем основные домены контента
        top_domains = profile.get_top_domains(3)
        params["main_domains"] = [domain.value for domain, _ in top_domains]

        # Добавляем часто используемые файлы и задачи
        params["frequent_tasks"] = profile.get_top_tasks(5)
        params["common_files"] = profile.get_top_files(5)

        return params

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """
        Анализирует задачу и предоставляет персонализированные рекомендации

        Args:
            task: Описание задачи

        Returns:
            Словарь с рекомендациями
        """
        profile = self.get_active_profile()
        if not profile:
            return {
                "personalized": False,
                "task_type": None,
                "recommended_approach": "standard",
                "risk_level": "medium",
                "detail_level": "medium"
            }

        # Определяем тип задачи
        task_type = self._detect_task_type(task)

        # Определяем домены контента
        domains = self._detect_content_domains(task)

        # Адаптируем рекомендации на основе предпочтений пользователя
        risk_tolerance = profile.get_preference("risk_tolerance")
        detail_level = profile.get_preference("detailed_planning")

        # Определяем подход на основе типа задачи и предпочтений
        recommended_approach = "standard"
        if task_type == "code_generation" and risk_tolerance > 0.6:
            recommended_approach = "rapid_prototyping"
        elif task_type == "code_refactoring" and detail_level > 0.6:
            recommended_approach = "thorough_analysis"
        elif task_type == "bug_fixing":
            recommended_approach = "diagnostic"

        # Устанавливаем уровень риска
        risk_level = "medium"
        if "rm" in task.lower() or "delete" in task.lower() or "удали" in task.lower():
            risk_level = "high"
        elif task_type in ["documentation", "code_explanation"]:
            risk_level = "low"

        # Рекомендуемый уровень детализации
        if detail_level > 0.7:
            detail_recommendation = "high"
        elif detail_level < 0.3:
            detail_recommendation = "low"
        else:
            detail_recommendation = "medium"

        # Анализируем историю для поиска похожих задач
        similar_tasks = self._find_similar_tasks(task, profile)

        return {
            "personalized": True,
            "task_type": task_type,
            "domains": [d.value for d, _ in domains[:2]],
            "recommended_approach": recommended_approach,
            "risk_level": risk_level,
            "detail_level": detail_recommendation,
            "similar_tasks": similar_tasks[:3] if similar_tasks else []
        }

    def _find_similar_tasks(self, task: str, profile: UserProfile) -> List[Dict[str, Any]]:
        """
        Находит похожие задачи в истории пользователя

        Args:
            task: Текущая задача
            profile: Профиль пользователя

        Returns:
            Список похожих задач
        """
        task_words = set(task.lower().split())
        similar_tasks = []

        # Ищем похожие взаимодействия
        for interaction in profile.recent_interactions:
            if interaction.interaction_type not in [InteractionType.COMMAND, InteractionType.PLAN_APPROVAL]:
                continue

            content_words = set(interaction.content.lower().split())
            common_words = task_words.intersection(content_words)

            # Если есть хотя бы 3 общих слова, считаем задачу похожей
            if len(common_words) >= 3:
                similar_tasks.append({
                    "content": interaction.content,
                    "timestamp": interaction.timestamp.isoformat(),
                    "success": interaction.success,
                    "interaction_id": interaction.interaction_id
                })

        return similar_tasks

    def export_profile(self, user_id: str, output_path: str) -> bool:
        """
        Экспортирует профиль пользователя в указанный файл

        Args:
            user_id: Идентификатор пользователя
            output_path: Путь для сохранения

        Returns:
            True, если экспорт успешен, иначе False
        """
        profile = self.get_profile(user_id)
        if not profile:
            logger.warning(f"Персонализация: невозможно экспортировать профиль {user_id}: профиль не найден")
            return False

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
                logger.info(f"Персонализация: профиль {user_id} экспортирован в {output_path}")
                return True
        except Exception as e:
            logger.error(f"Персонализация: ошибка экспорта профиля {user_id}: {str(e)}")
            return False

    def import_profile(self, input_path: str) -> Optional[str]:
        """
        Импортирует профиль пользователя из указанного файла

        Args:
            input_path: Путь к файлу профиля

        Returns:
            Идентификатор импортированного профиля или None в случае ошибки
        """
        if not os.path.exists(input_path):
            logger.warning(f"Персонализация: файл профиля {input_path} не найден")
            return None

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = UserProfile.from_dict(data)
                self.profiles[profile.user_id] = profile
                logger.info(f"Персонализация: профиль {profile.user_id} импортирован из {input_path}")
                return profile.user_id
        except Exception as e:
            logger.error(f"Персонализация: ошибка импорта профиля из {input_path}: {str(e)}")
            return None

    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех профилей

        Returns:
            Список с информацией о профилях
        """
        result = []

        for user_id, profile in self.profiles.items():
            result.append({
                "user_id": user_id,
                "created_at": profile.created_at.isoformat(),
                "last_active": profile.last_active.isoformat(),
                "preferences_count": len(profile.preferences),
                "interactions_count": len(profile.recent_interactions),
                "active": user_id == self.active_profile_id
            })

        return result

    def merge_profiles(self, source_id: str, target_id: str) -> bool:
        """
        Объединяет два профиля пользователя

        Args:
            source_id: Идентификатор источника
            target_id: Идентификатор цели

        Returns:
            True, если объединение успешно, иначе False
        """
        source = self.get_profile(source_id)
        target = self.get_profile(target_id)

        if not source or not target:
            logger.warning(f"Персонализация: невозможно объединить профили {source_id} и {target_id}: один из профилей не найден")
            return False

        try:
            # Копируем взаимодействия
            for interaction in source.recent_interactions:
                if interaction.interaction_id not in [i.interaction_id for i in target.recent_interactions]:
                    target.add_interaction(interaction)

            # Объединяем предпочтения
            for pref_id, preference in source.preferences.items():
                if pref_id in target.preferences:
                    # Если предпочтение уже существует в целевом профиле,
                    # обновляем его с учетом обоих значений и уверенности
                    target_pref = target.preferences[pref_id]
                    merged_value = (target_pref.value * target_pref.confidence +
                                   preference.value * preference.confidence) / (
                                   target_pref.confidence + preference.confidence)
                    merged_confidence = max(target_pref.confidence, preference.confidence)
                    target.set_preference(pref_id, target_pref.name, merged_value, merged_confidence)
                else:
                    # Иначе просто копируем предпочтение
                    target.preferences[pref_id] = preference

            # Объединяем домены контента
            for domain, value in source.content_domains.items():
                if domain in target.content_domains:
                    target.content_domains[domain] = max(target.content_domains[domain], value)
                else:
                    target.content_domains[domain] = value

            # Объединяем частые задачи
            for task, count in source.frequent_tasks.items():
                target.frequent_tasks[task] = target.frequent_tasks.get(task, 0) + count

            # Объединяем часто используемые файлы
            for file_path, count in source.common_files.items():
                target.common_files[file_path] = target.common_files.get(file_path, 0) + count

            logger.info(f"Персонализация: профили {source_id} и {target_id} успешно объединены")
            return True
        except Exception as e:
            logger.error(f"Персонализация: ошибка объединения профилей {source_id} и {target_id}: {str(e)}")
            return False
