"""
MainWindow class for GopiAI application.

This is the main window of the application, which uses mixins for different functionality.
"""

import logging
import os
import sys
import asyncio
import time
from concurrent.futures import TimeoutError

from PySide6 import __version__ as PYSIDE_VERSION_STR
from PySide6.QtCore import (
    QEvent, QPoint, QSettings, Qt, QThreadPool,
    QTimer, qVersion, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PySide6.QtGui import QAction, QCursor, QDesktopServices, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication, QDialog, QDockWidget, QFileDialog,
    QHBoxLayout, QInputDialog, QLabel, QMainWindow,
    QMenu, QMessageBox, QSizePolicy, QToolBar,
    QVBoxLayout, QWidget, QSplitter, QLineEdit,
    QPushButton, QProgressBar,
)

from app.ui.i18n.translator import JsonTranslationManager, tr
from app.ui.lucide_icon_manager import get_lucide_icon
from app.utils.theme_manager import ThemeManager

# Import logic modules
from ..logic.agent_setup import (
    connect_agent_signals,
    handle_agent_response,
    handle_user_message,
    setup_agent,
    update_agent_status_display,
)

# Import event handlers
from ..logic.event_handlers import (
    on_dock_visibility_changed,
    on_file_double_clicked,
    on_project_tree_double_clicked,
    on_tab_changed,
)
from ..plugins.plugin_manager import PluginManager
from ..utils.settings import restore_window_state
from ..utils.signal_checker import auto_connect_signals, check_main_window_signals
from ..utils.theme_utils import on_theme_changed_event
from ..utils.translation import on_language_changed_event, translate
from ..utils.ui_utils import (
    apply_dock_constraints,
    fix_duplicate_docks,
    load_fonts,
    update_custom_title_bars,
    validate_ui_components,
)
from .agent_ui_integration import (
    fix_missing_signals,
    save_integration_status_to_serena,
    update_integration_status,
)
from .central_widget import setup_central_widget
from .docks import create_docks
from .main_window_title_bar import MainWindowTitleBar
from .menus import setup_menus
from .status_bar import create_status_bar
from .toolbars import create_toolbars
from .browser_tab_widget import MultiBrowserWidget
from .browser_agent_interface import BrowserAgentInterface
from app.ui.unified_chat_view import UnifiedChatView, MODE_BROWSING, MODE_CODING

# Import mixins
from .main_window_components import (
    FileActionsMixin,
    EditActionsMixin,
    TabManagementMixin,
    ViewManagementMixin,
    AgentIntegrationMixin,
    WindowEventsMixin,
)

logger = logging.getLogger(__name__)


