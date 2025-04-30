import sys
import os
from PySide6.QtWidgets import QApplication
from app.ui.styles import load_styles  # Импортируем новый модуль стилей
import icons_rc  # Импортируем ресурсы иконок

# Добавляем вывод информации о версии Python
print(f"Запуск с Python: {sys.version}")
print(f"sys.version_info: {sys.version_info}")

def main():
    # Включаем функцию High DPI для лучшего отображения на мониторах с высоким разрешением
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Устанавливаем имя приложения для корректной работы настроек
    app.setApplicationName("GopiAI")
    app.setOrganizationName("GopiAI")

    # Загружаем стили и шрифты через новый модуль
    load_styles(app)

    # Импортируем MainWindow только после настройки приложения и стилей
    # чтобы избежать циклических импортов
    from app.ui.main_window import MainWindow

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
