"""
Менеджер истории сессий для Reasoning Agent

Обеспечивает сохранение, загрузку и управление историей сессий, включая:
- Текстовые диалоги
- Планы
- Деревья мыслей
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.agent.thought_tree import ThoughtTree
from app.logger import logger
from app.config import config


class SessionRecord:
    """
    Запись сессии, содержащая информацию о взаимодействии с агентом.
    """

    def __init__(
        self,
        session_id: str,
        title: str,
        timestamp: float = None,
        dialogue: List[Dict[str, Any]] = None,
        plans: List[Dict[str, Any]] = None,
        thought_tree_data: Dict[str, Any] = None
    ):
        """
        Инициализирует запись сессии.

        Args:
            session_id: Уникальный идентификатор сессии
            title: Название сессии
            timestamp: Временная метка создания сессии (unix timestamp)
            dialogue: Список сообщений диалога
            plans: Список созданных планов
            thought_tree_data: Данные дерева мыслей
        """
        self.session_id = session_id
        self.title = title
        self.timestamp = timestamp or time.time()
        self.dialogue = dialogue or []
        self.plans = plans or []
        self.thought_tree_data = thought_tree_data or {}

    @property
    def formatted_date(self) -> str:
        """Возвращает отформатированную дату создания сессии."""
        dt = datetime.datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def add_message(self, role: str, content: str, timestamp: float = None) -> None:
        """
        Добавляет сообщение в диалог сессии.

        Args:
            role: Роль сообщения ('user', 'assistant', 'system')
            content: Содержимое сообщения
            timestamp: Временная метка сообщения (по умолчанию текущее время)
        """
        self.dialogue.append({
            "role": role,
            "content": content,
            "timestamp": timestamp or time.time()
        })

    def add_plan(self, plan_data: Dict[str, Any]) -> None:
        """
        Добавляет план в историю сессии.

        Args:
            plan_data: Данные плана
        """
        self.plans.append(plan_data)

    def set_thought_tree(self, thought_tree: ThoughtTree) -> None:
        """
        Устанавливает дерево мыслей для сессии.

        Args:
            thought_tree: Дерево мыслей
        """
        if thought_tree:
            self.thought_tree_data = thought_tree.to_dict()

    def get_thought_tree(self) -> Optional[ThoughtTree]:
        """
        Создает объект дерева мыслей из сохраненных данных.

        Returns:
            Объект дерева мыслей или None, если данные отсутствуют
        """
        if not self.thought_tree_data:
            return None

        try:
            return ThoughtTree.from_dict(self.thought_tree_data)
        except Exception as e:
            logger.error(f"Error reconstructing thought tree: {str(e)}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует запись сессии в словарь для сериализации.

        Returns:
            Словарь с данными сессии
        """
        return {
            "session_id": self.session_id,
            "title": self.title,
            "timestamp": self.timestamp,
            "dialogue": self.dialogue,
            "plans": self.plans,
            "thought_tree_data": self.thought_tree_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionRecord":
        """
        Создает запись сессии из словаря.

        Args:
            data: Словарь с данными сессии

        Returns:
            Запись сессии
        """
        return cls(
            session_id=data.get("session_id", ""),
            title=data.get("title", ""),
            timestamp=data.get("timestamp"),
            dialogue=data.get("dialogue", []),
            plans=data.get("plans", []),
            thought_tree_data=data.get("thought_tree_data", {})
        )


class SessionHistoryManager:
    """
    Управляет историей сессий Reasoning Agent.

    Обеспечивает сохранение, загрузку и организацию истории сессий,
    включая текстовые диалоги, планы и деревья мыслей.
    """

    def __init__(self, history_dir: Optional[str] = None):
        """
        Инициализирует менеджер истории сессий.

        Args:
            history_dir: Директория для хранения истории сессий
                        (если None, используется директория из конфигурации)
        """
        # Определяем директорию для хранения истории
        if history_dir:
            self.history_dir = history_dir
        else:
            app_data_dir = config.get_app_data_dir()
            self.history_dir = os.path.join(app_data_dir, "reasoning_history")

        # Создаем директорию, если она не существует
        os.makedirs(self.history_dir, exist_ok=True)

        # Загружаем список сессий
        self.sessions: Dict[str, SessionRecord] = {}
        self._load_sessions_index()

        # Текущая активная сессия
        self.current_session: Optional[SessionRecord] = None

    def _get_index_file_path(self) -> str:
        """Возвращает путь к файлу индекса сессий."""
        return os.path.join(self.history_dir, "sessions_index.json")

    def _get_session_file_path(self, session_id: str) -> str:
        """Возвращает путь к файлу сессии."""
        return os.path.join(self.history_dir, f"session_{session_id}.json")

    def _load_sessions_index(self) -> None:
        """Загружает индекс сессий из файла."""
        index_path = self._get_index_file_path()

        if not os.path.exists(index_path):
            # Создаем пустой индекс
            self._save_sessions_index()
            return

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Загружаем базовую информацию о сессиях
            self.sessions = {}
            for session_info in index_data.get("sessions", []):
                session_id = session_info.get("session_id")
                if session_id:
                    self.sessions[session_id] = SessionRecord(
                        session_id=session_id,
                        title=session_info.get("title", ""),
                        timestamp=session_info.get("timestamp")
                    )

            logger.info(f"Loaded {len(self.sessions)} sessions from index")

        except Exception as e:
            logger.error(f"Error loading sessions index: {str(e)}")
            # Создаем пустой индекс в случае ошибки
            self.sessions = {}
            self._save_sessions_index()

    def _save_sessions_index(self) -> None:
        """Сохраняет индекс сессий в файл."""
        index_path = self._get_index_file_path()

        try:
            # Создаем список с базовой информацией о сессиях
            sessions_info = []
            for session_id, session in self.sessions.items():
                sessions_info.append({
                    "session_id": session_id,
                    "title": session.title,
                    "timestamp": session.timestamp
                })

            # Сортируем сессии по дате (сначала новые)
            sessions_info.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

            # Сохраняем индекс
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        "last_updated": time.time(),
                        "sessions": sessions_info
                    },
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            logger.info(f"Saved {len(sessions_info)} sessions to index")

        except Exception as e:
            logger.error(f"Error saving sessions index: {str(e)}")

    def create_session(self, title: Optional[str] = None) -> SessionRecord:
        """
        Создает новую сессию.

        Args:
            title: Название сессии (если None, будет использована дата)

        Returns:
            Запись новой сессии
        """
        # Генерируем уникальный ID сессии
        session_id = f"{int(time.time())}_{os.urandom(4).hex()}"

        # Определяем название, если не указано
        if not title:
            dt = datetime.datetime.now()
            title = f"Session {dt.strftime('%Y-%m-%d %H:%M')}"

        # Создаем запись сессии
        session = SessionRecord(
            session_id=session_id,
            title=title
        )

        # Добавляем сессию в индекс
        self.sessions[session_id] = session

        # Сохраняем индекс
        self._save_sessions_index()

        # Устанавливаем как текущую
        self.current_session = session

        logger.info(f"Created new session: {title} (id: {session_id})")
        return session

    def save_session(self, session: SessionRecord) -> bool:
        """
        Сохраняет сессию в файл.

        Args:
            session: Запись сессии для сохранения

        Returns:
            True в случае успеха, False при ошибке
        """
        file_path = self._get_session_file_path(session.session_id)

        try:
            # Сохраняем данные сессии
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    session.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            # Обновляем индекс
            self.sessions[session.session_id] = session
            self._save_sessions_index()

            logger.info(f"Saved session: {session.title} (id: {session.session_id})")
            return True

        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {str(e)}")
            return False

    def load_session(self, session_id: str) -> Optional[SessionRecord]:
        """
        Загружает полные данные сессии из файла.

        Args:
            session_id: ID сессии для загрузки

        Returns:
            Запись сессии или None при ошибке
        """
        file_path = self._get_session_file_path(session_id)

        if not os.path.exists(file_path):
            logger.error(f"Session file not found: {file_path}")
            return None

        try:
            # Загружаем данные сессии
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Создаем запись сессии
            session = SessionRecord.from_dict(session_data)

            # Обновляем текущую сессию
            self.current_session = session

            logger.info(f"Loaded session: {session.title} (id: {session.session_id})")
            return session

        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Удаляет сессию.

        Args:
            session_id: ID сессии для удаления

        Returns:
            True в случае успеха, False при ошибке
        """
        file_path = self._get_session_file_path(session_id)

        try:
            # Удаляем файл сессии, если он существует
            if os.path.exists(file_path):
                os.remove(file_path)

            # Удаляем из индекса
            if session_id in self.sessions:
                del self.sessions[session_id]

            # Сбрасываем текущую сессию, если она была удалена
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None

            # Обновляем индекс
            self._save_sessions_index()

            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False

    def get_sessions_list(self) -> List[Dict[str, Any]]:
        """
        Возвращает список сессий, отсортированный по дате (новые в начале).

        Returns:
            Список сессий с базовой информацией
        """
        sessions_list = []
        for session_id, session in self.sessions.items():
            sessions_list.append({
                "session_id": session_id,
                "title": session.title,
                "timestamp": session.timestamp,
                "formatted_date": session.formatted_date
            })

        # Сортируем по дате (новые в начале)
        sessions_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return sessions_list

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """
        Получает сессию по ID.

        Args:
            session_id: ID сессии

        Returns:
            Запись сессии или None, если не найдена
        """
        # Если сессия уже полностью загружена как текущая
        if self.current_session and self.current_session.session_id == session_id:
            return self.current_session

        # Если сессия есть в индексе, но полные данные не загружены
        if session_id in self.sessions:
            return self.load_session(session_id)

        return None
