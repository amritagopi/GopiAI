from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.interfaces import IAgent, AgentState as InterfaceAgentState, IToolProvider, IPromptProvider, ILLM
from app.llm import LLM
from app.logger import logger
from app.sandbox.client import SANDBOX_CLIENT
from app.schema import ROLE_TYPE, AgentState, Memory, Message


class BaseAgent(BaseModel, IAgent):
    """Abstract base class for managing agent state and execution.

    Provides foundational functionality for state transitions, memory management,
    and a step-based execution loop. Subclasses must implement the `step` method.

    Implements the IAgent interface to ensure standardized component interactions.
    """

    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Optional agent description")

    # Prompts
    system_prompt: Optional[str] = Field(
        None, description="System-level instruction prompt"
    )
    next_step_prompt: Optional[str] = Field(
        None, description="Prompt for determining next action"
    )

    # Dependencies
    llm: LLM = Field(default_factory=LLM, description="Language model instance")
    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")
    state: AgentState = Field(
        default=AgentState.IDLE, description="Current agent state"
    )

    # Providers
    tool_provider: Optional[IToolProvider] = Field(
        None, description="Provider for agent tools"
    )
    prompt_provider: Optional[IPromptProvider] = Field(
        None, description="Provider for agent prompts"
    )

    # Execution control
    max_steps: int = Field(default=10, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")

    duplicate_threshold: int = 2

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"  # Allow extra fields for flexibility in subclasses
    )

    # Методы из интерфейса IAgent
    @property
    def name(self) -> str:
        """Возвращает имя агента.

        Реализует метод из интерфейса IAgent.

        Returns:
            str: Имя агента
        """
        return self.name

    @property
    def state(self) -> InterfaceAgentState:
        """Возвращает текущее состояние агента.

        Реализует метод из интерфейса IAgent.
        Преобразует внутреннее состояние AgentState в состояние из интерфейса.

        Returns:
            InterfaceAgentState: Состояние агента
        """
        # Маппинг из внутреннего состояния в состояние из интерфейса
        state_mapping = {
            AgentState.IDLE: InterfaceAgentState.INITIALIZED,
            AgentState.RUNNING: InterfaceAgentState.RUNNING,
            AgentState.WAITING: InterfaceAgentState.WAITING,
            AgentState.FINISHED: InterfaceAgentState.COMPLETED,
            AgentState.ERROR: InterfaceAgentState.FAILED
        }
        return state_mapping.get(self.state, InterfaceAgentState.INITIALIZED)

    async def process(self, input_text: str, **kwargs) -> str:
        """Обрабатывает входной текст и возвращает результат.

        Реализует метод из интерфейса IAgent.

        Args:
            input_text: Входной текст для обработки
            **kwargs: Дополнительные параметры для обработки

        Returns:
            str: Результат обработки
        """
        if input_text:
            self.update_memory("user", input_text)

        # Выполнить один шаг обработки
        return await self.step()

    async def run(self, input_text: Optional[str] = None, **kwargs) -> str:
        """Execute the agent's main loop asynchronously.

        Implements the run method from IAgent interface.

        Args:
            input_text: Optional initial user request to process.
            **kwargs: Additional keyword arguments.

        Returns:
            A string summarizing the execution results.

        Raises:
            RuntimeError: If the agent is not in IDLE state at start.
        """
        if self.state != AgentState.IDLE:
            raise RuntimeError(f"Cannot run agent from state: {self.state}")

        if input_text:
            self.update_memory("user", input_text)

        results: List[str] = []
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                self.current_step += 1
                logger.info(f"Executing step {self.current_step}/{self.max_steps}")
                step_result = await self.step()

                # Check for stuck state
                if self.is_stuck():
                    self.handle_stuck_state()

                results.append(f"Step {self.current_step}: {step_result}")

            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"Terminated: Reached max steps ({self.max_steps})")
        await SANDBOX_CLIENT.cleanup()
        return "\n".join(results) if results else "No steps executed"

    async def reset(self) -> None:
        """Сбрасывает состояние агента.

        Реализует метод из интерфейса IAgent.
        """
        self.current_step = 0
        self.state = AgentState.IDLE
        self.memory = Memory()

    def set_llm(self, llm: ILLM) -> None:
        """Устанавливает LLM для агента.

        Реализует метод из интерфейса IAgent.

        Args:
            llm: Экземпляр LLM
        """
        # При необходимости можно добавить адаптер между ILLM и текущей LLM
        # На текущий момент просто предполагаем, что LLM также реализует ILLM
        if isinstance(llm, LLM):
            self.llm = llm
        else:
            logger.warning(f"LLM type {type(llm)} is not directly supported, may require adapter")
            self.llm = llm  # В будущем здесь может быть адаптер

    def set_tool_provider(self, tool_provider: IToolProvider) -> None:
        """Устанавливает провайдер инструментов для агента.

        Реализует метод из интерфейса IAgent.

        Args:
            tool_provider: Экземпляр провайдера инструментов
        """
        self.tool_provider = tool_provider

    def set_prompt_provider(self, prompt_provider: IPromptProvider) -> None:
        """Устанавливает провайдер промптов для агента.

        Реализует метод из интерфейса IAgent.

        Args:
            prompt_provider: Экземпляр провайдера промптов
        """
        self.prompt_provider = prompt_provider

    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """Initialize agent with default settings if not provided."""
        if self.llm is None or not isinstance(self.llm, LLM):
            self.llm = LLM(config_name=self.name.lower())
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        return self

    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """Context manager for safe agent state transitions.

        Args:
            new_state: The state to transition to during the context.

        Yields:
            None: Allows execution within the new state.

        Raises:
            ValueError: If the new_state is invalid.
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid state: {new_state}")

        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR  # Transition to ERROR on failure
            raise e
        finally:
            self.state = previous_state  # Revert to previous state

    def update_memory(
        self,
        role: ROLE_TYPE,  # type: ignore
        content: str,
        base64_image: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Add a message to the agent's memory.

        Args:
            role: The role of the message sender (user, system, assistant, tool).
            content: The message content.
            base64_image: Optional base64 encoded image.
            **kwargs: Additional arguments (e.g., tool_call_id for tool messages).

        Raises:
            ValueError: If the role is unsupported.
        """
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "tool": lambda content, **kw: Message.tool_message(content, **kw),
        }

        if role not in message_map:
            raise ValueError(f"Unsupported message role: {role}")

        # Create message with appropriate parameters based on role
        kwargs = {"base64_image": base64_image, **(kwargs if role == "tool" else {})}
        self.memory.add_message(message_map[role](content, **kwargs))

    @abstractmethod
    async def step(self) -> str:
        """Execute a single step in the agent's workflow.

        Must be implemented by subclasses to define specific behavior.
        """

    def handle_stuck_state(self):
        """Handle stuck state by adding a prompt to change strategy"""
        stuck_prompt = "\
        Observed duplicate responses. Consider new strategies and avoid repeating ineffective paths already attempted."
        self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
        logger.warning(f"Agent detected stuck state. Added prompt: {stuck_prompt}")

    def is_stuck(self) -> bool:
        """Check if the agent is stuck in a loop by detecting duplicate content"""
        if len(self.memory.messages) < 2:
            return False

        last_message = self.memory.messages[-1]
        if not last_message.content:
            return False

        # Count identical content occurrences
        duplicate_count = sum(
            1
            for msg in reversed(self.memory.messages[:-1])
            if msg.role == "assistant" and msg.content == last_message.content
        )

        return duplicate_count >= self.duplicate_threshold

    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of messages from the agent's memory."""
        return self.memory.messages

    @messages.setter
    def messages(self, value: List[Message]):
        """Set the list of messages in the agent's memory."""
        self.memory.messages = value

    async def think(self) -> bool:
        """
        Process the current state and decide the next action.

        This method should be implemented by subclasses to determine the next action
        based on the agent's memory, goals, and other state components.

        Returns:
            bool: True if thinking was successful, False otherwise.
        """
        # Оповещаем о начале обдумывания
        if hasattr(self, 'on_thinking_start') and callable(self.on_thinking_start):
            self.on_thinking_start()

        # Логика размышления (может быть переопределена в наследниках)
        result = True

        # Оповещаем о завершении обдумывания
        if hasattr(self, 'on_thinking_end') and callable(self.on_thinking_end):
            self.on_thinking_end()

        return result

    async def _execute_tool(self, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool with the given input.

        Uses tools from the tool provider if available, otherwise falls back to the
        instance's available_tools attribute.
        """
        tool_name = tool_input.get("name")

        # Сначала пробуем использовать инструменты из провайдера
        if self.tool_provider:
            tool = self.tool_provider.get_tool(tool_name)
            if tool:
                # Оповещаем о начале использования инструмента
                if hasattr(self, 'on_tool_start') and callable(self.on_tool_start):
                    self.on_tool_start(tool_name)

                # Выполняем инструмент через интерфейс IToolProvider
                result = await tool.execute(**tool_input.get("arguments", {}))

                # Оповещаем о завершении использования инструмента
                if hasattr(self, 'on_tool_end') and callable(self.on_tool_end):
                    self.on_tool_end(tool_name)

                return result

        # Фолбэк на традиционное использование инструментов
        if hasattr(self, 'available_tools'):
            for tool in self.available_tools.tools:
                if tool.name == tool_name:
                    # Оповещаем о начале использования инструмента
                    if hasattr(self, 'on_tool_start') and callable(self.on_tool_start):
                        self.on_tool_start(tool_name)

                    # Выполняем инструмент
                    result = await tool(tool_input)

                    # Оповещаем о завершении использования инструмента
                    if hasattr(self, 'on_tool_end') and callable(self.on_tool_end):
                        self.on_tool_end(tool_name)

                    return result

        raise ValueError(f"Tool '{tool_name}' not found")
