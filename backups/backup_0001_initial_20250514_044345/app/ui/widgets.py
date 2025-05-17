from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QTextBrowser,
    QLineEdit,
    QPlainTextEdit,
    QDialog,
    QPushButton,
    QScrollArea,
    QLabel,
    QFileDialog,
    QSizePolicy
)
from PySide6.QtGui import QFont, QFontMetrics, QTextCursor, QIcon, QColor  # Added QFont, QFontMetrics
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QEvent
from .i18n.translator import tr
from .lucide_icon_manager import get_lucide_icon
from app.ui.icon_adapter import get_icon

# Assuming theme_manager might be needed for full functionality based on original main_window.py
# from .theme_manager import theme_manager

import re
import os
import logging
import sys
from datetime import datetime
from typing import List, Optional


class MessageBubble(QWidget):
    """Виджет-пузырь для сообщения в чате."""

    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setObjectName("userMessageBubble" if is_user else "assistantMessageBubble")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)  # Уменьшенные отступы

        # Создаем текстовую метку
        message = QTextBrowser()
        message.setReadOnly(True)
        message.setOpenExternalLinks(True)
        message.setHtml(text)

        # Убираем рамку и фон
        message.setFrameShape(QTextBrowser.NoFrame)

        # Настраиваем шрифт
        font = message.font()
        font.setPointSize(10)  # Уменьшаем размер шрифта
        message.setFont(font)

        # Адаптивный размер
        message.document().setDocumentMargin(0)
        message.setFixedHeight(message.document().size().height() + 4)  # Добавляем отступ

        # Стилизуем в зависимости от отправителя
        if is_user:
            self.setStyleSheet("""
                #userMessageBubble {
                    background-color: #dcf8c6;
                    border-radius: 10px;
                    margin: 2px 40px 2px 80px; /* Увеличен отступ слева для выравнивания справа */
                }

                #userMessageBubble QTextBrowser {
                    color: #303030;
                    background-color: transparent;
                    margin-bottom: 4px; /* Добавляем отступ снизу */
                }
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet("""
                #assistantMessageBubble {
                    background-color: #ececec;
                    border-radius: 10px;
                    margin: 2px 80px 2px 10px; /* Увеличен отступ справа для выравнивания слева */
                }

                #assistantMessageBubble QTextBrowser {
                    color: #363636;
                    background-color: transparent;
                    margin-bottom: 4px; /* Добавляем отступ снизу */
                }
            """)
            layout.setAlignment(Qt.AlignLeft)

        layout.addWidget(message)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)


class ChatHistoryArea(QScrollArea):
    """Область для отображения истории чата."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)

        # Контейнер для пузырей сообщений
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(8)  # Меньший отступ между сообщениями
        self.layout.setContentsMargins(12, 12, 12, 12)  # Увеличен отступ от краев

        # Стиль фона, имитирующий WhatsApp
        container.setStyleSheet("background-color: #e5ddd5;")

        self.setWidget(container)

        # Включаем автоматическую прокрутку при добавлении сообщений
        self.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)

    def add_message(self, text, is_user=True):
        """Добавляет сообщение в историю чата."""
        bubble = MessageBubble(text, is_user, self)
        self.layout.addWidget(bubble)

        # Добавляем небольшую задержку перед прокруткой, чтобы виджет успел обновиться
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Прокручивает историю чата вниз."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class ExpandingTextEdit(QTextEdit):
    """Расширяемое поле ввода текста."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)
        self.document().setDocumentMargin(2)

        # Устанавливаем объектное имя для стилей
        self.setObjectName("messageInput")

        # Устанавливаем минимальную и максимальную высоту
        self.setMinimumHeight(32)
        self.setMaximumHeight(150)  # Увеличиваем максимальную высоту

        # Отслеживаем изменения текста для адаптации высоты
        self.textChanged.connect(self._adjust_height)

        # Включаем вертикальную полосу прокрутки при необходимости
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Устанавливаем стиль напрямую для гарантии применения
        self.setStyleSheet("""
            QTextEdit#messageInput {
                border-radius: 18px;
                background-color: white;
                padding: 8px 12px;
                padding-bottom: 12px;
                border: 1px solid #d1d7db;
                color: #333333;
            }
        """)

        # Установка начальной высоты (малая до ввода текста)
        self.setFixedHeight(32)

    def _adjust_height(self):
        """Подстраивает высоту поля ввода под содержимое."""
        # Рассчитываем высоту на основе содержимого
        doc_height = self.document().size().height()

        # Получаем текущий текст
        text = self.toPlainText().strip()

        # Если текст пустой, возвращаем минимальную высоту
        if not text:
            new_height = 32
        # Иначе подстраиваем высоту под контент
        else:
            # Ограничиваем высоту
            if doc_height < 32:
                new_height = 32
            elif doc_height > 150:
                new_height = 150
            else:
                new_height = doc_height + 20  # Увеличиваем отступы для текста

        self.setFixedHeight(int(new_height))


class ChatWidget(QWidget):
    message_sent = Signal(str)  # <--- Сигнал для отправки сообщений
    insert_code_to_editor = Signal(str)  # <--- Сигнал для вставки кода в редактор
    run_code_in_terminal = Signal(str)  # <--- Сигнал для запуска кода в терминале

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        # Основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Заголовок чата - делаем его меньше и менее заметным
        header = QWidget()
        header.setObjectName("chatHeader")
        header.setFixedHeight(0)  # Уменьшаем высоту до нуля (скрываем)
        header.setVisible(False)  # Делаем его невидимым
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)  # Убираем все отступы
        header_layout.setSpacing(0)

        # Иконка чата
        chat_icon = QLabel()
        chat_icon.setPixmap(get_lucide_icon("message-circle").pixmap(0, 0))  # Устанавливаем нулевой размер
        chat_icon.setVisible(False)
        header_layout.addWidget(chat_icon)

        # Название чата
        chat_title = QLabel(tr("chat.title", "Чат"))
        chat_title.setObjectName("chatTitle")
        chat_title.setStyleSheet("font-weight: bold; font-size: 0px;")  # Устанавливаем нулевой размер шрифта
        chat_title.setVisible(False)
        header_layout.addWidget(chat_title)

        header_layout.addStretch(1)  # Растягиваем пространство между названием и возможными кнопками

        main_layout.addWidget(header)

        # История чата
        self.chat_history = ChatHistoryArea()
        main_layout.addWidget(self.chat_history, 1)  # Растягивается

        # Панель ввода и кнопок - вертикальный лейаут
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_container_layout = QVBoxLayout(input_container)
        input_container_layout.setContentsMargins(5, 5, 5, 5)
        input_container_layout.setSpacing(5)

        # Верхний ряд - поле ввода
        input_row = QWidget()
        input_row_layout = QHBoxLayout(input_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(5)

        # Поле ввода сообщений
        self.message_input = ExpandingTextEdit()
        self.message_input.setPlaceholderText(tr("chat.input_placeholder", "Введите сообщение..."))
        self.message_input.textChanged.connect(self._update_send_button)
        input_row_layout.addWidget(self.message_input)

        input_container_layout.addWidget(input_row)

        # Нижний ряд - кнопки
        buttons_row = QWidget()
        buttons_row.setObjectName("buttonsRow")
        buttons_row_layout = QHBoxLayout(buttons_row)
        buttons_row_layout.setContentsMargins(0, 0, 0, 0)
        buttons_row_layout.setSpacing(5)

        # Кнопка эмодзи
        self.emoji_button = QPushButton()
        self.emoji_button.setIcon(get_lucide_icon("smile"))
        self.emoji_button.setIconSize(QSize(22, 22))  # Увеличиваем размер иконки
        self.emoji_button.setFixedSize(36, 36)  # Увеличиваем размер кнопки
        self.emoji_button.setObjectName("emojiButton")
        self.emoji_button.setProperty("class", "toolButton")
        self.emoji_button.clicked.connect(self._show_emoji_dialog)
        buttons_row_layout.addWidget(self.emoji_button)

        # Кнопка прикрепления файлов
        self.attach_button = QPushButton()
        self.attach_button.setIcon(get_lucide_icon("paperclip"))
        self.attach_button.setIconSize(QSize(22, 22))  # Увеличиваем размер иконки
        self.attach_button.setFixedSize(36, 36)  # Увеличиваем размер кнопки
        self.attach_button.setObjectName("attachButton")
        self.attach_button.setProperty("class", "toolButton")
        self.attach_button.clicked.connect(self._attach_file)
        buttons_row_layout.addWidget(self.attach_button)

        # Кнопка отправки изображения
        self.image_button = QPushButton()
        self.image_button.setIcon(get_lucide_icon("image"))
        self.image_button.setIconSize(QSize(22, 22))  # Увеличиваем размер иконки
        self.image_button.setFixedSize(36, 36)  # Увеличиваем размер кнопки
        self.image_button.setObjectName("imageButton")
        self.image_button.setProperty("class", "toolButton")
        self.image_button.clicked.connect(self._attach_image)
        buttons_row_layout.addWidget(self.image_button)

        # Кнопка Browsing Agent
        self.browser_agent_button = QPushButton()
        self.browser_agent_button.setIcon(get_lucide_icon("search"))
        self.browser_agent_button.setIconSize(QSize(22, 22))
        self.browser_agent_button.setFixedSize(36, 36)
        self.browser_agent_button.setObjectName("browserAgentButton")
        self.browser_agent_button.setProperty("class", "toolButton")
        self.browser_agent_button.setToolTip(tr("chat.browser_agent", "Browsing Agent"))
        self.browser_agent_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 18px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: rgba(128, 128, 128, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(128, 128, 128, 0.2);
            }
        """)
        self.browser_agent_button.clicked.connect(self._activate_browser_agent)
        buttons_row_layout.addWidget(self.browser_agent_button)

        # Растягивающийся спейсер
        buttons_row_layout.addStretch(1)

        # Для удобства тестирования - кнопка остановки генерации
        self.stop_button = QPushButton(tr("chat.stop_button", "Стоп"))
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setFixedSize(60, 36)  # Увеличиваем размер кнопки
        self.stop_button.setVisible(False)  # Скрыта по умолчанию
        self.stop_button.setFont(QFont("Arial", 10, QFont.Bold))  # Увеличиваем шрифт
        self.stop_button.clicked.connect(self._stop_generation)  # Восстанавливаем обработчик
        buttons_row_layout.addWidget(self.stop_button)

        # Кнопка отправки/микрофона
        self.send_mic_button = QPushButton()
        self.send_mic_button.setIcon(get_lucide_icon("send"))
        self.send_mic_button.setIconSize(QSize(22, 22))  # Увеличиваем размер иконки
        self.send_mic_button.setFixedSize(44, 44)  # Увеличиваем размер кнопки
        self.send_mic_button.setObjectName("sendMicButton")
        self.send_mic_button.clicked.connect(self._on_send_mic_clicked)
        buttons_row_layout.addWidget(self.send_mic_button)

        input_container_layout.addWidget(buttons_row)

        main_layout.addWidget(input_container)

        # Включаем перенос Enter для отправки, Shift+Enter для новой строки
        self.message_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Обрабатывает нажатия клавиш в поле ввода."""
        if obj == self.message_input and event.type() == QEvent.KeyPress:
            # Импортируем Qt.Key_* константы
            from PySide6.QtCore import Qt

            # Enter без Shift отправляет сообщение
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if not event.modifiers() & Qt.ShiftModifier:
                    self._on_message_sent()
                    return True
        return super().eventFilter(obj, event)

    def _update_send_button(self):
        """Обновляет иконку кнопки отправки в зависимости от того, есть ли текст в поле ввода."""
        if self.message_input.toPlainText().strip():
            # Если есть текст - показываем кнопку отправки
            self.send_mic_button.setIcon(get_lucide_icon("send"))
            # Используем более светлый фон для кнопки
            self.send_mic_button.setStyleSheet("background-color: #00a884;")
        else:
            # Если пусто - показываем кнопку микрофона
            self.send_mic_button.setIcon(get_lucide_icon("mic"))
            # Используем стандартный фон
            self.send_mic_button.setStyleSheet("")

    def _on_send_mic_clicked(self):
        """Обрабатывает нажатие на кнопку отправки/микрофона."""
        if self.message_input.toPlainText().strip():
            self._on_message_sent()
        else:
            # В будущем здесь будет функционал записи голоса
            pass

    def _on_message_sent(self):
        """Отправляет сообщение."""
        message = self.message_input.toPlainText().strip()
        if message:
            self.message_input.clear()
            # Добавляем сообщение как сообщение пользователя (без имени "You")
            self.add_message("", message, is_user=True)
            # Отправляем сигнал с сообщением для обработки
            self.message_sent.emit(message)
            # Обновляем кнопку после очистки поля
            self._update_send_button()

    def add_message(self, sender, text, is_user=False):
        """Добавляет сообщение в историю чата."""
        # Более красивое форматирование сообщения с пользовательским именем
        if is_user:
            # Для сообщений пользователя используем более компактный формат без имени
            formatted_text = f"{text}"
        else:
            # Для сообщений ассистента добавляем имя жирным шрифтом и отделяем текст
            formatted_text = f"<b>{sender}</b><br>{text}"

        self.chat_history.add_message(formatted_text, is_user)

    def _show_emoji_dialog(self):
        """Показывает диалог выбора эмодзи."""
        try:
            from app.ui.emoji_dialog import EmojiDialog

            dialog = EmojiDialog(self)
            dialog.emoji_selected.connect(self._insert_emoji)
            dialog.setStyleSheet("background-color: white;")

            # Позиционируем диалог возле кнопки эмодзи
            dialog_pos = self.emoji_button.mapToGlobal(self.emoji_button.rect().topRight())
            dialog.move(dialog_pos)

            dialog.exec()
        except ImportError as e:
            print(f"Ошибка при импорте EmojiDialog: {e}")
        except Exception as e:
            print(f"Ошибка при показе диалога эмодзи: {e}")

    def _insert_emoji(self, emoji):
        """Вставляет эмодзи в поле ввода."""
        self.message_input.insertPlainText(emoji)
        self.message_input.setFocus()

    def _attach_file(self):
        """Открывает диалог выбора файла для прикрепления."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("chat.attach_file.title", "Прикрепить файл"),
            "",
            tr("chat.attach_file.filter", "Все файлы (*.*)")
        )

        if file_path:
            # Добавляем информацию о прикрепленном файле
            file_name = os.path.basename(file_path)
            self.add_message("You", f"📎 {file_name} (File attached)", is_user=True)
            # Тут может быть логика отправки файла

    def _attach_image(self):
        """Открывает диалог выбора изображения для прикрепления."""
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("chat.attach_image.title", "Прикрепить изображение"),
            "",
            tr("chat.attach_image.filter", "Изображения (*.png *.jpg *.jpeg *.gif *.bmp)")
        )

        if image_path:
            # Добавляем информацию о прикрепленном изображении
            image_name = os.path.basename(image_path)
            self.add_message("You", f"🖼️ {image_name} (Image attached)", is_user=True)
            # Тут может быть логика отправки изображения

    def _extract_code_from_selection(self, text):
        """Извлекает код из выделенного текста."""
        import re

        markdown_code_match = re.search(r"```(?:\w*\n)?([\s\S]*?)```", text)
        if markdown_code_match:
            return markdown_code_match.group(1)
        return text

    def _stop_generation(self):
        """Останавливает генерацию текста."""
        # Логика остановки генерации будет добавлена позже
        pass

    def _activate_browser_agent(self):
        """Активирует Browsing Agent и открывает вкладку браузера"""
        if hasattr(self.main_window, "_toggle_browser"):
            self.main_window._toggle_browser()


