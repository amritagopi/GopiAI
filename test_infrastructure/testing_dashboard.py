"""
Testing dashboard for GopiAI testing infrastructure.
Provides a web-based dashboard for visualizing test results and quality metrics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import sqlite3


class TestingDashboard:
    """Web-based dashboard for test results visualization."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "test_reports"
        self.dashboard_dir = self.reports_dir / "dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Dashboard port
        self.port = 8080
    
    def generate_dashboard(self):
        """Generate complete testing dashboard."""
        print("🎯 Generating testing dashboard...")
        
        # Collect all report data
        dashboard_data = self._collect_dashboard_data()
        
        # Generate HTML dashboard
        self._generate_html_dashboard(dashboard_data)
        
        # Generate supporting files
        self._generate_css_styles()
        self._generate_javascript()
        
        print(f"✅ Dashboard generated at: {self.dashboard_dir / 'index.html'}")
    
    def _collect_dashboard_data(self) -> Dict:
        """Collect data from all report sources."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "coverage": self._load_coverage_data(),
            "failures": self._load_failure_data(),
            "quality": self._load_quality_data(),
            "performance": self._load_performance_data(),
            "security": self._load_security_data(),
            "trends": self._load_trend_data()
        }
        
        return data
    
    def _load_coverage_data(self) -> Dict:
        """Load coverage report data."""
        try:
            coverage_file = self.reports_dir / "coverage" / "coverage_latest.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load coverage data: {e}")
        
        return {"total_coverage": 0, "modules": [], "summary": {}}
    
    def _load_failure_data(self) -> Dict:
        """Load failure analysis data."""
        try:
            failure_file = self.reports_dir / "failures" / "failure_analysis_latest.json"
            if failure_file.exists():
                with open(failure_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load failure data: {e}")
        
        return {"total_failures": 0, "failures_by_category": {}, "failures": []}
    
    def _load_quality_data(self) -> Dict:
        """Load quality metrics data."""
        try:
            quality_file = self.reports_dir / "quality" / "quality_latest.json"
            if quality_file.exists():
                with open(quality_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load quality data: {e}")
        
        return {"quality_score": 0, "current_metrics": {}, "trends": []}
    
    def _load_performance_data(self) -> Dict:
        """Load performance test data."""
        try:
            perf_file = self.reports_dir / "performance" / "performance_latest.json"
            if perf_file.exists():
                with open(perf_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load performance data: {e}")
        
        return {"overall_score": 0, "benchmarks": []}
    
    def _load_security_data(self) -> Dict:
        """Load security test data."""
        try:
            security_file = self.reports_dir / "security" / "security_latest.json"
            if security_file.exists():
                with open(security_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load security data: {e}")
        
        return {"security_score": 0, "vulnerabilities": []}
    
    def _load_trend_data(self) -> Dict:
        """Load historical trend data."""
        trends = {}
        
        # Load coverage trends
        try:
            coverage_trends = self.reports_dir / "coverage" / "coverage_trends.json"
            if coverage_trends.exists():
                with open(coverage_trends, 'r') as f:
                    trends["coverage"] = json.load(f)
        except Exception:
            trends["coverage"] = {}
        
        # Load failure trends
        try:
            failure_trends = self.reports_dir / "failures" / "failure_trends.json"
            if failure_trends.exists():
                with open(failure_trends, 'r') as f:
                    trends["failures"] = json.load(f)
        except Exception:
            trends["failures"] = {}
        
        # Load quality trends from database
        try:
            quality_db = self.reports_dir / "quality" / "quality_metrics.db"
            if quality_db.exists():
                trends["quality"] = self._load_quality_trends_from_db(quality_db)
        except Exception:
            trends["quality"] = {}
        
        return trends
    
    def _load_quality_trends_from_db(self, db_path: Path) -> Dict:
        """Load quality trends from SQLite database."""
        trends = {}
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT DATE(timestamp) as date, 
                           AVG(coverage_percentage) as coverage,
                           AVG(success_rate) as success_rate,
                           AVG(performance_score) as performance
                    FROM quality_metrics 
                    WHERE timestamp > datetime('now', '-30 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """)
                
                for row in cursor.fetchall():
                    date, coverage, success_rate, performance = row
                    trends[date] = {
                        "coverage": coverage,
                        "success_rate": success_rate,
                        "performance": performance
                    }
        except Exception as e:
            print(f"⚠️ Failed to load quality trends: {e}")
        
        return trends
    
    def _generate_html_dashboard(self, data: Dict):
        """Generate main HTML dashboard."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GopiAI Testing Dashboard</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <header class="dashboard-header">
            <h1>🧪 GopiAI Testing Dashboard</h1>
            <p class="timestamp">Last Updated: {data['timestamp']}</p>
        </header>
        
        <div class="dashboard-grid">
            <!-- Overview Cards -->
            <div class="card overview-card">
                <h2>📊 Overview</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value">{data['coverage'].get('total_coverage', 0):.1f}%</div>
                        <div class="metric-label">Coverage</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data['quality'].get('quality_score', 0):.0f}</div>
                        <div class="metric-label">Quality Score</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data['failures'].get('total_failures', 0)}</div>
                        <div class="metric-label">Failures</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data['performance'].get('overall_score', 0):.0f}</div>
                        <div class="metric-label">Performance</div>
                    </div>
                </div>
            </div>
            
            <!-- Coverage Chart -->
            <div class="card chart-card">
                <h2>📈 Coverage Trends</h2>
                <canvas id="coverageChart"></canvas>
            </div>
            
            <!-- Failure Analysis -->
            <div class="card">
                <h2>🚨 Failure Analysis</h2>
                <div class="failure-categories">
                    {self._generate_failure_categories_html(data['failures'])}
                </div>
            </div>
            
            <!-- Quality Metrics -->
            <div class="card">
                <h2>⭐ Quality Metrics</h2>
                <div class="quality-metrics">
                    {self._generate_quality_metrics_html(data['quality'])}
                </div>
            </div>
            
            <!-- Module Coverage -->
            <div class="card">
                <h2>📦 Module Coverage</h2>
                <div class="module-list">
                    {self._generate_module_coverage_html(data['coverage'])}
                </div>
            </div>
            
            <!-- Recent Failures -->
            <div class="card">
                <h2>🔍 Recent Failures</h2>
                <div class="failure-list">
                    {self._generate_recent_failures_html(data['failures'])}
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h2>⚡ Performance</h2>
                <canvas id="performanceChart"></canvas>
            </div>
            
            <!-- Security Status -->
            <div class="card">
                <h2>🔒 Security</h2>
                <div class="security-status">
                    {self._generate_security_status_html(data['security'])}
                </div>
            </div>
        </div>
    </div>
    
    <script src="dashboard.js"></script>
    <script>
        // Initialize dashboard with data
        const dashboardData = {json.dumps(data, indent=2)};
        initializeDashboard(dashboardData);
    </script>
</body>
</html>
        """
        
        dashboard_file = self.dashboard_dir / "index.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_failure_categories_html(self, failure_data: Dict) -> str:
        """Generate HTML for failure categories."""
        categories = failure_data.get('failures_by_category', {})
        if not categories:
            return "<p>No failures detected! 🎉</p>"
        
        html = ""
        for category, count in categories.items():
            html += f"""
            <div class="failure-category">
                <span class="category-name">{category.replace('_', ' ').title()}</span>
                <span class="category-count">{count}</span>
            </div>
            """
        
        return html
    
    def _generate_quality_metrics_html(self, quality_data: Dict) -> str:
        """Generate HTML for quality metrics."""
        metrics = quality_data.get('current_metrics', {})
        if not metrics:
            return "<p>No quality data available</p>"
        
        html = f"""
        <div class="quality-grid">
            <div class="quality-item">
                <span class="quality-label">Test Count</span>
                <span class="quality-value">{metrics.get('test_count', 0)}</span>
            </div>
            <div class="quality-item">
                <span class="quality-label">Success Rate</span>
                <span class="quality-value">{metrics.get('success_rate', 0):.1f}%</span>
            </div>
            <div class="quality-item">
                <span class="quality-label">Tech Debt</span>
                <span class="quality-value">{metrics.get('technical_debt_hours', 0):.1f}h</span>
            </div>
            <div class="quality-item">
                <span class="quality-label">Lines of Code</span>
                <span class="quality-value">{metrics.get('lines_of_code', 0):,}</span>
            </div>
        </div>
        """
        
        return html
    
    def _generate_module_coverage_html(self, coverage_data: Dict) -> str:
        """Generate HTML for module coverage."""
        modules = coverage_data.get('modules', [])
        if not modules:
            return "<p>No module data available</p>"
        
        # Sort modules by coverage percentage
        sorted_modules = sorted(modules, key=lambda x: x.get('coverage_percent', 0), reverse=True)
        
        html = ""
        for module in sorted_modules[:10]:  # Show top 10
            coverage = module.get('coverage_percent', 0)
            css_class = self._get_coverage_css_class(coverage)
            
            html += f"""
            <div class="module-item {css_class}">
                <span class="module-name">{module.get('name', 'Unknown')}</span>
                <span class="module-coverage">{coverage:.1f}%</span>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: {coverage}%"></div>
                </div>
            </div>
            """
        
        return html
    
    def _generate_recent_failures_html(self, failure_data: Dict) -> str:
        """Generate HTML for recent failures."""
        failures = failure_data.get('failures', [])
        if not failures:
            return "<p>No recent failures! 🎉</p>"
        
        html = ""
        for failure in failures[:5]:  # Show last 5 failures
            priority_class = f"priority-{failure.get('priority', 4)}"
            
            html += f"""
            <div class="failure-item {priority_class}">
                <div class="failure-header">
                    <span class="failure-test">{failure.get('test_name', 'Unknown')}</span>
                    <span class="failure-category">{failure.get('category', 'unknown').replace('_', ' ')}</span>
                </div>
                <div class="failure-message">{failure.get('error_message', '')[:100]}...</div>
                <div class="failure-recommendation">{failure.get('recommendation', '')}</div>
            </div>
            """
        
        return html
    
    def _generate_security_status_html(self, security_data: Dict) -> str:
        """Generate HTML for security status."""
        score = security_data.get('security_score', 0)
        vulnerabilities = security_data.get('vulnerabilities', [])
        
        status_class = "excellent" if score >= 90 else "good" if score >= 80 else "warning"
        
        html = f"""
        <div class="security-score {status_class}">
            <div class="score-value">{score:.0f}/100</div>
            <div class="score-label">Security Score</div>
        </div>
        <div class="vulnerability-count">
            <span>{len(vulnerabilities)} vulnerabilities found</span>
        </div>
        """
        
        return html
    
    def _get_coverage_css_class(self, coverage: float) -> str:
        """Get CSS class based on coverage percentage."""
        if coverage >= 90:
            return "excellent"
        elif coverage >= 80:
            return "good"
        elif coverage >= 70:
            return "acceptable"
        else:
            return "poor"
    
    def _generate_css_styles(self):
        """Generate CSS styles for dashboard."""
        css_content = """
/* Dashboard Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f7fa;
    color: #333;
    line-height: 1.6;
}

.dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.dashboard-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.dashboard-header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.timestamp {
    color: #7f8c8d;
    font-size: 0.9em;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-2px);
}

.card h2 {
    margin-bottom: 15px;
    color: #2c3e50;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 10px;
}

.overview-card {
    grid-column: 1 / -1;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
}

.metric {
    text-align: center;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.metric-value {
    font-size: 2em;
    font-weight: bold;
    color: #27ae60;
}

.metric-label {
    color: #7f8c8d;
    font-size: 0.9em;
    margin-top: 5px;
}

.chart-card {
    min-height: 300px;
}

.failure-categories {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.failure-category {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
    border-left: 4px solid #e74c3c;
}

.category-count {
    background: #e74c3c;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}

.quality-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.quality-item {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
}

.quality-value {
    font-weight: bold;
    color: #2980b9;
}

.module-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.module-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
}

.module-name {
    flex: 1;
    font-weight: 500;
}

.module-coverage {
    font-weight: bold;
    min-width: 50px;
    text-align: right;
}

.coverage-bar {
    width: 100px;
    height: 8px;
    background: #ecf0f1;
    border-radius: 4px;
    overflow: hidden;
}

.coverage-fill {
    height: 100%;
    background: #27ae60;
    transition: width 0.3s;
}

.excellent .coverage-fill { background: #27ae60; }
.good .coverage-fill { background: #f39c12; }
.acceptable .coverage-fill { background: #e67e22; }
.poor .coverage-fill { background: #e74c3c; }

.failure-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.failure-item {
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
    border-left: 4px solid #e74c3c;
}

.failure-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}

.failure-test {
    font-weight: bold;
}

.failure-category {
    background: #e74c3c;
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 0.7em;
}

.failure-message {
    color: #7f8c8d;
    font-size: 0.9em;
    margin-bottom: 5px;
}

.failure-recommendation {
    color: #2980b9;
    font-size: 0.8em;
    font-style: italic;
}

.security-score {
    text-align: center;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.security-score.excellent { background: #d5f4e6; }
.security-score.good { background: #fef9e7; }
.security-score.warning { background: #fadbd8; }

.score-value {
    font-size: 2.5em;
    font-weight: bold;
}

.score-label {
    color: #7f8c8d;
    margin-top: 5px;
}

.vulnerability-count {
    text-align: center;
    color: #7f8c8d;
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .quality-grid {
        grid-template-columns: 1fr;
    }
}
        """
        
        css_file = self.dashboard_dir / "styles.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_javascript(self):
        """Generate JavaScript for dashboard interactivity."""
        js_content = """
// Dashboard JavaScript
function initializeDashboard(data) {
    console.log('Initializing dashboard with data:', data);
    
    // Initialize charts
    initializeCoverageChart(data.trends.coverage || {});
    initializePerformanceChart(data.trends.quality || {});
    
    // Auto-refresh every 5 minutes
    setInterval(() => {
        location.reload();
    }, 5 * 60 * 1000);
}

function initializeCoverageChart(coverageData) {
    const ctx = document.getElementById('coverageChart');
    if (!ctx) return;
    
    const dates = Object.keys(coverageData).sort();
    const values = dates.map(date => coverageData[date]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Coverage %',
                data: values,
                borderColor: '#27ae60',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initializePerformanceChart(qualityData) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    const dates = Object.keys(qualityData).sort();
    const performanceData = dates.map(date => qualityData[date]?.performance || 0);
    const successRateData = dates.map(date => qualityData[date]?.success_rate || 0);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Performance Score',
                    data: performanceData,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Success Rate %',
                    data: successRateData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard DOM loaded');
});
        """
        
        js_file = self.dashboard_dir / "dashboard.js"
        with open(js_file, 'w') as f:
            f.write(js_content)
    
    def serve_dashboard(self, open_browser: bool = True):
        """Serve dashboard on local HTTP server."""
        os.chdir(self.dashboard_dir)
        
        class DashboardHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress server logs
        
        server = HTTPServer(('localhost', self.port), DashboardHandler)
        
        if open_browser:
            url = f"http://localhost:{self.port}"
            print(f"🌐 Opening dashboard at: {url}")
            webbrowser.open(url)
        
        print(f"🚀 Dashboard server running on port {self.port}")
        print("Press Ctrl+C to stop the server")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard server stopped")
            server.shutdown()
    
    def start_dashboard_server(self):
        """Start dashboard server in background thread."""
        def run_server():
            self.serve_dashboard(open_browser=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return f"http://localhost:{self.port}"


def main():
    """Generate and serve testing dashboard."""
    dashboard = TestingDashboard()
    
    # Generate dashboard
    dashboard.generate_dashboard()
    
    # Serve dashboard
    dashboard.serve_dashboard()


if __name__ == "__main__":
    main()