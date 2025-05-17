# Решение проблемы с дублирующимися заголовками в чат-интерфейсе

## Проблема
В интерфейсе чата наблюдалось дублирование заголовков - верхний заголовок отображался дважды:
1. Заголовок от QDockWidget (стандартная панель dock-виджета)
2. Кастомный заголовок внутри ChatWidget (создаваемый в классе ChatWidget)

## Решение
Для устранения проблемы потребовался комплексный подход, включающий изменения в трёх компонентах:

### 1. Полное скрытие заголовка QDockWidget
```python
# app/ui/docks.py
# Усиленный метод для скрытия заголовка dock-виджета
empty_title_widget = QWidget()
empty_title_widget.setFixedHeight(0)
empty_title_widget.setMaximumHeight(0)
empty_title_widget.setVisible(False)
main_window.chat_dock.setTitleBarWidget(empty_title_widget)

# Применение CSS для дополнительного скрытия
main_window.chat_dock.setStyleSheet("""
    QDockWidget::title {
        margin: 0px;
        padding: 0px;
        visible: false;
        height: 0px;
        min-height: 0px;
        max-height: 0px;
    }
    QDockWidget {
        border-top: none;
    }
""")

# Дополнительное свойство для контроля высоты
main_window.chat_dock.setProperty("headerHeight", 0)
```

### 2. Удаление кастомного заголовка в ChatWidget
```python
# app/ui/widgets.py
# Скрытие заголовка внутри ChatWidget
header = QWidget()
header.setObjectName("chatHeader")
header.setFixedHeight(0)
header.setVisible(False)
header_layout = QHBoxLayout(header)
header_layout.setContentsMargins(0, 0, 0, 0)
```

### 3. Изменение стилей в QSS-файле темы
```css
/* app/ui/themes/dark.qss */
ChatWidget QWidget#chatHeader {
    background-color: transparent;
    border-bottom: none;
    padding: 0;
    margin: 0;
    height: 0px;
    min-height: 0px;
    max-height: 0px;
    visibility: hidden;
}

ChatWidget QLabel#chatTitle {
    color: transparent;
    font-size: 0px;
    margin: 0;
    padding: 0;
    height: 0px;
    visibility: hidden;
}
```

## Полезные выводы

1. **Многоуровневый подход**
   - При работе с Qt необходимо учитывать, что стили могут применяться на нескольких уровнях
   - Для сложных стилистических изменений следует вносить изменения на всех уровнях

2. **Борьба с кэшированием**
   - Необходимо удалять кэшированные Python-файлы (`__pycache__`)
   - Скомпилированные QSS-файлы также должны перегенерироваться

3. **Свойства видимости**
   - Для полного скрытия элемента лучше использовать комбинацию свойств:
     - Установка нулевых размеров
     - Явное отключение видимости
     - Установка прозрачности или настройка спрятанных стилей

4. **Расположение в иерархии виджетов**
   - Даже "скрытые" элементы занимают место в иерархии виджетов
   - Важно не только скрыть элемент, но и уменьшить его размеры до минимума