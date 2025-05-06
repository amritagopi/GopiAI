import asyncio
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit,
    QPushButton, QLineEdit, QLabel, QProgressBar, QMessageBox,
    QSizePolicy, QWidget, QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QPoint
from PySide6.QtGui import QIcon, QTextCursor, QCloseEvent, QAction, QContextMenuEvent

from app.ui.browser_tab_widget import MultiBrowserWidget
from app.ui.browser_agent_interface import BrowserAgentInterface
from app.ui.i18n.translator import tr
from app.ui.icon_manager import get_icon
from app.ui.theme_manager import ThemeManager


class ChatHistoryWidget(QTextEdit):
    """
    Виджет истории чата с расширенным функционалом.

    Добавляет контекстное меню для копирования и специальных действий.
    """
    url_open_requested = Signal(str)

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

            # Определяем, похоже ли выделение на URL
            is_url = (
                selected_text.startswith("http://") or
                selected_text.startswith("https://") or
                selected_text.startswith("www.")
            )

            if is_url:
                # Добавляем действие для открытия URL
                open_url_action = QAction(tr("browser_agent_dialog.open_url", "Open URL"), self)
                open_url_action.triggered.connect(lambda: self.url_open_requested.emit(selected_text))
                menu.addAction(open_url_action)

        menu.exec_(event.globalPos())


class BrowserAgentDialog(QDialog):
    """
    Диалог для взаимодействия с агентом браузера.

    Содержит встроенный браузер и интерфейс для общения с агентом,
    который может помогать с навигацией, поиском и извлечением данных из веб-страниц.
    """

    def __init__(self, parent=None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Устанавливаем заголовок и размер окна
        self.setWindowTitle(tr("browser_agent_dialog.title", "Browsing Agent"))
        self.setWindowIcon(get_icon("browser"))
        self.resize(1400, 900)

        # Создаем интерфейс агента
        self.agent_interface = BrowserAgentInterface(self)

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

        # Создаем сплиттер для разделения браузера и чата
        self.splitter = QSplitter(Qt.Horizontal)

        # Левая часть - браузер
        self.browser_widget = MultiBrowserWidget(self, self.theme_manager)

        # Устанавливаем ссылку на браузер в интерфейс агента
        self.agent_interface.set_browser_widget(self.browser_widget)

        # Правая часть - чат с агентом
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.setSpacing(10)

        # Заголовок чата
        chat_header = QLabel(tr("browser_agent_dialog.chat_header", "Browsing Agent Chat"))
        chat_header.setAlignment(Qt.AlignCenter)
        chat_layout.addWidget(chat_header)

        # История чата с расширенным функционалом
        self.chat_history = ChatHistoryWidget(self)
        self.chat_history.setPlaceholderText(
            tr("browser_agent_dialog.chat_placeholder", "Chat with the browsing agent here...")
        )
        chat_layout.addWidget(self.chat_history)

        # Панель инструментов для взаимодействия с браузером
        browser_actions_layout = QHBoxLayout()

        # Кнопка для анализа текущей страницы
        self.analyze_page_button = QPushButton(tr("browser_agent_dialog.analyze_page", "Analyze Current Page"))
        self.analyze_page_button.setIcon(get_icon("analyze"))
        self.analyze_page_button.clicked.connect(self.analyze_current_page)
        browser_actions_layout.addWidget(self.analyze_page_button)

        # Кнопка для поиска на странице
        self.search_page_button = QPushButton(tr("browser_agent_dialog.search_page", "Search on Page"))
        self.search_page_button.setIcon(get_icon("search"))
        self.search_page_button.clicked.connect(self.search_on_current_page)
        browser_actions_layout.addWidget(self.search_page_button)

        chat_layout.addLayout(browser_actions_layout)

        # Прогресс-бар для индикации работы агента
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.progress_bar.setVisible(False)
        chat_layout.addWidget(self.progress_bar)

        # Поле ввода и кнопка отправки
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            tr("browser_agent_dialog.input_placeholder", "Type your message here...")
        )
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton(tr("browser_agent_dialog.send", "Send"))
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)

        # Кнопка остановки выполнения агента
        self.stop_button = QPushButton(tr("browser_agent_dialog.stop", "Stop"))
        self.stop_button.clicked.connect(self.stop_agent)
        self.stop_button.setEnabled(False)
        chat_layout.addWidget(self.stop_button)

        # Добавляем виджеты в сплиттер
        self.splitter.addWidget(self.browser_widget)
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

        # Подключаем сигналы от браузера
        if hasattr(self.browser_widget, 'page_title_changed'):
            self.browser_widget.page_title_changed.connect(self.on_page_title_changed)

        # Подключаем сигналы от виджета истории чата
        self.chat_history.url_open_requested.connect(self.open_url)

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

    @Slot(str, str)
    def on_page_title_changed(self, url: str, title: str):
        """Обрабатывает изменение заголовка страницы браузера."""
        self.add_message_to_chat("Browser", f"Page loaded: {title} ({url})", is_progress=True)

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

    def analyze_current_page(self):
        """Запрашивает анализ текущей страницы у агента."""
        # Получаем текущую страницу и URL
        current_url = self.browser_widget.get_current_url()
        if not current_url:
            self.add_message_to_chat("System", tr("browser_agent_dialog.no_page_loaded", "No page is currently loaded"), is_progress=True)
            return

        # Добавляем в чат
        self.add_message_to_chat("You", tr("browser_agent_dialog.analyze_page_prompt", f"Please analyze the current page: {current_url}"))

        # Отправляем агенту запрос на анализ страницы
        prompt = f"Please analyze the current page: {current_url}"
        self.agent_interface.process_user_query(prompt)

    def search_on_current_page(self):
        """Запрашивает у пользователя текст для поиска и отправляет запрос агенту."""
        # Показываем диалог для ввода поискового запроса
        search_text, ok = QInputDialog.getText(
            self,
            tr("browser_agent_dialog.search_prompt_title", "Search on Page"),
            tr("browser_agent_dialog.search_prompt", "Enter text to search on the current page:")
        )

        if ok and search_text:
            # Добавляем в чат
            self.add_message_to_chat("You", tr("browser_agent_dialog.search_page_prompt", f"Please search for '{search_text}' on the current page"))

            # Отправляем агенту запрос на поиск на странице
            prompt = f"Please search for '{search_text}' on the current page and tell me what you find"
            self.agent_interface.process_user_query(prompt)

    def open_url(self, url: str):
        """Открывает URL в браузере."""
        # Проверяем и форматируем URL
        if not (url.startswith("http://") or url.startswith("https://")):
            if url.startswith("www."):
                url = "https://" + url
            else:
                url = "https://" + url

        # Открываем URL в браузере
        self.browser_widget.load_url(url)

        # Уведомление
        self.add_message_to_chat("System", tr("browser_agent_dialog.url_opened", f"Opening URL: {url}"), is_progress=True)

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
