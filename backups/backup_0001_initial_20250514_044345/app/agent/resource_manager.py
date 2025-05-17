"""
Модуль управления ресурсами для Reasoning Agent

Обеспечивает приоритизацию задач и оптимальное распределение ресурсов
для эффективного выполнения множества задач.
"""

import os
import time
import asyncio
import heapq
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Set, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from app.logger import logger


class ResourceType(Enum):
    """Типы ресурсов, которыми может управлять система"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    API_CALL = "api_call"
    LLM_CALL = "llm_call"
    BROWSER = "browser"


class TaskPriority(Enum):
    """Приоритеты задач для выполнения"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class ResourceRequirement:
    """Требование к ресурсу для выполнения задачи"""
    resource_type: ResourceType
    amount: float  # Относительное количество ресурса (0.0-1.0)
    min_amount: float = 0.1  # Минимальное необходимое количество
    can_scale: bool = True  # Может ли задача масштабироваться с доступным ресурсом


@dataclass
class Task:
    """Задача для выполнения с приоритетом и требованиями к ресурсам"""
    task_id: str
    name: str
    priority: TaskPriority
    resources: List[ResourceRequirement]
    callback: Callable[..., Awaitable[Any]]
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed, canceled, paused
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0  # Прогресс выполнения (0.0-1.0)
    dependencies: List[str] = field(default_factory=list)  # ID задач, от которых зависит эта задача
    metadata: Dict[str, Any] = field(default_factory=dict)  # Дополнительные метаданные

    # Поля для поддержки длительных операций
    is_paused: bool = False  # Флаг приостановки задачи
    can_be_paused: bool = False  # Может ли задача быть приостановлена
    intermediate_results: List[Any] = field(default_factory=list)  # Промежуточные результаты
    last_update_time: Optional[datetime] = None  # Время последнего обновления
    progress_callback: Optional[Callable[[float, Any], None]] = None  # Колбэк для обновления прогресса
    parent_task_id: Optional[str] = None  # ID родительской задачи (для подзадач)
    subtasks: List[str] = field(default_factory=list)  # Список ID подзадач

    def __lt__(self, other):
        """Сравнение для приоритетной очереди"""
        if not isinstance(other, Task):
            return NotImplemented
        return (self.priority.value, self.created_at) < (other.priority.value, other.created_at)

    def update_progress(self, progress: float, intermediate_result: Any = None) -> None:
        """
        Обновляет прогресс выполнения задачи.

        Args:
            progress: Прогресс выполнения (0.0-1.0)
            intermediate_result: Промежуточный результат (если есть)
        """
        self.progress = max(0.0, min(1.0, progress))  # Ограничиваем прогресс в диапазоне [0, 1]
        self.last_update_time = datetime.now()

        if intermediate_result is not None:
            self.intermediate_results.append(intermediate_result)

        if self.progress_callback:
            self.progress_callback(self.progress, intermediate_result)


@dataclass
class ResourceAllocation:
    """Выделение ресурса для задачи"""
    resource_type: ResourceType
    allocated_amount: float  # Фактически выделенное количество
    task_id: str


@dataclass
class ResourceMetrics:
    """Метрики использования ресурса"""
    resource_type: ResourceType
    total_capacity: float = 1.0
    allocated: float = 0.0
    peak_usage: float = 0.0
    average_usage: float = 0.0
    usage_samples: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


