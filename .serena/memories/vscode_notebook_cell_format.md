# VSCode Notebook Cell Format

## XML Structure
Each cell in VSCode notebooks должна быть оформлена в специальном XML формате:

```xml
<VSCode.Cell language="markdown|python|..." id="uniqueId">
content goes here
</VSCode.Cell>
```

## Правила форматирования:
1. Каждая ячейка должна быть обернута в тег `<VSCode.Cell>`
2. Обязательные атрибуты:
   - `language`: тип содержимого (markdown, python и т.д.)
   - `id`: уникальный идентификатор (только для существующих ячеек)
3. Новые ячейки не требуют атрибута `id`
4. Содержимое внутри ячеек НЕ нужно XML-кодировать
5. Структура должна быть валидным XML

## Пример использования:
```xml
<VSCode.Cell language="markdown">
# Заголовок
Описание в формате Markdown
</VSCode.Cell>

<VSCode.Cell language="python">
import pandas as pd
df = pd.DataFrame()
</VSCode.Cell>
```

## Нумерация
При обращении к ячейкам используется порядковый номер (начиная с 1), а не их id.