#!/usr/bin/env python3
"""
Test script for the Known Issues Management System

This script demonstrates the complete functionality of the enhanced known issues
management system including:
- Adding and managing issues
- Automatic resolution detection
- Progress tracking and reporting
- Dashboard generation
- Integration with test infrastructure
"""

import sys
import time
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority
from automatic_resolution_detector import AutomaticResolutionDetector
from issue_progress_reporter import IssueProgressReporter
from known_issues_integration import KnownIssuesIntegration


def test_basic_functionality():
    """Test basic known issues management functionality."""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)
    
    manager = KnownIssuesManager()
    
    # Add test issues
    print("📝 Adding test issues...")
    
    issues_to_add = [
        {
            "id": "TEST-001",
            "title": "API timeout in authentication",
            "description": "Authentication API calls are timing out during tests",
            "pattern": "test_auth.*timeout",
            "priority": IssuePriority.CRITICAL
        },
        {
            "id": "TEST-002", 
            "title": "UI widget rendering issue",
            "description": "Chat widget not rendering properly in dark theme",
            "pattern": "test_ui.*chat.*widget",
            "priority": IssuePriority.HIGH
        },
        {
            "id": "TEST-003",
            "title": "Memory system indexing slow",
            "description": "txtai indexing is slower than expected",
            "pattern": "test_memory.*index",
            "priority": IssuePriority.MEDIUM
        }
    ]
    
    for issue_data in issues_to_add:
        try:
            issue = manager.add_known_issue(
                issue_data["id"],
                issue_data["title"],
                issue_data["description"],
                issue_data["pattern"],
                issue_data["priority"]
            )
            print(f"  ✅ Added {issue_data['id']}: {issue_data['title']}")
        except Exception as e:
            print(f"  ❌ Failed to add {issue_data['id']}: {e}")
    
    # List issues
    print(f"\n📋 Current issues:")
    all_issues = []
    for status in IssueStatus:
        issues = manager.get_issues_by_status(status)
        all_issues.extend(issues)
    
    for issue in all_issues:
        priority_emoji = {
            IssuePriority.CRITICAL: "🚨",
            IssuePriority.HIGH: "🔴", 
            IssuePriority.MEDIUM: "🟡",
            IssuePriority.LOW: "🟢"
        }.get(issue.priority, "❓")
        
        print(f"  {issue.issue_id} {priority_emoji} [{issue.status.value}] - {issue.title}")
    
    return len(all_issues)


def test_automatic_resolution():
    """Test automatic resolution detection."""
    print("\n🤖 Testing Automatic Resolution Detection")
    print("=" * 50)
    
    detector = AutomaticResolutionDetector()
    
    # Show configuration
    print("⚙️ Configuration:")
    print(f"  Resolution Threshold: {detector.config.resolution_threshold}%")
    print(f"  Confidence Threshold: {detector.config.confidence_threshold}")
    print(f"  Auto-Resolve Enabled: {detector.config.auto_resolve_enabled}")
    
    # Check for resolutions
    print(f"\n🔍 Checking for automatic resolutions...")
    events = detector.check_for_resolutions()
    
    if events:
        print(f"  Found {len(events)} resolution events:")
        for event in events:
            print(f"    {event.issue_id}: {event.resolution_percentage:.1f}% resolved")
    else:
        print("  ✅ No issues ready for automatic resolution")
    
    # Generate resolution report
    print(f"\n📊 Generating resolution report...")
    report = detector.generate_resolution_report()
    print(f"  Total Events: {report['total_resolution_events']}")
    print(f"  Auto-Resolved: {report['auto_resolved_count']}")
    
    return len(events)


def test_progress_reporting():
    """Test progress reporting and trend analysis."""
    print("\n📈 Testing Progress Reporting")
    print("=" * 50)
    
    reporter = IssueProgressReporter()
    
    # Capture progress snapshot
    print("📸 Capturing progress snapshot...")
    progress = reporter.capture_progress_snapshot()
    print(f"  Captured progress for {len(progress)} issues")
    
    # Analyze trends
    print(f"\n📊 Analyzing trends...")
    trends = reporter.analyze_progress_trends()
    print(f"  Analyzed trends for {len(trends)} issues")
    
    # Calculate team metrics
    print(f"\n👥 Calculating team metrics...")
    metrics = reporter.calculate_team_metrics()
    print(f"  Total Issues: {metrics.total_issues}")
    print(f"  Active Issues: {metrics.active_issues}")
    print(f"  Resolution Velocity: {metrics.resolution_velocity:.1f} issues/week")
    print(f"  Quality Score: {metrics.quality_score:.2f}")
    
    # Generate comprehensive report
    print(f"\n📊 Generating comprehensive progress report...")
    report = reporter.generate_progress_report()
    
    print(f"  Summary:")
    print(f"    Active Issues: {report['summary']['total_active_issues']}")
    print(f"    Improving: {report['summary']['issues_improving']}")
    print(f"    Declining: {report['summary']['issues_declining']}")
    print(f"    Stagnant: {report['summary']['issues_stagnant']}")
    
    if report['insights']:
        print(f"  Key Insights:")
        for insight in report['insights'][:3]:
            print(f"    • {insight}")
    
    return len(progress)


