#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################
#                                                           #
#   ВНИМАНИЕ!                                               #
#   Это минимальный main window приложения GopiAI!           #
#   НЕ ДОБАВЛЯТЬ сюда никакие визуальные эффекты,            #
#   декорации, рамки, анимации, плавающие окна и т.д.!       #
#   Всё красивое — только в отдельные модули!                #
#   Здесь — только базовая логика и минимум UI!              #
#                                                           #
#   Если хочется добавить красоту — см. assets/decorative_layers.py #
#                                                           #
#   Нарушение этого правила = 🐰 будет грустить!              #
###############################################################

"""
Минимальная версия приложения GopiAI.
Содержит только главное окно, текстовый редактор и меню Файл с пунктами Открыть и Сохранить.
Использует frameless окно со своей панелью заголовка.
"""

import os
import sys
import logging
import chardet

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QMessageBox, QMenu, QMenuBar,
    QPushButton, QLabel, QSizePolicy, QDialog, QColorDialog, QTabWidget, QTabBar
)
from PySide6.QtGui import QAction, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QSettings

# Импорт иконок
try:
    from icons import get_icon
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False
    get_icon = lambda x: ""

# Импортируем функционал тем
try:
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
except Exception as e:
    print(f"Ошибка при настройке логирования: {e}")

# Импортируем новый диалог выбора темы
from simple_theme_manager import choose_theme_dialog, apply_theme, load_theme, _is_light
from assets.titlebar_with_menu import TitlebarWithMenu
from widgets.custom_grips import CustomGrip