class ResourcePool:
    """Пул ресурсов определенного типа"""

    def __init__(self, resource_type: ResourceType, capacity: float = 1.0):
        """
        Инициализирует пул ресурсов.

        Args:
            resource_type: Тип ресурса
            capacity: Общая ёмкость ресурса (относительная величина)
        """
        self.resource_type = resource_type
        self.capacity = capacity
        self.allocations: Dict[str, float] = {}  # task_id -> allocated_amount
        self.reserved: float = 0.0  # Зарезервировано, но не активно
        self.lock = Lock()  # Для синхронизации доступа к ресурсам
        self.metrics = ResourceMetrics(resource_type=resource_type, total_capacity=capacity)

    def available(self) -> float:
        """Возвращает доступное количество ресурса"""
        return self.capacity - self.allocated() - self.reserved

    def allocated(self) -> float:
        """Возвращает выделенное количество ресурса"""
        return sum(self.allocations.values())

    def can_allocate(self, amount: float) -> bool:
        """Проверяет, можно ли выделить указанное количество ресурса"""
        return self.available() >= amount

    def allocate(self, task_id: str, amount: float) -> float:
        """
        Выделяет ресурс для задачи.

        Args:
            task_id: Идентификатор задачи
            amount: Запрашиваемое количество ресурса

        Returns:
            Фактически выделенное количество
        """
        with self.lock:
            available = self.available()
            if amount > available:
                amount = available

            if amount > 0:
                self.allocations[task_id] = amount
                self._update_metrics()
                logger.debug(f"Allocated {amount:.2f} of {self.resource_type.value} for task {task_id}")

            return amount

    def reserve(self, amount: float) -> float:
        """
        Резервирует ресурс (например, для будущих задач).

        Args:
            amount: Запрашиваемое количество ресурса

        Returns:
            Фактически зарезервированное количество
        """
        with self.lock:
            available = self.available()
            if amount > available:
                amount = available

            self.reserved += amount
            return amount

    def release_reservation(self, amount: float) -> None:
        """
        Освобождает зарезервированный ресурс.

        Args:
            amount: Количество ресурса для освобождения
        """
        with self.lock:
            amount = min(amount, self.reserved)
            self.reserved -= amount

    def release(self, task_id: str) -> float:
        """
        Освобождает ресурс, выделенный для задачи.

        Args:
            task_id: Идентификатор задачи

        Returns:
            Освобожденное количество
        """
        with self.lock:
            if task_id in self.allocations:
                amount = self.allocations.pop(task_id)
                logger.debug(f"Released {amount:.2f} of {self.resource_type.value} from task {task_id}")
                return amount
            return 0.0

    def _update_metrics(self) -> None:
        """Обновляет метрики использования ресурса"""
        current_allocated = self.allocated()

        # Обновляем метрики
        self.metrics.allocated = current_allocated
        self.metrics.peak_usage = max(self.metrics.peak_usage, current_allocated)

        # Обновляем среднее использование
        self.metrics.average_usage = (
            (self.metrics.average_usage * self.metrics.usage_samples + current_allocated) /
            (self.metrics.usage_samples + 1)
        )
        self.metrics.usage_samples += 1
        self.metrics.last_updated = datetime.now()


