"""
🔍 GopiAI Web Search Tool для CrewAI
Инструмент для поиска в интернете с поддержкой разных поисковых систем:
- Brave Search API
- Tavily API
- Exa AI Search
- Firecrawl API
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Type, Union
from urllib.parse import parse_qs, quote_plus, urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from crewai.tools.agent_tools import StructuredTool as BaseTool
import os

def get_from_dict_or_env(data: dict, key: str, env_key: str, default=None):
    """Получает значение из словаря или переменных окружения"""
    if data and key in data:
        return data[key]
    return os.getenv(env_key, default)


class WebSearchInput(BaseModel):
    """Схема входных данных для инструмента поиска в интернете"""
    query: str = Field(description="Поисковый запрос")
    search_engine: str = Field(
        default="auto", 
        description="Поисковая система: auto, brave, tavily, exa, firecrawl, duckduckgo, google_scrape"
    )
    num_results: int = Field(default=5, description="Количество результатов (максимум 20)")
    language: str = Field(default="ru", description="Язык поиска (ru, en, etc.)")
    include_domains: Optional[List[str]] = Field(
        default=None, 
        description="Список доменов для включения в результаты (поддерживается не всеми API)"
    )


class GopiAIWebSearchTool(BaseTool):
    """
    Инструмент для поиска в интернете
    
    Поддерживаемые поисковые системы:
    - Brave Search API (требуется API ключ)
    - Tavily API (требуется API ключ)
    - Exa AI Search (требуется API ключ)
    - Firecrawl API (требуется API ключ)
    - DuckDuckGo (без API ключа)
    - Google (скрапинг, без API ключа)
    
    При выборе 'auto' автоматически выбирает лучший доступный метод.
    """
    
    name: str = Field(default="gopiai_web_search", description="Инструмент поиска в интернете")
    description: str = Field(default="""Инструмент для поиска информации в интернете.
    Поддерживает разные поисковые системы и автоматически выбирает доступный метод.
    Не требует API ключей для базового функционала.""", description="Описание инструмента")
    args_schema: Type[BaseModel] = WebSearchInput
    
    def __init__(self):
        """Инициализация инструмента поиска"""
        super().__init__()
    
    @property
    def logger(self):
        """Получение логгера для инструмента"""
        return logging.getLogger(__name__)
    
    @property
    def session(self):
        """Получение HTTP сессии"""
        if not hasattr(self, '_session'):
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        return self._session
    
    @property
    def timeout(self):
        """Получение таймаута"""
        return 10
    
    @property
    def serper_key(self):
        """Получение API ключа Serper"""
        return os.getenv('SERPER_API_KEY')
    
    @property
    def serpapi_key(self):
        """Получение API ключа SerpAPI"""
        return os.getenv('SERPAPI_API_KEY')
    
    def _run(self, query: str, search_engine: str = "duckduckgo", num_results: int = 10, language: str = "ru") -> str:
        """
        Выполнение поиска в интернете
        """
        try:
            # Валидация запроса
            if not query or not query.strip():
                return "❌ Поисковый запрос не указан"
            
            # Ограничиваем количество результатов
            num_results = min(max(num_results, 1), 20)
            
            # Выбираем метод поиска
            if search_engine == "auto":
                search_engine = self._choose_best_search_engine()
            
            # Выполняем поиск
            if search_engine == "duckduckgo":
                return self._search_duckduckgo(query, num_results, language)
            elif search_engine == "google_scrape":
                return self._search_google_scrape(query, num_results, language)
            elif search_engine == "brave" and os.getenv("BRAVE_API_KEY"):
                return self._search_brave(query, num_results, language)
            elif search_engine == "tavily" and os.getenv("TAVILY_API_KEY"):
                return self._search_tavily(query, num_results, language)
            elif search_engine == "exa" and os.getenv("EXA_API_KEY"):
                return self._search_exa(query, num_results, language)
            else:
                # Fallback к DuckDuckGo
                return self._search_duckduckgo(query, num_results, language)
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска в интернете: {e}")
            return f"❌ Ошибка поиска в интернете: {str(e)}"
    
    def _choose_best_search_engine(self) -> str:
        """Выбирает лучший доступный поисковый движок"""
        # Проверяем наличие API ключей в порядке приоритета
        if os.getenv("BRAVE_API_KEY"):
            return "brave"
        elif os.getenv("TAVILY_API_KEY"):
            return "tavily"
        elif os.getenv("EXA_API_KEY"):
            return "exa"
        elif os.getenv("FIRECRAWL_API_KEY"):
            return "firecrawl"
        else:
            # Если нет API ключей, используем бесплатные варианты
            return "duckduckgo"
    
    def _search_duckduckgo(self, query: str, num_results: int, language: str) -> str:
        """Поиск через DuckDuckGo (без API ключа)"""
        try:
            # Формируем URL для поиска
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            if language == "ru":
                url += "&kl=ru-ru"
            
            # Выполняем запрос
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Парсим результаты
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Ищем результаты поиска
            search_results = soup.find_all('div', class_='result')
            
            for result in search_results[:num_results]:
                try:
                    # Извлекаем заголовок и ссылку
                    title_elem = result.find('a', class_='result__a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # Извлекаем описание
                    snippet_elem = result.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and link:
                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Ошибка парсинга результата DuckDuckGo: {e}")
                    continue
            
            # Формируем ответ
            if results:
                response_text = f" Результаты поиска DuckDuckGo для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f" Результаты поиска не найдены для запроса '{query}' в DuckDuckGo"
                
        except Exception as e:
            return f" Ошибка поиска в DuckDuckGo: {str(e)}"
    
    def _search_google_scrape(self, query: str, num_results: int, language: str) -> str:
        """Поиск через Google (скрапинг)"""
        try:
            # Формируем URL для поиска
            encoded_query = quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            if language == "ru":
                url += "&hl=ru&lr=lang_ru"
            
            # Выполняем запрос
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Парсим результаты
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Ищем результаты поиска (Google часто меняет классы)
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results[:num_results]:
                try:
                    # Извлекаем заголовок и ссылку
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    
                    # Извлекаем описание
                    snippet_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and link and link.startswith('http'):
                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Ошибка парсинга результата Google: {e}")
                    continue
            
            # Формируем ответ
            if results:
                response_text = f" Результаты поиска Google для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f" Результаты поиска не найдены для запроса '{query}' в Google"
                
        except Exception as e:
            return f" Ошибка поиска в Google: {str(e)}"
    
    def _search_brave(self, query: str, num_results: int = 10, language: str = "ru") -> List[Dict]:
        """Поиск через Brave Search API"""
        try:
            api_key = os.getenv("BRAVE_API_KEY")
            if not api_key:
                self.logger.warning("BRAVE_API_KEY не найден в переменных окружения")
                return []
                
            headers = {
                "X-Subscription-Token": api_key,
                "Accept": "application/json",
            }
            
            params = {
                "q": query,
                "count": num_results,
                "country": "ru" if language == "ru" else "us",
                "ui_lang": language
            }
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'web' in data and 'results' in data['web']:
                for i, result in enumerate(data['web']['results'][:num_results], 1):
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('url', ''),
                        'snippet': result.get('description', '')[:200] + '...' if 'description' in result else '',
                        'source': 'brave',
                        'position': i
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка при поиске через Brave API: {e}")
            return []
            
    def _search_tavily(self, query: str, num_results: int = 5, language: str = "ru") -> List[Dict]:
        """Поиск через Tavily API"""
        try:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                self.logger.warning("TAVILY_API_KEY не найден в переменных окружения")
                return []
                
            url = "https://api.tavily.com/search"
            
            payload = {
                "api_key": api_key,
                "query": query,
                "include_answer": False,
                "include_raw_content": False,
                "max_results": num_results,
                "include_domains": [],
                "exclude_domains": [],
                "search_depth": "basic",
            }
            
            if language == "ru":
                payload["include_domains"] = [".ru", ".рф"]
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'results' in data:
                for i, result in enumerate(data['results'][:num_results], 1):
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('url', ''),
                        'snippet': result.get('content', '')[:200] + '...' if 'content' in result else '',
                        'source': 'tavily',
                        'position': i
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка при поиске через Tavily API: {e}")
            return []
            
    def get_available_engines(self) -> List[str]:
        """Возвращает список доступных поисковых движков"""
        engines = ["duckduckgo", "google_scrape"]
        
        # Добавляем API-зависимые движки, если ключи доступны
        if os.getenv("BRAVE_API_KEY"):
            engines.append("brave")
            
        if os.getenv("TAVILY_API_KEY"):
            engines.append("tavily")
            
        if os.getenv("EXA_API_KEY"):
            engines.append("exa")
            
        if os.getenv("FIRECRAWL_API_KEY"):
            engines.append("firecrawl")
        
        return engines