import os
import shutil

# Корень проекта (текущая рабочая директория)
project_root = os.getcwd()

# Название папки для архивации
archive_folder_name = "themes_to_archive"
archive_folder_path = os.path.join(project_root, archive_folder_name)

# Список файлов для перемещения (относительно корня проекта)
files_to_move = [
    "app/ui/themes/DARK-theme-fixed.qss",
    "app/ui/themes/LIGHT-theme-fixed.qss",
    "app/ui/themes/vars/dark-colors.qss",
    "app/ui/themes/vars/light-colors.qss",
    "app/ui/themes/compiled/fixed-dark-theme.qss",
    "app/ui/themes/compiled/fixed-light-theme.qss",
    "app/ui/themes/compiled/fixed-fixed-theme.qss",
    "app/ui/themes/compiled/fixed-theme.qss"
]

def archive_files():
    """
    Перемещает указанные файлы в папку для архивации.
    """
    print(f"Создание архивной папки: {archive_folder_path}")
    os.makedirs(archive_folder_path, exist_ok=True)
    print("-" * 30)

    moved_count = 0
    not_found_count = 0

    for file_relative_path in files_to_move:
        source_path = os.path.join(project_root, file_relative_path)

        # Создаем такую же структуру подпапок в архивной папке
        destination_relative_dir = os.path.dirname(file_relative_path)
        destination_dir_in_archive = os.path.join(archive_folder_path, destination_relative_dir)
        os.makedirs(destination_dir_in_archive, exist_ok=True)

        destination_path = os.path.join(archive_folder_path, file_relative_path)

        if os.path.exists(source_path):
            try:
                shutil.move(source_path, destination_path)
                print(f"Перемещен: '{source_path}' -> '{destination_path}'")
                moved_count += 1
            except Exception as e:
                print(f"ОШИБКА при перемещении '{source_path}': {e}")
        else:
            print(f"Файл не найден (пропущен): '{source_path}'")
            not_found_count += 1

    print("-" * 30)
    print(f"Завершено. Перемещено файлов: {moved_count}")
    if not_found_count > 0:
        print(f"Не найдено файлов: {not_found_count}")
    print(f"Все перемещенные файлы находятся в папке: '{archive_folder_path}'")

if __name__ == "__main__":
    archive_files()
