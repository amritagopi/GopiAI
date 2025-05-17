"""
Модуль для интеграции агентов с пользовательским интерфейсом.

Этот модуль обеспечивает централизованное подключение различных типов агентов
к соответствующим компонентам пользовательского интерфейса.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Signal, QObject

from app.agent.agent_manager import AgentManager
from app.logic.agent_controller import AgentController

# Константы идентификаторов компонентов для использования в других модулях
MAIN_CHAT_COMPONENT_ID = "main_chat"
CODING_AGENT_COMPONENT_ID = "coding_agent"
BROWSER_COMPONENT_ID = "browser_agent"

logger = logging.getLogger(__name__)


def integrate_all_agents(main_window: QMainWindow) -> bool:
    """
    Интегрирует все типы агентов с соответствующими компонентами интерфейса.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        True, если интеграция прошла успешно, False в противном случае
    """
    try:
        logger.info("Starting integration of all agents with UI components")

        # Убеждаемся, что контроллер агентов доступен
        if not hasattr(main_window, "agent_controller"):
            main_window.agent_controller = AgentController.instance()

        # Интегрируем различные типы агентов
        success = (
            integrate_main_chat_agent(main_window) and
            integrate_coding_agent(main_window) and
            integrate_browser_agent(main_window)
        )

        if success:
            logger.info("Successfully integrated all agents with UI components")
        else:
            logger.warning("Some agent integrations failed, see previous logs for details")

        return success
    except Exception as e:
        logger.error(f"Error integrating agents with UI: {str(e)}")
        return False


def integrate_main_chat_agent(main_window: QMainWindow) -> bool:
    """
    Интегрирует основного чат-агента с интерфейсом.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        True, если интеграция прошла успешно, False в противном случае
    """
    try:
        logger.info("Integrating main chat agent with UI")

        # Убеждаемся, что у нас есть виджет чата
        if not hasattr(main_window, "chat_widget") or not main_window.chat_widget:
            logger.error("Chat widget not available for main chat agent integration")
            return False

        # Получаем контроллер агентов
        agent_controller = main_window.agent_controller

        # Подключаем сигналы чата к действиям агента
        main_window.chat_widget.message_sent.connect(
            lambda message: agent_controller.process_query(MAIN_CHAT_COMPONENT_ID, message)
        )

        # Если у чат-виджета есть сигналы для вставки кода и запуска кода, подключаем их к редактору
        if hasattr(main_window, "editor_widget") and main_window.editor_widget:
            if hasattr(main_window.chat_widget, "insert_code_to_editor"):
                main_window.chat_widget.insert_code_to_editor.connect(
                    main_window.editor_widget.insert_code
                )
                logger.info("Connected chat insert_code_to_editor signal to editor")

            if hasattr(main_window.chat_widget, "run_code_in_terminal"):
                if hasattr(main_window, "terminal_widget") and main_window.terminal_widget:
                    main_window.chat_widget.run_code_in_terminal.connect(
                        main_window.terminal_widget.execute_command
                    )
                    logger.info("Connected chat run_code_in_terminal signal to terminal")

        logger.info("Main chat agent integration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error integrating main chat agent: {str(e)}")
        return False


def integrate_coding_agent(main_window: QMainWindow) -> bool:
    """
    Интегрирует агента кодирования с интерфейсом.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        True, если интеграция прошла успешно, False в противном случае
    """
    try:
        logger.info("Integrating coding agent with UI")

        # Проверяем наличие диалога агента кодирования
        if not hasattr(main_window, "coding_agent_dialog") or not main_window.coding_agent_dialog:
            logger.info("Coding agent dialog not available, will be created when needed")
            return True

        # Получаем интерфейс агента кодирования
        if hasattr(main_window.coding_agent_dialog, "agent_interface"):
            agent_interface = main_window.coding_agent_dialog.agent_interface

            # Убеждаемся, что у интерфейса агента кодирования есть редактор кода
            if hasattr(main_window.coding_agent_dialog, "editor_widget"):
                agent_interface.set_editor_widget(main_window.coding_agent_dialog.editor_widget)
                logger.info("Connected coding agent interface to editor widget")

            # Подключаем сигналы чата в диалоге к агенту
            if hasattr(main_window.coding_agent_dialog, "chat_widget"):
                chat_widget = main_window.coding_agent_dialog.chat_widget

                # Подключаем отправку сообщений чата к агенту кодирования
                if hasattr(chat_widget, "message_sent"):
                    chat_widget.message_sent.connect(
                        lambda message: agent_interface.send_message(message)
                    )
                    logger.info("Connected coding agent chat widget to agent interface")

        logger.info("Coding agent integration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error integrating coding agent: {str(e)}")
        return False


def integrate_browser_agent(main_window: QMainWindow) -> bool:
    """
    Интегрирует браузерного агента с пользовательским интерфейсом.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        True, если интеграция прошла успешно, False в противном случае
    """
    try:
        logger.info("Integrating browser agent with UI")

        # Проверяем, что у нас есть новая реализация браузерного агента в центральных вкладках
        has_browser_tab = False
        if hasattr(main_window, "central_tabs") and hasattr(main_window, "browser_tab_index"):
            if main_window.browser_tab_index >= 0 and main_window.browser_tab_index < main_window.central_tabs.count():
                widget = main_window.central_tabs.widget(main_window.browser_tab_index)
                if hasattr(widget, "is_browser_tab") and widget.is_browser_tab:
                    has_browser_tab = True
                    logger.info("Found integrated browser tab")

        # Проверяем наличие интерфейса агента
        has_agent_interface = hasattr(main_window, "browser_agent_interface")

        if has_browser_tab and has_agent_interface:
            logger.info("Browser agent tab already integrated")
            return True

        # Если вкладка не создана, создавать её здесь не будем
        # Она будет создана при нажатии на кнопку browserAgentButton

        logger.info("Browser agent integration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error integrating browser agent: {str(e)}")
        return False


def connect_editor_chat_signals(main_window: QMainWindow) -> bool:
    """
    Подключает сигналы между редактором кода и чатом.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        True, если подключение прошло успешно, False в противном случае
    """
    try:
        logger.info("Connecting editor and chat signals")

        # Получаем виджет чата
        if not hasattr(main_window, "chat_widget") or not main_window.chat_widget:
            logger.error("Chat widget not available for signal connection")
            return False

        chat_widget = main_window.chat_widget

        # Проверяем наличие редактора кода в основном окне
        if hasattr(main_window, "editor_widget") and main_window.editor_widget:
            editor_widget = main_window.editor_widget

            # Подключаем сигналы от чата к редактору
            if hasattr(chat_widget, "insert_code_to_editor"):
                chat_widget.insert_code_to_editor.connect(editor_widget.insert_code)
                logger.info("Connected chat insert_code_to_editor signal to main editor")

            # Подключаем сигналы от редактора к чату
            if hasattr(editor_widget, "send_to_chat"):
                editor_widget.send_to_chat.connect(
                    lambda code: chat_widget.add_message("Editor", code)
                )
                logger.info("Connected editor send_to_chat signal to chat")

        # Проверяем наличие редактора кода в диалоге агента кодирования
        elif hasattr(main_window, "coding_agent_dialog") and main_window.coding_agent_dialog:
            if hasattr(main_window.coding_agent_dialog, "editor_widget"):
                editor_widget = main_window.coding_agent_dialog.editor_widget

                # Подключаем сигналы от чата к редактору
                if hasattr(chat_widget, "insert_code_to_editor"):
                    chat_widget.insert_code_to_editor.connect(editor_widget.insert_code)
                    logger.info("Connected chat insert_code_to_editor signal to coding agent editor")

        # Соединяем сигналы от чата к терминалу
        if hasattr(main_window, "terminal_widget") and main_window.terminal_widget:
            terminal_widget = main_window.terminal_widget

            if hasattr(chat_widget, "run_code_in_terminal"):
                chat_widget.run_code_in_terminal.connect(terminal_widget.execute_command)
                logger.info("Connected chat run_code_in_terminal signal to terminal")

        return True
    except Exception as e:
        logger.error(f"Error connecting editor and chat signals: {str(e)}")
        return False


def update_integration_status(main_window: QMainWindow) -> Dict[str, bool]:
    """
    Проверяет и обновляет статус интеграции всех компонентов.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        Словарь с информацией о статусе интеграции различных компонентов
    """
    status = {
        "main_chat": False,
        "coding_agent": False,
        "browser_agent": False,
        "editor_chat": False
    }

    try:
        # Проверяем интеграцию основного чата
        if hasattr(main_window, "chat_widget") and main_window.chat_widget:
            if hasattr(main_window, "agent_controller"):
                status["main_chat"] = True

        # Проверяем интеграцию агента кодирования
        if hasattr(main_window, "coding_agent_dialog") and main_window.coding_agent_dialog:
            if hasattr(main_window.coding_agent_dialog, "agent_interface"):
                status["coding_agent"] = True

        # Проверяем интеграцию браузерного агента (новая реализация)
        if hasattr(main_window, "browser_agent_interface"):
            status["browser_agent"] = True
        # Проверяем вкладку браузера
        elif hasattr(main_window, "central_tabs") and hasattr(main_window, "browser_tab_index"):
            if main_window.browser_tab_index >= 0 and main_window.browser_tab_index < main_window.central_tabs.count():
                widget = main_window.central_tabs.widget(main_window.browser_tab_index)
                if hasattr(widget, "is_browser_tab") and widget.is_browser_tab:
                    status["browser_agent"] = True

        # Проверяем интеграцию редактора и чата
        if hasattr(main_window, "chat_widget") and main_window.chat_widget:
            if (
                (hasattr(main_window, "editor_widget") and main_window.editor_widget) or
                (hasattr(main_window, "coding_agent_dialog") and
                 main_window.coding_agent_dialog and
                 hasattr(main_window.coding_agent_dialog, "editor_widget"))
            ):
                status["editor_chat"] = True

    except Exception as e:
        logger.error(f"Error updating integration status: {str(e)}")

    return status


def fix_missing_signals(main_window: QMainWindow) -> Dict[str, List[str]]:
    """
    Проверяет наличие необходимых сигналов во всех компонентах и пытается исправить.

    Args:
        main_window: Экземпляр главного окна

    Returns:
        Словарь с информацией о добавленных сигналах по компонентам
    """
    fixes = {
        "chat_widget": [],
        "editor_widget": [],
        "terminal_widget": [],
        "coding_agent": [],
        "browser_agent": []
    }

    try:
        # Проверяем виджет чата
        if hasattr(main_window, "chat_widget") and main_window.chat_widget:
            chat_widget = main_window.chat_widget

            # Добавляем недостающие сигналы
            if not hasattr(chat_widget, "message_sent"):
                # Динамически добавляем сигнал
                setattr(chat_widget.__class__, "message_sent", Signal(str))
                chat_widget.message_sent = Signal(str)
                fixes["chat_widget"].append("message_sent")

            if not hasattr(chat_widget, "insert_code_to_editor"):
                setattr(chat_widget.__class__, "insert_code_to_editor", Signal(str))
                chat_widget.insert_code_to_editor = Signal(str)
                fixes["chat_widget"].append("insert_code_to_editor")

            if not hasattr(chat_widget, "run_code_in_terminal"):
                setattr(chat_widget.__class__, "run_code_in_terminal", Signal(str))
                chat_widget.run_code_in_terminal = Signal(str)
                fixes["chat_widget"].append("run_code_in_terminal")

            # Проверяем наличие метода _extract_code_from_selection
            if not hasattr(chat_widget, "_extract_code_from_selection"):
                # Импортируем в локальной области видимости, чтобы не создавать зависимость на уровне модуля
                import re

                def extract_code_from_selection(self, text: str) -> str:
                    """Извлекает код из выделенного текста."""
                    markdown_code_match = re.search(r'```(?:\w*\n)?([\s\S]*?)```', text)
                    if markdown_code_match:
                        return markdown_code_match.group(1)
                    return text

                # Добавляем метод в класс
                setattr(chat_widget.__class__, "_extract_code_from_selection", extract_code_from_selection)
                fixes["chat_widget"].append("_extract_code_from_selection (method)")

        # Проверяем виджет редактора
        if hasattr(main_window, "editor_widget") and main_window.editor_widget:
            editor_widget = main_window.editor_widget

            # Добавляем недостающие сигналы
            if not hasattr(editor_widget, "send_to_chat"):
                setattr(editor_widget.__class__, "send_to_chat", Signal(str))
                editor_widget.send_to_chat = Signal(str)
                fixes["editor_widget"].append("send_to_chat")

            if not hasattr(editor_widget, "code_check_requested"):
                setattr(editor_widget.__class__, "code_check_requested", Signal(str))
                editor_widget.code_check_requested = Signal(str)
                fixes["editor_widget"].append("code_check_requested")

            if not hasattr(editor_widget, "code_run_requested"):
                setattr(editor_widget.__class__, "code_run_requested", Signal(str))
                editor_widget.code_run_requested = Signal(str)
                fixes["editor_widget"].append("code_run_requested")

            # Проверяем наличие метода insert_code
            if not hasattr(editor_widget, "insert_code"):
                def insert_code(self, code: str):
                    """Вставляет код в текущий редактор."""
                    if hasattr(self, "tabs") and self.tabs.count() > 0:
                        current_editor = self.tabs.currentWidget()
                        if current_editor:
                            cursor = current_editor.textCursor()
                            cursor.insertText(code)
                            current_editor.setTextCursor(cursor)

                # Добавляем метод в класс
                setattr(editor_widget.__class__, "insert_code", insert_code)
                fixes["editor_widget"].append("insert_code (method)")

        # Проверяем терминал
        if hasattr(main_window, "terminal_widget") and main_window.terminal_widget:
            terminal_widget = main_window.terminal_widget

            # Проверяем наличие метода execute_command
            if not hasattr(terminal_widget, "execute_command"):
                def execute_command(self, command: str):
                    """Выполняет команду в терминале."""
                    if hasattr(self, "process") and hasattr(self.process, "write"):
                        self.process.write(command.encode() + b"\n")

                # Добавляем метод в класс
                setattr(terminal_widget.__class__, "execute_command", execute_command)
                fixes["terminal_widget"].append("execute_command (method)")

        # Проверяем диалог агента кодирования
        if hasattr(main_window, "coding_agent_dialog") and main_window.coding_agent_dialog:
            dialog = main_window.coding_agent_dialog

            # Проверяем наличие интерфейса агента
            if not hasattr(dialog, "agent_interface"):
                logger.warning("Coding agent dialog has no agent_interface, skipping fixes")

            # Проверяем наличие виджета чата
            if hasattr(dialog, "chat_widget"):
                chat_widget = dialog.chat_widget

                # Добавляем недостающие сигналы
                if not hasattr(chat_widget, "message_sent"):
                    setattr(chat_widget.__class__, "message_sent", Signal(str))
                    chat_widget.message_sent = Signal(str)
                    fixes["coding_agent"].append("chat.message_sent")

        # Проверяем диалог браузерного агента
        if hasattr(main_window, "browser_agent_dialog") and main_window.browser_agent_dialog:
            dialog = main_window.browser_agent_dialog

            # Проверяем наличие интерфейса агента
            if not hasattr(dialog, "agent_interface"):
                logger.warning("Browser agent dialog has no agent_interface, skipping fixes")

            # Проверяем наличие виджета чата
            if hasattr(dialog, "chat_history"):
                chat_widget = dialog.chat_history

                # Добавляем недостающие сигналы
                if not hasattr(chat_widget, "message_sent"):
                    setattr(chat_widget.__class__, "message_sent", Signal(str))
                    chat_widget.message_sent = Signal(str)
                    fixes["browser_agent"].append("chat.message_sent")

                if not hasattr(chat_widget, "url_open_requested"):
                    setattr(chat_widget.__class__, "url_open_requested", Signal(str))
                    chat_widget.url_open_requested = Signal(str)
                    fixes["browser_agent"].append("chat.url_open_requested")

        # Логируем результаты
        for component, component_fixes in fixes.items():
            if component_fixes:
                logger.info(f"Fixed {len(component_fixes)} issues in {component}: {', '.join(component_fixes)}")

        return fixes
    except Exception as e:
        logger.error(f"Error fixing missing signals: {str(e)}")
        return fixes


def save_integration_status_to_serena(main_window: QMainWindow, status: Dict[str, bool]) -> bool:
    """
    Сохраняет статус интеграции в памяти Serena.

    Args:
        main_window: Экземпляр главного окна
        status: Статус интеграции различных компонентов

    Returns:
        True, если сохранение прошло успешно, False в противном случае
    """
    try:
        if not hasattr(main_window, "agent_controller"):
            logger.warning("Agent controller not available for saving status to Serena")
            return False

        # Получаем клиент MCP из контроллера агентов
        agent_controller = main_window.agent_controller
        agent_manager = agent_controller.agent_manager

        if not hasattr(agent_manager, "mcp_client") or not agent_manager.mcp_client:
            logger.warning("MCP client not available for saving status to Serena")
            return False

        # Формируем данные для сохранения
        integration_data = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "fixes_applied": getattr(main_window, "_ui_fixes_applied", {}),
            "components": {
                "main_chat": hasattr(main_window, "chat_widget"),
                "editor": hasattr(main_window, "editor_widget"),
                "terminal": hasattr(main_window, "terminal_widget"),
                "coding_agent": hasattr(main_window, "coding_agent_dialog"),
                "browser_agent": hasattr(main_window, "browser_agent_dialog")
            }
        }

        # Преобразуем в JSON
        memory_content = json.dumps(integration_data, indent=2)

        # Проверяем доступность инструмента Serena
        mcp_client = agent_manager.mcp_client
        if not hasattr(mcp_client, "serena_write_memory"):
            logger.warning("Serena memory tools not available")
            return False

        # Асинхронно сохраняем в память Serena
        import asyncio

        async def save_memory():
            """Сохраняет данные в память Serena асинхронно."""
            try:
                # Сохраняем данные в память Serena
                result = await mcp_client.serena_write_memory(
                    "ui_integration_status.md",
                    f"# UI Integration Status\n\n"
                    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"## Status Summary\n\n"
                    f"| Component | Status |\n"
                    f"|-----------|--------|\n"
                    f"| Main Chat | {status.get('main_chat', False)} |\n"
                    f"| Coding Agent | {status.get('coding_agent', False)} |\n"
                    f"| Browser Agent | {status.get('browser_agent', False)} |\n"
                    f"| Editor-Chat | {status.get('editor_chat', False)} |\n\n"
                    f"## Technical Details\n\n"
                    f"```json\n{memory_content}\n```\n"
                )

                if result:
                    logger.info("Integration status saved to Serena successfully")
                    return True
                else:
                    logger.warning("Failed to save integration status to Serena")
                    return False
            except Exception as e:
                logger.error(f"Error saving to Serena: {str(e)}")
                return False

        # Запускаем сохранение в новом event loop
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(save_memory())
        loop.close()

        return result
    except Exception as e:
        logger.error(f"Error saving integration status to Serena: {str(e)}")
        return False
