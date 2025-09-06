"""
Quality metrics tracking system for GopiAI testing infrastructure.
Tracks code quality metrics over time and identifies trends.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
import sqlite3


@dataclass
class QualityMetrics:
    """Quality metrics for a specific time point."""
    timestamp: str
    coverage_percentage: float
    test_count: int
    failure_count: int
    success_rate: float
    performance_score: float
    security_score: float
    code_complexity: float
    technical_debt_hours: float
    lines_of_code: int
    test_lines_of_code: int


@dataclass
class QualityTrend:
    """Trend analysis for quality metrics."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend_direction: str  # "improving", "declining", "stable"
    recommendation: str


@dataclass
class QualityReport:
    """Complete quality tracking report."""
    timestamp: str
    current_metrics: QualityMetrics
    trends: List[QualityTrend]
    quality_score: float
    recommendations: List[str]
    historical_data: List[QualityMetrics]


class QualityTracker:
    """Tracks and analyzes code quality metrics over time."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test_reports" / "quality"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.reports_dir / "quality_metrics.db"
        self._init_database()
        
        # Quality thresholds
        self.thresholds = {
            "coverage": {"excellent": 90, "good": 80, "acceptable": 70},
            "success_rate": {"excellent": 95, "good": 90, "acceptable": 85},
            "performance": {"excellent": 90, "good": 80, "acceptable": 70},
            "security": {"excellent": 95, "good": 90, "acceptable": 85}
        }
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    coverage_percentage REAL,
                    test_count INTEGER,
                    failure_count INTEGER,
                    success_rate REAL,
                    performance_score REAL,
                    security_score REAL,
                    code_complexity REAL,
                    technical_debt_hours REAL,
                    lines_of_code INTEGER,
                    test_lines_of_code INTEGER
                )
            """)
            conn.commit()
    
    def collect_current_metrics(self) -> QualityMetrics:
        """Collect current quality metrics."""
        print("📊 Collecting quality metrics...")
        
        # Get coverage metrics
        coverage = self._get_coverage_metrics()
        
        # Get test metrics
        test_metrics = self._get_test_metrics()
        
        # Get performance metrics
        performance_score = self._get_performance_score()
        
        # Get security metrics
        security_score = self._get_security_score()
        
        # Get code complexity
        complexity = self._get_code_complexity()
        
        # Get technical debt
        tech_debt = self._estimate_technical_debt()
        
        # Get lines of code
        loc_metrics = self._get_lines_of_code()
        
        metrics = QualityMetrics(
            timestamp=datetime.now().isoformat(),
            coverage_percentage=coverage,
            test_count=test_metrics["total"],
            failure_count=test_metrics["failures"],
            success_rate=test_metrics["success_rate"],
            performance_score=performance_score,
            security_score=security_score,
            code_complexity=complexity,
            technical_debt_hours=tech_debt,
            lines_of_code=loc_metrics["source"],
            test_lines_of_code=loc_metrics["test"]
        )
        
        return metrics
    
    def _get_coverage_metrics(self) -> float:
        """Get current code coverage percentage."""
        try:
            # Try to read latest coverage report
            coverage_file = self.project_root / "test_reports" / "coverage" / "coverage_latest.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    data = json.load(f)
                    return data.get("total_coverage", 0.0)
        except Exception:
            pass
        
        return 0.0
    
    def _get_test_metrics(self) -> Dict[str, int]:
        """Get test execution metrics."""
        try:
            # Count test files
            test_files = list(self.project_root.glob("**/test_*.py"))
            total_tests = len(test_files)
            
            # Try to get failure count from latest failure report
            failure_file = self.project_root / "test_reports" / "failures" / "failure_analysis_latest.json"
            failures = 0
            if failure_file.exists():
                with open(failure_file, 'r') as f:
                    data = json.load(f)
                    failures = data.get("total_failures", 0)
            
            success_rate = ((total_tests - failures) / total_tests * 100) if total_tests > 0 else 0
            
            return {
                "total": total_tests,
                "failures": failures,
                "success_rate": success_rate
            }
        except Exception:
            return {"total": 0, "failures": 0, "success_rate": 0}
    
    def _get_performance_score(self) -> float:
        """Calculate performance score based on benchmarks."""
        try:
            # Try to read performance test results
            perf_file = self.project_root / "test_reports" / "performance" / "performance_latest.json"
            if perf_file.exists():
                with open(perf_file, 'r') as f:
                    data = json.load(f)
                    # Calculate score based on response times and throughput
                    return data.get("overall_score", 70.0)
        except Exception:
            pass
        
        return 70.0  # Default neutral score
    
    def _get_security_score(self) -> float:
        """Calculate security score based on security tests."""
        try:
            # Try to read security test results
            security_file = self.project_root / "test_reports" / "security" / "security_latest.json"
            if security_file.exists():
                with open(security_file, 'r') as f:
                    data = json.load(f)
                    return data.get("security_score", 85.0)
        except Exception:
            pass
        
        return 85.0  # Default good score
    
    def _get_code_complexity(self) -> float:
        """Calculate code complexity metrics."""
        try:
            # Use radon or similar tool to calculate complexity
            result = subprocess.run([
                "python", "-c", 
                "import radon.complexity as rc; print(rc.cc_visit('.'))"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse complexity result
                return float(result.stdout.strip()) if result.stdout.strip() else 5.0
        except Exception:
            pass
        
        return 5.0  # Default moderate complexity
    
    def _estimate_technical_debt(self) -> float:
        """Estimate technical debt in hours."""
        try:
            # Simple heuristic based on TODO comments, code smells, etc.
            todo_count = 0
            fixme_count = 0
            
            for py_file in self.project_root.glob("**/*.py"):
                if "test" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        todo_count += content.count("TODO")
                        fixme_count += content.count("FIXME")
                except Exception:
                    continue
            
            # Estimate: TODO = 0.5 hours, FIXME = 1 hour
            return todo_count * 0.5 + fixme_count * 1.0
        except Exception:
            return 0.0
    
    def _get_lines_of_code(self) -> Dict[str, int]:
        """Count lines of code."""
        try:
            source_lines = 0
            test_lines = 0
            
            for py_file in self.project_root.glob("**/*.py"):
                if "__pycache__" in str(py_file):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                        
                        if "test" in str(py_file):
                            test_lines += lines
                        else:
                            source_lines += lines
                except Exception:
                    continue
            
            return {"source": source_lines, "test": test_lines}
        except Exception:
            return {"source": 0, "test": 0}
    
    def save_metrics(self, metrics: QualityMetrics):
        """Save metrics to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quality_metrics (
                    timestamp, coverage_percentage, test_count, failure_count,
                    success_rate, performance_score, security_score, code_complexity,
                    technical_debt_hours, lines_of_code, test_lines_of_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp, metrics.coverage_percentage, metrics.test_count,
                metrics.failure_count, metrics.success_rate, metrics.performance_score,
                metrics.security_score, metrics.code_complexity, metrics.technical_debt_hours,
                metrics.lines_of_code, metrics.test_lines_of_code
            ))
            conn.commit()
    
    def get_historical_metrics(self, days: int = 30) -> List[QualityMetrics]:
        """Get historical metrics from database."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM quality_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_date,))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append(QualityMetrics(
                    timestamp=row[1],
                    coverage_percentage=row[2],
                    test_count=row[3],
                    failure_count=row[4],
                    success_rate=row[5],
                    performance_score=row[6],
                    security_score=row[7],
                    code_complexity=row[8],
                    technical_debt_hours=row[9],
                    lines_of_code=row[10],
                    test_lines_of_code=row[11]
                ))
            
            return metrics
    
    def analyze_trends(self, current: QualityMetrics, historical: List[QualityMetrics]) -> List[QualityTrend]:
        """Analyze quality trends."""
        trends = []
        
        if not historical:
            return trends
        
        previous = historical[0] if historical else current
        
        # Define metrics to analyze
        metrics_to_analyze = [
            ("coverage_percentage", "Coverage"),
            ("success_rate", "Success Rate"),
            ("performance_score", "Performance"),
            ("security_score", "Security"),
            ("code_complexity", "Complexity"),
            ("technical_debt_hours", "Technical Debt")
        ]
        
        for attr, name in metrics_to_analyze:
            current_value = getattr(current, attr)
            previous_value = getattr(previous, attr)
            
            if previous_value == 0:
                change_percentage = 0
            else:
                change_percentage = ((current_value - previous_value) / previous_value) * 100
            
            # Determine trend direction
            if abs(change_percentage) < 2:
                direction = "stable"
            elif change_percentage > 0:
                direction = "improving" if attr != "code_complexity" and attr != "technical_debt_hours" else "declining"
            else:
                direction = "declining" if attr != "code_complexity" and attr != "technical_debt_hours" else "improving"
            
            # Generate recommendation
            recommendation = self._get_trend_recommendation(attr, direction, change_percentage)
            
            trends.append(QualityTrend(
                metric_name=name,
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=change_percentage,
                trend_direction=direction,
                recommendation=recommendation
            ))
        
        return trends
    
    def _get_trend_recommendation(self, metric: str, direction: str, change: float) -> str:
        """Get recommendation based on trend."""
        if direction == "stable":
            return f"Maintain current {metric.replace('_', ' ')} levels"
        
        if metric == "coverage_percentage":
            if direction == "declining":
                return "Add more unit tests to improve coverage"
            else:
                return "Great progress on test coverage!"
        
        elif metric == "success_rate":
            if direction == "declining":
                return "Focus on fixing failing tests"
            else:
                return "Excellent test reliability improvement"
        
        elif metric == "performance_score":
            if direction == "declining":
                return "Optimize slow operations and API calls"
            else:
                return "Performance improvements are working well"
        
        elif metric == "technical_debt_hours":
            if direction == "declining":  # Actually good for debt
                return "Good progress on reducing technical debt"
            else:
                return "Address TODO items and code smells"
        
        return f"Monitor {metric.replace('_', ' ')} trends"
    
    def calculate_quality_score(self, metrics: QualityMetrics) -> float:
        """Calculate overall quality score."""
        weights = {
            "coverage": 0.25,
            "success_rate": 0.25,
            "performance": 0.20,
            "security": 0.20,
            "complexity": 0.10
        }
        
        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (metrics.code_complexity * 10))
        
        score = (
            metrics.coverage_percentage * weights["coverage"] +
            metrics.success_rate * weights["success_rate"] +
            metrics.performance_score * weights["performance"] +
            metrics.security_score * weights["security"] +
            complexity_score * weights["complexity"]
        )
        
        return min(100, max(0, score))
    
    def generate_report(self) -> QualityReport:
        """Generate comprehensive quality report."""
        print("📊 Generating quality report...")
        
        # Collect current metrics
        current_metrics = self.collect_current_metrics()
        
        # Save to database
        self.save_metrics(current_metrics)
        
        # Get historical data
        historical_data = self.get_historical_metrics()
        
        # Analyze trends
        trends = self.analyze_trends(current_metrics, historical_data)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(current_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(current_metrics, trends, quality_score)
        
        report = QualityReport(
            timestamp=datetime.now().isoformat(),
            current_metrics=current_metrics,
            trends=trends,
            quality_score=quality_score,
            recommendations=recommendations,
            historical_data=historical_data[:10]  # Last 10 data points
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_recommendations(self, metrics: QualityMetrics, trends: List[QualityTrend], score: float) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        # Overall score recommendations
        if score >= 90:
            recommendations.append("🏆 Excellent quality! Maintain current standards")
        elif score >= 80:
            recommendations.append("👍 Good quality. Focus on minor improvements")
        elif score >= 70:
            recommendations.append("⚠️ Acceptable quality. Several areas need attention")
        else:
            recommendations.append("🚨 Quality needs significant improvement")
        
        # Specific metric recommendations
        if metrics.coverage_percentage < 70:
            recommendations.append("📈 Priority: Increase test coverage to at least 70%")
        
        if metrics.success_rate < 90:
            recommendations.append("🔧 Fix failing tests to improve reliability")
        
        if metrics.technical_debt_hours > 10:
            recommendations.append("🧹 Address technical debt (TODO/FIXME items)")
        
        # Trend-based recommendations
        declining_trends = [t for t in trends if t.trend_direction == "declining" and abs(t.change_percentage) > 5]
        if declining_trends:
            recommendations.append(f"📉 Address declining trends: {', '.join([t.metric_name for t in declining_trends])}")
        
        return recommendations
    
    def _save_report(self, report: QualityReport):
        """Save quality report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = self.reports_dir / f"quality_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.reports_dir / "quality_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Generate HTML report
        self._generate_html_report(report, timestamp)
        
        print(f"📊 Quality report saved: {json_file}")
    
    def _generate_html_report(self, report: QualityReport, timestamp: str):
        """Generate HTML quality report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GopiAI Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #e8f5e8; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 2em; font-weight: bold; color: #28a745; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .trends {{ margin: 20px 0; }}
        .trend {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .improving {{ border-left: 4px solid #28a745; }}
        .declining {{ border-left: 4px solid #dc3545; }}
        .stable {{ border-left: 4px solid #6c757d; }}
        .recommendations {{ background: #d4edda; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GopiAI Quality Report</h1>
        <p>Generated: {report.timestamp}</p>
        <div class="score">Quality Score: {report.quality_score:.1f}/100</div>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Coverage</h3>
            <p>{report.current_metrics.coverage_percentage:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <p>{report.current_metrics.success_rate:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Performance</h3>
            <p>{report.current_metrics.performance_score:.1f}/100</p>
        </div>
        <div class="metric">
            <h3>Security</h3>
            <p>{report.current_metrics.security_score:.1f}/100</p>
        </div>
        <div class="metric">
            <h3>Tech Debt</h3>
            <p>{report.current_metrics.technical_debt_hours:.1f}h</p>
        </div>
        <div class="metric">
            <h3>Lines of Code</h3>
            <p>{report.current_metrics.lines_of_code:,}</p>
        </div>
    </div>
    
    <div class="trends">
        <h3>Quality Trends</h3>
        {''.join([f'''
        <div class="trend {trend.trend_direction}">
            <strong>{trend.metric_name}</strong>: {trend.current_value:.1f} 
            ({trend.change_percentage:+.1f}% change)
            <br><em>{trend.recommendation}</em>
        </div>
        ''' for trend in report.trends])}
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
        </ul>
    </div>
</body>
</html>
        """
        
        html_file = self.reports_dir / f"quality_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as latest
        latest_html = self.reports_dir / "quality_latest.html"
        with open(latest_html, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Generate quality report."""
    tracker = QualityTracker()
    report = tracker.generate_report()
    
    print(f"\n📊 Quality Report Summary:")
    print(f"Quality Score: {report.quality_score:.1f}/100")
    print(f"Coverage: {report.current_metrics.coverage_percentage:.1f}%")
    print(f"Success Rate: {report.current_metrics.success_rate:.1f}%")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()