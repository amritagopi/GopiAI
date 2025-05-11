"""
Модуль, предоставляющий централизованное управление взаимодействием между UI и агентами.

Реализует паттерн Фасад для доступа к агентам из различных компонентов интерфейса.
"""

import asyncio
import threading
from typing import Dict, Optional, Any, Callable, List, Union
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, Signal, Slot, QThread

from app.agent.agent_manager import AgentManager
from app.agent.base import BaseAgent
from app.agent.coding_agent import CodingAgent
from app.schema import Message
from app.logger import logger


class AgentWorkerSignals(QObject):
    """Сигналы для взаимодействия с агентами."""

    # Сигналы для обновления UI
    message_received = Signal(str, str)  # компонент_id, сообщение
    error_occurred = Signal(str, str)  # компонент_id, сообщение об ошибке
    thinking_state = Signal(str, bool)  # компонент_id, состояние обдумывания
    finished = Signal(str)  # компонент_id

    # Сигналы для специфичных обновлений
    code_snippet_received = Signal(str, str)  # компонент_id, код
    web_content_received = Signal(str, str, str)  # компонент_id, url, содержимое
    tool_execution_started = Signal(str, str)  # компонент_id, название инструмента
    tool_execution_finished = Signal(str, str, bool)  # компонент_id, название инструмента, успех


class AgentWorker(QThread):
    """
    Рабочий поток для выполнения запросов к агентам.

    Обрабатывает запросы асинхронно и отправляет результаты через сигналы.
    """

    def __init__(self, agent: BaseAgent, component_id: str, signals: AgentWorkerSignals):
        super().__init__()
        self.agent = agent
        self.component_id = component_id
        self.signals = signals
        self.running = False
        self.query = None
        self.loop = None

    def run(self):
        """Выполняет задачу в отдельном потоке."""
        if not self.query:
            self.signals.error_occurred.emit(self.component_id, "No query specified")
            return

        self.running = True
        self.signals.thinking_state.emit(self.component_id, True)

        try:
            # Создаем event loop для асинхронного выполнения
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Обновляем память агента с запросом пользователя
            self.loop.run_until_complete(self._add_user_message(self.query))

            # Запускаем агента
            result = self.loop.run_until_complete(self.agent.process(self.query))

            # Отправляем результат
            self.signals.message_received.emit(self.component_id, result)
        except asyncio.CancelledError:
            self.signals.error_occurred.emit(self.component_id, "Task was cancelled")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            self.signals.error_occurred.emit(self.component_id, f"Error: {str(e)}")
        finally:
            self.running = False
            self.signals.thinking_state.emit(self.component_id, False)
            self.signals.finished.emit(self.component_id)

    async def _add_user_message(self, message: str):
        """Добавляет сообщение пользователя в память агента."""
        if hasattr(self.agent, "update_memory"):
            self.agent.update_memory("user", message)
        elif hasattr(self.agent, "add_user_message"):
            await self.agent.add_user_message(message)

    def stop(self):
        """Останавливает выполнение задачи."""
        if self.running and self.loop:
            self.loop.call_soon_threadsafe(lambda: self._cancel_tasks())

    def _cancel_tasks(self):
        """Отменяет все задачи в event loop."""
        for task in asyncio.all_tasks(self.loop):
            task.cancel()


