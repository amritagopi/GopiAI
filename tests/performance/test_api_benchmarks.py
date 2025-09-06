"""
API performance benchmarks for CrewAI server endpoints.
"""
import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
import statistics


class APIBenchmark:
    """API performance benchmark utilities."""
    
    def __init__(self, base_url: str = "http://localhost:5051"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def benchmark_endpoint(self, endpoint: str, method: str = "GET", 
                          data: Dict = None, iterations: int = 10) -> Dict[str, float]:
        """Benchmark a single endpoint."""
        response_times = []
        errors = 0
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                if method.upper() == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=30)
                elif method.upper() == "POST":
                    response = self.session.post(
                        f"{self.base_url}{endpoint}", 
                        json=data, 
                        timeout=30
                    )
                
                response.raise_for_status()
                end_time = time.perf_counter()
                response_times.append((end_time - start_time) * 1000)
                
            except Exception as e:
                errors += 1
                print(f"Error in benchmark: {e}")
        
        if not response_times:
            return {
                'avg_response_time_ms': float('inf'),
                'min_response_time_ms': float('inf'),
                'max_response_time_ms': float('inf'),
                'p95_response_time_ms': float('inf'),
                'error_rate': 1.0,
                'throughput_ops_per_sec': 0.0
            }
        
        return {
            'avg_response_time_ms': statistics.mean(response_times),
            'min_response_time_ms': min(response_times),
            'max_response_time_ms': max(response_times),
            'p95_response_time_ms': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else response_times[0],
            'error_rate': errors / iterations,
            'throughput_ops_per_sec': len(response_times) / (sum(response_times) / 1000) if response_times else 0.0
        }
    
    def concurrent_benchmark(self, endpoint: str, concurrent_users: int = 5, 
                           requests_per_user: int = 10) -> Dict[str, float]:
        """Benchmark endpoint with concurrent users."""
        all_response_times = []
        errors = 0
        
        def user_requests():
            user_times = []
            user_errors = 0
            
            for _ in range(requests_per_user):
                start_time = time.perf_counter()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                    response.raise_for_status()
                    end_time = time.perf_counter()
                    user_times.append((end_time - start_time) * 1000)
                except Exception:
                    user_errors += 1
            
            return user_times, user_errors
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_requests) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    times, user_errors = future.result()
                    all_response_times.extend(times)
                    errors += user_errors
                except Exception as e:
                    print(f"Concurrent benchmark error: {e}")
                    errors += requests_per_user
        
        total_requests = concurrent_users * requests_per_user
        
        if not all_response_times:
            return {
                'avg_response_time_ms': float('inf'),
                'error_rate': 1.0,
                'throughput_ops_per_sec': 0.0
            }
        
        return {
            'avg_response_time_ms': statistics.mean(all_response_times),
            'error_rate': errors / total_requests,
            'throughput_ops_per_sec': len(all_response_times) / (sum(all_response_times) / 1000)
        }


@pytest.fixture
def api_benchmark():
    """Fixture providing API benchmark utilities."""
    return APIBenchmark()


