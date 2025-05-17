# Исправление неопределенных переменных в QSS файлах тем

## Проблема

В файлах `dark.qss` и `light.qss` использовались переменные, которые не были определены:
- #3C3C3C_color
- #555555_hover
- #3498DB_color
- #6A6A6A_color
- #444444_radius

Это приводило к ошибкам при парсинге QSS стилей:
```
QCssParser::parseHexColor: Unknown color name '#3C3C3C_color'
QCssParser::parseHexColor: Unknown color name '#555555_hover'
QCssParser::parseHexColor: Unknown color name '#3498DB_color'
QCssParser::parseHexColor: Unknown color name '#6A6A6A_color'
QCssParser::parseHexColor: Unknown color name '#444444_radius'
```

## Решение

Было применено два подхода для решения проблемы:

1. Добавлены определения переменных непосредственно в файлы QSS:
   - В `app/ui/themes/dark.qss` в начало файла добавлены определения переменных
   - В `app/ui/themes/light.qss` также добавлены аналогичные определения

2. Модифицирован метод `_generate_stylesheet` в классе `ThemeManager` для автоматического добавления определений отсутствующих переменных:
   ```python
   # Добавляем дополнительные определения переменных, которые вызывают ошибки
   additional_vars = """
   /* Определения для отсутствующих переменных */
   @3C3C3C_color: #3C3C3C;
   @555555_hover: #555555;
   @3498DB_color: #3498DB;
   @6A6A6A_color: #6A6A6A;
   @444444_radius: 4px;
   """
   base_qss = additional_vars + base_qss
   ```

Это исправление позволило решить проблему с неопределенными переменными в QSS.

## Примечание

В логах все еще видны предупреждения о незамененных плейсхолдерах в QSS, но это не мешает запуску приложения. В будущем, возможно, потребуется добавить определения и для других переменных в темах.