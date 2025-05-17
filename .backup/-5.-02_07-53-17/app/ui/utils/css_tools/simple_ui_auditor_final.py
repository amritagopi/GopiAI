import os
import re
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QTextEdit, QProgressBar, QFileDialog,
                             QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QTextCursor
from app.ui.i18n.translator import tr

# Игнорируемые селекторы при проверке на дублирование
IGNORED_SELECTORS = [
    '@font-face',  # Нормально использовать несколько раз для разных весов шрифта
    'root',        # CSS-переменные часто определяются несколько раз
    '*'            # Универсальный селектор может использоваться несколько раз
]

# Исключаемые паттерны для псевдоклассов
PSEUDOCLASS_PATTERNS = [
    ':hover', ':pressed', ':selected', ':vertical', ':horizontal',
    ':active', ':focus', ':disabled', ':checked'
]

class WorkerSignals(QObject):
    """Определяет сигналы, доступные из рабочего потока."""
    progress = Signal(int)
    message = Signal(str)
    finished = Signal()
    error = Signal(str)

class AuditWorker(QThread):
    """Рабочий поток для выполнения аудита."""

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.signals = WorkerSignals()
        self.is_running = True

    def run(self):
        """Выполняет аудит UI."""
        try:
            # Собираем файлы для анализа
            python_files = []
            qss_files = []
            ui_files = []

            total_files = 0
            processed_files = 0

            # Подсчитываем количество файлов
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.endswith(('.py', '.qss', '.ui', '.css')):
                        total_files += 1

            if total_files == 0:
                self.signals.message.emit(tr("simple_ui_auditor.no_files_found", "Не найдено файлов для анализа."))
                self.signals.finished.emit()
                return

            self.signals.message.emit(tr("simple_ui_auditor.files_found", "Найдено {total_files} файлов для анализа.").format(total_files=total_files))

            # Собираем файлы для анализа
            for root, dirs, files in os.walk(self.project_path):
                # Пропускаем директории venv и .git
                if 'venv' in root or '.git' in root:
                    continue

                for file in files:
                    if not self.is_running:
                        return

                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
                    elif file.endswith(('.qss', '.css')):
                        qss_files.append(os.path.join(root, file))
                    elif file.endswith('.ui'):
                        ui_files.append(os.path.join(root, file))

                    processed_files += 1
                    progress = int(processed_files / total_files * 100)
                    self.signals.progress.emit(progress)

            self.signals.message.emit(tr("simple_ui_auditor.files_collected", "Файлы собраны: {python} Python, {qss} QSS/CSS, {ui} UI").format(python=len(python_files), qss=len(qss_files), ui=len(ui_files)))

            # Анализ Python файлов
            self.signals.message.emit("\n=== Анализ Python файлов ===\n")
            self.analyze_python_files(python_files)

            # Анализ QSS файлов
            self.signals.message.emit("\n=== Анализ QSS/CSS файлов ===\n")
            self.analyze_qss_files(qss_files)

            # Анализ UI файлов
            self.signals.message.emit("\n=== Анализ UI файлов ===\n")
            self.analyze_ui_files(ui_files)

            self.signals.message.emit("\nАудит завершен.")
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(tr("simple_ui_auditor.audit_error", f"Ошибка при выполнении аудита: {str(e)}"))
            self.signals.finished.emit()

    def stop(self):
        """Останавливает выполнение аудита."""
        self.is_running = False

    def analyze_python_files(self, files):
        """Анализирует Python файлы на наличие проблем с UI."""
        if not files:
            self.signals.message.emit(tr("simple_ui_auditor.python_files_not_found", "Python файлы не найдены."))
            return

        issues_found = 0
        hardcoded_colors = {}

        for i, file_path in enumerate(files):
            if not self.is_running:
                return

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Поиск хардкодированных цветов
                hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
                if hex_colors:
                    for color in hex_colors:
                        if color not in hardcoded_colors:
                            hardcoded_colors[color] = []
                        hardcoded_colors[color].append(file_path)
                        issues_found += 1

                # Поиск нелокализованных строк
                ui_strings = re.findall(r'(?:setText|setTitle|setWindowTitle|setToolTip)\(["\']([^"\']+)["\']\)', content)
                for string in ui_strings:
                    if not re.search(r'self\.tr\(["\']' + re.escape(string) + r'["\']\)', content):
                        self.signals.message.emit(
                            tr("simple_ui_auditor.unlocalized_string", "  ⚠️ {file_path}: Нелокализованная строка: \"{string}\"")
                            .format(file_path=file_path, string=string)
                        )
                        issues_found += 1

                # Обновляем прогресс
                progress = int((i + 1) / len(files) * 100)
                self.signals.progress.emit(progress)

            except Exception as e:
                self.signals.message.emit(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

        # Отчет по хардкодированным цветам
        if hardcoded_colors:
            self.signals.message.emit(tr("simple_ui_auditor.hardcoded_colors_found", "\n  ⚠️ Найдено {count} различных хардкодированных цветов:").format(count=len(hardcoded_colors)))
            most_used_colors = sorted([(color, len(files)) for color, files in hardcoded_colors.items()],
                                    key=lambda x: x[1], reverse=True)[:10]
            for color, count in most_used_colors:
                self.signals.message.emit(tr("simple_ui_auditor.color_usage", "    - {color}: {count} использований").format(color=color, count=count))
        else:
            self.signals.message.emit(tr("simple_ui_auditor.no_hardcoded_colors", "  ✅ Хардкодированные цвета не найдены"))

        if issues_found == 0:
            self.signals.message.emit(tr("simple_ui_auditor.no_issues_found", "  ✅ В Python файлах проблем не обнаружено"))

    def analyze_qss_files(self, files):
        """Анализирует QSS файлы на наличие проблем."""
        if not files:
            self.signals.message.emit(tr("simple_ui_auditor.qss_files_not_found", "QSS/CSS файлы не найдены."))
            return

        issues_found = 0

        for i, file_path in enumerate(files):
            if not self.is_running:
                return

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Проверка на неправильные цветовые коды
                invalid_colors = re.findall(r'#[0-9a-fA-F]{5}\b', content)
                if invalid_colors:
                    joined_colors = ', '.join(set(invalid_colors))
                    self.signals.message.emit(
                        tr("simple_ui_auditor.invalid_colors", "  ❌ {file_path}: Неправильные цветовые коды: {colors}")
                        .format(file_path=file_path, colors=joined_colors)
                    )
                    issues_found += 1

                # Проверка на дублирование селекторов
                selectors = re.findall(r'([^{]+)\s*\{', content)
                # Очищаем селекторы от пробелов
                selectors = [s.strip() for s in selectors]

                # Фильтруем игнорируемые селекторы
                filtered_selectors = []
                for selector in selectors:
                    # Пропускаем игнорируемые селекторы
                    if any(ignored in selector for ignored in IGNORED_SELECTORS):
                        continue

                    # Нормализуем селекторы, удаляя псевдоклассы для сравнения
                    normalized = selector
                    for pseudo in PSEUDOCLASS_PATTERNS:
                        if pseudo in normalized:
                            # Получаем базовый селектор без псевдокласса
                            parts = normalized.split(pseudo, 1)
                            normalized = parts[0].strip()

                    # Добавляем нормализованный селектор
                    filtered_selectors.append(normalized)

                # Считаем полностью идентичные селекторы после нормализации
                selector_counts = {}
                for selector in filtered_selectors:
                    if selector in selector_counts:
                        selector_counts[selector] += 1
                    else:
                        selector_counts[selector] = 1

                # Находим только дублирующиеся селекторы (те, что встречаются более раза)
                duplicates = [s for s, count in selector_counts.items() if count > 1]

                if duplicates:
                    joined_duplicates = ', '.join([d[:30] + '...' if len(d) > 30 else d for d in duplicates[:5]])
                    self.signals.message.emit(
                        tr("simple_ui_auditor.duplicate_selectors", "  ⚠️ {file_path}: Дублирующиеся селекторы: {dups}")
                        .format(file_path=file_path, dups=joined_duplicates)
                    )
                    issues_found += 1

                # Обновляем прогресс
                progress = int((i + 1) / len(files) * 100)
                self.signals.progress.emit(progress)

            except Exception as e:
                self.signals.message.emit(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

        if issues_found == 0:
            self.signals.message.emit(tr("simple_ui_auditor.no_issues_found", "  ✅ В QSS/CSS файлах проблем не обнаружено"))

    def analyze_ui_files(self, files):
        """Анализирует UI файлы на наличие проблем."""
        if not files:
            self.signals.message.emit(tr("simple_ui_auditor.ui_files_not_found", "UI файлы не найдены."))
            return

        issues_found = 0

        for i, file_path in enumerate(files):
            if not self.is_running:
                return

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Проверка на использование фиксированных размеров
                if re.search(r'<width>(\d+)</width>', content) and not re.search(r'<layout', content):
                    self.signals.message.emit(tr("simple_ui_auditor.fixed_sizes_without_layout", "  ⚠️ {file_path}: Используются фиксированные размеры без layout").format(file_path=file_path))
                    issues_found += 1

                # Обновляем прогресс
                progress = int((i + 1) / len(files) * 100)
                self.signals.progress.emit(progress)

            except Exception as e:
                self.signals.message.emit(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

        if issues_found == 0:
            self.signals.message.emit(tr("simple_ui_auditor.no_issues_found", "  ✅ В UI файлах проблем не обнаружено"))


class SimpleUIAuditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("simple_ui_auditor.title", "GopiAI UI Auditor"))
        self.resize(800, 600)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Текстовое поле для вывода результатов
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Кнопки действий
        audit_button = QPushButton("Провести аудит UI")
        audit_button.clicked.connect(self.run_audit)
        layout.addWidget(audit_button)

        export_button = QPushButton("Экспортировать отчет")
        export_button.clicked.connect(self.export_report)
        layout.addWidget(export_button)

        self.worker = None

    def run_audit(self):
        """Запускает процесс аудита."""
        try:
            # Устанавливаем проект для анализа
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Выводим сообщение о начале аудита
            self.append_message(tr("simple_ui_auditor.audit_starting", "Запуск аудита UI..."))

            # Создаем рабочий поток
            self.worker = AuditWorker(project_path)
            self.worker.signals.progress.connect(self.update_progress)
            self.worker.signals.message.connect(self.append_message)
            self.worker.signals.finished.connect(self.audit_finished)
            self.worker.signals.error.connect(self.handle_error)

            # Запускаем поток
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, tr("simple_ui_auditor.error", "Ошибка"),
                                str(e))

    def update_progress(self, value):
        """Обновляет прогресс-бар."""
        self.progress_bar.setValue(value)

    def append_message(self, message):
        """Добавляет сообщение в текстовое поле."""
        self.results_text.append(message)
        # Прокручиваем до конца
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.results_text.setTextCursor(cursor)

    def audit_finished(self):
        """Вызывается при завершении аудита."""
        self.progress_bar.setValue(100)
        self.append_message("\nАудит завершен.")

    def handle_error(self, error_message):
        """Обрабатывает ошибки."""
        QMessageBox.critical(self, tr("simple_ui_auditor.error_title", "Ошибка"), error_message)

    def export_report(self):
        """Экспортирует отчет в файл."""
        if not self.results_text.toPlainText():
            QMessageBox.warning(self, "Предупреждение", "Нет данных для экспорта!")
            return

        # Создаем директорию logs, если ее нет
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = os.path.join(project_root, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Формируем имя файла с датой и временем
        from datetime import datetime
        now = datetime.now()
        default_filename = f"ui_audit_report_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        default_path = os.path.join(logs_dir, default_filename)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", default_path, "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())
                QMessageBox.information(self, "Успех", tr("simple_ui_auditor.report_saved", f"Отчет сохранен в {file_path}"))
            except Exception as e:
                QMessageBox.critical(self, tr("simple_ui_auditor.error_title", "Ошибка"), tr("simple_ui_auditor.save_error", f"Не удалось сохранить отчет: {str(e)}"))

    def closeEvent(self, event):
        """Обрабатывает закрытие окна."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

def run_audit_cli():
    """Запускает аудит из командной строки без GUI."""
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Создаем директорию logs, если ее нет
    project_root = os.path.dirname(os.path.dirname(project_path))
    logs_dir = os.path.join(project_root, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Формируем имя файла с датой и временем для CLI версии
    from datetime import datetime
    now = datetime.now()
    log_filename = f"ui_audit_report_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    log_path = os.path.join(logs_dir, log_filename)

    # Перенаправляем вывод в файл и на экран
    class TeeOutput:
        def __init__(self, file_path):
            self.file = open(file_path, 'w', encoding='utf-8')
            self.stdout = sys.stdout

        def write(self, message):
            self.file.write(message)
            self.stdout.write(message)
            self.file.flush()
            self.stdout.flush()

        def flush(self):
            self.file.flush()
            self.stdout.flush()

        def close(self):
            self.file.close()

    # Сохраняем оригинальный stdout
    original_stdout = sys.stdout
    try:
        # Перенаправляем вывод в файл и консоль
        sys.stdout = TeeOutput(log_path)

        # Заголовок
        print(tr("simple_ui_auditor.audit_starting", "Запуск аудита UI..."))

        # Собираем файлы для анализа
        python_files = []
        qss_files = []
        ui_files = []

        total_files = 0

        # Подсчитываем количество файлов
        for root, dirs, files in os.walk(project_path):
            # Пропускаем директории venv и .git
            if 'venv' in root or '.git' in root:
                continue

            for file in files:
                if file.endswith(('.py', '.qss', '.ui', '.css')):
                    total_files += 1

        if total_files == 0:
            print(tr("simple_ui_auditor.no_files_found", "Не найдено файлов для анализа."))
            return

        print(tr("simple_ui_auditor.files_found", "Найдено {total_files} файлов для анализа.").format(total_files=total_files))

        # Собираем файлы для анализа
        for root, dirs, files in os.walk(project_path):
            # Пропускаем директории venv и .git
            if 'venv' in root or '.git' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                elif file.endswith(('.qss', '.css')):
                    qss_files.append(os.path.join(root, file))
                elif file.endswith('.ui'):
                    ui_files.append(os.path.join(root, file))

        print(tr("simple_ui_auditor.files_collected", "Файлы собраны: {python} Python, {qss} QSS/CSS, {ui} UI").format(python=len(python_files), qss=len(qss_files), ui=len(ui_files)))

        # Анализ Python файлов
        print("\n=== Анализ Python файлов ===\n")
        analyze_python_files_cli(python_files)

        # Анализ QSS файлов
        print("\n=== Анализ QSS/CSS файлов ===\n")
        analyze_qss_files_cli(qss_files)

        # Анализ UI файлов
        print("\n=== Анализ UI файлов ===\n")
        analyze_ui_files_cli(ui_files)

        print("\nАудит завершен.")
    finally:
        # Восстанавливаем оригинальный stdout и закрываем файл
        if sys.stdout != original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout
        print(f"Отчет сохранен в {log_path}")

    return

def analyze_python_files_cli(files):
    """Анализирует Python файлы на наличие проблем с UI (консольная версия)."""
    if not files:
        print(tr("simple_ui_auditor.python_files_not_found", "Python файлы не найдены."))
        return

    issues_found = 0
    hardcoded_colors = {}

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Поиск хардкодированных цветов
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
            if hex_colors:
                for color in hex_colors:
                    if color not in hardcoded_colors:
                        hardcoded_colors[color] = []
                    hardcoded_colors[color].append(file_path)
                    issues_found += 1

            # Поиск нелокализованных строк
            ui_strings = re.findall(r'(?:setText|setTitle|setWindowTitle|setToolTip)\(["\']([^"\']+)["\']\)', content)
            for string in ui_strings:
                if not re.search(r'tr\(["\']', content) or not re.search(r'self\.tr\(["\']', content):
                    print(tr("simple_ui_auditor.unlocalized_string", "  ⚠️ {file_path}: Нелокализованная строка: \"{string}\"").format(file_path=file_path, string=string))
                    issues_found += 1

        except Exception as e:
            print(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

    # Отчет по хардкодированным цветам
    if hardcoded_colors:
        print(tr("simple_ui_auditor.hardcoded_colors_found", "\n  ⚠️ Найдено {count} различных хардкодированных цветов:").format(count=len(hardcoded_colors)))
        most_used_colors = sorted([(color, len(files)) for color, files in hardcoded_colors.items()],
                                key=lambda x: x[1], reverse=True)[:10]
        for color, count in most_used_colors:
            print(tr("simple_ui_auditor.color_usage", "    - {color}: {count} использований").format(color=color, count=count))
    else:
        print(tr("simple_ui_auditor.no_hardcoded_colors", "  ✅ Хардкодированные цвета не найдены"))

    if issues_found == 0:
        print(tr("simple_ui_auditor.no_issues_found", "  ✅ В Python файлах проблем не обнаружено"))

def analyze_qss_files_cli(files):
    """Анализирует QSS файлы на наличие проблем (консольная версия)."""
    if not files:
        print(tr("simple_ui_auditor.qss_files_not_found", "QSS/CSS файлы не найдены."))
        return

    issues_found = 0

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Проверка на неправильные цветовые коды
            invalid_colors = re.findall(r'#[0-9a-fA-F]{5}\b', content)
            if invalid_colors:
                joined_colors = ', '.join(set(invalid_colors))
                print(tr("simple_ui_auditor.invalid_colors", "  ❌ {file_path}: Неправильные цветовые коды: {colors}").format(file_path=file_path, colors=joined_colors))
                issues_found += 1

            # Проверка на дублирование селекторов
            selectors = re.findall(r'([^{]+)\s*\{', content)
            # Очищаем селекторы от пробелов
            selectors = [s.strip() for s in selectors]

            # Фильтруем игнорируемые селекторы
            filtered_selectors = []
            for selector in selectors:
                # Пропускаем игнорируемые селекторы
                if any(ignored in selector for ignored in IGNORED_SELECTORS):
                    continue

                # Нормализуем селекторы, удаляя псевдоклассы для сравнения
                normalized = selector
                for pseudo in PSEUDOCLASS_PATTERNS:
                    if pseudo in normalized:
                        # Получаем базовый селектор без псевдокласса
                        parts = normalized.split(pseudo, 1)
                        normalized = parts[0].strip()

                # Добавляем нормализованный селектор
                filtered_selectors.append(normalized)

            # Считаем полностью идентичные селекторы после нормализации
            selector_counts = {}
            for selector in filtered_selectors:
                if selector in selector_counts:
                    selector_counts[selector] += 1
                else:
                    selector_counts[selector] = 1

            # Находим только дублирующиеся селекторы (те, что встречаются более раза)
            duplicates = [s for s, count in selector_counts.items() if count > 1]

            if duplicates:
                joined_duplicates = ', '.join([d[:30] + '...' if len(d) > 30 else d for d in duplicates[:5]])
                print(tr("simple_ui_auditor.duplicate_selectors", "  ⚠️ {file_path}: Дублирующиеся селекторы: {dups}").format(file_path=file_path, dups=joined_duplicates))
                issues_found += 1

        except Exception as e:
            print(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

    if issues_found == 0:
        print(tr("simple_ui_auditor.no_issues_found", "  ✅ В QSS/CSS файлах проблем не обнаружено"))

def analyze_ui_files_cli(files):
    """Анализирует UI файлы на наличие проблем (консольная версия)."""
    if not files:
        print(tr("simple_ui_auditor.ui_files_not_found", "UI файлы не найдены."))
        return

    issues_found = 0

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Проверка на использование фиксированных размеров
            if re.search(r'<width>(\d+)</width>', content) and not re.search(r'<layout', content):
                print(tr("simple_ui_auditor.fixed_sizes_without_layout", "  ⚠️ {file_path}: Используются фиксированные размеры без layout").format(file_path=file_path))
                issues_found += 1

        except Exception as e:
            print(tr("simple_ui_auditor.analysis_error", f"  ⚠️ Ошибка при анализе {file_path}: {str(e)}"))

    if issues_found == 0:
        print(tr("simple_ui_auditor.no_issues_found", "  ✅ В UI файлах проблем не обнаружено"))

if __name__ == "__main__":
    # Проверяем, запущен ли скрипт напрямую или из console
    if os.environ.get('PYTHONIOENCODING') == 'utf-8' or sys.stdout.encoding == 'utf-8':
        # Запуск в режиме консоли
        run_audit_cli()
    else:
        # Запуск GUI
        app = QApplication(sys.argv)
        auditor = SimpleUIAuditor()
        auditor.show()
        auditor.run_audit()
        sys.exit(app.exec())
