#!/usr/bin/env python3
"""
Скрипт для сброса кеша иконок и перезагрузки LucideIconManager.
Используется для обновления иконок без перезапуска приложения.
"""

import sys
import os
import logging

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем необходимые модули
from app.ui.lucide_icon_manager import LucideIconManager

def reset_icon_cache():
    """Сбрасывает кеш иконок и перезагружает менеджер иконок."""
    manager = LucideIconManager.instance()
    
    # Очищаем кеш
    manager.clear_cache()
    
    # Пересканируем доступные иконки
    manager.available_icons = manager._scan_available_icons()
    
    return manager.list_available_icons()

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Сбрасываем кеш
    icons = reset_icon_cache()
    
    # Выводим список доступных иконок
    print(f"Кеш иконок сброшен. Доступно {len(icons)} иконок.")
    
    # Проверяем, есть ли в списке иконка git
    if "git" in icons:
        print("✅ Иконка 'git' найдена в списке доступных иконок.")
    else:
        print("❌ Иконка 'git' НЕ найдена! Проверьте наличие файла git.svg в директории иконок.")
    
    print("\nПрименение изменений произойдет при следующем запросе иконки.")