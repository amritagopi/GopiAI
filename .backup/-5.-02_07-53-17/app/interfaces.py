"""
Абстрактные интерфейсы для ключевых компонентов системы GopiAI.

Этот модуль содержит определения интерфейсов для основных компонентов системы,
таких как агенты, инструменты, потоки выполнения и т.д. Интерфейсы определяют
контракты взаимодействия между компонентами и обеспечивают стандартизацию API.
"""

import abc
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable, Awaitable

from pydantic import BaseModel


# Типы для типизации
T = TypeVar('T')
U = TypeVar('U')
R = TypeVar('R')

# =====================================================================
# Интерфейсы для работы с LLM
# =====================================================================

class IMessage(BaseModel, abc.ABC):
    """Интерфейс для сообщений, отправляемых в LLM."""

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сообщение в словарь для отправки в LLM API.

        Returns:
            Dict[str, Any]: Словарь с данными сообщения
        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IMessage':
        """Создает сообщение из словаря.

        Args:
            data: Словарь с данными сообщения

        Returns:
            IMessage: Экземпляр сообщения
        """
        pass

    @classmethod
    @abc.abstractmethod
    def system_message(cls, content: str) -> 'IMessage':
        """Создает системное сообщение.

        Args:
            content: Текст сообщения

        Returns:
            IMessage: Системное сообщение
        """
        pass

    @classmethod
    @abc.abstractmethod
    def user_message(cls, content: str) -> 'IMessage':
        """Создает пользовательское сообщение.

        Args:
            content: Текст сообщения

        Returns:
            IMessage: Пользовательское сообщение
        """
        pass

    @classmethod
    @abc.abstractmethod
    def assistant_message(cls, content: str) -> 'IMessage':
        """Создает сообщение ассистента.

        Args:
            content: Текст сообщения

        Returns:
            IMessage: Сообщение ассистента
        """
        pass


