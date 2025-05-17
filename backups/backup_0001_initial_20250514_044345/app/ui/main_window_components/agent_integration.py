"""
Agent Integration Mixin for MainWindow.

This module contains methods for integrating with coding/browser agents in MainWindow.
"""

import logging
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from app.ui.i18n.translator import tr
from app.ui.unified_chat_view import UnifiedChatView, MODE_CODING, MODE_BROWSING

logger = logging.getLogger(__name__)


class AgentIntegrationMixin:
    """Provides agent integration functionality for MainWindow."""

    def _toggle_coding_agent(self, checked=None):
        """Переключает видимость окна Coding Agent.

        Args:
            checked (bool, optional): Принудительно устанавливает видимость.
                                     True - показать, False - скрыть, None - переключить.
        """
        logger.debug(f"Action: Toggle Coding Agent {checked}")
        if self.unified_chat_view and hasattr(self.unified_chat_view, "isVisible"):
            if checked is False or self.unified_chat_view.isVisible():
                # Скрываем окно и сохраняем состояние
                self.unified_chat_view.hide()
                self.settings.setValue("unified_chat_visible", False)
                logger.debug("Unified Chat View window hidden")
            else:
                # Показываем окно
                self.show_coding_agent_dialog()
                logger.debug("Unified Chat View window shown")
        else:
            # Open if it doesn't exist or can't be toggled
            self.show_coding_agent_dialog()
            logger.debug("Unified Chat View window created and shown")

        # Update the view menu to show the correct state
        self._update_view_menu()

    def show_coding_agent_dialog(self):
        """Показывает диалог агента кодирования."""
        logger.info("Action: Show Coding Agent Dialog")

        try:
            # Check if already opened and just show it
            if self.unified_chat_view and hasattr(self.unified_chat_view, "show"):
                logger.info("Showing existing unified chat view window")

                # Restore the unified chat window position from settings
                if hasattr(self, "settings") and self.settings:
                    settings = QSettings(tr("app.title", "GopiAI"), "UI")
                    geometry = settings.value("unified_chat_geometry")
                    if geometry:
                        self.unified_chat_view.restoreGeometry(geometry)

                # Show the window
                self.unified_chat_view.show()
                self.unified_chat_view.activateWindow()
                self.unified_chat_view.raise_()

                # Save visibility state
                self.settings.setValue("unified_chat_visible", True)

                # Set the coding mode if the current mode is browsing
                if self.unified_chat_view.active_mode != MODE_CODING:
                    self.unified_chat_view.set_mode(MODE_CODING)

                # Update the view menu
                self._update_view_menu()

                return self.unified_chat_view

            # Create a new dialog if it doesn't exist
            logger.info("Creating new unified chat view")

            # Get app-wide settings
            settings = QSettings(tr("app.title", "GopiAI"), "UI")

            # Create the UnifiedChatView instance
            self.unified_chat_view = UnifiedChatView(
                self.icon_manager,
                self.theme_manager,
                parent=None
            )

            # Setup connections and customizations
            self.unified_chat_view.setWindowTitle(tr("app.title", "GopiAI"))

            # Restore window position if saved
            geometry = settings.value("unified_chat_geometry")
            if geometry:
                self.unified_chat_view.restoreGeometry(geometry)

            # Enable non-modal behavior
            self.unified_chat_view.setModal(False)

            # Show the dialog
            self.unified_chat_view.show()

            # Set initial mode to coding
            if self.unified_chat_view.active_mode != MODE_CODING:
                self.unified_chat_view.set_mode(MODE_CODING)

            # Save state
            settings.setValue("unified_chat_visible", True)

            # Update the view menu to show the correct state
            self._update_view_menu()

            # Return reference to the newly created dialog
            return self.unified_chat_view
        except Exception as e:
            logger.error(f"Error opening unified chat view: {e}")
            return None

    def _on_configure_agent(self):
        """Показывает диалог настройки агента."""
        logger.info("Action: Configure Agent")

        # Opening unified chat view in coding mode
        if not self.unified_chat_view or not hasattr(self.unified_chat_view, "isVisible"):
            self.show_coding_agent_dialog()
        elif not self.unified_chat_view.isVisible():
            self.unified_chat_view.show()
            self.unified_chat_view.activateWindow()
            self.unified_chat_view.raise_()

        # Make sure we're in coding mode
        if self.unified_chat_view.active_mode != MODE_CODING:
            self.unified_chat_view.set_mode(MODE_CODING)

        # Open settings from the unified view
        if hasattr(self.unified_chat_view, "show_agent_settings"):
            QApplication.processEvents()  # Process events to ensure UI is updated
            self.unified_chat_view.show_agent_settings()
        else:
            logger.error("UnifiedChatView.show_agent_settings method not found")

    def _toggle_browser_agent(self, checked=None):
        """Переключает видимость окна Browser Agent.

        Args:
            checked (bool, optional): Принудительно устанавливает видимость.
                                     True - показать, False - скрыть, None - переключить.
        """
        logger.debug(f"Action: Toggle Browser Agent {checked}")
        if self.unified_chat_view and hasattr(self.unified_chat_view, "isVisible"):
            if checked is False or self.unified_chat_view.isVisible():
                # Скрываем окно и сохраняем состояние
                self.unified_chat_view.hide()
                self.settings.setValue("unified_chat_visible", False)
                logger.debug("Unified Chat View window hidden")
            else:
                # Показываем окно
                self.show_browser_agent_dialog()
                logger.debug("Unified Chat View window shown")
        else:
            # Open if it doesn't exist or can't be toggled
            self.show_browser_agent_dialog()
            logger.debug("Unified Chat View window created and shown")

        # Update the view menu to show the correct state
        self._update_view_menu()

    def show_browser_agent_dialog(self):
        """Показывает диалог браузерного агента."""
        logger.info("Action: Show Browser Agent Dialog")

        try:
            # Check if already opened and just show it
            if self.unified_chat_view and hasattr(self.unified_chat_view, "show"):
                logger.info("Showing existing unified chat view window")

                # Restore the unified chat window position from settings
                if hasattr(self, "settings") and self.settings:
                    settings = QSettings(tr("app.title", "GopiAI"), "UI")
                    geometry = settings.value("unified_chat_geometry")
                    if geometry:
                        self.unified_chat_view.restoreGeometry(geometry)

                # Show the window
                self.unified_chat_view.show()
                self.unified_chat_view.activateWindow()
                self.unified_chat_view.raise_()

                # Save visibility state
                self.settings.setValue("unified_chat_visible", True)

                # Set the browsing mode if the current mode is coding
                if self.unified_chat_view.active_mode != MODE_BROWSING:
                    self.unified_chat_view.set_mode(MODE_BROWSING)

                # Update the view menu
                self._update_view_menu()

                return self.unified_chat_view

            # Create a new dialog if it doesn't exist
            logger.info("Creating new unified chat view")

            # Get app-wide settings
            settings = QSettings(tr("app.title", "GopiAI"), "UI")

            # Create the UnifiedChatView instance
            self.unified_chat_view = UnifiedChatView(
                self.icon_manager,
                self.theme_manager,
                parent=None
            )

            # Setup connections and customizations
            self.unified_chat_view.setWindowTitle(tr("app.title", "GopiAI"))

            # Restore window position if saved
            geometry = settings.value("unified_chat_geometry")
            if geometry:
                self.unified_chat_view.restoreGeometry(geometry)

            # Enable non-modal behavior
            self.unified_chat_view.setModal(False)

            # Show the dialog
            self.unified_chat_view.show()

            # Set initial mode to browsing
            if self.unified_chat_view.active_mode != MODE_BROWSING:
                self.unified_chat_view.set_mode(MODE_BROWSING)

            # Save state
            settings.setValue("unified_chat_visible", True)

            # Update the view menu to show the correct state
            self._update_view_menu()

            # Return reference to the newly created dialog
            return self.unified_chat_view
        except Exception as e:
            logger.error(f"Error opening unified chat view: {e}")
            return None
