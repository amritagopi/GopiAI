#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простой менеджер тем с минимальным количеством функций и без усложнений.
"""

import os
import json
import logging
import math
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к файлу настроек
SETTINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings")
THEME_FILE = os.path.join(SETTINGS_DIR, "simple_theme.json")

# Выводим пути для отладки
print(f"Файл менеджера тем: {__file__}")
print(f"Директория настроек: {SETTINGS_DIR}")
print(f"Файл темы: {THEME_FILE}")

# --- КОЛЛЕКЦИЯ ТЕМ ---
MATERIAL_SKY_THEME = {
    "name": "Material Sky",
    "description": "Тема, сгенерированная на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fcf8f8",
        "header_color": "#cde5ff",
        "control_color": "#006398",
        "accent_color": "#7a4c8f",
        "titlebar_background": "#cde5ff",
        "button_color": "#3d6281",
        "button_hover_color": "#93ccff",
        "button_active_color": "#006398",
        "text_color": "#1c1b1c",
        "border_color": "#75777b",
        "titlebar_text": "#001d31"
    },
    "dark": {
        "main_color": "#131314",
        "header_color": "#004b73",
        "control_color": "#93ccff",
        "accent_color": "#e9b3ff",
        "titlebar_background": "#004b73",
        "button_color": "#a5caee",
        "button_hover_color": "#234a68",
        "button_active_color": "#003351",
        "text_color": "#e5e2e2",
        "border_color": "#8f9195",
        "titlebar_text": "#cde5ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

EMERALD_GARDEN_THEME = {
    "name": "Emerald Garden",
    "description": "Зелёная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fcf9f6",
        "header_color": "#b9f47d",
        "control_color": "#3b6a00",
        "accent_color": "#006c53",
        "titlebar_background": "#b9f47d",
        "button_color": "#4f6538",
        "button_hover_color": "#9ed764",
        "button_active_color": "#3b6a00",
        "text_color": "#1c1b1b",
        "border_color": "#767870",
        "titlebar_text": "#0e2000"
    },
    "dark": {
        "main_color": "#131312",
        "header_color": "#2b5000",
        "control_color": "#9ed764",
        "accent_color": "#5ddcb5",
        "titlebar_background": "#2b5000",
        "button_color": "#b5cf98",
        "button_hover_color": "#384d22",
        "button_active_color": "#1c3700",
        "text_color": "#e5e2e0",
        "border_color": "#909189",
        "titlebar_text": "#b9f47d"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

CRIMSON_RELIC_THEME = {
    "name": "Crimson Relic",
    "description": "Красная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fff8f7",
        "header_color": "#ffdad7",
        "control_color": "#c00020",
        "accent_color": "#875219",
        "titlebar_background": "#ffdad7",
        "button_color": "#894e4b",
        "button_hover_color": "#ffb3ae",
        "button_active_color": "#c00020",
        "text_color": "#1e1b1b",
        "border_color": "#817473",
        "titlebar_text": "#410005"
    },
    "dark": {
        "main_color": "#151313",
        "header_color": "#930016",
        "control_color": "#ffb3ae",
        "accent_color": "#ffb876",
        "titlebar_background": "#930016",
        "button_color": "#ffb3ae",
        "button_hover_color": "#6d3735",
        "button_active_color": "#68000c",
        "text_color": "#e8e1e0",
        "border_color": "#9b8e8c",
        "titlebar_text": "#ffdad7"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

GOLDEN_EMBER_THEME = {
    "name": "Golden Ember",
    "description": "Оранжево-золотая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fef8f7",
        "header_color": "#ffdbcf",
        "control_color": "#a43d0b",
        "accent_color": "#6e5e00",
        "titlebar_background": "#ffdbcf",
        "button_color": "#88503a",
        "button_hover_color": "#ffb59a",
        "button_active_color": "#a43d0b",
        "text_color": "#1d1b1b",
        "border_color": "#807571",
        "titlebar_text": "#380d00"
    },
    "dark": {
        "main_color": "#151313",
        "header_color": "#802a00",
        "control_color": "#ffb59a",
        "accent_color": "#ddc661",
        "titlebar_background": "#802a00",
        "button_color": "#ffb59a",
        "button_hover_color": "#6c3925",
        "button_active_color": "#5b1b00",
        "text_color": "#e7e1e0",
        "border_color": "#9b8e8a",
        "titlebar_text": "#ffdbcf"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

SUNLIT_MEADOW_THEME = {
    "name": "Sunlit Meadow",
    "description": "Жёлто-зелёная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fdf8f6",
        "header_color": "#ffdf91",
        "control_color": "#755b00",
        "accent_color": "#506600",
        "titlebar_background": "#ffdf91",
        "button_color": "#715c21",
        "button_hover_color": "#f3c015",
        "button_active_color": "#755b00",
        "text_color": "#1c1b1a",
        "border_color": "#7c766d",
        "titlebar_text": "#241a00"
    },
    "dark": {
        "main_color": "#141312",
        "header_color": "#594400",
        "control_color": "#f3c015",
        "accent_color": "#b2d34e",
        "titlebar_background": "#594400",
        "button_color": "#e0c47e",
        "button_hover_color": "#574409",
        "button_active_color": "#3e2e00",
        "text_color": "#e6e2df",
        "border_color": "#969086",
        "titlebar_text": "#ffdf91"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

MINT_FROST_THEME = {
    "name": "Mint Frost",
    "description": "Мятно-серо-лавандовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fcf8f7",
        "header_color": "#c8ead9",
        "control_color": "#466557",
        "accent_color": "#585d77",
        "titlebar_background": "#c8ead9",
        "button_color": "#54615b",
        "button_hover_color": "#adcebe",
        "button_active_color": "#466557",
        "text_color": "#1c1b1b",
        "border_color": "#747875",
        "titlebar_text": "#012016"
    },
    "dark": {
        "main_color": "#141313",
        "header_color": "#2f4d40",
        "control_color": "#adcebe",
        "accent_color": "#c1c5e3",
        "titlebar_background": "#2f4d40",
        "button_color": "#bccac2",
        "button_hover_color": "#3d4a44",
        "button_active_color": "#18362a",
        "text_color": "#e5e2e1",
        "border_color": "#8e928e",
        "titlebar_text": "#c8ead9"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

VIOLET_DREAM_THEME = {
    "name": "Violet Dream",
    "description": "Сине-фиолетовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fcf8f9",
        "header_color": "#e0e0ff",
        "control_color": "#3e4ade",
        "accent_color": "#82478f",
        "titlebar_background": "#e0e0ff",
        "button_color": "#555a90",
        "button_hover_color": "#bec2ff",
        "button_active_color": "#3e4ade",
        "text_color": "#1c1b1c",
        "border_color": "#78767c",
        "titlebar_text": "#000569"
    },
    "dark": {
        "main_color": "#141314",
        "header_color": "#202cc7",
        "control_color": "#bec2ff",
        "accent_color": "#f4aeff",
        "titlebar_background": "#202cc7",
        "button_color": "#bec2ff",
        "button_hover_color": "#3e4276",
        "button_active_color": "#000ca5",
        "text_color": "#e5e1e2",
        "border_color": "#929096",
        "titlebar_text": "#e0e0ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

INDIGO_CANDY_THEME = {
    "name": "Indigo Candy",
    "description": "Индиго-розовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fcf8f9",
        "header_color": "#e1e0ff",
        "control_color": "#4b50c6",
        "accent_color": "#8b428d",
        "titlebar_background": "#e1e0ff",
        "button_color": "#585a89",
        "button_hover_color": "#c0c1ff",
        "button_active_color": "#4b50c6",
        "text_color": "#1c1b1c",
        "border_color": "#78767c",
        "titlebar_text": "#04006d"
    },
    "dark": {
        "main_color": "#141314",
        "header_color": "#3235ad",
        "control_color": "#c0c1ff",
        "accent_color": "#ffa9fd",
        "titlebar_background": "#3235ad",
        "button_color": "#c1c2f7",
        "button_hover_color": "#41436f",
        "button_active_color": "#161598",
        "text_color": "#e5e1e2",
        "border_color": "#929095",
        "titlebar_text": "#e1e0ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

PINK_MIRAGE_THEME = {
    "name": "Pink Mirage",
    "description": "Розово-фиолетовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fef8f8",
        "header_color": "#ffd7f2",
        "control_color": "#ab00a1",
        "accent_color": "#894d55",
        "titlebar_background": "#ffd7f2",
        "button_color": "#8b4580",
        "button_hover_color": "#ffabed",
        "button_active_color": "#ab00a1",
        "text_color": "#1d1b1c",
        "border_color": "#7d7579",
        "titlebar_text": "#390035"
    },
    "dark": {
        "main_color": "#151314",
        "header_color": "#83007b",
        "control_color": "#ffabed",
        "accent_color": "#ffb2bb",
        "titlebar_background": "#83007b",
        "button_color": "#ffabed",
        "button_hover_color": "#6f2d66",
        "button_active_color": "#5d0057",
        "text_color": "#e7e1e2",
        "border_color": "#988e93",
        "titlebar_text": "#ffd7f2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

OLIVE_LIBRARY_THEME = {
    "name": "Olive Library",
    "description": "Оливково-бежево-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fdf8f7",
        "header_color": "#eae2c9",
        "control_color": "#635e4a",
        "accent_color": "#596154",
        "titlebar_background": "#eae2c9",
        "button_color": "#615e54",
        "button_hover_color": "#cec6ae",
        "button_active_color": "#635e4a",
        "text_color": "#1c1b1b",
        "border_color": "#797770",
        "titlebar_text": "#1f1c0c"
    },
    "dark": {
        "main_color": "#141313",
        "header_color": "#4b4734",
        "control_color": "#cec6ae",
        "accent_color": "#c1c9b9",
        "titlebar_background": "#4b4734",
        "button_color": "#cbc6ba",
        "button_hover_color": "#49473e",
        "button_active_color": "#34301f",
        "text_color": "#e5e2e1",
        "border_color": "#939189",
        "titlebar_text": "#eae2c9"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

LAVENDER_MIST_THEME = {
    "name": "Lavender Mist",
    "description": "Лавандово-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fdf8f8",
        "header_color": "#e0e1f2",
        "control_color": "#5b5e6b",
        "accent_color": "#6a5a64",
        "titlebar_background": "#e0e1f2",
        "button_color": "#5e5e63",
        "button_hover_color": "#c4c6d5",
        "button_active_color": "#5b5e6b",
        "text_color": "#1c1b1b",
        "border_color": "#78767b",
        "titlebar_text": "#181b26"
    },
    "dark": {
        "main_color": "#141313",
        "header_color": "#434653",
        "control_color": "#c4c6d5",
        "accent_color": "#d6c1cd",
        "titlebar_background": "#434653",
        "button_color": "#c7c6cc",
        "button_hover_color": "#46464b",
        "button_active_color": "#2d303c",
        "text_color": "#e5e2e1",
        "border_color": "#929094",
        "titlebar_text": "#e0e1f2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

GRAPHITE_NIGHT_THEME = {
    "name": "Graphite Night",
    "description": "Графитово-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fdf8f8",
        "header_color": "#dde4e3",
        "control_color": "#586060",
        "accent_color": "#605d64",
        "titlebar_background": "#dde4e3",
        "button_color": "#5c5f5e",
        "button_hover_color": "#c1c8c7",
        "button_active_color": "#586060",
        "text_color": "#1c1b1b",
        "border_color": "#747779",
        "titlebar_text": "#161d1d"
    },
    "dark": {
        "main_color": "#141313",
        "header_color": "#414848",
        "control_color": "#c1c8c7",
        "accent_color": "#cac5cd",
        "titlebar_background": "#414848",
        "button_color": "#c5c7c6",
        "button_hover_color": "#444747",
        "button_active_color": "#2b3232",
        "text_color": "#e5e2e1",
        "border_color": "#8e9192",
        "titlebar_text": "#dde4e3"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

PUMPKIN_FIELD_THEME = {
    "name": "Pumpkin Field",
    "description": "Тыквенно-оранжевая с зелёным акцентом тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fef8f6",
        "header_color": "#ffdcc6",
        "control_color": "#944a00",
        "accent_color": "#5d6300",
        "titlebar_background": "#ffdcc6",
        "button_color": "#815433",
        "button_hover_color": "#ffb784",
        "button_active_color": "#944a00",
        "text_color": "#1d1b1a",
        "border_color": "#80756f",
        "titlebar_text": "#301400"
    },
    "dark": {
        "main_color": "#141312",
        "header_color": "#713700",
        "control_color": "#ffb784",
        "accent_color": "#c6ce56",
        "titlebar_background": "#713700",
        "button_color": "#f5ba92",
        "button_hover_color": "#653d1e",
        "button_active_color": "#4f2500",
        "text_color": "#e7e1e0",
        "border_color": "#9a8e88",
        "titlebar_text": "#ffdcc6"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

SCARLET_FIRE_THEME = {
    "name": "Scarlet Fire",
    "description": "Алый, насыщенно-красный вариант на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#fff8f7",
        "header_color": "#ffdad5",
        "control_color": "#c00007",
        "accent_color": "#875203",
        "titlebar_background": "#ffdad5",
        "button_color": "#884f46",
        "button_hover_color": "#ffb4a9",
        "button_active_color": "#c00007",
        "text_color": "#1e1b1a",
        "border_color": "#817472",
        "titlebar_text": "#410001"
    },
    "dark": {
        "main_color": "#151312",
        "header_color": "#930004",
        "control_color": "#ffb4a9",
        "accent_color": "#ffb867",
        "titlebar_background": "#930004",
        "button_color": "#ffb4a9",
        "button_hover_color": "#6c3831",
        "button_active_color": "#690002",
        "text_color": "#e8e1e0",
        "border_color": "#9c8d8b",
        "titlebar_text": "#ffdad5"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

TROPICAL_BOUQUET_THEME = {
    "name": "Tropical Bouquet",
    "description": "Тропическая тема: попугайчики, бугенвиллия, салатовые и розовые акценты. Светлый — нежный, тёмный — неоновый!",
    "light": {
        "main_color": "#fff8f8",
        "header_color": "#ffd9e2",
        "control_color": "#b90063",
        "accent_color": "#506600",
        "titlebar_background": "#ffd9e2",
        "button_color": "#326b00",
        "button_hover_color": "#ffb1c8",
        "button_active_color": "#b90063",
        "text_color": "#1d1b1b",
        "border_color": "#807477",
        "titlebar_text": "#3e001d"
    },
    "dark": {
        "main_color": "#151313",
        "header_color": "#8e004a",
        "control_color": "#ffb1c8",
        "accent_color": "#aad600",
        "titlebar_background": "#8e004a",
        "button_color": "#70e000",
        "button_hover_color": "#245100",
        "button_active_color": "#650033",
        "text_color": "#e7e1e1",
        "border_color": "#9a8e90",
        "titlebar_text": "#ffd9e2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

THEME_COLLECTION = [MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME, CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME, SUNLIT_MEADOW_THEME, MINT_FROST_THEME, VIOLET_DREAM_THEME, INDIGO_CANDY_THEME, PINK_MIRAGE_THEME, OLIVE_LIBRARY_THEME, LAVENDER_MIST_THEME, GRAPHITE_NIGHT_THEME, PUMPKIN_FIELD_THEME, SCARLET_FIRE_THEME, TROPICAL_BOUQUET_THEME]

def theme_palette_to_struct(palette):
    """
    Преобразует палитру HEX-кодов в структуру темы для simple_theme_manager.
    palette: список HEX-строк (от 6 до 10)
    Возвращает dict с ключами темы.
    """
    def safe(idx, default):
        try:
            return palette[idx]
        except IndexError:
            return default
    return {
        "main_color": safe(1, palette[0]),
        "header_color": safe(2, palette[0]),
        "control_color": safe(6, palette[0]),
        "accent_color": safe(7, palette[0]),
        "titlebar_background": safe(2, palette[0]),
        "button_color": safe(3, palette[0]),
        "button_hover_color": _lighten_color(safe(3, palette[0]), 15),
        "button_active_color": safe(6, palette[0]),
        "text_color": "#222" if _is_light(safe(1, palette[0])) else "#fff",
        "border_color": _darken_color(safe(1, palette[0]), 10),
        "titlebar_text": "#fff" if not _is_light(safe(2, palette[0])) else "#222"
    }

def _is_light(hex_color):
    """True если цвет светлый (для текста)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance > 180

