# This file makes the logs directory a Python package
# It can be used to configure logging at the package level

# Import the enhanced logging configuration
from ..enhanced_logging import setup_logging, SignalLogger, log_function_calls

# Set up default logging when the package is imported
setup_logging()

__all__ = ['setup_logging', 'SignalLogger', 'log_function_calls']
