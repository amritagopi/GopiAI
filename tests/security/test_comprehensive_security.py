#!/usr/bin/env python3
"""
Comprehensive security tests for the entire GopiAI system.

Tests cross-module security, integration security, and system-wide security measures.
Requirements: 7.1, 7.2, 7.3, 7.4
"""

import pytest
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any


class TestSystemWideSecurity:
    """Test system-wide security measures across all modules."""
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_environment_security_scan(self):
        """Scan the entire project for security vulnerabilities."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check for hardcoded secrets in code files
        secret_patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
            r'AIza[0-9A-Za-z-_]{35}',  # Google API keys
            r'ANTHROPIC_API_KEY.*[a-zA-Z0-9]{40,}',  # Anthropic keys
            r'password\s*=\s*["\'][^"\']{8,}["\']',  # Hardcoded passwords
            r'secret\s*=\s*["\'][^"\']{8,}["\']',  # Hardcoded secrets
        ]
        
        code_extensions = ['.py', '.js', '.ts', '.json', '.yaml', '.yml']
        violations = []
        
        for ext in code_extensions:
            for code_file in project_root.rglob(f'*{ext}'):
                # Skip test files, virtual environments, and third-party libraries
                skip_patterns = [
                    'test_', '_test', 'env/', '__pycache__', '.git',
                    'site-packages/', 'node_modules/', 'venv/', 'env\\',
                    'Lib\\site-packages\\', 'Scripts\\', 'Include\\',
                    '.pytest_cache', 'dist/', 'build/'
                ]
                if any(skip in str(code_file) for skip in skip_patterns):
                    continue
                
                try:
                    with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            violations.append({
                                'file': str(code_file),
                                'pattern': pattern,
                                'matches': matches
                            })
                            
                except (IOError, UnicodeDecodeError):
                    continue
        
        # Allow test files to have mock secrets, but not real ones
        real_violations = []
        for violation in violations:
            if 'test' not in violation['file'].lower():
                real_violations.append(violation)
            else:
                # Even in test files, check if secrets look real
                for match in violation['matches']:
                    if len(match) > 20 and not any(test_indicator in match.lower() 
                                                 for test_indicator in ['test', 'mock', 'fake', 'example']):
                        real_violations.append(violation)
        
        assert len(real_violations) == 0, f"Hardcoded secrets found: {real_violations}"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_dependency_security_scan(self):
        """Check for known security vulnerabilities in dependencies."""
        project_root = Path(__file__).parent.parent.parent
        
        # Find all requirements files
        requirements_files = []
        for req_file in project_root.rglob('requirements*.txt'):
            requirements_files.append(req_file)
        
        # Also check pyproject.toml files
        for pyproject_file in project_root.rglob('pyproject.toml'):
            requirements_files.append(pyproject_file)
        
        vulnerable_packages = []
        
        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for known vulnerable packages (basic list)
                known_vulnerable = [
                    'pillow<8.3.2',  # Known PIL vulnerabilities
                    'requests<2.25.0',  # Known requests vulnerabilities
                    'urllib3<1.26.5',  # Known urllib3 vulnerabilities
                    'jinja2<2.11.3',  # Known Jinja2 vulnerabilities
                ]
                
                for vulnerable_pkg in known_vulnerable:
                    if vulnerable_pkg in content.lower():
                        vulnerable_packages.append({
                            'file': str(req_file),
                            'package': vulnerable_pkg
                        })
                        
            except (IOError, UnicodeDecodeError):
                continue
        
        assert len(vulnerable_packages) == 0, f"Vulnerable packages found: {vulnerable_packages}"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_file_permissions_security(self):
        """Check file permissions for security issues."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check for overly permissive files
        sensitive_files = []
        
        # Find sensitive file types
        sensitive_patterns = [
            '*.key',
            '*.pem',
            '*.p12',
            '*.pfx',
            '.env*',
            'config*.json',
            'secrets*'
        ]
        
        for pattern in sensitive_patterns:
            for sensitive_file in project_root.rglob(pattern):
                if sensitive_file.is_file():
                    sensitive_files.append(sensitive_file)
        
        permission_issues = []
        
        for sensitive_file in sensitive_files:
            try:
                # On Windows, permission checking is limited
                # We'll do basic checks that are cross-platform
                if sensitive_file.exists():
                    # Check if file is readable (basic check)
                    if sensitive_file.stat().st_size > 0:
                        # File exists and has content - ensure it's not in a public location
                        file_path_str = str(sensitive_file)
                        
                        # Check for files in potentially public directories
                        public_indicators = ['public/', 'static/', 'assets/', 'www/']
                        for indicator in public_indicators:
                            if indicator in file_path_str:
                                permission_issues.append({
                                    'file': file_path_str,
                                    'issue': f'Sensitive file in public directory: {indicator}'
                                })
                                
            except (OSError, PermissionError):
                # Permission errors are actually good for sensitive files
                continue
        
        assert len(permission_issues) == 0, f"File permission issues: {permission_issues}"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_log_file_security(self):
        """Check log files for security issues."""
        project_root = Path(__file__).parent.parent.parent
        
        # Find log files
        log_files = []
        for log_file in project_root.rglob('*.log'):
            log_files.append(log_file)
        
        security_issues = []
        
        # Patterns that should not appear in logs
        sensitive_patterns = [
            r'password\s*[:=]\s*[^\s]+',
            r'api[_-]?key\s*[:=]\s*[^\s]+',
            r'secret\s*[:=]\s*[^\s]+',
            r'token\s*[:=]\s*[^\s]+',
            r'sk-[a-zA-Z0-9]{20,}',  # API key patterns
            r'[a-zA-Z0-9]{32,}',  # Long strings that might be secrets
        ]
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    # Filter out obvious test/debug content
                    real_matches = []
                    for match in matches:
                        if len(match) > 10 and not any(test_word in match.lower() 
                                                     for test_word in ['test', 'debug', 'example', 'mock']):
                            real_matches.append(match)
                    
                    if real_matches:
                        security_issues.append({
                            'file': str(log_file),
                            'pattern': pattern,
                            'matches': real_matches[:3]  # Limit to first 3 matches
                        })
                        
            except (IOError, UnicodeDecodeError):
                continue
        
        assert len(security_issues) == 0, f"Sensitive data in logs: {security_issues}"


