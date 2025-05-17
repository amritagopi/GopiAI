"""
Модуль для работы с иконками Lucide в GopiAI.

Предоставляет интерфейс для использования минималистичных иконок Lucide
в приложении с интеграцией в Qt/PySide6.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Union

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)


class LucideIconManager:
    """Менеджер для работы с иконками Lucide в приложении GopiAI."""

    _instance = None
    _cache = {}  # Кеш для иконок

    @classmethod
    def instance(cls):
        """Получение единственного экземпляра менеджера иконок (паттерн Singleton)."""
        if cls._instance is None:
            cls._instance = LucideIconManager()
        return cls._instance

    def __init__(self):
        """Инициализация менеджера иконок Lucide."""
        self.icons_dir = self._get_icons_directory()
        self.available_icons = self._scan_available_icons()
        logger.info(
            f"LucideIconManager инициализирован. Найдено {len(self.available_icons)} иконок."
        )

    def _get_icons_directory(self) -> Path:
        """Получение пути к директории с иконками Lucide."""
        # Корень проекта
        project_root = Path(
            os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )

        # Путь к иконкам Lucide в node_modules
        lucide_path = project_root / "node_modules" / "lucide" / "dist" / "svg"

        # Если путь не существует, создаем локальную директорию для иконок
        if not lucide_path.exists():
            fallback_path = project_root / "assets" / "icons" / "lucide"
            fallback_path.mkdir(parents=True, exist_ok=True)
            logger.warning(
                f"Директория Lucide не найдена в node_modules. Используем {fallback_path}"
            )
            return fallback_path

        return lucide_path

    def _scan_available_icons(self) -> Dict[str, Path]:
        """Сканирование доступных иконок в директориях."""
        icons = {}

        # Список директорий для поиска иконок в порядке приоритета
        icon_dirs = [
            self.icons_dir,  # Основная директория (может быть assets или node_modules)
            Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            / "assets"
            / "icons"
            / "lucide",  # Локальная директория
            Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            / "node_modules"
            / "lucide"
            / "dist"
            / "svg",  # node_modules
        ]

        # Удаляем дубликаты путей
        unique_dirs = []
        for dir_path in icon_dirs:
            if dir_path not in unique_dirs:
                unique_dirs.append(dir_path)

        # Сканируем каждую директорию
        for icon_dir in unique_dirs:
            if not icon_dir.exists():
                logger.debug(f"Директория с иконками не существует: {icon_dir}")
                continue

            logger.info(f"Сканирование иконок в директории: {icon_dir}")
            count = 0

            try:
                for file_path in icon_dir.glob("*.svg"):
                    try:
                        icon_name = file_path.stem
                        # Если такая иконка уже есть, пропускаем (поддерживаем приоритет директорий)
                        if icon_name not in icons:
                            icons[icon_name] = file_path
                            count += 1
                    except Exception as e:
                        logger.warning(f"Ошибка обработки файла {file_path}: {e}")

                logger.info(f"Найдено {count} иконок в {icon_dir}")
            except Exception as e:
                logger.error(f"Ошибка при сканировании директории {icon_dir}: {e}")

        # Добавляем alias-ы для иконок (например, file-text -> file_text)
        aliases = {}
        for name, path in list(icons.items()):
            # Для иконок с дефисами добавляем вариант с подчеркиванием
            if "-" in name:
                alias = name.replace("-", "_")
                if alias not in icons:
                    aliases[alias] = path

        # Добавляем алиасы в основной словарь
        icons.update(aliases)

        total_count = len(icons)
        if total_count == 0:
            logger.warning("Не найдено ни одной SVG иконки!")
        else:
            logger.info(f"Всего найдено {total_count} иконок (включая алиасы)")

        return icons

    def get_icon(
        self,
        icon_name: str,
        color: Optional[str] = None,
        size: Union[QSize, int] = QSize(24, 24),
    ) -> QIcon:
        """
        Получение иконки Lucide по имени.

        Args:
            icon_name: Имя иконки
            color: Цвет иконки в формате CSS (#RRGGBB)
            size: Размер иконки (QSize или int)

        Returns:
            QIcon: Объект иконки Qt
        """
        # Нормализуем имя иконки (заменяем дефисы на подчеркивания для совместимости)
        normalized_name = icon_name.replace("-", "_")

        # Если передано число как размер, создаем QSize
        if isinstance(size, int):
            size = QSize(size, size)

        # Создаем ключ для кеширования
        cache_key = f"{normalized_name}_{color}_{size.width()}x{size.height()}"

        # Проверяем кеш
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Если иконка не найдена среди доступных
        if (
            normalized_name not in self.available_icons
            and icon_name not in self.available_icons
        ):
            logger.warning(f"Иконка не найдена: {icon_name}. Используем fallback.")
            # Можно вернуть дефолтную иконку или пустую
            return self._get_fallback_icon(size)

        # Получаем путь к SVG файлу
        if normalized_name in self.available_icons:
            svg_path = self.available_icons[normalized_name]
        else:
            svg_path = self.available_icons[icon_name]

        # Создаем иконку из SVG
        try:
            icon = self._create_icon_from_svg(svg_path, color, size)
            # Кешируем иконку
            self._cache[cache_key] = icon
            return icon
        except Exception as e:
            logger.error(f"Ошибка при создании иконки {icon_name}: {e}")
            return self._get_fallback_icon(size)

    def _create_icon_from_svg(
        self, svg_path: Path, color: Optional[str], size: QSize
    ) -> QIcon:
        """Создание QIcon из SVG файла с опциональным изменением цвета."""
        icon = QIcon()

        try:
            # Проверяем существование файла
            if not svg_path.exists():
                logger.error(f"SVG файл не существует: {svg_path}")
                return self._get_fallback_icon(size)

            # Читаем содержимое SVG файла
            try:
                with open(svg_path, "r", encoding="utf-8") as f:
                    svg_content = f.read()
            except Exception as e:
                logger.error(f"Ошибка чтения SVG файла {svg_path}: {e}")
                return self._get_fallback_icon(size)

            # Проверяем, что файл содержит валидный SVG
            if not svg_content or "<svg" not in svg_content:
                logger.error(f"Файл {svg_path} не содержит валидный SVG код")
                return self._get_fallback_icon(size)

            # Если указан цвет, изменяем stroke и fill в SVG
            if color:
                try:
                    svg_content = svg_content.replace(
                        'stroke="currentColor"', f'stroke="{color}"'
                    )
                    svg_content = svg_content.replace(
                        'fill="currentColor"', f'fill="{color}"'
                    )
                except Exception as e:
                    logger.warning(f"Ошибка при изменении цвета SVG {svg_path}: {e}")
                    # Продолжаем с оригинальным SVG, без изменения цвета

            # Создаем рендерер SVG
            renderer = QSvgRenderer()

            # Загружаем SVG в рендерер
            if not renderer.load(svg_content.encode("utf-8")):
                logger.error(f"Не удалось загрузить SVG из {svg_path} в рендерер")
                return self._get_fallback_icon(size)

            # Проверяем, что размер валидный
            if size.width() <= 0 or size.height() <= 0:
                logger.warning(
                    f"Некорректный размер {size} для {svg_path}, используем 24x24"
                )
                size = QSize(24, 24)

            try:
                # Создаем пустой QPixmap нужного размера
                pixmap = QPixmap(size)
                pixmap.fill(Qt.transparent)  # Прозрачный фон

                # Рисуем SVG на pixmap
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()

                # Добавляем pixmap в иконку
                icon.addPixmap(pixmap)

                # Также добавляем версию иконки для состояния Disabled, чтобы она выглядела серой
                disabled_pixmap = QPixmap(size)
                disabled_pixmap.fill(Qt.transparent)

                painter = QPainter(disabled_pixmap)
                # Устанавливаем непрозрачность 50% для отключенного состояния
                painter.setOpacity(0.5)
                renderer.render(painter)
                painter.end()

                icon.addPixmap(disabled_pixmap, QIcon.Disabled)

                return icon
            except Exception as e:
                logger.error(f"Ошибка при рендеринге SVG {svg_path}: {e}")
                return self._get_fallback_icon(size)
        except Exception as e:
            logger.error(
                f"Непредвиденная ошибка при создании иконки из {svg_path}: {e}"
            )
            return self._get_fallback_icon(size)

        return icon

    def _get_fallback_icon(self, size: QSize) -> QIcon:
        """Создание заметной иконки-заполнителя для случаев, когда запрошенная иконка не найдена."""
        icon = QIcon()

        try:
            # Создаем пустой QPixmap нужного размера
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)  # Прозрачный фон

            # Создаем QPainter для рисования
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Устанавливаем перо для рисования
            pen = QPen(QColor("#FF5555"))  # Красное перо
            pen.setWidth(2)
            painter.setPen(pen)

            # Рисуем крестик
            margin = size.width() // 4
            painter.drawLine(
                margin, margin, size.width() - margin, size.height() - margin
            )
            painter.drawLine(
                margin, size.height() - margin, size.width() - margin, margin
            )

            # Рисуем рамку
            painter.drawRect(1, 1, size.width() - 2, size.height() - 2)

            # Завершаем рисование
            painter.end()

            # Добавляем pixmap в иконку
            icon.addPixmap(pixmap)

            return icon
        except Exception as e:
            logger.error(f"Ошибка при создании fallback иконки: {e}")
            # В случае ошибки, возвращаем простой прозрачный pixmap
            fallback_pixmap = QPixmap(size)
            fallback_pixmap.fill(Qt.transparent)
            return QIcon(fallback_pixmap)

    def clear_cache(self):
        """Очистка кеша иконок."""
        self._cache.clear()
        logger.info("Кеш иконок очищен")

    def list_available_icons(self) -> list:
        """Получение списка всех доступных иконок."""
        return sorted(list(self.available_icons.keys()))

    def extract_icons_from_node_modules(self):
        """
        Извлечение иконок из node_modules/lucide в assets/icons/lucide.
        Используется, если необходимо скопировать иконки локально.
        """
        project_root = Path(
            os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        )
        source_path = project_root / "node_modules" / "lucide" / "dist" / "svg"
        target_path = project_root / "assets" / "icons" / "lucide"

        if not source_path.exists():
            logger.error(f"Исходная директория не существует: {source_path}")
            return False

        # Создаем целевую директорию, если она не существует
        target_path.mkdir(parents=True, exist_ok=True)

        # Копируем все SVG файлы
        import shutil

        count = 0
        for svg_file in source_path.glob("*.svg"):
            shutil.copy2(svg_file, target_path / svg_file.name)
            count += 1

        logger.info(f"Скопировано {count} иконок из {source_path} в {target_path}")
        return True

    def generate_icon_index(self, output_path: Optional[Path] = None):
        """
        Генерация JSON-индекса всех доступных иконок.
        Полезно для документации и отладки.
        """
        if output_path is None:
            project_root = Path(
                os.path.abspath(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                )
            )
            output_path = project_root / "assets" / "icons" / "lucide_index.json"

        index = {
            "total": len(self.available_icons),
            "icons": sorted(list(self.available_icons.keys())),
            "source_directory": str(self.icons_dir),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

        logger.info(f"Индекс иконок сохранен в {output_path}")
        return output_path


# Алиас для совместимости со старым кодом
def get_lucide_icon(icon_name, color=None, size=24):
    """Функция для получения иконки Lucide (для обратной совместимости)."""
    return LucideIconManager.instance().get_icon(icon_name, color, size)
