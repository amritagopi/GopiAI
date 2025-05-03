"""
Модуль для создания кастомизированных заголовков QDockWidget
с поддержкой кнопок управления в зависимости от типа и состояния окна.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QDockWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from app.ui.theme_manager import theme_manager

class DockTitleBar(QWidget):
    """
    Кастомный заголовок для QDockWidget с кнопками и стилизацией.
    """

    # Сигналы для обработки действий пользователя
    close_clicked = Signal()
    float_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(self, title="", parent=None):
        """
        Инициализирует панель заголовка с заданным текстом и родителем.

        Args:
            title (str): Текст заголовка.
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.title = title
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Настраивает UI компоненты заголовка."""
        # Создаем горизонтальный макет для заголовка
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)  # Устанавливаем минимальные отступы
        layout.setSpacing(3)  # Минимальный промежуток между элементами

        # Создаем и настраиваем иконку заголовка
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setObjectName("dockTitleIcon")

        # Создаем и настраиваем текст заголовка
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("dockTitleText")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Кнопка плавающего режима
        self.float_button = QPushButton()
        self.float_button.setObjectName("dockFloatButton")
        self.float_button.setToolTip("Открепить панель")
        self.float_button.setFixedSize(16, 16)
        self.float_button.setFlat(True)
        self.float_button.clicked.connect(self.float_clicked)

        # Кнопка максимизации
        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("dockMaximizeButton")
        self.maximize_button.setToolTip("Развернуть панель")
        self.maximize_button.setFixedSize(16, 16)
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize_clicked)

        # Кнопка закрытия
        self.close_button = QPushButton()
        self.close_button.setObjectName("dockCloseButton")
        self.close_button.setToolTip("Закрыть панель")
        self.close_button.setFixedSize(16, 16)
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close_clicked)

        # Добавляем все элементы в макет
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.float_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        # Устанавливаем макет
        self.setLayout(layout)

        # Применяем иконки для кнопок и заголовка
        self._update_icons()

    def _setup_styles(self):
        """Настраивает стили для компонентов заголовка."""
        # Используем темы из theme_manager
        self.setStyleSheet("""
            DockTitleBar {
                background-color: palette(window);
                border-bottom: 1px solid palette(mid);
                min-height: 22px;
                max-height: 22px;
            }

            DockTitleBar QLabel#dockTitleText {
                font-weight: bold;
                color: palette(text);
            }

            DockTitleBar QPushButton {
                background-color: transparent;
                border: none;
            }

            DockTitleBar QPushButton:hover {
                background-color: rgba(127, 127, 127, 0.2);
                border-radius: 2px;
            }

            DockTitleBar QPushButton:pressed {
                background-color: rgba(127, 127, 127, 0.4);
                border-radius: 2px;
            }

            DockTitleBar QPushButton#dockCloseButton:hover {
                background-color: rgba(255, 80, 80, 0.3);
            }

            DockTitleBar QPushButton#dockCloseButton:pressed {
                background-color: rgba(255, 80, 80, 0.5);
            }
        """)

    def _update_icons(self):
        """Обновляет иконки для кнопок в зависимости от текущей темы."""
        # Определяем, используется ли темная тема
        is_dark_theme = "dark" in theme_manager.get_current_theme()

        # Фоллбэк значения для иконок, если их не удается загрузить
        self.close_button.setIcon(QIcon.fromTheme("window-close"))
        self.float_button.setIcon(QIcon.fromTheme("window-new"))
        self.maximize_button.setIcon(QIcon.fromTheme("window-maximize"))

        # Устанавливаем размер иконки
        icon_size = QSize(12, 12)
        self.close_button.setIconSize(icon_size)
        self.float_button.setIconSize(icon_size)
        self.maximize_button.setIconSize(icon_size)

        # Установка иконки для заголовка в зависимости от типа дока
        if "chat" in self.title.lower():
            self.icon_label.setPixmap(QIcon.fromTheme("dialog-information").pixmap(16, 16))
        elif "terminal" in self.title.lower():
            self.icon_label.setPixmap(QIcon.fromTheme("utilities-terminal").pixmap(16, 16))
        elif "browser" in self.title.lower():
            self.icon_label.setPixmap(QIcon.fromTheme("applications-internet").pixmap(16, 16))
        elif "explorer" in self.title.lower() or "files" in self.title.lower():
            self.icon_label.setPixmap(QIcon.fromTheme("system-file-manager").pixmap(16, 16))
        else:
            self.icon_label.setPixmap(QIcon.fromTheme("applications-other").pixmap(16, 16))

    def update_theme(self):
        """Обновляет стили в соответствии с текущей темой."""
        self._setup_styles()
        self._update_icons()

    def set_title(self, title):
        """Устанавливает текст заголовка."""
        self.title = title
        self.title_label.setText(title)
        self._update_icons()  # Обновляем иконки, так как они могут зависеть от заголовка

def apply_custom_title_bar(dock_widget, is_docked_permanent=False):
    """
    Применяет кастомный заголовок к QDockWidget.

    Args:
        dock_widget (QDockWidget): Док-виджет, к которому применяется заголовок.
        is_docked_permanent (bool): Является ли док постоянно закрепленным.

    Returns:
        DockTitleBar: Созданный заголовок
    """
    title_bar = DockTitleBar(dock_widget.windowTitle(), dock_widget)

    # Подключаем сигналы
    title_bar.close_clicked.connect(dock_widget.close)
    title_bar.float_clicked.connect(lambda: dock_widget.setFloating(True))
    title_bar.maximize_clicked.connect(lambda: dock_widget.setFloating(not dock_widget.isFloating()))

    # Следим за изменением состояния окна
    dock_widget.topLevelChanged.connect(
        lambda floating: title_bar.set_title(dock_widget.windowTitle())
    )

    # Настраиваем обработку изменения заголовка
    dock_widget.windowTitleChanged.connect(title_bar.set_title)

    # Применяем заголовок к dock_widget
    dock_widget.setTitleBarWidget(title_bar)

    return title_bar
