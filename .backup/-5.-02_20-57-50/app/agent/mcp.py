"""
MCP Agent для GopiAI

Базовый класс агента, использующего MCP (Model Control Protocol).
"""

import asyncio
from typing import Dict, List, Any, Optional, Set

from app.logger import logger
from app.mcp.client import MCPClient
from app.schema import Message, AgentState


class MCPAgent:
    """
    Базовый класс агента, работающего через MCP.

    Предоставляет базовую функциональность для инициализации MCP клиента,
    вызова инструментов и обработки сообщений.
    """

    name: str = "mcp_agent"
    description: str = "A base agent using MCP (Model Control Protocol)"

    # Системный промпт по умолчанию
    system_prompt: str = "You are a helpful AI assistant powered by MCP."

    def __init__(self):
        """
        Инициализирует агента с настройками по умолчанию.
        """
        self.mcp_clients = MCPClient()
        self.memory = AgentMemory()
        self.state = AgentState.IDLE

    async def initialize(
        self,
        connection_type: Optional[str] = None,
        server_url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
    ) -> None:
        """
        Инициализирует агента и устанавливает соединение с MCP сервером.

        Args:
            connection_type: Тип подключения ("stdio" или "sse")
            server_url: URL MCP сервера (для SSE подключения)
            command: Команда для запуска (для stdio подключения)
            args: Аргументы для команды (для stdio подключения)
        """
        try:
            # Инициализируем клиент MCP
            client_initialized = await self.mcp_clients.initialize()
            if not client_initialized:
                raise ValueError("Failed to initialize MCP client")

            # Инициализируем память с системным промптом
            self.memory.add_message(Message.system_message(self.system_prompt))

            # Устанавливаем состояние агента
            self.state = AgentState.READY

            logger.info(f"MCP Agent '{self.name}' initialized successfully")

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Error initializing MCP Agent: {str(e)}")
            raise

    async def process_tool_call(self, name: str, **kwargs) -> Any:
        """
        Обрабатывает вызов инструмента.

        Args:
            name: Имя инструмента
            **kwargs: Аргументы для инструмента

        Returns:
            Результат выполнения инструмента
        """
        try:
            # Вызываем инструмент через MCP клиент
            result = await self.mcp_clients.call_tool(name, kwargs)
            return result

        except Exception as e:
            logger.error(f"Error processing tool call {name}: {str(e)}")
            return {"error": str(e)}

    async def run(self, request: Optional[str] = None) -> str:
        """
        Запускает агента для обработки запроса.

        Args:
            request: Запрос пользователя

        Returns:
            Результат обработки запроса
        """
        # Проверяем состояние агента
        if self.state == AgentState.ERROR:
            return "Agent is in error state. Please initialize again."

        if self.state != AgentState.READY:
            return "Agent is not ready. Please initialize first."

        # Если есть запрос, добавляем его в память
        if request:
            self.memory.add_message(Message.user_message(request))

        # Здесь должен быть код обработки запроса через MCP
        # В данной заглушке просто возвращаем эхо запроса
        return f"Echo: {request}"

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы агента.
        """
        # Здесь должен быть код освобождения ресурсов
        logger.info(f"MCP Agent '{self.name}' cleanup completed")


class AgentMemory:
    """
    Класс для хранения истории сообщений агента.
    """

    def __init__(self):
        """
        Инициализирует память агента.
        """
        self.messages: List[Message] = []

    def add_message(self, message: Message) -> None:
        """
        Добавляет сообщение в историю.

        Args:
            message: Сообщение для добавления
        """
        self.messages.append(message)

    def get_history(self) -> List[Message]:
        """
        Возвращает историю сообщений.

        Returns:
            Список сообщений
        """
        return self.messages

    def clear(self) -> None:
        """
        Очищает историю сообщений.
        """
        self.messages.clear()
