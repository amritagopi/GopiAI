# --- START OF FILE chat_async_handler.py (UNIFIED VERSION) ---

import logging
import logging.handlers
import os
import threading
import time
import json
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QTimer, Slot

# Настройка логирования для ChatAsyncHandler
logger = logging.getLogger(__name__)

# Создаем директорию для логов, если её нет
try:
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    logs_dir = os.path.join(app_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
except Exception:
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

# Настраиваем файловый обработчик для логов
async_log_file = os.path.join(logs_dir, 'chat_async_handler.log')
file_handler = logging.handlers.RotatingFileHandler(
    async_log_file, 
    maxBytes=5 * 1024 * 1024,  # 5 МБ
    backupCount=3,
    encoding='utf-8'
)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

class ChatAsyncHandler(QObject):
    """Объединенный асинхронный обработчик чата с оптимизированным polling"""
    
    # Основные сигналы
    response_ready = Signal(dict)  # Полный ответ готов
    status_update = Signal(str)  # Обновление статуса
    message_error = Signal(str)  # Ошибка
    partial_response = Signal(str, str)  # Частичный ответ (chunk, message_type)
    
    # Дополнительные сигналы для совместимости
    message_chunk_received = Signal(str, str)  # Алиас для partial_response
    message_completed = Signal(dict)  # Алиас для response_ready
    status_updated = Signal(str)  # Алиас для status_update
    start_polling_signal = Signal(str)  # Сигнал для безопасного запуска таймера

    def __init__(self, crew_ai_client, parent=None):
        super().__init__(parent)
        self.crew_ai_client = crew_ai_client
        self._current_task_id = None
        self._polling_timer = QTimer(self)
        self._polling_timer.timeout.connect(self._check_task_status)
        
        # Настройки оптимизированного polling
        self.polling_active = False
        self.last_response_length = 0
        self.initial_delay = 300  # 300ms начальная задержка
        self.max_delay = 3000     # 3s максимальная задержка
        self.delay_multiplier = 1.2  # Множитель для экспоненциальной задержки
        self.current_delay = self.initial_delay
        
        # Подключаем сигналы
        self.start_polling_signal.connect(self._start_polling_from_main_thread)
        
        # Подключаем алиасы сигналов для совместимости
        self.message_completed.connect(self.response_ready.emit)
        self.status_updated.connect(self.status_update.emit)
        self.message_chunk_received.connect(self.partial_response.emit)
        
        logger.info("[ChatAsyncHandler] Объединенный обработчик чата инициализирован")

    def send_message(self, message: str, metadata: dict = None) -> bool:
        """
        Отправка сообщения и начало асинхронной обработки (улучшенный интерфейс)
        
        Args:
            message: Текст сообщения
            metadata: Дополнительные метаданные
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            # Формируем данные сообщения
            message_data = {
                'message': message,
                'metadata': metadata or {}
            }
            
            # Запускаем обработку
            self.process_message(message_data)
            return True
            
        except Exception as e:
            logger.error(f"[ChatAsyncHandler] Ошибка отправки сообщения: {e}")
            self.message_error.emit(str(e))
            return False

    def process_message(self, message_data: dict):
        """Запускает асинхронную обработку сообщения в отдельном потоке."""
        logger.info(f"[ChatAsyncHandler] Начинаем обработку сообщения: {message_data}")
        
        # Сбрасываем настройки polling
        self.polling_active = True
        self.last_response_length = 0
        self.current_delay = self.initial_delay
        
        # Запускаем обработку в отдельном потоке
        try:
            thread = threading.Thread(target=self._process_in_background, args=(message_data,))
            thread.daemon = True
            thread.start()
            
            logger.info("[ChatAsyncHandler] Поток для обработки сообщения запущен успешно")
            
        except Exception as e:
            logger.error(f"[ChatAsyncHandler] Ошибка при запуске потока: {e}", exc_info=True)
            self.message_error.emit(str(e))

    def _process_in_background(self, message_data: dict):
        try:
            print("[DEBUG-ASYNC-BG] Начало фоновой обработки сообщения")
            logger.debug(f"[ASYNC] Начало фоновой обработки сообщения")
            
            # Преобразуем сообщение в строку для логирования
            if isinstance(message_data, dict):
                msg_text = message_data.get('message', '')
                msg_log = f"{msg_text[:50]}..." if len(msg_text) > 50 else msg_text
            else:
                msg_log = f"{message_data[:50]}..." if len(str(message_data)) > 50 else message_data
            
            print(f"[DEBUG-ASYNC-BG] Отправка сообщения через API клиент: {msg_log}")
            logger.debug(f"[ASYNC] Отправка сообщения через API клиент: {msg_log}")
            
            # Используем API клиент вместо прямого обращения к crew_ai_client
            try:
                from ..api.client import get_default_client
                api_client = get_default_client()
                
                # Проверяем доступность сервера
                print("[DEBUG-ASYNC-BG] Проверяем доступность API сервера...")
                if not api_client.health_check():
                    print("[DEBUG-ASYNC-BG-ERROR] API сервер недоступен!")
                    logger.error("[ASYNC-ERROR] API сервер недоступен!")
                    error_response = {
                        "status": "error",
                        "error_code": "CONNECTION_ERROR",
                        "message": "Сервер недоступен. Проверьте, что бэкенд сервер запущен.",
                        "response": "**Ошибка подключения к серверу**\n\n"
                                   "Сервер GopiAI в настоящее время недоступен. Пожалуйста, убедитесь, что:\n\n"
                                   "1. Сервер запущен и работает\n"
                                   "2. Сервер доступен по адресу http://localhost:5051\n"
                                   "3. Нет проблем с сетевыми настройками\n\n"
                                   "Вы можете перезапустить сервер с помощью соответствующего скрипта."
                    }
                    self.message_error.emit(error_response)
                    return
                
                # Извлекаем данные для API запроса
                message_text = message_data.get('message', '')
                metadata = message_data.get('metadata', {})
                model_id = metadata.get('model_id')
                session_id = metadata.get('session_id')
                
                print(f"[DEBUG-ASYNC-BG] Отправляем запрос к API: message='{msg_log}', model_id='{model_id}'")
                logger.debug(f"[ASYNC] Отправляем запрос к API: model_id='{model_id}', session_id='{session_id}'")
                
                # Отправляем сообщение через API клиент
                response = api_client.send_message(
                    message=message_text,
                    model_id=model_id,
                    session_id=session_id
                )
                
                print(f"[DEBUG-ASYNC-BG] Получен ответ от API: {response}")
                logger.debug(f"[ASYNC] Получен ответ от API: {response}")
                
                if not response:
                    print("[DEBUG-ASYNC-BG-ERROR] Получен пустой ответ от API")
                    logger.error("[ASYNC-ERROR] Получен пустой ответ от API")
                    error_response = {
                        "status": "error",
                        "error_code": "EMPTY_RESPONSE",
                        "message": "Получен пустой ответ от сервера",
                        "response": "Сервер вернул пустой ответ. Попробуйте еще раз."
                    }
                    self.message_error.emit(error_response)
                    return
                
                # Проверяем статус ответа
                if isinstance(response, dict) and response.get('status') == 'error':
                    print(f"[DEBUG-ASYNC-BG-ERROR] API вернул ошибку: {response.get('message', 'Неизвестная ошибка')}")
                    logger.error(f"[ASYNC-ERROR] API вернул ошибку: {response}")
                    self.message_error.emit(response)
                    return
                
                # Проверяем на асинхронную обработку (task_id)
                if isinstance(response, dict) and "task_id" in response:
                    print(f"[DEBUG-ASYNC-BG] Получен task_id: {response['task_id']}, запуск опроса статуса")
                    logger.info(f"[ASYNC] Получен task_id: {response['task_id']}, запуск опроса статуса")
                    self.start_polling_signal.emit(response["task_id"])
                else:
                    print("[DEBUG-ASYNC-BG] Получен синхронный ответ, отправка в UI")
                    logger.info("[ASYNC] Получен синхронный ответ, отправка в UI")
                    self.response_ready.emit(response)
                    
            except ImportError as e:
                print(f"[DEBUG-ASYNC-BG-ERROR] Не удалось импортировать API клиент: {e}")
                logger.error(f"[ASYNC-ERROR] Не удалось импортировать API клиент: {e}")
                # Fallback к старому методу
                self._fallback_to_crew_ai_client(message_data)
                
        except Exception as e:
            print(f"[DEBUG-ASYNC-BG-ERROR] Ошибка в фоновой обработке: {e}")
            logger.error(f"[ASYNC-ERROR] Ошибка в фоновой обработке: {e}", exc_info=True)
            error_response = {
                "status": "error",
                "error_code": "PROCESSING_ERROR",
                "message": f"Ошибка обработки сообщения: {str(e)}",
                "response": f"Произошла ошибка при обработке вашего сообщения: {str(e)}"
            }
            self.message_error.emit(error_response)
    
    def _fallback_to_crew_ai_client(self, message_data: dict):
        """Fallback метод для использования старого crew_ai_client"""
        try:
            print("[DEBUG-ASYNC-BG] Fallback: используем crew_ai_client")
            logger.debug("[ASYNC] Fallback: используем crew_ai_client")
            
            is_available = self.crew_ai_client.is_available(force_check=True)
            if not is_available:
                error_response = {
                    "status": "error",
                    "error_code": "CONNECTION_ERROR",
                    "message": "CrewAI сервер недоступен",
                    "response": "Сервер CrewAI недоступен. Проверьте подключение."
                }
                self.message_error.emit(error_response)
                return
            
            response = self.crew_ai_client.process_request(message_data)
            
            if isinstance(response, dict) and "task_id" in response:
                self.start_polling_signal.emit(response["task_id"])
            else:
                if isinstance(response, dict) and response.get("status") == "failed":
                    err = response.get("error", "Неизвестная ошибка")
                    self.message_error.emit(err)
                else:
                    self.response_ready.emit(response)
                    
        except Exception as e:
            logger.error(f"[ASYNC-ERROR] Ошибка в fallback методе: {e}")
            error_response = {
                "status": "error",
                "error_code": "FALLBACK_ERROR",
                "message": f"Ошибка fallback обработки: {str(e)}",
                "response": f"Не удалось обработать сообщение: {str(e)}"
            }
            self.message_error.emit(error_response)
            
    # ### ИЗМЕНЕНО: Создаем новый слот, который будет выполняться в основном потоке ###
    @Slot(str)
    def _start_polling_from_main_thread(self, task_id: str):
        """Запускает таймер для опроса статуса задачи. Должен вызываться из основного UI потока."""
        self._current_task_id = task_id
        self._current_polling_attempt = 0
        self._polling_timer.start(1000) # 1 секунда
        logger.info(f"[POLLING] Запущен опрос статуса для task_id: {task_id}")
        self.status_update.emit("Обрабатываю запрос...")

    def _check_task_status(self):
        """Периодически опрашивает сервер о ходе выполнения задачи."""
        if self._current_task_id is None:
            logger.warning("[POLLING] Попытка опроса статуса без task_id, останавливаем таймер")
            self._polling_timer.stop()
            return

        try:
            # Добавляем счетчик попыток для отладки
            if not hasattr(self, '_current_polling_attempt'):
                self._current_polling_attempt = 0
            self._current_polling_attempt += 1
            
            logger.debug(f"[POLLING] Попытка #{self._current_polling_attempt} проверки статуса задачи {self._current_task_id}")
            
            status = self.crew_ai_client.check_task_status(self._current_task_id)
            logger.debug(f"[POLLING] Получен статус: {status}")
            
            # Ожидаем, что сервер возвращает словарь с ключами `done` и `result`
            # Также проверяем статус на "completed" или "error" для завершения опроса
            if status.get("done") or status.get("status") == "completed" or status.get("status") == "error":
                logger.info(f"[POLLING-COMPLETE] Задача {self._current_task_id} завершена после {self._current_polling_attempt} попыток")
                self._polling_timer.stop()
                
                # Проверяем наличие результата
                result = status.get("result")
                if result:
                    logger.debug(f"[POLLING-RESULT] Получен результат: {result}")
                else:
                    logger.warning(f"[POLLING-RESULT] Задача завершена, но результат пуст")
                
                # Сбрасываем счетчик и идентификатор задачи
                task_id = self._current_task_id
                self._current_task_id = None
                self._current_polling_attempt = 0
                
                # Проверяем на ошибку
                if isinstance(result, dict) and result.get("status") == "failed":
                    self.message_error.emit(result.get("error", "Неизвестная ошибка"))
                else:
                    self.response_ready.emit(result)
                logger.info(f"[POLLING-COMPLETE] Результат задачи {task_id} отправлен в UI")
            else:
                # Обновляем статус в UI
                status_text = status.get("status", "Обрабатываю запрос...")
                logger.debug(f"[POLLING-PROGRESS] Задача {self._current_task_id} в процессе: {status_text}")
                self.status_update.emit(status_text)
                
                # Проверяем статус на "completed" или "error" для завершения опроса
                if status_text == "completed" or status_text == "error":
                    logger.info(f"[POLLING-STATUS-COMPLETE] Задача {self._current_task_id} завершена со статусом: {status_text}")
                    self._polling_timer.stop()
                    result = status.get("result", {"response": f"Задача завершена со статусом: {status_text}"})
                    self._current_task_id = None
                    self._current_polling_attempt = 0
                    if status_text == "error":
                        self.message_error.emit(result.get("response", "Ошибка обработки"))
                    else:
                        self.response_ready.emit(result)
                
                # Проверяем на зацикливание - если больше 30 попыток, останавливаем
                if self._current_polling_attempt > 30:
                    logger.warning(f"[POLLING-TIMEOUT] Превышено максимальное количество попыток опроса для задачи {self._current_task_id}")
                    self._polling_timer.stop()
                    self._current_task_id = None
                    self._current_polling_attempt = 0
                    self.message_error.emit("Превышено время ожидания ответа от сервера.")
        except Exception as e:
            logger.error(f"[POLLING-ERROR] Ошибка при опросе статуса задачи {self._current_task_id}: {e}", exc_info=True)
            self._polling_timer.stop()
            self._current_task_id = None
            self._current_polling_attempt = 0
            self.message_error.emit(str(e))

# --- КОНЕЦ ФАЙЛА chat_async_handler.py ---