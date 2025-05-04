import sys
import os  # Импортируем os для получения текущей директории
import asyncio
import threading
import subprocess  # Добавляем subprocess для Show in Explorer
import tempfile
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QDockWidget, QProgressBar,
    QMenu, QMenuBar, QApplication, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QFileDialog, QMessageBox,
    QToolButton, QStatusBar, QSplitter, QStyle, QStyleFactory,
    QDialog, QTextEdit, QLineEdit, QTreeView, QFileSystemModel,
    QInputDialog, QPlainTextEdit
)
from PySide6.QtCore import (
    Qt, QThread, QObject, Signal, QSettings, QModelIndex,
    QTimer, QDir, QUrl, QFileInfo, QThreadPool, QEvent
)
from PySide6.QtGui import (
    QIcon, QKeySequence, QFont, QFontDatabase, QDesktopServices,
    QPixmap, QColor, QTextCursor, QTextOption, QSyntaxHighlighter,
    QTextCharFormat, QStandardItemModel, QStandardItem, QTextDocument,
    QAction, QActionGroup
)

# Импортируем наш новый виджет чата
from .chat_widget import ChatWidget
from .code_editor import CodeEditor
from .terminal_widget import TerminalWidget  # Добавляем импорт терминала
from .project_explorer import ProjectExplorer
from .menu_manager import MenuManager
from .output_widget import OutputWidget
from .i18n.translator import JsonTranslationManager, tr
from .browser_tab_widget import MultiBrowserWidget
from .browser_widget import shutdown_cef

# Импортируем наши диалоги агентов
from .coding_agent_dialog import CodingAgentDialog
from .browser_agent_dialog import BrowserAgentDialog

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
from app.ui.emoji_dialog import EmojiDialog  # Импорт нового диалога эмодзи
from app.utils.theme_manager import ThemeManager

# Импорт менеджера иконок
from .icon_manager import get_icon, list_icons

# Импортируем ресурсы с иконками
try:
    import icons_rc
except ImportError:
    print("Warning: Icons resource file (icons_rc.py) not found.")

# Настройки для WebEngine перед импортом
import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

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
from .dock_title_bar import apply_custom_title_bar  # Импортируем наш новый модуль

# Импортируем новый импорт
from app.ui.settings_widget import SettingsWidget
from app.ui.theme_settings_dialog import ThemeSettingsDialog
from app.ui.coding_agent_dialog import CodingAgentDialog

# Импорт диалога настроек Reasoning
from .reasoning_settings_dialog import ReasoningSettingsDialog

# Инициализация логгера
logger = logging.getLogger(__name__)

