#!/usr/bin/env python3
"""
Service Management System for GopiAI Testing Infrastructure

Manages the lifecycle of services required for testing, including:
- CrewAI API server
- UI application (for E2E tests)
- Memory system (txtai)
- Test data isolation
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import requests
import psutil


class ServiceStatus(Enum):
    """Service status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    command: List[str]
    working_directory: str
    environment_vars: Dict[str, str]
    health_check_url: Optional[str] = None
    health_check_timeout: int = 30
    startup_timeout: int = 60
    port: Optional[int] = None
    log_file: Optional[str] = None


@dataclass
class ServiceInfo:
    """Information about a running service."""
    name: str
    status: ServiceStatus
    pid: Optional[int] = None
    port: Optional[int] = None
    process: Optional[subprocess.Popen] = None
    start_time: Optional[float] = None
    log_file: Optional[str] = None


class ServiceManager:
    """Manages services required for testing."""
    
    def __init__(self, root_path: str = ".", test_mode: bool = True):
        self.root_path = Path(root_path)
        self.services: Dict[str, ServiceInfo] = {}
        self.logger = self._setup_logging()
        self.test_mode = test_mode
        self._shutdown_handlers_registered = False
        self._test_isolation_setup = False
        
        # Service configurations
        self.service_configs = self._create_service_configs()
        
        # Test data isolation paths
        self.test_data_paths = {
            "conversations": self.root_path / "test_conversations",
            "memory": self.root_path / "test_memory", 
            "logs": self.root_path / "test_logs",
            "cache": self.root_path / "test_cache",
            "config": self.root_path / "test_config"
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the service manager."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _create_service_configs(self) -> Dict[str, ServiceConfig]:
        """Create service configurations."""
        configs = {}
        
        # CrewAI API Server
        configs["crewai_server"] = ServiceConfig(
            name="crewai_server",
            command=[str(sys.executable), "crewai_api_server.py"],
            working_directory=str(self.root_path / "GopiAI-CrewAI"),
            environment_vars={
                "CREWAI_TEST_MODE": "true",
                "FLASK_ENV": "testing"
            },
            health_check_url="http://localhost:5051/health",
            port=5051,
            log_file="test_crewai_server.log"
        )
        
        # UI Application (for E2E tests)
        configs["ui_app"] = ServiceConfig(
            name="ui_app",
            command=[str(sys.executable), "-m", "gopiai.ui.main", "--test-mode"],
            working_directory=str(self.root_path / "GopiAI-UI"),
            environment_vars={
                "QT_QPA_PLATFORM": "offscreen",  # For headless testing
                "DISPLAY": ":99"  # Virtual display
            },
            startup_timeout=30,
            log_file="test_ui_app.log"
        )
        
        # Memory System (txtai)
        configs["memory_system"] = ServiceConfig(
            name="memory_system",
            command=[str(sys.executable), "memory_server.py"],
            working_directory=str(self.root_path / "rag_memory_system"),
            environment_vars={
                "TXTAI_TEST_MODE": "true"
            },
            health_check_url="http://localhost:8000/health",
            port=8000,
            log_file="test_memory_system.log"
        )
        
        return configs
    
    
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.service_configs:
            self.logger.error(f"Service {service_name} not configured")
            return False
        
        if service_name in self.services:
            current_status = self.services[service_name].status
            if current_status == ServiceStatus.RUNNING:
                self.logger.info(f"Service {service_name} is already running")
                return True
            elif current_status == ServiceStatus.STARTING:
                self.logger.info(f"Service {service_name} is already starting")
                return self._wait_for_service_start(service_name)
        
        config = self.service_configs[service_name]
        self.logger.info(f"Starting service: {service_name}")
        
        # Create service info
        service_info = ServiceInfo(
            name=service_name,
            status=ServiceStatus.STARTING,
            port=config.port,
            start_time=time.time()
        )
        self.services[service_name] = service_info
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(config.environment_vars)
            
            # Prepare log file
            if config.log_file:
                log_path = Path(config.working_directory) / config.log_file
                service_info.log_file = str(log_path)
                log_file = open(log_path, 'w')
            else:
                log_file = subprocess.PIPE
            
            # Start the process
            process = subprocess.Popen(
                config.command,
                cwd=config.working_directory,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            service_info.process = process
            service_info.pid = process.pid
            
            # Wait for service to start
            if self._wait_for_service_start(service_name):
                service_info.status = ServiceStatus.RUNNING
                self.logger.info(f"Service {service_name} started successfully (PID: {process.pid})")
                
                # Register shutdown handlers
                if not self._shutdown_handlers_registered:
                    self._register_shutdown_handlers()
                
                return True
            else:
                service_info.status = ServiceStatus.ERROR
                self.logger.error(f"Service {service_name} failed to start")
                self._cleanup_failed_service(service_name)
                return False
                
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            self.logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    def _wait_for_service_start(self, service_name: str) -> bool:
        """Wait for a service to start and become healthy."""
        config = self.service_configs[service_name]
        service_info = self.services[service_name]
        
        start_time = time.time()
        timeout = config.startup_timeout
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if service_info.process and service_info.process.poll() is not None:
                self.logger.error(f"Service {service_name} process terminated unexpectedly")
                return False
            
            # Check health endpoint if available
            if config.health_check_url:
                try:
                    response = requests.get(
                        config.health_check_url,
                        timeout=config.health_check_timeout
                    )
                    if response.status_code == 200:
                        return True
                except requests.RequestException:
                    pass
            else:
                # For services without health check, just wait a bit
                if time.time() - start_time > 5:  # Give it 5 seconds
                    return True
            
            time.sleep(1)
        
        return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            self.logger.warning(f"Service {service_name} is not running")
            return True
        
        service_info = self.services[service_name]
        if service_info.status == ServiceStatus.STOPPED:
            return True
        
        self.logger.info(f"Stopping service: {service_name}")
        service_info.status = ServiceStatus.STOPPING
        
        try:
            if service_info.process:
                # Try graceful shutdown first
                service_info.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    service_info.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.logger.warning(f"Force killing service {service_name}")
                    service_info.process.kill()
                    service_info.process.wait()
                
                service_info.status = ServiceStatus.STOPPED
                service_info.process = None
                service_info.pid = None
                
                self.logger.info(f"Service {service_name} stopped successfully")
                return True
            
        except Exception as e:
            self.logger.error(f"Error stopping service {service_name}: {e}")
            service_info.status = ServiceStatus.ERROR
            return False
        
        return True
    
    def _cleanup_failed_service(self, service_name: str):
        """Clean up a failed service."""
        if service_name in self.services:
            service_info = self.services[service_name]
            if service_info.process:
                try:
                    service_info.process.kill()
                    service_info.process.wait()
                except:
                    pass
            del self.services[service_name]
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get the status of a service."""
        if service_name not in self.services:
            return ServiceStatus.STOPPED
        
        service_info = self.services[service_name]
        
        # Check if process is still running
        if service_info.process and service_info.process.poll() is not None:
            service_info.status = ServiceStatus.STOPPED
            service_info.process = None
            service_info.pid = None
        
        return service_info.status
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        if service_name not in self.service_configs:
            return False
        
        config = self.service_configs[service_name]
        
        # Check if service is running
        if self.get_service_status(service_name) != ServiceStatus.RUNNING:
            return False
        
        # Check health endpoint if available
        if config.health_check_url:
            try:
                response = requests.get(
                    config.health_check_url,
                    timeout=config.health_check_timeout
                )
                return response.status_code == 200
            except requests.RequestException:
                return False
        
        # If no health check URL, assume healthy if running
        return True
    
    def comprehensive_health_check(self) -> Dict[str, Dict[str, Any]]:
        """Perform comprehensive health check on all services."""
        self.logger.info("Performing comprehensive health check...")
        
        health_report = {}
        
        for service_name in self.service_configs:
            service_health = {
                "status": self.get_service_status(service_name).value,
                "healthy": False,
                "details": {},
                "test_isolation_verified": False,
                "dependencies_met": False
            }
            
            if service_name in self.services:
                service_info = self.services[service_name]
                service_health["details"] = {
                    "pid": service_info.pid,
                    "port": service_info.port,
                    "start_time": service_info.start_time,
                    "log_file": service_info.log_file,
                    "uptime": time.time() - service_info.start_time if service_info.start_time else 0
                }
            
            # Check basic health
            service_health["healthy"] = self.check_service_health(service_name)
            
            # Verify test isolation for this service
            service_health["test_isolation_verified"] = self._verify_service_test_isolation(service_name)
            
            # Check service dependencies
            service_health["dependencies_met"] = self._check_service_dependencies(service_name)
            
            # Additional checks based on service type
            if service_name == "crewai_server":
                service_health["details"].update(self._check_crewai_health())
            elif service_name == "memory_system":
                service_health["details"].update(self._check_memory_health())
            elif service_name == "ui_app":
                service_health["details"].update(self._check_ui_health())
            
            health_report[service_name] = service_health
        
        return health_report
    
    def _check_crewai_health(self) -> Dict[str, Any]:
        """Detailed health check for CrewAI server."""
        details = {}
        
        try:
            # Check main health endpoint
            response = requests.get("http://localhost:5051/health", timeout=5)
            details["health_endpoint"] = response.status_code == 200
            
            # Check if API endpoints are responding
            endpoints_to_check = ["/api/models", "/api/status"]
            endpoint_health = {}
            
            for endpoint in endpoints_to_check:
                try:
                    resp = requests.get(f"http://localhost:5051{endpoint}", timeout=3)
                    endpoint_health[endpoint] = resp.status_code in [200, 404]  # 404 is ok for some endpoints
                except:
                    endpoint_health[endpoint] = False
            
            details["endpoints"] = endpoint_health
            details["all_endpoints_healthy"] = all(endpoint_health.values())
            
        except Exception as e:
            details["error"] = str(e)
            details["health_endpoint"] = False
            details["all_endpoints_healthy"] = False
        
        return details
    
    def _check_memory_health(self) -> Dict[str, Any]:
        """Detailed health check for memory system."""
        details = {}
        
        try:
            # Check if txtai index exists and is accessible
            index_path = self.test_data_paths["memory"] / "txtai_test_index"
            details["index_path_exists"] = index_path.exists()
            
            # Check memory directory permissions
            memory_dir = self.test_data_paths["memory"]
            details["memory_dir_writable"] = os.access(memory_dir, os.W_OK)
            
            # If memory service has health endpoint, check it
            try:
                response = requests.get("http://localhost:8000/health", timeout=3)
                details["health_endpoint"] = response.status_code == 200
            except:
                details["health_endpoint"] = False
                
        except Exception as e:
            details["error"] = str(e)
        
        return details
    
    def _check_ui_health(self) -> Dict[str, Any]:
        """Detailed health check for UI application."""
        details = {}
        
        try:
            # Check if UI process is responsive (basic check)
            if "ui_app" in self.services:
                service_info = self.services["ui_app"]
                if service_info.process:
                    details["process_responsive"] = service_info.process.poll() is None
                else:
                    details["process_responsive"] = False
            
            # Check if test display is available (for headless testing)
            details["display_available"] = os.environ.get("DISPLAY") is not None
            details["qt_platform"] = os.environ.get("QT_QPA_PLATFORM", "default")
            
        except Exception as e:
            details["error"] = str(e)
        
        return details
    
    def _verify_service_test_isolation(self, service_name: str) -> bool:
        """Verify that a service is properly isolated for testing."""
        try:
            if service_name == "crewai_server":
                # Check that CrewAI is using test environment
                test_indicators = [
                    os.environ.get("CREWAI_TEST_MODE") == "true",
                    os.environ.get("FLASK_ENV") == "testing"
                ]
                return all(test_indicators)
            
            elif service_name == "ui_app":
                # Check that UI is using test mode and headless display
                test_indicators = [
                    os.environ.get("QT_QPA_PLATFORM") == "offscreen"
                ]
                return all(test_indicators)
            
            elif service_name == "memory_system":
                # Check that memory system is using test paths
                test_indicators = [
                    str(self.test_data_paths["memory"]) in os.environ.get("TXTAI_INDEX_PATH", "")
                ]
                return all(test_indicators)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying test isolation for {service_name}: {e}")
            return False
    
    def _check_service_dependencies(self, service_name: str) -> bool:
        """Check if service dependencies are met."""
        try:
            config = self.service_configs[service_name]
            
            # Check if working directory exists
            if not Path(config.working_directory).exists():
                return False
            
            # Check if Python executable exists
            if service_name == "crewai_server":
                # Check if required modules are available
                required_modules = ["flask", "crewai", "gopiai.crewai"]
                return self._check_python_modules(sys.executable, required_modules)
            
            elif service_name == "ui_app":
                # Check if required modules are available
                required_modules = ["PySide6", "gopiai.ui"]
                return self._check_python_modules(sys.executable, required_modules)
            
            elif service_name == "memory_system":
                # Check if required modules are available
                required_modules = ["txtai", "numpy"]
                return self._check_python_modules(sys.executable, required_modules)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking dependencies for {service_name}: {e}")
            return False
    
    def _check_python_modules(self, python_exe: Path, modules: List[str]) -> bool:
        """Check if required Python modules are available."""
        try:
            for module in modules:
                result = subprocess.run(
                    [str(python_exe), "-c", f"import {module}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    self.logger.warning(f"Module {module} not available in {python_exe}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking Python modules: {e}")
            return False
    
    def wait_for_all_services_healthy(self, timeout: int = 60) -> bool:
        """Wait for all services to become healthy."""
        self.logger.info(f"Waiting for all services to become healthy (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            health_report = self.comprehensive_health_check()
            
            all_healthy = True
            unhealthy_services = []
            
            for service_name, health_info in health_report.items():
                if not health_info["healthy"]:
                    all_healthy = False
                    unhealthy_services.append(service_name)
            
            if all_healthy:
                self.logger.info("All services are healthy")
                return True
            
            self.logger.debug(f"Waiting for services to become healthy: {unhealthy_services}")
            time.sleep(2)
        
        self.logger.error("Timeout waiting for services to become healthy")
        return False
    
    def validate_test_readiness(self) -> Dict[str, Any]:
        """Validate that all services are ready for testing."""
        self.logger.info("Validating test readiness...")
        
        validation_report = {
            "ready": False,
            "test_isolation": False,
            "services_healthy": False,
            "dependencies_met": False,
            "issues": [],
            "recommendations": []
        }
        
        # Check test isolation
        if not self.verify_test_isolation():
            validation_report["issues"].append("Test isolation not properly configured")
            validation_report["recommendations"].append("Run setup_test_isolation() before starting tests")
        else:
            validation_report["test_isolation"] = True
        
        # Check service health
        health_report = self.comprehensive_health_check()
        all_healthy = True
        all_dependencies_met = True
        
        for service_name, health_info in health_report.items():
            if not health_info["healthy"]:
                all_healthy = False
                validation_report["issues"].append(f"Service {service_name} is not healthy")
                validation_report["recommendations"].append(f"Check logs for {service_name} and restart if needed")
            
            if not health_info.get("dependencies_met", False):
                all_dependencies_met = False
                validation_report["issues"].append(f"Dependencies not met for {service_name}")
                validation_report["recommendations"].append(f"Install required dependencies for {service_name}")
            
            if not health_info.get("test_isolation_verified", False):
                validation_report["issues"].append(f"Test isolation not verified for {service_name}")
                validation_report["recommendations"].append(f"Verify test environment configuration for {service_name}")
        
        validation_report["services_healthy"] = all_healthy
        validation_report["dependencies_met"] = all_dependencies_met
        
        # Overall readiness
        validation_report["ready"] = (
            validation_report["test_isolation"] and
            validation_report["services_healthy"] and
            validation_report["dependencies_met"]
        )
        
        if validation_report["ready"]:
            self.logger.info("All systems ready for testing")
        else:
            self.logger.warning(f"System not ready for testing. Issues: {len(validation_report['issues'])}")
        
        return validation_report
    
    def start_all_services(self) -> bool:
        """Start all configured services."""
        self.logger.info("Starting all services...")
        
        success = True
        for service_name in self.service_configs:
            if not self.start_service(service_name):
                success = False
        
        if success:
            self.logger.info("All services started successfully")
        else:
            self.logger.error("Some services failed to start")
        
        return success
    
    def stop_all_services(self) -> bool:
        """Stop all running services."""
        self.logger.info("Stopping all services...")
        
        success = True
        for service_name in list(self.services.keys()):
            if not self.stop_service(service_name):
                success = False
        
        if success:
            self.logger.info("All services stopped successfully")
        else:
            self.logger.error("Some services failed to stop cleanly")
        
        return success
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
        self.logger.info(f"Restarting service: {service_name}")
        
        if not self.stop_service(service_name):
            return False
        
        # Wait a moment before restarting
        time.sleep(2)
        
        return self.start_service(service_name)
    
    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get detailed information about a service."""
        return self.services.get(service_name)
    
    def list_services(self) -> Dict[str, ServiceInfo]:
        """List all services and their status."""
        return self.services.copy()
    
    def setup_test_isolation(self):
        """Set up comprehensive test data isolation."""
        if self._test_isolation_setup:
            return
            
        self.logger.info("Setting up test data isolation...")
        
        # Backup current environment variables that we'll modify
        self._backup_env_vars()
        
        # Create test-specific directories with proper permissions
        for name, path in self.test_data_paths.items():
            path.mkdir(parents=True, exist_ok=True)
            # Ensure test directories are writable
            os.chmod(path, 0o755)
            self.logger.debug(f"Created test directory: {path}")
        
        # Set environment variables for test isolation
        test_env_vars = {
            
            "GOPIAI_TEST_MODE": "true",
            "GOPIAI_CONVERSATIONS_DIR": str(self.test_data_paths["conversations"]),
            "GOPIAI_MEMORY_DIR": str(self.test_data_paths["memory"]),
            "GOPIAI_LOGS_DIR": str(self.test_data_paths["logs"]),
            "GOPIAI_CACHE_DIR": str(self.test_data_paths["cache"]),
            "GOPIAI_CONFIG_DIR": str(self.test_data_paths["config"]),
            # Prevent production data access
            "GOPIAI_PRODUCTION_MODE": "false",
            "CREWAI_TEST_MODE": "true",
            "TXTAI_TEST_MODE": "true",
            "FLASK_ENV": "testing",
            # Use test database/memory
            "DATABASE_URL": f"sqlite:///{self.test_data_paths['memory']}/test.db",
            "TXTAI_INDEX_PATH": str(self.test_data_paths["memory"] / "txtai_test_index"),
            # Test-specific API settings
            "USE_MOCK_RESPONSES": "true",
            "ENABLE_EXTERNAL_APIS": "false",
            "CREWAI_PORT": "5051",
            "MEMORY_PORT": "8000",
            # UI test settings
            "QT_QPA_PLATFORM": "offscreen",
            "DISPLAY": ":99"
        }
        
        for key, value in test_env_vars.items():
            os.environ[key] = value
        
        # Create test configuration files
        self._create_test_configs()
        
        # Initialize test databases and indexes
        self._initialize_test_data_structures()
        
        self._test_isolation_setup = True
        self.logger.info("Test data isolation configured successfully")
    
    def _backup_env_vars(self):
        """Backup environment variables that will be modified."""
        self._env_backup = {}
        vars_to_backup = [
            "GOPIAI_TEST_MODE", "GOPIAI_CONVERSATIONS_DIR",
            "GOPIAI_MEMORY_DIR", "GOPIAI_LOGS_DIR", "GOPIAI_CACHE_DIR",
            "GOPIAI_CONFIG_DIR", "CREWAI_TEST_MODE", "TXTAI_TEST_MODE",
            "DATABASE_URL", "TXTAI_INDEX_PATH", "QT_QPA_PLATFORM", "DISPLAY"
        ]
        
        for var in vars_to_backup:
            if var in os.environ:
                self._env_backup[var] = os.environ[var]
    
    def _initialize_test_data_structures(self):
        """Initialize test-specific data structures."""
        try:
            # Create test database
            db_path = self.test_data_paths["memory"] / "test.db"
            if not db_path.exists():
                # Create empty SQLite database
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)")
                conn.commit()
                conn.close()
                self.logger.debug(f"Created test database: {db_path}")
            
            # Create txtai test index directory
            index_path = self.test_data_paths["memory"] / "txtai_test_index"
            index_path.mkdir(exist_ok=True)
            self.logger.debug(f"Created txtai test index directory: {index_path}")
            
            # Create test conversation files
            conversations_path = self.test_data_paths["conversations"]
            test_conversation = conversations_path / "test_conversation.json"
            if not test_conversation.exists():
                import json
                test_data = {
                    "conversation_id": "test_001",
                    "messages": [],
                    "created_at": time.time(),
                    "test_mode": True
                }
                with open(test_conversation, 'w') as f:
                    json.dump(test_data, f, indent=2)
                self.logger.debug(f"Created test conversation file: {test_conversation}")
                
        except Exception as e:
            self.logger.error(f"Error initializing test data structures: {e}")
    
    def _create_test_configs(self):
        """Create test-specific configuration files."""
        config_dir = self.test_data_paths["config"]
        
        # Create test .env file
        test_env_content = """
# Test Environment Configuration
GOPIAI_TEST_MODE=true
CREWAI_TEST_MODE=true

# Test API Keys (mock values)
OPENAI_API_KEY=test_openai_key
ANTHROPIC_API_KEY=test_anthropic_key
GOOGLE_API_KEY=test_google_key

# Test Database
DATABASE_URL=sqlite:///test_memory/test.db

# Test Ports
CREWAI_PORT=5051
MEMORY_PORT=8000

# Disable external services in test mode
ENABLE_EXTERNAL_APIS=false
USE_MOCK_RESPONSES=true
"""
        
        test_env_path = config_dir / ".env.test"
        with open(test_env_path, 'w') as f:
            f.write(test_env_content.strip())
        
        self.logger.debug(f"Created test environment file: {test_env_path}")
    
    def verify_test_isolation(self) -> bool:
        """Verify that test isolation is properly configured."""
        self.logger.info("Verifying test isolation...")
        
        # Check environment variables
        required_env_vars = [
            "GOPIAI_TEST_MODE", 
            "GOPIAI_CONVERSATIONS_DIR",
            "GOPIAI_MEMORY_DIR"
        ]
        
        for var in required_env_vars:
            if not os.environ.get(var):
                self.logger.error(f"Environment variable {var} not set")
                return False
        
        # Check test directories exist
        for name, path in self.test_data_paths.items():
            if not path.exists():
                self.logger.error(f"Test directory {name} does not exist: {path}")
                return False
        
        # Verify we're not using production paths
        production_paths = [
            self.root_path / "conversations",
            self.root_path / "memory",
            Path.home() / ".gopiai"
        ]
        
        for prod_path in production_paths:
            if str(prod_path) in os.environ.get("GOPIAI_CONVERSATIONS_DIR", ""):
                self.logger.error(f"Test isolation failed: using production path {prod_path}")
                return False
        
        self.logger.info("Test isolation verification passed")
        return True
    
    def cleanup_test_data(self):
        """Clean up test data after tests complete."""
        self.logger.info("Cleaning up test data...")
        
        import shutil
        
        # Remove test directories
        for name, path in self.test_data_paths.items():
            if path.exists():
                try:
                    shutil.rmtree(path)
                    self.logger.debug(f"Removed test directory {name}: {path}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove test directory {name} at {path}: {e}")
        
        # Restore backed up environment variables
        if hasattr(self, '_env_backup'):
            for var, value in self._env_backup.items():
                os.environ[var] = value
            self.logger.debug("Restored backed up environment variables")
        
        # Clean up test-specific environment variables
        test_env_vars = [
            "GOPIAI_TEST_MODE", "GOPIAI_CONVERSATIONS_DIR",
            "GOPIAI_MEMORY_DIR", "GOPIAI_LOGS_DIR", "GOPIAI_CACHE_DIR",
            "GOPIAI_CONFIG_DIR", "CREWAI_TEST_MODE",
            "DATABASE_URL", "USE_MOCK_RESPONSES",
            "ENABLE_EXTERNAL_APIS", "FLASK_ENV"
        ]
        
        for var in test_env_vars:
            if var in os.environ and not hasattr(self, '_env_backup') or var not in self._env_backup:
                del os.environ[var]
        
        self._test_isolation_setup = False
        self.logger.info("Test data cleanup completed")
    
    def _register_shutdown_handlers(self):
        """Register handlers to clean up services on shutdown."""
        def cleanup_handler(signum, frame):
            self.logger.info("Received shutdown signal, cleaning up services...")
            self.stop_all_services()
            self.cleanup_test_data()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        self._shutdown_handlers_registered = True
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_test_isolation()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all_services()
        self.cleanup_test_data()


# Convenience functions for common operations
def start_crewai_server() -> bool:
    """Start only the CrewAI server."""
    manager = ServiceManager()
    return manager.start_service("crewai_server")


def stop_crewai_server() -> bool:
    """Stop the CrewAI server."""
    manager = ServiceManager()
    return manager.stop_service("crewai_server")


def check_crewai_health() -> bool:
    """Check if CrewAI server is healthy."""
    manager = ServiceManager()
    return manager.check_service_health("crewai_server")


# Test utilities
class TestServiceManager:
    """Simplified service manager for testing."""
    
    def __init__(self):
        self.manager = ServiceManager()
    
    def __enter__(self):
        self.manager.setup_test_isolation()
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.stop_all_services()
        self.manager.cleanup_test_data()


if __name__ == "__main__":
    # Command-line interface for service management
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI Service Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "health"])
    parser.add_argument("--service", help="Specific service name")
    parser.add_argument("--all", action="store_true", help="Apply to all services")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.action == "start":
        if args.all:
            success = manager.start_all_services()
        elif args.service:
            success = manager.start_service(args.service)
        else:
            print("Specify --service or --all")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        if args.all:
            success = manager.stop_all_services()
        elif args.service:
            success = manager.stop_service(args.service)
        else:
            print("Specify --service or --all")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "restart":
        if args.service:
            success = manager.restart_service(args.service)
        else:
            print("Specify --service for restart")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        services = manager.list_services()
        if not services:
            print("No services running")
        else:
            for name, info in services.items():
                print(f"{name}: {info.status.value} (PID: {info.pid})")
    
    elif args.action == "health":
        if args.service:
            healthy = manager.check_service_health(args.service)
            print(f"{args.service}: {'healthy' if healthy else 'unhealthy'}")
            sys.exit(0 if healthy else 1)
        else:
            all_healthy = True
            for service_name in manager.service_configs:
                healthy = manager.check_service_health(service_name)
                print(f"{service_name}: {'healthy' if healthy else 'unhealthy'}")
                if not healthy:
                    all_healthy = False
            sys.exit(0 if all_healthy else 1)