import sys
import os
from PySide6.QtWidgets import QApplication
from app.logger import logger  # Включаем подробное логирование
from PySide6.QtCore import QSettings, Qt
from app.ui.i18n.translator import APP_NAME, tr  # Импортируем константу APP_NAME

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

# Добавляем вывод информации о версии Python
print(f"Запуск с Python: {sys.version}")
print(f"sys.version_info: {sys.version_info}")
logger.info(f"Запуск с Python: {sys.version}")
logger.info(f"sys.version_info: {sys.version_info}")

def main():
    # Включаем высокое DPI (используем современный API)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # Загружаем сохраненные настройки
    settings = QSettings(APP_NAME, "UI")

    # Настраиваем менеджер тем
    from app.utils.theme_manager import ThemeManager
    theme_manager = ThemeManager.instance(app)

    # Загружаем сохраненные настройки визуальной темы и применяем ее
    visual_theme = settings.value("visual_theme", "light")
    theme_manager.switch_visual_theme(visual_theme)
    logger.info(f"Применена визуальная тема: {visual_theme}")

    # Настраиваем менеджер переводов
    from app.ui.i18n.translator import JsonTranslationManager

    # Загружаем сохраненные настройки языка и применяем их
    language = settings.value("language", "en_US")
    JsonTranslationManager.instance().switch_language(language)
    logger.info(f"Применен язык: {language}")

    # Инициализируем главное окно
    from app.ui.main_window import MainWindow
    main_window = MainWindow()

    # Отображаем окно и запускаем цикл событий
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
