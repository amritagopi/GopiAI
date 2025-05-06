from typing import Any, Dict, List, Optional
# from app.tool.search.search_web import TavilyTool # Incorrect import
# from app.tool.tavily_tool import TavilyTool # Correct import

class PlanningAgent:
    """Mock implementation of PlanningAgent."""

    def __init__(self, name: str = "planning", tavily_api_key: Optional[str] = None):
        """Initialize a planning agent.

        Args:
            name (str): Name of the agent.
            tavily_api_key (Optional[str]): API key for Tavily. If not provided, will be loaded from config.
        """
        self.name = name
        self.plan = {}
        self.tools = []
        # Регистрация TavilyTool (ключ будет загружен из config.toml внутри TavilyTool)
        # tavily_tool = TavilyTool(api_key=tavily_api_key) # Rely on TavilyTool internal config loading
        # tavily_tool = TavilyTool() # Rely on TavilyTool internal config loading

    def register_tool(self, tool: Any) -> None:
        """Register a tool for the agent to use."""
        tool_name = tool.name
        self.tools.append({"name": tool_name, "tool": tool})

    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the provided data."""
        task = data.get("task", "")
        if not task:
            return {"error": "No task provided"}
        return await self.create_initial_plan(task)

    async def create_initial_plan(self, request: str) -> Dict[str, Any]:
        """Create an initial plan based on the request, using Tavily for research."""
        for tool in self.tools:
            if tool["name"] == "tavily_search":
                search_results = tool["tool"].search(request)
                break
        else:
            search_results = "Нет данных: инструмент поиска не найден."

        self.plan = {
            "title": f"Plan for: {request[:50]}...",
            "steps": [
                {"id": 1, "description": f"Research results: {search_results[:100]}..."},
                {"id": 2, "description": "Create initial draft"},
                {"id": 3, "description": "Review and optimize"},
                {"id": 4, "description": "Finalize and distribute"}
            ],
            "status": "created"
        }
        return self.plan

    async def get_plan(self) -> Dict[str, Any]:
        """Get the current plan."""
        return self.plan
