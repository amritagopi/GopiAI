"""
Performance Test - Benchmarks for Project Cleanup Analyzer

This module provides benchmarks for the project cleanup analyzer to measure
performance improvements from caching and optimization features.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisConfig
from project_cleanup_orchestrator import ProjectCleanupAnalyzer


class PerformanceBenchmark:
    """Benchmarks for the project cleanup analyzer."""
    
    def __init__(self, project_path: str):
        """
        Initialize the benchmark.
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = project_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure the project path exists
        if not Path(project_path).exists():
            raise ValueError(f"Project path does not exist: {project_path}")
    
    def run_benchmark(self, iterations: int = 2, parallel: bool = True) -> Dict[str, Any]:
        """
        Run a benchmark with different configurations.
        
        Args:
            iterations: Number of iterations for each configuration
            parallel: Whether to run analyzers in parallel
            
        Returns:
            Dictionary with benchmark results
        """
        results = {}
        
        # Test configurations
        configs = [
            {
                'name': 'baseline',
                'enable_caching': False,
                'incremental_analysis': False,
                'analysis_depth': 'standard'
            },
            {
                'name': 'with_caching',
                'enable_caching': True,
                'incremental_analysis': False,
                'analysis_depth': 'standard'
            },
            {
                'name': 'with_incremental',
                'enable_caching': True,
                'incremental_analysis': True,
                'analysis_depth': 'standard'
            },
            {
                'name': 'quick_depth',
                'enable_caching': True,
                'incremental_analysis': True,
                'analysis_depth': 'quick'
            },
            {
                'name': 'full_depth',
                'enable_caching': True,
                'incremental_analysis': True,
                'analysis_depth': 'full'
            }
        ]
        
        # Run benchmarks for each configuration
        for config in configs:
            config_name = config['name']
            self.logger.info(f"Running benchmark for configuration: {config_name}")
            
            # Create configuration
            analysis_config = AnalysisConfig(
                project_path=self.project_path,
                enable_caching=config['enable_caching'],
                incremental_analysis=config['incremental_analysis'],
                analysis_depth=config['analysis_depth']
            )
            
            # Run iterations
            times = []
            for i in range(iterations):
                self.logger.info(f"  Iteration {i+1}/{iterations}")
                
                # Create analyzer
                analyzer = ProjectCleanupAnalyzer(config=analysis_config)
                
                # Run analysis and measure time
                start_time = time.time()
                analyzer.run_full_analysis(parallel=parallel, output_path=f"benchmark_{config_name}_{i}.md")
                elapsed = time.time() - start_time
                
                times.append(elapsed)
                self.logger.info(f"  Completed in {elapsed:.2f} seconds")
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results[config_name] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'times': times,
                'config': config
            }
            
            self.logger.info(f"  Average time: {avg_time:.2f} seconds")
        
        return results
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Print benchmark results.
        
        Args:
            results: Benchmark results
        """
        print("\nBenchmark Results:")
        print("-" * 80)
        print(f"{'Configuration':<15} {'Avg Time (s)':<15} {'Min Time (s)':<15} {'Max Time (s)':<15}")
        print("-" * 80)
        
        baseline_time = results.get('baseline', {}).get('avg_time', 0)
        
        for name, result in results.items():
            avg_time = result['avg_time']
            min_time = result['min_time']
            max_time = result['max_time']
            
            # Calculate speedup compared to baseline
            speedup = baseline_time / avg_time if baseline_time > 0 and avg_time > 0 else 0
            speedup_str = f" ({speedup:.2f}x)" if name != 'baseline' and speedup > 0 else ""
            
            print(f"{name:<15} {avg_time:<15.2f} {min_time:<15.2f} {max_time:<15.2f}{speedup_str}")
        
        print("-" * 80)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Project Cleanup Analyzer Performance Benchmark')
    
    parser.add_argument(
        '--project-path', '-p',
        type=str,
        default=os.getcwd(),
        help='Path to the project root directory'
    )
    
    parser.add_argument(
        '--iterations', '-i',
        type=int,
        default=2,
        help='Number of iterations for each configuration'
    )
    
    parser.add_argument(
        '--sequential', '-s',
        action='store_true',
        help='Run analyzers sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level'
    )
    
    return parser.parse_args()


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('performance_benchmark.log')
        ]
    )


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    
    try:
        # Run benchmark
        benchmark = PerformanceBenchmark(args.project_path)
        results = benchmark.run_benchmark(
            iterations=args.iterations,
            parallel=not args.sequential
        )
        
        # Print results
        benchmark.print_results(results)
        
    except Exception as e:
        logging.error(f"Error during benchmark: {e}", exc_info=True)
        sys.exit(1)