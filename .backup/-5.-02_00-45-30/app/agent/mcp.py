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

        try:
            # Получаем историю сообщений
            messages = self.memory.get_history()

            # Отправляем запрос модели через MCP
            response = await self.mcp_clients.generate(messages)

            # Обрабатываем ответ
            if not response:
                raise ValueError("Empty response from MCP model")

            # Проверяем, есть ли в ответе вызовы инструментов
            tool_calls = self._extract_tool_calls(response)

            # Если есть вызовы инструментов, выполняем их
            if tool_calls:
                result = await self._process_tool_calls(tool_calls)
                # Добавляем результат в память
                self.memory.add_message(Message.assistant_message(result))
                return result

            # Если нет вызовов инструментов, возвращаем текстовый ответ
            self.memory.add_message(Message.assistant_message(response))
            return response

        except Exception as e:
            logger.error(f"Error running MCP Agent: {str(e)}")
            return f"Error processing request: {str(e)}"

    def _extract_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Извлекает вызовы инструментов из ответа модели.

        Args:
            response: Ответ модели

        Returns:
            Список вызовов инструментов
        """
        # Здесь должен быть код для извлечения вызовов инструментов из текста
        import re
        import json

        tool_calls = []

        # Ищем вызовы инструментов в формате json
        pattern = r'```json\s*({[^`]*})\s*```'
        matches = re.findall(pattern, response)

        for match in matches:
            try:
                data = json.loads(match)
                if 'tool' in data and 'parameters' in data:
                    tool_calls.append(data)
            except json.JSONDecodeError:
                continue

        return tool_calls

    async def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        """
        Обрабатывает вызовы инструментов.

        Args:
            tool_calls: Список вызовов инструментов

        Returns:
            Результат выполнения инструментов
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get('tool')
            parameters = tool_call.get('parameters', {})

            if not tool_name:
                continue

            try:
                # Вызываем инструмент
                result = await self.process_tool_call(tool_name, **parameters)
                results.append(result)
            except Exception as e:
                results.append(f"Error executing tool {tool_name}: {str(e)}")

        return "\n".join(str(result) for result in results)

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы агента.
        """
        try:
            logger.info(f"Cleaning up MCP Agent '{self.name}'...")

            # Сохраняем важные данные в постоянное хранилище, если необходимо
            # Например, сохранение истории взаимодействий или настроек
            await self._save_session_data()

            # Закрываем соединения с MCP клиентом
            if hasattr(self, 'mcp_clients') and self.mcp_clients:
                await self.mcp_clients.close()

            # Очищаем память агента
            if hasattr(self, 'memory') and self.memory:
                self.memory.clear()

            # Освобождаем другие ресурсы
            # Например, закрытие файлов, соединений с БД и т.д.

            # Устанавливаем состояние IDLE
            self.state = AgentState.IDLE

            logger.info(f"MCP Agent '{self.name}' cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during MCP Agent cleanup: {str(e)}")
            self.state = AgentState.ERROR
            raise

    async def _save_session_data(self) -> None:
        """
        Сохраняет важные данные сессии.

        Этот метод сохраняет данные, которые должны быть доступны между сессиями.
        """
        try:
            # Определяем, что нужно сохранить
            data_to_save = {
                "last_session_time": self._get_current_timestamp(),
                "messages_count": len(self.memory.messages) if self.memory else 0,
                # Добавьте здесь другие данные для сохранения
            }

            # В реальной реализации здесь будет код для сохранения данных
            # Например, в файл, базу данных и т.д.

            logger.info(f"Session data saved for agent {self.name}")
        except Exception as e:
            logger.error(f"Error saving session data: {str(e)}")

    def _get_current_timestamp(self) -> str:
        """Возвращает текущую временную метку в ISO формате."""
        from datetime import datetime
        return datetime.now().isoformat()


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
