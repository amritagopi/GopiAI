"""
🔍 GopiAI Web Search Tool для CrewAI
Простой инструмент для поиска в интернете с поддержкой разных поисковых систем
"""

import requests
import logging
import os
from typing import Type, Any, Optional, Dict, List
from pydantic import BaseModel, Field

# Безопасный импорт BeautifulSoup
try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None  # type: ignore

import json
import time
from urllib.parse import quote_plus

# Импортируем BaseTool из crewai с фоллбеком
try:
    from crewai.tools.base_tool import BaseTool  # type: ignore
except Exception:
    class BaseTool:  # минимальная заглушка
        name: str = "BaseTool"
        description: str = "Stub BaseTool when crewai is unavailable"

        def tool_schema(self):
            return {
                "type": "function",
                "function": {
                    "name": getattr(self, "name", "tool"),
                    "description": getattr(self, "description", ""),
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        def _run(self, *args, **kwargs):
            return {"error": "crewai BaseTool is unavailable"}

class WebSearchInput(BaseModel):
    """Схема входных данных для инструмента поиска в интернете"""
    query: str = Field(description="Поисковый запрос")
    search_engine: str = Field(default="duckduckgo", description="Поисковая система: duckduckgo, google_scrape, serper, serpapi")
    num_results: int = Field(default=10, description="Количество результатов (максимум 20)")
    language: str = Field(default="ru", description="Язык поиска (ru, en)")

class GopiAIWebSearchTool(BaseTool):
    """
    Инструмент для поиска в интернете
    
    Возможности:
    - Поиск через DuckDuckGo (без API ключа)
    - Поиск через Google (скрапинг)
    - Поиск через Serper API (с ключом)
    - Поиск через SerpAPI (с ключом)
    - Автоматический выбор доступного метода
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
            elif search_engine == "serper" and self.serper_key:
                return self._search_serper(query, num_results, language)
            elif search_engine == "serpapi" and self.serpapi_key:
                return self._search_serpapi(query, num_results, language)
            else:
                # Fallback к DuckDuckGo
                return self._search_duckduckgo(query, num_results, language)
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска в интернете: {e}")
            return f"❌ Ошибка поиска в интернете: {str(e)}"
    
    def _choose_best_search_engine(self) -> str:
        """Выбирает лучший доступный поисковый движок"""
        if self.serper_key:
            return "serper"
        elif self.serpapi_key:
            return "serpapi"
        else:
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
            if BeautifulSoup is None:
                return "❌ BeautifulSoup (bs4) не установлен — парсинг результатов недоступен"
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
                response_text = f"🔍 Результаты поиска DuckDuckGo для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f"❌ Результаты поиска не найдены для запроса '{query}' в DuckDuckGo"
                
        except Exception as e:
            return f"❌ Ошибка поиска в DuckDuckGo: {str(e)}"
    
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
                response_text = f"🔍 Результаты поиска Google для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f"❌ Результаты поиска не найдены для запроса '{query}' в Google"
                
        except Exception as e:
            return f"❌ Ошибка поиска в Google: {str(e)}"
    
    def _search_serper(self, query: str, num_results: int, language: str) -> str:
        """Поиск через Serper API"""
        try:
            url = "https://google.serper.dev/search"
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            if language == "ru":
                payload["gl"] = "ru"
                payload["hl"] = "ru"
            
            headers = {
                "X-API-KEY": self.serper_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Извлекаем органические результаты
            if 'organic' in data:
                for result in data['organic'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', '')
                    })
            
            # Формируем ответ
            if results:
                response_text = f"🔍 Результаты поиска Serper для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f"❌ Результаты поиска не найдены для запроса '{query}' в Serper"
                
        except Exception as e:
            return f"❌ Ошибка поиска в Serper: {str(e)}"
    
    def _search_serpapi(self, query: str, num_results: int, language: str) -> str:
        """Поиск через SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            
            params = {
                "engine": "google",
                "q": query,
                "num": num_results,
                "api_key": self.serpapi_key
            }
            
            if language == "ru":
                params["gl"] = "ru"
                params["hl"] = "ru"
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Извлекаем органические результаты
            if 'organic_results' in data:
                for result in data['organic_results'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', '')
                    })
            
            # Формируем ответ
            if results:
                response_text = f"🔍 Результаты поиска SerpAPI для '{query}' ({len(results)} результатов):\n\n"
                for i, result in enumerate(results, 1):
                    response_text += f"{i}. **{result['title']}**\n"
                    response_text += f"   {result['link']}\n"
                    if result['snippet']:
                        response_text += f"   {result['snippet']}\n"
                    response_text += "\n"
                return response_text
            else:
                return f"❌ Результаты поиска не найдены для запроса '{query}' в SerpAPI"
                
        except Exception as e:
            return f"❌ Ошибка поиска в SerpAPI: {str(e)}"
    
    def get_available_engines(self) -> List[str]:
        """Возвращает список доступных поисковых движков"""
        engines = ["duckduckgo", "google_scrape"]
        
        if self.serper_key:
            engines.append("serper")
        
        if self.serpapi_key:
            engines.append("serpapi")
        
        return engines