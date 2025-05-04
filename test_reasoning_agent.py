#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы Reasoning Agent.

Скрипт демонстрирует основные возможности ReasoningAgent:
1. Создание плана
2. Одобрение плана
3. Выполнение действий
"""

import asyncio
import argparse
import sys
from typing import Optional

from app.agent.reasoning import ReasoningAgent
from app.logger import logger


async def test_plan_creation(agent: ReasoningAgent, task: str) -> None:
    """
    Тестирует создание плана для указанной задачи.

    Args:
        agent: Экземпляр ReasoningAgent
        task: Задача для планирования
    """
    print(f"\n--- Создание плана для задачи: {task} ---\n")

    try:
        plan = await agent.create_plan(task)
        print("План успешно создан:")
        print("-" * 80)
        print(plan)
        print("-" * 80)
        return plan
    except Exception as e:
        print(f"Ошибка при создании плана: {str(e)}")
        return None


async def test_plan_approval(agent: ReasoningAgent) -> bool:
    """
    Тестирует одобрение текущего плана.

    Args:
        agent: Экземпляр ReasoningAgent

    Returns:
        True если план одобрен, False если нет
    """
    print("\n--- Одобрение плана ---\n")

    if agent.current_plan is None:
        print("Нет текущего плана для одобрения")
        return False

    approval = input("Одобрить план? (y/n): ")
    if approval.lower() in ['y', 'yes', 'да']:
        agent.approve_plan()
        print("План одобрен")
        return True
    else:
        agent.reject_plan()
        print("План отклонен")
        return False


async def test_execution(agent: ReasoningAgent, request: str) -> None:
    """
    Тестирует выполнение запроса после одобрения плана.

    Args:
        agent: Экземпляр ReasoningAgent
        request: Запрос для выполнения
    """
    print(f"\n--- Выполнение запроса: {request} ---\n")

    try:
        result = await agent.run(request)
        print("Результат выполнения:")
        print("-" * 80)
        print(result)
        print("-" * 80)
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")


async def test_reasoning(
    connection_type: str = "stdio",
    server_url: Optional[str] = None,
    task: str = "Создать тестовый файл с текстом 'Привет, мир!'",
) -> None:
    """
    Запускает полный тест ReasoningAgent.

    Args:
        connection_type: Тип подключения к MCP-серверу
        server_url: URL для подключения (для SSE)
        task: Задача для тестирования
    """
    agent = ReasoningAgent()

    try:
        # Инициализируем агента
        print("\n=== Инициализация агента ===\n")
        if connection_type == "stdio":
            await agent.initialize(
                connection_type="stdio",
                command=sys.executable,
                args=["-m", "mcp.server"],
            )
        else:  # sse
            await agent.initialize(connection_type="sse", server_url=server_url)

        print("Агент успешно инициализирован")

        # Создаем план
        plan = await test_plan_creation(agent, task)
        if plan is None:
            return

        # Одобряем план
        approved = await test_plan_approval(agent)
        if not approved:
            return

        # Выполняем запрос
        await test_execution(agent, task)

    except Exception as e:
        print(f"Ошибка в тесте: {str(e)}")
    finally:
        # Очищаем ресурсы
        await agent.cleanup()
        print("\n=== Тест завершен ===\n")


def parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Тест Reasoning Agent")
    parser.add_argument(
        "--connection",
        "-c",
        choices=["stdio", "sse"],
        default="stdio",
        help="Тип подключения: stdio или sse",
    )
    parser.add_argument(
        "--server-url",
        default="http://127.0.0.1:8000/sse",
        help="URL для SSE подключения",
    )
    parser.add_argument(
        "--task",
        "-t",
        default="Создать тестовый файл test.txt с текстом 'Привет, мир!'",
        help="Задача для тестирования",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(test_reasoning(args.connection, args.server_url, args.task))
