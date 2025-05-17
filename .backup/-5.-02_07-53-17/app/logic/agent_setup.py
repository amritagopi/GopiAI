# logic/agent_setup.py
import logging

from PySide6.QtCore import QThread  # Added QThread import

from app.agent.agent_manager import AgentManager
from app.logic.agent_controller import AgentController  # Добавляем импорт
from app.ui.agent_ui_integration import (  # Импортируем константы из agent_ui_integration.py для предотвращения циклических импортов; Импорт новых функций и констант
    BROWSER_COMPONENT_ID,
    CODING_AGENT_COMPONENT_ID,
    MAIN_CHAT_COMPONENT_ID,
    connect_editor_chat_signals,
    integrate_all_agents,
)

logger = logging.getLogger(__name__)

# Константы теперь определены в app.ui.agent_ui_integration для предотвращения циклических импортов


# Agent-related handlers, moved from MainWindow
def handle_user_message(main_window, message: str):
    """Handles user messages sent to the agent."""
    logger.debug(f"User message to agent: {message}")

    # Используем AgentController вместо прямого доступа к worker
    agent_controller = AgentController.instance()
    agent_controller.process_query(MAIN_CHAT_COMPONENT_ID, message)


def handle_agent_response(main_window, response):
    """Handles responses received from the agent."""
    logger.debug(f"Agent response received: {response}")
    if hasattr(main_window, "chat_widget") and main_window.chat_widget:
        if isinstance(response, str):
            main_window.chat_widget.add_message("Assistant", response)
        else:
            logger.warning(
                f"Received non-string agent response: {type(response)}, content: {response}"
            )
    else:
        logger.warning("Chat widget not available to display agent response.")


def update_agent_status_display(main_window, status_message: str):
    """Updates the agent status display in the UI."""
    if hasattr(main_window, "agent_status_label") and main_window.agent_status_label:
        main_window.agent_status_label.setText(status_message)
    logger.info(f"Agent status updated: {status_message}")


def setup_agent(main_window):
    """Настраивает агента ИИ и возвращает его экземпляр."""
    logger.info("Initializing agent")
    try:
        # Используем AgentController вместо прямого создания агента
        agent_controller = AgentController.instance()

        # Регистрируем основной компонент чата
        component_id = agent_controller.register_component(
            MAIN_CHAT_COMPONENT_ID,
            agent_type="reactive",  # Используем ReactAgent вместо реализации по умолчанию
        )

        # Регистрируем обратные вызовы для обработки событий
        agent_controller.register_callback(
            component_id, "message", lambda msg: handle_agent_response(main_window, msg)
        )

        agent_controller.register_callback(
            component_id,
            "thinking",
            lambda thinking: update_agent_status_display(
                main_window, "Thinking... 🤔" if thinking else "Ready"
            ),
        )

        agent_controller.register_callback(
            component_id,
            "error",
            lambda err: update_agent_status_display(main_window, f"Error: {err} ❌"),
        )

        # Получаем агента для совместимости с существующим кодом
        agent = AgentManager.instance().get_active_agent(MAIN_CHAT_COMPONENT_ID)

        # Если агент не удалось получить, создаем его вручную
        if agent is None:
            logger.warning("No active agent found for main chat, creating manually")
            agent = AgentManager.instance().create_agent("reactive")
            AgentManager.instance().set_active_agent(MAIN_CHAT_COMPONENT_ID, agent)

        return agent
    except ImportError as e:
        logger.warning(f"Agent module not found: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}")
        return None


def connect_agent_signals(main_window):
    """Подключает сигналы агента к интерфейсу."""
    # Используем новую реализацию из agent_ui_integration.py
    logger.info("Connecting agent signals using agent_ui_integration")

    # Для совместимости с существующим кодом устанавливаем атрибуты main_window
    main_window.agent_controller = AgentController.instance()

    # Интегрируем всех агентов с UI компонентами
    integration_success = integrate_all_agents(main_window)

    # Подключаем сигналы между редактором и чатом
    editor_chat_connected = connect_editor_chat_signals(main_window)

    if integration_success and editor_chat_connected:
        logger.info("All agent signals connected successfully")
    else:
        logger.warning("Some agent signals could not be connected")

    return integration_success and editor_chat_connected