class MainWindow(
    QMainWindow,
    FileActionsMixin,
    EditActionsMixin,
    TabManagementMixin,
    ViewManagementMixin,
    AgentIntegrationMixin,
    WindowEventsMixin,
):
    """Главное окно приложения GopiAI."""

    def __init__(self, icon_manager, parent=None):
        """Инициализация главного окна приложения.

        Args:
            icon_manager: Менеджер иконок
            parent: Родительский виджет
        """
        super().__init__(parent)

        # Сохраняем менеджер иконок для использования в других методах
        self.icon_manager = icon_manager

        # Инициализируем менеджер тем
        self.theme_manager = ThemeManager.instance()

        # Атрибуты, которые будут инициализированы позже
        self.mode_indicator = None
        self.status_bar = None
        self.settings = QSettings("GopiAI", "GopiEditor")
        self.recent_files = []

        # Дополнительные атрибуты для работы с UI
        self.unified_chat_view = None      # Единый интерфейс чата
        self.browser_dock = None
        self.reasoning_agent_dialog = None
        self.settings_menu = None
        self.view_menu = None
        self.file_menu = None
        self.help_menu = None
        self.recent_menu = None
        self.themes_menu = None
        self.toolbar = None
        self.central_tabs = None
        self.editor_widget = None
        self.project_explorer_dock = None
        self.chat_dock = None
        self.terminal_dock = None
        self.toggle_project_explorer_action = None
        self.toggle_chat_action = None
        self.toggle_terminal_action = None
        self.toggle_browser_action = None
        self.toggle_coding_agent_action = None

        # Устанавливаем заголовок окна
        self.setWindowTitle(tr("app.title", "GopiAI"))
        self.resize(1200, 800)
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.translation_manager = JsonTranslationManager.instance()

        # Создаем главный виджет и макет
        central_widget = QWidget()
        central_widget.setObjectName("mainCentralWidget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем контейнер для содержимого
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Сразу применяем тему, чтобы избежать "мигания" с белой темой
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_visual_theme()
            logger.info(
                f"Принудительно применяем тему при инициализации: {current_theme}"
            )
            self.theme_manager.switch_visual_theme(current_theme, force_apply=True)
            QApplication.processEvents()  # Обрабатываем события, чтобы тема применилась немедленно

        self.thread_pool = QThreadPool()
        self.setObjectName("MainWindow")
        self.sessions = {}
        self.agent = setup_agent(self)

        # Инициализируем менеджер плагинов
        self.plugin_manager = PluginManager.instance()
        self.plugin_manager.set_main_window(self)

        # Подключаемся к сигналу languageChanged
        self.translation_manager.languageChanged.connect(self._on_language_changed_event)
        logger.info(
            "Подключен сигнал JsonTranslationManager.languageChanged к MainWindow._on_language_changed_event"
        )

        # Подключаемся к сигналу visualThemeChanged
        self.theme_manager.visualThemeChanged.connect(
            lambda theme_name: on_theme_changed_event(self, theme_name)
        )
        logger.info(
            "Подключен сигнал ThemeManager.visualThemeChanged к on_theme_changed_event"
        )

        self._setup_ui()
        self.installEventFilter(self)

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        try:
            logger.info("Starting _setup_ui in MainWindow")
            load_fonts(self)

            # Создаем макет основного содержимого
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)

            # Создаем центральный виджет
            central_container = QWidget()
            central_container.setObjectName("centralContainer")
            central_container.setLayout(self.main_layout)
            self.setCentralWidget(central_container)

            # Устанавливаем центральный виджет с редактором и табами
            setup_central_widget(self)

            # Создаем строку статуса
            self.status_bar = create_status_bar(self)
            self.setStatusBar(self.status_bar)

            # Создаем доки (проводник проекта, чат, терминал)
            create_docks(self)

            # Создаем меню
            setup_menus(self)

            # Создаем панели инструментов
            create_toolbars(self)

            # Подключаем сигналы для вкладок
            if hasattr(self, "central_tabs") and self.central_tabs:
                self.central_tabs.currentChanged.connect(
                    lambda index: on_tab_changed(self, index)
                )
                # Добавляем контекстное меню для вкладок
                self.central_tabs.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
                self.central_tabs.tabBar().customContextMenuRequested.connect(
                    self._show_tab_context_menu
                )

            # Подключаем сигналы для проводника проекта
            if (
                hasattr(self, "project_explorer")
                and hasattr(self.project_explorer, "tree_view")
                and self.project_explorer.tree_view
            ):
                # Подключаем двойной клик в проводнике проекта
                self.project_explorer.tree_view.doubleClicked.connect(
                    lambda index: on_project_tree_double_clicked(self, index)
                )

                # Подключаем контекстное меню для дерева проекта
                self.project_explorer.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
                self.project_explorer.tree_view.customContextMenuRequested.connect(
                    self._show_project_tree_context_menu
                )

            # Auto-connect signals
            self._auto_connect_signals()

            # Применяем начальный макет
            self._apply_initial_layout()

            # Проверяем интеграцию агентов и сохраняем в Serena
            update_integration_status(self)
            save_integration_status_to_serena(self)

            # Исправляем отсутствующие сигналы
            fix_missing_signals(self)

            # Проверка сигналов для отладки
            QTimer.singleShot(2000, self._check_signals)

            # Валидация компонентов UI
            validate_ui_components(self)

            logger.info("UI setup completed")

        except Exception as e:
            logger.error(f"Error in _setup_ui: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    def _connect_global_ui_signals(self):
        """Подключает глобальные сигналы UI."""
        # Подключаем сигналы изменения видимости доков
        if hasattr(self, "project_explorer_dock") and self.project_explorer_dock:
            self.project_explorer_dock.visibilityChanged.connect(
                lambda visible: on_dock_visibility_changed(
                    self, "project_explorer", visible
                )
            )

        if hasattr(self, "chat_dock") and self.chat_dock:
            self.chat_dock.visibilityChanged.connect(
                lambda visible: on_dock_visibility_changed(self, "chat", visible)
            )

        if hasattr(self, "terminal_dock") and self.terminal_dock:
            self.terminal_dock.visibilityChanged.connect(
                lambda visible: on_dock_visibility_changed(self, "terminal", visible)
            )

        if hasattr(self, "browser_dock") and self.browser_dock:
            self.browser_dock.visibilityChanged.connect(
                lambda visible: on_dock_visibility_changed(self, "browser", visible)
            )

    def _apply_initial_layout(self):
        """Применяет начальный макет окна."""
        restore_window_state(self)

        # Ensure theme is applied on startup - IMPORTANT ADDITION
        logger.info("Applying theme on startup")
        if self.theme_manager:
            # Force the theme to be applied on startup
            current_theme = self.theme_manager.get_current_visual_theme()
            logger.info(f"Applying theme on startup: {current_theme}")

            # Apply the theme
            self.theme_manager.switch_visual_theme(current_theme, force_apply=True)

            # Force the application to process the theme change
            QApplication.processEvents()
        else:
            logger.error(
                "ThemeManager instance is not available in _apply_initial_layout."
            )

        update_custom_title_bars(self, self.icon_manager)

        # Открываем окно Unified Chat View только если пользователь не отключил его специально
        settings = QSettings(tr("app.title", "GopiAI"), "UI")
        show_unified_chat = settings.value("unified_chat_visible", True, bool)

        if show_unified_chat:
            logger.info("Открываем Unified Chat View по умолчанию при запуске")
            # Запускаем открытие окна с небольшой задержкой
            QTimer.singleShot(500, self.show_coding_agent_dialog)

        self._update_view_menu()
        QApplication.processEvents()

    def _on_language_changed_event(self, language_code):
        """Обрабатывает изменение языка.

        Args:
            language_code (str): Код языка
        """
        logger.info(f"Language changed to {language_code}")
        try:
            # Вызываем функцию обработки изменения языка
            on_language_changed_event(self, language_code)

            # Обновляем заголовок
            self.setWindowTitle(tr("app.title", "GopiAI"))

            # Обновляем меню
            if hasattr(self, "menuBar") and self.menuBar():
                self.menuBar().clear()
                setup_menus(self)
                logger.info("Menus recreated after language change")
        except Exception as e:
            logger.error(f"Error processing language change: {e}")

    def _auto_connect_signals(self):
        """Автоматически подключает сигналы."""
        try:
            # Автоматически подключаем сигналы для автоматической проверки сигналов
            auto_connect_signals(self)
            logger.info("Signal auto-connection completed")
        except Exception as e:
            logger.error(f"Error in _auto_connect_signals: {e}")

    def _check_signals(self):
        """Проверяет корректность подключения сигналов."""
        try:
            # Проверяем сигналы главного окна
            check_main_window_signals(self)
            logger.info("Signal checking completed")
        except Exception as e:
            logger.error(f"Error in _check_signals: {e}")
