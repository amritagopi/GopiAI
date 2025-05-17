import subprocess
import os
import sys
from pathlib import Path

# Пути к утилитам Qt
LRELEASE_PATH = r"C:\Users\amritagopi\AppData\Roaming\Python\Python313\site-packages\PySide6\lrelease.exe"

# Директория с файлами перевода
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")

# Проверяем существование указанного пути
if not os.path.exists(LRELEASE_PATH):
    # Пробуем искать в других возможных местах
    alternative_paths = [
        r"C:\Python313\Lib\site-packages\PySide6\lrelease.exe",
        r"C:\Python312\Lib\site-packages\PySide6\lrelease.exe",
        r"C:\Python311\Lib\site-packages\PySide6\lrelease.exe",
        r"C:\Python310\Lib\site-packages\PySide6\lrelease.exe",
        r"C:\Users\amritagopi\AppData\Roaming\Python\Python312\site-packages\PySide6\lrelease.exe",
        r"C:\Users\amritagopi\AppData\Local\Programs\Python\Python313\Lib\site-packages\PySide6\lrelease.exe",
        r"C:\Users\amritagopi\AppData\Local\Programs\Python\Python312\Lib\site-packages\PySide6\lrelease.exe"
    ]

    for path in alternative_paths:
        if os.path.exists(path):
            LRELEASE_PATH = path
            print(f"Найден lrelease по альтернативному пути: {LRELEASE_PATH}")
            break
    else:
        print("ВНИМАНИЕ: Не удалось найти lrelease.exe. Компиляция переводов может быть недоступна.")

def ensure_en_us_translation():
    """Создает пустой файл перевода для английского языка, если его еще нет"""
    en_ts_path = os.path.join(TRANSLATIONS_DIR, "en_US.ts")
    en_qm_path = os.path.join(TRANSLATIONS_DIR, "en_US.qm")

    # Если файла .ts нет, создаем его
    if not os.path.exists(en_ts_path):
        print(f"Создание пустого файла перевода для английского языка: {en_ts_path}")
        with open(en_ts_path, 'w', encoding='utf-8') as f:
            f.write('''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
</TS>''')

    # Если файла .qm нет, создаем пустой файл
    if not os.path.exists(en_qm_path):
        print(f"Создание пустого .qm файла для английского языка: {en_qm_path}")
        # Пытаемся скомпилировать пустой файл
        try:
            if os.path.exists(LRELEASE_PATH):
                subprocess.run([LRELEASE_PATH, en_ts_path, "-qm", en_qm_path], check=True)
            else:
                # Если lrelease не найден, создаем пустой файл
                with open(en_qm_path, 'wb') as f:
                    f.write(b'')
        except:
            # Если не получается, создаем пустой файл
            with open(en_qm_path, 'wb') as f:
                f.write(b'')

    return os.path.exists(en_qm_path)

def fix_translation_file(ts_path):
    """Исправляет файл перевода, заменяя <n> на <n>"""
    with open(ts_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Заменяем <n> на <n>
    content = content.replace('<n>', '<n>').replace('</n>', '</n>')

    with open(ts_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Файл перевода {ts_path} исправлен")

def compile_translations():
    """Компилирует все .ts файлы в .qm"""
    if not os.path.exists(LRELEASE_PATH):
        print(f"Ошибка: lrelease не найден по пути {LRELEASE_PATH}")
        return False

    # Проверяем наличие директории переводов
    if not os.path.exists(TRANSLATIONS_DIR):
        print(f"Создание директории переводов: {TRANSLATIONS_DIR}")
        os.makedirs(TRANSLATIONS_DIR, exist_ok=True)

    # Создаем пустой файл перевода для английского языка
    ensure_en_us_translation()

    # Компилируем все .ts файлы
    success = True
    for ts_file in os.listdir(TRANSLATIONS_DIR):
        if ts_file.endswith(".ts"):
            ts_path = os.path.join(TRANSLATIONS_DIR, ts_file)
            qm_path = os.path.join(TRANSLATIONS_DIR, ts_file.replace(".ts", ".qm"))

            # Исправляем файл перевода перед компиляцией
            fix_translation_file(ts_path)

            try:
                print(f"Компиляция {ts_file}...")
                result = subprocess.run([LRELEASE_PATH, ts_path, "-qm", qm_path], check=True,
                                       capture_output=True, text=True)
                print(f"Результат: {result.stdout}")
                print(f"Создан файл: {qm_path}")
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при компиляции {ts_file}: {e}")
                print(f"Вывод ошибки: {e.stderr}")
                success = False

    return success

if __name__ == "__main__":
    if compile_translations():
        print("Все файлы перевода скомпилированы успешно.")
    else:
        print("Произошли ошибки при компиляции файлов перевода.")
        sys.exit(1)
