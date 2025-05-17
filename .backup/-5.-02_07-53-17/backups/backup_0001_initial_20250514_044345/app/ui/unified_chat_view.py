"""
Унифицированный интерфейс чата для различных режимов работы.

Объединяет функциональность различных агентов (Browsing, Coding и др.)
в единый интерфейс с переключаемыми режимами.
"""

import asyncio
import logging
import os
import datetime
import json
from typing import Dict, List, Optional, Any, Callable

from PySide6.QtCore import QPoint, QSize, Qt, Signal, Slot, QTimer
from PySide6.QtGui import QAction, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QSplitter, QTabWidget, QToolBar, QMessageBox, QFileDialog,
    QProgressBar, QStackedWidget, QButtonGroup, QSizePolicy, QAbstractButton,
    QDialog, QMenu, QInputDialog
)

from app.ui.browser_agent_interface import BrowserAgentInterface
from app.ui.coding_agent_interface import CodingAgentInterface
from app.ui.browser_tab_widget import MultiBrowserWidget
from app.ui.code_editor_widget import MultiEditorWidget
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon
from app.utils.theme_manager import ThemeManager
from app.utils.chat_indexer import ChatHistoryIndexer
from app.ui.chat_search_dialog import ChatSearchDialog

# Константы для режимов
MODE_BROWSING = "browsing"
MODE_CODING = "coding"

logger = logging.getLogger(__name__)


class ChatHistoryWidget(QTextEdit):
    """
    Виджет истории чата с расширенным функционалом.

    Объединяет функциональность ChatHistoryWidget из browser_agent_dialog.py и coding_agent_dialog.py.
    """
    url_open_requested = Signal(str)
    code_insert_requested = Signal(str)
    run_code_in_terminal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def contextMenuEvent(self, event):
        """Переопределенное контекстное меню с расширенными возможностями."""
        menu = self.createStandardContextMenu()

        # Получаем выделенный текст
        selected_text = self.textCursor().selectedText()

        if selected_text:
            # Добавляем разделитель
            menu.addSeparator()

            # Определяем, похоже ли выделение на URL
            is_url = (
                selected_text.startswith("http://")
                or selected_text.startswith("https://")
                or selected_text.startswith("www.")
            )

            if is_url:
                # Добавляем действие для открытия URL
                open_url_action = QAction(
                    tr("unified_chat_view.open_url", "Open URL"), self
                )
                open_url_action.triggered.connect(
                    lambda: self.url_open_requested.emit(selected_text)
                )
                menu.addAction(open_url_action)

            # Добавляем действия для работы с кодом
            insert_action = QAction(
                tr("unified_chat_view.insert_to_editor", "Insert to Editor"), self
            )
            insert_action.triggered.connect(
                lambda: self.code_insert_requested.emit(selected_text)
            )
            menu.addAction(insert_action)

            # Добавляем действие для запуска кода в терминале
            run_action = QAction(
                tr("unified_chat_view.run_in_terminal", "Run in Terminal"), self
            )
            run_action.triggered.connect(
                lambda: self.run_code_in_terminal.emit(selected_text)
            )
            menu.addAction(run_action)

        # Добавляем разделитель и пункт для вставки эмодзи
        menu.addSeparator()

        # Импортируем функцию для получения Lucide иконок
        from app.ui.lucide_icon_manager import get_lucide_icon

        emoji_action = QAction(tr("menu.insert_emoji", "Insert Emoji"), self)
        emoji_action.setIcon(get_lucide_icon("smile"))

        # Используем глобальную позицию курсора для отображения диалога
        global_pos = event.globalPos()
        emoji_action.triggered.connect(lambda: self._show_emoji_dialog(global_pos))
        menu.addAction(emoji_action)

        menu.exec(event.globalPos())

    def _show_emoji_dialog(self, position):
        """Показывает диалог выбора эмодзи."""
        try:
            from app.ui.emoji_dialog import EmojiDialog
            from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
            from PySide6.QtCore import QPoint

            # Проверяем, не readonly ли виджет
            if self.isReadOnly():
                return False

            # Проверяем тип позиции и преобразуем при необходимости
            if position and not isinstance(position, QPoint):
                position = QApplication.instance().cursor().pos()

            # Создаем диалог эмодзи
            dialog = EmojiDialog(self)

            # Подключаем сигнал для вставки эмодзи
            dialog.emoji_selected.connect(self.insertPlainText)

            # Позиционируем диалог
            if position:
                dialog_size = dialog.sizeHint()
                screen_geometry = QApplication.primaryScreen().geometry()

                # Расчитываем позицию так, чтобы диалог не выходил за пределы экрана
                x = min(position.x(), screen_geometry.width() - dialog_size.width())
                y = min(position.y(), screen_geometry.height() - dialog_size.height())

                dialog.move(x, y)

            # Показываем диалог
            result = dialog.exec()
            return result == QDialog.Accepted

        except Exception as e:
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.emoji_error", "Could not show emoji dialog: {error}").format(
                    error=str(e)
                ),
            )
            return False


