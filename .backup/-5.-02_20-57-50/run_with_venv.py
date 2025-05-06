import os
import platform
import subprocess
import sys


def print_separator():
    print("="*50)

def main():
    # Проверяем наличие виртуального окружения
    venv_dir = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_dir):
        print(f"Ошибка: Виртуальное окружение не найдено в {venv_dir}")
        return 1

    # Определяем путь к python в venv
    if platform.system() == "Windows":
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(python_exe):
        print(f"Ошибка: Python не найден в виртуальном окружении {python_exe}")
        return 1

    # Проверяем версию Python в venv
    try:
        ver_result = subprocess.run([python_exe, "--version"], capture_output=True, text=True)
        python_version = ver_result.stdout.strip() or ver_result.stderr.strip()
        print(f"Запуск с использованием {python_version} из виртуального окружения")
    except Exception as e:
        print(f"Ошибка при проверке версии Python: {e}")
        return 1

    # Формируем команду для запуска main.py с аргументами
    cmd = [python_exe, "main.py"] + sys.argv[1:]

    # Запускаем приложение
    print(f"Запуск команды: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
