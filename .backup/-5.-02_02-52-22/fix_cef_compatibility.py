import os
import sys
import re
import shutil
from pathlib import Path

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

def fix_cef_init_file(init_path):
    """Исправляет проверку версии Python в __init__.py модуля CEF."""
    if not os.path.exists(init_path):
        print(f"Ошибка: Файл {init_path} не найден")
        return False

    # Создаем резервную копию
    if not backup_file(init_path):
        return False

    try:
        with open(init_path, 'r') as f:
            content = f.read()

        # Ищем проверки версии Python
        version_pattern = r'if\s+sys\.version_info\[:(\d+)\]\s*!=\s*\((\d+),\s*(\d+)\):'
        matches = re.findall(version_pattern, content)

        if not matches:
            print("Не найдены проверки версии Python в формате 'if sys.version_info[:X] != (Y, Z):'")
            return False

        modified_content = content

        # Модифицируем каждую проверку версии для поддержки Python 3.13
        for match in matches:
            depth, major, minor = match

            # Формируем оригинальную строку
            orig_pattern = rf'if\s+sys\.version_info\[:{depth}\]\s*!=\s*\({major},\s*{minor}\):'
            orig_check = re.search(orig_pattern, content)

            if orig_check:
                orig_text = orig_check.group(0)
                # Создаем новую проверку, которая поддерживает Python 3.13
                if int(major) == 3 and int(minor) <= 12:
                    new_text = f"""if (sys.version_info[:1] != ({major},) or
        (sys.version_info[1] != {minor} and sys.version_info[1] != 13)):"""

                    # Заменяем старую проверку на новую
                    modified_content = modified_content.replace(orig_text, new_text)
                    print(f"Заменено: '{orig_text}' -> '{new_text}'")

        # Записываем модифицированный контент обратно в файл
        if modified_content != content:
            with open(init_path, 'w') as f:
                f.write(modified_content)
            print(f"Файл {init_path} успешно модифицирован для поддержки Python 3.13")
            return True
        else:
            print("Не произведено никаких изменений в файле")
            return False

    except Exception as e:
        print(f"Ошибка при модификации файла {init_path}: {e}")
        return False

def find_and_fix_cef():
    """Находит установку CEF и исправляет ее."""
    print_separator()
    print("Поиск установки CEF...")

    # Проверяем различные места установки CEF
    possible_locations = []

    # 1. В текущем виртуальном окружении
    venv_dir = os.path.join(os.getcwd(), "venv")
    if os.path.exists(venv_dir):
        site_packages = os.path.join(venv_dir, "Lib", "site-packages", "cefpython3")
        if os.path.exists(site_packages):
            possible_locations.append(site_packages)

    # 2. В AppData/Roaming для разных версий Python
    python_versions = ["Python37", "Python38", "Python39", "Python310", "Python311", "Python312", "Python313"]
    user_path = os.path.expanduser("~")
    appdata_roaming = os.path.join(user_path, "AppData", "Roaming", "Python")

    if os.path.exists(appdata_roaming):
        for py_ver in python_versions:
            py_path = os.path.join(appdata_roaming, py_ver, "site-packages", "cefpython3")
            if os.path.exists(py_path):
                possible_locations.append(py_path)

    # 3. В системных директориях Python
    if "PYTHONPATH" in os.environ:
        for path in os.environ["PYTHONPATH"].split(os.pathsep):
            cef_path = os.path.join(path, "cefpython3")
            if os.path.exists(cef_path):
                possible_locations.append(cef_path)

    if sys.executable:
        python_lib = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "cefpython3")
        if os.path.exists(python_lib):
            possible_locations.append(python_lib)

    if not possible_locations:
        print("CEF не найден в известных местах установки")
        return False

    print(f"Найдено {len(possible_locations)} установок CEF:")
    for i, location in enumerate(possible_locations, 1):
        print(f"{i}. {location}")

    success = False
    for location in possible_locations:
        init_path = os.path.join(location, "__init__.py")
        if os.path.exists(init_path):
            print(f"\nИсправление {init_path}...")
            if fix_cef_init_file(init_path):
                success = True
                print(f"Файл {init_path} успешно исправлен")
            else:
                print(f"Не удалось исправить {init_path}")

    return success

def main():
    print("Инструмент для исправления совместимости CEF с Python 3.13")
    print(f"Текущая версия Python: {sys.version}")

    result = find_and_fix_cef()

    if result:
        print_separator()
        print("Исправление завершено успешно!")
        print("Теперь CEF должен работать с Python 3.13")
    else:
        print_separator()
        print("Не удалось исправить CEF для работы с Python 3.13")
        print("Попробуйте запустить приложение с помощью скрипта run_with_venv.py,")
        print("который использует Python из виртуального окружения")

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