class UnifiedChatView(QDialog):
    """
    Унифицированный интерфейс чата с поддержкой различных режимов работы.

    Объединяет функциональность Browsing Agent и Coding Agent в единый интерфейс
    с переключаемыми режимами.
    """

    def __init__(self, parent=None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.active_mode = MODE_BROWSING  # режим по умолчанию

        # Устанавливаем заголовок и размер окна
        self.setWindowTitle(tr("unified_chat_view.title", "Chat Assistant"))
        self.setWindowIcon(get_icon("chat"))
        self.resize(1400, 900)

        # Создаем интерфейсы агентов
        self.browser_agent_interface = BrowserAgentInterface(self)
        self.coding_agent_interface = CodingAgentInterface(self)

        # Создаем индексатор истории чата
        self.chat_indexer = ChatHistoryIndexer()

        # Инициализируем структуру для хранения истории сообщений
        self.chat_history_data = {
            "session_id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "messages": []
        }

        # Инициализируем UI
        self.init_ui()

        # Подключаем сигналы
        self.connect_signals()

        # Загружаем предыдущую историю сообщений
        self.load_chat_history()

    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        # Главный лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем панель переключения режимов
        self.mode_selector = QToolBar()
        self.mode_selector.setIconSize(QSize(24, 24))

        # Создаем кнопки переключения режимов
        self.browsing_mode_button = QPushButton(tr("chat_view.browsing_mode", "Browsing"))
        self.browsing_mode_button.setIcon(get_icon("browser"))
        self.browsing_mode_button.setCheckable(True)
        self.browsing_mode_button.setChecked(self.active_mode == MODE_BROWSING)

        self.coding_mode_button = QPushButton(tr("chat_view.coding_mode", "Coding"))
        self.coding_mode_button.setIcon(get_icon("code"))
        self.coding_mode_button.setCheckable(True)
        self.coding_mode_button.setChecked(self.active_mode == MODE_CODING)

        # Группируем кнопки
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.addButton(self.browsing_mode_button)
        self.mode_button_group.addButton(self.coding_mode_button)
        self.mode_button_group.buttonClicked.connect(self.on_mode_changed)

        # Добавляем кнопки на панель
        self.mode_selector.addWidget(self.browsing_mode_button)
        self.mode_selector.addWidget(self.coding_mode_button)

        main_layout.addWidget(self.mode_selector)

        # Создаем сплиттер для разделения контент-панели и чата
        self.splitter = QSplitter(Qt.Horizontal)

        # Контент-панель (StackedWidget для переключения между браузером и редактором)
        self.content_stack = QStackedWidget()

        # Создаем виджеты для разных режимов
        self.browser_widget = MultiBrowserWidget(self, self.theme_manager)
        self.editor_widget = MultiEditorWidget(self, self.theme_manager)

        # Добавляем виджеты в стек
        self.content_stack.addWidget(self.browser_widget)
        self.content_stack.addWidget(self.editor_widget)

        # Устанавливаем ссылки на виджеты в интерфейсы агентов
        self.browser_agent_interface.set_browser_widget(self.browser_widget)
        self.coding_agent_interface.set_editor_widget(self.editor_widget)

        # Правая часть - чат с агентом
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.setSpacing(10)

        # Заголовок чата (будет меняться в зависимости от режима)
        header_layout = QHBoxLayout()

        self.chat_header = QLabel(tr("chat_view.header", "Chat"))
        self.chat_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(self.chat_header, 1)  # 1 - растягивающий фактор

        # Кнопка поиска по истории (общая для всех режимов)
        self.search_history_button = QPushButton(tr("chat_view.search_history", "Search History"))
        self.search_history_button.setIcon(get_icon("search"))
        self.search_history_button.clicked.connect(self.open_search_dialog)
        header_layout.addWidget(self.search_history_button)

        # Кнопка экспорта истории (общая для всех режимов)
        self.export_button = QPushButton(tr("chat_view.export", "Export"))
        self.export_button.setIcon(get_icon("download"))
        self.export_button.clicked.connect(self.show_export_menu)
        header_layout.addWidget(self.export_button)

        chat_layout.addLayout(header_layout)

        # История чата с расширенным функционалом
        self.chat_history = ChatHistoryWidget(self)
        self.chat_history.setPlaceholderText(tr("chat_view.placeholder", "Chat with the assistant here..."))
        chat_layout.addWidget(self.chat_history)

        # Создаем панели инструментов для разных режимов

        # Панель инструментов для режима браузера
        self.browser_tools = QWidget()
        browser_tools_layout = QHBoxLayout(self.browser_tools)
        browser_tools_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки для режима браузера
        self.analyze_page_button = QPushButton(tr("chat_view.analyze_page", "Analyze Current Page"))
        self.analyze_page_button.setIcon(get_icon("search"))
        self.analyze_page_button.clicked.connect(self.analyze_current_page)
        browser_tools_layout.addWidget(self.analyze_page_button)

        self.search_page_button = QPushButton(tr("chat_view.search_page", "Search on Page"))
        self.search_page_button.setIcon(get_icon("search"))
        self.search_page_button.clicked.connect(self.search_on_current_page)
        browser_tools_layout.addWidget(self.search_page_button)

        # Панель инструментов для режима кодирования
        self.coding_tools = QWidget()
        coding_tools_layout = QHBoxLayout(self.coding_tools)
        coding_tools_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки для режима кодирования
        self.send_code_button = QPushButton(tr("chat_view.send_code", "Send Selected Code"))
        self.send_code_button.setIcon(get_icon("code"))
        self.send_code_button.clicked.connect(self.send_selected_code_to_chat)
        coding_tools_layout.addWidget(self.send_code_button)

        self.check_code_button = QPushButton(tr("chat_view.check_code", "Check Selected Code"))
        self.check_code_button.setIcon(get_icon("check"))
        self.check_code_button.clicked.connect(self.check_selected_code)
        coding_tools_layout.addWidget(self.check_code_button)

        # Стек панелей инструментов
        self.tools_stack = QStackedWidget()
        self.tools_stack.addWidget(self.browser_tools)
        self.tools_stack.addWidget(self.coding_tools)
        chat_layout.addWidget(self.tools_stack)

        # Прогресс-бар для индикации работы агента
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.progress_bar.setVisible(False)
        chat_layout.addWidget(self.progress_bar)

        # Индикатор статуса выполнения задачи
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        chat_layout.addWidget(self.status_label)

        # Поле ввода и кнопка отправки
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(tr("chat_view.input_placeholder", "Type your message here..."))
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton(tr("chat_view.send", "Send"))
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)

        # Кнопка остановки выполнения агента
        self.stop_button = QPushButton(tr("chat_view.stop", "Stop"))
        self.stop_button.clicked.connect(self.stop_agent)
        self.stop_button.setEnabled(False)
        chat_layout.addWidget(self.stop_button)

        # Добавляем виджеты в сплиттер
        self.splitter.addWidget(self.content_stack)
        self.splitter.addWidget(chat_widget)

        # Устанавливаем начальные размеры для сплиттера (70% слева, 30% справа)
        self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])

        # Добавляем сплиттер в основной лейаут
        main_layout.addWidget(self.splitter, 1)  # 1 - растягивающий фактор

        # Устанавливаем начальный режим
        self.set_mode(self.active_mode)

        # Применяем стили из текущей темы
        self.update_styles()

    def connect_signals(self):
        """Подключает сигналы и слоты."""
        # Сигналы от интерфейса браузерного агента
        self.browser_agent_interface.agent_message.connect(self.on_agent_message)
        self.browser_agent_interface.agent_error.connect(self.on_agent_error)
        self.browser_agent_interface.agent_thinking.connect(self.on_agent_thinking)
        self.browser_agent_interface.agent_finished.connect(self.on_agent_finished)

        # Сигналы от интерфейса агента кодирования
        self.coding_agent_interface.agent_message.connect(self.on_agent_message)
        self.coding_agent_interface.agent_error.connect(self.on_agent_error)
        self.coding_agent_interface.agent_thinking.connect(self.on_agent_thinking)
        self.coding_agent_interface.agent_finished.connect(self.on_agent_finished)

        # Сигналы от виджета истории чата
        self.chat_history.url_open_requested.connect(self.open_url)
        self.chat_history.code_insert_requested.connect(self.insert_code_to_editor)
        self.chat_history.run_code_in_terminal.connect(self.run_code_in_terminal)

        # Сигналы от браузера
        if hasattr(self.browser_widget, "page_title_changed"):
            self.browser_widget.page_title_changed.connect(self.on_page_title_changed)

        # Подключаем сигнал закрытия вкладки браузера к обработчику
        if hasattr(self.browser_widget, "tab_closed"):
            self.browser_widget.tab_closed.connect(self.on_browser_tab_closed)

        # Подключаем сигнал изменения темы
        if self.theme_manager:
            self.theme_manager.visualThemeChanged.connect(self.update_styles)

    @Slot(QAbstractButton)
    def on_mode_changed(self, button):
        """Обработчик изменения режима работы."""
        if button == self.browsing_mode_button:
            self.set_mode(MODE_BROWSING)
        elif button == self.coding_mode_button:
            self.set_mode(MODE_CODING)

    @Slot(str)
    def on_agent_message(self, message: str):
        """Обрабатывает сообщение от агента."""
        agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
        self.add_message_to_chat(agent_name, message)

    @Slot(str)
    def on_agent_error(self, error: str):
        """Обрабатывает сообщение об ошибке от агента."""
        agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
        self.add_message_to_chat(f"{agent_name} [Error]", error, is_error=True)
        self.on_agent_finished()

    @Slot(bool)
    def on_agent_thinking(self, is_thinking: bool):
        """Обрабатывает состояние обработки запроса агентом."""
        # Обновляем видимость прогресс-бара и статуса
        self.progress_bar.setVisible(is_thinking)
        self.status_label.setVisible(is_thinking)

        # Обновляем текст статуса
        if is_thinking:
            agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
            status_text = tr("chat_view.agent_thinking_status", "{agent_name} is processing your request...").format(
                agent_name=agent_name
            )
            self.status_label.setText(status_text)

            # Добавляем анимацию текста через таймер
            if not hasattr(self, "_status_timer"):
                self._status_timer = QTimer()
                self._status_timer.timeout.connect(self._update_status_animation)
                self._status_animation_dots = 0

            if not self._status_timer.isActive():
                self._status_timer.start(500)  # Обновление каждые 500 мс
        else:
            # Останавливаем анимацию статуса
            if hasattr(self, "_status_timer") and self._status_timer.isActive():
                self._status_timer.stop()

        # Обновляем состояние элементов управления
        self.message_input.setEnabled(not is_thinking)
        self.send_button.setEnabled(not is_thinking)
        self.stop_button.setEnabled(is_thinking)

        # Устанавливаем иконку для кнопки остановки
        if is_thinking:
            # Импортируем функцию для получения иконок
            from app.ui.icon_adapter import get_icon
            self.stop_button.setIcon(get_icon("stop"))

            # Добавляем сообщение о начале обработки в чат
            agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
            self.add_message_to_chat(
                "System",
                tr("chat_view.agent_thinking", "{agent_name} is processing your request...").format(agent_name=agent_name),
                is_progress=True
            )
        else:
            self.stop_button.setIcon(QIcon())  # Убираем иконку

        # Отключаем кнопки инструментов в зависимости от режима
        if self.active_mode == MODE_BROWSING:
            self.analyze_page_button.setEnabled(not is_thinking)
            self.search_page_button.setEnabled(not is_thinking)
        elif self.active_mode == MODE_CODING:
            self.send_code_button.setEnabled(not is_thinking)
            self.check_code_button.setEnabled(not is_thinking)

    def _update_status_animation(self):
        """Обновляет анимацию текста статуса."""
        if not hasattr(self, "_status_animation_dots"):
            self._status_animation_dots = 0

        self._status_animation_dots = (self._status_animation_dots + 1) % 4
        dots = "." * self._status_animation_dots

        agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
        status_text = tr("chat_view.agent_thinking_status", "{agent_name} is processing your request").format(
            agent_name=agent_name
        )

        self.status_label.setText(f"{status_text}{dots}")

    @Slot()
    def on_agent_finished(self):
        """Обрабатывает завершение работы агента."""
        self.progress_bar.setVisible(False)
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Включаем кнопки инструментов
        if self.active_mode == MODE_BROWSING:
            self.analyze_page_button.setEnabled(True)
            self.search_page_button.setEnabled(True)
        elif self.active_mode == MODE_CODING:
            self.send_code_button.setEnabled(True)
            self.check_code_button.setEnabled(True)

    @Slot(str, str)
    def on_page_title_changed(self, url: str, title: str):
        """Обрабатывает изменение заголовка страницы браузера."""
        if self.active_mode == MODE_BROWSING:
            self.add_message_to_chat(
                "Browser", f"Page loaded: {title} ({url})", is_progress=True
            )

    def add_message_to_chat(
        self,
        sender: str,
        message: str,
        is_error: bool = False,
        is_progress: bool = False,
    ):
        """Добавляет сообщение в историю чата."""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Получаем текущее время и форматируем его
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        timestamp = f"{current_time} {current_date}"

        # Получаем цвета из темы для адаптации стилей
        timestamp_color = "#888888"  # Цвет по умолчанию
        if self.theme_manager:
            timestamp_color = self.theme_manager.get_color("text_secondary", timestamp_color)

        if is_error:
            self.chat_history.insertHtml(
                f"<p><b style='color: red;'>{sender}:</b> {message} <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
            )
        elif is_progress:
            self.chat_history.insertHtml(
                f"<p><i style='color: gray;'>{sender}: {message}</i> <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
            )
        else:
            self.chat_history.insertHtml(
                f"<p><b>{sender}:</b> {message} <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
            )

        # Прокручиваем чат вниз
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

        # Сохраняем сообщение в структуре данных
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": f"{current_date} {current_time}",
            "is_error": is_error,
            "is_progress": is_progress,
            "mode": self.active_mode  # Сохраняем текущий режим
        }
        self.chat_history_data["messages"].append(message_data)

        # Автоматически сохраняем историю после каждого сообщения
        self.save_chat_history()

        # Добавляем сообщение в индекс
        self.chat_indexer.add_message(
            session_id=self.chat_history_data["session_id"],
            sender=sender,
            message=message,
            timestamp=f"{current_date} {current_time}",
            is_error=is_error,
            is_progress=is_progress,
            metadata={"mode": self.active_mode}  # Добавляем режим в метаданные
        )

    def send_message(self):
        """Отправляет сообщение агенту."""
        message = self.message_input.text().strip()
        if not message:
            return

        # Отображаем сообщение в чате
        self.add_message_to_chat("You", message)

        # Очищаем поле ввода
        self.message_input.clear()

        # Отправляем сообщение соответствующему агенту в зависимости от режима
        if self.active_mode == MODE_BROWSING:
            self.browser_agent_interface.process_user_query(message)
        elif self.active_mode == MODE_CODING:
            self.coding_agent_interface.process_user_query(message)

    def stop_agent(self):
        """Останавливает выполнение агента."""
        if self.active_mode == MODE_BROWSING:
            self.browser_agent_interface.stop_agent()
        elif self.active_mode == MODE_CODING:
            self.coding_agent_interface.stop_agent()

        # Добавляем сообщение в чат о том, что агент остановлен
        agent_name = "Browsing Agent" if self.active_mode == MODE_BROWSING else "Coding Agent"
        self.add_message_to_chat(
            "System",
            tr("chat_view.agent_stopped", "{agent_name} was stopped by user").format(agent_name=agent_name),
            is_progress=True
        )

        # Убедимся, что UI обновлен
        self.on_agent_finished()

    # Методы для режима браузера
    def analyze_current_page(self):
        """Запрашивает анализ текущей страницы у агента."""
        if self.active_mode != MODE_BROWSING:
            return

        # Получаем текущую страницу и URL
        current_url = self.browser_widget.get_current_url()
        if not current_url:
            self.add_message_to_chat(
                "System",
                tr("chat_view.no_page_loaded", "No page is currently loaded"),
                is_progress=True,
            )
            return

        # Добавляем в чат
        self.add_message_to_chat(
            "You",
            tr("chat_view.analyze_page_prompt", f"Please analyze the current page: {current_url}"),
        )

        # Отправляем агенту запрос на анализ страницы
        prompt = f"Please analyze the current page: {current_url}"
        self.browser_agent_interface.process_user_query(prompt)

    def search_on_current_page(self):
        """Запрашивает у пользователя текст для поиска и отправляет запрос агенту."""
        if self.active_mode != MODE_BROWSING:
            return

        # Показываем диалог для ввода поискового запроса
        search_text, ok = QInputDialog.getText(
            self,
            tr("chat_view.search_prompt_title", "Search on Page"),
            tr("chat_view.search_prompt", "Enter text to search on the current page:"),
        )

        if ok and search_text:
            # Добавляем в чат
            self.add_message_to_chat(
                "You",
                tr("chat_view.search_page_prompt", f"Please search for '{search_text}' on the current page"),
            )

            # Отправляем агенту запрос на поиск на странице
            prompt = f"Please search for '{search_text}' on the current page and tell me what you find"
            self.browser_agent_interface.process_user_query(prompt)

    def open_url(self, url: str):
        """Открывает URL в браузере."""
        if self.active_mode != MODE_BROWSING:
            self.set_mode(MODE_BROWSING)

        # Проверяем и форматируем URL
        if not (url.startswith("http://") or url.startswith("https://")):
            if url.startswith("www."):
                url = "https://" + url
            else:
                url = "https://" + url

        # Открываем URL в браузере
        self.browser_widget.load_url(url)

        # Уведомление
        self.add_message_to_chat(
            "System",
            tr("chat_view.url_opened", f"Opening URL: {url}"),
            is_progress=True,
        )

    # Методы для режима кодирования
    def send_selected_code_to_chat(self):
        """Отправляет выделенный код из редактора в чат."""
        if self.active_mode != MODE_CODING:
            return

        try:
            # Получаем выделенный текст из текущего редактора
            selected_text = self.editor_widget.get_selected_text()

            if not selected_text:
                # Если ничего не выделено, показываем сообщение
                QMessageBox.information(
                    self,
                    tr("chat_view.info", "Information"),
                    tr("chat_view.no_selection", "No text selected in the editor.")
                )
                return

            # Добавляем выделенный код в чат
            self.add_message_to_chat("You", f"```\n{selected_text}\n```")

            # Отправляем агенту запрос на анализ кода
            prompt = f"I'm sending you this code:\n\n```\n{selected_text}\n```\n\nPlease analyze it."
            self.coding_agent_interface.process_user_query(prompt)

        except Exception as e:
            logger.error(f"Error sending selected code to chat: {e}")
            self.add_message_to_chat(
                "System",
                tr("chat_view.send_code_error", f"Error sending code: {str(e)}"),
                is_error=True
            )

    def check_selected_code(self):
        """Проверяет выделенный код из редактора."""
        if self.active_mode != MODE_CODING:
            return

        try:
            # Получаем выделенный текст из текущего редактора
            selected_text = self.editor_widget.get_selected_text()

            if not selected_text:
                # Если ничего не выделено, показываем сообщение
                QMessageBox.information(
                    self,
                    tr("chat_view.info", "Information"),
                    tr("chat_view.no_selection", "No text selected in the editor.")
                )
                return

            # Добавляем выделенный код в чат
            self.add_message_to_chat("You", f"```\n{selected_text}\n```\nPlease check this code for errors or improvements.")

            # Отправляем агенту запрос на проверку кода
            prompt = f"I'm sending you this code:\n\n```\n{selected_text}\n```\n\nPlease check for errors or improvements."
            self.coding_agent_interface.process_user_query(prompt)

        except Exception as e:
            logger.error(f"Error checking selected code: {e}")
            self.add_message_to_chat(
                "System",
                tr("chat_view.check_code_error", f"Error checking code: {str(e)}"),
                is_error=True
            )

    def insert_code_to_editor(self, code: str):
        """Вставляет код в редактор."""
        if self.active_mode != MODE_CODING:
            # Переключаемся в режим кодирования, если не активен
            self.set_mode(MODE_CODING)

        try:
            self.editor_widget.insert_code(code)
            self.add_message_to_chat(
                "System",
                tr("chat_view.code_inserted", "Code inserted into editor."),
                is_progress=True
            )
        except Exception as e:
            logger.error(f"Error inserting code to editor: {e}")
            self.add_message_to_chat(
                "System",
                tr("chat_view.insert_code_error", f"Error inserting code: {str(e)}"),
                is_error=True
            )

    def run_code_in_terminal(self, code: str):
        """Запускает код в терминале."""
        try:
            # Эмитируем сигнал для запуска кода в терминале
            # (предполагается, что главное окно обрабатывает этот сигнал)
            if hasattr(self.parent(), "run_code_in_terminal"):
                self.parent().run_code_in_terminal(code)
                self.add_message_to_chat(
                    "System",
                    tr("chat_view.code_sent_to_terminal", "Code sent to terminal."),
                    is_progress=True
                )
            else:
                logger.warning("Parent window does not have run_code_in_terminal method")
                self.add_message_to_chat(
                    "System",
                    tr("chat_view.terminal_not_available", "Terminal functionality not available."),
                    is_error=True
                )
        except Exception as e:
            logger.error(f"Error running code in terminal: {e}")
            self.add_message_to_chat(
                "System",
                tr("chat_view.run_code_error", f"Error running code: {str(e)}"),
                is_error=True
            )

    # Методы для работы с историей чата
    def open_search_dialog(self):
        """Открывает диалог поиска по истории чатов."""
        try:
            # Создаем диалог поиска
            search_dialog = ChatSearchDialog(self, self.theme_manager)

            # Подключаем сигнал выбора сообщения, если нужно
            # search_dialog.message_selected.connect(self.on_search_message_selected)

            # Показываем диалог
            search_dialog.exec()

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("chat_view.search_dialog_error", f"Error opening search dialog: {str(e)}"),
                is_error=True
            )

    def show_export_menu(self):
        """Показывает меню для выбора формата экспорта истории."""
        export_menu = QMenu(self)

        json_action = QAction(tr("chat_view.export_json", "Export as JSON"), self)
        json_action.triggered.connect(lambda: self.export_chat_history("json"))
        export_menu.addAction(json_action)

        txt_action = QAction(tr("chat_view.export_txt", "Export as TXT"), self)
        txt_action.triggered.connect(lambda: self.export_chat_history("txt"))
        export_menu.addAction(txt_action)

        html_action = QAction(tr("chat_view.export_html", "Export as HTML"), self)
        html_action.triggered.connect(lambda: self.export_chat_history("html"))
        export_menu.addAction(html_action)

        # Показываем меню под кнопкой экспорта
        export_menu.exec(self.export_button.mapToGlobal(QPoint(0, self.export_button.height())))

    def save_chat_history(self):
        """Сохраняет историю чата в JSON файл."""
        try:
            # Определяем директорию для хранения истории чатов
            history_dir = os.path.join(os.path.expanduser("~"), ".gopi_ai", "chat_history")

            # Создаем директорию, если она не существует
            os.makedirs(history_dir, exist_ok=True)

            # Путь к файлу с историей текущей сессии
            history_file = os.path.join(history_dir, f"unified_chat_{self.chat_history_data['session_id']}.json")

            # Сохраняем данные в JSON файл
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history_data, f, ensure_ascii=False, indent=2)

            # Экспортируем в TXT для удобства чтения
            self.chat_indexer.export_session_to_txt(self.chat_history_data['session_id'])

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("chat_view.save_history_error", f"Error saving chat history: {str(e)}"),
                is_error=True
            )

    def load_chat_history(self):
        """Загружает последнюю историю чата, если она существует."""
        try:
            # Директория с историей чатов
            history_dir = os.path.join(os.path.expanduser("~"), ".gopi_ai", "chat_history")

            if not os.path.exists(history_dir):
                return

            # Ищем файлы истории унифицированного чата
            history_files = [
                os.path.join(history_dir, f)
                for f in os.listdir(history_dir)
                if f.startswith("unified_chat_") and f.endswith(".json")
            ]

            if not history_files:
                return

            # Сортируем по времени модификации (от новых к старым)
            history_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

            # Загружаем самый последний файл
            with open(history_files[0], 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)

            # Восстанавливаем сообщения в интерфейсе
            self.restore_chat_messages(loaded_history)

            # Индексируем историю, если она еще не проиндексирована
            self.chat_indexer.import_from_json(history_files[0])

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("chat_view.load_history_error", f"Error loading chat history: {str(e)}"),
                is_error=True
            )

    def restore_chat_messages(self, history_data: Dict):
        """Восстанавливает сообщения чата из загруженных данных."""
        # Очищаем текущие сообщения в интерфейсе
        self.chat_history.clear()

        # Устанавливаем данные истории
        self.chat_history_data = history_data

        # Восстанавливаем сообщения в интерфейсе без добавления в историю
        for msg in history_data.get("messages", []):
            cursor = self.chat_history.textCursor()
            cursor.movePosition(QTextCursor.End)

            timestamp = msg.get("timestamp", "")
            sender = msg.get("sender", "")
            message = msg.get("message", "")
            is_error = msg.get("is_error", False)
            is_progress = msg.get("is_progress", False)
            mode = msg.get("mode", MODE_BROWSING)  # Получаем режим из сообщения

            # Получаем цвета из темы
            timestamp_color = "#888888"  # Цвет по умолчанию
            if self.theme_manager:
                timestamp_color = self.theme_manager.get_color("text_secondary", timestamp_color)

            if is_error:
                self.chat_history.insertHtml(
                    f"<p><b style='color: red;'>{sender}:</b> {message} <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
                )
            elif is_progress:
                self.chat_history.insertHtml(
                    f"<p><i style='color: gray;'>{sender}: {message}</i> <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
                )
            else:
                self.chat_history.insertHtml(
                    f"<p><b>{sender}:</b> {message} <span style='font-size: 0.8em; color: {timestamp_color};'>[{timestamp}]</span></p>"
                )

        # Прокручиваем чат вниз
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

        # Если последнее сообщение было от определенного режима, устанавливаем этот режим
        if history_data.get("messages"):
            last_message = history_data["messages"][-1]
            last_mode = last_message.get("mode", MODE_BROWSING)
            self.set_mode(last_mode)

    def export_chat_history(self, format_type="json"):
        """Экспортирует историю чата в файл выбранного формата."""
        try:
            # Определяем начальную директорию для диалога сохранения
            default_dir = os.path.expanduser("~")

            # Получаем путь для сохранения через диалог
            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)

            if format_type == "json":
                file_dialog.setNameFilter("JSON Files (*.json)")
                default_filename = f"unified_chat_history_{self.chat_history_data['session_id']}.json"
            elif format_type == "txt":
                file_dialog.setNameFilter("Text Files (*.txt)")
                default_filename = f"unified_chat_history_{self.chat_history_data['session_id']}.txt"
            elif format_type == "html":
                file_dialog.setNameFilter("HTML Files (*.html)")
                default_filename = f"unified_chat_history_{self.chat_history_data['session_id']}.html"
            else:
                return

            file_dialog.selectFile(os.path.join(default_dir, default_filename))

            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]

                if format_type == "json":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.chat_history_data, f, ensure_ascii=False, indent=2)
                elif format_type == "txt":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for msg in self.chat_history_data.get("messages", []):
                            f.write(f"[{msg.get('timestamp')}] {msg.get('sender')}: {msg.get('message')}\n")
                elif format_type == "html":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("<html><head><title>Unified Chat History</title>")
                        f.write("<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;}")
                        f.write(".message{margin-bottom:10px;}.sender{font-weight:bold;}")
                        f.write(".timestamp{font-size:0.8em;color:#888;}.error{color:red;}.progress{color:gray;font-style:italic;}")
                        f.write(".browsing{background-color:#f0f8ff;}.coding{background-color:#f0fff0;}")
                        f.write("</style></head><body><h1>Unified Chat History</h1>")

                        for msg in self.chat_history_data.get("messages", []):
                            mode_class = ""
                            if msg.get("mode") == MODE_BROWSING:
                                mode_class = "browsing"
                            elif msg.get("mode") == MODE_CODING:
                                mode_class = "coding"

                            cls = ""
                            if msg.get("is_error", False):
                                cls = "error"
                            elif msg.get("is_progress", False):
                                cls = "progress"

                            f.write(f"<div class='message {cls} {mode_class}'>")
                            f.write(f"<span class='sender'>{msg.get('sender')}:</span> ")
                            f.write(f"{msg.get('message')} ")
                            f.write(f"<span class='timestamp'>[{msg.get('timestamp')}]</span>")
                            if mode_class:
                                f.write(f" <span class='mode'>[{mode_class}]</span>")
                            f.write("</div>")

                        f.write("</body></html>")

                self.add_message_to_chat(
                    "System",
                    tr("chat_view.export_success", f"Chat history exported to {file_path}"),
                    is_progress=True
                )

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("chat_view.export_error", f"Error exporting chat history: {str(e)}"),
                is_error=True
            )

    def update_styles(self):
        """Обновляет стили элементов интерфейса в соответствии с текущей темой."""
        if not self.theme_manager:
            return

        # Получаем цвета из текущей темы
        bg_color = self.theme_manager.get_color("background", "#2D2D2D")
        text_color = self.theme_manager.get_color("foreground", "#EAEAEA")
        secondary_bg = self.theme_manager.get_color("secondary_background", "#3C3C3C")
        border_color = self.theme_manager.get_color("border", "#444444")
        accent_color = self.theme_manager.get_color("accent", "#3498db")
        error_color = self.theme_manager.get_color("error", "#e74c3c")
        success_color = self.theme_manager.get_color("success", "#2ecc71")

        # Применяем стили к виджету истории чата
        self.chat_history.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; }}"
        )

        # Применяем стили к полю ввода
        self.message_input.setStyleSheet(
            f"QLineEdit {{ background-color: {secondary_bg}; color: {text_color}; border: 1px solid {border_color}; }}"
        )

        # Применяем стили к кнопке остановки
        self.stop_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {error_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:disabled {{
                background-color: #7f8c8d;
                color: #bdc3c7;
            }}
            """
        )

        # Применяем стили к прогресс-бару
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                background-color: {secondary_bg};
                text-align: center;
                color: {text_color};
                font-weight: bold;
                height: 6px;
                min-height: 6px;
                max-height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 3px;
            }}
            """
        )

        # Применяем стили к метке статуса
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {accent_color};
                font-weight: bold;
                padding: 3px;
                background-color: {bg_color};
                border-radius: 3px;
            }}
            """
        )

    def closeEvent(self, event):
        """Обрабатывает закрытие диалога."""
        # Останавливаем работу агентов
        self.browser_agent_interface.stop_agent()
        self.coding_agent_interface.stop_agent()

        # Сохраняем историю сообщений
        self.save_chat_history()

        # Запускаем очистку ресурсов агентов
        asyncio.create_task(self.cleanup())

        # Закрываем диалог
        super().closeEvent(event)

    async def cleanup(self):
        """Очищает ресурсы перед закрытием диалога."""
        await self.browser_agent_interface.cleanup()
        await self.coding_agent_interface.cleanup()

    @Slot(int, QWidget)
    def on_browser_tab_closed(self, tab_index, tab_widget):
        """
        Обрабатывает закрытие вкладки браузера.

        Args:
            tab_index: Индекс закрываемой вкладки
            tab_widget: Виджет закрываемой вкладки
        """
        if self.active_mode == MODE_BROWSING:
            # Добавляем сообщение в чат о закрытии вкладки
            tab_url = ""
            if hasattr(tab_widget, "get_current_url"):
                tab_url = tab_widget.get_current_url()
            elif hasattr(tab_widget, "browser") and hasattr(tab_widget.browser, "get_current_url"):
                tab_url = tab_widget.browser.get_current_url()

            if tab_url:
                self.add_message_to_chat(
                    "System",
                    tr("chat_view.tab_closed", "Tab with URL: {url} was closed").format(url=tab_url),
                    is_progress=True
                )

            # Запускаем очистку ресурсов вкладки в браузерном интерфейсе
            asyncio.create_task(self.browser_agent_interface.cleanup_tab(tab_index, tab_widget))

    def set_mode(self, mode):
        """
        Устанавливает текущий режим работы чата.

        Args:
            mode: Строка, идентифицирующая режим (MODE_BROWSING или MODE_CODING)
        """
        self.active_mode = mode

        # Обновляем UI в соответствии с режимом
        if mode == MODE_BROWSING:
            self.content_stack.setCurrentWidget(self.browser_widget)
            self.tools_stack.setCurrentWidget(self.browser_tools)
            self.chat_header.setText(tr("chat_view.browsing_header", "Browsing Agent Chat"))
            self.browsing_mode_button.setChecked(True)
        elif mode == MODE_CODING:
            self.content_stack.setCurrentWidget(self.editor_widget)
            self.tools_stack.setCurrentWidget(self.coding_tools)
            self.chat_header.setText(tr("chat_view.coding_header", "Coding Agent Chat"))
            self.coding_mode_button.setChecked(True)
