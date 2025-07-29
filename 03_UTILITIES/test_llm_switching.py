#!/usr/bin/env python3
"""
Скрипт для тестирования переключения между провайдерами LLM
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

def test_env_configuration():
    """Проверка конфигурации переменных окружения"""
    logger.info("Проверка конфигурации переменных окружения...")
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    logger.info(f"Gemini API Key: {'✅ Найден' if gemini_key else '❌ Не найден'}")
    logger.info(f"OpenRouter API Key: {'✅ Найден' if openrouter_key else '❌ Не найден'}")
    
    return bool(gemini_key), bool(openrouter_key)

def main():
    """Основная функция тестирования"""
    logger.info("=== Начало тестирования переключения провайдеров LLM ===")
    
    # Проверка конфигурации
    test_env_configuration()
    
    logger.info("=== Тестирование завершено ===")

if __name__ == "__main__":
    main()
