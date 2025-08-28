"""
🌐 GopiAI Web Viewer Tool для CrewAI
Простой инструмент для просмотра веб-страниц без автоматизации браузера
"""

import requests
import logging
from typing import Type, Any, Optional, Dict
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool

class WebViewerInput(BaseModel):
    """Схема входных данных для инструмента просмотра веб-страниц"""
    action: str = Field(description="Действие: fetch, extract_text, extract_links, get_title, get_meta")
    url: str = Field(description="URL веб-страницы для просмотра")
    selector: str = Field(default="", description="CSS селектор для извлечения конкретных элементов")
    max_length: int = Field(default=5000, description="Максимальная длина извлекаемого текста")

class GopiAIWebViewerTool(BaseTool):
    """
    Простой инструмент для просмотра веб-страниц
    
    Возможности:
    - Загрузка веб-страниц через HTTP/HTTPS
    - Извлечение текста и метаданных
    - Поиск ссылок и элементов
    - Безопасный парсинг HTML
    """
    
    name: str = Field(default="gopiai_web_viewer", description="Инструмент просмотра веб-страниц")
    description: str = Field(default="""Простой инструмент для просмотра веб-страниц без автоматизации браузера.
    Поддерживает: загрузку страниц, извлечение текста, поиск ссылок, получение метаданных.
    Безопасен и не требует установки браузерных драйверов.""", description="Описание инструмента")
    args_schema: Type[BaseModel] = WebViewerInput
    
    def __init__(self):
        """Инициализация инструмента просмотра веб-страниц"""
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
    def _page_cache(self):
        """Получение кэша страниц"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        return self._cache
    
    def _run(self, action: str, url: str, selector: str = "", max_length: int = 5000) -> str:
        """
        Выполнение действия просмотра веб-страницы
        """
        try:
            # Валидация URL
            if not url or not url.strip():
                return "❌ URL не указан"
            
            # Добавляем протокол если отсутствует
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Выполняем действие
            if action == "fetch":
                return self._fetch_page(url)
            elif action == "extract_text":
                return self._extract_text(url, selector, max_length)
            elif action == "extract_links":
                return self._extract_links(url)
            elif action == "get_title":
                return self._get_title(url)
            elif action == "get_meta":
                return self._get_meta(url)
            else:
                return f"❌ Неизвестное действие: {action}. Доступные: fetch, extract_text, extract_links, get_title, get_meta"
                
        except Exception as e:
            self.logger.error(f"Ошибка просмотра веб-страницы: {e}")
            return f"❌ Ошибка просмотра веб-страницы: {str(e)}"
    
    def _fetch_page(self, url: str) -> str:
        """Загружает веб-страницу и возвращает основную информацию"""
        try:
            # Проверяем кэш
            if url in self._page_cache:
                self.logger.info(f"Используем кэшированную страницу: {url}")
                soup = self._page_cache[url]
            else:
                # Загружаем страницу
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Парсим HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                self._page_cache[url] = soup
            
            # Извлекаем основную информацию
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "Без названия"
            
            # Извлекаем описание
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Извлекаем основной текст (первые 2000 символов)
            body_text = ""
            body = soup.find('body')
            if body:
                # Удаляем скрипты и стили
                for script in body(["script", "style"]):
                    script.decompose()
                body_text = body.get_text(separator=' ', strip=True)[:2000]
            
            result = f"""✅ Страница загружена: {url}
            
📄 Заголовок: {title_text}

📝 Описание: {description}

📖 Содержимое (первые 2000 символов):
{body_text}

