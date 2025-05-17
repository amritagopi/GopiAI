import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QTextCharFormat, QTextOption
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFormLayout,
                               QGroupBox, QHBoxLayout, QLabel, QMessageBox,
                               QProgressBar, QPushButton, QScrollArea,
                               QSpinBox, QSplitter, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget, QApplication, QTreeWidget,
                               QTreeWidgetItem, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QGridLayout, QMenu, QToolBar)

from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon

logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    """Сигналы для воркера."""
    started = Signal()
    finished = Signal()
    progress = Signal(int)
    log = Signal(str)
    error = Signal(str)
    results = Signal(object)

class AnalysisWorker(QThread):
    """Класс для выполнения анализа кода в отдельном потоке."""

    def __init__(self, analysis_type, params=None):
        super().__init__()
        self.analysis_type = analysis_type
        self.params = params or {}
        self.signals = WorkerSignals()
        self.is_running = True

    def run(self):
        """Выполняет анализ кода в отдельном потоке."""
        self.signals.started.emit()
        try:
            if self.analysis_type == "dependencies":
                self._run_dependencies_analysis()
            elif self.analysis_type == "unused_code":
                self._run_unused_code_analysis()
            elif self.analysis_type == "duplication":
                self._run_duplication_analysis()
            elif self.analysis_type == "dead_code":
                self._run_dead_code_analysis()
            else:
                raise ValueError(f"Неизвестный тип анализа: {self.analysis_type}")
        except Exception as e:
            logger.exception(f"Ошибка в процессе анализа {self.analysis_type}: {e}")
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def _run_dependencies_analysis(self):
        """Запускает анализ зависимостей проекта."""
        from importlib import import_module
        self.signals.log.emit("Запуск анализа зависимостей проекта...")

        try:
            # Импортируем наш адаптер
            adapter = import_module("code_analysis_integration_adapter")

            # Получаем параметры
            project_dir = self.params.get('project_dir', '.')

            # Выполняем анализ через адаптер
            self.signals.log.emit(f"Анализируем директорию: {project_dir}")

            result = adapter.analyze_dependencies_project(
                project_dir,
                self._progress_callback
            )

            # Выводим информацию о результатах
            output_file = result.get('output_file')
            if output_file:
                self.signals.log.emit(f"Результаты сохранены в {output_file}")

            self.signals.results.emit(result)
            self.signals.log.emit("Анализ зависимостей завершен успешно.")

        except Exception as e:
            self.signals.error.emit(f"Ошибка при анализе зависимостей: {str(e)}")
            logger.exception("Ошибка при анализе зависимостей")

    def _run_unused_code_analysis(self):
        """Запускает анализ неиспользуемого кода."""
        from importlib import import_module
        self.signals.log.emit("Запуск анализа неиспользуемого кода...")

        try:
            # Импортируем наш адаптер
            adapter = import_module("code_analysis_integration_adapter")

            # Получаем параметры
            project_dir = self.params.get('project_dir', '.')

            # Выполняем анализ через адаптер
            self.signals.log.emit(f"Анализируем директорию: {project_dir}")

            result = adapter.find_unused_files_in_project(
                project_dir,
                self._progress_callback
            )

            # Выводим информацию о результатах
            output_file = result.get('output_file')
            if output_file:
                self.signals.log.emit(f"Результаты сохранены в {output_file}")

            self.signals.results.emit(result)
            self.signals.log.emit("Анализ неиспользуемого кода завершен успешно.")

        except Exception as e:
            self.signals.error.emit(f"Ошибка при анализе неиспользуемого кода: {str(e)}")
            logger.exception("Ошибка при анализе неиспользуемого кода")

    def _run_duplication_analysis(self):
        """Запускает анализ дублирования кода."""
        from importlib import import_module
        self.signals.log.emit("Запуск анализа дублирования кода...")

        try:
            # Импортируем наш адаптер
            adapter = import_module("code_analysis_integration_adapter")

            # Получаем параметры
            project_dir = self.params.get('project_dir', '.')
            min_lines = self.params.get('min_lines', 5)
            include_comments = self.params.get('include_comments', False)

            # Выполняем анализ через адаптер
            self.signals.log.emit(f"Анализируем директорию: {project_dir}")

            result = adapter.analyze_code_duplication(
                project_dir,
                min_lines=min_lines,
                include_comments=include_comments,
                progress_callback=self._progress_callback
            )

            # Выводим информацию о результатах
            output_files = result.get('output_files', [])
            if output_files:
                self.signals.log.emit(f"Результаты сохранены в: {', '.join(output_files)}")

            self.signals.results.emit(result)
            self.signals.log.emit("Анализ дублирования кода завершен успешно.")

        except Exception as e:
            self.signals.error.emit(f"Ошибка при анализе дублирования кода: {str(e)}")
            logger.exception("Ошибка при анализе дублирования кода")

    def _run_dead_code_analysis(self):
        """Запускает анализ и маркировку мертвого кода."""
        from importlib import import_module
        self.signals.log.emit("Запуск анализа мертвого кода...")

        try:
            # Импортируем наш адаптер
            adapter = import_module("code_analysis_integration_adapter")

            # Получаем параметры
            project_dir = self.params.get('project_dir', '.')
            dry_run = self.params.get('dry_run', True)  # По умолчанию - без изменений
            confidence = self.params.get('confidence', 90)

            # Выполняем анализ через адаптер
            self.signals.log.emit(f"Анализируем директорию: {project_dir}")

            result = adapter.analyze_and_mark_dead_code(
                project_dir,
                confidence=confidence,
                dry_run=dry_run,
                progress_callback=self._progress_callback
            )

            # Выводим информацию о результатах
            output_file = result.get('output_file')
            if output_file:
                self.signals.log.emit(f"Результаты сохранены в {output_file}")

            self.signals.results.emit(result)

            if dry_run:
                self.signals.log.emit("Анализ мертвого кода завершен успешно (без внесения изменений).")
            else:
                self.signals.log.emit("Анализ и маркировка мертвого кода завершены успешно.")

        except Exception as e:
            self.signals.error.emit(f"Ошибка при анализе мертвого кода: {str(e)}")
            logger.exception("Ошибка при анализе мертвого кода")

    def _progress_callback(self, progress):
        """Callback для обновления прогресса."""
        if isinstance(progress, int):
            self.signals.progress.emit(progress)
        elif isinstance(progress, str):
            self.signals.log.emit(progress)

    def stop(self):
        """Останавливает выполнение анализа."""
        self.is_running = False
        self.signals.log.emit("Остановка анализа по запросу пользователя...")
        self.terminate()