class AgentController(QObject):
    """
    Контроллер для централизованного управления агентами.

    Предоставляет единый интерфейс для взаимодействия с различными типами агентов
    и маршрутизирует результаты обратно к компонентам интерфейса.
    """

    def __init__(self):
        super().__init__()
        self.agent_manager = AgentManager.instance()
        self.signals = AgentWorkerSignals()
        self.workers: Dict[str, AgentWorker] = {}
        self.worker_threads: Dict[str, QThread] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.component_callbacks: Dict[str, Dict[str, Callable]] = {}

    def register_component(self, component_id: str, agent_type: str = None, **kwargs) -> str:
        """
        Регистрирует компонент интерфейса и создает для него агента.

        Args:
            component_id: Уникальный идентификатор компонента
            agent_type: Тип агента для создания (по умолчанию используется агент по умолчанию)
            **kwargs: Дополнительные параметры для создания агента

        Returns:
            Идентификатор компонента
        """
        # Проверяем, зарегистрирован ли уже этот компонент
        if component_id in self.component_callbacks:
            logger.warning(f"Component {component_id} already registered")
            return component_id

        # Создаем агента
        agent = None
        if agent_type == "coding":
            agent = self.agent_manager.create_coding_agent(**kwargs)
        elif agent_type:
            agent = self.agent_manager.create_agent(agent_type, **kwargs)
        else:
            agent = self.agent_manager.get_default_agent()

        if not agent:
            logger.error(f"Failed to create agent for component {component_id}")
            return None

        # Устанавливаем агента как активный для компонента
        self.agent_manager.set_active_agent(component_id, agent)

        # Инициализируем словарь для обратных вызовов
        self.component_callbacks[component_id] = {}

        return component_id

    def unregister_component(self, component_id: str) -> bool:
        """
        Отменяет регистрацию компонента и освобождает связанные ресурсы.

        Args:
            component_id: Идентификатор компонента

        Returns:
            True, если компонент был отменен, False в противном случае
        """
        if component_id not in self.component_callbacks:
            return False

        # Останавливаем рабочий поток, если он существует
        if component_id in self.workers:
            worker = self.workers[component_id]
            if worker.isRunning():
                worker.stop()
                worker.wait()
            del self.workers[component_id]

        # Удаляем обратные вызовы
        del self.component_callbacks[component_id]

        # Очищаем неактивные агенты
        self.agent_manager.clear_inactive_agents()

        return True

    def register_callback(self, component_id: str, event_type: str, callback: Callable) -> bool:
        """
        Регистрирует обратный вызов для определенного типа события компонента.

        Args:
            component_id: Идентификатор компонента
            event_type: Тип события (message, error, thinking, finished)
            callback: Функция обратного вызова

        Returns:
            True, если обратный вызов был зарегистрирован, False в противном случае
        """
        if component_id not in self.component_callbacks:
            return False

        self.component_callbacks[component_id][event_type] = callback
        return True

    def process_query(self, component_id: str, query: str) -> bool:
        """
        Отправляет запрос агенту для обработки.

        Args:
            component_id: Идентификатор компонента
            query: Текст запроса

        Returns:
            True, если запрос был отправлен, False в противном случае
        """
        if component_id not in self.component_callbacks:
            logger.error(f"Component {component_id} not registered")
            return False

        # Получаем агента для компонента
        agent = self.agent_manager.get_active_agent(component_id)
        if not agent:
            logger.error(f"No agent found for component {component_id}")
            return False

        # Создаем новый рабочий поток, если нужно
        if component_id in self.workers:
            worker = self.workers[component_id]
            if worker.isRunning():
                logger.warning(f"Worker for component {component_id} is already running")
                return False

            # Удаляем старый рабочий поток
            del self.workers[component_id]

        # Создаем новый рабочий поток
        worker = AgentWorker(agent, component_id, self.signals)
        worker.query = query
        self.workers[component_id] = worker

        # Подключаем сигналы к соответствующим обратным вызовам
        self._connect_signals(component_id)

        # Запускаем рабочий поток
        worker.start()

        return True

    def stop_query(self, component_id: str) -> bool:
        """
        Останавливает выполнение запроса для указанного компонента.

        Args:
            component_id: Идентификатор компонента

        Returns:
            True, если запрос был остановлен, False в противном случае
        """
        if component_id not in self.workers:
            return False

        worker = self.workers[component_id]
        if not worker.isRunning():
            return False

        worker.stop()
        return True

    def _connect_signals(self, component_id: str):
        """
        Подключает сигналы рабочего потока к обратным вызовам компонента.

        Args:
            component_id: Идентификатор компонента
        """
        # Получаем словарь обратных вызовов для компонента
        callbacks = self.component_callbacks.get(component_id, {})

        # Подключаем сигналы к соответствующим обратным вызовам
        if "message" in callbacks:
            self.signals.message_received.connect(
                lambda cid, msg: self._handle_signal(cid, "message", msg)
            )

        if "error" in callbacks:
            self.signals.error_occurred.connect(
                lambda cid, err: self._handle_signal(cid, "error", err)
            )

        if "thinking" in callbacks:
            self.signals.thinking_state.connect(
                lambda cid, state: self._handle_signal(cid, "thinking", state)
            )

        if "finished" in callbacks:
            self.signals.finished.connect(
                lambda cid: self._handle_signal(cid, "finished", None)
            )

        if "code_snippet" in callbacks:
            self.signals.code_snippet_received.connect(
                lambda cid, code: self._handle_signal(cid, "code_snippet", code)
            )

        if "web_content" in callbacks:
            self.signals.web_content_received.connect(
                lambda cid, url, content: self._handle_signal(cid, "web_content", (url, content))
            )

        if "tool_started" in callbacks:
            self.signals.tool_execution_started.connect(
                lambda cid, tool: self._handle_signal(cid, "tool_started", tool)
            )

        if "tool_finished" in callbacks:
            self.signals.tool_execution_finished.connect(
                lambda cid, tool, success: self._handle_signal(cid, "tool_finished", (tool, success))
            )

    def _handle_signal(self, component_id: str, event_type: str, data: Any):
        """
        Обрабатывает сигнал и вызывает соответствующий обратный вызов.

        Args:
            component_id: Идентификатор компонента
            event_type: Тип события
            data: Данные события
        """
        # Проверяем, что сигнал предназначен для этого компонента
        if component_id not in self.component_callbacks:
            return

        # Получаем обратный вызов для типа события
        callback = self.component_callbacks.get(component_id, {}).get(event_type)
        if not callback:
            return

        # Вызываем обратный вызов с данными
        try:
            callback(data)
        except Exception as e:
            logger.error(f"Error in callback for {event_type}: {str(e)}")

    @staticmethod
    def instance() -> 'AgentController':
        """
        Возвращает глобальный экземпляр контроллера агентов.

        Returns:
            Экземпляр AgentController
        """
        if not hasattr(AgentController, "_instance"):
            AgentController._instance = AgentController()
        return AgentController._instance
