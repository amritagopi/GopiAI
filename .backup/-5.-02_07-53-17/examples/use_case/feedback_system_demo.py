#!/usr/bin/env python3
"""
Демонстрация работы системы обратной связи для стратегий исследования

Этот скрипт показывает, как использовать систему обратной связи
для улучшения стратегий исследования в GopiAI Reasoning Agent.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, List

# Добавляем корневую директорию проекта в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agent.feedback_system import (
    FeedbackManager, FeedbackType, FeedbackSource, FeedbackItem
)
from app.agent.exploration_feedback_integration import (
    FeedbackEnabledWebExplorationStrategy,
    FeedbackEnabledFileExplorationStrategy
)
from app.agent.file_system_access import FileSystemAccess
from app.agent.browser_access import BrowserAccess
from app.agent.thought_tree import ThoughtTree


async def demo_web_strategy():
    """
    Демонстрация работы стратегии веб-исследования с обратной связью
    """
    print("\n=== Демонстрация стратегии веб-исследования с обратной связью ===\n")

    # Создаем зависимости
    browser_access = BrowserAccess()
    thought_tree = ThoughtTree()

    # Создаем стратегию
    strategy = FeedbackEnabledWebExplorationStrategy(
        browser_access=browser_access,
        thought_tree=thought_tree,
        max_pages=3,
        max_depth=1
    )

    # 1. Выполняем первое исследование
    print("Выполнение первого исследования...")
    query = "Новые технологии в разработке ИИ"

    collection = await strategy.explore_with_feedback(query)

    print(f"Собрано элементов: {len(collection.items)}")

    # 2. Добавляем ручную обратную связь
    print("\nДобавление ручной обратной связи...")

    strategy.apply_user_feedback(
        feedback_type=FeedbackType.RELEVANCE,
        score=0.4,  # Низкая оценка релевантности
        description="Результаты недостаточно релевантны запросу"
    )

    strategy.apply_user_feedback(
        feedback_type=FeedbackType.EFFICIENCY,
        score=0.7,  # Хорошая оценка эффективности
        description="Стратегия работает достаточно быстро"
    )

    # 3. Получаем и выводим производительность
    print("\nПроизводительность стратегии после первого запуска:")

    performance = strategy.feedback_manager.get_strategy_performance(strategy.name)
    print_dict(performance)

    # 4. Получаем и выводим рекомендации
    print("\nРекомендации по улучшению стратегии:")

    recommendations = strategy.feedback_manager.get_improvement_recommendations(strategy.name)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['issue']} (приоритет: {rec['priority']})")
        print(f"   Действие: {rec['action']}")

    # 5. Выполняем второе исследование (с адаптивными параметрами)
    print("\nВыполнение второго исследования (с адаптивными параметрами)...")

    collection2 = await strategy.explore_with_feedback(query)

    print(f"Собрано элементов: {len(collection2.items)}")

    # 6. Добавляем положительную обратную связь
    print("\nДобавление положительной обратной связи...")

    strategy.apply_user_feedback(
        feedback_type=FeedbackType.RELEVANCE,
        score=0.8,  # Хорошая оценка релевантности
        description="Результаты стали значительно лучше"
    )

    # 7. Получаем и выводим обновленную производительность
    print("\nПроизводительность стратегии после второго запуска:")

    performance = strategy.feedback_manager.get_strategy_performance(strategy.name)
    print_dict(performance)


async def demo_file_strategy():
    """
    Демонстрация работы стратегии исследования файловой системы с обратной связью
    """
    print("\n=== Демонстрация стратегии исследования файловой системы с обратной связью ===\n")

    # Создаем зависимости
    file_system = FileSystemAccess()
    thought_tree = ThoughtTree()

    # Создаем стратегию
    strategy = FeedbackEnabledFileExplorationStrategy(
        file_system=file_system,
        thought_tree=thought_tree,
        max_files=5
    )

    # 1. Выполняем первое исследование
    print("Выполнение первого исследования...")
    query = "модули искусственного интеллекта"

    collection = await strategy.explore_with_feedback(
        query,
        directory="app",
        recursive=True
    )

    print(f"Собрано элементов: {len(collection.items)}")

    # 2. Добавляем обратную связь (низкая полнота)
    print("\nДобавление обратной связи (низкая полнота)...")

    strategy.apply_user_feedback(
        feedback_type=FeedbackType.COMPLETENESS,
        score=0.3,  # Низкая оценка полноты
        description="Найдено слишком мало файлов по запросу"
    )

    # 3. Получаем и выводим рекомендации
    print("\nРекомендации по улучшению стратегии:")

    recommendations = strategy.feedback_manager.get_improvement_recommendations(strategy.name)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['issue']} (приоритет: {rec['priority']})")
        print(f"   Действие: {rec['action']}")

    # 4. Выполняем второе исследование (с адаптивными параметрами)
    print("\nВыполнение второго исследования (с адаптивными параметрами)...")

    collection2 = await strategy.explore_with_feedback(
        query,
        directory="app",
        recursive=True
    )

    print(f"Собрано элементов: {len(collection2.items)}")

    # 5. Получаем и выводим адаптивные параметры
    print("\nАдаптивные параметры, примененные во втором запуске:")

    adaptive_params = strategy.get_adaptive_parameters(query)
    print_dict(adaptive_params)

    # 6. Добавляем положительную обратную связь
    print("\nДобавление положительной обратной связи...")

    strategy.apply_user_feedback(
        feedback_type=FeedbackType.COMPLETENESS,
        score=0.8,  # Хорошая оценка полноты
        description="Теперь найдено достаточно файлов"
    )

    # 7. Получаем и выводим все данные обратной связи
    print("\nВсе данные обратной связи для стратегии:")

    all_feedback = strategy.feedback_manager.get_all_feedback(strategy.name)
    print(f"Всего элементов обратной связи: {len(all_feedback)}")

    for i, feedback in enumerate(all_feedback, 1):
        print(f"{i}. Тип: {feedback['feedback_type']}, Оценка: {feedback['score']:.1f}, Источник: {feedback['source']}")
        if feedback['description']:
            print(f"   Описание: {feedback['description']}")


def demo_feedback_analysis():
    """
    Демонстрация анализа данных обратной связи
    """
    print("\n=== Демонстрация анализа данных обратной связи ===\n")

    # Создаем менеджер обратной связи
    manager = FeedbackManager()

    # Создаем тестовые данные для двух стратегий
    strategy1 = "strategy_a"
    strategy2 = "strategy_b"

    # Добавляем данные для первой стратегии (хорошие показатели)
    print("Добавление тестовых данных для первой стратегии (хорошие показатели)...")

    manager.add_user_feedback(
        strategy_id=strategy1,
        feedback_type=FeedbackType.RELEVANCE,
        score=0.9,
        description="Очень релевантные результаты"
    )

    manager.add_user_feedback(
        strategy_id=strategy1,
        feedback_type=FeedbackType.EFFICIENCY,
        score=0.8,
        description="Быстрое выполнение"
    )

    manager.add_user_feedback(
        strategy_id=strategy1,
        feedback_type=FeedbackType.COMPLETENESS,
        score=0.7,
        description="Достаточно полные результаты"
    )

    # Добавляем данные для второй стратегии (плохие показатели)
    print("Добавление тестовых данных для второй стратегии (плохие показатели)...")

    manager.add_user_feedback(
        strategy_id=strategy2,
        feedback_type=FeedbackType.RELEVANCE,
        score=0.4,
        description="Недостаточно релевантные результаты"
    )

    manager.add_user_feedback(
        strategy_id=strategy2,
        feedback_type=FeedbackType.EFFICIENCY,
        score=0.3,
        description="Очень медленное выполнение"
    )

    manager.add_user_feedback(
        strategy_id=strategy2,
        feedback_type=FeedbackType.COMPLETENESS,
        score=0.5,
        description="Средняя полнота результатов"
    )

    # Сравниваем производительность стратегий
    print("\nСравнение производительности стратегий:")

    perf1 = manager.get_strategy_performance(strategy1)
    perf2 = manager.get_strategy_performance(strategy2)

    print(f"Стратегия A - общая оценка: {perf1['overall_score']:.2f}")
    print(f"Стратегия B - общая оценка: {perf2['overall_score']:.2f}")

    print("\nРазбивка по метрикам:")

    metrics1 = perf1.get("metrics", {})
    metrics2 = perf2.get("metrics", {})

    for metric_type in FeedbackType:
        type_value = metric_type.value
        score1 = metrics1.get(type_value, "N/A")
        score2 = metrics2.get(type_value, "N/A")

        if score1 != "N/A":
            score1 = f"{score1:.2f}"
        if score2 != "N/A":
            score2 = f"{score2:.2f}"

        print(f"{type_value.capitalize()}: Стратегия A = {score1}, Стратегия B = {score2}")

    # Получаем рекомендации для проблемной стратегии
    print("\nРекомендации для проблемной стратегии (B):")

    recommendations = manager.get_improvement_recommendations(strategy2)

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['issue']} (приоритет: {rec['priority']})")
        print(f"   Действие: {rec['action']}")


def print_dict(data: Dict[str, Any], indent: int = 0):
    """
    Форматированный вывод словаря

    Args:
        data: Словарь для вывода
        indent: Отступ
    """
    for key, value in data.items():
        if isinstance(value, dict):
            print(" " * indent + f"{key}:")
            print_dict(value, indent + 2)
        elif isinstance(value, list):
            if not value:
                print(" " * indent + f"{key}: []")
            else:
                print(" " * indent + f"{key}:")
                if isinstance(value[0], dict):
                    for i, item in enumerate(value):
                        print(" " * (indent + 2) + f"[{i}]:")
                        print_dict(item, indent + 4)
                else:
                    for item in value:
                        print(" " * (indent + 2) + f"- {item}")
        else:
            print(" " * indent + f"{key}: {value}")


async def main():
    """
    Основная функция демонстрации
    """
    print("=== Демонстрация системы обратной связи для стратегий исследования ===")

    # Демонстрация анализа данных обратной связи
    demo_feedback_analysis()

    # Демонстрация стратегии веб-исследования
    await demo_web_strategy()

    # Демонстрация стратегии исследования файловой системы
    await demo_file_strategy()

    print("\n=== Демонстрация завершена ===")


if __name__ == "__main__":
    asyncio.run(main())
