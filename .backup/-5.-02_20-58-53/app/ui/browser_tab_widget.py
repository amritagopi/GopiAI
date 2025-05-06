import os
from PySide6.QtCore import Qt, Signal, QSize, QUrl, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTabWidget, QMenu, QToolBar, QTabBar, QLabel,
    QProgressBar, QToolButton, QSizePolicy, QComboBox, QSplitter
)
from PySide6.QtGui import QIcon, QAction, QKeySequence

from .browser_widget import get_browser_widget, initialize_cef
from .icon_manager import get_icon
from app.ui.i18n.translator import tr
from app.utils.theme_manager import ThemeManager

# Стили для улучшения интерфейса браузера
def generate_browser_qss(theme_manager):
    return f"""
QToolBar {{
    background-color: {theme_manager.get_color('background')};
    border: none;
    padding: 5px;
}}

QTabWidget::pane {{
    border: 1px solid {theme_manager.get_color('border')};
    background-color: {theme_manager.get_color('background')};
}}

QTabBar::tab {{
    background-color: {theme_manager.get_color('background')};
    border: 1px solid {theme_manager.get_color('border')};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {theme_manager.get_color('foreground')};
    border-bottom: 1px solid {theme_manager.get_color('foreground')};
}}

QLineEdit {{
    border: 1px solid {theme_manager.get_color('input_border')};
    border-radius: 24px;
    padding: 5px 10px;
    background-color: {theme_manager.get_color('input_background')};
    selection-background-color: {theme_manager.get_color('accent')};
}}

QPushButton {{
    border: none;
    padding: 5px;
    border-radius: 4px;
    background-color: transparent;
}}

QPushButton:hover {{
    background-color: {theme_manager.get_color('button_hover')};
}}

QProgressBar {{
    border: none;
    background-color: {theme_manager.get_color('background')};
    height: 3px;
}}

QProgressBar::chunk {{
    background-color: {theme_manager.get_color('accent')};
}}
"""

############################################################################
# !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
# Метод отвечает за создание панели навигации браузера
# Изменение логики может привести к поломке UI и нарушению работы приложения
# Особенно важна корректная работа поля URL и связь с виджетом браузера
# Тесно связан с методами _on_url_edit_return и _on_loading_state_changed
############################################################################
def _create_navigation_bar(self, parent):
    """Создает панель навигации для браузера."""
    # Создаем панель инструментов
    nav_bar = QToolBar()
    nav_bar.setMovable(False)
    nav_bar.setIconSize(QSize(16, 16))

    # Кнопка "Назад"
    self.back_button = QPushButton(tr("browser.back", "Back"))
    self.back_button.setIcon(get_icon("arrow_left"))
    self.back_button.setToolTip(tr("browser.back", "Back"))
    self.back_button.setEnabled(False)
    self.back_button.clicked.connect(self.go_back)
    nav_bar.addWidget(self.back_button)

    # Кнопка "Вперед"
    self.forward_button = QPushButton(tr("browser.forward", "Forward"))
    self.forward_button.setIcon(get_icon("arrow_right"))
    self.forward_button.setToolTip(tr("browser.forward", "Forward"))
    self.forward_button.setEnabled(False)
    self.forward_button.clicked.connect(self.go_forward)
    nav_bar.addWidget(self.forward_button)

    # Кнопка "Обновить/Остановить"
    self.reload_button = QPushButton(tr("browser.refresh", "Refresh"))
    self.reload_button.setIcon(get_icon("refresh"))
    self.reload_button.setToolTip(tr("browser.refresh", "Refresh"))
    self.reload_button.clicked.connect(self._on_reload_clicked)
    nav_bar.addWidget(self.reload_button)

    # Кнопка "Домой"
    self.home_button = QPushButton(tr("browser.home", "Home Page"))
    self.home_button.setIcon(get_icon("home"))
    self.home_button.setToolTip(tr("browser.home", "Home Page"))
    self.home_button.clicked.connect(lambda: self.navigate("https://www.google.com"))
    nav_bar.addWidget(self.home_button)

    # Поле ввода URL
    self.url_edit = QLineEdit()
    self.url_edit.setStyleSheet("""
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 3px;
            padding-left: 5px;
            background-color: #ffffff;
            selection-background-color: #3498db;
        }
        QLineEdit:focus {
            border: 1px solid #3498db;
        }
    """)
    self.url_edit.setClearButtonEnabled(True)
    self.url_edit.returnPressed.connect(self._on_url_edit_return)
    nav_bar.addWidget(self.url_edit)

    return nav_bar

