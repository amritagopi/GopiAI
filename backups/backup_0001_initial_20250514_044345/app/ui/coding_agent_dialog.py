import asyncio
import logging
import os
from typing import Optional

from PySide6.QtCore import QPoint, QSettings, QSize, Qt, Signal, Slot
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QContextMenuEvent,
    QCursor,
    QIcon,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
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
)

from app.ui.code_editor_widget import MultiEditorWidget
from app.ui.coding_agent_interface import CodingAgentInterface
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon
from app.utils.theme_manager import ThemeManager

# Создаем logger для модуля
logger = logging.getLogger(__name__)


class ChatHistoryWidget(QTextEdit):
    """
    Виджет истории чата с расширенным функционалом.

    Добавляет контекстное меню для копирования и вставки кода.
    """

    code_insert_requested = Signal(str)
    run_code_in_terminal = Signal(str)

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
            insert_action = QAction(
                tr("coding_agent_dialog.insert_to_editor", "Insert to Editor"), self
            )
            insert_action.triggered.connect(
                lambda: self.code_insert_requested.emit(selected_text)
            )
            menu.addAction(insert_action)

            # Добавляем действие для запуска кода в терминале
            run_action = QAction(
                tr("coding_agent_dialog.run_in_terminal", "Run in Terminal"), self
            )
            run_action.triggered.connect(lambda: self.run_in_terminal(selected_text))
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

        menu.exec_(event.globalPos())

    def run_in_terminal(self, code: str):
        """Запускает код в терминале."""
        # Отправляем сигнал с кодом для запуска
        self.run_code_in_terminal.emit(code)

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
                logger.info(f"Positioned emoji dialog at {x},{y}")

            # Показываем диалог
            result = dialog.exec()
            logger.info(f"Emoji dialog result: {result}")

            return result == QDialog.Accepted

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not show emoji dialog: {str(e)}")
            return False


