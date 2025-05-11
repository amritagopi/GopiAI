#!/usr/bin/env python
"""
Демонстрация работы системы приоритизации задач и ресурсов

Этот скрипт показывает, как ReasoningAgent управляет задачами
с разными приоритетами и требованиями к ресурсам.
"""

import os
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

from app.agent.reasoning import ReasoningAgent
from app.agent.resource_manager import ResourceType, TaskPriority, ResourceRequirement, Task


# Демонстрационные задачи
async def task_heavy_processing(duration: float, iterations: int = 10) -> Dict[str, Any]:
    """Задача с тяжелыми вычислениями"""
    start_time = time.time()
    result = 0

    for i in range(iterations):
        # Симулируем вычисления
        await asyncio.sleep(duration / iterations)
        result += i * i

    end_time = time.time()
    return {
        "result": result,
        "execution_time": end_time - start_time,
        "iterations": iterations
    }


async def task_api_call(url: str, delay: float = 1.0) -> Dict[str, Any]:
    """Задача, симулирующая вызов API"""
    start_time = time.time()

    # Симулируем задержку сети
    await asyncio.sleep(delay)

    end_time = time.time()
    return {
        "url": url,
        "status": "success",
        "response_time": end_time - start_time,
        "data": {"timestamp": datetime.now().isoformat()}
    }


async def task_file_operation(operation: str, file_size: int = 1024) -> Dict[str, Any]:
    """Задача, симулирующая операции с файлами"""
    start_time = time.time()

    # Симулируем операцию с файлом
    await asyncio.sleep(0.5 + file_size / 10000)

    end_time = time.time()
    return {
        "operation": operation,
        "file_size": file_size,
        "execution_time": end_time - start_time,
        "status": "completed"
    }


