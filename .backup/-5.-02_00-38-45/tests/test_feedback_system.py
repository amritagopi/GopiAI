"""
Тесты для системы обратной связи

Проверка функциональности системы обратной связи для улучшения стратегий.
"""

import unittest
import asyncio
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

from app.agent.feedback_system import (
    FeedbackItem, FeedbackType, FeedbackSource,
    FeedbackStorage, FeedbackAnalyzer, FeedbackManager
)
from app.agent.exploration_strategy import (
    InformationCollection, InformationItem, InformationSource
)
from app.agent.exploration_feedback_integration import (
    FeedbackEnabledExplorationStrategy,
    FeedbackEnabledWebExplorationStrategy,
    FeedbackEnabledFileExplorationStrategy
)


class TestFeedbackItem(unittest.TestCase):
    """Тесты для класса FeedbackItem"""

    def test_create_item(self):
        """Тест создания элемента обратной связи"""
        item = FeedbackItem(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.7,
            source=FeedbackSource.USER,
            description="Test feedback",
            exploration_id="test_exploration"
        )

        self.assertEqual(item.strategy_id, "test_strategy")
        self.assertEqual(item.feedback_type, FeedbackType.RELEVANCE)
        self.assertEqual(item.score, 0.7)
        self.assertEqual(item.source, FeedbackSource.USER)
        self.assertEqual(item.description, "Test feedback")
        self.assertEqual(item.exploration_id, "test_exploration")

    def test_to_dict_and_from_dict(self):
        """Тест сериализации и десериализации элемента обратной связи"""
        original_item = FeedbackItem(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.ACCURACY,
            score=0.8,
            source=FeedbackSource.AUTOMATIC,
            description="Test automatic feedback",
            exploration_id="test_exploration",
            metadata={"key": "value"}
        )

        # Сериализуем в словарь
        item_dict = original_item.to_dict()

        # Десериализуем обратно
        restored_item = FeedbackItem.from_dict(item_dict)

        # Проверяем, что данные сохранились
        self.assertEqual(restored_item.strategy_id, original_item.strategy_id)
        self.assertEqual(restored_item.feedback_type, original_item.feedback_type)
        self.assertEqual(restored_item.score, original_item.score)
        self.assertEqual(restored_item.source, original_item.source)
        self.assertEqual(restored_item.description, original_item.description)
        self.assertEqual(restored_item.exploration_id, original_item.exploration_id)
        self.assertEqual(restored_item.metadata, original_item.metadata)


