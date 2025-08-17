# Enhanced Logging for GopiAI-UI

This document describes the enhanced logging system implemented for the GopiAI-UI application.

## Overview

The enhanced logging system provides comprehensive logging capabilities including:

- Detailed log messages with timestamps and source locations
- Log rotation (10MB per file, 5 backups)
- Separate log levels for different components
- Signal logging for PyQt signals
- Function call logging
- Exception handling and stack traces
- Import tracing
- Environment information

## Files

- `gopiai/enhanced_logging.py`: Core logging configuration and utilities
- `gopiai/logs/__init__.py`: Package initialization with logging setup
- `main_with_logging.py`: Main application entry point with enhanced logging
- `run_with_enhanced_logging.sh`: Shell script to run with full debugging
- `logs/gopiai_ui.log`: Main log file (rotated)

## Usage

### Running with Enhanced Logging

```bash
./run_with_enhanced_logging.sh
```

This will:
1. Enable Qt debug plugins
2. Set up Python's development mode
3. Log all output to both console and file
4. Save a copy of startup logs with timestamp

### Logging in Your Code

```python
import logging

# Get a logger for your module
logger = logging.getLogger('gopiai.your_module')

# Log messages at different levels
logger.debug("Detailed debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")

# Log exceptions with stack traces
try:
    # Your code here
    pass
except Exception as e:
    logger.exception("An error occurred")
```

### Logging PyQt Signals

```python
from gopiai.enhanced_logging import SignalLogger

# Connect a signal and log its emissions
button.clicked.connect(
    SignalLogger.connect_signal(button.clicked, your_slot_function)
)
```

### Logging Function Calls

```python
from gopiai.enhanced_logging import log_function_calls

@log_function_calls
class YourClass:
    def your_method(self, arg1, arg2):
        # Method implementation
        pass
```

## Log File Location

Logs are stored in the `logs` directory:
- Main log: `logs/gopiai_ui.log`
- Startup logs: `logs/startup_YYYYMMDD_HHMMSS.log`

## Configuration

You can adjust the logging configuration in `gopiai/enhanced_logging.py`:
- Log level
- Log file location and rotation settings
- Format of log messages
- Which modules have debug logging enabled

## Viewing Logs

### Terminal
```bash
tail -f logs/gopiai_ui.log
```

### Filtering Logs
```bash
# Show only error messages
grep "\[ERROR\]" logs/gopiai_ui.log

# Show logs for a specific module
grep "\[your_module\]" logs/gopiai_ui.log

# Show recent errors
tail -n 100 logs/gopiai_ui.log | grep -i error
```
