"""
Централизованная система управления путями для проекта GopiAI.
Обеспечивает безопасное добавление путей в sys.path и предотвращает дублирование.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class PathManager:
    """Менеджер для управления путями в sys.path"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.added_paths = set()

    def add_path(self, path: str, position: int = -1) -> bool:
        """
        Безопасно добавить путь в sys.path

        Args:
            path: Путь для добавления
            position: Позиция в sys.path (-1 для append, 0 для insert в начало)

        Returns:
            bool: True если путь был добавлен, False если уже существует или не существует
        """
        path = str(path)

        # Проверяем существование директории
        if not os.path.isdir(path):
            print(f"[WARNING] Путь не существует: {path}")
            return False

        # Проверяем, не добавлен ли уже путь
        if path in sys.path:
            return False

        # Добавляем путь
        if position == 0:
            sys.path.insert(0, path)
        else:
            sys.path.append(path)

        self.added_paths.add(path)
        print(f"[INFO] Добавлен путь: {path}")
        return True

    def add_project_paths(self):
        """Добавить основные пути проекта"""
        paths_to_add = [
            # Основные модули
            self.project_root / "GopiAI-CrewAI",
            self.project_root / "GopiAI-UI",
            self.project_root / "GopiAI-Assets",

            # Инструменты
            self.project_root / "GopiAI-CrewAI" / "tools",

            # Тестовая инфраструктура
            self.project_root / "test_infrastructure",

            # CI/CD
            self.project_root / "ci_cd",
        ]

        for path in paths_to_add:
            self.add_path(str(path), position=0)

    def add_gopiai_integration(self) -> bool:
        """
        Добавить путь к gopiai_integration если существует

        Returns:
            bool: True если путь был добавлен
        """
        # Сначала проверяем основную директорию
        primary_path = self.project_root / "GopiAI-CrewAI" / "tools" / "gopiai_integration"
        if self.add_path(str(primary_path), position=0):
            return True

        # Если основной путь не существует, проверяем backup
        backup_path = self.project_root / "GopiAI-CrewAI" / "tools_backup_20250828_101657" / "gopiai_integration"
        if self.add_path(str(backup_path), position=0):
            print("[WARNING] Используется backup версия gopiai_integration")
            return True

        print("[ERROR] Модуль gopiai_integration не найден ни в основной, ни в backup директории")
        return False

    def cleanup_invalid_paths(self):
        """Удалить недействительные пути из sys.path"""
        invalid_paths = []
        for path in sys.path:
            if not os.path.isdir(path):
                invalid_paths.append(path)

        for path in invalid_paths:
            sys.path.remove(path)
            print(f"[INFO] Удален недействительный путь: {path}")

    def get_path_stats(self) -> dict:
        """Получить статистику по путям"""
        return {
            "total_paths": len(sys.path),
            "added_by_manager": len(self.added_paths),
            "invalid_paths": len([p for p in sys.path if not os.path.isdir(p)])
        }


# Глобальный экземпляр менеджера
path_manager = PathManager()


def setup_project_paths():
    """Настроить пути проекта - основная функция для импорта"""
    path_manager.cleanup_invalid_paths()
    path_manager.add_project_paths()
    return path_manager


def add_gopiai_integration():
    """Добавить gopiai_integration в путь"""
    return path_manager.add_gopiai_integration()


def get_path_manager():
    """Получить экземпляр менеджера путей"""
    return path_manager