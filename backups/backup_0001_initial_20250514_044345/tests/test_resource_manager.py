"""
Тесты для модуля управления ресурсами и приоритизации задач.

Проверяет функциональность ResourceManager и интеграцию с ReasoningAgent.
"""

import os
import json
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.agent.resource_manager import (
    ResourceManager, ResourceType, TaskPriority,
    ResourceRequirement, Task, ResourcePool
)


class TestResourcePool(unittest.TestCase):
    """Тесты для класса ResourcePool"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.resource_pool = ResourcePool(ResourceType.CPU, capacity=1.0)

    def test_availability(self):
        """Проверка расчета доступного ресурса"""
        # Изначально доступно 100%
        self.assertEqual(1.0, self.resource_pool.available())

        # Выделяем 30% для задачи
        self.resource_pool.allocate("task1", 0.3)
        self.assertEqual(0.7, self.resource_pool.available())

        # Резервируем еще 20%
        self.resource_pool.reserve(0.2)
        self.assertEqual(0.5, self.resource_pool.available())

    def test_overallocation_prevention(self):
        """Проверка предотвращения превышения доступных ресурсов"""
        # Выделяем 60% ресурса
        allocated1 = self.resource_pool.allocate("task1", 0.6)
        self.assertEqual(0.6, allocated1)

        # Пытаемся выделить еще 60%, должно выделиться только 40%
        allocated2 = self.resource_pool.allocate("task2", 0.6)
        self.assertEqual(0.4, allocated2)

        # Теперь ресурс полностью использован
        self.assertEqual(0.0, self.resource_pool.available())

        # Пытаемся выделить еще, должно выделиться 0
        allocated3 = self.resource_pool.allocate("task3", 0.1)
        self.assertEqual(0.0, allocated3)

    def test_release(self):
        """Проверка освобождения ресурса"""
        # Выделяем ресурс для задачи
        allocated = self.resource_pool.allocate("task1", 0.5)
        self.assertEqual(0.5, allocated)
        self.assertEqual(0.5, self.resource_pool.allocated())

        # Освобождаем ресурс
        released = self.resource_pool.release("task1")
        self.assertEqual(0.5, released)
        self.assertEqual(0.0, self.resource_pool.allocated())
        self.assertEqual(1.0, self.resource_pool.available())

    def test_metrics_update(self):
        """Проверка обновления метрик использования"""
        # Изначально метрики нулевые
        self.assertEqual(0.0, self.resource_pool.metrics.peak_usage)
        self.assertEqual(0.0, self.resource_pool.metrics.average_usage)

        # Выделяем ресурс
        self.resource_pool.allocate("task1", 0.3)

        # Проверяем обновление метрик
        self.assertEqual(0.3, self.resource_pool.metrics.peak_usage)
        self.assertEqual(0.3, self.resource_pool.metrics.average_usage)

        # Выделяем больше ресурса
        self.resource_pool.allocate("task2", 0.4)

        # Проверяем обновление пикового использования
        self.assertEqual(0.7, self.resource_pool.metrics.peak_usage)

        # Среднее должно быть между предыдущими значениями
        self.assertTrue(0.3 < self.resource_pool.metrics.average_usage < 0.7)


class TestResourceManager(unittest.TestCase):
    """Тесты для класса ResourceManager"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.resource_manager = ResourceManager()

    def tearDown(self):
        """Очистка после каждого теста"""
        asyncio.run(self.resource_manager.cleanup())

    async def test_task_addition(self):
        """Проверка добавления задачи в очередь"""
        # Тестовая задача
        async def test_func():
            return "test_result"

        task = Task(
            task_id="test_task",
            name="Test Task",
            priority=TaskPriority.MEDIUM,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.2)
            ],
            callback=test_func
        )

        # Добавляем задачу
        task_id = await self.resource_manager.add_task(task)
        self.assertEqual("test_task", task_id)

        # Проверяем, что задача запланирована или выполняется
        task_info = self.resource_manager.get_task("test_task")
        self.assertIsNotNone(task_info)

        # Дожидаемся выполнения задачи
        max_wait = 5  # максимальное время ожидания в секундах
        for _ in range(max_wait * 10):
            task_info = self.resource_manager.get_task("test_task")
            if task_info.status in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)

        # Проверяем, что задача выполнена
        self.assertEqual("completed", task_info.status)
        self.assertEqual("test_result", task_info.result)

    async def test_task_prioritization(self):
        """Проверка приоритизации задач"""
        # Ограничиваем количество одновременных задач
        self.resource_manager.set_max_concurrent_tasks(1)

        # Функция для тестовой задачи
        async def test_func(task_name, duration=0.1):
            await asyncio.sleep(duration)
            return f"result_{task_name}"

        # Создаем задачи с разными приоритетами
        low_task = Task(
            task_id="low_task",
            name="Low Priority Task",
            priority=TaskPriority.LOW,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.1)
            ],
            callback=test_func,
            args=("low",)
        )

        high_task = Task(
            task_id="high_task",
            name="High Priority Task",
            priority=TaskPriority.HIGH,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.1)
            ],
            callback=test_func,
            args=("high",)
        )

        critical_task = Task(
            task_id="critical_task",
            name="Critical Task",
            priority=TaskPriority.CRITICAL,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.1)
            ],
            callback=test_func,
            args=("critical",)
        )

        # Добавляем задачи в порядке от низкого к высокому приоритету
        await self.resource_manager.add_task(low_task)
        await self.resource_manager.add_task(high_task)
        await self.resource_manager.add_task(critical_task)

        # Ожидаем, пока все задачи не будут выполнены
        completed = set()
        execution_order = []
        max_wait = 10  # максимальное время ожидания в секундах

        for _ in range(max_wait * 10):
            # Проверяем историю выполненных задач
            history = self.resource_manager.get_task_history_info(limit=10)

            for task in history:
                task_id = task["task_id"]
                if task_id not in completed and task["status"] == "completed":
                    completed.add(task_id)
                    execution_order.append(task_id)

            if len(completed) == 3:
                break

            await asyncio.sleep(0.1)

        # Проверяем порядок выполнения задач (от высокого приоритета к низкому)
        self.assertEqual(3, len(execution_order), "Не все задачи были выполнены")
        self.assertEqual("critical_task", execution_order[0], "Задача CRITICAL должна быть выполнена первой")
        self.assertEqual("high_task", execution_order[1], "Задача HIGH должна быть выполнена второй")
        self.assertEqual("low_task", execution_order[2], "Задача LOW должна быть выполнена последней")

    async def test_resource_allocation(self):
        """Проверка выделения ресурсов"""
        # Настраиваем емкость ресурса
        self.resource_manager.configure_resource(ResourceType.MEMORY, 0.5)  # 50% памяти

        # Тестовая функция
        async def test_func():
            await asyncio.sleep(0.2)
            return "test"

        # Создаем задачу, требующую 40% памяти
        task1 = Task(
            task_id="task1",
            name="Memory Task 1",
            priority=TaskPriority.MEDIUM,
            resources=[
                ResourceRequirement(ResourceType.MEMORY, amount=0.4, min_amount=0.3)
            ],
            callback=test_func
        )

        # Создаем вторую задачу, требующую 30% памяти
        task2 = Task(
            task_id="task2",
            name="Memory Task 2",
            priority=TaskPriority.MEDIUM,
            resources=[
                ResourceRequirement(ResourceType.MEMORY, amount=0.3, min_amount=0.2)
            ],
            callback=test_func
        )

        # Добавляем первую задачу
        await self.resource_manager.add_task(task1)

        # Проверяем использование ресурса
        await asyncio.sleep(0.1)  # Даем время на запуск задачи
        memory_pool = self.resource_manager.resource_pools[ResourceType.MEMORY]

        self.assertGreaterEqual(memory_pool.allocated(), 0.3)  # Должно быть выделено не менее min_amount

        # Добавляем вторую задачу, она должна ожидать освобождения ресурсов
        await self.resource_manager.add_task(task2)

        # Проверяем, что вторая задача в очереди
        self.assertGreater(len(self.resource_manager.task_queue), 0)

        # Ждем завершения всех задач
        for _ in range(50):  # Максимум 5 секунд
            if not self.resource_manager.active_tasks and not self.resource_manager.task_queue:
                break
            await asyncio.sleep(0.1)

        # После завершения обеих задач ресурс должен быть освобожден
        self.assertEqual(0.0, memory_pool.allocated())

        # Обе задачи должны быть в истории
        history = self.resource_manager.get_task_history_info(limit=10)
        history_ids = [task["task_id"] for task in history]

        self.assertIn("task1", history_ids)
        self.assertIn("task2", history_ids)

    async def test_task_cancellation(self):
        """Проверка отмены задачи"""
        # Тестовая функция с длительным выполнением
        async def long_running_task():
            await asyncio.sleep(10)  # Долгая задача
            return "completed"

        # Создаем задачу
        task = Task(
            task_id="cancel_task",
            name="Task to Cancel",
            priority=TaskPriority.MEDIUM,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.1)
            ],
            callback=long_running_task
        )

        # Добавляем задачу
        await self.resource_manager.add_task(task)

        # Даем задаче время на запуск
        await asyncio.sleep(0.2)

        # Отменяем задачу
        result = await self.resource_manager.cancel_task("cancel_task")
        self.assertTrue(result)

        # Проверяем статус задачи
        task_info = self.resource_manager.get_task("cancel_task")
        self.assertEqual("canceled", task_info.status)

        # Проверяем, что ресурсы освобождены
        for resource_type in ResourceType:
            pool = self.resource_manager.resource_pools[resource_type]
            allocated = pool.allocations.get("cancel_task", 0)
            self.assertEqual(0, allocated)


# Запускаем тесты, если файл запущен напрямую
if __name__ == "__main__":
    unittest.main()
