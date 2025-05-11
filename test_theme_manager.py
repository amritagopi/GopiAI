import os
import sys

# Добавляем текущую директорию в path, чтобы модули были доступны
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Теперь пробуем импортировать
from app.utils.theme_manager import ThemeManager

print("ThemeManager успешно импортирован!")
