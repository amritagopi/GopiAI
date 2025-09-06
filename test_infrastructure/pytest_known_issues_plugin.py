"""
Pytest plugin for known issues management.

This plugin automatically handles xfail markers for known issues and provides
integration with the known issues management system.
"""

import json
import pytest
from pathlib import Path

from known_issues_manager import KnownIssuesManager, IssueStatus


class KnownIssuesPlugin:
    """Pytest plugin for known issues management."""
    
    def __init__(self):
        self.issues_manager = None
        self.active_issues = {}
        self.test_results = {}
        
    def pytest_configure(self, config):
        """Configure the plugin."""
        # Initialize issues manager
        root_path = config.rootpath if hasattr(config, 'rootpath') else str(Path.cwd())
        self.issues_manager = KnownIssuesManager(str(root_path))
        
        # Load active issues
        self._load_active_issues()
        
        # Register markers
        self._register_markers(config)
    
    def _load_active_issues(self):
        """Load active known issues."""
        if not self.issues_manager:
            return
        
        try:
            active_issues = (
                self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
                self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
            )
            
            for issue in active_issues:
                marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
                self.active_issues[marker_name] = {
                    "issue_id": issue.issue_id,
                    "title": issue.title,
                    "affected_tests": issue.affected_tests,
                    "priority": issue.priority.value
                }
        
        except Exception as e:
            print(f"⚠️ Warning: Could not load known issues: {e}")
    
    def _register_markers(self, config):
        """Register known issue markers with pytest."""
        for marker_name, issue_info in self.active_issues.items():
            config.addinivalue_line(
                "markers",
                f"{marker_name}: {issue_info['title']} (Issue: {issue_info['issue_id']})"
            )
    
    def pytest_runtest_setup(self, item):
        """Setup hook called before each test."""
        # Check if test should be marked as xfail based on known issues
        self._auto_apply_xfail(item)
    
    def _auto_apply_xfail(self, item):
        """Automatically apply xfail marker if test matches known issue pattern."""
        test_name = item.nodeid
        
        for marker_name, issue_info in self.active_issues.items():
            # Check if this test is in the affected tests list
            if any(test_name in affected_test or affected_test in test_name 
                   for affected_test in issue_info["affected_tests"]):
                
                # Apply xfail marker
                xfail_marker = pytest.mark.xfail(
                    reason=f"{issue_info['title']} (Issue: {issue_info['issue_id']})",
                    strict=False
                )
                item.add_marker(xfail_marker)
                break
    
    def pytest_runtest_makereport(self, item, call):
        """Hook called after test execution to create report."""
        if call.when == "call":
            # Record test result for known issues tracking
            test_name = item.nodeid
            outcome = "passed" if call.excinfo is None else "failed"
            
            # Check if this test is related to a known issue
            for marker_name, issue_info in self.active_issues.items():
                if any(test_name in affected_test or affected_test in test_name 
                       for affected_test in issue_info["affected_tests"]):
                    
                    if issue_info["issue_id"] not in self.test_results:
                        self.test_results[issue_info["issue_id"]] = {
                            "passed": 0,
                            "failed": 0,
                            "total": 0
                        }
                    
                    self.test_results[issue_info["issue_id"]][outcome] += 1
                    self.test_results[issue_info["issue_id"]]["total"] += 1
                    break
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Hook called after test session finishes."""
        # Update known issues with test results
        self._update_issue_progress()
        
        # Generate summary report
        self._generate_session_report(session, exitstatus)
    
    def _update_issue_progress(self):
        """Update known issues with latest test results."""
        if not self.issues_manager or not self.test_results:
            return
        
        try:
            for issue_id, results in self.test_results.items():
                # This would integrate with the resolution progress tracking
                # For now, just log the results
                pass_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
                print(f"📊 Issue {issue_id}: {pass_rate:.1f}% pass rate ({results['passed']}/{results['total']})")
        
        except Exception as e:
            print(f"⚠️ Warning: Could not update issue progress: {e}")
    
    def _generate_session_report(self, session, exitstatus):
        """Generate session report for known issues."""
        if not self.test_results:
            return
        
        report = {
            "session_timestamp": session.startdir.strftime("%Y-%m-%d %H:%M:%S") if hasattr(session, 'startdir') else "unknown",
            "exit_status": exitstatus,
            "known_issues_results": self.test_results,
            "summary": {
                "total_issues_tested": len(self.test_results),
                "issues_improving": 0,
                "issues_stable": 0,
                "issues_declining": 0
            }
        }
        
        # Save session report
        try:
            report_dir = Path("test_infrastructure/known_issues")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / "pytest_session_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        except Exception as e:
            print(f"⚠️ Warning: Could not save session report: {e}")


# Plugin entry point
def pytest_configure(config):
    """Configure the known issues plugin."""
    config.pluginmanager.register(KnownIssuesPlugin(), "known_issues")


def pytest_addoption(parser):
    """Add command line options for known issues."""
    group = parser.getgroup("known_issues")
    group.addoption(
        "--known-issues-report",
        action="store_true",
        default=False,
        help="Generate detailed known issues report after test run"
    )
    group.addoption(
        "--auto-xfail-known-issues",
        action="store_true",
        default=True,
        help="Automatically apply xfail markers for known issues"
    )
    group.addoption(
        "--update-known-issues",
        action="store_true",
        default=False,
        help="Update known issues status based on test results"
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected test items to add known issue markers."""
    if not config.getoption("--auto-xfail-known-issues"):
        return
    
    # This hook allows us to modify test items before they run
    # The actual xfail application is handled in the plugin class
    pass


