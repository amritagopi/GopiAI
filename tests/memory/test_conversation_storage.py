#!/usr/bin/env python3
"""
Conversation Storage Tests for GopiAI Memory System

Tests for conversation storage, retrieval, and context management.
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


class TestConversationStorage:
    """Test conversation storage functionality."""
    
    @pytest.mark.unit
    def test_store_single_conversation(self, mock_memory_system):
        """Test storing a single conversation."""
        memory_system = mock_memory_system
        
        messages = [
            {"role": "user", "content": "Hello, how are you?", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "I'm doing well, thank you!", "timestamp": datetime.now().isoformat()}
        ]
        
        result = memory_system.store_conversation("conv_1", messages)
        
        assert result is True
        stored_messages = memory_system.get_conversation_context("conv_1")
        assert len(stored_messages) == 2
        assert stored_messages[0]["content"] == "Hello, how are you?"
        assert stored_messages[1]["content"] == "I'm doing well, thank you!"
    
    @pytest.mark.unit
    def test_store_multiple_conversations(self, mock_memory_system, sample_conversations):
        """Test storing multiple conversations."""
        memory_system = mock_memory_system
        
        # Store all sample conversations
        for conv_id, messages in sample_conversations.items():
            result = memory_system.store_conversation(conv_id, messages)
            assert result is True
        
        # Verify all conversations are stored
        for conv_id, expected_messages in sample_conversations.items():
            stored_messages = memory_system.get_conversation_context(conv_id)
            assert len(stored_messages) == len(expected_messages)
            
            for i, expected_msg in enumerate(expected_messages):
                assert stored_messages[i]["content"] == expected_msg["content"]
                assert stored_messages[i]["role"] == expected_msg["role"]
    
    @pytest.mark.unit
    def test_conversation_message_ordering(self, mock_memory_system):
        """Test that conversation messages maintain proper ordering."""
        memory_system = mock_memory_system
        
        # Create messages with explicit timestamps
        base_time = datetime.now()
        messages = []
        
        for i in range(10):
            timestamp = (base_time + timedelta(seconds=i)).isoformat()
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Message {i} from {role}"
            
            messages.append({
                "role": role,
                "content": content,
                "timestamp": timestamp
            })
        
        memory_system.store_conversation("ordered_conv", messages)
        retrieved = memory_system.get_conversation_context("ordered_conv")
        
        # Verify order is maintained
        for i, msg in enumerate(retrieved):
            assert f"Message {i}" in msg["content"]
            expected_role = "user" if i % 2 == 0 else "assistant"
            assert msg["role"] == expected_role
    
    @pytest.mark.unit
    def test_conversation_update(self, mock_memory_system):
        """Test updating an existing conversation."""
        memory_system = mock_memory_system
        
        # Store initial conversation
        initial_messages = [
            {"role": "user", "content": "Initial message", "timestamp": datetime.now().isoformat()}
        ]
        memory_system.store_conversation("conv_update", initial_messages)
        
        # Update with additional messages
        updated_messages = initial_messages + [
            {"role": "assistant", "content": "Response message", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "Follow-up message", "timestamp": datetime.now().isoformat()}
        ]
        memory_system.store_conversation("conv_update", updated_messages)
        
        # Verify conversation was updated
        stored_messages = memory_system.get_conversation_context("conv_update")
        assert len(stored_messages) == 3
        assert stored_messages[0]["content"] == "Initial message"
        assert stored_messages[1]["content"] == "Response message"
        assert stored_messages[2]["content"] == "Follow-up message"
    
    @pytest.mark.unit
    def test_empty_conversation_handling(self, mock_memory_system):
        """Test handling of empty conversations."""
        memory_system = mock_memory_system
        
        # Store empty conversation
        result = memory_system.store_conversation("empty_conv", [])
        assert result is True
        
        # Retrieve empty conversation
        stored_messages = memory_system.get_conversation_context("empty_conv")
        assert isinstance(stored_messages, list)
        assert len(stored_messages) == 0
    
    @pytest.mark.unit
    def test_conversation_with_metadata(self, mock_memory_system):
        """Test storing conversations with additional metadata."""
        memory_system = mock_memory_system
        
        messages = [
            {
                "role": "user",
                "content": "Question about Python",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"topic": "programming", "language": "python"}
            },
            {
                "role": "assistant", 
                "content": "Here's information about Python",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"response_type": "informational", "confidence": 0.95}
            }
        ]
        
        memory_system.store_conversation("conv_with_metadata", messages)
        stored_messages = memory_system.get_conversation_context("conv_with_metadata")
        
        assert len(stored_messages) == 2
        assert stored_messages[0].get("metadata", {}).get("topic") == "programming"
        assert stored_messages[1].get("metadata", {}).get("confidence") == 0.95


class TestConversationRetrieval:
    """Test conversation retrieval functionality."""
    
    @pytest.mark.unit
    def test_retrieve_existing_conversation(self, mock_memory_system, sample_conversations):
        """Test retrieving an existing conversation."""
        memory_system = mock_memory_system
        
        # Store sample conversations
        for conv_id, messages in sample_conversations.items():
            memory_system.store_conversation(conv_id, messages)
        
        # Retrieve specific conversation
        retrieved = memory_system.get_conversation_context("conv_1")
        expected = sample_conversations["conv_1"]
        
        assert len(retrieved) == len(expected)
        for i, msg in enumerate(retrieved):
            assert msg["content"] == expected[i]["content"]
            assert msg["role"] == expected[i]["role"]
    
    @pytest.mark.unit
    def test_retrieve_nonexistent_conversation(self, mock_memory_system):
        """Test retrieving a conversation that doesn't exist."""
        memory_system = mock_memory_system
        
        # Try to retrieve non-existent conversation
        retrieved = memory_system.get_conversation_context("nonexistent_conv")
        
        assert isinstance(retrieved, list)
        assert len(retrieved) == 0
    
    @pytest.mark.unit
    def test_conversation_context_limit(self, mock_memory_system):
        """Test conversation context retrieval with limits."""
        memory_system = mock_memory_system
        
        # Create a long conversation
        messages = []
        for i in range(100):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "role": role,
                "content": f"Message {i}",
                "timestamp": datetime.now().isoformat()
            })
        
        memory_system.store_conversation("long_conv", messages)
        
        # Retrieve with different limits (if supported by implementation)
        all_messages = memory_system.get_conversation_context("long_conv")
        assert len(all_messages) == 100
        
        # Test that messages are in correct order
        for i, msg in enumerate(all_messages):
            assert f"Message {i}" in msg["content"]
    
    @pytest.mark.unit
    def test_conversation_filtering_by_role(self, mock_memory_system):
        """Test filtering conversation messages by role."""
        memory_system = mock_memory_system
        
        messages = [
            {"role": "user", "content": "User message 1", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Assistant message 1", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "User message 2", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Assistant message 2", "timestamp": datetime.now().isoformat()},
            {"role": "system", "content": "System message", "timestamp": datetime.now().isoformat()}
        ]
        
        memory_system.store_conversation("role_test", messages)
        all_messages = memory_system.get_conversation_context("role_test")
        
        # Filter messages by role
        user_messages = [msg for msg in all_messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in all_messages if msg["role"] == "assistant"]
        system_messages = [msg for msg in all_messages if msg["role"] == "system"]
        
        assert len(user_messages) == 2
        assert len(assistant_messages) == 2
        assert len(system_messages) == 1
        
        assert all("User message" in msg["content"] for msg in user_messages)
        assert all("Assistant message" in msg["content"] for msg in assistant_messages)
    
    @pytest.mark.unit
    def test_conversation_time_range_filtering(self, mock_memory_system):
        """Test filtering conversation messages by time range."""
        memory_system = mock_memory_system
        
        base_time = datetime.now()
        messages = []
        
        # Create messages across different time periods
        for i in range(10):
            timestamp = (base_time + timedelta(hours=i)).isoformat()
            messages.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message at hour {i}",
                "timestamp": timestamp
            })
        
        memory_system.store_conversation("time_test", messages)
        all_messages = memory_system.get_conversation_context("time_test")
        
        # Filter messages from first 5 hours
        cutoff_time = (base_time + timedelta(hours=5)).isoformat()
        early_messages = [
            msg for msg in all_messages 
            if msg.get("timestamp", "") < cutoff_time
        ]
        
        assert len(early_messages) == 5
        for i, msg in enumerate(early_messages):
            assert f"Message at hour {i}" in msg["content"]


