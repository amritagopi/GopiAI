import os
import sys
import platform
import ctypes
from PySide6.QtCore import QTimer, Qt, Signal, QSize, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QMessageBox, QLabel
from PySide6.QtGui import QWindow, QColor

# Полностью отключаем аппаратное ускорение для WebEngine
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-gpu-compositing --disable-accelerated-2d-canvas --disable-accelerated-video-decode --disable-webgl"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# Отладочная информация о WebEngine
print(f"WebEngine flags: {os.environ.get('QTWEBENGINE_CHROMIUM_FLAGS', '')}")

# Проверяем доступность QWebEngineView
WEBENGINE_AVAILABLE = False
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    WEBENGINE_AVAILABLE = True
    print("WebEngine успешно загружен")
except ImportError as e:
    print(f"Ошибка загрузки WebEngine: {e}")
    print("Проверка доступности альтернативного WebEngine не удалась")

# Глобальная переменная для отслеживания доступности CEF
CEF_AVAILABLE = False

# Пытаемся импортировать CEF
try:
    from cefpython3 import cefpython as cef
    CEF_AVAILABLE = True
    print("CEF успешно загружен")
except Exception as e:
    print(f"Ошибка загрузки CEF: {e}")
    if WEBENGINE_AVAILABLE:
        print("Будет использован QWebEngineView вместо CEF")
    else:
        print("Функциональность браузера будет отключена")


class WebEngineWidget(QWidget):
    """Виджет для встраивания QWebEngineView браузера в PySide6."""

    # Сигналы браузера
    url_changed = Signal(str)
    title_changed = Signal(str)
    loading_state_changed = Signal(bool, bool, bool)  # isLoading, canGoBack, canGoForward

    def __init__(self, parent=None, start_url="https://www.google.com"):
        super(WebEngineWidget, self).__init__(parent)
        self.start_url = start_url

        # Создаём layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Устанавливаем белый фон для виджета
        self.setStyleSheet("background-color: white;")

        # Создаем WebEngineView
        self.browser = QWebEngineView(self)

        # Настройка для улучшения отображения
        settings = self.browser.page().settings()

        # Отключаем все потенциально конфликтующие функции
        try:
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
            settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)

            # Устанавливаем стандартные шрифты
            settings.setFontFamily(QWebEngineSettings.StandardFont, "Arial")
            settings.setFontFamily(QWebEngineSettings.FixedFont, "Courier New")
            settings.setFontFamily(QWebEngineSettings.SerifFont, "Times New Roman")
            settings.setFontFamily(QWebEngineSettings.SansSerifFont, "Arial")

            # Размер шрифта по умолчанию
            settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)

            print("Настройки WebEngine применены успешно")
        except Exception as e:
            print(f"Предупреждение: не удалось установить настройки WebEngine: {e}")

        # Устанавливаем белый фон для страницы
        try:
            self.browser.page().setBackgroundColor(QColor(255, 255, 255))
        except Exception as e:
            print(f"Предупреждение: не удалось установить фон: {e}")

        self.layout.addWidget(self.browser)

        # Подключаем сигналы
        self.browser.loadStarted.connect(lambda: self._on_loading_state_changed(True))
        self.browser.loadFinished.connect(lambda: self._on_loading_state_changed(False))
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.titleChanged.connect(self._on_title_changed)

        # Загружаем начальный URL
        self.navigate(start_url)

    def _on_url_changed(self, url):
        """Обрабатывает изменение URL."""
        self.url_changed.emit(url.toString())

    def _on_title_changed(self, title):
        """Обрабатывает изменение заголовка страницы."""
        self.title_changed.emit(title)

    def _on_loading_state_changed(self, is_loading):
        """Обрабатывает изменение состояния загрузки."""
        can_go_back = self.browser.history().canGoBack()
        can_go_forward = self.browser.history().canGoForward()
        self.loading_state_changed.emit(is_loading, can_go_back, can_go_forward)

    def navigate(self, url):
        """Загружает указанный URL в браузер."""
        # Проверяем, что url - это строка
        if not isinstance(url, str):
            url = "https://www.google.com"

        # Добавляем протокол http://, если он отсутствует
        if url and not url.startswith(("http://", "https://", "file://")):
            url = "http://" + url

        try:
            self.browser.load(QUrl(url))
        except Exception as e:
            print(f"Ошибка при загрузке URL {url}: {e}")
            self.browser.load(QUrl("https://www.google.com"))

    def go_back(self):
        """Переходит на предыдущую страницу."""
        self.browser.back()

    def go_forward(self):
        """Переходит на следующую страницу."""
        self.browser.forward()

    def reload(self):
        """Перезагружает текущую страницу."""
        self.browser.reload()

    def stop(self):
        """Останавливает загрузку текущей страницы."""
        self.browser.stop()

    def get_current_url(self):
        """Возвращает текущий URL."""
        return self.browser.url().toString()

    def execute_javascript(self, code, callback=None):
        """Выполняет JavaScript код.

        Args:
            code: JavaScript код для выполнения
            callback: Опциональная функция обратного вызова для получения результата
        """
        if callback:
            self.browser.page().runJavaScript(code, callback)
        else:
            self.browser.page().runJavaScript(code)


