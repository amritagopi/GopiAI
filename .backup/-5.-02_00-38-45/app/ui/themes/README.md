# Система управления темами и цветами GopiAI

## Обзор

Система управления темами и цветами в GopiAI предоставляет централизованный способ управления внешним видом приложения. Она поддерживает темную и светлую темы, а также позволяет создавать пользовательские темы.

## Архитектура

Система состоит из следующих компонентов:

1. **ThemeManager** - основной класс для управления темами интерфейса
2. **ColorSystem** - система управления цветами и цветовыми переменными
3. **QSS файлы тем** - файлы стилей для темной и светлой темы
4. **Файлы переменных цветов** - CSS-переменные для каждой темы

## Использование в коде

### Менеджер тем

```python
from app.ui.theme_manager import ThemeManager

# Получение экземпляра менеджера тем
theme_manager = ThemeManager.instance()

# Получение текущей темы
current_theme = theme_manager.get_current_theme()

# Установка темы
theme_manager.switch_theme('dark')  # или 'light'

# Применение темы к приложению
theme_manager.apply_theme()
```

### Система цветов

```python
from app.ui.themes.color_system import ColorSystem

# Получение экземпляра системы цветов
color_system = ColorSystem.instance()

# Получение цвета из текущей темы
color = color_system.get_color('primary')

# Получение QColor из текущей темы
qcolor = color_system.get_qcolor('accent')

# Установка темы
color_system.set_theme('dark')  # или 'light'

# Генерация CSS-переменных для текущей темы
css_vars = color_system.generate_css_variables()
```

## Доступные цвета

### Базовые цвета

- **primary** - Основной цвет
- **primary-variant** - Вариант основного цвета
- **secondary** - Вторичный цвет
- **accent** - Акцентный цвет
- **background** - Основной фон
- **surface** - Поверхность (карточки, панели)
- **background-variant** - Вариант фона
- **on-primary** - Цвет текста на primary
- **on-secondary** - Цвет текста на secondary
- **on-background** - Цвет текста на background
- **on-surface** - Цвет текста на surface
- **error** - Ошибка
- **warning** - Предупреждение
- **success** - Успех
- **info** - Информация
- **border** - Границы
- **divider** - Разделители
- **disabled** - Отключенные элементы
- **hover** - При наведении
- **selected** - Выбранные элементы

### Компонентные цвета

- **button-background** - Фон кнопки
- **button-text** - Текст кнопки
- **button-hover** - Фон кнопки при наведении
- **button-hover-text** - Текст кнопки при наведении
- **button-pressed** - Фон кнопки при нажатии
- **button-disabled** - Фон отключенной кнопки
- **input-background** - Фон полей ввода
- **input-text** - Текст в полях ввода
- **input-border** - Границы полей ввода
- **input-focus-border** - Границы полей ввода в фокусе
- **tab-background** - Фон вкладки
- **tab-text** - Текст вкладки
- **tab-selected** - Фон выбранной вкладки
- **tab-selected-text** - Текст выбранной вкладки
- **dock-title** - Заголовок док-виджета
- **dock-border** - Границы док-виджета
- **menu-background** - Фон меню
- **menu-text** - Текст меню
- **menu-hover** - Фон меню при наведении
- **menu-hover-text** - Текст меню при наведении
- **terminal-background** - Фон терминала
- **terminal-text** - Текст терминала
- **scrollbar-background** - Фон полосы прокрутки
- **scrollbar-handle** - Ползунок полосы прокрутки
- **scrollbar-hover** - Ползунок при наведении

## Структура директорий

```
themes/
├── DARK-theme.qss          # Основной QSS файл темной темы
├── LIGHT-theme.qss         # Основной QSS файл светлой темы
├── compiled/               # Скомпилированные темы
│   ├── dark-theme.qss      # Скомпилированная темная тема
│   └── light-theme.qss     # Скомпилированная светлая тема
├── vars/                   # Переменные цветов
│   ├── dark-colors.qss     # Переменные цветов для темной темы
│   └── light-colors.qss    # Переменные цветов для светлой темы
├── color_system.py         # Класс системы цветов
└── README.md               # Документация
```

## Утилиты

Для управления темами и цветами доступны следующие утилиты:

1. **css_fixer.py** - Улучшенный инструмент для исправления CSS/QSS файлов
2. **css_refactor.py** - Инструмент для рефакторинга CSS/QSS файлов
3. **theme_compiler.py** - Компилятор тем
4. **fix_all_css_final.bat** - Пакетный файл для комплексного исправления всех CSS/QSS файлов
5. **fonts_fixer.py** - Исправляет файлы шрифтов CSS

## Настройка пользовательской темы

Для создания своей темы:

1. Создайте JSON-файл с определением темы:
   ```json
   {
     "name": "my_theme",
     "type": "dark",
     "base_colors": {
       "primary": "#3498DB",
       "background": "#2D2D2D",
       ...
     },
     "component_colors": {
       "button-background": "@background-variant",
       ...
     }
   }
   ```

2. Загрузите тему в `ColorSystem`:
   ```python
   ColorSystem.instance().load_theme_from_json('path/to/my_theme.json')
   ```

3. Примените тему:
   ```python
   ColorSystem.instance().set_theme('dark')
   ```

## Обнаруженные проблемы и их решения

1. **Дублирующиеся селекторы в QSS файлах**:
   - Решение: Использование утилиты `css_refactor.py` для исправления дубликатов

2. **Хардкодированные цвета**:
   - Решение: Использование системы цветовых переменных через `ColorSystem`

3. **Дублирующиеся селекторы в fonts.css**:
   - Решение: Использование утилиты `fonts_fixer.py` для нормализации шрифтов

## Инструменты для работы с темами

Для упрощения работы с темами и стилями реализованы следующие инструменты:

### 1. css_fixer.py

Улучшенный инструмент для исправления CSS/QSS файлов. Решает проблемы с дублирующимися селекторами.

```bash
python css_fixer.py <путь_к_файлу_или_директории>
```

### 2. css_refactor.py

Инструмент для рефакторинга CSS/QSS файлов:
- Выявляет и объединяет дублирующиеся селекторы
- Находит хардкодированные цвета и заменяет их на переменные
- Создает файл с цветовыми переменными

```bash
python css_refactor.py <путь_к_файлу> [--fix-duplicates] [--fix-colors] [--output <выходной_файл>]
```

### 3. theme_compiler.py

Компилирует QSS файлы тем с применением цветовых переменных:

```bash
python theme_compiler.py --compile-all --themes-dir app/ui/themes --output-dir app/ui/themes/compiled
```

### 4. fix_all_css_final.bat

Пакетный файл для комплексного исправления всех CSS/QSS файлов:

```bash
.\fix_all_css_final.bat
```

### 5. fonts_fixer.py

Исправляет файлы шрифтов CSS:

```bash
python fonts_fixer.py <путь_к_css_файлу> [выходной_файл]
```

## Рекомендации по разработке тем

1. Используйте CSS-переменные для всех цветов, определяя их в :root селекторе
2. Соблюдайте принятые соглашения об именовании (--bg-primary, --fg-secondary и т.д.)
3. После внесения изменений в исходные файлы темы используйте утилиты для компиляции и исправления
4. Перед коммитом проверьте наличие дублирующихся селекторов с помощью css_fixer.py

## Применение тем в приложении

Темы загружаются и применяются через класс `ThemeManager`. Для смены темы используйте:

```python
ThemeManager.instance().apply_theme("dark")
```

или

```python
ThemeManager.instance().apply_theme("light")
```
