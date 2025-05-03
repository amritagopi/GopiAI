import sys
import subprocess
import threading
import os # Для получения текущей директории
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QApplication, QSizePolicy,
    QPlainTextEdit # Добавляем QPlainTextEdit
)
from PySide6.QtCore import Qt, QObject, Signal, QTimer, QEvent # Добавляем QEvent
from PySide6.QtGui import QColor, QPalette, QFont, QKeyEvent # Добавляем QKeyEvent


class CommandRunner(QObject):
    """Выполняет команду в отдельном потоке."""
    finished = Signal(str, str) # stdout, stderr

    def run_command(self, command: str):
        thread = threading.Thread(target=self._execute, args=(command,))
        thread.daemon = True # Поток завершится, если завершится основное приложение
        thread.start()

    def _execute(self, command: str):
        stdout_res = ""
        stderr_res = ""
        try:
            # Выполняем команду в текущей рабочей директории
            # shell=True - для простоты, позволяет использовать пайпы, перенаправления и т.д.
            # ВНИМАНИЕ: shell=True может быть небезопасным, если команда приходит из недоверенного источника!
            # Лучше использовать shell=False и передавать команду как список аргументов, если возможно.
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8', # Пытаемся декодировать как UTF-8
                errors='replace', # Заменяем символы, которые не удалось декодировать
                cwd=os.getcwd() # Используем текущую директорию
            )
            stdout_res = process.stdout
            stderr_res = process.stderr
        except FileNotFoundError:
            stderr_res = f"Command not found: {command.split()[0] if command else ''}"
        except Exception as e:
            stderr_res = f"Error executing command: {e}"
        finally:
            # Отправляем сигнал из потока в главный поток
            self.finished.emit(stdout_res, stderr_res)


class TerminalWidget(QWidget):
    """Виджет терминала с реальным выполнением команд."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.command_runner = CommandRunner()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2) # Небольшие отступы
        layout.setSpacing(2)

        # Область вывода
        self.output_browser = QTextBrowser(self)
        self.output_browser.setReadOnly(True)
        # Устанавливаем политику размера для области вывода
        self.output_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_browser.setMinimumHeight(100)

        # Установим "терминальный" шрифт и темный фон
        font = QFont("Consolas", 10) # Или другой моноширинный
        self.output_browser.setFont(font)
        palette = self.output_browser.palette()
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        self.output_browser.setPalette(palette)
        self.output_browser.append("Welcome to GopiAI Terminal (simulation)!") # Приветствие

        # Заменяем однострочное поле ввода на многострочное
        self.input_line = QPlainTextEdit(self)
        self.input_line.setFont(font)
        # Увеличиваем высоту поля ввода
        self.input_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.input_line.setMinimumHeight(100)  # Было 28, увеличиваем примерно в 3.5 раза
        self.input_line.setMaximumHeight(200)  # Ограничиваем максимальную высоту

        self.input_line.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgb(45, 45, 45);
                color: rgb(220, 220, 220);
                border: 1px solid rgb(60, 60, 60);
                padding: 5px;
            }
        """)
        # Устанавливаем обработчик событий для Enter
        self.input_line.installEventFilter(self)

        layout.addWidget(self.output_browser, 1)  # Вес 1 - растягивается
        layout.addWidget(self.input_line, 0)      # Вес 0 - не растягивается

    def eventFilter(self, obj, event):
        """Фильтр событий для обработки нажатия Enter в поле ввода."""
        if obj is self.input_line and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key_Return and not key_event.modifiers() & Qt.ShiftModifier:
                # Enter без Shift выполняет команду
                self._process_command()
                return True
            elif key_event.key() == Qt.Key_Return and key_event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter добавляет новую строку
                return False
        return super().eventFilter(obj, event)

    def _connect_signals(self):
        # Убираем сигнал returnPressed, так как теперь используем eventFilter
        # self.input_line.returnPressed.connect(self._process_command)
        self.command_runner.finished.connect(self._on_command_output)

    def _process_command(self):
        command = self.input_line.toPlainText().strip()
        if command:
            # Выводим саму команду
            # TODO: Использовать реальный префикс (e.g., cwd)
            prompt_prefix = f"<font color='#8AE234'>$</font> <font color='white'>{command}</font>"
            self.output_browser.append(prompt_prefix)
            self.input_line.clear()

            # Блокируем ввод на время выполнения
            self.input_line.setEnabled(False)

            # Запускаем выполнение команды
            self.command_runner.run_command(command)

    def process_external_command(self, command: str):
        """
        Обработка команды, вызванной извне (например, из инструмента Terminal).
        Отображает команду в терминале без её фактического выполнения.

        Args:
            command: Команда для отображения
        """
        if command:
            # Отображаем команду как будто она была введена пользователем
            prompt_prefix = f"<font color='#8AE234'>$</font> <font color='white'>{command}</font>"
            self.output_browser.append(prompt_prefix)

            # Прокрутка вниз
            self.output_browser.verticalScrollBar().setValue(
                self.output_browser.verticalScrollBar().maximum()
            )

    def _on_command_output(self, stdout: str, stderr: str):
        """Обрабатывает вывод команды после ее завершения."""
        # Добавляем stdout, если он есть
        if stdout.strip():
            self.output_browser.append(stdout.strip())

        # Добавляем stderr, если он есть (другим цветом)
        if stderr.strip():
            self.output_browser.append(f'<font color="#FF6B68">{stderr.strip()}</font>')

        # Разблокируем ввод и возвращаем фокус
        self.input_line.setEnabled(True)
        self.input_line.setFocus()

        # Прокрутка вниз
        self.output_browser.verticalScrollBar().setValue(
            self.output_browser.verticalScrollBar().maximum()
        )

# Пример запуска
if __name__ == '__main__':
    app = QApplication(sys.argv)
    term = TerminalWidget()
    term.resize(600, 400)
    term.show()
    sys.exit(app.exec())
