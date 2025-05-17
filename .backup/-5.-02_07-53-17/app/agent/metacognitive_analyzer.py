"""
Модуль метакогнитивного анализа для Reasoning Agent

Предоставляет инструменты для оценки эффективности стратегий планирования
и принятия решений, а также для улучшения качества рассуждений агента.
"""

import asyncio
import time
import json
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

from app.config.reasoning_config import ReasoningStrategy
from app.agent.planning_strategy import TaskComplexity
from app.logger import logger
from app.mcp.sequential_thinking import SequentialThinking


class StrategyEvaluationMetric(str, Enum):
    """Метрики для оценки стратегий планирования"""
    ACCURACY = "accuracy"             # Точность (соответствие плана фактическому выполнению)
    EFFICIENCY = "efficiency"         # Эффективность (отношение результата к затраченным ресурсам)
    ADAPTABILITY = "adaptability"     # Адаптивность (способность подстраиваться под изменения)
    COMPLETENESS = "completeness"     # Полнота (охват всех аспектов задачи)
    ROBUSTNESS = "robustness"         # Устойчивость (к непредвиденным ситуациям)
    CLARITY = "clarity"               # Ясность (понятность плана)
    TIME_EFFICIENCY = "time_efficiency"  # Временная эффективность (скорость планирования)


