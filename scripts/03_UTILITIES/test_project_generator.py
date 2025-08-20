"""
Test Project Generator - Creates test projects with known issues for validation

This module generates test project structures with predefined issues to validate
the project cleanup analyzer. It creates directories and files with various issues
like code duplication, dead code, style violations, etc.
"""

import os
import sys
import shutil
import random
import string
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestProjectGenerator:
    """Generates test projects with known issues for validation."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the test project generator.
        
        Args:
            output_dir: Directory where test projects will be created
        """
        self.output_dir = Path(output_dir)
        self.current_project_dir = None
        self.logger = logging.getLogger(__name__)
        
    def create_project(self, project_name: str) -> Path:
        """
        Create a new test project directory.
        
        Args:
            project_name: Name of the test project
            
        Returns:
            Path to the created project directory
        """
        # Create project directory
        project_dir = self.output_dir / project_name
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        project_dir.mkdir(parents=True, exist_ok=True)
        self.current_project_dir = project_dir
        
        return project_dir
    
    def add_structure_issues(self) -> Dict[str, Any]:
        """
        Add structure-related issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "misplaced_files": [],
            "inconsistent_naming": [],
            "missing_required_files": []
        }
        
        # Create GopiAI-like module structure
        modules = ["GopiAI-Core", "GopiAI-UI", "GopiAI-Extensions"]
        for module in modules:
            module_dir = self.current_project_dir / module
            module_dir.mkdir(parents=True, exist_ok=True)
            
            # Create proper structure in first module
            if module == "GopiAI-Core":
                (module_dir / "gopiai").mkdir(parents=True, exist_ok=True)
                (module_dir / "tests").mkdir(parents=True, exist_ok=True)
                
                # Create proper files
                self._write_file(module_dir / "pyproject.toml", self._generate_pyproject_content(module))
                self._write_file(module_dir / "README.md", f"# {module}\n\nThis is a test module.")
                
                # Create source files
                self._write_file(
                    module_dir / "gopiai" / "__init__.py",
                    '"""Core module initialization."""\n\n__version__ = "0.1.0"\n'
                )
                self._write_file(
                    module_dir / "gopiai" / "core.py",
                    self._generate_python_file_with_classes(2)
                )
                
                # Create test files
                self._write_file(
                    module_dir / "tests" / "test_core.py",
                    self._generate_test_file("core")
                )
            
            # Create inconsistent structure in second module
            elif module == "GopiAI-UI":
                # Missing gopiai directory (inconsistent)
                (module_dir / "src").mkdir(parents=True, exist_ok=True)  # Wrong structure
                (module_dir / "tests").mkdir(parents=True, exist_ok=True)
                
                # Create files with inconsistent naming
                self._write_file(module_dir / "setup.py", self._generate_setup_py_content(module))  # Should be pyproject.toml
                issues["inconsistent_naming"].append(str(module_dir / "setup.py"))
                
                # Create source files in wrong location
                self._write_file(
                    module_dir / "src" / "__init__.py",
                    '"""UI module initialization."""\n\n__version__ = "0.1.0"\n'
                )
                issues["misplaced_files"].append(str(module_dir / "src" / "__init__.py"))
                
                self._write_file(
                    module_dir / "src" / "ui.py",
                    self._generate_python_file_with_classes(3)
                )
                issues["misplaced_files"].append(str(module_dir / "src" / "ui.py"))
                
                # Missing README.md
                issues["missing_required_files"].append(f"{module}/README.md")
            
            # Create third module with mixed issues
            else:
                # Partially correct structure
                (module_dir / "gopiai").mkdir(parents=True, exist_ok=True)
                # Missing tests directory
                issues["missing_required_files"].append(f"{module}/tests")
                
                # Create some files
                self._write_file(module_dir / "pyproject.toml", self._generate_pyproject_content(module))
                
                # Create source files
                self._write_file(
                    module_dir / "gopiai" / "__init__.py",
                    '"""Extensions module initialization."""\n\n__version__ = "0.1.0"\n'
                )
                
                # Misplaced file
                self._write_file(
                    module_dir / "extensions.py",  # Should be in gopiai/
                    self._generate_python_file_with_classes(2)
                )
                issues["misplaced_files"].append(str(module_dir / "extensions.py"))
        
        # Create some files in the root directory (misplaced)
        self._write_file(
            self.current_project_dir / "utils.py",
            self._generate_python_file_with_functions(3)
        )
        issues["misplaced_files"].append(str(self.current_project_dir / "utils.py"))
        
        return issues

    def add_code_quality_issues(self) -> Dict[str, Any]:
        """
        Add code quality issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "style_violations": [],
            "complex_functions": [],
            "inconsistent_naming": []
        }
        
        # Create a file with style violations
        style_file = self.current_project_dir / "GopiAI-Core" / "gopiai" / "style_issues.py"
        style_content = '''"""Module with style issues."""

import os, sys, random # Multiple imports on one line
from pathlib import Path

def badlyNamedFunction( param1,param2 ):
    """This function has style issues."""
    x=1+2 # No spaces around operators
    y= [i*i for i in range(10)] # Inconsistent spacing
    
    if(x>0):print("Positive") # No whitespace and inline statement
    
    return x+y[0]

class badClass:
    """Class with style issues."""
    
    def __init__( self ):
        self.attr1=10
        self.Attr2=20 # Inconsistent naming
    
    def Another_Method(self): # Inconsistent naming
        return self.attr1+self.Attr2
'''
        self._write_file(style_file, style_content)
        issues["style_violations"].append(str(style_file))
        
        # Create a file with complex functions
        complex_file = self.current_project_dir / "GopiAI-UI" / "src" / "complex.py"
        complex_content = '''"""Module with complex functions."""

def complex_function(a, b, c, d, e):
    """This function has high cyclomatic complexity."""
    result = 0
    
    if a > 0:
        if b > 0:
            if c > 0:
                result = a + b + c
            else:
                if d > 0:
                    result = a + b + d
                else:
                    result = a + b
        else:
            if d > 0:
                if e > 0:
                    result = a + d + e
                else:
                    result = a + d
            else:
                if e > 0:
                    result = a + e
                else:
                    result = a
    else:
        if b > 0:
            if c > 0:
                result = b + c
            else:
                result = b
        else:
            if d > 0:
                result = d
            else:
                if e > 0:
                    result = e
                else:
                    result = 0
    
    return result

def another_complex_function(data):
    """Another function with high complexity."""
    result = []
    
    for i in range(len(data)):
        if i % 2 == 0:
            if i % 3 == 0:
                result.append(data[i] * 2)
            else:
                if i % 5 == 0:
                    result.append(data[i] * 3)
                else:
                    result.append(data[i])
        else:
            if i % 3 == 0:
                if i % 7 == 0:
                    result.append(data[i] // 2)
                else:
                    result.append(data[i] + 1)
            else:
                result.append(data[i] - 1)
    
    return result
'''
        self._write_file(complex_file, complex_content)
        issues["complex_functions"].append(str(complex_file))
        
        # Create a file with inconsistent naming
        naming_file = self.current_project_dir / "GopiAI-Extensions" / "gopiai" / "naming_issues.py"
        naming_content = '''"""Module with naming issues."""

def camelCaseFunction(param):
    """This function uses camelCase instead of snake_case."""
    return param * 2

def snake_case_function(param):
    """This function uses snake_case (correct)."""
    return param + 1

def UPPERCASE_FUNCTION(param):
    """This function uses UPPERCASE_FUNCTION instead of snake_case."""
    return param - 1

class mixedNamingClass:
    """Class with mixed naming conventions."""
    
    def __init__(self):
        self.snake_case_attr = 1
        self.camelCaseAttr = 2
        self.UPPERCASE_ATTR = 3
    
    def snake_case_method(self):
        """Method with correct naming."""
        return self.snake_case_attr
    
    def camelCaseMethod(self):
        """Method with incorrect naming."""
        return self.camelCaseAttr
    
    def UPPERCASE_METHOD(self):
        """Method with incorrect naming."""
        return self.UPPERCASE_ATTR
'''
        self._write_file(naming_file, naming_content)
        issues["inconsistent_naming"].append(str(naming_file))
        
        return issues
    
    def add_dead_code_issues(self) -> Dict[str, Any]:
        """
        Add dead code issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "unused_imports": [],
            "unused_functions": [],
            "unused_variables": [],
            "commented_code": []
        }
        
        # Create a file with unused imports
        imports_file = self.current_project_dir / "GopiAI-Core" / "gopiai" / "unused_imports.py"
        imports_content = '''"""Module with unused imports."""

import os  # Used
import sys  # Unused
import random  # Unused
import json  # Unused
from pathlib import Path  # Used
from typing import List, Dict, Any  # Partially used
import datetime  # Unused
import re  # Unused

def get_files(directory):
    """Get list of files in a directory."""
    return [f for f in os.listdir(directory) if Path(f).is_file()]
'''
        self._write_file(imports_file, imports_content)
        issues["unused_imports"].append(str(imports_file))
        
        # Create a file with unused functions and variables
        unused_file = self.current_project_dir / "GopiAI-UI" / "src" / "unused_code.py"
        unused_content = '''"""Module with unused functions and variables."""

# Unused constant
MAX_ITEMS = 100

# Used constant
DEFAULT_SIZE = 10

def used_function(size=DEFAULT_SIZE):
    """This function is used."""
    return [i for i in range(size)]

def unused_function():
    """This function is never called."""
    # Unused variable
    result = []
    for i in range(MAX_ITEMS):
        result.append(i * i)
    return result

def another_unused_function():
    """Another function that is never called."""
    return "This is never used"

class SampleClass:
    """Class with unused methods."""
    
    def __init__(self, size=DEFAULT_SIZE):
        self.size = size
        # Unused attribute
        self.max_size = MAX_ITEMS
    
    def used_method(self):
        """This method is used."""
        return used_function(self.size)
    
    def unused_method(self):
        """This method is never called."""
        return self.size * 2

# Create an instance and call the used method
sample = SampleClass()
result = sample.used_method()
'''
        self._write_file(unused_file, unused_content)
        issues["unused_functions"].append(str(unused_file))
        issues["unused_variables"].append(str(unused_file))
        
        # Create a file with commented-out code
        commented_file = self.current_project_dir / "GopiAI-Extensions" / "gopiai" / "commented_code.py"
        commented_content = '''"""Module with commented-out code."""

def active_function():
    """This function is active."""
    return "I am active"

# def old_function():
#     """This function was commented out."""
#     return "I am old"
#
# class OldClass:
#     """This class was commented out."""
#     
#     def __init__(self):
#         self.value = 42
#     
#     def get_value(self):
#         return self.value

def another_function():
    """Another active function."""
    # Old implementation:
    # result = []
    # for i in range(10):
    #     result.append(i * i)
    # return result
    
    # New implementation:
    return [i * i for i in range(10)]
'''
        self._write_file(commented_file, commented_content)
        issues["commented_code"].append(str(commented_file))
        
        return issues   
 def add_duplicate_code_issues(self) -> Dict[str, Any]:
        """
        Add duplicate code issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "duplicate_functions": [],
            "duplicate_classes": [],
            "similar_code": []
        }
        
        # Create files with duplicate functions
        duplicate_func_file1 = self.current_project_dir / "GopiAI-Core" / "gopiai" / "utils.py"
        duplicate_func_content1 = '''"""Utility functions."""

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_max_value(data):
    """Find the maximum value in a list."""
    if not data:
        return None
    max_val = data[0]
    for val in data:
        if val > max_val:
            max_val = val
    return max_val

def find_min_value(data):
    """Find the minimum value in a list."""
    if not data:
        return None
    min_val = data[0]
    for val in data:
        if val < min_val:
            min_val = val
    return min_val
'''
        self._write_file(duplicate_func_file1, duplicate_func_content1)
        
        duplicate_func_file2 = self.current_project_dir / "GopiAI-UI" / "src" / "helpers.py"
        duplicate_func_content2 = '''"""Helper functions."""

def get_average(values):
    """Calculate the average of a list of values."""
    if not values:
        return 0
    return sum(values) / len(values)  # Duplicate of calculate_average

def find_maximum(data):
    """Find the maximum value in a list."""
    if not data:
        return None
    max_val = data[0]
    for val in data:
        if val > max_val:
            max_val = val
    return max_val  # Duplicate of find_max_value

def find_minimum(data):
    """Find the minimum value in a list."""
    if not data:
        return None
    min_val = data[0]
    for val in data:
        if val < min_val:
            min_val = val
    return min_val  # Duplicate of find_min_value
'''
        self._write_file(duplicate_func_file2, duplicate_func_content2)
        
        issues["duplicate_functions"].extend([
            str(duplicate_func_file1),
            str(duplicate_func_file2)
        ])
        
        # Create files with duplicate classes
        duplicate_class_file1 = self.current_project_dir / "GopiAI-Core" / "gopiai" / "models.py"
        duplicate_class_content1 = '''"""Data models."""

class User:
    """User model."""
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password  # Should be hashed in real code
    
    def validate(self):
        """Validate user data."""
        if not self.username or len(self.username) < 3:
            return False
        if not self.email or '@' not in self.email:
            return False
        if not self.password or len(self.password) < 8:
            return False
        return True
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'username': self.username,
            'email': self.email
        }
'''
        self._write_file(duplicate_class_file1, duplicate_class_content1)
        
        duplicate_class_file2 = self.current_project_dir / "GopiAI-Extensions" / "gopiai" / "user.py"
        duplicate_class_content2 = '''"""User management."""

class UserModel:  # Duplicate of User class with minor changes
    """User model."""
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    
    def is_valid(self):  # Same as validate but renamed
        """Validate user data."""
        if not self.username or len(self.username) < 3:
            return False
        if not self.email or '@' not in self.email:
            return False
        if not self.password or len(self.password) < 8:
            return False
        return True
    
    def as_dict(self):  # Same as to_dict but renamed
        """Convert to dictionary."""
        return {
            'username': self.username,
            'email': self.email
        }
'''
        self._write_file(duplicate_class_file2, duplicate_class_content2)
        
        issues["duplicate_classes"].extend([
            str(duplicate_class_file1),
            str(duplicate_class_file2)
        ])
        
        # Create files with similar code patterns
        similar_code_file1 = self.current_project_dir / "GopiAI-Core" / "gopiai" / "processors.py"
        similar_code_content1 = '''"""Data processors."""

def process_user_data(user_data):
    """Process user data."""
    result = []
    for user in user_data:
        if 'name' in user and 'age' in user:
            processed = {
                'name': user['name'].strip().title(),
                'age': int(user['age']),
                'is_adult': int(user['age']) >= 18
            }
            result.append(processed)
    return result

def process_product_data(product_data):
    """Process product data."""
    result = []
    for product in product_data:
        if 'name' in product and 'price' in product:
            processed = {
                'name': product['name'].strip().title(),
                'price': float(product['price']),
                'is_premium': float(product['price']) > 100
            }
            result.append(processed)
    return result

def process_order_data(order_data):
    """Process order data."""
    result = []
    for order in order_data:
        if 'id' in order and 'items' in order:
            processed = {
                'id': order['id'].strip(),
                'items': len(order['items']),
                'is_large': len(order['items']) > 5
            }
            result.append(processed)
    return result
'''
        self._write_file(similar_code_file1, similar_code_content1)
        
        issues["similar_code"].append(str(similar_code_file1))
        
        return issues
    
    def add_dependency_issues(self) -> Dict[str, Any]:
        """
        Add dependency-related issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "outdated_dependencies": [],
            "version_conflicts": [],
            "unused_dependencies": []
        }
        
        # Create pyproject.toml with outdated dependencies
        core_pyproject = self.current_project_dir / "GopiAI-Core" / "pyproject.toml"
        core_pyproject_content = '''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gopiai-core"
version = "0.1.0"
description = "GopiAI Core Module"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
dependencies = [
    "requests==2.25.0",  # Outdated, current is 2.28.x
    "pyyaml==5.3.1",     # Outdated, current is 6.x
    "pytest==6.2.5",     # Outdated, current is 7.x
    "black==21.5b2",     # Outdated, current is 23.x
    "unused-package==1.0.0",  # Not actually used in the code
]

[project.optional-dependencies]
dev = [
    "flake8>=3.9.0",
    "mypy>=0.812",
]
'''
        self._write_file(core_pyproject, core_pyproject_content)
        issues["outdated_dependencies"].append(str(core_pyproject))
        issues["unused_dependencies"].append(str(core_pyproject))
        
        # Create requirements.txt with version conflicts
        ui_requirements = self.current_project_dir / "GopiAI-UI" / "requirements.txt"
        ui_requirements_content = '''# UI Module Requirements
requests==2.28.1  # Conflicts with Core's 2.25.0
pyyaml==6.0      # Conflicts with Core's 5.3.1
pytest==7.3.1    # Conflicts with Core's 6.2.5
black==23.3.0    # Conflicts with Core's 21.5b2
pyside6==6.5.0
unused-lib==2.0.0  # Not actually used in the code
'''
        self._write_file(ui_requirements, ui_requirements_content)
        issues["version_conflicts"].append(str(ui_requirements))
        issues["unused_dependencies"].append(str(ui_requirements))
        
        return issues
    
    def add_documentation_issues(self) -> Dict[str, Any]:
        """
        Add documentation-related issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "missing_docstrings": [],
            "outdated_readme": [],
            "inconsistent_docs": []
        }
        
        # Create a file with missing docstrings
        missing_docs_file = self.current_project_dir / "GopiAI-Core" / "gopiai" / "missing_docs.py"
        missing_docs_content = '''"""Module with missing docstrings."""

# Missing function docstring
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

# Missing class docstring
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    # Missing method docstring
    def process(self):
        return [item * 2 for item in self.data]
    
    """This docstring is misplaced and should be above the method."""
    def filter(self, threshold):
        return [item for item in self.data if item > threshold]

# Function with proper docstring
def calculate_average(items):
    """Calculate the average of a list of items."""
    if not items:
        return 0
    return sum(items) / len(items)
'''
        self._write_file(missing_docs_file, missing_docs_content)
        issues["missing_docstrings"].append(str(missing_docs_file))
        
        # Create an outdated README
        outdated_readme = self.current_project_dir / "GopiAI-Core" / "README.md"
        outdated_readme_content = '''# GopiAI Core

Core module for the GopiAI project.

## Installation

```bash
pip install -e .
```

## Features

- Base interfaces and abstract classes
- Error handling framework
- Configuration management

## Dependencies

- Python 3.7+
- requests 2.24.0
- pyyaml 5.3.0

## Usage

```python
from gopiai.core import BaseClass

class MyClass(BaseClass):
    def __init__(self):
        super().__init__()
```

## API Reference

### BaseClass

Base class for all GopiAI components.

### ErrorHandler

Handles errors during processing.
'''
        self._write_file(outdated_readme, outdated_readme_content)
        issues["outdated_readme"].append(str(outdated_readme))
        
        # Create inconsistent documentation
        inconsistent_docs_file = self.current_project_dir / "GopiAI-Extensions" / "gopiai" / "inconsistent_docs.py"
        inconsistent_docs_content = '''"""Module with inconsistent documentation."""

def process_data(data, options=None):
    """Process the input data.
    
    Args:
        data: The data to process
        
    Returns:
        Processed data
    """
    if options is None:
        options = {}
    
    # Process the data
    result = []
    for item in data:
        result.append(item * 2)
    
    return result

class DataHandler:
    """Handles data processing.
    
    Parameters:
        data_source (str): Source of the data
        cache_size (int, optional): Size of the cache
    """
    
    def __init__(self, data_source, cache_size=100):
        self.data_source = data_source
        self.cache_size = cache_size
    
    def load_data(self):
        """Load data from the source.
        
        Return:
            List of data items
        """
        # Simulate loading data
        return [i for i in range(10)]
    
    def save_data(self, data):
        """
        Save data to the source.
        
        Parameters
        ----------
        data : list
            Data to save
        
        Returns
        -------
        bool
            Success status
        """
        # Simulate saving data
        return True
'''
        self._write_file(inconsistent_docs_file, inconsistent_docs_content)
        issues["inconsistent_docs"].append(str(inconsistent_docs_file))
        
        return issues
    
    def add_conflict_issues(self) -> Dict[str, Any]:
        """
        Add potential conflict issues to the project.
        
        Returns:
            Dictionary with details of created issues
        """
        issues = {
            "global_variables": [],
            "threading_issues": [],
            "resource_leaks": []
        }
        
        # Create a file with global variables
        globals_file = self.current_project_dir / "GopiAI-Core" / "gopiai" / "globals.py"
        globals_content = '''"""Module with global variables."""

# Global configuration
CONFIG = {
    "api_url": "https://api.example.com",
    "timeout": 30,
    "max_retries": 3
}

# Global counter
COUNTER = 0

# Global cache
CACHE = {}

def increment_counter():
    """Increment the global counter."""
    global COUNTER
    COUNTER += 1
    return COUNTER

def add_to_cache(key, value):
    """Add an item to the global cache."""
    global CACHE
    CACHE[key] = value

def get_from_cache(key):
    """Get an item from the global cache."""
    return CACHE.get(key)

def update_config(key, value):
    """Update the global configuration."""
    global CONFIG
    CONFIG[key] = value
'''
        self._write_file(globals_file, globals_content)
        issues["global_variables"].append(str(globals_file))
        
        # Create a file with threading issues
        threading_file = self.current_project_dir / "GopiAI-UI" / "src" / "threading_issues.py"
        threading_content = '''"""Module with threading issues."""

import threading
import time

# Shared counter without proper locking
counter = 0

def increment_counter():
    """Increment the counter without proper locking."""
    global counter
    local_value = counter
    time.sleep(0.1)  # Simulate some work
    counter = local_value + 1

def run_threads():
    """Run multiple threads that increment the counter."""
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=increment_counter)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return counter

# Shared resource without proper synchronization
class SharedResource:
    """A resource shared between threads without proper synchronization."""
    
    def __init__(self):
        self.data = []
        self.counter = 0
    
    def add_data(self, item):
        """Add data to the shared resource."""
        self.data.append(item)
        self.counter += 1
    
    def get_data(self):
        """Get data from the shared resource."""
        return self.data
    
    def get_count(self):
        """Get the count of items."""
        return self.counter
'''
        self._write_file(threading_file, threading_content)
        issues["threading_issues"].append(str(threading_file))
        
        # Create a file with resource leaks
        leaks_file = self.current_project_dir / "GopiAI-Extensions" / "gopiai" / "resource_leaks.py"
        leaks_content = '''"""Module with resource leaks."""

def read_file_with_leak(file_path):
    """Read a file without properly closing it."""
    f = open(file_path, 'r')  # Resource leak: file not closed
    content = f.read()
    return content

def process_files_with_leak(file_paths):
    """Process multiple files without properly closing them."""
    results = []
    for path in file_paths:
        f = open(path, 'r')  # Resource leak: files not closed in loop
        results.append(f.read())
    return results

class DatabaseConnection:
    """Database connection that is not properly closed."""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self):
        """Connect to the database."""
        # Simulate opening a connection
        self.connection = {"status": "connected"}
        return self.connection
    
    def execute_query(self, query):
        """Execute a query."""
        if not self.connection:
            self.connect()
        
        # Simulate executing a query
        return [{"result": "data"}]
    
    # Missing close method to release the connection
'''
        self._write_file(leaks_file, leaks_content)
        issues["resource_leaks"].append(str(leaks_file))
        
        return issues   
 def generate_test_project(self, project_name: str = "test_project") -> Dict[str, Any]:
        """
        Generate a complete test project with various issues.
        
        Args:
            project_name: Name of the test project
            
        Returns:
            Dictionary with details of all created issues
        """
        project_dir = self.create_project(project_name)
        
        # Add various issues
        structure_issues = self.add_structure_issues()
        code_quality_issues = self.add_code_quality_issues()
        dead_code_issues = self.add_dead_code_issues()
        duplicate_issues = self.add_duplicate_code_issues()
        dependency_issues = self.add_dependency_issues()
        documentation_issues = self.add_documentation_issues()
        conflict_issues = self.add_conflict_issues()
        
        # Combine all issues
        all_issues = {
            "project_dir": str(project_dir),
            "structure_issues": structure_issues,
            "code_quality_issues": code_quality_issues,
            "dead_code_issues": dead_code_issues,
            "duplicate_issues": duplicate_issues,
            "dependency_issues": dependency_issues,
            "documentation_issues": documentation_issues,
            "conflict_issues": conflict_issues
        }
        
        # Save issues to a JSON file for reference
        issues_file = project_dir / "known_issues.json"
        with open(issues_file, 'w') as f:
            import json
            json.dump(all_issues, f, indent=2)
        
        return all_issues
    
    def generate_edge_case_project(self, project_name: str = "edge_case_project") -> Dict[str, Any]:
        """
        Generate a test project with edge cases.
        
        Args:
            project_name: Name of the test project
            
        Returns:
            Dictionary with details of all created edge cases
        """
        project_dir = self.create_project(project_name)
        edge_cases = {}
        
        # Create very large file
        large_file = project_dir / "large_file.py"
        with open(large_file, 'w') as f:
            f.write('"""Very large file."""\n\n')
            for i in range(10000):
                f.write(f'# Line {i}\nvar_{i} = {i}\n')
        edge_cases["large_file"] = str(large_file)
        
        # Create file with non-ASCII characters
        non_ascii_file = project_dir / "non_ascii.py"
        with open(non_ascii_file, 'w', encoding='utf-8') as f:
            f.write('"""File with non-ASCII characters."""\n\n')
            f.write('# Russian: Привет, мир!\n')
            f.write('# Chinese: 你好，世界！\n')
            f.write('# Emoji: 😀 🚀 🐍\n\n')
            f.write('def greet():\n')
            f.write('    return "Привет, мир!"\n')
        edge_cases["non_ascii_file"] = str(non_ascii_file)
        
        # Create file with syntax errors
        syntax_error_file = project_dir / "syntax_error.py"
        with open(syntax_error_file, 'w') as f:
            f.write('"""File with syntax errors."""\n\n')
            f.write('def broken_function(:\n')  # Missing closing parenthesis
            f.write('    return "broken"\n\n')
            f.write('class BrokenClass\n')  # Missing colon
            f.write('    def __init__(self):\n')
            f.write('        self.value = 42\n')
        edge_cases["syntax_error_file"] = str(syntax_error_file)
        
        # Create deeply nested directories
        nested_dir = project_dir
        for i in range(10):
            nested_dir = nested_dir / f"level_{i}"
            nested_dir.mkdir(parents=True, exist_ok=True)
        
        nested_file = nested_dir / "deeply_nested.py"
        with open(nested_file, 'w') as f:
            f.write('"""Deeply nested file."""\n\n')
            f.write('def nested_function():\n')
            f.write('    return "I am deeply nested"\n')
        edge_cases["deeply_nested_file"] = str(nested_file)
        
        # Create file with very long lines
        long_lines_file = project_dir / "long_lines.py"
        with open(long_lines_file, 'w') as f:
            f.write('"""File with very long lines."""\n\n')
            f.write('# ' + 'x' * 1000 + '\n')
            f.write('very_long_variable_name = ' + ' + '.join([f'"{c}"' for c in 'abcdefghijklmnopqrstuvwxyz' * 10]) + '\n')
            f.write('def function_with_long_line():\n')
            f.write('    return ' + ' + '.join([str(i) for i in range(100)]) + '\n')
        edge_cases["long_lines_file"] = str(long_lines_file)
        
        # Create file with unusual extensions
        unusual_ext_file = project_dir / "unusual.xyz"
        with open(unusual_ext_file, 'w') as f:
            f.write('This file has an unusual extension.\n')
        edge_cases["unusual_ext_file"] = str(unusual_ext_file)
        
        # Save edge cases to a JSON file for reference
        edge_cases_file = project_dir / "edge_cases.json"
        with open(edge_cases_file, 'w') as f:
            import json
            json.dump(edge_cases, f, indent=2)
        
        return edge_cases
    
    def _write_file(self, path: Path, content: str) -> None:
        """
        Write content to a file, creating parent directories if needed.
        
        Args:
            path: Path to the file
            content: Content to write
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    
    def _generate_pyproject_content(self, module_name: str) -> str:
        """
        Generate content for a pyproject.toml file.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Content for pyproject.toml
        """
        package_name = module_name.lower().replace('-', '_')
        return f'''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{module_name.lower()}"
version = "0.1.0"
description = "{module_name} Module"
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}
dependencies = [
    "requests>=2.25.0",
    "pyyaml>=5.3.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.2.5",
    "black>=21.5b2",
]
'''
    
    def _generate_setup_py_content(self, module_name: str) -> str:
        """
        Generate content for a setup.py file.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Content for setup.py
        """
        package_name = module_name.lower().replace('-', '_')
        return f'''from setuptools import setup, find_packages

setup(
    name="{module_name.lower()}",
    version="0.1.0",
    description="{module_name} Module",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.3.1",
    ],
    extras_require={{
        "dev": [
            "pytest>=6.2.5",
            "black>=21.5b2",
        ]
    }},
    python_requires=">=3.8",
)
'''
    
    def _generate_python_file_with_classes(self, num_classes: int) -> str:
        """
        Generate a Python file with classes.
        
        Args:
            num_classes: Number of classes to generate
            
        Returns:
            Content for the Python file
        """
        content = '"""Generated Python file with classes."""\n\n'
        
        for i in range(num_classes):
            content += f'''class Class{i + 1}:
    """Class {i + 1} documentation."""
    
    def __init__(self, value=0):
        self.value = value
    
    def get_value(self):
        """Get the value."""
        return self.value
    
    def set_value(self, value):
        """Set the value."""
        self.value = value
        return self
    
    def __str__(self):
        return f"Class{i + 1}({{self.value}})"

'''
        
        return content
    
    def _generate_python_file_with_functions(self, num_functions: int) -> str:
        """
        Generate a Python file with functions.
        
        Args:
            num_functions: Number of functions to generate
            
        Returns:
            Content for the Python file
        """
        content = '"""Generated Python file with functions."""\n\n'
        
        for i in range(num_functions):
            content += f'''def function{i + 1}(param1, param2=0, *args, **kwargs):
    """Function {i + 1} documentation.
    
    Args:
        param1: First parameter
        param2: Second parameter (default: 0)
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
    
    Returns:
        Result of the function
    """
    result = param1 + param2
    
    for arg in args:
        result += arg
    
    for key, value in kwargs.items():
        if isinstance(value, (int, float)):
            result += value
    
    return result

'''
        
        return content
    
    def _generate_test_file(self, module_name: str) -> str:
        """
        Generate a test file for a module.
        
        Args:
            module_name: Name of the module to test
            
        Returns:
            Content for the test file
        """
        content = f'''"""Tests for the {module_name} module."""

import unittest
from gopiai import {module_name}

class Test{module_name.title()}(unittest.TestCase):
    """Test case for the {module_name} module."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Tear down test fixtures."""
        pass
    
    def test_example(self):
        """Test example functionality."""
        self.assertEqual(1 + 1, 2)
    
    def test_another_example(self):
        """Test another example."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
        
        return content


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test projects with known issues')
    parser.add_argument('--output-dir', '-o', type=str, default='test_projects',
                        help='Directory where test projects will be created')
    parser.add_argument('--project-name', '-n', type=str, default='test_project',
                        help='Name of the test project')
    parser.add_argument('--edge-cases', '-e', action='store_true',
                        help='Generate edge case project')
    
    args = parser.parse_args()
    
    generator = TestProjectGenerator(args.output_dir)
    
    if args.edge_cases:
        print(f"Generating edge case project '{args.project_name}_edge_cases'...")
        edge_cases = generator.generate_edge_case_project(f"{args.project_name}_edge_cases")
        print(f"Edge case project created at: {edge_cases['project_dir']}")
    else:
        print(f"Generating test project '{args.project_name}'...")
        issues = generator.generate_test_project(args.project_name)
        print(f"Test project created at: {issues['project_dir']}")
        print(f"Known issues saved to: {issues['project_dir']}/known_issues.json")
        """
        Add edge case files to the project for testing extreme scenarios.
        
        Returns:
            Dictionary with details of created edge cases
        """
        edge_cases = {
            "empty_files": [],
            "very_large_files": [],
            "invalid_syntax": [],
            "unusual_encodings": [],
            "binary_files": [],
            "deeply_nested": []
        }
        
        # Create empty files
        empty_file = self.current_project_dir / "empty_file.py"
        self._write_file(empty_file, "")
        edge_cases["empty_files"].append(str(empty_file))
        
        # Create a very large file
        large_file = self.current_project_dir / "very_large.py"
        large_content = '"""Very large file."""\n\n'
        for i in range(1000):
            large_content += f"def function_{i}():\n    return {i}\n\n"
        self._write_file(large_file, large_content)
        edge_cases["very_large_files"].append(str(large_file))
        
        # Create file with invalid syntax
        invalid_file = self.current_project_dir / "invalid_syntax.py"
        invalid_content = '''"""File with invalid syntax."""

def broken_function():
    if True
        print("Missing colon")
    
    return None

class BrokenClass
    def __init__(self):
        self.value = 42
'''
        self._write_file(invalid_file, invalid_content)
        edge_cases["invalid_syntax"].append(str(invalid_file))
        
        # Create file with unusual encoding
        encoding_file = self.current_project_dir / "unusual_encoding.py"
        encoding_content = '''# -*- coding: utf-8 -*-
"""File with unusual characters."""

def unicode_function():
    # Some unicode characters
    text = "こんにちは世界"  # Hello world in Japanese
    symbols = "★☆♠♣♥♦♪♫"
    emoji = "😀😁😂🤣😃😄😅"
    return text + symbols + emoji
'''
        self._write_file(encoding_file, encoding_content)
        edge_cases["unusual_encodings"].append(str(encoding_file))
        
        # Create binary file
        binary_file = self.current_project_dir / "binary_file.bin"
        with open(binary_file, "wb") as f:
            f.write(os.urandom(1024))  # 1KB of random binary data
        edge_cases["binary_files"].append(str(binary_file))
        
        # Create deeply nested directories and files
        nested_dir = self.current_project_dir
        for i in range(10):  # Create 10 levels of nesting
            nested_dir = nested_dir / f"level_{i}"
            nested_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a file at this level
            nested_file = nested_dir / f"file_{i}.py"
            self._write_file(nested_file, f'"""Level {i} file."""\n\ndef level_{i}_function():\n    return {i}\n')
            edge_cases["deeply_nested"].append(str(nested_file))
        
        return edge_cases
    
    def generate_large_codebase(self, num_modules: int = 5, files_per_module: int = 20, lines_per_file: int = 200) -> Dict[str, Any]:
        """
        Generate a large codebase for performance testing.
        
        Args:
            num_modules: Number of modules to create
            files_per_module: Number of files per module
            lines_per_file: Average number of lines per file
            
        Returns:
            Dictionary with details of the generated codebase
        """
        stats = {
            "modules": num_modules,
            "total_files": 0,
            "total_lines": 0
        }
        
        # Create modules
        for module_idx in range(num_modules):
            module_name = f"Module{module_idx}"
            module_dir = self.current_project_dir / module_name
            module_dir.mkdir(parents=True, exist_ok=True)
            
            # Create package structure
            src_dir = module_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)
            
            tests_dir = module_dir / "tests"
            tests_dir.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files
            self._write_file(src_dir / "__init__.py", f'"""Module {module_name} package."""\n\n__version__ = "0.1.0"\n')
            self._write_file(tests_dir / "__init__.py", '"""Test package."""\n')
            
            # Create module files
            for file_idx in range(files_per_module):
                # Determine file type
                if file_idx % 10 == 0:
                    # Create a configuration file
                    file_path = module_dir / f"config_{file_idx}.json"
                    content = '{\n'
                    for i in range(50):
                        content += f'    "setting_{i}": "value_{i}",\n'
                    content += '    "version": "1.0.0"\n}'
                    
                elif file_idx % 10 == 1:
                    # Create a README file
                    file_path = module_dir / "README.md"
                    content = f"# {module_name}\n\n"
                    content += "## Overview\n\n"
                    for i in range(20):
                        content += f"This is paragraph {i} of the documentation.\n\n"
                    
                elif file_idx % 10 == 2:
                    # Create a requirements file
                    file_path = module_dir / "requirements.txt"
                    content = "# Requirements\n"
                    for i in range(30):
                        content += f"package{i}=={i}.0.0\n"
                    
                else:
                    # Create a Python file
                    file_name = f"module_{file_idx}.py"
                    file_path = src_dir / file_name
                    
                    # Generate content with classes and functions
                    content = f'"""{module_name} - {file_name}\n\nThis module contains generated code for performance testing.\n"""\n\n'
                    
                    # Import statements
                    content += "import os\n"
                    content += "import sys\n"
                    content += "import random\n"
                    content += "from typing import List, Dict, Any, Optional\n\n"
                    
                    # Add constants
                    content += f"MODULE_NAME = '{module_name}'\n"
                    content += f"FILE_NAME = '{file_name}'\n"
                    content += f"VERSION = '0.1.{file_idx}'\n\n"
                    
                    # Add classes
                    for class_idx in range(3):
                        class_name = f"Class{class_idx}"
                        content += f"class {class_name}:\n"
                        content += f'    """{class_name} for performance testing."""\n\n'
                        
                        # Add methods
                        content += "    def __init__(self, value: int = 0):\n"
                        content += "        self.value = value\n"
                        content += "        self.name = f'{MODULE_NAME}_{FILE_NAME}_{value}'\n\n"
                        
                        for method_idx in range(5):
                            method_name = f"method_{method_idx}"
                            content += f"    def {method_name}(self, param: int = 0) -> int:\n"
                            content += f'        """Perform operation {method_name}."""\n'
                            content += "        result = self.value + param\n"
                            
                            # Add some complexity
                            content += "        if result > 100:\n"
                            content += "            result = 100\n"
                            content += "        elif result < 0:\n"
                            content += "            result = 0\n"
                            content += "        return result\n\n"
                    
                    # Add functions
                    for func_idx in range(10):
                        func_name = f"function_{func_idx}"
                        content += f"def {func_name}(a: int, b: int) -> int:\n"
                        content += f'    """{func_name} for performance testing."""\n'
                        content += "    result = a * b\n"
                        
                        # Add some complexity
                        content += "    if a > b:\n"
                        content += "        result += a - b\n"
                        content += "    else:\n"
                        content += "        result += b - a\n"
                        content += "    return result\n\n"
                    
                    # Add a main block
                    content += "if __name__ == '__main__':\n"
                    content += "    print(f'Running {MODULE_NAME}/{FILE_NAME}')\n"
                    content += f"    obj = Class0()\n"
                    content += f"    print(obj.method_0(42))\n"
                    content += f"    print(function_0(10, 20))\n"
                
                # Write the file
                self._write_file(file_path, content)
                
                # Update statistics
                stats["total_files"] += 1
                stats["total_lines"] += content.count('\n') + 1
                
                # Create a test file for Python modules
                if file_path.suffix == '.py' and 'module_' in file_path.name:
                    test_file_path = tests_dir / f"test_{file_path.name}"
                    test_content = f'"""Tests for {file_path.name}"""\n\n'
                    test_content += "import unittest\n"
                    test_content += f"from src.{file_path.stem} import *\n\n"
                    
                    test_content += f"class Test{file_path.stem.capitalize()}(unittest.TestCase):\n"
                    test_content += '    """Test case for the module."""\n\n'
                    
                    test_content += "    def setUp(self):\n"
                    test_content += "        self.obj = Class0(42)\n\n"
                    
                    test_content += "    def test_method_0(self):\n"
                    test_content += "        self.assertEqual(self.obj.method_0(10), 52)\n\n"
                    
                    test_content += "    def test_function_0(self):\n"
                    test_content += "        self.assertEqual(function_0(10, 20), 210)\n\n"
                    
                    test_content += "if __name__ == '__main__':\n"
                    test_content += "    unittest.main()\n"
                    
                    self._write_file(test_file_path, test_content)
                    
                    # Update statistics
                    stats["total_files"] += 1
                    stats["total_lines"] += test_content.count('\n') + 1
        
        self.logger.info(f"Generated large codebase with {stats['total_files']} files and {stats['total_lines']} lines")
        return stats
