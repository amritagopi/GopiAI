"""
Comprehensive Test Suite for Project Cleanup Analyzer

This module provides a comprehensive test suite for the project cleanup analyzer,
integrating all individual analyzers and testing their combined functionality.
It also includes regression tests using existing GopiAI modules and performance
benchmarks for large codebase analysis.
"""

import os
import sys
import unittest
import tempfile
import shutil
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import analyzer modules
from project_cleanup_analyzer import AnalysisConfig, AnalysisResult
from project_cleanup_orchestrator import ProjectCleanupAnalyzer
from test_project_generator import TestProjectGenerator
from structure_analyzer import StructureAnalyzer
from code_quality_analyzer import CodeQualityAnalyzer
from dead_code_analyzer import DeadCodeAnalyzer
from file_analyzer import FileAnalyzer
from dependency_analyzer import DependencyAnalyzer
from duplicate_analyzer import DuplicateAnalyzer
from conflict_analyzer import ConflictAnalyzer
from documentation_analyzer import DocumentationAnalyzer
from report_generator import ReportGenerator
from analyzer_cache import AnalyzerCache


class ComprehensiveTestSuite(unittest.TestCase):
    """Comprehensive test suite for the project cleanup analyzer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test suite."""
        # Create a temporary directory for test projects
        cls.test_dir = tempfile.mkdtemp(prefix="project_cleanup_test_")
        
        # Create a test project generator
        cls.project_generator = TestProjectGenerator(cls.test_dir)
        
        # Generate a test project with all issue types
        cls.project_path = cls.project_generator.create_project("test_project")
        cls.project_generator.add_structure_issues()
        cls.project_generator.add_code_quality_issues()
        cls.project_generator.add_dead_code_issues()
        cls.project_generator.add_duplicate_code_issues()
        cls.project_generator.add_dependency_issues()
        cls.project_generator.add_documentation_issues()
        cls.project_generator.add_conflict_issues()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(cls.test_dir, 'test_suite.log'))
            ]
        )
        
        cls.logger = logging.getLogger(__name__)
        cls.logger.info(f"Test project created at: {cls.project_path}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after the test suite."""
        # Remove the temporary directory
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up each test."""
        # Create a basic configuration
        self.config = AnalysisConfig(
            project_path=str(self.project_path),
            enable_caching=True,
            incremental_analysis=False,
            analysis_depth="standard"
        )
    
    def test_individual_analyzers(self):
        """Test each analyzer individually."""
        analyzers = [
            (StructureAnalyzer, "structure"),
            (CodeQualityAnalyzer, "code_quality"),
            (DeadCodeAnalyzer, "dead_code"),
            (FileAnalyzer, "file"),
            (DependencyAnalyzer, "dependency"),
            (DuplicateAnalyzer, "duplicate"),
            (ConflictAnalyzer, "conflict"),
            (DocumentationAnalyzer, "documentation")
        ]
        
        for analyzer_class, category in analyzers:
            with self.subTest(analyzer=analyzer_class.__name__):
                # Create the analyzer
                analyzer = analyzer_class(self.config)
                
                # Run analysis
                results = analyzer.analyze(str(self.project_path))
                
                # Check that results were returned
                self.assertIsInstance(results, list)
                self.assertGreater(len(results), 0, f"No results from {analyzer_class.__name__}")
                
                # Check that results have the correct category
                for result in results:
                    self.assertIsInstance(result, AnalysisResult)
                    self.assertEqual(result.category, category)
    
    def test_analyzer_combinations(self):
        """Test combinations of analyzers."""
        # Test pairs of analyzers
        analyzer_pairs = [
            (StructureAnalyzer, CodeQualityAnalyzer),
            (DeadCodeAnalyzer, DuplicateAnalyzer),
            (FileAnalyzer, DependencyAnalyzer),
            (ConflictAnalyzer, DocumentationAnalyzer)
        ]
        
        for analyzer_class1, analyzer_class2 in analyzer_pairs:
            with self.subTest(pair=f"{analyzer_class1.__name__}+{analyzer_class2.__name__}"):
                # Create analyzers
                analyzer1 = analyzer_class1(self.config)
                analyzer2 = analyzer_class2(self.config)
                
                # Run analysis
                results1 = analyzer1.analyze(str(self.project_path))
                results2 = analyzer2.analyze(str(self.project_path))
                
                # Check that both analyzers returned results
                self.assertGreater(len(results1), 0)
                self.assertGreater(len(results2), 0)
                
                # Check that there's no interference between analyzers
                self.assertEqual(
                    len(results1),
                    len(analyzer_class1(self.config).analyze(str(self.project_path)))
                )
                self.assertEqual(
                    len(results2),
                    len(analyzer_class2(self.config).analyze(str(self.project_path)))
                )
    
    def test_full_analysis_pipeline(self):
        """Test the full analysis pipeline with all analyzers."""
        # Create the orchestrator
        orchestrator = ProjectCleanupAnalyzer(config=self.config)
        
        # Run full analysis
        output_path = os.path.join(self.test_dir, "full_analysis_report.md")
        report_path = orchestrator.run_full_analysis(parallel=True, output_path=output_path)
        
        # Check that the report was generated
        self.assertTrue(os.path.exists(report_path))
        
        # Check report content
        with open(report_path, "r") as f:
            content = f.read()
            
            # Check for section headers
            self.assertIn("# Project Cleanup Analysis Report", content)
            self.assertIn("## Summary", content)
            
            # Check for results from each analyzer
            self.assertIn("### Structure Issues", content)
            self.assertIn("### Code Quality Issues", content)
            self.assertIn("### Dead Code Issues", content)
            self.assertIn("### File Issues", content)
            self.assertIn("### Dependency Issues", content)
            self.assertIn("### Duplicate Code Issues", content)
            self.assertIn("### Potential Conflicts", content)
            self.assertIn("### Documentation Issues", content)
    
    def test_regression_with_gopiai_modules(self):
        """Test regression using existing GopiAI modules."""
        # Find the GopiAI modules in the project
        project_root = Path(__file__).parent.parent
        gopiai_modules = [
            d for d in project_root.iterdir()
            if d.is_dir() and d.name.startswith("GopiAI-")
        ]
        
        # Skip the test if no GopiAI modules are found
        if not gopiai_modules:
            self.skipTest("No GopiAI modules found for regression testing")
        
        # Test with each module
        for module_path in gopiai_modules[:2]:  # Limit to 2 modules to keep test time reasonable
            with self.subTest(module=module_path.name):
                # Create a configuration for this module
                module_config = AnalysisConfig(
                    project_path=str(module_path),
                    enable_caching=True,
                    incremental_analysis=False,
                    analysis_depth="quick"  # Use quick analysis for regression tests
                )
                
                # Create the orchestrator
                orchestrator = ProjectCleanupAnalyzer(config=module_config)
                
                # Run analysis
                output_path = os.path.join(self.test_dir, f"{module_path.name}_report.md")
                report_path = orchestrator.run_full_analysis(parallel=True, output_path=output_path)
                
                # Check that the report was generated
                self.assertTrue(os.path.exists(report_path))
    
    def test_edge_cases(self):
        """Test edge cases with specially generated test data."""
        # Create a project with edge cases
        edge_case_project = self.project_generator.create_project("edge_cases")
        
        # Add edge case files
        self.project_generator.add_edge_case_files()
        
        # Create a configuration for edge case testing
        edge_config = AnalysisConfig(
            project_path=str(edge_case_project),
            enable_caching=True,
            incremental_analysis=False,
            analysis_depth="full"  # Use full analysis for edge cases
        )
        
        # Create the orchestrator
        orchestrator = ProjectCleanupAnalyzer(config=edge_config)
        
        # Run analysis
        output_path = os.path.join(self.test_dir, "edge_case_report.md")
        report_path = orchestrator.run_full_analysis(parallel=True, output_path=output_path)
        
        # Check that the report was generated without errors
        self.assertTrue(os.path.exists(report_path))
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for large codebase analysis."""
        # Skip this test if running in CI environment to avoid long-running tests
        if os.environ.get("CI") == "true":
            self.skipTest("Skipping performance benchmarks in CI environment")
        
        # Create a large test project
        large_project = self.project_generator.create_project("large_project")
        
        # Generate a large codebase
        self.project_generator.generate_large_codebase(
            num_modules=5,
            files_per_module=20,
            lines_per_file=200
        )
        
        # Create configurations for benchmarking
        configs = [
            {
                'name': 'baseline',
                'enable_caching': False,
                'incremental_analysis': False,
                'analysis_depth': 'standard'
            },
            {
                'name': 'with_caching',
                'enable_caching': True,
                'incremental_analysis': False,
                'analysis_depth': 'standard'
            },
            {
                'name': 'with_incremental',
                'enable_caching': True,
                'incremental_analysis': True,
                'analysis_depth': 'standard'
            }
        ]
        
        results = {}
        
        # Run benchmarks for each configuration
        for config_dict in configs:
            config_name = config_dict['name']
            
            # Create configuration
            config = AnalysisConfig(
                project_path=str(large_project),
                enable_caching=config_dict['enable_caching'],
                incremental_analysis=config_dict['incremental_analysis'],
                analysis_depth=config_dict['analysis_depth']
            )
            
            # Create orchestrator
            orchestrator = ProjectCleanupAnalyzer(config=config)
            
            # Run analysis and measure time
            start_time = time.time()
            orchestrator.run_full_analysis(
                parallel=True,
                output_path=os.path.join(self.test_dir, f"benchmark_{config_name}.md")
            )
            elapsed = time.time() - start_time
            
            results[config_name] = elapsed
            
            self.logger.info(f"Benchmark {config_name}: {elapsed:.2f} seconds")
        
        # Check that caching improves performance
        if 'baseline' in results and 'with_caching' in results:
            self.assertLess(
                results['with_caching'],
                results['baseline'],
                "Caching should improve performance"
            )
        
        # Check that incremental analysis improves performance on second run
        if 'with_incremental' in results:
            # Run again with the same configuration
            config = AnalysisConfig(
                project_path=str(large_project),
                enable_caching=True,
                incremental_analysis=True,
                analysis_depth='standard'
            )
            
            orchestrator = ProjectCleanupAnalyzer(config=config)
            
            start_time = time.time()
            orchestrator.run_full_analysis(
                parallel=True,
                output_path=os.path.join(self.test_dir, "benchmark_incremental_second.md")
            )
            second_run_time = time.time() - start_time
            
            self.logger.info(f"Benchmark incremental (second run): {second_run_time:.2f} seconds")
            
            # Second run should be faster
            self.assertLess(
                second_run_time,
                results['with_incremental'],
                "Incremental analysis should improve performance on second run"
            )


if __name__ == "__main__":
    unittest.main()