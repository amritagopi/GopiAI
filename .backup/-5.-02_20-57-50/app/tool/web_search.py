"""
Web search tools adapter for browser_use_tool
Using DuckDuckGo search engine
"""

from app.tool.base import BaseTool, ToolResult
from app.tool.search import DuckDuckGoSearchEngine

class WebSearch(BaseTool):
    """Web search tool that uses DuckDuckGo."""

    name: str = "web_search"
    description: str = "Search the web for information using DuckDuckGo."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    engine: DuckDuckGoSearchEngine = None

    def __init__(self):
        super().__init__()
        self.engine = DuckDuckGoSearchEngine()

    async def execute(
        self, query: str, num_results: int = 5, **kwargs
    ) -> ToolResult:
        """Execute web search using DuckDuckGo."""
        try:
            print(f"Executing search for query: {query}")
            results = await self.engine.perform_search(query, num_results=num_results)
            print(f"Raw search results: {results}")
            formatted_results = self._format_results(results)
            print(f"Formatted results: {formatted_results}")

            # Возвращаем результаты в обоих полях для совместимости
            return ToolResult(
                output=formatted_results,
                results=results,  # Добавляем результаты в поле results
                success=True
            )
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return ToolResult(
                error=f"Error performing web search: {str(e)}",
                success=False
            )

    def _format_results(self, results):
        """Format search results into a readable string."""
        if not results:
            return "No results found."

        formatted = "Search results:\n\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", result.get("href", "No URL"))
            snippet = result.get("snippet", result.get("body", "No description"))

            formatted += f"{i}. {title}\n"
            formatted += f"   URL: {url}\n"
            formatted += f"   {snippet}\n\n"

        return formatted