class BrowserTab(QWidget):
    """Виджет вкладки с браузером и панелью навигации."""

    # Сигналы
    title_changed = Signal(str, QWidget)
    url_changed = Signal(str, QWidget)
    favicon_changed = Signal(QIcon, QWidget)
    progress_update = None  # Сигнал для прокидывания прогресса

    def __init__(self, parent=None, url="https://www.google.com", favicon=None, theme_manager=None):
        super(BrowserTab, self).__init__(parent)
        self.theme_manager = theme_manager
        self.url = url
        self.favicon = favicon if favicon else get_icon("browser")

        # Настраиваем layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем панель навигации
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.layout.addWidget(self.toolbar)

        # Кнопка "Назад"
        self.back_button = QToolButton()
        self.back_button.setIcon(get_icon("back"))
        self.back_button.setToolTip(tr("browser.back", "Назад"))
        self.back_button.clicked.connect(self._on_back_clicked)
        self.toolbar.addWidget(self.back_button)

        # Кнопка "Вперед"
        self.forward_button = QToolButton()
        self.forward_button.setIcon(get_icon("forward"))
        self.forward_button.setToolTip(tr("browser.forward", "Вперед"))
        self.forward_button.clicked.connect(self._on_forward_clicked)
        self.toolbar.addWidget(self.forward_button)

        # Кнопка "Обновить/Остановить"
        self.reload_button = QToolButton()
        self.reload_button.setIcon(get_icon("refresh"))
        self.reload_button.setToolTip(tr("browser.refresh", "Обновить"))
        self.reload_button.clicked.connect(self._on_reload_clicked)
        self.toolbar.addWidget(self.reload_button)

        # Кнопка "Домой"
        self.home_button = QToolButton()
        self.home_button.setIcon(get_icon("home"))
        self.home_button.setToolTip(tr("browser.home", "Домашняя страница"))
        self.home_button.clicked.connect(self._on_home_clicked)
        self.toolbar.addWidget(self.home_button)

        # Адресная строка
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(tr("browser.url_placeholder", "Введите URL или поисковый запрос..."))
        self.url_edit.returnPressed.connect(self._on_url_edit_return)
        self.toolbar.addWidget(self.url_edit)

        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        # Добавляем браузер
        self.browser = get_browser_widget(self, url)
        self.layout.addWidget(self.browser)

        # Связываем сигналы
        self.browser.url_changed.connect(self._on_url_changed)
        self.browser.title_changed.connect(self._on_title_changed)
        self.browser.loading_state_changed.connect(self._on_loading_state_changed)

        # Применяем стили
        self.setStyleSheet(generate_browser_qss(self.theme_manager))

    def _on_back_clicked(self):
        """Обработчик нажатия кнопки "Назад"."""
        if self.browser:
            self.browser.go_back()

    def _on_forward_clicked(self):
        """Обработчик нажатия кнопки "Вперед"."""
        if self.browser:
            self.browser.go_forward()

    def _on_reload_clicked(self):
        """Обработчик нажатия кнопки "Обновить/Остановить"."""
        if self.browser:
            # Проверяем текущее состояние кнопки
            if self.reload_button.toolTip() == tr("browser.stop", "Остановить"):
                self.browser.stop()
            else:
                self.browser.reload()

    def _on_home_clicked(self):
        """Обработчик нажатия кнопки "Домой"."""
        self.navigate("https://www.google.com")

    def _on_url_edit_return(self):
        """Обрабатывает нажатие Enter в поле ввода URL."""
        url = self.url_edit.text().strip()
        if url:
            self.navigate(url)

    def _on_url_changed(self, url):
        """Обрабатывает изменение URL."""
        self.url = url
        self.url_edit.setText(url)
        self.url_changed.emit(url, self)

    def _on_title_changed(self, title):
        """Обрабатывает изменение заголовка страницы."""
        # Сигнал передаёт заголовок и id вкладки (хэш от self)
        self.title_changed.emit(title, self)

    def _on_loading_state_changed(self, is_loading, can_go_back, can_go_forward):
        """Обрабатывает изменение состояния загрузки."""
        from PySide6.QtCore import QTimer

        # Обновляем кнопки навигации
        self.back_button.setEnabled(can_go_back)
        self.forward_button.setEnabled(can_go_forward)

        # Обновляем кнопку "Обновить/Остановить"
        if is_loading:
            self.reload_button.setIcon(get_icon("close"))
            self.reload_button.setToolTip(tr("browser.stop", "Stop"))
            self.progress_bar.show()
            self.progress_bar.setValue(10)  # Начальное значение
            # Имитируем процесс загрузки
            QTimer.singleShot(100, lambda: self.progress_bar.setValue(30))
            QTimer.singleShot(200, lambda: self.progress_bar.setValue(50))
            QTimer.singleShot(300, lambda: self.progress_bar.setValue(70))
            QTimer.singleShot(400, lambda: self.progress_bar.setValue(90))
            if self.progress_update:
                self.progress_update.emit(tr("browser.loading", "Loading page..."))
        else:
            self.reload_button.setIcon(get_icon("refresh"))
            self.reload_button.setToolTip(tr("browser.refresh", "Refresh"))
            self.progress_bar.setValue(100)
            QTimer.singleShot(300, lambda: self.progress_bar.hide())
            if self.progress_update:
                self.progress_update.emit(tr("browser.loading_complete", "Loading complete"))

    def navigate(self, url):
        """Загружает указанный URL в браузер."""
        if self.browser:
            self.browser.navigate(url)

    def reload_or_stop(self):
        """Перезагружает или останавливает загрузку страницы в зависимости от текущего состояния."""
        if self.reload_button.toolTip() == tr("browser.stop", "Остановить"):
            # Остановка загрузки
            if hasattr(self.browser, 'stop'):
                self.browser.stop()
        else:
            # Перезагрузка страницы
            if hasattr(self.browser, 'reload'):
                self.browser.reload()

    def execute_javascript(self, code, callback=None):
        """Выполняет JavaScript код в браузере.

        Args:
            code: JavaScript код для выполнения
            callback: Опциональная функция обратного вызова для получения результата
        """
        if hasattr(self.browser, "execute_javascript"):
            self.browser.execute_javascript(code, callback)
        else:
            print(tr("browser.js_execution_error", "Ошибка: Метод execute_javascript не найден в браузере"))

    def get_current_url(self):
        """Возвращает текущий URL страницы."""
        if hasattr(self.browser, "get_current_url"):
            return self.browser.get_current_url()
        return self.url  # Возвращаем сохраненный URL, если метод не найден

