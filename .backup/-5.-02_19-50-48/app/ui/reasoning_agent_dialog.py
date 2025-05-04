"""
Диалог для работы с Reasoning Agent

Предоставляет интерфейс взаимодействия с агентом, позволяющий:
- Создавать планы для решения задач
- Одобрять или отклонять планы
- Контролировать выполнение планов
"""

import asyncio
import threading
import time
import os
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QToolBar, QSplitter, QWidget,
    QComboBox, QCheckBox, QProgressBar, QFrame, QToolButton,
    QScrollArea, QSizePolicy, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize, QObject, QThread
from PySide6.QtGui import QIcon, QAction, QTextCursor, QFont, QColor, QTextCharFormat

from app.agent.reasoning import ReasoningAgent
from app.ui.icon_manager import get_icon
from app.logger import logger
from app.ui.i18n.translator import tr


class AgentWorkerThread(QObject):
    """
    Рабочий поток для выполнения задач Reasoning Agent.
    """
    # Сигналы
    started = Signal()
    finished = Signal(str)
    progress = Signal(str)
    error = Signal(str)
    plan_created = Signal(str)
    execution_completed = Signal()
    thinking_started = Signal()
    thinking_ended = Signal()
    tool_started = Signal(str)
    tool_ended = Signal(str)

    def __init__(self, agent: ReasoningAgent):
        super().__init__()
        self.agent = agent
        self.request = ""
        self.loop = None
        self.request_type = ""
        self._is_running = False
        self._cancelled = False

    @Slot(str)
    def create_plan(self, task: str):
        """Запускает создание плана."""
        self.request = task
        self.request_type = "plan"
        self._run_task()

    @Slot(str)
    def execute_request(self, request: str):
        """Запускает выполнение запроса."""
        self.request = request
        self.request_type = "execute"
        self._run_task()

    def _run_task(self):
        """Запускает задачу агента в отдельном потоке."""
        if self._is_running:
            logger.warning("Agent is already running")
            return

        self._is_running = True
        self._cancelled = False
        self.started.emit()

        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=self._run_agent_task)
        thread.daemon = True
        thread.start()

    def _run_agent_task(self):
        """Выполняет задачу агента."""
        try:
            # Создаем новый event loop для потока
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Выполняем нужную операцию в зависимости от типа запроса
            if self.request_type == "plan":
                result = self.loop.run_until_complete(self.agent.create_plan(self.request))
                self.plan_created.emit(result)
            elif self.request_type == "execute":
                result = self.loop.run_until_complete(self.agent.run(self.request))
                self.finished.emit(result)
            else:
                result = "Unknown request type"
                self.error.emit(f"Unknown request type: {self.request_type}")
        except Exception as e:
            logger.error(f"Error in agent task: {str(e)}")
            self.error.emit(f"Error: {str(e)}")
        finally:
            self._is_running = False
            self.loop = None

    def cancel(self):
        """Отменяет текущую задачу агента."""
        if self._is_running and not self._cancelled:
            self._cancelled = True

            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self._cancel_task(), self.loop)

    async def _cancel_task(self):
        """Корутина для отмены задачи агента."""
        if hasattr(self.agent, "cleanup"):
            await self.agent.cleanup()


