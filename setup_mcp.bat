@echo off
echo Setting up MCP servers for GopiAI...

REM Проверка наличия Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден! Пожалуйста, установите Python и добавьте его в PATH.
    exit /b 1
)

REM Проверка наличия Node.js и NPM
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo NPM не найден! Пожалуйста, установите Node.js и NPM.
    exit /b 1
)

REM Установка MCP серверов
echo Установка MCP серверов из NPM...
python setup_mcp_servers.py
if %errorlevel% neq 0 (
    echo Ошибка при установке MCP серверов!
    exit /b 1
)

REM Инициализация базы данных SQLite
echo Инициализация базы данных SQLite...
python init_database.py
if %errorlevel% neq 0 (
    echo Ошибка при инициализации базы данных!
    exit /b 1
)

echo Настройка MCP серверов успешно завершена!
echo.
echo Доступные серверы:
echo - sequential-thinking: для пошагового мышления
echo - ddg_search: для поиска в интернете
echo - memory: для хранения данных

echo.
echo Для запуска MCP сервера выполните: python run_mcp_server.py

pause
