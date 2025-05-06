"""
Модуль мониторинга производительности для ReasoningAgent

Обеспечивает сбор, анализ и визуализацию метрик производительности
для оптимизации использования ресурсов и выявления узких мест.
"""

import os
import time
import json
import asyncio
import threading
import psutil
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
import logging
import statistics
from collections import deque

from app.agent.resource_manager import ResourceType, ResourceManager
from app.logger import logger


class MetricType(Enum):
    """Типы отслеживаемых метрик"""
    CPU_USAGE = "cpu_usage"  # Использование CPU
    MEMORY_USAGE = "memory_usage"  # Использование памяти
    DISK_IO = "disk_io"  # Операции ввода-вывода диска
    NETWORK_IO = "network_io"  # Сетевые операции
    TASK_THROUGHPUT = "task_throughput"  # Пропускная способность задач
    RESPONSE_TIME = "response_time"  # Время отклика
    RESOURCE_UTILIZATION = "resource_utilization"  # Эффективность использования ресурса
    ERROR_RATE = "error_rate"  # Частота ошибок


class AlertLevel(Enum):
    """Уровни важности оповещений о производительности"""
    INFO = "info"  # Информационное сообщение
    WARNING = "warning"  # Предупреждение
    CRITICAL = "critical"  # Критическое состояние


