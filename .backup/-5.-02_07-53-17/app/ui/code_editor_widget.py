import os
from pathlib import Path

from PySide6.QtCore import QMimeData, QSize, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QFontDatabase,
    QKeyEvent,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
    QTextOption,
    QCursor,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from app.logger import logger
from app.ui.code_editor import CodeEditor
from app.ui.i18n.translator import tr

# Удаляем get_icon, IconManager импортируем только для проверки типа, если нужно
from app.ui.icon_adapter import get_icon


class MultiEditorWidget(QWidget):
    """Виджет с несколькими вкладками редактора кода."""

    file_changed = Signal(str)
    progress_update = Signal(str)

    # Новые сигналы для интеграции с чатом
    send_to_chat = Signal(str)
    code_check_requested = Signal(str)
    code_run_requested = Signal(str)

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.open_files = {}  # Хранит пути к открытым файлам

        # Создаем основной вертикальный лейаут
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем сплиттер для редактора и консоли
        self.splitter = QSplitter(Qt.Vertical)

        # Создаем панель инструментов
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)

        # Кнопки файловых операций
        self.new_file_action = QAction(
            get_icon("file"), tr("editor.new_file", "New File"), self
        )  # Используем file
        self.new_file_action.triggered.connect(self.new_file)
        self.toolbar.addAction(self.new_file_action)

        self.open_file_action = QAction(
            get_icon("folder_open"),
            tr("editor.open_file", "Open File"),
            self,
        )  # Используем folder_open
        self.open_file_action.triggered.connect(self.open_file)
        self.toolbar.addAction(self.open_file_action)

        self.save_file_action = QAction(
            get_icon("save"),
            tr("editor.save_file", "Save File"),
            self,
        )
        self.save_file_action.triggered.connect(self.save_file)
        self.toolbar.addAction(self.save_file_action)

        self.save_as_action = QAction(
            get_icon("save"), tr("editor.save_as", "Save As"), self
        )
        self.save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(self.save_as_action)

        self.toolbar.addSeparator()

        # Кнопки редактирования
        self.undo_action = QAction(get_icon("undo"), tr("editor.undo", "Undo"), self)
        self.undo_action.triggered.connect(self._undo)
        self.toolbar.addAction(self.undo_action)

        self.redo_action = QAction(get_icon("redo"), tr("editor.redo", "Redo"), self)
        self.redo_action.triggered.connect(self._redo)
        self.toolbar.addAction(self.redo_action)

        self.toolbar.addSeparator()

        # Кнопки для работы с кодом
        self.run_action = QAction(get_icon("play"), tr("editor.run", "Run"), self)
        self.run_action.triggered.connect(self.run_current_file)
        self.toolbar.addAction(self.run_action)

        self.search_action = QAction(
            get_icon("search"), tr("editor.search", "Search"), self
        )
        self.search_action.triggered.connect(self.search_in_file)
        self.toolbar.addAction(self.search_action)

        self.toolbar.addSeparator()

        # Панель поиска (скрыта по умолчанию)
        self.search_panel = QWidget()
        search_layout = QHBoxLayout(self.search_panel)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            tr("editor.search.placeholder", "Search...")
        )
        self.search_input.returnPressed.connect(self._search_next)
        search_layout.addWidget(self.search_input)

        self.search_prev_button = QPushButton(get_icon("arrow_up"), "")
        self.search_prev_button.setToolTip(tr("editor.search.prev", "Find Previous"))
        self.search_prev_button.clicked.connect(self._search_prev)
        search_layout.addWidget(self.search_prev_button)

        self.search_next_button = QPushButton(get_icon("arrow_down"), "")
        self.search_next_button.setToolTip(tr("editor.search.next", "Find Next"))
        self.search_next_button.clicked.connect(self._search_next)
        search_layout.addWidget(self.search_next_button)

        self.search_close_button = QPushButton(get_icon("close"), "")
        self.search_close_button.setToolTip(tr("editor.search.close", "Close"))
        self.search_close_button.clicked.connect(
            lambda: self.search_panel.setVisible(False)
        )
        search_layout.addWidget(self.search_close_button)

        # Скрываем панель поиска по умолчанию
        self.search_panel.setVisible(False)

        # Кнопки для интеграции с чатом
        self.send_to_chat_action = QAction(
            get_icon("chat"), tr("editor.send_to_chat", "Send to Chat"), self
        )
        self.send_to_chat_action.triggered.connect(self.send_selected_to_chat)
        self.toolbar.addAction(self.send_to_chat_action)

        self.check_code_action = QAction(
            get_icon("debug"), tr("editor.check_code", "Check Code"), self
        )
        self.check_code_action.triggered.connect(self.check_selected_code)
        self.toolbar.addAction(self.check_code_action)

        self.run_code_action = QAction(
            get_icon("terminal"), tr("editor.run_in_terminal", "Run in Terminal"), self
        )
        self.run_code_action.triggered.connect(self.run_selected_code)
        self.toolbar.addAction(self.run_code_action)

        # Добавляем панель инструментов в лейаут
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.search_panel)

        # Создаем контейнер для редактора
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # Можно закрывать вкладки отдельно
        self.tabs.setMovable(True)  # Можно перемещать вкладки
        self.tabs.setContextMenuPolicy(
            Qt.CustomContextMenu
        )  # Добавить контекстное меню для вкладок

        # Подключаем обработчик контекстного меню
        self.tabs.customContextMenuRequested.connect(self._show_tab_context_menu)

        # Подключаем обработчик закрытия вкладок
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.editor_layout.addWidget(self.tabs)

        # Добавляем контейнер редактора в сплиттер
        self.splitter.addWidget(self.editor_container)

        # Создаем консоль вывода
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText(
            tr("editor.console.placeholder", "Output will appear here...")
        )

        # Добавляем консоль в сплиттер
        self.splitter.addWidget(self.console)

        # Устанавливаем размеры сплиттера
        self.splitter.setSizes([700, 300])

        # Добавляем сплиттер в основной лейаут
        self.layout.addWidget(self.splitter)

        # Создаем первую вкладку
        self.add_new_tab()

        # Устанавливаем политику размеров
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Активируем поддержку эмодзи
        self.ensure_emoji_support()

    def add_new_tab(self, file_path=None):
        """Добавляет новую вкладку редактора кода."""
        # Создаем редактор кода
        editor = CodeEditor(self)

        logger.info(f"Creating new tab with file path: {file_path}")

        # Подключаем сигналы редактора к обработчикам
        editor.send_to_chat.connect(self.send_to_chat.emit)
        editor.check_code.connect(self.code_check_requested.emit)
        editor.run_code.connect(self.code_run_requested.emit)

        # Устанавливаем атрибут для хранения пути к файлу
        editor.file_path = file_path

        # Если передан путь к файлу, загружаем его содержимое
        if file_path and os.path.isfile(file_path):
            try:
                logger.info(f"Loading file content from {file_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    editor.setPlainText(f.read())

                # Обновляем словарь открытых файлов
                self.open_files[file_path] = editor

                # Устанавливаем заголовок вкладки как имя файла
                tab_title = os.path.basename(file_path)

                # Определяем иконку на основе файла
                file_name = os.path.basename(file_path)
                suffix = Path(file_path).suffix.lower().lstrip(".")

                # Вызываем _get_file_icon_name с расширением или для специальных файлов - с полным именем
                if file_name.lower() in [
                    "makefile",
                    "dockerfile",
                    "readme.md",
                    ".gitignore",
                    ".gitattributes",
                ] or file_name.lower().startswith("license"):
                    icon_name = self._get_file_icon_name(file_name)
                else:
                    icon_name = self._get_file_icon_name(suffix)

                icon = get_icon(icon_name)
                logger.info(f"Using icon: {icon_name} for file {file_name}")
            except Exception as e:
                logger.error(f"Ошибка при открытии файла: {e}")
                QMessageBox.critical(
                    self,
                    tr("editor.error", "Ошибка"),
                    tr(
                        "editor.error.open_file", "Ошибка при открытии файла: {error}"
                    ).format(error=str(e)),
                )
                tab_title = tr("editor.new_tab", "Новый файл")
                icon = get_icon("file")
        else:
            # Для новой вкладки без файла
            tab_title = tr("editor.new_tab", "Новый файл")
            icon = get_icon("file")
            logger.info("Created empty new tab")

        # Добавляем вкладку с иконкой
        index = self.tabs.addTab(editor, icon, tab_title)
        self.tabs.setCurrentIndex(index)
        logger.info(f"Added tab at index {index} with title {tab_title}")

        # Сигнализируем о новом файле
        if file_path:
            self.file_changed.emit(file_path)

        return editor

    def _get_file_icon_name(self, suffix):
        """Возвращает имя иконки для файла на основе его расширения или имени файла."""
        # Словарь соответствия расширений и имен иконок
        icon_mapping = {
            # Текстовые/код
            "py": "python_file",
            "js": "js_file",
            "ts": "file-code",
            "jsx": "file-code",
            "tsx": "file-code",
            "html": "html_file",
            "htm": "html_file",
            "css": "css_file",
            "scss": "css_file",
            "sass": "css_file",
            "less": "css_file",
            "json": "json",
            "xml": "file-code",
            "yml": "file-code",
            "yaml": "file-code",
            "md": "markdown",
            "txt": "text_file",
            "csv": "spreadsheet",
            "log": "text_file",
            "sql": "database",
            "sh": "terminal",
            "bat": "terminal",
            "ps1": "terminal",
            "c": "file-code",
            "cpp": "file-code",
            "h": "file-code",
            "hpp": "file-code",
            "java": "file-code",
            "php": "file-code",
            "rb": "file-code",
            "go": "file-code",
            "rs": "file-code",
            "swift": "file-code",
            "kt": "file-code",
            # Изображения
            "jpg": "image_file",
            "jpeg": "image_file",
            "png": "image_file",
            "gif": "image_file",
            "bmp": "image_file",
            "svg": "image_file",
            "ico": "image_file",
            "webp": "image_file",
            # Документы
            "doc": "document",
            "docx": "document",
            "xls": "spreadsheet",
            "xlsx": "spreadsheet",
            "ppt": "file-text",
            "pptx": "file-text",
            "pdf": "pdf",
            # Архивы
            "zip": "archive",
            "rar": "archive",
            "7z": "archive",
            "tar": "archive",
            "gz": "archive",
            "tgz": "archive",
            # Другие
            "mp3": "music",
            "wav": "music",
            "ogg": "music",
            "mp4": "video",
            "avi": "video",
            "mov": "video",
            "mkv": "video",
            "exe": "package",
            "msi": "package",
            "dll": "package",
            "so": "package",
            # Конфигурация и настройки
            "ini": "settings",
            "cfg": "settings",
            "conf": "settings",
            "gitignore": "git",
            "gitattributes": "git",
            "env": "settings",
        }

        # Проверяем специальные имена файлов
        filename = suffix.lower() if isinstance(suffix, str) else ""

        # Проверяем точные соответствия специальных файлов
        if filename in ["makefile", "dockerfile"]:
            return "file-code"
        if filename == "readme.md":
            return "markdown"
        if filename in [".gitignore", ".gitattributes"]:
            return "git"

        # Проверяем файлы, начинающиеся с определенного префикса
        if filename.startswith("license"):
            return "file-text"

        # Если это обычное расширение, ищем в словаре
        if suffix in icon_mapping:
            return icon_mapping[suffix]

        # Если не нашли соответствий, возвращаем стандартную иконку файла
        return "file"

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        editor = self.tabs.widget(index)

        # Проверяем, есть ли несохраненные изменения
        if editor and editor.document().isModified():
            reply = QMessageBox.question(
                self,
                tr("editor.unsaved_changes", "Несохраненные изменения"),
                tr("editor.save_before_close", "Сохранить изменения перед закрытием?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        # Удаляем запись из словаря открытых файлов
        if editor and hasattr(editor, "file_path") and editor.file_path:
            if editor.file_path in self.open_files:
                del self.open_files[editor.file_path]

        # Закрываем вкладку
        self.tabs.removeTab(index)

        # Если не осталось вкладок, создаем новую
        if self.tabs.count() == 0:
            self.add_new_tab()

    def on_tab_changed(self, index):
        """Обрабатывает переключение между вкладками."""
        if index >= 0:
            editor = self.tabs.widget(index)
            if editor and hasattr(editor, "file_path") and editor.file_path:
                self.file_changed.emit(editor.file_path)

    def new_file(self):
        """Создает новый файл."""
        self.add_new_tab()

    def open_file(self):
        """Открывает диалог выбора файла и загружает выбранный файл."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("editor.open_file_dialog", "Открыть файл"),
            "",
            tr(
                "editor.file_filter",
                "Текстовые файлы (*.txt *.py *.js *.html *.css *.json *.xml);;Все файлы (*)",
            ),
        )

        logger.info(f"User selected file to open: {file_path}")
        if file_path:
            # Проверяем, может быть файл уже открыт
            if file_path in self.open_files:
                # Переключаемся на вкладку с уже открытым файлом
                editor = self.open_files[file_path]
                index = self.tabs.indexOf(editor)
                if index >= 0:
                    logger.info(f"File already open, switching to tab index {index}")
                    self.tabs.setCurrentIndex(index)
                    return
                else:
                    logger.warning(
                        f"File {file_path} marked as open but tab not found!"
                    )

            # Открываем новую вкладку с файлом
            logger.info(f"Opening new tab with file: {file_path}")
            self.add_new_tab(file_path)

    def save_file(self):
        """Сохраняет текущий файл."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            logger.warning("Cannot save file: no active tab")
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            logger.warning("Cannot save file: no editor widget in current tab")
            return

        # Если файл еще не сохранен, вызываем диалог сохранения
        if not hasattr(editor, "file_path") or not editor.file_path:
            logger.info("No file path defined, redirecting to save_file_as")
            self.save_file_as()
            return

        try:
            # Сохраняем содержимое в файл
            logger.info(f"Saving file: {editor.file_path}")
            with open(editor.file_path, "w", encoding="utf-8") as f:
                content = editor.toPlainText()
                f.write(content)
                logger.debug(f"Written {len(content)} characters to file")

            # Обновляем флаг модификации
            editor.document().setModified(False)

            # Обновляем заголовок вкладки
            tab_title = os.path.basename(editor.file_path)
            self.tabs.setTabText(current_index, tab_title)
            logger.info(f"File saved successfully: {editor.file_path}")

            # Сигнализируем об успешном сохранении
            self.progress_update.emit(
                tr("editor.file_saved", "Файл сохранен: {path}").format(
                    path=editor.file_path
                )
            )

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                tr("editor.error", "Ошибка"),
                tr(
                    "editor.error.save_file", "Ошибка при сохранении файла: {error}"
                ).format(error=str(e)),
            )

    def save_file_as(self):
        """Сохраняет текущий файл под новым именем."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            logger.warning("Cannot save file as: no active tab")
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            logger.warning("Cannot save file as: no editor widget in current tab")
            return

        # Показываем диалог сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("editor.save_as_dialog", "Сохранить как"),
            "",
            tr(
                "editor.file_filter",
                "Текстовые файлы (*.txt *.py *.js *.html *.css *.json *.xml);;Все файлы (*)",
            ),
        )

        if not file_path:
            logger.info("Save As dialog was cancelled by user")
            return

        try:
            # Сохраняем содержимое в файл
            logger.info(f"Saving file as: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                content = editor.toPlainText()
                f.write(content)
                logger.debug(f"Written {len(content)} characters to file")

            # Обновляем путь к файлу в редакторе
            old_path = getattr(editor, "file_path", None)
            editor.file_path = file_path
            logger.info(f"File path updated from {old_path} to {file_path}")

            # Обновляем словарь открытых файлов
            if old_path in self.open_files:
                del self.open_files[old_path]
            self.open_files[file_path] = editor
            logger.debug("Updated open_files dictionary")

            # Обновляем флаг модификации
            editor.document().setModified(False)

            # Обновляем заголовок вкладки
            tab_title = os.path.basename(file_path)
            self.tabs.setTabText(current_index, tab_title)
            logger.info(f"Tab title updated to {tab_title}")

            # Обновляем иконку вкладки если нужно
            suffix = Path(file_path).suffix.lower().lstrip(".")
            icon_name = self._get_file_icon_name(suffix)
            icon = get_icon(icon_name)
            self.tabs.setTabIcon(current_index, icon)
            logger.debug(f"Tab icon updated to {icon_name}")

            # Сигнализируем об успешном сохранении
            self.progress_update.emit(
                tr("editor.file_saved", "Файл сохранен: {path}").format(path=file_path)
            )
            self.file_changed.emit(file_path)
            logger.info(f"File saved successfully as: {file_path}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла как: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                tr("editor.error", "Ошибка"),
                tr(
                    "editor.error.save_file", "Ошибка при сохранении файла: {error}"
                ).format(error=str(e)),
            )

    def run_current_file(self):
        """Запускает текущий файл."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor or not hasattr(editor, "file_path") or not editor.file_path:
            QMessageBox.information(
                self,
                tr("editor.info", "Информация"),
                tr("editor.save_before_run", "Сохраните файл перед запуском."),
            )
            return

        # Сохраняем файл перед запуском
        if editor.document().isModified():
            self.save_file()

        # Очищаем консоль
        self.console.clear()

        # Получаем расширение файла
        file_ext = os.path.splitext(editor.file_path)[1].lower()

        # В реальном приложении здесь будет логика запуска файла
        # в зависимости от расширения
        self.console.append(
            tr("editor.running_file", "Запуск файла: {path}").format(
                path=editor.file_path
            )
        )
        self.console.append("-------------------------")

        # Простая имитация запуска
        if file_ext == ".py":
            self.console.append(tr("editor.python_run", "Запуск Python файла..."))
            # Здесь будет реальный запуск Python-скрипта
        elif file_ext in [".js", ".html"]:
            self.console.append(tr("editor.web_run", "Запуск веб-файла..."))
            # Здесь будет открытие в браузере или запуск JavaScript
        else:
            self.console.append(
                tr("editor.generic_run", "Запуск файла с расширением: {ext}").format(
                    ext=file_ext
                )
            )

        self.progress_update.emit(
            tr("editor.file_executed", "Файл выполнен: {path}").format(
                path=editor.file_path
            )
        )

    def search_in_file(self):
        """Ищет текст в текущем файле."""
        search_text = self.search_input.text()
        if not search_text:
            return

        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        # Выполняем поиск
        cursor = editor.textCursor()
        position = cursor.position()  # Сохраняем текущую позицию

        # Начинаем поиск с текущей позиции
        found = editor.find(search_text)

        # Если не нашли с текущей позиции, начинаем сначала
        if not found:
            cursor.setPosition(0)
            editor.setTextCursor(cursor)
            found = editor.find(search_text)

        if not found:
            self.progress_update.emit(
                tr("editor.search_not_found", "Текст '{text}' не найден").format(
                    text=search_text
                )
            )
        else:
            self.progress_update.emit(
                tr("editor.search_found", "Найдено: '{text}'").format(text=search_text)
            )

    def get_current_file(self):
        """Возвращает путь к текущему открытому файлу."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return None

        editor = self.tabs.widget(current_index)
        if not editor or not hasattr(editor, "file_path"):
            return None

        return editor.file_path

    def get_open_files(self):
        """Возвращает список путей к открытым файлам."""
        return list(self.open_files.keys())

    def add_console_message(self, message, error=False):
        """Добавляет сообщение в консоль."""
        if error:
            self.console.append(f"<span style='color: red;'>{message}</span>")
        else:
            self.console.append(message)

        # Прокручиваем консоль вниз
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def _show_tab_context_menu(self, position):
        """Показывает контекстное меню для вкладок."""
        index = self.tabs.tabBar().tabAt(position)
        if index < 0:
            return

        # Создаем контекстное меню
        menu = QMenu(self)

        # Действие "Закрыть"
        close_action = QAction(tr("dialogs.close", "Close"), self)
        close_action.triggered.connect(lambda: self.close_tab(index))
        menu.addAction(close_action)

        # Действие "Закрыть все"
        close_all_action = QAction(tr("dialogs.close_all", "Close All Tabs"), self)
        close_all_action.triggered.connect(self._close_all_tabs)
        menu.addAction(close_all_action)

        # Действие "Закрыть другие"
        close_others_action = QAction(
            tr("dialogs.close_others", "Close Other Tabs"), self
        )
        close_others_action.triggered.connect(lambda: self._close_other_tabs(index))
        menu.addAction(close_others_action)

        # Добавляем разделитель
        menu.addSeparator()

        # Действия для работы с кодом (если есть выделенный текст)
        editor = self.tabs.widget(index)
        if editor and editor.textCursor().hasSelection():
            # Отправить код в чат
            send_to_chat_action = QAction(
                tr("editor.send_to_chat", "Send to Chat"), self
            )
            send_to_chat_action.triggered.connect(self.send_selected_to_chat)
            menu.addAction(send_to_chat_action)

            # Проверить код
            check_code_action = QAction(tr("editor.check_code", "Check Code"), self)
            check_code_action.triggered.connect(self.check_selected_code)
            menu.addAction(check_code_action)

            # Запустить код
            run_code_action = QAction(
                tr("editor.run_selected", "Run Selected Code"), self
            )
            run_code_action.triggered.connect(self.run_selected_code)
            menu.addAction(run_code_action)

        # Добавляем разделитель и пункт для вставки эмодзи
        menu.addSeparator()

        # Импортируем функцию для получения Lucide иконок
        from app.ui.lucide_icon_manager import get_lucide_icon

        # Добавляем действие для вставки эмодзи
        emoji_action = QAction(tr("menu.emoji", "Insert Emoji"), self)
        emoji_action.setIcon(get_lucide_icon("smile"))

        # Получаем глобальную позицию для отображения диалога
        global_pos = self.tabs.tabBar().mapToGlobal(position)

        # Подключаем действие к методу insertEmoji текущего редактора
        if editor:
            emoji_action.triggered.connect(
                lambda: self._show_emoji_dialog(editor, global_pos)
            )
        menu.addAction(emoji_action)

        # Показываем меню в позиции курсора
        menu.exec_(self.tabs.tabBar().mapToGlobal(position))

    def _show_emoji_dialog(self, editor, position=None):
        """Показывает диалог выбора эмодзи.

        Args:
            editor: Редактор, в который будет вставлен эмодзи
            position (QPoint, optional): Позиция для отображения диалога
        """
        if not editor:
            return

        try:
            from app.ui.emoji_dialog import EmojiDialog

            # Создаем диалог эмодзи
            dialog = EmojiDialog(self)

            # Подключаем сигнал для вставки эмодзи в редактор
            dialog.emoji_selected.connect(editor.insertPlainText)

            # Получаем позицию курсора, если не передана
            if not position:
                position = QCursor.pos()

            dialog_size = dialog.sizeHint()
            screen_geometry = QApplication.primaryScreen().geometry()

            # Расчитываем позицию так, чтобы диалог не выходил за пределы экрана
            x = min(position.x(), screen_geometry.width() - dialog_size.width())
            y = min(position.y(), screen_geometry.height() - dialog_size.height())

            dialog.move(x, y)

            # Устанавливаем флаг, чтобы диалог оставался поверх других окон - больше не нужно
            # dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

            # Показываем диалог
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing emoji dialog: {e}")

    def send_selected_to_chat(self):
        """Отправляет выделенный текст в чат."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.progress_update.emit(tr("editor.no_selected_text", "No text selected"))
            return

        self.send_to_chat.emit(selected_text)
        self.progress_update.emit(
            tr("editor.sent_to_chat", "Selected code sent to chat")
        )

    def check_selected_code(self):
        """Отправляет выделенный код на проверку."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.progress_update.emit(tr("editor.no_selected_text", "No text selected"))
            return

        self.code_check_requested.emit(selected_text)
        self.progress_update.emit(
            tr("editor.code_check_requested", "Code check requested")
        )

    def run_selected_code(self):
        """Запускает выделенный код."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text:
            self.progress_update.emit(tr("editor.no_selected_text", "No text selected"))
            return

        self.code_run_requested.emit(selected_text)
        self.progress_update.emit(
            tr("editor.code_run_requested", "Code execution requested")
        )

    def _close_all_tabs(self):
        """Закрывает все вкладки."""
        count = self.tabs.count()
        for i in range(count - 1, -1, -1):
            self.close_tab(i)

    def _close_other_tabs(self, keep_index):
        """Закрывает все вкладки, кроме указанной."""
        # Получаем список индексов для закрытия в обратном порядке
        indices_to_close = [i for i in range(self.tabs.count()) if i != keep_index]
        indices_to_close.sort(reverse=True)

        # Закрываем каждую вкладку
        for idx in indices_to_close:
            self.close_tab(idx)

    def insert_code(self, code: str):
        """
        Вставляет код из чата в текущий редактор.

        Args:
            code: Текст кода для вставки
        """
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            # Если нет активной вкладки, создаем новую
            editor = self.add_new_tab()
        else:
            editor = self.tabs.widget(current_index)

        if not editor:
            return

        # Вставляем код в позицию курсора
        cursor = editor.textCursor()
        cursor.insertText(code)

        # Обновляем курсор в редакторе
        editor.setTextCursor(cursor)

        # Фокусируемся на редакторе
        editor.setFocus()

        # Уведомляем о вставке
        self.progress_update.emit(tr("editor.code_inserted", "Code inserted from chat"))

    def ensure_emoji_support(self):
        """Обеспечивает поддержку эмодзи в редакторе кода."""
        try:
            # Получаем текущий редактор
            if hasattr(self, "editor") and self.editor:
                # Проверяем шрифты, которые поддерживают эмодзи
                emoji_fonts = [
                    "Segoe UI Emoji",
                    "Noto Color Emoji",
                    "Apple Color Emoji",
                    "Segoe UI Symbol",
                    "Arial Unicode MS",
                ]

                # Находим доступные шрифты в системе
                available_fonts = QFontDatabase().families()

                # Ищем подходящий шрифт с поддержкой эмодзи
                fallback_font = None
                for emoji_font in emoji_fonts:
                    if any(
                        f == emoji_font or f.startswith(emoji_font)
                        for f in available_fonts
                    ):
                        fallback_font = emoji_font
                        break

                # Если нашли подходящий шрифт, устанавливаем его как запасной
                if fallback_font:
                    try:
                        # Устанавливаем запасной шрифт для документа
                        option = self.editor.document().defaultTextOption()
                        current_fonts = (
                            option.fontFamilies()
                            if hasattr(option, "fontFamilies")
                            and callable(option.fontFamilies)
                            else []
                        )

                        # Добавляем эмодзи-шрифт, если его еще нет в списке шрифтов
                        if not current_fonts or fallback_font not in current_fonts:
                            new_fonts = list(current_fonts) + [fallback_font]
                            if hasattr(option, "setFontFamilies") and callable(
                                option.setFontFamilies
                            ):
                                option.setFontFamilies(new_fonts)
                                self.editor.document().setDefaultTextOption(option)
                                logger.info(
                                    f"Added emoji font fallback: {fallback_font}"
                                )
                    except Exception as e:
                        logger.error(
                            f"Error setting up emoji font in CodeEditorWidget: {e}"
                        )
                else:
                    logger.warning(
                        "No appropriate emoji font found for CodeEditorWidget."
                    )
        except Exception as e:
            logger.error(f"Error in ensure_emoji_support: {e}")

    def insertEmoji(self, emoji):
        """Вставляет эмодзи в текущую позицию курсора."""
        if self.editor:
            # Вставляем эмодзи
            self.editor.insertPlainText(emoji)

            # Обновляем редактор, чтобы отобразить эмодзи
            self.editor.update()

            # Устанавливаем фокус обратно на редактор
            self.editor.setFocus()

            logger.info(f"Inserted emoji {emoji} into CodeEditorWidget")

            # Помечаем содержимое как измененное
            self.content_modified = True
            self.content_changed.emit()

    def _redo(self):
        """Повторяет последнее отмененное действие в текущем редакторе."""
        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, "redo"):
            current_tab.redo()
        else:
            logger.warning("Текущая вкладка не поддерживает redo")

    def _undo(self):
        """Отменяет последнее действие в текущем редакторе."""
        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, "undo"):
            current_tab.undo()
        else:
            logger.warning("Текущая вкладка не поддерживает undo")

    def _search_next(self):
        """Находит следующее вхождение текста в текущем редакторе."""
        search_text = self.search_input.text()
        if not search_text:
            return

        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, "find"):
            found = current_tab.find(search_text)
            if not found:
                # Если не нашли, начинаем поиск сначала
                cursor = current_tab.textCursor()
                cursor.movePosition(cursor.Start)
                current_tab.setTextCursor(cursor)
                current_tab.find(search_text)
        else:
            logger.warning("Текущая вкладка не поддерживает поиск")

    def _search_prev(self):
        """Находит предыдущее вхождение текста в текущем редакторе."""
        search_text = self.search_input.text()
        if not search_text:
            return

        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, "find"):
            found = current_tab.find(search_text, QTextDocument.FindBackward)
            if not found:
                # Если не нашли, начинаем поиск с конца
                cursor = current_tab.textCursor()
                cursor.movePosition(cursor.End)
                current_tab.setTextCursor(cursor)
                current_tab.find(search_text, QTextDocument.FindBackward)
        else:
            logger.warning("Текущая вкладка не поддерживает поиск")
