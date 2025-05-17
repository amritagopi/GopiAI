"""
Тесты для стратегий исследования

Проверка функциональности различных стратегий исследования для сбора информации.
"""

import unittest
import asyncio
import os
import time
from unittest.mock import MagicMock, patch

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationSource, InformationItem, InformationCollection
)
from app.agent.web_exploration_strategy import WebExplorationStrategy
from app.agent.file_exploration_strategy import FileExplorationStrategy
from app.agent.thought_tree import ThoughtTree
from app.agent.reasoning import ReasoningAgent
from app.agent.file_system_access import FileSystemAccess
from app.agent.browser_access import BrowserAccess


class TestInformationItem(unittest.TestCase):
    """Тесты для проверки класса InformationItem"""

    def test_create_item(self):
        """Тест создания элемента информации"""
        item = InformationItem(
            content="Тестовый контент",
            source=InformationSource.WEB,
            source_details={"url": "https://example.com"},
            relevance_score=0.7,
            confidence_score=0.8,
            tags=["test", "example"]
        )

        self.assertEqual(item.content, "Тестовый контент")
        self.assertEqual(item.source, InformationSource.WEB)
        self.assertEqual(item.source_details, {"url": "https://example.com"})
        self.assertEqual(item.relevance_score, 0.7)
        self.assertEqual(item.confidence_score, 0.8)
        self.assertEqual(item.tags, ["test", "example"])

    def test_update_scores(self):
        """Тест обновления оценок релевантности и достоверности"""
        item = InformationItem(
            content="Тестовый контент",
            source=InformationSource.WEB,
            relevance_score=0.5,
            confidence_score=0.5
        )

        # Обновляем оценки
        item.update_scores(relevance=0.8, confidence=0.9)

        self.assertEqual(item.relevance_score, 0.8)
        self.assertEqual(item.confidence_score, 0.9)

    def test_add_tags(self):
        """Тест добавления тегов"""
        item = InformationItem(
            content="Тестовый контент",
            source=InformationSource.WEB,
            tags=["initial"]
        )

        # Добавляем теги
        item.add_tags(["new", "tags"])

        self.assertEqual(item.tags, ["initial", "new", "tags"])

        # Проверяем, что дубликаты не добавляются
        item.add_tags(["new", "another"])

        self.assertEqual(item.tags, ["initial", "new", "tags", "another"])

    def test_to_dict_and_from_dict(self):
        """Тест сериализации и десериализации"""
        original_item = InformationItem(
            content="Тестовый контент",
            source=InformationSource.WEB,
            source_details={"url": "https://example.com"},
            relevance_score=0.7,
            confidence_score=0.8,
            tags=["test", "example"]
        )

        # Сериализуем в словарь
        item_dict = original_item.to_dict()

        # Десериализуем обратно
        restored_item = InformationItem.from_dict(item_dict)

        # Проверяем, что данные сохранились
        self.assertEqual(restored_item.content, original_item.content)
        self.assertEqual(restored_item.source, original_item.source)
        self.assertEqual(restored_item.source_details, original_item.source_details)
        self.assertEqual(restored_item.relevance_score, original_item.relevance_score)
        self.assertEqual(restored_item.confidence_score, original_item.confidence_score)
        self.assertEqual(restored_item.tags, original_item.tags)


class TestInformationCollection(unittest.TestCase):
    """Тесты для проверки класса InformationCollection"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.collection = InformationCollection(name="test_collection")

        # Создаем несколько тестовых элементов
        self.web_item = InformationItem(
            content="Web content",
            source=InformationSource.WEB,
            source_details={"url": "https://example.com"},
            relevance_score=0.7,
            confidence_score=0.6,
            tags=["web", "example"]
        )

        self.file_item = InformationItem(
            content="File content",
            source=InformationSource.FILES,
            source_details={"file_path": "test.txt", "extension": ".txt"},
            relevance_score=0.5,
            confidence_score=0.8,
            tags=["file", "txt"]
        )

        # Добавляем элементы в коллекцию
        self.web_item_id = self.collection.add_item(self.web_item)
        self.file_item_id = self.collection.add_item(self.file_item)

    def test_add_and_get_item(self):
        """Тест добавления и получения элемента"""
        item = self.collection.get_item(self.web_item_id)

        self.assertEqual(item.content, "Web content")
        self.assertEqual(item.source, InformationSource.WEB)

    def test_remove_item(self):
        """Тест удаления элемента"""
        # Удаляем элемент
        result = self.collection.remove_item(self.web_item_id)

        self.assertTrue(result)
        self.assertIsNone(self.collection.get_item(self.web_item_id))
        self.assertEqual(len(self.collection.items), 1)

        # Пробуем удалить несуществующий элемент
        result = self.collection.remove_item("non_existent_id")

        self.assertFalse(result)

    def test_filter_by_source(self):
        """Тест фильтрации по источнику"""
        web_items = self.collection.filter_by_source(InformationSource.WEB)
        file_items = self.collection.filter_by_source(InformationSource.FILES)

        self.assertEqual(len(web_items), 1)
        self.assertEqual(len(file_items), 1)
        self.assertEqual(web_items[0].content, "Web content")
        self.assertEqual(file_items[0].content, "File content")

    def test_filter_by_tags(self):
        """Тест фильтрации по тегам"""
        # Фильтрация с require_all=False (any tag match)
        items = self.collection.filter_by_tags(["web", "txt"], require_all=False)
        self.assertEqual(len(items), 2)  # Оба элемента должны быть найдены

        # Фильтрация с require_all=True (all tags must match)
        items = self.collection.filter_by_tags(["web", "example"], require_all=True)
        self.assertEqual(len(items), 1)  # Только web_item должен быть найден
        self.assertEqual(items[0].source, InformationSource.WEB)

    def test_filter_by_relevance_and_confidence(self):
        """Тест фильтрации по релевантности и достоверности"""
        # Фильтрация по релевантности
        items = self.collection.filter_by_relevance(min_score=0.6)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, InformationSource.WEB)

        # Фильтрация по достоверности
        items = self.collection.filter_by_confidence(min_score=0.7)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, InformationSource.FILES)

    def test_get_summary(self):
        """Тест получения сводной информации"""
        summary = self.collection.get_summary()

        self.assertEqual(summary["total_items"], 2)
        self.assertEqual(summary["sources"], {
            InformationSource.WEB.value: 1,
            InformationSource.FILES.value: 1
        })
        self.assertEqual(summary["avg_relevance"], 0.6)  # (0.7 + 0.5) / 2
        self.assertEqual(summary["avg_confidence"], 0.7)  # (0.6 + 0.8) / 2

    def test_to_dict_and_from_dict(self):
        """Тест сериализации и десериализации коллекции"""
        # Сериализуем в словарь
        collection_dict = self.collection.to_dict()

        # Десериализуем обратно
        restored_collection = InformationCollection.from_dict(collection_dict)

        # Проверяем, что данные сохранились
        self.assertEqual(restored_collection.name, self.collection.name)
        self.assertEqual(len(restored_collection.items), len(self.collection.items))

        # Проверяем элементы
        for item_id, original_item in self.collection.items.items():
            restored_item = restored_collection.items[item_id]
            self.assertEqual(restored_item.content, original_item.content)
            self.assertEqual(restored_item.source.value, original_item.source.value)


class TestFileExplorationStrategy(unittest.TestCase):
    """Тесты для проверки стратегии исследования файловой системы"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок-объекты для зависимостей
        self.file_system = MagicMock(spec=FileSystemAccess)
        self.thought_tree = MagicMock(spec=ThoughtTree)

        # Настраиваем стратегию исследования
        self.strategy = FileExplorationStrategy(
            file_system=self.file_system,
            thought_tree=self.thought_tree,
            max_files=5,
            default_extensions=[".txt", ".md", ".py"]
        )

    @patch("app.agent.file_exploration_strategy.logger")
    async def test_explore_basic(self, mock_logger):
        """Тест базового исследования файловой системы"""
        # Настраиваем поведение мок-объектов
        self.file_system.list_directory_contents.return_value = {
            "success": True,
            "items": [
                {"name": "test.txt", "type": "file"},
                {"name": "folder", "type": "directory"}
            ]
        }

        self.file_system.get_file_information.return_value = {
            "success": True,
            "size": 100
        }

        self.file_system.read_file_content.return_value = {
            "success": True,
            "content": "Test content"
        }

        # Запускаем исследование
        collection = await self.strategy.explore("test query")

        # Проверяем результаты
        self.assertIsInstance(collection, InformationCollection)
        self.assertEqual(len(collection.items), 1)  # Должен быть один файл

        # Проверяем, что методы были вызваны
        self.file_system.list_directory_contents.assert_called_once()
        self.file_system.get_file_information.assert_called_once()
        self.file_system.read_file_content.assert_called_once()

        # Проверяем, что дерево мыслей использовалось
        self.thought_tree.add_thought.assert_called()

    @patch("app.agent.file_exploration_strategy.logger")
    async def test_process_results(self, mock_logger):
        """Тест обработки результатов исследования"""
        # Создаем тестовую коллекцию
        collection = InformationCollection(name="test_collection")

        # Добавляем тестовые элементы
        item1 = InformationItem(
            content="Test content 1",
            source=InformationSource.FILES,
            source_details={"file_path": "test1.txt", "extension": ".txt"},
            relevance_score=0.6,
            confidence_score=0.7,
            tags=["file", "txt"]
        )

        item2 = InformationItem(
            content="Test content 2",
            source=InformationSource.FILES,
            source_details={"file_path": "test2.py", "extension": ".py"},
            relevance_score=0.5,
            confidence_score=0.8,
            tags=["file", "py"]
        )

        collection.add_item(item1)
        collection.add_item(item2)

        # Патчим методы оценки
        with patch.object(self.strategy, '_estimate_relevance', return_value=0.7), \
             patch.object(self.strategy, '_estimate_confidence', return_value=0.8):

            # Обрабатываем результаты
            results = await self.strategy.process_results(collection, min_relevance=0.3, min_confidence=0.4)

            # Проверяем результаты
            self.assertEqual(results["items_collected"], 2)
            self.assertEqual(results["relevant_items"], 2)
            self.assertEqual(results["confident_items"], 2)
            self.assertEqual(results["good_items"], 2)
            self.assertTrue("extensions" in results)
            self.assertEqual(results["extensions"], {"txt": 1, "py": 1})


