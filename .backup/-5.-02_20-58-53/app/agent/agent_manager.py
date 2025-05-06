"""
Модуль управления агентами приложения.

Предоставляет единую точку доступа к различным типам агентов
и управляет их жизненным циклом.
"""

import threading
from typing import Dict, Optional, Type, Any

from app.agent.base import BaseAgent
from app.agent.react import ReActAgent
from app.agent.toolcall import ReactAgent
from app.agent.planning import PlanningAgent
from app.agent.manus import Manus
from app.logger import logger


class AgentManager:
    """
    Синглтон для управления агентами приложения.

    Предоставляет методы для создания и получения экземпляров различных типов агентов,
    а также управления их настройками и состоянием.
    """
    _instance = None
    _lock = threading.Lock()

    # Словарь, связывающий строковые идентификаторы с классами агентов
    AGENT_TYPES = {
        "react": ReActAgent,
        "reactive": ReactAgent,
        "planning": PlanningAgent,
        "manus": Manus,
    }

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AgentManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    # Словарь для хранения экземпляров агентов
                    self._agents: Dict[str, BaseAgent] = {}
                    # Экземпляр агента по умолчанию
                    self._default_agent: Optional[BaseAgent] = None
                    self._default_agent_type = "manus"  # Тип агента по умолчанию
                    self._initialized = True

    @classmethod
    def instance(cls) -> 'AgentManager':
        """Возвращает экземпляр синглтона."""
        if cls._instance is None:
            cls._instance = AgentManager()
        return cls._instance

    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        """
        Возвращает класс агента по его типу.

        Args:
            agent_type: Строковый идентификатор типа агента

        Returns:
            Класс агента

        Raises:
            ValueError: Если указан неизвестный тип агента
        """
        agent_class = self.AGENT_TYPES.get(agent_type.lower())
        if agent_class is None:
            available_types = ", ".join(self.AGENT_TYPES.keys())
            raise ValueError(
                f"Unknown agent type: {agent_type}. Available types: {available_types}"
            )
        return agent_class

    def create_agent(self, agent_type: str, **kwargs) -> BaseAgent:
        """
        Создает экземпляр агента указанного типа.

        Args:
            agent_type: Строковый идентификатор типа агента
            **kwargs: Аргументы для конструктора агента

        Returns:
            Экземпляр агента
        """
        # Получаем класс агента
        agent_class = self.get_agent_class(agent_type)

        # Создаем и сохраняем экземпляр агента
        try:
            agent = agent_class(**kwargs)
            agent_id = f"{agent_type}_{id(agent)}"
            self._agents[agent_id] = agent
            return agent
        except Exception as e:
            logger.error(f"Error creating agent of type {agent_type}: {e}")
            # В случае ошибки создаем простой резервный агент
            logger.info("Creating fallback agent")
            return self.create_default_agent()

    def create_default_agent(self) -> BaseAgent:
        """
        Создает агент по умолчанию, если он еще не создан.

        Returns:
            Экземпляр агента по умолчанию
        """
        if self._default_agent is None:
            try:
                # Создаем агент с настройками по умолчанию
                agent_class = self.get_agent_class(self._default_agent_type)
                self._default_agent = agent_class()
                logger.info(f"Created default agent of type {self._default_agent_type}")
            except Exception as e:
                logger.error(f"Error creating default agent: {e}")
                # Если не удалось создать указанный тип, пробуем создать Manus
                try:
                    self._default_agent = Manus()
                    logger.info("Created Manus as fallback default agent")
                except Exception as e2:
                    logger.error(f"Error creating Manus agent: {e2}")
                    # Если и это не удалось, возвращаем None
                    return None

        return self._default_agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Возвращает экземпляр агента по его идентификатору.

        Args:
            agent_id: Идентификатор агента

        Returns:
            Экземпляр агента или None, если агент не найден
        """
        return self._agents.get(agent_id)

    def get_default_agent(self) -> Optional[BaseAgent]:
        """
        Возвращает агент по умолчанию, создавая его при необходимости.

        Returns:
            Экземпляр агента по умолчанию
        """
        if self._default_agent is None:
            self.create_default_agent()
        return self._default_agent
