"""
API клиент для коммуникации с бэкенд сервером GopiAI.
"""

from .client import GopiAIAPIClient, get_default_client, set_default_client

__all__ = ['GopiAIAPIClient', 'get_default_client', 'set_default_client']