class CodingAgentDialog(QDialog):
    """
    Диалог для взаимодействия с агентом кодирования.

    Содержит редактор кода и интерфейс для общения с агентом,
    который может помогать с редактированием, анализом и запуском кода.
    """

    def __init__(
        self,
        parent=None,
        theme_manager: Optional[ThemeManager] = None,
    ):
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
            tr(
                "coding_agent_dialog.chat_placeholder",
                "Chat with the coding agent here...",
            )
        )
        chat_layout.addWidget(self.chat_history)

        # Панель инструментов для взаимодействия с кодом
        code_actions_layout = QHBoxLayout()

        # Кнопка для отправки выделенного кода в чат
        self.send_code_button = QPushButton(
            tr("coding_agent_dialog.send_code", "Send Code to Chat")
        )
        self.send_code_button.setIcon(get_icon("chat"))
        self.send_code_button.clicked.connect(self.send_selected_code_to_chat)
        code_actions_layout.addWidget(self.send_code_button)

        # Кнопка для проверки кода
        self.check_code_button = QPushButton(
            tr("coding_agent_dialog.check_code", "Check Code")
        )
        self.check_code_button.setIcon(get_icon("debug"))
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

        # Создаем группу кнопок для дополнительных действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(2)

        # Кнопка эмодзи
        self.emoji_button = QPushButton()
        self.emoji_button.setIcon(get_icon("emoji"))
        self.emoji_button.setToolTip(tr("coding_agent_dialog.emoji", "Insert Emoji"))
        self.emoji_button.setFixedSize(32, 32)
        self.emoji_button.clicked.connect(
            lambda: self._show_emoji_selector(
                self.emoji_button.mapToGlobal(self.emoji_button.rect().topRight())
            )
        )
        actions_layout.addWidget(self.emoji_button)

        # Кнопка для прикрепления файлов
        self.attach_button = QPushButton()
        self.attach_button.setIcon(get_icon("paperclip"))
        self.attach_button.setToolTip(tr("coding_agent_dialog.attach", "Attach File"))
        self.attach_button.setFixedSize(32, 32)
        self.attach_button.clicked.connect(self._attach_file)
        actions_layout.addWidget(self.attach_button)

        # Кнопка для прикрепления изображений
        self.image_button = QPushButton()
        self.image_button.setIcon(get_icon("image_file"))
        self.image_button.setToolTip(tr("coding_agent_dialog.image", "Attach Image"))
        self.image_button.setFixedSize(32, 32)
        self.image_button.clicked.connect(self._attach_image)
        actions_layout.addWidget(self.image_button)

        input_layout.addLayout(actions_layout)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            tr("coding_agent_dialog.input_placeholder", "Type your message here...")
        )
        self.message_input.returnPressed.connect(self.send_message)
        # Устанавливаем минимальную высоту для поля ввода и политику растяжения по горизонтали
        self.message_input.setMinimumHeight(32)
        self.message_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.message_input, 1)  # 1 устанавливает растяжение

        self.send_button = QPushButton(tr("coding_agent_dialog.send", "Send"))
        self.send_button.setIcon(get_icon("send"))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedSize(70, 32)
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

        # Устанавливаем начальные размеры для сплиттера (50% слева, 50% справа)
        self.splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)])

        # Устанавливаем политику обработки растяжения
        self.splitter.setStretchFactor(0, 1)  # Редактор может растягиваться
        self.splitter.setStretchFactor(1, 1)  # Чат может растягиваться

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
        self.chat_history.run_code_in_terminal.connect(self.run_code_in_terminal)

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

        if is_error:
            self.chat_history.insertHtml(
                f"<p><b style='color: red;'>{sender}:</b> {message}</p>"
            )
        elif is_progress:
            self.chat_history.insertHtml(
                f"<p><i style='color: gray;'>{sender}: {message}</i></p>"
            )
        else:
            self.chat_history.insertHtml(f"<p><b>{sender}:</b> {message}</p>")

        # Прокручиваем чат вниз
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
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

    def send_selected_code_to_chat(self):
        """Отправляет выделенный в редакторе код в чат."""
        # Получаем текущий редактор и выделенный текст
        editor = self.editor_widget.tabs.currentWidget()
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.add_message_to_chat(
                "System",
                tr("coding_agent_dialog.no_selected_code", "No code selected"),
                is_progress=True,
            )
            return

        # Форматируем сообщение с кодом
        formatted_message = f"```\n{selected_text}\n```"

        # Добавляем в чат
        self.add_message_to_chat("You", formatted_message)

        # Отправляем агенту запрос на анализ кода
        prompt = tr(
            "coding_agent_dialog.analyze_code_prompt",
            "Please analyze the following code and provide feedback:",
        )
        self.agent_interface.process_user_query(f"{prompt}\n{formatted_message}")

    def check_selected_code(self):
        """Проверяет выделенный код на ошибки."""
        # Получаем текущий редактор и выделенный текст
        editor = self.editor_widget.tabs.currentWidget()
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.add_message_to_chat(
                "System",
                tr("coding_agent_dialog.no_selected_code", "No code selected"),
                is_progress=True,
            )
            return

        # Форматируем сообщение с кодом
        formatted_message = f"```\n{selected_text}\n```"

        # Добавляем в чат
        self.add_message_to_chat(
            "You",
            tr(
                "coding_agent_dialog.check_code_prompt",
                "Please check this code for errors:",
            ),
        )
        self.add_message_to_chat("You", formatted_message)

        # Отправляем агенту запрос на проверку кода
        prompt = tr(
            "coding_agent_dialog.check_code_prompt",
            "Please check this code for errors and suggest improvements:",
        )
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
        self.add_message_to_chat(
            "System",
            tr("coding_agent_dialog.code_inserted", "Code inserted to editor"),
            is_progress=True,
        )

    def run_code_in_terminal(self, code: str):
        """Запускает код в терминале."""
        # Отправляем сигнал с кодом для запуска
        self.chat_history.run_code_in_terminal.emit(code)

    def _show_emoji_selector(self, position=None):
        """Показывает селектор эмодзи.

        Args:
            position (QPoint, optional): Позиция для отображения диалога. Если None,
                                         используется текущая позиция курсора.
        """
        try:
            from app.ui.emoji_dialog import EmojiDialog

            # Создаем диалог для выбора эмодзи
            emoji_dialog = EmojiDialog(self)
            emoji_dialog.emoji_selected.connect(self._insert_emoji)

            # Получаем текущую позицию курсора, если не передана
            if not position:
                position = QCursor.pos()

            # Проверяем тип позиции и преобразуем при необходимости
            if position and not isinstance(position, QPoint):
                logger.warning(f"Converting position {position} to QPoint")
                position = QCursor.pos()

            dialog_size = emoji_dialog.sizeHint()
            screen_geometry = QApplication.primaryScreen().geometry()

            # Расчитываем позицию так, чтобы диалог не выходил за пределы экрана
            x = min(position.x(), screen_geometry.width() - dialog_size.width())
            y = min(position.y(), screen_geometry.height() - dialog_size.height())

            emoji_dialog.move(x, y)
            logger.info(f"Positioned emoji dialog at {x},{y}")

            # Показываем диалог
            result = emoji_dialog.exec()
            logger.info(f"Emoji dialog result: {result}")

            return result == QDialog.Accepted

        except Exception as e:
            logger.error(f"Error showing emoji selector: {e}")
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr(
                    "dialog.emoji_error", "Could not load emoji selector: {error}"
                ).format(error=str(e)),
            )
            return False

    def _insert_emoji(self, emoji):
        """Вставляет выбранный эмодзи в поле ввода."""
        current_text = self.message_input.text()
        current_pos = self.message_input.cursorPosition()

        # Вставляем эмодзи в текущую позицию курсора
        new_text = current_text[:current_pos] + emoji + current_text[current_pos:]
        self.message_input.setText(new_text)

        # Перемещаем курсор после вставленного эмодзи
        self.message_input.setCursorPosition(current_pos + len(emoji))

        # Возвращаем фокус на поле ввода
        self.message_input.setFocus()

    def _attach_file(self):
        """Прикрепляет файл к сообщению."""
        try:
            # Открываем диалог выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("dialog.select_file", "Select File"),
                "",
                tr("dialog.all_files", "All Files (*)"),
            )

            if file_path:
                # Вставляем упоминание о файле в поле ввода
                file_name = os.path.basename(file_path)
                self.message_input.setText(
                    f"{self.message_input.text()} [File: {file_name}]"
                )

                # Здесь можно добавить логику для фактического прикрепления файла
                # к сообщению в чате (хранение в памяти/отправка и т.д.)
                logger.info(f"File attached: {file_path}")
        except Exception as e:
            logger.error(f"Error attaching file: {e}")
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.file_error", "Could not attach file: {error}").format(
                    error=str(e)
                ),
            )

    def _attach_image(self):
        """Прикрепляет изображение к сообщению."""
        try:
            # Открываем диалог выбора изображения
            image_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("dialog.select_image", "Select Image"),
                "",
                tr(
                    "dialog.image_files", "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
                ),
            )

            if image_path:
                # Вставляем упоминание об изображении в поле ввода
                image_name = os.path.basename(image_path)
                self.message_input.setText(
                    f"{self.message_input.text()} [Image: {image_name}]"
                )

                # Здесь можно добавить логику для фактического прикрепления изображения
                # к сообщению в чате (хранение в памяти/отправка и т.д.)
                logger.info(f"Image attached: {image_path}")
        except Exception as e:
            logger.error(f"Error attaching image: {e}")
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.image_error", "Could not attach image: {error}").format(
                    error=str(e)
                ),
            )

    def closeEvent(self, event: QCloseEvent):
        """Обработчик события закрытия диалога."""
        try:
            # Сохраняем размеры и позицию окна
            settings = QSettings()
            settings.setValue("coding_agent_dialog/geometry", self.saveGeometry())
            settings.setValue("coding_agent_dialog/size", self.size())
            settings.setValue("coding_agent_dialog/pos", self.pos())
            logger.info("Сохранены размер и позиция окна Coding Agent")

            # Останавливаем работу агента
            if hasattr(self, "agent_interface") and self.agent_interface:
                self.agent_interface.stop_agent()

                # Убираем асинхронный вызов cleanup, делаем его синхронно
                # asyncio.create_task(self.cleanup()) - было неправильно
                self.cleanup_sync()

            # Принимаем событие закрытия
            event.accept()
        except Exception as e:
            logger.error(f"Ошибка при закрытии диалога: {e}")
            event.accept()

    def cleanup_sync(self):
        """Синхронная версия метода cleanup для корректного закрытия ресурсов."""
        try:
            # Останавливаем агента
            if hasattr(self, "agent_interface") and self.agent_interface:
                self.agent_interface.stop_agent()

                # Отменяем регистрацию компонента через AgentController
                from app.logic.agent_controller import AgentController
                from app.ui.agent_ui_integration import CODING_AGENT_COMPONENT_ID

                controller = AgentController.instance()
                controller.unregister_component(CODING_AGENT_COMPONENT_ID)

                logger.info("Ресурсы Coding Agent Dialog успешно очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов Coding Agent Dialog: {e}")

    async def cleanup(self):
        """Асинхронный метод очистки ресурсов (оставлен для обратной совместимости)."""
        try:
            if hasattr(self, "agent_interface") and self.agent_interface:
                await self.agent_interface.cleanup()
                logger.info(
                    "Асинхронная очистка ресурсов Coding Agent Dialog выполнена"
                )
        except Exception as e:
            logger.error(f"Ошибка при асинхронной очистке ресурсов: {e}")