# Определение класса BrowserWidget для совместимости
class BrowserWidget(QWidget):
    """Обертка для браузерного виджета, чтобы обеспечить совместимость с новым кодом."""

    # Сигналы
    url_changed = Signal(str)
    title_changed = Signal(str)
    loading_state_changed = Signal(bool, bool, bool)  # is_loading, can_go_back, can_go_forward

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.is_loading = False

        # Создаем layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем базовый браузерный виджет
        self.browser = get_browser_widget(self)
        self.layout.addWidget(self.browser)

        # Подключаем сигналы браузера к нашим сигналам
        if hasattr(self.browser, 'url_changed'):
            self.browser.url_changed.connect(self._on_url_changed)
        if hasattr(self.browser, 'title_changed'):
            self.browser.title_changed.connect(self._on_title_changed)
        if hasattr(self.browser, 'loading_state_changed'):
            self.browser.loading_state_changed.connect(self._on_loading_state_changed)

    def _on_url_changed(self, url):
        """Обработчик сигнала изменения URL."""
        self.url_changed.emit(url)

    def _on_title_changed(self, title):
        """Обработчик сигнала изменения заголовка."""
        self.title_changed.emit(title)

    def _on_loading_state_changed(self, is_loading, can_go_back, can_go_forward):
        """Обработчик сигнала изменения состояния загрузки."""
        self.is_loading = is_loading
        self.loading_state_changed.emit(is_loading, can_go_back, can_go_forward)

    def page(self):
        """Возвращает объект страницы для совместимости."""
        return self.browser

    def url(self):
        """Возвращает текущий URL."""
        return QUrl(self.browser.get_current_url())

    def load(self, url):
        """Загружает указанный URL."""
        self.browser.navigate(url.toString())

    def go_back(self):
        """Переходит на предыдущую страницу."""
        self.browser.go_back()

    def go_forward(self):
        """Переходит на следующую страницу."""
        self.browser.go_forward()

    def reload(self):
        """Перезагружает текущую страницу."""
        self.browser.reload()

    def stop(self):
        """Останавливает загрузку страницы."""
        if hasattr(self.browser, 'stop'):
            self.browser.stop()

    def reload_or_stop(self):
        """Перезагружает страницу или останавливает загрузку."""
        if self.is_loading:
            self.stop()
        else:
            self.reload()

    def go_home(self):
        """Переходит на домашнюю страницу."""
        self.browser.navigate("https://www.google.com")

    def get_current_url(self):
        """Возвращает текущий URL в виде строки."""
        if hasattr(self.browser, 'get_current_url'):
            return self.browser.get_current_url()
        return ""

    def navigate(self, url):
        """Загружает указанный URL."""
        self.browser.navigate(url)

    def execute_javascript(self, code, callback=None):
        """Выполняет JavaScript код в браузере."""
        if hasattr(self.browser, 'execute_javascript'):
            self.browser.execute_javascript(code, callback)
        else:
            print(tr("browser.js_execution_error", "Error: execute_javascript method not found in browser"))

