"""
Компонент мониторинга выполнения задач CrewAI
Отображает статус выполнения команд в реальном времени
"""

import logging
from typing import Dict, List
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel, QProgressBar, QTextEdit, QTabWidget, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal
from PySide6.QtGui import QFont
import requests
from gopiai.ui.utils.icon_helpers import create_icon_button

logger = logging.getLogger(__name__)

class TaskStatus:
    """Статусы задач"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskMonitorWorker(QThread):
    """Воркер для периодического опроса статуса задач"""
    
    tasks_updated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_base: str, refresh_interval: int = 5):
        super().__init__()
        self.api_base = api_base
        self.refresh_interval = refresh_interval
        self.running = False
    
    def run(self):
        """Основной цикл мониторинга"""
        self.running = True
        while self.running:
            try:
                # Получаем список задач
                response = requests.get(f"{self.api_base}/api/tasks", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    tasks = data.get('tasks', [])
                    self.tasks_updated.emit(tasks)
                else:
                    self.error_occurred.emit(f"Ошибка HTTP: {response.status_code}")
                    
            except requests.RequestException as e:
                self.error_occurred.emit(f"Ошибка сети: {str(e)}")
            except Exception as e:
                self.error_occurred.emit(f"Неожиданная ошибка: {str(e)}")
            
            # Ждем перед следующим обновлением
            self.msleep(self.refresh_interval * 1000)
    
    def stop(self):
        """Остановка мониторинга"""
        self.running = False
        self.quit()
        self.wait()

class TaskItemWidget(QWidget):
    """Виджет отображения отдельной задачи"""
    
    task_selected = Signal(str)  # task_id
    
    def __init__(self, task_data: Dict, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Заголовок задачи
        header_layout = QHBoxLayout()
        
        # ID задачи (кликабельный)
        self.task_id_label = QPushButton(f"#{self.task_data.get('task_id', '')[:8]}")
        self.task_id_label.setFlat(True)
        self.task_id_label.setStyleSheet("text-align: left; font-weight: bold;")
        self.task_id_label.clicked.connect(self._on_task_clicked)
        header_layout.addWidget(self.task_id_label)
        
        header_layout.addStretch()
        
        # Статус
        self.status_label = QLabel()
        header_layout.addWidget(self.status_label)
        
        # Время создания
        created_at = self.task_data.get('created_at', 0)
        if created_at:
            created_time = datetime.fromtimestamp(created_at)
            time_str = created_time.strftime("%H:%M:%S")
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: gray; font-size: 12px;")
            header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(6)
        layout.addWidget(self.progress_bar)
        
        # Описание прогресса
        self.progress_label = QLabel()
        self.progress_label.setWordWrap(True)
        self.progress_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.progress_label)
    
    def _update_display(self):
        """Обновляет отображение данных задачи"""
        status = self.task_data.get('status', TaskStatus.PENDING)
        
        # Обновляем статус
        self.status_label.setText(status.upper())
        self._set_status_color(status)
        
        # Обновляем прогресс
        progress_text = self.task_data.get('progress', '')
        self.progress_label.setText(progress_text)
        
        # Обновляем прогресс бар
        if status == TaskStatus.PENDING:
            self.progress_bar.setValue(0)
        elif status == TaskStatus.RUNNING:
            self.progress_bar.setRange(0, 0)  # Индетерминированный
        elif status == TaskStatus.COMPLETED:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
        elif status == TaskStatus.FAILED:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
    
    def _set_status_color(self, status: str):
        """Устанавливает цвет статуса"""
        colors = {
            TaskStatus.PENDING: "#f39c12",     # Оранжевый
            TaskStatus.RUNNING: "#3498db",     # Синий  
            TaskStatus.COMPLETED: "#2ecc71",   # Зеленый
            TaskStatus.FAILED: "#e74c3c",      # Красный
            TaskStatus.CANCELLED: "#95a5a6"    # Серый
        }
        
        color = colors.get(status, "#95a5a6")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _on_task_clicked(self):
        """Обрабатывает клик по задаче"""
        task_id = self.task_data.get('task_id', '')
        self.task_selected.emit(task_id)
    
    def update_task_data(self, new_data: Dict):
        """Обновляет данные задачи"""
        self.task_data = new_data
        self._update_display()

class TaskDetailsWidget(QWidget):
    """Виджет с детальной информацией о задаче"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_task_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Выберите задачу для просмотра деталей")
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Кнопка обновления
        self.refresh_btn = create_icon_button("refresh-cw", "Обновить детали")
        self.refresh_btn.clicked.connect(self._refresh_details)
        self.refresh_btn.setEnabled(False)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Табы с деталями
        self.tabs = QTabWidget()
        
        # Таб основной информации
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        self.tabs.addTab(info_widget, "Информация")
        
        # Таб результата
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        self.tabs.addTab(result_widget, "Результат")
        
        # Таб логов
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("font-family: 'Courier New', monospace;")
        logs_layout.addWidget(self.logs_text)
        
        self.tabs.addTab(logs_widget, "Логи")
        
        layout.addWidget(self.tabs)
    
    def show_task_details(self, task_id: str, api_base: str):
        """Показывает детали задачи"""
        self.current_task_id = task_id
        self.refresh_btn.setEnabled(True)
        
        try:
            # Получаем детальную информацию о задаче
            response = requests.get(f"{api_base}/api/tasks/{task_id}", timeout=10)
            
            if response.status_code == 200:
                task_data = response.json()
                self._display_task_data(task_data)
            else:
                self._show_error(f"Ошибка получения деталей: {response.status_code}")
                
        except requests.RequestException as e:
            self._show_error(f"Ошибка сети: {str(e)}")
        except Exception as e:
            self._show_error(f"Неожиданная ошибка: {str(e)}")
    
    def _display_task_data(self, task_data: Dict):
        """Отображает данные задачи в интерфейсе"""
        task_id = task_data.get('task_id', 'Неизвестно')
        self.title_label.setText(f"Задача: {task_id[:12]}...")
        
        # Основная информация
        info_parts = []
        info_parts.append(f"ID: {task_id}")
        info_parts.append(f"Статус: {task_data.get('status', 'Неизвестно')}")
        
        created_at = task_data.get('created_at')
        if created_at:
            created_time = datetime.fromtimestamp(created_at)
            info_parts.append(f"Создано: {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        completed_at = task_data.get('completed_at')
        if completed_at:
            completed_time = datetime.fromtimestamp(completed_at)
            info_parts.append(f"Завершено: {completed_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Время выполнения
            if created_at:
                duration = completed_at - created_at
                info_parts.append(f"Время выполнения: {duration:.2f} сек")
        
        progress = task_data.get('progress')
        if progress:
            info_parts.append(f"Прогресс: {progress}")
        
        error = task_data.get('error')
        if error:
            info_parts.append(f"Ошибка: {error}")
        
        self.info_text.setPlainText('\n'.join(info_parts))
        
        # Результат
        result = task_data.get('result', 'Результат пока недоступен')
        self.result_text.setPlainText(result)
        
        # Логи (если есть)
        logs = task_data.get('logs', 'Логи недоступны')
        self.logs_text.setPlainText(logs)
    
    def _show_error(self, error_msg: str):
        """Показывает ошибку"""
        self.info_text.setPlainText(f"Ошибка: {error_msg}")
        self.result_text.setPlainText("")
        self.logs_text.setPlainText("")
    
    def _refresh_details(self):
        """Обновляет детали текущей задачи"""
        if self.current_task_id:
            from gopiai.ui.utils.network import get_crewai_server_base_url
            api_base = get_crewai_server_base_url()
            self.show_task_details(self.current_task_id, api_base)

class TaskMonitorTab(QWidget):
    """Вкладка мониторинга задач CrewAI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from gopiai.ui.utils.network import get_crewai_server_base_url
        self.api_base = get_crewai_server_base_url()
        
        self.tasks_data = []
        self.task_widgets = {}  # task_id -> TaskItemWidget
        self.monitor_worker = None
        
        self._setup_ui()
        self._start_monitoring()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок и управление
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Мониторинг задач")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Статистика
        self.stats_label = QLabel("Загрузка...")
        header_layout.addWidget(self.stats_label)
        
        # Кнопки управления
        self.pause_btn = create_icon_button("pause", "Приостановить мониторинг")
        self.pause_btn.clicked.connect(self._toggle_monitoring)
        header_layout.addWidget(self.pause_btn)
        
        refresh_btn = create_icon_button("refresh-cw", "Обновить сейчас")
        refresh_btn.clicked.connect(self._refresh_tasks)
        header_layout.addWidget(refresh_btn)
        
        clear_btn = create_icon_button("trash-2", "Очистить завершенные")
        clear_btn.clicked.connect(self._clear_completed_tasks)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Основной контент
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - список задач
        tasks_widget = self._create_tasks_panel()
        splitter.addWidget(tasks_widget)
        
        # Правая панель - детали
        self.details_widget = TaskDetailsWidget()
        splitter.addWidget(self.details_widget)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
    
    def _create_tasks_panel(self):
        """Создает панель со списком задач"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        
        all_btn = QPushButton("Все")
        all_btn.setCheckable(True)
        all_btn.setChecked(True)
        all_btn.clicked.connect(lambda: self._filter_tasks("all"))
        filters_layout.addWidget(all_btn)
        
        running_btn = QPushButton("Выполняются")
        running_btn.setCheckable(True)
        running_btn.clicked.connect(lambda: self._filter_tasks("running"))
        filters_layout.addWidget(running_btn)
        
        completed_btn = QPushButton("Завершенные")
        completed_btn.setCheckable(True)
        completed_btn.clicked.connect(lambda: self._filter_tasks("completed"))
        filters_layout.addWidget(completed_btn)
        
        failed_btn = QPushButton("Ошибки")
        failed_btn.setCheckable(True)  
        failed_btn.clicked.connect(lambda: self._filter_tasks("failed"))
        filters_layout.addWidget(failed_btn)
        
        layout.addLayout(filters_layout)
        
        # Скролл-область для задач
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(4)
        
        scroll_area.setWidget(self.tasks_container)
        layout.addWidget(scroll_area)
        
        return widget
    
    def _start_monitoring(self):
        """Запускает мониторинг задач"""
        if self.monitor_worker is None:
            self.monitor_worker = TaskMonitorWorker(self.api_base)
            self.monitor_worker.tasks_updated.connect(self._update_tasks)
            self.monitor_worker.error_occurred.connect(self._show_error)
            self.monitor_worker.start()
    
    def _stop_monitoring(self):
        """Останавливает мониторинг"""
        if self.monitor_worker:
            self.monitor_worker.stop()
            self.monitor_worker = None
    
    def _toggle_monitoring(self):
        """Переключает состояние мониторинга"""
        if self.monitor_worker and self.monitor_worker.running:
            self._stop_monitoring()
            self.pause_btn.setToolTip("Возобновить мониторинг")
            # Обновляем иконку на play
        else:
            self._start_monitoring()
            self.pause_btn.setToolTip("Приостановить мониторинг")
            # Обновляем иконку на pause
    
    def _update_tasks(self, tasks: List[Dict]):
        """Обновляет список задач"""
        self.tasks_data = tasks
        
        # Обновляем статистику
        total = len(tasks)
        running = len([t for t in tasks if t.get('status') == TaskStatus.RUNNING])
        completed = len([t for t in tasks if t.get('status') == TaskStatus.COMPLETED])
        failed = len([t for t in tasks if t.get('status') == TaskStatus.FAILED])
        
        self.stats_label.setText(f"Всего: {total} | Выполняется: {running} | Завершено: {completed} | Ошибки: {failed}")
        
        # Обновляем виджеты задач
        self._render_tasks()
    
    def _render_tasks(self):
        """Отображает задачи в интерфейсе"""
        # Удаляем старые виджеты
        for widget in self.task_widgets.values():
            widget.setParent(None)
        self.task_widgets.clear()
        
        # Сортируем задачи по времени создания (новые сверху)
        sorted_tasks = sorted(self.tasks_data, key=lambda t: t.get('created_at', 0), reverse=True)
        
        # Создаем виджеты для задач
        for task_data in sorted_tasks:
            task_id = task_data.get('task_id', '')
            
            task_widget = TaskItemWidget(task_data)
            task_widget.task_selected.connect(self._on_task_selected)
            
            self.task_widgets[task_id] = task_widget
            self.tasks_layout.addWidget(task_widget)
        
        # Добавляем растягивающийся элемент
        self.tasks_layout.addStretch()
    
    def _on_task_selected(self, task_id: str):
        """Обрабатывает выбор задачи"""
        logger.info(f"Выбрана задача: {task_id}")
        self.details_widget.show_task_details(task_id, self.api_base)
    
    def _filter_tasks(self, filter_type: str):
        """Фильтрует задачи по типу"""
        # TODO: Реализовать фильтрацию
        logger.info(f"Применен фильтр: {filter_type}")
    
    def _refresh_tasks(self):
        """Обновляет задачи вручную"""
        if self.monitor_worker:
            # Форсируем обновление
            pass
    
    def _clear_completed_tasks(self):
        """Очищает завершенные задачи"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить все завершенные и неуспешные задачи?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Отправить запрос на сервер для удаления
            logger.info("Запрос на очистку завершенных задач")
    
    def _show_error(self, error_msg: str):
        """Показывает ошибку мониторинга"""
        self.stats_label.setText(f"Ошибка: {error_msg}")
        logger.error(f"Ошибка мониторинга: {error_msg}")
    
    def closeEvent(self, event):
        """Обработка закрытия виджета"""
        self._stop_monitoring()
        event.accept()