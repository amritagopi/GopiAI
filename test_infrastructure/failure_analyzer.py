"""
Test failure analysis system for GopiAI testing infrastructure.
Analyzes test failures and provides actionable recommendations for fixes.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import xml.etree.ElementTree as ET


class FailureCategory(Enum):
    """Categories of test failures."""
    ASSERTION_ERROR = "assertion_error"
    IMPORT_ERROR = "import_error"
    TIMEOUT_ERROR = "timeout_error"
    CONNECTION_ERROR = "connection_error"
    ENVIRONMENT_ERROR = "environment_error"
    DEPENDENCY_ERROR = "dependency_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class FailurePattern:
    """Pattern for identifying failure types."""
    category: FailureCategory
    pattern: str
    description: str
    recommendation: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low


@dataclass
class TestFailure:
    """Individual test failure information."""
    test_name: str
    module: str
    category: FailureCategory
    error_message: str
    stack_trace: str
    file_path: str
    line_number: int
    recommendation: str
    priority: int
    timestamp: str


@dataclass
class FailureAnalysisReport:
    """Complete failure analysis report."""
    timestamp: str
    total_failures: int
    failures_by_category: Dict[str, int]
    failures: List[TestFailure]
    recommendations: List[str]
    trend_data: Optional[Dict[str, int]] = None


class FailureAnalyzer:
    """Analyzes test failures and provides recommendations."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test_reports" / "failures"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Define failure patterns
        self.failure_patterns = [
            FailurePattern(
                FailureCategory.IMPORT_ERROR,
                r"ModuleNotFoundError|ImportError",
                "Missing module or import error",
                "Install missing dependencies or check module paths",
                1
            ),
            FailurePattern(
                FailureCategory.CONNECTION_ERROR,
                r"ConnectionError|ConnectTimeout|HTTPError|requests\.exceptions",
                "Network or service connection failure",
                "Check service availability and network connectivity",
                2
            ),
            FailurePattern(
                FailureCategory.TIMEOUT_ERROR,
                r"TimeoutError|timeout|Timeout",
                "Operation timed out",
                "Increase timeout values or optimize slow operations",
                2
            ),
            FailurePattern(
                FailureCategory.ASSERTION_ERROR,
                r"AssertionError|assert",
                "Test assertion failed",
                "Review test expectations and actual behavior",
                3
            ),
            FailurePattern(
                FailureCategory.ENVIRONMENT_ERROR,
                r"EnvironmentError|FileNotFoundError|PermissionError",
                "Environment or file system error",
                "Check file permissions and environment setup",
                2
            ),
            FailurePattern(
                FailureCategory.DEPENDENCY_ERROR,
                r"AttributeError.*has no attribute|TypeError.*missing.*argument",
                "API or dependency version mismatch",
                "Update dependencies or check API compatibility",
                2
            ),
            FailurePattern(
                FailureCategory.CONFIGURATION_ERROR,
                r"KeyError.*API_KEY|ValueError.*configuration|ConfigurationError",
                "Configuration or API key error",
                "Check .env files and configuration settings",
                1
            )
        ]
    
    def analyze_failures(self, test_results_path: str = None) -> FailureAnalysisReport:
        """Analyze test failures from pytest results."""
        print("🔍 Analyzing test failures...")
        
        # Parse test results
        failures = self._parse_test_results(test_results_path)
        
        # Categorize failures
        categorized_failures = self._categorize_failures(failures)
        
        # Generate summary statistics
        failures_by_category = self._count_failures_by_category(categorized_failures)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categorized_failures, failures_by_category)
        
        # Load trend data
        trend_data = self._load_trend_data()
        
        report = FailureAnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_failures=len(categorized_failures),
            failures_by_category=failures_by_category,
            failures=categorized_failures,
            recommendations=recommendations,
            trend_data=trend_data
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _parse_test_results(self, results_path: str = None) -> List[Dict]:
        """Parse test results from various sources."""
        failures = []
        
        # Try to find pytest XML results
        xml_files = list(self.project_root.glob("**/test_results_*.xml"))
        if results_path:
            xml_files = [Path(results_path)]
        
        for xml_file in xml_files:
            if xml_file.exists():
                failures.extend(self._parse_junit_xml(xml_file))
        
        # Also check for pytest cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            failures.extend(self._parse_pytest_cache())
        
        return failures
    
    def _parse_junit_xml(self, xml_file: Path) -> List[Dict]:
        """Parse JUnit XML test results."""
        failures = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for testcase in root.findall(".//testcase"):
                failure = testcase.find("failure")
                error = testcase.find("error")
                
                if failure is not None or error is not None:
                    element = failure if failure is not None else error
                    
                    failures.append({
                        "test_name": testcase.get("name", "unknown"),
                        "module": testcase.get("classname", "unknown"),
                        "error_message": element.get("message", ""),
                        "stack_trace": element.text or "",
                        "file_path": testcase.get("file", ""),
                        "line_number": 0
                    })
        
        except Exception as e:
            print(f"⚠️ Failed to parse XML results: {e}")
        
        return failures
    
    def _parse_pytest_cache(self) -> List[Dict]:
        """Parse pytest cache for failure information."""
        failures = []
        
        try:
            cache_dir = self.project_root / ".pytest_cache" / "v" / "cache"
            if cache_dir.exists():
                for cache_file in cache_dir.glob("lastfailed"):
                    with open(cache_file, 'r') as f:
                        failed_tests = json.load(f)
                        
                    for test_path, _ in failed_tests.items():
                        failures.append({
                            "test_name": test_path.split("::")[-1] if "::" in test_path else test_path,
                            "module": test_path.split("::")[0] if "::" in test_path else "unknown",
                            "error_message": "Test failed (from cache)",
                            "stack_trace": "",
                            "file_path": test_path.split("::")[0] if "::" in test_path else "",
                            "line_number": 0
                        })
        
        except Exception as e:
            print(f"⚠️ Failed to parse pytest cache: {e}")
        
        return failures
    
    def _categorize_failures(self, failures: List[Dict]) -> List[TestFailure]:
        """Categorize failures using pattern matching."""
        categorized = []
        
        for failure in failures:
            category, recommendation, priority = self._classify_failure(
                failure["error_message"], 
                failure["stack_trace"]
            )
            
            # Extract line number from stack trace
            line_number = self._extract_line_number(failure["stack_trace"])
            
            test_failure = TestFailure(
                test_name=failure["test_name"],
                module=failure["module"],
                category=category,
                error_message=failure["error_message"],
                stack_trace=failure["stack_trace"],
                file_path=failure["file_path"],
                line_number=line_number,
                recommendation=recommendation,
                priority=priority,
                timestamp=datetime.now().isoformat()
            )
            
            categorized.append(test_failure)
        
        return categorized
    
    def _classify_failure(self, error_message: str, stack_trace: str) -> Tuple[FailureCategory, str, int]:
        """Classify failure using pattern matching."""
        full_text = f"{error_message} {stack_trace}"
        
        for pattern in self.failure_patterns:
            if re.search(pattern.pattern, full_text, re.IGNORECASE):
                return pattern.category, pattern.recommendation, pattern.priority
        
        return FailureCategory.UNKNOWN_ERROR, "Review error details and stack trace", 4
    
    def _extract_line_number(self, stack_trace: str) -> int:
        """Extract line number from stack trace."""
        line_match = re.search(r'line (\d+)', stack_trace)
        return int(line_match.group(1)) if line_match else 0
    
    def _count_failures_by_category(self, failures: List[TestFailure]) -> Dict[str, int]:
        """Count failures by category."""
        counts = {}
        for failure in failures:
            category = failure.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _generate_recommendations(self, failures: List[TestFailure], counts: Dict[str, int]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if not failures:
            recommendations.append("✅ No test failures detected!")
            return recommendations
        
        # Priority-based recommendations
        critical_failures = [f for f in failures if f.priority == 1]
        if critical_failures:
            recommendations.append(
                f"🚨 CRITICAL: {len(critical_failures)} critical failures need immediate attention"
            )
        
        # Category-specific recommendations
        if counts.get("import_error", 0) > 0:
            recommendations.append(
                f"📦 Import Errors ({counts['import_error']}): Run 'pip install -r requirements.txt' in all environments"
            )
        
        if counts.get("connection_error", 0) > 0:
            recommendations.append(
                f"🌐 Connection Errors ({counts['connection_error']}): Check if CrewAI server is running on port 5051"
            )
        
        if counts.get("configuration_error", 0) > 0:
            recommendations.append(
                f"⚙️ Configuration Errors ({counts['configuration_error']}): Verify .env files and API keys"
            )
        
        if counts.get("timeout_error", 0) > 0:
            recommendations.append(
                f"⏱️ Timeout Errors ({counts['timeout_error']}): Consider increasing timeout values or optimizing slow operations"
            )
        
        # Module-specific recommendations
        module_failures = {}
        for failure in failures:
            module = failure.module
            module_failures[module] = module_failures.get(module, 0) + 1
        
        if module_failures:
            worst_module = max(module_failures.items(), key=lambda x: x[1])
            if worst_module[1] > 1:
                recommendations.append(
                    f"🎯 Focus on module '{worst_module[0]}' with {worst_module[1]} failures"
                )
        
        return recommendations
    
    def _load_trend_data(self) -> Optional[Dict[str, int]]:
        """Load historical failure trend data."""
        trend_file = self.reports_dir / "failure_trends.json"
        
        if trend_file.exists():
            try:
                with open(trend_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def _save_report(self, report: FailureAnalysisReport):
        """Save failure analysis report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report
        json_file = self.reports_dir / f"failure_analysis_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save latest report
        latest_file = self.reports_dir / "failure_analysis_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Update trend data
        self._update_trend_data(report.total_failures)
        
        # Generate HTML report
        self._generate_html_report(report, timestamp)
        
        print(f"📊 Failure analysis saved: {json_file}")
    
    def _update_trend_data(self, current_failures: int):
        """Update failure trend data."""
        trend_file = self.reports_dir / "failure_trends.json"
        
        trends = {}
        if trend_file.exists():
            try:
                with open(trend_file, 'r') as f:
                    trends = json.load(f)
            except Exception:
                pass
        
        # Add current data point
        date_key = datetime.now().strftime("%Y-%m-%d")
        trends[date_key] = current_failures
        
        # Keep only last 30 days
        sorted_dates = sorted(trends.keys())
        if len(sorted_dates) > 30:
            for old_date in sorted_dates[:-30]:
                del trends[old_date]
        
        with open(trend_file, 'w') as f:
            json.dump(trends, f, indent=2)
    
    def _generate_html_report(self, report: FailureAnalysisReport, timestamp: str):
        """Generate HTML failure analysis report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GopiAI Failure Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f8d7da; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }}
        .failures {{ margin: 20px 0; }}
        .failure {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; border-left: 4px solid #dc3545; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; }}
        .critical {{ border-left-color: #dc3545; }}
        .high {{ border-left-color: #fd7e14; }}
        .medium {{ border-left-color: #ffc107; }}
        .low {{ border-left-color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GopiAI Test Failure Analysis</h1>
        <p>Generated: {report.timestamp}</p>
        <p>Total Failures: <strong>{report.total_failures}</strong></p>
    </div>
    
    <div class="summary">
        {''.join([f'''
        <div class="metric">
            <h3>{category.replace('_', ' ').title()}</h3>
            <p>{count} failures</p>
        </div>
        ''' for category, count in report.failures_by_category.items()])}
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in report.recommendations])}
        </ul>
    </div>
    
    <div class="failures">
        <h3>Detailed Failures</h3>
        {''.join([f'''
        <div class="failure priority-{failure.priority}">
            <h4>{failure.test_name}</h4>
            <p><strong>Module:</strong> {failure.module}</p>
            <p><strong>Category:</strong> {failure.category.value}</p>
            <p><strong>Error:</strong> {failure.error_message}</p>
            <p><strong>Recommendation:</strong> {failure.recommendation}</p>
        </div>
        ''' for failure in report.failures])}
    </div>
</body>
</html>
        """
        
        html_file = self.reports_dir / f"failure_analysis_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as latest
        latest_html = self.reports_dir / "failure_analysis_latest.html"
        with open(latest_html, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Analyze test failures."""
    analyzer = FailureAnalyzer()
    report = analyzer.analyze_failures()
    
    print(f"\n📊 Failure Analysis Summary:")
    print(f"Total Failures: {report.total_failures}")
    print(f"Categories: {len(report.failures_by_category)}")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()