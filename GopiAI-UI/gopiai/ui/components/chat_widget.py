# --- START OF FILE chat_widget.py ---

import logging
import time
import os
import html
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QSizePolicy, QListWidget, QListWidgetItem, QTabWidget
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QResizeEvent, QTextCursor, QTextOption
import uuid
from datetime import datetime
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImageWriter
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMessageBox

# --- Импорты наших новых модулей-обработчиков ---
from .crewai_client import CrewAIClient
from ..memory import get_memory_manager
from .chat_async_handler import ChatAsyncHandler
from gopiai.ui.utils.icon_helpers import create_icon_button
from .enhanced_browser_widget import EnhancedBrowserWidget

# Импорт виджетов моделей
try:
    from .gemini_model_widget import GeminiModelWidget
    # Оставляем старые импорты для совместимости
    from .model_selector_widget import ModelSelectorWidget
except ImportError as e:
    print(f"Не удалось импортировать виджеты моделей: {e}")
    GeminiModelWidget = None
    ModelSelectorWidget = None

logger = logging.getLogger(__name__)

class ChatWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setAcceptDrops(True)
        
        # Опциональные атрибуты для типизатора/проверок
        self.model_selector_widget = None
        self._widget = None

        self.session_id = None
        self._waiting_message_id = None
        self.current_tool = None
        self._animation_timer = None
        self._pending_updates = []
        self._is_updating = False
        self.attached_files = []
        
        # Информация о выбранной модели
        self.current_provider = "gemini"  # По умолчанию Gemini
        self.current_model_id = None
        self.current_model_data = None
        
        # Прикрепленные инструменты и агенты
        self.attached_tools = []
        self.attached_agents = []
        self.attached_flow = None
        # Виджет браузера будет создан лениво
        self.browser_widget = None
        
        logger.info("[CHAT] Инициализация ChatWidget начата")
        
        logger.info("[CHAT] Инициализация менеджера памяти")
        self.memory_manager = get_memory_manager()
        
        self._setup_ui()
        
        self._setup_animation_timer()
        
        self._initialize_session_and_history()
        
        logger.info("[CHAT] Инициализация CrewAI клиента")
        self.crew_ai_client = CrewAIClient()
        
        logger.info("[CHART] Инициализация объединенного обработчика сообщений")
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
        
        # Отображаем ошибку
        self._append_message_with_style("error", f"Ошибка: {error_message}")

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
        # Добавляем обработчик клавиш для области истории
        self.history.keyPressEvent = self._history_key_press_event
        # Включаем корректные переносы и ограничение ширины
        opt = self.history.document().defaultTextOption()
        opt.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.history.document().setDefaultTextOption(opt)
        self.history.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.history.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Применяем объединенные стили (базовые + markdown)
        # Перебиваем глобальные стили и темы: добавляем повышенную специфичность и !important
        def _strong_css(css: str) -> str:
            # оборачиваем правила для повышения специфичности и добавляем !important к ключевым свойствам переноса
            css = css.replace("QTextEdit {", "QTextEdit, QTextEdit#ChatHistory {")
            replacements = [
                ("word-break: break-word;", "word-break: break-word !important;"),
                ("word-wrap: break-word;", "word-wrap: break-word !important;"),
                ("overflow-wrap: anywhere;", "overflow-wrap: anywhere !important;"),
                ("white-space: pre-wrap;", "white-space: pre-wrap !important;"),
                ("max-width: 100%;", "max-width: 100% !important;"),
            ]
            for old, new in replacements:
                css = css.replace(old, new)
            return css
        self.history.setStyleSheet(_strong_css(self._get_basic_chat_styles() + self._get_markdown_styles()))
        
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

        # Вкладка моделей с переключателем Gemini/
        try:
            from .unified_models_tab import UnifiedModelsTab
            self.models_tab = UnifiedModelsTab()
            self.tab_widget.addTab(self.models_tab, "Модели")
            
            # Подключаем сигналы
            # У нас только Gemini провайдер, поэтому provider_changed не нужен
            self.models_tab.model_changed.connect(self._on_model_changed)
            
            logger.info("✅ Вкладка моделей с переключателем инициализирована")
        except ImportError:
            logger.warning("⚠️ UnifiedModelsTab недоступен, используем fallback")
            

        # Вкладка персонализации
        try:
            from .personality_tab import PersonalityTab
            self.personality_tab = PersonalityTab()
            self.tab_widget.addTab(self.personality_tab, "Персонализация")
            
            logger.info("✅ Вкладка персонализации инициализирована")
        except ImportError:
            logger.warning("⚠️ PersonalityTab недоступен")

        # Вкладка инструментов
        try:
            from .tools_tab import ToolsTab
            self.tools_tab = ToolsTab()
            self.tab_widget.addTab(self.tools_tab, "Инструменты")
            
            # Подключаем сигнал для прикрепления инструментов
            self.tools_tab.tools_attached.connect(self._on_tools_attached)
            
            logger.info("✅ Вкладка инструментов инициализирована")
        except ImportError as e:
            logger.warning(f"⚠️ ToolsTab недоступен: {e}")

        # Вкладка агентов и флоу
        try:
            from .agents_tab import AgentsTab
            self.agents_tab = AgentsTab()
            self.tab_widget.addTab(self.agents_tab, "Агенты/Флоу")
            
            # Подключаем сигналы для прикрепления агентов и флоу
            self.agents_tab.agents_attached.connect(self._on_agents_attached)
            self.agents_tab.flow_attached.connect(self._on_flow_attached)
            
            logger.info("✅ Вкладка агентов/флоу инициализирована")
        except ImportError as e:
            logger.warning(f"⚠️ AgentsTab недоступен: {e}")

        self.main_layout.addWidget(self.tab_widget, 1)

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
        self.input.keyPressEvent = self._input_key_press_event
        # Устанавливаем фокус на поле ввода и настраиваем политику фокуса
        self.input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.input.setFocus()
        bottom_layout.addWidget(self.input, 1)

        self._setup_action_buttons(bottom_layout)
        
        self.main_layout.addWidget(bottom_container)

    def _ensure_browser_tab(self):
        """Ленивая инициализация вкладки браузера в основной области с редакторами."""
        try:
            # Получаем главное окно через parent chain
            main_window = self._get_main_window()
            if not main_window or not hasattr(main_window, 'tab_document'):
                logger.error("[BROWSER] Главное окно или tab_document не найдены")
                self._append_message_with_style('error', 'Не удалось найти область редакторов для браузера')
                return False
                
            if self.browser_widget is None:
                self.browser_widget = EnhancedBrowserWidget()
                self.browser_widget.page_loaded.connect(self._on_browser_page_loaded)
                logger.info("[BROWSER] Виджет браузера создан")
            
            # Используем существующий метод для добавления вкладки браузера
            main_window.tab_document.add_browser_tab(title="🌐 Браузер")
            # Находим виджет браузера, чтобы передать ему команды
            self.browser_widget = main_window.tab_document.get_browser_widget()
            if self.browser_widget:
                # Подключаем сигнал только если виджет был успешно получен
                self.browser_widget.page_loaded.connect(self._on_browser_page_loaded)
                logger.info("[BROWSER] Вкладка браузера добавлена/активирована через TabDocumentWidget")
            else:
                logger.error("[BROWSER] Не удалось получить виджет браузера после его создания")
                return False
            return True
        except Exception as e:
            logger.error(f"[BROWSER] Ошибка создания вкладки браузера: {e}")
            self._append_message_with_style('error', f'Не удалось открыть браузер: {e}')
            return False
            
    def _get_main_window(self):
        """Получает ссылку на главное окно через parent chain."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'tab_document'):
                    return parent
                parent = parent.parent()
            return None
        except Exception as e:
            logger.debug(f"[BROWSER] Ошибка поиска главного окна: {e}")
            return None

    def _on_browser_page_loaded(self, url: str, title: str):
        """Отображает статус загрузки страницы браузера в чате."""
        try:
            self._append_message_with_style('system', f"Браузер загрузил страницу: {title}\n{url}")
        except Exception as e:
            logger.debug(f"[BROWSER] _on_browser_page_loaded error: {e}")

    def _apply_browser_actions_from_response(self, response: dict) -> None:
        """Извлекает и выполняет команды браузера из ответа сервера.

        Поддерживаются расположения:
        - response['browser_actions']
        - response['metadata']['browser_actions']
        - response['result']['browser_actions']
        - response['tool_result']['browser_actions']
        Если найдено, гарантирует открытую вкладку браузера и вызывает
        EnhancedBrowserWidget.apply_actions(...).
        """
        try:
            if not isinstance(response, dict):
                return
            candidate_paths = [
                (response, 'browser_actions'),
                (response.get('metadata', {}) if isinstance(response.get('metadata', {}), dict) else {}, 'browser_actions'),
                (response.get('result', {}) if isinstance(response.get('result', {}), dict) else {}, 'browser_actions'),
                (response.get('tool_result', {}) if isinstance(response.get('tool_result', {}), dict) else {}, 'browser_actions'),
            ]
            actions = None
            for container, key in candidate_paths:
                if key in container and container[key]:
                    actions = container[key]
                    break
            # также поддержим вариант, когда инструменты возвращают список действий по ключу 'actions'
            if actions is None and isinstance(response.get('tool_result'), dict):
                maybe = response['tool_result'].get('actions')
                if maybe:
                    actions = maybe
            if not actions:
                return
            # Гарантируем открытую вкладку браузера
            if not self._ensure_browser_tab():
                logger.error("[BROWSER] Не удалось открыть вкладку браузера для применения действий")
                return
            # Применяем действия
            try:
                self.browser_widget.apply_actions(actions)
                self._append_message_with_style('system', 'Выполняю команды в браузере...')
            except Exception as e:
                logger.error(f"[BROWSER] Ошибка выполнения действий браузера: {e}")
                self._append_message_with_style('error', f"Ошибка выполнения действий браузера: {e}")
        except Exception as e:
            logger.debug(f"[BROWSER] _apply_browser_actions_from_response error: {e}")

    def resizeEvent(self, event: QResizeEvent):
        """Обрабатывает изменение размера виджета"""
        super().resizeEvent(event)
        if hasattr(self, 'history'):
            self.history.document().setTextWidth(self.history.viewport().width())
            self.history.document().adjustSize()

    def _setup_action_buttons(self, parent_layout):
        """Настраивает кнопки действий"""
        action_buttons_layout = QVBoxLayout()
        
        # Кнопка прикрепления файла
        self.attach_file_btn = create_icon_button("paperclip", "Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        action_buttons_layout.addWidget(self.attach_file_btn)
        
        # Кнопка прикрепления изображения
        self.attach_image_btn = create_icon_button("image", "Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        action_buttons_layout.addWidget(self.attach_image_btn)
        
        parent_layout.addLayout(action_buttons_layout)

        # Кнопка отправки
        self.send_btn = create_icon_button("send", "Отправить сообщение")
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
            word-break: break-word;
            overflow-wrap: anywhere;
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
            word-break: break-word;
            overflow-wrap: anywhere;
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
        code { background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; word-break: break-word; overflow-wrap: anywhere; }
        pre { background: rgba(0,0,0,0.05); padding: 8px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; word-break: break-word; overflow-wrap: anywhere; max-height: 300px; max-width: 100%; }
        a { color: inherit; text-decoration: underline; word-break: break-word; overflow-wrap: anywhere; }
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
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
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

    def _scroll_history_to_end(self):
        """Прокручивает окно истории чата к концу безопасно."""
        try:
            if hasattr(self, 'history') and self.history is not None:
                cursor = self.history.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.history.setTextCursor(cursor)
                self.history.ensureCursorVisible()
        except Exception as e:
            logger.debug(f"[CHAT] _scroll_history_to_end error: {e}")

    def _get_chat_history(self, limit: int = 50):
        """Возвращает последние сообщения текущей сессии в формате списка словарей.

        Каждый элемент: { 'role': 'user'|'assistant'|'system', 'content': str, 'timestamp': str }
        Используется при отправке сообщения для передачи контекста в backend.
        """
        try:
            if not getattr(self, 'session_id', None):
                return []
            if not hasattr(self, 'memory_manager') or self.memory_manager is None:
                return []
            msgs = self.memory_manager.get_session_messages(self.session_id, limit=limit)
            history = []
            for m in msgs:
                history.append({
                    'role': m.get('role', ''),
                    'content': m.get('content', ''),
                    'timestamp': m.get('timestamp', '')
                })
            return history
        except Exception as e:
            logger.warning(f"[CHAT] Не удалось получить историю чата: {e}")
            return []

    def _send_message_basic_wrapper(self):
        """Обертка для совместимости: вызывает основной send_message ниже."""
        try:
            return self.send_message()
        except Exception as e:
            logger.error(f"[CHAT] Ошибка в _send_message_basic_wrapper: {e}")
            raise

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
        
        # Инлайн-стили, чтобы перебить глобальные qApp стили/темы
        bubble_style = "max-width:75%; display:inline-block; position:relative; white-space:pre-wrap; word-wrap:break-word; word-break:break-word; overflow-wrap:anywhere;"
        pre_style = "background:rgba(0,0,0,0.05); padding:8px; border-radius:8px; overflow-x:auto; white-space:pre-wrap; word-wrap:break-word; word-break:break-word; overflow-wrap:anywhere; max-height:300px; max-width:100%;"
        code_style = "background:rgba(0,0,0,0.05); padding:2px 4px; border-radius:4px; word-break:break-word; overflow-wrap:anywhere;"
        # Подставляем стили в сгенерированный HTML (минимально инвазивно)
        formatted_text_styled = formatted_text.replace("<pre>", f'<pre style="{pre_style}">').replace("<code>", f'<code style="{code_style}">')
        
        message_html = f"""
        <div id="{msg_id}" class="message {style_class}" style="{bubble_style}">
            {avatar}
            <b>{author}:</b> {formatted_text_styled}
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
        # На всякий случай отключаем горизонтальный скролл и выставляем перенос по виджету каждый раз
        self.history.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        
        # Обрабатываем успешный ответ
        if isinstance(response, dict):
            if 'terminal_output' in response:
                self._handle_terminal_output(response['terminal_output'])
                full_message = response.get('response', 'Command executed in terminal. See terminal tab for output.')
            else:
                # Извлекаем текст ответа из словаря
                full_message = response.get('response', str(response))
            # Попытка применить команды браузера, если они есть в ответе
            try:
                self._apply_browser_actions_from_response(response)
            except Exception as e:
                logger.debug(f"[BROWSER] Ошибка при попытке применить действия из ответа: {e}")
        else:
            full_message = self._clean_response_message(str(response))
        
        # Очищаем сообщение от пустых строк
        full_message = "\n".join(line for line in full_message.splitlines() if line.strip())
        self._append_message_with_style("assistant", full_message)
        if self.session_id:
            self.memory_manager.add_message(self.session_id, "assistant", full_message)
        
        self.send_btn.setEnabled(True)

    @Slot(str)
    def _handle_partial_response(self, partial_text: str):
        """Обрабатывает частичные ответы для streaming отображения"""
        # Fallback для обычного QTextEdit
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(partial_text)
        self.history.setTextCursor(cursor)
        
        self._scroll_history_to_end()

    def _append_message_basic(self, role: str, message: str):
        """Метод для добавления сообщений с базовым стилем"""
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
        match = re.search(r"'response':\s*['\"](.+?)['\"]", message, re.DOTALL)
        if match:
            message = match.group(1).strip()
        
        # Удаляем системные префиксы/суффиксы
        message = re.sub(r"^\{{.*'response':", '', message, flags=re.DOTALL)
        message = re.sub(r"\}}.*$", '', message, flags=re.DOTALL)
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
                    # Расширенный список поддерживаемых форматов изображений
                    image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif']
                    att_type = 'image' if ext in image_exts else 'file'
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
        """Обработка нажатий клавиш в поле ввода"""
        # Enter/Return - отправка сообщения (без Shift)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.send_message()
            event.accept()
            return
        
        # Shift+Enter - новая строка (стандартное поведение QTextEdit)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            QTextEdit.keyPressEvent(self.input, event)
            return
        
        # Ctrl+V - вставка (включая изображения)
        if event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            if mime.hasImage():
                image = clipboard.image()
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    writer = QImageWriter(tmp.name, b'png')
                    if writer.write(image):
                        self.attached_files.append({'path': tmp.name, 'type': 'image'})
                        self._append_message_with_style('system', 'Image pasted from clipboard')
                event.accept()
                return
            elif mime.hasUrls():
                for url in mime.urls():
                    if url.isLocalFile():
                        path = url.toLocalFile()
                        name = os.path.basename(path)
                        ext = os.path.splitext(name)[1].lower()
                        # Расширенный список поддерживаемых форматов изображений
                        image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif']
                        att_type = 'image' if ext in image_exts else 'file'
                        self.attached_files.append({'path': path, 'type': att_type})
                        self._append_message_with_style('system', f'{att_type.capitalize()} pasted: {name}')
                event.accept()
                return
            # Если нет изображений/файлов, выполняем стандартную вставку текста
            QTextEdit.keyPressEvent(self.input, event)
            return
        
        # Стандартные комбинации клавиш (Ctrl+C/X/A/Z/Y)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() in (
            Qt.Key.Key_C, Qt.Key.Key_X, Qt.Key.Key_A, Qt.Key.Key_Z, Qt.Key.Key_Y
        ):
            QTextEdit.keyPressEvent(self.input, event)
            return
        
        # Все остальные клавиши - стандартная обработка
        QTextEdit.keyPressEvent(self.input, event)

    def _history_key_press_event(self, event):
        """Обработка нажатий клавиш в области истории чата"""
        # Ctrl+C - копирование выделенного текста
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            QTextEdit.keyPressEvent(self.history, event)
            return
        
        # Ctrl+A - выделить всё
        if event.key() == Qt.Key.Key_A and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            QTextEdit.keyPressEvent(self.history, event)
            return
        
        # Ctrl+F - поиск (если поддерживается)
        if event.key() == Qt.Key.Key_F and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            QTextEdit.keyPressEvent(self.history, event)
            return
        
        # Стрелки, Page Up/Down, Home/End - навигация
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right,
                          Qt.Key.Key_PageUp, Qt.Key.Key_PageDown, Qt.Key.Key_Home, Qt.Key.Key_End):
            QTextEdit.keyPressEvent(self.history, event)
            return
        
        # Все остальные клавиши - стандартная обработка для read-only поля
        QTextEdit.keyPressEvent(self.history, event)

    def keyPressEvent(self, event):
        """Глобальная обработка клавиш для всего виджета чата"""
        # Ctrl+Enter - отправка сообщения (альтернативный способ)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.send_message()
            event.accept()
            return
        
        # Escape - очистка поля ввода
        if event.key() == Qt.Key.Key_Escape:
            self.input.clear()
            event.accept()
            return
        
        # Передаем обработку родительскому классу
        super().keyPressEvent(event)
            
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
            filter="Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg *.tiff *.tif)"
        )
        if image_path:
            logger.info(f"Изображение прикреплено: {os.path.basename(image_path)}")
            self._append_message_with_style("system", f"Изображение прикреплено: {os.path.basename(image_path)}")
            self.attached_files.append({"path": image_path, "type": "image"})

    def show_context_stats(self):
        """Показывает статистику контекста"""
        QMessageBox.information(self, "Статистика", "Логика статистики будет добавлена позже.")

