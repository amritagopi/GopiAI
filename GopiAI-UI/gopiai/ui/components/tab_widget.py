"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

import logging
import os
from gopiai.ui.utils.safe_ops import safe_widget_operation, stable_widget_creation
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QLabel,
    QStackedWidget,
    QToolButton,
    QTextEdit
)
from PySide6.QtCore import Qt, QUrl, QEvent, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from gopiai.ui.utils.icon_helpers import create_icon_button, get_icon

import chardet
import traceback
from typing import Optional, Dict, Any

# --------- Simplified build (no stability subsystem in this branch) ---------
STABILITY_ENHANCEMENTS_AVAILABLE = False

class _NoopStabilityManager:
    def register_widget(self, *args, **kwargs): return None
    def unregister_widget(self, *args, **kwargs): return None
    def handle_error(self, *args, **kwargs): return None
    def get_stability_metrics(self): return {}
    def force_garbage_collection(self): return 0

class _NoopStabilityMonitor:
    def __init__(self):
        class _Timer:
            def isActive(self): return False
            def start(self): pass
            def stop(self): pass
        self.timer = _Timer()
    def start_monitoring(self): pass
    @property
    def stability_issue_detected(self):
        class _Signal:
            def connect(self, *args, **kwargs): pass
        return _Signal()

class _NoopErrorRecovery:
    def attempt_recovery(self, *args, **kwargs): return False

stability_manager = _NoopStabilityManager()  # type: ignore
stability_monitor = _NoopStabilityMonitor()  # type: ignore
error_recovery = _NoopErrorRecovery()  # type: ignore

# В этой ветке нет отдельной подсистемы ErrorDisplay - используем no-op
ERROR_DISPLAY_AVAILABLE = False

class _NoopErrorDisplay:
    def __init__(self, *args, **kwargs): pass
    def setVisible(self, *args, **kwargs): pass
    def show_component_error(self, *args, **kwargs): pass
    def show_generic_error(self, *args, **kwargs): pass
    @property
    def retryRequested(self):
        class _Signal:
            def connect(self, *a, **k): pass
        return _Signal()
    @property
    def dismissRequested(self):
        class _Signal:
            def connect(self, *a, **k): pass
        return _Signal()

def show_critical_error(*args, **kwargs): pass  # type: ignore
ErrorDisplayWidget = _NoopErrorDisplay  # type: ignore

# Полный отказ от зависимости gopiai.widgets: используем локальный минимальный редактор.
class TextEditorWidget(QTextEdit):  # type: ignore
    # минимальная совместимость: .text_editor и .setPlainText доступны
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.text_editor = self
    def setPlainText(self, text):
        super().setPlainText(text)
