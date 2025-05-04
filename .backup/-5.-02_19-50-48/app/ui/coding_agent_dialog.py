import asyncio
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit,
    QPushButton, QLineEdit, QLabel, QProgressBar, QMessageBox,
    QSizePolicy, QWidget, QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QPoint
from PySide6.QtGui import QIcon, QTextCursor, QCloseEvent, QAction, QContextMenuEvent

from app.ui.code_editor_widget import MultiEditorWidget
from app.ui.coding_agent_interface import CodingAgentInterface
from app.ui.i18n.translator import tr
from app.ui.icon_manager import get_icon
from app.ui.theme_manager import ThemeManager


class ChatHistoryWidget(QTextEdit):
    """
    Виджет истории чата с расширенным функционалом.

    Добавляет контекстное меню для копирования и вставки кода.
    """
    code_insert_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Переопределяем стандартное контекстное меню."""
        menu = self.createStandardContextMenu()

        # Получаем выделенный текст
        selected_text = self.textCursor().selectedText()

        if selected_text:
            # Добавляем разделитель
            menu.addSeparator()

            # Добавляем действие для вставки кода в редактор
            insert_action = QAction(tr("coding_agent_dialog.insert_to_editor", "Insert to Editor"), self)
            insert_action.triggered.connect(lambda: self.code_insert_requested.emit(selected_text))
            menu.addAction(insert_action)

            # Добавляем действие для запуска кода в терминале
            run_action = QAction(tr("coding_agent_dialog.run_in_terminal", "Run in Terminal"), self)
            run_action.triggered.connect(lambda: self.run_in_terminal(selected_text))
            menu.addAction(run_action)

        menu.exec_(event.globalPos())

    def run_in_terminal(self, code: str):
        """Отправляет код на выполнение в терминал."""
        # Пока просто эмулируем, реальная реализация будет добавлена позже
        self.parent().add_message_to_chat("System", tr("coding_agent_dialog.terminal_run", "Code sent to terminal"), is_progress=True)


class CodingAgentDialog(QDialog):
    """
    Диалог для взаимодействия с агентом кодирования.

    Содержит редактор кода и интерфейс для общения с агентом,
    который может помогать с редактированием, анализом и запуском кода.
    """

    def __init__(self, parent=None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Устанавливаем заголовок и размер окна
        self.setWindowTitle(tr("coding_agent_dialog.title", "Coding Agent"))
        self.setWindowIcon(get_icon("code"))
        self.resize(1200, 800)

        # Создаем интерфейс агента
        self.agent_interface = CodingAgentInterface(self)

        # Инициализируем UI
        self.init_ui()

        # Подключаем сигналы
        self.connect_signals()

    def init_ui(self):
        """Инициализирует интерфейс пользователя."""
        # Главный лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем сплиттер для разделения редактора и чата
        self.splitter = QSplitter(Qt.Horizontal)

        # Левая часть - редактор кода
        self.editor_widget = MultiEditorWidget(self, self.theme_manager)

        # Устанавливаем ссылку на редактор в интерфейс агента
        self.agent_interface.set_editor_widget(self.editor_widget)

        # Правая часть - чат с агентом
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.setSpacing(10)

        # Заголовок чата
        chat_header = QLabel(tr("coding_agent_dialog.chat_header", "Coding Agent Chat"))
        chat_header.setAlignment(Qt.AlignCenter)
        chat_layout.addWidget(chat_header)

        # История чата с расширенным функционалом
        self.chat_history = ChatHistoryWidget(self)
        self.chat_history.setPlaceholderText(
            tr("coding_agent_dialog.chat_placeholder", "Chat with the coding agent here...")
        )
        chat_layout.addWidget(self.chat_history)

        # Панель инструментов для взаимодействия с кодом
        code_actions_layout = QHBoxLayout()

        # Кнопка для отправки выделенного кода в чат
        self.send_code_button = QPushButton(tr("coding_agent_dialog.send_code", "Send Code to Chat"))
        self.send_code_button.setIcon(get_icon("send_to_chat"))
        self.send_code_button.clicked.connect(self.send_selected_code_to_chat)
        code_actions_layout.addWidget(self.send_code_button)

        # Кнопка для проверки кода
        self.check_code_button = QPushButton(tr("coding_agent_dialog.check_code", "Check Code"))
        self.check_code_button.setIcon(get_icon("check"))
        self.check_code_button.clicked.connect(self.check_selected_code)
        code_actions_layout.addWidget(self.check_code_button)

        chat_layout.addLayout(code_actions_layout)

        # Прогресс-бар для индикации работы агента
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.progress_bar.setVisible(False)
        chat_layout.addWidget(self.progress_bar)

        # Поле ввода и кнопка отправки
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            tr("coding_agent_dialog.input_placeholder", "Type your message here...")
        )
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton(tr("coding_agent_dialog.send", "Send"))
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)

        # Кнопка остановки выполнения агента
        self.stop_button = QPushButton(tr("coding_agent_dialog.stop", "Stop"))
        self.stop_button.clicked.connect(self.stop_agent)
        self.stop_button.setEnabled(False)
        chat_layout.addWidget(self.stop_button)

        # Добавляем виджеты в сплиттер
        self.splitter.addWidget(self.editor_widget)
        self.splitter.addWidget(chat_widget)

        # Устанавливаем начальные размеры для сплиттера (70% слева, 30% справа)
        self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])

        # Добавляем сплиттер в основной лейаут
        main_layout.addWidget(self.splitter)

    def connect_signals(self):
        """Подключает сигналы и слоты."""
        # Подключаем сигналы от интерфейса агента к UI
        self.agent_interface.agent_message.connect(self.on_agent_message)
        self.agent_interface.agent_error.connect(self.on_agent_error)
        self.agent_interface.agent_thinking.connect(self.on_agent_thinking)
        self.agent_interface.agent_finished.connect(self.on_agent_finished)

        # Подключаем сигналы от редактора
        self.editor_widget.progress_update.connect(self.on_editor_progress)

        # Подключаем сигналы от виджета истории чата
        self.chat_history.code_insert_requested.connect(self.insert_code_to_editor)

    @Slot(str)
    def on_agent_message(self, message: str):
        """Обрабатывает сообщение от агента."""
        self.add_message_to_chat("Agent", message)

    @Slot(str)
    def on_agent_error(self, error: str):
        """Обрабатывает сообщение об ошибке от агента."""
        self.add_message_to_chat("Agent [Error]", error, is_error=True)
        self.on_agent_finished()

    @Slot(bool)
    def on_agent_thinking(self, is_thinking: bool):
        """Обрабатывает состояние обработки запроса агентом."""
        self.progress_bar.setVisible(is_thinking)
        self.message_input.setEnabled(not is_thinking)
        self.send_button.setEnabled(not is_thinking)
        self.stop_button.setEnabled(is_thinking)

    @Slot()
    def on_agent_finished(self):
        """Обрабатывает завершение работы агента."""
        self.progress_bar.setVisible(False)
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @Slot(str)
    def on_editor_progress(self, message: str):
        """Обрабатывает сообщения о прогрессе от редактора."""
        self.add_message_to_chat("Editor", message, is_progress=True)

    def add_message_to_chat(self, sender: str, message: str, is_error: bool = False, is_progress: bool = False):
        """Добавляет сообщение в историю чата."""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)

        if is_error:
            self.chat_history.insertHtml(f"<p><b style='color: red;'>{sender}:</b> {message}</p>")
        elif is_progress:
            self.chat_history.insertHtml(f"<p><i style='color: gray;'>{sender}: {message}</i></p>")
        else:
            self.chat_history.insertHtml(f"<p><b>{sender}:</b> {message}</p>")

        # Прокручиваем чат вниз
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def send_message(self):
        """Отправляет сообщение агенту."""
        message = self.message_input.text().strip()
        if not message:
            return

        # Отображаем сообщение в чате
        self.add_message_to_chat("You", message)

        # Очищаем поле ввода
        self.message_input.clear()

        # Отправляем сообщение агенту
        self.agent_interface.process_user_query(message)

    def stop_agent(self):
        """Останавливает выполнение агента."""
        self.agent_interface.stop_agent()

    def send_selected_code_to_chat(self):
        """Отправляет выделенный в редакторе код в чат."""
        # Получаем текущий редактор и выделенный текст
        editor = self.editor_widget.tabs.currentWidget()
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.add_message_to_chat("System", tr("coding_agent_dialog.no_selected_code", "No code selected"), is_progress=True)
            return

        # Форматируем сообщение с кодом
        formatted_message = f"```\n{selected_text}\n```"

        # Добавляем в чат
        self.add_message_to_chat("You", formatted_message)

        # Отправляем агенту запрос на анализ кода
        prompt = tr("coding_agent_dialog.analyze_code_prompt", "Please analyze the following code and provide feedback:")
        self.agent_interface.process_user_query(f"{prompt}\n{formatted_message}")

    def check_selected_code(self):
        """Проверяет выделенный код на ошибки."""
        # Получаем текущий редактор и выделенный текст
        editor = self.editor_widget.tabs.currentWidget()
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.add_message_to_chat("System", tr("coding_agent_dialog.no_selected_code", "No code selected"), is_progress=True)
            return

        # Форматируем сообщение с кодом
        formatted_message = f"```\n{selected_text}\n```"

        # Добавляем в чат
        self.add_message_to_chat("You", tr("coding_agent_dialog.check_code_prompt", "Please check this code for errors:"))
        self.add_message_to_chat("You", formatted_message)

        # Отправляем агенту запрос на проверку кода
        prompt = tr("coding_agent_dialog.check_code_prompt", "Please check this code for errors and suggest improvements:")
        self.agent_interface.process_user_query(f"{prompt}\n{formatted_message}")

    def insert_code_to_editor(self, code: str):
        """Вставляет код из чата в текущий редактор."""
        # Получаем текущий редактор
        editor = self.editor_widget.tabs.currentWidget()
        if not editor:
            # Создаем новую вкладку, если нет открытых
            editor = self.editor_widget.add_new_tab()

        # Вставляем код в позицию курсора
        editor.insertPlainText(code)

        # Уведомление
        self.add_message_to_chat("System", tr("coding_agent_dialog.code_inserted", "Code inserted to editor"), is_progress=True)

    def closeEvent(self, event: QCloseEvent):
        """Обрабатывает закрытие диалога."""
        # Останавливаем работу агента
        self.agent_interface.stop_agent()

        # Запускаем очистку ресурсов агента
        asyncio.create_task(self.cleanup())

        # Закрываем диалог
        super().closeEvent(event)

    async def cleanup(self):
        """Очищает ресурсы перед закрытием диалога."""
        await self.agent_interface.cleanup()