class ReasoningAgentDialog(QDialog):
    """
    Диалог для работы с Reasoning Agent.

    Предоставляет интерфейс для создания плана действий, его одобрения
    и контроля выполнения в соответствии с методикой
    "План → Разрешение → Выполнение".
    """

    def __init__(self, agent: ReasoningAgent, parent=None):
        super().__init__(parent)

        self.agent = agent
        self.worker = AgentWorkerThread(agent)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Состояние диалога
        self.current_plan = None  # Текущий план

        self.setWindowTitle(tr("reasoning_agent.title", "Reasoning Agent"))
        self.setMinimumSize(900, 700)

        # Настройка UI
        self._setup_ui()

        # Подключение сигналов
        self._connect_signals()

    def _setup_ui(self):
        """Настраивает интерфейс диалога."""
        main_layout = QVBoxLayout()

        # Верхняя панель инструментов
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))

        # Кнопки управления
        self.new_plan_button = QAction(get_icon("plan_create"), tr("reasoning_agent.new_plan", "New Plan"), self)
        self.approve_button = QAction(get_icon("plan_approve"), tr("reasoning_agent.approve", "Approve Plan"), self)
        self.reject_button = QAction(get_icon("plan_reject"), tr("reasoning_agent.reject", "Reject Plan"), self)
        self.execute_button = QAction(get_icon("execute"), tr("reasoning_agent.execute", "Execute"), self)
        self.stop_button = QAction(get_icon("stop"), tr("reasoning_agent.stop", "Stop"), self)

        # Добавляем подсказки
        self.new_plan_button.setToolTip(tr("reasoning_agent.new_plan.tooltip", "Create a new action plan"))
        self.approve_button.setToolTip(tr("reasoning_agent.approve.tooltip", "Approve the current plan"))
        self.reject_button.setToolTip(tr("reasoning_agent.reject.tooltip", "Reject the current plan"))
        self.execute_button.setToolTip(tr("reasoning_agent.execute.tooltip", "Execute a request"))
        self.stop_button.setToolTip(tr("reasoning_agent.stop.tooltip", "Stop the current operation"))

        # Настраиваем начальное состояние кнопок
        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Добавляем кнопки на панель
        toolbar.addAction(self.new_plan_button)
        toolbar.addSeparator()
        toolbar.addAction(self.approve_button)
        toolbar.addAction(self.reject_button)
        toolbar.addSeparator()
        toolbar.addAction(self.execute_button)
        toolbar.addAction(self.stop_button)

        # Добавляем выпадающий список стратегий
        toolbar.addSeparator()
        strategy_label = QLabel(tr("reasoning_agent.strategy", "Strategy:"))
        toolbar.addWidget(strategy_label)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItem(tr("reasoning_agent.strategy.sequential", "Sequential"))
        self.strategy_combo.addItem(tr("reasoning_agent.strategy.tree", "Tree"))
        self.strategy_combo.addItem(tr("reasoning_agent.strategy.adaptive", "Adaptive"))
        self.strategy_combo.setToolTip(tr("reasoning_agent.strategy.tooltip", "Select reasoning strategy"))
        toolbar.addWidget(self.strategy_combo)

        # Добавляем панель в основной layout
        main_layout.addWidget(toolbar)

        # Сплиттер для области текста
        splitter = QSplitter(Qt.Vertical)

        # Верхняя область - лог и результаты
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        # Заголовок для лога
        top_layout.addWidget(QLabel(tr("reasoning_agent.output", "Agent Output:")))

        # Область вывода
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #f5f5f5; font-family: 'Consolas', monospace;")
        top_layout.addWidget(self.output_text)

        # Нижняя область - текущий план
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        # Заголовок для плана
        bottom_layout.addWidget(QLabel(tr("reasoning_agent.current_plan", "Current Plan:")))

        # Область плана
        self.plan_text = QTextEdit()
        self.plan_text.setReadOnly(True)
        self.plan_text.setStyleSheet("background-color: #f0f7ff; font-family: 'Consolas', monospace;")
        bottom_layout.addWidget(self.plan_text)

        # Добавляем виджеты в сплиттер
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([300, 400])  # Начальные размеры

        # Добавляем сплиттер в основной layout
        main_layout.addWidget(splitter)

        # Строка ввода и кнопка отправки
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(tr("reasoning_agent.input.placeholder", "Enter your request or 'plan <task>' to create a plan"))
        input_layout.addWidget(self.input_field, 1)

        self.send_button = QPushButton(tr("reasoning_agent.send", "Send"))
        self.send_button.setIcon(get_icon("send"))
        input_layout.addWidget(self.send_button)

        # Добавляем строку ввода в основной layout
        main_layout.addLayout(input_layout)

        # Панель состояния
        status_layout = QHBoxLayout()

        self.status_label = QLabel(tr("reasoning_agent.status.ready", "Ready"))
        status_layout.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Бесконечный режим
        status_layout.addWidget(self.progress_bar)

        # Добавляем панель состояния в основной layout
        main_layout.addLayout(status_layout)

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Подключает сигналы и слоты."""
        # Кнопки панели инструментов
        self.new_plan_button.triggered.connect(self._on_new_plan_clicked)
        self.approve_button.triggered.connect(self._on_approve_clicked)
        self.reject_button.triggered.connect(self._on_reject_clicked)
        self.execute_button.triggered.connect(self._on_execute_clicked)
        self.stop_button.triggered.connect(self._on_stop_clicked)

        # Строка ввода
        self.input_field.returnPressed.connect(self._on_input_entered)
        self.send_button.clicked.connect(self._on_input_entered)

        # Сигналы worker'а
        self.worker.started.connect(self._on_worker_started)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.plan_created.connect(self._on_plan_created)

        # События состояния мышления
        self.worker.thinking_started.connect(lambda: self._update_status("Thinking..."))
        self.worker.thinking_ended.connect(lambda: self._update_status("Processing..."))
        self.worker.tool_started.connect(lambda tool: self._update_status(f"Using tool: {tool}"))
        self.worker.tool_ended.connect(lambda tool: self._update_status(f"Finished using tool: {tool}"))

    def _on_new_plan_clicked(self):
        """Обрабатывает нажатие кнопки 'Новый план'."""
        # Запрашиваем задачу
        task, ok = QInputDialog.getText(
            self,
            tr("reasoning_agent.new_plan.title", "Create New Plan"),
            tr("reasoning_agent.new_plan.prompt", "Enter the task description:")
        )

        if ok and task:
            self._create_plan(task)

    def _on_approve_clicked(self):
        """Обрабатывает нажатие кнопки 'Одобрить план'."""
        if self.agent and self.current_plan:
            self.agent.approve_plan()
            self._update_status(tr("reasoning_agent.status.plan_approved", "Plan approved"))

            # Выводим сообщение об одобрении
            self._append_output(
                tr("reasoning_agent.plan_approved", "Plan approved. You can now execute requests."),
                "blue"
            )

            # Обновляем состояние кнопок
            self.approve_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.execute_button.setEnabled(True)

    def _on_reject_clicked(self):
        """Обрабатывает нажатие кнопки 'Отклонить план'."""
        if self.agent and self.current_plan:
            self.agent.reject_plan()
            self._update_status(tr("reasoning_agent.status.plan_rejected", "Plan rejected"))

            # Выводим сообщение об отклонении
            self._append_output(
                tr("reasoning_agent.plan_rejected", "Plan rejected. Create a new plan."),
                "red"
            )

            # Очищаем текущий план
            self.current_plan = None
            self.plan_text.clear()

            # Обновляем состояние кнопок
            self.approve_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.new_plan_button.setEnabled(True)

    def _on_execute_clicked(self):
        """Обрабатывает нажатие кнопки 'Выполнить'."""
        # Получаем текст из строки ввода
        text = self.input_field.text().strip()

        if text:
            self._execute_request(text)
            self.input_field.clear()

    def _on_stop_clicked(self):
        """Обрабатывает нажатие кнопки 'Остановить'."""
        # Останавливаем текущую операцию
        if self.worker:
            self.worker.cancel()
            self._update_status(tr("reasoning_agent.status.stopping", "Stopping operation..."))

    def _on_input_entered(self):
        """Обрабатывает ввод текста и нажатие Enter."""
        # Получаем текст из строки ввода
        text = self.input_field.text().strip()

        if not text:
            return

        # Проверяем, является ли ввод командой
        if text.lower().startswith("plan "):
            # Создание плана
            task = text[5:].strip()
            self._create_plan(task)
        elif text.lower() == "approve":
            # Одобрение плана
            self._on_approve_clicked()
        elif text.lower() == "reject":
            # Отклонение плана
            self._on_reject_clicked()
        else:
            # Обычный запрос на выполнение
            self._execute_request(text)

        # Очищаем строку ввода
        self.input_field.clear()

    def _create_plan(self, task: str):
        """Запускает создание плана для задачи."""
        if not task:
            return

        # Сбрасываем текущий план
        self.current_plan = None
        self.plan_text.clear()

        # Отображаем задачу в логе
        self._append_output(
            tr("reasoning_agent.creating_plan", "Creating plan for task: {0}").format(task),
            "green"
        )

        # Запускаем создание плана
        self.worker.create_plan(task)

        # Обновляем состояние кнопок
        self.new_plan_button.setEnabled(False)
        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.execute_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _execute_request(self, request: str):
        """Запускает выполнение запроса."""
        if not request:
            return

        # Проверяем, одобрен ли план
        if not self.current_plan:
            self._append_output(
                tr("reasoning_agent.no_plan", "No approved plan. Please create and approve a plan first."),
                "red"
            )
            return

        # Отображаем запрос в логе
        self._append_output(
            tr("reasoning_agent.executing", "Executing request: {0}").format(request),
            "green"
        )

        # Запускаем выполнение запроса
        self.worker.execute_request(request)

        # Обновляем состояние кнопок
        self.new_plan_button.setEnabled(False)
        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.execute_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _on_worker_started(self):
        """Обрабатывает начало работы worker'а."""
        # Показываем индикатор прогресса
        self.progress_bar.setVisible(True)

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.working", "Working..."))

    def _on_worker_finished(self, result: str):
        """Обрабатывает завершение работы worker'а."""
        # Скрываем индикатор прогресса
        self.progress_bar.setVisible(False)

        # Выводим результат
        self._append_output(result)

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.ready", "Ready"))

        # Обновляем состояние кнопок
        self.new_plan_button.setEnabled(True)
        self.execute_button.setEnabled(bool(self.current_plan))
        self.stop_button.setEnabled(False)

    def _on_worker_error(self, error: str):
        """Обрабатывает ошибку worker'а."""
        # Скрываем индикатор прогресса
        self.progress_bar.setVisible(False)

        # Выводим ошибку
        self._append_output(error, "red")

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.error", "Error occurred"))

        # Обновляем состояние кнопок
        self.new_plan_button.setEnabled(True)
        self.execute_button.setEnabled(bool(self.current_plan))
        self.stop_button.setEnabled(False)

    def _on_worker_progress(self, message: str):
        """Обрабатывает прогресс worker'а."""
        # Выводим сообщение о прогрессе
        self._append_output(message, "gray")

    def _on_plan_created(self, plan: str):
        """Обрабатывает создание плана."""
        # Сохраняем план
        self.current_plan = plan

        # Отображаем план
        self.plan_text.setPlainText(plan)

        # Обновляем состояние кнопок
        self.approve_button.setEnabled(True)
        self.reject_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.plan_created", "Plan created, waiting for approval"))

        # Выводим сообщение
        self._append_output(
            tr("reasoning_agent.plan_created", "Plan created. Please review and approve or reject."),
            "blue"
        )

    def _append_output(self, text: str, color: str = None):
        """Добавляет текст в область вывода с форматированием."""
        # Получаем текущую позицию курсора
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Создаем формат текста с цветом
        if color:
            fmt = QTextCharFormat()
            if color == "red":
                fmt.setForeground(QColor(200, 0, 0))
            elif color == "green":
                fmt.setForeground(QColor(0, 120, 0))
            elif color == "blue":
                fmt.setForeground(QColor(0, 0, 180))
            elif color == "gray":
                fmt.setForeground(QColor(100, 100, 100))
            cursor.setCharFormat(fmt)

        # Вставляем текст
        cursor.insertText(text + "\n\n")

        # Прокручиваем до конца
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

    def _update_status(self, status: str):
        """Обновляет статусную строку."""
        self.status_label.setText(status)

    def closeEvent(self, event):
        """Обрабатывает закрытие диалога."""
        # Останавливаем рабочий поток
        if self.worker_thread.isRunning():
            self.worker.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait(1000)  # Ждем 1 секунду

        # Закрываем диалог
        event.accept()
