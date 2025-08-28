#!/usr/bin/env python3
"""
Memory System Tests for GopiAI

Tests for txtai indexing, search, conversation storage, and data migration.
Covers Requirements 2.3 and 6.2 from the comprehensive testing system spec.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any
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

try:
    from gopiai.core.interfaces import MemoryInterface
    from gopiai.core.schema import MemoryEntry, SearchResult, Message, Conversation
except ImportError:
    # Fallback for testing without full module installation
    MemoryInterface = object
    MemoryEntry = MockMemoryEntry
    SearchResult = MockSearchResult


class TestTxtaiIndexing:
    """Test txtai indexing functionality."""
    
    @pytest.mark.unit
    def test_txtai_index_creation(self, mock_txtai_index):
        """Test creating a txtai index."""
        index = mock_txtai_index
        
        # Test initial state
        assert not index.is_built
        assert index.count() == 0
        
        # Test index creation
        documents = [
            {"id": "doc1", "text": "This is a test document"},
            {"id": "doc2", "text": "Another test document for indexing"}
        ]
        
        index.index(documents)
        
        assert index.is_built
        assert index.count() == 2
        assert index.documents == documents
    
    @pytest.mark.unit
    @pytest.mark.skip(reason="Requires sentence_transformers with compatible tokenizers version")
    def test_txtai_index_with_embeddings(self, mock_txtai_index, mock_embedding_model):
        """Test txtai index with custom embeddings."""
        index = mock_txtai_index
        
        documents = [
            {"id": "doc1", "text": "Machine learning document"},
            {"id": "doc2", "text": "Natural language processing text"}
        ]
        
        # Mock embedding generation
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            mock_transformer.return_value = mock_embedding_model
            
            index.index(documents)
            embeddings = index.transform(documents)
            
            assert len(embeddings) == len(documents)
            assert all(isinstance(emb, list) for emb in embeddings)
            assert all(len(emb) == 5 for emb in embeddings)  # Mock embedding size
    
    @pytest.mark.unit
    def test_txtai_index_persistence(self, mock_txtai_index, temp_memory_dir):
        """Test saving and loading txtai index."""
        index = mock_txtai_index
        index_path = os.path.join(temp_memory_dir, "test_index.json")
        
        # Create and save index
        documents = [{"id": "doc1", "text": "Persistent document"}]
        index.index(documents)
        index.save(index_path)
        
        # Create new index and load
        new_index = MockTxtaiIndex()
        new_index.load(index_path)
        
        assert new_index.is_built
        assert new_index.count() == 1
        assert new_index.documents == documents
    
    @pytest.mark.unit
    @pytest.mark.xfail_known_issue
    def test_txtai_large_document_indexing(self, mock_txtai_index):
        """Test indexing very large documents."""
        # This test documents a known issue with memory usage for large documents
        large_content = "Large document content. " * 10000  # ~250KB document
        
        documents = [{"id": "large_doc", "text": large_content}]
        
        # This might cause memory issues in real txtai
        index = mock_txtai_index
        index.index(documents)
        
        assert index.is_built
        assert index.count() == 1


class TestMemorySearch:
    """Test memory search functionality."""
    
    @pytest.mark.unit
    def test_basic_memory_search(self, mock_memory_system, sample_memory_entries):
        """Test basic memory search functionality."""
        memory_system = mock_memory_system
        
        # Add sample entries
        for entry in sample_memory_entries:
            memory_system.add_memory(
                content=entry.content,
                category=entry.category,
                conversation_id=entry.conversation_id,
                metadata=entry.metadata
            )
        
        # Test search
        results = memory_system.search_memory("Python programming")
        
        assert len(results) > 0
        assert any("Python programming" in result.get("content", "") for result in results)
        
        # Validate search results
        MemoryTestUtils.assert_search_results_valid(results)
    
    @pytest.mark.unit
    def test_category_filtered_search(self, mock_memory_system, sample_memory_entries):
        """Test search with category filtering."""
        memory_system = mock_memory_system
        
        # Add sample entries
        for entry in sample_memory_entries:
            memory_system.add_memory(
                content=entry.content,
                category=entry.category,
                conversation_id=entry.conversation_id
            )
        
        # Test category-specific search
        code_results = memory_system.search_memory("", category="code")
        docs_results = memory_system.search_memory("", category="docs")
        
        assert len(code_results) > 0
        assert len(docs_results) > 0
        assert all(result.get("category") == "code" for result in code_results)
        assert all(result.get("category") == "docs" for result in docs_results)
    
    @pytest.mark.unit
    def test_conversation_filtered_search(self, mock_memory_system, sample_memory_entries):
        """Test search with conversation filtering."""
        memory_system = mock_memory_system
        
        # Add sample entries
        for entry in sample_memory_entries:
            memory_system.add_memory(
                content=entry.content,
                category=entry.category,
                conversation_id=entry.conversation_id
            )
        
        # Test conversation-specific search
        conv1_results = memory_system.search_memory("", conversation_id="conv_1")
        conv2_results = memory_system.search_memory("", conversation_id="conv_2")
        
        assert len(conv1_results) > 0
        assert len(conv2_results) > 0
        assert all(result.get("conversation_id") == "conv_1" for result in conv1_results)
        assert all(result.get("conversation_id") == "conv_2" for result in conv2_results)
    
    @pytest.mark.unit
    def test_semantic_search_similarity(self, mock_txtai_index):
        """Test semantic search similarity scoring."""
        index = mock_txtai_index
        
        # Set up documents with varying similarity
        documents = [
            {"id": "doc1", "text": "Python programming tutorial"},
            {"id": "doc2", "text": "Python coding examples"},
            {"id": "doc3", "text": "Java programming guide"},
            {"id": "doc4", "text": "Cooking recipes collection"}
        ]
        
        index.index(documents)
        
        # Mock search results with decreasing similarity scores
        index.search_results = [
            {"id": "doc1", "text": "Python programming tutorial", "score": 0.95},
            {"id": "doc2", "text": "Python coding examples", "score": 0.87},
            {"id": "doc3", "text": "Java programming guide", "score": 0.65},
            {"id": "doc4", "text": "Cooking recipes collection", "score": 0.12}
        ]
        
        results = index.search("Python programming", limit=4)
        
        assert len(results) == 4
        assert results[0]["score"] > results[1]["score"]
        assert results[1]["score"] > results[2]["score"]
        assert results[2]["score"] > results[3]["score"]
    
    @pytest.mark.unit
    def test_empty_search_results(self, mock_memory_system):
        """Test handling of empty search results."""
        memory_system = mock_memory_system
        
        # Search in empty memory system
        results = memory_system.search_memory("nonexistent query")
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.unit
    def test_search_result_limit(self, mock_memory_system, sample_memory_entries):
        """Test search result limiting."""
        memory_system = mock_memory_system
        
        # Add many entries
        for i in range(20):
            memory_system.add_memory(
                content=f"Test document {i} with searchable content",
                category="test"
            )
        
        # Test different limits
        results_5 = memory_system.search_memory("searchable", limit=5)
        results_10 = memory_system.search_memory("searchable", limit=10)
        results_all = memory_system.search_memory("searchable", limit=100)
        
        assert len(results_5) <= 5
        assert len(results_10) <= 10
        assert len(results_all) <= 20


class TestConversationStorage:
    """Test conversation storage and retrieval."""
    
    @pytest.mark.unit
    def test_store_conversation(self, mock_memory_system, sample_conversations):
        """Test storing conversations in memory."""
        memory_system = mock_memory_system
        
        for conv_id, messages in sample_conversations.items():
            result = memory_system.store_conversation(conv_id, messages)
            assert result is True
        
        # Verify conversations are stored
        for conv_id, expected_messages in sample_conversations.items():
            stored_messages = memory_system.get_conversation_context(conv_id)
            assert stored_messages == expected_messages
    
    @pytest.mark.unit
    def test_conversation_context_retrieval(self, mock_memory_system, sample_conversations):
        """Test retrieving conversation context."""
        memory_system = mock_memory_system
        
        # Store conversations
        for conv_id, messages in sample_conversations.items():
            memory_system.store_conversation(conv_id, messages)
        
        # Test context retrieval
        context = memory_system.get_conversation_context("conv_1")
        
        assert len(context) == 4  # 4 messages in conv_1
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"
        assert "memory search" in context[0]["content"]
    
    @pytest.mark.unit
    def test_conversation_message_persistence(self, temp_memory_dir):
        """Test conversation message persistence to file."""
        memory_file = os.path.join(temp_memory_dir, "conversations.json")
        
        # Create test conversation data
        conversations = {
            "conv_1": [
                {"role": "user", "content": "Hello", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": "Hi there!", "timestamp": datetime.now().isoformat()}
            ]
        }
        
        # Save to file
        MemoryTestUtils.create_test_memory_file(memory_file, {"conversations": conversations})
        
        # Load and verify
        loaded_data = MemoryTestUtils.load_memory_file(memory_file)
        assert "conversations" in loaded_data
        assert "conv_1" in loaded_data["conversations"]
        assert len(loaded_data["conversations"]["conv_1"]) == 2
    
    @pytest.mark.unit
    def test_conversation_memory_integration(self, mock_memory_system):
        """Test integration between conversation storage and memory search."""
        memory_system = mock_memory_system
        
        # Store conversation
        messages = [
            {"role": "user", "content": "How do I use txtai for search?"},
            {"role": "assistant", "content": "You can use txtai.Embeddings() to create an index..."}
        ]
        memory_system.store_conversation("conv_test", messages)
        
        # Add conversation messages to searchable memory
        for msg in messages:
            memory_system.add_memory(
                content=msg["content"],
                category="conversation",
                conversation_id="conv_test",
                metadata={"role": msg["role"]}
            )
        
        # Search for conversation content
        results = memory_system.search_memory("txtai search", category="conversation")
        
        assert len(results) > 0
        assert any("txtai" in result.get("content", "") for result in results)
    
    @pytest.mark.unit
    def test_conversation_history_ordering(self, mock_memory_system):
        """Test that conversation history maintains message order."""
        memory_system = mock_memory_system
        
        # Create messages with timestamps
        messages = []
        base_time = datetime.now()
        
        for i in range(5):
            messages.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}",
                "timestamp": (base_time + timedelta(seconds=i)).isoformat()
            })
        
        memory_system.store_conversation("ordered_conv", messages)
        retrieved = memory_system.get_conversation_context("ordered_conv")
        
        # Verify order is maintained
        for i, msg in enumerate(retrieved):
            assert f"Message {i}" in msg["content"]


class TestMemoryPerformance:
    """Test memory system performance."""
    
    @pytest.mark.performance
    def test_search_performance_small_dataset(self, mock_memory_system, memory_performance_data):
        """Test search performance with small dataset."""
        memory_system = mock_memory_system
        
        # Add small dataset
        for i, content in enumerate(memory_performance_data["small_dataset"]):
            memory_system.add_memory(content, category="performance_test")
        
        # Measure search performance
        def search_func(query):
            return memory_system.search_memory(query, category="performance_test")
        
        performance = MemoryTestUtils.measure_search_performance(
            search_func, "test content", iterations=10
        )
        
        # Performance assertions (adjust thresholds as needed)
        assert performance["avg_time"] < 0.1  # Should be under 100ms on average
        assert performance["max_time"] < 0.5  # Max time should be under 500ms
    
    @pytest.mark.performance
    def test_search_performance_medium_dataset(self, mock_memory_system, memory_performance_data):
        """Test search performance with medium dataset."""
        memory_system = mock_memory_system
        
        # Add medium dataset
        for i, content in enumerate(memory_performance_data["medium_dataset"]):
            memory_system.add_memory(content, category="performance_test")
        
        def search_func(query):
            return memory_system.search_memory(query, category="performance_test")
        
        performance = MemoryTestUtils.measure_search_performance(
            search_func, "performance testing", iterations=5
        )
        
        # Medium dataset should still be reasonably fast
        assert performance["avg_time"] < 0.5  # Should be under 500ms on average
        assert performance["max_time"] < 2.0  # Max time should be under 2s
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_search_performance_large_dataset(self, mock_memory_system, memory_performance_data):
        """Test search performance with large dataset."""
        memory_system = mock_memory_system
        
        # Add large dataset (this test is marked as slow)
        for i, content in enumerate(memory_performance_data["large_dataset"][:1000]):  # Limit for testing
            memory_system.add_memory(content, category="performance_test")
        
        def search_func(query):
            return memory_system.search_memory(query, category="performance_test")
        
        performance = MemoryTestUtils.measure_search_performance(
            search_func, "memory system", iterations=3
        )
        
        # Large dataset performance (more lenient thresholds)
        assert performance["avg_time"] < 2.0  # Should be under 2s on average
        assert performance["max_time"] < 5.0  # Max time should be under 5s
    
    @pytest.mark.performance
    def test_indexing_performance(self, mock_txtai_index, memory_performance_data):
        """Test txtai indexing performance."""
        index = mock_txtai_index
        
        # Prepare documents for indexing
        documents = [
            {"id": f"doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["medium_dataset"][:100])
        ]
        
        # Measure indexing time
        start_time = time.time()
        index.index(documents)
        indexing_time = time.time() - start_time
        
        # Performance assertions
        assert indexing_time < 5.0  # Should index 100 docs in under 5 seconds
        assert index.is_built
        assert index.count() == 100
    
    @pytest.mark.performance
    def test_memory_usage_growth(self, mock_memory_system):
        """Test memory usage doesn't grow excessively."""
        memory_system = mock_memory_system
        
        # Add entries in batches and monitor
        batch_size = 100
        num_batches = 5
        
        for batch in range(num_batches):
            for i in range(batch_size):
                memory_system.add_memory(
                    content=f"Batch {batch} entry {i} with some content",
                    category="memory_test"
                )
            
            # Check that memory system can still search efficiently
            start_time = time.time()
            results = memory_system.search_memory("content", category="memory_test")
            search_time = time.time() - start_time
            
            # Search time shouldn't degrade significantly
            assert search_time < 0.5  # Should stay under 500ms
            assert len(results) > 0
    
    @pytest.mark.performance
    def test_concurrent_search_performance(self, mock_memory_system, memory_performance_data):
        """Test performance under concurrent search load."""
        import threading
        import queue
        
        memory_system = mock_memory_system
        
        # Add test data
        for content in memory_performance_data["small_dataset"]:
            memory_system.add_memory(content, category="concurrent_test")
        
        # Concurrent search function
        def search_worker(query_queue, result_queue):
            while True:
                try:
                    query = query_queue.get(timeout=1)
                    start_time = time.time()
                    results = memory_system.search_memory(query, category="concurrent_test")
                    end_time = time.time()
                    result_queue.put({
                        "query": query,
                        "time": end_time - start_time,
                        "results": len(results)
                    })
                    query_queue.task_done()
                except queue.Empty:
                    break
        
        # Set up concurrent test
        query_queue = queue.Queue()
        result_queue = queue.Queue()
        
        # Add queries
        for query in memory_performance_data["search_queries"] * 4:  # 20 total queries
            query_queue.put(query)
        
        # Start worker threads
        threads = []
        for _ in range(3):  # 3 concurrent workers
            thread = threading.Thread(target=search_worker, args=(query_queue, result_queue))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        query_queue.join()
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Performance assertions
        assert len(results) == 20  # All queries completed
        avg_time = sum(r["time"] for r in results) / len(results)
        assert avg_time < 0.2  # Average time under 200ms even with concurrency