class AnalysisResult:
    """
    Результат метакогнитивного анализа

    Содержит оценки, рекомендации и метаданные анализа стратегии планирования.
    """

    def __init__(
        self,
        strategy_type: ReasoningStrategy,
        metrics: Dict[StrategyEvaluationMetric, float],
        task_complexity: TaskComplexity,
        execution_time: float,
        success_rate: float,
        recommendations: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует результат анализа

        Args:
            strategy_type: Тип стратегии планирования
            metrics: Словарь метрик и их значений
            task_complexity: Сложность задачи
            execution_time: Время выполнения в секундах
            success_rate: Процент успешности выполнения (0-1)
            recommendations: Список рекомендаций по улучшению
            metadata: Дополнительные метаданные анализа
        """
        self.strategy_type = strategy_type
        self.metrics = metrics
        self.task_complexity = task_complexity
        self.execution_time = execution_time
        self.success_rate = success_rate
        self.recommendations = recommendations
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def get_overall_score(self) -> float:
        """
        Рассчитывает общую оценку стратегии на основе метрик

        Returns:
            Средняя оценка по всем метрикам
        """
        if not self.metrics:
            return 0.0

        return sum(self.metrics.values()) / len(self.metrics)

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует результат анализа в словарь

        Returns:
            Словарь с результатами анализа
        """
        return {
            "strategy_type": self.strategy_type.value,
            "metrics": {k.value: v for k, v in self.metrics.items()},
            "task_complexity": self.task_complexity.value,
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "recommendations": self.recommendations,
            "overall_score": self.get_overall_score(),
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """
        Создает объект результата из словаря

        Args:
            data: Словарь с данными результата

        Returns:
            Объект результата анализа
        """
        # Преобразуем строковые ключи в enum
        metrics = {
            StrategyEvaluationMetric(k): v
            for k, v in data.get("metrics", {}).items()
        }

        return cls(
            strategy_type=ReasoningStrategy(data.get("strategy_type", "adaptive")),
            metrics=metrics,
            task_complexity=TaskComplexity(data.get("task_complexity", "medium")),
            execution_time=data.get("execution_time", 0.0),
            success_rate=data.get("success_rate", 0.0),
            recommendations=data.get("recommendations", []),
            metadata=data.get("metadata", {})
        )


class MetacognitiveAnalyzer:
    """
    Анализатор для метакогнитивной оценки стратегий планирования

    Обеспечивает мониторинг, анализ и улучшение стратегий планирования
    на основе результатов их применения и обратной связи от выполнения планов.
    """

    def __init__(self, sequential_thinking: Optional[SequentialThinking] = None):
        """
        Инициализирует анализатор

        Args:
            sequential_thinking: Модуль последовательного мышления для анализа
        """
        self.sequential_thinking = sequential_thinking
        self.analysis_history: List[AnalysisResult] = []
        self.strategy_performance: Dict[ReasoningStrategy, List[AnalysisResult]] = {
            ReasoningStrategy.SEQUENTIAL: [],
            ReasoningStrategy.TREE: [],
            ReasoningStrategy.ADAPTIVE: []
        }

    async def set_sequential_thinking(self, sequential_thinking: SequentialThinking) -> None:
        """
        Устанавливает модуль последовательного мышления

        Args:
            sequential_thinking: Модуль последовательного мышления
        """
        self.sequential_thinking = sequential_thinking

    async def analyze_strategy_execution(
        self,
        strategy_type: ReasoningStrategy,
        original_plan: Dict[str, Any],
        execution_result: Dict[str, Any],
        task: str,
        task_complexity: TaskComplexity,
        execution_time: float
    ) -> AnalysisResult:
        """
        Анализирует результаты выполнения плана и оценивает стратегию

        Args:
            strategy_type: Тип стратегии планирования
            original_plan: Исходный план
            execution_result: Результат выполнения
            task: Описание задачи
            task_complexity: Сложность задачи
            execution_time: Время выполнения в секундах

        Returns:
            Результат анализа стратегии
        """
        logger.info(f"Analyzing execution of {strategy_type.value} strategy for task: {task[:50]}...")

        if not self.sequential_thinking:
            logger.warning("Sequential Thinking not available for metacognitive analysis")
            return self._create_default_analysis(strategy_type, task_complexity, execution_time)

        # Подготовка данных для анализа
        plan_text = original_plan.get("plan_text", str(original_plan))
        success_rate = execution_result.get("success_rate", 0.0)
        errors = execution_result.get("errors", [])
        completed_steps = execution_result.get("completed_steps", [])

        # Формирование запроса для анализа через Sequential Thinking
        analysis_prompt = (
            f"Проведи метакогнитивный анализ выполнения плана для задачи: '{task}'\n\n"
            f"План:\n{plan_text}\n\n"
            f"Результаты выполнения:\n"
            f"- Успешность: {success_rate * 100:.1f}%\n"
            f"- Выполненные шаги: {len(completed_steps)}\n"
            f"- Ошибки: {len(errors)}\n\n"
            f"Оцени следующие аспекты по шкале от 0 до 1:\n"
            f"1. Точность планирования (ACCURACY)\n"
            f"2. Эффективность (EFFICIENCY)\n"
            f"3. Адаптивность (ADAPTABILITY)\n"
            f"4. Полнота (COMPLETENESS)\n"
            f"5. Устойчивость к ошибкам (ROBUSTNESS)\n"
            f"6. Ясность плана (CLARITY)\n"
            f"7. Временная эффективность (TIME_EFFICIENCY)\n\n"
            f"Также предложи 3-5 конкретных рекомендаций по улучшению стратегии планирования."
        )

        # Выполняем анализ через Sequential Thinking
        analysis_result = await self.sequential_thinking.run_thinking_chain(
            initial_thought=analysis_prompt,
            max_steps=5
        )

        # Извлекаем оценки и рекомендации из результата
        metrics, recommendations = self._extract_metrics_and_recommendations(
            analysis_result[-1]["thought"] if analysis_result else ""
        )

        # Создаем результат анализа
        result = AnalysisResult(
            strategy_type=strategy_type,
            metrics=metrics,
            task_complexity=task_complexity,
            execution_time=execution_time,
            success_rate=success_rate,
            recommendations=recommendations,
            metadata={
                "plan_size": len(str(original_plan)),
                "errors_count": len(errors),
                "completed_steps_count": len(completed_steps),
                "task_length": len(task)
            }
        )

        # Сохраняем результат в историю
        self.analysis_history.append(result)
        self.strategy_performance[strategy_type].append(result)

        logger.info(f"Metacognitive analysis completed with overall score: {result.get_overall_score():.2f}")
        return result

    def _extract_metrics_and_recommendations(
        self,
        analysis_text: str
    ) -> Tuple[Dict[StrategyEvaluationMetric, float], List[str]]:
        """
        Извлекает метрики и рекомендации из текста анализа

        Args:
            analysis_text: Текст анализа

        Returns:
            Кортеж из словаря метрик и списка рекомендаций
        """
        metrics = {}
        recommendations = []

        # Словарь для распознавания метрик в тексте
        metric_keywords = {
            StrategyEvaluationMetric.ACCURACY: ["accuracy", "точность"],
            StrategyEvaluationMetric.EFFICIENCY: ["efficiency", "эффективность"],
            StrategyEvaluationMetric.ADAPTABILITY: ["adaptability", "адаптивность"],
            StrategyEvaluationMetric.COMPLETENESS: ["completeness", "полнота"],
            StrategyEvaluationMetric.ROBUSTNESS: ["robustness", "устойчивость"],
            StrategyEvaluationMetric.CLARITY: ["clarity", "ясность"],
            StrategyEvaluationMetric.TIME_EFFICIENCY: ["time_efficiency", "временная эффективность"]
        }

        # Извлекаем метрики
        for metric, keywords in metric_keywords.items():
            for keyword in keywords:
                if keyword in analysis_text.lower():
                    # Ищем числовое значение рядом с ключевым словом
                    parts = analysis_text.lower().split(keyword)
                    if len(parts) > 1:
                        after_keyword = parts[1]
                        # Ищем число от 0 до 1 с одним десятичным знаком
                        import re
                        matches = re.findall(r"0\.\d+|1\.0|1", after_keyword)
                        if matches:
                            try:
                                value = float(matches[0])
                                metrics[metric] = value
                                break
                            except ValueError:
                                pass

        # Заполняем значения по умолчанию для отсутствующих метрик
        for metric in StrategyEvaluationMetric:
            if metric not in metrics:
                metrics[metric] = 0.5  # Среднее значение по умолчанию

        # Извлекаем рекомендации
        recommendation_section = False
        for line in analysis_text.split("\n"):
            line = line.strip()

            if not line:
                continue

            if "рекомендации" in line.lower() or "recommendations" in line.lower():
                recommendation_section = True
                continue

            if recommendation_section and (line.startswith("-") or line.startswith("•") or
                                         line[0].isdigit() and "." in line[:3]):
                # Очищаем от маркеров списка
                clean_line = line.lstrip("-•0123456789. ")
                if clean_line:
                    recommendations.append(clean_line)

        return metrics, recommendations

    def _create_default_analysis(
        self,
        strategy_type: ReasoningStrategy,
        task_complexity: TaskComplexity,
        execution_time: float
    ) -> AnalysisResult:
        """
        Создает анализ по умолчанию, когда нет достаточных данных

        Args:
            strategy_type: Тип стратегии
            task_complexity: Сложность задачи
            execution_time: Время выполнения

        Returns:
            Результат анализа по умолчанию
        """
        # Устанавливаем все метрики на среднее значение
        metrics = {metric: 0.5 for metric in StrategyEvaluationMetric}

        return AnalysisResult(
            strategy_type=strategy_type,
            metrics=metrics,
            task_complexity=task_complexity,
            execution_time=execution_time,
            success_rate=0.5,  # Среднее значение
            recommendations=[
                "Недостаточно данных для анализа стратегии",
                "Рекомендуется включить Sequential Thinking для полного анализа",
                "Собрать больше данных о выполнении планов"
            ]
        )

    async def recommend_strategy(
        self,
        task: str,
        task_complexity: TaskComplexity
    ) -> Tuple[ReasoningStrategy, float, List[str]]:
        """
        Рекомендует оптимальную стратегию для задачи на основе предыдущего опыта

        Args:
            task: Описание задачи
            task_complexity: Сложность задачи

        Returns:
            Кортеж из рекомендуемой стратегии, уверенности и обоснований
        """
        logger.info(f"Recommending strategy for task: {task[:50]}... (complexity: {task_complexity.value})")

        # Если нет достаточной истории, используем стандартную логику
        if sum(len(history) for history in self.strategy_performance.values()) < 5:
            # Для простых задач - последовательная
            if task_complexity == TaskComplexity.SIMPLE:
                return ReasoningStrategy.SEQUENTIAL, 0.8, ["Простая задача с линейным решением"]

            # Для сложных задач - адаптивная
            elif task_complexity in [TaskComplexity.COMPLEX, TaskComplexity.UNCERTAIN]:
                return ReasoningStrategy.ADAPTIVE, 0.7, ["Сложная задача требует адаптивного подхода"]

            # Для средних задач - древовидная
            else:
                return ReasoningStrategy.TREE, 0.6, ["Задача средней сложности с несколькими ветвлениями"]

        # Фильтруем историю по сложности задачи
        similar_complexity_results = {
            strategy: [
                result for result in history
                if result.task_complexity == task_complexity
            ]
            for strategy, history in self.strategy_performance.items()
        }

        # Если нет результатов для данной сложности, используем все результаты
        if all(len(results) == 0 for results in similar_complexity_results.values()):
            similar_complexity_results = self.strategy_performance

        # Рассчитываем средние оценки для каждой стратегии
        strategy_scores = {}
        for strategy, results in similar_complexity_results.items():
            if not results:
                continue

            # Средняя общая оценка
            avg_score = sum(result.get_overall_score() for result in results) / len(results)
            # Средняя успешность
            avg_success = sum(result.success_rate for result in results) / len(results)
            # Взвешенная оценка
            weighted_score = 0.7 * avg_score + 0.3 * avg_success

            strategy_scores[strategy] = weighted_score

        # Если есть оценки, выбираем лучшую стратегию
        if strategy_scores:
            best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
            confidence = min(0.95, best_strategy[1])  # Ограничиваем максимальную уверенность

            # Готовим обоснования
            justifications = [
                f"Стратегия {best_strategy[0].value} имеет наивысшую оценку: {best_strategy[1]:.2f}",
                f"Основано на анализе {len(similar_complexity_results[best_strategy[0]])} предыдущих задач аналогичной сложности"
            ]

            return best_strategy[0], confidence, justifications

        # Если нет оценок, используем адаптивную стратегию
        return ReasoningStrategy.ADAPTIVE, 0.5, ["Нет достаточных данных для определения оптимальной стратегии"]

    async def analyze_strategy_improvement(
        self,
        strategy_type: ReasoningStrategy,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Анализирует улучшение стратегии с течением времени

        Args:
            strategy_type: Тип стратегии
            time_period_days: Период анализа в днях

        Returns:
            Словарь с данными об улучшении стратегии
        """
        if strategy_type not in self.strategy_performance:
            return {"error": "Стратегия не найдена"}

        history = self.strategy_performance[strategy_type]
        if not history:
            return {"error": "Нет данных для анализа"}

        # Фильтруем по указанному периоду
        now = datetime.now()
        filtered_history = [
            result for result in history
            if (now - datetime.fromisoformat(result.timestamp)).days <= time_period_days
        ]

        if not filtered_history:
            return {"error": f"Нет данных за последние {time_period_days} дней"}

        # Сортируем по времени
        sorted_history = sorted(filtered_history, key=lambda x: x.timestamp)

        # Разбиваем на равные периоды для анализа тренда
        num_periods = min(len(sorted_history), 5)  # До 5 периодов
        period_size = len(sorted_history) // num_periods
        periods = []

        for i in range(num_periods):
            start_idx = i * period_size
            end_idx = start_idx + period_size if i < num_periods - 1 else len(sorted_history)

            period_data = sorted_history[start_idx:end_idx]
            if not period_data:
                continue

            # Рассчитываем средние метрики за период
            avg_metrics = {
                metric: sum(data.metrics.get(metric, 0) for data in period_data) / len(period_data)
                for metric in StrategyEvaluationMetric
            }

            # Средняя успешность
            avg_success = sum(data.success_rate for data in period_data) / len(period_data)

            # Временной период
            start_time = datetime.fromisoformat(period_data[0].timestamp)
            end_time = datetime.fromisoformat(period_data[-1].timestamp)

            periods.append({
                "period": f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
                "metrics": {k.value: v for k, v in avg_metrics.items()},
                "success_rate": avg_success,
                "sample_size": len(period_data)
            })

        # Рассчитываем процент улучшения для каждой метрики
        improvements = {}
        if len(periods) >= 2:
            first_period = periods[0]
            last_period = periods[-1]

            for metric in StrategyEvaluationMetric:
                first_value = first_period["metrics"][metric.value]
                last_value = last_period["metrics"][metric.value]

                if first_value > 0:
                    improvement_pct = ((last_value - first_value) / first_value) * 100
                else:
                    improvement_pct = 0 if last_value == 0 else 100

                improvements[metric.value] = improvement_pct

            # Улучшение по успешности
            if first_period["success_rate"] > 0:
                success_improvement = ((last_period["success_rate"] - first_period["success_rate"]) /
                                     first_period["success_rate"]) * 100
            else:
                success_improvement = 0 if last_period["success_rate"] == 0 else 100

            improvements["success_rate"] = success_improvement

        return {
            "strategy": strategy_type.value,
            "time_period_days": time_period_days,
            "periods": periods,
            "improvements": improvements,
            "total_samples": len(filtered_history)
        }

    def get_common_recommendations(self, strategy_type: ReasoningStrategy, limit: int = 5) -> List[str]:
        """
        Получает наиболее часто встречающиеся рекомендации для стратегии

        Args:
            strategy_type: Тип стратегии
            limit: Максимальное количество рекомендаций

        Returns:
            Список наиболее частых рекомендаций
        """
        if strategy_type not in self.strategy_performance:
            return []

        history = self.strategy_performance[strategy_type]
        if not history:
            return []

        # Собираем все рекомендации
        all_recommendations = []
        for result in history:
            all_recommendations.extend(result.recommendations)

        # Считаем частоту рекомендаций
        from collections import Counter
        recommendation_counter = Counter(all_recommendations)

        # Возвращаем наиболее частые
        return [rec for rec, _ in recommendation_counter.most_common(limit)]

    def save_analysis_history(self, file_path: str) -> bool:
        """
        Сохраняет историю анализа в файл

        Args:
            file_path: Путь к файлу

        Returns:
            True в случае успеха, False при ошибке
        """
        try:
            history_data = {
                "timestamp": datetime.now().isoformat(),
                "analysis_results": [result.to_dict() for result in self.analysis_history]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved metacognitive analysis history to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving metacognitive analysis history: {str(e)}")
            return False

    def load_analysis_history(self, file_path: str) -> bool:
        """
        Загружает историю анализа из файла

        Args:
            file_path: Путь к файлу

        Returns:
            True в случае успеха, False при ошибке
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)

            # Преобразуем данные в объекты
            self.analysis_history = [
                AnalysisResult.from_dict(result_data)
                for result_data in history_data.get("analysis_results", [])
            ]

            # Обновляем производительность стратегий
            self.strategy_performance = {strategy: [] for strategy in ReasoningStrategy}
            for result in self.analysis_history:
                if result.strategy_type in self.strategy_performance:
                    self.strategy_performance[result.strategy_type].append(result)

            logger.info(f"Loaded metacognitive analysis history from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading metacognitive analysis history: {str(e)}")
            return False
