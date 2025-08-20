#!/usr/bin/env python3
"""
GopiAI Test Runner

Unified test runner for all GopiAI modules with comprehensive reporting
and problem discovery integration.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add test_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / "test_infrastructure"))

from master_test_runner import MasterTestRunner
from test_discovery import TestCategory, TestEnvironment
from problem_discovery import ProblemDiscovery


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_runner.log')
        ]
    )


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(
        description="GopiAI Comprehensive Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit                   # Run only unit tests
  python run_tests.py --integration            # Run only integration tests
  python run_tests.py --ui                     # Run only UI tests
  python run_tests.py --e2e                    # Run only E2E tests
  python run_tests.py --performance            # Run only performance tests
  python run_tests.py --security               # Run only security tests
  
  python run_tests.py --env crewai_env          # Run tests in CrewAI environment
  python run_tests.py --env gopiai_env          # Run tests in GopiAI environment
  
  python run_tests.py --module GopiAI-UI        # Run tests for specific module
  python run_tests.py --discover-problems      # Run problem discovery only
  
  python run_tests.py --unit --parallel        # Run unit tests in parallel
  python run_tests.py --all --no-reports       # Run all tests without reports
        """
    )
    
    # Test category options
    test_group = parser.add_argument_group('Test Categories')
    test_group.add_argument('--all', action='store_true', 
                           help='Run all tests')
    test_group.add_argument('--unit', action='store_true', 
                           help='Run unit tests')
    test_group.add_argument('--integration', action='store_true', 
                           help='Run integration tests')
    test_group.add_argument('--ui', action='store_true', 
                           help='Run UI tests')
    test_group.add_argument('--e2e', action='store_true', 
                           help='Run end-to-end tests')
    test_group.add_argument('--performance', action='store_true', 
                           help='Run performance tests')
    test_group.add_argument('--security', action='store_true', 
                           help='Run security tests')
    
    # Environment options
    env_group = parser.add_argument_group('Environment Options')
    env_group.add_argument('--env', choices=['crewai_env', 'gopiai_env', 'txtai_env'],
                          help='Run tests in specific environment')
    
    # Module options
    module_group = parser.add_argument_group('Module Options')
    module_group.add_argument('--module', choices=['GopiAI-Core', 'GopiAI-UI', 'GopiAI-CrewAI', 'GopiAI-Assets'],
                             help='Run tests for specific module')
    
    # Execution options
    exec_group = parser.add_argument_group('Execution Options')
    exec_group.add_argument('--parallel', action='store_true', 
                           help='Run tests in parallel')
    exec_group.add_argument('--no-reports', action='store_true', 
                           help='Skip report generation')
    exec_group.add_argument('--timeout', type=int, default=300,
                           help='Test timeout in seconds (default: 300)')
    
    # Discovery options
    discovery_group = parser.add_argument_group('Discovery Options')
    discovery_group.add_argument('--discover-problems', action='store_true',
                                help='Run problem discovery only')
    discovery_group.add_argument('--discover-tests', action='store_true',
                                help='Run test discovery only')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--verbose', '-v', action='store_true',
                             help='Verbose output')
    output_group.add_argument('--quiet', '-q', action='store_true',
                             help='Quiet output (errors only)')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        setup_logging(False)
        logging.getLogger().setLevel(logging.ERROR)
    else:
        setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    
    # Handle discovery-only options
    if args.discover_problems:
        logger.info("Running problem discovery...")
        discovery = ProblemDiscovery()
        problems = discovery.discover_all_problems()
        report = discovery.generate_report()
        discovery.generate_pytest_markers()
        
        print(f"\nProblem Discovery Results:")
        print(f"Total problems found: {len(problems)}")
        print(f"Report saved to: problem_discovery_report.json")
        print(f"Pytest markers saved to: pytest_markers.py")
        
        return 0
    
    if args.discover_tests:
        logger.info("Running test discovery...")
        from test_discovery import TestDiscovery
        discovery = TestDiscovery()
        test_modules = discovery.discover_all_tests()
        report = discovery.generate_discovery_report()
        
        print(f"\nTest Discovery Results:")
        print(f"Total test modules found: {len(test_modules)}")
        print(f"Report saved to: test_discovery_report.json")
        
        return 0
    
    # Determine what tests to run
    categories = []
    if args.all:
        categories = list(TestCategory)
    else:
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
    
    # Default to unit tests if nothing specified
    if not categories:
        categories = [TestCategory.UNIT]
        logger.info("No test category specified, defaulting to unit tests")
    
    # Determine environments
    environments = []
    if args.env:
        environments = [TestEnvironment(args.env)]
    
    # Create and run tests
    logger.info("Starting GopiAI test runner...")
    runner = MasterTestRunner()
    
    try:
        summary = runner.run_all_tests(
            categories=categories,
            environments=environments,
            parallel=args.parallel,
            generate_reports=not args.no_reports
        )
        
        # Print summary
        print("\n" + "="*60)
        print("GOPIAI TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total executions: {summary['total_executions']}")
        print(f"Passed: {summary['passed']} ✓")
        print(f"Failed: {summary['failed']} ✗")
        print(f"Skipped: {summary['skipped']} ⊝")
        print(f"Errors: {summary['errors']} ⚠")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total duration: {summary['total_duration']:.2f}s")
        
        if not args.no_reports:
            print(f"\nReports generated:")
            print(f"  - Test execution report: test_execution_report.json")
            print(f"  - Problem discovery report: test_problems_report.json")
            print(f"  - Known issues markers: test_known_issues.py")
        
        print("="*60)
        
        # Exit with appropriate code
        if summary['failed'] > 0 or summary['errors'] > 0:
            logger.error("Some tests failed or had errors")
            return 1
        else:
            logger.info("All tests passed successfully")
            return 0
            
    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())