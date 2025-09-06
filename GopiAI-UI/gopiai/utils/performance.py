"""
Модуль для оптимизации производительности приложения.

Содержит утилиты для асинхронного выполнения задач и кэширования.
"""
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps, lru_cache
from typing import Any, Callable, TypeVar, Optional, ParamSpec, Generic
import logging
from datetime import datetime, timedelta
from threading import Lock

# Настройка логирования
logger = logging.getLogger(__name__)

# Глобальный пул потоков для тяжелых операций
_global_thread_pool = ThreadPoolExecutor(
    max_workers=4,  # Можно настроить в зависимости от ядер процессора
    thread_name_prefix="perf_worker_"
)

# Кэш для хранения результатов
_result_cache = {}
_cache_lock = Lock()

# Тип для аннотаций
P = ParamSpec('P')
T = TypeVar('T')

def async_execute(func: Callable[P, T]) -> Callable[P, Future[T]]:
    """
    Декоратор для асинхронного выполнения функции в пуле потоков.
    
    Args:
        func: Функция для асинхронного выполнения
        
    Returns:
        Обертка, которая запускает функцию в отдельном потоке
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        # Запускаем функцию в пуле потоков
        future: Future[T] = _global_thread_pool.submit(func, *args, **kwargs)
        return future
    return wrapper

class AsyncTask(Generic[T]):
    """Класс для управления асинхронными задачами"""
    
    def __init__(self, func: Callable[..., T], *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._future: Optional[Future[T]] = None
        
    def start(self) -> 'AsyncTask[T]':
        """Запускает задачу в пуле потоков"""
        self._future = _global_thread_pool.submit(self.func, *self.args, **self.kwargs)
        return self
    
    def result(self, timeout: Optional[float] = None) -> T:
        """Получает результат выполнения задачи"""
        if self._future is None:
            self.start()
        assert self._future is not None
        return self._future.result(timeout=timeout)
    
    def done(self) -> bool:
        """Проверяет, завершена ли задача"""
        f = self._future
        return f is not None and f.done()

class CachedResult:
    """Класс для хранения закэшированных результатов"""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """Проверяет, истек ли срок действия кэша"""
        return datetime.now() > self.expires_at

def cached(ttl: int = 300, maxsize: int = 128):
    """
    Декоратор для кэширования результатов функции.
    
    Args:
        ttl: Время жизни кэша в секундах (по умолчанию 5 минут)
        maxsize: Максимальное количество элементов в кэше (по умолчанию 128)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @lru_cache(maxsize=maxsize)
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Генерируем ключ кэша
            cache_key = (func.__module__, func.__name__, args, frozenset(kwargs.items()))
            
            with _cache_lock:
                # Проверяем кэш
                if cache_key in _result_cache:
                    cached_result = _result_cache[cache_key]
                    if not cached_result.is_expired():
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cached_result.value  # type: ignore[return-value]
            
            # Выполняем функцию, если кэш пуст или истек
            result: T = func(*args, **kwargs)
            with _cache_lock:
                _result_cache[cache_key] = CachedResult(result, ttl)
                logger.debug(f"Cached result for {func.__name__} (TTL: {ttl}s)")
            return result
        return wrapper
    return decorator

def clear_cache():
    """Очищает весь кэш"""
    with _cache_lock:
        _result_cache.clear()

# Пример использования:
if __name__ == "__main__":
    import time
    
    # Пример асинхронной функции
    @async_execute
    def long_running_task(seconds: int) -> str:
        time.sleep(seconds)
        return f"Task completed after {seconds} seconds"
    
    # Пример кэшированной функции
    @cached(ttl=10)  # Кэшировать на 10 секунд
    def expensive_operation(x: int) -> int:
        print(f"Вычисление для {x}...")
        time.sleep(1)  # Имитация долгой операции
        return x * x
    
    # Тестирование асинхронного выполнения
    print("Запуск асинхронных задач...")
    task1 = long_running_task(2)
    task2 = long_running_task(3)
    
    print("Ожидание завершения задач...")
    print(task1.result())  # Блокируется до завершения
    print(task2.result())  # Блокируется до завершения
    
    # Тестирование кэширования
    print("\nТестирование кэширования:")
    print(expensive_operation(4))  # Вычисляется
    print(expensive_operation(4))  # Берется из кэша
    print(expensive_operation(5))  # Вычисляется
    print(expensive_operation(5))  # Берется из кэша
