"""
Memory system performance tests for txtai integration.
"""
import pytest
import time
import tempfile
import shutil
import os
import statistics
from typing import List, Dict
import psutil
import threading


class MemorySystemBenchmark:
    """Memory system performance benchmark utilities."""
    
    def __init__(self):
        self.temp_dir = None
        self.index = None
        
    def setup_test_index(self, documents: List[str] = None):
        """Setup a test txtai index."""
        try:
            import txtai
            from txtai import Embeddings
            
            self.temp_dir = tempfile.mkdtemp()
            self.index = Embeddings()
            
            if documents:
                # Create test documents
                test_docs = [(i, doc, None) for i, doc in enumerate(documents)]
                self.index.index(test_docs)
                
            return True
        except ImportError:
            pytest.skip("txtai not available for memory performance tests")
        except Exception as e:
            print(f"Failed to setup test index: {e}")
            return False
    
    def cleanup_test_index(self):
        """Cleanup test index and temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.index = None
    
    def benchmark_indexing(self, documents: List[str], batch_size: int = 100) -> Dict[str, float]:
        """Benchmark document indexing performance."""
        if not self.setup_test_index():
            return {}
        
        try:
            # Prepare documents for indexing
            test_docs = [(i, doc, None) for i, doc in enumerate(documents)]
            
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Index documents in batches
            for i in range(0, len(test_docs), batch_size):
                batch = test_docs[i:i + batch_size]
                self.index.index(batch)
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            duration_ms = (end_time - start_time) * 1000
            memory_used_mb = end_memory - start_memory
            
            return {
                'total_duration_ms': duration_ms,
                'docs_per_second': len(documents) / (duration_ms / 1000),
                'memory_used_mb': memory_used_mb,
                'avg_time_per_doc_ms': duration_ms / len(documents)
            }
            
        except Exception as e:
            print(f"Indexing benchmark failed: {e}")
            return {}
        finally:
            self.cleanup_test_index()
    
    def benchmark_search(self, query: str, iterations: int = 100) -> Dict[str, float]:
        """Benchmark search performance."""
        if not self.index:
            return {}
        
        response_times = []
        errors = 0
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                results = self.index.search(query, limit=10)
                end_time = time.perf_counter()
                response_times.append((end_time - start_time) * 1000)
            except Exception as e:
                errors += 1
                print(f"Search error: {e}")
        
        if not response_times:
            return {
                'avg_response_time_ms': float('inf'),
                'error_rate': 1.0
            }
        
        return {
            'avg_response_time_ms': statistics.mean(response_times),
            'min_response_time_ms': min(response_times),
            'max_response_time_ms': max(response_times),
            'p95_response_time_ms': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else response_times[0],
            'error_rate': errors / iterations,
            'searches_per_second': len(response_times) / (sum(response_times) / 1000) if response_times else 0.0
        }
    
    def benchmark_concurrent_search(self, queries: List[str], concurrent_users: int = 5) -> Dict[str, float]:
        """Benchmark concurrent search performance."""
        if not self.index:
            return {}
        
        all_response_times = []
        errors = 0
        
        def user_searches():
            user_times = []
            user_errors = 0
            
            for query in queries:
                start_time = time.perf_counter()
                try:
                    results = self.index.search(query, limit=10)
                    end_time = time.perf_counter()
                    user_times.append((end_time - start_time) * 1000)
                except Exception:
                    user_errors += 1
            
            return user_times, user_errors
        
        threads = []
        results = []
        
        # Start concurrent searches
        for _ in range(concurrent_users):
            thread = threading.Thread(target=lambda: results.append(user_searches()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        for times, user_errors in results:
            all_response_times.extend(times)
            errors += user_errors
        
        total_searches = concurrent_users * len(queries)
        
        if not all_response_times:
            return {
                'avg_response_time_ms': float('inf'),
                'error_rate': 1.0,
                'throughput_searches_per_sec': 0.0
            }
        
        return {
            'avg_response_time_ms': statistics.mean(all_response_times),
            'error_rate': errors / total_searches,
            'throughput_searches_per_sec': len(all_response_times) / (sum(all_response_times) / 1000)
        }


@pytest.fixture
def memory_benchmark():
    """Fixture providing memory system benchmark utilities."""
    benchmark = MemorySystemBenchmark()
    yield benchmark
    benchmark.cleanup_test_index()


@pytest.fixture
def test_documents():
    """Sample documents for memory performance testing."""
    return [
        "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
        "Python is a popular programming language for data science and AI applications.",
        "Neural networks are inspired by the structure and function of biological neural networks.",
        "Deep learning uses multiple layers of neural networks to learn complex patterns.",
        "Natural language processing enables computers to understand and generate human language.",
        "Computer vision allows machines to interpret and understand visual information.",
        "Reinforcement learning is a type of machine learning where agents learn through interaction.",
        "Data preprocessing is crucial for building effective machine learning models.",
        "Feature engineering involves selecting and transforming variables for machine learning.",
        "Model evaluation helps assess the performance and generalization of ML algorithms.",
        "Cross-validation is a technique to assess how well a model generalizes to unseen data.",
        "Overfitting occurs when a model learns the training data too well and fails to generalize.",
        "Regularization techniques help prevent overfitting in machine learning models.",
        "Ensemble methods combine multiple models to improve prediction accuracy.",
        "Gradient descent is an optimization algorithm used to minimize loss functions.",
        "Backpropagation is the algorithm used to train neural networks by computing gradients.",
        "Convolutional neural networks are particularly effective for image recognition tasks.",
        "Recurrent neural networks are designed to work with sequential data like text or time series.",
        "Transfer learning allows models trained on one task to be adapted for related tasks.",
        "Hyperparameter tuning involves optimizing the configuration of machine learning algorithms."
    ] * 10  # Multiply to get more documents for testing


class TestMemorySystemPerformance:
    """Memory system performance tests."""
    
    def test_small_dataset_indexing_performance(self, memory_benchmark, benchmark_config, perf_assert):
        """Test indexing performance with small dataset."""
        small_docs = [
            "Test document 1 about machine learning",
            "Test document 2 about artificial intelligence", 
            "Test document 3 about data science",
            "Test document 4 about neural networks",
            "Test document 5 about deep learning"
        ]
        
        metrics = memory_benchmark.benchmark_indexing(small_docs)
        
        if metrics:
            perf_assert.assert_response_time(
                metrics['total_duration_ms'],
                5000.0,  # 5 seconds for small dataset
                "Small dataset indexing"
            )
            
            assert metrics['docs_per_second'] > 1.0, (
                f"Indexing rate {metrics['docs_per_second']:.2f} docs/sec too slow"
            )
    
    def test_medium_dataset_indexing_performance(self, memory_benchmark, test_documents, 
                                               benchmark_config, perf_assert):
        """Test indexing performance with medium dataset."""
        medium_docs = test_documents[:50]  # 50 documents
        
        metrics = memory_benchmark.benchmark_indexing(medium_docs)
        
        if metrics:
            perf_assert.assert_response_time(
                metrics['total_duration_ms'],
                30000.0,  # 30 seconds for medium dataset
                "Medium dataset indexing"
            )
            
            perf_assert.assert_memory_usage(
                metrics['memory_used_mb'],
                200.0,  # 200MB threshold
                "Medium dataset indexing"
            )
    
    @pytest.mark.slow
    def test_large_dataset_indexing_performance(self, memory_benchmark, test_documents, 
                                              benchmark_config, perf_assert):
        """Test indexing performance with large dataset."""
        large_docs = test_documents  # All test documents
        
        metrics = memory_benchmark.benchmark_indexing(large_docs, batch_size=50)
        
        if metrics:
            perf_assert.assert_response_time(
                metrics['total_duration_ms'],
                120000.0,  # 2 minutes for large dataset
                "Large dataset indexing"
            )
            
            perf_assert.assert_memory_usage(
                metrics['memory_used_mb'],
                500.0,  # 500MB threshold
                "Large dataset indexing"
            )
    
    def test_search_performance(self, memory_benchmark, test_documents, 
                              sample_test_data, benchmark_config, perf_assert):
        """Test search performance."""
        if not memory_benchmark.setup_test_index(test_documents[:20]):
            pytest.skip("Could not setup test index")
        
        for query in sample_test_data['search_queries']:
            metrics = memory_benchmark.benchmark_search(query, iterations=20)
            
            if metrics:
                perf_assert.assert_response_time(
                    metrics['avg_response_time_ms'],
                    benchmark_config['search_response_threshold_ms'],
                    f"Search for '{query}'"
                )
                
                assert metrics['error_rate'] == 0.0, (
                    f"Search for '{query}' had {metrics['error_rate']:.2%} error rate"
                )
                
                assert metrics['searches_per_second'] > 10.0, (
                    f"Search throughput {metrics['searches_per_second']:.2f} searches/sec too low"
                )
    
    def test_concurrent_search_performance(self, memory_benchmark, test_documents, 
                                         sample_test_data, benchmark_config):
        """Test concurrent search performance."""
        if not memory_benchmark.setup_test_index(test_documents[:30]):
            pytest.skip("Could not setup test index")
        
        metrics = memory_benchmark.benchmark_concurrent_search(
            sample_test_data['search_queries'],
            concurrent_users=3
        )
        
        if metrics:
            assert metrics['avg_response_time_ms'] < 2000.0, (
                f"Concurrent search took {metrics['avg_response_time_ms']:.2f}ms on average"
            )
            
            assert metrics['error_rate'] <= 0.05, (
                f"Concurrent search error rate {metrics['error_rate']:.2%} too high"
            )
            
            assert metrics['throughput_searches_per_sec'] > 5.0, (
                f"Concurrent search throughput {metrics['throughput_searches_per_sec']:.2f} too low"
            )
    
    def test_memory_usage_during_operations(self, memory_benchmark, test_documents, 
                                          performance_monitor, benchmark_config, perf_assert):
        """Test memory usage during memory system operations."""
        performance_monitor.start_monitoring(interval=0.2)
        
        # Setup index and perform operations
        if memory_benchmark.setup_test_index(test_documents[:10]):
            # Perform several searches
            for query in ["machine learning", "artificial intelligence", "data science"]:
                try:
                    memory_benchmark.benchmark_search(query, iterations=5)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Search failed: {e}")
        
        metrics = performance_monitor.stop_monitoring()
        
        if metrics:
            max_memory = max(m.memory_mb for m in metrics)
            avg_cpu = statistics.mean(m.cpu_percent for m in metrics)
            
            perf_assert.assert_memory_usage(
                max_memory,
                benchmark_config['memory_threshold_mb'],
                "Memory system operations"
            )
            
            perf_assert.assert_cpu_usage(
                avg_cpu,
                benchmark_config['cpu_threshold_percent'],
                "Memory system operations"
            )
    
    def test_search_accuracy_vs_performance_tradeoff(self, memory_benchmark, test_documents):
        """Test the tradeoff between search accuracy and performance."""
        if not memory_benchmark.setup_test_index(test_documents[:50]):
            pytest.skip("Could not setup test index")
        
        query = "machine learning algorithms"
        limit_values = [5, 10, 20, 50]
        
        for limit in limit_values:
            start_time = time.perf_counter()
            try:
                results = memory_benchmark.index.search(query, limit=limit)
                end_time = time.perf_counter()
                
                response_time = (end_time - start_time) * 1000
                
                print(f"Limit {limit}: {response_time:.2f}ms, {len(results)} results")
                
                # Higher limits should not dramatically increase response time
                assert response_time < 1000.0, (
                    f"Search with limit {limit} took {response_time:.2f}ms"
                )
                
            except Exception as e:
                print(f"Search with limit {limit} failed: {e}")
    
    @pytest.mark.slow
    def test_memory_system_stress_test(self, memory_benchmark, performance_monitor, benchmark_config):
        """Stress test the memory system with sustained operations."""
        if not memory_benchmark.setup_test_index():
            pytest.skip("Could not setup test index")
        
        performance_monitor.start_monitoring(interval=1.0)
        
        # Run sustained operations for 60 seconds
        start_time = time.time()
        operation_count = 0
        errors = 0
        
        queries = ["test query", "machine learning", "artificial intelligence", "data science"]
        
        while time.time() - start_time < 60:
            try:
                query = queries[operation_count % len(queries)]
                memory_benchmark.benchmark_search(query, iterations=1)
                operation_count += 1
            except Exception:
                errors += 1
            
            time.sleep(0.5)
        
        system_metrics = performance_monitor.stop_monitoring()
        
        # Verify system remained stable
        if system_metrics:
            avg_memory = statistics.mean(m.memory_mb for m in system_metrics)
            max_memory = max(m.memory_mb for m in system_metrics)
            
            assert max_memory < benchmark_config['memory_threshold_mb'], (
                f"Memory usage {max_memory:.2f}MB exceeded threshold during stress test"
            )
            
            # Check for memory leaks
            if len(system_metrics) > 10:
                early_avg = statistics.mean(m.memory_mb for m in system_metrics[:5])
                late_avg = statistics.mean(m.memory_mb for m in system_metrics[-5:])
                memory_growth = late_avg - early_avg
                
                assert memory_growth < 50.0, (
                    f"Memory grew by {memory_growth:.2f}MB during stress test (possible leak)"
                )
        
        error_rate = errors / operation_count if operation_count > 0 else 1.0
        assert error_rate <= 0.1, f"Error rate {error_rate:.2%} too high during stress test"


if __name__ == "__main__":
    # Allow running benchmarks directly
    benchmark = MemorySystemBenchmark()
    
    print("Running memory system benchmarks...")
    
    # Test documents
    test_docs = [
        "Machine learning is a subset of artificial intelligence.",
        "Python is popular for data science applications.",
        "Neural networks learn complex patterns from data."
    ]
    
    # Indexing benchmark
    indexing_metrics = benchmark.benchmark_indexing(test_docs)
    if indexing_metrics:
        print(f"Indexing: {indexing_metrics['total_duration_ms']:.2f}ms total, "
              f"{indexing_metrics['docs_per_second']:.2f} docs/sec")
    
    # Search benchmark
    if benchmark.setup_test_index(test_docs):
        search_metrics = benchmark.benchmark_search("machine learning", iterations=10)
        if search_metrics:
            print(f"Search: {search_metrics['avg_response_time_ms']:.2f}ms avg, "
                  f"{search_metrics['searches_per_second']:.2f} searches/sec")
    
    benchmark.cleanup_test_index()