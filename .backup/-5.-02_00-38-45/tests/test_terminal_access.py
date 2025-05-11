#!/usr/bin/env python
"""
Тестовый скрипт для проверки модуля TerminalAccess.

Проверяет основные функции безопасного доступа к терминалу,
в том числе выполнение Python-скриптов.
"""

import os
import sys
import asyncio
import argparse
import tempfile
from typing import List, Dict, Any

# Добавляем корень проекта в sys.path для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from app.agent.terminal_access import TerminalAccess
from app.logger import logger


async def test_python_script_execution(terminal: TerminalAccess) -> None:
    """
    Тестирует безопасное выполнение Python-скриптов.

    Args:
        terminal: Экземпляр TerminalAccess
    """
    print("\n=== Тест выполнения Python-скриптов ===\n")

    # Создаем временный Python-скрипт
    script_content = '''#!/usr/bin/env python
import sys
import os
import argparse

def main():
    print("Тестовый скрипт запущен успешно!")

    # Получаем аргументы
    parser = argparse.ArgumentParser(description="Тестовый скрипт")
    parser.add_argument("--arg1", help="Первый аргумент")
    parser.add_argument("--arg2", help="Второй аргумент")

    # Обрабатываем случай прямого вызова без аргументов
    args = parser.parse_args()

    # Выводим информацию об аргументах
    if args.arg1:
        print(f"Аргумент 1: {args.arg1}")
    if args.arg2:
        print(f"Аргумент 2: {args.arg2}")

    # Выводим переменные окружения
    if os.environ.get("TEST_VAR"):
        print(f"Переменная TEST_VAR: {os.environ.get('TEST_VAR')}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

    script_path = os.path.join(project_root, "temp_test_script.py")
    bat_script_path = os.path.join(project_root, "temp_test_script.bat")

    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        print(f"Создан временный скрипт: {script_path}")

        # Добавляем директорию к разрешенным, если она еще не разрешена
        if not terminal.is_file_access_allowed(script_path):
            terminal.add_allowed_directory(os.path.dirname(script_path))

        # Выполнение скрипта без аргументов
        print("Выполнение скрипта без аргументов:")
        result = await terminal.execute_python_script(script_path)

        print(f"  Статус: {'Успех' if result.get('success', False) else 'Ошибка'}")
        if result.get("stdout"):
            print(f"  Вывод:\n{result['stdout']}")
        if result.get("stderr"):
            print(f"  Ошибки:\n{result['stderr']}")

        # Выполнение скрипта с аргументами
        print("Выполнение скрипта с аргументами:")
        result = await terminal.execute_python_script(
            script_path,
            ["--arg1", "value1", "--arg2", "value2"]
        )

        print(f"  Статус: {'Успех' if result.get('success', False) else 'Ошибка'}")
        if result.get("stdout"):
            print(f"  Вывод:\n{result['stdout']}")
        if result.get("stderr"):
            print(f"  Ошибки:\n{result['stderr']}")

        # Проверка ограничения доступа к файлам
        print("Проверка ограничения доступа к файлам:")
        with open(bat_script_path, "w", encoding="utf-8") as f:
            f.write("@echo Test batch script\n")

        print(f"Создан недопустимый скрипт: {bat_script_path}")

        # Выполнение недопустимого скрипта
        result = await terminal.execute_python_script(bat_script_path)

        print(f"  Статус: {'Успех' if result.get('success', False) else 'Ошибка'}")
        if "error" in result:
            print(f"  Ошибка доступа (ожидаемо): {result['error']}")
        elif result.get("stderr"):
            print(f"  Ошибки:\n{result['stderr']}")

    finally:
        # Удаляем временные файлы
        if os.path.exists(script_path):
            os.remove(script_path)
        if os.path.exists(bat_script_path):
            os.remove(bat_script_path)


async def main():
    """Основная функция запуска тестов."""
    parser = argparse.ArgumentParser(description="Тест модуля TerminalAccess")
    parser.add_argument(
        "--test", "-t",
        choices=["all", "python"],
        default="all",
        help="Выбор теста для запуска"
    )
    args = parser.parse_args()

    # Создаем экземпляр TerminalAccess
    terminal = TerminalAccess(root_dir=project_root, safe_mode=True)

    # Запускаем выбранный тест
    if args.test == "all" or args.test == "python":
        await test_python_script_execution(terminal)

    print("\n=== Тесты завершены ===\n")


if __name__ == "__main__":
    asyncio.run(main())
