"""
Модуль для работы с файлами и файловой системой.

Этот модуль содержит набор функций для выполнения операций с файлами
и файловой системой, включая чтение/запись различных форматов файлов,
безопасные операции с файлами, поиск файлов и другие вспомогательные функции.
"""

import os
import json
import csv
import pickle
import shutil
import tempfile
import logging
import fnmatch
from typing import Any, Dict, List, Tuple, Set, Optional, Union, IO, BinaryIO, TextIO, Iterator, Callable, TypeVar

# Настройка логирования
logger = logging.getLogger(__name__)

# Типы для типизации
T = TypeVar('T')

# =====================================================================
# Работа с путями к файлам
# =====================================================================

def get_absolute_path(relative_path: str, base_dir: Optional[str] = None) -> str:
    """Преобразует относительный путь в абсолютный.

    Args:
        relative_path: Относительный путь к файлу
        base_dir: Базовая директория. Если None, используется текущая директория

    Returns:
        Абсолютный путь к файлу
    """
    if base_dir is None:
        base_dir = os.getcwd()
    return os.path.abspath(os.path.join(base_dir, relative_path))

def normalize_path(path: str) -> str:
    """Нормализует путь к файлу, заменяя все разделители на подходящие для данной ОС.

    Args:
        path: Путь к файлу

    Returns:
        Нормализованный путь
    """
    return os.path.normpath(path)

def get_directory_name(path: str) -> str:
    """Возвращает имя директории из полного пути.

    Args:
        path: Путь к файлу

    Returns:
        Имя директории
    """
    return os.path.dirname(path)

def get_filename(path: str, with_extension: bool = True) -> str:
    """Возвращает имя файла из полного пути.

    Args:
        path: Путь к файлу
        with_extension: Включать ли расширение файла

    Returns:
        Имя файла (с расширением или без)
    """
    if with_extension:
        return os.path.basename(path)
    return os.path.splitext(os.path.basename(path))[0]

# =====================================================================
# Операции с файлами
# =====================================================================

def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    """Читает текстовый файл и возвращает его содержимое.

    Args:
        file_path: Путь к файлу
        encoding: Кодировка файла

    Returns:
        Содержимое файла

    Raises:
        FileNotFoundError: Если файл не найден
        IOError: При ошибке чтения файла
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
        raise

def write_text_file(file_path: str, content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> None:
    """Записывает текст в файл.

    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        encoding: Кодировка файла
        create_dirs: Создавать ли директории, если они не существуют

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except IOError as e:
        logger.error(f"Ошибка при записи в файл {file_path}: {str(e)}")
        raise

def append_to_file(file_path: str, content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> None:
    """Добавляет текст в конец файла.

    Args:
        file_path: Путь к файлу
        content: Содержимое для добавления
        encoding: Кодировка файла
        create_dirs: Создавать ли директории, если они не существуют

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'a', encoding=encoding) as f:
            f.write(content)
    except IOError as e:
        logger.error(f"Ошибка при добавлении в файл {file_path}: {str(e)}")
        raise

def read_binary_file(file_path: str) -> bytes:
    """Читает бинарный файл и возвращает его содержимое.

    Args:
        file_path: Путь к файлу

    Returns:
        Бинарное содержимое файла

    Raises:
        FileNotFoundError: Если файл не найден
        IOError: При ошибке чтения файла
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Ошибка при чтении бинарного файла {file_path}: {str(e)}")
        raise

def write_binary_file(file_path: str, content: bytes, create_dirs: bool = True) -> None:
    """Записывает бинарные данные в файл.

    Args:
        file_path: Путь к файлу
        content: Бинарное содержимое для записи
        create_dirs: Создавать ли директории, если они не существуют

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(content)
    except IOError as e:
        logger.error(f"Ошибка при записи в бинарный файл {file_path}: {str(e)}")
        raise

# =====================================================================
# Работа с форматированными файлами (JSON, CSV, Pickle)
# =====================================================================

def read_json_file(file_path: str, encoding: str = 'utf-8') -> Dict:
    """Читает JSON-файл и возвращает его содержимое.

    Args:
        file_path: Путь к файлу
        encoding: Кодировка файла

    Returns:
        Данные из JSON-файла

    Raises:
        FileNotFoundError: Если файл не найден
        json.JSONDecodeError: Если файл содержит некорректный JSON
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON-файл не найден: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при декодировании JSON-файла {file_path}: {str(e)}")
        raise

def write_json_file(file_path: str, data: Dict, encoding: str = 'utf-8', indent: int = 4,
                    create_dirs: bool = True) -> None:
    """Записывает данные в JSON-файл.

    Args:
        file_path: Путь к файлу
        data: Данные для записи
        encoding: Кодировка файла
        indent: Отступ для форматирования JSON
        create_dirs: Создавать ли директории, если они не существуют

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except IOError as e:
        logger.error(f"Ошибка при записи в JSON-файл {file_path}: {str(e)}")
        raise

def read_csv_file(file_path: str, delimiter: str = ',', encoding: str = 'utf-8',
                  as_dict: bool = False) -> List:
    """Читает CSV-файл и возвращает его содержимое.

    Args:
        file_path: Путь к файлу
        delimiter: Разделитель полей
        encoding: Кодировка файла
        as_dict: Если True, каждая строка возвращается как словарь

    Returns:
        Список строк из CSV-файла

    Raises:
        FileNotFoundError: Если файл не найден
        csv.Error: При ошибке чтения CSV
    """
    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            if as_dict:
                reader = csv.DictReader(f, delimiter=delimiter)
                return list(reader)
            else:
                reader = csv.reader(f, delimiter=delimiter)
                return list(reader)
    except FileNotFoundError:
        logger.error(f"CSV-файл не найден: {file_path}")
        raise
    except csv.Error as e:
        logger.error(f"Ошибка при чтении CSV-файла {file_path}: {str(e)}")
        raise

def write_csv_file(file_path: str, data: List, delimiter: str = ',',
                   encoding: str = 'utf-8', create_dirs: bool = True,
                   headers: Optional[List[str]] = None) -> None:
    """Записывает данные в CSV-файл.

    Args:
        file_path: Путь к файлу
        data: Список списков или словарей для записи
        delimiter: Разделитель полей
        encoding: Кодировка файла
        create_dirs: Создавать ли директории, если они не существуют
        headers: Заголовки столбцов (только для списка списков)

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding=encoding, newline='') as f:
            if data and isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f, delimiter=delimiter)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
    except IOError as e:
        logger.error(f"Ошибка при записи в CSV-файл {file_path}: {str(e)}")
        raise

