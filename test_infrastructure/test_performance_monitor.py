#!/usr/bin/env python3
"""
Test Performance Monitoring System

This module provides comprehensive monitoring of test performance itself,
tracking execution times, resource usage, and identifying performance bottlenecks
in the testing system.
"""
import json
import time
import threading
import statistics
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import psutil
from contextlib import contextmanager


@dataclass
class TestExecutionMetrics:
    """Metrics for a single test execution."""
    test_id: str
    test_name: str
    category: str
    module: str
    start_time: float
    end_time: float
    duration_seconds: float
    memory_peak_mb: float
    memory_avg_mb: float
    cpu_peak_percent: float
    cpu_avg_percent: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    exit_code: int
    success: bool
    retry_count: int
    parallel_worker_id: Optional[int] = None
    dependencies_wait_time: float = 0.0
    setup_time: float = 0.0
    teardown_time: float = 0.0


@dataclass
class TestSuiteMetrics:
    """Metrics for an entire test suite execution."""
    suite_id: str
    suite_name: str
    start_time: float
    end_time: float
    total_duration_seconds: float
    test_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    parallel_workers: int
    parallel_efficiency: float
    resource_utilization: Dict[str, float]
    bottlenecks: List[str]
    performance_score: float


class TestPerformanceMonitor:
    """Monitors test performance and resource usage."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # Create monitoring directory
        self.monitoring_dir = self.project_root / "test_reports" / "performance_monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.monitoring_dir / "test_performance.db"
        self._init_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.current_suite_id = None
        self.test_metrics: List[TestExecutionMetrics] = []
        self.resource_monitor = None
        
        # Performance thresholds
        self.thresholds = {
            'slow_test_seconds': 30.0,
            'memory_heavy_mb': 500.0,
            'cpu_intensive_percent': 80.0,
            'parallel_efficiency_min': 0.6
        }
    
    def _init_database(self):
        """Initialize SQLite database for performance metrics."""
        with sqlite3.connect(self.db_path) as conn:
            # Test execution metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    category TEXT,
                    module TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration_seconds REAL,
                    memory_peak_mb REAL,
                    memory_avg_mb REAL,
                    cpu_peak_percent REAL,
                    cpu_avg_percent REAL,
                    disk_read_mb REAL,
                    disk_write_mb REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    exit_code INTEGER,
                    success BOOLEAN,
                    retry_count INTEGER,
                    parallel_worker_id INTEGER,
                    dependencies_wait_time REAL,
                    setup_time REAL,
                    teardown_time REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Test suite metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_suites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suite_id TEXT NOT NULL,
                    suite_name TEXT NOT NULL,
                    start_time REAL,
                    end_time REAL,
                    total_duration_seconds REAL,
                    test_count INTEGER,
                    passed_count INTEGER,
                    failed_count INTEGER,
                    skipped_count INTEGER,
                    parallel_workers INTEGER,
                    parallel_efficiency REAL,
                    resource_utilization TEXT,
                    bottlenecks TEXT,
                    performance_score REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def monitor_test_suite(self, suite_name: str, parallel_workers: int = 1):
        """Context manager for monitoring an entire test suite."""
        suite_id = f"{suite_name}_{int(time.time())}"
        self.current_suite_id = suite_id
        self.monitoring_active = True
        self.test_metrics.clear()
        
        # Start resource monitoring
        self.resource_monitor = SystemResourceMonitor()
        self.resource_monitor.start_monitoring(interval=0.5)
        
        suite_start = time.time()
        
        self.logger.info(f"📊 Started monitoring test suite: {suite_name}")
        
        try:
            yield self
        finally:
            suite_end = time.time()
            
            # Stop resource monitoring
            resource_data = []
            if self.resource_monitor:
                resource_data = self.resource_monitor.stop_monitoring()
            
            # Create suite metrics
            suite_metrics = self._create_suite_metrics(
                suite_id, suite_name, suite_start, suite_end, 
                parallel_workers, resource_data
            )
            
            # Save metrics
            self._save_suite_metrics(suite_metrics)
            
            # Generate performance report
            self._generate_performance_report(suite_metrics)
            
            self.monitoring_active = False
            self.logger.info(f"📊 Completed monitoring test suite: {suite_name}")
    
    @contextmanager
    def monitor_test(self, test_name: str, category: str = "unknown", 
                    module: str = "unknown", worker_id: Optional[int] = None):
        """Context manager for monitoring a single test."""
        if not self.monitoring_active:
            yield
            return
        
        test_id = f"{test_name}_{int(time.time() * 1000)}"
        
        # Initialize metrics
        metrics = TestExecutionMetrics(
            test_id=test_id,
            test_name=test_name,
            category=category,
            module=module,
            start_time=time.time(),
            end_time=0.0,
            duration_seconds=0.0,
            memory_peak_mb=0.0,
            memory_avg_mb=0.0,
            cpu_peak_percent=0.0,
            cpu_avg_percent=0.0,
            disk_read_mb=0.0,
            disk_write_mb=0.0,
            network_sent_mb=0.0,
            network_recv_mb=0.0,
            exit_code=0,
            success=True,
            retry_count=0,
            parallel_worker_id=worker_id
        )
        
        # Start individual test monitoring
        test_monitor = IndividualTestMonitor()
        test_monitor.start_monitoring()
        
        try:
            yield metrics
            metrics.success = True
            metrics.exit_code = 0
        except Exception as e:
            metrics.success = False
            metrics.exit_code = 1
            self.logger.warning(f"Test {test_name} failed: {e}")
        finally:
            metrics.end_time = time.time()
            metrics.duration_seconds = metrics.end_time - metrics.start_time
            
            # Get resource usage from monitor
            resource_stats = test_monitor.stop_monitoring()
            if resource_stats:
                metrics.memory_peak_mb = resource_stats['memory_peak_mb']
                metrics.memory_avg_mb = resource_stats['memory_avg_mb']
                metrics.cpu_peak_percent = resource_stats['cpu_peak_percent']
                metrics.cpu_avg_percent = resource_stats['cpu_avg_percent']
                metrics.disk_read_mb = resource_stats['disk_read_mb']
                metrics.disk_write_mb = resource_stats['disk_write_mb']
                metrics.network_sent_mb = resource_stats['network_sent_mb']
                metrics.network_recv_mb = resource_stats['network_recv_mb']
            
            # Add to test metrics
            self.test_metrics.append(metrics)
            
            # Save individual test metrics
            self._save_test_metrics(metrics)
    
    def _create_suite_metrics(self, suite_id: str, suite_name: str, 
                            start_time: float, end_time: float,
                            parallel_workers: int, resource_data: List[Dict]) -> TestSuiteMetrics:
        """Create test suite metrics from collected data."""
        total_duration = end_time - start_time
        
        # Count test results
        passed_count = len([m for m in self.test_metrics if m.success])
        failed_count = len([m for m in self.test_metrics if not m.success])
        test_count = len(self.test_metrics)
        
        # Calculate parallel efficiency
        if test_count > 0 and parallel_workers > 1:
            total_test_time = sum(m.duration_seconds for m in self.test_metrics)
            theoretical_parallel_time = total_test_time / parallel_workers
            parallel_efficiency = min(1.0, theoretical_parallel_time / total_duration)
        else:
            parallel_efficiency = 1.0
        
        # Calculate resource utilization
        resource_utilization = {}
        if resource_data:
            resource_utilization = {
                'avg_cpu_percent': statistics.mean(d.get('cpu_percent', 0) for d in resource_data),
                'peak_cpu_percent': max(d.get('cpu_percent', 0) for d in resource_data),
                'avg_memory_mb': statistics.mean(d.get('memory_mb', 0) for d in resource_data),
                'peak_memory_mb': max(d.get('memory_mb', 0) for d in resource_data)
            }
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks()
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(
            total_duration, test_count, passed_count, parallel_efficiency, resource_utilization
        )
        
        return TestSuiteMetrics(
            suite_id=suite_id,
            suite_name=suite_name,
            start_time=start_time,
            end_time=end_time,
            total_duration_seconds=total_duration,
            test_count=test_count,
            passed_count=passed_count,
            failed_count=failed_count,
            skipped_count=0,  # TODO: Track skipped tests
            parallel_workers=parallel_workers,
            parallel_efficiency=parallel_efficiency,
            resource_utilization=resource_utilization,
            bottlenecks=bottlenecks,
            performance_score=performance_score
        )
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks in test execution."""
        bottlenecks = []
        
        if not self.test_metrics:
            return bottlenecks
        
        # Identify slow tests
        avg_duration = statistics.mean(m.duration_seconds for m in self.test_metrics)
        slow_tests = [m for m in self.test_metrics if m.duration_seconds > avg_duration * 2]
        
        if slow_tests:
            slowest = max(slow_tests, key=lambda m: m.duration_seconds)
            bottlenecks.append(f"Slow test: {slowest.test_name} ({slowest.duration_seconds:.2f}s)")
        
        # Identify memory-heavy tests
        memory_heavy = [m for m in self.test_metrics if m.memory_peak_mb > self.thresholds['memory_heavy_mb']]
        if memory_heavy:
            heaviest = max(memory_heavy, key=lambda m: m.memory_peak_mb)
            bottlenecks.append(f"Memory-heavy test: {heaviest.test_name} ({heaviest.memory_peak_mb:.1f}MB)")
        
        # Identify CPU-intensive tests
        cpu_intensive = [m for m in self.test_metrics if m.cpu_peak_percent > self.thresholds['cpu_intensive_percent']]
        if cpu_intensive:
            most_intensive = max(cpu_intensive, key=lambda m: m.cpu_peak_percent)
            bottlenecks.append(f"CPU-intensive test: {most_intensive.test_name} ({most_intensive.cpu_peak_percent:.1f}%)")
        
        # Check for dependency wait times
        high_wait_times = [m for m in self.test_metrics if m.dependencies_wait_time > 5.0]
        if high_wait_times:
            bottlenecks.append(f"High dependency wait times: {len(high_wait_times)} tests")
        
        return bottlenecks
    
    def _calculate_performance_score(self, total_duration: float, test_count: int, 
                                   passed_count: int, parallel_efficiency: float,
                                   resource_utilization: Dict) -> float:
        """Calculate overall performance score for the test suite."""
        if test_count == 0:
            return 0.0
        
        # Success rate component (40%)
        success_rate = passed_count / test_count
        success_score = success_rate * 40
        
        # Speed component (30%)
        avg_test_time = total_duration / test_count if test_count > 0 else 0
        speed_score = max(0, 30 - (avg_test_time / 10) * 5)  # Penalize slow tests
        
        # Parallel efficiency component (20%)
        efficiency_score = parallel_efficiency * 20
        
        # Resource efficiency component (10%)
        resource_score = 10
        if resource_utilization:
            cpu_usage = resource_utilization.get('avg_cpu_percent', 0)
            memory_usage = resource_utilization.get('avg_memory_mb', 0)
            
            # Penalize very high or very low resource usage
            if cpu_usage > 90 or cpu_usage < 10:
                resource_score -= 3
            if memory_usage > 2000:  # 2GB
                resource_score -= 3
        
        total_score = success_score + speed_score + efficiency_score + resource_score
        return min(100.0, max(0.0, total_score))
    
    def _save_test_metrics(self, metrics: TestExecutionMetrics):
        """Save individual test metrics to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO test_executions (
                    test_id, test_name, category, module, start_time, end_time,
                    duration_seconds, memory_peak_mb, memory_avg_mb, cpu_peak_percent,
                    cpu_avg_percent, disk_read_mb, disk_write_mb, network_sent_mb,
                    network_recv_mb, exit_code, success, retry_count, parallel_worker_id,
                    dependencies_wait_time, setup_time, teardown_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.test_id, metrics.test_name, metrics.category, metrics.module,
                metrics.start_time, metrics.end_time, metrics.duration_seconds,
                metrics.memory_peak_mb, metrics.memory_avg_mb, metrics.cpu_peak_percent,
                metrics.cpu_avg_percent, metrics.disk_read_mb, metrics.disk_write_mb,
                metrics.network_sent_mb, metrics.network_recv_mb, metrics.exit_code,
                metrics.success, metrics.retry_count, metrics.parallel_worker_id,
                metrics.dependencies_wait_time, metrics.setup_time, metrics.teardown_time
            ))
            conn.commit()
    
    def _save_suite_metrics(self, metrics: TestSuiteMetrics):
        """Save test suite metrics to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO test_suites (
                    suite_id, suite_name, start_time, end_time, total_duration_seconds,
                    test_count, passed_count, failed_count, skipped_count, parallel_workers,
                    parallel_efficiency, resource_utilization, bottlenecks, performance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.suite_id, metrics.suite_name, metrics.start_time, metrics.end_time,
                metrics.total_duration_seconds, metrics.test_count, metrics.passed_count,
                metrics.failed_count, metrics.skipped_count, metrics.parallel_workers,
                metrics.parallel_efficiency, json.dumps(metrics.resource_utilization),
                json.dumps(metrics.bottlenecks), metrics.performance_score
            ))
            conn.commit()
    
    def _generate_performance_report(self, suite_metrics: TestSuiteMetrics):
        """Generate comprehensive performance report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create detailed report
        report = {
            'suite_metrics': asdict(suite_metrics),
            'test_metrics': [asdict(m) for m in self.test_metrics],
            'performance_analysis': self._analyze_performance(),
            'recommendations': self._generate_recommendations(),
            'historical_comparison': self._compare_with_history(suite_metrics.suite_name)
        }
        
        # Save JSON report
        json_file = self.monitoring_dir / f"performance_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save as latest
        latest_file = self.monitoring_dir / "performance_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate HTML report
        self._generate_html_report(report, timestamp)
        
        self.logger.info(f"📊 Performance report generated: {json_file}")
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze test performance patterns."""
        if not self.test_metrics:
            return {}
        
        analysis = {
            'execution_times': {
                'fastest_test': min(self.test_metrics, key=lambda m: m.duration_seconds),
                'slowest_test': max(self.test_metrics, key=lambda m: m.duration_seconds),
                'avg_duration': statistics.mean(m.duration_seconds for m in self.test_metrics),
                'median_duration': statistics.median(m.duration_seconds for m in self.test_metrics)
            },
            'resource_usage': {
                'peak_memory_test': max(self.test_metrics, key=lambda m: m.memory_peak_mb),
                'avg_memory_usage': statistics.mean(m.memory_avg_mb for m in self.test_metrics),
                'peak_cpu_test': max(self.test_metrics, key=lambda m: m.cpu_peak_percent),
                'avg_cpu_usage': statistics.mean(m.cpu_avg_percent for m in self.test_metrics)
            },
            'categories': {},
            'modules': {}
        }
        
        # Analyze by category
        categories = set(m.category for m in self.test_metrics)
        for category in categories:
            cat_metrics = [m for m in self.test_metrics if m.category == category]
            analysis['categories'][category] = {
                'count': len(cat_metrics),
                'avg_duration': statistics.mean(m.duration_seconds for m in cat_metrics),
                'success_rate': len([m for m in cat_metrics if m.success]) / len(cat_metrics)
            }
        
        # Analyze by module
        modules = set(m.module for m in self.test_metrics)
        for module in modules:
            mod_metrics = [m for m in self.test_metrics if m.module == module]
            analysis['modules'][module] = {
                'count': len(mod_metrics),
                'avg_duration': statistics.mean(m.duration_seconds for m in mod_metrics),
                'success_rate': len([m for m in mod_metrics if m.success]) / len(mod_metrics)
            }
        
        return analysis
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        if not self.test_metrics:
            return recommendations
        
        # Analyze slow tests
        avg_duration = statistics.mean(m.duration_seconds for m in self.test_metrics)
        slow_tests = [m for m in self.test_metrics if m.duration_seconds > avg_duration * 3]
        
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow tests (>3x average duration)")
        
        # Analyze memory usage
        high_memory_tests = [m for m in self.test_metrics if m.memory_peak_mb > 1000]
        if high_memory_tests:
            recommendations.append(f"Investigate {len(high_memory_tests)} memory-intensive tests (>1GB)")
        
        # Analyze failure patterns
        failed_tests = [m for m in self.test_metrics if not m.success]
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failing tests to improve reliability")
        
        # Analyze parallel efficiency
        if len(self.test_metrics) > 1:
            total_time = sum(m.duration_seconds for m in self.test_metrics)
            suite_duration = max(m.end_time for m in self.test_metrics) - min(m.start_time for m in self.test_metrics)
            
            if suite_duration > 0:
                efficiency = total_time / suite_duration
                if efficiency < 2.0:  # Less than 2x speedup
                    recommendations.append("Consider increasing parallelization for better efficiency")
        
        return recommendations
    
    def _compare_with_history(self, suite_name: str) -> Dict[str, Any]:
        """Compare current performance with historical data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT performance_score, total_duration_seconds, parallel_efficiency
                    FROM test_suites 
                    WHERE suite_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, (suite_name,))
                
                historical_data = cursor.fetchall()
                
                if len(historical_data) > 1:
                    current = historical_data[0]
                    previous = historical_data[1]
                    
                    return {
                        'performance_trend': (current[0] - previous[0]) / previous[0] * 100 if previous[0] > 0 else 0,
                        'duration_trend': (current[1] - previous[1]) / previous[1] * 100 if previous[1] > 0 else 0,
                        'efficiency_trend': (current[2] - previous[2]) / previous[2] * 100 if previous[2] > 0 else 0,
                        'historical_count': len(historical_data)
                    }
        except Exception as e:
            self.logger.warning(f"Failed to compare with history: {e}")
        
        return {}
    
    def _generate_html_report(self, report: Dict, timestamp: str):
        """Generate HTML performance report."""
        suite_metrics = report['suite_metrics']
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Performance Report - {suite_metrics['suite_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #e8f4fd; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 2em; font-weight: bold; color: #0066cc; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .bottlenecks {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .recommendations {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .test-list {{ max-height: 400px; overflow-y: auto; }}
        .test-item {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .slow {{ border-left: 4px solid #dc3545; }}
        .fast {{ border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Performance Report</h1>
        <h2>{suite_metrics['suite_name']}</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="score">Performance Score: {suite_metrics['performance_score']:.1f}/100</div>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Total Duration</h3>
            <p>{suite_metrics['total_duration_seconds']:.2f}s</p>
        </div>
        <div class="metric">
            <h3>Tests Run</h3>
            <p>{suite_metrics['test_count']}</p>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <p>{(suite_metrics['passed_count'] / max(suite_metrics['test_count'], 1) * 100):.1f}%</p>
        </div>
        <div class="metric">
            <h3>Parallel Efficiency</h3>
            <p>{suite_metrics['parallel_efficiency']:.1%}</p>
        </div>
        <div class="metric">
            <h3>Parallel Workers</h3>
            <p>{suite_metrics['parallel_workers']}</p>
        </div>
        <div class="metric">
            <h3>Avg Memory</h3>
            <p>{suite_metrics['resource_utilization'].get('avg_memory_mb', 0):.1f}MB</p>
        </div>
    </div>
    
    <div class="bottlenecks">
        <h3>Performance Bottlenecks</h3>
        <ul>
            {''.join([f'<li>{bottleneck}</li>' for bottleneck in suite_metrics['bottlenecks']])}
        </ul>
    </div>
    
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in report['recommendations']])}
        </ul>
    </div>
    
    <div class="test-list">
        <h3>Individual Test Performance</h3>
        {''.join([f'''
        <div class="test-item {'slow' if test['duration_seconds'] > 10 else 'fast'}">
            <strong>{test['test_name']}</strong> ({test['category']})
            <br>Duration: {test['duration_seconds']:.2f}s | Memory: {test['memory_peak_mb']:.1f}MB | 
            CPU: {test['cpu_peak_percent']:.1f}% | Success: {'✅' if test['success'] else '❌'}
        </div>
        ''' for test in report['test_metrics']])}
    </div>
</body>
</html>
        """
        
        html_file = self.monitoring_dir / f"performance_report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save as latest
        latest_html = self.monitoring_dir / "performance_latest.html"
        with open(latest_html, 'w', encoding='utf-8') as f:
            f.write(html_content)


