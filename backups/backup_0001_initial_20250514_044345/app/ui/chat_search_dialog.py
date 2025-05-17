"""
Диалог для поиска по истории чатов.

Предоставляет интерфейс для поиска сообщений
с возможностью фильтрации по различным критериям.
"""

import os
import datetime
from typing import List, Dict, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDateEdit,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QSplitter,
    QTextEdit,
    QMessageBox,
    QFileDialog,
)

from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon
from app.utils.chat_indexer import ChatHistoryIndexer
from app.utils.theme_manager import ThemeManager


class ChatSearchDialog(QDialog):
    """
    Диалог для поиска по истории чатов с различными фильтрами
    и возможностью просмотра результатов.
    """

    # Сигналы
    message_selected = Signal(dict)  # Сигнал о выборе сообщения

    def __init__(self, parent=None, theme_manager: Optional[ThemeManager] = None):
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Создаем индексатор
        self.indexer = ChatHistoryIndexer()

        # Состояние диалога
        self.current_results = []

        # Настройка UI
        self.setup_ui()

        # Применяем стили из текущей темы
        self.update_styles()

        # Загружаем сессии
        self.load_sessions()

    def setup_ui(self):
        """Настраивает пользовательский интерфейс диалога."""
        # Основные свойства диалога
        self.setWindowTitle(tr("chat_search_dialog.title", "Chat History Search"))
        self.setWindowIcon(get_icon("search"))
        self.resize(900, 600)

        # Основной лейаут
        main_layout = QVBoxLayout(self)

        # === Верхняя часть: Панель поиска ===
        search_group = QGroupBox(tr("chat_search_dialog.search_panel", "Search Criteria"))
        search_layout = QVBoxLayout(search_group)

        # Строка поиска
        search_input_layout = QHBoxLayout()
        search_input_layout.addWidget(QLabel(tr("chat_search_dialog.search_query", "Search:")))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("chat_search_dialog.search_placeholder", "Enter search query..."))
        search_input_layout.addWidget(self.search_input, 1)  # 1 = stretch factor

        self.search_button = QPushButton(tr("chat_search_dialog.search", "Search"))
        self.search_button.setIcon(get_icon("search"))
        self.search_button.clicked.connect(self.perform_search)
        search_input_layout.addWidget(self.search_button)

        search_layout.addLayout(search_input_layout)

        # Дополнительные фильтры
        filters_layout = QHBoxLayout()

        # Сессии
        session_layout = QVBoxLayout()
        session_layout.addWidget(QLabel(tr("chat_search_dialog.session", "Session:")))
        self.session_combo = QComboBox()
        self.session_combo.addItem(tr("chat_search_dialog.all_sessions", "All Sessions"), "")
        session_layout.addWidget(self.session_combo)
        filters_layout.addLayout(session_layout)

        # Отправитель
        sender_layout = QVBoxLayout()
        sender_layout.addWidget(QLabel(tr("chat_search_dialog.sender", "Sender:")))
        self.sender_combo = QComboBox()
        self.sender_combo.addItem(tr("chat_search_dialog.all_senders", "All Senders"), "")
        self.sender_combo.addItem("You", "You")
        self.sender_combo.addItem("Agent", "Agent")
        self.sender_combo.addItem("System", "System")
        self.sender_combo.addItem("Browser", "Browser")
        sender_layout.addWidget(self.sender_combo)
        filters_layout.addLayout(sender_layout)

        # Даты
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel(tr("chat_search_dialog.date_range", "Date Range:")))
        date_input_layout = QHBoxLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(datetime.datetime.now().date().replace(day=1))  # Первый день текущего месяца
        date_input_layout.addWidget(self.start_date)

        date_input_layout.addWidget(QLabel(" - "))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(datetime.datetime.now().date())  # Сегодня
        date_input_layout.addWidget(self.end_date)

        self.use_date_filter = QCheckBox(tr("chat_search_dialog.use_date_filter", "Use Date Filter"))
        date_input_layout.addWidget(self.use_date_filter)

        date_layout.addLayout(date_input_layout)
        filters_layout.addLayout(date_layout)

        search_layout.addLayout(filters_layout)

        # Дополнительные опции
        options_layout = QHBoxLayout()

        self.include_errors = QCheckBox(tr("chat_search_dialog.include_errors", "Include Errors"))
        self.include_errors.setChecked(True)
        options_layout.addWidget(self.include_errors)

        self.include_progress = QCheckBox(tr("chat_search_dialog.include_progress", "Include Progress Messages"))
        self.include_progress.setChecked(True)
        options_layout.addWidget(self.include_progress)

        options_layout.addStretch(1)

        # Кнопки экспорта
        self.export_button = QPushButton(tr("chat_search_dialog.export_results", "Export Results"))
        self.export_button.setIcon(get_icon("download"))
        self.export_button.clicked.connect(self.export_results)
        options_layout.addWidget(self.export_button)

        search_layout.addLayout(options_layout)

        main_layout.addWidget(search_group)

        # === Центральная часть: Сплиттер с результатами и предпросмотром ===
        splitter = QSplitter(Qt.Horizontal)

        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            tr("chat_search_dialog.table_date", "Date/Time"),
            tr("chat_search_dialog.table_session", "Session"),
            tr("chat_search_dialog.table_sender", "Sender"),
            tr("chat_search_dialog.table_message", "Message")
        ])

        # Настройка таблицы
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.itemSelectionChanged.connect(self.on_result_selected)

        splitter.addWidget(self.results_table)

        # Предпросмотр сообщения
        preview_group = QGroupBox(tr("chat_search_dialog.message_preview", "Message Preview"))
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        self.open_session_button = QPushButton(tr("chat_search_dialog.open_session", "Open This Session"))
        self.open_session_button.setIcon(get_icon("open"))
        self.open_session_button.clicked.connect(self.open_current_session)
        preview_layout.addWidget(self.open_session_button)

        splitter.addWidget(preview_group)

        # Устанавливаем соотношение размеров (60% таблица, 40% предпросмотр)
        splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])

        main_layout.addWidget(splitter, 1)  # 1 = stretch factor

        # === Нижняя часть: Статус и кнопки ===
        bottom_layout = QHBoxLayout()

        self.status_label = QLabel(tr("chat_search_dialog.status_ready", "Ready"))
        bottom_layout.addWidget(self.status_label, 1)

        self.close_button = QPushButton(tr("chat_search_dialog.close", "Close"))
        self.close_button.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_button)

        main_layout.addLayout(bottom_layout)

    def update_styles(self):
        """Обновляет стили элементов интерфейса в соответствии с текущей темой."""
        if not self.theme_manager:
            return

        # Получаем цвета из текущей темы
        bg_color = self.theme_manager.get_color("background", "#2D2D2D")
        text_color = self.theme_manager.get_color("foreground", "#EAEAEA")
        secondary_bg = self.theme_manager.get_color("secondary_background", "#3C3C3C")
        border_color = self.theme_manager.get_color("border", "#444444")
        hover_color = self.theme_manager.get_color("hover", "#4E4E4E")
        selected_color = self.theme_manager.get_color("selected", "#505050")

        # Применяем стили к таблице результатов
        self.results_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                gridline-color: {border_color};
            }}
            QTableWidget::item:selected {{
                background-color: {selected_color};
            }}
            QTableWidget::item:hover {{
                background-color: {hover_color};
            }}
            QHeaderView::section {{
                background-color: {secondary_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 4px;
            }}
            """
        )

        # Применяем стили к виджету предпросмотра
        self.preview_text.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; }}"
        )

    def load_sessions(self):
        """Загружает список сессий в комбобокс."""
        try:
            # Очищаем комбобокс
            current_index = self.session_combo.currentIndex()
            self.session_combo.clear()
            self.session_combo.addItem(tr("chat_search_dialog.all_sessions", "All Sessions"), "")

            # Получаем список сессий
            sessions = self.indexer.get_sessions()

            for session in sessions:
                # Форматируем название сессии для отображения
                session_id = session['session_id']
                start_time = session['start_time']
                message_count = session['message_count']

                # Пытаемся извлечь дату из session_id (обычно в формате YYYYMMDD_HHMMSS)
                display_name = f"Session {session_id}"
                if start_time:
                    display_name = f"{start_time} ({message_count} messages)"

                self.session_combo.addItem(display_name, session_id)

            # Восстанавливаем выбранный индекс
            if current_index >= 0 and current_index < self.session_combo.count():
                self.session_combo.setCurrentIndex(current_index)

            self.status_label.setText(
                tr("chat_search_dialog.sessions_loaded", f"Loaded {len(sessions)} chat sessions")
            )

        except Exception as e:
            self.status_label.setText(
                tr("chat_search_dialog.sessions_error", f"Error loading sessions: {str(e)}")
            )

    @Slot()
    def perform_search(self):
        """Выполняет поиск по заданным критериям."""
        try:
            # Получаем параметры поиска
            query = self.search_input.text().strip()
            session_id = self.session_combo.currentData()
            sender = self.sender_combo.currentData()

            # Даты
            start_date = None
            end_date = None
            if self.use_date_filter.isChecked():
                start_date = self.start_date.date().toString('dd.MM.yyyy')
                end_date = self.end_date.date().toString('dd.MM.yyyy')

            # Выполняем поиск
            self.status_label.setText(tr("chat_search_dialog.searching", "Searching..."))

            results = self.indexer.search_messages(
                query=query,
                session_id=session_id,
                sender=sender,
                start_date=start_date,
                end_date=end_date,
                limit=1000  # Ограничиваем результаты
            )

            # Фильтруем результаты по дополнительным критериям
            if not self.include_errors.isChecked():
                results = [msg for msg in results if not msg['is_error']]

            if not self.include_progress.isChecked():
                results = [msg for msg in results if not msg['is_progress']]

            # Сохраняем результаты
            self.current_results = results

            # Отображаем результаты
            self.display_results(results)

            # Обновляем статус
            self.status_label.setText(
                tr("chat_search_dialog.search_results", f"Found {len(results)} messages")
            )

        except Exception as e:
            self.status_label.setText(
                tr("chat_search_dialog.search_error", f"Error during search: {str(e)}")
            )
            QMessageBox.warning(
                self,
                tr("chat_search_dialog.error_title", "Search Error"),
                tr("chat_search_dialog.search_error_details", f"Error during search: {str(e)}")
            )

    def display_results(self, results: List[Dict]):
        """
        Отображает результаты поиска в таблице.

        Args:
            results: Список сообщений для отображения
        """
        # Очищаем таблицу
        self.results_table.setRowCount(0)

        # Заполняем таблицу
        for i, message in enumerate(results):
            self.results_table.insertRow(i)

            # Дата/время
            timestamp_item = QTableWidgetItem(message['timestamp'])
            self.results_table.setItem(i, 0, timestamp_item)

            # Сессия
            session_item = QTableWidgetItem(message['session_id'])
            self.results_table.setItem(i, 1, session_item)

            # Отправитель
            sender_item = QTableWidgetItem(message['sender'])
            self.results_table.setItem(i, 2, sender_item)

            # Сообщение - сокращенное
            message_text = message['message']
            if len(message_text) > 100:
                message_text = message_text[:97] + "..."
            message_item = QTableWidgetItem(message_text)
            self.results_table.setItem(i, 3, message_item)

            # Сохраняем полные данные о сообщении в первом элементе
            timestamp_item.setData(Qt.UserRole, message)

            # Устанавливаем цвет фона для сообщений с ошибками и прогрессом
            if message['is_error']:
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(i, col)
                    if item:
                        item.setBackground(Qt.red)
                        item.setForeground(Qt.white)
            elif message['is_progress']:
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(i, col)
                    if item:
                        item.setBackground(Qt.gray)

        # Сортируем по времени (по убыванию - новые сверху)
        self.results_table.sortItems(0, Qt.DescendingOrder)

        # Очищаем предпросмотр
        self.preview_text.clear()

    @Slot()
    def on_result_selected(self):
        """Обрабатывает выбор сообщения в таблице."""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return

        # Получаем полные данные о сообщении
        row = selected_items[0].row()
        timestamp_item = self.results_table.item(row, 0)
        if not timestamp_item:
            return

        message_data = timestamp_item.data(Qt.UserRole)
        if not message_data:
            return

        # Отображаем полное сообщение в предпросмотре
        sender = message_data['sender']
        timestamp = message_data['timestamp']
        message_text = message_data['message']

        # Форматируем текст для предпросмотра
        html = f"<h3>{sender}</h3>"
        html += f"<p><i>{timestamp}</i></p>"
        html += f"<hr>"

        # Добавляем метки для особых сообщений
        prefix = ""
        if message_data['is_error']:
            prefix = "<span style='color:red;'>[ERROR]</span> "
        elif message_data['is_progress']:
            prefix = "<span style='color:gray;'>[PROGRESS]</span> "

        html += f"<p>{prefix}{message_text}</p>"

        # Добавляем информацию о сессии
        html += "<hr>"
        html += f"<p><b>Session ID:</b> {message_data['session_id']}</p>"

        self.preview_text.setHtml(html)

        # Эмитируем сигнал о выборе сообщения
        self.message_selected.emit(message_data)

    @Slot()
    def open_current_session(self):
        """Открывает текущую выбранную сессию."""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                tr("chat_search_dialog.info", "Information"),
                tr("chat_search_dialog.no_selected_message", "Please select a message first")
            )
            return

        # Получаем данные о сессии
        row = selected_items[0].row()
        timestamp_item = self.results_table.item(row, 0)
        if not timestamp_item:
            return

        message_data = timestamp_item.data(Qt.UserRole)
        if not message_data:
            return

        session_id = message_data['session_id']

        # Здесь будет код для открытия сессии
        # Пока выводим информационное сообщение
        QMessageBox.information(
            self,
            tr("chat_search_dialog.session_info", "Session Information"),
            tr("chat_search_dialog.session_id", f"Session ID: {session_id}")
        )

        # TODO: Реализовать открытие сессии

    @Slot()
    def export_results(self):
        """Экспортирует результаты поиска в файл."""
        if not self.current_results:
            QMessageBox.information(
                self,
                tr("chat_search_dialog.info", "Information"),
                tr("chat_search_dialog.no_results", "No results to export")
            )
            return

        # Диалог сохранения файла
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Text Files (*.txt);;CSV Files (*.csv);;HTML Files (*.html)")

        if not file_dialog.exec_():
            return

        file_path = file_dialog.selectedFiles()[0]
        if not file_path:
            return

        # Определяем формат по расширению
        format_type = "txt"
        if file_path.endswith(".csv"):
            format_type = "csv"
        elif file_path.endswith(".html"):
            format_type = "html"

        try:
            # Экспортируем в выбранном формате
            if format_type == "txt":
                self._export_as_txt(file_path)
            elif format_type == "csv":
                self._export_as_csv(file_path)
            elif format_type == "html":
                self._export_as_html(file_path)

            self.status_label.setText(
                tr("chat_search_dialog.export_success", f"Results exported to {file_path}")
            )

            QMessageBox.information(
                self,
                tr("chat_search_dialog.export_title", "Export Successful"),
                tr("chat_search_dialog.export_success_details", f"Results exported to {file_path}")
            )

        except Exception as e:
            self.status_label.setText(
                tr("chat_search_dialog.export_error", f"Error exporting results: {str(e)}")
            )

            QMessageBox.warning(
                self,
                tr("chat_search_dialog.error_title", "Export Error"),
                tr("chat_search_dialog.export_error_details", f"Error exporting results: {str(e)}")
            )

    def _export_as_txt(self, file_path: str):
        """Экспортирует результаты в текстовый файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=== CHAT HISTORY SEARCH RESULTS ===\n\n")
            f.write(f"Search time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total results: {len(self.current_results)}\n\n")

            for i, msg in enumerate(self.current_results, 1):
                prefix = ""
                if msg['is_error']:
                    prefix = "[ERROR] "
                elif msg['is_progress']:
                    prefix = "[PROGRESS] "

                f.write(f"--- Result {i} ---\n")
                f.write(f"Session: {msg['session_id']}\n")
                f.write(f"Time: {msg['timestamp']}\n")
                f.write(f"Sender: {msg['sender']}\n")
                f.write(f"Message: {prefix}{msg['message']}\n\n")

    def _export_as_csv(self, file_path: str):
        """Экспортирует результаты в CSV файл."""
        import csv

        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Заголовок
            writer.writerow(["Timestamp", "Session", "Sender", "Type", "Message"])

            # Данные
            for msg in self.current_results:
                msg_type = "Normal"
                if msg['is_error']:
                    msg_type = "Error"
                elif msg['is_progress']:
                    msg_type = "Progress"

                writer.writerow([
                    msg['timestamp'],
                    msg['session_id'],
                    msg['sender'],
                    msg_type,
                    msg['message']
                ])

    def _export_as_html(self, file_path: str):
        """Экспортирует результаты в HTML файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Chat History Search Results</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
                    .message { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
                    .error { border-color: #ff0000; background-color: #ffeeee; }
                    .progress { border-color: #999; background-color: #f5f5f5; color: #555; }
                    .header { font-weight: bold; margin-bottom: 5px; }
                    .timestamp { color: #888; font-size: 0.9em; }
                    .sender { color: #0066cc; }
                    h1 { color: #333; }
                    .meta { color: #666; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <h1>Chat History Search Results</h1>
                <div class="meta">
                    <p>Search time: %s</p>
                    <p>Total results: %d</p>
                </div>
            """ % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(self.current_results)))

            for msg in self.current_results:
                css_class = "message"
                prefix = ""

                if msg['is_error']:
                    css_class += " error"
                    prefix = "<strong>[ERROR]</strong> "
                elif msg['is_progress']:
                    css_class += " progress"
                    prefix = "<em>[PROGRESS]</em> "

                f.write(f"""
                <div class="{css_class}">
                    <div class="header">
                        <span class="sender">{msg['sender']}</span>
                        <span class="timestamp">({msg['timestamp']})</span>
                        <span class="session">Session: {msg['session_id']}</span>
                    </div>
                    <div class="content">
                        {prefix}{msg['message']}
                    </div>
                </div>
                """)

            f.write("""
            </body>
            </html>
            """)
