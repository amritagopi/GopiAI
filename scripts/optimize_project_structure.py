#!/usr/bin/env python
"""
Скрипт для оптимизации структуры проекта GopiAI.
Перемещает скрипты из корневой директории в соответствующие поддиректории.
"""

import os
import shutil
import re
import glob
from pathlib import Path

# Определение корневой директории проекта
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Определение целевых директорий
TARGET_DIRS = {
    "run": PROJECT_ROOT / "scripts" / "run",
    "setup": PROJECT_ROOT / "scripts" / "setup",
    "ui": PROJECT_ROOT / "scripts" / "ui",
    "mcp": PROJECT_ROOT / "scripts" / "mcp",
    "utils": PROJECT_ROOT / "scripts" / "utils",
    "analyzers": PROJECT_ROOT / "project_health" / "analyzers",
    "reports": PROJECT_ROOT / "project_health" / "reports",
}

# Проверка и создание директорий, если они не существуют
for target_dir in TARGET_DIRS.values():
    if not target_dir.exists():
        print(f"Создание директории: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)

# Шаблоны для распознавания файлов по категориям
FILE_PATTERNS = {
    "run": [
        r"^run_.*\.py$",
        r"^run_.*\.bat$",
    ],
    "setup": [
        r"^setup.*\.py$",
        r"^setup.*\.bat$",
        r"^setup.*\.ps1$",
        r"^init.*\.py$",
    ],
    "ui": [
        r".*icon.*\.py$",
        r".*theme.*\.py$",
        r".*style.*\.py$",
        r".*resource.*\.py$",
        r"^build_resources\.py$",
        r"^archive_theme_files\.py$",
        r"^reset_icon_cache\.py$",
        r"^css_tools\.bat$",
    ],
    "mcp": [
        r"^.*mcp.*\.py$",
        r"^.*mcp.*\.bat$",
        r"^.*mcp.*\.ps1$",
        r"^mcp\.json$",
    ],
    "analyzers": [
        r"^check_.*\.py$",
        r"^find_.*\.py$",
        r"^analyze.*\.py$",
        r"^mark_dead_code\.py$",
        r"^improve_mark_dead_code\.py$",
        r"^code_analysis.*\.py$",
        r"^dependency_mapper\.py$",
        r"^visualize_dependencies\.py$",
        r"^vulture_clean_scan\.py$",
        r"^check_component_connections\.py$",
    ],
    "reports": [
        r".*_report.*\.txt$",
        r".*_report.*\.md$",
        r".*_report.*\.json$",
        r".*analysis.*\.txt$",
        r".*analysis.*\.md$",
        r".*stubs_report.*$",
    ],
    "utils": [
        r"^clean_project\.py$",
        r"^translate_checker\.py$",
        r"^base64_to_image\.py$",
        r"^check_python_version\.py$",
        r"^move_unused\.py$",
        r"^debug_.*\.py$",
        r"^language_diagnostics\.py$",
        r"^semantic_search\.py$",
    ],
}

# Файлы, которые не следует перемещать
EXCLUDED_FILES = [
    "main.py",
    "setup.py",
    "pyproject.toml",
    "optimize_project_structure.py",
    "requirements.txt",
    "package.json",
    "package-lock.json",
    ".gitignore",
    "icons.qrc",
    "icons_rc.py",
]

def get_target_dir(filename):
    """Определяет целевую директорию для файла на основе его имени."""
    for category, patterns in FILE_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, filename, re.IGNORECASE):
                return TARGET_DIRS[category]
    return None

def should_move_file(filepath):
    """Проверяет, следует ли перемещать данный файл."""
    filename = os.path.basename(filepath)

    # Не перемещаем файлы из списка исключений
    if filename in EXCLUDED_FILES:
        return False

    # Не перемещаем директории
    if os.path.isdir(filepath):
        return False

    # Не перемещаем файлы, которые уже находятся в целевых директориях
    for target_dir in TARGET_DIRS.values():
        if str(filepath).startswith(str(target_dir)):
            return False

    # Не перемещаем файлы из определенных директорий
    excluded_dirs = ["app", "tests", "docs", "examples", "assets", "config", ".git", ".vscode", "venv", "__pycache__", ".cursor", "node_modules"]
    for excluded_dir in excluded_dirs:
        if f"/{excluded_dir}/" in str(filepath) or f"\\{excluded_dir}\\" in str(filepath):
            return False

    # Перемещаем только Python-скрипты, batch-файлы и отчеты
    extensions = [".py", ".bat", ".ps1", ".md", ".txt"]
    if not any(filename.endswith(ext) for ext in extensions):
        return False

    # Проверяем, есть ли целевая директория для файла
    target_dir = get_target_dir(filename)
    return target_dir is not None

