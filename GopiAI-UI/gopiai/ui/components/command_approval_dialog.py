"""
Диалог подтверждения команд для GopiAI
Показывает пользователю команды, требующие подтверждения, и позволяет их принять или отклонить
"""

import logging
import requests
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QWidget, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from gopiai.ui.utils.icon_helpers import create_icon_button, get_icon
from gopiai.ui.utils.network import get_crewai_server_base_url

logger = logging.getLogger(__name__)

class CommandApprovalWidget(QFrame):
    """Виджет для отображения одной команды, требующей подтверждения"""
    
    command_approved = Signal(str)  # command_id
    command_rejected = Signal(str)  # command_id
    
    def __init__(self, command_info: Dict, parent=None):
        super().__init__(parent)
        self.command_info = command_info
        self.command_id = command_info.get('id', '')
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Заголовок с уровнем риска
        header_layout = QHBoxLayout()
        
        risk_level = self.command_info.get('risk_level', 'UNKNOWN')
        risk_label = QLabel(f"🔐 Команда требует подтверждения (риск: {risk_level})")
        risk_font = QFont()
        risk_font.setBold(True)
        risk_label.setFont(risk_font)
        
        # Цвет в зависимости от уровня риска
        if risk_level == 'HIGH':
            risk_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        elif risk_level == 'MEDIUM':
            risk_label.setStyleSheet("color: #fd7e14; font-weight: bold;")
        else:
            risk_label.setStyleSheet("color: #28a745; font-weight: bold;")
        
        header_layout.addWidget(risk_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Команда
        command_text = self.command_info.get('command', '')
        command_label = QLabel("Команда:")
        command_font = QFont()
        command_font.setBold(True)
        command_label.setFont(command_font)
        layout.addWidget(command_label)
        
        command_display = QTextEdit()
        command_display.setPlainText(command_text)
        command_display.setMaximumHeight(80)
        command_display.setReadOnly(True)
        command_display.setStyleSheet("""
            QTextEdit {
                background-color: #f1f3f4;
                border: 1px solid #dadce0;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 6px;
            }
        """)
        layout.addWidget(command_display)
        
        # Информация о команде
        reason = self.command_info.get('reason', '')
        if reason:
            reason_label = QLabel(f"Причина: {reason}")
            reason_label.setWordWrap(True)
            reason_label.setStyleSheet("color: #6c757d; font-size: 11px;")
            layout.addWidget(reason_label)
        
        # Время создания
        created_at = self.command_info.get('created_at', '')
        if created_at:
            time_label = QLabel(f"Создано: {created_at}")
            time_label.setStyleSheet("color: #6c757d; font-size: 10px;")
            layout.addWidget(time_label)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка отклонения
        reject_btn = QPushButton("🚫 Отклонить")
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        reject_btn.clicked.connect(self._on_reject_clicked)
        buttons_layout.addWidget(reject_btn)
        
        # Кнопка подтверждения
        approve_btn = QPushButton("✅ Подтвердить")
        approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        approve_btn.clicked.connect(self._on_approve_clicked)
        buttons_layout.addWidget(approve_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_approve_clicked(self):
        """Обработчик подтверждения команды"""
        logger.info(f"Пользователь подтвердил команду: {self.command_id}")
        self.command_approved.emit(self.command_id)
    
    def _on_reject_clicked(self):
        """Обработчик отклонения команды"""
        logger.info(f"Пользователь отклонил команду: {self.command_id}")
        self.command_rejected.emit(self.command_id)


class CommandApprovalDialog(QDialog):
    """Диалог для подтверждения команд"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_base = get_crewai_server_base_url()
        self.pending_commands: Dict[str, CommandApprovalWidget] = {}
        
        # Таймер для polling pending команд
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_pending_commands)
        self.poll_timer.start(2000)  # Проверяем каждые 2 секунды
        
        self._setup_ui()
        self._poll_pending_commands()  # Первоначальная загрузка
        
        logger.info("CommandApprovalDialog инициализирован")
    
    def _setup_ui(self):
        self.setWindowTitle("Подтверждение команд GopiAI")
        self.setModal(False)  # Не блокируем основное окно
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Заголовок
        title_label = QLabel("🔐 Команды, требующие подтверждения")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Описание
        desc_label = QLabel(
            "Некоторые команды требуют вашего подтверждения перед выполнением. "
            "Пожалуйста, внимательно проверьте команды перед подтверждением."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Область прокрутки для команд
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.commands_container = QWidget()
        self.commands_layout = QVBoxLayout(self.commands_container)
        self.commands_layout.setContentsMargins(0, 0, 0, 0)
        self.commands_layout.setSpacing(8)
        
        # Сообщение когда нет команд
        self.no_commands_label = QLabel("✅ Нет команд, требующих подтверждения")
        self.no_commands_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_commands_label.setStyleSheet("""
            color: #28a745;
            font-size: 14px;
            font-weight: bold;
            padding: 40px;
        """)
        self.commands_layout.addWidget(self.no_commands_label)
        
        scroll_area.setWidget(self.commands_container)
        layout.addWidget(scroll_area, 1)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._poll_pending_commands)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _poll_pending_commands(self):
        """Запрашивает список pending команд с сервера"""
        try:
            response = requests.get(f"{self.api_base}/api/commands/pending", timeout=5)
            if response.status_code == 200:
                data = response.json()
                pending_commands = data.get('commands', [])
                self._update_commands_display(pending_commands)
            else:
                logger.warning(f"Не удалось получить pending команды: {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"Ошибка при запросе pending команд: {e}")
    
    def _update_commands_display(self, commands: List[Dict]):
        """Обновляет отображение команд"""
        # Удаляем команды, которых больше нет
        current_command_ids = {cmd.get('id') for cmd in commands}
        for command_id in list(self.pending_commands.keys()):
            if command_id not in current_command_ids:
                widget = self.pending_commands.pop(command_id)
                widget.deleteLater()
        
        # Добавляем новые команды
        for command_info in commands:
            command_id = command_info.get('id')
            if command_id and command_id not in self.pending_commands:
                widget = CommandApprovalWidget(command_info)
                widget.command_approved.connect(self._approve_command)
                widget.command_rejected.connect(self._reject_command)
                
                self.pending_commands[command_id] = widget
                self.commands_layout.addWidget(widget)
        
        # Показываем/скрываем сообщение о отсутствии команд
        has_commands = len(self.pending_commands) > 0
        self.no_commands_label.setVisible(not has_commands)
        
        # Показываем диалог, если есть команды и он скрыт
        if has_commands and not self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()
    
    def _approve_command(self, command_id: str):
        """Подтверждает выполнение команды"""
        try:
            response = requests.post(
                f"{self.api_base}/api/commands/{command_id}/approve",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Команда {command_id} успешно подтверждена")
                # Удаляем виджет команды
                if command_id in self.pending_commands:
                    widget = self.pending_commands.pop(command_id)
                    widget.deleteLater()
                    
                    # Проверяем, остались ли команды
                    if not self.pending_commands:
                        self.no_commands_label.setVisible(True)
                        # Закрываем диалог через 3 секунды, если больше нет команд
                        QTimer.singleShot(3000, self._auto_close_if_empty)
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось подтвердить команду: {response.status_code}")
        except requests.RequestException as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при подтверждении команды: {e}")
    
    def _reject_command(self, command_id: str):
        """Отклоняет выполнение команды"""
        try:
            response = requests.post(
                f"{self.api_base}/api/commands/{command_id}/reject",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Команда {command_id} отклонена")
                # Удаляем виджет команды
                if command_id in self.pending_commands:
                    widget = self.pending_commands.pop(command_id)
                    widget.deleteLater()
                    
                    # Проверяем, остались ли команды
                    if not self.pending_commands:
                        self.no_commands_label.setVisible(True)
                        # Закрываем диалог через 3 секунды, если больше нет команд
                        QTimer.singleShot(3000, self._auto_close_if_empty)
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось отклонить команду: {response.status_code}")
        except requests.RequestException as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при отклонении команды: {e}")
    
    def _auto_close_if_empty(self):
        """Автоматически закрывает диалог, если нет pending команд"""
        if not self.pending_commands:
            self.close()
    
    def closeEvent(self, event):
        """Обработчик закрытия диалога"""
        # Останавливаем таймер polling при закрытии
        self.poll_timer.stop()
        super().closeEvent(event)
    
    def show(self):
        """Переопределяем show для логирования"""
        logger.info("Показываем диалог подтверждения команд")
        super().show()