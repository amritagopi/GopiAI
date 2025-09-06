#!/usr/bin/env python3
"""
Unit Test Runner for GopiAI-CrewAI.

Runs all unit tests and provides comprehensive reporting.
"""

import pytest
import sys
from pathlib import Path
import json
from datetime import datetime
# from test_config import TestConfig

class TestConfig:
    """Simple test configuration class."""
    def __init__(self):
        self.enable_coverage = False


class CrewAIUnitTestRunner:
    """Test runner for GopiAI-CrewAI unit tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.config = TestConfig()
        
    def discover_tests(self):
        """Discover all unit test files."""
        test_files = []
        for test_file in self.test_dir.glob("test_*.py"):
            if test_file.name != "test_runner.py":
                test_files.append(test_file)
        return sorted(test_files)
    
    def run_single_test(self, test_file, verbose=True):
        """Run a single test file."""
        print(f"\n{'='*60}")
        print(f"Running: {test_file.name}")
        print(f"{'='*60}")
        
        # Prepare pytest arguments
        args = [
            str(test_file),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "--color=yes",
            f"--junitxml={self.test_dir}/reports/{test_file.stem}_results.xml"
        ]
        
        # Add coverage if requested
        if self.config.enable_coverage:
            args.extend([
                "--cov=gopiai",
                f"--cov-report=html:{self.test_dir}/coverage/{test_file.stem}",
                "--cov-report=term-missing"
            ])
        
        # Run test
        result = pytest.main(args)
        return result == 0
    
    def run_all_tests(self, verbose=True, stop_on_failure=False):
        """Run all unit tests."""
        print(f"\n{'='*80}")
        print("GopiAI-CrewAI Unit Test Suite")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Create reports directory
        reports_dir = self.test_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Create coverage directory
        if self.config.enable_coverage:
            coverage_dir = self.test_dir / "coverage"
            coverage_dir.mkdir(exist_ok=True)
        
        # Discover tests
        test_files = self.discover_tests()
        print(f"Discovered {len(test_files)} test files:")
        for test_file in test_files:
            print(f"  - {test_file.name}")
        
        # Run tests
        results = {}
        passed = 0
        failed = 0
        
        for test_file in test_files:
            try:
                success = self.run_single_test(test_file, verbose)
                results[test_file.name] = "PASSED" if success else "FAILED"
                
                if success:
                    passed += 1
                else:
                    failed += 1
                    if stop_on_failure:
                        print(f"\nStopping on first failure: {test_file.name}")
                        break
                        
            except Exception as e:
                print(f"Error running {test_file.name}: {e}")
                results[test_file.name] = f"ERROR: {e}"
                failed += 1
                if stop_on_failure:
                    break
        
        # Generate summary
        self._generate_summary(results, passed, failed)
        
        return failed == 0
    
    def run_specific_tests(self, test_patterns, verbose=True):
        """Run tests matching specific patterns."""
        print(f"\n{'='*80}")
        print("Running Specific Tests")
        print(f"Patterns: {', '.join(test_patterns)}")
        print(f"{'='*80}")
        
        # Build pytest arguments
        args = []
        for pattern in test_patterns:
            args.extend(["-k", pattern])
        
        args.extend([
            str(self.test_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "--color=yes"
        ])
        
        # Run tests
        result = pytest.main(args)
        return result == 0
    
    def run_by_category(self, category, verbose=True):
        """Run tests by category (markers)."""
        print(f"\n{'='*80}")
        print(f"Running {category.upper()} Tests")
        print(f"{'='*80}")
        
        # Build pytest arguments
        args = [
            str(self.test_dir),
            "-m", category,
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings",
            "--color=yes"
        ]
        
        # Add coverage if requested
        if self.config.enable_coverage:
            args.extend([
                "--cov=gopiai",
                f"--cov-report=html:{self.test_dir}/coverage/{category}",
                "--cov-report=term-missing"
            ])
        
        # Run tests
        result = pytest.main(args)
        return result == 0
    
    def _generate_summary(self, results, passed, failed):
        """Generate test summary report."""
        total = passed + failed
        
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            print(f"\nFAILED TESTS:")
            for test_name, result in results.items():
                if result != "PASSED":
                    print(f"  ❌ {test_name}: {result}")
        
        if passed > 0:
            print(f"\nPASSED TESTS:")
            for test_name, result in results.items():
                if result == "PASSED":
                    print(f"  ✅ {test_name}")
        
        # Save summary to file
        summary_file = self.test_dir / "reports" / "test_summary.json"
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed/total*100) if total > 0 else 0,
            "results": results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\nDetailed results saved to: {summary_file}")
        print(f"{'='*80}")
    
    def check_dependencies(self):
        """Check if all required dependencies are available."""
        print("Checking test dependencies...")
        
        required_packages = [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-xdist"
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (missing)")
                missing.append(package)
        
        if missing:
            print(f"\nMissing packages: {', '.join(missing)}")
            print("Install with: pip install " + " ".join(missing))
            return False
        
        print("All dependencies available!")
        return True
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        if not self.config.enable_coverage:
            print("Coverage reporting is disabled")
            return
        
        print("Generating coverage report...")
        
        # Run tests with coverage
        args = [
            str(self.test_dir),
            "--cov=gopiai",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing",
            "--cov-fail-under=60"
        ]
        
        result = pytest.main(args)
        
        if result == 0:
            print("✅ Coverage report generated successfully")
            print("HTML report: htmlcov/index.html")
            print("XML report: coverage.xml")
        else:
            print("❌ Coverage report generation failed")


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI-CrewAI Unit Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    parser.add_argument("--stop-on-failure", "-x", action="store_true", help="Stop on first failure")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--category", "-m", help="Run tests by category/marker")
    parser.add_argument("--pattern", "-k", action="append", help="Run tests matching pattern")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    parser.add_argument("--list-tests", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = CrewAIUnitTestRunner()
    
    # Check dependencies if requested
    if args.check_deps:
        return 0 if runner.check_dependencies() else 1
    
    # List tests if requested
    if args.list_tests:
        test_files = runner.discover_tests()
        print(f"Available test files ({len(test_files)}):")
        for test_file in test_files:
            print(f"  - {test_file.name}")
        return 0
    
    # Set verbosity
    verbose = args.verbose and not args.quiet
    
    # Enable coverage if requested
    if args.coverage:
        runner.config.enable_coverage = True
    
    # Run tests based on arguments
    success = True
    
    if args.category:
        success = runner.run_by_category(args.category, verbose)
    elif args.pattern:
        success = runner.run_specific_tests(args.pattern, verbose)
    else:
        success = runner.run_all_tests(verbose, args.stop_on_failure)
    
    # Generate coverage report if requested
    if args.coverage:
        runner.generate_coverage_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())