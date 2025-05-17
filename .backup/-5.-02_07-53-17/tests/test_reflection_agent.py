"""
Тесты для модуля агента размышлений
"""

import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.agent.reflection_agent import (
    ReflectionAgent, ReflectionMode, ReflectionResult
)


class TestReflectionResult(unittest.TestCase):
    """Тесты для класса результатов рефлексии"""

    def test_reflection_result_creation(self):
        """Тест создания объекта результата рефлексии"""
        result = ReflectionResult(
            mode=ReflectionMode.CONTRADICTION,
            original_content="Test content",
            reflection_summary="Test summary",
            issues_found=[{"type": "contradiction", "description": "Test issue"}],
            recommendations=["Test recommendation"],
            confidence_score=0.8
        )

        self.assertEqual(result.mode, ReflectionMode.CONTRADICTION)
        self.assertEqual(result.original_content, "Test content")
        self.assertEqual(result.reflection_summary, "Test summary")
        self.assertEqual(len(result.issues_found), 1)
        self.assertEqual(result.issues_found[0]["description"], "Test issue")
        self.assertEqual(len(result.recommendations), 1)
        self.assertEqual(result.recommendations[0], "Test recommendation")
        self.assertEqual(result.confidence_score, 0.8)

    def test_reflection_result_to_dict(self):
        """Тест преобразования результата в словарь"""
        result = ReflectionResult(
            mode=ReflectionMode.ASSUMPTION,
            original_content="Test content",
            reflection_summary="Test summary",
            issues_found=[{"type": "assumption", "description": "Test assumption"}],
            recommendations=["Test recommendation"],
            confidence_score=0.7,
            metadata={"test_key": "test_value"}
        )

        result_dict = result.to_dict()

        self.assertEqual(result_dict["mode"], "assumption")
        self.assertEqual(result_dict["original_content"], "Test content")
        self.assertEqual(result_dict["reflection_summary"], "Test summary")
        self.assertEqual(len(result_dict["issues_found"]), 1)
        self.assertEqual(result_dict["issues_found"][0]["type"], "assumption")
        self.assertEqual(len(result_dict["recommendations"]), 1)
        self.assertEqual(result_dict["confidence_score"], 0.7)
        self.assertEqual(result_dict["metadata"]["test_key"], "test_value")
        self.assertTrue("timestamp" in result_dict)

    def test_reflection_result_from_dict(self):
        """Тест создания результата из словаря"""
        data = {
            "mode": "verification",
            "original_content": "Test content",
            "reflection_summary": "Test summary",
            "issues_found": [{"type": "verification", "description": "Test verification issue"}],
            "recommendations": ["Test recommendation"],
            "confidence_score": 0.6,
            "metadata": {"test_key": "test_value"},
            "timestamp": datetime.now().isoformat()
        }

        result = ReflectionResult.from_dict(data)

        self.assertEqual(result.mode, ReflectionMode.VERIFICATION)
        self.assertEqual(result.original_content, "Test content")
        self.assertEqual(result.reflection_summary, "Test summary")
        self.assertEqual(len(result.issues_found), 1)
        self.assertEqual(result.issues_found[0]["type"], "verification")
        self.assertEqual(len(result.recommendations), 1)
        self.assertEqual(result.confidence_score, 0.6)
        self.assertEqual(result.metadata["test_key"], "test_value")


