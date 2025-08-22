#!/usr/bin/env python3
"""
Test Configuration for GopiAI Testing Infrastructure

Centralized configuration for all testing environments and modules.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import logging


class TestEnvironment(Enum):
    """Available test environments."""
    VENV = ".venv"


class TestCategory(Enum):
    """Test categories."""
    UNIT = "unit"
    INTEGRATION = "integration"
    UI = "ui"
    API = "api"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class ModuleTestConfig:
    """Configuration for a specific GopiAI module."""
    name: str
    path: Path
    environment: TestEnvironment
    test_categories: List[TestCategory]
    pytest_ini_path: Path
    coverage_threshold: float
    requires_display: bool = False
    requires_server: bool = False
    timeout_seconds: int = 300


@dataclass
class TestInfrastructureConfig:
    """Main configuration for the testing infrastructure."""
    root_path: Path
    modules: Dict[str, ModuleTestConfig]
    parallel_execution: bool = True
    max_workers: int = 4
    default_timeout: int = 300
    coverage_threshold: float = 70.0
    report_formats: List[str] = None
    
    def __post_init__(self):
        if self.report_formats is None:
            self.report_formats = ["html", "term", "json"]


class TestConfigManager:
    """Manages test configuration for all GopiAI modules."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.config = self._create_default_config()
    
    def _create_default_config(self) -> TestInfrastructureConfig:
        """Create default configuration for all modules."""
        modules = {}
        
        # GopiAI-UI configuration
        ui_path = self.root_path / "GopiAI-UI"
        if ui_path.exists():
            modules["gopiai-ui"] = ModuleTestConfig(
                name="gopiai-ui",
                path=ui_path,
                environment=TestEnvironment.VENV,
                test_categories=[
                    TestCategory.UNIT,
                    TestCategory.INTEGRATION,
                    TestCategory.UI
                ],
                pytest_ini_path=ui_path / "pytest.ini",
                coverage_threshold=70.0,
                requires_display=True,
                requires_server=True,
                timeout_seconds=600  # UI tests may take longer
            )
        
        # GopiAI-CrewAI configuration
        crewai_path = self.root_path / "GopiAI-CrewAI"
        if crewai_path.exists():
            modules["gopiai-crewai"] = ModuleTestConfig(
                name="gopiai-crewai",
                path=crewai_path,
                environment=TestEnvironment.VENV,
                test_categories=[
                    TestCategory.UNIT,
                    TestCategory.INTEGRATION,
                    TestCategory.API
                ],
                pytest_ini_path=crewai_path / "pytest.ini",
                coverage_threshold=60.0,
                requires_server=True,
                timeout_seconds=300
            )
        
        # GopiAI-Assets configuration
        assets_path = self.root_path / "GopiAI-Assets"
        if assets_path.exists():
            modules["gopiai-assets"] = ModuleTestConfig(
                name="gopiai-assets",
                path=assets_path,
                environment=TestEnvironment.VENV,
                test_categories=[TestCategory.UNIT],
                pytest_ini_path=assets_path / "pytest.ini",
                coverage_threshold=80.0,
                timeout_seconds=120
            )
        
        return TestInfrastructureConfig(
            root_path=self.root_path,
            modules=modules,
            parallel_execution=True,
            max_workers=min(4, len(modules)),
            default_timeout=300,
            coverage_threshold=70.0
        )
    
    def get_module_config(self, module_name: str) -> Optional[ModuleTestConfig]:
        """Get configuration for a specific module."""
        return self.config.modules.get(module_name)
    
    def get_modules_by_environment(self, environment: TestEnvironment) -> List[ModuleTestConfig]:
        """Get all modules that use a specific environment."""
        return [
            module for module in self.config.modules.values()
            if module.environment == environment
        ]
    
    def get_modules_by_category(self, category: TestCategory) -> List[ModuleTestConfig]:
        """Get all modules that support a specific test category."""
        return [
            module for module in self.config.modules.values()
            if category in module.test_categories
        ]
    
    def validate_environment(self, environment: TestEnvironment) -> bool:
        """Validate that a test environment is properly set up."""
        env_path = self.root_path / environment.value
        
        if not env_path.exists():
            return False
        
        # Check for Python executable
        python_exe = env_path / "Scripts" / "python.exe"  # Windows
        if not python_exe.exists():
            python_exe = env_path / "bin" / "python"  # Unix
        
        return python_exe.exists()
    
    def get_environment_python(self, environment: TestEnvironment) -> Optional[Path]:
        """Get the Python executable path for an environment."""
        env_path = self.root_path / environment.value
        
        # Windows
        python_exe = env_path / "Scripts" / "python.exe"
        if python_exe.exists():
            return python_exe.absolute()
        
        # Unix
        python_exe = env_path / "bin" / "python"
        if python_exe.exists():
            return python_exe.absolute()
        
        return None
    
    def create_test_command(self, module_name: str, category: TestCategory = None, 
                          specific_test: str = None) -> List[str]:
        """Create a pytest command for a specific module and category."""
        module_config = self.get_module_config(module_name)
        if not module_config:
            raise ValueError(f"Module {module_name} not found in configuration")
        
        python_exe = self.get_environment_python(module_config.environment)
        if not python_exe:
            raise RuntimeError(f"Python executable not found for environment {module_config.environment.value}")
        
        cmd = [str(python_exe), "-m", "pytest"]
        
        # Add configuration file
        if module_config.pytest_ini_path.exists():
            cmd.extend(["-c", str(module_config.pytest_ini_path)])
        
        # Add test path
        if specific_test:
            cmd.append(str(module_config.path / "tests" / specific_test))
        elif category:
            cmd.append(str(module_config.path / "tests" / category.value))
        else:
            cmd.append(str(module_config.path / "tests"))
        
        # Add category marker if specified
        if category:
            cmd.extend(["-m", category.value])
        
        return cmd
    
    def export_config(self, output_file: str = "test_config.json"):
        """Export configuration to JSON file."""
        import json
        
        config_dict = {
            "root_path": str(self.config.root_path),
            "parallel_execution": self.config.parallel_execution,
            "max_workers": self.config.max_workers,
            "default_timeout": self.config.default_timeout,
            "coverage_threshold": self.config.coverage_threshold,
            "report_formats": self.config.report_formats,
            "modules": {}
        }
        
        for name, module in self.config.modules.items():
            config_dict["modules"][name] = {
                "name": module.name,
                "path": str(module.path),
                "environment": module.environment.value,
                "test_categories": [cat.value for cat in module.test_categories],
                "pytest_ini_path": str(module.pytest_ini_path),
                "coverage_threshold": module.coverage_threshold,
                "requires_display": module.requires_display,
                "requires_server": module.requires_server,
                "timeout_seconds": module.timeout_seconds
            }
        
        with open(output_file, 'w') as f:
            json.dump(config_dict, f, indent=2)


