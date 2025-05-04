# Менеджер тем GopiAI

## Обзор

Менеджер тем предоставляет централизованный способ управления внешним видом приложения GopiAI. 
Он поддерживает темную и светлую темы, а также позволяет создавать пользовательские темы.

## Использование в коде

```python
from app.utils.theme_manager import ThemeManager

# Получение экземпляра менеджера тем
theme_manager = ThemeManager.instance()

# Получение цвета из текущей темы
color = theme_manager.get_color('accent')

# Получение QColor из текущей темы
qcolor = theme_manager.get_qcolor('accent')

# Установка темы
theme_manager.set_theme('dark')  # или 'light'

Доступные цвета
background: Основной фоновый цвет
foreground: Основной цвет текста
accent: Акцентный цвет
secondary: Вторичный цвет
error: Цвет ошибок
success: Цвет успеха
warning: Цвет предупреждений
border: Цвет границ
tab_active: Цвет активной вкладки
tab_inactive: Цвет неактивной вкладки
button_normal: Цвет кнопки в обычном состоянии
button_hover: Цвет кнопки при наведении
button_pressed: Цвет кнопки при нажатии
input_background: Фоновый цвет полей ввода
input_text: Цвет текста в полях ввода
input_border: Цвет границы полей ввода