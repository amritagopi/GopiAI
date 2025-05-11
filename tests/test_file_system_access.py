#!/usr/bin/env python
"""
Тестовый скрипт для проверки модуля FileSystemAccess.

Проверяет основные функции безопасного доступа к файловой системе:
1. Чтение и запись файлов
2. Отклонение опасных путей
3. Работа с директориями
4. Получение информации о файлах
5. Поддержка путей из чата
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

from app.agent.file_system_access import FileSystemAccess
from app.logger import logger


async def test_directory_operations(fs: FileSystemAccess) -> None:
    """
    Проверяет операции с директориями.

    Args:
        fs: Экземпляр FileSystemAccess
    """
    print("\n=== Тест операций с директориями ===\n")

    # Проверяем получение текущей директории
    current_dir = fs.get_current_directory()
    print(f"Текущая директория: {current_dir}")

    # Проверяем список файлов
    workspace_dir = os.path.join(project_root, "workspace")
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir, exist_ok=True)
        print(f"Создана директория workspace: {workspace_dir}")

    # Создаем тестовый файл во временной директории
    test_file_path = os.path.join(workspace_dir, "test_fs_access.txt")
    with open(test_file_path, "w") as f:
        f.write("Тестовый файл для FileSystemAccess")

    # Проверяем установку директории
    print(f"Установка рабочей директории: {workspace_dir}")
    result = fs.set_current_directory(workspace_dir)
    print(f"  Результат: {'Успех' if result else 'Ошибка'}")
    print(f"  Новая директория: {fs.get_current_directory()}")

    # Проверяем получение списка файлов
    print("\nСписок файлов в директории:")
    dir_result = await fs.list_directory(".")
    if dir_result["success"]:
        print(f"  Директории: {dir_result['directories']}")
        print(f"  Файлы: {dir_result['files']}")
    else:
        print(f"  Ошибка: {dir_result['error']}")

    # Проверяем рекурсивное получение файлов
    print("\nРекурсивный список файлов:")
    recursive_result = await fs.list_directory(".", recursive=True)
    if recursive_result["success"]:
        print(f"  Количество директорий: {len(recursive_result['directories'])}")
        print(f"  Количество файлов: {len(recursive_result['files'])}")
    else:
        print(f"  Ошибка: {recursive_result['error']}")

    # Проверяем получение информации о директории
    print("\nИнформация о директории:")
    info_result = await fs.get_file_info(".")
    if info_result["success"]:
        print(f"  Имя: {info_result['name']}")
        print(f"  Директория: {info_result['is_dir']}")
        print(f"  Дата изменения: {info_result['modified']}")
    else:
        print(f"  Ошибка: {info_result['error']}")

    print("-" * 50)


async def test_file_operations(fs: FileSystemAccess) -> None:
    """
    Проверяет операции с файлами.

    Args:
        fs: Экземпляр FileSystemAccess
    """
    print("\n=== Тест операций с файлами ===\n")

    # Проверяем запись в файл
    workspace_dir = os.path.join(project_root, "workspace")
    test_file = os.path.join(workspace_dir, "test_file_write.txt")
    test_content = "Это тестовый файл для проверки записи.\nВторая строка."

    print(f"Запись в файл: {test_file}")
    write_result = await fs.write_file(test_file, test_content)
    print(f"  Результат: {'Успех' if write_result['success'] else 'Ошибка'}")
    if not write_result["success"]:
        print(f"  Ошибка: {write_result['error']}")

    # Проверяем чтение файла
    print(f"Чтение файла: {test_file}")
    read_result = await fs.read_file(test_file)
    if read_result["success"]:
        print(f"  Размер файла: {read_result['size']} байт")
        print(f"  Содержимое: {read_result['content'][:50]}...")
    else:
        print(f"  Ошибка: {read_result['error']}")

    # Проверяем получение информации о файле
    print(f"Информация о файле: {test_file}")
    info_result = await fs.get_file_info(test_file)
    if info_result["success"]:
        print(f"  Имя: {info_result['name']}")
        print(f"  Размер: {info_result['size']} байт")
        print(f"  Расширение: {info_result['extension']}")
    else:
        print(f"  Ошибка: {info_result['error']}")

    # Проверяем удаление файла
    print(f"Удаление файла: {test_file}")
    delete_result = await fs.delete_file(test_file)
    print(f"  Результат: {'Успех' if delete_result['success'] else 'Ошибка'}")
    if not delete_result["success"]:
        print(f"  Ошибка: {delete_result['error']}")

    # Проверяем, что файл действительно удален
    print(f"Проверка удаления файла: {test_file}")
    exists = os.path.exists(test_file)
    print(f"  Файл существует: {exists}")

    print("-" * 50)


async def test_unsafe_paths(fs: FileSystemAccess) -> None:
    """
    Проверяет отклонение небезопасных путей.

    Args:
        fs: Экземпляр FileSystemAccess
    """
    print("\n=== Тест отклонения небезопасных путей ===\n")

    unsafe_paths = [
        "../../../etc/passwd",
        "C:\\Windows\\System32\\cmd.exe",
        "./app/../../../Windows/win.ini",
        "../../malicious.exe",
        "./.git/config"
    ]

    for path in unsafe_paths:
        print(f"Попытка чтения из небезопасного пути: {path}")
        result = await fs.read_file(path)
        print(f"  Результат: {'Успех' if result['success'] else 'Ошибка'}")
        if not result["success"]:
            print(f"  Причина отказа: {result['error']}")

        print(f"Попытка записи в небезопасный путь: {path}")
        write_result = await fs.write_file(path, "test content")
        print(f"  Результат: {'Успех' if write_result['success'] else 'Ошибка'}")
        if not write_result["success"]:
            print(f"  Причина отказа: {write_result['error']}")

        print("-" * 30)

    print("-" * 50)


async def test_chat_paths(fs: FileSystemAccess) -> None:
    """
    Проверяет извлечение и обработку путей из чата.

    Args:
        fs: Экземпляр FileSystemAccess
    """
    print("\n=== Тест извлечения путей из чата ===\n")

    chat_messages = [
        "Пожалуйста, прочитай файл workspace/test_file.txt",
        "Мне нужно записать данные в ./app/test_data.json",
        "Проверь информацию о C:\\Users\\amritagopi\\GopiAI\\workspace\\test_file.txt",
        "Что находится в директории ./docs?",
        "Удали файл workspace\\tmp\\temp_file.txt"
    ]

    for message in chat_messages:
        print(f"Сообщение: {message}")
        path = fs.parse_chat_path(message)
        print(f"  Извлеченный путь: {path or 'Не найден'}")
        if path:
            print(f"  Абсолютный путь: {os.path.abspath(path)}")
        print("-" * 30)

    print("-" * 50)


async def test_history(fs: FileSystemAccess) -> None:
    """
    Проверяет историю файловых операций.

    Args:
        fs: Экземпляр FileSystemAccess
    """
    print("\n=== Тест истории операций ===\n")

    history = fs.get_operation_history()
    print(f"Количество операций: {len(history)}")

    if history:
        print("\nПоследние 5 операций:")
        for i, operation in enumerate(history[-5:]):
            print(f"  {i+1}. {operation['operation']} - {operation['path']} - {'Успех' if operation['success'] else 'Ошибка'}")

    print("-" * 50)


async def main() -> None:
    """Основная функция запуска тестов."""
    parser = argparse.ArgumentParser(description="Тест модуля FileSystemAccess")
    parser.add_argument(
        "--safe-mode",
        "-s",
        action="store_true",
        default=True,
        help="Включить режим безопасности",
    )
    parser.add_argument(
        "--chat-paths",
        "-c",
        action="store_true",
        default=True,
        help="Включить поддержку путей из чата",
    )
    parser.add_argument(
        "--test",
        "-t",
        choices=["all", "directory", "file", "unsafe", "chat", "history"],
        default="all",
        help="Выбор конкретного теста",
    )
    args = parser.parse_args()

    # Создаем экземпляр FileSystemAccess
    fs = FileSystemAccess(
        root_dir=project_root,
        safe_mode=args.safe_mode,
        chat_paths_enabled=args.chat_paths
    )

    try:
        # Запускаем выбранные тесты
        if args.test in ["all", "directory"]:
            await test_directory_operations(fs)

        if args.test in ["all", "file"]:
            await test_file_operations(fs)

        if args.test in ["all", "unsafe"]:
            await test_unsafe_paths(fs)

        if args.test in ["all", "chat"]:
            await test_chat_paths(fs)

        if args.test in ["all", "history"]:
            await test_history(fs)

    except Exception as e:
        print(f"Ошибка при выполнении тестов: {str(e)}")

    print("\n=== Тесты завершены ===\n")


if __name__ == "__main__":
    asyncio.run(main())
