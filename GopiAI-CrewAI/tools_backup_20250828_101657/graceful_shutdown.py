import atexit
import signal
import logging
import threading
import time
from typing import Optional, Callable, List

logger = logging.getLogger(__name__)

_shutdown_started = False
_shutdown_callbacks: List[Callable[[], None]] = []


def register_on_shutdown(cb: Callable[[], None]) -> None:
    """
    Позволяет сторонним модулям регистрировать свои коллбеки завершения.
    Коллбек должен быть идемпотентным и не бросать исключений.
    """
    try:
        _shutdown_callbacks.append(cb)
        logger.debug("[SHUTDOWN] Зарегистрирован внешний коллбек завершения: %s", getattr(cb, "__name__", str(cb)))
    except Exception as e:
        logger.warning("[SHUTDOWN] Не удалось зарегистрировать коллбек: %s", e)


def stop_background_threads() -> None:
    """
    Остановить фоновые потоки/исполнители. 
    Здесь только каркас — реальные исполнители должны регистрировать свои стоп-функции через register_on_shutdown().
    """
    try:
        logger.info("[SHUTDOWN] Останавливаем фоновые потоки/исполнители...")
        # Пример: если используете concurrent.futures.ThreadPoolExecutor
        # executor.shutdown(wait=False)
        # Для кастомных потоков: выставить флаг stop и выполнить join с таймаутом
        # for t in list_of_threads:
        #     t.request_stop = True
        # for t in list_of_threads:
        #     t.join(timeout=2.0)
    except Exception as e:
        logger.warning("[SHUTDOWN] Ошибка при остановке потоков: %s", e)


def close_external_clients() -> None:
    """
    Закрыть внешние клиенты/ресурсы (HTTP-сессии, WebSocket, аудио/видео, БД/индексы, RAG и т.д.).
    Реальные клиенты должны регистрировать .close()/.shutdown() через register_on_shutdown().
    """
    try:
        logger.info("[SHUTDOWN] Закрываем внешние клиенты/ресурсы...")
        # Примеры (внешние модули должны сами регистрировать здесь свои коллбеки):
        # if openrouter_client: openrouter_client.close()
        # if requests_session: requests_session.close()
        # if rag_system and hasattr(rag_system, 'close'): rag_system.close()
    except Exception as e:
        logger.warning("[SHUTDOWN] Ошибка при закрытии клиентов: %s", e)


def release_ui_native_handles() -> None:
    """
    Освобождаем нативные ресурсы UI (обычно не требуется на серверной стороне).
    """
    try:
        logger.info("[SHUTDOWN] Освобождаем UI-нэйтив ресурсы (если есть)...")
        # Если сервер создавал UI/рендер-контексты (не типично) — закрыть их тут.
    except Exception as e:
        logger.warning("[SHUTDOWN] Ошибка при освобождении UI-ресурсов: %s", e)


def _run_external_callbacks() -> None:
    """
    Вызов зарегистрированных внешних коллбеков завершения.
    """
    for cb in list(_shutdown_callbacks):
        try:
            cb()
        except Exception as e:
            logger.warning("[SHUTDOWN] Коллбек завершения %s выбросил исключение: %s", getattr(cb, "__name__", str(cb)), e)


def shutdown(signum: Optional[int] = None, frame=None) -> None:
    """
    Идемпотентное завершение процессов/ресурсов.
    Вызывается:
    - через atexit.register
    - через signal (SIGINT/SIGTERM)
    - вручную из серверного кода при штатной остановке
    """
    global _shutdown_started
    if _shutdown_started:
        return
    _shutdown_started = True

    logger.info("[SHUTDOWN] Инициирован graceful shutdown (signal=%s)", str(signum))

    try:
        # 1) Остановить фоновые потоки/исполнители
        stop_background_threads()

        # 2) Закрыть внешние клиенты/ресурсы
        close_external_clients()

        # 3) Вызвать внешние коллбеки (закрытие RAG, HTTP-сессий, аудио/видео и т.д.)
        _run_external_callbacks()

        # 4) Освободить UI-нэйтив ресурсы (если вдруг созданы на серверной стороне)
        release_ui_native_handles()

    except Exception as e:
        logger.error("[SHUTDOWN] Исключение при завершении: %s", e)
    finally:
        logger.info("[SHUTDOWN] Завершение завершено")


# Регистрация хуков — выполняется при импорте модуля
atexit.register(shutdown)
try:
    # На Windows поддержка сигналов ограничена, но SIGINT (Ctrl+C) и иногда SIGTERM доступны
    signal.signal(signal.SIGINT, shutdown)
    try:
        signal.signal(signal.SIGTERM, shutdown)
    except Exception:
        # Может отсутствовать на некоторых окружениях Windows — не критично
        pass
except Exception:
    # Если окружение не позволяет регистрировать сигналы (например, embed/GUI) — полагаемся на atexit
    pass
