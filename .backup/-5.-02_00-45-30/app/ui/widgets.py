from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPlainTextEdit
from PySide6.QtGui import QFont, QFontMetrics # Added QFont, QFontMetrics
from PySide6.QtCore import Qt, Signal
from .i18n.translator import tr
# Assuming icon_manager and theme_manager might be needed for full functionality based on original main_window.py
# from .icon_manager import get_icon
# from .theme_manager import theme_manager

class ChatWidget(QWidget):
    message_sent = Signal(str) # <--- Сигнал для отправки сообщений
    insert_code_to_editor = Signal(str) # <--- Сигнал для вставки кода в редактор
    run_code_in_terminal = Signal(str) # <--- Сигнал для запуска кода в терминале

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Это можно будет убрать, если main_window больше не нужен напрямую
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.layout.addWidget(self.chat_history)

        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self._on_message_sent)
        self.layout.addWidget(self.message_input)

    def _on_message_sent(self):
        message = self.message_input.text()
        self.message_input.clear()
        # self.main_window._handle_user_message(message) # <--- Заменяем прямой вызов
        self.message_sent.emit(message) # <--- Испускаем сигнал

    def add_message(self, sender, text):
        """Добавляет сообщение в историю чата."""
        message = f"<b>{sender}:</b> {text}"
        self.chat_history.append(message)

    def _extract_code_from_selection(self, text):
        """Извлекает код из выделенного текста."""
        import re
        markdown_code_match = re.search(r'```(?:\w*\n)?([\s\S]*?)```', text)
        if markdown_code_match:
            return markdown_code_match.group(1)
        return text

class CodeEditor(QPlainTextEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.file_path = None
        self._init_editor()

    def _init_editor(self):
        font = QFont("JetBrains Mono")
        font.setPointSize(10)
        self.setFont(font)

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(4 * QFontMetrics(font).horizontalAdvance(' '))

    def insert_code(self, code):
        """Insert code at the current cursor position."""
        cursor = self.textCursor()
        cursor.insertText(code)
        self.setTextCursor(cursor)

class TerminalWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Initialize terminal widget with actual terminal functionality

        # Terminal output display
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.layout.addWidget(self.terminal_output)

        # Command input
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self._on_command_entered)
        self.layout.addWidget(self.command_input)

        # Set up process for command execution
        self.process = None

    def _on_command_entered(self):
        """Handle command input."""
        command = self.command_input.text()
        self.command_input.clear()
        self.execute_command(command)

    def execute_command(self, command):
        """Execute a command in the terminal."""
        # Display the command in the output
        self.terminal_output.append(f"> {command}")

        # Actual implementation would connect to a real terminal/process
        # For now, just simulate output
        self.terminal_output.append("Command executed (this is a placeholder)")

        # In a real implementation, you would:
        # if hasattr(self, "process") and hasattr(self.process, "write"):
        #     self.process.write(command.encode() + b"\n")