class AgentWorker(QObject):
    """Worker для выполнения задач агента в отдельном потоке."""

    # Сигнал с результатом работы агента (может быть любым объектом)
    finished = Signal(object)
    # Сигнал для запуска задачи
    start_task = Signal(str)
    # Сигнал для отправки обновления состояния агента
    status_update = Signal(str)
    # Сигнал для отправки промежуточных результатов
    intermediate_result = Signal(str)

    def __init__(self, agent):
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
    """
    Главное окно приложения GopiAI.

    # Принципы интерфейса приложения GopiAI

## Основные принципы
- Максимальная дружелюбность к пользователю
- Отсутствие сложных терминов и настроек
- Описание всего простым языком, ясно и логично
- Интуитивно понятная навигация

## Структура интерфейса

### Левая часть — Файловый проводник:
- Закреплен у левого края, не может быть отсоединен
- Может изменять размер вправо, но всегда остается слева

### Правая часть — ИИ-чат:
- Закреплен у правого края, не может быть отсоединен
- Может изменять размер влево (становиться шире), но всегда остается справа

### Текстовый редактор:
- Текстовые вкладки имеют один цвет, а другие типы вкладок — другие цвета, должны быть визуально различимы

## Поведение остальных окон
Все окна (кроме файлового проводника и чата) могут:
- Становиться плавающими,
- менять размер
- размещаться в пространстве между проводником и чатом в виде вкладок

Логика вкладок должна оставаться согласованной во всех случаях.
    """
    def __init__(self, parent=None):
        """Инициализация главного окна приложения."""
        super().__init__(parent)

        # Устанавливаем название и размер окна
        self.setWindowTitle(tr("app.title", "GopiAI"))
        self.resize(1200, 800)

        # Получаем данные о текущей директории для проекта
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Инициализация менеджера локализации
        self.translation_manager = JsonTranslationManager.instance()

        # Инициализация менеджера тем
        self.theme_manager = ThemeManager.instance(QApplication.instance())

        # Подготавливаем мультипоточное окружение для воркеров
        self.thread_pool = QThreadPool()
        self.setObjectName("MainWindow")

        # Инициализация настроек
        self.settings = QSettings(tr("app.title", "GopiAI"), "UI")

        # Инициализация хранилища сессий
        self.sessions = {}

        # Запускаем агента ИИ
        # Метод ниже настраивает модель и токены, создает экземпляр агента
        self.agent = self._setup_agent()

        # Настраиваем менеджер тем
        theme_manager = ThemeManager.instance()

        # Инициализируем пользовательский интерфейс
        self._setup_ui()

        # Настраиваем обработку событий закрытия окна
        self.installEventFilter(self)

        # Подключаем остальные сигналы
        self.connect_agent_signals()

    def _setup_agent(self):
        """Настраивает агента ИИ и возвращает его экземпляр."""
        logger.info("Initializing agent (placeholder)")

        try:
            # Импортируем менеджер агентов
            from app.agent.agent_manager import AgentManager

            # Получаем экземпляр менеджера агентов
            agent_manager = AgentManager.instance()

            # Инициализируем агента с настройками по умолчанию
            agent = agent_manager.create_default_agent()

            return agent

        except ImportError as e:
            # Если модуль агента не найден, возвращаем None
            logger.warning(f"Agent module not found: {str(e)}")
            return None

        except Exception as e:
            # В случае любых других ошибок логируем и возвращаем None
            logger.error(f"Error initializing agent: {str(e)}")
            return None

    def _setup_ui(self):
        """Настраивает основной интерфейс окна."""
        # Настраиваем размер и заголовок
        self.resize(1280, 720)
        self.setWindowTitle(self._translate("app.title", "GopiAI"))

        # Загружаем действия
        self._create_actions()

        # Создаем строку состояния
        self._create_status_bar()

        # Настраиваем центральный виджет (редактор)
        self._setup_central_widget()

        # Создаем меню
        self._setup_menus()

        # Создаем доки (боковые панели)
        self._create_docks()

        # Добавляем возможность принимать перетаскиваемые файлы
        self.setAcceptDrops(True)

        # Применяем стили
        self._apply_styles()

    def _validate_ui_components(self):
        """Проверяет наличие всех необходимых компонентов UI и создает недостающие."""
        # Проверяем наличие центрального виджета
        if not hasattr(self, 'central_tabs') or self.central_tabs is None:
            logger.warning("Центральный виджет отсутствует, создаем заново")
            self._setup_central_widget()

        # Проверяем наличие панелей
        for dock_name in ['project_explorer_dock', 'chat_dock', 'terminal_dock', 'browser_dock']:
            if not hasattr(self, dock_name) or getattr(self, dock_name) is None:
                logger.warning(f"Док-виджет {dock_name} отсутствует, восстанавливаем доки")
                self._create_docks()
                break

        # Проверяем наличие меню тем
        if not hasattr(self, 'theme_menu') or self.theme_menu is None:
            logger.warning("Меню тем отсутствует, обновляем меню")
            self._create_menus()

        # Обновляем заголовки доков
        self._update_custom_title_bars()

        # Обновляем переводы интерфейса
        self.retranslateUi()

    def _load_fonts(self):
        """Загружаем современные шрифты для приложения."""
        try:
            font_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "fonts"
            )

            # Создаем директорию для шрифтов, если её нет
            os.makedirs(font_dir, exist_ok=True)

            # Проверяем наличие шрифтов
            inter_file = os.path.join(font_dir, "Inter", "Inter-Regular.ttf")
            jet_brains_file = os.path.join(font_dir, "JetBrainsMono-Regular.ttf")

            # Добавляем шрифты в систему QFontDatabase
            font_loaded = False

            # Загружаем шрифт Inter, если он есть
            font_id = QFontDatabase.addApplicationFont(inter_file)
            if font_id != -1:
                font_loaded = True
                print(f"Loaded font: {inter_file}")

            # Загружаем JetBrains Mono, если он есть
            font_id = QFontDatabase.addApplicationFont(jet_brains_file)
            if font_id != -1:
                font_loaded = True
                print(f"Loaded font: {jet_brains_file}")

            # Устанавливаем современный шрифт для всего приложения
            default_font = QFont("Inter", 10)
            QApplication.setFont(default_font)

            # Если ни один шрифт не был загружен, используем системный
            if not font_loaded:
                print("Using system fonts as fallback")

            print("Fonts applied to application")
        except Exception as e:
            print(f"Error loading fonts: {e}")

    def _load_styles(self, force_reload=False):
        """Загружает стили из текущей активной темы."""
        ############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за загрузку файлов стилей и применение их к приложению
        # Изменение логики может привести к поломке UI и нарушению работы приложения
        # Особенно важна обработка SVG иконок и корректное определение путей
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ############################################################################
        try:
            # Получаем путь к файлу темы
            style_path = ThemeManager.instance().get_theme_qss_path()

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

                    # Добавляем стили для разных типов вкладок
                    # Определяем, используется ли темная тема
                    is_dark_theme = "dark" in ThemeManager.instance().get_current_theme()

                    # Выбираем стили в зависимости от темы
                    if is_dark_theme:
                        tab_styles = """
                        /* Стили для различных типов вкладок - темная тема */

                        /* Стиль для текстовых вкладок - базовый */
                        QTabWidget::tab-bar {
                            alignment: left;
                        }

                        QTabBar::tab {
                            background-color: #333333;
                            border: 1px solid #555555;
                            border-bottom-color: transparent;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px;
                            min-width: 8ex;
                            padding: 6px 10px;
                            margin-right: 2px;
                            color: #cccccc;
                        }

                        QTabBar::tab:selected {
                            background-color: #404040;
                            border-bottom-color: #404040;
                            font-weight: bold;
                            color: #ffffff;
                        }

                        QTabBar::tab:hover:!selected {
                            background-color: #3a3a3a;
                        }

                        /* Стиль для вкладок терминала - темно-зеленые */
                        #TerminalDock QTabBar::tab {
                            background-color: #2a3a2a;
                            border: 1px solid #384838;
                            color: #a0c0a0;
                        }

                        #TerminalDock QTabBar::tab:selected {
                            background-color: #304030;
                            border-bottom-color: #304030;
                            color: #c0ffc0;
                        }

                        #TerminalDock QTabBar::tab:hover:!selected {
                            background-color: #2c382c;
                        }

                        /* Стиль для вкладок браузера - темно-синие */
                        #BrowserDock QTabBar::tab {
                            background-color: #2a3a4a;
                            border: 1px solid #384858;
                            color: #a0c0e0;
                        }

                        #BrowserDock QTabBar::tab:selected {
                            background-color: #304050;
                            border-bottom-color: #304050;
                            color: #c0e0ff;
                        }

                        #BrowserDock QTabBar::tab:hover:!selected {
                            background-color: #2c3842;
                        }

                        /* Стиль для кастомных заголовков QDockWidget */
                        QDockWidget {
                            titlebar-close-icon: url(close.png);
                            titlebar-normal-icon: url(undock.png);
                        }

                        QDockWidget::title {
                            text-align: left;
                            background: #333333;
                            padding-left: 5px;
                            height: 24px;
                            color: #ffffff;
                        }

                        QDockWidget::close-button, QDockWidget::float-button {
                            border: none;
                            border-radius: 2px;
                            background: transparent;
                        }

                        QDockWidget::close-button:hover, QDockWidget::float-button:hover {
                            background: rgba(255, 80, 80, 0.3);
                        }

                        QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
                            background: rgba(255, 80, 80, 0.5);
                        }

                        /* Стили для заголовков доков */
                        DockTitleBar {
                            background-color: #333333;
                            border-bottom: 1px solid #555555;
                        }

                        DockTitleBar QLabel {
                            font-weight: bold;
                            color: #ffffff;
                        }

                        DockTitleBar QPushButton {
                            background-color: transparent;
                            border: none;
                            border-radius: 2px;
                            font-size: 10px;
                            color: #cccccc;
                        }

                        DockTitleBar QPushButton:hover {
                            background-color: rgba(255, 255, 255, 0.2);
                        }

                        DockTitleBar QPushButton[text="❌"]:hover {
                            background-color: rgba(255, 80, 80, 0.3);
                        }
                        """
                    else:
                        tab_styles = """
                        /* Стили для различных типов вкладок - светлая тема */

                        /* Стиль для текстовых вкладок - базовый */
                        QTabWidget::tab-bar {
                            alignment: left;
                        }

                        QTabBar::tab {
                            background-color: #f0f0f0;
                            border: 1px solid #c0c0c0;
                            border-bottom-color: transparent;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px;
                            min-width: 8ex;
                            padding: 6px 10px;
                            margin-right: 2px;
                            color: #505050;
                        }

                        QTabBar::tab:selected {
                            background-color: #ffffff;
                            border-bottom-color: #ffffff;
                            font-weight: bold;
                            color: #303030;
                        }

                        QTabBar::tab:hover:!selected {
                            background-color: #e0e0e0;
                        }

                        /* Стиль для вкладок терминала - серо-зеленые */
                        #TerminalDock QTabBar::tab {
                            background-color: #e0f0e0;
                            border: 1px solid #c0d0c0;
                            color: #305030;
                        }

                        #TerminalDock QTabBar::tab:selected {
                            background-color: #f0fff0;
                            border-bottom-color: #f0fff0;
                            color: #203020;
                        }

                        #TerminalDock QTabBar::tab:hover:!selected {
                            background-color: #e8f8e8;
                        }

                        /* Стиль для вкладок браузера - серо-голубые */
                        #BrowserDock QTabBar::tab {
                            background-color: #e0e8f0;
                            border: 1px solid #c0c8d0;
                            color: #304060;
                        }

                        #BrowserDock QTabBar::tab:selected {
                            background-color: #f0f8ff;
                            border-bottom-color: #f0f8ff;
                            color: #203050;
                        }

                        #BrowserDock QTabBar::tab:hover:!selected {
                            background-color: #e8f0f8;
                        }

                        /* Стиль для кастомных заголовков QDockWidget */
                        QDockWidget {
                            titlebar-close-icon: url(close.png);
                            titlebar-normal-icon: url(undock.png);
                        }

                        QDockWidget::title {
                            text-align: left;
                            background: #f0f0f0;
                            padding-left: 5px;
                            height: 24px;
                        }

                        QDockWidget::close-button, QDockWidget::float-button {
                            border: none;
                            border-radius: 2px;
                            background: transparent;
                        }

                        QDockWidget::close-button:hover, QDockWidget::float-button:hover {
                            background: rgba(255, 0, 0, 0.1);
                        }

                        QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
                            background: rgba(255, 0, 0, 0.3);
                        }

                        /* Стили для заголовков доков */
                        DockTitleBar {
                            background-color: #f0f0f0;
                            border-bottom: 1px solid #cccccc;
                        }

                        DockTitleBar QLabel {
                            font-weight: bold;
                            color: #333333;
                        }

                        DockTitleBar QPushButton {
                            background-color: transparent;
                            border: none;
                            border-radius: 2px;
                            font-size: 10px;
                        }

                        DockTitleBar QPushButton:hover {
                            background-color: rgba(0, 0, 0, 0.1);
                        }

                        DockTitleBar QPushButton[text="❌"]:hover {
                            background-color: rgba(255, 0, 0, 0.2);
                        }
                        """

                    # Добавляем стили для вкладок к основному стилю
                    style += tab_styles

                    self.setStyleSheet(style)
                    print(f"Стили загружены из {style_path}")
            else:
                print(f"Файл стиля не найден: {style_path}")
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")

    def _translate(self, key, default_text=""):
        """Возвращает перевод для указанного ключа."""
        from app.ui.i18n.translator import tr
        return tr(key, default_text)

    def _create_actions(self):
        """Создает все действия для меню и панелей инструментов."""
        # --- File Menu Actions ---
        # Создание нового файла
        self.new_file_action = QAction(
            get_icon("file_new"), self._translate("menu.new", ""), self
        )
        self.new_file_action.setShortcut(QKeySequence.New)
        self.new_file_action.setStatusTip(self._translate("menu.new.tooltip", ""))

        # Открытие существующего файла
        self.open_file_action = QAction(
            get_icon("folder_open"), self._translate("menu.open_file", ""), self
        )
        self.open_file_action.setShortcut(QKeySequence.Open)
        self.open_file_action.setStatusTip(self._translate("menu.open_file.tooltip", ""))

        # Сохранение текущего файла
        self.save_file_action = QAction(
            get_icon("save"), self._translate("menu.save", ""), self
        )
        self.save_file_action.setShortcut(QKeySequence.Save)
        self.save_file_action.setStatusTip(self._translate("menu.save.tooltip", ""))

        # Сохранение файла с новым именем
        self.save_as_action = QAction(
            get_icon("save_as"), self._translate("menu.save_as", ""), self
        )
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.setStatusTip(self._translate("menu.save_as.tooltip", ""))

        # Выход из приложения
        self.exit_action = QAction(
            get_icon("exit"), self._translate("menu.exit", ""), self
        )
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.setStatusTip(self._translate("menu.exit.tooltip", ""))

        # --- Edit Menu Actions ---
        # Вырезать
        self.cut_action = QAction(
            get_icon("cut"), self._translate("menu.cut", ""), self
        )
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.setStatusTip(self._translate("menu.cut.tooltip", ""))

        # Копировать
        self.copy_action = QAction(
            get_icon("copy"), self._translate("menu.copy", ""), self
        )
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setStatusTip(self._translate("menu.copy.tooltip", ""))

        # Вставить
        self.paste_action = QAction(
            get_icon("paste"), self._translate("menu.paste", ""), self
        )
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.setStatusTip(self._translate("menu.paste.tooltip", ""))

        # Отменить
        self.undo_action = QAction(
            get_icon("undo"), self._translate("menu.undo", ""), self
        )
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setStatusTip(self._translate("menu.undo.tooltip", ""))

        # Повторить
        self.redo_action = QAction(
            get_icon("redo"), self._translate("menu.redo", ""), self
        )
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setStatusTip(self._translate("menu.redo.tooltip", ""))

        # Выделить все
        self.select_all_action = QAction(
            get_icon("select_all"), self._translate("menu.select_all", ""), self
        )
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.setStatusTip(self._translate("menu.select_all.tooltip", ""))

        # Emoji
        self.emoji_action = QAction(
            get_icon("emoji"), self._translate("menu.emoji", ""), self
        )
        self.emoji_action.setStatusTip(self._translate("menu.emoji.tooltip", ""))

        # --- View Menu Actions ---
        # Терминал
        self.toggle_terminal_action = QAction(
            get_icon("terminal"), self._translate("dock.terminal.toggle", ""), self
        )
        self.toggle_terminal_action.setCheckable(True)
        self.toggle_terminal_action.setStatusTip(self._translate("dock.terminal.toggle.tooltip", ""))

        # Проводник проекта
        self.toggle_project_explorer_action = QAction(
            get_icon("folder"), self._translate("dock.project_explorer.toggle", ""), self
        )
        self.toggle_project_explorer_action.setCheckable(True)
        self.toggle_project_explorer_action.setStatusTip(self._translate("dock.project_explorer.toggle.tooltip", ""))

        # Чат
        self.toggle_chat_action = QAction(
            get_icon("chat"), self._translate("dock.chat.toggle", ""), self
        )
        self.toggle_chat_action.setCheckable(True)
        self.toggle_chat_action.setStatusTip(self._translate("dock.chat.toggle.tooltip", ""))

        # Браузер
        self.toggle_browser_action = QAction(
            get_icon("browser"), self._translate("dock.browser.toggle", ""), self
        )
        self.toggle_browser_action.setCheckable(True)
        self.toggle_browser_action.setStatusTip(self._translate("dock.browser.toggle.tooltip", ""))

        # Сброс расположения панелей
        self.reset_layout_action = QAction(
            get_icon("reset"), self._translate("menu.reset_layout", ""), self
        )
        self.reset_layout_action.setStatusTip(self._translate("menu.reset_layout.tooltip", ""))

        # Сброс интерфейса
        self.reset_ui_action = QAction(
            get_icon("refresh"), self._translate("menu.reset_ui", ""), self
        )
        self.reset_ui_action.setStatusTip(self._translate("menu.reset_ui.tooltip", ""))

        # Открыть URL
        self.open_url_action = QAction(
            get_icon("link"), self._translate("menu.tools.open_url", ""), self
        )
        self.open_url_action.setStatusTip(self._translate("menu.tools.open_url.tooltip", ""))

        # --- Tools Menu Actions ---
        # Настройка агента
        self.configure_agent_action = QAction(
            get_icon("settings"), self._translate("menu.configure_agent", ""), self
        )
        self.configure_agent_action.setStatusTip(self._translate("menu.configure_agent.tooltip", ""))

        # Визуализация потока
        self.view_flow_action = QAction(
            get_icon("flow"), self._translate("menu.view_flow", ""), self
        )
        self.view_flow_action.setStatusTip(self._translate("menu.view_flow.tooltip", ""))

        # Настройки
        self.preferences_action = QAction(
            get_icon("preferences"), self._translate("menu.preferences", ""), self
        )
        self.preferences_action.setStatusTip(self._translate("menu.preferences.tooltip", ""))

        # --- Help Menu Actions ---
        # О программе
        self.about_action = QAction(
            get_icon("info"), self._translate("menu.about", ""), self
        )
        self.about_action.setStatusTip(self._translate("menu.about.tooltip", ""))

        # Документация
        self.documentation_action = QAction(
            get_icon("documentation"), self._translate("menu.documentation", ""), self
        )
        self.documentation_action.setStatusTip(self._translate("menu.documentation.tooltip", ""))

        # Инструменты
        tool_callbacks = {
            "web_browser": self._toggle_browser,
            "browsing_agent": self._open_browsing_agent,
            "coding_agent": self._open_coding_agent,
            "flow_visualization": self._show_flow_visualization,
            "configure_agent": self._on_configure_agent,
            "preferences": self._show_preferences_dialog
        }

        # ... остальной существующий код ...

    def _open_coding_agent(self):
        """Открывает диалог с агентом кодирования."""
        try:
            # Создаем диалог
            dialog = CodingAgentDialog(self, self.theme_manager)

            # Отображаем его как немодальный диалог
            dialog.show()

            # Добавляем информацию в статусную строку
            self.statusBar().showMessage(tr("main.coding_agent_opened", "Coding Agent opened"), 3000)
        except Exception as e:
            logger.error(f"Ошибка при открытии Coding Agent: {e}")
            QMessageBox.critical(
                self,
                tr("dialogs.error", "Error"),
                tr("dialogs.coding_agent_error", "Error opening Coding Agent: {error}").format(error=str(e))
            )

    def _open_browsing_agent(self):
        """Открывает диалог с агентом браузера."""
        try:
            # Создаем диалог
            dialog = BrowserAgentDialog(self, self.theme_manager)

            # Отображаем его как немодальный диалог
            dialog.show()

            # Добавляем информацию в статусную строку
            self.statusBar().showMessage(tr("main.browsing_agent_opened", "Browsing Agent opened"), 3000)
        except Exception as e:
            logger.error(f"Ошибка при открытии Browsing Agent: {e}")
            QMessageBox.critical(
                self,
                tr("dialogs.error", "Error"),
                tr("dialogs.browsing_agent_error", "Error opening Browsing Agent: {error}").format(error=str(e))
            )

    def _setup_menus(self):
        """Настраивает меню приложения."""
        try:
            # Создаем менеджер меню
            self.menu_manager = MenuManager(self)

            # Устанавливаем меню
            self.setMenuBar(self.menu_manager.menubar)

            # Подключаем сигналы от меню
            self.menu_manager.theme_changed.connect(self._on_theme_changed)
            self.menu_manager.language_changed.connect(self._on_language_changed_event)

        except Exception as e:
            logger.error(f"Error setting up menus: {str(e)}")

    def _create_menus(self):
        """Создает меню приложения - устаревший метод."""
        pass  # Теперь меню создается в MenuManager

    def changeEvent(self, event):
        """Обрабатывает события изменения в приложении, такие как смена языка."""
        try:
            # Вызываем метод родительского класса
            super().changeEvent(event)

            # Если это событие смены языка
            if event.type() == QEvent.LanguageChange:
                # Обновляем переводы элементов интерфейса
                self.retranslateUi()
                # Обновляем меню
                if hasattr(self, 'menu_manager'):
                    self.menu_manager.update_translations()
        except Exception as e:
            logger.error(f"Ошибка при обработке события изменения: {str(e)}")

        # Возвращаем управление системе
        return False

    def _toggle_terminal(self, checked=None):
        """Переключает видимость панели терминала."""
        if not hasattr(self, 'terminal_dock'):
            print("Терминал не инициализирован")
            return

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

    def _on_dock_visibility_changed(self, visible):
        """Обрабатывает изменение видимости док-панелей."""
        # Обновляем состояние меню View
        self._update_view_menu()

    def _update_view_menu(self):
        """Обновляет состояние пунктов меню View в зависимости от видимости панелей."""
        # Обновляем состояние чекбоксов меню
        if hasattr(self, 'toggle_project_explorer_action'):
            self.toggle_project_explorer_action.setChecked(
                hasattr(self, 'project_explorer_dock') and self.project_explorer_dock.isVisible()
            )

        if hasattr(self, 'toggle_chat_action'):
            self.toggle_chat_action.setChecked(
                hasattr(self, 'chat_dock') and self.chat_dock.isVisible()
            )

        if hasattr(self, 'toggle_terminal_action'):
            self.toggle_terminal_action.setChecked(
                hasattr(self, 'terminal_dock') and self.terminal_dock.isVisible()
            )

        if hasattr(self, 'toggle_browser_action'):
            self.toggle_browser_action.setChecked(
                hasattr(self, 'browser_dock') and self.browser_dock.isVisible()
            )

    def _on_file_double_clicked(self, file_path):
        """Обрабатывает двойной клик на файле в проводнике проекта."""
        # Проверяем существование файла
        if not os.path.isfile(file_path):
            return

        # Здесь должен быть код для открытия файла в редакторе
        print(f"Открываем файл: {file_path}")

        # В будущем здесь будет вызов метода для открытия файла в редакторе
        # self._open_file_in_editor(file_path)

    def _connect_ui_signals(self):
        """Подключает сигналы UI-элементов к соответствующим слотам (методам)."""
        # --- Центральный виджет ---
        # Сигналы для вкладок
        if hasattr(self, 'central_tabs'):
            self.central_tabs.tabCloseRequested.connect(self._close_tab)
            self.central_tabs.currentChanged.connect(self._on_tab_changed)
            # Контекстное меню вкладок
            self.central_tabs.setContextMenuPolicy(Qt.CustomContextMenu)
            self.central_tabs.customContextMenuRequested.connect(self._show_tab_context_menu)

        # --- Проводник проектов ---
        # Двойной клик по элементу в проводнике
        if hasattr(self, 'project_explorer'):
            self.project_explorer.tree_view.doubleClicked.connect(self._on_project_tree_double_clicked)
            # Контекстное меню в проводнике
            self.project_explorer.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
            self.project_explorer.tree_view.customContextMenuRequested.connect(self._show_project_tree_context_menu)

        # --- Сигналы чата ---
        if hasattr(self, 'chat_widget'):
            # Сигнал отправки сообщения пользователем
            self.chat_widget.message_sent.connect(self._handle_user_message)

            # При наличии ChatWidget и TerminalWidget, настраиваем также сигналы Terminate
            if hasattr(self, 'terminal_widget') and hasattr(self.terminal_widget, 'command_executed'):
                self.terminal_widget.command_executed.connect(lambda cmd, out:
                    self.chat_widget.log_event(f"Command executed: {cmd}\n{out}")
                )

        # --- Сигналы для пунктов меню и панелей инструментов ---
        # Файл
        self.new_file_action.triggered.connect(self._new_file)
        self.open_file_action.triggered.connect(self._open_file)
        self.save_file_action.triggered.connect(self._save_file)
        self.save_as_action.triggered.connect(self._save_file_as)
        self.exit_action.triggered.connect(self.close)

        # Правка
        self.cut_action.triggered.connect(self._on_cut)
        self.copy_action.triggered.connect(self._on_copy)
        self.paste_action.triggered.connect(self._on_paste)
        self.undo_action.triggered.connect(self._on_undo)
        self.redo_action.triggered.connect(self._on_redo)
        self.select_all_action.triggered.connect(self._on_select_all)

        # Если есть действие эмодзи, подключаем его
        if hasattr(self, 'emoji_action'):
            self.emoji_action.triggered.connect(self._show_emoji_dialog)

        # Вид
        self.toggle_project_explorer_action.triggered.connect(self._toggle_project_explorer)
        self.toggle_chat_action.triggered.connect(self._toggle_chat)
        self.toggle_terminal_action.triggered.connect(self._toggle_terminal)
        if hasattr(self, 'toggle_browser_action'):
            self.toggle_browser_action.triggered.connect(self._toggle_browser)

        # Сброс layout и UI
        self.reset_layout_action.triggered.connect(self.reset_dock_layout)
        self.reset_ui_action.triggered.connect(self.reset_ui)

        # Инструменты
        self.configure_agent_action.triggered.connect(self._on_configure_agent)
        if hasattr(self, 'open_url_action'):
            self.open_url_action.triggered.connect(self._open_url_in_browser)
        if hasattr(self, 'view_flow_action'):
            self.view_flow_action.triggered.connect(self._show_flow_visualization)
        self.preferences_action.triggered.connect(self._show_preferences_dialog)

        # Справка
        self.about_action.triggered.connect(self._on_about)
        self.documentation_action.triggered.connect(self._on_documentation)

        # --- Изменение видимости доков ---
        # При изменении видимости доков обновляем состояние меню
        for dock in [self.project_explorer_dock, self.chat_dock, self.terminal_dock]:
            dock.visibilityChanged.connect(self._on_dock_visibility_changed)

        if hasattr(self, 'browser_dock'):
            self.browser_dock.visibilityChanged.connect(self._on_dock_visibility_changed)

    def connect_agent_signals(self):
        """Подключает сигналы агента к интерфейсу."""
        try:
            if not self.agent:
                logger.warning("Agent is not initialized, cannot connect signals")
                return

            # В будущем здесь будет подключение сигналов агента
            logger.info("Agent signals connected")
        except Exception as e:
            logger.error(f"Error connecting agent signals: {str(e)}")

    def update_agent_status(self, status: str):
        """Обновляет статус агента в строке состояния и логирует изменения."""
        try:
            if hasattr(self, 'agent_status_label'):
                self.agent_status_label.setText(status)
            else:
                print(f"[{APP_NAME}] Статус агента: {status}")
        except Exception as e:
            print(f"[{APP_NAME}] Ошибка обновления статуса агента: {e}")

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

    def _on_project_tree_double_clicked(self, index):
        """Обрабатывает двойной клик по элементу в проводнике проектов."""
        try:
            if not hasattr(self, 'project_explorer'):
                return

            # Получаем путь к файлу из модели данных
            file_path = self.project_explorer.tree_model.filePath(index)
            if not file_path:
                return

            # Проверяем, является ли элемент директорией
            file_info = QFileInfo(file_path)
            if file_info.isDir():
                # Если директория, просто открываем/закрываем её в дереве
                self.project_explorer.tree_view.setExpanded(index, not self.project_explorer.tree_view.isExpanded(index))
            else:
                # Если файл, открываем его в редакторе
                self._open_file(file_path)
        except Exception as e:
            logger.error(f"Error handling project tree double click: {str(e)}")

    def _on_tab_changed(self, index):
        """Обработчик смены активной вкладки."""
        # Обновляем заголовок окна
        if index != -1:
            tab_widget = self.central_tabs.widget(index)
            if hasattr(tab_widget, 'file_path') and tab_widget.file_path:
                file_name = os.path.basename(tab_widget.file_path)
                self.setWindowTitle(f"{file_name} - {APP_NAME}")
            else:
                self.setWindowTitle(APP_NAME)

        # Обновляем статус активной вкладки
        self._update_tab_status(index)

    def _update_tab_status(self, index):
        """Обновляет статусную строку в зависимости от активной вкладки."""
        if index == -1 or not hasattr(self, 'status_bar'):
            return

        tab_widget = self.central_tabs.widget(index)

        # Обновляем информацию о файле в статусной строке
        if hasattr(tab_widget, 'file_path') and tab_widget.file_path:
            file_path = tab_widget.file_path
            file_info = QFileInfo(file_path)

            # Показываем имя файла и его размер
            file_size = self._format_file_size(file_info.size())
            status_text = f"{file_info.fileName()} | {file_size}"

            # Добавляем информацию о типе файла
            file_type = self._get_file_type(file_path)
            if file_type:
                status_text += f" | {file_type}"

            # Устанавливаем информацию в статусной строке
            if hasattr(self, 'file_info_label'):
                self.file_info_label.setText(status_text)

    def _format_file_size(self, size_in_bytes):
        """Форматирует размер файла в читаемый вид."""
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        elif size_in_bytes < 1024 * 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _get_file_type(self, file_path):
        """Определяет тип файла по расширению."""
        ext = os.path.splitext(file_path)[1].lower()

        file_types = {
            '.py': tr('file_types.python', 'Python Script'),
            '.js': tr('file_types.javascript', 'JavaScript'),
            '.html': tr('file_types.html', 'HTML'),
            '.css': tr('file_types.css', 'CSS'),
            '.json': tr('file_types.json', 'JSON'),
            '.md': tr('file_types.markdown', 'Markdown'),
            '.txt': tr('file_types.text', 'Text File'),
            '.xml': tr('file_types.xml', 'XML'),
            '.yaml': tr('file_types.yaml', 'YAML'),
            '.yml': tr('file_types.yaml', 'YAML'),
            '.csv': tr('file_types.csv', 'CSV'),
            '.sql': tr('file_types.sql', 'SQL')
        }

        return file_types.get(ext, None)

    def _show_project_tree_context_menu(self, position):
        """Показывает контекстное меню для элементов в проводнике проектов."""
        try:
            if not hasattr(self, 'project_explorer'):
                return

            # Получаем индекс элемента под курсором
            index = self.project_explorer.tree_view.indexAt(position)
            if not index.isValid():
                return

            # Получаем путь к файлу/директории
            file_path = self.project_explorer.tree_model.filePath(index)
            if not file_path:
                return

            # Создаем контекстное меню
            menu = QMenu(self)

            # Получаем информацию о файле
            file_info = QFileInfo(file_path)

            if file_info.isDir():
                # Опции для директорий
                open_in_explorer = QAction(self._translate("context_menu.open_in_explorer", "Открыть в проводнике"), self)
                open_in_explorer.triggered.connect(lambda: self._open_in_explorer(file_path))
                menu.addAction(open_in_explorer)
            else:
                # Опции для файлов
                open_file = QAction(self._translate("context_menu.open", "Открыть"), self)
                open_file.triggered.connect(lambda: self._open_file(file_path))
                menu.addAction(open_file)

                # Показ в проводнике
                show_in_explorer = QAction(self._translate("context_menu.show_in_explorer", "Показать в проводнике"), self)
                show_in_explorer.triggered.connect(lambda: self._open_in_explorer(os.path.dirname(file_path)))
                menu.addAction(show_in_explorer)

            # Показываем меню
            menu.exec_(self.project_explorer.tree_view.viewport().mapToGlobal(position))
        except Exception as e:
            logger.error(f"Error showing project tree context menu: {str(e)}")

    def _open_in_explorer(self, path):
        """Открывает указанный путь в проводнике операционной системы."""
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', path])
            else:  # Linux
                subprocess.call(['xdg-open', path])
        except Exception as e:
            logger.error(f"Error opening path in explorer: {str(e)}")

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за обновление переводов интерфейса при смене языка
    # Изменение логики может привести к неправильным переводам или отсутствию локализации
    # Важны правильная последовательность вызовов и синхронизация с менеджером тем
    # Тесно связан с методами _translate и _on_theme_changed
    ############################################################################
    def _update_ui_translations(self):
        """Обновляет переводы всех текстов интерфейса."""
        # Устанавливаем флаг, что идет процесс обновления переводов, чтобы избежать рекурсивных вызовов
        if hasattr(self, '_is_updating_translations') and self._is_updating_translations:
            return

        self._is_updating_translations = True

        try:
            # Обновление заголовка окна
            self.setWindowTitle(self._translate("main_window", ""))

            # Обновление действий меню File
            if hasattr(self, 'new_file_action'):
                self.new_file_action.setText(self._translate("menu.new", ""))
                self.new_file_action.setStatusTip(self._translate("menu.new.tooltip", ""))

            if hasattr(self, 'open_file_action'):
                self.open_file_action.setText(self._translate("menu.open_file", ""))
                self.open_file_action.setStatusTip(self._translate("menu.open_file.tooltip", ""))

            if hasattr(self, 'save_file_action'):
                self.save_file_action.setText(self._translate("menu.save", ""))
                self.save_file_action.setStatusTip(self._translate("menu.save.tooltip", ""))

            if hasattr(self, 'save_as_action'):
                self.save_as_action.setText(self._translate("menu.save_as", ""))
                self.save_as_action.setStatusTip(self._translate("menu.save_as.tooltip", ""))

            if hasattr(self, 'exit_action'):
                self.exit_action.setText(self._translate("menu.exit", ""))
                self.exit_action.setStatusTip(self._translate("menu.exit.tooltip", ""))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню Edit
            if hasattr(self, 'cut_action'):
                self.cut_action.setText(self._translate("menu.cut", ""))
                self.cut_action.setStatusTip(self._translate("menu.cut.tooltip", ""))

            if hasattr(self, 'copy_action'):
                self.copy_action.setText(self._translate("menu.copy", ""))
                self.copy_action.setStatusTip(self._translate("menu.copy.tooltip", ""))

            if hasattr(self, 'paste_action'):
                self.paste_action.setText(self._translate("menu.paste", ""))
                self.paste_action.setStatusTip(self._translate("menu.paste.tooltip", ""))

            if hasattr(self, 'emoji_action'):
                self.emoji_action.setText(self._translate("menu.insert_emoji", ""))
                self.emoji_action.setStatusTip(self._translate("menu.insert_emoji.tooltip", ""))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню View
            if hasattr(self, 'toggle_terminal_action'):
                self.toggle_terminal_action.setText(self._translate("dock.terminal.toggle", ""))

            if hasattr(self, 'toggle_project_explorer_action'):
                self.toggle_project_explorer_action.setText(self._translate("dock.project_explorer.toggle", ""))

            if hasattr(self, 'toggle_chat_action'):
                self.toggle_chat_action.setText(self._translate("dock.chat.toggle", ""))

            # Обновление действий меню Tools
            if hasattr(self, 'configure_agent_action'):
                self.configure_agent_action.setText(self._translate("menu.configure_agent", ""))
                self.configure_agent_action.setStatusTip(self._translate("menu.configure_agent.tooltip", ""))

            if hasattr(self, 'view_flow_action'):
                self.view_flow_action.setText(self._translate("menu.view_flow", ""))
                self.view_flow_action.setStatusTip(self._translate("menu.view_flow.tooltip", ""))

            if hasattr(self, 'preferences_action'):
                self.preferences_action.setText(self._translate("menu.preferences", ""))
                self.preferences_action.setStatusTip(self._translate("menu.preferences.tooltip", ""))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление действий меню Help
            if hasattr(self, 'about_action'):
                self.about_action.setText(self._translate("menu.about", ""))

            if hasattr(self, 'documentation_action'):
                self.documentation_action.setText(self._translate("menu.documentation", ""))

            # Обновление меню
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(self._translate("menu.file", ""))

            if hasattr(self, 'edit_menu'):
                self.edit_menu.setTitle(self._translate("menu.edit", ""))

            if hasattr(self, 'view_menu'):
                self.view_menu.setTitle(self._translate("menu.view", ""))

            if hasattr(self, 'tools_menu'):
                self.tools_menu.setTitle(self._translate("menu.tools", ""))

            if hasattr(self, 'help_menu'):
                self.help_menu.setTitle(self._translate("menu.help", ""))

            if hasattr(self, 'theme_menu'):
                self.theme_menu.setTitle(self._translate("menu.theme", ""))

            # Обработка событий, чтобы интерфейс мог реагировать во время обновления
            QApplication.processEvents()

            # Обновление имен доков
            if hasattr(self, 'terminal_dock'):
                self.terminal_dock.setWindowTitle(self._translate("dock.terminal", ""))

            if hasattr(self, 'project_explorer_dock'):
                self.project_explorer_dock.setWindowTitle(self._translate("dock.project_explorer", ""))

            if hasattr(self, 'chat_dock'):
                self.chat_dock.setWindowTitle(self._translate("dock.chat", ""))

            # Обновляем текст статус-бара
            if hasattr(self, 'status_label'):
                self.status_label.setText(self._translate("status.ready", ""))

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
        # Этот метод настраивает центральный виджет - текстовый редактор с вкладками.
        # Важные принципы:
        # - Текстовый редактор расположен в центре и сверху
        # - Использует вкладки для удобного переключения между файлами
        # - Текстовые вкладки должны визуально отличаться от других типов вкладок
        # - Интерфейс должен быть интуитивно понятным и удобным для пользователя

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

    def _show_tab_context_menu(self, pos):
        """Показывает контекстное меню для вкладок."""
        index = self.central_tabs.tabBar().tabAt(pos)
        if index < 0:
            return

        # Создаем контекстное меню
        menu = QMenu(self)

        # Действие "Закрыть"
        close_action = QAction(self._translate("dialogs.close", "Close"), self)
        close_action.triggered.connect(lambda: self._close_tab(index))
        menu.addAction(close_action)

        # Действие "Закрыть все"
        close_all_action = QAction(self._translate("dialogs.close_all", "Close All Tabs"), self)
        close_all_action.triggered.connect(self._close_all_tabs)
        menu.addAction(close_all_action)

        # Действие "Закрыть другие"
        close_others_action = QAction(self._translate("dialogs.close_others", "Close Other Tabs"), self)
        close_others_action.triggered.connect(lambda: self._close_other_tabs(index))
        menu.addAction(close_others_action)

        # Показываем меню в позиции курсора
        menu.exec_(self.central_tabs.tabBar().mapToGlobal(pos))

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
        count = self.central_tabs.count()
        for i in range(count - 1, -1, -1):
            self._close_tab(i)

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

    def _update_themes_menu(self):
        """Обновляет меню выбора тем на основе доступных тем."""
        # Очищаем существующее меню тем
        if hasattr(self, 'theme_menu'):
            self.theme_menu.clear()

            # Создаем группу для взаимоисключающих действий выбора темы
            if hasattr(self, 'theme_action_group'):
                if self.theme_action_group is not None:
                    self.theme_action_group.deleteLater()

            self.theme_action_group = QActionGroup(self)

            # Получаем список доступных тем
            themes = ThemeManager.instance().get_available_visual_themes()
            current_theme = ThemeManager.instance().get_current_visual_theme()

            # Создаем подменю для тем интерфейса
            for theme in themes:
                theme_display_name = ThemeManager.instance().get_theme_display_name(theme)
                theme_action = QAction(theme_display_name, self, checkable=True)
                theme_action.setData(theme)
                if theme == current_theme:
                    theme_action.setChecked(True)
                theme_action.triggered.connect(lambda checked, t=theme: self._on_theme_changed(t))
                self.theme_action_group.addAction(theme_action)
                self.theme_menu.addAction(theme_action)

            # Добавляем опцию настройки тем
            self.theme_menu.addSeparator()
            customize_action = QAction(tr("menu.theme.customize", "Customize Theme..."), self)
            customize_action.triggered.connect(self.open_theme_settings)
            self.theme_menu.addAction(customize_action)

    def _update_language_menu(self):
        """Обновляет меню выбора языка."""
        try:
            if hasattr(self, 'language_menu'):
                # Очищаем меню языков
                self.language_menu.clear()

            if hasattr(self, 'language_action_group'):
                if self.language_action_group is not None:
                    self.language_action_group.deleteLater()

            self.language_action_group = QActionGroup(self)

            # Получаем текущий язык
            from app.ui.i18n.translator import JsonTranslationManager
            current_language = JsonTranslationManager.instance().get_current_language()

            # Добавляем доступные языки
            language_options = [
                {"code": "en_US", "name": tr("language.english", "English")},
                {"code": "ru_RU", "name": tr("language.russian", "Русский")}
            ]

            for lang in language_options:
                lang_action = QAction(lang["name"], self, checkable=True)
                lang_action.setData(lang["code"])
                if lang["code"] == current_language:
                    lang_action.setChecked(True)
                lang_action.triggered.connect(lambda checked, lc=lang["code"]: self._on_language_changed(lc))
                self.language_action_group.addAction(lang_action)
                self.language_menu.addAction(lang_action)

        except Exception as e:
            logger.error(f"Error updating language menu: {str(e)}")

    def _connect_theme_language_signals(self):
        """Подключает сигналы изменения темы и языка."""
        try:
            # Подключаем сигнал изменения темы
            ThemeManager.instance().themeChanged.connect(self._on_theme_changed_event)

            # Подключаем сигнал изменения языка
            from app.ui.i18n.translator import JsonTranslationManager
            JsonTranslationManager.instance().languageChanged.connect(self._on_language_changed_event)
        except Exception as e:
            logger.error(f"Error connecting theme and language signals: {str(e)}")

    def _on_theme_changed(self, theme_name):
        """Обработчик изменения темы интерфейса."""
        try:
            ThemeManager.instance().switch_visual_theme(theme_name)
        except Exception as e:
            logger.error(f"Error changing theme: {str(e)}")

    def _on_theme_changed_event(self, theme_name):
        """Обработчик события изменения темы интерфейса."""
        try:
            # Обновляем меню тем
            self._update_themes_menu()
            # Загружаем стили
            self._load_styles()
            # Обновляем интерфейс
            self.update()
        except Exception as e:
            logger.error(f"Error handling theme change event: {str(e)}")

    def _on_language_changed(self, language_code):
        """Обработчик изменения языка интерфейса."""
        try:
            from app.ui.i18n.translator import JsonTranslationManager
            JsonTranslationManager.instance().switch_language(language_code)
        except Exception as e:
            logger.error(f"Error changing language: {str(e)}")

    def _on_language_changed_event(self, language_code):
        """Обработчик события изменения языка интерфейса."""
        try:
            # Обновляем меню языков и тем
            self._update_language_menu()
            self._update_themes_menu()

            # Обновляем переводы интерфейса
            self.retranslateUi()

            # Обновляем меню через менеджер меню
            if hasattr(self, 'menu_manager'):
                self.menu_manager.update_translations()

            # Обновляем доки и их заголовки
            self._update_custom_title_bars()

            # Обновляем интерфейс
            self.update()
        except Exception as e:
            logger.error(f"Error handling language change event: {str(e)}")

    def _create_toolbars(self):
        """Создает панели инструментов."""
        # --- Основная панель инструментов ---
        self.main_toolbar = self.addToolBar(self._translate("toolbar.main", "Main Toolbar"))
        self.main_toolbar.setObjectName("MainToolBar")  # Для сохранения настроек
        self.main_toolbar.setMovable(True)  # Пользователь может перемещать тулбар

        # Добавляем действия на панель инструментов
        self.main_toolbar.addAction(self.new_file_action)
        self.main_toolbar.addAction(self.open_file_action)
        self.main_toolbar.addAction(self.save_file_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.cut_action)
        self.main_toolbar.addAction(self.copy_action)
        self.main_toolbar.addAction(self.paste_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.undo_action)
        self.main_toolbar.addAction(self.redo_action)

    def _create_status_bar(self):
        """Создает и настраивает статус-бар."""
        self.status_bar = self.statusBar()
        self.status_bar.setSizeGripEnabled(True)  # Показывать маркер изменения размера

        # Создаем виджеты статус-бара
        self.status_label = QLabel(self._translate("status.ready", "Ready"))
        self.status_bar.addPermanentWidget(self.status_label, 1)  # Растягивать по ширине

        # Информация о файле
        self.file_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.file_info_label)

        # Статус агента
        self.agent_status_label = QLabel("")
        self.status_bar.addPermanentWidget(self.agent_status_label)

        # Прогресс-бар для операций
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setVisible(False)  # По умолчанию скрыт
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _apply_dock_constraints(self):
        """Применяет ограничения для док-виджетов."""
        try:
            # Определяем разрешенные области для док-виджетов
            if hasattr(self, 'project_explorer_dock'):
                self.project_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)

            if hasattr(self, 'chat_dock'):
                self.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea)

            if hasattr(self, 'terminal_dock'):
                self.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea |
                                                  Qt.LeftDockWidgetArea |
                                                  Qt.RightDockWidgetArea)

            if hasattr(self, 'browser_dock'):
                self.browser_dock.setAllowedAreas(Qt.RightDockWidgetArea |
                                                 Qt.BottomDockWidgetArea)

            # Обновляем заголовки доков
            self._update_custom_title_bars()

        except Exception as e:
            logger.error(f"Error applying dock constraints: {str(e)}")

    def _update_custom_title_bars(self):
        """Обновляет кастомные заголовки доков."""
        try:
            # Применяем кастомные заголовки ко всем докам
            if hasattr(self, 'project_explorer_dock'):
                apply_custom_title_bar(self.project_explorer_dock, is_docked_permanent=True)

            if hasattr(self, 'chat_dock'):
                apply_custom_title_bar(self.chat_dock, is_docked_permanent=True)

            if hasattr(self, 'terminal_dock'):
                apply_custom_title_bar(self.terminal_dock, is_docked_permanent=False)

            if hasattr(self, 'browser_dock'):
                apply_custom_title_bar(self.browser_dock, is_docked_permanent=False)

        except Exception as e:
            logger.error(f"Error updating custom title bars: {str(e)}")

    def _apply_initial_layout(self):
        """Применяет начальный макет окна и восстанавливает настройки."""
        # Восстанавливаем геометрию и состояние окна, если они были сохранены
        self._restore_window_state()

        # Инициализируем менеджер тем
        theme_manager = ThemeManager.instance()

        # Получаем менеджер переводов
        from app.ui.i18n.translator import JsonTranslationManager

        # Применяем сохраненную визуальную тему
        current_visual_theme = theme_manager.get_current_visual_theme()
        theme_manager.switch_visual_theme(current_visual_theme)

        # Применяем сохраненный язык
        current_language = JsonTranslationManager.instance().get_current_language()
        JsonTranslationManager.instance().switch_language(current_language)

        # Обновляем заголовки всех доков
        self._update_custom_title_bars()

        # Показываем основные доки (проводник проекта и чат)
        if hasattr(self, 'project_explorer_dock'):
            self.project_explorer_dock.show()

        if hasattr(self, 'chat_dock'):
            self.chat_dock.show()

        # Скрываем второстепенные доки
        if hasattr(self, 'terminal_dock'):
            self.terminal_dock.hide()

        if hasattr(self, 'browser_dock'):
            self.browser_dock.hide()

        # Добавляем обработку событий для корректного отображения
        QApplication.processEvents()

    def _restore_window_state(self):
        """Восстанавливает геометрию и состояние окна из настроек."""
        try:
            # Восстанавливаем размер и позицию окна
            geometry = self.settings.value("window/geometry")
            if geometry:
                self.restoreGeometry(geometry)
            else:
                # Устанавливаем размер по умолчанию, если нет сохраненных настроек
                self.resize(1280, 720)
                # Центрируем окно на экране
                center_point = QApplication.primaryScreen().availableGeometry().center()
                frame_geometry = self.frameGeometry()
                frame_geometry.moveCenter(center_point)
                self.move(frame_geometry.topLeft())

            # Восстанавливаем состояние окна (панели инструментов, доки)
            state = self.settings.value("window/state")
            if state:
                self.restoreState(state)

        except Exception as e:
            logger.error(f"Error restoring window state: {str(e)}")
            # Устанавливаем размер по умолчанию в случае ошибки
            self.resize(1280, 720)

    def retranslateUi(self):
        """Обновляет тексты интерфейса при смене языка."""
        from app.ui.i18n.translator import tr

        # Заголовок главного окна
        self.setWindowTitle(tr("main_window", "GopiAI"))

        # Обновляем только заголовки существующих меню, не пересоздавая их
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(tr("menu.file", "File"))
        if hasattr(self, 'edit_menu'):
            self.edit_menu.setTitle(tr("menu.edit", "Edit"))
        if hasattr(self, 'view_menu'):
            self.view_menu.setTitle(tr("menu.view", "View"))
        if hasattr(self, 'tools_menu'):
            self.tools_menu.setTitle(tr("menu.tools", "Tools"))
        if hasattr(self, 'help_menu'):
            self.help_menu.setTitle(tr("menu.help", "Help"))
        if hasattr(self, 'theme_menu'):
            self.theme_menu.setTitle(tr("menu.theme", "Theme"))
        if hasattr(self, 'language_menu'):
            self.language_menu.setTitle(tr("menu.language", "Language"))

        # Обновляем переводы для действий меню
        if hasattr(self, 'new_file_action'):
            self.new_file_action.setText(tr("menu.new", "New"))
            self.new_file_action.setStatusTip(tr("menu.new.tooltip", "Create a new file"))

        if hasattr(self, 'open_file_action'):
            self.open_file_action.setText(tr("menu.open_file", "Open"))
            self.open_file_action.setStatusTip(tr("menu.open_file.tooltip", "Open an existing file"))

        if hasattr(self, 'save_file_action'):
            self.save_file_action.setText(tr("menu.save", "Save"))
            self.save_file_action.setStatusTip(tr("menu.save.tooltip", "Save the current file"))

        if hasattr(self, 'save_as_action'):
            self.save_as_action.setText(tr("menu.save_as", "Save As"))
            self.save_as_action.setStatusTip(tr("menu.save_as.tooltip", "Save the file with a new name"))

        if hasattr(self, 'exit_action'):
            self.exit_action.setText(tr("menu.exit", "Exit"))
            self.exit_action.setStatusTip(tr("menu.exit.tooltip", "Exit the application"))

        # Обработка событий для плавности интерфейса
        QApplication.processEvents()

        # Обновление действий меню Edit
        if hasattr(self, 'cut_action'):
            self.cut_action.setText(tr("menu.cut", "Cut"))
            self.cut_action.setStatusTip(tr("menu.cut.tooltip", "Cut the selected text"))

        if hasattr(self, 'copy_action'):
            self.copy_action.setText(tr("menu.copy", "Copy"))
            self.copy_action.setStatusTip(tr("menu.copy.tooltip", "Copy the selected text"))

        if hasattr(self, 'paste_action'):
            self.paste_action.setText(tr("menu.paste", "Paste"))
            self.paste_action.setStatusTip(tr("menu.paste.tooltip", "Paste from clipboard"))

        if hasattr(self, 'undo_action'):
            self.undo_action.setText(tr("menu.undo", "Undo"))
            self.undo_action.setStatusTip(tr("menu.undo.tooltip", "Undo the last action"))

        if hasattr(self, 'redo_action'):
            self.redo_action.setText(tr("menu.redo", "Redo"))
            self.redo_action.setStatusTip(tr("menu.redo.tooltip", "Redo the undone action"))

        if hasattr(self, 'select_all_action'):
            self.select_all_action.setText(tr("menu.select_all", "Select All"))
            self.select_all_action.setStatusTip(tr("menu.select_all.tooltip", "Select all content"))

    def open_theme_settings(self):
        """Открывает диалог настроек темы и языка."""
        try:
            from app.ui.theme_settings_dialog import ThemeSettingsDialog
            dialog = ThemeSettingsDialog(self)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                # Показываем сообщение об успешном применении настроек
                QMessageBox.information(
                    self,
                    tr("main_window.settings_applied", "Settings Applied"),
                    tr("main_window.theme_settings_success", "Theme and language settings successfully applied.")
                )
        except Exception as e:
            logger.error(f"Error opening theme settings: {str(e)}")
            QMessageBox.warning(
                self,
                tr("error.title", "Error"),
                tr("error.theme_change", "Error changing theme") + f": {str(e)}"
            )

    def _close_tab(self, index):
        """Закрывает указанную вкладку."""
        # Получаем виджет вкладки
        widget = self.central_tabs.widget(index)

        # Проверяем, есть ли несохраненные изменения (если виджет поддерживает)
        if hasattr(widget, 'is_modified') and widget.is_modified():
            # Спрашиваем пользователя о сохранении изменений
            reply = QMessageBox.question(
                self,
                tr("dialogs.save_changes", "Save Changes?"),
                tr("dialogs.unsaved_changes", "You have unsaved changes. Do you want to save them?"),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                # Если пользователь хочет сохранить
                if hasattr(widget, 'file_path') and widget.file_path:
                    # Если есть путь к файлу, сохраняем
                    if hasattr(widget, 'save'):
                        widget.save()
                else:
                    # Если нет пути, предлагаем сохранить как
                    if hasattr(widget, 'save_as'):
                        success = widget.save_as()
                        if not success:  # Если пользователь отменил сохранение
                            return
            elif reply == QMessageBox.Cancel:
                # Если пользователь отменил, не закрываем вкладку
                return

        # Закрываем вкладку и удаляем виджет
        self.central_tabs.removeTab(index)
        if hasattr(widget, 'close') and callable(widget.close):
            widget.close()
        widget.deleteLater()

    def _new_file(self):
        """Создает новую вкладку с пустым файлом."""
        try:
            from app.ui.editor import CodeEditor
            from app.ui.i18n.translator import tr

            # Создаем новый редактор кода
            editor = CodeEditor(self)

            # Используем перевод для имени нового файла
            new_file_name = tr("code.new_file", "new_file.py")

            # Добавляем временный путь (будет заменен при первом сохранении)
            editor.file_path = new_file_name

            # Добавляем вкладку
            index = self.central_tabs.addTab(editor, new_file_name)
            self.central_tabs.setCurrentIndex(index)

            # Фокус на новом редакторе
            editor.setFocus()

            # Обновляем статус
            self.status_label.setText(tr("status.ready", "Ready"))

        except Exception as e:
            logger.error(f"Error creating new file: {str(e)}")
            from app.ui.i18n.translator import tr
            QMessageBox.warning(
                self,
                tr("error.title", "Error"),
                tr("error.creating_file", "Error creating new file") + f": {str(e)}"
            )

    def _open_file(self, file_path=None):
        """Открывает файл в редакторе."""
        try:
            # Если путь к файлу не указан, показываем диалог выбора файла
            if not file_path:
                dialog = QFileDialog(self)
                dialog.setWindowTitle(tr("dialogs.file.open", "Open File"))
                dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
                dialog.setViewMode(QFileDialog.ViewMode.Detail)

                # Если пользователь выбрал файл
                if dialog.exec():
                    file_path = dialog.selectedFiles()[0]
                else:
                    return  # Пользователь отменил операцию

            # Проверяем существование файла
            if not os.path.isfile(file_path):
                logger.error(f"Файл не существует: {file_path}")
                QMessageBox.warning(
                    self,
                    tr("dialogs.error.title", "Error"),
                    tr("dialogs.file.open_error", "Error opening file")
                )
                return

            # Загружаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Создаем новый редактор кода
            from app.ui.editor import CodeEditor
            editor = CodeEditor(self)
            editor.file_path = file_path
            editor.setPlainText(content)

            # Получаем имя файла для вкладки
            file_name = os.path.basename(file_path)

            # Добавляем вкладку
            index = self.central_tabs.addTab(editor, file_name)
            self.central_tabs.setCurrentIndex(index)

            # Фокус на новом редакторе
            editor.setFocus()

            # Обновляем статус
            self.status_label.setText(tr("status.file_opened", "File opened"))

            # Обновляем заголовок окна
            self.setWindowTitle(f"{file_name} - {APP_NAME}")

            return True

        except Exception as e:
            logger.error(f"Ошибка при открытии файла: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"{tr('dialogs.file.open_error', 'Error opening file')}: {str(e)}"
            )
            return False

    def _save_file(self):
        """Сохраняет текущий файл."""
        try:
            # Получаем индекс текущей вкладки
            current_index = self.central_tabs.currentIndex()
            if current_index == -1:
                return False  # Нет активной вкладки

            # Получаем виджет текущей вкладки
            editor = self.central_tabs.widget(current_index)
            if not hasattr(editor, 'file_path'):
                return False  # Не редактор кода

            # Если путь к файлу не установлен, вызываем save_as
            if not editor.file_path or editor.file_path == tr("code.new_file", "new_file.py"):
                return self._save_file_as()

            # Сохраняем содержимое в файл
            content = editor.toPlainText()
            with open(editor.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Обновляем заголовок вкладки
            self.central_tabs.setTabText(current_index, os.path.basename(editor.file_path))

            # Обновляем статус
            self.status_label.setText(tr("status.file_saved", "File saved"))

            # Очищаем флаг измененного файла, если он есть
            if hasattr(editor, 'set_modified'):
                editor.set_modified(False)

            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"{tr('dialogs.file.save_error', 'Error saving file')}: {str(e)}"
            )
            return False

    def _save_file_as(self):
        """Сохраняет текущий файл под новым именем."""
        try:
            # Получаем индекс текущей вкладки
            current_index = self.central_tabs.currentIndex()
            if current_index == -1:
                return False  # Нет активной вкладки

            # Получаем виджет текущей вкладки
            editor = self.central_tabs.widget(current_index)
            if not hasattr(editor, 'file_path'):
                return False  # Не редактор кода

            # Показываем диалог сохранения файла
            dialog = QFileDialog(self)
            dialog.setWindowTitle(tr("dialogs.file.save", "Save File"))
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)

            # Если есть текущий путь к файлу, устанавливаем начальный каталог
            if editor.file_path and editor.file_path != tr("code.new_file", "new_file.py"):
                dialog.setDirectory(os.path.dirname(editor.file_path))
                dialog.selectFile(os.path.basename(editor.file_path))

            # Если пользователь выбрал файл
            if dialog.exec():
                file_path = dialog.selectedFiles()[0]

                # Сохраняем путь к файлу
                editor.file_path = file_path

                # Сохраняем содержимое в файл
                content = editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Обновляем заголовок вкладки
                file_name = os.path.basename(file_path)
                self.central_tabs.setTabText(current_index, file_name)

                # Обновляем заголовок окна
                self.setWindowTitle(f"{file_name} - {APP_NAME}")

                # Обновляем статус
                self.status_label.setText(tr("status.file_saved", "File saved"))

                # Очищаем флаг измененного файла, если он есть
                if hasattr(editor, 'set_modified'):
                    editor.set_modified(False)

                return True
            else:
                # Пользователь отменил операцию
                return False

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"{tr('dialogs.file.save_error', 'Error saving file')}: {str(e)}"
            )
            return False

    def _on_cut(self):
        """Вырезает выделенный текст."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'cut'):
                current_widget.cut()
        except Exception as e:
            logger.error(f"Ошибка при вырезании текста: {str(e)}")

    def _on_copy(self):
        """Копирует выделенный текст."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'copy'):
                current_widget.copy()
        except Exception as e:
            logger.error(f"Ошибка при копировании текста: {str(e)}")

    def _on_paste(self):
        """Вставляет текст из буфера обмена."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'paste'):
                current_widget.paste()
        except Exception as e:
            logger.error(f"Ошибка при вставке текста: {str(e)}")

    def _on_undo(self):
        """Отменяет последнее действие."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'undo'):
                current_widget.undo()
        except Exception as e:
            logger.error(f"Ошибка при отмене действия: {str(e)}")

    def _on_redo(self):
        """Повторяет отмененное действие."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'redo'):
                current_widget.redo()
        except Exception as e:
            logger.error(f"Ошибка при повторе действия: {str(e)}")

    def _on_select_all(self):
        """Выделяет весь текст."""
        try:
            current_widget = self.central_tabs.currentWidget()
            if hasattr(current_widget, 'selectAll'):
                current_widget.selectAll()
        except Exception as e:
            logger.error(f"Ошибка при выделении всего текста: {str(e)}")

    def _show_emoji_dialog(self):
        """Показывает диалог выбора эмодзи."""
        try:
            # Получаем текущий виджет
            current_widget = self.central_tabs.currentWidget()
            if not hasattr(current_widget, 'insertPlainText'):
                return  # Текущий виджет не поддерживает вставку текста

            # Создаем диалог эмодзи
            emoji_dialog = EmojiDialog(self)

            # Подключаем сигнал выбора эмодзи
            emoji_dialog.emoji_selected.connect(
                lambda emoji: current_widget.insertPlainText(emoji)
            )

            # Показываем диалог
            emoji_dialog.exec()

        except Exception as e:
            logger.error(f"Ошибка при показе диалога эмодзи: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error showing emoji dialog: {str(e)}"
            )

    def _toggle_browser(self, checked=None):
        """Переключает видимость панели браузера."""
        if not hasattr(self, 'browser_dock'):
            print("Браузер не инициализирован")
            return

        if checked is None:
            checked = not self.browser_dock.isVisible()
        self.browser_dock.setVisible(checked)
        if hasattr(self, 'toggle_browser_action'):
            self.toggle_browser_action.setChecked(checked)

    def _open_url_in_browser(self):
        """Показывает диалог для ввода URL и открывает его в браузере."""
        try:
            # Проверяем, доступен ли браузер
            if not hasattr(self, 'browser_widget'):
                QMessageBox.warning(
                    self,
                    tr("dialogs.error.title", "Error"),
                    "Web browser module is not available"
                )
                return

            # Показываем диалог для ввода URL
            url, ok = QInputDialog.getText(
                self,
                tr("dialogs.open_url", "Open URL"),
                tr("dialogs.enter_url", "Enter URL to open:")
            )

            if ok and url:
                # Если URL не содержит протокол, добавляем http://
                if not url.startswith('http://') and not url.startswith('https://'):
                    url = 'https://' + url

                # Делаем браузер видимым, если он скрыт
                if not self.browser_dock.isVisible():
                    self._toggle_browser(True)

                # Загружаем URL в браузер
                self.browser_widget.load_url(url)
                self.status_label.setText(tr("status.url_opened", "URL opened"))

        except Exception as e:
            logger.error(f"Ошибка при открытии URL: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error opening URL: {str(e)}"
            )

    def _show_flow_visualization(self):
        """Показывает визуализацию потока агента."""
        try:
            # Проверяем, доступен ли агент
            if not hasattr(self, 'agent') or self.agent is None:
                QMessageBox.warning(
                    self,
                    tr("agent.not_initialized", "Agent Not Initialized"),
                    tr("agent.not_initialized_message", "Please initialize the agent first.")
                )
                return

            # Получаем поток агента
            flow = None
            if hasattr(self.agent, 'get_flow'):
                flow = self.agent.get_flow()

            # Если поток недоступен, показываем сообщение
            if flow is None:
                QMessageBox.information(
                    self,
                    tr("flow.no_flow", "No Flow Available"),
                    tr("flow.no_flow_message", "The current agent does not have an available flow to visualize.")
                )
                return

            # Показываем диалог визуализации потока
            show_flow_visualizer_dialog(flow, parent=self)

        except Exception as e:
            logger.error(f"Ошибка при показе визуализации потока: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error showing flow visualization: {str(e)}"
            )

    def _on_configure_agent(self):
        """Показывает диалог настройки агента."""
        try:
            # Проверяем, доступен ли агент
            if not hasattr(self, 'agent') or self.agent is None:
                QMessageBox.warning(
                    self,
                    tr("agent.not_initialized", "Agent Not Initialized"),
                    tr("agent.not_initialized_message", "Please initialize the agent first.")
                )
                return

            # В будущем здесь будет показ диалога настройки агента
            QMessageBox.information(
                self,
                tr("agent.config.dialog_title", "Agent Configuration"),
                "Agent configuration dialog is not implemented yet."
            )

        except Exception as e:
            logger.error(f"Ошибка при настройке агента: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error configuring agent: {str(e)}"
            )

    def _show_preferences_dialog(self):
        """Показывает диалог настроек."""
        try:
            from app.ui.settings_widget import SettingsDialog

            # Создаем диалог настроек
            settings_dialog = SettingsDialog(self)

            # Показываем диалог
            result = settings_dialog.exec()

            # Если пользователь нажал OK, применяем настройки
            if result == QDialog.Accepted:
                # Обновляем настройки
                self._load_styles(True)
                self.retranslateUi()

        except Exception as e:
            logger.error(f"Ошибка при показе диалога настроек: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error showing preferences dialog: {str(e)}"
            )

    def _on_about(self):
        """Показывает информацию о программе."""
        try:
            about_title = tr("about.title", "About GopiAI")
            about_text = tr("about.description", "An AI assistant with advanced capabilities.")

            # Версия приложения
            version = "1.0.0"  # Здесь следует получать версию из конфигурации
            version_text = f"{tr('app.version', 'Version')}: {version}"

            # Полный текст
            full_text = f"{about_text}\n\n{version_text}"

            # Показываем диалог "О программе"
            QMessageBox.about(self, about_title, full_text)

        except Exception as e:
            logger.error(f"Ошибка при показе информации о программе: {str(e)}")

    def _on_documentation(self):
        """Показывает документацию."""
        try:
            doc_title = tr("documentation.title", "Documentation")
            doc_text = tr("documentation.not_implemented", "Documentation is not implemented yet.")

            # Показываем диалог с документацией
            QMessageBox.information(self, doc_title, doc_text)

        except Exception as e:
            logger.error(f"Ошибка при показе документации: {str(e)}")

    def reset_ui(self):
        """Сбрасывает состояние пользовательского интерфейса."""
        try:
            # Сбрасываем расположение панелей
            self.reset_dock_layout()

            # Повторно загружаем стили
            self._load_styles(True)

            # Обновляем переводы
            self.retranslateUi()

            # Показываем сообщение об успешном сбросе
            self.status_label.setText(tr("status.ui_reset", "UI reset to defaults"))

        except Exception as e:
            logger.error(f"Ошибка при сбросе интерфейса: {str(e)}")
            QMessageBox.warning(
                self,
                tr("dialogs.error.title", "Error"),
                f"Error resetting UI: {str(e)}"
            )

    def show_coding_agent(self):
        """Показывает диалог с агентом кодирования."""
        self._open_coding_agent()

    def show_browsing_agent(self):
        """Показывает диалог с агентом браузера."""
        self._open_browsing_agent()

    def show_reasoning_agent(self):
        """Открывает диалог Reasoning Agent."""
        try:
            from app.agent.reasoning import ReasoningAgent
            from app.ui.reasoning_agent_dialog import ReasoningAgentDialog

            # Инициализируем Reasoning Agent
            reasoning_agent = ReasoningAgent()

            # Создаем и показываем диалог
            reasoning_dialog = ReasoningAgentDialog(reasoning_agent, self)
            reasoning_dialog.show()

            logger.info("Opened Reasoning Agent dialog")
        except ImportError as e:
            logger.error(f"Failed to import Reasoning components: {e}")
            QMessageBox.warning(
                self,
                self.tr("menu.reasoning_agent.error.title", "Reasoning Agent Error"),
                self.tr("menu.reasoning_agent.error.message",
                      "Failed to load Reasoning Agent components. Check if all required modules are installed.")
            )

    def show_reasoning_settings(self):
        """Открывает диалог настроек Reasoning."""
        try:
            dialog = ReasoningSettingsDialog(self)

            # Подключаем сигнал изменения настроек
            dialog.settings_changed.connect(self._on_reasoning_settings_changed)

            # Показываем диалог
            dialog.exec()

            logger.info("Opened Reasoning Settings dialog")
        except Exception as e:
            logger.error(f"Failed to open Reasoning Settings dialog: {e}")
            QMessageBox.warning(
                self,
                self.tr("menu.reasoning_settings.error.title", "Settings Error"),
                self.tr("menu.reasoning_settings.error.message",
                      "Failed to open Reasoning Settings dialog. Error: {0}").format(str(e))
            )

    def _on_reasoning_settings_changed(self):
        """Обрабатывает изменение настроек Reasoning."""
        logger.info("Reasoning settings were changed")

        # Если есть активные экземпляры Reasoning Agent, уведомляем их
        # о необходимости перезагрузить настройки

        # Уведомляем пользователя
        self.statusBar().showMessage(
            self.tr("menu.reasoning_settings.changed", "Reasoning settings updated"),
            3000
        )
