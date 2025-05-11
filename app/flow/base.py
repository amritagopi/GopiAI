from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, ConfigDict

from app.agent.base import BaseAgent
from app.interfaces import IFlow, IAgent


class FlowType(str, Enum):
    PLANNING = "planning"
    AGENT = "agent"
    HYBRID = "hybrid"


class BaseFlow(BaseModel, IFlow):
    """Base class for execution flows supporting multiple agents.

    Implements the IFlow interface to ensure standardized component interactions.
    """

    name: str = "base_flow"
    agents: Dict[str, BaseAgent]
    tools: Optional[List] = None
    primary_agent_key: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self, agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]], **data
    ):
        # Handle different ways of providing agents
        if isinstance(agents, BaseAgent):
            agents_dict = {"default": agents}
        elif isinstance(agents, list):
            agents_dict = {f"agent_{i}": agent for i, agent in enumerate(agents)}
        else:
            agents_dict = agents

        # If primary agent not specified, use first agent
        primary_key = data.get("primary_agent_key")
        if not primary_key and agents_dict:
            primary_key = next(iter(agents_dict))
            data["primary_agent_key"] = primary_key

        # Set the agents dictionary
        data["agents"] = agents_dict

        # Ensure name is present
        if "name" not in data:
            data["name"] = "base_flow"

        # Initialize using BaseModel's init
        super().__init__(**data)

    @property
    def name(self) -> str:
        """Возвращает имя потока.

        Реализует метод из интерфейса IFlow.

        Returns:
            str: Имя потока
        """
        return self.name

    @property
    def primary_agent(self) -> Optional[IAgent]:
        """Get the primary agent for the flow.

        Implements primary_agent property from IFlow interface.

        Returns:
            Optional[IAgent]: Основной агент или None
        """
        return self.agents.get(self.primary_agent_key)

    def get_agent(self, key: str) -> Optional[IAgent]:
        """Get a specific agent by key.

        Implements get_agent method from IFlow interface.

        Args:
            key: Ключ агента

        Returns:
            Optional[IAgent]: Агент или None, если агент не найден
        """
        return self.agents.get(key)

    def add_agent(self, key: str, agent: IAgent) -> None:
        """Add a new agent to the flow.

        Implements add_agent method from IFlow interface.

        Args:
            key: Ключ агента
            agent: Экземпляр агента
        """
        # Проверка типа для обеспечения совместимости
        if not isinstance(agent, BaseAgent):
            raise TypeError(f"Agent must be an instance of BaseAgent, got {type(agent)}")

        self.agents[key] = agent

    @abstractmethod
    async def execute(self, input_text: str, **kwargs) -> str:
        """Execute the flow with given input.

        Implements execute method from IFlow interface.

        Args:
            input_text: Входной текст для выполнения
            **kwargs: Дополнительные параметры для выполнения

        Returns:
            str: Результат выполнения
        """
        pass