class TestAPIPerformance:
    """API performance tests."""
    
    def test_health_endpoint_performance(self, api_benchmark, benchmark_config, perf_assert):
        """Test health endpoint performance."""
        metrics = api_benchmark.benchmark_endpoint("/health", iterations=20)
        
        perf_assert.assert_response_time(
            metrics['avg_response_time_ms'],
            100.0,  # Health check should be very fast
            "Health endpoint"
        )
        
        assert metrics['error_rate'] == 0.0, "Health endpoint should not have errors"
        assert metrics['throughput_ops_per_sec'] > 10.0, "Health endpoint should have high throughput"
    
    def test_models_endpoint_performance(self, api_benchmark, benchmark_config, perf_assert):
        """Test models listing endpoint performance."""
        metrics = api_benchmark.benchmark_endpoint("/models", iterations=10)
        
        perf_assert.assert_response_time(
            metrics['avg_response_time_ms'],
            benchmark_config['response_time_threshold_ms'],
            "Models endpoint"
        )
        
        assert metrics['error_rate'] <= 0.1, "Models endpoint should have low error rate"
    
    def test_chat_endpoint_performance(self, api_benchmark, benchmark_config, 
                                     sample_test_data, perf_assert):
        """Test chat endpoint performance with different message sizes."""
        test_cases = [
            ("small", sample_test_data['small_message']),
            ("medium", sample_test_data['medium_message']),
            ("large", sample_test_data['large_message'])
        ]
        
        for size, message in test_cases:
            chat_data = {
                "message": message,
                "model": "gpt-3.5-turbo",
                "stream": False
            }
            
            metrics = api_benchmark.benchmark_endpoint(
                "/chat", 
                method="POST", 
                data=chat_data, 
                iterations=5
            )
            
            # Adjust thresholds based on message size
            threshold_multiplier = {"small": 1.0, "medium": 2.0, "large": 3.0}[size]
            adjusted_threshold = benchmark_config['response_time_threshold_ms'] * threshold_multiplier
            
            perf_assert.assert_response_time(
                metrics['avg_response_time_ms'],
                adjusted_threshold,
                f"Chat endpoint ({size} message)"
            )
    
    def test_concurrent_users_performance(self, api_benchmark, benchmark_config):
        """Test API performance under concurrent load."""
        metrics = api_benchmark.concurrent_benchmark(
            "/health",
            concurrent_users=benchmark_config['concurrent_users'],
            requests_per_user=10
        )
        
        assert metrics['avg_response_time_ms'] < 1000.0, (
            f"Concurrent requests took {metrics['avg_response_time_ms']:.2f}ms on average"
        )
        
        assert metrics['error_rate'] <= 0.05, (
            f"Error rate {metrics['error_rate']:.2%} too high under concurrent load"
        )
        
        assert metrics['throughput_ops_per_sec'] > 5.0, (
            f"Throughput {metrics['throughput_ops_per_sec']:.2f} ops/sec too low"
        )
    
    def test_memory_usage_during_requests(self, api_benchmark, performance_monitor, 
                                        benchmark_config, perf_assert):
        """Test memory usage during API requests."""
        performance_monitor.start_monitoring(interval=0.1)
        
        # Make several requests to stress test memory
        for _ in range(20):
            try:
                api_benchmark.benchmark_endpoint("/health", iterations=1)
                time.sleep(0.1)
            except Exception as e:
                print(f"Request failed: {e}")
        
        metrics = performance_monitor.stop_monitoring()
        
        if metrics:
            max_memory = max(m.memory_mb for m in metrics)
            avg_cpu = statistics.mean(m.cpu_percent for m in metrics)
            
            perf_assert.assert_memory_usage(
                max_memory,
                benchmark_config['memory_threshold_mb'],
                "API requests"
            )
            
            perf_assert.assert_cpu_usage(
                avg_cpu,
                benchmark_config['cpu_threshold_percent'],
                "API requests"
            )
    
    @pytest.mark.slow
    def test_sustained_load_performance(self, api_benchmark, performance_monitor, benchmark_config):
        """Test API performance under sustained load."""
        performance_monitor.start_monitoring(interval=0.5)
        
        # Run sustained load for 30 seconds
        start_time = time.time()
        request_count = 0
        errors = 0
        
        while time.time() - start_time < 30:
            try:
                metrics = api_benchmark.benchmark_endpoint("/health", iterations=1)
                request_count += 1
                if metrics['error_rate'] > 0:
                    errors += 1
            except Exception:
                errors += 1
            
            time.sleep(0.1)
        
        system_metrics = performance_monitor.stop_monitoring()
        
        # Verify system remained stable
        if system_metrics:
            avg_memory = statistics.mean(m.memory_mb for m in system_metrics)
            max_memory = max(m.memory_mb for m in system_metrics)
            
            assert max_memory < benchmark_config['memory_threshold_mb'], (
                f"Memory usage {max_memory:.2f}MB exceeded threshold during sustained load"
            )
            
            # Memory should not grow significantly over time (no major leaks)
            memory_growth = max_memory - system_metrics[0].memory_mb
            assert memory_growth < 100.0, (
                f"Memory grew by {memory_growth:.2f}MB during sustained load"
            )
        
        error_rate = errors / request_count if request_count > 0 else 1.0
        assert error_rate <= 0.05, f"Error rate {error_rate:.2%} too high during sustained load"


if __name__ == "__main__":
    # Allow running benchmarks directly
    benchmark = APIBenchmark()
    
    print("Running API benchmarks...")
    
    # Health endpoint
    health_metrics = benchmark.benchmark_endpoint("/health", iterations=10)
    print(f"Health endpoint: {health_metrics['avg_response_time_ms']:.2f}ms avg")
    
    # Concurrent load
    concurrent_metrics = benchmark.concurrent_benchmark("/health", concurrent_users=3, requests_per_user=5)
    print(f"Concurrent load: {concurrent_metrics['avg_response_time_ms']:.2f}ms avg, "
          f"{concurrent_metrics['throughput_ops_per_sec']:.2f} ops/sec")