def read_pickle_file(file_path: str) -> Any:
    """Читает данные из Pickle-файла.

    Args:
        file_path: Путь к файлу

    Returns:
        Данные из Pickle-файла

    Raises:
        FileNotFoundError: Если файл не найден
        pickle.UnpicklingError: При ошибке декодирования Pickle
    """
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        logger.error(f"Pickle-файл не найден: {file_path}")
        raise
    except pickle.UnpicklingError as e:
        logger.error(f"Ошибка при декодировании Pickle-файла {file_path}: {str(e)}")
        raise

def write_pickle_file(file_path: str, data: Any, create_dirs: bool = True) -> None:
    """Записывает данные в Pickle-файл.

    Args:
        file_path: Путь к файлу
        data: Данные для записи
        create_dirs: Создавать ли директории, если они не существуют

    Raises:
        IOError: При ошибке записи в файл
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    except IOError as e:
        logger.error(f"Ошибка при записи в Pickle-файл {file_path}: {str(e)}")
        raise

# =====================================================================
# Операции с файловой системой
# =====================================================================

def list_files(directory: str, pattern: str = '*', recursive: bool = False) -> List[str]:
    """Возвращает список файлов в директории, соответствующих шаблону.

    Args:
        directory: Путь к директории
        pattern: Шаблон имени файла (например, '*.py')
        recursive: Включать ли файлы в поддиректориях

    Returns:
        Список путей к файлам

    Raises:
        FileNotFoundError: Если директория не существует
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Директория не существует: {directory}")

    result = []

    if recursive:
        for root, _, files in os.walk(directory):
            for filename in fnmatch.filter(files, pattern):
                result.append(os.path.join(root, filename))
    else:
        for filename in fnmatch.filter(os.listdir(directory), pattern):
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                result.append(path)

    return result

def safe_remove_file(file_path: str) -> bool:
    """Безопасно удаляет файл, если он существует.

    Args:
        file_path: Путь к файлу

    Returns:
        True, если файл был успешно удален, иначе False
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            logger.debug(f"Файл успешно удален: {file_path}")
            return True
        else:
            logger.warning(f"Файл не существует: {file_path}")
            return False
    except PermissionError:
        logger.error(f"Недостаточно прав для удаления файла: {file_path}")
        return False
    except OSError as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {str(e)}")
        return False

def safe_make_dirs(directory: str) -> bool:
    """Безопасно создает директорию и все промежуточные директории.

    Args:
        directory: Путь к директории

    Returns:
        True, если директории были созданы успешно, иначе False
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Директория успешно создана: {directory}")
        return True
    except PermissionError:
        logger.error(f"Недостаточно прав для создания директории: {directory}")
        return False
    except OSError as e:
        logger.error(f"Ошибка при создании директории {directory}: {str(e)}")
        return False

