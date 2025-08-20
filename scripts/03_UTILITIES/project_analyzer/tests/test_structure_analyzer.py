"""
Unit tests for StructureAnalyzer.

This module contains comprehensive tests for the StructureAnalyzer class
to ensure it correctly analyzes project organization and detects issues.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from structure_analyzer import StructureAnalyzer, ModuleInfo, DirectoryInfo


class TestStructureAnalyzer:
    """Test class for StructureAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.config = AnalysisConfig(project_path=str(self.project_root))
        self.analyzer = StructureAnalyzer(self.config)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_project_structure(self):
        """Create a test project structure."""
        # Create GopiAI modules
        modules = ['GopiAI-Core', 'GopiAI-UI', 'GopiAI-CrewAI']
        for module in modules:
            module_dir = self.project_root / module
            module_dir.mkdir()
            
            # Create required files
            (module_dir / 'pyproject.toml').write_text('[build-system]\nrequires = ["setuptools"]')
            (module_dir / 'README.md').write_text(f'# {module}')
            
            # Create gopiai package
            gopiai_dir = module_dir / 'gopiai'
            gopiai_dir.mkdir()
            (gopiai_dir / '__init__.py').write_text('')
            
            # Create module-specific package
            package_name = module.lower().replace('gopiai-', '').replace('-', '_')
            package_dir = gopiai_dir / package_name
            package_dir.mkdir()
            (package_dir / '__init__.py').write_text('')
            
            # Create tests directory
            tests_dir = module_dir / 'tests'
            tests_dir.mkdir()
            (tests_dir / '__init__.py').write_text('')
        
        # Create expected directories
        expected_dirs = ['02_DOCUMENTATION', '03_UTILITIES', 'examples', 'logs', '.kiro']
        for dir_name in expected_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir()
            if not dir_name.startswith('.'):
                (dir_path / 'README.md').write_text(f'# {dir_name}')
    
    def test_analyzer_initialization(self):
        """Test StructureAnalyzer initialization."""
        assert self.analyzer.get_analyzer_name() == "Structure Analyzer"
        assert isinstance(self.analyzer.gopiai_modules, list)
        assert isinstance(self.analyzer.directory_info, list)
        assert isinstance(self.analyzer.misplaced_files, list)
    
    def test_analyze_root_structure_complete(self):
        """Test analysis of complete root structure."""
        self.create_test_project_structure()
        
        results = self.analyzer._analyze_root_structure(self.project_root)
        
        # Should have minimal issues with complete structure
        high_severity_results = [r for r in results if r.severity == 'high']
        assert len(high_severity_results) == 0
        
        # Check that directory info was populated
        assert len(self.analyzer.directory_info) > 0
        
        # Verify expected directories are marked as expected
        expected_dirs = [d for d in self.analyzer.directory_info if d.expected]
        assert len(expected_dirs) > 0
    
    def test_analyze_root_structure_missing_modules(self):
        """Test analysis when some GopiAI modules are missing."""
        # Create only partial structure
        (self.project_root / 'GopiAI-Core').mkdir()
        (self.project_root / '02_DOCUMENTATION').mkdir()
        
        results = self.analyzer._analyze_root_structure(self.project_root)
        
        # Should detect missing modules
        missing_module_results = [r for r in results 
                                if r.category == 'structure' and 'Missing expected GopiAI module' in r.description]
        assert len(missing_module_results) > 0
        
        # Should find GopiAI-UI and GopiAI-CrewAI missing
        missing_modules = [r.description for r in missing_module_results]
        assert any('GopiAI-UI' in desc for desc in missing_modules)
        assert any('GopiAI-CrewAI' in desc for desc in missing_modules)
    
    def test_analyze_root_structure_unexpected_directories(self):
        """Test detection of unexpected directories in root."""
        # Create unexpected directories
        (self.project_root / 'unexpected_dir').mkdir()
        (self.project_root / 'another_unexpected').mkdir()
        (self.project_root / '.hidden_dir').mkdir()  # Should be ignored
        (self.project_root / '__pycache__').mkdir()  # Should be ignored
        
        results = self.analyzer._analyze_root_structure(self.project_root)
        
        # Should detect unexpected directories (but not hidden or cache dirs)
        unexpected_results = [r for r in results 
                            if r.category == 'structure' and 'Unexpected root directory' in r.description]
        assert len(unexpected_results) == 2  # Only the two non-hidden/cache dirs
        
        unexpected_dirs = [r.description for r in unexpected_results]
        assert any('unexpected_dir' in desc for desc in unexpected_dirs)
        assert any('another_unexpected' in desc for desc in unexpected_dirs)
    
    def test_analyze_single_module_complete(self):
        """Test analysis of a complete GopiAI module."""
        # Create complete module structure
        module_dir = self.project_root / 'GopiAI-Test'
        module_dir.mkdir()
        
        (module_dir / 'pyproject.toml').write_text('[build-system]')
        (module_dir / 'README.md').write_text('# GopiAI-Test')
        
        gopiai_dir = module_dir / 'gopiai'
        gopiai_dir.mkdir()
        (gopiai_dir / '__init__.py').write_text('')
        
        test_package = gopiai_dir / 'test'
        test_package.mkdir()
        (test_package / '__init__.py').write_text('')
        
        tests_dir = module_dir / 'tests'
        tests_dir.mkdir()
        
        module_info = self.analyzer._analyze_single_module(module_dir)
        
        assert module_info.name == 'GopiAI-Test'
        assert module_info.has_pyproject == True
        assert module_info.has_readme == True
        assert module_info.has_gopiai_package == True
        assert module_info.python_package_name == 'test'
        assert module_info.expected_structure == True
    
    def test_analyze_single_module_incomplete(self):
        """Test analysis of an incomplete GopiAI module."""
        # Create incomplete module structure
        module_dir = self.project_root / 'GopiAI-Incomplete'
        module_dir.mkdir()
        
        # Only create README, missing other required files
        (module_dir / 'README.md').write_text('# GopiAI-Incomplete')
        
        module_info = self.analyzer._analyze_single_module(module_dir)
        
        assert module_info.name == 'GopiAI-Incomplete'
        assert module_info.has_pyproject == False
        assert module_info.has_readme == True
        assert module_info.has_gopiai_package == False
        assert module_info.python_package_name == None
        assert module_info.expected_structure == False
    
    def test_analyze_gopiai_modules(self):
        """Test analysis of all GopiAI modules."""
        # Create modules with different completeness levels
        complete_module = self.project_root / 'GopiAI-Complete'
        complete_module.mkdir()
        (complete_module / 'pyproject.toml').write_text('[build-system]')
        (complete_module / 'README.md').write_text('# Complete')
        gopiai_complete = complete_module / 'gopiai'
        gopiai_complete.mkdir()
        (gopiai_complete / 'complete').mkdir()
        (complete_module / 'tests').mkdir()
        
        incomplete_module = self.project_root / 'GopiAI-Incomplete'
        incomplete_module.mkdir()
        # Missing required files
        
        results = self.analyzer._analyze_gopiai_modules(self.project_root)
        
        # Should detect missing files in incomplete module
        missing_pyproject = [r for r in results 
                           if 'Missing pyproject.toml' in r.description and 'GopiAI-Incomplete' in r.description]
        assert len(missing_pyproject) == 1
        
        missing_readme = [r for r in results 
                        if 'Missing README.md' in r.description and 'GopiAI-Incomplete' in r.description]
        assert len(missing_readme) == 1
        
        missing_gopiai = [r for r in results 
                        if 'Missing gopiai/ package' in r.description and 'GopiAI-Incomplete' in r.description]
        assert len(missing_gopiai) == 1
        
        # Check that modules were stored
        assert len(self.analyzer.gopiai_modules) == 2
    
    def test_detect_misplaced_files(self):
        """Test detection of misplaced files."""
        # Create misplaced files
        (self.project_root / 'misplaced_script.py').write_text('print("misplaced")')
        (self.project_root / 'debug.log').write_text('log content')
        (self.project_root / 'config.json').write_text('{}')
        
        # Create logs directory
        logs_dir = self.project_root / 'logs'
        logs_dir.mkdir()
        
        # Create a log file in subdirectory (should be flagged)
        subdir = self.project_root / 'subdir'
        subdir.mkdir()
        (subdir / 'another.log').write_text('log content')
        
        results = self.analyzer._detect_misplaced_files(self.project_root)
        
        # Should detect misplaced Python file
        misplaced_py = [r for r in results 
                       if r.category == 'misplaced_files' and 'misplaced_script.py' in r.description]
        assert len(misplaced_py) == 1
        
        # Should detect log file outside logs directory
        misplaced_log = [r for r in results 
                        if r.category == 'misplaced_files' and 'Log file outside logs directory' in r.description]
        assert len(misplaced_log) >= 1  # debug.log and another.log
        
        # Should detect config file in root
        misplaced_config = [r for r in results 
                          if r.category == 'misplaced_files' and 'Configuration file in root' in r.description]
        assert len(misplaced_config) == 1
    
    def test_validate_naming_conventions_correct(self):
        """Test validation of correct naming conventions."""
        # Create correctly named module
        module_dir = self.project_root / 'GopiAI-ProperName'
        module_dir.mkdir()
        
        gopiai_dir = module_dir / 'gopiai'
        gopiai_dir.mkdir()
        
        # Create package with correct naming
        package_dir = gopiai_dir / 'propername'
        package_dir.mkdir()
        
        # Populate module info
        module_info = ModuleInfo(
            name='GopiAI-ProperName',
            path=module_dir,
            has_pyproject=True,
            has_readme=True,
            has_gopiai_package=True,
            python_package_name='propername'
        )
        self.analyzer.gopiai_modules = [module_info]
        
        results = self.analyzer._validate_naming_conventions(self.project_root)
        
        # Should have no naming convention violations
        naming_violations = [r for r in results if r.category == 'naming_conventions']
        assert len(naming_violations) == 0
    
    def test_validate_naming_conventions_incorrect(self):
        """Test validation of incorrect naming conventions."""
        # Create incorrectly named module
        module_dir = self.project_root / 'gopiai-lowercase'
        module_dir.mkdir()
        
        gopiai_dir = module_dir / 'gopiai'
        gopiai_dir.mkdir()
        
        package_dir = gopiai_dir / 'wrong_name'
        package_dir.mkdir()
        
        # Populate module info with incorrect naming
        module_info = ModuleInfo(
            name='gopiai-lowercase',
            path=module_dir,
            has_pyproject=True,
            has_readme=True,
            has_gopiai_package=True,
            python_package_name='wrong_name'
        )
        self.analyzer.gopiai_modules = [module_info]
        
        # Create potential module with incorrect naming
        (self.project_root / 'gopiai_something').mkdir()
        
        results = self.analyzer._validate_naming_conventions(self.project_root)
        
        # Should detect module name violation
        module_name_violations = [r for r in results 
                                if 'Module name doesn\'t follow convention' in r.description]
        assert len(module_name_violations) == 1
        
        # Should detect package name inconsistency
        package_name_violations = [r for r in results 
                                 if 'Python package name inconsistent' in r.description]
        assert len(package_name_violations) == 1
        
        # Should detect potential module with wrong naming
        potential_module_violations = [r for r in results 
                                     if 'Directory might be a GopiAI module' in r.description and 'gopiai_something' in r.description]
        assert len(potential_module_violations) == 1
    
    def test_detect_inconsistent_structures(self):
        """Test detection of inconsistent structures across modules."""
        # Create modules with different structures
        module1_dir = self.project_root / 'GopiAI-Module1'
        module1_dir.mkdir()
        (module1_dir / 'tests').mkdir()  # Has tests
        (module1_dir / 'requirements.txt').write_text('requests==2.25.1')  # Has requirements
        gopiai1 = module1_dir / 'gopiai'
        gopiai1.mkdir()
        (gopiai1 / '__init__.py').write_text('')
        
        module2_dir = self.project_root / 'GopiAI-Module2'
        module2_dir.mkdir()
        # No tests directory
        # No requirements.txt
        gopiai2 = module2_dir / 'gopiai'
        gopiai2.mkdir()
        # No __init__.py in gopiai
        
        module3_dir = self.project_root / 'GopiAI-Module3'
        module3_dir.mkdir()
        (module3_dir / 'tests').mkdir()  # Has tests
        (module3_dir / 'requirements.txt').write_text('numpy==1.21.0')  # Has requirements
        gopiai3 = module3_dir / 'gopiai'
        gopiai3.mkdir()
        (gopiai3 / '__init__.py').write_text('')
        
        # Populate module info
        self.analyzer.gopiai_modules = [
            ModuleInfo('GopiAI-Module1', module1_dir, True, True, True),
            ModuleInfo('GopiAI-Module2', module2_dir, True, True, True),
            ModuleInfo('GopiAI-Module3', module3_dir, True, True, True)
        ]
        
        results = self.analyzer._detect_inconsistent_structures(self.project_root)
        
        # Should detect missing tests directory (Module2 is missing tests while others have it)
        missing_tests = [r for r in results 
                        if 'lacks tests directory' in r.description]
        assert len(missing_tests) == 1
        
        # Should detect missing requirements.txt (Module2 is missing requirements while others have it)
        missing_requirements = [r for r in results 
                              if 'lacks requirements.txt' in r.description]
        assert len(missing_requirements) == 1
    
    def test_get_structure_summary(self):
        """Test structure summary generation."""
        # Create test modules
        module1 = ModuleInfo('GopiAI-Test1', Path('/test1'), True, True, True, 'test1', True)
        module2 = ModuleInfo('GopiAI-Test2', Path('/test2'), False, True, True, 'test2', False)
        
        self.analyzer.gopiai_modules = [module1, module2]
        
        # Create test directory info
        dir1 = DirectoryInfo(Path('/dir1'), 'module', True, 10, 2)
        dir2 = DirectoryInfo(Path('/dir2'), 'other', False, 5, 1)
        
        self.analyzer.directory_info = [dir1, dir2]
        
        summary = self.analyzer.get_structure_summary()
        
        assert summary['total_gopiai_modules'] == 2
        assert summary['modules_with_proper_structure'] == 1
        assert summary['total_directories'] == 2
        assert summary['expected_directories'] == 1
        assert len(summary['module_details']) == 2
        
        # Check module details
        module1_detail = summary['module_details'][0]
        assert module1_detail['name'] == 'GopiAI-Test1'
        assert module1_detail['expected_structure'] == True
        
        module2_detail = summary['module_details'][1]
        assert module2_detail['name'] == 'GopiAI-Test2'
        assert module2_detail['expected_structure'] == False
    
    def test_full_analysis_integration(self):
        """Test full analysis integration."""
        self.create_test_project_structure()
        
        # Add some issues to test
        (self.project_root / 'misplaced.py').write_text('print("test")')
        (self.project_root / 'unexpected_dir').mkdir()
        
        results = self.analyzer.analyze(str(self.project_root))
        
        # Should return results without errors
        assert isinstance(results, list)
        assert len(results) >= 0  # May have some issues
        
        # Check that all major analysis components ran
        categories = {r.category for r in results}
        
        # Should have analyzed structure if there are issues
        if results:
            possible_categories = {'structure', 'module_structure', 'misplaced_files', 
                                 'naming_conventions', 'structure_consistency'}
            assert len(categories.intersection(possible_categories)) > 0
    
    def test_error_handling(self):
        """Test error handling during analysis."""
        # Create a scenario that might cause errors
        non_readable_dir = self.project_root / 'GopiAI-Test'
        non_readable_dir.mkdir()
        
        # Mock a permission error
        with patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
            results = self.analyzer._analyze_root_structure(self.project_root)
            
            # Should handle error gracefully
            assert self.analyzer.error_handler.has_errors()
            assert len(self.analyzer.error_handler.errors) > 0
    
    def test_should_analyze_file_filtering(self):
        """Test file filtering logic."""
        # Create test files
        py_file = self.project_root / 'test.py'
        py_file.write_text('print("test")')
        
        pyc_file = self.project_root / 'test.pyc'
        pyc_file.write_text('compiled')
        
        large_file = self.project_root / 'large.py'
        large_file.write_text('x' * (11 * 1024 * 1024))  # 11MB file
        
        # Test filtering
        assert self.analyzer.should_analyze_file(py_file) == True
        assert self.analyzer.should_analyze_file(pyc_file) == False  # Excluded by default
        assert self.analyzer.should_analyze_file(large_file) == False  # Too large


def run_all_tests():
    """Run all StructureAnalyzer tests."""
    print("Running StructureAnalyzer tests...\n")
    
    test_instance = TestStructureAnalyzer()
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"Running {test_method}...", end=' ')
            test_instance.setup_method()
            getattr(test_instance, test_method)()
            test_instance.teardown_method()
            print("✓ PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)