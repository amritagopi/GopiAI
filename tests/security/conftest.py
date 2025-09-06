#!/usr/bin/env python3
"""
Security test configuration and fixtures.

Provides common fixtures and utilities for security testing.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch


@pytest.fixture
def temp_directory():
    """Create a temporary directory for security tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_api_server():
    """Mock API server for security testing."""
    class MockAPIServer:
        def __init__(self):
            self.is_running = False
            self.port = 5051
            self.endpoints = {}
        
        def start(self):
            self.is_running = True
        
        def stop(self):
            self.is_running = False
        
        def add_endpoint(self, path, handler):
            self.endpoints[path] = handler
        
        def handle_request(self, path, data):
            if path in self.endpoints:
                return self.endpoints[path](data)
            return {"error": "Not found", "status": 404}
    
    server = MockAPIServer()
    yield server
    server.stop()


@pytest.fixture
def mock_secure_storage():
    """Mock secure storage for testing credential management."""
    class MockSecureStorage:
        def __init__(self):
            self._storage = {}
        
        def store(self, key: str, value: str):
            # Mock encryption
            encrypted_value = f"encrypted_{value}"
            self._storage[key] = encrypted_value
        
        def retrieve(self, key: str) -> str:
            encrypted_value = self._storage.get(key, "")
            if encrypted_value.startswith("encrypted_"):
                return encrypted_value[10:]  # Mock decryption
            return ""
        
        def delete(self, key: str):
            if key in self._storage:
                del self._storage[key]
        
        def list_keys(self):
            return list(self._storage.keys())
    
    return MockSecureStorage()


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for security testing."""
    test_env = {
        "OPENAI_API_KEY": "sk-test1234567890abcdef1234567890abcdef12345678",
        "ANTHROPIC_API_KEY": "ant-test1234567890abcdef1234567890abcdef12345678",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO"
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        yield test_env


@pytest.fixture
def security_test_data():
    """Provide common test data for security tests."""
    return {
        "malicious_inputs": [
            "<script>alert('XSS')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ],
        "safe_inputs": [
            "Hello, world!",
            "This is a normal message.",
            "User input with special chars: !@#$%",
            "Multi-line\ninput\ntext",
        ],
        "api_keys": [
            "sk-1234567890abcdef1234567890abcdef12345678",
            "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI",
            "ant-1234567890abcdef1234567890abcdef12345678",
        ],
        "sensitive_patterns": [
            r'sk-[a-zA-Z0-9]{48}',
            r'AIza[0-9A-Za-z-_]{35}',
            r'ant-[a-zA-Z0-9]{48}',
            r'password\s*[:=]\s*[^\s]+',
        ]
    }


@pytest.fixture
def mock_file_system():
    """Mock file system for testing file security."""
    class MockFileSystem:
        def __init__(self):
            self.files = {}
            self.permissions = {}
        
        def create_file(self, path: str, content: str, permissions: str = "644"):
            self.files[path] = content
            self.permissions[path] = permissions
        
        def read_file(self, path: str) -> str:
            return self.files.get(path, "")
        
        def delete_file(self, path: str):
            if path in self.files:
                del self.files[path]
            if path in self.permissions:
                del self.permissions[path]
        
        def list_files(self):
            return list(self.files.keys())
        
        def get_permissions(self, path: str) -> str:
            return self.permissions.get(path, "644")
        
        def is_safe_path(self, path: str) -> bool:
            """Check if path is safe (no directory traversal)."""
            return ".." not in path and not path.startswith("/")
    
    return MockFileSystem()


@pytest.fixture
def mock_logger():
    """Mock logger for testing security logging."""
    class MockLogger:
        def __init__(self):
            self.logs = []
        
        def log(self, level: str, message: str, **kwargs):
            self.logs.append({
                "level": level,
                "message": message,
                "extra": kwargs
            })
        
        def debug(self, message: str, **kwargs):
            self.log("DEBUG", message, **kwargs)
        
        def info(self, message: str, **kwargs):
            self.log("INFO", message, **kwargs)
        
        def warning(self, message: str, **kwargs):
            self.log("WARNING", message, **kwargs)
        
        def error(self, message: str, **kwargs):
            self.log("ERROR", message, **kwargs)
        
        def get_logs(self, level: str = None):
            if level:
                return [log for log in self.logs if log["level"] == level]
            return self.logs
        
        def clear(self):
            self.logs.clear()
    
    return MockLogger()


@pytest.fixture
def security_config():
    """Security configuration for tests."""
    return {
        "max_login_attempts": 5,
        "session_timeout": 1800,  # 30 minutes
        "password_min_length": 8,
        "api_rate_limit": 100,  # requests per minute
        "allowed_file_extensions": [".txt", ".json", ".csv", ".log"],
        "blocked_file_extensions": [".exe", ".bat", ".sh", ".scr"],
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "encryption_algorithm": "AES-256",
        "hash_algorithm": "SHA-256",
    }


def pytest_configure(config):
    """Configure pytest for security tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "requires_server: mark test as requiring a running server"
    )
    config.addinivalue_line(
        "markers", "slow_security: mark test as a slow security test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for security tests."""
    for item in items:
        # Add security marker to all tests in security directory
        if "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        
        # Mark tests that require external services
        if "requires_server" in item.keywords:
            item.add_marker(pytest.mark.requires_server)


@pytest.fixture(autouse=True)
def security_test_environment():
    """Set up secure test environment."""
    # Ensure we're in test mode
    original_env = os.environ.get("TESTING", "")
    os.environ["TESTING"] = "true"
    
    # Disable debug mode for security tests
    original_debug = os.environ.get("DEBUG", "")
    os.environ["DEBUG"] = "false"
    
    yield
    
    # Restore original environment
    if original_env:
        os.environ["TESTING"] = original_env
    else:
        os.environ.pop("TESTING", None)
    
    if original_debug:
        os.environ["DEBUG"] = original_debug
    else:
        os.environ.pop("DEBUG", None)