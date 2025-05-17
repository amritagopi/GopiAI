"""
Модуль управления агентами приложения.

Предоставляет единую точку доступа к различным типам агентов
и управляет их жизненным циклом.
"""

import threading
from typing import Any, Dict, List, Optional, Type

from app.agent.base import BaseAgent
from app.agent.coding_agent import CodingAgent
from app.agent.manus import Manus
from app.agent.planning import PlanningAgent
from app.agent.react import ReActAgent
from app.agent.toolcall import ReactAgent
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
        "coding": CodingAgent,
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
                    self._default_agent_type = "reactive"  # Меняем тип агента по умолчанию на "reactive" (ReactAgent)

                    # Активные агенты для разных компонентов интерфейса
                    self._active_agents: Dict[str, BaseAgent] = {}

                    self._initialized = True

    @classmethod
    def instance(cls) -> "AgentManager":
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
                logger.error(f"Error creating default agent: '{str(e)}'")
                # Если не удалось создать указанный тип, пробуем создать ReactAgent
                try:
                    # Используем ReactAgent из app.agent.toolcall
                    self._default_agent = ReactAgent()
                    logger.info("Created ReactAgent as fallback default agent")
                except Exception as e2:
                    logger.error(f"Error creating ReactAgent: '{str(e2)}'")
                    # Если и это не удалось, создаем пустой базовый агент
                    try:
                        from app.agent.base import BaseAgent

                        self._default_agent = BaseAgent()
                        logger.info("Created BaseAgent as fallback")
                    except Exception as e3:
                        logger.error(f"Error creating BaseAgent: '{str(e3)}'")
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

    # Новые методы для расширенной функциональности

    def create_coding_agent(self, **kwargs) -> CodingAgent:
        """
        Создает и возвращает агент для работы с кодом.

        Args:
            **kwargs: Аргументы для конструктора CodingAgent

        Returns:
            Экземпляр CodingAgent
        """
        try:
            agent = self.create_agent("coding", **kwargs)
            if isinstance(agent, CodingAgent):
                logger.info("Created coding agent")
                return agent
            else:
                # Если create_agent вернул резервный агент другого типа
                logger.warning("Failed to create coding agent, creating directly")
                agent = CodingAgent(**kwargs)
                agent_id = f"coding_{id(agent)}"
                self._agents[agent_id] = agent
                return agent
        except Exception as e:
            logger.error(f"Error creating coding agent: {e}")
            # В случае ошибки возвращаем новый экземпляр CodingAgent
            # без дополнительных настроек
            agent = CodingAgent()
            agent_id = f"coding_{id(agent)}"
            self._agents[agent_id] = agent
            return agent

    def get_active_agents(self) -> List[BaseAgent]:
        """
        Возвращает список всех активных агентов.

        Returns:
            Список активных агентов
        """
        return list(self._active_agents.values())

    def set_active_agent(self, component_id: str, agent: BaseAgent) -> None:
        """
        Устанавливает активный агент для указанного компонента интерфейса.

        Args:
            component_id: Идентификатор компонента интерфейса
            agent: Экземпляр агента
        """
        self._active_agents[component_id] = agent
        logger.info(f"Set active agent for component {component_id}")

    def get_active_agent(self, component_id: str) -> Optional[BaseAgent]:
        """
        Возвращает активный агент для указанного компонента интерфейса.

        Args:
            component_id: Идентификатор компонента интерфейса

        Returns:
            Экземпляр агента или None, если агент не найден
        """
        return self._active_agents.get(component_id)

    def clear_inactive_agents(self) -> int:
        """
        Удаляет неактивные агенты из словаря _agents.

        Агент считается неактивным, если он не является активным ни для одного
        из компонентов интерфейса и не является агентом по умолчанию.

        Returns:
            Количество удаленных агентов
        """
        active_agent_ids = {id(agent) for agent in self._active_agents.values()}
        if self._default_agent:
            active_agent_ids.add(id(self._default_agent))

        keys_to_delete = []
        for agent_id, agent in self._agents.items():
            if id(agent) not in active_agent_ids:
                keys_to_delete.append(agent_id)

        for key in keys_to_delete:
            del self._agents[key]

        logger.info(f"Cleared {len(keys_to_delete)} inactive agents")
        return len(keys_to_delete)
