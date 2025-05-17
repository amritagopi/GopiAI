# ui/menus.py
from .menu_manager import MenuManager
import logging
from app.ui.i18n.translator import tr # Added import for tr
# from app.ui.icon_manager import get_icon # Удаляем, так как будем использовать main_window.icon_manager
from PySide6.QtGui import QAction # Added import for QAction
import os
import sys
from pathlib import Path
from PySide6.QtCore import QKeyCombination, Qt, QSettings
from PySide6.QtWidgets import QMenu, QApplication

# Добавляем путь к каталогу minimal_version для импорта color_harmony_dialog
minimal_version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "minimal_version")
if minimal_version_path not in sys.path:
    sys.path.append(minimal_version_path)

# Импортируем ColorHarmonyDialog (с обработкой возможной ошибки импорта)
try:
    from color_harmony_dialog import ColorHarmonyDialog
    has_color_harmony_dialog = True
except ImportError:
    has_color_harmony_dialog = False

logger = logging.getLogger(__name__)

def setup_menus(main_window):
    """Настраивает меню приложения."""
    try:
        logger.info("Начинаем настройку меню через setup_menus...")

        # Проверка на _create_menus
        if hasattr(main_window, '_create_menus'):
            logger.warning("Внимание: В MainWindow уже существует метод _create_menus, который может конфликтовать с setup_menus")

        # Проверка существования icon_manager
        if not hasattr(main_window, 'icon_manager'):
            logger.error("Ошибка: main_window.icon_manager отсутствует, необходим для создания MenuManager")
            return False

        logger.info(f"icon_manager найден: {main_window.icon_manager}")

        # Передаем icon_manager из main_window в MenuManager
        logger.info("Создаем MenuManager...")
        main_window.menu_manager = MenuManager(main_window, main_window.icon_manager)
        logger.info(f"MenuManager создан: {main_window.menu_manager}")

        logger.info("Устанавливаем menubar...")
        main_window.setMenuBar(main_window.menu_manager.menubar)
        main_window.tools_menu = main_window.menu_manager.tools_menu
        logger.info("Menubar установлен")

        # Копируем действия
        logger.info("Копируем действия из MenuManager в MainWindow...")
        main_window.new_file_action = main_window.menu_manager.new_file_action
        main_window.open_file_action = main_window.menu_manager.open_file_action
        main_window.save_file_action = main_window.menu_manager.save_file_action
        main_window.save_as_action = main_window.menu_manager.save_as_action
        main_window.exit_action = main_window.menu_manager.exit_action
        main_window.cut_action = main_window.menu_manager.cut_action
        main_window.copy_action = main_window.menu_manager.copy_action
        main_window.paste_action = main_window.menu_manager.paste_action
        main_window.undo_action = main_window.menu_manager.undo_action
        main_window.redo_action = main_window.menu_manager.redo_action
        main_window.select_all_action = main_window.menu_manager.select_all_action
        main_window.emoji_action = main_window.menu_manager.emoji_action
        main_window.toggle_terminal_action = main_window.menu_manager.toggle_terminal_action
        main_window.toggle_project_explorer_action = main_window.menu_manager.toggle_project_explorer_action
        main_window.toggle_chat_action = main_window.menu_manager.toggle_chat_action
        main_window.toggle_browser_action = main_window.menu_manager.toggle_browser_action
        main_window.toggle_coding_agent_action = main_window.menu_manager.toggle_coding_agent_action
        main_window.reset_layout_action = main_window.menu_manager.reset_layout_action
        main_window.open_url_action = main_window.menu_manager.open_url_action
        main_window.configure_agent_action = main_window.menu_manager.configure_agent_action
        main_window.view_flow_action = main_window.menu_manager.view_flow_action
        main_window.preferences_action = main_window.menu_manager.preferences_action
        main_window.about_action = main_window.menu_manager.about_action
        main_window.documentation_action = main_window.menu_manager.documentation_action
        logger.info("Действия скопированы")

        # Диагностика UI
        logger.info("Настраиваем действие диагностики UI...")
        if hasattr(main_window.menu_manager, "run_ui_diagnostics_action"):
            main_window.run_diagnostics_action = main_window.menu_manager.run_ui_diagnostics_action
            logger.info("Использовано действие run_ui_diagnostics_action из MenuManager")
        else:
            logger.warning("run_ui_diagnostics_action не найден в MenuManager, создаем новое действие")
            main_window.run_diagnostics_action = QAction(
                main_window.icon_manager.get_icon("debug"), tr("menu.tools.run_diagnostics", "Run UI Diagnostics"), main_window
            )
            main_window.run_diagnostics_action.setStatusTip(
                tr("menu.tools.run_diagnostics.tooltip", "Test and diagnose UI components")
            )
            # Assuming _run_ui_diagnostics is a method in MainWindow
            if hasattr(main_window, "_run_ui_diagnostics"):
                 main_window.run_diagnostics_action.triggered.connect(main_window._run_ui_diagnostics)
                 logger.info("Действие подключено к _run_ui_diagnostics")
            else:
                 logger.warning("Метод _run_ui_diagnostics не найден в MainWindow")

        # Connect to the event handler in theme_utils
        logger.info("Подключаем сигналы MenuManager...")
        try:
            from ..utils.theme_utils import on_theme_changed_event
            main_window.menu_manager.theme_changed.connect(lambda theme_name: on_theme_changed_event(main_window, theme_name))
            logger.info("Сигнал theme_changed подключен к on_theme_changed_event")
        except Exception as e:
            logger.error(f"Ошибка при подключении сигнала theme_changed: {e}")

        # Connect to the event handler in translation.py
        try:
            from ..utils.translation import on_language_changed_event as translation_on_language_changed_event
            main_window.menu_manager.language_changed.connect(lambda lang_code: translation_on_language_changed_event(main_window, lang_code))
            logger.info("Сигнал language_changed подключен к on_language_changed_event")
        except Exception as e:
            logger.error(f"Ошибка при подключении сигнала language_changed: {e}")

        # Примечание: не добавляем дополнительные подключения сигналов здесь,
        # так как все подключения уже выполнены в MenuManager.connect_signals

        logger.info("Проверяем, есть ли run_diagnostics_action в tools_menu...")
        if hasattr(main_window, "run_diagnostics_action") and main_window.tools_menu:
            already_added = False
            for action in main_window.tools_menu.actions():
                if action == main_window.run_diagnostics_action:
                    already_added = True
                    break
            if not already_added:
                main_window.tools_menu.addSeparator()
                main_window.tools_menu.addAction(main_window.run_diagnostics_action)
                logger.info("run_diagnostics_action добавлен в tools_menu")
            else:
                logger.info("run_diagnostics_action уже присутствует в tools_menu")
        else:
            logger.warning("run_diagnostics_action или tools_menu отсутствуют, не добавляем действие")

        # Настраиваем меню справки, если есть соответствующий метод
        if hasattr(main_window, '_setup_help_menu'):
            logger.info("Настраиваем меню справки через _setup_help_menu...")
            main_window._setup_help_menu(main_window.menu_manager.menubar)
            logger.info("Меню справки успешно настроено")
        else:
            logger.warning("Метод _setup_help_menu не найден в MainWindow, пропускаем настройку меню справки")

        # Файл
        main_window.file_menu = main_window.menuBar().addMenu(tr("menu.file", "Файл"))
        main_window.file_menu.setObjectName("fileMenu")

        # Вид
        main_window.view_menu = main_window.menuBar().addMenu(tr("menu.view", "Вид"))
        main_window.view_menu.setObjectName("viewMenu")

        # Добавляем пункт меню для настройки цветовой гармонии
        if has_color_harmony_dialog:
            color_harmony_action = QAction(tr("menu.view.color_harmony", "Цветовая гармония"), main_window)
            color_harmony_action.setStatusTip(tr("menu.view.color_harmony.status", "Открыть диалог настройки цветовой гармонии"))
            color_harmony_action.triggered.connect(main_window.open_color_harmony_dialog)
            main_window.view_menu.addAction(color_harmony_action)

        # Добавляем пункт меню настройки темы
        themes_action = QAction(tr("menu.view.theme_settings", "Настройки темы"), main_window)
        themes_action.setStatusTip(
            tr("menu.view.theme_settings.status", "Открыть диалог настройки темы")
        )
        themes_action.triggered.connect(main_window.open_theme_settings)
        main_window.view_menu.addAction(themes_action)

        # Настройки
        main_window.settings_menu = main_window.menuBar().addMenu(tr("menu.settings", "Настройки"))
        main_window.settings_menu.setObjectName("settingsMenu")

        # Справка
        main_window.help_menu = main_window.menuBar().addMenu(tr("menu.help", "Справка"))
        main_window.help_menu.setObjectName("helpMenu")

        logger.info("Меню успешно настроено через setup_menus")
        return True
    except Exception as e:
        logger.error(f"Ошибка при настройке меню: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
