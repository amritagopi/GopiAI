"""
Тестирование извлечения путей из чата

Этот скрипт проверяет способность системы извлекать пути к файлам и директориям
из сообщений чата и выполнять с ними операции.
"""

import os
import asyncio
import tempfile
from pathlib import Path

from app.agent.file_system_access import FileSystemAccess
from app.agent.reasoning import ReasoningAgent
from app.logger import logger


async def test_path_extraction():
    """
    Тестирует извлечение путей из чата с использованием FileSystemAccess.
    """
    print("Тестирование извлечения путей из чата...")

    # Создаем временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем подструктуру для тестов
        docs_dir = os.path.join(temp_dir, "docs")
        code_dir = os.path.join(temp_dir, "code")
        data_dir = os.path.join(temp_dir, "data")

        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(code_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # Создаем тестовые файлы
        with open(os.path.join(docs_dir, "readme.txt"), "w") as f:
            f.write("This is a readme file.")

        with open(os.path.join(code_dir, "main.py"), "w") as f:
            f.write("print('Hello, world!')")

        with open(os.path.join(data_dir, "config.json"), "w") as f:
            f.write('{"setting": "value"}')

        # Инициализируем FileSystemAccess
        fs = FileSystemAccess(
            root_dir=temp_dir,
            safe_mode=True,
            chat_paths_enabled=True
        )

        # Добавляем разрешенные директории
        for dir_name in ["docs", "code", "data"]:
            fs.ALLOWED_DIRS.append(os.path.join(temp_dir, dir_name))

        # Тестовые сообщения
        messages = [
            "Проверь файл readme.txt в директории docs.",
            "Можешь запустить main.py из папки code?",
            "Посмотри содержимое файла data/config.json.",
            "Проверь директорию \"docs\" и файл 'code/main.py'.",
            "В папке docs должен быть файл readme.txt.",
            "Файл: readme.txt, директория: code",
            "Можешь проверить файл (docs/readme.txt) и [data/config.json]?",
        ]

        for i, message in enumerate(messages):
            print(f"\nТест {i+1}: {message}")

            # Проверяем извлечение путей
            paths = fs.extract_all_paths_from_chat(message)
            print(f"Извлеченные пути: {paths}")

            # Проверяем извлечение файлов
            files = fs.find_files_from_chat(message)
            print(f"Найденные файлы: {files}")

            # Проверяем извлечение директорий
            dirs = fs.find_directories_from_chat(message)
            print(f"Найденные директории: {dirs}")

        # Тест с конкретным примером
        test_message = f"Проверь файл {os.path.join(docs_dir, 'readme.txt')} и директорию {code_dir}"
        print(f"\nКонкретный тест: {test_message}")

        # Проверяем извлечение путей
        paths = fs.extract_all_paths_from_chat(test_message)
        print(f"Извлеченные пути: {paths}")

        # Полная обработка сообщения
        result = await fs.process_chat_with_paths(test_message)
        print("Результат обработки:", result)


async def test_reasoning_agent_paths():
    """
    Тестирует интеграцию извлечения путей из чата с ReasoningAgent.
    """
    print("\nТестирование интеграции извлечения путей из чата с ReasoningAgent...")

    # Создаем временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем подструктуру для тестов
        workspace_dir = os.path.join(temp_dir, "workspace")
        os.makedirs(workspace_dir, exist_ok=True)

        # Создаем тестовые файлы
        with open(os.path.join(workspace_dir, "test.py"), "w") as f:
            f.write("print('Test file')")

        with open(os.path.join(workspace_dir, "data.txt"), "w") as f:
            f.write("Test data")

        # Инициализируем агента
        agent = ReasoningAgent()
        try:
            # Инициализируем агента с минимальной конфигурацией для теста
            await agent.initialize(skip_serena_check=True)

            # Модифицируем разрешенные директории в FileSystemAccess агента
            agent.file_system.ALLOWED_DIRS.append(temp_dir)
            agent.file_system.ALLOWED_DIRS.append(workspace_dir)

            # Создаем текущий план (нужен для работы разрешений)
            agent.current_plan = "Test plan for chat paths integration"

            # Одобряем план
            agent.approve_plan()

            # Тестовое сообщение с путями
            test_message = f"Проверь файл {os.path.join(workspace_dir, 'test.py')} и директорию {workspace_dir}"

            # Тестируем извлечение путей
            paths_result = await agent.extract_paths_from_chat(test_message)
            print("Результат извлечения путей:", paths_result)

            # Тестируем поиск файлов
            files_result = await agent.find_files_from_chat(test_message)
            print("Результат поиска файлов:", files_result)

            # Тестируем поиск директорий
            dirs_result = await agent.find_directories_from_chat(test_message)
            print("Результат поиска директорий:", dirs_result)

            # Тестируем установку директории
            set_dir_result = await agent.set_directory_from_chat(test_message)
            print("Результат установки директории:", set_dir_result)

            # Проверяем текущую директорию
            current_dir = agent.file_system.get_current_directory()
            print(f"Текущая директория: {current_dir}")

        finally:
            # Очищаем ресурсы агента
            await agent.cleanup()


async def main():
    """
    Основная функция для запуска тестов.
    """
    print("== Тестирование функциональности извлечения путей из чата ==\n")

    # Тест базовой функциональности FileSystemAccess
    await test_path_extraction()

    # Тест интеграции с ReasoningAgent
    await test_reasoning_agent_paths()

    print("\nТестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