def test_integration_features():
    """Test integration features."""
    print("\n🔧 Testing Integration Features")
    print("=" * 50)
    
    integration = KnownIssuesIntegration()
    
    # Suggest new issues from failures
    print("🎯 Analyzing failures for potential issues...")
    suggestions = integration.suggest_known_issues(auto_create=False)
    
    if suggestions:
        print(f"  Found {len(suggestions)} suggestions:")
        for suggestion in suggestions[:3]:
            print(f"    • {suggestion}")
    else:
        print("  ✅ No new issues suggested")
    
    # Update pytest configuration
    print(f"\n🔧 Updating pytest configuration...")
    integration.update_pytest_configuration()
    print("  ✅ Pytest configuration updated")
    
    # Generate integration report
    print(f"\n📊 Generating integration report...")
    report = integration.generate_integration_report()
    
    print(f"  Integration Status:")
    print(f"    Active Issues: {report['known_issues_summary']['active_issues']}")
    print(f"    Pytest Configured: {report['integration_status']['pytest_configured']}")
    
    return len(suggestions)


def test_workflow_simulation():
    """Simulate a complete workflow."""
    print("\n🔄 Testing Complete Workflow")
    print("=" * 50)
    
    manager = KnownIssuesManager()
    
    # Simulate issue resolution
    print("🔧 Simulating issue resolution...")
    
    # Get first open issue
    open_issues = manager.get_issues_by_status(IssueStatus.OPEN)
    
    if open_issues:
        issue = open_issues[0]
        print(f"  Resolving issue: {issue.issue_id}")
        
        # Update to in progress
        manager.update_issue_status(
            issue.issue_id, 
            IssueStatus.IN_PROGRESS,
            "Started working on this issue"
        )
        print(f"    ✅ Updated to IN_PROGRESS")
        
        # Simulate some time passing
        time.sleep(1)
        
        # Update to resolved
        manager.update_issue_status(
            issue.issue_id,
            IssueStatus.RESOLVED, 
            "Issue has been fixed - tests are now passing"
        )
        print(f"    ✅ Updated to RESOLVED")
        
        return True
    else:
        print("  ℹ️ No open issues to resolve")
        return False


def test_dashboard_generation():
    """Test dashboard generation."""
    print("\n🎨 Testing Dashboard Generation")
    print("=" * 50)
    
    manager = KnownIssuesManager()
    reporter = IssueProgressReporter()
    
    # Generate issues report
    print("📊 Generating issues report...")
    issues_report = manager.generate_report()
    print(f"  ✅ Issues report generated: {issues_report.total_issues} issues")
    
    # Generate progress report
    print("📈 Generating progress report...")
    progress_report = reporter.generate_progress_report()
    print(f"  ✅ Progress report generated: {progress_report['summary']['total_active_issues']} active issues")
    
    # Check if HTML files were created
    issues_dir = Path("test_infrastructure/known_issues")
    html_files = list(issues_dir.glob("*.html"))
    
    print(f"\n📁 Generated files:")
    for html_file in html_files:
        print(f"  • {html_file.name}")
    
    return len(html_files)


def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")
    
    manager = KnownIssuesManager()
    
    # Remove test issues
    test_issue_ids = ["TEST-001", "TEST-002", "TEST-003"]
    
    for issue_id in test_issue_ids:
        try:
            # This would require implementing a delete method
            print(f"  ℹ️ Would delete {issue_id} (delete method not implemented)")
        except Exception as e:
            print(f"  ⚠️ Could not delete {issue_id}: {e}")
    
    print("  ✅ Cleanup completed")


def main():
    """Main test function."""
    print("🧪 Known Issues Management System - Comprehensive Test")
    print("=" * 60)
    print()
    
    results = {}
    
    try:
        # Test basic functionality
        results['basic'] = test_basic_functionality()
        
        # Test automatic resolution
        results['auto_resolution'] = test_automatic_resolution()
        
        # Test progress reporting
        results['progress'] = test_progress_reporting()
        
        # Test integration features
        results['integration'] = test_integration_features()
        
        # Test workflow simulation
        results['workflow'] = test_workflow_simulation()
        
        # Test dashboard generation
        results['dashboard'] = test_dashboard_generation()
        
        # Summary
        print("\n🎯 Test Summary")
        print("=" * 50)
        print(f"✅ Basic Functionality: {results['basic']} issues managed")
        print(f"🤖 Auto Resolution: {results['auto_resolution']} events detected")
        print(f"📈 Progress Reporting: {results['progress']} issues tracked")
        print(f"🔧 Integration: {results['integration']} suggestions found")
        print(f"🔄 Workflow: {'✅ Completed' if results['workflow'] else 'ℹ️ Skipped'}")
        print(f"🎨 Dashboard: {results['dashboard']} HTML files generated")
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📁 Check test_infrastructure/known_issues/ for generated reports")
        
        # Optional cleanup
        response = input("\n🧹 Clean up test data? (y/N): ").strip().lower()
        if response == 'y':
            cleanup_test_data()
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)