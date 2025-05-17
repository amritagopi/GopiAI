#!/usr/bin/env python
"""
Скрипт для сброса кеша иконок и перезагрузки всех иконок Lucide в приложении.
Запустите этот скрипт, если иконки отображаются некорректно.
"""

import logging
import os
import shutil
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("reset_icon_cache")


def clear_icon_cache():
    """Очищает кеш иконок приложения."""
    # Получаем путь к корню проекта
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))

    # Путь к кешу иконок
    cache_dirs = [
        project_root / ".cache" / "icons",  # Возможный путь к кешу
        project_root / "assets" / "icons" / "cache",  # Другой возможный путь
    ]

    found = False
    for cache_dir in cache_dirs:
        if cache_dir.exists() and cache_dir.is_dir():
            logger.info(f"Очистка кеша иконок в: {cache_dir}")
            try:
                # Удаляем содержимое директории
                for item in cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                logger.info(f"Кеш иконок успешно очищен: {cache_dir}")
                found = True
            except Exception as e:
                logger.error(f"Ошибка при очистке кеша: {e}")

    if not found:
        logger.info("Директории кеша иконок не найдены")


def ensure_lucide_icons():
    """Проверяет наличие Lucide иконок и создает их копию в assets/icons/lucide, если нужно."""
    # Получаем путь к корню проекта
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))

    # Пути к иконкам
    node_modules_path = project_root / "node_modules" / "lucide" / "dist" / "svg"
    assets_path = project_root / "assets" / "icons" / "lucide"

    # Проверяем наличие иконок в assets
    if not assets_path.exists() or not any(assets_path.glob("*.svg")):
        logger.info(f"Иконки не найдены в {assets_path}, проверяем node_modules")

        # Проверяем наличие иконок в node_modules
        if node_modules_path.exists() and any(node_modules_path.glob("*.svg")):
            logger.info(f"Копируем иконки из {node_modules_path} в {assets_path}")

            # Создаем директорию, если её нет
            assets_path.mkdir(parents=True, exist_ok=True)

            # Копируем все SVG файлы
            count = 0
            for svg_file in node_modules_path.glob("*.svg"):
                shutil.copy2(svg_file, assets_path / svg_file.name)
                count += 1

            logger.info(f"Скопировано {count} SVG иконок")
        else:
            logger.warning("Иконки Lucide не найдены ни в assets, ни в node_modules")
            logger.info(
                "Проверьте установку библиотеки Lucide и перезапустите приложение"
            )
    else:
        logger.info(f"Иконки Lucide найдены в {assets_path}")
        logger.info(f"Найдено {len(list(assets_path.glob('*.svg')))} SVG-файлов")


def reset_lucide_manager():
    """Попытка сбросить состояние LucideIconManager через импорт."""
    try:
        from app.ui.icon_adapter import IconAdapter
        from app.ui.lucide_icon_manager import LucideIconManager

        # Очищаем кеш иконок в менеджерах
        IconAdapter.instance().clear_cache()
        LucideIconManager.instance().clear_cache()

        logger.info("Кеши иконок в менеджерах очищены")
    except ImportError:
        logger.warning(
            "Не удалось импортировать менеджеры иконок - запустите скрипт из корня проекта"
        )
    except Exception as e:
        logger.error(f"Ошибка при сбросе менеджеров иконок: {e}")


def main():
    """Основная функция скрипта."""
    logger.info("Начинаем сброс кеша иконок...")

    # Очистка кеша
    clear_icon_cache()

    # Проверка наличия иконок
    ensure_lucide_icons()

    # Сброс менеджеров
    reset_lucide_manager()

    logger.info("Сброс кеша иконок завершен")
    logger.info("Перезапустите приложение для применения изменений")


if __name__ == "__main__":
    main()
