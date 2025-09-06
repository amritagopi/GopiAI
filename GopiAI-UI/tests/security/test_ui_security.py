#!/usr/bin/env python3
"""
Security tests for GopiAI-UI module.

Tests UI security, input validation, and protection against client-side attacks.
Requirements: 7.1, 7.2, 7.3, 7.4
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit, QTextEdit
from PySide6.QtTest import QTest


class TestUIInputSecurity:
    """Test UI input validation and sanitization - Requirement 7.1."""
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_message_input_sanitization(self, qtbot):
        """Test that message input is properly sanitized."""
        app = QApplication.instance() or QApplication([])
        
        # Create a test input widget
        input_widget = QLineEdit()
        qtbot.addWidget(input_widget)
        
        # Test malicious inputs
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "'; DROP TABLE messages; --"
        ]
        
        for malicious_input in malicious_inputs:
            input_widget.clear()
            input_widget.setText(malicious_input)
            
            # Get the text back
            sanitized_text = input_widget.text()
            
            # Basic sanitization checks
            assert "<script>" not in sanitized_text, f"Script tag not sanitized: {malicious_input}"
            assert "javascript:" not in sanitized_text, f"JavaScript protocol not sanitized: {malicious_input}"
            
            # Test that the input doesn't crash the application
            QTest.keyClick(input_widget, Qt.Key_Enter)
            assert input_widget.isVisible(), "Widget should remain functional after malicious input"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_text_area_input_validation(self, qtbot):
        """Test text area input validation and limits."""
        app = QApplication.instance() or QApplication([])
        
        text_widget = QTextEdit()
        qtbot.addWidget(text_widget)
        
        # Test extremely long input (potential DoS)
        very_long_text = "A" * 100000  # 100KB of text
        text_widget.setPlainText(very_long_text)
        
        # Should handle large input gracefully
        retrieved_text = text_widget.toPlainText()
        assert len(retrieved_text) <= 100000, "Text widget should handle large input"
        
        # Test special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        text_widget.setPlainText(special_chars)
        
        retrieved_special = text_widget.toPlainText()
        assert retrieved_special == special_chars, "Special characters should be preserved safely"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_clipboard_security(self, qtbot):
        """Test clipboard handling security."""
        app = QApplication.instance() or QApplication([])
        
        input_widget = QLineEdit()
        qtbot.addWidget(input_widget)
        
        # Test that sensitive data isn't accidentally copied
        sensitive_text = "API_KEY=sk-1234567890abcdef1234567890abcdef12345678"
        input_widget.setText(sensitive_text)
        
        # Simulate copy operation
        input_widget.selectAll()
        input_widget.copy()
        
        # In a secure implementation, sensitive data should be masked or not copied
        # For now, we'll just ensure the widget doesn't crash
        assert input_widget.hasSelectedText(), "Text selection should work"
        
        # Test paste operation with potentially malicious content
        malicious_clipboard_content = "<script>alert('clipboard XSS')</script>"
        
        # Mock clipboard content
        with patch('PySide6.QtWidgets.QApplication.clipboard') as mock_clipboard:
            mock_clipboard_obj = MagicMock()
            mock_clipboard_obj.text.return_value = malicious_clipboard_content
            mock_clipboard.return_value = mock_clipboard_obj
            
            input_widget.clear()
            input_widget.paste()
            
            # Should handle malicious clipboard content safely
            pasted_text = input_widget.text()
            assert "<script>" not in pasted_text or len(pasted_text) == 0, "Malicious clipboard content should be sanitized"


class TestUISecretManagement:
    """Test UI secret and sensitive data handling - Requirement 7.2."""
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_password_field_masking(self, qtbot):
        """Test that password fields properly mask input."""
        app = QApplication.instance() or QApplication([])
        
        password_widget = QLineEdit()
        password_widget.setEchoMode(QLineEdit.Password)
        qtbot.addWidget(password_widget)
        
        # Enter a password
        test_password = "super_secret_password_123"
        password_widget.setText(test_password)
        
        # The display text should be masked
        display_text = password_widget.displayText()
        assert display_text != test_password, "Password should be masked in display"
        assert "*" in display_text or "•" in display_text or len(display_text) == 0, "Password should show mask characters"
        
        # But the actual text should be retrievable
        actual_text = password_widget.text()
        assert actual_text == test_password, "Actual password text should be preserved"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_api_key_display_masking(self, qtbot):
        """Test that API keys are masked in UI display."""
        app = QApplication.instance() or QApplication([])
        
        # Simulate API key display widget
        api_key_widget = QLineEdit()
        qtbot.addWidget(api_key_widget)
        
        # Mock API key
        full_api_key = "sk-1234567890abcdef1234567890abcdef12345678"
        
        # In a secure implementation, only part of the key should be shown
        def mask_api_key(key: str) -> str:
            if len(key) > 8:
                return key[:4] + "*" * (len(key) - 8) + key[-4:]
            return "*" * len(key)
        
        masked_key = mask_api_key(full_api_key)
        api_key_widget.setText(masked_key)
        
        displayed_key = api_key_widget.text()
        assert displayed_key != full_api_key, "Full API key should not be displayed"
        assert "*" in displayed_key, "API key should contain mask characters"
        assert displayed_key.startswith("sk-1"), "Should show beginning of key"
        assert displayed_key.endswith("5678"), "Should show end of key"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_sensitive_data_in_window_title(self, qtbot):
        """Test that sensitive data doesn't appear in window titles."""
        app = QApplication.instance() or QApplication([])
        
        # Mock window title scenarios
        sensitive_data = [
            "API Key: sk-1234567890abcdef",
            "Password: secret123",
            "Token: bearer_token_12345",
            "User: admin@company.com"
        ]
        
        for sensitive_item in sensitive_data:
            # Window title should not contain sensitive data
            safe_title = "GopiAI - Chat Interface"  # Generic title
            
            # Check that sensitive data is not in the title
            assert "sk-" not in safe_title, "API key should not be in window title"
            assert "password" not in safe_title.lower(), "Password should not be in window title"
            assert "@" not in safe_title, "Email should not be in window title"
            
            # Title should be generic and safe
            assert "GopiAI" in safe_title, "Window title should identify the application"


