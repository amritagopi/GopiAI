import json
from typing import Any, Optional

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.logger import logger
from app.prompt.browser import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import Message, ToolChoice

# from app.tool.tavily_tool import TavilyTool <-- Commenting out this import
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection


class BrowserAgent(ToolCallAgent):
    """
    A browser agent that uses the browser_use library to control a browser.

    This agent can navigate web pages, interact with elements, fill forms,
    extract content, and perform other browser-based actions to accomplish tasks.
    """

    name: str = "browser"
    description: str = "A browser agent that can control a browser to accomplish tasks"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # Используем правильное имя поля tools_collection вместо browser_tools
    tools_collection: ToolCollection = Field(
        default_factory=lambda: ToolCollection(Terminate())
    )

    # Use Auto for tool choice to allow both tool usage and free-form responses
    tool_choices: ToolChoice = ToolChoice.AUTO
    special_tool_names: list[str] = Field(
        default_factory=lambda: [Terminate().terminate_name]
    )

    _current_base64_image: Optional[str] = None

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        if not self._is_special_tool(name):
            return
        else:
            # Закомментируем код для BrowserUseTool
            # await self.tools_collection.get_tool(BrowserUseTool().name).cleanup()
            await super()._handle_special_tool(name, result, **kwargs)

    async def get_browser_state(self) -> Optional[dict]:
        """Get the current browser state for context in next steps."""
        # Возвращаем None, так как нет browser state при использовании Tavily
        return None

    async def think(self) -> bool:
        """Process current state and decide next actions using tools, with browser state info added"""
        # Так как нет browser state, просто вызываем родительский метод think
        result = await super().think()
        return result
