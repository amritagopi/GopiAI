#!/usr/bin/env python
"""
Демонстрация экспорта и импорта накопленного опыта

Этот скрипт демонстрирует новую функциональность экспорта и импорта
накопленного опыта в ReasoningAgent.
"""

import os
import asyncio
import json
from datetime import datetime
import tempfile
import shutil

from app.agent.reasoning import ReasoningAgent
from app.agent.personalization_manager import (
    PersonalizationManager, InteractionType, ContentDomain, UserProfile
)
from app.agent.experience_manager import ExperienceArchive
from app.agent.error_manager import ErrorManager
from app.config import config


async def demo_experience_export_import():
    """Основная демонстрационная функция"""
    print("="*80)
    print("Демонстрация экспорта и импорта накопленного опыта")
    print("="*80)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    print("\n1. Подготовка тестовых данных")
    print("-"*80)

    # Создаем дополнительные профили для демонстрации
    if agent.personalization_manager:
        # Создаем профиль разработчика
        dev_profile = agent.personalization_manager.create_profile("developer")
        dev_profile.set_preference("code_comments", "Уровень комментирования кода", 0.8, 0.7)
        dev_profile.set_preference("tech_level", "Технический уровень", 0.9, 0.8)
        dev_profile.update_content_domain(ContentDomain.WEB_DEVELOPMENT, 0.9)
        dev_profile.update_content_domain(ContentDomain.BACKEND, 0.7)

        # Симулируем взаимодействия для профиля разработчика
        agent.personalization_manager.record_interaction(
            InteractionType.COMMAND,
            "git commit -m 'Реализована функция экспорта опыта'",
            {"directory": "."}
        )
        agent.personalization_manager.record_interaction(
            InteractionType.FILE_ACCESS,
            "Чтение файла app/agent/experience_manager.py",
            {"file_path": "app/agent/experience_manager.py", "operation": "read"}
        )
        agent.personalization_manager.save_profile("developer")

        # Создаем профиль аналитика
        analyst_profile = agent.personalization_manager.create_profile("analyst")
        analyst_profile.set_preference("verbosity", "Подробность объяснений", 0.9, 0.8)
        analyst_profile.set_preference("detailed_planning", "Детализация планирования", 0.8, 0.7)
        analyst_profile.update_content_domain(ContentDomain.DATA_SCIENCE, 0.9)
        analyst_profile.update_content_domain(ContentDomain.DOCUMENTATION, 0.7)

        # Симулируем взаимодействия для профиля аналитика
        agent.personalization_manager.record_interaction(
            InteractionType.COMMAND,
            "python analyze_data.py --input data.csv --output report.pdf",
            {"directory": "data"}
        )
        agent.personalization_manager.record_interaction(
            InteractionType.FILE_ACCESS,
            "Чтение файла data/results.csv",
            {"file_path": "data/results.csv", "operation": "read"}
        )
        agent.personalization_manager.save_profile("analyst")

        # Возвращаемся к стандартному профилю
        agent.personalization_manager.set_active_profile("default_user")

        # Выводим информацию о созданных профилях
        print("Созданы тестовые профили:")
        profiles = await agent.list_available_user_profiles()
        for profile in profiles.get("profiles", []):
            active_marker = " (активный)" if profile.get("active", False) else ""
            print(f"- {profile['user_id']}{active_marker}")

    # Создаем тестовые записи об ошибках
    if agent.error_manager:
        from app.agent.error_analysis_system import ErrorSource, ErrorSeverity

        # Добавляем несколько тестовых ошибок
        agent.error_manager.log_error(
            message="Файл не найден: data/config.json",
            source=ErrorSource.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM
        )

        agent.error_manager.log_error(
            message="Неверный формат данных в запросе API",
            source=ErrorSource.API_CALL,
            severity=ErrorSeverity.HIGH
        )

        agent.error_manager.log_error(
            message="Таймаут операции: git pull",
            source=ErrorSource.TERMINAL,
            severity=ErrorSeverity.LOW
        )

        print("\nДобавлены тестовые записи об ошибках")

    print("\n2. Экспорт накопленного опыта")
    print("-"*80)

    # Экспортируем весь опыт
    export_result = await agent.export_all_experience("demo_experience")

    if export_result.get("success", False):
        print(f"Опыт успешно экспортирован в архив: {export_result['archive_path']}")
        print(f"Включено профилей: {len(export_result.get('profiles_included', []))}")

        # Выводим список архивов
        archives_list = await agent.get_experience_archives_list()
        if archives_list.get("success", False):
            print(f"\nДоступные архивы ({archives_list.get('count', 0)}):")
            for archive_info in archives_list.get("archives", []):
                print(f"- {archive_info['filename']} ({archive_info['size'] // 1024} КБ)")
                if archive_info.get("metadata"):
                    print(f"  Создан: {archive_info['metadata'].get('created_at', 'Неизвестно')}")

        # Получаем статистику текущего опыта
        print("\nСтатистика текущего опыта:")
        stats_result = await agent.get_experience_statistics()
        if stats_result.get("success", False):
            stats = stats_result.get("statistics", {})

            if "profiles" in stats:
                profiles_stats = stats["profiles"]
                print(f"Профили: {profiles_stats.get('profiles_count', 0)}")
                print(f"Взаимодействия: {profiles_stats.get('total_interactions', 0)}")

                if "top_domains" in profiles_stats:
                    print("\nОсновные домены контента:")
                    for domain, value in profiles_stats.get("top_domains", {}).items():
                        print(f"- {domain}: {value:.2f}")

            if "errors" in stats:
                errors_stats = stats["errors"]
                print(f"\nОшибки: {errors_stats.get('total_errors', 0)}")
    else:
        print(f"Ошибка экспорта опыта: {export_result.get('error', 'Неизвестная ошибка')}")

    print("\n3. Демонстрация импорта опыта")
    print("-"*80)

    # Создаем временную директорию для демонстрации импорта
    temp_dir = tempfile.mkdtemp()

    try:
        # Создаем временный экземпляр агента для демонстрации импорта
        print("Создаем новый экземпляр агента с пустым профилем...")

        # Создаем временную директорию для персонализации
        personalization_dir = os.path.join(temp_dir, "personalization")
        os.makedirs(personalization_dir, exist_ok=True)

        # Создаем экземпляры менеджеров
        temp_personalization = PersonalizationManager(storage_dir=personalization_dir)
        temp_error_manager = ErrorManager()
        temp_experience = ExperienceArchive(
            base_dir=os.path.join(temp_dir, "archives"),
            personalization_manager=temp_personalization,
            error_manager=temp_error_manager
        )

        # Создаем базовый профиль
        temp_personalization.create_profile("default_user")

        print("Проверяем статистику нового экземпляра (до импорта):")
        # Получаем текущую статистику для временного экземпляра
        temp_stats = temp_experience.extract_aggregate_statistics(export_result["archive_path"])

        if "profiles" in temp_stats:
            profiles_stats = temp_stats["profiles"]
            print(f"Профили в архиве: {profiles_stats.get('profiles_count', 0)} (будут импортированы)")

        print("\nИмпортируем архив опыта...")
        # Импортируем архив в новый экземпляр
        import_result = temp_experience.import_archive(
            archive_path=export_result["archive_path"],
            import_profiles=True,
            import_errors=True,
            merge_existing=True
        )

        if import_result.get("success", False):
            print("Архив успешно импортирован")

            # Проверяем импортированные профили
            imported_profiles = import_result.get("results", {}).get("imported_profiles", [])
            print(f"Импортировано профилей: {len(imported_profiles)}")
            for profile_id in imported_profiles:
                print(f"- {profile_id}")

            # Проверяем, что профили действительно загружены
            profiles_list = temp_personalization.list_profiles()
            print(f"\nДоступные профили после импорта: {len(profiles_list)}")
            for profile_info in profiles_list:
                print(f"- {profile_info['user_id']}")

            # Проверяем, что ошибки импортированы
            if import_result.get("results", {}).get("imported_errors", False):
                error_count = import_result.get("results", {}).get("imported_errors_count", 0)
                print(f"\nИмпортировано записей об ошибках: {error_count}")

                # Получаем статистику ошибок
                error_stats = temp_error_manager.get_error_statistics()
                if "by_source" in error_stats:
                    print("Ошибки по источникам:")
                    for source, count in error_stats.get("by_source", {}).items():
                        print(f"- {source}: {count}")
        else:
            print(f"Ошибка импорта архива: {import_result.get('error', 'Неизвестная ошибка')}")

    finally:
        # Удаляем временную директорию
        shutil.rmtree(temp_dir)

    print("\n4. Работа с утилитой командной строки")
    print("-"*80)
    print("Для работы с архивами опыта можно использовать скрипт experience_archiver.py:")
    print("- python scripts/experience_archiver.py create my_archive")
    print("- python scripts/experience_archiver.py import path/to/archive.zip")
    print("- python scripts/experience_archiver.py list")
    print("- python scripts/experience_archiver.py stats path/to/archive.zip")
    print("- python scripts/experience_archiver.py delete archive_name.zip")

    print("\nЗавершение демонстрации")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(demo_experience_export_import())
