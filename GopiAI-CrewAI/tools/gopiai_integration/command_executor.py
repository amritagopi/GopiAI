"""
Command Executor - исполнитель команд из ответов Gemini
Восстановлено из коммита 2f0fe4256d7f0d5bf2168a4db56d6b6def937860
"""

import logging
import re
import subprocess
import os
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Для графического интерфейса - используем PySide6 и интеграцию с GopiAI UI системой
try:
    from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    # Пытаемся импортировать систему тем GopiAI
    import sys
    import os
    ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'GopiAI-UI'))
    if ui_path not in sys.path:
        sys.path.insert(0, ui_path)
    
    try:
        from gopiai.ui.utils.simple_theme_manager import SimpleThemeManager
        from gopiai.ui.utils.icon_helpers import load_lucide_icon, create_icon_button
        HAS_GOPIAI_THEMES = True
    except ImportError:
        HAS_GOPIAI_THEMES = False
        
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    HAS_GOPIAI_THEMES = False

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Уровни риска команд"""
    SAFE = "safe"           # Безопасные команды (ls, pwd, etc.)
    LOW = "low"             # Низкий риск (cat, head, tail, etc.)
    MEDIUM = "medium"       # Средний риск (curl, wget, python, etc.)
    HIGH = "high"           # Высокий риск (rm, chmod, sudo, etc.)
    CRITICAL = "critical"   # Критический риск (format, shutdown, etc.)

@dataclass
class CommandRisk:
    """Информация о риске команды"""
    level: RiskLevel
    description: str
    consequences: str
    
class CommandExecutor:
    """Исполнитель команд с интерактивным контролем безопасности"""
    
    def __init__(self):
        # Убираем ограничения supported_commands - теперь поддерживаем всё!
        self.risk_database = self._build_risk_database()
        logger.info("CommandExecutor initialized (all restrictions removed)")
    
    def process_gemini_response(self, response_text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Анализирует ответ Gemini на наличие команд и выполняет их
        
        Returns:
            Tuple[str, List[Dict]]: (обновленный_текст, список_результатов_команд)
        """
        if not response_text:
            return response_text, []
        
        # Извлекаем команды из текста
        commands = self._extract_commands(response_text)
        
        if not commands:
            logger.info("No commands found in response")
            return response_text, []
        
        logger.info(f"Found {len(commands)} commands to execute")
        
        # Выполняем команды
        command_results = []
        updated_response = response_text
        
        for i, command in enumerate(commands):
            logger.info(f"Executing command {i+1}/{len(commands)}: {command}")
            
            result = self._execute_command(command)
            command_results.append({
                "command": command,
                "result": result,
                "index": i
            })
            
            # Заменяем в тексте ответа информацию о выполнении
            if result["success"]:
                replacement = f"Command `{command}` executed:\n```\n{result['stdout'][:500]}{'...' if len(result.get('stdout', '')) > 500 else ''}\n```"
            else:
                replacement = f"Error executing `{command}`: {result.get('error', 'Unknown error')}"
            
            # Ищем и заменяем упоминания команды в тексте
            patterns = [
                f"`{re.escape(command)}`",
                f"команда {re.escape(command)}",
                f"выполнить {re.escape(command)}",
                re.escape(command)
            ]
            
            for pattern in patterns:
                if re.search(pattern, updated_response, re.IGNORECASE):
                    updated_response = re.sub(pattern, replacement, updated_response, count=1, flags=re.IGNORECASE)
                    break
        
        return updated_response, command_results
    
    def _extract_commands(self, text: str) -> List[str]:
        """Извлекает команды из текста ответа"""
        commands = []
        
        # Паттерны для поиска команд (исправленные)
        patterns = [
            # ПРИОРИТЕТ 1: tool_code блоки - гибкий паттерн
            r'```tool_code\s*\nbash:\s*([^\n]+)',
            # ПРИОРИТЕТ 2: Команды в блоках bash кода
            r'```(?:bash|shell|sh)\n([^\n]+)',
            # ПРИОРИТЕТ 3: Простые команды в обратных кавычках
            r'`([a-zA-Z][a-zA-Z0-9_\-\.\s/]*)`'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                command = match.group(1).strip()
                
                # Базовая фильтрация для избежания мусора
                if command and len(command.strip()) > 0:
                    command = command.strip()
                    # Убираем слишком длинные "команды" - вероятно это не команды
                    if len(command) < 200 and not any(word in command.lower() for word in ['execute', 'выполни', 'следующую']):
                        if command not in commands:  # Избегаем дублей
                            commands.append(command)
                            logger.info(f"Found command: {command}")
        
        return commands
    
    def _execute_command(self, command: str) -> Dict[str, Any]:
        """Выполняет команду с интерактивным контролем безопасности"""
        
        # Оцениваем риск команды
        risk_info = self._assess_command_risk(command)
        
        # Если команда не полностью безопасна, спрашиваем пользователя
        if risk_info.level != RiskLevel.SAFE:
            if not self._ask_user_permission(command, risk_info):
                return {
                    "success": False,
                    "error": "Выполнение отменено пользователем",
                    "stdout": "",
                    "stderr": "",
                    "user_cancelled": True
                }
        
        try:
            # Выполняем команду БЕЗ ограничений
            timeout = self._get_timeout_for_risk(risk_info.level)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Превышен таймаут выполнения ({timeout}s)",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def _build_risk_database(self) -> Dict[str, CommandRisk]:
        """Создает базу данных рисков команд"""
        return {
            # БЕЗОПАСНЫЕ команды
            'ls': CommandRisk(RiskLevel.SAFE, "Просмотр содержимого директории", "Никаких рисков"),
            'pwd': CommandRisk(RiskLevel.SAFE, "Показать текущую директорию", "Никаких рисков"),
            'whoami': CommandRisk(RiskLevel.SAFE, "Показать текущего пользователя", "Никаких рисков"),
            'date': CommandRisk(RiskLevel.SAFE, "Показать дату/время", "Никаких рисков"),
            'uname': CommandRisk(RiskLevel.SAFE, "Информация о системе", "Никаких рисков"),
            
            # НИЗКИЙ РИСК
            'cat': CommandRisk(RiskLevel.LOW, "Чтение файлов", "Может показать приватные данные"),
            'head': CommandRisk(RiskLevel.LOW, "Чтение начала файла", "Может показать приватные данные"),
            'tail': CommandRisk(RiskLevel.LOW, "Чтение конца файла", "Может показать приватные данные"),
            'grep': CommandRisk(RiskLevel.LOW, "Поиск в файлах", "Может найти приватную информацию"),
            'find': CommandRisk(RiskLevel.LOW, "Поиск файлов", "Может найти скрытые файлы"),
            'wc': CommandRisk(RiskLevel.LOW, "Подсчет строк/слов", "Может показать размеры приватных файлов"),
            
            # СРЕДНИЙ РИСК  
            'curl': CommandRisk(RiskLevel.MEDIUM, "HTTP запросы", "Может скачать вредоносные файлы или отправить данные"),
            'wget': CommandRisk(RiskLevel.MEDIUM, "Загрузка файлов", "Может скачать вредоносные файлы"),
            'python': CommandRisk(RiskLevel.MEDIUM, "Выполнение Python кода", "Может выполнить любой код"),
            'bash': CommandRisk(RiskLevel.MEDIUM, "Выполнение bash скриптов", "Может выполнить любые команды"),
            'sh': CommandRisk(RiskLevel.MEDIUM, "Выполнение shell скриптов", "Может выполнить любые команды"),
            'chmod': CommandRisk(RiskLevel.MEDIUM, "Изменение прав доступа", "Может сделать файлы исполняемыми или недоступными"),
            
            # ВЫСОКИЙ РИСК
            'rm': CommandRisk(RiskLevel.HIGH, "Удаление файлов", "НЕОБРАТИМОЕ удаление данных"),
            'sudo': CommandRisk(RiskLevel.HIGH, "Выполнение с правами root", "Полный контроль над системой"),
            'kill': CommandRisk(RiskLevel.HIGH, "Завершение процессов", "Может прервать важные процессы"),
            'killall': CommandRisk(RiskLevel.HIGH, "Завершение всех процессов по имени", "Может прервать множество процессов"),
            'chown': CommandRisk(RiskLevel.HIGH, "Изменение владельца файлов", "Может сделать файлы недоступными"),
            
            # КРИТИЧЕСКИЙ РИСК
            'format': CommandRisk(RiskLevel.CRITICAL, "Форматирование дисков", "ПОЛНАЯ ПОТЕРЯ ВСЕХ ДАННЫХ"),
            'shutdown': CommandRisk(RiskLevel.CRITICAL, "Выключение системы", "Система будет выключена"),
            'reboot': CommandRisk(RiskLevel.CRITICAL, "Перезагрузка системы", "Система будет перезагружена"),
            'halt': CommandRisk(RiskLevel.CRITICAL, "Остановка системы", "Система будет остановлена"),
        }
    
    def _assess_command_risk(self, command: str) -> CommandRisk:
        """Оценивает риск команды"""
        command_word = command.strip().split()[0].lower()
        
        # Проверяем в базе данных
        if command_word in self.risk_database:
            return self.risk_database[command_word]
        
        # Эвристическая оценка для неизвестных команд
        command_lower = command.lower()
        
        # Проверяем на потенциально опасные паттерны
        if any(pattern in command_lower for pattern in ['>', '>>', '&&', '||', ';']):
            return CommandRisk(RiskLevel.MEDIUM, "Команда с перенаправлениями", "Может изменить файлы или выполнить множественные команды")
            
        if 'sudo' in command_lower:
            return CommandRisk(RiskLevel.HIGH, "Команда с sudo", "Выполнение с правами администратора")
            
        # По умолчанию - низкий риск для неизвестных команд
        return CommandRisk(RiskLevel.LOW, "Неизвестная команда", "Риск неизвестен, но потенциально безопасная")
    
    def _get_timeout_for_risk(self, risk_level: RiskLevel) -> int:
        """Возвращает таймаут в зависимости от уровня риска"""
        timeouts = {
            RiskLevel.SAFE: 30,
            RiskLevel.LOW: 60,
            RiskLevel.MEDIUM: 120,
            RiskLevel.HIGH: 300,
            RiskLevel.CRITICAL: 600
        }
        return timeouts.get(risk_level, 60)
    
    def _ask_user_permission(self, command: str, risk_info: CommandRisk) -> bool:
        """Спрашивает разрешение пользователя с помощью GUI или консоли"""
        
        if HAS_GUI and os.environ.get('DISPLAY'):  # Если есть графический интерфейс
            return self._ask_permission_gui(command, risk_info)
        else:
            return self._ask_permission_console(command, risk_info)
    
    def _ask_permission_gui(self, command: str, risk_info: CommandRisk) -> bool:
        """Элегантный графический диалог с использованием GopiAI тем и Lucide иконок"""
        
        # Получаем или создаем QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Создаем диалог
        dialog = QDialog()
        dialog.setWindowTitle(f"Command Execution - {risk_info.level.value.upper()} Risk")
        dialog.setModal(True)
        dialog.resize(450, 200)
        
        # Применяем тему GopiAI если доступна
        if HAS_GOPIAI_THEMES:
            theme_manager = SimpleThemeManager()
            theme_manager.apply_theme_to_dialog(dialog)
        
        # Создаем layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel(f"Execute Command ({risk_info.level.value.capitalize()} Risk)")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Команда
        command_label = QLabel(f"Command: {command}")
        command_font = QFont("monospace")
        command_label.setFont(command_font)
        command_label.setWordWrap(True)
        layout.addWidget(command_label)
        
        # Описание
        desc_label = QLabel(f"Description: {risk_info.description}")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Предупреждения для опасных команд
        if risk_info.level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            warning_label = QLabel(f"Warning: {risk_info.consequences}")
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(warning_label)
            
        if risk_info.level == RiskLevel.CRITICAL:
            critical_label = QLabel("CRITICAL WARNING: This command may cause serious system damage!")
            critical_label.setWordWrap(True)
            critical_label.setStyleSheet("color: red; font-weight: bold; font-size: 11px;")
            layout.addWidget(critical_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        # Переменная для хранения результата
        result = {'value': False}
        
        def on_accept():
            result['value'] = True
            dialog.accept()
            
        def on_reject():
            result['value'] = False
            dialog.reject()
        
        # Кнопка "Да" с иконкой
        accept_button = QPushButton("Execute")
        if HAS_GOPIAI_THEMES:
            accept_icon = load_lucide_icon('check')
            if accept_icon:
                accept_button.setIcon(accept_icon)
        accept_button.clicked.connect(on_accept)
        accept_button.setDefault(False)  # Не делаем по умолчанию для безопасности
        
        # Кнопка "Нет" с иконкой  
        reject_button = QPushButton("Cancel")
        if HAS_GOPIAI_THEMES:
            reject_icon = load_lucide_icon('x')
            if reject_icon:
                reject_button.setIcon(reject_icon)
        reject_button.clicked.connect(on_reject)
        reject_button.setDefault(True)  # По умолчанию для безопасности
        
        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)
        layout.addLayout(button_layout)
        
        # Запускаем диалог
        dialog.exec()
        
        return result['value']
    
    def _ask_permission_console(self, command: str, risk_info: CommandRisk) -> bool:
        """Консольный диалог подтверждения (fallback) без эмодзи и с минимальным оформлением"""
        
        print(f"\nCommand Execution Request")
        print(f"-" * 40)
        print(f"Command: {command}")
        print(f"Risk Level: {risk_info.level.value.upper()}")
        print(f"Description: {risk_info.description}")
        
        if risk_info.level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            print(f"Warning: {risk_info.consequences}")
            
        if risk_info.level == RiskLevel.CRITICAL:
            print(f"CRITICAL WARNING: This command may cause serious system damage!")
        
        print(f"\nExecute this command?")
        
        while True:
            choice = input(f"Your choice ([y]es / [n]o): ").lower().strip()
            if choice in ['y', 'yes']:
                print(f"Command will be executed\n")
                return True
            elif choice in ['n', 'no']:
                print(f"Execution cancelled\n")
                return False
            else:
                print(f"Please enter 'y' (yes) or 'n' (no)")