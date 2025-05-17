# Исправление отображения браузера в интерфейсе GopiAI

## Описание проблемы
Браузерный компонент не отображался в интерфейсе приложения. При этом функционал был настроен и работал, но не был правильно подключен к интерфейсу.

## Причины проблемы
В функции `create_docks` в файле `app/ui/docks.py` отсутствовал код для создания и настройки `browser_dock`. При этом в коде `MainWindow` были методы, которые предполагали наличие `browser_dock` и его атрибута `web_view`.

## Решение
1. Добавлен код создания и настройки `browser_dock` в функцию `create_docks` в файле `app/ui/docks.py`.
2. Обеспечено, чтобы `web_view` был доступен как атрибут `browser_dock`, для совместимости с существующими методами в `MainWindow`.

## Ключевые изменения

```python
# Браузер
logger.info("Creating browser dock")
main_window.browser_dock = QDockWidget(tr("dock.browser", "Браузер"), main_window)
main_window.browser_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
main_window.browser_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
main_window.browser_dock.setMinimumWidth(250)
main_window.browser_dock.setMinimumHeight(200)
main_window.browser_dock.setObjectName("BrowserDock")
main_window.browser_dock.visibilityChanged.connect(lambda visible: on_dock_visibility_changed(main_window, visible))

# Создаем веб-браузер и устанавливаем его в док
# ВАЖНО: Добавляем web_view как атрибут browser_dock для совместимости
# с существующими методами в MainWindow (_toggle_browser и др.)
web_view = get_browser_widget(main_window)
main_window.browser_dock.web_view = web_view  # Важно: делаем web_view атрибутом browser_dock
main_window.browser_dock.setWidget(web_view)

# Добавляем док в правую область, но не показываем его сразу
main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.browser_dock)
apply_custom_title_bar(main_window.browser_dock, main_window.icon_manager, is_docked_permanent=False)
main_window.browser_dock.hide()
logger.info("Browser dock created successfully")
```

## Взаимодействие с интерфейсом
Браузер теперь можно открыть через меню "Вид" > "Браузер" или с помощью действия "Открыть URL".

## Методы, использующие browser_dock
Основные методы, работающие с browser_dock:
1. `_toggle_browser` - переключает видимость браузера
2. `_open_url_in_browser` - открывает заданный URL в браузере
3. `_on_documentation` - открывает документацию в браузере

## Замечания
1. По умолчанию браузер скрыт и отображается только при явном вызове.
2. Браузер размещается в правой части интерфейса, но может быть перемещен в нижнюю часть.
3. Важно, чтобы `web_view` был доступен как атрибут `browser_dock`, иначе методы MainWindow не смогут правильно работать.