"""
Unit tests for DeadCodeAnalyzer.

This module contains comprehensive tests for the DeadCodeAnalyzer class
to ensure it correctly identifies unused code and commented-out code blocks.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import ast

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from dead_code_analyzer import DeadCodeAnalyzer, UnusedCode, ImportVisitor, NameVisitor


class TestDeadCodeAnalyzer:
    """Test class for DeadCodeAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.config = AnalysisConfig(project_path=str(self.project_root))
        self.analyzer = DeadCodeAnalyzer(self.config)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_python_file(self, file_name, content):
        """Create a test Python file with the given content."""
        file_path = self.project_root / file_name
        file_path.write_text(content)
        return file_path
    
    def test_analyzer_initialization(self):
        """Test DeadCodeAnalyzer initialization."""
        assert self.analyzer.get_analyzer_name() == "Dead Code Analyzer"
        assert isinstance(self.analyzer.unused_code, list)
        assert isinstance(self.analyzer.module_imports, dict)
        assert isinstance(self.analyzer.module_references, dict)
    
    def test_check_tool_available(self):
        """Test checking if external tools are available."""
        # Mock subprocess.run to simulate tool availability
        with patch('subprocess.run') as mock_run:
            # Tool is available
            mock_run.return_value = MagicMock(returncode=0)
            assert self.analyzer._check_tool_available('available_tool') == True
            
            # Tool is not available
            mock_run.return_value = MagicMock(returncode=1)
            assert self.analyzer._check_tool_available('unavailable_tool') == False
            
            # Tool check raises exception
            mock_run.side_effect = FileNotFoundError("Command failed")
            assert self.analyzer._check_tool_available('error_tool') == False
    
    def test_run_vulture(self):
        """Test running vulture for dead code detection."""
        # Create a test file with unused code
        test_content = """
def used_function():
    return 1

def unused_function():
    return 2

class UsedClass:
    def method(self):
        return used_function()

class UnusedClass:
    def method(self):
        return 3

used_var = 1
unused_var = 2

def main():
    obj = UsedClass()
    print(used_var)
    return obj.method()

if __name__ == "__main__":
    main()
"""
        file_path = self.create_test_python_file("test_vulture.py", test_content)
        
        # Mock vulture availability and execution
        self.analyzer.vulture_available = True
        
        with patch('subprocess.run') as mock_run:
            # Simulate vulture output
            mock_output = f"{file_path}:5: unused function 'unused_function' (90% confidence)\n" \
                         f"{file_path}:10: unused class 'UnusedClass' (85% confidence)\n" \
                         f"{file_path}:15: unused variable 'unused_var' (60% confidence)"
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr=""
            )
            
            results = self.analyzer._run_vulture([file_path])
            
            # Check that issues were detected
            assert len(results) == 3
            assert all(r.category == "unused_code" for r in results)
            
            # Check that unused code was stored
            assert len(self.analyzer.unused_code) == 3
            
            # Check specific issues
            unused_types = [u.type for u in self.analyzer.unused_code]
            assert "function" in unused_types
            assert "class" in unused_types
            assert "variable" in unused_types
            
            # Check that the correct names were identified
            unused_names = [u.name for u in self.analyzer.unused_code]
            assert "unused_function" in unused_names
            assert "UnusedClass" in unused_names
            assert "unused_var" in unused_names
    
    def test_build_import_graph(self):
        """Test building the import graph."""
        # Create test files with imports
        module1_content = """
import os
import sys
from pathlib import Path
import module2
from module3 import function
"""
        module2_content = """
import os
import module3
"""
        module3_content = """
import sys
"""
        
        module1_path = self.create_test_python_file("module1.py", module1_content)
        module2_path = self.create_test_python_file("module2.py", module2_content)
        module3_path = self.create_test_python_file("module3.py", module3_content)
        
        python_files = [module1_path, module2_path, module3_path]
        
        # Build the import graph
        self.analyzer._build_import_graph(python_files)
        
        # Check that imports were correctly identified
        assert "os" in self.analyzer.module_imports[str(module1_path)]
        assert "sys" in self.analyzer.module_imports[str(module1_path)]
        assert "pathlib" in self.analyzer.module_imports[str(module1_path)]
        assert "module2" in self.analyzer.module_imports[str(module1_path)]
        assert "module3" in self.analyzer.module_imports[str(module1_path)]
        
        assert "os" in self.analyzer.module_imports[str(module2_path)]
        assert "module3" in self.analyzer.module_imports[str(module2_path)]
        
        assert "sys" in self.analyzer.module_imports[str(module3_path)]
        
        # Check that module references were correctly built
        assert str(module1_path) in self.analyzer.module_references["module2"]
        assert str(module1_path) in self.analyzer.module_references["module3"]
        assert str(module2_path) in self.analyzer.module_references["module3"]
    
    def test_find_unreferenced_modules(self):
        """Test finding unreferenced modules."""
        # Create a project structure with referenced and unreferenced modules
        # Create package structure
        package_dir = self.project_root / "package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("")
        
        # Create modules
        main_module = self.create_test_python_file("main.py", """
import package.referenced_module

def main():
    package.referenced_module.function()

if __name__ == "__main__":
    main()
""")
        
        referenced_module = self.create_test_python_file("package/referenced_module.py", """
def function():
    return "I am referenced"
""")
        
        unreferenced_module = self.create_test_python_file("package/unreferenced_module.py", """
def function():
    return "I am not referenced"
""")
        
        # Also create a standalone script that's not imported but has a main block
        standalone_script = self.create_test_python_file("standalone_script.py", """
def function():
    return "I am standalone"

if __name__ == "__main__":
    function()
""")
        
        # Create a truly unreferenced module without a main block
        truly_unreferenced = self.create_test_python_file("truly_unreferenced.py", """
def function():
    return "I am truly unreferenced"
""")
        
        python_files = [
            main_module, 
            referenced_module, 
            unreferenced_module, 
            standalone_script,
            truly_unreferenced,
            package_dir / "__init__.py"
        ]
        
        # Build the import graph first
        self.analyzer._build_import_graph(python_files)
        
        # Find unreferenced modules
        results = self.analyzer._find_unreferenced_modules(python_files)
        
        # Check that unreferenced modules were detected
        unreferenced_results = [r for r in results if r.category == "unreferenced_module"]
        
        # The package/unreferenced_module.py and truly_unreferenced.py should be detected
        assert len(unreferenced_results) >= 2
        
        # Check specific modules
        unreferenced_paths = [r.file_path for r in unreferenced_results]
        assert str(unreferenced_module) in unreferenced_paths
        assert str(truly_unreferenced) in unreferenced_paths
        
        # The standalone script should not be detected as unreferenced (has main block)
        assert str(standalone_script) not in unreferenced_paths
        
        # The referenced module should not be detected as unreferenced
        assert str(referenced_module) not in unreferenced_paths
    
    def test_detect_commented_code(self):
        """Test detection of commented-out code blocks."""
        # Create a test file with commented-out code
        test_content = """
# This is a regular comment
# Another regular comment

# def commented_function():
#     return "This is commented out"
#     
# This is not a code comment

# class CommentedClass:
#     def method(self):
#         return "This is also commented out"

def real_function():
    # This is an inline comment
    return "This is real code"

# for i in range(10):
#     print(i)

# if x > 0:
#     print("positive")
# else:
#     print("negative")
"""
        file_path = self.create_test_python_file("test_comments.py", test_content)
        
        results = self.analyzer._detect_commented_code([file_path])
        
        # Check that commented code blocks were detected
        assert len(results) >= 3  # At least 3 blocks of commented code
        
        # Check that commented code was stored
        commented_code = [u for u in self.analyzer.unused_code if u.type == "commented_code"]
        assert len(commented_code) >= 3
        
        # All results should be in the "commented_code" category
        assert all(r.category == "commented_code" for r in results)
        
        # Check that line numbers were correctly identified
        line_numbers = sorted([r.line_number for r in results])
        
        # Check that we have at least 3 different line numbers
        assert len(line_numbers) >= 3
    
    def test_is_commented_code(self):
        """Test identification of commented code."""
        # Test cases that should be identified as code
        code_comments = [
            ["# def function():", "#     return 1"],
            ["# class MyClass:", "#     def method(self):", "#         pass"],
            ["# if x > 0:", "#     print('positive')"],
            ["# for i in range(10):", "#     print(i)"],
            ["# import os", "# import sys"],
            ["# x = 1", "# y = 2", "# z = x + y"]
        ]
        
        # Test cases that should not be identified as code
        non_code_comments = [
            ["# This is a regular comment"],
            ["# TODO: Fix this later"],
            ["# Note: This is important"],
            ["# Author: John Doe", "# Date: 2023-01-01"]
        ]
        
        # Check code comments
        for comment_block in code_comments:
            assert self.analyzer._is_commented_code(comment_block) == True, f"Failed to identify code: {comment_block}"
        
        # Check non-code comments
        for comment_block in non_code_comments:
            assert self.analyzer._is_commented_code(comment_block) == False, f"Incorrectly identified as code: {comment_block}"
    
    def test_analyze_unused_code_with_ast(self):
        """Test AST-based analysis for unused code."""
        # Create a test file with unused imports
        test_content = """
import os  # Used
import sys  # Unused
import re  # Unused
from pathlib import Path  # Used
from datetime import datetime  # Unused
import numpy as np  # Used with alias

def function():
    path = Path("test")
    size = os.path.getsize("file")
    array = np.array([1, 2, 3])
    return path, size, array
"""
        file_path = self.create_test_python_file("test_unused_imports.py", test_content)
        
        # Clear any previous results
        self.analyzer.unused_code = []
        
        results = self.analyzer._analyze_unused_code_with_ast([file_path])
        
        # Check that unused imports were detected
        assert len(results) > 0  # At least some unused imports
        
        # Check that unused imports were stored
        unused_imports = [u for u in self.analyzer.unused_code if u.type == "import"]
        assert len(unused_imports) > 0
        
        # All results should be in the "unused_import" category
        assert all(r.category == "unused_import" for r in results)
        
        # Check specific imports - at least one of these should be detected
        unused_import_names = [u.name for u in unused_imports]
        assert any(name in unused_import_names for name in ["sys", "re", "datetime"])
        
        # Check that we have at least one import that's used and one that's unused
        assert len(unused_import_names) > 0
    
    def test_import_visitor(self):
        """Test the ImportVisitor AST visitor."""
        # Create a simple AST for testing
        code = """
import os
import sys as system
from pathlib import Path
from datetime import datetime as dt
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        # Check that imports were correctly identified
        assert "os" in visitor.imports
        assert "sys" in visitor.imports
        assert "pathlib" in visitor.imports
        assert "datetime" in visitor.imports
        
        # Check that aliases were correctly identified
        assert visitor.aliases["system"] == "sys"
        assert visitor.aliases["dt"] == "datetime.datetime"
        
        # Check that line numbers were correctly recorded
        assert visitor.line_numbers["os"] == 2
        assert visitor.line_numbers["sys"] == 3
        assert visitor.line_numbers["pathlib"] == 4
        assert visitor.line_numbers["datetime"] == 5
    
    def test_name_visitor(self):
        """Test the NameVisitor AST visitor."""
        # Create a simple AST for testing
        code = """
