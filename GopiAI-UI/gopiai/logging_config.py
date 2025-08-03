import logging
import logging.handlers # Импортируем модуль для обработчиков ротации
import os

def setup_logging(
    log_file_path: str = 'application.log',
    level: int = logging.DEBUG,
    console_output: bool = True,
    single_file_mode: bool = True
):
    """
    Настраивает базовое логирование для всего приложения.

    Сообщения из всех модулей будут записываться в указанный файл
    и, опционально, выводиться в консоль.

    Args:
        log_file_path (str): Путь к файлу логов.
        level (int): Минимальный уровень логирования (например, logging.INFO, logging.DEBUG).
        console_output (bool): Если True, логи также будут выводиться в консоль.
        single_file_mode (bool): Если True, каждый запуск перезаписывает файл лога.
    """
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Удаляем все существующие обработчики, чтобы избежать дублирования
    # Это важно, если функция вызывается несколько раз или если уже есть дефолтные обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Обработчик для записи в файл
    try:
        if single_file_mode:
            # Режим одного файла - каждый запуск перезаписывает файл
            # Удаляем старый файл лога если он существует
            if os.path.exists(log_file_path):
                try:
                    os.remove(log_file_path)
                except (OSError, PermissionError):
                    print(f"[WARNING] Не удалось удалить старый лог файл {log_file_path}, возможно он открыт в редакторе")
            
            # Используем обычный FileHandler в режиме записи (перезапись)
            file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
        else:
            # Режим ротации - используем RotatingFileHandler для ротации логов по размеру
            # maxBytes=10*1024*1024 (10 МБ), backupCount=5 (хранить 5 старых файлов)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
            )
        
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"[OK] Логирование настроено с записью в файл: {log_file_path}")
        
    except (OSError, PermissionError) as e:
        print(f"[WARNING] Не удалось создать файл лога {log_file_path}: {e}")
        print("[INFO] Логирование будет только в консоль")

    # Обработчик для вывода в консоль (опционально)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)