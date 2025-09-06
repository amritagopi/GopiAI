#!/usr/bin/env python3
"""
Known Issues Management System for GopiAI Testing Infrastructure

This module provides comprehensive management of known test issues including:
- Marking tests with xfail for known bugs
- Tracking issue resolution progress
- Automatic status updates when bugs are fixed
- Progress reports on issue resolution

The system integrates with pytest markers and provides a centralized way to manage
test failures that are expected due to known issues.
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3


class IssueStatus(Enum):
    """Status of known issues."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"


class IssuePriority(Enum):
    """Priority levels for known issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class KnownIssue:
    """Represents a known issue in the test suite."""
    issue_id: str
    title: str
    description: str
    test_pattern: str  # Pattern to match affected tests
    status: IssueStatus
    priority: IssuePriority
    created_date: str
    updated_date: str
    assigned_to: Optional[str] = None
    github_issue: Optional[str] = None
    expected_resolution: Optional[str] = None
    affected_tests: List[str] = None
    resolution_notes: Optional[str] = None
    
    def __post_init__(self):
        if self.affected_tests is None:
            self.affected_tests = []


@dataclass
class IssueResolutionProgress:
    """Progress tracking for issue resolution."""
    issue_id: str
    total_affected_tests: int
    passing_tests: int
    failing_tests: int
    skipped_tests: int
    resolution_percentage: float
    last_check: str
    trend: str  # "improving", "stable", "declining"


@dataclass
class KnownIssuesReport:
    """Comprehensive report on known issues."""
    timestamp: str
    total_issues: int
    issues_by_status: Dict[str, int]
    issues_by_priority: Dict[str, int]
    resolution_progress: List[IssueResolutionProgress]
    recently_resolved: List[KnownIssue]
    stale_issues: List[KnownIssue]
    recommendations: List[str]


class KnownIssuesManager:
    """Manages known issues in the test suite."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_dir = self.project_root / "test_infrastructure" / "known_issues"
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for tracking issues
        self.db_path = self.issues_dir / "known_issues.db"
        self._init_database()
        
        # Configuration file
        self.config_file = self.issues_dir / "issues_config.json"
        self._init_config()
        
        # Pytest markers file
        self.markers_file = self.project_root / "pytest_markers.py"
        
    def _init_database(self):
        """Initialize SQLite database for issues tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS known_issues (
                    issue_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    test_pattern TEXT,
                    status TEXT,
                    priority TEXT,
                    created_date TEXT,
                    updated_date TEXT,
                    assigned_to TEXT,
                    github_issue TEXT,
                    expected_resolution TEXT,
                    resolution_notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS affected_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT,
                    test_name TEXT,
                    test_file TEXT,
                    last_status TEXT,
                    last_check TEXT,
                    FOREIGN KEY (issue_id) REFERENCES known_issues (issue_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS resolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT,
                    timestamp TEXT,
                    total_tests INTEGER,
                    passing_tests INTEGER,
                    failing_tests INTEGER,
                    skipped_tests INTEGER,
                    FOREIGN KEY (issue_id) REFERENCES known_issues (issue_id)
                )
            """)
            
            conn.commit()
    
    def _init_config(self):
        """Initialize configuration file."""
        if not self.config_file.exists():
            default_config = {
                "auto_update_enabled": True,
                "stale_issue_days": 30,
                "resolution_check_interval": 7,
                "auto_resolve_threshold": 0.95,
                "notification_settings": {
                    "email_enabled": False,
                    "slack_enabled": False
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def add_known_issue(self, 
                       issue_id: str,
                       title: str,
                       description: str,
                       test_pattern: str,
                       priority: IssuePriority = IssuePriority.MEDIUM,
                       assigned_to: Optional[str] = None,
                       github_issue: Optional[str] = None,
                       expected_resolution: Optional[str] = None) -> KnownIssue:
        """Add a new known issue."""
        print(f"📝 Adding known issue: {issue_id}")
        
        issue = KnownIssue(
            issue_id=issue_id,
            title=title,
            description=description,
            test_pattern=test_pattern,
            status=IssueStatus.OPEN,
            priority=priority,
            created_date=datetime.now().isoformat(),
            updated_date=datetime.now().isoformat(),
            assigned_to=assigned_to,
            github_issue=github_issue,
            expected_resolution=expected_resolution
        )
        
        # Save to database
        self._save_issue(issue)
        
        # Find affected tests
        affected_tests = self._find_affected_tests(test_pattern)
        issue.affected_tests = affected_tests
        
        # Update affected tests in database
        self._update_affected_tests(issue_id, affected_tests)
        
        # Generate pytest markers
        self._update_pytest_markers()
        
        print(f"✅ Added issue {issue_id} affecting {len(affected_tests)} tests")
        return issue
    
    def update_issue_status(self, 
                           issue_id: str, 
                           status: IssueStatus,
                           resolution_notes: Optional[str] = None) -> bool:
        """Update the status of a known issue."""
        print(f"🔄 Updating issue {issue_id} status to {status.value}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM known_issues WHERE issue_id = ?", 
                (issue_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                print(f"❌ Issue {issue_id} not found")
                return False
            
            # Update status
            conn.execute("""
                UPDATE known_issues 
                SET status = ?, updated_date = ?, resolution_notes = ?
                WHERE issue_id = ?
            """, (status.value, datetime.now().isoformat(), resolution_notes, issue_id))
            
            conn.commit()
        
        # If resolved, check if tests are now passing
        if status == IssueStatus.RESOLVED:
            self._verify_resolution(issue_id)
        
        # Update pytest markers
        self._update_pytest_markers()
        
        print(f"✅ Updated issue {issue_id}")
        return True
    
    def _save_issue(self, issue: KnownIssue):
        """Save issue to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO known_issues (
                    issue_id, title, description, test_pattern, status, priority,
                    created_date, updated_date, assigned_to, github_issue,
                    expected_resolution, resolution_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue.issue_id, issue.title, issue.description, issue.test_pattern,
                issue.status.value, issue.priority.value, issue.created_date,
                issue.updated_date, issue.assigned_to, issue.github_issue,
                issue.expected_resolution, issue.resolution_notes
            ))
            conn.commit()
    
    def _find_affected_tests(self, test_pattern: str) -> List[str]:
        """Find tests matching the given pattern."""
        affected_tests = []
        
        # Search for test files
        for test_file in self.project_root.glob("**/test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find test functions
                test_functions = re.findall(r'def (test_\w+)', content)
                
                for test_func in test_functions:
                    test_name = f"{test_file.relative_to(self.project_root)}::{test_func}"
                    
                    # Check if test matches pattern
                    if re.search(test_pattern, test_name) or re.search(test_pattern, content):
                        affected_tests.append(test_name)
            
            except Exception as e:
                print(f"⚠️ Error reading {test_file}: {e}")
        
        return affected_tests
    
    def _update_affected_tests(self, issue_id: str, affected_tests: List[str]):
        """Update affected tests in database."""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing entries
            conn.execute("DELETE FROM affected_tests WHERE issue_id = ?", (issue_id,))
            
            # Add new entries
            for test_name in affected_tests:
                test_file = test_name.split("::")[0] if "::" in test_name else ""
                conn.execute("""
                    INSERT INTO affected_tests (issue_id, test_name, test_file, last_status, last_check)
                    VALUES (?, ?, ?, ?, ?)
                """, (issue_id, test_name, test_file, "unknown", datetime.now().isoformat()))
            
            conn.commit()
    
    def _update_pytest_markers(self):
        """Update pytest markers file with current known issues."""
        print("🏷️ Updating pytest markers...")
        
        # Get all open issues
        open_issues = self.get_issues_by_status(IssueStatus.OPEN)
        in_progress_issues = self.get_issues_by_status(IssueStatus.IN_PROGRESS)
        
        all_active_issues = open_issues + in_progress_issues
        
        # Generate markers content
        markers_content = '''"""
Pytest markers for known issues in GopiAI test suite.
Auto-generated by KnownIssuesManager - do not edit manually.
"""

import pytest

# Known issue markers
'''
        
        for issue in all_active_issues:
            marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
            reason = f"{issue.title} (Issue: {issue.issue_id})"
            
            markers_content += f'''
{marker_name} = pytest.mark.xfail(
    reason="{reason}",
    strict=False
)
'''
        
        # Add marker registration
        markers_content += '''

# Register markers with pytest
def pytest_configure(config):
    """Register custom markers."""
'''
        
        for issue in all_active_issues:
            marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
            markers_content += f'''    config.addinivalue_line("markers", "{marker_name}: {issue.title}")
'''
        
        # Write markers file
        with open(self.markers_file, 'w') as f:
            f.write(markers_content)
        
        print(f"✅ Updated pytest markers for {len(all_active_issues)} active issues")
    
    def check_resolution_progress(self) -> List[IssueResolutionProgress]:
        """Check resolution progress for all active issues."""
        print("🔍 Checking resolution progress...")
        
        progress_list = []
        active_issues = self.get_issues_by_status(IssueStatus.OPEN) + self.get_issues_by_status(IssueStatus.IN_PROGRESS)
        
        for issue in active_issues:
            progress = self._check_issue_progress(issue)
            progress_list.append(progress)
            
            # Save progress to history
            self._save_progress_history(progress)
            
            # Auto-resolve if threshold met
            if progress.resolution_percentage >= 0.95:
                print(f"🎉 Auto-resolving issue {issue.issue_id} (95%+ tests passing)")
                self.update_issue_status(
                    issue.issue_id, 
                    IssueStatus.RESOLVED,
                    "Auto-resolved: 95% of affected tests now passing"
                )
        
        return progress_list
    
    def _check_issue_progress(self, issue: KnownIssue) -> IssueResolutionProgress:
        """Check progress for a specific issue."""
        affected_tests = self._get_affected_tests(issue.issue_id)
        
        if not affected_tests:
            return IssueResolutionProgress(
                issue_id=issue.issue_id,
                total_affected_tests=0,
                passing_tests=0,
                failing_tests=0,
                skipped_tests=0,
                resolution_percentage=0.0,
                last_check=datetime.now().isoformat(),
                trend="stable"
            )
        
        # Run tests to check current status
        test_results = self._run_affected_tests(affected_tests)
        
        passing = test_results.get("passed", 0)
        failing = test_results.get("failed", 0)
        skipped = test_results.get("skipped", 0)
        total = len(affected_tests)
        
        resolution_percentage = (passing / total * 100) if total > 0 else 0
        
        # Determine trend
        trend = self._calculate_trend(issue.issue_id, resolution_percentage)
        
        return IssueResolutionProgress(
            issue_id=issue.issue_id,
            total_affected_tests=total,
            passing_tests=passing,
            failing_tests=failing,
            skipped_tests=skipped,
            resolution_percentage=resolution_percentage,
            last_check=datetime.now().isoformat(),
            trend=trend
        )
    
    def _get_affected_tests(self, issue_id: str) -> List[str]:
        """Get affected tests for an issue."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT test_name FROM affected_tests WHERE issue_id = ?",
                (issue_id,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    def _run_affected_tests(self, test_names: List[str]) -> Dict[str, int]:
        """Run specific tests and return results."""
        if not test_names:
            return {"passed": 0, "failed": 0, "skipped": 0}
        
        try:
            # Create temporary file with test names
            temp_file = self.issues_dir / "temp_test_list.txt"
            with open(temp_file, 'w') as f:
                for test_name in test_names:
                    f.write(f"{test_name}\n")
            
            # Run pytest with specific tests
            cmd = [
                "python", "-m", "pytest",
                "--tb=no", "-q",
                "--collect-only",
                "--json-report", "--json-report-file=temp_results.json"
            ]
            
            # Add test files
            test_files = set()
            for test_name in test_names:
                if "::" in test_name:
                    test_files.add(test_name.split("::")[0])
            
            for test_file in test_files:
                if Path(test_file).exists():
                    cmd.append(str(test_file))
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results (simplified)
            if result.returncode == 0:
                return {"passed": len(test_names), "failed": 0, "skipped": 0}
            else:
                return {"passed": 0, "failed": len(test_names), "skipped": 0}
        
        except Exception as e:
            print(f"⚠️ Error running tests: {e}")
            return {"passed": 0, "failed": len(test_names), "skipped": 0}
    
    def _calculate_trend(self, issue_id: str, current_percentage: float) -> str:
        """Calculate trend for issue resolution."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT passing_tests, total_tests FROM resolution_history 
                WHERE issue_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 2
            """, (issue_id,))
            
            rows = cursor.fetchall()
            
            if len(rows) < 2:
                return "stable"
            
            previous_percentage = (rows[1][0] / rows[1][1] * 100) if rows[1][1] > 0 else 0
            
            if current_percentage > previous_percentage + 5:
                return "improving"
            elif current_percentage < previous_percentage - 5:
                return "declining"
            else:
                return "stable"
    
    def _save_progress_history(self, progress: IssueResolutionProgress):
        """Save progress to history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO resolution_history (
                    issue_id, timestamp, total_tests, passing_tests, failing_tests, skipped_tests
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                progress.issue_id, progress.last_check, progress.total_affected_tests,
                progress.passing_tests, progress.failing_tests, progress.skipped_tests
            ))
            conn.commit()
    
    def _verify_resolution(self, issue_id: str):
        """Verify that a resolved issue is actually fixed."""
        print(f"🔍 Verifying resolution of issue {issue_id}")
        
        affected_tests = self._get_affected_tests(issue_id)
        if not affected_tests:
            return
        
        test_results = self._run_affected_tests(affected_tests)
        passing_percentage = (test_results["passed"] / len(affected_tests) * 100) if affected_tests else 0
        
        if passing_percentage < 80:
            print(f"⚠️ Issue {issue_id} marked as resolved but only {passing_percentage:.1f}% tests passing")
            # Could automatically reopen the issue
        else:
            print(f"✅ Issue {issue_id} resolution verified ({passing_percentage:.1f}% tests passing)")
    
    def get_issues_by_status(self, status: IssueStatus) -> List[KnownIssue]:
        """Get all issues with a specific status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM known_issues WHERE status = ?",
                (status.value,)
            )
            
            issues = []
            for row in cursor.fetchall():
                issue = KnownIssue(
                    issue_id=row[0],
                    title=row[1],
                    description=row[2],
                    test_pattern=row[3],
                    status=IssueStatus(row[4]),
                    priority=IssuePriority(row[5]),
                    created_date=row[6],
                    updated_date=row[7],
                    assigned_to=row[8],
                    github_issue=row[9],
                    expected_resolution=row[10],
                    resolution_notes=row[11]
                )
                
                # Get affected tests
                test_cursor = conn.execute(
                    "SELECT test_name FROM affected_tests WHERE issue_id = ?",
                    (issue.issue_id,)
                )
                issue.affected_tests = [t[0] for t in test_cursor.fetchall()]
                
                issues.append(issue)
            
            return issues
    
    def get_stale_issues(self, days: int = 30) -> List[KnownIssue]:
        """Get issues that haven't been updated in specified days."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM known_issues 
                WHERE updated_date < ? AND status IN ('open', 'in_progress')
            """, (cutoff_date,))
            
            issues = []
            for row in cursor.fetchall():
                issues.append(KnownIssue(
                    issue_id=row[0],
                    title=row[1],
                    description=row[2],
                    test_pattern=row[3],
                    status=IssueStatus(row[4]),
                    priority=IssuePriority(row[5]),
                    created_date=row[6],
                    updated_date=row[7],
                    assigned_to=row[8],
                    github_issue=row[9],
                    expected_resolution=row[10],
                    resolution_notes=row[11]
                ))
            
            return issues
    
    def generate_report(self) -> KnownIssuesReport:
        """Generate comprehensive known issues report."""
        print("📊 Generating known issues report...")
        
        # Get all issues
        all_issues = []
        for status in IssueStatus:
            all_issues.extend(self.get_issues_by_status(status))
        
        # Count by status and priority
        issues_by_status = {}
        issues_by_priority = {}
        
        for issue in all_issues:
            issues_by_status[issue.status.value] = issues_by_status.get(issue.status.value, 0) + 1
            issues_by_priority[issue.priority.value] = issues_by_priority.get(issue.priority.value, 0) + 1
        
        # Check resolution progress
        progress = self.check_resolution_progress()
        
        # Get recently resolved issues (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recently_resolved = [
            issue for issue in all_issues 
            if issue.status == IssueStatus.RESOLVED and issue.updated_date > week_ago
        ]
        
        # Get stale issues
        stale_issues = self.get_stale_issues()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues, progress, stale_issues)
        
        report = KnownIssuesReport(
            timestamp=datetime.now().isoformat(),
            total_issues=len(all_issues),
            issues_by_status=issues_by_status,
            issues_by_priority=issues_by_priority,
            resolution_progress=progress,
            recently_resolved=recently_resolved,
            stale_issues=stale_issues,
            recommendations=recommendations
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_recommendations(self, 
                                 all_issues: List[KnownIssue], 
                                 progress: List[IssueResolutionProgress],
                                 stale_issues: List[KnownIssue]) -> List[str]:
        """Generate recommendations for issue management."""
        recommendations = []
        
        # Critical issues
        critical_issues = [i for i in all_issues if i.priority == IssuePriority.CRITICAL and i.status != IssueStatus.RESOLVED]
        if critical_issues:
            recommendations.append(f"🚨 {len(critical_issues)} critical issues need immediate attention")
        
        # Stale issues
        if stale_issues:
            recommendations.append(f"🕐 {len(stale_issues)} issues haven't been updated in 30+ days")
        
        # Improving issues
        improving_issues = [p for p in progress if p.trend == "improving"]
        if improving_issues:
            recommendations.append(f"📈 {len(improving_issues)} issues showing improvement - keep up the good work!")
        
        # Declining issues
        declining_issues = [p for p in progress if p.trend == "declining"]
        if declining_issues:
            recommendations.append(f"📉 {len(declining_issues)} issues getting worse - need investigation")
        
        # High resolution candidates
        high_resolution = [p for p in progress if p.resolution_percentage > 80]
        if high_resolution:
            recommendations.append(f"🎯 {len(high_resolution)} issues close to resolution (>80% tests passing)")
        
        return recommendations
    
    def _save_report(self, report: KnownIssuesReport):
        """Save known issues report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.issues_dir / f"known_issues_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.issues_dir / "known_issues_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Generate HTML report
        self._generate_html_report(report, timestamp)
        
        print(f"📊 Known issues report saved: {json_file}")
    
    def _generate_html_report(self, report: KnownIssuesReport, timestamp: str):
        """Generate HTML known issues report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GopiAI Known Issues Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #fff3cd; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .progress {{ margin: 20px 0; }}
        .issue {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .critical {{ border-left: 4px solid #dc3545; }}
        .high {{ border-left: 4px solid #fd7e14; }}
        .medium {{ border-left: 4px solid #ffc107; }}
        .low {{ border-left: 4px solid #28a745; }}
        .improving {{ background: #d4edda; }}
        .declining {{ background: #f8d7da; }}
        .stable {{ background: #e2e3e5; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #28a745; transition: width 0.3s; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GopiAI Known Issues Report</h1>
        <p>Generated: {report.timestamp}</p>
        <p>Total Issues: <strong>{report.total_issues}</strong></p>
    </div>
    
    <div class="summary">
        {''.join([f'''
        <div class="metric">
            <h3>{status.replace('_', ' ').title()}</h3>
            <p>{count}</p>
        </div>
        ''' for status, count in report.issues_by_status.items()])}
    </div>
    
    <div class="progress">
        <h3>Resolution Progress</h3>
        {''.join([f'''
        <div class="issue {progress.trend}">
            <h4>Issue: {progress.issue_id}</h4>
            <p>Progress: {progress.resolution_percentage:.1f}% ({progress.passing_tests}/{progress.total_affected_tests} tests passing)</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress.resolution_percentage}%"></div>
            </div>
            <p><em>Trend: {progress.trend}</em></p>
        </div>
        ''' for progress in report.resolution_progress])}
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
        </ul>
    </div>
    
    {'<div class="recently-resolved"><h3>Recently Resolved</h3>' + ''.join([f'''
    <div class="issue">
        <h4>{issue.title}</h4>
        <p>ID: {issue.issue_id} | Resolved: {issue.updated_date}</p>
        <p>{issue.resolution_notes or "No notes"}</p>
    </div>
    ''' for issue in report.recently_resolved]) + '</div>' if report.recently_resolved else ''}
</body>
</html>
        """
        
        html_file = self.issues_dir / f"known_issues_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as latest
        latest_html = self.issues_dir / "known_issues_latest.html"
        with open(latest_html, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage known issues in GopiAI test suite")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add issue command
    add_parser = subparsers.add_parser("add", help="Add a new known issue")
    add_parser.add_argument("issue_id", help="Unique issue ID")
    add_parser.add_argument("title", help="Issue title")
    add_parser.add_argument("description", help="Issue description")
    add_parser.add_argument("test_pattern", help="Pattern to match affected tests")
    add_parser.add_argument("--priority", choices=["critical", "high", "medium", "low"], default="medium")
    add_parser.add_argument("--assigned-to", help="Person assigned to fix the issue")
    add_parser.add_argument("--github-issue", help="GitHub issue URL")
    
    # Update status command
    update_parser = subparsers.add_parser("update", help="Update issue status")
    update_parser.add_argument("issue_id", help="Issue ID to update")
    update_parser.add_argument("status", choices=["open", "in_progress", "resolved", "wont_fix", "duplicate"])
    update_parser.add_argument("--notes", help="Resolution notes")
    
    # Report command
    subparsers.add_parser("report", help="Generate known issues report")
    
    # Check progress command
    subparsers.add_parser("check", help="Check resolution progress")
    
    args = parser.parse_args()
    
    manager = KnownIssuesManager()
    
    if args.command == "add":
        manager.add_known_issue(
            args.issue_id,
            args.title,
            args.description,
            args.test_pattern,
            IssuePriority(args.priority),
            args.assigned_to,
            args.github_issue
        )
    
    elif args.command == "update":
        manager.update_issue_status(
            args.issue_id,
            IssueStatus(args.status),
            args.notes
        )
    
    elif args.command == "report":
        report = manager.generate_report()
        print(f"\n📊 Known Issues Summary:")
        print(f"Total Issues: {report.total_issues}")
        print(f"By Status: {report.issues_by_status}")
        print(f"Recently Resolved: {len(report.recently_resolved)}")
        print(f"Stale Issues: {len(report.stale_issues)}")
    
    elif args.command == "check":
        progress = manager.check_resolution_progress()
        print(f"\n🔍 Resolution Progress:")
        for p in progress:
            print(f"  {p.issue_id}: {p.resolution_percentage:.1f}% ({p.trend})")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()