def generate_default_colors():
    """
    Генерирует дефолтные цвета на основе начального положения маркеров на цветовом колесе.
    Это позволяет иметь приятную цветовую схему без необходимости настройки пользователем.

    Returns:
        list: Список QColor объектов (основной, фон, заголовок, кнопки)
    """
    # Создаем основной цвет (яркий синий)
    primary_color = QColor(0, 120, 255)  # #0078FF - ярко-синий

    # Фон - светло-серый
    bg_color = QColor(240, 240, 240)  # #F0F0F0 - светло-серый

    # Заголовок - темно-синий
    header_color = QColor(0, 50, 100)  # #003264 - темно-синий

    # Кнопки - яркие, привлекательные
    button_color = QColor(255, 80, 0)  # #FF5000 - оранжевый

    # Акцент/выделение
    accent_color = QColor(255, 0, 100)  # #FF0064 - розовый

    return [primary_color, bg_color, header_color, button_color, accent_color]

def save_theme(colors):
    """
    Простая функция для сохранения темы в файл.

    Args:
        colors: Список QColor объектов (обычно 4 цвета: основной, фон, заголовок, кнопки)
    """
    try:
        # Создаем директорию, если она не существует
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        # Выводим отладочную информацию
        print(f"Сохраняем тему. Директория настроек: {SETTINGS_DIR}")
        print(f"Файл темы: {THEME_FILE}")
        print(f"Директория существует: {os.path.exists(SETTINGS_DIR)}")
        # Создаем новую структуру темы без дефолтных цветов
        theme_data = {}
        if len(colors) >= 4:
            # Получаем основные цвета
            main_color = colors[0]  # Основной/акцентный цвет
            bg_color = colors[1]    # Фон
            header_color = colors[2]  # Заголовок
            button_color = colors[3]  # Кнопки

            # Выбираем подходящий цвет текста на основе яркости фона
            bg_luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
            text_color = "#FFFFFF" if bg_luminance < 128 else "#000000"

            # Формируем hex-представление
            theme_data.update({
                "main_color": bg_color.name(),
                "header_color": header_color.name(),
                "control_color": main_color.name(),
                "accent_color": main_color.name(),
                "titlebar_background": header_color.name(),
                "button_color": button_color.name(),
                # Создаем цвет при наведении, делая кнопку немного светлее
                "button_hover_color": _lighten_color(button_color.name()),
                "button_active_color": main_color.name(),
                "text_color": text_color,  # Адаптивный цвет текста
                "border_color": _darken_color(bg_color.name(), 10),  # Создаем рамку на основе фона
                "titlebar_text": "#FFFFFF"  # Белый текст заголовка
            })

            # Добавляем информацию о исходных цветах для отладки
            theme_data["_original_colors"] = [
                {"index": 0, "name": "primary", "hex": main_color.name(),
                 "rgb": [main_color.red(), main_color.green(), main_color.blue()]},
                {"index": 1, "name": "background", "hex": bg_color.name(),
                 "rgb": [bg_color.red(), bg_color.green(), bg_color.blue()]},
                {"index": 2, "name": "header", "hex": header_color.name(),
                 "rgb": [header_color.red(), header_color.green(), header_color.blue()]},
                {"index": 3, "name": "button", "hex": button_color.name(),
                 "rgb": [button_color.red(), button_color.green(), button_color.blue()]}
            ]

        # Сохраняем простой JSON без лишних вложенных структур
        with open(THEME_FILE, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2)

        print(f"Тема сохранена в файл: {THEME_FILE}")

        # Показываем дамп файла для отладки
        print("Содержимое файла настроек темы:")
        with open(THEME_FILE, 'r', encoding='utf-8') as f:
            print(f.read())

        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении темы: {e}")
        return False

