#!/usr/bin/env python3
"""
Memory Search Performance Tests for GopiAI Memory System

Tests for search performance, indexing speed, and scalability.
Part of task 8: Реализовать тесты системы памяти.
"""

import os
import sys
import json
import pytest
import tempfile
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add test infrastructure to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from memory_fixtures import (
    MockMemorySystem, MockTxtaiIndex, MockMemoryEntry, MockSearchResult,
    MemoryTestUtils, temp_memory_dir, mock_memory_system, mock_txtai_index,
    sample_memory_entries, sample_conversations, memory_performance_data,
    mock_embedding_model, memory_migration_data
)

# Add GopiAI modules to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()


class TestSearchPerformanceBasic:
    """Test basic search performance characteristics."""
    
    @pytest.mark.performance
    def test_small_dataset_search_performance(self, mock_memory_system, memory_performance_data):
        """Test search performance with small dataset (100 entries)."""
        memory_system = mock_memory_system
        
        # Add small dataset
        for i, content in enumerate(memory_performance_data["small_dataset"]):
            memory_system.add_memory(
                content=content,
                category="performance_test",
                metadata={"index": i}
            )
        
        # Measure search performance for different queries
        search_times = []
        for query in memory_performance_data["search_queries"]:
            start_time = time.time()
            results = memory_system.search_memory(query, category="performance_test")
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            assert isinstance(results, list)
        
        # Performance assertions
        avg_time = sum(search_times) / len(search_times)
        max_time = max(search_times)
        
        assert avg_time < 0.05  # Average under 50ms for small dataset
        assert max_time < 0.2   # Max under 200ms for small dataset
        
        # Verify search quality
        test_results = memory_system.search_memory("test content", category="performance_test")
        assert len(test_results) > 0
    
    @pytest.mark.performance
    def test_medium_dataset_search_performance(self, mock_memory_system, memory_performance_data):
        """Test search performance with medium dataset (1000 entries)."""
        memory_system = mock_memory_system
        
        # Add medium dataset
        for i, content in enumerate(memory_performance_data["medium_dataset"]):
            memory_system.add_memory(
                content=content,
                category="performance_test",
                metadata={"index": i}
            )
        
        # Measure search performance
        search_times = []
        result_counts = []
        
        for query in memory_performance_data["search_queries"]:
            start_time = time.time()
            results = memory_system.search_memory(query, category="performance_test", limit=10)
            search_time = time.time() - start_time
            
            search_times.append(search_time)
            result_counts.append(len(results))
            
            assert isinstance(results, list)
            assert len(results) <= 10  # Respect limit
        
        # Performance assertions
        avg_time = sum(search_times) / len(search_times)
        max_time = max(search_times)
        
        assert avg_time < 0.2   # Average under 200ms for medium dataset
        assert max_time < 1.0   # Max under 1s for medium dataset
        
        # Verify search returns results
        avg_results = sum(result_counts) / len(result_counts)
        assert avg_results > 0  # Should find some results on average
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_dataset_search_performance(self, mock_memory_system, memory_performance_data):
        """Test search performance with large dataset (limited to 2000 entries for testing)."""
        memory_system = mock_memory_system
        
        # Add large dataset (limited for testing)
        large_subset = memory_performance_data["large_dataset"][:2000]
        
        for i, content in enumerate(large_subset):
            memory_system.add_memory(
                content=content,
                category="performance_test",
                metadata={"index": i}
            )
        
        # Measure search performance
        search_times = []
        
        for query in memory_performance_data["search_queries"]:
            start_time = time.time()
            results = memory_system.search_memory(query, category="performance_test", limit=20)
            search_time = time.time() - start_time
            
            search_times.append(search_time)
            assert isinstance(results, list)
            assert len(results) <= 20
        
        # Performance assertions (more lenient for large dataset)
        avg_time = sum(search_times) / len(search_times)
        max_time = max(search_times)
        
        assert avg_time < 1.0   # Average under 1s for large dataset
        assert max_time < 3.0   # Max under 3s for large dataset
    
    @pytest.mark.performance
    def test_search_result_limit_performance(self, mock_memory_system, memory_performance_data):
        """Test how search performance varies with result limits."""
        memory_system = mock_memory_system
        
        # Add medium dataset
        for i, content in enumerate(memory_performance_data["medium_dataset"][:500]):
            memory_system.add_memory(
                content=content,
                category="limit_test",
                metadata={"index": i}
            )
        
        # Test different result limits
        limits = [1, 5, 10, 20, 50, 100]
        limit_times = {}
        
        for limit in limits:
            times = []
            for query in memory_performance_data["search_queries"][:3]:  # Test with 3 queries
                start_time = time.time()
                results = memory_system.search_memory(query, category="limit_test", limit=limit)
                search_time = time.time() - start_time
                times.append(search_time)
                
                assert len(results) <= limit
            
            limit_times[limit] = sum(times) / len(times)
        
        # Performance should not degrade significantly with higher limits
        # (for mock implementation, this might not show real performance characteristics)
        for limit in limits:
            assert limit_times[limit] < 0.5  # All limits should be under 500ms
    
    @pytest.mark.performance
    def test_repeated_search_performance(self, mock_memory_system, memory_performance_data):
        """Test performance of repeated searches (caching effects)."""
        memory_system = mock_memory_system
        
        # Add test data
        for i, content in enumerate(memory_performance_data["small_dataset"]):
            memory_system.add_memory(content, category="repeat_test")
        
        query = "test content"
        
        # Measure first search
        start_time = time.time()
        first_results = memory_system.search_memory(query, category="repeat_test")
        first_time = time.time() - start_time
        
        # Measure repeated searches
        repeat_times = []
        for _ in range(10):
            start_time = time.time()
            repeat_results = memory_system.search_memory(query, category="repeat_test")
            repeat_time = time.time() - start_time
            repeat_times.append(repeat_time)
            
            # Results should be consistent
            assert len(repeat_results) == len(first_results)
        
        avg_repeat_time = sum(repeat_times) / len(repeat_times)
        
        # Repeated searches should be fast (though mock might not show caching)
        assert avg_repeat_time < 0.1  # Average repeat search under 100ms
        assert all(t < 0.2 for t in repeat_times)  # All repeat searches under 200ms


