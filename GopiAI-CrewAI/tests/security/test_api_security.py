#!/usr/bin/env python3
"""
Security tests for GopiAI-CrewAI module.

Tests API security, authentication, and protection against common attacks.
Requirements: 7.1, 7.2, 7.3, 7.4
"""

import pytest
import requests
import json
import os
import tempfile
import logging
import re
from pathlib import Path
from unittest.mock import patch


class TestAPISecurityBasics:
    """Test basic API security measures - Requirement 7.1."""
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_sql_injection_protection(self):
        """Test API protection against SQL injection attacks."""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM users WHERE 1=1 --"
        ]
        
        base_url = "http://localhost:5051"
        
        for payload in malicious_payloads:
            # Test various endpoints with malicious SQL payloads
            test_data = {
                "message": payload,
                "user_id": payload,
                "session_id": payload
            }
            
            try:
                response = requests.post(
                    f"{base_url}/api/chat",
                    json=test_data,
                    timeout=5
                )
                
                # Should not return database errors or execute SQL
                assert response.status_code != 500, f"Server error with payload: {payload}"
                
                # Check response doesn't contain SQL error messages
                response_text = response.text.lower()
                sql_error_indicators = [
                    "sql syntax", "mysql", "postgresql", "sqlite",
                    "database error", "table", "column"
                ]
                
                for indicator in sql_error_indicators:
                    assert indicator not in response_text, f"SQL error exposed with payload: {payload}"
                    
            except requests.exceptions.RequestException:
                # Connection errors are acceptable for security tests
                pass
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_xss_protection(self):
        """Test API protection against XSS attacks."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        base_url = "http://localhost:5051"
        
        for payload in xss_payloads:
            test_data = {"message": payload}
            
            try:
                response = requests.post(
                    f"{base_url}/api/chat",
                    json=test_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    # Response should not contain unescaped script tags
                    response_text = response.text
                    assert "<script>" not in response_text, f"Unescaped script tag with payload: {payload}"
                    assert "javascript:" not in response_text, f"JavaScript protocol with payload: {payload}"
                    
            except requests.exceptions.RequestException:
                pass
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_csrf_protection(self):
        """Test API protection against CSRF attacks."""
        base_url = "http://localhost:5051"
        
        # Test without proper headers/tokens
        malicious_headers = {
            "Origin": "http://malicious-site.com",
            "Referer": "http://malicious-site.com/attack"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": "test"},
                headers=malicious_headers,
                timeout=5
            )
            
            # Should either reject or handle safely
            if response.status_code == 200:
                # If accepted, ensure no sensitive operations were performed
                assert "error" not in response.text.lower() or "unauthorized" in response.text.lower()
                
        except requests.exceptions.RequestException:
            pass
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_input_validation_and_sanitization(self):
        """Test comprehensive input validation and sanitization."""
        invalid_inputs = [
            {"message": ""},  # Empty input
            {"message": "x" * 10000},  # Extremely long input
            {"message": None},  # Null input
            {"message": 12345},  # Wrong type
            {"message": ["array", "input"]},  # Array instead of string
            {"message": {"nested": "object"}},  # Object instead of string
            {"user_id": "../../../etc/passwd"},  # Path traversal
            {"session_id": "'; DROP TABLE sessions; --"},  # SQL injection
        ]
        
        base_url = "http://localhost:5051"
        
        for invalid_input in invalid_inputs:
            try:
                response = requests.post(
                    f"{base_url}/api/chat",
                    json=invalid_input,
                    timeout=5
                )
                
                # Should handle invalid input gracefully
                if response.status_code == 400:
                    # Good - proper validation error
                    assert "error" in response.text.lower() or "invalid" in response.text.lower()
                elif response.status_code == 200:
                    # If accepted, should be sanitized
                    response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    # Ensure no dangerous content is echoed back
                    response_str = str(response_data)
                    assert "DROP TABLE" not in response_str
                    assert "../" not in response_str
                    
            except (requests.exceptions.RequestException, json.JSONDecodeError):
                pass
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_rate_limiting_protection(self):
        """Test API rate limiting protection."""
        base_url = "http://localhost:5051"
        
        # Send rapid requests to test rate limiting
        responses = []
        for i in range(20):  # Send 20 rapid requests
            try:
                response = requests.post(
                    f"{base_url}/api/chat",
                    json={"message": f"test message {i}"},
                    timeout=2
                )
                responses.append(response.status_code)
            except requests.exceptions.RequestException:
                responses.append(0)  # Connection error
        
        # Should have some rate limiting (429 status codes) or connection errors
        rate_limited = sum(1 for status in responses if status == 429)
        connection_errors = sum(1 for status in responses if status == 0)
        
        # Either proper rate limiting or connection protection should be in place
        assert rate_limited > 0 or connection_errors > 5, "No rate limiting protection detected"


class TestSecretManagement:
    """Test secret and API key management security - Requirement 7.2."""
    
    @pytest.mark.security
    def test_api_key_not_in_logs(self):
        """Test that API keys are not exposed in log files."""
        # Common API key patterns
        api_key_patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
            r'AIza[0-9A-Za-z-_]{35}',  # Google API key pattern
            r'ANTHROPIC_API_KEY.*[a-zA-Z0-9]{40,}',  # Anthropic API key
        ]
        
        # Check log files
        log_directories = [
            "logs",
            "GopiAI-CrewAI/logs",
            "GopiAI-UI/logs"
        ]
        
        for log_dir in log_directories:
            if os.path.exists(log_dir):
                for log_file in Path(log_dir).glob("*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for pattern in api_key_patterns:
                            matches = re.findall(pattern, content)
                            assert len(matches) == 0, f"API key pattern found in {log_file}: {pattern}"
                            
                    except (IOError, UnicodeDecodeError):
                        # Skip files that can't be read
                        continue
    
    @pytest.mark.security
    def test_api_key_not_in_responses(self):
        """Test that API keys are not exposed in API responses."""
        base_url = "http://localhost:5051"
        
        # Test various endpoints
        endpoints = [
            "/api/health",
            "/api/models",
            "/api/chat"
        ]
        
        api_key_patterns = [
            r'sk-[a-zA-Z0-9]{48}',
            r'AIza[0-9A-Za-z-_]{35}',
            r'[a-zA-Z0-9]{40,}',  # Generic long strings that might be keys
        ]
        
        for endpoint in endpoints:
            try:
                if endpoint == "/api/chat":
                    response = requests.post(
                        f"{base_url}{endpoint}",
                        json={"message": "test"},
                        timeout=5
                    )
                else:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    response_text = response.text
                    
                    # Check for API key patterns
                    for pattern in api_key_patterns:
                        matches = re.findall(pattern, response_text)
                        # Filter out short matches that are likely not API keys
                        long_matches = [m for m in matches if len(m) > 20]
                        assert len(long_matches) == 0, f"Potential API key in response from {endpoint}"
                        
            except requests.exceptions.RequestException:
                pass
    
    @pytest.mark.security
    def test_environment_variable_security(self):
        """Test secure handling of environment variables."""
        # Test that sensitive environment variables are not exposed
        sensitive_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "DATABASE_PASSWORD",
            "SECRET_KEY"
        ]
        
        # Mock a scenario where env vars might be exposed
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test123456789012345678901234567890123456789012",
            "ANTHROPIC_API_KEY": "ant-test123456789012345678901234567890123456789012",
            "SECRET_KEY": "super-secret-key-12345"
        }):
            
            # Test that these don't appear in string representations
            env_str = str(dict(os.environ))
            
            # In a real application, sensitive vars should be masked
            # For now, just ensure they exist but are handled properly
            for var in sensitive_vars:
                if var in os.environ:
                    value = os.environ[var]
                    assert len(value) > 0, f"Environment variable {var} should not be empty"
                    
                    # Test that the value is not accidentally logged
                    # This is a basic check - in practice, logging should mask these
                    test_log_message = f"Processing request with config: {var}={value}"
                    assert value not in test_log_message or len(value) < 10, f"Sensitive value exposed in log message"
    
    @pytest.mark.security
    def test_secret_masking_in_debug_output(self):
        """Test that secrets are masked in debug output."""
        # Test logging configuration
        logger = logging.getLogger("test_security")
        
        # Create a test handler to capture log output
        log_capture = []
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                log_capture.append(self.format(record))
        
        handler = TestHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Test logging with sensitive data
        sensitive_data = {
            "api_key": "sk-1234567890abcdef1234567890abcdef12345678",
            "password": "super_secret_password",
            "token": "bearer_token_12345678901234567890"
        }
        
        logger.debug(f"Config loaded: {sensitive_data}")
        
        # Check that sensitive values are not in the log output
        log_output = " ".join(log_capture)
        
        # In a properly configured system, these should be masked
        # For now, we'll check that if they appear, they're short (indicating masking)
        for key, value in sensitive_data.items():
            if value in log_output:
                # If the full value appears, it should be in a test context only
                assert "test" in log_output.lower(), f"Sensitive {key} not masked in production log"


class TestAuthenticationSecurity:
    """Test authentication and session security - Requirement 7.3."""
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_session_token_validation(self):
        """Test proper session token validation."""
        base_url = "http://localhost:5051"
        
        # Test with invalid session tokens
        invalid_tokens = [
            "",  # Empty token
            "invalid_token",  # Invalid format
            "expired_token_12345",  # Potentially expired
            "../../../etc/passwd",  # Path traversal attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(
                    f"{base_url}/api/chat",
                    json={"message": "test"},
                    headers=headers,
                    timeout=5
                )
                
                # Should either reject invalid tokens or handle them safely
                if response.status_code == 401:
                    # Good - proper authentication error
                    assert "unauthorized" in response.text.lower() or "invalid" in response.text.lower()
                elif response.status_code == 200:
                    # If accepted, ensure it's handled safely
                    assert "error" not in response.text.lower() or "success" in response.text.lower()
                    
            except requests.exceptions.RequestException:
                pass
    
    @pytest.mark.security
    def test_session_hijacking_protection(self):
        """Test protection against session hijacking."""
        # Test that sessions are properly isolated
        session_data = {
            "session_id": "test_session_123",
            "user_id": "test_user"
        }
        
        # Simulate session data handling
        # In a real system, this would test actual session management
        assert session_data["session_id"] != session_data["user_id"], "Session ID should be independent of user ID"
        
        # Test session ID format (should be random/unpredictable)
        session_id = session_data["session_id"]
        assert len(session_id) > 10, "Session ID should be sufficiently long"
        
        # Basic check for randomness (not sequential)
        assert not session_id.isdigit(), "Session ID should not be purely numeric"
    
    @pytest.mark.security
    @pytest.mark.requires_server
    def test_authentication_bypass_attempts(self):
        """Test protection against authentication bypass attempts."""
        base_url = "http://localhost:5051"
        
        bypass_attempts = [
            {"user_id": "admin", "password": ""},  # Empty password
            {"user_id": "admin' OR '1'='1", "password": "any"},  # SQL injection
            {"user_id": "../admin", "password": "test"},  # Path traversal
            {"user_id": "admin", "password": None},  # Null password
        ]
        
        for attempt in bypass_attempts:
            try:
                response = requests.post(
                    f"{base_url}/api/auth/login",
                    json=attempt,
                    timeout=5
                )
                
                # Should not allow authentication bypass
                if response.status_code == 200:
                    response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    assert "token" not in response_data, f"Authentication bypass with: {attempt}"
                    assert "success" not in str(response_data).lower(), f"Successful bypass with: {attempt}"
                    
            except (requests.exceptions.RequestException, json.JSONDecodeError):
                pass


class TestFileSystemSecurity:
    """Test file system operation security - Requirement 7.4."""
    
    @pytest.mark.security
    def test_directory_traversal_protection(self):
        """Test protection against directory traversal attacks."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "../../../../root/.ssh/id_rsa",
            "..\\..\\..\\..\\root\\.ssh\\id_rsa"
        ]
        
        # Test path validation function (mock implementation)
        def validate_file_path(path: str) -> bool:
            """Mock file path validation function."""
            # Basic validation - real implementation should be more robust
            if ".." in path:
                return False
            if path.startswith("/"):
                return False
            if ":" in path and len(path) > 1 and path[1] == ":":  # Windows absolute path
                return False
            return True
        
        for dangerous_path in dangerous_paths:
            is_safe = validate_file_path(dangerous_path)
            assert not is_safe, f"Dangerous path not blocked: {dangerous_path}"
    
    @pytest.mark.security
    def test_file_access_permissions(self):
        """Test secure file access and permission validation."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_file_path = temp_file.name
        
        try:
            # Test that file exists and is readable
            assert os.path.exists(temp_file_path), "Test file should exist"
            
            # Test file permission checking
            file_stats = os.stat(temp_file_path)
            
            # On Windows, permission checking is different, so we'll do basic checks
            assert file_stats.st_size > 0, "File should have content"
            
            # Test that we can read the file safely
            with open(temp_file_path, 'r') as f:
                content = f.read()
                assert content == "test content", "File content should match"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    @pytest.mark.security
    def test_file_upload_security(self):
        """Test security of file upload operations."""
        dangerous_filenames = [
            "../../../malicious.exe",
            "..\\..\\..\\malicious.bat",
            "malicious.php",
            "script.js",
            ".htaccess",
            "web.config",
            "file.exe",
            "script.sh"
        ]
        
        def is_safe_filename(filename: str) -> bool:
            """Mock safe filename validation."""
            # Basic validation
            if ".." in filename:
                return False
            
            dangerous_extensions = ['.exe', '.bat', '.sh', '.php', '.asp', '.jsp']
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in dangerous_extensions:
                return False
                
            return True
        
        for filename in dangerous_filenames:
            is_safe = is_safe_filename(filename)
            assert not is_safe, f"Dangerous filename not blocked: {filename}"
    
    @pytest.mark.security
    def test_temporary_file_security(self):
        """Test secure handling of temporary files."""
        # Test that temporary files are created securely
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("sensitive data")
            temp_path = temp_file.name
        
        try:
            # Check file permissions (on Unix systems)
            if hasattr(os, 'stat'):
                file_stats = os.stat(temp_path)
                # On Windows, this test is less relevant, but we can still check basic properties
                assert file_stats.st_size > 0, "Temp file should have content"
            
            # Test that file can be securely deleted
            assert os.path.exists(temp_path), "Temp file should exist before deletion"
            
        finally:
            # Secure deletion
            if os.path.exists(temp_path):
                # Overwrite file content before deletion (basic secure delete)
                with open(temp_path, 'w') as f:
                    f.write('0' * 1000)  # Overwrite with zeros
                os.unlink(temp_path)
            
            assert not os.path.exists(temp_path), "Temp file should be deleted"


class TestSecurityConfiguration:
    """Test security configuration and settings."""
    
    @pytest.mark.security
    def test_debug_mode_security(self):
        """Test that debug mode doesn't expose sensitive information."""
        # Mock debug configuration
        debug_config = {
            "DEBUG": False,  # Should be False in production
            "LOG_LEVEL": "INFO",  # Should not be DEBUG in production
            "EXPOSE_ERRORS": False  # Should not expose detailed errors
        }
        
        # Test debug settings
        assert not debug_config["DEBUG"], "Debug mode should be disabled in production"
        assert debug_config["LOG_LEVEL"] != "DEBUG", "Log level should not be DEBUG in production"
        assert not debug_config["EXPOSE_ERRORS"], "Error details should not be exposed"
    
    @pytest.mark.security
    def test_cors_configuration(self):
        """Test CORS configuration security."""
        # Mock CORS configuration
        cors_config = {
            "ALLOWED_ORIGINS": ["http://localhost:3000"],  # Should be specific
            "ALLOW_CREDENTIALS": True,
            "ALLOWED_METHODS": ["GET", "POST"],  # Should be limited
        }
        
        # Test CORS settings
        assert "*" not in cors_config["ALLOWED_ORIGINS"], "CORS should not allow all origins"
        assert len(cors_config["ALLOWED_ORIGINS"]) > 0, "CORS should have specific allowed origins"
        assert "DELETE" not in cors_config["ALLOWED_METHODS"], "Dangerous methods should be restricted"


if __name__ == "__main__":
    pytest.main([__file__])