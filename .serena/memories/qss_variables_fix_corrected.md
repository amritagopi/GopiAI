# Исправление неопределенных переменных в QSS файлах тем

## Проблема

В файлах `dark.qss` и `light.qss` использовались переменные, которые не были определены:
- #3C3C3C_color
- #555555_hover
- #3498DB_color
- #6A6A6A_color
- #444444_radius

Это приводило к ошибкам при парсинге QSS стилей:
```
QCssParser::parseHexColor: Unknown color name '#3C3C3C_color'
QCssParser::parseHexColor: Unknown color name '#555555_hover'
QCssParser::parseHexColor: Unknown color name '#3498DB_color'
QCssParser::parseHexColor: Unknown color name '#6A6A6A_color'
QCssParser::parseHexColor: Unknown color name '#444444_radius'
```

## Решения

1. Добавлены определения переменных в начало файлов QSS с правильным синтаксисом:
```css
/* Определения для отсутствующих переменных */
#3C3C3C_color: #3C3C3C;
#555555_hover: #555555;
#3498DB_color: #3498DB;
#6A6A6A_color: #6A6A6A;
#444444_radius: 4px;
```

2. Добавлены те же определения в метод `_generate_stylesheet` в ThemeManager для подстраховки:
```python
# Добавляем дополнительные определения переменных, которые вызывают ошибки
additional_vars = """
/* Определения для отсутствующих переменных */
#3C3C3C_color: #3C3C3C;
#555555_hover: #555555;
#3498DB_color: #3498DB;
#6A6A6A_color: #6A6A6A;
#444444_radius: 4px;
"""
base_qss = additional_vars + base_qss
```

## Другие проблемы

Была исправлена ошибка в методе `_update_themes_menu` класса MainWindow:
```python
# Было:
for action in self.menu_manager.themes_menu.actions():
    if hasattr(action, "theme_name"):
        action.setChecked(action.theme_name == current_theme)

# Стало:
for action in self.menu_manager.themes_menu.actions():
    if action.data():
        action.setChecked(action.data() == current_theme)
```

Метод проверял несуществующее свойство `theme_name` у действий меню, хотя в `menu_manager.py` используется `action.setData(theme_name)`. После исправления проверяется наличие данных через `action.data()`.