class TestDataMigration:
    """Test data migration between versions."""
    
    @pytest.mark.unit
    def test_v1_to_v2_migration(self, temp_memory_dir, memory_migration_data):
        """Test migration from v1 to v2 memory format."""
        v1_file = os.path.join(temp_memory_dir, "memory_v1.json")
        v2_file = os.path.join(temp_memory_dir, "memory_v2.json")
        
        # Create v1 format file
        MemoryTestUtils.create_test_memory_file(v1_file, memory_migration_data["v1_format"])
        
        # Mock migration function
        def migrate_v1_to_v2(v1_path: str, v2_path: str):
            v1_data = MemoryTestUtils.load_memory_file(v1_path)
            
            v2_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "migrated_from": "1.0"
                }
            }
            
            # Convert v1 entries to v2 format
            for old_entry in v1_data.get("memories", []):
                new_entry = {
                    "id": old_entry["id"],
                    "content": old_entry.get("text", ""),  # v1 used 'text', v2 uses 'content'
                    "category": "general",  # Default category for migrated entries
                    "conversation_id": "migrated",
                    "created_at": old_entry.get("timestamp", datetime.now().isoformat()),
                    "metadata": {"migrated": True}
                }
                v2_data["memories"].append(new_entry)
            
            MemoryTestUtils.create_test_memory_file(v2_path, v2_data)
        
        # Perform migration
        migrate_v1_to_v2(v1_file, v2_file)
        
        # Verify migration
        v2_data = MemoryTestUtils.load_memory_file(v2_file)
        
        assert v2_data["metadata"]["version"] == "2.0"
        assert v2_data["metadata"]["migrated_from"] == "1.0"
        assert len(v2_data["memories"]) == 1
        
        migrated_entry = v2_data["memories"][0]
        assert migrated_entry["id"] == "old_1"
        assert migrated_entry["content"] == "Old format memory entry"
        assert migrated_entry["category"] == "general"
        assert migrated_entry["metadata"]["migrated"] is True
    
    @pytest.mark.unit
    def test_migration_data_integrity(self, temp_memory_dir):
        """Test that migration preserves data integrity."""
        original_file = os.path.join(temp_memory_dir, "original.json")
        migrated_file = os.path.join(temp_memory_dir, "migrated.json")
        
        # Create original data with various entry types
        original_data = {
            "memories": [
                {
                    "id": "entry_1",
                    "text": "Important conversation content",
                    "timestamp": "2023-06-01T10:00:00",
                    "user": "test_user"
                },
                {
                    "id": "entry_2", 
                    "text": "Code snippet: def search(query): return results",
                    "timestamp": "2023-06-01T11:00:00",
                    "type": "code"
                }
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(original_file, original_data)
        
        # Mock migration with data validation
        def migrate_with_validation(src_path: str, dst_path: str):
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {"version": "2.0", "created": datetime.now().isoformat()}
            }
            
            for entry in src_data["memories"]:
                # Validate original entry
                assert "id" in entry
                assert "text" in entry
                
                # Convert to new format
                new_entry = {
                    "id": entry["id"],
                    "content": entry["text"],
                    "category": entry.get("type", "general"),
                    "conversation_id": "migrated",
                    "created_at": entry.get("timestamp", datetime.now().isoformat()),
                    "metadata": {k: v for k, v in entry.items() if k not in ["id", "text", "timestamp", "type"]}
                }
                
                # Validate new entry
                MemoryTestUtils.assert_memory_entry_valid(new_entry)
                migrated_data["memories"].append(new_entry)
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
        
        # Perform migration
        migrate_with_validation(original_file, migrated_file)
        
        # Verify all data was preserved
        migrated_data = MemoryTestUtils.load_memory_file(migrated_file)
        
        assert len(migrated_data["memories"]) == 2
        
        # Check first entry
        entry1 = migrated_data["memories"][0]
        assert entry1["content"] == "Important conversation content"
        assert entry1["metadata"]["user"] == "test_user"
        
        # Check second entry
        entry2 = migrated_data["memories"][1]
        assert entry2["content"] == "Code snippet: def search(query): return results"
        assert entry2["category"] == "code"
    
    @pytest.mark.unit
    def test_migration_error_handling(self, temp_memory_dir):
        """Test migration error handling for corrupted data."""
        corrupted_file = os.path.join(temp_memory_dir, "corrupted.json")
        output_file = os.path.join(temp_memory_dir, "output.json")
        
        # Create corrupted data
        corrupted_data = {
            "memories": [
                {"id": "good_entry", "text": "Valid entry"},
                {"text": "Missing ID"},  # Invalid: no ID
                {"id": "empty_text", "text": ""},  # Invalid: empty text
                {"id": "valid_entry", "text": "Another valid entry"}
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(corrupted_file, corrupted_data)
        
        # Mock migration with error handling
        def migrate_with_error_handling(src_path: str, dst_path: str):
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "migration_errors": []
                }
            }
            
            for i, entry in enumerate(src_data["memories"]):
                try:
                    # Validate entry
                    if "id" not in entry:
                        raise ValueError(f"Entry {i}: Missing ID")
                    if not entry.get("text", "").strip():
                        raise ValueError(f"Entry {i}: Empty or missing text")
                    
                    # Convert valid entries
                    new_entry = {
                        "id": entry["id"],
                        "content": entry["text"],
                        "category": "general",
                        "conversation_id": "migrated",
                        "created_at": datetime.now().isoformat(),
                        "metadata": {}
                    }
                    
                    migrated_data["memories"].append(new_entry)
                    
                except ValueError as e:
                    migrated_data["metadata"]["migration_errors"].append(str(e))
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
        
        # Perform migration
        migrate_with_error_handling(corrupted_file, output_file)
        
        # Verify error handling
        result_data = MemoryTestUtils.load_memory_file(output_file)
        
        # Should have migrated only valid entries
        assert len(result_data["memories"]) == 2
        assert len(result_data["metadata"]["migration_errors"]) == 2
        
        # Check that valid entries were migrated
        migrated_ids = [entry["id"] for entry in result_data["memories"]]
        assert "good_entry" in migrated_ids
        assert "valid_entry" in migrated_ids
    
    @pytest.mark.unit
    def test_migration_rollback(self, temp_memory_dir):
        """Test migration rollback functionality."""
        original_file = os.path.join(temp_memory_dir, "original.json")
        backup_file = os.path.join(temp_memory_dir, "backup.json")
        migrated_file = os.path.join(temp_memory_dir, "migrated.json")
        
        # Create original data
        original_data = {
            "memories": [{"id": "test", "text": "Test content"}]
        }
        
        MemoryTestUtils.create_test_memory_file(original_file, original_data)
        
        # Mock migration with backup and rollback
        def migrate_with_rollback(src_path: str, dst_path: str, backup_path: str):
            # Create backup
            shutil.copy2(src_path, backup_path)
            
            try:
                # Simulate migration failure
                raise Exception("Migration failed")
                
            except Exception:
                # Rollback: restore from backup
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, src_path)
                    return False
            
            return True
        
        # Attempt migration
        success = migrate_with_rollback(original_file, migrated_file, backup_file)
        
        # Verify rollback
        assert not success
        assert os.path.exists(backup_file)
        
        # Original file should be unchanged
        restored_data = MemoryTestUtils.load_memory_file(original_file)
        assert restored_data == original_data


