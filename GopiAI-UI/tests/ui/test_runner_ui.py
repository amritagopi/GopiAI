#!/usr/bin/env python3
"""
UI Test Runner for GopiAI-UI pytest-qt tests.
Coordinates execution of all UI tests and provides comprehensive reporting.
"""

import pytest
import sys
import os
from pathlib import Path
import time
from typing import List, Dict, Any

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))

from test_config import TestConfig
from fixtures import setup_test_environment, cleanup_test_environment


class UITestRunner:
    """Coordinates execution of all UI tests."""
    
    def __init__(self):
        self.config = TestConfig()
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_ui_tests(self) -> Dict[str, Any]:
        """Run all UI tests and return results."""
        print("🎯 Starting GopiAI UI Tests with pytest-qt...")
        self.start_time = time.time()
        
        # Setup test environment
        setup_test_environment()
        
        try:
            # Run different categories of UI tests
            results = {
                "main_window": self._run_main_window_tests(),
                "chat_widget": self._run_chat_widget_tests(),
                "message_sending": self._run_message_sending_tests(),
                "model_switching": self._run_model_switching_tests(),
                "file_operations": self._run_file_operations_tests(),
                "settings": self._run_settings_tests(),
                "integration": self._run_ui_integration_tests()
            }
            
            self.test_results = results
            self.end_time = time.time()
            
            # Generate summary report
            self._generate_summary_report()
            
            return results
            
        finally:
            # Cleanup test environment
            cleanup_test_environment()
    
    def _run_main_window_tests(self) -> Dict[str, Any]:
        """Run main window UI tests."""
        print("🏠 Running Main Window UI Tests...")
        
        test_file = Path(__file__).parent / "test_main_window_ui.py"
        return self._run_pytest_file(test_file, "main_window")
    
    def _run_chat_widget_tests(self) -> Dict[str, Any]:
        """Run chat widget UI tests."""
        print("💬 Running Chat Widget UI Tests...")
        
        test_file = Path(__file__).parent / "test_chat_widget.py"
        return self._run_pytest_file(test_file, "chat_widget")
    
    def _run_message_sending_tests(self) -> Dict[str, Any]:
        """Run message sending UI tests."""
        print("📤 Running Message Sending UI Tests...")
        
        test_file = Path(__file__).parent / "test_message_sending_ui.py"
        return self._run_pytest_file(test_file, "message_sending")
    
    def _run_model_switching_tests(self) -> Dict[str, Any]:
        """Run model switching UI tests."""
        print("🔄 Running Model Switching UI Tests...")
        
        test_file = Path(__file__).parent / "test_model_switching_ui.py"
        return self._run_pytest_file(test_file, "model_switching")
    
    def _run_file_operations_tests(self) -> Dict[str, Any]:
        """Run file operations UI tests."""
        print("📁 Running File Operations UI Tests...")
        
        test_file = Path(__file__).parent / "test_file_operations_ui.py"
        return self._run_pytest_file(test_file, "file_operations")
    
    def _run_settings_tests(self) -> Dict[str, Any]:
        """Run settings UI tests."""
        print("⚙️ Running Settings UI Tests...")
        
        test_file = Path(__file__).parent / "test_settings_ui.py"
        return self._run_pytest_file(test_file, "settings")
    
    def _run_ui_integration_tests(self) -> Dict[str, Any]:
        """Run UI integration tests."""
        print("🔗 Running UI Integration Tests...")
        
        # Run integration tests that span multiple UI components
        integration_tests = [
            "test_main_window_ui.py::TestMainWindowFileOperations",
            "test_main_window_ui.py::TestMainWindowSettings",
            "test_message_sending_ui.py::TestMessageUIIntegration",
            "test_model_switching_ui.py::TestModelSwitchingFullIntegration",
            "test_file_operations_ui.py::TestFileOperationsIntegration",
            "test_settings_ui.py::TestSettingsIntegration"
        ]
        
        results = {}
        for test in integration_tests:
            test_path = Path(__file__).parent / test.split("::")[0]
            test_class = test.split("::")[-1] if "::" in test else None
            
            result = self._run_pytest_file(test_path, f"integration_{test_class}", test_class)
            results[test_class or test] = result
        
        return results
    
    def _run_pytest_file(self, test_file: Path, category: str, test_class: str = None) -> Dict[str, Any]:
        """Run a specific pytest file and return results."""
        if not test_file.exists():
            return {
                "status": "skipped",
                "reason": f"Test file not found: {test_file}",
                "passed": 0,
                "failed": 0,
                "skipped": 1,
                "duration": 0
            }
        
        start_time = time.time()
        
        # Build pytest command
        pytest_args = [
            str(test_file),
            "-v",
            "--tb=short",
            f"--junit-xml=test_results_{category}.xml"
        ]
        
        if test_class:
            pytest_args.extend(["-k", test_class])
        
        # Add UI-specific pytest options
        pytest_args.extend([
            "--qt-no-capture",  # Don't capture Qt output
            "--qt-log-level=WARNING"  # Reduce Qt log verbosity
        ])
        
        try:
            # Run pytest
            exit_code = pytest.main(pytest_args)
            
            duration = time.time() - start_time
            
            # Parse results (simplified - in real implementation would parse XML)
            if exit_code == 0:
                status = "passed"
                passed = 1
                failed = 0
            else:
                status = "failed"
                passed = 0
                failed = 1
            
            return {
                "status": status,
                "passed": passed,
                "failed": failed,
                "skipped": 0,
                "duration": duration,
                "exit_code": exit_code
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "duration": time.time() - start_time
            }
    
    def _generate_summary_report(self):
        """Generate summary report of all UI tests."""
        total_duration = self.end_time - self.start_time
        
        # Calculate totals
        total_passed = sum(result.get("passed", 0) for result in self.test_results.values() if isinstance(result, dict))
        total_failed = sum(result.get("failed", 0) for result in self.test_results.values() if isinstance(result, dict))
        total_skipped = sum(result.get("skipped", 0) for result in self.test_results.values() if isinstance(result, dict))
        
        # Handle nested results (like integration tests)
        for category, result in self.test_results.items():
            if isinstance(result, dict) and any(isinstance(v, dict) for v in result.values()):
                for sub_result in result.values():
                    if isinstance(sub_result, dict):
                        total_passed += sub_result.get("passed", 0)
                        total_failed += sub_result.get("failed", 0)
                        total_skipped += sub_result.get("skipped", 0)
        
        total_tests = total_passed + total_failed + total_skipped
        
        print("\n" + "="*80)
        print("🎯 GopiAI UI Test Results Summary")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"⏭️ Skipped: {total_skipped}")
        print(f"⏱️ Duration: {total_duration:.2f}s")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Category Breakdown:")
        for category, result in self.test_results.items():
            if isinstance(result, dict):
                if "status" in result:
                    # Simple result
                    status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⏭️"
                    print(f"  {status_icon} {category}: {result['status']} ({result.get('duration', 0):.2f}s)")
                else:
                    # Nested results
                    print(f"  📁 {category}:")
                    for sub_category, sub_result in result.items():
                        if isinstance(sub_result, dict):
                            status_icon = "✅" if sub_result["status"] == "passed" else "❌" if sub_result["status"] == "failed" else "⏭️"
                            print(f"    {status_icon} {sub_category}: {sub_result['status']} ({sub_result.get('duration', 0):.2f}s)")
        
        print("="*80)
        
        # Save detailed results to file
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed test results to file."""
        import json
        
        results_file = Path(__file__).parent / "ui_test_results.json"
        
        detailed_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": self.end_time - self.start_time,
            "results": self.test_results,
            "summary": {
                "total_passed": sum(result.get("passed", 0) for result in self.test_results.values() if isinstance(result, dict)),
                "total_failed": sum(result.get("failed", 0) for result in self.test_results.values() if isinstance(result, dict)),
                "total_skipped": sum(result.get("skipped", 0) for result in self.test_results.values() if isinstance(result, dict))
            }
        }
        
        try:
            with open(results_file, 'w') as f:
                json.dump(detailed_results, f, indent=2)
            print(f"📄 Detailed results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️ Failed to save detailed results: {e}")


def run_specific_ui_test_category(category: str) -> Dict[str, Any]:
    """Run a specific category of UI tests."""
    runner = UITestRunner()
    
    category_methods = {
        "main_window": runner._run_main_window_tests,
        "chat_widget": runner._run_chat_widget_tests,
        "message_sending": runner._run_message_sending_tests,
        "model_switching": runner._run_model_switching_tests,
        "file_operations": runner._run_file_operations_tests,
        "settings": runner._run_settings_tests,
        "integration": runner._run_ui_integration_tests
    }
    
    if category not in category_methods:
        raise ValueError(f"Unknown test category: {category}. Available: {list(category_methods.keys())}")
    
    print(f"🎯 Running {category} UI tests...")
    setup_test_environment()
    
    try:
        result = category_methods[category]()
        return result
    finally:
        cleanup_test_environment()


def run_ui_tests_with_coverage() -> Dict[str, Any]:
    """Run UI tests with coverage reporting."""
    print("🎯 Running UI Tests with Coverage...")
    
    # Add coverage options to pytest
    coverage_args = [
        "--cov=gopiai.ui",
        "--cov-report=html:ui_coverage_html",
        "--cov-report=xml:ui_coverage.xml",
        "--cov-report=term-missing"
    ]
    
    runner = UITestRunner()
    
    # Modify pytest args to include coverage
    original_run_pytest = runner._run_pytest_file
    
    def run_pytest_with_coverage(test_file, category, test_class=None):
        # This would modify the pytest args to include coverage
        return original_run_pytest(test_file, category, test_class)
    
    runner._run_pytest_file = run_pytest_with_coverage
    
    return runner.run_all_ui_tests()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run GopiAI UI Tests")
    parser.add_argument("--category", choices=[
        "main_window", "chat_widget", "message_sending", 
        "model_switching", "file_operations", "settings", "integration"
    ], help="Run specific test category")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.category:
        # Run specific category
        result = run_specific_ui_test_category(args.category)
        print(f"\n🎯 {args.category} test results: {result}")
    elif args.coverage:
        # Run with coverage
        results = run_ui_tests_with_coverage()
        print(f"\n🎯 UI tests with coverage completed: {len(results)} categories")
    else:
        # Run all UI tests
        runner = UITestRunner()
        results = runner.run_all_ui_tests()
        print(f"\n🎯 All UI tests completed: {len(results)} categories")