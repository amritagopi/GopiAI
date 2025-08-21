#!/usr/bin/env python3
"""
Comprehensive known issues check and management script.

This script provides a complete workflow for managing known issues:
1. Analyzes recent test failures
2. Suggests new known issues
3. Checks resolution progress
4. Updates pytest configuration
5. Generates comprehensive reports

Usage:
    python run_known_issues_check.py [--auto-create] [--update-markers] [--full-report]
"""

import argparse
import sys
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from known_issues_manager import KnownIssuesManager
from known_issues_integration import KnownIssuesIntegration
from failure_analyzer import FailureAnalyzer


def main():
    """Main function for comprehensive known issues check."""
    parser = argparse.ArgumentParser(
        description="Comprehensive known issues check and management"
    )
    parser.add_argument(
        "--auto-create",
        action="store_true",
        help="Automatically create known issues for recurring failures"
    )
    parser.add_argument(
        "--update-markers",
        action="store_true",
        help="Update pytest markers and configuration"
    )
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate full HTML and JSON reports"
    )
    parser.add_argument(
        "--check-progress",
        action="store_true",
        help="Check resolution progress for all active issues"
    )
    parser.add_argument(
        "--suggest-only",
        action="store_true",
        help="Only suggest new issues, don't create them"
    )
    
    args = parser.parse_args()
    
    print("🔧 GopiAI Known Issues Management")
    print("=" * 50)
    
    # Initialize managers
    issues_manager = KnownIssuesManager()
    integration = KnownIssuesIntegration()
    failure_analyzer = FailureAnalyzer()
    
    # Step 1: Analyze current failures
    print("\n📊 Step 1: Analyzing test failures...")
    failure_report = failure_analyzer.analyze_failures()
    
    if failure_report.total_failures > 0:
        print(f"   Found {failure_report.total_failures} test failures")
        print(f"   Categories: {len(failure_report.failures_by_category)}")
    else:
        print("   ✅ No test failures found")
    
    # Step 2: Suggest or create known issues
    print("\n🎯 Step 2: Analyzing for potential known issues...")
    suggestions = integration.suggest_known_issues(auto_create=args.auto_create)
    
    if suggestions:
        print("   Suggestions:")
        for suggestion in suggestions:
            print(f"   {suggestion}")
    else:
        print("   ✅ No new issues suggested")
    
    # Step 3: Check resolution progress
    if args.check_progress:
        print("\n🔍 Step 3: Checking resolution progress...")
        progress_list = issues_manager.check_resolution_progress()
        
        if progress_list:
            print(f"   Checking {len(progress_list)} active issues:")
            for progress in progress_list:
                trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(progress.trend, "❓")
                print(f"   {progress.issue_id}: {progress.resolution_percentage:.1f}% {trend_emoji}")
        else:
            print("   ✅ No active issues to check")
    
    # Step 4: Update pytest configuration
    if args.update_markers:
        print("\n🔧 Step 4: Updating pytest configuration...")
        integration.update_pytest_configuration()
        issues_manager._update_pytest_markers()
        print("   ✅ Pytest configuration updated")
    
    # Step 5: Generate reports
    print("\n📊 Step 5: Generating reports...")
    
    # Generate known issues report
    issues_report = issues_manager.generate_report()
    print(f"   Known Issues Report: {issues_report.total_issues} total issues")
    
    # Generate integration report
    integration_report = integration.generate_integration_report()
    print(f"   Integration Report: {integration_report['known_issues_summary']['active_issues']} active issues")
    
    if args.full_report:
        print("   📄 Full HTML and JSON reports generated")
    
    # Step 6: Summary and recommendations
    print("\n💡 Summary and Recommendations:")
    print("=" * 50)
    
    # Overall statistics
    active_issues = issues_report.issues_by_status.get("open", 0) + issues_report.issues_by_status.get("in_progress", 0)
    resolved_issues = issues_report.issues_by_status.get("resolved", 0)
    
    print(f"📈 Active Issues: {active_issues}")
    print(f"✅ Resolved Issues: {resolved_issues}")
    print(f"❌ Current Failures: {failure_report.total_failures}")
    
    # Priority recommendations
    if issues_report.recommendations:
        print("\n🎯 Priority Actions:")
        for i, rec in enumerate(issues_report.recommendations[:5], 1):
            print(f"   {i}. {rec}")
    
    # Integration recommendations
    if integration_report["recommendations"]:
        print("\n🔧 Integration Actions:")
        for i, rec in enumerate(integration_report["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # Next steps
    print("\n🚀 Next Steps:")
    
    if not args.auto_create and suggestions:
        print("   • Run with --auto-create to automatically create suggested issues")
    
    if not args.update_markers:
        print("   • Run with --update-markers to update pytest configuration")
    
    if not args.check_progress:
        print("   • Run with --check-progress to check resolution progress")
    
    if active_issues > 0:
        print(f"   • Review and prioritize {active_issues} active issues")
    
    if failure_report.total_failures > 0:
        print(f"   • Investigate {failure_report.total_failures} current test failures")
    
    # File locations
    print("\n📁 Generated Files:")
    print("   • Known Issues Database: test_infrastructure/known_issues/known_issues.db")
    print("   • Reports: test_infrastructure/known_issues/")
    print("   • Pytest Markers: pytest_markers.py")
    
    # Exit with appropriate code
    if failure_report.total_failures > 10 or active_issues > 5:
        print("\n⚠️  High number of issues detected - consider immediate attention")
        return 1
    elif active_issues > 0 or failure_report.total_failures > 0:
        print("\n📋 Issues detected but manageable")
        return 0
    else:
        print("\n✅ All systems healthy!")
        return 0


def run_quick_check():
    """Run a quick check without full analysis."""
    print("🔍 Quick Known Issues Check")
    print("=" * 30)
    
    try:
        issues_manager = KnownIssuesManager()
        
        # Get basic statistics
        from known_issues_manager import IssueStatus
        open_issues = len(issues_manager.get_issues_by_status(IssueStatus.OPEN))
        in_progress = len(issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS))
        resolved = len(issues_manager.get_issues_by_status(IssueStatus.RESOLVED))
        
        print(f"📊 Open: {open_issues} | In Progress: {in_progress} | Resolved: {resolved}")
        
        if open_issues + in_progress == 0:
            print("✅ No active known issues")
        else:
            print(f"⚠️  {open_issues + in_progress} active issues need attention")
        
        return open_issues + in_progress
    
    except Exception as e:
        print(f"❌ Error during quick check: {e}")
        return -1


if __name__ == "__main__":
    # Check if running in quick mode
    if len(sys.argv) == 2 and sys.argv[1] == "--quick":
        exit_code = run_quick_check()
        sys.exit(exit_code if exit_code >= 0 else 1)
    else:
        exit_code = main()
        sys.exit(exit_code)