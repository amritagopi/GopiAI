"""
Модуль для управления меню приложения.

Предоставляет класс MenuManager, который отвечает за создание
и управление всеми меню приложения.
"""

import os
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar, QMessageBox

from app.ui.i18n.translator import tr
from app.utils.theme_manager import ThemeManager

# get_icon больше не нужен, так как мы используем self.icon_manager.get_icon()
# from app.ui.icon_manager import get_icon


class MenuManager(QObject):
    """
    Класс для управления меню приложения.

    Отвечает за создание и обновление всех меню и действий.
    """

    # Эти сигналы больше не нужны, так как MainWindow напрямую подключается к синглтонам
    # Оставляем для обратной совместимости, но пометим как устаревшие
    theme_changed = Signal(
        str
    )  # Deprecated - используйте ThemeManager.visualThemeChanged
    language_changed = Signal(
        str
    )  # Deprecated - используйте JsonTranslationManager.languageChanged

    def __init__(self, main_window: QMainWindow, icon_manager):  # Добавлен icon_manager
        """
        Инициализирует менеджер меню.

        Args:
            main_window: Главное окно приложения, к которому привязано меню
            icon_manager: Экземпляр IconAdapter
        """
        super().__init__()
        self.main_window = main_window
        self.icon_manager = icon_manager  # Сохраняем экземпляр

        # Создаем меню-бар
        self.menubar = QMenuBar(main_window)

        # Создаем основные действия
        self.create_actions()

        # Создаем меню
        self.create_menus()

        # Подключаем сигналы
        self.connect_signals()

        # Подключаемся к сигналу смены языка от JsonTranslationManager
        try:
            from app.ui.i18n.translator import JsonTranslationManager

            translator = JsonTranslationManager.instance()
            translator.languageChanged.connect(self.update_translations)
            import logging

            logger = logging.getLogger(__name__)
            logger.info("Менеджер меню подключен к сигналу смены языка")
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при подключении сигнала смены языка: {str(e)}")

        # Подключаемся к сигналу смены темы от ThemeManager
        try:
            theme_manager = ThemeManager.instance()
            theme_manager.visualThemeChanged.connect(self.update_themes_menu)
            import logging

            logger = logging.getLogger(__name__)
            logger.info("Менеджер меню подключен к сигналу смены темы")
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при подключении сигнала смены темы: {str(e)}")

    def create_actions(self):
        """Создает все действия для меню."""
        # --- File Menu Actions ---
        # Создание нового файла
        self.new_file_action = QAction(
            self.icon_manager.get_icon("file"), tr("menu.new", "New"), self.main_window
        )
        self.new_file_action.setStatusTip(tr("menu.new.tooltip", "Create a new file"))

        # Открытие существующего файла
        self.open_file_action = QAction(
            self.icon_manager.get_icon("folder_open"),
            tr("menu.open_file", "Open"),
            self.main_window,
        )
        self.open_file_action.setStatusTip(
            tr("menu.open_file.tooltip", "Open an existing file")
        )

        # Сохранение текущего файла
        self.save_file_action = QAction(
            self.icon_manager.get_icon("save"),
            tr("menu.save", "Save"),
            self.main_window,
        )
        self.save_file_action.setStatusTip(
            tr("menu.save.tooltip", "Save the current file")
        )

        # Сохранение файла под другим именем
        self.save_as_action = QAction(
            self.icon_manager.get_icon("save"),
            tr("menu.save_as", "Save As"),
            self.main_window,
        )
        self.save_as_action.setStatusTip(
            tr("menu.save_as.tooltip", "Save the file with a new name")
        )

        # Выход из приложения
        self.exit_action = QAction(
            self.icon_manager.get_icon("close"),
            tr("menu.exit", "Exit"),
            self.main_window,
        )
        self.exit_action.setStatusTip(tr("menu.exit.tooltip", "Exit the application"))

        # --- Edit Menu Actions ---
        # Вырезать
        self.cut_action = QAction(
            self.icon_manager.get_icon("cut"), tr("menu.cut", "Cut"), self.main_window
        )
        self.cut_action.setStatusTip(tr("menu.cut.tooltip", "Cut the selected text"))

        # Копировать
        self.copy_action = QAction(
            self.icon_manager.get_icon("copy"),
            tr("menu.copy", "Copy"),
            self.main_window,
        )
        self.copy_action.setStatusTip(tr("menu.copy.tooltip", "Copy the selected text"))

        # Вставить
        self.paste_action = QAction(
            self.icon_manager.get_icon("paste"),
            tr("menu.paste", "Paste"),
            self.main_window,
        )
        self.paste_action.setStatusTip(tr("menu.paste.tooltip", "Paste from clipboard"))

        # Отменить
        self.undo_action = QAction(
            self.icon_manager.get_icon("arrow_left"),
            tr("menu.undo", "Undo"),
            self.main_window,
        )
        self.undo_action.setStatusTip(tr("menu.undo.tooltip", "Undo the last action"))

        # Повторить
        self.redo_action = QAction(
            self.icon_manager.get_icon("arrow_right"),
            tr("menu.redo", "Redo"),
            self.main_window,
        )
        self.redo_action.setStatusTip(tr("menu.redo.tooltip", "Redo the undone action"))

        # Выделить все
        self.select_all_action = QAction(
            self.icon_manager.get_icon("arrow"),
            tr("menu.select_all", "Select All"),
            self.main_window,
        )
        self.select_all_action.setStatusTip(
            tr("menu.select_all.tooltip", "Select all content")
        )

        # Эмодзи
        self.emoji_action = QAction(
            self.icon_manager.get_icon("emoji"),
            tr("menu.emoji", "Insert Emoji"),
            self.main_window,
        )
        self.emoji_action.setStatusTip(
            tr("menu.emoji.tooltip", "Insert emoji character")
        )

        # --- View Menu Actions ---
        # Терминал
        self.toggle_terminal_action = QAction(
            self.icon_manager.get_icon("terminal"),
            tr("dock.terminal.toggle", "Terminal"),
            self.main_window,
        )
        self.toggle_terminal_action.setCheckable(True)
        self.toggle_terminal_action.setStatusTip(
            tr("dock.terminal.toggle.tooltip", "Show/hide terminal")
        )

        # Проводник проекта
        self.toggle_project_explorer_action = QAction(
            self.icon_manager.get_icon("folder"),
            tr("dock.project_explorer.toggle", "Project Explorer"),
            self.main_window,
        )
        self.toggle_project_explorer_action.setCheckable(True)
        self.toggle_project_explorer_action.setStatusTip(
            tr("dock.project_explorer.toggle.tooltip", "Show/hide project explorer")
        )

        # Чат
        self.toggle_chat_action = QAction(
            self.icon_manager.get_icon("chat"),
            tr("dock.chat.toggle", "AI Chat"),
            self.main_window,
        )
        self.toggle_chat_action.setCheckable(True)
        self.toggle_chat_action.setStatusTip(
            tr("dock.chat.toggle.tooltip", "Show/hide AI chat")
        )

        # Браузер
        self.toggle_browser_action = QAction(
            self.icon_manager.get_icon("browser"),
            tr("dock.browser.toggle", "Browser"),
            self.main_window,
        )
        self.toggle_browser_action.setCheckable(True)
        self.toggle_browser_action.setStatusTip(
            tr("dock.browser.toggle.tooltip", "Show/hide browser")
        )

        # Coding Agent (новое действие)
        self.toggle_coding_agent_action = QAction(
            self.icon_manager.get_icon("code"),
            tr("dock.coding_agent.toggle", "Coding Agent"),
            self.main_window,
        )
        self.toggle_coding_agent_action.setCheckable(True)
        self.toggle_coding_agent_action.setStatusTip(
            tr("dock.coding_agent.toggle.tooltip", "Show/hide coding agent window")
        )

        # Сброс расположения
        self.reset_layout_action = QAction(
            self.icon_manager.get_icon("refresh"),
            tr("menu.reset_layout", "Reset Layout"),
            self.main_window,
        )
        self.reset_layout_action.setStatusTip(
            tr("menu.reset_layout.tooltip", "Reset panels layout to default")
        )

        # --- Themes ---
        # self.theme_action_group создается и управляется в update_themes_menu

        # --- Language ---
        self.language_action_group = QActionGroup(self.main_window)

        # --- Tools Menu Actions ---
        # Открыть URL
        self.open_url_action = QAction(
            self.icon_manager.get_icon("link"),
            tr("menu.tools.open_url", "Open URL"),
            self.main_window,
        )
        self.open_url_action.setStatusTip(
            tr("menu.tools.open_url.tooltip", "Open URL in browser")
        )

        # Диагностика UI
        self.run_ui_diagnostics_action = QAction(
            self.icon_manager.get_icon("debug"),
            tr("menu.tools.run_diagnostics", "Run UI Diagnostics"),
            self.main_window,
        )
        self.run_ui_diagnostics_action.setStatusTip(
            tr("menu.tools.run_diagnostics.tooltip", "Test and diagnose UI components")
        )

        # Настройка агента
        self.configure_agent_action = QAction(
            self.icon_manager.get_icon("settings"),
            tr("menu.configure_agent", "Configure Agent"),
            self.main_window,
        )
        self.configure_agent_action.setStatusTip(
            tr("menu.configure_agent.tooltip", "Configure AI agent settings")
        )

        # Визуализация потока
        self.view_flow_action = QAction(
            self.icon_manager.get_icon("flow"),
            tr("menu.view_flow", "View Flow"),
            self.main_window,
        )
        self.view_flow_action.setStatusTip(
            tr("menu.view_flow.tooltip", "View agent flow visualization")
        )

        # Настройки
        self.preferences_action = QAction(
            self.icon_manager.get_icon("preferences"),
            tr("menu.preferences", "Preferences"),
            self.main_window,
        )
        self.preferences_action.setStatusTip(
            tr("menu.preferences.tooltip", "Application preferences")
        )

        # --- Help Menu Actions ---
        # О программе
        self.about_action = QAction(
            self.icon_manager.get_icon("info"),
            tr("menu.about", "About"),
            self.main_window,
        )
        self.about_action.setStatusTip(
            tr("menu.about.tooltip", "About this application")
        )

        # Документация
        self.documentation_action = QAction(
            self.icon_manager.get_icon("documentation"),
            tr("menu.documentation", "Documentation"),
            self.main_window,
        )
        self.documentation_action.setStatusTip(
            tr("menu.documentation.tooltip", "View documentation")
        )

    def create_menus(self):
        """Создает структуру меню."""
        # --- File Menu ---
        self.file_menu = self.menubar.addMenu(tr("menu.file", "File"))
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # --- Edit Menu ---
        self.edit_menu = self.menubar.addMenu(tr("menu.edit", "Edit"))
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.select_all_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.emoji_action)

        # --- View Menu ---
        self.view_menu = self.menubar.addMenu(tr("menu.view", "View"))
        self.view_menu.addAction(self.toggle_project_explorer_action)
        self.view_menu.addAction(self.toggle_chat_action)
        self.view_menu.addAction(self.toggle_terminal_action)
        self.view_menu.addAction(self.toggle_browser_action)
        self.view_menu.addAction(self.toggle_coding_agent_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.reset_layout_action)

        # --- Themes Menu ---
        self.theme_menu = self.view_menu.addMenu(tr("menu.theme", "Theme"))
        self.update_themes_menu()

        # --- Language Menu ---
        self.language_menu = self.view_menu.addMenu(tr("menu.language", "Language"))
        self.update_language_menu()

        # --- Tools Menu ---
        self.tools_menu = self.menubar.addMenu(tr("menu.tools", "Tools"))
        self.tools_menu.addAction(self.open_url_action)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction(self.configure_agent_action)
        self.tools_menu.addAction(self.view_flow_action)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction(self.run_ui_diagnostics_action)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction(self.preferences_action)

        # --- Help Menu ---
        self.help_menu = self.menubar.addMenu(tr("menu.help", "Help"))
        self.help_menu.addAction(self.documentation_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)

    def update_themes_menu(self):
        """Обновляет меню выбора тем с возможностью удаления пользовательских тем."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Обновление меню выбора тем")

        self.theme_menu.clear()

        # Пересоздаем группу действий для тем, чтобы избежать проблем с устаревшими действиями
        if hasattr(self, "theme_action_group") and self.theme_action_group:
            for action in self.theme_action_group.actions():
                self.theme_action_group.removeAction(action)
                action.deleteLater()  # Удаляем само действие
            self.theme_action_group.deleteLater()  # Удаляем группу

        self.theme_action_group = QActionGroup(self.main_window)
        self.theme_action_group.setExclusive(True)

        theme_manager = ThemeManager.instance()
        available_themes = theme_manager.get_available_visual_themes()
        current_theme_name = theme_manager.get_current_visual_theme()

        for theme_name in available_themes:
            theme_display_name = theme_manager.get_theme_display_name(theme_name)

            if theme_name in ["light", "dark"]:  # Встроенные темы
                action = QAction(theme_display_name, self.main_window, checkable=True)
                action.setData(theme_name)
                if theme_name == current_theme_name:
                    action.setChecked(True)

                # Вызываем ThemeManager.switch_visual_theme напрямую
                action.triggered.connect(
                    lambda checked, t=theme_name: theme_manager.switch_visual_theme(
                        t, force_apply=True
                    )
                )
                self.theme_action_group.addAction(action)
                self.theme_menu.addAction(action)
            else:  # Пользовательские темы
                custom_theme_submenu = QMenu(theme_display_name, self.main_window)

                # Действие "Применить"
                apply_action = QAction(
                    tr("menu.theme.apply", "Apply"), self.main_window, checkable=True
                )
                apply_action.setData(theme_name)
                if theme_name == current_theme_name:
                    apply_action.setChecked(True)

                # Вызываем ThemeManager.switch_visual_theme напрямую
                apply_action.triggered.connect(
                    lambda checked, t=theme_name: theme_manager.switch_visual_theme(
                        t, force_apply=True
                    )
                )
                self.theme_action_group.addAction(
                    apply_action
                )  # Добавляем в общую группу
                custom_theme_submenu.addAction(apply_action)

                # Действие "Удалить"
                delete_action = QAction(
                    tr("menu.theme.delete", "Delete"), self.main_window
                )
                delete_action.setData(theme_name)
                delete_action.triggered.connect(
                    lambda checked, t=theme_name: self._handle_delete_theme(t)
                )
                custom_theme_submenu.addAction(delete_action)

                self.theme_menu.addMenu(custom_theme_submenu)

        self.theme_menu.addSeparator()
        customize_action = QAction(
            tr("menu.theme.customize", "Customize Theme..."), self.main_window
        )
        customize_action.triggered.connect(
            lambda: self.main_window.open_theme_settings()
        )
        self.theme_menu.addAction(customize_action)

        logger.info(f"Меню выбора тем обновлено, текущая тема: {current_theme_name}")

    def _handle_delete_theme(self, theme_name: str):
        """Обрабатывает удаление пользовательской темы."""
        theme_manager = ThemeManager.instance()
        theme_display_name = theme_manager.get_theme_display_name(theme_name)

        reply = QMessageBox.question(
            self.main_window,
            tr("menu.theme.delete.confirm.title", "Confirm Deletion"),
            tr(
                "menu.theme.delete.confirm.text",
                "Are you sure you want to delete the theme '{theme_name}'?",
            ).format(theme_name=theme_display_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = theme_manager.delete_custom_theme(theme_name)
            if success:
                # ThemeManager.delete_custom_theme должен вызвать visualThemeChanged,
                # что приведет к вызову self.update_themes_menu() и обновлению меню.
                # Дополнительно можно показать уведомление об успехе, если нужно.
                QMessageBox.information(
                    self.main_window,
                    tr("menu.theme.delete.success.title", "Theme Deleted"),
                    tr(
                        "menu.theme.delete.success.text",
                        "Theme '{theme_name}' has been deleted.",
                    ).format(theme_name=theme_display_name),
                )
            else:
                QMessageBox.warning(
                    self.main_window,
                    tr("menu.theme.delete.error.title", "Error Deleting Theme"),
                    tr(
                        "menu.theme.delete.error.text",
                        "Could not delete theme '{theme_name}'.",
                    ).format(theme_name=theme_display_name),
                )
        # Если пользователь нажал "Нет", ничего не делаем.

    def update_language_menu(self):
        """Обновляет меню выбора языка."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Обновление меню выбора языка")

        try:
            # Очищаем меню
            self.language_menu.clear()

            # Очищаем группу действий языка, если она уже существует
            if hasattr(self, "language_action_group") and self.language_action_group:
                for action in self.language_action_group.actions():
                    self.language_action_group.removeAction(action)
                    if action:
                        action.deleteLater()
                self.language_action_group.deleteLater()

            # Создаем новую группу действий
            self.language_action_group = QActionGroup(self.main_window)

            # Получаем текущий язык
            from app.ui.i18n.translator import JsonTranslationManager, tr

            translator = JsonTranslationManager.instance()
            current_language = translator.get_current_language()

            # Добавляем доступные языки
            language_options = [
                {"code": "en_US", "name": tr("language.english", "English")},
                {"code": "ru_RU", "name": tr("language.russian", "Русский")},
            ]

            for lang in language_options:
                lang_code = lang["code"]  # Явно используем строковое значение
                lang_name = lang["name"]

                # Создаем действие с проверкой типов
                lang_action = QAction(lang_name, self.main_window, checkable=True)
                lang_action.setData(
                    lang_code
                )  # Устанавливаем строковый код языка как данные

                # Проверяем текущий язык строго как строку, без преобразования типов
                if lang_code == current_language:
                    lang_action.setChecked(True)

                # Используем напрямую метод switch_language у JsonTranslationManager
                lang_action.triggered.connect(
                    lambda checked, lc=lang_code: translator.switch_language(lc)
                )

                # Добавляем в группу и меню
                self.language_action_group.addAction(lang_action)
                self.language_menu.addAction(lang_action)

            # Добавляем разделитель
            self.language_menu.addSeparator()

            # Добавляем пункт меню "Настройки языка"
            language_settings_action = QAction(
                tr("menu.language.settings", "Настройки языка..."), self.main_window
            )
            language_settings_action.triggered.connect(
                self.main_window._show_language_selector
            )
            self.language_menu.addAction(language_settings_action)

            logger.info(f"Меню языка обновлено, текущий язык: {current_language}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении меню языка: {str(e)}", exc_info=True)

    def update_translations(self):
        """Обновляет все пункты меню при изменении языка."""
        try:
            import logging

            logger = logging.getLogger(__name__)
            from app.ui.i18n.translator import tr

            logger.info("Обновление переводов всех меню")

            # Обновляем заголовки основных меню, проверяя наличие атрибутов
            if hasattr(self, "file_menu"):
                self.file_menu.setTitle(tr("menu.file", "Файл"))
            if hasattr(self, "edit_menu"):
                self.edit_menu.setTitle(tr("menu.edit", "Правка"))
            if hasattr(self, "view_menu"):
                self.view_menu.setTitle(tr("menu.view", "Вид"))
            if hasattr(self, "help_menu"):
                self.help_menu.setTitle(tr("menu.help", "Справка"))
            if hasattr(self, "tools_menu"):
                self.tools_menu.setTitle(tr("menu.tools", "Инструменты"))
            if hasattr(self, "language_menu"):
                self.language_menu.setTitle(tr("menu.language", "Язык"))
            if hasattr(self, "theme_menu"):
                self.theme_menu.setTitle(tr("menu.theme", "Тема"))

            # Обновляем тексты действий меню "Файл"
            if hasattr(self, "new_file_action"):
                self.new_file_action.setText(tr("menu.new", "Новый"))
            if hasattr(self, "open_file_action"):
                self.open_file_action.setText(tr("menu.open_file", "Открыть файл..."))
            if hasattr(self, "save_file_action"):
                self.save_file_action.setText(tr("menu.save", "Сохранить"))
            if hasattr(self, "save_as_action"):
                self.save_as_action.setText(tr("menu.save_as", "Сохранить как..."))
            if hasattr(self, "exit_action"):
                self.exit_action.setText(tr("menu.exit", "Выход"))

            # Обновляем тексты действий меню "Правка"
            if hasattr(self, "copy_action"):
                self.copy_action.setText(tr("menu.copy", "Копировать"))
            if hasattr(self, "cut_action"):
                self.cut_action.setText(tr("menu.cut", "Вырезать"))
            if hasattr(self, "paste_action"):
                self.paste_action.setText(tr("menu.paste", "Вставить"))
            if hasattr(self, "undo_action"):
                self.undo_action.setText(tr("menu.undo", "Отменить"))
            if hasattr(self, "redo_action"):
                self.redo_action.setText(tr("menu.redo", "Повторить"))
            if hasattr(self, "select_all_action"):
                self.select_all_action.setText(tr("menu.select_all", "Выделить всё"))
            if hasattr(self, "emoji_action"):
                self.emoji_action.setText(tr("menu.emoji", "Вставить эмодзи"))

            # Обновляем тексты действий меню "Вид"
            if hasattr(self, "toggle_project_explorer_action"):
                self.toggle_project_explorer_action.setText(
                    tr("dock.project_explorer.toggle", "Проводник проекта")
                )
                self.toggle_project_explorer_action.setStatusTip(
                    tr(
                        "dock.project_explorer.toggle.tooltip",
                        "Показать/скрыть проводник проекта",
                    )
                )
            if hasattr(self, "toggle_chat_action"):
                self.toggle_chat_action.setText(tr("dock.chat.toggle", "ИИ-чат"))
                self.toggle_chat_action.setStatusTip(
                    tr("dock.chat.toggle.tooltip", "Показать/скрыть ИИ-чат")
                )
            if hasattr(self, "toggle_terminal_action"):
                self.toggle_terminal_action.setText(
                    tr("dock.terminal.toggle", "Терминал")
                )
                self.toggle_terminal_action.setStatusTip(
                    tr("dock.terminal.toggle.tooltip", "Показать/скрыть терминал")
                )
            if hasattr(self, "toggle_browser_action"):
                self.toggle_browser_action.setText(tr("dock.browser.toggle", "Браузер"))
                self.toggle_browser_action.setStatusTip(
                    tr("dock.browser.toggle.tooltip", "Показать/скрыть браузер")
                )
            if hasattr(self, "reset_layout_action"):
                self.reset_layout_action.setText(
                    tr("menu.reset_layout", "Сбросить расположение")
                )
                self.reset_layout_action.setStatusTip(
                    tr(
                        "menu.reset_layout.tooltip",
                        "Вернуть расположение панелей по умолчанию",
                    )
                )
            if hasattr(self, "reset_ui_action"):
                self.reset_ui_action.setText(tr("menu.reset_ui", "Сбросить интерфейс"))
                self.reset_ui_action.setStatusTip(
                    tr("menu.reset_ui.tooltip", "Сбросить весь интерфейс по умолчанию")
                )

            # Обновляем тексты действий меню "Инструменты"
            if hasattr(self, "open_url_action"):
                self.open_url_action.setText(
                    tr("menu.tools.open_url", "Открыть URL...")
                )
                self.open_url_action.setStatusTip(
                    tr("menu.tools.open_url.tooltip", "Открыть URL в браузере")
                )
            if hasattr(self, "configure_agent_action"):
                self.configure_agent_action.setText(
                    tr("menu.configure_agent", "Настроить агента")
                )
                self.configure_agent_action.setStatusTip(
                    tr("menu.configure_agent.tooltip", "Настроить параметры AI-агента")
                )
            if hasattr(self, "view_flow_action"):
                self.view_flow_action.setText(tr("menu.view_flow", "Просмотр потока"))
                self.view_flow_action.setStatusTip(
                    tr("menu.view_flow.tooltip", "Визуализировать поток агента")
                )
            if hasattr(self, "preferences_action"):
                self.preferences_action.setText(tr("menu.preferences", "Настройки"))
                self.preferences_action.setStatusTip(
                    tr("menu.preferences.tooltip", "Настройки приложения")
                )
            if hasattr(self, "run_ui_diagnostics_action"):
                self.run_ui_diagnostics_action.setText(
                    tr("menu.tools.run_diagnostics", "Диагностика UI")
                )
                self.run_ui_diagnostics_action.setStatusTip(
                    tr("menu.tools.run_diagnostics.tooltip", "Запустить диагностику UI")
                )

            # Обновляем тексты действий меню "Справка"
            if hasattr(self, "about_action"):
                self.about_action.setText(tr("menu.about", "О программе"))
                self.about_action.setStatusTip(
                    tr("menu.about.tooltip", "Информация о программе")
                )
            if hasattr(self, "documentation_action"):
                self.documentation_action.setText(
                    tr("menu.documentation", "Документация")
                )
                self.documentation_action.setStatusTip(
                    tr("menu.documentation.tooltip", "Просмотр документации")
                )

            # Обновляем меню "Язык"
            self.update_language_menu()

            # Обновляем меню "Темы"
            self.update_themes_menu()

            logger.info("Обновление переводов меню завершено")
        except Exception as e:
            import logging
            import traceback

            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при обновлении переводов меню: {str(e)}")
            logger.error(traceback.format_exc())

    def connect_signals(self):
        """Подключает сигналы в менеджере меню."""
        import logging

        logger = logging.getLogger(__name__)

        # Сигналы theme_changed и language_changed оставлены для обратной совместимости,
        # но рекомендуется подключаться напрямую к ThemeManager.visualThemeChanged и
        # JsonTranslationManager.languageChanged
        logger.info("Подключение сигналов в MenuManager")

        # Проверим, существуют ли методы, к которым подключаемся
        methods_to_check = [
            ("_new_file", self.main_window),
            ("_open_file", self.main_window),
            ("_save_file", self.main_window),
            ("_save_file_as", self.main_window),
            ("_on_cut", self.main_window),
            ("_on_copy", self.main_window),
            ("_on_paste", self.main_window),
            ("_on_undo", self.main_window),
            ("_on_redo", self.main_window),
            ("_on_select_all", self.main_window),
            ("_show_emoji_dialog", self.main_window),
            ("_toggle_terminal", self.main_window),
            ("_toggle_project_explorer", self.main_window),
            ("_toggle_chat", self.main_window),
            ("_toggle_browser", self.main_window),
            ("_toggle_coding_agent", self.main_window),
            ("reset_dock_layout", self.main_window),
            ("_open_url_in_browser", self.main_window),
            ("_on_configure_agent", self.main_window),
            ("_show_flow_visualization", self.main_window),
            ("_run_ui_diagnostics", self.main_window),
            ("_show_preferences_dialog", self.main_window),
            ("_on_about", self.main_window),
            ("_on_documentation", self.main_window),
        ]

        missing_methods = []
        for method_name, obj in methods_to_check:
            if not hasattr(obj, method_name):
                missing_methods.append(method_name)
            elif not callable(getattr(obj, method_name)):
                missing_methods.append(f"{method_name} (not callable)")

        if missing_methods:
            logger.error(
                f"В главном окне отсутствуют методы: {', '.join(missing_methods)}"
            )
        else:
            logger.info("Все методы для подключения сигналов существуют в главном окне")

        # Файловые операции
        self.new_file_action.triggered.connect(self.main_window._new_file)
        self.open_file_action.triggered.connect(self.main_window._open_file)
        self.save_file_action.triggered.connect(self.main_window._save_file)
        self.save_as_action.triggered.connect(self.main_window._save_file_as)
        self.exit_action.triggered.connect(self.main_window.close)

        # Операции редактирования
        self.cut_action.triggered.connect(self.main_window._on_cut)
        self.copy_action.triggered.connect(self.main_window._on_copy)
        self.paste_action.triggered.connect(self.main_window._on_paste)
        self.undo_action.triggered.connect(self.main_window._on_undo)
        self.redo_action.triggered.connect(self.main_window._on_redo)
        self.select_all_action.triggered.connect(self.main_window._on_select_all)
        self.emoji_action.triggered.connect(self.main_window._show_emoji_dialog)

        # Видимость панелей
        self.toggle_terminal_action.triggered.connect(self.main_window._toggle_terminal)
        self.toggle_project_explorer_action.triggered.connect(
            self.main_window._toggle_project_explorer
        )
        self.toggle_chat_action.triggered.connect(self.main_window._toggle_chat)
        self.toggle_browser_action.triggered.connect(self.main_window._toggle_browser)
        self.toggle_coding_agent_action.triggered.connect(
            self.main_window._toggle_coding_agent
        )
        self.reset_layout_action.triggered.connect(self.main_window.reset_dock_layout)

        # Инструменты
        self.open_url_action.triggered.connect(self.main_window._open_url_in_browser)
        self.configure_agent_action.triggered.connect(
            self.main_window._on_configure_agent
        )
        self.view_flow_action.triggered.connect(
            self.main_window._show_flow_visualization
        )
        self.run_ui_diagnostics_action.triggered.connect(
            self.main_window._run_ui_diagnostics
        )
        self.preferences_action.triggered.connect(
            self.main_window._show_preferences_dialog
        )

        # Справка
        self.about_action.triggered.connect(self.main_window._on_about)
        self.documentation_action.triggered.connect(self.main_window._on_documentation)

        logger.info("Сигналы в MenuManager подключены")
