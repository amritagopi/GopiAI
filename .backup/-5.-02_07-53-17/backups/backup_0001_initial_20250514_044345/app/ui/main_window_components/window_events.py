"""
Window Events Mixin for MainWindow.

This module contains methods for handling window events in the MainWindow class.
"""

import logging
from PySide6.QtCore import QEvent, QSettings
from PySide6.QtWidgets import QApplication

from app.ui.i18n.translator import tr

logger = logging.getLogger(__name__)


class WindowEventsMixin:
    """Provides window event handling functionality for MainWindow."""

    def closeEvent(self, event):
        """Обрабатывает закрытие главного окна приложения."""
        try:
            # Сохраняем состояние главного окна перед закрытием
            if hasattr(self, "settings"):
                try:
                    # Геометрия центрального виджета
                    self.settings.setValue("geometry", self.saveGeometry())
                    self.settings.setValue("windowState", self.saveState())

                    # Геометрия единого чата
                    if hasattr(self, "unified_chat_view") and self.unified_chat_view:
                        try:
                            geom = self.unified_chat_view.saveGeometry()
                            self.settings.setValue("unified_chat_geometry", geom)
                            self.settings.setValue(
                                "unified_chat_visible", self.unified_chat_view.isVisible()
                            )
                            logger.info("Saved unified chat view state")
                        except Exception as e:
                            logger.error(f"Error saving unified chat view geometry: {e}")
                except Exception as e:
                    logger.error(f"Error saving window state: {e}")

            # Закрываем все вкладки перед закрытием основного окна
            if hasattr(self, "central_tabs") and self.central_tabs:
                logger.info("Closing all tabs before window close")
                tab_count = self.central_tabs.count()
                for i in range(tab_count - 1, -1, -1):
                    try:
                        self._close_tab(i)
                    except Exception as e:
                        logger.error(f"Error closing tab {i}: {e}")

            # Освобождаем ресурсы единого чата
            if hasattr(self, "unified_chat_view") and self.unified_chat_view:
                try:
                    self.unified_chat_view.close()
                    logger.info("Unified chat view closed")
                except Exception as e:
                    logger.error(f"Error closing unified chat view: {e}")

        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")

        event.accept()

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна."""
        super().resizeEvent(event)
        # Здесь можно добавить дополнительную логику при изменении размера

    def changeEvent(self, event):
        """Обрабатывает события изменения состояния окна."""
        if event.type() == QEvent.WindowStateChange:
            # Обрабатываем изменение состояния окна
            logger.debug(f"Window state changed to {self.windowState()}")
        super().changeEvent(event)

    def moveEvent(self, event):
        """Обрабатывает перемещение окна."""
        super().moveEvent(event)
        # Здесь можно добавить дополнительную логику при перемещении окна

    def _toggle_maximized(self):
        """Переключает между полноэкранным и обычным режимом окна."""
        if self.isMaximized():
            self.showNormal()
            logger.debug("Window restored from maximized state")
        else:
            self.showMaximized()
            logger.debug("Window maximized")

    def eventFilter(self, watched, event):
        """Фильтр событий для главного окна.

        Позволяет перехватывать и обрабатывать события до того, как они будут
        доставлены объектам, за которыми ведется наблюдение.
        """
        # Пример обработки глобальных горячих клавиш или других событий
        return super().eventFilter(watched, event)