def move_files(dry_run=True):
    """
    Перемещает файлы в соответствующие директории.

    Args:
        dry_run: Если True, только показывает, какие файлы будут перемещены, но не перемещает их.
    """
    moved_files = []

    # Ищем все файлы в корневой директории
    for file_path in glob.glob(str(PROJECT_ROOT / "*.py")) + glob.glob(str(PROJECT_ROOT / "*.bat")) + glob.glob(str(PROJECT_ROOT / "*.ps1")):
        file_path = Path(file_path)
        filename = file_path.name

        if should_move_file(file_path):
            target_dir = get_target_dir(filename)
            if target_dir:
                target_path = target_dir / filename

                if dry_run:
                    print(f"[DRY RUN] Перемещение {file_path} -> {target_path}")
                else:
                    print(f"Перемещение {file_path} -> {target_path}")
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
                        moved_files.append((file_path, target_path))
                    else:
                        print(f"ПРОПУЩЕНО: {target_path} уже существует")

    return moved_files

def update_imports(moved_files, dry_run=True):
    """
    Обновляет импорты в файлах после перемещения.

    Args:
        moved_files: Список кортежей (исходный_путь, новый_путь)
        dry_run: Если True, только показывает изменения без их применения
    """
    # Карта перемещенных файлов: {имя_файла: новый_относительный_путь}
    file_map = {
        os.path.basename(src.name): os.path.relpath(dst, PROJECT_ROOT)
        for src, dst in moved_files
    }

    # Шаблон для поиска импортов
    import_pattern = re.compile(r'^\s*(?:from|import)\s+([.\w]+)')

    # Обновляем импорты во всех Python-файлах проекта
    python_files = []
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    for py_file in python_files:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Ищем импорты, которые могут быть затронуты
        modified = False
        for old_name, new_path in file_map.items():
            old_name_without_ext = os.path.splitext(old_name)[0]
            new_path_without_ext = os.path.splitext(new_path)[0].replace('\\', '/')

            # Заменяем импорты с учетом нового пути
            # Исправлена проблема с ссылкой на группу, используя литералы для шаблонов замены
            old_import = f'from {old_name_without_ext} import'
            new_import = f'from {new_path_without_ext} import'
            if old_import in content:
                content = content.replace(old_import, new_import)
                modified = True

            old_import = f'import {old_name_without_ext}'
            new_import = f'import {new_path_without_ext}'
            if old_import in content:
                # Заменяем только точные совпадения, чтобы не затронуть другие импорты
                # Например, не должны заменить "import run_mcp" на "import scripts/run/run_mcp"
                # когда "import run_mcp_server" также присутствует
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # Заменяем только если это точное совпадение или за ним следует пробел, запятая или конец строки
                    if (old_import + ' ' in line or
                        old_import + ',' in line or
                        old_import + '\n' in line or
                        line.strip() == old_import):
                        lines[i] = line.replace(old_import, new_import)
                        modified = True
                content = '\n'.join(lines)

        # Если были изменения, записываем новое содержимое
        if modified:
            if dry_run:
                print(f"[DRY RUN] Обновление импортов в {py_file}")
            else:
                print(f"Обновление импортов в {py_file}")
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)

def main():
    """Основная функция скрипта"""
    import argparse

    parser = argparse.ArgumentParser(description="Оптимизация структуры проекта GopiAI")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, без фактического выполнения")
    parser.add_argument("--only-move", action="store_true", help="Только переместить файлы без обновления импортов")
    args = parser.parse_args()

    print("=== Оптимизация структуры проекта GopiAI ===")

    # Перемещаем файлы
    moved_files = move_files(dry_run=args.dry_run)

    # Обновляем импорты, если требуется
    if not args.only_move and moved_files:
        update_imports(moved_files, dry_run=args.dry_run)

    # Итоги
    print("\n=== Итоги ===")
    print(f"Всего перемещено файлов: {len(moved_files)}")
    print(f"{'[Режим DRY RUN] ' if args.dry_run else ''}Оптимизация структуры {'проведена успешно' if not args.dry_run else 'подготовлена'}")

    if args.dry_run:
        print("\nДля фактического перемещения файлов запустите скрипт без флага --dry-run")

if __name__ == "__main__":
    main()
