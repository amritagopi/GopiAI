import os
from PySide6.QtCore import Qt, Signal, QSize, QUrl, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTabWidget, QMenu, QToolBar, QTabBar, QLabel,
    QProgressBar, QToolButton, QSizePolicy, QComboBox
)
from PySide6.QtGui import QIcon, QAction, QKeySequence

from .browser_widget import get_browser_widget, initialize_cef
from .icon_manager import get_icon

# Стили для улучшения интерфейса браузера
BROWSER_STYLE = """
QToolBar {
    background-color: #f8f9fa;
    border: none;
    padding: 5px;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: white;
}

QTabBar::tab {
    background-color: #f8f9fa;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 1px solid white;
}

QLineEdit {
    border: 1px solid #dfe1e5;
    border-radius: 24px;
    padding: 5px 10px;
    background-color: white;
    selection-background-color: #e8f0fe;
}

QPushButton {
    border: none;
    padding: 5px;
    border-radius: 4px;
    background-color: transparent;
}

QPushButton:hover {
    background-color: #e8e8e8;
}

QProgressBar {
    border: none;
    background-color: #f8f9fa;
    height: 3px;
}

QProgressBar::chunk {
    background-color: #1a73e8;
}
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
    self.back_button = QPushButton()
    self.back_button.setIcon(get_icon("arrow_left"))
    self.back_button.setToolTip("Назад")
    self.back_button.setEnabled(False)
    self.back_button.clicked.connect(self.go_back)
    nav_bar.addWidget(self.back_button)

    # Кнопка "Вперед"
    self.forward_button = QPushButton()
    self.forward_button.setIcon(get_icon("arrow_right"))
    self.forward_button.setToolTip("Вперед")
    self.forward_button.setEnabled(False)
    self.forward_button.clicked.connect(self.go_forward)
    nav_bar.addWidget(self.forward_button)

    # Кнопка "Обновить/Остановить"
    self.reload_button = QPushButton()
    self.reload_button.setIcon(get_icon("refresh"))
    self.reload_button.setToolTip("Перезагрузить")
    self.reload_button.clicked.connect(self.reload_or_stop)
    nav_bar.addWidget(self.reload_button)

    # Кнопка "Домой"
    self.home_button = QPushButton()
    self.home_button.setIcon(get_icon("home"))
    self.home_button.setToolTip("Домашняя страница")
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

    def __init__(self, parent=None, url="https://www.google.com", favicon=None):
        super(BrowserTab, self).__init__(parent)
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
        self.back_button.setToolTip("Назад")
        self.back_button.clicked.connect(self._on_back_clicked)
        self.toolbar.addWidget(self.back_button)

        # Кнопка "Вперед"
        self.forward_button = QToolButton()
        self.forward_button.setIcon(get_icon("forward"))
        self.forward_button.setToolTip("Вперед")
        self.forward_button.clicked.connect(self._on_forward_clicked)
        self.toolbar.addWidget(self.forward_button)

        # Кнопка "Обновить/Остановить"
        self.reload_button = QToolButton()
        self.reload_button.setIcon(get_icon("refresh"))
        self.reload_button.setToolTip("Обновить")
        self.reload_button.clicked.connect(self._on_reload_clicked)
        self.toolbar.addWidget(self.reload_button)

        # Кнопка "Домой"
        self.home_button = QToolButton()
        self.home_button.setIcon(get_icon("home"))
        self.home_button.setToolTip("Домашняя страница")
        self.home_button.clicked.connect(self._on_home_clicked)
        self.toolbar.addWidget(self.home_button)

        # Адресная строка
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Введите URL или поисковый запрос...")
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
        self.setStyleSheet(BROWSER_STYLE)

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
            if self.reload_button.toolTip() == "Остановить":
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
            self.reload_button.setToolTip("Остановить")
            self.progress_bar.show()
            self.progress_bar.setValue(10)  # Начальное значение
            # Имитируем процесс загрузки
            QTimer.singleShot(100, lambda: self.progress_bar.setValue(30))
            QTimer.singleShot(200, lambda: self.progress_bar.setValue(50))
            QTimer.singleShot(300, lambda: self.progress_bar.setValue(70))
            QTimer.singleShot(400, lambda: self.progress_bar.setValue(90))
        else:
            self.reload_button.setIcon(get_icon("refresh"))
            self.reload_button.setToolTip("Обновить")
            self.progress_bar.setValue(100)
            QTimer.singleShot(300, lambda: self.progress_bar.hide())

    def navigate(self, url):
        """Загружает указанный URL в браузер."""
        if self.browser:
            self.browser.navigate(url)

    def reload_or_stop(self):
        """Перезагружает или останавливает загрузку страницы в зависимости от текущего состояния."""
        if self.reload_button.toolTip() == "Остановить":
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
            print("Ошибка: Метод execute_javascript не найден в браузере")

    def get_current_url(self):
        """Возвращает текущий URL страницы."""
        if hasattr(self.browser, "get_current_url"):
            return self.browser.get_current_url()
        return self.url  # Возвращаем сохраненный URL, если метод не найден

class MultiBrowserWidget(QWidget):
    """Виджет с несколькими вкладками браузера."""

    def __init__(self, parent=None):
        super(MultiBrowserWidget, self).__init__(parent)

        # Создаем главный layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Словарь для хранения соответствия между хешем вкладки и её индексом
        self.tab_hash_to_index = {}

        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.layout.addWidget(self.tabs)

        # Кнопка "Новая вкладка"
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setFixedSize(20, 20)
        self.new_tab_button.setToolTip("Новая вкладка")
        self.new_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)

        # Создаем первую вкладку
        self.add_new_tab()

        # Применяем стили
        self.setStyleSheet(BROWSER_STYLE)

    def add_new_tab(self, url="https://www.google.com"):
        """Добавляет новую вкладку с браузером."""
        tab = BrowserTab(parent=self, url=url)
        tab.title_changed.connect(self.update_tab_title)
        tab.url_changed.connect(self.update_tab_url)

        # Добавляем вкладку и активируем её
        index = self.tabs.addTab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)

        # Сохраняем хеш вкладки и её индекс
        self.tab_hash_to_index[hash(tab)] = index

        return tab

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tabs.count() > 1:
            tab = self.tabs.widget(index)
            if tab:
                # Удаляем запись из словаря
                if hash(tab) in self.tab_hash_to_index:
                    del self.tab_hash_to_index[hash(tab)]

                # Обновляем индексы оставшихся вкладок
                for tab_hash, tab_index in list(self.tab_hash_to_index.items()):
                    if tab_index > index:
                        self.tab_hash_to_index[tab_hash] = tab_index - 1

                self.tabs.removeTab(index)
        else:
            # Если это последняя вкладка, создаем новую с домашней страницей
            self.tabs.setTabText(0, "Новая вкладка")
            current_tab = self.tabs.widget(0)
            if current_tab:
                current_tab.navigate("https://www.google.com")

    def update_tab_title(self, title, tab):
        """Обновляет заголовок вкладки."""
        index = self.tabs.indexOf(tab)
        if index >= 0:
            # Ограничиваем длину заголовка
            if len(title) > 20:
                title = title[:17] + "..."
            self.tabs.setTabText(index, title)

    def update_tab_url(self, url, tab):
        """Обновляет URL вкладки."""
        # Можно использовать для обновления иконки вкладки на основе домена
        pass

    def on_tab_changed(self, index):
        """Обрабатывает изменение активной вкладки."""
        if index >= 0:
            # Фокусируем адресную строку или виджет браузера
            current_tab = self.tabs.widget(index)
            if current_tab:
                current_tab.setFocus()

    def navigate_current_tab(self, url):
        """Загружает URL в текущей вкладке."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            current_tab = self.tabs.widget(current_index)
            if current_tab:
                current_tab.navigate(url)
