"""
Browser Access Agent для GopiAI

Агент, расширяющий ReasoningAgent для работы с браузером.
Интегрирует возможности управления браузером с системой рассуждений и разрешений.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import Field

from app.agent.reasoning import ReasoningAgent
from app.agent.browser_access import BrowserAccess
from app.logger import logger
from app.schema import AgentState, Message
from app.tool.browser_tools_integration import get_browser_tools
from app.prompt.browser import BROWSER_AGENT_SYSTEM_PROMPT


class BrowserAccessAgent(ReasoningAgent):
    """
    Агент для интеграции возможностей работы с браузером в режиме рассуждений.

    Расширяет ReasoningAgent, добавляя:
    1. Интеграцию с browser_tools (BrowserControl, BrowserAnalyzer, BrowserScreenshot)
    2. Планирование и выполнение браузерных действий с учетом разрешений
    3. Упрощенный интерфейс для самых частых браузерных операций
    4. Возможность сохранения и анализа истории браузерных действий
    """

    name: str = "browser_access_agent"
    description: str = "Reasoning agent с расширенными возможностями для работы с браузером"

    # Дополнительные модули, которые должны быть активны
    required_tools = ReasoningAgent.required_tools + [
        "browser_use",  # Базовый инструмент для работы с браузером
        "browser_control",  # Инструмент для управления браузером
        "browser_analyzer",  # Инструмент для анализа содержимого страницы
    ]

    # Состояние браузера
    current_browser_state: Optional[Dict[str, Any]] = None
    browser_history: List[Dict[str, Any]] = []

    async def initialize(self, **kwargs) -> None:
        """
        Инициализирует агент и его компоненты для работы с браузером.

        Args:
            **kwargs: Параметры для инициализации базового ReasoningAgent
        """
        # Инициализируем базовый класс ReasoningAgent
        await super().initialize(**kwargs)

        # Проверяем доступность инструментов браузера
        missing_browser_tools = self._check_browser_tools()
        if missing_browser_tools:
            missing_names = ', '.join(missing_browser_tools)
            error_msg = f"Missing required browser tools: {missing_names}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Обновляем системный промпт с учетом возможностей браузера
        browser_prompt = BROWSER_AGENT_SYSTEM_PROMPT
        self.memory.add_message(
            Message.system_message(
                f"This agent has browser capabilities. {browser_prompt}"
            )
        )

        # Инициализируем историю браузера
        self.browser_history = []

        logger.info("BrowserAccessAgent initialized successfully")

    def _check_browser_tools(self) -> List[str]:
        """
        Проверяет наличие инструментов для работы с браузером.

        Returns:
            Список отсутствующих инструментов
        """
        available_tools = set(self.mcp_clients.tool_map.keys())
        required_browser_tools = [
            "browser_use", "browser_control", "browser_analyzer"
        ]

        missing_tools = []
        for tool_name in required_browser_tools:
            if not any(t.startswith(tool_name) for t in available_tools):
                missing_tools.append(tool_name)

        return missing_tools

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """
        Переходит на указанный URL.

        Args:
            url: URL для перехода

        Returns:
            Результат выполнения действия
        """
        # Проверяем разрешение через permission_manager
        if self.permission_manager:
            request = self.permission_manager.request_permission(
                tool_name="browser_use",
                args={"action": "go_to_url", "url": url},
                reason=f"Navigating to URL: {url}"
            )

            if not request.approved:
                return {
                    "success": False,
                    "error": "Permission denied for navigating to URL",
                    "url": url
                }

        # Если есть разрешение, используем browser_access для выполнения
        if self.browser_access:
            result = await self.browser_access.execute_action(
                action="go_to_url",
                url=url
            )

            # Добавляем в историю
            self._add_to_browser_history("navigate", {"url": url}, result)

            return result
        else:
            return {
                "success": False,
                "error": "Browser access module not initialized",
                "url": url
            }

    async def click_element(self, selector: str, index: int = 0) -> Dict[str, Any]:
        """
        Кликает по элементу на странице.

        Args:
            selector: CSS-селектор элемента
            index: Индекс элемента, если найдено несколько

        Returns:
            Результат выполнения действия
        """
        # Проверяем разрешение
        if self.permission_manager:
            request = self.permission_manager.request_permission(
                tool_name="browser_use",
                args={"action": "click", "selector": selector, "index": index},
                reason=f"Clicking element with selector: {selector}"
            )

            if not request.approved:
                return {
                    "success": False,
                    "error": "Permission denied for clicking element",
                    "selector": selector
                }

        # Выполняем действие
        if self.browser_access:
            result = await self.browser_access.execute_action(
                action="click",
                selector=selector,
                index=index
            )

            # Добавляем в историю
            self._add_to_browser_history("click", {"selector": selector, "index": index}, result)

            return result
        else:
            return {
                "success": False,
                "error": "Browser access module not initialized",
                "selector": selector
            }

    async def input_text(self, selector: str, text: str, index: int = 0) -> Dict[str, Any]:
        """
        Вводит текст в поле ввода.

        Args:
            selector: CSS-селектор поля ввода
            text: Текст для ввода
            index: Индекс элемента, если найдено несколько

        Returns:
            Результат выполнения действия
        """
        # Проверяем разрешение
        if self.permission_manager:
            request = self.permission_manager.request_permission(
                tool_name="browser_use",
                args={"action": "input_text", "selector": selector, "text": text},
                reason=f"Inputting text into element with selector: {selector}"
            )

            if not request.approved:
                return {
                    "success": False,
                    "error": "Permission denied for text input",
                    "selector": selector
                }

        # Выполняем действие
        if self.browser_access:
            result = await self.browser_access.execute_action(
                action="input_text",
                selector=selector,
                text=text,
                index=index
            )

            # Добавляем в историю (маскируем потенциально конфиденциальный текст)
            safe_text = text[:10] + "..." if len(text) > 10 else text
            self._add_to_browser_history(
                "input_text",
                {"selector": selector, "text": safe_text, "index": index},
                result
            )

            return result
        else:
            return {
                "success": False,
                "error": "Browser access module not initialized",
                "selector": selector
            }

    async def extract_content(self, selector: str = "body", index: int = 0) -> Dict[str, Any]:
        """
        Извлекает текстовое содержимое элемента.

        Args:
            selector: CSS-селектор элемента
            index: Индекс элемента, если найдено несколько

        Returns:
            Результат выполнения действия с извлеченным текстом
        """
        # Для чтения можно не требовать явного разрешения, так как это безопасная операция

        # Выполняем действие
        if self.browser_access:
            result = await self.browser_access.execute_action(
                action="extract_text",
                selector=selector,
                index=index
            )

            # Добавляем в историю
            self._add_to_browser_history("extract_content", {"selector": selector, "index": index}, result)

            return result
        else:
            return {
                "success": False,
                "error": "Browser access module not initialized",
                "selector": selector
            }

    async def get_page_structure(self) -> Dict[str, Any]:
        """
        Получает структуру страницы в виде дерева элементов.

        Returns:
            Результат анализа структуры страницы
        """
        # Для чтения можно не требовать явного разрешения

        # Выполняем действие через browser_analyzer
        try:
            # Получаем инструмент browser_analyzer через MCP
            if self.mcp_clients and "browser_analyzer" in self.mcp_clients.tool_map:
                result = await self.mcp_clients.call_tool(
                    "browser_analyzer",
                    {"action": "analyze_page_structure"}
                )

                # Добавляем в историю
                self._add_to_browser_history("get_page_structure", {}, result)

                return result
            else:
                return {
                    "success": False,
                    "error": "browser_analyzer tool is not available",
                }
        except Exception as e:
            logger.error(f"Error getting page structure: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting page structure: {str(e)}",
            }

    async def take_screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """
        Делает скриншот текущей страницы.

        Args:
            full_page: Делать ли скриншот всей страницы или только видимой части

        Returns:
            Результат со ссылкой на сохраненный скриншот
        """
        # Проверяем разрешение
        if self.permission_manager:
            request = self.permission_manager.request_permission(
                tool_name="browser_screenshot",
                args={"full_page": full_page},
                reason="Taking a screenshot of the current page"
            )

            if not request.approved:
                return {
                    "success": False,
                    "error": "Permission denied for taking screenshot",
                }

        # Выполняем действие через browser_screenshot
        try:
            # Получаем инструмент browser_screenshot через MCP
            if self.mcp_clients and "browser_screenshot" in self.mcp_clients.tool_map:
                result = await self.mcp_clients.call_tool(
                    "browser_screenshot",
                    {"full_page": full_page}
                )

                # Добавляем в историю
                self._add_to_browser_history("take_screenshot", {"full_page": full_page}, result)

                return result
            else:
                return {
                    "success": False,
                    "error": "browser_screenshot tool is not available",
                }
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return {
                "success": False,
                "error": f"Error taking screenshot: {str(e)}",
            }

    async def update_browser_state(self) -> None:
        """
        Обновляет текущее состояние браузера.
        """
        if not self.browser_access:
            return

        try:
            # Получаем текущее состояние браузера
            state = await self.browser_access.get_current_state()
            if state.get("success", False):
                self.current_browser_state = state.get("state", {})
        except Exception as e:
            logger.error(f"Error updating browser state: {str(e)}")

    def _add_to_browser_history(self, action_type: str, params: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Добавляет запись в историю браузерных действий.

        Args:
            action_type: Тип действия
            params: Параметры действия
            result: Результат выполнения
        """
        import time

        history_record = {
            "timestamp": time.time(),
            "action": action_type,
            "params": params,
            "success": result.get("success", False),
            "error": result.get("error", None),
        }

        self.browser_history.append(history_record)

        # Ограничиваем размер истории
        if len(self.browser_history) > 100:
            self.browser_history = self.browser_history[-100:]

    def get_browser_history(self) -> List[Dict[str, Any]]:
        """
        Возвращает историю браузерных действий.

        Returns:
            Список словарей с информацией о выполненных действиях
        """
        return self.browser_history

    async def prepare_browser_plan(self, task: str) -> str:
        """
        Создает план выполнения задачи с использованием браузера.

        Args:
            task: Описание задачи для выполнения в браузере

        Returns:
            Строка с планом выполнения задачи
        """
        # Обновляем состояние браузера перед созданием плана
        await self.update_browser_state()

        # Дополняем задачу информацией о текущем состоянии браузера
        browser_context = ""
        if self.current_browser_state:
            browser_context = f"\n\nТекущее состояние браузера:\n{json.dumps(self.current_browser_state, indent=2, ensure_ascii=False)}"

        task_with_context = f"{task}{browser_context}"

        # Создаем план с учетом специфики браузера
        return await self.create_plan(task_with_context)

    async def execute_browser_plan(self, approved_plan: bool = False) -> str:
        """
        Выполняет одобренный план работы с браузером.

        Args:
            approved_plan: Флаг, указывающий, что план уже был одобрен ранее

        Returns:
            Результат выполнения плана
        """
        if not approved_plan and not self.current_plan:
            return "Нет одобренного плана для выполнения. Создайте и утвердите план."

        if not approved_plan:
            # Устанавливаем одобрение плана
            self.approve_plan()

        # Обновляем состояние браузера перед выполнением
        await self.update_browser_state()

        # Выполняем план
        return await self.run("execute plan")

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы агента.
        """
        # Вызываем метод родительского класса
        await super().cleanup()

        # Дополнительная очистка специфичных для браузера ресурсов
        # (Большая часть очистки браузера происходит в ReasoningAgent.cleanup())

        logger.info("BrowserAccessAgent cleanup completed")
