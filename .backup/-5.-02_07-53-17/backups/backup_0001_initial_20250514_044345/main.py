import argparse
import os
import sys

from loguru import logger

# Импортируем ресурсы иконок
import app.icons_rc
from app.config import PROJECT_ROOT, VERSION_STRING
from app.logger import define_log_level

# Настройки для WebEngine перед импортом
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"


def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="GopiAI - интеллектуальный помощник")
    parser.add_argument(
        "--debug", action="store_true", help="Запустить в режиме отладки"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Отключить встроенный браузер"
    )
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

        from app.ui.main_window import MainWindow, initialize_signals

        # Сначала создаем QApplication, затем импортируем ThemeManager
        app = QApplication(sys.argv)
        app.setApplicationName("GopiAI")
        app.setOrganizationName("GopiAI")
        app.setApplicationVersion(VERSION_STRING)

        # Инициализируем ThemeManager только ПОСЛЕ создания QApplication
        from app.utils.theme_manager import ThemeManager

        theme_manager = ThemeManager.instance()
        theme_manager.switch_visual_theme("dark")

        # Инициализируем IconAdapter для поддержки нового формата иконок
        from app.ui.icon_adapter import IconAdapter

        icon_manager = IconAdapter.instance()  # Создаем экземпляр напрямую

        # Показываем окно и запускаем приложение
        main_window = MainWindow(icon_manager=icon_manager)  # Передаем icon_manager
        main_window.show()

        # Инициализируем проверку сигналов после создания и показа окна
        initialize_signals(main_window)

        # Запускаем основной цикл обработки событий
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
