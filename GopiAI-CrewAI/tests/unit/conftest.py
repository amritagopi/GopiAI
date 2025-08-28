#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for GopiAI-CrewAI unit tests.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import json

# Add test infrastructure to path
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

# Import shared fixtures
from fixtures import temp_dir, ai_service_mocker, mock_crewai_server, mock_tool_manager
from crewai_fixtures import (
    mock_crewai_agent, mock_crewai_task, mock_crewai_crew,
    mock_llm_provider, mock_openrouter_client, mock_api_server,
    mock_state_manager, mock_command_processor, mock_tool_executor,
    mock_memory_system, crewai_test_config, mock_env_file,
    mock_rate_limiter, mock_model_switcher
)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
    # Заменено на использование path_manager: sys.path.append(str(project_root))


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables."""
    test_env = {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        "GEMINI_API_KEY": "test-gemini-key",
        "OPENROUTER_API_KEY": "test-openrouter-key",
        "CREWAI_API_HOST": "localhost",
        "CREWAI_API_PORT": "5051",
        "GOPIAI_TERMINAL_UNSAFE": "0",
        "GOPIAI_DEBUG": "1",
        "TESTING": "1"
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_flask_request():
    """Mock Flask request object."""
    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.url = "http://localhost:5051/api/process"
    mock_request.headers = {"Content-Type": "application/json"}
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "message": "Test message",
        "metadata": {"test": "data"}
    }
    mock_request.get_data.return_value = b'{"message": "Test message"}'
    mock_request.environ = {"gopiai.request_id": "test-request-id"}
    
    return mock_request


@pytest.fixture
def mock_smart_delegator():
    """Mock SmartDelegator for testing."""
    mock_delegator = MagicMock()
    
    # Configure default responses
    mock_delegator.process_request.return_value = {
        "response": "Mock response from SmartDelegator",
        "processed_with_crewai": False,
        "analysis": {
            "type": "general",
            "complexity": 1,
            "requires_crewai": False
        },
        "model_info": {
            "provider": "gemini",
            "model_id": "gemini-1.5-flash",
            "display_name": "Gemini 1.5 Flash"
        }
    }
    
    # Mock initialization properties
    mock_delegator.rag_available = True
    mock_delegator.local_tools_available = True
    mock_delegator.crewai_tools_available = True
    mock_delegator.mcp_available = False
    
    return mock_delegator


@pytest.fixture
def mock_rag_system():
    """Mock RAG system for testing."""
    mock_rag = MagicMock()
    
    # Mock embeddings
    mock_embeddings = MagicMock()
    mock_embeddings.count.return_value = 150
    mock_rag.embeddings = mock_embeddings
    
    # Mock context retrieval
    mock_rag.get_context_for_prompt.return_value = "Retrieved context for the prompt"
    
    return mock_rag


@pytest.fixture
def mock_task_queue():
    """Mock task queue for testing."""
    mock_queue = MagicMock()
    
    # Mock queue operations
    mock_queue.put.return_value = None
    mock_queue.get.return_value = {
        "task_id": "test-task-id",
        "message": "Test message",
        "metadata": {}
    }
    mock_queue.empty.return_value = False
    mock_queue.qsize.return_value = 5
    
    return mock_queue


@pytest.fixture
def sample_models_config():
    """Sample models configuration for testing."""
    return [
        {
            "display_name": "Gemini 1.5 Flash",
            "id": "gemini/gemini-1.5-flash",
            "provider": "gemini",
            "rpm": 15,
            "tpm": 2_500_000,
            "type": ["simple", "dialog", "code"],
            "priority": 3,
            "rpd": 50,
            "base_score": 0.5,
        },
        {
            "display_name": "GPT-4 (OpenRouter)",
            "id": "openrouter/openai/gpt-4",
            "provider": "openrouter",
            "rpm": 10,
            "tpm": 8_000,
            "type": ["dialog", "code", "complex"],
            "priority": 1,
            "rpd": 100,
            "base_score": 0.9,
        },
        {
            "display_name": "Claude 3 Sonnet (OpenRouter)",
            "id": "openrouter/anthropic/claude-3-sonnet",
            "provider": "openrouter",
            "rpm": 20,
            "tpm": 200_000,
            "type": ["dialog", "summarize"],
            "priority": 2,
            "rpd": 200,
            "base_score": 0.8,
        }
    ]


@pytest.fixture
def sample_chat_history():
    """Sample chat history for testing."""
    return [
        {
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I'm doing well, thank you! How can I help you today?",
            "timestamp": "2024-01-01T10:00:05Z"
        },
        {
            "role": "user",
            "content": "Can you help me with a coding problem?",
            "timestamp": "2024-01-01T10:01:00Z"
        },
        {
            "role": "assistant",
            "content": "Of course! I'd be happy to help with your coding problem. What are you working on?",
            "timestamp": "2024-01-01T10:01:03Z"
        }
    ]


@pytest.fixture
def sample_tool_commands():
    """Sample tool commands for testing."""
    return {
        "single_command": {
            "tool": "filesystem_tools",
            "params": {
                "command": "ls",
                "path": "/home/user"
            }
        },
        "multiple_commands": [
            {
                "tool": "filesystem_tools",
                "params": {"command": "ls", "path": "."}
            },
            {
                "tool": "browser_tools",
                "params": {"command": "open", "url": "https://example.com"}
            }
        ],
        "invalid_command": {
            "tool": "filesystem_tools"
            # Missing required "params" field
        }
    }


@pytest.fixture
def mock_litellm():
    """Mock LiteLLM for testing."""
    mock_llm = MagicMock()
    
    # Mock completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mock LLM response"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    
    mock_llm.completion.return_value = mock_response
    
    return mock_llm


@pytest.fixture
def mock_google_genai():
    """Mock Google Generative AI for testing."""
    mock_genai = MagicMock()
    
    # Mock model
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Mock Gemini response"
    mock_genai.GenerativeModel.return_value = mock_model
    
    return mock_genai


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up logging for tests."""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Suppress noisy loggers during tests
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


