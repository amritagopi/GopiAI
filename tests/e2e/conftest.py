#!/usr/bin/env python3
"""
Pytest configuration for End-to-End tests.

Provides E2E-specific fixtures, markers, and configuration.
"""

import pytest
import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()


def pytest_configure(config):
    """Configure pytest for E2E tests."""
    # Register E2E-specific markers
    config.addinivalue_line(
        "markers", "e2e: End-to-end integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests (may take several minutes)"
    )
    config.addinivalue_line(
        "markers", "requires_services: Tests requiring external services to be running"
    )
    config.addinivalue_line(
        "markers", "requires_crewai: Tests requiring CrewAI server"
    )
    config.addinivalue_line(
        "markers", "requires_memory: Tests requiring memory system"
    )
    config.addinivalue_line(
        "markers", "requires_ui: Tests requiring UI application"
    )
    config.addinivalue_line(
        "markers", "load_test: Load and performance tests"
    )
    config.addinivalue_line(
        "markers", "recovery_test: Service recovery and resilience tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for E2E tests."""
    # Add slow marker to all E2E tests
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Add service requirement markers based on test names
        if "conversation" in item.name.lower() or "chat" in item.name.lower():
            item.add_marker(pytest.mark.requires_crewai)
        
        if "memory" in item.name.lower() or "persistence" in item.name.lower():
            item.add_marker(pytest.mark.requires_memory)
        
        if "recovery" in item.name.lower() or "failure" in item.name.lower():
            item.add_marker(pytest.mark.recovery_test)
        
        if "multiple_users" in item.name.lower() or "concurrent" in item.name.lower():
            item.add_marker(pytest.mark.load_test)


@pytest.fixture(scope="session")
def e2e_test_session():
    """Session-scoped fixture for E2E test setup."""
    session_data = {
        "session_id": f"e2e_test_session_{int(time.time())}",
        "start_time": time.time(),
        "temp_dirs": [],
        "cleanup_functions": []
    }
    
    # Set test environment variables
    original_env = os.environ.copy()
    test_env_vars = {
        "GOPIAI_TEST_MODE": "true",
        "CREWAI_TEST_MODE": "true",
        "TXTAI_TEST_MODE": "true",
        "FLASK_ENV": "testing",
        "QT_QPA_PLATFORM": "offscreen"  # For headless UI testing
    }
    
    os.environ.update(test_env_vars)
    session_data["original_env"] = original_env
    
    yield session_data
    
    # Cleanup
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Clean up temporary directories
    import shutil
    for temp_dir in session_data["temp_dirs"]:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Run cleanup functions
    for cleanup_func in session_data["cleanup_functions"]:
        try:
            cleanup_func()
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture
def e2e_temp_dir(e2e_test_session):
    """Provide a temporary directory for E2E tests."""
    temp_dir = Path(tempfile.mkdtemp(prefix="gopiai_e2e_"))
    e2e_test_session["temp_dirs"].append(temp_dir)
    return temp_dir


@pytest.fixture
def mock_ai_responses():
    """Provide mock AI responses for E2E tests."""
    responses = {
        "openai": [
            "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?",
            "I'd be happy to help you with Python programming! What specific topic would you like to learn about?",
            "Here's a simple Python function example:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))\n```",
            "Great question! Let me explain that concept in more detail...",
            "I understand you're working on a project. Can you tell me more about what you're trying to achieve?"
        ],
        "anthropic": [
            "Hi there! I'm Claude, an AI assistant created by Anthropic. What can I do for you?",
            "I'd be delighted to help you with your programming questions. What language are you working with?",
            "That's an interesting problem! Here's how I would approach it...",
            "Let me break that down into smaller, more manageable steps...",
            "I notice you mentioned earlier that you're working on AI projects. How is that going?"
        ],
        "google": [
            "Greetings! I'm Gemini, Google's AI assistant. How may I assist you?",
            "I can help you with a wide variety of topics. What would you like to explore?",
            "That's a great question about machine learning! Let me explain...",
            "Here are some best practices for that approach...",
            "Based on our previous conversation, I remember you're interested in..."
        ]
    }
    return responses


@pytest.fixture
def mock_conversation_data():
    """Provide mock conversation data for testing."""
    return {
        "conversations": [
            {
                "id": "conv_001",
                "title": "Python Programming Help",
                "created_at": "2025-01-01T10:00:00Z",
                "messages": [
                    {"role": "user", "content": "I need help with Python functions"},
                    {"role": "assistant", "content": "I'd be happy to help! What specific aspect of Python functions would you like to learn about?"},
                    {"role": "user", "content": "How do I create a function that takes multiple arguments?"},
                    {"role": "assistant", "content": "Here's how you can create functions with multiple arguments in Python..."}
                ]
            },
            {
                "id": "conv_002", 
                "title": "Web Development Discussion",
                "created_at": "2025-01-01T11:00:00Z",
                "messages": [
                    {"role": "user", "content": "What's the best framework for web development?"},
                    {"role": "assistant", "content": "The best framework depends on your specific needs. Let me break down some popular options..."}
                ]
            }
        ],
        "memory_entries": [
            {"content": "User is learning Python programming", "score": 0.9, "source": "conv_001"},
            {"content": "User interested in web development", "score": 0.8, "source": "conv_002"},
            {"content": "User prefers practical examples", "score": 0.7, "source": "conv_001"}
        ]
    }


@pytest.fixture
def mock_service_responses():
    """Mock HTTP responses for service endpoints."""
    def create_mock_response(status_code, json_data):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        return mock_response
    
    return {
        "health_check": create_mock_response(200, {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}),
        "models_list": create_mock_response(200, {
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-sonnet", "claude-3-haiku"],
            "google": ["gemini-pro"]
        }),
        "chat_response": create_mock_response(200, {
            "response": "This is a mock AI response",
            "model": "gpt-4",
            "provider": "openai",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }),
        "conversation_start": create_mock_response(200, {
            "id": "conv_test_123",
            "status": "active"
        }),
        "memory_search": create_mock_response(200, {
            "results": [
                {"content": "Previous conversation context", "score": 0.9},
                {"content": "Related memory", "score": 0.8}
            ]
        })
    }


@pytest.fixture
def e2e_test_config():
    """Provide configuration for E2E tests."""
    return {
        "timeouts": {
            "service_startup": 60,
            "service_health_check": 30,
            "api_request": 30,
            "test_execution": 300
        },
        "services": {
            "crewai_server": {
                "host": "localhost",
                "port": 5051,
                "health_endpoint": "/health"
            },
            "memory_system": {
                "host": "localhost", 
                "port": 8000,
                "health_endpoint": "/health"
            }
        },
        "test_data": {
            "max_conversations": 10,
            "max_messages_per_conversation": 20,
            "max_memory_entries": 100
        },
        "performance": {
            "max_response_time": 30,
            "avg_response_time_threshold": 15,
            "concurrent_users": 5,
            "load_test_duration": 60
        }
    }


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during E2E tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {
                "response_times": [],
                "memory_usage": [],
                "cpu_usage": [],
                "api_calls": 0,
                "errors": 0
            }
            self.start_time = time.time()
        
        def record_response_time(self, duration):
            self.metrics["response_times"].append(duration)
        
        def record_api_call(self):
            self.metrics["api_calls"] += 1
        
        def record_error(self):
            self.metrics["errors"] += 1
        
        def get_summary(self):
            response_times = self.metrics["response_times"]
            return {
                "total_duration": time.time() - self.start_time,
                "api_calls": self.metrics["api_calls"],
                "errors": self.metrics["errors"],
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0
            }
    
    return PerformanceMonitor()


@pytest.fixture
def e2e_logger():
    """Provide logger for E2E tests."""
    import logging
    
    logger = logging.getLogger("e2e_tests")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


@pytest.fixture
def mock_user_sessions():
    """Provide mock user sessions for multi-user testing."""
    sessions = []
    for i in range(5):
        session = {
            "session_id": f"user_{i}_session_{int(time.time())}",
            "user_id": f"user_{i}",
            "conversation_id": f"conv_user_{i}_{int(time.time())}",
            "preferences": {
                "model": ["gpt-4", "claude-3-sonnet", "gemini-pro"][i % 3],
                "theme": ["light", "dark"][i % 2],
                "language": "en"
            },
            "context": {
                "name": f"TestUser{i}",
                "interests": ["programming", "web development", "AI", "data science", "mobile apps"][i],
                "experience_level": ["beginner", "intermediate", "advanced"][i % 3]
            }
        }
        sessions.append(session)
    
    return sessions


# Pytest hooks for E2E test reporting
def pytest_runtest_setup(item):
    """Setup hook for each E2E test."""
    if "e2e" in item.keywords:
        # Log test start
        print(f"\n🚀 Starting E2E test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for each E2E test."""
    if "e2e" in item.keywords:
        # Log test completion
        print(f"✅ Completed E2E test: {item.name}")


def pytest_runtest_makereport(item, call):
    """Generate test reports for E2E tests."""
    if "e2e" in item.keywords and call.when == "call":
        # Add E2E-specific reporting
        if call.excinfo is not None:
            print(f"❌ E2E test failed: {item.name}")
            print(f"   Error: {call.excinfo.value}")
        else:
            print(f"✅ E2E test passed: {item.name}")


# Skip E2E tests if running in CI without proper setup
def pytest_runtest_setup(item):
    """Skip E2E tests if environment is not suitable."""
    if "e2e" in item.keywords:
        # Check if we're in a CI environment without service setup
        if os.environ.get("CI") and not os.environ.get("E2E_TESTS_ENABLED"):
            pytest.skip("E2E tests disabled in CI environment")
        
        