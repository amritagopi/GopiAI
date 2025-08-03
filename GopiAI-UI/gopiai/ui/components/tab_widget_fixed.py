"""
Исправленная версия Tab Widget Component для GopiAI
==================================================

Упрощенная версия с надежным управлением вкладками
"""

import logging
import os
import weakref
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextEdit, QMenu, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class BackgroundImageWidget(QLabel):
    """Виджет для отображения фонового изображения"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = None
        self.load_image()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)

    def load_image(self):
        """Загрузка изображения"""
        try:
            if os.path.exists(self.image_path):
                self.original_pixmap = QPixmap(self.image_path)
                logger.info(f"Фоновое изображение загружено: {self.image_path}")
            else:
                logger.warning(f"Файл изображения не найден: {self.image_path}")
                self.original_pixmap = QPixmap(400, 300)
                self.original_pixmap.fill(Qt.GlobalColor.lightGray)
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
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

        widget_size = self.size()
        scaled_pixmap = self.original_pixmap.scaled(
            widget_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled_pixmap)


class EnhancedTabWidget(QTabWidget):
    """Улучшенный виджет вкладок с надежным контекстным меню"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._operation_in_progress = False

    def contextMenuEvent(self, event):
        """Обработка правого клика для показа контекстного меню"""
        try:
            tab_index = self.tabBar().tabAt(event.pos())
            if tab_index == -1:
                return

            if not (0 <= tab_index < self.count()):
                return

            menu = QMenu(self)
            
            # Основные операции
            close_current = menu.addAction("🗙 Закрыть вкладку")
            close_current.triggered.connect(lambda: self._safe_close_tab(tab_index))

            close_others = menu.addAction("🗙 Закрыть остальные")
            close_others.triggered.connect(lambda: self._safe_close_others(tab_index))

            close_all = menu.addAction("🗙 Закрыть все")
            close_all.triggered.connect(self._safe_close_all)

            menu.addSeparator()

            close_left = menu.addAction("← Закрыть слева")
            close_left.triggered.connect(lambda: self._safe_close_left(tab_index))

            close_right = menu.addAction("→ Закрыть справа")
            close_right.triggered.connect(lambda: self._safe_close_right(tab_index))

            # Отключаем неприменимые опции
            if self.count() <= 1:
                close_others.setEnabled(False)
                close_all.setEnabled(False)

            if tab_index == 0:
                close_left.setEnabled(False)

            if tab_index == self.count() - 1:
                close_right.setEnabled(False)

            menu.exec(event.globalPos())

        except Exception as e:
            logger.error(f"Ошибка контекстного меню: {e}")

    def _safe_close_tab(self, index):
        """Безопасное закрытие одной вкладки"""
        try:
            if self._operation_in_progress:
                return

            if not (0 <= index < self.count()):
                return

            self._operation_in_progress = True
            
            # Получаем виджет для очистки
            widget = self.widget(index)
            if widget and self.parent_widget:
                self.parent_widget._cleanup_widget(widget)

            # Закрываем вкладку
            self.removeTab(index)
            
            # Обновляем отображение
            if self.parent_widget:
                self.parent_widget._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладки {index}: {e}")
        finally:
            self._operation_in_progress = False

    def _safe_close_others(self, keep_index):
        """Безопасное закрытие всех вкладок кроме указанной"""
        try:
            if self._operation_in_progress:
                return

            if not (0 <= keep_index < self.count()):
                return

            self._operation_in_progress = True
            
            # Собираем индексы для закрытия
            to_close = []
            for i in range(self.count()):
                if i != keep_index:
                    to_close.append(i)

            # Закрываем в обратном порядке (справа налево)
            for index in reversed(to_close):
                if index < self.count():
                    widget = self.widget(index)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_widget(widget)
                    self.removeTab(index)

            # Обновляем отображение
            if self.parent_widget:
                self.parent_widget._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия других вкладок: {e}")
        finally:
            self._operation_in_progress = False

    def _safe_close_all(self):
        """Безопасное закрытие всех вкладок"""
        try:
            if self._operation_in_progress:
                return

            self._operation_in_progress = True
            
            # Закрываем все вкладки в обратном порядке
            while self.count() > 0:
                widget = self.widget(self.count() - 1)
                if widget and self.parent_widget:
                    self.parent_widget._cleanup_widget(widget)
                self.removeTab(self.count() - 1)

            # Обновляем отображение
            if self.parent_widget:
                self.parent_widget._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия всех вкладок: {e}")
        finally:
            self._operation_in_progress = False

    def _safe_close_left(self, index):
        """Безопасное закрытие вкладок слева"""
        try:
            if self._operation_in_progress or index <= 0:
                return

            self._operation_in_progress = True
            
            # Закрываем вкладки слева в обратном порядке
            for i in range(index - 1, -1, -1):
                if i < self.count():
                    widget = self.widget(i)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_widget(widget)
                    self.removeTab(i)

            # Обновляем отображение
            if self.parent_widget:
                self.parent_widget._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладок слева: {e}")
        finally:
            self._operation_in_progress = False

    def _safe_close_right(self, index):
        """Безопасное закрытие вкладок справа"""
        try:
            if self._operation_in_progress or index >= self.count() - 1:
                return

            self._operation_in_progress = True
            
            # Закрываем вкладки справа в обратном порядке
            while self.count() > index + 1:
                widget = self.widget(self.count() - 1)
                if widget and self.parent_widget:
                    self.parent_widget._cleanup_widget(widget)
                self.removeTab(self.count() - 1)

            # Обновляем отображение
            if self.parent_widget:
                self.parent_widget._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладок справа: {e}")
        finally:
            self._operation_in_progress = False