class TestFeedbackStorage(unittest.TestCase):
    """Тесты для класса FeedbackStorage"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FeedbackStorage(feedback_dir=self.temp_dir)

        # Создаем несколько тестовых элементов
        self.relevance_item = FeedbackItem(
            strategy_id="strategy1",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.7,
            source=FeedbackSource.USER,
            description="Relevance feedback"
        )

        self.efficiency_item = FeedbackItem(
            strategy_id="strategy1",
            feedback_type=FeedbackType.EFFICIENCY,
            score=0.5,
            source=FeedbackSource.AUTOMATIC,
            description="Efficiency feedback"
        )

        self.accuracy_item = FeedbackItem(
            strategy_id="strategy2",
            feedback_type=FeedbackType.ACCURACY,
            score=0.8,
            source=FeedbackSource.SYSTEM,
            description="Accuracy feedback"
        )

        # Добавляем элементы в хранилище
        self.relevance_id = self.storage.add_feedback(self.relevance_item)
        self.efficiency_id = self.storage.add_feedback(self.efficiency_item)
        self.accuracy_id = self.storage.add_feedback(self.accuracy_item)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.temp_dir)

    def test_add_and_get_feedback(self):
        """Тест добавления и получения элемента обратной связи"""
        item = self.storage.get_feedback(self.relevance_id)

        self.assertEqual(item.strategy_id, "strategy1")
        self.assertEqual(item.feedback_type, FeedbackType.RELEVANCE)
        self.assertEqual(item.score, 0.7)

    def test_get_all_by_strategy(self):
        """Тест получения всех элементов для стратегии"""
        items = self.storage.get_all_by_strategy("strategy1")

        self.assertEqual(len(items), 2)
        self.assertTrue(any(item.feedback_type == FeedbackType.RELEVANCE for item in items))
        self.assertTrue(any(item.feedback_type == FeedbackType.EFFICIENCY for item in items))

    def test_get_by_type(self):
        """Тест получения элементов по типу"""
        items = self.storage.get_by_type(FeedbackType.RELEVANCE)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].feedback_type, FeedbackType.RELEVANCE)

    def test_get_by_source(self):
        """Тест получения элементов по источнику"""
        items = self.storage.get_by_source(FeedbackSource.AUTOMATIC)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, FeedbackSource.AUTOMATIC)

    def test_get_average_score(self):
        """Тест получения средней оценки"""
        # Средняя оценка для стратегии
        avg_score = self.storage.get_average_score(strategy_id="strategy1")
        expected_avg = (0.7 + 0.5) / 2
        self.assertAlmostEqual(avg_score, expected_avg)

        # Средняя оценка для типа
        avg_score = self.storage.get_average_score(feedback_type=FeedbackType.RELEVANCE)
        self.assertEqual(avg_score, 0.7)

        # Средняя оценка для стратегии и типа
        avg_score = self.storage.get_average_score(
            strategy_id="strategy1",
            feedback_type=FeedbackType.EFFICIENCY
        )
        self.assertEqual(avg_score, 0.5)

    def test_save_and_load(self):
        """Тест сохранения и загрузки данных"""
        # Сохраняем данные
        result = self.storage.save()
        self.assertTrue(result)

        # Создаем новое хранилище и загружаем данные
        new_storage = FeedbackStorage(feedback_dir=self.temp_dir)
        result = new_storage.load()
        self.assertTrue(result)

        # Проверяем, что данные загружены корректно
        self.assertEqual(len(new_storage.feedback_items), 3)

        # Проверяем конкретный элемент
        item = new_storage.get_feedback(self.relevance_id)
        self.assertIsNotNone(item)
        self.assertEqual(item.strategy_id, "strategy1")
        self.assertEqual(item.feedback_type, FeedbackType.RELEVANCE)


class TestFeedbackAnalyzer(unittest.TestCase):
    """Тесты для класса FeedbackAnalyzer"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FeedbackStorage(feedback_dir=self.temp_dir)
        self.analyzer = FeedbackAnalyzer(storage=self.storage)

        # Создаем тестовые данные
        self._create_test_data()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.temp_dir)

    def _create_test_data(self):
        """Создание тестовых данных"""
        # Стратегия с хорошими показателями
        self.storage.add_feedback(FeedbackItem(
            strategy_id="good_strategy",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.9,
            source=FeedbackSource.USER,
            description="Очень релевантные результаты"
        ))
        self.storage.add_feedback(FeedbackItem(
            strategy_id="good_strategy",
            feedback_type=FeedbackType.EFFICIENCY,
            score=0.8,
            source=FeedbackSource.AUTOMATIC,
            description="Эффективное выполнение"
        ))
        self.storage.add_feedback(FeedbackItem(
            strategy_id="good_strategy",
            feedback_type=FeedbackType.COMPLETENESS,
            score=0.7,
            source=FeedbackSource.SYSTEM,
            description="Хорошая полнота"
        ))

        # Стратегия с плохими показателями
        self.storage.add_feedback(FeedbackItem(
            strategy_id="bad_strategy",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.3,
            source=FeedbackSource.USER,
            description="Слабая релевантность результатов"
        ))
        self.storage.add_feedback(FeedbackItem(
            strategy_id="bad_strategy",
            feedback_type=FeedbackType.EFFICIENCY,
            score=0.2,
            source=FeedbackSource.AUTOMATIC,
            description="Очень медленное выполнение"
        ))
        self.storage.add_feedback(FeedbackItem(
            strategy_id="bad_strategy",
            feedback_type=FeedbackType.COMPLETENESS,
            score=0.4,
            source=FeedbackSource.SYSTEM,
            description="Неполные результаты"
        ))

    def test_get_strategy_performance(self):
        """Тест анализа производительности стратегии"""
        # Проверяем стратегию с хорошими показателями
        perf = self.analyzer.get_strategy_performance("good_strategy")

        self.assertEqual(perf["strategy_id"], "good_strategy")
        self.assertAlmostEqual(perf["overall_score"], 0.8)  # (0.9 + 0.8 + 0.7) / 3
        self.assertEqual(perf["feedback_count"], 3)
        self.assertEqual(len(perf["metrics"]), len(FeedbackType))
        self.assertEqual(perf["metrics"][FeedbackType.RELEVANCE.value], 0.9)
        self.assertEqual(perf["metrics"][FeedbackType.EFFICIENCY.value], 0.8)
        self.assertEqual(perf["metrics"][FeedbackType.COMPLETENESS.value], 0.7)

        # Проверяем стратегию с плохими показателями
        perf = self.analyzer.get_strategy_performance("bad_strategy")

        self.assertEqual(perf["strategy_id"], "bad_strategy")
        self.assertAlmostEqual(perf["overall_score"], 0.3)  # (0.3 + 0.2 + 0.4) / 3
        self.assertEqual(perf["feedback_count"], 3)

    def test_get_improvement_recommendations(self):
        """Тест получения рекомендаций по улучшению"""
        # Проверяем рекомендации для стратегии с плохими показателями
        recs = self.analyzer.get_improvement_recommendations("bad_strategy")

        self.assertTrue(len(recs) > 0)

        # Проверяем, что рекомендации содержат проблемные области
        problem_areas = [rec["area"] for rec in recs]
        self.assertIn(FeedbackType.RELEVANCE.value, problem_areas)
        self.assertIn(FeedbackType.EFFICIENCY.value, problem_areas)

        # Проверяем рекомендации для стратегии с хорошими показателями
        recs = self.analyzer.get_improvement_recommendations("good_strategy")

        for rec in recs:
            # Проверяем, что рекомендации для хорошей стратегии имеют низкий приоритет
            self.assertEqual(rec["priority"], "low")


