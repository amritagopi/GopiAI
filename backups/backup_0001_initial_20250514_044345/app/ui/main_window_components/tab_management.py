"""
Tab Management Mixin for MainWindow.

This module contains methods related to tab management operations in the MainWindow class.
"""

import logging
import asyncio
import time
from concurrent.futures import TimeoutError

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QMenu

from app.ui.i18n.translator import tr
from app.ui.lucide_icon_manager import get_lucide_icon

logger = logging.getLogger(__name__)


class TabManagementMixin:
    """Provides tab management functionality for MainWindow."""

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

        # Проверяем, является ли вкладка вкладкой браузера
        is_browser_tab = False
        if hasattr(tab_widget, "is_browser_tab") and tab_widget.is_browser_tab:
            is_browser_tab = True
            # Если это вкладка браузера, запускаем очистку ресурсов
            logger.info("Closing browser tab, cleaning up resources")
            # Очищаем ресурсы браузерного агента, если он создан
            if hasattr(self, "browser_agent_interface"):
                try:
                    # Синхронная обертка для асинхронного метода cleanup с таймаутом
                    start_time = time.time()
                    loop = asyncio.new_event_loop()

                    try:
                        # Устанавливаем таймаут 3 секунды для очистки ресурсов
                        task = loop.create_task(self.browser_agent_interface.cleanup())
                        # Запускаем с таймаутом
                        loop.run_until_complete(asyncio.wait_for(task, timeout=3.0))
                        cleanup_time = time.time() - start_time
                        logger.info(f"Browser agent resources cleaned up in {cleanup_time:.2f} seconds")
                    except TimeoutError:
                        logger.warning(f"Browser agent cleanup timed out after 3.0 seconds, continuing with tab close")
                    except Exception as e:
                        logger.error(f"Error during browser agent cleanup: {e}")
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"Error cleaning up browser agent: {e}")

            # Сбрасываем индекс вкладки браузера
            if hasattr(self, "browser_tab_index") and self.browser_tab_index == index:
                self.browser_tab_index = -1

        # Проверяем, есть ли несохраненные изменения
        if (
            hasattr(tab_widget, "has_unsaved_changes")
            and callable(tab_widget.has_unsaved_changes)
            and tab_widget.has_unsaved_changes()
        ):
            # Спрашиваем пользователя о сохранении
            reply = QMessageBox.question(
                self,
                tr("dialog.unsaved_changes.title", "Unsaved changes"),
                tr(
                    "dialog.unsaved_changes.message",
                    "There are unsaved changes. Do you want to save before closing?",
                ),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
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

        # Сообщаем об освобождении ресурсов браузера, если это была вкладка браузера
        if is_browser_tab:
            logger.info("Browser tab resources released")

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
        close_others_action = menu.addAction(
            tr("menu.tab.close_others", "Close Others")
        )
        close_right_action = menu.addAction(
            tr("menu.tab.close_right", "Close Tabs to the Right")
        )
        menu.addSeparator()
        close_all_action = menu.addAction(tr("menu.tab.close_all", "Close All"))

        # Добавляем раздел для редактирования
        menu.addSeparator()
        edit_submenu = menu.addMenu(tr("menu.tab.edit", "Edit"))

        # Импортируем функцию для получения Lucide иконок
        from app.ui.lucide_icon_manager import get_lucide_icon

        # Добавляем действие для вставки эмодзи с текущей позицией курсора
        emoji_action = edit_submenu.addAction(tr("menu.emoji", "Insert Emoji"))
        # Добавляем иконку улыбки
        emoji_action.setIcon(get_lucide_icon("smile"))
        global_pos = tab_bar.mapToGlobal(pos)
        emoji_action.triggered.connect(lambda: self._show_emoji_dialog(global_pos))

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

    def _show_project_tree_context_menu(self, position):
        """Показывает контекстное меню для дерева проекта."""
        logger.info(f"Action: Project tree context menu at {position}")

        if not hasattr(self, "project_explorer"):
            logger.error(
                "Cannot show project tree context menu: project_explorer not found"
            )
            return

        # Получаем индекс элемента под курсором
        if hasattr(self.project_explorer, "tree_view"):
            index = self.project_explorer.tree_view.indexAt(position)

            if not index.isValid():
                logger.debug("No valid item under cursor position")
                return

            # Перенаправляем вызов к методу в ProjectExplorer
            if hasattr(self.project_explorer, "_show_context_menu") and callable(
                self.project_explorer._show_context_menu
            ):
                self.project_explorer._show_context_menu(position)
            else:
                logger.error("ProjectExplorer._show_context_menu method not found")
        else:
            logger.error("ProjectExplorer.tree_view not found")
