#!/usr/bin/env python3
"""
Memory System Test Fixtures for GopiAI Testing Infrastructure

Provides fixtures and mocks specifically for memory system testing.
"""

import os
import json
import tempfile
import pytest
import shutil
from typing import Dict, Any, Optional, List
from unittest.mock import Mock
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class MockMemoryEntry:
    """Mock memory entry for testing."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 0.0
    conversation_id: str = "default"
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "relevance_score": self.relevance_score,
            "conversation_id": self.conversation_id,
            "category": self.category
        }


@dataclass
class MockSearchResult:
    """Mock search result for testing."""
    entry: MockMemoryEntry
    score: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry": self.entry.to_dict(),
            "score": self.score,
            "context": self.context
        }


class MockTxtaiIndex:
    """Mock txtai index for testing."""
    
    def __init__(self):
        self.documents = []
        self.embeddings = {}
        self.config = {}
        self.is_built = False
        self.search_results = []
        
    def index(self, documents):
        """Mock index method."""
        self.documents = documents
        self.is_built = True
        
    def search(self, query: str, limit: int = 10):
        """Mock search method."""
        if self.search_results:
            return self.search_results[:limit]
        
        # Return mock results based on query
        results = []
        for i, doc in enumerate(self.documents[:limit]):
            score = 0.9 - (i * 0.1)  # Decreasing relevance
            results.append({
                "id": doc.get("id", f"doc_{i}"),
                "text": doc.get("text", doc.get("content", "")),
                "score": score
            })
        return results
    
    def transform(self, documents):
        """Mock transform method."""
        return [[0.1, 0.2, 0.3] for _ in documents]
    
    def save(self, path: str):
        """Mock save method."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump({
                "documents": self.documents,
                "config": self.config,
                "is_built": self.is_built
            }, f)
    
    def load(self, path: str):
        """Mock load method."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
                self.config = data.get("config", {})
                self.is_built = data.get("is_built", False)
    
    def count(self):
        """Mock count method."""
        return len(self.documents)
    
    def exists(self):
        """Mock exists method."""
        return self.is_built


class MockMemorySystem:
    """Mock memory system for testing."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.memory_file = os.path.join(self.temp_dir, "memory.json")
        self.vector_index_path = os.path.join(self.temp_dir, "vectors")
        self.conversations = {}
        self.memories = []
        self.search_results = []
        self.txtai_index = MockTxtaiIndex()
        
        # Initialize memory file
        self._ensure_memory_file()
    
    def _ensure_memory_file(self):
        """Ensure memory file exists."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "memories": [],
                    "metadata": {"created": datetime.now().isoformat()}
                }, f)
    
    def store_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        """Mock store conversation."""
        self.conversations[conversation_id] = messages
        return True
    
    def search_memory(self, query: str, limit: int = 10, 
                     category: str = None, conversation_id: str = None) -> List[Dict[str, Any]]:
        """Mock search memory."""
        if self.search_results:
            return self.search_results[:limit]
        
        # Filter memories based on criteria
        filtered_memories = []
        for memory in self.memories:
            if category and memory.get("category") != category:
                continue
            if conversation_id and memory.get("conversation_id") != conversation_id:
                continue
            
            # If no query, return all matching memories
            if not query:
                filtered_memories.append(memory)
            else:
                # Simple semantic matching for common terms
                content_lower = memory.get("content", "").lower()
                query_lower = query.lower()
                
                # Direct match
                if query_lower in content_lower:
                    filtered_memories.append(memory)
                # Semantic matching for common programming terms
                elif query_lower == "coding" and ("python" in content_lower or "programming" in content_lower):
                    filtered_memories.append(memory)
                elif query_lower == "recipe" and ("pasta" in content_lower or "sauce" in content_lower or "cook" in content_lower):
                    filtered_memories.append(memory)
                elif query_lower == "programming" and ("python" in content_lower or "learn" in content_lower):
                    filtered_memories.append(memory)
                # Handle txtai search queries
                elif "txtai" in query_lower and ("txtai" in content_lower or "search" in content_lower or "embeddings" in content_lower):
                    filtered_memories.append(memory)
                # Generic content matching for performance tests
                elif query_lower in ["test content", "performance testing", "memory system", "txtai search", "semantic similarity"]:
                    if "document" in content_lower or "content" in content_lower or "test" in content_lower:
                        filtered_memories.append(memory)
                # Match any query that contains common words
                elif any(word in content_lower for word in query_lower.split() if len(word) > 2):
                    filtered_memories.append(memory)
        
        return filtered_memories[:limit]
    
    def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Mock get conversation context."""
        return self.conversations.get(conversation_id, [])
    
    def clear_memory(self) -> bool:
        """Mock clear memory."""
        self.memories.clear()
        self.conversations.clear()
        return True
    
    def add_memory(self, content: str, category: str = "general", 
                  conversation_id: str = "default", metadata: Dict[str, Any] = None):
        """Add a memory entry for testing."""
        memory = {
            "id": str(uuid.uuid4()),
            "content": content,
            "category": category,
            "conversation_id": conversation_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "relevance_score": 0.0
        }
        self.memories.append(memory)
        return memory
    
    def set_search_results(self, results: List[Dict[str, Any]]):
        """Set mock search results."""
        self.search_results = results
    
    def cleanup(self):
        """Cleanup temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


@pytest.fixture
def temp_memory_dir():
    """Provide temporary directory for memory tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except (OSError, FileNotFoundError):
        # Ignore cleanup errors on Windows
        pass


