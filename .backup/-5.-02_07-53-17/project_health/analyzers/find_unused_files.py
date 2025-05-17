import logging
import os
import sys
from pathlib import Path

from analyze_dependencies import analyze_dependencies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_unused_files(project_path):
    """
    Находит неиспользуемые Python файлы в проекте.

    Args:
        project_path: Путь к проекту.

    Returns:
        Список неиспользуемых файлов.
    """
    logger.info("Начинаем анализ неиспользуемых файлов...")

    try:
        # Получаем все Python файлы в проекте
        all_files = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py"):
                    all_files.append(os.path.join(root, file))

        logger.info(f"Всего найдено {len(all_files)} Python файлов")

        # Получаем граф зависимостей
        dependency_map = analyze_dependencies(project_path)

        # Создаем словарь реальных путей для преобразования имен модулей в пути файлов
        module_to_path = {}
        for file_path in all_files:
            module_name = file_path.replace(project_path, "").replace(os.sep, ".").strip(".")
            if module_name.endswith(".py"):
                module_name = module_name[:-3]  # Убираем расширение .py
            module_to_path[module_name] = file_path

        # Создаем множество всех используемых файлов
        used_files = set(dependency_map.keys())  # Все файлы, которые мы смогли проанализировать

        # Добавляем файлы, на которые есть ссылки
        for file_path, deps in dependency_map.items():
            for dep in deps:
                # Пытаемся найти соответствующий файл для каждой зависимости
                if dep in module_to_path:
                    used_files.add(module_to_path[dep])
                elif dep.split(".")[0] in module_to_path:
                    # Если нет точного соответствия, попробуем найти по первой части имени
                    used_files.add(module_to_path[dep.split(".")[0]])

        # Находим неиспользуемые файлы
        unused_files = [f for f in all_files if f not in used_files]

        logger.info(f"Найдено {len(unused_files)} неиспользуемых файлов")
        return unused_files

    except Exception as e:
        logger.error(f"Ошибка при анализе неиспользуемых файлов: {e}")
        return []

def count_all_python_files(project_path):
    """
    Подсчитывает общее количество Python файлов в проекте.

    Args:
        project_path: Путь к проекту.

    Returns:
        Количество Python файлов.
    """
    count = 0
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                count += 1
    return count

if __name__ == "__main__":
    project_path = os.path.abspath(".")
    unused_files = find_unused_files(project_path)
    total_files = count_all_python_files(project_path)

    if unused_files:
        print("\nСписок неиспользуемых файлов:")
        for i, file in enumerate(sorted(unused_files), 1):
            rel_path = os.path.relpath(file, project_path)
            print(f"{i}. {rel_path}")

        # Сохраняем результат в отчет
        logger.info("Сохраняем результаты в отчет...")

        # Создаем директорию для отчетов, если она не существует
        report_dir = os.path.join(project_path, "imports_reports")
        os.makedirs(report_dir, exist_ok=True)

        # Формируем имя файла отчета
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(report_dir, f"unused_files_summary_{timestamp}.txt")

        # Сохраняем отчет
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"Анализ неиспользуемых файлов от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего проанализировано файлов: {total_files}\n")
            f.write(f"Найдено неиспользуемых файлов: {len(unused_files)}\n\n")
            f.write("Список неиспользуемых файлов:\n")
            for i, file in enumerate(sorted(unused_files), 1):
                rel_path = os.path.relpath(file, project_path)
                f.write(f"{i}. {rel_path}\n")

        logger.info(f"Отчет сохранен в файл: {report_file}")
    else:
        print("Неиспользуемых файлов не найдено.")
