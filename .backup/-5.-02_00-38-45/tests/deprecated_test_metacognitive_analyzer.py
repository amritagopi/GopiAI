"""
Тесты для модуля метакогнитивного анализа
"""

import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch

from app.agent.metacognitive_analyzer import (
    MetacognitiveAnalyzer,
    AnalysisResult,
    StrategyEvaluationMetric
)
from app.config.reasoning_config import ReasoningStrategy
from app.agent.planning_strategy import TaskComplexity


@pytest.fixture
def mock_sequential_thinking():
    """Фикстура для мока Sequential Thinking"""
    mock = AsyncMock()

    # Настраиваем мок для метода run_thinking_chain
    async def run_thinking_chain(initial_thought, max_steps):
        # Возвращаем заглушку для результата запуска цепочки мыслей
        return [
            {"thought": "Первый шаг анализа..."},
            {"thought": "Второй шаг анализа..."},
            {"thought": """
Проведем анализ выполнения плана:

1. Точность планирования (ACCURACY): 0.8
   Планирование было достаточно точным, большинство шагов соответствовали фактически необходимым действиям.

2. Эффективность (EFFICIENCY): 0.7
   Эффективность использования ресурсов была хорошей, но не оптимальной.

3. Адаптивность (ADAPTABILITY): 0.6
   Стратегия показала среднюю способность адаптироваться к изменениям.

4. Полнота (COMPLETENESS): 0.9
   План был очень полным и охватывал практически все аспекты задачи.

5. Устойчивость к ошибкам (ROBUSTNESS): 0.5
   Средняя устойчивость к непредвиденным ситуациям.

6. Ясность плана (CLARITY): 0.8
   План был четким и понятным.

7. Временная эффективность (TIME_EFFICIENCY): 0.7
   Временные затраты на планирование были разумными.

Рекомендации по улучшению:
1. Улучшить механизмы адаптации к изменениям во время выполнения
2. Усилить проверку устойчивости к ошибкам
3. Добавить резервные планы для критических точек
4. Оптимизировать распределение ресурсов для повышения эффективности
5. Улучшить мониторинг выполнения плана
            """}
        ]

    # Настраиваем мок для метода think
    async def think(thought, next_thought_needed):
        return {"thought": "Анализ показывает, что сложность задачи средняя (medium)"}

    mock.run_thinking_chain = run_thinking_chain
    mock.think = think

    return mock


@pytest.fixture
def analyzer(mock_sequential_thinking):
    """Фикстура для создания анализатора"""
    analyzer = MetacognitiveAnalyzer(mock_sequential_thinking)
    return analyzer


