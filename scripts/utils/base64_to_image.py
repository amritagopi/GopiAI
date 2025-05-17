import base64
from PIL import Image
import io
import argparse

def base64_to_image(base64_string, output_filename):
    """
    Конвертирует строку base64 в изображение и сохраняет его.

    Args:
        base64_string (str): Строка base64, представляющая изображение.
        output_filename (str): Имя файла для сохранения изображения.
                               Расширение файла определяет формат (например, .png, .jpg).
    """
    try:
        # Убираем префикс data:image/png;base64, если он есть
        if "," in base64_string:
            header, base64_data = base64_string.split(",", 1)
        else:
            base64_data = base64_string

        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))
        image.save(output_filename)
        print(f"Изображение успешно сохранено как {output_filename}")
    except Exception as e:
        print(f"Ошибка при конвертации или сохранении изображения: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Конвертирует строку base64 в файл изображения.")
    parser.add_argument("base64_string", help="Строка base64 для конвертации.")
    parser.add_argument("output_filename", help="Имя выходного файла (например, image.png или image.jpg).")

    args = parser.parse_args()

    base64_to_image(args.base64_string, args.output_filename)
    print(f"Скрипт завершил работу. Изображение должно быть сохранено как {args.output_filename}")

    # Пример вызова из командной строки:
    # python base64_to_image.py "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" "pixel.png"
