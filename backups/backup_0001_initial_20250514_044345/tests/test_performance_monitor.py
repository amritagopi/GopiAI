#!/usr/bin/env python
"""
Модульные тесты для системы мониторинга производительности
"""

import os
import sys
import asyncio
import pytest
import tempfile
import time
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.performance_monitor import (
    PerformanceMonitor, PerformanceMetric, PerformanceAlert,
    MetricType, AlertLevel, ResourceMetricsHistory
)
from app.agent.resource_manager import ResourceManager, ResourceType


class TestResourceMetricsHistory:
    """Тесты для класса ResourceMetricsHistory"""

    def test_add_metric(self):
        """Тест добавления метрик в историю"""
        history = ResourceMetricsHistory(resource_type=ResourceType.CPU)
        assert len(history.metrics) == 0

        # Добавляем метрику
        metric = PerformanceMetric(metric_type=MetricType.CPU_USAGE, value=0.5)
        history.add_metric(metric)
        assert len(history.metrics) == 1
        assert history.metrics[0].value == 0.5

        # Проверяем ограничение размера истории
        history.max_history_size = 3
        for i in range(5):
            history.add_metric(PerformanceMetric(metric_type=MetricType.CPU_USAGE, value=float(i)))

        # Должны остаться только последние 3 метрики
        assert len(history.metrics) == 3
        assert [m.value for m in history.metrics] == [2.0, 3.0, 4.0]

    def test_get_recent_metrics(self):
        """Тест получения последних метрик"""
        history = ResourceMetricsHistory(resource_type=ResourceType.MEMORY)

        # Добавляем 5 метрик
        for i in range(5):
            history.add_metric(PerformanceMetric(metric_type=MetricType.MEMORY_USAGE, value=float(i * 0.1)))

        # Получаем последние 3 метрики
        recent = history.get_recent_metrics(3)
        assert len(recent) == 3
        assert [m.value for m in recent] == [0.2, 0.3, 0.4]

        # Получаем все метрики
        all_metrics = history.get_recent_metrics(10)
        assert len(all_metrics) == 5

    def test_get_metrics_in_timespan(self):
        """Тест получения метрик в указанном временном интервале"""
        history = ResourceMetricsHistory(resource_type=ResourceType.NETWORK)

        # Добавляем метрики с разным временем
        now = datetime.now()

        history.add_metric(PerformanceMetric(
            metric_type=MetricType.NETWORK_IO,
            value=0.1,
            timestamp=now - timedelta(minutes=10)
        ))

        history.add_metric(PerformanceMetric(
            metric_type=MetricType.NETWORK_IO,
            value=0.2,
            timestamp=now - timedelta(minutes=5)
        ))

        history.add_metric(PerformanceMetric(
            metric_type=MetricType.NETWORK_IO,
            value=0.3,
            timestamp=now - timedelta(minutes=1)
        ))

        # Получаем метрики за последние 6 минут
        recent = history.get_metrics_in_timespan(now - timedelta(minutes=6))
        assert len(recent) == 2
        assert [m.value for m in recent] == [0.2, 0.3]

        # Получаем метрики в определенном интервале
        interval = history.get_metrics_in_timespan(
            now - timedelta(minutes=8),
            now - timedelta(minutes=2)
        )
        assert len(interval) == 1
        assert interval[0].value == 0.2

    def test_calculate_average(self):
        """Тест вычисления среднего значения метрик"""
        history = ResourceMetricsHistory(resource_type=ResourceType.CPU)

        # Проверка для пустой истории
        assert history.calculate_average() == 0.0

        # Добавляем метрики
        now = datetime.now()

        # Старая метрика (за пределами интервала в 60 секунд)
        history.add_metric(PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.1,
            timestamp=now - timedelta(seconds=120)
        ))

        # Метрики в интервале
        history.add_metric(PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.2,
            timestamp=now - timedelta(seconds=30)
        ))

        history.add_metric(PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.4,
            timestamp=now - timedelta(seconds=10)
        ))

        # Среднее за последние 60 секунд должно быть (0.2 + 0.4) / 2 = 0.3
        assert history.calculate_average(60) == 0.3

        # Среднее за последние 200 секунд должно быть (0.1 + 0.2 + 0.4) / 3 = 0.23333
        assert abs(history.calculate_average(200) - 0.2333) < 0.001


