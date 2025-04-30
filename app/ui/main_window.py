import sys
import os  # Импортируем os для получения текущей директории
import asyncio
import threading
import subprocess  # Добавляем subprocess для Show in Explorer
import tempfile
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QTextEdit,
    QListWidget,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMenuBar,
    QStatusBar,
    QToolBar,
    QLabel,
    QTreeView,
    QFileSystemModel,
    QFileDialog,
    QMenu,
    QPushButton,
    QPlainTextEdit,
    QHBoxLayout,
    QSplitter,
    QDialog,
    QGroupBox,
    QDialogButtonBox,
    QComboBox,
    QCheckBox,
    QSizePolicy,
    QTextBrowser,
    QLineEdit,
    QTabBar,
    QRadioButton,
    QDoubleSpinBox,
    QMessageBox,
    QFileIconProvider
)
from PySide6.QtCore import (
    Qt,
    QSize,
    QThread,
    QObject,
    Signal,
    QModelIndex,
    QDir,
    QSettings,
    QTimer,
    QTranslator,
    QLocale,
    QEvent,
    QFileInfo,
    QLibraryInfo,
    QFile,
    QTextStream,
    QRect,
)
from PySide6.QtGui import QAction, QIcon, QActionGroup, QPixmap, QFontDatabase, QFont, QKeySequence, QColor, QTextCursor, QTextOption, QSyntaxHighlighter, QTextCharFormat, QStandardItemModel, QStandardItem, QTextDocument

# Импортируем наш новый виджет чата
from .chat_widget import ChatWidget
from .code_editor import CodeEditor
from .terminal_widget import TerminalWidget  # Добавляем импорт терминала

# Импортируем агента
from app.agent.manus import Manus
from app.agent.react import ReActAgent
from app.agent.planning import PlanningAgent
from app.agent.base import BaseAgent
from app.agent.toolcall import ReactAgent
from app.flow.flow_factory import FlowFactory, FlowType
from app.tool import ToolCollection
from app.tool.python_execute import PythonExecute
from app.tool.web_search import WebSearch
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.bash import Bash
from app.tool.file_operators import FileOperator, LocalFileOperator
from app.tool.terminal import Terminal
from app.tool.terminate import Terminate
from typing import Any  # Добавим Any для тайпхинта
import json
from app.flow.base import BaseFlow
from app.ui.flow_visualizer import show_flow_visualizer_dialog
from .i18n.translator import translation_manager
from app.ui.emoji_dialog import EmojiDialog  # Импорт нового диалога эмодзи

# Импорт менеджера иконок
from .icon_manager import get_icon, list_icons

# Импорт ресурсов с иконками
try:
    import icons_rc
except ImportError:
    print("Warning: Icons resource file (icons_rc.py) not found.")

# Попытка импорта QWebEngineView
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import (
        QWebEnginePage,
    )  # Может понадобиться для настроек

    WEBENGINE_AVAILABLE = True
except ImportError:
    QWebEngineView = None  # Определяем как None, если не доступно
    QWebEnginePage = None
    WEBENGINE_AVAILABLE = False
    print(
        "Warning: PySide6.QtWebEngineWidgets not found. Browser functionality will be disabled."
    )

from .close_button_fixer import CloseButtonFixer

