#!/usr/bin/env python3
"""
Simple test script for DuplicateAnalyzer to verify core functionality.
"""

import tempfile
import shutil
from pathlib import Path
from project_cleanup_analyzer import AnalysisConfig
from duplicate_analyzer import DuplicateAnalyzer

def test_duplicate_analyzer():
    """Test the DuplicateAnalyzer with a simple example."""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    try:
        # Create test files with duplicates
        file1_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def unique_function1():
    return "unique1"
'''
        
        file2_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def unique_function2():
    return "unique2"
'''
        
        file3_content = '''
def similar_function(x, y):
    """Calculate sum with different variable names."""
    return x + y

def another_unique():
    return "unique3"
'''
        
        # Write test files
        (project_path / "file1.py").write_text(file1_content)
        (project_path / "file2.py").write_text(file2_content)
        (project_path / "file3.py").write_text(file3_content)
        
        # Create analyzer and run analysis
        config = AnalysisConfig(project_path=str(project_path))
        analyzer = DuplicateAnalyzer(config)
        
        print("Running duplicate analysis...")
        results = analyzer.analyze(str(project_path))
        
        print(f"Found {len(results)} duplicate issues:")
        
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
        
        # Print summary
        summary = analyzer.get_duplicate_summary()
        print(f"\nSUMMARY:")
        print(f"  Code blocks: {summary['total_code_blocks']}")
        print(f"  Functions: {summary['total_functions']}")
        print(f"  Duplicate groups: {summary['duplicate_groups']}")
        print(f"  Exact duplicates: {summary['exact_duplicates']}")
        
        # Verify we found the expected duplicate
        exact_duplicates = [r for r in results if r.category == "exact_duplicate"]
        assert len(exact_duplicates) > 0, "Should find exact duplicate functions"
        
        duplicate_result = exact_duplicates[0]
        print(f"Duplicate result description: {duplicate_result.description}")
        assert "function" in duplicate_result.description.lower(), "Should mention function type"
        assert "file1.py" in duplicate_result.description, "Should mention first file"
        assert "file2.py" in duplicate_result.description, "Should mention second file"
        
        print("\n✅ Test passed! DuplicateAnalyzer is working correctly.")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_duplicate_analyzer()