TEXT_EDITOR_AVAILABLE = False  # держим False, чтобы ветки fallback продолжали работать

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
    """Кастомный виджет вкладок с контекстным меню и улучшенной обработкой ошибок"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self._tab_close_in_progress = False  # Флаг для предотвращения рекурсивных закрытий
        # Устанавливаем иконки на кнопки прокрутки вкладок и следим за изменениями
        try:
            self.tabBar().installEventFilter(self)
            self._apply_scroll_button_icons()
        except Exception as e:
            logger.debug(f"Не удалось установить иконки кнопок прокрутки: {e}")

    def eventFilter(self, obj, event):
        try:
            if obj is self.tabBar() and event.type() in (
                QEvent.Type.Show,
                QEvent.Type.Resize,
                QEvent.Type.LayoutRequest,
                QEvent.Type.PolishRequest,
            ):
                self._apply_scroll_button_icons()
        except Exception as e:
            logger.debug(f"Ошибка в eventFilter для таббара: {e}")
        return super().eventFilter(obj, event)

    def _apply_scroll_button_icons(self):
        """Назначает Lucide-иконки стрелок на кнопки прокрутки вкладок."""
        try:
            left_icon = get_icon("arrow-left", size=16)
            right_icon = get_icon("arrow-right", size=16)
            for btn in self.findChildren(QToolButton):
                # Кнопки прокрутки обычно имеют arrowType Left/Right
                at = getattr(btn, "arrowType", lambda: Qt.ArrowType.NoArrow)()
                if at == Qt.ArrowType.LeftArrow:
                    if left_icon:
                        btn.setArrowType(Qt.ArrowType.NoArrow)
                        btn.setIcon(left_icon)
                        btn.setIconSize(QSize(16, 16))
                        btn.setToolTip("Прокрутить вкладки влево")
                elif at == Qt.ArrowType.RightArrow:
                    if right_icon:
                        btn.setArrowType(Qt.ArrowType.NoArrow)
                        btn.setIcon(right_icon)
                        btn.setIconSize(QSize(16, 16))
                        btn.setToolTip("Прокрутить вкладки вправо")
        except Exception as e:
            logger.debug(f"Не удалось применить иконки для кнопок прокрутки: {e}")

    @safe_widget_operation("context_menu_creation")
    def contextMenuEvent(self, event):
        """Обработка правого клика для показа контекстного меню с улучшенной обработкой ошибок"""
        tab_index = -1
        try:
            # Определяем, на какой вкладке был клик
            tab_index = self.tabBar().tabAt(event.pos())
            if tab_index == -1:
                logger.debug("Клик вне области вкладок, контекстное меню не показывается")
                return

            # Проверяем, что индекс валиден
            if not (0 <= tab_index < self.count()):
                logger.warning(f"Невалидный индекс вкладки для контекстного меню: {tab_index}")
                return

            # Создаем контекстное меню с обработкой ошибок
            menu = QMenu(self)
            if not menu:
                logger.error("Не удалось создать контекстное меню")
                return

            # Опции закрытия с проверкой состояния
            close_current_action = menu.addAction("🗙 Закрыть вкладку")
            close_current_action.triggered.connect(
                lambda: self._safe_close_tab_at_index(tab_index)
            )

            close_others_action = menu.addAction("🗙 Закрыть остальные")
            close_others_action.triggered.connect(
                lambda: self._safe_close_other_tabs(tab_index)
            )

            close_all_action = menu.addAction("🗙 Закрыть все")
            close_all_action.triggered.connect(self._safe_close_all_tabs)

            menu.addSeparator()

            # Дополнительные опции
            close_left_action = menu.addAction("← Закрыть слева")
            close_left_action.triggered.connect(
                lambda: self._safe_close_tabs_to_left(tab_index)
            )

            close_right_action = menu.addAction("→ Закрыть справа")
            close_right_action.triggered.connect(
                lambda: self._safe_close_tabs_to_right(tab_index)
            )

            # Отключаем опции, если они неприменимы
            current_count = self.count()
            if current_count <= 1:
                close_others_action.setEnabled(False)
                close_all_action.setEnabled(False)

            if tab_index == 0:
                close_left_action.setEnabled(False)

            if tab_index == current_count - 1:
                close_right_action.setEnabled(False)

            # Показываем меню с проверкой
            if event.globalPos().isNull():
                logger.warning("Невалидная позиция для контекстного меню")
                return
                
            menu.exec(event.globalPos())
            logger.debug(f"Показано контекстное меню для вкладки {tab_index}")

        except Exception as e:
            logger.error(f"Ошибка создания контекстного меню: {e}", exc_info=True)
            # Показываем упрощенное меню в случае ошибки
            self._show_fallback_context_menu(event, tab_index)

    def _show_fallback_context_menu(self, event, tab_index):
        """Показ упрощенного контекстного меню в случае ошибки"""
        try:
            menu = QMenu(self)
            close_action = menu.addAction("Закрыть вкладку")
            close_action.triggered.connect(lambda: self._safe_close_tab_at_index(tab_index))
            menu.exec(event.globalPos())
            logger.info("Показано упрощенное контекстное меню")
        except Exception as e:
            logger.error(f"Ошибка показа упрощенного контекстного меню: {e}")

    @safe_widget_operation("tab_closing")
    def _safe_close_tab_at_index(self, index):
        """Безопасное закрытие вкладки по индексу с обработкой ошибок"""
        if self._tab_close_in_progress:
            logger.debug("Закрытие вкладки уже в процессе, пропускаем")
            return

        try:
            self._tab_close_in_progress = True
            
            if not (0 <= index < self.count()):
                logger.warning(f"Попытка закрыть вкладку с невалидным индексом: {index}")
                return

            # Получаем виджет перед закрытием для правильной очистки
            widget = self.widget(index)
            tab_title = self.tabText(index)
            
            logger.debug(f"Закрываем вкладку '{tab_title}' с индексом {index}")

            # Выполняем очистку виджета
            if widget and self.parent_widget:
                self.parent_widget._cleanup_tab_widget(widget)

            # Закрываем вкладку
            self.removeTab(index)
            
            # Обновляем отображение
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()
                
            logger.info(f"Вкладка '{tab_title}' успешно закрыта")

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладки {index}: {e}", exc_info=True)
            # Попытка принудительного закрытия
            try:
                if 0 <= index < self.count():
                    self.removeTab(index)
                    logger.warning(f"Принудительно закрыта вкладка {index}")
            except Exception as force_error:
                logger.error(f"Ошибка принудительного закрытия вкладки {index}: {force_error}")
        finally:
            self._tab_close_in_progress = False

    @safe_widget_operation("multiple_tab_closing")
    def _safe_close_other_tabs(self, keep_index):
        """Безопасное закрытие всех вкладок кроме указанной"""
        if self._tab_close_in_progress:
            logger.debug("Закрытие вкладок уже в процессе, пропускаем")
            return

        try:
            self._tab_close_in_progress = True
            
            if not (0 <= keep_index < self.count()):
                logger.warning(f"Невалидный индекс для сохранения: {keep_index}")
                return

            initial_count = self.count()
            logger.debug(f"Закрываем все вкладки кроме {keep_index}, всего вкладок: {initial_count}")

            # Безопасное закрытие с защитой от бесконечного цикла
            max_iterations = 100
            iteration = 0

            # Закрываем справа от keep_index
            while self.count() > keep_index + 1 and iteration < max_iterations:
                try:
                    widget = self.widget(keep_index + 1)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_tab_widget(widget)
                    self.removeTab(keep_index + 1)
                    iteration += 1
                except Exception as e:
                    logger.error(f"Ошибка закрытия вкладки справа: {e}")
                    break

            # Закрываем слева от keep_index
            iteration = 0
            while keep_index > 0 and iteration < max_iterations:
                try:
                    widget = self.widget(0)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_tab_widget(widget)
                    self.removeTab(0)
                    keep_index -= 1
                    iteration += 1
                except Exception as e:
                    logger.error(f"Ошибка закрытия вкладки слева: {e}")
                    break

            # Обновляем отображение
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()
                
            logger.info(f"Закрыто {initial_count - self.count()} вкладок, осталось {self.count()}")

        except Exception as e:
            logger.error(f"Ошибка закрытия других вкладок: {e}", exc_info=True)
        finally:
            self._tab_close_in_progress = False

    @safe_widget_operation("all_tabs_closing")
    def _safe_close_all_tabs(self):
        """Безопасное закрытие всех вкладок"""
        if self._tab_close_in_progress:
            logger.debug("Закрытие вкладок уже в процессе, пропускаем")
            return

        try:
            self._tab_close_in_progress = True
            
            initial_count = self.count()
            logger.debug(f"Закрываем все {initial_count} вкладок")

            # Безопасное закрытие всех вкладок с защитой от бесконечного цикла
            max_iterations = 100
            iteration = 0

            while self.count() > 0 and iteration < max_iterations:
                try:
                    widget = self.widget(0)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_tab_widget(widget)
                    self.removeTab(0)
                    iteration += 1
                except Exception as e:
                    logger.error(f"Ошибка закрытия вкладки при закрытии всех: {e}")
                    # Принудительное удаление в случае ошибки
                    try:
                        self.removeTab(0)
                    except (RuntimeError, IndexError):
                        break

            if iteration >= max_iterations:
                logger.warning(
                    f"Достигнуто максимальное количество итераций при закрытии всех вкладок. "
                    f"Осталось {self.count()} вкладок"
                )

            # Обновляем отображение
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()
                
            logger.info(f"Закрыто {initial_count - self.count()} из {initial_count} вкладок")

        except Exception as e:
            logger.error(f"Ошибка закрытия всех вкладок: {e}", exc_info=True)
        finally:
            self._tab_close_in_progress = False

    @safe_widget_operation("left_tabs_closing")
    def _safe_close_tabs_to_left(self, index):
        """Безопасное закрытие всех вкладок слева от указанной"""
        if self._tab_close_in_progress:
            logger.debug("Закрытие вкладок уже в процессе, пропускаем")
            return

        try:
            self._tab_close_in_progress = True
            
            if index <= 0:
                logger.debug("Нет вкладок слева для закрытия")
                return

            logger.debug(f"Закрываем {index} вкладок слева от индекса {index}")

            # Безопасное закрытие с защитой от бесконечного цикла
            max_iterations = 100
            iteration = 0
            closed_count = 0

            while index > 0 and iteration < max_iterations:
                try:
                    widget = self.widget(0)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_tab_widget(widget)
                    self.removeTab(0)
                    index -= 1
                    closed_count += 1
                    iteration += 1
                except Exception as e:
                    logger.error(f"Ошибка закрытия вкладки слева: {e}")
                    break

            # Обновляем отображение
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()
                
            logger.info(f"Закрыто {closed_count} вкладок слева")

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладок слева: {e}", exc_info=True)
        finally:
            self._tab_close_in_progress = False

    @safe_widget_operation("right_tabs_closing")
    def _safe_close_tabs_to_right(self, index):
        """Безопасное закрытие всех вкладок справа от указанной"""
        if self._tab_close_in_progress:
            logger.debug("Закрытие вкладок уже в процессе, пропускаем")
            return

        try:
            self._tab_close_in_progress = True
            
            if index < 0 or index >= self.count() - 1:
                logger.debug("Нет вкладок справа для закрытия")
                return

            tabs_to_close = self.count() - index - 1
            logger.debug(f"Закрываем {tabs_to_close} вкладок справа от индекса {index}")

            # Безопасное закрытие с защитой от бесконечного цикла
            max_iterations = 100
            iteration = 0
            closed_count = 0

            while self.count() > index + 1 and iteration < max_iterations:
                try:
                    widget = self.widget(index + 1)
                    if widget and self.parent_widget:
                        self.parent_widget._cleanup_tab_widget(widget)
                    self.removeTab(index + 1)
                    closed_count += 1
                    iteration += 1
                except Exception as e:
                    logger.error(f"Ошибка закрытия вкладки справа: {e}")
                    break

            # Обновляем отображение
            if self.parent_widget and hasattr(self.parent_widget, "_update_display"):
                self.parent_widget._update_display()
                
            logger.info(f"Закрыто {closed_count} вкладок справа")

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладок справа: {e}", exc_info=True)
        finally:
            self._tab_close_in_progress = False


class TabDocumentWidget(QWidget):
    """Центральная область с вкладками документов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabDocument")

        # Словарь для хранения ссылок на виджеты (предотвращение garbage collection)
        self._widget_references: Dict[int, Any] = {}

        # Система отображения ошибок
        self._error_display: Optional[ErrorDisplayWidget] = None

        # В этой ветке мониторинг стабильности отключен
        # (оставлено для совместимости интерфейса)

        self._setup_ui()
        
    def _init_stability_monitoring(self):
        """Отключено в этой ветке"""
        return
            
    def _handle_stability_issue(self, issue_type: str, data: dict):
        """Обработка проблем стабильности"""
        try:
            if issue_type == "memory_leaks" and self._error_display:
                self._error_display.show_generic_error(
                    "Обнаружены утечки памяти",
                    f"Система обнаружила {data.get('memory_leaks_detected', 0)} утечек памяти в UI компонентах.",
                    "Рекомендуется перезапустить приложение для оптимальной производительности."
                )
            elif issue_type == "high_creation_errors" and self._error_display:
                self._error_display.show_generic_error(
                    "Множественные ошибки создания виджетов",
                    f"Обнаружено {data.get('widget_creation_errors', 0)} ошибок создания виджетов.",
                    "Возможны проблемы со стабильностью системы."
                )
        except Exception as e:
            logger.error(f"Ошибка обработки проблемы стабильности {issue_type}: {e}")

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
            "wallpapers.png",
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

        # В упрощенной ветке ErrorDisplay отсутствует — не добавляем в layout
        self._error_display = None

    def _update_display(self):
        """Улучшенное обновление отображения в зависимости от количества вкладок"""
        try:
            current_tab_count = self.tab_widget.count()
            logger.debug(f"Обновляем отображение, количество вкладок: {current_tab_count}")
            
            if current_tab_count > 0:
                # Есть вкладки - показываем виджет вкладок
                if self.stacked_widget.currentWidget() != self.tab_widget:
                    self.stacked_widget.setCurrentWidget(self.tab_widget)
                    logger.debug("Переключились на отображение вкладок")
            else:
                # Нет вкладок - показываем фоновое изображение
                if self.stacked_widget.currentWidget() != self.background_widget:
                    self.stacked_widget.setCurrentWidget(self.background_widget)
                    logger.debug("Переключились на фоновое изображение")
                    
                # Убеждаемся, что фоновое изображение корректно отображается
                self._ensure_background_display()
                
        except Exception as e:
            logger.error(f"Ошибка обновления отображения: {e}", exc_info=True)
            
            # Fallback - пытаемся показать фон
            try:
                self.stacked_widget.setCurrentWidget(self.background_widget)
                logger.warning("Использован fallback для отображения фона")
            except Exception as fallback_error:
                logger.error(f"Ошибка fallback отображения: {fallback_error}")

    def _ensure_background_display(self):
        """Обеспечение корректного отображения фонового изображения"""
        try:
            if not self.background_widget:
                logger.warning("Фоновый виджет не инициализирован")
                return
                
            # Проверяем, что изображение загружено
            if not self.background_widget.original_pixmap:
                logger.warning("Фоновое изображение не загружено, перезагружаем")
                self.background_widget.load_image()
                
            # Принудительно обновляем масштабирование
            self.background_widget.scale_image()
            
            # Убеждаемся, что виджет видим
            if not self.background_widget.isVisible():
                self.background_widget.setVisible(True)
                
            logger.debug("Фоновое изображение корректно отображается")
            
        except Exception as e:
            logger.error(f"Ошибка обеспечения отображения фона: {e}", exc_info=True)

    @stable_widget_creation(fallback_factory=lambda self, title="Новый документ", content="": self._create_fallback_text_editor(title, content))
    @safe_widget_operation("text_tab_creation")
    def add_new_tab(self, title="Новый документ", content=""):
        """Улучшенное добавление новой вкладки с текстовым редактором"""
        editor = None
        
        try:
            if TEXT_EDITOR_AVAILABLE:
                # Используем продвинутый текстовый редактор с нумерацией строк
                editor = TextEditorWidget()
                if hasattr(editor, 'text_editor') and editor.text_editor:
                    editor.text_editor.setPlainText(content)
                else:
                    # Fallback если text_editor недоступен
                    editor.setPlainText(content)
                    
                # Сохраняем ссылку на виджет
                widget_id = id(editor)
                self._widget_references[widget_id] = editor
                
                # Регистрация стабильности отключена в этой ветке

                index = self.tab_widget.addTab(editor, title)
                self.tab_widget.setCurrentIndex(index)
                self._update_display()
                
                logger.info(f"Создана вкладка с TextEditorWidget: {title}")
                return editor
            else:
                raise ImportError("TextEditorWidget недоступен")

        except Exception as e:
            logger.error(f"Ошибка создания текстовой вкладки: {e}", exc_info=True)
            
            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_component_error(
                    "Текстовый редактор", str(e), fallback_available=True
                )

            # Fallback к обычному QTextEdit
            return self._create_fallback_text_editor(title, content)

    def _create_fallback_text_editor(self, title: str, content: str = "") -> Optional[QTextEdit]:
        """Создание fallback текстового редактора"""
        try:
            editor = QTextEdit()
            editor.setPlainText(content)
            
            # Сохраняем ссылку на fallback виджет
            widget_id = id(editor)
            self._widget_references[widget_id] = editor
            
            # Регистрация стабильности отключена

            index = self.tab_widget.addTab(editor, f"{title} (простой редактор)")
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Создана fallback текстовая вкладка: {title}")
            return editor

        except Exception as fallback_error:
            logger.critical(f"Критическая ошибка создания fallback текстового редактора: {fallback_error}")
            if self._error_display:
                self._error_display.show_generic_error(
                    "Критическая ошибка",
                    "Не удалось создать ни основной, ни резервный текстовый редактор",
                    str(fallback_error)
                )
            return None

    @stable_widget_creation(fallback_factory=lambda self, title="Новый блокнот", content="", menu_bar=None: self._create_fallback_notebook(title, content))
    @safe_widget_operation("notebook_tab_creation")
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
                
                # Регистрация стабильности отключена

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
            
            # Попытка восстановления через систему восстановления
            if STABILITY_ENHANCEMENTS_AVAILABLE:
                recovery_success = error_recovery.attempt_recovery(
                    'widget_creation', e, {
                        'widget_type': 'notebook',
                        'title': title,
                        'fallback_factory': lambda: self._create_fallback_notebook(title, content)
                    }
                )
                if recovery_success:
                    return self._create_fallback_notebook(title, content)
            
            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_component_error(
                    "Блокнот", str(e), fallback_available=True
                )

            # Fallback к обычному текстовому редактору
            return self._create_fallback_notebook(title, content)
            
    def _create_fallback_notebook(self, title: str, content: str = "") -> Optional[QTextEdit]:
        """Создание fallback блокнота"""
        try:
            fallback_editor = QTextEdit()
            fallback_editor.setPlainText(content if content else "")
            fallback_editor.setAcceptRichText(True)  # Включаем поддержку форматирования

            # Сохраняем ссылку на fallback виджет
            widget_id = id(fallback_editor)
            self._widget_references[widget_id] = fallback_editor
            
            # Регистрация стабильности отключена

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
                    f"Ошибка fallback: {str(fallback_error)}",
                    self,
                )
            return None

    @stable_widget_creation(fallback_factory=lambda self, file_path: self._create_error_tab(f"Ошибка открытия файла: {file_path}"))
    @safe_widget_operation("file_opening")
    def open_file_in_tab(self, file_path):
        """Улучшенное открытие файла в новой вкладке с обработкой ошибок"""
        editor = None
        
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")
                
            # Проверяем права на чтение
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Нет прав на чтение файла: {file_path}")

            # Читаем файл с определением кодировки
            with open(file_path, "rb") as f:
                raw = f.read()
                
            # Определяем кодировку
            encoding_info = chardet.detect(raw)
            encoding = encoding_info.get("encoding", "utf-8") or "utf-8"
            confidence = encoding_info.get("confidence", 0)
            
            if confidence < 0.7:
                logger.warning(f"Низкая уверенность в кодировке {encoding} ({confidence:.2f}) для файла {file_path}")
                
            text = raw.decode(encoding, errors="replace")
            tab_title = os.path.basename(file_path)

            if TEXT_EDITOR_AVAILABLE:
                # Создаем продвинутый текстовый редактор
                editor = TextEditorWidget()
                
                # Устанавливаем текст (поддержка как text_editor, так и прямого вызова)
                if hasattr(editor, 'text_editor') and getattr(editor, 'text_editor'):
                    editor.text_editor.setPlainText(text)
                elif hasattr(editor, 'setPlainText'):
                    editor.setPlainText(text)
                
                # Подключаем сигнал изменения имени файла (если есть)
                sig = getattr(editor, "file_name_changed", None)
                if sig is not None:
                    try:
                        sig.connect(
                            lambda name, ed=editor: self._update_tab_title(ed, name)  # type: ignore[attr-defined]
                        )
                    except Exception:
                        pass
                    
                logger.info(f"Файл открыт в TextEditorWidget: {file_path}")
            else:
                # Fallback к обычному редактору
                editor = QTextEdit()
                editor.setPlainText(text)
                logger.info(f"Файл открыт в QTextEdit (fallback): {file_path}")

            # Сохраняем ссылку на виджет
            widget_id = id(editor)
            self._widget_references[widget_id] = editor
            
            # Регистрация стабильности отключена

            # Добавляем вкладку
            index = self.tab_widget.addTab(editor, tab_title)
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Файл '{file_path}' успешно открыт в вкладке")
            return editor

        except Exception as e:
            logger.error(f"Ошибка открытия файла {file_path}: {e}", exc_info=True)
            
            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_generic_error(
                    "Ошибка открытия файла",
                    f"Не удалось открыть файл: {os.path.basename(file_path)}",
                    str(e)
                )
            
            # Создаем вкладку с сообщением об ошибке
            return self._create_error_tab(f"Ошибка открытия файла: {file_path}", str(e))

    def _create_error_tab(self, title: str, error_message: str = "") -> QTextEdit:
        """Создание вкладки с сообщением об ошибке"""
        try:
            error_tab = QTextEdit()
            error_content = f"❌ {title}\n\n"
            if error_message:
                error_content += f"Детали ошибки:\n{error_message}\n\n"
            error_content += "Попробуйте:\n• Проверить путь к файлу\n• Убедиться в наличии прав на чтение\n• Выбрать другой файл"
            
            error_tab.setPlainText(error_content)
            error_tab.setReadOnly(True)
            
            # Сохраняем ссылку на виджет
            widget_id = id(error_tab)
            self._widget_references[widget_id] = error_tab
            
            # Регистрация стабильности отключена

            index = self.tab_widget.addTab(error_tab, "❌ Ошибка")
            self.tab_widget.setCurrentIndex(index)
            self._update_display()
            
            logger.info(f"Создана вкладка с ошибкой: {title}")
            return error_tab
            
        except Exception as tab_error:
            logger.critical(f"Критическая ошибка создания вкладки с ошибкой: {tab_error}")
            # Возвращаем минимальный виджет
            minimal_tab = QTextEdit()
            minimal_tab.setPlainText("Критическая ошибка создания вкладки")
            minimal_tab.setReadOnly(True)
            return minimal_tab

    def _update_tab_title(self, editor_widget, new_title):
        """Обновление заголовка вкладки"""
        try:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == editor_widget:
                    self.tab_widget.setTabText(i, new_title)
                    logger.debug(f"Обновлен заголовок вкладки {i}: {new_title}")
                    break
        except Exception as e:
            logger.error(f"Ошибка обновления заголовка вкладки: {e}")

    def _handle_error_retry(self):
        """Обработка запроса повтора после ошибки"""
        try:
            logger.info("Пользователь запросил повтор после ошибки")
            if self._error_display:
                self._error_display.setVisible(False)
        except Exception as e:
            logger.error(f"Ошибка обработки повтора: {e}")


    def get_stability_metrics(self) -> Dict[str, Any]:
        """Метрики без подсистемы стабильности"""
        return {
            'total_tabs': self.tab_widget.count(),
            'registered_widgets': len(self._widget_references),
            'background_displayed': self.stacked_widget.currentWidget() == self.background_widget,
            'error_display_available': False,
            'stability_enhancements_available': False
        }

    def force_cleanup(self):
        """Принудительная очистка всех ресурсов"""
        try:
            logger.info("Выполняем принудительную очистку TabDocumentWidget")
            
            # Закрываем все вкладки
            while self.tab_widget.count() > 0:
                widget = self.tab_widget.widget(0)
                self._cleanup_tab_widget(widget)
                self.tab_widget.removeTab(0)
                
            # Очищаем словарь ссылок
            self._widget_references.clear()
            
            # Обновляем отображение
            self._update_display()
            
            logger.info("Принудительная очистка завершена")
            
        except Exception as e:
            logger.error(f"Ошибка принудительной очистки: {e}", exc_info=True)


    @safe_widget_operation("tab_closing")
    def _close_tab(self, index):
        """Улучшенное закрытие вкладки по индексу с обработкой ошибок"""
        try:
            if not (self.tab_widget.count() > 0 and 0 <= index < self.tab_widget.count()):
                logger.warning(f"Попытка закрыть вкладку с невалидным индексом: {index}")
                return

            # Получаем виджет и заголовок перед закрытием
            widget = self.tab_widget.widget(index)
            tab_title = self.tab_widget.tabText(index)
            
            logger.debug(f"Закрываем вкладку '{tab_title}' с индексом {index}")

            # Выполняем правильную очистку виджета
            self._cleanup_tab_widget(widget)

            # Закрываем вкладку
            self.tab_widget.removeTab(index)
            
            # Обновляем отображение после закрытия
            self._update_display()
            
            logger.info(f"Вкладка '{tab_title}' успешно закрыта")

        except Exception as e:
            logger.error(f"Ошибка закрытия вкладки {index}: {e}", exc_info=True)
            
            # Показываем ошибку пользователю
            if self._error_display:
                self._error_display.show_generic_error(
                    "Ошибка закрытия вкладки",
                    f"Не удалось корректно закрыть вкладку {index}",
                    str(e)
                )
            
            # Попытка принудительного закрытия
            try:
                if 0 <= index < self.tab_widget.count():
                    self.tab_widget.removeTab(index)
                    self._update_display()
                    logger.warning(f"Принудительно закрыта вкладка {index}")
            except Exception as force_error:
                logger.error(f"Ошибка принудительного закрытия вкладки {index}: {force_error}")

    def add_browser_tab(self, url="about:blank", title="Браузер"):
        """Добавление новой вкладки с браузером"""  # type: ignore
        logger.info("Создаем встроенный браузер...")
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
            back_btn = create_icon_button("arrow-left", "Назад")
            back_btn.setObjectName("browserBackBtn")

            # Кнопка "Вперед"
            forward_btn = create_icon_button("arrow-right", "Вперед")
            forward_btn.setObjectName("browserForwardBtn")

            # Кнопка "Обновить"
            refresh_btn = create_icon_button("refresh-cw", "Обновить")
            refresh_btn.setObjectName("browserRefreshBtn")

            # Адресная строка
            address_bar = QLineEdit()
            address_bar.setPlaceholderText("Введите URL или поисковый запрос...")
            address_bar.setObjectName("browserAddressBar")

            # Кнопка "Перейти"
            go_btn = create_icon_button("corner-down-right", "Перейти")
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
                logger.info("📡 Загружаем Google")
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

        # Возвращаем внутренний редактор, если это TextEditorWidget, иначе QTextEdit
        try:
            if TEXT_EDITOR_AVAILABLE and isinstance(current_widget, TextEditorWidget):
                # TextEditorWidget может иметь поле text_editor; если нет - сам виджет совместим
                return getattr(current_widget, "text_editor", current_widget)
        except Exception:
            pass
        if isinstance(current_widget, QTextEdit):
            return current_widget
        return None

    def get_browser_widget(self) -> Optional[QWidget]:
        """Находит и возвращает виджет браузера, если он открыт.

        Returns:
            Виджет браузера (EnhancedBrowserWidget) или None, если не найден.
        """
        try:
            # Импортируем здесь, чтобы избежать циклических зависимостей
            from gopiai.ui.components.enhanced_browser_widget import EnhancedBrowserWidget
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                # Проверяем как сам виджет, так и его дочерние элементы, если он контейнер
                if isinstance(widget, EnhancedBrowserWidget):
                    return widget
                # Случай, когда браузер внутри другого виджета (например, контейнера с адресной строкой)
                browser_child = widget.findChild(EnhancedBrowserWidget)
                if browser_child:
                    return browser_child
            return None
        except Exception as e:
            logger.error(f"Ошибка поиска виджета браузера: {e}")
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
                
                with open(file_path, "rb") as f:
                    raw = f.read()
                encoding = chardet.detect(raw)["encoding"] or "utf-8"
                text = raw.decode(encoding, errors="replace")
                if hasattr(editor, 'text_editor') and getattr(editor, 'text_editor', None):
                    editor.text_editor.setPlainText(text)
                elif hasattr(editor, 'setPlainText'):
                    editor.setPlainText(text)
                
                tab_title = os.path.basename(file_path)
                sig = getattr(editor, "file_name_changed", None)
                if sig is not None:
                    try:
                        sig.connect(
                            lambda name, ed=editor: self._update_tab_title(ed, name)  # type: ignore[attr-defined]
                        )
                    except Exception:
                        pass
                
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
            
            # Дополнительная универсальная очистка
            try:
                if hasattr(widget, 'clear'):
                    widget.clear()
                if hasattr(widget, 'page'):
                    try:
                        page = widget.page()
                        if page and hasattr(page, 'deleteLater'):
                            page.deleteLater()
                    except Exception as pe:
                        logger.warning(f"Ошибка очистки страницы веб-виджета: {pe}")
                if hasattr(widget, 'timer') and hasattr(widget.timer, 'stop'):
                    widget.timer.stop()
            except Exception as cleanup_error:
                logger.warning(f"Ошибка дополнительной очистки виджета: {cleanup_error}")
            
            # Общая очистка QWidget
            try:
                widget.deleteLater()
                logger.debug("Виджет помечен для удаления")
            except Exception as e:
                logger.warning(f"Ошибка при deleteLater: {e}")
                
        except Exception as e:
            logger.error(f"Ошибка очистки виджета: {e}", exc_info=True)

    def _handle_error_dismiss(self):
        """Обработка закрытия сообщения об ошибке"""
        try:
            logger.debug("Пользователь отклонил сообщение об ошибке")
            if self._error_display:
                self._error_display.setVisible(False)
        except Exception as e:
            logger.error(f"Ошибка отклонения сообщения об ошибке: {e}")

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
