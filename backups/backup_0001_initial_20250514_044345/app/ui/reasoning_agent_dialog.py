"""
Диалог для работы с Reasoning Agent

Предоставляет интерфейс взаимодействия с агентом, позволяющий:
- Создавать планы для решения задач
- Одобрять или отклонять планы
- Контролировать выполнение планов
- Визуализировать дерево мыслей
- Управлять историей сессий
"""

import asyncio
import os
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QSize, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from app.agent.reasoning import ReasoningAgent
from app.agent.thought_tree import ThoughtNode, ThoughtTree
from app.logger import logger
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon
from app.ui.plan_view_widget import PlanViewWidget
from app.ui.session_history_manager import SessionHistoryManager, SessionRecord
from app.ui.thought_tree_widget import ThoughtTreeWidget


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
    thought_added = Signal(object)  # ThoughtNode

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

            # Привязываем обработчик для дерева мыслей
            self._connect_thought_tree_handlers()

            # Выполняем нужную операцию в зависимости от типа запроса
            if self.request_type == "plan":
                result = self.loop.run_until_complete(
                    self.agent.create_plan(self.request)
                )
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

    def _connect_thought_tree_handlers(self):
        """Подключает обработчики событий дерева мыслей."""
        if hasattr(self.agent, "thought_tree") and self.agent.thought_tree:
            # Устанавливаем функцию-обработчик для новых мыслей
            def on_thought_added(node):
                self.thought_added.emit(node)

            self.agent.thought_tree.set_callback("on_node_added", on_thought_added)

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


