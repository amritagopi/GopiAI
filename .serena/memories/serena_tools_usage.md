# Использование инструментов Serena

## Настройка и запуск
- Serena MCP-сервер запускается командой `uv run serena-mcp-server --transport sse --port 9121`
- Для работы с инструментами Serena необходимо активировать проект: `mcp_serena_activate_project`
- После активации проекта доступны все инструменты Serena

## Основные инструменты
- `mcp_serena_list_memories` - получение списка файлов памяти
- `mcp_serena_read_memory` - чтение содержимого файла памяти
- `mcp_serena_write_memory` - создание или обновление файла памяти
- `mcp_serena_get_symbols_overview` - получение обзора символов в файле или директории
- `mcp_serena_find_symbol` - поиск символа по имени
- `mcp_serena_read_file` - чтение содержимого файла

## Редактирование кода
- `mcp_serena_replace_symbol_body` - замена тела символа
- `mcp_serena_insert_after_symbol` - вставка кода после символа
- `mcp_serena_insert_before_symbol` - вставка кода перед символом
- `mcp_serena_replace_regex` - замена текста по регулярному выражению

## Мыслительные инструменты
- `mcp_serena_think_about_collected_information` - анализ собранной информации
- `mcp_serena_think_about_task_adherence` - проверка соответствия задаче
- `mcp_serena_think_about_whether_you_are_done` - проверка завершенности задачи

## Примечание
Инструменты Serena значительно упрощают работу с кодом, позволяя анализировать и редактировать код на уровне символов (функций, классов, методов) вместо работы с текстом файлов напрямую.