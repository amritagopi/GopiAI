"""
Общие утилитарные функции для проекта GopiAI.

Этот модуль содержит часто используемые утилитарные функции, которые
могут быть полезны в различных частях проекта. Функции организованы по
категориям: работа со строками, коллекциями, файловой системой, валидация и др.
"""

import os
import re
import json
import time
import logging
import hashlib
import datetime
from typing import Any, Dict, List, Tuple, Set, Optional, Union, Callable, TypeVar, Generic

# Настройка логирования
logger = logging.getLogger(__name__)

# Типы для типизации
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# =====================================================================
# Функции для работы со строками
# =====================================================================

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Обрезает строку до указанной длины с добавлением суффикса.

    Args:
        text: Исходная строка
        max_length: Максимальная длина результата
        suffix: Суффикс, добавляемый к обрезанной строке

    Returns:
        Обрезанная строка с суффиксом, если она была обрезана
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def slugify(text: str) -> str:
    """Преобразует строку в URL-дружественный формат.

    Args:
        text: Исходная строка

    Returns:
        Строка, содержащая только латинские буквы, цифры и дефисы
    """
    # Заменяем пробелы на дефисы
    text = text.lower().strip().replace(' ', '-')

    # Удаляем все символы, кроме букв, цифр и дефисов
    return re.sub(r'[^a-z0-9\-]', '', text)

def normalize_text(text: str) -> str:
    """Нормализует текст, удаляя лишние пробелы и переносы строк.

    Args:
        text: Исходная строка

    Returns:
        Нормализованная строка
    """
    # Заменяем переносы строк на пробелы
    text = re.sub(r'\n+', ' ', text)

    # Заменяем множественные пробелы на один пробел
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def generate_hash(text: str, algorithm: str = 'md5') -> str:
    """Генерирует хеш строки с использованием указанного алгоритма.

    Args:
        text: Исходная строка
        algorithm: Алгоритм хеширования ('md5', 'sha1', 'sha256')

    Returns:
        Хеш строки в виде шестнадцатеричной строки
    """
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Неподдерживаемый алгоритм хеширования: {algorithm}")

# =====================================================================
# Функции для работы с коллекциями
# =====================================================================

def chunks(lst: List[T], n: int) -> List[List[T]]:
    """Разбивает список на части равного размера.

    Args:
        lst: Исходный список
        n: Размер каждого подсписка

    Returns:
        Список подсписков
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def find_duplicates(items: List[T]) -> List[T]:
    """Находит дублирующиеся элементы в списке.

    Args:
        items: Исходный список

    Returns:
        Список дублирующихся элементов
    """
    seen = set()
    duplicates = []

    for item in items:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)

    return duplicates

def flatten(nested_list: List[Any]) -> List[Any]:
    """Преобразует вложенный список в плоский список.

    Args:
        nested_list: Вложенный список

    Returns:
        Плоский список
    """
    result = []

    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)

    return result

def group_by(items: List[T], key_fn: Callable[[T], K]) -> Dict[K, List[T]]:
    """Группирует элементы списка по ключу.

    Args:
        items: Список элементов
        key_fn: Функция для получения ключа из элемента

    Returns:
        Словарь, где ключи - результаты key_fn, значения - списки элементов
    """
    result: Dict[K, List[T]] = {}

    for item in items:
        key = key_fn(item)
        if key not in result:
            result[key] = []
        result[key].append(item)

    return result

# =====================================================================
# Функции для работы с датами и временем
# =====================================================================

def get_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """Возвращает текущую дату и время в указанном формате.

    Args:
        format_str: Строка формата даты/времени

    Returns:
        Отформатированная строка с датой и временем
    """
    return datetime.datetime.now().strftime(format_str)

def format_duration(seconds: float) -> str:
    """Форматирует продолжительность в секундах в читаемый вид.

    Args:
        seconds: Продолжительность в секундах

    Returns:
        Форматированная строка (например, "2ч 30м 15с")
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    result = []
    if hours > 0:
        result.append(f"{hours}ч")
    if minutes > 0 or hours > 0:
        result.append(f"{minutes}м")
    result.append(f"{seconds}с")

    return " ".join(result)

# =====================================================================
# Функции для работы с файлами
# =====================================================================

def ensure_dir(directory: str) -> None:
    """Создает директорию, если она не существует.

    Args:
        directory: Путь к директории
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(path: str) -> str:
    """Получает расширение файла из пути.

    Args:
        path: Путь к файлу

    Returns:
        Расширение файла (без точки)
    """
    return os.path.splitext(path)[1][1:].lower()

def is_text_file(file_path: str, sample_size: int = 1024) -> bool:
    """Проверяет, является ли файл текстовым.

    Args:
        file_path: Путь к файлу
        sample_size: Размер образца для проверки

    Returns:
        True, если файл текстовый, иначе False
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        return b'\0' not in sample
    except Exception as e:
        logger.error(f"Ошибка при проверке файла {file_path}: {str(e)}")
        return False

# =====================================================================
# Функции для валидации и проверки
# =====================================================================

def is_valid_email(email: str) -> bool:
    """Проверяет, является ли строка валидным email-адресом.

    Args:
        email: Email-адрес для проверки

    Returns:
        True, если email валиден, иначе False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_url(url: str) -> bool:
    """Проверяет, является ли строка валидным URL.

    Args:
        url: URL для проверки

    Returns:
        True, если URL валиден, иначе False
    """
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))

def safe_cast(value: Any, to_type: Callable[[Any], T], default: Optional[T] = None) -> Optional[T]:
    """Безопасное приведение значения к указанному типу.

    Args:
        value: Исходное значение
        to_type: Функция преобразования типа (int, float, str, и т.д.)
        default: Значение по умолчанию в случае ошибки

    Returns:
        Результат приведения или значение по умолчанию в случае ошибки
    """
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default

# =====================================================================
# Функции для профилирования и отладки
# =====================================================================

def timed(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения функции.

    Args:
        func: Декорируемая функция

    Returns:
        Обертка функции, которая измеряет время выполнения
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"Функция {func.__name__} выполнена за {end_time - start_time:.6f} сек")
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: Tuple = (Exception,)) -> Callable:
    """Декоратор для повторного выполнения функции при возникновении исключения.

    Args:
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками (в секундах)
        exceptions: Кортеж исключений, при которых нужно повторять вызов

    Returns:
        Декоратор функции
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    logger.warning(f"Попытка {attempts} не удалась: {str(e)}. Повтор через {delay} сек...")
                    time.sleep(delay)
        return wrapper
    return decorator
