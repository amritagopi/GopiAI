#!/usr/bin/env python
# Debug script for PreferencesDialog

import sys
import os
import logging
from PySide6.QtWidgets import QApplication

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the app directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Create QApplication instance (required for dialogs)
app = QApplication(sys.argv)

def debug_preferences_dialog():
    """Debug the PreferencesDialog class"""
    try:
        # First check ThemeManager methods
        from app.utils.theme_manager import ThemeManager
        theme_manager = ThemeManager.instance()

        # Check if expected methods exist in ThemeManager
        methods_to_check = [
            "get_available_visual_themes",
            "get_current_visual_theme",
            "switch_visual_theme",
        ]

        logger.info("Checking ThemeManager methods:")
        for method_name in methods_to_check:
            if hasattr(theme_manager, method_name) and callable(getattr(theme_manager, method_name)):
                logger.info(f"✓ ThemeManager.{method_name} exists and is callable")
            else:
                logger.error(f"✗ ThemeManager.{method_name} does not exist or is not callable")

        # Now test PreferencesDialog
        try:
            from app.ui.preferences_dialog import PreferencesDialog

            # Create the dialog (without showing it)
            dialog = PreferencesDialog()
            logger.info("PreferencesDialog created successfully")

            # Check theme combo
            if hasattr(dialog, "theme_combo"):
                themes_count = dialog.theme_combo.count()
                logger.info(f"Theme combo contains {themes_count} items")

                # List all themes in combo
                theme_list = []
                for i in range(themes_count):
                    theme_text = dialog.theme_combo.itemText(i)
                    theme_data = dialog.theme_combo.itemData(i)
                    theme_list.append(f"{theme_text} (data: {theme_data})")

                logger.info(f"Themes in combo: {theme_list}")
            else:
                logger.error("theme_combo does not exist in PreferencesDialog")

            # Check language combo
            if hasattr(dialog, "language_combo"):
                langs_count = dialog.language_combo.count()
                logger.info(f"Language combo contains {langs_count} items")

                # List all languages in combo
                lang_list = []
                for i in range(langs_count):
                    lang_text = dialog.language_combo.itemText(i)
                    lang_data = dialog.language_combo.itemData(i)
                    lang_list.append(f"{lang_text} (data: {lang_data})")

                logger.info(f"Languages in combo: {lang_list}")
            else:
                logger.error("language_combo does not exist in PreferencesDialog")

        except ImportError as e:
            logger.error(f"Could not import PreferencesDialog: {e}")
        except Exception as e:
            logger.error(f"Error creating PreferencesDialog: {e}")
            import traceback
            logger.error(traceback.format_exc())

    except ImportError as e:
        logger.error(f"Could not import ThemeManager: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    debug_preferences_dialog()
    sys.exit(0)  # Exit without starting the event loop
