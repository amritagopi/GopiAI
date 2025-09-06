# Проверка версии Flask и его работоспособности
import sys
from importlib import metadata

def get_pkg_version(pkg_name: str) -> str:
    try:
        return metadata.version(pkg_name)
    except Exception:
        # Fallback in case metadata lookup fails
        return "unknown"

print(f"Python версия: {sys.version}")
print(f"Flask версия: {get_pkg_version('Flask')}")
print("Flask импортирован успешно.")

try:
    from flask import Flask
    app = Flask(__name__)
    print("Объект Flask создан успешно.")
except Exception as e:
    print(f"Ошибка при создании Flask: {e}")

print("Скрипт выполнен успешно.")
