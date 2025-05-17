"""
Модуль управления накопленным опытом для Reasoning Agent

Обеспечивает функциональность для экспорта, импорта и объединения
накопленного опыта взаимодействия с пользователем.
"""

import os
import json
import shutil
import zipfile
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

from app.agent.personalization_manager import PersonalizationManager, UserProfile
from app.agent.error_manager import ErrorManager
from app.logger import logger


class ExperienceArchive:
    """
    Класс для управления архивами накопленного опыта.

    Поддерживает экспорт, импорт и объединение опыта из разных источников.
    """

    def __init__(self,
                 base_dir: str = "data/experience_archives",
                 personalization_manager: Optional[PersonalizationManager] = None,
                 error_manager: Optional[ErrorManager] = None):
        """
        Инициализирует менеджер архивов опыта.

        Args:
            base_dir: Директория для хранения архивов
            personalization_manager: Менеджер персонализации
            error_manager: Менеджер ошибок
        """
        self.base_dir = base_dir
        self.personalization_manager = personalization_manager
        self.error_manager = error_manager

        # Создаем директорию для архивов, если она не существует
        os.makedirs(base_dir, exist_ok=True)

        logger.info(f"ExperienceArchive: инициализирован с хранилищем в {base_dir}")

    def create_archive(self,
                      archive_name: str,
                      profiles_to_include: Optional[List[str]] = None,
                      include_errors: bool = True,
                      include_metadata: bool = True) -> Dict[str, Any]:
        """
        Создает архив накопленного опыта.

        Args:
            archive_name: Имя архива (без расширения)
            profiles_to_include: Список ID профилей для включения (None - все)
            include_errors: Включить данные об ошибках
            include_metadata: Включить метаданные

        Returns:
            Словарь с результатами операции
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Персонализация не инициализирована"
            }

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"{archive_name}_{timestamp}.zip"
            archive_path = os.path.join(self.base_dir, archive_filename)

            temp_dir = os.path.join(self.base_dir, f"temp_{timestamp}")
            os.makedirs(temp_dir, exist_ok=True)

            # Получаем все профили, если не указаны конкретные
            if profiles_to_include is None:
                profiles_list = self.personalization_manager.list_profiles()
                profiles_to_include = [p["user_id"] for p in profiles_list]

            # Экспортируем профили
            profiles_dir = os.path.join(temp_dir, "profiles")
            os.makedirs(profiles_dir, exist_ok=True)

            for user_id in profiles_to_include:
                profile_path = os.path.join(profiles_dir, f"{user_id}.json")
                self.personalization_manager.export_profile(user_id, profile_path)

            # Экспортируем данные об ошибках, если включено
            if include_errors and self.error_manager:
                errors_dir = os.path.join(temp_dir, "errors")
                os.makedirs(errors_dir, exist_ok=True)
                self.error_manager.export_learning_dataset(
                    os.path.join(errors_dir, "errors_dataset.json")
                )

                # Экспортируем статистику ошибок
                with open(os.path.join(errors_dir, "error_statistics.json"), "w", encoding="utf-8") as f:
                    json.dump(self.error_manager.get_error_statistics(), f, ensure_ascii=False, indent=2)

            # Создаем метаданные, если включено
            if include_metadata:
                metadata = {
                    "archive_name": archive_name,
                    "created_at": datetime.datetime.now().isoformat(),
                    "profiles": profiles_to_include,
                    "includes_errors": include_errors,
                    "version": "1.0"
                }

                with open(os.path.join(temp_dir, "metadata.json"), "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

            # Создаем ZIP-архив
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, relative_path)

            # Удаляем временную директорию
            shutil.rmtree(temp_dir)

            logger.info(f"ExperienceArchive: создан архив {archive_filename}")

            return {
                "success": True,
                "archive_path": archive_path,
                "archive_name": archive_filename,
                "profiles_included": profiles_to_include
            }

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка создания архива: {str(e)}")
            # Удаляем временную директорию при ошибке
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            return {
                "success": False,
                "error": f"Ошибка создания архива: {str(e)}"
            }

    def import_archive(self,
                      archive_path: str,
                      import_profiles: bool = True,
                      import_errors: bool = True,
                      merge_existing: bool = True) -> Dict[str, Any]:
        """
        Импортирует архив накопленного опыта.

        Args:
            archive_path: Путь к архиву
            import_profiles: Импортировать профили
            import_errors: Импортировать данные об ошибках
            merge_existing: Объединять с существующими данными

        Returns:
            Словарь с результатами операции
        """
        if not os.path.exists(archive_path):
            return {
                "success": False,
                "error": f"Архив не найден: {archive_path}"
            }

        temp_dir = os.path.join(self.base_dir, f"temp_import_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

        try:
            # Распаковываем архив
            os.makedirs(temp_dir, exist_ok=True)

            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(temp_dir)

            # Проверяем метаданные
            metadata_path = os.path.join(temp_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    logger.info(f"ExperienceArchive: импорт архива {metadata.get('archive_name')}, создан {metadata.get('created_at')}")

            results = {
                "imported_profiles": [],
                "imported_errors": False,
                "metadata": metadata if os.path.exists(metadata_path) else None
            }

            # Импортируем профили
            if import_profiles and self.personalization_manager:
                profiles_dir = os.path.join(temp_dir, "profiles")
                if os.path.exists(profiles_dir):
                    profile_files = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]

                    for profile_file in profile_files:
                        profile_path = os.path.join(profiles_dir, profile_file)

                        # Импортируем профиль
                        imported_user_id = self.personalization_manager.import_profile(profile_path)

                        if imported_user_id:
                            results["imported_profiles"].append(imported_user_id)

                            # Если нужно объединить с существующим профилем
                            if merge_existing and imported_user_id != "default_user":
                                # Проверяем, существует ли профиль по умолчанию
                                default_profile = self.personalization_manager.get_profile("default_user")
                                if default_profile:
                                    # Объединяем импортированный профиль с профилем по умолчанию
                                    self.personalization_manager.merge_profiles(imported_user_id, "default_user")
                                    logger.info(f"ExperienceArchive: профиль {imported_user_id} объединен с default_user")

            # Импортируем данные об ошибках
            if import_errors and self.error_manager:
                errors_dir = os.path.join(temp_dir, "errors")
                errors_dataset_path = os.path.join(errors_dir, "errors_dataset.json")

                if os.path.exists(errors_dataset_path):
                    imported_count = self.error_manager.import_learning_dataset(errors_dataset_path)
                    results["imported_errors"] = True
                    results["imported_errors_count"] = imported_count
                    logger.info(f"ExperienceArchive: импортировано {imported_count} записей о ошибках")

            # Удаляем временную директорию
            shutil.rmtree(temp_dir)

            return {
                "success": True,
                "results": results
            }

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка импорта архива: {str(e)}")
            # Удаляем временную директорию при ошибке
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            return {
                "success": False,
                "error": f"Ошибка импорта архива: {str(e)}"
            }

    def list_archives(self) -> List[Dict[str, Any]]:
        """
        Возвращает список доступных архивов.

        Returns:
            Список информации об архивах
        """
        result = []

        try:
            for filename in os.listdir(self.base_dir):
                if filename.endswith(".zip"):
                    file_path = os.path.join(self.base_dir, filename)
                    file_info = os.stat(file_path)

                    # Извлекаем метаданные из архива, если возможно
                    metadata = self._extract_archive_metadata(file_path)

                    archive_info = {
                        "filename": filename,
                        "path": file_path,
                        "size": file_info.st_size,
                        "created": datetime.datetime.fromtimestamp(file_info.st_ctime).isoformat(),
                        "metadata": metadata
                    }

                    result.append(archive_info)

            # Сортируем по времени создания (от новых к старым)
            result.sort(key=lambda x: x["created"], reverse=True)

            return result

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка получения списка архивов: {str(e)}")
            return []

    def _extract_archive_metadata(self, archive_path: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает метаданные из архива.

        Args:
            archive_path: Путь к архиву

        Returns:
            Словарь с метаданными или None в случае ошибки
        """
        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                if "metadata.json" in zipf.namelist():
                    with zipf.open("metadata.json") as f:
                        return json.load(f)

            return None

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка извлечения метаданных из архива {archive_path}: {str(e)}")
            return None

    def delete_archive(self, archive_filename: str) -> bool:
        """
        Удаляет архив.

        Args:
            archive_filename: Имя файла архива

        Returns:
            True в случае успеха, False в случае ошибки
        """
        file_path = os.path.join(self.base_dir, archive_filename)

        if not os.path.exists(file_path):
            logger.warning(f"ExperienceArchive: архив не найден: {archive_filename}")
            return False

        try:
            os.remove(file_path)
            logger.info(f"ExperienceArchive: архив удален: {archive_filename}")
            return True

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка удаления архива {archive_filename}: {str(e)}")
            return False

    def extract_aggregate_statistics(self,
                                    archive_path: str) -> Dict[str, Any]:
        """
        Извлекает агрегированную статистику из архива.

        Args:
            archive_path: Путь к архиву

        Returns:
            Словарь со статистикой
        """
        temp_dir = os.path.join(self.base_dir, f"temp_stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

        try:
            # Распаковываем архив
            os.makedirs(temp_dir, exist_ok=True)

            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(temp_dir)

            # Анализируем профили
            profiles_dir = os.path.join(temp_dir, "profiles")
            profiles_stats = self._analyze_profiles_directory(profiles_dir)

            # Анализируем ошибки
            errors_dir = os.path.join(temp_dir, "errors")
            errors_stats = {}

            errors_stats_path = os.path.join(errors_dir, "error_statistics.json")
            if os.path.exists(errors_stats_path):
                with open(errors_stats_path, "r", encoding="utf-8") as f:
                    errors_stats = json.load(f)

            # Получаем метаданные
            metadata = {}
            metadata_path = os.path.join(temp_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

            # Формируем агрегированную статистику
            statistics = {
                "profiles": profiles_stats,
                "errors": errors_stats,
                "metadata": metadata
            }

            # Удаляем временную директорию
            shutil.rmtree(temp_dir)

            return statistics

        except Exception as e:
            logger.error(f"ExperienceArchive: ошибка извлечения статистики из архива: {str(e)}")
            # Удаляем временную директорию при ошибке
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            return {
                "error": f"Ошибка извлечения статистики: {str(e)}"
            }

    def _analyze_profiles_directory(self, profiles_dir: str) -> Dict[str, Any]:
        """
        Анализирует директорию с профилями.

        Args:
            profiles_dir: Путь к директории с профилями

        Returns:
            Словарь со статистикой профилей
        """
        if not os.path.exists(profiles_dir):
            return {}

        profiles = []
        domains_counter = {}
        tasks_counter = {}
        preferences_stats = {}
        total_interactions = 0

        for filename in os.listdir(profiles_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(profiles_dir, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        profile_data = json.load(f)

                        # Добавляем базовую информацию о профиле
                        profiles.append({
                            "user_id": profile_data.get("user_id"),
                            "created_at": profile_data.get("created_at"),
                            "last_active": profile_data.get("last_active"),
                            "interactions_count": len(profile_data.get("recent_interactions", []))
                        })

                        # Подсчитываем общее количество взаимодействий
                        total_interactions += len(profile_data.get("recent_interactions", []))

                        # Агрегируем домены контента
                        for domain, value in profile_data.get("content_domains", {}).items():
                            if domain in domains_counter:
                                domains_counter[domain] += value
                            else:
                                domains_counter[domain] = value

                        # Агрегируем частые задачи
                        for task, count in profile_data.get("frequent_tasks", {}).items():
                            if task in tasks_counter:
                                tasks_counter[task] += count
                            else:
                                tasks_counter[task] = count

                        # Анализируем предпочтения
                        for pref_id, pref_data in profile_data.get("preferences", {}).items():
                            if pref_id not in preferences_stats:
                                preferences_stats[pref_id] = {
                                    "name": pref_data.get("name"),
                                    "values": [],
                                    "confidences": []
                                }

                            preferences_stats[pref_id]["values"].append(pref_data.get("value", 0.5))
                            preferences_stats[pref_id]["confidences"].append(pref_data.get("confidence", 0.0))

                except Exception as e:
                    logger.error(f"ExperienceArchive: ошибка анализа профиля {filename}: {str(e)}")

        # Вычисляем средние значения предпочтений
        for pref_id, stats in preferences_stats.items():
            if stats["values"]:
                stats["avg_value"] = sum(stats["values"]) / len(stats["values"])
            else:
                stats["avg_value"] = 0.5

            if stats["confidences"]:
                stats["avg_confidence"] = sum(stats["confidences"]) / len(stats["confidences"])
            else:
                stats["avg_confidence"] = 0.0

            # Удаляем списки, оставляем только средние значения
            del stats["values"]
            del stats["confidences"]

        # Сортируем домены и задачи по убыванию значимости
        sorted_domains = sorted(domains_counter.items(), key=lambda x: x[1], reverse=True)
        sorted_tasks = sorted(tasks_counter.items(), key=lambda x: x[1], reverse=True)

        return {
            "profiles_count": len(profiles),
            "profiles": profiles,
            "total_interactions": total_interactions,
            "top_domains": dict(sorted_domains[:5]),
            "top_tasks": dict(sorted_tasks[:5]),
            "preferences": preferences_stats
        }
