#!/usr/bin/env python3
"""
Problem Discovery System for GopiAI Testing Infrastructure

This module discovers and categorizes existing problems in the GopiAI codebase
to help prioritize testing efforts and mark known issues.
"""
import ast
import json
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re


class ProblemSeverity(Enum):
    """Severity levels for discovered problems."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ProblemCategory(Enum):
    """Categories of problems that can be discovered."""
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    MISSING_DEPENDENCY = "missing_dependency"
    DEPRECATED_API = "deprecated_api"
    TODO_FIXME = "todo_fixme"
    EXCEPTION_HANDLING = "exception_handling"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_ISSUE = "security_issue"
    CODE_SMELL = "code_smell"
    CONFIGURATION_ISSUE = "configuration_issue"


@dataclass
class Problem:
    """Represents a discovered problem in the codebase."""
    file_path: str
    line_number: int
    category: ProblemCategory
    severity: ProblemSeverity
    description: str
    code_snippet: str
    suggested_fix: Optional[str] = None
    test_marker: Optional[str] = None


class ProblemDiscovery:
    """Discovers and categorizes problems in the GopiAI codebase."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.problems: List[Problem] = []
        self.logger = logging.getLogger(__name__)
        
        # Patterns for different types of problems
        self.todo_patterns = [
            r'#\s*TODO[:\s](.+)',
            r'#\s*FIXME[:\s](.+)',
            r'#\s*HACK[:\s](.+)',
            r'#\s*XXX[:\s](.+)',
            r'#\s*BUG[:\s](.+)',
        ]
        
        self.deprecated_patterns = [
            r'warnings\.warn.*deprecated',
            r'DeprecationWarning',
            r'@deprecated',
        ]
        
        self.security_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'subprocess\.call.*shell=True',
            r'os\.system\s*\(',
            r'input\s*\(',  # Potential for injection
        ]
        
        # Known problematic imports/modules
        self.problematic_imports = {
            'imp': 'deprecated in Python 3.4+',
            'asyncore': 'deprecated in Python 3.6+',
            'asynchat': 'deprecated in Python 3.6+',
        }

    def discover_all_problems(self) -> List[Problem]:
        """Discover all problems in the GopiAI modules."""
        self.problems = []
        
        # Discover problems in each GopiAI module
        gopiai_modules = [
            "GopiAI-UI",
            "GopiAI-CrewAI", 
            "GopiAI-Assets"
        ]
        
        for module in gopiai_modules:
            module_path = self.root_path / module
            if module_path.exists():
                self.logger.info(f"Scanning module: {module}")
                self._scan_module(module_path, module)
        
        # Sort problems by severity and file path
        self.problems.sort(key=lambda p: (p.severity.value, p.file_path, p.line_number))
        
        return self.problems

    def _scan_module(self, module_path: Path, module_name: str):
        """Scan a specific GopiAI module for problems."""
        for py_file in module_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                self._scan_python_file(py_file, module_name)
            except Exception as e:
                self.logger.error(f"Error scanning {py_file}: {e}")
                self.problems.append(Problem(
                    file_path=str(py_file.relative_to(self.root_path)),
                    line_number=1,
                    category=ProblemCategory.SYNTAX_ERROR,
                    severity=ProblemSeverity.HIGH,
                    description=f"Failed to parse file: {e}",
                    code_snippet="",
                    test_marker="xfail_known_issue"
                ))

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during scanning."""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "venv",
            "env",
            "_env",
            ".egg-info",
            "htmlcov"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _scan_python_file(self, file_path: Path, module_name: str):
        """Scan a Python file for various types of problems."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            self.logger.error(f"Could not read {file_path}: {e}")
            return

        # Try to parse the AST
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, file_path, lines, module_name)
        except SyntaxError as e:
            self.problems.append(Problem(
                file_path=str(file_path.relative_to(self.root_path)),
                line_number=e.lineno or 1,
                category=ProblemCategory.SYNTAX_ERROR,
                severity=ProblemSeverity.CRITICAL,
                description=f"Syntax error: {e.msg}",
                code_snippet=lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else "",
                test_marker="xfail_known_issue"
            ))

        # Scan for text-based patterns
        self._scan_text_patterns(file_path, lines, module_name)

    def _analyze_ast(self, tree: ast.AST, file_path: Path, lines: List[str], module_name: str):
        """Analyze the AST for various problems."""
        for node in ast.walk(tree):
            # Check for problematic imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.problematic_imports:
                        self.problems.append(Problem(
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_number=node.lineno,
                            category=ProblemCategory.DEPRECATED_API,
                            severity=ProblemSeverity.MEDIUM,
                            description=f"Deprecated import: {alias.name} - {self.problematic_imports[alias.name]}",
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            suggested_fix=f"Replace {alias.name} with modern alternative"
                        ))
            
            # Check for bare except clauses
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.problems.append(Problem(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=node.lineno,
                        category=ProblemCategory.EXCEPTION_HANDLING,
                        severity=ProblemSeverity.MEDIUM,
                        description="Bare except clause - catches all exceptions",
                        code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        suggested_fix="Specify specific exception types to catch"
                    ))
            
            # Check for potential security issues
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        self.problems.append(Problem(
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_number=node.lineno,
                            category=ProblemCategory.SECURITY_ISSUE,
                            severity=ProblemSeverity.HIGH,
                            description=f"Potentially dangerous function: {node.func.id}",
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            suggested_fix="Avoid using eval/exec or validate input thoroughly"
                        ))

    def _scan_text_patterns(self, file_path: Path, lines: List[str], module_name: str):
        """Scan file content for text-based patterns."""
        for line_num, line in enumerate(lines, 1):
            # Check for TODO/FIXME comments
            for pattern in self.todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    self.problems.append(Problem(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=line_num,
                        category=ProblemCategory.TODO_FIXME,
                        severity=ProblemSeverity.LOW,
                        description=f"TODO/FIXME comment: {match.group(1).strip()}",
                        code_snippet=line.strip(),
                        test_marker="xfail_known_issue"
                    ))
            
            # Check for deprecated patterns
            for pattern in self.deprecated_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.problems.append(Problem(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=line_num,
                        category=ProblemCategory.DEPRECATED_API,
                        severity=ProblemSeverity.MEDIUM,
                        description="Deprecated API usage detected",
                        code_snippet=line.strip()
                    ))
            
            # Check for security patterns
            for pattern in self.security_patterns:
                if re.search(pattern, line):
                    self.problems.append(Problem(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=line_num,
                        category=ProblemCategory.SECURITY_ISSUE,
                        severity=ProblemSeverity.HIGH,
                        description="Potential security issue detected",
                        code_snippet=line.strip(),
                        suggested_fix="Review for security implications"
                    ))

    def generate_report(self, output_file: str = "problem_discovery_report.json"):
        """Generate a JSON report of discovered problems."""
        report = {
            "summary": {
                "total_problems": len(self.problems),
                "by_severity": {},
                "by_category": {},
                "by_module": {}
            },
            "problems": []
        }
        
        # Convert problems to serializable format
        for problem in self.problems:
            problem_dict = asdict(problem)
            problem_dict["category"] = problem.category.value
            problem_dict["severity"] = problem.severity.value
            report["problems"].append(problem_dict)
        
        # Calculate summary statistics
        for problem in self.problems:
            # By severity
            severity = problem.severity.value
            report["summary"]["by_severity"][severity] = report["summary"]["by_severity"].get(severity, 0) + 1
            
            # By category
            category = problem.category.value
            report["summary"]["by_category"][category] = report["summary"]["by_category"].get(category, 0) + 1
            
            # By module
            module = problem.file_path.split('/')[0] if '/' in problem.file_path else problem.file_path.split('\\')[0]
            report["summary"]["by_module"][module] = report["summary"]["by_module"].get(module, 0) + 1
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Problem discovery report written to {output_file}")
        return report

    def generate_pytest_markers(self, output_file: str = "pytest_markers.py"):
        """Generate pytest markers for known issues."""
        markers_content = '''"""
Pytest markers for known issues in GopiAI codebase.
Auto-generated by problem discovery system.
"""

import pytest

# Known issue markers for expected failures
'''
        
        # Group problems by file for easier marker generation
        file_problems = {}
        for problem in self.problems:
            if problem.test_marker:
                file_key = problem.file_path.replace('/', '_').replace('\\', '_').replace('.py', '')
                if file_key not in file_problems:
                    file_problems[file_key] = []
                file_problems[file_key].append(problem)
        
        # Generate marker functions
        for file_key, problems in file_problems.items():
            markers_content += f'''

def mark_known_issues_{file_key}():
    """Mark known issues for {file_key}."""
    markers = []
'''
            for problem in problems:
                markers_content += f'''    markers.append(pytest.mark.xfail(
        reason="{problem.description}",
        strict=False
    ))
'''
            markers_content += "    return markers\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markers_content)
        
        self.logger.info(f"Pytest markers written to {output_file}")


def main():
    """Main function to run problem discovery."""
    logging.basicConfig(level=logging.INFO)
    
    discovery = ProblemDiscovery()
    problems = discovery.discover_all_problems()
    
    print(f"Discovered {len(problems)} problems in GopiAI codebase")
    
    # Generate reports
    report = discovery.generate_report()
    discovery.generate_pytest_markers()
    
    # Print summary
    print("\nSummary by severity:")
    for severity, count in report["summary"]["by_severity"].items():
        print(f"  {severity}: {count}")
    
    print("\nSummary by category:")
    for category, count in report["summary"]["by_category"].items():
        print(f"  {category}: {count}")
    
    print("\nSummary by module:")
    for module, count in report["summary"]["by_module"].items():
        print(f"  {module}: {count}")


if __name__ == "__main__":
    main()