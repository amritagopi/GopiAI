import os

PROJECT_DIR = "C:/Users/amritagopi/GopiAI"  # путь к корню проекта
OLD = "from app.utils.theme_manager import ThemeManager"
NEW = "from app.utils.theme_manager import ThemeManager"

def fix_theme_imports():
    for root, _, files in os.walk(PROJECT_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if OLD in content:
                    content = content.replace(OLD, NEW)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"🛠️ Заменено в {path}")

if __name__ == "__main__":
    fix_theme_imports()
