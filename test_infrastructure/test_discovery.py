#!/usr/bin/env python3
"""
Test Discovery System for GopiAI Testing Infrastructure

This module discovers and categorizes tests across all GopiAI modules,
providing a unified interface for test execution and reporting.
"""

import os
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import importlib.util
import sys


class TestCategory(Enum):
    """Categories of tests that can be discovered."""
    UNIT = "unit"
    INTEGRATION = "integration"
    UI = "ui"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"





@dataclass
class TestModule:
    """Represents a discovered test module."""
    file_path: str
    module_name: str
    category: TestCategory
    test_functions: List[str]
    dependencies: List[str]
    markers: List[str]
    estimated_duration: float = 0.0
    requires_services: List[str] = None


@dataclass
class TestSuite:
    """Represents a collection of test modules."""
    name: str
    category: TestCategory
    modules: List[TestModule]
    setup_requirements: List[str]
    total_tests: int = 0
    estimated_duration: float = 0.0


class TestDiscovery:
    """Discovers and categorizes tests across GopiAI modules."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.test_modules: List[TestModule] = []
        self.test_suites: List[TestSuite] = []
        self.logger = logging.getLogger(__name__)
        
        
        
        # Test category patterns
        self.category_patterns = {
            TestCategory.UNIT: ["test_*.py", "*_test.py"],
            TestCategory.INTEGRATION: ["test_*integration*.py", "*integration*_test.py"],
            TestCategory.UI: ["test_*ui*.py", "*ui*_test.py"],
            TestCategory.E2E: ["test_*e2e*.py", "*e2e*_test.py", "test_*end_to_end*.py"],
            TestCategory.PERFORMANCE: ["test_*performance*.py", "*performance*_test.py"],
            TestCategory.SECURITY: ["test_*security*.py", "*security*_test.py"],
        }

    def discover_all_tests(self) -> List[TestModule]:
        """Discover all tests in the GopiAI modules."""
        self.test_modules = []
        
        # Discover tests in each GopiAI module
        gopiai_modules = [
            "GopiAI-Core",
            "GopiAI-UI", 
            "GopiAI-CrewAI",
            "GopiAI-Assets"
        ]
        
        for module in gopiai_modules:
            module_path = self.root_path / module
            if module_path.exists():
                self.logger.info(f"Discovering tests in module: {module}")
                self._discover_module_tests(module_path, module)
        
        # Also discover tests in test_infrastructure
        infra_path = self.root_path / "test_infrastructure"
        if infra_path.exists():
            self.logger.info("Discovering tests in test_infrastructure")
            self._discover_module_tests(infra_path, "test_infrastructure")
        
        # Create test suites
        self._create_test_suites()
        
        return self.test_modules

    def _discover_module_tests(self, module_path: Path, module_name: str):
        """Discover tests in a specific GopiAI module."""
        tests_path = module_path / "tests"
        if not tests_path.exists():
            self.logger.warning(f"No tests directory found in {module_name}")
            return
        
        for py_file in tests_path.rglob("test_*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                test_module = self._analyze_test_file(py_file, module_name)
                if test_module:
                    self.test_modules.append(test_module)
            except Exception as e:
                self.logger.error(f"Error analyzing test file {py_file}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a test file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".pytest_cache",
            "conftest.py",
            "__init__.py"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_test_file(self, file_path: Path, module_name: str) -> Optional[TestModule]:
        """Analyze a test file to extract information."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Could not read {file_path}: {e}")
            return None

        # Parse AST to find test functions
        test_functions = []
        dependencies = []
        markers = []
        
        try:
            tree = ast.parse(content)
            
            # Find test functions and imports
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_functions.append(node.name)
                    
                    # Check for pytest markers
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['mark', 'fixture']:
                                markers.append(f"pytest.{decorator.func.attr}")
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
        
        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
            return None
        
        # Determine test category
        category = self._determine_test_category(file_path)
        
        
        
        # Determine service requirements
        requires_services = self._determine_service_requirements(content, dependencies)
        
        return TestModule(
            file_path=str(file_path.relative_to(self.root_path)),
            module_name=module_name,
            category=category,
            
            test_functions=test_functions,
            dependencies=dependencies,
            markers=markers,
            requires_services=requires_services
        )

    def _determine_test_category(self, file_path: Path) -> TestCategory:
        """Determine the category of a test file based on its path and name."""
        file_str = str(file_path).lower()
        
        # Check for specific category patterns
        if any(pattern in file_str for pattern in ["ui", "widget", "gui"]):
            return TestCategory.UI
        elif any(pattern in file_str for pattern in ["integration", "api", "endpoint"]):
            return TestCategory.INTEGRATION
        elif any(pattern in file_str for pattern in ["e2e", "end_to_end", "scenario"]):
            return TestCategory.E2E
        elif any(pattern in file_str for pattern in ["performance", "benchmark", "load"]):
            return TestCategory.PERFORMANCE
        elif any(pattern in file_str for pattern in ["security", "auth", "permission"]):
            return TestCategory.SECURITY
        else:
            return TestCategory.UNIT

    def _determine_service_requirements(self, content: str, dependencies: List[str]) -> List[str]:
        """Determine what services a test requires based on its content."""
        services = []
        
        # Check for CrewAI server requirements
        if any(dep in content for dep in ["crewai", "requests", "http", "api"]):
            services.append("crewai_server")
        
        # Check for UI requirements
        if any(dep in content for dep in ["PySide6", "QTest", "pytest-qt", "QApplication"]):
            services.append("display")
        
        # Check for memory system requirements
        if any(dep in content for dep in ["txtai", "memory", "vector", "embedding"]):
            services.append("memory_system")
        
        return services

    def _create_test_suites(self):
        """Create test suites by grouping test modules."""
        self.test_suites = []
        
        # Group by category
        suite_groups = {}
        for module in self.test_modules:
            key = module.category
            if key not in suite_groups:
                suite_groups[key] = []
            suite_groups[key].append(module)
        
        # Create test suites
        for category, modules in suite_groups.items():
            suite_name = f"{category.value}_{environment.value}"
            
            # Determine setup requirements
            setup_requirements = ["crewai_server", "memory_system"] # Assuming these are always required
            
            # Add service requirements
            for module in modules:
                if module.requires_services:
                    setup_requirements.extend(module.requires_services)
            
            setup_requirements = list(set(setup_requirements))  # Remove duplicates
            
            total_tests = sum(len(module.test_functions) for module in modules)
            
            suite = TestSuite(
                name=suite_name,
                category=category,
                
                modules=modules,
                setup_requirements=setup_requirements,
                total_tests=total_tests
            )
            
            self.test_suites.append(suite)

    def get_tests_by_category(self, category: TestCategory) -> List[TestModule]:
        """Get all test modules of a specific category."""
        return [module for module in self.test_modules if module.category == category]

    

    def get_test_suite(self, category: TestCategory) -> Optional[TestSuite]:
        """Get a specific test suite."""
        for suite in self.test_suites:
            if suite.category == category:
                return suite
        return None

    def generate_discovery_report(self, output_file: str = "test_discovery_report.json"):
        """Generate a JSON report of discovered tests."""
        report = {
            "summary": {
                "total_modules": len(self.test_modules),
                "total_suites": len(self.test_suites),
                "total_tests": sum(len(module.test_functions) for module in self.test_modules),
                "by_category": {},
                "by_module": {}
            },
            "test_modules": [],
            "test_suites": []
        }
        
        # Convert test modules to serializable format
        for module in self.test_modules:
            module_dict = asdict(module)
            module_dict["category"] = module.category.value
            module_dict["environment"] = module.environment.value
            report["test_modules"].append(module_dict)
        
        # Convert test suites to serializable format
        for suite in self.test_suites:
            suite_dict = asdict(suite)
            suite_dict["category"] = suite.category.value
            
            # Convert modules to just file paths to avoid duplication
            suite_dict["modules"] = [module.file_path for module in suite.modules]
            report["test_suites"].append(suite_dict)
        
        # Calculate summary statistics
        for module in self.test_modules:
            # By category
            category = module.category.value
            report["summary"]["by_category"][category] = report["summary"]["by_category"].get(category, 0) + 1
            
            
            
            # By module
            module_name = module.module_name
            report["summary"]["by_module"][module_name] = report["summary"]["by_module"].get(module_name, 0) + 1
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test discovery report written to {output_file}")
        return report


def main():
    """Main function to run test discovery."""
    logging.basicConfig(level=logging.INFO)
    
    discovery = TestDiscovery()
    test_modules = discovery.discover_all_tests()
    
    print(f"Discovered {len(test_modules)} test modules in GopiAI codebase")
    
    # Generate report
    report = discovery.generate_discovery_report()
    
    # Print summary
    print("\nSummary by category:")
    for category, count in report["summary"]["by_category"].items():
        print(f"  {category}: {count}")
    
    
    
    print("\nSummary by module:")
    for module, count in report["summary"]["by_module"].items():
        print(f"  {module}: {count}")
    
    print(f"\nTotal test suites: {len(discovery.test_suites)}")
    for suite in discovery.test_suites:
        print(f"  {suite.name}: {suite.total_tests} tests")


if __name__ == "__main__":
    main()