# Global configuration instance
config_manager = TestConfigManager()

# Enhanced problem discovery integration
class ProblemAwareTestConfig:
    """Test configuration that integrates with problem discovery."""
    
    def __init__(self, config_manager: TestConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def get_known_issues_markers(self) -> Dict[str, List[str]]:
        """Get pytest markers for known issues."""
        try:
            from problem_discovery import ProblemDiscovery
            discovery = ProblemDiscovery()
            problems = discovery.discover_all_problems()
            
            # Group problems by file for marker generation
            markers = {}
            for problem in problems:
                if problem.test_marker:
                    file_key = problem.file_path.replace('/', '_').replace('\\', '_')
                    if file_key not in markers:
                        markers[file_key] = []
                    markers[file_key].append(problem.test_marker)
            
            return markers
        except Exception as e:
            self.logger.error(f"Failed to get known issues markers: {e}")
            return {}
    
    def should_skip_test(self, test_path: str, test_name: str) -> bool:
        """Determine if a test should be skipped based on known issues."""
        # This can be extended to implement intelligent test skipping
        # based on problem discovery results
        return False
    
    def get_test_timeout(self, test_category: str) -> int:
        """Get timeout for specific test category."""
        config = self.config_manager.config
        if not config:
            return 30
        
        timeouts = {
            "unit": config.default_timeout,
            "integration": config.default_timeout * 2,
            "ui": config.default_timeout * 3,
            "e2e": config.default_timeout * 5,
            "performance": config.default_timeout * 10,
            "security": config.default_timeout * 2
        }
        
        return timeouts.get(test_category, config.default_timeout)


# Enhanced configuration with problem awareness
problem_aware_config = ProblemAwareTestConfig(config_manager)