#!/usr/bin/env python3
"""
Integration Test Runner

Comprehensive test runner for all CrewAI API integration tests.
Manages test execution order, service dependencies, and reporting.

Requirements covered:
- 2.1: API integration testing coordination
- 2.2: Service integration testing management
- 7.1: Security testing coordination
"""

import pytest
import sys
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
# Инициализируем пути проекта
path_manager = setup_project_paths()

try:
    from test_infrastructure.service_manager import ServiceManager
except ImportError:
    from .mock_service_manager import MockServiceManager as ServiceManager


class IntegrationTestRunner:
    """Manages execution of integration tests."""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.test_results = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging for test execution."""
        log_dir = Path.home() / ".gopiai" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "integration_tests.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for running tests."""
        self.logger.info("Checking test prerequisites...")
        
        # Check if CrewAI server can be started
        if not self.service_manager.start_service("crewai_server"):
            self.logger.error("Failed to start CrewAI server")
            return False
        
        # Wait for server to be ready
        if not self._wait_for_server_ready():
            self.logger.error("CrewAI server did not become ready")
            self.service_manager.stop_service("crewai_server")
            return False
        
        self.logger.info("Prerequisites check passed")
        return True
    
    def _wait_for_server_ready(self, timeout: int = 30) -> bool:
        """Wait for CrewAI server to be ready."""
        import requests
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:5051/api/health", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
        
        return False
    
    def run_test_suite(self, test_file: str, verbose: bool = True) -> Dict[str, Any]:
        """Run a specific test suite."""
        self.logger.info(f"Running test suite: {test_file}")
        
        # Prepare pytest arguments
        args = [
            test_file,
            "-v" if verbose else "",
            "--tb=short",
            "--durations=10",
            f"--junitxml={Path.home()}/.gopiai/logs/junit_{Path(test_file).stem}.xml"
        ]
        
        # Filter out empty arguments
        args = [arg for arg in args if arg]
        
        # Run tests
        start_time = time.time()
        exit_code = pytest.main(args)
        end_time = time.time()
        
        result = {
            "test_file": test_file,
            "exit_code": exit_code,
            "duration": end_time - start_time,
            "status": "passed" if exit_code == 0 else "failed"
        }
        
        self.test_results[test_file] = result
        self.logger.info(f"Test suite {test_file} completed with exit code {exit_code}")
        
        return result
    
    def run_all_integration_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all integration tests in the correct order."""
        self.logger.info("Starting comprehensive integration test run")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return {"error": "Prerequisites not met"}
        
        # Define test execution order
        test_files = [
            "test_api_endpoints.py",      # Basic API functionality
            "test_authentication.py",     # Authentication and security
            "test_error_handling.py",     # Error handling
            "test_external_ai_services.py"  # External service integration
        ]
        
        # Get full paths
        test_dir = Path(__file__).parent
        test_files = [str(test_dir / test_file) for test_file in test_files]
        
        # Run each test suite
        overall_start = time.time()
        
        for test_file in test_files:
            if not Path(test_file).exists():
                self.logger.warning(f"Test file not found: {test_file}")
                continue
            
            try:
                result = self.run_test_suite(test_file, verbose)
                
                # Log result
                if result["status"] == "passed":
                    self.logger.info(f"✓ {Path(test_file).name} passed in {result['duration']:.2f}s")
                else:
                    self.logger.error(f"✗ {Path(test_file).name} failed in {result['duration']:.2f}s")
                
            except Exception as e:
                self.logger.error(f"Error running {test_file}: {e}")
                self.test_results[test_file] = {
                    "test_file": test_file,
                    "exit_code": -1,
                    "duration": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        overall_end = time.time()
        
        # Generate summary
        summary = self.generate_summary(overall_end - overall_start)
        
        # Cleanup
        self.cleanup()
        
        return summary
    
    def generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate test execution summary."""
        passed = sum(1 for r in self.test_results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.test_results.values() if r["status"] == "failed")
        errors = sum(1 for r in self.test_results.values() if r["status"] == "error")
        total = len(self.test_results)
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration": total_duration,
            "results": self.test_results
        }
        
        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("INTEGRATION TEST SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total test suites: {total}")
        self.logger.info(f"Passed: {passed}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Errors: {errors}")
        self.logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Total duration: {total_duration:.2f}s")
        self.logger.info("=" * 60)
        
        # Log individual results
        for test_file, result in self.test_results.items():
            status_symbol = "✓" if result["status"] == "passed" else "✗"
            self.logger.info(f"{status_symbol} {Path(test_file).name}: {result['status']} ({result['duration']:.2f}s)")
        
        return summary
    
    def cleanup(self):
        """Clean up resources after test execution."""
        self.logger.info("Cleaning up test resources...")
        
        # Stop services
        self.service_manager.stop_service("crewai_server")
        
        self.logger.info("Cleanup completed")
    
    def run_specific_test_category(self, category: str, verbose: bool = True) -> Dict[str, Any]:
        """Run tests for a specific category."""
        category_mapping = {
            "api": ["test_api_endpoints.py"],
            "auth": ["test_authentication.py"],
            "errors": ["test_error_handling.py"],
            "external": ["test_external_ai_services.py"],
            "security": ["test_authentication.py", "test_error_handling.py"]
        }
        
        if category not in category_mapping:
            return {"error": f"Unknown category: {category}"}
        
        self.logger.info(f"Running {category} tests")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return {"error": "Prerequisites not met"}
        
        test_files = category_mapping[category]
        test_dir = Path(__file__).parent
        
        overall_start = time.time()
        
        for test_file in test_files:
            full_path = str(test_dir / test_file)
            if Path(full_path).exists():
                self.run_test_suite(full_path, verbose)
        
        overall_end = time.time()
        
        summary = self.generate_summary(overall_end - overall_start)
        self.cleanup()
        
        return summary


def main():
    """Main entry point for integration test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CrewAI integration tests")
    parser.add_argument(
        "--category",
        choices=["all", "api", "auth", "errors", "external", "security"],
        default="all",
        help="Test category to run"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except errors"
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    runner = IntegrationTestRunner()
    
    try:
        # Run tests
        if args.category == "all":
            summary = runner.run_all_integration_tests(verbose=args.verbose)
        else:
            summary = runner.run_specific_test_category(args.category, verbose=args.verbose)
        
        # Check for errors
        if "error" in summary:
            print(f"Error: {summary['error']}")
            sys.exit(1)
        
        # Exit with appropriate code
        if summary["failed"] > 0 or summary["errors"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        runner.cleanup()
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        runner.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()