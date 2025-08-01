"""
Error Display System для GopiAI UI
=================================

Централизованная система отображения ошибок пользователю.
Обеспечивает user-friendly отображение различных типов ошибок.
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame, QMessageBox, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

logger = logging.getLogger(__name__)


class ErrorDisplayWidget(QWidget):
    """Виджет для отображения ошибок в интерфейсе"""
    
    # Сигналы для взаимодействия
    retryRequested = Signal(str)  # Запрос повтора операции
    dismissRequested = Signal()   # Запрос закрытия ошибки
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("errorDisplayWidget")
        self._setup_ui()
        self._current_error_data = None
        
    def _setup_ui(self):
        """Настройка интерфейса виджета ошибок"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок ошибки
        self.error_title = QLabel()
        self.error_title.setObjectName("errorTitle")
        self.error_title.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.error_title.setFont(font)
        layout.addWidget(self.error_title)
        
        # Описание ошибки
        self.error_description = QLabel()
        self.error_description.setObjectName("errorDescription")
        self.error_description.setWordWrap(True)
        self.error_description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.error_description)
        
        # Детали ошибки (скрываемые)
        self.details_frame = QFrame()
        self.details_frame.setFrameStyle(QFrame.Shape.Box)
        self.details_frame.setVisible(False)
        details_layout = QVBoxLayout(self.details_frame)
        
        self.error_details = QTextEdit()
        self.error_details.setObjectName("errorDetails")
        self.error_details.setMaximumHeight(150)
        self.error_details.setReadOnly(True)
        details_layout.addWidget(self.error_details)
        
        layout.addWidget(self.details_frame)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        self.retry_button = QPushButton("🔄 Повторить")
        self.retry_button.setObjectName("retryButton")
        self.retry_button.clicked.connect(self._on_retry_clicked)
        self.retry_button.setVisible(False)
        buttons_layout.addWidget(self.retry_button)
        
        self.details_button = QPushButton("📋 Подробности")
        self.details_button.setObjectName("detailsButton")
        self.details_button.clicked.connect(self._toggle_details)
        buttons_layout.addWidget(self.details_button)
        
        self.dismiss_button = QPushButton("✖ Закрыть")
        self.dismiss_button.setObjectName("dismissButton")
        self.dismiss_button.clicked.connect(self._on_dismiss_clicked)
        buttons_layout.addWidget(self.dismiss_button)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Применяем стили
        self._apply_error_styles()
        
    def _apply_error_styles(self):
        """Применение стилей для отображения ошибок"""
        self.setStyleSheet("""
            QWidget#errorDisplayWidget {
                background-color: #ffebee;
                border: 2px solid #f44336;
                border-radius: 8px;
                margin: 5px;
            }
            QLabel#errorTitle {
                color: #c62828;
                padding: 5px;
            }
            QLabel#errorDescription {
                color: #424242;
                padding: 5px;
            }
            QTextEdit#errorDetails {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#retryButton {
                background-color: #4caf50;
                color: white;
                border: none;
            }
            QPushButton#retryButton:hover {
                background-color: #45a049;
            }
            QPushButton#detailsButton {
                background-color: #2196f3;
                color: white;
                border: none;
            }
            QPushButton#detailsButton:hover {
                background-color: #1976d2;
            }
            QPushButton#dismissButton {
                background-color: #f44336;
                color: white;
                border: none;
            }
            QPushButton#dismissButton:hover {
                background-color: #d32f2f;
            }
        """)
        
    def show_api_error(self, error_message: str, error_code: str = None, retry_action: str = None):
        """Отображение ошибки API"""
        self.error_title.setText("🔌 Ошибка подключения к API")
        
        if error_code:
            description = f"Код ошибки: {error_code}\n{error_message}"
        else:
            description = error_message
            
        self.error_description.setText(description)
        
        # Показываем кнопку повтора для API ошибок
        if retry_action:
            self.retry_button.setVisible(True)
            self._current_error_data = {"type": "api", "action": retry_action}
        else:
            self.retry_button.setVisible(False)
            
        self.error_details.setText(f"Время: {self._get_current_time()}\nТип: API Error\nДетали: {error_message}")
        self.setVisible(True)
        
    def show_connection_error(self, service_name: str = "Backend Server"):
        """Отображение ошибки подключения"""
        self.error_title.setText("🚫 Ошибка подключения")
        self.error_description.setText(
            f"Не удается подключиться к {service_name}.\n"
            "Проверьте, что сервер запущен и доступен."
        )
        
        self.retry_button.setVisible(True)
        self._current_error_data = {"type": "connection", "service": service_name}
        
        self.error_details.setText(
            f"Время: {self._get_current_time()}\n"
            f"Тип: Connection Error\n"
            f"Сервис: {service_name}\n"
            "Возможные причины:\n"
            "- Сервер не запущен\n"
            "- Проблемы с сетью\n"
            "- Неверная конфигурация"
        )
        self.setVisible(True)
        
    def show_component_error(self, component_name: str, error_details: str, fallback_available: bool = False):
        """Отображение ошибки компонента UI"""
        self.error_title.setText(f"⚠️ Ошибка компонента: {component_name}")
        
        description = f"Произошла ошибка при работе с компонентом {component_name}."
        if fallback_available:
            description += "\nИспользуется резервный режим работы."
            
        self.error_description.setText(description)
        
        self.retry_button.setVisible(not fallback_available)
        if not fallback_available:
            self._current_error_data = {"type": "component", "component": component_name}
            
        self.error_details.setText(
            f"Время: {self._get_current_time()}\n"
            f"Тип: Component Error\n"
            f"Компонент: {component_name}\n"
            f"Детали: {error_details}"
        )
        self.setVisible(True)
        
    def show_tool_error(self, tool_name: str, error_message: str, command: str = None):
        """Отображение ошибки выполнения инструмента"""
        self.error_title.setText(f"🔧 Ошибка инструмента: {tool_name}")
        
        description = f"Не удалось выполнить операцию с помощью {tool_name}."
        if command:
            description += f"\nКоманда: {command}"
            
        self.error_description.setText(description)
        
        self.retry_button.setVisible(True)
        self._current_error_data = {"type": "tool", "tool": tool_name, "command": command}
        
        self.error_details.setText(
            f"Время: {self._get_current_time()}\n"
            f"Тип: Tool Error\n"
            f"Инструмент: {tool_name}\n"
            f"Команда: {command or 'N/A'}\n"
            f"Ошибка: {error_message}"
        )
        self.setVisible(True)
        
    def show_generic_error(self, title: str, message: str, details: str = None):
        """Отображение общей ошибки"""
        self.error_title.setText(f"❌ {title}")
        self.error_description.setText(message)
        
        self.retry_button.setVisible(False)
        self._current_error_data = {"type": "generic"}
        
        error_details = f"Время: {self._get_current_time()}\nТип: Generic Error\nСообщение: {message}"
        if details:
            error_details += f"\nДетали: {details}"
            
        self.error_details.setText(error_details)
        self.setVisible(True)
        
    def _toggle_details(self):
        """Переключение отображения деталей ошибки"""
        is_visible = self.details_frame.isVisible()
        self.details_frame.setVisible(not is_visible)
        
        if is_visible:
            self.details_button.setText("📋 Подробности")
        else:
            self.details_button.setText("📋 Скрыть подробности")
            
    def _on_retry_clicked(self):
        """Обработка нажатия кнопки повтора"""
        if self._current_error_data:
            error_type = self._current_error_data.get("type", "")
            self.retryRequested.emit(error_type)
            
    def _on_dismiss_clicked(self):
        """Обработка нажатия кнопки закрытия"""
        self.setVisible(False)
        self.dismissRequested.emit()
        
    def _get_current_time(self) -> str:
        """Получение текущего времени в читаемом формате"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def auto_hide_after(self, seconds: int):
        """Автоматическое скрытие ошибки через указанное время"""
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.setVisible(False))
        timer.setSingleShot(True)
        timer.start(seconds * 1000)


class ErrorDialog(QDialog):
    """Диалоговое окно для критических ошибок"""
    
    def __init__(self, title: str, message: str, details: str = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Сообщение об ошибке
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Детали ошибки (если есть)
        if details:
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)
            
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)
        
        layout.addLayout(buttons_layout)


def show_error_dialog(title: str, message: str, details: str = None, parent=None):
    """Удобная функция для показа диалога ошибки"""
    dialog = ErrorDialog(title, message, details, parent)
    return dialog.exec()


def show_critical_error(message: str, details: str = None, parent=None):
    """Показ критической ошибки"""
    return show_error_dialog("Критическая ошибка", message, details, parent)


def show_warning_message(message: str, details: str = None, parent=None):
    """Показ предупреждения"""
    return show_error_dialog("Предупреждение", message, details, parent)