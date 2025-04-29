import sys
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QPushButton, QHBoxLayout, QSizePolicy,
    QPlainTextEdit, QToolButton, QFileDialog, QMenu # Удаляем QAction из импорта QtWidgets
)
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QDir # Добавляем QDir
from PySide6.QtGui import QKeyEvent, QIcon, QCursor, QAction # Добавляем QAction
from .icon_manager import get_icon # Добавляем импорт функции get_icon

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
        # Основной layout - вертикальный
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Убираем отступы у основного layout
        main_layout.setSpacing(5) # Небольшой отступ между элементами

        # Добавляем панель кнопок для истории чата
        history_buttons_layout = QHBoxLayout()
        history_buttons_layout.setContentsMargins(2, 2, 2, 2)

        # Кнопка для новой истории
        self.new_chat_button = QToolButton(self)
        self.new_chat_button.setToolTip("Новый чат")
        self.new_chat_button.setIcon(get_icon("new_chat"))
        self.new_chat_button.setIconSize(QSize(24, 24))
        self.new_chat_button.setFixedSize(30, 30)

        # Кнопка для сохранения чата
        self.save_chat_button = QToolButton(self)
        self.save_chat_button.setToolTip("Сохранить историю чата")
        self.save_chat_button.setIcon(get_icon("save"))
        self.save_chat_button.setIconSize(QSize(24, 24))
        self.save_chat_button.setFixedSize(30, 30)

        # Кнопка для загрузки чата
        self.load_chat_button = QToolButton(self)
        self.load_chat_button.setToolTip("Загрузить историю чата")
        self.load_chat_button.setIcon(get_icon("open"))
        self.load_chat_button.setIconSize(QSize(24, 24))
        self.load_chat_button.setFixedSize(30, 30)

        # Добавляем кнопки в layout
        history_buttons_layout.addWidget(self.new_chat_button)
        history_buttons_layout.addWidget(self.save_chat_button)
        history_buttons_layout.addWidget(self.load_chat_button)
        history_buttons_layout.addStretch(1)

        # Добавляем панель кнопок истории в основной layout
        main_layout.addLayout(history_buttons_layout)

        # 1. Область для отображения истории сообщений
        self.history_display = QTextBrowser(self)
        self.history_display.setReadOnly(True)
        # Используем placeholder из переводов через _translate, это будет исправлено при инициализации
        self.history_display.setPlaceholderText("История сообщений будет отображаться здесь...")
        # Устанавливаем политику размера, чтобы история занимала максимум пространства
        self.history_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Устанавливаем минимальную высоту, чтобы всегда был виден хотя бы фрагмент истории
        self.history_display.setMinimumHeight(100)

        # Включаем контекстное меню для истории
        self.history_display.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_display.customContextMenuRequested.connect(self._show_history_context_menu)

        # 2. Область для ввода сообщения (поле ввода + кнопки)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(2, 2, 2, 2)  # Небольшие отступы
        input_layout.setSpacing(5)

        # Заменяем QLineEdit на QPlainTextEdit для многострочного ввода
        self.input_field = QPlainTextEdit(self)
        self.input_field.setPlaceholderText("Введите сообщение...")
        # Устанавливаем политику размера для поля ввода
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Устанавливаем минимальную и максимальную высоту (значительно увеличиваем)
        self.input_field.setMinimumHeight(100)  # Было 36, увеличиваем почти в 3 раза
        self.input_field.setMaximumHeight(250)  # Было 100, увеличиваем для возможности видеть больше текста

        # Создаем вертикальный layout для кнопок справа
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)

        # Создаем кнопки для прикрепления файлов и изображений
        attachment_layout = QHBoxLayout()
        attachment_layout.setSpacing(2)

        # Кнопка для прикрепления файла
        self.attach_file_button = QToolButton(self)
        self.attach_file_button.setToolTip("Attach File")
        self.attach_file_button.setIcon(get_icon("attach_file"))
        self.attach_file_button.setIconSize(QSize(24, 24))
        self.attach_file_button.setFixedSize(30, 30)

        # Кнопка для прикрепления изображения
        self.attach_image_button = QToolButton(self)
        self.attach_image_button.setToolTip("Attach Image")
        self.attach_image_button.setIcon(get_icon("attach_image"))
        self.attach_image_button.setIconSize(QSize(24, 24))
        self.attach_image_button.setFixedSize(30, 30)

        # Кнопка для вставки эмодзи
        self.emoji_button = QToolButton(self)
        self.emoji_button.setToolTip("Вставить эмодзи")
        self.emoji_button.setIcon(get_icon("emoji"))
        self.emoji_button.setIconSize(QSize(24, 24))
        self.emoji_button.setFixedSize(30, 30)

        # Добавляем кнопки в горизонтальный layout
        attachment_layout.addWidget(self.attach_file_button)
        attachment_layout.addWidget(self.attach_image_button)
        attachment_layout.addWidget(self.emoji_button)
        attachment_layout.addStretch(1)  # Добавляем растягивающийся спейсер

        # Добавляем attachment_layout в buttons_layout
        buttons_layout.addLayout(attachment_layout)

        # Кнопка отправки с уменьшенным размером
        self.send_button = QPushButton("Отправить", self)
        # Уменьшаем размер кнопки в два раза
        self.send_button.setFixedWidth(70)
        self.send_button.setFixedHeight(50)  # Было 100, делаем в два раза меньше

        # Добавляем кнопку отправки в buttons_layout
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addStretch(1)  # Добавляем растягивающийся спейсер снизу

        # Добавляем поле ввода и layout с кнопками в основной горизонтальный layout
        input_layout.addWidget(self.input_field, 1)  # Вес 1, чтобы растягивалось
        input_layout.addLayout(buttons_layout, 0)  # Вес 0, не растягивается

        # Добавляем элементы в основной layout
        main_layout.addWidget(self.history_display, 1)  # Вес 1 - растягивается первым
        main_layout.addLayout(input_layout, 0)  # Вес 0 - не растягивается

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
            self.history_display.verticalScrollBar().setValue(
                self.history_display.verticalScrollBar().maximum()
            )

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

        copy_action = QAction("Копировать", self)
        copy_action.triggered.connect(self._copy_selection)
        context_menu.addAction(copy_action)

        clear_action = QAction("Очистить историю", self)
        clear_action.triggered.connect(self._new_chat)
        context_menu.addAction(clear_action)

        context_menu.addSeparator()

        save_action = QAction("Сохранить историю...", self)
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
            self.add_message("System", "Нет сообщений для сохранения")
            return

        # Форматируем дату и время для имени файла по умолчанию
        default_filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Открываем диалог сохранения файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить историю чата",
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

                self.add_message("System", f"История чата сохранена в {file_path}")
            except Exception as e:
                self.add_message("System", f"Ошибка при сохранении: {str(e)}")

    def _load_chat(self):
        """Загружает историю чата из файла JSON."""
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить историю чата",
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

                    self.add_message("System", f"История чата загружена из {file_path}")
                else:
                    self.add_message("System", "Формат файла не поддерживается")
            except Exception as e:
                self.add_message("System", f"Ошибка при загрузке: {str(e)}")

    def set_input_enabled(self, enabled: bool):
        """Включает или отключает поле ввода и кнопку отправки."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.attach_file_button.setEnabled(enabled)
        self.attach_image_button.setEnabled(enabled)
        self.emoji_button.setEnabled(enabled)  # Добавляем в список отключаемых элементов

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