@dataclass
class PerformanceMetric:
    """Метрика производительности с временной меткой"""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Оповещение о проблеме с производительностью"""
    metric_type: MetricType
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    current_value: float = 0.0
    threshold: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetricsHistory:
    """История метрик для конкретного ресурса"""
    resource_type: ResourceType
    metrics: List[PerformanceMetric] = field(default_factory=list)
    max_history_size: int = 1000

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Добавляет метрику в историю с ограничением размера"""
        self.metrics.append(metric)
        # Удаляем старые метрики, если превышен максимальный размер
        if len(self.metrics) > self.max_history_size:
            self.metrics = self.metrics[-self.max_history_size:]

    def get_recent_metrics(self, count: int = 10) -> List[PerformanceMetric]:
        """Возвращает последние N метрик"""
        return self.metrics[-count:] if count < len(self.metrics) else self.metrics.copy()

    def get_metrics_in_timespan(self, start_time: datetime, end_time: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Возвращает метрики в указанном временном интервале"""
        if end_time is None:
            end_time = datetime.now()
        return [m for m in self.metrics if start_time <= m.timestamp <= end_time]

    def calculate_average(self, timespan_seconds: int = 60) -> float:
        """Вычисляет среднее значение метрик за указанный период в секундах"""
        start_time = datetime.now() - timedelta(seconds=timespan_seconds)
        metrics_in_timespan = self.get_metrics_in_timespan(start_time)
        if not metrics_in_timespan:
            return 0.0
        return sum(m.value for m in metrics_in_timespan) / len(metrics_in_timespan)


class PerformanceMonitor:
    """
    Система мониторинга производительности для ReasoningAgent.

    Отвечает за:
    1. Сбор метрик использования ресурсов в реальном времени
    2. Анализ трендов и выявление аномалий
    3. Генерацию оповещений при обнаружении проблем
    4. Рекомендации по оптимизации использования ресурсов
    5. Визуализацию и экспорт данных мониторинга
    """

    def __init__(self, resource_manager: Optional[ResourceManager] = None):
        """
        Инициализирует монитор производительности.

        Args:
            resource_manager: Менеджер ресурсов для мониторинга (если None, будет использоваться независимый мониторинг)
        """
        self.resource_manager = resource_manager
        self.metrics_history: Dict[ResourceType, ResourceMetricsHistory] = {
            resource_type: ResourceMetricsHistory(resource_type=resource_type)
            for resource_type in ResourceType
        }

        # Добавляем отслеживание системных ресурсов
        self.system_metrics: Dict[str, ResourceMetricsHistory] = {
            "system_cpu": ResourceMetricsHistory(ResourceType.CPU),
            "system_memory": ResourceMetricsHistory(ResourceType.MEMORY),
            "system_disk": ResourceMetricsHistory(ResourceType.DISK),
            "system_network": ResourceMetricsHistory(ResourceType.NETWORK)
        }

        # Очередь оповещений
        self.alerts: List[PerformanceAlert] = []

        # Настройки пороговых значений для генерации оповещений
        self.alert_thresholds: Dict[MetricType, Dict[AlertLevel, float]] = {
            MetricType.CPU_USAGE: {
                AlertLevel.WARNING: 0.75,  # 75%
                AlertLevel.CRITICAL: 0.9   # 90%
            },
            MetricType.MEMORY_USAGE: {
                AlertLevel.WARNING: 0.8,   # 80%
                AlertLevel.CRITICAL: 0.95  # 95%
            },
            MetricType.RESOURCE_UTILIZATION: {
                AlertLevel.WARNING: 0.85,  # 85%
                AlertLevel.CRITICAL: 0.95  # 95%
            },
            MetricType.ERROR_RATE: {
                AlertLevel.WARNING: 0.05,  # 5%
                AlertLevel.CRITICAL: 0.15  # 15%
            }
        }

        # Индикатор работы мониторинга
        self._running = False
        self._collection_interval = 5  # Интервал сбора метрик в секундах
        self._monitoring_task = None
        self._lock = threading.Lock()

        # Счетчики и агрегированные метрики
        self.task_completion_times: Dict[str, float] = {}
        self.task_error_counts: Dict[str, int] = {
            "total": 0,
            "timeout": 0,
            "resource_error": 0,
            "task_error": 0
        }
        self.last_optimization_check = datetime.now()

        # Обработчики оповещений
        self.alert_handlers: List[Callable[[PerformanceAlert], None]] = []

        logger.info("PerformanceMonitor: система мониторинга производительности инициализирована")

    async def start_monitoring(self) -> None:
        """Запускает мониторинг производительности в фоновом режиме"""
        if self._running:
            logger.warning("PerformanceMonitor: мониторинг уже запущен")
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("PerformanceMonitor: запущен мониторинг производительности")

    async def stop_monitoring(self) -> None:
        """Останавливает мониторинг производительности"""
        if not self._running:
            return

        self._running = False
        if self._monitoring_task:
            try:
                self._monitoring_task.cancel()
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                pass

        logger.info("PerformanceMonitor: мониторинг производительности остановлен")

    async def _monitoring_loop(self) -> None:
        """Основной цикл сбора метрик производительности"""
        try:
            while self._running:
                await self._collect_resource_manager_metrics()
                await self._collect_system_metrics()
                await self._analyze_metrics()

                # Проверяем необходимость оптимизации раз в минуту
                if (datetime.now() - self.last_optimization_check).total_seconds() > 60:
                    await self._check_for_optimizations()
                    self.last_optimization_check = datetime.now()

                await asyncio.sleep(self._collection_interval)
        except asyncio.CancelledError:
            logger.info("PerformanceMonitor: цикл мониторинга отменен")
        except Exception as e:
            logger.error(f"PerformanceMonitor: ошибка в цикле мониторинга: {str(e)}")

    async def _collect_resource_manager_metrics(self) -> None:
        """Собирает метрики из ResourceManager, если он доступен"""
        if not self.resource_manager:
            return

        try:
            # Получаем информацию об использовании ресурсов
            for resource_type, pool in self.resource_manager.resource_pools.items():
                # Использование ресурса
                utilization = pool.allocated() / pool.capacity if pool.capacity > 0 else 0

                # Создаем и сохраняем метрику
                metric = PerformanceMetric(
                    metric_type=MetricType.RESOURCE_UTILIZATION,
                    value=utilization,
                    context={
                        "resource_type": resource_type.value,
                        "allocated": pool.allocated(),
                        "capacity": pool.capacity,
                        "available": pool.available()
                    }
                )

                self.metrics_history[resource_type].add_metric(metric)

                # Проверяем необходимость генерации оповещений
                self._check_alert_threshold(metric)

            # Собираем метрики о задачах
            active_tasks = len(self.resource_manager.active_tasks)
            queued_tasks = len(self.resource_manager.task_queue)

            # Метрика пропускной способности задач
            throughput_metric = PerformanceMetric(
                metric_type=MetricType.TASK_THROUGHPUT,
                value=active_tasks,
                context={
                    "active_tasks": active_tasks,
                    "queued_tasks": queued_tasks,
                    "max_concurrent": self.resource_manager.max_concurrent_tasks
                }
            )

            # Добавляем в историю CPU как наиболее близкого ресурса
            self.metrics_history[ResourceType.CPU].add_metric(throughput_metric)

            # Анализ времени выполнения задач
            for task_id, task in self.resource_manager.task_history.items():
                if task.status in ["completed", "failed"] and task_id not in self.task_completion_times:
                    if task.started_at and task.completed_at:
                        execution_time = (task.completed_at - task.started_at).total_seconds()
                        self.task_completion_times[task_id] = execution_time

                        # Метрика времени отклика
                        response_metric = PerformanceMetric(
                            metric_type=MetricType.RESPONSE_TIME,
                            value=execution_time,
                            context={
                                "task_id": task_id,
                                "task_name": task.name,
                                "priority": task.priority.value,
                                "status": task.status
                            }
                        )

                        # Добавляем в общую историю
                        for resource_req in task.resources:
                            self.metrics_history[resource_req.resource_type].add_metric(response_metric)

                    # Учет ошибок
                    if task.status == "failed":
                        self.task_error_counts["total"] += 1
                        if task.error and "timeout" in task.error.lower():
                            self.task_error_counts["timeout"] += 1
                        else:
                            self.task_error_counts["task_error"] += 1

                        # Метрика частоты ошибок
                        total_tasks = len(self.resource_manager.task_history)
                        error_rate = self.task_error_counts["total"] / total_tasks if total_tasks > 0 else 0

                        error_metric = PerformanceMetric(
                            metric_type=MetricType.ERROR_RATE,
                            value=error_rate,
                            context={
                                "total_tasks": total_tasks,
                                "total_errors": self.task_error_counts["total"],
                                "error_type": "timeout" if "timeout" in task.error.lower() else "task_error"
                            }
                        )

                        # Добавляем во все ресурсы
                        for resource_type in ResourceType:
                            self.metrics_history[resource_type].add_metric(error_metric)

                        # Проверяем превышение порога ошибок
                        self._check_alert_threshold(error_metric)

        except Exception as e:
            logger.error(f"PerformanceMonitor: ошибка при сборе метрик ResourceManager: {str(e)}")

    async def _collect_system_metrics(self) -> None:
        """Собирает системные метрики с помощью psutil"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100  # Преобразуем в диапазон 0-1
            cpu_metric = PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=cpu_percent,
                context={"cores": psutil.cpu_count()}
            )
            self.system_metrics["system_cpu"].add_metric(cpu_metric)

            # Память
            memory = psutil.virtual_memory()
            memory_usage = memory.percent / 100  # Преобразуем в диапазон 0-1
            memory_metric = PerformanceMetric(
                metric_type=MetricType.MEMORY_USAGE,
                value=memory_usage,
                context={
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3)
                }
            )
            self.system_metrics["system_memory"].add_metric(memory_metric)

            # Диск
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent / 100  # Преобразуем в диапазон 0-1
            disk_metric = PerformanceMetric(
                metric_type=MetricType.DISK_IO,
                value=disk_usage,
                context={
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3)
                }
            )
            self.system_metrics["system_disk"].add_metric(disk_metric)

            # Сеть (только счетчик байт, без процентов)
            network = psutil.net_io_counters()
            network_metric = PerformanceMetric(
                metric_type=MetricType.NETWORK_IO,
                value=0.0,  # Здесь нет процентного значения
                context={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            )
            self.system_metrics["system_network"].add_metric(network_metric)

            # Проверка пороговых значений для системных метрик
            self._check_alert_threshold(cpu_metric)
            self._check_alert_threshold(memory_metric)

        except Exception as e:
            logger.error(f"PerformanceMonitor: ошибка при сборе системных метрик: {str(e)}")

    def _check_alert_threshold(self, metric: PerformanceMetric) -> None:
        """
        Проверяет, превышает ли метрика пороговые значения для оповещений.

        Args:
            metric: Метрика для проверки
        """
        if metric.metric_type not in self.alert_thresholds:
            return

        thresholds = self.alert_thresholds[metric.metric_type]

        # Проверяем критический уровень, затем предупреждающий
        if metric.value >= thresholds.get(AlertLevel.CRITICAL, float('inf')):
            self._create_alert(
                metric_type=metric.metric_type,
                level=AlertLevel.CRITICAL,
                message=f"Критическое значение {metric.metric_type.value}: {metric.value:.2f}",
                current_value=metric.value,
                threshold=thresholds.get(AlertLevel.CRITICAL, 0),
                context=metric.context
            )
        elif metric.value >= thresholds.get(AlertLevel.WARNING, float('inf')):
            self._create_alert(
                metric_type=metric.metric_type,
                level=AlertLevel.WARNING,
                message=f"Предупреждение: высокое значение {metric.metric_type.value}: {metric.value:.2f}",
                current_value=metric.value,
                threshold=thresholds.get(AlertLevel.WARNING, 0),
                context=metric.context
            )

    def _create_alert(self, metric_type: MetricType, level: AlertLevel, message: str,
                     current_value: float, threshold: float, context: Dict[str, Any]) -> None:
        """
        Создает оповещение о проблеме с производительностью.

        Args:
            metric_type: Тип метрики
            level: Уровень важности
            message: Сообщение оповещения
            current_value: Текущее значение метрики
            threshold: Пороговое значение
            context: Контекст оповещения
        """
        alert = PerformanceAlert(
            metric_type=metric_type,
            level=level,
            message=message,
            current_value=current_value,
            threshold=threshold,
            context=context
        )

        self.alerts.append(alert)

        # Ограничиваем историю оповещений
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # Логируем оповещение
        log_message = f"PerformanceAlert [{level.value}]: {message}"
        if level == AlertLevel.CRITICAL:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Вызываем обработчики оповещений
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"PerformanceMonitor: ошибка в обработчике оповещений: {str(e)}")

    async def _analyze_metrics(self) -> None:
        """Анализирует собранные метрики для выявления трендов и аномалий"""
        # Анализ каждого типа ресурса
        for resource_type, history in self.metrics_history.items():
            # Получаем последние метрики
            recent_metrics = history.get_recent_metrics(20)
            if len(recent_metrics) < 5:  # Нужно минимальное количество метрик для анализа
                continue

            # Анализ тренда использования ресурса
            recent_values = [m.value for m in recent_metrics]

            # Проверка на устойчивый рост (каждое следующее значение больше предыдущего)
            is_increasing = all(recent_values[i] <= recent_values[i+1] for i in range(len(recent_values)-1))

            # Проверка на устойчивое снижение
            is_decreasing = all(recent_values[i] >= recent_values[i+1] for i in range(len(recent_values)-1))

            # Вычисляем стандартное отклонение для обнаружения нестабильности
            if len(recent_values) > 1:
                std_dev = statistics.stdev(recent_values)
                mean_value = statistics.mean(recent_values)

                # Высокая вариативность может указывать на проблемы
                if std_dev > 0.2 and mean_value > 0.5:
                    self._create_alert(
                        metric_type=MetricType.RESOURCE_UTILIZATION,
                        level=AlertLevel.WARNING,
                        message=f"Нестабильное использование ресурса {resource_type.value}",
                        current_value=std_dev,
                        threshold=0.2,
                        context={
                            "resource_type": resource_type.value,
                            "mean_value": mean_value,
                            "std_dev": std_dev
                        }
                    )

            # Создаем информационное оповещение для устойчивых трендов
            if is_increasing and recent_values[-1] > 0.5:
                self._create_alert(
                    metric_type=MetricType.RESOURCE_UTILIZATION,
                    level=AlertLevel.INFO,
                    message=f"Устойчивый рост использования ресурса {resource_type.value}",
                    current_value=recent_values[-1],
                    threshold=0.0,
                    context={
                        "resource_type": resource_type.value,
                        "trend": "increasing",
                        "start_value": recent_values[0],
                        "end_value": recent_values[-1]
                    }
                )

    async def _check_for_optimizations(self) -> None:
        """Проверяет необходимость оптимизации на основе собранных метрик"""
        if not self.resource_manager:
            return

        optimizations = []

        # Проверка на оптимальное количество одновременных задач
        cpu_history = self.system_metrics["system_cpu"]
        recent_cpu = cpu_history.calculate_average(60)  # Среднее за минуту

        current_max = self.resource_manager.max_concurrent_tasks

        # Если CPU слишком загружен, но используется максимум задач,
        # предлагаем снизить количество одновременных задач
        if recent_cpu > 0.85 and len(self.resource_manager.active_tasks) >= current_max:
            optimizations.append({
                "type": "reduce_concurrent_tasks",
                "message": "Высокая загрузка CPU. Рекомендуется снизить количество одновременных задач.",
                "current_value": current_max,
                "suggested_value": max(1, current_max - 1),
                "metric": "cpu_usage",
                "priority": "high"
            })
        # Если CPU мало загружен, а задачи в очереди, можно повысить параллелизм
        elif recent_cpu < 0.4 and len(self.resource_manager.task_queue) > 0:
            optimizations.append({
                "type": "increase_concurrent_tasks",
                "message": "Низкая загрузка CPU при наличии задач в очереди. Можно увеличить количество одновременных задач.",
                "current_value": current_max,
                "suggested_value": current_max + 1,
                "metric": "cpu_usage",
                "priority": "medium"
            })

        # Проверка на оптимальные таймауты задач
        timeout_errors = self.task_error_counts["timeout"]
        if timeout_errors > 0 and timeout_errors / max(1, self.task_error_counts["total"]) > 0.5:
            optimizations.append({
                "type": "increase_task_timeouts",
                "message": "Большое количество таймаутов. Рекомендуется увеличить время ожидания для задач.",
                "current_value": "default",
                "suggested_value": "increase_by_50_percent",
                "metric": "timeout_errors",
                "priority": "high"
            })

        # Добавляем найденные оптимизации в виде информационных оповещений
        for opt in optimizations:
            self._create_alert(
                metric_type=MetricType.RESOURCE_UTILIZATION,
                level=AlertLevel.INFO,
                message=f"Возможная оптимизация: {opt['message']}",
                current_value=0.0,
                threshold=0.0,
                context=opt
            )

    def add_alert_handler(self, handler: Callable[[PerformanceAlert], None]) -> None:
        """
        Добавляет обработчик оповещений.

        Args:
            handler: Функция-обработчик, принимающая оповещение
        """
        self.alert_handlers.append(handler)

    def get_recent_alerts(self, count: int = 10, level: Optional[AlertLevel] = None) -> List[PerformanceAlert]:
        """
        Получает последние оповещения с опциональной фильтрацией по уровню.

        Args:
            count: Количество оповещений для возврата
            level: Фильтр по уровню важности

        Returns:
            Список последних оповещений
        """
        if level:
            filtered_alerts = [a for a in self.alerts if a.level == level]
            return filtered_alerts[-count:] if count < len(filtered_alerts) else filtered_alerts
        else:
            return self.alerts[-count:] if count < len(self.alerts) else self.alerts.copy()

    def get_resource_utilization(self, resource_type: ResourceType, timespan_seconds: int = 300) -> Dict[str, Any]:
        """
        Получает данные об использовании указанного ресурса за период.

        Args:
            resource_type: Тип ресурса
            timespan_seconds: Период в секундах

        Returns:
            Словарь с данными об использовании ресурса
        """
        if resource_type not in self.metrics_history:
            return {"error": "Resource type not found"}

        history = self.metrics_history[resource_type]
        start_time = datetime.now() - timedelta(seconds=timespan_seconds)

        metrics = history.get_metrics_in_timespan(start_time)

        if not metrics:
            return {
                "resource_type": resource_type.value,
                "average": 0.0,
                "max": 0.0,
                "min": 0.0,
                "current": 0.0,
                "samples": 0
            }

        values = [m.value for m in metrics]

        return {
            "resource_type": resource_type.value,
            "average": statistics.mean(values) if values else 0.0,
            "max": max(values) if values else 0.0,
            "min": min(values) if values else 0.0,
            "current": values[-1] if values else 0.0,
            "samples": len(values),
            "timespan_seconds": timespan_seconds
        }

    def get_system_metrics(self, timespan_seconds: int = 300) -> Dict[str, Any]:
        """
        Получает данные о системных метриках за период.

        Args:
            timespan_seconds: Период в секундах

        Returns:
            Словарь с системными метриками
        """
        result = {}
        start_time = datetime.now() - timedelta(seconds=timespan_seconds)

        for metric_name, history in self.system_metrics.items():
            metrics = history.get_metrics_in_timespan(start_time)

            if not metrics:
                result[metric_name] = {
                    "average": 0.0,
                    "max": 0.0,
                    "min": 0.0,
                    "current": 0.0,
                    "samples": 0
                }
                continue

            values = [m.value for m in metrics]

            result[metric_name] = {
                "average": statistics.mean(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "min": min(values) if values else 0.0,
                "current": values[-1] if values else 0.0,
                "samples": len(values)
            }

        return result

    def get_performance_snapshot(self) -> Dict[str, Any]:
        """
        Получает полный снимок текущего состояния производительности.

        Returns:
            Словарь с данными о производительности
        """
        # Собираем данные по каждому ресурсу
        resource_data = {}
        for resource_type in ResourceType:
            resource_data[resource_type.value] = self.get_resource_utilization(resource_type)

        # Добавляем системные метрики
        system_data = self.get_system_metrics()

        # Информация о задачах (если есть resource_manager)
        task_data = {}
        if self.resource_manager:
            active_count = len(self.resource_manager.active_tasks)
            queue_count = len(self.resource_manager.task_queue)
            history_count = len(self.resource_manager.task_history)

            task_data = {
                "active_tasks": active_count,
                "queued_tasks": queue_count,
                "completed_tasks": history_count,
                "error_rate": self.task_error_counts["total"] / max(1, history_count),
                "error_counts": self.task_error_counts.copy()
            }

            # Добавляем статистику времени выполнения, если есть данные
            if self.task_completion_times:
                times = list(self.task_completion_times.values())
                task_data["execution_times"] = {
                    "average": statistics.mean(times) if times else 0.0,
                    "max": max(times) if times else 0.0,
                    "min": min(times) if times else 0.0,
                    "samples": len(times)
                }

        # Последние оповещения
        recent_alerts = []
        for alert in self.get_recent_alerts(5):
            recent_alerts.append({
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metric_type": alert.metric_type.value
            })

        # Объединяем все данные
        return {
            "timestamp": datetime.now().isoformat(),
            "resources": resource_data,
            "system": system_data,
            "tasks": task_data,
            "recent_alerts": recent_alerts,
            "monitoring_active": self._running
        }

    def export_metrics_to_json(self, filepath: str, timespan_seconds: int = 3600) -> bool:
        """
        Экспортирует метрики в JSON-файл.

        Args:
            filepath: Путь к файлу для сохранения
            timespan_seconds: Период в секундах

        Returns:
            True, если экспорт успешен, иначе False
        """
        try:
            start_time = datetime.now() - timedelta(seconds=timespan_seconds)

            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "timespan_seconds": timespan_seconds,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat()
                },
                "resources": {},
                "system": {},
                "alerts": []
            }

            # Добавляем метрики ресурсов
            for resource_type, history in self.metrics_history.items():
                metrics = history.get_metrics_in_timespan(start_time)
                export_data["resources"][resource_type.value] = [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value,
                        "context": m.context
                    }
                    for m in metrics
                ]

            # Добавляем системные метрики
            for metric_name, history in self.system_metrics.items():
                metrics = history.get_metrics_in_timespan(start_time)
                export_data["system"][metric_name] = [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value,
                        "context": m.context
                    }
                    for m in metrics
                ]

            # Добавляем оповещения
            for alert in self.alerts:
                if alert.timestamp >= start_time:
                    export_data["alerts"].append({
                        "level": alert.level.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat(),
                        "metric_type": alert.metric_type.value,
                        "current_value": alert.current_value,
                        "threshold": alert.threshold,
                        "context": alert.context
                    })

            # Сохраняем в файл
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"PerformanceMonitor: метрики экспортированы в {filepath}")
            return True

        except Exception as e:
            logger.error(f"PerformanceMonitor: ошибка при экспорте метрик: {str(e)}")
            return False

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Генерирует рекомендации по оптимизации на основе собранных метрик.

        Returns:
            Список рекомендаций по оптимизации
        """
        recommendations = []

        # Ищем оповещения с контекстом оптимизации
        for alert in self.alerts:
            if alert.level == AlertLevel.INFO and "type" in alert.context and alert.context.get("type", "").startswith(""):
                recommendations.append({
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "type": alert.context.get("type", "unknown"),
                    "priority": alert.context.get("priority", "medium"),
                    "current_value": alert.context.get("current_value"),
                    "suggested_value": alert.context.get("suggested_value")
                })

        # Анализируем баланс ресурсов
        if self.resource_manager:
            # Проверяем эффективность распределения ресурсов
            resource_usage = {}
            for resource_type in ResourceType:
                usage_data = self.get_resource_utilization(resource_type, timespan_seconds=300)
                resource_usage[resource_type.value] = usage_data.get("average", 0.0)

            # Если есть ресурсы с крайне низкой и высокой загрузкой, это может указывать на дисбаланс
            min_usage = min(resource_usage.values())
            max_usage = max(resource_usage.values())

            if max_usage > 0.8 and min_usage < 0.2 and len(resource_usage) > 1:
                # Находим самый загруженный и самый свободный ресурс
                most_used = max(resource_usage.items(), key=lambda x: x[1])
                least_used = min(resource_usage.items(), key=lambda x: x[1])

                recommendations.append({
                    "message": f"Обнаружен дисбаланс использования ресурсов: {most_used[0]} ({most_used[1]:.1%}) перегружен, а {least_used[0]} ({least_used[1]:.1%}) недогружен",
                    "timestamp": datetime.now().isoformat(),
                    "type": "resource_balancing",
                    "priority": "high",
                    "most_used_resource": most_used[0],
                    "least_used_resource": least_used[0]
                })

        # Рассматриваем оптимизацию на основе частоты ошибок
        error_rate = self.task_error_counts["total"] / max(1, len(self.task_completion_times))
        if error_rate > 0.1:  # Более 10% задач с ошибками
            # Анализируем типы ошибок
            if self.task_error_counts["timeout"] / max(1, self.task_error_counts["total"]) > 0.5:
                recommendations.append({
                    "message": "Высокая частота таймаутов. Рекомендуется увеличить таймауты задач или оптимизировать выполнение длительных операций",
                    "timestamp": datetime.now().isoformat(),
                    "type": "reduce_timeouts",
                    "priority": "high",
                    "error_rate": error_rate
                })

        return recommendations

    def set_collection_interval(self, seconds: int) -> None:
        """
        Устанавливает интервал сбора метрик.

        Args:
            seconds: Интервал в секундах (минимум 1)
        """
        if seconds < 1:
            logger.warning("PerformanceMonitor: интервал сбора метрик не может быть меньше 1 секунды")
            return

        self._collection_interval = seconds
        logger.info(f"PerformanceMonitor: интервал сбора метрик установлен на {seconds} секунд")

    def reset_metrics(self) -> None:
        """Сбрасывает все собранные метрики и оповещения"""
        with self._lock:
            # Сбрасываем истории метрик
            for resource_type in ResourceType:
                self.metrics_history[resource_type] = ResourceMetricsHistory(resource_type=resource_type)

            # Сбрасываем системные метрики
            for metric_name in self.system_metrics:
                resource_type = self.system_metrics[metric_name].resource_type
                self.system_metrics[metric_name] = ResourceMetricsHistory(resource_type=resource_type)

            # Сбрасываем счетчики и оповещения
            self.task_completion_times = {}
            self.task_error_counts = {
                "total": 0,
                "timeout": 0,
                "resource_error": 0,
                "task_error": 0
            }
            self.alerts = []

        logger.info("PerformanceMonitor: метрики сброшены")