# --- Текстовый редактор ---
class TextEditorWidget(QWidget):
    """Виджет для текстового редактора."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.current_encoding = "utf-8"
        self.settings = QSettings("GopiAI", "MinimalVersion")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.text_editor = QTextEdit()
        layout.addWidget(self.text_editor)
        logger.info("Текстовый редактор инициализирован")
    def open_file(self):
        logger.info("Открытие файла...")
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)")
        if file_path:
            try:
                with open(file_path, "rb") as raw_file:
                    raw_data = raw_file.read()
                detected = chardet.detect(raw_data)
                encoding = detected["encoding"] if detected["encoding"] else "utf-8"
                try:
                    content = raw_data.decode(encoding)
                except UnicodeDecodeError:
                    fallback_encodings = ["cp1251", "latin-1", "utf-16", "ascii"]
                    for enc in fallback_encodings:
                        try:
                            content = raw_data.decode(enc)
                            encoding = enc
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        content = raw_data.decode("latin-1")
                        encoding = "latin-1"
                self.text_editor.setText(content)
                self.current_file = file_path
                self.current_encoding = encoding
                main_window = self.window()
                if hasattr(main_window, "update_title"):
                    main_window.update_title(os.path.basename(file_path))
                logger.info(f"Файл открыт: {file_path} (кодировка: {encoding})")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")
                logger.error(f"Ошибка при открытии файла: {e}")
    def save_file(self):
        logger.info("Сохранение файла...")
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    def save_file_as(self):
        logger.info("Сохранение файла с новым именем...")
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы (*)")
        if file_path:
            self._save_to_file(file_path)
    def _save_to_file(self, file_path):
        try:
            encoding = "utf-8"
            with open(file_path, "w", encoding=encoding) as f:
                f.write(self.text_editor.toPlainText())
            main_window = self.window()
            if hasattr(main_window, "update_title"):
                main_window.update_title(os.path.basename(file_path))
            logger.info(f"Файл сохранен: {file_path} (кодировка: {encoding})")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
            logger.error(f"Ошибка при сохранении файла: {e}")
    def show_theme_collection_dialog(self):
        app = QApplication.instance()
        choose_theme_dialog(app)

# --- Функция для base64 -> QPixmap ---
def base64_to_pixmap(base64_str):
    try:
        cleaned_base64 = base64_str.replace("\n", "").replace("\r", "").replace(" ", "").replace("\t", "")
        if not cleaned_base64:
            logger.error("Пустая строка base64 после очистки")
            return QPixmap()
        import base64
        image_data = base64.b64decode(cleaned_base64)
        pixmap = QPixmap()
        success = pixmap.loadFromData(image_data)
        if not success or pixmap.isNull():
            logger.error("Не удалось загрузить данные изображения в QPixmap")
            return QPixmap()
        return pixmap
    except Exception as e:
        logger.error(f"Ошибка при преобразовании base64 в QPixmap: {e}")
        return QPixmap()


# --- FramelessMainWindow ---
class FramelessEditorWindow(QMainWindow):
    def __init__(self, editor_widget, title, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setObjectName("framelessEditorWindow")
        self.setMinimumSize(400, 300)
        self.editor_widget = editor_widget
        self.setCentralWidget(editor_widget)
        self.setWindowTitle(title)
        self._drag_active = False
        self._drag_pos = None
        # Кнопка 'Прикрепить обратно'
        self.attach_btn = QPushButton("⤺", self)
        self.attach_btn.setToolTip("Прикрепить обратно во вкладку")
        self.attach_btn.setFixedSize(32, 32)
        self.attach_btn.move(self.width() - 40, 8)
        self.attach_btn.clicked.connect(self.attach_back)
        self.attach_btn.raise_()
        self.attach_btn.setStyleSheet("border-radius: 16px; background: #eee; font-size: 18px; font-weight: bold;")
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.attach_btn.move(self.width() - 40, 8)
    def showEvent(self, event):
        super().showEvent(event)
        # Ставим фокус на QTextEdit, если есть
        te = getattr(self.editor_widget, 'text_editor', None)
        if te:
            te.setFocus()
    def attach_back(self):
        # Импортируем главное окно и возвращаем редактор обратно
        main_window = None
        for w in QApplication.topLevelWidgets():
            if isinstance(w, FramelessMainWindow):
                main_window = w
                break
        if main_window:
            main_window.attach_tab_by_widget(self.editor_widget, self.windowTitle())

class FramelessMainWindow(QMainWindow):
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setObjectName("framelessMainWindow")
        self.setMinimumSize(800, 600)
        # --- Titlebar + Menu ---
        self.titlebar_with_menu = TitlebarWithMenu(self)
        self.titlebar_with_menu.set_window(self)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.vertical_layout = QVBoxLayout(self.central_widget)
        self.vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.vertical_layout.setSpacing(15)
        self.vertical_layout.addWidget(self.titlebar_with_menu)
        # --- Tab workspace ---
        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.vertical_layout.addWidget(self.tab_widget, 1)
        # --- Открыть первую вкладку ---
        self.open_text_editor()
        # --- Drag support ---
        self._drag_active = False
        self._drag_pos = None
        # --- Меню: подключение выбора темы ---
        self._connect_theme_menu()
        self._apply_tab_theme()
        # --- Resize grips ---
        self._init_grips()
        self._detached_windows = []
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self._show_tab_context_menu)
    def _connect_theme_menu(self):
        # Находим пункт 'Тема' в меню 'Вид' и подключаем к нему choose_theme_dialog
        menubar = self.titlebar_with_menu.menubar
        for action in menubar.actions():
            menu = action.menu()
            if menu and menu.title() == "Вид":
                for subaction in menu.actions():
                    if subaction.text() == "Тема":
                        subaction.triggered.connect(self._show_theme_dialog)
    def _apply_tab_theme(self):
        theme = load_theme() or {}
        tab_color = theme.get("control_color") or theme.get("header_color") or "#cccccc"
        active_color = theme.get("accent_color") or tab_color
        border_color = theme.get("border_color") or tab_color
        # Автоопределение цвета текста для вкладок
        def get_tab_text_color(bg):
            try:
                return "#222" if _is_light(bg) else "#fff"
            except Exception:
                return "#222"
        text_color = get_tab_text_color(tab_color)
        active_text_color = get_tab_text_color(active_color)
        self.tab_widget.setStyleSheet(f"""
            QTabBar::tab {{
                background: {tab_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 6px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {active_color};
                color: {active_text_color};
                border: 1px solid {border_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: 8px;
                top: -1px;
            }}
        """)
    def _show_theme_dialog(self):
        app = QApplication.instance()
        choose_theme_dialog(app)
        self._apply_tab_theme()
    def open_text_editor(self, filename=None):
        editor = TextEditorWidget(self)
        idx = self.tab_widget.addTab(editor, filename or "Новый файл")
        self.tab_widget.setCurrentIndex(idx)
    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget.deleteLater()
    def update_title(self, filename=None):
        if filename:
            self.titlebar_with_menu.update_title(filename)
        else:
            self.titlebar_with_menu.update_title("GopiAI - Минимальная версия")
    def maximize_window(self):
        self.titlebar_with_menu.maximize_window()
    def restore_window(self):
        self.titlebar_with_menu.restore_window()
    def _init_grips(self):
        self._grip_top = CustomGrip(self, Qt.TopEdge)
        self._grip_bottom = CustomGrip(self, Qt.BottomEdge)
        self._grip_left = CustomGrip(self, Qt.LeftEdge)
        self._grip_right = CustomGrip(self, Qt.RightEdge)
        self._update_grips()
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_grips()
    def _update_grips(self):
        margin = 0
        w, h = self.width(), self.height()
        self._grip_top.setGeometry(margin, margin, w - 2 * margin, 10)
        self._grip_bottom.setGeometry(margin, h - 10 - margin, w - 2 * margin, 10)
        self._grip_left.setGeometry(margin, 10 + margin, 10, h - 20 - 2 * margin)
        self._grip_right.setGeometry(w - 10 - margin, 10 + margin, 10, h - 20 - 2 * margin)
    def _show_tab_context_menu(self, pos):
        index = self.tab_widget.tabBar().tabAt(pos)
        if index < 0:
            return
        widget = self.tab_widget.widget(index)
        menu = QMenu(self)
        if not hasattr(widget, '_detached_window') or widget._detached_window is None:
            menu.addAction("Открепить (Detach)", lambda: self.detach_tab(index))
        else:
            menu.addAction("Прикрепить обратно (Attach)", lambda: self.attach_tab_by_widget(widget, self.tab_widget.tabText(index)))
        menu.exec(self.tab_widget.mapToGlobal(pos))
    def detach_tab(self, index):
        widget = self.tab_widget.widget(index)
        title = self.tab_widget.tabText(index)
        self.tab_widget.removeTab(index)
        win = FramelessEditorWindow(widget, title)
        widget._detached_window = win
        self._detached_windows.append(win)
        win.show()
        win.setAttribute(Qt.WA_DeleteOnClose)
        def on_close():
            if hasattr(widget, '_detached_window'):
                widget._detached_window = None
            if win in self._detached_windows:
                self._detached_windows.remove(win)
            self.attach_tab_by_widget(widget, title)
        win.destroyed.connect(on_close)
    def attach_tab_by_widget(self, widget, title):
        if hasattr(widget, '_detached_window') and widget._detached_window:
            widget._detached_window.close()
            widget._detached_window = None
        idx = self.tab_widget.addTab(widget, title)
        self.tab_widget.setCurrentIndex(idx)

# --- UI для выбора темы и акцента ---
class FramelessColorDialog(QColorDialog):
    def __init__(self, initial, parent=None):
        super().__init__(initial, parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self._drag_active = False
        self._drag_pos = None
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)

def get_frameless_color_dialog(initial, parent, title):
    dlg = FramelessColorDialog(initial, parent)
    dlg.setWindowTitle(title)
    dlg.setOption(QColorDialog.ShowAlphaChannel, False)
    if dlg.exec() == QDialog.Accepted:
        return dlg.selectedColor()
    return initial

def main():
    """Основная функция программы."""
    app = QApplication(sys.argv)
    # Автоматически применяем тему при запуске
    apply_theme(app)
    # Создаем и отображаем главное окно
    main_window = FramelessMainWindow()
    main_window.show()
    try:
        result = app.exec()
    except Exception as e:
        logger.error(f"Ошибка в цикле событий: {e}")
        result = 1
    finally:
        sys.exit(result)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
