import sys
import os
import argparse
from loguru import logger

from app.config import VERSION_STRING, PROJECT_ROOT
from app.logger import define_log_level

# Настройки для WebEngine перед импортом
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

# Создаем базовые иконки при запуске, если они отсутствуют
try:
    from create_basic_icons import create_basic_icons
    create_basic_icons()
    import icons_rc  # Импортируем ресурсы иконок
except ImportError:
    print("Warning: Unable to import or create icons")
    logger.warning("Unable to import or create icons")

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="GopiAI - интеллектуальный помощник")
    parser.add_argument('--debug', action='store_true', help='Запустить в режиме отладки')
    parser.add_argument('--no-browser', action='store_true', help='Отключить встроенный браузер')
    args = parser.parse_args()

    # Настройка логирования
    log_level = "DEBUG" if args.debug else "INFO"
    logger = define_log_level(print_level=log_level)

    # Логируем информацию о запуске
    logger.info(f"Запуск GopiAI {VERSION_STRING}")
    logger.info(f"Рабочий каталог: {PROJECT_ROOT}")

    # Импорты внутри функции для ускорения запуска при ошибках
    try:
        # Инициализация Qt
        from PySide6.QtWidgets import QApplication
        from app.ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("GopiAI")
        app.setOrganizationName("GopiAI")
        app.setApplicationVersion(VERSION_STRING)

        # Загружаем и применяем стили
        from app.ui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme_manager.apply_theme()

        # Показываем окно и запускаем приложение
        main_window = MainWindow()
        main_window.show()

        # Запускаем основной цикл обработки событий
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске приложения: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
