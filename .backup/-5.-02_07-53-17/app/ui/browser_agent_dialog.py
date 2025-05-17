import asyncio
from typing import Optional, Dict
import datetime
import json
import os

from PySide6.QtCore import QPoint, QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QContextMenuEvent, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from app.ui.browser_agent_interface import BrowserAgentInterface
from app.ui.browser_tab_widget import MultiBrowserWidget
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon
from app.utils.theme_manager import ThemeManager
from app.utils.chat_indexer import ChatHistoryIndexer
from app.ui.chat_search_dialog import ChatSearchDialog


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
                selected_text.startswith("http://")
                or selected_text.startswith("https://")
                or selected_text.startswith("www.")
            )

            if is_url:
                # Добавляем действие для открытия URL
                open_url_action = QAction(
                    tr("browser_agent_dialog.open_url", "Open URL"), self
                )
                open_url_action.triggered.connect(
                    lambda: self.url_open_requested.emit(selected_text)
                )
                menu.addAction(open_url_action)

        # Добавляем разделитель и пункт для вставки эмодзи, если виджет не только для чтения
        if not self.isReadOnly():
            menu.addSeparator()

            # Импортируем функцию для получения Lucide иконок
            from app.ui.lucide_icon_manager import get_lucide_icon

            emoji_action = QAction(tr("menu.insert_emoji", "Insert Emoji"), self)
            emoji_action.setIcon(get_lucide_icon("smile"))

            # Используем глобальную позицию курсора для отображения диалога
            global_pos = event.globalPos()
            emoji_action.triggered.connect(lambda: self._show_emoji_dialog(global_pos))
            menu.addAction(emoji_action)

        menu.exec_(event.globalPos())

    def _show_emoji_dialog(self, position):
        """Показывает диалог выбора эмодзи в указанной позиции."""
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

        # Загружаем предыдущую историю сообщений, если она существует
        self.load_chat_history()

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

        # Заголовок чата с кнопками действий
        header_layout = QHBoxLayout()

        chat_header = QLabel(
            tr("browser_agent_dialog.chat_header", "Browsing Agent Chat")
        )
        chat_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(chat_header, 1)  # 1 - растягивающий фактор

        # Кнопка поиска по истории
        self.search_history_button = QPushButton(tr("browser_agent_dialog.search_history", "Search History"))
        self.search_history_button.setIcon(get_icon("search"))
        self.search_history_button.clicked.connect(self.open_search_dialog)
        header_layout.addWidget(self.search_history_button)

        # Кнопка экспорта истории
        self.export_button = QPushButton(tr("browser_agent_dialog.export", "Export"))
        self.export_button.setIcon(get_icon("download"))
        self.export_button.clicked.connect(self.show_export_menu)
        header_layout.addWidget(self.export_button)

        chat_layout.addLayout(header_layout)

        # История чата с расширенным функционалом
        self.chat_history = ChatHistoryWidget(self)
        self.chat_history.setPlaceholderText(
            tr(
                "browser_agent_dialog.chat_placeholder",
                "Chat with the browsing agent here...",
            )
        )
        chat_layout.addWidget(self.chat_history)

        # Панель инструментов для взаимодействия с браузером
        browser_actions_layout = QHBoxLayout()

        # Кнопка для анализа текущей страницы
        self.analyze_page_button = QPushButton(
            tr("browser_agent_dialog.analyze_page", "Analyze Current Page")
        )
        self.analyze_page_button.setIcon(get_icon("analyze"))
        self.analyze_page_button.clicked.connect(self.analyze_current_page)
        browser_actions_layout.addWidget(self.analyze_page_button)

        # Кнопка для поиска на странице
        self.search_page_button = QPushButton(
            tr("browser_agent_dialog.search_page", "Search on Page")
        )
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

        # Применяем стили из текущей темы
        self.update_styles()

    def connect_signals(self):
        """Подключает сигналы и слоты."""
        # Подключаем сигналы от интерфейса агента к UI
        self.agent_interface.agent_message.connect(self.on_agent_message)
        self.agent_interface.agent_error.connect(self.on_agent_error)
        self.agent_interface.agent_thinking.connect(self.on_agent_thinking)
        self.agent_interface.agent_finished.connect(self.on_agent_finished)

        # Подключаем сигналы от браузера
        if hasattr(self.browser_widget, "page_title_changed"):
            self.browser_widget.page_title_changed.connect(self.on_page_title_changed)

        # Подключаем сигналы от виджета истории чата
        self.chat_history.url_open_requested.connect(self.open_url)

        # Подключаем сигнал изменения темы
        if self.theme_manager:
            self.theme_manager.visualThemeChanged.connect(self.update_styles)

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
            "is_progress": is_progress
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
            is_progress=is_progress
        )

    def save_chat_history(self):
        """Сохраняет историю чата в JSON файл."""
        try:
            # Определяем директорию для хранения истории чатов
            history_dir = os.path.join(os.path.expanduser("~"), ".gopi_ai", "chat_history")

            # Создаем директорию, если она не существует
            os.makedirs(history_dir, exist_ok=True)

            # Путь к файлу с историей текущей сессии
            history_file = os.path.join(history_dir, f"browser_agent_{self.chat_history_data['session_id']}.json")

            # Сохраняем данные в JSON файл
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history_data, f, ensure_ascii=False, indent=2)

            # Экспортируем в TXT для удобства чтения
            self.chat_indexer.export_session_to_txt(self.chat_history_data['session_id'])

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("browser_agent_dialog.save_history_error", f"Error saving chat history: {str(e)}"),
                is_error=True
            )

    def load_chat_history(self):
        """Загружает последнюю историю чата, если она существует."""
        try:
            # Директория с историей чатов
            history_dir = os.path.join(os.path.expanduser("~"), ".gopi_ai", "chat_history")

            if not os.path.exists(history_dir):
                return

            # Ищем файлы истории браузерного агента
            history_files = [
                os.path.join(history_dir, f)
                for f in os.listdir(history_dir)
                if f.startswith("browser_agent_") and f.endswith(".json")
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
                tr("browser_agent_dialog.load_history_error", f"Error loading chat history: {str(e)}"),
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
                default_filename = f"browser_agent_history_{self.chat_history_data['session_id']}.json"
            elif format_type == "txt":
                file_dialog.setNameFilter("Text Files (*.txt)")
                default_filename = f"browser_agent_history_{self.chat_history_data['session_id']}.txt"
            elif format_type == "html":
                file_dialog.setNameFilter("HTML Files (*.html)")
                default_filename = f"browser_agent_history_{self.chat_history_data['session_id']}.html"
            else:
                return

            file_dialog.selectFile(os.path.join(default_dir, default_filename))

            if file_dialog.exec_():
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
                        f.write("<html><head><title>Browser Agent Chat History</title>")
                        f.write("<style>body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;}")
                        f.write(".message{margin-bottom:10px;}.sender{font-weight:bold;}")
                        f.write(".timestamp{font-size:0.8em;color:#888;}.error{color:red;}.progress{color:gray;font-style:italic;}")
                        f.write("</style></head><body><h1>Browser Agent Chat History</h1>")

                        for msg in self.chat_history_data.get("messages", []):
                            cls = ""
                            if msg.get("is_error", False):
                                cls = "error"
                            elif msg.get("is_progress", False):
                                cls = "progress"

                            f.write(f"<div class='message {cls}'>")
                            f.write(f"<span class='sender'>{msg.get('sender')}:</span> ")
                            f.write(f"{msg.get('message')} ")
                            f.write(f"<span class='timestamp'>[{msg.get('timestamp')}]</span>")
                            f.write("</div>")

                        f.write("</body></html>")

                self.add_message_to_chat(
                    "System",
                    tr("browser_agent_dialog.export_success", f"Chat history exported to {file_path}"),
                    is_progress=True
                )

        except Exception as e:
            self.add_message_to_chat(
                "System",
                tr("browser_agent_dialog.export_error", f"Error exporting chat history: {str(e)}"),
                is_error=True
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
            self.add_message_to_chat(
                "System",
                tr(
                    "browser_agent_dialog.no_page_loaded", "No page is currently loaded"
                ),
                is_progress=True,
            )
            return

        # Добавляем в чат
        self.add_message_to_chat(
            "You",
            tr(
                "browser_agent_dialog.analyze_page_prompt",
                f"Please analyze the current page: {current_url}",
            ),
        )

        # Отправляем агенту запрос на анализ страницы
        prompt = f"Please analyze the current page: {current_url}"
        self.agent_interface.process_user_query(prompt)

    def search_on_current_page(self):
        """Запрашивает у пользователя текст для поиска и отправляет запрос агенту."""
        # Показываем диалог для ввода поискового запроса
        search_text, ok = QInputDialog.getText(
            self,
            tr("browser_agent_dialog.search_prompt_title", "Search on Page"),
            tr(
                "browser_agent_dialog.search_prompt",
                "Enter text to search on the current page:",
            ),
        )

        if ok and search_text:
            # Добавляем в чат
            self.add_message_to_chat(
                "You",
                tr(
                    "browser_agent_dialog.search_page_prompt",
                    f"Please search for '{search_text}' on the current page",
                ),
            )

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
        self.add_message_to_chat(
            "System",
            tr("browser_agent_dialog.url_opened", f"Opening URL: {url}"),
            is_progress=True,
        )

    def closeEvent(self, event: QCloseEvent):
        """Обрабатывает закрытие диалога."""
        # Останавливаем работу агента
        self.agent_interface.stop_agent()

        # Сохраняем историю сообщений
        self.save_chat_history()

        # Запускаем очистку ресурсов агента
        asyncio.create_task(self.cleanup())

        # Закрываем диалог
        super().closeEvent(event)

    async def cleanup(self):
        """Очищает ресурсы перед закрытием диалога."""
        await self.agent_interface.cleanup()

    def show_export_menu(self):
        """Показывает меню для выбора формата экспорта истории."""
        export_menu = QMenu(self)

        json_action = QAction(tr("browser_agent_dialog.export_json", "Export as JSON"), self)
        json_action.triggered.connect(lambda: self.export_chat_history("json"))
        export_menu.addAction(json_action)

        txt_action = QAction(tr("browser_agent_dialog.export_txt", "Export as TXT"), self)
        txt_action.triggered.connect(lambda: self.export_chat_history("txt"))
        export_menu.addAction(txt_action)

        html_action = QAction(tr("browser_agent_dialog.export_html", "Export as HTML"), self)
        html_action.triggered.connect(lambda: self.export_chat_history("html"))
        export_menu.addAction(html_action)

        # Показываем меню под кнопкой экспорта
        export_menu.exec_(self.export_button.mapToGlobal(QPoint(0, self.export_button.height())))

    def update_styles(self):
        """Обновляет стили элементов интерфейса в соответствии с текущей темой."""
        if not self.theme_manager:
            return

        # Получаем цвета из текущей темы
        bg_color = self.theme_manager.get_color("background", "#2D2D2D")
        text_color = self.theme_manager.get_color("foreground", "#EAEAEA")
        secondary_bg = self.theme_manager.get_color("secondary_background", "#3C3C3C")
        border_color = self.theme_manager.get_color("border", "#444444")

        # Применяем стили к виджету истории чата
        self.chat_history.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; }}"
        )

        # Применяем стили к полю ввода
        self.message_input.setStyleSheet(
            f"QLineEdit {{ background-color: {secondary_bg}; color: {text_color}; border: 1px solid {border_color}; }}"
        )

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
                tr("browser_agent_dialog.search_dialog_error", f"Error opening search dialog: {str(e)}"),
                is_error=True
            )