class TestMetacognitiveAnalyzer:
    """Тесты для метакогнитивного анализатора"""

    async def test_analyze_strategy_execution(self, analyzer):
        """Тестирует анализ выполнения стратегии"""
        # Подготовка данных для теста
        strategy_type = ReasoningStrategy.ADAPTIVE
        original_plan = {
            "plan_text": "План выполнения задачи:\n1. Первый шаг\n2. Второй шаг\n3. Третий шаг",
            "task_complexity": "medium"
        }
        execution_result = {
            "success_rate": 0.8,
            "completed_steps": ["шаг 1", "шаг 2", "шаг 3"],
            "errors": ["небольшая ошибка в шаге 2"]
        }
        task = "Тестовая задача для проверки анализатора"
        task_complexity = TaskComplexity.MEDIUM
        execution_time = 5.5

        # Выполнение анализа
        result = await analyzer.analyze_strategy_execution(
            strategy_type=strategy_type,
            original_plan=original_plan,
            execution_result=execution_result,
            task=task,
            task_complexity=task_complexity,
            execution_time=execution_time
        )

        # Проверки результата
        assert isinstance(result, AnalysisResult)
        assert result.strategy_type == strategy_type
        assert result.task_complexity == task_complexity
        assert result.execution_time == execution_time
        assert result.success_rate == execution_result["success_rate"]
        assert len(result.recommendations) > 0
        assert len(result.metrics) > 0

        # Проверка метрик
        assert StrategyEvaluationMetric.ACCURACY in result.metrics
        assert StrategyEvaluationMetric.EFFICIENCY in result.metrics
        assert StrategyEvaluationMetric.COMPLETENESS in result.metrics

        # Проверка общей оценки
        overall_score = result.get_overall_score()
        assert 0 <= overall_score <= 1

    async def test_recommend_strategy(self, analyzer):
        """Тестирует рекомендацию стратегии для задачи"""
        task = "Сложная задача с множеством взаимозависимых шагов"
        task_complexity = TaskComplexity.COMPLEX

        # Вызов метода
        strategy, confidence, justifications = await analyzer.recommend_strategy(
            task=task,
            task_complexity=task_complexity
        )

        # Проверки результата
        assert isinstance(strategy, ReasoningStrategy)
        assert 0 <= confidence <= 1
        assert isinstance(justifications, list)
        assert len(justifications) > 0

    def test_extract_metrics_and_recommendations(self, analyzer):
        """Тестирует извлечение метрик и рекомендаций из текста анализа"""
        analysis_text = """
        Анализ стратегии:

        Точность (Accuracy): 0.8
        Эффективность (Efficiency): 0.7
        Адаптивность (Adaptability): 0.6
        Полнота (Completeness): 0.9

        Рекомендации:
        1. Улучшить механизмы адаптации
        2. Добавить дополнительные проверки
        - Оптимизировать ресурсы
        """

        # Вызов метода
        metrics, recommendations = analyzer._extract_metrics_and_recommendations(analysis_text)

        # Проверки результата
        assert len(metrics) > 0
        assert len(recommendations) > 0
        assert StrategyEvaluationMetric.ACCURACY in metrics
        assert metrics[StrategyEvaluationMetric.ACCURACY] == 0.8
        assert "Улучшить механизмы адаптации" in recommendations

    async def test_analysis_result_serialization(self, analyzer):
        """Тестирует сериализацию и десериализацию результатов анализа"""
        # Создаем тестовый результат анализа
        metrics = {
            StrategyEvaluationMetric.ACCURACY: 0.8,
            StrategyEvaluationMetric.EFFICIENCY: 0.7,
            StrategyEvaluationMetric.ADAPTABILITY: 0.6
        }
        recommendations = [
            "Рекомендация 1",
            "Рекомендация 2"
        ]
        result = AnalysisResult(
            strategy_type=ReasoningStrategy.ADAPTIVE,
            metrics=metrics,
            task_complexity=TaskComplexity.MEDIUM,
            execution_time=5.5,
            success_rate=0.8,
            recommendations=recommendations
        )

        # Сериализуем в словарь
        result_dict = result.to_dict()

        # Проверяем ключи словаря
        assert "strategy_type" in result_dict
        assert "metrics" in result_dict
        assert "task_complexity" in result_dict
        assert "execution_time" in result_dict
        assert "success_rate" in result_dict
        assert "recommendations" in result_dict
        assert "overall_score" in result_dict

        # Десериализуем обратно
        deserialized_result = AnalysisResult.from_dict(result_dict)

        # Проверяем, что десериализованный объект эквивалентен исходному
        assert deserialized_result.strategy_type == result.strategy_type
        assert deserialized_result.task_complexity == result.task_complexity
        assert deserialized_result.execution_time == result.execution_time
        assert deserialized_result.success_rate == result.success_rate
        assert set(deserialized_result.recommendations) == set(result.recommendations)
        assert len(deserialized_result.metrics) == len(result.metrics)

    @pytest.mark.asyncio
    async def test_save_and_load_history(self, analyzer, tmp_path):
        """Тестирует сохранение и загрузку истории анализа"""
        # Создаем тестовый путь к файлу
        file_path = tmp_path / "test_history.json"

        # Добавляем тестовые данные в историю анализатора
        strategy_type = ReasoningStrategy.ADAPTIVE
        metrics = {m: 0.7 for m in StrategyEvaluationMetric}
        recommendations = ["Тестовая рекомендация"]

        result = AnalysisResult(
            strategy_type=strategy_type,
            metrics=metrics,
            task_complexity=TaskComplexity.MEDIUM,
            execution_time=5.0,
            success_rate=0.8,
            recommendations=recommendations
        )

        # Добавляем в историю
        analyzer.analysis_history.append(result)
        analyzer.strategy_performance[strategy_type].append(result)

        # Сохраняем историю
        save_success = analyzer.save_analysis_history(str(file_path))
        assert save_success
        assert os.path.exists(file_path)

        # Очищаем историю
        analyzer.analysis_history = []
        analyzer.strategy_performance = {s: [] for s in ReasoningStrategy}

        # Загружаем историю
        load_success = analyzer.load_analysis_history(str(file_path))
        assert load_success
        assert len(analyzer.analysis_history) == 1
        assert len(analyzer.strategy_performance[strategy_type]) == 1

        # Проверяем загруженные данные
        loaded_result = analyzer.analysis_history[0]
        assert loaded_result.strategy_type == strategy_type
        assert loaded_result.task_complexity == TaskComplexity.MEDIUM
        assert loaded_result.execution_time == 5.0
        assert loaded_result.success_rate == 0.8
        assert loaded_result.recommendations == recommendations
