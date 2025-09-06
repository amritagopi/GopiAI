"""
Terminal Widget Component для GopiAI Standalone Interface
======================================================

Интерактивный виджет терминала с вкладками и поддержкой выполнения команд.
"""
from typing import cast, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QTextEdit
from PySide6.QtCore import Signal, Qt, QProcess
from PySide6.QtGui import QTextCursor, QFont
from gopiai.ui.utils.icon_helpers import create_icon_button
# Импорт ansi2html с fallback
try:
    # Локально алиасим внешний класс, чтобы Pyright видел единый символ
    from ansi2html import Ansi2HTMLConverter as _ExternalAnsi2HTMLConverter  # type: ignore[import-not-found]
    Ansi2HTMLConverter = _ExternalAnsi2HTMLConverter  # type: ignore[assignment]
    ANSI2HTML_AVAILABLE = True
except ImportError:
    print("[WARNING] ansi2html module not found, using fallback implementation.")
    ANSI2HTML_AVAILABLE = False

    class Ansi2HTMLConverter:
        """Fallback класс для ansi2html"""
        def __init__(self):
            pass

        def convert(self, text, full=True):
            # Простая очистка ANSI кодов
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            return ansi_escape.sub('', text)


class InteractiveTerminal(QTextEdit):
    """Интерактивный терминал с поддержкой ввода команд (строго ВСТРОЕННЫЙ виджет, не окно)"""
    
    command_executed = Signal(str)  # Сигнал для выполненной команды
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # ЖЕСТКАЯ ЗАЩИТА ОТ "ПЛАВАЮЩЕГО ОКНА"
        # Принудительно запрещаем любые оконные флаги и всплывающее отображение
        try:
            # Только виджет, без флагов окна
            self.setWindowFlags(Qt.WindowType.Widget)
            # На всякий случай скрыт (видимость контролирует контейнер внизу)
            self.setVisible(True)
        except Exception:
            pass

        self.prompt = '> '
        self.setFont(QFont("Consolas", 10))
        self.setReadOnly(False)

        # Процесс терминала
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.stateChanged.connect(self.handle_state)
        # Всегда запускаем в текущем окружении без открытия дополнительных окон
        self.process.setProgram("cmd.exe")
        self.process.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return: # type: ignore[attr-defined]
            command = self.toPlainText()[self.toPlainText().rfind(self.prompt) + len(self.prompt):]
            self.process.write(command.encode() + b'\n')
            self.insertPlainText('\n')
            self._scroll_to_bottom()
        else:
            super().keyPressEvent(event)

    def handle_stdout(self):
        data = bytes(self.process.readAllStandardOutput().data()).decode('cp866')  # Декодируем в CP866 (для cmd.exe на русском)
        converter: Any = Ansi2HTMLConverter()
        html = converter.convert(data, full=False)
        self.insertHtml(html)
        self.insertPlainText(self.prompt)
        self._scroll_to_bottom()

    def handle_stderr(self):
        data = bytes(self.process.readAllStandardError().data()).decode('cp866')  # Декодируем в CP866
        # Не используем жесткие цвета — выводим как простой текст с пометкой stderr
        converter: Any = Ansi2HTMLConverter()
        text = converter.convert(data, full=False)
        self.insertPlainText(f"[stderr] {text}")
        self.insertPlainText(self.prompt)
        self._scroll_to_bottom()

    def handle_state(self, state):
        if state == QProcess.ProcessState.Running:
            self.insertPlainText('Process running\n' + self.prompt)
            self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class TerminalWidget(QWidget):
    """Виджет терминала с вкладками (встраиваемый док). Плавающие окна запрещены."""
    # Singleton-ссылка на встроенный экземпляр
    instance: "TerminalWidget | None" = None  # type: ignore[name-defined]

    def __init__(self, parent=None):
        super().__init__(parent)

        # Если кто-то создаёт TerminalWidget без родителя, не позволяем сделать его отдельным окном
        if parent is None:
            try:
                self.setWindowFlags(Qt.WindowType.Widget)
                self.setVisible(False)
            except Exception:
                pass

        # Политика размеров: терминал плавно масштабируется по ширине и имеет фиксированную высоту
        try:
            from PySide6.QtWidgets import QSizePolicy
            size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            size_policy.setHorizontalStretch(1)
            size_policy.setVerticalStretch(0)
            self.setSizePolicy(size_policy)
        except Exception:
            pass

        # Внешние отступы: небольшой отступ СНИЗУ, как у других панелей
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 8)  # top=0, bottom=8
        layout.setSpacing(6)

        # Область вкладок терминала
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs, 1)

        # Нижняя панель действий + заголовок слева (единая линия управления)
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 6, 0, 0)
        title = QLabel("Терминал")
        title.setObjectName("panelHeader")
        title.setFixedHeight(24)
        controls.addWidget(title)
        controls.addStretch()
        add_tab_btn = create_icon_button("plus", "Новая вкладка терминала")
        add_tab_btn.clicked.connect(self.add_tab)
        controls.addWidget(add_tab_btn)
        layout.addLayout(controls)

        # Рекомендуемые пределы высоты, чтобы работало “между” панелями
        self.setMinimumHeight(150)
        self.setMaximumHeight(400)

        # Устанавливаем singleton
        try:
            TerminalWidget.instance = self  # type: ignore[assignment]
        except Exception:
            pass

        self.add_tab()

    def add_tab(self):
        # Создаем терминал только как дочерний виджет вкладки
        terminal = InteractiveTerminal(parent=self)
        # На всякий случай убеждаемся, что это не отдельное окно
        try:
            terminal.setWindowFlags(Qt.WindowType.Widget)
        except Exception:
            pass
        index = self.tabs.addTab(terminal, f"Terminal {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(index)
        return index

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def execute_command(self, command, tab_index=-1):
        if tab_index == -1:
            tab_index = self.tabs.currentIndex()
        terminal = cast(InteractiveTerminal, self.tabs.widget(tab_index))
        if terminal:
            # НИКОГДА не показывать отдельное окно — работаем только во встроенном виджете
            try:
                terminal.setWindowFlags(Qt.WindowType.Widget)
            except Exception:
                pass
            terminal.insertPlainText(command + '\n')
            terminal.process.write(command.encode() + b'\n')
            terminal.insertPlainText(terminal.prompt)

    def log_ai_command(self, command, output):
        current_terminal = cast(InteractiveTerminal, self.tabs.currentWidget())
        if current_terminal:
            current_terminal.insertPlainText(f'[AI] Executed: {command}\n{output}\n')
            current_terminal.insertPlainText(current_terminal.prompt)
