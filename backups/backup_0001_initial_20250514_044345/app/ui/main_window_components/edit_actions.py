"""
Edit Actions Mixin for MainWindow.

This module contains methods related to editing operations in the MainWindow class.
"""

import logging
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox

from app.ui.i18n.translator import tr

logger = logging.getLogger(__name__)


class EditActionsMixin:
    """Provides editing operations functionality for MainWindow."""

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

    def _show_emoji_dialog(self, position=None):
        """Показывает диалог выбора эмодзи.

        Args:
            position (QPoint, optional): Позиция для отображения диалога. Если None,
                                         используется текущая позиция курсора.
        """
        logger.info("Action: Show Emoji Dialog")

        try:
            from app.ui.emoji_dialog import EmojiDialog

            # Создаем диалог эмодзи
            dialog = EmojiDialog(self)

            # Подключаем сигнал для вставки эмодзи
            dialog.emoji_selected.connect(self._insert_emoji)

            # Получаем текущую позицию курсора, если не передана
            if not position:
                from PySide6.QtGui import QCursor
                position = QCursor.pos()

            # Проверяем тип позиции и преобразуем при необходимости
            if position and not isinstance(position, QPoint):
                from PySide6.QtCore import QPoint
                logger.warning(f"Converting position {position} to QPoint")
                position = QCursor.pos()

            dialog_size = dialog.sizeHint()
            screen_geometry = QApplication.primaryScreen().geometry()

            # Расчитываем позицию так, чтобы диалог не выходил за пределы экрана
            x = min(position.x(), screen_geometry.width() - dialog_size.width())
            y = min(position.y(), screen_geometry.height() - dialog_size.height())

            dialog.move(x, y)
            logger.info(f"Positioned emoji dialog at {x},{y}")

            # Показываем диалог
            from PySide6.QtWidgets import QDialog
            result = dialog.exec()
            logger.info(f"Emoji dialog result: {result}")

            return result == QDialog.Accepted
        except ImportError:
            logger.error("Could not import emoji_dialog module.")
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.emoji.import_error", "Could not load emoji dialog."),
            )
            return False
        except Exception as e:
            logger.error(f"Error showing emoji dialog: {e}", exc_info=True)
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.emoji.error", f"Error showing emoji dialog: {str(e)}"),
            )
            return False

    def _insert_emoji(self, emoji):
        """Вставляет эмодзи в текущий активный редактор.

        Args:
            emoji (str): Эмодзи для вставки.
        """
        logger.info(f"Inserting emoji: {emoji}")

        # Получаем активный виджет
        focused_widget = QApplication.focusWidget()

        # Проверяем, есть ли активный виджет
        if not focused_widget:
            logger.warning("Could not insert emoji: no widget is focused")
            QMessageBox.warning(
                self,
                tr("dialog.warning", "Warning"),
                tr(
                    "dialog.emoji.no_focus",
                    "No text field is focused. Please click in a text field first.",
                ),
            )
            return False

        # Пытаемся вставить эмодзи в зависимости от типа виджета
        inserted = False

        # Для QLineEdit и подобных виджетов с методами text(), cursorPosition() и setCursorPosition()
        if (
            hasattr(focused_widget, "text")
            and callable(focused_widget.text)
            and hasattr(focused_widget, "cursorPosition")
            and callable(focused_widget.cursorPosition)
            and hasattr(focused_widget, "setText")
            and callable(focused_widget.setText)
            and hasattr(focused_widget, "setCursorPosition")
            and callable(focused_widget.setCursorPosition)
        ):

            current_text = focused_widget.text()
            current_pos = focused_widget.cursorPosition()

            # Вставляем эмодзи в текущую позицию курсора
            new_text = current_text[:current_pos] + emoji + current_text[current_pos:]
            focused_widget.setText(new_text)

            # Перемещаем курсор после вставленного эмодзи
            focused_widget.setCursorPosition(current_pos + len(emoji))

            inserted = True
            logger.info(
                f"Emoji {emoji} inserted into QLineEdit widget at position {current_pos}"
            )

        # Для текстовых редакторов (QTextEdit, QPlainTextEdit)
        elif hasattr(focused_widget, "insertPlainText") and callable(
            focused_widget.insertPlainText
        ):
            focused_widget.insertPlainText(emoji)
            inserted = True
            logger.info(f"Emoji {emoji} inserted into text editor widget")

        # Если не удалось вставить эмодзи
        if not inserted:
            logger.warning(
                f"Could not insert emoji: unsupported widget type {type(focused_widget).__name__}"
            )
            QMessageBox.warning(
                self,
                tr("dialog.warning", "Warning"),
                tr(
                    "dialog.emoji.unsupported",
                    "Could not insert emoji: the focused control does not support text input.",
                ),
            )
            return False

        # Возвращаем фокус на виджет
        focused_widget.setFocus()
        return True
