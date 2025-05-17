from duckduckgo_search import DDGS

from app.tool.search.base import WebSearchEngine


class DuckDuckGoSearchEngine(WebSearchEngine):
    async def perform_search(self, query: str, num_results: int = 10, *args, **kwargs):
        """DuckDuckGo search engine."""
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=num_results))
            print(f"Raw DuckDuckGo results: {raw_results}")  # Debug print

            formatted_results = []
            for result in raw_results:
                # Print each raw result to see its structure
                print(f"Processing result: {result}")
                formatted_results.append({
                    "title": result.get("title", "No title"),
                    "url": result.get("href", "No URL"),  # Сохраняем 'href' как 'url'
                    "snippet": result.get("body", "No description"),  # Сохраняем 'body' как 'snippet'
                    # Добавляем оригинальные поля для совместимости
                    "href": result.get("href", "No URL"),
                    "body": result.get("body", "No description")
                })

            return formatted_results
