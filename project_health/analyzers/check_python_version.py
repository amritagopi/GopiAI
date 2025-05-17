import sys
import os
import subprocess
import platform

def print_separator():
    print("="*50)

print_separator()
print(f"sys.version: {sys.version}")
print(f"sys.version_info: {sys.version_info}")
print(f"sys.executable: {sys.executable}")
print(f"sys.path:")
for path in sys.path:
    print(f"  - {path}")

print_separator()
print("Переменные окружения:")
for key, value in os.environ.items():
    if "PYTHON" in key.upper() or "PATH" in key.upper():
        print(f"  {key}: {value}")

print_separator()
print("Проверка интерпретаторов Python в PATH:")
try:
    if platform.system() == "Windows":
        python_cmd = "where python"
    else:
        python_cmd = "which -a python python3"

    result = subprocess.run(python_cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        for line in result.stdout.splitlines():
            print(f"  {line}")
            try:
                ver_cmd = f'"{line}" --version'
                ver_result = subprocess.run(ver_cmd, shell=True, capture_output=True, text=True)
                print(f"    Version: {ver_result.stdout.strip() or ver_result.stderr.strip()}")
            except Exception as e:
                print(f"    Error checking version: {e}")
    else:
        print("  Не найдено команд python в PATH")
except Exception as e:
    print(f"  Ошибка при выполнении команды: {e}")

print_separator()
print("Проверка виртуального окружения:")
venv_dir = os.path.join(os.getcwd(), "venv")
if os.path.exists(venv_dir):
    print(f"  Виртуальное окружение найдено: {venv_dir}")
    try:
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "python")
        if os.path.exists(python_exe):
            try:
                ver_cmd = f'"{python_exe}" --version'
                ver_result = subprocess.run(ver_cmd, shell=True, capture_output=True, text=True)
                print(f"  Python в venv: {python_exe}")
                print(f"  Version: {ver_result.stdout.strip() or ver_result.stderr.strip()}")
            except Exception as e:
                print(f"    Error checking version: {e}")
        else:
            print(f"  Python не найден в виртуальном окружении: {python_exe}")
    except Exception as e:
        print(f"  Ошибка при проверке venv: {e}")
else:
    print(f"  Виртуальное окружение не найдено в {venv_dir}")

# Проверка наличия cefpython3
print_separator()
print("Проверка модуля cefpython3:")
try:
    # Проверяем, установлен ли cefpython3 и какая версия Python поддерживается
    python_versions = ["Python37", "Python38", "Python39", "Python310", "Python311", "Python312", "Python313"]
    user_path = os.path.expanduser("~")
    appdata_roaming = os.path.join(user_path, "AppData", "Roaming", "Python")

    if os.path.exists(appdata_roaming):
        print(f"  AppData/Roaming/Python директория существует")
        for py_ver in python_versions:
            py_path = os.path.join(appdata_roaming, py_ver)
            if os.path.exists(py_path):
                print(f"  Найдена директория Python: {py_path}")
                site_packages = os.path.join(py_path, "site-packages")
                if os.path.exists(site_packages):
                    cef_path = os.path.join(site_packages, "cefpython3")
                    if os.path.exists(cef_path):
                        print(f"  CEF установлен для {py_ver}: {cef_path}")
                        # Проверим версию Python в __init__.py
                        init_path = os.path.join(cef_path, "__init__.py")
                        if os.path.exists(init_path):
                            with open(init_path, 'r') as f:
                                init_content = f.read()
                                print(f"  Анализ {init_path}:")
                                # Поиск проверки версии Python
                                import re
                                version_checks = re.findall(r"if\s+sys\.version_info.*?:|assert\s+sys\.version_info.*?[,)]", init_content)
                                for vc in version_checks:
                                    print(f"    Проверка версии: {vc.strip()}")
                    else:
                        print(f"  CEF не найден для {py_ver}")
    else:
        print(f"  Директория {appdata_roaming} не существует")

    # Проверяем в venv/Lib/site-packages
    if os.path.exists(venv_dir):
        site_packages = os.path.join(venv_dir, "Lib", "site-packages")
        if os.path.exists(site_packages):
            cef_path = os.path.join(site_packages, "cefpython3")
            if os.path.exists(cef_path):
                print(f"  CEF установлен в venv: {cef_path}")
                # Проверим версию Python в __init__.py
                init_path = os.path.join(cef_path, "__init__.py")
                if os.path.exists(init_path):
                    with open(init_path, 'r') as f:
                        init_content = f.read()
                        print(f"  Анализ {init_path}:")
                        # Поиск проверки версии Python
                        import re
                        version_checks = re.findall(r"if\s+sys\.version_info.*?:|assert\s+sys\.version_info.*?[,)]", init_content)
                        for vc in version_checks:
                            print(f"    Проверка версии: {vc.strip()}")
            else:
                print(f"  CEF не найден в venv/Lib/site-packages")
except Exception as e:
    print(f"  Ошибка при проверке cefpython3: {e}")

# Проверяем выполнение autorun.bat
print_separator()
print("Анализ autorun.bat:")
try:
    bat_path = os.path.join(os.getcwd(), "autorun.bat")
    if os.path.exists(bat_path):
        with open(bat_path, 'r') as f:
            bat_content = f.read()
            print(f"  Содержимое {bat_path}:")
            print(bat_content)

            # Проверяем переменную PYTHON
            python_var = re.search(r'set\s+PYTHON=(.*)', bat_content)
            if python_var:
                python_path = python_var.group(1).strip()
                print(f"  Переменная PYTHON: {python_path}")
                if os.path.exists(python_path):
                    try:
                        ver_cmd = f'"{python_path}" --version'
                        ver_result = subprocess.run(ver_cmd, shell=True, capture_output=True, text=True)
                        print(f"  Version: {ver_result.stdout.strip() or ver_result.stderr.strip()}")
                    except Exception as e:
                        print(f"  Error checking version: {e}")
                else:
                    print(f"  Файл {python_path} не существует")
    else:
        print(f"  Файл {bat_path} не найден")
except Exception as e:
    print(f"  Ошибка при анализе autorun.bat: {e}")

print_separator()
