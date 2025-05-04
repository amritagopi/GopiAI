from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon, QActionGroup
from app.ui.i18n.translator import tr, JsonTranslationManager
from app.utils.theme_manager import ThemeManager
from app.ui.icon_manager import get_icon

import logging
logger = logging.getLogger(__name__)


class MenuManager(QObject):
    """
    Класс для управления меню приложения.
    Обеспечивает централизованное создание и управление меню и действиями.
    """

    # Сигналы
    menu_action_triggered = Signal(str)  # Сигнал с идентификатором действия
    theme_changed = Signal(str)
    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menus = {}
        self.actions = {}
        self.menubar = None
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.theme_menu = None
        self.language_menu = None
        self.tools_menu = None
        self.help_menu = None

        # Группы действий для радио-кнопок
        self.theme_action_group = None
        self.language_action_group = None

        # Создаем меню
        self.create_menubar()

    def create_menubar(self):
        """Создает главное меню приложения."""
        # Создаем панель меню
        self.menubar = QMenuBar(self.parent)

        # Создаем все подменю
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()

        return self.menubar

    def create_file_menu(self):
        """Создает меню 'Файл'."""
        self.file_menu = QMenu(tr("menu.file", "File"), self.parent)

        # Добавляем пункты меню
        new_action = QAction(get_icon("file_new"), tr("menu.new", "New"), self.parent)
        new_action.setToolTip(tr("menu.new.tooltip", "Create a new file"))
        new_action.triggered.connect(self.parent.new_file)
        self.file_menu.addAction(new_action)

        open_action = QAction(get_icon("folder_open"), tr("menu.open_file", "Open File..."), self.parent)
        open_action.setToolTip(tr("menu.open_file.tooltip", "Open an existing file"))
        open_action.triggered.connect(self.parent.open_file)
        self.file_menu.addAction(open_action)

        save_action = QAction(get_icon("save"), tr("menu.save", "Save"), self.parent)
        save_action.setToolTip(tr("menu.save.tooltip", "Save the current file"))
        save_action.triggered.connect(self.parent.save_file)
        self.file_menu.addAction(save_action)

        save_as_action = QAction(get_icon("save_as"), tr("menu.save_as", "Save As..."), self.parent)
        save_as_action.setToolTip(tr("menu.save_as.tooltip", "Save the current file under a new name"))
        save_as_action.triggered.connect(self.parent.save_file_as)
        self.file_menu.addAction(save_as_action)

        self.file_menu.addSeparator()

        exit_action = QAction(get_icon("exit"), tr("menu.exit", "Exit"), self.parent)
        exit_action.setToolTip(tr("menu.exit.tooltip", "Exit the application"))
        exit_action.triggered.connect(self.parent.close)
        self.file_menu.addAction(exit_action)

        self.menubar.addMenu(self.file_menu)

    def create_edit_menu(self):
        """Создает меню 'Правка'."""
        self.edit_menu = QMenu(tr("menu.edit", "Edit"), self.parent)

        # Добавляем пункты меню
        undo_action = QAction(get_icon("undo"), tr("menu.undo", "Undo"), self.parent)
        undo_action.triggered.connect(self.parent.undo)
        self.edit_menu.addAction(undo_action)

        redo_action = QAction(get_icon("redo"), tr("menu.redo", "Redo"), self.parent)
        redo_action.triggered.connect(self.parent.redo)
        self.edit_menu.addAction(redo_action)

        self.edit_menu.addSeparator()

        cut_action = QAction(get_icon("cut"), tr("menu.cut", "Cut"), self.parent)
        cut_action.setToolTip(tr("menu.cut.tooltip", "Cut the selected content to the clipboard"))
        cut_action.triggered.connect(self.parent.cut)
        self.edit_menu.addAction(cut_action)

        copy_action = QAction(get_icon("copy"), tr("menu.copy", "Copy"), self.parent)
        copy_action.setToolTip(tr("menu.copy.tooltip", "Copy the selected content to the clipboard"))
        copy_action.triggered.connect(self.parent.copy)
        self.edit_menu.addAction(copy_action)

        paste_action = QAction(get_icon("paste"), tr("menu.paste", "Paste"), self.parent)
        paste_action.setToolTip(tr("menu.paste.tooltip", "Paste content from the clipboard"))
        paste_action.triggered.connect(self.parent.paste)
        self.edit_menu.addAction(paste_action)

        select_all_action = QAction(get_icon("select_all"), tr("menu.select_all", "Select All"), self.parent)
        select_all_action.triggered.connect(self.parent.select_all)
        self.edit_menu.addAction(select_all_action)

        self.edit_menu.addSeparator()

        emoji_action = QAction(get_icon("emoji"), tr("menu.insert_emoji", "Insert Emoji..."), self.parent)
        emoji_action.setToolTip(tr("menu.insert_emoji.tooltip", "Open emoji selection dialog"))
        emoji_action.triggered.connect(self.parent.show_emoji_dialog)
        self.edit_menu.addAction(emoji_action)

        self.menubar.addMenu(self.edit_menu)

    def create_view_menu(self):
        """Создает меню 'Вид'."""
        self.view_menu = QMenu(tr("menu.view", "View"), self.parent)

        # Подменю для выбора темы
        self.theme_menu = QMenu(tr("menu.theme", "Theme"), self.parent)
        self.view_menu.addMenu(self.theme_menu)

        # Подменю для выбора языка
        self.language_menu = QMenu(tr("menu.language", "Language"), self.parent)
        self.view_menu.addMenu(self.language_menu)

        # Обновляем подменю тем и языков
        self.update_themes_menu()
        self.update_language_menu()

        self.menubar.addMenu(self.view_menu)

    def create_tools_menu(self):
        """Создает меню 'Инструменты'."""
        self.tools_menu = QMenu(tr("menu.tools", "Tools"), self.parent)

        # Добавляем пункты меню
        terminal_action = QAction(get_icon("terminal"), tr("menu.tools.terminal", "Terminal"), self.parent)
        terminal_action.setToolTip(tr("menu.tools.terminal.tooltip", "Open the integrated terminal"))
        terminal_action.triggered.connect(self.parent.toggle_terminal)
        self.tools_menu.addAction(terminal_action)

        browser_action = QAction(get_icon("browser"), tr("menu.tools.browser", "Web Browser"), self.parent)
        browser_action.setToolTip(tr("menu.tools.browser.tooltip", "Open the integrated web browser"))
        browser_action.triggered.connect(self.parent.toggle_browser)
        self.tools_menu.addAction(browser_action)

        coding_agent_action = QAction(get_icon("code"), tr("menu.tools.coding_agent", "Coding Agent"), self.parent)
        coding_agent_action.setToolTip(tr("menu.tools.coding_agent.tooltip", "Open Coding Agent to help with coding tasks"))
        coding_agent_action.triggered.connect(self.parent.show_coding_agent)
        self.tools_menu.addAction(coding_agent_action)

        # Добавляем действие для Browsing Agent
        browsing_agent_action = QAction(get_icon("search_web"), tr("menu.tools.browsing_agent", "Browsing Agent"), self.parent)
        browsing_agent_action.setToolTip(tr("menu.tools.browsing_agent.tooltip", "Open Browsing Agent to help with web tasks"))
        browsing_agent_action.triggered.connect(self.parent.show_browsing_agent)
        self.tools_menu.addAction(browsing_agent_action)

        # Добавляем действие для Reasoning Agent
        reasoning_agent_action = QAction(get_icon("brain"), tr("menu.tools.reasoning_agent", "Reasoning Agent"), self.parent)
        reasoning_agent_action.setToolTip(tr("menu.tools.reasoning_agent.tooltip", "Open Reasoning Agent with Serena and Sequential Thinking"))
        reasoning_agent_action.triggered.connect(self.parent.show_reasoning_agent)
        self.tools_menu.addAction(reasoning_agent_action)

        self.tools_menu.addSeparator()

        url_action = QAction(get_icon("link"), tr("menu.tools.open_url", "Open URL..."), self.parent)
        url_action.setToolTip(tr("menu.tools.open_url.tooltip", "Open URL in browser"))
        url_action.triggered.connect(self.parent.show_open_url_dialog)
        self.tools_menu.addAction(url_action)

        self.tools_menu.addSeparator()

        agent_action = QAction(get_icon("chat"), tr("menu.configure_agent", "Configure Agent..."), self.parent)
        agent_action.setToolTip(tr("menu.configure_agent.tooltip", "Configure agent settings"))
        agent_action.triggered.connect(self.parent.show_agent_config_dialog)
        self.tools_menu.addAction(agent_action)

        flow_action = QAction(get_icon("flow"), tr("menu.view_flow", "Show Flow Visualization"), self.parent)
        flow_action.setToolTip(tr("menu.view_flow.tooltip", "Visualize agent's flow"))
        flow_action.triggered.connect(self.parent.show_flow_visualization)
        self.tools_menu.addAction(flow_action)

        self.tools_menu.addSeparator()

        # Добавляем пункт настроек Reasoning
        reasoning_settings_action = QAction(get_icon("settings_reasoning"), tr("menu.reasoning_settings", "Reasoning Settings..."), self.parent)
        reasoning_settings_action.setToolTip(tr("menu.reasoning_settings.tooltip", "Configure Reasoning Agent settings"))
        reasoning_settings_action.triggered.connect(self.parent.show_reasoning_settings)
        self.tools_menu.addAction(reasoning_settings_action)

        preferences_action = QAction(get_icon("settings"), tr("menu.preferences", "Preferences..."), self.parent)
        preferences_action.setToolTip(tr("menu.preferences.tooltip", "Edit application preferences"))
        preferences_action.triggered.connect(self.parent.show_preferences)
        self.tools_menu.addAction(preferences_action)

        self.menubar.addMenu(self.tools_menu)

    def create_help_menu(self):
        """Создает меню 'Справка'."""
        self.help_menu = QMenu(tr("menu.help", "Help"), self.parent)

        # Добавляем пункты меню
        docs_action = QAction(get_icon("docs"), tr("menu.documentation", "Documentation"), self.parent)
        docs_action.triggered.connect(self.parent.show_documentation)
        self.help_menu.addAction(docs_action)

        about_action = QAction(get_icon("about"), tr("menu.about", "About GopiAI"), self.parent)
        about_action.triggered.connect(self.parent.show_about_dialog)
        self.help_menu.addAction(about_action)

        self.menubar.addMenu(self.help_menu)

    def create_menu(self, parent_menu, menu_id, title, icon=None):
        """
        Создает подменю и добавляет его в родительское меню.

        Args:
            parent_menu (QMenu): Родительское меню
            menu_id (str): Идентификатор меню
            title (str): Заголовок меню
            icon (QIcon, optional): Иконка для меню

        Returns:
            QMenu: Созданное меню
        """
        menu = QMenu(parent_menu)
        menu.setObjectName(menu_id)

        if title.startswith("tr:"):
            # Если title начинается с 'tr:', используем функцию перевода
            tr_key = title[3:]
            menu.setTitle(tr(tr_key, tr_key.split('.')[-1]))
        else:
            menu.setTitle(title)

        if icon:
            if isinstance(icon, str):
                icon = get_icon(icon)
            menu.setIcon(icon)

        parent_menu.addMenu(menu)
        self.menus[menu_id] = menu

        return menu

    def create_action(self, action_id, title, shortcut=None, status_tip=None,
                      icon=None, checkable=False, checked=False):
        """
        Создает QAction с заданными параметрами.

        Args:
            action_id (str): Идентификатор действия
            title (str): Заголовок действия
            shortcut (str, optional): Комбинация клавиш
            status_tip (str, optional): Текст подсказки в статусной строке
            icon (QIcon/str, optional): Иконка или имя иконки
            checkable (bool, optional): Может ли действие быть отмечено
            checked (bool, optional): Начальное состояние отметки

        Returns:
            QAction: Созданное действие
        """
        # Если icon передан как строка, получаем иконку
        if isinstance(icon, str):
            icon = get_icon(icon)

        # Создаем действие
        action = QAction(icon, title, self.parent)
        action.setObjectName(action_id)

        # Настраиваем действие
        if shortcut:
            action.setShortcut(shortcut)
        if status_tip:
            action.setStatusTip(status_tip)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)

        # Подключаем сигнал
        action.triggered.connect(lambda: self._on_action_triggered(action_id))

        # Сохраняем действие
        self.actions[action_id] = action

        return action

    def add_action_to_menu(self, menu_id, action_id):
        """
        Добавляет существующее действие в меню.

        Args:
            menu_id (str): Идентификатор меню
            action_id (str): Идентификатор действия

        Returns:
            bool: True если добавление успешно, иначе False
        """
        if menu_id in self.menus and action_id in self.actions:
            self.menus[menu_id].addAction(self.actions[action_id])
            return True
        return False

    def add_separator_to_menu(self, menu_id):
        """
        Добавляет разделитель в меню.

        Args:
            menu_id (str): Идентификатор меню

        Returns:
            bool: True если добавление успешно, иначе False
        """
        if menu_id in self.menus:
            self.menus[menu_id].addSeparator()
            return True
        return False

    def get_action(self, action_id):
        """
        Возвращает действие по идентификатору.

        Args:
            action_id (str): Идентификатор действия

        Returns:
            QAction: Действие или None, если не найдено
        """
        return self.actions.get(action_id)

    def get_menu(self, menu_id):
        """
        Возвращает меню по идентификатору.

        Args:
            menu_id (str): Идентификатор меню

        Returns:
            QMenu: Меню или None, если не найдено
        """
        return self.menus.get(menu_id)

    def _on_action_triggered(self, action_id):
        """
        Обработчик сигнала triggered для действий.

        Args:
            action_id (str): Идентификатор действия
        """
        self.menu_action_triggered.emit(action_id)

    def update_translations(self):
        """
        Обновляет переводы для всех меню и действий.
        Должна вызываться при изменении языка.
        """
        # Обновляем меню "Файл"
        if self.file_menu:
            self.file_menu.setTitle(tr("menu.file", "File"))

            if hasattr(self, 'new_file_action'):
                self.new_file_action.setText(tr("menu.file.new", "New File"))

            if hasattr(self, 'open_file_action'):
                self.open_file_action.setText(tr("menu.file.open", "Open..."))

            if hasattr(self, 'save_file_action'):
                self.save_file_action.setText(tr("menu.file.save", "Save"))

            if hasattr(self, 'save_as_action'):
                self.save_as_action.setText(tr("menu.file.save_as", "Save As..."))

            if hasattr(self, 'exit_action'):
                self.exit_action.setText(tr("menu.file.exit", "Exit"))

        # Обновляем меню "Правка"
        if self.edit_menu:
            self.edit_menu.setTitle(tr("menu.edit", "Edit"))

            if hasattr(self, 'undo_action'):
                self.undo_action.setText(tr("menu.edit.undo", "Undo"))

            if hasattr(self, 'redo_action'):
                self.redo_action.setText(tr("menu.edit.redo", "Redo"))

            if hasattr(self, 'cut_action'):
                self.cut_action.setText(tr("menu.edit.cut", "Cut"))

            if hasattr(self, 'copy_action'):
                self.copy_action.setText(tr("menu.edit.copy", "Copy"))

            if hasattr(self, 'paste_action'):
                self.paste_action.setText(tr("menu.edit.paste", "Paste"))

            if hasattr(self, 'select_all_action'):
                self.select_all_action.setText(tr("menu.edit.select_all", "Select All"))

            if hasattr(self, 'emoji_action'):
                self.emoji_action.setText(tr("menu.edit.emoji", "Insert Emoji..."))

        # Обновляем меню "Вид"
        if self.view_menu:
            self.view_menu.setTitle(tr("menu.view", "View"))

            if hasattr(self, 'toggle_project_explorer_action'):
                self.toggle_project_explorer_action.setText(tr("menu.view.project_explorer", "Project Explorer"))

            if hasattr(self, 'toggle_chat_action'):
                self.toggle_chat_action.setText(tr("menu.view.chat", "Chat"))

            if hasattr(self, 'toggle_terminal_action'):
                self.toggle_terminal_action.setText(tr("menu.view.terminal", "Terminal"))

            if hasattr(self, 'toggle_browser_action'):
                self.toggle_browser_action.setText(tr("menu.view.browser", "Browser"))

            if hasattr(self, 'reset_layout_action'):
                self.reset_layout_action.setText(tr("menu.view.reset_layout", "Reset Layout"))

            if hasattr(self, 'reset_ui_action'):
                self.reset_ui_action.setText(tr("menu.view.reset_ui", "Reset All UI"))

            # Обновляем подменю выбора темы
            if hasattr(self, 'themes_menu'):
                self.themes_menu.setTitle(tr("menu.view.themes", "Themes"))

            # Обновляем подменю выбора языка
            if hasattr(self, 'language_menu'):
                self.language_menu.setTitle(tr("menu.view.language", "Language"))

        # Обновляем меню "Инструменты"
        if self.tools_menu:
            self.tools_menu.setTitle(tr("menu.tools", "Tools"))

            if hasattr(self, 'configure_agent_action'):
                self.configure_agent_action.setText(tr("menu.tools.configure_agent", "Configure Agent"))

            if hasattr(self, 'open_url_action'):
                self.open_url_action.setText(tr("menu.tools.open_url", "Open URL..."))

            if hasattr(self, 'view_flow_action'):
                self.view_flow_action.setText(tr("menu.tools.view_flow", "View Flow"))

            if hasattr(self, 'preferences_action'):
                self.preferences_action.setText(tr("menu.tools.preferences", "Preferences..."))

        # Обновляем меню "Справка"
        if self.help_menu:
            self.help_menu.setTitle(tr("menu.help", "Help"))

            if hasattr(self, 'about_action'):
                self.about_action.setText(tr("menu.help.about", "About GopiAI"))

            if hasattr(self, 'documentation_action'):
                self.documentation_action.setText(tr("menu.help.documentation", "Documentation"))

        # Перестраиваем подменю с выбором тем и языков
        self.update_themes_menu()
        self.update_language_menu()

        # Пересоздаем все меню с новыми переводами
        self.recreate_menus()

    def recreate_menus(self):
        """Пересоздает все меню после изменения языка."""
        if self.menubar:
            self.menubar.clear()
            self.create_file_menu()
            self.create_edit_menu()
            self.create_view_menu()
            self.create_tools_menu()
            self.create_help_menu()

    def update_themes_menu(self):
        """Обновляет меню выбора тем."""
        if not self.theme_menu:
            return

        self.theme_menu.clear()

        if self.theme_action_group:
            self.theme_action_group.deleteLater()

        self.theme_action_group = QActionGroup(self.parent)

        # Получаем список доступных тем и текущую тему
        theme_manager = ThemeManager.instance()
        themes = theme_manager.get_available_visual_themes()
        current_theme = theme_manager.get_current_visual_theme()

        # Добавляем темы в меню
        for theme in themes:
            theme_display_name = theme_manager.get_theme_display_name(theme)
            theme_action = QAction(theme_display_name, self.parent, checkable=True)
            theme_action.setData(theme)
            if theme == current_theme:
                theme_action.setChecked(True)
            theme_action.triggered.connect(lambda checked=False, t=theme: self.on_theme_changed(t))
            self.theme_action_group.addAction(theme_action)
            self.theme_menu.addAction(theme_action)

        # Добавляем опцию настройки тем
        self.theme_menu.addSeparator()
        customize_action = QAction(tr("menu.theme.customize", "Customize Theme..."), self.parent)
        customize_action.triggered.connect(self.parent.show_theme_settings)
        self.theme_menu.addAction(customize_action)

    def update_language_menu(self):
        """Обновляет меню выбора языка."""
        if not self.language_menu:
            return

        self.language_menu.clear()

        if self.language_action_group:
            self.language_action_group.deleteLater()

        self.language_action_group = QActionGroup(self.parent)

        # Получаем текущий язык
        translator = JsonTranslationManager.instance()
        current_language = translator.get_current_language()

        # Добавляем доступные языки
        language_options = [
            {"code": "en_US", "name": tr("language.english", "English")},
            {"code": "ru_RU", "name": tr("language.russian", "Русский")}
        ]

        for lang in language_options:
            lang_action = QAction(lang["name"], self.parent, checkable=True)
            lang_action.setData(lang["code"])
            if lang["code"] == current_language:
                lang_action.setChecked(True)
            lang_action.triggered.connect(lambda checked=False, lc=lang["code"]: self.on_language_changed(lc))
            self.language_action_group.addAction(lang_action)
            self.language_menu.addAction(lang_action)

    def on_theme_changed(self, theme):
        """Обработчик изменения темы."""
        # Применяем тему
        ThemeManager.instance().switch_visual_theme(theme)
        # Сигнализируем об изменении
        self.theme_changed.emit(theme)

    def on_language_changed(self, language_code):
        """Обработчик изменения языка."""
        # Применяем язык
        JsonTranslationManager.instance().switch_language(language_code)
        # Обновляем переводы для всех меню
        self.update_translations()
        # Сигнализируем об изменении
        self.language_changed.emit(language_code)
