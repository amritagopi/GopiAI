# Исправление обработчиков видимости доков (visibilityChanged)

В файле `app/ui/docks.py` были найдены ошибки в обработчиках событий для сигналов `visibilityChanged`, что приводило к ошибкам:

```
TypeError: on_dock_visibility_changed() missing 1 required positional argument: 'visible'
```

## Проблема
Функция `on_dock_visibility_changed` в файле `app/logic/event_handlers.py` ожидает три параметра:
```python
def on_dock_visibility_changed(main_window, dock_name, visible):
```

Но в коде подключения сигналов использовались лямбда-функции, которые передавали только два параметра:
```python
main_window.chat_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, visible))
```

## Решение
Исправлены лямбда-функции в `docks.py`, теперь они правильно передают имя дока:

1. Для chat_dock:
```python
main_window.chat_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "chat", visible))
```

2. Для terminal_dock:
```python
main_window.terminal_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "terminal", visible))
```

3. Для browser_dock:
```python
main_window.browser_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, "browser", visible))
```

Это исправление устранило ошибки при запуске приложения, хотя в консоли все еще есть предупреждения, связанные с незамененными плейсхолдерами в QSS стилях и отсутствующими методами, которые должны быть переопределены в миксинах.