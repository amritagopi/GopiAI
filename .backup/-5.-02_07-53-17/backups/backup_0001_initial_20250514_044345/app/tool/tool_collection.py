"""Collection classes for managing multiple tools."""

from typing import Any, Dict, List

from pydantic import ConfigDict

from app.exceptions import ToolError
from app.tool.base import BaseTool, ToolFailure, ToolResult


class ToolCollection:
    """A collection of defined tools."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *tools: BaseTool):
        self.tools = tools
        self.tool_map = {}

        # Заполняем tool_map с учетом специфики Terminate
        for tool in tools:
            if hasattr(tool, "terminate_name"):
                # Если это класс Terminate или его наследник
                self.tool_map[tool.terminate_name] = tool
            else:
                # Для обычных инструментов
                self.tool_map[tool.name] = tool

    def __iter__(self):
        return iter(self.tools)

    def to_params(self) -> List[Dict[str, Any]]:
        return [tool.to_param() for tool in self.tools]

    async def execute(
        self, *, name: str, tool_input: Dict[str, Any] = None
    ) -> ToolResult:
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        try:
            result = await tool(**tool_input)
            return result
        except ToolError as e:
            return ToolFailure(error=e.message)

    async def execute_all(self) -> List[ToolResult]:
        """Execute all tools in the collection sequentially."""
        results = []
        for tool in self.tools:
            try:
                result = await tool()
                results.append(result)
            except ToolError as e:
                results.append(ToolFailure(error=e.message))
        return results

    def get_tool(self, name: str) -> BaseTool:
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        self.tools += (tool,)

        # Добавляем инструмент с учетом специфики Terminate
        if hasattr(tool, "terminate_name"):
            # Если это класс Terminate или его наследник
            self.tool_map[tool.terminate_name] = tool
        else:
            # Для обычных инструментов
            self.tool_map[tool.name] = tool

        return self

    def add_tools(self, *tools: BaseTool):
        for tool in tools:
            self.add_tool(tool)
        return self