class TestMemorySystemIntegration:
    """Integration tests for memory system components."""
    
    @pytest.mark.integration
    def test_memory_tool_integration(self, temp_memory_dir):
        """Test integration with memory tools using mock implementation."""
        # Mock implementation of memory tool since gopiai_integration was removed
        class MockMemoryTool:
            def __init__(self):
                self.local_memory_file = ""
                self.memories = {}
            
            def init_files(self):
                # Initialize any required files
                if not os.path.exists(os.path.dirname(self.local_memory_file)):
                    os.makedirs(os.path.dirname(self.local_memory_file))
            
            def _run(self, action, *args):
                if action == "store":
                    key, content, category = args
                    self.memories[key] = {"content": content, "category": category}
                    return "✅ Memory stored successfully"
                elif action == "search":
                    query = args[0]
                    # Simple search in memory
                    results = [f"🔍 Found: {k} - {v['content']}" 
                             for k, v in self.memories.items() 
                             if query.lower() in v['content'].lower()]
                    return "\n".join(results) if results else "🔍 No results found"
                return "❌ Unknown action"
        
        # Initialize mock tool
        memory_tool = MockMemoryTool()
        memory_tool.local_memory_file = os.path.join(temp_memory_dir, "test_memory.json")
        memory_tool.init_files()
        
        # Test basic operations
        result = memory_tool._run("store", "test_key", "Test memory content", "test")
        assert "✅" in result  # Success indicator
        
        result = memory_tool._run("search", "Test memory")
        assert "🔍" in result  # Search indicator
        assert "Test memory content" in result
    
    @pytest.mark.integration
    def test_ui_memory_integration(self, temp_memory_dir):
        """Test integration with UI memory configuration."""
        try:
            # Try to import UI memory config
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
            from gopiai.ui.memory.memory_config import MEMORY_BASE_DIR, CHATS_FILE_PATH
            
            # Test that paths are accessible
            assert isinstance(MEMORY_BASE_DIR, Path)
            assert isinstance(CHATS_FILE_PATH, Path)
            
        except ImportError:
            pytest.skip("GopiAI UI memory config not available for integration test")
    
    @pytest.mark.integration
    @pytest.mark.xfail_known_issue
    def test_full_memory_pipeline(self, mock_memory_system):
        """Test full memory pipeline from storage to search."""
        # This test documents the expected full pipeline behavior
        memory_system = mock_memory_system
        
        # 1. Store conversation
        conversation = [
            {"role": "user", "content": "How do I implement semantic search?"},
            {"role": "assistant", "content": "You can use txtai embeddings for semantic search..."}
        ]
        
        memory_system.store_conversation("pipeline_test", conversation)
        
        # 2. Index conversation content
        for msg in conversation:
            memory_system.add_memory(
                content=msg["content"],
                category="conversation",
                conversation_id="pipeline_test"
            )
        
        # 3. Search for relevant content
        results = memory_system.search_memory("semantic search", conversation_id="pipeline_test")
        
        # 4. Verify pipeline worked
        assert len(results) > 0
        assert any("semantic search" in result.get("content", "") for result in results)
        
        # This test might fail due to integration complexity
        # but documents the expected behavior


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])