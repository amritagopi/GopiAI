"""
Скрипт для преобразования SVG-иконки в base64 и добавления стиля в файлы тем
"""
import os
import base64

# Путь к SVG-иконке
svg_path = os.path.join('..', '..', 'assets', 'icons', 'close.svg')

# Чтение SVG-файла
with open(svg_path, 'rb') as f:
    svg_content = f.read()
    svg_base64 = base64.b64encode(svg_content).decode('utf-8')

# Создаем стиль для кнопки закрытия вкладки
tab_close_style = f"""
/* Кнопка закрытия вкладки с SVG-иконкой */
QTabBar::close-button {{
    image: url(data:image/svg+xml;base64,{svg_base64});
    width: 16px;
    height: 16px;
    subcontrol-position: right;
    subcontrol-origin: margin;
    margin: 2px;
}}

QTabBar::close-button:hover {{
    background-color: rgba(255, 85, 85, 0.3);
    border-radius: 4px;
}}
"""

# Добавляем стиль в файл светлой темы
light_theme_path = os.path.join('themes', 'light_theme.qss')
with open(light_theme_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, не добавлен ли уже стиль
if 'QTabBar::close-button' not in content:
    with open(light_theme_path, 'a', encoding='utf-8') as f:
        f.write('\n' + tab_close_style)
        print(f"Стиль добавлен в {light_theme_path}")

# Добавляем стиль в файл темной темы
dark_theme_path = os.path.join('themes', 'dark_theme.qss')
with open(dark_theme_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, не добавлен ли уже стиль
if 'QTabBar::close-button' not in content:
    with open(dark_theme_path, 'a', encoding='utf-8') as f:
        f.write('\n' + tab_close_style)
        print(f"Стиль добавлен в {dark_theme_path}")

print("Готово!")