class TestReflectionAgent(unittest.TestCase):
    """Тесты для агента размышлений"""

    def setUp(self):
        """Настройка окружения для тестов"""
        # Создаем мок для ThoughtTree
        self.mock_thought_tree = MagicMock()
        self.mock_thought_tree.root = MagicMock()
        self.mock_thought_tree.add_thought = MagicMock(return_value="test_node_id")

        # Создаем мок для SequentialThinking
        self.mock_sequential_thinking = MagicMock()
        self.mock_sequential_thinking.run_thinking_chain = MagicMock(
            return_value=asyncio.Future()
        )
        self.mock_sequential_thinking.run_thinking_chain.return_value.set_result([
            {"thought": "Initial thought"},
            {"thought": "Intermediate thought"},
            {"thought": "Final thought with some contradictions discovered.\n\n"
                        "Contradictions:\n"
                        "- The statement A contradicts with statement B\n\n"
                        "Recommendations:\n"
                        "- Revise statement A\n"
                        "- Clarify statement B\n\n"
                        "Confidence score: 0.7"}
        ])

        # Патчим базовый класс ReasoningAgent
        self.reasoning_agent_patcher = patch('app.agent.reflection_agent.ReasoningAgent')
        self.mock_reasoning_agent = self.reasoning_agent_patcher.start()

    def tearDown(self):
        """Очистка окружения после тестов"""
        self.reasoning_agent_patcher.stop()

    @patch('app.agent.reflection_agent.logger')
    async def test_initialization(self, mock_logger):
        """Тест инициализации агента размышлений"""
        # Создаем агента
        agent = ReflectionAgent()
        agent.thought_tree = self.mock_thought_tree

        # Инициализируем агента
        await agent.initialize()

        # Проверяем, что был создан узел для ветки рефлексий
        self.mock_thought_tree.add_thought.assert_called_once()
        self.assertTrue(hasattr(agent, 'reflection_branch_id'))
        self.assertEqual(agent.reflection_branch_id, "test_node_id")
        mock_logger.info.assert_called_with("Reflection agent initialization completed")

    @patch('app.agent.reflection_agent.logger')
    async def test_reflect_on_content(self, mock_logger):
        """Тест функции рефлексивного анализа содержимого"""
        # Создаем агента
        agent = ReflectionAgent()
        agent.thought_tree = self.mock_thought_tree
        agent.reflection_branch_id = "test_branch_id"
        agent.sequential_thinking = self.mock_sequential_thinking

        # Мокаем приватные методы
        agent._process_reflection_results = MagicMock(
            return_value=asyncio.Future()
        )
        agent._process_reflection_results.return_value.set_result(
            ReflectionResult(
                mode=ReflectionMode.CONTRADICTION,
                original_content="Test content",
                reflection_summary="Test summary",
                issues_found=[{"type": "contradiction", "description": "Test issue"}],
                recommendations=["Test recommendation"],
                confidence_score=0.7
            )
        )

        agent._add_reflection_to_thought_tree = MagicMock(
            return_value=asyncio.Future()
        )
        agent._add_reflection_to_thought_tree.return_value.set_result("test_node_id")

        # Вызываем метод рефлексии
        result = await agent.reflect_on_content(
            content="Test content",
            mode=ReflectionMode.CONTRADICTION
        )

        # Проверяем результаты
        self.mock_sequential_thinking.run_thinking_chain.assert_called_once()
        agent._process_reflection_results.assert_called_once()
        agent._add_reflection_to_thought_tree.assert_called_once()

        self.assertEqual(result.mode, ReflectionMode.CONTRADICTION)
        self.assertEqual(result.confidence_score, 0.7)
        self.assertEqual(len(agent.reflection_history), 1)

    @patch('app.agent.reflection_agent.logger')
    async def test_analyze_reasoning_strategy(self, mock_logger):
        """Тест анализа стратегии рассуждения"""
        # Создаем агента
        agent = ReflectionAgent()
        agent.thought_tree = self.mock_thought_tree
        agent.reflection_branch_id = "test_branch_id"
        agent.sequential_thinking = self.mock_sequential_thinking

        # Мокаем метод рефлексии
        agent.reflect_on_content = MagicMock(
            return_value=asyncio.Future()
        )
        agent.reflect_on_content.return_value.set_result(
            ReflectionResult(
                mode=ReflectionMode.COMPREHENSIVE,
                original_content="Test strategy content",
                reflection_summary="Strategy analysis summary",
                issues_found=[{"type": "assumption", "description": "Strategy assumption issue"}],
                recommendations=["Strategy recommendation"],
                confidence_score=0.8
            )
        )

        # Мокаем методы получения стратегии
        agent._get_strategy_description = MagicMock(return_value="Test strategy description")
        agent._get_strategy_by_name = MagicMock(return_value=None)

        # Вызываем метод анализа стратегии
        result = await agent.analyze_reasoning_strategy(
            strategy_name="test_strategy"
        )

        # Проверяем результаты
        agent._get_strategy_description.assert_called_once_with("test_strategy")
        agent.reflect_on_content.assert_called_once()

        self.assertEqual(result.mode, ReflectionMode.COMPREHENSIVE)
        self.assertEqual(result.confidence_score, 0.8)
        self.assertEqual(result.reflection_summary, "Strategy analysis summary")

    @patch('app.agent.reflection_agent.logger')
    @patch('app.agent.reflection_agent.os')
    @patch('app.agent.reflection_agent.json')
    async def test_save_reflection_history(self, mock_json, mock_os, mock_logger):
        """Тест сохранения истории рефлексий"""
        # Создаем агента
        agent = ReflectionAgent()
        agent.name = "test_agent"

        # Добавляем тестовые записи в историю
        agent.reflection_history = [
            ReflectionResult(
                mode=ReflectionMode.CONTRADICTION,
                original_content="Test content 1",
                reflection_summary="Test summary 1",
                issues_found=[{"type": "contradiction", "description": "Test issue 1"}],
                recommendations=["Test recommendation 1"],
                confidence_score=0.7
            ),
            ReflectionResult(
                mode=ReflectionMode.ASSUMPTION,
                original_content="Test content 2",
                reflection_summary="Test summary 2",
                issues_found=[{"type": "assumption", "description": "Test issue 2"}],
                recommendations=["Test recommendation 2"],
                confidence_score=0.8
            )
        ]

        # Настраиваем моки
        mock_os.path.join = MagicMock(return_value="logs/test_file.json")
        mock_os.makedirs = MagicMock()
        mock_file = MagicMock()
        mock_open = MagicMock(return_value=mock_file)

        # Патчим встроенную функцию open
        with patch('builtins.open', mock_open):
            # Вызываем метод сохранения истории
            file_path = await agent.save_reflection_history(filename="test_file.json")

        # Проверяем результаты
        mock_os.makedirs.assert_called_once_with("logs", exist_ok=True)
        mock_open.assert_called_once_with("logs/test_file.json", 'w', encoding='utf-8')
        mock_json.dump.assert_called_once()
        self.assertEqual(file_path, "logs/test_file.json")
        mock_logger.info.assert_called_with("Reflection history saved to logs/test_file.json")

    def test_extract_issues_and_recommendations(self):
        """Тест извлечения проблем и рекомендаций из текста"""
        # Создаем агента
        agent = ReflectionAgent()

        # Тестовый текст с проблемами и рекомендациями
        test_text = """
        # Анализ противоречий

        В тексте обнаружены следующие противоречия:
        - Утверждение A противоречит утверждению B
        - Метод X несовместим с подходом Y

        # Рекомендации

        Предлагаются следующие рекомендации:
        - Пересмотреть утверждение A
        - Уточнить метод X

        # Оценка достоверности

        Общая оценка достоверности: 0.7
        """

        # Вызываем метод извлечения
        issues, recommendations, confidence_score = agent._extract_issues_and_recommendations(
            test_text, ReflectionMode.CONTRADICTION
        )

        # Проверяем результаты
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]["type"], "contradiction")
        self.assertEqual(issues[0]["description"], "Утверждение A противоречит утверждению B")

        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0], "Пересмотреть утверждение A")

        self.assertEqual(confidence_score, 0.7)


if __name__ == '__main__':
    unittest.main()
