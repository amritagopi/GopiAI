# --- START OF FILE chat_async_handler.py (UNIFIED VERSION) ---

import logging
import os
import threading
import time
from typing import Dict, Any, Optional, cast
from PySide6.QtCore import QObject, Signal, QTimer, Slot

# Настройка логирования для ChatAsyncHandler
logger = logging.getLogger(__name__)
logger.propagate = False  # avoid duplicate logs if root logger configured elsewhere

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
try:
    # Используем FileHandler с mode='w' для перезаписи файла при каждом запуске
    file_handler = logging.FileHandler(async_log_file, mode='w', encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    # Очищаем все существующие обработчики перед добавлением нового
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    logger.info("Логирование инициализировано (режим перезаписи)")
except Exception as _log_exc:
    # Fall back to basicConfig
    logging.basicConfig(level=logging.DEBUG)
    logger.warning("Failed to attach FileHandler: %s", _log_exc)

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

    def __init__(self, crew_ai_client: Any, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.crew_ai_client = crew_ai_client
        self._current_task_id = None
        self._polling_timer = QTimer(self)
        self._polling_timer.timeout.connect(self._check_task_status)
        
        # Настройки оптимизированного polling
        self.polling_active = False
        self.last_response_length = 0
        self.initial_delay = 500   # 500ms начальная задержка - оптимальный баланс
        self.max_delay = 5000      # 5s максимальная задержка для долгих операций
        self.delay_multiplier = 1.5  # Умеренный рост для лучшего опыта
        self.current_delay = self.initial_delay
        
        # Смарт-параметры для оптимизации
        self.fast_polling_threshold = 10  # первые N попыток - быстрый polling
        self.progress_reset_count = 0  # сброс задержки при прогрессе
        
        # Подключаем сигналы
        self.start_polling_signal.connect(self._start_polling_from_main_thread)
        
        # Подключаем алиасы сигналов для совместимости
        self.message_completed.connect(self.response_ready.emit)
        self.status_updated.connect(self.status_update.emit)
        self.message_chunk_received.connect(self.partial_response.emit)
        
        logger.info("[ChatAsyncHandler] Объединенный обработчик чата инициализирован")

    def _stop_and_reset_polling(self) -> None:
        """Останавливает таймер и сбрасывает связанные с опросом поля (без изменения task_id)."""
        try:
            if hasattr(self, "_polling_timer") and self._polling_timer.isActive():
                self._polling_timer.stop()
        except Exception:
            # defensive: ничего не делаем, просто гарантируем очистку состояния
            pass
        # Сбрасываем состояние, чтобы не было остаточных значений от прошлых задач
        self._polling_start_time = None
        self._current_polling_attempt = 0
        # Сбрасываем delay к начальному состоянию — безопасно
        self.current_delay = self.initial_delay
        logger.debug("[POLLING] _stop_and_reset_polling executed: start_time reset, attempts reset, delay reset")

    def send_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
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

    def process_message(self, message_data: Dict[str, Any]) -> None:
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

    def _process_in_background(self, message_data: Dict[str, Any]) -> None:
        try:
            print("[DEBUG-ASYNC-BG] Начало фоновой обработки сообщения")
            logger.debug(f"[ASYNC] Начало фоновой обработки сообщения")
            
            # Преобразуем сообщение в строку для логирования
            if isinstance(message_data, dict):
                msg_text = message_data.get('message', '')
                msg_log = f"{msg_text[:50]}..." if len(msg_text) > 50 else msg_text
            else:
                msg_log = f"{message_data[:50]}..." if len(str(message_data)) > 50 else message_data
            
            print(f"[DEBUG-ASYNC-BG] Отправка сообщения в CrewAI: {msg_log}")
            logger.debug(f"[ASYNC] Отправка сообщения в CrewAI: {msg_log}")
            
            print("[DEBUG-ASYNC-BG] Проверяем доступность CrewAI API...")
            is_available = self.crew_ai_client.is_available(force_check=True)
            print(f"[DEBUG-ASYNC-BG] CrewAI API доступен: {is_available}")
            logger.debug(f"[ASYNC] CrewAI API доступен: {is_available}")
            
            if not is_available:
                print("[DEBUG-ASYNC-BG-ERROR] CrewAI API недоступен!")
                logger.error("[ASYNC-ERROR] CrewAI API недоступен!")
                from gopiai.ui.utils.network import get_crewai_server_base_url
                base_url = get_crewai_server_base_url()
                error_message = {
                    "response": f"**Ошибка подключения к серверу**\n\n"
                               f"Сервер CrewAI в настоящее время недоступен. Пожалуйста, убедитесь, что:\n\n"
                               f"1. Сервер CrewAI запущен и работает\n"
                               f"2. Сервер доступен по адресу {base_url}\n"
                               f"3. Нет проблем с сетевыми настройками\n\n"
                               f"Вы можете перезапустить сервер с помощью скрипта `start_linux.sh`."
                }
                self.message_error.emit(error_message.get("response", "Ошибка сервера"))
                return
            
            print("[DEBUG-ASYNC-BG] Вызываем crew_ai_client.process_request...")
            logger.debug("[ASYNC] Вызываем crew_ai_client.process_request...")
            
            response = self.crew_ai_client.process_request(message_data)
            
            print(f"[DEBUG-ASYNC-BG] Получен ответ от CrewAI: {response}")
            logger.debug(f"[ASYNC] Получен ответ от CrewAI: %s", response)
            
            if not response:
                print("[DEBUG-ASYNC-BG-ERROR] Получен пустой ответ от сервера")
                logger.error("[ASYNC-ERROR] Получен пустой ответ от сервера")
                raise ValueError("Received an empty response from the server.")
            
            # Ожидаемые варианты ответа: dict с task_id (асинхронный) или dict/str для синхронного
            if isinstance(response, dict) and "task_id" in response and isinstance(response["task_id"], str):
                task_id = cast(str, response["task_id"])
                print(f"[DEBUG-ASYNC-BG] Получен task_id: {task_id}, запуск опроса статуса")
                logger.info(f"[ASYNC] Получен task_id: %s, запуск опроса статуса", task_id)
                self.start_polling_signal.emit(task_id)
            else:
                print("[DEBUG-ASYNC-BG] Получен синхронный ответ, отправка в UI")
                logger.info("[ASYNC] Получен синхронный ответ, отправка в UI")
                # Нормализуем тип: UI ожидает dict, обернем строку/иные типы
                normalized: Dict[str, Any]
                if isinstance(response, dict):
                    normalized = response
                else:
                    normalized = {"response": str(response)}
                self.response_ready.emit(normalized)

        except Exception as e:
            print(f"[DEBUG-ASYNC-BG-ERROR] Ошибка в фоновой обработке: {e}")
            logger.error(f"[ASYNC-ERROR] Ошибка в фоновой обработке: {e}", exc_info=True)
            self.message_error.emit(str(e))
            
    # ### ИЗМЕНЕНО: Создаем новый слот, который будет выполняться в основном потоке ###
    @Slot(str)
    def _start_polling_from_main_thread(self, task_id: str):
        """Запускает/перезапускает таймер для опроса статуса задачи — безопасно сбрасывает старое состояние."""
        # Останавливаем и сбрасываем любое старое состояние, чтобы избежать гонок
        self._stop_and_reset_polling()

        # Устанавливаем новую задачу и начальное состояние
        self._current_task_id = task_id
        self._current_polling_attempt = 0
        self.current_delay = self.initial_delay

        # Устанавливаем стартовое время опроса ЗДЕСЬ, чтобы _check_task_status не видел "старое" значение
        # Используем monotonic() для устойчивости к изменениям системного времени
        try:
            self._polling_start_time = time.monotonic()
        except Exception:
            # на всякий случай — fallback к time.time()
            self._polling_start_time = time.time()

        # Запускаем таймер с текущей задержкой
        self._polling_timer.start(self.current_delay)
        logger.info(f"[POLLING] (re)started polling for task_id={task_id} initial_delay={self.current_delay}ms start_time={self._polling_start_time}")
        self.status_update.emit("Обработка запроса начата...")

    def _check_task_status(self) -> None:
        """Периодически опрашивает сервер о ходе выполнения задачи."""
        if self._current_task_id is None:
            logger.warning("[POLLING] Попытка опроса статуса без task_id, останавливаем таймер")
            self._stop_and_reset_polling()
            return

        try:
            # Добавляем счетчик попыток для отладки
            if not hasattr(self, '_current_polling_attempt'):
                self._current_polling_attempt = 0
            self._current_polling_attempt += 1
            
            logger.debug(f"[POLLING] Попытка #{self._current_polling_attempt} проверки статуса задачи {self._current_task_id}")
            
            # Проверяем наличие метода check_task_status или get_task_status
            if hasattr(self.crew_ai_client, 'check_task_status'):
                status_raw = self.crew_ai_client.check_task_status(self._current_task_id)
            elif hasattr(self.crew_ai_client, 'get_task_status'):
                status_raw = self.crew_ai_client.get_task_status(self._current_task_id)
            else:
                logger.error("[POLLING-ERROR] Клиент CrewAI не имеет методов check_task_status или get_task_status")
                status_raw = {"error": "Метод проверки статуса недоступен", "status": "error"}
                
            logger.debug("[POLLING] Получен статус: %s", status_raw)
            status: Dict[str, Any] = status_raw if isinstance(status_raw, dict) else {"status": str(status_raw)}
            
            done = (bool(status.get("done")) or
                   status.get("status") in ("completed", "error", "failed", "cancelled"))
            
            if done:
                task_status = status.get("status")
                logger.info(f"[POLLING-COMPLETE] Задача {self._current_task_id} завершена после {self._current_polling_attempt} попыток со статусом: {task_status}")
                self._stop_and_reset_polling()
                
                if task_status == "failed":
                    error_msg = status.get("error", "Task failed with unknown error")
                    logger.error(f"[POLLING-FAILED] Задача {self._current_task_id} завершилась с ошибкой: {error_msg}")
                    self.message_error.emit(error_msg)
                    self._current_task_id = None
                    return
                elif task_status == "error":
                    error_msg = status.get("error", "Task ended with error status")
                    logger.error(f"[POLLING-ERROR] Задача {self._current_task_id} завершилась с ошибкой: {error_msg}")
                    self.message_error.emit(error_msg)
                    self._current_task_id = None
                    return
                elif task_status == "cancelled":
                    logger.warning(f"[POLLING-CANCELLED] Задача {self._current_task_id} была отменена")
                    self.message_error.emit("Task was cancelled")
                    self._current_task_id = None
                    return
                
                result = status.get("result")
                if result:
                    logger.debug("[POLLING-RESULT] Получен результат: %s", result)
                else:
                    logger.warning("[POLLING-RESULT] Задача завершена, но результат пуст")
                
                task_id = self._current_task_id
                self._current_task_id = None
                
                norm_result: Dict[str, Any]
                if isinstance(result, dict):
                    norm_result = result
                elif result is None:
                    norm_result = {"response": "Пустой результат"}
                else:
                    norm_result = {"response": str(result)}
                self.response_ready.emit(norm_result)
                logger.info(f"[POLLING-COMPLETE] Результат задачи {task_id} отправлен в UI")
            else:
                status_text = str(status.get("status", "Обрабатываю запрос..."))
                logger.debug(f"[POLLING-PROGRESS] Задача {self._current_task_id} в процессе: {status_text}")
                self.status_update.emit(status_text)
                
                if status_text in ("completed", "error"):
                    logger.info(f"[POLLING-STATUS-COMPLETE] Задача {self._current_task_id} завершена со статусом: {status_text}")
                    self._stop_and_reset_polling()
                    result = status.get("result", {"response": f"Задача завершена со статусом: {status_text}"})
                    self._current_task_id = None
                    if status_text == "error":
                        resp_text = result.get("response") if isinstance(result, dict) else str(result)
                        self.message_error.emit(resp_text or "Ошибка обработки")
                    else:
                        norm_result = result if isinstance(result, dict) else {"response": str(result)}
                        self.response_ready.emit(norm_result)
                else:
                    prev_delay = self.current_delay
                    
                    # Смарт-логика для оптимального backoff
                    if self._current_polling_attempt <= self.fast_polling_threshold:
                        # Первые попытки - быстрый polling
                        next_delay = self.initial_delay
                    else:
                        # Exponential backoff с проверкой на прогресс
                        current_progress = status.get("progress", 0)
                        if hasattr(self, '_last_progress') and current_progress > self._last_progress:
                            # Есть прогресс - сбрасываем задержку для отзывчивости
                            self.progress_reset_count += 1
                            next_delay = max(self.initial_delay, int(self.current_delay * 0.8))
                            logger.debug(f"[POLLING-PROGRESS] Прогресс обнаружен ({self._last_progress} -> {current_progress}), уменьшаем задержку")
                        else:
                            # Нет прогресса - увеличиваем задержку
                            next_delay = int(min(self.max_delay, self.current_delay * self.delay_multiplier))
                        
                        self._last_progress = current_progress
                    
                    self.current_delay = next_delay
                    if self._polling_timer.isActive():
                        self._polling_timer.stop()
                    self._polling_timer.start(self.current_delay)
                    logger.debug(f"[POLLING-BACKOFF] attempt={self._current_polling_attempt}, delay: {prev_delay}ms -> {self.current_delay}ms")
                
                if hasattr(self, '_polling_start_time') and self._polling_start_time is not None:
                    try:
                        elapsed = time.monotonic() - self._polling_start_time
                    except Exception:
                        elapsed = time.time() - self._polling_start_time
                    if elapsed > 180:  # Увеличиваем UI timeout до 3 минут
                        logger.warning(f"[POLLING-TIMEOUT] Превышено время ожидания (180s) для задачи {self._current_task_id}")
                        self._stop_and_reset_polling()
                        self._current_task_id = None
                        self.message_error.emit("Превышено время ожидания ответа от сервера (3 минуты).")
                        return
                else:
                    try:
                        self._polling_start_time = time.monotonic()
                    except Exception:
                        self._polling_start_time = time.time()
                    
                if self._current_polling_attempt > 120:
                    logger.warning(f"[POLLING-TIMEOUT] Превышено максимальное количество попыток опроса для задачи {self._current_task_id}")
                    self._stop_and_reset_polling()
                    self._current_task_id = None
                    self.message_error.emit("Превышено максимальное количество попыток опроса статуса.")
        except Exception as e:
            logger.error(f"[POLLING-ERROR] Ошибка при опросе статуса задачи {self._current_task_id}: {e}", exc_info=True)
            self._stop_and_reset_polling()
            self._current_task_id = None
            self.message_error.emit(str(e))

# --- КОНЕЦ ФАЙЛА chat_async_handler.py ---