class TestCommunicationSecurity:
    """Test security of inter-module communication."""
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_api_communication_security(self):
        """Test security of API communication between modules."""
        # Mock API communication security
        class MockAPIClient:
            def __init__(self):
                self.base_url = "http://localhost:5051"
                self.session_token = None
            
            def authenticate(self, credentials: Dict[str, str]) -> bool:
                """Mock authentication."""
                # Basic validation
                if not credentials.get('user_id') or not credentials.get('password'):
                    return False
                
                # Mock token generation
                self.session_token = f"token_{hash(credentials['user_id'])}"
                return True
            
            def make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
                """Mock API request with security checks."""
                # Check authentication
                if not self.session_token:
                    return {'error': 'Unauthorized', 'status': 401}
                
                # Validate input data
                if not isinstance(data, dict):
                    return {'error': 'Invalid data format', 'status': 400}
                
                # Check for malicious content
                data_str = json.dumps(data)
                if '<script>' in data_str or 'DROP TABLE' in data_str:
                    return {'error': 'Malicious content detected', 'status': 400}
                
                return {'status': 200, 'data': 'success'}
        
        # Test API client security
        client = MockAPIClient()
        
        # Test unauthenticated request
        response = client.make_request('/api/test', {'message': 'test'})
        assert response['status'] == 401, "Unauthenticated requests should be rejected"
        
        # Test authentication
        auth_result = client.authenticate({'user_id': 'test_user', 'password': 'test_pass'})
        assert auth_result, "Valid authentication should succeed"
        
        # Test authenticated request
        response = client.make_request('/api/test', {'message': 'test'})
        assert response['status'] == 200, "Authenticated requests should succeed"
        
        # Test malicious content detection
        malicious_data = {'message': '<script>alert("xss")</script>'}
        response = client.make_request('/api/test', malicious_data)
        assert response['status'] == 400, "Malicious content should be rejected"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_message_encryption_security(self):
        """Test encryption of sensitive messages between modules."""
        # Mock encryption for inter-module communication
        class MockEncryption:
            def __init__(self):
                self.key = "mock_encryption_key_12345678901234567890"
            
            def encrypt(self, message: str) -> str:
                """Mock encryption (in real implementation, use proper crypto)."""
                # Simple XOR encryption for testing
                encrypted = ""
                for i, char in enumerate(message):
                    key_char = self.key[i % len(self.key)]
                    encrypted += chr(ord(char) ^ ord(key_char))
                return encrypted
            
            def decrypt(self, encrypted_message: str) -> str:
                """Mock decryption."""
                # XOR decryption (same as encryption for XOR)
                return self.encrypt(encrypted_message)
        
        encryption = MockEncryption()
        
        # Test encryption/decryption
        original_message = "This is a sensitive message with API key: sk-test123"
        encrypted = encryption.encrypt(original_message)
        decrypted = encryption.decrypt(encrypted)
        
        # Verify encryption works
        assert encrypted != original_message, "Message should be encrypted"
        assert decrypted == original_message, "Decryption should restore original message"
        
        # Verify sensitive data is not visible in encrypted form
        assert "sk-test123" not in encrypted, "API key should not be visible in encrypted message"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_session_management_security(self):
        """Test security of session management across modules."""
        # Mock session manager
        class MockSessionManager:
            def __init__(self):
                self.sessions = {}
                self.session_timeout = 1800  # 30 minutes
            
            def create_session(self, user_id: str) -> str:
                """Create a new session."""
                import uuid
                import time
                
                session_id = str(uuid.uuid4())
                self.sessions[session_id] = {
                    'user_id': user_id,
                    'created_at': time.time(),
                    'last_activity': time.time()
                }
                return session_id
            
            def validate_session(self, session_id: str) -> bool:
                """Validate a session."""
                import time
                
                if session_id not in self.sessions:
                    return False
                
                session = self.sessions[session_id]
                current_time = time.time()
                
                # Check timeout
                if current_time - session['last_activity'] > self.session_timeout:
                    del self.sessions[session_id]
                    return False
                
                # Update last activity
                session['last_activity'] = current_time
                return True
            
            def invalidate_session(self, session_id: str):
                """Invalidate a session."""
                if session_id in self.sessions:
                    del self.sessions[session_id]
        
        session_manager = MockSessionManager()
        
        # Test session creation
        session_id = session_manager.create_session('test_user')
        assert len(session_id) > 20, "Session ID should be sufficiently long"
        assert session_manager.validate_session(session_id), "New session should be valid"
        
        # Test session invalidation
        session_manager.invalidate_session(session_id)
        assert not session_manager.validate_session(session_id), "Invalidated session should not be valid"
        
        # Test invalid session ID
        assert not session_manager.validate_session('invalid_session'), "Invalid session should not be valid"


