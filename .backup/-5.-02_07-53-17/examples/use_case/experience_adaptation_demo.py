#!/usr/bin/env python
"""
Демонстрация механизма адаптации к предыдущему опыту

Этот скрипт демонстрирует, как ReasoningAgent адаптирует свое поведение
на основе предыдущего опыта взаимодействия и анализа ошибок.
"""

import os
import asyncio
import json
from datetime import datetime
import time

from app.agent.reasoning import ReasoningAgent
from app.agent.personalization_manager import (
    PersonalizationManager, InteractionType, ContentDomain, UserProfile
)
from app.agent.experience_manager import ExperienceArchive
from app.agent.experience_adapter import ExperienceAdapter, AdaptationSuggestion
from app.agent.error_manager import ErrorManager, ErrorSource, ErrorSeverity
from app.config import config


async def demo_experience_adaptation():
    """Основная демонстрационная функция"""
    print("="*80)
    print("Демонстрация механизма адаптации к предыдущему опыту")
    print("="*80)

    # Инициализируем агента
    agent = ReasoningAgent()
    await agent.initialize()

    print("\n1. Подготовка тестовой истории опыта")
    print("-"*80)

    # Создаем тестовую историю опыта
    if agent.personalization_manager:
        # Симулируем успешный опыт работы с файлами
        agent.personalization_manager.record_interaction(
            InteractionType.COMMAND,
            "Чтение файла config.json и обновление настроек",
            {
                "task_type": "file_operation",
                "approach": "Сначала проверить существование файла, затем использовать json.load",
                "result": "Успешно прочитаны настройки",
                "success": True,
                "error": None
            }
        )

        # Симулируем неудачный опыт работы с API
        agent.personalization_manager.record_interaction(
            InteractionType.COMMAND,
            "Получение данных из API weatherapi.com",
            {
                "task_type": "api_call",
                "approach": "Прямой запрос без проверки ошибок",
                "result": "Ошибка подключения к API",
                "success": False,
                "error": "Соединение прервано из-за таймаута"
            }
        )

        # Симулируем успешный опыт после исправления
        agent.personalization_manager.record_interaction(
            InteractionType.COMMAND,
            "Получение данных из API weatherapi.com с обработкой ошибок",
            {
                "task_type": "api_call",
                "approach": "Запрос с обработкой исключений и таймаутом в 30 секунд",
                "result": "Успешно получены данные",
                "success": True,
                "error": None
            }
        )

        # Сохраняем профиль
        agent.personalization_manager.save_profile()

    # Добавляем тестовые записи об ошибках
    if agent.error_manager:
        # Имитируем несколько ошибок работы с файлами
        agent.error_manager.log_error(
            message="Файл не найден: data/config.json",
            source=ErrorSource.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context="При попытке чтения файла конфигурации",
            metadata={"file_path": "data/config.json", "operation": "read"}
        )

        agent.error_manager.log_error(
            message="Некорректный формат JSON в файле настроек",
            source=ErrorSource.FILE_SYSTEM,
            severity=ErrorSeverity.HIGH,
            context="При загрузке файла config.json",
            metadata={"file_path": "config.json", "operation": "parse"}
        )

        # Имитируем ошибки API
        agent.error_manager.log_error(
            message="Таймаут при обращении к API",
            source=ErrorSource.API_CALL,
            severity=ErrorSeverity.MEDIUM,
            context="При получении данных из внешнего API",
            metadata={"url": "https://api.example.com/data", "timeout": 10}
        )

        agent.error_manager.log_error(
            message="Ошибка сетевого подключения",
            source=ErrorSource.API_CALL,
            severity=ErrorSeverity.HIGH,
            context="При обращении к API без проверки соединения",
            metadata={"url": "https://api.example.com/data"}
        )

        # Инициируем анализ ошибок для создания паттернов
        agent.error_manager.detect_error_patterns()

    print("Создана тестовая история опыта и ошибок")

    print("\n2. Демонстрация адаптации к предыдущему опыту")
    print("-"*80)

    # Демонстрация 1: Задача работы с файлами
    print("\nПример 1: Задача работы с файлами")
    task1 = "Прочитать файл settings.json и обновить настройки приложения"

    # Получаем рекомендации на основе опыта
    suggestions = await agent.get_experience_based_suggestions(task1)

    if suggestions.get("success", False):
        print(f"Найдено предложений: {suggestions.get('count', 0)}")
        for idx, suggestion in enumerate(suggestions.get("suggestions", []), 1):
            print(f"{idx}. {suggestion['suggestion']}")
            print(f"   Тип: {suggestion['type']}")
            print(f"   Обоснование: {suggestion['reasoning']}")
            print(f"   Уверенность: {suggestion['confidence']:.2f}")
            print()

    # Получаем советы по предотвращению ошибок
    approach1 = "Открыть файл и загрузить JSON"
    error_tips = await agent.get_error_prevention_for_task(task1, approach1)

    if error_tips.get("success", False):
        print(f"Советы по предотвращению ошибок ({error_tips.get('count', 0)}):")
        for idx, tip in enumerate(error_tips.get("tips", []), 1):
            print(f"{idx}. {tip['prevention_tip']}")
            print(f"   Тип ошибки: {tip['error_type']}")
            print(f"   Обоснование: {tip['reasoning']}")
            print()

    # Создаем план для задачи
    print("Создаем план для задачи с учетом предыдущего опыта:")
    plan = await agent.create_plan(task1)
    print(plan)

    # Демонстрация 2: Задача работы с API
    print("\nПример 2: Задача работы с API")
    task2 = "Получить данные о погоде из API openweathermap.org для Москвы"

    # Получаем рекомендации на основе опыта
    suggestions = await agent.get_experience_based_suggestions(task2)

    if suggestions.get("success", False):
        print(f"Найдено предложений: {suggestions.get('count', 0)}")
        for idx, suggestion in enumerate(suggestions.get("suggestions", []), 1):
            print(f"{idx}. {suggestion['suggestion']}")
            print(f"   Тип: {suggestion['type']}")
            print(f"   Обоснование: {suggestion['reasoning']}")
            print(f"   Уверенность: {suggestion['confidence']:.2f}")
            print()

    # Получаем советы по предотвращению ошибок
    approach2 = "Выполнить HTTP запрос к API"
    error_tips = await agent.get_error_prevention_for_task(task2, approach2)

    if error_tips.get("success", False):
        print(f"Советы по предотвращению ошибок ({error_tips.get('count', 0)}):")
        for idx, tip in enumerate(error_tips.get("tips", []), 1):
            print(f"{idx}. {tip['prevention_tip']}")
            print(f"   Тип ошибки: {tip['error_type']}")
            print(f"   Обоснование: {tip['reasoning']}")
            print()

    # Демонстрация 3: Улучшение решения на основе опыта
    print("\nПример 3: Улучшение решения на основе опыта")
    task3 = "Загрузить данные из API и сохранить в CSV файл"

    initial_solution = """
    import requests

    url = "https://api.example.com/data"
    response = requests.get(url)
    data = response.json()

    with open("data.csv", "w") as f:
        for item in data:
            f.write(f"{item['id']},{item['name']},{item['value']}\\n")
    """

    print("Исходное решение:")
    print(initial_solution)

    improvement = await agent.improve_solution(task3, initial_solution)

    if improvement.get("success", False) and improvement.get("has_improvement", False):
        print("\nУлучшенное решение на основе предыдущего опыта:")
        print(improvement.get("improved_solution", ""))
        print(f"\nОбоснование: {improvement.get('reasoning', '')}")
    else:
        print("\nНе удалось улучшить решение.")
        print(f"Причина: {improvement.get('message', improvement.get('error', 'Неизвестно'))}")

    print("\n3. Адаптация параметров планирования")
    print("-"*80)

    # Демонстрация адаптации параметров планирования
    print("Адаптация параметров планирования для разных задач:")

    tasks = [
        "Проанализировать журнал ошибок и выявить закономерности",
        "Настроить базовую конфигурацию проекта",
        "Реализовать сложную систему аутентификации с несколькими провайдерами"
    ]

    for idx, task in enumerate(tasks, 1):
        params = await agent.experience_adapter.adapt_planning_parameters(task)
        print(f"\nЗадача {idx}: {task}")
        print(f"Стратегия: {params.get('strategy', 'Неизвестно')}")
        print(f"Глубина планирования: {params.get('max_depth', 0)}")
        print(f"Уровень детализации: {params.get('detail_level', 0):.2f}")
        print(f"Порог риска: {params.get('risk_threshold', 0):.2f}")
        print(f"Параллелизация: {'Да' if params.get('allow_parallelization', False) else 'Нет'}")
        print(f"Адаптировано: {'Да' if params.get('adapted', False) else 'Нет'}")

    print("\nЗавершение демонстрации")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(demo_experience_adaptation())