@pytest.fixture
def mock_memory_system(temp_memory_dir):
    """Provide mock memory system."""
    system = MockMemorySystem(temp_memory_dir)
    yield system
    system.cleanup()


@pytest.fixture
def mock_txtai_index():
    """Provide mock txtai index."""
    return MockTxtaiIndex()


@pytest.fixture
def sample_memory_entries():
    """Provide sample memory entries for testing."""
    entries = [
        MockMemoryEntry(
            id="mem_1",
            content="This is a test conversation about Python programming",
            category="conversation",
            conversation_id="conv_1",
            metadata={"user": "test_user", "topic": "programming"}
        ),
        MockMemoryEntry(
            id="mem_2", 
            content="Documentation about GopiAI memory system implementation",
            category="docs",
            conversation_id="conv_1",
            metadata={"source": "documentation", "version": "2.0"}
        ),
        MockMemoryEntry(
            id="mem_3",
            content="Research findings on semantic search algorithms",
            category="research",
            conversation_id="conv_2",
            metadata={"author": "researcher", "date": "2024-01-01"}
        ),
        MockMemoryEntry(
            id="mem_4",
            content="Code snippet for txtai integration",
            category="code",
            conversation_id="conv_1",
            metadata={"language": "python", "function": "search"}
        )
    ]
    return entries


@pytest.fixture
def sample_conversations():
    """Provide sample conversations for testing."""
    conversations = {
        "conv_1": [
            {"role": "user", "content": "How do I implement memory search?"},
            {"role": "assistant", "content": "You can use txtai for semantic search..."},
            {"role": "user", "content": "Can you show me a code example?"},
            {"role": "assistant", "content": "Here's a Python example..."}
        ],
        "conv_2": [
            {"role": "user", "content": "What are the latest research findings?"},
            {"role": "assistant", "content": "Recent studies show that..."}
        ]
    }
    return conversations


@pytest.fixture
def memory_performance_data():
    """Provide performance test data."""
    return {
        "small_dataset": [f"Document {i} with some test content" for i in range(100)],
        "medium_dataset": [f"Document {i} with more detailed content for testing search performance" for i in range(1000)],
        "large_dataset": [f"Document {i} with extensive content to test memory system performance under load" for i in range(10000)],
        "search_queries": [
            "test content",
            "performance testing",
            "memory system",
            "txtai search",
            "semantic similarity"
        ]
    }


@pytest.fixture
def mock_embedding_model():
    """Provide mock embedding model."""
    mock_model = Mock()
    mock_model.encode.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5] for _ in range(10)]
    return mock_model


@pytest.fixture
def memory_migration_data():
    """Provide data for migration testing."""
    return {
        "v1_format": {
            "memories": [
                {
                    "id": "old_1",
                    "text": "Old format memory entry",
                    "timestamp": "2023-01-01T00:00:00"
                }
            ]
        },
        "v2_format": {
            "memories": [
                {
                    "id": "new_1",
                    "content": "New format memory entry",
                    "category": "general",
                    "conversation_id": "default",
                    "created_at": "2024-01-01T00:00:00",
                    "metadata": {}
                }
            ],
            "metadata": {"version": "2.0", "created": "2024-01-01T00:00:00"}
        }
    }


class MemoryTestUtils:
    """Utility functions for memory testing."""
    
    @staticmethod
    def create_test_memory_file(path: str, data: Dict[str, Any]):
        """Create a test memory file with given data."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_memory_file(path: str) -> Dict[str, Any]:
        """Load memory file data."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def assert_memory_entry_valid(entry: Dict[str, Any]):
        """Assert that a memory entry is valid."""
        required_fields = ["id", "content", "created_at"]
        for field in required_fields:
            assert field in entry, f"Missing required field: {field}"
        
        assert isinstance(entry["content"], str), "Content must be string"
        assert len(entry["content"]) > 0, "Content cannot be empty"
    
    @staticmethod
    def assert_search_results_valid(results: List[Dict[str, Any]]):
        """Assert that search results are valid."""
        assert isinstance(results, list), "Results must be a list"
        
        for result in results:
            assert "score" in result or "relevance_score" in result, "Result must have score"
            assert "content" in result or "text" in result, "Result must have content"
    
    @staticmethod
    def measure_search_performance(search_func, query: str, iterations: int = 100):
        """Measure search performance."""
        import time
        
        times = []
        for _ in range(iterations):
            start_time = time.time()
            search_func(query)
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times)
        }


# Export all fixtures and utilities
__all__ = [
    "MockMemoryEntry",
    "MockSearchResult", 
    "MockTxtaiIndex",
    "MockMemorySystem",
    "MemoryTestUtils",
    "temp_memory_dir",
    "mock_memory_system",
    "mock_txtai_index",
    "sample_memory_entries",
    "sample_conversations",
    "memory_performance_data",
    "mock_embedding_model",
    "memory_migration_data"
]