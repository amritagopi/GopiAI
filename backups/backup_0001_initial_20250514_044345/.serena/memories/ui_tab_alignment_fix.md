# Исправление выравнивания вкладок по левому краю

В файле `app/ui/central_widget.py` был исправлен стиль для выравнивания вкладок по левому краю. 

## Исправление

Изменена строка:
```python
main_window.central_tabs.setStyleSheet("QTabBar::tab { text-align: left; } QTabBar { alignment: left; }")
```

на:
```python
main_window.central_tabs.setStyleSheet("QTabWidget::tab-bar { alignment: left; } QTabBar::tab { text-align: left; }")
```

## Объяснение
Ключевое изменение: используется селектор `QTabWidget::tab-bar` вместо просто `QTabBar`, так как именно этот селектор отвечает за выравнивание контейнера вкладок. Селектор `QTabBar::tab` отвечает за выравнивание текста внутри каждой вкладки, но не за выравнивание самих вкладок в контейнере.

## Дополнительные наблюдения
В файле `theme_utils.py` есть шаблон стиля, который использует переменную `@tab_bar_alignment`:
```css
QTabWidget::tab-bar {
    alignment: @tab_bar_alignment;
}
```

Эта переменная не определена в JSON-файлах тем, и если в будущем потребуется более гибкое управление выравниванием вкладок через темы, можно добавить этот параметр в конфигурацию тем.