import os
import sys
from pathlib import Path

x = 1
y = 2

def function(a, b):
    c = a + b
    return os.path.join(str(c), Path("test"))

result = function(x, y)
"""
        tree = ast.parse(code)
        visitor = NameVisitor()
        visitor.visit(tree)
        
        # Check that used names were correctly identified
        assert "os" in visitor.used_names
        assert "Path" in visitor.used_names
        assert "x" in visitor.used_names
        assert "y" in visitor.used_names
        assert "function" in visitor.used_names
        assert "str" in visitor.used_names
        
        # sys is imported but not used
        assert "sys" not in visitor.used_names
    
    def test_get_dead_code_summary(self):
        """Test generation of dead code summary."""
        # Populate test data
        self.analyzer.unused_code = [
            UnusedCode("unused_function", "function", "file1.py", 10),
            UnusedCode("UnusedClass", "class", "file1.py", 20),
            UnusedCode("unused_var", "variable", "file1.py", 30),
            UnusedCode("sys", "import", "file2.py", 5),
            UnusedCode("re", "import", "file2.py", 6),
            UnusedCode("commented_code_line_15", "commented_code", "file2.py", 15, "# def unused():\n#     pass"),
            UnusedCode("commented_code_line_20", "commented_code", "file2.py", 20, "# if x > 0:\n#     print(x)")
        ]
        
        summary = self.analyzer.get_dead_code_summary()
        
        # Check summary values
        assert summary['total_unused_code'] == 7
        assert summary['unused_functions'] == 1
        assert summary['unused_classes'] == 1
        assert summary['unused_variables'] == 1
        assert summary['unused_imports'] == 2
        assert summary['commented_code_blocks'] == 2
        assert summary['files_with_dead_code'] == 2  # file1.py and file2.py
    
    def test_full_analysis_integration(self):
        """Test full analysis integration."""
        # Create test files with various issues
        module1_dir = self.project_root / "module1"
        module1_dir.mkdir()
        
        module2_dir = self.project_root / "module2"
        module2_dir.mkdir()
        
        # Create __init__.py files
        (module1_dir / "__init__.py").write_text("")
        (module2_dir / "__init__.py").write_text("")
        
        # Module 1 file with unused code and imports
        module1_file = module1_dir / "code.py"
        module1_file.write_text("""
