"""
Documentation Analyzer - Documentation Quality Assessment

This module implements the DocumentationAnalyzer class for analyzing documentation quality,
including README.md validation, docstring coverage analysis, documentation consistency checks,
and detection of outdated documentation references.
"""

import ast
import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from collections import defaultdict
import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError, AnalysisConfig


@dataclass
class DocstringInfo:
    """Represents information about a docstring."""
    file_path: str
    element_name: str
    element_type: str  # 'module', 'class', 'function', 'method'
    line_number: int
    has_docstring: bool
    docstring_length: int = 0
    has_parameters: bool = False
    has_returns: bool = False
    has_examples: bool = False


@dataclass
class ReadmeInfo:
    """Represents information about a README file."""
    file_path: str
    content: str
    last_modified: datetime.datetime
    sections: List[str]
    has_introduction: bool = False
    has_installation: bool = False
    has_usage: bool = False
    has_api_docs: bool = False
    references_files: List[str] = None


@dataclass
class DocumentationReference:
    """Represents a reference in documentation to code or other files."""
    source_file: str
    target_file: str
    line_number: int
    reference_text: str
    is_valid: bool = True
    reason: str = ""


class DocumentationAnalyzer(BaseAnalyzer):
    """Analyzer for documentation quality assessment."""
    
    # Common README sections to check for
    README_SECTIONS = [
        'introduction', 'overview', 'about',  # Introduction sections
        'installation', 'setup', 'getting started',  # Installation sections
        'usage', 'examples', 'how to use',  # Usage sections
        'api', 'documentation', 'reference',  # API documentation sections
        'contributing', 'development',  # Contributing sections
        'license', 'copyright'  # License sections
    ]
    
    # Patterns for detecting file references in documentation
    FILE_REFERENCE_PATTERNS = [
        r'(?:file|path):\s*[\'"`]([^\'"`]+)[\'"`]',  # file: "path/to/file.py"
        r'(?:import|from)\s+([a-zA-Z0-9_.]+)',  # import module or from module
        r'(?:see|check)\s+[\'"`]?([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]+)[\'"`]?',  # see "file.py"
        r'[\'"`]([a-zA-Z0-9_./\\-]+\.(py|md|txt|json|yaml|yml|toml))[\'"`]',  # "file.py"
    ]
    
    def __init__(self, config: AnalysisConfig):
        super().__init__(config)
        self.docstring_info: List[DocstringInfo] = []
        self.readme_files: List[ReadmeInfo] = []
        self.documentation_references: List[DocumentationReference] = []
        self.project_files: Set[str] = set()
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Documentation Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform documentation analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Get all project files for reference validation
            all_files = self.get_project_files(project_path)
            self.project_files = {str(f.relative_to(project_root)) for f in all_files}
            
            # Get Python files for docstring analysis
            python_files = [f for f in all_files if f.suffix.lower() == '.py']
            
            # Get README files
            readme_files = [f for f in all_files if f.name.lower() in ['readme.md', 'readme.txt', 'readme']]
            
            # Get documentation files
            doc_files = []
            for f in all_files:
                if f.suffix.lower() in ['.md', '.txt']:
                    # Check if file is in a documentation directory
                    if len(f.parts) >= 2 and ('doc' in f.parts[-2].lower() or 'documentation' in f.parts[-2].lower()):
                        doc_files.append(f)
                    # Also include files with 'doc' in their name
                    elif 'doc' in f.name.lower() or 'documentation' in f.name.lower():
                        doc_files.append(f)
            
            self.logger.info(f"Found {len(python_files)} Python files for docstring analysis")
            self.logger.info(f"Found {len(readme_files)} README files for analysis")
            self.logger.info(f"Found {len(doc_files)} documentation files for analysis")
            
            # Analyze docstrings in Python files
            for file_path in python_files:
                self._analyze_docstrings(file_path)
            
            # Analyze README files
            for file_path in readme_files:
                self._analyze_readme(file_path)
            
            # Analyze documentation references
            for file_path in readme_files + doc_files:
                self._analyze_documentation_references(file_path, project_root)
            
            # Generate analysis results
            results.extend(self._analyze_docstring_coverage())
            results.extend(self._analyze_readme_quality())
            results.extend(self._analyze_documentation_consistency())
            results.extend(self._analyze_outdated_references())
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze documentation: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _analyze_docstrings(self, file_path: Path) -> None:
        """
        Analyze docstrings in a Python file.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Skip very large files to avoid recursion issues
            if len(file_content) > 500000:  # Skip files larger than ~500KB
                self.logger.warning(f"Skipping large file {file_path} (size: {len(file_content)} bytes)")
                return
            
            # Parse the AST
            tree = ast.parse(file_content)
            
            # Analyze docstrings
            analyzer = DocstringAnalyzer(str(file_path))
            try:
                analyzer.visit(tree)
                self.docstring_info.extend(analyzer.docstring_info)
            except RecursionError:
                self.logger.warning(f"Recursion limit reached while analyzing {file_path}")
                # Still add any docstrings that were found before the recursion error
                self.docstring_info.extend(analyzer.docstring_info)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to analyze docstrings: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _analyze_readme(self, file_path: Path) -> None:
        """
        Analyze a README file.
        
        Args:
            file_path: Path to the README file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get last modified time
            last_modified = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Extract sections from markdown headings
            sections = []
            for line in content.splitlines():
                if line.startswith('#'):
                    section = line.lstrip('#').strip().lower()
                    sections.append(section)
            
            # Check for common sections
            readme_info = ReadmeInfo(
                file_path=str(file_path),
                content=content,
                last_modified=last_modified,
                sections=sections,
                references_files=[]
            )
            
            # Check for specific sections
            readme_info.has_introduction = any(
                section in ' '.join(sections).lower() 
                for section in ['introduction', 'overview', 'about']
            )
            readme_info.has_installation = any(
                section in ' '.join(sections).lower() 
                for section in ['installation', 'setup', 'getting started']
            )
            readme_info.has_usage = any(
                section in ' '.join(sections).lower() 
                for section in ['usage', 'examples', 'how to use']
            )
            readme_info.has_api_docs = any(
                section in ' '.join(sections).lower() 
                for section in ['api', 'documentation', 'reference']
            )
            
            # Extract file references
            references = []
            for pattern in self.FILE_REFERENCE_PATTERNS:
                for match in re.finditer(pattern, content):
                    references.append(match.group(1))
            
            readme_info.references_files = references
            self.readme_files.append(readme_info)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to analyze README: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _analyze_documentation_references(self, file_path: Path, project_root: Path) -> None:
        """
        Analyze references in documentation files.
        
        Args:
            file_path: Path to the documentation file
            project_root: Path to the project root
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all file references
            line_number = 0
            for line in content.splitlines():
                line_number += 1
                
                for pattern in self.FILE_REFERENCE_PATTERNS:
                    for match in re.finditer(pattern, line):
                        reference_text = match.group(1)
                        
                        # Normalize path
                        normalized_path = reference_text.replace('\\', '/')
                        
                        # Check if the referenced file exists
                        is_valid = normalized_path in self.project_files
                        
                        # If it's a Python import, check if the module exists
                        if not is_valid and '.' in normalized_path and '/' not in normalized_path:
                            # Could be a Python module import
                            possible_paths = [
                                f"{normalized_path.replace('.', '/')}.py",
                                f"{normalized_path.split('.')[0]}.py"
                            ]
                            is_valid = any(path in self.project_files for path in possible_paths)
                        
                        reason = "" if is_valid else "Referenced file does not exist"
                        
                        self.documentation_references.append(DocumentationReference(
                            source_file=str(file_path),
                            target_file=normalized_path,
                            line_number=line_number,
                            reference_text=reference_text,
                            is_valid=is_valid,
                            reason=reason
                        ))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to analyze documentation references: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _analyze_docstring_coverage(self) -> List[AnalysisResult]:
        """
        Analyze docstring coverage and quality.
        
        Returns:
            List of analysis results for docstring issues
        """
        results = []
        
        # Group docstrings by file
        docstrings_by_file = defaultdict(list)
        for info in self.docstring_info:
            docstrings_by_file[info.file_path].append(info)
        
        # Check files with low docstring coverage
        for file_path, docstrings in docstrings_by_file.items():
            # Skip files with very few elements (likely not needing extensive docs)
            if len(docstrings) < 3:
                continue
            
            # Calculate coverage
            total_elements = len(docstrings)
            documented_elements = sum(1 for d in docstrings if d.has_docstring)
            coverage_percent = (documented_elements / total_elements) * 100 if total_elements > 0 else 0
            
            # Report low coverage
            if coverage_percent < 50:
                results.append(AnalysisResult(
                    category="docstring_coverage",
                    severity="medium",
                    description=f"Low docstring coverage ({coverage_percent:.1f}%) in {file_path}",
                    file_path=file_path,
                    recommendation=f"Add docstrings to improve documentation coverage"
                ))
            
            # Check for public functions/methods without docstrings
            for docstring in docstrings:
                if (not docstring.has_docstring and 
                    docstring.element_type in ['function', 'method', 'class'] and
                    not docstring.element_name.startswith('_')):
                    
                    results.append(AnalysisResult(
                        category="missing_docstring",
                        severity="medium" if docstring.element_type == 'class' else "low",
                        description=f"Missing docstring for public {docstring.element_type} '{docstring.element_name}'",
                        file_path=docstring.file_path,
                        line_number=docstring.line_number,
                        recommendation=f"Add docstring to document the {docstring.element_type}'s purpose and usage"
                    ))
            
            # Check for incomplete docstrings (missing parameters or returns)
            for docstring in docstrings:
                if (docstring.has_docstring and 
                    docstring.element_type in ['function', 'method'] and
                    not docstring.element_name.startswith('_') and
                    not (docstring.has_parameters and docstring.has_returns)):
                    
                    missing = []
                    if not docstring.has_parameters:
                        missing.append("parameters")
                    if not docstring.has_returns:
                        missing.append("return values")
                    
                    if missing:
                        results.append(AnalysisResult(
                            category="incomplete_docstring",
                            severity="low",
                            description=f"Incomplete docstring for '{docstring.element_name}', missing {' and '.join(missing)}",
                            file_path=docstring.file_path,
                            line_number=docstring.line_number,
                            recommendation=f"Add documentation for {' and '.join(missing)}"
                        ))
        
        return results
    
    def _analyze_readme_quality(self) -> List[AnalysisResult]:
        """
        Analyze README quality and completeness.
        
        Returns:
            List of analysis results for README issues
        """
        results = []
        
        for readme in self.readme_files:
            # Check for missing essential sections
            missing_sections = []
            
            if not readme.has_introduction:
                missing_sections.append("introduction/overview")
            if not readme.has_installation:
                missing_sections.append("installation/setup")
            if not readme.has_usage:
                missing_sections.append("usage/examples")
            
            if missing_sections:
                results.append(AnalysisResult(
                    category="readme_completeness",
                    severity="medium",
                    description=f"README missing essential sections: {', '.join(missing_sections)}",
                    file_path=readme.file_path,
                    recommendation=f"Add {', '.join(missing_sections)} sections to improve README completeness"
                ))
            
            # Check for very short READMEs
            if len(readme.content) < 500:  # Arbitrary threshold for a minimal README
                results.append(AnalysisResult(
                    category="readme_length",
                    severity="low",
                    description=f"README is very short ({len(readme.content)} characters)",
                    file_path=readme.file_path,
                    recommendation="Expand README with more detailed information about the project"
                ))
            
            # Check for outdated READMEs (not modified in a long time)
            last_modified_days = (datetime.datetime.now() - readme.last_modified).days
            if last_modified_days > 180:  # 6 months
                results.append(AnalysisResult(
                    category="readme_freshness",
                    severity="low",
                    description=f"README not updated in {last_modified_days} days",
                    file_path=readme.file_path,
                    recommendation="Review and update README to reflect current project state"
                ))
        
        return results
    
    def _analyze_documentation_consistency(self) -> List[AnalysisResult]:
        """
        Analyze documentation consistency across modules.
        
        Returns:
            List of analysis results for documentation consistency issues
        """
        results = []
        
        # Group docstrings by module prefix (e.g., 'gopiai.core')
        module_docstrings = defaultdict(list)
        
        for info in self.docstring_info:
            # Extract module prefix from file path
            parts = Path(info.file_path).parts
            if 'gopiai' in parts:
                idx = parts.index('gopiai')
                if idx + 1 < len(parts):
                    module_prefix = f"gopiai.{parts[idx+1]}"
                    module_docstrings[module_prefix].append(info)
        
        # Check consistency within modules
        for module, docstrings in module_docstrings.items():
            # Skip modules with very few elements
            if len(docstrings) < 5:
                continue
            
            # Check docstring style consistency
            has_google_style = 0
            has_numpy_style = 0
            has_sphinx_style = 0
            
            for doc in docstrings:
                if not doc.has_docstring:
                    continue
                
                # Count different docstring styles
                if re.search(r'Args:', doc.element_name) or re.search(r'Returns:', doc.element_name):
                    has_google_style += 1
                elif re.search(r'Parameters\n-+', doc.element_name) or re.search(r'Returns\n-+', doc.element_name):
                    has_numpy_style += 1
                elif re.search(r':param', doc.element_name) or re.search(r':return:', doc.element_name):
                    has_sphinx_style += 1
            
            # Check if multiple styles are used
            styles_used = sum(1 for count in [has_google_style, has_numpy_style, has_sphinx_style] if count > 0)
            
            if styles_used > 1:
                results.append(AnalysisResult(
                    category="docstring_style_inconsistency",
                    severity="low",
                    description=f"Inconsistent docstring styles in {module} module",
                    file_path=docstrings[0].file_path,
                    recommendation="Standardize on a single docstring style (Google, NumPy, or Sphinx) across the module"
                ))
        
        return results
    
    def _analyze_outdated_references(self) -> List[AnalysisResult]:
        """
        Analyze outdated documentation references.
        
        Returns:
            List of analysis results for outdated reference issues
        """
        results = []
        
        # Check for invalid references
        for reference in self.documentation_references:
            if not reference.is_valid:
                results.append(AnalysisResult(
                    category="invalid_reference",
                    severity="medium",
                    description=f"Invalid file reference: '{reference.reference_text}'",
                    file_path=reference.source_file,
                    line_number=reference.line_number,
                    recommendation=f"Update or remove reference to non-existent file"
                ))
        
        # Check for references to outdated file paths
        # This would require historical data, which we don't have in this implementation
        
        return results
    
    def get_documentation_summary(self) -> Dict[str, Any]:
        """Get a summary of the documentation analysis."""
        return {
            'total_python_files': len(set(info.file_path for info in self.docstring_info)),
            'total_readme_files': len(self.readme_files),
            'total_docstrings': len(self.docstring_info),
            'documented_elements': sum(1 for info in self.docstring_info if info.has_docstring),
            'documentation_references': len(self.documentation_references),
            'invalid_references': sum(1 for ref in self.documentation_references if not ref.is_valid)
        }


class DocstringAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze docstrings in Python files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.docstring_info: List[DocstringInfo] = []
        self.current_class = None
    
    def visit_Module(self, node):
        """Visit module node to check for module-level docstring."""
        docstring = ast.get_docstring(node)
        
        self.docstring_info.append(DocstringInfo(
            file_path=self.file_path,
            element_name="module",
            element_type="module",
            line_number=1,
            has_docstring=docstring is not None,
            docstring_length=len(docstring) if docstring else 0,
            has_parameters=False,
            has_returns=False,
            has_examples=bool(docstring and 'example' in docstring.lower()) if docstring else False
        ))
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definition to check for class docstring."""
        docstring = ast.get_docstring(node)
        
        self.docstring_info.append(DocstringInfo(
            file_path=self.file_path,
            element_name=node.name,
            element_type="class",
            line_number=node.lineno,
            has_docstring=docstring is not None,
            docstring_length=len(docstring) if docstring else 0,
            has_parameters=bool(docstring and ('param' in docstring.lower() or 'args' in docstring.lower())) if docstring else False,
            has_returns=False,
            has_examples=bool(docstring and 'example' in docstring.lower()) if docstring else False
        ))
        
        # Track current class for method context
        old_class = self.current_class
        self.current_class = node.name
        
        self.generic_visit(node)
        
        # Restore previous class context
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definition to check for function/method docstring."""
        docstring = ast.get_docstring(node)
        
        # Determine if this is a function or method
        element_type = "method" if self.current_class else "function"
        
        # Check for parameters and return documentation
        has_parameters = False
        has_returns = False
        has_examples = False
        
        if docstring:
            has_parameters = ('param' in docstring.lower() or 
                             'args:' in docstring.lower() or 
                             'parameters' in docstring.lower())
            
            has_returns = ('return' in docstring.lower() or 
                          'yields' in docstring.lower())
            
            has_examples = 'example' in docstring.lower()
        
        self.docstring_info.append(DocstringInfo(
            file_path=self.file_path,
            element_name=f"{self.current_class}.{node.name}" if self.current_class else node.name,
            element_type=element_type,
            line_number=node.lineno,
            has_docstring=docstring is not None,
            docstring_length=len(docstring) if docstring else 0,
            has_parameters=has_parameters,
            has_returns=has_returns,
            has_examples=has_examples
        ))
        
        self.generic_visit(node)


if __name__ == "__main__":
    # Test the DocumentationAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Increase recursion limit for complex ASTs
    sys.setrecursionlimit(3000)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = DocumentationAnalyzer(config)
        
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
        
        # Print documentation summary
        summary = analyzer.get_documentation_summary()
        print(f"\nDOCUMENTATION ANALYSIS SUMMARY:")
        print(f"  Python files analyzed: {summary['total_python_files']}")
        print(f"  README files analyzed: {summary['total_readme_files']}")
        print(f"  Code elements analyzed: {summary['total_docstrings']}")
        print(f"  Documented elements: {summary['documented_elements']}")
        print(f"  Documentation references: {summary['documentation_references']}")
        print(f"  Invalid references: {summary['invalid_references']}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)