class CodeAnalysisWidget(QWidget):
    """Виджет для анализа кода в проекте."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(tr("code_analysis.title", "Анализ кода"))
        self.setObjectName("CodeAnalysisWidget")

        # Инициализация UI
        self._setup_ui()

        # Подключение сигналов
        self._connect_signals()

        # Инициализация рабочего потока
        self.worker = None

        # Устанавливаем значения по умолчанию
        self._set_default_values()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Верхняя панель с настройками
        self.settings_group = QGroupBox(tr("code_analysis.settings", "Настройки анализа"))
        settings_layout = QFormLayout(self.settings_group)

        # Выбор типа анализа
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItem(tr("code_analysis.type.dependencies", "Анализ зависимостей"), "dependencies")
        self.analysis_type_combo.addItem(tr("code_analysis.type.unused", "Поиск неиспользуемого кода"), "unused_code")
        self.analysis_type_combo.addItem(tr("code_analysis.type.duplication", "Анализ дублирования"), "duplication")
        self.analysis_type_combo.addItem(tr("code_analysis.type.dead_code", "Маркировка мертвого кода"), "dead_code")

        settings_layout.addRow(tr("code_analysis.type", "Тип анализа:"), self.analysis_type_combo)

        # Выбор директории проекта
        self.project_dir_layout = QHBoxLayout()
        self.project_dir_edit = QComboBox()
        self.project_dir_edit.setEditable(True)
        self.project_dir_edit.addItem(os.getcwd())
        self.project_dir_button = QPushButton("...")
        self.project_dir_button.setMaximumWidth(30)

        self.project_dir_layout.addWidget(self.project_dir_edit)
        self.project_dir_layout.addWidget(self.project_dir_button)

        settings_layout.addRow(tr("code_analysis.project_dir", "Директория проекта:"), self.project_dir_layout)

        # Дополнительные настройки для анализа дублирования
        self.duplication_settings = QGroupBox(tr("code_analysis.duplication.settings", "Настройки анализа дублирования"))
        duplication_layout = QFormLayout(self.duplication_settings)

        self.min_lines_spin = QSpinBox()
        self.min_lines_spin.setRange(3, 100)
        self.min_lines_spin.setValue(5)
        self.min_lines_spin.setToolTip(tr("code_analysis.duplication.min_lines.tooltip",
                                         "Минимальное количество строк в дублированном фрагменте"))

        self.include_comments_check = QCheckBox(tr("code_analysis.duplication.include_comments", "Включать комментарии"))
        self.include_comments_check.setChecked(False)

        duplication_layout.addRow(tr("code_analysis.duplication.min_lines", "Минимум строк:"), self.min_lines_spin)
        duplication_layout.addRow("", self.include_comments_check)

        # Дополнительные настройки для анализа мертвого кода
        self.dead_code_settings = QGroupBox(tr("code_analysis.dead_code.settings", "Настройки анализа мертвого кода"))
        dead_code_layout = QFormLayout(self.dead_code_settings)

        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(50, 100)
        self.confidence_spin.setValue(90)
        self.confidence_spin.setToolTip(tr("code_analysis.dead_code.confidence.tooltip",
                                         "Уровень уверенности для маркировки мертвого кода"))

        self.dry_run_check = QCheckBox(tr("code_analysis.dead_code.dry_run", "Только анализ (без изменений)"))
        self.dry_run_check.setChecked(True)

        dead_code_layout.addRow(tr("code_analysis.dead_code.confidence", "Уровень уверенности:"), self.confidence_spin)
        dead_code_layout.addRow("", self.dry_run_check)

        # Скрываем дополнительные настройки по умолчанию
        self.duplication_settings.setVisible(False)
        self.dead_code_settings.setVisible(False)

        # Добавляем все настройки в основной layout
        main_layout.addWidget(self.settings_group)
        main_layout.addWidget(self.duplication_settings)
        main_layout.addWidget(self.dead_code_settings)

        # Кнопки управления
        self.buttons_layout = QHBoxLayout()

        self.start_button = QPushButton(tr("code_analysis.start", "Запустить анализ"))
        self.start_button.setIcon(get_icon("play"))

        self.stop_button = QPushButton(tr("code_analysis.stop", "Остановить"))
        self.stop_button.setIcon(get_icon("stop"))
        self.stop_button.setEnabled(False)

        self.view_results_button = QPushButton(tr("code_analysis.view_results", "Просмотр результатов"))
        self.view_results_button.setIcon(get_icon("view"))
        self.view_results_button.setEnabled(False)

        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.buttons_layout.addWidget(self.view_results_button)

        main_layout.addLayout(self.buttons_layout)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Лог операций
        self.log_group = QGroupBox(tr("code_analysis.log", "Лог операций"))
        log_layout = QVBoxLayout(self.log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)

        # Устанавливаем моноширинный шрифт для лога
        font = QFont("Courier New", 10)
        self.log_text.setFont(font)

        log_layout.addWidget(self.log_text)

        # Кнопка очистки лога
        self.clear_log_button = QPushButton(tr("code_analysis.clear_log", "Очистить лог"))
        self.clear_log_button.setIcon(get_icon("clear"))
        log_layout.addWidget(self.clear_log_button)

        main_layout.addWidget(self.log_group)

        # Устанавливаем размеры виджетов и растяжение
        main_layout.setStretch(4, 1)  # Лог операций растягивается

    def _connect_signals(self):
        """Подключает сигналы к слотам."""
        # Сигналы настроек
        self.analysis_type_combo.currentIndexChanged.connect(self._on_analysis_type_changed)
        self.project_dir_button.clicked.connect(self._on_select_project_dir)

        # Сигналы кнопок
        self.start_button.clicked.connect(self._on_start_analysis)
        self.stop_button.clicked.connect(self._on_stop_analysis)
        self.view_results_button.clicked.connect(self._on_view_results)
        self.clear_log_button.clicked.connect(self.log_text.clear)

    def _set_default_values(self):
        """Устанавливает значения по умолчанию."""
        # Устанавливаем текущую директорию проекта
        self.project_dir_edit.setCurrentText(os.getcwd())

        # Значения для остальных полей устанавливаются при инициализации

        # Добавляем начальное сообщение в лог
        self._log_message(tr("code_analysis.ready", "Инструмент анализа кода готов к работе."))
        self._log_message(tr("code_analysis.select_type", "Выберите тип анализа и нажмите 'Запустить анализ'."))

    def _on_analysis_type_changed(self, index):
        """Обрабатывает изменение типа анализа."""
        analysis_type = self.analysis_type_combo.currentData()

        # Показываем/скрываем дополнительные настройки в зависимости от типа анализа
        self.duplication_settings.setVisible(analysis_type == "duplication")
        self.dead_code_settings.setVisible(analysis_type == "dead_code")

        # Логируем изменение
        self._log_message(tr("code_analysis.type_changed", f"Выбран тип анализа: {self.analysis_type_combo.currentText()}"))

    def _on_select_project_dir(self):
        """Обрабатывает выбор директории проекта."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            tr("code_analysis.select_dir", "Выберите директорию проекта"),
            self.project_dir_edit.currentText()
        )

        if dir_path:
            # Добавляем директорию в список, если её там нет
            if self.project_dir_edit.findText(dir_path) == -1:
                self.project_dir_edit.addItem(dir_path)

            # Устанавливаем текущую директорию
            self.project_dir_edit.setCurrentText(dir_path)

            self._log_message(tr("code_analysis.dir_selected", f"Выбрана директория проекта: {dir_path}"))

    def _on_start_analysis(self):
        """Запускает анализ кода."""
        # Проверяем, что директория существует
        project_dir = self.project_dir_edit.currentText()
        if not os.path.isdir(project_dir):
            QMessageBox.warning(
                self,
                tr("code_analysis.error", "Ошибка"),
                tr("code_analysis.dir_not_exist", f"Директория {project_dir} не существует.")
            )
            return

        # Получаем тип анализа
        analysis_type = self.analysis_type_combo.currentData()

        # Подготавливаем параметры
        params = {
            'project_dir': project_dir
        }

        # Добавляем параметры в зависимости от типа анализа
        if analysis_type == "duplication":
            params.update({
                'min_lines': self.min_lines_spin.value(),
                'include_comments': self.include_comments_check.isChecked()
            })
        elif analysis_type == "dead_code":
            params.update({
                'confidence': self.confidence_spin.value(),
                'dry_run': self.dry_run_check.isChecked()
            })

        # Логируем начало анализа
        self._log_message(tr("code_analysis.started", f"Начинаем анализ: {self.analysis_type_combo.currentText()}"))
        self._log_message(tr("code_analysis.params", f"Параметры: {params}"))

        # Обновляем UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.view_results_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # Создаем и запускаем рабочий поток
        self.worker = AnalysisWorker(analysis_type, params)

        # Подключаем сигналы
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.log.connect(self._log_message)
        self.worker.signals.error.connect(self._log_error)
        self.worker.signals.results.connect(self._on_results_ready)

        # Запускаем поток
        self.worker.start()

    def _on_stop_analysis(self):
        """Останавливает анализ кода."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._log_message(tr("code_analysis.stopping", "Останавливаем анализ..."))

    def _on_view_results(self):
        """Отображает результаты анализа."""
        if not hasattr(self, 'results_data') or not self.results_data:
            return

        analysis_type = self.analysis_type_combo.currentData()

        # В зависимости от типа анализа, отображаем результаты по-разному
        if analysis_type == "dependencies":
            self._show_dependencies_results()
        elif analysis_type == "unused_code":
            self._show_unused_code_results()
        elif analysis_type == "duplication":
            self._show_duplication_results()
        elif analysis_type == "dead_code":
            self._show_dead_code_results()

    def _show_dependencies_results(self):
        """Отображает результаты анализа зависимостей."""
        # Обрабатываем отображение результатов анализа зависимостей
        # В идеале, здесь нужно создать специализированный виджет для визуализации графа зависимостей
        self._log_message(tr("code_analysis.view_dependencies", "Отображение результатов анализа зависимостей..."))

        # Простой вариант - просто открываем файл с результатами, если он есть
        if isinstance(self.results_data, dict) and 'output_file' in self.results_data:
            os.startfile(self.results_data['output_file'])
        else:
            self._log_message(tr("code_analysis.no_results_file", "Файл с результатами не найден."))

    def _show_unused_code_results(self):
        """Отображает результаты анализа неиспользуемого кода."""
        # Обрабатываем отображение результатов анализа неиспользуемого кода
        self._log_message(tr("code_analysis.view_unused", "Отображение результатов анализа неиспользуемого кода..."))

        # Открываем файл с результатами, если он есть
        if isinstance(self.results_data, dict) and 'output_file' in self.results_data:
            os.startfile(self.results_data['output_file'])
        else:
            self._log_message(tr("code_analysis.no_results_file", "Файл с результатами не найден."))

    def _show_duplication_results(self):
        """Отображает результаты анализа дублирования кода."""
        # Обрабатываем отображение результатов анализа дублирования
        self._log_message(tr("code_analysis.view_duplication", "Отображение результатов анализа дублирования кода..."))

        # Открываем HTML-отчет, если он есть
        if isinstance(self.results_data, dict) and 'output_files' in self.results_data:
            for file in self.results_data['output_files']:
                if file.endswith('.html'):
                    os.startfile(file)
                    return

            # Если HTML-отчета нет, открываем текстовый
            for file in self.results_data['output_files']:
                if file.endswith('.txt'):
                    os.startfile(file)
                    return
        else:
            self._log_message(tr("code_analysis.no_results_file", "Файл с результатами не найден."))

    def _show_dead_code_results(self):
        """Отображает результаты анализа мертвого кода."""
        # Обрабатываем отображение результатов анализа мертвого кода
        self._log_message(tr("code_analysis.view_dead_code", "Отображение результатов анализа мертвого кода..."))

        # Открываем файл с результатами, если он есть
        if isinstance(self.results_data, dict) and 'output_file' in self.results_data:
            os.startfile(self.results_data['output_file'])
        else:
            self._log_message(tr("code_analysis.no_results_file", "Файл с результатами не найден."))

    def _on_worker_started(self):
        """Обрабатывает начало работы анализатора."""
        # Обновляем UI
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.view_results_button.setEnabled(False)

        # Логируем начало работы
        self._log_message(tr("code_analysis.worker_started", "Анализатор начал работу..."))

    def _on_worker_finished(self):
        """Обрабатывает завершение работы анализатора."""
        # Обновляем UI
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.view_results_button.setEnabled(hasattr(self, 'results_data') and self.results_data is not None)

        # Логируем завершение работы
        self._log_message(tr("code_analysis.worker_finished", "Анализатор завершил работу."))

    def _on_results_ready(self, results):
        """Обрабатывает получение результатов анализа."""
        # Сохраняем результаты
        self.results_data = results

        # Обновляем кнопку просмотра результатов
        self.view_results_button.setEnabled(True)

        # Логируем получение результатов
        self._log_message(tr("code_analysis.results_ready", "Получены результаты анализа."))

    def _log_message(self, message):
        """Добавляет сообщение в лог."""
        # Форматируем сообщение с временной меткой
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"

        # Добавляем сообщение в лог
        self.log_text.append(formatted_message)

        # Прокручиваем лог до конца
        self.log_text.moveCursor(QTextCursor.End)

    def _log_error(self, error_message):
        """Добавляет сообщение об ошибке в лог."""
        # Создаем формат для текста ошибки (красный цвет)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(255, 0, 0))  # Красный цвет

        # Получаем текущий курсор
        cursor = self.log_text.textCursor()

        # Запоминаем текущий формат
        current_format = cursor.charFormat()

        # Форматируем сообщение с временной меткой
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] ОШИБКА: {error_message}"

        # Устанавливаем формат ошибки
        cursor.setCharFormat(error_format)

        # Добавляем сообщение
        cursor.insertText(formatted_message + "\n")

        # Восстанавливаем предыдущий формат
        cursor.setCharFormat(current_format)

        # Прокручиваем лог до конца
        self.log_text.moveCursor(QTextCursor.End)

        # Логируем ошибку
        logger.error(error_message)

# Функция для интеграции виджета в главное окно
def integrate_code_analysis_widget(main_window):
    """Интегрирует виджет анализа кода в главное окно приложения."""
    try:
        # Создаем виджет анализа кода
        code_analysis_widget = CodeAnalysisWidget(main_window)

        # Добавляем вкладку анализа кода в основной виджет приложения
        if hasattr(main_window, 'central_tabs'):
            tab_index = main_window.central_tabs.addTab(
                code_analysis_widget,
                get_icon("analyze"),
                tr("code_analysis.tab_title", "Анализ кода")
            )

            # Активируем вкладку
            main_window.central_tabs.setCurrentIndex(tab_index)

            # Добавляем информацию в статусную строку
            if hasattr(main_window, 'status_label'):
                main_window.status_label.setText(
                    tr("code_analysis.status.opened", "Открыт инструмент анализа кода")
                )

            return code_analysis_widget
        else:
            # Если нет central_tabs, создаем отдельное окно
            from PySide6.QtWidgets import QDialog, QVBoxLayout

            dialog = QDialog(main_window)
            dialog.setWindowTitle(tr("code_analysis.window_title", "Инструмент анализа кода"))
            dialog.resize(800, 600)

            layout = QVBoxLayout(dialog)
            layout.addWidget(code_analysis_widget)

            dialog.show()

            return code_analysis_widget

    except Exception as e:
        logger.exception(f"Ошибка при интеграции виджета анализа кода: {e}")
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            main_window,
            tr("code_analysis.error", "Ошибка"),
            tr("code_analysis.integration_error", f"Ошибка при интеграции виджета анализа кода: {str(e)}")
        )

        return None