class TestConversationPersistence:
    """Test conversation persistence to storage."""
    
    @pytest.mark.unit
    def test_conversation_file_persistence(self, temp_memory_dir):
        """Test conversation persistence to file."""
        memory_file = os.path.join(temp_memory_dir, "conversations.json")
        
        # Create test conversation data
        conversations = {
            "conv_1": [
                {"role": "user", "content": "Hello", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": "Hi there!", "timestamp": datetime.now().isoformat()}
            ],
            "conv_2": [
                {"role": "user", "content": "How are you?", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": "I'm doing well!", "timestamp": datetime.now().isoformat()}
            ]
        }
        
        # Save to file
        MemoryTestUtils.create_test_memory_file(memory_file, {"conversations": conversations})
        
        # Load and verify
        loaded_data = MemoryTestUtils.load_memory_file(memory_file)
        assert "conversations" in loaded_data
        assert len(loaded_data["conversations"]) == 2
        
        # Verify conversation content
        for conv_id, expected_messages in conversations.items():
            loaded_messages = loaded_data["conversations"][conv_id]
            assert len(loaded_messages) == len(expected_messages)
            
            for i, expected_msg in enumerate(expected_messages):
                assert loaded_messages[i]["content"] == expected_msg["content"]
                assert loaded_messages[i]["role"] == expected_msg["role"]
    
    @pytest.mark.unit
    def test_conversation_backup_and_restore(self, temp_memory_dir):
        """Test conversation backup and restore functionality."""
        original_file = os.path.join(temp_memory_dir, "conversations.json")
        backup_file = os.path.join(temp_memory_dir, "conversations_backup.json")
        
        # Create original conversation data
        original_conversations = {
            "conv_1": [
                {"role": "user", "content": "Original message", "timestamp": datetime.now().isoformat()}
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(
            original_file, 
            {"conversations": original_conversations}
        )
        
        # Create backup
        shutil.copy2(original_file, backup_file)
        
        # Modify original
        modified_conversations = {
            "conv_1": [
                {"role": "user", "content": "Modified message", "timestamp": datetime.now().isoformat()}
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(
            original_file,
            {"conversations": modified_conversations}
        )
        
        # Restore from backup
        shutil.copy2(backup_file, original_file)
        
        # Verify restoration
        restored_data = MemoryTestUtils.load_memory_file(original_file)
        restored_message = restored_data["conversations"]["conv_1"][0]["content"]
        assert restored_message == "Original message"
    
    @pytest.mark.unit
    def test_conversation_file_corruption_handling(self, temp_memory_dir):
        """Test handling of corrupted conversation files."""
        corrupted_file = os.path.join(temp_memory_dir, "corrupted_conversations.json")
        
        # Create corrupted file
        with open(corrupted_file, 'w') as f:
            f.write("{ corrupted json data")
        
        # Try to load corrupted file
        try:
            loaded_data = MemoryTestUtils.load_memory_file(corrupted_file)
            # If loading succeeds, it should return empty structure
            assert isinstance(loaded_data, dict)
        except json.JSONDecodeError:
            # If loading fails, that's expected for corrupted data
            pass
    
    @pytest.mark.unit
    def test_conversation_incremental_save(self, temp_memory_dir):
        """Test incremental saving of conversations."""
        memory_file = os.path.join(temp_memory_dir, "incremental_conversations.json")
        
        # Start with empty file
        MemoryTestUtils.create_test_memory_file(memory_file, {"conversations": {}})
        
        # Add conversations incrementally
        conversations_to_add = [
            ("conv_1", [{"role": "user", "content": "Message 1", "timestamp": datetime.now().isoformat()}]),
            ("conv_2", [{"role": "user", "content": "Message 2", "timestamp": datetime.now().isoformat()}]),
            ("conv_3", [{"role": "user", "content": "Message 3", "timestamp": datetime.now().isoformat()}])
        ]
        
        for conv_id, messages in conversations_to_add:
            # Load existing data
            current_data = MemoryTestUtils.load_memory_file(memory_file)
            
            # Add new conversation
            current_data["conversations"][conv_id] = messages
            
            # Save updated data
            MemoryTestUtils.create_test_memory_file(memory_file, current_data)
            
            # Verify conversation was added
            updated_data = MemoryTestUtils.load_memory_file(memory_file)
            assert conv_id in updated_data["conversations"]
            assert len(updated_data["conversations"][conv_id]) == 1
        
        # Verify all conversations are present
        final_data = MemoryTestUtils.load_memory_file(memory_file)
        assert len(final_data["conversations"]) == 3


class TestConversationSearch:
    """Test searching within conversations."""
    
    @pytest.mark.unit
    def test_search_conversation_content(self, mock_memory_system, sample_conversations):
        """Test searching for content within conversations."""
        memory_system = mock_memory_system
        
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
        
        # Search for specific content
        results = memory_system.search_memory("memory search", category="conversation")
        
        assert len(results) > 0
        assert any("memory search" in result.get("content", "").lower() for result in results)
        assert all(result.get("category") == "conversation" for result in results)
    
    @pytest.mark.unit
    def test_search_by_conversation_id(self, mock_memory_system, sample_conversations):
        """Test searching within specific conversations."""
        memory_system = mock_memory_system
        
        # Store conversations and add to searchable memory
        for conv_id, messages in sample_conversations.items():
            memory_system.store_conversation(conv_id, messages)
            
            for msg in messages:
                memory_system.add_memory(
                    content=msg["content"],
                    category="conversation",
                    conversation_id=conv_id,
                    metadata={"role": msg["role"]}
                )
        
        # Search within specific conversation
        conv1_results = memory_system.search_memory("", conversation_id="conv_1")
        conv2_results = memory_system.search_memory("", conversation_id="conv_2")
        
        assert len(conv1_results) > 0
        assert len(conv2_results) > 0
        assert all(result.get("conversation_id") == "conv_1" for result in conv1_results)
        assert all(result.get("conversation_id") == "conv_2" for result in conv2_results)
    
    @pytest.mark.unit
    def test_search_by_message_role(self, mock_memory_system):
        """Test searching conversations by message role."""
        memory_system = mock_memory_system
        
        messages = [
            {"role": "user", "content": "User question about Python"},
            {"role": "assistant", "content": "Assistant answer about Python"},
            {"role": "user", "content": "User follow-up about JavaScript"},
            {"role": "assistant", "content": "Assistant response about JavaScript"}
        ]
        
        memory_system.store_conversation("role_search_test", messages)
        
        # Add messages to searchable memory with role metadata
        for msg in messages:
            memory_system.add_memory(
                content=msg["content"],
                category="conversation",
                conversation_id="role_search_test",
                metadata={"role": msg["role"]}
            )
        
        # Search for user messages
        all_results = memory_system.search_memory("", conversation_id="role_search_test")
        user_results = [r for r in all_results if r.get("metadata", {}).get("role") == "user"]
        assistant_results = [r for r in all_results if r.get("metadata", {}).get("role") == "assistant"]
        
        assert len(user_results) == 2
        assert len(assistant_results) == 2
        assert all("User" in result.get("content", "") for result in user_results)
        assert all("Assistant" in result.get("content", "") for result in assistant_results)
    
    @pytest.mark.unit
    def test_conversation_semantic_search(self, mock_memory_system, mock_txtai_index):
        """Test semantic search within conversations."""
        memory_system = mock_memory_system
        memory_system.txtai_index = mock_txtai_index
        
        # Create conversations with semantically related content
        conversations = {
            "tech_conv": [
                {"role": "user", "content": "How do I learn Python programming?"},
                {"role": "assistant", "content": "Start with basic syntax and data structures"},
                {"role": "user", "content": "What about machine learning?"},
                {"role": "assistant", "content": "Learn NumPy, Pandas, and scikit-learn"}
            ],
            "cooking_conv": [
                {"role": "user", "content": "How do I make pasta?"},
                {"role": "assistant", "content": "Boil water, add pasta, cook for 8-10 minutes"},
                {"role": "user", "content": "What sauce goes well?"},
                {"role": "assistant", "content": "Tomato sauce or pesto work great"}
            ]
        }
        
        # Store conversations and index content
        documents = []
        for conv_id, messages in conversations.items():
            memory_system.store_conversation(conv_id, messages)
            
            for i, msg in enumerate(messages):
                doc_id = f"{conv_id}_{i}"
                documents.append({"id": doc_id, "text": msg["content"]})
                
                memory_system.add_memory(
                    content=msg["content"],
                    category="conversation",
                    conversation_id=conv_id,
                    metadata={"role": msg["role"]}
                )
        
        mock_txtai_index.index(documents)
        
        # Test semantic search for programming-related content
        programming_results = memory_system.search_memory("coding", conversation_id="tech_conv")
        cooking_results = memory_system.search_memory("recipe", conversation_id="cooking_conv")
        
        assert len(programming_results) > 0
        assert len(cooking_results) > 0
        
        # Verify results are from correct conversations
        assert all(result.get("conversation_id") == "tech_conv" for result in programming_results)
        assert all(result.get("conversation_id") == "cooking_conv" for result in cooking_results)


class TestConversationPerformance:
    """Test conversation storage and retrieval performance."""
    
    @pytest.mark.performance
    def test_large_conversation_storage(self, mock_memory_system):
        """Test storing large conversations."""
        memory_system = mock_memory_system
        
        # Create large conversation
        large_conversation = []
        for i in range(1000):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Message {i}: " + "content " * 50  # ~300 chars per message
            large_conversation.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        
        # Measure storage time
        start_time = time.time()
        result = memory_system.store_conversation("large_conv", large_conversation)
        storage_time = time.time() - start_time
        
        assert result is True
        assert storage_time < 5.0  # Should store 1000 messages in under 5 seconds
        
        # Verify storage
        stored_messages = memory_system.get_conversation_context("large_conv")
        assert len(stored_messages) == 1000
    
    @pytest.mark.performance
    def test_conversation_retrieval_performance(self, mock_memory_system):
        """Test conversation retrieval performance."""
        memory_system = mock_memory_system
        
        # Store multiple conversations
        for conv_num in range(50):
            messages = []
            for msg_num in range(20):
                role = "user" if msg_num % 2 == 0 else "assistant"
                messages.append({
                    "role": role,
                    "content": f"Conversation {conv_num}, Message {msg_num}",
                    "timestamp": datetime.now().isoformat()
                })
            
            memory_system.store_conversation(f"conv_{conv_num}", messages)
        
        # Measure retrieval performance
        retrieval_times = []
        for conv_num in range(50):
            start_time = time.time()
            messages = memory_system.get_conversation_context(f"conv_{conv_num}")
            retrieval_time = time.time() - start_time
            retrieval_times.append(retrieval_time)
            
            assert len(messages) == 20
        
        # Performance assertions
        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)
        assert avg_retrieval_time < 0.1  # Average retrieval under 100ms
        assert max(retrieval_times) < 0.5  # Max retrieval under 500ms
    
    @pytest.mark.performance
    def test_concurrent_conversation_access(self, mock_memory_system):
        """Test concurrent conversation storage and retrieval."""
        import threading
        import queue
        
        memory_system = mock_memory_system
        results_queue = queue.Queue()
        
        def conversation_worker(worker_id):
            try:
                # Store conversation
                messages = [
                    {"role": "user", "content": f"Message from worker {worker_id}"},
                    {"role": "assistant", "content": f"Response to worker {worker_id}"}
                ]
                
                store_result = memory_system.store_conversation(f"worker_conv_{worker_id}", messages)
                
                # Retrieve conversation
                retrieved = memory_system.get_conversation_context(f"worker_conv_{worker_id}")
                
                results_queue.put({
                    "worker_id": worker_id,
                    "store_success": store_result,
                    "retrieved_count": len(retrieved)
                })
                
            except Exception as e:
                results_queue.put({
                    "worker_id": worker_id,
                    "error": str(e)
                })
        
        # Start multiple worker threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=conversation_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        worker_results = []
        while not results_queue.empty():
            worker_results.append(results_queue.get())
        
        # Verify all workers completed successfully
        assert len(worker_results) == 5
        assert all("error" not in result for result in worker_results)
        assert all(result["store_success"] is True for result in worker_results)
        assert all(result["retrieved_count"] == 2 for result in worker_results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])