class ILLM(abc.ABC):
    """Интерфейс для взаимодействия с языковыми моделями."""

    @abc.abstractmethod
    async def ask(
        self,
        messages: List[Union[Dict[str, Any], IMessage]],
        system_msgs: Optional[List[Union[Dict[str, Any], IMessage]]] = None,
        stream: bool = True,
        temperature: Optional[float] = None
    ) -> str:
        """Отправляет запрос LLM-модели и получает ответ.

        Args:
            messages: Список сообщений для отправки
            system_msgs: Опциональные системные сообщения
            stream: Флаг использования потоковой передачи ответа
            temperature: Температура для генерации ответа

        Returns:
            str: Ответ модели
        """
        pass

    @abc.abstractmethod
    async def ask_with_tools(
        self,
        messages: List[Union[Dict[str, Any], IMessage]],
        tools: List[Dict[str, Any]],
        system_msgs: Optional[List[Union[Dict[str, Any], IMessage]]] = None,
        timeout: int = 300,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Отправляет запрос LLM-модели с инструментами и получает ответ.

        Args:
            messages: Список сообщений для отправки
            tools: Список инструментов для использования
            system_msgs: Опциональные системные сообщения
            timeout: Таймаут для запроса
            temperature: Температура для генерации ответа

        Returns:
            Dict[str, Any]: Ответ модели с вызовами инструментов
        """
        pass

    @abc.abstractmethod
    def format_messages(
        self, messages: List[Union[Dict[str, Any], IMessage]], supports_images: bool = False
    ) -> List[Dict[str, Any]]:
        """Форматирует сообщения для отправки в LLM API.

        Args:
            messages: Список сообщений
            supports_images: Флаг поддержки изображений

        Returns:
            List[Dict[str, Any]]: Форматированный список сообщений
        """
        pass

    @abc.abstractmethod
    def count_tokens(self, text: str) -> int:
        """Подсчитывает количество токенов в тексте.

        Args:
            text: Текст для подсчета токенов

        Returns:
            int: Количество токенов
        """
        pass

    @abc.abstractmethod
    def count_message_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Подсчитывает количество токенов в сообщениях.

        Args:
            messages: Список сообщений

        Returns:
            int: Общее количество токенов
        """
        pass


class IPromptProvider(abc.ABC):
    """Интерфейс для провайдеров промптов."""

    @abc.abstractmethod
    def get_system_prompt(self, **kwargs) -> str:
        """Возвращает системный промпт.

        Args:
            **kwargs: Дополнительные параметры для формирования промпта

        Returns:
            str: Системный промпт
        """
        pass

    @abc.abstractmethod
    def get_user_prompt(self, **kwargs) -> str:
        """Возвращает пользовательский промпт.

        Args:
            **kwargs: Дополнительные параметры для формирования промпта

        Returns:
            str: Пользовательский промпт
        """
        pass

    @abc.abstractmethod
    def format_prompt(self, template: str, **kwargs) -> str:
        """Форматирует шаблон промпта с заданными параметрами.

        Args:
            template: Шаблон промпта
            **kwargs: Параметры для форматирования

        Returns:
            str: Отформатированный промпт
        """
        pass


# =====================================================================
# Интерфейсы для инструментов
# =====================================================================

class ToolResult(BaseModel):
    """Результат выполнения инструмента."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ITool(abc.ABC):
    """Интерфейс для инструментов."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Возвращает имя инструмента.

        Returns:
            str: Имя инструмента
        """
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Возвращает описание инструмента.

        Returns:
            str: Описание инструмента
        """
        pass

    @property
    @abc.abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Возвращает параметры инструмента.

        Returns:
            Dict[str, Any]: Описание параметров инструмента
        """
        pass

    @abc.abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Выполняет инструмент с заданными параметрами.

        Args:
            **kwargs: Параметры для выполнения инструмента

        Returns:
            ToolResult: Результат выполнения инструмента
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует инструмент в словарь для использования в LLM API.

        Returns:
            Dict[str, Any]: Словарь с описанием инструмента
        """
        pass


class IToolProvider(abc.ABC):
    """Интерфейс для провайдеров инструментов."""

    @abc.abstractmethod
    def get_tools(self) -> List[ITool]:
        """Возвращает список доступных инструментов.

        Returns:
            List[ITool]: Список инструментов
        """
        pass

    @abc.abstractmethod
    def get_tool(self, name: str) -> Optional[ITool]:
        """Возвращает инструмент по имени.

        Args:
            name: Имя инструмента

        Returns:
            Optional[ITool]: Инструмент или None, если инструмент не найден
        """
        pass


# =====================================================================
# Интерфейсы для агентов
# =====================================================================

class AgentState(Enum):
    """Состояние агента."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentConfig(BaseModel):
    """Конфигурация агента."""
    name: str
    description: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None


class IAgent(abc.ABC):
    """Интерфейс для агентов."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Возвращает имя агента.

        Returns:
            str: Имя агента
        """
        pass

    @property
    @abc.abstractmethod
    def state(self) -> AgentState:
        """Возвращает текущее состояние агента.

        Returns:
            AgentState: Состояние агента
        """
        pass

    @abc.abstractmethod
    async def process(self, input_text: str, **kwargs) -> str:
        """Обрабатывает входной текст и возвращает результат.

        Args:
            input_text: Входной текст для обработки
            **kwargs: Дополнительные параметры для обработки

        Returns:
            str: Результат обработки
        """
        pass

    @abc.abstractmethod
    async def run(self, input_text: str, **kwargs) -> str:
        """Запускает агента с заданным входным текстом.

        Args:
            input_text: Входной текст для запуска
            **kwargs: Дополнительные параметры для запуска

        Returns:
            str: Результат выполнения
        """
        pass

    @abc.abstractmethod
    async def reset(self) -> None:
        """Сбрасывает состояние агента."""
        pass

    @abc.abstractmethod
    def set_llm(self, llm: ILLM) -> None:
        """Устанавливает LLM для агента.

        Args:
            llm: Экземпляр LLM
        """
        pass

    @abc.abstractmethod
    def set_tool_provider(self, tool_provider: IToolProvider) -> None:
        """Устанавливает провайдер инструментов для агента.

        Args:
            tool_provider: Экземпляр провайдера инструментов
        """
        pass

    @abc.abstractmethod
    def set_prompt_provider(self, prompt_provider: IPromptProvider) -> None:
        """Устанавливает провайдер промптов для агента.

        Args:
            prompt_provider: Экземпляр провайдера промптов
        """
        pass


# =====================================================================
# Интерфейсы для потоков выполнения
# =====================================================================

class FlowConfig(BaseModel):
    """Конфигурация потока выполнения."""
    name: str
    description: Optional[str] = None
    agents: List[str]
    primary_agent: Optional[str] = None


class IFlow(abc.ABC):
    """Интерфейс для потоков выполнения."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Возвращает имя потока.

        Returns:
            str: Имя потока
        """
        pass

    @abc.abstractmethod
    async def execute(self, input_text: str, **kwargs) -> str:
        """Выполняет поток с заданным входным текстом.

        Args:
            input_text: Входной текст для выполнения
            **kwargs: Дополнительные параметры для выполнения

        Returns:
            str: Результат выполнения
        """
        pass

    @abc.abstractmethod
    def add_agent(self, key: str, agent: IAgent) -> None:
        """Добавляет агента в поток.

        Args:
            key: Ключ агента
            agent: Экземпляр агента
        """
        pass

    @abc.abstractmethod
    def get_agent(self, key: str) -> Optional[IAgent]:
        """Возвращает агента по ключу.

        Args:
            key: Ключ агента

        Returns:
            Optional[IAgent]: Агент или None, если агент не найден
        """
        pass

    @property
    @abc.abstractmethod
    def primary_agent(self) -> Optional[IAgent]:
        """Возвращает основного агента потока.

        Returns:
            Optional[IAgent]: Основной агент или None
        """
        pass


class IFlowFactory(abc.ABC):
    """Интерфейс для фабрики потоков выполнения."""

    @abc.abstractmethod
    def create_flow(self, config: FlowConfig) -> IFlow:
        """Создает поток с заданной конфигурацией.

        Args:
            config: Конфигурация потока

        Returns:
            IFlow: Экземпляр потока
        """
        pass

    @abc.abstractmethod
    def register_agent_factory(self, agent_type: str, factory: Callable[[AgentConfig], IAgent]) -> None:
        """Регистрирует фабрику агентов.

        Args:
            agent_type: Тип агента
            factory: Фабричная функция для создания агента
        """
        pass


# =====================================================================
# Интерфейсы для UI
# =====================================================================

class IUIComponent(abc.ABC):
    """Интерфейс для компонентов пользовательского интерфейса."""

    @abc.abstractmethod
    def update(self) -> None:
        """Обновляет компонент."""
        pass

    @abc.abstractmethod
    def show(self) -> None:
        """Отображает компонент."""
        pass

    @abc.abstractmethod
    def hide(self) -> None:
        """Скрывает компонент."""
        pass

    @abc.abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """Устанавливает активность компонента.

        Args:
            enabled: Флаг активности
        """
        pass


class IUIEventHandler(abc.ABC):
    """Интерфейс для обработчика событий UI."""

    @abc.abstractmethod
    def on_event(self, event_type: str, data: Any) -> None:
        """Обрабатывает событие UI.

        Args:
            event_type: Тип события
            data: Данные события
        """
        pass