def load_theme():
    """
    Простая функция для загрузки темы из файла.

    Returns:
        dict: Словарь с настройками темы или None, если тема не найдена
    """
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                print(f"Тема загружена из файла: {THEME_FILE}")
                return theme_data
    except Exception as e:
        logger.error(f"Ошибка при загрузке темы: {e}")

    # Возвращаем None, чтобы показать, что пользователю нужно выбрать тему
    print("Тема не найдена, будут использованы дефолтные цвета")
    return None

def apply_theme(app):
    """
    Применяет тему к приложению.

    Args:
        app: Экземпляр QApplication
    """
    if not app:
        logger.error("QApplication не предоставлен")
        print("ОШИБКА: QApplication не предоставлен")
        return False
    print("\n--- ДИАГНОСТИКА ПРИМЕНЕНИЯ ТЕМЫ ---")
    print(f"Текущий стиль: {app.style().objectName()}")
    # Загружаем тему
    theme = load_theme()
    print(f"Результат загрузки темы: {'Успешно' if theme else 'Неудача'}")
    # Если тема не найдена, создаем и сохраняем дефолтную тему
    if not theme:
        default_colors = generate_default_colors()
        print("Создаем и сохраняем дефолтную тему на основе положения маркеров")
        # Проверяем существование директории
        if not os.path.exists(SETTINGS_DIR):
            print(f"Директория настроек не существует, создаём: {SETTINGS_DIR}")
            os.makedirs(SETTINGS_DIR, exist_ok=True)
        # Сохраняем тему
        save_result = save_theme(default_colors)
        print(f"Результат сохранения темы: {'Успешно' if save_result else 'Ошибка'}")
        # Проверяем, создался ли файл
        print(f"Файл темы существует после сохранения: {os.path.exists(THEME_FILE)}")
        # Перезагружаем тему из файла
        theme = load_theme()
        print(f"Повторная загрузка темы: {'Успешно' if theme else 'Неудача'}")
        if not theme:
            print("Не удалось создать дефолтную тему")
            return False
    print(f"Доступные ключи в теме: {', '.join(theme.keys())}")

    # Проверяем и устанавливаем контрастные цвета текста
    # Если text_color не указан или цвет фона и текста слишком близкие
    if "main_color" in theme:
        main_color = QColor(theme.get("main_color"))
        # Проверяем яркость основного цвета (0-255)
        luminance = (0.299 * main_color.red() + 0.587 * main_color.green() + 0.114 * main_color.blue())

        # Если фон темный, устанавливаем светлый текст
        if luminance < 128:
            theme["text_color"] = "#FFFFFF"  # Белый текст для темного фона
            print(f"Установлен светлый текст для темного фона (яркость: {luminance})")
        else:
            theme["text_color"] = "#000000"  # Черный текст для светлого фона
            print(f"Установлен темный текст для светлого фона (яркость: {luminance})")
    # Применяем палитру цветов для элементов, которые не покрываются CSS
    try:
        # Создаем и настраиваем палитру на основе цветов темы
        palette = QPalette()
        # Получаем цвета из темы без дефолтов
        main_color = QColor(theme.get("main_color", "#FFFFFF"))
        text_color = QColor(theme.get("text_color", "#000000"))
        accent_color = QColor(theme.get("accent_color", "#0078D7"))
        border_color = QColor(theme.get("border_color", "#CCCCCC"))
        button_color = QColor(theme.get("button_color", "#E0E0E0"))
        header_color = QColor(theme.get("header_color", "#F0F0F0"))
        print(f"Цвета из темы: main={main_color.name()}, text={text_color.name()}, accent={accent_color.name()}")
        # Настраиваем все цвета палитры
        palette.setColor(QPalette.Window, main_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, main_color)  # Изменено с main_color.darker(110)
        palette.setColor(QPalette.AlternateBase, main_color.lighter(110))
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, button_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, accent_color)
        palette.setColor(QPalette.Highlight, accent_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipBase, main_color)  # Изменено с main_color.darker(120)
        palette.setColor(QPalette.ToolTipText, text_color)

        # Устанавливаем палитру
        app.setPalette(palette)
        print("Цветовая палитра успешно применена")
    except Exception as e:
        logger.error(f"Ошибка при настройке палитры: {e}")
        print(f"ОШИБКА при настройке палитры: {e}")

    # Применяем стиль приложения через CSS
    try:
        style_sheet = generate_style_sheet(theme)
        print(f"Длина сгенерированной таблицы стилей: {len(style_sheet)} символов")
        app.setStyleSheet(style_sheet)
        print("Таблица стилей применена к приложению")
    except Exception as e:
        logger.error(f"Ошибка при применении стилей: {e}")
        print(f"ОШИБКА при применении стилей: {e}")

    # Принудительно обновляем стили всех виджетов
    try:
        widget_count = 0
        for widget in app.allWidgets():
            try:
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                # update() у некоторых виджетов (например, QListWidget) требует аргумент, поэтому вызываем только если сигнатура без аргументов
                if hasattr(widget, 'update'):
                    import inspect
                    sig = inspect.signature(widget.update)
                    if len(sig.parameters) == 0:
                        widget.update()
                widget_count += 1
            except Exception as werr:
                logger.warning(f"Ошибка при обновлении виджета {type(widget).__name__}: {werr}")
        print(f"Обновлено {widget_count} виджетов")
    except Exception as e:
        logger.error(f"Ошибка при обновлении виджетов: {e}")
        print(f"ОШИБКА при обновлении виджетов: {e}")

    # Удаляем файл current_theme.json, если он существует,
    # чтобы избежать конфликтов с устаревшей системой тем
    try:
        old_theme_file = os.path.join(SETTINGS_DIR, "current_theme.json")
        if os.path.exists(old_theme_file):
            os.remove(old_theme_file)
            print(f"Удален устаревший файл темы: {old_theme_file}")
    except Exception as e:
        logger.error(f"Ошибка при удалении устаревшего файла темы: {e}")

    print("--- КОНЕЦ ДИАГНОСТИКИ ---\n")
    return True

