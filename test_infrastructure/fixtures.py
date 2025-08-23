#!/usr/bin/env python3
"""
Common Test Fixtures and Mocks for GopiAI Testing Infrastructure

Provides reusable fixtures and mocks for all GopiAI modules.
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass


@dataclass
class MockAIResponse:
    """Mock response from AI services."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = None


@dataclass
class MockConversation:
    """Mock conversation data."""
    id: str
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]


class AIServiceMocker:
    """Mock AI service responses for testing."""
    
    def __init__(self):
        self.responses = []
        self.call_count = 0
        self.provider_responses = {
            "openai": [],
            "anthropic": [],
            "google": [],
            "openrouter": []
        }
    
    def add_response(self, content: str, model: str = "test-model", 
                    provider: str = "test-provider"):
        """Add a mock response to the queue."""
        response = MockAIResponse(
            content=content,
            model=model,
            provider=provider,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )
        self.responses.append(response)
    
    def add_provider_response(self, provider: str, content: str, model: str = None):
        """Add a response for a specific provider."""
        if model is None:
            model_map = {
                "openai": "gpt-4",
                "anthropic": "claude-3-sonnet",
                "google": "gemini-pro",
                "openrouter": "openrouter/auto"
            }
            model = model_map.get(provider, "test-model")
        
        response = MockAIResponse(
            content=content,
            model=model,
            provider=provider,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )
        self.provider_responses[provider].append(response)
    
    def get_next_response(self) -> MockAIResponse:
        """Get the next mock response."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        # Default response if no more responses queued
        return MockAIResponse(
            content="Mock AI response",
            model="default-model",
            provider="default-provider",
            usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15}
        )
    
    def get_provider_response(self, provider: str) -> MockAIResponse:
        """Get a response for a specific provider."""
        if provider in self.provider_responses and self.provider_responses[provider]:
            return self.provider_responses[provider].pop(0)
        return self.get_next_response()
    
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = self.get_provider_response("openai").content
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client
    
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = self.get_provider_response("anthropic").content
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_response
        return mock_client


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        "CREWAI_API_URL": "http://localhost:5051",
        
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def ai_service_mocker():
    """Provide AI service mocker for tests."""
    mocker = AIServiceMocker()
    
    # Add some default responses for each provider
    mocker.add_provider_response("openai", "Hello, this is a test response from OpenAI!", "gpt-4")
    mocker.add_provider_response("anthropic", "This is a test response from Claude.", "claude-3-sonnet")
    mocker.add_provider_response("google", "Greetings from Gemini!", "gemini-pro")
    mocker.add_provider_response("openrouter", "OpenRouter response here.", "openrouter/auto")
    
    return mocker


@pytest.fixture
def mock_crewai_server():
    """Mock CrewAI server responses."""
    def mock_get_response(url, **kwargs):
        """Mock GET responses based on URL."""
        mock_response = MagicMock()
        
        if "/health" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}
        elif "/models" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-sonnet", "claude-3-haiku"],
                "google": ["gemini-pro", "gemini-pro-vision"]
            }
        elif "/state" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "current_provider": "openai",
                "current_model": "gpt-4",
                "usage_stats": {"requests": 10, "tokens": 1000}
            }
        else:
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
        
        return mock_response
    
    def mock_post_response(url, **kwargs):
        """Mock POST responses based on URL."""
        mock_response = MagicMock()
        
        if "/chat" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "response": "This is a mock AI response",
                "model": "gpt-4",
                "provider": "openai",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20}
            }
        elif "/switch_provider" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "switched", "new_provider": "anthropic"}
        elif "/update_state" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "updated"}
        else:
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
        
        return mock_response
    
    with patch('requests.get', side_effect=mock_get_response) as mock_get, \
         patch('requests.post', side_effect=mock_post_response) as mock_post:
        
        yield {
            "get": mock_get,
            "post": mock_post
        }


@pytest.fixture
def mock_txtai_memory():
    """Mock txtai memory system."""
    class MockTxtaiIndex:
        def __init__(self):
            self.documents = {}
            self.indexed = False
            self.config = {"path": "sentence-transformers/all-MiniLM-L6-v2"}
        
        def search(self, query, limit=10):
            """Mock search functionality."""
            # Return mock search results based on query
            if "test" in query.lower():
                return [
                    {"id": "1", "text": "Test memory about testing", "score": 0.9},
                    {"id": "2", "text": "Another test memory", "score": 0.8}
                ]
            elif "conversation" in query.lower():
                return [
                    {"id": "3", "text": "Previous conversation context", "score": 0.85},
                    {"id": "4", "text": "Chat history memory", "score": 0.75}
                ]
            else:
                return [
                    {"id": "5", "text": "General memory item", "score": 0.6}
                ]
        
        def index(self, documents):
            """Mock indexing operation."""
            if isinstance(documents, list):
                for i, doc in enumerate(documents):
                    self.documents[str(i)] = doc
            else:
                self.documents["0"] = documents
            self.indexed = True
        
        def upsert(self, documents):
            """Mock upsert operation."""
            self.index(documents)
        
        def delete(self, ids):
            """Mock delete operation."""
            if isinstance(ids, list):
                for doc_id in ids:
                    self.documents.pop(str(doc_id), None)
            else:
                self.documents.pop(str(ids), None)
        
        def count(self):
            """Mock count operation."""
            return len(self.documents)
        
        def exists(self):
            """Mock exists check."""
            return self.indexed
        
        def save(self, path):
            """Mock save operation."""
            return True
        
        def load(self, path):
            """Mock load operation."""
            self.indexed = True
            return True
    
    mock_index = MockTxtaiIndex()
    
    # Don't try to import txtai, just return the mock directly
    # This avoids dependency issues during testing
    yield mock_index


@pytest.fixture
def sample_conversation():
    """Provide sample conversation data."""
    return MockConversation(
        id="test-conversation-123",
        messages=[
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "Can you help me with Python programming?"},
            {"role": "assistant", "content": "Of course! I'd be happy to help you with Python programming. What specific topic would you like to learn about?"}
        ],
        metadata={
            "created_at": "2025-01-01T00:00:00Z",
            "model": "gpt-4",
            "provider": "openai",
            "session_id": "test-session-456"
        }
    )


@pytest.fixture
def mock_ui_events():
    """Mock UI events for testing."""
    from unittest.mock import MagicMock
    
    # Mock Qt events
    mock_events = {
        "click": MagicMock(),
        "key_press": MagicMock(),
        "text_change": MagicMock(),
        "window_close": MagicMock(),
        "model_switch": MagicMock(),
        "message_send": MagicMock(),
        "theme_change": MagicMock()
    }
    
    return mock_events


@pytest.fixture
def mock_pyside6_app():
    """Mock PySide6 QApplication for UI tests."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        import sys
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Mock common UI operations
        with patch('PySide6.QtWidgets.QMessageBox.information') as mock_info, \
             patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning, \
             patch('PySide6.QtWidgets.QMessageBox.critical') as mock_critical:
            
            yield {
                "app": app,
                "message_box": {
                    "information": mock_info,
                    "warning": mock_warning,
                    "critical": mock_critical
                }
            }
    except ImportError:
        # If PySide6 is not available, provide a mock
        mock_app = MagicMock()
        yield {"app": mock_app, "message_box": {"information": MagicMock(), "warning": MagicMock(), "critical": MagicMock()}}


