# GopiAI MCP и SQLite интеграция

Данный документ описывает настройку и использование Modular Coding Platform (MCP) и SQLite интеграции для GopiAI.

## Содержание

- [Установка и настройка](#установка-и-настройка)
- [Структура конфигурации](#структура-конфигурации)
- [SQLite интеграция](#sqlite-интеграция)
- [Serena инструменты](#serena-инструменты)
- [Исправление проблем с MCP серверами](#исправление-проблем-с-mcp-серверами)

## Установка и настройка

### Windows

1. Убедитесь, что у вас установлены Python 3 и Node.js
2. Запустите скрипт `setup_mcp.bat`:
   ```cmd
   setup_mcp.bat
   ```
3. Скрипт автоматически:
   - Установит необходимые NPM пакеты для MCP серверов
   - Создаст структуру директорий для базы данных
   - Инициализирует базу данных SQLite с нужными таблицами

### Linux/macOS

1. Убедитесь, что у вас установлены Python 3 и Node.js
2. Сделайте скрипт исполняемым и запустите его:
   ```bash
   chmod +x setup_mcp.sh
   ./setup_mcp.sh
   ```

### Ручная установка

1. Установите необходимые NPM пакеты:
   ```bash
   npm install -g @modelcontextprotocol/server-sequential-thinking @oevortex/ddg_search @modelcontextprotocol/server-memory @modelcontextprotocol/server-fetch @modelcontextprotocol/server-github @modelcontextprotocol/server-time @modelcontextprotocol/server-everart @modelcontextprotocol/server-markdown2doc
   ```
2. Инициализируйте базу данных:
   ```bash
   python init_database.py
   ```

## Структура конфигурации

Конфигурация MCP хранится в файле `mcp.json` в корне проекта. Структура файла:

```json
{
  "version": "0.1.0",
  "name": "gopi-ai-mcp",
  "description": "GopiAI MCP Configuration",
  "tools": [
    {
      "name": "sqlite",
      "description": "SQLite database tools for GopiAI",
      "path": "app/mcp/sqlite_tools.py",
      "tools": [
        "init_database",
        "execute_query",
        "select_query",
        "insert_data",
        "update_data",
        "delete_data",
        "create_table"
      ]
    },
    {
      "name": "serena",
      "description": "Serena integration tools for GopiAI",
      "path": "app/mcp/serena_tools.py"
    }
  ],
  "servers": [
    {
      "name": "sequential-thinking",
      "package": "@modelcontextprotocol/server-sequential-thinking",
      "description": "Sequential thinking server for step-by-step reasoning"
    },
    {
      "name": "ddg_search",
      "package": "@oevortex/ddg_search",
      "description": "DuckDuckGo search integration"
    },
    {
      "name": "memory",
      "package": "@modelcontextprotocol/server-memory",
      "description": "Memory server for storing and retrieving information"
    },
    {
      "name": "fetch",
      "package": "@modelcontextprotocol/server-fetch",
      "description": "Fetch server for HTTP requests"
    },
    {
      "name": "github",
      "package": "@modelcontextprotocol/server-github",
      "description": "GitHub integration server"
    },
    {
      "name": "time",
      "package": "@modelcontextprotocol/server-time",
      "description": "Time server for date/time operations"
    },
    {
      "name": "everart",
      "package": "@modelcontextprotocol/server-everart",
      "description": "Everart server for AI art generation"
    },
    {
      "name": "markdown2doc",
      "package": "@modelcontextprotocol/server-markdown2doc",
      "description": "Markdown to document conversion server"
    }
  ],
  "database": {
    "path": "data/gopi_ai.db",
    "init_tables": [
      {
        "name": "conversations",
        "columns": [
          "id INTEGER PRIMARY KEY AUTOINCREMENT",
          "title TEXT NOT NULL",
          "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
          "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
      },
      {
        "name": "messages",
        "columns": [
          "id INTEGER PRIMARY KEY AUTOINCREMENT",
          "conversation_id INTEGER NOT NULL",
          "role TEXT NOT NULL",
          "content TEXT NOT NULL",
          "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
          "FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE"
        ]
      },
      {
        "name": "settings",
        "columns": [
          "id INTEGER PRIMARY KEY AUTOINCREMENT",
          "key TEXT UNIQUE NOT NULL",
          "value TEXT NOT NULL",
          "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
      }
    ]
  }
}
```

## SQLite интеграция

SQLite интеграция предоставляет инструменты для работы с базой данных в GopiAI. Доступные функции:

- `init_database` - инициализация базы данных
- `execute_query` - выполнение произвольного SQL запроса
- `select_query` - выполнение SELECT запроса
- `insert_data` - вставка данных в таблицу
- `update_data` - обновление данных в таблице
- `delete_data` - удаление данных из таблицы
- `create_table` - создание новой таблицы

### Примеры использования

```python
# Инициализация базы данных
await init_database()

# Выполнение SELECT запроса
result = await select_query("SELECT * FROM conversations LIMIT 10")

# Вставка данных
data = json.dumps({"title": "Новый разговор"})
result = await insert_data("conversations", data)

# Обновление данных
data = json.dumps({"title": "Обновленный разговор"})
condition = "id = ?"
params = json.dumps([1])
result = await update_data("conversations", data, condition, params)

# Удаление данных
condition = "id = ?"
params = json.dumps([1])
result = await delete_data("conversations", condition, params)
```

## Serena инструменты

Serena инструменты предоставляют функциональность для работы с файлами и кодом в GopiAI. Доступные функции:

- `restart_language_server` - перезапуск языкового сервера
- `read_file` - чтение файла
- `create_text_file` - создание/перезапись файла
- `list_dir` - просмотр содержимого директории
- `get_symbols_overview` - получение обзора символов в файлах

### Примеры использования

```python
# Чтение файла
result = await read_file("main.py")

# Создание файла
await create_text_file("new_file.py", "print('Hello, world!')")

# Просмотр директории
result = await list_dir("app", recursive=True)

# Получение обзора символов
symbols = await get_symbols_overview("app/agent")
```

## Исправление проблем с MCP серверами

Если у вас возникают проблемы с MCP серверами в Cursor (красные ошибки "Failed to create client"), выполните следующие шаги:

### Быстрое исправление

1. Запустите скрипт `fix_mcp_servers.bat` (Windows) или `fix_mcp_servers.sh` (Linux/macOS):
   ```
   fix_mcp_servers.bat
   ```
   или
   ```bash
   ./fix_mcp_servers.sh
   ```

2. Этот скрипт выполнит:
   - Удаление существующих MCP серверов
   - Очистку кэша NPM
   - Пошаговую установку всех необходимых пакетов
   - Проверку установки

3. После завершения работы скрипта перезапустите Cursor IDE

### Ручное исправление

Если скрипт не помог, попробуйте выполнить следующие шаги вручную:

1. Удалите существующие пакеты:
   ```
   npm uninstall -g @modelcontextprotocol/server-sequential-thinking @oevortex/ddg_search @modelcontextprotocol/server-memory @modelcontextprotocol/server-fetch @modelcontextprotocol/server-github @modelcontextprotocol/server-time @modelcontextprotocol/server-everart @modelcontextprotocol/server-markdown2doc
   ```

2. Очистите кэш NPM:
   ```
   npm cache clean --force
   ```

3. Установите пакеты по одному:
   ```
   npm install -g @modelcontextprotocol/server-sequential-thinking
   npm install -g @oevortex/ddg_search
   npm install -g @modelcontextprotocol/server-memory
   npm install -g @modelcontextprotocol/server-fetch
   npm install -g @modelcontextprotocol/server-github
   npm install -g @modelcontextprotocol/server-time
   npm install -g @modelcontextprotocol/server-everart
   npm install -g @modelcontextprotocol/server-markdown2doc
   ```

4. Проверьте, что пакеты установлены:
   ```
   npm list -g --depth=0
   ```

5. Перезапустите Cursor IDE

### Проверка доступности пакетов

Если указанные пакеты недоступны в NPM, проверьте их наличие:
```
npm view @modelcontextprotocol/server-fetch
npm view @modelcontextprotocol/server-github
npm view @modelcontextprotocol/server-time
npm view @modelcontextprotocol/server-everart
npm view @modelcontextprotocol/server-markdown2doc
```

Если пакеты действительно недоступны, это может указывать на то, что Cursor использует внутренние или устаревшие пакеты MCP, которые не опубликованы в публичном NPM реестре. В этом случае обратитесь к документации Cursor или к разработчикам для получения правильных версий пакетов.
