#!/usr/bin/env python3
"""
Прокси-модуль для импорта LLM из crewai
Используется для совместимости с кодом, который импортирует LLM из crewai
"""

import logging
from typing import Any, Dict, List, Optional

# Импортируем реальный класс из crewai
from crewai.llm import LLM

logger = logging.getLogger(__name__)

# Теперь этот модуль просто ре-экспортирует класс из crewai
# Все заглушки удалены и заменены на реальные классы
