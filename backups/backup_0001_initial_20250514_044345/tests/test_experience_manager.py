"""
Тесты для модуля экспорта и импорта накопленного опыта.

Проверяет функциональность ExperienceArchive.
"""

import os
import json
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.agent.experience_manager import ExperienceArchive
from app.agent.personalization_manager import PersonalizationManager
from app.agent.error_manager import ErrorManager


class TestExperienceArchive(unittest.TestCase):
    """Тесты для ExperienceArchive"""

    def setUp(self):
        """Подготовка перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()

        # Создаем временную директорию для хранения профилей
        self.profiles_dir = os.path.join(self.test_dir, "profiles")
        os.makedirs(self.profiles_dir, exist_ok=True)

        # Создаем моки для персонализации и ошибок
        self.personalization_manager = MagicMock(spec=PersonalizationManager)
        self.personalization_manager.storage_dir = self.profiles_dir

        self.error_manager = MagicMock(spec=ErrorManager)

        # Настраиваем моки
        self.personalization_manager.list_profiles.return_value = [
            {"user_id": "test_user1"},
            {"user_id": "test_user2"}
        ]

        self.personalization_manager.export_profile.return_value = True
        self.personalization_manager.import_profile.return_value = "test_user1"

        self.error_manager.export_learning_dataset.return_value = True
        self.error_manager.import_learning_dataset.return_value = 10
        self.error_manager.get_error_statistics.return_value = {"total_errors": 10}

        # Создаем архив опыта
        self.archive = ExperienceArchive(
            base_dir=os.path.join(self.test_dir, "archives"),
            personalization_manager=self.personalization_manager,
            error_manager=self.error_manager
        )

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)

    def test_create_archive(self):
        """Тестирует создание архива опыта"""
        # Создаем архив
        result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Проверяем успешность создания
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["archive_path"]))
        self.assertIn("test_archive", result["archive_name"])
        self.assertEqual(["test_user1"], result["profiles_included"])

        # Проверяем вызовы методов
        self.personalization_manager.export_profile.assert_called_with(
            "test_user1",
            os.path.join(self.archive.base_dir, "temp_", "profiles", "test_user1.json")
        )

        self.error_manager.export_learning_dataset.assert_called_once()
        self.error_manager.get_error_statistics.assert_called_once()

    def test_list_archives(self):
        """Тестирует получение списка архивов"""
        # Создаем архив
        result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Получаем список архивов
        archives = self.archive.list_archives()

        # Проверяем результат
        self.assertEqual(1, len(archives))
        self.assertEqual(result["archive_name"], archives[0]["filename"])

    def test_import_archive(self):
        """Тестирует импорт архива"""
        # Создаем архив
        create_result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Импортируем архив
        import_result = self.archive.import_archive(
            archive_path=create_result["archive_path"],
            import_profiles=True,
            import_errors=True,
            merge_existing=True
        )

        # Проверяем результат
        self.assertTrue(import_result["success"])
        self.assertIn("test_user1", import_result["results"]["imported_profiles"])
        self.assertTrue(import_result["results"]["imported_errors"])

        # Проверяем вызовы методов
        self.personalization_manager.import_profile.assert_called_once()
        self.error_manager.import_learning_dataset.assert_called_once()

    def test_extract_archive_metadata(self):
        """Тестирует извлечение метаданных из архива"""
        # Создаем архив
        create_result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Извлекаем метаданные
        metadata = self.archive._extract_archive_metadata(create_result["archive_path"])

        # Проверяем результат
        self.assertIsNotNone(metadata)
        self.assertEqual("test_archive", metadata["archive_name"])
        self.assertEqual(["test_user1"], metadata["profiles"])
        self.assertTrue(metadata["includes_errors"])

    def test_delete_archive(self):
        """Тестирует удаление архива"""
        # Создаем архив
        create_result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Удаляем архив
        success = self.archive.delete_archive(create_result["archive_name"])

        # Проверяем результат
        self.assertTrue(success)
        self.assertFalse(os.path.exists(create_result["archive_path"]))

    def test_extract_aggregate_statistics(self):
        """Тестирует извлечение агрегированной статистики из архива"""
        # Создаем тестовые данные для профиля
        test_profile_dir = os.path.join(self.test_dir, "temp_profile")
        os.makedirs(test_profile_dir, exist_ok=True)

        # Создаем тестовый профиль
        test_profile = {
            "user_id": "test_user1",
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "preferences": {
                "verbosity": {
                    "preference_id": "verbosity",
                    "name": "Подробность объяснений",
                    "value": 0.7,
                    "confidence": 0.8,
                    "last_updated": datetime.now().isoformat(),
                    "evidence_count": 5
                }
            },
            "recent_interactions": [
                {
                    "interaction_id": "test_interaction",
                    "timestamp": datetime.now().isoformat(),
                    "interaction_type": "command",
                    "content": "test command",
                    "metadata": {},
                    "success": True,
                    "duration": 0.5
                }
            ],
            "content_domains": {"web_development": 0.8, "backend": 0.5},
            "frequent_tasks": {"code_generation": 5, "code_explanation": 3},
            "common_files": {"main.py": 10, "app/config.py": 5}
        }

        # Сохраняем тестовый профиль
        with open(os.path.join(test_profile_dir, "test_user1.json"), "w", encoding="utf-8") as f:
            json.dump(test_profile, f, ensure_ascii=False, indent=2)

        # Переопределяем мок для экспорта профиля
        def export_profile_side_effect(user_id, output_path):
            shutil.copy(
                os.path.join(test_profile_dir, "test_user1.json"),
                output_path
            )
            return True

        self.personalization_manager.export_profile.side_effect = export_profile_side_effect

        # Создаем архив
        create_result = self.archive.create_archive(
            archive_name="test_archive",
            profiles_to_include=["test_user1"],
            include_errors=True,
            include_metadata=True
        )

        # Извлекаем статистику
        stats = self.archive.extract_aggregate_statistics(create_result["archive_path"])

        # Проверяем результат
        self.assertIn("profiles", stats)
        self.assertIn("errors", stats)
        self.assertIn("metadata", stats)

        # Проверяем статистику профилей
        profiles_stats = stats["profiles"]
        self.assertEqual(1, profiles_stats["profiles_count"])
        self.assertIn("top_domains", profiles_stats)
        self.assertIn("top_tasks", profiles_stats)
        self.assertIn("preferences", profiles_stats)


if __name__ == "__main__":
    unittest.main()
