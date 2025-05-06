"""
Тестирование системы разрешений Reasoning Agent

Проверяет работу PermissionManager и интеграцию с ReasoningAgent
для обеспечения безопасности выполнения действий.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.permission_manager import PermissionManager, PermissionLevel, ActionCategory
from app.agent.reasoning import ReasoningAgent
from app.ui.plan_view_widget import PlanViewWidget
from app.ui.reasoning_agent_dialog import ReasoningAgentDialog
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from app.ui.i18n.translator import tr


class PermissionManagerTest:
    """Класс для тестирования менеджера разрешений"""

    def __init__(self):
        """Инициализирует тестовый класс"""
        self.permission_manager = PermissionManager()
        self.test_results = []

        # Устанавливаем обработчик разрешений для тестов
        self.permission_manager.set_permission_handler(self.mock_permission_handler)

        # Одобренные запросы для тестов
        self.approved_actions = [
            ("read_test.py", ActionCategory.FILE_READ),
            ("git add .", ActionCategory.TERMINAL_COMMAND),
            ("https://api.example.com", ActionCategory.NETWORK_REQUEST)
        ]

    def mock_permission_handler(self, action: str, category: ActionCategory,
                              risk_level: PermissionLevel, explanation: str) -> bool:
        """
        Тестовый обработчик запросов разрешений.

        Args:
            action: Действие
            category: Категория
            risk_level: Уровень риска
            explanation: Пояснение

        Returns:
            True если действие одобрено, иначе False
        """
        print(f"Request permission for: {category.value}:{action}")
        print(f"Risk level: {risk_level.name}")
        print(f"Explanation: {explanation}")

        # Одобряем только те действия, которые в списке одобренных
        for approved_action, approved_category in self.approved_actions:
            if action == approved_action and category == approved_category:
                return True

        # По умолчанию не одобряем
        return False

    def run_tests(self):
        """Запускает все тесты"""
        self.test_permission_levels()
        self.test_plan_approval()
        self.test_risk_explanations()
        self.test_action_permissions()
        self.test_plan_risk_analysis()

        # Выводим результаты
        print("\n=== Test Results ===")
        for i, (test_name, result) in enumerate(self.test_results, 1):
            status = "PASSED" if result else "FAILED"
            print(f"{i}. {test_name}: {status}")

        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        print(f"\nPassed {passed}/{total} tests ({passed/total*100:.1f}%)")

    def test_permission_levels(self):
        """Тестирует определение уровней разрешений"""
        print("\n=== Testing Permission Levels ===")

        # Тесты для файловых операций
        read_py_level = self.permission_manager.evaluate_risk("test.py", ActionCategory.FILE_READ)
        read_config_level = self.permission_manager.evaluate_risk("app.config", ActionCategory.FILE_READ)
        read_password_level = self.permission_manager.evaluate_risk("password.txt", ActionCategory.FILE_READ)

        # Тесты для команд терминала
        ls_level = self.permission_manager.evaluate_risk("ls", ActionCategory.TERMINAL_COMMAND)
        pip_level = self.permission_manager.evaluate_risk("pip install", ActionCategory.TERMINAL_COMMAND)
        rm_level = self.permission_manager.evaluate_risk("rm -rf", ActionCategory.TERMINAL_COMMAND)

        # Проверка результатов
        self.test_results.append(("File read permission levels",
                                read_py_level == PermissionLevel.LOW_RISK and
                                read_config_level == PermissionLevel.MEDIUM_RISK and
                                read_password_level == PermissionLevel.HIGH_RISK))

        self.test_results.append(("Terminal command permission levels",
                                ls_level == PermissionLevel.LOW_RISK and
                                pip_level == PermissionLevel.MEDIUM_RISK and
                                rm_level == PermissionLevel.HIGH_RISK))

        print(f"Read .py file: {read_py_level.name}")
        print(f"Read config file: {read_config_level.name}")
        print(f"Read password file: {read_password_level.name}")
        print(f"ls command: {ls_level.name}")
        print(f"pip install command: {pip_level.name}")
        print(f"rm -rf command: {rm_level.name}")

    def test_plan_approval(self):
        """Тестирует настройку одобрения плана"""
        print("\n=== Testing Plan Approval ===")

        # Исходное состояние
        initial_state = self.permission_manager.is_plan_approved()

        # Одобряем план
        self.permission_manager.set_plan_approved(True)
        approved_state = self.permission_manager.is_plan_approved()

        # Отклоняем план
        self.permission_manager.set_plan_approved(False)
        rejected_state = self.permission_manager.is_plan_approved()

        # Проверка результатов
        self.test_results.append(("Plan approval state changes",
                                initial_state == False and
                                approved_state == True and
                                rejected_state == False))

        print(f"Initial state: {initial_state}")
        print(f"After approval: {approved_state}")
        print(f"After rejection: {rejected_state}")

    def test_risk_explanations(self):
        """Тестирует генерацию объяснений рисков"""
        print("\n=== Testing Risk Explanations ===")

        # Генерируем объяснения для разных действий
        file_read_exp = self.permission_manager.generate_risk_explanation(
            "test.py", ActionCategory.FILE_READ)

        file_delete_exp = self.permission_manager.generate_risk_explanation(
            "important.json", ActionCategory.FILE_DELETE)

        terminal_exp = self.permission_manager.generate_risk_explanation(
            "sudo rm -rf", ActionCategory.TERMINAL_COMMAND)

        # Проверка результатов
        self.test_results.append(("Risk explanations generation",
                                len(file_read_exp) > 0 and
                                len(file_delete_exp) > 0 and
                                len(terminal_exp) > 0))

        print("File read explanation:")
        print(file_read_exp)
        print("\nFile delete explanation:")
        print(file_delete_exp)
        print("\nTerminal command explanation:")
        print(terminal_exp)

    def test_action_permissions(self):
        """Тестирует запросы разрешений на действия"""
        print("\n=== Testing Action Permissions ===")

        # Сначала с неодобренным планом
        self.permission_manager.set_plan_approved(False)

        no_plan_allowed = self.permission_manager.request_permission(
            "test.py", ActionCategory.FILE_READ, "Нужно прочитать файл")

        # Теперь с одобренным планом
        self.permission_manager.set_plan_approved(True)

        # Низкий риск должен автоматически разрешаться
        low_risk_allowed = self.permission_manager.request_permission(
            "test.py", ActionCategory.FILE_READ, "Нужно прочитать файл")

        # Средний риск должен запрашивать разрешение
        medium_risk_allowed = self.permission_manager.request_permission(
            "git add .", ActionCategory.TERMINAL_COMMAND, "Добавление файлов в git")

        medium_risk_denied = self.permission_manager.request_permission(
            "pip install package", ActionCategory.TERMINAL_COMMAND, "Установка пакета")

        # Высокий риск должен запрашивать разрешение
        high_risk_denied = self.permission_manager.request_permission(
            "rm -rf *", ActionCategory.TERMINAL_COMMAND, "Удаление всех файлов")

        # Проверка результатов
        self.test_results.append(("Action permissions with/without plan",
                                no_plan_allowed == False and
                                low_risk_allowed == True and
                                medium_risk_allowed == True and
                                medium_risk_denied == False and
                                high_risk_denied == False))

        print(f"Without plan approval, low risk: {no_plan_allowed}")
        print(f"With plan approval, low risk: {low_risk_allowed}")
        print(f"With plan approval, medium risk (approved): {medium_risk_allowed}")
        print(f"With plan approval, medium risk (denied): {medium_risk_denied}")
        print(f"With plan approval, high risk (denied): {high_risk_denied}")

    def test_plan_risk_analysis(self):
        """Тестирует анализ рисков плана"""
        print("\n=== Testing Plan Risk Analysis ===")

        # Создаем тестовый план
        test_plan = {
            "task": "Тестовая задача",
            "steps": [
                {
                    "id": 1,
                    "title": "Чтение файла",
                    "category": "file_read",
                    "action": "test.py"
                },
                {
                    "id": 2,
                    "title": "Запись в файл",
                    "category": "file_write",
                    "action": "config.json"
                },
                {
                    "id": 3,
                    "title": "Удаление файла",
                    "category": "file_delete",
                    "action": "important.py"
                }
            ]
        }

        # Анализируем риски
        risk_analysis = self.permission_manager.analyze_plan_risks(test_plan)

        # Проверяем результаты
        has_overall_risk = "overall_risk_level" in risk_analysis
        has_steps_risk = "steps_risk" in risk_analysis and len(risk_analysis["steps_risk"]) == 3
        has_risk_summary = "risk_summary" in risk_analysis
        overall_risk_high = risk_analysis["overall_risk_level"] == PermissionLevel.HIGH_RISK

        self.test_results.append(("Plan risk analysis",
                                has_overall_risk and has_steps_risk and
                                has_risk_summary and overall_risk_high))

        print(f"Overall risk level: {risk_analysis['overall_risk_level'].name}")
        print(f"Steps risk count: {len(risk_analysis['steps_risk'])}")
        print(f"Risk summary: {risk_analysis['risk_summary']}")


class PlanViewTest(QWidget):
    """Тест для проверки виджета представления плана"""

    def __init__(self):
        """Инициализирует тестовое окно"""
        super().__init__()
        self.setWindowTitle(tr("test.plan_view", "План - Тестовый просмотр"))
        self.setGeometry(100, 100, 1000, 800)

        layout = QVBoxLayout()

        # Создаем компонент
        self.plan_view = PlanViewWidget()

        # Кнопки для тестов
        test_plan_button = QPushButton(tr("test.test_plan", "Тестовый план"))
        test_plan_button.clicked.connect(self.show_test_plan)

        complex_plan_button = QPushButton(tr("test.complex_plan", "Сложный план"))
        complex_plan_button.clicked.connect(self.show_complex_plan)

        high_risk_plan_button = QPushButton(tr("test.high_risk_plan", "План высокого риска"))
        high_risk_plan_button.clicked.connect(self.show_high_risk_plan)

        clear_button = QPushButton(tr("test.clear_plan", "Очистить план"))
        clear_button.clicked.connect(self.plan_view.clear)

        # Добавляем элементы на форму
        layout.addWidget(QLabel(tr("test.plan_view_test", "Тест виджета просмотра плана")))
        layout.addWidget(test_plan_button)
        layout.addWidget(complex_plan_button)
        layout.addWidget(high_risk_plan_button)
        layout.addWidget(clear_button)
        layout.addWidget(self.plan_view)

        self.setLayout(layout)

        # Подключаем сигналы
        self.plan_view.plan_approved.connect(lambda: print("Plan approved"))
        self.plan_view.plan_rejected.connect(lambda: print("Plan rejected"))
        self.plan_view.step_details_requested.connect(
            lambda step_id: print(f"Details requested for step {step_id+1}"))

    def show_test_plan(self):
        """Показывает тестовый план"""
        test_plan = {
            "task": "Создать класс для работы с файловой системой",
            "steps": [
                {
                    "title": "Изучить требования",
                    "description": "Анализ требований к классу и его функциональности",
                    "risk_level": "low",
                    "tools": ["codebase_search", "read_file"]
                },
                {
                    "title": "Создать файл класса",
                    "description": "Создание файла file_system.py с базовой структурой класса FileSystem",
                    "risk_level": "medium",
                    "tools": ["edit_file"]
                },
                {
                    "title": "Реализовать методы",
                    "description": "Добавление основных методов для работы с файлами",
                    "risk_level": "medium",
                    "tools": ["edit_file", "run_terminal_cmd"]
                }
            ],
            "risks": {
                "Нарушение существующего функционала": "Провести тщательное тестирование",
                "Проблемы с доступом к файлам": "Добавить обработку исключений",
                "Потенциальные утечки памяти": "Реализовать корректное закрытие файловых дескрипторов"
            }
        }

        self.plan_view.set_plan(test_plan)

    def show_complex_plan(self):
        """Показывает сложный тестовый план"""
        complex_plan = {
            "task": "Реализовать систему кэширования для улучшения производительности",
            "steps": [
                {
                    "title": "Анализ требований к кэшированию",
                    "description": "Определение типов данных для кэширования, времени жизни кэша, стратегии инвалидации кэша и требований к производительности.",
                    "risk_level": "low",
                    "tools": ["codebase_search", "read_file"]
                },
                {
                    "title": "Выбор стратегии кэширования",
                    "description": "Выбор между in-memory кэшированием, файловым кэшем или распределенным кэшем (Redis, Memcached). Определение структуры ключей кэша и политики вытеснения.",
                    "risk_level": "low",
                    "tools": ["web_search", "codebase_search"]
                },
                {
                    "title": "Создание интерфейса кэширования",
                    "description": "Разработка абстрактного интерфейса кэширования с методами get(), set(), invalidate() и clear().",
                    "risk_level": "medium",
                    "tools": ["edit_file", "read_file"]
                },
                {
                    "title": "Реализация базового кэша в памяти",
                    "description": "Создание класса MemoryCache, реализующего интерфейс кэширования с использованием словаря в памяти. Добавление поддержки TTL (Time To Live) для записей кэша.",
                    "risk_level": "medium",
                    "tools": ["edit_file", "run_terminal_cmd"]
                },
                {
                    "title": "Реализация кэширования файлов",
                    "description": "Создание класса FileCache, сохраняющего кэш на диск с сериализацией данных.",
                    "risk_level": "high",
                    "tools": ["edit_file", "run_terminal_cmd"]
                },
                {
                    "title": "Интеграция с существующим кодом",
                    "description": "Добавление декоратора @cached для функций и методов, а также создание кэш-прослойки для ключевых мест приложения.",
                    "risk_level": "high",
                    "tools": ["codebase_search", "edit_file"]
                },
                {
                    "title": "Тестирование производительности",
                    "description": "Написание бенчмарков для сравнения производительности до и после внедрения кэширования.",
                    "risk_level": "low",
                    "tools": ["edit_file", "run_terminal_cmd"]
                }
            ],
            "risks": {
                "Утечка памяти": "Установить максимальный размер кэша и автоматическую очистку старых записей",
                "Несогласованность данных": "Реализовать механизм инвалидации кэша при изменении данных",
                "Повышенное использование диска": "Мониторинг размера файлового кэша и периодическая очистка",
                "Влияние на производительность": "Тщательное тестирование до внедрения в production",
                "Сложность отладки": "Добавить логирование операций кэша и возможность отключения кэширования"
            }
        }

        self.plan_view.set_plan(complex_plan)

    def show_high_risk_plan(self):
        """Показывает план с высоким уровнем риска"""
        high_risk_plan = {
            "task": "Рефакторинг системы аутентификации",
            "steps": [
                {
                    "title": "Анализ существующего кода аутентификации",
                    "description": "Изучение текущей реализации аутентификации и выявление проблем.",
                    "risk_level": "low",
                    "tools": ["codebase_search", "read_file"]
                },
                {
                    "title": "Разработка новой структуры для хранения учетных данных",
                    "description": "Создание улучшенной схемы базы данных для хранения пользовательских данных с усиленной безопасностью.",
                    "risk_level": "high",
                    "tools": ["edit_file", "grep_search"]
                },
                {
                    "title": "Изменение алгоритма хеширования паролей",
                    "description": "Переход с MD5 на Argon2id или bcrypt для безопасного хранения паролей.",
                    "risk_level": "critical",
                    "tools": ["edit_file", "web_search"]
                },
                {
                    "title": "Миграция существующих пользовательских данных",
                    "description": "Скрипт для безопасной миграции существующих пользовательских учетных данных в новую структуру с перехешированием паролей.",
                    "risk_level": "critical",
                    "tools": ["edit_file", "run_terminal_cmd"]
                },
                {
                    "title": "Обновление механизма сессий и токенов",
                    "description": "Реализация JWT-токенов с ротацией и механизмом отзыва.",
                    "risk_level": "high",
                    "tools": ["edit_file"]
                },
                {
                    "title": "Добавление двухфакторной аутентификации",
                    "description": "Интеграция с сервисами 2FA или реализация собственного решения с TOTP.",
                    "risk_level": "medium",
                    "tools": ["edit_file", "web_search"]
                }
            ],
            "risks": {
                "Потеря доступа пользователей к аккаунтам": "Создать механизм восстановления доступа и предусмотреть откат изменений",
                "Уязвимости в безопасности": "Провести аудит безопасности и тестирование на проникновение",
                "Несовместимость с существующими клиентами": "Поддерживать старые методы аутентификации параллельно с новыми",
                "Прерывание работы сервиса": "Выполнять миграцию в нерабочее время и иметь план отката",
                "Утечка конфиденциальных данных": "Усилить шифрование и ограничить доступ к данным во время миграции"
            }
        }

        self.plan_view.set_plan(high_risk_plan)


async def main():
    """Главная функция для запуска тестов"""
    print("=== Permission Manager Tests ===")
    permission_test = PermissionManagerTest()
    permission_test.run_tests()

    # Запускаем тестирование UI
    print("\n=== Plan View Widget Test ===")
    print("Starting GUI test - close the window to continue")

    ui_test = PlanViewTest()
    ui_test.show()

    # Ждем, пока пользователь закроет окно
    while ui_test.isVisible():
        await asyncio.sleep(0.1)

    print("All tests completed!")


if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(main())