class CodeEditor(QPlainTextEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.file_path = None
        self._init_editor()

    def _init_editor(self):
        font = QFont("JetBrains Mono")
        font.setPointSize(10)
        self.setFont(font)

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(4 * QFontMetrics(font).horizontalAdvance(" "))

    def insert_code(self, code):
        """Insert code at the current cursor position."""
        cursor = self.textCursor()
        cursor.insertText(code)
        self.setTextCursor(cursor)

    def contextMenuEvent(self, event):
        """Переопределяем стандартное контекстное меню для добавления пункта Insert Emoji."""
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import Qt

        # Создаем стандартное меню
        menu = super().createStandardContextMenu()

        # Добавляем разделитель и пункт для вставки эмодзи
        menu.addSeparator()

        # Создаем действие для вставки эмодзи с локализацией
        emoji_action = QAction(tr("menu.insert_emoji", "Insert Emoji"), self)

        # Добавляем иконку смайлика, если доступен менеджер иконок
        try:
            from app.ui.lucide_icon_manager import get_lucide_icon

            emoji_action.setIcon(get_lucide_icon("smile"))
        except ImportError:
            pass  # Если не получилось импортировать иконку, продолжаем без нее

        # Подключаем действие к методу показа диалога эмодзи
        emoji_action.triggered.connect(
            lambda: self._show_emoji_dialog(event.globalPos())
        )
        menu.addAction(emoji_action)

        # Отображаем меню
        menu.exec(event.globalPos())

    def _show_emoji_dialog(self, position):
        """Показывает диалог выбора эмодзи."""
        try:
            from app.ui.emoji_dialog import EmojiDialog
            from PySide6.QtWidgets import QDialog
            import logging

            logger = logging.getLogger(__name__)

            # Создаем диалог
            dialog = EmojiDialog(self)

            # Подключаем сигнал для вставки эмодзи
            dialog.emoji_selected.connect(self.insertPlainText)

            # Позиционируем диалог
            dialog.move(position)

            # Показываем диалог
            result = dialog.exec()

            return result == QDialog.Accepted
        except ImportError as e:
            print(f"Ошибка при импорте EmojiDialog: {e}")
            return False
        except Exception as e:
            print(f"Ошибка при показе диалога эмодзи: {e}")
            return False


class TerminalWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Initialize terminal widget with actual terminal functionality

        # Terminal output display
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.layout.addWidget(self.terminal_output)

        # Command input
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self._on_command_entered)
        self.layout.addWidget(self.command_input)

        # Set up process for command execution
        self.process = None

    def _on_command_entered(self):
        """Handle command input."""
        command = self.command_input.text()
        self.command_input.clear()
        self.execute_command(command)

    def execute_command(self, command):
        """Execute a command in the terminal."""
        # Display the command in the output
        self.terminal_output.append(f"> {command}")

        # Actual implementation would connect to a real terminal/process
        # For now, just simulate output
        self.terminal_output.append("Command executed (this is a placeholder)")

        # In a real implementation, you would:
        # if hasattr(self, "process") and hasattr(self.process, "write"):
        #     self.process.write(command.encode() + b"\n")
