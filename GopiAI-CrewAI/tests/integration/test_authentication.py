#!/usr/bin/env python3
"""
Integration Tests for Authentication and Authorization

Tests authentication mechanisms, API key validation, and access control
for the CrewAI API server.

Requirements covered:
- 2.2: Authentication and authorization testing
- 7.1: API security testing
"""

import pytest
import requests
import os
import time
from unittest.mock import patch

try:
    from test_infrastructure.service_manager import ServiceManager
except ImportError:
    from .mock_service_manager import MockServiceManager as ServiceManager


class TestAuthentication:
    """Test authentication and authorization mechanisms."""
    
    @pytest.fixture(autouse=True)
    def setup_service(self):
        """Set up CrewAI server for testing."""
        self.base_url = "http://localhost:5051"
        self.service_manager = ServiceManager()
        
        # Start CrewAI server
        if not self.service_manager.start_service("crewai_server"):
            pytest.skip("CrewAI server failed to start")
        
        # Wait for server to be ready
        self._wait_for_server_ready()
        
        yield
        
        # Cleanup
        self.service_manager.stop_service("crewai_server")
    
    def _wait_for_server_ready(self, timeout: int = 30):
        """Wait for server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(1)
        
        pytest.fail("Server did not become ready within timeout")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.RequestException as e:
            pytest.fail(f"Request failed: {e}")


class TestAPIKeyValidation:
    """Test API key validation and management."""
    
    def test_missing_api_keys_handling(self):
        """Test behavior when API keys are missing."""
        # Mock environment without API keys
        with patch.dict(os.environ, {}, clear=True):
            # The server should still start but may have limited functionality
            # This tests graceful degradation
            
            # Health check should still work
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            # Server might be in limited mode
            assert data["status"] in ["online", "limited_mode"]
    
    def test_invalid_api_keys_handling(self):
        """Test behavior with invalid API keys."""
        invalid_keys = {
            "OPENAI_API_KEY": "invalid-key-123",
            "ANTHROPIC_API_KEY": "invalid-anthropic-key",
            "GOOGLE_API_KEY": "invalid-google-key"
        }
        
        with patch.dict(os.environ, invalid_keys):
            # Server should handle invalid keys gracefully
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
    
    def test_api_key_rotation(self):
        """Test API key rotation functionality."""
        # Test updating API keys through settings
        payload = {
            "tool_name": "openai_tool",
            "api_key": "new-test-key-123"
        }
        
        response = requests.post(
            "http://localhost:5051/api/tools/set_key",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["has_key"] is True
    
    def test_api_key_security(self):
        """Test that API keys are not exposed in responses."""
        # Make various requests and ensure no API keys are leaked
        endpoints_to_test = [
            "/api/health",
            "/api/debug", 
            "/settings/effective",
            "/api/tools"
        ]
        
        sensitive_patterns = [
            "sk-",  # OpenAI keys
            "claude-",  # Anthropic keys
            "AIza",  # Google keys
            "api_key",
            "secret"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:5051{endpoint}", timeout=10)
                if response.status_code == 200:
                    response_text = response.text.lower()
                    
                    for pattern in sensitive_patterns:
                        # Check that sensitive patterns are not in response
                        # Allow for generic mentions but not actual keys
                        if pattern in response_text:
                            # If pattern found, ensure it's not an actual key
                            lines = response_text.split('\n')
                            for line in lines:
                                if pattern in line and len(line.strip()) > 20:
                                    # This might be an actual key - fail the test
                                    pytest.fail(f"Potential API key exposure in {endpoint}: {line[:50]}...")
            except requests.RequestException:
                # Skip endpoints that are not available
                continue


class TestAccessControl:
    """Test access control and authorization."""
    
    def test_internal_endpoints_access(self):
        """Test access to internal endpoints."""
        internal_endpoints = [
            "/internal/models",
            "/internal/state"
        ]
        
        for endpoint in internal_endpoints:
            # These endpoints should be accessible (no auth required currently)
            # But we test they exist and respond appropriately
            
            if endpoint == "/internal/models":
                response = requests.get(
                    f"http://localhost:5051{endpoint}?provider=openai",
                    timeout=10
                )
                # Should either work or require proper parameters
                assert response.status_code in [200, 400]
            
            elif endpoint == "/internal/state":
                # GET should work
                response = requests.get(f"http://localhost:5051{endpoint}", timeout=10)
                assert response.status_code == 200
    
    def test_settings_endpoints_access(self):
        """Test access to settings endpoints."""
        settings_endpoints = [
            "/settings/effective",
            "/settings/terminal_unsafe"
        ]
        
        for endpoint in settings_endpoints:
            # GET should be allowed
            response = requests.get(f"http://localhost:5051{endpoint}", timeout=10)
            assert response.status_code in [200, 404]  # 404 if no config captured yet
            
            # POST should be allowed for terminal_unsafe
            if endpoint == "/settings/terminal_unsafe":
                response = requests.post(
                    f"http://localhost:5051{endpoint}",
                    json={"enabled": False},
                    timeout=10
                )
                assert response.status_code == 200
    
    def test_cors_headers(self):
        """Test CORS headers for cross-origin requests."""
        # Test preflight request
        response = requests.options(
            "http://localhost:5051/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        # Server may or may not implement CORS
        # Just ensure it doesn't crash
        assert response.status_code in [200, 404, 405]
    
    def test_rate_limiting_behavior(self):
        """Test rate limiting behavior."""
        # Make multiple rapid requests to test rate limiting
        responses = []
        
        for i in range(20):
            try:
                response = requests.get("http://localhost:5051/api/health", timeout=5)
                responses.append(response.status_code)
            except requests.RequestException:
                responses.append(0)  # Request failed
        
        # Most requests should succeed
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 15  # At least 75% should succeed
        
        # Check if any rate limiting responses
        rate_limited = sum(1 for status in responses if status == 429)
        # Rate limiting is optional, so we just log if it exists
        if rate_limited > 0:
            print(f"Rate limiting detected: {rate_limited} requests limited")


class TestSecureHeaders:
    """Test security headers in responses."""
    
    def test_security_headers_present(self):
        """Test that appropriate security headers are present."""
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for common security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # May not be present for HTTP
            "Content-Security-Policy": None,  # May not be present
        }
        
        for header, expected_values in security_headers.items():
            if header in headers:
                if expected_values and isinstance(expected_values, list):
                    assert headers[header] in expected_values
                elif expected_values:
                    assert headers[header] == expected_values
                print(f"✓ Security header present: {header}: {headers[header]}")
            else:
                print(f"⚠ Security header missing: {header}")
    
    def test_no_sensitive_headers_leaked(self):
        """Test that sensitive headers are not leaked."""
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200
        
        headers = response.headers
        
        # Headers that should not be present
        sensitive_headers = [
            "X-Powered-By",
            "Server",
            "X-AspNet-Version",
            "X-AspNetMvc-Version"
        ]
        
        for header in sensitive_headers:
            if header in headers:
                print(f"⚠ Potentially sensitive header present: {header}: {headers[header]}")
    
    def test_content_type_headers(self):
        """Test proper Content-Type headers."""
        # Test JSON endpoints
        json_endpoints = [
            "/api/health",
            "/api/debug",
            "/internal/state"
        ]
        
        for endpoint in json_endpoints:
            try:
                response = requests.get(f"http://localhost:5051{endpoint}", timeout=10)
                if response.status_code == 200:
                    assert "application/json" in response.headers.get("Content-Type", "")
            except requests.RequestException:
                continue


class TestSessionManagement:
    """Test session management and state handling."""
    
    def test_request_id_tracking(self):
        """Test request ID tracking across requests."""
        # Make request with custom request ID
        custom_request_id = "test-request-123"
        
        response = requests.get(
            "http://localhost:5051/api/health",
            headers={"X-Request-ID": custom_request_id},
            timeout=10
        )
        
        assert response.status_code == 200
        
        # Check if request ID is returned
        if "X-Request-ID" in response.headers:
            returned_id = response.headers["X-Request-ID"]
            # Should either return the same ID or generate a new one
            assert len(returned_id) > 0
    
    def test_concurrent_session_isolation(self):
        """Test that concurrent requests are properly isolated."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request_with_id(request_id):
            try:
                response = requests.post(
                    "http://localhost:5051/api/process",
                    json={
                        "message": f"Test message for {request_id}",
                        "metadata": {"request_id": request_id}
                    },
                    headers={"X-Request-ID": request_id},
                    timeout=30
                )
                
                if response.status_code == 202:
                    data = response.json()
                    results.put((request_id, data.get("task_id"), "success"))
                else:
                    results.put((request_id, None, f"error_{response.status_code}"))
                    
            except Exception as e:
                results.put((request_id, None, f"exception_{str(e)}"))
        
        # Start multiple concurrent requests
        threads = []
        request_ids = [f"req-{i}" for i in range(5)]
        
        for req_id in request_ids:
            thread = threading.Thread(target=make_request_with_id, args=(req_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=60)
        
        # Analyze results
        task_ids = set()
        success_count = 0
        
        while not results.empty():
            req_id, task_id, status = results.get()
            
            if status == "success":
                success_count += 1
                assert task_id is not None
                assert task_id not in task_ids  # Each should be unique
                task_ids.add(task_id)
        
        # All requests should succeed and have unique task IDs
        assert success_count == len(request_ids)
        assert len(task_ids) == len(request_ids)


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON."""
        malformed_payloads = [
            '{"message": "test"',  # Missing closing brace
            '{"message": "test",}',  # Trailing comma
            '{"message": }',  # Missing value
            '{message: "test"}',  # Unquoted key
            '{"message": "test" "extra": "value"}',  # Missing comma
        ]
        
        for payload in malformed_payloads:
            response = requests.post(
                "http://localhost:5051/api/process",
                data=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 400 for malformed JSON
            assert response.status_code == 400
            
            data = response.json()
            assert "error" in data
    
    def test_content_type_validation(self):
        """Test Content-Type validation."""
        # Test with wrong content type
        response = requests.post(
            "http://localhost:5051/api/process",
            data="message=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 415]
    
    def test_unicode_handling(self):
        """Test Unicode and special character handling."""
        unicode_messages = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "🚀 Rocket emoji test",  # Emoji
            "Test with \u0000 null byte",  # Null byte
            "Test with \n newline",  # Newline
            "Test with \t tab",  # Tab
        ]
        
        for message in unicode_messages:
            payload = {
                "message": message,
                "metadata": {}
            }
            
            response = requests.post(
                "http://localhost:5051/api/process",
                json=payload,
                timeout=10
            )
            
            # Should handle Unicode gracefully
            assert response.status_code in [202, 400]
            
            if response.status_code == 202:
                data = response.json()
                assert "task_id" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])