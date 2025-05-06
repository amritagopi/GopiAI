
import os

# === НАСТРОЙКИ ===
fluent_icons_dir = input("Введи путь к папке с Fluent UI иконками: ").strip()
icon_list_path = "my_icons.txt"  # Файл со своими названиями
top_matches = 3  # Количество похожих имён, которые показывать

# === Чтение своего списка иконок ===
with open(icon_list_path, "r", encoding="utf-8") as f:
    my_icons = [line.strip() for line in f if line.strip()]

# === Сбор всех путей до SVG файлов ===
svg_files = []
for root, _, files in os.walk(fluent_icons_dir):
    for file in files:
        if file.lower().endswith(".svg"):
            svg_files.append((file, os.path.join(root, file)))

# === Поиск похожих файлов по подстроке ===
from collections import defaultdict

results = defaultdict(list)

for my_icon in my_icons:
    name_core = os.path.splitext(my_icon)[0].lower()
    found = []
    for fname, path in svg_files:
        if name_core in fname.lower():
            found.append((fname, path))
        elif any(part in fname.lower() for part in name_core.split("_")):
            found.append((fname, path))
    # Убираем дубликаты и сортируем по длине имени
    unique = list({f: p for f, p in found}.items())
    unique.sort(key=lambda x: len(x[0]))
    results[my_icon] = unique[:top_matches]

# === Вывод результата ===
for original, matches in results.items():
    print(f"\n🔍 {original}:")
    if not matches:
        print("  ❌ ничего не найдено")
    else:
        for fname, path in matches:
            print(f"  ✅ {fname} — {path}")