@pytest.fixture
def isolated_test_environment(temp_dir, test_environment):
    """Create isolated test environment with temporary directories."""
    # Create test-specific directories
    test_dirs = {
        'logs': temp_dir / 'logs',
        'cache': temp_dir / 'cache',
        'config': temp_dir / 'config',
        'state': temp_dir / 'state'
    }
    
    for dir_path in test_dirs.values():
        dir_path.mkdir(exist_ok=True)
    
    # Patch environment paths
    with patch.dict(os.environ, {
        'GOPIAI_LOGS_DIR': str(test_dirs['logs']),
        'GOPIAI_CACHE_DIR': str(test_dirs['cache']),
        'GOPIAI_CONFIG_DIR': str(test_dirs['config']),
        'GOPIAI_STATE_DIR': str(test_dirs['state'])
    }):
        yield test_dirs


# Pytest markers for categorizing tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "requires_server: Tests that require CrewAI server running"
    )
    config.addinivalue_line(
        "markers", "requires_ai_service: Tests that require external AI services"
    )
    config.addinivalue_line(
        "markers", "xfail_known_issue: Known issues marked as expected failures"
    )


# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to all tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add api marker to API tests
        if "api" in item.name.lower() or "endpoint" in item.name.lower():
            item.add_marker(pytest.mark.api)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["concurrent", "performance", "load"]):
            item.add_marker(pytest.mark.slow)


# Test session fixtures
@pytest.fixture(scope="session")
def test_session_info():
    """Provide information about the test session."""
    return {
        "start_time": pytest.current_time if hasattr(pytest, 'current_time') else None,
        "test_directory": Path(__file__).parent,
        "project_root": project_root,
        "python_version": sys.version,
        "platform": sys.platform
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Clean up after each test."""
    yield
    
    # Clean up any global state that might affect other tests
    # This is important for unit tests to be isolated
    
    # Reset any module-level variables if needed
    # Clear caches if needed
    # Reset mock states if needed
    pass