import sys
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QPushButton, QHBoxLayout, QSizePolicy,
    QPlainTextEdit, QToolButton, QFileDialog, QMenu, QScrollArea, QFrame, QTextEdit, QLabel, QMessageBox # Добавляем QMessageBox
)
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QDir, QTimer, QMimeData # Добавляем QMimeData
from PySide6.QtGui import QKeyEvent, QIcon, QCursor, QAction # Добавляем QAction
from .icon_manager import get_icon # Добавляем импорт функции get_icon
from .i18n.translator import tr # Добавляем импорт функции tr
from .theme_manager import theme_manager # Добавляем импорт функции theme_manager

class ChatWidget(QWidget):
    # Сигнал, который будет отправляться при отправке сообщения пользователем
    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Устанавливаем имя объекта для стилей QSS
        self.setObjectName("ChatWidget")

        # Хранение истории чата
        self.chat_history = []

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Основной макет - вертикальный
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем панель с кнопками для управления историей
        history_controls = QWidget()
        history_controls_layout = QHBoxLayout(history_controls)
        history_controls_layout.setContentsMargins(10, 5, 10, 5)
        history_controls_layout.setSpacing(5)

        # Создаем кнопки для управления историей
        self.new_chat_button = QPushButton(tr("chat.new_chat", "New Chat"))
        self.new_chat_button.setIcon(get_icon("new_document"))
        self.new_chat_button.setToolTip(tr("chat.tooltip.new_chat", "Start a new chat"))

        self.save_chat_button = QPushButton(tr("chat.save_chat", "Save"))
        self.save_chat_button.setIcon(get_icon("save"))
        self.save_chat_button.setToolTip(tr("chat.tooltip.save", "Save chat history"))

        self.load_chat_button = QPushButton(tr("chat.load_chat", "Load"))
        self.load_chat_button.setIcon(get_icon("open"))
        self.load_chat_button.setToolTip(tr("chat.tooltip.load", "Load chat history"))

        # Добавляем кнопки в макет
        history_controls_layout.addWidget(self.new_chat_button)
        history_controls_layout.addWidget(self.save_chat_button)
        history_controls_layout.addWidget(self.load_chat_button)
        history_controls_layout.addStretch(1)  # Растягиваемый пробел

        # Добавляем панель управления в основной макет
        main_layout.addWidget(history_controls)

        # Макет для сообщений (основная часть)
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setSpacing(10)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)

        # Создаем QTextBrowser для отображения истории сообщений
        self.history_display = QTextBrowser()
        self.history_display.setOpenLinks(False)  # Отключаем автоматическое открытие ссылок
        self.history_display.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_display.customContextMenuRequested.connect(self._show_history_context_menu)

        # Виджет для прокрутки сообщений
        messages_container = QWidget()
        messages_container.setLayout(self.messages_layout)

        # Область прокрутки для сообщений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(messages_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Добавляем пространство для сообщений
        main_layout.addWidget(self.history_display, 1)  # Заменяем scroll_area на history_display

        # Полоса разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); margin: 0;")
        main_layout.addWidget(separator)

        # Контейнер для ввода сообщения (нижняя часть)
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        # Поле ввода и кнопки
        input_area = QWidget()
        input_area_layout = QHBoxLayout(input_area)
        input_area_layout.setContentsMargins(0, 0, 0, 0)
        input_area_layout.setSpacing(10)

        # Поле ввода сообщения
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText(tr("chat.placeholder", "Type a message..."))
        self.input_field.setFixedHeight(70)  # Фиксированная высота

        # Подключаемся к менеджеру тем, чтобы определить текущую тему
        theme_manager

        # Устанавливаем стиль в зависимости от темы
        if theme_manager.is_dark_theme():
            self.input_field.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: rgba(134, 112, 125, 0.9);
                    color: white;
                }
            """)
        else:
            self.input_field.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: rgba(255, 255, 255, 0.9);
                }
            """)

        # Подключаем обработчик изменения темы
        theme_manager.themeChanged.connect(self._update_input_field_style)

        # Кнопки действий
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)
        button_layout.setAlignment(Qt.AlignTop)

        # Кнопка отправки сообщения
        self.send_button = QPushButton(tr("chat.send", "Send"))
        self.send_button.setFixedHeight(35)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)

        # Кнопка вложения файла
        self.attach_file_button = QPushButton()
        self.attach_file_button.setIcon(get_icon("attach"))
        self.attach_file_button.setFixedSize(30, 30)
        self.attach_file_button.setIconSize(QSize(16, 16))
        self.attach_file_button.setToolTip(tr("tools.file", "Attach file"))

        # Кнопка вложения изображения
        self.attach_image_button = QPushButton()
        self.attach_image_button.setIcon(get_icon("image"))
        self.attach_image_button.setFixedSize(30, 30)
        self.attach_image_button.setIconSize(QSize(16, 16))
        self.attach_image_button.setToolTip(tr("tools.image_viewer", "Attach image"))

        # Кнопка эмодзи
        self.emoji_button = QPushButton()
        self.emoji_button.setIcon(get_icon("emoji"))
        self.emoji_button.setFixedSize(30, 30)
        self.emoji_button.setIconSize(QSize(16, 16))
        self.emoji_button.setToolTip(tr("tools.insert_emoji", "Insert emoji"))

        # Создаем горизонтальный контейнер для маленьких кнопок
        small_buttons_container = QWidget()
        small_buttons_layout = QHBoxLayout(small_buttons_container)
        small_buttons_layout.setContentsMargins(0, 0, 0, 0)
        small_buttons_layout.setSpacing(5)

        # Добавляем маленькие кнопки в контейнер
        small_buttons_layout.addWidget(self.attach_file_button)
        small_buttons_layout.addWidget(self.attach_image_button)
        small_buttons_layout.addWidget(self.emoji_button)

        # Добавляем кнопки в контейнер кнопок
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(small_buttons_container)

        # Добавляем компоненты в макет области ввода
        input_area_layout.addWidget(self.input_field, 1)  # 1 = растягивается
        input_area_layout.addWidget(button_container, 0)  # 0 = не растягивается

        # Добавляем область ввода в контейнер ввода
        input_layout.addWidget(input_area)

        # Добавляем контейнер ввода в основной макет с фиксированной высотой
        input_container.setFixedHeight(100)  # Фиксируем высоту контейнера ввода
        main_layout.addWidget(input_container, 0)  # 0 = не растягивается

        # Стартовое сообщение-подсказка
        self._add_system_message(tr("chat.history", "Message history will appear here..."))

        # Соединяем сигналы
        self.send_button.clicked.connect(self._on_send_message)
        self.input_field.textChanged.connect(self._on_input_changed)

        # Активируем отправку по Enter, но не по Shift+Enter
        self.input_field.installEventFilter(self)

        # Добавляем поддержку D&D для истории сообщений
        self.history_display.setAcceptDrops(True)
        self.history_display.dragEnterEvent = self._history_drag_enter_event
        self.history_display.dropEvent = self._history_drop_event

        # Добавляем поддержку D&D для поля ввода
        self.input_field.setAcceptDrops(True)
        self.input_field.dragEnterEvent = self._input_drag_enter_event
        self.input_field.dropEvent = self._input_drop_event

    def _connect_signals(self):
        """Подключаем сигналы к слотам."""
        self.send_button.clicked.connect(self._on_send_message)
        # Т.к. теперь у нас QPlainTextEdit, меняем обработку нажатия Enter
        self.input_field.installEventFilter(self)

        # Добавляем обработчики для новых кнопок
        self.attach_file_button.clicked.connect(self._on_attach_file)
        self.attach_image_button.clicked.connect(self._on_attach_image)
        self.emoji_button.clicked.connect(self._on_emoji_button_clicked)

        # Обработчики для кнопок истории
        self.new_chat_button.clicked.connect(self._new_chat)
        self.save_chat_button.clicked.connect(self._save_chat)
        self.load_chat_button.clicked.connect(self._load_chat)

    def eventFilter(self, obj, event):
        """Фильтр событий для обработки нажатия Enter в поле ввода."""
        if obj is self.input_field and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key_Return and not key_event.modifiers() & Qt.ShiftModifier:
                # Enter без Shift отправляет сообщение
                self._on_send_message()
                return True
            elif key_event.key() == Qt.Key_Return and key_event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter добавляет новую строку
                return False
        return super().eventFilter(obj, event)

    def changeEvent(self, event):
        """Обработчик события изменения языка."""
        if event.type() == QEvent.LanguageChange:
            # Обновляем тексты в интерфейсе при изменении языка
            self.new_chat_button.setText(tr("chat.new_chat", "New Chat"))
            self.new_chat_button.setToolTip(tr("chat.tooltip.new_chat", "Start a new chat"))
            self.save_chat_button.setText(tr("chat.save_chat", "Save"))
            self.save_chat_button.setToolTip(tr("chat.tooltip.save", "Save chat history"))
            self.load_chat_button.setText(tr("chat.load_chat", "Load"))
            self.load_chat_button.setToolTip(tr("chat.tooltip.load", "Load chat history"))
            self.input_field.setPlaceholderText(tr("chat.placeholder", "Type a message..."))
            self.send_button.setText(tr("chat.send", "Send"))
            self.attach_file_button.setToolTip(tr("tools.file", "Attach file"))
            self.attach_image_button.setToolTip(tr("tools.image_viewer", "Attach image"))
            self.emoji_button.setToolTip(tr("tools.insert_emoji", "Insert emoji"))

            # Если история пуста, обновляем начальное сообщение
            if len(self.chat_history) == 0:
                self._add_system_message(tr("chat.history", "Message history will appear here..."))

        super().changeEvent(event)

    def _on_input_changed(self):
        """Обработчик изменения текста в поле ввода."""
        # Проверяем, есть ли текст в поле ввода
        has_text = bool(self.input_field.toPlainText().strip())
        # Активируем/деактивируем кнопку отправки
        self.send_button.setEnabled(has_text)

    def _on_send_message(self):
        """Обработчик отправки сообщения."""
        message_text = self.get_input_text()
        if message_text:
            # Добавляем сообщение пользователя в историю
            self.add_message("User", message_text)

            # Очищаем поле ввода
            self.clear_input()

            # Отправляем сигнал с текстом сообщения
            self.message_sent.emit(message_text)

            # Убираем эхо-ответ ассистента - он будет приходить от агента
            # self.add_message("Assistant", f"Echo: {message_text}")

            # Прокрутка истории вниз
            self._scroll_to_bottom()

    def add_message(self, sender: str, message: str):
        """Добавляет форматированное сообщение в историю чата."""
        # Сохраняем сообщение в истории для дальнейшего сохранения
        timestamp = datetime.now().isoformat()
        self.chat_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })

        # Простая HTML-разметка для стилизации
        if sender.lower() == "user":
            # Сообщение пользователя (например, синий цвет)
            formatted_message = f'<p style="color: #66b3ff;"><b>{sender}:</b> {message}</p>'
        elif sender.lower() == "assistant":
            # Сообщение ассистента (например, зеленый цвет)
            formatted_message = f'<p style="color: #90ee90;"><b>{sender}:</b> {message}</p>'
        else:
            # Другие сообщения (например, системные - серый)
            formatted_message = f'<p style="color: gray;"><i>[{sender}]</i> {message}</p>'

        self.history_display.append(formatted_message) # Используем append для HTML

        # Прокручиваем историю вниз
        self._scroll_to_bottom()

    def clear_input(self):
        """Очищает поле ввода."""
        self.input_field.clear()

    def get_input_text(self) -> str:
        """Возвращает текст из поля ввода."""
        return self.input_field.toPlainText().strip()

    def _on_attach_file(self):
        """Обработчик нажатия кнопки прикрепления файла."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*)")
        if file_path:
            # TODO: Реализовать прикрепление файла
            self.add_message("System", f"File attached: {file_path}")

    def _on_attach_image(self):
        """Обработчик нажатия кнопки прикрепления изображения."""
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Attach Image", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if image_path:
            # TODO: Реализовать прикрепление изображения
            self.add_message("System", f"Image attached: {image_path}")

    def _on_emoji_button_clicked(self):
        """Обработчик нажатия кнопки вставки эмодзи."""
        # Создаем сигнал для вызова диалога эмодзи из главного окна
        parent = self.window()  # Получаем родительское окно
        if hasattr(parent, '_show_emoji_dialog'):
            parent._show_emoji_dialog()

    def _show_history_context_menu(self, position):
        """Показывает контекстное меню для истории сообщений."""
        context_menu = QMenu(self)

        copy_action = QAction(tr("menu.copy", "Copy"), self)
        copy_action.triggered.connect(self._copy_selection)
        context_menu.addAction(copy_action)

        clear_action = QAction(tr("chat.clear", "Clear History"), self)
        clear_action.triggered.connect(self._new_chat)
        context_menu.addAction(clear_action)

        context_menu.addSeparator()

        save_action = QAction(tr("chat.save_chat", "Save History..."), self)
        save_action.triggered.connect(self._save_chat)
        context_menu.addAction(save_action)

        context_menu.exec(QCursor.pos())

    def _copy_selection(self):
        """Копирует выделенный текст в буфер обмена."""
        self.history_display.copy()

    def _new_chat(self):
        """Создает новую сессию чата."""
        # Очищаем историю сообщений и отображение
        self.chat_history = []
        self.history_display.clear()
        self.add_message("System", "Начат новый чат")

    def _save_chat(self):
        """Сохраняет историю чата в файл JSON."""
        if not self.chat_history:
            self.add_message("System", tr("chat.error_save", "No messages to save"))
            return

        # Форматируем дату и время для имени файла по умолчанию
        default_filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Открываем диалог сохранения файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("dialogs.file.save", "Save Chat History"),
            os.path.join(QDir.homePath(), default_filename),
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                # Сохраняем историю в формате JSON
                chat_data = {
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "messages": self.chat_history
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=2)

                self.add_message("System", tr("chat.saved", "Chat history saved to {file_path}").format(file_path=file_path))
            except Exception as e:
                self.add_message("System", tr("chat.error_save", "Error saving chat: {error}").format(error=str(e)))

    def _load_chat(self):
        """Загружает историю чата из файла JSON."""
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("dialogs.file.open", "Load Chat History"),
            QDir.homePath(),
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)

                # Проверяем версию и формат
                if 'version' in chat_data and 'messages' in chat_data:
                    # Очищаем текущую историю
                    self.history_display.clear()
                    self.chat_history = []

                    # Загружаем сообщения
                    for message in chat_data['messages']:
                        if 'sender' in message and 'message' in message:
                            # Отображаем сообщение в истории
                            sender = message['sender']
                            text = message['message']
                            # Добавляем сообщение вручную, чтобы избежать дублирования в истории
                            if sender.lower() == "user":
                                formatted_message = f'<p style="color: #66b3ff;"><b>{sender}:</b> {text}</p>'
                            elif sender.lower() == "assistant":
                                formatted_message = f'<p style="color: #90ee90;"><b>{sender}:</b> {text}</p>'
                            else:
                                formatted_message = f'<p style="color: gray;"><i>[{sender}]</i> {text}</p>'

                            self.history_display.append(formatted_message)

                    # Сохраняем загруженные сообщения в историю
                    self.chat_history = chat_data['messages']

                    self.add_message("System", tr("chat.loaded", "Chat history loaded from {file_path}").format(file_path=file_path))
                else:
                    self.add_message("System", tr("chat.error_load", "Unsupported file format"))
            except Exception as e:
                self.add_message("System", tr("chat.error_load", "Error loading chat: {error}").format(error=str(e)))

    def set_input_enabled(self, enabled: bool):
        """Включает или отключает поле ввода и кнопку отправки."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.attach_file_button.setEnabled(enabled)
        self.attach_image_button.setEnabled(enabled)
        self.emoji_button.setEnabled(enabled)  # Добавляем в список отключаемых элементов

    def insert_text(self, text: str):
        """Вставляет текст в позицию курсора в поле ввода."""
        if self.input_field.isEnabled():
            self.input_field.insertPlainText(text)
            # Устанавливаем фокус обратно на поле ввода
            self.input_field.setFocus()

    def _scroll_to_bottom(self):
        """Прокручивает историю чата вниз."""
        # Прокручиваем QTextBrowser
        self.history_display.verticalScrollBar().setValue(
            self.history_display.verticalScrollBar().maximum()
        )

    def _add_system_message(self, text):
        """Добавляет системное сообщение в историю чата."""
        current_time = datetime.now().strftime("%H:%M")
        system_sender = f"[{tr('chat.system', 'System')}]"

        html = f"""
        <div style="margin-bottom: 8px; padding: 8px; background-color: rgba(0, 0, 0, 0.05); border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: bold; color: #888888;">{system_sender}</span>
                <span style="color: #888888; font-size: 0.8em;">{current_time}</span>
            </div>
            <div style="color: #555555;">{text}</div>
        </div>
        """

        # Добавляем HTML в историю
        current_html = self.history_display.toHtml()
        self.history_display.setHtml(current_html + html)

        # Прокручиваем к последнему сообщению
        self._scroll_to_bottom()

    # Методы для поддержки перетаскивания файлов
    def _history_drag_enter_event(self, event):
        """Обработчик начала перетаскивания для истории чата."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            QTextBrowser.dragEnterEvent(self.history_display, event)

    def _history_drop_event(self, event):
        """Обработчик перетаскивания файла в историю чата."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    # Добавляем сообщение в чат о прикрепленном файле
                    self.add_message("user", f"Прикрепленный файл: {file_path}")

                    # Можно добавить дополнительную обработку для текстовых файлов
                    try:
                        # Для текстовых файлов можно отобразить содержимое
                        if self._is_text_file(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                                # Ограничиваем размер для отображения
                                if len(file_content) > 500:
                                    file_content = file_content[:500] + "\n[...]\n(файл слишком большой, показано начало)"
                                self.add_message("system", f"Содержимое файла {os.path.basename(file_path)}:\n```\n{file_content}\n```")
                        else:
                            self.add_message("system", f"Файл {os.path.basename(file_path)} прикреплен. Это не текстовый файл.")
                    except Exception as e:
                        self.add_message("system", f"Ошибка при чтении файла: {str(e)}")

            event.acceptProposedAction()
        else:
            QTextBrowser.dropEvent(self.history_display, event)

    def _input_drag_enter_event(self, event):
        """Обработчик начала перетаскивания для поля ввода."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            QTextEdit.dragEnterEvent(self.input_field, event)

    def _input_drop_event(self, event):
        """Обработчик перетаскивания файла в поле ввода."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    # Для текстовых файлов добавляем содержимое в поле ввода
                    try:
                        if self._is_text_file(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                                # Ограничиваем размер для вставки
                                if len(file_content) > 1000:
                                    file_content = file_content[:1000] + "\n[...]\n(файл слишком большой, показано начало)"
                                # Вставляем содержимое в поле ввода
                                self.input_field.insertPlainText(f"\nСодержимое файла {os.path.basename(file_path)}:\n```\n{file_content}\n```")
                        else:
                            # Для нетекстовых файлов добавляем ссылку
                            self.input_field.insertPlainText(f"\nФайл: {file_path}")
                    except Exception as e:
                        QMessageBox.warning(self, tr("Ошибка"), tr(f"Ошибка при чтении файла: {str(e)}"))

            event.acceptProposedAction()
        else:
            QTextEdit.dropEvent(self.input_field, event)

    def _is_text_file(self, file_path):
        """Проверяет, является ли файл текстовым."""
        # Проверка по расширению
        text_extensions = ['.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml', '.csv', '.log', '.ini',
                          '.c', '.cpp', '.h', '.hpp', '.cs', '.java', '.sh', '.bat', '.ps1', '.yaml', '.yml', '.toml']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions or self._check_file_content(file_path)

    def _check_file_content(self, file_path):
        """Проверяет содержимое файла на текстовый формат."""
        try:
            # Читаем первые 1024 байта файла для определения типа
            with open(file_path, 'rb') as f:
                data = f.read(1024)
            # Проверяем наличие нулевых байтов, что характерно для бинарных файлов
            return b'\x00' not in data
        except Exception:
            return False

    def _update_input_field_style(self):
        """Обновляет стиль поля ввода в зависимости от темы."""
        # Подключаемся к менеджеру тем, чтобы определить текущую тему
        theme_manager

        # Устанавливаем стиль в зависимости от темы
        if theme_manager.is_dark_theme():
            self.input_field.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: rgba(134, 112, 125, 0.9);
                    color: white;
                }
            """)
        else:
            self.input_field.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: rgba(255, 255, 255, 0.9);
                }
            """)

# Пример запуска для теста самого виджета
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    chat_widget = ChatWidget()
    chat_widget.add_message("User", "Hello!")
    chat_widget.add_message("Assistant", "Hi there! How can I help?")
    chat_widget.resize(400, 600)
    chat_widget.show()
    sys.exit(app.exec())
