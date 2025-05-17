# ui/docks.py
from PySide6.QtWidgets import QDockWidget, QMainWindow, QWidget
from PySide6.QtCore import Qt
from .project_explorer import ProjectExplorer
from .widgets import ChatWidget, TerminalWidget
# Removed CodingAgentDialog import as it will be handled separately
from ..logic.event_handlers import on_dock_visibility_changed # Import the handler
from app.ui.i18n.translator import tr
from .dock_title_bar import apply_custom_title_bar
import logging
from .browser_widget import get_browser_widget  # Импорт функции для создания браузера

logger = logging.getLogger(__name__)

def create_docks(main_window: QMainWindow):
    """Создает боковые панели (dock-виджеты) приложения."""
    try:
        # Проводник проекта
        main_window.project_explorer_dock = QDockWidget(
            tr("dock.project_explorer", "Проводник проекта"), main_window
        )
        main_window.project_explorer_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.project_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        main_window.project_explorer_dock.setMinimumWidth(100)
        main_window.project_explorer_dock.setObjectName("ProjectExplorerDock")
        # main_window.project_explorer_dock.visibilityChanged.connect(main_window._on_dock_visibility_changed) # Будет подключено в main_window
        main_window.project_explorer = ProjectExplorer(main_window.icon_manager, main_window) # Передаем icon_manager
        main_window.project_explorer_dock.setWidget(main_window.project_explorer)
        main_window.addDockWidget(Qt.LeftDockWidgetArea, main_window.project_explorer_dock)
        apply_custom_title_bar(main_window.project_explorer_dock, main_window.icon_manager, is_docked_permanent=True) # Передаем icon_manager
        # Connect to the event handler, ensuring main_window context is passed correctly
        from ..logic.event_handlers import on_file_double_clicked as eh_on_file_double_clicked
        main_window.project_explorer.file_double_clicked.connect(lambda file_path: eh_on_file_double_clicked(main_window, file_path))

        # Чат
        main_window.chat_dock = QDockWidget(tr("dock.chat", "ИИ-чат"), main_window)
        main_window.chat_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        main_window.chat_dock.setMinimumWidth(200)
        main_window.chat_dock.setObjectName("ChatDock")
        main_window.chat_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "chat", visible))
        main_window.chat_widget = ChatWidget(main_window)
        main_window.chat_dock.setWidget(main_window.chat_widget)
        main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.chat_dock)
        apply_custom_title_bar(main_window.chat_dock, main_window.icon_manager, is_docked_permanent=True)

        # Connect chat_widget's message_sent signal to the new handler
        from app.logic.agent_setup import handle_user_message
        try:
            if hasattr(main_window.chat_widget, "message_sent"):
                main_window.chat_widget.message_sent.connect(lambda msg: handle_user_message(main_window, msg))
                logger.info("Connected chat widget message_sent signal to handle_user_message")
            else:
                logger.warning("Chat widget does not have message_sent signal")
        except Exception as e:
            logger.error(f"Error connecting chat widget message_sent signal: {str(e)}")

        # Подключаем сигналы для передачи кода между редактором и чатом
        if hasattr(main_window, "coding_agent_dialog") and main_window.coding_agent_dialog is not None:
            # Подключаем сигналы, если диалог уже создан
            _connect_editor_chat_signals(main_window)
        else:
            # Сохраняем функцию для подключения сигналов при создании диалога
            main_window._connect_editor_chat_signals = _connect_editor_chat_signals

        # Coding Agent is now handled separately as a standalone window
        # and not as a dock anymore

        # Терминал
        main_window.terminal_dock = QDockWidget(tr("dock.terminal", "Терминал"), main_window)
        main_window.terminal_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        main_window.terminal_dock.setMinimumHeight(100)
        main_window.terminal_dock.setObjectName("TerminalDock")
        main_window.terminal_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "terminal", visible))
        main_window.terminal_widget = TerminalWidget(main_window)
        main_window.terminal_dock.setWidget(main_window.terminal_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, main_window.terminal_dock)
        apply_custom_title_bar(main_window.terminal_dock, main_window.icon_manager, is_docked_permanent=True) # Передаем icon_manager
        main_window.terminal_dock.hide()

        # Браузер
        logger.info("Creating browser dock")
        main_window.browser_dock = QDockWidget(tr("dock.browser", "Браузер"), main_window)
        main_window.browser_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.browser_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        main_window.browser_dock.setMinimumWidth(250)
        main_window.browser_dock.setMinimumHeight(200)
        main_window.browser_dock.setObjectName("BrowserDock")
        main_window.browser_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "browser", visible))

        # Создаем веб-браузер и устанавливаем его в док
        # ВАЖНО: Добавляем web_view как атрибут browser_dock для совместимости
        # с существующими методами в MainWindow (_toggle_browser и др.)
        web_view = get_browser_widget(main_window)
        main_window.browser_dock.web_view = web_view  # Важно: делаем web_view атрибутом browser_dock
        main_window.browser_dock.setWidget(web_view)

        # Добавляем док в правую область, но не показываем его сразу
        main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.browser_dock)
        apply_custom_title_bar(main_window.browser_dock, main_window.icon_manager, is_docked_permanent=False)
        main_window.browser_dock.hide()
        logger.info("Browser dock created successfully")

    except Exception as e:
        logger.error(f"Error creating docks: {e}")

