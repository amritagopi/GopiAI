#!/usr/bin/env python3
"""
End-to-End Test Runner for GopiAI System

Specialized test runner for E2E tests with proper service management
and environment setup.
"""

import pytest
import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from test_infrastructure.service_manager import ServiceManager
from test_infrastructure.test_config import TestConfig


class E2ETestRunner:
    """Specialized runner for end-to-end tests."""
    
    def __init__(self):
        self.service_manager = ServiceManager(test_mode=True)
        self.test_config = TestConfig()
        self.logger = self._setup_logging()
        self.services_started = False
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for E2E test runner."""
        logger = logging.getLogger("e2e_test_runner")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def setup_test_environment(self) -> bool:
        """Set up the complete E2E test environment."""
        self.logger.info("Setting up E2E test environment...")
        
        try:
            # Setup test isolation
            self.service_manager.setup_test_isolation()
            
            # Start required services for E2E tests
            required_services = ["crewai_server", "memory_system"]
            
            for service in required_services:
                self.logger.info(f"Starting service: {service}")
                if not self.service_manager.start_service(service):
                    self.logger.error(f"Failed to start {service}")
                    return False
            
            # Wait for all services to be healthy
            self.logger.info("Waiting for services to become healthy...")
            if not self.service_manager.wait_for_all_services_healthy(timeout=120):
                self.logger.error("Services failed to become healthy within timeout")
                return False
            
            # Validate test readiness
            validation_report = self.service_manager.validate_test_readiness()
            if not validation_report["ready"]:
                self.logger.error("System not ready for testing")
                self.logger.error(f"Issues: {validation_report['issues']}")
                return False
            
            self.services_started = True
            self.logger.info("E2E test environment setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup E2E test environment: {e}")
            return False
    
    def teardown_test_environment(self):
        """Clean up the E2E test environment."""
        self.logger.info("Tearing down E2E test environment...")
        
        if self.services_started:
            # Stop all services
            self.service_manager.stop_all_services()
            
            # Clean up test data
            self.service_manager.cleanup_test_isolation()
            
            self.services_started = False
        
        self.logger.info("E2E test environment teardown complete")
    
    def run_e2e_tests(self, test_patterns: List[str] = None, verbose: bool = True) -> Dict[str, Any]:
        """Run E2E tests with proper environment management."""
        self.logger.info("Starting E2E test execution...")
        
        # Setup environment
        if not self.setup_test_environment():
            return {
                "success": False,
                "error": "Failed to setup test environment",
                "tests_run": 0,
                "failures": 0
            }
        
        try:
            # Prepare pytest arguments
            pytest_args = [
                "-v" if verbose else "-q",
                "--tb=short",
                "-m", "e2e",
                "--durations=10",
                "--strict-markers",
                "--disable-warnings"
            ]
            
            # Add test patterns if specified
            if test_patterns:
                for pattern in test_patterns:
                    pytest_args.append(pattern)
            else:
                # Run all E2E tests
                pytest_args.append(str(Path(__file__).parent))
            
            # Add custom markers for E2E tests
            pytest_args.extend([
                "--markers",
                "e2e: End-to-end tests",
                "slow: Slow running tests",
                "requires_services: Tests requiring external services"
            ])
            
            self.logger.info(f"Running pytest with args: {pytest_args}")
            
            # Run the tests
            exit_code = pytest.main(pytest_args)
            
            # Analyze results
            result = {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "environment_healthy": self._check_environment_health()
            }
            
            if exit_code == 0:
                self.logger.info("All E2E tests passed successfully")
            else:
                self.logger.warning(f"E2E tests completed with exit code: {exit_code}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during E2E test execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "environment_healthy": False
            }
        
        finally:
            # Always cleanup
            self.teardown_test_environment()
    
    def _check_environment_health(self) -> bool:
        """Check if the test environment is still healthy."""
        try:
            health_report = self.service_manager.comprehensive_health_check()
            return all(service["healthy"] for service in health_report.values())
        except Exception:
            return False
    
    def run_specific_test_class(self, test_class: str) -> Dict[str, Any]:
        """Run a specific E2E test class."""
        test_pattern = f"**/test_*.py::{test_class}"
        return self.run_e2e_tests([test_pattern])
    
    def run_conversation_flow_tests(self) -> Dict[str, Any]:
        """Run only conversation flow E2E tests."""
        return self.run_specific_test_class("TestCompleteConversationFlow")
    
    def run_memory_persistence_tests(self) -> Dict[str, Any]:
        """Run only memory persistence E2E tests."""
        return self.run_specific_test_class("TestMemoryPersistence")
    
    def run_service_recovery_tests(self) -> Dict[str, Any]:
        """Run only service recovery E2E tests."""
        return self.run_specific_test_class("TestServiceRecovery")
    
    def run_multiple_users_tests(self) -> Dict[str, Any]:
        """Run only multiple users E2E tests."""
        return self.run_specific_test_class("TestMultipleUsers")
    
    def validate_e2e_environment(self) -> Dict[str, Any]:
        """Validate that the E2E environment is properly configured."""
        self.logger.info("Validating E2E test environment...")
        
        validation_results = {
            "overall_status": "unknown",
            "service_manager": False,
            "test_isolation": False,
            "required_services": {},
            "dependencies": {},
            "recommendations": []
        }
        
        try:
            # Check service manager
            validation_results["service_manager"] = self.service_manager is not None
            
            # Check test isolation setup
            validation_results["test_isolation"] = self.service_manager.verify_test_isolation()
            
            # Check required services configuration
            required_services = ["crewai_server", "memory_system"]
            for service in required_services:
                service_config = self.service_manager.service_configs.get(service)
                validation_results["required_services"][service] = {
                    "configured": service_config is not None,
                    "dependencies_met": self.service_manager._check_service_dependencies(service) if service_config else False
                }
            
            # Check Python environments
            # No longer checking specific Python environments as they are managed by the system
            validation_results["dependencies"] = {"status": "not_applicable", "message": "Python environments are managed by the system."}
            
            # Generate recommendations
            if not validation_results["test_isolation"]:
                validation_results["recommendations"].append(
                    "Run setup_test_isolation() before starting E2E tests"
                )
            
            for service, info in validation_results["required_services"].items():
                if not info["configured"]:
                    validation_results["recommendations"].append(
                        f"Configure {service} in service manager"
                    )
                if not info["dependencies_met"]:
                    validation_results["recommendations"].append(
                        f"Install dependencies for {service}"
                    )
            
            # Determine overall status
            all_services_ready = all(
                info["configured"] and info["dependencies_met"]
                for info in validation_results["required_services"].values()
            )
            
            if validation_results["test_isolation"] and all_services_ready:
                validation_results["overall_status"] = "ready"
            elif validation_results["service_manager"]:
                validation_results["overall_status"] = "needs_setup"
            else:
                validation_results["overall_status"] = "not_ready"
            
            self.logger.info(f"E2E environment validation: {validation_results['overall_status']}")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error during environment validation: {e}")
            validation_results["overall_status"] = "error"
            validation_results["error"] = str(e)
            return validation_results


def main():
    """Main entry point for E2E test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI E2E Test Runner")
    parser.add_argument(
        "--validate-only", 
        action="store_true",
        help="Only validate the E2E environment, don't run tests"
    )
    parser.add_argument(
        "--test-class",
        type=str,
        help="Run specific test class (e.g., TestCompleteConversationFlow)"
    )
    parser.add_argument(
        "--conversation-flow",
        action="store_true",
        help="Run only conversation flow tests"
    )
    parser.add_argument(
        "--memory-persistence",
        action="store_true",
        help="Run only memory persistence tests"
    )
    parser.add_argument(
        "--service-recovery",
        action="store_true",
        help="Run only service recovery tests"
    )
    parser.add_argument(
        "--multiple-users",
        action="store_true",
        help="Run only multiple users tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output"
    )
    parser.add_argument(
        "test_patterns",
        nargs="*",
        help="Specific test patterns to run"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = E2ETestRunner()
    
    # Handle validation only
    if args.validate_only:
        validation_results = runner.validate_e2e_environment()
        print(f"\nE2E Environment Validation Results:")
        print(f"Overall Status: {validation_results['overall_status']}")
        
        if validation_results["recommendations"]:
            print("\nRecommendations:")
            for rec in validation_results["recommendations"]:
                print(f"  - {rec}")
        
        return 0 if validation_results["overall_status"] == "ready" else 1
    
    # Handle specific test categories
    if args.conversation_flow:
        result = runner.run_conversation_flow_tests()
    elif args.memory_persistence:
        result = runner.run_memory_persistence_tests()
    elif args.service_recovery:
        result = runner.run_service_recovery_tests()
    elif args.multiple_users:
        result = runner.run_multiple_users_tests()
    elif args.test_class:
        result = runner.run_specific_test_class(args.test_class)
    else:
        # Run all E2E tests or specific patterns
        result = runner.run_e2e_tests(args.test_patterns, args.verbose)
    
    # Print results
    print(f"\nE2E Test Results:")
    print(f"Success: {result['success']}")
    if "exit_code" in result:
        print(f"Exit Code: {result['exit_code']}")
    if "error" in result:
        print(f"Error: {result['error']}")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())