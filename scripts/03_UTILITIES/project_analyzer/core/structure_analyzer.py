"""
Structure Analyzer - Project Organization Analysis

This module implements the StructureAnalyzer class for analyzing project
organization, validating GopiAI-* module naming conventions, and detecting
misplaced files and inconsistent structures.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from .project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError


@dataclass
class ModuleInfo:
    """Information about a GopiAI module."""
    name: str
    path: Path
    has_pyproject: bool
    has_readme: bool
    has_gopiai_package: bool
    python_package_name: Optional[str] = None
    expected_structure: bool = False


@dataclass
class DirectoryInfo:
    """Information about a directory structure."""
    path: Path
    purpose: str  # 'module', 'documentation', 'utilities', 'examples', 'logs', 'config', 'other'
    expected: bool
    files_count: int
    subdirs_count: int


class StructureAnalyzer(BaseAnalyzer):
    """Analyzer for project organization and structure validation."""
    
    # Expected root-level directories and their purposes
    EXPECTED_ROOT_STRUCTURE = {
        'GopiAI-Core': 'module',
        'GopiAI-UI': 'module', 
        'GopiAI-CrewAI': 'module',
        'GopiAI-Extensions': 'module',
        'GopiAI-Widgets': 'module',
        'GopiAI-App': 'module',
        'GopiAI-Assets': 'module',
        '02_DOCUMENTATION': 'documentation',
        '03_UTILITIES': 'utilities',
        'examples': 'examples',
        'logs': 'logs',
        'conversations': 'data',
        '.kiro': 'config',
        '.serena': 'config',
        '.git': 'vcs',
        '.vscode': 'config',
        '.windsurf': 'config',
        'gopiai_env': 'environment',
        'crewai_env': 'environment',
        'txtai_env': 'environment',
        'potential_conflicts': 'temporary',
        'project_health': 'analysis',
        'rag_memory_system': 'legacy'
    }
    
    # Expected files in GopiAI-* modules
    EXPECTED_MODULE_FILES = {
        'pyproject.toml': 'required',
        'README.md': 'required', 
        'requirements.txt': 'optional'
    }
    
    # Expected structure within GopiAI-* modules
    EXPECTED_MODULE_DIRS = {
        'gopiai': 'required',
        'tests': 'recommended',
        'examples': 'optional'
    }
    
    def __init__(self, config):
        super().__init__(config)
        self.gopiai_modules: List[ModuleInfo] = []
        self.directory_info: List[DirectoryInfo] = []
        self.misplaced_files: List[Path] = []
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Structure Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform structure analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Convert project_root to absolute path for comparison
            project_root_abs = project_root.resolve()
            
            # Analyze root directory structure
            results.extend(self._analyze_root_structure(project_root))
            
            # Analyze GopiAI-* modules
            results.extend(self._analyze_gopiai_modules(project_root))
            
            # Check for misplaced files
            results.extend(self._detect_misplaced_files(project_root))
            
            # Validate naming conventions
            results.extend(self._validate_naming_conventions(project_root))
            
            # Check for inconsistent structures
            results.extend(self._detect_inconsistent_structures(project_root))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze project structure: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _analyze_root_structure(self, project_root: Path) -> List[AnalysisResult]:
        """Analyze the root directory structure."""
        results = []
        
        try:
            # Get all items in root directory
            root_items = [item for item in project_root.iterdir() if item.is_dir()]
            
            # Check for expected directories
            found_dirs = {item.name for item in root_items}
            expected_dirs = set(self.EXPECTED_ROOT_STRUCTURE.keys())
            
            # Find missing expected directories
            missing_dirs = expected_dirs - found_dirs
            for missing_dir in missing_dirs:
                purpose = self.EXPECTED_ROOT_STRUCTURE[missing_dir]
                if purpose == 'module':
                    results.append(AnalysisResult(
                        category="structure",
                        severity="medium",
                        description=f"Missing expected GopiAI module: {missing_dir}",
                        file_path=str(project_root),
                        recommendation=f"Consider creating {missing_dir} module if needed for project completeness"
                    ))
                elif purpose in ['documentation', 'utilities']:
                    results.append(AnalysisResult(
                        category="structure", 
                        severity="low",
                        description=f"Missing expected directory: {missing_dir}",
                        file_path=str(project_root),
                        recommendation=f"Create {missing_dir} directory for better project organization"
                    ))
            
            # Find unexpected directories
            unexpected_dirs = found_dirs - expected_dirs
            for unexpected_dir in unexpected_dirs:
                # Skip hidden directories and common temporary directories
                if not unexpected_dir.startswith('.') and unexpected_dir not in ['__pycache__', 'node_modules']:
                    results.append(AnalysisResult(
                        category="structure",
                        severity="low", 
                        description=f"Unexpected root directory: {unexpected_dir}",
                        file_path=str(project_root / unexpected_dir),
                        recommendation=f"Review if {unexpected_dir} belongs in root or should be moved/removed"
                    ))
            
            # Store directory information for later analysis
            for item in root_items:
                purpose = self.EXPECTED_ROOT_STRUCTURE.get(item.name, 'other')
                expected = item.name in self.EXPECTED_ROOT_STRUCTURE
                
                try:
                    files_count = len([f for f in item.rglob('*') if f.is_file()])
                    subdirs_count = len([d for d in item.rglob('*') if d.is_dir()])
                except (PermissionError, OSError):
                    files_count = 0
                    subdirs_count = 0
                
                self.directory_info.append(DirectoryInfo(
                    path=item,
                    purpose=purpose,
                    expected=expected,
                    files_count=files_count,
                    subdirs_count=subdirs_count
                ))
                
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze root structure: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _analyze_gopiai_modules(self, project_root: Path) -> List[AnalysisResult]:
        """Analyze GopiAI-* module structure and conventions."""
        results = []
        
        # Find all GopiAI-* directories
        gopiai_dirs = [d for d in project_root.iterdir() 
                      if d.is_dir() and d.name.startswith('GopiAI-')]
        
        for module_dir in gopiai_dirs:
            try:
                module_info = self._analyze_single_module(module_dir)
                self.gopiai_modules.append(module_info)
                
                # Check required files
                if not module_info.has_pyproject:
                    results.append(AnalysisResult(
                        category="module_structure",
                        severity="high",
                        description=f"Missing pyproject.toml in {module_info.name}",
                        file_path=str(module_dir),
                        recommendation="Add pyproject.toml file for proper Python package configuration"
                    ))
                
                if not module_info.has_readme:
                    results.append(AnalysisResult(
                        category="module_structure", 
                        severity="medium",
                        description=f"Missing README.md in {module_info.name}",
                        file_path=str(module_dir),
                        recommendation="Add README.md file to document the module purpose and usage"
                    ))
                
                if not module_info.has_gopiai_package:
                    results.append(AnalysisResult(
                        category="module_structure",
                        severity="high",
                        description=f"Missing gopiai/ package directory in {module_info.name}",
                        file_path=str(module_dir),
                        recommendation="Create gopiai/ directory with proper Python package structure"
                    ))
                
                # Check for expected structure
                if not module_info.expected_structure:
                    results.append(AnalysisResult(
                        category="module_structure",
                        severity="medium", 
                        description=f"Module {module_info.name} doesn't follow expected structure",
                        file_path=str(module_dir),
                        recommendation="Reorganize module to follow GopiAI module conventions"
                    ))
                
            except Exception as e:
                error = AnalysisError(
                    analyzer=self.get_analyzer_name(),
                    file_path=str(module_dir),
                    error=f"Failed to analyze module {module_dir.name}: {str(e)}",
                    original_exception=e
                )
                self.error_handler.handle_error(error)
        
        return results
    
    def _analyze_single_module(self, module_dir: Path) -> ModuleInfo:
        """Analyze a single GopiAI module."""
        module_name = module_dir.name
        
        # Check for required files
        has_pyproject = (module_dir / 'pyproject.toml').exists()
        has_readme = (module_dir / 'README.md').exists()
        
        # Check for gopiai package directory
        gopiai_dir = module_dir / 'gopiai'
        has_gopiai_package = gopiai_dir.exists() and gopiai_dir.is_dir()
        
        # Determine Python package name if gopiai directory exists
        python_package_name = None
        if has_gopiai_package:
            # Look for subdirectories in gopiai/ that represent the actual package
            subdirs = [d for d in gopiai_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
            if subdirs:
                python_package_name = subdirs[0].name
        
        # Check if structure follows expected pattern
        expected_structure = (
            has_pyproject and 
            has_gopiai_package and
            (module_dir / 'tests').exists()
        )
        
        return ModuleInfo(
            name=module_name,
            path=module_dir,
            has_pyproject=has_pyproject,
            has_readme=has_readme,
            has_gopiai_package=has_gopiai_package,
            python_package_name=python_package_name,
            expected_structure=expected_structure
        )
    
    def _detect_misplaced_files(self, project_root: Path) -> List[AnalysisResult]:
        """Detect files that might be in the wrong location."""
        results = []
        
        try:
            # Check for Python files in root directory
            root_py_files = [f for f in project_root.glob('*.py') 
                           if f.is_file() and not f.name.startswith('_')]
            
            for py_file in root_py_files:
                # Skip known utility scripts
                if py_file.name not in ['apply_memory_fix.py', 'fix_chat_issues.py']:
                    results.append(AnalysisResult(
                        category="misplaced_files",
                        severity="medium",
                        description=f"Python file in root directory: {py_file.name}",
                        file_path=str(py_file),
                        recommendation="Consider moving to appropriate module or 03_UTILITIES directory"
                    ))
            
            # Check for log files outside logs directory
            log_files = list(project_root.rglob('*.log'))
            logs_dir = project_root / 'logs'
            
            for log_file in log_files:
                if not str(log_file).startswith(str(logs_dir)):
                    results.append(AnalysisResult(
                        category="misplaced_files",
                        severity="low",
                        description=f"Log file outside logs directory: {log_file.name}",
                        file_path=str(log_file),
                        recommendation="Move log files to logs/ directory for better organization"
                    ))
            
            # Check for configuration files in wrong locations
            config_patterns = ['*.env', '*.json', '*.yml', '*.yaml', '*.toml']
            for pattern in config_patterns:
                config_files = list(project_root.glob(pattern))
                for config_file in config_files:
                    # Skip files that are expected in root
                    if config_file.name not in ['.env', 'pyproject.toml', 'requirements.txt']:
                        results.append(AnalysisResult(
                            category="misplaced_files",
                            severity="low",
                            description=f"Configuration file in root: {config_file.name}",
                            file_path=str(config_file),
                            recommendation="Consider moving to appropriate config directory"
                        ))
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to detect misplaced files: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _validate_naming_conventions(self, project_root: Path) -> List[AnalysisResult]:
        """Validate GopiAI-* module naming conventions."""
        results = []
        
        try:
            # Check GopiAI module naming
            for module_info in self.gopiai_modules:
                # Validate module name format
                if not re.match(r'^GopiAI-[A-Z][a-zA-Z]*$', module_info.name):
                    results.append(AnalysisResult(
                        category="naming_conventions",
                        severity="medium",
                        description=f"Module name doesn't follow convention: {module_info.name}",
                        file_path=str(module_info.path),
                        recommendation="Module names should follow GopiAI-PascalCase pattern"
                    ))
                
                # Check Python package naming within gopiai/
                if module_info.python_package_name:
                    expected_package_name = module_info.name.lower().replace('gopiai-', '').replace('-', '_')
                    if module_info.python_package_name != expected_package_name:
                        results.append(AnalysisResult(
                            category="naming_conventions",
                            severity="low",
                            description=f"Python package name inconsistent in {module_info.name}: {module_info.python_package_name}",
                            file_path=str(module_info.path / 'gopiai' / module_info.python_package_name),
                            recommendation=f"Consider renaming to {expected_package_name} for consistency"
                        ))
            
            # Check for directories that look like they should be GopiAI modules
            potential_modules = [d for d in project_root.iterdir() 
                               if d.is_dir() and 
                               ('gopiai' in d.name.lower() or 'gopi' in d.name.lower()) and
                               not d.name.startswith('GopiAI-')]
            
            for potential_module in potential_modules:
                results.append(AnalysisResult(
                    category="naming_conventions",
                    severity="medium",
                    description=f"Directory might be a GopiAI module with incorrect naming: {potential_module.name}",
                    file_path=str(potential_module),
                    recommendation="If this is a GopiAI module, rename to follow GopiAI-* convention"
                ))
                
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to validate naming conventions: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _detect_inconsistent_structures(self, project_root: Path) -> List[AnalysisResult]:
        """Detect inconsistent structures across modules."""
        results = []
        
        try:
            if len(self.gopiai_modules) < 2:
                return results  # Need at least 2 modules to compare
            
            # Analyze structure consistency across modules
            structure_patterns = {}
            
            for module_info in self.gopiai_modules:
                pattern = {
                    'has_tests': (module_info.path / 'tests').exists(),
                    'has_examples': (module_info.path / 'examples').exists(),
                    'has_requirements': (module_info.path / 'requirements.txt').exists(),
                    'has_init_in_gopiai': (module_info.path / 'gopiai' / '__init__.py').exists()
                }
                structure_patterns[module_info.name] = pattern
            
            # Find inconsistencies
            all_patterns = list(structure_patterns.values())
            if len(set(str(p) for p in all_patterns)) > 1:  # More than one unique pattern
                # Check specific inconsistencies
                
                # Tests directory consistency
                modules_with_tests = [name for name, pattern in structure_patterns.items() if pattern['has_tests']]
                modules_without_tests = [name for name, pattern in structure_patterns.items() if not pattern['has_tests']]
                
                if modules_with_tests and modules_without_tests:
                    for module_name in modules_without_tests:
                        results.append(AnalysisResult(
                            category="structure_consistency",
                            severity="medium",
                            description=f"Module {module_name} lacks tests directory while others have it",
                            file_path=str(project_root / module_name),
                            recommendation="Add tests directory for consistency with other modules"
                        ))
                
                # Requirements file consistency
                modules_with_req = [name for name, pattern in structure_patterns.items() if pattern['has_requirements']]
                modules_without_req = [name for name, pattern in structure_patterns.items() if not pattern['has_requirements']]
                
                if len(modules_with_req) > len(modules_without_req) and modules_without_req:
                    for module_name in modules_without_req:
                        results.append(AnalysisResult(
                            category="structure_consistency",
                            severity="low",
                            description=f"Module {module_name} lacks requirements.txt while most others have it",
                            file_path=str(project_root / module_name),
                            recommendation="Consider adding requirements.txt for dependency management consistency"
                        ))
                
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to detect inconsistent structures: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def get_structure_summary(self) -> Dict[str, any]:
        """Get a summary of the project structure analysis."""
        return {
            'total_gopiai_modules': len(self.gopiai_modules),
            'modules_with_proper_structure': len([m for m in self.gopiai_modules if m.expected_structure]),
            'total_directories': len(self.directory_info),
            'expected_directories': len([d for d in self.directory_info if d.expected]),
            'misplaced_files_count': len(self.misplaced_files),
            'module_details': [
                {
                    'name': m.name,
                    'has_pyproject': m.has_pyproject,
                    'has_readme': m.has_readme,
                    'has_gopiai_package': m.has_gopiai_package,
                    'expected_structure': m.expected_structure
                }
                for m in self.gopiai_modules
            ]
        }


if __name__ == "__main__":
    # Simple test of the StructureAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = StructureAnalyzer(config)
        
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
            for result in category_results:
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    → {result.recommendation}")
        
        # Print structure summary
        summary = analyzer.get_structure_summary()
        print(f"\nSTRUCTURE SUMMARY:")
        print(f"  GopiAI modules found: {summary['total_gopiai_modules']}")
        print(f"  Modules with proper structure: {summary['modules_with_proper_structure']}")
        print(f"  Total directories analyzed: {summary['total_directories']}")
        print(f"  Expected directories found: {summary['expected_directories']}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
