import logging
import sys


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stderr)])

import argparse
import asyncio
import atexit
import json
import os
import importlib
from inspect import Parameter, Signature
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from app.logger import logger
from app.tool.base import BaseTool
from app.tool.bash import Bash
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.terminate import Terminate


class MCPServer:
    """MCP Server implementation with tool registration and management."""

    def __init__(self, name: str = "openmanus", config_path: str = "mcp.json"):
        self.server = FastMCP(name)
        self.tools: Dict[str, BaseTool] = {}
        self.config_path = config_path
        self.config = self._load_config()

        # Initialize standard tools
        self.tools["bash"] = Bash()
        self.tools["browser"] = BrowserUseTool()
        self.tools["editor"] = StrReplaceEditor()
        self.tools["terminate"] = Terminate()

        # Initialize tools from config
        self._load_tools_from_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                logger.info(f"Loaded MCP configuration from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"Error loading MCP configuration: {e}")
        else:
            logger.warning(f"MCP configuration file not found at {self.config_path}, using defaults")
        return {"tools": [], "servers": []}

    def _load_tools_from_config(self) -> None:
        """Load tools defined in the MCP configuration."""
        if not self.config or "tools" not in self.config:
            return

        for tool_config in self.config.get("tools", []):
            name = tool_config.get("name")
            path = tool_config.get("path")

            if not name or not path:
                logger.warning(f"Skipping invalid tool configuration: {tool_config}")
                continue

            try:
                # Convert path to module reference
                module_path = path.replace("/", ".").replace(".py", "")
                module = importlib.import_module(module_path)

                # Register specific tools if listed
                tool_names = tool_config.get("tools", [])
                if tool_names:
                    for tool_name in tool_names:
                        if hasattr(module, tool_name):
                            tool_func = getattr(module, tool_name)
                            self._register_function_as_tool(tool_name, tool_func)
                        else:
                            logger.warning(f"Tool function {tool_name} not found in {path}")
                else:
                    # Register all public functions in the module
                    for attr_name in dir(module):
                        if not attr_name.startswith("_"):
                            attr = getattr(module, attr_name)
                            if callable(attr) and asyncio.iscoroutinefunction(attr):
                                self._register_function_as_tool(attr_name, attr)

                logger.info(f"Loaded tools from {path}")
            except Exception as e:
                logger.error(f"Error loading tools from {path}: {e}")

    def _register_function_as_tool(self, name: str, func) -> None:
        """Register a function directly as an MCP tool."""
        # Create a wrapper function with the same signature
        async def tool_wrapper(**kwargs):
            try:
                logger.info(f"Executing {name}: {kwargs}")
                result = await func(**kwargs)
                return result
            except Exception as e:
                logger.error(f"Error executing {name}: {e}")
                return json.dumps({"status": "error", "message": str(e)})

        # Set method metadata
        tool_wrapper.__name__ = name
        tool_wrapper.__doc__ = func.__doc__

        # Register with server
        self.server.tool()(tool_wrapper)
        logger.info(f"Registered function as tool: {name}")

    def register_tool(self, tool: BaseTool, method_name: Optional[str] = None) -> None:
        """Register a tool with parameter validation and documentation."""
        tool_name = method_name or tool.name
        tool_param = tool.to_param()
        tool_function = tool_param["function"]

        # Define the async function to be registered
        async def tool_method(**kwargs):
            logger.info(f"Executing {tool_name}: {kwargs}")
            result = await tool.execute(**kwargs)

            logger.info(f"Result of {tool_name}: {result}")

            # Handle different types of results (match original logic)
            if hasattr(result, "model_dump"):
                return json.dumps(result.model_dump())
            elif isinstance(result, dict):
                return json.dumps(result)
            return result

        # Set method metadata
        tool_method.__name__ = str(tool_name)
        tool_method.__doc__ = self._build_docstring(tool_function)
        tool_method.__signature__ = self._build_signature(tool_function)

        # Store parameter schema (important for tools that access it programmatically)
        param_props = tool_function.get("parameters", {}).get("properties", {})
        required_params = tool_function.get("parameters", {}).get("required", [])
        tool_method._parameter_schema = {
            param_name: {
                "description": param_details.get("description", ""),
                "type": param_details.get("type", "any"),
                "required": param_name in required_params,
            }
            for param_name, param_details in param_props.items()
        }

        # Register with server
        self.server.tool()(tool_method)
        logger.info(f"Registered tool: {tool_name}")

    def _build_docstring(self, tool_function: dict) -> str:
        """Build a formatted docstring from tool function metadata."""
        description = tool_function.get("description", "")
        param_props = tool_function.get("parameters", {}).get("properties", {})
        required_params = tool_function.get("parameters", {}).get("required", [])

        # Build docstring (match original format)
        docstring = description
        if param_props:
            docstring += "\n\nParameters:\n"
            for param_name, param_details in param_props.items():
                required_str = (
                    "(required)" if param_name in required_params else "(optional)"
                )
                param_type = param_details.get("type", "any")
                param_desc = param_details.get("description", "")
                docstring += (
                    f"    {param_name} ({param_type}) {required_str}: {param_desc}\n"
                )

        return docstring

    def _build_signature(self, tool_function: dict) -> Signature:
        """Build a function signature from tool function metadata."""
        param_props = tool_function.get("parameters", {}).get("properties", {})
        required_params = tool_function.get("parameters", {}).get("required", [])

        parameters = []

        # Follow original type mapping
        for param_name, param_details in param_props.items():
            param_type = param_details.get("type", "")
            default = Parameter.empty if param_name in required_params else None

            # Map JSON Schema types to Python types (same as original)
            annotation = Any
            if param_type == "string":
                annotation = str
            elif param_type == "integer":
                annotation = int
            elif param_type == "number":
                annotation = float
            elif param_type == "boolean":
                annotation = bool
            elif param_type == "object":
                annotation = dict
            elif param_type == "array":
                annotation = list

            # Create parameter with same structure as original
            param = Parameter(
                name=param_name,
                kind=Parameter.KEYWORD_ONLY,
                default=default,
                annotation=annotation,
            )
            parameters.append(param)

        return Signature(parameters=parameters)

    async def cleanup(self) -> None:
        """Clean up server resources."""
        logger.info("Cleaning up resources")
        # Follow original cleanup logic - only clean browser tool
        if "browser" in self.tools and hasattr(self.tools["browser"], "cleanup"):
            await self.tools["browser"].cleanup()

    def register_all_tools(self) -> None:
        """Register all tools with the server."""
        for tool in self.tools.values():
            self.register_tool(tool)

    def run(self, transport: str = "stdio") -> None:
        """Run the MCP server."""
        # Register all tools
        self.register_all_tools()

        # Register cleanup function (match original behavior)
        atexit.register(lambda: asyncio.run(self.cleanup()))

        # Start server (with same logging as original)
        logger.info(f"Starting OpenManus server ({transport} mode)")
        self.server.run(transport=transport)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="OpenManus MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Communication method: stdio or http (default: stdio)",
    )
    parser.add_argument(
        "--config",
        default="mcp.json",
        help="Path to MCP configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Create and run server with configuration
    server = MCPServer(config_path=args.config)
    server.run(transport=args.transport)
