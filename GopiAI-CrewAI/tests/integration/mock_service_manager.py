#!/usr/bin/env python3
"""
Mock Service Manager for Integration Tests

Simplified service manager for integration tests that doesn't require
external dependencies like psutil.
"""

import time
import requests
import logging


class MockServiceManager:
    """Simplified service manager for integration tests."""
    
    def __init__(self):
        self.services = {}
        self.logger = logging.getLogger(__name__)
    
    def start_service(self, service_name: str) -> bool:
        """Start a service (simplified implementation)."""
        if service_name == "crewai_server":
            return self._start_crewai_server()
        
        self.logger.warning(f"Unknown service: {service_name}")
        return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a service (simplified implementation)."""
        if service_name in self.services:
            process = self.services[service_name]
            try:
                if hasattr(process, 'terminate'):
                    process.terminate()
                    process.wait(timeout=10)
                del self.services[service_name]
                return True
            except Exception as e:
                self.logger.error(f"Error stopping {service_name}: {e}")
                return False
        
        return True  # Service not running, consider it stopped
    
    def _start_crewai_server(self) -> bool:
        """Start the CrewAI server."""
        # Check if server is already running
        if self._is_server_running():
            self.logger.info("CrewAI server is already running")
            return True
        
        # Try to start the server (simplified - just check if it can be reached)
        # In a real implementation, this would start the actual server process
        self.logger.info("Checking if CrewAI server can be started...")
        
        # For integration tests, we assume the server is started externally
        # or we just verify it can be reached
        return self._wait_for_server_ready()
    
    def _is_server_running(self) -> bool:
        """Check if the CrewAI server is running."""
        try:
            response = requests.get("http://localhost:5051/api/health", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _wait_for_server_ready(self, timeout: int = 30) -> bool:
        """Wait for the server to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._is_server_running():
                self.logger.info("CrewAI server is ready")
                return True
            time.sleep(1)
        
        self.logger.error("CrewAI server did not become ready within timeout")
        return False
    
    def get_service_status(self, service_name: str) -> str:
        """Get the status of a service."""
        if service_name == "crewai_server":
            return "running" if self._is_server_running() else "stopped"
        
        return "unknown"
    
    def cleanup_all_services(self):
        """Clean up all managed services."""
        for service_name in list(self.services.keys()):
            self.stop_service(service_name)