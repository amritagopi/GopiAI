#!/usr/bin/env python3
"""
Заглушка для модуля litellm
Используется для совместимости с кодом, который импортирует litellm
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logger.warning("WARNING: Using litellm stub instead of actual litellm module")

# Основные функции litellm
def completion(**kwargs):
    """
    Заглушка для функции completion
    
    Args:
        **kwargs: Параметры запроса
        
    Returns:
        Dict: Заглушка ответа
    """
    logger.warning("WARNING: Using litellm stub - no actual completion will be generated")
    return {
        "choices": [
            {
                "message": {
                    "content": "[LITELLM STUB] This is a stub response. The litellm module is not available."
                }
            }
        ]
    }

# Классы для совместимости
class RateLimitError(Exception):
    """Заглушка для RateLimitError"""
    pass

class APIError(Exception):
    """Заглушка для APIError"""
    pass

class Timeout(Exception):
    """Заглушка для Timeout"""
    pass

class ServiceUnavailableError(Exception):
    """Заглушка для ServiceUnavailableError"""
    pass

class AuthenticationError(Exception):
    """Заглушка для AuthenticationError"""
    pass

# Функции для управления ключами API
def get_api_key(api_key=None):
    """
    Заглушка для get_api_key
    
    Args:
        api_key: API ключ
        
    Returns:
        str: Заглушка API ключа
    """
    return "sk-stub-api-key"

def set_api_key(api_key):
    """
    Заглушка для set_api_key
    
    Args:
        api_key: API ключ
    """
    pass