class ResourceManager:
    """
    Менеджер ресурсов для управления распределением и приоритизацией.

    Основные функции:
    1. Управление пулами ресурсов разных типов
    2. Приоритизация задач для выполнения
    3. Оптимальное распределение ресурсов на основе приоритетов
    4. Мониторинг использования ресурсов
    """

    def __init__(self):
        """Инициализирует менеджер ресурсов с пулами ресурсов по умолчанию"""
        self.resource_pools: Dict[ResourceType, ResourcePool] = {
            resource_type: ResourcePool(resource_type=resource_type)
            for resource_type in ResourceType
        }

        # Очередь задач, отсортированная по приоритету
        self.task_queue: List[Task] = []

        # Активные задачи
        self.active_tasks: Dict[str, Task] = {}

        # История задач
        self.task_history: Dict[str, Task] = {}

        # Максимальное количество одновременно выполняемых задач
        self.max_concurrent_tasks = 5

        # Пул потоков для выполнения длительных операций
        self.thread_pool = ThreadPoolExecutor(max_workers=5)

        # Блокировки для синхронизации
        self.queue_lock = Lock()

        # Функция проверки условий для запуска задач
        self.can_start_condition: Optional[Callable[[Task], bool]] = None

        # Система мониторинга производительности
        self.performance_monitor = None

        logger.info("ResourceManager: менеджер ресурсов инициализирован")

    def configure_resource(self, resource_type: ResourceType, capacity: float) -> None:
        """
        Настраивает ёмкость ресурса.

        Args:
            resource_type: Тип ресурса
            capacity: Общая ёмкость (относительная величина)
        """
        if resource_type in self.resource_pools:
            old_capacity = self.resource_pools[resource_type].capacity
            self.resource_pools[resource_type].capacity = capacity
            logger.info(f"ResourceManager: ёмкость ресурса {resource_type.value} изменена с {old_capacity} на {capacity}")
        else:
            self.resource_pools[resource_type] = ResourcePool(resource_type=resource_type, capacity=capacity)
            logger.info(f"ResourceManager: добавлен ресурс {resource_type.value} с ёмкостью {capacity}")

    def set_max_concurrent_tasks(self, max_tasks: int) -> None:
        """
        Устанавливает максимальное количество одновременно выполняемых задач.

        Args:
            max_tasks: Максимальное количество задач
        """
        if max_tasks < 1:
            raise ValueError("Максимальное количество задач должно быть положительным")

        old_value = self.max_concurrent_tasks
        self.max_concurrent_tasks = max_tasks
        logger.info(f"ResourceManager: максимальное количество одновременных задач изменено с {old_value} на {max_tasks}")

    def set_can_start_condition(self, condition: Optional[Callable[[Task], bool]]) -> None:
        """
        Устанавливает функцию проверки условий для запуска задач.

        Args:
            condition: Функция, принимающая задачу и возвращающая True,
                      если задача может быть запущена, или None для отключения
        """
        self.can_start_condition = condition
        logger.info(f"ResourceManager: установлено условие запуска задач: {condition.__name__ if condition else 'None'}")

    async def add_task(self, task: Task) -> str:
        """
        Добавляет задачу в очередь.

        Args:
            task: Задача для выполнения

        Returns:
            Идентификатор задачи
        """
        with self.queue_lock:
            # Проверяем зависимости
            for dep_id in task.dependencies:
                if dep_id not in self.task_history:
                    # Если зависимость еще не выполнена, задача не может быть запущена
                    logger.warning(f"ResourceManager: задача {task.name} зависит от невыполненной задачи {dep_id}")

            # Добавляем задачу в очередь
            heapq.heappush(self.task_queue, task)
            logger.info(f"ResourceManager: добавлена задача {task.name} с приоритетом {task.priority.name}")

        # Пытаемся запустить задачи из очереди
        await self._process_queue()

        return task.task_id

    async def _process_queue(self) -> None:
        """Обрабатывает очередь задач, запуская те, для которых достаточно ресурсов"""
        with self.queue_lock:
            # Если уже запущено максимальное количество задач, ничего не делаем
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return

            # Создаем копию очереди для обработки
            queue_copy = self.task_queue.copy()
            self.task_queue = []

            # Сортируем копию по приоритету
            heapq.heapify(queue_copy)

            while queue_copy and len(self.active_tasks) < self.max_concurrent_tasks:
                task = heapq.heappop(queue_copy)

                # Проверяем возможность запуска задачи
                can_start = True

                # Проверяем пользовательское условие запуска
                if self.can_start_condition and not self.can_start_condition(task):
                    can_start = False

                # Проверяем зависимости
                for dep_id in task.dependencies:
                    if dep_id not in self.task_history or self.task_history[dep_id].status != "completed":
                        can_start = False
                        break

                # Проверяем наличие ресурсов
                allocations = []
                if can_start:
                    for resource_req in task.resources:
                        pool = self.resource_pools[resource_req.resource_type]

                        # Если не хватает ресурсов для минимального требования, не запускаем задачу
                        if not pool.can_allocate(resource_req.min_amount):
                            can_start = False
                            break

                        # Пытаемся выделить ресурсы
                        requested_amount = resource_req.amount
                        allocated = pool.allocate(task.task_id, requested_amount)

                        # Если не смогли выделить достаточно и задача не масштабируемая, не запускаем
                        if allocated < requested_amount and not resource_req.can_scale:
                            # Освобождаем уже выделенные ресурсы
                            for alloc in allocations:
                                self.resource_pools[alloc.resource_type].release(task.task_id)
                            can_start = False
                            break

                        allocations.append(ResourceAllocation(
                            resource_type=resource_req.resource_type,
                            allocated_amount=allocated,
                            task_id=task.task_id
                        ))

                if can_start:
                    # Запускаем задачу
                    task.status = "running"
                    task.started_at = datetime.now()
                    self.active_tasks[task.task_id] = task

                    # Запускаем выполнение асинхронно
                    asyncio.create_task(self._execute_task(task))
                    logger.info(f"ResourceManager: запущена задача {task.name} с приоритетом {task.priority.name}")
                else:
                    # Возвращаем задачу в очередь
                    heapq.heappush(self.task_queue, task)

            # Возвращаем необработанные задачи в очередь
            for task in queue_copy:
                heapq.heappush(self.task_queue, task)

    async def _execute_task(self, task: Task) -> None:
        """
        Выполняет задачу и обрабатывает результат.

        Args:
            task: Задача для выполнения
        """
        try:
            # Устанавливаем обработчик обновления прогресса
            original_callback = task.callback
            if asyncio.iscoroutinefunction(task.callback) and hasattr(task.callback, "__self__"):
                if hasattr(task.callback.__self__, "set_progress_handler"):
                    task.callback.__self__.set_progress_handler(
                        lambda p, r: task.update_progress(p, r)
                    )

            # Создаем задачу с таймаутом, если он указан
            if task.timeout:
                try:
                    task.result = await asyncio.wait_for(
                        task.callback(*task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                except asyncio.TimeoutError:
                    task.status = "failed"
                    task.error = f"Timeout after {task.timeout} seconds"
                    logger.error(f"ResourceManager: задача {task.name} превысила таймаут {task.timeout}с")
            else:
                task.result = await task.callback(*task.args, **task.kwargs)

            # Если задача завершилась успешно
            if task.status != "failed":
                task.status = "completed"
                task.progress = 1.0  # Устанавливаем прогресс в 100%
                logger.info(f"ResourceManager: задача {task.name} успешно завершена")
        except asyncio.CancelledError:
            task.status = "canceled"
            logger.info(f"ResourceManager: задача {task.name} отменена")
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"ResourceManager: ошибка при выполнении задачи {task.name}: {str(e)}")
        finally:
            # Освобождаем ресурсы
            for resource_req in task.resources:
                self.resource_pools[resource_req.resource_type].release(task.task_id)

            # Обновляем статус задачи
            task.completed_at = datetime.now()

            # Перемещаем задачу в историю
            self.task_history[task.task_id] = task
            self.active_tasks.pop(task.task_id, None)

            # Пытаемся запустить следующие задачи из очереди
            await self._process_queue()

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Получает информацию о задаче.

        Args:
            task_id: Идентификатор задачи

        Returns:
            Задача или None, если не найдена
        """
        # Сначала ищем в активных задачах
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]

        # Затем ищем в истории
        if task_id in self.task_history:
            return self.task_history[task_id]

        # Ищем в очереди
        for task in self.task_queue:
            if task.task_id == task_id:
                return task

        return None

    async def cancel_task(self, task_id: str) -> bool:
        """
        Отменяет выполнение задачи.

        Args:
            task_id: Идентификатор задачи

        Returns:
            True, если задача была отменена, False в противном случае
        """
        # Проверяем, есть ли задача в очереди
        with self.queue_lock:
            for i, task in enumerate(self.task_queue):
                if task.task_id == task_id:
                    # Удаляем задачу из очереди
                    task.status = "canceled"
                    task.completed_at = datetime.now()
                    self.task_history[task_id] = task

                    # Пересоздаем очередь без отмененной задачи
                    new_queue = [t for t in self.task_queue if t.task_id != task_id]
                    self.task_queue = new_queue
                    heapq.heapify(self.task_queue)

                    logger.info(f"ResourceManager: задача {task.name} отменена из очереди")
                    return True

        # Проверяем, есть ли задача в активных
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "canceled"
            task.completed_at = datetime.now()

            # Освобождаем ресурсы
            for resource_req in task.resources:
                self.resource_pools[resource_req.resource_type].release(task_id)

            # Перемещаем в историю
            self.task_history[task_id] = task
            self.active_tasks.pop(task_id)

            logger.info(f"ResourceManager: активная задача {task.name} отменена")

            # Пытаемся запустить следующие задачи
            await self._process_queue()

            return True

        return False

    def get_task_queue_info(self) -> List[Dict[str, Any]]:
        """
        Получает информацию о задачах в очереди.

        Returns:
            Список с информацией о задачах
        """
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "priority": task.priority.name,
                "created_at": task.created_at.isoformat(),
                "status": task.status,
                "resources": [
                    {
                        "type": req.resource_type.value,
                        "amount": req.amount,
                        "min_amount": req.min_amount,
                        "can_scale": req.can_scale
                    }
                    for req in task.resources
                ],
                "dependencies": task.dependencies
            }
            for task in self.task_queue
        ]

    def get_active_tasks_info(self) -> List[Dict[str, Any]]:
        """
        Получает информацию об активных задачах.

        Returns:
            Список с информацией о задачах
        """
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "priority": task.priority.name,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "status": task.status,
                "progress": task.progress,
                "resources": [
                    {
                        "type": req.resource_type.value,
                        "amount": req.amount,
                        "min_amount": req.min_amount,
                        "can_scale": req.can_scale
                    }
                    for req in task.resources
                ]
            }
            for task in self.active_tasks.values()
        ]

    def get_task_history_info(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получает информацию о выполненных задачах.

        Args:
            limit: Максимальное количество задач для возврата

        Returns:
            Список с информацией о задачах
        """
        # Сортируем историю по времени завершения (от новых к старым)
        sorted_history = sorted(
            self.task_history.values(),
            key=lambda t: t.completed_at if t.completed_at else datetime.min,
            reverse=True
        )

        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "priority": task.priority.name,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "status": task.status,
                "error": task.error
            }
            for task in sorted_history[:limit]
        ]

    def get_resource_usage_info(self) -> Dict[str, Any]:
        """
        Получает информацию об использовании ресурсов.

        Returns:
            Словарь с информацией о ресурсах
        """
        return {
            resource_type.value: {
                "capacity": pool.capacity,
                "allocated": pool.allocated(),
                "available": pool.available(),
                "reserved": pool.reserved,
                "metrics": {
                    "peak_usage": pool.metrics.peak_usage,
                    "average_usage": pool.metrics.average_usage,
                    "usage_samples": pool.metrics.usage_samples,
                    "last_updated": pool.metrics.last_updated.isoformat()
                }
            }
            for resource_type, pool in self.resource_pools.items()
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Получает общую информацию о состоянии системы.

        Returns:
            Словарь с информацией о системе
        """
        return {
            "queue_length": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_history_size": len(self.task_history),
            "resources": self.get_resource_usage_info(),
            "priorities": {
                priority.name: len([t for t in self.task_queue if t.priority == priority])
                for priority in TaskPriority
            }
        }

    async def cleanup(self) -> None:
        """Освобождает ресурсы и завершает работу менеджера"""
        # Отменяем все активные задачи
        active_task_ids = list(self.active_tasks.keys())
        for task_id in active_task_ids:
            await self.cancel_task(task_id)

        # Отменяем задачи в очереди
        for task in self.task_queue:
            task.status = "canceled"
            task.completed_at = datetime.now()
            self.task_history[task.task_id] = task

        self.task_queue = []

        # Закрываем пул потоков
        self.thread_pool.shutdown(wait=True)

        # Останавливаем монитор производительности, если он активен
        if self.performance_monitor:
            await self.performance_monitor.stop_monitoring()

        logger.info("ResourceManager: менеджер ресурсов завершил работу")

    async def pause_task(self, task_id: str) -> bool:
        """
        Приостанавливает выполнение задачи, если она поддерживает приостановку.

        Args:
            task_id: Идентификатор задачи

        Returns:
            True, если задача успешно приостановлена, False в противном случае
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]

            if not task.can_be_paused:
                logger.warning(f"ResourceManager: задача {task.name} не поддерживает приостановку")
                return False

            task.is_paused = True
            task.status = "paused"
            logger.info(f"ResourceManager: задача {task.name} приостановлена")

            return True

        return False

    async def resume_task(self, task_id: str) -> bool:
        """
        Возобновляет выполнение приостановленной задачи.

        Args:
            task_id: Идентификатор задачи

        Returns:
            True, если задача успешно возобновлена, False в противном случае
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]

            if task.status != "paused":
                logger.warning(f"ResourceManager: задача {task.name} не приостановлена")
                return False

            task.is_paused = False
            task.status = "running"
            logger.info(f"ResourceManager: задача {task.name} возобновлена")

            return True

        return False

    async def create_subtask(self, parent_task_id: str, subtask: Task) -> str:
        """
        Создает подзадачу, связанную с родительской задачей.

        Args:
            parent_task_id: Идентификатор родительской задачи
            subtask: Подзадача для создания

        Returns:
            Идентификатор созданной подзадачи

        Raises:
            ValueError: Если родительская задача не существует
        """
        parent_task = self.get_task(parent_task_id)
        if parent_task is None:
            raise ValueError(f"Родительская задача {parent_task_id} не найдена")

        # Устанавливаем связь между задачами
        subtask.parent_task_id = parent_task_id
        parent_task.subtasks.append(subtask.task_id)

        # Добавляем подзадачу в очередь
        await self.add_task(subtask)

        return subtask.task_id

    def get_task_with_intermediate_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о задаче вместе с промежуточными результатами.

        Args:
            task_id: Идентификатор задачи

        Returns:
            Словарь с информацией о задаче или None, если задача не найдена
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "last_update": task.last_update_time.isoformat() if task.last_update_time else None,
            "intermediate_results": task.intermediate_results,
            "result": task.result,
            "error": task.error,
            "can_be_paused": task.can_be_paused,
            "is_paused": task.is_paused,
            "parent_task_id": task.parent_task_id,
            "subtasks": task.subtasks
        }

    async def run_long_operation(
        self,
        name: str,
        callback: Callable[..., Awaitable[Any]],
        priority: TaskPriority = TaskPriority.MEDIUM,
        resources: Optional[List[ResourceRequirement]] = None,
        can_be_paused: bool = False,
        progress_callback: Optional[Callable[[float, Any], None]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Запускает длительную операцию асинхронно с поддержкой мониторинга прогресса.

        Args:
            name: Имя операции
            callback: Функция для выполнения (должна быть асинхронной)
            priority: Приоритет операции
            resources: Требования к ресурсам
            can_be_paused: Может ли операция быть приостановлена
            progress_callback: Функция обратного вызова для обновления прогресса
            timeout: Таймаут выполнения в секундах
            **kwargs: Дополнительные аргументы для callback

        Returns:
            Идентификатор задачи
        """
        if resources is None:
            # Требования к ресурсам по умолчанию
            resources = [
                ResourceRequirement(ResourceType.CPU, amount=0.2, min_amount=0.1),
                ResourceRequirement(ResourceType.MEMORY, amount=0.2, min_amount=0.1)
            ]

        task_id = f"long_op_{int(time.time())}_{name.replace(' ', '_')}"

        task = Task(
            task_id=task_id,
            name=name,
            priority=priority,
            resources=resources,
            callback=callback,
            kwargs=kwargs,
            timeout=timeout,
            can_be_paused=can_be_paused,
            progress_callback=progress_callback
        )

        await self.add_task(task)
        logger.info(f"ResourceManager: запущена длительная операция '{name}' с ID {task_id}")

        return task_id

    def get_active_tasks_with_progress(self) -> List[Dict[str, Any]]:
        """
        Получает информацию об активных задачах с прогрессом выполнения.

        Returns:
            Список с информацией о задачах и их прогрессе
        """
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "priority": task.priority.name,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "last_update": task.last_update_time.isoformat() if task.last_update_time else None,
                "can_be_paused": task.can_be_paused,
                "is_paused": task.is_paused,
                "has_intermediate_results": len(task.intermediate_results) > 0
            }
            for task in self.active_tasks.values()
        ]

    def get_task_tree(self, root_task_id: str) -> Dict[str, Any]:
        """
        Получает дерево задач, начиная с корневой задачи.

        Args:
            root_task_id: Идентификатор корневой задачи

        Returns:
            Словарь, представляющий дерево задач
        """
        root_task = self.get_task(root_task_id)
        if root_task is None:
            return {}

        def build_task_tree(task_id: str) -> Dict[str, Any]:
            task = self.get_task(task_id)
            if task is None:
                return {}

            result = {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status,
                "progress": task.progress,
                "subtasks": []
            }

            for subtask_id in task.subtasks:
                subtask_tree = build_task_tree(subtask_id)
                if subtask_tree:
                    result["subtasks"].append(subtask_tree)

            return result

        return build_task_tree(root_task_id)

    def enable_performance_monitoring(self, monitor=None, collection_interval: int = 5) -> None:
        """
        Включает систему мониторинга производительности.

        Args:
            monitor: Экземпляр PerformanceMonitor или None для создания нового
            collection_interval: Интервал сбора метрик в секундах
        """
        # Импортируем здесь для предотвращения циклических импортов
        from app.agent.performance_monitor import PerformanceMonitor

        if not monitor:
            monitor = PerformanceMonitor(resource_manager=self)
            monitor.set_collection_interval(collection_interval)

        self.performance_monitor = monitor

        # Добавляем обработчик оповещений для логирования
        self.performance_monitor.add_alert_handler(self._handle_performance_alert)

        logger.info(f"ResourceManager: включен мониторинг производительности с интервалом {collection_interval}с")

    async def start_performance_monitoring(self) -> bool:
        """
        Запускает мониторинг производительности, если он был включен.

        Returns:
            True, если мониторинг успешно запущен, иначе False
        """
        if not self.performance_monitor:
            logger.warning("ResourceManager: не удалось запустить мониторинг - монитор не инициализирован")
            return False

        await self.performance_monitor.start_monitoring()
        logger.info("ResourceManager: запущен мониторинг производительности")
        return True

    async def stop_performance_monitoring(self) -> bool:
        """
        Останавливает мониторинг производительности.

        Returns:
            True, если мониторинг успешно остановлен, иначе False
        """
        if not self.performance_monitor:
            return False

        await self.performance_monitor.stop_monitoring()
        logger.info("ResourceManager: остановлен мониторинг производительности")
        return True

    def _handle_performance_alert(self, alert) -> None:
        """
        Обрабатывает оповещения от системы мониторинга производительности.

        Args:
            alert: Оповещение о проблеме с производительностью
        """
        # Реализуем автоматическую корректировку параметров на основе оповещений
        if alert.level.value == "critical":
            # Проверяем тип метрики и контекст
            if alert.metric_type.value == "resource_utilization":
                # Если обнаружено критическое использование ресурсов, уменьшаем максимальное число задач
                if self.max_concurrent_tasks > 1:
                    old_value = self.max_concurrent_tasks
                    self.max_concurrent_tasks -= 1
                    logger.warning(
                        f"ResourceManager: автоматическое уменьшение числа одновременных задач с {old_value} до {self.max_concurrent_tasks} "
                        f"из-за критической загрузки ресурса {alert.context.get('resource_type', 'unknown')}"
                    )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получает текущие метрики производительности.

        Returns:
            Словарь с метриками производительности или пустой словарь, если мониторинг не активен
        """
        if not self.performance_monitor:
            return {}

        return self.performance_monitor.get_performance_snapshot()

    def apply_performance_optimization(self, optimization_id: str) -> Dict[str, Any]:
        """
        Применяет рекомендацию по оптимизации производительности.

        Args:
            optimization_id: Идентификатор оптимизации

        Returns:
            Словарь с результатом применения оптимизации
        """
        if not self.performance_monitor:
            return {"success": False, "message": "Мониторинг производительности не активен"}

        # Получаем рекомендации по оптимизации
        recommendations = self.performance_monitor.get_optimization_recommendations()

        # Ищем рекомендацию по ID (который является типом рекомендации)
        matching_recommendations = [r for r in recommendations if r.get("type") == optimization_id]

        if not matching_recommendations:
            return {"success": False, "message": f"Рекомендация с ID {optimization_id} не найдена"}

        recommendation = matching_recommendations[0]

        # Применяем оптимизацию в зависимости от типа
        if optimization_id == "reduce_concurrent_tasks":
            if self.max_concurrent_tasks > 1:
                old_value = self.max_concurrent_tasks
                self.max_concurrent_tasks -= 1
                logger.info(f"ResourceManager: уменьшено число одновременных задач с {old_value} до {self.max_concurrent_tasks}")
                return {
                    "success": True,
                    "message": f"Уменьшено максимальное количество одновременных задач до {self.max_concurrent_tasks}",
                    "old_value": old_value,
                    "new_value": self.max_concurrent_tasks
                }
            else:
                return {"success": False, "message": "Нельзя уменьшить количество задач ниже 1"}

        elif optimization_id == "increase_concurrent_tasks":
            old_value = self.max_concurrent_tasks
            self.max_concurrent_tasks += 1
            logger.info(f"ResourceManager: увеличено число одновременных задач с {old_value} до {self.max_concurrent_tasks}")
            return {
                "success": True,
                "message": f"Увеличено максимальное количество одновременных задач до {self.max_concurrent_tasks}",
                "old_value": old_value,
                "new_value": self.max_concurrent_tasks
            }

        elif optimization_id == "resource_balancing":
            # Для балансировки ресурсов просто выводим рекомендацию, так как конкретные действия зависят от контекста
            return {
                "success": True,
                "message": "Рекомендация по балансировке ресурсов предоставлена. Требуется ручная настройка.",
                "details": recommendation.get("message"),
                "most_used_resource": recommendation.get("most_used_resource"),
                "least_used_resource": recommendation.get("least_used_resource")
            }

        else:
            return {"success": False, "message": f"Неизвестный тип оптимизации: {optimization_id}"}

    def export_performance_data(self, filepath: str, timespan_seconds: int = 3600) -> Dict[str, Any]:
        """
        Экспортирует данные о производительности в JSON-файл.

        Args:
            filepath: Путь к файлу для сохранения
            timespan_seconds: Период в секундах

        Returns:
            Словарь с результатом экспорта
        """
        if not self.performance_monitor:
            return {"success": False, "message": "Мониторинг производительности не активен"}

        success = self.performance_monitor.export_metrics_to_json(filepath, timespan_seconds)

        if success:
            return {
                "success": True,
                "message": f"Данные о производительности успешно экспортированы в {filepath}",
                "filepath": filepath,
                "timespan_seconds": timespan_seconds
            }
        else:
            return {"success": False, "message": f"Не удалось экспортировать данные в {filepath}"}


# Пример использования
async def demo_task(task_name: str, duration: float = 1.0) -> str:
    """Демонстрационная задача, которая просто ждет указанное время"""
    start = time.time()
    await asyncio.sleep(duration)
    end = time.time()
    return f"Задача {task_name} выполнена за {end - start:.2f} секунд"


async def main() -> None:
    """Демонстрация использования ResourceManager"""
    # Создаем менеджер ресурсов
    manager = ResourceManager()

    # Настраиваем ресурсы
    manager.configure_resource(ResourceType.CPU, 0.8)
    manager.configure_resource(ResourceType.MEMORY, 0.6)

    # Создаем несколько задач с разными приоритетами
    tasks = []
    for i in range(10):
        priority = TaskPriority.HIGH if i < 3 else TaskPriority.MEDIUM if i < 7 else TaskPriority.LOW
        task = Task(
            task_id=f"task_{i}",
            name=f"Задача {i}",
            priority=priority,
            resources=[
                ResourceRequirement(ResourceType.CPU, amount=0.2, min_amount=0.1, can_scale=True),
                ResourceRequirement(ResourceType.MEMORY, amount=0.1, min_amount=0.05, can_scale=True)
            ],
            callback=demo_task,
            args=(f"Задача {i}", 1.0 + i * 0.5),
            timeout=10.0
        )
        task_id = await manager.add_task(task)
        tasks.append(task_id)
        print(f"Добавлена задача {task.name} с ID {task_id}")

    # Ждем некоторое время для выполнения задач
    await asyncio.sleep(5)

    # Выводим статус системы
    print("\nСтатус системы:")
    status = manager.get_system_status()
    for key, value in status.items():
        if key != "resources":
            print(f"{key}: {value}")

    # Ждем завершения всех задач
    while manager.active_tasks or manager.task_queue:
        await asyncio.sleep(1)

    # Выводим историю задач
    print("\nИстория задач:")
    history = manager.get_task_history_info(limit=20)
    for task in history:
        print(f"{task['name']} - {task['status']}")

    # Завершаем работу менеджера
    await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
