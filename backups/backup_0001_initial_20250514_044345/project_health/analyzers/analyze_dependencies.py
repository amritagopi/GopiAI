import ast
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_dependencies(project_path):
    """
    Анализирует зависимости проекта Python.

    Args:
        project_path: Путь к проекту.

    Returns:
        Словарь, где ключи - пути к файлам, а значения - списки их зависимостей.
    """

    dependencies_map = {}

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_dependencies = []

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        tree = ast.parse(content)

                        for node in ast.walk(tree):
                            if isinstance(node, (ast.Import, ast.ImportFrom)):
                                for alias in node.names:
                                    import_name = alias.name
                                    file_dependencies.append(import_name)

                    dependencies_map[file_path] = file_dependencies

                except (SyntaxError, UnicodeDecodeError) as e:
                    logger.warning(f"Ошибка при анализе файла {file_path}: {e}, skipping")
                    continue # Пропускаем файл с ошибкой

    return dependencies_map


if __name__ == "__main__":
    # Пример использования
    project_path = "."
    dependencies_map = analyze_dependencies(project_path)

    # Выводим количество файлов и их зависимости
    logger.info(f"Проанализировано файлов: {len(dependencies_map)}")

    # Выводим первые 5 файлов и их зависимости для примера
    for i, (file, deps) in enumerate(list(dependencies_map.items())[:5]):
        logger.info(f"Файл {i+1}: {file}")
        logger.info(f"  Зависимости: {deps[:10]}{'...' if len(deps) > 10 else ''}")