# Fixtures for known issues testing
@pytest.fixture
def known_issues_manager():
    """Fixture providing access to known issues manager."""
    return KnownIssuesManager()


@pytest.fixture
def skip_if_known_issue(request, known_issues_manager):
    """Fixture to skip tests if they're part of a known issue."""
    test_name = request.node.nodeid
    
    # Check if test is affected by any known issue
    active_issues = (
        known_issues_manager.get_issues_by_status(IssueStatus.OPEN) +
        known_issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
    )
    
    for issue in active_issues:
        if any(test_name in affected_test or affected_test in test_name 
               for affected_test in issue.affected_tests):
            pytest.skip(f"Skipping due to known issue: {issue.title} ({issue.issue_id})")


# Markers for manual use
def pytest_configure(config):
    """Register additional markers."""
    config.addinivalue_line(
        "markers", "known_issue(issue_id): mark test as affected by known issue"
    )
    config.addinivalue_line(
        "markers", "expected_failure: mark test as expected to fail"
    )
    config.addinivalue_line(
        "markers", "flaky: mark test as flaky/unstable"
    )


# Helper functions for test files
def mark_known_issue(issue_id: str, reason: str = None):
    """Helper function to mark a test with a known issue."""
    marker_name = f"xfail_issue_{issue_id.replace('-', '_')}"
    return pytest.mark.xfail(
        reason=reason or f"Known issue: {issue_id}",
        strict=False
    )


def is_known_issue_resolved(issue_id: str) -> bool:
    """Check if a known issue has been resolved."""
    try:
        manager = KnownIssuesManager()
        issues = manager.get_issues_by_status(IssueStatus.RESOLVED)
        return any(issue.issue_id == issue_id for issue in issues)
    except Exception:
        return False


# Example usage in test files:
"""
# In a test file, you can use:

import pytest
from test_infrastructure.pytest_known_issues_plugin import mark_known_issue, is_known_issue_resolved

@mark_known_issue("ISSUE-001", "API timeout issue")
def test_api_call():
    # This test will be marked as xfail if ISSUE-001 is still open
    pass

@pytest.mark.skipif(not is_known_issue_resolved("ISSUE-002"), reason="Waiting for ISSUE-002 resolution")
def test_feature_that_depends_on_fix():
    # This test will be skipped until ISSUE-002 is resolved
    pass

def test_with_fixture(skip_if_known_issue):
    # This test will be automatically skipped if it matches any known issue pattern
    pass
"""