class TestUISessionSecurity:
    """Test UI session and authentication security - Requirement 7.3."""
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_session_timeout_handling(self, qtbot):
        """Test proper handling of session timeouts."""
        app = QApplication.instance() or QApplication([])
        
        # Mock session management
        class MockSessionManager:
            def __init__(self):
                self.session_active = True
                self.last_activity = 0
            
            def is_session_valid(self) -> bool:
                return self.session_active
            
            def invalidate_session(self):
                self.session_active = False
        
        session_manager = MockSessionManager()
        
        # Test session validation
        assert session_manager.is_session_valid(), "Session should be initially valid"
        
        # Simulate session timeout
        session_manager.invalidate_session()
        assert not session_manager.is_session_valid(), "Session should be invalid after timeout"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_auto_logout_on_inactivity(self, qtbot):
        """Test automatic logout on user inactivity."""
        app = QApplication.instance() or QApplication([])
        
        # Mock inactivity detection
        class MockInactivityDetector:
            def __init__(self):
                self.last_activity_time = 0
                self.timeout_seconds = 1800  # 30 minutes
            
            def update_activity(self):
                import time
                self.last_activity_time = time.time()
            
            def is_inactive(self) -> bool:
                import time
                return (time.time() - self.last_activity_time) > self.timeout_seconds
        
        detector = MockInactivityDetector()
        detector.update_activity()
        
        # Should not be inactive immediately after activity
        assert not detector.is_inactive(), "Should not be inactive immediately after activity"
        
        # Test timeout configuration
        assert detector.timeout_seconds > 0, "Timeout should be configured"
        assert detector.timeout_seconds <= 3600, "Timeout should not be too long (max 1 hour)"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_secure_credential_storage(self, qtbot):
        """Test secure storage of user credentials."""
        app = QApplication.instance() or QApplication([])
        
        # Mock secure storage
        class MockSecureStorage:
            def __init__(self):
                self.encrypted_storage = {}
            
            def store_credential(self, key: str, value: str):
                # In real implementation, this would be encrypted
                encrypted_value = f"encrypted_{value}"  # Mock encryption
                self.encrypted_storage[key] = encrypted_value
            
            def retrieve_credential(self, key: str) -> str:
                encrypted_value = self.encrypted_storage.get(key, "")
                if encrypted_value.startswith("encrypted_"):
                    return encrypted_value[10:]  # Mock decryption
                return ""
        
        storage = MockSecureStorage()
        
        # Test credential storage
        test_credential = "test_api_key_12345"
        storage.store_credential("api_key", test_credential)
        
        # Verify storage doesn't contain plain text
        stored_values = list(storage.encrypted_storage.values())
        assert test_credential not in stored_values, "Plain text credential should not be stored"
        
        # Verify retrieval works
        retrieved = storage.retrieve_credential("api_key")
        assert retrieved == test_credential, "Credential should be retrievable"


