#!/usr/bin/env python3
"""
Automated Test Documentation Generator

This module automatically generates comprehensive documentation for the GopiAI testing system
by analyzing test files, extracting metadata, and creating formatted documentation.
"""
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TestFunction:
    """Represents a single test function."""
    name: str
    docstring: Optional[str]
    file_path: str
    line_number: int
    markers: List[str]
    parameters: List[str]
    fixtures: List[str]
    category: str
    complexity: str
    estimated_runtime: str


@dataclass
class TestClass:
    """Represents a test class."""
    name: str
    docstring: Optional[str]
    file_path: str
    line_number: int
    methods: List[TestFunction]
    fixtures: List[str]
    category: str


@dataclass
class TestModule:
    """Represents a test module/file."""
    name: str
    file_path: str
    docstring: Optional[str]
    classes: List[TestClass]
    functions: List[TestFunction]
    fixtures: List[str]
    imports: List[str]
    category: str
    total_tests: int
    estimated_runtime: str


@dataclass
class TestSuite:
    """Represents a complete test suite."""
    name: str
    modules: List[TestModule]
    total_tests: int
    total_fixtures: int
    categories: Dict[str, int]
    estimated_runtime: str
    coverage_info: Optional[Dict[str, Any]] = None


class TestDocumentationGenerator:
    """Generates comprehensive documentation for test suites."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.test_patterns = [
            "test_*.py",
            "*_test.py",
            "tests.py"
        ]
        self.category_mapping = {
            "unit": ["unit", "test_unit"],
            "integration": ["integration", "test_integration"],
            "ui": ["ui", "test_ui", "gui"],
            "e2e": ["e2e", "end_to_end", "test_e2e"],
            "performance": ["performance", "benchmark", "test_performance"],
            "security": ["security", "test_security"]
        }
        
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in the project."""
        test_files = []
        
        # Only look in specific project directories, not virtual environments
        project_dirs = [
            "GopiAI-Core/tests",
            "GopiAI-UI/tests", 
            "GopiAI-CrewAI/tests",
            "GopiAI-Assets/tests",
            "tests",
            "test_infrastructure"
        ]
        
        for project_dir in project_dirs:
            project_path = self.root_path / project_dir
            if project_path.exists():
                for pattern in self.test_patterns:
                    test_files.extend(project_path.rglob(pattern))
        
        # Filter out __pycache__ and other unwanted directories
        filtered_files = []
        for file_path in test_files:
            path_str = str(file_path)
            if ("__pycache__" not in path_str and 
                file_path.is_file() and
                not any(env in path_str for env in ["_env", "site-packages", "node_modules"])):
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    def parse_test_file(self, file_path: Path) -> TestModule:
        """Parse a single test file and extract test information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_docstring = ast.get_docstring(tree)
            classes = []
            functions = []
            fixtures = []
            imports = []
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Extract classes and functions
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    test_class = self._parse_test_class(node, file_path)
                    classes.append(test_class)
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_func = self._parse_test_function(node, file_path)
                        functions.append(test_func)
                    elif self._is_fixture(node):
                        fixtures.append(node.name)
            
            category = self._determine_category(file_path)
            total_tests = len(functions) + sum(len(cls.methods) for cls in classes)
            estimated_runtime = self._estimate_runtime(functions, classes)
            
            return TestModule(
                name=file_path.stem,
                file_path=str(file_path),
                docstring=module_docstring,
                classes=classes,
                functions=functions,
                fixtures=fixtures,
                imports=imports,
                category=category,
                total_tests=total_tests,
                estimated_runtime=estimated_runtime
            )
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return TestModule(
                name=file_path.stem,
                file_path=str(file_path),
                docstring=f"Error parsing file: {e}",
                classes=[],
                functions=[],
                fixtures=[],
                imports=[],
                category="unknown",
                total_tests=0,
                estimated_runtime="unknown"
            )
    
    def _parse_test_class(self, node: ast.ClassDef, file_path: Path) -> TestClass:
        """Parse a test class and extract its methods."""
        docstring = ast.get_docstring(node)
        methods = []
        fixtures = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith('test_'):
                    test_method = self._parse_test_function(item, file_path)
                    methods.append(test_method)
                elif self._is_fixture(item):
                    fixtures.append(item.name)
        
        category = self._determine_category(file_path)
        
        return TestClass(
            name=node.name,
            docstring=docstring,
            file_path=str(file_path),
            line_number=node.lineno,
            methods=methods,
            fixtures=fixtures,
            category=category
        )
    
    def _parse_test_function(self, node: ast.FunctionDef, file_path: Path) -> TestFunction:
        """Parse a test function and extract its metadata."""
        docstring = ast.get_docstring(node)
        markers = self._extract_markers(node)
        parameters = [arg.arg for arg in node.args.args if arg.arg != 'self']
        fixtures = self._extract_fixtures(node)
        category = self._determine_category(file_path)
        complexity = self._estimate_complexity(node)
        estimated_runtime = self._estimate_function_runtime(node, markers)
        
        return TestFunction(
            name=node.name,
            docstring=docstring,
            file_path=str(file_path),
            line_number=node.lineno,
            markers=markers,
            parameters=parameters,
            fixtures=fixtures,
            category=category,
            complexity=complexity,
            estimated_runtime=estimated_runtime
        )
    
    def _extract_markers(self, node: ast.FunctionDef) -> List[str]:
        """Extract pytest markers from a function."""
        markers = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if isinstance(decorator.value, ast.Name) and decorator.value.id == 'pytest':
                    markers.append(decorator.attr)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == 'pytest':
                        markers.append(decorator.func.attr)
        
        return markers
    
    def _extract_fixtures(self, node: ast.FunctionDef) -> List[str]:
        """Extract fixture dependencies from function parameters."""
        fixtures = []
        
        # Common fixture names
        common_fixtures = [
            'qtbot', 'qapp', 'mock', 'monkeypatch', 'tmp_path', 'capsys',
            'api_client', 'test_database', 'mock_ai_service', 'service_manager'
        ]
        
        for arg in node.args.args:
            if arg.arg in common_fixtures or arg.arg.endswith('_fixture'):
                fixtures.append(arg.arg)
        
        return fixtures
    
    def _is_fixture(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a pytest fixture."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if isinstance(decorator.value, ast.Name) and decorator.value.id == 'pytest':
                    if decorator.attr == 'fixture':
                        return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == 'pytest':
                        if decorator.func.attr == 'fixture':
                            return True
        return False
    
    def _determine_category(self, file_path: Path) -> str:
        """Determine test category based on file path."""
        path_str = str(file_path).lower()
        
        for category, keywords in self.category_mapping.items():
            if any(keyword in path_str for keyword in keywords):
                return category
        
        return "unit"  # Default category
    
    def _estimate_complexity(self, node: ast.FunctionDef) -> str:
        """Estimate test complexity based on AST analysis."""
        complexity_score = 0
        
        # Count control flow statements
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity_score += 1
            elif isinstance(child, ast.Call):
                complexity_score += 0.5
        
        if complexity_score < 3:
            return "simple"
        elif complexity_score < 8:
            return "medium"
        else:
            return "complex"
    
    def _estimate_function_runtime(self, node: ast.FunctionDef, markers: List[str]) -> str:
        """Estimate function runtime based on markers and content."""
        if 'slow' in markers or 'performance' in markers:
            return "slow (>30s)"
        elif 'integration' in markers or 'e2e' in markers:
            return "medium (5-30s)"
        else:
            return "fast (<5s)"
    
    def _estimate_runtime(self, functions: List[TestFunction], classes: List[TestClass]) -> str:
        """Estimate total runtime for a module."""
        total_functions = len(functions) + sum(len(cls.methods) for cls in classes)
        
        if total_functions == 0:
            return "0s"
        elif total_functions < 10:
            return "fast (<30s)"
        elif total_functions < 50:
            return "medium (30s-5m)"
        else:
            return "slow (>5m)"
    
    def generate_test_suite_documentation(self, output_path: str = "02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md") -> TestSuite:
        """Generate comprehensive test suite documentation."""
        test_files = self.discover_test_files()
        modules = []
        
        print(f"Discovered {len(test_files)} test files")
        
        for file_path in test_files:
            print(f"Parsing {file_path}")
            module = self.parse_test_file(file_path)
            modules.append(module)
        
        # Calculate suite statistics
        total_tests = sum(module.total_tests for module in modules)
        total_fixtures = sum(len(module.fixtures) for module in modules)
        
        categories = {}
        for module in modules:
            categories[module.category] = categories.get(module.category, 0) + module.total_tests
        
        estimated_runtime = self._estimate_suite_runtime(modules)
        
        test_suite = TestSuite(
            name="GopiAI Test Suite",
            modules=modules,
            total_tests=total_tests,
            total_fixtures=total_fixtures,
            categories=categories,
            estimated_runtime=estimated_runtime
        )
        
        # Generate documentation
        self._write_suite_documentation(test_suite, output_path)
        
        return test_suite
    
    def _estimate_suite_runtime(self, modules: List[TestModule]) -> str:
        """Estimate total suite runtime."""
        total_tests = sum(module.total_tests for module in modules)
        
        if total_tests < 100:
            return "fast (<10m)"
        elif total_tests < 500:
            return "medium (10-30m)"
        else:
            return "slow (>30m)"
    
    def _write_suite_documentation(self, test_suite: TestSuite, output_path: str):
        """Write comprehensive test suite documentation to file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_documentation_content(test_suite))
        
        print(f"Documentation generated: {output_path}")
    
    def _generate_documentation_content(self, test_suite: TestSuite) -> str:
        """Generate the complete documentation content."""
        content = []
        
        # Header
        content.append("# GopiAI Test Suite Documentation")
        content.append("")
        content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Overview
        content.append("## Overview")
        content.append("")
        content.append(f"This document provides comprehensive documentation for the {test_suite.name}.")
        content.append(f"The test suite contains **{test_suite.total_tests} tests** across **{len(test_suite.modules)} modules**.")
        content.append(f"Estimated total runtime: **{test_suite.estimated_runtime}**")
        content.append("")
        
        # Statistics
        content.append("## Test Statistics")
        content.append("")
        content.append("| Metric | Value |")
        content.append("|--------|-------|")
        content.append(f"| Total Tests | {test_suite.total_tests} |")
        content.append(f"| Total Modules | {len(test_suite.modules)} |")
        content.append(f"| Total Fixtures | {test_suite.total_fixtures} |")
        content.append(f"| Estimated Runtime | {test_suite.estimated_runtime} |")
        content.append("")
        
        # Category breakdown
        content.append("### Tests by Category")
        content.append("")
        content.append("| Category | Count | Percentage |")
        content.append("|----------|-------|------------|")
        
        for category, count in sorted(test_suite.categories.items()):
            percentage = (count / test_suite.total_tests * 100) if test_suite.total_tests > 0 else 0
            content.append(f"| {category.title()} | {count} | {percentage:.1f}% |")
        content.append("")
        
        # Module documentation
        content.append("## Test Modules")
        content.append("")
        
        for module in sorted(test_suite.modules, key=lambda m: m.category):
            content.extend(self._generate_module_documentation(module))
        
        # Fixtures documentation
        content.append("## Test Fixtures")
        content.append("")
        content.append("This section documents all available test fixtures.")
        content.append("")
        
        all_fixtures = set()
        for module in test_suite.modules:
            all_fixtures.update(module.fixtures)
        
        if all_fixtures:
            content.append("| Fixture Name | Module | Description |")
            content.append("|--------------|--------|-------------|")
            
            for fixture in sorted(all_fixtures):
                modules_with_fixture = [m.name for m in test_suite.modules if fixture in m.fixtures]
                content.append(f"| `{fixture}` | {', '.join(modules_with_fixture)} | Auto-detected fixture |")
        else:
            content.append("No fixtures detected.")
        
        content.append("")
        
        # Running tests
        content.append("## Running Tests")
        content.append("")
        content.append("### Run All Tests")
        content.append("```bash")
        content.append("python run_all_tests.py")
        content.append("```")
        content.append("")
        
        content.append("### Run by Category")
        for category in sorted(test_suite.categories.keys()):
            content.append(f"```bash")
            content.append(f"pytest -m {category}")
            content.append(f"```")
        content.append("")
        
        content.append("### Run Specific Modules")
        for module in test_suite.modules[:5]:  # Show first 5 as examples
            content.append(f"```bash")
            content.append(f"pytest {module.file_path}")
            content.append(f"```")
        content.append("")
        
        # Troubleshooting
        content.append("## Troubleshooting")
        content.append("")
        content.append("For common issues and solutions, see:")
        content.append("- [Test Troubleshooting Guide](TEST_TROUBLESHOOTING_GUIDE.md)")
        content.append("- [Testing System Guide](TESTING_SYSTEM_GUIDE.md)")
        content.append("- [Adding New Tests Guide](ADDING_NEW_TESTS_GUIDE.md)")
        content.append("")
        
        return "\n".join(content)
    
    def _generate_module_documentation(self, module: TestModule) -> List[str]:
        """Generate documentation for a single test module."""
        content = []
        
        content.append(f"### {module.name}")
        content.append("")
        content.append(f"**File:** `{module.file_path}`")
        content.append(f"**Category:** {module.category.title()}")
        content.append(f"**Tests:** {module.total_tests}")
        content.append(f"**Estimated Runtime:** {module.estimated_runtime}")
        content.append("")
        
        if module.docstring:
            content.append("**Description:**")
            content.append(module.docstring)
            content.append("")
        
        # Test functions
        if module.functions:
            content.append("#### Test Functions")
            content.append("")
            content.append("| Function | Complexity | Runtime | Markers |")
            content.append("|----------|------------|---------|---------|")
            
            for func in module.functions:
                markers_str = ", ".join(func.markers) if func.markers else "none"
                content.append(f"| `{func.name}` | {func.complexity} | {func.estimated_runtime} | {markers_str} |")
            content.append("")
        
        # Test classes
        if module.classes:
            content.append("#### Test Classes")
            content.append("")
            
            for cls in module.classes:
                content.append(f"**{cls.name}**")
                if cls.docstring:
                    content.append(f"- {cls.docstring}")
                content.append(f"- Methods: {len(cls.methods)}")
                content.append("")
        
        # Fixtures
        if module.fixtures:
            content.append("#### Fixtures")
            content.append("")
            for fixture in module.fixtures:
                content.append(f"- `{fixture}`")
            content.append("")
        
        content.append("---")
        content.append("")
        
        return content
    
    def generate_json_report(self, output_path: str = "test_documentation_report.json") -> Dict[str, Any]:
        """Generate a JSON report of the test suite."""
        test_files = self.discover_test_files()
        modules = []
        
        for file_path in test_files:
            module = self.parse_test_file(file_path)
            modules.append(module)
        
        # Convert to JSON-serializable format
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_files": len(test_files),
            "total_tests": sum(module.total_tests for module in modules),
            "modules": [asdict(module) for module in modules]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"JSON report generated: {output_path}")
        return report


def main():
    """Main entry point for the test documentation generator."""
    parser = argparse.ArgumentParser(description="Generate test documentation for GopiAI")
    parser.add_argument("--root", default=".", help="Root directory to scan for tests")
    parser.add_argument("--output", default="02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md", 
                       help="Output file for documentation")
    parser.add_argument("--json", help="Generate JSON report to specified file")
    parser.add_argument("--list-files", action="store_true", help="List discovered test files")
    
    args = parser.parse_args()
    
    generator = TestDocumentationGenerator(args.root)
    
    if args.list_files:
        test_files = generator.discover_test_files()
        print(f"Discovered {len(test_files)} test files:")
        for file_path in test_files:
            print(f"  {file_path}")
        return
    
    # Generate main documentation
    test_suite = generator.generate_test_suite_documentation(args.output)
    
    # Generate JSON report if requested
    if args.json:
        generator.generate_json_report(args.json)
    
    print(f"\nDocumentation Summary:")
    print(f"- Total tests: {test_suite.total_tests}")
    print(f"- Total modules: {len(test_suite.modules)}")
    print(f"- Categories: {', '.join(test_suite.categories.keys())}")
    print(f"- Estimated runtime: {test_suite.estimated_runtime}")


if __name__ == "__main__":
    main()