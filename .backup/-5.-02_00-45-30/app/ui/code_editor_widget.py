import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QToolBar, QSizePolicy,
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QSplitter,
    QTextEdit, QLabel
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction

from app.ui.code_editor import CodeEditor
from app.ui.i18n.translator import tr
# Удаляем get_icon, IconManager импортируем только для проверки типа, если нужно
from app.ui.icon_manager import IconManager
from app.logger import logger


class MultiEditorWidget(QWidget):
    """Виджет с несколькими вкладками редактора кода."""

    file_changed = Signal(str)
    progress_update = Signal(str)

    # Новые сигналы для интеграции с чатом
    send_to_chat = Signal(str)
    code_check_requested = Signal(str)
    code_run_requested = Signal(str)

    def __init__(self, icon_manager: IconManager, parent=None, theme_manager=None): # Добавлен icon_manager
        super().__init__(parent)
        self.icon_manager = icon_manager # Сохраняем экземпляр
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
        self.new_file_action = QAction(self.icon_manager.get_icon("file"), tr("editor.new_file", "New File"), self) # Используем file
        self.new_file_action.triggered.connect(self.new_file)
        self.toolbar.addAction(self.new_file_action)

        self.open_file_action = QAction(self.icon_manager.get_icon("folder_open"), tr("editor.open_file", "Open File"), self) # Используем folder_open
        self.open_file_action.triggered.connect(self.open_file)
        self.toolbar.addAction(self.open_file_action)

        self.save_file_action = QAction(self.icon_manager.get_icon("save"), tr("editor.save_file", "Save File"), self)
        self.save_file_action.triggered.connect(self.save_file)
        self.toolbar.addAction(self.save_file_action)

        self.save_as_action = QAction(self.icon_manager.get_icon("save"), tr("editor.save_as", "Save As"), self) # Иконка save-as отсутствует, используем save
        self.save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(self.save_as_action)

        self.toolbar.addSeparator()

        # Кнопки запуска
        self.run_action = QAction(self.icon_manager.get_icon("play"), tr("editor.run", "Run"), self) # Используем play
        self.run_action.triggered.connect(self.run_current_file)
        self.toolbar.addAction(self.run_action)

        # Новые кнопки для ИИ-интеграции
        self.toolbar.addSeparator()

        self.send_to_chat_action = QAction(self.icon_manager.get_icon("chat"), tr("editor.send_to_chat", "Send to Chat"), self)
        self.send_to_chat_action.triggered.connect(self.send_selected_to_chat)
        self.toolbar.addAction(self.send_to_chat_action)

        self.check_code_action = QAction(self.icon_manager.get_icon("debug"), tr("editor.check_code", "Check Code"), self) # Используем debug
        self.check_code_action.triggered.connect(self.check_selected_code)
        self.toolbar.addAction(self.check_code_action)

        self.toolbar.addSeparator()

        # Поле для поиска
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(tr("editor.search", "Search in file..."))
        self.search_field.setMaximumWidth(200)
        self.search_field.returnPressed.connect(self.search_in_file)
        self.toolbar.addWidget(self.search_field)

        # Добавляем панель инструментов в лейаут
        self.layout.addWidget(self.toolbar)

        # Создаем виджет вкладок для редакторов
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True) # Можно закрывать вкладки отдельно
        self.tabs.setMovable(True) # Можно перемещать вкладки
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu) # Добавить контекстное меню для вкладок

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
        self.console.setPlaceholderText(tr("editor.console.placeholder", "Output will appear here..."))

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

    def add_new_tab(self, file_path=None):
        """Добавляет новую вкладку редактора кода."""
        # Создаем редактор кода
        editor = CodeEditor(self)

        # Подключаем сигналы редактора к обработчикам
        editor.send_to_chat.connect(self.send_to_chat.emit)
        editor.check_code.connect(self.code_check_requested.emit)
        editor.run_code.connect(self.code_run_requested.emit)

        # Устанавливаем атрибут для хранения пути к файлу
        editor.file_path = file_path

        # Если передан путь к файлу, загружаем его содержимое
        if file_path and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    editor.setPlainText(f.read())

                # Обновляем словарь открытых файлов
                self.open_files[file_path] = editor

                # Устанавливаем заголовок вкладки как имя файла
                tab_title = os.path.basename(file_path)
            except Exception as e:
                logger.error(f"Ошибка при открытии файла: {e}")
                QMessageBox.critical(self, tr("editor.error", "Ошибка"),
                                    tr("editor.error.open_file", "Ошибка при открытии файла: {error}").format(error=str(e)))
                tab_title = tr("editor.new_tab", "Новый файл")
        else:
            # Для новой вкладки без файла
            tab_title = tr("editor.new_tab", "Новый файл")

        # Добавляем вкладку
        index = self.tabs.addTab(editor, tab_title)
        self.tabs.setCurrentIndex(index)

        # Сигнализируем о новом файле
        if file_path:
            self.file_changed.emit(file_path)

        return editor

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        editor = self.tabs.widget(index)

        # Проверяем, есть ли несохраненные изменения
        if editor and editor.document().isModified():
            reply = QMessageBox.question(
                self,
                tr("editor.unsaved_changes", "Несохраненные изменения"),
                tr("editor.save_before_close", "Сохранить изменения перед закрытием?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        # Удаляем запись из словаря открытых файлов
        if editor and hasattr(editor, 'file_path') and editor.file_path:
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
            if editor and hasattr(editor, 'file_path') and editor.file_path:
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
            tr("editor.file_filter", "Текстовые файлы (*.txt *.py *.js *.html *.css *.json *.xml);;Все файлы (*)")
        )

        if file_path:
            # Проверяем, может быть файл уже открыт
            if file_path in self.open_files:
                # Переключаемся на вкладку с уже открытым файлом
                editor = self.open_files[file_path]
                index = self.tabs.indexOf(editor)
                if index >= 0:
                    self.tabs.setCurrentIndex(index)
                    return

            # Открываем новую вкладку с файлом
            self.add_new_tab(file_path)

    def save_file(self):
        """Сохраняет текущий файл."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        # Если файл еще не сохранен, вызываем диалог сохранения
        if not hasattr(editor, 'file_path') or not editor.file_path:
            self.save_file_as()
            return

        try:
            # Сохраняем содержимое в файл
            with open(editor.file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())

            # Обновляем флаг модификации
            editor.document().setModified(False)

            # Обновляем заголовок вкладки
            self.tabs.setTabText(current_index, os.path.basename(editor.file_path))

            # Сигнализируем об успешном сохранении
            self.progress_update.emit(tr("editor.file_saved", "Файл сохранен: {path}").format(path=editor.file_path))

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            QMessageBox.critical(self, tr("editor.error", "Ошибка"),
                               tr("editor.error.save_file", "Ошибка при сохранении файла: {error}").format(error=str(e)))

    def save_file_as(self):
        """Сохраняет текущий файл под новым именем."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor:
            return

        # Показываем диалог сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("editor.save_as_dialog", "Сохранить как"),
            "",
            tr("editor.file_filter", "Текстовые файлы (*.txt *.py *.js *.html *.css *.json *.xml);;Все файлы (*)")
        )

        if not file_path:
            return

        try:
            # Сохраняем содержимое в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())

            # Обновляем путь к файлу в редакторе
            editor.file_path = file_path

            # Обновляем словарь открытых файлов
            self.open_files[file_path] = editor

            # Обновляем флаг модификации
            editor.document().setModified(False)

            # Обновляем заголовок вкладки
            self.tabs.setTabText(current_index, os.path.basename(file_path))

            # Сигнализируем об успешном сохранении
            self.progress_update.emit(tr("editor.file_saved", "Файл сохранен: {path}").format(path=file_path))
            self.file_changed.emit(file_path)

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            QMessageBox.critical(self, tr("editor.error", "Ошибка"),
                               tr("editor.error.save_file", "Ошибка при сохранении файла: {error}").format(error=str(e)))

    def run_current_file(self):
        """Запускает текущий файл."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return

        editor = self.tabs.widget(current_index)
        if not editor or not hasattr(editor, 'file_path') or not editor.file_path:
            QMessageBox.information(self, tr("editor.info", "Информация"),
                                  tr("editor.save_before_run", "Сохраните файл перед запуском."))
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
        self.console.append(tr("editor.running_file", "Запуск файла: {path}").format(path=editor.file_path))
        self.console.append("-------------------------")

        # Простая имитация запуска
        if file_ext == ".py":
            self.console.append(tr("editor.python_run", "Запуск Python файла..."))
            # Здесь будет реальный запуск Python-скрипта
        elif file_ext in [".js", ".html"]:
            self.console.append(tr("editor.web_run", "Запуск веб-файла..."))
            # Здесь будет открытие в браузере или запуск JavaScript
        else:
            self.console.append(tr("editor.generic_run", "Запуск файла с расширением: {ext}").format(ext=file_ext))

        self.progress_update.emit(tr("editor.file_executed", "Файл выполнен: {path}").format(path=editor.file_path))

    def search_in_file(self):
        """Ищет текст в текущем файле."""
        search_text = self.search_field.text()
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
            self.progress_update.emit(tr("editor.search_not_found", "Текст '{text}' не найден").format(text=search_text))
        else:
            self.progress_update.emit(tr("editor.search_found", "Найдено: '{text}'").format(text=search_text))

    def get_current_file(self):
        """Возвращает путь к текущему открытому файлу."""
        current_index = self.tabs.currentIndex()
        if current_index < 0:
            return None

        editor = self.tabs.widget(current_index)
        if not editor or not hasattr(editor, 'file_path'):
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
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

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
        close_others_action = QAction(tr("dialogs.close_others", "Close Other Tabs"), self)
        close_others_action.triggered.connect(lambda: self._close_other_tabs(index))
        menu.addAction(close_others_action)

        # Добавляем разделитель
        menu.addSeparator()

        # Действия для работы с кодом (если есть выделенный текст)
        editor = self.tabs.widget(index)
        if editor and editor.textCursor().hasSelection():
            # Отправить код в чат
            send_to_chat_action = QAction(tr("editor.send_to_chat", "Send to Chat"), self)
            send_to_chat_action.triggered.connect(self.send_selected_to_chat)
            menu.addAction(send_to_chat_action)

            # Проверить код
            check_code_action = QAction(tr("editor.check_code", "Check Code"), self)
            check_code_action.triggered.connect(self.check_selected_code)
            menu.addAction(check_code_action)

            # Запустить код
            run_code_action = QAction(tr("editor.run_selected", "Run Selected Code"), self)
            run_code_action.triggered.connect(self.run_selected_code)
            menu.addAction(run_code_action)

        # Показываем меню в позиции курсора
        menu.exec_(self.tabs.tabBar().mapToGlobal(position))

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
        self.progress_update.emit(tr("editor.sent_to_chat", "Selected code sent to chat"))

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
        self.progress_update.emit(tr("editor.code_check_requested", "Code check requested"))

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
        self.progress_update.emit(tr("editor.code_run_requested", "Code execution requested"))

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