def generate_style_sheet(theme):
    """
    Генерирует таблицу стилей для приложения на основе темы.

    Args:
        theme: Словарь с настройками темы

    Returns:
        str: Строка с CSS-стилями
    """
    # Базовый CSS для темы, используем только цвета из темы, никаких дефолтных значений
    qss = f"""
        /* ГЛОБАЛЬНЫЕ НАСТРОЙКИ ДЛЯ ВСЕХ ВИДЖЕТОВ С ВЫСШИМ ПРИОРИТЕТОМ */
        * {{
            background-color: {theme.get("main_color")};
            color: {theme.get("text_color")};
        }}

        /* ОСНОВНЫЕ ВИДЖЕТЫ */
        QMainWindow, QMainWindow > QWidget, QDialog, QWidget, QFrame, QMenu, QMenuBar, QScrollArea {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
        }}

        /* ОЧЕНЬ ВАЖНО: Явно указываем цвет фона для центрального виджета и его дочерних элементов */
        QMainWindow::centralWidget, #centralWidget, #centralWidget > QWidget, #centralWidget * {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
        }}

        /* Стиль для всех элементов редактора */
        TextEditorWidget, TextEditorWidget QWidget, TextEditorWidget > * {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
        }}

        /* Форсированное применение основного стиля ко ВСЕМ виджетам */
        QWidget, QWidget * {{
            background-color: {theme.get("main_color")};
            color: {theme.get("text_color")};
        }}

        /* Стиль для безрамочного окна */
        #framelessMainWindow, #framelessMainWindow > * {{
            background-color: {theme.get("main_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 10px;
        }}

        /* Стиль для панели заголовка */
        #titlebarWidget, .QToolBar, #titleBarWidget {{
            background-color: {theme.get("titlebar_background")} !important;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            color: {theme.get("titlebar_text")} !important;
            height: 40px;
        }}

        /* Стиль для заголовка окна */
        #windowTitle, QLabel#titleLabel, #titleLabel {{
            color: {theme.get("titlebar_text")} !important;
            font-weight: bold;
            padding-left: 15px;
            font-size: 14px;
            background-color: transparent !important;
        }}

        /* Стиль для всех диалогов */
        QDialog, QDialog > * {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 10px;
        }}

        /* Стили для ComplementaryThemeDialog */
        #mainContainer {{
            background-color: {theme.get("main_color")} !important;
            border-radius: 15px;
            border: 1px solid {theme.get("border_color")};
        }}

        #contentContainer {{
            background-color: {theme.get("main_color")} !important;
            border-radius: 15px;
            border: 1px solid {theme.get("border_color")};
        }}

        #titleBarWidget {{
            background-color: {theme.get("titlebar_background")} !important;
            color: {theme.get("titlebar_text")} !important;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            height: 30px;
        }}

        /* Все метки/текстовые поля */
        QLabel {{
            background-color: transparent !important;
            color: {theme.get("text_color")} !important;
        }}

        /* Стиль для кнопок панели заголовка */
        #minimizeButton, #maximizeButton, #restoreButton, #closeButton {{
            font-family: 'Segoe UI Symbol', 'Arial Unicode MS';
            font-size: 14px;
            border-radius: 0px;
            background-color: transparent !important;
            border: none;
            color: {theme.get("text_color")} !important;
            width: 40px;
            height: 40px;
            padding: 0px;
        }}

        #minimizeButton:hover, #maximizeButton:hover, #restoreButton:hover {{
            background-color: {theme.get("button_hover_color")} !important;
        }}

        #closeButton:hover {{
            background-color: #E81123 !important;
        }}

        #minimizeButton:pressed, #maximizeButton:pressed, #restoreButton:pressed {{
            background-color: {theme.get("button_active_color")} !important;
        }}

        #closeButton:pressed {{
            background-color: #F1707A !important;
        }}

        /* Стиль для текстового редактора */
        QPlainTextEdit, QTextEdit {{
            background-color: {_darken_color(theme.get("main_color"), 10)} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 5px;
            padding: 5px;
            selection-background-color: {theme.get("control_color")};
            selection-color: {theme.get("text_color")};
        }}

        /* Стиль для кнопок */
        QPushButton {{
            background-color: {theme.get("button_color")} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 5px;
            padding: 5px 15px;
            min-height: 30px;
        }}

        QPushButton:hover {{
            background-color: {theme.get("button_hover_color")} !important;
            border: 1px solid {theme.get("control_color")};
        }}

        QPushButton:pressed {{
            background-color: {theme.get("button_active_color")} !important;
        }}

        /* Специальные кнопки в диалоге комплементарных тем - оставляем фиксированные цвета */
        #saveButton {{
            background-color: #4CAF50 !important;
            border: 1px solid #388E3C;
            color: white !important;
            min-width: 150px;
            min-height: 45px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
        }}

        #saveButton:hover {{
            background-color: #66BB6A !important;
            border: 1px solid #4CAF50;
        }}

        #saveButton:pressed {{
            background-color: #388E3C !important;
        }}

        #okButton {{
            background-color: #2196F3 !important;
            border: 1px solid #1976D2;
            color: white !important;
            min-width: 150px;
            min-height: 45px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
        }}

        #okButton:hover {{
            background-color: #42A5F5 !important;
            border: 1px solid #2196F3;
        }}

        #okButton:pressed {{
            background-color: #1976D2 !important;
        }}

        #cancelButton {{
            background-color: #F44336 !important;
            border: 1px solid #D32F2F;
            color: white !important;
            min-width: 150px;
            min-height: 45px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
        }}

        #cancelButton:hover {{
            background-color: #EF5350 !important;
            border: 1px solid #F44336;
        }}

        #cancelButton:pressed {{
            background-color: #D32F2F !important;
        }}

        /* Стили для комбобоксов и списков */
        QComboBox, QListView {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 5px;
            padding: 5px;
        }}

        QComboBox:on {{ /* при открытии */
            background-color: {theme.get("main_color")} !important;
            border: 1px solid {theme.get("control_color")};
        }}

        QComboBox QAbstractItemView {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
            selection-background-color: {theme.get("control_color")};
            selection-color: {theme.get("text_color")};
            border: 1px solid {theme.get("border_color")};
        }}

        /* Стиль для статус бара */
        QStatusBar {{
            background-color: {theme.get("titlebar_background")} !important;
            color: {theme.get("text_color")} !important;
            border-top: 1px solid {theme.get("border_color")};
        }}

        /* Цветовые индикаторы в диалоге тем */
        ColorPreview {{
            background-color: {theme.get("main_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 3px;
        }}

        ColorButton {{
            background-color: {theme.get("button_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 3px;
        }}

        /* Стиль для группирующих рамок */
        QGroupBox {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: {theme.get("text_color")} !important;
        }}

        /* Стиль для полосы прокрутки */
        QScrollBar:vertical {{
            background-color: {theme.get("main_color")} !important;
            width: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {theme.get("button_color")} !important;
            min-height: 20px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {theme.get("button_hover_color")} !important;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background-color: {theme.get("main_color")} !important;
            height: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {theme.get("button_color")} !important;
            min-width: 20px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {theme.get("button_hover_color")} !important;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Цветовое колесо на панели темы */
        ComplementaryPaletteWidget {{
            background-color: {theme.get("main_color")} !important;
            border: 1px solid {theme.get("border_color")};
            border-radius: 5px;
        }}

        /* Стиль для меню */
        QMenuBar {{
            background-color: {theme.get("header_color")} !important;
            color: {theme.get("text_color")} !important;
            border-bottom: 1px solid {theme.get("border_color")};
        }}

        QMenuBar::item {{
            background-color: transparent !important;
            padding: 5px 10px;
        }}

        QMenuBar::item:selected {{
            background-color: {theme.get("control_color")} !important;
        }}

        QMenu {{
            background-color: {theme.get("main_color")} !important;
            color: {theme.get("text_color")} !important;
            border: 1px solid {theme.get("border_color")};
        }}

        QMenu::item {{
            padding: 5px 30px 5px 20px;
        }}

        QMenu::item:selected {{
            background-color: {theme.get("control_color")} !important;
        }}
    """
    return qss

