"""
Master reporting system for GopiAI testing infrastructure.
Coordinates all reporting components and generates comprehensive reports.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import concurrent.futures

# Import our reporting components
from .coverage_reporter import CoverageReporter
from .failure_analyzer import FailureAnalyzer
from .quality_tracker import QualityTracker
from .testing_dashboard import TestingDashboard


@dataclass
class MasterReport:
    """Comprehensive master report combining all testing aspects."""
    timestamp: str
    summary: Dict[str, any]
    coverage_report: Dict
    failure_analysis: Dict
    quality_metrics: Dict
    recommendations: List[str]
    dashboard_url: Optional[str] = None


class MasterReporter:
    """Coordinates all reporting systems and generates master reports."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize reporting components
        self.coverage_reporter = CoverageReporter(project_root)
        self.failure_analyzer = FailureAnalyzer(project_root)
        self.quality_tracker = QualityTracker(project_root)
        self.dashboard = TestingDashboard(project_root)
        
        # Report generation status
        self.generation_status = {
            "coverage": False,
            "failures": False,
            "quality": False,
            "dashboard": False
        }
    
    def generate_master_report(self, run_tests: bool = True, generate_dashboard: bool = True) -> MasterReport:
        """Generate comprehensive master report."""
        print("🎯 Generating master testing report...")
        
        # Run tests first if requested
        if run_tests:
            self._run_comprehensive_tests()
        
        # Generate all reports in parallel
        reports = self._generate_all_reports_parallel()
        
        # Generate dashboard if requested
        dashboard_url = None
        if generate_dashboard:
            dashboard_url = self._generate_dashboard()
        
        # Create master report
        master_report = self._create_master_report(reports, dashboard_url)
        
        # Save master report
        self._save_master_report(master_report)
        
        # Print summary
        self._print_report_summary(master_report)
        
        return master_report
    
    def _run_comprehensive_tests(self):
        """Run comprehensive test suite before generating reports."""
        print("🧪 Running comprehensive test suite...")
        
        try:
            # Run master test runner
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "--tb=short", 
                "--maxfail=50",
                "--timeout=300"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print(f"⚠️ Some tests failed (exit code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print("⏱️ Test execution timed out")
        except Exception as e:
            print(f"❌ Failed to run tests: {e}")
    
    def _generate_all_reports_parallel(self) -> Dict:
        """Generate all reports in parallel for efficiency."""
        print("📊 Generating reports in parallel...")
        
        reports = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all report generation tasks
            future_to_report = {
                executor.submit(self._generate_coverage_report): "coverage",
                executor.submit(self._generate_failure_analysis): "failures",
                executor.submit(self._generate_quality_report): "quality"
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_report):
                report_type = future_to_report[future]
                try:
                    reports[report_type] = future.result()
                    self.generation_status[report_type] = True
                    print(f"✅ {report_type.title()} report generated")
                except Exception as e:
                    print(f"❌ Failed to generate {report_type} report: {e}")
                    reports[report_type] = {}
                    self.generation_status[report_type] = False
        
        return reports
    
    def _generate_coverage_report(self) -> Dict:
        """Generate coverage report."""
        try:
            report = self.coverage_reporter.generate_coverage_report()
            return asdict(report)
        except Exception as e:
            print(f"⚠️ Coverage report generation failed: {e}")
            return {}
    
    def _generate_failure_analysis(self) -> Dict:
        """Generate failure analysis report."""
        try:
            report = self.failure_analyzer.analyze_failures()
            return asdict(report)
        except Exception as e:
            print(f"⚠️ Failure analysis failed: {e}")
            return {}
    
    def _generate_quality_report(self) -> Dict:
        """Generate quality metrics report."""
        try:
            report = self.quality_tracker.generate_report()
            return asdict(report)
        except Exception as e:
            print(f"⚠️ Quality report generation failed: {e}")
            return {}
    
    def _generate_dashboard(self) -> Optional[str]:
        """Generate testing dashboard."""
        try:
            self.dashboard.generate_dashboard()
            self.generation_status["dashboard"] = True
            print("✅ Dashboard generated")
            
            # Start dashboard server in background
            dashboard_url = self.dashboard.start_dashboard_server()
            return dashboard_url
            
        except Exception as e:
            print(f"❌ Dashboard generation failed: {e}")
            self.generation_status["dashboard"] = False
            return None
    
    def _create_master_report(self, reports: Dict, dashboard_url: Optional[str]) -> MasterReport:
        """Create comprehensive master report."""
        # Extract key metrics from individual reports
        summary = self._create_summary(reports)
        
        # Generate master recommendations
        recommendations = self._generate_master_recommendations(reports, summary)
        
        master_report = MasterReport(
            timestamp=datetime.now().isoformat(),
            summary=summary,
            coverage_report=reports.get("coverage", {}),
            failure_analysis=reports.get("failures", {}),
            quality_metrics=reports.get("quality", {}),
            recommendations=recommendations,
            dashboard_url=dashboard_url
        )
        
        return master_report
    
    def _create_summary(self, reports: Dict) -> Dict[str, any]:
        """Create summary metrics from all reports."""
        summary = {
            "generation_timestamp": datetime.now().isoformat(),
            "reports_generated": sum(self.generation_status.values()),
            "total_reports": len(self.generation_status),
            "generation_success_rate": (sum(self.generation_status.values()) / len(self.generation_status)) * 100
        }
        
        # Coverage summary
        coverage_report = reports.get("coverage", {})
        summary["coverage_percentage"] = coverage_report.get("total_coverage", 0)
        summary["modules_analyzed"] = len(coverage_report.get("modules", []))
        
        # Failure summary
        failure_report = reports.get("failures", {})
        summary["total_failures"] = failure_report.get("total_failures", 0)
        summary["failure_categories"] = len(failure_report.get("failures_by_category", {}))
        
        # Quality summary
        quality_report = reports.get("quality", {})
        summary["quality_score"] = quality_report.get("quality_score", 0)
        current_metrics = quality_report.get("current_metrics", {})
        summary["test_count"] = current_metrics.get("test_count", 0)
        summary["success_rate"] = current_metrics.get("success_rate", 0)
        
        # Overall health score
        summary["overall_health_score"] = self._calculate_overall_health(summary)
        
        return summary
    
    def _calculate_overall_health(self, summary: Dict) -> float:
        """Calculate overall project health score."""
        weights = {
            "coverage": 0.3,
            "quality": 0.3,
            "success_rate": 0.25,
            "failure_impact": 0.15
        }
        
        coverage_score = min(100, summary.get("coverage_percentage", 0))
        quality_score = summary.get("quality_score", 0)
        success_rate = summary.get("success_rate", 0)
        
        # Failure impact (inverse - fewer failures is better)
        failure_count = summary.get("total_failures", 0)
        test_count = max(1, summary.get("test_count", 1))
        failure_rate = (failure_count / test_count) * 100
        failure_impact_score = max(0, 100 - failure_rate)
        
        overall_score = (
            coverage_score * weights["coverage"] +
            quality_score * weights["quality"] +
            success_rate * weights["success_rate"] +
            failure_impact_score * weights["failure_impact"]
        )
        
        return round(overall_score, 1)
    
    def _generate_master_recommendations(self, reports: Dict, summary: Dict) -> List[str]:
        """Generate master recommendations based on all reports."""
        recommendations = []
        
        # Overall health recommendations
        health_score = summary.get("overall_health_score", 0)
        if health_score >= 90:
            recommendations.append("🏆 Excellent project health! Maintain current quality standards")
        elif health_score >= 80:
            recommendations.append("👍 Good project health. Focus on minor improvements")
        elif health_score >= 70:
            recommendations.append("⚠️ Acceptable health. Several areas need attention")
        else:
            recommendations.append("🚨 Project health needs significant improvement")
        
        # Coverage recommendations
        coverage = summary.get("coverage_percentage", 0)
        if coverage < 70:
            recommendations.append("📈 PRIORITY: Increase test coverage to at least 70%")
        elif coverage < 85:
            recommendations.append("📊 Good coverage. Push towards 85% for excellent quality")
        
        # Failure recommendations
        failures = summary.get("total_failures", 0)
        if failures > 0:
            recommendations.append(f"🔧 Address {failures} failing tests to improve reliability")
        
        # Quality recommendations
        quality_score = summary.get("quality_score", 0)
        if quality_score < 80:
            recommendations.append("⭐ Focus on improving code quality metrics")
        
        # Success rate recommendations
        success_rate = summary.get("success_rate", 0)
        if success_rate < 95:
            recommendations.append("🎯 Improve test reliability - target 95%+ success rate")
        
        # Add specific recommendations from individual reports
        for report_type, report_data in reports.items():
            if isinstance(report_data, dict) and "recommendations" in report_data:
                report_recs = report_data["recommendations"]
                if isinstance(report_recs, list):
                    # Add top 2 recommendations from each report
                    recommendations.extend(report_recs[:2])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Limit to top 10
    
    def _save_master_report(self, report: MasterReport):
        """Save master report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report
        json_file = self.reports_dir / f"master_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.reports_dir / "master_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Generate executive summary
        self._generate_executive_summary(report, timestamp)
        
        print(f"📊 Master report saved: {json_file}")
    
    def _generate_executive_summary(self, report: MasterReport, timestamp: str):
        """Generate executive summary document."""
        summary_content = f"""
# GopiAI Testing Executive Summary

**Generated:** {report.timestamp}
**Overall Health Score:** {report.summary['overall_health_score']}/100

## Key Metrics

- **Test Coverage:** {report.summary['coverage_percentage']:.1f}%
- **Test Success Rate:** {report.summary['success_rate']:.1f}%
- **Quality Score:** {report.summary['quality_score']:.1f}/100
- **Active Failures:** {report.summary['total_failures']}
- **Modules Analyzed:** {report.summary['modules_analyzed']}

## Health Assessment

{self._get_health_assessment(report.summary['overall_health_score'])}

## Priority Recommendations

{chr(10).join([f"- {rec}" for rec in report.recommendations[:5]])}

## Report Generation Status

- Coverage Report: {"✅" if self.generation_status["coverage"] else "❌"}
- Failure Analysis: {"✅" if self.generation_status["failures"] else "❌"}
- Quality Metrics: {"✅" if self.generation_status["quality"] else "❌"}
- Dashboard: {"✅" if self.generation_status["dashboard"] else "❌"}

## Dashboard Access

{f"🌐 **Dashboard URL:** {report.dashboard_url}" if report.dashboard_url else "❌ Dashboard not available"}

## Next Steps

1. Review detailed reports in the test_reports directory
2. Address priority recommendations above
3. Monitor trends using the dashboard
4. Schedule regular report generation

---
*This report was automatically generated by the GopiAI Testing Infrastructure*
        """
        
        summary_file = self.reports_dir / f"executive_summary_{timestamp}.md"
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        # Save as latest
        latest_summary = self.reports_dir / "executive_summary_latest.md"
        with open(latest_summary, 'w') as f:
            f.write(summary_content)
    
    def _get_health_assessment(self, score: float) -> str:
        """Get health assessment text based on score."""
        if score >= 90:
            return "🟢 **EXCELLENT** - Project is in excellent health with high quality standards maintained across all areas."
        elif score >= 80:
            return "🟡 **GOOD** - Project health is good with minor areas for improvement."
        elif score >= 70:
            return "🟠 **ACCEPTABLE** - Project health is acceptable but requires attention in several areas."
        else:
            return "🔴 **NEEDS IMPROVEMENT** - Project health requires immediate attention and significant improvements."
    
    def _print_report_summary(self, report: MasterReport):
        """Print report summary to console."""
        print("\n" + "="*60)
        print("🎯 GOPIAI TESTING MASTER REPORT SUMMARY")
        print("="*60)
        print(f"📅 Generated: {report.timestamp}")
        print(f"🏥 Overall Health Score: {report.summary['overall_health_score']}/100")
        print(f"📊 Coverage: {report.summary['coverage_percentage']:.1f}%")
        print(f"✅ Success Rate: {report.summary['success_rate']:.1f}%")
        print(f"❌ Failures: {report.summary['total_failures']}")
        print(f"⭐ Quality Score: {report.summary['quality_score']:.1f}/100")
        
        if report.dashboard_url:
            print(f"🌐 Dashboard: {report.dashboard_url}")
        
        print("\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"  {i}. {rec}")
        
        print("\n📁 Detailed reports available in: test_reports/")
        print("="*60)
    
    def open_dashboard(self):
        """Open the testing dashboard in browser."""
        try:
            self.dashboard.serve_dashboard()
        except Exception as e:
            print(f"❌ Failed to open dashboard: {e}")


def main():
    """Generate master testing report."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate GopiAI master testing report")
    parser.add_argument("--no-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--no-dashboard", action="store_true", help="Skip dashboard generation")
    parser.add_argument("--open-dashboard", action="store_true", help="Open dashboard after generation")
    
    args = parser.parse_args()
    
    reporter = MasterReporter()
    
    # Generate master report
    report = reporter.generate_master_report(
        run_tests=not args.no_tests,
        generate_dashboard=not args.no_dashboard
    )
    
    # Open dashboard if requested
    if args.open_dashboard:
        reporter.open_dashboard()


if __name__ == "__main__":
    main()