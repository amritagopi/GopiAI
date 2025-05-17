from datetime import datetime
import os
import re
import json


def analyze_project(
    directory,
    output_file="project_map.json",
    extensions=[".py", ".js", ".ts", ".jsx", ".tsx"],
):
    # Создаем словарь для хранения зависимостей
    dependencies = {}
    all_files = []

    # Анализируем импорты в файлах
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                all_files.append(rel_path)

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Простой паттерн для поиска импортов (можно улучшить)
                    imports = re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', content)
                    dependencies[rel_path] = []

                    for imp in imports:
                        # Преобразование относительных импортов в абсолютные пути (упрощенно)
                        if imp.startswith("."):
                            base_dir = os.path.dirname(rel_path)
                            if imp.startswith("./"):
                                imp_path = os.path.normpath(
                                    os.path.join(base_dir, imp[2:])
                                )
                            elif imp.startswith("../"):
                                imp_path = os.path.normpath(os.path.join(base_dir, imp))
                            else:
                                imp_path = os.path.normpath(
                                    os.path.join(base_dir, imp[1:])
                                )

                            # Добавляем расширение, если его нет
                            if not any(imp_path.endswith(ext) for ext in extensions):
                                for ext in extensions:
                                    if os.path.exists(
                                        os.path.join(directory, imp_path + ext)
                                    ):
                                        imp_path += ext
                                        break

                            if os.path.exists(os.path.join(directory, imp_path)):
                                dependencies[rel_path].append(imp_path)
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")

    # Добавляем метаданные
    result = {
        "generated_at": datetime.now().isoformat(),
        "dependencies": dependencies,
        "files_count": len(all_files),
        "relationships_count": sum(len(deps) for deps in dependencies.values()),
    }

    # Сохраняем результат
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Project map updated at {result['generated_at']}")
    return result


if __name__ == "__main__":
    project_dir = "C:/Users/crazy/GopiAI"  # Ваш путь к проекту
    analyze_project(project_dir)
