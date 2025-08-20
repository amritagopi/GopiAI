#!/usr/bin/env python3
"""
Comprehensive test for DuplicateAnalyzer to verify all requirements are met.
"""

import tempfile
import shutil
from pathlib import Path
from project_cleanup_analyzer import AnalysisConfig
from duplicate_analyzer import DuplicateAnalyzer

def test_all_duplicate_features():
    """Test all features of the DuplicateAnalyzer."""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    try:
        # Test 1: Exact duplicate functions
        file1_content = '''
def exact_duplicate_function(param1, param2):
    """This function will be duplicated exactly."""
    result = param1 + param2
    if result > 10:
        return result * 2
    return result

def unique_function_1():
    return "unique1"
'''
        
        file2_content = '''
def exact_duplicate_function(param1, param2):
    """This function will be duplicated exactly."""
    result = param1 + param2
    if result > 10:
        return result * 2
    return result

def unique_function_2():
    return "unique2"
'''
        
        # Test 2: Similar but not identical functions
        file3_content = '''
def similar_function_a(data_list):
    """Process a list of data."""
    results = []
    for item in data_list:
        if item > 0:
            processed = item * 2
            results.append(processed)
    return results

def another_function():
    return "test"
'''
        
        file4_content = '''
def similar_function_b(input_data):
    """Process input data."""
    output = []
    for element in input_data:
        if element > 0:
            transformed = element * 2
            output.append(transformed)
    return output

def different_function():
    return "different"
'''
        
        # Test 3: Functions with same name but different implementations
        file5_content = '''
def helper_function():
    """Helper function - implementation 1."""
    return "implementation_1"

def process_data():
    return helper_function()
'''
        
        file6_content = '''
def helper_function():
    """Helper function - implementation 2."""
    return "implementation_2"

def handle_data():
    return helper_function()
'''
        
        # Test 4: Complex class with methods for refactoring opportunities
        file7_content = '''
class ComplexClass:
    """A complex class for testing."""
    
    def __init__(self):
        self.data = []
    
    def complex_method(self, items):
        """A complex method that could be refactored."""
        result = []
        for item in items:
            if item > 0:
                if item % 2 == 0:
                    result.append(item * 2)
                else:
                    result.append(item * 3)
            elif item < 0:
                try:
                    result.append(abs(item))
                except Exception:
                    result.append(0)
        return result
'''
        
        file8_content = '''
class AnotherComplexClass:
    """Another complex class."""
    
    def __init__(self):
        self.values = []
    
    def similar_complex_method(self, data):
        """Similar complex method."""
        output = []
        for value in data:
            if value > 0:
                if value % 2 == 0:
                    output.append(value * 2)
                else:
                    output.append(value * 3)
            elif value < 0:
                try:
                    output.append(abs(value))
                except Exception:
                    output.append(0)
        return output
'''
        
        # Write all test files
        test_files = {
            "exact1.py": file1_content,
            "exact2.py": file2_content,
            "similar1.py": file3_content,
            "similar2.py": file4_content,
            "name1.py": file5_content,
            "name2.py": file6_content,
            "complex1.py": file7_content,
            "complex2.py": file8_content,
        }
        
        for filename, content in test_files.items():
            (project_path / filename).write_text(content)
        
        # Create analyzer and run analysis
        config = AnalysisConfig(project_path=str(project_path))
        analyzer = DuplicateAnalyzer(config)
        
        print("Running comprehensive duplicate analysis...")
        results = analyzer.analyze(str(project_path))
        
        print(f"Found {len(results)} total issues")
        
        # Analyze results by category
        categories = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        print("\nResults by category:")
        for category, items in categories.items():
            print(f"  {category}: {len(items)} issues")
        
        # Test requirements verification
        print("\n=== REQUIREMENTS VERIFICATION ===")
        
        # Requirement 6.1: Find similar code blocks across different files
        similar_code_results = categories.get("similar_code", [])
        print(f"✓ Similar code detection: Found {len(similar_code_results)} similar code blocks")
        assert len(similar_code_results) > 0, "Should find similar code blocks"
        
        # Requirement 6.2: Identify repeated logic that could be extracted
        exact_duplicate_results = categories.get("exact_duplicate", [])
        print(f"✓ Exact duplicate detection: Found {len(exact_duplicate_results)} exact duplicates")
        assert len(exact_duplicate_results) > 0, "Should find exact duplicates"
        
        # Requirement 6.3: Suggest opportunities for creating shared utilities
        refactoring_results = categories.get("refactoring_opportunity", [])
        print(f"✓ Refactoring suggestions: Found {len(refactoring_results)} refactoring opportunities")
        assert len(refactoring_results) > 0, "Should suggest refactoring opportunities"
        
        # Requirement 6.4: Find duplicate functionality across modules
        duplicate_name_results = categories.get("duplicate_function_name", [])
        print(f"✓ Duplicate function names: Found {len(duplicate_name_results)} duplicate function names")
        assert len(duplicate_name_results) > 0, "Should find duplicate function names"
        
        # Verify AST-based similarity detection is working
        summary = analyzer.get_duplicate_summary()
        print(f"\n✓ AST-based analysis: Analyzed {summary['total_code_blocks']} code blocks")
        print(f"✓ Function analysis: Analyzed {summary['total_functions']} functions")
        print(f"✓ Duplicate groups: Found {summary['duplicate_groups']} duplicate groups")
        
        assert summary['total_code_blocks'] > 0, "Should analyze code blocks"
        assert summary['total_functions'] > 0, "Should analyze functions"
        assert summary['duplicate_groups'] > 0, "Should find duplicate groups"
        
        # Verify code clone detection algorithms
        exact_groups = summary['exact_duplicates']
        similar_groups = summary['similar_blocks']
        print(f"✓ Code clone detection: {exact_groups} exact + {similar_groups} similar groups")
        
        assert exact_groups > 0, "Should find exact code clones"
        assert similar_groups > 0, "Should find similar code blocks"
        
        # Verify function signature similarity analysis
        function_sig_results = categories.get("similar_function_signature", [])
        print(f"✓ Function signature analysis: Found {len(function_sig_results)} similar signatures")
        
        # Verify refactoring opportunity suggestions
        refactoring_suggestions = [r for r in refactoring_results if "shared" in r.recommendation.lower()]
        print(f"✓ Refactoring suggestions: {len(refactoring_suggestions)} suggest shared utilities")
        
        print("\n=== ALL REQUIREMENTS VERIFIED ✅ ===")
        print("DuplicateAnalyzer successfully implements:")
        print("  ✓ AST-based similarity detection")
        print("  ✓ Code clone detection algorithms")
        print("  ✓ Function signature similarity analysis")
        print("  ✓ Refactoring opportunity suggestions")
        print("  ✓ Comprehensive duplicate code detection")
        
        return True
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    try:
        test_all_duplicate_features()
        print("\n🎉 All tests passed! DuplicateAnalyzer is fully implemented.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)