def _lighten_color(hex_color, percent=20):
    """
    Осветляет цвет на указанный процент.

    Args:
        hex_color: Цвет в формате hex (#RRGGBB)
        percent: Процент осветления

    Returns:
        str: Новый цвет в формате hex
    """
    # Преобразуем hex в rgb
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Осветляем каждый канал
    r = min(255, int(r * (1 + percent / 100)))
    g = min(255, int(g * (1 + percent / 100)))
    b = min(255, int(b * (1 + percent / 100)))

    # Возвращаем hex
    return f"#{r:02x}{g:02x}{b:02x}"

def _darken_color(hex_color, percent=20):
    """
    Затемняет цвет на указанный процент.

    Args:
        hex_color: Цвет в формате hex (#RRGGBB)
        percent: Процент затемнения

    Returns:
        str: Новый цвет в формате hex
    """
    # Преобразуем hex в rgb
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Затемняем каждый канал
    r = max(0, int(r * (1 - percent / 100)))
    g = max(0, int(g * (1 - percent / 100)))
    b = max(0, int(b * (1 - percent / 100)))

    # Возвращаем hex
    return f"#{r:02x}{g:02x}{b:02x}"

def get_theme_variant(theme, variant):
    """Возвращает палитру для выбранной темы и варианта ('light' или 'dark')."""
    if variant not in ("light", "dark"):
        variant = "light"
    return theme[variant]

