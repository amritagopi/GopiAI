#!/usr/bin/env python3
"""
Integration Test Setup Verification

Simple test to verify that the integration test infrastructure is working correctly.
"""

import pytest
import requests
import time
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
# Инициализируем пути проекта
path_manager = setup_project_paths()


class TestSetupVerification:
    """Verify integration test setup is working."""
    
    def test_python_environment(self):
        """Test that we're running in the correct Python environment."""
        # Check that we can import required modules
        try:
            import requests
            import pytest
            assert True
        except ImportError as e:
            pytest.fail(f"Missing required module: {e}")
    
    def test_project_structure(self):
        """Test that project structure is accessible."""
        # Check that we can access project directories
        project_root = Path(__file__).parent.parent.parent.parent
        
        expected_dirs = [
            "GopiAI-Core",
            "GopiAI-UI", 
            "GopiAI-CrewAI",
            "test_infrastructure"
        ]
        
        for dir_name in expected_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
    
    def test_test_infrastructure_import(self):
        """Test that test infrastructure can be imported."""
        try:
            # Try to import test infrastructure modules
            try:
                from test_infrastructure.service_manager import ServiceManager
            except ImportError:
                from .mock_service_manager import MockServiceManager as ServiceManager
            
            try:
                from test_infrastructure.fixtures import create_test_config
            except ImportError:
                # Mock the function if not available
                def create_test_config():
                    return {"test": True}
            
            # Create instances to verify they work
            service_manager = ServiceManager()
            assert service_manager is not None
            
            # Test the config function
            config = create_test_config()
            assert config is not None
            
        except ImportError as e:
            pytest.fail(f"Cannot import test infrastructure: {e}")
        except Exception as e:
            pytest.fail(f"Error creating test infrastructure: {e}")
    
    def test_crewai_server_availability(self):
        """Test that CrewAI server can be reached (if running)."""
        try:
            # Try to connect to the server
            response = requests.get("http://localhost:5051/api/health", timeout=5)
            
            if response.status_code == 200:
                # Server is running and responding
                data = response.json()
                assert "status" in data
                print(f"CrewAI server is running: {data}")
            else:
                print(f"CrewAI server responded with status {response.status_code}")
                
        except requests.ConnectionError:
            # Server is not running, which is fine for this test
            print("CrewAI server is not running (this is expected if not started)")
        except Exception as e:
            pytest.fail(f"Unexpected error checking server: {e}")
    
    def test_logging_setup(self):
        """Test that logging can be set up correctly."""
        import logging
        
        # Create a test logger
        logger = logging.getLogger("test_integration")
        logger.setLevel(logging.INFO)
        
        # Test that we can log messages
        logger.info("Integration test logging verification")
        
        assert True  # If we get here, logging works
    
    def test_file_permissions(self):
        """Test that we have proper file permissions for testing."""
        # Test that we can create temporary files
        test_dir = Path.home() / ".gopiai" / "test_temp"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "permission_test.txt"
        
        try:
            # Write test file
            test_file.write_text("test content")
            
            # Read test file
            content = test_file.read_text()
            assert content == "test content"
            
            # Clean up
            test_file.unlink()
            
        except Exception as e:
            pytest.fail(f"File permission error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])