def _connect_editor_chat_signals(main_window):
    """
    Подключает сигналы для взаимодействия между редактором кода и чатом.

    Args:
        main_window: Экземпляр MainWindow
    """
    try:
        logger.info("Connecting editor and chat signals")

        # Получаем виджеты
        chat_widget = main_window.chat_widget

        # Проверяем, существует ли редактор кода
        if hasattr(main_window, "coding_agent_dialog") and main_window.coding_agent_dialog is not None:
            if hasattr(main_window.coding_agent_dialog, "editor_widget"):
                editor_widget = main_window.coding_agent_dialog.editor_widget

                # Соединяем сигналы от чата к редактору
                if hasattr(chat_widget, "insert_code_to_editor") and hasattr(editor_widget, "insert_code"):
                    try:
                        chat_widget.insert_code_to_editor.connect(editor_widget.insert_code)
                        logger.info("Connected chat insert_code_to_editor signal to editor insert_code")
                    except Exception as e:
                        logger.error(f"Error connecting chat insert_code_to_editor: {str(e)}")

                # Соединяем сигналы от редактора к чату
                if hasattr(editor_widget, "send_to_chat") and hasattr(chat_widget, "add_message"):
                    try:
                        editor_widget.send_to_chat.connect(lambda code: chat_widget.add_message("Editor", code))
                        logger.info("Connected editor send_to_chat signal to chat add_message")
                    except Exception as e:
                        logger.error(f"Error connecting editor send_to_chat: {str(e)}")

                logger.info("Editor and chat signals connected successfully")
            else:
                logger.warning("Editor widget not found in coding_agent_dialog")

        # Соединяем сигналы от чата к терминалу
        if hasattr(main_window, "terminal_widget"):
            terminal_widget = main_window.terminal_widget

            if hasattr(chat_widget, "run_code_in_terminal") and hasattr(terminal_widget, "execute_command"):
                try:
                    chat_widget.run_code_in_terminal.connect(terminal_widget.execute_command)
                    logger.info("Connected chat run_code_in_terminal signal to terminal execute_command")
                except Exception as e:
                    logger.error(f"Error connecting chat run_code_in_terminal: {str(e)}")
            else:
                if not hasattr(chat_widget, "run_code_in_terminal"):
                    logger.warning("Chat widget does not have run_code_in_terminal signal")
                if not hasattr(terminal_widget, "execute_command"):
                    logger.warning("Terminal widget does not have execute_command method")
        else:
            logger.warning("Terminal widget not found")

    except Exception as e:
        logger.error(f"Error connecting editor and chat signals: {e}")