class TabDocumentWidgetFixed(QWidget):
    """Исправленная версия центральной области с вкладками документов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabDocument")
        
        # Словарь для хранения ссылок на виджеты
        self._widget_references: Dict[int, Any] = {}
        
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Стек виджетов для переключения между фоном и вкладками
        self.stacked_widget = QStackedWidget()

        # Фоновое изображение
        image_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "GopiAI-Assets",
            "gopiai", "assets", "lotus_animation.svg"
        )
        image_path = os.path.abspath(image_path)

        self.background_widget = BackgroundImageWidget(image_path)
        self.stacked_widget.addWidget(self.background_widget)

        # Виджет вкладок
        self.tab_widget = EnhancedTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)

        self.stacked_widget.addWidget(self.tab_widget)

        # Подключаем сигналы
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._update_display)

        # Изначально показываем фон
        self.stacked_widget.setCurrentWidget(self.background_widget)

        layout.addWidget(self.stacked_widget)

    def _update_display(self):
        """Обновление отображения в зависимости от количества вкладок"""
        try:
            if self.tab_widget.count() > 0:
                if self.stacked_widget.currentWidget() != self.tab_widget:
                    self.stacked_widget.setCurrentWidget(self.tab_widget)
            else:
                if self.stacked_widget.currentWidget() != self.background_widget:
                    self.stacked_widget.setCurrentWidget(self.background_widget)
                self._ensure_background_display()
        except Exception as e:
            logger.error(f"Ошибка обновления отображения: {e}")

    def _ensure_background_display(self):
        """Обеспечение корректного отображения фонового изображения"""
        try:
            if self.background_widget and not self.background_widget.original_pixmap:
                self.background_widget.load_image()
            if self.background_widget:
                self.background_widget.scale_image()
        except Exception as e:
            logger.error(f"Ошибка отображения фона: {e}")

    def _cleanup_widget(self, widget):
        """Правильная очистка виджета"""
        try:
            if not widget:
                return

            widget_id = id(widget)
            
            # Удаляем ссылку
            if widget_id in self._widget_references:
                del self._widget_references[widget_id]

            # Дополнительная очистка
            if hasattr(widget, 'clear'):
                widget.clear()

        except Exception as e:
            logger.error(f"Ошибка очистки виджета: {e}")

    def _close_tab(self, index):
        """Закрытие вкладки по индексу"""
        try:
            if not (0 <= index < self.tab_widget.count()):
                return

            widget = self.tab_widget.widget(index)
            self._cleanup_widget(widget)
            self.tab_widget.removeTab(index)
            self._update_display()

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладки {index}: {e}")

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой текстовой вкладки"""
        try:
            editor = QTextEdit()
            editor.setPlainText(content)
            
            # Сохраняем ссылку
            widget_id = id(editor)
            self._widget_references[widget_id] = editor

            index = self.tab_widget.addTab(editor, title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            return editor

        except Exception as e:
            logger.error(f"Ошибка создания вкладки: {e}")
            return None

    def force_cleanup(self):
        """Принудительная очистка всех ресурсов"""
        try:
            while self.tab_widget.count() > 0:
                widget = self.tab_widget.widget(0)
                self._cleanup_widget(widget)
                self.tab_widget.removeTab(0)
                
            self._widget_references.clear()
            self._update_display()

        except Exception as e:
            logger.error(f"Ошибка принудительной очистки: {e}")

    def get_stability_metrics(self):
        """Получение метрик стабильности"""
        return {
            'total_tabs': self.tab_widget.count(),
            'registered_widgets': len(self._widget_references),
            'background_displayed': self.stacked_widget.currentWidget() == self.background_widget
        }