class TestConcurrentSearchPerformance:
    """Test search performance under concurrent load."""
    
    @pytest.mark.performance
    def test_concurrent_search_load(self, mock_memory_system, memory_performance_data):
        """Test search performance with concurrent users."""
        memory_system = mock_memory_system
        
        # Add test data
        for i, content in enumerate(memory_performance_data["medium_dataset"][:200]):
            memory_system.add_memory(content, category="concurrent_test")
        
        results_queue = queue.Queue()
        
        def search_worker(worker_id, num_searches):
            worker_times = []
            for i in range(num_searches):
                query = memory_performance_data["search_queries"][i % len(memory_performance_data["search_queries"])]
                
                start_time = time.time()
                results = memory_system.search_memory(query, category="concurrent_test")
                search_time = time.time() - start_time
                
                worker_times.append(search_time)
            
            results_queue.put({
                "worker_id": worker_id,
                "times": worker_times,
                "avg_time": sum(worker_times) / len(worker_times),
                "max_time": max(worker_times)
            })
        
        # Start multiple worker threads
        num_workers = 5
        searches_per_worker = 10
        threads = []
        
        for i in range(num_workers):
            thread = threading.Thread(target=search_worker, args=(i, searches_per_worker))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        worker_results = []
        while not results_queue.empty():
            worker_results.append(results_queue.get())
        
        # Analyze concurrent performance
        assert len(worker_results) == num_workers
        
        all_times = []
        for result in worker_results:
            all_times.extend(result["times"])
            # Each worker should maintain reasonable performance
            assert result["avg_time"] < 0.3  # Average under 300ms per worker
            assert result["max_time"] < 1.0  # Max under 1s per worker
        
        # Overall concurrent performance
        overall_avg = sum(all_times) / len(all_times)
        overall_max = max(all_times)
        
        assert overall_avg < 0.3  # Overall average under 300ms
        assert overall_max < 1.0  # Overall max under 1s
    
    @pytest.mark.performance
    def test_mixed_read_write_performance(self, mock_memory_system, memory_performance_data):
        """Test performance with mixed read/write operations."""
        memory_system = mock_memory_system
        
        # Add initial data
        for i, content in enumerate(memory_performance_data["small_dataset"][:50]):
            memory_system.add_memory(content, category="mixed_test")
        
        results_queue = queue.Queue()
        
        def mixed_worker(worker_id):
            worker_times = {"search": [], "write": []}
            
            for i in range(20):
                if i % 3 == 0:  # Write operation
                    start_time = time.time()
                    memory_system.add_memory(
                        f"New content from worker {worker_id}, iteration {i}",
                        category="mixed_test"
                    )
                    write_time = time.time() - start_time
                    worker_times["write"].append(write_time)
                    
                else:  # Search operation
                    query = memory_performance_data["search_queries"][i % len(memory_performance_data["search_queries"])]
                    start_time = time.time()
                    results = memory_system.search_memory(query, category="mixed_test")
                    search_time = time.time() - start_time
                    worker_times["search"].append(search_time)
            
            results_queue.put({
                "worker_id": worker_id,
                "search_times": worker_times["search"],
                "write_times": worker_times["write"],
                "avg_search": sum(worker_times["search"]) / len(worker_times["search"]) if worker_times["search"] else 0,
                "avg_write": sum(worker_times["write"]) / len(worker_times["write"]) if worker_times["write"] else 0
            })
        
        # Start worker threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=mixed_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Analyze mixed operation performance
        worker_results = []
        while not results_queue.empty():
            worker_results.append(results_queue.get())
        
        assert len(worker_results) == 3
        
        for result in worker_results:
            # Search performance should remain good even with concurrent writes
            if result["avg_search"] > 0:
                assert result["avg_search"] < 0.2  # Search average under 200ms
            
            # Write performance should be reasonable
            if result["avg_write"] > 0:
                assert result["avg_write"] < 0.1  # Write average under 100ms
    
    @pytest.mark.performance
    def test_search_under_memory_pressure(self, mock_memory_system):
        """Test search performance under memory pressure."""
        memory_system = mock_memory_system
        
        # Add many large entries to create memory pressure
        large_entries = []
        for i in range(100):
            large_content = f"Large entry {i}: " + "content " * 1000  # ~7KB per entry
            large_entries.append(large_content)
            memory_system.add_memory(large_content, category="memory_pressure_test")
        
        # Measure search performance under memory pressure
        search_times = []
        
        for i in range(10):
            query = f"Large entry {i * 10}"  # Search for specific entries
            
            start_time = time.time()
            results = memory_system.search_memory(query, category="memory_pressure_test")
            search_time = time.time() - start_time
            
            search_times.append(search_time)
            assert len(results) > 0  # Should find the entry
        
        # Performance should still be reasonable under memory pressure
        avg_time = sum(search_times) / len(search_times)
        max_time = max(search_times)
        
        assert avg_time < 0.5  # Average under 500ms even with large entries
        assert max_time < 2.0  # Max under 2s even with large entries