@pytest.fixture
def mock_gopiai_widgets():
    """Mock GopiAI custom widgets."""
    mock_widgets = {
        "chat_widget": MagicMock(),
        "model_selector": MagicMock(),
        "settings_panel": MagicMock(),
        "conversation_list": MagicMock(),
        "theme_selector": MagicMock()
    }
    
    # Configure mock behaviors
    mock_widgets["model_selector"].get_current_model.return_value = "gpt-4"
    mock_widgets["model_selector"].get_current_provider.return_value = "openai"
    mock_widgets["chat_widget"].get_message_text.return_value = "Test message"
    mock_widgets["settings_panel"].get_theme.return_value = "dark"
    
    return mock_widgets


@pytest.fixture
def test_config_file(temp_dir):
    """Create a test configuration file."""
    config = {
        "api": {
            "base_url": "http://localhost:5051",
            "timeout": 30
        },
        "ui": {
            "theme": "dark",
            "font_size": 12
        },
        "memory": {
            "max_entries": 1000,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    }
    
    config_file = temp_dir / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_file


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system operations."""
    # Create some test files
    test_files = {
        "test.txt": "This is a test file",
        "config.json": '{"test": true}',
        "data.csv": "name,age\nJohn,30\nJane,25"
    }
    
    for filename, content in test_files.items():
        file_path = temp_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    return temp_dir


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    def connect(self):
        """Mock database connection."""
        self.connected = True
        return True
    
    def disconnect(self):
        """Mock database disconnection."""
        self.connected = False
    
    def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Mock data insertion."""
        if table not in self.data:
            self.data[table] = []
        
        record_id = f"{table}_{len(self.data[table])}"
        record = {"id": record_id, **data}
        self.data[table].append(record)
        return record_id
    
    def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock data selection."""
        if table not in self.data:
            return []
        
        records = self.data[table]
        
        if filters:
            filtered_records = []
            for record in records:
                match = True
                for key, value in filters.items():
                    if key not in record or record[key] != value:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
            return filtered_records
        
        return records
    
    def update(self, table: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Mock data update."""
        if table not in self.data:
            return False
        
        for record in self.data[table]:
            if record["id"] == record_id:
                record.update(data)
                return True
        
        return False
    
    def delete(self, table: str, record_id: str) -> bool:
        """Mock data deletion."""
        if table not in self.data:
            return False
        
        for i, record in enumerate(self.data[table]):
            if record["id"] == record_id:
                del self.data[table][i]
                return True
        
        return False


@pytest.fixture
def mock_database():
    """Provide mock database for tests."""
    db = MockDatabase()
    db.connect()
    
    # Add some test data
    db.insert("users", {"name": "Test User", "email": "test@example.com"})
    db.insert("conversations", {"user_id": "users_0", "title": "Test Chat"})
    
    yield db
    
    db.disconnect()


@pytest.fixture
def mock_model_config_manager():
    """Mock model configuration manager."""
    mock_manager = MagicMock()
    
    # Mock model configurations
    mock_manager.get_available_models.return_value = {
        "openai": ["gpt-4", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-sonnet", "claude-3-haiku"],
        "google": ["gemini-pro"]
    }
    
    mock_manager.get_current_model.return_value = "gpt-4"
    mock_manager.get_current_provider.return_value = "openai"
    mock_manager.switch_model.return_value = True
    mock_manager.get_model_limits.return_value = {"requests_per_minute": 60, "tokens_per_minute": 40000}
    
    return mock_manager


@pytest.fixture
def mock_usage_tracker():
    """Mock usage tracker for rate limiting."""
    mock_tracker = MagicMock()
    
    mock_tracker.can_make_request.return_value = True
    mock_tracker.record_request.return_value = None
    mock_tracker.get_usage_stats.return_value = {
        "requests_made": 5,
        "tokens_used": 1000,
        "requests_remaining": 55,
        "tokens_remaining": 39000
    }
    mock_tracker.reset_usage.return_value = None
    
    return mock_tracker


@pytest.fixture
def mock_conversation_manager():
    """Mock conversation manager."""
    mock_manager = MagicMock()
    
    # Mock conversation data
    mock_conversations = [
        {"id": "conv1", "title": "Test Chat 1", "created_at": "2025-01-01T00:00:00Z"},
        {"id": "conv2", "title": "Test Chat 2", "created_at": "2025-01-01T01:00:00Z"}
    ]
    
    mock_manager.get_conversations.return_value = mock_conversations
    mock_manager.create_conversation.return_value = "new_conv_id"
    mock_manager.get_conversation.return_value = {
        "id": "conv1",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
    mock_manager.add_message.return_value = True
    mock_manager.delete_conversation.return_value = True
    
    return mock_manager


@pytest.fixture
def mock_settings_manager():
    """Mock settings manager."""
    mock_manager = MagicMock()
    
    # Default settings
    default_settings = {
        "theme": "dark",
        "font_size": 12,
        "auto_save": True,
        "api_timeout": 30,
        "max_tokens": 4000
    }
    
    mock_manager.get_setting.side_effect = lambda key, default=None: default_settings.get(key, default)
    mock_manager.set_setting.return_value = True
    mock_manager.get_all_settings.return_value = default_settings
    mock_manager.save_settings.return_value = True
    mock_manager.load_settings.return_value = default_settings
    
    return mock_manager


@pytest.fixture
def mock_tool_manager():
    """Mock tool manager for CrewAI tools."""
    mock_manager = MagicMock()
    
    # Mock available tools
    mock_tools = {
        "browser_tools": {
            "name": "Browser Tools",
            "description": "Web browsing capabilities",
            "available": True
        },
        "filesystem_tools": {
            "name": "File System Tools", 
            "description": "File operations",
            "available": True
        },
        "terminal_tools": {
            "name": "Terminal Tools",
            "description": "Command line access",
            "available": False  # Disabled by default for safety
        }
    }
    
    mock_manager.get_available_tools.return_value = mock_tools
    mock_manager.execute_tool.return_value = {"status": "success", "result": "Mock tool execution result"}
    mock_manager.is_tool_available.side_effect = lambda tool: mock_tools.get(tool, {}).get("available", False)
    
    return mock_manager


# Pytest configuration for common markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "ui: UI tests"
    )
    config.addinivalue_line(
        "markers", "api: API tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "requires_display: Tests requiring display"
    )
    config.addinivalue_line(
        "markers", "requires_server: Tests requiring server"
    )
    config.addinivalue_line(
        "markers", "requires_ai_service: Tests requiring external AI services"
    )
    config.addinivalue_line(
        "markers", "xfail_known_issue: Known issues marked as expected failures"
    )