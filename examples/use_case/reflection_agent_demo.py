"""
Демонстрационный скрипт для тестирования агента размышлений (Reflection Agent)

Этот скрипт демонстрирует использование ReflectionAgent для анализа текста
и стратегий рассуждения.
"""

import asyncio
import json
import os
from typing import Dict, Any

from app.agent.reflection_agent import ReflectionAgent, ReflectionMode
from app.agent.planning_strategy import (
    SequentialStrategy, DecompositionStrategy, AnalogicalStrategy
)


async def reflection_demo():
    """
    Демонстрирует основные возможности агента размышлений
    """
    print("\n===== Демонстрация агента размышлений (Reflection Agent) =====\n")

    # Инициализируем агента
    agent = ReflectionAgent()
    await agent.initialize()

    print("Агент размышлений инициализирован.\n")

    # Пример текста для анализа
    sample_text = """
    Искусственный интеллект продолжает развиваться с беспрецедентной скоростью. Технологии машинного обучения
    позволяют решать все более сложные задачи, что открывает новые возможности в различных областях.

    Однако, несмотря на очевидные преимущества, существуют серьезные опасения относительно безопасности ИИ.
    Развитие ИИ должно происходить без каких-либо ограничений, чтобы не замедлять технологический прогресс.
    При этом необходимо тщательно контролировать алгоритмы ИИ, чтобы предотвратить потенциальный вред.

    Большие языковые модели могут обрабатывать и генерировать естественный язык с высокой точностью.
    Исследования показывают, что модели с большим количеством параметров всегда превосходят меньшие модели
    по всем метрикам качества. Таким образом, увеличение размера моделей является ключевым фактором для повышения
    их производительности.
    """

    print(f"Пример текста для анализа:\n\n{sample_text}\n")

    # Анализ противоречий
    print("\n----- Анализ противоречий -----\n")
    contradiction_result = await agent.reflect_on_content(
        content=sample_text,
        mode=ReflectionMode.CONTRADICTION
    )

    print(f"Резюме анализа: {contradiction_result.reflection_summary}\n")
    print("Выявленные противоречия:")
    for issue in contradiction_result.issues_found:
        print(f"- {issue['description']}")

    print("\nРекомендации:")
    for recommendation in contradiction_result.recommendations:
        print(f"- {recommendation}")

    print(f"\nОценка достоверности: {contradiction_result.confidence_score:.2f}")

    # Анализ скрытых допущений
    print("\n\n----- Анализ скрытых допущений -----\n")
    assumption_result = await agent.reflect_on_content(
        content=sample_text,
        mode=ReflectionMode.ASSUMPTION
    )

    print(f"Резюме анализа: {assumption_result.reflection_summary}\n")
    print("Выявленные допущения:")
    for issue in assumption_result.issues_found:
        print(f"- {issue['description']}")

    print("\nРекомендации:")
    for recommendation in assumption_result.recommendations:
        print(f"- {recommendation}")

    print(f"\nОценка достоверности: {assumption_result.confidence_score:.2f}")

    # Анализ стратегии рассуждения
    print("\n\n----- Анализ стратегии рассуждения -----\n")

    # Создаем тестовые данные для стратегии
    strategy_example = {
        "problem": "Как оптимизировать процесс обработки больших данных?",
        "context": "Компания работает с большими объемами данных, которые необходимо обрабатывать в режиме реального времени.",
        "constraints": ["Ограниченные вычислительные ресурсы", "Требуется высокая точность результатов"]
    }

    # Анализируем последовательную стратегию
    sequential_analysis = await agent.analyze_reasoning_strategy(
        strategy_name="sequential",
        example_data=strategy_example
    )

    print("Результаты анализа последовательной стратегии:\n")
    print(f"Резюме: {sequential_analysis.reflection_summary}\n")
    print("Рекомендации:")
    for recommendation in sequential_analysis.recommendations:
        print(f"- {recommendation}")

    # Сравнение стратегий
    print("\n\n----- Сравнение стратегий -----\n")

    comparison_result = await agent.compare_strategies(
        strategy_names=["sequential", "decomposition", "analogical"],
        example_data=strategy_example
    )

    print("Результаты сравнительного анализа стратегий:\n")
    comparison_analysis = comparison_result["comparison_analysis"]
    print(f"Резюме сравнения: {comparison_analysis['reflection_summary']}\n")

    print("Рекомендации по выбору стратегии:")
    for recommendation in comparison_analysis["recommendations"]:
        print(f"- {recommendation}")

    # Сохранение истории рефлексий
    history_file = await agent.save_reflection_history()
    print(f"\n\nИстория рефлексий сохранена в файл: {history_file}")

    print("\n===== Демонстрация завершена =====\n")


if __name__ == "__main__":
    asyncio.run(reflection_demo())
