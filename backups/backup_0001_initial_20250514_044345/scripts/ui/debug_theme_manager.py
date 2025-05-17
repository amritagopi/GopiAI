#!/usr/bin/env python
# Debug script for ThemeManager

import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the app directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Create QApplication instance (required for ThemeManager)
app = QApplication(sys.argv)

def run_theme_manager_tests():
    """Run tests for ThemeManager functionality"""
    try:
        from app.utils.theme_manager import ThemeManager

        # Get ThemeManager instance
        theme_manager = ThemeManager.instance()
        logger.info(f"ThemeManager instance created: {theme_manager}")

        # Test get_available_visual_themes method
        try:
            available_themes = theme_manager.get_available_visual_themes()
            logger.info(f"Available visual themes: {available_themes}")
        except Exception as e:
            logger.error(f"Error in get_available_visual_themes: {e}")

        # Test get_current_visual_theme method
        try:
            current_theme = theme_manager.get_current_visual_theme()
            logger.info(f"Current visual theme: {current_theme}")
        except Exception as e:
            logger.error(f"Error in get_current_visual_theme: {e}")

        # Test switch_visual_theme method
        try:
            if 'dark' in available_themes and theme_manager.current_visual_theme != 'dark':
                success = theme_manager.switch_visual_theme('dark')
                logger.info(f"Switch to dark theme result: {success}")
                current_theme = theme_manager.get_current_visual_theme()
                logger.info(f"New current theme: {current_theme}")
        except Exception as e:
            logger.error(f"Error in switch_visual_theme: {e}")

    except ImportError as e:
        logger.error(f"Could not import ThemeManager: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_theme_manager_tests()
    sys.exit(0)  # Exit without starting the event loop
