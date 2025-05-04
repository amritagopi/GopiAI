import os
import sys
import shutil
import re

def print_separator():
    print("="*50)

def backup_file(file_path):
    """Создает резервную копию файла перед модификацией."""
    backup_path = f"{file_path}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Создана резервная копия: {backup_path}")
        return True
    except Exception as e:
        print(f"Ошибка при создании резервной копии: {e}")
        return False

def fix_autorun_bat():
    """Исправляет файл autorun.bat для использования Python из venv."""
    autorun_path = os.path.join(os.getcwd(), "autorun.bat")

    if not os.path.exists(autorun_path):
        print(f"Ошибка: Файл {autorun_path} не найден")
        return False

    # Создаем резервную копию
    if not backup_file(autorun_path):
        return False

    try:
        # Создаем новое содержимое с ASCII-символами
        new_content = """@echo off
echo Starting GopiAI using Python from virtual environment

:: Check for virtual environment
if not exist "venv\\Scripts\\python.exe" (
    echo Error: Virtual environment not found at venv\\Scripts\\python.exe
    pause
    exit /b 1
)

:: Activate virtual environment and run the application
call venv\\Scripts\\activate.bat

:: Run the application
python main.py %*

:: Deactivate virtual environment
call venv\\Scripts\\deactivate.bat
"""

        # Записываем новое содержимое
        with open(autorun_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Файл {autorun_path} успешно исправлен")
        return True

    except Exception as e:
        print(f"Ошибка при модификации файла {autorun_path}: {e}")
        return False

def main():
    print("Инструмент для исправления файла autorun.bat")
    print("Текущий каталог:", os.getcwd())

    result = fix_autorun_bat()

    if result:
        print_separator()
        print("Исправление autorun.bat завершено успешно!")
        print("Теперь autorun.bat будет использовать Python из venv")
    else:
        print_separator()
        print("Не удалось исправить autorun.bat")

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
