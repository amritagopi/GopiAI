#!/usr/bin/env python
"""
Демонстрация системы мониторинга производительности для ReasoningAgent

Этот скрипт показывает возможности системы мониторинга производительности,
включая сбор метрик, анализ трендов, генерацию оповещений и оптимизацию
использования ресурсов.
"""

import os
import sys
import asyncio
import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt
import numpy as np

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agent.reasoning import ReasoningAgent
from app.agent.resource_manager import ResourceType, TaskPriority, ResourceRequirement
from app.agent.performance_monitor import MetricType, AlertLevel


# Набор демонстрационных задач разной продолжительности и с разными требованиями к ресурсам
async def cpu_intensive_task(iterations: int = 5000000) -> Dict[str, Any]:
    """Симулирует CPU-интенсивную операцию"""
    print(f"Запуск CPU-интенсивной задачи ({iterations} итераций)")
    result = 0
    start_time = time.time()

    # Проверяем наличие обработчика прогресса
    progress_handler = getattr(cpu_intensive_task, 'progress_handler', None)

    for i in range(iterations):
        # Вычисляем что-то, что нагружает CPU
        result += i ** 2 % 100

        # Периодически обновляем прогресс
        if i % (iterations // 20) == 0:
            progress = i / iterations
            if progress_handler:
                progress_handler(progress, {"iteration": i})

            # Добавляем задержку для более наглядной демонстрации
            if i % (iterations // 5) == 0:
                await asyncio.sleep(0.1)

    elapsed = time.time() - start_time
    print(f"CPU-интенсивная задача завершена за {elapsed:.2f}с")
    return {"result": result, "elapsed": elapsed}


async def memory_intensive_task(memory_mb: int = 100, hold_seconds: int = 5) -> Dict[str, Any]:
    """Симулирует операцию с интенсивным использованием памяти"""
    print(f"Запуск задачи с выделением {memory_mb}MB памяти на {hold_seconds}с")

    # Создаем большой список, чтобы выделить память
    chunk_size = 1024 * 1024 // 8  # Размер float64 - 8 байт
    data = []

    progress_handler = getattr(memory_intensive_task, 'progress_handler', None)

    # Поэтапно выделяем память
    chunks = 10  # Количество чанков для заполнения
    chunk_mb = memory_mb / chunks

    for i in range(chunks):
        # Выделяем память для текущего чанка
        chunk = [random.random() for _ in range(int(chunk_mb * chunk_size))]
        data.append(chunk)

        # Обновляем прогресс
        progress = (i + 1) / (chunks + hold_seconds)
        if progress_handler:
            progress_handler(progress, {"phase": "allocation", "chunk": i+1, "allocated_mb": (i+1) * chunk_mb})

        print(f"Выделено {(i+1) * chunk_mb:.1f}MB памяти ({(i+1) / chunks:.1%})")
        await asyncio.sleep(0.2)

    print(f"Выделено {memory_mb}MB памяти, удерживаем на {hold_seconds}с")

    # Удерживаем память на указанное время
    for i in range(hold_seconds):
        await asyncio.sleep(1)
        progress = (chunks + i + 1) / (chunks + hold_seconds)
        if progress_handler:
            progress_handler(progress, {"phase": "holding", "second": i+1, "allocated_mb": memory_mb})
        print(f"Удержание памяти: {i+1}/{hold_seconds}с")

    # Освобождаем память
    data = None

    print(f"Память освобождена")
    return {"allocated_mb": memory_mb, "hold_seconds": hold_seconds}


async def io_intensive_task(file_size_mb: int = 50, file_count: int = 5) -> Dict[str, Any]:
    """Симулирует операцию с интенсивным использованием диска"""
    print(f"Запуск IO-интенсивной задачи (запись {file_count} файлов по {file_size_mb}MB)")

    # Временная директория для файлов
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp_io_test')
    os.makedirs(temp_dir, exist_ok=True)

    progress_handler = getattr(io_intensive_task, 'progress_handler', None)

    total_size = 0
    files_created = []

    for i in range(file_count):
        filename = os.path.join(temp_dir, f'test_file_{i+1}.dat')

        # Создаем файл указанного размера
        bytes_to_write = file_size_mb * 1024 * 1024
        written = 0

        print(f"Создание файла {i+1}/{file_count}: {filename}")

        with open(filename, 'wb') as f:
            # Записываем данные по частям
            chunk_size = 1024 * 1024  # 1MB
            while written < bytes_to_write:
                # Создаем случайные данные
                chunk = os.urandom(min(chunk_size, bytes_to_write - written))
                f.write(chunk)
                written += len(chunk)

                # Обновляем прогресс
                file_progress = written / bytes_to_write
                total_progress = (i + file_progress) / file_count

                if progress_handler:
                    progress_handler(total_progress, {
                        "file": i+1,
                        "file_progress": file_progress,
                        "bytes_written": written
                    })

                # Добавляем задержку для наглядности
                if random.random() < 0.2:
                    await asyncio.sleep(0.1)

        total_size += os.path.getsize(filename)
        files_created.append(filename)

        print(f"Файл {i+1}/{file_count} создан ({file_size_mb}MB)")

    # Читаем созданные файлы
    for i, filename in enumerate(files_created):
        print(f"Чтение файла {i+1}/{file_count}")

        with open(filename, 'rb') as f:
            # Читаем файл по частям
            total_size = os.path.getsize(filename)
            read_size = 0
            chunk_size = 1024 * 1024  # 1MB

            while read_size < total_size:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                read_size += len(chunk)

                # Обновляем прогресс
                file_progress = read_size / total_size
                total_progress = (file_count + i + file_progress) / (file_count * 2)

                if progress_handler:
                    progress_handler(total_progress, {
                        "phase": "reading",
                        "file": i+1,
                        "file_progress": file_progress,
                        "bytes_read": read_size
                    })

                # Добавляем задержку для наглядности
                if random.random() < 0.1:
                    await asyncio.sleep(0.1)

    # Удаляем созданные файлы
    for filename in files_created:
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Ошибка при удалении файла {filename}: {str(e)}")

    try:
        os.rmdir(temp_dir)
    except Exception as e:
        print(f"Ошибка при удалении временной директории: {str(e)}")

    print(f"IO-интенсивная задача завершена")
    return {"file_count": file_count, "file_size_mb": file_size_mb, "total_size_mb": file_count * file_size_mb}


async def network_intensive_task(requests: int = 10, data_per_request_kb: int = 500) -> Dict[str, Any]:
    """Симулирует операцию с интенсивным использованием сети"""
    print(f"Запуск задачи с имитацией сетевых запросов ({requests} запросов)")

    progress_handler = getattr(network_intensive_task, 'progress_handler', None)

    total_data = 0
    success_count = 0
    failure_count = 0

    for i in range(requests):
        # Симулируем запрос и ответ
        request_size = data_per_request_kb * 1024
        response_size = int(request_size * random.uniform(0.8, 1.5))

        # Случайная задержка для симуляции сетевой латентности
        latency = random.uniform(0.2, 1.5)
        print(f"Запрос {i+1}/{requests}: отправка {data_per_request_kb}KB, ожидание {latency:.2f}с")

        await asyncio.sleep(latency)

        # 10% шанс ошибки сети
        if random.random() < 0.1:
            failure_count += 1
            print(f"Запрос {i+1}/{requests}: ошибка сети")
        else:
            success_count += 1
            total_data += request_size + response_size
            print(f"Запрос {i+1}/{requests}: успешно, получено {response_size / 1024:.1f}KB")

        # Обновляем прогресс
        progress = (i + 1) / requests
        if progress_handler:
            progress_handler(progress, {
                "request": i+1,
                "success": success_count,
                "failures": failure_count,
                "total_data_kb": total_data / 1024
            })

    print(f"Задача с сетевыми запросами завершена: {success_count} успешных, {failure_count} ошибок")
    return {
        "requests": requests,
        "successful": success_count,
        "failed": failure_count,
        "total_data_kb": total_data / 1024
    }


async def unstable_task(steps: int = 20, failure_rate: float = 0.3) -> Dict[str, Any]:
    """Симулирует нестабильную задачу с вероятностью сбоев"""
    print(f"Запуск нестабильной задачи ({steps} шагов, вероятность сбоя {failure_rate:.1%})")

    progress_handler = getattr(unstable_task, 'progress_handler', None)

    success_steps = 0
    failed_steps = 0
    errors = []

    for i in range(steps):
        print(f"Шаг {i+1}/{steps}")

        # Случайная задержка
        delay = random.uniform(0.1, 0.8)
        await asyncio.sleep(delay)

        # Проверка на сбой
        if random.random() < failure_rate:
            failed_steps += 1
            error_msg = f"Ошибка на шаге {i+1}"
            errors.append(error_msg)
            print(f"Шаг {i+1}/{steps}: {error_msg}")

            # Иногда делаем повторные попытки
            if random.random() < 0.5:
                retry_count = random.randint(1, 3)
                for r in range(retry_count):
                    print(f"Повторная попытка {r+1}/{retry_count} для шага {i+1}")
                    await asyncio.sleep(delay / 2)

                    if random.random() > failure_rate:
                        success_steps += 1
                        print(f"Повторная попытка успешна")
                        break
                    else:
                        error_msg = f"Ошибка повторной попытки {r+1} для шага {i+1}"
                        errors.append(error_msg)
                        print(error_msg)
        else:
            success_steps += 1
            print(f"Шаг {i+1}/{steps}: успешно")

        # Обновляем прогресс
        progress = (i + 1) / steps
        if progress_handler:
            progress_handler(progress, {
                "step": i+1,
                "success_steps": success_steps,
                "failed_steps": failed_steps,
                "current_error_rate": failed_steps / (success_steps + failed_steps) if (success_steps + failed_steps) > 0 else 0
            })

    error_rate = failed_steps / steps
    result = {
        "steps": steps,
        "success_steps": success_steps,
        "failed_steps": failed_steps,
        "error_rate": error_rate,
        "errors": errors
    }

    print(f"Нестабильная задача завершена: успешно {success_steps}/{steps}, ошибок {failed_steps}")
    return result


async def visualize_metrics(performance_data, output_dir: str = None):
    """Визуализирует метрики производительности"""
    # Создаем директорию для графиков, если она не существует
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'performance_charts')
    os.makedirs(output_dir, exist_ok=True)

    # Проверяем наличие данных
    if not performance_data or not isinstance(performance_data, dict):
        print("Нет данных для визуализации")
        return

    # Визуализация использования ресурсов
    resources_data = performance_data.get("resources", {})
    if resources_data:
        plt.figure(figsize=(12, 6))

        resource_types = list(resources_data.keys())
        resource_usage = [resources_data[r].get("average", 0) * 100 for r in resource_types]

        plt.bar(resource_types, resource_usage, color='skyblue')
        plt.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Порог предупреждения')
        plt.axhline(y=95, color='darkred', linestyle='--', alpha=0.7, label='Критический порог')

        plt.xlabel('Тип ресурса')
        plt.ylabel('Использование (%)')
        plt.title('Среднее использование ресурсов')
        plt.ylim(0, 100)
        plt.legend()
        plt.tight_layout()

        # Сохраняем график
        plt.savefig(os.path.join(output_dir, 'resource_usage.png'))
        print(f"График использования ресурсов сохранен: {os.path.join(output_dir, 'resource_usage.png')}")

    # Визуализация системных метрик
    system_data = performance_data.get("system", {})
    if system_data:
        plt.figure(figsize=(12, 8))

        # Строим графики для CPU и памяти
        system_cpu = system_data.get("system_cpu", {})
        system_memory = system_data.get("system_memory", {})

        metrics = ['average', 'max', 'min', 'current']
        cpu_values = [system_cpu.get(m, 0) * 100 for m in metrics]
        memory_values = [system_memory.get(m, 0) * 100 for m in metrics]

        plt.subplot(2, 1, 1)
        plt.bar(metrics, cpu_values, color='orange')
        plt.title('Использование CPU')
        plt.ylabel('Процент (%)')
        plt.ylim(0, 100)

        plt.subplot(2, 1, 2)
        plt.bar(metrics, memory_values, color='green')
        plt.title('Использование памяти')
        plt.ylabel('Процент (%)')
        plt.ylim(0, 100)

        plt.tight_layout()

        # Сохраняем график
        plt.savefig(os.path.join(output_dir, 'system_metrics.png'))
        print(f"График системных метрик сохранен: {os.path.join(output_dir, 'system_metrics.png')}")

    # Визуализация оповещений по уровню важности
    recent_alerts = performance_data.get("recent_alerts", [])
    if recent_alerts:
        alert_levels = {}
        for alert in recent_alerts:
            level = alert.get("level", "unknown")
            alert_levels[level] = alert_levels.get(level, 0) + 1

        plt.figure(figsize=(10, 5))

        levels = list(alert_levels.keys())
        counts = [alert_levels[level] for level in levels]

        # Назначаем цвета в зависимости от уровня
        colors = []
        for level in levels:
            if level == "critical":
                colors.append("darkred")
            elif level == "warning":
                colors.append("orange")
            else:
                colors.append("blue")

        plt.bar(levels, counts, color=colors)
        plt.xlabel('Уровень оповещения')
        plt.ylabel('Количество')
        plt.title('Оповещения по уровню важности')
        plt.tight_layout()

        # Сохраняем график
        plt.savefig(os.path.join(output_dir, 'alerts_by_level.png'))
        print(f"График оповещений сохранен: {os.path.join(output_dir, 'alerts_by_level.png')}")

    print(f"Визуализация метрик завершена, графики сохранены в директорию: {output_dir}")


async def create_stress_test(agent: ReasoningAgent) -> None:
    """Запускает набор задач для создания нагрузки и генерации метрик"""
    print("\nЗапуск стресс-теста для сбора метрик производительности")
    print("=" * 80)

    # Определяем требования к ресурсам для разных типов задач
    cpu_resources = [
        ResourceRequirement(ResourceType.CPU, amount=0.7, min_amount=0.5),
        ResourceRequirement(ResourceType.MEMORY, amount=0.2, min_amount=0.1)
    ]

    memory_resources = [
        ResourceRequirement(ResourceType.MEMORY, amount=0.6, min_amount=0.4),
        ResourceRequirement(ResourceType.CPU, amount=0.2, min_amount=0.1)
    ]

    io_resources = [
        ResourceRequirement(ResourceType.DISK, amount=0.8, min_amount=0.5),
        ResourceRequirement(ResourceType.CPU, amount=0.1, min_amount=0.05)
    ]

    network_resources = [
        ResourceRequirement(ResourceType.NETWORK, amount=0.7, min_amount=0.4),
        ResourceRequirement(ResourceType.API_CALL, amount=0.5, min_amount=0.3)
    ]

    # Создаем несколько параллельных задач разных типов
    task_responses = []

    # CPU-интенсивные задачи
    print("\nЗапуск CPU-интенсивных задач")
    for i in range(3):
        response = await agent.execute_with_priority(
            name=f"CPU задача {i+1}",
            callback=cpu_intensive_task,
            priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
            resources=cpu_resources,
            kwargs={"iterations": random.randint(3000000, 7000000)}
        )
        if response.get("success", False):
            task_responses.append({
                "task_id": response.get("task_id"),
                "name": f"CPU задача {i+1}",
                "type": "cpu"
            })
            print(f"Запущена CPU задача {i+1} с ID: {response.get('task_id')}")

    # Задачи с интенсивным использованием памяти
    print("\nЗапуск задач с интенсивным использованием памяти")
    for i in range(2):
        response = await agent.execute_with_priority(
            name=f"Память задача {i+1}",
            callback=memory_intensive_task,
            priority=TaskPriority.MEDIUM,
            resources=memory_resources,
            kwargs={
                "memory_mb": random.randint(50, 200),
                "hold_seconds": random.randint(3, 8)
            }
        )
        if response.get("success", False):
            task_responses.append({
                "task_id": response.get("task_id"),
                "name": f"Память задача {i+1}",
                "type": "memory"
            })
            print(f"Запущена задача с использованием памяти {i+1} с ID: {response.get('task_id')}")

    # IO-интенсивные задачи
    print("\nЗапуск IO-интенсивных задач")
    for i in range(2):
        response = await agent.execute_with_priority(
            name=f"IO задача {i+1}",
            callback=io_intensive_task,
            priority=TaskPriority.LOW,
            resources=io_resources,
            kwargs={
                "file_size_mb": random.randint(10, 30),
                "file_count": random.randint(3, 7)
            }
        )
        if response.get("success", False):
            task_responses.append({
                "task_id": response.get("task_id"),
                "name": f"IO задача {i+1}",
                "type": "io"
            })
            print(f"Запущена IO задача {i+1} с ID: {response.get('task_id')}")

    # Задачи с интенсивным использованием сети
    print("\nЗапуск задач с имитацией сетевых запросов")
    for i in range(2):
        response = await agent.execute_with_priority(
            name=f"Сеть задача {i+1}",
            callback=network_intensive_task,
            priority=TaskPriority.MEDIUM,
            resources=network_resources,
            kwargs={
                "requests": random.randint(8, 15),
                "data_per_request_kb": random.randint(200, 800)
            }
        )
        if response.get("success", False):
            task_responses.append({
                "task_id": response.get("task_id"),
                "name": f"Сеть задача {i+1}",
                "type": "network"
            })
            print(f"Запущена задача с сетевыми запросами {i+1} с ID: {response.get('task_id')}")

    # Нестабильные задачи для генерации ошибок
    print("\nЗапуск нестабильных задач")
    for i in range(2):
        failure_rate = 0.4 if i == 0 else 0.2
        response = await agent.execute_with_priority(
            name=f"Нестабильная задача {i+1}",
            callback=unstable_task,
            priority=TaskPriority.LOW,
            resources=[],  # Без специфических требований к ресурсам
            kwargs={
                "steps": random.randint(15, 25),
                "failure_rate": failure_rate
            }
        )
        if response.get("success", False):
            task_responses.append({
                "task_id": response.get("task_id"),
                "name": f"Нестабильная задача {i+1}",
                "type": "unstable"
            })
            print(f"Запущена нестабильная задача {i+1} с ID: {response.get('task_id')}")

    # Ожидаем некоторое время для сбора метрик
    print("\nОжидание выполнения задач и сбора метрик...")

    # Периодически проверяем статус задач
    active_tasks = task_responses.copy()
    completed_tasks = []

    while active_tasks:
        await asyncio.sleep(2)

        # Получаем статус всех задач
        for task in active_tasks[:]:
            status_response = await agent.get_task_status(task["task_id"])

            if status_response.get("success", False):
                task_info = status_response.get("task", {})
                status = task_info.get("status", "unknown")

                if status in ["completed", "failed", "canceled"]:
                    print(f"Задача {task['name']} ({task['task_id']}) завершена со статусом: {status}")
                    active_tasks.remove(task)
                    completed_tasks.append({
                        **task,
                        "status": status,
                        "completion_time": datetime.now().isoformat()
                    })

        # Выводим количество оставшихся задач
        if active_tasks:
            print(f"Осталось активных задач: {len(active_tasks)}")

    print("\nВсе задачи завершены")
    print(f"Успешно завершено: {len([t for t in completed_tasks if t['status'] == 'completed'])}")
    print(f"Завершено с ошибкой: {len([t for t in completed_tasks if t['status'] == 'failed'])}")

    # Возвращаемся для дальнейшего анализа


async def run_demo():
    """Основная функция демонстрации"""
    print("=" * 80)
    print("Демонстрация системы мониторинга производительности")
    print("=" * 80)

    # Создаем временную директорию для экспорта данных
    output_dir = os.path.join(os.path.dirname(__file__), 'performance_data')
    os.makedirs(output_dir, exist_ok=True)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    # Проверяем, активен ли мониторинг производительности
    metrics_response = await agent.get_performance_metrics()
    if not metrics_response.get("success", False):
        print("Мониторинг производительности не активен. Включение...")

        # Включаем мониторинг вручную через ResourceManager
        agent.resource_manager.enable_performance_monitoring(collection_interval=3)
        await agent.resource_manager.start_performance_monitoring()

        print("Мониторинг производительности включен")
    else:
        print("Мониторинг производительности уже активен")

    # 1. Проверка текущего состояния производительности
    print("\n1. Проверка текущего состояния производительности")
    print("-" * 80)

    baseline_response = await agent.get_performance_metrics()
    if baseline_response.get("success", False):
        baseline_data = baseline_response.get("performance_data", {})

        print("\nБазовые метрики производительности:")
        for resource_type, data in baseline_data.get("resources", {}).items():
            print(f"  {resource_type}: {data.get('current', 0)*100:.1f}% (Средн.: {data.get('average', 0)*100:.1f}%)")

        print("\nСистемные метрики:")
        for name, data in baseline_data.get("system", {}).items():
            if name == "system_cpu" or name == "system_memory":
                print(f"  {name}: {data.get('current', 0)*100:.1f}% (Max: {data.get('max', 0)*100:.1f}%)")

        # Проверяем наличие оповещений
        alerts = baseline_data.get("recent_alerts", [])
        if alerts:
            print("\nПоследние оповещения:")
            for alert in alerts[:3]:  # Показываем только 3 последних оповещения
                print(f"  [{alert.get('level', 'unknown')}] {alert.get('message', '')}")
        else:
            print("\nНет активных оповещений")
    else:
        print(f"Ошибка при получении метрик: {baseline_response.get('error', 'Неизвестная ошибка')}")

    # 2. Создание нагрузки для сбора метрик
    print("\n2. Создание нагрузки для сбора метрик производительности")
    print("-" * 80)

    await create_stress_test(agent)

    # 3. Анализ собранных метрик
    print("\n3. Анализ собранных метрик и рекомендации по оптимизации")
    print("-" * 80)

    metrics_response = await agent.get_performance_metrics()
    if metrics_response.get("success", False):
        performance_data = metrics_response.get("performance_data", {})

        # Проверяем рекомендации по оптимизации
        recommendations = performance_data.get("optimization_recommendations", [])

        if recommendations:
            print("\nРекомендации по оптимизации производительности:")
            for i, rec in enumerate(recommendations):
                print(f"  {i+1}. {rec.get('message', '')}")
                print(f"     Приоритет: {rec.get('priority', 'medium')}")
                print(f"     Тип: {rec.get('type', 'unknown')}")
                if rec.get('current_value') is not None and rec.get('suggested_value') is not None:
                    print(f"     Текущее значение: {rec.get('current_value')}, Рекомендуемое: {rec.get('suggested_value')}")
                print()

            # Применяем первую рекомендацию (если есть)
            if recommendations and len(recommendations) > 0:
                opt_type = recommendations[0].get("type")
                if opt_type:
                    print(f"\nПрименение рекомендации: {opt_type}")
                    opt_response = await agent.apply_performance_optimization(opt_type)

                    if opt_response.get("success", False):
                        print(f"Оптимизация успешно применена: {opt_response.get('message', '')}")
                    else:
                        print(f"Ошибка при применении оптимизации: {opt_response.get('error', 'Неизвестная ошибка')}")
        else:
            print("\nРекомендации по оптимизации отсутствуют")

        # Экспортируем данные о производительности
        export_file = os.path.join(output_dir, 'performance_metrics.json')
        export_response = await agent.export_performance_data(export_file)

        if export_response.get("success", False):
            print(f"\nДанные о производительности экспортированы: {export_file}")
        else:
            print(f"\nОшибка при экспорте данных: {export_response.get('error', 'Неизвестная ошибка')}")

        # Визуализируем метрики
        await visualize_metrics(performance_data, output_dir)
    else:
        print(f"Ошибка при получении метрик: {metrics_response.get('error', 'Неизвестная ошибка')}")

    # 4. Получение полного отчета о ресурсах
    print("\n4. Формирование полного отчета об использовании ресурсов")
    print("-" * 80)

    report_response = await agent.get_resource_usage_report()

    if report_response.get("success", False):
        report = report_response

        print(f"\nОтчет об использовании ресурсов ({report.get('timestamp', '')})")
        print(f"Всего ресурсов: {report.get('summary', {}).get('total_resources', 0)}")
        print(f"Активных задач: {report.get('summary', {}).get('active_tasks', 0)}")
        print(f"Задач в очереди: {report.get('summary', {}).get('queued_tasks', 0)}")

        # Выводим информацию по каждому ресурсу
        print("\nИспользование ресурсов:")
        for resource_type, info in report.get("resources", {}).items():
            utilization = info.get("allocated", 0) / info.get("capacity", 1) if info.get("capacity", 0) > 0 else 0
            print(f"  {resource_type}: {utilization*100:.1f}% ({info.get('allocated', 0):.2f}/{info.get('capacity', 0):.2f})")

        # Выводим рекомендации
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\nРекомендации:")
            for i, rec in enumerate(recommendations):
                print(f"  {i+1}. [{rec.get('priority', 'medium')}] {rec.get('message', '')}")

        # Сохраняем отчет в JSON
        report_file = os.path.join(output_dir, 'resource_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nПолный отчет сохранен: {report_file}")
    else:
        print(f"Ошибка при формировании отчета: {report_response.get('error', 'Неизвестная ошибка')}")

    # Закрываем менеджер ресурсов
    print("\nЗавершение работы менеджера ресурсов...")
    if agent.resource_manager:
        await agent.resource_manager.cleanup()

    print("\nДемонстрация завершена!")
    print("=" * 80)
    print(f"Все данные и графики сохранены в директории: {output_dir}")


if __name__ == "__main__":
    asyncio.run(run_demo())