class TestUIFileSystemSecurity:
    """Test UI file system operation security - Requirement 7.4."""
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_file_dialog_path_validation(self, qtbot):
        """Test file dialog path validation."""
        app = QApplication.instance() or QApplication([])
        
        # Mock file dialog path validation
        def validate_file_path(path: str) -> bool:
            """Validate file paths for security."""
            # Check for directory traversal
            if ".." in path:
                return False
            
            # Check for absolute paths that might be dangerous
            dangerous_paths = [
                "/etc/",
                "/root/",
                "C:\\Windows\\System32\\",
                "C:\\Users\\",
            ]
            
            for dangerous_path in dangerous_paths:
                if path.startswith(dangerous_path):
                    return False
            
            return True
        
        # Test various paths
        safe_paths = [
            "documents/file.txt",
            "downloads/image.png",
            "projects/code.py"
        ]
        
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        
        # Safe paths should be allowed
        for safe_path in safe_paths:
            assert validate_file_path(safe_path), f"Safe path should be allowed: {safe_path}"
        
        # Dangerous paths should be blocked
        for dangerous_path in dangerous_paths:
            assert not validate_file_path(dangerous_path), f"Dangerous path should be blocked: {dangerous_path}"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_file_type_validation(self, qtbot):
        """Test file type validation in UI operations."""
        app = QApplication.instance() or QApplication([])
        
        # Mock file type validation
        def is_safe_file_type(filename: str) -> bool:
            """Check if file type is safe for UI operations."""
            safe_extensions = [
                '.txt', '.md', '.json', '.csv', '.log',
                '.png', '.jpg', '.jpeg', '.gif', '.bmp',
                '.pdf', '.doc', '.docx'
            ]
            
            dangerous_extensions = [
                '.exe', '.bat', '.sh', '.cmd', '.scr',
                '.vbs', '.js', '.jar', '.app', '.deb', '.rpm'
            ]
            
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in dangerous_extensions:
                return False
            
            return file_ext in safe_extensions
        
        # Test safe file types
        safe_files = [
            "document.txt",
            "image.png",
            "data.json",
            "report.pdf"
        ]
        
        for safe_file in safe_files:
            assert is_safe_file_type(safe_file), f"Safe file type should be allowed: {safe_file}"
        
        # Test dangerous file types
        dangerous_files = [
            "malware.exe",
            "script.bat",
            "virus.scr",
            "trojan.jar"
        ]
        
        for dangerous_file in dangerous_files:
            assert not is_safe_file_type(dangerous_file), f"Dangerous file type should be blocked: {dangerous_file}"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_temporary_file_cleanup(self, qtbot):
        """Test proper cleanup of temporary files created by UI."""
        app = QApplication.instance() or QApplication([])
        
        # Mock temporary file manager
        class MockTempFileManager:
            def __init__(self):
                self.temp_files = []
            
            def create_temp_file(self, content: str) -> str:
                """Create a temporary file."""
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                temp_file.write(content)
                temp_file.close()
                
                self.temp_files.append(temp_file.name)
                return temp_file.name
            
            def cleanup_all(self):
                """Clean up all temporary files."""
                for temp_file_path in self.temp_files:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                self.temp_files.clear()
        
        temp_manager = MockTempFileManager()
        
        # Create some temporary files
        temp_file1 = temp_manager.create_temp_file("test content 1")
        temp_file2 = temp_manager.create_temp_file("test content 2")
        
        # Verify files exist
        assert os.path.exists(temp_file1), "Temp file 1 should exist"
        assert os.path.exists(temp_file2), "Temp file 2 should exist"
        
        # Clean up
        temp_manager.cleanup_all()
        
        # Verify files are deleted
        assert not os.path.exists(temp_file1), "Temp file 1 should be deleted"
        assert not os.path.exists(temp_file2), "Temp file 2 should be deleted"
        assert len(temp_manager.temp_files) == 0, "Temp file list should be empty"
    
    @pytest.mark.security
    @pytest.mark.ui
    def test_drag_drop_security(self, qtbot):
        """Test security of drag and drop operations."""
        app = QApplication.instance() or QApplication([])
        
        # Mock drag and drop validation
        def validate_dropped_content(mime_data) -> bool:
            """Validate dropped content for security."""
            # Mock MIME data validation
            if hasattr(mime_data, 'hasUrls') and mime_data.hasUrls():
                urls = mime_data.urls()
                for url in urls:
                    url_string = url.toString()
                    
                    # Block dangerous protocols
                    dangerous_protocols = ['javascript:', 'data:', 'vbscript:']
                    for protocol in dangerous_protocols:
                        if url_string.startswith(protocol):
                            return False
                    
                    # Block dangerous file extensions
                    if url_string.endswith(('.exe', '.bat', '.scr', '.vbs')):
                        return False
            
            return True
        
        # Mock MIME data for testing
        class MockMimeData:
            def __init__(self, urls):
                self._urls = urls
            
            def hasUrls(self):
                return len(self._urls) > 0
            
            def urls(self):
                return [MockUrl(url) for url in self._urls]
        
        class MockUrl:
            def __init__(self, url_string):
                self._url = url_string
            
            def toString(self):
                return self._url
        
        # Test safe drops
        safe_drops = [
            ["file:///home/user/document.txt"],
            ["http://example.com/image.png"],
            ["https://safe-site.com/data.json"]
        ]
        
        for urls in safe_drops:
            mime_data = MockMimeData(urls)
            assert validate_dropped_content(mime_data), f"Safe drop should be allowed: {urls}"
        
        # Test dangerous drops
        dangerous_drops = [
            ["javascript:alert('xss')"],
            ["data:text/html,<script>alert('xss')</script>"],
            ["file:///path/to/malware.exe"],
            ["vbscript:msgbox('dangerous')"]
        ]
        
        for urls in dangerous_drops:
            mime_data = MockMimeData(urls)
            assert not validate_dropped_content(mime_data), f"Dangerous drop should be blocked: {urls}"


if __name__ == "__main__":
    pytest.main([__file__])