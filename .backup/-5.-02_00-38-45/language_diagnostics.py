#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для диагностики проблем с локализацией и переводами в приложении.
"""

import os
import sys
import json
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_translation_consistency():
    """
    Проверяет согласованность ключей переводов между различными файлами.
    """
    # Определяем пути к файлам переводов
    root_dir = Path(__file__).parent

    i18n_dir = root_dir / "app" / "ui" / "i18n"
    themes_dir = root_dir / "app" / "ui" / "themes"

    en_path_i18n = i18n_dir / "en.json"
    ru_path_i18n = i18n_dir / "ru.json"

    en_path_themes = themes_dir / "EN-translations.json"
    ru_path_themes = themes_dir / "RU-translations.json"

    # Проверка существования файлов
    files_to_check = [
        (en_path_i18n, "English (i18n)"),
        (ru_path_i18n, "Russian (i18n)"),
        (en_path_themes, "English (themes)"),
        (ru_path_themes, "Russian (themes)")
    ]

    translations = {}

    # Загружаем содержимое файлов
    for file_path, file_desc in files_to_check:
        if not file_path.exists():
            logger.warning(f"Файл {file_desc} не найден: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations[file_desc] = json.load(f)
                logger.info(f"Загружен файл {file_desc}: {len(translations[file_desc])} ключей верхнего уровня")
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла {file_desc}: {str(e)}")

    # Получаем все ключи из английского i18n файла (основной источник)
    if "English (i18n)" in translations:
        en_i18n_keys = set(_flatten_keys(translations["English (i18n)"]))
        logger.info(f"Английский i18n содержит {len(en_i18n_keys)} ключей (включая вложенные)")

        # Проверяем ключи в русском i18n файле
        if "Russian (i18n)" in translations:
            ru_i18n_keys = set(_flatten_keys(translations["Russian (i18n)"]))
            logger.info(f"Русский i18n содержит {len(ru_i18n_keys)} ключей (включая вложенные)")

            # Проверяем отсутствующие ключи
            missing_in_ru = en_i18n_keys - ru_i18n_keys
            if missing_in_ru:
                logger.warning(f"В русском i18n отсутствует {len(missing_in_ru)} ключей:")
                for key in sorted(missing_in_ru):
                    logger.warning(f"  - {key}")
            else:
                logger.info("Все ключи из английского i18n присутствуют в русском i18n!")

            # Проверяем лишние ключи
            extra_in_ru = ru_i18n_keys - en_i18n_keys
            if extra_in_ru:
                logger.warning(f"В русском i18n есть {len(extra_in_ru)} лишних ключей:")
                for key in sorted(extra_in_ru):
                    logger.warning(f"  - {key}")
            else:
                logger.info("В русском i18n нет лишних ключей!")

        # Проверяем ключи в английском themes файле
        if "English (themes)" in translations:
            en_themes_keys = set(_flatten_keys(translations["English (themes)"]))
            logger.info(f"Английский themes содержит {len(en_themes_keys)} ключей (включая вложенные)")

            # Проверяем перекрытия между i18n и themes
            overlapping_en = en_i18n_keys.intersection(en_themes_keys)
            if overlapping_en:
                logger.warning(f"Обнаружено {len(overlapping_en)} перекрывающихся ключей между En i18n и En themes:")
                for key in sorted(overlapping_en):
                    logger.warning(f"  - {key}")

                    # Проверяем, отличаются ли значения
                    i18n_value = _get_nested_value(translations["English (i18n)"], key.split('.'))
                    themes_value = _get_nested_value(translations["English (themes)"], key.split('.'))

                    if i18n_value != themes_value:
                        logger.error(f"    Значения различаются!")
                        logger.error(f"    i18n: {i18n_value}")
                        logger.error(f"    themes: {themes_value}")
            else:
                logger.info("Нет перекрывающихся ключей между английскими i18n и themes!")

        # Проверяем ключи в русском themes файле
        if "Russian (themes)" in translations and "Russian (i18n)" in translations:
            ru_themes_keys = set(_flatten_keys(translations["Russian (themes)"]))
            logger.info(f"Русский themes содержит {len(ru_themes_keys)} ключей (включая вложенные)")

            # Проверяем перекрытия между i18n и themes
            overlapping_ru = ru_i18n_keys.intersection(ru_themes_keys)
            if overlapping_ru:
                logger.warning(f"Обнаружено {len(overlapping_ru)} перекрывающихся ключей между Ru i18n и Ru themes:")
                for key in sorted(overlapping_ru):
                    logger.warning(f"  - {key}")

                    # Проверяем, отличаются ли значения
                    i18n_value = _get_nested_value(translations["Russian (i18n)"], key.split('.'))
                    themes_value = _get_nested_value(translations["Russian (themes)"], key.split('.'))

                    if i18n_value != themes_value:
                        logger.error(f"    Значения различаются!")
                        logger.error(f"    i18n: {i18n_value}")
                        logger.error(f"    themes: {themes_value}")
            else:
                logger.info("Нет перекрывающихся ключей между русскими i18n и themes!")

def _flatten_keys(d, parent_key=''):
    """
    Рекурсивно проходит по вложенному словарю и возвращает список всех ключей с учетом иерархии.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items

def _get_nested_value(d, key_parts):
    """
    Получает значение из вложенного словаря по списку частей ключа.
    """
    current = d
    for part in key_parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def check_todo_translations():
    """
    Проверяет наличие строк с пометкой TODO в файлах переводов.
    """
    from translate_checker import check_translations

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
        logger.info("Проблем с метками TODO в переводах не найдено!")
        return 0

    # Выводим найденные проблемы
    for file_path, file_problems in problems.items():
        logger.warning(f"\n{file_path} ({len(file_problems)} проблем):")
        for problem in file_problems:
            logger.warning(f"  {problem['path']}: {problem['value']}")

    return len(problems)

def main():
    """Основная функция скрипта."""
    print("\n===== ДИАГНОСТИКА ЛОКАЛИЗАЦИИ GOPI-AI =====\n")

    # Проверка согласованности ключей
    print("\n----- ПРОВЕРКА СОГЛАСОВАННОСТИ КЛЮЧЕЙ -----\n")
    check_translation_consistency()

    # Проверка наличия меток TODO
    print("\n----- ПРОВЕРКА МЕТОК TODO -----\n")
    todo_count = check_todo_translations()

    print("\n===== ЗАВЕРШЕНИЕ ДИАГНОСТИКИ =====\n")

    if todo_count > 0:
        print(f"ВНИМАНИЕ: Найдено {todo_count} меток TODO в переводах!")
    else:
        print("Все проверки завершены успешно!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
