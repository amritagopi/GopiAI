# main_window.py
import os
import logging
from PySide6.QtWidgets import QMainWindow, QApplication, QDockWidget, QMessageBox, QDialog, QVBoxLayout, QWidget, QToolBar, QMenu, QLabel, QFileDialog, QHBoxLayout, QSizePolicy # Удаляем QAction
from PySide6.QtGui import QAction, QKeySequence # Добавляем импорт QKeySequence
from PySide6.QtCore import QSettings, QThreadPool, Qt, QTimer, QEvent
from app.utils.theme_manager import ThemeManager
from app.ui.i18n.translator import JsonTranslationManager, tr
from .central_widget import setup_central_widget
from .docks import create_docks
from .menus import setup_menus
from .toolbars import create_toolbars
from .status_bar import create_status_bar
from .coding_agent_dialog import CodingAgentDialog # Added import for separate window usage
from .main_window_title_bar import MainWindowTitleBar # Импортируем класс кастомного заголовка
from ..logic.agent_setup import setup_agent, connect_agent_signals, handle_user_message, handle_agent_response, update_agent_status_display
from ..utils.ui_utils import validate_ui_components, apply_dock_constraints, update_custom_title_bars, fix_duplicate_docks, load_fonts
from ..utils.theme_utils import on_theme_changed_event
from ..utils.translation import translate, on_language_changed_event
from ..utils.settings import restore_window_state
from ..plugins.plugin_manager import PluginManager # Импортируем менеджер плагинов
from .agent_ui_integration import update_integration_status, fix_missing_signals, save_integration_status_to_serena # Добавляем импорт функции сохранения статуса
# Import event handlers
from ..logic.event_handlers import (
    on_file_double_clicked,
    on_tab_changed,
    on_project_tree_double_clicked,
    on_dock_visibility_changed
)
from ..utils.signal_checker import check_main_window_signals, auto_connect_signals

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, icon_manager, parent=None): # Добавлен icon_manager
        super().__init__(parent)
        self.icon_manager = icon_manager # Сохраняем экземпляр

        # Удаляем флаг безрамочного окна, чтобы вернуть стандартную рамку
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # Удаляем атрибуты, связанные с безрамочным окном
        # self.setAttribute(Qt.WA_NoSystemBackground, False)
        # self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setWindowTitle(tr("app.title", "GopiAI"))
        self.resize(1200, 800)
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.translation_manager = JsonTranslationManager.instance()
        self.theme_manager = ThemeManager.instance() # Убрали аргумент

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

        # Инициализация переменных для перетаскивания окна - больше не нужны
        # self.dragging = False
        # self.drag_position = None

        # Удаляем создание кастомного виджета с кнопками управления окном
        # from .window_control_widget import WindowControlWidget
        # self.window_controls = WindowControlWidget(self.icon_manager, self)

        # Сразу применяем тему, чтобы избежать "мигания" с белой темой
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_visual_theme()
            logger.info(f"Принудительно применяем тему при инициализации: {current_theme}")
            self.theme_manager.switch_visual_theme(current_theme, force_apply=True)
            QApplication.processEvents()  # Обрабатываем события, чтобы тема применилась немедленно

        self.thread_pool = QThreadPool()
        self.setObjectName("MainWindow")
        self.settings = QSettings(tr("app.title", "GopiAI"), "UI")
        self.sessions = {}
        self.agent = setup_agent(self)

        # Инициализируем менеджер плагинов
        self.plugin_manager = PluginManager.instance()
        self.plugin_manager.set_main_window(self)

        # Coding agent dialog reference
        self.coding_agent_dialog = None

        # Подключаемся к сигналу languageChanged
        self.translation_manager.languageChanged.connect(self._on_language_changed_event)
        logger.info("Подключен сигнал JsonTranslationManager.languageChanged к MainWindow._on_language_changed_event")

        # Подключаемся к сигналу visualThemeChanged
        self.theme_manager.visualThemeChanged.connect(lambda theme_name: on_theme_changed_event(self, theme_name))
        logger.info("Подключен сигнал ThemeManager.visualThemeChanged к on_theme_changed_event")

        self._setup_ui()
        self.installEventFilter(self)

        # Проверка интеграции агентов и сохранение в Serena перемещено в _setup_ui

    def _setup_ui(self):
        try:
            logger.info("Starting _setup_ui in MainWindow")
            load_fonts(self)

            # Удаляю код, связанный с кастомным размещением кнопок управления окном
            # menubar_layout = QHBoxLayout()
            # menubar_layout.setContentsMargins(0, 0, 0, 0)
            # menubar_layout.setSpacing(0)

            # Используем существующий menuBar
            self.menuBar = self.menuBar()
            # menubar_layout.addWidget(self.menuBar, 1)  # Меню занимает всё доступное пространство

            # Добавляем пустой растягивающийся элемент, чтобы меню не занимало всё пространство - больше не нужно
            # spacer = QWidget()
            # spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            # menubar_layout.addWidget(spacer)

            # Добавляем кнопки управления окном - больше не нужно
            # if hasattr(self, "window_controls"):
            #     menubar_layout.addWidget(self.window_controls)

            # Создаем контейнер для menuBar и контролов окна - больше не нужно
            # menu_container = QWidget()
            # menu_container.setLayout(menubar_layout)

            # Основной макет окна
            main_layout = QVBoxLayout()
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Добавляем контейнер меню в верхнюю часть - больше не нужно
            # main_layout.addWidget(menu_container)

            # Вместо прямой установки через setCentralWidget
            # мы теперь добавляем компоненты в self.content_widget
            setup_central_widget(self, self.content_widget)

            # Добавляем основной контент в макет
            main_layout.addWidget(self.content_widget, 1)  # 1 = растягивается по вертикали

            # Создаем главный виджет, который будет содержать всё
            central_container = QWidget()
            central_container.setLayout(main_layout)
            self.setCentralWidget(central_container)

            create_docks(self)

            # Use only setup_menus, NEVER fall back to _create_menus
            logger.info("Setting up menus through setup_menus...")
            setup_result = setup_menus(self)
            if not setup_result:
                logger.error("Error setting up menus through setup_menus")
                # Do not fall back to _create_menus anymore - it causes conflicts
                logger.critical("Menu setup failed! UI may be non-functional.")
            else:
                logger.info("Menus set up successfully via setup_menus")

            create_toolbars(self)
            create_status_bar(self)
            validate_ui_components(self)
            apply_dock_constraints(self)
            self._connect_global_ui_signals()
            current_language = JsonTranslationManager.instance().get_current_language()
            on_language_changed_event(self, current_language)
            self._apply_initial_layout()

            # Удаляем настройку инспектора стилей Qt
            # self._setup_style_inspector()

            # Исправляем отсутствующие сигналы перед подключением агентов
            logger.info("Fixing missing signals before agent connection")
            fixes = fix_missing_signals(self)
            fixed_components = [comp for comp, fixes in fixes.items() if fixes]
            if fixed_components:
                logger.info(f"Fixed signals in components: {', '.join(fixed_components)}")
                # Сохраняем информацию о примененных исправлениях
                self._ui_fixes_applied = {comp: fixes for comp, fixes in fixes.items() if fixes}

            # Подключаем сигналы агентов
            connect_agent_signals(self)

            # Проверяем статус интеграции агентов
            integration_status = update_integration_status(self)
            for component, status in integration_status.items():
                if status:
                    logger.info(f"Integration of {component} is successful")
                else:
                    logger.warning(f"Integration of {component} is incomplete")

            # Сохраняем статус интеграции в памяти Serena
            save_result = save_integration_status_to_serena(self, integration_status)
            if save_result:
                logger.info("Integration status saved to Serena memory")
            else:
                logger.warning("Failed to save integration status to Serena memory")

            QApplication.processEvents()
            logger.info("Completed _setup_ui in MainWindow")
        except Exception as e:
            logger.error(f"Error setting up UI: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def _connect_global_ui_signals(self):
        if hasattr(self, "project_explorer_dock"):
            self.project_explorer_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(self, visible))
        if hasattr(self, "chat_dock"):
            self.chat_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(self, visible))
        if hasattr(self, "terminal_dock"):
            self.terminal_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(self, visible))

        if hasattr(self, "project_explorer") and hasattr(self.project_explorer, "file_double_clicked"):
             self.project_explorer.file_double_clicked.connect(lambda file_path: on_file_double_clicked(self, file_path))

        if hasattr(self, "central_tabs"):
            self.central_tabs.currentChanged.connect(lambda index: on_tab_changed(self, index))
            if hasattr(self, "_show_tab_context_menu"):
                 self.central_tabs.customContextMenuRequested.connect(self._show_tab_context_menu)
            if hasattr(self, "_close_tab"):
                 self.central_tabs.tabCloseRequested.connect(self._close_tab)

        # Сигналы MenuManager больше не нужны, так как мы напрямую подключаемся
        # к JsonTranslationManager.languageChanged и ThemeManager.visualThemeChanged
        pass

    def _apply_initial_layout(self):
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
            logger.error("ThemeManager instance is not available in _apply_initial_layout.")

        update_custom_title_bars(self, self.icon_manager) # Передаем icon_manager
        fix_duplicate_docks(self)
        if hasattr(self, "project_explorer_dock") and self.project_explorer_dock: self.project_explorer_dock.setVisible(True)
        if hasattr(self, "chat_dock") and self.chat_dock: self.chat_dock.setVisible(True)
        if hasattr(self, "terminal_dock") and self.terminal_dock: self.terminal_dock.setVisible(False)

        # Открываем окно Coding Agent как отдельное окно
        # Это можно отключить, если не нужно, чтобы окно открывалось автоматически
        QApplication.processEvents() # Обработаем события перед открытием окна

        # Открываем Coding Agent только если пользователь не отключил его специально
        settings = QSettings(tr("app.title", "GopiAI"), "UI")
        show_coding_agent = settings.value("coding_agent_visible", True, bool)

        if show_coding_agent:
            logger.info("Открываем Coding Agent по умолчанию при запуске")
            # Запускаем открытие окна с небольшой задержкой
            QTimer.singleShot(500, self.show_coding_agent_dialog)

        self._update_view_menu()
        QApplication.processEvents()

    def _update_view_menu(self):
        try:
            if hasattr(self, "toggle_project_explorer_action") and hasattr(self, "project_explorer_dock") and self.project_explorer_dock and isinstance(self.project_explorer_dock, QDockWidget):
                self.toggle_project_explorer_action.setChecked(self.project_explorer_dock.isVisible())
            if hasattr(self, "toggle_chat_action") and hasattr(self, "chat_dock") and self.chat_dock and isinstance(self.chat_dock, QDockWidget):
                self.toggle_chat_action.setChecked(self.chat_dock.isVisible())
            if hasattr(self, "toggle_terminal_action") and hasattr(self, "terminal_dock") and self.terminal_dock and isinstance(self.terminal_dock, QDockWidget):
                self.toggle_terminal_action.setChecked(self.terminal_dock.isVisible())

            # Add the coding agent action state update if it exists
            if hasattr(self, "toggle_coding_agent_action"):
                has_coding_agent_open = self.coding_agent_dialog is not None and not self.coding_agent_dialog.isHidden()
                self.toggle_coding_agent_action.setChecked(has_coding_agent_open)
        except RuntimeError as e:
            logger.warning(f"Error updating view menu, dock might have been deleted: {e}")
        pass

    # New method to show coding agent in a separate window
    def show_coding_agent_dialog(self):
        """Opens the coding agent in a separate window"""
        try:
            logger.info("Opening coding agent dialog as separate window")

            # Create a new dialog if it doesn't exist or is deleted
            if not self.coding_agent_dialog or not hasattr(self.coding_agent_dialog, "isVisible"):
                self.coding_agent_dialog = CodingAgentDialog(self.icon_manager, self, self.theme_manager)

                # Восстанавливаем размер и позицию окна, если они были сохранены
                try:
                    saved_geometry = self.settings.value("coding_agent_geometry")
                    if saved_geometry:
                        logger.info("Восстанавливаем размер и позицию окна Coding Agent")
                        self.coding_agent_dialog.restoreGeometry(saved_geometry)
                except Exception as e:
                    logger.warning(f"Не удалось восстановить размер и позицию окна Coding Agent: {e}")

                # Connect the window's close event to update the action in the view menu
                self.coding_agent_dialog.finished.connect(self._update_view_menu)

                # Устанавливаем видимость в настройках
                self.settings.setValue("coding_agent_visible", True)

                # Подключаем сигналы между редактором и чатом
                if hasattr(self, "_connect_editor_chat_signals"):
                    self._connect_editor_chat_signals(self)

            # Show and bring to front if it exists but is hidden
            if not self.coding_agent_dialog.isVisible():
                self.coding_agent_dialog.show()
                self.coding_agent_dialog.raise_()
                self.coding_agent_dialog.activateWindow()
                self.settings.setValue("coding_agent_visible", True)

            # Update the view menu to show the correct state
            self._update_view_menu()

            # Return reference to the newly created dialog
            return self.coding_agent_dialog
        except Exception as e:
            logger.error(f"Error opening coding agent dialog: {e}")
            return None

    # Placeholder/Callback methods с реальной функциональностью
    def _new_file(self):
        """Создает новый файл."""
        logger.info("Action: New File - creating new file")

        # Если есть центральные табы, добавляем новую вкладку
        if hasattr(self, "central_tabs"):
            from app.ui.editor import CodeEditor
            editor = CodeEditor(self)
            editor.set_new_file()
            self.central_tabs.addTab(editor, "Untitled")
            self.central_tabs.setCurrentWidget(editor)
            logger.info("New file tab created")
        else:
            logger.error("Cannot create new file: central_tabs not found")

    def _open_file(self, file_path=None):
        """Открывает файл."""
        logger.info(f"Action: Open File {file_path}")

        # Если путь к файлу не указан, показываем диалог выбора файла
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, tr("dialog.open_file", "Open File"), "",
                tr("dialog.file_filter", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
            )

        if file_path and os.path.isfile(file_path):
            # Проверяем, может файл уже открыт
            if hasattr(self, "central_tabs"):
                # Попробуем найти, открыт ли уже этот файл
                for i in range(self.central_tabs.count()):
                    widget = self.central_tabs.widget(i)
                    if hasattr(widget, "file_path") and widget.file_path == file_path:
                        self.central_tabs.setCurrentIndex(i)
                        logger.info(f"File already open: {file_path}")
                        return

                # Файл не открыт, создаем новую вкладку
                from app.ui.editor import CodeEditor
                editor = CodeEditor(self)
                editor.open_file(file_path)
                filename = os.path.basename(file_path)
                self.central_tabs.addTab(editor, filename)
                self.central_tabs.setCurrentWidget(editor)
                logger.info(f"File opened: {file_path}")
            else:
                logger.error("Cannot open file: central_tabs not found")

    def _save_file(self):
        """Сохраняет текущий файл."""
        logger.info("Action: Save File")

        if hasattr(self, "central_tabs"):
            current_widget = self.central_tabs.currentWidget()
            if current_widget and hasattr(current_widget, "save_file"):
                current_widget.save_file()
                logger.info("File saved")
            else:
                logger.warning("Current widget does not support saving")
        else:
            logger.error("Cannot save file: central_tabs not found")

    def _save_file_as(self):
        """Сохраняет файл под новым именем."""
        logger.info("Action: Save File As")

        if hasattr(self, "central_tabs"):
            current_widget = self.central_tabs.currentWidget()
            if current_widget and hasattr(current_widget, "save_file_as"):
                current_widget.save_file_as()
                # Обновляем заголовок вкладки, если имя файла изменилось
                if hasattr(current_widget, "file_path"):
                    filename = os.path.basename(current_widget.file_path)
                    self.central_tabs.setTabText(self.central_tabs.currentIndex(), filename)
                logger.info("File saved as new name")
            else:
                logger.warning("Current widget does not support 'save as'")
        else:
            logger.error("Cannot save file: central_tabs not found")

    def _on_cut(self):
        """Вырезает выделенный текст."""
        logger.info("Action: Cut")

        # Находим активный виджет, который может поддерживать вырезание
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "cut") and callable(focused_widget.cut):
            focused_widget.cut()
            logger.info("Cut performed on focused widget")
        else:
            logger.warning("No widget with cut() method is focused")

    def _on_copy(self):
        """Копирует выделенный текст."""
        logger.info("Action: Copy")

        # Находим активный виджет, который может поддерживать копирование
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "copy") and callable(focused_widget.copy):
            focused_widget.copy()
            logger.info("Copy performed on focused widget")
        else:
            logger.warning("No widget with copy() method is focused")

    def _on_paste(self):
        """Вставляет текст из буфера обмена."""
        logger.info("Action: Paste")

        # Находим активный виджет, который может поддерживать вставку
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "paste") and callable(focused_widget.paste):
            focused_widget.paste()
            logger.info("Paste performed on focused widget")
        else:
            logger.warning("No widget with paste() method is focused")

    def _on_undo(self):
        """Отменяет последнее действие."""
        logger.info("Action: Undo")

        # Находим активный виджет, который может поддерживать отмену
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "undo") and callable(focused_widget.undo):
            focused_widget.undo()
            logger.info("Undo performed on focused widget")
        else:
            logger.warning("No widget with undo() method is focused")

    def _on_redo(self):
        """Повторяет отмененное действие."""
        logger.info("Action: Redo")

        # Находим активный виджет, который может поддерживать повтор
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "redo") and callable(focused_widget.redo):
            focused_widget.redo()
            logger.info("Redo performed on focused widget")
        else:
            logger.warning("No widget with redo() method is focused")

    def _on_select_all(self):
        """Выделяет весь текст."""
        logger.info("Action: Select All")

        # Находим активный виджет, который может поддерживать выделение всего
        focused_widget = QApplication.focusWidget()
        if hasattr(focused_widget, "selectAll") and callable(focused_widget.selectAll):
            focused_widget.selectAll()
            logger.info("Select All performed on focused widget")
        else:
            logger.warning("No widget with selectAll() method is focused")

    def _show_emoji_dialog(self):
        """Показывает диалог выбора эмодзи."""
        logger.info("Action: Show Emoji Dialog")

        try:
            from app.ui.emoji_dialog import EmojiDialog
            dialog = EmojiDialog(self)

            # Подключаем сигнал выбора эмодзи
            if hasattr(dialog, "emoji_selected"):
                dialog.emoji_selected.connect(self._insert_emoji)

            # Показываем диалог
            dialog.exec()
            logger.info("Emoji dialog shown")
        except ImportError:
            logger.error("Could not import EmojiDialog")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                               tr("dialog.emoji.import_error", "Could not load emoji dialog."))

    def _insert_emoji(self, emoji):
        """Вставляет выбранный эмодзи в активный виджет."""
        logger.info(f"Inserting emoji: {emoji}")

        # Получаем активный виджет
        focused_widget = QApplication.focusWidget()

        # Пытаемся вставить эмодзи
        if hasattr(focused_widget, "insertPlainText") and callable(focused_widget.insertPlainText):
            focused_widget.insertPlainText(emoji)
            logger.info(f"Emoji {emoji} inserted into focused widget")
        elif hasattr(focused_widget, "setText") and callable(focused_widget.setText) and hasattr(focused_widget, "text"):
            current_text = focused_widget.text()
            focused_widget.setText(current_text + emoji)
            logger.info(f"Emoji {emoji} appended to text in focused widget")
        else:
            logger.warning("Could not insert emoji: no suitable widget focused")

    def _toggle_project_explorer(self, checked=None):
        """Показывает/скрывает проводник проекта."""
        logger.info(f"Action: Toggle Project Explorer {checked}")

        if hasattr(self, "project_explorer_dock"):
            # Если checked задан явно, устанавливаем нужную видимость
            if checked is not None:
                self.project_explorer_dock.setVisible(checked)
            # Иначе переключаем текущее состояние
            else:
                self.project_explorer_dock.setVisible(not self.project_explorer_dock.isVisible())

            # Обновляем состояние действия
            if hasattr(self, "toggle_project_explorer_action"):
                self.toggle_project_explorer_action.setChecked(self.project_explorer_dock.isVisible())

            logger.info(f"Project explorer visibility set to {self.project_explorer_dock.isVisible()}")
        else:
            logger.error("Cannot toggle project explorer: dock not found")

    def _toggle_chat(self, checked=None):
        """Показывает/скрывает чат."""
        logger.info(f"Action: Toggle Chat {checked}")

        if hasattr(self, "chat_dock"):
            # Если checked задан явно, устанавливаем нужную видимость
            if checked is not None:
                self.chat_dock.setVisible(checked)
            # Иначе переключаем текущее состояние
            else:
                self.chat_dock.setVisible(not self.chat_dock.isVisible())

            # Обновляем состояние действия
            if hasattr(self, "toggle_chat_action"):
                self.toggle_chat_action.setChecked(self.chat_dock.isVisible())

            logger.info(f"Chat visibility set to {self.chat_dock.isVisible()}")
        else:
            logger.error("Cannot toggle chat: dock not found")

    def _toggle_terminal(self, checked=None):
        """Показывает/скрывает терминал."""
        logger.info(f"Action: Toggle Terminal {checked}")

        if hasattr(self, "terminal_dock"):
            # Если checked задан явно, устанавливаем нужную видимость
            if checked is not None:
                self.terminal_dock.setVisible(checked)
            # Иначе переключаем текущее состояние
            else:
                self.terminal_dock.setVisible(not self.terminal_dock.isVisible())

            # Обновляем состояние действия
            if hasattr(self, "toggle_terminal_action"):
                self.toggle_terminal_action.setChecked(self.terminal_dock.isVisible())

            logger.info(f"Terminal visibility set to {self.terminal_dock.isVisible()}")
        else:
            logger.error("Cannot toggle terminal: dock not found")

    def _toggle_browser(self, checked=None):
        """Показывает/скрывает браузер."""
        logger.info(f"Action: Toggle Browser {checked}")

        if hasattr(self, "browser_dock") and hasattr(self.browser_dock, "web_view"):
            # Если checked задан явно, устанавливаем нужную видимость
            if checked is not None:
                self.browser_dock.setVisible(checked)
            # Иначе переключаем текущее состояние
            else:
                self.browser_dock.setVisible(not self.browser_dock.isVisible())

            # Обновляем состояние действия
            if hasattr(self, "toggle_browser_action"):
                self.toggle_browser_action.setChecked(self.browser_dock.isVisible())

            logger.info(f"Browser visibility set to {self.browser_dock.isVisible()}")
        else:
            logger.error("Cannot toggle browser: dock not found")

    # Modified to toggle the coding agent dialog visibility
    def _toggle_coding_agent(self, checked=None):
        logger.debug(f"Action: Toggle Coding Agent {checked}")
        if self.coding_agent_dialog and hasattr(self.coding_agent_dialog, "isVisible"):
            if checked is False or self.coding_agent_dialog.isVisible():
                # Скрываем окно и сохраняем состояние
                self.coding_agent_dialog.hide()
                self.settings.setValue("coding_agent_visible", False)
                logger.debug("Coding Agent window hidden")
            else:
                # Показываем окно
                self.show_coding_agent_dialog()
                logger.debug("Coding Agent window shown")
        else:
            # Open if it doesn't exist or has been deleted
            self.show_coding_agent_dialog()
            logger.debug("Coding Agent window created and shown")

    def reset_dock_layout(self):
        """Сбрасывает расположение панелей к виду по умолчанию."""
        logger.info("Action: Reset Dock Layout")

        # Восстанавливаем состояние окон
        try:
            # Сначала делаем все доки плавающими, чтобы избежать конфликтов
            if hasattr(self, "project_explorer_dock") and self.project_explorer_dock:
                self.project_explorer_dock.setFloating(True)
            if hasattr(self, "chat_dock") and self.chat_dock:
                self.chat_dock.setFloating(True)
            if hasattr(self, "terminal_dock") and self.terminal_dock:
                self.terminal_dock.setFloating(True)
            if hasattr(self, "browser_dock") and self.browser_dock:
                self.browser_dock.setFloating(True)

            # Затем располагаем их как нужно
            if hasattr(self, "project_explorer_dock") and self.project_explorer_dock:
                self.addDockWidget(Qt.LeftDockWidgetArea, self.project_explorer_dock)
                self.project_explorer_dock.setFloating(False)
                self.project_explorer_dock.setVisible(True)

            if hasattr(self, "chat_dock") and self.chat_dock:
                self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock)
                self.chat_dock.setFloating(False)
                self.chat_dock.setVisible(True)

            if hasattr(self, "terminal_dock") and self.terminal_dock:
                self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)
                self.terminal_dock.setFloating(False)
                self.terminal_dock.setVisible(False)  # По умолчанию скрыт

            if hasattr(self, "browser_dock") and self.browser_dock:
                self.addDockWidget(Qt.RightDockWidgetArea, self.browser_dock)
                self.browser_dock.setFloating(False)
                self.browser_dock.setVisible(False)  # По умолчанию скрыт

            # Обновляем состояние действий
            self._update_view_menu()
            logger.info("Dock layout reset to defaults")
        except Exception as e:
            logger.error(f"Error resetting dock layout: {e}")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                              tr("dialog.reset_layout.error", "Error resetting layout: {0}").format(str(e)))

    def _on_configure_agent(self):
        """Открывает диалог настройки агента."""
        logger.info("Action: Configure Agent")

        try:
            from app.ui.agent_config_dialog import AgentConfigDialog
            dialog = AgentConfigDialog(self)
            result = dialog.exec()

            if result == QDialog.Accepted:
                logger.info("Agent configuration saved")

                # Если нужно перезагрузить агента
                if self.agent:
                    try:
                        self.agent.reload_config()
                        logger.info("Agent configuration reloaded")
                    except Exception as e:
                        logger.error(f"Error reloading agent configuration: {e}")
        except ImportError:
            logger.error("Could not import AgentConfigDialog")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                               tr("dialog.agent_config.import_error", "Could not load agent configuration dialog."))
        except Exception as e:
            logger.error(f"Error showing agent configuration dialog: {e}")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                              tr("dialog.agent_config.error", "Error configuring agent: {0}").format(str(e)))

    def _open_url_in_browser(self):
        """Открывает URL в браузере."""
        logger.info("Action: Open URL in Browser")

        from PySide6.QtWidgets import QInputDialog
        from PySide6.QtCore import QUrl

        # Запрашиваем URL
        url, ok = QInputDialog.getText(self,
                                     tr("dialog.open_url.title", "Open URL"),
                                     tr("dialog.open_url.prompt", "Enter URL:"),
                                     text="https://")

        if ok and url:
            # Проверяем, есть ли браузер
            if hasattr(self, "browser_dock") and hasattr(self.browser_dock, "web_view"):
                # Показываем браузер
                self.browser_dock.setVisible(True)

                # Загружаем URL
                qurl = QUrl(url)
                if not qurl.scheme():
                    qurl = QUrl("https://" + url)

                self.browser_dock.web_view.load(qurl)
                logger.info(f"URL opened in browser: {url}")
            else:
                logger.error("Browser dock or web view not found")
                QMessageBox.warning(self, tr("dialog.error", "Error"),
                                   tr("dialog.open_url.no_browser", "Browser component not available."))
        else:
            logger.info("Open URL cancelled")

    def _show_flow_visualization(self):
        """Показывает визуализацию потока агента."""
        logger.info("Action: Show Flow Visualization")

        try:
            from app.ui.flow_visualization import FlowVisualizationDialog
            dialog = FlowVisualizationDialog(self)
            dialog.show()
            logger.info("Flow visualization shown")
        except ImportError:
            logger.error("Could not import FlowVisualizationDialog")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                               tr("dialog.flow_vis.import_error", "Could not load flow visualization."))
        except Exception as e:
            logger.error(f"Error showing flow visualization: {e}")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                              tr("dialog.flow_vis.error", "Error showing flow visualization: {0}").format(str(e)))

    def _run_ui_diagnostics(self):
        """Запускает диагностику UI."""
        logger.info("Action: Run UI Diagnostics")

        # Собираем информацию о состоянии UI
        results = []

        # Проверяем основные компоненты
        results.append(("MainWindow", True))

        # Проверяем, есть ли central_tabs
        has_central_tabs = hasattr(self, "central_tabs")
        results.append(("Central Tabs", has_central_tabs))

        # Проверяем доки
        has_project_explorer = hasattr(self, "project_explorer_dock") and self.project_explorer_dock is not None
        results.append(("Project Explorer", has_project_explorer))

        has_chat = hasattr(self, "chat_dock") and self.chat_dock is not None
        results.append(("Chat", has_chat))

        has_terminal = hasattr(self, "terminal_dock") and self.terminal_dock is not None
        results.append(("Terminal", has_terminal))

        has_browser = hasattr(self, "browser_dock") and self.browser_dock is not None
        results.append(("Browser", has_browser))

        # Проверяем меню
        has_menu_manager = hasattr(self, "menu_manager") and self.menu_manager is not None
        results.append(("Menu Manager", has_menu_manager))

        # Проверяем связь с агентом
        has_agent = hasattr(self, "agent") and self.agent is not None
        results.append(("Agent", has_agent))

        # Создаем отчет
        report = tr("dialog.diagnostics.results", "UI Diagnostics Results") + ":\n\n"
        for name, status in results:
            icon = "✓" if status else "✗"
            report += f"{icon} {name}\n"

        # Дополнительная информация
        report += "\n" + tr("dialog.diagnostics.additional", "Additional Information") + ":\n"
        report += f"Qt Version: {QApplication.instance().applicationVersion()}\n"
        report += f"Window Size: {self.width()}x{self.height()}\n"
        report += f"Theme: {ThemeManager.instance().get_current_visual_theme()}\n"
        report += f"Language: {JsonTranslationManager.instance().get_current_language()}\n"

        # Показываем отчет
        QMessageBox.information(self, tr("dialog.diagnostics.title", "UI Diagnostics"), report)
        logger.info("UI diagnostics completed")

    def _on_about(self):
        """Показывает диалог "О программе"."""
        logger.info("Action: About")

        about_text = """
        <h1>GopiAI</h1>
        <h3>Intelligent Coding Assistant</h3>
        <p>Version: 1.0</p>
        <p>&copy; 2023 GopiAI Team</p>
        <p>GopiAI is an intelligent coding assistant that helps you write better code faster.</p>
        """

        QMessageBox.about(self, tr("dialog.about.title", "About GopiAI"), about_text)
        logger.info("About dialog shown")

    def _on_documentation(self):
        """Открывает документацию."""
        logger.info("Action: Documentation")

        # Путь к документации
        docs_path = os.path.join(self.project_dir, "docs", "index.html")

        # Проверяем, существует ли документация
        if os.path.exists(docs_path):
            # Если есть браузер, показываем в нем
            if hasattr(self, "browser_dock") and hasattr(self.browser_dock, "web_view"):
                self.browser_dock.setVisible(True)
                self.browser_dock.web_view.load(QUrl.fromLocalFile(docs_path))
                logger.info(f"Documentation opened in browser: {docs_path}")
            else:
                # Пытаемся открыть через системный браузер
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl.fromLocalFile(docs_path))
                logger.info(f"Documentation opened in system browser: {docs_path}")
        else:
            # Документация не найдена
            logger.error(f"Documentation not found at {docs_path}")
            QMessageBox.warning(self, tr("dialog.error", "Error"),
                              tr("dialog.documentation.not_found", "Documentation not found."))

        logger.info("Documentation action completed")

    def _close_tab(self, index):
        """Закрывает указанную вкладку с проверкой на несохраненные изменения."""
        logger.info(f"Action: Close tab {index}")

        if not hasattr(self, "central_tabs"):
            logger.error("Cannot close tab: central_tabs not found")
            return

        if index < 0 or index >= self.central_tabs.count():
            logger.error(f"Cannot close tab: invalid index {index}")
            return

        # Получаем виджет вкладки
        tab_widget = self.central_tabs.widget(index)

        # Проверяем, есть ли несохраненные изменения
        if hasattr(tab_widget, "has_unsaved_changes") and callable(tab_widget.has_unsaved_changes) and tab_widget.has_unsaved_changes():
            # Спрашиваем пользователя о сохранении
            reply = QMessageBox.question(
                self,
                tr("dialog.unsaved_changes.title", "Unsaved changes"),
                tr("dialog.unsaved_changes.message", "There are unsaved changes. Do you want to save before closing?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                # Сохраняем изменения
                if hasattr(tab_widget, "save_file") and callable(tab_widget.save_file):
                    saved = tab_widget.save_file()
                    if not saved:
                        # Если сохранение не удалось, отменяем закрытие
                        return
                else:
                    logger.warning("Widget has unsaved changes but no save_file method")
            elif reply == QMessageBox.Cancel:
                # Отменяем закрытие
                return

        # Закрываем вкладку
        self.central_tabs.removeTab(index)

        # Освобождаем ресурсы, если нужно
        if hasattr(tab_widget, "close") and callable(tab_widget.close):
            tab_widget.close()

        logger.info(f"Tab {index} closed")

    def _show_tab_context_menu(self, pos):
        """Показывает контекстное меню для вкладки."""
        logger.info(f"Action: Tab context menu at {pos}")

        if not hasattr(self, "central_tabs"):
            logger.error("Cannot show tab context menu: central_tabs not found")
            return

        # Получаем индекс вкладки под курсором
        tab_bar = self.central_tabs.tabBar()
        index = tab_bar.tabAt(pos)

        if index == -1:  # Если курсор не над вкладкой
            logger.debug("No tab under cursor position")
            return

        # Создаем меню
        menu = QMenu(self)

        # Добавляем действия
        close_action = menu.addAction(tr("menu.tab.close", "Close"))
        close_others_action = menu.addAction(tr("menu.tab.close_others", "Close Others"))
        close_right_action = menu.addAction(tr("menu.tab.close_right", "Close Tabs to the Right"))
        menu.addSeparator()
        close_all_action = menu.addAction(tr("menu.tab.close_all", "Close All"))

        # Отключаем некоторые действия если только одна вкладка
        if self.central_tabs.count() <= 1:
            close_others_action.setEnabled(False)
            close_right_action.setEnabled(False)
            close_all_action.setEnabled(False)

        # Отключаем "Закрыть вкладки справа", если это последняя вкладка
        if index == self.central_tabs.count() - 1:
            close_right_action.setEnabled(False)

        # Показываем меню
        action = menu.exec(tab_bar.mapToGlobal(pos))

        # Обрабатываем действия
        if action == close_action:
            self._close_tab(index)
        elif action == close_others_action:
            self._close_other_tabs(index)
        elif action == close_right_action:
            self._close_tabs_to_right(index)
        elif action == close_all_action:
            self._close_all_tabs()

    def _show_project_tree_context_menu(self, position):
        """Показывает контекстное меню для дерева проекта."""
        logger.info(f"Action: Project tree context menu at {position}")

        if not hasattr(self, "project_explorer"):
            logger.error("Cannot show project tree context menu: project_explorer not found")
            return

        # Получаем индекс элемента под курсором
        if hasattr(self.project_explorer, "tree_view"):
            index = self.project_explorer.tree_view.indexAt(position)

            if not index.isValid():
                logger.debug("No valid item under cursor position")
                return

            # Перенаправляем вызов к методу в ProjectExplorer
            if hasattr(self.project_explorer, "_show_context_menu") and callable(self.project_explorer._show_context_menu):
                self.project_explorer._show_context_menu(position)
            else:
                logger.error("ProjectExplorer._show_context_menu method not found")
        else:
            logger.error("ProjectExplorer.tree_view not found")

    def _close_other_tabs(self, keep_index):
        """Закрывает все вкладки, кроме указанной."""
        logger.info(f"Action: Close other tabs except {keep_index}")

        if not hasattr(self, "central_tabs"):
            logger.error("Cannot close tabs: central_tabs not found")
            return

        if keep_index < 0 or keep_index >= self.central_tabs.count():
            logger.error(f"Cannot close other tabs: invalid index {keep_index}")
            return

        # Сначала закрываем вкладки с индексами больше keep_index
        i = self.central_tabs.count() - 1
        while i > keep_index:
            self._close_tab(i)
            i -= 1

        # Затем закрываем вкладки с индексами меньше keep_index
        # Поскольку индексы смещаются при удалении, keep_index теперь всегда 0
        while self.central_tabs.count() > 1:
            self._close_tab(0)

    def _close_tabs_to_right(self, start_index):
        """Закрывает все вкладки справа от указанной."""
        logger.info(f"Action: Close tabs to the right of {start_index}")

        if not hasattr(self, "central_tabs"):
            logger.error("Cannot close tabs: central_tabs not found")
            return

        if start_index < 0 or start_index >= self.central_tabs.count():
            logger.error(f"Cannot close tabs to right: invalid index {start_index}")
            return

        i = self.central_tabs.count() - 1
        while i > start_index:
            self._close_tab(i)
            i -= 1

    def _close_all_tabs(self):
        """Закрывает все вкладки."""
        logger.info("Action: Close all tabs")

        if not hasattr(self, "central_tabs"):
            logger.error("Cannot close tabs: central_tabs not found")
            return

        while self.central_tabs.count() > 0:
            self._close_tab(0)

    # Agent-related methods are now in app.logic.agent_setup
    # _handle_user_message, _handle_agent_response, update_agent_status
    # are called via functions from agent_setup, e.g., handle_user_message(self, message)

    # Example of how a UI element (e.g., a send button in chat_widget) would call the new handler:
    # In chat_widget.py, when send button is clicked:
    #   from app.logic.agent_setup import handle_user_message
    #   handle_user_message(QApplication.instance().main_window, self.input_field.text())
    # Note: This assumes main_window is accessible, e.g., stored on QApplication instance.
    # Or, if chat_widget has a direct reference to main_window:
    #   handle_user_message(self.main_window_ref, self.input_field.text())

    # The connection for chat_widget's send_message signal to _handle_user_message
    # will need to be updated if it was done in setup_central_widget or similar.
    # For now, we assume connect_agent_signals handles the agent's responses and status updates.
    # The MainWindow._handle_user_message was likely connected to a signal from the chat_widget.
    # This connection needs to be updated to call the new `handle_user_message` function.
    # Let's assume for now that the chat_widget itself will call this new function.
    # If `chat_widget.send_message.connect(self._handle_user_message)` was present,
    # it should be changed to `chat_widget.send_message.connect(lambda msg: handle_user_message(self, msg))`
    # or handled within the chat_widget.

    # The connection for chat_widget's send_message signal to _handle_user_message
    # will need to be updated if it was done in setup_central_widget or similar.
    # For now, we assume connect_agent_signals handles the agent's responses and status updates.
    # The MainWindow._handle_user_message was likely connected to a signal from the chat_widget.
    # This connection needs to be updated to call the new `handle_user_message` function.
    # Let's assume for now that the chat_widget itself will call this new function.
    # If `chat_widget.send_message.connect(self._handle_user_message)` was present,
    # it should be changed to `chat_widget.send_message.connect(lambda msg: handle_user_message(self, msg))`
    # or handled within the chat_widget.

    def _update_themes_menu(self):
        """Обновляет меню выбора темы в соответствии с текущей установленной темой."""
        try:
            logger.debug(f"Attempting to update themes menu.")

            # Проверяем, есть ли menu_manager
            if not hasattr(self, 'menu_manager'):
                logger.warning("menu_manager отсутствует в MainWindow, пропускаем обновление меню тем")
                return

            if not self.menu_manager or not hasattr(self.menu_manager, 'themes_menu'):
                logger.warning("self.menu_manager.themes_menu отсутствует, пропускаем обновление меню тем")
                return

            # Получаем текущую тему
            current_theme = self.theme_manager.current_theme

            # Обновляем отметку в меню
            for action in self.menu_manager.themes_menu.actions():
                if hasattr(action, 'theme_name'):
                    action.setChecked(action.theme_name == current_theme)

            logger.debug(f"Themes menu updated successfully. Current theme: {current_theme}")
        except Exception as e:
            logger.error(f"Error updating themes menu: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def open_theme_settings(self):
        # This method should open the theme settings dialog.
        # Assuming ThemeSettingsDialog is in app.ui.theme_settings_dialog
        try:
            from app.ui.theme_settings_dialog import ThemeSettingsDialog
            dialog = ThemeSettingsDialog(self)
            # Connect signals if needed, e.g., dialog.settings_applied.connect(self.on_theme_settings_applied)
            dialog.exec() # Use exec() for modal dialog
            logger.info("Theme settings dialog opened and closed.")
        except ImportError:
            logger.error("Could not import ThemeSettingsDialog.")
            QMessageBox.critical(self, tr("error.title", "Error"), tr("main_window.theme_settings.dialog_import_error", "Could not open theme settings."))
        except Exception as e:
            logger.error(f"Error opening theme settings dialog: {e}")
            QMessageBox.critical(self, tr("error.title", "Error"), f"{tr('main_window.theme_settings.open_error_prefix', 'Could not open theme settings:')} {e}")

    def _on_language_changed_event(self, language_code):
        """
        Обрабатывает событие смены языка приложения.
        """
        try:
            logging.info(f"_on_language_changed_event called with language {language_code}")
            from ..utils.translation import on_language_changed_event
            on_language_changed_event(self, language_code)
            logging.info("Translation completed")

            # Обновляем заголовок окна при смене языка
            self.setWindowTitle(tr("app.title", "GopiAI"))
        except Exception as e:
            logging.error(f"Error in _on_language_changed_event: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

    def _show_preferences_dialog(self):
        """Открывает диалог настроек."""
        try:
            from app.ui.preferences_dialog import PreferencesDialog
            dialog = PreferencesDialog(self)
            dialog.exec()
            logger.info("Preferences dialog closed")
        except ImportError:
            logger.error("Could not import PreferencesDialog.")
            QMessageBox.critical(self, tr("error.title", "Error"), tr("main_window.preferences.dialog_import_error", "Could not open preferences dialog."))
        except Exception as e:
            logger.error(f"Error opening preferences dialog: {e}")
            QMessageBox.critical(self, tr("error.title", "Error"), f"{tr('main_window.preferences.open_error_prefix', 'Could not open preferences:')} {e}")

    def _show_language_selector(self):
        """Открывает диалог выбора языка."""
        try:
            from app.ui.language_selector import LanguageSelector
            dialog = QDialog(self)
            dialog.setWindowTitle(tr("language_selector.dialog_title", "Выбор языка"))
            dialog.setMinimumWidth(300)

            layout = QVBoxLayout(dialog)
            language_selector = LanguageSelector(dialog)

            # Подключаем сигнал language_changed от LanguageSelector к обработчику
            # Этот сигнал будет отправлен, когда пользователь изменит язык через селектор
            language_selector.language_changed.connect(self._on_language_changed_event)

            layout.addWidget(language_selector)

            dialog.setLayout(layout)
            dialog.exec()
            logger.info("Language selector dialog closed")
        except ImportError:
            logger.error("Could not import LanguageSelector.")
            QMessageBox.critical(self, tr("error.title", "Error"), tr("main_window.language_selector.dialog_import_error", "Could not open language selector."))
        except Exception as e:
            logger.error(f"Error opening language selector: {e}")
            QMessageBox.critical(self, tr("error.title", "Error"), f"{tr('main_window.language_selector.open_error_prefix', 'Could not open language selector:')} {e}")

    def reset_layout(self):
        """Полностью сбрасывает интерфейс."""
        logger.info("Action: Reset Layout")
        # Сначала сбрасываем расположение доков
        self.reset_dock_layout()

        # Затем сбрасываем другие настройки интерфейса
        settings = QSettings(tr("app.title", "GopiAI"), "UI")
        settings.setValue("mainWindowState", None)
        settings.setValue("mainWindowGeometry", None)

        QMessageBox.information(self,
                              tr("dialog.reset_layout.title", "Layout Reset"),
                              tr("dialog.reset_layout.message", "Layout has been reset. Please restart the application for changes to take full effect."))
        logger.info("Layout reset completed")

    def _check_signals(self):
        """Запускает проверку сигналов приложения."""
        try:
            # Показываем уведомление о начале проверки
            self.statusBar().showMessage(tr("status.checking_signals", "Проверка сигналов..."), 3000)

            # Запускаем проверку сигналов
            unconnected_signals = check_main_window_signals(self)

            if not unconnected_signals:
                # Если неподключенных сигналов нет
                QMessageBox.information(
                    self,
                    tr("dialog.signals.title", "Проверка сигналов"),
                    tr("dialog.signals.no_issues", "Не обнаружено неподключенных сигналов.")
                )
            else:
                # Если есть неподключенные сигналы, показываем подробную информацию
                total_count = sum(len(signals) for signals in unconnected_signals.values())

                details = tr("dialog.signals.details", "Обнаружены следующие неподключенные сигналы:\n\n")
                for obj_path, signals in unconnected_signals.items():
                    details += f"✘ {obj_path}:\n"
                    for signal_info in signals:
                        details += f"   - {signal_info}\n"
                    details += "\n"

                # Создаем диалог с возможностью просмотра деталей
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle(tr("dialog.signals.title", "Проверка сигналов"))
                msg_box.setText(tr("dialog.signals.issues_found", f"Обнаружено {total_count} неподключенных сигналов."))
                msg_box.setDetailedText(details)

                # Добавляем кнопку для автоматического подключения
                auto_connect_button = msg_box.addButton(tr("dialog.signals.auto_connect", "Подключить автоматически"), QMessageBox.ActionRole)
                msg_box.addButton(QMessageBox.Ok)

                msg_box.exec()

                # Если была нажата кнопка автоматического подключения
                if msg_box.clickedButton() == auto_connect_button:
                    self._auto_connect_signals()

                # Обновляем статусбар
                self.statusBar().showMessage(
                    tr("status.signals_checked", f"Проверка завершена. Найдено {total_count} неподключенных сигналов."), 5000
                )
        except Exception as e:
            logger.error(f"Ошибка при проверке сигналов: {e}")
            QMessageBox.critical(
                self,
                tr("dialog.error", "Ошибка"),
                tr("dialog.signals.error", f"Ошибка при проверке сигналов: {str(e)}")
            )

    def _auto_connect_signals(self):
        """Автоматически подключает сигналы по шаблонам имен."""
        try:
            self.statusBar().showMessage(tr("status.auto_connect_signals", "Подключение сигналов..."), 3000)

            # Запускаем автоматическое подключение
            connected_count, connections_info = auto_connect_signals(self)

            if connected_count == 0:
                QMessageBox.information(
                    self,
                    tr("dialog.signals_auto.title", "Автоподключение сигналов"),
                    tr("dialog.signals_auto.no_connections", "Не удалось автоматически подключить сигналы.")
                )
            else:
                # Формируем подробную информацию о подключениях
                details = tr("dialog.signals_auto.details", f"Автоматически подключено {connected_count} сигналов:\n\n")
                for obj_path, signals in connections_info.items():
                    details += f"✓ {obj_path}:\n"
                    for signal_name in signals:
                        details += f"   - {signal_name}\n"
                    details += "\n"

                # Показываем информацию о подключениях
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle(tr("dialog.signals_auto.title", "Автоподключение сигналов"))
                msg_box.setText(tr("dialog.signals_auto.connections_made", f"Автоматически подключено {connected_count} сигналов."))
                msg_box.setDetailedText(details)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec()

                self.statusBar().showMessage(
                    tr("status.signals_auto_connected", f"Подключено {connected_count} сигналов"), 5000
                )
        except Exception as e:
            logger.error(f"Ошибка при автоматическом подключении сигналов: {e}")
            QMessageBox.critical(
                self,
                tr("dialog.error", "Ошибка"),
                tr("dialog.signals_auto.error", f"Ошибка при автоматическом подключении сигналов: {str(e)}")
            )

    def _toggle_maximized(self):
        """Переключает окно между развернутым и обычным состояниями."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна."""
        super().resizeEvent(event)
        # Если есть window_controls, обновляем его состояние
        if hasattr(self, "window_controls") and self.isMaximized():
            self.window_controls.update_maximized_state(True)
        elif hasattr(self, "window_controls"):
            self.window_controls.update_maximized_state(False)

    def changeEvent(self, event):
        """Обрабатывает изменение состояния окна."""
        if event.type() == QEvent.Type.WindowStateChange:
            # Если окно было развернуто или восстановлено, обновляем состояние кнопок
            if hasattr(self, "window_controls"):
                self.window_controls.update_maximized_state(self.isMaximized())
        super().changeEvent(event)

    def _setup_help_menu(self, menu_bar):
        """Устанавливает меню справки."""
        help_menu = menu_bar.addMenu(tr("&Help"))
        # Пункт меню "О программе"
        about_action = QAction(tr("&About"), self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

        # Добавляем подменю для иконок если доступны более красивые иконки
        from app.ui.icon_manager import show_icon_browser

        # Создаем иконки для пунктов меню с использованием современных иконок
        icon_menu = help_menu.addMenu(tr("Icons"))
        icon_menu.setIcon(self.icon_manager.get_modern_icon("palette", color="#3498DB"))

        # Пункт для открытия браузера иконок
        browse_icons_action = QAction(self.icon_manager.get_modern_icon("icons", color="#3498DB"), tr("Browse Icons"), self)
        browse_icons_action.triggered.connect(self._show_icon_browser)
        icon_menu.addAction(browse_icons_action)

        # Пункт для отображения информации о доступных наборах иконок
        icon_info_action = QAction(self.icon_manager.get_modern_icon("info", color="#3498DB"), tr("Icon Sets Info"), self)
        icon_info_action.triggered.connect(self._show_icon_info)
        icon_menu.addAction(icon_info_action)

    def _show_icon_browser(self):
        """Открывает браузер иконок."""
        from app.ui.icon_manager import show_icon_browser

        def on_icon_selected(icon_name):
            """Обрабатывает выбор иконки."""
            logger.info(f"Выбрана иконка: {icon_name}")
            QMessageBox.information(self, tr("Icon Selected"),
                                   tr("Selected icon: {}").format(icon_name))

        dialog = show_icon_browser(self.icon_manager, on_icon_selected)
        dialog.exec()

    def _show_icon_info(self):
        """Показывает информацию о доступных наборах иконок."""
        icon_sets = self.icon_manager.get_available_icon_sets()

        info_text = tr("Available icon sets:") + "\n\n"

        for set_name, icons in icon_sets.items():
            display_name = set_name.replace('_', ' ').title()
            info_text += f"{display_name}: {len(icons)} icons\n"

        QMessageBox.information(self, tr("Icon Sets Information"), info_text)
