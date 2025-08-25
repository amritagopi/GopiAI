"""Диалог настроек GopiAI"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTabWidget,
    QWidget,
    QGroupBox,
    QCheckBox,
    QSlider,
    QSpinBox,
    QLineEdit,
    QTextEdit,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QGridLayout,
    QFormLayout,
    QSpacerItem,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from pathlib import Path
from gopiai.ui.utils.icon_helpers import create_icon_button

# Клиент CrewAI API для работы с настройкой небезопасного терминала
try:
    from ..components.crewai_client import crewai_client
except Exception as e:
    crewai_client = None
    print(f"⚠️ Не удалось импортировать crewai_client: {e}")

class SettingsCard(QFrame):
    """Карточка настроек"""

    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        # Устанавливаем objectName для лучшего стилизирования
        self.setObjectName("SettingsCard")
        
        # Убираем все жестко заданные стили - они будут применяться из глобальной темы
        self.setContentsMargins(16, 16, 16, 16)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Заголовок
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Описание
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setObjectName("DescriptionLabel")
            # Убираем жестко заданные стили - они будут из темы
            layout.addWidget(desc_label)

        # Контейнер для контента
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

    def add_content(self, widget):
        """Добавить виджет в карточку"""
        self.content_layout.addWidget(widget)



# Вспомогательные функции
def is_qt_object_valid(obj):
    """Безопасно проверяет валидность Qt объекта без зависимости от sip"""
    if obj is None:
        return False
    try:
        # Пробуем вызвать какой-нибудь метод, который есть у всех QObject
        # isVisible() - безопасный метод, который должен быть у всех виджетов
        return (
            obj.isVisible() or True
        )  # Возвращаем True даже если невидим, главное что метод отработал
    except RuntimeError:
        # Если метод вызвал RuntimeError, значит C++ объект уже удален
        return False
    except Exception:
        # При любой другой ошибке считаем объект невалидным
        return False


class GopiAISettingsDialog(QDialog):
    """Диалог настроек GopiAI"""

    settings_applied = Signal(dict)  # Сигнал применения настроек
    themeChanged = Signal(str)  # Сигнал изменения темы

    # Не переопределяем QDialog.DialogCode, объявляем собственный набор кодов
    class ResultCode:
        Accepted = int(QDialog.DialogCode.Accepted)
        Rejected = int(QDialog.DialogCode.Rejected)

    # Функция для определения яркости цвета
    def _is_light_color(self, color):
        """Определяет, является ли цвет светлым"""
        # Убираем # если есть
        if color.startswith("#"):
            color = color[1:]

        # Для HEX формата #RRGGBB
        if len(color) == 6:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)  # Формула для определения яркости
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness > 128
        return True  # По умолчанию считаем светлым
    
    def __init__(self, theme_manager=None, parent=None):
            print("🔧 GopiAISettingsDialog.__init__ начат")
            super().__init__(parent)
            print("🔧 super().__init__ выполнен")
            # Добавляем свойство безрамочного окна
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
            self.theme_manager = theme_manager
            self.settings = {}
    
            # Переменная для хранения позиции мыши при перетаскивании
            self._drag_position = None
    
            print("🔧 Вызываем setup_ui()")
            self.setup_ui()
            print("🔧 setup_ui() завершен")
            print("🔧 Вызываем load_current_settings()")
            self.load_current_settings()
            print("🔧 load_current_settings() завершен")

    def _load_terminal_unsafe(self):
        """Читает текущее значение terminal_unsafe из CrewAI и обновляет чекбокс."""
        try:
            if not hasattr(self, 'terminal_unsafe_check') or self.terminal_unsafe_check is None:
                return
            # По умолчанию делаем неактивным до получения данных
            self.terminal_unsafe_check.setEnabled(False)
            if crewai_client is None:
                self.terminal_unsafe_check.setToolTip("CrewAI клиент недоступен")
                return
            value = crewai_client.get_terminal_unsafe()
            if value is None:
                # Сервер недоступен или ошибка — оставляем выключенным
                self.terminal_unsafe_check.setChecked(False)
                self.terminal_unsafe_check.setToolTip("Не удалось получить состояние с сервера CrewAI")
            else:
                # Блокируем сигнал на время программной установки
                try:
                    self.terminal_unsafe_check.blockSignals(True)
                    self.terminal_unsafe_check.setChecked(bool(value))
                finally:
                    self.terminal_unsafe_check.blockSignals(False)
                self.terminal_unsafe_check.setToolTip(
                    "Небезопасный терминал включен" if value else "Небезопасный терминал выключен"
                )
            # Разблокируем возможность изменения, если клиент есть
            self.terminal_unsafe_check.setEnabled(crewai_client is not None)
        except Exception as e:
            print(f"❌ Ошибка при загрузке terminal_unsafe: {e}")
            try:
                self.terminal_unsafe_check.setEnabled(False)
            except Exception:
                pass

    def _on_terminal_unsafe_toggled(self, state: int):
        """Обработчик изменения чекбокса: отправляет новое значение на сервер CrewAI."""
        try:
            if crewai_client is None:
                print("⚠️ Невозможно сохранить terminal_unsafe: crewai_client недоступен")
                return
            value = bool(state == Qt.CheckState.Checked)
            ok = crewai_client.set_terminal_unsafe(value)
            if not ok:
                print("❌ Не удалось обновить terminal_unsafe на сервере — откатываем состояние")
                try:
                    self.terminal_unsafe_check.blockSignals(True)
                    # Откатываем в реальное состояние сервера
                    current = crewai_client.get_terminal_unsafe()
                    self.terminal_unsafe_check.setChecked(bool(current) if current is not None else False)
                finally:
                    self.terminal_unsafe_check.blockSignals(False)
            else:
                # Обновим тултип
                self.terminal_unsafe_check.setToolTip(
                    "Небезопасный терминал включен" if value else "Небезопасный терминал выключен"
                )
        except Exception as e:
            print(f"❌ Ошибка при установке terminal_unsafe: {e}")
            try:
                self.terminal_unsafe_check.blockSignals(True)
                self.terminal_unsafe_check.setChecked(False)
            finally:
                self.terminal_unsafe_check.blockSignals(False)
            print("🔧 GopiAISettingsDialog.__init__ завершен")    
    def _get_theme_colors_for_dialog(self):
        """Получает полную палитру цветов для диалога настроек"""
        if not self.theme_manager:
            return {
                'bg_color': '#f8f9fa',
                'text_color': '#212529',
                'border_color': '#dee2e6',
                'hover_color': '#e9ecef',
                'selected_color': '#007bff',
                'button_color': '#6c757d',
                'accent_color': '#007bff'
            }
        
        theme_data = self.theme_manager.get_current_theme_data()
        if not theme_data:
            return {
                'bg_color': '#f8f9fa',
                'text_color': '#212529',
                'border_color': '#dee2e6',
                'hover_color': '#e9ecef',
                'selected_color': '#007bff',
                'button_color': '#6c757d',
                'accent_color': '#007bff'
            }
        
        # Получаем основные цвета из темы (используем точные названия из simple_theme_manager)
        bg_color = theme_data.get('main_color', '#f8f9fa')
        text_color = theme_data.get('text_color', '#212529')
        button_color = theme_data.get('button_color', '#6c757d')
        border_color = theme_data.get('border_color', '#dee2e6')
        accent_color = theme_data.get('accent_color', '#007bff')
        
        # Используем правильные цвета из темы, если они есть
        hover_color = theme_data.get('button_hover_color', button_color)
        selected_color = theme_data.get('button_active_color', accent_color)
        
        # Если button_hover_color отсутствует, создаем его программно
        if 'button_hover_color' not in theme_data:
            is_light = self._is_light_color(button_color)
            if is_light:
                hover_color = self._darken_color(button_color, 0.1)
            else:
                hover_color = self._lighten_color(button_color, 0.1)
        
        # Если button_active_color отсутствует, используем control_color или создаем программно
        if 'button_active_color' not in theme_data:
            selected_color = theme_data.get('control_color', accent_color)
        
        return {
            'bg_color': bg_color,
            'text_color': text_color,
            'border_color': border_color,
            'hover_color': hover_color,
            'selected_color': selected_color,
            'button_color': button_color,
            'accent_color': accent_color
        }

    
    def _darken_color(self, color, amount):
        """Затемняет цвет на указанную величину"""
        try:
            if color.startswith('#'):
                color = color[1:]
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = max(0, int(r * (1 - amount)))
            g = max(0, int(g * (1 - amount)))
            b = max(0, int(b * (1 - amount)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError, TypeError):
            return color
    
    def _lighten_color(self, color, amount):
        """Осветляет цвет на указанную величину"""
        try:
            if color.startswith('#'):
                color = color[1:]
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = min(255, int(r + (255 - r) * amount))
            g = min(255, int(g + (255 - g) * amount))
            b = min(255, int(b + (255 - b) * amount))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError, TypeError):
            return color
        
    def _apply_theme_styles(self):
        """Применяет полную интеграцию с темой для всех элементов диалога с автоматической адаптацией цвета текста"""
        colors = self._get_theme_colors_for_dialog()
        
        # Автоматически определяем контрастный цвет текста для каждого фона
        def get_contrast_text_color(bg_color):
            """Возвращает контрастный цвет текста для данного фона"""
            is_light = self._is_light_color(bg_color)
            return "#1a1a1a" if is_light else "#e5e5e5"
        
        # Определяем цвета текста для каждого элемента
        main_text_color = get_contrast_text_color(colors['bg_color'])
        button_text_color = get_contrast_text_color(colors['button_color'])
        hover_text_color = get_contrast_text_color(colors['hover_color'])
        selected_text_color = get_contrast_text_color(colors['selected_color'])
        accent_text_color = get_contrast_text_color(colors['accent_color'])
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
                color: {main_text_color};
                border: 1px solid {colors['border_color']};
                border-radius: 8px;
            }}
            QWidget {{
                background-color: {colors['bg_color']};
                color: {main_text_color};
            }}
            QLabel {{
                color: {main_text_color};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {colors['button_color']};
                color: {button_text_color};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors['hover_color']};
                color: {hover_text_color};
                border-color: {colors['accent_color']};
            }}
            QPushButton:pressed {{
                background-color: {colors['selected_color']};
                color: {selected_text_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border_color']};
                border-radius: 6px;
                background-color: {colors['bg_color']};
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {colors['button_color']};
                color: {button_text_color};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid {colors['border_color']};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['bg_color']};
                color: {main_text_color};
                border-bottom: 1px solid {colors['bg_color']};
            }}
            QTabBar::tab:hover {{
                background-color: {colors['hover_color']};
                color: {hover_text_color};
            }}
            /* Убираем рамки и фон у всех QFrame, QGroupBox, SettingsCard */
            QFrame, QGroupBox, QFrame#SettingsCard {{
                background: transparent;
                border: none;
                border-color: none;
            }}
            QLabel#DescriptionLabel {{
                color: {main_text_color};
                background-color: transparent;
                font-size: 9pt;
                opacity: 0.8;
            }}
            QComboBox {{
                background-color: {colors['button_color']};
                color: {button_text_color};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 6px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {colors['accent_color']};
                background-color: {colors['hover_color']};
                color: {hover_text_color};
            }}
            QComboBox:focus {{
                border-color: {colors['accent_color']};
                border-width: 2px;
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: transparent;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['button_color']};
                color: {button_text_color};
                border: 1px solid {colors['border_color']};
                selection-background-color: {colors['accent_color']};
                selection-color: {accent_text_color};
            }}
            QCheckBox {{
                color: {main_text_color};
                spacing: 8px;
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors['border_color']};
                border-radius: 4px;
                background-color: {colors['button_color']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {colors['accent_color']};
                background-color: {colors['hover_color']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['accent_color']};
                border-color: {colors['accent_color']};
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {colors['selected_color']};
            }}
            QSpinBox, QLineEdit, QTextEdit {{
                background-color: {colors['button_color']};
                color: {button_text_color};
                border: 1px solid {colors['border_color']};
                border-radius: 4px;
                padding: 6px;
            }}
            QSpinBox:hover, QLineEdit:hover, QTextEdit:hover {{
                border-color: {colors['accent_color']};
                background-color: {colors['hover_color']};
                color: {hover_text_color};
            }}
            QSpinBox:focus, QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['accent_color']};
                border-width: 2px;
            }}
            QScrollArea {{
                background-color: {colors['bg_color']};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {colors['bg_color']};
            }}
            QScrollBar:vertical {{
                background-color: {colors['button_color']};
                width: 12px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['border_color']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['accent_color']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QFormLayout, QVBoxLayout, QHBoxLayout, QGridLayout {{
                background-color: transparent;
            }}
        """)



    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Настройки GopiAI")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)

        # Применяем полную интеграцию с темой
        self._apply_theme_styles()

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("Настройки")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Добавляем кнопку закрытия для безрамочного режима
        self.close_button = create_icon_button("x", "Закрыть настройки")
        self.close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.close_button)

        main_layout.addLayout(header_layout)

        # Tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Создание вкладок
        self.create_appearance_tab()
        self.create_interface_tab()
        self.create_advanced_tab()

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_button = create_icon_button("check", "Применить")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        self.ok_button = create_icon_button("check", "OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = create_icon_button("x", "Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def create_appearance_tab(self):
        """Создание вкладки внешнего вида"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Карточка темы
        theme_card = SettingsCard(
            "Тема приложения", "Выберите тему оформления интерфейса"
        )

        theme_layout = QVBoxLayout()

        # Выбор темы
        theme_combo_layout = QHBoxLayout()
        theme_label = QLabel("Тема:")
        theme_combo_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        print(f"🔧 theme_combo создан: {self.theme_combo}")

        # Заполнение списка тем
        if self.theme_manager:
            themes = self.theme_manager.get_theme_display_names()
            for theme_key, display_name in themes.items():
                self.theme_combo.addItem(display_name, theme_key)
            print(f"🔧 theme_combo заполнен, count = {self.theme_combo.count()}")

        theme_combo_layout.addWidget(self.theme_combo)
        print(f"🔧 theme_combo добавлен в layout")
        theme_combo_layout.addStretch()
        theme_layout.addLayout(theme_combo_layout)

        # Переключатель темного режима
        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addWidget(QLabel("Темный режим:"))

        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setToolTip("Включить темный режим интерфейса")
        dark_mode_layout.addWidget(self.dark_mode_check)
        dark_mode_layout.addStretch()
        theme_layout.addLayout(dark_mode_layout)

        # Добавляем все в карточку
        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)
        theme_card.add_content(theme_widget)
        layout.addWidget(theme_card)

        # Карточка шрифтов
        font_card = SettingsCard("Шрифты", "Настройка размера и типа шрифтов")

        font_layout = QFormLayout()

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(10)
        font_layout.addRow("Размер шрифта:", self.font_size_spin)

        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(
            [
                "System Default",
                "Arial",
                "Helvetica",
                "Times New Roman",
                "Courier New",
                "Verdana",
                "Georgia",
                "Comic Sans MS",
            ]
        )
        font_layout.addRow("Семейство шрифта:", self.font_family_combo)

        font_widget = QWidget()
        font_widget.setLayout(font_layout)
        font_card.add_content(font_widget)
        layout.addWidget(font_card)

        # Добавляем вкладку в TabWidget
        self.tab_widget.addTab(scroll, "Внешний вид")

    def create_interface_tab(self):
        """Создание вкладки интерфейса"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Карточка панели инструментов
        toolbar_card = SettingsCard(
            "Панель инструментов", "Настройка отображения панели инструментов"
        )

        toolbar_layout = QVBoxLayout()

        self.show_toolbar_check = QCheckBox("Показывать панель инструментов")
        self.show_toolbar_check.setChecked(True)
        toolbar_layout.addWidget(self.show_toolbar_check)
        # Размер панели инструментов
        toolbar_size_layout = QHBoxLayout()
        toolbar_size_layout.addWidget(QLabel("Размер иконок:"))

        self.toolbar_size_combo = QComboBox()
        self.toolbar_size_combo.addItems(["Маленькая", "Средняя", "Большая"])
        self.toolbar_size_combo.setCurrentText("Средняя")
        toolbar_size_layout.addWidget(self.toolbar_size_combo)
        toolbar_size_layout.addStretch()
        toolbar_layout.addLayout(toolbar_size_layout)

        toolbar_layout.addStretch()

        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_card.add_content(toolbar_widget)
        layout.addWidget(toolbar_card)

        # Карточка статусной строки
        status_card = SettingsCard(
            "Статусная строка", "Настройка информации в статусной строке"
        )

        status_layout = QVBoxLayout()

        self.show_status_check = QCheckBox("Показывать статусную строку")
        self.show_status_check.setChecked(True)
        status_layout.addWidget(self.show_status_check)

        self.show_memory_check = QCheckBox("Показывать использование памяти")
        self.show_memory_check.setChecked(False)
        status_layout.addWidget(self.show_memory_check)

        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_card.add_content(status_widget)
        layout.addWidget(status_card)

        # Карточка окон
        windows_card = SettingsCard("Окна", "Настройка поведения окон")

        windows_layout = QVBoxLayout()

        self.remember_geometry_check = QCheckBox("Запоминать размер и положение окон")
        self.remember_geometry_check.setChecked(True)
        windows_layout.addWidget(self.remember_geometry_check)

        self.minimize_to_tray_check = QCheckBox("Сворачивать в системный трей")
        self.minimize_to_tray_check.setChecked(False)
        windows_layout.addWidget(self.minimize_to_tray_check)

        windows_widget = QWidget()
        windows_widget.setLayout(windows_layout)
        windows_card.add_content(windows_widget)
        layout.addWidget(windows_card)

        layout.addStretch()
        self.tab_widget.addTab(scroll, "Интерфейс")

    def create_advanced_tab(self):
        """Создание вкладки дополнительных настроек"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Карточка производительности
        performance_card = SettingsCard(
            "Производительность", "Настройки для оптимизации работы приложения"
        )

        perf_layout = QFormLayout()

        self.animation_check = QCheckBox("Включить анимации")
        self.animation_check.setChecked(True)
        perf_layout.addRow("Анимации:", self.animation_check)

        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" МБ")
        perf_layout.addRow("Размер кэша:", self.cache_size_spin)

        perf_widget = QWidget()
        perf_widget.setLayout(perf_layout)
        performance_card.add_content(perf_widget)
        layout.addWidget(performance_card)

        # Карточка логирования
        logging_card = SettingsCard("Логирование", "Настройка уровня детализации логов")

        log_layout = QFormLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow("Уровень логирования:", self.log_level_combo)

        self.log_to_file_check = QCheckBox("Сохранять логи в файл")
        self.log_to_file_check.setChecked(True)
        log_layout.addRow("В файл:", self.log_to_file_check)

        log_widget = QWidget()
        log_widget.setLayout(log_layout)
        logging_card.add_content(log_widget)
        layout.addWidget(logging_card)

        # Карточка инструментов (терминал)
        tools_card = SettingsCard(
            "Инструменты",
            "Настройка инструментов. Внимание: небезопасный терминал позволяет выполнять реальные команды ОС. Используйте с осторожностью!",
        )

        tools_layout = QVBoxLayout()
        self.terminal_unsafe_check = QCheckBox("Разрешить терминал без ограничений (ОПАСНО)")
        self.terminal_unsafe_check.setToolTip(
            "Включает реальное выполнение команд в терминале без ограничений безопасности."
        )
        self.terminal_unsafe_check.stateChanged.connect(self._on_terminal_unsafe_toggled)
        tools_layout.addWidget(self.terminal_unsafe_check)

        tools_widget = QWidget()
        tools_widget.setLayout(tools_layout)
        tools_card.add_content(tools_widget)
        layout.addWidget(tools_card)

        # Карточка сброса настроек
        reset_card = SettingsCard(
            "Сброс настроек", "Восстановление настроек по умолчанию"
        )

        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Сбросить все настройки")
        self.reset_button.clicked.connect(self.reset_settings)
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()

        reset_widget = QWidget()
        reset_widget.setLayout(reset_layout)
        reset_card.add_content(reset_widget)
        layout.addWidget(reset_card)

        layout.addStretch()
        self.tab_widget.addTab(scroll, "Дополнительно")

        # Загрузим состояние небезопасного терминала после построения вкладки
        self._load_terminal_unsafe()

    def load_current_settings(self):
        """Загрузка текущих настроек"""
        print("🔧 load_current_settings() начат")
        try:
            if self.theme_manager:
                print("🔧 theme_manager существует")
                current_theme = self.theme_manager.get_current_theme()
                print(f"🔧 current_theme = {current_theme}")

                # Проверяем, что theme_combo существует и действителен
                if hasattr(self, "theme_combo") and self.theme_combo:
                    try:
                        # Безопасная проверка валидности объекта
                        if not is_qt_object_valid(self.theme_combo):
                            print(
                                "⚠️ theme_combo недействителен, пропускаем установку текущей темы"
                            )
                            return

                        print(f"🔧 theme_combo существует: {self.theme_combo}")
                        count = self.theme_combo.count()
                        print(f"🔧 theme_combo.count() = {count}")

                        # Найти индекс текущей темы в комбобоксе
                        for i in range(count):
                            try:
                                if self.theme_combo.itemData(i) == current_theme:
                                    self.theme_combo.setCurrentIndex(i)
                                    print(f"🔧 Установлен индекс темы: {i}")
                                    break
                            except Exception as e:
                                print(
                                    f"⚠️ Ошибка при получении данных из theme_combo: {e}"
                                )
                                break
                    except RuntimeError as e:
                        if "Internal C++ object" in str(e):
                            print(f"⚠️ C++ объект QComboBox уже удален: {e}")
                        else:
                            print(f"❌ Ошибка при работе с theme_combo: {e}")
                    except Exception as e:
                        print(f"❌ Ошибка при работе с theme_combo: {e}")
                        print(f"❌ Тип ошибки: {type(e)}")
                else:
                    print("❌ theme_combo не существует или был удален!")

                # Устанавливаем темный режим если у менеджера тем есть соответствующий атрибут
                try:
                    if hasattr(self, "dark_mode_check") and hasattr(
                        self.theme_manager, "_current_variant"
                    ):
                        # Проверяем, что dark_mode_check действителен
                        if not is_qt_object_valid(self.dark_mode_check):
                            print(
                                "⚠️ dark_mode_check недействителен, пропускаем установку темного режима"
                            )
                            return

                        self.dark_mode_check.setChecked(
                            self.theme_manager._current_variant == "dark"
                        )
                        print(
                            f"🔧 Установлен темный режим: {self.theme_manager._current_variant == 'dark'}"
                        )
                except Exception as e:
                    print(f"❌ Ошибка при установке темного режима: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка открытия настроек: {e}")

        print("🔧 load_current_settings() завершен")

    def collect_settings(self) -> dict:
        """Сбор всех настроек из интерфейса"""
        settings = {}
        try:
            # Безопасное получение значений из виджетов
            if is_qt_object_valid(self.theme_combo):
                settings["theme"] = self.theme_combo.currentData()
            if is_qt_object_valid(self.dark_mode_check):
                settings["dark_mode"] = self.dark_mode_check.isChecked()
            if is_qt_object_valid(self.font_size_spin):
                settings["font_size"] = self.font_size_spin.value()
            if is_qt_object_valid(self.font_family_combo):
                settings["font_family"] = self.font_family_combo.currentText()
            if is_qt_object_valid(self.show_toolbar_check):
                settings["show_toolbar"] = self.show_toolbar_check.isChecked()
            if is_qt_object_valid(self.toolbar_size_combo):
                settings["toolbar_size"] = self.toolbar_size_combo.currentText()
            if is_qt_object_valid(self.show_status_check):
                settings["show_status"] = self.show_status_check.isChecked()
            if is_qt_object_valid(self.show_memory_check):
                settings["show_memory"] = self.show_memory_check.isChecked()
            if is_qt_object_valid(self.remember_geometry_check):
                settings["remember_geometry"] = self.remember_geometry_check.isChecked()
            if is_qt_object_valid(self.minimize_to_tray_check):
                settings["minimize_to_tray"] = self.minimize_to_tray_check.isChecked()
            if is_qt_object_valid(self.animation_check):
                settings["animations"] = self.animation_check.isChecked()
            if is_qt_object_valid(self.cache_size_spin):
                settings["cache_size"] = self.cache_size_spin.value()
            if is_qt_object_valid(self.log_level_combo):
                settings["log_level"] = self.log_level_combo.currentText()
            if is_qt_object_valid(self.log_to_file_check):
                settings["log_to_file"] = self.log_to_file_check.isChecked()
        except Exception as e:
            print(f"⚠️ Ошибка при сборе настроек: {e}")

        return settings

    # События мыши для перетаскивания безрамочного окна
    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши для начала перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перетаскивания окна"""
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and self._drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши для завершения перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            event.accept()

    def apply_settings(self):
        """Применение настроек"""
        try:
            self.settings = self.collect_settings()

            # Применение темы и темного режима
            if self.theme_manager and "theme" in self.settings:
                theme_name = self.settings.get("theme")

                # Устанавливаем темный/светлый вариант в менеджере тем
                if (
                    hasattr(self.theme_manager, "_current_variant")
                    and "dark_mode" in self.settings
                ):
                    self.theme_manager._current_variant = (
                        "dark" if self.settings.get("dark_mode", False) else "light"
                    )

                # Применяем тему
                self.theme_manager.apply_theme(theme_name)

                # Применяем тему также к диалогу настроек для мгновенного обновления
                self._update_dialog_theme()

                # Сигнал изменения темы
                self.themeChanged.emit(theme_name)

            # Испускание сигнала для передачи настроек в основное окно
            self.settings_applied.emit(self.settings)
        except Exception as e:
            print(f"⚠️ Ошибка при применении настроек: {e}")

    def _update_dialog_theme(self):
        """Обновляет тему диалога настроек, применяя текущие цвета из менеджера тем"""
        try:
            # Применяем новую систему стилей с полной интеграцией
            self._apply_theme_styles()
            
            # Обновляем стиль кнопки закрытия
            if hasattr(self, 'close_button'):
                self._apply_close_button_style()
            
            # Принудительно обновляем все дочерние виджеты
            for child in self.findChildren(QWidget):
                if is_qt_object_valid(child):
                    try:
                        # Некоторые виджеты (например QListView) требуют аргументы для update()
                        # Поэтому вызываем repaint() который безопаснее
                        child.repaint()
                    except Exception:
                        # Если и repaint не работает, просто пропускаем
                        pass
    
            # Обновляем также сам диалог
            self.repaint()
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении темы диалога: {e}")




    def accept_settings(self):
        """Принятие и применение настроек с закрытием диалога"""
        try:
            self.apply_settings()
            self.accept()
        except Exception as e:
            print(f"⚠️ Ошибка при принятии настроек: {e}")

    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            # Сброс темы
            if is_qt_object_valid(self.theme_combo) and self.theme_combo.count() > 0:
                self.theme_combo.setCurrentIndex(0)

            # Сброс темного режима
            if is_qt_object_valid(self.dark_mode_check):
                self.dark_mode_check.setChecked(False)

            # Сброс других настроек
            if is_qt_object_valid(self.font_size_spin):
                self.font_size_spin.setValue(10)
            if is_qt_object_valid(self.font_family_combo):
                self.font_family_combo.setCurrentIndex(0)
            if is_qt_object_valid(self.show_toolbar_check):
                self.show_toolbar_check.setChecked(True)
            if is_qt_object_valid(self.toolbar_size_combo):
                self.toolbar_size_combo.setCurrentText("Средняя")
            if is_qt_object_valid(self.show_status_check):
                self.show_status_check.setChecked(True)
            if is_qt_object_valid(self.show_memory_check):
                self.show_memory_check.setChecked(False)
            if is_qt_object_valid(self.remember_geometry_check):
                self.remember_geometry_check.setChecked(True)
            if is_qt_object_valid(self.minimize_to_tray_check):
                self.minimize_to_tray_check.setChecked(False)
            if is_qt_object_valid(self.animation_check):
                self.animation_check.setChecked(True)            
            if is_qt_object_valid(self.cache_size_spin):
                self.cache_size_spin.setValue(100)
            if is_qt_object_valid(self.log_level_combo):
                self.log_level_combo.setCurrentText("INFO")
            if is_qt_object_valid(self.log_to_file_check):
                self.log_to_file_check.setChecked(True)
        except Exception as e:
            print(f"⚠️ Ошибка при сбросе настроек: {e}")