def safe_copy_file(src_path: str, dst_path: str, create_dirs: bool = True) -> bool:
    """Безопасно копирует файл из одного места в другое.

    Args:
        src_path: Путь к исходному файлу
        dst_path: Путь к копии файла
        create_dirs: Создавать ли директории назначения, если они не существуют

    Returns:
        True, если файл был успешно скопирован, иначе False
    """
    try:
        if not os.path.exists(src_path):
            logger.error(f"Исходный файл не существует: {src_path}")
            return False

        if create_dirs:
            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

        shutil.copy2(src_path, dst_path)
        logger.debug(f"Файл успешно скопирован: {src_path} -> {dst_path}")
        return True
    except PermissionError:
        logger.error(f"Недостаточно прав для копирования файла: {src_path} -> {dst_path}")
        return False
    except OSError as e:
        logger.error(f"Ошибка при копировании файла {src_path} -> {dst_path}: {str(e)}")
        return False

def safe_move_file(src_path: str, dst_path: str, create_dirs: bool = True) -> bool:
    """Безопасно перемещает файл из одного места в другое.

    Args:
        src_path: Путь к исходному файлу
        dst_path: Путь к новому расположению файла
        create_dirs: Создавать ли директории назначения, если они не существуют

    Returns:
        True, если файл был успешно перемещен, иначе False
    """
    try:
        if not os.path.exists(src_path):
            logger.error(f"Исходный файл не существует: {src_path}")
            return False

        if create_dirs:
            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

        shutil.move(src_path, dst_path)
        logger.debug(f"Файл успешно перемещен: {src_path} -> {dst_path}")
        return True
    except PermissionError:
        logger.error(f"Недостаточно прав для перемещения файла: {src_path} -> {dst_path}")
        return False
    except OSError as e:
        logger.error(f"Ошибка при перемещении файла {src_path} -> {dst_path}: {str(e)}")
        return False

# =====================================================================
# Временные файлы и директории
# =====================================================================

def create_temp_file(prefix: str = 'tmp_', suffix: str = '', content: Optional[str] = None) -> str:
    """Создает временный файл с опциональным содержимым.

    Args:
        prefix: Префикс имени временного файла
        suffix: Суффикс имени временного файла (например, расширение)
        content: Содержимое для записи во временный файл

    Returns:
        Путь к созданному временному файлу
    """
    try:
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)

        if content is not None:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return temp_path
    except OSError as e:
        logger.error(f"Ошибка при создании временного файла: {str(e)}")
        raise

def create_temp_dir(prefix: str = 'tmpdir_') -> str:
    """Создает временную директорию.

    Args:
        prefix: Префикс имени временной директории

    Returns:
        Путь к созданной временной директории
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        return temp_dir
    except OSError as e:
        logger.error(f"Ошибка при создании временной директории: {str(e)}")
        raise

# =====================================================================
# Проверка файлов и директорий
# =====================================================================

def file_exists(path: str) -> bool:
    """Проверяет, существует ли файл.

    Args:
        path: Путь к файлу

    Returns:
        True, если файл существует, иначе False
    """
    return os.path.isfile(path)

def dir_exists(path: str) -> bool:
    """Проверяет, существует ли директория.

    Args:
        path: Путь к директории

    Returns:
        True, если директория существует, иначе False
    """
    return os.path.isdir(path)

def is_empty_dir(path: str) -> bool:
    """Проверяет, пуста ли директория.

    Args:
        path: Путь к директории

    Returns:
        True, если директория пуста или не существует, иначе False
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return True
    return len(os.listdir(path)) == 0

def get_file_size(path: str) -> int:
    """Возвращает размер файла в байтах.

    Args:
        path: Путь к файлу

    Returns:
        Размер файла в байтах

    Raises:
        FileNotFoundError: Если файл не существует
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не существует: {path}")
    return os.path.getsize(path)

def get_file_modification_time(path: str) -> float:
    """Возвращает время последней модификации файла.

    Args:
        path: Путь к файлу

    Returns:
        Время последней модификации файла (количество секунд с начала эпохи)

    Raises:
        FileNotFoundError: Если файл не существует
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не существует: {path}")
    return os.path.getmtime(path)

def is_file_newer_than(path: str, reference_time: float) -> bool:
    """Проверяет, был ли файл изменен после указанного времени.

    Args:
        path: Путь к файлу
        reference_time: Время для сравнения (количество секунд с начала эпохи)

    Returns:
        True, если файл был изменен после указанного времени, иначе False

    Raises:
        FileNotFoundError: Если файл не существует
    """
    return get_file_modification_time(path) > reference_time
