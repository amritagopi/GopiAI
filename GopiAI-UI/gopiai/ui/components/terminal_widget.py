"""
Terminal Widget Component для GopiAI Standalone Interface
======================================================

Интерактивный виджет терминала с вкладками и поддержкой выполнения команд.
Исправлена проблема с созданием терминала в отдельных окнах - теперь терминал
создается только в вкладках основного интерфейса.
"""

import subprocess
import threading
import os
import sys
import weakref
from typing import Optional, cast, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit, QLineEdit
from PySide6.QtCore import QTimer, Signal, Qt, QProcess
from PySide6.QtGui import QTextCursor, QFont, QKeyEvent
import logging

logger = logging.getLogger(__name__)
# Импорт ansi2html с fallback
try:
    from ansi2html import Ansi2HTMLConverter
    ANSI2HTML_AVAILABLE = True
except ImportError:
    print("⚠️ ansi2html недоступен, используем fallback")
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
    """Интерактивный терминал с поддержкой ввода команд"""
    
    command_executed = Signal(str)  # Сигнал для выполненной команды
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt = '> '
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
        # Инициализация процесса с обработкой ошибок
        self.process = None
        self._init_process()
        
        # Добавляем приветственное сообщение
        self.append("GopiAI Terminal - готов к работе")
        self.append("Введите команду и нажмите Enter для выполнения")
        self.insertPlainText(self.prompt)
        self._scroll_to_bottom()
        
    def _init_process(self):
        """Инициализация процесса терминала с обработкой ошибок"""
        try:
            self.process = QProcess(self)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.handle_finished)
            
            # Определяем команду для запуска в зависимости от ОС
            if os.name == 'nt':  # Windows
                self.process.start("cmd.exe")
            else:  # Unix-like systems
                self.process.start("/bin/bash")
                
            logger.info("Процесс терминала инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации процесса терминала: {e}")
            self.append(f"Ошибка инициализации терминала: {e}")
            self.append("Терминал работает в ограниченном режиме")

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш с улучшенной логикой"""
        if event.key() == Qt.Key_Return: # type: ignore[attr-defined]
            try:
                # Получаем текущую команду
                full_text = self.toPlainText()
                last_prompt_pos = full_text.rfind(self.prompt)
                
                if last_prompt_pos != -1:
                    command = full_text[last_prompt_pos + len(self.prompt):].strip()
                    
                    if command:
                        self.execute_command(command)
                    else:
                        self.insertPlainText('\n' + self.prompt)
                        self._scroll_to_bottom()
                else:
                    self.insertPlainText('\n' + self.prompt)
                    self._scroll_to_bottom()
                    
            except Exception as e:
                logger.error(f"Ошибка обработки команды: {e}")
                self.append(f"Ошибка: {e}")
                self.insertPlainText(self.prompt)
                self._scroll_to_bottom()
        else:
            super().keyPressEvent(event)
            
    def execute_command(self, command: str):
        """Выполнение команды с улучшенной обработкой ошибок"""
        try:
            if not self.process or self.process.state() != QProcess.ProcessState.Running:
                self._init_process()
                
            if self.process and self.process.state() == QProcess.ProcessState.Running:
                self.insertPlainText('\n')
                self.process.write(command.encode() + b'\n')
                self.command_executed.emit(command)
                logger.debug(f"Выполнена команда: {command}")
            else:
                self.append("Ошибка: процесс терминала не запущен")
                self.insertPlainText(self.prompt)
                self._scroll_to_bottom()
                
        except Exception as e:
            logger.error(f"Ошибка выполнения команды '{command}': {e}")
            self.append(f"Ошибка выполнения команды: {e}")
            self.insertPlainText(self.prompt)
            self._scroll_to_bottom()

    def handle_stdout(self):
        """Обработка стандартного вывода с улучшенным декодированием"""
        try:
            if not self.process:
                return
                
            data = bytes(self.process.readAllStandardOutput().data())
            
            # Пытаемся декодировать с разными кодировками
            text = self._decode_output(data)
            
            if text:
                converter = Ansi2HTMLConverter()
                html = converter.convert(text, full=False)
                self.insertHtml(html)
                self.insertPlainText(self.prompt)
                self._scroll_to_bottom()
                
        except Exception as e:
            logger.error(f"Ошибка обработки stdout: {e}")

    def handle_stderr(self):
        """Обработка стандартного вывода ошибок"""
        try:
            if not self.process:
                return
                
            data = bytes(self.process.readAllStandardError().data())
            text = self._decode_output(data)
            
            if text:
                converter = Ansi2HTMLConverter()
                html = converter.convert(text, full=False)
                self.insertHtml(f'<font color="#ff6b6b">{html}</font>')
                self.insertPlainText(self.prompt)
                self._scroll_to_bottom()
                
        except Exception as e:
            logger.error(f"Ошибка обработки stderr: {e}")

    def handle_state(self, state):
        """Обработка изменения состояния процесса"""
        try:
            if state == QProcess.ProcessState.Running:
                logger.debug("Процесс терминала запущен")
            elif state == QProcess.ProcessState.NotRunning:
                logger.warning("Процесс терминала остановлен")
                self.append("Процесс терминала завершен")
                self.insertPlainText(self.prompt)
                self._scroll_to_bottom()
        except Exception as e:
            logger.error(f"Ошибка обработки состояния процесса: {e}")
            
    def handle_finished(self, exit_code, exit_status):
        """Обработка завершения процесса"""
        try:
            logger.info(f"Процесс терминала завершен с кодом {exit_code}")
            self.append(f"Процесс завершен (код: {exit_code})")
            self.insertPlainText(self.prompt)
            self._scroll_to_bottom()
        except Exception as e:
            logger.error(f"Ошибка обработки завершения процесса: {e}")
            
    def _decode_output(self, data: bytes) -> str:
        """Декодирование вывода с попыткой разных кодировок"""
        encodings = ['utf-8', 'cp866', 'cp1251', 'latin-1']
        
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
                
        # Если ничего не сработало, используем замену ошибочных символов
        return data.decode('utf-8', errors='replace')

    def _scroll_to_bottom(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class TerminalWidget(QWidget):
    """Виджет терминала с вкладками - исправлен для работы только в основном интерфейсе"""
    
    # Singleton для глобального доступа
    instance = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Устанавливаем singleton
        TerminalWidget.instance = self
        
        # Словарь для хранения ссылок на терминалы
        self._terminal_references: Dict[int, InteractiveTerminal] = {}
        
        self._setup_ui()
        
        # Создаем первую вкладку терминала
        self.add_tab()
        
        logger.info("TerminalWidget инициализирован")
        
    def _setup_ui(self):
        """Настройка интерфейса терминала"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Заголовок и кнопки управления
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🖥️ Терминал")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Кнопка добавления новой вкладки
        add_tab_btn = QPushButton("➕ Новая вкладка")
        add_tab_btn.setToolTip("Создать новую вкладку терминала")
        add_tab_btn.clicked.connect(self.add_tab)
        add_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(add_tab_btn)
        
        layout.addLayout(header_layout)
        
        # Виджет вкладок терминала
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        
        layout.addWidget(self.tabs)

    def add_tab(self, title: str = None) -> int:
        """Добавление новой вкладки терминала"""
        try:
            terminal = InteractiveTerminal(self)
            
            if title is None:
                title = f"Терминал {self.tabs.count() + 1}"
                
            # Сохраняем ссылку на терминал
            terminal_id = id(terminal)
            self._terminal_references[terminal_id] = terminal
            
            index = self.tabs.addTab(terminal, title)
            self.tabs.setCurrentIndex(index)
            
            logger.info(f"Добавлена вкладка терминала: {title}")
            return index
            
        except Exception as e:
            logger.error(f"Ошибка создания вкладки терминала: {e}")
            return -1

    def close_tab(self, index: int):
        """Закрытие вкладки терминала"""
        try:
            if self.tabs.count() > 1 and 0 <= index < self.tabs.count():
                # Получаем терминал перед закрытием
                terminal = cast(InteractiveTerminal, self.tabs.widget(index))
                
                if terminal:
                    # Завершаем процесс терминала
                    if terminal.process and terminal.process.state() == QProcess.ProcessState.Running:
                        terminal.process.kill()
                        terminal.process.waitForFinished(3000)  # Ждем 3 секунды
                    
                    # Удаляем ссылку
                    terminal_id = id(terminal)
                    if terminal_id in self._terminal_references:
                        del self._terminal_references[terminal_id]
                
                self.tabs.removeTab(index)
                logger.info(f"Закрыта вкладка терминала с индексом {index}")
            else:
                logger.warning("Нельзя закрыть последнюю вкладку терминала")
                
        except Exception as e:
            logger.error(f"Ошибка закрытия вкладки терминала: {e}")

    def execute_command(self, command: str, tab_index: int = -1):
        """Выполнение команды в указанной вкладке терминала"""
        try:
            if tab_index == -1:
                tab_index = self.tabs.currentIndex()
                
            if 0 <= tab_index < self.tabs.count():
                terminal = cast(InteractiveTerminal, self.tabs.widget(tab_index))
                if terminal:
                    terminal.execute_command(command)
                    logger.debug(f"Команда '{command}' отправлена в терминал {tab_index}")
                else:
                    logger.error(f"Терминал не найден в вкладке {tab_index}")
            else:
                logger.error(f"Неверный индекс вкладки: {tab_index}")
                
        except Exception as e:
            logger.error(f"Ошибка выполнения команды '{command}': {e}")

    def log_ai_command(self, command: str, output: str):
        """Логирование команды AI в текущем терминале"""
        try:
            current_terminal = cast(InteractiveTerminal, self.tabs.currentWidget())
            if current_terminal:
                current_terminal.append(f'\n[🤖 AI] Выполнена команда: {command}')
                if output:
                    current_terminal.append(f'Результат:\n{output}')
                current_terminal.insertPlainText(current_terminal.prompt)
                current_terminal._scroll_to_bottom()
                logger.debug(f"Залогирована AI команда: {command}")
            else:
                logger.warning("Текущий терминал не найден для логирования AI команды")
                
        except Exception as e:
            logger.error(f"Ошибка логирования AI команды: {e}")
            
    def get_current_terminal(self) -> Optional[InteractiveTerminal]:
        """Получение текущего активного терминала"""
        try:
            return cast(InteractiveTerminal, self.tabs.currentWidget())
        except Exception as e:
            logger.error(f"Ошибка получения текущего терминала: {e}")
            return None
            
    def cleanup(self):
        """Очистка ресурсов при закрытии"""
        try:
            # Завершаем все процессы терминалов
            for i in range(self.tabs.count()):
                terminal = cast(InteractiveTerminal, self.tabs.widget(i))
                if terminal and terminal.process:
                    if terminal.process.state() == QProcess.ProcessState.Running:
                        terminal.process.kill()
                        terminal.process.waitForFinished(1000)
                        
            # Очищаем ссылки
            self._terminal_references.clear()
            logger.info("Ресурсы TerminalWidget очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов TerminalWidget: {e}")


# Глобальные функции для совместимости
def get_terminal_widget() -> Optional[TerminalWidget]:
    """Получение глобального экземпляра TerminalWidget"""
    return TerminalWidget.instance


def set_terminal_widget(terminal_widget: TerminalWidget):
    """Установка глобального экземпляра TerminalWidget"""
    TerminalWidget.instance = terminal_widget
    logger.info("Установлен глобальный экземпляр TerminalWidget")