class SessionHistoryWidget(QWidget):
    """
    Виджет для отображения и управления историей сессий.
    """

    # Сигналы
    session_selected = Signal(str)  # ID выбранной сессии
    session_deleted = Signal(str)  # ID удаленной сессии

    def __init__(self, history_manager: SessionHistoryManager, parent=None):
        """
        Инициализирует виджет истории сессий.

        Args:
            history_manager: Менеджер истории сессий
            parent: Родительский виджет
        """
        super().__init__(parent)

        self.history_manager = history_manager
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        layout = QVBoxLayout(self)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel(tr("reasoning_agent.sessions.title", "Session History"))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label, 1)

        # Кнопки управления
        refresh_btn = QPushButton(get_icon("refresh"), "")
        refresh_btn.setToolTip(
            tr("reasoning_agent.sessions.refresh", "Refresh Sessions")
        )
        refresh_btn.clicked.connect(self.refresh_sessions)

        delete_btn = QPushButton(get_icon("delete"), "")
        delete_btn.setToolTip(
            tr("reasoning_agent.sessions.delete", "Delete Selected Session")
        )
        delete_btn.clicked.connect(self._delete_selected_session)

        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Список сессий
        self.sessions_list = QListWidget()
        self.sessions_list.setAlternatingRowColors(True)
        self.sessions_list.itemDoubleClicked.connect(self._on_session_double_clicked)

        # Контекстное меню для списка
        self.sessions_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.sessions_list)

        # Загружаем список сессий
        self.refresh_sessions()

    def refresh_sessions(self):
        """Обновляет список сессий."""
        self.sessions_list.clear()

        sessions = self.history_manager.get_sessions_list()

        for session in sessions:
            item = QListWidgetItem(f"{session['title']} ({session['formatted_date']})")
            item.setData(Qt.UserRole, session["session_id"])
            self.sessions_list.addItem(item)

    def _on_session_double_clicked(self, item):
        """Обработчик двойного щелчка по элементу списка сессий."""
        session_id = item.data(Qt.UserRole)
        self.session_selected.emit(session_id)

    def _delete_selected_session(self):
        """Удаляет выбранную сессию."""
        selected_items = self.sessions_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        session_id = item.data(Qt.UserRole)

        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            tr("reasoning_agent.sessions.delete.confirm.title", "Confirm Deletion"),
            tr(
                "reasoning_agent.sessions.delete.confirm.text",
                "Are you sure you want to delete this session?",
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Удаляем сессию
            if self.history_manager.delete_session(session_id):
                # Обновляем список и отправляем сигнал
                self.refresh_sessions()
                self.session_deleted.emit(session_id)

    def _show_context_menu(self, position):
        """Показывает контекстное меню для списка сессий."""
        menu = QMenu(self)

        # Действия
        load_action = QAction(
            tr("reasoning_agent.sessions.context.load", "Load Session"), self
        )
        rename_action = QAction(
            tr("reasoning_agent.sessions.context.rename", "Rename Session"), self
        )
        delete_action = QAction(
            tr("reasoning_agent.sessions.context.delete", "Delete Session"), self
        )

        # Добавляем действия в меню
        menu.addAction(load_action)
        menu.addAction(rename_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        # Получаем выбранный элемент
        selected_items = self.sessions_list.selectedItems()

        # Если нет выбранных элементов, отключаем все действия
        has_selection = len(selected_items) > 0
        load_action.setEnabled(has_selection)
        rename_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)

        # Обработчики действий
        if has_selection:
            session_id = selected_items[0].data(Qt.UserRole)

            load_action.triggered.connect(
                lambda: self.session_selected.emit(session_id)
            )
            delete_action.triggered.connect(self._delete_selected_session)
            rename_action.triggered.connect(lambda: self._rename_session(session_id))

        # Показываем меню в позиции курсора
        menu.exec(self.sessions_list.mapToGlobal(position))

    def _rename_session(self, session_id):
        """Переименовывает сессию."""
        # Загружаем сессию
        session = self.history_manager.get_session(session_id)
        if not session:
            return

        # Запрашиваем новое название
        new_title, ok = QInputDialog.getText(
            self,
            tr("reasoning_agent.sessions.rename.title", "Rename Session"),
            tr("reasoning_agent.sessions.rename.prompt", "Enter new session title:"),
            QLineEdit.Normal,
            session.title,
        )

        if ok and new_title:
            # Обновляем название
            session.title = new_title

            # Сохраняем сессию
            if self.history_manager.save_session(session):
                # Обновляем список
                self.refresh_sessions()


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

        # Инициализируем историю сессий
        self.history_manager = SessionHistoryManager()

        # Создаем новую сессию
        self.current_session = self.history_manager.create_session()

        # Состояние диалога
        self.current_plan = None  # Текущий план

        self.setWindowTitle(tr("reasoning_agent.title", "Reasoning Agent"))
        self.setMinimumSize(1000, 800)

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
        self.new_plan_button = QAction(
            get_icon("plan_create"), tr("reasoning_agent.new_plan", "New Plan"), self
        )
        self.approve_button = QAction(
            get_icon("plan_approve"),
            tr("reasoning_agent.approve", "Approve Plan"),
            self,
        )
        self.reject_button = QAction(
            get_icon("plan_reject"), tr("reasoning_agent.reject", "Reject Plan"), self
        )
        self.execute_button = QAction(
            get_icon("execute"), tr("reasoning_agent.execute", "Execute"), self
        )
        self.stop_button = QAction(
            get_icon("stop"), tr("reasoning_agent.stop", "Stop"), self
        )
        self.save_session_button = QAction(
            get_icon("save"), tr("reasoning_agent.save_session", "Save Session"), self
        )

        # Добавляем подсказки
        self.new_plan_button.setToolTip(
            tr("reasoning_agent.new_plan.tooltip", "Create a new action plan")
        )
        self.approve_button.setToolTip(
            tr("reasoning_agent.approve.tooltip", "Approve the current plan")
        )
        self.reject_button.setToolTip(
            tr("reasoning_agent.reject.tooltip", "Reject the current plan")
        )
        self.execute_button.setToolTip(
            tr("reasoning_agent.execute.tooltip", "Execute a request")
        )
        self.stop_button.setToolTip(
            tr("reasoning_agent.stop.tooltip", "Stop the current operation")
        )
        self.save_session_button.setToolTip(
            tr("reasoning_agent.save_session.tooltip", "Save current session")
        )

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
        toolbar.addSeparator()
        toolbar.addAction(self.save_session_button)

        # Добавляем выпадающий список стратегий
        toolbar.addSeparator()
        strategy_label = QLabel(tr("reasoning_agent.strategy", "Strategy:"))
        toolbar.addWidget(strategy_label)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItem(
            tr("reasoning_agent.strategy.sequential", "Sequential")
        )
        self.strategy_combo.addItem(tr("reasoning_agent.strategy.tree", "Tree"))
        self.strategy_combo.addItem(tr("reasoning_agent.strategy.adaptive", "Adaptive"))
        self.strategy_combo.setToolTip(
            tr("reasoning_agent.strategy.tooltip", "Select reasoning strategy")
        )
        toolbar.addWidget(self.strategy_combo)

        # Добавляем панель в основной лейаут
        main_layout.addWidget(toolbar)

        # Основной интерфейс с вкладками
        self.tab_widget = QTabWidget()

        # Вкладка с основным интерфейсом
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)

        # Разделитель для основной области и панели плана
        splitter = QSplitter(Qt.Horizontal)

        # Левая часть - поле ввода и вывода
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Поле вывода
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setAcceptRichText(True)
        self.output_text.setMinimumHeight(300)
        left_layout.addWidget(self.output_text, 3)

        # Поле статуса
        status_layout = QHBoxLayout()
        status_label = QLabel(tr("reasoning_agent.status", "Status:"))
        self.status_text = QLabel(tr("reasoning_agent.status.idle", "Idle"))
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_text, 1)
        left_layout.addLayout(status_layout)

        # Панель ввода
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            tr("reasoning_agent.input.placeholder", "Enter your request here...")
        )

        send_button = QPushButton(get_icon("send"), "")
        send_button.setToolTip(tr("reasoning_agent.input.send", "Send"))
        send_button.clicked.connect(self._on_input_entered)

        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(send_button)

        left_layout.addLayout(input_layout)

        # Правая часть - отображение плана
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.plan_view = PlanViewWidget()
        right_layout.addWidget(self.plan_view)

        # Добавляем панели в разделитель
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Устанавливаем начальное соотношение ширины (60/40)
        splitter.setSizes([600, 400])

        main_tab_layout.addWidget(splitter)

        # Вкладка с деревом мыслей
        thought_tree_tab = QWidget()
        thought_tree_layout = QVBoxLayout(thought_tree_tab)

        self.thought_tree_widget = ThoughtTreeWidget()
        thought_tree_layout.addWidget(self.thought_tree_widget)

        # Устанавливаем дерево мыслей из агента, если оно есть
        if hasattr(self.agent, "thought_tree") and self.agent.thought_tree:
            self.thought_tree_widget.set_thought_tree(self.agent.thought_tree)

        # Вкладка с историей сессий
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        self.history_widget = SessionHistoryWidget(self.history_manager)
        history_layout.addWidget(self.history_widget)

        # Добавляем вкладки
        self.tab_widget.addTab(main_tab, tr("reasoning_agent.tab.main", "Main"))
        self.tab_widget.addTab(
            thought_tree_tab, tr("reasoning_agent.tab.thought_tree", "Thought Tree")
        )
        self.tab_widget.addTab(
            history_tab, tr("reasoning_agent.tab.history", "History")
        )

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

        # Устанавливаем фокус на поле ввода
        self.input_field.setFocus()

    def _connect_signals(self):
        """Подключает сигналы и слоты."""
        # Кнопки управления
        self.new_plan_button.triggered.connect(self._on_new_plan_clicked)
        self.approve_button.triggered.connect(self._on_approve_clicked)
        self.reject_button.triggered.connect(self._on_reject_clicked)
        self.execute_button.triggered.connect(self._on_execute_clicked)
        self.stop_button.triggered.connect(self._on_stop_clicked)
        self.save_session_button.triggered.connect(self._on_save_session_clicked)

        # Сигналы рабочего потока
        self.worker.started.connect(self._on_worker_started)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.error.connect(self._on_worker_error)
        self.worker.plan_created.connect(self._on_plan_created)
        self.worker.execution_completed.connect(
            lambda: self._update_status(
                tr("reasoning_agent.status.execution_completed", "Execution completed")
            )
        )
        self.worker.thought_added.connect(self._on_thought_added)

        # Строка ввода
        self.input_field.returnPressed.connect(self._on_input_entered)

        # План
        self.plan_view.step_details_requested.connect(self._on_step_details_requested)

        # История сессий
        self.history_widget.session_selected.connect(self._on_session_selected)
        self.history_widget.session_deleted.connect(self._on_session_deleted)

        # Выбор стратегии
        self.strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)

    def _on_new_plan_clicked(self):
        """Обработчик нажатия кнопки создания нового плана."""
        # Запрашиваем текст задачи
        task, ok = QInputDialog.getText(
            self,
            tr("reasoning_agent.new_plan.title", "Create Plan"),
            tr("reasoning_agent.new_plan.prompt", "Enter task description:"),
            QLineEdit.Normal,
        )

        if ok and task:
            self._create_plan(task)

    def _on_approve_clicked(self):
        """Обработчик нажатия кнопки подтверждения плана."""
        if not self.current_plan:
            return

        self._append_output(
            tr(
                "reasoning_agent.plan.approved",
                "Plan approved. Type a command or request to execute.",
            ),
            "green",
        )

        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)

        # Сохраняем план в сессию
        if self.current_session:
            self.current_session.add_plan(self.current_plan)
            self.history_manager.save_session(self.current_session)

        # Сохраняем одобренный план в агенте
        self.agent.set_approved_plan(self.current_plan)

    def _on_reject_clicked(self):
        """Обработчик нажатия кнопки отклонения плана."""
        if not self.current_plan:
            return

        # Очищаем текущий план
        self.current_plan = None
        self.plan_view.clear_plan()

        self._append_output(
            tr(
                "reasoning_agent.plan.rejected",
                "Plan rejected. Create a new plan or type a different request.",
            ),
            "red",
        )

        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)

        # Очищаем план в агенте
        self.agent.clear_plan()

    def _on_execute_clicked(self):
        """Обработчик нажатия кнопки выполнения запроса."""
        # Запрашиваем текст запроса, если поле ввода пусто
        request = self.input_field.text().strip()

        if not request:
            request, ok = QInputDialog.getText(
                self,
                tr("reasoning_agent.execute.title", "Execute Request"),
                tr("reasoning_agent.execute.prompt", "Enter request to execute:"),
                QLineEdit.Normal,
            )

            if not (ok and request):
                return

        self._execute_request(request)
        self.input_field.clear()

    def _on_stop_clicked(self):
        """Обработчик нажатия кнопки остановки операции."""
        self.worker.cancel()

        self._append_output(
            tr("reasoning_agent.operation.cancelled", "Operation cancelled."), "orange"
        )

        self._update_status(tr("reasoning_agent.status.idle", "Idle"))
        self.stop_button.setEnabled(False)

    def _on_save_session_clicked(self):
        """Обработчик нажатия кнопки сохранения сессии."""
        if not self.current_session:
            return

        # Запрашиваем название сессии
        title, ok = QInputDialog.getText(
            self,
            tr("reasoning_agent.save_session.title", "Save Session"),
            tr("reasoning_agent.save_session.prompt", "Enter session title:"),
            QLineEdit.Normal,
            self.current_session.title,
        )

        if ok and title:
            # Обновляем название сессии
            self.current_session.title = title

            # Сохраняем дерево мыслей, если оно есть
            if hasattr(self.agent, "thought_tree") and self.agent.thought_tree:
                self.current_session.set_thought_tree(self.agent.thought_tree)

            # Сохраняем сессию
            if self.history_manager.save_session(self.current_session):
                self._append_output(
                    tr("reasoning_agent.session.saved", "Session saved: {0}").format(
                        title
                    ),
                    "blue",
                )

                # Обновляем список сессий
                self.history_widget.refresh_sessions()
            else:
                self._append_output(
                    tr("reasoning_agent.session.save_error", "Error saving session"),
                    "red",
                )

    def _on_input_entered(self):
        """Обработчик ввода в поле ввода."""
        text = self.input_field.text().strip()

        if not text:
            return

        # Если есть одобренный план, выполняем запрос
        if self.agent.has_approved_plan():
            self._execute_request(text)
        else:
            # Иначе создаем новый план
            self._create_plan(text)

        # Добавляем сообщение пользователя в сессию
        if self.current_session:
            self.current_session.add_message("user", text)
            self.history_manager.save_session(self.current_session)

        # Очищаем поле ввода
        self.input_field.clear()

    def _on_strategy_changed(self, index):
        """Обработчик изменения стратегии рассуждения."""
        strategy = self.strategy_combo.currentText().lower()

        # Устанавливаем стратегию в агенте
        if hasattr(self.agent, "set_strategy"):
            try:
                self.agent.set_strategy(strategy)
                self._append_output(
                    tr(
                        "reasoning_agent.strategy.changed",
                        "Reasoning strategy changed to: {0}",
                    ).format(strategy),
                    "blue",
                )
            except Exception as e:
                logger.error(f"Error setting strategy: {str(e)}")
                self._append_output(
                    tr(
                        "reasoning_agent.strategy.error", "Error setting strategy: {0}"
                    ).format(str(e)),
                    "red",
                )

    def _create_plan(self, task: str):
        """
        Запускает создание плана.

        Args:
            task: Описание задачи
        """
        # Очищаем предыдущий план
        self.current_plan = None
        self.plan_view.clear_plan()

        # Отключаем кнопки
        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)

        # Добавляем текст запроса в вывод
        self._append_output(
            tr("reasoning_agent.task", "Task: {0}").format(task), "blue"
        )

        # Обновляем статус
        self._update_status(
            tr("reasoning_agent.status.creating_plan", "Creating plan...")
        )

        # Запускаем создание плана
        self.worker.create_plan(task)

    def _execute_request(self, request: str):
        """
        Запускает выполнение запроса.

        Args:
            request: Текст запроса
        """
        # Добавляем текст запроса в вывод
        self._append_output(
            tr("reasoning_agent.request", "Request: {0}").format(request), "blue"
        )

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.executing", "Executing..."))

        # Запускаем выполнение
        self.worker.execute_request(request)

    def _on_worker_started(self):
        """Обработчик начала выполнения задачи воркером."""
        # Включаем кнопку остановки
        self.stop_button.setEnabled(True)

        # Отключаем остальные кнопки
        self.new_plan_button.setEnabled(False)
        self.approve_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.execute_button.setEnabled(False)

    def _on_worker_finished(self, result: str):
        """
        Обработчик завершения выполнения задачи воркером.

        Args:
            result: Результат выполнения
        """
        # Добавляем результат в вывод
        self._append_output(result)

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.idle", "Idle"))

        # Включаем кнопки
        self.new_plan_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Добавляем сообщение агента в сессию
        if self.current_session:
            self.current_session.add_message("assistant", result)
            self.history_manager.save_session(self.current_session)

    def _on_worker_error(self, error: str):
        """
        Обработчик ошибки выполнения задачи воркером.

        Args:
            error: Текст ошибки
        """
        # Добавляем ошибку в вывод
        self._append_output(
            tr("reasoning_agent.error", "Error: {0}").format(error), "red"
        )

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.error", "Error"))

        # Включаем кнопки
        self.new_plan_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Добавляем сообщение об ошибке в сессию
        if self.current_session:
            self.current_session.add_message("system", f"Error: {error}")
            self.history_manager.save_session(self.current_session)

    def _on_worker_progress(self, message: str):
        """
        Обработчик прогресса выполнения задачи воркером.

        Args:
            message: Сообщение о прогрессе
        """
        self._append_output(message)

    def _on_plan_created(self, plan: str):
        """
        Обработчик создания плана воркером.

        Args:
            plan: Текст плана
        """
        # Парсим план
        self.current_plan = self._parse_plan(plan)

        # Добавляем план в вывод
        self._append_output(
            tr("reasoning_agent.plan.created", "Plan created:"), "green"
        )
        self._append_output(plan)

        # Отображаем план в визуализаторе
        self.plan_view.set_plan(self.current_plan)

        # Включаем кнопки управления планом
        self.approve_button.setEnabled(True)
        self.reject_button.setEnabled(True)

        # Обновляем статус
        self._update_status(tr("reasoning_agent.status.plan_ready", "Plan ready"))

        # Включаем основные кнопки
        self.new_plan_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Добавляем сообщение агента в сессию
        if self.current_session:
            self.current_session.add_message("assistant", plan)
            self.current_session.add_plan(self.current_plan)
            self.history_manager.save_session(self.current_session)

    def _on_thought_added(self, node: ThoughtNode):
        """
        Обработчик добавления мысли в дерево мыслей.

        Args:
            node: Узел дерева мыслей
        """
        # Обновляем виджет дерева мыслей
        self.thought_tree_widget.refresh_tree()

        # Записываем промежуточное состояние дерева мыслей в сессию
        if (
            self.current_session
            and hasattr(self.agent, "thought_tree")
            and self.agent.thought_tree
        ):
            self.current_session.set_thought_tree(self.agent.thought_tree)
            self.history_manager.save_session(self.current_session)

    def _on_session_selected(self, session_id: str):
        """
        Обработчик выбора сессии в истории.

        Args:
            session_id: ID выбранной сессии
        """
        # Загружаем сессию
        session = self.history_manager.load_session(session_id)

        if not session:
            self._append_output(
                tr("reasoning_agent.session.load_error", "Error loading session"), "red"
            )
            return

        # Устанавливаем текущую сессию
        self.current_session = session

        # Загружаем диалог
        self.output_text.clear()
        for message in session.dialogue:
            role = message.get("role")
            content = message.get("content")

            if role == "user":
                self._append_output(
                    tr("reasoning_agent.message.user", "User: {0}").format(content),
                    "blue",
                )
            elif role == "assistant":
                self._append_output(content)
            elif role == "system":
                self._append_output(content, "gray")

        # Загружаем план, если есть
        if session.plans:
            # Берем последний план
            self.current_plan = session.plans[-1]
            self.plan_view.set_plan(self.current_plan)

            # Устанавливаем план в агенте
            self.agent.set_approved_plan(self.current_plan)

            # Включаем кнопки управления планом
            self.approve_button.setEnabled(True)
            self.reject_button.setEnabled(True)

        # Загружаем дерево мыслей, если есть
        thought_tree = session.get_thought_tree()
        if thought_tree:
            # Устанавливаем дерево мыслей в агенте
            if hasattr(self.agent, "set_thought_tree"):
                self.agent.set_thought_tree(thought_tree)

            # Обновляем виджет дерева мыслей
            self.thought_tree_widget.set_thought_tree(thought_tree)

            # Переключаемся на вкладку дерева мыслей
            self.tab_widget.setCurrentIndex(1)

        self._append_output(
            tr("reasoning_agent.session.loaded", "Session loaded: {0}").format(
                session.title
            ),
            "green",
        )

    def _on_session_deleted(self, session_id: str):
        """
        Обработчик удаления сессии.

        Args:
            session_id: ID удаленной сессии
        """
        # Если удалена текущая сессия, создаем новую
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = self.history_manager.create_session()

            self._append_output(
                tr("reasoning_agent.session.new", "Started new session"), "green"
            )

    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """
        Парсит текст плана в структурированный формат.

        Args:
            plan_text: Текстовое представление плана

        Returns:
            Структурированный план в виде словаря
        """
        try:
            lines = plan_text.strip().split("\n")

            # Ищем заголовок плана
            title = ""
            plan_start_idx = 0

            for i, line in enumerate(lines):
                if line.lower().startswith("plan:") or line.lower().startswith(
                    "# plan"
                ):
                    title = line.split(":", 1)[1].strip() if ":" in line else ""
                    plan_start_idx = i + 1
                    break

            # Разбираем шаги плана
            steps = []
            current_step = None

            for i in range(plan_start_idx, len(lines)):
                line = lines[i].strip()

                # Пропускаем пустые строки
                if not line:
                    continue

                # Ищем новый шаг
                if line.startswith("Step ") or (line[0].isdigit() and "." in line[:5]):
                    # Сохраняем предыдущий шаг, если есть
                    if current_step:
                        steps.append(current_step)

                    # Парсим номер и заголовок шага
                    step_parts = line.split(":", 1) if ":" in line else [line, ""]
                    step_title = step_parts[1].strip() if len(step_parts) > 1 else ""

                    # Создаем новый шаг
                    current_step = {
                        "id": len(steps) + 1,
                        "title": step_title,
                        "description": "",
                        "substeps": [],
                        "rationale": "",
                        "raw_text": line,
                    }

                # Добавляем содержимое к текущему шагу
                elif current_step:
                    current_step["raw_text"] += "\n" + line

                    # Пытаемся определить тип контента
                    if line.startswith("- ") or line.startswith("* "):
                        # Это подшаг или пункт списка
                        substep = line[2:].strip()
                        current_step["substeps"].append(substep)
                    elif "rationale:" in line.lower() or "reasoning:" in line.lower():
                        # Это обоснование
                        current_step["rationale"] = line.split(":", 1)[1].strip()
                    else:
                        # Это описание
                        if current_step["description"]:
                            current_step["description"] += "\n" + line
                        else:
                            current_step["description"] = line

            # Добавляем последний шаг
            if current_step:
                steps.append(current_step)

            # Собираем план
            plan = {"title": title, "steps": steps, "raw_text": plan_text}

            return plan

        except Exception as e:
            logger.error(f"Error parsing plan: {str(e)}")
            # Возвращаем базовую структуру, если парсинг не удался
            return {"title": "", "steps": [], "raw_text": plan_text}

    def _on_step_details_requested(self, step_id: int):
        """
        Обработчик запроса деталей шага плана.

        Args:
            step_id: ID шага
        """
        if not self.current_plan or not self.current_plan["steps"]:
            return

        # Ищем шаг с указанным ID
        step = None
        for s in self.current_plan["steps"]:
            if s["id"] == step_id:
                step = s
                break

        if not step:
            return

        # Отображаем информацию о шаге
        details = QMessageBox(self)
        details.setWindowTitle(tr("reasoning_agent.step.details.title", "Step Details"))

        # Формируем текст с деталями
        detail_text = f"<h3>{step['title']}</h3>"

        if step["description"]:
            detail_text += f"<p><b>{tr('reasoning_agent.step.details.description', 'Description:')}</b> {step['description']}</p>"

        if step["substeps"]:
            detail_text += f"<p><b>{tr('reasoning_agent.step.details.substeps', 'Substeps:')}</b></p><ul>"
            for substep in step["substeps"]:
                detail_text += f"<li>{substep}</li>"
            detail_text += "</ul>"

        if step["rationale"]:
            detail_text += f"<p><b>{tr('reasoning_agent.step.details.rationale', 'Rationale:')}</b> {step['rationale']}</p>"

        details.setText(detail_text)
        details.setTextFormat(Qt.RichText)
        details.setStandardButtons(QMessageBox.Ok)
        details.exec()

    def _append_output(self, text: str, color: str = None):
        """
        Добавляет текст в поле вывода.

        Args:
            text: Текст для добавления
            color: Цвет текста (None для черного, или название цвета)
        """
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Создаем формат текста
        format = QTextCharFormat()

        if color:
            format.setForeground(QColor(color))

        # Применяем формат и вставляем текст
        cursor.setCharFormat(format)

        # Добавляем перенос строки, если текст не пустой и в поле есть содержимое
        if self.output_text.toPlainText() and text:
            cursor.insertText("\n")

        # Вставляем новый текст
        cursor.insertText(text)

        # Прокручиваем вниз
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)

    def _update_status(self, status: str):
        """Обновляет текст статуса."""
        self.status_text.setText(status)

    def closeEvent(self, event):
        """Обработчик закрытия диалога."""
        # Сохраняем текущую сессию
        if self.current_session:
            self.history_manager.save_session(self.current_session)

        # Отменяем текущую операцию, если она выполняется
        self.worker.cancel()

        # Завершаем поток
        self.worker_thread.quit()
        self.worker_thread.wait()

        super().closeEvent(event)