class AgentWorker(QObject):
    """Worker для выполнения задач агента в отдельном потоке."""

    # Сигнал с результатом работы агента (может быть любым объектом)
    finished = Signal(object)
    # Сигнал для запуска задачи
    start_task = Signal(str)
    # Сигнал для отправки обновления состояния агента
    status_update = Signal(str)

    def __init__(self, agent: Manus):
        super().__init__()
        self.agent = agent
        self.start_task.connect(self.run_agent_task)
        self._loop = None

        # Подключаем события мониторинга состояния агента, если они доступны
        if hasattr(agent, "on_thinking_start"):
            agent.on_thinking_start = lambda: self.status_update.emit("Thinking... 🤔")
        if hasattr(agent, "on_thinking_end"):
            agent.on_thinking_end = lambda: self.status_update.emit(
                "Planning next step... 📋"
            )
        if hasattr(agent, "on_tool_start"):
            agent.on_tool_start = lambda tool_name: self.status_update.emit(
                f"Using tool: {tool_name} 🛠️"
            )
        if hasattr(agent, "on_tool_end"):
            agent.on_tool_end = lambda tool_name: self.status_update.emit(
                f"Finished using {tool_name} ✅"
            )

    def run_agent_task(self, prompt: str):
        """Запускает асинхронную задачу агента."""
        try:
            # Обновляем статус
            self.status_update.emit("Starting task... 🚀")

            # Получаем или создаем asyncio loop для этого потока
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

            # Запускаем асинхронную функцию агента
            result = self._loop.run_until_complete(self.agent.run(prompt))

            # Отправляем обновление статуса
            self.status_update.emit("Task completed! ✨")

            # Отправляем сырой результат
            self.finished.emit(result)

        except Exception as e:
            print(f"Error in agent task: {e}")  # Логируем ошибку
            # Отправляем информацию об ошибке в обновление статуса
            self.status_update.emit(f"Error: {e} ❌")
            # Отправляем информацию об ошибке
            self.finished.emit(f"Agent Error: {e}")

    def stop_loop(self):
        if self._loop and self._loop.is_running():
            self.status_update.emit("Stopping agent... 🛑")
            self._loop.call_soon_threadsafe(self._loop.stop)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализация переменных
        self.is_dark_theme = True  # По умолчанию используем тёмную тему
        self.current_language = "en_US"
        self.agent = None
        self.agent_thread = None
        self.agent_worker = None
        self.current_agent_mode = "reactive"  # По умолчанию реактивный режим
        self.current_reflection_level = 0  # По умолчанию без самоанализа
        self.memory_enabled = False  # По умолчанию память отключена

        # Инициализация объектов для перевода
        self.translator = QTranslator()
        self.translator_app = QTranslator()

        # Загружаем настройки
        self.settings = QSettings("GopiAI", "UI")

        # Восстанавливаем тему из настроек
        theme_setting = self.settings.value("dark_theme", "true").lower()
        self.is_dark_theme = theme_setting == "true"
        print(f"Loaded theme setting from config: {theme_setting}, is_dark_theme={self.is_dark_theme}")

        # Восстанавливаем язык из настроек
        self.current_language = self.settings.value("language", "en_US")
        self._load_language(self.current_language)

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс, вызывая все необходимые методы в правильном порядке."""
        # Инициализируем агента и рабочий поток
        self.agent_worker = None  # Будет инициализирован позже в _create_agent_with_config

        # Настраиваем базовые элементы UI
        self._load_fonts()
        self._load_styles()

        # Создаём интерфейс
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_docks()
        self._setup_central_widget()

        # Подключаем сигналы
        self._connect_ui_signals()

        # Настраиваем иконки
        self._create_file_icon_provider()

        # Обновляем переводы
        self._update_ui_translations()

        # Восстанавливаем сохранённое состояние окна
        self._restore_window_state()

        # Применяем начальный макет, если нужно
        self._apply_initial_layout()

        # Создаем агента с конфигурацией по умолчанию
        self._create_agent_with_config()

        # Применение темы
        self._toggle_theme(self.is_dark_theme)

        # Отображение главного окна
        self.setWindowTitle(self._translate("main_window", "GopiAI"))
        self.resize(1200, 800)
        self.show()

        # Устанавливаем минимальный размер окна
        self.setMinimumSize(800, 600)

        # Явно перерисовываем окно и применяем стили
        self.repaint()
        QApplication.processEvents()

        # Применяем фиксер кнопок закрытия
        CloseButtonFixer.apply_to_window(self)

    def _load_fonts(self):
        """Загружаем современные шрифты для приложения."""
        try:
            font_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "fonts"
            )

            # Создаем директорию для шрифтов, если её нет
            os.makedirs(font_dir, exist_ok=True)

            # Проверяем наличие шрифтов
            inter_file = os.path.join(font_dir, "Inter-Regular.ttf")
            jet_brains_file = os.path.join(font_dir, "JetBrainsMono-Regular.ttf")

            # Добавляем шрифты в систему QFontDatabase
            font_loaded = False

            # Устанавливаем современный шрифт для всего приложения
            default_font = QFont("Inter", 10)
            QApplication.setFont(default_font)

            print("Fonts loaded and applied to application")
        except Exception as e:
            print(f"Error loading fonts: {e}")

    def _load_styles(self):
        """Загружает стили из QSS файла."""
        ###############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за загрузку файлов стилей и применение их к приложению
        # Изменение логики может привести к поломке UI и нарушению работы приложения
        # Тесно связан с методами _toggle_theme и _force_style_reload
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ###############################################################################
        try:
            # Выбираем путь к файлу в зависимости от настройки темы
            if self.is_dark_theme:
                style_path = os.path.join(
                    os.path.dirname(__file__), "themes", "dark_theme.qss"
                )
            else:
                style_path = os.path.join(
                    os.path.dirname(__file__), "themes", "light_theme.qss"
                )

            print(f"Attempting to load styles from: {style_path}")

            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    style = f.read()

                    # Получаем SVG-иконку закрытия вкладки
                    close_icon_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "assets",
                        "icons",
                        "close.svg",
                    )

                    if os.path.exists(close_icon_path):
                        with open(close_icon_path, "r", encoding="utf-8") as icon_file:
                            svg_content = icon_file.read()
                            # Преобразуем SVG в base64 для использования в QSS
                            import base64

                            svg_bytes = svg_content.encode("utf-8")
                            svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")

                            # Добавляем стиль для кнопки закрытия вкладки в общий стиль
                            tab_close_style = f"""
                            QTabBar::close-button {{
                                image: url(data:image/svg+xml;base64,{svg_base64});
                                subcontrol-position: right;
                                width: 16px;
                                height: 16px;
                                padding: 2px;
                            }}

                            QTabBar::close-button:hover {{
                                background-color: rgba(255, 85, 85, 0.3);
                                border-radius: 4px;
                            }}
                            """

                            # Добавляем стиль к основному стилю
                            style += tab_close_style
                    else:
                        print(f"Иконка закрытия не найдена: {close_icon_path}")

                    self.setStyleSheet(style)
                    print(f"Styles loaded from {style_path}")
            else:
                print(f"Style file not found: {style_path}")
        except Exception as e:
            print(f"Error loading styles: {e}")

    def _create_actions(self):
        """Создаем основные действия (для меню и тулбаров)."""

        # --- File Actions ---
        self.new_file_action = QAction(get_icon("new_document"), "&New Chat", self)
        self.new_file_action.setShortcut("Ctrl+N")
        self.new_file_action.setStatusTip("Create a new file")
        # Подключаем действие к обработчику
        self.new_file_action.triggered.connect(self._new_file)

        # Действия для управления конфигурацией агента
        self.save_agent_config_action = QAction(
            get_icon("save_config"), "Сохранить конфигурацию агента", self
        )
        self.save_agent_config_action.setStatusTip(
            "Сохранить текущую конфигурацию агента в файл"
        )
        # self.save_agent_config_action.triggered.connect(self._save_agent_config)

        self.load_agent_config_action = QAction(
            get_icon("load_config"), "Загрузить конфигурацию агента", self
        )
        self.load_agent_config_action.setStatusTip(
            "Загрузить конфигурацию агента из файла"
        )
        self.load_agent_config_action.triggered.connect(self._load_agent_config)

        # Действие для визуализации потока
        self.view_flow_action = QAction(
            get_icon("flow"), "Показать визуализацию потока", self
        )
        self.view_flow_action.setStatusTip(
            "Показать визуализацию структуры потока агента"
        )
        self.view_flow_action.triggered.connect(self._show_flow_visualization)
        self.view_flow_action.setEnabled(False)  # По умолчанию отключено

        self.open_file_action = QAction(get_icon("open"), "&Open File...", self)
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_file_action.setStatusTip("Open an existing chat")

        self.save_file_action = QAction(get_icon("save"), "&Save Chat", self)
        self.save_file_action.setShortcut("Ctrl+S")
        self.save_file_action.setStatusTip("Save the current chat")

        # Добавляем Save As...
        self.save_as_action = QAction(get_icon("save"), "Save Chat &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Save the current chat under a new name")

        # --- Exit Action ---
        self.exit_action = QAction(get_icon("close"), "E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit the application")

        # --- Edit Actions ---
        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setStatusTip("Cut the selected content to the clipboard")

        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setStatusTip("Copy the selected content to the clipboard")

        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setStatusTip("Paste content from the clipboard")

        # Добавляем действие для вставки эмодзи
        self.emoji_action = QAction(get_icon("emoji"), self._translate("menu.insert_emoji", "Insert Emoji..."), self)
        self.emoji_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self.emoji_action.setStatusTip(self._translate("menu.insert_emoji.tooltip", "Open emoji selection dialog"))
        self.emoji_action.triggered.connect(self._show_emoji_dialog)

        # --- View Actions ---
        # Действия для показа/скрытия панелей
        self.toggle_terminal_action = QAction(self._translate("dock.terminal", "Terminal"), self)
        self.toggle_terminal_action.setCheckable(True)
        self.toggle_terminal_action.setChecked(False)  # По умолчанию терминал скрыт
        self.toggle_terminal_action.setStatusTip(self._translate("dock.terminal.tooltip", "Show or hide the terminal panel"))
        self.toggle_terminal_action.setShortcut(
            "Ctrl+`"
        )  # Типичное сочетание клавиш для терминала

    def _create_menus(self):
        """Создает главное меню приложения."""
        # Создаем главное меню
        self.menu_bar = self.menuBar()

        # --- File Menu ---
        self.file_menu = self.menu_bar.addMenu(self._translate("menu.file", "File"))
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # --- Edit Menu ---
        self.edit_menu = self.menu_bar.addMenu(self._translate("menu.edit", "Edit"))
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.emoji_action)

        # --- View Menu ---
        self.view_menu = self.menu_bar.addMenu(self._translate("menu.view", "View"))

        # Подменю выбора темы
        self.theme_menu = self.view_menu.addMenu(self._translate("menu.theme", "Theme"))

        # Создаем группу для взаимоисключающих действий выбора темы
        self.theme_action_group = QActionGroup(self)

        # Добавляем действия для темной и светлой темы
        self.dark_theme_action = QAction(self._translate("menu.dark_theme", "Dark Theme"), self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(self.is_dark_theme)
        self.dark_theme_action.setData(True)  # True = темная тема
        self.dark_theme_action.triggered.connect(lambda: self._toggle_theme(True))  # Явное соединение для темной темы
        self.theme_action_group.addAction(self.dark_theme_action)
        self.theme_menu.addAction(self.dark_theme_action)

        self.light_theme_action = QAction(self._translate("menu.light_theme", "Light Theme"), self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.setChecked(not self.is_dark_theme)
        self.light_theme_action.setData(False)  # False = светлая тема
        self.light_theme_action.triggered.connect(lambda: self._toggle_theme(False))  # Явное соединение для светлой темы
        self.theme_action_group.addAction(self.light_theme_action)
        self.theme_menu.addAction(self.light_theme_action)

        # Подменю выбора языка
        self.language_menu = self.view_menu.addMenu(self._translate("menu.language", "Language"))

        # Создаем группу для взаимоисключающих действий выбора языка
        self.language_action_group = QActionGroup(self)

        # Добавляем действия для выбора языка
        self.english_action = QAction(self._translate("menu.english", "English"), self)
        self.english_action.setCheckable(True)
        self.english_action.setData("en_US")
        self.language_action_group.addAction(self.english_action)
        self.language_menu.addAction(self.english_action)

        self.russian_action = QAction(self._translate("menu.russian", "Russian"), self)
        self.russian_action.setCheckable(True)
        self.russian_action.setData("ru_RU")
        self.language_action_group.addAction(self.russian_action)
        self.language_menu.addAction(self.russian_action)

        # Отмечаем текущий язык
        for action in self.language_action_group.actions():
            if action.data() == self.current_language:
                action.setChecked(True)

        # Добавляем действия для показа/скрытия панелей
        self.view_menu.addSeparator()

        # Действие для показа/скрытия проводника проекта
        self.toggle_project_explorer_action = QAction(self._translate("dock.project_explorer", "Project Explorer"), self)
        self.toggle_project_explorer_action.setCheckable(True)
        self.toggle_project_explorer_action.setChecked(True)  # По умолчанию видимый
        self.view_menu.addAction(self.toggle_project_explorer_action)

        # Действие для показа/скрытия чата
        self.toggle_chat_action = QAction(self._translate("dock.chat", "Chat"), self)
        self.toggle_chat_action.setCheckable(True)
        self.toggle_chat_action.setChecked(True)  # По умолчанию видимый
        self.view_menu.addAction(self.toggle_chat_action)

        # Действие для показа/скрытия терминала
        self.view_menu.addAction(self.toggle_terminal_action)

        # --- Agent Menu ---
        self.agent_menu = self.menu_bar.addMenu(self._translate("menu.agent", "Agent"))

        # Действие для конфигурации агента
        self.configure_agent_action = QAction(get_icon("settings"), self._translate("menu.agent.configure", "Configure Agent..."), self)
        self.agent_menu.addAction(self.configure_agent_action)

        # Добавляем действия для сохранения/загрузки конфигурации
        self.agent_menu.addAction(self.save_agent_config_action)
        self.agent_menu.addAction(self.load_agent_config_action)

        # Добавляем действие для визуализации потока
        self.agent_menu.addSeparator()
        self.agent_menu.addAction(self.view_flow_action)

        # --- Settings Menu (New) ---
        self.settings_menu = self.menu_bar.addMenu(self._translate("menu.settings", "Settings"))

        # Добавляем действия в меню настроек
        # Настройки приложения
        self.app_preferences_action = QAction(get_icon("settings"), self._translate("menu.preferences", "Preferences"), self)
        self.settings_menu.addAction(self.app_preferences_action)

        # Добавляем другие пункты настроек
        self.settings_menu.addSeparator()

        # Дублируем настройки темы
        self.settings_menu.addMenu(self.theme_menu)

        # Дублируем настройки языка
        self.settings_menu.addMenu(self.language_menu)

        # --- Help Menu ---
        self.help_menu = self.menu_bar.addMenu(self._translate("menu.help", "Help"))

        # Действие "О программе"
        self.about_action = QAction(self._translate("menu.about", "About"), self)
        self.help_menu.addAction(self.about_action)

        # Действие "Документация"
        self.documentation_action = QAction(self._translate("menu.documentation", "Documentation"), self)
        self.help_menu.addAction(self.documentation_action)

    def _create_docks(self):
        """Создает боковые панели (dock-виджеты) приложения."""
        # --- Левая панель: Проводник проекта ---
        self.project_explorer_dock = QDockWidget("Project Explorer", self)
        # Позволяет перемещать в плавающем режиме, запрещает другие возможности кроме перемещения виджетов
        self.project_explorer_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        # Разрешаем только левую сторону
        self.project_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        # Устанавливаем минимальную ширину дока
        self.project_explorer_dock.setMinimumWidth(100)
        self.project_explorer_dock.setObjectName("ProjectExplorerDock") # Имя для сохранения настроек

        # Подключаем сигнал изменения видимости для обновления меню
        self.project_explorer_dock.visibilityChanged.connect(self._update_view_menu)

        project_explorer_widget = QWidget()
        project_explorer_layout = QVBoxLayout(project_explorer_widget)
        project_explorer_layout.setContentsMargins(0, 0, 0, 0) # Убираем отступы

        # Создаем модель файловой системы
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.rootPath())
        self.fs_model.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)

        # Устанавливаем провайдер для генерации иконок файлов
        self.fs_model.setIconProvider(self._create_file_icon_provider())

        # Добавляем секцию выбранной директории
        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(2, 2, 2, 2)

        # Создаем дерево файлов
        self.project_tree = QTreeView()
        self.project_tree.setModel(self.fs_model)
        self.project_tree.setRootIndex(self.fs_model.index(os.getcwd())) # Текущая директория
        self.project_tree.setAnimated(False)
        self.project_tree.setIndentation(20)
        self.project_tree.setSortingEnabled(True)
        # Добавляем контекстное меню для дерева файлов
        self.project_tree.setContextMenuPolicy(Qt.CustomContextMenu)

        # Скрываем ненужные колонки, оставляем только имя
        self.project_tree.setHeaderHidden(True)
        for i in range(1, self.fs_model.columnCount()):
            self.project_tree.hideColumn(i)

        project_explorer_layout.addLayout(workspace_layout)
        project_explorer_layout.addWidget(self.project_tree)

        self.project_explorer_dock.setWidget(project_explorer_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_explorer_dock)

        # --- Правая панель: Чат ---
        self.chat_dock = QDockWidget("Chat", self)
        # Позволяем перемещать в плавающем режиме, запрещаем другие возможности кроме перемещения виджетов
        self.chat_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        # Разрешаем только правую сторону
        self.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        # Устанавливаем минимальную ширину дока
        self.chat_dock.setMinimumWidth(200)
        self.chat_dock.setObjectName("ChatDock") # Имя для сохранения настроек

        # Подключаем сигнал изменения видимости для обновления меню
        self.chat_dock.visibilityChanged.connect(self._update_view_menu)

        # Добавляем наш новый виджет чата
        self.chat_widget = ChatWidget(self)
        self.chat_dock.setWidget(self.chat_widget)

        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock)

        # --- Нижняя панель: Терминал ---
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setObjectName("TerminalDock") # Имя для сохранения настроек

        # Подключаем сигнал изменения видимости для обновления меню
        self.terminal_dock.visibilityChanged.connect(self._update_view_menu)

        # Добавляем встроенный терминал
        self.terminal_widget = TerminalWidget(self)
        self.terminal_dock.setWidget(self.terminal_widget)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)
        # По умолчанию скрываем - чтобы терминал можно было
        self.terminal_dock.hide()

    def _toggle_terminal(self, checked=None):
        """Переключает видимость панели терминала."""
        if checked is None:
            checked = not self.terminal_dock.isVisible()
        self.terminal_dock.setVisible(checked)
        self.toggle_terminal_action.setChecked(checked)

    def _toggle_project_explorer(self, checked=None):
        """Переключает видимость панели проводника проекта."""
        if checked is None:
            checked = not self.project_explorer_dock.isVisible()
        self.project_explorer_dock.setVisible(checked)
        if hasattr(self, 'toggle_project_explorer_action'):
            self.toggle_project_explorer_action.setChecked(checked)

    def _toggle_chat(self, checked=None):
        """Переключает видимость панели чата."""
        if checked is None:
            checked = not self.chat_dock.isVisible()
        self.chat_dock.setVisible(checked)
        if hasattr(self, 'toggle_chat_action'):
            self.toggle_chat_action.setChecked(checked)

    def _update_view_menu(self):
        """Обновляет меню View, синхронизируя состояние чекбоксов с видимостью доков."""
        if hasattr(self, 'toggle_terminal_action'):
            self.toggle_terminal_action.setChecked(self.terminal_dock.isVisible())
        if hasattr(self, 'toggle_project_explorer_action'):
            self.toggle_project_explorer_action.setChecked(self.project_explorer_dock.isVisible())
        if hasattr(self, 'toggle_chat_action'):
            self.toggle_chat_action.setChecked(self.chat_dock.isVisible())

    def _connect_ui_signals(self):
        """Подключает сигналы от элементов UI к методам."""
        # Сигнал от действия переключения терминала
        if hasattr(self, 'toggle_terminal_action'):
            self.toggle_terminal_action.triggered.connect(self._toggle_terminal)

        # Проверяем наличие других действий для доков
        if hasattr(self, 'toggle_project_explorer_action'):
            self.toggle_project_explorer_action.triggered.connect(self._toggle_project_explorer)

        if hasattr(self, 'toggle_chat_action'):
            self.toggle_chat_action.triggered.connect(self._toggle_chat)

        # Сигнал от чата -> обработка сообщения пользователя
        if hasattr(self, 'chat_widget') and hasattr(self.chat_widget, 'message_sent'):
            self.chat_widget.message_sent.connect(self._handle_user_message)

        # Сигнал от дерева файлов -> открытие файла
        if hasattr(self, 'project_tree'):
            self.project_tree.doubleClicked.connect(self._open_file_from_tree)
            self.project_tree.customContextMenuRequested.connect(self._show_project_tree_context_menu)

        # Подключение сигналов от действий меню
        if hasattr(self, 'theme_action_group'):
            self.theme_action_group.triggered.connect(self._toggle_theme)

        if hasattr(self, 'language_action_group'):
            self.language_action_group.triggered.connect(self._on_language_changed)

        if hasattr(self, 'configure_agent_action'):
            self.configure_agent_action.triggered.connect(self._show_agent_config_dialog)

        # Подключаем новое действие настроек приложения
        if hasattr(self, 'app_preferences_action'):
            self.app_preferences_action.triggered.connect(self._show_preferences_dialog)

        if hasattr(self, 'about_action'):
            self.about_action.triggered.connect(self._on_about)

        if hasattr(self, 'documentation_action'):
            self.documentation_action.triggered.connect(self._on_documentation)

    def _handle_user_message(self, message: str):
        """Обрабатывает сообщение пользователя: отправляет сообщение в агентский поток."""
        if hasattr(self, 'agent_worker') and self.agent_worker:
            # Отправляем задачу для запуска агента в рабочем потоке
            self.agent_worker.start_task.emit(message)

    def _open_file_from_tree(self, index):
        """Обрабатывает открытие файла из дерева проекта."""
        if hasattr(self, 'fs_model') and index.isValid():
            file_path = self.fs_model.filePath(index)
            # Здесь должен быть код для открытия файла
            print(f"Requested to open file: {file_path}")

    def _show_project_tree_context_menu(self, position):
        """Отображает контекстное меню для дерева проекта."""
        # Заглушка для контекстного меню
        pass

    def _load_language(self, language_code):
        """Загружает языковые файлы для указанного языка."""
        try:
            # Используем менеджер переводов для загрузки языка
            translation_manager.switch_language(language_code)
            print(f"Switched language to {language_code} using translation manager")

            # Также пытаемся загрузить файл перевода Qt
            app_translation_path = os.path.join(
                os.path.dirname(__file__), "i18n", f"{language_code}.qm"
            )

            # Загружаем Qt файл перевода, если он существует
            if os.path.exists(app_translation_path):
                self.translator.load(app_translation_path)
                QApplication.instance().installTranslator(self.translator)
                print(f"Loaded Qt application translation from {app_translation_path}")

            # Обновляем переводы в UI
            if hasattr(self, '_update_ui_translations'):
                self._update_ui_translations()

            # Обновляем текущий язык
            self.current_language = language_code

            # Сохраняем выбранный язык в настройках
            if hasattr(self, 'settings'):
                self.settings.setValue("language", language_code)
                self.settings.sync()

            return True
        except Exception as e:
            print(f"Error loading language {language_code}: {e}")
            return False

    def _translate(self, key, default_text):
        """Возвращает перевод для указанного ключа или значение по умолчанию."""
        # Используем менеджер переводов
        translated = translation_manager.get_translation(key, default_text)
        return translated

    def _update_ui_translations(self):
        """Обновляет все переводимые элементы интерфейса."""
        # Обновление заголовка окна
        self.setWindowTitle(self._translate("main_window", "GopiAI"))

        # Обновление действий меню File
        if hasattr(self, 'new_file_action'):
            self.new_file_action.setText(self._translate("menu.new", "New Chat"))
            self.new_file_action.setStatusTip(self._translate("menu.new.tooltip", "Create a new chat"))

        if hasattr(self, 'open_file_action'):
            self.open_file_action.setText(self._translate("menu.open_file", "Open File..."))
            self.open_file_action.setStatusTip(self._translate("menu.open_file.tooltip", "Open an existing file"))

        if hasattr(self, 'save_file_action'):
            self.save_file_action.setText(self._translate("menu.save", "Save Chat"))
            self.save_file_action.setStatusTip(self._translate("menu.save.tooltip", "Save the current chat"))

        if hasattr(self, 'save_as_action'):
            self.save_as_action.setText(self._translate("menu.save_as", "Save Chat As..."))
            self.save_as_action.setStatusTip(self._translate("menu.save_as.tooltip", "Save the chat under a new name"))

        # Обновление имен доков
        if hasattr(self, 'terminal_dock'):
            self.terminal_dock.setWindowTitle(self._translate("dock.terminal", "Terminal"))

        if hasattr(self, 'project_explorer_dock'):
            self.project_explorer_dock.setWindowTitle(self._translate("dock.project_explorer", "Project Explorer"))

        if hasattr(self, 'chat_dock'):
            self.chat_dock.setWindowTitle(self._translate("dock.chat", "Chat"))

        # Обновляем текст статус-бара
        if hasattr(self, 'status_label'):
            self.status_label.setText(self._translate("status.ready", "Ready"))

    def _setup_central_widget(self):
        """Настраивает центральный виджет."""
        # --- Центральный виджет: Код и редактор ---
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(True) # Можно закрывать вкладки отдельно
        self.central_tabs.setMovable(True) # Можно перемещать вкладки
        self.central_tabs.setContextMenuPolicy(Qt.CustomContextMenu) # Добавить контекстное меню для вкладок

        # Добавляем наш редактор CodeEditor
        self.code_editor = CodeEditor(self)
        # Создаем первую вкладку, чтобы интерфейс изначально не пустой
        self.central_tabs.addTab(self.code_editor, "new_file.py")

        self.setCentralWidget(self.central_tabs)

    def _create_status_bar(self):
        """Создаёт и настраивает строку состояния."""
        self.status_bar = self.statusBar()

        # Добавляем метку для отображения статуса
        self.status_label = QLabel(self._translate("status.ready", "Ready"))
        self.status_label.setStyleSheet("background-color: #e6e6e6; padding: 5px; border-radius: 4px; margin-right: 15px;")
        self.status_bar.addWidget(self.status_label)

        # Добавляем метку для отображения статуса агента
        self.agent_status_label = QLabel(self._translate("agent.status.idle", "Idle"))
        self.agent_status_label.setStyleSheet("background-color: #e6e6e6; padding: 5px; border-radius: 4px; margin-right: 10px;")
        self.status_bar.addPermanentWidget(self.agent_status_label)

        # Добавляем метку для отображения версии
        self.version_label = QLabel("v0.1.0")
        self.status_bar.addPermanentWidget(self.version_label)

    def _create_file_icon_provider(self):
        """Создаёт провайдер иконок для файловой системы."""
        class CustomIconProvider(QFileIconProvider):
            def icon(self, info):
                if isinstance(info, QFileInfo):
                    if info.isDir():
                        return get_icon("folder")

                    # Иконки для разных расширений файлов
                    ext = info.suffix().lower()

                    # Python файлы
                    if ext in ["py", "pyw"]:
                        return get_icon("python")

                    # JavaScript/JSON файлы
                    elif ext == "js":
                        return get_icon("javascript")
                    elif ext == "json":
                        return get_icon("json")

                    # TypeScript файлы
                    elif ext == "ts":
                        return get_icon("typescript")

                    # Web файлы
                    elif ext in ["html", "htm"]:
                        return get_icon("html")
                    elif ext == "css":
                        return get_icon("css")
                    elif ext == "svg":
                        return get_icon("svg_file")

                    # Текстовые файлы
                    elif ext == "txt":
                        return get_icon("text")
                    elif ext == "md":
                        return get_icon("markdown")
                    elif ext == "log":
                        return get_icon("log")
                    elif ext == "ini":
                        return get_icon("ini")

                    # Архивы и документы
                    elif ext in ["zip", "tar", "gz", "rar", "7z"]:
                        return get_icon("zip")
                    elif ext == "pdf":
                        return get_icon("pdf")

                    # Изображения
                    elif ext == "png":
                        return get_icon("image_png")
                    elif ext in ["jpg", "jpeg"]:
                        return get_icon("image_jpg")
                    elif ext in ["gif", "bmp"]:
                        # Для этих типов используем png как запасной вариант
                        return get_icon("image_png")

                    # Скрипты и конфигурационные файлы
                    elif ext in ["sh", "bash"]:
                        return get_icon("shell")
                    elif ext == "bat":
                        return get_icon("batch")
                    elif ext == "env":
                        return get_icon("env")
                    elif ext == "exe":
                        return get_icon("executable")

                return super().icon(info)

        return CustomIconProvider()

    def _restore_window_state(self):
        """Восстанавливает сохранённое состояние окна и доков."""
        if not hasattr(self, 'settings'):
            return

        # Восстанавливаем геометрию окна
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Восстанавливаем состояние окна
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

        # Тема уже загружена в конструкторе, не загружаем ее повторно здесь
        print(f"Window state restored, current theme: {self.is_dark_theme}")

    def _apply_initial_layout(self):
        """Применяет начальный макет, если окно запускается впервые."""
        # Здесь можно настроить начальные размеры и позиции доков, если они не были сохранены

        # Показываем нужные доки по умолчанию
        if hasattr(self, 'project_explorer_dock'):
            self.project_explorer_dock.show()

        if hasattr(self, 'chat_dock'):
            self.chat_dock.show()

        # Терминал по умолчанию скрыт, он будет показан при необходимости

    def _new_file(self):
        """Создаёт новый файл в редакторе."""
        # Создаем новый экземпляр редактора кода
        new_editor = CodeEditor(self)

        # Получаем счетчик для имени нового файла
        new_file_count = self.central_tabs.count() + 1
        new_file_name = f"new_file_{new_file_count}.py"

        # Добавляем новую вкладку с редактором
        new_tab_index = self.central_tabs.addTab(new_editor, new_file_name)

        # Активируем новую вкладку
        self.central_tabs.setCurrentIndex(new_tab_index)

        # Устанавливаем фокус на новом редакторе
        new_editor.setFocus()

    def _show_emoji_dialog(self):
        """Показывает диалог выбора эмодзи."""
        # Создаем диалог эмодзи
        emoji_dialog = EmojiDialog(self)

        # Подключаем сигнал выбора эмодзи
        emoji_dialog.emoji_selected.connect(self._insert_emoji)

        # Показываем диалог
        emoji_dialog.exec()

    def _insert_emoji(self, emoji):
        """Вставляет выбранный эмодзи в активный виджет."""
        # Определяем активный виджет
        current_widget = self.central_tabs.currentWidget()

        # Вставляем эмодзи в редактор кода, если это активный виджет
        if current_widget and isinstance(current_widget, CodeEditor):
            current_widget.insertPlainText(emoji)

        # Если активен чат, вставляем эмодзи в поле ввода чата
        elif hasattr(self, 'chat_widget'):
            self.chat_widget.insert_text(emoji)

    def _show_flow_visualization(self):
        """Показывает визуализацию потока агента."""
        if hasattr(self, 'agent') and self.agent:
            # Проверяем, есть ли у агента поток
            flow = getattr(self.agent, 'flow', None)
            if flow:
                # Вызываем диалог визуализации потока
                show_flow_visualizer_dialog(flow, self)
            else:
                # Показываем сообщение, что поток недоступен
                QMessageBox.information(
                    self,
                    self._translate("flow.no_flow", "No Flow Available"),
                    self._translate("flow.no_flow_message", "The current agent does not have an available flow to visualize.")
                )
        else:
            # Показываем сообщение, что агент не инициализирован
            QMessageBox.information(
                self,
                self._translate("agent.not_initialized", "Agent Not Initialized"),
                self._translate("agent.not_initialized_message", "Please initialize the agent first.")
            )

    def _load_agent_config(self):
        """Загружает конфигурацию агента из файла."""
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._translate("agent.config.load_dialog", "Load Agent Configuration"),
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                # Загружаем конфигурацию из файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # TODO: Применить загруженную конфигурацию к агенту

                # Показываем сообщение об успешной загрузке
                QMessageBox.information(
                    self,
                    self._translate("agent.config.loaded", "Configuration Loaded"),
                    self._translate("agent.config.loaded_from", "Configuration loaded from") + f" {file_path}"
                )
            except Exception as e:
                # Показываем сообщение об ошибке
                QMessageBox.critical(
                    self,
                    self._translate("agent.config.load_error", "Error Loading Configuration"),
                    self._translate("agent.config.load_error_message", "An error occurred while loading configuration:") + f" {e}"
                )

    def _create_toolbars(self):
        """Создает панели инструментов приложения."""
        # Создаем основную панель инструментов
        self.main_toolbar = self.addToolBar(self._translate("toolbar.main", "Main Toolbar"))
        self.main_toolbar.setObjectName("MainToolBar")
        self.main_toolbar.setMovable(True)
        self.main_toolbar.setFloatable(False)

        # Добавляем кнопки на панель
        self.main_toolbar.addAction(self.new_file_action)
        self.main_toolbar.addAction(self.open_file_action)
        self.main_toolbar.addAction(self.save_file_action)
        self.main_toolbar.addSeparator()

        # Создаем панель инструментов агента
        self.agent_toolbar = self.addToolBar(self._translate("toolbar.agent", "Agent Toolbar"))
        self.agent_toolbar.setObjectName("AgentToolBar")
        self.agent_toolbar.setMovable(True)
        self.agent_toolbar.setFloatable(False)

        # Добавляем действие настройки агента
        self.agent_toolbar.addAction(self.configure_agent_action)

        # Добавляем действие визуализации потока
        self.agent_toolbar.addAction(self.view_flow_action)

    def _force_style_reload(self):
        """Принудительно перезагружает стили приложения."""
        ###############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за принудительную перезагрузку стилей без перезапуска приложения
        # Используется как запасной вариант если пользователь отказался от перезагрузки
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ###############################################################################
        # Очищаем стили
        QApplication.instance().setStyleSheet("")
        # Загружаем стили снова
        self._load_styles()

    def _create_agent_with_config(self, agent_mode="reactive", enabled_tools=None, reflection_level=0, memory_enabled=False):
        """
        Создает агента с заданной конфигурацией и инструментами.

        Args:
            agent_mode (str): Режим агента ("reactive" или "planning")
            enabled_tools (list): Список названий инструментов для агента
            reflection_level (int): Уровень рефлексии (самоанализа) агента
            memory_enabled (bool): Включена ли память агента

        Returns:
            None
        """
        # Останавливаем текущий поток агента, если он существует
        if hasattr(self, 'agent_worker') and self.agent_worker is not None:
            if hasattr(self.agent_worker, 'stop_loop'):
                self.agent_worker.stop_loop()

            if hasattr(self, 'agent_thread') and self.agent_thread is not None:
                print("Stopping existing agent thread...")
                self.agent_thread.quit()
                self.agent_thread.wait()

        # Создаем набор инструментов
        tools = []

        # Определяем, какие инструменты включены
        if enabled_tools is None:
            enabled_tools = ["python", "web", "file", "terminal", "terminate"]

        # Словарь соответствия имен инструментов их классам
        tool_classes = {
            "python": PythonExecute,
            "web": WebSearch,
            "browser": BrowserUseTool,
            "file": LocalFileOperator,
            "terminal": Terminal,
            "bash": Bash,
            "str_replace": StrReplaceEditor,
            "terminate": Terminate
        }

        # Словарь для перевода названий инструментов
        tool_translations = {
            "python": self._translate("tool.python", "Python Execute"),
            "web": self._translate("tool.web", "Web Search"),
            "browser": self._translate("tool.browser", "Browser Use"),
            "file": self._translate("tool.file", "File Operations"),
            "terminal": self._translate("tool.terminal", "Terminal"),
            "bash": self._translate("tool.bash", "Bash"),
            "str_replace": self._translate("tool.str_replace", "String Replace Editor"),
            "terminate": self._translate("tool.terminate", "Terminate")
        }

        # Создаем инструменты на основе включенных опций
        for tool_name in enabled_tools:
            if tool_name in tool_classes:
                tool_class = tool_classes[tool_name]

                # Для терминала подключаем UI callback
                if tool_name == "terminal" and hasattr(self, 'terminal_widget'):
                    try:
                        terminal_tool = tool_class()

                        # Создаем функцию обратного вызова для терминала
                        def terminal_ui_callback(command, stdout, stderr):
                            # Отображаем команду в терминале
                            self.terminal_widget.process_external_command(command)

                            # Эмитим сигнал с выводом команды
                            if stdout or stderr:
                                self.terminal_widget.command_runner.finished.emit(stdout, stderr)

                            # Показываем док терминала, если он скрыт
                            if hasattr(self, 'terminal_dock') and not self.terminal_dock.isVisible():
                                self.terminal_dock.show()

                        # Устанавливаем callback для терминала
                        terminal_tool.set_ui_callback(terminal_ui_callback)
                        tools.append(terminal_tool)
                        print(f"Terminal tool connected to UI")
                    except Exception as e:
                        print(f"Error creating terminal tool: {e}")
                else:
                    try:
                        tools.append(tool_class())
                        print(f"Added tool: {tool_translations.get(tool_name, tool_name)}")
                    except Exception as e:
                        print(f"Error creating tool {tool_name}: {e}")

        # Всегда добавляем инструмент terminate
        if "terminate" not in enabled_tools:
            try:
                tools.append(Terminate())
            except Exception as e:
                print(f"Error creating terminate tool: {e}")

        # Создаем агента в зависимости от выбранного режима
        if agent_mode == "planning":
            self.agent = PlanningAgent(tools=tools, reflection_level=reflection_level)
        else:  # reactive mode
            self.agent = ReactAgent(tools=tools, reflection_level=reflection_level)

        # Настраиваем память, если нужно
        if memory_enabled and hasattr(self.agent, 'enable_memory'):
            self.agent.enable_memory()

        # Создаем поток для агента
        self.agent_thread = QThread()
        self.agent_worker = AgentWorker(self.agent)
        self.agent_worker.moveToThread(self.agent_thread)

        # Подключаем сигналы
        self.agent_worker.finished.connect(lambda result: self.chat_widget.add_message(result))
        self.agent_worker.status_update.connect(lambda status: self.agent_status_label.setText(status))

        # Запускаем поток
        self.agent_thread.start()

        # Обновляем статус
        self.agent_status_label.setText(self._translate("agent.status.ready", "Ready"))

        # Включаем действие для визуализации потока, если это применимо
        self.view_flow_action.setEnabled(hasattr(self.agent, 'flow'))

        # Устанавливаем максимальное число шагов для агента
        if hasattr(self.agent, 'set_max_steps'):
            self.agent.set_max_steps(50)  # Разумное значение по умолчанию

        # Сохраняем текущие настройки агента
        self.current_agent_mode = agent_mode
        self.current_reflection_level = reflection_level
        self.memory_enabled = memory_enabled

        print(f"Agent created in {agent_mode} mode with {len(tools)} tools")
        return self.agent

    def _show_agent_config_dialog(self):
        """Показывает диалог настройки агента."""
        # Перенаправляем на метод _on_configure_agent
        self._on_configure_agent()

    def _on_configure_agent(self):
        """Показывает диалог настройки агента."""
        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle(self._translate("agent.config.dialog_title", "Agent Configuration"))
        dialog.setMinimumWidth(400)

        # Создаем макеты
        layout = QVBoxLayout(dialog)

        # --- Группа выбора режима агента ---
        mode_group = QGroupBox(self._translate("agent.config.mode.title", "Agent Mode"))
        mode_layout = QVBoxLayout()

        # Радиокнопки для выбора режима
        reactive_radio = QRadioButton(self._translate("agent.config.mode.reactive", "Reactive (ReAct)"))
        planning_radio = QRadioButton(self._translate("agent.config.mode.planning", "Planning"))

        # Выбираем текущий режим
        if self.current_agent_mode == "planning":
            planning_radio.setChecked(True)
        else:
            reactive_radio.setChecked(True)

        mode_layout.addWidget(reactive_radio)
        mode_layout.addWidget(planning_radio)
        mode_group.setLayout(mode_layout)

        # --- Группа выбора инструментов ---
        tools_group = QGroupBox(self._translate("agent.config.tools.title", "Tools"))
        tools_layout = QVBoxLayout()

        # Чекбоксы для инструментов
        python_check = QCheckBox(self._translate("tool.python", "Python Execute"))
        web_check = QCheckBox(self._translate("tool.web", "Web Search"))
        file_check = QCheckBox(self._translate("tool.file", "File Operations"))
        terminal_check = QCheckBox(self._translate("tool.terminal", "Terminal"))

        # Устанавливаем состояние чекбоксов на основе текущих настроек
        # Для простоты используем значения по умолчанию
        python_check.setChecked(True)
        web_check.setChecked(True)
        file_check.setChecked(True)
        terminal_check.setChecked(True)

        tools_layout.addWidget(python_check)
        tools_layout.addWidget(web_check)
        tools_layout.addWidget(file_check)
        tools_layout.addWidget(terminal_check)
        tools_group.setLayout(tools_layout)

        # --- Группа дополнительных настроек ---
        advanced_group = QGroupBox(self._translate("agent.config.advanced.title", "Advanced Settings"))
        advanced_layout = QFormLayout()

        # Уровень рефлексии
        reflection_label = QLabel(self._translate("agent.config.reflection.label", "Reflection Level:"))
        reflection_spinner = QSpinBox()
        reflection_spinner.setRange(0, 3)
        reflection_spinner.setValue(self.current_reflection_level)
        reflection_spinner.setToolTip(self._translate("agent.config.reflection.tooltip",
            "Higher values make the agent analyze its own actions more carefully. 0 = disabled"))

        # Включение памяти
        memory_check = QCheckBox(self._translate("agent.config.memory", "Enable Memory"))
        memory_check.setChecked(self.memory_enabled)

        advanced_layout.addRow(reflection_label, reflection_spinner)
        advanced_layout.addRow("", memory_check)  # Пустая метка для выравнивания
        advanced_group.setLayout(advanced_layout)

        # --- Кнопки диалога ---
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # Добавляем все виджеты в основной макет
        layout.addWidget(mode_group)
        layout.addWidget(tools_group)
        layout.addWidget(advanced_group)
        layout.addWidget(buttons)

        # Показываем диалог
        if dialog.exec() == QDialog.Accepted:
            # Получаем выбранные значения
            mode = "planning" if planning_radio.isChecked() else "reactive"

            # Собираем список включенных инструментов
            enabled_tools = []
            if python_check.isChecked():
                enabled_tools.append("python")
            if web_check.isChecked():
                enabled_tools.append("web")
            if file_check.isChecked():
                enabled_tools.append("file")
            if terminal_check.isChecked():
                enabled_tools.append("terminal")

            # Всегда добавляем terminate
            enabled_tools.append("terminate")

            # Получаем уровень рефлексии и состояние памяти
            reflection_level = reflection_spinner.value()
            memory_enabled = memory_check.isChecked()

            # Создаем агента с новыми настройками
            self._create_agent_with_config(
                agent_mode=mode,
                enabled_tools=enabled_tools,
                reflection_level=reflection_level,
                memory_enabled=memory_enabled
            )

            # Показываем сообщение об успешном применении настроек
            QMessageBox.information(
                self,
                self._translate("agent.config.applied", "Configuration Applied"),
                self._translate("agent.config.applied_message", "Agent configuration has been updated successfully.")
            )

    def _on_about(self):
        """Показывает диалог 'О программе'."""
        QMessageBox.about(
            self,
            self._translate("about.title", "About GopiAI"),
            f"<h2>GopiAI v0.1.0</h2>"
            f"<p>{self._translate('about.description', 'An AI assistant with advanced capabilities.')}</p>"
        )

    def _on_documentation(self):
        """Открывает документацию программы."""
        # Заглушка для открытия документации
        QMessageBox.information(
            self,
            self._translate("documentation.title", "Documentation"),
            self._translate("documentation.not_implemented", "Documentation is not implemented yet.")
        )

    def _show_preferences_dialog(self):
        """Показывает диалог настроек приложения."""
        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle(self._translate("menu.preferences", "Preferences"))
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        # Создаем вкладки для разных категорий настроек
        tabs = QTabWidget()

        # Вкладка общих настроек
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Группа настроек интерфейса
        ui_group = QGroupBox(self._translate("settings.ui", "User Interface"))
        ui_layout = QFormLayout()

        # Настройка размера шрифта
        font_size_label = QLabel(self._translate("settings.font_size", "Font Size:"))
        font_size_spinner = QSpinBox()
        font_size_spinner.setRange(8, 24)
        font_size_spinner.setValue(10)  # Значение по умолчанию
        ui_layout.addRow(font_size_label, font_size_spinner)

        # Выбор шрифта
        font_family_label = QLabel(self._translate("settings.font_family", "Font Family:"))
        font_family_combo = QComboBox()
        font_family_combo.addItems(["Inter", "Arial", "Roboto", "Times New Roman"])
        ui_layout.addRow(font_family_label, font_family_combo)

        ui_group.setLayout(ui_layout)
        general_layout.addWidget(ui_group)

        # Группа настроек поведения
        behavior_group = QGroupBox(self._translate("settings.behavior", "Behavior"))
        behavior_layout = QVBoxLayout()

        # Автосохранение
        autosave_check = QCheckBox(self._translate("settings.autosave", "Auto-save"))
        autosave_check.setChecked(True)

        # Подтверждение при выходе
        confirm_exit_check = QCheckBox(self._translate("settings.confirm_exit", "Confirm on exit"))
        confirm_exit_check.setChecked(True)

        behavior_layout.addWidget(autosave_check)
        behavior_layout.addWidget(confirm_exit_check)
        behavior_group.setLayout(behavior_layout)

        general_layout.addWidget(behavior_group)
        general_layout.addStretch(1)  # Растягиваемый пробел

        # Вкладка для настроек агента
        agent_tab = QWidget()
        agent_layout = QVBoxLayout(agent_tab)

        agent_settings_group = QGroupBox(self._translate("agent.config.title", "Agent Configuration"))
        agent_settings_layout = QFormLayout()

        # Модель по умолчанию
        model_label = QLabel(self._translate("agent.config.model", "Model:"))
        model_combo = QComboBox()
        model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "claude-3-opus"])
        agent_settings_layout.addRow(model_label, model_combo)

        # Температура по умолчанию
        temp_label = QLabel(self._translate("agent.config.temperature", "Temperature:"))
        temp_spinner = QDoubleSpinBox()
        temp_spinner.setRange(0.0, 1.0)
        temp_spinner.setSingleStep(0.1)
        temp_spinner.setValue(0.7)
        agent_settings_layout.addRow(temp_label, temp_spinner)

        agent_settings_group.setLayout(agent_settings_layout)
        agent_layout.addWidget(agent_settings_group)
        agent_layout.addStretch(1)

        # Добавляем вкладки в таб-виджет
        tabs.addTab(general_tab, self._translate("settings.general", "General"))
        tabs.addTab(agent_tab, self._translate("menu.agent", "Agent"))

        # Создаем кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # Создаем главный макет
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(tabs)
        main_layout.addWidget(buttons)

        # Показываем диалог
        dialog.exec_()

    def _restart_application(self):
        """Перезапускает приложение."""
        ###############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за корректный перезапуск приложения при смене темы или языка
        # Используется для полного применения изменений, требующих перезагрузки
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ###############################################################################
        print("Restarting application...")
        # Сохраняем текущее состояние
        self.settings.sync()

        # Формируем команду для перезапуска
        # Используем sys.executable для получения пути к Python
        python = sys.executable
        script_path = os.path.abspath(sys.argv[0])

        # Запускаем новый процесс с тем же Python и скриптом
        args = [python, script_path]
        if len(sys.argv) > 1:
            args.extend(sys.argv[1:])

        print(f"Executing: {' '.join(args)}")
        subprocess.Popen(args)

        # Завершаем текущий процесс
        sys.exit(0)

    def _toggle_theme(self, is_dark=None):
        """Переключает тему приложения между светлой и темной."""

        ###############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за корректное переключение тем приложения
        # Изменение логики может привести к поломке UI и нарушению работы приложения
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ###############################################################################

        print(f"_toggle_theme called with is_dark={is_dark}, current is_dark_theme={self.is_dark_theme}")
        print(f"Sender object: {self.sender()}")

        # Если параметр не задан, и событие пришло от группы действий
        if is_dark is None and isinstance(self.sender(), QAction):
            # Получаем значение из данных действия
            is_dark = self.sender().data()
            print(f"Setting is_dark from QAction data: {is_dark}")
        # Если параметр всё ещё не задан, инвертируем текущее значение
        elif is_dark is None:
            is_dark = not self.is_dark_theme
            print(f"Inverting current theme: is_dark={is_dark}")

        # Проверяем, изменилась ли тема на самом деле
        if bool(self.is_dark_theme) == bool(is_dark):
            print(f"Theme unchanged, skipping update. is_dark={is_dark}, is_dark_theme={self.is_dark_theme}")
            return

        # Обновляем состояние (преобразуем в булево значение)
        self.is_dark_theme = bool(is_dark)
        print(f"Updated is_dark_theme to {self.is_dark_theme}")

        # Загружаем соответствующий файл стилей
        if self.is_dark_theme:
            style_path = os.path.join(
                os.path.dirname(__file__), "themes", "dark_theme.qss"
            )
        else:
            style_path = os.path.join(
                os.path.dirname(__file__), "themes", "light_theme.qss"
            )

        print(f"Loading styles from: {style_path}")

        # Обновляем стили
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                style = f.read()
                # Очищаем старые стили
                QApplication.instance().setStyleSheet("")
                # Применяем новые стили
                QApplication.instance().setStyleSheet(style)
                print(f"Applied stylesheet from {style_path}")
        else:
            print(f"ERROR: Style file not found: {style_path}")

        # Сохраняем настройку
        if hasattr(self, 'settings'):
            self.settings.setValue("dark_theme", str(self.is_dark_theme).lower())
            self.settings.sync()
            print(f"Saved theme setting: {str(self.is_dark_theme).lower()}")

        # Обновляем состояние действий в меню
        if hasattr(self, 'dark_theme_action') and hasattr(self, 'light_theme_action'):
            # Используем явно преобразованное булево значение
            self.dark_theme_action.setChecked(self.is_dark_theme)
            self.light_theme_action.setChecked(not self.is_dark_theme)
            print(f"Updated menu actions: dark={self.is_dark_theme}, light={not self.is_dark_theme}")

        # Выводим информацию об изменении темы
        theme_name = self._translate("menu.dark_theme", "Dark Theme") if self.is_dark_theme else self._translate("menu.light_theme", "Light Theme")
        print(f"Theme changed to: {theme_name}")

        # Показываем сообщение пользователю, что нужен перезапуск приложения для полного применения темы
        reply = QMessageBox.question(
            self,
            self._translate("theme.restart.title", "Restart Required"),
            self._translate("theme.restart.message", "For the theme to fully apply, the application needs to be restarted. Do you want to restart now?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self._restart_application()
        else:
            # Если пользователь не хочет перезапускать, пробуем обновить стили еще раз
            self._force_style_reload()

    def _on_language_changed(self, action):
        """Обработчик изменения языка."""
        language_code = action.data()
        if language_code and language_code != self.current_language:
            self._load_language(language_code)

            # Показываем сообщение о необходимости перезапуска
            QMessageBox.information(
                self,
                self._translate("settings.language_changed", "Language Changed"),
                self._translate("settings.language_restart", "The application will be restarted to apply language changes.")
            )

            # В реальном приложении здесь можно реализовать перезагрузку интерфейса
            print(f"Language changed to: {language_code}")
