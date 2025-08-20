"""
Dependency Analyzer for Project Cleanup

This module analyzes external dependencies in the GopiAI project by parsing
pyproject.toml and requirements.txt files, checking for security vulnerabilities,
version conflicts, and unused dependencies.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
import json
import logging
from dataclasses import dataclass
from packaging import version
from packaging.requirements import Requirement, InvalidRequirement

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError


@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version_spec: str
    source_file: str
    line_number: Optional[int] = None
    is_dev: bool = False
    is_optional: bool = False


@dataclass
class SecurityVulnerability:
    """Information about a security vulnerability."""
    package: str
    installed_version: str
    vulnerability_id: str
    description: str
    fixed_version: Optional[str] = None


class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes external dependencies for security, conflicts, and usage."""
    
    def __init__(self, config):
        super().__init__(config)
        self.dependencies: Dict[str, List[DependencyInfo]] = {}
        self.all_dependencies: Set[str] = set()
        self.security_vulnerabilities: List[SecurityVulnerability] = []
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Dependency Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Analyze dependencies in the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Parse all dependency files
            self._parse_dependency_files(project_root)
            
            # Analyze for various issues
            results.extend(self._check_security_vulnerabilities())
            results.extend(self._check_version_conflicts())
            results.extend(self._check_unused_dependencies(project_root))
            results.extend(self._check_outdated_dependencies())
            results.extend(self._check_dependency_consistency())
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze dependencies: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _parse_dependency_files(self, project_root: Path) -> None:
        """Parse all dependency files in the project."""
        # Find all pyproject.toml files
        for toml_file in project_root.rglob('pyproject.toml'):
            if self.should_analyze_file(toml_file):
                self._parse_pyproject_toml(toml_file)
        
        # Find all requirements.txt files
        for req_file in project_root.rglob('requirements.txt'):
            if self.should_analyze_file(req_file):
                self._parse_requirements_txt(req_file)
        
        # Also check for other common requirement files
        for pattern in ['requirements-*.txt', 'dev-requirements.txt', '*requirements.txt']:
            for req_file in project_root.rglob(pattern):
                if self.should_analyze_file(req_file) and req_file.name != 'requirements.txt':
                    self._parse_requirements_txt(req_file)
    
    def _parse_pyproject_toml(self, toml_file: Path) -> None:
        """Parse a pyproject.toml file for dependencies."""
        try:
            with open(toml_file, 'rb') as f:
                data = tomllib.load(f)
            
            # Use absolute path or relative to project root instead of cwd
            try:
                project_root = Path(self.config.project_path).resolve()
                source_file = str(toml_file.relative_to(project_root))
            except ValueError:
                # If file is outside project root, use absolute path
                source_file = str(toml_file)
            
            # Parse main dependencies
            if 'project' in data and 'dependencies' in data['project']:
                for dep in data['project']['dependencies']:
                    dep_info = self._parse_dependency_string(dep, source_file)
                    if dep_info:
                        self._add_dependency(dep_info)
            
            # Parse optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group_name, deps in data['project']['optional-dependencies'].items():
                    for dep in deps:
                        dep_info = self._parse_dependency_string(dep, source_file)
                        if dep_info:
                            dep_info.is_optional = True
                            dep_info.is_dev = group_name in ['dev', 'development', 'test', 'testing']
                            self._add_dependency(dep_info)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(toml_file),
                error=f"Failed to parse pyproject.toml: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _parse_requirements_txt(self, req_file: Path) -> None:
        """Parse a requirements.txt file for dependencies."""
        try:
            # Пробуем сначала с UTF-8
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Если UTF-8 не работает, пробуем с другими кодировками
                try:
                    with open(req_file, 'r', encoding='latin-1') as f:
                        lines = f.readlines()
                except UnicodeDecodeError:
                    # Если и это не работает, используем binary mode и игнорируем ошибки
                    with open(req_file, 'rb') as f:
                        lines = [line.decode('utf-8', errors='ignore') for line in f.readlines()]
            
            # Use absolute path or relative to project root instead of cwd
            try:
                project_root = Path(self.config.project_path).resolve()
                source_file = str(req_file.relative_to(project_root))
            except ValueError:
                # If file is outside project root, use absolute path
                source_file = str(req_file)
            is_dev = 'dev' in req_file.name.lower() or 'test' in req_file.name.lower()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Skip editable installs and URLs for now
                if line.startswith('-e') or line.startswith('http'):
                    continue
                
                dep_info = self._parse_dependency_string(line, source_file, line_num)
                if dep_info:
                    dep_info.is_dev = is_dev
                    self._add_dependency(dep_info)
                    
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(req_file),
                error=f"Failed to parse requirements.txt: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _parse_dependency_string(self, dep_string: str, source_file: str, line_number: Optional[int] = None) -> Optional[DependencyInfo]:
        """Parse a dependency string into DependencyInfo."""
        try:
            # Clean up the dependency string
            dep_string = dep_string.strip()
            
            # Handle comments
            if '#' in dep_string:
                dep_string = dep_string.split('#')[0].strip()
            
            if not dep_string:
                return None
            
            # Parse using packaging library
            req = Requirement(dep_string)
            
            return DependencyInfo(
                name=req.name.lower(),
                version_spec=str(req.specifier) if req.specifier else "",
                source_file=source_file,
                line_number=line_number
            )
            
        except InvalidRequirement as e:
            # Log but don't fail - some dependency strings might be complex
            self.logger.debug(f"Could not parse dependency '{dep_string}' in {source_file}: {e}")
            return None
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=source_file,
                error=f"Failed to parse dependency string '{dep_string}': {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
            return None
    
    def _add_dependency(self, dep_info: DependencyInfo) -> None:
        """Add a dependency to the tracking collections."""
        if dep_info.name not in self.dependencies:
            self.dependencies[dep_info.name] = []
        
        self.dependencies[dep_info.name].append(dep_info)
        self.all_dependencies.add(dep_info.name)
    
    def _check_security_vulnerabilities(self) -> List[AnalysisResult]:
        """Check for security vulnerabilities using pip-audit."""
        results = []
        
        try:
            # Try to run pip-audit
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'list', '--format=json'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                installed_packages = json.loads(result.stdout)
                installed_dict = {pkg['name'].lower(): pkg['version'] for pkg in installed_packages}
                
                # Check if pip-audit is available
                try:
                    audit_result = subprocess.run([
                        sys.executable, '-m', 'pip_audit', '--format=json'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if audit_result.returncode == 0:
                        vulnerabilities = json.loads(audit_result.stdout)
                        
                        for vuln in vulnerabilities:
                            package_name = vuln.get('name', '').lower()
                            if package_name in self.all_dependencies:
                                results.append(AnalysisResult(
                                    category="security",
                                    severity="high",
                                    description=f"Security vulnerability in {package_name}: {vuln.get('description', 'Unknown vulnerability')}",
                                    file_path="dependencies",
                                    recommendation=f"Update {package_name} to version {vuln.get('fix_versions', ['latest'])[0] if vuln.get('fix_versions') else 'latest'}"
                                ))
                    
                except FileNotFoundError:
                    # pip-audit not installed, suggest installation
                    results.append(AnalysisResult(
                        category="security",
                        severity="medium",
                        description="pip-audit not available for security vulnerability scanning",
                        file_path="dependencies",
                        recommendation="Install pip-audit with: pip install pip-audit"
                    ))
                
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path="dependencies",
                error=f"Failed to check security vulnerabilities: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _check_version_conflicts(self) -> List[AnalysisResult]:
        """Check for version conflicts between different modules."""
        results = []
        
        # Group dependencies by name and check for conflicts
        for dep_name, dep_list in self.dependencies.items():
            if len(dep_list) > 1:
                # Check if there are conflicting version specifications
                version_specs = set()
                source_files = []
                
                for dep in dep_list:
                    if dep.version_spec:
                        version_specs.add(dep.version_spec)
                    source_files.append(dep.source_file)
                
                if len(version_specs) > 1:
                    results.append(AnalysisResult(
                        category="version_conflict",
                        severity="high",
                        description=f"Version conflict for {dep_name}: {', '.join(version_specs)} in files: {', '.join(set(source_files))}",
                        file_path=", ".join(set(source_files)),
                        recommendation=f"Standardize version specification for {dep_name} across all dependency files"
                    ))
        
        return results
    
    def _check_unused_dependencies(self, project_root: Path) -> List[AnalysisResult]:
        """Check for potentially unused dependencies."""
        results = []
        
        try:
            # Get all Python files in the project
            python_files = self.get_project_files(str(project_root), ['.py'])
            
            # Extract all import statements
            imported_modules = set()
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find import statements
                    import_patterns = [
                        r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                        r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
                    ]
                    
                    for pattern in import_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        imported_modules.update(matches)
                
                except Exception as e:
                    # Skip files that can't be read
                    continue
            
            # Check which dependencies might be unused
            potentially_unused = []
            
            for dep_name in self.all_dependencies:
                # Skip some common packages that might not be directly imported
                skip_packages = {
                    'setuptools', 'wheel', 'pip', 'build', 'twine',
                    'pytest', 'black', 'isort', 'flake8', 'mypy'
                }
                
                if dep_name in skip_packages:
                    continue
                
                # Check if the package name or common variations are imported
                variations = [
                    dep_name,
                    dep_name.replace('-', '_'),
                    dep_name.replace('_', '-'),
                    dep_name.split('-')[0] if '-' in dep_name else dep_name,
                    dep_name.split('_')[0] if '_' in dep_name else dep_name
                ]
                
                if not any(var in imported_modules for var in variations):
                    potentially_unused.append(dep_name)
            
            # Report potentially unused dependencies
            for dep_name in potentially_unused:
                dep_sources = [dep.source_file for dep in self.dependencies[dep_name]]
                results.append(AnalysisResult(
                    category="unused_dependency",
                    severity="medium",
                    description=f"Potentially unused dependency: {dep_name}",
                    file_path=", ".join(set(dep_sources)),
                    recommendation=f"Verify if {dep_name} is actually needed and remove if unused"
                ))
        
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to check unused dependencies: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _check_outdated_dependencies(self) -> List[AnalysisResult]:
        """Check for outdated dependencies."""
        results = []
        
        try:
            # Get list of outdated packages
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                outdated_packages = json.loads(result.stdout)
                
                for pkg in outdated_packages:
                    pkg_name = pkg['name'].lower()
                    if pkg_name in self.all_dependencies:
                        current_version = pkg['version']
                        latest_version = pkg['latest_version']
                        
                        # Determine severity based on version difference
                        try:
                            current_ver = version.parse(current_version)
                            latest_ver = version.parse(latest_version)
                            
                            # Major version difference = high severity
                            if latest_ver.major > current_ver.major:
                                severity = "high"
                            # Minor version difference = medium severity
                            elif latest_ver.minor > current_ver.minor:
                                severity = "medium"
                            else:
                                severity = "low"
                        except:
                            severity = "medium"
                        
                        dep_sources = [dep.source_file for dep in self.dependencies[pkg_name]]
                        results.append(AnalysisResult(
                            category="outdated_dependency",
                            severity=severity,
                            description=f"Outdated dependency: {pkg_name} {current_version} (latest: {latest_version})",
                            file_path=", ".join(set(dep_sources)),
                            recommendation=f"Consider updating {pkg_name} to version {latest_version}"
                        ))
        
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path="dependencies",
                error=f"Failed to check outdated dependencies: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return results
    
    def _check_dependency_consistency(self) -> List[AnalysisResult]:
        """Check for dependency consistency issues."""
        results = []
        
        # Check for missing dependencies in some modules
        all_source_files = set()
        for dep_list in self.dependencies.values():
            for dep in dep_list:
                all_source_files.add(dep.source_file)
        
        # Group dependencies by source file
        deps_by_file = {}
        for dep_name, dep_list in self.dependencies.items():
            for dep in dep_list:
                if dep.source_file not in deps_by_file:
                    deps_by_file[dep.source_file] = set()
                deps_by_file[dep.source_file].add(dep_name)
        
        # Check for common dependencies that might be missing in some files
        common_deps = {'pyside6', 'requests', 'python-dotenv'}
        
        for source_file, file_deps in deps_by_file.items():
            missing_common = common_deps - file_deps
            if missing_common and 'pyproject.toml' in source_file:
                for missing_dep in missing_common:
                    if missing_dep in self.all_dependencies:  # It exists in other files
                        results.append(AnalysisResult(
                            category="dependency_consistency",
                            severity="medium",
                            description=f"Common dependency {missing_dep} missing from {source_file}",
                            file_path=source_file,
                            recommendation=f"Consider adding {missing_dep} to {source_file} if needed"
                        ))
        
        return results


if __name__ == "__main__":
    # Test the DependencyAnalyzer
    import sys
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = DependencyAnalyzer(config)
        
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
            for result in category_results:
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    Recommendation: {result.recommendation}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)