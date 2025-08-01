"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

import logging
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QMenu,
    QLabel,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QUrl, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

import chardet
import traceback
import weakref
from typing import Optional, Dict, Any

# Импорт системы отображения ошибок
try:
    from .error_display import ErrorDisplayWidget, show_critical_error

    ERROR_DISPLAY_AVAILABLE = True
except ImportError:
    ErrorDisplayWidget = None
    show_critical_error = None
    ERROR_DISPLAY_AVAILABLE = False

# Импортируем продвинутый текстовый редактор
import sys
import os

# Добавляем путь к модулю GopiAI-Widgets
widgets_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "GopiAI-Widgets"
)
widgets_path = os.path.abspath(widgets_path)
if widgets_path not in sys.path:
    sys.path.insert(0, widgets_path)

try:
    from gopiai.widgets.core.text_editor import TextEditorWidget

    TEXT_EDITOR_AVAILABLE = True
except ImportError:
    TextEditorWidget = None
    TEXT_EDITOR_AVAILABLE = False

try:
    from gopiai.ui.components.rich_text_notebook_widget import NotebookEditorWidget

    NOTEBOOK_EDITOR_AVAILABLE = True
except ImportError:
    NotebookEditorWidget = None
    NOTEBOOK_EDITOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class BackgroundImageWidget(QLabel):
    """Виджет для отображения фонового изображения"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = None
        self.load_image()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)  # Мы будем масштабировать вручную

    def load_image(self):
        """Загрузка изображения"""
        try:
            if os.path.exists(self.image_path):
                self.original_pixmap = QPixmap(self.image_path)
                logger.info(f"Фоновое изображение загружено: {self.image_path}")
            else:
                logger.warning(f"Файл изображения не найден: {self.image_path}")
                # Создаем заглушку
                self.original_pixmap = QPixmap(400, 300)
                self.original_pixmap.fill(Qt.GlobalColor.lightGray)
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            # Создаем заглушку при ошибке
            self.original_pixmap = QPixmap(400, 300)
            self.original_pixmap.fill(Qt.GlobalColor.lightGray)

    def resizeEvent(self, event):
        """Обработка изменения размера для масштабирования изображения"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.scale_image()

    def scale_image(self):
        """Масштабирование изображения под размер виджета"""
        if not self.original_pixmap:
            return

        # Получаем размеры виджета
        widget_size = self.size()

        # Масштабируем изображение с сохранением пропорций
        scaled_pixmap = self.original_pixmap.scaled(
            widget_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled_pixmap)


