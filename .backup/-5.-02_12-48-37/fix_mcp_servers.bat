@echo off
chcp 65001
echo Исправление проблем с MCP серверами для GopiAI...

REM Проверка наличия NPM
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo NPM не найден! Пожалуйста, установите Node.js и NPM.
    exit /b 1
)

REM Удаление глобальных пакетов, если они существуют (для чистой установки)
echo Удаление существующих MCP серверов...
npm uninstall -g @modelcontextprotocol/server-sequential-thinking @oevortex/ddg_search @modelcontextprotocol/server-memory @modelcontextprotocol/server-github @modelcontextprotocol/server-everart
echo Удаление завершено!
timeout /t 2

REM Очистка кэша NPM
echo Очистка кэша NPM...
npm cache clean --force
echo Очистка завершена!
timeout /t 2

REM Установка пакетов по одному для лучшей отладки
echo Установка MCP серверов...

echo Установка server-sequential-thinking...
npm install -g @modelcontextprotocol/server-sequential-thinking
echo Завершена установка server-sequential-thinking!
timeout /t 2

echo Установка ddg_search...
npm install -g @oevortex/ddg_search
echo Завершена установка ddg_search!
timeout /t 2

echo Установка server-memory...
npm install -g @modelcontextprotocol/server-memory
echo Завершена установка server-memory!
timeout /t 2

echo Установка server-github...
npm install -g @modelcontextprotocol/server-github
echo Завершена установка server-github!
timeout /t 2

echo Установка server-everart...
npm install -g @modelcontextprotocol/server-everart
echo Завершена установка server-everart!
timeout /t 2

echo Проверка установки...
npm list -g --depth=0
echo Проверка завершена!
timeout /t 2

echo Исправление завершено!
echo Пожалуйста, перезапустите Cursor IDE.
pause
