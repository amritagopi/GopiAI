"""
Интеграция с MCP Serena для GopiAI

Модуль обеспечивает подключение и взаимодействие с модулем Serena
"""

import json
import os
from typing import Dict, List, Optional, Any, Set

from app.logger import logger
from app.mcp.client import MCPClient
from app.mcp.serena_tools import SerenaTools


class SerenaIntegration:
    """
    Класс для интеграции с MCP Serena.

    Обеспечивает:
    - Подключение к MCP Serena
    - Проверку доступности Serena инструментов
    - Доступ к файловой системе через инструменты Serena
    - Доступ к кодовой базе через инструменты Serena
    """

    # Список инструментов Serena, которые должны быть доступны
    REQUIRED_TOOLS = [
        "mcp_serena_initial_instructions",
        "mcp_serena_check_onboarding_performed",
        "mcp_serena_read_file",
        "mcp_serena_create_text_file",
        "mcp_serena_list_dir",
        "mcp_serena_get_symbols_overview",
        "mcp_serena_find_symbol",
        "mcp_serena_find_referencing_symbols",
    ]

    def __init__(self, mcp_client: MCPClient):
        """
        Инициализирует интеграцию с Serena.

        Args:
            mcp_client: Клиент MCP для отправки запросов к модулю
        """
        self.mcp_client = mcp_client
        self.tools = SerenaTools()
        self.available_tools: Set[str] = set()
        self.initialized = False
        self.memory_files: List[str] = []

    async def initialize(self) -> bool:
        """
        Инициализирует соединение с Serena и проверяет доступность инструментов.

        Returns:
            True если инициализация успешна, False в противном случае
        """
        try:
            # Проверяем доступные инструменты
            self.available_tools = set(self.mcp_client.tool_map.keys())

            # Проверяем необходимые инструменты
            missing_tools = self._check_required_tools()
            if missing_tools:
                logger.error(f"Missing required Serena tools: {', '.join(missing_tools)}")
                return False

            # Получаем исходные инструкции Serena
            await self._get_initial_instructions()

            # Проверяем, был ли выполнен onboarding
            result = await self._check_onboarding()
            if not result:
                logger.warning("Serena onboarding not performed, some features may be limited")

            # Получаем список доступных memories
            self.memory_files = await self._list_memories()

            logger.info(f"Serena integration initialized successfully, {len(self.available_tools)} tools available")
            logger.info(f"Memory files available: {len(self.memory_files)}")

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Error initializing Serena integration: {str(e)}")
            return False

    def _check_required_tools(self) -> List[str]:
        """
        Проверяет наличие всех необходимых инструментов Serena.

        Returns:
            Список отсутствующих инструментов
        """
        missing_tools = []
        for tool_name in self.REQUIRED_TOOLS:
            if tool_name not in self.available_tools:
                missing_tools.append(tool_name)
        return missing_tools

    async def _get_initial_instructions(self) -> Dict[str, Any]:
        """
        Получает исходные инструкции от MCP Serena.

        Returns:
            Словарь с инструкциями
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_initial_instructions",
                {"random_string": "check"}
            )

            if isinstance(response, str):
                logger.info("Received Serena initial instructions")
                return {"status": "success", "instructions": response}
            else:
                return response

        except Exception as e:
            logger.error(f"Error getting Serena initial instructions: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def _check_onboarding(self) -> bool:
        """
        Проверяет, был ли выполнен onboarding Serena.

        Returns:
            True если onboarding выполнен, False в противном случае
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_check_onboarding_performed",
                {"random_string": "check"}
            )

            # Предполагаем, что результат содержит информацию об onboarding
            if isinstance(response, dict) and response.get("performed", False):
                logger.info("Serena onboarding performed")
                return True

            logger.warning("Serena onboarding not performed")
            return False

        except Exception as e:
            logger.error(f"Error checking Serena onboarding: {str(e)}")
            return False

    async def _list_memories(self) -> List[str]:
        """
        Получает список доступных memory файлов Serena.

        Returns:
            Список имен файлов
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_list_memories",
                {"random_string": "check"}
            )

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "memories" in response:
                return response["memories"]
            else:
                logger.warning(f"Unexpected response from list_memories: {response}")
                return []

        except Exception as e:
            logger.error(f"Error listing Serena memories: {str(e)}")
            return []

    async def read_file(
        self,
        relative_path: str,
        start_line: int = 0,
        end_line: Optional[int] = None,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Читает файл через Serena.

        Args:
            relative_path: Относительный путь к файлу
            start_line: Начальная строка (0-based)
            end_line: Конечная строка (включительно)
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            params = {
                "relative_path": relative_path,
                "start_line": start_line
            }

            if end_line is not None:
                params["end_line"] = end_line

            params["max_answer_chars"] = max_answer_chars

            response = await self.mcp_client.call_tool(
                "mcp_serena_read_file",
                params
            )

            return response

        except Exception as e:
            logger.error(f"Error reading file through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def create_text_file(
        self,
        relative_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Создает или перезаписывает текстовый файл через Serena.

        Args:
            relative_path: Относительный путь к файлу
            content: Содержимое файла

        Returns:
            Результат операции
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_create_text_file",
                {
                    "relative_path": relative_path,
                    "content": content
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error creating text file through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def list_dir(
        self,
        relative_path: str,
        recursive: bool = False,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Перечисляет содержимое директории через Serena.

        Args:
            relative_path: Относительный путь к директории
            recursive: Флаг рекурсивного обхода
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_list_dir",
                {
                    "relative_path": relative_path,
                    "recursive": recursive,
                    "max_answer_chars": max_answer_chars
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error listing directory through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_symbols_overview(
        self,
        relative_path: str,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Получает обзор символов в файле или директории через Serena.

        Args:
            relative_path: Относительный путь к файлу или директории
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_get_symbols_overview",
                {
                    "relative_path": relative_path,
                    "max_answer_chars": max_answer_chars
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error getting symbols overview through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def find_symbol(
        self,
        name: str,
        depth: int = 0,
        include_body: bool = False,
        substring_matching: bool = False,
        within_relative_path: Optional[str] = None,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Ищет символы (классы, методы, функции и т.д.) через Serena.

        Args:
            name: Имя символа для поиска
            depth: Глубина поиска вложенных символов
            include_body: Включать ли тело символа
            substring_matching: Искать ли по подстроке
            within_relative_path: Ограничить поиск указанным путем
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            params = {
                "name": name,
                "depth": depth,
                "include_body": include_body,
                "substring_matching": substring_matching,
                "max_answer_chars": max_answer_chars
            }

            if within_relative_path is not None:
                params["within_relative_path"] = within_relative_path

            response = await self.mcp_client.call_tool(
                "mcp_serena_find_symbol",
                params
            )

            return response

        except Exception as e:
            logger.error(f"Error finding symbol through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def find_referencing_symbols(
        self,
        relative_path: str,
        line: int,
        column: int,
        include_body: bool = False,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Ищет символы, ссылающиеся на указанный символ.

        Args:
            relative_path: Относительный путь к файлу
            line: Номер строки символа
            column: Номер колонки символа
            include_body: Включать ли тело символа
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_find_referencing_symbols",
                {
                    "relative_path": relative_path,
                    "line": line,
                    "column": column,
                    "include_body": include_body,
                    "max_answer_chars": max_answer_chars
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error finding referencing symbols through Serena: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def read_memory(
        self,
        memory_file_name: str,
        max_answer_chars: int = 200000
    ) -> str:
        """
        Читает содержимое memory файла Serena.

        Args:
            memory_file_name: Имя memory файла
            max_answer_chars: Максимальное количество символов

        Returns:
            Содержимое memory файла
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_read_memory",
                {
                    "memory_file_name": memory_file_name,
                    "max_answer_chars": max_answer_chars
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error reading Serena memory file: {str(e)}")
            return f"Error: {str(e)}"

    async def write_memory(
        self,
        memory_file_name: str,
        content: str,
        max_answer_chars: int = 200000
    ) -> Dict[str, Any]:
        """
        Записывает содержимое в memory файл Serena.

        Args:
            memory_file_name: Имя memory файла
            content: Содержимое файла
            max_answer_chars: Максимальное количество символов

        Returns:
            Результат операции
        """
        try:
            response = await self.mcp_client.call_tool(
                "mcp_serena_write_memory",
                {
                    "memory_file_name": memory_file_name,
                    "content": content,
                    "max_answer_chars": max_answer_chars
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error writing Serena memory file: {str(e)}")
            return {"status": "error", "error": str(e)}

    def is_available(self) -> bool:
        """
        Проверяет, доступна ли Serena.

        Returns:
            True если Serena доступна, False в противном случае
        """
        return self.initialized and len(self._check_required_tools()) == 0
