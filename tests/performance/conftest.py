"""
Performance tests configuration and fixtures.
"""
import pytest
import psutil
import time
import threading
from typing import List
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    cpu_percent: float
    memory_mb: float
    duration_ms: float
    response_time_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    error_rate: float = 0.0


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 0.1):
        """Start performance monitoring."""
        self.monitoring = True
        self.metrics.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> List[PerformanceMetrics]:
        """Stop monitoring and return collected metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self.metrics.copy()
        
    def _monitor_loop(self, interval: float):
        """Monitor system resources in a loop."""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                metric = PerformanceMetrics(
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    duration_ms=0.0
                )
                self.metrics.append(metric)
                
                time.sleep(interval)
            except Exception:
                # Continue monitoring even if we can't get metrics
                pass


@contextmanager
def performance_timer():
    """Context manager to measure execution time."""
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    return (end_time - start_time) * 1000  # Return milliseconds


@pytest.fixture
def performance_monitor():
    """Fixture providing performance monitoring."""
    monitor = PerformanceMonitor()
    yield monitor
    # Ensure monitoring is stopped
    if monitor.monitoring:
        monitor.stop_monitoring()


@pytest.fixture
def benchmark_config():
    """Configuration for benchmark tests."""
    return {
        'api_timeout': 30.0,
        'memory_threshold_mb': 500.0,
        'cpu_threshold_percent': 80.0,
        'response_time_threshold_ms': 5000.0,
        'ui_response_threshold_ms': 100.0,
        'search_response_threshold_ms': 1000.0,
        'concurrent_users': 5,
        'test_iterations': 10
    }


@pytest.fixture
def sample_test_data():
    """Sample data for performance testing."""
    return {
        'small_message': "Hello, how are you?",
        'medium_message': "This is a medium-sized message for testing purposes. " * 10,
        'large_message': "This is a large message for performance testing. " * 100,
        'search_queries': [
            "machine learning",
            "artificial intelligence",
            "python programming",
            "data science",
            "neural networks"
        ],
        'conversation_history': [
            {"role": "user", "content": f"Test message {i}"}
            for i in range(50)
        ]
    }


class PerformanceAssertions:
    """Helper class for performance assertions."""
    
    @staticmethod
    def assert_response_time(actual_ms: float, threshold_ms: float, operation: str):
        """Assert response time is within threshold."""
        assert actual_ms <= threshold_ms, (
            f"{operation} took {actual_ms:.2f}ms, "
            f"exceeding threshold of {threshold_ms}ms"
        )
    
    @staticmethod
    def assert_memory_usage(actual_mb: float, threshold_mb: float, operation: str):
        """Assert memory usage is within threshold."""
        assert actual_mb <= threshold_mb, (
            f"{operation} used {actual_mb:.2f}MB, "
            f"exceeding threshold of {threshold_mb}MB"
        )
    
    @staticmethod
    def assert_cpu_usage(actual_percent: float, threshold_percent: float, operation: str):
        """Assert CPU usage is within threshold."""
        assert actual_percent <= threshold_percent, (
            f"{operation} used {actual_percent:.2f}% CPU, "
            f"exceeding threshold of {threshold_percent}%"
        )


@pytest.fixture
def perf_assert():
    """Fixture providing performance assertions."""
    return PerformanceAssertions()