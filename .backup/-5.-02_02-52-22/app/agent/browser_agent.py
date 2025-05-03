import json
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.logger import logger
from app.prompt.browser import BROWSER_AGENT_SYSTEM_PROMPT, BROWSER_AGENT_NEXT_STEP_PROMPT
from app.schema import Message, ToolChoice
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection
from app.tool.browser_tools_integration import get_browser_tools


class EnhancedBrowserAgent(ToolCallAgent):
    """
    Улучшенный браузерный агент с возможностью управления и анализа браузера.

    Агент может выполнять различные задачи с использованием браузера, включая
    навигацию, выполнение JavaScript, извлечение данных и анализ структуры страниц.
    """

    name: str = "browser_agent"
    description: str = "Агент для работы с браузером, который может управлять браузером и анализировать веб-страницы"

    # Подсказки для системы и следующего шага
    system_prompt: str = BROWSER_AGENT_SYSTEM_PROMPT
    next_step_prompt: str = BROWSER_AGENT_NEXT_STEP_PROMPT

    # Ограничения
    max_observe: int = 15000
    max_steps: int = 30

    # Доступные инструменты (добавляем только базовые в конструкторе)
    tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(Terminate())
    )

    # Выбор инструментов (AUTO позволяет как использовать инструменты, так и давать ответы)
    tool_choices: ToolChoice = ToolChoice.AUTO

    # Специальные инструменты
    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    # Сохраненное состояние браузера
    _current_browser_state: Optional[Dict] = None

    def __init__(self, **data):
        super().__init__(**data)

        # Добавляем инструменты браузера
        browser_tools = get_browser_tools()
        for tool in browser_tools:
            self.tools.add_tool(tool)

        logger.info(f"Инициализирован {self.name} с {len(self.tools.tools)} инструментами")

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        """Обработка вызова специальных инструментов."""
        if not self._is_special_tool(name):
            return
        else:
            await super()._handle_special_tool(name, result, **kwargs)

    async def get_browser_state(self) -> Optional[Dict]:
        """
        Получает текущее состояние браузера для контекста следующих шагов.

        Использует инструменты браузера для получения информации о текущей странице,
        открытых вкладках и других данных.

        Returns:
            Dict с состоянием браузера или None, если информация недоступна
        """
        # В этой версии пока не реализован полный сбор состояния браузера
        # В будущем можно добавить вызов инструмента browser_control с action="get_tabs_info"
        # и других методов для сбора полной информации о состоянии браузера
        return self._current_browser_state

    async def update_browser_state(self):
        """
        Обновляет сохраненное состояние браузера.

        Получает информацию о текущей странице и вкладках с помощью инструментов браузера.
        """
        try:
            # Пытаемся получить информацию о вкладках
            browser_control = self.tools.get_tool("browser_control")
            if browser_control:
                tabs_result = await browser_control.execute(action="get_tabs_info")

                if not tabs_result.error:
                    tabs_info = tabs_result.output
                else:
                    tabs_info = "Не удалось получить информацию о вкладках"

                # Пытаемся получить URL текущей страницы
                current_url_result = await browser_control.execute(action="get_current_url")
                if not current_url_result.error:
                    current_url = current_url_result.output
                else:
                    current_url = "Не удалось получить текущий URL"

                # Сохраняем состояние
                self._current_browser_state = {
                    "tabs": tabs_info,
                    "current_url": current_url
                }

                return self._current_browser_state
        except Exception as e:
            logger.error(f"Ошибка при обновлении состояния браузера: {e}")

        return None

    async def think(self) -> bool:
        """
        Обрабатывает текущее состояние и решает, какие действия выполнять дальше,
        используя инструменты с добавлением информации о состоянии браузера.

        Returns:
            bool: True, если обработка успешна, False в противном случае
        """
        # Сначала обновляем информацию о браузере
        await self.update_browser_state()

        # Вызываем родительский метод для обработки текущего состояния
        result = await super().think()
        return result

    async def format_next_step_prompt(self) -> str:
        """
        Форматирует подсказку для следующего шага с учетом состояния браузера.

        Returns:
            str: Отформатированная подсказка для следующего шага
        """
        browser_state = await self.get_browser_state()
        browser_state_str = ""

        if browser_state:
            browser_state_str = f"Текущее состояние браузера: {json.dumps(browser_state, ensure_ascii=False)}"

        # Заменяем метку {browser_state} в подсказке для следующего шага
        next_prompt = self.next_step_prompt.replace("{browser_state}", browser_state_str)

        return next_prompt
