from typing import List, Optional, TypeVar, Generic, Dict, Iterable, SupportsIndex, overload
from crewai.tools import BaseTool

T = TypeVar('T', bound=BaseTool)

class ToolCollection(list, Generic[T]):
    """
    A collection of tools that can be accessed by index or name

    This class extends the built-in list to provide dictionary-like
    access to tools based on their name property.

    Usage:
        tools = ToolCollection(list_of_tools)
        # Access by index (regular list behavior)
        first_tool = tools[0]
        # Access by name (new functionality)
        search_tool = tools.by_name("search")
    """

    def __init__(self, tools: Optional[List[T]] = None):
        super().__init__(tools or [])
        self._name_cache: Dict[str, T] = {}
        self._build_name_cache()

    def _build_name_cache(self) -> None:
        self._name_cache = {tool.name: tool for tool in self}

    def by_name(self, name: str) -> T:
        return self._name_cache[name]

    def get_by_name(self, name: str, default: Optional[T] = None) -> Optional[T]:
        return self._name_cache.get(name, default)

    def append(self, tool: T) -> None:
        super().append(tool)
        self._name_cache[tool.name] = tool

    def extend(self, tools: Iterable[T]) -> None:
        super().extend(tools)
        self._build_name_cache()

    def insert(self, index: SupportsIndex, tool: T) -> None:
        super().insert(index, tool)
        self._name_cache[tool.name] = tool

    def remove(self, tool: T) -> None:
        super().remove(tool)
        if tool.name in self._name_cache:
            del self._name_cache[tool.name]

    @overload
    def pop(self) -> T: ...
    @overload
    def pop(self, index: SupportsIndex) -> T: ...
    def pop(self, index: SupportsIndex = -1) -> T:  # type: ignore[override]
        tool = super().pop(index)
        if tool.name in self._name_cache:
            del self._name_cache[tool.name]
        return tool

    def clear(self) -> None:
        super().clear()
        self._name_cache.clear()
