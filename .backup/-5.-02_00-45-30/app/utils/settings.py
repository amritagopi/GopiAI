# utils/settings.py
from PySide6.QtWidgets import QApplication
import logging

logger = logging.getLogger(__name__)

def restore_window_state(main_window):
    try:
        geometry = main_window.settings.value("window/geometry")
        if geometry:
            main_window.restoreGeometry(geometry)
        else:
            main_window.resize(1280, 720)
            # Ensure QApplication instance is available for screen geometry
            app_instance = QApplication.instance()
            if app_instance:
                center_point = app_instance.primaryScreen().availableGeometry().center()
                frame_geometry = main_window.frameGeometry()
                frame_geometry.moveCenter(center_point)
                main_window.move(frame_geometry.topLeft())
            else:
                logger.warning("QApplication instance not found, cannot center window.")

        state = main_window.settings.value("window/state")
        if state:
            main_window.restoreState(state)
    except Exception as e:
        logger.error(f"Error restoring window state: {str(e)}")
        main_window.resize(1280, 720) # Fallback size