class TestWebExplorationStrategy(unittest.TestCase):
    """Тесты для проверки стратегии исследования веб-ресурсов"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок-объекты для зависимостей
        self.browser_access = MagicMock(spec=BrowserAccess)
        self.file_system = MagicMock(spec=FileSystemAccess)
        self.thought_tree = MagicMock(spec=ThoughtTree)

        # Настраиваем стратегию исследования
        self.strategy = WebExplorationStrategy(
            browser_access=self.browser_access,
            file_system=self.file_system,
            thought_tree=self.thought_tree,
            max_pages=3
        )

    @patch("app.agent.web_exploration_strategy.logger")
    async def test_explore_basic(self, mock_logger):
        """Тест базового исследования веб-ресурсов"""
        # Настраиваем поведение мок-объектов
        self.browser_access.execute_action.side_effect = [
            # Для go_to_url
            {"success": True},
            # Для get_elements
            {"success": True, "elements": [
                {"attributes": {"href": "https://example.com/page1"}},
                {"attributes": {"href": "https://example.com/page2"}}
            ]},
            # Для go_to_url первой страницы
            {"success": True},
            # Для get_page_text первой страницы
            {"success": True, "text": "Page 1 content"},
            # Для get_page_title первой страницы
            {"success": True, "title": "Page 1"},
            # Для go_to_url второй страницы
            {"success": True},
            # Для get_page_text второй страницы
            {"success": True, "text": "Page 2 content"},
            # Для get_page_title второй страницы
            {"success": True, "title": "Page 2"}
        ]

        # Запускаем исследование
        collection = await self.strategy.explore("test query")

        # Проверяем результаты
        self.assertIsInstance(collection, InformationCollection)
        self.assertEqual(len(collection.items), 2)  # Должны быть две страницы

        # Проверяем, что методы были вызваны
        self.assertEqual(self.browser_access.execute_action.call_count, 8)

        # Проверяем, что дерево мыслей использовалось
        self.thought_tree.add_thought.assert_called()

    @patch("app.agent.web_exploration_strategy.logger")
    async def test_process_results(self, mock_logger):
        """Тест обработки результатов исследования"""
        # Создаем тестовую коллекцию
        collection = InformationCollection(name="test_collection")

        # Добавляем тестовые элементы
        item1 = InformationItem(
            content="Page content with relevant information",
            source=InformationSource.WEB,
            source_details={"url": "https://example.com/page1", "title": "Page 1"},
            relevance_score=0.6,
            confidence_score=0.7,
            tags=["web", "example"]
        )

        item2 = InformationItem(
            content="404 not found",
            source=InformationSource.WEB,
            source_details={"url": "https://example.com/page2", "title": "Error"},
            relevance_score=0.2,
            confidence_score=0.5,
            tags=["web", "error"]
        )

        collection.add_item(item1)
        collection.add_item(item2)

        # Патчим методы оценки
        with patch.object(self.strategy, '_estimate_relevance', side_effect=[0.8, 0.2]), \
             patch.object(self.strategy, '_estimate_confidence', side_effect=[0.7, 0.3]):

            # Обрабатываем результаты
            results = await self.strategy.process_results(collection, min_relevance=0.5, min_confidence=0.4)

            # Проверяем результаты
            self.assertEqual(results["items_collected"], 2)
            self.assertEqual(results["relevant_items"], 1)  # Только первый элемент релевантный
            self.assertEqual(results["confident_items"], 1)  # Только первый элемент достоверный
            self.assertEqual(results["good_items"], 1)      # Только первый элемент хороший


class TestReasoningAgentExploration(unittest.TestCase):
    """Тесты для проверки методов исследования в ReasoningAgent"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем мок-объект агента
        self.agent = MagicMock(spec=ReasoningAgent)

        # Настраиваем стратегии исследования
        self.web_strategy = MagicMock(spec=WebExplorationStrategy)
        self.file_strategy = MagicMock(spec=FileExplorationStrategy)

        # Связываем мок-объекты с агентом
        self.agent.web_exploration = self.web_strategy
        self.agent.file_exploration = self.file_strategy
        self.agent.exploration_strategies = {
            "web": self.web_strategy,
            "file": self.file_strategy
        }

        # Настраиваем методы из ReasoningAgent
        self.agent.explore_web.side_effect = self._mock_explore_web
        self.agent.explore_files.side_effect = self._mock_explore_files
        self.agent.get_combined_exploration.side_effect = self._mock_get_combined_exploration

        # Мок для менеджера разрешений
        self.permission_manager = MagicMock()
        self.agent.permission_manager = self.permission_manager

    async def _mock_explore_web(self, query, **kwargs):
        """Мок для метода explore_web"""
        # Настраиваем поведение мок-объекта для разрешений
        permission_request = MagicMock()
        permission_request.approved = True
        self.permission_manager.request_permission.return_value = permission_request

        # Настраиваем результаты исследования
        mock_collection = MagicMock(spec=InformationCollection)
        mock_collection.items = {"item1": MagicMock(), "item2": MagicMock()}

        self.web_strategy.explore.return_value = mock_collection
        self.web_strategy.process_results.return_value = {"relevant_items": 2}

        return {
            "success": True,
            "collection": mock_collection,
            "results": {"relevant_items": 2},
            "items_count": len(mock_collection.items),
            "query": query
        }

    async def _mock_explore_files(self, query, **kwargs):
        """Мок для метода explore_files"""
        # Настраиваем поведение мок-объекта для разрешений
        permission_request = MagicMock()
        permission_request.approved = True
        self.permission_manager.request_permission.return_value = permission_request

        # Настраиваем результаты исследования
        mock_collection = MagicMock(spec=InformationCollection)
        mock_collection.items = {"item1": MagicMock()}

        self.file_strategy.explore.return_value = mock_collection
        self.file_strategy.process_results.return_value = {"relevant_items": 1}

        return {
            "success": True,
            "collection": mock_collection,
            "results": {"relevant_items": 1},
            "items_count": len(mock_collection.items),
            "query": query
        }

    async def _mock_get_combined_exploration(self, query, **kwargs):
        """Мок для метода get_combined_exploration"""
        # Сначала вызываем индивидуальные методы
        web_result = await self._mock_explore_web(query)
        file_result = await self._mock_explore_files(query)

        # Комбинируем результаты
        combined_collection = MagicMock(spec=InformationCollection)
        combined_collection.items = {**web_result["collection"].items, **file_result["collection"].items}

        return {
            "success": True,
            "query": query,
            "strategies_executed": ["web", "file"],
            "items_collected": len(combined_collection.items),
            "collection": combined_collection,
            "results_by_strategy": {
                "web": web_result,
                "file": file_result
            }
        }

    @patch("app.agent.reasoning.logger")
    async def test_explore_web(self, mock_logger):
        """Тест метода explore_web"""
        result = await self.agent.explore_web("python tutorial")

        self.assertTrue(result["success"])
        self.assertEqual(result["items_count"], 2)
        self.assertEqual(result["results"]["relevant_items"], 2)

        # Проверяем, что методы были вызваны
        self.permission_manager.request_permission.assert_called_once()
        self.web_strategy.explore.assert_called_once()
        self.web_strategy.process_results.assert_called_once()

    @patch("app.agent.reasoning.logger")
    async def test_explore_files(self, mock_logger):
        """Тест метода explore_files"""
        result = await self.agent.explore_files("python code")

        self.assertTrue(result["success"])
        self.assertEqual(result["items_count"], 1)
        self.assertEqual(result["results"]["relevant_items"], 1)

        # Проверяем, что методы были вызваны
        self.permission_manager.request_permission.assert_called_once()
        self.file_strategy.explore.assert_called_once()
        self.file_strategy.process_results.assert_called_once()

    @patch("app.agent.reasoning.logger")
    async def test_get_combined_exploration(self, mock_logger):
        """Тест метода get_combined_exploration"""
        result = await self.agent.get_combined_exploration("python programming")

        self.assertTrue(result["success"])
        self.assertEqual(result["items_collected"], 3)  # 2 от web + 1 от file
        self.assertEqual(len(result["strategies_executed"]), 2)
        self.assertTrue("web" in result["strategies_executed"])
        self.assertTrue("file" in result["strategies_executed"])

        # Проверяем результаты по стратегиям
        self.assertTrue(result["results_by_strategy"]["web"]["success"])
        self.assertTrue(result["results_by_strategy"]["file"]["success"])


# Функция для запуска асинхронных тестов
def run_async_test(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


if __name__ == "__main__":
    # Патчим тесты, чтобы работать с асинхронными методами
    TestFileExplorationStrategy.test_explore_basic = lambda self: run_async_test(self.test_explore_basic())
    TestFileExplorationStrategy.test_process_results = lambda self: run_async_test(self.test_process_results())

    TestWebExplorationStrategy.test_explore_basic = lambda self: run_async_test(self.test_explore_basic())
    TestWebExplorationStrategy.test_process_results = lambda self: run_async_test(self.test_process_results())

    TestReasoningAgentExploration.test_explore_web = lambda self: run_async_test(self.test_explore_web())
    TestReasoningAgentExploration.test_explore_files = lambda self: run_async_test(self.test_explore_files())
    TestReasoningAgentExploration.test_get_combined_exploration = lambda self: run_async_test(self.test_get_combined_exploration())

    unittest.main()