import os
import sys  # Unused
import re  # Unused

def used_function():
    return os.path.join("a", "b")

def unused_function():
    return "This is never called"

# Commented out code
# def old_function():
#     return "This was removed"

x = 1  # Used
y = 2  # Unused

def main():
    print(used_function())
    print(x)

if __name__ == "__main__":
    main()
""")
        
        # Module 2 file that imports module1
        module2_file = module2_dir / "code.py"
        module2_file.write_text("""
from module1.code import used_function

def wrapper():
    return used_function()

if __name__ == "__main__":
    wrapper()
""")
        
        # Unreferenced module
        unreferenced_file = self.project_root / "unreferenced.py"
        unreferenced_file.write_text("""
def function():
    return "I am not used anywhere"
""")
        
        # Mock vulture
        self.analyzer.vulture_available = False
        
        # Run full analysis
        results = self.analyzer.analyze(str(self.project_root))
        
        # Should return results without errors
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check that all major analysis components ran
        categories = {r.category for r in results}
        
        # Should have detected various issues
        assert "unused_import" in categories
        assert "commented_code" in categories
        assert "unreferenced_module" in categories


def run_all_tests():
    """Run all DeadCodeAnalyzer tests."""
    print("Running DeadCodeAnalyzer tests...\n")
    
    test_instance = TestDeadCodeAnalyzer()
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