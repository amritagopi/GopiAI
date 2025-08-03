# --- START OF FILE chat_widget.py ---

import logging
import time
import os
import html
import re
from typing import Optional, cast
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                               QFileDialog, QSizePolicy, QMessageBox, QListWidget, QListWidgetItem, QTabWidget)
from PySide6.QtCore import Qt, Slot, QPoint, QTimer
from PySide6.QtGui import QResizeEvent, QTextCursor, QDropEvent, QDragEnterEvent, QTextCursor, QTextCharFormat, QColor, QTextOption
import uuid
from datetime import datetime
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImageWriter
from PySide6.QtCore import QUrl, QMimeData
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMessageBox

# Импорт виджетов моделей
try:
    from .unified_model_widget import UnifiedModelWidget
    # Оставляем старые импорты для совместимости
    from .openrouter_model_widget import OpenRouterModelWidget
    from .model_selector_widget import ModelSelectorWidget
except ImportError as e:
    print(f"Не удалось импортировать виджеты моделей: {e}")
    UnifiedModelWidget = None
    OpenRouterModelWidget = None
    ModelSelectorWidget = None

logger = logging.getLogger(__name__)

# --- Импорты наших новых модулей-обработчиков ---
from .crewai_client import CrewAIClient
from ..memory import get_memory_manager
from .chat_async_handler import ChatAsyncHandler
# from .optimized_chat_widget import OptimizedChatWidget  # Модуль не найден, закомментировано
from .icon_file_system_model import UniversalIconManager
from .terminal_widget import TerminalWidget
from .error_display import ErrorDisplayWidget

class ChatWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setAcceptDrops(True)
        
        self.session_id = None
        self._waiting_message_id = None
        self.theme_manager = None
        self.current_tool = None
        self._animation_timer = None
        self._pending_updates = []
        self._is_updating = False
        self.attached_files = []
        
        # Информация о выбранной модели
        self.current_provider = "gemini"  # По умолчанию Gemini
        self.current_model_id = None
        self.current_model_data = None
        
        logger.info("[CHAT] Инициализация ChatWidget начата")
        
        logger.info("[CHAT] Инициализация менеджера памяти")
        self.memory_manager = get_memory_manager()
        
        # Инициализация виджета отображения ошибок
        self.error_display = ErrorDisplayWidget(self)
        self.error_display.setVisible(False)  # Скрыт по умолчанию
        self.error_display.retryRequested.connect(self._handle_error_retry)
        self.error_display.dismissRequested.connect(self._handle_error_dismiss)
        
        self._setup_ui()
        
        self._setup_animation_timer()
        
        self._initialize_session_and_history()
        
        logger.info("[CHAT] Инициализация CrewAI клиента")
        self.crew_ai_client = CrewAIClient()
        
        logger.info("[CHAT] Инициализация объединенного обработчика сообщений")
        self.async_handler = ChatAsyncHandler(self.crew_ai_client, self)
        
        logger.info("[CHAT] Подключение сигналов объединенного обработчика")
        self.async_handler.response_ready.connect(self._handle_response)
        self.async_handler.status_update.connect(self._update_status_message)
        self.async_handler.partial_response.connect(self._handle_partial_response)
        self.async_handler.message_error.connect(self._handle_error)
        
        logger.info("[CHAT] Инициализация ChatWidget завершена")

    def _handle_error(self, error_message):
        """Обрабатывает ошибки от асинхронного обработчика"""
        if self._animation_timer is not None:
            self._animation_timer.stop()
        
        # Удаляем статусное сообщение
        doc = self.history.document()
        cursor = doc.find('id="status_msg"')
        if cursor:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
        
        # Включаем кнопку отправки обратно
        self.send_btn.setEnabled(True)
        
        # Определяем тип ошибки и отображаем соответствующее сообщение
        if isinstance(error_message, dict):
            error_code = error_message.get('error_code', 'UNKNOWN_ERROR')
            message = error_message.get('message', str(error_message))
            
            if error_code == 'CONNECTION_ERROR':
                self.show_connection_error()
            elif error_code == 'API_ERROR':
                self.show_api_error(message, error_code)
            elif error_code == 'TIMEOUT_ERROR':
                self.show_api_error(message, error_code)
            else:
                self.error_display.show_generic_error("Ошибка системы", message)
        else:
            # Анализируем текст ошибки для определения типа
            error_text = str(error_message).lower()
            
            if 'connection' in error_text or 'подключ' in error_text:
                self.show_connection_error()
            elif 'timeout' in error_text or 'таймаут' in error_text:
                self.show_api_error(str(error_message), 'TIMEOUT_ERROR')
            elif 'api' in error_text or 'сервер' in error_text:
                self.show_api_error(str(error_message), 'API_ERROR')
            else:
                self.error_display.show_generic_error("Ошибка", str(error_message))
        
        logger.error(f"[CHAT_ERROR] {error_message}")

    def _setup_animation_timer(self):
        """Настраивает таймер для анимации точек загрузки"""
        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(500)  # 500ms между обновлениями
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_dots = 0

    def _update_animation(self):
        """Обновляет анимацию точек в статусном сообщении"""
        if hasattr(self, '_current_status_text'):
            self._animation_dots = (self._animation_dots + 1) % 4
            dots = "." * self._animation_dots
            self._update_status_display(f"{self._current_status_text}{dots}")

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)  # Cleaner tab style, no extra labels

        # Chat tab
        self.chat_area_widget = QWidget()
        self.chat_area_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chat_area_layout = QVBoxLayout(self.chat_area_widget)
        chat_area_layout.setContentsMargins(0, 0, 0, 0)

        # Используем обычный QTextEdit вместо OptimizedChatWidget (временно)
        self.history = QTextEdit(self)
        self.history.setObjectName("ChatHistory")
        self.history.setReadOnly(True)
        # Применяем базовые стили
        self.history.setStyleSheet(self._get_basic_chat_styles())
        
        chat_area_layout.addWidget(self.history)
        self.tab_widget.addTab(self.chat_area_widget, "Чат")

        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.sessions_list = QListWidget()
        sessions = sorted(self.memory_manager.list_sessions(), key=lambda s: s.get('created_at', '0'), reverse=True)
        for sess in sessions:
            item = QListWidgetItem(sess.get('title', sess['id']))
            item.setData(Qt.ItemDataRole.UserRole, sess['id'])
            self.sessions_list.addItem(item)
        self.sessions_list.itemClicked.connect(self._load_session_history)
        self.sessions_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self._show_history_context_menu)  # type: ignore[attr-defined]
        history_layout.addWidget(self.sessions_list)
        self.tab_widget.addTab(history_tab, "История")

        # Вкладка моделей с переключателем Gemini/OpenRouter
        try:
            from .unified_models_tab import UnifiedModelsTab
            self.models_tab = UnifiedModelsTab()
            self.tab_widget.addTab(self.models_tab, "Модели")
            
            # Подключаем сигналы
            self.models_tab.provider_changed.connect(self._on_provider_changed)
            self.models_tab.model_changed.connect(self._on_model_changed)
            
            logger.info("✅ Вкладка моделей с переключателем инициализирована")
        except ImportError:
            logger.warning("⚠️ UnifiedModelsTab недоступен, используем fallback")
            
            # Fallback: старая вкладка OpenRouter
            if OpenRouterModelWidget:
                self.openrouter_widget = OpenRouterModelWidget()
                self.tab_widget.addTab(self.openrouter_widget, "OpenRouter")
                
                # Подключаем сигналы
                self.openrouter_widget.model_selected.connect(self._on_openrouter_model_selected)
                self.openrouter_widget.provider_switch_requested.connect(self._on_provider_switch_requested)
                
                logger.info("✅ Fallback: вкладка OpenRouter восстановлена")

        # Вкладка персонализации
        try:
            from .personality_tab import PersonalityTab
            self.personality_tab = PersonalityTab()
            self.tab_widget.addTab(self.personality_tab, "Персонализация")
            
            logger.info("✅ Вкладка персонализации инициализирована")
        except ImportError:
            logger.warning("⚠️ PersonalityTab недоступен")

        self.main_layout.addWidget(self.tab_widget, 1)
        
        # Добавляем виджет отображения ошибок
        self.main_layout.addWidget(self.error_display)

        self._setup_bottom_panel()

    def _show_history_context_menu(self, pos):
        item = self.sessions_list.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        delete_action = menu.addAction('Удалить')
        delete_action.triggered.connect(lambda: self._delete_session(item))
        menu.exec(self.sessions_list.viewport().mapToGlobal(pos))

    def _delete_session(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if not session_id:
            logger.debug("[DELETE] No session_id, skipping")
            return
        logger.debug(f"[DELETE] Requesting delete for {session_id}")
        try:
            msg_box = QMessageBox()
            msg_box.setWindowModality(Qt.WindowModality.NonModal)
            msg_box.setText(f'Удалить сессию {session_id}?')
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            result = msg_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                logger.debug(f"[DELETE] Confirmed delete for {session_id}")
                self.memory_manager.delete_session(session_id)
                self.sessions_list.takeItem(self.sessions_list.row(item))
                if self.session_id == session_id:
                    self.session_id = None
                    self.history.clear()
                logger.debug(f"[DELETE] Session {session_id} deleted")
        except Exception as e:
            logger.error(f"[DELETE] Error in confirmation dialog: {e}")

    def _setup_bottom_panel(self):
        """Настраивает нижнюю панель с полем ввода и кнопками"""
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(6)
        
        self.input = QTextEdit(self)
        self.input.setPlaceholderText("Введите сообщение...")
        self.input.setObjectName("ChatInput")
        self.input.setFixedHeight(80)
        self.input.keyPressEvent = self._input_key_press_event
        bottom_layout.addWidget(self.input, 1)

        self._setup_action_buttons(bottom_layout)
        
        self.main_layout.addWidget(bottom_container)

    def resizeEvent(self, event: QResizeEvent):
        """Обрабатывает изменение размера виджета"""
        super().resizeEvent(event)
        if hasattr(self, 'history'):
            self.history.document().setTextWidth(self.history.viewport().width())
            self.history.document().adjustSize()

    def _setup_action_buttons(self, parent_layout):
        """Настраивает кнопки действий"""
        icon_mgr = UniversalIconManager.instance()
        action_buttons_layout = QVBoxLayout()
        
        # Кнопка прикрепления файла
        self.attach_file_btn = QPushButton(icon_mgr.get_icon("paperclip"), "", self)
        self.attach_file_btn.setToolTip("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        action_buttons_layout.addWidget(self.attach_file_btn)
        
        # Кнопка прикрепления изображения
        self.attach_image_btn = QPushButton(icon_mgr.get_icon("image"), "", self)
        self.attach_image_btn.setToolTip("Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        action_buttons_layout.addWidget(self.attach_image_btn)
        
        parent_layout.addLayout(action_buttons_layout)

        # Кнопка отправки
        self.send_btn = QPushButton(icon_mgr.get_icon("send"), "", self)
        self.send_btn.setToolTip("Отправить сообщение")
        self.send_btn.setFixedSize(40, 80)
        self.send_btn.clicked.connect(self.send_message)
        parent_layout.addWidget(self.send_btn)

    def _get_basic_chat_styles(self) -> str:
        """Возвращает базовые стили для обычного QTextEdit"""
        return """
        QTextEdit {
            border-radius: 8px;
            padding: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
        }
        """

    def _get_markdown_styles(self) -> str:
        """Возвращает адаптивные CSS стили для элегантного чата"""
        return """
        :root {
            --user-bg: rgba(0, 120, 255, 0.15); /* Лёгкий синий, адаптивный */
            --assistant-bg: rgba(128, 128, 128, 0.1); /* Лёгкий серый */
            --text-color: inherit; /* Адаптируется к глобальной теме */
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            padding: 8px;
            color: var(--text-color);
            background: transparent;
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-all;
        }
        
        .message {
            max-width: 75%;
            margin: 6px 0;
            padding: 8px 12px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            animation: fadeIn 0.3s ease-out;
            transition: all 0.2s ease;
            display: inline-block;
            position: relative;
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-all;
        }
        
        .message:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--user-bg), transparent);
            margin-left: auto;
            text-align: right;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, var(--assistant-bg), transparent);
            margin-right: auto;
            text-align: left;
        }
        
        .system-message {
            background: rgba(255, 193, 7, 0.05);
            font-style: italic;
            text-align: center;
            margin: 0 auto;
            opacity: 0.8;
            border-radius: 10px;
        }
        
        .error-message {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            text-align: center;
        }
        
        .status-message {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
            margin: 10px auto;
        }
        
        .spinner {
            border: 3px solid rgba(0,0,0,0.1);
            border-top: 3px solid var(--user-bg);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        
        .avatar {
            display: inline-block;
            width: 24px;
            height: 24px;
            margin: 0 4px;
            vertical-align: middle;
            border-radius: 50%;
        }
        
        .user-avatar {
            background-color: var(--user-bg);
            position: relative;
        }
        
        .user-avatar:after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 12px;
            height: 12px;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 50%;
        }
        
        .assistant-avatar {
            background-color: var(--assistant-bg);
            position: relative;
        }
        
        .assistant-avatar:after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 14px;
            height: 8px;
            border: 2px solid rgba(0, 0, 0, 0.2);
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
        
        .timestamp {
            font-size: 0.7em;
            opacity: 0.6;
            margin-top: 2px;
            text-align: right;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Markdown стили */
        h1, h2, h3 { margin: 8px 0; }
        code { background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; }
        pre { background: rgba(0,0,0,0.05); padding: 8px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 300px; }
        a { color: inherit; text-decoration: underline; }
        blockquote { border-left: 2px solid rgba(0,0,0,0.2); padding-left: 8px; opacity: 0.9; }
        """

    def _render_markdown(self, text: str) -> str:
        """Улучшенная функция рендеринга markdown в HTML"""
        if not text:
            return ""
            
        # Экранируем HTML символы, сохраняя уже существующие HTML теги
        text = self._safe_html_escape(text)
        
        # Обработка блоков кода с разбивкой длинных строк
        def insert_zws(match):
            code = match.group(1)
            # Вставляем zero-width space каждые 80 chars в длинных строках
            lines = []
            for line in code.splitlines():
                if len(line) > 80:
                    line = ''.join(c + '&#8203;' if i > 0 and i % 80 == 0 else c for i, c in enumerate(line))
                lines.append(line)
            return f'<pre><code>{"\n".join(lines)}</code></pre>'
        
        text = re.sub(r'```([^`]*?)```', insert_zws, text)
        
        # Обработка инлайн-кода (тоже с zws для очень длинных)
        def inline_zws(match):
            code = match.group(1)
            if len(code) > 80:
                code = ''.join(c + '&#8203;' if i > 0 and i % 80 == 0 else c for i, c in enumerate(code))
            return f'<code>{code}</code>'
        
        text = re.sub(r'`([^`]+)`', inline_zws, text)
        
        # Заголовки
        for i in range(6, 0, -1):
            pattern = r'^{} (.+)$'.format('#' * i)
            text = re.sub(pattern, r'<h{0}>\1</h{0}>'.format(i), text, flags=re.MULTILINE)
        
        # Жирный текст
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Курсив
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Списки
        text = re.sub(r'^\* (.+)$', r'<ul><li>\1</li></ul>', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.+)$', r'<ol><li>\1</li></ol>', text, flags=re.MULTILINE)
        
        # Ссылки
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Горизонтальная линия
        text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
        
        # Параграфы (только для строк, которые не являются HTML)
        lines = []
        for line in text.split('\n'):
            if line.strip() and not line.strip().startswith(('<', '>')):
                lines.append(f'<p>{line}</p>')
            else:
                lines.append(line)
        
        return '\n'.join(lines)

    def _safe_html_escape(self, text: str) -> str:
        """Безопасное экранирование HTML с сохранением существующих тегов"""
        chunks = []
        last_pos = 0
        
        for match in re.finditer(r'<[^>]+>', text):
            start, end = match.span()
            # Экранируем текст до тега
            if start > last_pos:
                chunks.append(html.escape(text[last_pos:start]))
            # Сохраняем тег как есть
            chunks.append(text[start:end])
            last_pos = end
            
        # Добавляем оставшийся текст
        if last_pos < len(text):
            chunks.append(html.escape(text[last_pos:]))
            
        return ''.join(chunks)

    def send_message(self):
        """Отправляет сообщение"""
        logger.debug("[CHAT] Вызван метод send_message")
        
        text = self.input.toPlainText().strip()
        if not text:
            return
            
        # Очищаем поле ввода и блокируем кнопку
        self.input.clear()
        self.send_btn.setEnabled(False)
        
        # Добавляем сообщение пользователя
        self._append_message_with_style("user", text)
        
        # Добавляем индикатор загрузки
        self._show_loading_indicator()
        
        # Сохраняем в память, если сессия инициализирована
        if self.session_id:
            self.memory_manager.add_message(self.session_id, "user", text)
        else:
            logger.warning("[CHAT] Session not initialized, message not saved")

        # Запускаем асинхронную обработку
        message_data = {
            "message": text,
            "metadata": {
                "session_id": self.session_id,
                "current_tool": self.current_tool,
                "attachments": self.attached_files,
                # Добавляем информацию о выбранной модели
                "model_provider": self.current_provider,
                "model_id": self.current_model_id,
                "model_data": self.current_model_data
            }
        }
        
        # Логируем информацию о выбранной модели
        logger.info(f"[CHAT] Отправка сообщения с провайдером: {self.current_provider}")
        if self.current_model_id:
            logger.info(f"[CHAT] Выбранная модель: {self.current_model_id}")
        # Извлекаем текст сообщения и метаданные для ImprovedAsyncChatHandler
        message_text = message_data.get("message", "")
        metadata = message_data.get("metadata", {})
        
        # Вызываем правильный метод
        self.async_handler.send_message(message_text, metadata)
        self.attached_files = []

    def _show_loading_indicator(self):
        """Показывает индикатор загрузки с анимацией"""
        self._current_status_text = "Обрабатываю запрос"
        status_html = f"""
        <div id="status_msg" class="status-message">
            <div class="spinner"></div>
            {self._current_status_text}
        </div>
        """
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(status_html)
        self._scroll_history_to_end()
        if self._animation_timer is not None:
            self._animation_timer.start()

    def _append_message_with_style(self, role: str, text: str):
        """Добавляет сообщение с соответствующим стилем"""
        msg_id = 'status_msg' if role == 'status' else f'msg_{uuid.uuid4().hex[:8]}'
        
        style_class = {
            "user": "user-message",
            "assistant": "assistant-message",
            "system": "system-message",
            "error": "error-message",
            "status": "status-message"
        }.get(role, "message")
        
        formatted_text = self._render_markdown(text) if role in ["assistant", "system"] else html.escape(text)
        
        author = {
            "user": "Вы",
            "assistant": "Ассистент",
            "system": "Система",
            "error": "Ошибка",
            "status": "Статус"
        }.get(role, "")
        
        # Используем CSS классы вместо эмодзи для аватаров
        avatar = ''
        if role == 'user':
            avatar = '<span class="avatar user-avatar"></span>'
        elif role == 'assistant':
            avatar = '<span class="avatar assistant-avatar"></span>'
        
        timestamp = datetime.now().strftime('%H:%M')
        
        message_html = f"""
        <div id="{msg_id}" class="message {style_class}">
            {avatar}
            <b>{author}:</b> {formatted_text}
            <div class="timestamp">{timestamp}</div>
        </div>
        """
        
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(message_html)
        self.history.setTextCursor(cursor)
        self.history.document().setTextWidth(self.history.viewport().width())
        self.history.document().adjustSize()
        self.history.ensureCursorVisible()
        self._scroll_history_to_end()

    def _update_status_display(self, text: str):
        """Обновляет текст статусного сообщения без повторного добавления"""
        doc = self.history.document()
        cursor = doc.find('id="status_msg"')
        if cursor:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            updated_html = f"""
            <div id="status_msg" class="status-message">
                <div class="spinner"></div>
                {text}
            </div>
            """
            cursor.insertHtml(updated_html)
            self.history.document().setTextWidth(self.history.viewport().width())
            self.history.document().adjustSize()
            self.history.ensureCursorVisible()
            self._scroll_history_to_end()

    @Slot(str)
    def _update_status_message(self, status_text: str):
        """Обновляет статусное сообщение с анимацией"""
        self._current_status_text = status_text
        self._update_status_display(f"{status_text}...")

    def _handle_response(self, response):
        """Обрабатывает ответ от асинхронного обработчика"""
        if self._animation_timer is not None:
            self._animation_timer.stop()
        
        # Удаляем статусное сообщение
        doc = self.history.document()
        cursor = doc.find('id="status_msg"')
        if cursor:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
        
        # Включаем кнопку отправки обратно
        self.send_btn.setEnabled(True)
        
        # Проверяем, является ли ответ ошибкой
        if isinstance(response, dict) and response.get('status') == 'error':
            self._handle_error(response)
            return
        
        # Обрабатываем успешный ответ
        if isinstance(response, dict):
            if 'terminal_output' in response:
                self._handle_terminal_output(response['terminal_output'])
                full_message = response.get('response', 'Command executed in terminal. See terminal tab for output.')
            else:
                # Извлекаем текст ответа из словаря
                full_message = response.get('response', str(response))
        else:
            full_message = self._clean_response_message(str(response))
        
        # Очищаем сообщение от пустых строк
        full_message = "\n".join(line for line in full_message.splitlines() if line.strip())
        self._append_message_with_style("assistant", full_message)
        if self.session_id:
            self.memory_manager.add_message(self.session_id, "assistant", full_message)

    @Slot(str)
    def _handle_partial_response(self, partial_text: str):
        """Обрабатывает частичные ответы для streaming отображения"""
        # Fallback для обычного QTextEdit
        cursor = self.history.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(partial_text)
        self.history.setTextCursor(cursor)
        
        self._scroll_history_to_end()

    def _append_message_with_style(self, role: str, message: str):
        """Метод для добавления сообщений с базовым стилем"""
        # Используем обычный QTextEdit
        timestamp = datetime.now().strftime("%H:%M")
        role_class = f"{role}-message"
        avatar_class = f"{role}-avatar"
        
        html_message = f"""
        <div class="message {role_class}">
            <div class="avatar {avatar_class}"></div>
            {self._render_markdown(message)}
            <div class="timestamp">{timestamp}</div>
        </div>
        """
        
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html_message)
        
        self._scroll_history_to_end()

    def _handle_terminal_output(self, term_out: dict):
        """Отображает вывод терминала в чате"""
        formatted = f"Команда: {term_out.get('command', '')}\nВывод: {term_out.get('output', '')}\nОшибки: {term_out.get('error', 'Нет')}"
        self._append_message_with_style("system", formatted)

    def _clean_response_message(self, message: str) -> str:
        """Расширенная очистка от лишних символов и меток"""
        import re
        # Удаляем JSON артефакты
        match = re.search(r"'response':\s*['\"](.*?)['\"]", message, re.DOTALL)
        if match:
            message = match.group(1).strip()
        
        # Удаляем системные префиксы/суффиксы
        message = re.sub(r"^\{.*'response':", '', message, flags=re.DOTALL)
        message = re.sub(r"\}.*$", '', message, flags=re.DOTALL)
        message = re.sub(r"analysis\.time: [\d.]+, 'complexity': \d+, 'requires\.crewai': (True|False), 'type': '[^']+', 'processed\.with_crewai': (True|False),", '', message)
        
        # Удаляем лишние символы: кавычки, скобки, даты, тесты
        message = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", '', message)  # Даты
        message = re.sub(r"Тестовая запись от.*", '', message)  # Тестовые метки
        message = message.strip("'\"{}[]() \n")
        
        message = message.replace('\\n', '\n')
        
        return message

    def _scroll_history_to_end(self):
        scrollbar = self.history.verticalScrollBar()
        QTimer.singleShot(0, lambda: scrollbar.setValue(scrollbar.maximum()))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    name = os.path.basename(path)
                    ext = os.path.splitext(name)[1].lower()
                    att_type = 'image' if ext in ['.png', '.jpg', '.jpeg'] else 'file'
                    self.attached_files.append({'path': path, 'type': att_type})
                    self._append_message_with_style('system', f'{att_type.capitalize()} dropped: {name}')
        elif mime.hasImage():
            image = mime.imageData()
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                writer = QImageWriter(tmp.name, b'png')
                if writer.write(image):
                    self.attached_files.append({'path': tmp.name, 'type': 'image'})
                    self._append_message_with_style('system', 'Image pasted from clipboard')
        event.acceptProposedAction()

    def _input_key_press_event(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.send_message()
            event.accept()
        elif event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            if mime.hasImage():
                image = clipboard.image()
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    writer = QImageWriter(tmp.name, b'png')
                    if writer.write(image):
                        self.attached_files.append({'path': tmp.name, 'type': 'image'})
                        self._append_message_with_style('system', 'Image pasted from clipboard')
            elif mime.hasUrls():
                for url in mime.urls():
                    if url.isLocalFile():
                        path = url.toLocalFile()
                        name = os.path.basename(path)
                        ext = os.path.splitext(name)[1].lower()
                        att_type = 'image' if ext in ['.png', '.jpg', '.jpeg'] else 'file'
                        self.attached_files.append({'path': path, 'type': att_type})
                        self._append_message_with_style('system', f'{att_type.capitalize()} pasted: {name}')
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.input, event)
            
    def attach_file(self):
        """Обработчик прикрепления файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            logger.info(f"Файл прикреплен: {os.path.basename(file_path)}")
            self._append_message_with_style("system", f"Файл прикреплен: {os.path.basename(file_path)}")
            self.attached_files.append({"path": file_path, "type": "file"})

    def attach_image(self):
        """Обработчик прикрепления изображения"""
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение",
            filter="Images (*.png *.jpg *.jpeg)"
        )
        if image_path:
            logger.info(f"Изображение прикреплено: {os.path.basename(image_path)}")
            self._append_message_with_style("system", f"Изображение прикреплено: {os.path.basename(image_path)}")
            self.attached_files.append({"path": image_path, "type": "image"})

    def show_context_stats(self):
        """Показывает статистику контекста"""
        QMessageBox.information(self, "Статистика", "Логика статистики будет добавлена позже.")
        
    def set_theme_manager(self, theme_manager):
        """Устанавливает менеджер тем"""
        self.theme_manager = theme_manager
        self.apply_theme()

    def apply_theme(self):
        """Применяет текущую тему"""
        if self.theme_manager:
            # TODO: Реализовать применение темы
            pass
        logger.info("Theme applied to ChatWidget")
        
    def _initialize_session_and_history(self):
        self.session_id = f"session_{int(time.time())}"
        logger.info(f"[CHAT] Создана новая сессия: {self.session_id}")
        self._load_history()

    def _load_history(self):
        """Загружает и отображает историю сообщений из памяти для текущей сессии"""
        if not self.session_id:
            logger.warning("[CHAT] Сессия не инициализирована, история не загружена")
            return
        
        try:
            messages = self.memory_manager.get_chat_history(self.session_id)
        except AttributeError:
            logger.warning("[CHAT] Метод get_chat_history не найден в MemoryManager")
            messages = []
        
        if not messages:
            logger.info("[CHAT] Нет сохраненных сообщений для сессии")
            return
        
        logger.info(f"[CHAT] Загрузка {len(messages)} сообщений из истории")
        for msg in messages:
            role = msg.get('role', 'system')
            content = msg.get('content', '')
            if role == 'user':
                self._append_message_with_style('user', content)
            elif role == 'assistant':
                self._append_message_with_style('assistant', content)
            else:
                self._append_message_with_style('system', content)
        
        # Прокручиваем к концу после загрузки
        self._scroll_history_to_end()

    def _load_session_history(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_id = session_id
        self.history.clear()
        self._load_history()
        self.tab_widget.setCurrentIndex(0)  # Switch to Chat tab

    # === Обработчики сигналов для виджетов моделей ===
    
    def _on_provider_changed(self, provider: str):
        """Обработчик изменения провайдера"""
        self.current_provider = provider
        logger.info(f"[MODEL] Провайдер изменен на: {provider}")
        
        # Сбрасываем информацию о модели при смене провайдера
        if provider == "gemini":
            self.current_model_id = None
            self.current_model_data = None
        
        print(f"Провайдер изменен на: {provider}")
    
    def _on_model_changed(self, provider: str, model_id: str):
        """Обработчик изменения модели"""
        self.current_provider = provider
        self.current_model_id = model_id
        logger.info(f"[MODEL] Модель изменена: {provider}/{model_id}")
        print(f"Модель изменена: {provider}/{model_id}")
    
    def _on_openrouter_model_selected(self, model_data: dict):
        """Обработчик выбора модели OpenRouter"""
        model_id = model_data.get('id', 'unknown')
        self.current_provider = "openrouter"
        self.current_model_id = model_id
        self.current_model_data = model_data
        
        logger.info(f"[MODEL] Выбрана модель OpenRouter: {model_id}")
        logger.debug(f"[MODEL] Данные модели: {model_data}")
        print(f"Выбрана модель OpenRouter: {model_id}")
    
    def _on_provider_switch_requested(self, provider: str):
        """Обработчик запроса переключения провайдера"""
        print(f"Запрос переключения на провайдера: {provider}")
        
        # Переключаемся на соответствующую вкладку
        if provider == "gemini" and hasattr(self, 'model_selector_widget'):
            # Находим индекс вкладки с ModelSelectorWidget
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.model_selector_widget:
                    self.tab_widget.setCurrentIndex(i)
                    break
        elif provider == "openrouter" and hasattr(self, 'openrouter_widget'):
            # Находим индекс вкладки с OpenRouterModelWidget
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.openrouter_widget:
                    self.tab_widget.setCurrentIndex(i)
                    break
    
    def get_openrouter_widget(self):
        """Возвращает виджет OpenRouter для внешнего доступа"""
        return getattr(self, 'openrouter_widget', None)
    
    def get_model_selector_widget(self):
        """Возвращает виджет выбора моделей для внешнего доступа"""
        return getattr(self, 'model_selector_widget', None)
    
    def switch_to_openrouter_tab(self):
        """Переключается на вкладку OpenRouter"""
        if hasattr(self, 'openrouter_widget'):
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.openrouter_widget:
                    self.tab_widget.setCurrentIndex(i)
                    print("Переключились на вкладку OpenRouter")
                    return True
        return False
    
    def switch_to_model_selector_tab(self):
        """Переключается на вкладку выбора моделей"""
        if hasattr(self, 'model_selector_widget'):
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.model_selector_widget:
                    self.tab_widget.setCurrentIndex(i)
                    print("Переключились на вкладку выбора моделей")
                    return True
        return False
    
    def _handle_error_retry(self, error_type: str):
        """Обрабатывает запрос повтора операции после ошибки"""
        logger.info(f"[ERROR_RETRY] Повтор операции для типа ошибки: {error_type}")
        
        if error_type == "connection":
            # Повторная проверка соединения с сервером
            self._retry_connection()
        elif error_type == "api":
            # Повтор последнего API запроса
            self._retry_last_message()
        elif error_type == "component":
            # Попытка перезагрузки компонента
            self._retry_component_initialization()
        elif error_type == "tool":
            # Повтор выполнения инструмента
            self._retry_tool_execution()
        else:
            logger.warning(f"[ERROR_RETRY] Неизвестный тип ошибки для повтора: {error_type}")
    
    def _handle_error_dismiss(self):
        """Обрабатывает закрытие сообщения об ошибке"""
        logger.debug("[ERROR_DISMISS] Ошибка закрыта пользователем")
        # Дополнительная логика при необходимости
    
    def _retry_connection(self):
        """Повторная попытка подключения к серверу"""
        try:
            from .api.client import get_default_client
            client = get_default_client()
            
            if client.health_check():
                self.error_display.setVisible(False)
                self._append_message_with_style("system", "✅ Соединение с сервером восстановлено")
                logger.info("[RETRY] Соединение с сервером восстановлено")
            else:
                self.error_display.show_connection_error("Backend Server")
                logger.warning("[RETRY] Сервер по-прежнему недоступен")
        except Exception as e:
            logger.error(f"[RETRY] Ошибка при проверке соединения: {e}")
            self.error_display.show_generic_error(
                "Ошибка повтора",
                f"Не удалось проверить соединение: {str(e)}"
            )
    
    def _retry_last_message(self):
        """Повторная отправка последнего сообщения"""
        try:
            # Получаем последнее сообщение пользователя из истории
            last_user_message = self._get_last_user_message()
            if last_user_message:
                logger.info(f"[RETRY] Повторная отправка сообщения: {last_user_message[:50]}...")
                self.error_display.setVisible(False)
                
                # Отправляем сообщение заново
                self._show_loading_indicator()
                message_data = {
                    "message": last_user_message,
                    "metadata": {
                        "session_id": self.session_id,
                        "current_tool": self.current_tool,
                        "model_provider": self.current_provider,
                        "model_id": self.current_model_id,
                        "model_data": self.current_model_data,
                        "retry": True
                    }
                }
                
                self.async_handler.send_message(last_user_message, message_data.get("metadata", {}))
            else:
                logger.warning("[RETRY] Не найдено последнее сообщение для повтора")
                self.error_display.show_generic_error(
                    "Ошибка повтора",
                    "Не найдено сообщение для повторной отправки"
                )
        except Exception as e:
            logger.error(f"[RETRY] Ошибка при повторной отправке сообщения: {e}")
            self.error_display.show_generic_error(
                "Ошибка повтора",
                f"Не удалось повторить отправку: {str(e)}"
            )
    
    def _retry_component_initialization(self):
        """Повторная инициализация компонента"""
        try:
            logger.info("[RETRY] Попытка перезагрузки компонентов")
            self.error_display.setVisible(False)
            
            # Попытка переинициализации критических компонентов
            if not hasattr(self, 'crew_ai_client') or self.crew_ai_client is None:
                self.crew_ai_client = CrewAIClient()
                logger.info("[RETRY] CrewAI клиент переинициализирован")
            
            if not hasattr(self, 'async_handler') or self.async_handler is None:
                self.async_handler = ChatAsyncHandler(self.crew_ai_client, self)
                self.async_handler.response_ready.connect(self._handle_response)
                self.async_handler.status_update.connect(self._update_status_message)
                self.async_handler.partial_response.connect(self._handle_partial_response)
                self.async_handler.message_error.connect(self._handle_error)
                logger.info("[RETRY] Асинхронный обработчик переинициализирован")
            
            self._append_message_with_style("system", "✅ Компоненты успешно перезагружены")
            
        except Exception as e:
            logger.error(f"[RETRY] Ошибка при перезагрузке компонентов: {e}")
            self.error_display.show_component_error(
                "Система",
                f"Не удалось перезагрузить компоненты: {str(e)}",
                fallback_available=False
            )
    
    def _retry_tool_execution(self):
        """Повторное выполнение инструмента"""
        try:
            logger.info("[RETRY] Повтор выполнения инструмента")
            self.error_display.setVisible(False)
            
            # Логика повтора зависит от конкретного инструмента
            # Пока просто скрываем ошибку и уведомляем пользователя
            self._append_message_with_style("system", "🔄 Попробуйте выполнить команду еще раз")
            
        except Exception as e:
            logger.error(f"[RETRY] Ошибка при повторе выполнения инструмента: {e}")
            self.error_display.show_tool_error(
                "Неизвестный инструмент",
                f"Не удалось повторить выполнение: {str(e)}"
            )
    
    def _get_last_user_message(self) -> Optional[str]:
        """Извлекает последнее сообщение пользователя из истории чата"""
        try:
            if self.session_id and self.memory_manager:
                messages = self.memory_manager.get_messages(self.session_id)
                # Ищем последнее сообщение пользователя
                for message in reversed(messages):
                    if message.get('role') == 'user':
                        return message.get('content', '')
            return None
        except Exception as e:
            logger.error(f"[RETRY] Ошибка при получении последнего сообщения: {e}")
            return None
    
    def show_api_error(self, error_message: str, error_code: str = None, retry_available: bool = True):
        """Публичный метод для отображения API ошибок"""
        retry_action = "api" if retry_available else None
        self.error_display.show_api_error(error_message, error_code, retry_action)
    
    def show_connection_error(self, service_name: str = "Backend Server"):
        """Публичный метод для отображения ошибок соединения"""
        self.error_display.show_connection_error(service_name)
    
    def show_component_error(self, component_name: str, error_details: str, fallback_available: bool = False):
        """Публичный метод для отображения ошибок компонентов"""
        self.error_display.show_component_error(component_name, error_details, fallback_available)
    
    def show_tool_error(self, tool_name: str, error_message: str, command: str = None):
        """Публичный метод для отображения ошибок инструментов"""
        self.error_display.show_tool_error(tool_name, error_message, command)