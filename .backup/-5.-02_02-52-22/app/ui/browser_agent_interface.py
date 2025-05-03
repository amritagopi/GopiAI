import asyncio
from typing import Optional, Callable

from PySide6.QtCore import QObject, Signal, Slot

from app.agent.browser_agent import EnhancedBrowserAgent
from app.ui.browser_tab_widget import MultiBrowserWidget
from app.tool.browser_tools_integration import initialize_browser_tools


class BrowserAgentInterface(QObject):
    """
    Интерфейс для связи между UI браузера и браузерным агентом.
    Управляет запуском агента и передачей сообщений между UI и агентом.
    """

    # Сигналы для взаимодействия с UI
    agent_message = Signal(str)  # Сообщение от агента
    agent_error = Signal(str)  # Сообщение об ошибке
    agent_thinking = Signal(bool)  # Сигнал о том, что агент обрабатывает запрос
    agent_finished = Signal()  # Сигнал о завершении работы агента

    def __init__(self, parent=None):
        super(BrowserAgentInterface, self).__init__(parent)
        self.browser_widget: Optional[MultiBrowserWidget] = None
        self.agent: Optional[EnhancedBrowserAgent] = None
        self._running_task = None

    def set_browser_widget(self, browser_widget: MultiBrowserWidget):
        """
        Устанавливает виджет браузера и инициализирует инструменты для агента.

        Args:
            browser_widget: Виджет браузера из UI
        """
        self.browser_widget = browser_widget

        # Инициализируем инструменты
        initialize_browser_tools(browser_widget)

    def initialize_agent(self):
        """
        Инициализирует агента браузера.
        Вызывается после установки виджета браузера.
        """
        if not self.browser_widget:
            self.agent_error.emit("Ошибка: виджет браузера не установлен")
            return False

        try:
            self.agent = EnhancedBrowserAgent()
            return True
        except Exception as e:
            self.agent_error.emit(f"Ошибка инициализации агента: {str(e)}")
            return False

    @Slot(str)
    def process_user_query(self, query: str):
        """
        Обрабатывает запрос пользователя и запускает агента.

        Args:
            query: Запрос пользователя
        """
        if not self.agent:
            if not self.initialize_agent():
                return

        self.agent_thinking.emit(True)

        # Создаем и запускаем задачу
        self._running_task = asyncio.create_task(self._run_agent(query))

    async def _run_agent(self, query: str):
        """
        Запускает агента для обработки запроса пользователя.

        Args:
            query: Запрос пользователя
        """
        try:
            # Обновляем сообщения в агенте
            self.agent.messages = []

            # Добавляем сообщение пользователя
            await self.agent.add_user_message(query)

            # Запускаем агента
            result = await self.agent.run()

            # Отправляем результат в UI
            if result:
                self.agent_message.emit(result)
            else:
                self.agent_message.emit("Агент завершил работу без результата")

        except Exception as e:
            self.agent_error.emit(f"Ошибка при выполнении запроса: {str(e)}")
        finally:
            self.agent_thinking.emit(False)
            self.agent_finished.emit()

    @Slot()
    def stop_agent(self):
        """
        Останавливает работающего агента.
        """
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()
            self.agent_message.emit("Работа агента остановлена")
            self.agent_thinking.emit(False)
            self.agent_finished.emit()

    async def cleanup(self):
        """
        Очищает ресурсы агента перед закрытием приложения.
        """
        # Останавливаем текущую задачу, если она выполняется
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()

        # Очищаем ресурсы агента, если он был инициализирован
        if self.agent:
            # В будущем здесь можно добавить дополнительную логику очистки
            self.agent = None
