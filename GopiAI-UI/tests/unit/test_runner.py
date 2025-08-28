#!/usr/bin/env python3
"""
Unit Test Runner for GopiAI-UI

Comprehensive test runner for all UI unit tests.
Provides organized test execution, reporting, and error handling.
"""

import pytest
import sys
import os
from pathlib import Path
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))


class UITestRunner:
    """Test runner for GopiAI-UI unit tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all UI unit tests."""
        logger.info("Starting GopiAI-UI unit tests...")
        
        test_files = [
            "test_main_window.py",
            "test_theme_manager.py", 
            "test_settings_dialog.py",
            "test_model_selector.py",
            "test_user_input_handling.py",
            "test_notification_system.py"
        ]
        
        results = {}
        
        for test_file in test_files:
            logger.info(f"Running tests from {test_file}...")
            result = self._run_test_file(test_file)
            results[test_file] = result
            
        self.results = results
        self._generate_summary()
        return results
    
    def run_specific_test(self, test_name: str) -> Dict[str, Any]:
        """Run a specific test file."""
        logger.info(f"Running specific test: {test_name}")
        
        if not test_name.endswith('.py'):
            test_name += '.py'
            
        result = self._run_test_file(test_name)
        return {test_name: result}
    
    def run_test_category(self, category: str) -> Dict[str, Any]:
        """Run tests by category (ui, integration, slow, etc.)."""
        logger.info(f"Running tests with marker: {category}")
        
        test_path = str(self.test_dir)
        args = [
            test_path,
            "-v",
            "--tb=short",
            f"-m {category}",
            "--color=yes"
        ]
        
        exit_code = pytest.main(args)
        
        return {
            "category": category,
            "exit_code": exit_code,
            "status": "PASSED" if exit_code == 0 else "FAILED"
        }
    
    def _run_test_file(self, test_file: str) -> Dict[str, Any]:
        """Run a single test file."""
        test_path = self.test_dir / test_file
        
        if not test_path.exists():
            logger.error(f"Test file not found: {test_path}")
            return {
                "status": "ERROR",
                "message": f"Test file not found: {test_file}",
                "exit_code": -1
            }
        
        # Run pytest on the specific file
        args = [
            str(test_path),
            "-v",
            "--tb=short",
            "--color=yes",
            "--disable-warnings"
        ]
        
        try:
            exit_code = pytest.main(args)
            status = "PASSED" if exit_code == 0 else "FAILED"
            
            return {
                "status": status,
                "exit_code": exit_code,
                "test_file": test_file
            }
            
        except Exception as e:
            logger.error(f"Error running {test_file}: {e}")
            return {
                "status": "ERROR",
                "message": str(e),
                "exit_code": -1,
                "test_file": test_file
            }
    
    def _generate_summary(self):
        """Generate test summary."""
        if not self.results:
            logger.warning("No test results to summarize")
            return
            
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r.get("status") == "PASSED")
        failed_tests = sum(1 for r in self.results.values() if r.get("status") == "FAILED")
        error_tests = sum(1 for r in self.results.values() if r.get("status") == "ERROR")
        
        logger.info("=" * 60)
        logger.info("UI UNIT TESTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total test files: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Errors: {error_tests}")
        logger.info("=" * 60)
        
        # Detailed results
        for test_file, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            logger.info(f"{test_file}: {status}")
            
            if result.get("message"):
                logger.info(f"  Message: {result['message']}")
        
        logger.info("=" * 60)
    
    def run_with_coverage(self) -> Dict[str, Any]:
        """Run tests with coverage reporting."""
        logger.info("Running UI unit tests with coverage...")
        
        test_path = str(self.test_dir)
        args = [
            test_path,
            "-v",
            "--tb=short",
            "--cov=gopiai.ui",
            "--cov-report=html:htmlcov_ui",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
            "--color=yes"
        ]
        
        exit_code = pytest.main(args)
        
        return {
            "status": "PASSED" if exit_code == 0 else "FAILED",
            "exit_code": exit_code,
            "coverage_enabled": True
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-related tests."""
        return self.run_test_category("slow")
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        return self.run_test_category("integration")
    
    def run_ui_tests(self) -> Dict[str, Any]:
        """Run UI-specific tests."""
        return self.run_test_category("ui")


def main():
    """Main entry point for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI-UI Unit Test Runner")
    parser.add_argument(
        "--test", 
        help="Run specific test file",
        type=str
    )
    parser.add_argument(
        "--category", 
        help="Run tests by category (ui, integration, slow)",
        type=str
    )
    parser.add_argument(
        "--coverage", 
        help="Run tests with coverage reporting",
        action="store_true"
    )
    parser.add_argument(
        "--all", 
        help="Run all unit tests",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    runner = UITestRunner()
    
    try:
        if args.test:
            results = runner.run_specific_test(args.test)
        elif args.category:
            results = runner.run_test_category(args.category)
        elif args.coverage:
            results = runner.run_with_coverage()
        elif args.all:
            results = runner.run_all_tests()
        else:
            # Default: run all tests
            results = runner.run_all_tests()
        
        # Exit with appropriate code
        if isinstance(results, dict):
            if "exit_code" in results:
                sys.exit(results["exit_code"])
            else:
                # Check if any test failed
                failed = any(
                    r.get("status") == "FAILED" or r.get("status") == "ERROR"
                    for r in results.values()
                    if isinstance(r, dict)
                )
                sys.exit(1 if failed else 0)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()