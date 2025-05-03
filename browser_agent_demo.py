import sys
import asyncio
import signal
import platform
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QSplitter, QStatusBar
)
from PySide6.QtCore import Qt, QSize, QObject, Signal, Slot, QEvent
# Обновляем импорт QEventLoop с правильной версией
try:
    from qasync import QEventLoop
except ImportError:
    # Если qasync не доступен, пробуем альтернативный вариант
    from PySide6.QtCore import QEventLoop

from app.ui.browser_tab_widget import MultiBrowserWidget
from app.ui.browser_agent_interface import BrowserAgentInterface


class MainWindow(QMainWindow):
    """Главное окно демонстрационного приложения."""

    def __init__(self):
        super().__init__()

        # Настройки окна
        self.setWindowTitle("GopiAI - Демонстрация Браузерного Агента")
        self.setMinimumSize(1200, 800)

        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Основной layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Создаем разделитель для браузера и чата
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Создаем браузер
        self.browser_widget = MultiBrowserWidget()
        self.splitter.addWidget(self.browser_widget)

        # Создаем панель чата
        self.chat_panel = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_panel)

        # Заголовок чата
        self.chat_title = QLabel("Браузерный Агент")
        self.chat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        self.chat_layout.addWidget(self.chat_title)

        # История чата
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.chat_layout.addWidget(self.chat_history)

        # Панель ввода
        self.input_panel = QWidget()
        self.input_layout = QHBoxLayout(self.input_panel)
        self.input_layout.setContentsMargins(0, 0, 0, 0)

        # Поле ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите запрос для агента...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.input_layout.addWidget(self.input_field)

        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4c72b0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a5a8b;
            }
            QPushButton:pressed {
                background-color: #2c4565;
            }
        """)
        self.input_layout.addWidget(self.send_button)

        # Кнопка остановки
        self.stop_button = QPushButton("Остановить")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)
        self.input_layout.addWidget(self.stop_button)

        self.chat_layout.addWidget(self.input_panel)

        # Добавляем панель чата в сплиттер
        self.splitter.addWidget(self.chat_panel)

        # Устанавливаем начальные размеры сплиттера
        self.splitter.setSizes([800, 400])

        # Статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Готов к работе")
        self.status_bar.addWidget(self.status_label)

        # Создаем интерфейс для агента
        self.agent_interface = BrowserAgentInterface()
        self.agent_interface.set_browser_widget(self.browser_widget)

        # Подключаем сигналы
        self.connect_signals()

        # Открываем начальную страницу
        self.browser_widget.add_new_tab("https://www.google.com")

    def connect_signals(self):
        """Подключает сигналы и слоты."""
        # Сигналы UI
        self.send_button.clicked.connect(self.on_send_message)
        self.input_field.returnPressed.connect(self.on_send_message)
        self.stop_button.clicked.connect(self.on_stop_agent)

        # Сигналы агента
        self.agent_interface.agent_message.connect(self.on_agent_message)
        self.agent_interface.agent_error.connect(self.on_agent_error)
        self.agent_interface.agent_thinking.connect(self.on_agent_thinking)
        self.agent_interface.agent_finished.connect(self.on_agent_finished)

    @Slot()
    def on_send_message(self):
        """Обрабатывает отправку сообщения пользователем."""
        query = self.input_field.text().strip()
        if not query:
            return

        # Добавляем сообщение пользователя в историю
        self.chat_history.append(f"<b>Вы:</b> {query}")
        self.chat_history.append("")  # Пустая строка для разделения сообщений
        self.chat_history.ensureCursorVisible()

        # Очищаем поле ввода
        self.input_field.clear()

        # Отправляем запрос агенту
        self.agent_interface.process_user_query(query)

    @Slot(str)
    def on_agent_message(self, message):
        """Обрабатывает сообщение от агента."""
        self.chat_history.append(f"<b>Агент:</b> {message}")
        self.chat_history.append("")  # Пустая строка для разделения сообщений
        self.chat_history.ensureCursorVisible()

    @Slot(str)
    def on_agent_error(self, error):
        """Обрабатывает сообщение об ошибке от агента."""
        self.chat_history.append(f"<span style='color: red;'><b>Ошибка:</b> {error}</span>")
        self.chat_history.append("")  # Пустая строка для разделения сообщений
        self.chat_history.ensureCursorVisible()
        self.status_label.setText("Ошибка")

    @Slot(bool)
    def on_agent_thinking(self, is_thinking):
        """Обрабатывает изменение состояния обработки запроса агентом."""
        if is_thinking:
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Агент обрабатывает запрос...")
        else:
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    @Slot()
    def on_agent_finished(self):
        """Обрабатывает завершение работы агента."""
        self.status_label.setText("Готов к работе")

    @Slot()
    def on_stop_agent(self):
        """Останавливает работу агента."""
        self.agent_interface.stop_agent()

    async def cleanup(self):
        """Очищает ресурсы перед закрытием приложения."""
        # Очищаем ресурсы агента
        await self.agent_interface.cleanup()

    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна."""
        # Создаем событие для очистки ресурсов
        asyncio.create_task(self.cleanup())
        # Принимаем событие закрытия
        event.accept()


async def main():
    """Основная функция для запуска приложения."""
    # Создаем приложение
    app = QApplication(sys.argv)

    # Создаем event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Обработка сигнала прерывания (Ctrl+C) только для POSIX-систем
    if hasattr(signal, 'SIGINT') and platform.system() != "Windows":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем event loop - исправляем проблему с await
    with loop:
        loop.run_forever()  # Убираем await, так как run_forever() не является корутиной


async def shutdown(loop):
    """Корректно завершает работу приложения."""
    # Останавливаем все задачи
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    asyncio.run(main())
