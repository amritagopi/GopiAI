"""
Dead Code Analyzer - Unused Code Detection

This module implements the DeadCodeAnalyzer class for identifying unused functions,
classes, variables, imports, and commented-out code blocks in Python files.
"""

import ast
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import importlib.util

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError, AnalysisConfig


@dataclass
class UnusedCode:
    """Information about unused code."""
    name: str
    type: str  # 'function', 'class', 'variable', 'import', 'commented_code'
    file_path: str
    line_number: int
    code_snippet: str = ""


class DeadCodeAnalyzer(BaseAnalyzer):
    """Analyzer for detecting unused code in Python files."""
    
    # Patterns for commented-out code detection
    COMMENTED_CODE_PATTERNS = [
        r'^\s*#\s*def\s+\w+',  # Commented function definition
        r'^\s*#\s*class\s+\w+', # Commented class definition
        r'^\s*#\s*import\s+\w+', # Commented import statement
        r'^\s*#\s*from\s+[\w\.]+\s+import', # Commented from import
        r'^\s*#\s*if\s+.*:', # Commented if statement
        r'^\s*#\s*for\s+.*:', # Commented for loop
        r'^\s*#\s*while\s+.*:', # Commented while loop
        r'^\s*#\s*try:', # Commented try block
        r'^\s*#\s*with\s+.*:', # Commented with statement
        r'^\s*#\s*\w+\s*=\s*.*', # Commented assignment
    ]
    
    def __init__(self, config: AnalysisConfig):
        super().__init__(config)
        self.vulture_available = self._check_tool_available('vulture')
        self.logger.info(f"Vulture available: {self.vulture_available}")
        
        # Store analysis results for reporting
        self.unused_code: List[UnusedCode] = []
        self.module_imports: Dict[str, Set[str]] = {}  # file_path -> set of imported modules
        self.module_references: Dict[str, Set[str]] = {}  # module_name -> set of files referencing it
    
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Dead Code Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform dead code analysis on the project.
        
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
            
            self.logger.info(f"Found {len(python_files)} Python files for analysis")
            
            # Use vulture for dead code detection if available
            if self.vulture_available:
                results.extend(self._run_vulture(python_files))
            
            # Analyze imports and build import graph
            self._build_import_graph(python_files)
            
            # Find unreferenced modules
            results.extend(self._find_unreferenced_modules(python_files))
            
            # Check for commented-out code blocks
            results.extend(self._detect_commented_code(python_files))
            
            # Perform custom AST-based analysis for unused code
            results.extend(self._analyze_unused_code_with_ast(python_files))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze dead code: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _check_tool_available(self, tool_name: str) -> bool:
        """
        Check if an external tool is available.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if the tool is available, False otherwise
        """
        try:
            # Use subprocess.run with a simple command to check if tool exists
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['where', tool_name], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    timeout=2
                )
            else:  # Unix/Linux/Mac
                result = subprocess.run(
                    ['which', tool_name], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    timeout=2
                )
            
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _run_vulture(self, python_files: List[Path]) -> List[AnalysisResult]:
        """
        Run vulture on Python files to detect unused code.
        
        Args:
            python_files: List of Python files to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        try:
            # Create a temporary file with the list of files to check
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                for file_path in python_files:
                    temp_file.write(f"{file_path}\n")
                temp_file_path = temp_file.name
            
            # Run vulture with the file list
            vulture_cmd = ['vulture', '--min-confidence', '80', f'--paths-file={temp_file_path}']
            
            process = subprocess.run(
                vulture_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30  # Timeout after 30 seconds
            )
            
            # Parse vulture output
            # Format: path/to/file.py:line: unused function 'function_name' (60% confidence)
            pattern = r'(.+?):(\d+): unused (\w+) \'(.+?)\' \((\d+)% confidence\)'
            
            for line in process.stdout.splitlines():
                match = re.match(pattern, line)
                if match:
                    file_path, line_num, code_type, name, confidence = match.groups()
                    
                    # Determine severity based on confidence
                    confidence_int = int(confidence)
                    severity = 'low'
                    if confidence_int >= 90:
                        severity = 'high'
                    elif confidence_int >= 70:
                        severity = 'medium'
                    
                    # Store unused code
                    self.unused_code.append(UnusedCode(
                        name=name,
                        type=code_type,
                        file_path=file_path,
                        line_number=int(line_num)
                    ))
                    
                    # Add analysis result
                    results.append(AnalysisResult(
                        category="unused_code",
                        severity=severity,
                        description=f"Unused {code_type}: '{name}' ({confidence}% confidence)",
                        file_path=file_path,
                        line_number=int(line_num),
                        recommendation=f"Consider removing unused {code_type} '{name}'"
                    ))
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path="multiple files",
                error=f"Failed to run vulture: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _build_import_graph(self, python_files: List[Path]) -> None:
        """
        Build an import graph to track module dependencies.
        
        Args:
            python_files: List of Python files to analyze
        """
        # Reset import tracking
        self.module_imports = {}
        self.module_references = {}
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Parse the AST
                tree = ast.parse(file_content)
                
                # Find all imports
                import_visitor = ImportVisitor()
                import_visitor.visit(tree)
                
                # Store imports for this file
                self.module_imports[str(file_path)] = set(import_visitor.imports)
                
                # Update module references
                for module_name in import_visitor.imports:
                    if module_name not in self.module_references:
                        self.module_references[module_name] = set()
                    self.module_references[module_name].add(str(file_path))
                
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to analyze imports: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
    
    def _find_unreferenced_modules(self, python_files: List[Path]) -> List[AnalysisResult]:
        """
        Find modules that are not referenced by any other module.
        
        Args:
            python_files: List of Python files to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        # Get all module names from file paths
        module_names = {}
        for file_path in python_files:
            try:
                # Convert file path to potential module name
                rel_path = file_path.relative_to(Path(self.config.project_path))
                
                # Skip files in site-packages or other non-project directories
                if any(part.startswith('_') or part in ['site-packages', 'dist-packages'] 
                      for part in rel_path.parts):
                    continue
                
                # Convert path to module name (e.g., path/to/module.py -> path.to.module)
                module_path = str(rel_path).replace(os.sep, '.')
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]  # Remove .py extension
                
                # Store mapping of module name to file path
                module_names[module_path] = str(file_path)
                
                # Also store parent package paths
                parts = module_path.split('.')
                for i in range(1, len(parts)):
                    parent_module = '.'.join(parts[:i])
                    if parent_module not in module_names:
                        parent_dir = file_path.parent
                        for _ in range(len(parts) - i):
                            parent_dir = parent_dir.parent
                        init_file = parent_dir / '__init__.py'
                        if init_file.exists():
                            module_names[parent_module] = str(init_file)
                
            except Exception as e:
                self.logger.debug(f"Error processing module name for {file_path}: {e}")
        
        # Find unreferenced modules
        for module_name, file_path in module_names.items():
            # Skip __init__.py and __main__.py files
            if module_name.endswith('__init__') or module_name.endswith('__main__'):
                continue
            
            # Check if this module is imported anywhere
            is_referenced = False
            
            # Check direct imports
            if module_name in self.module_references:
                is_referenced = True
            
            # Check partial imports (e.g., 'from package.module import func')
            for ref_module in self.module_references:
                if ref_module.startswith(f"{module_name}.") or ref_module.startswith(f"from {module_name}"):
                    is_referenced = True
                    break
            
            # Check if it's a script that might be run directly
            if not is_referenced:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has a main block or is executable
                    if '__main__' in content and ('if __name__ == ' in content or 'if __name__==' in content):
                        is_referenced = True
                except Exception:
                    pass
            
            # If not referenced, add to results
            if not is_referenced:
                results.append(AnalysisResult(
                    category="unreferenced_module",
                    severity="medium",
                    description=f"Unreferenced module: {module_name}",
                    file_path=file_path,
                    recommendation=f"Consider removing or using module '{module_name}'"
                ))
        
        return results
    
    def _detect_commented_code(self, python_files: List[Path]) -> List[AnalysisResult]:
        """
        Detect commented-out code blocks using regex patterns.
        
        Args:
            python_files: List of Python files to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Track consecutive commented lines
                comment_block = []
                comment_start_line = 0
                
                for i, line in enumerate(lines, 1):
                    line = line.rstrip()
                    
                    # Check if this is a comment line
                    if line.strip().startswith('#'):
                        if not comment_block:
                            comment_start_line = i
                        comment_block.append(line)
                    else:
                        # Process the comment block if it exists
                        if comment_block:
                            # Check if the block contains code
                            if self._is_commented_code(comment_block):
                                # Store unused code
                                self.unused_code.append(UnusedCode(
                                    name=f"commented_code_line_{comment_start_line}",
                                    type="commented_code",
                                    file_path=str(file_path),
                                    line_number=comment_start_line,
                                    code_snippet='\n'.join(comment_block)
                                ))
                                
                                # Add analysis result
                                results.append(AnalysisResult(
                                    category="commented_code",
                                    severity="low",
                                    description=f"Commented-out code block at line {comment_start_line}",
                                    file_path=str(file_path),
                                    line_number=comment_start_line,
                                    recommendation="Remove commented-out code or add explanation if kept intentionally"
                                ))
                            
                            # Reset comment block
                            comment_block = []
                
                # Check final comment block if file ends with comments
                if comment_block and self._is_commented_code(comment_block):
                    self.unused_code.append(UnusedCode(
                        name=f"commented_code_line_{comment_start_line}",
                        type="commented_code",
                        file_path=str(file_path),
                        line_number=comment_start_line,
                        code_snippet='\n'.join(comment_block)
                    ))
                    
                    results.append(AnalysisResult(
                        category="commented_code",
                        severity="low",
                        description=f"Commented-out code block at line {comment_start_line}",
                        file_path=str(file_path),
                        line_number=comment_start_line,
                        recommendation="Remove commented-out code or add explanation if kept intentionally"
                    ))
                
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to detect commented code: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _is_commented_code(self, comment_lines: List[str]) -> bool:
        """
        Check if a block of comment lines contains code.
        
        Args:
            comment_lines: List of comment lines to check
            
        Returns:
            True if the comments appear to be code, False otherwise
        """
        # Skip short comment blocks (likely not code)
        if len(comment_lines) < 2:
            return False
        
        # Check for code patterns in the comment block
        for line in comment_lines:
            # Check against code patterns
            for pattern in self.COMMENTED_CODE_PATTERNS:
                if re.match(pattern, line):
                    return True
            
            # Check for indentation patterns that suggest code
            if re.match(r'^\s*#\s*\s{4,}', line):  # Indented at least 4 spaces
                return True
        
        # Check if the uncommented block would be valid Python
        try:
            # Remove the comment character and leading whitespace
            uncommented = '\n'.join(re.sub(r'^\s*#\s?', '', line) for line in comment_lines)
            if uncommented.strip():  # Only try to parse if there's actual content
                ast.parse(uncommented)
                return True
        except SyntaxError:
            # Not valid Python code when uncommented
            pass
        
        return False
    
    def _analyze_unused_code_with_ast(self, python_files: List[Path]) -> List[AnalysisResult]:
        """
        Use AST to analyze unused code that might be missed by vulture.
        
        Args:
            python_files: List of Python files to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Parse the AST
                tree = ast.parse(file_content)
                
                # Find unused imports
                import_visitor = ImportVisitor()
                import_visitor.visit(tree)
                
                # Find all name references
                name_visitor = NameVisitor()
                name_visitor.visit(tree)
                
                # Check for unused imports
                for import_name in import_visitor.imports:
                    # Skip common imports that might be used implicitly
                    if import_name in ['__future__', 'typing', 'abc']:
                        continue
                    
                    # Check if the import is used
                    base_name = import_name.split('.')[0]
                    if base_name not in name_visitor.used_names:
                        # Check if it's an import with alias
                        if base_name in import_visitor.aliases:
                            alias = import_visitor.aliases[base_name]
                            if alias not in name_visitor.used_names:
                                self._add_unused_import_result(results, import_name, file_path, import_visitor.line_numbers.get(base_name, 1))
                        else:
                            self._add_unused_import_result(results, import_name, file_path, import_visitor.line_numbers.get(base_name, 1))
                
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(file_path),
                    error=f"Failed to analyze AST: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _add_unused_import_result(self, results: List[AnalysisResult], import_name: str, file_path: Path, line_number: int) -> None:
        """
        Add an unused import result.
        
        Args:
            results: List to add the result to
            import_name: Name of the unused import
            file_path: Path to the file containing the import
            line_number: Line number of the import
        """
        # Store unused code
        self.unused_code.append(UnusedCode(
            name=import_name,
            type="import",
            file_path=str(file_path),
            line_number=line_number
        ))
        
        # Add analysis result
        results.append(AnalysisResult(
            category="unused_import",
            severity="low",
            description=f"Unused import: '{import_name}'",
            file_path=str(file_path),
            line_number=line_number,
            recommendation=f"Remove unused import '{import_name}'"
        ))
    
    def get_dead_code_summary(self) -> Dict[str, Any]:
        """Get a summary of the dead code analysis."""
        return {
            'total_unused_code': len(self.unused_code),
            'unused_functions': len([u for u in self.unused_code if u.type == 'function']),
            'unused_classes': len([u for u in self.unused_code if u.type == 'class']),
            'unused_variables': len([u for u in self.unused_code if u.type == 'variable']),
            'unused_imports': len([u for u in self.unused_code if u.type == 'import']),
            'commented_code_blocks': len([u for u in self.unused_code if u.type == 'commented_code']),
            'files_with_dead_code': len(set(u.file_path for u in self.unused_code))
        }


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to find all imports in a module."""
    
    def __init__(self):
        self.imports = []  # List of imported module names
        self.aliases = {}  # Map of alias -> original name
        self.line_numbers = {}  # Map of module name -> line number
    
    def visit_Import(self, node):
        """Visit an import statement."""
        for name in node.names:
            module_name = name.name
            self.imports.append(module_name)
            
            if name.asname:
                self.aliases[name.asname] = module_name
            
            self.line_numbers[module_name.split('.')[0]] = node.lineno
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit a from-import statement."""
        if node.module:
            module_name = node.module
            self.imports.append(module_name)
            
            for name in node.names:
                if name.asname:
                    self.aliases[name.asname] = f"{module_name}.{name.name}"
                
            self.line_numbers[module_name.split('.')[0]] = node.lineno
        
        self.generic_visit(node)


class NameVisitor(ast.NodeVisitor):
    """AST visitor to find all name references in a module."""
    
    def __init__(self):
        self.used_names = set()  # Set of used names
    
    def visit_Name(self, node):
        """Visit a name node."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Visit an attribute node."""
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        
        self.generic_visit(node)


if __name__ == "__main__":
    # Simple test of the DeadCodeAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = DeadCodeAnalyzer(config)
        
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
            print(f"\n{category.upper()}:")
            for result in category_results[:5]:  # Show only first 5 results per category
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    → {result.recommendation}")
            
            if len(category_results) > 5:
                print(f"    ... and {len(category_results) - 5} more issues")
        
        # Print dead code summary
        summary = analyzer.get_dead_code_summary()
        print(f"\nDEAD CODE SUMMARY:")
        print(f"  Total unused code: {summary['total_unused_code']}")
        print(f"  Unused functions: {summary['unused_functions']}")
        print(f"  Unused classes: {summary['unused_classes']}")
        print(f"  Unused variables: {summary['unused_variables']}")
        print(f"  Unused imports: {summary['unused_imports']}")
        print(f"  Commented code blocks: {summary['commented_code_blocks']}")
        print(f"  Files with dead code: {summary['files_with_dead_code']}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)