class CefWidget(QWidget):
    """Виджет для встраивания CEF браузера в PySide6."""

    # Сигналы браузера
    url_changed = Signal(str)
    title_changed = Signal(str)
    loading_state_changed = Signal(bool, bool, bool)  # isLoading, canGoBack, canGoForward

    def __init__(self, parent=None, start_url="https://www.google.com"):
        super(CefWidget, self).__init__(parent)
        self.browser = None
        self.start_url = start_url
        self.windowHandle = None
        self.browser_window = None

        # Настраиваем атрибуты виджета
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: white;")

        # Создаём layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        if not CEF_AVAILABLE:
            # Создаем заглушку вместо браузера
            self._create_fallback_ui()
            return

        # Инициализируем CEF, если еще не инициализирован
        if not initialize_cef():
            self._create_fallback_ui()
            return

        # Создаём фрейм для браузера
        self.browser_frame = QFrame(self)
        self.browser_frame.setObjectName("BrowserFrame")
        self.browser_frame.setStyleSheet("#BrowserFrame { border: 1px solid #999; }")
        self.layout.addWidget(self.browser_frame)

        # Таймер для обновления CEF
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cef)
        self.timer.start(10)  # 10ms

        # Отложенная инициализация браузера
        QTimer.singleShot(100, self.embed_browser)

    def _create_fallback_ui(self):
        """Создает заглушку UI для случаев, когда CEF недоступен."""
        self.label = QLabel("Браузер недоступен: библиотека CEF не поддерживает текущую версию Python.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #ff5555;
                padding: 20px;
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.label)

    def embed_browser(self):
        """Встраивает браузер CEF в виджет."""
        ############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за встраивание CEF браузера в виджет Qt
        # Изменение логики может привести к поломке UI и нарушению работы приложения
        # Тесно связан с методами initialize_cef и shutdown_cef
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ############################################################################
        if self.browser_frame.winId() == 0:
            # Фрейм ещё не создан, используем отложенную инициализацию
            QTimer.singleShot(100, self.embed_browser)
            return

        window_info = cef.WindowInfo()
        rect = self.browser_frame.geometry()

        # Получаем дескриптор окна для фрейма
        self.windowHandle = int(self.browser_frame.winId())

        # Устанавливаем настройки окна
        window_info.SetAsChild(self.windowHandle,
                               [0, 0, rect.width(), rect.height()])

        # Создаём браузер
        self.browser = cef.CreateBrowserSync(window_info,
                                             url=self.start_url,
                                             window_title="CEF Browser")

        # Настраиваем обработчики событий
        self.set_client_handlers()

        # Делаем фокус на браузере
        self.browser.SendFocusEvent(True)

    def set_client_handlers(self):
        """Устанавливает обработчики событий для браузера."""
        if not self.browser:
            return

        client_handlers = ClientHandlers(self)
        self.browser.SetClientHandler(client_handlers)

    def update_cef(self):
        """Обновляет CEF цикл обработки сообщений."""
        cef.MessageLoopWork()

    def navigate(self, url):
        """Переходит на указанный URL."""
        if self.browser:
            self.browser.LoadUrl(url)

    def go_back(self):
        """Переходит на предыдущую страницу."""
        if self.browser:
            self.browser.GoBack()

    def go_forward(self):
        """Переходит на следующую страницу."""
        if self.browser:
            self.browser.GoForward()

    def reload(self):
        """Перезагружает текущую страницу."""
        if self.browser:
            self.browser.Reload()

    def stop(self):
        """Останавливает загрузку текущей страницы."""
        if self.browser:
            self.browser.StopLoad()

    def get_current_url(self):
        """Возвращает текущий URL."""
        if self.browser:
            return self.browser.GetUrl()
        return ""

    def execute_javascript(self, code, callback=None):
        """Выполняет JavaScript код с возможностью получения результата.

        Args:
            code: JavaScript код для выполнения
            callback: Опциональная функция обратного вызова для получения результата
        """
        if not self.browser:
            print("Ошибка: Браузер не инициализирован")
            return

        try:
            if callback:
                # CEF поддерживает вызов JavaScript с получением результата
                self.browser.ExecuteJavascript(code,
                                               self.browser.GetMainFrame().GetUrl(),
                                               0,
                                               callback)
            else:
                self.browser.ExecuteJavascript(code,
                                              self.browser.GetMainFrame().GetUrl())
        except Exception as e:
            print(f"Ошибка выполнения JavaScript: {e}")

    def resizeEvent(self, event):
        """Обработчик события изменения размера виджета."""
        ############################################################################
        # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
        # Метод отвечает за корректное изменение размера браузера при ресайзе окна
        # Изменение логики может привести к поломке UI и нарушению работы приложения
        # Особенно важно для Windows платформы
        # Тщательно протестирован 30.04.2025 - РАБОТАЕТ КОРРЕКТНО!
        ############################################################################
        if self.browser:
            width, height = event.size().width(), event.size().height()
            if platform.system() == "Windows":
                ctypes.windll.user32.SetWindowPos(
                    self.windowHandle, 0, 0, 0, width, height, 0x0002)
            self.browser.NotifyMoveOrResizeStarted()
        super(CefWidget, self).resizeEvent(event)

    def closeEvent(self, event):
        """Обработчик события закрытия виджета."""
        # CEF закрывается на уровне приложения
        super(CefWidget, self).closeEvent(event)

    def showEvent(self, event):
        """Обработчик события показа виджета."""
        super(CefWidget, self).showEvent(event)

        if not CEF_AVAILABLE:
            return

        if hasattr(self, 'browser'):
            self.browser.WasResized()

    def focusInEvent(self, event):
        """Обработчик события получения фокуса."""
        super(CefWidget, self).focusInEvent(event)

        if not CEF_AVAILABLE:
            return

        if hasattr(self, 'browser'):
            # Уведомляем CEF о получении фокуса
            window_handle = int(self.winId())
            cef.WindowUtils().OnSetFocus(window_handle, 0, 0, 0)
            self.browser.SendFocusEvent(True)

    def focusOutEvent(self, event):
        """Обработчик события потери фокуса."""
        super(CefWidget, self).focusOutEvent(event)

        if not CEF_AVAILABLE:
            return

        if hasattr(self, 'browser'):
            self.browser.SendFocusEvent(False)


