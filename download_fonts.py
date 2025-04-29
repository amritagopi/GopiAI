import os
import sys
import zipfile
import shutil
from pathlib import Path
import requests
from io import BytesIO

# URL для загрузки шрифта Inter
INTER_URL = "https://github.com/rsms/inter/releases/download/v3.19/Inter-3.19.zip"

def download_and_install_inter():
    """Скачивает и устанавливает шрифт Inter."""
    print("Скачиваем шрифт Inter...")

    # Создаем директории, если они не существуют
    base_dir = Path(__file__).parent
    fonts_dir = base_dir / "assets" / "fonts"
    inter_dir = fonts_dir / "Inter"

    os.makedirs(inter_dir, exist_ok=True)

    try:
        # Скачиваем ZIP-файл с шрифтом
        response = requests.get(INTER_URL)
        response.raise_for_status()  # Проверяем на ошибки HTTP

        # Распаковываем ZIP-файл в память
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            # Получаем список файлов в архиве, которые нам нужны
            font_files = [f for f in zip_ref.namelist()
                         if f.endswith('.ttf') or f.endswith('.otf')]

            # Извлекаем только файлы шрифтов
            for file in font_files:
                # Получаем только имя файла, отбрасывая пути
                filename = os.path.basename(file)
                print(f"Устанавливаем {filename}...")

                # Извлекаем файл
                source = zip_ref.open(file)
                target = open(os.path.join(inter_dir, filename), "wb")

                with source, target:
                    shutil.copyfileobj(source, target)

        print(f"Шрифт Inter успешно установлен в {inter_dir}")

    except requests.RequestException as e:
        print(f"Ошибка при скачивании шрифта Inter: {e}")
        return False
    except zipfile.BadZipFile:
        print("Ошибка: Скачанный файл не является ZIP-архивом")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Начинаем установку шрифтов...")
    success = download_and_install_inter()

    if success:
        print("Шрифты успешно установлены!")
    else:
        print("Установка шрифтов завершилась с ошибками.")
        sys.exit(1)

    sys.exit(0)
