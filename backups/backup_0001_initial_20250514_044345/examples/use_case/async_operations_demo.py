#!/usr/bin/env python
"""
Демонстрация асинхронного выполнения длительных операций в ReasoningAgent

Этот скрипт показывает, как использовать систему асинхронного выполнения
и управления длительными операциями с отслеживанием прогресса.
"""

import os
import sys
import asyncio
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agent.reasoning import ReasoningAgent
from app.agent.resource_manager import ResourceType, TaskPriority, ResourceRequirement


# Демонстрационные асинхронные операции с отслеживанием прогресса
async def long_computation(steps: int = 10, step_delay: float = 0.5) -> Dict[str, Any]:
    """
    Симулирует длительную вычислительную операцию с отчетами о прогрессе.

    Args:
        steps: Количество шагов вычисления
        step_delay: Задержка между шагами в секундах

    Returns:
        Результат вычислений
    """
    print(f"Начинаем длительное вычисление ({steps} шагов)")
    result = 0

    # Проверяем, имеет ли функция обработчик прогресса
    has_progress_handler = hasattr(long_computation, 'set_progress_handler')
    progress_handler = getattr(long_computation, 'progress_handler', None)

    for i in range(steps):
        # Симулируем шаг вычисления
        await asyncio.sleep(step_delay)
        result += i * i

        # Обновляем прогресс, если есть обработчик
        progress = (i + 1) / steps
        if progress_handler:
            progress_handler(progress, {"step": i + 1, "current_result": result})

        print(f"Шаг {i+1}/{steps} завершен (прогресс: {progress:.1%})")

    print(f"Вычисление завершено, результат: {result}")
    return {"result": result, "steps": steps}


async def file_processing(file_count: int = 5, size_per_file: int = 1024, step_delay: float = 0.7) -> Dict[str, Any]:
    """
    Симулирует обработку файлов с отчетами о прогрессе.

    Args:
        file_count: Количество файлов для обработки
        size_per_file: Размер каждого файла в КБ
        step_delay: Задержка между обработкой файлов

    Returns:
        Результаты обработки
    """
    print(f"Начинаем обработку {file_count} файлов")
    processed_files = []
    total_size = 0

    # Проверяем, имеет ли функция обработчик прогресса
    progress_handler = getattr(file_processing, 'progress_handler', None)

    for i in range(file_count):
        # Симулируем размер файла (с вариацией)
        file_size = size_per_file * (0.5 + random.random())
        filename = f"file_{i+1}.dat"

        print(f"Обрабатываем файл {filename} ({file_size:.1f} КБ)")
        await asyncio.sleep(step_delay)

        # Добавляем файл в результаты
        processed_files.append(filename)
        total_size += file_size

        # Обновляем прогресс и промежуточные результаты
        progress = (i + 1) / file_count
        if progress_handler:
            progress_handler(
                progress,
                {"processed_file": filename, "size": file_size, "total_processed": i+1}
            )

        print(f"Файл {filename} обработан (прогресс: {progress:.1%})")

    print(f"Обработка завершена, всего обработано {file_count} файлов ({total_size:.1f} КБ)")
    return {
        "processed_files": processed_files,
        "total_files": file_count,
        "total_size": total_size
    }


async def api_operations(api_count: int = 8, variable_delay: bool = True) -> Dict[str, Any]:
    """
    Симулирует вызовы API с переменными задержками и возможностью приостановки.

    Args:
        api_count: Количество API вызовов
        variable_delay: Использовать ли переменные задержки

    Returns:
        Результаты API вызовов
    """
    print(f"Начинаем серию из {api_count} API вызовов")
    api_results = []

    # Проверяем, имеет ли функция обработчик прогресса
    progress_handler = getattr(api_operations, 'progress_handler', None)

    # Симулируем возможность приостановки
    api_operations.can_be_paused = True
    is_paused = False

    for i in range(api_count):
        # Проверяем, не приостановлена ли операция
        while getattr(api_operations, 'is_paused', False):
            print("API операция приостановлена, ожидаем возобновления...")
            await asyncio.sleep(1)
            is_paused = True

        if is_paused:
            print("API операция возобновлена")
            is_paused = False

        # Симулируем задержку API (переменную или постоянную)
        if variable_delay:
            delay = 0.5 + random.random() * 1.5  # 0.5-2.0 seconds
        else:
            delay = 1.0

        endpoint = f"api/endpoint{i+1}"
        print(f"Вызов API {i+1}/{api_count}: {endpoint} (задержка: {delay:.1f}с)")

        # Симулируем запрос к API
        await asyncio.sleep(delay)

        # Генерируем случайный результат
        result = {
            "endpoint": endpoint,
            "status": 200,
            "data": {"id": i+1, "timestamp": datetime.now().isoformat()}
        }
        api_results.append(result)

        # Обновляем прогресс и промежуточные результаты
        progress = (i + 1) / api_count
        if progress_handler:
            progress_handler(
                progress,
                {"endpoint": endpoint, "result": result}
            )

        print(f"API вызов завершен (прогресс: {progress:.1%})")

    print(f"Все API вызовы завершены, получено {len(api_results)} результатов")
    return {
        "api_results": api_results,
        "total_calls": api_count,
        "success_rate": 1.0  # В реальном сценарии здесь был бы процент успешных вызовов
    }