#    def apply_theme(self):
#        """Применяет текущую тему"""
#        if self.theme_manager:
#            theme_name = self.theme_combo.currentData()
#            if theme_name:
#                logger.info(f"Применение темы: {theme_name}")
#                success = self.theme_manager.apply_theme(theme_name)

#                # Показываем результат
#                msg_box = QMessageBox()
#                msg_box.setWindowTitle("Применение темы")
#                if success:
#                    msg_box.setText(f"Тема '{theme_name}' успешно применена.")
#                    msg_box.setIcon(QMessageBox.Information)
#                else:
#                    msg_box.setText(f"Не удалось применить тему '{theme_name}'.")
#                    msg_box.setIcon(QMessageBox.Warning)
#                msg_box.exec()
#            else:
#                logger.warning("Тема не выбрана в комбо-боксе.")
#        else:
#            logger.error("ThemeManager не инициализирован.")
        
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
        
        # Автоматически переключаемся на вкладку чата
        self.switch_to_chat_tab()
    
    def _on_model_changed(self, provider: str, model_id: str):
        """Обработчик изменения модели"""
        self.current_provider = provider
        self.current_model_id = model_id
        logger.info(f"[MODEL] Модель изменена: {provider}/{model_id}")
        print(f"Модель изменена: {provider}/{model_id}")
        
        # Автоматически переключаемся на вкладку чата
        self.switch_to_chat_tab()
    
    def _on__model_selected(self, model_data: dict):
        """Обработчик выбора модели """
        model_id = model_data.get('id', 'unknown')
        self.current_provider = ""
        self.current_model_id = model_id
        self.current_model_data = model_data
        
        logger.info(f"[MODEL] Выбрана модель : {model_id}")
        logger.debug(f"[MODEL] Данные модели: {model_data}")
        print(f"Выбрана модель : {model_id}")
        
        # Автоматически переключаемся на вкладку чата
        self.switch_to_chat_tab()
    
    def _on_provider_switch_requested(self, provider: str):
        """Обработчик запроса переключения провайдера"""
        print(f"Запрос переключения на провайдера: {provider}")
        
        # Переключаемся на соответствующую вкладку
        if provider == "gemini" and getattr(self, 'model_selector_widget', None) is not None:
            # Находим индекс вкладки с ModelSelectorWidget
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.model_selector_widget:
                    self.tab_widget.setCurrentIndex(i)
                    break
        elif provider == "" and hasattr(self, '_widget'):
            # Находим индекс вкладки с ModelWidget
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self._widget:
                    self.tab_widget.setCurrentIndex(i)
                    break
    
    def get__widget(self):
        """Возвращает виджет  для внешнего доступа"""
        return getattr(self, '_widget', None)
    
    def get_model_selector_widget(self):
        """Возвращает виджет выбора моделей для внешнего доступа"""
        return getattr(self, 'model_selector_widget', None)
    
    def switch_to__tab(self):
        """Переключается на вкладку """
        if hasattr(self, '_widget'):
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self._widget:
                    self.tab_widget.setCurrentIndex(i)
                    print("Переключились на вкладку ")
                    return True
        return False
    
    def switch_to_model_selector_tab(self):
        """Переключается на вкладку выбора моделей"""
        if getattr(self, 'model_selector_widget', None) is not None:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.model_selector_widget:
                    self.tab_widget.setCurrentIndex(i)
                    print("Переключились на вкладку выбора моделей")
                    return True
        return False
    
    def switch_to_chat_tab(self):
        """Переключается на вкладку чата"""
        self.tab_widget.setCurrentIndex(0)
    
    # === Обработчики сигналов для новых вкладок ===
    
    def _on_tools_attached(self, tools: list):
        """Обработчик прикрепления инструментов"""
        self.attached_tools = tools.copy()
        logger.info(f"[TOOLS] Прикреплены инструменты: {tools}")
    
    def _on_agents_attached(self, agents: list):
        """Обработчик прикрепления агентов"""
        self.attached_agents = agents.copy()
        logger.info(f"[AGENTS] Прикреплены агенты: {[a.get('name', a.get('id', '')) for a in agents]}")
    
    def _on_flow_attached(self, flow: dict):
        """Обработчик прикрепления флоу"""
        self.attached_flow = flow.copy() if flow else None
        if self.attached_flow:
            logger.info(f"[FLOW] Прикреплен флоу: {self.attached_flow.get('name', self.attached_flow.get('id', ''))}")
        else:
            logger.info("[FLOW] Флоу очищен")
    
    def send_message(self):
        """Отправляет сообщение с учетом прикрепленных инструментов и агентов (унифицировано)."""
        logger.debug("[CHAT] Вызван метод send_message (unified)")
        message_text = self.input.toPlainText().strip()
        if not message_text:
            return
        
        # Очищаем поле ввода и блокируем кнопку отправки
        self.input.clear()
        if hasattr(self, 'send_btn') and self.send_btn is not None:
            self.send_btn.setEnabled(False)
        
        # Отображаем сообщение пользователя
        self._append_message_with_style('user', message_text)

        # Перехват локальной команды открытия браузера
        try:
            lower = message_text.lower()
            if any(phrase in lower for phrase in ["открой браузер", "открыть браузер", "open browser", "open the browser"]):
                if self._ensure_browser_tab():
                    # Опционально: попытка открыть домашнюю страницу
                    try:
                        self.browser_widget.load_url("about:blank")
                    except Exception:
                        pass
                    self._append_message_with_style('system', 'Открыл встроенный браузер. Готов к навигации!')
                # Разблокировать кнопку и завершить без отправки на backend
                if hasattr(self, 'send_btn') and self.send_btn is not None:
                    self.send_btn.setEnabled(True)
                return
        except Exception as e:
            logger.debug(f"[CHAT] Ошибка при обработке команды открытия браузера: {e}")
        
        # Индикатор загрузки
        self._show_loading_indicator()
        
        # Сохраняем в память
        if getattr(self, 'session_id', None):
            try:
                self.memory_manager.add_message(self.session_id, 'user', message_text)
            except Exception as e:
                logger.warning(f"[CHAT] Не удалось сохранить сообщение пользователя в память: {e}")
        else:
            logger.warning("[CHAT] Session not initialized, message not saved")
        
        # Полное metadata
        metadata = {
            'session_id': self.session_id,
            'current_tool': self.current_tool,
            'chat_history': self._get_chat_history(),
            'attachments': self.attached_files.copy() if self.attached_files else [],
            'attached_files': self.attached_files.copy() if self.attached_files else [],
            'model_provider': self.current_provider,
            'model_id': self.current_model_id,
            'model_data': self.current_model_data,
        }
        # Дублируем для backend, ожидающего preferred_*
        if self.current_provider:
            metadata['preferred_provider'] = self.current_provider
        if self.current_model_id:
            metadata['preferred_model'] = self.current_model_id
        if self.current_model_data:
            metadata['model_info'] = self.current_model_data
        
        if self.attached_tools:
            metadata['force_tools'] = self.attached_tools.copy()
            logger.info(f"[SEND] Принудительные инструменты: {self.attached_tools}")
        if self.attached_agents:
            agent_ids = [a.get('id', a.get('name', '')) for a in self.attached_agents]
            metadata['force_agents'] = agent_ids
            logger.info(f"[SEND] Принудительные агенты: {agent_ids}")
        if self.attached_flow:
            flow_id = self.attached_flow.get('id', self.attached_flow.get('name', ''))
            metadata['force_flow'] = flow_id
            logger.info(f"[SEND] Принудительный флоу: {flow_id}")
        
        # Отправляем сообщение через асинхронный обработчик
        try:
            success = self.async_handler.send_message(message_text, metadata)
            if success:
                logger.info(f"[SEND] Сообщение отправлено успешно: {message_text[:50]}...")
                self.attached_files.clear()
            else:
                logger.error("[SEND] Ошибка отправки сообщения")
                self._append_message_with_style('error', 'Ошибка отправки сообщения')
                if hasattr(self, 'send_btn') and self.send_btn is not None:
                    self.send_btn.setEnabled(True)
        except Exception as e:
            logger.error(f"[SEND] Исключение при отправке: {e}")
            self._append_message_with_style('error', f'Ошибка: {str(e)}')
            if hasattr(self, 'send_btn') and self.send_btn is not None:
                self.send_btn.setEnabled(True)