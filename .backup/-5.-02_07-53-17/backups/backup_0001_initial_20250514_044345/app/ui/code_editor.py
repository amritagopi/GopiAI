import logging
import os
import re
import sys

from PySide6.QtCore import QMimeData, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QContextMenuEvent,
    QCursor,
    QFont,
    QFontDatabase,
    QIcon,
    QKeyEvent,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextFormat,
    QTextOption,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QSizePolicy,
    QTextEdit,
    QWidget,
)

# Импортируем наш хайлайтер
from .syntax_highlighter import PythonHighlighter
from .i18n.translator import tr  # Добавляем импорт tr для локализации


class LineNumberArea(QTextEdit):
    """Область с номерами строк для редактора кода."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setCursor(Qt.ArrowCursor)

        # Устанавливаем формат
        self.setFrameStyle(0)
        font = QFont("Courier New", 10)
        self.setFont(font)

        # Серый фон для зоны номеров строк
        self.setStyleSheet("background-color: #F0F0F0; color: #808080;")

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        # Делегируем отрисовку редактору
        self.editor.lineNumberAreaPaintEvent(event)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса Python."""

    def __init__(self, document):
        super().__init__(document)

        self.highlighting_rules = []

        # Ключевые слова Python
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "and",
            "as",
            "assert",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "False",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "None",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "True",
            "try",
            "while",
            "with",
            "yield",
        ]

        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Строки в одинарных кавычках
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append(
            (re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format)
        )

        # Строки в двойных кавычках
        self.highlighting_rules.append(
            (re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )

        # Комментарии
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        self.highlighting_rules.append((re.compile(r"#[^\n]*"), comment_format))

        # Функции
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#800000"))
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (re.compile(r"\bdef\s+(\w+)\s*\("), function_format)
        )
        self.highlighting_rules.append(
            (re.compile(r"\bclass\s+(\w+)\s*[:\(]"), function_format)
        )

        # Числа
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#A020A0"))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+\b"), number_format))

    def highlightBlock(self, text):
        """Подсвечивает блок текста."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class CodeEditor(QPlainTextEdit):
    """Редактор кода с подсветкой синтаксиса и номерами строк."""

    # Сигнал для отправки кода в чат
    send_to_chat = Signal(str)

    # Сигнал для проверки кода
    check_code = Signal(str)

    # Сигнал для запуска кода
    run_code = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Включаем перенос по словам
        self.setWordWrapMode(QTextOption.NoWrap)

        # Устанавливаем моноширинный шрифт
        font = QFont("Courier New", 10)
        self.setFont(font)

        # Добавляем поддержку эмодзи
        self._ensure_emoji_support()

        # Устанавливаем отступы табуляции
        self.setTabStopDistance(40)  # 40 пикселей

        # Добавляем область с номерами строк
        self.line_number_area = LineNumberArea(self)

        # Подключаем сигналы
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Обновляем ширину области номеров строк
        self.update_line_number_area_width(0)

        # Подсвечиваем текущую строку
        self.highlight_current_line()

        # Добавляем подсветку синтаксиса Python
        self.highlighter = PythonSyntaxHighlighter(self.document())

        # Устанавливаем стиль для редактора
        self.setStyleSheet("background-color: #FFFFFF; color: #000000;")

        # Инициализируем атрибут file_path
        self.file_path = None

    def set_new_file(self):
        """Устанавливает редактор как новый пустой файл."""
        logger = logging.getLogger(__name__)

        logger.info("Setting new file in CodeEditor")
        # Очищаем текст
        self.clear()

        # Сбрасываем путь к файлу
        self.file_path = None

        # Сбрасываем флаг модификации
        self.document().setModified(False)

        logger.info("New file successfully initialized")

        # Если редактор находится внутри вкладок, обновляем заголовок вкладки
        parent = self.parent()
        if parent and hasattr(parent, "central_tabs"):
            current_index = parent.central_tabs.indexOf(self)
            if current_index >= 0:
                parent.central_tabs.setTabText(current_index, "Untitled")
                logger.info(f"Tab title updated to 'Untitled' at index {current_index}")

    def open_file(self, file_path):
        """Открывает файл по указанному пути."""
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"Opening file: {file_path}")

            # Проверяем существование файла
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            # Проверяем расширение файла и определяем бинарный ли это файл
            binary_extensions = [
                ".bin",
                ".exe",
                ".dll",
                ".so",
                ".dylib",
                ".obj",
                ".o",
                ".pyc",
                ".pyd",
                ".class",
            ]
            is_binary_ext = any(
                file_path.lower().endswith(ext) for ext in binary_extensions
            )

            if is_binary_ext:
                logger.info(f"Detected binary file by extension: {file_path}")
                self._open_as_binary(file_path)
                return True

            # Попытка чтения с разными кодировками для текстовых файлов
            encodings = ["utf-8", "latin1", "cp1251", "ascii"]
            content = None
            success_encoding = None

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    success_encoding = encoding
                    logger.info(f"Successfully read file with encoding: {encoding}")
                    break
                except UnicodeDecodeError as e:
                    logger.warning(f"Failed to read with encoding {encoding}: {e}")
                    continue

            # Если ни одна кодировка не подошла, считаем файл бинарным
            if content is None:
                logger.info("None of the encodings worked, treating as binary file")
                self._open_as_binary(file_path)
                return True

            # Проверяем, есть ли подозрительные символы, указывающие на бинарный файл
            if self._looks_binary(content):
                logger.info("Text contains binary characters, treating as binary file")
                self._open_as_binary(file_path)
                return True

            # Устанавливаем содержимое в редактор для текстового файла
            self.setPlainText(content)

            # Сохраняем путь к файлу и кодировку
            self.file_path = file_path
            self.encoding = success_encoding

            # Сбрасываем флаг модификации
            self.document().setModified(False)

            # Если редактор находится внутри вкладок, обновляем заголовок вкладки
            parent = self.parent()
            if parent and hasattr(parent, "central_tabs"):
                current_index = parent.central_tabs.indexOf(self)
                if current_index >= 0:
                    tab_title = os.path.basename(file_path)
                    parent.central_tabs.setTabText(current_index, tab_title)
                    logger.info(
                        f"Tab title updated to '{tab_title}' at index {current_index}"
                    )

            logger.info(f"File opened successfully as text: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            import traceback

            logger.debug(traceback.format_exc())

            # Показываем сообщение об ошибке
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии файла: {e}")
            return False

    def _looks_binary(self, content):
        """Проверяет, содержит ли текст признаки бинарного файла."""
        # Проверяем первые 1000 символов на наличие непечатаемых символов (кроме пробельных)
        sample = content[:1000]
        binary_chars = 0
        for char in sample:
            if not (char.isprintable() or char.isspace()):
                binary_chars += 1

        # Если более 5% непечатаемых символов, считаем файл бинарным
        return (binary_chars / len(sample)) > 0.05 if sample else False

    def _open_as_binary(self, file_path):
        """Открывает файл как бинарный, отображая его в шестнадцатеричном формате."""
        logger = logging.getLogger(__name__)

        try:
            # Чтение файла в бинарном режиме
            with open(file_path, "rb") as f:
                data = f.read()

            # Преобразуем в шестнадцатеричное представление
            hex_view = self._format_hex_view(data)

            # Устанавливаем содержимое в редактор
            self.setPlainText(hex_view)

            # Помечаем файл как бинарный и сохраняем путь
            self.is_binary = True
            self.file_path = file_path

            # Сбрасываем флаг модификации и делаем редактор только для чтения
            self.document().setModified(False)
            self.setReadOnly(True)

            # Обновляем заголовок вкладки
            parent = self.parent()
            if parent and hasattr(parent, "central_tabs"):
                current_index = parent.central_tabs.indexOf(self)
                if current_index >= 0:
                    tab_title = os.path.basename(file_path) + " (Hex)"
                    parent.central_tabs.setTabText(current_index, tab_title)

            logger.info(f"File opened successfully as binary: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening binary file: {e}")
            return False

    def _format_hex_view(self, data):
        """Форматирует бинарные данные в шестнадцатеричное представление."""
        result = []
        bytes_per_line = 16

        for i in range(0, len(data), bytes_per_line):
            chunk = data[i : i + bytes_per_line]

            # Адрес
            address = f"{i:08x}: "

            # Шестнадцатеричное представление
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            hex_part = hex_part.ljust(bytes_per_line * 3 - 1)

            # ASCII представление (заменяем непечатаемые символы точками)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)

            # Добавляем строку в результат
            result.append(f"{address} {hex_part} | {ascii_part}")

        return "\n".join(result)

    def save_file(self):
        """Сохраняет содержимое в текущий файл или вызывает save_file_as, если файл новый."""
        logger = logging.getLogger(__name__)

        if not hasattr(self, "file_path") or not self.file_path:
            logger.info("No file path, redirecting to save_file_as")
            return self.save_file_as()

        try:
            logger.info(f"Saving file: {self.file_path}")
            with open(self.file_path, "w", encoding="utf-8") as f:
                content = self.toPlainText()
                f.write(content)

            # Сбрасываем флаг модификации
            self.document().setModified(False)

            # Если редактор находится внутри вкладок, обновляем заголовок вкладки
            parent = self.parent()
            if parent and hasattr(parent, "central_tabs"):
                current_index = parent.central_tabs.indexOf(self)
                if current_index >= 0:
                    tab_title = os.path.basename(self.file_path)
                    parent.central_tabs.setTabText(current_index, tab_title)

            logger.info(f"File saved successfully: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            import traceback

            logger.debug(traceback.format_exc())

            # Показываем сообщение об ошибке
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла: {e}")
            return False

    def save_file_as(self):
        """Открывает диалог для сохранения файла под новым именем."""
        logger = logging.getLogger(__name__)

        from PySide6.QtWidgets import QFileDialog

        try:
            # Открываем диалог сохранения
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить как",
                "",
                "Текстовые файлы (*.txt *.py *.js *.html *.css *.json *.xml);;Все файлы (*)",
            )

            if not file_path:
                logger.info("Save As dialog cancelled by user")
                return False

            logger.info(f"Saving file as: {file_path}")

            # Сохраняем содержимое в новый файл
            with open(file_path, "w", encoding="utf-8") as f:
                content = self.toPlainText()
                f.write(content)

            # Обновляем путь к файлу
            old_path = getattr(self, "file_path", None)
            self.file_path = file_path

            # Сбрасываем флаг модификации
            self.document().setModified(False)

            # Если редактор находится внутри вкладок, обновляем заголовок вкладки
            parent = self.parent()
            if parent and hasattr(parent, "central_tabs"):
                current_index = parent.central_tabs.indexOf(self)
                if current_index >= 0:
                    tab_title = os.path.basename(file_path)
                    parent.central_tabs.setTabText(current_index, tab_title)

            logger.info(f"File saved successfully as: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error in save_file_as: {e}")
            import traceback

            logger.debug(traceback.format_exc())

            # Показываем сообщение об ошибке
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла: {e}")
            return False

    def has_unsaved_changes(self):
        """Проверяет, есть ли несохраненные изменения."""
        return self.document().isModified()

    def line_number_area_width(self):
        """Вычисляет ширину области номеров строк."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        """Обновляет ширину области номеров строк."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Обновляет область номеров строк при прокрутке редактора."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        """Отрисовывает область номеров строк."""
        painter = QPainter(self.line_number_area.viewport())
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#808080"))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        """Подсвечивает текущую строку."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#F0F8FF")  # Светло-голубой цвет
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, event: QKeyEvent):
        """Обрабатывает нажатия клавиш."""
        # Автоматический отступ при нажатии Enter
        if event.key() == Qt.Key_Return and not event.modifiers() & (
            Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier
        ):
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()

            # Вычисляем отступ из текущей строки
            indent = ""
            for char in text:
                if char == " " or char == "\t":
                    indent += char
                else:
                    break

            # Если строка заканчивается двоеточием, добавляем дополнительный отступ
            if text.strip().endswith(":"):
                if "\t" in indent:
                    indent += "\t"  # Добавляем табуляцию
                else:
                    indent += "    "  # Добавляем 4 пробела

            # Вставляем новую строку с отступом
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        else:
            # Стандартная обработка для других клавиш
            super().keyPressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Переопределяем стандартное контекстное меню."""
        menu = self.createStandardContextMenu()

        # Получаем выделенный текст
        selected_text = self.textCursor().selectedText()

        if selected_text:
            # Добавляем разделитель
            menu.addSeparator()

            # Добавляем раздел для работы с кодом
            code_menu = QMenu(tr("menu.code_actions", "Code Actions"), menu)

            # Отправить код в чат
            send_to_chat_action = QAction(tr("menu.send_to_chat", "Send to Chat"), self)
            send_to_chat_action.triggered.connect(
                lambda: self.send_to_chat.emit(selected_text)
            )
            code_menu.addAction(send_to_chat_action)

            # Проверить код
            check_code_action = QAction(tr("menu.check_code", "Check Code"), self)
            check_code_action.triggered.connect(
                lambda: self.check_code.emit(selected_text)
            )
            code_menu.addAction(check_code_action)

            # Запустить код
            run_code_action = QAction(tr("menu.run_code", "Run Code"), self)
            run_code_action.triggered.connect(lambda: self.run_code.emit(selected_text))
            code_menu.addAction(run_code_action)

            # Добавляем меню кода в основное меню
            menu.addMenu(code_menu)

        # Добавляем разделитель и пункт для вставки эмодзи
        menu.addSeparator()

        # Импортируем функцию для получения Lucide иконок
        from app.ui.lucide_icon_manager import get_lucide_icon

        # Создаем действие для вставки эмодзи с локализованным текстом
        emoji_action = QAction(tr("menu.insert_emoji", "Insert Emoji"), self)
        emoji_action.setIcon(get_lucide_icon("smile"))

        # Используем глобальную позицию курсора для отображения диалога
        global_pos = event.globalPos()
        emoji_action.triggered.connect(lambda: self._show_emoji_dialog(global_pos))
        menu.addAction(emoji_action)

        menu.exec(event.globalPos())

    def _show_emoji_dialog(self, position):
        """Показывает диалог выбора эмодзи в указанной позиции."""
        try:
            from app.ui.emoji_dialog import EmojiDialog

            logger = logging.getLogger(__name__)
            logger.info(f"Showing emoji dialog at position {position}")

            # Проверяем тип позиции и преобразуем при необходимости
            if position and not isinstance(position, QPoint):
                logger.warning(f"Converting position {position} to QPoint")
                position = QCursor.pos()

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
            logger = logging.getLogger(__name__)
            logger.error(f"Error showing emoji dialog: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.emoji_error", "Could not show emoji dialog: {error}").format(
                    error=str(e)
                ),
            )
            return False

    # Реализация перетаскивания файлов
    def dragEnterEvent(self, event):
        """Обрабатывает событие при начале перетаскивания элемента на редактор."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        """Обрабатывает событие при перетаскивании файла на редактор."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # Проверяем, является ли файл текстовым
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.setPlainText(f.read())

                    # Сохраняем путь к файлу в атрибуте редактора
                    self.file_path = file_path

                    # Обновляем заголовок вкладки, если это возможно
                    if hasattr(self.parent(), "central_tabs"):
                        current_index = self.parent().central_tabs.indexOf(self)
                        if current_index >= 0:
                            self.parent().central_tabs.setTabText(
                                current_index, os.path.basename(file_path)
                            )

                    # Сбрасываем флаг модификации документа
                    self.document().setModified(False)
                except Exception as e:
                    # Показываем сообщение об ошибке
                    QMessageBox.critical(
                        self,
                        self.tr("Ошибка"),
                        self.tr(f"Ошибка при открытии файла: {e}"),
                    )

            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def _ensure_emoji_support(self):
        """Обеспечивает поддержку эмодзи в редакторе."""
        # Получаем текущий шрифт
        current_font = self.font()

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
                f == emoji_font or f.startswith(emoji_font) for f in available_fonts
            ):
                fallback_font = emoji_font
                break

        # Если нашли подходящий шрифт, устанавливаем его как запасной
        if fallback_font:
            try:
                # Создаем запасной шрифт для эмодзи
                emoji_font = QFont(fallback_font)

                # Устанавливаем запасной шрифт для документа
                option = self.document().defaultTextOption()
                current_fonts = (
                    option.fontFamilies()
                    if hasattr(option, "fontFamilies") and callable(option.fontFamilies)
                    else []
                )

                # Добавляем эмодзи-шрифт, если его еще нет в списке шрифтов
                if not current_fonts or fallback_font not in current_fonts:
                    new_fonts = list(current_fonts) + [fallback_font]
                    if hasattr(option, "setFontFamilies") and callable(
                        option.setFontFamilies
                    ):
                        option.setFontFamilies(new_fonts)
                        self.document().setDefaultTextOption(option)
                        logging.info(f"Added emoji support with font: {fallback_font}")
            except Exception as e:
                logging.error(f"Error setting up emoji font: {e}")
        else:
            logging.warning(
                "No appropriate emoji font found. Emoji display may be limited."
            )


# Пример запуска для теста
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText("This is a test.\nLine 2\nLine 3")
    editor.resize(600, 400)
    editor.show()
    sys.exit(app.exec())
