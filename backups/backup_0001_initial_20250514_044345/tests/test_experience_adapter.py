"""
Тесты для модуля адаптации к предыдущему опыту.

Проверяет функциональность ExperienceAdapter.
"""

import os
import json
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import asyncio

from app.agent.experience_adapter import (
    ExperienceAdapter, SimilarExperience, AdaptationSuggestion
)
from app.agent.personalization_manager import PersonalizationManager
from app.agent.error_manager import ErrorManager
from app.agent.experience_manager import ExperienceArchive
from app.config.reasoning_config import ReasoningStrategy


class TestExperienceAdapter(unittest.TestCase):
    """Тесты для ExperienceAdapter"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()

        # Создаем моки для зависимостей
        self.personalization_manager = MagicMock(spec=PersonalizationManager)
        self.error_manager = MagicMock(spec=ErrorManager)
        self.experience_archive = MagicMock(spec=ExperienceArchive)
        self.metacognitive_analyzer = MagicMock()

        # Настраиваем моки
        self.personalization_manager.get_active_profile.return_value = MagicMock()
        self.personalization_manager.analyze_task.return_value = {
            "personalized": True,
            "recommended_approach": "thorough_analysis",
            "detail_level": "high",
            "domains": ["web_development"]
        }

        # Создаем адаптер опыта
        self.adapter = ExperienceAdapter(
            personalization_manager=self.personalization_manager,
            error_manager=self.error_manager,
            experience_archive=self.experience_archive,
            metacognitive_analyzer=self.metacognitive_analyzer
        )

        # Подготавливаем некоторые тестовые данные
        self.adapter._pattern_cache = {
            "error_patterns": [
                {
                    "error_pattern": "Файл не найден",
                    "suggested_solution": "Проверяйте существование файла перед чтением",
                    "confidence": 0.8,
                    "occurrence_count": 5,
                    "context": "чтение файла конфигурации",
                    "triggers": ["чтение", "файл", "открыть"]
                },
                {
                    "error_pattern": "Таймаут соединения",
                    "suggested_solution": "Используйте параметр timeout и обработку исключений",
                    "confidence": 0.7,
                    "occurrence_count": 3,
                    "context": "запрос к API данных",
                    "triggers": ["api", "запрос", "http"]
                }
            ]
        }

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)

    def test_invalidate_cache(self):
        """Тестирует инвалидацию кэша паттернов"""
        # Заполняем кэш
        self.adapter._pattern_cache = {"test": "data"}
        old_timestamp = datetime.now() - timedelta(hours=1)
        self.adapter._cache_timestamp = old_timestamp

        # Инвалидируем кэш
        self.adapter.invalidate_cache()

        # Проверяем результаты
        self.assertEqual({}, self.adapter._pattern_cache)
        self.assertNotEqual(old_timestamp, self.adapter._cache_timestamp)

    def test_get_error_patterns_for_task(self):
        """Тестирует получение паттернов ошибок для задачи"""
        # Вызываем метод
        task = "Чтение файла config.json и обновление настроек"
        patterns = self.adapter._get_error_patterns_for_task(task)

        # Проверяем результаты
        self.assertEqual(1, len(patterns))
        self.assertEqual("Файл не найден", patterns[0]["error_pattern"])

    def test_get_personalized_approach(self):
        """Тестирует получение персонализированного подхода"""
        # Вызываем метод
        task = "Разработать веб-интерфейс для управления настройками"
        approach = self.adapter._get_personalized_approach(task)

        # Проверяем результаты
        self.assertIsNotNone(approach)
        self.assertIn("suggestion", approach)
        self.assertIn("тщательный анализ", approach["suggestion"])
        self.assertIn("учитывая специфику веб-разработка", approach["suggestion"])

    def test_get_generic_error_prevention_tips(self):
        """Тестирует получение общих советов по предотвращению ошибок"""
        # Вызываем метод для задачи с файлами
        task1 = "Открыть файл данных и прочитать его содержимое"
        tips1 = self.adapter._get_generic_error_prevention_tips(task1)

        # Проверяем результаты
        self.assertEqual(1, len(tips1))
        self.assertEqual("Ошибка доступа к файлу", tips1[0]["error_type"])

        # Вызываем метод для задачи с API
        task2 = "Выполнить запрос к REST API для получения данных"
        tips2 = self.adapter._get_generic_error_prevention_tips(task2)

        # Проверяем результаты
        self.assertEqual(1, len(tips2))
        self.assertEqual("Ошибка API", tips2[0]["error_type"])

    def test_is_significantly_better(self):
        """Тестирует определение значительно лучшего решения"""
        # Проверяем, что более длинное решение с другими словами считается лучше
        initial = "Открыть файл и прочитать его"
        improved = "Проверить существование файла, открыть его в режиме чтения, обработать возможные исключения, прочитать содержимое и закрыть файл"
        self.assertTrue(self.adapter._is_significantly_better(improved, initial))

        # Проверяем, что похожее решение не считается значительно лучше
        similar = "Открыть файл, прочитать содержимое и закрыть его"
        self.assertFalse(self.adapter._is_significantly_better(similar, initial))

    def test_merge_solutions(self):
        """Тестирует объединение решений"""
        initial = "Решение 1"
        improved = "Улучшенное решение"
        result = self.adapter._merge_solutions(initial, improved)
        self.assertEqual(improved, result)

    @patch("app.agent.experience_adapter.ExperienceAdapter._find_similar_experiences")
    async def test_analyze_current_task(self, mock_find_similar):
        """Тестирует анализ текущей задачи"""
        # Настраиваем мок
        similar_experience = SimilarExperience(
            similarity_score=0.8,
            task="Чтение файла config.json",
            approach="Проверить существование файла",
            result="Успешно прочитан",
            timestamp=datetime.now(),
            success=True,
            source_id="test",
            metadata={"strategy": "sequential"}
        )
        mock_find_similar.return_value = [similar_experience]

        # Вызываем метод
        task = "Чтение файла settings.json"
        suggestions = await self.adapter.analyze_current_task(task)

        # Проверяем результаты
        self.assertGreater(len(suggestions), 0)

        # Проверяем предложение стратегии
        strategy_suggestions = [s for s in suggestions if s.suggestion_type == "strategy"]
        self.assertEqual(1, len(strategy_suggestions))
        self.assertIn("последовательная", strategy_suggestions[0].suggestion.lower())

        # Проверяем предложение по предотвращению ошибок
        error_suggestions = [s for s in suggestions if s.suggestion_type == "error_prevention"]
        self.assertGreaterEqual(len(error_suggestions), 0)

    @patch("app.agent.experience_adapter.ExperienceAdapter._find_similar_experiences")
    async def test_adapt_planning_parameters(self, mock_find_similar):
        """Тестирует адаптацию параметров планирования"""
        # Настраиваем мок
        similar_experience = SimilarExperience(
            similarity_score=0.8,
            task="Разработка API для управления данными",
            approach="Последовательное создание эндпоинтов",
            result="Успешно реализовано",
            timestamp=datetime.now(),
            success=True,
            source_id="test",
            metadata={
                "strategy": "sequential",
                "max_depth": 5,
                "detail_level": 0.8,
                "risk_threshold": 0.3
            }
        )
        mock_find_similar.return_value = [similar_experience]

        # Вызываем метод
        task = "Разработка REST API для базы данных"
        params = await self.adapter.adapt_planning_parameters(task)

        # Проверяем результаты
        self.assertTrue(params["adapted"])
        self.assertEqual(ReasoningStrategy.SEQUENTIAL.value, params["strategy"])
        self.assertEqual(5, params["max_depth"])
        self.assertGreaterEqual(params["detail_level"], 0.7)
        self.assertLessEqual(params["risk_threshold"], 0.4)

    @patch("app.agent.experience_adapter.ExperienceAdapter._find_similar_experiences")
    async def test_get_improved_solution(self, mock_find_similar):
        """Тестирует улучшение решения"""
        # Настраиваем мок
        similar_experience = SimilarExperience(
            similarity_score=0.8,
            task="Получение данных из API",
            approach="""
            import requests

            try:
                response = requests.get("https://api.example.com/data", timeout=30)
                response.raise_for_status()
                data = response.json()
                return data
            except requests.RequestException as e:
                print(f"Ошибка при запросе к API: {e}")
                return None
            """,
            result="Успешно получены данные",
            timestamp=datetime.now(),
            success=True,
            source_id="test",
            metadata={}
        )
        mock_find_similar.return_value = [similar_experience]

        # Вызываем метод
        task = "Загрузить данные из API example.com"
        initial_solution = """
        import requests

        response = requests.get("https://api.example.com/data")
        data = response.json()
        return data
        """

        result = await self.adapter.get_improved_solution(task, initial_solution)

        # Проверяем результаты
        self.assertIsNotNone(result)
        self.assertTrue(result["has_improvement"])
        self.assertIn("timeout", result["improved_solution"])
        self.assertIn("try", result["improved_solution"])
        self.assertIn("except", result["improved_solution"])

    @patch("app.agent.experience_adapter.ExperienceAdapter._get_error_patterns_for_task")
    async def test_get_error_prevention_tips(self, mock_get_patterns):
        """Тестирует получение советов по предотвращению ошибок"""
        # Настраиваем мок
        mock_get_patterns.return_value = [
            {
                "error_type": "Ошибка API",
                "error_pattern": "Таймаут соединения",
                "suggested_solution": "Используйте параметр timeout и обработку исключений",
                "confidence": 0.7,
                "occurrence_count": 3,
                "triggers": ["api", "запрос", "http"]
            }
        ]

        # Вызываем метод
        task = "Получение данных из API"
        approach = "Выполнить HTTP запрос к API для получения данных"
        tips = await self.adapter.get_error_prevention_tips(task, approach)

        # Проверяем результаты
        self.assertGreater(len(tips), 0)
        self.assertEqual("Используйте параметр timeout и обработку исключений", tips[0]["prevention_tip"])
        self.assertEqual("Ошибка API", tips[0]["error_type"])


# Запускаем тесты, если файл запущен напрямую
if __name__ == "__main__":
    unittest.main()
