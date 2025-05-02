from abc import ABC, abstractmethod
from typing import Optional, Any

from pydantic import Field

from app.agent.base import BaseAgent
from app.llm import LLM
from app.schema import AgentState, Memory


class ReActAgent(BaseAgent, ABC):
    """Abstract base class for agents that implement the ReAct paradigm.
    
    This class defines the core interface for agents that follow the ReAct
    (Reasoning and Acting) paradigm, where the agent alternates between
    thinking about what to do next and taking actions.
    """
    name: str
    description: Optional[str] = None

    system_prompt: Optional[str] = None
    next_step_prompt: Optional[str] = None

    llm: Optional[LLM] = Field(default_factory=LLM)
    memory: Memory = Field(default_factory=Memory)
    state: AgentState = AgentState.IDLE
    
    @abstractmethod
    async def think(self) -> bool:
        """Execute the thinking phase of the ReAct paradigm.
        
        Returns:
            bool: True if the agent should finish execution, False otherwise.
        """
        pass
        
    @abstractmethod
    async def act(self) -> Optional[str]:
        """Execute the acting phase of the ReAct paradigm.
        
        Returns:
            Optional[str]: A string describing the action taken, or None.
        """
        pass
        
    async def step(self) -> str:
        """Execute a single step in the agent's workflow.
        
        This implementation handles thinking and acting based on the ReAct paradigm.
        
        Returns:
            A string describing the result of this step.
        """
        # Think phase - determine what to do next
        should_finish = await self.think()
        
        if should_finish or self.state == AgentState.FINISHED:
            self.state = AgentState.FINISHED
            return "Agent has completed its task."
        
        # Act phase - execute any actions
        action_result = await self.act()
        
        return action_result or "Step completed without specific action."

    max_steps: int = 10
    current_step: int = 0

    @abstractmethod
    async def think(self) -> bool:
        """Process current state and decide next action"""

    @abstractmethod
    async def act(self) -> str:
        """Execute decided actions"""

    async def step(self) -> str:
        """Execute a single step: think and act."""
        should_act = await self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return await self.act()


# This class will be defined in toolcall.py to avoid circular imports
# class ReactAgent will inherit from ToolCallAgent there
