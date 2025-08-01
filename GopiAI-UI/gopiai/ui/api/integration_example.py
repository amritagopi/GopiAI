"""
Пример интеграции API клиента с компонентами UI.

Этот файл демонстрирует, как использовать GopiAIAPIClient
в различных компонентах пользовательского интерфейса.
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QThread, QTimer
from PySide6.QtWidgets import QWidget, QMessageBox

from .client import GopiAIAPIClient, get_default_client


class ChatMessageWorker(QThread):
    """
    Рабочий поток для отправки сообщений в чат через API.
    
    Выполняет API запросы в отдельном потоке, чтобы не блокировать UI.
    """
    
    # Сигналы для коммуникации с основным потоком
    message_sent = Signal(dict)  # Успешная отправка
    error_occurred = Signal(str, str)  # Ошибка (код, сообщение)
    
    def __init__(self, message: str, model_id: str = None, session_id: str = None):
        super().__init__()
        self.message = message
        self.model_id = model_id
        self.session_id = session_id
        self.api_client = get_default_client()
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Выполнение запроса в отдельном потоке."""
        try:
            result = self.api_client.send_message(
                message=self.message,
                model_id=self.model_id,
                session_id=self.session_id
            )
            
            if result.get("status") == "success":
                self.message_sent.emit(result)
            else:
                error_code = result.get("error_code", "UNKNOWN_ERROR")
                error_message = result.get("message", "Неизвестная ошибка")
                self.error_occurred.emit(error_code, error_message)
                
        except Exception as e:
            self.logger.error(f"Ошибка в рабочем потоке: {e}")
            self.error_occurred.emit("THREAD_ERROR", str(e))


class APIHealthMonitor(QObject):
    """
    Монитор состояния API сервера.
    
    Периодически проверяет доступность бэкенд сервера
    и уведомляет UI о изменениях состояния.
    """
    
    # Сигналы для уведомления о состоянии
    server_online = Signal()
    server_offline = Signal()
    status_changed = Signal(bool)  # True = онлайн, False = офлайн
    
    def __init__(self, check_interval: int = 30):
        super().__init__()
        self.api_client = get_default_client()
        self.check_interval = check_interval * 1000  # Конвертация в миллисекунды
        self.last_status = None
        self.logger = logging.getLogger(__name__)
        
        # Таймер для периодических проверок
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_server_health)
    
    def start_monitoring(self):
        """Запуск мониторинга."""
        self.logger.info("Запуск мониторинга состояния API сервера")
        self.check_server_health()  # Первоначальная проверка
        self.timer.start(self.check_interval)
    
    def stop_monitoring(self):
        """Остановка мониторинга."""
        self.logger.info("Остановка мониторинга состояния API сервера")
        self.timer.stop()
    
    def check_server_health(self):
        """Проверка состояния сервера."""
        try:
            is_healthy = self.api_client.health_check()
            
            # Уведомление об изменении состояния
            if self.last_status != is_healthy:
                self.status_changed.emit(is_healthy)
                
                if is_healthy:
                    self.logger.info("API сервер доступен")
                    self.server_online.emit()
                else:
                    self.logger.warning("API сервер недоступен")
                    self.server_offline.emit()
                
                self.last_status = is_healthy
                
        except Exception as e:
            self.logger.error(f"Ошибка при проверке состояния сервера: {e}")
            if self.last_status is not False:
                self.status_changed.emit(False)
                self.server_offline.emit()
                self.last_status = False


class ChatIntegrationMixin:
    """
    Миксин для интеграции API клиента в компоненты чата.
    
    Предоставляет методы для отправки сообщений и обработки ответов.
    """
    
    def __init__(self):
        self.api_client = get_default_client()
        self.current_worker = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def send_chat_message(self, message: str, model_id: str = None, session_id: str = None):
        """
        Отправка сообщения в чат через API.
        
        Args:
            message: Текст сообщения
            model_id: ID модели (опционально)
            session_id: ID сессии (опционально)
        """
        # Остановка предыдущего запроса, если он выполняется
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
        
        # Создание и запуск нового рабочего потока
        self.current_worker = ChatMessageWorker(message, model_id, session_id)
        self.current_worker.message_sent.connect(self.on_message_sent)
        self.current_worker.error_occurred.connect(self.on_message_error)
        self.current_worker.start()
        
        self.logger.debug(f"Отправка сообщения: {message[:50]}...")
    
    def on_message_sent(self, result: Dict[str, Any]):
        """
        Обработка успешной отправки сообщения.
        
        Этот метод должен быть переопределен в наследующих классах.
        """
        self.logger.info("Сообщение успешно отправлено")
        # Здесь должна быть логика обновления UI
    
    def on_message_error(self, error_code: str, error_message: str):
        """
        Обработка ошибки отправки сообщения.
        
        Этот метод должен быть переопределен в наследующих классах.
        """
        self.logger.error(f"Ошибка отправки сообщения: {error_code} - {error_message}")
        # Здесь должна быть логика отображения ошибки в UI


