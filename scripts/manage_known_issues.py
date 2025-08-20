#!/usr/bin/env python3
"""
CLI script for managing known issues in GopiAI test suite.

This script provides a convenient command-line interface for:
- Adding new known issues
- Updating issue status
- Checking resolution progress
- Generating reports

Usage examples:
    python manage_known_issues.py add ISSUE-001 "API timeout" "API calls timing out" "test_api_*"
    python manage_known_issues.py update ISSUE-001 resolved --notes "Fixed timeout configuration"
    python manage_known_issues.py report
    python manage_known_issues.py check
"""

import sys
import os
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority


def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    manager = KnownIssuesManager()
    
    if command == "add":
        handle_add_command(manager, sys.argv[2:])
    elif command == "update":
        handle_update_command(manager, sys.argv[2:])
    elif command == "report":
        handle_report_command(manager)
    elif command == "check":
        handle_check_command(manager)
    elif command == "list":
        handle_list_command(manager, sys.argv[2:])
    elif command == "help":
        print_help()
    else:
        print(f"❌ Unknown command: {command}")
        print_help()


def handle_add_command(manager: KnownIssuesManager, args: list):
    """Handle add command."""
    if len(args) < 4:
        print("❌ Usage: add <issue_id> <title> <description> <test_pattern> [--priority <priority>] [--assigned-to <person>] [--github <url>]")
        return
    
    issue_id = args[0]
    title = args[1]
    description = args[2]
    test_pattern = args[3]
    
    # Parse optional arguments
    priority = IssuePriority.MEDIUM
    assigned_to = None
    github_issue = None
    
    i = 4
    while i < len(args):
        if args[i] == "--priority" and i + 1 < len(args):
            try:
                priority = IssuePriority(args[i + 1])
                i += 2
            except ValueError:
                print(f"❌ Invalid priority: {args[i + 1]}")
                return
        elif args[i] == "--assigned-to" and i + 1 < len(args):
            assigned_to = args[i + 1]
            i += 2
        elif args[i] == "--github" and i + 1 < len(args):
            github_issue = args[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        issue = manager.add_known_issue(
            issue_id, title, description, test_pattern,
            priority, assigned_to, github_issue
        )
        print(f"✅ Added issue {issue_id} affecting {len(issue.affected_tests)} tests")
    except Exception as e:
        print(f"❌ Error adding issue: {e}")


def handle_update_command(manager: KnownIssuesManager, args: list):
    """Handle update command."""
    if len(args) < 2:
        print("❌ Usage: update <issue_id> <status> [--notes <notes>]")
        return
    
    issue_id = args[0]
    try:
        status = IssueStatus(args[1])
    except ValueError:
        print(f"❌ Invalid status: {args[1]}")
        print("Valid statuses: open, in_progress, resolved, wont_fix, duplicate")
        return
    
    # Parse notes
    notes = None
    if len(args) > 2 and args[2] == "--notes" and len(args) > 3:
        notes = args[3]
    
    try:
        success = manager.update_issue_status(issue_id, status, notes)
        if success:
            print(f"✅ Updated issue {issue_id} to {status.value}")
        else:
            print(f"❌ Issue {issue_id} not found")
    except Exception as e:
        print(f"❌ Error updating issue: {e}")


def handle_report_command(manager: KnownIssuesManager):
    """Handle report command."""
    try:
        report = manager.generate_report()
        
        print("\n📊 Known Issues Report")
        print("=" * 50)
        print(f"Total Issues: {report.total_issues}")
        print(f"Generated: {report.timestamp}")
        
        print("\n📈 Issues by Status:")
        for status, count in report.issues_by_status.items():
            print(f"  {status.replace('_', ' ').title()}: {count}")
        
        print("\n🎯 Issues by Priority:")
        for priority, count in report.issues_by_priority.items():
            print(f"  {priority.title()}: {count}")
        
        if report.resolution_progress:
            print("\n🔍 Resolution Progress:")
            for progress in report.resolution_progress:
                trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(progress.trend, "❓")
                print(f"  {progress.issue_id}: {progress.resolution_percentage:.1f}% {trend_emoji} ({progress.passing_tests}/{progress.total_affected_tests})")
        
        if report.recently_resolved:
            print(f"\n🎉 Recently Resolved ({len(report.recently_resolved)}):")
            for issue in report.recently_resolved:
                print(f"  {issue.issue_id}: {issue.title}")
        
        if report.stale_issues:
            print(f"\n🕐 Stale Issues ({len(report.stale_issues)}):")
            for issue in report.stale_issues:
                print(f"  {issue.issue_id}: {issue.title} (updated: {issue.updated_date[:10]})")
        
        if report.recommendations:
            print("\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")
        
        print(f"\n📄 Detailed reports saved to: test_infrastructure/known_issues/")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")


def handle_check_command(manager: KnownIssuesManager):
    """Handle check command."""
    try:
        progress_list = manager.check_resolution_progress()
        
        if not progress_list:
            print("✅ No active issues to check")
            return
        
        print("\n🔍 Checking Resolution Progress")
        print("=" * 50)
        
        for progress in progress_list:
            trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(progress.trend, "❓")
            
            print(f"\n{progress.issue_id}:")
            print(f"  Progress: {progress.resolution_percentage:.1f}%")
            print(f"  Tests: {progress.passing_tests} passing, {progress.failing_tests} failing, {progress.skipped_tests} skipped")
            print(f"  Trend: {progress.trend} {trend_emoji}")
            print(f"  Last Check: {progress.last_check[:19]}")
        
        # Summary
        total_issues = len(progress_list)
        improving = len([p for p in progress_list if p.trend == "improving"])
        declining = len([p for p in progress_list if p.trend == "declining"])
        near_resolution = len([p for p in progress_list if p.resolution_percentage > 80])
        
        print(f"\n📊 Summary:")
        print(f"  Total Active Issues: {total_issues}")
        print(f"  Improving: {improving} 📈")
        print(f"  Declining: {declining} 📉")
        print(f"  Near Resolution (>80%): {near_resolution} 🎯")
        
    except Exception as e:
        print(f"❌ Error checking progress: {e}")


def handle_list_command(manager: KnownIssuesManager, args: list):
    """Handle list command."""
    status_filter = None
    if args and args[0] in ["open", "in_progress", "resolved", "wont_fix", "duplicate"]:
        status_filter = IssueStatus(args[0])
    
    try:
        if status_filter:
            issues = manager.get_issues_by_status(status_filter)
            print(f"\n📋 Issues with status: {status_filter.value}")
        else:
            # Get all issues
            issues = []
            for status in IssueStatus:
                issues.extend(manager.get_issues_by_status(status))
            print(f"\n📋 All Issues")
        
        print("=" * 80)
        
        if not issues:
            print("No issues found")
            return
        
        for issue in issues:
            priority_emoji = {
                IssuePriority.CRITICAL: "🚨",
                IssuePriority.HIGH: "🔴",
                IssuePriority.MEDIUM: "🟡",
                IssuePriority.LOW: "🟢"
            }.get(issue.priority, "❓")
            
            print(f"\n{issue.issue_id} {priority_emoji} [{issue.status.value}]")
            print(f"  Title: {issue.title}")
            print(f"  Priority: {issue.priority.value}")
            print(f"  Created: {issue.created_date[:10]}")
            print(f"  Updated: {issue.updated_date[:10]}")
            print(f"  Affected Tests: {len(issue.affected_tests)}")
            if issue.assigned_to:
                print(f"  Assigned: {issue.assigned_to}")
            if issue.github_issue:
                print(f"  GitHub: {issue.github_issue}")
        
        print(f"\nTotal: {len(issues)} issues")
        
    except Exception as e:
        print(f"❌ Error listing issues: {e}")


def print_help():
    """Print help information."""
    help_text = """
🔧 GopiAI Known Issues Manager

USAGE:
    python manage_known_issues.py <command> [arguments]

COMMANDS:
    add <id> <title> <description> <pattern>    Add a new known issue
        --priority <critical|high|medium|low>   Set issue priority (default: medium)
        --assigned-to <person>                  Assign to person
        --github <url>                          Link to GitHub issue
    
    update <id> <status> [--notes <notes>]     Update issue status
        Status: open, in_progress, resolved, wont_fix, duplicate
    
    list [status]                               List issues (optionally filter by status)
    
    check                                       Check resolution progress for active issues
    
    report                                      Generate comprehensive report
    
    help                                        Show this help

EXAMPLES:
    # Add a new critical issue
    python manage_known_issues.py add ISSUE-001 "API timeout" "API calls timing out randomly" "test_api_*" --priority critical
    
    # Update issue status
    python manage_known_issues.py update ISSUE-001 resolved --notes "Fixed timeout configuration"
    
    # List all open issues
    python manage_known_issues.py list open
    
    # Check progress
    python manage_known_issues.py check
    
    # Generate report
    python manage_known_issues.py report

FILES:
    Reports and data are saved to: test_infrastructure/known_issues/
    Pytest markers are updated in: pytest_markers.py
"""
    print(help_text)


if __name__ == "__main__":
    main()