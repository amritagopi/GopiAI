import logging
import logging.handlers
import os
import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# Configure root logger
def setup_logging(log_level: int = logging.DEBUG, log_to_file: bool = True) -> None:
    """
    Configure comprehensive logging for the application.
    
    Args:
        log_level: Logging level (default: DEBUG)
        log_to_file: Whether to log to file (default: True)
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Main application logger
    logger = logging.getLogger('gopiai')
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # File handler with rotation (10MB per file, keep 5 backups)
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / 'gopiai_ui.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
    
    # Detailed formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(detailed_formatter)
    if log_to_file:
        file_handler.setFormatter(detailed_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    if log_to_file:
        logger.addHandler(file_handler)
    
    # Configure third-party loggers
    for lib in ['PyQt5', 'urllib3', 'asyncio']:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    # Enable debug logging for specific modules
    debug_modules = [
        'gopiai.ui',
        'gopiai.core',
        'gopiai.api',
        'gopiai.utils'
    ]
    
    for module in debug_modules:
        logging.getLogger(module).setLevel(logging.DEBUG)
    
    # Log unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
    
    # Log all imports
    old_import = __import__
    
    def log_import(name, *args, **kwargs):
        logger.debug(f"Importing module: {name}")
        return old_import(name, *args, **kwargs)
    
    __builtins__['__import__'] = log_import
    
    logger.info("Logging system initialized")

# Signal logger for PyQt signals
class SignalLogger:
    """Utility class to log PyQt signal emissions"""
    
    @classmethod
    def log_signal(cls, signal, *args):
        """Log signal emission with arguments"""
        logger = logging.getLogger('gopiai.signals')
        try:
            signal_name = signal.__name__ if hasattr(signal, '__name__') else str(signal)
            args_str = ', '.join(repr(arg) for arg in args)
            logger.debug(f"Signal emitted: {signal_name}({args_str})")
        except Exception as e:
            logger.error(f"Error logging signal: {e}")
    
    @classmethod
    def connect_signal(cls, signal, slot):
        """Connect a signal and log its emissions"""
        def wrapped_slot(*args):
            cls.log_signal(signal, *args)
            return slot(*args)
        return signal.connect(wrapped_slot)

# Function to log function calls
def log_function_calls(cls):
    """Class decorator to log all method calls"""
    class DecoratedClass(cls):
        def __getattribute__(self, name):
            attr = super().__getattribute__(name)
            if callable(attr):
                logger = logging.getLogger(f'gopiai.methods.{cls.__name__}')
                
                def wrapped(*args, **kwargs):
                    logger.debug(f"Calling {cls.__name__}.{name} with args={args}, kwargs={kwargs}")
                    try:
                        result = attr(*args, **kwargs)
                        logger.debug(f"{cls.__name__}.{name} returned: {result}")
                        return result
                    except Exception as e:
                        logger.error(
                            f"Error in {cls.__name__}.{name}: {e}\n"
                            f"{traceback.format_exc()}"
                        )
                        raise
                return wrapped
            return attr
    return DecoratedClass

# Initialize logging when imported
setup_logging()