class ClientHandlers(object):
    """Обработчики событий CEF браузера."""

    def __init__(self, cef_widget):
        self.cef_widget = cef_widget

    def GetDisplayHandler(self):
        return DisplayHandler(self.cef_widget)

    def GetLoadHandler(self):
        return LoadHandler(self.cef_widget)


class DisplayHandler(object):
    """Обработчик отображения браузера."""

    def __init__(self, cef_widget):
        self.cef_widget = cef_widget

    def OnAddressChange(self, browser, frame, url):
        if frame.IsMain():
            self.cef_widget.url_changed.emit(url)

    def OnTitleChange(self, browser, title):
        self.cef_widget.title_changed.emit(title)


class LoadHandler(object):
    """Обработчик загрузки страниц браузера."""

    def __init__(self, cef_widget):
        self.cef_widget = cef_widget

    def OnLoadingStateChange(self, browser, is_loading, can_go_back, can_go_forward):
        self.cef_widget.loading_state_changed.emit(is_loading, can_go_back, can_go_forward)


def initialize_cef():
    """Инициализирует CEF."""
    if not CEF_AVAILABLE:
        print("CEF не доступен, инициализация пропущена")
        return False

    try:
        # Проверяем, не инициализирован ли CEF уже
        if not getattr(initialize_cef, "initialized", False):
            print("Инициализация CEF...")
            sys.excepthook = cef.ExceptHook  # Для захвата исключений Chromium в PyQt
            cef.Initialize(settings={
                "log_severity": cef.LOGSEVERITY_ERROR,
                "log_file": os.path.join(os.path.expanduser("~"), "cef.log"),
                "browser_subprocess_path": os.path.abspath("subprocess.exe"),
                "context_menu": {"enabled": True},
            })
            initialize_cef.initialized = True
            print("CEF инициализирован успешно")
        return True
    except Exception as e:
        print(f"Ошибка при инициализации CEF: {e}")
        return False


def shutdown_cef():
    """Завершает работу CEF."""
    if CEF_AVAILABLE and getattr(initialize_cef, "initialized", False):
        try:
            print("Завершение работы CEF...")
            cef.Shutdown()
            print("CEF успешно завершен")
        except Exception as e:
            print(f"Ошибка при завершении работы CEF: {e}")


def get_browser_widget(parent=None, start_url="https://www.google.com"):
    """Возвращает подходящий виджет браузера в зависимости от доступных библиотек."""
    if CEF_AVAILABLE:
        return CefWidget(parent, start_url)
    elif WEBENGINE_AVAILABLE:
        return WebEngineWidget(parent, start_url)
    else:
        # Создаем виджет с сообщением о недоступности браузера
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        label = QLabel("Браузер недоступен: не найдены необходимые библиотеки.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #ff5555;
                padding: 20px;
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        layout.addWidget(label)
        return widget