class CustomTabWidget(QTabWidget):
    """Кастомный виджет вкладок с контекстным меню"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def contextMenuEvent(self, event):
        """Обработка правого клика для показа контекстного меню"""
        # Определяем, на какой вкладке был клик
        tab_index = self.tabBar().tabAt(event.pos())
        if tab_index == -1:
            return

        # Создаем контекстное меню
        menu = QMenu(self)

        # Опции закрытия
        close_current_action = menu.addAction("🗙 Закрыть вкладку")
        close_current_action.triggered.connect(
            lambda: self._close_tab_at_index(tab_index)
        )

        close_others_action = menu.addAction("🗙 Закрыть остальные")
        close_others_action.triggered.connect(lambda: self._close_other_tabs(tab_index))

        close_all_action = menu.addAction("🗙 Закрыть все")
        close_all_action.triggered.connect(self._close_all_tabs)

        menu.addSeparator()

        # Дополнительные опции
        close_left_action = menu.addAction("← Закрыть слева")
        close_left_action.triggered.connect(lambda: self._close_tabs_to_left(tab_index))

        close_right_action = menu.addAction("→ Закрыть справа")
        close_right_action.triggered.connect(
            lambda: self._close_tabs_to_right(tab_index)
        )

        # Отключаем опции, если они неприменимы
        if self.count() <= 1:
            close_others_action.setEnabled(False)
            close_all_action.setEnabled(False)

        if tab_index == 0:
            close_left_action.setEnabled(False)

        if tab_index == self.count() - 1:
            close_right_action.setEnabled(False)

        # Показываем меню
        menu.exec(event.globalPos())

    def _close_tab_at_index(self, index):
        """Закрытие вкладки по индексу"""
        if 0 <= index < self.count():
            self.removeTab(index)
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()

    def _close_other_tabs(self, keep_index):
        """Закрытие всех вкладок кроме указанной"""
        if keep_index < 0 or keep_index >= self.count():
            return

        # Безопасное закрытие с защитой от бесконечного цикла
        max_iterations = 100
        iteration = 0

        # Закрываем справа от keep_index
        while self.count() > keep_index + 1 and iteration < max_iterations:
            self.removeTab(keep_index + 1)
            iteration += 1

        # Закрываем слева от keep_index
        iteration = 0
        while keep_index > 0 and iteration < max_iterations:
            self.removeTab(0)
            keep_index -= 1
            iteration += 1

        if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
            self.parent_widget._update_display()

    def _close_all_tabs(self):
        """Закрытие всех вкладок"""
        # Безопасное закрытие всех вкладок с защитой от бесконечного цикла
        max_iterations = 100  # Защита от бесконечного цикла
        iteration = 0

        while self.count() > 0 and iteration < max_iterations:
            self.removeTab(0)
            iteration += 1

        if iteration >= max_iterations:
            logger.warning(
                "Достигнуто максимальное количество итераций при закрытии всех вкладок"
            )

        if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
            self.parent_widget._update_display()

    def _close_tabs_to_left(self, index):
        """Закрытие всех вкладок слева от указанной"""
        if index <= 0:
            return

        # Безопасное закрытие с защитой от бесконечного цикла
        max_iterations = 100
        iteration = 0

        while index > 0 and iteration < max_iterations:
            self.removeTab(0)
            index -= 1
            iteration += 1

        if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
            self.parent_widget._update_display()

    def _close_tabs_to_right(self, index):
        """Закрытие всех вкладок справа от указанной"""
        if index < 0 or index >= self.count() - 1:
            return

        # Безопасное закрытие с защитой от бесконечного цикла
        max_iterations = 100
        iteration = 0

        while self.count() > index + 1 and iteration < max_iterations:
            self.removeTab(index + 1)
            iteration += 1

        if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
            self.parent_widget._update_display()


class TabDocumentWidget(QWidget):
    """Центральная область с вкладками документов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabDocument")

        # Словарь для хранения ссылок на виджеты (предотвращение garbage collection)
        self._widget_references: Dict[int, Any] = {}

        # Система отображения ошибок
        self._error_display: Optional[ErrorDisplayWidget] = None

        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса вкладок"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создаем стек виджетов для переключения между фоном и вкладками
        self.stacked_widget = QStackedWidget()

        # Создаем фоновое изображение
        image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "GopiAI-Assets",
            "gopiai",
            "assets",
            "wallpaper.png",
        )
        image_path = os.path.abspath(image_path)

        self.background_widget = BackgroundImageWidget(image_path)
        self.stacked_widget.addWidget(self.background_widget)

        # Используем кастомный виджет вкладок с контекстным меню
        self.tab_widget = CustomTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

        # Дополнительные настройки для удобства
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setUsesScrollButtons(
            True
        )  # Кнопки прокрутки при множестве вкладок
        self.tab_widget.setElideMode(
            Qt.TextElideMode.ElideRight
        )  # Обрезаем длинные названия

        self.stacked_widget.addWidget(self.tab_widget)

        # Подключаем сигналы для переключения между фоном и вкладками
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._update_display)

        # Изначально показываем фон (нет вкладок)
        self.stacked_widget.setCurrentWidget(self.background_widget)

        layout.addWidget(self.stacked_widget)

        # Создаем систему отображения ошибок
        if ERROR_DISPLAY_AVAILABLE:
            self._error_display = ErrorDisplayWidget(self)
            self._error_display.setVisible(False)
            self._error_display.retryRequested.connect(self._handle_error_retry)
            self._error_display.dismissRequested.connect(self._handle_error_dismiss)
            layout.addWidget(self._error_display)

    def _update_display(self):
        """Обновление отображения в зависимости от количества вкладок"""
        if self.tab_widget.count() > 0:
            # Есть вкладки - показываем виджет вкладок
            self.stacked_widget.setCurrentWidget(self.tab_widget)
        else:
            # Нет вкладок - показываем фоновое изображение
            self.stacked_widget.setCurrentWidget(self.background_widget)

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой вкладки с текстовым редактором"""
        if TEXT_EDITOR_AVAILABLE:
            # Используем продвинутый текстовый редактор с нумерацией строк
            editor = TextEditorWidget()
            editor.text_editor.setPlainText(content)  # type: ignore
            logger.info(f"Создана вкладка с TextEditorWidget: {title}")
        else:
            # Fallback к обычному QTextEdit
            editor = QTextEdit()
            editor.setPlainText(content)
            logger.info(f"Создана вкладка с QTextEdit (fallback): {title}")

        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(index)
        self._update_display()  # Обновляем отображение
        return editor

    def add_notebook_tab(self, title="Новый блокнот", content="", menu_bar=None):
        """Добавление новой вкладки-блокнота с форматированием (чистый rich text notebook)"""
        notebook = None
        fallback_used = False

        try:
            if NOTEBOOK_EDITOR_AVAILABLE and NotebookEditorWidget:
                notebook = NotebookEditorWidget()
                if content:
                    notebook.setPlainText(content)

                # Сохраняем ссылку на виджет для предотвращения garbage collection
                widget_id = id(notebook)
                self._widget_references[widget_id] = notebook

                index = self.tab_widget.addTab(notebook, title)
                self.tab_widget.setCurrentIndex(index)
                self._update_display()  # Обновляем отображение

                # Подключаем сигналы меню к QTextEdit, если menu_bar передан
                if menu_bar is not None:
                    try:
                        menu_bar.undoRequested.connect(notebook.editor.undo)
                        menu_bar.redoRequested.connect(notebook.editor.redo)
                        menu_bar.cutRequested.connect(notebook.editor.cut)
                        menu_bar.copyRequested.connect(notebook.editor.copy)
                        menu_bar.pasteRequested.connect(notebook.editor.paste)
                        menu_bar.deleteRequested.connect(notebook.editor.clear)
                        menu_bar.selectAllRequested.connect(notebook.editor.selectAll)
                    except Exception as e:
                        logger.warning(
                            f"Не удалось подключить сигналы меню к NotebookEditorWidget: {e}"
                        )

                logger.info(f"Создана вкладка-блокнот: {title}")
                return notebook
            else:
                raise ImportError("NotebookEditorWidget недоступен")

        except Exception as e:
            logger.error(f"Ошибка создания блокнота: {e}", exc_info=True)
            fallback_used = True

            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_component_error(
                    "Блокнот", str(e), fallback_available=True
                )

            # Fallback к обычному текстовому редактору
            try:
                fallback_editor = QTextEdit()
                fallback_editor.setPlainText(content if content else "")
                fallback_editor.setAcceptRichText(
                    True
                )  # Включаем поддержку форматирования

                # Сохраняем ссылку на fallback виджет
                widget_id = id(fallback_editor)
                self._widget_references[widget_id] = fallback_editor

                index = self.tab_widget.addTab(
                    fallback_editor, f"{title} (простой редактор)"
                )
                self.tab_widget.setCurrentIndex(index)
                self._update_display()
                logger.info(f"Создана fallback вкладка-блокнот: {title}")
                return fallback_editor

            except Exception as fallback_error:
                logger.critical(
                    f"Критическая ошибка создания fallback редактора: {fallback_error}"
                )
                if self._error_display:
                    self._error_display.show_generic_error(
                        "Критическая ошибка",
                        "Не удалось создать ни основной, ни резервный редактор",
                        str(fallback_error),
                    )
                elif show_critical_error:
                    show_critical_error(
                        "Не удалось создать редактор",
                        f"Основная ошибка: {str(e)}\nОшибка fallback: {str(fallback_error)}",
                        self,
                    )
                return None

    def open_file_in_tab(self, file_path):
        """Открытие файла в новой вкладке"""
        try:
            if TEXT_EDITOR_AVAILABLE:
                # Создаем текстовый редактор
                editor = TextEditorWidget()
                editor.current_file = file_path
                with open(file_path, "rb") as f:
                    raw = f.read()
                encoding = chardet.detect(raw)["encoding"] or "utf-8"
                text = raw.decode(encoding, errors="replace")
                editor.current_encoding = encoding
                editor.text_editor.setPlainText(text)
                tab_title = os.path.basename(file_path)
                editor.file_name_changed.connect(
                    lambda name: self._update_tab_title(editor, name)
                )
                logger.info(f"Файл открыт в TextEditorWidget: {file_path}")
            else:
                # Fallback к обычному редактору
                editor = QTextEdit()
                with open(file_path, "rb") as f:
                    raw = f.read()
                encoding = chardet.detect(raw)["encoding"] or "utf-8"
                content = raw.decode(encoding, errors="replace")
                editor.setPlainText(content)
                tab_title = os.path.basename(file_path)  # type: ignore
                logger.info(f"Файл открыт в QTextEdit (fallback): {file_path}")

            # Добавляем вкладку
            index = self.tab_widget.addTab(editor, tab_title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()  # Обновляем отображение
            return editor

        except Exception as e:  # type: ignore
            logger.error(f"Ошибка открытия файла {file_path}: {e}", exc_info=True)
            # Создаем вкладку с сообщением об ошибке
            error_tab = QTextEdit()
            error_tab.setPlainText(f"Ошибка открытия файла:\n{file_path}\n\n{str(e)}")
            error_tab.setReadOnly(True)
            index = self.tab_widget.addTab(error_tab, "Ошибка")
            self.tab_widget.setCurrentIndex(index)
            self._update_display()  # Обновляем отображение
            return error_tab

    def _update_tab_title(self, editor_widget, new_title):
        """Обновление заголовка вкладки"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == editor_widget:
                self.tab_widget.setTabText(i, new_title)
                break

    def _close_tab(self, index):
        """Закрытие вкладки по индексу"""
        if self.tab_widget.count() > 0 and 0 <= index < self.tab_widget.count():
            # Получаем виджет перед закрытием
            widget = self.tab_widget.widget(index)

            # Удаляем ссылку из словаря для освобождения памяти
            if widget:
                widget_id = id(widget)
                if widget_id in self._widget_references:
                    del self._widget_references[widget_id]

            # Закрываем вкладку
            self.tab_widget.removeTab(index)
            self._update_display()  # Обновляем отображение после закрытия

    def add_browser_tab(self, url="about:blank", title="Браузер"):
        """Добавление новой вкладки с браузером"""  # type: ignore
        logger.info(f"Создаем встроенный браузер...")
        try:
            # Создаем главный виджет браузера
            browser_widget = QWidget()
            browser_layout = QVBoxLayout(browser_widget)
            browser_layout.setContentsMargins(5, 5, 5, 5)
            browser_layout.setSpacing(2)

            # ==============================================
            # Панель навигации с адресной строкой
            # ==============================================
            nav_layout = QHBoxLayout()
            nav_layout.setContentsMargins(0, 0, 0, 0)
            nav_layout.setSpacing(5)

            # Кнопка "Назад"
            back_btn = QPushButton("←")
            back_btn.setFixedSize(30, 30)
            back_btn.setToolTip("Назад")
            back_btn.setObjectName("browserBackBtn")

            # Кнопка "Вперед"
            forward_btn = QPushButton("→")
            forward_btn.setFixedSize(30, 30)
            forward_btn.setToolTip("Вперед")
            forward_btn.setObjectName("browserForwardBtn")

            # Кнопка "Обновить"
            refresh_btn = QPushButton("↻")
            refresh_btn.setFixedSize(30, 30)
            refresh_btn.setToolTip("Обновить")
            refresh_btn.setObjectName("browserRefreshBtn")

            # Адресная строка
            address_bar = QLineEdit()
            address_bar.setPlaceholderText("Введите URL или поисковый запрос...")
            address_bar.setObjectName("browserAddressBar")

            # Кнопка "Перейти"
            go_btn = QPushButton("➤")
            go_btn.setFixedSize(30, 30)
            go_btn.setToolTip("Перейти")
            go_btn.setObjectName("browserGoBtn")

            # Добавляем элементы в панель навигации
            nav_layout.addWidget(back_btn)
            nav_layout.addWidget(forward_btn)
            nav_layout.addWidget(refresh_btn)
            nav_layout.addWidget(address_bar)
            nav_layout.addWidget(go_btn)

            # ==============================================
            # Веб-браузер с ПЕРСИСТЕНТНЫМ ПРОФИЛЕМ
            # ==============================================

            # 🔥 ИСПРАВЛЕНИЕ: Создаем персистентный профиль для сохранения данных
            import os
            from pathlib import Path
            from PySide6.QtWebEngineCore import QWebEngineProfile

            # Создаем папку для профиля браузера в рабочей директории
            profile_dir = Path.home() / ".gopiai" / "browser_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)

            # Создаем персистентный профиль (НЕ defaultProfile!)
            profile = QWebEngineProfile("GopiAI_Browser", browser_widget)

            # 🔧 Настраиваем сохранение данных
            profile.setPersistentStoragePath(str(profile_dir))
            profile.setCachePath(str(profile_dir / "cache"))
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB cache

            # 🔒 Настройки безопасности и удобства
            settings = profile.settings()
            settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(settings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(
                settings.WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            settings.setAttribute(
                settings.WebAttribute.LocalContentCanAccessFileUrls, True
            )

            # Создаем веб-вью с нашим персистентным профилем
            web_view = QWebEngineView()

            web_page = QWebEnginePage(profile, web_view)
            web_view.setPage(web_page)
            web_view.setMinimumSize(800, 600)

            # Принудительно показываем
            web_view.show()
            web_view.setVisible(True)

            logger.info(f"🔥 Браузер создан с персистентным профилем: {profile_dir}")

            # ==============================================
            # Подключение сигналов навигации
            # ==============================================
            def navigate_back():
                if web_view.history().canGoBack():
                    web_view.back()

            def navigate_forward():
                if web_view.history().canGoForward():
                    web_view.forward()

            def refresh_page():
                web_view.reload()

            def navigate_to_url():
                url_text = address_bar.text().strip()
                if not url_text:
                    return

                # Если не содержит протокол, добавляем https://
                if not url_text.startswith(
                    ("http://", "https://", "file://", "about:")
                ):
                    # Проверяем, выглядит ли это как URL
                    if "." in url_text and " " not in url_text:
                        url_text = "https://" + url_text
                    else:
                        # Выглядит как поисковый запрос
                        url_text = f"https://google.com/search?q={url_text}"

                logger.info(f"📡 Переходим к URL: {url_text}")
                web_view.load(QUrl(url_text))

            def update_address_bar(qurl):
                """Обновление адресной строки при изменении URL"""
                address_bar.setText(qurl.toString())

            def update_navigation_buttons():
                """Обновление состояния кнопок навигации"""
                back_btn.setEnabled(web_view.history().canGoBack())
                forward_btn.setEnabled(web_view.history().canGoForward())

            # Подключаем сигналы
            back_btn.clicked.connect(navigate_back)
            forward_btn.clicked.connect(navigate_forward)
            refresh_btn.clicked.connect(refresh_page)
            go_btn.clicked.connect(navigate_to_url)
            address_bar.returnPressed.connect(navigate_to_url)

            # Обновляем адресную строку при изменении URL
            web_view.urlChanged.connect(update_address_bar)
            web_view.loadFinished.connect(lambda: update_navigation_buttons())

            # ==============================================
            # Сборка интерфейса
            # ==============================================
            browser_layout.addLayout(nav_layout)
            browser_layout.addWidget(web_view)

            # Сохраняем ссылки на компоненты для доступа извне
            browser_widget.setProperty("_web_view", web_view)
            browser_widget.setProperty("_address_bar", address_bar)
            browser_widget.setProperty("_back_btn", back_btn)
            browser_widget.setProperty("_forward_btn", forward_btn)
            browser_widget.setProperty("_refresh_btn", refresh_btn)
            browser_widget.setProperty(
                "_profile", profile
            )  # 🔥 Сохраняем ссылку на профиль

            # Добавляем вкладку
            index = self.tab_widget.addTab(browser_widget, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()  # Обновляем отображение

            # Загружаем URL
            if url and url != "about:blank":
                logger.info(f"📡 Загружаем URL: {url}")
                address_bar.setText(url)
            else:
                # Загрузка Google
                url = "https://google.com"
                logger.info(f"📡 Загружаем Google")
                address_bar.setText(url)

            web_view.load(QUrl(url))

            logger.info(f"✅ Веб-страница с персистентным профилем загружена: {url}")
            return browser_widget

        except Exception as e:
            print(f"Ошибка при создании браузера: {e}")
            traceback.print_exc()
            return self._create_fallback_browser_tab(f"Ошибка: {str(e)}")

    def _create_fallback_browser_tab(self, error_msg):
        """Создает резервную вкладку с информацией об ошибке"""
        fallback_tab = QTextEdit()
        fallback_tab.setPlainText(
            f"""Браузер недоступен

{error_msg}

🔧 Возможные решения:
• Проверьте установку QWebEngineView
• Убедитесь, что Qt модуль WebEngine включен
• Попробуйте переустановить PySide6 с WebEngine: pip install PySide6[webengine]
"""
        )
        fallback_tab.setReadOnly(True)
        index = self.tab_widget.addTab(fallback_tab, "Браузер недоступен")
        self.tab_widget.setCurrentIndex(index)
        self._update_display()  # Обновляем отображение
        return fallback_tab

    def close_current_tab(self):
        """Закрытие текущей вкладки"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0 and self.tab_widget.count() > 1:
            self.tab_widget.removeTab(current_index)
            self._update_display()  # Обновляем отображение

    def get_current_editor(self):
        """Получение текущего редактора"""
        current_widget = self.tab_widget.currentWidget()

        # Проверяем, является ли это TextEditorWidget
        if TEXT_EDITOR_AVAILABLE and isinstance(current_widget, TextEditorWidget):
            return getattr(current_widget, "text_editor", None)
        elif isinstance(current_widget, QTextEdit):
            return current_widget
        return None

    def get_current_text(self):
        """Получение текста из текущей вкладки"""
        editor = self.get_current_editor()
        if editor:
            return editor.toPlainText()
        return ""

    def set_current_text(self, text):
        """Установка текста в текущую вкладку"""
        editor = self.get_current_editor()
        if editor:
            editor.setPlainText(text)

    def _handle_error_retry(self, error_type: str):
        """Обработка запроса повтора операции после ошибки"""
        logger.info(f"Повторная попытка операции после ошибки: {error_type}")
        
        # Скрываем сообщение об ошибке
        if self._error_display:
            self._error_display.setVisible(False)
        
        # В зависимости от типа ошибки, пытаемся повторить операцию
        if error_type == "notebook_creation":
            self.add_notebook_tab("Новый блокнот (повтор)")
        elif error_type == "tab_creation":
            self.add_new_tab("Новый документ (повтор)")
        elif error_type == "file_open":
            logger.info("Для повтора открытия файла требуется указать путь")

    def _handle_error_dismiss(self):
        """Обработка закрытия сообщения об ошибке"""
        if self._error_display:
            self._error_display.setVisible(False)

    def _safe_tab_creation(self, creation_func, fallback_func, error_context: str):
        """
        Безопасное создание вкладки с обработкой ошибок и fallback
        
        Args:
            creation_func: Основная функция создания вкладки
            fallback_func: Резервная функция при ошибке
            error_context: Контекст ошибки для логирования
        """
        try:
            return creation_func()
        except Exception as e:
            logger.error(f"Ошибка {error_context}: {e}", exc_info=True)
            
            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_component_error(
                    error_context, str(e), fallback_available=True
                )
            
            # Пытаемся использовать fallback
            try:
                return fallback_func()
            except Exception as fallback_error:
                logger.critical(f"Критическая ошибка fallback для {error_context}: {fallback_error}")
                if self._error_display:
                    self._error_display.show_generic_error(
                        "Критическая ошибка",
                        f"Не удалось создать {error_context}",
                        str(fallback_error)
                    )
                elif show_critical_error:
                    show_critical_error(
                        f"Критическая ошибка {error_context}",
                        f"Основная ошибка: {str(e)}\nОшибка fallback: {str(fallback_error)}",
                        self
                    )
                return None

    def add_notebook_tab_safe(self, title="Новый блокнот", content="", menu_bar=None):
        """Безопасное добавление вкладки-блокнота с обработкой ошибок"""
        
        def create_notebook():
            if not NOTEBOOK_EDITOR_AVAILABLE or not NotebookEditorWidget:
                raise ImportError("NotebookEditorWidget недоступен")
            
            notebook = NotebookEditorWidget()
            if content:
                notebook.setPlainText(content)

            # Сохраняем ссылку на виджет для предотвращения garbage collection
            widget_id = id(notebook)
            self._widget_references[widget_id] = notebook

            index = self.tab_widget.addTab(notebook, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()

            # Подключаем сигналы меню к QTextEdit, если menu_bar передан
            if menu_bar is not None:
                try:
                    menu_bar.undoRequested.connect(notebook.editor.undo)
                    menu_bar.redoRequested.connect(notebook.editor.redo)
                    menu_bar.cutRequested.connect(notebook.editor.cut)
                    menu_bar.copyRequested.connect(notebook.editor.copy)
                    menu_bar.pasteRequested.connect(notebook.editor.paste)
                    menu_bar.deleteRequested.connect(notebook.editor.clear)
                    menu_bar.selectAllRequested.connect(notebook.editor.selectAll)
                except Exception as e:
                    logger.warning(f"Не удалось подключить сигналы меню: {e}")

            logger.info(f"Создана вкладка-блокнот: {title}")
            return notebook
        
        def create_fallback():
            fallback_editor = QTextEdit()
            fallback_editor.setPlainText(content if content else "")
            fallback_editor.setAcceptRichText(True)

            # Сохраняем ссылку на fallback виджет
            widget_id = id(fallback_editor)
            self._widget_references[widget_id] = fallback_editor

            index = self.tab_widget.addTab(fallback_editor, f"{title} (простой редактор)")
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Создана fallback вкладка-блокнот: {title}")
            return fallback_editor
        
        return self._safe_tab_creation(create_notebook, create_fallback, "создания блокнота")

    def add_new_tab_safe(self, title="Новый документ", content=""):
        """Безопасное добавление новой вкладки с обработкой ошибок"""
        
        def create_text_editor():
            if not TEXT_EDITOR_AVAILABLE or not TextEditorWidget:
                raise ImportError("TextEditorWidget недоступен")
            
            editor = TextEditorWidget()
            editor.text_editor.setPlainText(content)
            
            # Сохраняем ссылку на виджет
            widget_id = id(editor)
            self._widget_references[widget_id] = editor
            
            index = self.tab_widget.addTab(editor, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Создана вкладка с TextEditorWidget: {title}")
            return editor
        
        def create_fallback():
            editor = QTextEdit()
            editor.setPlainText(content)
            
            # Сохраняем ссылку на fallback виджет
            widget_id = id(editor)
            self._widget_references[widget_id] = editor
            
            index = self.tab_widget.addTab(editor, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Создана вкладка с QTextEdit (fallback): {title}")
            return editor
        
        return self._safe_tab_creation(create_text_editor, create_fallback, "создания текстового редактора")

    def open_file_in_tab_safe(self, file_path):
        """Безопасное открытие файла в новой вкладке с обработкой ошибок"""
        
        def create_file_editor():
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            
            if TEXT_EDITOR_AVAILABLE and TextEditorWidget:
                editor = TextEditorWidget()
                editor.current_file = file_path
                
                with open(file_path, "rb") as f:
                    raw = f.read()
                encoding = chardet.detect(raw)["encoding"] or "utf-8"
                text = raw.decode(encoding, errors="replace")
                editor.current_encoding = encoding
                editor.text_editor.setPlainText(text)
                
                tab_title = os.path.basename(file_path)
                editor.file_name_changed.connect(
                    lambda name: self._update_tab_title(editor, name)
                )
                
                # Сохраняем ссылку на виджет
                widget_id = id(editor)
                self._widget_references[widget_id] = editor
                
                index = self.tab_widget.addTab(editor, tab_title)
                self.tab_widget.setCurrentIndex(index)
                self._update_display()
                
                logger.info(f"Файл открыт в TextEditorWidget: {file_path}")
                return editor
            else:
                raise ImportError("TextEditorWidget недоступен")
        
        def create_fallback():
            with open(file_path, "rb") as f:
                raw = f.read()
            encoding = chardet.detect(raw)["encoding"] or "utf-8"
            content = raw.decode(encoding, errors="replace")
            
            editor = QTextEdit()
            editor.setPlainText(content)
            tab_title = os.path.basename(file_path)
            
            # Сохраняем ссылку на fallback виджет
            widget_id = id(editor)
            self._widget_references[widget_id] = editor
            
            index = self.tab_widget.addTab(editor, tab_title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Файл открыт в QTextEdit (fallback): {file_path}")
            return editor
        
        return self._safe_tab_creation(create_file_editor, create_fallback, f"открытия файла {file_path}")

    def _cleanup_tab_widget(self, widget):
        """Очистка ресурсов виджета вкладки"""
        if not widget:
            return
        
        try:
            # Удаляем ссылку из словаря для освобождения памяти
            widget_id = id(widget)
            if widget_id in self._widget_references:
                del self._widget_references[widget_id]
                logger.debug(f"Удалена ссылка на виджет {widget_id}")
            
            # Специальная очистка для браузера
            if hasattr(widget, 'property'):
                web_view = widget.property("_web_view")
                profile = widget.property("_profile")
                
                if web_view:
                    try:
                        web_view.stop()
                        web_view.setPage(None)
                        logger.debug("Очищен веб-браузер")
                    except Exception as e:
                        logger.warning(f"Ошибка очистки веб-браузера: {e}")
                
                if profile:
                    try:
                        # Профиль будет автоматически очищен при удалении виджета
                        logger.debug("Профиль браузера будет очищен")
                    except Exception as e:
                        logger.warning(f"Ошибка очистки профиля браузера: {e}")
            
            # Очистка текстовых редакторов
            if hasattr(widget, 'text_editor'):
                try:
                    widget.text_editor.clear()
                    logger.debug("Очищен текстовый редактор")
                except Exception as e:
                    logger.warning(f"Ошибка очистки текстового редактора: {e}")
            
            # Общая очистка QWidget
            try:
                widget.deleteLater()
                logger.debug("Виджет помечен для удаления")
            except Exception as e:
                logger.warning(f"Ошибка при deleteLater: {e}")
                
        except Exception as e:
            logger.error(f"Ошибка очистки виджета вкладки: {e}", exc_info=True)
        logger.info(f"Запрос повтора операции для типа ошибки: {error_type}")

        if error_type == "component":
            # Попытка пересоздания компонента
            try:
                # Здесь можно добавить логику повтора создания компонента
                if self._error_display:
                    self._error_display.setVisible(False)
            except Exception as e:
                logger.error(f"Ошибка при повторе операции: {e}")

    def _handle_error_dismiss(self):
        """Обработка закрытия ошибки"""
        logger.debug("Ошибка закрыта пользователем")

    def add_terminal_tab(self, title="Терминал"):
        """Добавление новой вкладки с терминалом"""
        try:
            # Импортируем TerminalWidget локально для избежания циклических импортов
            from .terminal_widget import InteractiveTerminal

            terminal = InteractiveTerminal()

            # Сохраняем ссылку на виджет
            widget_id = id(terminal)
            self._widget_references[widget_id] = terminal

            index = self.tab_widget.addTab(terminal, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()

            logger.info(f"Создана вкладка терминала: {title}")
            return terminal

        except Exception as e:
            logger.error(f"Ошибка создания вкладки терминала: {e}", exc_info=True)

            if self._error_display:
                self._error_display.show_component_error(
                    "Терминал", str(e), fallback_available=False
                )
            elif show_critical_error:
                show_critical_error(
                    "Ошибка создания терминала",
                    f"Не удалось создать вкладку терминала: {str(e)}",
                    self,
                )
            return None

    def _handle_tab_creation_error(
        self, error: Exception, component_name: str, fallback_available: bool = False
    ):
        """Централизованная обработка ошибок создания вкладок"""
        logger.error(
            f"Ошибка создания вкладки {component_name}: {error}", exc_info=True
        )

        if self._error_display:
            self._error_display.show_component_error(
                component_name, str(error), fallback_available=fallback_available
            )
        elif show_critical_error:
            show_critical_error(f"Ошибка создания {component_name}", str(error), self)

    def cleanup_widget_references(self):
        """Очистка ссылок на виджеты при закрытии"""
        self._widget_references.clear()
        logger.debug("Очищены ссылки на виджеты")
