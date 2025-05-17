# Использование системы иконок в UI GopiAI

## Общие принципы
- Для всех кнопок, меню, вкладок и других элементов интерфейса используются иконки только через функцию `get_icon(name)` из `app/ui/icon_adapter.py`.
- Прямое указание путей к SVG/PNG-файлам запрещено — только логические имена иконок.
- При добавлении новых функций или инструментов рекомендуется использовать существующие иконки из библиотеки Lucide или добавлять новые.

## Примеры
```python
from app.ui.icon_adapter import get_icon
button = QPushButton(get_icon("play"), "Запустить")
menu_action = QAction(get_icon("settings"), "Настройки", self)
```

## Настройка цвета и размера иконок
Новая система иконок поддерживает гибкую настройку внешнего вида:

```python
# С использованием функции-адаптера
icon = get_icon("settings", color="#FF5500", size=QSize(32, 32))

# С прямым использованием LucideIconManager
from app.ui.lucide_icon_manager import LucideIconManager
icon_manager = LucideIconManager.instance()
icon = icon_manager.get_icon("settings", color="#FF5500", size=QSize(32, 32))
```

## Рефакторинг существующего кода
- Все прямые пути к иконкам (например, через QIcon("assets/icons/xxx.svg")) должны быть заменены на `get_icon("xxx")`.
- Если нужна иконка, которой нет в библиотеке Lucide, можно добавить её в папку `assets/icons/lucide/`.

## Проверка
- Для просмотра доступных иконок используйте утилиту `test_lucide_icons.py`.
- В ней можно увидеть все доступные иконки, а также протестировать изменение цвета и размера.

---

Документ обновлён в рамках задачи по модернизации системы иконок на основе Lucide.
