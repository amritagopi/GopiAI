#!/usr/bin/env python
"""
Утилита командной строки для экспорта/импорта накопленного опыта

Позволяет создавать архивы опыта, импортировать, просматривать список
и анализировать накопленный опыт из командной строки.

Примеры использования:
- Создание архива опыта: python experience_archiver.py create my_archive
- Импорт архива: python experience_archiver.py import archives/my_archive_20250605_120000.zip
- Просмотр списка архивов: python experience_archiver.py list
- Просмотр статистики архива: python experience_archiver.py stats archives/my_archive_20250605_120000.zip
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Добавляем корневой каталог проекта в sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.agent.experience_manager import ExperienceArchive
from app.agent.personalization_manager import PersonalizationManager
from app.agent.error_manager import ErrorManager


def setup_managers():
    """
    Инициализирует необходимые менеджеры.

    Returns:
        Tuple[ExperienceArchive, PersonalizationManager, ErrorManager]
    """
    personalization_manager = PersonalizationManager()
    error_manager = ErrorManager()
    experience_archive = ExperienceArchive(
        personalization_manager=personalization_manager,
        error_manager=error_manager
    )

    return experience_archive, personalization_manager, error_manager


def create_archive(args):
    """Создает архив опыта"""
    archive, personalization_manager, error_manager = setup_managers()

    # Загружаем профили, если они существуют
    if args.profiles:
        profiles = args.profiles.split(',')
        for profile_id in profiles:
            personalization_manager.load_profile(profile_id)

    result = archive.create_archive(
        archive_name=args.name,
        profiles_to_include=profiles if args.profiles else None,
        include_errors=not args.no_errors,
        include_metadata=True
    )

    if result["success"]:
        print(f"Архив успешно создан: {result['archive_path']}")
        print(f"Включено профилей: {len(result['profiles_included'])}")
    else:
        print(f"Ошибка создания архива: {result.get('error', 'Неизвестная ошибка')}")
        sys.exit(1)


def import_archive(args):
    """Импортирует архив опыта"""
    archive, personalization_manager, error_manager = setup_managers()

    result = archive.import_archive(
        archive_path=args.path,
        import_profiles=not args.no_profiles,
        import_errors=not args.no_errors,
        merge_existing=not args.no_merge
    )

    if result["success"]:
        print("Архив успешно импортирован")
        if "results" in result:
            if "imported_profiles" in result["results"]:
                print(f"Импортировано профилей: {len(result['results']['imported_profiles'])}")
                for profile_id in result["results"]["imported_profiles"]:
                    print(f"  - {profile_id}")

            if result["results"].get("imported_errors", False):
                print(f"Импортировано записей об ошибках: {result['results'].get('imported_errors_count', 0)}")

            if result["results"].get("metadata"):
                print(f"Метаданные архива:")
                print(f"  Имя: {result['results']['metadata'].get('archive_name', 'Неизвестно')}")
                print(f"  Создан: {result['results']['metadata'].get('created_at', 'Неизвестно')}")
    else:
        print(f"Ошибка импорта архива: {result.get('error', 'Неизвестная ошибка')}")
        sys.exit(1)


def list_archives(args):
    """Выводит список доступных архивов"""
    archive, _, _ = setup_managers()

    archives_list = archive.list_archives()

    if not archives_list:
        print("Архивы не найдены")
        return

    print(f"Найдено архивов: {len(archives_list)}")
    for idx, archive_info in enumerate(archives_list, 1):
        print(f"\n{idx}. {archive_info['filename']}")
        print(f"   Путь: {archive_info['path']}")
        print(f"   Размер: {archive_info['size'] // 1024} КБ")
        print(f"   Создан: {archive_info['created']}")

        if archive_info.get("metadata"):
            metadata = archive_info["metadata"]
            print(f"   Имя архива: {metadata.get('archive_name', 'Неизвестно')}")
            print(f"   Включено профилей: {len(metadata.get('profiles', []))}")
            print(f"   Включены ошибки: {'Да' if metadata.get('includes_errors', False) else 'Нет'}")


def show_stats(args):
    """Показывает статистику архива"""
    archive, _, _ = setup_managers()

    statistics = archive.extract_aggregate_statistics(args.path)

    if "error" in statistics:
        print(f"Ошибка извлечения статистики: {statistics['error']}")
        sys.exit(1)

    print("\n=== Статистика архива ===\n")

    # Выводим метаданные
    if "metadata" in statistics:
        metadata = statistics["metadata"]
        print("Метаданные:")
        print(f"  Имя архива: {metadata.get('archive_name', 'Неизвестно')}")
        print(f"  Создан: {metadata.get('created_at', 'Неизвестно')}")
        print(f"  Версия: {metadata.get('version', 'Неизвестно')}")
        print()

    # Выводим статистику профилей
    if "profiles" in statistics:
        profiles_stats = statistics["profiles"]
        print("Статистика профилей:")
        print(f"  Количество профилей: {profiles_stats.get('profiles_count', 0)}")
        print(f"  Общее количество взаимодействий: {profiles_stats.get('total_interactions', 0)}")

        if "top_domains" in profiles_stats:
            print("\n  Основные домены контента:")
            for domain, value in profiles_stats["top_domains"].items():
                print(f"    - {domain}: {value:.2f}")

        if "top_tasks" in profiles_stats:
            print("\n  Частые задачи:")
            for task, count in profiles_stats["top_tasks"].items():
                print(f"    - {task}: {count}")

        if "preferences" in profiles_stats:
            print("\n  Средние значения предпочтений:")
            for pref_id, stats in profiles_stats["preferences"].items():
                print(f"    - {stats.get('name', pref_id)}: {stats.get('avg_value', 0.5):.2f} "
                      f"(уверенность: {stats.get('avg_confidence', 0.0):.2f})")

        print()

    # Выводим статистику ошибок
    if "errors" in statistics and statistics["errors"]:
        errors_stats = statistics["errors"]
        print("Статистика ошибок:")
        print(f"  Общее количество ошибок: {errors_stats.get('total_errors', 0)}")

        if "by_severity" in errors_stats:
            print("\n  По серьезности:")
            for severity, count in errors_stats["by_severity"].items():
                print(f"    - {severity}: {count}")

        if "by_source" in errors_stats:
            print("\n  По источникам:")
            for source, count in errors_stats["by_source"].items():
                print(f"    - {source}: {count}")

        print()


def delete_archive(args):
    """Удаляет архив"""
    archive, _, _ = setup_managers()

    success = archive.delete_archive(args.filename)

    if success:
        print(f"Архив успешно удален: {args.filename}")
    else:
        print(f"Ошибка удаления архива: {args.filename}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Утилита для работы с архивами опыта GopiAI")
    subparsers = parser.add_subparsers(dest="command", help="Команда")

    # Команда создания архива
    create_parser = subparsers.add_parser("create", help="Создать архив опыта")
    create_parser.add_argument("name", help="Имя архива")
    create_parser.add_argument("--profiles", help="Список профилей через запятую")
    create_parser.add_argument("--no-errors", action="store_true", help="Не включать данные об ошибках")

    # Команда импорта архива
    import_parser = subparsers.add_parser("import", help="Импортировать архив опыта")
    import_parser.add_argument("path", help="Путь к архиву")
    import_parser.add_argument("--no-profiles", action="store_true", help="Не импортировать профили")
    import_parser.add_argument("--no-errors", action="store_true", help="Не импортировать данные об ошибках")
    import_parser.add_argument("--no-merge", action="store_true", help="Не объединять с существующими данными")

    # Команда просмотра списка архивов
    list_parser = subparsers.add_parser("list", help="Показать список архивов")

    # Команда просмотра статистики архива
    stats_parser = subparsers.add_parser("stats", help="Показать статистику архива")
    stats_parser.add_argument("path", help="Путь к архиву")

    # Команда удаления архива
    delete_parser = subparsers.add_parser("delete", help="Удалить архив")
    delete_parser.add_argument("filename", help="Имя файла архива")

    args = parser.parse_args()

    if args.command == "create":
        create_archive(args)
    elif args.command == "import":
        import_archive(args)
    elif args.command == "list":
        list_archives(args)
    elif args.command == "stats":
        show_stats(args)
    elif args.command == "delete":
        delete_archive(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
