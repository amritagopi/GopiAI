import asyncio
from typing import Optional, Dict, Any, List

from PySide6.QtCore import QObject, Signal, Slot, QThread

from app.agent.coding_agent import CodingAgent
from app.logic.agent_controller import AgentController
from app.ui.agent_ui_integration import CODING_AGENT_COMPONENT_ID
from app.schema import Message
from app.logger import logger


class CodingAgentInterface(QObject):
    """
    Интерфейс для взаимодействия с агентом кодирования.

    Обеспечивает связь между пользовательским интерфейсом и агентом кодирования,
    позволяя отправлять запросы и получать ответы от агента.
    """

    # Сигналы для обновления интерфейса
    agent_message = Signal(str)
    agent_error = Signal(str)
    agent_thinking = Signal(bool)
    agent_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Используем AgentController вместо прямого создания агента
        self.agent_controller = AgentController.instance()

        # Регистрируем компонент и получаем его идентификатор
        self.component_id = self.agent_controller.register_component(
            CODING_AGENT_COMPONENT_ID,
            agent_type="coding"
        )

        # Регистрируем обратные вызовы
        self._register_callbacks()

        # Ссылка на виджет редактора
        self.editor_widget = None

    def _register_callbacks(self):
        """Регистрирует обратные вызовы для обработки событий от агента."""
        # Регистрируем обработчики основных сигналов
        self.agent_controller.register_callback(
            self.component_id,
            "message",
            lambda msg: self.agent_message.emit(msg)
        )

        self.agent_controller.register_callback(
            self.component_id,
            "error",
            lambda err: self.agent_error.emit(err)
        )

        self.agent_controller.register_callback(
            self.component_id,
            "thinking",
            lambda thinking: self.agent_thinking.emit(thinking)
        )

        self.agent_controller.register_callback(
            self.component_id,
            "finished",
            lambda _: self.agent_finished.emit()
        )

        # Регистрируем обработчики для специфичных сигналов
        self.agent_controller.register_callback(
            self.component_id,
            "code_snippet",
            lambda code: self._handle_code_snippet(code)
        )

    def set_editor_widget(self, editor_widget):
        """Устанавливает виджет редактора, с которым будет взаимодействовать агент."""
        self.editor_widget = editor_widget

        # Подключаем сигналы от редактора
        if self.editor_widget:
            self.editor_widget.send_to_chat.connect(self.on_code_sent_to_chat)
            self.editor_widget.code_check_requested.connect(self.on_code_check_requested)
            self.editor_widget.code_run_requested.connect(self.on_code_run_requested)

    @Slot(str)
    def process_user_query(self, query: str):
        """
        Отправляет запрос пользователя агенту и обрабатывает ответ.

        Args:
            query: Текст запроса пользователя
        """
        # Используем AgentController для обработки запроса
        self.agent_controller.process_query(self.component_id, query)

    def stop_agent(self):
        """Останавливает выполнение текущего запроса агентом."""
        self.agent_controller.stop_query(self.component_id)

    @Slot(str)
    def on_code_sent_to_chat(self, code: str):
        """Обрабатывает отправку кода из редактора в чат."""
        formatted_message = f"```\n{code}\n```"

        # Запрашиваем анализ кода у агента
        query = f"Проанализируйте следующий код и предоставьте комментарии по его улучшению:\n{formatted_message}"
        self.process_user_query(query)

    @Slot(str)
    def on_code_check_requested(self, code: str):
        """Обрабатывает запрос на проверку кода."""
        formatted_message = f"```\n{code}\n```"

        # Запрашиваем проверку кода у агента
        query = f"Проверьте следующий код на наличие ошибок и предложите улучшения:\n{formatted_message}"
        self.process_user_query(query)

    @Slot(str)
    def on_code_run_requested(self, code: str):
        """Обрабатывает запрос на запуск кода."""
        formatted_message = f"```\n{code}\n```"

        # Запрашиваем запуск кода у агента
        query = f"Объясните, что делает этот код и как его можно выполнить:\n{formatted_message}"
        self.process_user_query(query)

    def _handle_code_snippet(self, code: str):
        """Обрабатывает получение фрагмента кода от агента."""
        # Если есть редактор, отправляем код в него
        if self.editor_widget and hasattr(self.editor_widget, "insert_code"):
            self.editor_widget.insert_code(code)

    async def cleanup(self):
        """Очищает ресурсы перед закрытием интерфейса."""
        # Отменяем регистрацию компонента
        self.agent_controller.unregister_component(self.component_id)