async def run_demo():
    """Основная демонстрационная функция"""
    print("=" * 80)
    print("Демонстрация системы приоритизации задач и ресурсов")
    print("=" * 80)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    # Проверяем, что менеджер ресурсов инициализирован
    if not agent.resource_manager:
        print("Ошибка: менеджер ресурсов не инициализирован")
        return

    print("\n1. Настройка ресурсов и приоритетов")
    print("-" * 80)

    # Настраиваем ресурсы (пулы ресурсов уже созданы при инициализации)
    agent.resource_manager.configure_resource(ResourceType.CPU, 0.7)  # 70% CPU
    agent.resource_manager.configure_resource(ResourceType.MEMORY, 0.6)  # 60% памяти
    agent.resource_manager.configure_resource(ResourceType.API_CALL, 0.4)  # 40% API вызовов
    agent.resource_manager.configure_resource(ResourceType.DISK, 0.8)  # 80% диска

    # Задаем максимальное количество одновременных задач
    agent.resource_manager.set_max_concurrent_tasks(3)

    print("Ресурсы настроены:")
    resources = await agent.get_resource_usage()
    if resources.get("success", False):
        for resource_name, resource_info in resources.get("resources", {}).items():
            print(f"  - {resource_name}: {resource_info['capacity']:.2f} (доступно: {resource_info['available']:.2f})")

    print("\n2. Добавление задач с разными приоритетами")
    print("-" * 80)

    # Создаем и добавляем задачи разных типов с разными приоритетами
    tasks = []

    # Критически важная задача с высоким приоритетом
    critical_task = Task(
        task_id=f"critical_{uuid.uuid4().hex[:8]}",
        name="Критически важная задача",
        priority=TaskPriority.CRITICAL,
        resources=[
            ResourceRequirement(ResourceType.CPU, amount=0.5, min_amount=0.3),
            ResourceRequirement(ResourceType.MEMORY, amount=0.3, min_amount=0.2)
        ],
        callback=task_heavy_processing,
        args=(2.0, 5),
        timeout=10.0
    )
    await agent.resource_manager.add_task(critical_task)
    tasks.append(critical_task.task_id)
    print(f"Добавлена критическая задача: {critical_task.name} (ID: {critical_task.task_id})")

    # Задачи с высоким приоритетом (API вызов)
    for i in range(2):
        high_task = Task(
            task_id=f"high_{uuid.uuid4().hex[:8]}",
            name=f"API вызов {i+1}",
            priority=TaskPriority.HIGH,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.2, min_amount=0.1),
                ResourceRequirement(ResourceType.API_CALL, amount=0.3, min_amount=0.2)
            ],
            callback=task_api_call,
            args=(f"https://api.example.com/data{i+1}",),
            kwargs={"delay": 1.5},
            timeout=5.0
        )
        await agent.resource_manager.add_task(high_task)
        tasks.append(high_task.task_id)
        print(f"Добавлена задача с высоким приоритетом: {high_task.name} (ID: {high_task.task_id})")

    # Задачи со средним приоритетом (файловые операции)
    for i in range(3):
        medium_task = Task(
            task_id=f"medium_{uuid.uuid4().hex[:8]}",
            name=f"Файловая операция {i+1}",
            priority=TaskPriority.MEDIUM,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.1, min_amount=0.05),
                ResourceRequirement(ResourceType.DISK, amount=0.2, min_amount=0.1)
            ],
            callback=task_file_operation,
            args=(f"write_file_{i+1}",),
            kwargs={"file_size": 2048 * (i+1)},
            timeout=8.0
        )
        await agent.resource_manager.add_task(medium_task)
        tasks.append(medium_task.task_id)
        print(f"Добавлена задача со средним приоритетом: {medium_task.name} (ID: {medium_task.task_id})")

    # Задачи с низким приоритетом (тяжелые вычисления)
    for i in range(2):
        low_task = Task(
            task_id=f"low_{uuid.uuid4().hex[:8]}",
            name=f"Фоновая обработка {i+1}",
            priority=TaskPriority.LOW,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.4, min_amount=0.1, can_scale=True),
                ResourceRequirement(ResourceType.MEMORY, amount=0.3, min_amount=0.1, can_scale=True)
            ],
            callback=task_heavy_processing,
            args=(3.0, 15),
            timeout=15.0
        )
        await agent.resource_manager.add_task(low_task)
        tasks.append(low_task.task_id)
        print(f"Добавлена задача с низким приоритетом: {low_task.name} (ID: {low_task.task_id})")

    print("\n3. Наблюдение за выполнением и приоритизацией")
    print("-" * 80)

    # Наблюдаем за выполнением задач
    all_completed = False
    check_interval = 1.0  # Интервал проверки в секундах
    max_observations = 10  # Максимальное количество наблюдений

    observations = 0
    while not all_completed and observations < max_observations:
        # Получаем текущий статус задач
        status = await agent.get_task_status()

        if status.get("success", False):
            # Выводим информацию о текущих активных задачах
            active_tasks = status.get("active_tasks", [])
            queue = status.get("queue", [])

            print(f"\nНаблюдение #{observations+1} (время: {datetime.now().strftime('%H:%M:%S')})")
            print(f"Активные задачи ({len(active_tasks)}):")
            for task in active_tasks:
                print(f"  - {task['name']} (приоритет: {task['priority']}, статус: {task['status']})")

            print(f"Задачи в очереди ({len(queue)}):")
            for task in queue:
                print(f"  - {task['name']} (приоритет: {task['priority']}, статус: {task['status']})")

            # Проверяем использование ресурсов
            system_status = status.get("system_status", {})
            resources_usage = system_status.get("resources", {})

            print("Использование ресурсов:")
            for resource_name, resource_info in resources_usage.items():
                if resource_name in ["cpu", "memory", "api_call", "disk"]:
                    allocated = resource_info.get("allocated", 0)
                    capacity = resource_info.get("capacity", 1.0)
                    usage_percent = (allocated / capacity) * 100 if capacity > 0 else 0
                    print(f"  - {resource_name}: {usage_percent:.1f}% ({allocated:.2f}/{capacity:.2f})")

            # Проверяем, все ли задачи завершены
            history = status.get("history", [])
            completed_tasks = [t for t in history if t["task_id"] in tasks]

            if len(completed_tasks) == len(tasks):
                all_completed = True
                print("\nВсе задачи завершены!")
                break
        else:
            print(f"Ошибка при получении статуса: {status.get('error', 'Неизвестная ошибка')}")

        # Увеличиваем счетчик наблюдений
        observations += 1

        # Ждем перед следующим наблюдением
        await asyncio.sleep(check_interval)

    print("\n4. Анализ результатов выполнения")
    print("-" * 80)

    # Получаем историю задач
    final_status = await agent.get_task_status()

    if final_status.get("success", False):
        history = final_status.get("history", [])

        # Фильтруем историю по нашим задачам
        our_tasks_history = [t for t in history if t["task_id"] in tasks]

        # Сортируем по времени завершения
        our_tasks_history.sort(key=lambda x: x.get("completed_at", ""))

        print("Порядок выполнения задач:")
        for idx, task in enumerate(our_tasks_history, 1):
            # Расчет времени выполнения
            started = datetime.fromisoformat(task.get("started_at", "")) if task.get("started_at") else None
            completed = datetime.fromisoformat(task.get("completed_at", "")) if task.get("completed_at") else None

            execution_time = None
            if started and completed:
                execution_time = (completed - started).total_seconds()

            print(f"{idx}. {task['name']} (приоритет: {task['priority']})")
            print(f"   Статус: {task['status']}")
            if execution_time is not None:
                print(f"   Время выполнения: {execution_time:.2f} секунд")

            if task['status'] == "failed" and task.get("error"):
                print(f"   Ошибка: {task['error']}")
            print()

        # Выводим статистику по приоритетам
        priorities = {}
        for task in our_tasks_history:
            priority = task["priority"]
            if priority not in priorities:
                priorities[priority] = {"count": 0, "completed": 0, "failed": 0}

            priorities[priority]["count"] += 1
            if task["status"] == "completed":
                priorities[priority]["completed"] += 1
            elif task["status"] == "failed":
                priorities[priority]["failed"] += 1

        print("Статистика по приоритетам:")
        for priority, stats in priorities.items():
            success_rate = (stats["completed"] / stats["count"]) * 100 if stats["count"] > 0 else 0
            print(f"  - {priority}: {stats['count']} задач, {stats['completed']} успешно ({success_rate:.1f}%)")
    else:
        print(f"Ошибка при получении статуса: {final_status.get('error', 'Неизвестная ошибка')}")

    print("\nДемонстрация завершена!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_demo())
