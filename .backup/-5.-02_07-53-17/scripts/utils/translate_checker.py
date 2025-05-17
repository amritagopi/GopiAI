#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для проверки файлов переводов на наличие строк с пометкой TODO,
которые требуют перевода.
"""

import json
import os
import sys

def check_translations(translation_files):
    """
    Проверяет файлы переводов на наличие строк с пометкой TODO.

    Args:
        translation_files (list): Список путей к файлам переводов

    Returns:
        dict: Словарь с найденными проблемами для каждого файла
    """
    problems = {}

    for file_path in translation_files:
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            file_problems = []
            _find_todo_in_dict(translations, "", file_problems)

            if file_problems:
                problems[file_path] = file_problems

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {str(e)}")

    return problems

def _find_todo_in_dict(data, path, problems):
    """
    Рекурсивно ищет строки с пометкой TODO в словаре.

    Args:
        data (dict): Словарь для проверки
        path (str): Текущий путь в словаре
        problems (list): Список для сохранения найденных проблем
    """
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            _find_todo_in_dict(value, new_path, problems)
    elif isinstance(data, str) and "TODO:" in data:
        problems.append({"path": path, "value": data})

def main():
    """Основная функция скрипта."""
    # Определяем пути к файлам переводов
    translation_files = [
        os.path.join("app", "ui", "i18n", "en.json"),
        os.path.join("app", "ui", "i18n", "ru.json"),
        os.path.join("app", "ui", "themes", "EN-translations.json"),
        os.path.join("app", "ui", "themes", "RU-translations.json")
    ]

    # Проверяем переводы
    problems = check_translations(translation_files)

    if not problems:
        print("Проблем с переводами не найдено!")
        return 0

    # Выводим найденные проблемы
    for file_path, file_problems in problems.items():
        print(f"\n{file_path} ({len(file_problems)} проблем):")
        for problem in file_problems:
            print(f"  {problem['path']}: {problem['value']}")

    return 1

if __name__ == "__main__":
    sys.exit(main())
