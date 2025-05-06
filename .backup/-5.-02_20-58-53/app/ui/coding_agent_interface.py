import asyncio
from typing import Optional, Dict, Any, List

from PySide6.QtCore import QObject, Signal, Slot, QThread

from app.agent.coding_agent import CodingAgent
from app.schema import Message
from app.logger import logger


class CodingAgentWorker(QObject):
    """Рабочий поток для выполнения запросов к агенту кодирования."""

    # Сигналы
    message_received = Signal(str)
    error_occurred = Signal(str)
    thinking_state = Signal(bool)
    finished = Signal()

    def __init__(self, agent: CodingAgent):
        super().__init__()
        self.agent = agent
        self.running = False
        self.current_task = None

    @Slot(str)
    async def process_query(self, query: str):
        """Обрабатывает запрос пользователя асинхронно."""
        self.running = True
        self.thinking_state.emit(True)

        try:
            # Добавляем запрос пользователя в историю сообщений агента
            await self.agent.add_user_message(query)

            # Запускаем обработку агентом
            self.current_task = asyncio.create_task(self.agent.think())
            await self.current_task

            # Получаем все новые сообщения агента с момента последнего запроса
            messages = self.agent.get_agent_messages()

            # Отправляем каждое сообщение в интерфейс
            if messages:
                for message in messages:
                    self.message_received.emit(message.content)
            else:
                self.message_received.emit("Обработка запроса завершена, но агент не отправил ответ.")

        except asyncio.CancelledError:
            self.error_occurred.emit("Запрос был отменен.")
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            self.error_occurred.emit(f"Произошла ошибка при обработке запроса: {str(e)}")
        finally:
            self.running = False
            self.thinking_state.emit(False)
            self.finished.emit()

    def stop(self):
        """Останавливает текущую задачу, если она выполняется."""
        if self.running and self.current_task:
            self.current_task.cancel()


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

        # Создаем агента
        self.agent = CodingAgent()

        # Инициализируем рабочий поток
        self.thread = QThread()
        self.worker = CodingAgentWorker(self.agent)
        self.worker.moveToThread(self.thread)

        # Подключаем сигналы и слоты
        self.worker.message_received.connect(self.agent_message)
        self.worker.error_occurred.connect(self.agent_error)
        self.worker.thinking_state.connect(self.agent_thinking)
        self.worker.finished.connect(self.agent_finished)

        # Запускаем поток
        self.thread.start()

        # Ссылка на виджет редактора
        self.editor_widget = None

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
        # Создаем событие цикла
        loop = asyncio.get_event_loop()

        # Запускаем обработку запроса в отдельном потоке
        asyncio.run_coroutine_threadsafe(
            self.worker.process_query(query),
            loop
        )

    def stop_agent(self):
        """Останавливает выполнение текущего запроса агентом."""
        self.worker.stop()

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

    async def cleanup(self):
        """Очищает ресурсы перед закрытием интерфейса."""
        # Останавливаем текущую задачу, если она выполняется
        self.worker.stop()

        # Останавливаем поток
        self.thread.quit()
        self.thread.wait()

        # Выполняем очистку агента
        await self.agent.cleanup()