class TestPerformanceMonitor:
    """Тесты для класса PerformanceMonitor"""

    @pytest.fixture
    def mock_resource_manager(self):
        """Создает мок ResourceManager для тестов"""
        mock_rm = MagicMock(spec=ResourceManager)

        # Настраиваем моки для ресурсов
        mock_pools = {}
        for resource_type in ResourceType:
            mock_pool = MagicMock()
            mock_pool.allocated.return_value = 0.5
            mock_pool.capacity = 1.0
            mock_pool.available.return_value = 0.5
            mock_pools[resource_type] = mock_pool

        mock_rm.resource_pools = mock_pools
        mock_rm.active_tasks = {}
        mock_rm.task_queue = []
        mock_rm.task_history = {}
        mock_rm.max_concurrent_tasks = 5

        return mock_rm

    @pytest.fixture
    def monitor(self, mock_resource_manager):
        """Создает экземпляр PerformanceMonitor для тестов"""
        return PerformanceMonitor(resource_manager=mock_resource_manager)

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, monitor):
        """Тест запуска и остановки мониторинга"""
        assert not monitor._running

        # Запускаем мониторинг
        await monitor.start_monitoring()
        assert monitor._running
        assert monitor._monitoring_task is not None

        # Останавливаем мониторинг
        await monitor.stop_monitoring()
        assert not monitor._running
        await asyncio.sleep(0.1)  # Даем время на остановку задачи

    def test_add_metric_and_check_alert(self, monitor):
        """Тест добавления метрики и проверки порогов оповещений"""
        # Метрика ниже порогов
        normal_metric = PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.5
        )

        monitor._check_alert_threshold(normal_metric)
        assert len(monitor.alerts) == 0

        # Метрика на уровне предупреждения
        warning_metric = PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.8
        )

        monitor._check_alert_threshold(warning_metric)
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0].level == AlertLevel.WARNING

        # Метрика на критическом уровне
        critical_metric = PerformanceMetric(
            metric_type=MetricType.CPU_USAGE,
            value=0.95
        )

        monitor._check_alert_threshold(critical_metric)
        assert len(monitor.alerts) == 2
        assert monitor.alerts[1].level == AlertLevel.CRITICAL

    def test_alert_handlers(self, monitor):
        """Тест обработчиков оповещений"""
        # Создаем обработчик, который считает оповещения
        alert_count = {"count": 0}

        def handler(alert):
            alert_count["count"] += 1

        monitor.add_alert_handler(handler)

        # Генерируем оповещение
        monitor._create_alert(
            metric_type=MetricType.MEMORY_USAGE,
            level=AlertLevel.WARNING,
            message="Test alert",
            current_value=0.8,
            threshold=0.75,
            context={}
        )

        assert alert_count["count"] == 1
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0].message == "Test alert"

    def test_get_recent_alerts(self, monitor):
        """Тест получения последних оповещений"""
        # Добавляем разные оповещения
        monitor._create_alert(
            metric_type=MetricType.CPU_USAGE,
            level=AlertLevel.WARNING,
            message="Warning 1",
            current_value=0.8,
            threshold=0.75,
            context={}
        )

        monitor._create_alert(
            metric_type=MetricType.MEMORY_USAGE,
            level=AlertLevel.CRITICAL,
            message="Critical 1",
            current_value=0.95,
            threshold=0.9,
            context={}
        )

        monitor._create_alert(
            metric_type=MetricType.ERROR_RATE,
            level=AlertLevel.INFO,
            message="Info 1",
            current_value=0.03,
            threshold=0.05,
            context={}
        )

        # Получаем все оповещения
        all_alerts = monitor.get_recent_alerts()
        assert len(all_alerts) == 3

        # Получаем только критические оповещения
        critical_alerts = monitor.get_recent_alerts(level=AlertLevel.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].message == "Critical 1"

        # Получаем последние 2 оповещения
        last_alerts = monitor.get_recent_alerts(2)
        assert len(last_alerts) == 2
        assert last_alerts[0].message == "Critical 1"
        assert last_alerts[1].message == "Info 1"

    def test_get_resource_utilization(self, monitor):
        """Тест получения данных об использовании ресурсов"""
        # Добавляем метрики для CPU
        for i in range(5):
            monitor.metrics_history[ResourceType.CPU].add_metric(
                PerformanceMetric(
                    metric_type=MetricType.CPU_USAGE,
                    value=0.1 * (i + 1)
                )
            )

        # Получаем данные об использовании
        utilization = monitor.get_resource_utilization(ResourceType.CPU)

        assert utilization["resource_type"] == ResourceType.CPU.value
        assert abs(utilization["average"] - 0.3) < 0.001  # Среднее (0.1 + 0.2 + 0.3 + 0.4 + 0.5) / 5 = 0.3
        assert utilization["max"] == 0.5
        assert utilization["min"] == 0.1
        assert utilization["current"] == 0.5  # Последнее значение
        assert utilization["samples"] == 5

    def test_get_system_metrics(self, monitor):
        """Тест получения системных метрик"""
        # Добавляем системные метрики
        monitor.system_metrics["system_cpu"].add_metric(
            PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=0.6
            )
        )

        monitor.system_metrics["system_memory"].add_metric(
            PerformanceMetric(
                metric_type=MetricType.MEMORY_USAGE,
                value=0.7
            )
        )

        # Получаем системные метрики
        metrics = monitor.get_system_metrics()

        assert "system_cpu" in metrics
        assert "system_memory" in metrics
        assert metrics["system_cpu"]["current"] == 0.6
        assert metrics["system_memory"]["current"] == 0.7

    def test_get_performance_snapshot(self, monitor):
        """Тест получения полного снимка производительности"""
        # Добавляем метрики
        for resource_type in ResourceType:
            monitor.metrics_history[resource_type].add_metric(
                PerformanceMetric(
                    metric_type=MetricType.RESOURCE_UTILIZATION,
                    value=0.5,
                    context={"resource_type": resource_type.value}
                )
            )

        # Добавляем системные метрики
        monitor.system_metrics["system_cpu"].add_metric(
            PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=0.6
            )
        )

        # Добавляем оповещение
        monitor._create_alert(
            metric_type=MetricType.CPU_USAGE,
            level=AlertLevel.WARNING,
            message="Test warning",
            current_value=0.8,
            threshold=0.75,
            context={}
        )

        # Получаем снимок
        snapshot = monitor.get_performance_snapshot()

        assert "resources" in snapshot
        assert "system" in snapshot
        assert "recent_alerts" in snapshot
        assert len(snapshot["recent_alerts"]) == 1
        assert snapshot["recent_alerts"][0]["message"] == "Test warning"

    @pytest.mark.asyncio
    async def test_analyze_metrics(self, monitor):
        """Тест анализа метрик и выявления трендов"""
        # Добавляем устойчивый тренд роста для CPU
        for i in range(10):
            monitor.metrics_history[ResourceType.CPU].add_metric(
                PerformanceMetric(
                    metric_type=MetricType.CPU_USAGE,
                    value=0.5 + i * 0.05,  # От 0.5 до 0.95
                    context={"resource_type": ResourceType.CPU.value}
                )
            )

        # Анализируем метрики
        await monitor._analyze_metrics()

        # Должно быть создано оповещение о тренде
        trend_alerts = [a for a in monitor.alerts if "рост" in a.message.lower()]
        assert len(trend_alerts) > 0

    @pytest.mark.asyncio
    async def test_check_for_optimizations(self, monitor):
        """Тест проверки необходимости оптимизации"""
        # Устанавливаем высокую загрузку CPU
        cpu_metrics = monitor.system_metrics["system_cpu"]
        for i in range(10):
            cpu_metrics.add_metric(
                PerformanceMetric(
                    metric_type=MetricType.CPU_USAGE,
                    value=0.9,  # Высокая загрузка
                    context={"cores": 4}
                )
            )

        # Настраиваем моки для ResourceManager
        monitor.resource_manager.active_tasks = {str(i): MagicMock() for i in range(5)}
        monitor.resource_manager.max_concurrent_tasks = 5

        # Проверяем оптимизации
        await monitor._check_for_optimizations()

        # Должно быть создано оповещение с рекомендацией уменьшить число одновременных задач
        optimization_alerts = [a for a in monitor.alerts if "reduce_concurrent_tasks" in str(a.context)]
        assert len(optimization_alerts) > 0

    def test_export_metrics_to_json(self, monitor):
        """Тест экспорта метрик в JSON"""
        # Добавляем метрики
        monitor.metrics_history[ResourceType.CPU].add_metric(
            PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=0.7,
                context={"cores": 4}
            )
        )

        monitor.system_metrics["system_memory"].add_metric(
            PerformanceMetric(
                metric_type=MetricType.MEMORY_USAGE,
                value=0.6,
                context={"total_gb": 16}
            )
        )

        # Создаем временный файл для экспорта
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            filepath = temp_file.name

        try:
            # Экспортируем метрики
            success = monitor.export_metrics_to_json(filepath)
            assert success

            # Проверяем, что файл существует и содержит данные
            assert os.path.exists(filepath)

            with open(filepath, 'r') as f:
                data = json.load(f)

            assert "resources" in data
            assert "system" in data
            assert "metadata" in data
            assert ResourceType.CPU.value in data["resources"]
            assert "system_memory" in data["system"]

        finally:
            # Удаляем временный файл
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_get_optimization_recommendations(self, monitor):
        """Тест получения рекомендаций по оптимизации"""
        # Добавляем оповещение с информацией об оптимизации
        monitor._create_alert(
            metric_type=MetricType.RESOURCE_UTILIZATION,
            level=AlertLevel.INFO,
            message="Возможная оптимизация: увеличить число задач",
            current_value=0.0,
            threshold=0.0,
            context={
                "type": "increase_concurrent_tasks",
                "priority": "medium",
                "current_value": 5,
                "suggested_value": 6
            }
        )

        # Добавляем несбалансированные ресурсы
        monitor.resource_manager.get_resource_usage_info = MagicMock(return_value={
            "CPU": {"allocated": 0.9, "capacity": 1.0},
            "MEMORY": {"allocated": 0.1, "capacity": 1.0}
        })

        # Получаем рекомендации
        recommendations = monitor.get_optimization_recommendations()

        assert len(recommendations) >= 1
        assert any(r.get("type") == "increase_concurrent_tasks" for r in recommendations)

        # Проверяем, была ли найдена рекомендация по балансировке ресурсов
        balance_recommendations = [r for r in recommendations if r.get("type") == "resource_balancing"]
        if balance_recommendations:
            assert "дисбаланс" in balance_recommendations[0].get("message", "").lower()

    def test_reset_metrics(self, monitor):
        """Тест сброса метрик"""
        # Добавляем метрики и оповещения
        monitor.metrics_history[ResourceType.CPU].add_metric(
            PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=0.7
            )
        )

        monitor._create_alert(
            metric_type=MetricType.CPU_USAGE,
            level=AlertLevel.WARNING,
            message="Test warning",
            current_value=0.8,
            threshold=0.75,
            context={}
        )

        monitor.task_completion_times = {"task1": 5.0}
        monitor.task_error_counts["total"] = 1

        assert len(monitor.metrics_history[ResourceType.CPU].metrics) == 1
        assert len(monitor.alerts) == 1
        assert len(monitor.task_completion_times) == 1
        assert monitor.task_error_counts["total"] == 1

        # Сбрасываем метрики
        monitor.reset_metrics()

        # Проверяем, что все метрики сброшены
        assert len(monitor.metrics_history[ResourceType.CPU].metrics) == 0
        assert len(monitor.alerts) == 0
        assert len(monitor.task_completion_times) == 0
        assert monitor.task_error_counts["total"] == 0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