class IndividualTestMonitor:
    """Monitors individual test execution."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_samples = []
        self.process = psutil.Process()
        self.initial_io = None
        self.initial_net = None
    
    def start_monitoring(self, interval: float = 0.1):
        """Start monitoring individual test."""
        self.monitoring = True
        self.resource_samples.clear()
        
        # Get initial I/O counters
        try:
            self.initial_io = self.process.io_counters()
        except (psutil.AccessDenied, AttributeError):
            self.initial_io = None
        
        try:
            self.initial_net = psutil.net_io_counters()
        except (psutil.AccessDenied, AttributeError):
            self.initial_net = None
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Optional[Dict[str, float]]:
        """Stop monitoring and return resource statistics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        if not self.resource_samples:
            return None
        
        # Calculate statistics
        memory_values = [s['memory_mb'] for s in self.resource_samples]
        cpu_values = [s['cpu_percent'] for s in self.resource_samples]
        
        # Get final I/O counters
        disk_read_mb = 0.0
        disk_write_mb = 0.0
        network_sent_mb = 0.0
        network_recv_mb = 0.0
        
        try:
            if self.initial_io:
                final_io = self.process.io_counters()
                disk_read_mb = (final_io.read_bytes - self.initial_io.read_bytes) / 1024 / 1024
                disk_write_mb = (final_io.write_bytes - self.initial_io.write_bytes) / 1024 / 1024
        except (psutil.AccessDenied, AttributeError):
            pass
        
        try:
            if self.initial_net:
                final_net = psutil.net_io_counters()
                network_sent_mb = (final_net.bytes_sent - self.initial_net.bytes_sent) / 1024 / 1024
                network_recv_mb = (final_net.bytes_recv - self.initial_net.bytes_recv) / 1024 / 1024
        except (psutil.AccessDenied, AttributeError):
            pass
        
        return {
            'memory_peak_mb': max(memory_values),
            'memory_avg_mb': statistics.mean(memory_values),
            'cpu_peak_percent': max(cpu_values),
            'cpu_avg_percent': statistics.mean(cpu_values),
            'disk_read_mb': disk_read_mb,
            'disk_write_mb': disk_write_mb,
            'network_sent_mb': network_sent_mb,
            'network_recv_mb': network_recv_mb
        }
    
    def _monitor_loop(self, interval: float):
        """Monitor resource usage in a loop."""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()
                
                sample = {
                    'timestamp': time.time(),
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'cpu_percent': cpu_percent
                }
                
                self.resource_samples.append(sample)
                
            except Exception:
                pass  # Ignore monitoring errors
            
            time.sleep(interval)


