"""
Code Quality Analyzer - Code Style and Quality Assessment

This module implements the CodeQualityAnalyzer class for analyzing Python code
quality, style consistency, and complexity. It uses AST parsing for analysis
and integrates with external tools when available.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError


@dataclass
class ComplexityResult:
    """Result of complexity analysis for a function or method."""
    name: str
    complexity: int
    line_number: int
    file_path: str
    type: str  # 'function', 'method', 'class'


@dataclass
class StyleIssue:
    """Represents a code style issue."""
    file_path: str
    line_number: int
    column: int
    issue_type: str
    description: str
    severity: str


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating cyclomatic complexity."""
    
    def __init__(self):
        self.complexity_results: List[Tuple[str, int, int]] = []
        self.current_complexity = 1
        self.function_stack: List[str] = []
        
    def visit_FunctionDef(self, node):
        """Visit function definition and calculate complexity."""
        self._analyze_function(node, 'function')
        
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition and calculate complexity."""
        self._analyze_function(node, 'async_function')
        
    def visit_ClassDef(self, node):
        """Visit class definition."""
        # Don't count class complexity, just visit methods
        self.generic_visit(node)
        
    def _analyze_function(self, node, func_type):
        """Analyze a function or method for complexity."""
        old_complexity = self.current_complexity
        self.current_complexity = 1
        self.function_stack.append(node.name)
        
        # Visit all child nodes to count complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                self.current_complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                self.current_complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                self.current_complexity += 1
            elif isinstance(child, ast.Assert):
                self.current_complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Count additional complexity for boolean operations
                self.current_complexity += len(child.values) - 1
        
        # Store result
        self.complexity_results.append((
            node.name,
            self.current_complexity,
            node.lineno
        ))
        
        self.function_stack.pop()
        self.current_complexity = old_complexity


class StyleChecker:
    """Checks for common Python style issues."""
    
    def __init__(self):
        self.issues: List[StyleIssue] = []
        
    def check_file(self, file_path: Path) -> List[StyleIssue]:
        """Check a Python file for style issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Check each line for style issues
            for line_num, line in enumerate(lines, 1):
                issues.extend(self._check_line(file_path, line_num, line))
                
            # Check overall file structure
            issues.extend(self._check_file_structure(file_path, lines))
            
        except Exception as e:
            # Return an issue for files that can't be read
            issues.append(StyleIssue(
                file_path=str(file_path),
                line_number=1,
                column=1,
                issue_type="file_error",
                description=f"Could not read file: {str(e)}",
                severity="low"
            ))
            
        return issues
    
    def _check_line(self, file_path: Path, line_num: int, line: str) -> List[StyleIssue]:
        """Check a single line for style issues."""
        issues = []
        
        # Check line length (PEP 8 recommends 79 characters)
        if len(line.rstrip()) > 88:  # Using Black's default of 88
            issues.append(StyleIssue(
                file_path=str(file_path),
                line_number=line_num,
                column=89,
                issue_type="line_too_long",
                description=f"Line too long ({len(line.rstrip())} > 88 characters)",
                severity="low"
            ))
        
        # Check for trailing whitespace
        if line.rstrip() != line.rstrip('\n\r'):
            issues.append(StyleIssue(
                file_path=str(file_path),
                line_number=line_num,
                column=len(line.rstrip()) + 1,
                issue_type="trailing_whitespace",
                description="Trailing whitespace",
                severity="low"
            ))
        
        # Check for tabs (should use spaces)
        if '\t' in line:
            issues.append(StyleIssue(
                file_path=str(file_path),
                line_number=line_num,
                column=line.find('\t') + 1,
                issue_type="tab_indentation",
                description="Use spaces instead of tabs for indentation",
                severity="medium"
            ))
        
        # Check for multiple statements on one line
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            # Simple check for multiple statements (semicolon not in string)
            if ';' in stripped and not self._is_in_string(stripped, stripped.find(';')):
                issues.append(StyleIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    column=line.find(';') + 1,
                    issue_type="multiple_statements",
                    description="Multiple statements on one line",
                    severity="medium"
                ))
        
        return issues
    
    def _check_file_structure(self, file_path: Path, lines: List[str]) -> List[StyleIssue]:
        """Check overall file structure."""
        issues = []
        
        # Check for missing docstring in modules
        if len(lines) > 0:
            # Skip shebang and encoding declarations
            start_line = 0
            for i, line in enumerate(lines[:3]):
                if line.strip().startswith('#'):
                    start_line = i + 1
                else:
                    break
            
            # Look for module docstring
            if start_line < len(lines):
                first_statement = lines[start_line].strip()
                if first_statement and not (first_statement.startswith('"""') or first_statement.startswith("'''")):
                    # Check if it's an import or other statement
                    if first_statement.startswith(('import ', 'from ', 'class ', 'def ', 'async def ')):
                        issues.append(StyleIssue(
                            file_path=str(file_path),
                            line_number=start_line + 1,
                            column=1,
                            issue_type="missing_module_docstring",
                            description="Module should have a docstring",
                            severity="low"
                        ))
        
        # Check for too many blank lines at end of file
        trailing_blank_lines = 0
        for line in reversed(lines):
            if line.strip() == '':
                trailing_blank_lines += 1
            else:
                break
        
        if trailing_blank_lines > 2:
            issues.append(StyleIssue(
                file_path=str(file_path),
                line_number=len(lines) - trailing_blank_lines + 1,
                column=1,
                issue_type="too_many_blank_lines",
                description=f"Too many blank lines at end of file ({trailing_blank_lines})",
                severity="low"
            ))
        
        return issues
    
    def _is_in_string(self, line: str, position: int) -> bool:
        """Check if a position in a line is inside a string literal."""
        # Simple check - count quotes before the position
        before_pos = line[:position]
        single_quotes = before_pos.count("'") - before_pos.count("\\'")
        double_quotes = before_pos.count('"') - before_pos.count('\\"')
        
        # If odd number of quotes, we're inside a string
        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)


