"""
Logger module for UI components.

This module provides a centralized logging system for all UI components.
"""

import logging
import sys
from pathlib import Path

# Create a logger with the specified name
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger (usually __name__)
        
    Returns:
        A configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(ch)
    
    # Add file handler if running in a script
    if not getattr(sys, 'frozen', False):
        try:
            # Create logs directory if it doesn't exist
            log_dir = Path(__file__).parent.parent.parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            # Create file handler which logs even debug messages
            fh = logging.FileHandler(log_dir / 'ui_components.log', encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger
