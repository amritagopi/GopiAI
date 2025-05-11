#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Система управления цветами для GopiAI.
Позволяет централизованно управлять цветами в приложении
и автоматически генерировать переменные CSS.
"""

import os
import json
from pathlib import Path
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, Signal, QSettings

class ColorSystem(QObject):
    """
    Система управления цветами для GopiAI.

    Предоставляет:
    - Централизованное хранение цветовых палитр
    - Управление цветами для разных тем
    - Генерация CSS переменных
    - Конвертация цветов в разные форматы
    """

    # Сигнал для оповещения об изменении палитры
    paletteChanged = Signal(str)

    _instance = None

    @classmethod
    def instance(cls):
        """Возвращает единственный экземпляр класса (singleton)."""
        if cls._instance is None:
            cls._instance = ColorSystem()
        return cls._instance

    def __init__(self):
        """Инициализирует систему управления цветами."""
        super().__init__()

        # Настройки
        self.settings = QSettings("GopiAI", "UI")

        # Базовые цвета для светлой и темной темы
        self.base_colors = {
            "light": {
                # Основные цвета
                "primary": "#2980B9",         # Основной цвет
                "primary-variant": "#3498DB", # Вариант основного цвета
                "secondary": "#16A085",       # Вторичный цвет
                "accent": "#E74C3C",          # Акцентный цвет

                # Фоновые цвета
                "background": "#F5F5F5",      # Основной фон
                "surface": "#FFFFFF",         # Поверхность (карточки, панели)
                "background-variant": "#EEEEEE", # Вариант фона

                # Цвета текста
                "on-primary": "#FFFFFF",      # Цвет текста на primary
                "on-secondary": "#FFFFFF",    # Цвет текста на secondary
                "on-background": "#333333",   # Цвет текста на background
                "on-surface": "#333333",      # Цвет текста на surface

                # Функциональные цвета
                "error": "#E74C3C",           # Ошибка
                "warning": "#F39C12",         # Предупреждение
                "success": "#2ECC71",         # Успех
                "info": "#3498DB",            # Информация

                # Служебные цвета
                "border": "#CCCCCC",          # Границы
                "divider": "#DDDDDD",         # Разделители
                "disabled": "#AAAAAA",        # Отключенные элементы
                "hover": "#E0E0E0",           # При наведении
                "selected": "#C0E0FF"         # Выбранные элементы
            },
            "dark": {
                # Основные цвета
                "primary": "#3498DB",         # Основной цвет
                "primary-variant": "#2980B9", # Вариант основного цвета
                "secondary": "#1ABC9C",       # Вторичный цвет
                "accent": "#E74C3C",          # Акцентный цвет

                # Фоновые цвета
                "background": "#2D2D2D",      # Основной фон
                "surface": "#3D3D3D",         # Поверхность (карточки, панели)
                "background-variant": "#252525", # Вариант фона

                # Цвета текста
                "on-primary": "#FFFFFF",      # Цвет текста на primary
                "on-secondary": "#FFFFFF",    # Цвет текста на secondary
                "on-background": "#FFFFFF",   # Цвет текста на background
                "on-surface": "#E0E0E0",      # Цвет текста на surface

                # Функциональные цвета
                "error": "#E74C3C",           # Ошибка
                "warning": "#F39C12",         # Предупреждение
                "success": "#2ECC71",         # Успех
                "info": "#3498DB",            # Информация

                # Служебные цвета
                "border": "#444444",          # Границы
                "divider": "#555555",         # Разделители
                "disabled": "#777777",        # Отключенные элементы
                "hover": "#505050",           # При наведении
                "selected": "#264F78"         # Выбранные элементы
            }
        }

        # Компонентные цвета (для конкретных компонентов интерфейса)
        self.component_colors = {
            "light": {
                # Кнопки
                "button-background": "@background-variant",
                "button-text": "@on-background",
                "button-hover": "@primary",
                "button-hover-text": "@on-primary",
                "button-pressed": "@primary-variant",
                "button-disabled": "@disabled",

                # Поля ввода
                "input-background": "@surface",
                "input-text": "@on-surface",
                "input-border": "@border",
                "input-focus-border": "@primary",

                # Вкладки
                "tab-background": "@background-variant",
                "tab-text": "@on-background",
                "tab-selected": "@primary",
                "tab-selected-text": "@on-primary",

                # Док-виджеты
                "dock-title": "@background-variant",
                "dock-border": "@border",

                # Меню
                "menu-background": "@background",
                "menu-text": "@on-background",
                "menu-hover": "@primary",
                "menu-hover-text": "@on-primary",

                # Терминал
                "terminal-background": "#F0F0F0",
                "terminal-text": "#000000",

                # Полосы прокрутки
                "scrollbar-background": "@background",
                "scrollbar-handle": "@background-variant",
                "scrollbar-hover": "@primary"
            },
            "dark": {
                # Кнопки
                "button-background": "@background-variant",
                "button-text": "@on-background",
                "button-hover": "@primary",
                "button-hover-text": "@on-primary",
                "button-pressed": "@primary-variant",
                "button-disabled": "@disabled",

                # Поля ввода
                "input-background": "@surface",
                "input-text": "@on-surface",
                "input-border": "@border",
                "input-focus-border": "@primary",

                # Вкладки
                "tab-background": "@background-variant",
                "tab-text": "@on-background",
                "tab-selected": "@primary",
                "tab-selected-text": "@on-primary",

                # Док-виджеты
                "dock-title": "@background-variant",
                "dock-border": "@border",

                # Меню
                "menu-background": "@background",
                "menu-text": "@on-background",
                "menu-hover": "@primary",
                "menu-hover-text": "@on-primary",

                # Терминал
                "terminal-background": "#1E1E1E",
                "terminal-text": "#E0E0E0",

                # Полосы прокрутки
                "scrollbar-background": "@background",
                "scrollbar-handle": "@background-variant",
                "scrollbar-hover": "@primary"
            }
        }

        # Текущая тема
        self.current_theme = self.settings.value("color_theme", "dark")

    def get_color(self, name, theme=None):
        """
        Получает цвет по имени.

        Args:
            name: Имя цвета
            theme: Тема (если None, используется текущая)

        Returns:
            Строка с цветом в формате HEX
        """
        theme = theme or self.current_theme

        # Проверяем сначала в компонентных цветах
        if name in self.component_colors.get(theme, {}):
            color_value = self.component_colors[theme][name]
            # Если значение ссылается на другой цвет (начинается с @)
            if color_value.startswith('@'):
                reference = color_value[1:]  # Убираем @
                return self.get_color(reference, theme)
            return color_value

        # Затем в базовых цветах
        if name in self.base_colors.get(theme, {}):
            return self.base_colors[theme][name]

        # Если не найдено, пробуем в альтернативной теме
        alt_theme = "light" if theme == "dark" else "dark"

        if name in self.component_colors.get(alt_theme, {}):
            color_value = self.component_colors[alt_theme][name]
            if color_value.startswith('@'):
                reference = color_value[1:]
                return self.get_color(reference, alt_theme)
            return color_value

        if name in self.base_colors.get(alt_theme, {}):
            return self.base_colors[alt_theme][name]

        # Если нигде не найдено, возвращаем значение по умолчанию
        print(f"Предупреждение: Цвет '{name}' не найден. Возвращаем значение по умолчанию.")
        return "#000000" if theme == "light" else "#FFFFFF"

    def get_qcolor(self, name, theme=None):
        """
        Получает цвет в формате QColor.

        Args:
            name: Имя цвета
            theme: Тема (если None, используется текущая)

        Returns:
            QColor
        """
        hex_color = self.get_color(name, theme)
        return QColor(hex_color)

    def set_theme(self, theme):
        """
        Устанавливает текущую тему.

        Args:
            theme: Имя темы ('light' или 'dark')

        Returns:
            bool: True если успешно, False если тема не поддерживается
        """
        if theme not in self.base_colors:
            print(f"Предупреждение: Тема '{theme}' не поддерживается.")
            return False

        self.current_theme = theme
        self.settings.setValue("color_theme", theme)
        self.settings.sync()

        # Оповещаем об изменении палитры
        self.paletteChanged.emit(theme)
        return True

    def get_current_theme(self):
        """Возвращает имя текущей темы."""
        return self.current_theme

    def generate_css_variables(self, theme=None):
        """
        Генерирует CSS-переменные для указанной или текущей темы.

        Args:
            theme: Имя темы (если None, используется текущая)

        Returns:
            str: CSS-определения переменных
        """
        theme = theme or self.current_theme
        css = ":root {\n"

        # Базовые цвета
        css += "    /* Base Colors */\n"
        for name, color in self.base_colors.get(theme, {}).items():
            css += f"    --{name}: {color};\n"

        # Компонентные цвета
        css += "\n    /* Component Colors */\n"
        for name, color_value in self.component_colors.get(theme, {}).items():
            # Если значение ссылается на другой цвет, разрешаем его
            if color_value.startswith('@'):
                reference = color_value[1:]
                resolved_color = self.get_color(reference, theme)
                css += f"    --{name}: {resolved_color}; /* from {color_value} */\n"
            else:
                css += f"    --{name}: {color_value};\n"

        css += "}\n"
        return css

    def save_css_variables(self, output_path, theme=None):
        """
        Сохраняет CSS-переменные в файл.

        Args:
            output_path: Путь для сохранения файла
            theme: Имя темы (если None, используется текущая)

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            css = self.generate_css_variables(theme)

            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(css)

            return True
        except Exception as e:
            print(f"Ошибка при сохранении CSS-переменных: {str(e)}")
            return False

    def load_theme_from_json(self, json_path):
        """
        Загружает тему из JSON-файла.

        Args:
            json_path: Путь к JSON-файлу с определением темы

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            theme_name = theme_data.get("name", "custom")
            theme_type = theme_data.get("type", "light")

            if "base_colors" in theme_data:
                self.base_colors[theme_type] = theme_data["base_colors"]

            if "component_colors" in theme_data:
                self.component_colors[theme_type] = theme_data["component_colors"]

            # Оповещаем об изменении палитры, если это текущая тема
            if self.current_theme == theme_type:
                self.paletteChanged.emit(theme_type)

            return True
        except Exception as e:
            print(f"Ошибка при загрузке темы из JSON: {str(e)}")
            return False

    def save_theme_to_json(self, json_path, theme_type=None, theme_name=None):
        """
        Сохраняет текущую или указанную тему в JSON-файл.

        Args:
            json_path: Путь для сохранения JSON-файла
            theme_type: Тип темы ('light' или 'dark', если None - текущая)
            theme_name: Имя темы (если None, используется 'custom')

        Returns:
            bool: True если успешно, False в случае ошибки
        """
        theme_type = theme_type or self.current_theme
        theme_name = theme_name or "custom"

        try:
            theme_data = {
                "name": theme_name,
                "type": theme_type,
                "base_colors": self.base_colors.get(theme_type, {}),
                "component_colors": self.component_colors.get(theme_type, {})
            }

            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4)

            return True
        except Exception as e:
            print(f"Ошибка при сохранении темы в JSON: {str(e)}")
            return False


# Создаем глобальный экземпляр системы цветов
color_system = ColorSystem()