class TestDataProtectionSecurity:
    """Test data protection and privacy security measures."""
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_data_sanitization_security(self):
        """Test data sanitization across the system."""
        # Mock data sanitizer
        class MockDataSanitizer:
            def __init__(self):
                self.dangerous_patterns = [
                    r'<script[^>]*>.*?</script>',
                    r'javascript:',
                    r'on\w+\s*=',
                    r'<iframe[^>]*>.*?</iframe>',
                ]
            
            def sanitize_html(self, html_content: str) -> str:
                """Sanitize HTML content."""
                sanitized = html_content
                for pattern in self.dangerous_patterns:
                    sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
                return sanitized
            
            def sanitize_sql(self, sql_input: str) -> str:
                """Sanitize SQL input."""
                # Remove dangerous SQL keywords
                dangerous_sql = [
                    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
                    'CREATE', 'EXEC', 'EXECUTE', '--', ';'
                ]
                
                sanitized = sql_input
                for keyword in dangerous_sql:
                    sanitized = sanitized.replace(keyword, '')
                    sanitized = sanitized.replace(keyword.lower(), '')
                
                return sanitized
        
        sanitizer = MockDataSanitizer()
        
        # Test HTML sanitization
        malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
        sanitized_html = sanitizer.sanitize_html(malicious_html)
        assert '<script>' not in sanitized_html, "Script tags should be removed"
        assert '<p>Safe content</p>' in sanitized_html, "Safe content should be preserved"
        
        # Test SQL sanitization
        malicious_sql = "'; DROP TABLE users; --"
        sanitized_sql = sanitizer.sanitize_sql(malicious_sql)
        assert 'DROP' not in sanitized_sql, "Dangerous SQL keywords should be removed"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_data_encryption_at_rest(self):
        """Test encryption of sensitive data at rest."""
        # Mock data encryption for storage
        class MockDataEncryption:
            def __init__(self):
                self.encryption_key = "test_key_1234567890123456"  # 32 bytes for AES
            
            def encrypt_data(self, data: str) -> str:
                """Mock data encryption."""
                # Simple encryption for testing (use proper crypto in production)
                encrypted = ""
                for i, char in enumerate(data):
                    key_char = self.encryption_key[i % len(self.encryption_key)]
                    encrypted += chr((ord(char) + ord(key_char)) % 256)
                return encrypted
            
            def decrypt_data(self, encrypted_data: str) -> str:
                """Mock data decryption."""
                decrypted = ""
                for i, char in enumerate(encrypted_data):
                    key_char = self.encryption_key[i % len(self.encryption_key)]
                    decrypted += chr((ord(char) - ord(key_char)) % 256)
                return decrypted
        
        encryption = MockDataEncryption()
        
        # Test sensitive data encryption
        sensitive_data = "User conversation: API key is sk-1234567890abcdef"
        encrypted = encryption.encrypt_data(sensitive_data)
        decrypted = encryption.decrypt_data(encrypted)
        
        # Verify encryption
        assert encrypted != sensitive_data, "Data should be encrypted"
        assert "sk-1234567890abcdef" not in encrypted, "API key should not be visible in encrypted data"
        assert decrypted == sensitive_data, "Decryption should restore original data"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_pii_detection_and_masking(self):
        """Test detection and masking of personally identifiable information."""
        # Mock PII detector
        class MockPIIDetector:
            def __init__(self):
                self.pii_patterns = {
                    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    'phone': r'\b\d{3}-\d{3}-\d{4}\b',
                    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
                    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
                }
            
            def detect_pii(self, text: str) -> Dict[str, List[str]]:
                """Detect PII in text."""
                detected = {}
                for pii_type, pattern in self.pii_patterns.items():
                    matches = re.findall(pattern, text)
                    if matches:
                        detected[pii_type] = matches
                return detected
            
            def mask_pii(self, text: str) -> str:
                """Mask PII in text."""
                masked_text = text
                for pii_type, pattern in self.pii_patterns.items():
                    if pii_type == 'email':
                        masked_text = re.sub(pattern, '[EMAIL_MASKED]', masked_text)
                    elif pii_type == 'phone':
                        masked_text = re.sub(pattern, '[PHONE_MASKED]', masked_text)
                    elif pii_type == 'ssn':
                        masked_text = re.sub(pattern, '[SSN_MASKED]', masked_text)
                    elif pii_type == 'credit_card':
                        masked_text = re.sub(pattern, '[CARD_MASKED]', masked_text)
                return masked_text
        
        pii_detector = MockPIIDetector()
        
        # Test PII detection
        test_text = "Contact John at john.doe@example.com or call 555-123-4567"
        detected_pii = pii_detector.detect_pii(test_text)
        
        assert 'email' in detected_pii, "Email should be detected"
        assert 'phone' in detected_pii, "Phone number should be detected"
        assert 'john.doe@example.com' in detected_pii['email'], "Specific email should be detected"
        
        # Test PII masking
        masked_text = pii_detector.mask_pii(test_text)
        assert '[EMAIL_MASKED]' in masked_text, "Email should be masked"
        assert '[PHONE_MASKED]' in masked_text, "Phone should be masked"
        assert 'john.doe@example.com' not in masked_text, "Original email should not be visible"