class ModelManagerMixin:
    """
    Миксин для управления моделями через API.
    
    Предоставляет методы для получения и кэширования списка моделей.
    """
    
    def __init__(self):
        self.api_client = get_default_client()
        self._cached_models = None
        self._models_cache_time = None
        self.cache_duration = 300  # 5 минут в секундах
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_available_models(self, use_cache: bool = True) -> list:
        """
        Получение списка доступных моделей.
        
        Args:
            use_cache: Использовать кэшированные данные если доступны
            
        Returns:
            Список моделей
        """
        import time
        
        # Проверка кэша
        if (use_cache and self._cached_models and self._models_cache_time and
            time.time() - self._models_cache_time < self.cache_duration):
            self.logger.debug("Использование кэшированного списка моделей")
            return self._cached_models
        
        # Получение свежих данных
        try:
            models = self.api_client.get_available_models()
            
            # Обновление кэша
            self._cached_models = models
            self._models_cache_time = time.time()
            
            self.logger.info(f"Получено {len(models)} моделей")
            return models
            
        except Exception as e:
            self.logger.error(f"Ошибка получения моделей: {e}")
            # Возврат кэшированных данных при ошибке
            return self._cached_models or []
    
    def clear_models_cache(self):
        """Очистка кэша моделей."""
        self._cached_models = None
        self._models_cache_time = None
        self.logger.debug("Кэш моделей очищен")


class ErrorDisplayMixin:
    """
    Миксин для отображения ошибок API в UI.
    
    Предоставляет методы для показа пользователю понятных сообщений об ошибках.
    """
    
    ERROR_MESSAGES = {
        "CONNECTION_ERROR": "Не удается подключиться к серверу. Проверьте, что бэкенд сервер запущен.",
        "TIMEOUT_ERROR": "Запрос превысил лимит времени. Попробуйте еще раз.",
        "API_ERROR": "Ошибка сервера. Попробуйте позже или обратитесь к администратору.",
        "JSON_ERROR": "Сервер вернул некорректные данные. Попробуйте еще раз.",
        "RATE_LIMIT_ERROR": "Превышен лимит запросов. Подождите немного и попробуйте снова.",
        "AUTH_ERROR": "Ошибка авторизации. Проверьте настройки API ключей."
    }
    
    def show_api_error(self, error_code: str, error_message: str, parent: QWidget = None):
        """
        Отображение ошибки API пользователю.
        
        Args:
            error_code: Код ошибки
            error_message: Сообщение об ошибке
            parent: Родительский виджет для диалога
        """
        # Получение понятного сообщения
        user_message = self.ERROR_MESSAGES.get(error_code, error_message)
        
        # Создание диалога с ошибкой
        msg_box = QMessageBox(parent or self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Ошибка API")
        msg_box.setText(user_message)
        msg_box.setDetailedText(f"Код ошибки: {error_code}\nДетали: {error_message}")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Retry)
        
        result = msg_box.exec()
        return result == QMessageBox.Retry
    
    def show_connection_error(self, parent: QWidget = None):
        """
        Отображение ошибки соединения с предложением действий.
        
        Args:
            parent: Родительский виджет для диалога
        """
        msg_box = QMessageBox(parent or self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Нет соединения с сервером")
        msg_box.setText("Не удается подключиться к бэкенд серверу.")
        msg_box.setInformativeText(
            "Убедитесь, что:\n"
            "• Бэкенд сервер запущен (порт 5051)\n"
            "• Нет блокировки файрволом\n"
            "• Настройки подключения корректны"
        )
        msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        
        return msg_box.exec() == QMessageBox.Retry


# Пример использования в реальном компоненте UI
class ExampleChatWidget(QWidget, ChatIntegrationMixin, ModelManagerMixin, ErrorDisplayMixin):
    """
    Пример виджета чата с интеграцией API клиента.
    
    Демонстрирует использование всех миксинов для создания
    полнофункционального компонента чата.
    """
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ChatIntegrationMixin.__init__(self)
        ModelManagerMixin.__init__(self)
        
        self.setup_ui()
        self.setup_health_monitor()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Здесь должна быть логика создания UI элементов
        pass
    
    def setup_health_monitor(self):
        """Настройка мониторинга состояния сервера."""
        self.health_monitor = APIHealthMonitor()
        self.health_monitor.server_online.connect(self.on_server_online)
        self.health_monitor.server_offline.connect(self.on_server_offline)
        self.health_monitor.start_monitoring()
    
    def on_message_sent(self, result: Dict[str, Any]):
        """Обработка успешной отправки сообщения."""
        # Обновление UI с ответом
        response = result.get("response", "")
        tools_used = result.get("tools_used", [])
        
        # Здесь должна быть логика отображения ответа в чате
        print(f"Ответ получен: {response}")
        if tools_used:
            print(f"Использованы инструменты: {[tool['name'] for tool in tools_used]}")
    
    def on_message_error(self, error_code: str, error_message: str):
        """Обработка ошибки отправки сообщения."""
        # Показ ошибки пользователю
        retry = self.show_api_error(error_code, error_message)
        
        if retry:
            # Логика повторной отправки
            pass
    
    def on_server_online(self):
        """Обработка восстановления соединения с сервером."""
        # Обновление UI - показать, что сервер доступен
        print("Сервер снова доступен")
    
    def on_server_offline(self):
        """Обработка потери соединения с сервером."""
        # Обновление UI - показать, что сервер недоступен
        print("Сервер недоступен")
    
    def closeEvent(self, event):
        """Обработка закрытия виджета."""
        # Остановка мониторинга и очистка ресурсов
        if hasattr(self, 'health_monitor'):
            self.health_monitor.stop_monitoring()
        
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
        
        super().closeEvent(event)