# Класс с возможностью быть приостановленным для демонстрации
class PausableProcessor:
    def __init__(self, total_items: int = 20):
        self.total_items = total_items
        self.processed = 0
        self.is_paused = False
        self.progress_handler = None

    def set_progress_handler(self, handler):
        self.progress_handler = handler

    def pause(self):
        print(f"Приостановка обработки на элементе {self.processed}/{self.total_items}")
        self.is_paused = True

    def resume(self):
        print(f"Возобновление обработки с элемента {self.processed}/{self.total_items}")
        self.is_paused = False

    async def process(self) -> Dict[str, Any]:
        """Обрабатывает элементы с возможностью приостановки"""
        print(f"Начинаем обработку {self.total_items} элементов (с поддержкой приостановки)")
        results = []

        for i in range(self.total_items):
            # Проверяем, не приостановлена ли обработка
            while self.is_paused:
                await asyncio.sleep(0.5)

            # Симулируем обработку
            await asyncio.sleep(0.3)
            result = {"item": i, "status": "processed", "timestamp": datetime.now().isoformat()}
            results.append(result)

            # Обновляем состояние
            self.processed = i + 1
            progress = self.processed / self.total_items

            # Отправляем прогресс
            if self.progress_handler:
                self.progress_handler(progress, result)

            print(f"Элемент {i+1}/{self.total_items} обработан (прогресс: {progress:.1%})")

        print("Обработка всех элементов завершена")
        return {
            "processed_items": self.processed,
            "total_items": self.total_items,
            "results": results
        }


# Функция для отображения прогресса задачи
async def monitor_task_progress(agent: ReasoningAgent, task_id: str, interval: float = 1.0, max_checks: int = 60) -> None:
    """
    Отслеживает прогресс задачи и выводит информацию о нём.

    Args:
        agent: Экземпляр ReasoningAgent
        task_id: Идентификатор задачи для мониторинга
        interval: Интервал между проверками в секундах
        max_checks: Максимальное количество проверок
    """
    print(f"\nНачинаем мониторинг задачи {task_id}...")
    checks = 0
    last_progress = -1

    while checks < max_checks:
        response = await agent.get_task_status(task_id)

        if not response.get("success", False):
            print(f"Ошибка мониторинга: {response.get('error', 'Неизвестная ошибка')}")
            break

        task_info = response.get("task", {})
        status = task_info.get("status", "unknown")
        progress = task_info.get("progress", 0)

        # Выводим информацию только если прогресс изменился или статус завершения
        if progress != last_progress or status in ["completed", "failed", "canceled"]:
            print(f"Задача: {task_info.get('name', 'Неизвестная задача')}")
            print(f"Статус: {status}, Прогресс: {progress:.1%}")

            # Проверяем промежуточные результаты
            intermediate_results = task_info.get("intermediate_results", [])
            if intermediate_results and intermediate_results[-1] != getattr(monitor_task_progress, "last_result", None):
                monitor_task_progress.last_result = intermediate_results[-1]
                print(f"Промежуточный результат: {intermediate_results[-1]}")

            print("-" * 40)
            last_progress = progress

        # Если задача завершена, выходим из цикла
        if status in ["completed", "failed", "canceled"]:
            if status == "completed":
                print(f"Задача {task_id} успешно завершена!")
                print(f"Результат: {task_info.get('result', 'Нет результата')}")
            elif status == "failed":
                print(f"Задача {task_id} завершилась с ошибкой: {task_info.get('error', 'Неизвестная ошибка')}")
            else:
                print(f"Задача {task_id} была отменена")
            break

        # Ожидаем перед следующей проверкой
        await asyncio.sleep(interval)
        checks += 1

    if checks >= max_checks:
        print(f"Достигнуто максимальное количество проверок ({max_checks}) для задачи {task_id}")


