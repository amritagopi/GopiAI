# Кастомный заголовок окна

В проекте реализован кастомный заголовок окна с помощью класса `MainWindowTitleBar`, который находится в файле `app/ui/main_window_title_bar.py`.

## Основные возможности

1. Отображение логотипа GopiAI (голубая спираль)
2. Кнопки управления окном (свернуть, развернуть/восстановить, закрыть)
3. Заголовок окна с названием приложения
4. Поддержка перетаскивания окна
5. Двойной клик для максимизации/восстановления
6. Адаптация к текущей теме (светлой или темной)

## Интеграция с MainWindow

`MainWindowTitleBar` встраивается в `MainWindow` через создание особой структуры макетов:

```python
# Создаем кастомный заголовок окна
self.title_bar = MainWindowTitleBar(tr("app.title", "GopiAI"), self.icon_manager, self)

# Устанавливаем кастомный заголовок в верхнюю часть окна
main_layout = QVBoxLayout()
main_layout.setContentsMargins(0, 0, 0, 0)
main_layout.setSpacing(0)
main_layout.addWidget(self.title_bar)

# Создаем центральный виджет для обертки основного содержимого
self.central_container = QWidget()
self.central_container.setObjectName("centralContainer")
main_layout.addWidget(self.central_container)

# Создаем отдельный контейнер для фактического содержимого
self.content_widget = QWidget(self.central_container)
self.content_layout = QVBoxLayout(self.content_widget)
self.content_layout.setContentsMargins(0, 0, 0, 0)
self.content_layout.setSpacing(0)

# Устанавливаем макет для центрального контейнера
content_container_layout = QVBoxLayout(self.central_container)
content_container_layout.setContentsMargins(0, 0, 0, 0)
content_container_layout.setSpacing(0)
content_container_layout.addWidget(self.content_widget)

# Устанавливаем главный контейнер как центральный виджет
central_widget = QWidget()
central_widget.setLayout(main_layout)
self.setCentralWidget(central_widget)
```

## Логотип приложения

Логотип добавлен в `SVG_ICON_DATA` в файле `app/ui/icon_manager.py` как "gopi_logo".

## Стилизация

Стили для `MainWindowTitleBar` добавлены в файлы тем `app/ui/themes/dark.qss` и `app/ui/themes/light.qss`.

## Обновление для смены темы

При изменении темы вызывается метод `update_theme()` у `MainWindowTitleBar`, который обновляет стили и иконки в соответствии с новой темой.