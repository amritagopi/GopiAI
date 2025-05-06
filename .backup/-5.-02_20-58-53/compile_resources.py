import os
import subprocess
import sys
from pathlib import Path


def check_pyside_tools():
    """Проверяет наличие инструментов PySide6 для компиляции ресурсов."""
    try:
        # Проверим, установлен ли PySide6-rcc
        result = subprocess.run(['pyside6-rcc', '--version'],
                               capture_output=True,
                               text=True)
        if result.returncode == 0:
            print(f"PySide6 Resource Compiler найден: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    # Если не нашли через прямой вызов, попробуем через python -m
    try:
        result = subprocess.run([sys.executable, '-m', 'PySide6.rcc', '--version'],
                               capture_output=True,
                               text=True)
        if result.returncode == 0:
            print(f"PySide6 Resource Compiler найден через Python: {result.stdout.strip()}")
            return "python"
    except:
        pass

    print("Ошибка: PySide6 Resource Compiler не найден.")
    print("Убедитесь, что PySide6 установлен: pip install PySide6")
    return False

def compile_resources():
    """Компилирует файлы ресурсов Qt в Python-модули."""
    base_dir = Path(__file__).parent

    # Список ресурсов для компиляции (пока только иконки)
    resources = [
        {"qrc": "icons.qrc", "output": "icons_rc.py"}
    ]

    # Проверяем наличие инструментов
    rcc_available = check_pyside_tools()
    if not rcc_available:
        return False

    for resource in resources:
        qrc_file = base_dir / resource["qrc"]
        output_file = base_dir / resource["output"]

        if not qrc_file.exists():
            print(f"Ошибка: Файл {qrc_file} не найден")
            continue

        print(f"Компиляция {qrc_file} в {output_file}...")

        try:
            if rcc_available == "python":
                # Используем Python-модуль для компиляции
                result = subprocess.run(
                    [sys.executable, '-m', 'PySide6.rcc', '-o', str(output_file), str(qrc_file)],
                    capture_output=True,
                    text=True
                )
            else:
                # Используем прямой вызов pyside6-rcc
                result = subprocess.run(
                    ['pyside6-rcc', '-o', str(output_file), str(qrc_file)],
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:
                print(f"Компиляция успешно завершена: {output_file}")
            else:
                print(f"Ошибка при компиляции {qrc_file}:")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"Ошибка при компиляции {qrc_file}: {e}")
            return False

    return True

def check_for_changes():
    """Проверяет, изменились ли ресурсные файлы с момента последней компиляции."""
    base_dir = Path(__file__).parent

    qrc_file = base_dir / "icons.qrc"
    py_file = base_dir / "icons_rc.py"

    if not py_file.exists():
        return True  # Файл не существует, нужна компиляция

    qrc_mtime = qrc_file.stat().st_mtime
    py_mtime = py_file.stat().st_mtime

    # Проверяем также время изменения самих SVG-файлов
    svg_files_changed = False
    icons_dir = base_dir / "assets" / "icons"

    with open(qrc_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Находим все пути к SVG-файлам в QRC
    import re
    svg_paths = re.findall(r'<file>(.*?\.svg)</file>', content)

    for svg_path in svg_paths:
        svg_file = base_dir / svg_path
        if svg_file.exists() and svg_file.stat().st_mtime > py_mtime:
            svg_files_changed = True
            break

    return qrc_mtime > py_mtime or svg_files_changed

if __name__ == "__main__":
    print("Проверка и компиляция ресурсов Qt...")

    # Проверяем, нужна ли компиляция
    if "--force" in sys.argv or check_for_changes():
        if "--force" in sys.argv:
            print("Принудительная перекомпиляция...")
        else:
            print("Обнаружены изменения в ресурсных файлах...")

        success = compile_resources()

        if success:
            print("Компиляция всех ресурсов успешно завершена!")
        else:
            print("Компиляция завершена с ошибками.")
            sys.exit(1)
    else:
        print("Ресурсные файлы не изменились. Компиляция не требуется.")

    sys.exit(0)
