"""
Tool Integration for GopiAI
Provides integration with various tools using native CrewAI functionality
"""

import logging
from typing import Dict, Any, List, Optional, Type
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ToolIntegration:
    """Base class for tool integrations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: List[BaseTool] = []
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup tools for this integration"""
        raise NotImplementedError("Subclasses must implement _setup_tools")
    
    def get_tools(self) -> List[BaseTool]:
        """Get list of available tools"""
        return self.tools

class WebSearchTool(BaseTool):
    """Tool for performing web searches"""
    
    name: str = "web_search"
    description: str = "Search the web for information"
    
    class InputSchema(BaseModel):
        query: str = Field(..., description="Search query")
        max_results: int = Field(5, description="Maximum number of results to return")
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """Perform a web search"""
        # Use CrewAI's built-in web search tool
        from crewai.tools import SerperDevTool
        search_tool = SerperDevTool()
        return search_tool.run({"query": query, "max_results": max_results})

class FileReadTool(BaseTool):
    """Tool for reading files"""
    
    name: str = "read_file"
    description: str = "Read contents of a file"
    
    class InputSchema(BaseModel):
        file_path: str = Field(..., description="Path to the file to read")
    
    def _run(self, file_path: str) -> str:
        """Read file contents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WebIntegration(ToolIntegration):
    """Web-related tool integration"""
    
    def _setup_tools(self):
        self.tools = [
            WebSearchTool(),
            # Add more web-related tools here
        ]

class FileSystemIntegration(ToolIntegration):
    """Filesystem tool integration"""
    
    def _setup_tools(self):
        self.tools = [
            FileReadTool(),
            # Add more filesystem tools here
        ]

class ToolManager:
    """Manages all available tools"""
    
    def __init__(self):
        self.integrations: Dict[str, ToolIntegration] = {}
        self._setup_integrations()
    
    def _setup_integrations(self):
        """Setup all tool integrations"""
        self.add_integration('web', WebIntegration())
        self.add_integration('filesystem', FileSystemIntegration())
        # Add more integrations as needed
    
    def add_integration(self, name: str, integration: ToolIntegration):
        """Add a tool integration"""
        self.integrations[name] = integration
        logger.info(f"Added tool integration: {name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        for integration in self.integrations.values():
            for tool in integration.get_tools():
                if tool.name == tool_name:
                    return tool
        return None
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all available tools"""
        tools = []
        for integration in self.integrations.values():
            tools.extend(integration.get_tools())
        return tools

# Global instance
_tool_manager = None

def get_tool_manager() -> ToolManager:
    """Get the global tool manager instance"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager
