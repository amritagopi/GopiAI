"""
Conflict Analyzer - Potential Error Detection

This module implements the ConflictAnalyzer class for analyzing potential runtime issues,
including global variable usage patterns, threading issues, resource management problems,
and unhandled exceptions in Python files.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from collections import defaultdict

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError, AnalysisConfig


@dataclass
class GlobalVariableUsage:
    """Represents usage of a global variable."""
    name: str
    file_path: str
    line_number: int
    usage_type: str  # 'read', 'write', 'modify'
    context: str  # Function or class context


@dataclass
class ThreadingIssue:
    """Represents a potential threading or race condition issue."""
    issue_type: str  # 'shared_state', 'race_condition', 'deadlock_risk'
    file_path: str
    line_number: int
    description: str
    severity: str


@dataclass
class ResourceIssue:
    """Represents a resource management issue."""
    resource_type: str  # 'file', 'connection', 'memory', 'lock'
    file_path: str
    line_number: int
    issue_description: str
    is_properly_closed: bool


@dataclass
class ExceptionIssue:
    """Represents an unhandled exception issue."""
    exception_type: str
    file_path: str
    line_number: int
    context: str
    is_handled: bool


class ConflictAnalyzer(BaseAnalyzer):
    """Analyzer for detecting potential conflicts and runtime errors."""
    
    # Patterns for detecting resource usage
    RESOURCE_PATTERNS = {
        'file': [
            r'open\s*\(',
            r'\.open\s*\(',
            r'file\s*\(',
        ],
        'connection': [
            r'connect\s*\(',
            r'\.connect\s*\(',
            r'Connection\s*\(',
            r'socket\s*\(',
        ],
        'lock': [
            r'Lock\s*\(',
            r'RLock\s*\(',
            r'Semaphore\s*\(',
            r'threading\.',
        ],
        'memory': [
            r'malloc\s*\(',
            r'calloc\s*\(',
            r'numpy\.array\s*\(',
            r'\.allocate\s*\(',
        ]
    }
    
    # Threading-related imports and functions
    THREADING_INDICATORS = {
        'threading', 'multiprocessing', 'concurrent.futures',
        'asyncio', 'queue', 'Queue'
    }
    
    def __init__(self, config: AnalysisConfig):
        super().__init__(config)
        self.global_variables: List[GlobalVariableUsage] = []
        self.threading_issues: List[ThreadingIssue] = []
        self.resource_issues: List[ResourceIssue] = []
        self.exception_issues: List[ExceptionIssue] = []
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Conflict Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform conflict analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Get all Python files
            python_files = self.get_project_files(project_path, ['.py'])
            
            if not python_files:
                self.logger.info("No Python files found for analysis")
                return []
            
            self.logger.info(f"Found {len(python_files)} Python files for conflict analysis")
            
            # Analyze each file
            for file_path in python_files:
                self._analyze_file(file_path)
            
            # Generate analysis results
            results.extend(self._analyze_global_variable_conflicts())
            results.extend(self._analyze_threading_issues())
            results.extend(self._analyze_resource_management())
            results.extend(self._analyze_exception_handling())
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze conflicts: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _analyze_file(self, file_path: Path) -> None:
        """
        Analyze a single Python file for potential conflicts.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                lines = file_content.splitlines()
            
            # Parse the AST
            tree = ast.parse(file_content)
            
            # Analyze different aspects
            self._analyze_global_variables(tree, str(file_path), lines)
            self._analyze_threading_patterns(tree, str(file_path), lines)
            self._analyze_resource_usage(tree, str(file_path), lines)
            self._analyze_exception_patterns(tree, str(file_path), lines)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to analyze file: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _analyze_global_variables(self, tree: ast.AST, file_path: str, lines: List[str]) -> None:
        """
        Analyze global variable usage patterns.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            lines: Lines of the file
        """
        analyzer = GlobalVariableAnalyzer(file_path)
        analyzer.visit(tree)
        self.global_variables.extend(analyzer.global_usages)
    
    def _analyze_threading_patterns(self, tree: ast.AST, file_path: str, lines: List[str]) -> None:
        """
        Analyze threading and race condition patterns.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            lines: Lines of the file
        """
        analyzer = ThreadingAnalyzer(file_path)
        analyzer.visit(tree)
        self.threading_issues.extend(analyzer.threading_issues)
    
    def _analyze_resource_usage(self, tree: ast.AST, file_path: str, lines: List[str]) -> None:
        """
        Analyze resource management patterns.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            lines: Lines of the file
        """
        analyzer = ResourceAnalyzer(file_path, lines)
        analyzer.visit(tree)
        self.resource_issues.extend(analyzer.resource_issues)
    
    def _analyze_exception_patterns(self, tree: ast.AST, file_path: str, lines: List[str]) -> None:
        """
        Analyze exception handling patterns.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            lines: Lines of the file
        """
        analyzer = ExceptionAnalyzer(file_path)
        analyzer.visit(tree)
        self.exception_issues.extend(analyzer.exception_issues)
    
    def _analyze_global_variable_conflicts(self) -> List[AnalysisResult]:
        """
        Analyze global variable usage for potential conflicts.
        
        Returns:
            List of analysis results for global variable issues
        """
        results = []
        
        # Group global variables by name
        global_by_name = defaultdict(list)
        for usage in self.global_variables:
            global_by_name[usage.name].append(usage)
        
        # Find variables used across multiple files
        for var_name, usages in global_by_name.items():
            files = set(usage.file_path for usage in usages)
            
            if len(files) > 1:
                # Check for write operations across files
                write_files = set(usage.file_path for usage in usages if usage.usage_type in ['write', 'modify'])
                
                if len(write_files) > 1:
                    file_list = ', '.join(files)
                    results.append(AnalysisResult(
                        category="global_variable_conflict",
                        severity="high",
                        description=f"Global variable '{var_name}' is modified in multiple files: {file_list}",
                        file_path=usages[0].file_path,
                        line_number=usages[0].line_number,
                        recommendation=f"Consider using a centralized state manager or passing '{var_name}' as a parameter instead of using global variables"
                    ))
                elif len(files) > 2:
                    file_list = ', '.join(files)
                    results.append(AnalysisResult(
                        category="global_variable_usage",
                        severity="medium",
                        description=f"Global variable '{var_name}' is accessed from multiple files: {file_list}",
                        file_path=usages[0].file_path,
                        line_number=usages[0].line_number,
                        recommendation=f"Consider refactoring to reduce global variable dependencies for '{var_name}'"
                    ))
        
        # Find variables with mixed read/write patterns
        for var_name, usages in global_by_name.items():
            has_reads = any(usage.usage_type == 'read' for usage in usages)
            has_writes = any(usage.usage_type in ['write', 'modify'] for usage in usages)
            
            if has_reads and has_writes and len(usages) > 3:
                results.append(AnalysisResult(
                    category="global_variable_complexity",
                    severity="medium",
                    description=f"Global variable '{var_name}' has complex usage pattern with {len(usages)} references",
                    file_path=usages[0].file_path,
                    line_number=usages[0].line_number,
                    recommendation=f"Consider encapsulating '{var_name}' in a class or module to better manage its state"
                ))
        
        return results
    
    def _analyze_threading_issues(self) -> List[AnalysisResult]:
        """
        Analyze threading issues for potential race conditions.
        
        Returns:
            List of analysis results for threading issues
        """
        results = []
        
        for issue in self.threading_issues:
            results.append(AnalysisResult(
                category="threading_issue",
                severity=issue.severity,
                description=issue.description,
                file_path=issue.file_path,
                line_number=issue.line_number,
                recommendation=self._get_threading_recommendation(issue.issue_type)
            ))
        
        return results
    
    def _analyze_resource_management(self) -> List[AnalysisResult]:
        """
        Analyze resource management for potential leaks.
        
        Returns:
            List of analysis results for resource management issues
        """
        results = []
        
        for issue in self.resource_issues:
            if not issue.is_properly_closed:
                severity = "high" if issue.resource_type in ['file', 'connection'] else "medium"
                results.append(AnalysisResult(
                    category="resource_leak",
                    severity=severity,
                    description=f"Potential {issue.resource_type} resource leak: {issue.issue_description}",
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    recommendation=self._get_resource_recommendation(issue.resource_type)
                ))
        
        return results
    
    def _analyze_exception_handling(self) -> List[AnalysisResult]:
        """
        Analyze exception handling for unhandled exceptions.
        
        Returns:
            List of analysis results for exception handling issues
        """
        results = []
        
        for issue in self.exception_issues:
            if not issue.is_handled:
                results.append(AnalysisResult(
                    category="unhandled_exception",
                    severity="medium",
                    description=f"Potential unhandled {issue.exception_type} exception in {issue.context}",
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    recommendation="Add proper exception handling with try-except blocks"
                ))
        
        return results
    
    def _get_threading_recommendation(self, issue_type: str) -> str:
        """Get recommendation for threading issues."""
        recommendations = {
            'shared_state': "Use locks, queues, or other synchronization primitives to protect shared state",
            'race_condition': "Implement proper synchronization mechanisms to prevent race conditions",
            'deadlock_risk': "Review lock ordering and consider using context managers or timeouts"
        }
        return recommendations.get(issue_type, "Review threading implementation for potential issues")
    
    def _get_resource_recommendation(self, resource_type: str) -> str:
        """Get recommendation for resource management issues."""
        recommendations = {
            'file': "Use 'with' statement or ensure files are properly closed in finally blocks",
            'connection': "Use connection context managers or ensure connections are closed in finally blocks",
            'lock': "Use 'with' statement for locks or ensure locks are released in finally blocks",
            'memory': "Ensure proper memory cleanup and consider using context managers"
        }
        return recommendations.get(resource_type, "Ensure proper resource cleanup")
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Get a summary of the conflict analysis."""
        return {
            'global_variables': len(self.global_variables),
            'threading_issues': len(self.threading_issues),
            'resource_issues': len(self.resource_issues),
            'exception_issues': len(self.exception_issues),
            'files_with_conflicts': len(set(
                [usage.file_path for usage in self.global_variables] +
                [issue.file_path for issue in self.threading_issues] +
                [issue.file_path for issue in self.resource_issues] +
                [issue.file_path for issue in self.exception_issues]
            ))
        }


class GlobalVariableAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze global variable usage patterns."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.global_usages: List[GlobalVariableUsage] = []
        self.current_context = "module"
        self.global_declarations = set()
    
    def visit_Global(self, node):
        """Visit global declarations."""
        for name in node.names:
            self.global_declarations.add(name)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        old_context = self.current_context
        self.current_context = f"function:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        old_context = self.current_context
        self.current_context = f"class:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
    
    def visit_Name(self, node):
        """Visit name references."""
        # Check if this might be a global variable
        if (isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)) and
            not node.id.startswith('_') and  # Skip private variables
            node.id not in ['self', 'cls'] and  # Skip common parameters
            not node.id.isupper()):  # Skip constants
            
            usage_type = 'read'
            if isinstance(node.ctx, ast.Store):
                usage_type = 'write'
            elif isinstance(node.ctx, ast.Del):
                usage_type = 'modify'
            
            # Only track if it's declared as global or used across contexts
            if (node.id in self.global_declarations or 
                self.current_context != "module"):
                
                self.global_usages.append(GlobalVariableUsage(
                    name=node.id,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    usage_type=usage_type,
                    context=self.current_context
                ))
        
        self.generic_visit(node)


class ThreadingAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze threading patterns and potential issues."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.threading_issues: List[ThreadingIssue] = []
        self.has_threading_imports = False
        self.shared_variables = set()
        self.lock_usage = []
    
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            if any(threading_mod in alias.name for threading_mod in ConflictAnalyzer.THREADING_INDICATORS):
                self.has_threading_imports = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from-import statements."""
        if node.module and any(threading_mod in node.module for threading_mod in ConflictAnalyzer.THREADING_INDICATORS):
            self.has_threading_imports = True
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visit function calls."""
        if self.has_threading_imports:
            # Check for threading-related calls
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['start', 'join', 'acquire', 'release']:
                    self._check_threading_call(node)
            elif isinstance(node.func, ast.Name):
                if node.func.id in ['Thread', 'Process', 'Lock', 'RLock']:
                    self._check_threading_call(node)
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Visit assignments."""
        if self.has_threading_imports:
            # Check for shared state assignments
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.shared_variables.add(target.id)
        
        self.generic_visit(node)
    
    def _check_threading_call(self, node):
        """Check threading-related function calls for issues."""
        # Check for potential race conditions
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'start':
            self.threading_issues.append(ThreadingIssue(
                issue_type='race_condition',
                file_path=self.file_path,
                line_number=node.lineno,
                description="Thread started - check for shared state access without synchronization",
                severity='medium'
            ))
        
        # Check for lock usage patterns
        if isinstance(node.func, ast.Name) and node.func.id in ['Lock', 'RLock']:
            self.lock_usage.append(node.lineno)
        
        # Check for acquire without release
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'acquire':
            self.threading_issues.append(ThreadingIssue(
                issue_type='deadlock_risk',
                file_path=self.file_path,
                line_number=node.lineno,
                description="Lock acquired - ensure it's properly released",
                severity='medium'
            ))


class ResourceAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze resource management patterns."""
    
    def __init__(self, file_path: str, lines: List[str]):
        self.file_path = file_path
        self.lines = lines
        self.resource_issues: List[ResourceIssue] = []
        self.open_resources = []
        self.with_statements = set()
    
    def visit_With(self, node):
        """Visit with statements."""
        # Track with statements for proper resource management
        for item in node.items:
            if hasattr(item, 'context_expr'):
                self.with_statements.add(node.lineno)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visit function calls."""
        # Check for resource-opening calls
        if isinstance(node.func, ast.Name):
            if node.func.id == 'open':
                self._check_file_usage(node)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['connect', 'open']:
                self._check_connection_usage(node)
        
        self.generic_visit(node)
    
    def _check_file_usage(self, node):
        """Check file usage patterns."""
        # Check if file is opened within a with statement
        is_in_with = any(
            with_line <= node.lineno <= with_line + 10  # Approximate range
            for with_line in self.with_statements
        )
        
        if not is_in_with:
            # Look for explicit close() calls in the following lines
            has_close = self._has_explicit_close(node.lineno)
            
            self.resource_issues.append(ResourceIssue(
                resource_type='file',
                file_path=self.file_path,
                line_number=node.lineno,
                issue_description="File opened without 'with' statement",
                is_properly_closed=has_close
            ))
    
    def _check_connection_usage(self, node):
        """Check connection usage patterns."""
        # Similar logic for connections
        is_in_with = any(
            with_line <= node.lineno <= with_line + 10
            for with_line in self.with_statements
        )
        
        if not is_in_with:
            has_close = self._has_explicit_close(node.lineno)
            
            self.resource_issues.append(ResourceIssue(
                resource_type='connection',
                file_path=self.file_path,
                line_number=node.lineno,
                issue_description="Connection opened without proper context management",
                is_properly_closed=has_close
            ))
    
    def _has_explicit_close(self, start_line: int) -> bool:
        """Check if there's an explicit close() call after the resource opening."""
        # Look in the next 20 lines for a close() call
        end_line = min(start_line + 20, len(self.lines))
        
        for i in range(start_line, end_line):
            if i < len(self.lines) and '.close()' in self.lines[i]:
                return True
        
        return False


class ExceptionAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze exception handling patterns."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.exception_issues: List[ExceptionIssue] = []
        self.try_blocks = set()
        self.current_context = "module"
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        old_context = self.current_context
        self.current_context = f"function:{node.name}"
        self.generic_visit(node)
        self.current_context = old_context
    
    def visit_Try(self, node):
        """Visit try statements."""
        self.try_blocks.add(node.lineno)
        self.generic_visit(node)
    
    def visit_Raise(self, node):
        """Visit raise statements."""
        # Check if raise is within a try block
        is_in_try = any(
            try_line <= node.lineno <= try_line + 50  # Approximate range
            for try_line in self.try_blocks
        )
        
        exception_type = "Exception"
        if node.exc and isinstance(node.exc, ast.Name):
            exception_type = node.exc.id
        elif node.exc and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
            exception_type = node.exc.func.id
        
        self.exception_issues.append(ExceptionIssue(
            exception_type=exception_type,
            file_path=self.file_path,
            line_number=node.lineno,
            context=self.current_context,
            is_handled=is_in_try
        ))
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visit function calls that might raise exceptions."""
        # Check for calls that commonly raise exceptions
        risky_calls = ['int', 'float', 'open', 'json.loads', 'requests.get']
        
        if isinstance(node.func, ast.Name) and node.func.id in risky_calls:
            is_in_try = any(
                try_line <= node.lineno <= try_line + 50
                for try_line in self.try_blocks
            )
            
            if not is_in_try:
                self.exception_issues.append(ExceptionIssue(
                    exception_type=f"{node.func.id}_exception",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    context=self.current_context,
                    is_handled=False
                ))
        
        self.generic_visit(node)


if __name__ == "__main__":
    # Test the ConflictAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = ConflictAnalyzer(config)
        
        print(f"Testing {analyzer.get_analyzer_name()}...")
        results = analyzer.analyze(project_path)
        
        print(f"Analysis complete. Found {len(results)} results:")
        
        # Group results by category
        by_category = {}
        for result in results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        for category, category_results in by_category.items():
            print(f"\n{category.upper()} ({len(category_results)} issues):")
            for result in category_results[:3]:  # Show only first 3 results per category
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    Recommendation: {result.recommendation}")
            
            if len(category_results) > 3:
                print(f"    ... and {len(category_results) - 3} more issues")
        
        # Print conflict summary
        summary = analyzer.get_conflict_summary()
        print(f"\nCONFLICT ANALYSIS SUMMARY:")
        print(f"  Global variables analyzed: {summary['global_variables']}")
        print(f"  Threading issues found: {summary['threading_issues']}")
        print(f"  Resource issues found: {summary['resource_issues']}")
        print(f"  Exception issues found: {summary['exception_issues']}")
        print(f"  Files with conflicts: {summary['files_with_conflicts']}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)