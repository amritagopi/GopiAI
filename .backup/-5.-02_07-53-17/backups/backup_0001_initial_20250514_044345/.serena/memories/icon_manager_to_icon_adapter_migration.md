# Миграция с icon_manager на icon_adapter

В проекте была проведена миграция с устаревшего модуля `icon_manager` на новый адаптер `icon_adapter`.

## Изменения

Старый импорт:
```python
from .icon_manager import get_icon
```

Новый импорт:
```python
from app.ui.icon_adapter import get_icon
```

## Исправленные файлы

Следующие файлы были исправлены для использования нового импорта:

1. app/ui/browser_tab_widget.py
2. app/ui/code_analysis_integration.py
3. app/ui/code_analysis_widget.py
4. app/ui/output_widget.py
5. app/ui/tools_widget.py
6. app/ui/flow_visualizer.py
7. app/ui/widgets.py (был закомментирован, добавлен новый импорт)

## Добавленные маппинги иконок

В файле icon_adapter.py были добавлены отсутствующие маппинги для иконок:
- back → chevron-left
- forward → chevron-right
- stop → x-circle
- analyze → search-check
- view → eye
- clear → trash-2

## Примечания

Модуль `icon_adapter` обеспечивает обратную совместимость со старым API через функцию `get_icon` и класс `IconAdapter`, который адаптирует новый `LucideIconManager` для использования со старым кодом.

В файле icon_adapter.py имеется функция-хелпер для обратной совместимости:

```python
def get_icon(icon_name, color=None, size=24):
    """Функция для получения иконки (для обратной совместимости)."""
    return IconAdapter.instance().get_icon(icon_name, color, size)
```

Эта миграция не влияет на функциональность приложения, но исправляет ошибки импорта и предупреждения, которые возникали при запуске.