class SystemResourceMonitor:
    """Monitors system-wide resources during test execution."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_data = []
    
    def start_monitoring(self, interval: float = 1.0):
        """Start system resource monitoring."""
        self.monitoring = True
        self.resource_data.clear()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> List[Dict]:
        """Stop monitoring and return collected data."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        return self.resource_data.copy()
    
    def _monitor_loop(self, interval: float):
        """Monitor system resources in a loop."""
        while self.monitoring:
            try:
                data = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_io': self._get_disk_io(),
                    'network_io': self._get_network_io()
                }
                
                self.resource_data.append(data)
                
            except Exception:
                pass  # Ignore monitoring errors
            
            time.sleep(interval)
    
    def _get_disk_io(self) -> Dict:
        """Get disk I/O statistics."""
        try:
            io_stats = psutil.disk_io_counters()
            if io_stats:
                return {
                    'read_mb': io_stats.read_bytes / 1024 / 1024,
                    'write_mb': io_stats.write_bytes / 1024 / 1024
                }
        except:
            pass
        
        return {'read_mb': 0, 'write_mb': 0}
    
    def _get_network_io(self) -> Dict:
        """Get network I/O statistics."""
        try:
            net_stats = psutil.net_io_counters()
            if net_stats:
                return {
                    'sent_mb': net_stats.bytes_sent / 1024 / 1024,
                    'recv_mb': net_stats.bytes_recv / 1024 / 1024
                }
        except:
            pass
        
        return {'sent_mb': 0, 'recv_mb': 0}


def main():
    """Example usage of test performance monitoring."""
    import time
    import random
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    monitor = TestPerformanceMonitor()
    
    # Simulate test suite execution
    with monitor.monitor_test_suite("example_suite", parallel_workers=4) as suite_monitor:
        
        # Simulate individual tests
        for i in range(10):
            test_name = f"test_example_{i}"
            category = random.choice(["unit", "integration", "ui"])
            module = f"module_{i % 3}"
            
            with suite_monitor.monitor_test(test_name, category, module) as test_metrics:
                # Simulate test execution
                execution_time = random.uniform(0.5, 5.0)
                time.sleep(execution_time)
                
                # Simulate occasional failures
                if random.random() < 0.1:
                    raise Exception("Simulated test failure")
    
    print("✅ Test performance monitoring completed")
    print("📊 Check test_reports/performance_monitoring/ for detailed reports")


if __name__ == "__main__":
    main()