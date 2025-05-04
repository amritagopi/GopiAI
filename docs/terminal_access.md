# Модуль TerminalAccess для GopiAI

## Обзор

TerminalAccess — это модуль для безопасного выполнения команд терминала в рамках Reasoning Agent. Модуль обеспечивает контролируемый доступ к терминалу с проверкой безопасности команд и ограничением доступа к директориям.

## Принцип работы

Модуль работает по следующим принципам:

1. **Проверка безопасности команд** — анализ команд на наличие потенциально опасных операций
2. **Контроль доступа к директориям** — ограничение работы только разрешенными директориями
3. **Логирование действий** — запись всех выполненных команд и их результатов
4. **Таймауты выполнения** — предотвращение зависания долгих операций
5. **Обработка ошибок** — корректное сообщение о любых проблемах выполнения

## Основные возможности

### Безопасное выполнение команд

```python
result = await terminal_access.execute_command(
    command="echo Hello World",
    working_dir=None,  # Используется текущая директория
    timeout=30.0  # Таймаут в секундах
)
```

### Управление рабочими директориями

```python
# Установка рабочей директории
success = terminal_access.set_current_directory("./app")

# Получение текущей директории
current_dir = terminal_access.get_current_directory()

# Выполнение команды в указанной директории
result = await terminal_access.execute_command(
    command="dir",
    working_dir="./tests"
)
```

### Получение истории команд

```python
history = terminal_access.get_command_history()
for entry in history:
    print(f"Command: {entry['command']}")
    print(f"Success: {entry.get('success', False)}")
    print(f"Timestamp: {entry['timestamp']}")
```

## Меры безопасности

### Список опасных команд

Модуль содержит встроенный список потенциально опасных команд и паттернов:

```python
UNSAFE_COMMANDS = [
    "rm -rf", "rmdir /s", "del /s", "format",
    "dd", ">", "DROP", "DELETE FROM", "sudo",
    "chmod -R", "chown -R", ":(){ :|:& };:",  # fork bomb
]
```

### Разрешенные директории

По умолчанию, разрешены следующие директории (относительно корня проекта):

```python
ALLOWED_DIRS = [
    ".", "./app", "./tests", "./examples", "./workspace",
    "./data", "./docs", "./scripts", "./logs"
]
```

### Дополнительные проверки

- Запрет на переход выше корневой директории (`cd ..`)
- Запрет на прямое выполнение скриптов (кроме python)
- Контроль вывода для предотвращения перегрузки памяти

## Интеграция с ReasoningAgent

Модуль TerminalAccess интегрирован в ReasoningAgent и автоматически используется для перехвата вызовов `run_terminal_cmd`:

```python
# Внутри ReasoningAgent
if name == "run_terminal_cmd" and self.terminal_access:
    command = kwargs.get("command", "")
    is_background = kwargs.get("is_background", False)

    result = await self.terminal_access.execute_command(
        command=command,
        working_dir=None,
        timeout=None if is_background else 30.0,
    )

    return {
        "exit_code": result.get("return_code", 1),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "success": result.get("success", False)
    }
```

## Результаты выполнения команд

Функция `execute_command` возвращает словарь со следующими полями:

```python
{
    "success": bool,  # Успешность выполнения
    "stdout": str,    # Вывод команды (stdout)
    "stderr": str,    # Ошибки команды (stderr)
    "return_code": int,  # Код возврата
    "command": str,      # Выполненная команда
    "working_dir": str,  # Рабочая директория
    "error": str         # Тип ошибки (если есть)
}
```

## Возможные ошибки

1. **AccessDenied** — попытка доступа к неразрешенной директории
2. **UnsafeCommand** — попытка выполнения небезопасной команды
3. **Timeout** — превышение времени выполнения команды
4. **ModuleNotInitialized** — модуль не инициализирован
5. **PlanNotApproved** — план не был одобрен для выполнения команд

## Пример использования

```python
from app.agent.terminal_access import TerminalAccess

# Создание экземпляра
terminal = TerminalAccess(
    root_dir="/path/to/project",
    max_output_lines=500,
    safe_mode=True
)

# Выполнение команды
result = await terminal.execute_command("python --version")
if result["success"]:
    print(f"Python version: {result['stdout']}")
else:
    print(f"Error: {result['stderr']}")

# Изменение директории
terminal.set_current_directory("./app")

# Выполнение команды в новой директории
result = await terminal.execute_command("dir" if sys.platform == "win32" else "ls -la")
print(result["stdout"])
```

## Тестирование

Для тестирования модуля используйте скрипт `tests/test_terminal_access.py`:

```bash
python tests/test_terminal_access.py
```

Возможные параметры тестирования:

- `--test basic` — тестирование базовых команд
- `--test unsafe` — тестирование отклонения опасных команд
- `--test directory` — тестирование навигации по директориям
- `--test timeout` — тестирование таймаутов команд
- `--test all` — запуск всех тестов (по умолчанию)
- `--safe-mode` — включение/выключение режима безопасности
