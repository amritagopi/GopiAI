# Модуль FileSystemAccess для GopiAI

## Обзор

FileSystemAccess — это модуль для безопасного доступа к файловой системе в рамках Reasoning Agent. Модуль обеспечивает контролируемый доступ к файлам и директориям с проверкой безопасности операций и ограничением потенциально опасных действий.

## Принцип работы

Модуль работает по следующим принципам:

1. **Проверка безопасности путей** — анализ путей к файлам и директориям на наличие потенциально опасных паттернов
2. **Проверка безопасности операций** — анализ операций с файлами на потенциальные риски
3. **Контроль доступа к файлам** — ограничение доступа только к разрешенным директориям
4. **Извлечение путей из чата** — распознавание и нормализация упоминаемых в чате путей к файлам
5. **Логирование операций** — запись всех выполненных файловых операций и их результатов

## Основные возможности

### Работа с файлами

```python
# Чтение файла
result = await file_system.read_file("path/to/file.txt")
if result["success"]:
    content = result["content"]

# Запись в файл
result = await file_system.write_file("path/to/file.txt", "Содержимое файла")
if result["success"]:
    print(f"Файл успешно записан, размер: {result['size']} байт")

# Удаление файла
result = await file_system.delete_file("path/to/file.txt")
```

### Работа с директориями

```python
# Получение текущей директории
current_dir = file_system.get_current_directory()

# Установка текущей директории
file_system.set_current_directory("path/to/directory")

# Получение списка файлов и директорий
result = await file_system.list_directory("path/to/directory", recursive=True)
if result["success"]:
    for directory in result["directories"]:
        print(f"Директория: {directory}")
    for file in result["files"]:
        print(f"Файл: {file}")
```

### Получение информации о файлах

```python
result = await file_system.get_file_info("path/to/file.txt")
if result["success"]:
    print(f"Имя: {result['name']}")
    print(f"Размер: {result['size']} байт")
    print(f"Дата изменения: {result['modified']}")
    print(f"Расширение: {result['extension']}")
```

### Извлечение путей из чата

```python
# Из сообщения "Пожалуйста, прочитай файл workspace/data.txt"
path = file_system.parse_chat_path("Пожалуйста, прочитай файл workspace/data.txt")
if path:
    result = await file_system.read_file(path)
```

### Получение истории операций

```python
history = file_system.get_operation_history()
for operation in history:
    print(f"Операция: {operation['operation']}")
    print(f"Путь: {operation['path']}")
    print(f"Успех: {operation['success']}")
```

## Меры безопасности

### Разрешенные директории

Модуль ограничивает доступ только к разрешенным директориям:

```python
ALLOWED_DIRS = [
    ".", "./app", "./tests", "./examples", "./workspace",
    "./data", "./docs", "./scripts", "./logs"
]
```

### Блокировка опасных расширений

Модуль блокирует доступ к файлам с потенциально опасными расширениями:

```python
UNSAFE_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".msi", ".dll",
    ".com", ".scr", ".pif", ".application", ".gadget", ".msc", ".jar"
}
```

### Блокировка опасных паттернов в путях

Модуль блокирует пути, содержащие потенциально опасные паттерны:

```python
UNSAFE_PATH_PATTERNS = [
    r"\.\.\/", r"\.\.\\"  # Пути с выходом на уровень выше
]
```

## Интеграция с ReasoningAgent

Модуль FileSystemAccess интегрирован в ReasoningAgent и используется для всех файловых операций:

```python
# Внутри ReasoningAgent
if name == "file_read" and self.file_system:
    file_path = kwargs.get("path", "")
    mode = kwargs.get("mode", "text")
    encoding = kwargs.get("encoding", "utf-8")

    # Выполняем действие через наш безопасный FileSystemAccess
    result = await self.file_system.read_file(file_path, mode, encoding)

    # Формируем ответ в формате ToolResult
    return {
        "output": result.get("content", ""),
        "error": result.get("error", ""),
    }
```

## Результаты выполнения операций

Функции модуля возвращают словари со следующими общими полями:

```python
{
    "success": bool,  # Успешность выполнения
    "error": str,     # Ошибка (если есть)
    "path": str       # Путь к файлу или директории
}
```

Дополнительные поля для операций чтения:

```python
{
    "content": str,   # Содержимое файла
    "size": int,      # Размер файла в байтах
    "mode": str,      # Режим чтения ("text" или "binary")
    "encoding": str   # Кодировка (для текстового режима)
}
```

## Возможные ошибки

1. **AccessDenied** — доступ к файлу или директории запрещен
2. **FileNotFound** — файл не найден
3. **DirectoryNotFound** — директория не найдена
4. **UnsafePath** — небезопасный путь
5. **UnsafeOperation** — небезопасная операция
6. **FileTooLarge** — файл слишком большой
7. **InvalidInput** — неверные входные данные

## Пример использования

```python
from app.agent.file_system_access import FileSystemAccess

# Создание экземпляра
file_system = FileSystemAccess(
    root_dir="/path/to/project",
    safe_mode=True,
    max_file_size=10 * 1024 * 1024,  # 10 MB
    chat_paths_enabled=True
)

# Установка рабочей директории
file_system.set_current_directory("workspace")

# Чтение файла
result = await file_system.read_file("data.txt")
if result["success"]:
    print(f"Содержимое файла: {result['content']}")
else:
    print(f"Ошибка: {result['error']}")

# Запись в файл
await file_system.write_file("output.txt", "Результаты анализа")

# Получение списка файлов в директории
dir_result = await file_system.list_directory(".", recursive=True)
if dir_result["success"]:
    print(f"Найдено файлов: {len(dir_result['files'])}")
    for file in dir_result['files']:
        print(f"- {file}")

# Извлечение пути из сообщения пользователя
path = file_system.parse_chat_path("Пожалуйста, посмотри файл logs/app.log")
if path:
    log_result = await file_system.read_file(path)
    if log_result["success"]:
        print(f"Последние 10 строк лога: {log_result['content'].splitlines()[-10:]}")
```

## Тестирование

Для тестирования модуля используйте скрипт `tests/test_file_system_access.py`:

```bash
python tests/test_file_system_access.py
```

Возможные параметры тестирования:

- `--test directory` — тестирование операций с директориями
- `--test file` — тестирование операций с файлами
- `--test unsafe` — тестирование отклонения небезопасных путей
- `--test chat` — тестирование извлечения путей из чата
- `--test history` — тестирование истории операций
- `--test all` — запуск всех тестов (по умолчанию)
- `--safe-mode` — включение/выключение режима безопасности
- `--chat-paths` — включение/выключение поддержки путей из чата
