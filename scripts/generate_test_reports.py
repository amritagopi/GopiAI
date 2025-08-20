#!/usr/bin/env python3
"""
GopiAI Test Reporting System
Cross-platform script for generating comprehensive test reports and analysis.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from test_infrastructure.master_reporter import MasterReporter
    from test_infrastructure.coverage_reporter import CoverageReporter
    from test_infrastructure.failure_analyzer import FailureAnalyzer
    from test_infrastructure.quality_tracker import QualityTracker
    from test_infrastructure.testing_dashboard import TestingDashboard
except ImportError as e:
    print(f"❌ Failed to import reporting modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def print_banner():
    """Print application banner."""
    print("\n" + "="*50)
    print("   🧪 GopiAI Test Reporting System")
    print("="*50)


def generate_individual_reports():
    """Generate individual reports separately."""
    print("📊 Generating individual reports...")
    
    reports_generated = 0
    total_reports = 4
    
    # Coverage Report
    try:
        print("\n[1/4] 📈 Generating Coverage Report...")
        coverage_reporter = CoverageReporter()
        coverage_reporter.generate_coverage_report()
        print("✅ Coverage report generated")
        reports_generated += 1
    except Exception as e:
        print(f"❌ Coverage report failed: {e}")
    
    # Failure Analysis
    try:
        print("\n[2/4] 🔍 Analyzing Test Failures...")
        failure_analyzer = FailureAnalyzer()
        failure_analyzer.analyze_failures()
        print("✅ Failure analysis completed")
        reports_generated += 1
    except Exception as e:
        print(f"❌ Failure analysis failed: {e}")
    
    # Quality Metrics
    try:
        print("\n[3/4] ⭐ Tracking Quality Metrics...")
        quality_tracker = QualityTracker()
        quality_tracker.generate_report()
        print("✅ Quality metrics tracked")
        reports_generated += 1
    except Exception as e:
        print(f"❌ Quality tracking failed: {e}")
    
    # Dashboard
    try:
        print("\n[4/4] 🎯 Generating Dashboard...")
        dashboard = TestingDashboard()
        dashboard.generate_dashboard()
        print("✅ Dashboard generated")
        reports_generated += 1
    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
    
    print(f"\n📊 Individual Reports: {reports_generated}/{total_reports} generated successfully")
    return reports_generated == total_reports


def generate_master_report(run_tests=True, generate_dashboard=True):
    """Generate comprehensive master report."""
    print("🎯 Generating Master Report...")
    
    try:
        reporter = MasterReporter()
        report = reporter.generate_master_report(
            run_tests=run_tests,
            generate_dashboard=generate_dashboard
        )
        return report
    except Exception as e:
        print(f"❌ Master report generation failed: {e}")
        return None


def open_dashboard():
    """Open the testing dashboard."""
    try:
        dashboard = TestingDashboard()
        print("🌐 Opening dashboard...")
        dashboard.serve_dashboard()
    except Exception as e:
        print(f"❌ Failed to open dashboard: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GopiAI Test Reporting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_test_reports.py                    # Generate all reports
  python generate_test_reports.py --individual       # Generate individual reports only
  python generate_test_reports.py --no-tests         # Skip running tests
  python generate_test_reports.py --dashboard-only   # Generate dashboard only
  python generate_test_reports.py --open-dashboard   # Open dashboard after generation
        """
    )
    
    parser.add_argument(
        "--individual", 
        action="store_true",
        help="Generate individual reports only (no master report)"
    )
    parser.add_argument(
        "--no-tests", 
        action="store_true",
        help="Skip running tests before generating reports"
    )
    parser.add_argument(
        "--no-dashboard", 
        action="store_true",
        help="Skip dashboard generation"
    )
    parser.add_argument(
        "--dashboard-only", 
        action="store_true",
        help="Generate dashboard only"
    )
    parser.add_argument(
        "--open-dashboard", 
        action="store_true",
        help="Open dashboard in browser after generation"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    # Ensure reports directory exists
    reports_dir = Path("test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    success = True
    
    try:
        if args.dashboard_only:
            # Generate dashboard only
            dashboard = TestingDashboard()
            dashboard.generate_dashboard()
            print("✅ Dashboard generated successfully")
            
        elif args.individual:
            # Generate individual reports only
            success = generate_individual_reports()
            
        else:
            # Generate master report (default)
            report = generate_master_report(
                run_tests=not args.no_tests,
                generate_dashboard=not args.no_dashboard
            )
            success = report is not None
        
        if success and not args.quiet:
            print("\n" + "="*50)
            print("   ✅ Report Generation Complete!")
            print("="*50)
            print(f"📁 Reports location: {reports_dir.absolute()}")
            print("📋 Executive summary: test_reports/executive_summary_latest.md")
            print("🌐 Dashboard: test_reports/dashboard/index.html")
            
            # Show available reports
            print("\n📊 Available Reports:")
            if (reports_dir / "coverage" / "coverage_latest.html").exists():
                print("  • Coverage Report: test_reports/coverage/coverage_latest.html")
            if (reports_dir / "failures" / "failure_analysis_latest.html").exists():
                print("  • Failure Analysis: test_reports/failures/failure_analysis_latest.html")
            if (reports_dir / "quality" / "quality_latest.html").exists():
                print("  • Quality Report: test_reports/quality/quality_latest.html")
        
        # Open dashboard if requested
        if args.open_dashboard:
            print("\n🌐 Opening dashboard...")
            open_dashboard()
            
    except KeyboardInterrupt:
        print("\n⚠️ Report generation interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        success = False
    
    if not success:
        sys.exit(1)
    
    if not args.quiet:
        print("\n🎉 All done! Happy testing!")


if __name__ == "__main__":
    main()