async def run_demo():
    """Основная функция демонстрации"""
    print("=" * 80)
    print("Демонстрация асинхронного выполнения длительных операций")
    print("=" * 80)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    # 1. Демонстрация запуска простой длительной операции
    print("\n1. Запуск вычислительной задачи с высоким приоритетом")
    print("-" * 80)

    # Определяем требования к ресурсам
    cpu_intensive_resources = [
        ResourceRequirement(ResourceType.CPU, amount=0.5, min_amount=0.3),
        ResourceRequirement(ResourceType.MEMORY, amount=0.2, min_amount=0.1)
    ]

    # Запускаем длительную операцию
    computation_response = await agent.execute_with_priority(
        name="Длительное вычисление",
        callback=long_computation,
        priority=TaskPriority.HIGH,
        resources=cpu_intensive_resources,
        kwargs={"steps": 10, "step_delay": 0.7}
    )

    if computation_response.get("success", False):
        computation_task_id = computation_response.get("task_id")
        print(f"Задача запущена с ID: {computation_task_id}")

        # Мониторим прогресс задачи
        await monitor_task_progress(agent, computation_task_id)
    else:
        print(f"Ошибка запуска задачи: {computation_response.get('error', 'Неизвестная ошибка')}")

    # 2. Демонстрация нескольких одновременных операций с разными приоритетами
    print("\n2. Запуск нескольких параллельных задач с разными приоритетами")
    print("-" * 80)

    # Определяем разные требования к ресурсам
    io_resources = [
        ResourceRequirement(ResourceType.DISK, amount=0.4, min_amount=0.2),
        ResourceRequirement(ResourceType.CPU, amount=0.1, min_amount=0.05)
    ]

    api_resources = [
        ResourceRequirement(ResourceType.NETWORK, amount=0.6, min_amount=0.3),
        ResourceRequirement(ResourceType.API_CALL, amount=0.5, min_amount=0.2)
    ]

    # Запускаем задачи параллельно
    file_response = await agent.execute_with_priority(
        name="Обработка файлов",
        callback=file_processing,
        priority=TaskPriority.MEDIUM,
        resources=io_resources,
        kwargs={"file_count": 8, "step_delay": 0.5}
    )

    api_response = await agent.execute_with_priority(
        name="API операции",
        callback=api_operations,
        priority=TaskPriority.HIGH,
        resources=api_resources,
        can_be_paused=True,
        kwargs={"api_count": 10}
    )

    # Получаем ID задач
    file_task_id = file_response.get("task_id") if file_response.get("success", False) else None
    api_task_id = api_response.get("task_id") if api_response.get("success", False) else None

    if file_task_id and api_task_id:
        print(f"Запущены задачи: 'Обработка файлов' (ID: {file_task_id}), 'API операции' (ID: {api_task_id})")

        # Демонстрируем приостановку и возобновление задачи API
        if api_task_id:
            print("\nДемонстрация приостановки и возобновления задачи:")
            # Даем время задаче запуститься
            await asyncio.sleep(2)

            # Приостанавливаем задачу API
            pause_response = await agent.pause_resume_task(api_task_id, pause=True)
            if pause_response.get("success", False):
                print(f"{pause_response.get('message', 'Задача API приостановлена')}")

                # Ждем некоторое время
                print("Задача приостановлена на 3 секунды...")
                await asyncio.sleep(3)

                # Возобновляем задачу
                resume_response = await agent.pause_resume_task(api_task_id, pause=False)
                if resume_response.get("success", False):
                    print(f"{resume_response.get('message', 'Задача API возобновлена')}")
                else:
                    print(f"Ошибка возобновления: {resume_response.get('error', 'Неизвестная ошибка')}")
            else:
                print(f"Ошибка приостановки: {pause_response.get('error', 'Неизвестная ошибка')}")

        # Мониторим общий статус задач
        print("\nМониторинг статуса всех задач:")
        for _ in range(5):
            status_response = await agent.get_task_status()
            if status_response.get("success", False):
                active_tasks = status_response.get("active_tasks", [])
                print(f"\nАктивные задачи ({len(active_tasks)}):")
                for task in active_tasks:
                    print(f"  - {task['name']} (приоритет: {task['priority']}, прогресс: {task['progress']:.1%})")

                # Информация о ресурсах
                system_status = status_response.get("system_status", {})
                resource_info = system_status.get("resources", {})

                print("\nИспользование ресурсов:")
                for resource_name, info in resource_info.items():
                    allocated = info.get("allocated", 0)
                    capacity = info.get("capacity", 1.0)
                    usage_pct = (allocated / capacity) * 100 if capacity > 0 else 0
                    print(f"  - {resource_name}: {usage_pct:.1f}% ({allocated:.2f}/{capacity:.2f})")

            await asyncio.sleep(2)
    else:
        if not file_task_id:
            print(f"Ошибка запуска задачи обработки файлов: {file_response.get('error', 'Неизвестная ошибка')}")
        if not api_task_id:
            print(f"Ошибка запуска задачи API: {api_response.get('error', 'Неизвестная ошибка')}")

    # 3. Демонстрация группы задач
    print("\n3. Демонстрация создания группы связанных задач")
    print("-" * 80)

    # Создаем процессор с возможностью приостановки
    processor = PausableProcessor(total_items=15)

    # Создаем группу задач
    tasks = [
        {
            "name": "Вычисления (подзадача 1)",
            "callback": long_computation,
            "priority": TaskPriority.MEDIUM,
            "resources": cpu_intensive_resources,
            "kwargs": {"steps": 5, "step_delay": 0.4}
        },
        {
            "name": "Обработка данных (подзадача 2)",
            "callback": processor.process,
            "priority": TaskPriority.HIGH,
            "resources": io_resources,
            "can_be_paused": True
        }
    ]

    group_response = await agent.create_task_group("Группа задач обработки", tasks)

    if group_response.get("success", False):
        group_id = group_response.get("group_id")
        subtask_ids = group_response.get("subtask_ids", [])

        print(f"Создана группа задач с ID: {group_id}")
        print(f"Подзадачи: {', '.join(subtask_ids)}")

        # Получаем дерево задач
        await asyncio.sleep(1)  # Даем время на запуск задач
        tree_response = await agent.get_task_status(group_id)

        if tree_response.get("success", False):
            task_info = tree_response.get("task", {})
            tree = task_info.get("task_tree", {})

            print("\nДерево задач:")
            print(f"Группа: {tree.get('name', 'Группа задач')}")

            for subtask in tree.get("subtasks", []):
                print(f"  - {subtask.get('name', 'Подзадача')} (прогресс: {subtask.get('progress', 0):.1%})")

            # Приостанавливаем вторую подзадачу (если это возможно)
            if len(subtask_ids) > 1:
                processor_task_id = subtask_ids[1]

                # Даем время на запуск
                await asyncio.sleep(2)

                # Приостанавливаем обработку
                processor.pause()
                print(f"\nПриостановлена обработка для задачи {processor_task_id}")

                # Ждем некоторое время
                await asyncio.sleep(3)

                # Возобновляем обработку
                processor.resume()
                print(f"Возобновлена обработка для задачи {processor_task_id}")

            # Ждем завершения группы задач
            print("\nОжидание завершения группы задач...")
            await monitor_task_progress(agent, group_id, interval=2.0)
    else:
        print(f"Ошибка создания группы задач: {group_response.get('error', 'Неизвестная ошибка')}")

    # 4. Отображение итоговой статистики использования ресурсов
    print("\n4. Итоговая статистика использования ресурсов")
    print("-" * 80)

    usage_response = await agent.get_resource_usage()

    if usage_response.get("success", False):
        resources = usage_response.get("resources", {})

        print("Статистика использования ресурсов:")
        for resource_name, info in resources.items():
            print(f"\nРесурс: {resource_name}")
            print(f"  Емкость: {info.get('capacity', 0):.2f}")
            print(f"  Текущее использование: {info.get('allocated', 0):.2f}")

            metrics = info.get("metrics", {})
            if metrics:
                print(f"  Пиковое использование: {metrics.get('peak_usage', 0):.2f}")
                print(f"  Среднее использование: {metrics.get('average_usage', 0):.2f}")

    else:
        print(f"Ошибка получения статистики: {usage_response.get('error', 'Неизвестная ошибка')}")

    print("\nДемонстрация завершена!")
    print("=" * 80)

    # Закрываем менеджер ресурсов
    if agent.resource_manager:
        await agent.resource_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(run_demo())