🔗 URL: {url}
📊 Статус: Успешно загружено
"""
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ Ошибка загрузки страницы {url}: {str(e)}"
        except Exception as e:
            return f"❌ Ошибка парсинга страницы {url}: {str(e)}"
    
    def _extract_text(self, url: str, selector: str = "", max_length: int = 5000) -> str:
        """Извлекает текст со страницы"""
        try:
            # Загружаем страницу если не в кэше
            if url not in self._page_cache:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                self._page_cache[url] = soup
            else:
                soup = self._page_cache[url]
            
            # Извлекаем текст
            if selector:
                # Используем CSS селектор
                elements = soup.select(selector)
                if not elements:
                    return f"❌ Элементы с селектором '{selector}' не найдены на {url}"
                
                texts = []
                for elem in elements[:10]:  # Максимум 10 элементов
                    text = elem.get_text(separator=' ', strip=True)
                    if text:
                        texts.append(text)
                
                result_text = '\n\n'.join(texts)
            else:
                # Извлекаем весь текст страницы
                # Удаляем скрипты и стили
                for script in soup(["script", "style", "nav", "header", "footer"]):
                    script.decompose()
                
                result_text = soup.get_text(separator=' ', strip=True)
            
            # Ограничиваем длину
            if len(result_text) > max_length:
                result_text = result_text[:max_length] + "..."
            
            return f"✅ Извлечен текст с {url} ({len(result_text)} символов):\n\n{result_text}"
            
        except Exception as e:
            return f"❌ Ошибка извлечения текста с {url}: {str(e)}"
    
    def _extract_links(self, url: str) -> str:
        """Извлекает ссылки со страницы"""
        try:
            # Загружаем страницу если не в кэше
            if url not in self._page_cache:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                self._page_cache[url] = soup
            else:
                soup = self._page_cache[url]
            
            # Извлекаем ссылки
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Преобразуем относительные ссылки в абсолютные
                absolute_url = urljoin(url, href)
                
                # Фильтруем только HTTP/HTTPS ссылки
                if absolute_url.startswith(('http://', 'https://')):
                    links.append({
                        'url': absolute_url,
                        'text': text[:100] if text else 'Без текста'
                    })
            
            # Ограничиваем количество ссылок
            links = links[:20]
            
            result = f"✅ Найдено {len(links)} ссылок на {url}:\n\n"
            for i, link in enumerate(links, 1):
                result += f"{i}. {link['text']}\n   {link['url']}\n\n"
            
            return result
            
        except Exception as e:
            return f"❌ Ошибка извлечения ссылок с {url}: {str(e)}"
    
    def _get_title(self, url: str) -> str:
        """Получает заголовок страницы"""
        try:
            # Загружаем страницу если не в кэше
            if url not in self._page_cache:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                self._page_cache[url] = soup
            else:
                soup = self._page_cache[url]
            
            title = soup.find('title')
            if title:
                title_text = title.get_text(strip=True)
                return f"✅ Заголовок страницы {url}: {title_text}"
            else:
                return f"❌ Заголовок не найден на {url}"
                
        except Exception as e:
            return f"❌ Ошибка получения заголовка с {url}: {str(e)}"
    
    def _get_meta(self, url: str) -> str:
        """Получает метаданные страницы"""
        try:
            # Загружаем страницу если не в кэше
            if url not in self._page_cache:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                self._page_cache[url] = soup
            else:
                soup = self._page_cache[url]
            
            meta_info = {}
            
            # Заголовок
            title = soup.find('title')
            if title:
                meta_info['title'] = title.get_text(strip=True)
            
            # Описание
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                meta_info['description'] = meta_desc.get('content', '')
            
            # Ключевые слова
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                meta_info['keywords'] = meta_keywords.get('content', '')
            
            # Open Graph данные
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title:
                meta_info['og_title'] = og_title.get('content', '')
            
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                meta_info['og_description'] = og_desc.get('content', '')
            
            # Формируем результат
            result = f"✅ Метаданные страницы {url}:\n\n"
            for key, value in meta_info.items():
                result += f"📋 {key}: {value}\n"
            
            return result if meta_info else f"❌ Метаданные не найдены на {url}"
            
        except Exception as e:
            return f"❌ Ошибка получения метаданных с {url}: {str(e)}"
    
    def clear_cache(self):
        """Очищает кэш страниц"""
        self._page_cache.clear()
        return "✅ Кэш страниц очищен"