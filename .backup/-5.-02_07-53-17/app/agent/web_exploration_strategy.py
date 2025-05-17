"""
Стратегии исследования веб-ресурсов для GopiAI Reasoning Agent

Реализует стратегии для сбора и анализа информации из веб-ресурсов.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Set
import re
import urllib.parse

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationSource, InformationItem,
    InformationCollection, ExplorationPhase
)
from app.agent.browser_access import BrowserAccess
from app.agent.file_system_access import FileSystemAccess
from app.agent.text_editor_access import TextEditorAccess
from app.agent.thought_tree import ThoughtTree
from app.logger import logger


class WebExplorationStrategy(ExplorationStrategy):
    """
    Стратегия для исследования и сбора информации из веб-ресурсов.

    Включает поиск, навигацию и извлечение информации с веб-страниц.
    """

    def __init__(
        self,
        browser_access: BrowserAccess,
        thought_tree: Optional[ThoughtTree] = None,
        file_system: Optional[FileSystemAccess] = None,
        text_editor: Optional[TextEditorAccess] = None,
        max_pages: int = 5,
        max_depth: int = 2,
        search_timeout: float = 30.0
    ):
        """
        Инициализирует стратегию исследования веб-ресурсов.

        Args:
            browser_access: Модуль доступа к браузеру (обязательный)
            thought_tree: Дерево мыслей для интеграции
            file_system: Модуль доступа к файловой системе
            text_editor: Модуль доступа к текстовому редактору
            max_pages: Максимальное количество страниц для посещения
            max_depth: Максимальная глубина навигации
            search_timeout: Таймаут для поиска (в секундах)
        """
        super().__init__(
            name="web_exploration",
            description="Стратегия для исследования веб-ресурсов",
            browser_access=browser_access,
            thought_tree=thought_tree,
            file_system=file_system,
            text_editor=text_editor
        )

        # Проверяем наличие обязательного компонента
        if not browser_access:
            raise ValueError("WebExplorationStrategy requires browser_access")

        self.max_pages = max_pages
        self.max_depth = max_depth
        self.search_timeout = search_timeout

        # Дополнительные настройки
        self.visited_urls: Set[str] = set()
        self.current_depth = 0
        self.search_engines = ["Google", "DuckDuckGo", "Bing"]
        self.default_search_engine = "Google"

    async def explore(self, query: str, **kwargs) -> InformationCollection:
        """
        Выполняет веб-исследование на основе запроса.

        Args:
            query: Текст запроса для исследования
            **kwargs: Дополнительные параметры
                - search_engine: Поисковая система для использования
                - max_pages: Переопределение максимального количества страниц
                - max_depth: Переопределение максимальной глубины
                - save_screenshots: Флаг для сохранения скриншотов

        Returns:
            Коллекция собранной информации
        """
        start_time = time.time()

        # Обновляем параметры из kwargs, если они заданы
        search_engine = kwargs.get("search_engine", self.default_search_engine)
        max_pages = kwargs.get("max_pages", self.max_pages)
        max_depth = kwargs.get("max_depth", self.max_depth)
        save_screenshots = kwargs.get("save_screenshots", False)

        # Сбрасываем состояние
        self.visited_urls = set()
        self.current_depth = 0

        # Создаем новую коллекцию для результатов
        collection_name = f"web_exploration_{int(time.time())}"
        collection = InformationCollection(name=collection_name)

        # Добавляем информацию о запросе в дерево мыслей
        root_thought_id = self.add_to_thought_tree(
            content=f"Начинаем веб-исследование на основе запроса: '{query}'",
            node_type=f"exploration_{ExplorationPhase.INITIAL_QUERY.value}"
        )

        # Этап 1: Выполняем поиск
        search_thought_id = self.add_to_thought_tree(
            content=f"Поиск информации через поисковую систему {search_engine}",
            node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
            parent_id=root_thought_id
        )

        try:
            # Определяем URL для поиска в зависимости от поисковой системы
            search_url = self._get_search_url(query, search_engine)

            # Выполняем поиск через браузер
            search_result = await self.browser_access.execute_action(
                action="go_to_url",
                url=search_url
            )

            if not search_result.get("success", False):
                error_message = search_result.get("error", "Unknown error")
                logger.error(f"Web search failed: {error_message}")

                # Записываем ошибку в дерево мыслей
                self.add_to_thought_tree(
                    content=f"Ошибка при поиске: {error_message}",
                    node_type="exploration_error",
                    parent_id=search_thought_id
                )

                # Записываем выполнение с ошибкой
                self._record_execution(
                    query=query,
                    result={"items_collected": 0, "error": error_message},
                    execution_time=time.time() - start_time,
                    success=False
                )

                return collection

            # Добавляем URL в посещенные
            self.visited_urls.add(search_url)

            # Делаем скриншот, если нужно
            if save_screenshots:
                await self._take_and_save_screenshot("search_results")

            # Этап 2: Извлекаем результаты поиска (ссылки)
            search_links = await self._extract_search_results(search_engine)

            # Добавляем информацию о найденных ссылках в дерево мыслей
            self.add_to_thought_tree(
                content=f"Найдено {len(search_links)} результатов поиска",
                node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
                parent_id=search_thought_id
            )

            # Этап 3: Посещаем и собираем информацию с найденных страниц
            collection_thought_id = self.add_to_thought_tree(
                content="Начинаем сбор информации с найденных страниц",
                node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                parent_id=root_thought_id
            )

            visited_count = 0
            for link in search_links:
                # Проверяем ограничения
                if visited_count >= max_pages:
                    break

                # Пропускаем уже посещенные URL
                if link in self.visited_urls:
                    continue

                # Делаем информацию о посещении страницы
                page_thought_id = self.add_to_thought_tree(
                    content=f"Посещаем страницу: {link}",
                    node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                    parent_id=collection_thought_id
                )

                # Посещаем страницу
                page_result = await self.browser_access.execute_action(
                    action="go_to_url",
                    url=link
                )

                if not page_result.get("success", False):
                    # Логируем ошибку, но продолжаем с другими ссылками
                    error_message = page_result.get("error", "Unknown error")
                    logger.warning(f"Failed to visit page {link}: {error_message}")

                    self.add_to_thought_tree(
                        content=f"Ошибка при посещении страницы: {error_message}",
                        node_type="exploration_error",
                        parent_id=page_thought_id
                    )

                    continue

                # Добавляем URL в посещенные
                self.visited_urls.add(link)
                visited_count += 1

                # Делаем скриншот, если нужно
                if save_screenshots:
                    await self._take_and_save_screenshot(f"page_{visited_count}")

                # Извлекаем информацию со страницы
                page_content = await self._extract_page_content()
                page_title = await self._extract_page_title()

                # Добавляем информацию в коллекцию
                if page_content:
                    item = InformationItem(
                        content=page_content,
                        source=InformationSource.WEB,
                        source_details={
                            "url": link,
                            "title": page_title,
                            "query": query,
                            "search_engine": search_engine
                        },
                        # Оценки будут обновлены при обработке
                        relevance_score=0.5,
                        confidence_score=0.7,
                        tags=["web_page", search_engine.lower()]
                    )

                    collection.add_item(item)

                    # Добавляем информацию о собранном контенте в дерево мыслей
                    content_summary = page_content[:200] + "..." if len(page_content) > 200 else page_content
                    self.add_to_thought_tree(
                        content=f"Собрана информация с '{page_title}': {content_summary}",
                        node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                        parent_id=page_thought_id
                    )

            # Этап 4: Анализ собранной информации
            analysis_thought_id = self.add_to_thought_tree(
                content=f"Анализ собранной информации ({len(collection.items)} элементов)",
                node_type=f"exploration_{ExplorationPhase.DATA_ANALYSIS.value}",
                parent_id=root_thought_id
            )

            # Выполняем обработку результатов
            processed_results = await self.process_results(collection)

            # Добавляем информацию о результатах в дерево мыслей
            self.add_to_thought_tree(
                content=f"Результаты анализа: найдено {processed_results.get('relevant_items', 0)} релевантных элементов",
                node_type=f"exploration_{ExplorationPhase.INFORMATION_SYNTHESIS.value}",
                parent_id=analysis_thought_id
            )

            # Записываем успешное выполнение
            self._record_execution(
                query=query,
                result=processed_results,
                execution_time=time.time() - start_time,
                success=True
            )

            return collection

        except Exception as e:
            logger.error(f"Error during web exploration: {str(e)}")

            # Записываем ошибку в дерево мыслей
            self.add_to_thought_tree(
                content=f"Ошибка при исследовании: {str(e)}",
                node_type="exploration_error",
                parent_id=root_thought_id
            )

            # Записываем выполнение с ошибкой
            self._record_execution(
                query=query,
                result={"items_collected": len(collection.items), "error": str(e)},
                execution_time=time.time() - start_time,
                success=False
            )

            return collection

    async def process_results(self, collection: InformationCollection, **kwargs) -> Dict[str, Any]:
        """
        Обрабатывает результаты исследования.

        Args:
            collection: Коллекция с собранной информацией
            **kwargs: Дополнительные параметры для обработки
                - min_relevance: Минимальная оценка релевантности для фильтрации
                - min_confidence: Минимальная оценка достоверности для фильтрации

        Returns:
            Словарь с обработанными результатами
        """
        min_relevance = kwargs.get("min_relevance", 0.3)
        min_confidence = kwargs.get("min_confidence", 0.4)

        # Обновляем оценки релевантности и достоверности
        for item in collection.items.values():
            # Оценка релевантности на основе простого анализа
            # В реальном сценарии здесь может быть более сложная логика
            item.update_scores(
                relevance=self._estimate_relevance(item),
                confidence=self._estimate_confidence(item)
            )

        # Фильтруем элементы по оценкам
        relevant_items = collection.filter_by_relevance(min_relevance)
        confident_items = collection.filter_by_confidence(min_confidence)

        # Элементы, которые одновременно релевантны и достоверны
        good_items = [
            item for item in relevant_items
            if item.confidence_score >= min_confidence
        ]

        # Суммаризируем результаты
        summary = collection.get_summary()

        return {
            "items_collected": len(collection.items),
            "relevant_items": len(relevant_items),
            "confident_items": len(confident_items),
            "good_items": len(good_items),
            "sources": summary["sources"],
            "avg_relevance": summary["avg_relevance"],
            "avg_confidence": summary["avg_confidence"]
        }

    def _get_search_url(self, query: str, search_engine: str) -> str:
        """
        Формирует URL для поиска в зависимости от поисковой системы.

        Args:
            query: Текст запроса
            search_engine: Название поисковой системы

        Returns:
            URL для поиска
        """
        # Кодируем запрос для URL
        encoded_query = urllib.parse.quote(query)

        # Определяем URL в зависимости от поисковой системы
        if search_engine.lower() == "google":
            return f"https://www.google.com/search?q={encoded_query}"
        elif search_engine.lower() == "duckduckgo":
            return f"https://duckduckgo.com/?q={encoded_query}"
        elif search_engine.lower() == "bing":
            return f"https://www.bing.com/search?q={encoded_query}"
        else:
            # По умолчанию используем Google
            return f"https://www.google.com/search?q={encoded_query}"

    async def _extract_search_results(self, search_engine: str) -> List[str]:
        """
        Извлекает ссылки из результатов поиска.

        Args:
            search_engine: Название поисковой системы

        Returns:
            Список URL из результатов поиска
        """
        links = []

        try:
            # Извлекаем селектор в зависимости от поисковой системы
            selector = self._get_search_results_selector(search_engine)

            # Получаем элементы поиска
            result_elements = await self.browser_access.execute_action(
                action="get_elements",
                selector=selector
            )

            if not result_elements.get("success", False):
                logger.warning(f"Failed to extract search results: {result_elements.get('error', 'Unknown error')}")
                return links

            elements = result_elements.get("elements", [])

            # Извлекаем ссылки из элементов
            for element in elements:
                href = element.get("attributes", {}).get("href", "")

                # Очищаем и фильтруем URL
                if href and self._is_valid_url(href) and not self._is_search_engine_url(href, search_engine):
                    # Для Google и других поисковых систем часто URL находятся в параметрах
                    href = self._normalize_search_result_url(href, search_engine)

                    if href:
                        links.append(href)

            return links

        except Exception as e:
            logger.error(f"Error extracting search results: {str(e)}")
            return links

    def _get_search_results_selector(self, search_engine: str) -> str:
        """
        Возвращает CSS-селектор для результатов поиска.

        Args:
            search_engine: Название поисковой системы

        Returns:
            CSS-селектор для результатов поиска
        """
        # Селекторы для разных поисковых систем
        if search_engine.lower() == "google":
            return "a[href^='http']:not([href^='https://accounts.google']):not([href^='https://support.google'])"
        elif search_engine.lower() == "duckduckgo":
            return ".result__a"
        elif search_engine.lower() == "bing":
            return ".b_algo h2 a"
        else:
            # По умолчанию используем общий селектор для ссылок
            return "a[href^='http']"

    def _normalize_search_result_url(self, url: str, search_engine: str) -> str:
        """
        Нормализует URL из результатов поиска.

        Args:
            url: URL для нормализации
            search_engine: Название поисковой системы

        Returns:
            Нормализованный URL
        """
        # Обработка для Google
        if search_engine.lower() == "google":
            # Google часто использует URL перенаправления
            if "/url?q=" in url:
                # Извлекаем настоящий URL из параметра q
                match = re.search(r"/url\?q=([^&]+)", url)
                if match:
                    decoded_url = urllib.parse.unquote(match.group(1))
                    return decoded_url

        # Другие поисковые системы или если не нужна специальная обработка
        return url

    def _is_valid_url(self, url: str) -> bool:
        """
        Проверяет, является ли URL допустимым.

        Args:
            url: URL для проверки

        Returns:
            True, если URL допустимый, иначе False
        """
        # Базовая проверка на допустимый URL
        if not url.startswith(("http://", "https://")):
            return False

        # Проверка на исключаемые домены (например, рекламу)
        excluded_domains = [
            "googleadservices.com",
            "doubleclick.net",
            "google.com/aclk",
            "youtube.com/watch"
        ]

        for domain in excluded_domains:
            if domain in url:
                return False

        return True

    def _is_search_engine_url(self, url: str, search_engine: str) -> bool:
        """
        Проверяет, является ли URL внутренним URL поисковой системы.

        Args:
            url: URL для проверки
            search_engine: Название поисковой системы

        Returns:
            True, если URL относится к поисковой системе, иначе False
        """
        if search_engine.lower() == "google":
            return "google.com/search" in url or "google.com/webhp" in url
        elif search_engine.lower() == "duckduckgo":
            return "duckduckgo.com" in url and ("?q=" in url or "/?q=" in url)
        elif search_engine.lower() == "bing":
            return "bing.com/search" in url

        return False

    async def _extract_page_content(self) -> str:
        """
        Извлекает основное содержимое страницы.

        Returns:
            Текст содержимого страницы
        """
        try:
            # Получаем текст страницы
            content_result = await self.browser_access.execute_action(
                action="get_page_text",
                selector="body"
            )

            if not content_result.get("success", False):
                logger.warning(f"Failed to extract page content: {content_result.get('error', 'Unknown error')}")
                return ""

            content = content_result.get("text", "")

            # Очищаем и форматируем текст
            content = self._clean_text(content)

            return content

        except Exception as e:
            logger.error(f"Error extracting page content: {str(e)}")
            return ""

    async def _extract_page_title(self) -> str:
        """
        Извлекает заголовок страницы.

        Returns:
            Заголовок страницы
        """
        try:
            # Получаем заголовок страницы
            title_result = await self.browser_access.execute_action(
                action="get_page_title"
            )

            if not title_result.get("success", False):
                logger.warning(f"Failed to extract page title: {title_result.get('error', 'Unknown error')}")
                return ""

            title = title_result.get("title", "")

            return title

        except Exception as e:
            logger.error(f"Error extracting page title: {str(e)}")
            return ""

    async def _take_and_save_screenshot(self, name_prefix: str) -> bool:
        """
        Делает и сохраняет скриншот текущей страницы.

        Args:
            name_prefix: Префикс имени файла скриншота

        Returns:
            True, если скриншот успешно сохранен, иначе False
        """
        if not self.file_system:
            logger.warning("Cannot save screenshot: file_system not available")
            return False

        try:
            # Делаем скриншот
            screenshot_result = await self.browser_access.execute_action(
                action="take_screenshot",
                full_page=True
            )

            if not screenshot_result.get("success", False):
                logger.warning(f"Failed to take screenshot: {screenshot_result.get('error', 'Unknown error')}")
                return False

            # Получаем данные скриншота
            screenshot_data = screenshot_result.get("data", "")
            if not screenshot_data:
                logger.warning("Screenshot data is empty")
                return False

            # Формируем имя файла
            timestamp = int(time.time())
            file_name = f"{name_prefix}_{timestamp}.png"

            # Создаем директорию для скриншотов, если нужно
            screenshots_dir = "exploration_screenshots"
            await self.file_system.create_directory(screenshots_dir)

            # Путь к файлу скриншота
            file_path = f"{screenshots_dir}/{file_name}"

            # Сохраняем скриншот
            save_result = await self.file_system.write_file_content(
                file_path=file_path,
                content=screenshot_data,
                mode="binary"
            )

            if not save_result.get("success", False):
                logger.warning(f"Failed to save screenshot: {save_result.get('error', 'Unknown error')}")
                return False

            logger.info(f"Screenshot saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error taking and saving screenshot: {str(e)}")
            return False

    def _clean_text(self, text: str) -> str:
        """
        Очищает и форматирует текст.

        Args:
            text: Текст для очистки

        Returns:
            Очищенный текст
        """
        # Удаляем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)

        # Удаляем непечатаемые символы
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)

        # Удаляем JavaScript-код
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)

        # Удаляем CSS
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)

        # Удаляем HTML-теги
        text = re.sub(r'<[^>]+>', ' ', text)

        # Заменяем HTML-сущности
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        # Обрезаем пробелы по краям
        text = text.strip()

        return text

    def _estimate_relevance(self, item: InformationItem) -> float:
        """
        Оценивает релевантность элемента информации.

        Args:
            item: Элемент для оценки

        Returns:
            Оценка релевантности (0.0 - 1.0)
        """
        # В реальном сценарии здесь может быть более сложная логика
        # с использованием NLP, векторных представлений и т.д.

        # Базовая оценка
        score = 0.5

        # Длина контента (предполагаем, что более длинный контент более информативен)
        content_length = len(item.content)
        if content_length > 1000:
            score += 0.2
        elif content_length < 100:
            score -= 0.1

        # Если это страница с ошибкой или пустая страница
        if "404" in item.content or "not found" in item.content.lower() or content_length < 50:
            score -= 0.3

        # Ограничиваем значение от 0.0 до 1.0
        return max(0.0, min(1.0, score))

    def _estimate_confidence(self, item: InformationItem) -> float:
        """
        Оценивает достоверность элемента информации.

        Args:
            item: Элемент для оценки

        Returns:
            Оценка достоверности (0.0 - 1.0)
        """
        # В реальном сценарии здесь может быть более сложная логика
        # с анализом источника, авторитетности домена и т.д.

        # Базовая оценка
        score = 0.6

        # Анализ источника
        url = item.source_details.get("url", "")

        # Высокая достоверность для некоторых доменов
        high_confidence_domains = [
            "wikipedia.org", "github.com", "stackoverflow.com",
            "docs.python.org", "microsoft.com", "google.com"
        ]

        for domain in high_confidence_domains:
            if domain in url:
                score += 0.2
                break

        # Низкая достоверность для некоторых доменов
        low_confidence_domains = [
            "forum.", "blog.", ".wordpress.", ".blogspot.",
            "answers.yahoo", "quora.com"
        ]

        for domain in low_confidence_domains:
            if domain in url:
                score -= 0.1
                break

        # Ограничиваем значение от 0.0 до 1.0
        return max(0.0, min(1.0, score))