class CodeQualityAnalyzer(BaseAnalyzer):
    """Analyzer for code quality, style, and complexity assessment."""
    
    def __init__(self, config):
        super().__init__(config)
        self.complexity_results: List[ComplexityResult] = []
        self.style_issues: List[StyleIssue] = []
        self.consistency_issues: List[AnalysisResult] = []
        
        # Check for external tool availability
        self.flake8_available = self._check_tool_availability('flake8')
        self.black_available = self._check_tool_availability('black')
        
        # Configuration thresholds
        self.complexity_threshold_high = 15
        self.complexity_threshold_medium = 10
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Code Quality Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform code quality analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        
        try:
            # Get Python files to analyze
            python_files = self.get_project_files(project_path, ['.py'])
            
            if not python_files:
                return results
            
            # Analyze code complexity
            results.extend(self._analyze_code_complexity(python_files))
            
            # Check code style
            results.extend(self._check_code_style(python_files))
            
            # Check for consistency issues across modules
            results.extend(self._check_consistency_across_modules(python_files))
            
            # Use external tools if available
            if self.flake8_available:
                results.extend(self._run_flake8_analysis(project_path))
            
            if self.black_available:
                results.extend(self._run_black_analysis(python_files))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=project_path,
                error=f"Failed to analyze code quality: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _analyze_code_complexity(self, python_files: List[Path]) -> List[AnalysisResult]:
        """Analyze cyclomatic complexity of Python functions."""
        results = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the AST
                tree = ast.parse(content, filename=str(file_path))
                
                # Visit nodes to calculate complexity
                visitor = ComplexityVisitor()
                visitor.visit(tree)
                
                # Process results
                for func_name, complexity, line_num in visitor.complexity_results:
                    complexity_result = ComplexityResult(
                        name=func_name,
                        complexity=complexity,
                        line_number=line_num,
                        file_path=str(file_path),
                        type='function'
                    )
                    self.complexity_results.append(complexity_result)
                    
                    # Create analysis results based on complexity thresholds
                    if complexity >= self.complexity_threshold_high:
                        results.append(AnalysisResult(
                            category="complexity",
                            severity="high",
                            description=f"Function '{func_name}' has high complexity ({complexity})",
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation=f"Consider refactoring '{func_name}' to reduce complexity. "
                                         f"Break it into smaller functions or simplify conditional logic."
                        ))
                    elif complexity >= self.complexity_threshold_medium:
                        results.append(AnalysisResult(
                            category="complexity",
                            severity="medium",
                            description=f"Function '{func_name}' has moderate complexity ({complexity})",
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation=f"Consider reviewing '{func_name}' for potential simplification."
                        ))
                
            except SyntaxError as e:
                results.append(AnalysisResult(
                    category="syntax_error",
                    severity="high",
                    description=f"Syntax error in file: {str(e)}",
                    file_path=str(file_path),
                    line_number=getattr(e, 'lineno', None),
                    recommendation="Fix syntax error to enable proper code analysis"
                ))
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to analyze complexity: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _check_code_style(self, python_files: List[Path]) -> List[AnalysisResult]:
        """Check code style using built-in style checker."""
        results = []
        
        style_checker = StyleChecker()
        
        for file_path in python_files:
            try:
                issues = style_checker.check_file(file_path)
                self.style_issues.extend(issues)
                
                # Convert style issues to analysis results
                for issue in issues:
                    results.append(AnalysisResult(
                        category="style",
                        severity=issue.severity,
                        description=f"{issue.issue_type}: {issue.description}",
                        file_path=issue.file_path,
                        line_number=issue.line_number,
                        recommendation=self._get_style_recommendation(issue.issue_type)
                    ))
                
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to check style: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _check_consistency_across_modules(self, python_files: List[Path]) -> List[AnalysisResult]:
        """Check for consistency issues across different modules."""
        results = []
        
        try:
            # Group files by module (GopiAI-* directories)
            modules = defaultdict(list)
            
            for file_path in python_files:
                # Find the GopiAI module this file belongs to
                parts = file_path.parts
                module_name = None
                
                for part in parts:
                    if part.startswith('GopiAI-'):
                        module_name = part
                        break
                
                if module_name:
                    modules[module_name].append(file_path)
            
            # Analyze consistency patterns
            if len(modules) > 1:
                results.extend(self._check_import_consistency(modules))
                results.extend(self._check_naming_consistency(modules))
                results.extend(self._check_docstring_consistency(modules))
        
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path="multiple_modules",
                error=f"Failed to check consistency: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _check_import_consistency(self, modules: Dict[str, List[Path]]) -> List[AnalysisResult]:
        """Check for consistent import patterns across modules."""
        results = []
        
        # Analyze import patterns in each module
        import_patterns = {}
        
        for module_name, files in modules.items():
            patterns = {
                'relative_imports': 0,
                'absolute_imports': 0,
                'star_imports': 0,
                'common_imports': set()
            }
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                patterns['common_imports'].add(alias.name)
                                patterns['absolute_imports'] += 1
                        elif isinstance(node, ast.ImportFrom):
                            if node.level > 0:
                                patterns['relative_imports'] += 1
                            else:
                                patterns['absolute_imports'] += 1
                            
                            if any(alias.name == '*' for alias in node.names):
                                patterns['star_imports'] += 1
                                
                except Exception:
                    continue  # Skip files that can't be parsed
            
            import_patterns[module_name] = patterns
        
        # Check for inconsistencies
        star_import_modules = [name for name, patterns in import_patterns.items() 
                              if patterns['star_imports'] > 0]
        
        if star_import_modules and len(star_import_modules) < len(modules):
            for module_name in star_import_modules:
                results.append(AnalysisResult(
                    category="consistency",
                    severity="medium",
                    description=f"Module {module_name} uses star imports while others don't",
                    file_path=module_name,
                    recommendation="Avoid star imports for better code clarity and consistency"
                ))
        
        return results
    
    def _check_naming_consistency(self, modules: Dict[str, List[Path]]) -> List[AnalysisResult]:
        """Check for consistent naming patterns across modules."""
        results = []
        
        # This is a simplified check - in a full implementation, you'd analyze
        # function names, class names, variable names, etc.
        
        naming_patterns = {}
        
        for module_name, files in modules.items():
            patterns = {
                'snake_case_functions': 0,
                'camelCase_functions': 0,
                'PascalCase_classes': 0,
                'snake_case_classes': 0
            }
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if '_' in node.name:
                                patterns['snake_case_functions'] += 1
                            elif node.name[0].islower() and any(c.isupper() for c in node.name):
                                patterns['camelCase_functions'] += 1
                        elif isinstance(node, ast.ClassDef):
                            if node.name[0].isupper() and not '_' in node.name:
                                patterns['PascalCase_classes'] += 1
                            elif '_' in node.name:
                                patterns['snake_case_classes'] += 1
                                
                except Exception:
                    continue
            
            naming_patterns[module_name] = patterns
        
        # Check for inconsistent function naming
        snake_case_modules = [name for name, patterns in naming_patterns.items() 
                             if patterns['snake_case_functions'] > patterns['camelCase_functions']]
        camel_case_modules = [name for name, patterns in naming_patterns.items() 
                             if patterns['camelCase_functions'] > patterns['snake_case_functions']]
        
        if snake_case_modules and camel_case_modules:
            for module_name in camel_case_modules:
                results.append(AnalysisResult(
                    category="consistency",
                    severity="low",
                    description=f"Module {module_name} uses camelCase functions while others use snake_case",
                    file_path=module_name,
                    recommendation="Consider using snake_case for function names (PEP 8 recommendation)"
                ))
        
        return results
    
    def _check_docstring_consistency(self, modules: Dict[str, List[Path]]) -> List[AnalysisResult]:
        """Check for consistent docstring patterns across modules."""
        results = []
        
        docstring_patterns = {}
        
        for module_name, files in modules.items():
            patterns = {
                'functions_with_docstrings': 0,
                'functions_without_docstrings': 0,
                'classes_with_docstrings': 0,
                'classes_without_docstrings': 0
            }
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if ast.get_docstring(node):
                                patterns['functions_with_docstrings'] += 1
                            else:
                                patterns['functions_without_docstrings'] += 1
                        elif isinstance(node, ast.ClassDef):
                            if ast.get_docstring(node):
                                patterns['classes_with_docstrings'] += 1
                            else:
                                patterns['classes_without_docstrings'] += 1
                                
                except Exception:
                    continue
            
            docstring_patterns[module_name] = patterns
        
        # Check for modules with significantly fewer docstrings
        total_functions = sum(p['functions_with_docstrings'] + p['functions_without_docstrings'] 
                             for p in docstring_patterns.values())
        total_with_docstrings = sum(p['functions_with_docstrings'] 
                                   for p in docstring_patterns.values())
        
        if total_functions > 0:
            overall_docstring_rate = total_with_docstrings / total_functions
            
            for module_name, patterns in docstring_patterns.items():
                module_functions = patterns['functions_with_docstrings'] + patterns['functions_without_docstrings']
                if module_functions > 0:
                    module_rate = patterns['functions_with_docstrings'] / module_functions
                    
                    if module_rate < overall_docstring_rate * 0.5:  # Significantly lower
                        results.append(AnalysisResult(
                            category="consistency",
                            severity="low",
                            description=f"Module {module_name} has lower docstring coverage ({module_rate:.1%}) than project average ({overall_docstring_rate:.1%})",
                            file_path=module_name,
                            recommendation="Add docstrings to functions and classes for better documentation consistency"
                        ))
        
        return results
    
    def _run_flake8_analysis(self, project_path: str) -> List[AnalysisResult]:
        """Run flake8 analysis if available."""
        results = []
        
        try:
            # Run flake8 with basic configuration
            cmd = ['flake8', '--max-line-length=88', '--extend-ignore=E203,W503', project_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return results  # No issues found
            
            # Parse flake8 output
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        file_path, line_num, col_num, message = parts
                        
                        # Determine severity based on error code
                        severity = "low"
                        if any(code in message for code in ['E9', 'F', 'C9']):
                            severity = "high"
                        elif any(code in message for code in ['E7', 'W6']):
                            severity = "medium"
                        
                        results.append(AnalysisResult(
                            category="flake8",
                            severity=severity,
                            description=f"Flake8: {message.strip()}",
                            file_path=file_path.strip(),
                            line_number=int(line_num) if line_num.isdigit() else None,
                            recommendation="Fix the style issue according to PEP 8 guidelines"
                        ))
        
        except subprocess.TimeoutExpired:
            results.append(AnalysisResult(
                category="tool_error",
                severity="low",
                description="Flake8 analysis timed out",
                file_path=project_path,
                recommendation="Consider running flake8 manually on smaller subsets of files"
            ))
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=project_path,
                error=f"Failed to run flake8: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _run_black_analysis(self, python_files: List[Path]) -> List[AnalysisResult]:
        """Run black analysis if available."""
        results = []
        
        try:
            # Run black in check mode
            file_paths = [str(f) for f in python_files[:10]]  # Limit to first 10 files
            cmd = ['black', '--check', '--diff'] + file_paths
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return results  # No formatting issues
            
            # Parse black output to find files that need formatting
            current_file = None
            for line in result.stderr.split('\n'):
                if line.startswith('would reformat'):
                    file_path = line.split()[-1]
                    results.append(AnalysisResult(
                        category="formatting",
                        severity="low",
                        description="File needs formatting according to Black standards",
                        file_path=file_path,
                        recommendation="Run 'black' on this file to auto-format it"
                    ))
        
        except subprocess.TimeoutExpired:
            results.append(AnalysisResult(
                category="tool_error",
                severity="low",
                description="Black analysis timed out",
                file_path="multiple_files",
                recommendation="Consider running black manually on individual files"
            ))
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path="multiple_files",
                error=f"Failed to run black: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _check_tool_availability(self, tool_name: str) -> bool:
        """Check if an external tool is available."""
        try:
            result = subprocess.run([tool_name, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _get_style_recommendation(self, issue_type: str) -> str:
        """Get recommendation for a specific style issue type."""
        recommendations = {
            'line_too_long': 'Break long lines using parentheses, backslashes, or refactor into smaller parts',
            'trailing_whitespace': 'Remove trailing whitespace from the end of lines',
            'tab_indentation': 'Use 4 spaces for indentation instead of tabs (PEP 8)',
            'multiple_statements': 'Put each statement on its own line for better readability',
            'missing_module_docstring': 'Add a module-level docstring explaining the purpose of this module',
            'too_many_blank_lines': 'Remove excessive blank lines at the end of the file',
            'file_error': 'Fix file encoding or permission issues'
        }
        return recommendations.get(issue_type, 'Review and fix the style issue')
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get a summary of the code quality analysis."""
        return {
            'total_complexity_issues': len([r for r in self.complexity_results 
                                          if r.complexity >= self.complexity_threshold_medium]),
            'high_complexity_functions': len([r for r in self.complexity_results 
                                            if r.complexity >= self.complexity_threshold_high]),
            'total_style_issues': len(self.style_issues),
            'style_issues_by_type': self._group_style_issues_by_type(),
            'average_complexity': self._calculate_average_complexity(),
            'most_complex_function': self._get_most_complex_function(),
            'flake8_available': self.flake8_available,
            'black_available': self.black_available
        }
    
    def _group_style_issues_by_type(self) -> Dict[str, int]:
        """Group style issues by type."""
        groups = defaultdict(int)
        for issue in self.style_issues:
            groups[issue.issue_type] += 1
        return dict(groups)
    
    def _calculate_average_complexity(self) -> float:
        """Calculate average complexity across all functions."""
        if not self.complexity_results:
            return 0.0
        return sum(r.complexity for r in self.complexity_results) / len(self.complexity_results)
    
    def _get_most_complex_function(self) -> Optional[ComplexityResult]:
        """Get the most complex function found."""
        if not self.complexity_results:
            return None
        return max(self.complexity_results, key=lambda r: r.complexity)


if __name__ == "__main__":
    # Simple test of the CodeQualityAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = CodeQualityAnalyzer(config)
        
        print(f"Testing {analyzer.get_analyzer_name()}...")
        print(f"Flake8 available: {analyzer.flake8_available}")
        print(f"Black available: {analyzer.black_available}")
        
        results = analyzer.analyze(project_path)
        
        print(f"Analysis complete. Found {len(results)} results:")
        
        # Group results by category
        by_category = defaultdict(list)
        for result in results:
            by_category[result.category].append(result)
        
        for category, category_results in by_category.items():
            print(f"\n{category.upper()}:")
            for result in category_results[:5]:  # Show first 5 of each category
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    -> {result.recommendation}")
        
        # Print quality summary
        summary = analyzer.get_quality_summary()
        print(f"\nQUALITY SUMMARY:")
        print(f"  Total complexity issues: {summary['total_complexity_issues']}")
        print(f"  High complexity functions: {summary['high_complexity_functions']}")
        print(f"  Total style issues: {summary['total_style_issues']}")
        print(f"  Average complexity: {summary['average_complexity']:.1f}")
        
        if summary['most_complex_function']:
            mcf = summary['most_complex_function']
            print(f"  Most complex function: {mcf.name} (complexity: {mcf.complexity})")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)