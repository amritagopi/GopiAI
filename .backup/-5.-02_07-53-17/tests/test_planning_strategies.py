"""
Тестирование стратегий планирования для Reasoning Agent

Проверяет работу различных стратегий планирования, включая адаптивную стратегию,
древовидную стратегию и стратегию с обработкой неопределенностей.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.planning_strategy import (
    get_planning_strategy, AdaptivePlanningStrategy,
    TreePlanningStrategy, UncertaintyPlanningStrategy,
    TaskComplexity
)
from app.config.reasoning_config import ReasoningStrategy
from app.mcp.sequential_thinking import SequentialThinking
from app.mcp.client import MCPClient


class PlanningStrategyTester:
    """Класс для тестирования стратегий планирования"""

    def __init__(self):
        """Инициализирует тестовый класс"""
        self.mcp_client = None
        self.sequential_thinking = None
        self.test_results = []

    async def setup(self):
        """Настраивает тестовое окружение"""
        print("\n=== Setting up PlanningStrategy test environment ===")

        try:
            # Создаем Mock MCP клиент
            self.mcp_client = MockMCPClient()

            # Инициализируем Sequential Thinking с мок-клиентом
            self.sequential_thinking = SequentialThinking(self.mcp_client)
            self.sequential_thinking.initialized = True  # Устанавливаем флаг вручную для тестирования

            print("Setup completed successfully")
            return True
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return False

    async def test_get_planning_strategy(self):
        """Тестирует фабричный метод для получения стратегий планирования"""
        print("\n=== Testing get_planning_strategy factory method ===")

        # Получаем стратегии разных типов
        adaptive_strategy = get_planning_strategy(ReasoningStrategy.ADAPTIVE)
        tree_strategy = get_planning_strategy(ReasoningStrategy.TREE)
        sequential_strategy = get_planning_strategy(ReasoningStrategy.SEQUENTIAL)

        # Проверяем, что получены правильные типы
        is_adaptive_correct = isinstance(adaptive_strategy, AdaptivePlanningStrategy)
        is_tree_correct = isinstance(tree_strategy, TreePlanningStrategy)
        is_sequential_correct = isinstance(sequential_strategy, AdaptivePlanningStrategy)  # Sequential использует адаптивную стратегию

        self.test_results.append(("Factory method - adaptive strategy", is_adaptive_correct))
        self.test_results.append(("Factory method - tree strategy", is_tree_correct))
        self.test_results.append(("Factory method - sequential strategy", is_sequential_correct))

        print(f"Adaptive strategy type correct: {is_adaptive_correct}")
        print(f"Tree strategy type correct: {is_tree_correct}")
        print(f"Sequential strategy type correct: {is_sequential_correct}")

    async def test_adaptive_strategy_with_simple_task(self):
        """Тестирует адаптивную стратегию с простой задачей"""
        print("\n=== Testing adaptive strategy with simple task ===")

        # Создаем стратегию
        strategy = AdaptivePlanningStrategy()

        # Простая задача
        simple_task = "Напиши функцию, которая проверяет, является ли число простым."

        # Запускаем анализ сложности
        complexity, metadata = await strategy.analyze_task_complexity(simple_task, self.sequential_thinking)

        # Создаем план
        plan_data = await strategy.create_plan(simple_task, self.sequential_thinking)

        # Проверяем результаты
        has_complexity = complexity is not None
        has_metadata = metadata is not None
        has_plan = plan_data is not None and "plan_text" in plan_data
        complexity_is_simple = complexity == TaskComplexity.SIMPLE

        self.test_results.append(("Adaptive strategy - simple task complexity analysis", has_complexity))
        self.test_results.append(("Adaptive strategy - simple task metadata", has_metadata))
        self.test_results.append(("Adaptive strategy - simple task plan creation", has_plan))
        self.test_results.append(("Adaptive strategy - complexity is SIMPLE", complexity_is_simple))

        print(f"Task complexity: {complexity.value if complexity else 'None'}")
        print(f"Has metadata: {has_metadata}")
        print(f"Has plan: {has_plan}")
        print(f"Complexity is SIMPLE: {complexity_is_simple}")

        if has_plan:
            # Показываем часть плана
            plan_text = plan_data.get("plan_text", "")
            print(f"Plan (first 100 chars): {plan_text[:100]}...")

    async def test_adaptive_strategy_with_complex_task(self):
        """Тестирует адаптивную стратегию со сложной задачей"""
        print("\n=== Testing adaptive strategy with complex task ===")

        # Создаем стратегию
        strategy = AdaptivePlanningStrategy()

        # Сложная задача
        complex_task = """
        Разработай систему рекомендаций товаров для интернет-магазина на основе истории покупок пользователя.
        Система должна учитывать следующие факторы:
        1. История покупок пользователя
        2. Похожие товары на основе характеристик
        3. Сезонность и тренды
        4. Акции и скидки
        5. Демографические данные пользователя

        Необходимо также реализовать A/B тестирование различных алгоритмов рекомендаций и систему сбора обратной связи.
        """

        # Запускаем анализ сложности
        complexity, metadata = await strategy.analyze_task_complexity(complex_task, self.sequential_thinking)

        # Создаем план
        plan_data = await strategy.create_plan(complex_task, self.sequential_thinking)

        # Проверяем результаты
        has_complexity = complexity is not None
        has_metadata = metadata is not None
        has_plan = plan_data is not None and "plan_text" in plan_data
        complexity_is_complex = complexity in [TaskComplexity.COMPLEX, TaskComplexity.MEDIUM]  # Может быть определено как MEDIUM

        self.test_results.append(("Adaptive strategy - complex task complexity analysis", has_complexity))
        self.test_results.append(("Adaptive strategy - complex task metadata", has_metadata))
        self.test_results.append(("Adaptive strategy - complex task plan creation", has_plan))
        self.test_results.append(("Adaptive strategy - complexity is COMPLEX/MEDIUM", complexity_is_complex))

        print(f"Task complexity: {complexity.value if complexity else 'None'}")
        print(f"Has metadata: {has_metadata}")
        print(f"Has plan: {has_plan}")
        print(f"Complexity is COMPLEX/MEDIUM: {complexity_is_complex}")

        if has_plan:
            # Показываем часть плана
            plan_text = plan_data.get("plan_text", "")
            print(f"Plan (first 100 chars): {plan_text[:100]}...")

    async def test_adaptive_strategy_with_uncertain_task(self):
        """Тестирует адаптивную стратегию с задачей с высокой неопределенностью"""
        print("\n=== Testing adaptive strategy with uncertain task ===")

        # Создаем стратегию
        strategy = AdaptivePlanningStrategy()

        # Задача с неопределенностью
        uncertain_task = """
        Исследуй возможность создания нового продукта на стыке искусственного интеллекта и здравоохранения.
        Необходимо учесть нормативно-правовую базу, которая может значительно отличаться в разных странах,
        потенциальные этические проблемы и возможные конфигурации продукта.
        Также важно оценить различные технологические подходы и их применимость.
        """

        # Запускаем анализ сложности
        complexity, metadata = await strategy.analyze_task_complexity(uncertain_task, self.sequential_thinking)

        # Создаем план
        plan_data = await strategy.create_plan(uncertain_task, self.sequential_thinking)

        # Проверяем результаты
        has_complexity = complexity is not None
        has_metadata = metadata is not None
        has_plan = plan_data is not None and "plan_text" in plan_data

        self.test_results.append(("Adaptive strategy - uncertain task complexity analysis", has_complexity))
        self.test_results.append(("Adaptive strategy - uncertain task metadata", has_metadata))
        self.test_results.append(("Adaptive strategy - uncertain task plan creation", has_plan))

        print(f"Task complexity: {complexity.value if complexity else 'None'}")
        print(f"Has metadata: {has_metadata}")
        print(f"Has plan: {has_plan}")

        if has_plan:
            # Показываем часть плана
            plan_text = plan_data.get("plan_text", "")
            print(f"Plan (first 100 chars): {plan_text[:100]}...")

    async def test_plan_adaptation(self):
        """Тестирует адаптацию плана при получении новой информации"""
        print("\n=== Testing plan adaptation ===")

        # Создаем стратегию
        strategy = AdaptivePlanningStrategy()

        # Создаем исходный план
        original_plan = {
            "task": "Разработать простое веб-приложение",
            "steps": [
                {"description": "Создать HTML структуру", "risk": "LOW"},
                {"description": "Добавить CSS стили", "risk": "LOW"},
                {"description": "Реализовать JavaScript функционал", "risk": "MEDIUM"}
            ],
            "tools": ["VS Code", "Chrome DevTools"],
            "complexity": "simple"
        }

        # Создаем новую информацию
        new_information = {
            "updated_steps": [
                {"description": "Создать HTML структуру", "risk": "LOW"},
                {"description": "Добавить CSS стили", "risk": "LOW"},
                {"description": "Реализовать JavaScript функционал", "risk": "MEDIUM"},
                {"description": "Добавить поддержку мобильных устройств", "risk": "MEDIUM"}
            ],
            "additional_tools": ["Mobile Device Emulator"],
            "complexity": "medium"
        }

        # Адаптируем план
        adapted_plan = await strategy.adapt_plan(original_plan, new_information)

        # Проверяем результаты
        has_adapted_plan = adapted_plan is not None
        steps_updated = len(adapted_plan.get("steps", [])) == 4 if has_adapted_plan else False
        tools_updated = "Mobile Device Emulator" in adapted_plan.get("tools", []) if has_adapted_plan else False
        complexity_updated = adapted_plan.get("complexity") == "medium" if has_adapted_plan else False

        self.test_results.append(("Plan adaptation - adapted plan created", has_adapted_plan))
        self.test_results.append(("Plan adaptation - steps updated", steps_updated))
        self.test_results.append(("Plan adaptation - tools updated", tools_updated))
        self.test_results.append(("Plan adaptation - complexity updated", complexity_updated))

        print(f"Adapted plan created: {has_adapted_plan}")
        print(f"Steps updated: {steps_updated}")
        print(f"Tools updated: {tools_updated}")
        print(f"Complexity updated: {complexity_updated}")

        if has_adapted_plan:
            print(f"Adapted plan steps count: {len(adapted_plan.get('steps', []))}")
            print(f"Adapted plan tools: {adapted_plan.get('tools', [])}")
            print(f"Adapted plan complexity: {adapted_plan.get('complexity')}")

    async def test_json_extraction(self):
        """Тестирует извлечение JSON из текста"""
        print("\n=== Testing JSON extraction ===")

        # Создаем стратегию
        strategy = AdaptivePlanningStrategy()

        # Тестовые тексты
        text_with_json_markers = """
        Вот структурированный план:

        ```json
        {
            "task": "Тестовая задача",
            "steps": [
                {"description": "Шаг 1", "risk": "LOW"},
                {"description": "Шаг 2", "risk": "MEDIUM"}
            ]
        }
        ```

        Этот план содержит все необходимые шаги.
        """

        text_with_json_no_markers = """
        Вот структурированный план:

        {
            "task": "Тестовая задача",
            "steps": [
                {"description": "Шаг 1", "risk": "LOW"},
                {"description": "Шаг 2", "risk": "MEDIUM"}
            ]
        }

        Этот план содержит все необходимые шаги.
        """

        text_without_json = "Этот текст не содержит JSON структуры."

        # Извлекаем JSON
        json_from_markers = strategy._extract_json_from_text(text_with_json_markers)
        json_without_markers = strategy._extract_json_from_text(text_with_json_no_markers)
        json_from_plain_text = strategy._extract_json_from_text(text_without_json)

        # Проверяем результаты
        can_parse_with_markers = True
        can_parse_without_markers = True
        empty_for_plain_text = json_from_plain_text == "{}"

        try:
            parsed_json = json.loads(json_from_markers)
            assert "task" in parsed_json
            assert "steps" in parsed_json
        except (json.JSONDecodeError, AssertionError):
            can_parse_with_markers = False

        try:
            parsed_json = json.loads(json_without_markers)
            assert "task" in parsed_json
            assert "steps" in parsed_json
        except (json.JSONDecodeError, AssertionError):
            can_parse_without_markers = False

        self.test_results.append(("JSON extraction - with markers", can_parse_with_markers))
        self.test_results.append(("JSON extraction - without markers", can_parse_without_markers))
        self.test_results.append(("JSON extraction - empty for plain text", empty_for_plain_text))

        print(f"Can parse JSON with markers: {can_parse_with_markers}")
        print(f"Can parse JSON without markers: {can_parse_without_markers}")
        print(f"Empty JSON for plain text: {empty_for_plain_text}")

    async def teardown(self):
        """Освобождает ресурсы после тестирования"""
        print("\n=== Tearing down test environment ===")
        print("Teardown completed successfully")

    async def run_tests(self):
        """Запускает все тесты"""
        setup_success = await self.setup()
        if not setup_success:
            print("Cannot run tests due to setup failure")
            return

        try:
            await self.test_get_planning_strategy()
            await self.test_adaptive_strategy_with_simple_task()
            await self.test_adaptive_strategy_with_complex_task()
            await self.test_adaptive_strategy_with_uncertain_task()
            await self.test_plan_adaptation()
            await self.test_json_extraction()

            # Выводим результаты
            print("\n=== Test Results ===")
            for i, (test_name, result) in enumerate(self.test_results, 1):
                status = "PASSED" if result else "FAILED"
                print(f"{i}. {test_name}: {status}")

            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            print(f"\nPassed {passed}/{total} tests ({passed/total*100:.1f}%)")

        finally:
            await self.teardown()


class MockMCPClient:
    """Mock-класс для MCP клиента в тестах"""

    def __init__(self):
        """Инициализирует mock-клиент"""
        self.tool_map = {"mcp_sequential-thinking_sequentialthinking": "mock_function"}
        self.query_log = []

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Имитирует вызов инструмента MCP

        Args:
            tool_name: Имя инструмента
            params: Параметры инструмента

        Returns:
            Мок-ответ инструмента
        """
        self.query_log.append((tool_name, params))

        # Имитация ответа Sequential Thinking
        if tool_name == "mcp_sequential-thinking_sequentialthinking":
            thought = params.get("thought", "")

            # Генерируем ответ в зависимости от содержимого мысли
            if "complexity" in thought.lower():
                # Для анализа сложности
                if "simple" in thought.lower():
                    return {
                        "thought": """
                        Analyzing task complexity:

                        Steps count: 3
                        Interdependencies: 2
                        Uncertainty: 3
                        Technical complexity: 2

                        Overall complexity category: Simple
                        """,
                        "nextThoughtNeeded": False
                    }
                elif "complex" in thought.lower():
                    return {
                        "thought": """
                        Analyzing task complexity:

                        Steps count: 8
                        Interdependencies: 7
                        Uncertainty: 6
                        Technical complexity: 8

                        Overall complexity category: Complex
                        """,
                        "nextThoughtNeeded": False
                    }
                else:
                    return {
                        "thought": """
                        Analyzing task complexity:

                        Steps count: 5
                        Interdependencies: 4
                        Uncertainty: 7
                        Technical complexity: 5

                        Overall complexity category: Uncertain
                        """,
                        "nextThoughtNeeded": False
                    }
            elif "plan" in thought.lower():
                # Для создания плана
                return {
                    "thought": """
                    Here's a structured plan:

                    ```json
                    {
                        "task": "Sample task from mock",
                        "steps": [
                            {"description": "Step 1", "risk": "LOW"},
                            {"description": "Step 2", "risk": "MEDIUM"},
                            {"description": "Step 3", "risk": "LOW"}
                        ],
                        "risks": [
                            {"description": "Potential issue 1", "level": "LOW", "mitigation": "Backup regularly"},
                            {"description": "Potential issue 2", "level": "MEDIUM", "mitigation": "Test thoroughly"}
                        ],
                        "tools": ["Tool 1", "Tool 2"]
                    }
                    ```
                    """,
                    "nextThoughtNeeded": False
                }
            else:
                # Общий случай
                return {
                    "thought": f"Mock response for: {thought}",
                    "nextThoughtNeeded": False
                }

        # Общий случай для других инструментов
        return {"result": "mock_result", "success": True}


async def main():
    """Главная функция для запуска тестов"""
    print("=== Starting PlanningStrategy Tests ===")

    tester = PlanningStrategyTester()
    await tester.run_tests()


if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(main())
