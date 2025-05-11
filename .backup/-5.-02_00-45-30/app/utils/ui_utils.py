# utils/ui_utils.py
from PySide6.QtWidgets import QDockWidget
from PySide6.QtCore import Qt # Added Qt
from app.ui.dock_title_bar import apply_custom_title_bar # Corrected import path assuming dock_title_bar is in app/ui
import logging

logger = logging.getLogger(__name__)

def load_fonts(main_window): # Added main_window parameter
    """Загружаем современные шрифты для приложения."""
    # This function was originally in MainWindow, moved here
    # Ensure QFontDatabase and QFont are imported if not already
    # For now, assuming they are available or will be imported where this is called
    # from PySide6.QtGui import QFontDatabase, QFont
    # from PySide6.QtWidgets import QApplication
    import os # Already imported but good to note dependency
    try:
        font_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), # Adjust path if necessary
             "assets", "fonts"
        )
        os.makedirs(font_dir, exist_ok=True)
        inter_file = os.path.join(font_dir, "Inter", "Inter-Regular.ttf")
        # jet_brains_file = os.path.join(font_dir, "JetBrainsMono-Regular.ttf") # Шрифт не найден, используем Inter
        font_loaded = False
        from PySide6.QtGui import QFontDatabase, QFont
        from PySide6.QtWidgets import QApplication

        font_id = QFontDatabase.addApplicationFont(inter_file)
        if font_id != -1:
            font_loaded = True
        # font_id = QFontDatabase.addApplicationFont(jet_brains_file) # Шрифт не найден
        # if font_id != -1:
        #     font_loaded = True
        default_font = QFont("Inter", 10)
        QApplication.setFont(default_font)
        if not font_loaded:
            logger.warning("Custom font 'Inter' not found. Using system fonts.")
        else:
            logger.info("Custom font 'Inter' applied.")
    except Exception as e:
        logger.error(f"Error loading fonts: {e}")


def validate_ui_components(main_window):
    if not hasattr(main_window, "central_tabs") or main_window.central_tabs is None:
        logger.warning("Центральный виджет отсутствует, создаем заново")
        from app.ui.central_widget import setup_central_widget # Corrected import path
        setup_central_widget(main_window)
    # Assuming browser_dock might not always be present as per previous logic
    for dock_name in ["project_explorer_dock", "chat_dock", "terminal_dock"]: # Removed browser_dock for now
        if not hasattr(main_window, dock_name) or getattr(main_window, dock_name) is None:
            logger.warning(f"Док-виджет {dock_name} отсутствует, восстанавливаем доки")
            from app.ui.docks import create_docks # Corrected import path
            create_docks(main_window) # create_docks теперь должен сам получить icon_manager из main_window
            break
    update_custom_title_bars(main_window, main_window.icon_manager) # Передаем icon_manager
    if hasattr(main_window, 'retranslateUi'): # Check if method exists
        main_window.retranslateUi()

def apply_dock_constraints(main_window):
    try:
        if hasattr(main_window, "project_explorer_dock"):
            main_window.project_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        if hasattr(main_window, "chat_dock"):
            main_window.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        if hasattr(main_window, "terminal_dock"):
            main_window.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        if hasattr(main_window, "browser_dock"): # Keep if browser_dock is intended
            main_window.browser_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        update_custom_title_bars(main_window, main_window.icon_manager) # Передаем icon_manager
    except Exception as e:
        logger.error(f"Error applying dock constraints: {str(e)}")

def update_custom_title_bars(main_window, icon_manager): # Добавлен icon_manager
    try:
        if hasattr(main_window, "project_explorer_dock"):
            apply_custom_title_bar(main_window.project_explorer_dock, icon_manager, is_docked_permanent=True)
        if hasattr(main_window, "chat_dock"):
            apply_custom_title_bar(main_window.chat_dock, icon_manager, is_docked_permanent=True)
        if hasattr(main_window, "terminal_dock"):
            apply_custom_title_bar(main_window.terminal_dock, icon_manager, is_docked_permanent=False)
        if hasattr(main_window, "browser_dock"): # Keep if browser_dock is intended
            apply_custom_title_bar(main_window.browser_dock, icon_manager, is_docked_permanent=False)
    except Exception as e:
        logger.error(f"Error updating custom title bars: {str(e)}")

def fix_duplicate_docks(main_window):
    try:
        docks = main_window.findChildren(QDockWidget)
        dock_names = {}
        duplicates = []
        for dock in docks:
            name = dock.objectName()
            if name in dock_names:
                duplicates.append(dock)
            else:
                dock_names[name] = dock
        for duplicate in duplicates:
            duplicate.setVisible(False)
            duplicate.deleteLater()
        logger.info(f"Проверка дублирования доков: найдено {len(duplicates)} дубликатов")
    except Exception as e:
        logger.error(f"Ошибка при проверке дублирования доков: {str(e)}")
