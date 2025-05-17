#!/usr/bin/env python
"""
Тестовый скрипт для проверки модуля BrowserAccess.

Проверяет основные функции безопасного доступа к браузеру:
1. Выполнение безопасных действий
2. Отклонение опасных действий
3. Навигация по веб-страницам
4. Получение состояния браузера
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

from app.agent.browser_access import BrowserAccess
from app.logger import logger


async def test_safe_navigation(browser: BrowserAccess) -> None:
    """
    Проверяет безопасную навигацию по веб-страницам.

    Args:
        browser: Экземпляр BrowserAccess
    """
    print("\n=== Тест безопасной навигации ===\n")

    # Проверяем переход на разрешенные страницы
    urls = [
        "https://www.google.com",
        "https://www.python.org",
        "https://docs.python.org/3/"
    ]

    for url in urls:
        print(f"Переход на URL: {url}")
        result = await browser.execute_action("go_to_url", url=url)

        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("error"):
            print(f"  Ошибка: {result['error']}")

        # Ждем немного для отображения страницы
        await asyncio.sleep(1)

        # Получаем текущее состояние браузера
        state = await browser.get_current_state()
        if state.get("success"):
            print(f"  Текущее состояние: URL загружен")
        else:
            print(f"  Ошибка получения состояния: {state.get('error', 'Неизвестная ошибка')}")

        print("-" * 50)


async def test_unsafe_urls(browser: BrowserAccess) -> None:
    """
    Проверяет отклонение небезопасных URL.

    Args:
        browser: Экземпляр BrowserAccess
    """
    print("\n=== Тест отклонения небезопасных URL ===\n")

    unsafe_urls = [
        "file:///etc/passwd",
        "chrome://settings",
        "about:config",
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('test')</script>"
    ]

    for url in unsafe_urls:
        print(f"Попытка перехода на небезопасный URL: {url}")
        result = await browser.execute_action("go_to_url", url=url)

        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("error"):
            print(f"  Причина отказа: {result['error']}")
        print("-" * 50)


async def test_browser_actions(browser: BrowserAccess) -> None:
    """
    Тестирует различные действия в браузере.

    Args:
        browser: Экземпляр BrowserAccess
    """
    print("\n=== Тест различных браузерных действий ===\n")

    # Переходим на тестовую страницу
    await browser.execute_action("go_to_url", url="https://www.python.org")
    await asyncio.sleep(2)  # Ждем загрузки страницы

    # Пробуем выполнить поиск
    print("Попытка ввода текста в поле поиска")
    search_result = await browser.execute_action("extract_content", goal="Find search input field")
    print(f"  Поиск поля поиска: {'Успех' if search_result['success'] else 'Ошибка'}")

    # Пробуем прокрутить страницу
    print("Прокрутка страницы вниз")
    scroll_result = await browser.execute_action("scroll_down", scroll_amount=500)
    print(f"  Прокрутка страницы: {'Успех' if scroll_result['success'] else 'Ошибка'}")
    await asyncio.sleep(1)

    # Пробуем прокрутить страницу в обратном направлении
    print("Прокрутка страницы вверх")
    scroll_up_result = await browser.execute_action("scroll_up", scroll_amount=300)
    print(f"  Прокрутка страницы вверх: {'Успех' if scroll_up_result['success'] else 'Ошибка'}")
    await asyncio.sleep(1)

    # Открываем новую вкладку
    print("Открытие новой вкладки")
    tab_result = await browser.execute_action("open_tab", url="https://docs.python.org")
    print(f"  Открытие новой вкладки: {'Успех' if tab_result['success'] else 'Ошибка'}")
    await asyncio.sleep(2)

    # Возвращаемся на предыдущую вкладку
    print("Переключение на предыдущую вкладку")
    switch_result = await browser.execute_action("switch_tab", tab_id=0)
    print(f"  Переключение вкладки: {'Успех' if switch_result['success'] else 'Ошибка'}")
    await asyncio.sleep(1)

    print("-" * 50)


async def test_unsafe_actions(browser: BrowserAccess) -> None:
    """
    Проверяет отклонение небезопасных действий.

    Args:
        browser: Экземпляр BrowserAccess
    """
    print("\n=== Тест отклонения небезопасных действий ===\n")

    unsafe_actions = [
        ("execute_script", {"script": "alert('test')"}),
        ("raw_input", {"text": "<script>alert('test')</script>"}),
        ("file_upload", {"file_path": "/etc/passwd"}),
        ("input_text", {"index": 0, "text": "<script>alert('XSS')</script>"})
    ]

    for action, params in unsafe_actions:
        print(f"Попытка выполнения небезопасного действия: {action}")
        result = await browser.execute_action(action, **params)

        print(f"  Статус: {'Успех' if result['success'] else 'Ошибка'}")
        if result.get("error"):
            print(f"  Причина отказа: {result['error']}")
        print("-" * 50)


async def test_browser_state(browser: BrowserAccess) -> None:
    """
    Тестирует получение текущего состояния браузера.

    Args:
        browser: Экземпляр BrowserAccess
    """
    print("\n=== Тест получения состояния браузера ===\n")

    # Переходим на тестовую страницу
    await browser.execute_action("go_to_url", url="https://www.python.org")
    await asyncio.sleep(2)  # Ждем загрузки страницы

    print("Получение текущего состояния браузера")
    state_result = await browser.get_current_state()
    print(f"  Получение состояния: {'Успех' if state_result['success'] else 'Ошибка'}")

    if state_result.get("success") and state_result.get("state"):
        print(f"  Текущий URL: {state_result['state'].get('current_url', 'Не удалось получить')}")
        print(f"  Заголовок страницы: {state_result['state'].get('title', 'Не удалось получить')}")

    print("Получение истории действий")
    history = browser.get_action_history()
    print(f"  Количество выполненных действий: {len(history)}")

    print("-" * 50)


async def main() -> None:
    """Основная функция запуска тестов."""
    parser = argparse.ArgumentParser(description="Тест модуля BrowserAccess")
    parser.add_argument(
        "--safe-mode",
        "-s",
        action="store_true",
        default=True,
        help="Включить режим безопасности",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Запустить браузер в headless режиме",
    )
    parser.add_argument(
        "--test",
        "-t",
        choices=["all", "safe", "unsafe", "actions", "state"],
        default="all",
        help="Выбор конкретного теста",
    )
    args = parser.parse_args()

    # Создаем экземпляр BrowserAccess
    browser = BrowserAccess(
        safe_mode=args.safe_mode,
        headless=args.headless
    )

    try:
        # Запускаем выбранные тесты
        if args.test in ["all", "safe"]:
            await test_safe_navigation(browser)

        if args.test in ["all", "unsafe"]:
            await test_unsafe_urls(browser)

        if args.test in ["all", "actions"]:
            await test_browser_actions(browser)

        if args.test in ["all", "unsafe"]:
            await test_unsafe_actions(browser)

        if args.test in ["all", "state"]:
            await test_browser_state(browser)

    except Exception as e:
        print(f"Ошибка при выполнении тестов: {str(e)}")
    finally:
        # Освобождаем ресурсы браузера
        await browser.cleanup()

    print("\n=== Тесты завершены ===\n")


if __name__ == "__main__":
    asyncio.run(main())
