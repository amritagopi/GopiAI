"""
Модуль для создания кастомизированных заголовков QDockWidget
с поддержкой кнопок управления в зависимости от типа и состояния окна.
"""

import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from app.ui.i18n.translator import tr
from app.ui.icon_adapter import IconAdapter
from app.utils.theme_manager import ThemeManager


class DockTitleBar(QWidget):
    """
    Кастомный заголовок для QDockWidget с кнопками и стилизацией.
    """

    # Сигналы для обработки действий пользователя
    close_clicked = Signal()
    float_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(
        self, title="", icon_manager: IconAdapter = None, parent=None
    ):  # Добавлен icon_manager
        """
        Инициализирует панель заголовка с заданным текстом и родителем.

        Args:
            title (str): Текст заголовка.
            icon_manager (IconAdapter): Экземпляр менеджера иконок.
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.title = title
        self.icon_manager = (
            icon_manager if icon_manager else IconAdapter.instance()
        )  # Для обратной совместимости, если не передан
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
        self.float_button.setToolTip(tr("dock_title_bar.float", "Undock panel"))
        self.float_button.setFixedSize(16, 16)
        self.float_button.setFlat(True)
        self.float_button.clicked.connect(self.float_clicked)

        # Кнопка максимизации
        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("dockMaximizeButton")
        self.maximize_button.setToolTip(tr("dock_title_bar.maximize", "Maximize panel"))
        self.maximize_button.setFixedSize(16, 16)
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize_clicked)

        # Кнопка закрытия
        self.close_button = QPushButton()
        self.close_button.setObjectName("dockCloseButton")
        self.close_button.setToolTip(tr("dock_title_bar.close", "Close panel"))
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
        # Получаем менеджер тем
        theme_manager = ThemeManager.instance()

        # Получаем цвета из темы
        bg_color = theme_manager.get_color("dock_title_background", "#3C3C3C")
        border_color = theme_manager.get_color("border", "#444444")
        text_color = theme_manager.get_color("dock_title_foreground", "#EAEAEA")
        button_hover_bg = theme_manager.get_color(
            "dock_title_button_hover_background_color", "rgba(255, 255, 255, 0.2)"
        )
        button_pressed_bg = theme_manager.get_color(
            "dock_title_button_pressed_background_color", "rgba(255, 255, 255, 0.1)"
        )
        close_hover_bg = theme_manager.get_color(
            "custom_dock_title_bar_close_button_hover_background_color",
            "rgba(232, 17, 35, 0.7)",
        )
        close_pressed_bg = theme_manager.get_color(
            "custom_dock_title_bar_close_button_pressed_background_color",
            "rgba(232, 17, 35, 0.9)",
        )

        # Применяем стили
        self.setStyleSheet(
            f"""
            DockTitleBar {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
                min-height: 22px;
                max-height: 22px;
            }}

            DockTitleBar QLabel#dockTitleText {{
                font-weight: bold;
                color: {text_color};
            }}

            DockTitleBar QPushButton {{
                background-color: transparent;
                border: none;
            }}

            DockTitleBar QPushButton:hover {{
                background-color: {button_hover_bg};
                border-radius: 2px;
            }}

            DockTitleBar QPushButton:pressed {{
                background-color: {button_pressed_bg};
                border-radius: 2px;
            }}

            DockTitleBar QPushButton#dockCloseButton:hover {{
                background-color: {close_hover_bg};
            }}

            DockTitleBar QPushButton#dockCloseButton:pressed {{
                background-color: {close_pressed_bg};
            }}
            """
        )

    def _update_icons(self):
        """Обновляет иконки в соответствии с текущей темой"""
        try:
            # Получаем текущую тему
            theme_manager = ThemeManager.instance()
            current_theme = theme_manager.get_current_visual_theme()

            # Проверяем, является ли текущая тема темной
            is_dark_theme = current_theme == "dark"

            # Загрузка иконок в зависимости от темы
            icon_suffix = "white" if is_dark_theme else "black"

            self.close_button.setIcon(
                self.icon_manager.get_icon(f"close_{icon_suffix}")
            )
            self.float_button.setIcon(
                self.icon_manager.get_icon(f"float_{icon_suffix}")
            )
            self.maximize_button.setIcon(
                self.icon_manager.get_icon(f"maximize_{icon_suffix}")
            )

            # Устанавливаем размер иконки
            icon_size = QSize(12, 12)
            self.close_button.setIconSize(icon_size)
            self.float_button.setIconSize(icon_size)
            self.maximize_button.setIconSize(icon_size)

            # Установка иконки для заголовка в зависимости от типа дока
            icon_name = "app_icon"  # Иконка по умолчанию

            if self.title:
                title_lower = self.title.lower()
                if "chat" in title_lower:
                    icon_name = "chat"
                elif "terminal" in title_lower:
                    icon_name = "terminal"
                elif "browser" in title_lower:
                    icon_name = "browser"
                elif "explorer" in title_lower or "files" in title_lower:
                    icon_name = "folder"

            # Устанавливаем иконку заголовка
            self.icon_label.setPixmap(
                self.icon_manager.get_icon(icon_name).pixmap(16, 16)
            )

            # Обновляем стили в соответствии с цветовой схемой
            text_color = theme_manager.get_color(
                "dock_title_foreground", "#EAEAEA" if is_dark_theme else "#333333"
            )
            bg_color = theme_manager.get_color(
                "dock_title_background", "#3C3C3C" if is_dark_theme else "#F0F0F0"
            )
            hover_bg = theme_manager.get_color(
                "dock_title_button_hover_background_color",
                "rgba(255, 255, 255, 0.2)" if is_dark_theme else "rgba(0, 0, 0, 0.1)",
            )
            pressed_bg = theme_manager.get_color(
                "dock_title_button_pressed_background_color",
                "rgba(255, 255, 255, 0.1)" if is_dark_theme else "rgba(0, 0, 0, 0.05)",
            )
            close_hover_bg = theme_manager.get_color(
                "custom_dock_title_bar_close_button_hover_background_color",
                "rgba(232, 17, 35, 0.7)",
            )

            # Применяем стиль к заголовку
            self.setStyleSheet(
                f"background-color: {bg_color}; border-bottom: 1px solid {theme_manager.get_color('border', '#444444')};"
            )

            # Устанавливаем цвет текста
            self.title_label.setStyleSheet(f"color: {text_color};")

            # Создаем стиль для кнопок с использованием переменных
            button_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
            """

            # Отдельный стиль для кнопки закрытия
            close_button_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {close_hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: rgba(232, 17, 35, 0.9);
                }}
            """

            self.close_button.setStyleSheet(close_button_style)
            self.float_button.setStyleSheet(button_style)
            self.maximize_button.setStyleSheet(button_style)

        except Exception as e:
            print(f"Ошибка при обновлении иконок заголовка: {str(e)}")

    def update_theme(self):
        """Обновляет стили в соответствии с текущей темой."""
        self._setup_styles()
        self._update_icons()

    def set_title(self, title):
        """Устанавливает текст заголовка."""
        self.title = title
        self.title_label.setText(title)
        self._update_icons()  # Обновляем иконки, так как они могут зависеть от заголовка


def apply_custom_title_bar(
    dock_widget, icon_manager: IconAdapter, is_docked_permanent=False
):  # Добавлен icon_manager
    """
    Применяет кастомный заголовок к QDockWidget.

    Args:
        dock_widget (QDockWidget): Док-виджет, к которому применяется заголовок.
        icon_manager (IconAdapter): Экземпляр менеджера иконок.
        is_docked_permanent (bool): Является ли док постоянно закрепленным.

    Returns:
        DockTitleBar: Созданный заголовок
    """
    title_bar = DockTitleBar(
        dock_widget.windowTitle(), icon_manager, dock_widget
    )  # Передаем icon_manager

    # Подключаем сигналы
    title_bar.close_clicked.connect(dock_widget.close)
    title_bar.float_clicked.connect(lambda: dock_widget.setFloating(True))
    title_bar.maximize_clicked.connect(
        lambda: dock_widget.setFloating(not dock_widget.isFloating())
    )

    # Следим за изменением состояния окна
    dock_widget.topLevelChanged.connect(
        lambda floating: title_bar.set_title(dock_widget.windowTitle())
    )

    # Настраиваем обработку изменения заголовка
    dock_widget.windowTitleChanged.connect(title_bar.set_title)

    # Применяем заголовок к dock_widget
    dock_widget.setTitleBarWidget(title_bar)

    return title_bar
