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
    QFileIconProvider,
    QHeaderView,
    QTableView,
    QFormLayout,
    QSpinBox
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
    QVariantAnimation
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
from app.ui.theme_manager import theme_manager  # Добавляем импорт theme_manager

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
        """Инициализация главного окна."""
        super().__init__()

        # Инициализация диалогов
        self.agent_config_dialog = None
        self.language_dialog = None
        self.preferences_dialog = None

        # Инициализация переменных
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

        self._setup_ui()

        # Восстанавливаем состояние окна и доков
        self._restore_window_state()

        # Применяем начальное расположение, если нет сохраненного состояния
        self._apply_initial_layout()

        # Проверяем, нужно создать агента с начальной конфигурацией
        self._create_agent_with_config()

        # Подключаем обработчик изменения темы
        theme_manager.themeChanged.connect(self._on_theme_changed)

        # Применяем фиксер кнопок закрытия вкладок
        CloseButtonFixer.apply_to_window(self)

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Устанавливаем заголовок окна
        self.setWindowTitle(theme_manager.get_translation("main_window", "GopiAI"))

        # Устанавливаем иконку приложения
        app_icon = QIcon(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets",
            "icons",
            "app_icon.png"
        ))
        self.setWindowIcon(app_icon)

        # Задаем минимальные размеры окна
        self.setMinimumSize(1200, 800)

        # Загружаем шрифты
        self._load_fonts()

        # Загружаем стили (темы)
        self._load_styles()

        # Создаем центральный виджет
        self._setup_central_widget()

        # Создаем док-виджеты
        self._create_docks()

        # Создаем меню и действия
        self._create_actions()
        self._create_menus()
        self._create_toolbars()

        # Создаем статус-бар
        self._create_status_bar()

        # Подключаем сигналы UI компонентов
        self._connect_ui_signals()

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

    def _load_styles(self, force_reload=False):
        """Загружает стили из текущей активной темы."""
        try:
            # Получаем путь к файлу темы
            style_path = theme_manager.get_theme_qss_path()

            if not style_path:
                print("Путь к файлу темы не найден")
                return

            print(f"Загрузка стилей из: {style_path}")

            if os.path.exists(style_path) or force_reload:
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
                    print(f"Стили загружены из {style_path}")
            else:
                print(f"Файл стиля не найден: {style_path}")
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")

    def _translate(self, key, default_text):
        """Возвращает перевод для указанного ключа или значение по умолчанию."""
        # Используем менеджер тем для получения переводов
        return theme_manager.get_translation(key, default_text)

    def _create_actions(self):
        """Создаем основные действия (для меню и тулбаров)."""

        # --- File Actions ---
        self.new_file_action = QAction(get_icon("new_document"), self._translate("menu.new", "New"), self)
        self.new_file_action.setShortcut("Ctrl+N")
        self.new_file_action.setStatusTip(self._translate("menu.new.tooltip", "Create a new file"))
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

        self.open_file_action = QAction(get_icon("open"), self._translate("menu.open_file", "Open File..."), self)
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_file_action.setStatusTip(self._translate("menu.open_file.tooltip", "Open an existing file"))
        # Подключаем действие к обработчику
        self.open_file_action.triggered.connect(self._open_file)

        self.save_file_action = QAction(get_icon("save"), self._translate("menu.save", "Save"), self)
        self.save_file_action.setShortcut("Ctrl+S")
        self.save_file_action.setStatusTip(self._translate("menu.save.tooltip", "Save the current file"))
        # Подключаем действие к обработчику
        self.save_file_action.triggered.connect(self._save_file)

        # Добавляем Save As...
        self.save_as_action = QAction(get_icon("save"), self._translate("menu.save_as", "Save As..."), self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip(self._translate("menu.save_as.tooltip", "Save the current file under a new name"))
        # Подключаем действие к обработчику
        self.save_as_action.triggered.connect(self._save_file_as)

        # --- Exit Action ---
        self.exit_action = QAction(get_icon("close"), self._translate("menu.exit", "Exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip(self._translate("menu.exit.tooltip", "Exit the application"))

        # --- Edit Actions ---
        self.cut_action = QAction(self._translate("menu.cut", "Cu&t"), self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setStatusTip(self._translate("menu.cut.tooltip", "Cut the selected content to the clipboard"))

        self.copy_action = QAction(self._translate("menu.copy", "&Copy"), self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setStatusTip(self._translate("menu.copy.tooltip", "Copy the selected content to the clipboard"))

        self.paste_action = QAction(self._translate("menu.paste", "&Paste"), self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setStatusTip(self._translate("menu.paste.tooltip", "Paste content from the clipboard"))

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

        # Создаем меню тем
        self._update_themes_menu()

        # Подменю выбора языка
        self.language_menu = self.view_menu.addMenu(self._translate("menu.language", "Language"))

        # Добавляем опцию для диалога выбора языка
        language_select_action = QAction(self._translate("dialogs.preferences.language", "Select Language..."), self)
        language_select_action.triggered.connect(self._show_language_dialog)
        self.language_menu.addAction(language_select_action)

        self.view_menu.addSeparator()

        # Добавляем действия для показа/скрытия панелей
        self.view_menu.addAction(self.toggle_terminal_action)
        if hasattr(self, 'toggle_project_explorer_action'):
            self.view_menu.addAction(self.toggle_project_explorer_action)
        if hasattr(self, 'toggle_chat_action'):
            self.view_menu.addAction(self.toggle_chat_action)

        # --- Tools Menu ---
        self.tools_menu = self.menu_bar.addMenu(self._translate("menu.tools", "Tools"))

        # Действие для настройки агента
        self.configure_agent_action = QAction(
            get_icon("settings"), self._translate("menu.configure_agent", "Configure Agent..."), self
        )
        self.configure_agent_action.setStatusTip(
            self._translate("menu.configure_agent.tooltip", "Configure agent settings")
        )
        self.configure_agent_action.triggered.connect(self._on_configure_agent)
        self.tools_menu.addAction(self.configure_agent_action)

        # Действие для визуализации потока
        self.tools_menu.addAction(self.view_flow_action)

        # Действие для настроек
        self.preferences_action = QAction(
            get_icon("preferences"), self._translate("menu.preferences", "Preferences..."), self
        )
        self.preferences_action.setStatusTip(
            self._translate("menu.preferences.tooltip", "Edit application preferences")
        )
        self.preferences_action.triggered.connect(self._show_preferences_dialog)
        self.tools_menu.addAction(self.preferences_action)

        # --- Help Menu ---
        self.help_menu = self.menu_bar.addMenu(self._translate("menu.help", "Help"))

        # About action
        self.about_action = QAction(
            get_icon("info"), self._translate("menu.about", "About GopiAI"), self
        )
        self.about_action.triggered.connect(self._on_about)
        self.help_menu.addAction(self.about_action)

        # Documentation action
        self.documentation_action = QAction(
            get_icon("documentation"), self._translate("menu.documentation", "Documentation"), self
        )
        self.documentation_action.triggered.connect(self._on_documentation)
        self.help_menu.addAction(self.documentation_action)

    def changeEvent(self, event):
        """Обработчик события изменения интерфейса (включая смену языка)."""
        if event.type() == QEvent.LanguageChange:
            # Обновляем все переводы
            self._update_ui_translations()

        # Передаем событие родительскому классу для обработки
        super().changeEvent(event)

    def _create_docks(self):
        """Создает боковые панели (dock-виджеты) приложения."""
        # --- Левая панель: Проводник проекта ---
        self.project_explorer_dock = QDockWidget(self._translate("dock.project_explorer", "Проводник проекта"), self)
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

        # Настройка drag & drop
        self.project_tree.setDragEnabled(True)
        self.project_tree.setDropIndicatorShown(True)
        # Двойной клик на элементе
        self.project_tree.doubleClicked.connect(self._on_project_tree_double_clicked)

        # Скрываем ненужные колонки, оставляем только имя
        self.project_tree.setHeaderHidden(True)
        for i in range(1, self.fs_model.columnCount()):
            self.project_tree.hideColumn(i)

        project_explorer_layout.addLayout(workspace_layout)
        project_explorer_layout.addWidget(self.project_tree)

        self.project_explorer_dock.setWidget(project_explorer_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_explorer_dock)

        # --- Правая панель: Чат ---
        self.chat_dock = QDockWidget(self._translate("dock.chat", "Chat"), self)
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
        self.terminal_dock = QDockWidget(self._translate("dock.terminal", "Terminal"), self)
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
        """Подключает сигналы UI компонентов к соответствующим слотам."""
        # Подключение signals к слотам
        if hasattr(self, 'exit_action'):
            self.exit_action.triggered.connect(self.close)

        # Обработка событий от проводника проекта
        if hasattr(self, 'project_tree'):
            self.project_tree.doubleClicked.connect(self._open_file_from_tree)
            self.project_tree.customContextMenuRequested.connect(self._show_project_tree_context_menu)

        # Обработчики изменения видимости панелей
        if hasattr(self, 'toggle_terminal_action'):
            self.toggle_terminal_action.triggered.connect(self._toggle_terminal)

        if hasattr(self, 'toggle_project_explorer_action'):
            self.toggle_project_explorer_action.triggered.connect(self._toggle_project_explorer)

        if hasattr(self, 'toggle_chat_action'):
            self.toggle_chat_action.triggered.connect(self._toggle_chat)

        # Подключаем действия редактирования
        if hasattr(self, 'cut_action'):
            self.cut_action.triggered.connect(self._on_cut)

        if hasattr(self, 'copy_action'):
            self.copy_action.triggered.connect(self._on_copy)

        if hasattr(self, 'paste_action'):
            self.paste_action.triggered.connect(self._on_paste)

        # Подключаем чат к обработчику сообщений
        if hasattr(self, 'chat_widget'):
            self.chat_widget.message_sent.connect(self._handle_user_message)

        # Подключение сигналов от действий меню
        if hasattr(self, 'configure_agent_action'):
            self.configure_agent_action.triggered.connect(self._show_agent_config_dialog)

        # Подключаем новое действие настроек приложения
        if hasattr(self, 'preferences_action'):
            self.preferences_action.triggered.connect(self._show_preferences_dialog)

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

    def _update_ui_translations(self):
        """Обновляет все переводимые элементы интерфейса."""
        # Устанавливаем флаг, что идет процесс обновления переводов, чтобы избежать рекурсивных вызовов
        if hasattr(self, '_is_updating_translations') and self._is_updating_translations:
            return

        self._is_updating_translations = True

        try:
            # Обновление заголовка окна
            self.setWindowTitle(self._translate("main_window", "GopiAI"))

            # Обновление действий меню File
            if hasattr(self, 'new_file_action'):
                self.new_file_action.setText(self._translate("menu.new", "New"))
                self.new_file_action.setStatusTip(self._translate("menu.new.tooltip", "Create a new file"))

            if hasattr(self, 'open_file_action'):
                self.open_file_action.setText(self._translate("menu.open_file", "Open File..."))
                self.open_file_action.setStatusTip(self._translate("menu.open_file.tooltip", "Open an existing file"))

            if hasattr(self, 'save_file_action'):
                self.save_file_action.setText(self._translate("menu.save", "Save"))
                self.save_file_action.setStatusTip(self._translate("menu.save.tooltip", "Save the current file"))

            if hasattr(self, 'save_as_action'):
                self.save_as_action.setText(self._translate("menu.save_as", "Save As..."))
                self.save_as_action.setStatusTip(self._translate("menu.save_as.tooltip", "Save the current file under a new name"))

            if hasattr(self, 'exit_action'):
                self.exit_action.setText(self._translate("menu.exit", "Exit"))
                self.exit_action.setStatusTip(self._translate("menu.exit.tooltip", "Exit the application"))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню Edit
            if hasattr(self, 'cut_action'):
                self.cut_action.setText(self._translate("menu.cut", "Cut"))
                self.cut_action.setStatusTip(self._translate("menu.cut.tooltip", "Cut the selected text"))

            if hasattr(self, 'copy_action'):
                self.copy_action.setText(self._translate("menu.copy", "Copy"))
                self.copy_action.setStatusTip(self._translate("menu.copy.tooltip", "Copy the selected text"))

            if hasattr(self, 'paste_action'):
                self.paste_action.setText(self._translate("menu.paste", "Paste"))
                self.paste_action.setStatusTip(self._translate("menu.paste.tooltip", "Paste text from clipboard"))

            if hasattr(self, 'emoji_action'):
                self.emoji_action.setText(self._translate("menu.emoji", "Insert Emoji..."))
                self.emoji_action.setStatusTip(self._translate("menu.emoji.tooltip", "Open emoji selector"))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню View
            if hasattr(self, 'toggle_terminal_action'):
                self.toggle_terminal_action.setText(self._translate("dock.terminal.toggle", "Show Terminal"))

            if hasattr(self, 'toggle_project_explorer_action'):
                self.toggle_project_explorer_action.setText(self._translate("dock.project_explorer.toggle", "Show Project Explorer"))

            if hasattr(self, 'toggle_chat_action'):
                self.toggle_chat_action.setText(self._translate("dock.chat.toggle", "Show Chat"))

            # Обновление действий меню Tools
            if hasattr(self, 'configure_agent_action'):
                self.configure_agent_action.setText(self._translate("menu.configure_agent", "Configure Agent..."))
                self.configure_agent_action.setStatusTip(self._translate("menu.configure_agent.tooltip", "Configure agent settings"))

            if hasattr(self, 'view_flow_action'):
                self.view_flow_action.setText(self._translate("menu.view_flow", "Show Flow Visualization"))
                self.view_flow_action.setStatusTip(self._translate("menu.view_flow.tooltip", "Visualize agent's flow"))

            if hasattr(self, 'preferences_action'):
                self.preferences_action.setText(self._translate("menu.preferences", "Preferences..."))
                self.preferences_action.setStatusTip(self._translate("menu.preferences.tooltip", "Edit application preferences"))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню Help
            if hasattr(self, 'about_action'):
                self.about_action.setText(self._translate("menu.about", "About GopiAI"))

            if hasattr(self, 'documentation_action'):
                self.documentation_action.setText(self._translate("menu.documentation", "Documentation"))

            # Обновление меню
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(self._translate("menu.file", "File"))

            if hasattr(self, 'edit_menu'):
                self.edit_menu.setTitle(self._translate("menu.edit", "Edit"))

            if hasattr(self, 'view_menu'):
                self.view_menu.setTitle(self._translate("menu.view", "View"))

            if hasattr(self, 'tools_menu'):
                self.tools_menu.setTitle(self._translate("menu.tools", "Tools"))

            if hasattr(self, 'help_menu'):
                self.help_menu.setTitle(self._translate("menu.help", "Help"))

            if hasattr(self, 'theme_menu'):
                self.theme_menu.setTitle(self._translate("menu.theme", "Theme"))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

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

            # Принудительно вызываем событие изменения языка для всех виджетов
            # но ограничиваем количество, чтобы избежать зависания
            count = 0
            max_widgets = 100  # Ограничение, чтобы избежать зависания

            event = QEvent(QEvent.LanguageChange)
            for widget in QApplication.allWidgets():
                QApplication.sendEvent(widget, event)
                count += 1
                if count >= max_widgets:
                    # Обработка событий и сброс счетчика
                    QApplication.processEvents()
                    count = 0

        finally:
            # Снимаем флаг обновления переводов в любом случае
            self._is_updating_translations = False

            # Финальная обработка событий
            QApplication.processEvents()

    def _setup_central_widget(self):
        """Настраивает центральный виджет."""
        # --- Центральный виджет: Код и редактор ---
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(True) # Можно закрывать вкладки отдельно
        self.central_tabs.setMovable(True) # Можно перемещать вкладки
        self.central_tabs.setContextMenuPolicy(Qt.CustomContextMenu) # Добавить контекстное меню для вкладок

        # Подключаем обработчик контекстного меню
        self.central_tabs.customContextMenuRequested.connect(self._show_tab_context_menu)

        # Подключаем обработчик закрытия вкладок
        self.central_tabs.tabCloseRequested.connect(self._close_tab)

        # Добавляем наш редактор CodeEditor
        self.code_editor = CodeEditor(self)
        # Создаем первую вкладку, чтобы интерфейс изначально не пустой
        self.central_tabs.addTab(self.code_editor, self._translate("code.new_file", "new_file.py"))

        self.setCentralWidget(self.central_tabs)

    def _show_tab_context_menu(self, position):
        """Показывает контекстное меню для вкладок."""
        # Получаем индекс вкладки под курсором
        tab_index = self.central_tabs.tabBar().tabAt(position)
        if tab_index < 0:
            return

        # Создаем контекстное меню
        menu = QMenu(self)

        # Добавляем действия
        close_tab_action = menu.addAction(self._translate("menu.close", "Закрыть"))
        close_other_tabs_action = menu.addAction(self._translate("dialogs.close_others", "Закрыть другие вкладки"))
        close_all_tabs_action = menu.addAction(self._translate("dialogs.close_all", "Закрыть все вкладки"))
        menu.addSeparator()
        save_tab_action = menu.addAction(self._translate("menu.save", "Сохранить"))
        save_as_tab_action = menu.addAction(self._translate("menu.save_as", "Сохранить как..."))

        # Показываем меню и получаем выбранное действие
        action = menu.exec_(self.central_tabs.tabBar().mapToGlobal(position))

        # Обрабатываем выбранное действие
        if action == close_tab_action:
            self._close_tab(tab_index)
        elif action == close_other_tabs_action:
            self._close_other_tabs(tab_index)
        elif action == close_all_tabs_action:
            self._close_all_tabs()
        elif action == save_tab_action:
            self._save_tab(tab_index)
        elif action == save_as_tab_action:
            self._save_tab_as(tab_index)

    def _close_other_tabs(self, keep_index):
        """Закрывает все вкладки, кроме указанной."""
        # Получаем список индексов для закрытия в обратном порядке
        indices_to_close = [i for i in range(self.central_tabs.count()) if i != keep_index]
        indices_to_close.sort(reverse=True)

        # Закрываем каждую вкладку
        for idx in indices_to_close:
            self._close_tab(idx)

        # Обработка событий после массового закрытия
        QApplication.processEvents()

    def _close_all_tabs(self):
        """Закрывает все вкладки."""
        # Получаем список индексов для закрытия в обратном порядке
        indices_to_close = range(self.central_tabs.count() - 1, -1, -1)

        # Закрываем каждую вкладку
        for idx in indices_to_close:
            self._close_tab(idx)

        # Обработка событий после массового закрытия
        QApplication.processEvents()

        # Добавляем новую вкладку, если нужно
        if self.central_tabs.count() == 0:
            self._new_file()

    def _save_tab(self, index):
        """Сохраняет содержимое указанной вкладки."""
        # Запоминаем текущий индекс
        current_index = self.central_tabs.currentIndex()

        # Активируем вкладку для сохранения
        self.central_tabs.setCurrentIndex(index)

        # Сохраняем файл
        self._save_file()

        # Возвращаемся к исходной вкладке
        self.central_tabs.setCurrentIndex(current_index)

    def _save_tab_as(self, index):
        """Сохраняет содержимое указанной вкладки под новым именем."""
        # Запоминаем текущий индекс
        current_index = self.central_tabs.currentIndex()

        # Активируем вкладку для сохранения
        self.central_tabs.setCurrentIndex(index)

        # Сохраняем файл под новым именем
        self._save_file_as()

        # Возвращаемся к исходной вкладке
        self.central_tabs.setCurrentIndex(current_index)

    def _close_tab(self, index):
        """Закрывает вкладку с указанным индексом."""
        # Проверяем, есть ли несохраненные изменения
        widget = self.central_tabs.widget(index)
        if hasattr(widget, 'document') and widget.document().isModified():
            # Спрашиваем пользователя, хочет ли он сохранить изменения
            reply = QMessageBox.question(
                self,
                self._translate("dialogs.save_changes", "Сохранить изменения?"),
                self._translate("dialogs.unsaved_changes", "У вас есть несохраненные изменения. Вы хотите сохранить их?"),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            # Обработка событий после вопроса
            QApplication.processEvents()

            # Обработка ответа пользователя
            if reply == QMessageBox.Yes:
                # Сохраняем файл и закрываем вкладку
                self._save_file()
            elif reply == QMessageBox.Cancel:
                # Отменяем закрытие
                return

        # Запоминаем виджет перед удалением вкладки
        tab_widget = self.central_tabs.widget(index)

        # Закрываем вкладку
        self.central_tabs.removeTab(index)

        # Удаляем виджет из памяти
        if tab_widget:
            tab_widget.deleteLater()

        # Обработка событий после закрытия вкладки
        QApplication.processEvents()

        # Если все вкладки закрыты, создаем новую
        if self.central_tabs.count() == 0:
            self._new_file()

    def _create_status_bar(self):
        """Создаёт и настраивает строку состояния."""
        self.status_bar = self.statusBar()

        # Добавляем метку для отображения статуса
        self.status_label = QLabel(self._translate("status.ready", "Ready"))
        self.status_label.setStyleSheet("""
            background-color: #e6e6e6;
            color: #333333;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
            margin-right: 15px;
        """)
        self.status_bar.addWidget(self.status_label)

        # Добавляем метку для отображения статуса агента
        self.agent_status_label = QLabel(self._translate("agent.status.idle", "Idle"))
        self.agent_status_label.setStyleSheet("""
            background-color: #e6e6e6;
            color: #333333;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
            margin-right: 10px;
        """)
        self.status_bar.addPermanentWidget(self.agent_status_label)

        # Добавляем метку для отображения версии
        self.version_label = QLabel("v0.1.0")
        self.version_label.setStyleSheet("""
            color: #555555;
            font-weight: bold;
        """)
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

        # Выводим информацию о текущей теме
        print(f"Window state restored, current theme: {theme_manager.get_current_theme()}")

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
        # Если активен чат, вставляем эмодзи в поле ввода чата
        if hasattr(self, 'chat_widget'):
            self.chat_widget.insert_text(emoji)
        # Иначе вставляем в редактор кода, если это активный виджет
        else:
            # Определяем активный виджет
            current_widget = self.central_tabs.currentWidget()
            # Вставляем эмодзи в редактор кода, если это активный виджет
            if current_widget and isinstance(current_widget, CodeEditor):
                current_widget.insertPlainText(emoji)

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
        """Принудительно перезагружает стили всех виджетов."""
        # Защита от рекурсивных вызовов
        if hasattr(self, '_is_reloading_style') and self._is_reloading_style:
            return

        self._is_reloading_style = True

        try:
            # Количество обработанных виджетов
            count = 0
            # Максимальное количество виджетов для обработки перед обновлением событий
            max_widgets = 50

            # Получаем текущий стиль приложения
            current_style = self.style().objectName()

            # Применяем стиль заново к виджетам
            for widget in QApplication.allWidgets():
                if widget.isWidgetType():
                    widget.setStyle(QApplication.style())

                    # Особая обработка для QHeaderView, который требует аргумент для update()
                    if isinstance(widget, QHeaderView):
                        # Обновляем всю область виджета
                        widget.update(widget.rect())
                    else:
                        # Для остальных виджетов вызываем обычный update()
                        widget.update()

                    # Увеличиваем счетчик и проверяем, нужно ли обработать события
                    count += 1
                    if count >= max_widgets:
                        # Обрабатываем события через каждые max_widgets виджетов
                        QApplication.processEvents()
                        count = 0

            # Обновляем главное окно
            self.update()

        finally:
            # Сбрасываем флаг в любом случае
            self._is_reloading_style = False

            # Финальная обработка событий
            QApplication.processEvents()

    def _update_themes_menu(self):
        """Обновляет меню выбора тем на основе доступных тем."""
        # Очищаем существующее меню тем
        if hasattr(self, 'theme_menu'):
            self.theme_menu.clear()

            # Создаем группу для взаимоисключающих действий выбора темы
            self.theme_action_group = QActionGroup(self)

            # Получаем список доступных тем
            themes = theme_manager.get_available_themes()
            current_theme = theme_manager.get_current_theme()

            for theme in themes:
                theme_display_name = theme_manager.get_theme_display_name(theme)
                theme_action = QAction(theme_display_name, self)
                theme_action.setCheckable(True)
                theme_action.setChecked(theme == current_theme)
                theme_action.setData(theme)
                theme_action.triggered.connect(self._on_theme_action_triggered)

                self.theme_action_group.addAction(theme_action)
                self.theme_menu.addAction(theme_action)

    def _on_theme_action_triggered(self):
        """Обработчик выбора темы из меню."""
        action = self.sender()
        if action and isinstance(action, QAction):
            theme_name = action.data()
            if theme_name:
                theme_manager.switch_theme(theme_name)

    def _on_theme_changed(self, theme_name):
        """Обработчик сигнала изменения темы."""
        # Проверяем, идет ли уже смена темы, чтобы избежать рекурсии
        if hasattr(self, '_is_changing_theme') and self._is_changing_theme:
            return

        self._is_changing_theme = True

        try:
            # Уведомление о процессе смены темы
            if hasattr(self, 'status_label'):
                theme_display_name = theme_manager.get_theme_display_name(theme_name)
                self.status_label.setText(self._translate("status.theme_changing", f"Changing theme to {theme_display_name}..."))

            # Обрабатываем события, чтобы обновить статус
            QApplication.processEvents()

            # Загружаем стили из новой темы
            self._load_styles(force_reload=True)

            # Обновляем переводы интерфейса
            self._update_ui_translations()

            # Обновляем состояние меню
            self._update_view_menu()

            # Обрабатываем события перед вызовом принудительного обновления стилей
            QApplication.processEvents()

            # Принудительно обновляем стили после обработки событий
            self._force_style_reload()

            # Показываем уведомление об успешной смене темы
            theme_display_name = theme_manager.get_theme_display_name(theme_name)
            if hasattr(self, 'status_label'):
                self.status_label.setText(self._translate(
                    "status.theme_changed",
                    f"Theme changed to {theme_display_name}"
                ))

        finally:
            # Снимаем флаг смены темы в любом случае
            self._is_changing_theme = False

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
        self.agent_worker.finished.connect(self._handle_agent_response)
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

    def _handle_agent_response(self, result):
        """Обрабатывает ответ от агента и отображает его в чате."""
        try:
            message = None

            print(f"Received agent response of type: {type(result)}")

            # Обработка различных типов ответов
            if isinstance(result, dict):
                if 'result' in result:
                    message = result['result']
                elif 'text' in result:
                    message = result['text']
                elif 'output' in result:
                    message = result['output']
                else:
                    # Преобразуем словарь в строку JSON
                    import json
                    message = json.dumps(result, indent=2, ensure_ascii=False)
            elif isinstance(result, str):
                # Если результат - просто строка
                message = result
            elif result is None:
                # Пустой ответ
                message = "Задача выполнена."
            else:
                # Для других форматов преобразуем в строку
                message = str(result)

            # Проверка на пустое сообщение
            if not message or message.strip() == "":
                message = "Задача выполнена, но ответ пустой."

            # Добавляем сообщение в чат
            self.chat_widget.add_message("Assistant", message)

            # Обновляем статус агента
            self.agent_status_label.setText(self._translate("agent.status.ready", "Ready"))

        except Exception as e:
            print(f"Error handling agent response: {e}")
            error_message = f"Ошибка при обработке ответа: {str(e)}"
            self.chat_widget.add_message("System", error_message)
            self.agent_status_label.setText(self._translate("agent.status.error", "Error"))

    def _show_agent_config_dialog(self):
        """Показывает диалог настройки агента."""
        # Перенаправляем на метод _on_configure_agent
        self._on_configure_agent()

    def _on_configure_agent(self):
        """Показывает диалог настройки агента."""
        # Проверяем, существует ли уже диалог и видим ли он
        if self.agent_config_dialog is not None and self.agent_config_dialog.isVisible():
            # Если диалог уже открыт, активируем его и выходим
            self.agent_config_dialog.activateWindow()
            self.agent_config_dialog.raise_()
            return

        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle(self._translate("agent.config.dialog_title", "Настройка агента"))
        # Устанавливаем правильный режим модальности
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(400)

        # Добавляем обработку клавиши Escape для закрытия диалога
        dialog.keyPressEvent = lambda event: dialog.reject() if event.key() == Qt.Key_Escape else QDialog.keyPressEvent(dialog, event)

        # Создаем макеты
        layout = QVBoxLayout(dialog)

        # --- Группа выбора режима агента ---
        mode_group = QGroupBox(self._translate("agent.mode.title", "Agent Mode"))
        mode_layout = QVBoxLayout(mode_group)

        # Радиокнопки для выбора режима
        self.reactive_radio = QRadioButton(self._translate("agent.mode.reactive", "Reactive Mode"))
        self.planning_radio = QRadioButton(self._translate("agent.mode.planning", "Planning"))

        if self.current_agent_mode == "reactive":
            self.reactive_radio.setChecked(True)
        else:
            self.planning_radio.setChecked(True)

        mode_layout.addWidget(self.reactive_radio)
        mode_layout.addWidget(self.planning_radio)
        layout.addWidget(mode_group)

        # --- Группа инструментов агента ---
        tools_group = QGroupBox(self._translate("agent.tools.title", "Инструменты"))
        tools_layout = QVBoxLayout(tools_group)

        # Добавить инструменты (заглушка)
        tools_layout.addWidget(QLabel(self._translate("agent.tools.developing",
                                     "Настройка инструментов в разработке")))
        layout.addWidget(tools_group)

        # --- Расширенные настройки ---
        advanced_group = QGroupBox(self._translate("agent.advanced.title", "Расширенные настройки"))
        advanced_layout = QVBoxLayout(advanced_group)

        # Уровень рефлексии
        reflection_layout = QHBoxLayout()
        reflection_label = QLabel(self._translate("agent.reflection.level", "Уровень рефлексии:"))
        self.reflection_spinner = QDoubleSpinBox()
        self.reflection_spinner.setRange(0, 1.0)
        self.reflection_spinner.setSingleStep(0.1)
        self.reflection_spinner.setValue(self.current_reflection_level)
        reflection_layout.addWidget(reflection_label)
        reflection_layout.addWidget(self.reflection_spinner)
        advanced_layout.addLayout(reflection_layout)

        # Память
        self.memory_checkbox = QCheckBox(self._translate("agent.memory.enable", "Включить память"))
        self.memory_checkbox.setChecked(self.memory_enabled)
        advanced_layout.addWidget(self.memory_checkbox)

        layout.addWidget(advanced_group)

        # Кнопки с переводом текста
        button_box = QDialogButtonBox()
        ok_button = button_box.addButton(self._translate("dialogs.ok", "OK"), QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton(self._translate("dialogs.cancel", "Cancel"), QDialogButtonBox.RejectRole)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Подключаем сигнал закрытия диалога к обработчику
        dialog.finished.connect(self._on_agent_config_finished)

        # Сохраняем ссылки на виджеты для обработки в колбэке
        dialog.reactive_radio = self.reactive_radio
        dialog.planning_radio = self.planning_radio
        dialog.reflection_spinner = self.reflection_spinner
        dialog.memory_checkbox = self.memory_checkbox

        # Сохраняем ссылку на диалог
        self.agent_config_dialog = dialog

        # Показываем диалог и запускаем цикл обработки событий
        dialog.open()
        # Обрабатываем ожидающие события Qt для решения проблемы с необходимостью двойного нажатия
        QApplication.processEvents()
        QApplication.processEvents()  # Двойной вызов для лучшей работы

    def _on_agent_config_finished(self, result):
        """Обрабатывает результат закрытия диалога настройки агента."""
        # Удаляем ссылку на диалог при закрытии
        self.agent_config_dialog = None

        if result == QDialog.Accepted:
            dialog = self.sender()

            # Применяем выбранные настройки
            if dialog.reactive_radio.isChecked():
                self.current_agent_mode = "reactive"
            else:
                self.current_agent_mode = "planning"

            self.current_reflection_level = dialog.reflection_spinner.value()
            self.memory_enabled = dialog.memory_checkbox.isChecked()

            # Если агент активен, пересоздаем его с новыми настройками
            if self.agent:
                self._create_agent_with_config()

            # Показываем сообщение о успешном применении настроек
            msg = QMessageBox()
            msg.setWindowTitle(self._translate("agent.config.applied_title", "Настройки применены"))
            msg.setText(self._translate("agent.config.applied_message",
                        "Настройки агента успешно обновлены!"))
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            QApplication.processEvents()  # Добавляем обработку событий после сообщения

    def _show_language_dialog(self):
        """Показывает диалог выбора языка."""
        # Проверяем, существует ли уже диалог и видим ли он
        if self.language_dialog is not None and self.language_dialog.isVisible():
            # Если диалог уже открыт, активируем его и выходим
            self.language_dialog.activateWindow()
            self.language_dialog.raise_()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(self._translate("settings.language.title", "Настройки языка"))
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(300)

        # Добавляем обработку клавиши Escape для закрытия диалога
        dialog.keyPressEvent = lambda event: dialog.reject() if event.key() == Qt.Key_Escape else QDialog.keyPressEvent(dialog, event)

        layout = QVBoxLayout(dialog)

        # Выбор языка
        language_layout = QHBoxLayout()
        language_label = QLabel(self._translate("settings.language.label", "Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en_US")
        self.language_combo.addItem("Русский", "ru_RU")

        # Устанавливаем текущий язык
        current_language = theme_manager.get_current_language()
        index = 0
        if current_language == "ru_RU":
            index = 1
        self.language_combo.setCurrentIndex(index)

        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        # Информационное сообщение
        info_label = QLabel(self._translate(
            "settings.language.restart_required",
            "Some changes require restarting the application"
        ))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Кнопки с переводом
        button_box = QDialogButtonBox()
        ok_button = button_box.addButton(self._translate("dialogs.ok", "OK"), QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton(self._translate("dialogs.cancel", "Cancel"), QDialogButtonBox.RejectRole)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Подключаем сигнал закрытия диалога
        dialog.finished.connect(self._on_language_dialog_finished)

        # Сохраняем ссылку на комбобокс
        dialog.language_combo = self.language_combo

        # Показываем диалог и запускаем цикл обработки событий
        dialog.open()
        # Обрабатываем ожидающие события Qt для решения проблемы с необходимостью двойного нажатия
        QApplication.processEvents()
        QApplication.processEvents()  # Двойной вызов для лучшей работы

        # Сохраняем ссылку на диалог
        self.language_dialog = dialog

    def _on_language_dialog_finished(self, result):
        """Обрабатывает результат закрытия диалога выбора языка."""
        # Удаляем ссылку на диалог
        self.language_dialog = None

        if result == QDialog.Accepted:
            dialog = self.sender()

            # Получаем выбранный язык
            selected_language = dialog.language_combo.currentData()

            # Изменяем тему и язык
            current_theme_type = "dark" if "dark" in theme_manager.current_theme else "light"
            theme_manager.switch_theme(f"{current_theme_type}_{selected_language.lower()[:2]}")

            # Показываем сообщение о успешном изменении языка
            restart_message = QMessageBox()
            restart_message.setWindowTitle(self._translate("settings.language.changed_title", "Язык изменен"))
            restart_message.setText(
                self._translate("settings.language.changed_message", f"Язык изменен на: {dialog.language_combo.currentText()}")
            )
            restart_message.setInformativeText(
                self._translate("settings.restart_required", "Некоторые изменения требуют перезапуска приложения.")
            )
            # Добавляем кнопки Restart Now и Restart Later
            restart_now_button = restart_message.addButton(
                self._translate("dialogs.preferences.restart_now", "Перезапустить сейчас"),
                QMessageBox.AcceptRole
            )
            restart_later_button = restart_message.addButton(
                self._translate("dialogs.preferences.restart_later", "Перезапустить позже"),
                QMessageBox.RejectRole
            )

            restart_message.exec()
            QApplication.processEvents()  # Добавляем обработку событий после сообщения

            # Если пользователь выбрал "Перезапустить сейчас", закрываем приложение
            if restart_message.clickedButton() == restart_now_button:
                self.close()
                # Если бы у нас был код для перезапуска приложения, мы бы вызвали его здесь

    def _show_preferences_dialog(self):
        """Показывает диалог настроек."""
        # Проверяем, существует ли уже диалог и видим ли он
        if self.preferences_dialog is not None and self.preferences_dialog.isVisible():
            # Если диалог уже открыт, активируем его и выходим
            self.preferences_dialog.activateWindow()
            self.preferences_dialog.raise_()
            return

        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle(self._translate("dialogs.preferences.title", "Настройки"))
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(400)

        # Добавляем обработку клавиши Escape для закрытия диалога
        dialog.keyPressEvent = lambda event: dialog.reject() if event.key() == Qt.Key_Escape else QDialog.keyPressEvent(dialog, event)

        layout = QVBoxLayout(dialog)

        # Создаем вкладки
        tabs = QTabWidget()

        # Вкладка общих настроек
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Группа внешнего вида
        appearance_group = QGroupBox(self._translate("settings.appearance", "Внешний вид"))
        appearance_layout = QFormLayout(appearance_group)

        # Выбор темы
        theme_label = QLabel(self._translate("settings.theme.label", "Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self._translate("settings.theme.light", "Светлая"), "light")
        self.theme_combo.addItem(self._translate("settings.theme.dark", "Тёмная"), "dark")

        # Устанавливаем текущую тему
        current_theme = "light"
        if "dark" in theme_manager.current_theme:
            current_theme = "dark"
            self.theme_combo.setCurrentIndex(1)

        appearance_layout.addRow(theme_label, self.theme_combo)

        # Выбор языка в настройках
        language_label = QLabel(self._translate("settings.language.label", "Язык:"))
        self.pref_language_combo = QComboBox()
        self.pref_language_combo.addItem("English", "en")
        self.pref_language_combo.addItem("Русский", "ru")

        # Устанавливаем текущий язык
        current_language = theme_manager.get_current_language()
        language_index = 0
        if "ru" in current_language:
            language_index = 1
        self.pref_language_combo.setCurrentIndex(language_index)

        appearance_layout.addRow(language_label, self.pref_language_combo)

        # Размер шрифта
        font_size_label = QLabel(self._translate("settings.font_size", "Font Size:"))
        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(8, 24)
        self.font_size_spinner.setValue(12)  # Предполагается, что у нас есть доступ к текущему размеру шрифта
        appearance_layout.addRow(font_size_label, self.font_size_spinner)

        # Шрифт
        font_family_label = QLabel(self._translate("settings.font_family", "Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Inter", "Arial", "Helvetica", "Times New Roman"])
        appearance_layout.addRow(font_family_label, self.font_family_combo)

        general_layout.addWidget(appearance_group)
        general_tab.setLayout(general_layout)

        # Вкладка расширенных настроек
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_group = QGroupBox(self._translate("settings.advanced", "Advanced"))
        advanced_inner_layout = QVBoxLayout(advanced_group)

        # Здесь могут быть дополнительные расширенные настройки
        advanced_layout.addWidget(advanced_group)
        advanced_tab.setLayout(advanced_layout)

        # Добавляем вкладки в виджет вкладок
        tabs.addTab(general_tab, self._translate("settings.general", "General"))
        tabs.addTab(advanced_tab, self._translate("settings.advanced", "Advanced"))

        layout.addWidget(tabs)

        # Кнопки с переводом
        button_box = QDialogButtonBox()
        apply_button = button_box.addButton(self._translate("dialogs.apply", "Применить"), QDialogButtonBox.ApplyRole)
        # Остальные кнопки
        ok_button = button_box.addButton(self._translate("dialogs.ok", "ОК"), QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton(self._translate("dialogs.cancel", "Отмена"), QDialogButtonBox.RejectRole)
        button_box.clicked.connect(lambda button: self._apply_preferences(dialog, False) if button == apply_button else None)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Подключаем сигнал закрытия диалога
        dialog.finished.connect(lambda result: self._on_preferences_dialog_finished(dialog, result))

        # Сохраняем ссылки на виджеты для обработчика
        dialog.theme_combo = self.theme_combo
        dialog.language_combo = self.pref_language_combo
        dialog.font_size_spinner = self.font_size_spinner
        dialog.font_family_combo = self.font_family_combo

        # Показываем диалог и запускаем цикл обработки событий
        dialog.open()
        # Обрабатываем ожидающие события Qt для решения проблемы с необходимостью двойного нажатия
        QApplication.processEvents()
        QApplication.processEvents()  # Двойной вызов для лучшей работы

        # Сохраняем ссылку на диалог
        self.preferences_dialog = dialog

    def _on_preferences_dialog_finished(self, dialog, result):
        """Обрабатывает результат закрытия диалога настроек."""
        # Удаляем ссылку на диалог
        self.preferences_dialog = None

        if result == QDialog.Accepted:
            self._apply_preferences(dialog)

    def _apply_preferences(self, dialog, show_message=True):
        """Применяет настройки из диалога."""
        try:
            selected_theme = dialog.theme_combo.currentData()
            selected_language = dialog.language_combo.currentData()
            font_size = dialog.font_size_spinner.value()

            # Сохраняем размер шрифта
            self.settings.setValue("font_size", font_size)

            # Формируем имя темы на основе выбранной темы и языка
            if selected_language == "ru":
                theme_name = f"{selected_theme}_ru"
            else:
                theme_name = f"{selected_theme}_en"

            # Применяем тему, если она отличается от текущей
            if theme_name != theme_manager.current_theme:
                try:
                    theme_manager.switch_theme(theme_name)
                except Exception as theme_error:
                    # Показываем локализованное сообщение об ошибке
                    error_msg = QMessageBox(self)
                    error_msg.setWindowTitle(self._translate("error.title", "Ошибка"))
                    error_msg.setText(self._translate("error.theme_change", "Ошибка при изменении темы"))
                    error_msg.setInformativeText(f"{str(theme_error)}")
                    error_msg.setIcon(QMessageBox.Critical)
                    error_msg.exec()
                    return

            # Применяем настройки шрифта
            if hasattr(dialog, 'font_family_combo') and dialog.font_family_combo:
                font_family = dialog.font_family_combo.currentText()
                self.settings.setValue("font_family", font_family)
                # Здесь можно добавить код для применения шрифта ко всему приложению

            # Показываем сообщение о успешном применении
            if show_message:
                QMessageBox.information(
                    self,
                    self._translate("settings.applied_title", "Настройки применены"),
                    self._translate("settings.applied_message", "Настройки успешно применены!")
                )
                QApplication.processEvents()  # Добавляем обработку событий после сообщения

        except Exception as e:
            # Показываем локализованное сообщение об ошибке
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle(self._translate("error.title", "Ошибка"))
            error_msg.setText(self._translate("error.settings_apply", "Ошибка при применении настроек"))
            error_msg.setInformativeText(f"{str(e)}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec()
            print(f"Error applying preferences: {e}")

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

    def _on_cut(self):
        """Обработчик действия 'Вырезать'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает вырезание
        if hasattr(focused_widget, 'cut') and callable(focused_widget.cut):
            focused_widget.cut()
        elif isinstance(focused_widget, QPlainTextEdit) or isinstance(focused_widget, QTextEdit):
            # Для текстовых редакторов, если нет стандартного метода cut()
            focused_widget.textCursor().removeSelectedText()

    def _on_copy(self):
        """Обработчик действия 'Копировать'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает копирование
        if hasattr(focused_widget, 'copy') and callable(focused_widget.copy):
            focused_widget.copy()

    def _on_paste(self):
        """Обработчик действия 'Вставить'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает вставку
        if hasattr(focused_widget, 'paste') and callable(focused_widget.paste):
            focused_widget.paste()

    def _on_undo(self):
        """Обработчик действия 'Отменить'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает отмену
        if hasattr(focused_widget, 'undo') and callable(focused_widget.undo):
            focused_widget.undo()

    def _on_redo(self):
        """Обработчик действия 'Повторить'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает повтор
        if hasattr(focused_widget, 'redo') and callable(focused_widget.redo):
            focused_widget.redo()

    def _on_select_all(self):
        """Обработчик действия 'Выделить всё'."""
        # Получаем активный виджет с фокусом
        focused_widget = QApplication.focusWidget()

        # Проверяем, что виджет существует и поддерживает выделение всего
        if hasattr(focused_widget, 'selectAll') and callable(focused_widget.selectAll):
            focused_widget.selectAll()

    def _open_file(self):
        """Открывает файл и отображает его в редакторе."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._translate("dialogs.file.open", "Open File"),
            "",
            "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                # Открываем файл
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Создаем новый редактор
                editor = CodeEditor(self)
                editor.setPlainText(content)

                # Получаем имя файла для вкладки
                file_name = os.path.basename(file_path)

                # Добавляем новую вкладку и делаем ее активной
                new_tab_index = self.central_tabs.addTab(editor, file_name)
                self.central_tabs.setCurrentIndex(new_tab_index)

                # Сохраняем путь к файлу в редакторе
                editor.file_path = file_path

                # Сбрасываем флаг модификации документа
                editor.document().setModified(False)

                # Обновляем статус
                self.status_label.setText(self._translate("status.file_opened", "File opened") + f": {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self._translate("dialogs.error.title", "Error"),
                    self._translate("dialogs.file.open_error", "Error opening file") + f": {e}"
                )

    def _save_file(self):
        """Сохраняет текущий файл."""
        # Получаем текущий редактор
        current_editor = self.central_tabs.currentWidget()
        if not current_editor:
            return

        # Проверяем, есть ли у редактора путь к файлу
        if hasattr(current_editor, 'file_path') and current_editor.file_path:
            file_path = current_editor.file_path
        else:
            # Если нет пути, вызываем диалог "Сохранить как..."
            return self._save_file_as()

        try:
            # Сохраняем содержимое в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(current_editor.toPlainText())

            # Сбрасываем флаг модификации документа
            current_editor.document().setModified(False)

            # Обновляем статус
            self.status_label.setText(self._translate("status.file_saved", "File saved") + f": {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                self._translate("dialogs.error.title", "Error"),
                self._translate("dialogs.file.save_error", "Error saving file") + f": {e}"
            )
            return False

    def _save_file_as(self):
        """Сохраняет текущий файл под новым именем."""
        # Получаем текущий редактор
        current_editor = self.central_tabs.currentWidget()
        if not current_editor:
            return False

        # Открываем диалог сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._translate("dialogs.file.save", "Save File"),
            "",
            "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                # Сохраняем содержимое в файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_editor.toPlainText())

                # Сохраняем путь к файлу в редакторе
                current_editor.file_path = file_path

                # Обновляем заголовок вкладки
                file_name = os.path.basename(file_path)
                self.central_tabs.setTabText(self.central_tabs.currentIndex(), file_name)

                # Сбрасываем флаг модификации документа
                current_editor.document().setModified(False)

                # Обновляем статус
                self.status_label.setText(self._translate("status.file_saved", "File saved") + f": {file_path}")
                return True
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self._translate("dialogs.error.title", "Error"),
                    self._translate("dialogs.file.save_error", "Error saving file") + f": {e}"
                )

        return False

    def _on_project_tree_double_clicked(self, index):
        """Обрабатывает двойной клик на элементе в проводнике проекта."""
        # Получаем путь к файлу
        file_path = self.fs_model.filePath(index)

        # Проверяем, что это файл, а не директория
        if os.path.isfile(file_path):
            # Открываем файл в редакторе
            self.open_file(file_path)
