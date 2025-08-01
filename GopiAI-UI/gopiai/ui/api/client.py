"""
Выделенный API клиент для коммуникации с бэкенд сервером GopiAI.

Этот модуль обеспечивает чистое разделение между фронтендом и бэкендом,
реализуя все коммуникации через HTTP API.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class GopiAIAPIClient:
    """
    API клиент для коммуникации с бэкенд сервером GopiAI.
    
    Обеспечивает:
    - Отправку сообщений в чат
    - Получение списка доступных моделей
    - Проверку состояния сервера
    - Обработку ошибок соединения и повторные попытки
    - Таймауты запросов и пулинг соединений
    """
    
    def __init__(self, base_url: str = "http://localhost:5051", timeout: int = 30):
        """
        Инициализация API клиента.
        
        Args:
            base_url: Базовый URL бэкенд сервера
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Настройка сессии с пулингом соединений
        self.session = requests.Session()
        
        # Настройка стратегии повторных попыток
        retry_strategy = Retry(
            total=3,  # Общее количество попыток
            backoff_factor=1,  # Экспоненциальная задержка
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP коды для повтора
            allowed_methods=["HEAD", "GET", "POST"]  # Разрешенные методы
        )
        
        # Настройка адаптера с повторными попытками
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Количество пулов соединений
            pool_maxsize=20  # Максимальный размер пула
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Установка заголовков по умолчанию
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GopiAI-UI-Client/1.0'
        })
    
    def send_message(self, message: str, model_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Отправка сообщения в чат для обработки бэкендом.
        
        Args:
            message: Текст сообщения пользователя
            model_id: ID модели для использования (опционально)
            session_id: ID сессии для контекста (опционально)
            
        Returns:
            Dict с ответом от бэкенда или информацией об ошибке
        """
        endpoint = "/api/process"
        url = urljoin(self.base_url, endpoint)
        
        payload = {
            "message": message,
            "metadata": {
                "timestamp": time.time(),
                "client": "GopiAI-UI"
            }
        }
        
        if model_id:
            payload["model_id"] = model_id
        if session_id:
            payload["session_id"] = session_id
        
        try:
            self.logger.debug(f"Отправка сообщения на {url}: {message[:100]}...")
            
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            # Проверка статуса ответа
            if response.status_code == 200:
                result = response.json()
                self.logger.debug(f"Получен успешный ответ: {result.get('status', 'unknown')}")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Ошибка API: {error_msg}")
                return self._create_error_response(
                    "API_ERROR",
                    f"Сервер вернул ошибку: {error_msg}",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ошибка соединения с сервером: {e}")
            return self._create_error_response(
                "CONNECTION_ERROR",
                "Не удается подключиться к серверу. Проверьте, что бэкенд сервер запущен.",
                {"original_error": str(e)}
            )
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Таймаут запроса: {e}")
            return self._create_error_response(
                "TIMEOUT_ERROR",
                f"Запрос превысил лимит времени ({self.timeout}s). Попробуйте еще раз.",
                {"timeout": self.timeout}
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса: {e}")
            return self._create_error_response(
                "REQUEST_ERROR",
                f"Произошла ошибка при выполнении запроса: {str(e)}",
                {"original_error": str(e)}
            )
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON ответа: {e}")
            return self._create_error_response(
                "JSON_ERROR",
                "Сервер вернул некорректный JSON ответ",
                {"original_error": str(e)}
            )
            
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка: {e}")
            return self._create_error_response(
                "UNKNOWN_ERROR",
                f"Произошла неожиданная ошибка: {str(e)}",
                {"original_error": str(e)}
            )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Получение списка доступных моделей от бэкенда.
        
        Returns:
            Список словарей с информацией о моделях или пустой список при ошибке
        """
        endpoint = "/api/models"
        url = urljoin(self.base_url, endpoint)
        
        try:
            self.logger.debug(f"Запрос списка моделей: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                models = response.json()
                self.logger.debug(f"Получено {len(models)} моделей")
                return models
            else:
                self.logger.error(f"Ошибка получения моделей: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.ConnectionError:
            self.logger.error("Не удается подключиться к серверу для получения моделей")
            return []
            
        except requests.exceptions.Timeout:
            self.logger.error("Таймаут при получении списка моделей")
            return []
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении моделей: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Проверка состояния бэкенд сервера.
        
        Returns:
            True если сервер доступен, False в противном случае
        """
        endpoint = "/api/health"
        url = urljoin(self.base_url, endpoint)
        
        try:
            self.logger.debug(f"Проверка состояния сервера: {url}")
            
            response = self.session.get(url, timeout=5)  # Короткий таймаут для health check
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                self.logger.debug(f"Состояние сервера: {status}")
                return status == 'healthy'
            else:
                self.logger.warning(f"Сервер вернул статус {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.debug("Сервер недоступен (connection error)")
            return False
            
        except requests.exceptions.Timeout:
            self.logger.debug("Сервер недоступен (timeout)")
            return False
            
        except Exception as e:
            self.logger.debug(f"Ошибка проверки состояния: {e}")
            return False
    
    def _create_error_response(self, error_code: str, message: str, details: Dict = None) -> Dict[str, Any]:
        """
        Создание стандартизированного ответа об ошибке.
        
        Args:
            error_code: Код ошибки
            message: Сообщение об ошибке для пользователя
            details: Дополнительные детали ошибки
            
        Returns:
            Словарь с информацией об ошибке
        """
        error_response = {
            "status": "error",
            "error_code": error_code,
            "message": message,
            "response": message,  # Для совместимости с существующим кодом
            "timestamp": time.time()
        }
        
        if details:
            error_response["details"] = details
            
        return error_response
    
    def close(self):
        """Закрытие сессии и освобождение ресурсов."""
        if hasattr(self, 'session'):
            self.session.close()
            self.logger.debug("API клиент закрыт")
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста."""
        self.close()


# Глобальный экземпляр клиента для удобства использования
_default_client = None

def get_default_client() -> GopiAIAPIClient:
    """
    Получение глобального экземпляра API клиента.
    
    Returns:
        Экземпляр GopiAIAPIClient
    """
    global _default_client
    if _default_client is None:
        _default_client = GopiAIAPIClient()
    return _default_client

def set_default_client(client: GopiAIAPIClient):
    """
    Установка глобального экземпляра API клиента.
    
    Args:
        client: Экземпляр GopiAIAPIClient
    """
    global _default_client
    _default_client = client