# Определение класса QWebEnginePage для совместимости
class QWebEnginePage:
    """Заглушка для QWebEnginePage для совместимости."""
    pass

class MultiBrowserWidget(QWidget):
    """Виджет с несколькими вкладками браузера."""

    url_changed = Signal(str)
    progress_update = Signal(str)

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager

        # Создаем основной вертикальный лейаут
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Создаем панель инструментов
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)

        # Кнопки навигации
        self.back_button = QAction(get_icon("back"), tr("browser.back", "Back"), self)
        self.back_button.triggered.connect(self.go_back)
        self.toolbar.addAction(self.back_button)

        self.forward_button = QAction(get_icon("forward"), tr("browser.forward", "Forward"), self)
        self.forward_button.triggered.connect(self.go_forward)
        self.toolbar.addAction(self.forward_button)

        self.reload_button = QAction(get_icon("refresh"), tr("browser.refresh", "Refresh"), self)
        self.reload_button.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_button)

        self.home_button = QAction(get_icon("home"), tr("browser.home", "Home Page"), self)
        self.home_button.triggered.connect(self.go_home)
        self.toolbar.addAction(self.home_button)

        self.toolbar.addSeparator()

        # Создаем строку ввода URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.url_bar.setPlaceholderText(tr("browser.url_placeholder", "Enter URL or search query..."))
        self.toolbar.addWidget(self.url_bar)

        # Кнопка для новой вкладки
        self.new_tab_button = QAction(get_icon("add"), tr("browser.new_tab", "New Tab"), self)
        self.new_tab_button.triggered.connect(lambda: self.add_browser_tab())
        self.toolbar.addAction(self.new_tab_button)

        self.layout.addWidget(self.toolbar)

        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.layout.addWidget(self.tabs)

        # Создаем первую вкладку
        self.add_browser_tab()

        # Устанавливаем политику размеров
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_browser_tab(self, url=None, title=None):
        """Добавляет новую вкладку браузера."""
        browser = BrowserWidget(self, self.theme_manager)

        # Подключаем сигналы
        browser_widget = browser.browser
        browser_widget.url_changed.connect(lambda url, b=browser: self.update_url(url, b))
        browser_widget.title_changed.connect(lambda title, b=browser: self.update_title(title, b))
        browser_widget.loading_state_changed.connect(lambda loading, can_back, can_forward, b=browser:
                                                     self.on_loading_state_changed(loading, b))

        # Если URL не передан, используем домашнюю страницу
        if url:
            browser.load(QUrl(url))
        else:
            browser.load(QUrl("https://www.google.com"))

        # Добавляем вкладку
        index = self.tabs.addTab(browser, title or tr("browser.new_tab_title", "New Tab"))
        self.tabs.setCurrentIndex(index)

        return browser

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tabs.count() > 1:
            tab = self.tabs.widget(index)
            if tab:
                self.tabs.removeTab(index)
        else:
            # Если это последняя вкладка, создаем новую с домашней страницей
            self.tabs.setTabText(0, tr("browser.new_tab_title", "New Tab"))
            current_tab = self.tabs.widget(0)
            if current_tab:
                current_tab.navigate("https://www.google.com")

    def on_tab_changed(self, index):
        """Обрабатывает переключение между вкладками."""
        if index >= 0:
            browser = self.tabs.widget(index)
            qurl = browser.url()
            self.url_bar.setText(qurl.toString())

            # Обновляем состояние кнопок навигации
            self.update_navigation_buttons(browser)

            # Генерируем сигнал с текущим URL
            self.url_changed.emit(qurl.toString())

    def update_navigation_buttons(self, browser):
        """Обновляет состояние кнопок навигации."""
        # Обновляем кнопки Back и Forward - всегда недоступны в этой версии
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

        # Обновляем кнопку Reload/Stop в зависимости от состояния загрузки
        if browser and hasattr(browser, 'is_loading'):
            if browser.is_loading:
                self.reload_button.setIcon(get_icon("stop"))
                self.reload_button.setText(tr("browser.stop", "Stop"))
                self.reload_button.triggered.disconnect()
                self.reload_button.triggered.connect(self.stop_loading)
            else:
                self.reload_button.setIcon(get_icon("refresh"))
                self.reload_button.setText(tr("browser.refresh", "Refresh"))
                self.reload_button.triggered.disconnect()
                self.reload_button.triggered.connect(self.reload_page)

    def on_load_started(self, browser):
        """Обрабатывает начало загрузки страницы."""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            browser.is_loading = True
            self.update_navigation_buttons(browser)
            self.progress_update.emit(tr("browser.loading", "Loading page..."))

    def on_load_finished(self, ok, browser):
        """Обрабатывает завершение загрузки страницы."""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            browser.is_loading = False
            self.update_navigation_buttons(browser)
            self.progress_update.emit(tr("browser.loading_complete", "Loading complete"))

    def go_back(self):
        """Обработчик нажатия кнопки "Назад"."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.go_back()

    def go_forward(self):
        """Обработчик нажатия кнопки "Вперед"."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.go_forward()

    def reload_page(self):
        """Обработчик нажатия кнопки "Обновить"."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.reload_or_stop()

    def go_home(self):
        """Обработчик нажатия кнопки "Домой"."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.go_home()

    def load_url(self):
        """Обработчик нажатия Enter в строке ввода URL."""
        url = self.url_bar.text().strip()
        if url:
            current_index = self.tabs.currentIndex()
            if current_index >= 0:
                current_tab = self.tabs.widget(current_index)
                if current_tab:
                    current_tab.navigate(url)

    def update_url(self, url, browser):
        """Обработчик изменения URL."""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            # Обновляем текст в адресной строке
            if self.tabs.currentIndex() == index:
                self.url_bar.setText(url)

            # Обновляем заголовок вкладки
            self.update_title(url, browser)

            # Генерируем сигнал с текущим URL
            self.url_changed.emit(url)

    def update_title(self, title, browser):
        """Обработчик изменения заголовка."""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            # Ограничиваем длину заголовка
            if len(title) > 20:
                title = title[:17] + "..."
            self.tabs.setTabText(index, title)

    def on_load_progress(self, progress, browser):
        """Обработчик изменения прогресса загрузки."""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, f"{progress}%")

    def stop_loading(self):
        """Обработчик остановки загрузки."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.reload_or_stop()

    def on_loading_state_changed(self, is_loading, browser):
        """Обрабатывает изменение состояния загрузки."""
        browser.is_loading = is_loading
        self.update_navigation_buttons(browser)
