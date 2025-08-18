#!/usr/bin/env python3
"""
GopiAI-UI with Enhanced Logging

This is the main entry point for the GopiAI UI application with comprehensive logging enabled.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and set up enhanced logging before any other imports
from gopiai.enhanced_logging import setup_logging, SignalLogger

# Configure logging with maximum verbosity
setup_logging(log_level=logging.DEBUG, log_to_file=True)
logger = logging.getLogger('gopiai.main')

# Log Python environment info
logger.info("=" * 80)
logger.info("Starting GopiAI-UI with enhanced logging")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

# Now import the rest of the application
from PySide6.QtWidgets import QApplication
from gopiai.ui.main_window import MainWindow

def main():
    try:
        logger.info("Initializing QApplication")
        app = QApplication(sys.argv)
        
        # Log application arguments
        logger.debug(f"Application arguments: {sys.argv}")
        
        # Log environment variables (safely)
        env_vars = [
            'PYTHONPATH', 'PATH', 'LD_LIBRARY_PATH',
            'QT_DEBUG_PLUGINS', 'QT_LOGGING_RULES'
        ]
        for var in env_vars:
            if var in os.environ:
                logger.debug(f"Environment {var}: {os.environ[var]}")
        
        logger.info("Creating main window")
        window = MainWindow()
        
        # Connect window signals to logger
        try:
            SignalLogger.connect_signal(window.aboutToQuit, lambda: logger.info("Application about to quit"))
        except Exception as e:
            logger.error(f"Failed to connect window signals: {e}")
        
        logger.info("Showing main window")
        window.show()
        
        logger.info("Entering application event loop")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical("Fatal error in main", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
