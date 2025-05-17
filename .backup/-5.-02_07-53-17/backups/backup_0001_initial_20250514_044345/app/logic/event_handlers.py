# logic/event_handlers.py
import logging
import os

from PySide6.QtCore import QFileInfo, Qt  # Added Qt
from PySide6.QtWidgets import QMessageBox  # Added QMessageBox

from app.ui.i18n.translator import tr  # Added tr

# Инициализация логгера
logger = logging.getLogger(__name__)


def on_file_double_clicked(main_window, file_path):
    if not os.path.isfile(file_path):
        # Optionally, show a message to the user or log this
        QMessageBox.warning(
            main_window, "File Not Found", f"The file {file_path} does not exist."
        )
        return
    logger.info(f"Открываем файл: {file_path}")  # Changed print to logger.info
    # Actual file opening logic should be called here, e.g., main_window._open_file(file_path)
    if hasattr(main_window, "_open_file"):
        main_window._open_file(file_path)
    else:
        logger.warning("MainWindow does not have _open_file method.")


def on_tab_changed(main_window, index):
    if index != -1:
        tab_widget = main_window.central_tabs.widget(index)
        if hasattr(tab_widget, "file_path") and tab_widget.file_path:
            file_name = os.path.basename(tab_widget.file_path)
            # Assuming APP_NAME is defined globally or accessible, otherwise pass it or define it
            # For now, using a placeholder.
            APP_NAME = tr("app.title", "GopiAI")  # Placeholder
            main_window.setWindowTitle(f"{file_name} - {APP_NAME}")
        else:
            main_window.setWindowTitle(tr("app.title", "GopiAI"))  # Placeholder
    if hasattr(main_window, "_update_tab_status"):
        main_window._update_tab_status(index)


def on_project_tree_double_clicked(main_window, index):
    try:
        if not hasattr(main_window, "project_explorer"):
            return

        # Исправлено: используем fs_model вместо tree_model
        if hasattr(main_window.project_explorer, "fs_model"):
            file_path = main_window.project_explorer.fs_model.filePath(index)
        else:
            logger.error("ProjectExplorer doesn't have fs_model attribute")
            return

        if not file_path:
            return

        file_info = QFileInfo(file_path)
        if file_info.isDir():
            main_window.project_explorer.tree_view.setExpanded(
                index, not main_window.project_explorer.tree_view.isExpanded(index)
            )
        else:
            if hasattr(main_window, "_open_file"):
                main_window._open_file(file_path)
            else:
                logger.warning(
                    "MainWindow does not have _open_file method for project tree."
                )
    except Exception as e:
        logger.error(
            f"Error handling project tree double click: {str(e)}"
        )  # Changed print to logger.error


def on_dock_visibility_changed(main_window, dock_name, visible):
    # Check if main_window and its relevant attributes/methods exist before calling
    if (
        main_window
        and hasattr(main_window, "_update_view_menu")
        and callable(main_window._update_view_menu)
    ):
        # Ensure that the dock widgets themselves are still valid Qt objects
        # This check might be better placed within _update_view_menu itself
        main_window._update_view_menu()
