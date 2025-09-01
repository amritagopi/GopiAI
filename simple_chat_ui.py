#!/usr/bin/env python3
"""
Простой чат UI для общения с CrewAI API
Минимальная версия для тестирования всех основных функций
"""

import sys
import os
import json
import base64
import requests
import threading
import time
from pathlib import Path
from typing import Optional

# Подавляем предупреждения Qt
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox, QFileDialog,
    QTabWidget, QListWidget, QSplitter, QFrame, QScrollArea,
    QMessageBox, QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap

class APIWorker(QThread):
    """Рабочий поток для API запросов"""
    response_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, message: str, files: list = None):
        super().__init__()
        self.message = message
        self.files = files or []
        
    def run(self):
        try:
            # Подготовка данных
            payload = {"message": self.message}
            
            # Добавляем файлы как base64 если есть
            if self.files:
                files_data = []
                for file_path in self.files:
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            encoded = base64.b64encode(content).decode('utf-8')
                            files_data.append({
                                "name": os.path.basename(file_path),
                                "content": encoded,
                                "type": self._detect_file_type(file_path)
                            })
                    except Exception as e:
                        self.error_occurred.emit(f"Ошибка чтения файла {file_path}: {e}")
                        return
                payload["files"] = files_data
            
            # Отправка запроса
            response = requests.post(
                "http://127.0.0.1:5052/api/process",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 202:
                task_data = response.json()
                task_id = task_data.get('task_id')
                
                # Ожидание результата
                for _ in range(60):  # 60 секунд максимум
                    time.sleep(1)
                    status_response = requests.get(
                        f"http://127.0.0.1:5052/api/task/{task_id}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        task_result = status_response.json()
                        if task_result.get('status') == 'completed':
                            self.response_ready.emit(task_result)
                            return
                        elif task_result.get('status') == 'failed':
                            self.error_occurred.emit(task_result.get('error', 'Неизвестная ошибка'))
                            return
                
                self.error_occurred.emit("Таймаут ожидания ответа")
            else:
                self.error_occurred.emit(f"Ошибка API: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _detect_file_type(self, file_path: str) -> str:
        """Определение типа файла"""
        ext = Path(file_path).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return 'image'
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            return 'text'
        elif ext in ['.pdf']:
            return 'pdf'
        else:
            return 'binary'

class ChatWidget(QWidget):
    """Виджет чата"""
    
    def __init__(self):
        super().__init__()
        self.current_worker = None
        self.attached_files = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # История чата
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        layout.addWidget(self.chat_display)
        
        # Прикрепленные файлы
        files_frame = QFrame()
        files_layout = QVBoxLayout(files_frame)
        files_layout.setContentsMargins(5, 5, 5, 5)
        
        self.files_label = QLabel("Прикрепленные файлы: нет")
        files_layout.addWidget(self.files_label)
        
        files_buttons_layout = QHBoxLayout()
        self.attach_button = QPushButton("📎 Прикрепить файл")
        self.attach_button.clicked.connect(self.attach_file)
        self.clear_files_button = QPushButton("🗑️ Очистить")
        self.clear_files_button.clicked.connect(self.clear_files)
        
        files_buttons_layout.addWidget(self.attach_button)
        files_buttons_layout.addWidget(self.clear_files_button)
        files_buttons_layout.addStretch()
        files_layout.addLayout(files_buttons_layout)
        
        layout.addWidget(files_frame)
        
        # Ввод сообщения
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # Добавляем приветственное сообщение
        self.add_message("System", "Чат готов к работе! Подключен к API серверу на порту 5052.")
    
    def attach_file(self):
        """Прикрепить файл"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", 
            "Все файлы (*);;Изображения (*.png *.jpg *.jpeg *.gif);;Текстовые файлы (*.txt *.md *.py)"
        )
        
        if file_path:
            self.attached_files.append(file_path)
            self.update_files_display()
    
    def clear_files(self):
        """Очистить прикрепленные файлы"""
        self.attached_files.clear()
        self.update_files_display()
    
    def update_files_display(self):
        """Обновить отображение файлов"""
        if self.attached_files:
            files_names = [os.path.basename(f) for f in self.attached_files]
            self.files_label.setText(f"Прикрепленные файлы ({len(files_names)}): {', '.join(files_names)}")
        else:
            self.files_label.setText("Прикрепленные файлы: нет")
    
    def add_message(self, sender: str, message: str):
        """Добавить сообщение в чат"""
        timestamp = time.strftime("%H:%M:%S")
        self.chat_display.append(f"<b>[{timestamp}] {sender}:</b><br>{message}<br>")
    
    def send_message(self):
        """Отправить сообщение"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Блокируем интерфейс
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.attach_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Бесконечная прогресс-бар
        
        # Добавляем сообщение пользователя
        files_info = f" (с файлами: {len(self.attached_files)})" if self.attached_files else ""
        self.add_message("Вы", message + files_info)
        
        # Очищаем поле ввода
        self.message_input.clear()
        
        # Запускаем рабочий поток
        self.current_worker = APIWorker(message, self.attached_files.copy())
        self.current_worker.response_ready.connect(self.handle_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.start()
        
        # Очищаем файлы после отправки
        self.clear_files()
    
    def handle_response(self, response_data: dict):
        """Обработка ответа от API"""
        result = response_data.get('result', 'Нет ответа')
        self.add_message("AI", result)
        self.reset_ui()
    
    def handle_error(self, error_message: str):
        """Обработка ошибки"""
        self.add_message("Ошибка", f"❌ {error_message}")
        self.reset_ui()
    
    def reset_ui(self):
        """Сброс состояния UI"""
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.attach_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.current_worker = None

class ModelSelector(QWidget):
    """Виджет выбора модели"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🤖 Выбор модели AI")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Выбор провайдера
        provider_group = QGroupBox("Провайдер")
        provider_layout = QVBoxLayout()
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "OpenRouter",
            "OpenAI", 
            "Gemini",
            "Claude"
        ])
        provider_layout.addWidget(self.provider_combo)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Выбор модели
        model_group = QGroupBox("Модель")
        model_layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        self.update_models()
        model_layout.addWidget(self.model_combo)
        
        # Кнопка обновления списка моделей
        refresh_button = QPushButton("🔄 Обновить список")
        refresh_button.clicked.connect(self.update_models)
        model_layout.addWidget(refresh_button)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Применить настройки
        apply_button = QPushButton("✅ Применить настройки")
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Подключаем изменение провайдера к обновлению моделей
        self.provider_combo.currentTextChanged.connect(self.update_models)
    
    def update_models(self):
        """Обновить список моделей"""
        provider = self.provider_combo.currentText()
        
        if provider == "OpenRouter":
            self.load_openrouter_models()
        else:
            # Заглушка для других провайдеров
            models_map = {
                "OpenAI": [
                    "gpt-4", 
                    "gpt-4-turbo",
                    "gpt-3.5-turbo"
                ],
                "Gemini": [
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ],
                "Claude": [
                    "claude-3-opus",
                    "claude-3-sonnet", 
                    "claude-3-haiku"
                ]
            }
            
            self.model_combo.clear()
            self.model_combo.addItems(models_map.get(provider, ["Модель не найдена"]))
    
    def load_openrouter_models(self):
        """Загрузить модели OpenRouter через API"""
        try:
            response = requests.get("http://127.0.0.1:5052/api/models/openrouter", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                self.model_combo.clear()
                for model in models:
                    # Показываем удобочитаемое имя, но сохраняем ID
                    display_name = f"{model['name']} ({model['id']})"
                    self.model_combo.addItem(display_name, model['id'])
            else:
                self.model_combo.clear()
                self.model_combo.addItem("❌ Ошибка загрузки моделей")
        except Exception as e:
            self.model_combo.clear()
            self.model_combo.addItem(f"❌ Ошибка: {str(e)}")
    
    def apply_settings(self):
        """Применить настройки модели"""
        provider = self.provider_combo.currentText()
        model = self.model_combo.currentText()
        model_id = self.model_combo.currentData()  # Получаем ID модели
        
        if not model_id:
            model_id = model  # Если нет ID, используем текст
        
        try:
            payload = {
                "provider": provider,
                "model": model_id
            }
            
            response = requests.post(
                "http://127.0.0.1:5052/api/model/set",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                QMessageBox.information(
                    self, 
                    "✅ Настройки применены", 
                    f"Модель успешно установлена:\n{result.get('message', 'Настройки сохранены')}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "❌ Ошибка",
                    f"Не удалось применить настройки.\nКод ошибки: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Ошибка подключения",
                f"Не удалось подключиться к серверу:\n{str(e)}"
            )

class AgentsTab(QWidget):
    """Вкладка управления агентами"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("👥 Управление CrewAI агентами")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Список агентов
        agents_group = QGroupBox("Доступные агенты")
        agents_layout = QVBoxLayout()
        
        self.agents_list = QListWidget()
        self.agents_list.addItem("🤖 General Purpose Assistant")
        self.agents_list.addItem("📝 Text Writer") 
        self.agents_list.addItem("💻 Code Assistant")
        self.agents_list.addItem("🔍 Research Agent")
        agents_layout.addWidget(self.agents_list)
        
        agents_group.setLayout(agents_layout)
        layout.addWidget(agents_group)
        
        # Управление агентами
        controls_group = QGroupBox("Управление")
        controls_layout = QHBoxLayout()
        
        create_button = QPushButton("➕ Создать агента")
        edit_button = QPushButton("✏️ Редактировать")
        delete_button = QPushButton("🗑️ Удалить")
        
        create_button.clicked.connect(self.create_agent)
        edit_button.clicked.connect(self.edit_agent)
        delete_button.clicked.connect(self.delete_agent)
        
        controls_layout.addWidget(create_button)
        controls_layout.addWidget(edit_button)
        controls_layout.addWidget(delete_button)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_agent(self):
        QMessageBox.information(self, "Создание агента", "Функция создания агента пока не реализована")
    
    def edit_agent(self):
        QMessageBox.information(self, "Редактирование", "Функция редактирования агента пока не реализована")
    
    def delete_agent(self):
        QMessageBox.information(self, "Удаление", "Функция удаления агента пока не реализована")

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.check_api_connection()
    
    def init_ui(self):
        self.setWindowTitle("GopiAI Chat - Простой UI для общения с AI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет с вкладками
        central_widget = QTabWidget()
        
        # Вкладка чата
        self.chat_widget = ChatWidget()
        central_widget.addTab(self.chat_widget, "💬 Чат")
        
        # Вкладка выбора модели
        self.model_selector = ModelSelector()
        central_widget.addTab(self.model_selector, "🤖 Модели")
        
        # Вкладка агентов
        self.agents_tab = AgentsTab()
        central_widget.addTab(self.agents_tab, "👥 Агенты")
        
        self.setCentralWidget(central_widget)
        
        # Статус бар
        self.statusBar().showMessage("Готово к работе")
        
    def check_api_connection(self):
        """Проверить подключение к API"""
        try:
            response = requests.get("http://127.0.0.1:5052/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                server_type = data.get('server', 'unknown')
                self.statusBar().showMessage(f"✅ Подключено к API серверу ({server_type})")
            else:
                self.statusBar().showMessage(f"⚠️ API сервер недоступен (код {response.status_code})")
        except Exception as e:
            self.statusBar().showMessage(f"❌ Нет подключения к API серверу: {e}")

def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("GopiAI Simple Chat")
    
    # Проверяем подключение к серверу
    try:
        response = requests.get("http://127.0.0.1:5052/api/health", timeout=2)
        if response.status_code != 200:
            QMessageBox.critical(None, "Ошибка", "API сервер не доступен!\nЗапустите сервер на порту 5052.")
            return 1
    except Exception as e:
        QMessageBox.critical(None, "Ошибка подключения", f"Не удается подключиться к API серверу:\n{e}\n\nУбедитесь, что сервер запущен на порту 5052.")
        return 1
    
    # Создаем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем приложение
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())