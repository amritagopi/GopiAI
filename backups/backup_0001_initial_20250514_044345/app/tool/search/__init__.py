"""Search engines for the agent."""

from app.tool.search.base import WebSearchEngine
from app.tool.search.duckduckgo_search import DuckDuckGoSearchEngine

__all__ = [
    "WebSearchEngine",
    "DuckDuckGoSearchEngine",
]
