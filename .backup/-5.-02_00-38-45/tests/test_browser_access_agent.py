"""
Тестирование BrowserAccessAgent

Проверяет работу BrowserAccessAgent и интеграцию с браузером
для обеспечения безопасной работы с веб-страницами.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.browser_access_agent import BrowserAccessAgent
from app.agent.permission_manager import PermissionManager, PermissionLevel, ActionCategory


class BrowserAccessAgentTester:
    """Класс для тестирования агента с браузерным доступом"""

    def __init__(self):
        """Инициализирует тестовый класс"""
        self.agent = None
        self.test_results = []
        self.permission_manager = None

    async def setup(self):
        """Настраивает тестовое окружение"""
        print("\n=== Setting up BrowserAccessAgent test environment ===")

        try:
            # Создаем агента
            self.agent = BrowserAccessAgent()

            # Инициализируем агента с пропуском проверки Serena для тестирования
            await self.agent.initialize(skip_serena_check=True)

            # Устанавливаем наш mock permission manager
            self.permission_manager = MockPermissionManager()
            self.agent.permission_manager = self.permission_manager

            print("Setup completed successfully")
            return True
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return False

    async def teardown(self):
        """Освобождает ресурсы после тестирования"""
        print("\n=== Tearing down test environment ===")

        if self.agent:
            try:
                await self.agent.cleanup()
                print("Teardown completed successfully")
            except Exception as e:
                print(f"Teardown error: {str(e)}")

    async def test_initialize(self):
        """Тестирует инициализацию агента"""
        print("\n=== Testing BrowserAccessAgent initialization ===")

        # Проверяем, что агент был правильно инициализирован
        is_initialized = self.agent is not None
        is_browser_access_initialized = hasattr(self.agent, 'browser_access') and self.agent.browser_access is not None

        self.test_results.append(("Browser agent initialization",
                                is_initialized and is_browser_access_initialized))

        print(f"Agent initialized: {is_initialized}")
        print(f"Browser access initialized: {is_browser_access_initialized}")

    async def test_browser_navigation(self):
        """Тестирует навигацию в браузере"""
        print("\n=== Testing browser navigation ===")

        # Устанавливаем разрешение для этого теста
        self.permission_manager.approved_actions.append(
            ("browser_use", {"action": "go_to_url", "url": "https://example.com"})
        )

        # Одобряем план (без этого действия будут блокироваться)
        self.agent.approve_plan()

        # Выполняем навигацию
        result = await self.agent.navigate_to_url("https://example.com")

        # Проверяем результат (код будет фиктивным, так как браузер не запускается в тестах)
        has_url = "url" in result

        self.test_results.append(("Browser navigation", has_url))

        print(f"Navigation result: {result}")

    async def test_browser_interaction(self):
        """Тестирует взаимодействие с элементами веб-страницы"""
        print("\n=== Testing browser interactions ===")

        # Устанавливаем разрешения для этого теста
        self.permission_manager.approved_actions.append(
            ("browser_use", {"action": "click", "selector": ".button"})
        )
        self.permission_manager.approved_actions.append(
            ("browser_use", {"action": "input_text", "selector": ".input-field"})
        )

        # Выполняем действия (без реального браузера, тестируем только API)
        click_result = await self.agent.click_element(".button")
        input_result = await self.agent.input_text(".input-field", "test input")

        # Проверяем результаты
        self.test_results.append(("Browser click element", "selector" in click_result))
        self.test_results.append(("Browser input text", "selector" in input_result))

        print(f"Click result: {click_result}")
        print(f"Input result: {input_result}")

    async def test_browser_content_extraction(self):
        """Тестирует извлечение содержимого страницы"""
        print("\n=== Testing content extraction ===")

        # Выполняем действия (без разрешений, так как это безопасные операции чтения)
        extract_result = await self.agent.extract_content("body")

        # Проверяем результаты
        self.test_results.append(("Content extraction", "selector" in extract_result))

        print(f"Extract content result: {extract_result}")

    async def test_browser_plan(self):
        """Тестирует создание и выполнение плана для браузера"""
        print("\n=== Testing browser plan creation ===")

        # Создаем план
        plan = await self.agent.prepare_browser_plan("Найти информацию о Python на сайте example.com")

        # Проверяем наличие плана
        has_plan = len(plan) > 0

        self.test_results.append(("Browser plan creation", has_plan))

        print(f"Created plan: {plan[:200]}...")

    async def run_tests(self):
        """Запускает все тесты"""
        setup_success = await self.setup()
        if not setup_success:
            print("Cannot run tests due to setup failure")
            return

        try:
            await self.test_initialize()
            await self.test_browser_navigation()
            await self.test_browser_interaction()
            await self.test_browser_content_extraction()
            await self.test_browser_plan()

            # Выводим результаты
            print("\n=== Test Results ===")
            for i, (test_name, result) in enumerate(self.test_results, 1):
                status = "PASSED" if result else "FAILED"
                print(f"{i}. {test_name}: {status}")

            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            print(f"\nPassed {passed}/{total} tests ({passed/total*100:.1f}%)")

        finally:
            await self.teardown()


class MockPermissionManager:
    """Mock-класс менеджера разрешений для тестирования"""

    def __init__(self):
        """Инициализирует mock-менеджер разрешений"""
        self.approved_actions = []
        self.action_log = []
        self._has_approved_plan = False

    def approve_plan(self):
        """Одобряет план"""
        self._has_approved_plan = True

    def reject_plan(self):
        """Отклоняет план"""
        self._has_approved_plan = False

    def is_plan_approved(self):
        """Проверяет, одобрен ли план"""
        return self._has_approved_plan

    def request_permission(self, tool_name: str, args: Dict[str, Any], reason: str = ""):
        """
        Обрабатывает запрос на разрешение действия.

        Args:
            tool_name: Имя инструмента
            args: Аргументы инструмента
            reason: Причина запроса разрешения

        Returns:
            Объект с информацией об одобрении запроса
        """
        # Регистрируем запрос
        self.action_log.append({
            "tool_name": tool_name,
            "args": args,
            "reason": reason
        })

        # Проверяем одобрение плана
        if not self._has_approved_plan:
            return RequestResponse(False, "No approved plan")

        # Проверяем, включено ли действие в список одобренных
        for approved_tool, approved_args in self.approved_actions:
            if tool_name == approved_tool:
                # Проверяем аргументы
                args_match = True
                for key, value in approved_args.items():
                    if key in args and args[key] != value:
                        args_match = False
                        break

                if args_match:
                    return RequestResponse(True, "Action approved")

        return RequestResponse(False, "Action not in approved list")


class RequestResponse:
    """Класс-ответ для запросов на разрешение"""

    def __init__(self, approved: bool, message: str):
        self.approved = approved
        self.message = message


async def main():
    """Главная функция для запуска тестов"""
    print("=== Starting BrowserAccessAgent Tests ===")

    tester = BrowserAccessAgentTester()
    await tester.run_tests()


if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(main())
