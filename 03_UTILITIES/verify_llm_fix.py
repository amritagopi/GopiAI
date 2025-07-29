#!/usr/bin/env python3
"""
Скрипт для проверки исправления проблемы переключения провайдеров LLM
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_file_structure():
    """Проверка наличия необходимых файлов"""
    logger.info("Проверка файловой структуры...")
    
    required_files = [
        "GopiAI-Core/gopiai/core/llm_client.py",
        "GopiAI-Core/gopiai/core/adapters/base_adapter.py",
        "GopiAI-Core/gopiai/core/adapters/gemini_adapter.py",
        "GopiAI-Core/gopiai/core/adapters/openrouter_adapter.py",
        "GopiAI-UI/gopiai/ui/llm.py",
        "02_DOCUMENTATION/USAGE/llm_switch.md",
        "02_DOCUMENTATION/LLM_PROVIDER_SWITCH_FIX_REPORT.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            logger.error(f"❌ Отсутствует файл: {file_path}")
        else:
            logger.info(f"✅ Найден файл: {file_path}")
    
    return len(missing_files) == 0

def check_env_configuration():
    """Проверка конфигурации переменных окружения"""
    logger.info("Проверка конфигурации переменных окружения...")
    
    # Проверка наличия .env файла
    env_file = Path(".env")
    if not env_file.exists():
        logger.error("❌ Отсутствует файл .env")
        return False
    
    logger.info("✅ Найден файл .env")
    
    # Проверка отсутствия .env.override
    env_override = Path(".env.override")
    if env_override.exists():
        logger.error("❌ Файл .env.override все еще существует")
        return False
    
    logger.info("✅ Файл .env.override отсутствует (удален)")
    
    return True

def check_imports():
    """Проверка импортов"""
    logger.info("Проверка импортов...")
    
    try:
        # Проверка импорта основного клиента
        from gopiai.core.llm_client import LlmClient
        logger.info("✅ LlmClient импортируется успешно")
        
        # Проверка импорта адаптеров
        from gopiai.core.adapters.base_adapter import BaseAdapter
        logger.info("✅ BaseAdapter импортируется успешно")
        
        from gopiai.core.adapters.gemini_adapter import GeminiAdapter
        logger.info("✅ GeminiAdapter импортируется успешно")
        
        from gopiai.core.adapters.openrouter_adapter import OpenRouterAdapter
        logger.info("✅ OpenRouterAdapter импортируется успешно")
        
        # Проверка импорта UI клиента
        from gopiai.ui.llm import get_llm_client
        logger.info("✅ UI LLM клиент импортируется успешно")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Другая ошибка: {e}")
        return False

async def check_functionality():
    """Проверка функциональности"""
    logger.info("Проверка функциональности...")
    
    try:
        # Проверка создания клиента
        from gopiai.core.llm_client import LlmClient
        client = LlmClient.instance()
        logger.info(f"✅ Клиент создан, текущий провайдер: {client.get_current_provider()}")
        
        # Проверка наличия метода swap_provider
        if hasattr(client, 'swap_provider'):
            logger.info("✅ Метод swap_provider доступен")
        else:
            logger.error("❌ Метод swap_provider отсутствует")
            return False
        
        # Проверка наличия адаптеров
        if hasattr(client, '_adapter'):
            logger.info("✅ Адаптер доступен")
        else:
            logger.warning("⚠️  Адаптер не инициализирован")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке функциональности: {e}")
        return False

def main():
    """Основная функция проверки"""
    logger.info("=== Начало проверки исправления проблемы переключения провайдеров LLM ===")
    
    checks = [
        ("Файловая структура", check_file_structure),
        ("Конфигурация", check_env_configuration),
        ("Импорты", check_imports),
        ("Функциональность", check_functionality)
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"\n--- Проверка: {check_name} ---")
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = asyncio.run(check_func())
            else:
                result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении проверки {check_name}: {e}")
            results.append((check_name, False))
    
    # Итоговый результат
    logger.info("\n=== Результаты проверки ===")
    all_passed = True
    for check_name, result in results:
        status = "✅ Пройдено" if result else "❌ Провалено"
        logger.info(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    logger.info(f"\nОбщий результат: {'✅ Все проверки пройдены' if all_passed else '❌ Есть проваленные проверки'}")
    
    if all_passed:
        logger.info("\n🎉 Исправление проблемы переключения провайдеров LLM успешно завершено!")
        logger.info("✅ Система готова к использованию")
    else:
        logger.error("\n❌ Исправление требует дополнительной работы")
        logger.info("Пожалуйста, проверьте логи выше для выявления проблем")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
