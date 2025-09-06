"""
Coverage reporting system for GopiAI testing infrastructure.
Generates detailed code coverage reports with analysis and recommendations.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import coverage


@dataclass
class CoverageMetrics:
    """Coverage metrics for a module or file."""
    name: str
    statements: int
    missing: int
    excluded: int
    coverage_percent: float
    missing_lines: List[int]
    branch_coverage: Optional[float] = None


@dataclass
class CoverageReport:
    """Complete coverage report with metrics and analysis."""
    timestamp: str
    total_coverage: float
    modules: List[CoverageMetrics]
    summary: Dict[str, float]
    recommendations: List[str]
    trend_data: Optional[Dict[str, float]] = None


class CoverageReporter:
    """Generates and analyzes code coverage reports."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test_reports" / "coverage"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Coverage thresholds
        self.thresholds = {
            "excellent": 90.0,
            "good": 80.0,
            "acceptable": 70.0,
            "poor": 50.0
        }
    
    def generate_coverage_report(self, test_paths: List[str] = None) -> CoverageReport:
        """Generate comprehensive coverage report."""
        print("🔍 Generating coverage report...")
        
        # Run coverage analysis
        coverage_data = self._run_coverage_analysis(test_paths)
        
        # Parse coverage results
        modules = self._parse_coverage_data(coverage_data)
        
        # Calculate summary metrics
        summary = self._calculate_summary(modules)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(modules, summary)
        
        # Load trend data
        trend_data = self._load_trend_data()
        
        report = CoverageReport(
            timestamp=datetime.now().isoformat(),
            total_coverage=summary["total_coverage"],
            modules=modules,
            summary=summary,
            recommendations=recommendations,
            trend_data=trend_data
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _run_coverage_analysis(self, test_paths: List[str] = None) -> Dict:
        """Run coverage analysis using coverage.py."""
        try:
            # Initialize coverage
            cov = coverage.Coverage(
                source=["GopiAI-Core", "GopiAI-UI", "GopiAI-CrewAI", "GopiAI-Assets"],
                omit=[
                    "*/tests/*",
                    "*/test_*",
                    "*/__pycache__/*",
                    "*/venv/*",
                    "*_env/*"
                ]
            )
            
            cov.start()
            
            # Run tests with coverage
            if test_paths:
                for test_path in test_paths:
                    subprocess.run([
                        "python", "-m", "pytest", test_path, "--tb=short"
                    ], capture_output=True)
            else:
                subprocess.run([
                    "python", "-m", "pytest", "--tb=short"
                ], capture_output=True)
            
            cov.stop()
            cov.save()
            
            # Generate coverage data
            coverage_data = {}
            for filename in cov.get_data().measured_files():
                analysis = cov.analysis2(filename)
                coverage_data[filename] = {
                    "statements": analysis[1],
                    "missing": analysis[3],
                    "excluded": analysis[2] if len(analysis) > 2 else [],
                    "coverage": len(analysis[1] - analysis[3]) / len(analysis[1]) * 100 if analysis[1] else 0
                }
            
            return coverage_data
            
        except Exception as e:
            print(f"❌ Coverage analysis failed: {e}")
            return {}
    
    def _parse_coverage_data(self, coverage_data: Dict) -> List[CoverageMetrics]:
        """Parse coverage data into structured metrics."""
        modules = []
        
        for filename, data in coverage_data.items():
            # Extract module name
            path = Path(filename)
            if "GopiAI-" in str(path):
                module_name = str(path).split("GopiAI-")[1].split("/")[0]
            else:
                module_name = path.stem
            
            metrics = CoverageMetrics(
                name=module_name,
                statements=len(data["statements"]),
                missing=len(data["missing"]),
                excluded=len(data["excluded"]),
                coverage_percent=data["coverage"],
                missing_lines=list(data["missing"])
            )
            
            modules.append(metrics)
        
        return modules
    
    def _calculate_summary(self, modules: List[CoverageMetrics]) -> Dict[str, float]:
        """Calculate summary metrics."""
        if not modules:
            return {"total_coverage": 0.0, "modules_count": 0}
        
        total_statements = sum(m.statements for m in modules)
        total_missing = sum(m.missing for m in modules)
        
        total_coverage = ((total_statements - total_missing) / total_statements * 100) if total_statements > 0 else 0
        
        # Module-level statistics
        module_coverages = [m.coverage_percent for m in modules if m.statements > 0]
        avg_module_coverage = sum(module_coverages) / len(module_coverages) if module_coverages else 0
        
        return {
            "total_coverage": round(total_coverage, 2),
            "average_module_coverage": round(avg_module_coverage, 2),
            "modules_count": len(modules),
            "total_statements": total_statements,
            "total_missing": total_missing,
            "well_covered_modules": len([m for m in modules if m.coverage_percent >= 80]),
            "poorly_covered_modules": len([m for m in modules if m.coverage_percent < 50])
        }
    
    def _generate_recommendations(self, modules: List[CoverageMetrics], summary: Dict[str, float]) -> List[str]:
        """Generate coverage improvement recommendations."""
        recommendations = []
        
        total_coverage = summary["total_coverage"]
        
        # Overall coverage recommendations
        if total_coverage < self.thresholds["poor"]:
            recommendations.append(
                f"🚨 Critical: Overall coverage is {total_coverage:.1f}%. "
                f"Immediate action needed to reach minimum {self.thresholds['acceptable']}%"
            )
        elif total_coverage < self.thresholds["acceptable"]:
            recommendations.append(
                f"⚠️ Warning: Coverage is {total_coverage:.1f}%. "
                f"Target {self.thresholds['good']}% for better quality assurance"
            )
        elif total_coverage < self.thresholds["good"]:
            recommendations.append(
                f"📈 Good progress: {total_coverage:.1f}% coverage. "
                f"Push to {self.thresholds['excellent']}% for excellent quality"
            )
        else:
            recommendations.append(
                f"✅ Excellent: {total_coverage:.1f}% coverage maintained!"
            )
        
        # Module-specific recommendations
        poorly_covered = [m for m in modules if m.coverage_percent < 50 and m.statements > 10]
        if poorly_covered:
            recommendations.append(
                f"🎯 Priority modules needing tests: {', '.join([m.name for m in poorly_covered[:3]])}"
            )
        
        # Missing lines recommendations
        high_missing = [m for m in modules if len(m.missing_lines) > 20]
        if high_missing:
            recommendations.append(
                f"📝 Focus on modules with many untested lines: {', '.join([m.name for m in high_missing[:3]])}"
            )
        
        return recommendations
    
    def _load_trend_data(self) -> Optional[Dict[str, float]]:
        """Load historical coverage trend data."""
        trend_file = self.reports_dir / "coverage_trends.json"
        
        if trend_file.exists():
            try:
                with open(trend_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def _save_report(self, report: CoverageReport):
        """Save coverage report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report
        json_file = self.reports_dir / f"coverage_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.reports_dir / "coverage_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Update trend data
        self._update_trend_data(report.total_coverage)
        
        # Generate HTML report
        self._generate_html_report(report, timestamp)
        
        print(f"📊 Coverage report saved: {json_file}")
    
    def _update_trend_data(self, current_coverage: float):
        """Update coverage trend data."""
        trend_file = self.reports_dir / "coverage_trends.json"
        
        trends = {}
        if trend_file.exists():
            try:
                with open(trend_file, 'r') as f:
                    trends = json.load(f)
            except Exception:
                pass
        
        # Add current data point
        date_key = datetime.now().strftime("%Y-%m-%d")
        trends[date_key] = current_coverage
        
        # Keep only last 30 days
        sorted_dates = sorted(trends.keys())
        if len(sorted_dates) > 30:
            for old_date in sorted_dates[:-30]:
                del trends[old_date]
        
        with open(trend_file, 'w') as f:
            json.dump(trends, f, indent=2)
    
    def _generate_html_report(self, report: CoverageReport, timestamp: str):
        """Generate HTML coverage report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GopiAI Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }}
        .modules {{ margin: 20px 0; }}
        .module {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; }}
        .excellent {{ color: #28a745; }}
        .good {{ color: #17a2b8; }}
        .warning {{ color: #ffc107; }}
        .critical {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GopiAI Code Coverage Report</h1>
        <p>Generated: {report.timestamp}</p>
        <p>Total Coverage: <strong>{report.total_coverage:.1f}%</strong></p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Modules</h3>
            <p>{report.summary['modules_count']} total</p>
        </div>
        <div class="metric">
            <h3>Statements</h3>
            <p>{report.summary['total_statements']} total</p>
        </div>
        <div class="metric">
            <h3>Missing</h3>
            <p>{report.summary['total_missing']} lines</p>
        </div>
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
        </ul>
    </div>
    
    <div class="modules">
        <h3>Module Coverage</h3>
        {''.join([f'''
        <div class="module">
            <strong>{module.name}</strong>: {module.coverage_percent:.1f}% 
            ({module.statements - module.missing}/{module.statements} statements)
        </div>
        ''' for module in sorted(report.modules, key=lambda x: x.coverage_percent, reverse=True)])}
    </div>
</body>
</html>
        """
        
        html_file = self.reports_dir / f"coverage_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as latest
        latest_html = self.reports_dir / "coverage_latest.html"
        with open(latest_html, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Generate coverage report."""
    reporter = CoverageReporter()
    report = reporter.generate_coverage_report()
    
    print(f"\n📊 Coverage Report Summary:")
    print(f"Total Coverage: {report.total_coverage:.1f}%")
    print(f"Modules Analyzed: {len(report.modules)}")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()