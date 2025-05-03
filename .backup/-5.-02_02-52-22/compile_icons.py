import os
import sys
import platform
import subprocess
from pathlib import Path

def print_separator():
    print("="*50)

def compile_resources():
    """Компилирует .qrc файл в Python-модуль."""
    print("Компиляция ресурсов иконок")

    # Путь к файлу ресурсов иконок
    icons_qrc = os.path.join(os.getcwd(), "icons.qrc")

    # Генерируем файл .qrc на основе содержимого директории с иконками
    if generate_qrc_file():
        print(f"Файл {icons_qrc} сгенерирован")
    else:
        print(f"Ошибка при генерации {icons_qrc}")
        return False

    # Определяем команду для компиляции ресурсов
    if platform.system() == "Windows":
        pyside_rcc = os.path.join(sys.prefix, "Scripts", "pyside6-rcc.exe")
    else:
        pyside_rcc = os.path.join(sys.prefix, "bin", "pyside6-rcc")

    # Проверяем наличие pyside6-rcc
    if not os.path.exists(pyside_rcc):
        print(f"Ошибка: pyside6-rcc не найден в {pyside_rcc}")
        print("Пробуем использовать из PATH...")
        if platform.system() == "Windows":
            pyside_rcc = "pyside6-rcc.exe"
        else:
            pyside_rcc = "pyside6-rcc"

    # Выходной файл Python-модуля
    output_file = os.path.join(os.getcwd(), "icons_rc.py")

    # Формируем и выполняем команду
    cmd = [pyside_rcc, "-o", output_file, icons_qrc]
    print(f"Выполняем команду: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Компиляция ресурсов успешно завершена")
        print(f"Создан файл {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при компиляции ресурсов: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def generate_qrc_file():
    """Генерирует .qrc файл на основе содержимого директории с иконками."""
    icons_dir = os.path.join(os.getcwd(), "assets", "icons")
    qrc_file = os.path.join(os.getcwd(), "icons.qrc")

    if not os.path.exists(icons_dir):
        print(f"Ошибка: директория с иконками не найдена: {icons_dir}")
        return False

    try:
        with open(qrc_file, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE RCC>\n')
            f.write('<RCC version="1.0">\n')
            f.write('    <qresource prefix="/icons">\n')

            # Добавляем манифест
            manifest_path = os.path.join(icons_dir, "manifest.json")
            if os.path.exists(manifest_path):
                rel_path = os.path.join("assets", "icons", "manifest.json")
                f.write(f'        <file>{rel_path}</file>\n')

            # Добавляем все иконки
            for file in os.listdir(icons_dir):
                if file.endswith(('.svg', '.png', '.jpg', '.ico')):
                    rel_path = os.path.join("assets", "icons", file)
                    f.write(f'        <file>{rel_path}</file>\n')

            f.write('    </qresource>\n')
            f.write('</RCC>\n')

        print(f"Файл .qrc сгенерирован: {qrc_file}")
        return True
    except Exception as e:
        print(f"Ошибка при генерации .qrc файла: {e}")
        return False

if __name__ == "__main__":
    print_separator()
    if compile_resources():
        print("Ресурсы успешно скомпилированы")
        sys.exit(0)
    else:
        print("Не удалось скомпилировать ресурсы")
        sys.exit(1)
