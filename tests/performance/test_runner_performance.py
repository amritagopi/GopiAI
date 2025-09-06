"""
Performance test runner for coordinated execution of all performance tests.
"""
import time
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics


@dataclass
class PerformanceTestResult:
    """Performance test result data structure."""
    test_name: str
    category: str  # api, memory, ui, system
    status: str  # passed, failed, skipped
    duration_ms: float
    metrics: Dict[str, Any]
    error_message: Optional[str] = None


class PerformanceTestRunner:
    """Coordinated performance test execution."""
    
    def __init__(self):
        self.results: List[PerformanceTestResult] = []
        self.start_time = None
        self.end_time = None
        
    def run_all_performance_tests(self, categories: List[str] = None) -> Dict[str, Any]:
        """Run all performance tests in specified categories."""
        if categories is None:
            categories = ['api', 'memory', 'ui', 'system']
        
        self.start_time = time.time()
        self.results.clear()
        
        print("Starting comprehensive performance test suite...")
        
        # Run tests by category
        for category in categories:
            print(f"\n=== Running {category.upper()} Performance Tests ===")
            self._run_category_tests(category)
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        return self._generate_performance_report()
    
    def _run_category_tests(self, category: str):
        """Run performance tests for a specific category."""
        test_modules = {
            'api': 'tests/performance/test_api_benchmarks.py',
            'memory': 'tests/performance/test_memory_performance.py',
            'ui': 'tests/performance/test_ui_performance.py',
            'system': 'tests/performance/test_system_monitoring.py'
        }
        
        if category not in test_modules:
            print(f"Unknown category: {category}")
            return
        
        module_path = test_modules[category]
        
        try:
            # Run pytest for the specific module
            import subprocess
            import sys
            
            cmd = [
                sys.executable, '-m', 'pytest',
                module_path,
                '-v',
                '--tb=short',
                '--json-report',
                f'--json-report-file=performance_report_{category}.json'
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            
            # Parse results
            self._parse_pytest_results(category, result, duration_ms)
            
        except subprocess.TimeoutExpired:
            error_result = PerformanceTestResult(
                test_name=f"{category}_tests",
                category=category,
                status="failed",
                duration_ms=300000,  # 5 minutes timeout
                metrics={},
                error_message="Test execution timed out"
            )
            self.results.append(error_result)
            
        except Exception as e:
            error_result = PerformanceTestResult(
                test_name=f"{category}_tests",
                category=category,
                status="failed",
                duration_ms=0,
                metrics={},
                error_message=str(e)
            )
            self.results.append(error_result)
    
    def _parse_pytest_results(self, category: str, result: subprocess.CompletedProcess, duration_ms: float):
        """Parse pytest results and extract performance metrics."""
        # Try to load JSON report if available
        json_file = f'performance_report_{category}.json'
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    pytest_data = json.load(f)
                
                # Extract test results
                for test in pytest_data.get('tests', []):
                    test_result = PerformanceTestResult(
                        test_name=test.get('nodeid', 'unknown'),
                        category=category,
                        status=test.get('outcome', 'unknown'),
                        duration_ms=test.get('duration', 0) * 1000,
                        metrics=self._extract_performance_metrics(test),
                        error_message=test.get('call', {}).get('longrepr') if test.get('outcome') == 'failed' else None
                    )
                    self.results.append(test_result)
                
                # Cleanup JSON file
                os.remove(json_file)
                
            except Exception as e:
                print(f"Failed to parse JSON report for {category}: {e}")
        
        # Fallback: create summary result
        if not any(r.category == category for r in self.results):
            status = "passed" if result.returncode == 0 else "failed"
            summary_result = PerformanceTestResult(
                test_name=f"{category}_summary",
                category=category,
                status=status,
                duration_ms=duration_ms,
                metrics={'return_code': result.returncode},
                error_message=result.stderr if result.returncode != 0 else None
            )
            self.results.append(summary_result)
    
    def _extract_performance_metrics(self, test_data: Dict) -> Dict[str, Any]:
        """Extract performance metrics from test data."""
        metrics = {}
        
        # Look for performance-related data in test output
        call_data = test_data.get('call', {})
        
        # Extract duration
        if 'duration' in test_data:
            metrics['duration_ms'] = test_data['duration'] * 1000
        
        # Look for custom performance metrics in stdout/stderr
        stdout = call_data.get('stdout', '')
        if 'response_time' in stdout.lower():
            # Try to extract response time metrics
            pass
        
        return metrics
    
    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.results:
            return {'error': 'No test results available'}
        
        # Categorize results
        results_by_category = {}
        for result in self.results:
            if result.category not in results_by_category:
                results_by_category[result.category] = []
            results_by_category[result.category].append(result)
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'passed'])
        failed_tests = len([r for r in self.results if r.status == 'failed'])
        skipped_tests = len([r for r in self.results if r.status == 'skipped'])
        
        # Calculate performance metrics
        durations = [r.duration_ms for r in self.results if r.duration_ms > 0]
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_duration_ms': (self.end_time - self.start_time) * 1000 if self.start_time and self.end_time else 0,
                'avg_test_duration_ms': statistics.mean(durations) if durations else 0,
                'max_test_duration_ms': max(durations) if durations else 0
            },
            'categories': {},
            'failed_tests': [],
            'performance_insights': [],
            'recommendations': []
        }
        
        # Category-specific analysis
        for category, category_results in results_by_category.items():
            category_passed = len([r for r in category_results if r.status == 'passed'])
            category_total = len(category_results)
            category_durations = [r.duration_ms for r in category_results if r.duration_ms > 0]
            
            report['categories'][category] = {
                'total_tests': category_total,
                'passed': category_passed,
                'success_rate': (category_passed / category_total * 100) if category_total > 0 else 0,
                'avg_duration_ms': statistics.mean(category_durations) if category_durations else 0,
                'max_duration_ms': max(category_durations) if category_durations else 0
            }
        
        # Failed tests details
        for result in self.results:
            if result.status == 'failed':
                report['failed_tests'].append({
                    'test_name': result.test_name,
                    'category': result.category,
                    'error': result.error_message,
                    'duration_ms': result.duration_ms
                })
        
        # Generate insights and recommendations
        report['performance_insights'] = self._generate_insights(results_by_category)
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _generate_insights(self, results_by_category: Dict[str, List[PerformanceTestResult]]) -> List[str]:
        """Generate performance insights from test results."""
        insights = []
        
        for category, results in results_by_category.items():
            if not results:
                continue
            
            durations = [r.duration_ms for r in results if r.duration_ms > 0]
            if not durations:
                continue
            
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            if avg_duration > 5000:  # 5 seconds
                insights.append(f"{category.upper()} tests are slow (avg: {avg_duration:.0f}ms)")
            
            if max_duration > 30000:  # 30 seconds
                insights.append(f"{category.upper()} has very slow tests (max: {max_duration:.0f}ms)")
            
            failed_count = len([r for r in results if r.status == 'failed'])
            if failed_count > 0:
                insights.append(f"{category.upper()} has {failed_count} failing performance tests")
        
        return insights
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on performance results."""
        recommendations = []
        
        # Overall success rate
        success_rate = report['summary']['success_rate']
        if success_rate < 80:
            recommendations.append("Performance test success rate is low - investigate failing tests")
        
        # Test duration
        avg_duration = report['summary']['avg_test_duration_ms']
        if avg_duration > 10000:  # 10 seconds
            recommendations.append("Performance tests are taking too long - consider optimization")
        
        # Category-specific recommendations
        for category, stats in report['categories'].items():
            if stats['success_rate'] < 70:
                recommendations.append(f"Improve {category} performance test reliability")
            
            if stats['avg_duration_ms'] > 15000:  # 15 seconds
                recommendations.append(f"Optimize {category} performance test execution time")
        
        # Failed tests
        if len(report['failed_tests']) > 0:
            recommendations.append("Address failing performance tests to improve system reliability")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save performance report to file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Performance report saved to: {filename}")
        except Exception as e:
            print(f"Failed to save report: {e}")


def run_performance_suite(categories: List[str] = None, save_report: bool = True) -> Dict[str, Any]:
    """Main entry point for running performance test suite."""
    runner = PerformanceTestRunner()
    
    try:
        report = runner.run_all_performance_tests(categories)
        
        # Print summary
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUITE SUMMARY")
        print("="*60)
        
        summary = report.get('summary', {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Skipped: {summary.get('skipped', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Total Duration: {summary.get('total_duration_ms', 0)/1000:.1f}s")
        
        # Print insights
        insights = report.get('performance_insights', [])
        if insights:
            print("\nPerformance Insights:")
            for insight in insights:
                print(f"  • {insight}")
        
        # Print recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        # Save report
        if save_report:
            runner.save_report(report)
        
        return report
        
    except Exception as e:
        print(f"Performance test suite failed: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    categories = None
    if len(sys.argv) > 1:
        categories = sys.argv[1].split(',')
        print(f"Running performance tests for categories: {categories}")
    else:
        print("Running all performance test categories")
    
    # Run performance suite
    report = run_performance_suite(categories=categories)
    
    # Exit with appropriate code
    if 'error' in report:
        sys.exit(1)
    elif report.get('summary', {}).get('failed', 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)