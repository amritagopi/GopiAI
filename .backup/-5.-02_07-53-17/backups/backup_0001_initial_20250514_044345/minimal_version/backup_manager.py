#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Менеджер резервных копий для GopiAI.
Используется для создания и управления бэкапами в процессе пересборки проекта.
"""

import os
import sys
import json
import shutil
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backup_history.log"),
    ],
)
logger = logging.getLogger(__name__)

# Константы
BACKUP_ROOT = Path("../backups")
BACKUP_INDEX = BACKUP_ROOT / "backup_index.json"
IGNORE_PATTERNS = [
    ".git", "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    "venv", ".venv", "node_modules", "*.log", "*.bak",
    "backups", "*.zip", "*.tar", "*.gz", ".idea", ".vs"
]

class BackupManager:
    """Менеджер для создания и восстановления резервных копий проекта."""

    def __init__(self):
        """Инициализация менеджера резервных копий."""
        self.ensure_backup_dir()
        self.backup_index = self.load_backup_index()

    def ensure_backup_dir(self) -> None:
        """Создает директорию для резервных копий, если она не существует."""
        BACKUP_ROOT.mkdir(exist_ok=True, parents=True)
        if not BACKUP_INDEX.exists():
            self.save_backup_index({
                "backups": [],
                "current": "",
                "last_backup_id": 0
            })

    def load_backup_index(self) -> Dict:
        """Загружает индекс резервных копий из JSON-файла."""
        try:
            if BACKUP_INDEX.exists():
                with open(BACKUP_INDEX, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"backups": [], "current": "", "last_backup_id": 0}
        except Exception as e:
            logger.error(f"Ошибка при загрузке индекса резервных копий: {e}")
            return {"backups": [], "current": "", "last_backup_id": 0}

    def save_backup_index(self, index_data: Dict) -> None:
        """Сохраняет индекс резервных копий в JSON-файл."""
        try:
            with open(BACKUP_INDEX, "w", encoding="utf-8") as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка при сохранении индекса резервных копий: {e}")

    def should_ignore(self, path: str) -> bool:
        """Проверяет, должен ли путь быть исключен из резервного копирования."""
        for pattern in IGNORE_PATTERNS:
            if pattern.startswith("*"):
                if path.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                return True
        return False

    def create_backup(self, source_dir: str, tag: str, description: str) -> Tuple[bool, str]:
        """
        Создает резервную копию указанной директории.

        Args:
            source_dir: Путь к директории для резервного копирования
            tag: Тег для идентификации резервной копии (например, 'этап1', 'v1.0')
            description: Описание резервной копии

        Returns:
            Tuple[bool, str]: (успех, идентификатор резервной копии)
        """
        try:
            # Создаем уникальный идентификатор для бэкапа
            backup_id = self.backup_index["last_backup_id"] + 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{backup_id:04d}_{tag}_{timestamp}"

            # Создаем директорию для бэкапа
            backup_dir = BACKUP_ROOT / backup_name
            backup_dir.mkdir(exist_ok=True)

            # Копируем файлы
            source_path = Path(source_dir)
            file_count = 0

            for root, dirs, files in os.walk(source_path):
                # Пропускаем игнорируемые директории
                dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]

                for file in files:
                    src_file = os.path.join(root, file)
                    if self.should_ignore(src_file):
                        continue

                    # Определяем относительный путь
                    rel_path = os.path.relpath(src_file, source_path)
                    dest_file = backup_dir / rel_path

                    # Создаем директории при необходимости
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                    # Копируем файл
                    shutil.copy2(src_file, dest_file)
                    file_count += 1

            # Сохраняем метаданные
            metadata = {
                "id": backup_id,
                "name": backup_name,
                "tag": tag,
                "description": description,
                "timestamp": timestamp,
                "file_count": file_count,
                "source_dir": os.path.abspath(source_dir)
            }

            with open(backup_dir / "backup_info.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Обновляем индекс резервных копий
            self.backup_index["backups"].append(metadata)
            self.backup_index["last_backup_id"] = backup_id
            self.backup_index["current"] = backup_name
            self.save_backup_index(self.backup_index)

            logger.info(f"Создана резервная копия: {backup_name} ({file_count} файлов)")
            return True, backup_name

        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, ""

    def restore_backup(self, backup_id: str, target_dir: Optional[str] = None) -> bool:
        """
        Восстанавливает резервную копию.

        Args:
            backup_id: Идентификатор или имя резервной копии
            target_dir: Целевая директория для восстановления (по умолчанию - исходная директория)

        Returns:
            bool: Успех операции
        """
        try:
            # Находим бэкап по ID или имени
            backup_info = None

            try:
                # Пробуем найти по числовому ID
                id_num = int(backup_id)
                for backup in self.backup_index["backups"]:
                    if backup["id"] == id_num:
                        backup_info = backup
                        break
            except ValueError:
                # Пробуем найти по имени или тегу
                for backup in self.backup_index["backups"]:
                    if backup_id in backup["name"] or backup_id == backup["tag"]:
                        backup_info = backup
                        break

            if not backup_info:
                logger.error(f"Резервная копия не найдена: {backup_id}")
                return False

            # Определяем директории
            backup_dir = BACKUP_ROOT / backup_info["name"]
            if not backup_dir.exists():
                logger.error(f"Директория резервной копии не найдена: {backup_dir}")
                return False

            if target_dir is None:
                target_dir = backup_info["source_dir"]

            # Подтверждение восстановления
            print(f"\nВосстановление резервной копии: {backup_info['name']}")
            print(f"Описание: {backup_info['description']}")
            print(f"Создана: {backup_info['timestamp']}")
            print(f"Целевая директория: {target_dir}")
            confirm = input("\nЭта операция перезапишет файлы. Продолжить? (y/n): ")

            if confirm.lower() != 'y':
                logger.info("Восстановление отменено пользователем")
                return False

            # Восстанавливаем файлы
            target_path = Path(target_dir)
            file_count = 0

            # Копируем все файлы из бэкапа, кроме метаданных
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    if file == "backup_info.json":
                        continue

                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, backup_dir)
                    dest_file = target_path / rel_path

                    # Создаем директории при необходимости
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                    # Копируем файл
                    shutil.copy2(src_file, dest_file)
                    file_count += 1

            # Обновляем индекс
            self.backup_index["current"] = backup_info["name"]
            self.save_backup_index(self.backup_index)

            logger.info(f"Восстановлена резервная копия: {backup_info['name']} ({file_count} файлов)")
            return True

        except Exception as e:
            logger.error(f"Ошибка при восстановлении резервной копии: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def list_backups(self) -> None:
        """Выводит список всех резервных копий."""
        backups = self.backup_index["backups"]
        current = self.backup_index["current"]

        if not backups:
            print("Резервные копии отсутствуют")
            return

        print("\nСписок резервных копий:")
        print("-" * 80)
        print(f"{'ID':^5} | {'Тег':^10} | {'Дата':^16} | {'Файлы':^7} | Описание")
        print("-" * 80)

        for backup in sorted(backups, key=lambda x: x["id"]):
            is_current = " *" if backup["name"] == current else ""
            date_str = backup["timestamp"]
            print(
                f"{backup['id']:5d} | {backup['tag']:10} | {date_str:16} | "
                f"{backup['file_count']:7d} | {backup['description']}{is_current}"
            )

        print("-" * 80)
        print("* - текущая активная версия")

def create_backup_cmd(args):
    """Команда для создания резервной копии."""
    manager = BackupManager()
    success, backup_id = manager.create_backup(
        args.source_dir, args.tag, args.description
    )
    if success:
        print(f"Успешно создана резервная копия: {backup_id}")
    else:
        print("Ошибка при создании резервной копии")
        sys.exit(1)

def restore_backup_cmd(args):
    """Команда для восстановления резервной копии."""
    manager = BackupManager()
    success = manager.restore_backup(args.backup_id, args.target_dir)
    if success:
        print("Резервная копия успешно восстановлена")
    else:
        print("Ошибка при восстановлении резервной копии")
        sys.exit(1)

def list_backups_cmd(args):
    """Команда для вывода списка резервных копий."""
    manager = BackupManager()
    manager.list_backups()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Менеджер резервных копий для GopiAI")
    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # Команда создания резервной копии
    create_parser = subparsers.add_parser("create", help="Создать резервную копию")
    create_parser.add_argument(
        "--source-dir", "-s", default="..",
        help="Исходная директория для резервного копирования (по умолчанию: ..)"
    )
    create_parser.add_argument(
        "--tag", "-t", required=True,
        help="Тег для идентификации резервной копии (например, 'этап1')"
    )
    create_parser.add_argument(
        "--description", "-d", required=True,
        help="Описание резервной копии"
    )
    create_parser.set_defaults(func=create_backup_cmd)

    # Команда восстановления резервной копии
    restore_parser = subparsers.add_parser("restore", help="Восстановить резервную копию")
    restore_parser.add_argument(
        "backup_id", help="ID, имя или тег резервной копии для восстановления"
    )
    restore_parser.add_argument(
        "--target-dir", "-t",
        help="Целевая директория для восстановления (по умолчанию: исходная)"
    )
    restore_parser.set_defaults(func=restore_backup_cmd)

    # Команда вывода списка резервных копий
    list_parser = subparsers.add_parser("list", help="Показать список резервных копий")
    list_parser.set_defaults(func=list_backups_cmd)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
