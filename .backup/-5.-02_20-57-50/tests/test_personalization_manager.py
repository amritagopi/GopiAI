"""
Тесты для модуля персонализации.

Проверяет функциональность PersonalizationManager и связанных классов.
"""

import os
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from app.agent.personalization_manager import (
    PersonalizationManager, UserProfile, UserPreference, UserInteraction,
    InteractionType, ContentDomain
)


class TestPersonalizationManager(unittest.TestCase):
    """Тесты для PersonalizationManager"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.manager = PersonalizationManager(storage_dir=self.test_dir)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)

    def test_create_profile(self):
        """Тест создания профиля"""
        profile = self.manager.create_profile("test_user")

        self.assertEqual(profile.user_id, "test_user")
        self.assertEqual(self.manager.active_profile_id, "test_user")
        self.assertIn("test_user", self.manager.profiles)

        # Проверяем, что созданы базовые предпочтения
        self.assertIn("verbosity", profile.preferences)
        self.assertIn("risk_tolerance", profile.preferences)

    def test_save_and_load_profile(self):
        """Тест сохранения и загрузки профиля"""
        # Создаем и сохраняем профиль
        profile = self.manager.create_profile("test_user")
        profile.set_preference("test_pref", "Test Preference", 0.75, 0.8)
        self.manager.save_profile("test_user")

        # Создаем новый менеджер и загружаем профиль
        new_manager = PersonalizationManager(storage_dir=self.test_dir)
        loaded_profile = new_manager.load_profile("test_user")

        # Проверяем, что профиль загружен правильно
        self.assertIsNotNone(loaded_profile)
        self.assertEqual(loaded_profile.user_id, "test_user")
        self.assertIn("test_pref", loaded_profile.preferences)
        self.assertEqual(loaded_profile.preferences["test_pref"].value, 0.75)
        self.assertEqual(loaded_profile.preferences["test_pref"].confidence, 0.8)

    def test_record_interaction(self):
        """Тест записи взаимодействия"""
        profile = self.manager.create_profile("test_user")

        # Записываем взаимодействие
        interaction_id = self.manager.record_interaction(
            InteractionType.COMMAND,
            "ls -la",
            {"directory": "/home"},
            True
        )

        # Проверяем, что взаимодействие добавлено
        self.assertIsNotNone(interaction_id)
        self.assertEqual(len(profile.recent_interactions), 1)
        interaction = profile.recent_interactions[0]
        self.assertEqual(interaction.interaction_type, InteractionType.COMMAND)
        self.assertEqual(interaction.content, "ls -la")
        self.assertEqual(interaction.metadata, {"directory": "/home"})
        self.assertTrue(interaction.success)

    def test_detect_content_domains(self):
        """Тест определения доменов контента"""
        domains = self.manager._detect_content_domains(
            "Нужно настроить конфигурацию Docker и настроить CI/CD пайплайн для деплоя."
        )

        # Проверяем, что DevOps в списке доменов
        self.assertTrue(any(domain == ContentDomain.DEVOPS for domain, _ in domains))

    def test_detect_task_type(self):
        """Тест определения типа задачи"""
        task_type = self.manager._detect_task_type(
            "Создай новый файл для реализации класса пользователя."
        )

        self.assertEqual(task_type, "code_generation")

        task_type = self.manager._detect_task_type(
            "Исправь ошибку в функции авторизации."
        )

        self.assertEqual(task_type, "bug_fixing")

    def test_get_personalized_parameters(self):
        """Тест получения персонализированных параметров"""
        # Без активного профиля
        params = self.manager.get_personalized_parameters()
        self.assertFalse(params["personalized"])

        # С активным профилем
        profile = self.manager.create_profile("test_user")
        profile.set_preference("verbosity", "Подробность объяснений", 0.8, 0.7)

        params = self.manager.get_personalized_parameters()
        self.assertTrue(params["personalized"])
        self.assertEqual(params["verbosity"], 0.8)

    def test_analyze_task(self):
        """Тест анализа задачи"""
        # Без активного профиля
        result = self.manager.analyze_task("Напиши код для проверки уникальности пользователей")
        self.assertFalse(result["personalized"])

        # С активным профилем
        profile = self.manager.create_profile("test_user")
        profile.set_preference("detailed_planning", "Детализация планирования", 0.8, 0.7)

        result = self.manager.analyze_task("Создай класс для работы с API базы данных")
        self.assertTrue(result["personalized"])
        self.assertEqual(result["task_type"], "code_generation")
        self.assertEqual(result["detail_level"], "high")

    def test_export_and_import_profile(self):
        """Тест экспорта и импорта профиля"""
        # Создаем профиль с данными
        profile = self.manager.create_profile("export_user")
        profile.set_preference("verbosity", "Подробность объяснений", 0.8, 0.7)
        self.manager.record_interaction(InteractionType.COMMAND, "git status")

        # Экспортируем профиль
        export_path = os.path.join(self.test_dir, "exported_profile.json")
        success = self.manager.export_profile("export_user", export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))

        # Создаем новый менеджер и импортируем профиль
        new_manager = PersonalizationManager(storage_dir=tempfile.mkdtemp())
        user_id = new_manager.import_profile(export_path)

        # Проверяем импортированный профиль
        self.assertEqual(user_id, "export_user")
        imported_profile = new_manager.get_profile("export_user")
        self.assertIsNotNone(imported_profile)
        self.assertEqual(imported_profile.preferences["verbosity"].value, 0.8)
        self.assertEqual(len(imported_profile.recent_interactions), 1)

    def test_merge_profiles(self):
        """Тест объединения профилей"""
        # Создаем два профиля
        profile1 = self.manager.create_profile("user1")
        profile1.set_preference("verbosity", "Подробность объяснений", 0.8, 0.7)
        self.manager.record_interaction(InteractionType.COMMAND, "git status")

        profile2 = self.manager.create_profile("user2")
        profile2.set_preference("code_style", "Стиль кода", 0.6, 0.5)
        self.manager.record_interaction(InteractionType.FILE_ACCESS, "main.py", {"file_path": "main.py"})

        # Объединяем профили
        success = self.manager.merge_profiles("user1", "user2")
        self.assertTrue(success)

        # Проверяем результат объединения
        merged_profile = self.manager.get_profile("user2")
        self.assertIn("verbosity", merged_profile.preferences)
        self.assertIn("code_style", merged_profile.preferences)
        self.assertEqual(len(merged_profile.recent_interactions), 2)


class TestUserProfile(unittest.TestCase):
    """Тесты для UserProfile"""

    def test_add_interaction(self):
        """Тест добавления взаимодействия"""
        profile = UserProfile("test_user")
        interaction = UserInteraction(
            interaction_id="test_id",
            timestamp=datetime.now(),
            interaction_type=InteractionType.COMMAND,
            content="test command",
            success=True
        )

        profile.add_interaction(interaction)
        self.assertEqual(len(profile.recent_interactions), 1)
        self.assertEqual(profile.recent_interactions[0].content, "test command")

    def test_update_preference(self):
        """Тест обновления предпочтения"""
        profile = UserProfile("test_user")

        # Добавляем новое предпочтение
        profile.set_preference("test", "Test", 0.5, 0.5)
        self.assertEqual(profile.preferences["test"].value, 0.5)

        # Обновляем предпочтение
        profile.set_preference("test", "Test", 0.8, 0.6)
        self.assertNotEqual(profile.preferences["test"].value, 0.5)  # Значение должно измениться
        self.assertNotEqual(profile.preferences["test"].value, 0.8)  # Но не точно до 0.8 из-за учета уверенности

    def test_get_top_domains(self):
        """Тест получения основных доменов"""
        profile = UserProfile("test_user")

        # Добавляем домены
        profile.update_content_domain(ContentDomain.WEB_DEVELOPMENT, 0.8)
        profile.update_content_domain(ContentDomain.DATA_SCIENCE, 0.5)
        profile.update_content_domain(ContentDomain.BACKEND, 0.3)

        # Проверяем топ доменов
        top_domains = profile.get_top_domains(2)
        self.assertEqual(len(top_domains), 2)
        self.assertEqual(top_domains[0][0], ContentDomain.WEB_DEVELOPMENT)

    def test_to_and_from_dict(self):
        """Тест сериализации и десериализации"""
        profile = UserProfile("test_user")
        profile.set_preference("test", "Test", 0.5, 0.5)
        profile.update_content_domain(ContentDomain.WEB_DEVELOPMENT, 0.8)

        # Сериализуем
        data = profile.to_dict()

        # Десериализуем
        new_profile = UserProfile.from_dict(data)

        # Проверяем
        self.assertEqual(new_profile.user_id, "test_user")
        self.assertIn("test", new_profile.preferences)
        self.assertEqual(new_profile.preferences["test"].value, 0.5)
        self.assertIn(ContentDomain.WEB_DEVELOPMENT, new_profile.content_domains)


class TestUserInteraction(unittest.TestCase):
    """Тесты для UserInteraction"""

    def test_create(self):
        """Тест создания взаимодействия"""
        interaction = UserInteraction.create(
            InteractionType.COMMAND,
            "test command",
            {"param": "value"},
            True
        )

        self.assertEqual(interaction.interaction_type, InteractionType.COMMAND)
        self.assertEqual(interaction.content, "test command")
        self.assertEqual(interaction.metadata, {"param": "value"})
        self.assertTrue(interaction.success)


if __name__ == "__main__":
    unittest.main()
