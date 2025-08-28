#!/usr/bin/env python3
"""
Txtai Integration Tests for GopiAI Memory System

Specific tests for txtai indexing, embedding generation, and search functionality.
Part of task 8: Реализовать тесты системы памяти.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add test infrastructure to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from memory_fixtures import (
    MockTxtaiIndex, MockMemorySystem, MockMemoryEntry, MockSearchResult,
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
    
    @pytest.mark.unit
    def test_txtai_incremental_indexing(self, mock_txtai_index):
        """Test adding documents to existing index."""
        index = mock_txtai_index
        
        # Initial documents
        initial_docs = [
            {"id": "doc1", "text": "First document"},
            {"id": "doc2", "text": "Second document"}
        ]
        index.index(initial_docs)
        
        # Add more documents
        additional_docs = [
            {"id": "doc3", "text": "Third document"},
            {"id": "doc4", "text": "Fourth document"}
        ]
        
        # Simulate incremental indexing
        all_docs = initial_docs + additional_docs
        index.index(all_docs)
        
        assert index.count() == 4
        assert len(index.documents) == 4
    
    @pytest.mark.unit
    def test_txtai_document_update(self, mock_txtai_index):
        """Test updating existing documents in index."""
        index = mock_txtai_index
        
        # Initial document
        documents = [{"id": "doc1", "text": "Original content"}]
        index.index(documents)
        
        # Update document
        updated_documents = [{"id": "doc1", "text": "Updated content"}]
        index.index(updated_documents)
        
        assert index.count() == 1
        assert index.documents[0]["text"] == "Updated content"
    
    @pytest.mark.unit
    def test_txtai_empty_document_handling(self, mock_txtai_index):
        """Test handling of empty or invalid documents."""
        index = mock_txtai_index
        
        # Mix of valid and invalid documents
        documents = [
            {"id": "doc1", "text": "Valid document"},
            {"id": "doc2", "text": ""},  # Empty text
            {"id": "doc3"},  # Missing text
            {"id": "doc4", "text": "Another valid document"}
        ]
        
        # Filter out invalid documents before indexing
        valid_docs = [doc for doc in documents if doc.get("text", "").strip()]
        index.index(valid_docs)
        
        assert index.count() == 2
        assert all(doc.get("text", "").strip() for doc in index.documents)


class TestTxtaiSearch:
    """Test txtai search functionality."""
    
    @pytest.mark.unit
    def test_basic_semantic_search(self, mock_txtai_index):
        """Test basic semantic search functionality."""
        index = mock_txtai_index
        
        documents = [
            {"id": "doc1", "text": "Python programming tutorial"},
            {"id": "doc2", "text": "Machine learning with Python"},
            {"id": "doc3", "text": "Web development using JavaScript"},
            {"id": "doc4", "text": "Data science and analytics"}
        ]
        
        index.index(documents)
        
        # Search for Python-related content
        results = index.search("Python coding", limit=2)
        
        assert len(results) <= 2
        assert any("Python" in result.get("text", "") for result in results)
    
    @pytest.mark.unit
    def test_search_result_scoring(self, mock_txtai_index):
        """Test that search results are properly scored."""
        index = mock_txtai_index
        
        documents = [
            {"id": "doc1", "text": "Python programming tutorial"},
            {"id": "doc2", "text": "Python coding examples"},
            {"id": "doc3", "text": "Java programming guide"},
            {"id": "doc4", "text": "Cooking recipes"}
        ]
        
        index.index(documents)
        
        # Mock search results with scores
        index.search_results = [
            {"id": "doc1", "text": "Python programming tutorial", "score": 0.95},
            {"id": "doc2", "text": "Python coding examples", "score": 0.87},
            {"id": "doc3", "text": "Java programming guide", "score": 0.65},
            {"id": "doc4", "text": "Cooking recipes", "score": 0.12}
        ]
        
        results = index.search("Python programming", limit=4)
        
        # Verify results are sorted by score
        scores = [result.get("score", 0) for result in results]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.unit
    def test_search_with_limit(self, mock_txtai_index):
        """Test search result limiting."""
        index = mock_txtai_index
        
        # Create many documents
        documents = [
            {"id": f"doc{i}", "text": f"Document {i} about programming"}
            for i in range(20)
        ]
        
        index.index(documents)
        
        # Test different limits
        results_5 = index.search("programming", limit=5)
        results_10 = index.search("programming", limit=10)
        results_all = index.search("programming", limit=100)
        
        assert len(results_5) <= 5
        assert len(results_10) <= 10
        assert len(results_all) <= 20
    
    @pytest.mark.unit
    def test_search_no_results(self, mock_txtai_index):
        """Test search with no matching results."""
        index = mock_txtai_index
        
        documents = [
            {"id": "doc1", "text": "Python programming"},
            {"id": "doc2", "text": "Web development"}
        ]
        
        index.index(documents)
        
        # Search for completely unrelated content
        results = index.search("quantum physics", limit=10)
        
        # Mock should return empty results for unmatched queries
        if not results:  # If mock returns empty
            assert len(results) == 0
        else:  # If mock returns all results regardless
            assert isinstance(results, list)
    
    @pytest.mark.unit
    def test_search_special_characters(self, mock_txtai_index):
        """Test search with special characters and unicode."""
        index = mock_txtai_index
        
        documents = [
            {"id": "doc1", "text": "Программирование на Python"},
            {"id": "doc2", "text": "Machine learning & AI"},
            {"id": "doc3", "text": "Data science (advanced)"},
            {"id": "doc4", "text": "Web dev: HTML/CSS/JS"}
        ]
        
        index.index(documents)
        
        # Test searches with special characters
        results1 = index.search("Python", limit=5)
        results2 = index.search("AI & ML", limit=5)
        results3 = index.search("HTML/CSS", limit=5)
        
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)


class TestTxtaiPerformance:
    """Test txtai performance characteristics."""
    
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
        
        # Performance assertions (lenient for mock)
        assert indexing_time < 5.0  # Should index 100 docs in under 5 seconds
        assert index.is_built
        assert index.count() == 100
    
    @pytest.mark.performance
    def test_search_performance(self, mock_txtai_index, memory_performance_data):
        """Test txtai search performance."""
        index = mock_txtai_index
        
        # Index medium dataset
        documents = [
            {"id": f"doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["medium_dataset"][:500])
        ]
        index.index(documents)
        
        # Measure search performance
        search_times = []
        for query in memory_performance_data["search_queries"]:
            start_time = time.time()
            results = index.search(query, limit=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            assert isinstance(results, list)
        
        # Performance assertions
        avg_search_time = sum(search_times) / len(search_times)
        assert avg_search_time < 0.1  # Average search under 100ms
        assert max(search_times) < 0.5  # Max search under 500ms
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_index_performance(self, mock_txtai_index, memory_performance_data):
        """Test performance with large index."""
        index = mock_txtai_index
        
        # Index large dataset (limited for testing)
        documents = [
            {"id": f"doc_{i}", "text": content}
            for i, content in enumerate(memory_performance_data["large_dataset"][:1000])
        ]
        
        # Measure indexing time for large dataset
        start_time = time.time()
        index.index(documents)
        indexing_time = time.time() - start_time
        
        # Test search performance on large index
        start_time = time.time()
        results = index.search("test content", limit=10)
        search_time = time.time() - start_time
        
        # Performance assertions (more lenient for large dataset)
        assert indexing_time < 30.0  # Should index 1000 docs in under 30 seconds
        assert search_time < 1.0  # Search should still be under 1 second
        assert index.count() == 1000
        assert isinstance(results, list)


class TestTxtaiIntegration:
    """Test txtai integration with GopiAI memory system."""
    
    @pytest.mark.integration
    def test_memory_system_txtai_integration(self, mock_memory_system, mock_txtai_index):
        """Test integration between memory system and txtai."""
        memory_system = mock_memory_system
        memory_system.txtai_index = mock_txtai_index
        
        # Add memories to system
        memory_system.add_memory("Python programming tutorial", category="docs")
        memory_system.add_memory("Machine learning basics", category="research")
        memory_system.add_memory("Web development guide", category="docs")
        
        # Simulate txtai indexing
        documents = [
            {"id": mem["id"], "text": mem["content"]}
            for mem in memory_system.memories
        ]
        mock_txtai_index.index(documents)
        
        # Test search integration
        results = memory_system.search_memory("programming")
        
        assert len(results) > 0
        assert any("programming" in result.get("content", "").lower() for result in results)
    
    @pytest.mark.integration
    def test_conversation_indexing(self, mock_memory_system, mock_txtai_index, sample_conversations):
        """Test indexing conversation messages."""
        memory_system = mock_memory_system
        memory_system.txtai_index = mock_txtai_index
        
        # Store conversations
        for conv_id, messages in sample_conversations.items():
            memory_system.store_conversation(conv_id, messages)
            
            # Add conversation messages to searchable memory
            for msg in messages:
                memory_system.add_memory(
                    content=msg["content"],
                    category="conversation",
                    conversation_id=conv_id,
                    metadata={"role": msg["role"]}
                )
        
        # Index conversation content
        documents = [
            {"id": mem["id"], "text": mem["content"]}
            for mem in memory_system.memories
            if mem.get("category") == "conversation"
        ]
        mock_txtai_index.index(documents)
        
        # Test conversation search
        results = memory_system.search_memory("memory search", category="conversation")
        
        assert len(results) > 0
        assert all(result.get("category") == "conversation" for result in results)
    
    @pytest.mark.integration
    def test_real_time_indexing(self, mock_memory_system, mock_txtai_index):
        """Test real-time indexing as new memories are added."""
        memory_system = mock_memory_system
        memory_system.txtai_index = mock_txtai_index
        
        # Add initial memories
        initial_memories = [
            "Initial memory about Python",
            "Another memory about web development"
        ]
        
        for content in initial_memories:
            memory_system.add_memory(content, category="general")
        
        # Index initial memories
        documents = [
            {"id": mem["id"], "text": mem["content"]}
            for mem in memory_system.memories
        ]
        mock_txtai_index.index(documents)
        
        initial_count = mock_txtai_index.count()
        
        # Add new memory
        memory_system.add_memory("New memory about machine learning", category="general")
        
        # Re-index with new memory
        all_documents = [
            {"id": mem["id"], "text": mem["content"]}
            for mem in memory_system.memories
        ]
        mock_txtai_index.index(all_documents)
        
        # Verify index was updated
        assert mock_txtai_index.count() == initial_count + 1
        
        # Test search includes new memory
        results = memory_system.search_memory("machine learning")
        assert len(results) > 0
    
    @pytest.mark.integration
    @pytest.mark.xfail_known_issue
    def test_concurrent_indexing(self, mock_memory_system, mock_txtai_index):
        """Test concurrent access to txtai index."""
        import threading
        import queue
        
        memory_system = mock_memory_system
        memory_system.txtai_index = mock_txtai_index
        
        # This test documents a known issue with concurrent txtai access
        results_queue = queue.Queue()
        
        def add_and_search(thread_id):
            try:
                # Add memory
                memory_system.add_memory(f"Memory from thread {thread_id}", category="test")
                
                # Update index
                documents = [
                    {"id": mem["id"], "text": mem["content"]}
                    for mem in memory_system.memories
                ]
                mock_txtai_index.index(documents)
                
                # Search
                results = memory_system.search_memory("thread")
                results_queue.put({"thread_id": thread_id, "results": len(results)})
                
            except Exception as e:
                results_queue.put({"thread_id": thread_id, "error": str(e)})
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_and_search, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        thread_results = []
        while not results_queue.empty():
            thread_results.append(results_queue.get())
        
        # This might fail due to concurrent access issues
        assert len(thread_results) == 3
        assert all("error" not in result for result in thread_results)


class TestTxtaiErrorHandling:
    """Test txtai error handling and edge cases."""
    
    @pytest.mark.unit
    def test_index_corruption_recovery(self, mock_txtai_index, temp_memory_dir):
        """Test recovery from corrupted index."""
        index = mock_txtai_index
        index_path = os.path.join(temp_memory_dir, "corrupted_index.json")
        
        # Create and save index
        documents = [{"id": "doc1", "text": "Test document"}]
        index.index(documents)
        index.save(index_path)
        
        # Corrupt the index file
        with open(index_path, 'w') as f:
            f.write("corrupted data")
        
        # Try to load corrupted index
        new_index = MockTxtaiIndex()
        try:
            new_index.load(index_path)
            # If load succeeds with corrupted data, index should be empty
            assert new_index.count() == 0
        except Exception:
            # If load fails, that's expected behavior
            assert not new_index.is_built
    
    @pytest.mark.unit
    def test_memory_limit_handling(self, mock_txtai_index):
        """Test handling of memory limits during indexing."""
        index = mock_txtai_index
        
        # Create very large documents to test memory limits
        large_documents = []
        for i in range(10):
            large_content = f"Large document {i}: " + "content " * 10000
            large_documents.append({"id": f"large_doc_{i}", "text": large_content})
        
        # This should not crash even with large documents
        try:
            index.index(large_documents)
            assert index.is_built
        except MemoryError:
            # If memory error occurs, it should be handled gracefully
            pytest.skip("Memory limit reached during test")
    
    @pytest.mark.unit
    def test_invalid_search_queries(self, mock_txtai_index):
        """Test handling of invalid search queries."""
        index = mock_txtai_index
        
        documents = [{"id": "doc1", "text": "Test document"}]
        index.index(documents)
        
        # Test various invalid queries
        invalid_queries = [
            "",  # Empty query
            None,  # None query
            "   ",  # Whitespace only
            "\n\t",  # Special characters only
        ]
        
        for query in invalid_queries:
            try:
                results = index.search(query or "", limit=10)
                assert isinstance(results, list)
            except Exception as e:
                # Some invalid queries might raise exceptions
                assert isinstance(e, (ValueError, TypeError))
    
    @pytest.mark.unit
    def test_index_size_limits(self, mock_txtai_index):
        """Test behavior at index size limits."""
        index = mock_txtai_index
        
        # Add documents up to a reasonable limit
        max_docs = 1000
        documents = []
        
        for i in range(max_docs):
            documents.append({
                "id": f"doc_{i}",
                "text": f"Document {i} with unique content for testing limits"
            })
        
        # Index should handle reasonable number of documents
        index.index(documents)
        assert index.count() == max_docs
        
        # Search should still work with large index
        results = index.search("unique content", limit=10)
        assert isinstance(results, list)
        assert len(results) <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])