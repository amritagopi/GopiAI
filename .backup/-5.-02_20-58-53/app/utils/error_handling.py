"""
Модуль для единообразной обработки ошибок в проекте GopiAI.

Предоставляет централизованный механизм обработки исключений, логирования
ошибок и создания пользовательских типов исключений для различных компонентов проекта.
"""

import sys
import traceback
import logging
import functools
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Type, TypeVar, Union, cast

# Настройка логирования
logger = logging.getLogger(__name__)

# TypeVar для декораторов
F = TypeVar('F', bound=Callable[..., Any])

# =====================================================================
# Классы исключений
# =====================================================================

class ErrorSeverity(Enum):
    """Перечисление для уровней серьезности ошибок."""
    DEBUG = 10      # Ошибки отладки
    INFO = 20       # Информационные ошибки
    WARNING = 30    # Предупреждения
    ERROR = 40      # Ошибки
    CRITICAL = 50   # Критические ошибки


class BaseError(Exception):
    """Базовый класс для всех исключений в проекте.

    Attributes:
        message: Сообщение об ошибке
        severity: Уровень серьезности ошибки
        details: Дополнительные детали об ошибке
    """
    def __init__(self,
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.severity = severity
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Форматирует сообщение об ошибке для отображения."""
        result = f"{self.severity.name}: {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" [{details_str}]"
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует исключение в словарь для сериализации."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.name,
            "details": self.details
        }


class ConfigError(BaseError):
    """Ошибки, связанные с конфигурацией."""
    pass


class FileError(BaseError):
    """Ошибки, связанные с файловыми операциями."""
    pass


class NetworkError(BaseError):
    """Ошибки, связанные с сетевыми операциями."""
    pass


class ValidationError(BaseError):
    """Ошибки, связанные с валидацией данных."""
    pass


class DatabaseError(BaseError):
    """Ошибки, связанные с базой данных."""
    pass


class APIError(BaseError):
    """Ошибки, связанные с API."""
    pass


class GUIError(BaseError):
    """Ошибки, связанные с графическим интерфейсом."""
    pass


class BusinessLogicError(BaseError):
    """Ошибки, связанные с бизнес-логикой."""
    pass


# =====================================================================
# Функции для обработки исключений
# =====================================================================

def log_exception(exc: Exception,
                  level: int = logging.ERROR,
                  include_traceback: bool = True) -> None:
    """Логирует исключение с опциональным трейсбеком.

    Args:
        exc: Исключение для логирования
        level: Уровень логирования
        include_traceback: Включать ли трейсбек в лог
    """
    message = str(exc)

    if include_traceback:
        tb = traceback.format_exc()
        message = f"{message}\n{tb}"

    logger.log(level, message)


def handle_exception(exc: Exception,
                     log_level: int = logging.ERROR,
                     include_traceback: bool = True,
                     raise_original: bool = False,
                     convert_to: Optional[Type[BaseError]] = None) -> None:
    """Обрабатывает исключение: логирует и опционально пробрасывает дальше.

    Args:
        exc: Исключение для обработки
        log_level: Уровень логирования
        include_traceback: Включать ли трейсбек в лог
        raise_original: Если True, пробрасывает оригинальное исключение дальше
        convert_to: Если указано, конвертирует исключение в указанный тип

    Raises:
        Exception: Пробрасывает оригинальное исключение, если raise_original=True
        convert_to: Пробрасывает сконвертированное исключение, если указан convert_to
    """
    log_exception(exc, log_level, include_traceback)

    if raise_original:
        raise exc

    if convert_to is not None:
        if isinstance(exc, BaseError):
            raise convert_to(exc.message, exc.severity, exc.details)
        else:
            raise convert_to(str(exc))


def convert_exception(from_exception: Type[Exception],
                      to_exception: Type[BaseError],
                      message: Optional[str] = None,
                      severity: ErrorSeverity = ErrorSeverity.ERROR,
                      include_original_message: bool = True) -> Callable[[F], F]:
    """Декоратор для конвертации одного типа исключения в другой.

    Args:
        from_exception: Исходный тип исключения
        to_exception: Целевой тип исключения
        message: Новое сообщение об ошибке (если None, используется сообщение исходного исключения)
        severity: Уровень серьезности для нового исключения
        include_original_message: Включать ли оригинальное сообщение

    Returns:
        Декоратор функции
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except from_exception as exc:
                error_message = message or str(exc)
                if message is not None and include_original_message:
                    error_message = f"{error_message}: {str(exc)}"

                details = {}
                if hasattr(exc, "details"):
                    details = getattr(exc, "details", {})

                raise to_exception(error_message, severity, details)

        return cast(F, wrapper)
    return decorator


def catch_all(log_level: int = logging.ERROR,
              reraise: bool = False,
              default_return: Any = None) -> Callable[[F], F]:
    """Декоратор для перехвата всех исключений в функции.

    Args:
        log_level: Уровень логирования для исключений
        reraise: Пробрасывать ли исключение дальше после логирования
        default_return: Значение по умолчанию для возврата при исключении

    Returns:
        Декоратор функции
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                log_exception(exc, log_level)
                if reraise:
                    raise
                return default_return

        return cast(F, wrapper)
    return decorator


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    log_level: int = logging.WARNING
) -> Callable[[F], F]:
    """Декоратор для повторного выполнения функции при возникновении исключения.

    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (в секундах)
        backoff_factor: Множитель для увеличения задержки с каждой попыткой
        exceptions: Тип или список типов исключений, при которых выполнять повтор
        log_level: Уровень логирования для исключений

    Returns:
        Декоратор функции
    """
    import time

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            exc_types = exceptions
            if not isinstance(exc_types, (list, tuple)):
                exc_types = [exc_types]

            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if not any(isinstance(exc, e) for e in exc_types):
                        raise

                    last_exception = exc
                    if attempt < max_attempts - 1:
                        logger.log(log_level,
                                  f"Попытка {attempt + 1}/{max_attempts} не удалась: {str(exc)}. "
                                  f"Повтор через {current_delay} сек...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor

            if last_exception:
                logger.error(f"Все {max_attempts} попыток завершились неудачно. "
                             f"Последняя ошибка: {str(last_exception)}")
                raise last_exception

        return cast(F, wrapper)
    return decorator


# =====================================================================
# Глобальный обработчик исключений
# =====================================================================

def set_global_exception_handler(callback: Optional[Callable[[Type[BaseException], BaseException, traceback.TracebackType], None]] = None) -> None:
    """Устанавливает глобальный обработчик исключений.

    Args:
        callback: Функция обратного вызова для обработки исключений
                 Если None, используется функция по умолчанию
    """
    def default_exception_handler(exc_type: Type[BaseException],
                                 exc_value: BaseException,
                                 exc_traceback: traceback.TracebackType) -> None:
        """Обработчик исключений по умолчанию."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Для корректной обработки прерывания по Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical("Неперехваченное исключение:",
                       exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = callback or default_exception_handler


# =====================================================================
# Вспомогательные функции
# =====================================================================

def format_exception_for_user(exc: Exception) -> str:
    """Форматирует исключение для отображения пользователю.

    Args:
        exc: Исключение для форматирования

    Returns:
        Отформатированное сообщение об ошибке для пользователя
    """
    if isinstance(exc, BaseError):
        severity_prefix = {
            ErrorSeverity.DEBUG: "Отладочная ошибка",
            ErrorSeverity.INFO: "Информация",
            ErrorSeverity.WARNING: "Предупреждение",
            ErrorSeverity.ERROR: "Ошибка",
            ErrorSeverity.CRITICAL: "Критическая ошибка"
        }
        return f"{severity_prefix[exc.severity]}: {exc.message}"
    else:
        return f"Ошибка: {str(exc)}"


def get_error_details(exc: Exception) -> Dict[str, Any]:
    """Получает подробную информацию об исключении.

    Args:
        exc: Исключение для анализа

    Returns:
        Словарь с подробной информацией об исключении
    """
    result = {
        "error_type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": traceback.format_exc()
    }

    if isinstance(exc, BaseError):
        result.update({
            "severity": exc.severity.name,
            "details": exc.details
        })

    return result


def is_critical_error(exc: Exception) -> bool:
    """Проверяет, является ли исключение критической ошибкой.

    Args:
        exc: Исключение для проверки

    Returns:
        True, если исключение является критической ошибкой, иначе False
    """
    if isinstance(exc, BaseError):
        return exc.severity == ErrorSeverity.CRITICAL

    # Для стандартных исключений проверяем тип
    critical_types = (
        SystemError,
        MemoryError,
        OSError,
        IOError,
        RuntimeError
    )

    return isinstance(exc, critical_types)


def create_error_report(exc: Exception,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Создает отчет об ошибке для логирования или отправки.

    Args:
        exc: Исключение для отчета
        context: Дополнительный контекст (состояние приложения, переменные и т.д.)

    Returns:
        Словарь с данными отчета об ошибке
    """
    import platform
    import datetime

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "error": get_error_details(exc),
        "system_info": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    }

    if context:
        report["context"] = context

    return report
