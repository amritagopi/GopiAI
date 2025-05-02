"""
Скрипт для программной установки иконки закрытия вкладки в PySide6
"""
import os
import sys
from PySide6.QtWidgets import QApplication, QTabBar, QMainWindow, QTabWidget, QPushButton
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, QTimer

class CloseButtonFixer:
    @staticmethod
    def apply_to_window(window):
        """Применяет фиксер к главному окну"""
        # Применяем к центральным вкладкам, если они есть
        if not hasattr(window, "central_tabs"):
            print("Окно не имеет атрибута central_tabs")
            return

        tab_widget = window.central_tabs
        if not isinstance(tab_widget, QTabWidget):
            print(f"central_tabs не является QTabWidget: {type(tab_widget)}")
            return

        # Получаем QTabBar из QTabWidget
        tab_bar = tab_widget.tabBar()
        if not tab_bar:
            print("Ошибка: tabBar не доступен")
            return

        # Принудительно включаем закрываемые вкладки
        tab_widget.setTabsClosable(True)

        # Путь к SVG иконке закрытия
        icon_path = "assets/icons/close.svg"

        # Проверяем, существует ли файл иконки
        if os.path.exists(icon_path):
            close_icon = QIcon(icon_path)
        else:
            # Создаем встроенную иконку в качестве запасного варианта
            close_icon = QIcon.fromTheme("window-close")
            print(f"Предупреждение: файл иконки не найден: {icon_path}, используем системную иконку")

        # Проходим по всем вкладкам и заменяем кнопки закрытия
        for i in range(tab_widget.count()):
            # Получаем текущую кнопку закрытия
            current_button = tab_bar.tabButton(i, QTabBar.RightSide)

            # Проверяем, нужно ли заменить кнопку
            if current_button is None or getattr(current_button, 'text', lambda: '')() == "Close Tab":
                # Создаем новую кнопку с иконкой
                button = QPushButton()
                button.setIcon(close_icon)
                button.setIconSize(QSize(16, 16))
                button.setFixedSize(20, 20)
                button.setFlat(True)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        margin: 0px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 0, 0, 0.2);
                        border-radius: 3px;
                    }
                    QPushButton:pressed {
                        background-color: rgba(255, 0, 0, 0.4);
                    }
                """)

                # Установка имени объекта для идентификации
                button.setObjectName("tabCloseButton")

                # Подключаем сигнал нажатия к закрытию соответствующей вкладки
                tab_index = i  # Сохраняем значение i для замыкания
                button.clicked.connect(lambda checked=False, index=tab_index: tab_widget.tabCloseRequested.emit(index))

                # Устанавливаем новую кнопку вместо старой
                tab_bar.setTabButton(i, QTabBar.RightSide, button)

        print("Иконки закрытия вкладок успешно обновлены!")

# Для интеграции в MainWindow:
"""
# В файле main_window.py добавьте импорт:
from .close_button_fixer import CloseButtonFixer

# В методе __init__ после создания central_tabs:
CloseButtonFixer.apply_to_window(self)

# Также добавьте в метод _toggle_theme для обновления при смене темы:
def _toggle_theme(self, is_dark):
    # ... существующий код ...

    # Обновляем иконки закрытия вкладок после смены темы
    CloseButtonFixer.apply_to_window(self)
"""
