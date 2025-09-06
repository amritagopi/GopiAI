#!/usr/bin/env python3
"""
Security test runner for GopiAI comprehensive testing system.

Provides utilities for running security tests with proper configuration and reporting.
Requirements: 7.1, 7.2, 7.3, 7.4
"""

import pytest
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecurityTestResult:
    """Security test result data structure."""
    test_name: str
    requirement: str
    status: str  # PASSED, FAILED, SKIPPED, ERROR
    duration: float
    error_message: Optional[str] = None
    security_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL


@dataclass
class SecurityTestSuite:
    """Security test suite results."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    results: List[SecurityTestResult]


class SecurityTestRunner:
    """Enhanced test runner for security tests."""
    
    def __init__(self):
        self.results = []
        self.start_time = 0
        self.end_time = 0
        
    def run_security_tests(self, test_path: str = None, requirements: List[str] = None) -> SecurityTestSuite:
        """Run security tests with enhanced reporting."""
        self.start_time = time.time()
        
        # Determine test path
        if test_path is None:
            test_path = str(Path(__file__).parent)
        
        # Build pytest arguments
        pytest_args = [
            test_path,
            "-v",
            "--tb=short",
            "-m", "security",
            "--json-report",
            "--json-report-file=security_test_results.json"
        ]
        
        # Filter by requirements if specified
        if requirements:
            requirement_filter = " or ".join([f"requirement_{req}" for req in requirements])
            pytest_args.extend(["-k", requirement_filter])
        
        # Run tests
        exit_code = pytest.main(pytest_args)
        
        self.end_time = time.time()
        
        # Parse results
        return self._parse_results(exit_code)
    
    def run_api_security_tests(self) -> SecurityTestSuite:
        """Run API security tests (Requirement 7.1)."""
        return self.run_security_tests(
            test_path=str(Path(__file__).parent / "test_api_security.py"),
            requirements=["7.1"]
        )
    
    def run_secret_management_tests(self) -> SecurityTestSuite:
        """Run secret management tests (Requirement 7.2)."""
        pytest_args = [
            str(Path(__file__).parent),
            "-v",
            "-k", "secret or api_key or password or environment",
            "-m", "security"
        ]
        
        self.start_time = time.time()
        exit_code = pytest.main(pytest_args)
        self.end_time = time.time()
        
        return self._parse_results(exit_code, "Secret Management Tests")
    
    def run_authentication_tests(self) -> SecurityTestSuite:
        """Run authentication security tests (Requirement 7.3)."""
        pytest_args = [
            str(Path(__file__).parent),
            "-v",
            "-k", "auth or session or token or login",
            "-m", "security"
        ]
        
        self.start_time = time.time()
        exit_code = pytest.main(pytest_args)
        self.end_time = time.time()
        
        return self._parse_results(exit_code, "Authentication Security Tests")
    
    def run_filesystem_security_tests(self) -> SecurityTestSuite:
        """Run file system security tests (Requirement 7.4)."""
        pytest_args = [
            str(Path(__file__).parent),
            "-v",
            "-k", "file or path or upload or directory",
            "-m", "security"
        ]
        
        self.start_time = time.time()
        exit_code = pytest.main(pytest_args)
        self.end_time = time.time()
        
        return self._parse_results(exit_code, "File System Security Tests")
    
    def run_comprehensive_security_scan(self) -> Dict[str, SecurityTestSuite]:
        """Run all security tests with comprehensive reporting."""
        results = {}
        
        print("🔒 Running Comprehensive Security Test Suite")
        print("=" * 50)
        
        # Run API security tests
        print("\n📡 Running API Security Tests (Requirement 7.1)...")
        results["api_security"] = self.run_api_security_tests()
        self._print_suite_summary(results["api_security"])
        
        # Run secret management tests
        print("\n🔐 Running Secret Management Tests (Requirement 7.2)...")
        results["secret_management"] = self.run_secret_management_tests()
        self._print_suite_summary(results["secret_management"])
        
        # Run authentication tests
        print("\n🔑 Running Authentication Security Tests (Requirement 7.3)...")
        results["authentication"] = self.run_authentication_tests()
        self._print_suite_summary(results["authentication"])
        
        # Run file system security tests
        print("\n📁 Running File System Security Tests (Requirement 7.4)...")
        results["filesystem"] = self.run_filesystem_security_tests()
        self._print_suite_summary(results["filesystem"])
        
        # Print overall summary
        self._print_overall_summary(results)
        
        return results
    
    def _parse_results(self, exit_code: int, suite_name: str = "Security Tests") -> SecurityTestSuite:
        """Parse test results from pytest execution."""
        # Try to read JSON report if available
        json_report_path = Path("security_test_results.json")
        
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    report_data = json.load(f)
                
                # Parse JSON report
                return self._parse_json_report(report_data, suite_name)
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse JSON report: {e}")
            finally:
                # Clean up JSON report
                if json_report_path.exists():
                    json_report_path.unlink()
        
        # Fallback to basic result parsing
        return self._create_basic_result(exit_code, suite_name)
    
    def _parse_json_report(self, report_data: Dict[str, Any], suite_name: str) -> SecurityTestSuite:
        """Parse pytest JSON report."""
        summary = report_data.get("summary", {})
        tests = report_data.get("tests", [])
        
        results = []
        for test in tests:
            # Extract requirement from test name or markers
            requirement = self._extract_requirement(test)
            
            # Determine security level
            security_level = self._determine_security_level(test)
            
            result = SecurityTestResult(
                test_name=test.get("nodeid", "unknown"),
                requirement=requirement,
                status=test.get("outcome", "UNKNOWN").upper(),
                duration=test.get("duration", 0.0),
                error_message=self._extract_error_message(test),
                security_level=security_level
            )
            results.append(result)
        
        return SecurityTestSuite(
            suite_name=suite_name,
            total_tests=summary.get("total", 0),
            passed=summary.get("passed", 0),
            failed=summary.get("failed", 0),
            skipped=summary.get("skipped", 0),
            errors=summary.get("error", 0),
            duration=self.end_time - self.start_time,
            results=results
        )
    
    def _create_basic_result(self, exit_code: int, suite_name: str) -> SecurityTestSuite:
        """Create basic result when JSON report is not available."""
        status = "PASSED" if exit_code == 0 else "FAILED"
        
        return SecurityTestSuite(
            suite_name=suite_name,
            total_tests=1,
            passed=1 if exit_code == 0 else 0,
            failed=0 if exit_code == 0 else 1,
            skipped=0,
            errors=0,
            duration=self.end_time - self.start_time,
            results=[
                SecurityTestResult(
                    test_name=suite_name,
                    requirement="Unknown",
                    status=status,
                    duration=self.end_time - self.start_time,
                    security_level="MEDIUM"
                )
            ]
        )
    
    def _extract_requirement(self, test: Dict[str, Any]) -> str:
        """Extract requirement number from test data."""
        test_name = test.get("nodeid", "").lower()
        
        # Map test patterns to requirements
        if any(keyword in test_name for keyword in ["injection", "xss", "csrf", "validation"]):
            return "7.1"
        elif any(keyword in test_name for keyword in ["secret", "api_key", "password", "environment"]):
            return "7.2"
        elif any(keyword in test_name for keyword in ["auth", "session", "token", "login"]):
            return "7.3"
        elif any(keyword in test_name for keyword in ["file", "path", "upload", "directory"]):
            return "7.4"
        else:
            return "7.x"
    
    def _determine_security_level(self, test: Dict[str, Any]) -> str:
        """Determine security level based on test type."""
        test_name = test.get("nodeid", "").lower()
        
        # Critical security tests
        if any(keyword in test_name for keyword in ["injection", "xss", "auth", "secret"]):
            return "CRITICAL"
        
        # High security tests
        elif any(keyword in test_name for keyword in ["csrf", "session", "password"]):
            return "HIGH"
        
        # Medium security tests
        elif any(keyword in test_name for keyword in ["validation", "file", "path"]):
            return "MEDIUM"
        
        # Low security tests
        else:
            return "LOW"
    
    def _extract_error_message(self, test: Dict[str, Any]) -> Optional[str]:
        """Extract error message from test data."""
        if test.get("outcome") in ["failed", "error"]:
            call = test.get("call", {})
            return call.get("longrepr", "Unknown error")
        return None
    
    def _print_suite_summary(self, suite: SecurityTestSuite):
        """Print summary for a test suite."""
        print(f"  📊 {suite.suite_name}")
        print(f"     Total: {suite.total_tests}, Passed: {suite.passed}, Failed: {suite.failed}")
        print(f"     Duration: {suite.duration:.2f}s")
        
        if suite.failed > 0:
            print(f"     ⚠️  {suite.failed} security test(s) failed!")
            for result in suite.results:
                if result.status == "FAILED":
                    print(f"       - {result.test_name} ({result.security_level})")
    
    def _print_overall_summary(self, results: Dict[str, SecurityTestSuite]):
        """Print overall security test summary."""
        print("\n" + "=" * 50)
        print("🔒 SECURITY TEST SUMMARY")
        print("=" * 50)
        
        total_tests = sum(suite.total_tests for suite in results.values())
        total_passed = sum(suite.passed for suite in results.values())
        total_failed = sum(suite.failed for suite in results.values())
        total_duration = sum(suite.duration for suite in results.values())
        
        print(f"📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        # Security level breakdown
        security_levels = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        failed_by_level = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for suite in results.values():
            for result in suite.results:
                security_levels[result.security_level] += 1
                if result.status == "FAILED":
                    failed_by_level[result.security_level] += 1
        
        print(f"\n🎯 Security Level Breakdown:")
        for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            total = security_levels[level]
            failed = failed_by_level[level]
            if total > 0:
                print(f"   {level}: {total-failed}/{total} passed ({failed} failed)")
        
        # Recommendations
        if total_failed > 0:
            print(f"\n⚠️  SECURITY ISSUES DETECTED!")
            print(f"   {total_failed} security test(s) failed.")
            print(f"   Please review and fix security vulnerabilities before deployment.")
        else:
            print(f"\n✅ ALL SECURITY TESTS PASSED!")
            print(f"   System appears to be secure based on current test coverage.")
    
    def generate_security_report(self, results: Dict[str, SecurityTestSuite], output_file: str = "security_report.json"):
        """Generate detailed security report."""
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_suites": len(results),
                "total_tests": sum(suite.total_tests for suite in results.values()),
                "total_passed": sum(suite.passed for suite in results.values()),
                "total_failed": sum(suite.failed for suite in results.values()),
                "total_duration": sum(suite.duration for suite in results.values())
            },
            "suites": {name: asdict(suite) for name, suite in results.items()}
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed security report saved to: {output_file}")


def main():
    """Main entry point for security test runner."""
    runner = SecurityTestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "api":
            results = {"api_security": runner.run_api_security_tests()}
        elif command == "secrets":
            results = {"secret_management": runner.run_secret_management_tests()}
        elif command == "auth":
            results = {"authentication": runner.run_authentication_tests()}
        elif command == "files":
            results = {"filesystem": runner.run_filesystem_security_tests()}
        elif command == "all":
            results = runner.run_comprehensive_security_scan()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python test_runner_security.py [api|secrets|auth|files|all]")
            sys.exit(1)
    else:
        # Default: run all security tests
        results = runner.run_comprehensive_security_scan()
    
    # Generate report
    runner.generate_security_report(results)
    
    # Exit with appropriate code
    total_failed = sum(suite.failed for suite in results.values())
    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()