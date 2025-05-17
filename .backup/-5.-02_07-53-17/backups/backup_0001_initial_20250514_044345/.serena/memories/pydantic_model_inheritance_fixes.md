# Исправления наследования в pydantic моделях

В рамках исправления конфликтов при наследовании в pydantic моделях были внесены следующие изменения:

## Переименованы поля name в классах BaseTool для избежания конфликтов:

1. `Terminate`: поле `name` → `terminate_name`
2. `WebSearch`: поле `name` → `web_search_name`
3. `BrowserUseTool`: поле `name` → `browser_use_name`
4. `CodeControlTool`: поле `name` → `code_control_name`
5. `CodeEditTool`: поле `name` → `code_edit_name`
6. `CodeAnalyzeTool`: поле `name` → `code_analyze_name`
7. `CodeRunTool`: поле `name` → `code_run_name`

## Переименованы поля в классах ToolCallAgent и его наследниках:

1. `ToolCallAgent`: поле `available_tools` → `tools_collection`
2. `BrowserAgent`: поле `tools` → `browser_tools`
3. `SWEAgent`: поле `available_tools` → `swe_tools`
4. `Manus`: поле `available_tools` → `manus_tools`
5. `CodingAgent`: поле `tools` → `coding_tools`
6. `ReactAgent`: поля `name` и `description` → `agent_name` и `agent_description`

## Обновлены методы для работы с новыми именами полей:

1. Обновлен метод `to_param` в `BaseTool` для поддержки специальных имен полей
2. Обновлен метод `_is_special_tool` в `ToolCallAgent` для корректного сравнения имен
3. Модифицирован класс `ToolCollection` для работы с новыми именами полей

## Обновлены ссылки на поля во всех классах, где они использовались.

Эти изменения устраняют конфликты наследования между родительскими и дочерними классами, где дочерние классы переопределяли атрибуты родительских классов с новыми аннотациями типов.