class TestIndexingPerformance:
    """Test indexing and reindexing performance."""
    
    @pytest.mark.performance
    def test_initial_indexing_performance(self, mock_txtai_index, memory_performance_data):
        """Test initial indexing performance."""
        index = mock_txtai_index
        
        # Prepare documents for indexing
        documents = [
            {"id": f"doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["medium_dataset"][:500])
        ]
        
        # Measure initial indexing time
        start_time = time.time()
        index.index(documents)
        indexing_time = time.time() - start_time
        
        # Performance assertions
        assert indexing_time < 10.0  # Should index 500 docs in under 10 seconds
        assert index.is_built
        assert index.count() == 500
        
        # Test search performance after indexing
        start_time = time.time()
        results = index.search("test content", limit=10)
        search_time = time.time() - start_time
        
        assert search_time < 0.1  # Search should be fast after indexing
        assert isinstance(results, list)
    
    @pytest.mark.performance
    def test_incremental_indexing_performance(self, mock_txtai_index, memory_performance_data):
        """Test incremental indexing performance."""
        index = mock_txtai_index
        
        # Initial indexing
        initial_docs = [
            {"id": f"initial_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["small_dataset"])
        ]
        
        start_time = time.time()
        index.index(initial_docs)
        initial_time = time.time() - start_time
        
        initial_count = index.count()
        
        # Incremental additions
        incremental_times = []
        batch_size = 10
        
        for batch_num in range(5):  # Add 5 batches of 10 documents each
            batch_docs = []
            start_idx = batch_num * batch_size
            
            for i in range(batch_size):
                doc_idx = start_idx + i
                if doc_idx < len(memory_performance_data["medium_dataset"]):
                    batch_docs.append({
                        "id": f"incremental_{doc_idx}",
                        "text": memory_performance_data["medium_dataset"][doc_idx]
                    })
            
            if batch_docs:
                # Simulate incremental indexing by re-indexing all documents
                all_docs = initial_docs + batch_docs
                
                start_time = time.time()
                index.index(all_docs)
                incremental_time = time.time() - start_time
                
                incremental_times.append(incremental_time)
                initial_docs.extend(batch_docs)  # Update for next iteration
        
        # Performance assertions
        assert initial_time < 5.0  # Initial indexing should be fast
        
        for inc_time in incremental_times:
            assert inc_time < 8.0  # Incremental indexing should be reasonable
        
        # Indexing time shouldn't grow too much with size
        if len(incremental_times) > 1 and incremental_times[0] > 0:
            time_growth = incremental_times[-1] / incremental_times[0]
            assert time_growth < 3.0  # Time shouldn't grow more than 3x
    
    @pytest.mark.performance
    def test_reindexing_performance(self, mock_txtai_index, memory_performance_data):
        """Test full reindexing performance."""
        index = mock_txtai_index
        
        # Initial indexing
        documents = [
            {"id": f"doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["medium_dataset"][:200])
        ]
        
        index.index(documents)
        
        # Measure reindexing performance
        reindex_times = []
        
        for _ in range(3):  # Test multiple reindexing operations
            start_time = time.time()
            index.index(documents)  # Reindex same documents
            reindex_time = time.time() - start_time
            reindex_times.append(reindex_time)
        
        # Performance assertions
        avg_reindex_time = sum(reindex_times) / len(reindex_times)
        max_reindex_time = max(reindex_times)
        
        assert avg_reindex_time < 8.0  # Average reindexing under 8 seconds
        assert max_reindex_time < 15.0  # Max reindexing under 15 seconds
        
        # Verify index integrity after reindexing
        assert index.is_built
        assert index.count() == 200
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_scale_indexing_performance(self, mock_txtai_index, memory_performance_data):
        """Test indexing performance with large document sets."""
        index = mock_txtai_index
        
        # Prepare large document set (limited for testing)
        large_docs = [
            {"id": f"large_doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["large_dataset"][:1000])
        ]
        
        # Measure large-scale indexing
        start_time = time.time()
        index.index(large_docs)
        large_indexing_time = time.time() - start_time
        
        # Performance assertions
        assert large_indexing_time < 60.0  # Should index 1000 docs in under 1 minute
        assert index.is_built
        assert index.count() == 1000
        
        # Test search performance on large index
        search_times = []
        for query in memory_performance_data["search_queries"]:
            start_time = time.time()
            results = index.search(query, limit=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            assert isinstance(results, list)
            assert len(results) <= 10
        
        # Search should still be fast on large index
        avg_search_time = sum(search_times) / len(search_times)
        assert avg_search_time < 0.2  # Average search under 200ms even on large index


class TestMemoryUsagePerformance:
    """Test memory usage characteristics during search operations."""
    
    @pytest.mark.performance
    def test_memory_usage_growth(self, mock_memory_system, memory_performance_data):
        """Test that memory usage doesn't grow excessively during operations."""
        memory_system = mock_memory_system
        
        # Add entries in batches and monitor search performance
        batch_size = 50
        num_batches = 10
        search_times = []
        
        for batch in range(num_batches):
            # Add batch of entries
            for i in range(batch_size):
                entry_idx = batch * batch_size + i
                if entry_idx < len(memory_performance_data["medium_dataset"]):
                    memory_system.add_memory(
                        content=memory_performance_data["medium_dataset"][entry_idx],
                        category="memory_growth_test",
                        metadata={"batch": batch, "index": i}
                    )
            
            # Test search performance after each batch
            start_time = time.time()
            results = memory_system.search_memory("test content", category="memory_growth_test")
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            assert isinstance(results, list)
        
        # Search performance shouldn't degrade significantly
        if len(search_times) > 1:
            first_half_avg = sum(search_times[:len(search_times)//2]) / (len(search_times)//2)
            second_half_avg = sum(search_times[len(search_times)//2:]) / (len(search_times) - len(search_times)//2)
            
            # Performance degradation should be minimal
            performance_ratio = second_half_avg / first_half_avg if first_half_avg > 0 else 1
            assert performance_ratio < 3.0  # Performance shouldn't degrade more than 3x
    
    @pytest.mark.performance
    def test_search_result_memory_efficiency(self, mock_memory_system, memory_performance_data):
        """Test memory efficiency of search results."""
        memory_system = mock_memory_system
        
        # Add large entries
        for i, content in enumerate(memory_performance_data["medium_dataset"][:100]):
            # Make entries larger to test memory efficiency
            large_content = content + " " + "additional content " * 100
            memory_system.add_memory(
                content=large_content,
                category="memory_efficiency_test",
                metadata={"size": len(large_content)}
            )
        
        # Test different result limits
        limits = [1, 5, 10, 25, 50]
        
        for limit in limits:
            # Search with different limits
            results = memory_system.search_memory("content", category="memory_efficiency_test", limit=limit)
            
            assert len(results) <= limit
            assert isinstance(results, list)
            
            # Verify results don't contain excessive data
            for result in results:
                assert isinstance(result, dict)
                # Results should contain necessary fields but not be bloated
                assert "content" in result or "text" in result
    
    @pytest.mark.performance
    def test_cleanup_after_operations(self, mock_memory_system):
        """Test that memory is properly cleaned up after operations."""
        memory_system = mock_memory_system
        
        # Perform many operations
        for i in range(100):
            # Add memory
            memory_system.add_memory(f"Temporary content {i}", category="cleanup_test")
            
            # Search
            results = memory_system.search_memory(f"content {i}", category="cleanup_test")
            
            # Verify operation completed
            assert isinstance(results, list)
        
        # Clear memory to test cleanup
        cleanup_result = memory_system.clear_memory()
        assert cleanup_result is True
        
        # Verify memory was cleared
        results = memory_system.search_memory("content", category="cleanup_test")
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])