# Структура утилит UI в GopiAI

Данный каталог (`app/ui/utils`) содержит утилиты для работы с UI компонентами приложения.

## Основные компоненты

- `css_tools/` - набор инструментов для обработки CSS/QSS файлов
  - Компиляция тем
  - Исправление дублирующихся селекторов
  - Работа с цветами и переменными
  - Автоматическая очистка и оптимизация CSS

## Взаимодействие с другими модулями

### Система тем

Важно: основная система управления темами находится в `app/utils/theme_manager.py` и `app/utils/theme_utils.py`.
В `app/ui/utils` мы используем ThemeManager, импортируя его из `app.utils`.

```python
# Правильный способ импорта ThemeManager
from app.utils.theme_manager import ThemeManager
```

### Разделение ответственности

- `app/utils/theme_manager.py` - управление темами в приложении (переключение, получение цветов)
- `app/utils/theme_utils.py` - утилиты для поддержки ThemeManager
- `app/ui/utils/css_tools` - инструменты для обработки CSS/QSS файлов на этапе разработки

Не рекомендуется дублировать функциональность между этими модулями.

## Использование инструментов CSS

Инструменты CSS доступны в `app.ui.utils.css_tools` и могут использоваться следующим образом:

```python
from app.ui.utils.css_tools import fix_css_file, fix_duplicate_selectors

# Пример использования
fix_css_file('path/to/style.qss')
```
