"""
Модуль для создания кастомизированного заголовка главного окна
с поддержкой логотипа и кнопок управления окном.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QToolButton,
    QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QIcon, QMouseEvent
from app.utils.theme_manager import ThemeManager
from app.ui.icon_manager import IconManager
from app.ui.i18n.translator import tr

class MainWindowTitleBar(QWidget):
    """
    Кастомный заголовок для главного окна приложения с логотипом и кнопками.
    """

    # Сигналы для обработки действий пользователя
    minimize_clicked = Signal()
    maximize_restore_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, title="", icon_manager=None, parent=None):
        """
        Инициализирует панель заголовка с заданным текстом и родителем.

        Args:
            title (str): Текст заголовка.
            icon_manager (IconManager): Экземпляр менеджера иконок.
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.title = title
        self.icon_manager = icon_manager if icon_manager else IconManager()
        self.is_maximized = False
        self.dragging = False
        self.drag_position = QPoint()

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает UI компоненты заголовка."""
        # Создаем горизонтальный макет для заголовка
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)  # Минимальные отступы
        layout.setSpacing(3)  # Минимальный промежуток между элементами

        # Создаем пустое пространство для перетаскивания
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(spacer)

        # Кнопка свертывания окна
        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("windowMinimizeButton")
        self.minimize_button.setToolTip(tr("window_title_bar.minimize", "Свернуть"))
        self.minimize_button.setFixedSize(16, 16)
        self.minimize_button.setFlat(True)
        self.minimize_button.clicked.connect(self.minimize_clicked)
        layout.addWidget(self.minimize_button)

        # Кнопка максимизации/восстановления
        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("windowMaximizeButton")
        self.maximize_button.setToolTip(tr("window_title_bar.maximize", "Развернуть"))
        self.maximize_button.setFixedSize(16, 16)
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize_restore_clicked)
        layout.addWidget(self.maximize_button)

        # Кнопка закрытия
        self.close_button = QPushButton()
        self.close_button.setObjectName("windowCloseButton")
        self.close_button.setToolTip(tr("window_title_bar.close", "Закрыть"))
        self.close_button.setFixedSize(16, 16)
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close_clicked)
        layout.addWidget(self.close_button)

        # Устанавливаем макет
        self.setLayout(layout)

        # Устанавливаем минимальную высоту для заголовка
        self.setMinimumHeight(28)

        # Применяем иконки для кнопок
        self._update_icons()

    def _update_icons(self):
        """Обновляет иконки в соответствии с текущей темой"""
        try:
            # Получаем текущую тему
            theme_manager = ThemeManager.instance()
            current_theme = theme_manager.get_current_visual_theme()

            # Проверяем, является ли текущая тема темной
            is_dark_theme = current_theme == 'dark'

            # Загрузка иконок в зависимости от темы
            icon_suffix = "white" if is_dark_theme else "black"

            # Устанавливаем размер иконки
            icon_size = QSize(12, 12)

            # Иконка для кнопки закрытия - красный X
            self.close_button.setIcon(self.icon_manager.get_icon(f"close_{icon_suffix}"))
            self.close_button.setIconSize(icon_size)

            # Иконка для кнопки минимизации - стрелка вниз
            min_icon = self.icon_manager.get_icon(f"arrow")
            self.minimize_button.setIcon(min_icon)
            self.minimize_button.setIconSize(icon_size)

            # Иконка максимизации/восстановления зависит от текущего состояния
            if self.is_maximized:
                self.maximize_button.setIcon(self.icon_manager.get_icon(f"float_{icon_suffix}"))
                self.maximize_button.setToolTip(tr("window_title_bar.restore", "Восстановить"))
            else:
                self.maximize_button.setIcon(self.icon_manager.get_icon(f"maximize_{icon_suffix}"))
                self.maximize_button.setToolTip(tr("window_title_bar.maximize", "Развернуть"))
            self.maximize_button.setIconSize(icon_size)

        except Exception as e:
            print(f"Ошибка при обновлении иконок заголовка: {str(e)}")

    def update_theme(self):
        """Обновляет стили в соответствии с текущей темой."""
        self._update_icons()

    def set_window_title(self, title):
        """Устанавливает текст заголовка окна."""
        self.title = title

    def update_maximized_state(self, is_maximized):
        """Обновляет состояние максимизации и соответствующую иконку."""
        self.is_maximized = is_maximized
        self._update_icons()

    # События мыши для перетаскивания окна

    def mousePressEvent(self, event: QMouseEvent):
        """Обрабатывает нажатие кнопки мыши для начала перетаскивания."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обрабатывает движение мыши для перетаскивания окна."""
        if self.dragging and event.buttons() & Qt.LeftButton:
            # Если окно максимизировано, не перемещаем его
            if not self.window().isMaximized():
                self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обрабатывает отпускание кнопки мыши для завершения перетаскивания."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Обрабатывает двойной клик для максимизации/восстановления окна."""
        if event.button() == Qt.LeftButton:
            self.maximize_restore_clicked.emit()
            event.accept()
        super().mouseDoubleClickEvent(event)