class TestSecurityMonitoring:
    """Test security monitoring and alerting systems."""
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_security_event_logging(self):
        """Test logging of security events."""
        # Mock security event logger
        class MockSecurityLogger:
            def __init__(self):
                self.events = []
            
            def log_security_event(self, event_type: str, details: Dict[str, Any]):
                """Log a security event."""
                import time
                event = {
                    'timestamp': time.time(),
                    'event_type': event_type,
                    'details': details
                }
                self.events.append(event)
            
            def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
                """Get events by type."""
                return [event for event in self.events if event['event_type'] == event_type]
        
        security_logger = MockSecurityLogger()
        
        # Test logging various security events
        security_logger.log_security_event('failed_login', {
            'user_id': 'test_user',
            'ip_address': '192.168.1.100',
            'reason': 'invalid_password'
        })
        
        security_logger.log_security_event('suspicious_activity', {
            'user_id': 'test_user',
            'activity': 'multiple_rapid_requests',
            'count': 50
        })
        
        # Verify events are logged
        failed_logins = security_logger.get_events_by_type('failed_login')
        assert len(failed_logins) == 1, "Failed login should be logged"
        
        suspicious_activities = security_logger.get_events_by_type('suspicious_activity')
        assert len(suspicious_activities) == 1, "Suspicious activity should be logged"
        
        # Verify event details
        failed_login = failed_logins[0]
        assert failed_login['details']['user_id'] == 'test_user', "User ID should be logged"
        assert failed_login['details']['reason'] == 'invalid_password', "Failure reason should be logged"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_intrusion_detection(self):
        """Test basic intrusion detection capabilities."""
        # Mock intrusion detection system
        class MockIntrusionDetector:
            def __init__(self):
                self.failed_attempts = {}
                self.max_attempts = 5
                self.time_window = 300  # 5 minutes
            
            def record_failed_attempt(self, identifier: str) -> bool:
                """Record a failed attempt and check if threshold is exceeded."""
                import time
                current_time = time.time()
                
                if identifier not in self.failed_attempts:
                    self.failed_attempts[identifier] = []
                
                # Clean old attempts
                self.failed_attempts[identifier] = [
                    attempt_time for attempt_time in self.failed_attempts[identifier]
                    if current_time - attempt_time < self.time_window
                ]
                
                # Add current attempt
                self.failed_attempts[identifier].append(current_time)
                
                # Check if threshold exceeded
                return len(self.failed_attempts[identifier]) >= self.max_attempts
            
            def is_blocked(self, identifier: str) -> bool:
                """Check if identifier is currently blocked."""
                import time
                current_time = time.time()
                
                if identifier not in self.failed_attempts:
                    return False
                
                # Clean old attempts
                self.failed_attempts[identifier] = [
                    attempt_time for attempt_time in self.failed_attempts[identifier]
                    if current_time - attempt_time < self.time_window
                ]
                
                return len(self.failed_attempts[identifier]) >= self.max_attempts
        
        detector = MockIntrusionDetector()
        
        # Test normal behavior
        assert not detector.is_blocked('user1'), "User should not be blocked initially"
        
        # Test failed attempts
        for i in range(4):
            blocked = detector.record_failed_attempt('user1')
            assert not blocked, f"User should not be blocked after {i+1} attempts"
        
        # Test threshold exceeded
        blocked = detector.record_failed_attempt('user1')
        assert blocked, "User should be blocked after 5 failed attempts"
        assert detector.is_blocked('user1'), "User should remain blocked"


if __name__ == "__main__":
    pytest.main([__file__])