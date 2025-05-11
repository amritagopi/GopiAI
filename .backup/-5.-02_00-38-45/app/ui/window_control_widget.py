"""
Виджет с кнопками управления окном в стиле Cursor IDE.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from app.ui.i18n.translator import tr
from app.ui.icon_manager import IconManager


class WindowControlWidget(QWidget):
    """
    Виджет с кнопками управления окном (свернуть, развернуть/восстановить, закрыть)
    в стиле Cursor IDE - без рамок, компактный.
    """
    # Сигналы для обработки действий пользователя
    minimize_clicked = Signal()
    maximize_restore_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, icon_manager, parent=None):
        super().__init__(parent)
        self.icon_manager = icon_manager
        self.maximized = False
        self._setup_ui()
        self._update_icons()

    def _setup_ui(self):
        """Настраивает UI компоненты виджета."""
        # Создаем горизонтальный макет
        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)  # Минимальные отступы
        layout.setSpacing(6)  # Небольшой промежуток между кнопками

        # Кнопка свертывания окна
        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("windowMinimizeButton")
        self.minimize_button.setToolTip(tr("window_control.minimize", "Свернуть"))
        self.minimize_button.setFixedSize(22, 22)
        self.minimize_button.setFlat(True)
        self.minimize_button.clicked.connect(self.minimize_clicked)
        layout.addWidget(self.minimize_button)

        # Кнопка разворачивания/восстановления окна
        self.maximize_restore_button = QPushButton()
        self.maximize_restore_button.setObjectName("windowMaxRestoreButton")
        self.maximize_restore_button.setToolTip(tr("window_control.maximize", "Развернуть"))
        self.maximize_restore_button.setFixedSize(22, 22)
        self.maximize_restore_button.setFlat(True)
        self.maximize_restore_button.clicked.connect(self.maximize_restore_clicked)
        layout.addWidget(self.maximize_restore_button)

        # Кнопка закрытия окна
        self.close_button = QPushButton()
        self.close_button.setObjectName("windowCloseButton")
        self.close_button.setToolTip(tr("window_control.close", "Закрыть"))
        self.close_button.setFixedSize(22, 22)
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close_clicked)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def _update_icons(self):
        """Обновляет иконки в соответствии с текущей темой"""
        try:
            # Получаем суффикс в зависимости от текущей темы
            from app.utils.theme_manager import ThemeManager
            theme_manager = ThemeManager.instance()
            current_theme = theme_manager.get_current_visual_theme() if theme_manager else 'light'
            is_dark_theme = current_theme == 'dark'
            icon_suffix = "white" if is_dark_theme else "black"

            # Устанавливаем размер иконки
            icon_size = QSize(14, 14)

            # Иконка для кнопки закрытия - X
            self.close_button.setIcon(self.icon_manager.get_icon(f"close_{icon_suffix}"))
            self.close_button.setIconSize(icon_size)

            # Иконка для кнопки минимизации - горизонтальная линия
            self.minimize_button.setIcon(self.icon_manager.get_icon(f"minimize_{icon_suffix}"))
            self.minimize_button.setIconSize(icon_size)

            # Иконка для кнопки максимизации/восстановления - квадрат или двойной квадрат
            icon_name = f"restore_{icon_suffix}" if self.maximized else f"maximize_{icon_suffix}"
            self.maximize_restore_button.setIcon(self.icon_manager.get_icon(icon_name))
            self.maximize_restore_button.setIconSize(icon_size)

            # Обновляем подсказку
            tip_key = "window_control.restore" if self.maximized else "window_control.maximize"
            tip_default = "Восстановить" if self.maximized else "Развернуть"
            self.maximize_restore_button.setToolTip(tr(tip_key, tip_default))
        except Exception as e:
            import logging
            logging.error(f"Ошибка при обновлении иконок в WindowControlWidget: {str(e)}")

    def update_maximized_state(self, maximized):
        """Обновляет состояние кнопки максимизации/восстановления."""
        if self.maximized != maximized:
            self.maximized = maximized
            self._update_icons()
