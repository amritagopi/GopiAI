#!/usr/bin/env python
"""
Тестовый скрипт для проверки модуля TerminalAccess.

Проверяет основные функции безопасного доступа к терминалу:
1. Выполнение безопасных команд
2. Отклонение опасных команд
3. Управление рабочими директориями
"""

import os
import sys
import asyncio
import argparse
from typing import List, Dict, Any

# Добавляем корень проекта в sys.path для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from app.agent.terminal_access import TerminalAccess
from app.logger import logger


async def test_basic_commands(terminal: TerminalAccess) -> None:
    """
    Проверяет выполнение базовых безопасных команд.

    Args:
        terminal: Экземпляр TerminalAccess
    """
    print("\n=== Тест выполнения базовых команд ===\n")

    commands = [
        "echo Hello World",
        "dir" if sys.platform == "win32" else "ls -la",
        "python --version",
        "pwd" if sys.platform != "win32" else "cd",
    ]

    for cmd in commands:
        print(f"Выполнение команды: {cmd}")
        result = await terminal.execute_command(cmd)

        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("stdout"):
            print(f"  Вывод:\n{result['stdout']}")
        if result.get("stderr") and result["stderr"]:
            print(f"  Ошибки:\n{result['stderr']}")
        print("-" * 50)


async def test_unsafe_commands(terminal: TerminalAccess) -> None:
    """
    Проверяет отклонение небезопасных команд.

    Args:
        terminal: Экземпляр TerminalAccess
    """
    print("\n=== Тест отклонения небезопасных команд ===\n")

    unsafe_commands = [
        "rm -rf /",  # Опасная команда удаления всего
        "DROP TABLE users",  # SQL запрос
        "sudo rm file.txt",  # Использование sudo
        "../../../etc/passwd",  # Попытка выхода за пределы директории
        ":() { :|:& };:",  # Fork bomb
    ]

    for cmd in unsafe_commands:
        print(f"Попытка выполнения небезопасной команды: {cmd}")
        result = await terminal.execute_command(cmd)

        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("stderr") and result["stderr"]:
            print(f"  Причина отказа: {result['stderr']}")
        print("-" * 50)


async def test_directory_navigation(terminal: TerminalAccess) -> None:
    """
    Тестирует навигацию по директориям.

    Args:
        terminal: Экземпляр TerminalAccess
    """
    print("\n=== Тест навигации по директориям ===\n")

    # Получаем текущую директорию
    current_dir = terminal.get_current_directory()
    print(f"Текущая директория: {current_dir}")

    # Переходим в разрешенную директорию
    new_dir = os.path.join(project_root, "app")
    print(f"Переход в директорию: {new_dir}")

    success = terminal.set_current_directory(new_dir)
    if success:
        print(f"Успешно установлена директория: {terminal.get_current_directory()}")
    else:
        print(f"Ошибка установки директории")

    # Пробуем перейти через cd
    result = await terminal.execute_command("cd ..")
    print(f"Переход через команду cd: {result['success']}")
    print(f"Текущая директория после cd: {terminal.get_current_directory()}")

    # Пробуем перейти в неразрешенную директорию
    bad_dir = os.path.abspath("/tmp") if sys.platform != "win32" else "C:\\Windows\\System32"
    print(f"Попытка перехода в запрещенную директорию: {bad_dir}")

    success = terminal.set_current_directory(bad_dir)
    if not success:
        print("Доступ к директории правильно запрещен")
    else:
        print(f"Ошибка: получен доступ к запрещенной директории: {terminal.get_current_directory()}")

    print("-" * 50)


async def test_command_timeouts(terminal: TerminalAccess) -> None:
    """
    Тестирует тайм-ауты при выполнении команд.

    Args:
        terminal: Экземпляр TerminalAccess
    """
    print("\n=== Тест тайм-аутов команд ===\n")

    # Команда со сном на 5 секунд
    sleep_cmd = "timeout 5" if sys.platform != "win32" else "ping -n 5 127.0.0.1"

    # Выполняем с таймаутом 2 секунды
    print(f"Выполнение команды с тайм-аутом 2 секунды: {sleep_cmd}")
    result = await terminal.execute_command(sleep_cmd, timeout=2.0)

    if result.get("error") == "Timeout":
        print("Тайм-аут правильно сработал")
    else:
        print(f"Ошибка: команда должна была вызвать тайм-аут, но завершилась с результатом:")
        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("stdout"):
            print(f"  Вывод:\n{result['stdout']}")

    # Выполняем с достаточным таймаутом
    print(f"Выполнение команды с тайм-аутом 10 секунд: {sleep_cmd}")
    result = await terminal.execute_command(sleep_cmd, timeout=10.0)

    if not result.get("error") == "Timeout":
        print("Команда успешно выполнена без тайм-аута")
    else:
        print("Ошибка: команда вызвала тайм-аут с достаточным временем ожидания")

    print("-" * 50)


async def main() -> None:
    """Основная функция запуска тестов."""
    parser = argparse.ArgumentParser(description="Тест модуля TerminalAccess")
    parser.add_argument(
        "--safe-mode",
        "-s",
        action="store_true",
        default=True,
        help="Включить режим безопасности",
    )
    parser.add_argument(
        "--test",
        "-t",
        choices=["all", "basic", "unsafe", "directory", "timeout"],
        default="all",
        help="Выбор конкретного теста",
    )
    args = parser.parse_args()

    # Создаем экземпляр с текущей директорией проекта
    terminal = TerminalAccess(
        root_dir=project_root,
        safe_mode=args.safe_mode
    )

    try:
        if args.test in ["all", "basic"]:
            await test_basic_commands(terminal)

        if args.test in ["all", "unsafe"]:
            await test_unsafe_commands(terminal)

        if args.test in ["all", "directory"]:
            await test_directory_navigation(terminal)

        if args.test in ["all", "timeout"]:
            await test_command_timeouts(terminal)

    except Exception as e:
        print(f"Ошибка при выполнении тестов: {str(e)}")

    print("\n=== Тесты завершены ===\n")


if __name__ == "__main__":
    asyncio.run(main())
