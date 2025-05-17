"""
File Actions Mixin for MainWindow.

This module contains methods related to file operations in the MainWindow class.
"""

import logging
import os
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from app.ui.i18n.translator import tr

logger = logging.getLogger(__name__)


class FileActionsMixin:
    """Provides file operations functionality for MainWindow."""

    def _new_file(self):
        """Создает новый файл."""
        logger.info("Action: New File - creating new file")

        try:
            # Если есть центральные табы, добавляем новую вкладку
            if hasattr(self, "central_tabs"):
                from app.ui.editor import CodeEditor

                logger.info("Creating new CodeEditor instance")

                editor = CodeEditor(self)

                # Используем метод set_new_file
                logger.info("Calling set_new_file on editor")
                editor.set_new_file()

                logger.info("Adding new tab to central_tabs")
                tab_index = self.central_tabs.addTab(editor, "Untitled")
                self.central_tabs.setCurrentWidget(editor)
                logger.info(f"New file tab created at index {tab_index}")

                # Активируем новый редактор
                editor.setFocus()
                logger.info("Focus set to new editor")

                return editor
            else:
                logger.error("Cannot create new file: central_tabs not found")
                QMessageBox.warning(
                    self,
                    tr("dialog.error", "Error"),
                    tr(
                        "dialog.central_tabs_not_found",
                        "Cannot create new file: tab container not found",
                    ),
                )
        except Exception as e:
            logger.error(f"Error creating new file: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                tr("dialog.error", "Error"),
                tr(
                    "dialog.error_creating_file", "Error creating new file: {error}"
                ).format(error=str(e)),
            )

    def _open_file(self, file_path=None):
        """Открывает файл."""
        logger.info(f"Action: Open File {file_path}")

        # Если путь к файлу не указан, показываем диалог выбора файла
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("dialog.open_file", "Open File"),
                "",
                tr(
                    "dialog.file_filter",
                    "All Files (*);;Text Files (*.txt);;Python Files (*.py)",
                ),
            )
            logger.info(f"User selected file: {file_path}")

        if not file_path:
            logger.info("No file path provided or user cancelled the dialog")
            return

        if not os.path.isfile(file_path):
            logger.error(
                f"Cannot open {file_path}: file does not exist or is not a file"
            )
            QMessageBox.warning(
                self,
                tr("dialog.error", "Error"),
                tr("dialog.file_not_found", "File not found: {path}").format(
                    path=file_path
                ),
            )
            return

        # Проверяем, есть ли у нас виджет MultiEditorWidget для открытия файла
        multi_editor = None
        if hasattr(self, "central_widget") and hasattr(self.central_widget, "editor"):
            multi_editor = self.central_widget.editor
            logger.info("Using MultiEditorWidget for file opening")

        # Если есть многоредакторный виджет, используем его
        if multi_editor and hasattr(multi_editor, "add_new_tab"):
            # Проверяем, может файл уже открыт
            if (
                hasattr(multi_editor, "open_files")
                and file_path in multi_editor.open_files
            ):
                # Переключаемся на вкладку с уже открытым файлом
                editor = multi_editor.open_files[file_path]
                index = multi_editor.tabs.indexOf(editor)
                if index >= 0:
                    multi_editor.tabs.setCurrentIndex(index)
                    logger.info(
                        f"File already open in MultiEditorWidget, switching to tab {index}"
                    )
                    return
                else:
                    logger.warning(
                        f"File {file_path} marked as open but tab not found in MultiEditorWidget"
                    )

            # Открываем новую вкладку в MultiEditorWidget
            logger.info(f"Opening file in MultiEditorWidget: {file_path}")
            multi_editor.add_new_tab(file_path)
            return

        # Если у нас нет MultiEditorWidget, используем обычные табы
        if hasattr(self, "central_tabs"):
            # Попробуем найти, открыт ли уже этот файл
            for i in range(self.central_tabs.count()):
                widget = self.central_tabs.widget(i)
                if hasattr(widget, "file_path") and widget.file_path == file_path:
                    self.central_tabs.setCurrentIndex(i)
                    logger.info(
                        f"File already open in central_tabs, switching to tab {i}"
                    )
                    return

            # Файл не открыт, создаем новую вкладку
            try:
                from app.ui.editor import CodeEditor

                editor = CodeEditor(self)
                editor.open_file(file_path)
                filename = os.path.basename(file_path)
                index = self.central_tabs.addTab(editor, filename)
                self.central_tabs.setCurrentWidget(editor)
                logger.info(f"File opened in a new tab: {file_path}")
                return
            except Exception as e:
                logger.error(f"Error creating editor for file: {e}")
                import traceback

                logger.debug(traceback.format_exc())
                QMessageBox.critical(
                    self,
                    tr("dialog.error", "Error"),
                    tr(
                        "dialog.error_opening_file", "Error opening file: {error}"
                    ).format(error=str(e)),
                )
                return

        logger.error(
            "Cannot open file: no suitable editor found (neither MultiEditorWidget nor central_tabs)"
        )
        QMessageBox.critical(
            self,
            tr("dialog.error", "Error"),
            tr("dialog.error_no_editor", "Cannot open file: no suitable editor found"),
        )

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
                    self.central_tabs.setTabText(
                        self.central_tabs.currentIndex(), filename
                    )
                logger.info("File saved as new name")
            else:
                logger.warning("Current widget does not support 'save as'")
        else:
            logger.error("Cannot save file: central_tabs not found")