def choose_theme_dialog(app=None):
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QListWidget, QListWidgetItem
    from PySide6.QtCore import Qt

    class ThemeDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Выбор темы и варианта оформления")
            self.setMinimumWidth(420)
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            self._drag_active = False
            self._drag_pos = None
            layout = QVBoxLayout(self)
            self.list = QListWidget(self)
            self._items = []
            self._current_variant = "light"
            for theme in THEME_COLLECTION:
                item = QListWidgetItem(theme["name"])
                pal = get_theme_variant(theme, self._current_variant)
                item.setBackground(QColor(pal["main_color"]))
                item.setForeground(QColor(pal["text_color"]))
                self.list.addItem(item)
                self._items.append(item)
            layout.addWidget(self.list)
            self.variant_combo = QComboBox(self)
            self.variant_combo.addItem("Светлая (Light)", "light")
            self.variant_combo.addItem("Тёмная (Dark)", "dark")
            layout.addWidget(self.variant_combo)
            self.desc = QLabel("", self)
            self.desc.setWordWrap(True)
            layout.addWidget(self.desc)
            self.preview = QLabel(self)
            self.preview.setFixedHeight(32)
            layout.addWidget(self.preview)
            btns = QHBoxLayout()
            self.ok = QPushButton("OK", self)
            self.cancel = QPushButton("Отмена", self)
            btns.addWidget(self.ok)
            btns.addWidget(self.cancel)
            layout.addLayout(btns)
            self.list.currentRowChanged.connect(self.update_preview)
            self.variant_combo.currentIndexChanged.connect(self.update_variant)
            self.ok.clicked.connect(self.accept)
            self.cancel.clicked.connect(self.reject)
            self.list.setCurrentRow(0)
            self.update_preview(0)
        def update_variant(self, idx):
            self._current_variant = self.variant_combo.currentData()
            for i, theme in enumerate(THEME_COLLECTION):
                pal = get_theme_variant(theme, self._current_variant)
                self._items[i].setBackground(QColor(pal["main_color"]))
                self._items[i].setForeground(QColor(pal["text_color"]))
            self.update_preview(self.list.currentRow())
        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
            super().mousePressEvent(event)
        def mouseMoveEvent(self, event):
            if self._drag_active and event.buttons() & Qt.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
            super().mouseMoveEvent(event)
        def mouseReleaseEvent(self, event):
            if event.button() == Qt.LeftButton:
                self._drag_active = False
            super().mouseReleaseEvent(event)
        def update_preview(self, idx):
            theme = THEME_COLLECTION[self.list.currentRow()]
            variant = self.variant_combo.currentData()
            pal = get_theme_variant(theme, variant)
            self.desc.setText(theme["description"])
            grad = f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {pal['main_color']}, stop:0.5 {pal['accent_color']}, stop:1 {pal['button_color']});"
            self.preview.setStyleSheet(grad)
        def get_selected(self):
            return self.list.currentRow(), self.variant_combo.currentData()
    dlg = ThemeDialog()
    if dlg.exec() == QDialog.Accepted:
        idx, variant = dlg.get_selected()
        theme = THEME_COLLECTION[idx]
        pal = get_theme_variant(theme, variant)
        save_material_sky_theme(pal)  # сохраняем в том же формате
        if app:
            apply_theme(app)
        return idx, variant
    return None

def save_material_sky_theme(pal):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(THEME_FILE, 'w', encoding='utf-8') as f:
        json.dump(pal, f, indent=2)

def load_theme():
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                print(f"Тема загружена из файла: {THEME_FILE}")
                return theme_data
    except Exception as e:
        logger.error(f"Ошибка при загрузке темы: {e}")
    print("Тема не найдена, будут использованы дефолтные цвета")
    return get_theme_variant(MATERIAL_SKY_THEME, "light")

# Пример использования:
# app = QApplication([])
# apply_theme(app)
