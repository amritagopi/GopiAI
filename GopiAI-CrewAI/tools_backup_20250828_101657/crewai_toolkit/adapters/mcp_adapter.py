from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from crewai.tools import BaseTool
# Поддержка разных версий структуры пакета crewai_tools
try:
    # Новые версии экспортируют напрямую из корня
    from crewai_tools import ToolCollection  # type: ignore[reportMissingImports]
except Exception:
    # Фолбэк для старых версий
    from crewai_tools.tool_collection import ToolCollection  # type: ignore[reportMissingImports]
"""
MCPServer for CrewAI.


"""
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from mcp import StdioServerParameters
    try:
        from mcpadapt.core import MCPAdapt  # type: ignore[reportMissingImports]
        from mcpadapt.crewai_adapter import CrewAIAdapter  # type: ignore[reportMissingImports]
    except Exception:
        # Подсказки типизации, если пакета нет в окружении
        from typing import Any as MCPAdapt  # type: ignore[assignment]
        from typing import Any as CrewAIAdapter  # type: ignore[assignment]


try:
    from mcp import StdioServerParameters  # type: ignore[reportMissingImports]
    from mcpadapt.core import MCPAdapt  # type: ignore[reportMissingImports]
    from mcpadapt.crewai_adapter import CrewAIAdapter  # type: ignore[reportMissingImports]

    MCP_AVAILABLE = True
except Exception:
    MCP_AVAILABLE = False


class MCPServerAdapter:
    """Manages the lifecycle of an MCP server and make its tools available to CrewAI.

    Note: tools can only be accessed after the server has been started with the
        `start()` method.

    Attributes:
        tools: The CrewAI tools available from the MCP server.

    Usage:
        # context manager + stdio
        with MCPServerAdapter(...) as tools:
            # tools is now available

        # context manager + sse
        with MCPServerAdapter({"url": "http://localhost:8000/sse"}) as tools:
            # tools is now available

        # manually stop mcp server
        try:
            mcp_server = MCPServerAdapter(...)
            tools = mcp_server.tools
            ...
        finally:
            mcp_server.stop()

        # Best practice is ensure cleanup is done after use.
        mcp_server.stop() # run after crew().kickoff()
    """

    def __init__(
        self,
        serverparams: StdioServerParameters | dict[str, Any],
    ):
        """Initialize the MCP Server

        Args:
            serverparams: The parameters for the MCP server it supports either a
                `StdioServerParameters` or a `dict` respectively for STDIO and SSE.

        """

        super().__init__()
        self._adapter: "MCPAdapt | None" = None
        self._tools: "ToolCollection[BaseTool] | None" = None

        if not MCP_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'mcp' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "mcp crewai-tools[mcp]"], check=True)

                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install mcp package")
            else:
                raise ImportError(
                    "`mcp` package not found, please run `uv add crewai-tools[mcp]`"
                )

        try:
            self._serverparams = serverparams
            self._adapter = MCPAdapt(self._serverparams, CrewAIAdapter())
            self.start()

        except Exception as e:
            if self._adapter is not None:
                try:
                    self.stop()
                except Exception as stop_e:
                    logger.error(f"Error during stop cleanup: {stop_e}")
            raise RuntimeError(f"Failed to initialize MCP Adapter: {e}") from e

    def start(self):
        """Start the MCP server and initialize the tools."""
        if self._adapter is None:
            raise RuntimeError("MCP adapter is not initialized")
        self._tools = self._adapter.__enter__()  # type: ignore[reportAttributeAccessIssue]

    def stop(self):
        """Stop the MCP server"""
        if self._adapter is not None:
            self._adapter.__exit__(None, None, None)  # type: ignore[reportAttributeAccessIssue]

    @property
    def tools(self) -> ToolCollection[BaseTool]:
        """The CrewAI tools available from the MCP server.

        Raises:
            ValueError: If the MCP server is not started.

        Returns:
            The CrewAI tools available from the MCP server.
        """
        if self._tools is None:
            raise ValueError(
                "MCP server not started, run `mcp_server.start()` first before accessing `tools`"
            )
        return ToolCollection(self._tools)

    def __enter__(self):
        """
        Enter the context manager. Note that `__init__()` already starts the MCP server.
        So tools should already be available.
        """
        return self.tools

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        if self._adapter is not None:
            return self._adapter.__exit__(exc_type, exc_value, traceback)  # type: ignore[reportAttributeAccessIssue]
        return None
