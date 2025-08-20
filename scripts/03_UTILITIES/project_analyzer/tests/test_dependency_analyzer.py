"""
Unit tests for DependencyAnalyzer

Tests the dependency analysis functionality including parsing of pyproject.toml
and requirements.txt files, security vulnerability detection, version conflict
detection, and unused dependency detection.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import subprocess

from dependency_analyzer import DependencyAnalyzer, DependencyInfo, SecurityVulnerability
from project_cleanup_analyzer import AnalysisConfig, AnalysisResult


class TestDependencyAnalyzer:
    """Test cases for DependencyAnalyzer."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create sample pyproject.toml
            pyproject_content = """
[project]
name = "test-project"
dependencies = [
    "requests>=2.25.0",
    "pyside6==6.7.3",
    "python-dotenv"
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black",
    "isort"
]
test = [
    "pytest-qt",
    "coverage"
]
"""
            (project_path / "pyproject.toml").write_text(pyproject_content)
            
            # Create sample requirements.txt
            requirements_content = """
# Main dependencies
requests>=2.25.0
pyside6==6.7.3
python-dotenv

# Optional
numpy==1.21.0  # For data processing
"""
            (project_path / "requirements.txt").write_text(requirements_content)
            
            # Create dev-requirements.txt
            dev_requirements_content = """
pytest>=6.0.0
black
isort
flake8
"""
            (project_path / "dev-requirements.txt").write_text(dev_requirements_content)
            
            # Create some Python files with imports
            (project_path / "main.py").write_text("""
import requests
import sys
from pyside6 import QtWidgets
from dotenv import load_dotenv
""")
            
            (project_path / "test_file.py").write_text("""
import pytest
import numpy as np
""")
            
            yield project_path
    
    @pytest.fixture
    def analyzer(self, temp_project):
        """Create a DependencyAnalyzer instance for testing."""
        config = AnalysisConfig(project_path=str(temp_project))
        return DependencyAnalyzer(config)
    
    def test_analyzer_name(self, analyzer):
        """Test that analyzer returns correct name."""
        assert analyzer.get_analyzer_name() == "Dependency Analyzer"
    
    def test_parse_pyproject_toml(self, analyzer, temp_project):
        """Test parsing of pyproject.toml files."""
        analyzer._parse_dependency_files(temp_project)
        
        # Check that dependencies were parsed
        assert "requests" in analyzer.dependencies
        assert "pyside6" in analyzer.dependencies
        assert "python-dotenv" in analyzer.dependencies
        assert "pytest" in analyzer.dependencies
        assert "black" in analyzer.dependencies
        
        # Check dependency details
        requests_deps = analyzer.dependencies["requests"]
        assert len(requests_deps) > 0
        assert any(dep.version_spec == ">=2.25.0" for dep in requests_deps)
        
        # Check dev dependencies
        pytest_deps = analyzer.dependencies["pytest"]
        dev_deps = [dep for dep in pytest_deps if dep.is_dev]
        assert len(dev_deps) > 0
    
    def test_parse_requirements_txt(self, analyzer, temp_project):
        """Test parsing of requirements.txt files."""
        analyzer._parse_dependency_files(temp_project)
        
        # Check that dependencies from requirements.txt were parsed
        assert "requests" in analyzer.dependencies
        assert "numpy" in analyzer.dependencies
        
        # Check that dev dependencies are marked correctly
        flake8_deps = analyzer.dependencies.get("flake8", [])
        if flake8_deps:
            assert any(dep.is_dev for dep in flake8_deps)
    
    def test_dependency_string_parsing(self, analyzer):
        """Test parsing of individual dependency strings."""
        # Test simple dependency
        dep = analyzer._parse_dependency_string("requests", "test.txt")
        assert dep.name == "requests"
        assert dep.version_spec == ""
        
        # Test dependency with version
        dep = analyzer._parse_dependency_string("requests>=2.25.0", "test.txt")
        assert dep.name == "requests"
        assert dep.version_spec == ">=2.25.0"
        
        # Test dependency with comment
        dep = analyzer._parse_dependency_string("requests>=2.25.0  # HTTP library", "test.txt")
        assert dep.name == "requests"
        assert dep.version_spec == ">=2.25.0"
        
        # Test invalid dependency
        dep = analyzer._parse_dependency_string("invalid>>dependency", "test.txt")
        assert dep is None
    
    def test_version_conflict_detection(self, analyzer, temp_project):
        """Test detection of version conflicts."""
        # Add conflicting dependency files
        conflict_toml = temp_project / "module1" / "pyproject.toml"
        conflict_toml.parent.mkdir()
        conflict_toml.write_text("""
[project]
dependencies = ["requests>=3.0.0"]
""")
        
        analyzer._parse_dependency_files(temp_project)
        results = analyzer._check_version_conflicts()
        
        # Should detect conflict between requests>=2.25.0 and requests>=3.0.0
        conflict_results = [r for r in results if r.category == "version_conflict"]
        assert len(conflict_results) > 0
        assert any("requests" in r.description for r in conflict_results)
    
    @patch('subprocess.run')
    def test_security_vulnerability_detection(self, mock_run, analyzer, temp_project):
        """Test security vulnerability detection."""
        # Mock pip list output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps([
            {"name": "requests", "version": "2.25.0"},
            {"name": "pyside6", "version": "6.7.3"}
        ])
        
        analyzer._parse_dependency_files(temp_project)
        
        # Mock pip-audit not available
        with patch('subprocess.run') as mock_audit:
            mock_audit.side_effect = [
                MagicMock(returncode=0, stdout=json.dumps([
                    {"name": "requests", "version": "2.25.0"}
                ])),
                FileNotFoundError()
            ]
            
            results = analyzer._check_security_vulnerabilities()
            
            # Should suggest installing pip-audit
            audit_results = [r for r in results if "pip-audit" in r.description]
            assert len(audit_results) > 0
    
    @patch('subprocess.run')
    def test_outdated_dependency_detection(self, mock_run, analyzer, temp_project):
        """Test detection of outdated dependencies."""
        # Mock pip list --outdated output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps([
            {
                "name": "requests",
                "version": "2.25.0",
                "latest_version": "2.28.0"
            }
        ])
        
        analyzer._parse_dependency_files(temp_project)
        results = analyzer._check_outdated_dependencies()
        
        # Should detect outdated requests
        outdated_results = [r for r in results if r.category == "outdated_dependency"]
        assert len(outdated_results) > 0
        assert any("requests" in r.description for r in outdated_results)
    
    def test_unused_dependency_detection(self, analyzer, temp_project):
        """Test detection of potentially unused dependencies."""
        analyzer._parse_dependency_files(temp_project)
        results = analyzer._check_unused_dependencies(temp_project)
        
        # Should detect some unused dependencies
        unused_results = [r for r in results if r.category == "unused_dependency"]
        
        # black, isort, flake8 might be detected as unused since they're not imported
        unused_names = [r.description for r in unused_results]
        assert any("black" in desc or "isort" in desc for desc in unused_names)
    
    def test_dependency_consistency_check(self, analyzer, temp_project):
        """Test dependency consistency checking."""
        analyzer._parse_dependency_files(temp_project)
        results = analyzer._check_dependency_consistency()
        
        # Results depend on the specific dependencies found
        consistency_results = [r for r in results if r.category == "dependency_consistency"]
        # This test mainly ensures the method runs without errors
        assert isinstance(consistency_results, list)
    
    def test_full_analysis(self, analyzer, temp_project):
        """Test full dependency analysis."""
        results = analyzer.analyze(str(temp_project))
        
        # Should return a list of AnalysisResult objects
        assert isinstance(results, list)
        assert all(isinstance(r, AnalysisResult) for r in results)
        
        # Should have various categories of results
        categories = {r.category for r in results}
        expected_categories = {
            "version_conflict", "unused_dependency", "outdated_dependency",
            "dependency_consistency", "security"
        }
        
        # At least some categories should be present
        assert len(categories.intersection(expected_categories)) > 0
    
    def test_error_handling(self, analyzer):
        """Test error handling for invalid project paths."""
        # Test with non-existent path
        results = analyzer.analyze("/non/existent/path")
        
        # Should handle errors gracefully
        assert isinstance(results, list)
        assert analyzer.error_handler.has_errors()
    
    def test_dependency_info_dataclass(self):
        """Test DependencyInfo dataclass."""
        dep = DependencyInfo(
            name="requests",
            version_spec=">=2.25.0",
            source_file="requirements.txt",
            line_number=1,
            is_dev=False,
            is_optional=True
        )
        
        assert dep.name == "requests"
        assert dep.version_spec == ">=2.25.0"
        assert dep.source_file == "requirements.txt"
        assert dep.line_number == 1
        assert not dep.is_dev
        assert dep.is_optional
    
    def test_security_vulnerability_dataclass(self):
        """Test SecurityVulnerability dataclass."""
        vuln = SecurityVulnerability(
            package="requests",
            installed_version="2.25.0",
            vulnerability_id="CVE-2023-1234",
            description="Test vulnerability",
            fixed_version="2.26.0"
        )
        
        assert vuln.package == "requests"
        assert vuln.installed_version == "2.25.0"
        assert vuln.vulnerability_id == "CVE-2023-1234"
        assert vuln.description == "Test vulnerability"
        assert vuln.fixed_version == "2.26.0"


if __name__ == "__main__":
    pytest.main([__file__])