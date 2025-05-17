# utils/translation.py
import logging

# Import QWidget and other necessary Qt classes if they are used in on_language_changed_event
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from app.ui.i18n.translator import JsonTranslationManager, tr

logger = logging.getLogger(__name__)


def translate(key, default_text=""):
    return tr(key, default_text)


def on_language_changed_event(main_window, language_code, skip_menu_update=False):
    try:
        logger.info(f"Получено событие смены языка на: {language_code}")
        main_window.setWindowTitle(tr("app.title", "GopiAI"))
        if hasattr(main_window, "menu_manager") and not skip_menu_update:
            logger.info("Обновляем переводы меню")
            if hasattr(main_window.menu_manager, "update_translations"):
                main_window.menu_manager.update_translations()
            else:
                logger.warning("Метод update_translations не найден в menu_manager")

        if hasattr(main_window, "_update_tab_titles"):  # Check if method exists
            main_window._update_tab_titles()

        for child in main_window.findChildren(QWidget):
            if hasattr(child, "windowTitle") and hasattr(child, "objectName"):
                obj_name = child.objectName()
                if obj_name and not obj_name.startswith(
                    "qt_"
                ):  # Avoid Qt internal widgets
                    # Construct a key based on object name, assuming a convention like "dock.objectName"
                    # This part might need adjustment based on how keys are actually structured
                    title_key = f"dock.{obj_name.replace('Dock', '').lower()}"  # Example key construction
                    if "project" in obj_name.lower():
                        title_key = "dock.project_explorer"
                    elif "chat" in obj_name.lower():
                        title_key = "dock.chat"
                    elif "terminal" in obj_name.lower():
                        title_key = "dock.terminal"
                    # Add more specific key mappings if needed

                    original_title = (
                        child.windowTitle()
                    )  # Get current title as default if key not found
                    translated_title = tr(title_key, original_title)
                    if translated_title != child.windowTitle():
                        child.setWindowTitle(translated_title)
                        logger.debug(
                            f"Обновлен заголовок {obj_name}: {translated_title}"
                        )

            if isinstance(child, QPushButton) and hasattr(child, "objectName"):
                obj_name = child.objectName()
                if obj_name and not obj_name.startswith("qt_"):
                    button_key = f"button.{obj_name.lower()}"  # Example key
                    original_text = child.text()
                    translated_text = tr(button_key, original_text)
                    if translated_text != child.text():
                        child.setText(translated_text)
                        logger.debug(
                            f"Обновлен текст кнопки {obj_name}: {translated_text}"
                        )

            if isinstance(child, QLabel) and hasattr(child, "objectName"):
                obj_name = child.objectName()
                if obj_name and not obj_name.startswith("qt_"):
                    # Specific handling for known labels
                    if obj_name == "status_label":
                        label_key = "status.ready"
                    elif obj_name == "file_info_label":
                        label_key = "status.file_info_default"  # Assuming a default key
                    elif obj_name == "agent_status_label":
                        label_key = "status.agent_default"  # Assuming a default key
                    else:
                        label_key = f"label.{obj_name.lower()}"  # Generic key

                    original_text = child.text()
                    translated_text = tr(
                        label_key, original_text if original_text else ""
                    )  # Provide default if empty
                    if translated_text != child.text():
                        child.setText(translated_text)
                        logger.debug(
                            f"Обновлен текст метки {obj_name}: {translated_text}"
                        )
        logger.info(f"Язык успешно изменен на {language_code}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении языка UI: {str(e)}")
        import traceback