class TestFeedbackManager(unittest.TestCase):
    """Тесты для класса FeedbackManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.manager = FeedbackManager(feedback_dir=self.temp_dir)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.temp_dir)

    def test_add_user_feedback(self):
        """Тест добавления обратной связи от пользователя"""
        # Добавляем обратную связь
        feedback_id = self.manager.add_user_feedback(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.7,
            description="Пользовательский отзыв"
        )

        # Проверяем, что обратная связь добавлена
        all_feedback = self.manager.get_all_feedback()
        self.assertEqual(len(all_feedback), 1)
        self.assertEqual(all_feedback[0]["id"], feedback_id)
        self.assertEqual(all_feedback[0]["source"], FeedbackSource.USER.value)

    def test_add_automatic_feedback(self):
        """Тест генерации автоматической обратной связи"""
        # Создаем тестовую коллекцию информации
        collection = InformationCollection(name="test_collection")

        # Добавляем элементы в коллекцию
        item1 = InformationItem(
            content="Test content 1",
            source=InformationSource.WEB,
            relevance_score=0.8,
            confidence_score=0.7
        )
        item2 = InformationItem(
            content="Test content 2",
            source=InformationSource.FILES,
            relevance_score=0.6,
            confidence_score=0.9
        )

        collection.add_item(item1)
        collection.add_item(item2)

        # Генерируем автоматическую обратную связь
        feedback_ids = self.manager.add_automatic_feedback(
            strategy_id="test_strategy",
            collection=collection,
            execution_time=1.5,
            query="test query"
        )

        # Проверяем, что все типы обратной связи созданы
        self.assertIn("efficiency", feedback_ids)
        self.assertIn("relevance", feedback_ids)
        self.assertIn("accuracy", feedback_ids)
        self.assertIn("completeness", feedback_ids)

        # Проверяем, что обратная связь добавлена в хранилище
        all_feedback = self.manager.get_all_feedback()
        self.assertEqual(len(all_feedback), 4)  # Четыре типа обратной связи

    def test_get_strategy_performance(self):
        """Тест получения информации о производительности стратегии"""
        # Добавляем обратную связь
        self.manager.add_user_feedback(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.RELEVANCE,
            score=0.7,
            description="Хорошая релевантность"
        )
        self.manager.add_user_feedback(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.EFFICIENCY,
            score=0.5,
            description="Средняя эффективность"
        )

        # Получаем производительность
        performance = self.manager.get_strategy_performance("test_strategy")

        self.assertEqual(performance["strategy_id"], "test_strategy")
        self.assertEqual(performance["feedback_count"], 2)
        self.assertAlmostEqual(performance["overall_score"], 0.6)  # (0.7 + 0.5) / 2

    def test_get_improvement_recommendations(self):
        """Тест получения рекомендаций по улучшению"""
        # Добавляем обратную связь с низкими оценками
        self.manager.add_user_feedback(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.EFFICIENCY,
            score=0.3,
            description="Очень медленная работа"
        )
        self.manager.add_user_feedback(
            strategy_id="test_strategy",
            feedback_type=FeedbackType.COMPLETENESS,
            score=0.4,
            description="Неполные результаты"
        )

        # Получаем рекомендации
        recommendations = self.manager.get_improvement_recommendations("test_strategy")

        self.assertTrue(len(recommendations) > 0)

        # Проверяем, что рекомендации содержат проблемные области
        problem_areas = [rec["area"] for rec in recommendations]
        self.assertIn(FeedbackType.EFFICIENCY.value, problem_areas)
        self.assertIn(FeedbackType.COMPLETENESS.value, problem_areas)


class TestFeedbackEnabledStrategy(unittest.TestCase):
    """Тесты для стратегий исследования с поддержкой обратной связи"""

    @patch("app.agent.exploration_feedback_integration.FeedbackManager")
    def test_explore_with_feedback(self, mock_feedback_manager):
        """Тест исследования с обратной связью"""
        # Создаем мок-стратегию
        strategy = MagicMock(spec=FeedbackEnabledExplorationStrategy)
        strategy.name = "test_strategy"
        strategy.last_query = ""
        strategy.last_execution_time = 0.0
        strategy.adaptive_parameters = {}

        # Настройка поведения функции explore
        collection = InformationCollection(name="test_result")
        strategy.explore = asyncio.coroutine(lambda query, **kwargs: collection)

        # Включаем метод explore_with_feedback
        result = asyncio.run(FeedbackEnabledExplorationStrategy.explore_with_feedback(
            strategy, "test query"
        ))

        # Проверяем, что метод explore был вызван
        strategy.explore.assert_called_once()

        # Проверяем, что добавлена автоматическая обратная связь
        mock_feedback_manager.return_value.add_automatic_feedback.assert_called_once()

        # Проверяем результат
        self.assertEqual(result, collection)

    @patch("app.agent.exploration_feedback_integration.FeedbackManager")
    def test_get_adaptive_parameters(self, mock_feedback_manager):
        """Тест получения адаптивных параметров"""
        # Создаем мок-объект FeedbackManager
        mock_manager = MagicMock()
        mock_feedback_manager.return_value = mock_manager

        # Настраиваем поведение get_strategy_performance
        mock_manager.get_strategy_performance.return_value = {
            "metrics": {
                FeedbackType.RELEVANCE.value: 0.3,  # Низкая релевантность
                FeedbackType.EFFICIENCY.value: 0.8   # Хорошая эффективность
            }
        }

        # Создаем мок-стратегию web-исследования
        web_strategy = MagicMock(spec=FeedbackEnabledWebExplorationStrategy)
        web_strategy.name = "web_exploration"
        web_strategy.adaptive_parameters = {}
        web_strategy.max_pages = 5
        web_strategy.default_search_engine = "Google"
        web_strategy.feedback_manager = mock_manager

        # Получаем адаптивные параметры
        params = FeedbackEnabledWebExplorationStrategy.get_adaptive_parameters(
            web_strategy, "test query"
        )

        # Проверяем, что изменена поисковая система из-за низкой релевантности
        self.assertIn("search_engine", params)
        self.assertEqual(params["search_engine"], "DuckDuckGo")

        # Создаем мок-стратегию файлового исследования
        file_strategy = MagicMock(spec=FeedbackEnabledFileExplorationStrategy)
        file_strategy.name = "file_exploration"
        file_strategy.adaptive_parameters = {}
        file_strategy.max_files = 10
        file_strategy.default_extensions = [".txt", ".py"]
        file_strategy.feedback_manager = mock_manager

        # Получаем адаптивные параметры
        params = FeedbackEnabledFileExplorationStrategy.get_adaptive_parameters(
            file_strategy, "test query"
        )

        # Проверяем, что добавлен шаблон для поиска из-за низкой релевантности
        self.assertIn("pattern", params)


if __name__ == "__main__":
    unittest.main()
