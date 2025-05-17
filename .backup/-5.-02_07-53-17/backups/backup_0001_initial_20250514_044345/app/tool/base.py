from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.interfaces import ITool
from app.interfaces import ToolResult as InterfaceToolResult


class BaseTool(BaseModel, ITool):
    """Base class for all tools.

    Implements the ITool interface to ensure standardized component interactions.
    """

    name: str
    description: str
    parameters: Optional[dict] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def name(self) -> str:
        """Возвращает имя инструмента.

        Реализует метод из интерфейса ITool.

        Returns:
            str: Имя инструмента
        """
        return self.name

    @property
    def description(self) -> str:
        """Возвращает описание инструмента.

        Реализует метод из интерфейса ITool.

        Returns:
            str: Описание инструмента
        """
        return self.description

    @property
    def parameters(self) -> Dict[str, Any]:
        """Возвращает параметры инструмента.

        Реализует метод из интерфейса ITool.

        Returns:
            Dict[str, Any]: Описание параметров инструмента
        """
        return self.parameters or {}

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует инструмент в словарь для использования в LLM API.

        Реализует метод из интерфейса ITool.

        Returns:
            Dict[str, Any]: Словарь с описанием инструмента
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters or {},
        }

    async def __call__(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        result = await self.execute(**kwargs)

        # Если результат уже соответствует интерфейсу, возвращаем его
        if isinstance(result, InterfaceToolResult):
            return result

        # Преобразуем старый формат результата в новый
        if isinstance(result, ToolResult):
            success = result.error is None
            message = str(result)
            data = {
                "output": result.output,
                "base64_image": result.base64_image,
                "system": result.system,
            }
            return InterfaceToolResult(success=success, message=message, data=data)

        # Если результат примитивного типа, преобразуем его в стандартный формат
        return InterfaceToolResult(
            success=True,
            message=str(result) if result is not None else "",
            data={"output": result},
        )

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters.

        This method should be implemented by concrete tool classes to provide
        the actual functionality.

        Args:
            **kwargs: Parameters for tool execution

        Returns:
            Any: Result of tool execution, which will be converted to ToolResult format
        """
        pass

    def to_param(self) -> Dict:
        """Convert tool to function call format."""
        # Определяем имя инструмента с учетом специального случая для Terminate
        tool_name = getattr(self, "terminate_name", None) or self.name

        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolResult(BaseModel):
    """Represents the result of a tool execution."""

    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    base64_image: Optional[str] = Field(default=None)
    system: Optional[str] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __bool__(self):
        return any(getattr(self, field) for field in self.__fields__)

    def __add__(self, other: "ToolResult"):
        def combine_fields(
            field: Optional[str], other_field: Optional[str], concatenate: bool = True
        ):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine tool results")
            return field or other_field

        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error),
            base64_image=combine_fields(self.base64_image, other.base64_image, False),
            system=combine_fields(self.system, other.system),
        )

    def __str__(self):
        return f"Error: {self.error}" if self.error else self.output

    def replace(self, **kwargs):
        """Returns a new ToolResult with the given fields replaced."""
        # return self.copy(update=kwargs)
        return type(self)(**{**self.dict(), **kwargs})

    def to_interface_result(self) -> InterfaceToolResult:
        """Converts this ToolResult to the standardized InterfaceToolResult.

        Returns:
            InterfaceToolResult: Standardized result format
        """
        success = self.error is None
        message = str(self)
        data = {
            "output": self.output,
            "base64_image": self.base64_image,
            "system": self.system,
        }
        return InterfaceToolResult(success=success, message=message, data=data)


class CLIResult(ToolResult):
    """A ToolResult that can be rendered as a CLI output."""


class ToolFailure(ToolResult):
    """A ToolResult that represents a failure."""

    def to_interface_result(self) -> InterfaceToolResult:
        """Converts this ToolFailure to the standardized InterfaceToolResult.

        Returns:
            InterfaceToolResult: Standardized result format with success=False
        """
        message = str(self)
        data = {
            "output": self.output,
            "base64_image": self.base64_image,
            "system": self.system,
        }
        return InterfaceToolResult(success=False, message=message, data=data)
