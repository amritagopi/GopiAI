#!/usr/bin/env python3
"""
Single Entry Point for All GopiAI Tests

This script provides a unified interface for running all types of tests
across the GopiAI project with enhanced features:

- Parallel execution of independent tests
- Test prioritization by importance  
- Automatic retry for unstable tests
- Comprehensive reporting and analysis

Usage Examples:
    python run_all_tests.py                    # Run all tests with smart defaults
    python run_all_tests.py --unit             # Run only unit tests
    python run_all_tests.py --integration      # Run only integration tests
    python run_all_tests.py --ui               # Run only UI tests
    python run_all_tests.py --e2e              # Run only E2E tests
    python run_all_tests.py --performance      # Run only performance tests
    python run_all_tests.py --security         # Run only security tests
    
    python run_all_tests.py --fast             # Run critical tests only (fast)
    python run_all_tests.py --full             # Run all tests (comprehensive)
    
    python run_all_tests.py --sequential       # Run tests sequentially
    python run_all_tests.py --no-retry         # Disable retry mechanism
    python run_all_tests.py --max-workers 8    # Use 8 parallel workers
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

try:
    from master_test_runner import MasterTestRunner, TestCategory, TestEnvironment, RetryConfig
    from test_discovery import TestDiscovery
    from problem_discovery import ProblemDiscovery
except ImportError as e:
    print(f"❌ Error importing test infrastructure: {e}")
    print("Please ensure test_infrastructure modules are available")
    sys.exit(1)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('run_all_tests.log')
        ]
    )
    return logging.getLogger(__name__)


def print_banner():
    """Print the application banner."""
    print("=" * 80)
    print("🚀 GopiAI Comprehensive Test Runner")
    print("   Single Entry Point for All Test Types")
    print("   Features: Parallel Execution | Prioritization | Auto-Retry | Smart Reporting")
    print("=" * 80)


def main():
    """Main entry point for the comprehensive test runner."""
    parser = argparse.ArgumentParser(
        description="GopiAI Comprehensive Test Runner - Single Entry Point for All Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Categories:
  --unit          Run unit tests (fast, isolated tests)
  --integration   Run integration tests (component interaction tests)
  --ui            Run UI tests (user interface tests)
  --e2e           Run end-to-end tests (full user scenarios)
  --performance   Run performance tests (benchmarks and load tests)
  --security      Run security tests (vulnerability and auth tests)

Execution Modes:
  --fast          Run critical tests only (unit + integration + security)
  --full          Run all test categories (comprehensive testing)
  --parallel      Run tests in parallel (default, faster)
  --sequential    Run tests sequentially (slower, better for debugging)

Advanced Options:
  --prioritize    Enable test prioritization (default, runs important tests first)
  --retry         Enable automatic retry for failed tests (default)
  --max-workers N Use N parallel workers (default: 4)
  --timeout N     Set test timeout in seconds (default: 600)

Examples:
  python run_all_tests.py                    # Smart defaults (fast, parallel, with retry)
  python run_all_tests.py --full             # Run all tests comprehensively
  python run_all_tests.py --unit --parallel  # Run unit tests in parallel
  python run_all_tests.py --integration --sequential --no-retry
  python run_all_tests.py --fast --max-workers 8
        """
    )
    
    # Test category selection
    category_group = parser.add_argument_group('Test Categories')
    category_group.add_argument('--unit', action='store_true', 
                               help='Run unit tests')
    category_group.add_argument('--integration', action='store_true', 
                               help='Run integration tests')
    category_group.add_argument('--ui', action='store_true', 
                               help='Run UI tests')
    category_group.add_argument('--e2e', action='store_true', 
                               help='Run end-to-end tests')
    category_group.add_argument('--performance', action='store_true', 
                               help='Run performance tests')
    category_group.add_argument('--security', action='store_true', 
                               help='Run security tests')
    
    # Execution modes
    mode_group = parser.add_argument_group('Execution Modes')
    mode_group.add_argument('--fast', action='store_true',
                           help='Run critical tests only (unit + integration + security)')
    mode_group.add_argument('--full', action='store_true',
                           help='Run all test categories')
    mode_group.add_argument('--parallel', action='store_true', default=True,
                           help='Run tests in parallel (default)')
    mode_group.add_argument('--sequential', action='store_true',
                           help='Run tests sequentially')
    
    # Environment selection
    env_group = parser.add_argument_group('Environment Options')
    env_group.add_argument('--env', choices=['crewai_env', 'gopiai_env', 'txtai_env'],
                          help='Run tests in specific environment only')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--no-prioritize', action='store_true',
                               help='Disable test prioritization')
    advanced_group.add_argument('--no-retry', action='store_true',
                               help='Disable automatic retry for failed tests')
    advanced_group.add_argument('--max-workers', type=int, default=4,
                               help='Maximum number of parallel workers (default: 4)')
    advanced_group.add_argument('--max-retries', type=int, default=3,
                               help='Maximum retries per failed test (default: 3)')
    advanced_group.add_argument('--retry-delay', type=float, default=1.0,
                               help='Base delay between retries in seconds (default: 1.0)')
    advanced_group.add_argument('--timeout', type=int, default=600,
                               help='Test timeout in seconds (default: 600)')
    
    # Discovery and reporting
    discovery_group = parser.add_argument_group('Discovery and Reporting')
    discovery_group.add_argument('--discover-only', action='store_true',
                                help='Only discover tests, do not run them')
    discovery_group.add_argument('--problems-only', action='store_true',
                                help='Only discover problems, do not run tests')
    discovery_group.add_argument('--no-reports', action='store_true',
                                help='Skip comprehensive report generation')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--verbose', '-v', action='store_true',
                             help='Verbose output with debug information')
    output_group.add_argument('--quiet', '-q', action='store_true',
                             help='Quiet mode (errors and summary only)')
    output_group.add_argument('--no-banner', action='store_true',
                             help='Skip banner display')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    logger = setup_logging(log_level)
    
    # Print banner unless suppressed
    if not args.no_banner and not args.quiet:
        print_banner()
    
    # Handle discovery-only modes
    if args.discover_only:
        logger.info("🔍 Running test discovery only...")
        discovery = TestDiscovery()
        test_modules = discovery.discover_all_tests()
        report = discovery.generate_discovery_report()
        
        print(f"\n📊 Test Discovery Results:")
        print(f"   Total test modules: {len(test_modules)}")
        print(f"   Report saved to: test_discovery_report.json")
        return 0
    
    if args.problems_only:
        logger.info("🔍 Running problem discovery only...")
        discovery = ProblemDiscovery()
        problems = discovery.discover_all_problems()
        report = discovery.generate_report()
        discovery.generate_pytest_markers()
        
        print(f"\n⚠️ Problem Discovery Results:")
        print(f"   Total problems found: {len(problems)}")
        print(f"   Report saved to: problem_discovery_report.json")
        return 0
    
    # Determine test categories to run
    categories = []
    
    if args.fast:
        categories = [TestCategory.UNIT, TestCategory.INTEGRATION, TestCategory.SECURITY]
        logger.info("🏃 Fast mode: Running critical tests only")
    elif args.full:
        categories = list(TestCategory)
        logger.info("🔬 Full mode: Running all test categories")
    else:
        # Individual category selection
        if args.unit:
            categories.append(TestCategory.UNIT)
        if args.integration:
            categories.append(TestCategory.INTEGRATION)
        if args.ui:
            categories.append(TestCategory.UI)
        if args.e2e:
            categories.append(TestCategory.E2E)
        if args.performance:
            categories.append(TestCategory.PERFORMANCE)
        if args.security:
            categories.append(TestCategory.SECURITY)
        
        # Default to fast mode if no categories specified
        if not categories:
            categories = [TestCategory.UNIT, TestCategory.INTEGRATION, TestCategory.SECURITY]
            logger.info("🎯 No categories specified, defaulting to critical tests")
    
    # Determine environments
    environments = []
    if args.env:
        environments = [TestEnvironment(args.env)]
    
    # Determine execution mode
    parallel = args.parallel and not args.sequential
    prioritize = not args.no_prioritize
    enable_retry = not args.no_retry
    
    # Create retry configuration
    retry_config = RetryConfig(
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        exponential_backoff=True
    )
    
    # Print configuration
    if not args.quiet:
        print(f"⚙️ Configuration:")
        print(f"   📂 Categories: {[c.value for c in categories]}")
        print(f"   🌍 Environments: {[e.value for e in environments] if environments else 'all'}")
        print(f"   ⚡ Parallel: {parallel} (workers: {args.max_workers})")
        print(f"   🎯 Prioritization: {prioritize}")
        print(f"   🔄 Retry: {enable_retry} (max: {args.max_retries})")
        print()
    
    try:
        # Create and configure test runner
        runner = MasterTestRunner(
            max_workers=args.max_workers,
            retry_config=retry_config
        )
        
        # Run tests
        logger.info("🚀 Starting test execution...")
        summary = runner.run_all_tests(
            categories=categories,
            environments=environments,
            parallel=parallel,
            prioritize=prioritize,
            enable_retry=enable_retry,
            generate_reports=not args.no_reports
        )
        
        # Print results
        if not args.quiet:
            print("\n" + "="*80)
            print("📊 TEST EXECUTION RESULTS")
            print("="*80)
            print(f"📈 Total executions: {summary['total_executions']}")
            print(f"✅ Passed: {summary['passed']}")
            print(f"❌ Failed: {summary['failed']}")
            print(f"⊝ Skipped: {summary['skipped']}")
            print(f"💥 Errors: {summary['errors']}")
            print(f"🔄 Total retries: {summary['total_retries']}")
            print(f"📊 Success rate: {summary['success_rate']:.1f}%")
            print(f"⏱️ Total duration: {summary['total_duration']:.2f}s")
            
            # Show priority breakdown
            if summary.get('by_priority'):
                print(f"\n🎯 Results by Priority:")
                for priority, stats in summary['by_priority'].items():
                    success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    print(f"   {priority}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
            
            # Show retry statistics
            retry_stats = summary.get('retry_statistics', {})
            if retry_stats.get('tests_retried', 0) > 0:
                print(f"\n🔄 Retry Statistics:")
                print(f"   Tests retried: {retry_stats['tests_retried']}")
                print(f"   Successful after retry: {retry_stats['successful_retries']}")
                print(f"   Failed after retry: {retry_stats['failed_after_retry']}")
            
            if not args.no_reports:
                print(f"\n📋 Reports Generated:")
                print(f"   📊 Execution report: test_execution_report.json")
                print(f"   ⚠️ Problem report: test_problems_report.json")
                print(f"   🏷️ Known issues: test_known_issues.py")
            
            print("="*80)
        
        # Determine exit code
        if summary['failed'] > 0 or summary['errors'] > 0:
            if not args.quiet:
                print("❌ Some tests failed - check logs and reports for details")
            return 1
        else:
            if not args.quiet:
                print("✅ All tests passed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())