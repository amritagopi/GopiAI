#!/usr/bin/env python
"""
Демонстрация системы персонализации

Этот скрипт демонстрирует работу механизма персонализации в ReasoningAgent.
"""

import os
import asyncio
import json
from datetime import datetime

from app.agent.reasoning import ReasoningAgent
from app.agent.personalization_manager import (
    PersonalizationManager, InteractionType, ContentDomain, UserProfile
)
from app.config import config


async def demo_personalization():
    """Основная демонстрационная функция"""
    print("="*80)
    print("Демонстрация системы персонализации")
    print("="*80)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    print("\n1. Получаем информацию о текущих настройках персонализации")
    print("-"*80)

    # Проверяем, что менеджер персонализации инициализирован
    if not agent.personalization_manager:
        print("Ошибка: Менеджер персонализации не инициализирован")
        return

    # Получаем и выводим активный профиль
    active_profile = agent.personalization_manager.get_active_profile()
    if active_profile:
        print(f"Активный профиль: {active_profile.user_id}")
        print(f"Создан: {active_profile.created_at}")
        print(f"Последняя активность: {active_profile.last_active}")
        print(f"Количество предпочтений: {len(active_profile.preferences)}")
        print(f"Количество взаимодействий: {len(active_profile.recent_interactions)}")
    else:
        print("Активный профиль не найден")

    # Получаем персонализированные параметры
    params = await agent.get_personalized_parameters()
    print("\nПерсонализированные параметры:")
    print(json.dumps(params, indent=2, ensure_ascii=False))

    print("\n2. Симуляция взаимодействий пользователя")
    print("-"*80)

    # Симулируем различные типы взаимодействий
    interactions = [
        (InteractionType.COMMAND, "ls -la app/agent", {"directory": "app/agent"}),
        (InteractionType.COMMAND, "git status", {"directory": "."}),
        (InteractionType.FILE_ACCESS, "Чтение файла app/agent/reasoning.py", {"file_path": "app/agent/reasoning.py", "operation": "read"}),
        (InteractionType.PLAN_APPROVAL, "Создать класс для персонализации", {"plan_complexity": 0.7, "task_type": "code_generation"}),
        (InteractionType.FEEDBACK, "Обратная связь по подробности объяснений", {"feedback_type": "verbosity", "value": 0.8})
    ]

    for interaction_type, content, metadata in interactions:
        interaction_id = agent.personalization_manager.record_interaction(
            interaction_type=interaction_type,
            content=content,
            metadata=metadata
        )
        print(f"Записано взаимодействие ({interaction_type.value}): {content}")

    # Обновляем некоторые предпочтения
    agent.personalization_manager.get_active_profile().set_preference(
        "verbosity", "Подробность объяснений", 0.8, 0.7
    )
    agent.personalization_manager.get_active_profile().set_preference(
        "code_comments", "Уровень комментирования кода", 0.6, 0.6
    )

    # Обновляем домены контента
    agent.personalization_manager.get_active_profile().update_content_domain(ContentDomain.WEB_DEVELOPMENT, 0.7)
    agent.personalization_manager.get_active_profile().update_content_domain(ContentDomain.BACKEND, 0.5)

    print("\n3. Анализ персонализированных параметров после взаимодействий")
    print("-"*80)

    # Получаем обновленные персонализированные параметры
    params = await agent.get_personalized_parameters()
    print("Обновленные персонализированные параметры:")
    print(json.dumps(params, indent=2, ensure_ascii=False))

    print("\n4. Персонализированный анализ задачи")
    print("-"*80)

    # Анализируем различные задачи
    tasks = [
        "Создай компонент для отображения данных в React с использованием Hooks",
        "Оптимизируй запрос к базе данных для улучшения производительности",
        "Исправь ошибку в функции авторизации пользователей",
    ]

    for task in tasks:
        analysis = agent.personalization_manager.analyze_task(task)
        print(f"\nАнализ задачи: {task}")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

    print("\n5. Демонстрация экспорта и импорта профиля")
    print("-"*80)

    # Создаем директорию для экспорта, если она не существует
    export_dir = "data/export"
    os.makedirs(export_dir, exist_ok=True)

    # Экспортируем текущий профиль
    export_path = os.path.join(export_dir, "profile_export.json")
    export_result = await agent.export_user_experience(export_path)

    if export_result["success"]:
        print(f"Профиль успешно экспортирован в {export_path}")

        # Создаем второй профиль для демонстрации импорта
        second_profile_id = "test_user"
        second_profile = agent.personalization_manager.create_profile(second_profile_id)
        second_profile.set_preference("risk_tolerance", "Толерантность к риску", 0.2, 0.5)

        # Импортируем экспортированный профиль
        import_result = await agent.import_user_experience(export_path)

        if import_result["success"]:
            print(f"Профиль успешно импортирован из {export_path}")

            # Получаем список доступных профилей
            profiles_result = await agent.list_available_user_profiles()
            print("\nДоступные профили:")
            for profile_info in profiles_result["profiles"]:
                active_marker = " (активный)" if profile_info["active"] else ""
                print(f"- {profile_info['user_id']}{active_marker}")
                print(f"  Создан: {profile_info['created_at']}")
                print(f"  Последняя активность: {profile_info['last_active']}")

            # Объединяем профили
            merge_result = await agent.merge_user_experiences(second_profile_id, import_result["user_id"])

            if merge_result["success"]:
                print(f"\nПрофили успешно объединены: {second_profile_id} → {import_result['user_id']}")

                # Получаем предпочтения объединенного профиля
                prefs_result = await agent.get_user_preferences()
                if prefs_result["success"]:
                    print("\nПредпочтения объединенного профиля:")
                    for pref_id, pref_data in prefs_result["preferences"].items():
                        print(f"- {pref_data['name']}: {pref_data['value']:.2f} "
                              f"(уверенность: {pref_data['confidence']:.2f})")
            else:
                print(f"Ошибка при объединении профилей: {merge_result['error']}")
        else:
            print(f"Ошибка при импорте профиля: {import_result['error']}")
    else:
        print(f"Ошибка при экспорте профиля: {export_result['error']}")

    print("\n6. Демонстрация адаптации рекомендаций")
    print("-"*80)

    # Создаем план для задачи с учетом персонализации
    task = "Реализовать механизм персонализации на основе истории взаимодействия"
    plan = await agent.create_plan(task)

    print(f"Задача: {task}")
    print("\nПерсонализированный план:")
    print(plan)

    print("\nЗавершение демонстрации")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(demo_personalization())
