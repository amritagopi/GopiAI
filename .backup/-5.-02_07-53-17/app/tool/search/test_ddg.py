from duckduckgo_search import DDGS

def test_search():
    """Простой тест поиска через DuckDuckGo."""
    with DDGS() as ddgs:
        results = list(ddgs.text("Что такое искусственный интеллект?", max_results=3))

        print("Результаты поиска:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['href']}")
            print(f"   Описание: {result['body']}\n")

if __name__ == "__main__":
    test_search()
